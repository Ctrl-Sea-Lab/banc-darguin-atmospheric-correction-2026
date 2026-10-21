#!/usr/bin/env python3
"""Normalize generated text whitespace and hash documentation deliverables only.
Run after rendering. Does not read or write source datasets.
"""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parents[1]
for f in [P/'report.html',P/'provenance/render.txt']:
 if f.exists():f.write_text('\n'.join(line.rstrip() for line in f.read_text().splitlines())+'\n')
for f in (P/'tables').glob('*.csv'):
 f.write_bytes(f.read_bytes().replace(b'\r\n',b'\n'))
files=[]
for f in sorted(P.rglob('*')):
 if f.is_file() and not any(x in f.parts for x in ['.quarto','__pycache__']) and f.name not in ['deliverable_manifest.json','.gitkeep']:
  files.append({'path':str(f.relative_to(P)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
manifest={'documentation_only':True,'manifest_excludes_itself':True,'source_snapshot_sha256':json.loads((P/'provenance/inventory_run.json').read_text())['source_snapshot_sha256'],'report_sha256':next(x['sha256'] for x in files if x['path']=='report.md'),'files':files}
(P/'provenance/deliverable_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(manifest['report_sha256'])
