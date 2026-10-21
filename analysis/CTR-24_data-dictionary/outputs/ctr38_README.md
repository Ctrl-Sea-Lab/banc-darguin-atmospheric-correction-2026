# CTR-38 station reflectance figures

Open `station-matchups.html` directly: it embeds both SVG figures and all rendering resources. Edit `station-matchups.qmd`, or edit its reproducible generator in `scripts/ctr38_build.py`. The existing reviewed dictionary remains `report.qmd` / `report.html`.

Figures are under `figures/generated/` in PNG (600 dpi), PDF and SVG. Nominal publication sizes: station panels 180 × 220 mm; scatter 180 × 116 mm. PDF text is embedded/selectable; Cairo SVG glyphs are editable vector paths. Full-precision source metrics are `tables/ctr37_station_metrics.csv`; readable rounded values are `tables/ctr38_display_metrics.csv`. Supplementary NA metrics and the original exclusions/empty validation table are included.

These are exploratory discrepancies: 18 station–band triples, six primary stations, seven unavailable supplementary stations, zero validation-eligible pairs. The spatial support and exposure limitations remain. No correction ranking, inferential intervals or new sampling variability is supplied.

Reproduce in the canonical original checkout at the exact commit recorded in the task's figure-delivery document and in `CTR38_DELIVERY.json` inside the ZIP:

```bash
.venv/bin/python analysis/CTR-24_data-dictionary/scripts/ctr38_build.py
```

Only existing small tables and approved Python/base R/Quarto environments are used. No extraction, spectral integration or metric calculation is rerun. The pipeline verifies frozen inputs before displaying results. It renders `station-matchups.qmd` explicitly from the investigation directory; the project wrapper that always renders `report.qmd` is deliberately not used for this separate report.

Before committing a revised delivery, inspect all exports, update the author visual-inspection record and freeze its manifest:

```bash
.venv/bin/python analysis/CTR-24_data-dictionary/scripts/ctr38_package.py --freeze
```

After committing the exact revision, create the downloadable bundle:

```bash
.venv/bin/python analysis/CTR-24_data-dictionary/scripts/ctr38_package.py
```

The bundle carries analysis-relative paths. It is a review archive; regeneration uses the existing original repository and its locked environments. Unzip into a separate viewing location only if needed to inspect files; do not overwrite scientific inputs. PNG/SVG values and HTML content are deterministic; PDF creation metadata can change on rerender. Native presentation and independent scientific reviews remain distinct from PI scientific approval and manuscript integration, merge and publication authority.
