"""Hash every physical source used, including full selected ZIP containers, without modifying it."""
from common import *
P=json.loads((A/'outputs/pairs.json').read_text());paths=set()
for p in P:
    paths.update(p['acolite'].values())
    if p['flags']:paths.add(p['flags'])
    s=p['sen2cor']
    if s['container'].endswith('.zip'):paths.add(s['container'])
    else:paths.update([*s['bands'].values(),s['scl'],s['product_metadata'],s['tile_metadata']])
rows=[]
for i,path in enumerate(sorted(paths)):
    p=Path(path);before=p.stat();h=sha(p);after=p.stat();assert before.st_size==after.st_size and before.st_mtime_ns==after.st_mtime_ns
    rows.append(dict(path=str(p),bytes=before.st_size,mtime_ns=before.st_mtime_ns,sha256=h,stable_during_hash=True))
    if i%20==0:print('HASH',i,len(paths),flush=True)
table(A/'provenance/input_hashes.csv',rows)
save(A/'provenance/input_integrity.json',dict(files=len(rows),total_bytes=sum(r['bytes'] for r in rows),all_stable_during_hash=True,scope='Full physical ZIP containers for selected Sen2Cor products; used bands, flags and metadata for loose inputs. Unpaired inputs catalogued but not hashed or processed.',raw_write_operations=0))
