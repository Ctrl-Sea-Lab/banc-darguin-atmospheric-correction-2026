#!/usr/bin/env python3
"""Build the compact, editable CTR24 numerical amendment from verified tables."""
import csv
import json
from pathlib import Path
P = Path(__file__).resolve().parents[1]

def rows(name):
    return list(csv.DictReader((P/'tables'/name).open()))

def md_table(data, columns):
    out = ['| ' + ' | '.join(columns) + ' |', '| ' + ' | '.join(['---']*len(columns)) + ' |']
    for row in data:
        out.append('| ' + ' | '.join(str(row[k]) for k in columns) + ' |')
    return '\n'.join(out)

metrics=rows('ctr37_station_metrics.csv')
pretty=[{'Station':r['station_id'],'Correction':r['correction_label'],'N bands':r['n_paired_bands'], **{k:f"{float(r[k]):.6f}" for k in ['bias','MAE','RMSE']}} for r in metrics]
sensitivity=rows('ctr37_v5_sensitivity_metrics.csv')
sens=[{'Station':r['station_id'],'Correction':r['correction_label'], **{k:f"{float(r[k]):.6f}" for k in ['bias','MAE','RMSE']}} for r in sensitivity if r['population']=='primary']
audit=json.loads((P/'provenance/ctr37_input_audit.json').read_text())
contract=json.loads((P/'outputs/ctr37_contract.json').read_text())
text=r'''---
title: "Station-level satellite–ASD numerical agreement"
subtitle: "CTR24 diagnostic amendment • CTR-37 • 20 October 2026"
author: "Thomas Bayes · Ctrl+Sea"
format:
  html:
    embed-resources: true
    toc: true
    number-sections: false
execute:
  enabled: false
---

Six stations have complete B02/B03/B04 numerical matchups for the two supplied correction products. The results below describe **exploratory discrepancies in dimensionless reflectance (1)**. All 18 station–band triples retain their physical holds; **zero pairs are eligible for validation**. These results do not estimate correction accuracy or establish a preferred correction.

## Question and scope

For each of AC01, AC02, AC05, AC06, AC07 and AC08, how far do the fixed containing-cell satellite values differ from the supplied ASD station-average spectrum integrated against the S2B band responses? This dated amendment implements the CTR-35 diagnostic estimand, superseding the earlier prohibition on *held numerical diagnostics* only. The original validation population remains empty and unchanged. The reviewed dictionary remains in `report.qmd`/`report.html`; this separate amendment preserves it.

No statistical model is fitted. Bands are repeated spectral measurements of a station, not independent biological replicates. There are no p-values, correlation coefficients, uncertainty intervals, inferred scan variability, or regional conclusions. The six stations define the frozen descriptive population, not a validated or representative sample.

## Results

Every primary station has three common finite bands, with exactly the same rows used by both corrections. No primary spectrum is partial. N bands is a denominator count, not an independent sample size. Values are rounded to six decimals here; CSV files retain computation precision.

'''+md_table(pretty,['Station','Correction','N bands','bias','MAE','RMSE'])+r'''

Sen2Cor operational L2A station biases range from +0.009023 to +0.107728; ACOLITE biases range from −0.001827 to +0.064366. Station MAEs range from 0.009023 to 0.107728 for L2A and from 0.005246 to 0.064366 for ACOLITE. These are observed discrepancies on the fixed diagnostic set, not estimates of algorithm performance.

At AC06, ACOLITE's signed bias is −0.001827, MAE is 0.007502 and RMSE is 0.008342. Opposite-signed band differences partly cancel in the bias. Near-zero bias therefore does not imply close agreement in every band.

Seven additional non-mud stations, D06_A through D06_G, have retained continuous ASD spectra but no exported satellite match or band-integrated reference in the handoff. Their 21 station–band triples remain explicitly NA; both corrections receive N=0 and NA metrics. They are supplementary and are not substituted into the six-station population. AC03 **mbp_mud** and AC04 **mpb_mud** remain PI-excluded, with original spellings retained in the exclusion ledger. B08 remains excluded for insufficient spectral coverage.

## Methods and input audit

The task reuses the exact consolidated handoff at `eea2b6067284f867770c0854edb84b17b55a4143`, and the existing CTR-29 design and CTR-30 concurrence. The CTR-35 amendment was saved before comparisons; the local computation contract was additionally committed at `be87422` before any metric calculation. The pipeline saves a successful input audit before computing errors and fails closed if a frozen essential input or identity check fails.

The documented scene pair is S2B, 27 March 2026, T28QCH. Metadata record satellite time 11:45:53.975343 UTC; the product-name time is not substituted for that time. ASD wavelength units (nm), dimensionless reflectance and identity conversion are supported by the recorded PI field testimony. Station IDs, original ASD columns, GPS joins and EPSG:4326 coordinates are retained; the saved projected containing cells use EPSG:32628. AC01/02 use the documented Iwik correction while retaining obsolete source text in historical records.

Supplied ACOLITE DSF `rhos` is dimensionless surface reflectance read directly from Float32 values. Operational Sen2Cor L2A PB05.12 values use (DN−1000)/10000 after DN 0 and 65535 are masked. Valid negative values are not clipped. This compares supplied products; neither atmospheric processor was rerun. Shared scene identity is documented, but byte-identical upstream L1C ancestry remains unestablished.

The supplied S2B v4 SRF is primary. Existing normalized response-weighted ASD integration uses trapezoidal integration on union knots, finite adjacent ASD interpolation at gaps no larger than 1 nm, no extrapolation and minimum response coverage 0.999. B02/B03/B04 references pass; the saved independent quadrature checks and source/SRF identities are retained. V5 references remain separate sensitivity inputs.

The new audit verifies frozen input/evidence hashes, source hashes, raster path/size/mtime, units, scene and station joins, saved raw decoding, and reference numerators/denominators. It reuses the saved 256-check centre/coordinate audit and 128-check technical/quadrature audit without rerunning extraction. Raster identity is bounded metadata and recorded centre/window evidence, not a whole-raster byte identity claim.

For station s, correction c and its common finite band set B_s:

$$ e_{scb} = y_{scb} - x_{sb}, \qquad
\mathrm{Bias}_{sc}=\frac{1}{N_s}\sum_{b\in B_s}e_{scb},\qquad
\mathrm{MAE}_{sc}=\frac{1}{N_s}\sum_{b\in B_s}|e_{scb}|,\qquad
\mathrm{RMSE}_{sc}=\sqrt{\frac{1}{N_s}\sum_{b\in B_s}e_{scb}^{2}}. $$

Positive bias means satellite reflectance exceeds ASD reflectance. Each available band has weight 1/N_s; for all primary results N_s=3. A band is common only when ASD and both satellite values are finite. The primary table requires all three bands; partial or unavailable spectra are supplementary with explicit missing reasons. No pooled or per-band average is reported, so no extra station-weighting estimand is introduced. NA is never replaced with zero.

## Separate v5 sensitivity

The largest absolute v5−v4 reference change across the 18 existing references is **0.0000155204** reflectance units, at AC06 B02. V5 metrics below use the same satellite values, stations and bands. Small SRF sensitivity does not resolve the spatial-support or exposure limitations.

'''+md_table(sens,['Station','Correction','bias','MAE','RMSE'])+r'''

## Physical limitations retained

ASD measures a small field footprint; the satellite number is a containing stored cell. Exact effective radiometric contributors, common full-support QA and representative field-patch support are unresolved. AC01/02/06/07/08 retain material patch-representativeness concerns; AC05/06/08 also retain overpass exposure/optical-path ambiguity. All six retain an unverified effective-support bound. No detected identity or unit mismatch prevents these numerical diagnostics, but physical equivalence remains unproven.

Field timing is described as around acquisition; precise clock/timezone, station-average membership, calibration variance and scan variance remain unavailable. SCL categories alone do not establish immersion or ecological identity. No guessed error bars or independent station/band count is supplied. Uncertainty in spatial support, exposure and processing lineage is not estimated by these discrepancy metrics.

## Figure handoff to Edward

Use `tables/ctr37_spectral_long.csv` for station facets: one row per station, band and series (ASD, L2A, ACOLITE); 54 finite values for the six primary stations and 63 explicit NA values for supplementary stations. Plot B02/B03/B04 as an ordered categorical band axis; connecting lines indicate spectral order only. This avoids assigning an undocumented common effective wavelength to distinct product/reference responses. V5 has a separate long table and must not replace primary v4 values.

Use `tables/ctr37_figure_pairs.csv` for the two-correction scatter: x=ASD_reflectance, y=satellite_reflectance, band colour, literal target class shape. There are 36 finite correction rows representing the same 18 triples, plus 42 explicit supplementary NA rows. Retain a 1:1 line and comparable axes. Filter on `common_finite_triple=True`, fixed primary station IDs and `station_completeness=complete`. Do not interpret `included_validation_pair=False` as missing diagnostic data or clear it for plotting. The separate status fields preserve this distinction. Do not draw regression fits or inferential error bars.

**Station-facet caption:** Band-integrated ASD station averages and containing-cell reflectance from supplied operational Sen2Cor L2A and ACOLITE DSF for six non-mud stations on 27 March 2026, using S2B v4 references and B02/B03/B04. Values are dimensionless. Lines connect fixed bands for display; uncertainty is not estimated. All 18 triples are exploratory and physically held; zero validation-eligible pairs.

**Scatter caption:** Exploratory satellite–ASD numerical agreement for the same six stations and three bands in each correction panel (18 plotted points per correction). The diagonal is 1:1 numerical agreement. Bands are repeated measurements; the points are not independent replicates. Spatial-support and exposure holds remain. Supplementary D06 stations lack matched exports and are omitted from the scatter with missingness reported separately.

The CSV schema, statuses, exact keys, missing reasons and units are documented in `outputs/ctr37_table_contract.json`. Figure styling, PNG/PDF/SVG production and assembly of the final report belong to the existing CTR-38 task; this numerical delivery does not claim those products are complete.

## Verification, reproduction and review

'''+f"The new input audit passed {audit['check_count']} checks. Base R independently recomputed the metrics from the frozen wide inputs and passed 74 checks, including mixed-sign and empty-set fixtures, exact figure values, identical correction subsets, missingness, unique keys and RMSE ≥ MAE ≥ |bias|. This independent arithmetic implementation is author QA, not independent scientific review.\n\n"+r'''
From the canonical repository root, using the existing project environments:

```bash
.venv/bin/python analysis/CTR-24_data-dictionary/scripts/ctr37_diagnostics.py
./scripts/project-env.sh Rscript analysis/CTR-24_data-dictionary/scripts/ctr37_verify.R
.venv/bin/python analysis/CTR-24_data-dictionary/scripts/ctr37_report.py
(cd analysis/CTR-24_data-dictionary && ../../scripts/project-env.sh quarto render diagnostic-agreement.qmd --to html)
```

Python uses only its standard library; verification uses base R. No dependency changes, MCMC or random draws are required. Audit/run timestamps may change on reproduction; numerical tables must reproduce byte-for-byte. Saved provenance records software versions, source/table hashes, the frozen input commit and development warnings. The Paperclip diagnostic-agreement document records the exact final commit and downloadable bundle identity. Preserve the existing dictionary and original eligible-validation table.

**Review status:** Author numerical handoff only. Edward assembles figures/report; Rachel checks presentation and Karl independently reviews the exact assembled revision through CTR-38's native stages. Charles coordinates PI submission. Scientific approval, manuscript integration, protected merge and public publication are not granted by this report.
'''
(P/'diagnostic-agreement.qmd').write_text(text)
(P/'outputs/ctr37_table_contract.json').write_text(json.dumps({
 'primary_metrics':'ctr37_station_metrics.csv: 12 rows; station/correction unique; v4, complete fixed spectra',
 'supplementary_metrics':'ctr37_supplementary_metrics.csv: 14 unavailable station/correction rows; N=0, metrics NA',
 'v5_metrics':'ctr37_v5_sensitivity_metrics.csv: 26 rows; 12 finite primary plus 14 unavailable supplementary',
 'figure_pairs':'ctr37_figure_pairs.csv: 78 rows; station/band/correction unique; 36 finite primary, 42 supplementary NA',
 'spectral_long':'ctr37_spectral_long.csv: 117 rows; station/band/series unique; 54 finite primary, 63 supplementary NA',
 'booleans':'CSV True/False strings; explicitly parse in R; included_validation_pair always False',
 'NA':'literal NA for unknown quantities; zero n_paired_bands means no usable band, not zero discrepancy',
 'unit':'1 (dimensionless reflectance); signed difference and all metrics on same scale',
 'band_order':['B02','B03','B04'], 'station_order':contract['primary_stations'],
 'classes':'literal dry_sand, algae_mud, white_sand, seagrass; supplementary zn/sand; do not silently recode',
 'plot_filter':'fixed six primary stations; common_finite_triple=True; v4_primary; complete spectra',
 'status':'EXPLORATORY_DIAGNOSTIC_PHYSICAL_HOLD or UNAVAILABLE_NOT_SUBSTITUTED; no validation eligibility release',
 'captions':'diagnostic-agreement.qmd, Figure handoff to Edward',
 'sensitivity':'v5 tables explicitly separate; do not duplicate primary plotted points',
 'precision':'full Python round-trip float precision in CSV; displayed metrics six decimals'
},indent=2)+'\n')
print('Report and table contract built from verified outputs')
