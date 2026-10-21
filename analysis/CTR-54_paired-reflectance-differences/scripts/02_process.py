"""Exact native-grid differences, disk-backed temporal chunks, paired QA and coverage sensitivity."""
from common import *
import numpy as np, warnings, math, time
from xml.sax.saxutils import escape
P=json.loads((A/'outputs/pairs.json').read_text()); W,H=P[0]['grid']['size'];N=len(P);GT=P[0]['grid']['geotransform'];SCRATCH.mkdir(parents=True,exist_ok=True)
# ENVI is a transparent, documented bridge to the pinned NumPy environment; GDAL owns raster I/O.
def extract(src,name,dtype='Float32',window=None,warp=False):
    out=SCRATCH/(name+'.bin')
    if warp:
        run(['gdalwarp','-q','-overwrite','-of','ENVI','-ot',dtype,'-r','near','-te',GT[0],GT[3]-H*10,GT[0]+W*10,GT[3],'-ts',W,H,'-t_srs','EPSG:32628',src,out])
    else:
        cmd=['gdal_translate','-q','-of','ENVI','-ot',dtype]
        if window:cmd+=['-srcwin',*window]
        run(cmd+[src,out])
    dt={'Float32':'<f4','UInt16':'<u2','Int32':'<i4','Byte':'u1'}[dtype]
    return np.memmap(out,dtype=dt,mode='r',shape=(H,W))
def export(arr,path,description,units='1',dtype='Float32',nodata=-9999):
    path.parent.mkdir(parents=True,exist_ok=True); raw=SCRATCH/'export.bin';vrt=SCRATCH/'export.vrt'
    dt={'Float32':'<f4','Byte':'u1','UInt16':'<u2'}[dtype];aa=np.asarray(arr,dtype=dt)
    if dtype=='Float32':aa=np.where(np.isfinite(aa),aa,nodata).astype(dt)
    aa.tofile(raw);item=np.dtype(dt).itemsize
    vrt.write_text(f'<VRTDataset rasterXSize="{W}" rasterYSize="{H}"><SRS>EPSG:32628</SRS><GeoTransform>{",".join(map(str,GT))}</GeoTransform><Metadata><MDI key="SIGN">ACOLITE minus Sen2Cor</MDI><MDI key="PAIRS">{N}</MDI></Metadata><VRTRasterBand dataType="{dtype}" band="1" subClass="VRTRawRasterBand"><Description>{escape(description)}</Description><UnitType>{units}</UnitType><NoDataValue>{nodata}</NoDataValue><SourceFilename relativeToVRT="0">{raw}</SourceFilename><ImageOffset>0</ImageOffset><PixelOffset>{item}</PixelOffset><LineOffset>{W*item}</LineOffset><ByteOrder>LSB</ByteOrder></VRTRasterBand></VRTDataset>')
    run(['gdal_translate','-q','-of','GTiff','-co','TILED=YES','-co','COMPRESS=DEFLATE','-co','PREDICTOR='+('3' if dtype=='Float32' else '2'),vrt,path])
def summary(x):
    x=np.asarray(x);x=x[np.isfinite(x)].astype('float64');n=x.size
    return dict(n_valid=int(n),median_delta=float(np.median(x)) if n else None,sd_delta=float(x.std(ddof=1)) if n>1 else None,min_delta=float(x.min()) if n else None,max_delta=float(x.max()) if n else None)
def stack(b,mode='r+'):
    return np.memmap(SCRATCH/(b+'_stack.bin'),mode=mode,dtype='<f4',shape=(N,H,W))
# 2.6 GB disk allocation, at most one date's sources and one band held at a time.
for b in BANDS:
    x=stack(b,'w+');x[:]=np.nan;x.flush();del x
footcount=np.zeros((H,W),dtype='uint8');rows=[];quality=[];start=time.monotonic()
for t,p in enumerate(P):
    print('DATE',t+1,N,p['id'],flush=True)
    scl=extract(p['sen2cor']['scl'],'scl','Byte',warp=True)
    flags=extract(p['flags'],'flags','Int32') if p['flags'] else np.zeros((H,W),dtype='int32')
    g=p['acolite_metadata'];bits={k:1<<int(g['NC_GLOBAL#flag_exponent_'+k]) for k in ['cirrus','outofscene','toa','dem_shadow','negative','swir']}
    # SWIR and negative flags do not define invalid terrestrial or dark pixels.
    ac_bad=(flags & (bits['cirrus']|bits['outofscene']|bits['dem_shadow']))!=0
    clear=np.isin(scl,[4,5,6]) & ~ac_bad
    permissive=np.isin(scl,[4,5,6,7]) & ~ac_bad
    strict=clear & ((flags & bits['toa'])==0)
    footprint=np.ones((H,W),dtype=bool)
    q=dict(date=p['date'],id=p['id'],acolite_flags_available=bool(p['flags']),acolite_cirrus_pixels=int(np.count_nonzero(flags & bits['cirrus'])),acolite_outofscene_pixels=int(np.count_nonzero(flags & bits['outofscene'])),acolite_high_toa_pixels=int(np.count_nonzero(flags & bits['toa'])),acolite_negative_flag_pixels=int(np.count_nonzero(flags & bits['negative'])),acolite_swir_flag_pixels=int(np.count_nonzero(flags & bits['swir'])))
    for c in range(12):q['scl_'+str(c)]=int(np.count_nonzero(scl==c))
    quality.append(q)
    for b in BANDS:
        ac=extract(p['acolite'][b],'ac');dn=extract(p['sen2cor']['bands'][b],'dn','UInt16',p['sen2cor_window'])
        # The TIFF deliveries contain the netCDF default Float32 fill despite NoData=NaN.
        # Match that exact sentinel, never a threshold that could discard legitimate reflectance.
        fill=np.float32(9.969209968386869e36)
        encoded_fill=(ac==fill)
        finite=np.isfinite(ac)&~encoded_fill&(dn>0)&(dn<65535);footprint &= finite
        sen=(np.asarray(dn,dtype='float64')+p['sen2cor']['offsets'][b])/p['sen2cor']['quantification']
        delta=np.asarray(ac,dtype='float64')-sen
        valid=finite&clear;d=np.where(valid,delta,np.nan).astype('float32');x=stack(b);x[t]=d;x.flush();del x
        base=dict(date=p['date'],pair_id=p['id'],sensor=p['sen2cor']['sensor'],tile=p['sen2cor']['tile'],band=b,n_grid=W*H,n_footprint=int(finite.sum()),coverage_fraction=float(valid.sum()/(W*H)),footprint_valid_fraction=float(valid.sum()/finite.sum()) if finite.any() else None,n_ac_negative_retained=int(np.count_nonzero(valid&(ac<0))),n_sen_negative_retained=int(np.count_nonzero(valid&(sen<0))),n_ac_encoded_fill=int(encoded_fill.sum()),flags_available=bool(p['flags']),exclusion_reason='' if valid.any() else 'No pixels pass paired QA')
        rows.append({**base,'domain':'primary',**summary(d)})
        rows.append({**base,'domain':'include_SCL7',**summary(np.where(finite&permissive,delta,np.nan))})
        rows.append({**base,'domain':'exclude_high_TOA',**summary(np.where(finite&strict,delta,np.nan))})
        export(d,A/'outputs/paired_differences'/f'{p["id"]}_{b}_delta.tif',f'{p["id"]} {b} paired delta reflectance')
        del ac,dn,sen,delta,d
    footcount+=footprint
    del scl,flags,ac_bad,clear,permissive,strict,footprint
export(footcount,A/'outputs/temporal/footprint_count.tif','Number of dates with finite paired observations in all four bands before QA','dates','Byte',255)
np.save(SCRATCH/'footcount.npy',footcount)
# Exact temporal statistics per cell using all retained dates, no raster subsampling.
statrows=[];coverrows=[]
for b in BANDS:
    print('TEMPORAL',b,flush=True);x=stack(b,'r');med=np.full((H,W),np.nan,'float32');sd=med.copy();count=np.zeros((H,W),'uint8')
    for r in range(0,H,64):
        ch=np.asarray(x[:,r:r+64,:],dtype='float64');ct=np.isfinite(ch).sum(axis=0)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore',RuntimeWarning);m=np.nanmedian(ch,axis=0);s=np.nanstd(ch,axis=0,ddof=1)
        med[r:r+64]=m;sd[r:r+64]=s;count[r:r+64]=ct
    for name,ar in [('median',med),('sd',sd),('n',count)]:
        export(ar,A/'outputs/temporal'/f'{b}_{name}.tif',f'{b} temporal {name} delta reflectance' if name!='n' else f'{b} number of valid paired dates', 'dates' if name=='n' else '1','Byte' if name=='n' else 'Float32',255 if name=='n' else -9999)
        if name!='n':
            ar.astype('<f4').tofile(A/'outputs'/f'{b}_{name}_display.bin')
            statrows.append(dict(band=b,statistic=name,**summary(ar),p01=float(np.nanquantile(ar,.01)),p50=float(np.nanquantile(ar,.5)),p99=float(np.nanquantile(ar,.99))))
    for n in range(N+1):coverrows.append(dict(band=b,valid_dates=n,n_pixels=int((count==n).sum()),fraction_grid=float((count==n).mean())))
    for name,mask in [('complete_dates',count==N),('coverage80',count>=math.ceil(.8*N)),('common_footprint',footcount==N)]:
        export(mask.astype('uint8'),A/'outputs/temporal'/f'{b}_{name}_domain.tif',f'{b} {name} spatial sensitivity domain','1','Byte',255)
        for t,p in enumerate(P):
            base=next(row for row in rows if row['pair_id']==p['id'] and row['band']==b and row['domain']=='primary')
            rows.append({**base,'domain':name,**summary(x[t][mask]),'coverage_fraction':float(np.count_nonzero(np.isfinite(x[t])&mask)/(W*H))})
    del x,med,sd,count
# Fix domain-specific fractions, negatives/footprint are primary diagnostics and explicitly labelled in schema.
for row in rows:row['coverage_fraction']=int(row['n_valid'])/(W*H)
table(A/'tables/date_band_summary.csv',rows);table(A/'tables/quality_counts.csv',quality);table(A/'tables/temporal_raster_summary.csv',statrows);table(A/'tables/temporal_coverage.csv',coverrows)
save(A/'provenance/processing.json',dict(pairs=N,width=W,height=H,epsg=32628,geotransform=GT,units='dimensionless reflectance',sign='ACOLITE minus Sen2Cor',mask={'SCL_keep':[4,5,6],'SCL_sensitivity_keep':[4,5,6,7],'ACOLITE_rejected_flags':['cirrus','outofscene','dem_shadow'],'ACOLITE_high_TOA':'sensitivity only; bright terrestrial reflectance is not automatically invalid','ACOLITE_SWIR_and_negative':'retained; no marine-only or positivity selection','missing_flags':'Sen2Cor SCL and finite observations only; no independent ACOLITE QA'},n_dates_without_ac_flags=sum(not p['flags'] for p in P),elapsed_seconds=time.monotonic()-start,chunk_rows=64,encoded_fill_value=float(np.float32(9.969209968386869e36)),temporal_sd_ddof=1,spatial_sd_ddof=1,median_minimum_n=1,sd_minimum_n=2))
print('DONE seconds',time.monotonic()-start,flush=True)
