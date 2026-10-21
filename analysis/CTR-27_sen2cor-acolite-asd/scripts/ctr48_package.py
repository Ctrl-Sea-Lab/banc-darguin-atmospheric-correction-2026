#!/usr/bin/env python3
"""Package exact committed validation and predecessor inputs, without raw data."""
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path
P=Path(__file__).resolve().parents[1]
ROOT=P.parents[1]
paths=[P/'CTR48_HANDOFF.md',P/'CTR47_HANDOFF.md']
for folder,patterns in {'scripts':['ctr48_*','ctr47_*.py'],'tables':['ctr48_*.csv','ctr47_*.csv'],
                        'provenance':['ctr48_*.json','ctr48_*.txt','ctr47_*.json'],
                        'outputs':['ctr47_raster_headers.json']}.items():
    for pattern in patterns:paths.extend((P/folder).glob(pattern))
paths.extend(P/n for n in ['scripts/ctr42_extract.py','tables/ctr42_band_contract.csv','tables/ctr42_sources.csv','tables/station_crosswalk.csv','provenance/ctr42_scene_pair.json','provenance/ctr42_validation.json'])
paths.extend(ROOT/n for n in ['pyproject.toml','uv.lock','renv.lock','scripts/project-env.sh','scripts/check-env.sh','scripts/bootstrap-env.sh','scripts/bootstrap-renv.R'])
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
payload={}
for p in sorted(set(paths)):
    n=str(p.relative_to(ROOT));data=p.read_bytes()
    assert subprocess.check_output(['git','show',head+':'+n],cwd=ROOT)==data,n
    payload[n]=data
assert json.loads((P/'provenance/ctr48_validation.json').read_text())['status']=='pass'
assert (P/'provenance/ctr48_R_validation.txt').read_text().startswith('PASS:')
manifest=dict(commit=head,predecessor='82ca0df0b699e51135afc680b23eda9def5bbfe2',branch='ctr-48-target-validation',scientific_approval=False,original_raw_data_included=False,files={n:dict(bytes=len(d),sha256=hashlib.sha256(d).hexdigest()) for n,d in payload.items()})
payload['CTR48_REVISION_AND_MANIFEST.json']=(json.dumps(manifest,indent=2)+'\n').encode()
out=P/'outputs/CTR48-verified-target-handoff.zip'
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for n,d in sorted(payload.items()):
        info=zipfile.ZipInfo(n,date_time=(2026,10,20,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,d)
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    for n,d in payload.items():assert z.read(n)==d
print(json.dumps(dict(commit=head,path=str(out),sha256=hashlib.sha256(out.read_bytes()).hexdigest(),bytes=out.stat().st_size,entries=len(payload)),indent=2))
