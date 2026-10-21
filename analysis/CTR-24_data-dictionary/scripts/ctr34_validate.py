#!/usr/bin/env python3
"""Scientific release invariants, independent numerical checks, and preservation validation."""
import csv,json,collections,hashlib,subprocess,itertools
import numpy as np
import ctr34_support as m
import ctr34_extract as e
P=m.P;ROOT=m.ROOT

def main():
 checks=[]
 def check(name,condition):
  assert condition,name;checks.append({'check':name,'status':'pass'})
 c=json.loads((P/'outputs/ctr34_release_contract.json').read_text());ts=m.rows('tables/ctr34_targets.csv');lg=m.rows('tables/ctr34_candidate_ledger.csv');sp=m.rows('tables/ctr34_support.csv');qa=m.rows('tables/ctr34_qa_cells.csv');links=m.rows('tables/ctr34_qa_links.csv');w=m.rows('tables/ctr34_weights.csv');ref=json.loads((P/'outputs/ctr34_references_occasions.json').read_text());old=json.loads((P/'outputs/normalized_design.json').read_text());ids={t['target_id'] for t in ts};rids={r['reference_id'] for r in ref['references']};oids={r['occasion_id'] for r in ref['occasions']};scenes={r['scene_pair_id'] for r in old['scene_pairs']};mids={r['matchup_id'] for r in lg};qids={r['qa_cell_id'] for r in qa}
 check('165 historical candidates; 15 targets; unique normalized key and matchup ID',len(lg)==165 and len(ts)==15 and len(mids)==165 and len({(r['target_id'],r['occasion_id'],r['band_id'],r['extraction_version']) for r in lg})==165)
 check('historical station-band mapping preserved one-to-one', {(r['station_id'],r['band_id']) for r in lg}=={(r['station_id'],r['band']) for r in m.rows('tables/proposed_matchups.csv')})
 check('reference/occasion/scene/target foreign keys',all(r['target_id'] in ids and r['reference_id'] in rids and r['occasion_id'] in oids and r['scene_pair_id'] in scenes for r in lg))
 check('support and QA key/foreign-key cardinality',len(sp)==36 and len({r['support_id'] for r in sp})==36 and len(qids)==len(qa) and all(r['matchup_id'] in mids for r in sp) and all(r['matchup_id'] in mids and r['qa_cell_id'] in qids for r in links) and len({(r['matchup_id'],r['qa_cell_id']) for r in links})==len(links))
 check('six primary x three bands; common pair held; ledger mutually reconciled',len([r for r in lg if r['role']=='primary_intended' and r['band_id'] in m.BANDS])==18 and collections.Counter(r['primary_reason'] for r in lg)['PI_mud_microphytobenthos_excluded']==22 and len([r for r in lg if r['role']=='supplementary_only'])==77 and all(r['included_pair']=='False' for r in lg))
 check('included numerical fields null while held',all(all(r[k]=='' for k in ['eligible_ASD_reflectance','eligible_L2A_reflectance','eligible_ACOLITE_reflectance','statistical_weight']) for r in lg))
 check('empty eligible P_b/P* table is header only',not m.rows('tables/ctr34_eligible_pairs.csv') and c['P_star']==[] and all(not x for x in c['P_b'].values()))
 check('stored extraction weights normalize independently of statistical weights',all(float(s['numerical_extraction_weight'])==1 and s['stored_contributor_total']=='1' and s['statistical_weight']=='' for s in sp) and all(r['complete_spectrum_statistical_weight']==r['per_band_statistical_weight']=='' for r in w))
 check('unknown grouping not fabricated as singleton/QA groups',c['actual_G'] is None and json.loads((P/'outputs/ctr34_dependence_graph.json').read_text())['connected_components'] is None and all(r['resampling_unit_id']=='' for r in ts))
 for sid,b in itertools.product(m.PRIMARY,m.BANDS):
  rr=[r for r in sp if r['station_id']==sid and r['band_id']==b];check('common stored boundary '+sid+':'+b,len(rr)==2 and all(rr[0][k]==rr[1][k] for k in ['xmin','ymin','xmax','ymax','CRS']))
 check('nominal mask envelopes: 3600 clear defect flags; 450 valid detector values; SCL conditional',len([r for r in m.rows('tables/ctr34_local_qa.csv') if r['kind']=='QUALIT'])==3600 and all(int(r['raw'])==0 for r in qa if r['kind']=='QUALIT') and len([r for r in m.rows('tables/ctr34_local_qa.csv') if r['kind']=='DETFOO'])==450 and all(1<=int(r['raw'])<=12 for r in qa if r['kind']=='DETFOO') and set(int(r['raw']) for r in qa if r['kind']=='SCL')<={4,5,6})
 decoded=m.decode(np.array([0,65535,1000,500,11000],dtype=np.float64));check('special codes masked before decoding; valid negative retained',np.isnan(decoded[:2]).all() and np.allclose(decoded[2:],[0,-.05,1],rtol=0,atol=1e-15))
 raw=m.rows('tables/ctr34_raw_decode.csv');check('36 original centre reads agree with decoding and stored 11x11 diagnostics',len(raw)==36 and all(abs(float(r['decoded_reflectance'])-((float(r['raw_value'])-1000)/10000 if r['method']=='L2A' else float(r['raw_value'])))<1e-14 for r in raw))
 im=m.rows('tables/ctr34_local_imagery.csv')
 for r in raw:
  z=next(x for x in im if x['station_id']==r['station_id'] and x['method']==r['method'] and x['band']==r['band_id'] and x['dx']==x['dy']=='0');check('centre/window consistency '+r['station_id']+r['method']+r['band_id'],abs(float(z['reflectance'])-float(r['decoded_reflectance']))<1e-14)
 check('new current spectra and diagnostics exclude AC03/04; supplementary not substituted',all(r['station_id'] not in ['AC03','AC04'] for name in ['ctr34_current_spectra.csv','ctr34_current_spectral_summary.csv','ctr34_held_diagnostics.csv','ctr34_convolved_references.csv','ctr34_local_imagery.csv'] for r in m.rows('tables/'+name)) and len(m.rows('tables/ctr34_current_spectral_summary.csv'))==13 and {r['station_id'] for r in m.rows('tables/ctr34_held_diagnostics.csv')}==set(m.PRIMARY))
 # Analytic checks catch normalization, scaling, extrapolation and missing-interval failures.
 wl=np.arange(400.,901.);curve=np.array([[449.,0.],[450.,1.],[550.,1.],[551.,0.]])
 a=e.convolve(wl,np.full(wl.shape,.25),curve);check('constant reflectance preserved by response convolution',a[1]=='pass' and abs(a[0]-.25)<1e-14)
 a=e.convolve(wl,wl/1000,curve);check('linear reflectance and symmetric SRF analytic mean',abs(a[0]-.5)<1e-14)
 yy=np.full(wl.shape,.25);yy[100]=np.nan;check('missing interval intersecting positive SRF rejected',e.convolve(wl,yy,curve)[1]=='missing_positive_response_interval')
 check('positive response outside ASD rejected without truncation',e.convolve(wl,np.full(wl.shape,.25),np.array([[350.,0.],[399.,1.],[401.,0.]]))[0] is None)
 # Independent actual-data quadrature on the 1nm ASD grid (the supplied curves share 1nm knots).
 rr=m.rows('tables/ctr34_convolved_references.csv');check('18 v4 references and 18 separately identified v5 sensitivities',collections.Counter(r['SRF_role'] for r in rr)=={'v4_primary':18,'v5_sensitivity':18})
 names=(ROOT/rr[0]['ASD_source']).open().readline().split();data=np.loadtxt(ROOT/rr[0]['ASD_source'],skiprows=1)
 for version in ['v4_primary','v5_sensitivity']:
  group=[r for r in rr if r['SRF_role']==version];cur=e.curves(ROOT/group[0]['SRF_file'])
  for r in group:
   x,y=cur[r['band_id']]['curve'].T;reflect=data[:,names.index(r['ASD_column'])];inter=np.interp(x,data[:,0],reflect,left=np.nan,right=np.nan);product=np.zeros(len(x));positive=y>0;product[positive]=inter[positive]*y[positive]
   # Explicit sums rather than production np.trapezoid/union-knot path.
   den=sum((y[1:]+y[:-1])*np.diff(x)/2);num=sum((product[1:]+product[:-1])*np.diff(x)/2);check('independent reference integral '+version+r['station_id']+r['band_id'],abs(float(r['convolved_reflectance'])-num/den)<2e-14)
 loc=m.rows('tables/ctr34_locations.csv');out=subprocess.check_output(['gdaltransform','-s_srs','EPSG:32628','-t_srs','EPSG:4326'],input='\n'.join(r['x_m']+' '+r['y_m'] for r in loc),text=True).splitlines();check('coordinate order and roundtrip to WGS84 within 1e-9 degree',all(abs(float(v.split()[0])-float(r['lon']))<1e-9 and abs(float(v.split()[1])-float(r['lat']))<1e-9 for v,r in zip(out,loc)))
 for name,digest in c['frozen_files'].items():check('frozen metadata bytes '+name,m.sha(P/name)==digest)
 run=json.loads((P/'provenance/ctr34_extract.json').read_text());check('release contract timestamp and Git freeze precede diagnostic export',c['created_utc']<run['started_utc'] and run['freeze_contract_sha256']==m.sha(P/'outputs/ctr34_release_contract.json'))
 check('all raw path/size/mtime records preserved',m.raw_snapshot()==json.loads((P/'provenance/ctr34_raw_before.json').read_text()))
 accepted=json.loads((P/'provenance/ctr34_baseline_run.json').read_text());check('full-byte small inputs match accepted audit identities',all(m.sha(ROOT/i['path'])==i['sha256'] for i in accepted['inputs'] if i.get('sha256') and (ROOT/i['path']).exists()))
 check('no lockfile/dependency changes',run['locks']=={s:m.sha(ROOT/s) for s in ['uv.lock','renv.lock']})
 # Check declared formulas with unequal artificial component sizes, never observed data or metric values.
 simulated=[1/(2*t*3) for t in [1,2] for _ in range(t*3)];perband=[1/(2*t) for t in [1,2] for _ in range(t)];check('statistical weighting algebra sums to one in unequal-unit fixture',abs(sum(simulated)-1)<1e-14 and abs(sum(perband)-1)<1e-14)
 m.dump('provenance/ctr36_legacy_validation.json',{'completed_utc':m.now(),'status':'pass','checks':checks,'check_count':len(checks),'scope':'technical and numerical consistency; not independent scientific review or PI approval','raw_preservation_scope':'whole inventory path/size/mtime plus full small-input hashes and repeated window byte hashes; no full-byte 91GB identity claim'})
 print(len(checks),'checks passed')
if __name__=='__main__':main()
