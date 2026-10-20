# CTR-34 execution amendment to CTR-27

Current conclusion: no justified primary matchup under the dated support/exposure contract. All 18 intended B02–B04 pairs are held; 165 historical dispositions remain auditable. AC03/04 are PI-excluded mud targets. No ASD errors, pooled estimates or correction rankings were computed. Karl reviews the exact delivery, then Charles reconciles; PI scientific approval is pending.

Open `report.html` for the self-contained current report. `report.qmd` is editable. All current CSV/JSON results have `ctr34_` prefixes. Unprefixed CTR-28 artifacts and the separate CTR-33 report are historical; their old 8-primary/24-candidate and all-15 spectra populations are not current. Historical originals are preserved in Git.

The bundle preserves repository-relative paths. Restore it into an isolated checkout of the private authorized repository at the exact delivery commit shown in the bundle manifest/task outcome. The bundle omits raw field/raster data; those remain read-only on the authorized NAS. It includes the separately retained official v5 reference cache; its SHA-256 must be `42be3ebd8bfcbde11c37caeb2e2fdda65fefa8d2b6f8329559b7806d02cdc9e2`. V4 is primary. Use the existing locked canonical project environment; do not create system installs or a second project environment.

From the isolated repository root:

```bash
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr34_validate.py
# A bounded repeat requires byte-identical numerical/schema/metadata artifacts.
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr34_reproduce.py
Rscript --vanilla analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr34_figures.R analysis/CTR-27_sen2cor-acolite-asd /tmp/ctr34-figures
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr34_publish_figures.py
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr34_report.py
./scripts/render-analysis.sh analysis/CTR-27_sen2cor-acolite-asd
```

`ctr34_freeze.py` is the original pre-value decision creation script and refuses to overwrite the contract. Routine reproduction uses the committed frozen contract as input. If independent review changes the scientific decision, preserve this version and issue a dated amendment before a revised export. No exact-review or PI approval is implied by rerunning technical checks.

Null CSV fields mean unknown/not evaluated/not applicable according to reason/status; never zero or a QA pass. Parse `True`/`False` explicitly. `ctr34_held_diagnostics.csv`, convolved references and raw decodes are HELD DIAGNOSTICS ONLY; `ctr34_eligible_pairs.csv` is intentionally header-only. QA witness coordinates in the deduplicated cell table are not target ownership; use many-to-many QA links. Stored extraction weights (=1) are separate from null statistical weights and unknown upstream contributor weights.

Source identity distinguishes full small-file SHA-256, decoded original-image window hashes, and raster header/path/stat evidence. Full raster bytes were not hashed. The raw-preservation test covers all 894 paths/sizes/mtimes plus full small-file hashes and repeated source-window identity. The selected 3×3/5×5 offset windows do not estimate GPS accuracy or establish a native support bound.

The science amendment reuses CTR-33's scientific-first order and compact styling while changing only the parent investigation files. Its branch starts at `86e0d6c`; CTR-33 files/branch remain unchanged, and CTR-33 review does not approve this amendment. No manuscript file, protected merge or public publication is authorized.
