"""Validate current CTR44 presentation, frozen numbers, gaps, and preservation."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote
import csv,hashlib,json,math,subprocess
A=Path(__file__).resolve().parents[1]; ROOT=A.parents[1]
BASE='dc10ebe93e8e5053f4f7fb6aa377ba7fb9a174bd'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(name):
    with (A/'tables'/name).open(newline='') as f:return list(csv.DictReader(f))
class Links(HTMLParser):
    def __init__(self):super().__init__();self.ids=set();self.links=[];self.resources=[];self.imgs=0
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if 'id' in d:self.ids.add(d['id'])
        if tag=='a' and 'href' in d:self.links.append(d['href'])
        if tag=='img':self.imgs+=1
        if 'src' in d:self.resources.append(d['src'])
        if tag=='link' and 'href' in d:self.resources.append(d['href'])
def main():
    audit=json.loads((A/'provenance/ctr43_computation.json').read_text())
    for n,h in audit['tables_sha256'].items():assert sha(A/'tables'/n)==h,n
    before=json.loads((A/'provenance/ctr44_before.json').read_text())
    for n,h in before['figure1'].items():assert sha(A/n)==h,n
    unrelated_changes={n:{'before':h,'current':sha(ROOT/n)} for n,h in before['unrelated_files'].items() if sha(ROOT/n)!=h}
    # CTR39 is independently active; record changes, never restore or overwrite it.
    (A/'provenance/ctr44_unrelated_changes.json').write_text(json.dumps({'active_issue':'CTR-39','active_run_observed':'88ba401d-6729-434b-b661-6d7981792266','baseline_files':len(before['unrelated_files']),'externally_changed_files':unrelated_changes,'CTR44_writes_confined_to':'analysis/CTR-27_sen2cor-acolite-asd','no_CTR39_files_deleted_or_restored':True},indent=2)+'\n')
    for p in (A/'tables').glob('ctr42_*.csv'):
        assert p.read_bytes()==subprocess.check_output(['git','show',f'{BASE}:{p.relative_to(ROOT)}'],cwd=ROOT),p
    d=[r for r in read('ctr43_spectral_long.csv') if r['SRF_role']=='v4_primary']
    assert len(d)==351 and len({(r['station_id'],r['band_id'],r['series']) for r in d})==351
    assert {r['band_id'] for r in d}=={'B01','B02','B03','B04','B05','B06','B07','B08','B8A'}
    assert all(r['validation_eligible']=='False' and r['unit']=='1' for r in d)
    assert sum(r['reflectance']!='NA' for r in d)==338
    assert sum(r['series']!='ASD' and r['SCL_flag']=='True' for r in d)==109
    for r in d:
        assert r['observation_date']==('2026-03-27' if r['series']=='ASD' else '2026-03-07')
        if r['series']=='ASD' and r['band_id']=='B08':assert r['reflectance']=='NA' and r['segment_id']=='NA' and r['availability_reason']=='insufficient_coverage'
        else:assert math.isfinite(float(r['reflectance']))
        if r['series']=='ASD' and r['band_id']=='B8A':assert r['segment_id']=='2'
    accounting=read('ctr43_station_accounting.csv');assert len(accounting)==15
    assert {(r['station_id'],r['class_literal']) for r in accounting if r['disposition']=='excluded'}=={('AC03','mbp_mud'),('AC04','mpb_mud')}
    pairs=read('ctr38_figure3_reference_pairs.csv');assert len(pairs)==108
    assert {r['station'] for r in pairs}=={'AC01','AC02','AC05','AC06','AC07','AC08'}
    summaries=read('ctr38_figure3_summary_metrics.csv');assert len(summaries)==2 and all(r['population']=='reference' for r in summaries)
    for r in summaries:
        expected=('0.066','+0.050') if r['correction']=='Sen2Cor' else ('0.042','+0.020')
        assert (format(float(r['RMSE']),'.3f'),format(float(r['bias']),'+.3f'))==expected
    q=(A/'report.qmd').read_text()
    for obsolete in ['ctr38_figure3_primary.svg','0.065747','0.036927','0.051881','ctr37_station_metrics.csv','Per-station bias','three-band comparison in the same style']:assert obsolete not in q,obsolete
    for path in ['figures/generated/ctr38_figure3_primary.svg','figures/generated/ctr38_figure3_station_spectra.svg','tables/ctr38_figure3_primary_pairs.csv','tables/ctr37_station_metrics.csv','diagnostic-agreement.html']:assert not (A/path).exists(),path
    assert '20 days' in q and 'zero pairs are validation-eligible' in q
    assert all(s in q for s in ['Figure 1.','Figure 3.','Figure S1.','NA','AC03 mbp_mud','AC04 mpb_mud'])
    import re
    for path in re.findall(r'<img src="([^"]+)"',q):assert (A/path).is_file(),path
    total=0
    for name in ['report.html','report-portable.html']:
        h=(A/name).read_text();p=Links();p.feed(h);assert p.imgs==3
        assert not [u for u in p.resources if not u.startswith(('data:','#'))]
        for link in p.links:
            if link.startswith('#'):assert unquote(link[1:]) in p.ids,link
            elif not link.startswith(('https:','http:','mailto:','data:')):assert (A/unquote(link.split('#')[0])).exists(),link
        assert 'zero pairs are validation-eligible' in h
        total+=len(p.links)
    def mainbody(p):
        t=p.read_text();return t[t.index('<main'):t.index('</main>')+7]
    assert mainbody(A/'report.html')==mainbody(A/'report-portable.html')
    # The renderer consumes these fields directly: no remapping, interpolation or statistics.
    src=(A/'scripts/ctr44_spectra.R').read_text()
    for s in ['v4_primary','q$segment_id==seg','q$reflectance','q$plot_wavelength_nm','NA [COV]']:assert s in src
    results={'status':'pass','upstream_commit':BASE,'frozen_CTR43_tables':len(audit['tables_sha256']),'frozen_CTR42_tables':len(list((A/'tables').glob('ctr42_*.csv'))),'unchanged_figure1_exports':len(before['figure1']),'unrelated_CTR39_baseline_files_still_present':len(before['unrelated_files']),'unrelated_CTR39_external_changes_recorded':len(unrelated_changes),'primary_role_rows':351,'finite_satellite_values':234,'finite_ASD_values':104,'ASD_B08_NA':13,'SCL_flagged_satellite_values':109,'all_stations_accounted':15,'validation_eligible_pairs':0,'obsolete_scatter_and_metrics_removed':True,'html_images_each':3,'html_links_checked':total,'portable_main_identical':True,'new_statistics_or_extraction':False,'review_status':'pending Rachel then Karl on exact revision; no PI approval'}
    (A/'provenance/ctr44_validation.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
if __name__=='__main__':main()
