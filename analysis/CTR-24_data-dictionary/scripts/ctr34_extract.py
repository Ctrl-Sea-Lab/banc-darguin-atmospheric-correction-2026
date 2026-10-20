#!/usr/bin/env python3
"""Post-freeze held diagnostics and current non-mud spectra. Never computes ASD errors."""
import json,hashlib,subprocess,sys,platform
import numpy as np
import ctr34_support as m
P=m.P;ROOT=m.ROOT

def curves(p):
 rows=m.a.workbook(p)['Spectral Responses (S2B)'];head=rows[0]['cells'];out={}
 for col,name in head.items():
  if 'SR_AV_B' not in name:continue
  raw=name.split('SR_AV_')[-1];band='B'+raw[1:].zfill(2) if raw[1:].isdigit() else raw.upper();v=[]
  for r in rows[1:]:
   try:v.append((float(r['cells']['A']),float(r['cells'][col])))
   except (KeyError,ValueError):pass
  if v:out[band]={'column':col,'label':name,'curve':np.asarray(v)}
 return out

def convolve(wl,refl,curve):
 x,r=curve.T;assert np.all(np.diff(x)>0) and np.all(r>=0);den=float(np.trapezoid(r,x));inside=(x>=wl[0])&(x<=wl[-1]);coverage=float(np.trapezoid(r[inside],x[inside])/den)
 if coverage<.999:return None,'insufficient_coverage',None,den,coverage
 # Every ASD interval intersecting positive response must have finite adjacent endpoints <=1nm.
 bad=[]
 for i in range(len(wl)-1):
  if not (np.isfinite(refl[i]) and np.isfinite(refl[i+1]) and wl[i+1]-wl[i]<=1):
   xx=x[(x>=wl[i])&(x<=wl[i+1])];rr=np.interp(np.r_[wl[i],xx,wl[i+1]],x,r,left=0,right=0)
   if (rr>0).any():bad.append([float(wl[i]),float(wl[i+1])])
 if bad:return None,'missing_positive_response_interval',None,den,coverage
 knots=np.union1d(x,wl);rr=np.interp(knots,x,r,left=0,right=0);needed=rr>0
 # Positive response may not be extrapolated; excluded zero-response endpoints can be safely omitted from product.
 if ((knots[needed]<wl[0])|(knots[needed]>wl[-1])).any():return None,'positive_response_outside_ASD',None,den,coverage
 prod=np.zeros(knots.shape);prod[needed]=np.interp(knots[needed],wl,refl)*rr[needed]
 num=float(np.trapezoid(prod,knots));return num/den,'pass',num,den,coverage

def main():
 start=m.now();contract=P/'outputs/ctr34_release_contract.json';contract_sha=m.sha(contract);c=json.loads(contract.read_text());assert c['eligible_pairs']==0
 # The dated artifact must already be in Git, and its bytes equal the committed freeze.
 frozen=subprocess.check_output(['git','show','1f14a2d369a62498bd81de6813fe036e1ed49794:analysis/CTR-27_sen2cor-acolite-asd/outputs/ctr34_release_contract.json']);assert hashlib.sha256(frozen).hexdigest()==contract_sha
 before=m.raw_snapshot();assert before==json.loads((P/'provenance/ctr34_raw_before.json').read_text())
 st=m.rows('tables/station_crosswalk.csv');src=ROOT/st[0]['asd_path'];names=src.open().readline().split();arr=np.loadtxt(src,skiprows=1);wl=arr[:,0];assert np.array_equal(wl,np.arange(400,901))
 v4=ROOT/c['reference']['v4_primary']['primary_reference'];v5=P/'outputs/official-srf-v5.xlsx';srf={'v4_primary':(v4,curves(v4)),'v5_sensitivity':(v5,curves(v5))};refs=[];spec=[];summary=[];vals={}
 for s in st:
  sid=s['station_id']
  if sid in ['AC03','AC04']:continue
  y=arr[:,names.index(s['asd_column_raw'])];assert np.isfinite(y).all()
  summary.append({'station_id':sid,'class_literal':s['target_class_raw'],'role':'primary_intended_held' if sid in m.PRIMARY else 'supplementary_not_primary','n_wavelengths_not_replicates':len(y),'mean_across_channels':float(y.mean()),'SD_across_channels_ddof1':float(y.std(ddof=1)),'minimum':float(y.min()),'maximum':float(y.max()),'unit':'1','meaning':'spectrum description only; no repeated-measurement uncertainty'})
  for x,z in zip(wl,y):spec.append({'station_id':sid,'wavelength_nm':float(x),'reflectance':float(z),'class_literal':s['target_class_raw'],'role':'primary_intended_held' if sid in m.PRIMARY else 'supplementary_not_primary'})
  if sid not in m.PRIMARY:continue
  for version,(p,cur) in srf.items():
   for band in m.BANDS:
    val,status,num,den,cov=convolve(wl,y,cur[band]['curve']);assert status=='pass';vals[sid,band,version]=val
    refs.append({'station_id':sid,'band_id':band,'SRF_role':version,'SRF_file':str(p.relative_to(ROOT)),'SRF_sha256':m.sha(p),'sheet':'Spectral Responses (S2B)','wavelength_column':'A','response_column':cur[band]['column'],'response_label':cur[band]['label'],'ASD_source':str(src.relative_to(ROOT)),'ASD_sha256':m.sha(src),'ASD_column':s['asd_column_raw'],'coverage':cov,'response_weighted_numerator':num,'response_denominator':den,'convolved_reflectance':val,'unit':'1','reference_spectral_validity':status,'matchup_included':False,'status':'held_reference_diagnostic; not an included pair'})
 bc={b['band']:b for b in m.rows('tables/band_contract.csv')};loc={s['station_id']:s for s in m.rows('tables/ctr34_locations.csv')};ledger={r['matchup_id']:r for r in m.rows('tables/ctr34_candidate_ledger.csv')};sup=m.rows('tables/ctr34_support.csv');diag=[];raw=[]
 for sid in m.PRIMARY:
  for band in m.BANDS:
   ss=[s for s in sup if s['station_id']==sid and s['band_id']==band];d={'matchup_id':ss[0]['matchup_id'],'station_id':sid,'band_id':band,'ASD_v4_diagnostic':vals[sid,band,'v4_primary'],'ASD_v5_sensitivity_diagnostic':vals[sid,band,'v5_sensitivity'],'included_pair':False,'status':'HELD_DIAGNOSTIC_ONLY','physical_reason':ledger[ss[0]['matchup_id']]['all_reasons']}
   for s in ss:
    rr=m.Raster(ROOT/s['source_id']);v=rr.read(int(s['stored_col_0based']),int(s['stored_row_0based']));rr.close();rawval=float(v[0,0]);z=m.decode(v) if s['method']=='L2A' else v;val=float(z[0,0]);assert np.isfinite(val)
    d[s['method']+'_diagnostic']=val
    raw.append({'matchup_id':s['matchup_id'],'station_id':sid,'band_id':band,'method':s['method'],'source_id':s['source_id'],'row_0based':s['stored_row_0based'],'col_0based':s['stored_col_0based'],'raw_value':rawval,'decoded_reflectance':val,'unit':'1','special_value':False,'finite_decoded':True,'negative_retained':val<0,'numerical_extraction_weight':1.0,'contributing_stored_cells':1,'full_native_support_QA':'unknown','statistical_weight':None,'window_sha256_float64':hashlib.sha256(v.astype('<f8').tobytes()).hexdigest(),'status':'HELD_DIAGNOSTIC_ONLY','contract_sha256':contract_sha})
   diag.append(d)
 m.table('tables/ctr34_convolved_references.csv',refs);m.table('tables/ctr34_held_diagnostics.csv',diag);m.table('tables/ctr34_raw_decode.csv',raw);m.table('tables/ctr34_current_spectra.csv',spec);m.table('tables/ctr34_current_spectral_summary.csv',summary)
 m.table('tables/ctr34_eligible_pairs.csv',[],['matchup_id','target_id','occasion_id','reference_id','scene_pair_id','station_id','band_id','ASD_v4_reflectance','L2A_reflectance','ACOLITE_reflectance','component_id','per_band_weight','complete_spectrum_weight'])
 m.table('tables/ctr34_source_identity.csv',[{'path':str(p.relative_to(ROOT)),'identity_strength':'full_file_SHA256','sha256':m.sha(p),'bytes':p.stat().st_size,'mtime_ns':p.stat().st_mtime_ns} for p in [src,v4,v5,ROOT/st[0]['gps_path'],ROOT/st[0]['cover_path'],ROOT/'data/raw/ASD/202603_Measurement_log.txt']])
 # Optional relative-registration diagnostic compares texture only, never ASD or correction performance.
 im=m.rows('tables/ctr34_local_imagery.csv');reg=[]
 for sid in m.PRIMARY:
  for band in m.BANDS:
   vv={method:np.array([float(x['reflectance']) for x in im if x['station_id']==sid and x['band']==band and x['method']==method]).reshape(11,11) for method in ['L2A','ACOLITE']}
   for dy,dx in __import__('itertools').product([-1,0,1],repeat=2):
    a=vv['L2A'][1:10,1:10].ravel();b=vv['ACOLITE'][1+dy:10+dy,1+dx:10+dx].ravel();aa=a-a.mean();bb=b-b.mean();corr=float(aa@bb/np.sqrt((aa@aa)*(bb@bb)))
    reg.append({'station_id':sid,'band_id':band,'shift_dx_pixels':dx,'shift_dy_pixels':dy,'texture_correlation':corr,'applied_shift':False,'meaning':'relative source-image diagnostic; no ASD correlation, ground control, or empirical registration accuracy'})
 m.table('tables/ctr34_relative_registration.csv',reg)
 after=m.raw_snapshot();assert before==after
 m.dump('provenance/ctr34_extract.json',{'started_utc':start,'completed_utc':m.now(),'freeze_contract_sha256':contract_sha,'freeze_commit':'1f14a2d369a62498bd81de6813fe036e1ed49794','contract_document_revision':'93ceeeeb-41b8-4734-b977-36208ab764ff','eligible_pair_count':0,'held_pair_diagnostic_count':len(diag),'held_reference_count_by_SRF':18,'raw_decode_diagnostics':len(raw),'current_nonmud_spectra':len(summary),'raw_stat_unchanged':True,'python':sys.version,'numpy':np.__version__,'GDAL':subprocess.check_output(['gdalinfo','--version'],text=True).strip(),'host':platform.node(),'locks':{s:m.sha(ROOT/s) for s in ['uv.lock','renv.lock']},'metrics_calculated':False,'rankings_examined':False,'reference_rule':'response-weighted union-knot trapezoid; missing intervals checked; no positive-response extrapolation; no noisy intervals independently documented; no invented noise filter'})
 print('0 eligible; 18 held diagnostics; 18 reference values each v4/v5; 13 current nonmud spectra')
if __name__=='__main__':main()
