"""Independent date-summary audit; read-only inputs, SSD raster bridges."""
from pathlib import Path
import csv, hashlib, json, os, subprocess, tempfile
import numpy as np
A=Path(__file__).resolve().parents[1]
SOURCE=Path(os.environ.get('CTR56_PRODUCTS','/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026/analysis/CTR-54_paired-reflectance-differences'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
d=list(csv.DictReader((A/'tables/date_band_summary.csv').open()))
assert len(d)==528 and len({(r['pair_id'],r['band'],r['domain']) for r in d})==528
for r in d:
 assert int(r['n_valid'])>1 and float(r['sd_delta'])>0
 assert abs(float(r['coverage_fraction'])-int(r['n_valid'])/int(r['n_grid']))<1e-14
 assert float(r['min_delta'])<=float(r['median_delta'])<=float(r['max_delta'])
manifest={r['path']:r for r in csv.DictReader((A/'provenance/output_hashes.csv').open())}
print('manifest sample',list(manifest)[:2],flush=True)
selected=['2025-01-06','2025-03-22','2025-09-28','2025-12-27','2026-03-07','2026-03-27']
checks=[]; hashes=[]
with tempfile.TemporaryDirectory(prefix='ctr56-summary-audit-',dir='/tmp') as scratch:
 def read_raster(rel,dtype):
  p=SOURCE/rel
  digest=sha(p)
  row=manifest.get(str(rel)) or next((v for k,v in manifest.items() if k.endswith(str(rel))),None)
  assert row is not None and digest==row['sha256'],str(rel)
  hashes.append(dict(path=str(rel),sha256=digest,bytes=p.stat().st_size))
  out=Path(scratch)/'raster.bin'
  subprocess.run(['gdal_translate','-q','-of','ENVI','-ot','Byte' if dtype=='u1' else 'Float32',str(p),str(out)],check=True,env={**os.environ,'GDAL_PAM_ENABLED':'NO'})
  return np.fromfile(out,dtype=dtype)
 for band in ['B2','B3','B4','B8']:
  core=read_raster(Path('outputs/temporal')/f'{band}_complete_dates_domain.tif','u1')==1
  for r in d:
   if r['band']!=band or r['domain']!='primary' or r['date'] not in selected:continue
   x=read_raster(Path('outputs/paired_differences')/f"{r['pair_id']}_{band}_delta.tif",'<f4').astype('float64')
   for dom,mask in [('primary',np.isfinite(x)&(x!=-9999)),('complete_dates',core&np.isfinite(x)&(x!=-9999))]:
    v=x[mask];expected=next(z for z in d if z['pair_id']==r['pair_id'] and z['band']==band and z['domain']==dom)
    med=float(np.median(v)); sd=float(np.sqrt(np.sum((v-v.mean())**2)/(v.size-1)))
    em=abs(med-float(expected['median_delta']));es=abs(sd-float(expected['sd_delta']))
    assert v.size==int(expected['n_valid']) and em<1e-12 and es<1e-12
    checks.append(dict(date=r['date'],band=band,domain=dom,n_valid=v.size,median_recomputed=med,sd_recomputed=sd,median_error=em,sd_error=es))
   print('checked',band,r['date'],flush=True)
with (A/'tables/ctr56_summary_audit.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=checks[0]);w.writeheader();w.writerows(checks)
(A/'provenance/ctr56_input_validation.json').write_text(json.dumps(dict(source_scientific_revision='1bbb23b3b94e775a60aa921f8c9c4f86f51926cb',source_handoff_revision='1631082',date_table_sha256=sha(A/'tables/date_band_summary.csv'),table_rows=528,checked_summary_rows=len(checks),checked_dates=selected,checks='unique keys; finite positive SD; coverage; range; exact counts and independent full-resolution median/sample SD',raster_hashes=hashes,max_median_error=max(r['median_error'] for r in checks),max_sd_error=max(r['sd_error'] for r in checks)),indent=2)+'\n')
