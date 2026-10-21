#!/usr/bin/env python3
"""PI-authorized descriptive expansion; no admitted ASD validation or accuracy inference."""
import csv, datetime, hashlib, io, json, math, subprocess, sys, tempfile
from pathlib import Path
import numpy as np
import audit as a
P=a.OUT; ROOT=a.ROOT
sys.path.insert(0,str(ROOT/'scripts'))
from figure_io import write_generated_bytes

def rows(path):
    with path.open() as f: return list(csv.DictReader(f))
def summary(values):
    x=np.asarray(values,dtype=float)
    assert len(x)>1 and np.isfinite(x).all()
    q=np.quantile(x,[.25,.5,.75],method='linear')
    return dict(n=len(x),mean=float(x.mean()),SD=float(x.std(ddof=1)),Q1=float(q[0]),median=float(q[1]),Q3=float(q[2]),minimum=float(x.min()),maximum=float(x.max()))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    before=a.snapshot();start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    st=rows(P/'tables/station_crosswalk.csv'); joins=rows(P/'tables/aoi_station_join.csv')
    inputs=[r for r in rows(P/'tables/aoi_input_inventory.csv') if r['used']=='True']
    run=json.loads((P/'provenance/run.json').read_text())
    asdp=ROOT/st[0]['asd_path']; assert sha(asdp)==next(x['sha256'] for x in run['inputs'] if x['path']==st[0]['asd_path'])
    names=asdp.open().readline().split(); arr=np.loadtxt(asdp,skiprows=1)
    assert np.array_equal(arr[:,0],np.arange(400,901))
    fs=[]
    for s in st:
        vals=arr[:,names.index(s['asd_column_raw'])]
        fs.append(dict(station_id=s['station_id'],ASD_column=s['asd_column_raw'],role=s['role'],label_literal=s['target_class_raw'],wavelength_min_nm=400,wavelength_max_nm=900,**summary(vals)))
    a.writecsv('tables/field_spectral_summary.csv',fs)
    # Source GPS transform check; saved points are never relocated to a named AOI.
    transformed=a.run(['gdaltransform','-s_srs','EPSG:4326','-t_srs','EPSG:32628'], ''.join(s['lon_raw']+' '+s['lat_raw']+' 0\n' for s in st)).splitlines()
    coords={s['station_id']:tuple(map(float,line.split()[:2])) for s,line in zip(st,transformed)}
    for j in joins:
        assert math.dist(coords[j['station_id']],(float(j['station_x_m']),float(j['station_y_m'])))<1e-6
    data={}
    for i in inputs:
        q=ROOT/i['path']; assert sha(q)==i['sha256']; rs=rows(q)
        data[q.parent.name]={(r['AOI'],r['pixel_id']):r for r in rs}
    assert data['Sen2Cor'].keys()==data['ACOLITE'].keys() and len(data['Sen2Cor'])==1463
    distributions=[]; diffs=[]; exclusions=[]
    for group in ['Arel','Iwik']:
        keys=[k for k in data['Sen2Cor'] if k[0]==group]
        assert len(keys)==(730 if group=='Arel' else 733)
        for band in ['B02','B03','B04']:
            vals={m:np.array([float(data[m][k][band]) for k in keys]) for m in data}
            # Already-decoded CSV values: do not apply L2A scale/offset again.
            masks={m:np.isfinite(v) & (~np.isin(v,[-.1,6.4535]) if m=='Sen2Cor' else True) for m,v in vals.items()}
            ok=masks['Sen2Cor'] & masks['ACOLITE']
            exclusions.append(dict(AOI=group,band=band,total_pairs=len(keys),nonfinite_L2A=int((~np.isfinite(vals['Sen2Cor'])).sum()),nonfinite_ACOLITE=int((~np.isfinite(vals['ACOLITE'])).sum()),decoded_L2A_special=int(np.isin(vals['Sen2Cor'],[-.1,6.4535]).sum()),retained_pairs=int(ok.sum()),excluded_pairs=int((~ok).sum()),QA='not validated'))
            for k in keys: assert data['Sen2Cor'][k]['x']==data['ACOLITE'][k]['x'] and data['Sen2Cor'][k]['y']==data['ACOLITE'][k]['y']
            for m,v in vals.items():
                distributions.append(dict(AOI=group,band=band,method='operational L2A' if m=='Sen2Cor' else 'ACOLITE DSF',**summary(v[ok])))
            diffs.append(dict(AOI=group,band=band,sign='ACOLITE minus operational L2A',**summary(vals['ACOLITE'][ok]-vals['Sen2Cor'][ok])))
    a.writecsv('tables/aoi_descriptive.csv',distributions);a.writecsv('tables/aoi_paired_differences.csv',diffs);a.writecsv('tables/descriptive_exclusions.csv',exclusions)
    feasible=[dict(quantity=k,count=v,denominator=d) for k,v,d in [
        ('date-eligible field spectra',15,'15 March27 station-average columns'),('primary candidate stations',8,'15 eligible stations'),('supplementary candidate stations',7,'15 eligible stations'),('paired AOI cells',1463,'1463 qualified (AOI,pixel_id) keys'),('Arel paired cells',730,'1463 paired AOI cells'),('Iwik paired cells',733,'1463 paired AOI cells'),('station/AOI containing-cell joins',0,'15 field stations'),('admitted ASD-validation band-pairs',0,'165 held candidate station-band rows; not observed n'),('held candidate ledger rows',165,'15 stations x 11 bands; design count only'),('possible primary band-pairs before holds',24,'8 stations x 3 bands; design maximum only')]]
    a.writecsv('tables/feasibility_counts.csv',feasible)
    # Save only plotting geometry derived from the existing source-preserving audit.
    vectors=json.loads((P/'outputs/vector_records.json').read_text())['TimeSeries_Polygons_Matchup.shp']
    vertices=[dict(AOI=f['properties']['AOI'],vertex=i,x=xy[0],y=xy[1]) for f in vectors['features'] for i,xy in enumerate(f['geometry']['coordinates'][0])]
    a.writecsv('tables/aoi_plot_vertices.csv',vertices)
    with tempfile.TemporaryDirectory(prefix='ctr28-figures-') as scratch:
        subprocess.run([str(ROOT/'scripts/project-env.sh'),'Rscript',str(P/'scripts/descriptive_figures.R'),scratch],cwd=ROOT,check=True)
        for q in sorted(Path(scratch).iterdir()): write_generated_bytes(P,q.name,q.read_bytes())
    assert before==a.snapshot(),'raw input stat tuples changed'
    evidence=dict(started_utc=start,ended_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),base_commit=a.run(['git','rev-parse','HEAD']).strip(),PI_scope_comment='cd589b22-be5b-45ed-9df8-accc7ff5949e',review_revision='41b37e06-40fd-471b-b7de-ef3e2d339803',raw_stat_unchanged=True,raw_files=len(before),raw_stat_snapshot_sha256=hashlib.sha256(json.dumps(before,sort_keys=True).encode()).hexdigest(),used_input_hashes=[dict(path=i['path'],sha256=i['sha256']) for i in inputs]+[dict(path=st[0]['asd_path'],sha256=sha(asdp))],quantile='NumPy linear = R type 7; SD sample ddof=1',exclusion='paired complete finite B02-B04 per band; decoded L2A special values -0.1 and 6.4535 excluded; no range clipping or ecological/QA filtering',source_encoding='CSV already decoded; operational L2A native DN maps to (DN-1000)/10000 excluding 0,65535; ACOLITE Float32 rhos direct; no second scale/offset',station_transform='gdaltransform EPSG:4326 to EPSG:32628 agrees with all 15 saved points within 1e-6 m; no location shifts',resampling='none; paired identical supplied 10m cell centres; actual effective support/QA remain unverified',new_raster_reads=0,field_summary='501 wavelength channels per station; SD and quantiles describe spectral variation, not replicate variability',AOI_summary='spatially dependent supplied pixel records; no uncertainty intervals, p-values or correction ranking',locks={n:sha(ROOT/n) for n in ['uv.lock','renv.lock']},scripts={str(q.relative_to(P)):sha(q) for q in [P/'scripts/descriptive.py',P/'scripts/descriptive_figures.R']},ASD_validation_metrics='not estimable: zero admitted field matchups',independent_review='pending',PI_scientific_approval='pending')
    a.dump('provenance/descriptive_run.json',evidence)
    print(json.dumps(dict(field_spectra=len(fs),AOI_distribution_rows=len(distributions),paired_difference_rows=len(diffs),excluded_band_pairs=sum(r['excluded_pairs'] for r in exclusions),raw_stat_unchanged=True)))
if __name__=='__main__': main()
