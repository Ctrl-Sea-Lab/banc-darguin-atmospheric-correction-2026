#!/usr/bin/env python3
"""CTR42: bounded March 7 containing-cell spectra; no performance metrics or plots.
Run from project root: .venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr42_extract.py
Uses existing locked numpy and installed GDAL CLI/C API. Raw files always read-only.
Workbook reader, raster access and convolution adapted from saved CTR34 scripts;
all original method hashes are recorded. This script writes only CTR27 ctr42_* files.
"""
import csv, ctypes as C, ctypes.util, datetime as D, hashlib, json, math, os
import platform, subprocess, sys, zipfile
from pathlib import Path
import xml.etree.ElementTree as E
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
P = Path(__file__).resolve().parents[1]
OLD = ROOT / 'analysis/CTR-24_data-dictionary'
RAW = ROOT / 'data/raw'
BANDS = ['B01','B02','B03','B04','B05','B06','B07','B08','B8A']
WAVES = dict(zip(BANDS, ['442','492','559','665','704','739','780','833','864']))
RES = {b: 10 if b in ['B02','B03','B04','B08'] else 60 if b == 'B01' else 20 for b in BANDS}
EXCLUDED = {'AC03': 'mbp_mud', 'AC04': 'mpb_mud'}
os.environ.update(GDAL_PAM_ENABLED='NO', CPL_TMPDIR='/tmp', PROJ_NETWORK='OFF', GDAL_NUM_THREADS='1')

def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda: f.read(4*1024*1024), b''): h.update(block)
    return h.hexdigest()

def rel(p): return str(Path(p).relative_to(ROOT))
def rows(p):
    with Path(p).open(newline='') as f: return list(csv.DictReader(f))
def js(p): return json.loads(Path(p).read_text())
def dump(name, obj): (P/name).write_text(json.dumps(obj, indent=2, allow_nan=False)+'\n')
def table(name, rs):
    with (P/'tables'/name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rs[0]), lineterminator='\n'); w.writeheader()
        w.writerows({k: 'NA' if v is None else v for k,v in r.items()} for r in rs)
def run(args, inp=None): return subprocess.check_output(args, text=True, input=inp, timeout=90)
def only(ps):
    ps=list(ps); assert len(ps)==1, [str(p) for p in ps]; return ps[0]
def xmlvalues(p):
    out={}
    for e in E.parse(p).iter():
        if len(e)==0 and e.text and e.text.strip(): out.setdefault(e.tag.split('}')[-1], []).append(e.text.strip())
    return out

def workbook(p):
    ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(p) as z:
        strings=[''.join(x.itertext()) for x in E.fromstring(z.read('xl/sharedStrings.xml'))] if 'xl/sharedStrings.xml' in z.namelist() else []
        links={r.get('Id'):r.get('Target') for r in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))}; sheets={}
        for sh in E.fromstring(z.read('xl/workbook.xml')).find('m:sheets',ns):
            t=links[sh.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
            t=t.lstrip('/') if t.startswith('/') else 'xl/'+t
            rr=[]
            for row in E.fromstring(z.read(t)).findall('.//m:sheetData/m:row',ns):
                cells={}
                for c in row:
                    v=c.find('m:v',ns); v=v.text if v is not None else ''.join(c.itertext())
                    if c.get('t')=='s' and v: v=strings[int(v)]
                    if v: cells[''.join(filter(str.isalpha,c.get('r')))]=v
                if cells: rr.append({'row':int(row.get('r')), 'cells':cells})
            sheets[sh.get('name')]=rr
        return sheets

def curves(p):
    rr=workbook(p)['Spectral Responses (S2B)']; out={}
    for col, label in rr[0]['cells'].items():
        if 'SR_AV_B' not in label: continue
        raw=label.split('SR_AV_')[-1]; band='B'+raw[1:].zfill(2) if raw[1:].isdigit() else raw.upper()
        v=[]
        for r in rr[1:]:
            try: v.append((float(r['cells']['A']),float(r['cells'][col])))
            except (KeyError,ValueError): pass
        if v: out[band]={'column':col, 'label':label, 'curve':np.asarray(v)}
    return out

def convolve(wl, refl, curve):
    # Exact saved CTR34 union-knot trapezoid rule, without extrapolation.
    x,r=curve.T; assert np.all(np.diff(x)>0) and np.all(r>=0)
    den=float(np.trapezoid(r,x)); inside=(x>=wl[0])&(x<=wl[-1])
    coverage=float(np.trapezoid(r[inside],x[inside])/den)
    if coverage<.999: return None,'insufficient_coverage',None,den,coverage
    for i in range(len(wl)-1):
        if not (np.isfinite(refl[i]) and np.isfinite(refl[i+1]) and wl[i+1]-wl[i]<=1):
            xx=x[(x>=wl[i])&(x<=wl[i+1])]
            if (np.interp(np.r_[wl[i],xx,wl[i+1]],x,r,left=0,right=0)>0).any():
                return None,'missing_positive_response_interval',None,den,coverage
    knots=np.union1d(x,wl); rr=np.interp(knots,x,r,left=0,right=0); needed=rr>0
    if ((knots[needed]<wl[0])|(knots[needed]>wl[-1])).any():
        return None,'positive_response_outside_ASD',None,den,coverage
    prod=np.zeros(knots.shape); prod[needed]=np.interp(knots[needed],wl,refl)*rr[needed]
    num=float(np.trapezoid(prod,knots)); return num/den,'pass',num,den,coverage

class Raster:
    lib=C.CDLL(ctypes.util.find_library('gdal')); lib.GDALAllRegister()
    for fn,args,ret in [('GDALOpen',[C.c_char_p,C.c_int],C.c_void_p),('GDALGetRasterBand',[C.c_void_p,C.c_int],C.c_void_p),('GDALClose',[C.c_void_p],None),('GDALRasterIO',[C.c_void_p,C.c_int,C.c_int,C.c_int,C.c_int,C.c_int,C.c_void_p,C.c_int,C.c_int,C.c_int,C.c_int,C.c_int],C.c_int)]:
        f=getattr(lib,fn); f.argtypes=args; f.restype=ret
    def __init__(self,p):
        self.path=p; self.h=json.loads(run(['gdalinfo','-json','-noct','-nogcp',str(p)]))
        assert '32628' in self.h['coordinateSystem']['wkt']
        self.ds=self.lib.GDALOpen(str(p).encode(),0); assert self.ds
        g=self.h['geoTransform']; assert g[2]==g[4]==0 and g[1]>0 and g[5]<0
    def index(self,x,y):
        g=self.h['geoTransform']; return math.floor((x-g[0])/g[1]), math.floor((y-g[3])/g[5])
    def bounds(self,c,r):
        g=self.h['geoTransform']; x=g[0]+c*g[1]; y=g[3]+r*g[5]; return [x,y+g[5],x+g[1],y]
    def read(self,c,r,nx=1,ny=1,band=1):
        assert c>=0 and r>=0 and c+nx<=self.h['size'][0] and r+ny<=self.h['size'][1]
        v=np.empty((ny,nx),dtype='<f8')
        assert self.lib.GDALRasterIO(self.lib.GDALGetRasterBand(self.ds,band),0,c,r,nx,ny,v.ctypes.data_as(C.c_void_p),nx,ny,7,0,0)==0
        return v
    def close(self): self.lib.GDALClose(self.ds)

def main():
    started=D.datetime.now(D.timezone.utc).isoformat()
    sources={}; cache={}; windows=[]; headers={}
    def track(p,role):
        p=Path(p); n=rel(p)
        if n not in sources:
            st=p.stat(); sources[n]=dict(path=n,role=role,bytes=st.st_size,mtime_ns=st.st_mtime_ns,sha256=sha(p),hash_scope='full_file_SHA256')
        return p
    def raster(p,role):
        p=track(p,role); n=rel(p)
        if n not in cache: cache[n]=Raster(p); headers[n]=cache[n].h
        return cache[n]
    def sample(rr,sid,band,method,c,r,nx=1,ny=1,layer=1):
        v=rr.read(c,r,nx,ny,layer)
        windows.append(dict(station_id=sid,band_id=band,method=method,source_path=rel(rr.path),layer=layer,col_start=c,row_start=r,cols=nx,rows=ny,raw_float64_le_sha256=hashlib.sha256(v.tobytes()).hexdigest(),hash_scope='decoded raw stored-cell window, before radiometric scale',values_json=json.dumps(v.tolist())))
        return v
    cross=P/'tables/station_crosswalk.csv'; inv=P/'tables/ctr36_nonmud_station_inventory.csv'
    st=rows(track(cross,'saved station identity crosswalk')); inventory=rows(track(inv,'saved retained population'))
    assert len(st)==15 and len(inventory)==13
    assert {s['station_id'] for s in st if s['station_id'] not in EXCLUDED}=={s['station_id'] for s in inventory}
    for f in ['scripts/ctr34_extract.py','scripts/ctr34_support.py','scripts/ctr34_audit.py']:
        track(OLD/f,'saved method provenance; not executed')
    for f in ['tables/ctr34_convolved_references.csv','tables/ctr34_target_decisions.csv','tables/ctr36_exclusions.csv']:
        track(P/f,'prior evidence; not modified')
    for f in ['uv.lock','renv.lock','pyproject.toml']: track(ROOT/f,'locked environment')
    asd=track(ROOT/st[0]['asd_path'],'raw station-average ASD'); gps=track(ROOT/st[0]['gps_path'],'raw GPS workbook')
    cover=track(ROOT/st[0]['cover_path'],'raw cover labels'); log=track(RAW/'ASD/202603_Measurement_log.txt','raw field date log')
    assert 'day06 20260327' in log.read_text()
    names=asd.open().readline().split(); arr=np.loadtxt(asd,skiprows=1); wl=arr[:,0]
    assert len(names)==arr.shape[1] and len(set(names))==len(names) and np.array_equal(wl,np.arange(400,901))
    gg=workbook(gps)['Sheet1']; gh=gg[0]['cells']; gp=[{gh[k]:v for k,v in r['cells'].items() if k in gh} for r in gg[1:]]
    with cover.open() as f: cc=list(csv.DictReader(f,delimiter='\t'))
    stations=[]; exclusions=[]
    for s in st:
        sid=s['station_id']; g=only(r for r in gp if r.get('station')==sid); c=only(r for r in cc if r['station']==sid)
        date=(D.datetime(1899,12,30)+D.timedelta(days=float(g['date']))).date().isoformat()
        assert date==s['field_date']=='2026-03-27'
        assert float(g['lon'])==float(s['lon_raw']) and float(g['lat'])==float(s['lat_raw']) and c['comment']==s['target_class_raw']
        if sid in EXCLUDED:
            assert c['comment']==EXCLUDED[sid]; exclusions.append(dict(station_id=sid,class_literal=c['comment'],reason='original_PI_mud_exclusion',radiometric_reads=0,reference_integrations=0)); continue
        assert s['asd_column_raw'] in names
        stations.append(dict(station_id=sid,ASD_column=s['asd_column_raw'],class_literal=s['target_class_raw'],role='primary_intended' if sid.startswith('AC') else 'supplementary_only',longitude=float(s['lon_raw']),latitude=float(s['lat_raw']),coordinate_CRS='EPSG:4326',field_date=date,field_clock_timezone='unknown',acquisition_date='2026-03-07',field_minus_satellite_days=20,coordinate_identity='saved explicit crosswalk rechecked against raw GPS and cover',coordinate_accuracy='unknown',geographic_group='Iwik' if sid in ['AC01','AC02'] else 'offshore_Arel',geographic_evidence='prior authenticated PI correction for AC01/02; raw Arel location retained unchanged',validation_eligible=False))
    xy=run(['gdaltransform','-s_srs','EPSG:4326','-t_srs','EPSG:32628'], '\n'.join(f"{s['longitude']} {s['latitude']}" for s in stations)).splitlines()
    for s,line in zip(stations,xy): s.update(zip(['x_32628_m','y_32628_m'],map(float,line.split()[:2])))
    safe=only((RAW/'S2').glob('*20260307*.SAFE')); gran=only(safe.glob('GRANULE/*'))
    prod=track(safe/'MTD_MSIL2A.xml','Sen2Cor product metadata'); tile=track(gran/'MTD_TL.xml','Sen2Cor tile metadata')
    pv,tv=xmlvalues(prod),xmlvalues(tile)
    assert pv['SPACECRAFT_NAME']==['Sentinel-2B'] and pv['PROCESSING_BASELINE']==['05.12']
    assert pv['BOA_QUANTIFICATION_VALUE']==['10000'] and pv['BOA_ADD_OFFSET']==['-1000']*13
    assert tv['HORIZONTAL_CS_CODE']==['EPSG:32628'] and tv['SENSING_TIME']==['2026-03-07T11:45:54.425534Z']
    quant=float(pv['BOA_QUANTIFICATION_VALUE'][0]); offsets={int(e.get('band_id')):float(e.text) for e in E.parse(prod).iter() if e.tag.split('}')[-1]=='BOA_ADD_OFFSET'}
    band_indices={b:i for i,b in enumerate(['B01','B02','B03','B04','B05','B06','B07','B08','B8A','B09','B10','B11','B12'])}
    sml=['PRODUCT_START_TIME','PRODUCT_URI','PROCESSING_BASELINE','SPACECRAFT_NAME','DATATAKE_SENSING_START','SENSING_ORBIT_NUMBER']
    scene=dict(scene_pair_id='S2B_20260307_R080_T28QCH_A047010',same_acquisition_evidence='exact tile sensing time plus S2B, T28QCH, orbit A047010, datatake 20260307T113319 and L1C tile processing identity; original upstream L1C bytes not available',sen2cor_product={k:pv[k] for k in sml},sen2cor_tile={k:tv[k] for k in ['SENSING_TIME','L1C_TILE_ID','TILE_ID','HORIZONTAL_CS_CODE']},metadata_consistent_same_acquisition=True,byte_identical_L1C_ancestry_verified=False,alternatives='no equally plausible early-March 2026 pair in current product roots; March 2025 and 27 March 2026 not substituted')
    scl_labels={}
    for e in E.parse(prod).iter():
        if e.tag.split('}')[-1]=='Scene_Classification_ID':
            labels={c.tag.split('}')[-1]:c.text for c in e}
            scl_labels[labels['SCENE_CLASSIFICATION_INDEX']]=labels['SCENE_CLASSIFICATION_TEXT']
    scene['SCL_labels_from_product_XML']=scl_labels
    sat=[]; qa=[]; contracts=[]
    sclpath=only(gran.glob('IMG_DATA/R20m/*_SCL_20m.jp2')); scl=raster(sclpath,'Sen2Cor SCL QA')
    for b in BANDS:
        ap=only((RAW/'S2/ACOLITE/20260307').glob('*_rhos_'+WAVES[b]+'.tif'))
        sp=only(gran.glob(f'IMG_DATA/R{RES[b]}m/*_{b}_{RES[b]}m.jp2'))
        aa=raster(ap,'ACOLITE surface reflectance '+b); ss=raster(sp,'Sen2Cor native stored band '+b)
        am=aa.h['metadata']['']; ab=aa.h['bands'][0]; bm=ab['metadata']['']
        assert am['NC_GLOBAL#sensor']=='S2B_MSI' and am['NC_GLOBAL#granule']=='L1C_T28QCH_A047010_20260307T114112'
        assert D.datetime.fromisoformat(am['NC_GLOBAL#isodate'])==D.datetime.fromisoformat(tv['SENSING_TIME'][0].replace('Z','+00:00'))
        assert 'S2B_MSIL1C_20260307T113319_N0512_R080_T28QCH_20260307T153536.SAFE' in am['NC_GLOBAL#inputfile']
        assert tv['L1C_TILE_ID'][0]=='S2B_OPER_MSI_L1C_TL_2BPS_20260307T153536_A047010_T28QCH_N05.12'
        assert bm['NETCDF_VARNAME']=='rhos_'+WAVES[b] and ab['unit']=='1' and bm['standard_name']=='surface_bidirectional_reflectance'
        assert ab.get('scale',1)==1 and ab.get('offset',0)==0 and ab['type']=='Float32'
        assert aa.h['geoTransform'][1]==10 and ss.h['geoTransform'][1]==RES[b]
        assert all(abs((aa.h['geoTransform'][i]-ss.h['geoTransform'][i])/10-round((aa.h['geoTransform'][i]-ss.h['geoTransform'][i])/10))<1e-9 for i in [0,3])
        lineage_keys=['sensor','granule','inputfile','isodate','acolite_version','atmospheric_correction_method','ac_model','l2w_mask','rsr_version','s2_target_res','output_projection_resampling_method','warp_resampling_method']
        if b==BANDS[0]: scene['acolite']={k:am.get('NC_GLOBAL#'+k) for k in lineage_keys}
        contracts.append(dict(band_id=b,platform='S2B',sensor_native_resolution_m=RES[b],sen2cor_path=rel(sp),sen2cor_stored_resolution_m=RES[b],sen2cor_quantification=quant,sen2cor_add_offset_DN=offsets[band_indices[b]],sen2cor_nodata_DN=0,sen2cor_saturation_DN=65535,acolite_path=rel(ap),acolite_variable=bm['NETCDF_VARNAME'],acolite_wavelength_nm=float(bm['wave_nm']),acolite_stored_resolution_m=10,acolite_units=ab['unit'],acolite_nodata=ab.get('noDataValue'),acolite_scale=1,acolite_offset=0,acolite_mask=am.get('NC_GLOBAL#l2w_mask'),acolite_resampling_evidence='10m exported grid; bilinear warp/output settings present; exact upstream bandwise interpolation kernel/weights unverified',extraction='single containing stored cell per correction; no resampling by CTR42',effective_optical_support='unverified; stored footprint and native sensor resolution are not effective PSF',same_grid_role='10m grids nominally nested; unequal stored footprints for coarser Sen2Cor bands; no pixelwise subtraction'))
        for s in stations:
            sid=s['station_id']; x,y=s['x_32628_m'],s['y_32628_m']
            footprints={}
            for method,rr in [('Sen2Cor',ss),('ACOLITE',aa)]:
                col,row=rr.index(x,y); inside=0<=col<rr.h['size'][0] and 0<=row<rr.h['size'][1]
                raw=None; value=None; reason='outside_raster_extent'
                if inside:
                    raw=float(sample(rr,sid,b,method,col,row)[0,0]); reason='available_stored_value'
                    nd=rr.h['bands'][0].get('noDataValue')
                    if not math.isfinite(raw): reason='nonfinite_or_nodata'
                    elif method=='Sen2Cor' and raw in [0,65535]: reason='nodata_DN_0' if raw==0 else 'saturated_DN_65535'
                    elif nd is not None and str(nd).lower()!='nan' and raw==float(nd): reason='declared_nodata'
                    else: value=(raw+offsets[band_indices[b]])/quant if method=='Sen2Cor' else raw
                bbox=rr.bounds(col,row); footprints[method]=bbox
                sat.append(dict(station_id=sid,class_literal=s['class_literal'],population=s['role'],band_id=b,correction=method,scene_pair_id=scene['scene_pair_id'],tile_sensing_time=tv['SENSING_TIME'][0],field_date=s['field_date'],field_minus_satellite_days=20,source_path=rel(rr.path),source_sha256=sources[rel(rr.path)]['sha256'],row_0based=row,col_0based=col,stored_resolution_m=rr.h['geoTransform'][1],sensor_native_resolution_m=RES[b],cell_bounds_EPSG32628_json=json.dumps(bbox),raw_value=raw if raw is not None and math.isfinite(raw) else None,reflectance=value,unit='1',availability_reason=reason,negative_retained=value is not None and value<0,quality_disposition='stored numeric value; inspect raw QA table; not independently validated',validation_eligible=False,hold_reason='field_20_days_after_satellite;overpass_optical_state_unresolved;effective_support_unverified;GPS_registration_accuracy_unknown;'+('supplementary_support_not_established' if sid.startswith('D06') else 'prior_physical_holds_retained')))
            # Raw QA for every cell overlapping each stored radiometric footprint.
            # This is a bounded geometric audit, not a claim about full effective PSF.
            for method,bbox in footprints.items():
                qp=[('SCL',scl)]
                if method=='Sen2Cor':
                    for kind in ['QUALIT','DETFOO']:
                        p=gran/'QI_DATA'/f'MSK_{kind}_{b}.jp2'
                        if p.exists(): qp.append((kind,raster(p,'Sen2Cor native QA '+kind+' '+b)))
                        else: qa.append(dict(station_id=sid,band_id=b,correction=method,kind=kind,source_path=rel(p),layer=None,col_start=None,row_start=None,cols=0,rows=0,cell_counts_json='{}',status='missing_QA_file'))
                for kind,rr in qp:
                    eps=1e-5; c0,r0=rr.index(bbox[0]+eps,bbox[3]-eps); c1,r1=rr.index(bbox[2]-eps,bbox[1]+eps)
                    nx,ny=c1-c0+1,r1-r0+1
                    if c0<0 or r0<0 or c1>=rr.h['size'][0] or r1>=rr.h['size'][1]:
                        qa.append(dict(station_id=sid,band_id=b,correction=method,kind=kind,source_path=rel(rr.path),layer=None,col_start=c0,row_start=r0,cols=nx,rows=ny,cell_counts_json='{}',status='QA_extent_incomplete')); continue
                    for layer in range(1,len(rr.h['bands'])+1):
                        v=sample(rr,sid,b,method+'_QA_'+kind,c0,r0,nx,ny,layer); vals,counts=np.unique(v,return_counts=True)
                        qa.append(dict(station_id=sid,band_id=b,correction=method,kind=kind,source_path=rel(rr.path),layer=layer,col_start=c0,row_start=r0,cols=nx,rows=ny,cell_counts_json=json.dumps({str(int(a)):int(n) for a,n in zip(vals,counts)},sort_keys=True),status='raw_codes_over_stored_cell_footprint;not_effective_support_clearance'))
    for rr in cache.values(): rr.close()
    v4=track(only(RAW.glob('*.xlsx')),'supplied S2B SRF v4 primary')
    v5=track(OLD/'outputs/official-srf-v5.xlsx','saved official S2B SRF v5 sensitivity')
    assert sha(v5)=='42be3ebd8bfcbde11c37caeb2e2fdda65fefa8d2b6f8329559b7806d02cdc9e2'
    refs=[]; coverage=[]
    prior={(r['station_id'],r['band_id'],r['SRF_role']):r for r in rows(P/'tables/ctr34_convolved_references.csv')}
    for role,path in [('v4_primary',v4),('v5_sensitivity',v5)]:
        cur=curves(path)
        for b in BANDS:
            cv=cur[b]; xx,rr=cv['curve'].T; pos=rr>0
            for s in stations:
                y=arr[:,names.index(s['ASD_column'])]
                val,status,num,den,cov=convolve(wl,y,cv['curve'])
                old=prior.get((s['station_id'],b,role))
                if old is not None: assert val is not None and abs(val-float(old['convolved_reflectance']))<1e-14
                refs.append(dict(station_id=s['station_id'],class_literal=s['class_literal'],population=s['role'],band_id=b,SRF_role=role,ASD_reflectance=val,unit='1',reference_status=status,response_fraction_inside_ASD=cov,response_weighted_numerator=num,response_denominator=den,ASD_source=rel(asd),ASD_sha256=sha(asd),ASD_column=s['ASD_column'],ASD_field_date=s['field_date'],SRF_file=rel(path),SRF_sha256=sha(path),sheet='Spectral Responses (S2B)',wavelength_column='A',response_column=cv['column'],response_label=cv['label'],matches_prior_threeband_value=old is not None,validation_eligible=False))
            coverage.append(dict(band_id=b,SRF_role=role,SRF_file=rel(path),SRF_sha256=sha(path),positive_response_min_nm=float(xx[pos].min()),positive_response_max_nm=float(xx[pos].max()),ASD_min_nm=float(wl.min()),ASD_max_nm=float(wl.max()),ASD_spacing_nm=1,response_fraction_inside_ASD=cov,coverage_threshold=.999,coverage_fraction_pass=cov>=.999,positive_response_outside_ASD=bool(((xx[pos]<wl.min())|(xx[pos]>wl.max())).any()),reference_status=status,no_extrapolation=True))
    # Surface-class QA is evidence, not independent habitat truth. Keep stored values
    # visible but attach operational cloud/shadow labels; do not silently filter rows.
    prior_holds={r['station_id']:r['all_reasons'] for r in rows(P/'tables/ctr34_target_decisions.csv')}
    qmap={(r['station_id'],r['band_id'],r['correction']):r for r in qa if r['kind']=='SCL'}
    for r in sat:
        q=qmap[(r['station_id'],r['band_id'],r['correction'])]
        codes=json.loads(q['cell_counts_json']); bad=sorted(set(codes)&{'0','1','2','3','8','9','10','11'},key=int)
        r['SCL_over_stored_footprint_counts_json']=q['cell_counts_json']
        r['SCL_labels']=';'.join(scl_labels[k] for k in sorted(codes,key=int))
        r['SCL_cloud_shadow_or_invalid_flag']=bool(bad)
        r['quality_disposition']='operational_SCL_cloud_shadow_or_invalid_flag;stored_value_retained_for_context' if bad else 'no_SCL_cloud_shadow_invalid_code_over_stored_footprint;full_effective_support_unverified'
        r['prior_physical_hold_reason']=prior_holds.get(r['station_id'],'supplementary_support_requires_separate_design')
        if bad: r['hold_reason']+=';operational_SCL_flag:'+','.join(scl_labels[k] for k in bad)
    sharing=[]
    for source,col,row in sorted({(r['source_path'],r['col_0based'],r['row_0based']) for r in sat}):
        group=[r for r in sat if (r['source_path'],r['col_0based'],r['row_0based'])==(source,col,row)]
        sharing.append(dict(source_path=source,band_id=group[0]['band_id'],correction=group[0]['correction'],col_0based=col,row_0based=row,n_stations=len(group),station_ids=';'.join(r['station_id'] for r in group),independence='shared stored cell is not an independent satellite sample; distinct cells also do not establish ecological independence'))
    table('ctr42_cell_sharing.csv',sharing)
    ledger=[]
    for s in stations:
        for b in BANDS:
            sr=[r for r in sat if r['station_id']==s['station_id'] and r['band_id']==b]
            rr=[r for r in refs if r['station_id']==s['station_id'] and r['band_id']==b]
            ledger.append(dict(station_id=s['station_id'],band_id=b,population=s['role'],Sen2Cor_status=sr[0]['availability_reason'],ACOLITE_status=sr[1]['availability_reason'],Sen2Cor_SCL_labels=sr[0]['SCL_labels'],ACOLITE_SCL_labels=sr[1]['SCL_labels'],Sen2Cor_SCL_flag=sr[0]['SCL_cloud_shadow_or_invalid_flag'],ACOLITE_SCL_flag=sr[1]['SCL_cloud_shadow_or_invalid_flag'],ASD_v4_status=rr[0]['reference_status'],ASD_v5_status=rr[1]['reference_status'],common_finite_triple_v4=all(v is not None and math.isfinite(v) for v in [sr[0]['reflectance'],sr[1]['reflectance'],rr[0]['ASD_reflectance']]),common_finite_triple_v5=all(v is not None and math.isfinite(v) for v in [sr[0]['reflectance'],sr[1]['reflectance'],rr[1]['ASD_reflectance']]),validation_eligible=False,hold_reason=sr[0]['hold_reason'],required_to_resolve='March7 coincident field/overpass evidence and effective footprint/registration/patch support; B08 needs measured wider ASD coverage, not extrapolation' if b=='B08' else 'coincident field/overpass evidence and effective footprint/registration/patch support'))
    # Retain full contextual ASD curve from existing validated export, not as a March7 observation.
    context=P/'tables/ctr34_current_spectra.csv'; track(context,'existing contextual March27 full ASD curve; do not relabel')
    for n,rs in [('ctr42_stations.csv',stations),('ctr42_exclusions.csv',exclusions),('ctr42_band_contract.csv',contracts),('ctr42_satellite.csv',sat),('ctr42_qa.csv',qa),('ctr42_references.csv',refs),('ctr42_srf_coverage.csv',coverage),('ctr42_availability.csv',ledger),('ctr42_windows.csv',windows)]: table(n,rs)
    dump('provenance/ctr42_scene_pair.json',scene); dump('outputs/ctr42_raster_headers.json',headers)
    for n,r in sources.items():
        p=ROOT/n; assert [p.stat().st_size,p.stat().st_mtime_ns]==[r['bytes'],r['mtime_ns']], n
    table('ctr42_sources.csv',list(sources.values()))
    summary=dict(started_utc=started,completed_utc=D.datetime.now(D.timezone.utc).isoformat(),station_count=len(stations),excluded_stations=EXCLUDED,band_count=9,satellite_rows=len(sat),satellite_finite=sum(r['reflectance'] is not None for r in sat),reference_rows=len(refs),reference_finite=sum(r['ASD_reflectance'] is not None for r in refs),common_triples_v4=sum(r['common_finite_triple_v4'] for r in ledger),common_triples_v5=sum(r['common_finite_triple_v5'] for r in ledger),eligible_validation_rows=0,raw_QA_rows=len(qa),operational_SCL_flagged_satellite_rows=sum(r['SCL_cloud_shadow_or_invalid_flag'] for r in sat),distinct_stored_cells=len(sharing),shared_stored_cell_groups=sum(r['n_stations']>1 for r in sharing),window_count=len(windows),max_window_cells=max(r['cols']*r['rows'] for r in windows),raw_sources_stat_unchanged=True,software=dict(python=sys.version,numpy=np.__version__,GDAL=run(['gdalinfo','--version']).strip(),host=platform.node()),source_hash_scope='streamed full-file SHA256; raster processing only bounded windows; no full-scene arrays',convolution='exact saved CTR34 union-knot trapezoid; threshold .999 plus no positive-response extrapolation; gaps in positive response prohibited',environment_changed=False,script_sha256=sha(Path(__file__)),existing_report_edited=False,scientific_approval='none; author QA only; Thomas numerical check then presentation and independent review required')
    dump('provenance/ctr42_extraction.json',summary)
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
