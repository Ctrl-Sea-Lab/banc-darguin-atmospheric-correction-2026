from pathlib import Path
import os, json, subprocess, csv, hashlib
A = Path(__file__).resolve().parents[1]
REPO = A.parents[1]
SOURCE = Path(os.environ.get('CTR54_SOURCE','/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026/data/raw/S2'))
SCRATCH = Path(os.environ.get('CTR54_SCRATCH','/tmp/ctr54-paired-reflectance'))
BANDS = ['B2','B3','B4','B8']
def run(args):
    return subprocess.check_output([str(x) for x in args], text=True, env={**os.environ,'GDAL_PAM_ENABLED':'NO','GDAL_CACHEMAX':'256','OPJ_NUM_THREADS':'1'})
def info(path): return json.loads(run(['gdalinfo','-json',path]))
def save(path, obj):
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def table(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()
