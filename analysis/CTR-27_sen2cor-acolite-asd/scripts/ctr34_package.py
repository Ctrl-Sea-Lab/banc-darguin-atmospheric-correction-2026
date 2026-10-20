#!/usr/bin/env python3
"""Create a review bundle from the exact Git delivery plus official v5 reference cache."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1]
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
files=[P/n for n in ['report.qmd','report.md','report.html','report.css','_quarto.yml','task.yml','CTR34_README.md']]
for directory,pattern in [('tables','ctr34_*.csv'),('outputs','ctr34_*.json'),('provenance','ctr34_*'),('scripts','ctr34_*'),('figures/generated','ctr34-*.png')]:files+=sorted(p for p in (P/directory).glob(pattern) if p.is_file())
# Minimal accepted dependency evidence needed by the deterministic scripts.
files+=[P/n for n in ['scripts/audit.py','tables/station_crosswalk.csv','tables/proposed_matchups.csv','tables/band_contract.csv','outputs/normalized_design.json','outputs/data_contract.json','provenance/run.json','provenance/official_sources.json','outputs/official-srf-v5.xlsx']]
files+=[ROOT/n for n in ['uv.lock','renv.lock','pyproject.toml','scripts/figure_io.py','scripts/render-analysis.sh','scripts/project-env.sh']]
files+=sorted((P/'outputs/ctr34_browser').glob('*.png'))
files=list(dict.fromkeys(files));assert all(p.is_file() for p in files)
manifest={'task':'CTR-34','delivery_commit':head,'contract_sha256':hashlib.sha256((P/'outputs/ctr34_release_contract.json').read_bytes()).hexdigest(),'scope':'current CTR34 technical release and necessary accepted provenance; no confidential raw input files; zero included matchups','reproduce':'restore bundle into authorized repository layout; raw sources remain on NAS; start with analysis/CTR-27_sen2cor-acolite-asd/CTR34_README.md','v5':'official public sensitivity reference included; supplied raw v4 and campaign data omitted','files':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
path=P/'outputs/CTR-34_review-bundle.zip'
with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 z.writestr('CTR34_bundle_manifest.json',json.dumps(manifest,indent=2)+'\n')
 for p in files:z.write(p,str(p.relative_to(ROOT)))
print(json.dumps({'path':str(path),'commit':head,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'files':len(files)}))
