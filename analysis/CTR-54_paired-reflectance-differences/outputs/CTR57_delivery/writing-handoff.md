**Take-home message:** The standalone scientific report is ready for the existing execution and independent-review chain. ACOLITE reflectance is lower than Sen2Cor on most matched dates, but the sparse series and quality sensitivity support descriptive temporal curves only.

**Meaningful results:** Integrated the revised eight-map figure, two-panel GAM time series, publication-quality methods/results, two source-derived summary tables, a numerical claim ledger, six verified methodological documentation citations, limitations and reproducibility information. Date-level medians are −0.00962, −0.00924, −0.00751 and −0.00935 for B2/B3/B4/B8; these remain distinct from map-level summaries. No accuracy ranking or ecological-change claim is made.

**Issues and limitations:** Twenty-two irregular acquisitions and absent ACOLITE flags on both March 2026 dates limit inference. Independent review on CTR-59 and PI scientific approval remain pending. Source-data hashing, raster processing and model computation are reused from the exact upstream evidence, not represented as rerun by the writer.

**Implications and next steps:** This completes the bounded writing task. Alan on [CTR-58](/CTR/issues/CTR-58) should consume the immutable writing candidate, verify execution and actual display, prepare the exact review package and authorized PR, then hand off to Karl on [CTR-59](/CTR/issues/CTR-59). The overall investigation is not yet scientifically complete. Manuscript integration, merge and publication remain separately unauthorized.

## Exact revision and sources

Writing candidate: `f79b98cdd810c2ffada1479dd0bddc3d34e22341`, local branch `ctr-57-scientific-report`. Worktree: `/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026/.task-worktrees/CTR-57/`.

Geospatial science: `1bbb23b3b94e775a60aa921f8c9c4f86f51926cb`; map candidate: `8dc80d7141d8c4482b8e36ee00f4cee4c9bf8e04` (manifest from handoff `2f69c2311f1ca9956845e3896d25d678619e597e`); statistical science: `f1ae24ad409ae31f82cad4fd1767ed9861145fbf` (handoff `a1e75bc`). The writing branch combines both upstream histories without conflict. Fetched origin/main remains `0085c9b`; existing project working trees and untracked products were preserved. No final-manuscript or protected path changed; no push, PR, merge or publication was performed by this task.

Permanent snapshot: `/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026/analysis/CTR-54_paired-reflectance-differences/outputs/CTR57_delivery/`. It preserves prior canonical and CTR-56 reports. `report.qmd`, `report.html`, `library.bib`, `report.css`, `task.yml`, scripts, tables, figures, provenance and source handoffs are available there and in the portable package. The package excludes raw data and large scientific rasters, which remain in established project storage.

## Checks and actual display

- Consumed table/figure/manifests match exact upstream Git bytes; 528 unique domain rows and 88 primary rows checked. Date medians/extrema/signs, map coverage, sensor counts, date gaps and influence dates independently recomputed from author tables. All reported diagnostics/sensitivities retained in `tables/ctr57_claim_ledger.csv`.
- Final HTML embeds both figures, resolves six methodological citations and has valid full-resolution links. The report renders through the investigation-specific configuration using `scripts/render-analysis.sh`.
- Installed Chrome measured the revised map at **1376 CSS px in a 1440 px viewport** and **1600 CSS px at 1920 px**, versus **798.984375 CSS px** previously. The final 390 px viewport has no page overflow. Writer inspected the desktop screenshot; final screenshots, measurements and browser audit script are retained. Alan must independently check the final exact package.
- All SD anchors and per-band saturation percentages are incorporated from Roger’s unchanged map-v2 evidence. Full-resolution map PNG SHA-256 is `ca9d6e599cd98e875bc04e4602eece1b480d222f721658e654afbd53ecaae0be`.
- All 34 repository policy tests passed; project environment check passed; no dependency/lockfile changes. Exact-candidate PI contribution guard against source handoff `a1e75bc` passed with no protected changes. Working tree is clean.
- Writer checks are not independent scientific review or authenticated PI approval. The optional display audit uses the worker’s installed browser/system tooling; it is not a scientific package dependency.

## Saved files on CTR-57

Use the file chips on this issue. Their confirmed project-workspace references use `4428c5e5-ad6b-4a27-a3bd-e9e4c94916a9`. No invented direct file endpoint or new human-open confirmation is claimed. The HTML multipart attempt returned HTTP 409 with an indeterminate host-bridge timeout; the attachment list was then empty and the upload was not retried. Project-file work products are the confirmed access route, established earlier by CTR-60/CTR-61.

| Deliverable | Work product | Bytes | SHA-256 |
|---|---|---:|---|
| CTR-57 standalone scientific HTML report | `2c52630d-3e9a-4b7e-be3d-04658019237d` | 4870217 | `a1ba565a3729a1b64e25f62c2c40979d9eaa4a71e8814be76d5e01fa38c0db84` |
| CTR-57 complete writing review package | `e9618323-5db5-467f-9141-9e8521e5c244` | 40960237 | `7897b93011b84764ab2f0961501d63ad7241560d34a58d7b5b9e99eacceb32bb` |
| CTR-57 editable source and numerical traceability | `196e3194-de1a-4d63-8cf6-392f9961b207` | 932347 | `af2c27d4304da4b3a32c1ccb1c9ef669fc5253925f9f89e072a5c1c081e35fa3` |
| CTR-57 revised eight-map figure — full-resolution PNG | `8eeb97b9-de95-41d9-b810-570a206e66ec` | 17602104 | `ca9d6e599cd98e875bc04e4602eece1b480d222f721658e654afbd53ecaae0be` |
| CTR-57 revised eight-map figure — PDF | `c028b060-61a8-4a7c-afb8-ff52e32f1ed5` | 12965942 | `b202c1ffa79365b4d332a70d0507cbf999777f0961d0b2038f0a542a64523d3d` |
| CTR-57 two-panel temporal GAM figure — PNG | `b078a854-85d6-4451-bf26-58057fd879f9` | 251105 | `2b820b0b477e72c33324c0550e16cef2febbaf27b5873e055d41734ff6793aef` |
| CTR-57 two-panel temporal GAM figure — PDF | `de91581d-77f1-4060-a232-c61e0350d90e` | 27314 | `d3dc35bc1809a3750231e245b0293bb8d4c619bd46342cd6115845ecea9f5550` |

The complete archive contains 156 files and passed ZIP integrity and required-content checks. `delivery.json` records each enclosed file hash and the writing revision. The HTML SHA-256 is `a1ba565a3729a1b64e25f62c2c40979d9eaa4a71e8814be76d5e01fa38c0db84`. Exact raw-input, upstream-output and statistical manifests are retained; scientific rasters were not recopied or modified.
