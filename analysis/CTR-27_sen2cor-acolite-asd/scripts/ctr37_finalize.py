#!/usr/bin/env python3
"""Verify delivery and package derived files; run after the standalone HTML render."""
import csv
import hashlib
import json
import subprocess
import zipfile
from html.parser import HTMLParser
from pathlib import Path
P=Path(__file__).resolve().parents[1]
ROOT=P.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    before={f.name:sha(f) for f in (P/'tables').glob('ctr37_*.csv')}
    report_before=sha(P/'diagnostic-agreement.qmd')
    r=subprocess.run([str(ROOT/'.venv/bin/python'),str(P/'scripts/ctr37_diagnostics.py')],cwd=ROOT,capture_output=True,text=True,check=True)
    (P/'provenance/ctr37_execution.txt').write_text(r.stdout)
    after={f.name:sha(f) for f in (P/'tables').glob('ctr37_*.csv')}
    assert before==after
    subprocess.run([str(ROOT/'scripts/project-env.sh'),'Rscript',str(P/'scripts/ctr37_verify.R')],cwd=ROOT,check=True)
    subprocess.run([str(ROOT/'.venv/bin/python'),str(P/'scripts/ctr37_report.py')],cwd=ROOT,check=True)
    assert sha(P/'diagnostic-agreement.qmd')==report_before
    class Check(HTMLParser):
        def __init__(self):
            super().__init__();self.tables=0;self.rows=0;self.remote=[];self.text=[]
        def handle_starttag(self,tag,attrs):
            a=dict(attrs)
            if tag=='table':self.tables+=1
            if tag=='tr':self.rows+=1
            if tag in ['script','img','link']:
                url=a.get('src',a.get('href',''))
                if url.startswith(('https://','http://')):self.remote.append(url)
        def handle_data(self,d):self.text.append(d)
    h=Check();h.feed((P/'diagnostic-agreement.html').read_text())
    assert h.tables==2 and h.rows==26 and not h.remote
    text=' '.join(h.text)
    for r in csv.DictReader((P/'tables/ctr37_station_metrics.csv').open()):
        for k in ['bias','MAE','RMSE']:assert f'{float(r[k]):.6f}' in text
    q=(P/'diagnostic-agreement.qmd').read_text()
    assert '\\frac' in q and '\x0c' not in q and '\x08' not in q
    original=json.loads((P/'provenance/ctr36_original_tracked.json').read_text())
    assert all(sha(ROOT/n)==v for n,v in original.items())
    validation={'status':'pass','numeric_tables_replayed_identically':len(before),'table_sha256':after,'html_tables':h.tables,'html_table_rows_including_headers':h.rows,'external_render_assets':h.remote,'all_primary_rounded_metrics_found_in_html':True,'original_tracked_files_preserved':len(original),'input_audit_checks':json.loads((P/'provenance/ctr37_input_audit.json').read_text())['check_count'],'R_checks':74,'dict_report_unchanged':True,'review':'author verification, not independent scientific review'}
    (P/'provenance/ctr37_delivery_validation.json').write_text(json.dumps(validation,indent=2)+'\n')
    files=sorted({*P.glob('scripts/ctr37_*'),*P.glob('tables/ctr37_*'),*P.glob('provenance/ctr37_*'),*P.glob('outputs/ctr37_*.json'),P/'diagnostic-agreement.qmd',P/'diagnostic-agreement.html'}-{P/'provenance/ctr37_delivery_manifest.json'})
    manifest={str(f.relative_to(P)):{'sha256':sha(f),'bytes':f.stat().st_size} for f in files}
    (P/'provenance/ctr37_delivery_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    files.append(P/'provenance/ctr37_delivery_manifest.json')
    files.extend(P/f for f in ['tables/ctr36_station_inputs.csv','tables/ctr36_supplementary_unmatched.csv','tables/ctr36_nonmud_station_inventory.csv','tables/ctr36_exclusions.csv','tables/ctr34_eligible_pairs.csv'])
    bundle=P/'outputs/CTR37_diagnostic-agreement.zip'
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for f in files:z.write(f,str(f.relative_to(P)))
    with zipfile.ZipFile(bundle) as z:
        assert z.testzip() is None
        assert all(hashlib.sha256(z.read(n)).hexdigest()==v['sha256'] for n,v in manifest.items())
    print(json.dumps({'checks':'pass','bundle_bytes':bundle.stat().st_size,'bundle_sha256':sha(bundle),'manifest_files':len(manifest)}))

if __name__=='__main__':main()
