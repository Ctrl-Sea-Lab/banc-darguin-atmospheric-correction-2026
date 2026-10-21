**Take-home message:** The requested presentation revision is ready: eight visibly larger maps use the fixed SD blue–white–red mapping, while scientific rasters and tables remain unchanged.

**Meaningful results:** The 20 × 6.1 inch canvas has eight 4.42 × 2.31865 inch geographical panels, tight margins and compact shared legends. The PNG is 8000 × 2440 pixels at 400 dpi; a 2400 × 732 preview and PDF are supplied. Full geographic extent and aspect ratio are preserved. SD exceeds 0.02 for B2/B3/B4/B8 in 4.47%/11.85%/15.19%/14.23% of valid pixels; saturation is explicitly marked.

**Issues and limitations:** This changes presentation only. Independent scientific review on CTR-59 and PI scientific approval remain pending. The standalone report has not yet incorporated this revision: Rachel owns integration on CTR-57 and Alan owns actual HTML display verification and exact-candidate packaging on CTR-58. The old report, figures, processing evidence and archives are preserved as prior-revision evidence.

**Implications and next steps:** Rachel should replace the old map and caption with this candidate. Use the preview for inline display with an accessible full-resolution PNG/PDF link. Recommended desktop figure container: full report width up to 1600 CSS pixels, with responsive width 100% and height auto. Alan must measure the actual image width after rendering at desktop viewport sizes (1440 and 1920 pixels), record a screenshot and compare with the prior report; DPI alone is insufficient. Karl should check this exact figure, anchor CSV, saturation audit and rendered size after assembly. This bounded CTR-55 revision is ready for downstream use; no manuscript integration, merge or publication is authorized.

### Concise figure caption

Temporal median (top) and sample standard deviation (bottom; n ≥ 2) of paired surface-reflectance differences, ΔR = ACOLITE − Sen2Cor, for B2/B3/B4/B8 across 22 Sentinel-2 acquisitions. Maps retain the full common supplied extent in EPSG:32628; quantities are dimensionless. Median maps share the original zero-centered limits ±0.04644; low-end display saturation affects 0.89%, 1.04%, 1.54% and 4.55% of valid pixels, respectively. All SD maps share blue = 0, white = 0.01 and red = 0.02; white is a display midpoint, not a zero or significance threshold. SD values >0.02 saturate red (upper legend triangle), affecting 4.47%, 11.85%, 15.19% and 14.23% of valid pixels in band order. Gray denotes NoData; all numerical raster values are preserved. Coverage and quality-mask limitations preclude correction-accuracy or ecological-change claims.

### Exact candidate and reproduction

Figure/code candidate commit: `8dc80d7141d8c4482b8e36ee00f4cee4c9bf8e04` on `ctr-55-paired-reflectance` (local, not merged). Completed scientific source revision: `1bbb23b3b94e775a60aa921f8c9c4f86f51926cb`; previous task head: `1631082eb8089b2beeaec8a97f6214191373f8e7`.

Durable worktree: `/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026/.task-worktrees/CTR-55/analysis/CTR-54_paired-reflectance-differences`. New v2 files are also copied without replacing prior outputs to `/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026/analysis/CTR-54_paired-reflectance-differences/`.

Reproduce only the presentation revision from the worktree:

```bash
/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026/.venv/bin/python analysis/CTR-54_paired-reflectance-differences/scripts/04_figures_v2.py
/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026/.venv/bin/python analysis/CTR-54_paired-reflectance-differences/scripts/10_validate_figure_v2.py
```

Temporary bridges use a unique local `/tmp/ctr55-figure-v2-*` directory and are cleaned afterward. No raw input or scientific raster is written. The raster NoData value (−9999) is read from metadata and represented as NaN only in these temporary drawing bridges. Display sampling includes all four outer edge pixels and maps the entire scientific extent; it does not change the scientific grid. Prior scientific uncertainties continue to apply.

Validation passed: eight raster SHA-256 values match the original delivered output manifest; their CRS, transform, units and NoData metadata match. The input manifest, modelling table, scientific validation and processing records, and original PNG/PDF also match their prior hashes. All eight panel aspect ratios and extents pass. R anchor indices 1/129/257 produce `#2166AC`/`#FFFFFF`/`#B2182B` at 0/0.01/0.02; an independent Python normalization check agrees. Final PNG preview and rendered PDF were visually inspected by Roger (analysis author); this is not independent review. See `provenance/figure_v2_validation.json`, `provenance/figure_v2_inspection.json` and `tables/*v2.csv`.

Input manifest SHA-256: `e0b207ea8d92ea0058b1db9d9a970fee8041f5330541d0b607f4898758b30a31`. The eight raster input hashes and figure output hashes are in `provenance/figure_v2.json`. The versioned presentation-file manifest is `provenance/figure_v2_files.csv`.

| Deliverable | Bytes | SHA-256 |
|---|---:|---|
| `figures/generated/paired_reflectance_maps_v2.png` | 17602104 | `ca9d6e599cd98e875bc04e4602eece1b480d222f721658e654afbd53ecaae0be` |
| `figures/generated/paired_reflectance_maps_v2.pdf` | 12965942 | `b202c1ffa79365b4d332a70d0507cbf999777f0961d0b2038f0a542a64523d3d` |
| `figures/generated/paired_reflectance_maps_v2_preview.png` | 1954528 | `8f75cb51ff40d42281b782166e38bb3270a1df34f2936c4cc906ed4e76182a66` |
