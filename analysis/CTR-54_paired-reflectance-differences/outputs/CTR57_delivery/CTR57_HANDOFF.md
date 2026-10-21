# CTR-57 scientific writing handoff

The standalone report integrates verified geospatial and statistical findings and the revised eight-map figure. Processor disagreement is predominantly negative, but the temporal evidence supports descriptive curves only. Independent scientific review and PI scientific approval remain pending.

## Exact inputs and report

- Consumed geospatial scientific revision: `1bbb23b3b94e775a60aa921f8c9c4f86f51926cb`.
- Consumed map candidate: `8dc80d7141d8c4482b8e36ee00f4cee4c9bf8e04`; map-file manifest comes from handoff `2f69c2311f1ca9956845e3896d25d678619e597e`.
- Consumed statistical scientific revision: `f1ae24ad409ae31f82cad4fd1767ed9861145fbf`; statistical handoff `a1e75bc`.
- Writing branch: `ctr-57-scientific-report`, isolated worktree `.task-worktrees/CTR-57` in the project repository.
- Exact report HTML SHA-256: `a1ba565a3729a1b64e25f62c2c40979d9eaa4a71e8814be76d5e01fa38c0db84`.
- Exact consumed-file hashes/revisions and writer checks: `provenance/ctr57_assembly.json`.
- Numerical traceability: `tables/ctr57_claim_ledger.csv`. Report tables are generated from verified source CSVs by `scripts/ctr57_assemble.py`.

## Writing and presentation checks

The report keeps temporal and spatial aggregation distinct, retains mask/coverage sensitivities and inconclusive model intervals, and makes no correction-accuracy or ecological-change claim. Two main figures remain visually sparse. The map caption defines both signs, all color anchors, NoData, observation counts, missing flags and saturation by band. The original scientific rasters/tables and manually edited assets were preserved.

All 528 date/band/domain keys and the 88 primary rows passed writer checks. Date extrema, medians, signs, temporal coverage, sensor counts, acquisition gaps and influence dates were checked. All consumed scientific table and figure bytes match their source commits. Two figures are embedded, six methodological documentation citations resolve, and local full-resolution PNG/PDF links exist. The targeted documentation verification is not an atmospheric-correction literature review; no publication PDF is applicable to these sources.

Installed Chrome measured map widths of 1376 CSS px at a 1440 px viewport and 1600 CSS px at 1920 px, compared with 798.984375 px in the preceding report. Final screenshots and `provenance/ctr57_display.json` retain the evidence; writer visual inspection confirmed enlarged panels and legible legends. A 390 px viewport has no page overflow after responsive wrapping fixes. `scripts/ctr57_display.py` is an optional browser audit using the worker's installed Chrome and system websockets tool; it is not required for scientific computations or rendering. Alan should independently repeat the display check on the final packaged candidate.

The standalone report renders through `scripts/render-analysis.sh` under its investigation configuration. Repository environment check and all 34 policy tests passed. No dependencies or lockfiles changed. Upstream raster/model computations and raw-input hashing were reused, not rerun by the writer. The initial gate wrapper attempted a frozen local environment restore; it was stopped and readiness was verified using canonical project Python. The first render preceded table assembly and failed; after assembly the final render passed. No scientific result was changed to satisfy a check.

## Next owner and approval gates

Alan's existing CTR-58 owns execution validation, final render and exact-candidate packaging/PR. Start from this writing branch; preserve source evidence. Verify the actual displayed width and full-resolution file access, not export DPI alone. Use `provenance/ctr57_assembly.json`, final HTML checks and screenshots plus the original computational evidence for bounded verification. Karl's CTR-59 owns independent scientific review after that handoff.

This bounded writing delivery does not complete the entire investigation. Internal review and authenticated exact-revision PI scientific approval remain pending; manuscript integration, merge and publication are separately unauthorized. No final-manuscript or protected path was changed. The Paperclip delivery record will identify the exact writing commit, persistent file receipts and package hashes.
