# CTR-64 atmospheric correction review

Preferred fifth: C2RCC, retaining Sen2Cor, ACOLITE, POLYMER and MAJA. This is a literature/documentation recommendation, not a local accuracy ranking.

Open report.html for the complete readable report. Method/local-requirements/candidate/output/claim/source/search/reference tables are provided as CSV and included selectively in HTML. The protected root bibliography is unchanged; library_additions.bib is ready for the required synchronization workflow.

Reproduce the existing report without retrieving literature:

    scripts/render-analysis.sh analysis/CTR-64_sentinel2-atmospheric-correction-review

The source cache and local PDFs are intentionally excluded from Git/transfer artifacts. Full verification requires retrieving lawful sources into a fresh copy with acquire_evidence.py and acquire_supplement.py, or restoring project-local PDFs using reuse_prior_library.py <project-root>. Retrieval failures are expected and must be retained; do not bypass access controls. Source bytes are immutable: the acquisition helper refuses to overwrite a different existing source. Sources fetched later may differ from the review-date snapshots, whose hashes are in the manifest.

build_review_tables.py rebuilds the investigation tables and the task-owned project literature index/synthesis; inspect the latter before rerunning in a shared project with newer library edits. It reads but does not edit root library.bib. validate_review.py performs author audits, including source and PDF identities; it does not constitute independent review.

Seventeen scholarly PDFs were retained locally from nineteen verified scholarly references. Original source URLs and metadata remain available in the CSVs. Copyrighted full texts and downloaded processor source/license files are not redistributed in the archive.

CTR-65 returned Minor Revision for initial submission 943ee59. The corrections and focused verification are described in outputs/author_response.md. Focused reconsideration and PI scientific approval remain pending. Historical development provenance is separate from the content-bound submission record in provenance/submission.json. Installation, imagery processing, manuscript integration, merge and publication are outside this review.
