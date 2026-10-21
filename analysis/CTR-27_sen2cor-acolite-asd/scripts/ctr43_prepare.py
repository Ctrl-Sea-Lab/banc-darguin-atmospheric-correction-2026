#!/usr/bin/env python3
"""Verify frozen CTR42 handoff and export March7 contextual spectra, not accuracy.
Run using project .venv/bin/python. Writes only CTR27 ctr43_* outputs.
No raw writes, raster extraction, model fitting, inference or figure/report edits.
"""
import csv, hashlib, itertools, json, math, platform, struct, subprocess, sys
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET
import ctr42_extract as source_reader  # workbook parsing only; no extraction/convolution
P = Path(__file__).resolve().parents[1]
ROOT = P.parents[1]
INPUT_COMMIT = '51eeaf86353e895d18ee8f0747642d45d612909e'
BANDS = ['B01','B02','B03','B04','B05','B06','B07','B08','B8A']
METHODS = ['Sen2Cor','ACOLITE']
ROLES = ['v4_primary','v5_sensitivity']
CHECKS = []
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(4194304),b''): h.update(b)
    return h.hexdigest()
def read(n):
    with (P/'tables'/n).open(newline='') as f: return list(csv.DictReader(f))
def js(n): return json.loads((P/n).read_text())
def dump(n,x): (P/n).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def check(n,ok):
    if not ok:
        dump('provenance/ctr43_input_audit.json',dict(status='failed',failure=n,passed=CHECKS))
        raise AssertionError(n)
    CHECKS.append(n)
def table(n,rr):
    with (P/'tables'/n).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rr[0]),lineterminator='\n');w.writeheader()
        w.writerows({k:'NA' if v is None else v for k,v in r.items()} for r in rr)
def number(v):
    try: return float(v) if math.isfinite(float(v)) else None
    except (ValueError,TypeError): return None
def yes(v): return v=='True'
def common(a,b,c): return all(number(x) is not None for x in [a,b,c])
def metrics(e):
    return (math.fsum(e)/len(e),math.fsum(abs(v) for v in e)/len(e),math.sqrt(math.fsum(v*v for v in e)/len(e))) if e else (None,None,None)
def key(r): return r['station_id'],r['band_id']
def xml(p):
    d={}
    for e in ET.parse(p).iter():
        if not len(e) and e.text: d.setdefault(e.tag.split('}')[-1],[]).append(e.text.strip())
    return d

def audit():
    # Bind every handoff byte to Roger's exact commit before using saved QA.
    names=subprocess.check_output(['git','ls-tree','-r','--name-only',INPUT_COMMIT,'--',str(P.relative_to(ROOT))],cwd=ROOT,text=True).splitlines()
    frozen={}
    for n in names:
        if Path(n).name.startswith('ctr42_'):
            expected=hashlib.sha256(subprocess.check_output(['git','show',INPUT_COMMIT+':'+n],cwd=ROOT)).hexdigest()
            check('exact handoff '+n,sha(ROOT/n)==expected); frozen[n]=expected
    check('input revision is ancestor',subprocess.run(['git','merge-base','--is-ancestor',INPUT_COMMIT,'HEAD'],cwd=ROOT).returncode==0)
    sat,refs,stations,coverage,sources,windows,qa,ledger,bc=[read('ctr42_'+n+'.csv') for n in ['satellite','references','stations','srf_coverage','sources','windows','qa','availability','band_contract']]
    for s in sources: check('live source SHA256 '+s['path'],sha(ROOT/s['path'])==s['sha256'])
    src={s['path']:s for s in sources}
    author=js('provenance/ctr42_validation.json')
    check('saved author interface checks passed',author['status']=='pass' and author['independent_point_reads']==234 and author['independent_quadratures']==208)
    for n,h in author['output_sha256'].items(): check('author checked table '+n,sha(P/n)==h)
    ids={s['station_id'] for s in stations}; expected=set(itertools.product(ids,BANDS))
    check('13 specified stations',ids=={'AC01','AC02','AC05','AC06','AC07','AC08'}|{'D06_'+x for x in 'ABCDEFG'} and len(stations)==13)
    check('two literal exclusions', {r['station_id']:r['class_literal'] for r in read('ctr42_exclusions.csv')}=={'AC03':'mbp_mud','AC04':'mpb_mud'})
    check('satellite unique complete keys',len(sat)==234 and {(r['station_id'],r['band_id'],r['correction']) for r in sat}=={(*k,m) for k in expected for m in METHODS})
    check('reference unique complete keys',len(refs)==234 and {(r['station_id'],r['band_id'],r['SRF_role']) for r in refs}=={(*k,m) for k in expected for m in ROLES})
    check('ledger unique complete keys',len(ledger)==117 and {key(r) for r in ledger}==expected)
    contract={r['band_id']:r for r in bc}; smap={s['station_id']:s for s in stations}
    headers=js('outputs/ctr42_raster_headers.json')
    tilepath=next(ROOT/s['path'] for s in sources if s['role']=='Sen2Cor tile metadata')
    prodpath=next(ROOT/s['path'] for s in sources if s['role']=='Sen2Cor product metadata')
    tile,prod=xml(tilepath),xml(prodpath)
    check('live metadata scale and identity',prod['BOA_QUANTIFICATION_VALUE']==['10000'] and prod['BOA_ADD_OFFSET']==['-1000']*13 and tile['SENSING_TIME']==['2026-03-07T11:45:54.425534Z'] and tile['L1C_TILE_ID']==['S2B_OPER_MSI_L1C_TL_2BPS_20260307T153536_A047010_T28QCH_N05.12'])
    for b in bc:
        h=headers[b['acolite_path']]; meta=h['metadata']['']; bm=h['bands'][0]['metadata']['']
        check('same acquisition, rhos and dimensionless units '+b['band_id'],datetime.fromisoformat(meta['NC_GLOBAL#isodate'])==datetime.fromisoformat(tile['SENSING_TIME'][0].replace('Z','+00:00')) and meta['NC_GLOBAL#granule']=='L1C_T28QCH_A047010_20260307T114112' and bm['NETCDF_VARNAME']==b['acolite_variable'] and bm['standard_name']=='surface_bidirectional_reflectance' and h['bands'][0]['unit']=='1')
    wmap={(r['station_id'],r['band_id'],r['method']):r for r in windows if r['method'] in METHODS}
    qmap={(r['station_id'],r['band_id'],r['correction']):r for r in qa if r['kind']=='SCL'}
    for r in sat:
        k=(*key(r),r['correction']); w=wmap[k]; st=smap[r['station_id']]; raw=number(r['raw_value'])
        value=(raw-1000)/10000 if r['correction']=='Sen2Cor' else raw
        check('saved cell, decode and hash '+str(k),w['rows']==w['cols']=='1' and json.loads(w['values_json'])==[[raw]] and hashlib.sha256(struct.pack('<d',raw)).hexdigest()==w['raw_float64_le_sha256'] and raw not in ([0,65535] if r['correction']=='Sen2Cor' else []) and abs(value-float(r['reflectance']))<1e-14 and r['source_sha256']==src[r['source_path']]['sha256'])
        g=headers[r['source_path']]['geoTransform']; x,y=float(st['x_32628_m']),float(st['y_32628_m']); col,row=math.floor((x-g[0])/g[1]),math.floor((y-g[3])/g[5])
        check('containing cell indices '+str(k),col==int(r['col_0based'])==int(w['col_start']) and row==int(r['row_0based'])==int(w['row_start']))
        counts=json.loads(qmap[k]['cell_counts_json']); bad=bool(set(counts)&{'0','1','2','3','8','9','10','11'})
        check('QA and hold '+str(k),counts==json.loads(r['SCL_over_stored_footprint_counts_json']) and bad==yes(r['SCL_cloud_shadow_or_invalid_flag']) and r['validation_eligible']=='False' and 'field_20_days_after_satellite' in r['hold_reason'] and r['field_date']=='2026-03-27' and r['field_minus_satellite_days']=='20')
    # Independently sum original 1nm SRF knots with math.fsum. No production convolution.
    with (ROOT/refs[0]['ASD_source']).open() as f:
        names=f.readline().split(); data=[list(map(float,line.split())) for line in f if line.strip()]
    check('measured ASD grid exactly 400..900', [r[0] for r in data]==list(range(400,901)))
    curves={role:source_reader.curves(ROOT/next(r['SRF_file'] for r in refs if r['SRF_role']==role)) for role in ROLES}
    covmap={(r['band_id'],r['SRF_role']):r for r in coverage}
    old={(r['station_id'],r['band_id'],r['SRF_role']):r for r in read('ctr34_convolved_references.csv')}
    for r in refs:
        k=(*key(r),r['SRF_role']); cv=curves[r['SRF_role']][r['band_id']]['curve'].tolist(); c=covmap[(r['band_id'],r['SRF_role'])]
        check('SRF grid and nonnegative response '+str(k),all(cv[i+1][0]-cv[i][0]==1 for i in range(len(cv)-1)) and all(y>=0 for x,y in cv))
        den=math.fsum((a[1]+b[1])*(b[0]-a[0])/2 for a,b in zip(cv,cv[1:])); inside=[(x,y) for x,y in cv if 400<=x<=900]
        fraction=math.fsum((a[1]+b[1])*(b[0]-a[0])/2 for a,b in zip(inside,inside[1:]))/den
        supported=fraction>=.999 and all(400<=x<=900 for x,y in cv if y>0)
        check('coverage and support '+str(k),abs(fraction-float(r['response_fraction_inside_ASD']))<2e-14 and abs(fraction-float(c['response_fraction_inside_ASD']))<2e-14 and float(c['coverage_threshold'])==.999 and supported==(r['reference_status']=='pass'))
        if supported:
            col=names.index(r['ASD_column']); yy={d[0]:d[col] for d in data}; pp=[(x,yy[x]*y if y>0 else 0) for x,y in cv]
            num=math.fsum((a[1]+b[1])*(b[0]-a[0])/2 for a,b in zip(pp,pp[1:]))
            check('independent ASD integral '+str(k),abs(num/den-float(r['ASD_reflectance']))<2e-14 and abs(num-float(r['response_weighted_numerator']))<2e-12 and abs(den-float(r['response_denominator']))<2e-12)
        else: check('unsupported ASD remains NA '+str(k),r['band_id']=='B08' and r['ASD_reflectance']==r['response_weighted_numerator']=='NA')
        check('reference source and identity '+str(k),r['ASD_column']==smap[r['station_id']]['ASD_column'] and r['ASD_sha256']==src[r['ASD_source']]['sha256'] and r['SRF_sha256']==src[r['SRF_file']]['sha256'] and r['ASD_field_date']=='2026-03-27')
        if k in old: check('historical reference reused '+str(k),abs(float(old[k]['convolved_reflectance'])-float(r['ASD_reflectance']))<1e-14)
    check('negative remains finite; missing common rows excluded',common(-.1,.2,.3) and not common('NA',.2,.3) and not common(.1,'nan',.3))
    check('metric cancellation and empty fixture',metrics([-2,1,4])==(1,7/3,math.sqrt(7)) and metrics([])==(None,None,None))
    before=js('provenance/ctr42_preflight.json')
    for group in ['prior_tracked_ctr27_sha256','unrelated_ctr39_sha256']:
        for n,h in before[group].items(): check('preserved '+n,sha(ROOT/n)==h)
    audit_out=dict(status='pass',input_commit=INPUT_COMMIT,check_count=len(CHECKS),checks=CHECKS,input_sha256=frozen,full_source_hashes_verified=len(sources),independent_ASD_quadratures=208,raster_QA='reused exact hashed CTR42 GDAL rereads; independently checked stored cell geometry, raw window hashes and decoding; no re-extraction',scientific_status='numerical verification; independent final scientific review still required')
    dump('provenance/ctr43_input_audit.json',audit_out)
    return sat,refs,stations,contract,ledger

def main():
    sat,refs,stations,bc,ledger=audit()
    ss={(*key(r),r['correction']):r for r in sat}; rr={(*key(r),r['SRF_role']):r for r in refs}; ll={key(r):r for r in ledger}
    masks=[]; spectral=[]; comparisons=[]; summary=[]; availability=[]
    for role in ROLES:
        for st in stations:
            sid=st['station_id']; station_masks=[]
            for i,b in enumerate(BANDS,1):
                s,a=ss[(sid,b,'Sen2Cor')],ss[(sid,b,'ACOLITE')]; ref=rr[(sid,b,role)]
                finite=common(s['reflectance'],a['reflectance'],ref['ASD_reflectance']); flag=any(yes(x['SCL_cloud_shadow_or_invalid_flag']) for x in [s,a])
                missing=';'.join([m+':'+x['availability_reason'] for m,x in [('Sen2Cor',s),('ACOLITE',a)] if number(x['reflectance']) is None]+['ASD:'+ref['reference_status']]*int(number(ref['ASD_reflectance']) is None)) or 'none'
                row=dict(station_id=sid,class_literal=st['class_literal'],population=st['role'],band_id=b,band_order=i,SRF_role=role,plot_wavelength_nm=float(bc[b]['acolite_wavelength_nm']),wavelength_convention='ACOLITE metadata S2B band wavelength used for common display positions; no spectral interpolation',Sen2Cor_reflectance=number(s['reflectance']),ACOLITE_reflectance=number(a['reflectance']),ASD_reflectance=number(ref['ASD_reflectance']),Sen2Cor_available=number(s['reflectance']) is not None,ACOLITE_available=number(a['reflectance']) is not None,ASD_supported=number(ref['ASD_reflectance']) is not None,common_finite_triple=finite,missing_reason=missing,Sen2Cor_SCL_flag=yes(s['SCL_cloud_shadow_or_invalid_flag']),ACOLITE_SCL_flag=yes(a['SCL_cloud_shadow_or_invalid_flag']),either_SCL_flag=flag,common_finite_without_operational_SCL_flag=finite and not flag,ASD_reference_status=ref['reference_status'],ASD_response_coverage=float(ref['response_fraction_inside_ASD']),satellite_date='2026-03-07',ASD_date='2026-03-27',field_minus_satellite_days=20,unit='1',validation_eligible=False,hold_reason=s['hold_reason']+';'+a['hold_reason'],prior_physical_hold_reason=s['prior_physical_hold_reason'])
                check('ledger finite agreement '+sid+b+role,finite==yes(ll[(sid,b)]['common_finite_triple_'+role[:2]]))
                masks.append(row);station_masks.append(row)
                for method,x in [('Sen2Cor',s),('ACOLITE',a)]:
                    comparisons.append(dict(**{k:row[k] for k in ['station_id','class_literal','population','band_id','band_order','SRF_role','common_finite_triple','missing_reason','satellite_date','ASD_date','validation_eligible']},correction=method,satellite_reflectance=number(x['reflectance']),ASD_reflectance=row['ASD_reflectance'],signed_difference=float(x['reflectance'])-row['ASD_reflectance'] if finite else None,SCL_flag=yes(x['SCL_cloud_shadow_or_invalid_flag']),quality_disposition=x['quality_disposition'],hold_reason=x['hold_reason'],unit='1'))
            selected=[r for r in station_masks if r['common_finite_triple']]
            signature=hashlib.sha256('\n'.join(sid+'|'+r['band_id'] for r in selected).encode()).hexdigest()
            for method in METHODS:
                err=[r[method+'_reflectance']-r['ASD_reflectance'] for r in selected]; bias,mae,rmse=metrics(err)
                summary.append(dict(station_id=sid,class_literal=st['class_literal'],population=st['role'],SRF_role=role,correction=method,n_expected_bands=9,n_paired_bands=len(selected),bands=';'.join(r['band_id'] for r in selected) or 'none',pair_keys_sha256=signature,missing_band_reasons=';'.join(r['band_id']+':'+r['missing_reason'] for r in station_masks if not r['common_finite_triple']) or 'none',n_paired_bands_SCL_flagged=sum(r[method+'_SCL_flag'] for r in selected),n_paired_bands_either_SCL_flagged=sum(r['either_SCL_flag'] for r in selected),bias=bias,MAE=mae,RMSE=rmse,unit='1',band_weight=1/len(selected) if selected else None,satellite_date='2026-03-07',ASD_date='2026-03-27',status='EXPLORATORY_CROSS_DATE_SPECTRAL_DISCREPANCY',validation_eligible=False,inference='none; bands and nearby stations not independent; no accuracy ranking'))
            for series in ['ASD',*METHODS]:
                segment=0;previous=False
                for r in station_masks:
                    val=r[series+'_reflectance']; available=val is not None
                    if available and not previous: segment+=1
                    previous=available
                    origin=rr[(sid,r['band_id'],role)] if series=='ASD' else ss[(sid,r['band_id'],series)]
                    spectral.append(dict(**{k:r[k] for k in ['station_id','class_literal','population','band_id','band_order','SRF_role','plot_wavelength_nm','wavelength_convention','common_finite_triple','satellite_date','ASD_date','validation_eligible','unit']},series=series,reflectance=val,available=available,segment_id=segment if available else None,observation_date='2026-03-27' if series=='ASD' else '2026-03-07',availability_reason=origin['reference_status'] if series=='ASD' else origin['availability_reason'],SCL_flag=None if series=='ASD' else yes(origin['SCL_cloud_shadow_or_invalid_flag']),SCL_labels='not_applicable_field_reference' if series=='ASD' else origin['SCL_labels'],hold_reason=r['hold_reason'],source_path=origin['ASD_source'] if series=='ASD' else origin['source_path'],source_sha256=origin['ASD_sha256'] if series=='ASD' else origin['source_sha256'],stored_resolution_m=None if series=='ASD' else float(origin['stored_resolution_m']),SRF_sha256=origin['SRF_sha256'] if series=='ASD' else None))
        for b in BANDS:
            z=[r for r in masks if r['SRF_role']==role and r['band_id']==b]
            availability.append(dict(SRF_role=role,band_id=b,n_retained_stations=13,Sen2Cor_finite=sum(r['Sen2Cor_available'] for r in z),ACOLITE_finite=sum(r['ACOLITE_available'] for r in z),ASD_supported=sum(r['ASD_supported'] for r in z),common_finite_triples=sum(r['common_finite_triple'] for r in z),Sen2Cor_SCL_flagged=sum(r['Sen2Cor_SCL_flag'] for r in z),ACOLITE_SCL_flagged=sum(r['ACOLITE_SCL_flag'] for r in z),common_finite_without_operational_SCL_flag=sum(r['common_finite_without_operational_SCL_flag'] for r in z),ASD_reason=z[0]['ASD_reference_status'],response_coverage=z[0]['ASD_response_coverage'],validation_eligible_pairs=0))
    for n,rows in [('pair_masks',masks),('spectral_long',spectral),('comparison_long',comparisons),('station_metrics',summary),('band_availability',availability)]: table('ctr43_'+n+'.csv',rows)
    accounting=[dict(station_id=s['station_id'],class_literal=s['class_literal'],disposition='retained',population=s['role'],satellite_rows=18,ASD_supported_bands_per_role=8,ASD_missing_bands='B08',reason='cross_date_and_physical_holds',validation_eligible=False) for s in stations]
    accounting += [dict(station_id=s['station_id'],class_literal=s['class_literal'],disposition='excluded',population='excluded',satellite_rows=0,ASD_supported_bands_per_role=None,ASD_missing_bands=None,reason=s['reason'],validation_eligible=False) for s in read('ctr42_exclusions.csv')]
    table('ctr43_station_accounting.csv',accounting)
    delta=[]
    for sid in [s['station_id'] for s in stations]:
        for b in BANDS:
            v=[number(rr[(sid,b,role)]['ASD_reflectance']) for role in ROLES]
            delta.append(dict(station_id=sid,band_id=b,ASD_v4=v[0],ASD_v5=v[1],v5_minus_v4=v[1]-v[0] if all(x is not None for x in v) else None,unit='1'))
    table('ctr43_srf_sensitivity.csv',delta)
    out=dict(status='pass',input_commit=INPUT_COMMIT,station_count=13,excluded_count=2,requested_bands=BANDS,supported_bands=[b for b in BANDS if b!='B08'],satellite_finite=234,common_triples_per_role=104,eligible_validation_pairs=0,SCL_flagged_satellite_rows=sum(yes(r['SCL_cloud_shadow_or_invalid_flag']) for r in sat),max_abs_SRF_v5_minus_v4=max(abs(r['v5_minus_v4']) for r in delta if r['v5_minus_v4'] is not None),script_sha256=sha(Path(__file__)),input_audit_sha256=sha(P/'provenance/ctr43_input_audit.json'),tables_sha256={p.name:sha(p) for p in sorted((P/'tables').glob('ctr43_*.csv'))},software=dict(python=sys.version,host=platform.node(),numpy=source_reader.np.__version__),no_model_or_random_sampling=True,review='numerical handoff only; Rachel presentation then Karl independent scientific review and PI authority remain')
    dump('provenance/ctr43_computation.json',out)
    print(json.dumps({k:v for k,v in out.items() if k not in ['tables_sha256','software']},indent=2))
if __name__=='__main__': main()
