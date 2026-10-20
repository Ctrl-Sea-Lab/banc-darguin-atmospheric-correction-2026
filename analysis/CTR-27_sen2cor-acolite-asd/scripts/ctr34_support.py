#!/usr/bin/env python3
"""Read-only bounded CTR-34 metadata, native QA and imagery inspection; no ASD errors."""
import os,csv,json,ctypes as C,ctypes.util,hashlib,subprocess,datetime as dt
from pathlib import Path
import numpy as np
import audit as a
P=a.OUT; ROOT=a.ROOT; VERSION='ctr34-v1'; PRIMARY=['AC01','AC02','AC05','AC06','AC07','AC08']; BANDS=['B02','B03','B04']
os.environ.update(GDAL_PAM_ENABLED='NO',CPL_TMPDIR='/tmp',PROJ_NETWORK='OFF',GDAL_NUM_THREADS='1')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(n):return list(csv.DictReader((P/n).open()))
def dump(n,x):
 p=P/n;p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def table(n,rs,fields=None):
 p=P/n;p.parent.mkdir(exist_ok=True,parents=True)
 with p.open('w') as f:
  w=csv.DictWriter(f,fieldnames=fields or list(dict.fromkeys(k for r in rs for k in r)),lineterminator='\n');w.writeheader();w.writerows(rs)
def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def raw_snapshot():
 base=Path('/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026/data/raw');return {str(p.relative_to(base)):[p.stat().st_size,p.stat().st_mtime_ns] for p in base.rglob('*') if p.is_file()}
class Raster:
 lib=C.CDLL(ctypes.util.find_library('gdal'));lib.GDALAllRegister()
 for fn,args,ret in [('GDALOpen',[C.c_char_p,C.c_int],C.c_void_p),('GDALGetRasterBand',[C.c_void_p,C.c_int],C.c_void_p),('GDALGetRasterCount',[C.c_void_p],C.c_int),('GDALClose',[C.c_void_p],None),('GDALRasterIO',[C.c_void_p,C.c_int,C.c_int,C.c_int,C.c_int,C.c_int,C.c_void_p,C.c_int,C.c_int,C.c_int,C.c_int,C.c_int],C.c_int)]:
  f=getattr(lib,fn);f.argtypes=args;f.restype=ret
 def __init__(self,path):
  self.path=str(path);self.h=json.loads(subprocess.check_output(['gdalinfo','-json','-noct','-nogcp',self.path],text=True));self.ds=self.lib.GDALOpen(self.path.encode(),0);assert self.ds
 def index(self,x,y):
  g=self.h['geoTransform'];assert g[2]==g[4]==0;return int(np.floor((x-g[0])/g[1])),int(np.floor((y-g[3])/g[5]))
 def bounds(self,c,r):
  g=self.h['geoTransform'];x=g[0]+c*g[1];y=g[3]+r*g[5];return [x,y+g[5],x+g[1],y]
 def read(self,c,r,rad=0,band=1):
  n=2*rad+1;v=np.empty((n,n),dtype=np.float64);assert c-rad>=0 and r-rad>=0 and c+rad<self.h['size'][0] and r+rad<self.h['size'][1]
  assert self.lib.GDALRasterIO(self.lib.GDALGetRasterBand(self.ds,band),0,c-rad,r-rad,n,n,v.ctypes.data_as(C.c_void_p),n,n,7,0,0)==0
  return v
 def close(self):self.lib.GDALClose(self.ds)
def decode(v):
 out=np.full(v.shape,np.nan);good=(v!=0)&(v!=65535)&np.isfinite(v);out[good]=(v[good]-1000)/10000;return out

def inspect():
 before=raw_snapshot();dump('provenance/ctr34_raw_before.json',before)
 st=rows('tables/station_crosswalk.csv');bc={r['band']:r for r in rows('tables/band_contract.csv')};headers={};sources=[];cache={};windows=[];qa=[];images=[];stats=[];loc=[]
 def src(path):
  if path not in cache:
   rr=Raster(ROOT/path);cache[path]=rr;headers[path]=rr.h;s=Path(ROOT/path).stat();sources.append({'source_id':path,'path':path,'bytes':s.st_size,'mtime_ns':s.st_mtime_ns,'identity_strength':'header/path/stat + separately hashed decoded windows; no full raster hash','header_sha256':hashlib.sha256(json.dumps(rr.h,sort_keys=True).encode()).hexdigest(),'grid_id':hashlib.sha256(json.dumps([rr.h.get('geoTransform'),rr.h['size'],rr.h.get('coordinateSystem')],sort_keys=True).encode()).hexdigest()})
  return cache[path]
 xy=subprocess.check_output(['gdaltransform','-s_srs','EPSG:4326','-t_srs','EPSG:32628'],input='\n'.join(s['lon_raw']+' '+s['lat_raw'] for s in st),text=True).splitlines();xy=[list(map(float,l.split()[:2])) for l in xy]
 safe=bc['B02']['sen2cor_path'].split('/GRANULE/')[0];gran=bc['B02']['sen2cor_path'].split('/IMG_DATA/')[0];scl=next((ROOT/gran/'IMG_DATA/R20m').glob('*SCL_20m.jp2'));sclpath=str(scl.relative_to(ROOT))
 for s,(x,y) in zip(st,xy):
  sid=s['station_id'];raster=src(bc['B02']['sen2cor_path']);c,r=raster.index(x,y);bbox=raster.bounds(c,r)
  loc.append({'station_id':sid,'lon':float(s['lon_raw']),'lat':float(s['lat_raw']),'x_m':x,'y_m':y,'CRS':'EPSG:32628','SAFE_col_0based':c,'SAFE_row_0based':r,'xmin':bbox[0],'ymin':bbox[1],'xmax':bbox[2],'ymax':bbox[3],'class_literal':s['target_class_raw'],'geographic_group':'Iwik' if sid in ['AC01','AC02'] else 'offshore_Arel','PI_mud_excluded':sid in ['AC03','AC04'],'primary_intended':sid in PRIMARY})
  # No new radiometric/mask diagnostics of excluded mud or supplementary targets.
  if sid not in PRIMARY:continue
  for band in BANDS:
   for method,key in [('L2A','sen2cor_path'),('ACOLITE','acolite_path')]:
    path=bc[band][key];rr=src(path);col,row=rr.index(x,y);v=rr.read(col,row,5);out=decode(v) if method=='L2A' else v
    windows.append({'station_id':sid,'band':band,'method':method,'source_id':path,'row_start':row-5,'col_start':col-5,'rows':11,'cols':11,'dtype':'float64 little-endian','decoded_window_sha256':hashlib.sha256(v.astype('<f8').tobytes()).hexdigest(),'scope':'read window only; not full raster identity'})
    for i in range(11):
     for j in range(11):
      val=float(out[i,j]);images.append({'station_id':sid,'method':method,'band':band,'dy':i-5,'dx':j-5,'reflectance':val if np.isfinite(val) else None})
    # Heterogeneity across 3x3 and 5x5 analyst-selected scenarios, never ASD variance.
    for rad in [1,2]:
     z=out[5-rad:6+rad,5-rad:6+rad];valid=z[np.isfinite(z)]
     stats.append({'station_id':sid,'method':method,'band':band,'scenario_radius_pixels':rad,'width_m':(2*rad+1)*10,'finite_count':len(valid),'total_count':z.size,'minimum':float(valid.min()) if len(valid) else None,'maximum':float(valid.max()) if len(valid) else None,'range':float(np.ptp(valid)) if len(valid) else None,'standard_deviation_population':float(np.std(valid)) if len(valid) else None,'meaning':'spatial sensitivity; not GPS error or reference standard error'})
   for kind in ['QUALIT','DETFOO']:
    path=str((ROOT/gran/'QI_DATA'/f'MSK_{kind}_{band}.jp2').relative_to(ROOT));rr=src(path);col,row=rr.index(x,y)
    for layer in range(1,rr.lib.GDALGetRasterCount(rr.ds)+1):
     z=rr.read(col,row,2,layer);windows.append({'station_id':sid,'band':band,'method':'QA_'+kind+':'+str(layer),'source_id':path,'row_start':row-2,'col_start':col-2,'rows':5,'cols':5,'dtype':'float64 little-endian','decoded_window_sha256':hashlib.sha256(z.astype('<f8').tobytes()).hexdigest(),'scope':'native QA diagnostic window'})
     for i in range(5):
      for j in range(5):qa.append({'station_id':sid,'band':band,'kind':kind,'layer':layer,'source_id':path,'row':row+i-2,'col':col+j-2,'dx':j-2,'dy':i-2,'raw':int(z[i,j]),'pixel_bounds_32628':json.dumps(rr.bounds(col+j-2,row+i-2)),'role':'QA only; 5x5 scenario envelope, not radiometric contributor'})
  rr=src(sclpath);col,row=rr.index(x,y);z=rr.read(col,row,2)
  for i in range(5):
   for j in range(5):qa.append({'station_id':sid,'band':'all','kind':'SCL','layer':1,'source_id':sclpath,'row':row+i-2,'col':col+j-2,'dx':j-2,'dy':i-2,'raw':int(z[i,j]),'pixel_bounds_32628':json.dumps(rr.bounds(col+j-2,row+i-2)),'role':'categorical QA only; 20m native cells'})
 for rr in cache.values():rr.close()
 table('tables/ctr34_locations.csv',loc);table('tables/ctr34_local_qa.csv',qa);table('tables/ctr34_window_hashes.csv',windows);table('tables/ctr34_local_imagery.csv',images);table('tables/ctr34_heterogeneity.csv',stats)
 dump('outputs/ctr34_headers.json',headers);dump('outputs/ctr34_sources.json',sources)
 after=raw_snapshot();assert before==after;dump('provenance/ctr34_inspect.json',{'completed_utc':now(),'raw_stat_unchanged':True,'raw_files':len(before),'window_count':len(windows),'ASD_errors_computed':False,'excluded_mud_radiometric_reads':0,'limits':'six nonmud primary targets; 11x11 B02-B04 imagery; 5x5 native QA per target; no full-scene reads','environment':'existing locked project numpy; installed GDAL C API and CLI; no dependency changes'})
 print('Inspection complete:',len(windows),'windows')
if __name__=='__main__':inspect()
