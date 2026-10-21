"""CTR-55 presentation-only revision; reuse immutable temporal GeoTIFFs."""
from common import *
import numpy as np, sys, tempfile
sys.path.insert(0,str(REPO/'scripts'))
from figure_io import generated_figure_path
old=json.loads((A/'provenance/figure.json').read_text())
lim=old['limits']['median']
pairs=json.loads((A/'outputs/pairs.json').read_text()); W,H=pairs[0]['grid']['size']
rasters=[]; audit=[]
with tempfile.TemporaryDirectory(prefix='ctr55-figure-v2-',dir='/tmp') as scratch:
    scratch=Path(scratch)
    for stat in ['median','sd']:
        for b in BANDS:
            source=A/'outputs/temporal'/f'{b}_{stat}.tif'
            before=sha(source)
            run(['gdal_translate','-q','-of','ENVI','-ot','Float32',source,scratch/f'{b}_{stat}.bin'])
            x=np.memmap(scratch/f'{b}_{stat}.bin',dtype='<f4',mode='r+',shape=(H,W))
            meta=info(source); assert meta['size']==[W,H]
            nodata=meta['bands'][0]['noDataValue']
            x[x==nodata]=np.nan; x.flush()
            v=x[np.isfinite(x)]; low=-lim if stat=='median' else 0; high=lim if stat=='median' else .02
            assert v.size and (stat!='sd' or np.min(v)>=0)
            audit.append(dict(band=b,statistic=stat,display_min=low,display_max=high,n_finite=int(v.size),fraction_clipped_low=float(np.mean(v<low)),fraction_clipped_high=float(np.mean(v>high)),full_min=float(v.min()),full_max=float(v.max())))
            assert sha(source)==before
            rasters.append(dict(path=str(source.relative_to(A)),bytes=source.stat().st_size,sha256=before))
    table(A/'tables/display_limits_v2.csv',audit)
    paths=[generated_figure_path(A,'paired_reflectance_maps_v2.'+e) for e in ['png','pdf']]
    preview=generated_figure_path(A,'paired_reflectance_maps_v2_preview.png')
    run(['Rscript','--vanilla',A/'scripts/maps_v2.R',scratch,A,lim,*paths,preview,W,H])
    save(A/'provenance/figure_v2.json',dict(source_scientific_revision='1bbb23b3b94e775a60aa921f8c9c4f86f51926cb',source_head_before_revision='1631082eb8089b2beeaec8a97f6214191373f8e7',input_manifest_sha256=sha(A/'provenance/input_hashes.csv'),raster_hashes=rasters,extent=pairs[0]['grid'],median_limit=lim,median_scale_unchanged=True,sd_anchors={'0':'#2166AC','0.01':'#FFFFFF','0.02':'#B2182B'},sd_upper_extension=True,nodata='#D9D9D9',dimensions_inches=[20,6.1],png_dpi=400,preview_dpi=120,render_sampling='nearest regular display sampling including all four outer edge pixels; whole scientific extent retained; no scientific resampling or raster modification',audit='tables/display_limits_v2.csv',outputs=[dict(path=str(q.relative_to(A)),bytes=q.stat().st_size,sha256=sha(q)) for q in [*paths,preview]]))
print('Presentation revision complete; eight source rasters unchanged.')
