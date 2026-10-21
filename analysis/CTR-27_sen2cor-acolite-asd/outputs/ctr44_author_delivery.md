**Take-home message:** The requested figure/report amendment is implemented for exact-revision review. Both 7 March 2026 correction series are visible at all nine band positions for all 13 retained stations. ASD was measured 20 days later; B08 ASD remains NA. Zero validation-eligible pairs and all physical/QA holds are retained.

**Meaningful results:** Figure 1 PNG/PDF/SVG remain byte-identical to the recovered CTR41 baseline. Its supplied table and original source attachments retain their values, date limitations, three-class mapping, shared Sand symbol and requested legend placement. The former three-band scatter, its dedicated metric tables and narrative, previous station artifacts and obsolete report generators are removed from active delivery. They remain recoverable in Git. Figure 3 contains six primary stations; Figure S1 accounts for seven supplementary stations without changing their scientific status.

**Issues and limitations:** All 234 satellite values are present; the primary SRF view has 104 finite ASD values and 13 B08 NA entries. Operational SCL flags affect 109 satellite rows and are shown as rings. The dates differ by 20 days; pixel support, exposure, registration and representativeness remain unresolved. No statistics, extraction, integration, inference or processor ranking was added. The supplied Figure 1 does not provide a verified March7 acquisition date and is not relabelled as that result.

**Implications and next steps:** Charles must route the exact final revision through native Rachel presentation review, then Karl independent scientific review on CTR38. Prior presentation acceptance does not approve this revision. No PI approval, manuscript integration, merge or publication is claimed.

## Deliverables and verification

- Editable `report.qmd`, source template, standalone `report.html` and compact `report-portable.html`.
- Retained Figure 1 and two new station plates as 600 dpi PNG plus vector PDF/SVG.
- Unchanged CTR42/CTR43 numerical evidence, complete 15-station accounting and reason-coded NA/holds.
- Current regeneration and validation entry points, approved environment/lock context and current manifest.
- Complete, source/table and portable report ZIP packages.
- Explicit plotting-row audit of 351 primary-role rows, including 338 finite reflectances, original segment boundaries, QA flags and all dates; direct R-to-source serialization check.
- Checks of all 7 CTR43 table hashes, all 11 CTR42 CSVs, three retained Figure 1 export hashes, original PI attachment bytes, all HTML links/resources and identical offline main content.
- Full visual inspection of Figure 1 and all 13 new station panels. Initial clipped ylabel and overlapping supplementary legend were corrected before final inspection; common scales, isolated B8A ASD points and B08 gaps are visible.

The 60 pre-existing CTR39 baseline files remain present; 19 were independently changed while CTR39 had an active run. Both before/current hashes are recorded. CTR44 writes were confined to the existing CTR27 folder; no CTR39 file was restored, removed, stashed or staged. The workspace preflight therefore remains a real restriction on proposing a PR. No bypass was attempted. A local commit and inspectable draft PR description are supplied instead. Charles can coordinate workspace ownership before a real PR is proposed.

Exact commit and final package SHA-256 values are recorded in the Paperclip figure-delivery document, outside the committed files they identify. Reproduction preserves QMD, PNG and SVG content; PDF creation metadata/package timestamps may vary. This is author QA, not independent scientific review.
