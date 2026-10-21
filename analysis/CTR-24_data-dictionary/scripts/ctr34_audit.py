#!/usr/bin/env python3
"""CTR-28 read-only feasibility audit; no full-scene processing or comparison metrics.
Run from repository root with .venv/bin/python. Uses locked numpy, stdlib and installed GDAL CLI/C API.
PI-confirmed EPSG:4326 supports location diagnostics, not footprint/accuracy validation.
"""
import csv, ctypes as C, ctypes.util, datetime as D, hashlib, json, math, os, platform, subprocess, sys, urllib.request, zipfile
from pathlib import Path
import xml.etree.ElementTree as E
import numpy as np
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parents[1]; RAW=ROOT/'data/raw'
ENV=dict(os.environ,GDAL_PAM_ENABLED='NO',PROJ_NETWORK='OFF',CPL_TMPDIR='/tmp')
os.environ.update(GDAL_PAM_ENABLED='NO',PROJ_NETWORK='OFF')
for name in ['tables','outputs','provenance','figures']: (OUT/name).mkdir(exist_ok=True)
commands=[]; used={}
def rel(p):return str(Path(p).relative_to(ROOT))
def track(p,hashed=True):
 p=Path(p);s=p.stat();key=rel(p)
 if key not in used:used[key]={'path':key,'bytes':s.st_size,'mtime_ns':s.st_mtime_ns,'sha256':hashlib.sha256(p.read_bytes()).hexdigest() if hashed else None,'hash_scope':'whole_file' if hashed else 'header + diagnostic windows only; no full raster hash'}
 return p
def dump(name,obj):
 (OUT/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def writecsv(name,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with (OUT/name).open('w',newline='') as f:
  w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rows)
def run(args,inp=None):
 commands.append([str(x) for x in args]);return subprocess.check_output([str(x) for x in args],env=ENV,input=inp,text=True,timeout=60)
def snapshot():
 return {str(p.relative_to(RAW)):[p.stat().st_size,p.stat().st_mtime_ns] for p in RAW.rglob('*') if p.is_file()}
def workbook(p):
 ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
 with zipfile.ZipFile(track(p)) as z:
  strings=[''.join(x.itertext()) for x in E.fromstring(z.read('xl/sharedStrings.xml'))] if 'xl/sharedStrings.xml' in z.namelist() else []
  wb=E.fromstring(z.read('xl/workbook.xml'));links={r.get('Id'):r.get('Target') for r in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))};sheets={}
  for sh in wb.find('m:sheets',ns):
   t=links[sh.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')];t=t.lstrip('/') if t.startswith('/') else 'xl/'+t
   rows=[]
   for row in E.fromstring(z.read(t)).findall('.//m:sheetData/m:row',ns):
    cells={}
    for c in row:
     v=c.find('m:v',ns);v=v.text if v is not None else ''.join(c.itertext())
     if c.get('t')=='s' and v:v=strings[int(v)]
     if v:cells[''.join(filter(str.isalpha,c.get('r')))]=v
    if cells:rows.append({'row':int(row.get('r')),'cells':cells})
   sheets[sh.get('name')]=rows
  return sheets

def info(p):
 track(p,False);h=json.loads(run(['gdalinfo','-json','-noct','-nogcp',p]));h.pop('stac',None);return h

def features(p):
 for ext in ['.shp','.shx','.dbf','.prj','.cpg']:
  q=p.with_suffix(ext)
  if q.exists():track(q)
 return json.loads(run(['ogr2ogr','-f','GeoJSON','/vsistdout/',p]))

def xmlrows(p):
 root=E.parse(track(p)).getroot();out=[]
 def walk(e,path):
  tag=e.tag.split('}')[-1];path=path+'/'+tag
  if len(e)==0 and e.text and e.text.strip():out.append({'path':path,'value':e.text.strip(),'attributes':dict(e.attrib)})
  for c in e:walk(c,path)
 walk(root,'');return out

# Explicit, reviewed-by-author proposal; never generate a join by case/underscore stripping.
CROSSWALK={**{f'AC_{i:02}':f'AC{i:02}' for i in range(1,9)},**{f'D06_{c}':f'D06_{c}' for c in 'ABCDEFG'}}
def main():
 before=snapshot();start=D.datetime.now(D.timezone.utc).isoformat()
 log=track(RAW/'ASD/202603_Measurement_log.txt').read_text();cover=list(csv.DictReader(track(RAW/'ASD/202603_Seagrass_cover.txt').open(),delimiter='\t'))
 gpspath=next((RAW/'GPS').glob('*.xlsx'));gps=workbook(gpspath)['Sheet1'];header=gps[0]['cells'];gpsrows=[dict(row=x['row'],**{header[k]:v for k,v in x['cells'].items() if k in header}) for x in gps[1:]]
 asdp=track(RAW/'ASD/202603_Reflectance_avg.txt');names=asdp.open().readline().split();arr=np.loadtxt(asdp,skiprows=1);wl=arr[:,0];idx={s:i for i,s in enumerate(names)}
 assert len(set(names))==len(names) and np.all(np.diff(wl)>0)
 stations=[]
 for asd,station in CROSSWALK.items():
  cc=[r for r in cover if r['station']==station];gg=[r for r in gpsrows if r.get('station')==station]
  assert len(cc)==len(gg)==1,(station,len(cc),len(gg))
  c,g=cc[0],gg[0];date=(D.datetime(1899,12,30)+D.timedelta(days=float(g['date']))).date().isoformat();assert date=='2026-03-27'
  vals=arr[:,idx[asd]];finite=np.isfinite(vals)
  stations.append(dict(station_id=station,asd_column_raw=asd,cover_station_raw=c['station'],gps_station_raw=g['station'],gps_sheet='Sheet1',gps_row=g['row'],gps_date_serial=g['date'],field_date=date,field_time_utc=None,field_timezone=None,date_evidence='log day06 20260327 + workbook date serial (1900 system)',target_class_raw=c['comment'],gps_target_class_raw=g['comment'],target_class_proposed=c['comment'],class_status='literal label only; mbp_mud unresolved spelling; zn not expanded',cover_raw=c['cover'],waypoint_cover_raw=c['gps'],waypoint_gps_raw=g.get('waypoint'),gps_operator_raw=g.get('gps'),picture_raw=c['picture'],poskey_raw=g.get('poskey'),lat_raw=g.get('lat'),lon_raw=g.get('lon'),location_raw=g.get('location'),zone_raw=g.get('Zone'),field_crs='EPSG:4326',coordinate_status='PI-confirmed WGS84; accuracy/footprint unresolved; AC01/02 location discrepancy retained',field_geometry='nadir; qualitative consistent sun-relative orientation; numerical geometry unknown',exposure_state='intertidal exposed during field measurement; overpass state unknown',independent_unit_proposed=station,independence_status='candidate station cluster; spatial/pixel overlap must be checked',role='primary_candidate' if station.startswith('AC') else 'supplementary_candidate',footprint_evidence='log: 5 x 20 spectra in area size of S2 pixel; actual boundary/resolution absent' if station.startswith('AC') else 'seagrass-cover/core campaign; satellite-sized footprint not documented',asd_path=rel(asdp),gps_path=rel(gpspath),cover_path=rel(RAW/'ASD/202603_Seagrass_cover.txt'),asd_units='dimensionless 0-1',wavelength_units='nm',asd_mean_algorithm='PI-confirmed station average; membership/weights/variance unknown',field_evidence='PI interaction 4765af59-1308-4dfe-8c85-19b3f5190b1f answered 2026-10-20T06:05:15.036Z',instrument='ASD Handheld FieldSpec2',reference_panel='99% Spectralon',spectral_rows=len(wl),finite_values=int(finite.sum()),minimum_raw=float(np.min(vals[finite])),maximum_raw=float(np.max(vals[finite])),date_eligible=True,include_primary=False,hold_reasons='field footprint/position accuracy/registration and overpass comparability unresolved'+(' ; supplementary support requires separate design' if station.startswith('D06') else '')))
 writecsv('tables/station_crosswalk.csv',stations)
 # Every other spectral column is accounted for without assigning unverified coordinates.
 writecsv('tables/spectrum_disposition.csv',[{'asd_column_raw':s,'march27_candidate':s in CROSSWALK,'reason':'explicit crosswalk + log + dated workbook' if s in CROSSWALK else 'not March27 day06/AC; no substitution from other dates'} for s in names[1:]])
 # Capture relevant supplied vectors without creating aliases to station IDs.
 vectors={n:features(RAW/'SHP'/n) for n in ['POI_S2C_ACOLITE_targets.shp','TimeSeries_Polygons_Matchup.shp','extent.shp','mask/square_mask.shp']}
 dump('outputs/vector_records.json',vectors)
 s=next((RAW/'S2').glob('*20260327*.SAFE'));xml={rel(p):xmlrows(p) for p in [s/'MTD_MSIL2A.xml',next(s.glob('GRANULE/*/MTD_TL.xml')),next(s.glob('DATASTRIP/*/MTD_DS.xml')),s/'manifest.safe']}
 # Datastrip XML includes lengthy orbital/GPS sequences; retain scientific product/GIPP metadata, not all telemetry.
 xml={k:[r for r in v if not any(t in r['path'] for t in ['/GPS_Point','/Attitude','/Ephemeris','/Solar_Irradiance_List','/Satellite_Ancillary_Data_Info/','/Sensor_Configuration/','/Sun_Angles_Grid/','/Viewing_Incidence_Angles_Grids/'])] for k,v in xml.items()}
 dump('outputs/safe_metadata.json',xml)
 prod=xml[rel(s/'MTD_MSIL2A.xml')]; offsets=[r for r in prod if r['path'].endswith('/BOA_ADD_OFFSET')];q=[r['value'] for r in prod if r['path'].endswith('/BOA_QUANTIFICATION_VALUE')]
 assert len(offsets)==13 and all(r['value']=='-1000' for r in offsets) and q==['10000']
 tiffs=sorted((RAW/'S2/ACOLITE/20260327').glob('*.tif'));assert len(tiffs)==11
 headers={rel(p):info(p) for p in tiffs}
 # Select native sensor support grid per band; B01 additionally available at 20 m but native support is 60 m.
 amap=dict(zip(['442','492','559','665','704','739','780','833','864','1610','2186'],['B01','B02','B03','B04','B05','B06','B07','B08','B8A','B11','B12']))
 bands=[]
 for p in tiffs:
  h=headers[rel(p)];b=h['bands'][0];m=h['metadata'][''];bm=b.get('metadata',{}).get('',{});label=p.stem.rsplit('_',1)[1];band=amap[label];res=10 if band in ['B02','B03','B04','B08'] else (60 if band=='B01' else 20)
  sp=next(s.glob(f'GRANULE/*/IMG_DATA/R{res}m/*_{band}_{res}m.jp2'));sh=info(sp);headers[rel(sp)]=sh
  bands.append(dict(band=band,platform='S2B',acolite_path=rel(p),acolite_variable=bm.get('NETCDF_VARNAME'),acolite_wave_nm=bm.get('wave_nm'),acolite_units=b.get('unit'),acolite_type=b['type'],acolite_scale_declared=b.get('scale'),acolite_offset_declared=b.get('offset'),acolite_decode='Float32 direct unit 1; no extra scale/offset declared',acolite_nodata=str(b.get('noDataValue')),acolite_grid_m=10,acolite_sensing_time=m.get('NC_GLOBAL#isodate'),acolite_version=m.get('NC_GLOBAL#acolite_version'),acolite_inputfile=m.get('NC_GLOBAL#inputfile'),acolite_granule=m.get('NC_GLOBAL#granule'),acolite_mask=m.get('NC_GLOBAL#l2w_mask'),acolite_srf_version=m.get('NC_GLOBAL#rsr_version'),sen2cor_path=rel(sp),sen2cor_native_support_m=res,sen2cor_stored_grid_m=res,sen2cor_type=sh['bands'][0]['type'],sen2cor_decode='(DN - 1000) / 10000 after masking DN 0 and 65535',sen2cor_scale=0.0001,sen2cor_offset=-0.1,sen2cor_nodata=0,sen2cor_saturated=65535,reflectance_definition='dimensionless surface bidirectional reflectance; geometry/comparability still held',product_status='operational L2A PB05.12 versus supplied ACOLITE DSF; no independent Sen2Cor rerun'))
 scl=next(s.glob('GRANULE/*/IMG_DATA/R20m/*_SCL_20m.jp2'));headers[rel(scl)]=info(scl)
 dump('outputs/raster_headers.json',headers);writecsv('tables/band_contract.csv',bands)
 # Platform SRF numeric coverage diagnostics, retaining supplied v4 as primary reference.
 srfpath=next(RAW.glob('*.xlsx'));book=workbook(srfpath);srfrows=book['Spectral Responses (S2B)'];dump('outputs/srf_overview.json',{k:v for k,v in book.items() if k in ['Overview','Equivalent Wavelengths','Bandwidth and mid-wavelength']})
 def curves(rows):
  head=rows[0]['cells'];cs={}
  for col,label in head.items():
   if col=='A' or 'SR_AV_B' not in label:continue
   pair=[]
   for r in rows[1:]:
    try:pair.append((float(r['cells']['A']),float(r['cells'][col])))
    except (KeyError,ValueError):pass
   if pair:rawband=label.split('SR_AV_')[-1]; band='B'+rawband[1:].zfill(2) if rawband[1:].isdigit() else rawband.upper(); cs[band]=np.asarray(pair)
  return cs
 c4=curves(srfrows);sr=[]
 for band,c in c4.items():
  x,y=c.T;assert np.all(np.diff(x)>0);pos=y>0;total=float(np.trapezoid(y,x));inside=(x>=wl[0])&(x<=wl[-1]);negative=int((y<0).sum());support=x[pos]
  coverage=float(np.trapezoid(y[inside],x[inside])/total) if inside.any() else 0
  sr.append(dict(band=band,srf_version='supplied_v4.0',platform='S2B',path=rel(srfpath),sheet='Spectral Responses (S2B)',wavelength_units_reference='nm (workbook and authenticated PI field answer)',positive_support_min=float(support.min()),positive_support_max=float(support.max()),integral_response=total,negative_response_values=negative,asd_wl_min_raw=float(wl.min()),asd_wl_max_raw=float(wl.max()),response_fraction_in_ASD_range_if_nm=coverage,coverage_pass_if_nm=coverage>=0.999,satellite_pair_available=band in {b['band'] for b in bands}))
 writecsv('tables/srf_coverage.csv',sr)
 # Download only the separately named official reference, retaining supplied v4 unchanged.
 url='https://sentiwiki.copernicus.eu/__attachments/a_ad595cc9fa0018a4e9eb28e1e234124a751149b5933b0b8b1f6b80612eaab586/sentinel-2-spectral-response-functions-v5.xlsx?cb=0735bcc384fde7424ba8d58a19c4a9dd'
 v5=OUT/'outputs/official-srf-v5.xlsx'
 if not v5.exists():
  with urllib.request.urlopen(url,timeout=45) as response: data=response.read(5*1024*1024+1)
  assert len(data)<5*1024*1024;v5.write_bytes(data)
 assert hashlib.sha256(v5.read_bytes()).hexdigest()=='42be3ebd8bfcbde11c37caeb2e2fdda65fefa8d2b6f8329559b7806d02cdc9e2','official reference changed; inspect before proceeding'
 c5=curves(workbook(v5)['Spectral Responses (S2B)']);sens=[]
 for band,c in c4.items():
  x=np.union1d(c[:,0],c5[band][:,0]);a=np.interp(x,*c.T,left=0,right=0);b=np.interp(x,*c5[band].T,left=0,right=0)
  a=a/np.trapezoid(a,x);b=b/np.trapezoid(b,x);inside=(x>=wl.min())&(x<=wl.max())
  sens.append(dict(band=band,normalized_srf_L1_distance=float(np.trapezoid(np.abs(b-a),x)),v4_equivalent_nm=float(np.trapezoid(x*a,x)),v5_equivalent_nm=float(np.trapezoid(x*b,x)),v4_fraction_400_900=float(np.trapezoid(a[inside],x[inside])),v5_fraction_400_900=float(np.trapezoid(b[inside],x[inside]))))
 writecsv('tables/srf_v5_sensitivity.csv',sens)
 dump('provenance/official_sources.json',{'accessed_utc':D.datetime.now(D.timezone.utc).isoformat(),'v5_url':url,'v5_sha256':hashlib.sha256(v5.read_bytes()).hexdigest(),'primary_reference':'supplied v4; v5 diagnostic comparison only','sources':['https://sentiwiki.copernicus.eu/web/s2-products','https://sentiwiki.copernicus.eu/web/s2-processing','https://sentiwiki.copernicus.eu/web/s2-documents','https://sentinels.copernicus.eu/-/sentinel-2-spectral-response-functions-update','https://github.com/acolite/acolite','https://raw.githubusercontent.com/acolite/acolite/main/acolite/output/nc_to_geotiff.py'],'source_limit':'current documentation contextualizes supplied headers; it does not establish exact April2026 source commit'})
 coverage={r['band']:r for r in sr}
 for b in bands:
  b.update(srf_coverage_fraction_if_nm=coverage[b['band']]['response_fraction_in_ASD_range_if_nm'],spectral_coverage_pass_if_nm=coverage[b['band']]['coverage_pass_if_nm'],spatial_role='primary_candidate_10m' if b['band'] in ['B02','B03','B04'] else ('held: no ASD spectral coverage' if not coverage[b['band']]['coverage_pass_if_nm'] and b['band']!='B08' else ('held: incomplete B08 spectral coverage' if b['band']=='B08' else 'held: coarser native field support unestablished')))
 writecsv('tables/band_contract.csv',bands)
 # PI-confirmed coordinate diagnostic: pass lon,lat to gdaltransform in traditional GIS order.
 inp=''.join(f"{r['lon_raw']} {r['lat_raw']}\n" for r in stations)
 xy=[list(map(float,l.split()[:2])) for l in run(['gdaltransform','-s_srs','EPSG:4326','-t_srs','EPSG:32628'],inp).splitlines()]
 # GDAL C API strictly readonly, 3x3 only; shared native 10m B04 grid + SCL. No resampling.
 lib=C.CDLL(ctypes.util.find_library('gdal'));lib.GDALAllRegister();lib.GDALOpen.argtypes=[C.c_char_p,C.c_int];lib.GDALOpen.restype=C.c_void_p
 lib.GDALGetRasterBand.argtypes=[C.c_void_p,C.c_int];lib.GDALGetRasterBand.restype=C.c_void_p
 lib.GDALRasterIO.argtypes=[C.c_void_p,C.c_int,C.c_int,C.c_int,C.c_int,C.c_int,C.c_void_p,C.c_int,C.c_int,C.c_int,C.c_int,C.c_int];lib.GDALClose.argtypes=[C.c_void_p]
 def window(p,c,r):
  ds=lib.GDALOpen(str(ROOT/p).encode(),0);assert ds
  try:
   ba=lib.GDALGetRasterBand(ds,1);a=np.empty((3,3),dtype='float64');err=lib.GDALRasterIO(ba,0,c-1,r-1,3,3,a.ctypes.data_as(C.c_void_p),3,3,7,0,0);assert err==0
   return a
  finally:lib.GDALClose(ds)
 b4=next(b for b in bands if b['band']=='B04');diagnostics=[]
 for i,(r,(x,y)) in enumerate(zip(stations,xy)):
  poi=vectors['POI_S2C_ACOLITE_targets.shp']['features'];nearest=min(poi,key=lambda f:math.dist(f['geometry']['coordinates'],[x,y]))
  others=[(math.dist([x,y],p),stations[j]['station_id']) for j,p in enumerate(xy) if j!=i];distance,neighbor=min(others)
  rec=dict(station_id=r['station_id'],diagnostic_only=True,coordinate_assumption='PI-confirmed EPSG:4326 field lon/lat -> EPSG:32628; footprint and positional accuracy unvalidated',x_if_wgs84=x,y_if_wgs84=y,nearest_other_station=neighbor,nearest_other_station_m_if_wgs84=distance,nearest_supplied_target=nearest['properties']['Name'],nearest_supplied_target_distance_m_if_wgs84=math.dist(nearest['geometry']['coordinates'],[x,y]),supplied_target_join='UNMATCHED: no shared IDs; nearest point is diagnostic only')
  for key,p in [('acolite',b4['acolite_path']),('sen2cor',b4['sen2cor_path']),('scl',rel(scl))]:
   h=headers[p];gt=h['geoTransform'];col=math.floor((x-gt[0])/gt[1]);row=math.floor((y-gt[3])/gt[5]);inside=0<=col<h['size'][0] and 0<=row<h['size'][1];rec.update({key+'_inside':inside,key+'_col':col,key+'_row':row})
   if inside and 1<=col<h['size'][0]-1 and 1<=row<h['size'][1]-1:
    a=window(p,col,row);valid=np.isfinite(a)
    if key=='sen2cor':valid&=(a!=0)&(a!=65535)
    rec.update({key+'_valid_of_9':int(valid.sum()),key+'_window_sha256':hashlib.sha256(a.tobytes()).hexdigest()})
    if key=='scl':rec['scl_values']=','.join(map(str,sorted(set(a.ravel().astype(int)))));rec['scl_center']=int(a[1,1])
   if key=='sen2cor':rec['hypothetical_10m_pixel_cluster']=f'{col}:{row}'
  diagnostics.append(rec)
 writecsv('tables/conditional_spatial_diagnostics.csv',diagnostics)
 # Proposed long-form data contract: explicitly unextracted values, all inclusion flags false.
 manifest=[]
 for st in stations:
  for b in bands:
   manifest.append({**st,**b,'asd_band_reflectance':None,'satellite_acolite_reflectance':None,'satellite_sen2cor_reflectance':None,'paired_valid':False,'extraction_status':'not_extracted; pending contract and metadata resolution','srf_primary':'supplied v4 S2B; v5 sensitivity separate','common_support':'10m B02/B03/B04 candidate primary; B08 incomplete spectrum; coarser bands held pending footprint','mask_proposal':'common SCL; exclude 0,1,2,3,7,8,9,10,11; retain 4/5/6 only with field exposure evidence; native defect masks required'})
 writecsv('tables/proposed_matchups.csv',manifest)
 dump('outputs/data_contract.json',{
  'schema':'ctrlsea.matchup-feasibility.v1','task':'CTR-28','parent':'CTR-27','readiness':'blocked_for_scientific_extraction','manifest':'tables/proposed_matchups.csv','csv_null':'empty field; never zero','csv_boolean':'True or False; parse explicitly','primary_key':['station_id','band'],'candidate_counts':{'date_eligible':15,'primary_station_candidates':8,'supplementary_station_candidates':7,'potential_primary_band_pairs_before_holds':24,'included_pairs':0},
  'raw_identifier_crosswalk':CROSSWALK,'independent_unit':'candidate station; bands/acquisitions/5x20 readings are not independent replicates; review spatial overlap before inference',
  'convolution':{'platform':'S2B','primary_reference':rel(srfpath),'sheet':'Spectral Responses (S2B)','formula':'integral(R_field(lambda) * SRF_band(lambda), d_lambda) / integral(SRF_band(lambda), d_lambda)','integration':'trapezoidal on union of ASD and SRF knots; linear interpolate only between finite adjacent ASD samples spaced <=1 nm','minimum_response_coverage':0.999,'invalid_policy':'reject if nonfinite or missing/noisy interval intersects positive SRF; do not bridge, extrapolate, replace with zero, or silently renormalize truncated bands','ASD_units':'PI-confirmed dimensionless 0-1; no conversion','ASD_wavelength_unit':'PI-confirmed nm','version_sensitivity':'v5 separately hashed, normalized SRF diagnostics only; no silent substitution'},
  'spatial':{'primary_bands':['B02','B03','B04'],'primary_stations':['AC%02d'%i for i in range(1,9)],'CRS':'raster EPSG:32628; PI-confirmed field EPSG:4326','support':'confirmed field area first; primary containing 10m pixel only when same sampled footprint supported; fixed 3x3 neighborhood sensitivity, never post hoc value optimization','coarse_bands':'B01 native60m, B05/B06/B07/B8A native20m require documented homogeneous footprint of same support; 10m ACOLITE resampling does not create resolution','registration':'grid-aligned B02/B03/B04 with integer crop offset; image-to-ground registration unmeasured; no shifts fitted to ASD reflectance','resampling':'none for primary; area-weighted same-boundary aggregation only under agreed coarse-support contract; nearest neighbor for categorical masks','time':'same day insufficient; record UTC interval and tide/exposure at acquisition and field survey before enabling'},
  'masks':{'predeclared_common_scl_exclude':[0,1,2,3,7,8,9,10,11],'allowed_scl_subject_to_field_evidence':[4,5,6],'support_rule':'all primary support pixels must pass common masks; no partial-footprint averaging','sen2cor_invalid_dn':[0,65535],'acolite_invalid':'NaN/nonfinite; no provided l2_flags on March27; l2w_mask=False','defect_masks':'native MSK_QUALIT/MSK_DETFOO still require decoding and extraction-stage verification','water':'SCL6 not automatically discarded; exposure/optical quantity must be established independently','negative_reflectance':'retain finite values after quality masks; flag, do not clip to improve fit'},
  'statistics_handoff':{'status':'Thomas concurrence 1f9de7bb-a5fb-4c73-ad90-7444529f2189; normalized amendment required before extraction','common_pairs':'identical valid station-band pairs for both methods','cluster':'station and shared support; retain pixel cluster fields and all exclusion reasons','uncertainty':'field replicate uncertainty unavailable from mean export; within-target band dependence; few stations; spatial autocorrelation','no_results':['no bias','no RMSE','no rankings','no final scatterplot']},
  'review':{'internal':'pending independent reviewer','PI_scientific_approval':'pending','manuscript_integration':'not_authorized'}})
 # Source headers must agree on identity, units, grid, and decoding before delivery.
 ac=[v for k,v in headers.items() if '/ACOLITE/' in k]
 assert all(h['size']==ac[0]['size'] and h['geoTransform']==ac[0]['geoTransform'] for h in ac)
 assert all(h['bands'][0].get('unit')=='1' and h['bands'][0]['type']=='Float32' and h['bands'][0].get('noDataValue')=='NaN' for h in ac)
 assert all(h['bands'][0].get('scale',1)==1 and h['bands'][0].get('offset',0)==0 for h in ac)
 assert all(h['metadata'][''].get('NC_GLOBAL#sensor')=='S2B_MSI' and h['metadata'][''].get('NC_GLOBAL#isodate')=='2026-03-27T11:45:53.975343+00:00' for h in ac)
 # Diagnostics contain no reflectance pair; ensure no accidental eligibility promotion.
 assert len(stations)==15 and len(manifest)==165 and not any(x['include_primary'] or x['paired_valid'] for x in manifest)
 after=snapshot();assert before==after,'raw stat snapshot changed'
 dump('provenance/run.json',dict(started_utc=start,ended_utc=D.datetime.now(D.timezone.utc).isoformat(),raw_stat_unchanged=True,raw_file_count=len(before),raw_stat_snapshot_sha256=hashlib.sha256(json.dumps(before,sort_keys=True).encode()).hexdigest(),inputs=list(used.values()),commands=commands,python=sys.version,numpy=np.__version__,gdal=run(['gdalinfo','--version']).strip(),platform=platform.platform(),host=platform.node(),base_commit=run(['git','rev-parse','HEAD']).strip(),branch=run(['git','branch','--show-current']).strip(),dependency_changes='none',locks={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['uv.lock','renv.lock']},source_dictionary_commit='8d885c1c9ea1b10751dea939c2d1aee1432307bd',read_limits='small tables/reference worksheets; all March27 TIFF headers; selected SAFE headers; 3x3 B04 and SCL windows at 15 confirmed-CRS candidate locations only',validation='assertions passed; scientific approval pending'))
 print(json.dumps({'stations':len(stations),'manifest_rows':len(manifest),'wavelength_min_raw':float(wl.min()),'wavelength_max_raw':float(wl.max()),'raw_unchanged':before==after,'srf_bands':len(sr)}))
if __name__=='__main__':main()
