"""Shared row scales, full-value clipping audit, guarded generated output paths."""
from common import *
import numpy as np,sys
sys.path.insert(0,str(REPO/'scripts'))
from figure_io import generated_figure_path
P=json.loads((A/'outputs/pairs.json').read_text());W,H=P[0]['grid']['size']
samples={};audit=[];limits={}
for stat in ['median','sd']:
    samples[stat]=[]
    for b in BANDS:
        x=np.memmap(A/'outputs'/f'{b}_{stat}_display.bin',dtype='<f4',mode='r',shape=(H,W));v=x[::5,::5].ravel();samples[stat].append(v[np.isfinite(v)])
    v=np.concatenate(samples[stat]);limits[stat]=float(np.quantile(np.abs(v) if stat=='median' else v,.98))
for stat in limits:
    for b in BANDS:
        x=np.memmap(A/'outputs'/f'{b}_{stat}_display.bin',dtype='<f4',mode='r',shape=(H,W));v=x[np.isfinite(x)];lim=limits[stat]
        audit.append(dict(band=b,statistic=stat,display_min=-lim if stat=='median' else 0,display_max=lim,n_finite=int(v.size),fraction_clipped_low=float(np.mean(v<(-lim if stat=='median' else 0))),fraction_clipped_high=float(np.mean(v>lim)),full_min=float(v.min()),full_max=float(v.max())))
table(A/'tables/display_limits.csv',audit);save(A/'provenance/figure.json',dict(limits=limits,quantile=.98,quantile_sampling='regular every fifth row and column, pooled equally by valid pixel across all four bands',render_sampling='nearest regular every third row and column; map illustration only; final up-to-two edge pixels omitted only in display',data_rasters_unclipped=True,dimensions_inches=[14,4.4],png_dpi=400,html_preview_dpi=200))
paths=[generated_figure_path(A,'paired_reflectance_maps.'+ext) for ext in ['png','pdf']]
run(['Rscript','--vanilla',A/'scripts/maps.R',A,limits['median'],limits['sd'],*paths])

preview=generated_figure_path(A,'paired_reflectance_maps_preview.png')
run(['Rscript','--vanilla',A/'scripts/maps.R',A,limits['median'],limits['sd'],preview,'none',200])
