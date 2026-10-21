# Station matchup report

Open **report.html**, a standalone report, or edit **report.qmd**. This is the CTR-41 relocation of CTR-38's delivered report into the existing CTR-27 folder. Original CTR-27 processing is stopped.

From the repository root:

```bash
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr38_figure3_revision.py
./scripts/render-analysis.sh analysis/CTR-27_sen2cor-acolite-asd
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/validate_delivery.py
```

These commands use saved small tables and original supplied attachments. No raster extraction or spectral integration is performed. The ctr37 scripts are preserved upstream manifest dependencies; do not execute them as part of this delivery.

All source tables preserve their original values and labels. `provenance/source/` retains frozen source manifests. The current presentation manifest is regenerated at `provenance/ctr38_figure3_manifest.json`. The new revision remains pending CTR-38's presentation and independent scientific review.

Recovery: complete prior contents, including ignored unique files, are preserved at `.git/ctr41-recovery/CTR27-before-dc6db713.tar.gz`; tracked contents are available at commit `dc6db713a5179422b6ad94629472cd37f9bb32e8:analysis/CTR-27_sen2cor-acolite-asd/`. Extract into a separate recovery directory and compare inventories before any restoration. Source dictionary files are unchanged.
