# Two-figure scientific reports and spectral scale variants

**Take-home message:** Both report variants are ready for the existing presentation and independent scientific review route. All six targets and 54 paired bands are represented. Differences depend on target and band and do not establish either correction's accuracy. The main report shares one scale; the labelled alternative uses a separate scale for each target.

**Meaningful results:** Sen2Cor is higher throughout at T1/T4/T6, lower throughout at T2/T5, and changes from lower to higher between B05 and B06 at T3. Signed differences range from −0.054332 to +0.085140. Both reports show exactly the unchanged Figure 1 and the renewed Figure 3. All nine negative Sen2Cor values remain, without missing target–band pairs. No ASD series occurs in renewed Figure 3.

**Issues and limitations:** T2's thin-cirrus classification conflicts with zero cloud probability; both indicators are disclosed. Unequal stored spatial support and absent independent accuracy evidence prevent attributing all discrepancy to correction alone or ranking products. Supplied class labels are not verified habitats. Correlated bands are not independent replicates. Original physical-validation holds remain unresolved. Figure 1 has separate station/field-reference evidence and is not attributed to the new target set or acquisition.

**Implications and next steps:** Charles should route the exact final revision through Rachel's presentation stage and then Karl's independent scientific review on CTR38, including both scales and target/numerical correspondence. Their review does not constitute PI approval. No manuscript integration, merge or publication occurred. This closes Edward's specialist delivery only.

## Exact evidence and inputs

Verified numerical input revision: `c4ac607826d6f1c1f3b0ea6040e6a8775ac6bb5b`, following Roger's extraction `82ca0df0b699e51135afc680b23eda9def5bbfe2`. Approved presentation baseline: `3a2bf1b19e7f9f80b6830b8b0f056bbe6add2844`. Final author commit and package hashes are saved in the task delivery document and package manifest to avoid self-reference. Branch: `ctr-49-target-report`.

Use `tables/ctr48_plot_values.csv` (SHA-256 `065c9064993419f395c937e36a0027ab6c2e0f8bfa9b3152f35bb49865332629`) and `tables/ctr48_pairs.csv` (SHA-256 `047cfde28141ad81baa120c5e4773752b295f5c4cfbb3b4d0266bad3119032ad`). Accounting, target/band summaries, adjacent-band steps, scale ranges and independent arithmetic evidence remain unmodified. Roger and Thomas verified the exact six unique EPSG:32628 points, nine-band order and decode, original source identities, 108 finite values, point-specific QA and exclusions. No target coincides with an old station; neither AC03 nor AC04 maps to a target. Their original exclusions remain preserved. This task performed no raster reads or new integration.

The spectral pair represents the established 7 March 2026 Sentinel-2B acquisition. Full metadata, decode, pixel footprints, raster/window hashes, original-sidecar evidence and upstream-source limitations are retained in the predecessor technical files. Source imagery and raw confidential data are not included in the upload packages. This report revision reuses the CTR44 base-R/Quarto/compact-HTML framework, changes only the intended three existing report files, and adds scoped new files. All 500 other prior tracked files and 123 unrelated files passed byte-preservation checks. Original Figure 1 PNG/PDF/SVG and all underlying metrics and source attachments match the approved baseline.

## Outputs and validation

- `report.qmd` / `report.html`: main scientific report, one common y range across all target panels.
- `report-custom.qmd` / `report-custom.html`: labelled alternative, separate y range for each target shared by its two curves.
- `report-portable.html` / `report-custom-portable.html`: compact self-contained copies with the same main report content.
- `figures/generated/ctr49_target_spectra_{common,custom}.{png,pdf,svg}`: six-panel Figure 3 at 183 × 200 mm, 600 dpi PNG and editable vector exports. Retained Figure 1 exports are unchanged.
- `provenance/ctr49_target_spectra_*_rows.csv`: actual R drawing rows, byte-identical across variants; each compared with all 108 verified values.
- `provenance/ctr49_target_spectra_*_axes.csv`: actual scale limits; every value lies within them.
- `provenance/ctr49_validation.json`: input hashes, exact counts, report figure/resource checks, embedded Figure 1 byte checks and preservation results.
- `provenance/ctr49_visual_inspection.md` and `outputs/ctr49_*_check.png`: actual PNG/PDF and full-browser visual inspection evidence.

Reports contain scientific findings, significance, limitations and discussion only. Technical records, source identities, implementation, reproduction and review status remain here. No external literature mechanism or accuracy claim was introduced. Every scientific observation is supported by Thomas's verified findings and tables. No p-values, interval estimates, fitted models or ecological causal mechanisms were added.

## Reproduce

From the original repository root, using its existing locked environment:

```bash
./scripts/check-env.sh
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr49_delivery.py
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr49_export_300dpi.py
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr49_package.py
```

The first command passed without installations or dependency changes (pre-existing temporary-home normalization warning only). The second rebuilds both spectral exports, both editable reports, canonical and compact self-contained HTML, and validates them. R uses only base/grDevices; Python uses only the standard library. The safe generated-figure writer is reused. The final command packages the exact committed revision. Packages include repository-relative source paths and relevant environment/helper files; in the authorized repository no configuration replacement is required. Original extraction/independent validation utilities are retained for audit, not rerun by the presentation builder. Older CTR44 builders/validation records are historical and are not the entry point for these new reports. PDF creation metadata can vary without changing the data or plotted content. No seed is required.

## Draft PR evidence and remaining gate

The task-specific local branch and exact commit identify a reviewable result. Fetch completed. The mandatory clean-workspace preflight refuses 123 unrelated untracked CTR39 files in the shared checkout. They were preserved without deletion, stashing, staging or guard bypass. Analysis-only readiness passed. A proposed PR title/body is saved in `outputs/ctr49_draft_pr.md`; this is not a real PR. No pushed branch or PR is claimed while that prerequisite remains unsatisfied. Coordination and exact-revision review remain with Charles; no other task or parent review policy was modified.

## Transfer-sized packages

The transfer service returned an indeterminate timeout for large HTML/archive uploads; no upload receipt or accessible delivery is claimed for those attempts. Both compact standalone reports were saved successfully. To keep reviewer access usable, additional compact packages retain the exact editable QMD, generation/validation code, full-precision tables, source identities, numerical QA and hash manifest; browser captures and 600 dpi raster graphics remain in the complete local archive. The compact report ZIP contains both portable self-contained copies, preserving each canonical report's main content exactly. The compact figure ZIP contains PDF/SVG exports and additional 300 dpi PNGs rasterized directly from the exact vector PDFs through the safe generated writer. Original 600 dpi exports remain unchanged. This packaging adjustment changes no scientific figure values, scales or report content. The task document distinguishes confirmed uploads from complete local archives.
