# Target-point correction extraction: technical handoff

**Take-home message:** The requested layer contains six distinct targets, T1–T6, with both corrections available in every requested band. It is a different point set from the prior station analysis. The new 54 point–band pairs show differences that change with target and band; they do not establish the accuracy or superiority of either correction.

**Meaningful results:** All 108 extracted values are finite. Sen2Cor exceeds ACOLITE in all nine bands at T1, T4 and T6, falls below it in all nine at T2 and T5, and changes sign between B05 and B06 at T3. Nine negative Sen2Cor reflectances remain in the delivery. The largest positive signed difference is 0.08514004116058349 at T1/B08; the most negative is −0.05433157268166542 at T2/B04. These are observed differences in dimensionless reflectance, not errors against a reference.

**Issues and limitations:** T2 is labelled thin cirrus by the operational scene-classification layer throughout both products' stored footprints. Its cloud-probability values are zero, so the two operational indicators disagree. All values remain available with their flags; zero probability does not establish clear conditions. Stored spatial footprints differ for the coarser Sen2Cor bands and the ACOLITE exports. The supplied target classes are labels, not independently verified ecological identities. No independent reflectance accuracy assessment is available.

**Implications and next steps:** Thomas should validate this exact extraction and signed differences before Edward uses the values in either figure scale. Preserve every retained target, all nine bands, the negative values and the T2 caveat. Author QA is complete; scientific approval is not granted. The existing Rachel, Karl and PI gates remain in force.

## Point accounting and identity

The requested `Data/raw/shp/POI_S2C_ACOLITE_targets.shp` resolves on this case-sensitive filesystem to `data/raw/SHP/POI_S2C_ACOLITE_targets.shp`. The `.shp`, `.shx`, `.dbf`, `.prj` and `.cpg` files exist and have full-file SHA-256 records. The geometry is Point in WGS 84 / UTM zone 28N (EPSG:32628), in metres with easting/northing coordinate order. Six SHP records, six SHX entries, six active DBF records and six OGR features agree. The encoding sidecar specifies UTF-8. There are no duplicate names, duplicate coordinates, null/nonfinite points or deleted records. OGR coordinates match the original binary SHP doubles exactly.

Stable identifiers are the original `Name` attribute, T1–T6. `Class` is preserved literally. The zero-based source FID and one-based SHP record are supplementary provenance, not substitute identities.

| ID | Supplied class | Retained | Exact original station match |
|---|---|---|---|
| T1 | Terrestrial soil | yes | none |
| T2 | Water | yes | none |
| T3 | Seagrass | yes | none |
| T4 | Intertidal Sediment | yes | none |
| T5 | Underwater Vegetation | yes | none |
| T6 | Underwater Sand | yes | none |

All 15 original station coordinates and literal labels were rechecked against the raw GPS workbook and cover-label file, then transformed to EPSG:32628. The complete 6 × 15 correspondence table retains separation distances. Coordinate equivalence uses only a 1e−8 m numerical transformation tolerance, never a habitat or proximity matching radius. The nearest original station is at least 1296.58 m from any requested point. No station values or station cloud flags were reused.

The original AC03 `mbp_mud` and AC04 `mpb_mud` exclusions remain preserved by source identity. Neither maps to a requested target. Their nearest requested target is T5, respectively 5636.56 m and 5578.02 m away. T4 is not assigned AC03's identity merely because its supplied class is Intertidal Sediment. The exclusion mapping and every distance are supplied explicitly; all six requested targets are retained.

## Acquisition, quantities and extraction

The paired acquisition remains Sentinel-2B, 7 March 2026, tile T28QCH, orbit 80/A047010. The exact tile sensing time is `2026-03-07T11:45:54.425534Z`. The Sen2Cor Level-2A product has processing baseline 05.12. Its L1C tile identity and ACOLITE's recorded input L1C name, granule and time agree with the existing CTR42 pair evidence. Original upstream L1C bytes are unavailable, so byte-identical ancestry is not claimed. Product/tile metadata and all rasters used were hashed again and match their CTR42 full-file identities.

Band order is B01, B02, B03, B04, B05, B06, B07, B08, B8A. The unchanged `ctr42_band_contract.csv` provides exact band paths and wavelengths. The ACOLITE band wavelengths are approximately 442.23, 492.13, 558.95, 664.94, 703.83, 739.13, 779.72, 832.95 and 863.98 nm. These are discrete sensor bands; they are not an independently measured continuous spectrum.

Sen2Cor BOA reflectance is decoded from UInt16 DN as `(DN − 1000)/10000`, using the product's offset and quantification metadata. DN 0 and 65535 are declared NoData and saturation in the SAFE XML, even though the JP2 band headers do not declare NoData. They are excluded from numerical availability before scaling. ACOLITE's Float32 `rhos_*` exports declare dimensionless surface bidirectional reflectance with scale 1, offset 0 and NaN NoData. No division by π or further radiometric conversion was applied. The two products are compared as their delivered reflectance quantities, with no assertion of identical correction assumptions or independent physical accuracy.

For every target, each source's containing stored cell was sampled read-only. No interpolation, spatial average, scene mosaic, new correction, ASD integration or full-scene array was produced. Sen2Cor stored/native resolution is 60 m for B01, 10 m for B02/B03/B04/B08 and 20 m for B05/B06/B07/B8A. ACOLITE exports use 10 m cells for every band. Their metadata record bilinear output/warp settings; exact upstream band-specific weights and effective optical footprints are unverified. Source CRS and axis-aligned grid geometry were checked by the reused GDAL reader. Exact affine transforms, extents, dimensions and band metadata are saved in the header record. The earlier source contract documents the nominally nested grids. These are paired target-point samples with unequal spatial support in the coarse bands, not pixelwise image subtraction.

## Numerical observations for validation

All nine requested bands are available for all six targets and both corrections: 108/108 finite values, 54/54 finite pairs, zero missing or saturated samples, and zero sampled points outside either raster extent. Nine negative values are retained: T2 Sen2Cor B04–B8A (six), T3 Sen2Cor B01–B02 (two), and T5 Sen2Cor B8A (one). ACOLITE has no negative values at these samples. Availability does not imply scientific accuracy.

| Target | Minimum signed difference | Maximum signed difference | Direction across nine bands |
|---|---:|---:|---|
| T1 | 0.042381 | 0.085140 | Sen2Cor higher in 9 |
| T2 | −0.054332 | −0.026372 | Sen2Cor lower in 9 |
| T3 | −0.046423 | 0.017395 | lower B01–B05; higher B06–B8A |
| T4 | 0.022808 | 0.048643 | Sen2Cor higher in 9 |
| T5 | −0.024315 | −0.005627 | Sen2Cor lower in 9 |
| T6 | 0.012922 | 0.047605 | Sen2Cor higher in 9 |

Differences are Sen2Cor minus ACOLITE in dimensionless reflectance. The displayed rounding is for reading; the CSV retains full floating-point precision. No p-values, confidence intervals, causal mechanisms, ecological identifications or accuracy rankings are inferred. No requested targets share the same stored cell within a band/correction, but this does not establish ecological independence, and correlated bands are not independent replicates.

## Operational QA

SCL, cloud probability and snow probability were read over every stored radiometric footprint, using Sen2Cor's operational layers as shared scene evidence for both corrections. For Sen2Cor, all layers of the native QUALIT and DETFOO masks were also read. QA windows cover at most nine stored cells. Layer-specific raw counts, source identities, indices, values and decoded-window hashes are retained. QUALIT codes are all zero in the sampled windows; DETFOO codes are 4 or 5. Raw code availability is not an independent cloud or detector accuracy assessment.

T2's SCL code is 10 (thin cirrus), for all nine bands and both corrections: 18 flagged reflectance rows. Its cloud and snow probability codes are zero. T3's fine footprints have SCL 4; its B01 Sen2Cor footprint includes three SCL-4 and six SCL-5 cells. Its cloud probability codes are 0 or 1. T1 is SCL 5; T4, T5 and T6 are SCL 6. Supplied habitat labels are not relabelled using these scene classes.

All requested Sen2Cor QA files exist and cover the sampled footprints. An ACOLITE-specific quality-mask file is not supplied in the paired export directory; exported reflectance metadata say `l2w_mask=False`. Therefore no ACOLITE-specific mask clearance is asserted. Operational QA does not establish cloud-free full optical support. The prior physical-validation holds are unchanged. ASD coverage and a field/satellite date difference are not limitations of this satellite-only comparison; no field validation is attempted here.

## Successor inputs and reproduction

All new files are in the original `analysis/CTR-27_sen2cor-acolite-asd/` investigation. No report or figure is changed by this handoff.

| File | Use |
|---|---|
| `tables/ctr47_targets.csv` | Six exact coordinates, stable IDs, literal classes, source records and retention decisions |
| `tables/ctr47_satellite.csv` | 108 unique target/band/correction rows; raw and decoded values, source SHA-256, cell bounds and SCL flags |
| `tables/ctr47_pairs.csv` | 54 unique target/band rows; identical finite mask, both reflectances and signed difference |
| `tables/ctr47_station_correspondence.csv` | All 90 target/original-station distances; no inferred identity |
| `tables/ctr47_exclusion_mapping.csv` | Original AC03/AC04 source exclusions and explicit absence of a target mapping |
| `tables/ctr47_qa.csv`, `ctr47_windows.csv` | All footprint QA counts and bounded decoded source windows with hashes |
| `tables/ctr47_cell_sharing.csv` | Stored-cell membership, including explicit absence of sharing |
| `tables/ctr47_sources.csv` | Every input used: full-file hashes, sizes, times and equivalence to CTR42 sources |
| `outputs/ctr47_raster_headers.json` | Actual source grid, quantity and mask metadata |
| `provenance/ctr47_geometry.json`, `ctr47_scene_pair.json` | Geometry/identity checks and paired acquisition evidence |
| `provenance/ctr47_extraction.json`, `ctr47_validation.json` | Run environment, counts, limitations and author QA |
| `provenance/ctr47_preflight.json` | Baseline and unrelated-file preservation hashes, path readiness and guard finding |

From the authorized project root, using the unchanged locked environment and read-only original inputs:

```bash
./scripts/check-env.sh
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr47_extract.py
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr47_validate.py
```

The extraction imports only CTR42 utilities; its `main()` is not executed. The source package contains the reused reader, metadata contracts and lineage files required by this extraction, together with the new scripts, numerical tables and technical QA. Original raster products, GPS workbook and target sidecars remain at their recorded read-only source locations; they are not redistributed in the package. Raw-file hashes allow their exact identities to be checked.

The author validation passed, including separate GDAL CLI reads for all 108 radiometric values, separate SCL reads for 12 unique footprints, full source hashes, coordinates, decode, negative values, all pair differences, window counts/hashes and preservation of every prior tracked file plus unrelated CTR39 files. The project environment check passed without dependency changes. This is author QA, not independent scientific review.

## Revision and preservation

This work extends baseline `3a2bf1b19e7f9f80b6830b8b0f056bbe6add2844` on local branch `ctr-47-target-spectra`, in the original checkout. The exact committed revision and downloadable package hash are saved in the CTR47 task document outside this file, avoiding a self-referential commit claim.

The path-specific synchronization check permits these analysis-only paths. The clean-workspace preflight refuses the pre-existing unrelated untracked CTR39 files. They were neither deleted, stashed nor staged; no guard was bypassed, no new worktree was created, and no PR was proposed. The baseline reports, Figure 1 and all other figures, numerical history, CTR24 dictionary, manuscript, raw files and lockfiles are preserved. No scientific, manuscript-integration, merge or publication approval is claimed.
