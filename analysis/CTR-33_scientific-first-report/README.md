# CTR-33 editorial submission

The editable `report.qmd` and standalone `report.html` present the March 27
feasibility/descriptive investigation with the science first. The source is
`analysis/CTR-27_sen2cor-acolite-asd/` at
`9f0f06d2b5958b35de82adbca1577e4c384ae846`, associated with CTR-28 author document
revision `7f45ae7b-2969-4c9e-8b83-51250fc21432`. All 73 tracked source files and
both environment lockfiles are preserved byte-for-byte. The task directory was
initialized from `analysis/_template/`; no protected paths were changed.

The dedicated branch is `ctr-33-scientific-first-report`, stacked on
`ctr-28-matchup-feasibility` (draft PR #3). Its PR must target that branch to
isolate the presentation changes from the unmerged source investigation.
Do not merge either PR under this task. A later source change requires an
explicit scientific reconciliation and affected review checks before final review.

## What changed

- A 150–250 word scientific summary leads with existing product-difference
  magnitudes, spectral range, interpretation, material limits and next steps.
- Findings, interpretation and limitations precede concise Materials and Methods.
- All 21 original report body blocks remain; bulky metadata, exact commands,
  versions, historical decisions and the held design contract are in the appendix.
- All original tables, figures and captions are retained. Relative figure paths
  are rebased, and the legacy SRF image now has concise alt text.
- A new presentation-only generator owns this separate report. The original
  generator and its scientific scripts remain unchanged and cannot overwrite it.

## Evidence

`tables/content_map.csv` accounts for every original heading/body, with body
hashes before path rebasing. `tables/claim_evidence.csv` traces new framing to
existing outputs and lists interpretation limits. `outputs/source_preservation.json`
records every original file and lock hash. `outputs/figure_checks.json` records
embedded-image identity and caption checks. `provenance/preservation.json` records
the exact QMD/HTML hashes, input preservation and checks actually executed.

The author checks verify all retained figures and output bytes, six leading mean
differences and spectral values against the existing tables, all original text
bodies, standalone embedding, and all five alt attributes. No scientific
computation was rerun. Thirty-one small raw-input hashes match their recorded
values; all 894 raw-file size/mtime tuples remain unchanged. Rasters were not
read or fully hashed. The 34 existing preservation tests passed; their deliberate
guard-failure fixtures are not failures of this submission.

`outputs/browser-checks/` contains a Firefox first-page screenshot and four
screenshots of exact figure/caption DOM fragments extracted from the rendered
report, using its embedded CSS. Fragment screenshots were used because initial
headless captures at page anchors did not reliably wait for image layout; those
initial captures were discarded. These checks do not replace Rachel's independent
first-minute read or Karl's review. The author visually inspected the four
principal source images and all four rendered figure/caption fragments.

## Rebuild and check

From the project root:

```bash
python3 analysis/CTR-33_scientific-first-report/scripts/build_report.py
./scripts/render-analysis.sh analysis/CTR-33_scientific-first-report
python3 analysis/CTR-33_scientific-first-report/scripts/verify.py
python3 -m unittest discover -s tests -p 'test_*.py'
```

The presentation generator fails if the original report differs from its pinned
Git revision. Only text, source tables and existing image bytes are read. To repeat
the optional raw-preservation checks, add `--raw-root /path/to/source-checkout`
to `verify.py`; it uses the retained `provenance/raw_stats_before.json` snapshot.
File mtime checks are local preservation evidence, not portable identity checks.
Input hashes remain the byte-identity evidence for small inputs.

No dependency or lockfile changed. The initial worktree synchronization wrapper
attempted a frozen Python environment restore; it was stopped, its partial
environment removed, and an ignored `.venv` symlink uses the existing project
environment. Readiness was verified with the existing environment against the
actual analysis-only paths. No system software or R environment was changed.

## Source-review reconciliation and gates

During this task, Karl accepted the exact expanded source in CTR-28 review revision
`19a802d4-b1fa-4e67-b376-570dc689d939`. The authenticated PI comment
`22aa93c7-ae6a-4bd4-8bb5-970069b954c8` approves the immediately preceding exact
expanded source submission; decision document revision
`69563c8a-c599-4898-a7ba-e644c54a4d48` records that limited association.
The source advanced to Charles's coordination stage. Exact retrieved records are
preserved in `provenance/source_state.json`, `source-independent-review.md` and
`source-pi-decision.md`. No substantive scientific revision was requested.

The two non-blocking source editorial findings are addressed in this presentation:
historical pending labels are explicitly contextualized, and legacy SRF alt text
is added. The approved source artifact itself is unchanged. Its decisions do not
approve CTR-33. Rachel, Karl and Charles must review this exact rewritten revision
through the task's native stages before its PI-review package is complete.

Zero admitted ASD-validation pairs and B08/support/location/overpass/QA/grouping
holds remain. No correction ranking, ecological identity or causal conclusion was
added. Manuscript integration, merge and public publication remain unauthorized.
