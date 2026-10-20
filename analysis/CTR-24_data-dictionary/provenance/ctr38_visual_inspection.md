# CTR-38 author visual inspection

Edward Tufte, 20 October 2026, Linux Mint Research Worker (`simon-desktop`). This is author QA, not independent scientific review or PI approval.

Opened both final 600 dpi PNGs with the image viewer. Opened PDF rasterizations of both figures using Poppler. Opened a Firefox screenshot of the self-contained report, showing the station SVG, title, narrative, complete caption and start of the numerical table. Opened the scatter SVG rendered by Firefox. All six station panels and both scatter panels were examined.

The first station render exposed clipped RMSE columns and tight metric-to-panel spacing. These were corrected in the R source and rerendered. The revised exported PNG and PDF preview were opened and checked: all metric columns are visible, six station labels and panel letters are correct, table rows do not touch the next panel, axes share the 0–0.6 reflectance range, legends match symbols and lines, and no plotted finite values lie outside the axes. Data were not changed. The report SVG and standalone scatter SVG show the same composition as the PNG/PDF exports.

The nominal publication width is 180 mm, with 8 pt base typography and approximately 8 pt metric annotations. The station figure is 220 mm high; the companion is 116 mm high. The scatter panels have equal aspect and identical scales; the dashed line is 1:1. The report displays the SVGs at publication width, with an additional readable HTML metric table. All 36 rounded metric annotations were checked against saved values by extracting PDF text. The sign of AC06 ACOLITE bias (-0.001827) is preserved. No primary plotted reflectances are negative; the code would extend the axes to include finite negative values.

The seven supplementary stations appear individually in the HTML ledger with unavailable matched values and NA metrics, and full reasons remain in the original CSVs. Original exclusion labels AC03 mbp_mud and AC04 mpb_mud are retained; AC05 algae_mud is included. Captions identify v4, the three supported bands, physical holds and zero validation eligibility. No inferred intervals, fitted trends or correction ranking appear.

PNG dimensions are 4251 × 5196 and 4251 × 2740 pixels at 600 dpi. PDF text is embedded/selectable. SVG glyphs are vector outlines, editable as paths. Cairo rounds PDF dimensions to integer points (approximately the nominal publication dimensions). Quarto HTML contains both embedded SVGs and no external script, stylesheet or image rendering dependencies. A repeated build checks PNG/SVG/HTML byte identity; PDF creation metadata may vary.

Inspection evidence is retained in outputs/ctr38_station_preview.png, outputs/ctr38_scatter_preview.png, outputs/ctr38_html_preview.png and outputs/ctr38_scatter_svg_preview.png. The Firefox fragment screenshot returned the top of the page and was not treated as inspection of the later section; the standalone SVG was opened instead. Firefox printed a telemetry shutdown timeout after two successful screenshots; the screenshots were written and opened, and this did not affect R or Quarto outputs.

Independent presentation/scientific review and PI scientific approval remain pending at author submission. Native task decisions are the authoritative review record for the exact delivery commit.
