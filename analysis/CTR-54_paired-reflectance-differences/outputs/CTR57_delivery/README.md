# Paired Sentinel-2 reflectance differences

This investigation compares ACOLITE and Sen2Cor, without a ground-truth accuracy claim. Read `report.html` for findings and limitations, `METHODS.md` for the full method, and `TABLE_CONTRACT.md` before modelling.

The bounded geospatial delivery is CTR-55 within investigation CTR-54. Scientific review and PI approval are separate and pending. No final-manuscript files are changed.

## Reproduce

Restore the existing project environments using the repository's authorized bootstrap tools, then run:

```bash
./scripts/project-env.sh bash analysis/CTR-54_paired-reflectance-differences/scripts/run.sh
```

The default source is `/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026/data/raw/S2`. Set `CTR54_SOURCE` if moved. Use `CTR54_SCRATCH` for local SSD scratch (budget 12 GiB and approximately 1.5 GiB process RAM). `CTR54_PYTHON` may point to the already-restored shared project Python environment with the exact same lockfile. Do not install a separate scientific environment or modify raw data. Raster commands use the installed GDAL CLI and single-threaded JP2 decoding. The first run may take tens of minutes depending on NAS throughput.

`run.sh` executes inventory, cropped pairing, temporal statistics, direct source checks, figures, independent base R numerical checks, input hashes, report generation and isolated Quarto rendering. The raw data are never written. The source manifests, input metadata, generated data, figures and tables are retained. The handoff stage records output hashes and the exact Git revision; rerun it after any substantive result change.

## Files

- `outputs/paired_differences/`: 88 native-grid per-date/band difference GeoTIFFs.
- `outputs/temporal/`: median, sample SD and valid-count rasters, plus footprint counts and coverage-domain masks.
- `tables/`: acquisition inventory, wavelength/decoding contract, per-date summaries, mask counts, temporal coverage, clipping audit and numerical validation.
- `figures/generated/`: eight-map PNG/PDF and caption.
- `provenance/`: metadata snapshots, versions, lockfile hashes, resource estimate, input/output manifests and handoff.

Large generated rasters are intentionally outside Git tracking; SHA-256 manifests bind them to the recorded analysis revision. Preserve their durable NAS paths and task artifacts together with the tracked scripts. Display `.bin` bridges can be regenerated and are not required for interpreting the GeoTIFF products. All statistics use full-resolution data.
