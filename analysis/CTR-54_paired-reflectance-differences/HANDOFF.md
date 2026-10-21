# CTR-55 geospatial handoff for CTR-54

**Take-home message:** Across 22 matched acquisitions, ACOLITE is generally lower than Sen2Cor on the supplied footprint. The median of pixel temporal medians is −0.00962 (B2), −0.00857 (B3), −0.00793 (B4), and −0.00893 (B8), in dimensionless reflectance. These descriptive differences do not establish correction accuracy or ecological change.

**Meaningful results:** 88 paired-date/band difference rasters; 12 temporal median/SD/count rasters; 13 additional footprint and sensitivity masks; the 2×4 map figure; and 528 date/band/domain summary rows. Spatial coverage varies approximately 72–98% of the fixed grid. Source-pixel, temporal, R and full-grid validity checks pass.

**Issues and limitations:** Exact default-fill values were excluded explicitly after a complete 88-band audit; 118,596 fill cells occur per source raster despite declared NoData=NaN. March 2026 lacks ACOLITE flags. There is no independently validated quality mask or field-reference accuracy assessment. Full limitations and coverage sensitivities are in the report.

**Implications and next steps:** Thomas Bayes can use `tables/date_band_summary.csv`, starting with domain=primary and reading TABLE_CONTRACT.md. Downstream writing and engineering can consume this bounded geospatial delivery. Existing independent review is CTR-59 after downstream assembly; PI scientific approval remains pending. This completion does not authorize manuscript integration, merge or publication.

## Exact revision and durable delivery

Analysis revision: `1bbb23b3b94e775a60aa921f8c9c4f86f51926cb` on local branch `ctr-55-paired-reflectance`, based on `f21777bffe1392b0d207b265b852232a779a16f1`. This revision contains all analysis code, report, figure and manifests. A subsequent handoff-only commit adds this record without changing scientific outputs. No branch was merged or published.

Canonical investigation: `/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026/analysis/CTR-54_paired-reflectance-differences`

Isolated worktree investigation: `/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026/.task-worktrees/CTR-55/analysis/CTR-54_paired-reflectance-differences`

Inputs: `/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026/data/raw/S2` (preserved).

`provenance/input_hashes.csv`: SHA-256 `e0b207ea8d92ea0058b1db9d9a970fee8041f5330541d0b607f4898758b30a31`; 142 used physical input files, 22,240,796,841 bytes. All source sizes and modification times remain stable against the hash pass.

`provenance/output_hashes.csv`: SHA-256 `d6c86eb7be928dd850eb9190647b1927c0fa749fa8ad638ade993867b3ce5bbb`. It lists exact file sizes/hashes, including scientific rasters, tables, figures, report, scripts and provenance. Drawing bridges are regenerable and excluded. Handoff records are excluded to avoid self-reference.

Full-resolution raster archive: `outputs/CTR55_all_rasters.zip`; 2,092,926,845 bytes; SHA-256 `e4acbee5342215c8c94054b32ceb8ea830060b7b3cb6aa0b5297a03cadc383eb`. It contains 113 exact GeoTIFF products and no raw inputs. It remains on the NAS. Task workspace registration was rejected; remaining file delivery requires recovery. The modelling CSV is confirmed as a task artifact. Upload of the full report timed out with an indeterminate outcome; the subsequent review-package request was followed by failure of the task callback bridge. Report, figures and the source package are prepared and preserved, but their task publication is not confirmed.

## Validation evidence

- 12 direct original-source checks, maximum absolute difference 7.12e-10.
- 96 temporal raster checks, independently repeated in base R, maximum raster discrepancy 1.86e-09.
- All 113 raster grids, CRS, datatype and NoData definitions checked; all-cell median/SD validity agrees with temporal counts.
- Every used source band grid and every exact fill sentinel audited; 22 acquisition keys unique and exact tile sensing times checked.
- Project environment check passed, unchanged lockfiles; isolated Quarto HTML rendered and offline resource references checked.
- Figure visually inspected by the analysis author, with clipping fractions retained per band. Independent scientific review is pending.

Reproduce using `scripts/run.sh` through the repository's project environment. In a worktree, set `CTR54_PYTHON=/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026/.venv/bin/python` to reuse the checked environment. Use local SSD scratch and the recorded lockfiles. The analysis is confined to this investigation and modifies no manuscript or PI-protected path.

## Delivery recovery

Confirmed attachment: `abea9a9d-32d8-445d-9d12-45cf99db513f`; work product `4be3b355-24cc-44fe-aef6-660aa6c58cea`. Remaining uploads/registrations and the task completion update could not be saved because the callback bridge returns HTTP 503. Do not replay ambiguous uploads without checking saved attachments. Scientific computations need no rerun. A fresh execution context should recover delivery and then complete CTR-55 to release the existing downstream chain.
