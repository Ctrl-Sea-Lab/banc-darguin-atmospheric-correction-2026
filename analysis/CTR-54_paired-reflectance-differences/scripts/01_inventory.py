"""Inspect source metadata; pair actual datatake/sensor/tile and exact tile times."""
from common import *
import re, zipfile, xml.etree.ElementTree as ET
from datetime import datetime
PAT = r'(S2[ABC])_MSIL[12][AC]_(\d{8}T\d{6})_N(\d{4})_R(\d{3})_(T\w{5})_(\d{8}T\d{6})'
def local(root,tag):
    return next(e for e in root.iter() if e.tag.split('}')[-1]==tag)
def text(root,tag):return local(root,tag).text
def sen(container):
    iszip=container.suffix=='.zip'
    if iszip:
        with zipfile.ZipFile(container) as z:
            names=z.namelist(); pm=next(x for x in names if x.endswith('MTD_MSIL2A.xml'));tm=next(x for x in names if x.endswith('MTD_TL.xml'));p=ET.fromstring(z.read(pm));t=ET.fromstring(z.read(tm))
        path=lambda name:'/vsizip/'+str(container)+'/'+name
    else:
        names=[str(x.relative_to(container)) for x in container.rglob('*') if x.is_file()];pm='MTD_MSIL2A.xml';tm=next(x for x in names if x.endswith('MTD_TL.xml'));p=ET.parse(container/pm).getroot();t=ET.parse(container/tm).getroot();path=lambda name:str(container/name)
    product=text(p,'PRODUCT_URI');m=re.search(PAT,product);assert m
    sensor,start,baseline,orbit,tile,generation=m.groups()
    bandpaths={b:path(next(x for x in names if x.endswith(f'_B{int(b[1:]):02d}_10m.jp2'))) for b in BANDS}
    scl=path(next(x for x in names if x.endswith('_SCL_20m.jp2')))
    offsets={int(e.attrib['band_id']):float(e.text) for e in p.iter() if e.tag.split('}')[-1]=='BOA_ADD_OFFSET'}
    assert text(p,'PROCESSING_LEVEL')=='Level-2A';assert text(t,'HORIZONTAL_CS_CODE')=='EPSG:32628'
    centers={e.attrib['physicalBand']:float(text(e,'CENTRAL')) for e in p.iter() if e.tag.split('}')[-1]=='Spectral_Information'}
    return dict(container=str(container),product=product,key='|'.join([sensor,start,orbit,tile]),sensor=sensor,start=start,baseline=baseline,orbit=orbit,tile=tile,generation=generation,sensing_time=text(t,'SENSING_TIME'),tile_id=text(t,'TILE_ID'),l1c_tile_id=text(t,'L1C_TILE_ID'),quantification=float(text(p,'BOA_QUANTIFICATION_VALUE')),offsets={b:offsets[{'B2':1,'B3':2,'B4':3,'B8':7}[b]] for b in BANDS},bands=bandpaths,scl=scl,central_wavelengths_nm={b:centers['B'+str(int(b[1:]))] for b in BANDS},product_metadata=path(pm),tile_metadata=path(tm))
candidates=[sen(p) for p in sorted((SOURCE/'Sen2Cor').glob('*.zip'))]+[sen(p) for p in sorted(SOURCE.glob('*.SAFE'))]
# Deterministically select the highest processing baseline then generation, never double-count.
chosen={}
for s in candidates:
    if s['key'] not in chosen or (s['baseline'],s['generation'],s['container'])>(chosen[s['key']]['baseline'],chosen[s['key']]['generation'],chosen[s['key']]['container']):chosen[s['key']]=s
pairs=[];rows=[];mapping=[];usedkeys=set();raw=[]
for d in sorted((SOURCE/'ACOLITE').iterdir()):
    if not d.is_dir():continue
    first=next(d.glob('*rhos_*.tif'));j=info(first);g=j['metadata'][''];m=re.search(PAT,g['NC_GLOBAL#inputfile']);assert m
    sensor,start,baseline,orbit,tile,generation=m.groups();key='|'.join([sensor,start,orbit,tile]);s=chosen.get(key)
    ar={'processor':'ACOLITE','path':str(d),'sensor':sensor,'datatake_start':start,'tile':tile,'orbit':orbit,'status':'paired' if s else 'excluded','reason':'' if s else 'No same-sensor/datatake/tile Sen2Cor product','key':key};rows.append(ar)
    if not s:continue
    assert sensor==g['NC_GLOBAL#sensor'].split('_')[0] and tile==g['NC_GLOBAL#mgrs_tile']
    dt=lambda x:datetime.fromisoformat(x.replace('Z','+00:00'))
    difference=abs((dt(g['NC_GLOBAL#isodate'])-dt(s['sensing_time'])).total_seconds());assert difference<0.001
    assert re.search(r'_A\d+_',s['l1c_tile_id']).group() in ('_'+g['NC_GLOBAL#granule']+'_')
    ab={};metadata={}
    for b in BANDS:
        label=g['NC_GLOBAL#'+b[1:]+'_name'];p=next(d.glob('*_rhos_'+label+'.tif'));q=info(p);bm=q['bands'][0];md=bm['metadata']['']
        assert bm['type']=='Float32' and bm.get('scale',1)==1 and bm.get('offset',0)==0
        assert bm.get('unit')=='1' and md['standard_name']=='surface_bidirectional_reflectance' and md['parameter']=='rhos_'+label
        assert q['geoTransform']==j['geoTransform'] and q['size']==j['size'] and q['coordinateSystem']['wkt']==j['coordinateSystem']['wkt']
        ab[b]=str(p);metadata[b]=q
        mapping.append(dict(date=start[:8],sensor=sensor,band=b,acolite_parameter=md['parameter'],acolite_effective_wavelength_nm=md['wavelength'],sen2cor_central_wavelength_nm=s['central_wavelengths_nm'][b],acolite_units='1',sen2cor_scale=1/s['quantification'],sen2cor_offset_dn=s['offsets'][b]))
    sm=info(s['bands']['B2']);assert sm['geoTransform'][1:]==[10.,0.,2300040.,0.,-10.] and sm['size']==[10980,10980]
    assert '32628' in sm['coordinateSystem']['wkt'] and '32628' in j['coordinateSystem']['wkt']
    gt=j['geoTransform'];xoff=(gt[0]-sm['geoTransform'][0])/10;yoff=(sm['geoTransform'][3]-gt[3])/10
    assert xoff==int(xoff) and yoff==int(yoff)
    flags=sorted(d.glob('*_l2_flags.tif'))
    p=dict(id=start[:8]+'_'+sensor+'_'+tile,date=f'{start[:4]}-{start[4:6]}-{start[6:8]}',key=key,acolite_directory=str(d),acolite=ab,flags=str(flags[0]) if flags else None,acolite_metadata=g,sen2cor=s,grid={'size':j['size'],'geotransform':gt,'epsg':32628},sen2cor_window=[int(xoff),int(yoff),*j['size']],time_difference_seconds=difference)
    pairs.append(p);usedkeys.add(key)
    save(A/'provenance/metadata'/f'{p["id"]}.json',{'acolite':metadata,'sen2cor_reference':sm})
for s in candidates:
    status='paired' if s['key'] in usedkeys and chosen[s['key']]==s else 'excluded'
    reason='' if status=='paired' else ('Superseded processing version' if chosen[s['key']]!=s else 'No same-sensor/datatake/tile ACOLITE footprint')
    rows.append(dict(processor='Sen2Cor',path=s['container'],sensor=s['sensor'],datatake_start=s['start'],tile=s['tile'],orbit=s['orbit'],status=status,reason=reason,key=s['key']))
pairs.sort(key=lambda p:p['date']);assert len(set(p['key'] for p in pairs))==len(pairs)
assert all(p['grid']==pairs[0]['grid'] for p in pairs)
save(A/'outputs/pairs.json',pairs);table(A/'tables/acquisition_inventory.csv',rows);table(A/'tables/band_mapping.csv',mapping)
w,h=pairs[0]['grid']['size'];n=len(pairs)
save(A/'provenance/resource_estimate.json',dict(pairs=n,pixels=w*h,grid=pairs[0]['grid'],delta_stack_bytes=n*w*h*4*4,scratch_budget_GiB=12,working_memory_target_GiB=1.5,chunk_rows=64,gdal_cache_MiB=256,method='Sequential cropped GDAL extraction, NumPy disk-backed delta arrays; 64-row temporal chunks; no full SAFE extraction'))
print(json.dumps({'pairs':n,'dates':[p['date'] for p in pairs],'candidates':len(rows),'excluded':[r for r in rows if r['processor']=='ACOLITE' and r['status']=='excluded']}))
