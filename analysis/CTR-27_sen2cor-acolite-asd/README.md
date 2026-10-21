# Preferred custom-axis report — CTR52 presentation amendment

Open `report.html` or `report-custom.html` for the PI-selected custom-axis report. The compact self-contained main download is `report-custom-portable.html` (also `report-portable.html`). Exactly two figures remain: unchanged Figure 1 and the six-target satellite spectral figure, with flag annotations removed from that graphic. QA fields, caveats, values, bands, targets and per-panel limits remain unchanged.

The historical common-axis alternative is retained byte-for-byte as `report-common.qmd`, `report-common.html` and `report-common-portable.html`; its figure exports are unchanged. Earlier packages and handoffs remain historical evidence.

Regenerate only the preferred custom delivery from the authorized project root:

```bash
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr52_delivery.py
```

See `CTR52_HANDOFF.md` and `provenance/ctr52_validation.json` for preservation and visual evidence. Charles routes the exact new author revision through Rachel then Karl under CTR38. This presentation edit does not confer scientific approval. CTR50 remains an unresolved workspace/PR prerequisite; no guard bypass, push, PR, merge, publication or manuscript change occurred.

---

Historical CTR44 instructions below apply only to that superseded delivery. Use the CTR52 command above for the current report.

# CTR27 station matchup delivery — CTR44 amendment

The report retains Figure 1 unchanged and replaces the station spectra with both 7 March 2026 correction products across all nine requested bands. ASD was measured 20 days later; B08 ASD remains NA. All comparisons remain exploratory with zero validation-eligible pairs.

Open `report.html` or the compact `report-portable.html`; edit `scripts/ctr44_report_template.md`, which regenerates `report.qmd`.

From the original authorized project root:

```bash
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr44_delivery.py
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/validate_delivery.py
```

The former `ctr38_figure3_revision.py` entry point routes to the current presentation. Do not run upstream extraction or numerical preparation to reproduce this delivery. The exact CTR43 tables are hash-checked and unchanged. Figure 1 PNG/PDF/SVG and original PI attachments are preserved. The reference-only R renderer is retained as source for Figure 1; ordinary regeneration preserves its exact existing exports.

Current packages: `outputs/CTR44_complete-delivery.zip`, `CTR44_source-and-tables.zip`, and `CTR44_portable-report.zip`. Current hashes and author QA are in `provenance/ctr44_manifest.json` and `ctr44_validation.json`.

The removed scatter, dedicated metrics and previous station plots remain recoverable at Git revision `51805d91ffdef5cafa81c11fd91a74163eec4d83`. Shared historical supporting evidence and frozen provenance are retained; prior manifests may reference removed historical files and are not current QA receipts. `ctr44_removed.json` records the active removals.

Charles coordinates Rachel presentation review, then Karl scientific review on the exact revision. No PI approval, manuscript integration, merge or publication is implied. The pre-existing clean-workspace guard must be resolved before an actual PR; CTR39 files are not deleted, stashed or bypassed.
