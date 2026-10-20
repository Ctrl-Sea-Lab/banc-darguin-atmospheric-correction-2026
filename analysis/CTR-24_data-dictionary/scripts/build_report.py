#!/usr/bin/env python3
"""Build descriptive Markdown/Quarto from captured headers; no source-data reads."""
import csv,json,hashlib
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parents[1]
H=json.loads((P/'outputs/headers.json').read_text());S=json.loads((P/'provenance/inventory_run.json').read_text())
F=list(csv.DictReader((P/'tables/file_inventory.csv').open()));V=list(csv.DictReader((P/'tables/variable_dictionary.csv').open()))
def table(cols,rows):
 def esc(x):return str(x).replace('|','\\|').replace('\n',' ')
 return '\n'.join(['| '+' | '.join(cols)+' |','| '+' | '.join(['---']*len(cols))+' |']+['| '+' | '.join(esc(x) for x in row)+' |' for row in rows])+'\n'
def short(k):return k.split(':',1)[1]
def net(group):return [(k,h) for k,h in H.items() if group in k and k.endswith('.nc')]
def period(vals):
 vals=sorted(v for v in vals if v);return (vals[0]+' through '+vals[-1]) if vals else 'undocumented'
# Per-dataset metadata index for discoverability. Empty fields explicitly undocumented.
D=[]
for k,h in H.items():
 r=dict(source=k,metadata_evidence='outputs/headers.json :: '+k,sensor='undocumented',acquisition='undocumented',processing_level='undocumented',crs='undocumented',dimensions='undocumented',resolution='undocumented',variables='undocumented')
 if k.endswith('.nc'):
  a=h['/']['attributes'];r.update(sensor=a.get('sensor',a.get('source','undocumented')),acquisition=a.get('isodate',a.get('time_coverage_start','undocumented')),processing_level=a.get('acolite_file_type',a.get('source','undocumented')),crs=a.get('proj4_string','swath latitude/longitude; datum not declared in root attributes'),resolution=str(a.get('pixel_size',a.get('spatial_resolution','undocumented'))),dimensions=str(a.get('data_dimensions','per-variable dimensions in variable_dictionary.csv')),variables=';'.join(x['name'] for g in h.values() for x in g['variables']))
 elif 'bands' in h:
  r.update(crs=h.get('coordinateSystem',{}).get('wkt','undocumented'),dimensions=str(h.get('size')),resolution=str(h.get('geoTransform','undocumented')),variables=';'.join(str(b['band'])+':'+b.get('type','') for b in h['bands']))
 elif 'fields' in h and k.endswith('.shp'):
  r.update(crs=h['.prj'],dimensions='declared DBF records '+str(h['declared_records']),variables=';'.join(x['name'] for x in h['fields']),resolution='vector; no pixel resolution')
 elif 'sheets' in h:
  r.update(dimensions='; '.join(s['name']+':'+str(s['declared_used_range']) for s in h['sheets']),variables='see workbook sheet/field entries in variable_dictionary.csv')
 elif k.endswith('.zip'):
  r['dimensions']=str(h['members'])+' archive entries; see archive_inventory.csv';r['variables']='see selected_metadata and safe_structured_metadata in headers.json'
 else:continue
 D.append(r)
with (P/'tables/dataset_metadata.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,list(D[0]));w.writeheader();w.writerows(D)
sections=[]
def add(s):sections.append(s.strip()+'\n')
add('''# Banc d’Arguin 2026 — descriptive data dictionary

**CTR-25, supporting CTR-24. Documentation only; scientific analysis not started.**

This dictionary describes supplied files and declared schemas. No measurement statistics, model, classification, atmospheric correction, map, figure, ecological interpretation, or cross-dataset matching was produced. Internal review is pending Karl Popper (CTR-26). There is no PI scientific approval, manuscript-integration authorization, merge authorization, or publication authorization.
''')
add(f'''## Snapshot and locations

The inventory ran from **{S['started_utc']}** to **{S['ended_utc']}** on Linux Mint 22.3. It found **847 supplied files** and **2 Git placeholders**, totaling **{sum(int(f['size_bytes']) for f in F):,} bytes**. Archive members are listed separately and are not added to physical-file totals. There are **{S['archive_members']:,} ZIP entries** (including directories) and **{len(V):,} variable/band/reference-column records**. These are documentation counts, not measurement statistics.

The PI’s added files are physically under the repository-local `data/raw/`. This supersedes the empty-data description in the initialization README/config. No data were moved, renamed, or reprotected.
''')
add(table(['Root key','Exact directory','Physical files'],[(k,v,S['root_status'][k]['physical_file_count']) for k,v in S['roots'].items()]))
add('''`project_raw` is not a symlink. Both NAS roots are empty; `project_processed` contains only `.gitkeep`. Data can already be processed products even when stored under `raw/`; location is not a processing-level definition. File inventory captures every file’s path, bytes, timestamp, mode, UID/GID, role and metadata status. No symlink entries were present.

No whole-data content checksum was calculated. The source snapshot identifier below hashes sorted file-stat records, not measurement bytes:
''')
add('`'+S['source_snapshot_sha256']+'`')
add('''## Available groups

All paths in this table are relative to `project_raw`. Group labels derived from directory names are organizational labels; headers provide sensor/product definitions below.
''')
gdesc={'ASD':'Field spectrum table, field-cover table and measurement log','GPS':'Field information workbook','S2/ACOLITE':'Supplied ACOLITE NetCDF/GeoTIFF products and run settings','S2/expanded_SAFE':'Two expanded Level-2A SAFE products, imagery and metadata','S2/Sen2Cor':'46 zipped SAFE products; folder label Sen2Cor','SHP':'Seven shapefile sets, sidecars, QGIS metadata, one ZIP','Sentinel5P':'132 NetCDF products, 45 PNGs, two MATLAB scripts, one CSV','spectral_response_reference':'Sentinel-2 spectral-response reference workbook'}
add(table(['Group / relative location','Files','Bytes','Contents'],[(g,sum(f['group']==g for f in F),sum(int(f['size_bytes']) for f in F if f['group']==g),d) for g,d in gdesc.items()]))
add('''## Field spectroscopy and cover

Sources: `ASD/202603_Reflectance_avg.txt` first-line header, `ASD/202603_Seagrass_cover.txt` first-line header, and the complete 2,318-byte `ASD/202603_Measurement_log.txt`.

The log explicitly describes ASD seagrass-cover measurements, core-related measurements, and measurements for Sentinel-2 atmospheric-correction validation. It lists day01–day08 dated **2026-03-22 through 2026-03-29** and site names Ebel Kheaiznaya, Aouatif, Niroumi, Arel and Zira. These are source-log descriptions, not verified habitat identities or geographic extents. Listed participants include Jim, Pierre, Hacen, Laurent and Simon. ASD instrument model, calibration certificate, footprint, angular geometry, reflectance units, wavelength units, uncertainty and averaging method are undocumented.

The log states “number to save 20” and white/dark/sample counts of 50/20/50. These are recorded instrument settings; the number of usable observations was not checked. Drone flights are mentioned, but no separate UAV image/LiDAR dataset is present in this bounded inventory.
''')
sp=H['project_raw:ASD/202603_Reflectance_avg.txt']['literal_fields']
add(f'''The spectrum file is whitespace-delimited with **{len(sp)} literal columns**: `wl` followed by **{len(sp)-1} spectrum/station labels**, all enumerated in `variable_dictionary.csv`. The interpretation as averaged reflectance is inferred from the filename and field-log context, not a declared unit or processing specification. `wl` suggests wavelength, but its unit is undocumented. Rows were not counted and spectral values were not summarized.

Labels preserve case and punctuation, for example `d01_A`, `d02_C327`, `D05_H1`, `AC_01` and `D07_R`. Do not silently normalize these or assume they join the cover/GPS identifiers. The log’s `AC01-08` spelling differs from the spectrum-header convention. A day08 log entry is not proof that corresponding spectral columns were supplied.
''')
add(table(['Cover field','Definition supported by documentation'],[(v['variable'],v['description']) for v in V if v['source']=='project_raw:ASD/202603_Seagrass_cover.txt']))
add('''The cover table is tab-delimited. Column storage types are undeclared text serialization. A numeric-looking cover does not establish a percentage unit. Literal `NA` text occurs in the bounded initial schema inspection, but no formal missing-value convention is supplied; it was not recoded. Species/code meanings such as `zn` are undocumented. No row-level exclusions or joins were made.

## Field information workbook

Source: `GPS/Info spectral measure_biomass core_BdA 2026.xlsx`, `Sheet1!A1:L1`, OOXML dimension `A1:L131`, and first-data-row storage types/styles. The declared used range may include formatting and is not a validated record count. The 12 headers are:
''')
gps=[v for v in V if v['source'].startswith('project_raw:GPS/')]
add(table(['Field','Storage evidence','Meaning / limitation'],[(v['variable'].split('!')[-1],v['storage_type'],v['description']) for v in gps]))
add('''The workbook has numeric and shared-string cell types; numeric Excel dates retain their source style and number-format IDs in `headers.json`. No date-column scan or coordinate transformation was performed. `lat`/`lon` suggest geographic coordinates, but the datum, CRS, coordinate units, positional accuracy and GPS device model are not declared in the inspected schema. `cover`, `comment`, `Zone` and `poskey` have no supplied complete codebook. The `gps` column differs structurally from `waypoint`; neither is assumed equivalent to the text-table `gps` field. Biomass/core measurements are suggested by the filename, but no column explicitly defines measured biomass, its units, or its protocol.

## Sentinel-2 SAFE products

Sources: each product’s `MTD_MSIL2A.xml` (product identity, processing baseline, quantification, offsets, special values and spectral definitions), granule `MTD_TL.xml` (sensing time, CRS and grid), JP2 headers for expanded products, and ZIP central directories for archived products. Exact archive/member addresses are in `archive_inventory.csv` and the SAFE rows of `variable_dictionary.csv`.

`S2/Sen2Cor/` contains 46 ZIP files. The folder name is a supplied label; actual XML declares Level-2A products and spacecraft. `S2/` also contains two expanded Sentinel-2B Level-2A SAFE directories with product-start dates 2026-03-07 and 2026-03-27. This does not establish that archives and expanded directories are distinct acquisitions in a complete timeseries. No duplicate-content or cross-product comparison was performed.
''')
ident=[]
for k,h in H.items():
 sm=h.get('safe_structured_metadata',{})
 if k.endswith('.zip'):
  for member,m in sm.items():
   if isinstance(m,dict):ident.extend((k+'!'+member,x) for x in m.get('product_identity',[]))
 elif k.endswith('.xml') and isinstance(sm,dict):ident.extend((k,x) for x in sm.get('product_identity',[]))
add('Declared product-start interval across accessible XML metadata: '+period([x['text'] for k,x in ident if x['tag']=='PRODUCT_START_TIME'])+'.')
add('''The granule headers declare **WGS84 / UTM zone 28N, EPSG:32628**. Typical tile grids explicitly listed in the inspected `MTD_TL.xml` are 10 m (10,980 × 10,980), 20 m (5,490 × 5,490) and 60 m (1,830 × 1,830), with signed Y pixel spacing. Every file’s actual header dimensions/geotransform are retained; no co-registration or pixel alignment test was made.

Spectral metadata enumerate B1, B2, B3, B4, B5, B6, B7, B8, B8A, B9, B10, B11 and B12, each with wavelength bounds/central wavelength in nm and nominal resolution. A metadata definition, including B10, does not prove that an image of that band is present in a particular Level-2A archive. Use the member inventory to establish actual files. Expanded imagery also includes ancillary/display/quality layers such as AOT, WVP, SCL and TCI; these are not additional reflectance bands.

For example, `S2/Sen2Cor/S2A_MSIL2A_20250106T113451_N0511_R080_T28QCG_20250106T154249.zip!…SAFE/MTD_MSIL2A.xml` declares processing baseline 05.11, BOA quantification value 10,000, BOA offsets −1,000 indexed by band, AOT quantification 1,000, WVP quantification 1,000 with unit cm, special values NODATA=0 and SATURATED=65,535. These are literal encoding metadata; no reflectance conversion was applied. Per-product definitions must be consulted rather than transferring this example to a different processor’s products.

Scene-classification labels/codes, product quality declarations and masks are retained from metadata. They were not evaluated and do not constitute independently assessed classification accuracy. Atmospheric-correction adequacy, adjacency effects, glint, tide and ecological identity remain untested.

## Supplied ACOLITE products
''')
acs=net('/ACOLITE/')
add(f'''Sources: **{len(acs)} NetCDF headers**, corresponding GeoTIFF headers, and 66 supplied settings text files under `S2/ACOLITE/`. No supplied processing script was run. NetCDF globals explicitly identify `generated_by=ACOLITE`, sensors {', '.join(sorted({h['/']['attributes'].get('sensor','undocumented') for k,h in acs}))}, and `acolite_file_type=L2W`.

Header acquisition interval (`isodate`): {period([h['/']['attributes'].get('isodate') for k,h in acs])}. The header generation time is separate from acquisition time; source settings describe runs in April 2026. Old Windows input/output paths are historical provenance, not accessible Linux data locations.

The headers declare WGS84 UTM zone 28 projection parameters, 10 m signed pixel spacing, per-file `data_dimensions`, source tile/granule IDs, clipping limits and polygon paths. `warp_resampling_method=bilinear` and `atmospheric_correction_method=dark_spectrum` occur in the inspected ACOLITE header/settings. This documents supplied processing choices; their execution and suitability were not independently validated.
''')
samplek,sample=acs[0]
add('Representative source: `'+short(samplek)+'`. All file-specific variables are in the CSV. Representative schema:')
add(table(['Variable','Type','Declared units','Header meaning'],[(x['name'],x['type'],x['attributes'].get('units','undocumented'),x['attributes'].get('long_name','undocumented')) for x in sample['/']['variables']]))
add('''Reflectance variables explicitly carry `long_name=Surface reflectance`, `standard_name=surface_bidirectional_reflectance`, unit `1`, and wavelength metadata including `wave_nm`. Wavelength labels vary by platform/product; no common band-center table was imposed. GeoTIFF reflectance bands may declare NaN NoData, while the representative NetCDF reflectance variables have no explicit `_FillValue` attribute. These are separate declarations; no missing-value behavior was inferred from observation arrays.

The 2026-named ACOLITE subdirectories contain GeoTIFFs without corresponding supplied NetCDF/settings files. Dates/platforms inferred only from those filenames are not independently established acquisition metadata. Their TIFF headers remain individually inventoried.

`l2_flags` is a flag variable; settings supply flag-exponent names and masking switches. Those source declarations are preserved, but flag values were not read and mask application was not checked. Source settings contain generic defaults for many other sensors; those do not establish that such datasets are present. Processing status, atmospheric validation and independent accuracy remain unassessed.

## Vector layers

Sources: each `.shp` fixed header (geometry code and stored bounds), `.dbf` descriptors (fields, widths, decimals and declared record count), `.prj` and `.cpg`. No features or attribute-record values were read. The `.qmd` sidecars are QGIS XML metadata, not Quarto source; their title/abstract/CRS metadata are largely blank.
''')
shapes=[(k,h) for k,h in H.items() if k.endswith('.shp')]
add(table(['Shapefile relative path','Geometry','Declared DBF records','Fields','CRS / units'],[(short(k),'Point' if h['shape_type_code']==1 else 'Polygon' if h['shape_type_code']==5 else str(h['shape_type_code']),h['declared_records'],'; '.join(x['name']+':'+x['dbf_type']+'('+str(x['width'])+','+str(x['decimals'])+')' for x in h['fields']),'WGS 1984 geographic / Degree' if 'ICE_CREAMS' in k else 'WGS 1984 UTM Zone 28N / Meter') for k,h in shapes]))
add('''DBF `C` and `N` are literal stored character and numeric descriptors. `Class`, `AOI`, `Name`, `id`, `FID`, `FID_2` and `area` meanings and code domains are undocumented. In particular, a projected metre CRS does not establish the units of an `area` attribute. No training-label independence, class validity, geometry validity, coverage completeness or ecological identity was assessed. The additional `SHP/mask/Intertidal_merged.zip` is inventoried by member; no content-equivalence claim is made about its expanded namesake. Sidecars remain associated by their literal common stems.

## Sentinel-5P aerosol-index products and supporting files
''')
s5=net('Sentinel5P/')
add(f'''Sources: **{len(s5)} NetCDF root/group/variable headers** under `Sentinel5P/`. Root attributes explicitly identify KNMI, Sentinel-5 precursor, TROPOMI and Level-2 swath aerosol-index products. Per-file acquisition time, processing history/version, orbit, geographic metadata and declared spatial resolution are preserved. The filename tokens OFFL/RPRO remain literal supplied product identifiers; no product equivalence is inferred.

Header time-coverage start interval: {period([h['/']['attributes'].get('time_coverage_start') for k,h in s5])}. The full swaths are not local coastal grids. Latitude/longitude arrays describe pixel centers; four-corner bounds appear under `/PRODUCT/SUPPORT_DATA/GEOLOCATIONS`. Root latitude/longitude limits are supplied metadata, not extents recalculated from arrays. CRS/datum is not assumed from latitude/longitude labels.

Declared spatial-resolution strings present in this collection: {', '.join(sorted({str(h['/']['attributes'].get('spatial_resolution','undocumented')) for k,h in s5}))}. Dimensions vary by file and remain in the variable dictionary; no common grid or resampling was imposed.
''')
k,h=s5[0]
selected=[x for x in h['/PRODUCT']['variables'] if x['name'].split('/')[-1] in ['time','delta_time','time_utc','latitude','longitude','qa_value','aerosol_index_354_388','aerosol_index_340_380','aerosol_index_335_367']]
add('Representative source: `'+short(k)+'`.')
add(table(['Variable','Type','Units','Declared fill / scale'],[(x['name'],x['type'],x['attributes'].get('units','undocumented'),str(x['attributes'].get('_FillValue','undocumented'))+'; scale '+str(x['attributes'].get('scale_factor','undocumented'))) for x in selected]))
add('''Aerosol-index wavelength pairs and their precision variables are declared in the product attributes; values are dimensionless (`1`). The representative `qa_value` is packed unsigned byte, with scale approximately 0.01, offset 0, packed valid range 0–100 and fill 255. Its source comment describes a 0–1 quality descriptor and suggests ignoring values below 0.5; this inventory applies no threshold. Quality descriptors are not independent classification accuracy or ecological evidence.

The full CSV includes geolocation, detailed results, input-data/support variables and existing QA-statistics **schemas**. No QA histogram, probability-density array, wind/aerosol field or other variable array was read. Existing product summaries were not recalculated or used as research findings.

`Sentinel5P/Figures_AER_AI/` has 45 supplied PNG files. They are inventoried as supplied previews, not figures generated or validated by this task. `plot_data.m` and `missing_dates_5P.m` are supplied MATLAB code and were not executed. The latter’s text describes exporting a `Date` column to `S2_S5P_common_dates.csv`; only the CSV header was inventoried. Date matches were not recomputed or validated, and no inference is made from the plotted content.

## Spectral-response reference workbook

Source: `COPE-GSEG-EOPG-TN-15-0007 - Sentinel-2 Spectral Response Functions 2024 - 4.0.xlsx`, OOXML workbook/sheet headers and bounded metadata rows. The Overview identifies the title, document code and version 4.0. This is an instrument-response reference, not an in-situ campaign observation or atmospheric-correction result. File modification dates are not acquisition dates.
''')
srfk=next(k for k in H if 'COPE-' in k);srf=H[srfk]
add(table(['Sheet','Declared used range','Schema / interpretation'],[(s['name'],s['declared_used_range'],s['schema_strategy']) for s in srf['sheets']]))
add('''The three `Spectral Responses (S2A/S2B/S2C)` sheets begin with `SR_WL` and 13 platform-specific `S2*_SR_AV_B*` labels. All are enumerated in the CSV. Response normalization and units are not asserted from numeric values. The Equivalent Wavelengths and Bandwidth/mid-wavelength headers explicitly use nm. The S2C variation sheet contains supplied reference columns for min/avg/max/range/std; this task describes those labels and does not recompute them. The VNIR/SWIR visualization sheets are not rectangular measurement tables. Workbook used ranges include layout/formatting and are not verified sample counts. Authorship/source distribution is not independently authenticated by a local workbook path.

## Relationships, omissions and metadata gaps

Literal identifiers and historical processing paths are preserved. ACOLITE header `inputfile`, granule/tile ID, `rhot_ds`/`rhos_ds` and polygon paths document intended lineage; NetCDF coordinate/bounds/ancillary-variable attributes document within-file links. None establishes a verified match to another supplied file. Station case/format, dates, masks, Sentinel platforms and product grids were not reconciled.

The inventory covers all four stated data roots and all physical files found beneath them. Source headers were read for every accessible NetCDF, raster, shapefile, workbook and ZIP. Small metadata and settings were read within stated bounds. Scientific-code directories, `.venv`, caches, Git objects, template fixture data and synchronized PI-workspace copies are not supplied datasets and were excluded from data-root counts. Their repository revision is recorded. No search beyond authorized project/data scope was made.

Two pre-existing raster `.aux.xml` files could not be parsed as XML; their parent raster headers were readable. Both errors report an XML declaration away from the start of the entity:
''')
add('\n'.join('- `'+e['source']+'`: '+e['error'] for e in S['errors']))
add('''
These sidecars were preserved and not repaired. Archive CRC values are copied from central directories; payload CRCs and archive integrity were not tested. ZIP raster/feature payloads were not extracted or scanned; archived raster encoding/dimensions rely on supplied XML rather than every image header. Browse imagery was inventoried without interpreting image pixels. Metadata XML is bounded to 4 MiB, small text to 64 KiB, netCDF attributes to 65,536 elements, and workbook schema inspection to header rows plus first-data-row cell types. Oversized/unsupported payloads remain identifiable in the inventory.

Field spectral units/scaling, instrument calibration/model, field-code definitions, geographic datum/accuracy, missing-code conventions and independent validation provenance remain unresolved where not explicitly documented. No observation values were used to fill those gaps. Recorded source stat tuples were unchanged through inventory; that check cannot prove byte identity or detect changes preserving all recorded metadata. No data permissions were changed.

## Reproducibility and review
''')
add(f'''Repository snapshot: branch `{S['git_branch']}`, starting commit `{S['git_head']}`. The current report revision is identified by SHA-256 in `provenance/deliverable_manifest.json`; a report cannot contain its own final hash. Lockfile hashes, software versions, commands and source snapshot are in the provenance files. Python {S['python'].split()[0]}, {S['gdal']}, libnetcdf `{S['libnetcdf']}`. No dependencies or system software were installed.

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
''')
add(table(['Deliverable','Use'],[
 ('report.md / report.qmd / report.html','Readable dictionary, editable source and self-contained HTML'),
 ('tables/file_inventory.csv','Exact root/path/size/role/metadata status for every physical file'),
 ('tables/archive_inventory.csv','Exact ZIP member names, sizes, compression and stored CRC'),
 ('tables/variable_dictionary.csv','All inspected fields/bands, types, units, scale/offset/fill/flags and evidence'),
 ('tables/dataset_metadata.csv','Per-dataset sensor/time/processing/grid/schema index'),
 ('outputs/headers.json','Detailed captured header metadata; distributed in the metadata bundle, excluded from Git'),
 ('scripts/','Metadata inventory, enrichment, report builder and validator'),
 ('provenance/','Commands, versions, read errors, source snapshot, validation and deliverable hashes')]))
add('''Karl Popper should independently check path/file coverage, source-cited definitions, uncertainty labels, metadata-only operations and reproducibility. His review is CTR-26. Charles Darwin consolidates on CTR-24. This documentation handoff makes no scientific approval claim and does not authorize manuscript integration or publication.''')
body='\n'.join(sections)
(P/'report.md').write_text(body)
(P/'report.qmd').write_text('---\ntitle: "Banc d’Arguin 2026 — descriptive data dictionary"\nauthor: "Roger Tomlinson"\nexecute:\n  enabled: false\n---\n\n'+body)
print('Report written:',len(body),'characters; dataset index rows',len(D))
