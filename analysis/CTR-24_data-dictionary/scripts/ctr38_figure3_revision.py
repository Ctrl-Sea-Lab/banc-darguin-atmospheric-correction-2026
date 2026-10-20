"""Audit PI attachments, reproduce Figure 3, and render a standalone scientific report.

No extraction, spectral integration, processor run, inference or environment change.
Run from the canonical repository using its .venv/bin/python.
"""
from pathlib import Path
import csv
import hashlib
import html
import importlib.util
import json
import math
import subprocess
import tempfile
import zipfile

A = Path(__file__).resolve().parents[1]
ROOT = A.parents[1]
P = A / 'provenance/pi_figure3_20261020'
BASE = 'dd00258982cd3050d74d9a41291a1bf6fb061abc'
STATIONS = ['AC01','AC02','AC05','AC06','AC07','AC08']
CORRECTIONS = ['Sen2Cor','ACOLITE']
TARGETS = {'dry_sand':'Dry sand','algae_mud':'Algal mud','white_sand':'White sand','seagrass':'Seagrass'}


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    with p.open(newline='') as f:
        return list(csv.DictReader(f))


def write(p, rows):
    with p.open('w',newline='') as f:
        w = csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        w.writeheader(); w.writerows(rows)


def table(headings,rows):
    esc=lambda v: html.escape(str(v))
    return '<table><thead><tr>'+''.join('<th>'+esc(h)+'</th>' for h in headings)+'</tr></thead><tbody>\n'+''.join('<tr>'+''.join('<td>'+esc(v)+'</td>' for v in r)+'</tr>\n' for r in rows)+'</tbody></table>'


def main():
    expected = {'MatchupByBandAndSurface_Fig003.png':'d4090d416bed79e75b347aad423001662802b9f58436e972c5972d44b9d008f0',
                'figure3_matchup_data.csv':'1fb4abac9200a4fd09ff815f2ee855b91418bdfacb4681cf4bba9a8d9f950853',
                'make_figure3_frida.R':'106c6f11be8c76f5557bd4f9ad60c5ebeb23a2b5375dca0133d845740df001c0'}
    for n,h in expected.items(): assert digest(P/n)==h,n
    for n,v in json.loads((A/'provenance/ctr37_delivery_manifest.json').read_text()).items():
        assert digest(A/n)==v['sha256'],n
    assert json.loads((A/'provenance/ctr37_delivery_validation.json').read_text())['status']=='pass'
    assert len(read(A/'tables/ctr34_eligible_pairs.csv'))==0
    supplied=read(P/'figure3_matchup_data.csv')
    assert len(supplied)==126
    assert {r['station'] for r in supplied}==set(STATIONS+['AC04'])
    assert {r['band'] for r in supplied}=={'B1','B2','B3','B4','B5','B6','B7','B8','B8A'}
    for r in supplied:
        for k in ['asd_reflectance','satellite_reflectance','band_center']: assert math.isfinite(float(r[k]))
    key=lambda r:(r['station'],r['band'])
    keys=[{key(r) for r in supplied if r['correction']==c} for c in CORRECTIONS]
    assert len(keys[0])==63 and keys[0]==keys[1]
    src={(*key(r),r['correction']):r for r in supplied}
    for s,b in keys[0]:
        assert src[s,b,'Sen2Cor']['asd_reflectance']==src[s,b,'ACOLITE']['asd_reflectance']
        assert src[s,b,'Sen2Cor']['target']==src[s,b,'ACOLITE']['target']
    reference=[r for r in supplied if r['station'] in STATIONS]
    primary=[]; audit=[]
    for r in read(A/'tables/ctr37_figure_pairs.csv'):
        if r['common_finite_triple']!='True': continue
        c={'L2A':'Sen2Cor','ACOLITE':'ACOLITE'}[r['correction']]
        b='B'+str(int(r['band_id'][1:]))
        s=src[r['station_id'],b,c]
        da=abs(float(s['asd_reflectance'])-float(r['ASD_reflectance']))
        ds=abs(float(s['satellite_reflectance'])-float(r['satellite_reflectance']))
        assert max(da,ds)<1e-12
        assert r['included_validation_pair']=='False' and r['unit']=='1'
        primary.append(dict(station=r['station_id'],target=TARGETS[r['class_literal']],band=b,
                            asd_reflectance=r['ASD_reflectance'],satellite_reflectance=r['satellite_reflectance'],correction=c))
        audit.append(dict(station=r['station_id'],band=r['band_id'],correction=c,
                          ASD_absolute_difference=da,satellite_absolute_difference=ds,tolerance=1e-12,status='match'))
    assert len(primary)==36 and len(reference)==108 and len(audit)==36
    write(A/'tables/ctr38_figure3_primary_pairs.csv',primary)
    write(A/'tables/ctr38_figure3_reference_pairs.csv',reference)
    write(A/'tables/ctr38_figure3_source_audit.csv',audit)
    summaries=[]
    for label,rows in [('primary',primary),('reference',reference)]:
        for c in CORRECTIONS:
            z=[r for r in rows if r['correction']==c]
            dif=[float(r['satellite_reflectance'])-float(r['asd_reflectance']) for r in z]
            summaries.append(dict(population=label,correction=c,n_stations=6,n_bands=3 if label=='primary' else 9,
                 n_station_band_values=len(z),bias=math.fsum(dif)/len(z),MAE=math.fsum(abs(d) for d in dif)/len(z),
                 RMSE=math.sqrt(math.fsum(d*d for d in dif)/len(z)),unit='1',validation_eligible_pairs=0,
                 evidence_scope='exploratory_physical_hold' if label=='primary' else 'supplied_table_reproduction_only'))
    write(A/'tables/ctr38_figure3_summary_metrics.csv',summaries)
    # Independent identity: mean station biases and pooled station MSE match primary arithmetic.
    saved=read(A/'tables/ctr37_station_metrics.csv')
    for c in CORRECTIONS:
        sc='L2A' if c=='Sen2Cor' else c
        z=[r for r in saved if r['correction']==sc]
        m=next(r for r in summaries if r['population']=='primary' and r['correction']==c)
        for k,col in [('bias','bias'),('MAE','MAE')]: assert abs(m[k]-math.fsum(float(r[col]) for r in z)/6)<1e-14
        assert abs(m['RMSE']-math.sqrt(math.fsum(float(r['RMSE'])**2 for r in z)/6))<1e-14
    # Confirm the supplied image's printed rounding, without treating it as validated evidence.
    for c,rmse,bias in [('Sen2Cor','0.066','+0.050'),('ACOLITE','0.042','+0.020')]:
        m=next(r for r in summaries if r['population']=='reference' and r['correction']==c)
        assert format(m['RMSE'],'.3f')==rmse and format(m['bias'],'+.3f')==bias
    spec=importlib.util.spec_from_file_location('figure_io',ROOT/'scripts/figure_io.py')
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix='ctr38_figure3_',dir=A/'outputs') as tmp:
        run=subprocess.run([str(ROOT/'scripts/project-env.sh'),'Rscript',str(A/'scripts/ctr38_figure3_revision.R'),str(A),tmp],cwd=ROOT,capture_output=True,text=True,check=True)
        (A/'provenance/ctr38_figure3_render.txt').write_text(run.stdout+run.stderr)
        for p in Path(tmp).iterdir(): module.write_generated_bytes(A,p.name,p.read_bytes())
    md=(A/'scripts/ctr38_final_report_template.md').read_text()
    rows=[[r['population'],r['correction'],r['n_stations'],r['n_bands'],r['n_station_band_values'],f"{r['bias']:+.6f}",f"{r['MAE']:.6f}",f"{r['RMSE']:.6f}"] for r in summaries]
    md=md.replace('SUMMARY_TABLE',table(['Scope','Correction','Stations','Bands','Values','Bias (1)','MAE (1)','RMSD (1)'],rows))
    rows=[[r['station_id'],r['class_literal'],{'L2A':'Sen2Cor','ACOLITE':'ACOLITE'}[r['correction']],r['n_paired_bands']]+[format(float(r[k]),'.6f') for k in ['bias','MAE','RMSE']] for r in saved]
    md=md.replace('STATION_TABLE',table(['Station','Original target','Correction','Bands','Bias (1)','MAE (1)','RMSD (1)'],rows))
    coverage=read(A/'tables/ctr37_station_coverage.csv')
    rows=[[r['station_id'],r['class_literal'],'NA','NA',0] for r in coverage if r['population']=='supplementary']
    md=md.replace('MISSING_TABLE',table(['Station','Original target','ASD band reference','Satellite values','Common bands'],rows))
    md=md.replace('INPUT_HASH_TABLE',table(['Supplied attachment','SHA-256'],expected.items()))
    (A/'final-matchup-report.qmd').write_text(md)
    render=subprocess.run([str(ROOT/'scripts/project-env.sh'),'quarto','render','final-matchup-report.qmd','--to','html'],cwd=A,capture_output=True,text=True,check=True)
    (A/'provenance/ctr38_figure3_quarto.txt').write_text(render.stdout+render.stderr)
    report=(A/'final-matchup-report.html').read_text()
    from html.parser import HTMLParser
    class Resources(HTMLParser):
        external=[]
        def handle_starttag(self,tag,attrs):
            for k,v in attrs:
                if k=='src' or (tag=='link' and k=='href'):
                    if v and not v.startswith(('data:','#')): self.external.append(v)
    parser=Resources();parser.feed(report);assert not parser.external,parser.external
    for r in summaries:
        for k in ['bias','MAE','RMSE']: assert format(r[k],'+.6f' if k=='bias' else '.6f') in report
    result=dict(status='pass',previous_author_commit=BASE,source_comment_id='e6a042c8-55d1-433d-afce-18a6b2f9ec0d',
        supplied_rows=126,supplied_script_expected_rows=144,missing_script_input='figure3_metrics.csv',
        primary_values_per_correction=18,reference_values_per_correction=54,overlapping_values_checked=36,
        max_ASD_difference=max(r['ASD_absolute_difference'] for r in audit),
        max_satellite_difference=max(r['satellite_absolute_difference'] for r in audit),
        primary_summary_checked_against_saved_station_metrics=True,reference_printed_metrics_match_example=True,
        source_csv_excluded_station='AC04',source_csv_AC03_absent=True,validation_eligible_pairs=0,
        new_extraction=False,new_integration=False,inference=False,external_report_resources=parser.external,
        scientific_review='pending exact-revision independent review; not PI approval')
    (A/'provenance/ctr38_figure3_revision.json').write_text(json.dumps(result,indent=2)+'\n')
    paths=[A/'final-matchup-report.qmd',A/'final-matchup-report.html']
    for pattern in ['scripts/ctr38_figure3_revision.*','scripts/ctr38_final_report_template.md','tables/ctr38_figure3_*.csv','provenance/pi_figure3_20261020/*','provenance/ctr38_figure3_*','figures/generated/ctr38_figure3_*']:
        paths.extend(A.glob(pattern))
    # Include the original station-facet deliverable and saved metrics in the complete bundle.
    paths.extend([A/'figures/generated/ctr38_station_spectra.svg',A/'figures/generated/ctr38_station_spectra.pdf',
        A/'tables/ctr37_station_metrics.csv',A/'tables/ctr37_supplementary_metrics.csv',A/'tables/ctr36_exclusions.csv',
        A/'tables/ctr37_figure_pairs.csv',A/'tables/ctr37_station_coverage.csv'])
    manifest=A/'provenance/ctr38_figure3_manifest.json'
    paths=[p for p in paths if p != manifest]
    hashes={str(p.relative_to(A)):digest(p) for p in sorted(set(paths))}
    manifest.write_text(json.dumps(hashes,indent=2)+'\n')
    for name,extensions in [('CTR38_final-figure3-report.zip',None),('CTR38_figure3-source-and-tables.zip',{'.R','.py','.md','.qmd','.csv','.json'})]:
        with zipfile.ZipFile(A/'outputs'/name,'w',zipfile.ZIP_DEFLATED) as z:
            for p in sorted(set(paths+[manifest])):
                if extensions is None or p.suffix in extensions: z.write(p,str(p.relative_to(A)))
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
