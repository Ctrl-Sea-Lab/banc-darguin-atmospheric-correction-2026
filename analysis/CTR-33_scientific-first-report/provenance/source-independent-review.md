Recorded source document revision: 19a802d4-b1fa-4e67-b376-570dc689d939

# Independent review — expanded feasibility and descriptive report

## A. Review identification

- Reviewer: Karl Popper. Author: Roger Tomlinson. Coordinator: Charles Darwin. The reviewer specified acceptance criteria in earlier reviews but did not author the analysis or its figures; no substantial authorship conflict.
- Review date: 20 October 2026 UTC.
- Paperclip project: `5fc298b7-b03d-4a03-b14f-25b3e66ccf85`, atmospheric correction of Banc d’Arguin 2026.
- Task: [CTR-28](/CTR/issues/CTR-28), `93ec8661-a983-4b74-9265-612f876599e6`; parent [CTR-27](/CTR/issues/CTR-27).
- Repository: [Ctrl-Sea-Lab/banc-darguin-atmospheric-correction-2026](https://github.com/Ctrl-Sea-Lab/banc-darguin-atmospheric-correction-2026), [draft PR #3](https://github.com/Ctrl-Sea-Lab/banc-darguin-atmospheric-correction-2026/pull/3).
- Exact reviewed commit: `9f0f06d2b5958b35de82adbca1577e4c384ae846`. Investigation: `analysis/CTR-27_sen2cor-acolite-asd/`.
- Reviewed submission: [data-readiness document](/CTR/issues/CTR-28#document-data-readiness), revision `7f45ae7b-2969-4c9e-8b83-51250fc21432`; report QMD/HTML, four new PNG figures and their R drawing code, descriptive Python code, validation script, summary/count/crosswalk/join/ledger tables, normalized design/contract/graph assertions, provenance and lock identities. All 68 files in the three delivered ZIPs were compared with committed bytes. Original ASD and both March 27 AOI tables were independently read; GPS workbook rows were independently decoded.
- Scope: reassessment of the requested descriptive expansion, its numerical/visual claims and held feasibility design. Comparison baseline: `30bf024d129b70191b0ba90193eedc45dfc69b6a`; previous review `41b37e06-40fd-471b-b7de-ef3e2d339803` remains in document history. This verdict covers no later code or scientific release.
- [PI approval comment](/CTR/issues/CTR-28#comment-22aa93c7-ae6a-4bd4-8bb5-970069b954c8), 20 October 2026 at 08:30:46.535 UTC, states “I approve !” after the exact expanded submission. Record this as approval of that feasibility/descriptive deliverable. Its source is the authenticated user comment, not this reviewer’s recommendation. It does not supply missing physical evidence or separately authorize manuscript integration, merge or public publication.

## B. Overall assessment

The expanded report now supplies the requested statistics and plots. Its numerical summaries reproduce, and the new displays accurately distinguish station-average spectra, broad-AOI product values and the absence of validated field matchups. The principal result is a defensible feasibility limitation alongside descriptive differences between supplied products.

The spatially dependent pixels support description of these two AOIs, not independent ecological replication or correction accuracy. Unknown QA, effective support and overpass comparability remain explicit. Retaining these holds is scientifically appropriate. The user’s approval is acknowledged without changing evidential standards.

## C. Strengths

The report retains all 15 spectra and all 1,463 paired AOI records per primary band. It preserves AC01/02 at their supplied coordinates, exposes the location discrepancy, and makes no nearest-neighbour substitution. Summary tables state sample SD, type-7 quartiles and the difference direction. Wavelength-channel spread is explicitly separated from repeat-level uncertainty. Counts distinguish 165 held design rows from zero admitted validation observations. No significance testing, fabricated uncertainty or correction ranking is introduced.

## D. Critical and major concerns

**No unresolved critical or major concern was identified within the submitted feasibility/descriptive scope.** This is not a finding that the parent validation study is ready.

Previous expansion requirements are resolved:

1. **Field spectra:** all 15 supplied station averages appear in primary and supplementary panels; all 15 channel-summary rows independently reproduce.
2. **Station/AOI map:** all original GPS rows and transforms agree with the crosswalk. The map preserves locations, shows actual supplied nominal cell footprints and AOI outlines, labels differing panel scales, and retains AC01/02 discrepancy.
3. **Paired correction and difference plots:** B02–B04 are displayed separately for Arel and Iwik with common axes, reference lines, explicit sign and unvalidated-QA warnings.
4. **Descriptive tables:** all 12 product distributions and six paired-difference summaries reproduce; exclusions are zero under the stated finite/special-code rule. This rule is not QA validation.
5. **Feasibility and delivery:** denominators remain explicit; zero station/AOI containing-cell joins and 165 excluded ledger rows are verified. The downloadable HTML, sources/tables and four PDFs match the exact commit.

Field support/position, AC01/02 reconciliation, overpass state, QA, upstream radiometric support and grouping remain material barriers to the parent study. They are disclosed limitations of an accepted missing-input decision, not silently waived requirements.

## E. Minor and editorial concerns

1. **Editorial, non-blocking — historical decision labels.** The submitted report and provenance say review/PI approval are pending because they predate this decision. This review and the linked PI decision record supersede those status statements externally. On a future authorized revision, update them with exact decision links; do not silently alter the approved artifact or imply that later revisions inherit approval.
2. **Editorial, non-blocking — legacy SRF image accessibility.** All four new images have alternative text. The fifth, pre-existing SRF image has an empty HTML alt attribute despite its visible explanatory caption. Add concise alt text at the next report revision.

## F. Reproducibility verification

[Download independent verification evidence](/api/attachments/ba48d46e-ae3b-45fc-b193-cca4bac70e51/content?download=1): reviewer-owned script, machine-readable results and execution notes. ZIP SHA-256: `85ae9ebe20493edf62e9450c75af2aee326d55d7e6139f501cfc7e10b1af68ae`.

The author checkout was clean at the submitted SHA and remained clean. An exact Git archive was extracted into a separate review workspace. No author analysis, raw data, protected path or environment was modified.

Executed:

- `git status --short`, `git rev-parse HEAD`, `git cat-file`, `git diff --stat` and exact-commit `git archive`. The expansion diff is confined to the investigation.
- `python3 review-CTR-28/expanded/verify.py`: independently recomputed all 33 rows using standard-library statistics and explicit linear quantiles, without importing the author’s numerical functions.
- `gdaltransform -s_srs EPSG:4326 -t_srs EPSG:32628` on coordinates independently read from original XLSX rows 110–124. This repeats projection arithmetic using GDAL; it does not independently validate GPS accuracy.
- Submitted `scripts/validate.py` in the isolated snapshot after inspecting its writes. Its initial missing-input failure was resolved by copying the existing separately downloaded `official-srf-v5.xlsx` into the snapshot. The validator verified its recorded hash and then passed. This dependency is not in Git; reproducibility requires the preserved or matching downloaded workbook.
- Downloaded all three final archives; verified their hashes and every member against committed bytes. Parsed the HTML and compared all five embedded PNG payloads with committed images. Visually inspected all four new figures.

| Independent check | Result |
| --- | --- |
| Summary rows | 33/33 agree; maximum absolute discrepancy `5.551115123125783e-17` |
| Paired AOI keys | 1,463 unique keys per correction; 730 Arel, 733 Iwik |
| Coordinates across correction tables | All paired centres identical |
| Primary-band differences | All 4,389 values negative; these repeat 1,463 cells across three bands |
| Original GPS identities/date/coordinates | All 15 agree with saved crosswalk |
| Saved projected coordinates | All 15 agree with rerun GDAL output |
| Station containing-cell joins | 0/15 |
| Nearest-centre distances | 15.8511382284–989.7149028641 m; agree within `1e-6 m` |
| Held ledger | 165 unique rows; all excluded; all three reflectance fields empty |
| Submitted consistency validator | Normalized identities/foreign keys, support/QA/null/graph assertions and input/image hashes pass |
| Delivered archives | 1 HTML, 63 source/table/provenance files, 4 PDFs match committed bytes |
| HTML identity | SHA-256 `d35fcd6fe6d0b33a29f99149f35f6206f768c3c836f8c12ae8a90f2c8ceb932d` |
| Used raw input preservation | Size, nanosecond mtime and full hash unchanged before/after reviewer reads |
| Environment identities | Submitted lock hashes match snapshot and current project; no restore/install performed |

The validator repeats some historical author assertions in its output. Its “144 scalar raster reads,” “36/36 source checks” and “34 preservation tests” are **not new reviewer executions**. No raw raster/QA reads, original polygon reconstruction, empirical registration, SRF numerical integration, R figure regeneration, Quarto/browser rerender, full-scene processing or correction rerun was performed. Whole-scene byte identity, full environment restoration and physical field comparability remain unverified.

Literature check: the official product page supports metadata-based L2A offset/quantification decoding and the distinction between operational and user-generated L2A; this does not authenticate the submitted scene’s entire processing lineage. [SentiWiki product documentation](https://sentiwiki.copernicus.eu/web/s2-products). The inspected current exporter writes dataset arrays with georeferencing and NaN nodata; current code cannot authenticate the historical ACOLITE build. [ACOLITE export source](https://raw.githubusercontent.com/acolite/acolite/main/acolite/output/nc_to_geotiff.py). The cited SRF announcement could not be retrieved in this review, so its date/version narrative was not independently revalidated. The preserved workbook hash was checked; its response integrals were not recomputed. These limits do not change the reproduced descriptive results or justify releasing held bands.

## G. Claims and evidence

**Supported:** the supplied 15 station-average spectra and their channel summaries; descriptive product/difference summaries for the exact AOI tables; lower supplied ACOLITE values in every B02–B04 pair; a larger absolute discrepancy in Arel in these records; zero containing-cell joins at supplied GPS coordinates; zero admitted field pairs; accessible exact-commit figures and tables.

**Partially supported:** the proposed design is a structured basis for later extraction, with normalized identities and explicit holds. Full source provenance, native support, QA and eventual independent-unit grouping require additional evidence.

**Unsupported and appropriately not claimed:** superiority or accuracy of either correction against ASD, equal field/overpass optical conditions, causal explanations for AOI differences, ecological population inference or independent sample size derived from pixel counts.

## H. Final recommendation

**Accept — bounded feasibility audit and descriptive report at commit `9f0f06d2b5958b35de82adbca1577e4c384ae846`.**

The requested expansion is complete and its principal descriptive results withstand the independent checks above. The two editorial points are non-blocking. Acceptance does not certify a completed ASD validation. The authenticated PI approval is recorded separately from this independent recommendation. Proceed to Charles’s existing coordination review stage.

## I. Conditions for reconsideration

No additional author amendment is required to accept this deliverable. Future changes to data, figures, computations or scientific interpretation need review of their own exact revision. Before the parent study makes field-performance claims, resolve or explicitly bound the material support/location/overpass/QA/grouping conditions, freeze the common extraction/complete-case rules, and independently verify released matchups. B08 remains held.

Charles should retain the parent’s field-validation block while coordinating the accepted feasibility result and PI decision. Manuscript integration, merge and public publication retain separate authorization gates. The full review and evidence are available here to Charles and the PI.
