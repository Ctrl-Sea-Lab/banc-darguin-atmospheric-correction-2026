"""Bounded execution audit. Read scientific inputs/products; write CTR-58 evidence only."""
from pathlib import Path
import argparse, csv, hashlib, json, os, shutil, subprocess, tempfile
import numpy as np

A = Path(__file__).resolve().parents[1]
REPO = A.parents[1]
PREFIX = A.relative_to(REPO).as_posix()+'/'

def rows(p):
    with p.open(newline='') as f: return list(csv.DictReader(f))

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
    return h.hexdigest()

def run(args):
    return subprocess.check_output(list(map(str,args)),text=True,env={**os.environ,'GDAL_PAM_ENABLED':'NO','GDAL_CACHEMAX':'256','OPJ_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'})

def pixel(p,c,r):
    return float(run(['gdal_translate','-q','-of','XYZ','-srcwin',c,r,1,1,p,'/vsistdout/']).split()[-1])

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--products',required=True,type=Path)
    ap.add_argument('--env-root',required=True,type=Path)
    args=ap.parse_args(); products=args.products.resolve(); envroot=args.env_root.resolve()
    for f in ['uv.lock','renv.lock']:
        assert (REPO/f).read_bytes()==(envroot/f).read_bytes(),f
    evidence={'writer_revision':'f79b98cdd810c2ffada1479dd0bddc3d34e22341','products':str(products),'environment_root':str(envroot),'lockfiles':{f:sha(REPO/f) for f in ['uv.lock','renv.lock']},'verification_extent':'Full stored-raster hashes and metadata; bounded raw/source/temporal pixel checks; full compact model rerun. No raster-processing or full raw-input hash rerun.','scientific_review':'pending CTR-59','pi_approval':'pending'}
    # Immutable source table/figure evidence, checked against Git and disk.
    consumed=json.loads((A/'provenance/ctr57_assembly.json').read_text())['consumed_files']
    for r in consumed:
        assert sha(A/r['path'])==r['sha256'],r['path']
        obj=r['source_revision']+':'+PREFIX+r['path']
        if subprocess.run(['git','cat-file','-e',obj],cwd=REPO,stderr=subprocess.DEVNULL).returncode==0:
            gitbytes=subprocess.check_output(['git','show',obj],cwd=REPO)
            assert hashlib.sha256(gitbytes).hexdigest()==r['sha256']
    evidence['upstream_consumed_files_checked']=len(consumed)
    manifest={r['path']:r for r in rows(A/'provenance/output_hashes.csv')}
    checked=[]
    raster_files=sorted((products/'outputs').rglob('*.tif'))
    assert len(raster_files)==113,len(raster_files)
    for p in raster_files:
        rel=p.relative_to(products).as_posix(); h=sha(p)
        assert h==manifest[rel]['sha256'],rel
        j=json.loads(run(['gdalinfo','-json',p])); b=j['bands'][0]
        assert j['size']==[3763,1974] and j['geoTransform']==[334050,10,0,2209980,0,-10]
        assert '32628' in j['coordinateSystem']['wkt']
        assert b['type'] in ['Float32','Byte']
        assert b['noDataValue']==(-9999 if b['type']=='Float32' else 255)
        checked.append({'path':rel,'bytes':p.stat().st_size,'sha256':h,'epsg':32628,'type':b['type'],'nodata':b['noDataValue']})
    evidence['scientific_rasters']=checked
    print('PASS: 113 raster hashes, dimensions, CRS and nodata',flush=True)
    inputs=rows(A/'provenance/input_hashes.csv'); metadata=[]
    for r in inputs:
        p=Path(r['path']); st=p.stat()
        assert st.st_size==int(r['bytes']) and st.st_mtime_ns==int(r['mtime_ns']),r['path']
        metadata.append({'path':r['path'],'size_and_mtime_match':True})
    evidence['input_metadata_checked']=metadata
    pairs=json.loads((A/'outputs/pairs.json').read_text()); sources=[]; rawhashes={}
    for r in rows(A/'tables/source_pixel_checks.csv'):
        pair=next(p for p in pairs if p['date']==r['date']); band=r['band']; c=int(r['col']); y=int(r['row'])
        ac=Path(pair['acolite'][band]); av=pixel(ac,c,y)
        dn=pixel(pair['sen2cor']['bands'][band],c+pair['sen2cor_window'][0],y+pair['sen2cor_window'][1])
        value=av-(dn+pair['sen2cor']['offsets'][band])/pair['sen2cor']['quantification']
        stored=pixel(products/'outputs/paired_differences'/f"{pair['id']}_{band}_delta.tif",c,y)
        assert abs(value-stored)<2e-7 and abs(value-float(r['expected_delta']))<2e-7
        # Three dates, one raw band each: bounded checksum verification.
        if band=='B2':
            h=sha(ac); ref=next(z for z in inputs if z['path']==str(ac)); assert h==ref['sha256'];rawhashes[str(ac)]=h
        sources.append({'date':r['date'],'band':band,'absolute_error':abs(value-stored)})
    evidence['source_pixels']=sources; evidence['raw_files_rehashed']=rawhashes
    temporal=[]
    for band in ['B2','B3','B4','B8']:
        previous=rows(A/'tables/temporal_pixel_checks.csv')
        point=next(r for r in previous if r['band']==band and r['statistic']=='n' and float(r['expected'])>=2)
        c=int(point['col']);y=int(point['row']); values=[]
        for p in pairs:
            v=pixel(products/'outputs/paired_differences'/f"{p['id']}_{band}_delta.tif",c,y)
            if v!=-9999 and np.isfinite(v): values.append(v)
        for stat,expected in [('n',len(values)),('median',float(np.median(values))),('sd',float(np.std(values,ddof=1)))]:
            actual=pixel(products/'outputs/temporal'/f'{band}_{stat}.tif',c,y)
            assert abs(actual-expected)<2e-7,(band,stat,actual,expected)
            temporal.append({'band':band,'row':y,'col':c,'statistic':stat,'n':len(values),'expected':expected,'actual':actual,'absolute_error':abs(actual-expected)})
    evidence['temporal_pixels']=temporal
    print('PASS: 142 raw file sizes/mtimes, 3 raw checksums, 12 source pixels, 12 temporal statistics from all 22 dates',flush=True)
    # Verify reported display saturation using all finite temporal SD pixels.
    saturation=[]
    with tempfile.TemporaryDirectory(prefix='ctr58-audit-',dir='/tmp') as tmp:
        tmp=Path(tmp)
        for b in ['B2','B3','B4','B8']:
            out=tmp/(b+'.bin');run(['gdal_translate','-q','-of','ENVI','-ot','Float32',products/'outputs/temporal'/f'{b}_sd.tif',out])
            x=np.fromfile(out,dtype='<f4');v=x[(x!=-9999)&np.isfinite(x)]
            ref=next(r for r in rows(A/'tables/display_limits_v2.csv') if r['band']==b and r['statistic']=='sd')
            frac=float(np.mean(v>.02));assert len(v)==int(ref['n_finite']) and abs(frac-float(ref['fraction_clipped_high']))<1e-14
            saturation.append({'band':b,'finite_pixels':len(v),'fraction_above_0_02':frac})
        evidence['sd_saturation']=saturation
        # Run original compact models in scratch, preserving author's results.
        for d in ['tables','outputs','provenance','figures/generated']: (tmp/d).mkdir(parents=True,exist_ok=True)
        shutil.copy2(A/'tables/date_band_summary.csv',tmp/'tables/date_band_summary.csv')
        log=run([envroot/'scripts/project-env.sh','Rscript',A/'scripts/ctr56_models.R',tmp,tmp/'figures/generated'])
        (A/'provenance/ctr58_model_rerun.txt').write_text(log)
        model_check=run([envroot/'scripts/project-env.sh','Rscript',A/'scripts/ctr56_check_outputs.R',tmp])
        (A/'provenance/ctr58_model_checks.txt').write_text(model_check)
        comparisons=[]
        for p in sorted((tmp/'tables').glob('ctr56_*.csv')):
            original=rows(A/'tables'/p.name);new=rows(p)
            assert len(original)==len(new) and original[0].keys()==new[0].keys(),p.name
            maxerror=0
            for o,n in zip(original,new):
                for k in o:
                    try: a=float(o[k]);b=float(n[k])
                    except ValueError: assert o[k]==n[k],(p.name,k,o[k],n[k]);continue
                    assert np.isclose(a,b,rtol=1e-8,atol=1e-10,equal_nan=True),(p.name,k,a,b)
                    if np.isfinite(a) and np.isfinite(b):maxerror=max(maxerror,abs(a-b))
            comparisons.append({'path':'tables/'+p.name,'rows':len(new),'max_absolute_numeric_error':maxerror})
        evidence['model_rerun_tables']=comparisons
        evidence['model_check']=model_check
    # Check exact anchors, panel extent/aspect and preserved median range.
    anchors=rows(A/'tables/color_anchors_v2.csv')
    assert [(float(r['sd']),r['hex']) for r in anchors]==[(0,'#2166AC'),(.01,'#FFFFFF'),(.02,'#B2182B')]
    geometry=rows(A/'tables/panel_geometry_v2.csv');assert len(geometry)==8
    for r in geometry:
        assert np.isclose(float(r['width_inches'])/float(r['height_inches']),3763/1974)
        assert [float(r[k]) for k in ['xmin','xmax','ymin','ymax']]==[334050,371680,2190240,2209980]
    old=json.loads((A/'provenance/figure.json').read_text());new=json.loads((A/'provenance/figure_v2.json').read_text())
    assert old['limits']['median']==new['median_limit'] and new['sd_upper_extension'] and new['nodata']=='#D9D9D9'
    evidence['presentation']={'anchors':anchors,'panels':geometry,'median_limit':new['median_limit'],'upper_extension':True,'nodata':new['nodata']}
    evidence['status']='pass'
    (A/'provenance/ctr58_validation.json').write_text(json.dumps(evidence,indent=2,allow_nan=False)+'\n')
    print('PASS: compact model rerun and all numeric output tables; SD saturation; exact palette and panel geometry',flush=True)
if __name__=='__main__':main()
