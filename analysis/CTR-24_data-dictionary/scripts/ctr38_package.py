"""Freeze output hashes before commit; package the exact committed revision after commit."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import zipfile

A=Path(__file__).resolve().parents[1]
ROOT=A.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest_path=A/'provenance/ctr38_manifest.json'
if '--freeze' in sys.argv:
    files=[A/'station-matchups.qmd',A/'station-matchups.html']
    for folder in ['scripts','provenance','tables','figures/generated','outputs']:
        files.extend(p for p in (A/folder).glob('ctr38_*') if p.is_file() and p.suffix in ['.R','.py','.json','.md','.txt','.csv','.png','.pdf','.svg'])
    files=[p for p in files if p!=manifest_path]
    manifest_path.write_text(json.dumps({str(p.relative_to(A)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(set(files))},indent=2)+'\n')
    print(f'Frozen {len(files)} deliverable files')
else:
    manifest=json.loads(manifest_path.read_text())
    for n,r in manifest.items(): assert sha(A/n)==r['sha256'], n
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    assert not subprocess.check_output(['git','diff','HEAD','--name-only'],cwd=ROOT,text=True).strip(), 'Commit current source before packaging'
    files={A/n for n in manifest}|{manifest_path}
    numerical=json.loads((A/'provenance/ctr37_delivery_manifest.json').read_text())
    files|={A/n for n in numerical}|{A/'provenance/ctr37_delivery_manifest.json',A/'outputs/ctr37_contract.json'}
    contract=json.loads((A/'outputs/ctr37_contract.json').read_text())
    files|={A/n for n in contract['inputs']}
    # Build uses this extra table and preserves the original exclusion ledger.
    files|={A/'tables/ctr36_exclusions.csv'}
    assert all(p.is_file() and p.stat().st_size<5_000_000 for p in files)
    metadata={'issue':'CTR-38','commit':commit,'input_commit':'9a4ec93fc412736fda85b44a1aab56ed6e2c2beb','manifest_sha256':sha(manifest_path),'review':'Submitted for native Rachel then Karl reviews; not PI approval','files':{str(p.relative_to(A)):sha(p) for p in sorted(files)}}
    bundle=A/'outputs/CTR38_station-matchups.zip'
    with zipfile.ZipFile(bundle,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(files): z.write(p,str(p.relative_to(A)))
        z.writestr('CTR38_DELIVERY.json',json.dumps(metadata,indent=2)+'\n')
    with zipfile.ZipFile(bundle) as z: assert z.testzip() is None
    print(json.dumps({'commit':commit,'bundle':str(bundle),'sha256':sha(bundle),'bytes':bundle.stat().st_size,'files':len(files)+1},indent=2))
