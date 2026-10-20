#!/usr/bin/env python3
"""Bounded CTR-28 amendment: PI evidence, AOI intake and normalized held design.
Run audit.py first. No ASD convolution, paired errors or full-scene processing.
"""
import csv,ctypes as C,ctypes.util,datetime as D,hashlib,json,math
from collections import Counter
from pathlib import Path
import numpy as np
import audit as a
P=a.OUT; ROOT=a.ROOT; BANDS=['B02','B03','B04']; VERSION='ctr28-amendment-v2'
def rows(n):return list(csv.DictReader((P/'tables'/n).open()))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def uid(kind,*parts):return kind+':'+hashlib.sha256(json.dumps(parts,separators=(',',':')).encode()).hexdigest()[:24]
def inside(x,y,ring):
 hit=False
 for (x1,y1),(x2,y2) in zip(ring,ring[1:]):
  if (y1>y)!=(y2>y) and x < (x2-x1)*(y-y1)/(y2-y1)+x1:hit=not hit
 return hit

def main():
 start=D.datetime.now(D.timezone.utc).isoformat();before=a.snapshot()
 st=rows('station_crosswalk.csv');di=rows('conditional_spatial_diagnostics.csv');bands=rows('band_contract.csv');byband={b['band']:b for b in bands}
 headers=json.loads((P/'outputs/raster_headers.json').read_text());vectors=json.loads((P/'outputs/vector_records.json').read_text())
 field={'source_kind':'authenticated_PI_field_testimony','interaction_id':'4765af59-1308-4dfe-8c85-19b3f5190b1f','answered_utc':'2026-10-20T06:05:15.036Z','reconciliation_revision':'f820bfe7-8b71-4344-8b19-15fca9a25164','independent_review_revision':'71ca4c89-4664-4868-9eb2-07b4b9c9cd05','concurrence_revision':'1f9de7bb-a5fb-4c73-ad90-7444529f2189','supersedes_audit_revision':'6fec859e-0973-430f-9486-f618deb59b6b','supersedes_commit':'1cd34b042eca41f26da81e41fb838b7344357dca','confirmed':{'wavelength_unit':'nm','reflectance_unit':'dimensionless 0-1','export_aggregation':'station average','instrument':'ASD Handheld FieldSpec2','panel':'99% Spectralon','view':'nadir; qualitatively consistent stated sun-relative orientation','field_state':'all targets intertidal and exposed during field measurement','gps_crs':'EPSG:4326'},'not_established':['replicate membership/weights/variance','numerical geometry/height/FOV','GPS accuracy/field footprints','AC01/02 Iwik-versus-Arel location','field times/timezone','satellite-overpass exposure/wetness','AC03 mbp_mud spelling'],'scientific_approval':False}
 a.dump('provenance/field_evidence.json',field)
 # Inventory metadata for the entire new folder, hash/read ONLY two relevant dated inputs.
 folder=ROOT/'data/raw/Atm_Compare_AOI';assert folder.is_dir();inventory=[];data={};intake=[]
 for p in sorted(folder.rglob('*')):
  if not p.is_file():continue
  selected=p.name=='2026-03-27.csv';inventory.append({'path':a.rel(p),'bytes':p.stat().st_size,'mtime_ns':p.stat().st_mtime_ns,'used':selected,'sha256':sha(p) if selected else None,'scope':'whole-file SHA256 and table inspection' if selected else 'stat inventory only; other date excluded'})
  if selected:
   method=p.parent.name;r=list(csv.DictReader(p.open()));data[method]=r
   key=lambda x:(x['AOI'],x['pixel_id']);assert len({key(x) for x in r})==len(r)
   assert len({(x['x'],x['y']) for x in r})==len(r)
   assert all(x['date']=='2026-03-27' and x['atmospheric_correction']==method for x in r)
   for group in sorted({x['AOI'] for x in r}):
    s=[x for x in r if x['AOI']==group];bandnames=[k for k in r[0] if k.startswith('B')]
    intake.append({'correction':method,'AOI_raw':group,'rows':len(s),'scene_id_raw':s[0]['scene_id'],'source_address_raw':s[0]['source'],'unique_AOI_pixel_keys':len({key(x) for x in s}),'bands':bandnames,'station_identifier_field':None,'CRS_declared_in_CSV':None,'CRS_evidence':'all x,y/row,col exactly match EPSG:32628 source grid centres; CRS not declared in CSV','quantity_evidence':'native source headers + bounded value checks; CSV has no unit/scale/nodata metadata','scale_offset_export_metadata':None,'nodata_export_metadata':None,'QA_fields':[],'geometry_or_weight_fields':[],'band_nonfinite_counts':{b:sum(not math.isfinite(float(x[b])) for x in s) for b in bandnames},'pixel_id_scope':'restarts within AOI; never join on pixel_id alone','support_type':'10 m output grid cells in broad AOI; not station averages','min_x':min(float(x['x']) for x in s),'max_x':max(float(x['x']) for x in s),'min_y':min(float(x['y']) for x in s),'max_y':max(float(x['y']) for x in s)})
 assert set(data)=={'ACOLITE','Sen2Cor'}
 def key(x):return (x['AOI'],x['pixel_id'])
 paired={m:{key(r):r for r in rs} for m,rs in data.items()}
 assert paired['ACOLITE'].keys()==paired['Sen2Cor'].keys()
 for k,x in paired['Sen2Cor'].items():
  y=paired['ACOLITE'][k];assert x['x']==y['x'] and x['y']==y['y']
  assert int(x['row'])-int(y['row'])==9006 and int(x['col'])-int(y['col'])==3405
  for method,z in [('Sen2Cor',x),('ACOLITE',y)]:
   path=byband['B04']['sen2cor_path' if method=='Sen2Cor' else 'acolite_path'];gt=headers[path]['geoTransform']
   assert float(z['x'])==gt[0]+(int(z['col'])+.5)*gt[1] and float(z['y'])==gt[3]+(int(z['row'])+.5)*gt[5]
  assert x['scene_id']==Path(byband['B04']['sen2cor_path'].split('/GRANULE/')[0]).name
  assert y['scene_id']==Path(byband['B04']['acolite_path']).stem.rsplit('_rhos_',1)[0]
 # Reconstruct centre-in-polygon membership from the supplied SHP; do not assert producer's exact rasterization algorithm.
 polygon_checks=[]
 for f in vectors['TimeSeries_Polygons_Matchup.shp']['features']:
  ring=f['geometry']['coordinates'][0];name=f['properties']['AOI'];g=headers[byband['B04']['sen2cor_path']]['geoTransform'];xy=lambda col,row:(g[0]+(col+.5)*10,g[3]-(row+.5)*10)
  c0=math.floor((min(t[0] for t in ring)-g[0])/10);c1=math.floor((max(t[0] for t in ring)-g[0])/10)
  r0=math.floor((g[3]-max(t[1] for t in ring))/10);r1=math.floor((g[3]-min(t[1] for t in ring))/10)
  expected={xy(c,r) for c in range(c0,c1+1) for r in range(r0,r1+1) if inside(*xy(c,r),ring)}
  actual={(float(x['x']),float(x['y'])) for x in data['Sen2Cor'] if x['AOI']==name}
  polygon_checks.append({'AOI':name,'centre_in_polygon_cells':len(expected),'CSV_cells':len(actual),'missing_cells':len(expected-actual),'extra_cells':len(actual-expected),'exact_centre_set_match':expected==actual})
 # Station join is exact containing-cell membership; distances never supply a replacement alias.
 joins=[]
 for s,d in zip(st,di):
  x,y=float(d['x_if_wgs84']),float(d['y_if_wgs84']);matched=[r for r in data['Sen2Cor'] if (r['row'],r['col'])==(d['sen2cor_row'],d['sen2cor_col'])]
  near=min(data['Sen2Cor'],key=lambda r:math.hypot(float(r['x'])-x,float(r['y'])-y))
  joins.append({'station_id':s['station_id'],'station_crs':'EPSG:4326 (PI)','station_grid_crs':'EPSG:32628','station_x_m':x,'station_y_m':y,'containing_SAFE_row_0based':d['sen2cor_row'],'containing_SAFE_col_0based':d['sen2cor_col'],'exact_containing_cell_matches':len(matched),'join_status':'unmatched' if not matched else 'cell_match_only_not_field_support','nearest_AOI_raw':near['AOI'],'nearest_AOI_pixel_id':near['pixel_id'],'nearest_CSV_centre_distance_m':math.hypot(float(near['x'])-x,float(near['y'])-y),'nearest_is_alias':False,'field_footprint_status':'unknown'})
 a.writecsv('tables/aoi_station_join.csv',joins)
 # Six predetermined rows (first, midpoint, last per AOI), each available band, 1x1 reads.
 lib=C.CDLL(ctypes.util.find_library('gdal'));lib.GDALAllRegister();lib.GDALOpen.argtypes=[C.c_char_p,C.c_int];lib.GDALOpen.restype=C.c_void_p
 lib.GDALGetRasterBand.argtypes=[C.c_void_p,C.c_int];lib.GDALGetRasterBand.restype=C.c_void_p
 lib.GDALRasterIO.argtypes=[C.c_void_p,C.c_int,C.c_int,C.c_int,C.c_int,C.c_int,C.c_void_p,C.c_int,C.c_int,C.c_int,C.c_int,C.c_int];lib.GDALClose.argtypes=[C.c_void_p]
 checks=[];handles={}
 try:
  for group in ['Arel','Iwik']:
   rr=[r for r in data['Sen2Cor'] if r['AOI']==group]
   for index in [0,len(rr)//2,len(rr)-1]:
    k=key(rr[index])
    for method in ['Sen2Cor','ACOLITE']:
     r=paired[method][k]
     for band in [k for k in r if k.startswith('B')]:
      if band=='B09':
       safe=ROOT/byband['B04']['sen2cor_path'].split('/GRANULE/')[0];path=a.rel(next(safe.glob('GRANULE/*/IMG_DATA/R60m/*_B09_60m.jp2')))
       if path not in headers:headers[path]=a.info(ROOT/path)
      else:path=byband[band]['sen2cor_path' if method=='Sen2Cor' else 'acolite_path']
      h=headers[path];gt=h['geoTransform'];col=math.floor((float(r['x'])-gt[0])/gt[1]);row=math.floor((float(r['y'])-gt[3])/gt[5])
      if path not in handles:handles[path]=lib.GDALOpen(str(ROOT/path).encode(),0);assert handles[path]
      out=np.empty(1,dtype='float64');err=lib.GDALRasterIO(lib.GDALGetRasterBand(handles[path],1),0,col,row,1,1,out.ctypes.data_as(C.c_void_p),1,1,7,0,0);assert err==0
      raw=float(out[0]);value=(raw-1000)/10000 if method=='Sen2Cor' and raw not in [0,65535] else (raw if method=='ACOLITE' else None)
      csvvalue=float(r[band]);matches=value is not None and math.isclose(csvvalue,value,rel_tol=0,abs_tol=1e-7)
      checks.append({'method':method,'AOI':group,'CSV_data_index_within_AOI_0based':index,'pixel_id':r['pixel_id'],'band':band,'source_path':path,'source_row_0based':row,'source_col_0based':col,'stored_resolution_m':gt[1],'CSV_value':csvvalue,'source_raw_value':raw,'source_decoded_value':value,'matches_containing_native_stored_cell_1e_7':matches,'sample_sha256_float64':hashlib.sha256(out.tobytes()).hexdigest(),'claim':'encoding/identity diagnostic; coarser CSV resampling lineage not inferred from one-cell equality'})
 finally:
  for handle in handles.values():lib.GDALClose(handle)
 # B01 source resolution ambiguity: compare the same six locations with the supplied 20m representation.
 b01_20_path=a.rel(next((ROOT/byband['B01']['sen2cor_path'].split('/GRANULE/')[0]).glob('GRANULE/*/IMG_DATA/R20m/*_B01_20m.jp2')))
 b01_20_header=a.info(ROOT/b01_20_path);b01_20_checks=[]
 ds=lib.GDALOpen(str(ROOT/b01_20_path).encode(),0);assert ds
 try:
  for original in [c for c in checks if c['method']=='Sen2Cor' and c['band']=='B01']:
   r=paired['Sen2Cor'][(original['AOI'],original['pixel_id'])];g=b01_20_header['geoTransform'];col=math.floor((float(r['x'])-g[0])/g[1]);row=math.floor((float(r['y'])-g[3])/g[5]);v=np.empty(1,dtype='float64')
   assert lib.GDALRasterIO(lib.GDALGetRasterBand(ds,1),0,col,row,1,1,v.ctypes.data_as(C.c_void_p),1,1,7,0,0)==0
   val=(float(v[0])-1000)/10000
   b01_20_checks.append({'AOI':original['AOI'],'pixel_id':original['pixel_id'],'source_path':b01_20_path,'row_0based':row,'col_0based':col,'source_raw_value':float(v[0]),'source_decoded_value':val,'CSV_value':original['CSV_value'],'matches_1e_7':math.isclose(val,original['CSV_value'],abs_tol=1e-7,rel_tol=0),'sample_sha256_float64':hashlib.sha256(v.tobytes()).hexdigest(),'interpretation':'20m stored representation check; native sensor support remains 60m; export interpolation weights unverified'})
 finally:lib.GDALClose(ds)
 a.writecsv('tables/aoi_B01_representation_checks.csv',b01_20_checks)
 a.writecsv('tables/aoi_source_spotchecks.csv',checks)
 a.dump('outputs/aoi_intake.json',{'requested_path_literal':'Data/Raw/Atm_Compare_AOI','actual_path':'data/raw/Atm_Compare_AOI','used_inputs':[x for x in inventory if x['used']],'groups':intake,'all_row_checks':{'paired_AOI_pixel_keys':len(paired['Sen2Cor']),'common_centres_and_boundaries':True,'zero_based_row_col_matches_source_grids':True,'integer_crop_offset':[3405,9006],'station_containing_cell_matches':sum(x['exact_containing_cell_matches'] for x in joins)},'polygon_checks':polygon_checks,'spotchecks':{'rule':'first, midpoint and last CSV row per AOI, all available bands; chosen without ASD comparison','scalar_read_count':len(checks)+len(b01_20_checks),'B01_20m_followup_checks':len(b01_20_checks),'B01_20m_followup_matches':sum(c['matches_1e_7'] for c in b01_20_checks),'primary_band_checks':sum(c['band'] in BANDS for c in checks),'primary_band_matches':sum(c['band'] in BANDS and c['matches_containing_native_stored_cell_1e_7'] for c in checks),'mismatches_by_method_band':dict(Counter(c['method']+':'+c['band'] for c in checks if not c['matches_containing_native_stored_cell_1e_7']))},'eligibility':'not station matchups; no QA/aggregation/producer script or upstream resampling weights supplied; no automatic inclusion'})
 a.writecsv('tables/aoi_input_inventory.csv',inventory)
 # Normalized held design. Addresses are stable source IDs; byte identity strength remains explicit.
 run=json.loads((P/'provenance/run.json').read_text());sources=[]
 for i in run['inputs']:
  sources.append({'source_id':uid('source',i['path']),'path':i['path'],'sha256':i['sha256'],'identity_scope':i['hash_scope'],'bytes':i['bytes'],'mtime_ns':i['mtime_ns']})
 for i in inventory:
  if i['used']:sources.append({'source_id':uid('source',i['path']),'path':i['path'],'sha256':i['sha256'],'identity_scope':'whole_file','bytes':i['bytes'],'mtime_ns':i['mtime_ns']})
 # B09 is diagnostic only and was not in the original 11-pair header list.
 for i in a.used.values():
  if i['path'] not in {s['path'] for s in sources}:sources.append({'source_id':uid('source',i['path']),**i})
 for source in sources:
  path=source['path']
  if path in headers:
   h=headers[path];source.update(grid_id=uid('grid',source['source_id'],h['geoTransform']),CRS='EPSG:32628',geoTransform=h['geoTransform'],shape=h['size'])
  for b in bands:
   if path==b['sen2cor_path']:source.update(correction='operational L2A',band_id=b['band'],quantity='surface reflectance',original_unit='integer DN',decoded_unit='1',scale=0.0001,offset=-0.1,special_codes=[0,65535],decode_order='mask special codes then decode',native_sensor_resolution_m=int(b['sen2cor_native_support_m']),processing_baseline='05.12')
   if path==b['acolite_path']:source.update(correction='ACOLITE DSF',band_id=b['band'],quantity='surface_bidirectional_reflectance rhos',original_unit='1',decoded_unit='1',scale=1,offset=0,special_codes=['NaN/nonfinite'],native_sensor_resolution_m=int(b['sen2cor_native_support_m']),version=b['acolite_version'],upstream_L1C=b['acolite_inputfile'])
 source_ids={s['path']:s['source_id'] for s in sources};safe_scene=data['Sen2Cor'][0]['scene_id'];ac_scene=data['ACOLITE'][0]['scene_id'];scene_pair=uid('scene-pair',safe_scene,ac_scene)
 targets=[];refs=[];occasions=[];support=[];qas=[];qalinks=[];matchups=[];graph_edges=[]
 qa_path=next(k for k in headers if k.endswith('SCL_20m.jp2'));srf=json.loads((P/'outputs/data_contract.json').read_text())['convolution'];srfpath=srf['primary_reference'];srfhash=next(x['sha256'] for x in sources if x['path']==srfpath)
 srfrows={r['band']:r for r in rows('srf_coverage.csv')}
 for s,d,j in zip(st,di,joins):
  target=uid('target',s['station_id']);ref=uid('reference',source_ids[s['asd_path']],s['asd_column_raw']);occasion=uid('occasion',s['station_id'],s['field_date'],'supplied-single-average');site=None
  targets.append({'target_id':target,'station_id':s['station_id'],'raw_IDs':{k:s[k] for k in ['asd_column_raw','cover_station_raw','gps_station_raw']},'join_cardinality':'1:1:1','role':s['role'],'class_literal':s['target_class_raw'],'class_verified':None,'site_id':site,'site_raw':s['location_raw'],'site_evidence_status':'unknown; AC01/02 conflict retained','field_footprint':None,'field_footprint_status':'unknown','position_accuracy_m':None,'lat':float(s['lat_raw']),'lon':float(s['lon_raw']),'CRS':'EPSG:4326'})
  refs.append({'reference_id':ref,'target_id':target,'source_id':source_ids[s['asd_path']],'source_column':s['asd_column_raw'],'unit':'1','wavelength_unit':'nm','conversion':'identity','aggregation':'supplied station average (PI)','membership':None,'weights':None,'repeat_count':None,'variance':None,'instrument':s['instrument'],'panel':s['reference_panel'],'geometry':s['field_geometry'],'exposure_at_field':'exposed intertidal','evidence':field['interaction_id']})
  occasions.append({'occasion_id':occasion,'target_id':target,'reference_id':ref,'field_date':s['field_date'],'field_time_start_utc':None,'field_time_end_utc':None,'field_timezone':None,'time_precision':'date only','single_exported_average_verified':True,'physical_occasion_membership':'unknown beyond station/day average','satellite_time_utc':'2026-03-27T11:45:53.975343Z','overpass_exposure':'unknown'})
  qa_id=uid('qa-cell',source_ids[qa_path],int(d['scl_row']),int(d['scl_col']))
  if qa_id not in {q['qa_cell_id'] for q in qas}:qas.append({'qa_cell_id':qa_id,'source_id':source_ids[qa_path],'grid_id':uid('grid',source_ids[qa_path],headers[qa_path]['geoTransform']),'native_resolution_m':20,'row_0based':int(d['scl_row']),'col_0based':int(d['scl_col']),'raw_scl':int(d['scl_center']),'transfer_rule':'containing categorical cell; no bilinear','mask_validity':'not_evaluated','common_decision':'unknown','other_native_flags':'MSK_QUALIT/MSK_DETFOO not decoded; ACOLITE l2_flags absent'})
  for b in bands:
   band=b['band'];cov=srfrows[band];spectral='pass' if cov['coverage_pass_if_nm']=='True' else 'fail';mid=uid('matchup',target,occasion,band,VERSION)
   reasons=['field_support_unknown','registration_unknown','overpass_comparability_unknown','essential_QA_not_evaluated','grouping_unresolved','supplied_AOI_has_no_station_cell']
   if s['station_id'] in ['AC01','AC02']:reasons.insert(0,'AC01_02_location_conflict')
   if spectral=='fail':reasons.insert(0,'B08_incomplete_spectral_coverage' if band=='B08' else 'no_ASD_spectral_coverage')
   if int(b['sen2cor_native_support_m'])>10:reasons.insert(0,'coarser_field_support_unestablished')
   if s['role']=='supplementary_candidate':reasons.insert(0,'supplementary_outside_primary_population')
   matchups.append({'matchup_id':mid,'target_id':target,'occasion_id':occasion,'reference_id':ref,'scene_pair_id':scene_pair,'band_id':band,'extraction_version':VERSION,'source_ids':[source_ids[b['sen2cor_path']],source_ids[b['acolite_path']]],'spectral_reference_id':uid('srf',srfhash,'S2B',band),'coverage_numerator':float(cov['integral_response'])*float(cov['response_fraction_in_ASD_range_if_nm']),'coverage_denominator':float(cov['integral_response']),'SRF_column':'S2B_SR_AV_'+band.replace('B0','B'),'spectral_validity':spectral,'reference_validity':'not_evaluated','physical_validity':'unknown','Sen2Cor_validity':'not_evaluated','ACOLITE_validity':'not_evaluated','paired_validity':'not_evaluated','include_primary':False,'paired_valid':False,'all_reasons':reasons,'primary_reason':reasons[0],'reason_stage':'feasibility','reason_evidence':field['interaction_id']+'; tables/aoi_station_join.csv; outputs/aoi_intake.json','rule_version':VERSION,'component_id':None,'resampling_unit_id':None,'ASD_reflectance':None,'Sen2Cor_reflectance':None,'ACOLITE_reflectance':None,'statistical_weight':None})
   qalinks.append({'matchup_id':mid,'qa_cell_id':qa_id,'role':'QA_only; not radiometric support'})
   for method in ['Sen2Cor','ACOLITE']:
    path=b['sen2cor_path' if method=='Sen2Cor' else 'acolite_path'];h=headers[path];g=h['geoTransform'];x,y=float(d['x_if_wgs84']),float(d['y_if_wgs84']);col=math.floor((x-g[0])/g[1]);row=math.floor((y-g[3])/g[5]);x0=g[0]+col*g[1];y1=g[3]+row*g[5]
    support.append({'matchup_id':mid,'correction':method,'source_id':source_ids[path],'band_id':band,'grid_id':uid('grid',source_ids[path],g),'output_cell_locator':f'row={row};col={col};zero_based','output_boundary_EPSG32628':[x0,y1+g[5],x0+g[1],y1],'original_sensor_resolution_m':int(b['sen2cor_native_support_m']),'output_resolution_m':g[1],'candidate_native_cell_locator':f'row={row};col={col}' if method=='Sen2Cor' else None,'actual_primary_contributor':False,'contributor_status':'candidate locator only; primary field support not approved','upstream_native_contributors':None,'native_lineage_status':'native nominal cell; effective sensor kernel unknown' if method=='Sen2Cor' else 'upstream resampling weights unavailable; TIFF says bilinear; grid match alone insufficient','upstream_support_bound':None,'extraction_weight':None,'valid_contributor_count':None,'total_contributor_count':None,'support_weight_status':'not_evaluated'})
 # Typed known nominal relations. No diagnostic window becomes a primary contributor.
 for i,d in enumerate(di):
  for j in range(i+1,len(di)):
   e=di[j]
   if d['hypothetical_10m_pixel_cluster']==e['hypothetical_10m_pixel_cluster']:graph_edges.append({'from_station':d['station_id'],'to_station':e['station_id'],'type':'shared_candidate_native_10m_cell','evidence':'PI CRS + coordinate-derived SAFE cell','domain':'supplementary candidate; outside primary graph','merge_if_admitted':True,'actual_primary_support_confirmed':False})
   if (d['scl_col'],d['scl_row'])==(e['scl_col'],e['scl_row']):graph_edges.append({'from_station':d['station_id'],'to_station':e['station_id'],'type':'shared_QA_cell','evidence':'SCL20m qualified source cell','domain':'auxiliary_QA','merge_if_admitted':False,'actual_primary_support_confirmed':False})
 graph={'version':VERSION,'domain':{'stations':['AC%02d'%i for i in range(1,9)],'bands':BANDS,'support':'actual primary contributors only; excludes diagnostic 3x3 and coarse bands'},'status':'unresolved; no final G or components assigned','edges':graph_edges,'merge_rule':'union actual shared radiometric/field/repeated-unit edges across both corrections and B*, transitive closure then evidenced site/block merges; freeze before errors; never split after exclusions','QA_rule':'QA-only sharing is not radiometric merge; conservative QA grouping sensitivity separate','unresolved':['field overlap/accuracy','AC01/02 site conflict','ACOLITE upstream support envelope','empirical registration','station/site dependence'],'components':None}
 graph['sha256']=hashlib.sha256(json.dumps(graph,sort_keys=True).encode()).hexdigest()
 a.dump('outputs/dependence_graph.json',graph)
 norm={'schema':'ctrlsea.matchup-feasibility.v2','version':VERSION,'null_semantics':'null unknown/not evaluated, never zero/pass; booleans false while held','sources':sources,'targets':targets,'references':refs,'occasions':occasions,'scene_pairs':[{'scene_pair_id':scene_pair,'operational_L2A':safe_scene,'ACOLITE':ac_scene,'satellite_time_utc':'2026-03-27T11:45:53.975343Z','byte_identical_L1C_lineage':'unestablished'}],'matchups':matchups,'radiometric_support_candidates':support,'qa_cells':qas,'matchup_qa_links':qalinks,'target_complete_spectrum':[{'target_id':t['target_id'],'bands':BANDS,'status':'not_evaluated','complete_valid':False} for t in targets]}
 norm['spectral_references']=[{'spectral_reference_id':uid('srf',srfhash,'S2B',b['band']),'source_id':source_ids[srfpath],'sha256':srfhash,'version':'supplied v4.0','platform':'S2B','sheet':'Spectral Responses (S2B)','column':'S2B_SR_AV_'+b['band'].replace('B0','B'),'band_id':b['band'],'wavelength_unit':'nm','coverage_numerator':float(srfrows[b['band']]['integral_response'])*float(srfrows[b['band']]['response_fraction_in_ASD_range_if_nm']),'coverage_denominator':float(srfrows[b['band']]['integral_response']),'minimum_coverage':0.999,'convolution_policy':'outputs/data_contract.json: convolution'} for b in bands]
 norm['analysis_manifest']={'analysis_set_id':uid('analysis-set',VERSION,BANDS,'AC01-08'),'status':'held; not frozen/released','population':['AC%02d'%i for i in range(1,9)],'bands':BANDS,'schema_version':VERSION,'design_revision':'0744faa6-f2e0-493b-a9f8-0fe88904a8a7','concurrence_revision':field['concurrence_revision'],'reconciliation_revision':field['reconciliation_revision'],'support_rule_version':VERSION,'QA_rule_version':VERSION,'graph_sha256':graph['sha256'],'source_ids':[s['source_id'] for s in sources],'weights':'outputs/data_contract.json: statistics_handoff.weights','environment_lock_hashes':run['locks'],'freeze_time_utc':None,'freeze_authority':None}
 a.dump('outputs/normalized_design.json',norm)
 ledger=rows('proposed_matchups.csv');mapping={(t['station_id'],m['band_id']):m for t in targets for m in matchups if m['target_id']==t['target_id']}
 for r in ledger:
  m=mapping[(r['station_id'],r['band'])]
  for k in ['matchup_id','target_id','occasion_id','reference_id','scene_pair_id','extraction_version','primary_reason','rule_version','component_id','resampling_unit_id','spectral_validity','physical_validity','paired_validity']:r[k]=m[k]
  r['hold_reasons']=';'.join(m['all_reasons']);r['extraction_status']='not_extracted; material support/time/QA/grouping holds';r['field_evidence']=field['interaction_id']
 a.writecsv('tables/proposed_matchups.csv',ledger)
 contract=json.loads((P/'outputs/data_contract.json').read_text());contract.update(schema=norm['schema'],normalized_design='outputs/normalized_design.json',normalized_key=['target_id','occasion_id','band_id','extraction_version'],staging_key=['station_id','band'],primary_key=['matchup_id'],field_evidence='provenance/field_evidence.json',dependence_graph='outputs/dependence_graph.json',schema_version=VERSION,null_semantics=norm['null_semantics'])
 contract['convolution'].update(primary_reference_sha256=srfhash,ASD_units='PI-confirmed unitless 0-1; identity conversion',ASD_wavelength_unit='PI-confirmed nm',integration='trapezoidal on union knots; interpolate only adjacent finite ASD samples <=1 nm; no extrapolation',version_sensitivity='v5 separate reference after release; no convolution in amendment')
 contract['statistics_handoff']={'concurrence_revision':field['concurrence_revision'],'status':'schema completed as held design; not an executable released extraction','sets':{'P_b':'reference + both methods + common physical/full-support QA pass for a band','P_star':'intersection P_b across fixed B02/B03/B04; same targets/reference in both facets'},'weights':{'complete_spectrum':'1/(G*T_g*3)','per_band':'1/(G_b*T_gb)','normalization':'identical normalized weights for both corrections; extraction weights separate; RMSE sqrt(weighted squared error)'},'complete_case_coverage':{'status':'pending Charles/Roger freeze before errors','required_inventory':['targets and original frozen units retained/lost','literal/verified class','site','timing/exposure/support','ordered exclusion reasons'],'rule':'all planned classes/sites must be represented and exposure/QA loss assessed; unknown types stay unknown; a primary-population claim requires a dated metadata-based justification; no automatic numerical percentage cutoff','empty_P_star':'NA pooled metrics with reason, per-band valid tables only','unrepresentative_P_star':'subset description only; withhold primary-population ranking','fallback':'dated Charles amendment before replacement display/estimand; no dropping bands/imputation/supplementary substitution to populate primary'},'grouping':'freeze graph before errors; never split components by method/band/type or after exclusion; no final independent-n yet','tiers':'G=0 no estimate; G=1-4 descriptive; G=5-19 unit contrasts + leave-one-unit-out; no inferential intervals/p-values/bootstrap for current <=8 primary targets','contrast':'ACOLITE minus operational L2A MAE; signed bias and RMSE companion descriptive measures after release','ecological_threshold':'required for ecological-importance/equivalence claim, not descriptive discrepancy','sensitivity':['supplied v4 versus separately hashed official v5','prespecified registration +/-1 pixel and footprint alternatives, own support graph','equal-target sensitivity if unit sizes differ; distinct estimand','QA-grouped sensitivity if materially relevant; not default radiometric merge'],'scientific_metrics_computed':False}
 contract['schema_checks']=['unique normalized keys/IDs; all foreign keys; 165 ledger rows retained','later extraction: numerical contributor weights sum to 1 on fixed full support; common identity, per-method/reference/physical/paired/complete-spectrum status','unknown essential support/QA/grouping blocks extraction; no null passed/defaulted','common complete sets and complete-case loss reconciliation before error inspection']
 a.dump('outputs/data_contract.json',contract)
 assert len(matchups)==len(ledger)==165 and len(support)==330 and not any(m['include_primary'] or m['paired_valid'] for m in matchups)
 assert len({(m['target_id'],m['occasion_id'],m['band_id'],m['extraction_version']) for m in matchups})==165
 after=a.snapshot();assert before==after,'raw input stat changed'
 a.dump('provenance/amendment_run.json',{'started_utc':start,'ended_utc':D.datetime.now(D.timezone.utc).isoformat(),'base_commit':a.run(['git','rev-parse','HEAD']).strip(),'input_inventory':'tables/aoi_input_inventory.csv','raw_stat_unchanged':before==after,'raw_file_count':len(before),'raw_stat_snapshot_sha256':hashlib.sha256(json.dumps(before,sort_keys=True).encode()).hexdigest(),'read_limits':'two March27 CSVs; all their tabular identities/centres; six predetermined AOI cells x available bands = 138 scalar raster reads, plus six B01 stored-20m follow-up reads, plus audit.py 405 diagnostic window values; driver blocks may be larger','scalar_raster_reads':len(checks)+len(b01_20_checks),'used_new_inputs':[x for x in inventory if x['used']],'commands':a.commands,'metrics_computed':False,'dependencies_changed':False,'code_sha256':{str(q.relative_to(P)):sha(q) for q in sorted((P/'scripts').glob('*')) if q.is_file()},'environment_lock_sha256':run['locks'],'review':'independent reassessment and PI approval pending'})
 print(json.dumps({'CSV_rows_per_method':len(data['Sen2Cor']),'station_cell_matches':sum(x['exact_containing_cell_matches'] for x in joins),'polygon_checks':polygon_checks,'spotcheck_count':len(checks),'mismatches':Counter(c['method']+':'+c['band'] for c in checks if not c['matches_containing_native_stored_cell_1e_7']),'normalized_matchups':len(matchups),'included':0}))
if __name__=='__main__':main()
