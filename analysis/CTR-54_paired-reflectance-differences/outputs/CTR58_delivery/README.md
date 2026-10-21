# Paired Sentinel-2 reflectance differences

This investigation compares ACOLITE and Sen2Cor, without a ground-truth accuracy claim. Read `report.html` for findings and limitations, `METHODS.md` for the full method, and `TABLE_CONTRACT.md` before modelling.

The bounded geospatial delivery is CTR-55 within investigation CTR-54. Scientific review and PI approval are separate and pending. No final-manuscript files are changed.

## Reproduce the final report and verification

Use this investigation's `_quarto.yml`; never render through the root manuscript configuration. Restore the repository environments with `scripts/bootstrap-env.sh`, then verify them with `scripts/check-env.sh`. No packages or toolchain versions were changed for CTR-58.

From the repository root:

```bash
./scripts/project-env.sh .venv/bin/python analysis/CTR-54_paired-reflectance-differences/scripts/ctr57_assemble.py
./scripts/render-analysis.sh analysis/CTR-54_paired-reflectance-differences
./scripts/project-env.sh .venv/bin/python analysis/CTR-54_paired-reflectance-differences/scripts/ctr58_validate.py \
  --products /mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026/analysis/CTR-54_paired-reflectance-differences \
  --env-root /mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026
```

The two explicit roots identify the durable scientific rasters and the single existing locked project environment. For a restored clone, supply its matching environment root and the approved product location. Both lockfiles must match byte for byte. The validation script reads scientific products and raw inputs, writes only CTR-58 provenance, and uses temporary local SSD space. It hashes and checks all 113 stored rasters, checks 142 input sizes/mtimes, rehashes three raw B2 files, recomputes 12 source pixels and 12 temporal statistics from all 22 dates, audits full-resolution SD saturation, and reruns all compact statistical models and influence fits. It does not repeat raster processing or the original 22.24 GB raw-input hash pass. Metadata equality alone is not renewed cryptographic proof of unsampled raw content. Original full-run evidence remains in provenance.

`ctr57_assemble.py` verifies the recorded exact upstream hashes before generating the two report tables and numerical claim ledger. When upstream Git objects are present it also verifies Git bytes. A fresh focused checkout can use the committed source manifest without carrying unrelated investigations' history. This is provenance verification, not scientific approval.

An optional browser audit, `scripts/ctr58_display.py <investigation> <previous-report.html>`, uses the worker's installed Chrome and system websockets tooling, outside the scientific environment. Its previous-report argument is the original geospatial HTML from scientific revision `1bbb23b3b94e775a60aa921f8c9c4f86f51926cb`. This audit is optional for report rendering and scientific reproduction. Recorded browser measurements and screenshots are in `provenance/ctr58_display*`.

## Rebuild scientific outputs only when necessary

The author pipeline `scripts/run.sh` is retained unchanged for geospatial reconstruction. It writes the original geospatial report through `07_report.py`; run it only in a separate investigation copy, then restore the final writer's `report.qmd` and use the report commands above. Do not run it over a reviewed writing candidate. Statistical reconstruction uses `scripts/ctr56_run.py`; the bounded audit instead runs the unchanged model script into temporary scratch and compares every numerical output table.

The default raw source is `/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026/data/raw/S2`. `CTR54_SOURCE` can select an authorized relocated source. `CTR54_SCRATCH` selects SSD scratch (budget 12 GiB and approximately 1.5 GiB process RAM for full raster reconstruction). `CTR54_PYTHON` can select the already restored shared project Python with identical locks. All science uses full-resolution inputs and single-threaded GDAL JP2 decoding; the full raster pipeline may take tens of minutes on the NAS.

## Review package

CTR-58 uses a focused branch based on the existing `ctr-22-project-initialization` branch, which provides the identical scientific lockfiles. Its pull request is stacked on that branch and adds only this investigation. Upstream initialization acceptance and the investigation's independent review remain separate prerequisites; no merge is authorized. Source/output manifests distinguish original author evidence from CTR-58 checks. Large rasters and raw data remain outside Git and the portable package; permanent products are retained on the NAS and bound by SHA-256. The package contains the standalone embedded HTML plus accessible full-resolution figures, scripts, tables and provenance.

## Files

- `outputs/paired_differences/`: 88 native-grid per-date/band difference GeoTIFFs.
- `outputs/temporal/`: median, sample SD and valid-count rasters, plus footprint counts and coverage-domain masks.
- `tables/`: acquisition inventory, wavelength/decoding contract, per-date summaries, mask counts, temporal coverage, clipping audit and numerical validation.
- `figures/generated/`: eight-map PNG/PDF and caption.
- `provenance/`: metadata snapshots, versions, lockfile hashes, resource estimate, input/output manifests and handoff.

Large generated rasters are intentionally outside Git tracking; SHA-256 manifests bind them to the recorded analysis revision. Preserve their durable NAS paths and task artifacts together with the tracked scripts. Display `.bin` bridges can be regenerated and are not required for interpreting the GeoTIFF products. All statistics use full-resolution data.
