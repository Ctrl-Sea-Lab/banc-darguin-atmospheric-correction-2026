# CTR-56 statistical handoff for Rachel Carson

**Take-home message:** The requested two-panel temporal GAM figure is complete for 22 matched acquisitions and B2/B3/B4/B8. ACOLITE generally has lower surface reflectance than Sen2Cor. Changing spatial coverage alone does not explain the curves, but acquisition influence, residual departures and missing quality flags prevent strong trend or seasonal inference.

**Meaningful results:** Median across date-level spatial medians: B2 −0.00962, B3 −0.00924, B4 −0.00751, B8 −0.00935, dimensionless reflectance. Negative median differences occur on 19/22 visible-band dates and 21/22 B8 dates. Fixed complete-date cores retain approximately 3.54 million pixels per band; their fitted curves differ from primary by at most 0.00103 for medians and 0.000786 for SD. Do not confuse these date-level medians with the map-level statistics in CTR-55.

**Issues and limitations:** Only 22 irregular dates, with gaps of 2–70 days. Median-model residuals are left-tailed; log-SD residuals show negative adjacent-acquisition correlation. The strongest median influence is 22 March 2025; the strongest SD influence is 7 March 2026. Removing both March 2026 dates without ACOLITE flags changes SD curves by up to 0.00579 on shared temporal support. Approximate model intervals are illustrative, not calibrated temporal inference. No ground-truth accuracy or ecological-change claim is supported.

**Implications and next steps:** Use `ctr56-statistics.html` and `outputs/ctr56-report-body.qmd` for scientific writing, and the provided figure/caption. The combined `report.qmd` and `report.html` extend the predecessor report without deleting its body. Continue the existing CTR-57 → CTR-58 → CTR-59 writing, engineering and independent-review chain. This bounded modelling handoff is complete; the overall investigation is not scientifically complete or PI approved. Integration, merge and publication remain unauthorized.

## Exact revisions and paths

- Statistical scientific revision: `f1ae24ad409ae31f82cad4fd1767ed9861145fbf`, local branch `ctr-56-temporal-gam`.
- Consumed CTR-55 scientific revision: `1bbb23b3b94e775a60aa921f8c9c4f86f51926cb`.
- Extended CTR-55 handoff revision: `1631082eb8089b2beeaec8a97f6214191373f8e7`.
- Exact statistical output manifest: `provenance/ctr56_output_hashes.csv`; SHA-256 `3de7fb1f2a8a1763e8def45390707bda69f0f3a0226fffd4508bd70aa7fd04d7`.
- Consumed date-table SHA-256: `342f79e8f154dde2780bd6a6df974dfe3df097cfca9dd0246419f3bb81df202a`.
- Preserved predecessor output-manifest SHA-256: `d6c86eb7be928dd850eb9190647b1927c0fa749fa8ad638ade993867b3ce5bbb`.
- Preserved predecessor raw-input-manifest SHA-256: `e0b207ea8d92ea0058b1db9d9a970fee8041f5330541d0b607f4898758b30a31`.

Worktree: `/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026/.task-worktrees/CTR-56/analysis/CTR-54_paired-reflectance-differences/`.

Permanent delivery snapshot: `/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026/analysis/CTR-54_paired-reflectance-differences/outputs/CTR56_delivery/`.

The permanent snapshot and `CTR56_review_package.zip` preserve this task's combined report and task metadata without overwriting the canonical predecessor report or other agents' files. Manifest paths are relative to the statistical worktree/snapshot, not the old canonical report root. The predecessor `output_hashes.csv` identifies upstream outputs only; use the CTR-56 manifest for extended reports. The archive does not contain raw datasets or duplicate the large raster archive. A later handoff-only commit may add this document and delivery metadata; it does not change scientific outputs.

## Validation evidence

- All 528 unique date/band/domain rows checked for keys, positive finite SD, ranges and coverage/count consistency.
- 24 paired rasters and four complete-core masks matched the predecessor hashes. Full-resolution counts, medians and sample SDs matched all 48 selected primary/core rows within 10⁻¹²; six dates span the first date, negative outlier, minimum coverage, December and both March 2026 dates.
- All 48 domain/band/statistic models converged; eight primary models have smoothing-uncertainty covariance matrices.
- 176 leave-one-date-out refits, doubled-basis comparisons, five domain sensitivities, missing-flag exclusion, residual diagnostics and actual-time-lag semivariograms retained.
- Saved predictions/SEs match model calculations to 6.22×10⁻¹⁵; median GAM curves agree with independent ordinary least-squares calculations to 1.35×10⁻⁷. Positive inverse-transformed SD and endpoint covariance calculations checked.
- Repeated computation gives identical numerical tables. R model warning log is empty.
- Both HTML reports rendered under the investigation configuration and embed all figures; primary figure visually inspected, with no clipping and all dates plotted.
- Canonical repository environment check passed; lockfiles unchanged. A worktree-library configuration mistake was corrected, its failed render logs retained, its run-created nested library removed, and final renders/environment checks passed. No system software or project dependency changes are delivered.
- PI contribution guard against the exact source handoff: no protected changes detected. Authored R/Python/Quarto/task source passes whitespace checks. Generated HTML/R logs/CSV may contain generator whitespace; it has no numerical effect.

These are author validation checks, not independent scientific review. Karl's review and authenticated PI scientific approval remain pending.

## Reproduction and contents

Read the statistical HTML for executable commands. `scripts/ctr56_run.py` uses the canonical project environment by default; `CTR56_ENV_ROOT` can name an equivalent restored repository and both lockfiles must match. The raster audit reads existing products through `CTR56_PRODUCTS`; it never rewrites them. Intensive temporary raster bridges use `/tmp` on the worker. The main PNG is 3096×2232 at 360 dpi; a vector PDF is included. The statistical report is HTML only.

Deliverables include the combined and statistical HTML reports, report sources, four statistical scripts, figure PNG/PDF, coverage/uncertainty and residual figures, fitted model RDS, predictions, diagnostics, effect-size intervals, sensitivities, influence tables, input/hash audits, software versions and rendering evidence. The exact revision should be used for downstream work; do not recompute the geospatial pipeline merely to consume this handoff.

## Main figure caption

Date-level differences between atmospheric corrections. Points show all 22 spatial medians (top) and sample SDs (bottom) per band; lines are separate descriptive REML GAMs. ΔR = ACOLITE − Sen2Cor, dimensionless reflectance. SD curves are exponentiated log-scale fits. Curves span observed dates only; the two March 2026 acquisitions lack ACOLITE flags.
