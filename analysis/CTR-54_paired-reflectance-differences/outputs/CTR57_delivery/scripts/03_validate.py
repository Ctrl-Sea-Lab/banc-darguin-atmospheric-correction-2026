"""Independent direct source-pixel checks, output-grid checks and temporal spot checks."""
from common import *
import numpy as np, math, zipfile, xml.etree.ElementTree as ET
P=json.loads((A/'outputs/pairs.json').read_text());W,H=P[0]['grid']['size'];N=len(P);GT=P[0]['grid']['geotransform']
def pixel(path,col,row):
    s=run(['gdal_translate','-q','-of','XYZ','-srcwin',col,row,1,1,path,'/vsistdout/']);return float(s.split()[-1])
spots=[];times=[];check=[]; fullgrid=[]
audit=list(csv.DictReader((A/'tables/encoded_fill_audit.csv').open()))
summary_rows=list(csv.DictReader((A/'tables/date_band_summary.csv').open()))
for ar in audit:
    sr=next(r for r in summary_rows if r['date']==ar['date'] and r['band']==ar['band'] and r['domain']=='primary')
    assert int(sr['n_ac_encoded_fill'])==int(ar['encoded_default_fill_count'])
    assert int(sr['n_footprint'])<=W*H-int(ar['encoded_default_fill_count'])
sourcegrids=[]
for p in P:
    s=p['sen2cor']
    if s['container'].endswith('.zip'):
        with zipfile.ZipFile(s['container']) as z:
            xml=ET.fromstring(z.read(next(n for n in z.namelist() if n.endswith('MTD_MSIL2A.xml'))))
    else:xml=ET.parse(s['product_metadata']).getroot()
    specials=[]
    for e in xml.iter():
        if e.tag.split('}')[-1]=='Special_Values':
            children={c.tag.split('}')[-1]:c.text for c in e};specials.append((children['SPECIAL_VALUE_TEXT'],int(children['SPECIAL_VALUE_INDEX'])))
    assert ('NODATA',0) in specials and ('SATURATED',65535) in specials
    assert s['quantification']>0
    for b in BANDS:
        j=info(p['sen2cor']['bands'][b]);ref=json.loads((A/'provenance/metadata'/f'{p["id"]}.json').read_text())['sen2cor_reference']
        assert j['size']==ref['size'] and j['geoTransform']==ref['geoTransform'] and j['coordinateSystem']['wkt']==ref['coordinateSystem']['wkt']
        assert j['bands'][0]['type']=='UInt16'
        sourcegrids.append(dict(date=p['date'],band=b,source='Sen2Cor',alignment='exact integer crop',type='UInt16'))
    if p['flags']:
        j=info(p['flags']);assert j['size']==[W,H] and j['geoTransform']==GT and '32628' in j['coordinateSystem']['wkt']
table(A/'tables/source_grid_validation.csv',sourcegrids)
for b in BANDS:
    x=np.memmap(SCRATCH/(b+'_stack.bin'),dtype='<f4',mode='r',shape=(N,H,W))
    # Direct source values at three independent dates for every band.
    for t in [0,N//2,N-1]:
        v=np.flatnonzero(np.isfinite(x[t]));assert v.size
        idx=int(v[len(v)//2]);r,c=divmod(idx,W);p=P[t];ac=pixel(p['acolite'][b],c,r);dn=pixel(p['sen2cor']['bands'][b],c+p['sen2cor_window'][0],r+p['sen2cor_window'][1]);sen=(dn+p['sen2cor']['offsets'][b])/p['sen2cor']['quantification'];d=ac-sen
        actual=pixel(A/'outputs/paired_differences'/f'{p["id"]}_{b}_delta.tif',c,r);error=abs(actual-d);assert error<2e-7,(b,t,error)
        spots.append(dict(date=p['date'],band=b,row=r,col=c,ac_source=ac,sen_dn=dn,sen_reflectance=sen,expected_delta=d,tiff_delta=actual,absolute_error=error))
    # Select cells stratified by observed temporal count, including n=0 or 1 if present.
    count=np.isfinite(x).sum(axis=0)
    assert not np.any(x==np.float32(9.969209968386869e36))
    mm=np.memmap(A/'outputs'/f'{b}_median_display.bin',mode='r',dtype='<f4',shape=(H,W));ss=np.memmap(A/'outputs'/f'{b}_sd_display.bin',mode='r',dtype='<f4',shape=(H,W))
    assert np.array_equal(np.isfinite(mm),count>=1)
    assert np.array_equal(np.isfinite(ss),count>=2)
    fullgrid.append(dict(band=b,n_zero=int((count==0).sum()),n_one=int((count==1).sum()),n_at_least_two=int((count>=2).sum()),median_validity_matches=True,sd_validity_matches=True,encoded_fill_retained=0))
    del mm,ss
    indices=[]
    for n in [0,1,2,N//2,N]:
        ix=np.flatnonzero(count==n)
        if ix.size:indices.append(int(ix[len(ix)//2]))
    ix=np.flatnonzero(count>=2);indices+=list(map(int,ix[np.linspace(0,len(ix)-1,5).astype(int)]))
    for idx in sorted(set(indices)):
        r,c=divmod(idx,W);vals=np.asarray(x[:,r,c],dtype='float64');v=vals[np.isfinite(vals)];expected={'n':len(v),'median':float(np.median(v)) if len(v) else -9999,'sd':float(np.std(v,ddof=1)) if len(v)>1 else -9999}
        for stat,e in expected.items():
            actual=pixel(A/'outputs/temporal'/f'{b}_{stat}.tif',c,r);error=abs(actual-e);assert error<2e-7,(b,stat,error)
            check.append(dict(band=b,row=r,col=c,statistic=stat,expected=e,actual=actual,absolute_error=error))
        for t,vv in enumerate(vals):times.append(dict(band=b,row=r,col=c,date=P[t]['date'],delta=float(vv) if np.isfinite(vv) else None))
    del x
# Every exported raster must match the reference, use documented types and nodata.
rasters=[]
for path in sorted((A/'outputs').rglob('*.tif')):
    j=info(path);assert j['size']==[W,H] and j['geoTransform']==GT and '32628' in j['coordinateSystem']['wkt']
    band=j['bands'][0];assert band['type'] in ['Float32','Byte'];assert band['noDataValue']==(-9999 if band['type']=='Float32' else 255)
    rasters.append(dict(path=str(path.relative_to(A)),width=W,height=H,epsg=32628,type=band['type'],nodata=band['noDataValue']))
table(A/'tables/full_grid_validity_checks.csv',fullgrid);table(A/'tables/source_pixel_checks.csv',spots);table(A/'tables/temporal_pixel_checks.csv',check);table(A/'tables/temporal_samples_for_R.csv',times);table(A/'tables/raster_validation.csv',rasters)
save(A/'provenance/validation.json',dict(status='checks_passed_independent_scientific_review_pending',source_checks=len(spots),max_source_absolute_error=max(s['absolute_error'] for s in spots),temporal_checks=len(check),max_temporal_absolute_error=max(s['absolute_error'] for s in check),rasters_checked=len(rasters),source_inputs_opened_read_only=True,scientific_approval='pending'))
print('VALIDATION',len(spots),len(check),len(rasters))
