#!/usr/bin/env python3
"""Author QA with independent GDAL CLI point reads and independent SRF quadrature.
This validates the numerical handoff, not scientific eligibility or accuracy.
"""
import collections, csv, hashlib, itertools, json, math, subprocess
from pathlib import Path
import numpy as np
import ctr42_extract as m
P,ROOT=m.P,m.ROOT

def main():
    checks=[]
    def check(name,ok):
        if not ok:
            m.dump('provenance/ctr42_validation.json',dict(status='failed',failure=name,passed=checks)); raise AssertionError(name)
        checks.append(name)
    def read(name): return m.rows(P/'tables'/name)
    sat,refs,st,led,src,cov,win,qa=[read('ctr42_'+n+'.csv') for n in ['satellite','references','stations','availability','sources','srf_coverage','windows','qa']]
    ids={r['station_id'] for r in st}; expected=set(itertools.product(ids,m.BANDS))
    check('13 retained identities; literal original mud exclusions',len(st)==13 and ids=={'AC01','AC02','AC05','AC06','AC07','AC08'}|{'D06_'+c for c in 'ABCDEFG'} and {r['station_id']:r['class_literal'] for r in read('ctr42_exclusions.csv')}==m.EXCLUDED)
    check('234 unique satellite rows cover every retained station, band and correction',len(sat)==234 and {(r['station_id'],r['band_id'],r['correction']) for r in sat}=={(*k,c) for k in expected for c in ['Sen2Cor','ACOLITE']})
    check('234 unique reference rows cover both explicit SRF versions',len(refs)==234 and {(r['station_id'],r['band_id'],r['SRF_role']) for r in refs}=={(*k,c) for k in expected for c in ['v4_primary','v5_sensitivity']})
    check('117 availability rows; no excluded station extraction',len(led)==117 and {(r['station_id'],r['band_id']) for r in led}==expected and all(r['station_id'] in ids for r in win+qa))
    for r in src: check('full input SHA256 unchanged '+r['path'],m.sha(ROOT/r['path'])==r['sha256'])
    for r in sat:
        s=next(s for s in st if s['station_id']==r['station_id']); x,y=float(s['x_32628_m']),float(s['y_32628_m'])
        x0,y0,x1,y1=json.loads(r['cell_bounds_EPSG32628_json'])
        check('coordinate falls inside stored footprint '+r['station_id']+r['band_id']+r['correction'],x0<=x<x1 and y0<y<=y1 and x1-x0==y1-y0==float(r['stored_resolution_m']))
        # Different tool interface, WGS84 transform and cell lookup from production C API.
        v=float(m.run(['gdallocationinfo','-valonly','-wgs84',str(ROOT/r['source_path']),s['longitude'],s['latitude']]).strip())
        check('independent GDAL WGS84 point raw read '+r['station_id']+r['band_id']+r['correction'],math.isfinite(v) and abs(v-float(r['raw_value']))<1e-12)
        z=(v-1000)/10000 if r['correction']=='Sen2Cor' else v
        check('independent reflectance scale '+r['station_id']+r['band_id']+r['correction'],abs(z-float(r['reflectance']))<1e-12 and r['unit']=='1' and r['validation_eligible']=='False')
    check('actual source values finite without zero/NoData substitution',all(r['availability_reason']=='available_stored_value' for r in sat))
    # Independently computed SRF sums on their original 1nm knots, not production union knots.
    curves={}
    arr=np.loadtxt(ROOT/refs[0]['ASD_source'],skiprows=1)
    names=(ROOT/refs[0]['ASD_source']).open().readline().split()
    for r in refs:
        p=ROOT/r['SRF_file']; curves.setdefault(str(p),m.curves(p)) if str(p) not in curves else None
        x,y=curves[str(p)][r['band_id']]['curve'].T
        dx=np.diff(x); den=math.fsum((y[i]+y[i+1])*dx[i]/2 for i in range(len(dx)))
        inside=(x>=arr[0,0])&(x<=arr[-1,0]); xx=x[inside]; yy=y[inside]
        fraction=math.fsum((yy[i]+yy[i+1])*(xx[i+1]-xx[i])/2 for i in range(len(xx)-1))/den
        check('independent coverage '+r['station_id']+r['band_id']+r['SRF_role'],abs(fraction-float(r['response_fraction_inside_ASD']))<2e-14)
        if r['band_id']=='B08':
            check('B08 unsupported NA with measured coverage deficit '+r['station_id']+r['SRF_role'],r['ASD_reflectance']=='NA' and r['response_weighted_numerator']=='NA' and r['reference_status']=='insufficient_coverage' and fraction<.999)
        else:
            vals=np.interp(x,arr[:,0],arr[:,names.index(r['ASD_column'])],left=np.nan,right=np.nan)
            product=np.where(y>0,vals*y,0)
            num=math.fsum((product[i]+product[i+1])*dx[i]/2 for i in range(len(dx)))
            check('independent reference quadrature '+r['station_id']+r['band_id']+r['SRF_role'],r['reference_status']=='pass' and abs(num/den-float(r['ASD_reflectance']))<2e-14)
    check('B08 missing in both SRF roles; 208 finite values across eight bands',sum(r['ASD_reflectance']!='NA' for r in refs)==208 and all(r['ASD_reflectance']=='NA' for r in refs if r['band_id']=='B08'))
    check('all 36 prior B02/B03/B04 references reproduced without numerical change',sum(r['matches_prior_threeband_value']=='True' for r in refs)==36)
    scene=m.js(P/'provenance/ctr42_scene_pair.json')
    check('metadata confirms exact same sensing time and granule; upstream byte identity not asserted',scene['metadata_consistent_same_acquisition'] and not scene['byte_identical_L1C_ancestry_verified'] and scene['acolite']['granule']=='L1C_T28QCH_A047010_20260307T114112' and scene['sen2cor_tile']['SENSING_TIME']==['2026-03-07T11:45:54.425534Z'])
    check('all field dates remain March27 and 20-day mismatch remains explicit',all(r['field_date']=='2026-03-27' and r['field_minus_satellite_days']=='20' and r['validation_eligible']=='False' for r in st+sat))
    check('117 finite-table ledger rows remain scientifically held',all(r['validation_eligible']=='False' and 'field_20_days_after_satellite' in r['hold_reason'] for r in led))
    check('104 finite triples per version are availability counts, not eligible samples',sum(r['common_finite_triple_v4']=='True' for r in led)==104 and sum(r['common_finite_triple_v5']=='True' for r in led)==104)
    for r in win:
        v=np.asarray(json.loads(r['values_json']),dtype='<f8')
        check('window shape and hash '+r['station_id']+r['band_id']+r['method']+r['layer'],v.shape==(int(r['rows']),int(r['cols'])) and hashlib.sha256(v.tobytes()).hexdigest()==r['raw_float64_le_sha256'])
    check('all radiometric reads contain exactly one stored cell',all(r['rows']==r['cols']=='1' for r in win if r['method'] in ['Sen2Cor','ACOLITE']))
    check('all QA windows bounded to <=9 cells; missing QA not concealed',max(int(r['rows'])*int(r['cols']) for r in win)<=9 and all(r['status'].startswith('raw_codes_over_stored_cell_footprint') for r in qa))
    check('actual QUALIT codes zero and DETFOO nonzero; operational SCL limitation remains',all(set(json.loads(r['cell_counts_json']))=={'0'} for r in qa if r['kind']=='QUALIT') and all('0' not in json.loads(r['cell_counts_json']) for r in qa if r['kind']=='DETFOO') and any(r['SCL_cloud_shadow_or_invalid_flag']=='True' for r in sat))
    check('every flagged value explicitly retained and held',all(r['reflectance']!='NA' and r['validation_eligible']=='False' and 'operational_SCL_flag:' in r['hold_reason'] for r in sat if r['SCL_cloud_shadow_or_invalid_flag']=='True'))
    xy=m.run(['gdaltransform','-s_srs','EPSG:32628','-t_srs','EPSG:4326'],'\n'.join(r['x_32628_m']+' '+r['y_32628_m'] for r in st)).splitlines()
    check('coordinate axis order roundtrip within 1e-9 degrees',all(abs(float(line.split()[0])-float(r['longitude']))<1e-9 and abs(float(line.split()[1])-float(r['latitude']))<1e-9 for line,r in zip(xy,st)))
    # Adversarial scientific method tests: missingness and support must survive.
    wl=np.arange(400.,901.); curve=np.array([[449.,0.],[450.,1.],[550.,1.],[551.,0.]])
    check('constant reflectance retained by convolution',abs(m.convolve(wl,np.full(wl.shape,.25),curve)[0]-.25)<1e-14)
    y=np.full(wl.shape,.25); y[100]=np.nan
    check('missing ASD in positive response rejected',m.convolve(wl,y,curve)[1]=='missing_positive_response_interval')
    check('positive response outside ASD never extrapolated',m.convolve(wl,np.full(wl.shape,.25),np.array([[350.,0.],[399.,1.],[401.,0.]]))[0] is None)
    before=m.js(P/'provenance/ctr42_preflight.json')
    for n,h in before['prior_tracked_ctr27_sha256'].items(): check('baseline CTR27 file preserved '+n,m.sha(ROOT/n)==h)
    for n,h in before['unrelated_ctr39_sha256'].items(): check('unrelated CTR39 file preserved '+n,m.sha(ROOT/n)==h)
    tracked=subprocess.check_output(['git','diff','--name-only','HEAD'],text=True,cwd=ROOT).strip()
    check('no tracked baseline modifications in any investigation or protected path',tracked=='')
    summary=dict(status='pass',check_count=len(checks),checks=checks,independent_point_reads=len(sat),independent_quadratures=208,scientific_review='author QA only; independent Thomas/Karl review and PI decision remain required',script_sha256=m.sha(Path(__file__)),output_sha256={str(p.relative_to(P)):m.sha(p) for p in sorted((P/'tables').glob('ctr42_*.csv'))},QA_flagged_station_ids=sorted({r['station_id'] for r in sat if r['SCL_cloud_shadow_or_invalid_flag']=='True'}))
    m.dump('provenance/ctr42_validation.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k not in ['checks','output_sha256']},indent=2))
if __name__=='__main__': main()
