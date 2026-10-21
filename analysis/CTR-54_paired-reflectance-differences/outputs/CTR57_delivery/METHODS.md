# Geospatial methods and limitations — draft for scientific review

**Take-home message:** This investigation measures disagreement between two atmospheric corrections on matched Sentinel-2 observations. It cannot establish which correction is accurate or identify ecological causes of a difference.

**Meaningful results:** Numerical findings are generated in `report.qmd` after processing. Pairing establishes 22 distinct acquisitions on T28QCH, covering 6 January 2025–27 March 2026. ACOLITE dates 15 February and 13 October 2025 lack a same-sensor, same-datatake T28QCH Sen2Cor product.

**Issues and limitations:** Quality filtering varies where ACOLITE flags are missing; temporal coverage varies by pixel. The supplied ACOLITE crop limits geographic inference. There is no independent field reference, quality-mask validation, or atmospheric-correction accuracy estimate.

**Implications and next steps:** Use the tables for descriptive comparison and statistical design. Review coverage and sensor/baseline effects before interpreting temporal patterns. Independent review and PI approval remain pending.

## Pairing and domain

Inventory all 24 ACOLITE date directories, 46 Sen2Cor ZIP products and two loose SAFE products. Pair the sensor, product datatake start, relative orbit and MGRS tile parsed from the ACOLITE source-product metadata and Sen2Cor product XML. Check exact tile sensing times (agreement <0.001 s) and absolute orbit. Do not compare the product datatake start directly with the later ACOLITE tile sensing time. Select only one product per acquisition key, ordered by processing baseline and generation; report all exclusions. No overlap is counted twice. T28QCG products have no corresponding supplied ACOLITE tile and do not extend the comparison domain.

The fixed rectangular comparison grid is the common supplied ACOLITE extent: EPSG:32628; upper-left outer corner (334050, 2209980) m; 3763 columns × 1974 rows; 10 m pixels; bounds E=334050–371680 m, N=2190240–2209980 m. All four requested reflectance bands share this grid on all dates. Sen2Cor 10 m bands use the same CRS and pixel lattice, permitting an exact integer crop. No reflectance interpolation is performed. The Sen2Cor 20 m SCL is transferred to this reference grid by nearest neighbour. This transfer does not create 10 m quality information.

Retain the full supplied crop, including all valid land, intertidal and water pixels. ACOLITE metadata record prior polygon clipping; unavailable pre-crop pixels cannot be recovered. This investigation adds no ecological mask. Geometric common extent is distinguished from finite paired footprint and quality-filtered coverage. All pixel counts refer to equal-area 100 m² grid cells.

## Reflectance and spectral mapping

ΔR = ACOLITE − Sen2Cor, dimensionless surface reflectance. Positive values mean ACOLITE is higher. Select ACOLITE `rhos_*` by the stored sensor-specific `2_name`, `3_name`, `4_name`, and `8_name` metadata, and verify the band variable, wavelength, units, type and scale. B8 is the broad near-infrared band (~833–835 nm in these products), never B8A (~864–866 nm). ACOLITE files are Float32 surface bidirectional reflectance with units 1, scale 1 and offset 0; no division by π is applied. The fact that they are in L2W containers does not change their `rhos` variable identity. Actual effective and Sen2Cor central wavelengths are recorded per sensor/date in `band_mapping.csv`.

Decode each Sen2Cor band's DN as `(DN + BOA_ADD_OFFSET) / BOA_QUANTIFICATION_VALUE`, using that product's XML. The selected products use a −1000 DN offset and quantification 10000. Reject DN=0 and saturated DN=65535 before conversion. Exclude the exact default netCDF Float32 fill sentinel (9.969209968386869 × 10³⁶), found in the supplied TIFF deliveries despite their declared NoData=NaN. Its identity is verified against Unidata documentation and all 88 source band rasters are audited; no arbitrary upper-value clipping is applied. Preserve finite negative reflectance values. Atmospheric methods/configuration and ACOLITE version strings are retained in metadata snapshots, including dark-spectrum fitting and adjacency/glint settings. No original data are reprocessed through an atmospheric correction in this investigation.

## Paired quality masks

For every band/date, require finite ACOLITE values, valid Sen2Cor DN, and the same shared quality mask. Primary SCL classes are 4 (vegetation), 5 (non-vegetated) and 6 (water). Reject SCL 0/1 (no data/defective), 2/3 (dark/topographic shadow and cloud shadow), 7 (unclassified), 8/9 (cloud), 10 (cirrus) and 11 (snow/ice). These are algorithmic quality classes, not independently verified ecological identity.

Where supplied, reject ACOLITE cirrus, out-of-scene and DEM-shadow bits using each file's recorded bit exponents. Flags are computed even when application to L2W products is disabled; disabled masking is not evidence of empty flags. Do not reject the SWIR non-water or negative-reflectance bits. The high-TOA threshold (0.3 in the supplied metadata) can flag legitimate bright terrestrial pixels, so assess its exclusion as a separate sensitivity. No additional morphology or cloud buffer is introduced. Residual thin clouds, adjacency, glint, aerosols, tide, bottom visibility, phenology, viewing geometry and mixed pixels remain potential confounders.

The March 2026 ACOLITE deliveries lack flag rasters. For these dates, use Sen2Cor SCL and finite paired observations, identify the missing independent ACOLITE flags in all summaries, and do not claim equivalent quality information. The exact ACOLITE source-code revision that produced the supplied files is not recoverable from its timestamp-style version string; metadata and current official flag implementation support interpretation but do not establish that code identity.

## Summaries and coverage sensitivity

Write one full-resolution paired ΔR GeoTIFF per date/band. Compute each cell's exact temporal median from n≥1 retained differences and sample SD from n≥2 differences, with denominator n−1. A count raster records n; no-observation cells have count 0 and undefined median/SD. Float output NoData is −9999; count/mask NoData is 255, leaving zero meaningful. Use Float64 calculations and Float32 difference storage/output. Chunk temporal calculations in 64-row blocks using a disk-backed stack on local SSD; no spatial subsampling enters scientific statistics.

Per-date/band primary summaries are the spatial median and sample SD of valid paired differences, with n_valid, finite paired footprint, fixed-grid and within-footprint coverage, negative-value counts and missing-QA indicators. These are spatial distributions, not standard errors; pixels and dates are not assumed independent. Do not use n_valid as an independent statistical sample size.

Sensitivity domains are: include SCL 7; additionally exclude ACOLITE high-TOA flags; a fixed spatial core with all 22 primary dates valid; a fixed core with ≥18/22 primary dates valid; and cells with finite observations in all four bands before QA on every date. The final domain tests changing footprints separately from quality. Empty domains remain explicit. Common-core selection is a conditional sensitivity and can favour consistently clear locations. Domains overlap and must not be pooled as independent observations. Report descriptive differences from primary, without selecting thresholds on favourable results.

## Figure and numerical validation

Arrange B2/B3/B4/B8 in columns, temporal median on the first row and sample SD on the second. Use a zero-centred diverging scale for median and a sequential scale for SD, shared across bands within each row. Limits are the pooled 98th percentile of absolute median or SD values on a deterministic every-fifth-row/every-fifth-column sample. Audit clipping fractions against all full-resolution finite values, separately by band. A regular every-third-cell sample is used only for display. Up to two terminal edge pixels may be omitted in that display sample; all calculations and GeoTIFFs retain them. Neither display clipping nor display sampling changes scientific results. Export 400 dpi PNG and PDF using the guarded figure-output helper.

Direct source-pixel checks independently decode ACOLITE/Sen2Cor values at three dates for all four bands. Temporal checks include available n=0/1/2 strata and distributed valid cells; compare raster count, median and SD with independent calculations and base R. Check every source band and output raster grid, types and NoData; hash all used physical input files and outputs. These computational checks do not substitute for independent scientific review or validate the masks' thematic accuracy.

## Authoritative documentation

- [Copernicus SentiWiki: Sentinel-2 products](https://sentiwiki.copernicus.eu/web/s2-products): Level-2A organization, offsets and units.
- [Copernicus SentiWiki: Sentinel-2 processing](https://sentiwiki.copernicus.eu/web/s2-processing): scene classification and atmospheric processing.
- [ACOLITE official project](https://github.com/acolite/acolite): reflectance definitions and processing.
- [ACOLITE flag implementation](https://github.com/acolite/acolite/blob/main/acolite/acolite/acolite_flags.py) and [L2W implementation](https://github.com/acolite/acolite/blob/main/acolite/acolite/acolite_l2w.py): bit semantics and separation of flag generation from mask application. Consulted 20 October 2026; mutable documentation, not a recovered processing revision.

- [Unidata netCDF fill constants](https://docs.unidata.ucar.edu/netcdf-c/current/netcdf_8h.html): authoritative identity of the encoded default Float32 fill value.
