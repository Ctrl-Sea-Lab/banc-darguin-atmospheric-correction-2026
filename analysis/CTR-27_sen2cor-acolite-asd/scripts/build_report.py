#!/usr/bin/env python3
"""Build static standalone feasibility report from audited tables; no manuscript writes."""
from pathlib import Path
import csv,json
P=Path(__file__).resolve().parents[1]
def rows(name):return list(csv.DictReader((P/'tables'/name).open()))
def table(data,cols):
 return '| '+' | '.join(cols)+' |\n| '+' | '.join(['---']*len(cols))+' |\n'+''.join('| '+' | '.join(str(r.get(c,'')).replace('|','/') for c in cols)+' |\n' for r in data)
st=rows('station_crosswalk.csv');srf=rows('srf_coverage.csv');sens=rows('srf_v5_sensitivity.csv');run=json.loads((P/'provenance/run.json').read_text())
short=[{'ASD column':r['asd_column_raw'],'Station':r['station_id'],'GPS row':r['gps_row'],'Label (verbatim)':r['target_class_raw'],'Latitude (raw)':f"{float(r['lat_raw']):.6f}",'Longitude (raw)':f"{float(r['lon_raw']):.6f}",'Role':r['role']} for r in st]
bands=[{'Band':r['band'],'ACOLITE variable':r['acolite_variable'],'Native support (m)':r['sen2cor_native_support_m'],'Response coverage (%)':f"{100*float(r['srf_coverage_fraction_if_nm']):.4f}",'Proposed role':r['spatial_role']} for r in rows('band_contract.csv')]
text='''# March 27 ASD–Sentinel-2 data readiness

**CTR-28 feasibility handoff for CTR-27. Readiness: blocked for scientific extraction and validation.** Date joins and satellite metadata are established, and an explicit proposed contract is delivered. Zero pairs are currently included for extraction or inferential use. This amended bounded feasibility audit is submitted for reassessment; the parent scientific comparison, independent review and PI decisions remain pending. No algorithm ranking or final publication figure is produced.

## Question and scope

Can the supplied 27 March 2026 field spectra be compared fairly with the supplied operational Sentinel-2 Level-2A and ACOLITE surface reflectance? The audit separates evidence of date/identity from comparability of optical quantities and sampling support. It follows parent plan revision `e5d11291-44df-45ee-a80a-2e05b986c152` and reuses the CTR-25 dictionary revision `94e3777e-b618-4bf4-a88c-a7b502ca87d2`, commit `8d885c1c9ea1b10751dea939c2d1aee1432307bd`. The earlier dictionary was documentation, not scientific approval.

All edits are confined to `analysis/CTR-27_sen2cor-acolite-asd/`, initialized from `analysis/_template/`. `task.yml` records CTR-28 as implementation task. The clean starting checkout was fetched and passed `pi_guard.py preflight`; `verify-ready --task-id CTR-28 --agent roger-tomlinson --path analysis/CTR-27_sen2cor-acolite-asd/` returned ready, affected=false. The analysis exemption applies; no Ada synchronization mutation was required. Final manuscript and PI workspace were not edited.

## Amendment evidence

This amendment responds to Karl Popper's Major Revision, independent-review revision `71ca4c89-4664-4868-9eb2-07b4b9c9cd05`, covering audit revision `6fec859e-0973-430f-9486-f618deb59b6b` at commit `1cd34b042eca41f26da81e41fb838b7344357dca`. That earlier submission remains in Git history. The amendment incorporates Charles's reconciliation `f820bfe7-8b71-4344-8b19-15fca9a25164` and Thomas's concurrence `1f9de7bb-a5fb-4c73-ad90-7444529f2189`. `provenance/field_evidence.json` records the authenticated PI interaction `4765af59-1308-4dfe-8c85-19b3f5190b1f`, answered 20 October 2026 at 06:05:15.036 UTC. Field testimony resolves stated units, datum, station-average meaning, instrument/panel, qualitative geometry and field exposure; it is not calibration verification or scientific approval.

## Field evidence and exact proposed crosswalk

The measurement log explicitly assigns **day06 to 20260327**, including AC01–08 for Sentinel-2 atmospheric-correction validation and day06 cover/core sampling. GPS `Sheet1` rows **110–124**, date serial **46108**, independently agree on 27 March 2026 using the workbook's default 1900 date system. No measurement time is supplied; zero Excel fractional day is not interpreted as midnight observation.

There are **15 date-eligible spectral columns**: AC_01–AC_08 and D06_A–D06_G. The eight AC stations are primary design candidates; seven D06 spectra are supplementary candidates whose pixel-sized sampling is undocumented. `station_crosswalk.csv` encodes the explicit alias list, preserving all three raw identifiers. This is a proposed evidence-based join, not a generic string normalization rule. Every March 27 proposed ID has exactly one spectrum, cover row and GPS row; no duplicate or unmatched identifier occurs within these 15. `spectrum_disposition.csv` accounts for every supplied spectral column and excludes other days from this investigation.

{{STATIONS}}

The PI confirms **WGS84 EPSG:4326** for the supplied coordinates. Positional accuracy and measurement footprints remain unknown. Both AC01 and AC02 have waypoint text `Iwik station` and coastal coordinates, while their workbook location says Arel; the record is preserved, not relocated to Arel. AC01/02 are approximately 21 km from the Arel AC group using the PI-confirmed WGS84 coordinates. The cover table has no GPS waypoint for them; the workbook supplies coordinates. All other March 27 cover/GPS waypoints agree. D06_A–F carry cover and core identifiers; D06_G has label `sand`, cover 0. Cover units, the code `zn` and Poskey interpretation are not invented.

`AC03=mbp_mud` and `AC04=mpb_mud` are retained separately. Whether the former is a spelling error requires field confirmation. `seagrass` and `zn` do not establish species. No classifier or spectral resemblance was used to identify ecological classes.

The supplied `POI_S2C_ACOLITE_targets` has **six** EPSG:32628 points, named T1–T6: Terrestrial soil, Water, Seagrass, Intertidal Sediment, Underwater Vegetation, Underwater Sand. It has no AC/day06 identifiers or acquisition dates. It cannot provide a field crosswalk or evidence of March 27 exposure. Under the PI-confirmed field WGS84 transform, nearest point distances are about 1.30 km for AC01/02 and 5.57–5.77 km for the Arel group. These are unmatched records, not aliases. The two time-series polygons have AOI Arel/Iwik and null id fields; they are broad AOIs, not the AC field footprints. Extent and square-mask polygons supply spatial context only. Relevant features and CRS are preserved in `outputs/vector_records.json`.

### ASD quantity and sampling limitations

`202603_Reflectance_avg.txt` has **501 ordered wavelength rows**, numeric `wl` 400–900 at increment 1. All 15 candidate spectra are finite throughout; their pooled raw range is **0.0293690581–0.5736308287**. The PI confirms wavelengths in **nm** and reflectance **dimensionless 0–1**. No percent conversion or other scaling is applied. The original header alone does not supply these units.

The PI confirms that each supplied spectrum is a **station average**, measured with an **ASD Handheld FieldSpec2** and **99% Spectralon** panel, at nadir with the same stated angle/azimuth relative to the sun. All targets were intertidal and **exposed during field measurement**. This does not establish exposure/wetness at overpass or exact numerical solar/view angles, FOV or height.

The log records number-to-save 20 and spectrum counts white=50, dark=20, sample=50. For AC01–08 it states **5 × 20 spectra within an area the size of an S2 pixel**. The exact resolution/boundary, exported-average membership/weights, repeat variance, smoothing/noisy intervals and detailed panel calibration are not established. These optional details are documented uncertainties, not fabricated defaults or automatic stand-alone blockers for descriptive work. Unknown field support and material overpass-state changes remain essential holds. Raw repeat spectra and field images mentioned in the tables/log were not supplied in ASD/GPS. Day05/day07 water/glint/height details are not transferred to day06.

## Satellite identity, processing and spatial coverage

The expanded supplied product is **S2B_MSIL2A_20260327T113319_N0512_R080_T28QCH_20260327T152639.SAFE**. Product and datastrip XML identify Sentinel-2B, Level-2A, baseline **05.12**, relative orbit **80 descending**, absolute orbit **047296**, processing centre **2BPS**, generation **2026-03-27T15:26:39Z**. Product/datatake start is **11:33:19.024Z**. Tile XML, not the name alone, gives tile sensing **11:45:53.975343Z** and tile ID `S2B_OPER_MSI_L2A_TL_2BPS_20260327T152639_A047296_T28QCH_N05.12`.

This is an **operational Level-2A product using Sen2Cor-based processing**, not evidence of an independently rerun standalone Sen2Cor experiment. A standalone software version/configuration was not recovered; baseline and GIPP identifiers are available. No correction was rerun. The report should label this comparison operational L2A versus supplied ACOLITE DSF. Operational and user-generated L2A are distinct routes in the [official product documentation](https://sentiwiki.copernicus.eu/web/s2-products).

The 11 March 27 TIFFs in `S2/ACOLITE/20260327/` preserve embedded `NC_GLOBAL` metadata and band attributes even with PAM disabled. They explicitly identify **ACOLITE**, sensor `S2B_MSI`, L2W `rhos_*`, and **2026-03-27T11:45:53.975343+00:00**, exactly matching the L2A tile timestamp. Their source is recorded as `S2B_MSIL1C_20260327T113319_N0512_R080_T28QCH_20260327T150331.SAFE` under a historical Windows path; granule `L1C_T28QCH_A047296_20260327T113507`. Thus the same acquisition/platform/tile/orbit is supported by embedded headers. This does not prove byte-identical input ancestry: that March 27 Level-1C payload is not supplied for a hash check. The old Windows path is provenance, not an accessible input.

Recovered ACOLITE version is **Generic GitHub Clone c2026-04-07T11:45:24**, runid **20260407_115117**, generated **2026-04-07 13:26:22 Paris, Madrid (heure d’été)**. This string is not an exact Git commit. Settings embedded in every TIFF include `atmospheric_correction_method=dark_spectrum`, tiled AOT with intercept spectrum and min_drmsd selection, 600×600 tiles, linear tile interpolation and smoothing, selected `ac_model=ACOLITE-LUT-202110-MOD1`, target resolution 10 m, `warp_resampling_method=bilinear`, `l2w_parameters=rhos_*`, **l2w_mask=False**, no residual glint, interface-reflectance or adjacency correction. Model/header AOT values are processor provenance, not independent atmospheric measurements. An unused `dsf_fixed_lut=MOD2` setting must not replace the selected `ac_model=MOD1` in interpretation.

The TIFFs therefore recover much of the missing standalone 2026 settings/NetCDF provenance. Still missing are exact ACOLITE source SHA, LUT/ancillary content hashes, authenticated SRF version, complete execution log and recoverable March 27 source L1C. Current [ACOLITE source](https://github.com/acolite/acolite) and [GeoTIFF export code](https://raw.githubusercontent.com/acolite/acolite/main/acolite/output/nc_to_geotiff.py) explain the metadata/quantity conventions; current code does not authenticate the April clone. No settings from 2025 were substituted.

Both raster families declare **EPSG:32628**. L2A 10 m grid: origin **(300000,2300040)**, 10980×10980, bounds **x=300000–409800, y=2190240–2300040 m**. ACOLITE 10 m grid: origin **(334050,2209980)**, 3763×1974, bounds **x=334050–371680, y=2190240–2209980 m**. The AC crop is inside the SAFE grid, offset exactly **3405 columns and 9006 rows** at 10 m. This verifies grid alignment, not empirical geolocation or image registration accuracy.

L2A has B01–B09, B8A, B11 and B12 (12 unique bands); B10 is absent. Four 10 m bands are supplied, the 20 m set includes B01, and 60 m also includes B09. Native B01 support remains 60 m even where resampled to 20 m. ACOLITE has 11 `rhos` bands, including B01/B8A/B11/B12 but neither B09 nor B10. No March27 `l2_flags` file is supplied. Exact paths and per-band metadata are in `band_contract.csv` and captured headers.

{{BANDS}}

### Decode and quality contract

For L2A, product XML declares **BOA_QUANTIFICATION_VALUE=10000**, all 13 band-index offsets **−1000**, NODATA=0 and SATURATED=65535. Mask special codes first, then decode **(DN−1000)/10000**; JP2 band defaults alone are insufficient. This follows [official encoding guidance](https://sentiwiki.copernicus.eu/web/s2-products). ACOLITE TIFF bands are Float32 with unit **1**, `surface_bidirectional_reflectance`, NaN NoData and no additional scale/offset declared: read finite float values directly. Never divide them by 10000 or multiply by π. Do not compare Rrs (sr−1) directly to dimensionless reflectance; a π conversion alone cannot establish matching geometry or optical definitions.

Proposed common quality screening rejects SCL codes **0,1,2,3,7,8,9,10,11** and uses 4/5/6 only with independent field exposure evidence. Apply the same common mask to both methods; do not use an aquatic bright-land mask to discard the dry sand targets. Decode native defect/detector masks at extraction stage and require all pixels in an agreed primary support to pass. Do not silently average over a reduced footprint. ACOLITE l2w_mask=False means finite pixels alone are not a cloud or glint guarantee. Keep valid negative reflectance with flags rather than clipping to improve fit. SCL is processor classification, not ecological truth or independent accuracy.

## Spectral convolution specification and version choice

Primary reference remains the **supplied v4.0 S2B average response** sheet, hashed with the input inventory. The workbook Overview documents ground-measured instrument responses and nm units for wavelength columns. The PI independently confirms ASD wavelengths in nm. No Gaussian or nominal central-wavelength substitute is used.

For the later released extraction, compute each band as **∫Rfield(λ)Sband(λ)dλ / ∫Sband(λ)dλ**, trapezoid integration on the union of ASD and SRF knots with linear interpolation only between finite consecutive ASD samples separated by at most 1 nm. Preserve response normalization; a peak-normalized response need not have unit area. Reject a nonfinite, missing or known noisy interval intersecting positive SRF support. Do not extrapolate, fill with zero or silently normalize a truncated band. Proposed minimum response coverage is **99.9%**, fixed before any algorithm ranking; threshold is a conservative design choice, not an instrument accuracy specification. Supplied S2B responses have no negative response entries.

With PI-confirmed ASD nm units, B01–B07 and B8A have full supplied response coverage. **B08 spans 774–907 nm and only 99.4857969% is covered**: hold it from primary inference. B09, B10, B11 and B12 have no ASD support. B09/10 also lack a supplied correction pair. No missing wavelengths are fabricated. Even B01/red-edge/B8A cannot be promoted without field support at their native 60/20 m resolutions.

![Spectral response coverage using PI-confirmed field wavelengths in nm.](figures/srf-coverage.png)

The [20 August 2026 official SRF update](https://sentinels.copernicus.eu/-/sentinel-2-spectral-response-functions-update) announces v5 refinements and removal of negligible edge noise, intended for PB05.13. Our scene is PB05.12. V4 is retained to preserve the supplied design reference; this is not proof that every processor used exactly this workbook. The official v5 workbook was downloaded separately through the [SentiWiki library](https://sentiwiki.copernicus.eu/web/s2-documents), SHA-256 **42be3ebd8bfcbde11c37caeb2e2fdda65fefa8d2b6f8329559b7806d02cdc9e2**. It was not substituted into the supplied raw data.

Numerical response-only sensitivity finds v4→v5 equivalent-wavelength changes B02 **−0.015509 nm**, B03 **+0.003757 nm**, B04 **−0.011218 nm**; normalized response L1 distances respectively **0.0006682, 0.0017852, 0.0029923**. These are response-shape diagnostics, not reflectance errors. V5 B08 coverage is **99.5009575%**, still below 99.9%; the eligibility decision is unchanged. `srf_v5_sensitivity.csv` contains all 13 bands. After physical/QA holds are resolved, report a separate v5 convolved-reference sensitivity without changing the primary reference. Do not infer ACOLITE's exact SRF version from its rounded wavelength labels.

## Spatial and temporal extraction specification

With field CRS confirmed, establish the sampled area before extraction, transform coordinates explicitly (traditional GIS order lon,lat), retain raw coordinates, and use the **containing native 10 m pixel for B02/B03/B04** only if it represents the sampled area. Match the identical pixel boundary across corrections. If a genuine field polygon spans pixels, use a prespecified area-weighted aggregate of the same physical boundary for both methods and document the mismatch to the sensor point-spread function. No value-based selection of pixel, window, shift or tide tolerance is permitted. A fixed 3×3 neighborhood is a sensitivity/support diagnostic, not nine extra field replicates.

For coarser bands, require a demonstrably homogeneous 20/60 m field region; the existing 10 m ACOLITE interpolation cannot recreate native resolution. Any later common coarse grid must have explicit anchor and bounds, area-weighted reflectance aggregation and nearest-neighbor categorical masks. Keep original mask support and report coverage. B01 stored at 20 m does not become a 20 m observation.

Small diagnostic reads were repeated using the **PI-confirmed EPSG:4326 coordinates**. The historical column names containing `if_wgs84`/`hypothetical` are retained for traceability; their current evidence status is explicit in each record. These locators do not validate physical field support. At all 15 locations both B04 products have 9/9 finite/non-special pixels in 3×3 windows. SCL neighborhoods were also read. Total requested windows: **15×3×9=405 values** (logical reads can overlap; underlying driver blocks may be larger). No full raster statistics or scene processing occurred; diagnostic reflectance pairs were not calculated or passed to statistics.

AC01/02 have SCL centre 5; AC03–06 and AC08 centre 6; AC07 centre 4. SCL6 at stations labelled mud/sand/seagrass is a material exposure/mixture question, not proof that either the field label or classification is wrong. D06_A and D06_B are **1.567 m apart and share one 10 m pixel** using the confirmed CRS. AC01/02 are only **16.620 m apart** and share a 20 m SCL cell. Record D06_A/B as a shared candidate native-cell relation outside the primary population. Record AC01/02 sharing as a **QA-only relation**, not a radiometric merge. Final components and independent units remain unestablished; overlapping diagnostic neighborhoods are not primary contributors. Heterogeneous neighborhoods, GPS error, adjacency, sediment moisture, epiphytes, glint, atmospheric correction, tide and water column can all confound differences.

Grid alignment is established. Image-to-ground and inter-product registration are not: assess stable independent features/UAV or ground control before extraction, record residual offsets/uncertainty, and use a prespecified ±1 pixel sensitivity without fitting to ASD agreement. No co-registration shifts were applied.

The tile time is known to subsecond precision; exact field UTC interval/timezone and overpass tidal/exposure state are not established. Same date alone is not a validated matchup interval. Seek field start/end times and overpass state, or document irrecoverability and a bounded physical justification; use a named tide source/model/datum if reconstructed. Field exposure is already confirmed and is not asked again. No retrospective “close enough” time/tide tolerance is asserted. Unresolved material exposure/wetness changes keep affected records held. Missing exact timing may permit only a documented physically justified descriptive comparison; date agreement alone does not supply it.

## New AOI extracts: intake and source reconciliation

The actual case-sensitive location is **`data/raw/Atm_Compare_AOI`**; uppercase `Data` does not exist in this project. `tables/aoi_input_inventory.csv` inventories the supplied folder and whole-file SHA-256 hashes the two used March27 CSVs. Other dated files were inventoried by path/stat only and excluded from table/value inspection. Originals were read only. Historical Windows source strings are retained as provenance addresses, not accessible Linux inputs.

{{AOI}}

These files contain **pixel records across broad AOIs, not station means**. They have no station identifier, ecological label, explicit CRS/unit/NoData specification, QA columns, aggregation weights or producer script. `pixel_id` restarts in each AOI: only the qualified `(AOI, pixel_id)` key is unique. All 1,463 keys pair one-to-one across corrections, with exactly equal centre coordinates and 10 m nominal boundaries. All row/column centres match the respective EPSG:32628 source grids under a zero-based convention, and offsets are exactly 3,405 columns / 9,006 rows. The CSV scene identities match the supplied L2A product and ACOLITE stem; the tile metadata supplies the exact time. These checks establish nominal source/grid relationships, not field support, effective kernel equivalence or valid QA.

The centre-in-polygon cell sets were reconstructed from supplied `TimeSeries_Polygons_Matchup.shp`, with results in `outputs/aoi_intake.json`. This tests a candidate rasterization rule; it does not authenticate the producer's implementation. No station containing cell matches the CSV support at the confirmed GPS coordinates: **0 of 15**. Nearest CSV cell centres are 15.85–989.71 m from field positions. Even the nearest AC06 point is outside its containing-cell coverage; nearest neighbors are never aliases. `tables/aoi_station_join.csv` preserves every unmatched station. AOI names do not resolve the AC01/02 location conflict.

Six cells chosen without reference to ASD (first, midpoint and last record within each AOI) were checked in every available band, totaling **138 scalar raster reads**, followed by six B01 representation checks (**144** total in this amendment). `tables/aoi_source_spotchecks.csv` records source address, row/column, raw and decoded values and sample hashes. For primary B02–B04, all **36/36** values match their own source decode within 1e-7; this is an encoding diagnostic, not an atmospheric-correction performance metric. The six L2A B01 comparisons differ from the native-60 m stored representation. Follow-up comparisons use the supplied stored-20 m B01 representation; this does not change B01 native sensor support (60 m). The bounded checks are summarized below. Matching a coarser stored cell cannot recover unknown native weights; mismatching it does not by itself prove an error because the CSV resampling recipe is absent.

{{SPOTCHECK}}

The CSVs contain no QA or contributor counts. Their paired nominal cell set cannot establish common effective sensor support, which matters particularly for coarse bands resampled to 10 m. Headers document ACOLITE bilinear warping; native L1C contributors/weights and the CSV export recipe remain unavailable. No field polygon, station-to-AOI crosswalk or correction-specific full-support mask is inferred. The supplied AOI values therefore stay outside the station match-up ledger, whose reflectance values remain empty. No new correction run or full station extraction was performed.

## Normalized extraction–statistics contract

All **165 candidates** (15 stations × 11 paired bands) remain in `tables/proposed_matchups.csv`, mapped one-to-one to `outputs/normalized_design.json`. The stable key is `(target_id, occasion_id, band_id, extraction_version)`, with `matchup_id`, separate reference/scene-pair/source IDs, literal IDs, evidenced 1:1:1 joins, raw class, primary/supplementary role and reason-bearing states. The single exported average per station is established; its repeat composition and exact physical occasion remain unknown. Empty CSV fields / JSON null mean unknown or not evaluated, never zero or passed QA. All inclusion and paired-valid booleans remain false. The maximum **24 primary candidate band-pairs** is not a realized sample size.

The normalized file supplies targets, references, occasions, source identities with explicit full-file versus header/sample identity strength, scene pairs, matchups, **330 candidate radiometric-support records**, separate QA cells/links and target-level complete-spectrum states. Candidate cell locators are explicitly not approved primary contributors: field footprints remain unknown, numerical extraction weights and contributor counts are null. Source/output grid IDs, boundaries, native/output resolutions and upstream-lineage gaps are recorded. Diagnostic 3×3 windows never acquire primary weights. Actual upstream contributors or a defensible conservative support envelope must be supplied before support-based grouping can be implemented.

`outputs/dependence_graph.json` records typed relations and a version/hash. Its primary domain is AC01–08 and B02–B04 with actual primary contributors. Shared QA support is auxiliary; D06_A/B sharing a nominal native 10 m cell is outside the primary domain. Actual field overlap, native radiometric sharing across either correction, repeated units and documented site dependence require union, transitive closure and any evidenced site/block merges **before errors are inspected**. Components cannot later be split by method, band, type or exclusions. Site/footprint/ACOLITE upstream support remain unresolved, so final components, resampling-unit IDs, independent G and statistical weights are null.

`outputs/data_contract.json` carries Thomas's concurrence. For each band P_b requires reference and both methods to pass the same physical/full-support QA rule; P* is their target intersection across the fixed three bands. Main facets use identical P* targets and ASD references. Equal-unit weights are `1/(G × T_g × 3)` for P*, and `1/(G_b × T_gb)` per band, identical across corrections; extraction weights are separate. RMSE is the square root of weighted squared error. Complete-case coverage must disclose targets/units, literal/verified classes, sites, timing/exposure/support and ordered losses. Charles/Roger must freeze the metadata-based representativeness justification before errors; an absent intended class/site or systematic exposure/QA loss precludes an unqualified primary-population claim. Unknown classes stay unknown.

If P* is empty, pooled metrics are NA with a reason; valid P_b tables can be reported after physical release. If P* is unrepresentative, any summary describes only that subset and a primary-population ranking is withheld. Charles must record a dated amendment before a band-stratified replacement figure/estimand. No silent band drop, imputation or supplementary substitution is allowed. At most eight primary targets cannot meet the design's 20-unit interval rule: no bootstrap, inferential intervals or p-values are planned. G=0 yields no estimate; G=1–4 permits descriptive results; G=5–19 additionally requires unit contrasts and leave-one-unit-out sensitivity. Unknown grouping is reported as unknown. No bias, MAE, RMSE, correlation, R², inference or ranking is computed here.

## Remaining evidence and questions

Essential field-owner evidence: actual sampled boundaries/area and positional accuracy sufficient to justify support; resolution of AC01/02 Iwik coordinates versus Arel text; exact field times/timezone and overpass exposure/wetness, or documented irrecoverability with a defensible bounded physical comparison. The new AOI extracts do not resolve these. Charles owns the existing reconciliation and question path; this amendment creates no duplicate PI question.

AC03 `mbp_mud` remains literal and unconfirmed relative to AC04 `mpb_mud`; unknown label alone need not invalidate an otherwise physical overall matchup but prevents an inferred ecological class. Detailed geometry, average membership/weights/variance, calibration certificate and preprocessing remain optional uncertainties to document if available, not automatic blockers by themselves. No resolved unit/datum/field-exposure question is repeated. `zn` expansion matters only if supplementary samples are separately proposed.

Technical dependencies: recover extract export/resampling/NoData/QA recipe and upstream contributor lineage or justified support envelope; verify native detector/defect masks and empirical registration; freeze support, grouping and coverage rules before extraction. Exact ACOLITE source/LUT/ancillary/SRF provenance remains incomplete, limiting reproducibility and attribution. Charles has selected the bounded supplied-product comparison; no new correction run is requested. Unknown essential QA/support remains a hold. **Readiness stays blocked for station extraction.**

## Response to independent review

1. **Physical evidence superseded:** `scripts/audit.py`, crosswalk/ledger, report, figure and `provenance/field_evidence.json` now use the authenticated units, CRS, mean status, instrument/panel, qualitative geometry and exposed field state. Material footprint/location/overpass holds remain; optional uncertainties are distinguished.
2. **New extracts:** `scripts/amend.py`, input inventory, station join, source spotchecks and `outputs/aoi_intake.json` document exact path/hashes, identities, nominal support and missing QA/resampling. No valid station join was found; no AOI value was substituted for ASD-station reflectance.
3. **Contract:** normalized stable identities, separate candidate radiometric and QA support, typed unresolved graph, validity/null/reason states, full ledger retention and Thomas's grouping/complete-case/weight/fallback rules are delivered. This remains a held design, not an extraction release.

Minor finding: band-specific hold reasons now distinguish absent ASD spectral coverage, incomplete B08 coverage and unestablished 20/60 m field support. No band was promoted.

## Reproducibility, validation and review

Run from the project root:

```bash
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/audit.py
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/amend.py
./scripts/project-env.sh Rscript analysis/CTR-27_sen2cor-acolite-asd/scripts/coverage_figure.R
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/build_report.py
./scripts/render-analysis.sh analysis/CTR-27_sen2cor-acolite-asd
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/validate.py
```

Audit assertions check unique source IDs/date joins, monotone wavelength grid, metadata/units/NoData/grid consistency across 11 ACOLITE bands, L2A offsets, manifest count and all inclusion holds. Source stat tuples for all supplied files were unchanged during the audit. Small inputs/metadata/reference files are SHA-256 hashed. Rasters are documented by path/stat/header and sampled-window hashes; no whole-scene hashes were computed. This distinction limits byte-identity claims. PAM is disabled and originals remain untouched. The v5 download is separately named and exact-hash checked on rerun.

{{ENV}}

Technical verification of this amendment passed: the locked project environment check, all 34 preservation tests, standalone HTML rendering, input-hash verification, ledger/key/foreign-key checks and held-validity invariants. These are author checks; independent numerical/scientific review remains pending.

No dependencies, environment lockfiles or system software were changed. The standalone Quarto configuration does not inherit or render the final manuscript. `provenance/deliverable_manifest.json` identifies exact delivered file hashes; `provenance/run.json` records commands, environment and input provenance. A report cannot include its own final hash. `provenance/amendment_run.json` records the intake checks, stat preservation and explicit bounded read count. Original submission provenance remains recoverable at its exact Git commit; current outputs supersede it only within this investigation.

**Independent review pending. PI scientific approval pending. Manuscript integration, merge and publication not authorized.** Charles receives this handoff for scientific coordination and review routing. The readiness block concerns the parent extraction/comparison; the feasibility audit delivers an evidence-based missing-input decision.
'''
intake=json.loads((P/'outputs/aoi_intake.json').read_text())
aoi=[{'Correction':g['correction'],'AOI (raw)':g['AOI_raw'],'Pixel rows':g['rows'],'Bands':', '.join(g['bands'])} for g in intake['groups']]
checks=intake['spotchecks'];pc=intake['polygon_checks']
spot='Source-check mismatches against the containing stored cell: '+json.dumps(checks['mismatches_by_method_band'],sort_keys=True)+'. B01 stored-20m follow-up: '+str(checks['B01_20m_followup_matches'])+'/'+str(checks['B01_20m_followup_checks'])+' match. Polygon centre-set checks: '+json.dumps(pc,sort_keys=True)+'. Full per-record diagnostics are retained; no correction-to-ASD error is calculated.'
text=text.replace('{{AOI}}',table(aoi,list(aoi[0]))).replace('{{SPOTCHECK}}',spot)
text=text.replace('{{STATIONS}}',table(short,list(short[0]))).replace('{{BANDS}}',table(bands,list(bands[0]))).replace('{{ENV}}',f"Environment: Python {run['python'].split()[0]}, NumPy {run['numpy']}, {run['gdal']}. Source base {run['base_commit']}; branch `{run['branch']}`. UV lock SHA-256 `{run['locks']['uv.lock']}`; renv lock SHA-256 `{run['locks']['renv.lock']}`.")
(P/'report.md').write_text(text)
(P/'report.qmd').write_text('---\ntitle: "March 27 ASD–Sentinel-2 feasibility audit"\nsubtitle: "CTR-28 handoff for CTR-27; scientific extraction held"\nauthor: "Roger Tomlinson"\nformat: html\nexecute:\n  enabled: false\n---\n\n'+text)
print('Built static report')
if __name__=='__main__':pass
