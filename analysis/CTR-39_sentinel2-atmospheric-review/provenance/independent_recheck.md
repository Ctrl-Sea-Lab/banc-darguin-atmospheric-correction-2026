# Independent recheck — archival copy

Copied without changes from Karl Popper’s [CTR-46 review](/CTR/issues/CTR-46#document-independent-review), document revision `0274ae1d-ac6a-46e9-b195-d21c164a92fe`, saved 20 October 2026. The verdict applies only to the source revision named below.

---

**Take-home message:** **Accept**, for source revision `1d9f5bc97ca79a4053860f508a31a1b3f0e981b4`. Both limited corrections requested in [CTR-45](/CTR/issues/CTR-45#document-independent-review) are resolved. No unresolved critical, major, minor or editorial concern was identified within this focused recheck.

**Meaningful results:** The corrected synthesis accurately preserves Zarzuelo’s conflicting tidal-selection statements without inventing a stage-specific rule. Doxani’s section locator is correct. Independent reconstruction reproduced the submitted outputs byte for byte.

**Issues and limitations:** Zarzuelo’s internal ambiguity remains a limitation of the source. The review establishes faithful reporting and reproducibility of this literature revision, not the accuracy of any processor at Banc d’Arguin. The unchanged scientific synthesis relies on the earlier revision-specific review plus the present diff and correction checks; this was not a fresh review of every cited study.

**Implications and next steps:** No further author correction is required for M1 or E1. Charles Darwin owns coordination for PI consideration. This recommendation grants no PI approval, manuscript integration, shared-bibliography promotion, merge or publication authorization.

## A. Review identification

- Review: [CTR-46](/CTR/issues/CTR-46), task UUID `f560e06e-5c55-434c-a44e-9eba55c2b222`; parent [CTR-39](/CTR/issues/CTR-39).
- Project: [Atmopheric correction of the Banc D'arguin 2026](/CTR/projects/5fc298b7-b03d-4a03-b14f-25b3e66ccf85), UUID `5fc298b7-b03d-4a03-b14f-25b3e66ccf85`.
- Repository: `Ctrl-Sea-Lab/banc-darguin-atmospheric-correction-2026`, local root `/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026`.
- Exact submission: **`1d9f5bc97ca79a4053860f508a31a1b3f0e981b4`**, submitted on `ctr-39-intertidal-revision`; no remote push or merge verified or claimed.
- Previously reviewed base: `af8b45637a838d66ab6e53d08f154a93fc82817a`; prior review document revision `95a57167-dbf5-43af-9f76-445f78cdeae2`.
- Investigation: `analysis/CTR-39_sentinel2-atmospheric-review/`.
- Author: Rachel Carson. Independent reviewer: Karl Popper. Date: **20 October 2026**. I reviewed the preceding submission but did not author or edit this analysis or its corrections.
- Isolated verification checkout: `.task-worktrees/CTR-46-review/`, detached at the exact submission. Both review and author HEAD were verified.

Materials examined: author response; full nine-file diff; corrected narrative and rendered report; authoritative notes; search log; generated reference index and evidence matrix; source manifests; numerical-claim record; build/audit scripts and imported snapshot code; report configuration; environment/lockfiles; protected-file and snapshot manifests. Primary-source inspection covered Zarzuelo PDF pp. 7 and 12, with p. 5 for section/stage context, and Doxani PDF p. 9. The three requested PDF pages were also visually inspected after local rendering.

## B. Overall assessment

The revision resolves the prior concerns without changing the exposed-sediment question, processor recommendations or numerical claims. The low-tide scope remains explicit. Sen2Cor remains a starting point for local testing; comparative superiority remains unestablished. Successful reconstruction supports computational consistency, independently of the source interpretation checks.

## C. Strengths

- Both source statements and their locations are visible together, including in the first comparison table.
- The source’s uncertainty is retained rather than resolved by an unsupported explanation.
- Authoritative notes and generated records agree, and the limited revision preserves prior evidence and approval boundaries.

## D. Critical and major concerns

**None identified within scope.** No statistical model, spatial analysis or local performance result was added or altered; no new statistical or spatial validation was required for these corrections.

## E. Minor and editorial concerns

**M1 — Minor, resolved.** In `literature/literature_review.qmd:41,45`, `outputs/intertidal_notes.json:46–48`, `literature/search_log.md:39,46`, the generated Zarzuelo records and rendered HTML, the author now records both intermediate-tide retention (§3.1, PDF p. 7) and restriction of habitat zonation to low tide (Discussion, PDF p. 12). Inspection of §2.2.2–2.2.3 on p. 5 supports distinguishing extent detection and subsequent habitat classification, but does not establish a definitive allocation of the conflicting tide rules. The revision correctly leaves that relationship unclear. No correction remains. Source: [Zarzuelo et al.](https://doi.org/10.1016/j.jag.2025.104676), inspected from the local hash-verified PDF.

**E1 — Editorial, resolved.** `outputs/intertidal_notes.json:34` and both generated Doxani records now point to **§3.1.3, PDF p. 9**. That section contains the Sentinel-2 surface-reflectance exclusions and the discussion of reference/processor differences, including radiative-transfer and adjacency treatment. Only the locator changed; the scientific summary remains unchanged. No correction remains. Source: [Doxani et al.](https://doi.org/10.1016/j.rse.2022.113412), inspected from the local hash-verified PDF.

## F. Reproducibility verification

**Executed in the isolated checkout:**

```bash
python3 scripts/pi_sync.py --repository . verify-ready \
  --task-id CTR-46 --agent karl-popper \
  --path analysis/CTR-39_sentinel2-atmospheric-review
python3 analysis/CTR-39_sentinel2-atmospheric-review/scripts/build_library.py
./scripts/render-analysis.sh analysis/CTR-39_sentinel2-atmospheric-review
python3 analysis/CTR-39_sentinel2-atmospheric-review/scripts/audit_review.py
```

All exited 0. The readiness gate returned `ready`, classifying this analysis path as unrelated to protected synchronization. Rendering produced no warning or citation error. Reviewer-owned `verify.py` separately checked inputs, changes, regenerated output equality and preservation; it is included in the evidence bundle with logs and machine-readable results.

| Independent check | Result |
|---|---|
| Source material | 24 PDFs match recorded SHA-256 values; copies of all 24 PDFs and 24 text extracts match the author checkout. PDF copies remain Git-ignored. |
| Library/audit | 14 resolved cited sources, 27 entries, 25 unique DOIs, 24 checksum/title-overlap-checked PDFs, two rendered comparison tables. These automated identity checks do not constitute a fresh scientific review of all 24 papers. |
| Regenerated outputs | Bibliography, reference index, evidence matrix, library summary, audit JSON and report HTML are byte-identical to the submitted commit. |
| Diff scope | Exactly nine changed files, all within the investigation. Only Zarzuelo and Doxani rows change in the derived CSVs; their cells match authoritative notes. No other conclusion or numerical claim changes. Bibliography, source records/PDF hashes, numerical-claim record and scripts are unchanged from the base. |
| Protected material | Seven files match the author checkout, base and submission: `index.qmd`, root `library.bib`, root `_quarto.yml`, `AGENTS.md`, `PI_CONTRIBUTIONS.md`, `uv.lock`, `renv.lock`. Six are in the submitted protected manifest; `PI_CONTRIBUTIONS.md` was checked additionally. |
| Prior snapshot | All 18 manifest entries match their hashes, the reviewed base and corresponding originals at `7307ab30119da204ec62baea1f7a805b19094ff5`. |
| Author preservation | All 113 stored investigation files, excluding transient caches, are unchanged before/after verification and match the independently rebuilt checkout. Both Git statuses are clean. |

Observed tools: Python 3.12.3, Quarto 1.10.19, Poppler/pdftotext 24.02.0. Build/audit scripts use Python’s standard library. No package installation or cold dependency restoration was performed. Local `pdftotext -layout` extraction and `pdftoppm` page rendering were executed for the requested source pages; the remaining extracts were checksum-copied, not independently regenerated.

**Limits:** No broader literature search, satellite processing, field-data validation, statistical refitting or published-result recomputation was performed. The report’s HTML structure and corrected content were checked; no browser screenshot assessment was performed. Attempts to open the two repository PDFs through the web tool failed (Doxani: tool size limit; Zarzuelo: HTTP 403). The locally available, hash-verified PDFs were fully accessible for the targeted inspection. Full PDFs/page images are not redistributed in the evidence bundle.

## G. Claims and evidence

| Claim | Assessment |
|---|---|
| Zarzuelo records intermediate-tide selection and separately limits habitat zonation to low tide | **Supported**, by the inspected source pages. |
| The relationship between those rules is clearly established by workflow stage | **Not established; correctly not claimed.** |
| Doxani’s relevant exclusions/reference caveats occur in §3.1.3, PDF p. 9 | **Supported**, by text and visual page inspection. |
| The limited correction preserves the low-tide sediment question and existing recommendations | **Supported**, by the complete diff and report inspection. |
| A best processor or performance gain has been demonstrated for Banc d’Arguin | **Not established and not claimed.** Local validation remains future work. |

## H. Final recommendation

**Accept**, bound exclusively to `1d9f5bc97ca79a4053860f508a31a1b3f0e981b4`. The prior M1 and E1 findings are resolved, no additional concern arose within the authorized scope, and required reconstruction and preservation checks passed independently.

This is a scientific reviewer recommendation, not a PI approval decision or authorization for downstream integration, promotion, merge or publication.

## I. Conditions for reconsideration

No further correction is required for this exact submission. Later substantive changes require reassessment of affected claims and evidence. The source ambiguity remains documented and must not be silently converted into a stage-specific tidal rule. Charles owns PI coordination; any subsequent author correction remains Rachel’s responsibility. This standalone review is complete without editing the author submission or posting to the parent thread.
