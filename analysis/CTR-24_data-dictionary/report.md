# Banc d’Arguin 2026 — descriptive data dictionary

**CTR-25, supporting CTR-24. Documentation only; scientific analysis not started.**

This dictionary describes supplied files and declared schemas. No measurement statistics, model, classification, atmospheric correction, map, figure, ecological interpretation, or cross-dataset matching was produced. Internal review is pending Karl Popper (CTR-26). There is no PI scientific approval, manuscript-integration authorization, merge authorization, or publication authorization.

## Snapshot and locations

The inventory ran from **2026-10-20T01:36:52.496930+00:00** to **2026-10-20T01:38:03.757906+00:00** on Linux Mint 22.3. It found **847 supplied files** and **2 Git placeholders**, totaling **90,798,124,101 bytes**. Archive members are listed separately and are not added to physical-file totals. There are **4,376 ZIP entries** (including directories) and **13,594 variable/band/reference-column records**. These are documentation counts, not measurement statistics.

The PI’s added files are physically under the repository-local `data/raw/`. This supersedes the empty-data description in the initialization README/config. No data were moved, renamed, or reprotected.

| Root key | Exact directory | Physical files |
| --- | --- | --- |
| project_raw | /mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026/data/raw | 848 |
| project_processed | /mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026/data/processed | 1 |
| nas_raw | /mnt/PaperClip_Projects/data/raw/banc-darguin-atmospheric-correction-2026 | 0 |
| nas_processed | /mnt/PaperClip_Projects/data/processed/banc-darguin-atmospheric-correction-2026 | 0 |

`project_raw` is not a symlink. Both NAS roots are empty; `project_processed` contains only `.gitkeep`. Data can already be processed products even when stored under `raw/`; location is not a processing-level definition. File inventory captures every file’s path, bytes, timestamp, mode, UID/GID, role and metadata status. No symlink entries were present.

No whole-data content checksum was calculated. The source snapshot identifier below hashes sorted file-stat records, not measurement bytes:

`044a78e6d27d24ee9c8c2f347bac52d921d1154b190fcc456a9817ee4d5910a2`

## Available groups

All paths in this table are relative to `project_raw`. Group labels derived from directory names are organizational labels; headers provide sensor/product definitions below.

| Group / relative location | Files | Bytes | Contents |
| --- | --- | --- | --- |
| ASD | 3 | 1305661 | Field spectrum table, field-cover table and measurement log |
| GPS | 1 | 21503 | Field information workbook |
| S2/ACOLITE | 385 | 17666319540 | Supplied ACOLITE NetCDF/GeoTIFF products and run settings |
| S2/expanded_SAFE | 192 | 1884953226 | Two expanded Level-2A SAFE products, imagery and metadata |
| S2/Sen2Cor | 46 | 43365870598 | 46 zipped SAFE products; folder label Sen2Cor |
| SHP | 39 | 5035886 | Seven shapefile sets, sidecars, QGIS metadata, one ZIP |
| Sentinel5P | 180 | 27873278508 | 132 NetCDF products, 45 PNGs, two MATLAB scripts, one CSV |
| spectral_response_reference | 1 | 1339179 | Sentinel-2 spectral-response reference workbook |

## Field spectroscopy and cover

Sources: `ASD/202603_Reflectance_avg.txt` first-line header, `ASD/202603_Seagrass_cover.txt` first-line header, and the complete 2,318-byte `ASD/202603_Measurement_log.txt`.

The log explicitly describes ASD seagrass-cover measurements, core-related measurements, and measurements for Sentinel-2 atmospheric-correction validation. It lists day01–day08 dated **2026-03-22 through 2026-03-29** and site names Ebel Kheaiznaya, Aouatif, Niroumi, Arel and Zira. These are source-log descriptions, not verified habitat identities or geographic extents. Listed participants include Jim, Pierre, Hacen, Laurent and Simon. ASD instrument model, calibration certificate, footprint, angular geometry, reflectance units, wavelength units, uncertainty and averaging method are undocumented.

The log states “number to save 20” and white/dark/sample counts of 50/20/50. These are recorded instrument settings; the number of usable observations was not checked. Drone flights are mentioned, but no separate UAV image/LiDAR dataset is present in this bounded inventory.

The spectrum file is whitespace-delimited with **142 literal columns**: `wl` followed by **141 spectrum/station labels**, all enumerated in `variable_dictionary.csv`. The interpretation as averaged reflectance is inferred from the filename and field-log context, not a declared unit or processing specification. `wl` suggests wavelength, but its unit is undocumented. Rows were not counted and spectral values were not summarized.

Labels preserve case and punctuation, for example `d01_A`, `d02_C327`, `D05_H1`, `AC_01` and `D07_R`. Do not silently normalize these or assume they join the cover/GPS identifiers. The log’s `AC01-08` spelling differs from the spectrum-header convention. A day08 log entry is not proof that corresponding spectral columns were supplied.

| Cover field | Definition supported by documentation |
| --- | --- |
| station | literal station identifier; not normalized or joined |
| cover | cover field; field log describes seagrass-cover measurements; unit and scoring protocol undocumented |
| gps | literal gps field; identifier meaning is source-specific and undocumented |
| picture | literal picture reference; referenced photographs not established by this inventory |
| comment | free-text/code field; ecological abbreviations have no supplied codebook |
| cores | literal cores field; counting/protocol meaning undocumented |
| loripes | literal loripes field; meaning, units and missing-code convention undocumented |

The cover table is tab-delimited. Column storage types are undeclared text serialization. A numeric-looking cover does not establish a percentage unit. Literal `NA` text occurs in the bounded initial schema inspection, but no formal missing-value convention is supplied; it was not recoded. Species/code meanings such as `zn` are undocumented. No row-level exclusions or joins were made.

## Field information workbook

Source: `GPS/Info spectral measure_biomass core_BdA 2026.xlsx`, `Sheet1!A1:L1`, OOXML dimension `A1:L131`, and first-data-row storage types/styles. The declared used range may include formatting and is not a validated record count. The 12 headers are:

| Field | Storage evidence | Meaning / limitation |
| --- | --- | --- |
| station | xlsx cell s (first data row only) | literal station identifier; not normalized or joined |
| cover | xlsx cell n (first data row only) | cover field; field log describes seagrass-cover measurements; unit and scoring protocol undocumented |
| waypoint | xlsx cell n (first data row only) | literal waypoint identifier; coordinate precision/datum not declared in workbook |
| gps | xlsx cell s (first data row only) | literal gps field; identifier meaning is source-specific and undocumented |
| picture | xlsx cell s (first data row only) | literal picture reference; referenced photographs not established by this inventory |
| comment | xlsx cell s (first data row only) | free-text/code field; ecological abbreviations have no supplied codebook |
| poskey | xlsx cell undocumented (first data row only) | literal poskey field; relationship/key definition undocumented |
| date | xlsx cell n (first data row only) | literal date field; Excel numeric cell type and style retained in headers.json |
| location | xlsx cell s (first data row only) | literal location label; not verified geographic coverage |
| lat | xlsx cell n (first data row only) | literal lat field; latitude interpretation inferred from abbreviation; units and datum undocumented |
| lon | xlsx cell n (first data row only) | literal lon field; longitude interpretation inferred from abbreviation; units and datum undocumented |
| Zone | xlsx cell s (first data row only) | literal Zone label; classification scheme undocumented |

The workbook has numeric and shared-string cell types; numeric Excel dates retain their source style and number-format IDs in `headers.json`. No date-column scan or coordinate transformation was performed. `lat`/`lon` suggest geographic coordinates, but the datum, CRS, coordinate units, positional accuracy and GPS device model are not declared in the inspected schema. `cover`, `comment`, `Zone` and `poskey` have no supplied complete codebook. The `gps` column differs structurally from `waypoint`; neither is assumed equivalent to the text-table `gps` field. Biomass/core measurements are suggested by the filename, but no column explicitly defines measured biomass, its units, or its protocol.

## Sentinel-2 SAFE products

Sources: each product’s `MTD_MSIL2A.xml` (product identity, processing baseline, quantification, offsets, special values and spectral definitions), granule `MTD_TL.xml` (sensing time, CRS and grid), JP2 headers for expanded products, and ZIP central directories for archived products. Exact archive/member addresses are in `archive_inventory.csv` and the SAFE rows of `variable_dictionary.csv`.

`S2/Sen2Cor/` contains 46 ZIP files. The folder name is a supplied label; actual XML declares Level-2A products and spacecraft. `S2/` also contains two expanded Sentinel-2B Level-2A SAFE directories with product-start dates 2026-03-07 and 2026-03-27. This does not establish that archives and expanded directories are distinct acquisitions in a complete timeseries. No duplicate-content or cross-product comparison was performed.

Declared product-start interval across accessible XML metadata: 2025-01-06T11:34:51.024Z through 2026-03-27T11:33:19.024Z.

The granule headers declare **WGS84 / UTM zone 28N, EPSG:32628**. Typical tile grids explicitly listed in the inspected `MTD_TL.xml` are 10 m (10,980 × 10,980), 20 m (5,490 × 5,490) and 60 m (1,830 × 1,830), with signed Y pixel spacing. Every file’s actual header dimensions/geotransform are retained; no co-registration or pixel alignment test was made.

Spectral metadata enumerate B1, B2, B3, B4, B5, B6, B7, B8, B8A, B9, B10, B11 and B12, each with wavelength bounds/central wavelength in nm and nominal resolution. A metadata definition, including B10, does not prove that an image of that band is present in a particular Level-2A archive. Use the member inventory to establish actual files. Expanded imagery also includes ancillary/display/quality layers such as AOT, WVP, SCL and TCI; these are not additional reflectance bands.

For example, `S2/Sen2Cor/S2A_MSIL2A_20250106T113451_N0511_R080_T28QCG_20250106T154249.zip!…SAFE/MTD_MSIL2A.xml` declares processing baseline 05.11, BOA quantification value 10,000, BOA offsets −1,000 indexed by band, AOT quantification 1,000, WVP quantification 1,000 with unit cm, special values NODATA=0 and SATURATED=65,535. These are literal encoding metadata; no reflectance conversion was applied. Per-product definitions must be consulted rather than transferring this example to a different processor’s products.

Scene-classification labels/codes, product quality declarations and masks are retained from metadata. They were not evaluated and do not constitute independently assessed classification accuracy. Atmospheric-correction adequacy, adjacency effects, glint, tide and ecological identity remain untested.

## Supplied ACOLITE products

Sources: **22 NetCDF headers**, corresponding GeoTIFF headers, and 66 supplied settings text files under `S2/ACOLITE/`. No supplied processing script was run. NetCDF globals explicitly identify `generated_by=ACOLITE`, sensors S2A_MSI, S2B_MSI, S2C_MSI, and `acolite_file_type=L2W`.

Header acquisition interval (`isodate`): 2025-01-06T11:45:53.286481+00:00 through 2025-12-27T11:45:55.402868+00:00. The header generation time is separate from acquisition time; source settings describe runs in April 2026. Old Windows input/output paths are historical provenance, not accessible Linux data locations.

The headers declare WGS84 UTM zone 28 projection parameters, 10 m signed pixel spacing, per-file `data_dimensions`, source tile/granule IDs, clipping limits and polygon paths. `warp_resampling_method=bilinear` and `atmospheric_correction_method=dark_spectrum` occur in the inspected ACOLITE header/settings. This documents supplied processing choices; their execution and suitability were not independently validated.

Representative source: `S2/ACOLITE/2025-01-06/S2A_MSI_2025_01_06_11_45_53_T28QCH_L2W.nc`. All file-specific variables are in the CSV. Representative schema:

| Variable | Type | Declared units | Header meaning |
| --- | --- | --- | --- |
| /transverse_mercator | double | undocumented | undocumented |
| /x | double | m | x coordinate of projection |
| /y | double | m | y coordinate of projection |
| /lon | float | degree_east | longitude |
| /lat | float | degree_north | latitude |
| /rhos_443 | float | 1 | Surface reflectance |
| /rhos_492 | float | 1 | Surface reflectance |
| /rhos_560 | float | 1 | Surface reflectance |
| /rhos_665 | float | 1 | Surface reflectance |
| /rhos_704 | float | 1 | Surface reflectance |
| /rhos_740 | float | 1 | Surface reflectance |
| /rhos_783 | float | 1 | Surface reflectance |
| /rhos_833 | float | 1 | Surface reflectance |
| /rhos_865 | float | 1 | Surface reflectance |
| /rhos_1614 | float | 1 | Surface reflectance |
| /rhos_2202 | float | 1 | Surface reflectance |
| /l2_flags | int | undocumented | undocumented |

Reflectance variables explicitly carry `long_name=Surface reflectance`, `standard_name=surface_bidirectional_reflectance`, unit `1`, and wavelength metadata including `wave_nm`. Wavelength labels vary by platform/product; no common band-center table was imposed. GeoTIFF reflectance bands may declare NaN NoData, while the representative NetCDF reflectance variables have no explicit `_FillValue` attribute. These are separate declarations; no missing-value behavior was inferred from observation arrays.

The 2026-named ACOLITE subdirectories contain GeoTIFFs without corresponding supplied NetCDF/settings files. Dates/platforms inferred only from those filenames are not independently established acquisition metadata. Their TIFF headers remain individually inventoried.

`l2_flags` is a flag variable; settings supply flag-exponent names and masking switches. Those source declarations are preserved, but flag values were not read and mask application was not checked. Source settings contain generic defaults for many other sensors; those do not establish that such datasets are present. Processing status, atmospheric validation and independent accuracy remain unassessed.

## Vector layers

Sources: each `.shp` fixed header (geometry code and stored bounds), `.dbf` descriptors (fields, widths, decimals and declared record count), `.prj` and `.cpg`. No features or attribute-record values were read. The `.qmd` sidecars are QGIS XML metadata, not Quarto source; their title/abstract/CRS metadata are largely blank.

| Shapefile relative path | Geometry | Declared DBF records | Fields | CRS / units |
| --- | --- | --- | --- | --- |
| SHP/ICE_CREAMS_Training/Training_V1.3.1.shp | Polygon | 55 | Class:C(20,0) | WGS 1984 geographic / Degree |
| SHP/POI_S2C_ACOLITE_targets.shp | Point | 6 | Name:C(80,0); Class:C(80,0) | WGS 1984 UTM Zone 28N / Meter |
| SHP/TimeSeries_Polygons_Matchup.shp | Polygon | 2 | id:N(10,0); AOI:C(10,0) | WGS 1984 UTM Zone 28N / Meter |
| SHP/extent.shp | Polygon | 1 | id:N(10,0) | WGS 1984 UTM Zone 28N / Meter |
| SHP/mask/Intertidal_merged.shp | Polygon | 83 | area:N(24,15) | WGS 1984 UTM Zone 28N / Meter |
| SHP/mask/square_mask.shp | Polygon | 1 | id:N(10,0) | WGS 1984 UTM Zone 28N / Meter |
| SHP/s2_mask_test.shp | Polygon | 1 | FID:N(11,0); FID_2:N(11,0) | WGS 1984 UTM Zone 28N / Meter |

DBF `C` and `N` are literal stored character and numeric descriptors. `Class`, `AOI`, `Name`, `id`, `FID`, `FID_2` and `area` meanings and code domains are undocumented. In particular, a projected metre CRS does not establish the units of an `area` attribute. No training-label independence, class validity, geometry validity, coverage completeness or ecological identity was assessed. The additional `SHP/mask/Intertidal_merged.zip` is inventoried by member; no content-equivalence claim is made about its expanded namesake. Sidecars remain associated by their literal common stems.

## Sentinel-5P aerosol-index products and supporting files

Sources: **132 NetCDF root/group/variable headers** under `Sentinel5P/`. Root attributes explicitly identify KNMI, Sentinel-5 precursor, TROPOMI and Level-2 swath aerosol-index products. Per-file acquisition time, processing history/version, orbit, geographic metadata and declared spatial resolution are preserved. The filename tokens OFFL/RPRO remain literal supplied product identifiers; no product equivalence is inferred.

Header time-coverage start interval: 2018-05-08T13:23:13Z through 2026-03-07T14:38:52Z. The full swaths are not local coastal grids. Latitude/longitude arrays describe pixel centers; four-corner bounds appear under `/PRODUCT/SUPPORT_DATA/GEOLOCATIONS`. Root latitude/longitude limits are supplied metadata, not extents recalculated from arrays. CRS/datum is not assumed from latitude/longitude labels.

Declared spatial-resolution strings present in this collection: 5.5x3.5 km2, 7.0x3.5 km2. Dimensions vary by file and remain in the variable dictionary; no common grid or resampling was imposed.

Representative source: `Sentinel5P/S5P_OFFL_L2__AER_AI_20220815T135114_20220815T153243_25072_03_020400_20220818T080041.nc`.

| Variable | Type | Units | Declared fill / scale |
| --- | --- | --- | --- |
| /PRODUCT/time | int | seconds since 2010-01-01 00:00:00 | -2147483647.0; scale undocumented |
| /PRODUCT/latitude | float | degrees_north | 9.969209968386869e+36; scale undocumented |
| /PRODUCT/longitude | float | degrees_east | 9.969209968386869e+36; scale undocumented |
| /PRODUCT/delta_time | int | milliseconds since 2022-08-15 00:00:00 | -2147483647.0; scale undocumented |
| /PRODUCT/time_utc | string | undocumented | ['']; scale undocumented |
| /PRODUCT/qa_value | ubyte | 1 | 255.0; scale 0.009999999776482582 |
| /PRODUCT/aerosol_index_354_388 | float | 1 | 9.969209968386869e+36; scale undocumented |
| /PRODUCT/aerosol_index_340_380 | float | 1 | 9.969209968386869e+36; scale undocumented |
| /PRODUCT/aerosol_index_335_367 | float | 1 | 9.969209968386869e+36; scale undocumented |

Aerosol-index wavelength pairs and their precision variables are declared in the product attributes; values are dimensionless (`1`). The representative `qa_value` is packed unsigned byte, with scale approximately 0.01, offset 0, packed valid range 0–100 and fill 255. Its source comment describes a 0–1 quality descriptor and suggests ignoring values below 0.5; this inventory applies no threshold. Quality descriptors are not independent classification accuracy or ecological evidence.

The full CSV includes geolocation, detailed results, input-data/support variables and existing QA-statistics **schemas**. No QA histogram, probability-density array, wind/aerosol field or other variable array was read. Existing product summaries were not recalculated or used as research findings.

`Sentinel5P/Figures_AER_AI/` has 45 supplied PNG files. They are inventoried as supplied previews, not figures generated or validated by this task. `plot_data.m` and `missing_dates_5P.m` are supplied MATLAB code and were not executed. The latter’s text describes exporting a `Date` column to `S2_S5P_common_dates.csv`; only the CSV header was inventoried. Date matches were not recomputed or validated, and no inference is made from the plotted content.

## Spectral-response reference workbook

Source: `COPE-GSEG-EOPG-TN-15-0007 - Sentinel-2 Spectral Response Functions 2024 - 4.0.xlsx`, OOXML workbook/sheet headers and bounded metadata rows. The Overview identifies the title, document code and version 4.0. This is an instrument-response reference, not an in-situ campaign observation or atmospheric-correction result. File modification dates are not acquisition dates.

| Sheet | Declared used range | Schema / interpretation |
| --- | --- | --- |
| Overview | A1:F35 | bounded metadata/header rows; not rectangular data |
| Spectral Responses (S2A) | A1:V2302 | first row labels + first data row storage types |
| Spectral Responses (S2B) | A1:P2306 | first row labels + first data row storage types |
| Spectral Responses (S2C) | A1:P2306 | first row labels + first data row storage types |
| VNIR SR S2A, S2B & S2C | T8:T9 | bounded metadata/header rows; not rectangular data |
| SWIR SR S2A, S2B & S2C | A1 | bounded metadata/header rows; not rectangular data |
| Equivalent Wavelengths | B2:H16 | bounded metadata/header rows; not rectangular data |
| Bandwidth and mid-wavelength | A2:I18 | bounded metadata/header rows; not rectangular data |
| Variation  S2C ISRF over pixels | A1:L18 | bounded metadata/header rows; not rectangular data |

The three `Spectral Responses (S2A/S2B/S2C)` sheets begin with `SR_WL` and 13 platform-specific `S2*_SR_AV_B*` labels. All are enumerated in the CSV. Response normalization and units are not asserted from numeric values. The Equivalent Wavelengths and Bandwidth/mid-wavelength headers explicitly use nm. The S2C variation sheet contains supplied reference columns for min/avg/max/range/std; this task describes those labels and does not recompute them. The VNIR/SWIR visualization sheets are not rectangular measurement tables. Workbook used ranges include layout/formatting and are not verified sample counts. Authorship/source distribution is not independently authenticated by a local workbook path.

## Relationships, omissions and metadata gaps

Literal identifiers and historical processing paths are preserved. ACOLITE header `inputfile`, granule/tile ID, `rhot_ds`/`rhos_ds` and polygon paths document intended lineage; NetCDF coordinate/bounds/ancillary-variable attributes document within-file links. None establishes a verified match to another supplied file. Station case/format, dates, masks, Sentinel platforms and product grids were not reconciled.

The inventory covers all four stated data roots and all physical files found beneath them. Source headers were read for every accessible NetCDF, raster, shapefile, workbook and ZIP. Small metadata and settings were read within stated bounds. Scientific-code directories, `.venv`, caches, Git objects, template fixture data and synchronized PI-workspace copies are not supplied datasets and were excluded from data-root counts. Their repository revision is recorded. No search beyond authorized project/data scope was made.

Two pre-existing raster `.aux.xml` files could not be parsed as XML; their parent raster headers were readable. Both errors report an XML declaration away from the start of the entity:

- `project_raw:S2/S2B_MSIL2A_20260307T113319_N0512_R080_T28QCH_20260307T154921.SAFE/GRANULE/L2A_T28QCH_A047010_20260307T114112/IMG_DATA/R10m/T28QCH_20260307T113319_TCI_10m.jp2.aux.xml`: XML or text declaration not at start of entity: line 26, column 4
- `project_raw:S2/S2B_MSIL2A_20260327T113319_N0512_R080_T28QCH_20260327T152639.SAFE/GRANULE/L2A_T28QCH_A047296_20260327T113507/IMG_DATA/R10m/T28QCH_20260327T113319_TCI_10m.jp2.aux.xml`: XML or text declaration not at start of entity: line 26, column 4

These sidecars were preserved and not repaired. Archive CRC values are copied from central directories; payload CRCs and archive integrity were not tested. ZIP raster/feature payloads were not extracted or scanned; archived raster encoding/dimensions rely on supplied XML rather than every image header. Browse imagery was inventoried without interpreting image pixels. Metadata XML is bounded to 4 MiB, small text to 64 KiB, netCDF attributes to 65,536 elements, and workbook schema inspection to header rows plus first-data-row cell types. Oversized/unsupported payloads remain identifiable in the inventory.

Field spectral units/scaling, instrument calibration/model, field-code definitions, geographic datum/accuracy, missing-code conventions and independent validation provenance remain unresolved where not explicitly documented. No observation values were used to fill those gaps. Recorded source stat tuples were unchanged through inventory; that check cannot prove byte identity or detect changes preserving all recorded metadata. No data permissions were changed.

## Reproducibility and review

Repository snapshot: branch `ctr-25-data-dictionary`, starting commit `b023b619886b2a174a8b653bfc90166b7d001332`. The current report revision is identified by SHA-256 in `provenance/deliverable_manifest.json`; a report cannot contain its own final hash. Lockfile hashes, software versions, commands and source snapshot are in the provenance files. Python 3.12.3, GDAL 3.8.4, released 2024/02/08, libnetcdf `4.9.2 of Mar 31 2024 08:09:36 $`. No dependencies or system software were installed.

`verify-ready --task-id CTR-25 --agent roger-tomlinson --path analysis/CTR-24_data-dictionary/` returned `ready`, `affected=false`: independent analysis paths do not depend on PI synchronization. All writes stay in this directory. Protected manuscript/safeguard paths and the PI workspace were not modified. The directory uses the parent request’s CTR-24 convention; `task.yml` records CTR-25 as the implementation task.

From the project root:

```bash
.venv/bin/python analysis/CTR-24_data-dictionary/scripts/inventory.py
.venv/bin/python analysis/CTR-24_data-dictionary/scripts/enrich_metadata.py
.venv/bin/python analysis/CTR-24_data-dictionary/scripts/build_report.py
.venv/bin/python analysis/CTR-24_data-dictionary/scripts/validate.py
./scripts/render-analysis.sh analysis/CTR-24_data-dictionary
```

The Quarto report contains static documentation and uses its own `_quarto.yml`; it has no executable scientific chunks and does not render the root manuscript. Re-running snapshots current files and timestamps, so source-stat identifiers may change.

| Deliverable | Use |
| --- | --- |
| report.md / report.qmd / report.html | Readable dictionary, editable source and self-contained HTML |
| tables/file_inventory.csv | Exact root/path/size/role/metadata status for every physical file |
| tables/archive_inventory.csv | Exact ZIP member names, sizes, compression and stored CRC |
| tables/variable_dictionary.csv | All inspected fields/bands, types, units, scale/offset/fill/flags and evidence |
| tables/dataset_metadata.csv | Per-dataset sensor/time/processing/grid/schema index |
| outputs/headers.json | Detailed captured header metadata; distributed in the metadata bundle, excluded from Git |
| scripts/ | Metadata inventory, enrichment, report builder and validator |
| provenance/ | Commands, versions, read errors, source snapshot, validation and deliverable hashes |

Karl Popper should independently check path/file coverage, source-cited definitions, uncertainty labels, metadata-only operations and reproducibility. His review is CTR-26. Charles Darwin consolidates on CTR-24. This documentation handoff makes no scientific approval claim and does not authorize manuscript integration or publication.
