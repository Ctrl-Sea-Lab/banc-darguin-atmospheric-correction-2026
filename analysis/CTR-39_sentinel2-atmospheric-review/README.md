# Exposed intertidal sediment at low tide — revised CTR-39 review

Open **report.html** for the revised review. The principal recommendation is to start with Sen2Cor surface reflectance and test a focused land-surface alternative with careful exposure and moisture controls. No best processor for Banc d’Arguin is established.

The review now concerns exposed sediment, its moisture/texture and surface biological cover. Water-column retrieval is outside scope. ACOLITE remains a qualified surface-reflectance comparator, rather than the centre of a water-quality shortlist.

- `report.qmd` and `literature/literature_review.qmd`: current source.
- `library.bib` and `literature/references_index.csv`: 27 verified references, including 17 retained originals, nine added research papers and one official technical webpage.
- `literature/pdfs/`: 24 valid full-text PDFs, including all nine added papers. PDFs and extracted texts are excluded from Git and distributable source bundles.
- `tables/evidence_matrix.csv` and `outputs/numerical_claims.csv`: source passages and claim traceability.
- `literature/search_log.md`: revised search, selection, access and caveats.
- `scripts/build_library.py`, `scripts/restore_pdfs.py`, `scripts/audit_review.py`: reconstruction and validation.
- `provenance/previous-water-review/`: preserved earlier report and evidence records; complete earlier checkout remains at `.task-worktrees/CTR-39-final/` relative to project root.
- `provenance/intertidal_review_response.md`: response to the two CTR-45 corrections.
- `task.yml`: completed internal review. Karl Popper’s [focused CTR-46 recheck](/CTR/issues/CTR-46#document-independent-review) accepted exact corrected submission `1d9f5bc97ca79a4053860f508a31a1b3f0e981b4`; both CTR-45 findings are resolved.
- `provenance/independent_recheck.md`: attributed copy of the independent verdict, document revision `0274ae1d-ac6a-46e9-b195-d21c164a92fe`. Subsequent changes concern administrative status and provenance only; acceptance remains bound to that corrected submission.

Render from the task worktree with `./scripts/render-analysis.sh analysis/CTR-39_sentinel2-atmospheric-review`. The task-local configuration produces standalone HTML. Do not use manuscript configuration.

The shared root bibliography and final manuscript are unchanged. PI scientific approval and manuscript integration remain separate.
