"""Create the standalone Quarto report and task scaffold from verified numerical outputs."""
from common import *
import statistics, sys, platform
import numpy as np
read=lambda f:list(csv.DictReader((A/'tables'/f).open()))
rows=read('date_band_summary.csv');primary=[r for r in rows if r['domain']=='primary']; maps=read('temporal_raster_summary.csv');coverage=read('temporal_coverage.csv');fig=json.loads((A/'provenance/figure.json').read_text());valid=json.loads((A/'provenance/validation.json').read_text());pairs=json.loads((A/'outputs/pairs.json').read_text());display=read('display_limits.csv')
fmt=lambda x:f'{float(x):.5f}' if x not in [None,''] else 'undefined'
def md(headers,vals):return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+''.join('| '+' | '.join(map(str,r))+' |\n' for r in vals)
maprows=[];seriesrows=[];sensitivity=[]
for b in BANDS:
    mm=next(r for r in maps if r['band']==b and r['statistic']=='median');ss=next(r for r in maps if r['band']==b and r['statistic']=='sd');cc=[r for r in coverage if r['band']==b];pr=[r for r in primary if r['band']==b];nv=sum(int(r['n_pixels']) for r in cc if int(r['valid_dates'])>=2)
    maprows.append([b,fmt(mm['p50']),fmt(ss['p50']),f'{nv/7428162:.1%}',int(next(r['n_pixels'] for r in cc if int(r['valid_dates'])==22))])
    med=[float(r['median_delta']) for r in pr if r['median_delta']];co=[float(r['coverage_fraction']) for r in pr]
    seriesrows.append([b,fmt(min(med)),fmt(max(med)),f'{min(co):.1%}–{max(co):.1%}',sum(x>0 for x in med),len(med)])
    for domain in ['include_SCL7','exclude_high_TOA','complete_dates','coverage80','common_footprint']:
        dif=[];ns=[]
        for p in pr:
            s=next(r for r in rows if r['pair_id']==p['pair_id'] and r['band']==b and r['domain']==domain)
            if s['median_delta'] and p['median_delta']:dif.append(float(s['median_delta'])-float(p['median_delta']))
            ns.append(int(s['n_valid']))
        sensitivity.append([b,domain,fmt(statistics.median(dif)) if dif else 'undefined',min(ns),max(ns),len(dif)])
lim=fig['limits'];caption=f'Temporal median (top) and sample SD (bottom) of paired surface-reflectance differences, ACOLITE − Sen2Cor, for B2, B3, B4 and B8 across 22 acquisitions (6 January 2025–27 March 2026). The full supplied T28QCH comparison crop is retained at 10 m in UTM zone 28N; no marine-only mask is added. Blank cells lack the observations required for the statistic (median n≥1; SD n≥2). Median limits are shared at ±{lim["median"]:.5f}; SD limits are shared at 0–{lim["sd"]:.5f}, in dimensionless reflectance units. Display limits use pooled 98th-percentile scaling; values outside them are saturated for display only. Band-specific full-resolution clipping fractions appear below. A regular every-third-cell sample is used only to draw the maps. Missing ACOLITE flags on the two March 2026 dates and unequal per-pixel temporal coverage limit comparability; the figure does not establish correction accuracy.'
(A/'figures/generated/caption.md').write_text(caption+'\n')
review='Independent scientific review pending. PI scientific approval pending. Manuscript integration, merge and publication are not authorized.'
text='''---
title: "Paired Sentinel-2 reflectance differences"
subtitle: "CTR-54 geospatial analysis · CTR-55 delivery · draft for review"
author: "Roger Tomlinson · Ctrl+Sea"
date: "2026-10-20"
format:
  html:
    embed-resources: true
---

## Take-home message

ACOLITE surface reflectance is typically lower than Sen2Cor on the supplied T28QCH footprint across the 22 paired Sentinel-2 acquisitions. The maps and tables quantify disagreement between ACOLITE and Sen2Cor; they do not identify the more accurate correction or establish ecological change. Interpret temporal patterns alongside spatial coverage and quality information.

## Meaningful results

The comparison retains all valid land, intertidal and water pixels in the supplied 742.8162 km² rectangular crop. ACOLITE dates 15 February and 13 October 2025 have no same-tile Sen2Cor counterpart. All selected pairs have matching sensor, datatake, orbit, tile and tile sensing time. Reflectance grids align exactly.

'''
text+=md(['Band','Median of pixel temporal medians','Median of pixel temporal SDs','Grid with ≥2 valid dates','Pixels valid on all 22 dates'],maprows)
text+='''
These map-distribution summaries weight each eligible pixel once. The median of temporal medians is distinct from a pooled pixel/date median or the median of per-date spatial medians.

'''
text+=f'![Paired reflectance differences](figures/generated/paired_reflectance_maps_preview.png)\n\n{caption}\n\n'
text+='''### Spatial summaries within each acquisition

'''+md(['Band','Smallest date median ΔR','Largest date median ΔR','Primary grid coverage range','Dates with positive spatial median','Dates with defined median'],seriesrows)
text+='''
Each date/band has its own spatial median, sample SD and valid count in `tables/date_band_summary.csv`. Date gaps are unequal. Spatial SD is variation across retained pixels, not uncertainty of a mean or correction accuracy.

## Issues and limitations

The original ACOLITE crop and its earlier polygon clipping constrain geographic scope; full Sentinel-2 tile coverage cannot be inferred from this crop. The two March 2026 ACOLITE deliveries lack flag layers. Their quality filtering therefore relies on Sen2Cor SCL and finite paired observations. SCL and ACOLITE flags have no independent validation here. Cloud remnants, aerosols, adjacency, glint, tide, bottom visibility, phenology, sensor differences and changing spatial sampling can all affect observed differences. Negative reflectance is retained when otherwise valid.

No field observations or ground-truth accuracy assessment enter this investigation. Cross-correction agreement is not evidence that either correction is accurate. No causal/ecological trend is inferred. Small temporal counts must be read alongside the count rasters.

## Implications and next steps

Use the primary summaries for descriptive comparison and the sensitivity tables to assess dependence on quality and coverage. Statistical modelling should account for spatial/temporal dependence, sensor differences and unequal date gaps. The supplied spatial SD must not be treated as an independent measurement-error estimate. Independent review and a separate authenticated PI decision are required before findings can support the manuscript.

## Question, data and methods

How do paired ACOLITE and Sen2Cor surface reflectances differ for B2/B3/B4/B8 in the available Sentinel-2 observations? ΔR = ACOLITE − Sen2Cor, dimensionless. B8A is excluded.

The inventory contains 24 ACOLITE date directories, 46 Sen2Cor ZIP products and two loose SAFE products. Twenty-two T28QCH acquisitions are paired across Sentinel-2A/B/C, 6 January 2025–27 March 2026. Unpaired products and reasons remain in `tables/acquisition_inventory.csv`. Candidate QCG tiles are not duplicated or substituted for CH. Sensor-specific ACOLITE band parameters and actual wavelengths are recorded in `tables/band_mapping.csv`.

Reference grid: EPSG:32628; 3763 × 1974 cells; 10 m; E=334050–371680 m; N=2190240–2209980 m. Sen2Cor reflectance is cropped at exact integer pixel offsets without interpolation. SCL uses nearest-neighbour transfer from 20 to 10 m. No additional ecological mask is imposed.

ACOLITE Float32 `rhos` is already dimensionless surface reflectance (scale 1, offset 0). Sen2Cor is decoded with each product's XML as `(DN + BOA_ADD_OFFSET) / BOA_QUANTIFICATION_VALUE`; selected offsets are −1000 and quantification is 10000. DN=0, saturated DN, nonfinite ACOLITE observations and the exact default netCDF Float32 fill value are excluded. The supplied ACOLITE deliveries contain that finite sentinel despite their GeoTIFF NoData=NaN metadata; all 88 input band rasters are audited in `encoded_fill_audit.csv`. The audit identifies 118,596 fill cells per raster (1.60% of the rectangle). No arbitrary reflectance upper bound is applied; valid negative values are preserved.

Primary joint QA retains SCL 4/5/6 and rejects available ACOLITE cirrus, out-of-scene and DEM-shadow bits. Non-water SWIR and negative-reflectance flags are retained. Bright-pixel high-TOA flags are a separate sensitivity because they can remove valid land. Files without ACOLITE flags are identified explicitly. Full methods, assumptions and documentation are in `METHODS.md`.

Temporal median uses n≥1 and sample SD uses n≥2 with denominator n−1. Per-date spatial SD also uses n−1. Processing uses 64-row chunks, Float64 computation and disk-backed Float32 differences on local SSD. All reported statistics use full-resolution values; only drawing uses a regular sample. Raw files are read without alteration.

## Coverage and mask sensitivity

The complete-date core retains only pixels valid on all 22 dates. The 80% core retains pixels valid on ≥18 dates. The common-footprint core requires finite paired observations in every band/date before quality masking. These conditional cores test coverage effects but can favour consistently clear locations. Additional masks include SCL 7 or exclude high-TOA flags. All domains and empty cases are retained in the downstream table.

'''
text+=md(['Band','Sensitivity domain','Median across dates of change in spatial median ΔR','Min valid pixels/date','Max valid pixels/date','Comparable dates'],sensitivity)
text+='''
A change in the spatial median can reflect changed spatial support; this table is descriptive, not an inferential test. Sensitivity domains overlap and are not independent samples. Primary footprint and negative-count diagnostics repeated in sensitivity rows are labelled explicitly in `TABLE_CONTRACT.md`.

## Display clipping audit

'''
text+=md(['Band','Statistic','Display minimum','Display maximum','Clipped below','Clipped above'],[[r['band'],r['statistic'],fmt(r['display_min']),fmt(r['display_max']),f'{float(r["fraction_clipped_low"]):.2%}',f'{float(r["fraction_clipped_high"]):.2%}'] for r in display])
text+=f'''
The same limits apply to all four bands within a row. The full scientific rasters and tabulated minima/maxima remain unclipped. The exported PNG is 400 dpi (the HTML embeds a 200 dpi preview); the accompanying PDF preserves text and embeds map rasters.

## Validation and reproducibility

Direct checks against original source pixels: {valid['source_checks']}; maximum absolute discrepancy {valid['max_source_absolute_error']:.3g}. Temporal raster spot checks: {valid['temporal_checks']}; maximum absolute discrepancy {valid['max_temporal_absolute_error']:.3g}. All {valid['rasters_checked']} scientific raster outputs passed grid, CRS, datatype and NoData checks. Base R independently recomputes temporal statistics from the delivered sample values. Numerical check tables are retained; these checks are distinct from independent scientific review and thematic accuracy.

Inputs: `provenance/input_hashes.csv`; outputs: `provenance/output_hashes.csv`; exact revision, durable paths and execution commands: `HANDOFF.md` and `provenance/handoff.json`. Restore the repository lockfiles with the authorized project tools. Re-run the recorded `scripts/run.sh` sequence, including the source-fill audit, with `CTR54_SOURCE` and `CTR54_SCRATCH` set if needed. Figure and report stages use the recorded project Python/R and existing Quarto installation. No dependency change was required. Detailed software versions and lockfile hashes are in `provenance/environment.json`.

## Internal review and approval status

{review}

## Documentation

- [Copernicus Sentinel-2 product organization and reflectance decoding](https://sentiwiki.copernicus.eu/web/s2-products).
- [Copernicus Sentinel-2 processing and scene classification](https://sentiwiki.copernicus.eu/web/s2-processing).
- [Official ACOLITE project and processing documentation](https://github.com/acolite/acolite).
- [Official ACOLITE flag code](https://github.com/acolite/acolite/blob/main/acolite/acolite/acolite_flags.py). The source metadata record flag exponents; the original processor commit is not recoverable from the timestamp-style version string.
'''
(A/'report.qmd').write_text(text)
env=dict(python=sys.version,numpy=np.__version__,R=run(['Rscript','--vanilla','-e','cat(as.character(getRversion()))']).strip(),quarto=run(['quarto','--version']).strip(),gdal=run(['gdalinfo','--version']).strip(),platform=platform.platform(),python_executable=sys.executable,uv_lock_sha256=sha(REPO/'uv.lock'),renv_lock_sha256=sha(REPO/'renv.lock'),dependencies_changed=False)
save(A/'provenance/environment.json',env)
(A/'task.yml').write_text(f'''task:
  id: CTR-54
  delivery_task: CTR-55
  paperclip_issue_id: 868eb798-9341-4ffd-b10c-1b515fce46c0
  title: Paired Sentinel-2 reflectance differences
  research_question: How do matched ACOLITE and Sen2Cor surface reflectances differ?
  created_at: '2026-10-20'
analysis:
  status: computations_checked_review_pending
  language: [Python, R]
  input_datasets: [data/raw/S2/ACOLITE, data/raw/S2/Sen2Cor, data/raw/S2/top-level-SAFE]
  scripts: [scripts/01_inventory.py, scripts/09_fill_audit.py, scripts/02_process.py, scripts/03_validate.py, scripts/04_figures.py, scripts/05_R_crosscheck.R, scripts/06_input_manifest.py, scripts/07_report.py]
  report_source: report.qmd
  report_html: report.html
environment:
  python_lockfile: ../../uv.lock
  python_lockfile_sha256: {env['uv_lock_sha256']}
  r_lockfile: ../../renv.lock
  r_lockfile_sha256: {env['renv_lock_sha256']}
  python_version: '{platform.python_version()}'
  r_version: '{env['R']}'
  quarto_version: '{env['quarto']}'
  dependencies_changed: false
  provenance_file: provenance/environment.json
review:
  status: pending
  reviewer: Karl Popper
pi_approval:
  status: pending
  approved_revision: null
  note: This YAML is not evidence of authenticated PI approval.
manuscript:
  integration_status: not_authorized
  merge_status: not_authorized
  publication_status: not_authorized
''')
