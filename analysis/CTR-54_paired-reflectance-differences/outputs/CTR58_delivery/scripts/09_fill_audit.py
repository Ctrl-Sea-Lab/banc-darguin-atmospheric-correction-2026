"""Audit every used ACOLITE source for the exact default netCDF Float32 fill sentinel."""
from common import *
import numpy as np
P=json.loads((A/'outputs/pairs.json').read_text());W,H=P[0]['grid']['size'];rows=[]
for p in P:
    for b in BANDS:
        path=SCRATCH/'fill_audit.bin';run(['gdal_translate','-q','-of','ENVI','-ot','Float32',p['acolite'][b],path]);x=np.memmap(path,mode='r',dtype='<f4',shape=(H,W));n=int(np.count_nonzero(x==np.float32(9.969209968386869e36)))
        rows.append(dict(date=p['date'],band=b,declared_nodata='NaN',encoded_default_fill_count=n,nonfinite_count=int(np.count_nonzero(~np.isfinite(x)))))
        del x
print('Fill audit:',[(r['date'],r['band'],r['encoded_default_fill_count']) for r in rows if r['encoded_default_fill_count']])
table(A/'tables/encoded_fill_audit.csv',rows)
save(A/'provenance/fill_encoding.json',dict(exact_float32_fill=9.969209968386869e36,reference='https://docs.unidata.ucar.edu/netcdf-c/current/netcdf_8h.html',interpretation='Exact standard netCDF fill value found as finite pixels despite TIFF NoData=NaN; excluded by value identity, without clipping legitimate negatives.',audited_files=len(rows),affected_dates=sorted(set(r['date'] for r in rows if r['encoded_default_fill_count']))))
