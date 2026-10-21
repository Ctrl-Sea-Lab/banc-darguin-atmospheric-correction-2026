"""CTR-59 independent checks; candidate and raw products read only; scratch on /tmp."""
import csv,json,hashlib,subprocess,tempfile,os,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1]; A=R.parents[1]; REPO=A.parents[1]
ROOT=Path('/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026')
P=ROOT/'analysis/CTR-54_paired-reflectance-differences'
pairs=json.loads((A/'outputs/pairs.json').read_text()); bands=['B2','B3','B4','B8']
E={'candidate':'7b9232da45c68c82c5f996b37357f15fb7b9ed55','reviewer':'Karl Popper','checks':[]}
def rows(p): return list(csv.DictReader(p.open()))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def run(a): return subprocess.check_output(list(map(str,a)),env={**os.environ,'GDAL_PAM_ENABLED':'NO','GDAL_CACHEMAX':'128','OPJ_NUM_THREADS':'1'},text=True)
def record(name,**kw):
 E['checks'].append({'check':name,**kw});(R/'provenance/independent_checks.json').write_text(json.dumps(E,indent=2)+'\n');print(name,flush=True)
def info(p):return json.loads(run(['gdalinfo','-json',p]))
def text(root,tag):return next(e.text for e in root.iter() if e.tag.split('}')[-1]==tag)
assert len(pairs)==22 and len({p['key'] for p in pairs})==22
summary=rows(A/'tables/date_band_summary.csv')
manifest={r['path']:r['sha256'] for r in rows(A/'provenance/output_hashes.csv')}
E['candidate_hashes']={f:sha(A/f) for f in ['report.qmd','report.html','figures/generated/paired_reflectance_maps_v2.png','figures/generated/paired_reflectance_maps_v2_preview.png','figures/generated/ctr56_temporal_gam.png','provenance/input_hashes.csv']}
# Direct product XML independently re-opened for all 22 pairs.
metadata=[]
for p in pairs:
 s=p['sen2cor']; container=Path(s['container'])
 if container.suffix=='.zip':
  with zipfile.ZipFile(container) as z:
   pr=ET.fromstring(z.read(next(n for n in z.namelist() if n.endswith('MTD_MSIL2A.xml'))));tr=ET.fromstring(z.read(next(n for n in z.namelist() if n.endswith('MTD_TL.xml'))))
 else:
  pr=ET.parse(container/'MTD_MSIL2A.xml').getroot();tr=ET.parse(next(container.rglob('MTD_TL.xml'))).getroot()
 assert text(pr,'PRODUCT_URI')==s['product'] and text(tr,'SENSING_TIME')==s['sensing_time']
 assert text(tr,'HORIZONTAL_CS_CODE')=='EPSG:32628'
 q=float(text(pr,'BOA_QUANTIFICATION_VALUE')); offsets={int(e.attrib['band_id']):float(e.text) for e in pr.iter() if e.tag.split('}')[-1]=='BOA_ADD_OFFSET'}
 assert q==s['quantification'] and all(offsets[i]==s['offsets'][b] for b,i in zip(bands,[1,2,3,7]))
 ac=info(p['acolite']['B2']); g=ac['metadata']['']; assert g['NC_GLOBAL#isodate'].rstrip('Z')==s['sensing_time'].rstrip('Z') or abs(__import__('datetime').datetime.fromisoformat(g['NC_GLOBAL#isodate'].replace('Z','+00:00')).timestamp()-__import__('datetime').datetime.fromisoformat(s['sensing_time'].replace('Z','+00:00')).timestamp())<.001
 assert ac['size']==[3763,1974] and ac['geoTransform']==[334050,10,0,2209980,0,-10]
 assert s['start'] in g['NC_GLOBAL#inputfile'] and s['tile'] in g['NC_GLOBAL#inputfile'] and s['sensor'] in g['NC_GLOBAL#inputfile']
 metadata.append({'date':p['date'],'sensor':s['sensor'],'tile':s['tile'],'quantification':q,'offsets':offsets,'flags_available':bool(p['flags'])})
record('direct_metadata_all_pairs',pairs=metadata)
with tempfile.TemporaryDirectory(prefix='ctr59-review-',dir='/tmp') as td:
 td=Path(td);counter=0
 def raster(path,window=None,dtype='Float32'):
  global counter
  counter+=1; out=td/f'{counter}.bin';args=['gdal_translate','-q','-of','ENVI','-ot',dtype]
  if window:args+=['-srcwin',*window]
  run(args+[path,out]); shape=(window[3],window[2]) if window else (1974,3763)
  a=np.fromfile(out,dtype={'Float32':'<f4','Int32':'<i4','Byte':'u1'}[dtype]).reshape(shape)
  out.unlink();out.with_suffix('.hdr').unlink(missing_ok=True);return a
 selected=[pairs[0],next(p for p in pairs if p['date']=='2025-03-22'),pairs[-2],pairs[-1]]
 # Two patches selected independently of author points, one includes the crop boundary.
 for p in selected:
  for win in [(0,0,64,64),(1664,896,64,64)]:
   col,row,w,h=win;xo,yo,_,_=p['sen2cor_window'];scl0=raster(p['sen2cor']['scl'],[(xo+col)//2,(yo+row)//2,w//2,h//2],'Byte');scl=np.repeat(np.repeat(scl0,2,axis=0),2,axis=1)
   flags=raster(p['flags'],win,'Int32') if p['flags'] else np.zeros((h,w),dtype='i4')
   g=p['acolite_metadata'];badbits=sum(1<<int(g['NC_GLOBAL#flag_exponent_'+k]) for k in ['cirrus','outofscene','dem_shadow'])
   clear=np.isin(scl,[4,5,6])&((flags&badbits)==0)
   for b in bands:
    ac=raster(p['acolite'][b],win).astype('f8');dn=raster(p['sen2cor']['bands'][b],[xo+col,yo+row,w,h]).astype('f8')
    good=clear&np.isfinite(ac)&(ac!=float(np.float32(9.969209968386869e36)))&(dn!=0)&(dn!=65535)
    expected=(ac-(dn+p['sen2cor']['offsets'][b])/p['sen2cor']['quantification']).astype('f4')
    actual=raster(P/'outputs/paired_differences'/f"{p['id']}_{b}_delta.tif",win)
    assert np.array_equal(good,actual!=-9999),(p['date'],b,'mask')
    err=float(np.max(abs(expected[good].astype('f8')-actual[good]))) if good.any() else 0
    assert err<2e-7
    record('raw_patch',date=p['date'],band=b,window=win,retained=int(good.sum()),excluded=int((~good).sum()),max_error=err)
 for b in bands:
  # Two independent blocks, including low/no support boundary; all dates.
  for win in [(0,0,16,16),(1664,896,16,16)]:
   stack=np.stack([raster(P/'outputs/paired_differences'/f"{p['id']}_{b}_delta.tif",win) for p in pairs]).astype('f8');stack[stack==-9999]=np.nan
   import warnings
   with warnings.catch_warnings():
    warnings.simplefilter('ignore');expected={'n':np.isfinite(stack).sum(axis=0),'median':np.nanmedian(stack,axis=0),'sd':np.nanstd(stack,axis=0,ddof=1)}
   for stat,x in expected.items():
    actual=raster(P/'outputs/temporal'/f'{b}_{stat}.tif',win)
    if stat!='n':actual[actual==-9999]=np.nan
    assert np.array_equal(np.isnan(x),np.isnan(actual))
    error=float(np.nanmax(abs(x-actual))) if np.isfinite(x).any() else 0
    assert error<2e-7
    record('temporal_patch',band=b,statistic=stat,window=win,max_error=error)
  for stat in ['sd','median','n']:
   path=P/'outputs/temporal'/f'{b}_{stat}.tif';assert sha(path)==manifest[path.relative_to(P).as_posix()]
   ar=raster(path);v=ar[(ar!=-9999)&np.isfinite(ar)]
   if stat=='n':
    expected={int(r['valid_dates']):int(r['n_pixels']) for r in rows(A/'tables/temporal_coverage.csv') if r['band']==b}
    assert all(int((ar==k).sum())==n for k,n in expected.items())
    record('support_full_raster',band=b,counts=expected)
   else:
    ref=next(r for r in rows(A/'tables/display_limits_v2.csv') if r['band']==b and r['statistic']==stat)
    lo=float(ref['display_min']);hi=float(ref['display_max']);above=int((v>hi).sum());below=int((v<lo).sum())
    assert len(v)==int(ref['n_finite']) and abs(above/len(v)-float(ref['fraction_clipped_high']))<1e-14 and abs(below/len(v)-float(ref['fraction_clipped_low']))<1e-14
    record('display_full_raster',band=b,statistic=stat,finite=int(v.size),above=above,below=below,fraction_above=above/len(v),minimum=float(v.min()),maximum=float(v.max()),sha256=sha(path))
  # Full primary and fixed-core summaries on a flagged and an unflagged acquisition.
  domain=raster(P/'outputs/temporal'/f'{b}_complete_dates_domain.tif')==1
  for p in [pairs[0],pairs[-1]]:
   path=P/'outputs/paired_differences'/f"{p['id']}_{b}_delta.tif";assert sha(path)==manifest[path.relative_to(P).as_posix()];ar=raster(path)
   for name,mask in [('primary',ar!=-9999),('complete_dates',(ar!=-9999)&domain)]:
    v=ar[mask].astype('f8'); ref=next(r for r in summary if r['pair_id']==p['id'] and r['band']==b and r['domain']==name)
    med=float(np.median(v));sd=float(np.std(v,ddof=1))
    assert len(v)==int(ref['n_valid']) and abs(med-float(ref['median_delta']))<1e-12 and abs(sd-float(ref['sd_delta']))<1e-12
    record('full_spatial_summary',band=b,date=p['date'],domain=name,n=len(v),median=med,sd=sd)
for b in bands:
 rr=[r for r in summary if r['band']==b and r['domain']=='primary'];med=np.array([float(r['median_delta']) for r in rr]);sd=np.array([float(r['sd_delta']) for r in rr]);record('reported_band_summary',band=b,n_dates=len(rr),median_across_date_medians=float(np.median(med)),negative_dates=int((med<0).sum()),min_median=float(med.min()),max_median=float(med.max()),min_spatial_sd=float(sd.min()),max_spatial_sd=float(sd.max()))
E['status']='passed';(R/'provenance/independent_checks.json').write_text(json.dumps(E,indent=2)+'\n')
print('ALL INDEPENDENT CHECKS PASSED',flush=True)
