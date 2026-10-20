#!/usr/bin/env python3
"""Hash reviewable outputs and package delivery; exclude raw data and downloaded reference cache."""
import hashlib,json,zipfile
from pathlib import Path
P=Path(__file__).resolve().parents[1]
files=[p for p in sorted(P.rglob('*')) if p.is_file() and p.suffix not in ['.zip','.xlsx'] and p.name!='deliverable_manifest.json' and not any(x in p.parts for x in ['__pycache__','.quarto'])]
manifest=[{'path':str(p.relative_to(P)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
(P/'provenance/deliverable_manifest.json').write_text(json.dumps({'scope':'CTR-28 feasibility handoff; scientific extraction held; no raw input payloads','files':manifest},indent=2)+'\n')
with zipfile.ZipFile(P/'outputs/CTR-28_feasibility.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in [q for q in files if q.name!='report.html']+[P/'provenance/deliverable_manifest.json']:z.write(p,str(p.relative_to(P)))
p=P/'outputs/CTR-28_feasibility.zip';print(json.dumps({'file':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}))
