# Preferred custom-axis report without flag annotations

**Take-home message:** The PI-selected custom-axis report is now the preferred and canonical delivery. The flag annotation has been removed from the second displayed graphic, including PNG, PDF, SVG and the embedded report image. The scientific findings are unchanged.

**Meaningful results:** All six targets, nine bands, 108 original reflectance values, nine negative Sen2Cor values and both correction curves remain. Drawing rows, QA fields, missingness and per-panel axis limits are byte-identical to scientific baseline `4e4e46b3b05fb30ef11549c28f5e96e7a40f1bcc`. Exactly two figures remain with their existing labels. Figure 1 PNG/PDF/SVG and embedded SVG are unchanged. All 75 numerical tables are unchanged. No extraction or statistical analysis was rerun.

**Issues and limitations:** Thin-cirrus versus zero cloud probability, unavailable independent ACOLITE mask, unequal spatial support, supplied class labels, lack of independent accuracy evidence and earlier physical-validation limitations remain in scientific prose/evidence. Separate y ranges magnify smaller differences and cannot support comparison of panel heights as absolute magnitudes. This is author QA, not scientific approval. CTR50's clean-workspace/PR prerequisite remains unresolved; no push, PR, guard bypass, merge, publication or manuscript change occurred.

**Implications and next steps:** Charles verifies the new exact revision and routes it through the existing CTR38 Rachel presentation stage, then Karl independent scientific review. The PI's presentation preference and earlier reviews do not approve this revision scientifically. This bounded author task is complete on delivery; it does not wait for a new PI decision.

## Delivery and entry points

- `report.html` / `report.qmd` are canonical copies of `report-custom.html` / `report-custom.qmd`.
- `report-custom-portable.html` is the preferred compact standalone download; `report-portable.html` has identical bytes. Embedded graphics are self-contained.
- `report-common.{qmd,html}` and `report-common-portable.html` preserve the former common-axis entry points byte-for-byte. Existing common-axis figure exports and all previous packages remain unchanged.
- Updated graphic: `figures/generated/ctr49_target_spectra_custom.{png,pdf,svg}`, with an additional PDF-derived `_300dpi.png`. Figure identifiers were not arbitrarily relabelled.
- Source: `scripts/ctr49_spectra.R` now omits the note only in custom mode and accepts an optional mode argument. `scripts/ctr52_delivery.py` reuses CTR49 helpers and validated CTR48 inputs, rendering only the custom variant. The earlier CTR49 builder is historical; use CTR52 for the selected report.
- `scripts/ctr52_package.py` packages committed editable sources/evidence and reports; `outputs/CTR52-compact-editable-source.zip` is the transfer copy for the existing checkout, retaining the exact Figure 1 SVG while the unchanged Figure 1 PNG/PDF remain in the complete local source package and checkout. The standalone 300 dpi PNG is supplied alongside PDF/SVG when the larger 600 dpi transfer is refused. `outputs/CTR52_DELIVERY_HASHES.json` records the exact commit and artifact hashes. The task technical-delivery document contains the exact source revision and confirmed attachment links to avoid a self-referential commit.

## Preservation and validation

Before editing, live project instructions and branch state were read, origin was fetched, and analysis-only path readiness and environment checks passed. The baseline was exactly the assigned commit. The snapshot `provenance/ctr52_before.json` covers 546 tracked files and all 74 currently untracked unrelated CTR39 files. Validation preserves 534 tracked files and all 74 unrelated files byte-for-byte; only 12 explicitly permitted existing presentation paths change. Raw data, CTR24 dictionary, final manuscript, root configuration, PI synchronization state and unrelated work remain untouched. No unrelated file was staged or moved. The current 74-file snapshot is measured live and does not substitute for predecessor task counts.

`provenance/ctr52_validation.json` confirms unchanged 75 tables, exact drawing-row and axis CSVs, QA retention, two self-contained embedded figures per preferred report and exact embedded export bytes. Pixel comparison of the 600 dpi figure proves that only the removed annotation rectangle changes and becomes white; every pixel elsewhere remains identical. PDF text extraction finds no flag/cirrus/cloud-probability text in the graphic. The visible caption and limitations retain the scientific caveat. `provenance/ctr52_visual_inspection.md` records actual opened PNG, PDF-derived render and browser captures, including all six panels. Supporting screenshots are retained in outputs.

## Reproduce

In the existing authorized project Git checkout with baseline history and existing project environments:

```bash
./scripts/check-env.sh
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr52_delivery.py
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr52_package.py
```

The package step requires the source/output files already committed. Figure drawing uses the unchanged base R/grDevices framework and safe generated-figure writer. Project Python uses only the standard library; pixel QA calls the worker's already installed system Python with Pillow 10.2.0. No software was installed and no dependency or lockfile changed. Quarto uses the investigation configuration, never the manuscript configuration. PDF creation metadata can change between runs while figure content remains identical. Source packages are for the existing authorized checkout, not a new repository and not a raw-data distribution. Upstream extraction and statistical scripts are not rerun.

## Validated caption

<strong>Figure 3.</strong> A–F: T1 terrestrial soil, T2 water, T3 seagrass, T4 intertidal sediment, T5 underwater vegetation and T6 underwater sand. Sen2Cor (blue circles, solid lines) and ACOLITE (orange triangles, dashed lines) show dimensionless reflectance at the same nine band positions. Positions follow wavelength with unequal spacing; lines guide the eye between sampled bands. Separate y-axis ranges are used for each target; both curves share one range within each panel. Smaller absolute differences are visually magnified, so panel heights cannot be compared as magnitudes. All six targets and all 108 values are shown, including nine negative Sen2Cor values. No band or paired comparison is missing. T2 carries a thin-cirrus classification despite zero cloud probability. Class names are supplied labels, and the spectra do not demonstrate correction accuracy.
