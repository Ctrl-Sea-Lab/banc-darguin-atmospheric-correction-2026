"""Verify frozen numerical content, scientific holds and portable report links."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote
import csv
import hashlib
import json
import math

A = Path(__file__).resolve().parents[1]

def rows(name):
    with (A / 'tables' / name).open(newline='') as f:
        return list(csv.DictReader(f))

def main():
    for required in ['report.qmd', 'report.html', '_quarto.yml', 'task.yml',
                     'scripts/ctr38_figure3_revision.py', 'README.md']:
        assert (A / required).is_file(), required
    source = json.loads((A/'provenance/ctr41_source_table_hashes.json').read_text())
    for path, expected in source.items():
        assert hashlib.sha256((A/path).read_bytes()).hexdigest() == expected, path
    manifest = json.loads((A/'provenance/ctr38_figure3_manifest.json').read_text())
    for path, expected in manifest.items():
        assert hashlib.sha256((A/path).read_bytes()).hexdigest() == expected, path
    assert not rows('ctr34_eligible_pairs.csv')
    primary = rows('ctr38_figure3_primary_pairs.csv')
    reference = rows('ctr38_figure3_reference_pairs.csv')
    assert len(primary) == 36 and len(reference) == 108
    expected_stations = {'AC01', 'AC02', 'AC05', 'AC06', 'AC07', 'AC08'}
    assert {r['station'] for r in primary} == expected_stations
    assert {r['station'] for r in reference} == expected_stations
    assert {r['band'] for r in primary} == {'B2','B3','B4'}
    assert len({r['band'] for r in reference}) == 9
    pairs = rows('ctr37_figure_pairs.csv')
    assert all(r['included_validation_pair'] == 'False' for r in pairs)
    exclusions = (A/'tables/ctr36_exclusions.csv').read_text()
    assert 'AC03' in exclusions and 'mbp_mud' in exclusions
    assert 'AC04' in exclusions and 'mpb_mud' in exclusions
    missing = rows('ctr37_supplementary_metrics.csv')
    assert missing and any('NA' in r.values() for r in missing)
    classes = {r['original_class']:r['display_class'] for r in rows('ctr38_figure3_display_classes.csv')}
    assert classes == {'dry_sand':'Sand','white_sand':'Sand','algae_mud':'Macroalgae','seagrass':'Seagrass'}
    summaries = rows('ctr38_figure3_summary_metrics.csv')
    for r in summaries:
        z = primary if r['population'] == 'primary' else reference
        dif = [float(p['satellite_reflectance'])-float(p['asd_reflectance']) for p in z if p['correction'] == r['correction']]
        expected = {'bias':math.fsum(dif)/len(dif), 'MAE':math.fsum(map(abs,dif))/len(dif),
                    'RMSE':math.sqrt(math.fsum(v*v for v in dif)/len(dif))}
        assert r['validation_eligible_pairs'] == '0'
        for k,v in expected.items():assert math.isclose(float(r[k]),v,rel_tol=0,abs_tol=1e-14), (r,k)
    class Links(HTMLParser):
        def __init__(self):super().__init__();self.ids=set();self.links=[];self.resources=[]
        def handle_starttag(self,tag,attrs):
            d=dict(attrs)
            if d.get('id'):self.ids.add(d['id'])
            if tag=='a' and d.get('href'):self.links.append(d['href'])
            if d.get('src'):self.resources.append(d['src'])
            if tag=='link' and d.get('href'):self.resources.append(d['href'])
    html=(A/'report.html').read_text(); p=Links();p.feed(html)
    assert not [v for v in p.resources if not v.startswith(('data:','#'))]
    for link in p.links:
        if link.startswith('#'):assert unquote(link[1:]) in p.ids, link
        elif not link.startswith(('https:','http:','mailto:','data:')):assert (A/unquote(link.split('#')[0])).exists(), link
    assert 'zero pairs are validation-eligible' in html
    assert 'AC03' in html and 'AC04' in html and 'NA' in html
    qmd=(A/'report.qmd').read_text()
    import re
    for path in re.findall(r'!\[[^\]]*\]\(([^)]+)\)',qmd):assert (A/path).is_file(),path
    result = dict(status='pass',source_tables_byte_identical=len(source),current_manifest_entries=len(manifest),
                  primary_rows=len(primary),reference_rows=len(reference),validation_eligible_pairs=0,
                  supplementary_rows=len(missing),external_rendering_resources=0,links_checked=len(p.links),
                  exact_revision_review='pending; author engineering QA only')
    print(json.dumps(result,indent=2))

if __name__ == '__main__':main()
