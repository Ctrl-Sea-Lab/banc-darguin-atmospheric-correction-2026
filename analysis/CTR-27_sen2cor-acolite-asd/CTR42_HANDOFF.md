**Take-home message:** The live data establish a same-acquisition Sentinel-2B pair for 7 March 2026, and all requested station-band satellite values are available. These are exploratory contextual spectra: the ASD measurements are from 27 March, 20 days later, several locations have operational cloud/shadow flags, and B08 lacks adequate ASD response coverage. This handoff supports the requested spectral presentation, without establishing correction superiority or validation accuracy.

**Meaningful results:** The 13 retained stations each have nine containing-cell values from each correction: 234 finite satellite rows. Both supplied-v4 primary and saved-v5 sensitivity response functions support eight ASD bands per station, giving 104 finite station-band references per version (208 combined). All 26 B08 reference rows remain `NA`; both satellite B08 values remain visible. There are 117 availability rows, 18 band/version coverage rows, 1,287 raw QA records and 1,521 hashed bounded windows (maximum nine cells; every radiometric read is one cell). The author QA passed 2,941 checks, including 234 independent-interface point reads and 208 separately summed reference integrals. This is technical consistency evidence, not independent scientific review.

**Issues and limitations:** No row is declared validation eligible. Field dates are 20 days after acquisition, field clock/timezone are unknown, effective optical footprints and registration accuracy remain unverified, and the existing physical/support holds are retained. Operational Sen2Cor SCL flags affect 109 of the 234 satellite rows. These flags are transferred geometrically to the ACOLITE stored-cell footprint as same-acquisition contextual QA, not as an independently generated ACOLITE mask. ACOLITE metadata state `l2w_mask=False`. Stored numeric availability must not be reported as clear-sky usability. The original `AC03 mbp_mud` and `AC04 mpb_mud` exclusions remain literal, with no radiometric reads or new integrations. Raw labels remain unchanged; `zn` is not expanded into an ecological identity.

**Implications and next steps:** Thomas can check this exact handoff on CTR43, then Edward can update the existing report. Plot all nine satellite bands with the QA limitations visible; keep B08 ASD missing and avoid bridging it as measured support. The full ASD curve in the preserved `tables/ctr34_current_spectra.csv` is contextual **27 March** field reflectance. It must not be relabelled as a 7 March field observation. Any shared descriptive metric must use identical finite station-band rows for both corrections, disclose its band composition and QA context, and remain exploratory. The main supplied Figure 1 retains its original provenance/date. Rachel and Karl review the final presentation revision through CTR38; PI scientific approval is still required. This task does not edit report presentation, remove Figure 2, approve results, or integrate the manuscript.

**Verified acquisition identity**

- Sen2Cor operational L2A: `S2B_MSIL2A_20260307T113319_N0512_R080_T28QCH_20260307T154921.SAFE`, processing baseline 05.12; granule `L2A_T28QCH_A047010_20260307T114112`.
- Sen2Cor tile sensing time: `2026-03-07T11:45:54.425534Z`. Product datatake start is separately `2026-03-07T11:33:19.024Z`; these are different metadata concepts, not alternative acquisitions.
- ACOLITE: `data/raw/S2/ACOLITE/20260307/S2B_MSI_2026_03_07_11_45_54_T28QCH_L2W_rhos_*.tif`, nine requested bands extracted. Its ISO time is exactly the same tile sensing time, its granule is `L1C_T28QCH_A047010_20260307T114112`, and its declared input is `S2B_MSIL1C_20260307T113319_N0512_R080_T28QCH_20260307T153536.SAFE`.
- Sen2Cor's `L1C_TILE_ID` names the same processing time `20260307T153536`, absolute orbit `A047010`, tile and baseline. Metadata establish the same acquisition. Byte-identical upstream L1C ancestry is **not** verified: the referenced original upstream bytes are unavailable here.
- ACOLITE metadata: dark-spectrum correction, model `ACOLITE-LUT-202110-MOD2`, version string `Generic GitHub Clone c2026-04-07T11:45:24`; an exact processor source commit is not established. Sen2Cor is the supplied operational L2A product, not a new controlled rerun.
- The current roots contain one matching 7 March 2026 pair. The March 2025 inventory and 27 March 2026 products were not substituted. Exact metadata evidence is saved in `provenance/ctr42_scene_pair.json`, full headers in `outputs/ctr42_raster_headers.json`, and full-file source SHA-256 values in `tables/ctr42_sources.csv` (57 source records).

**Spatial, radiometric and reference methods**

The explicit saved station crosswalk was rechecked against the raw GPS workbook, raw cover labels and field-day log. The retained stations are AC01, AC02, AC05–AC08 and D06_A–D06_G. GPS longitude/latitude are EPSG:4326 and were transformed in longitude–latitude order to EPSG:32628; the round trip passed within 1e-9 degrees. The prior authenticated Iwik location correction for AC01/02 remains documented, without editing raw Arel labels. D06 stations retain supplementary status and their support limitations.

No raster resampling was performed here. Each correction uses the cell containing the verified coordinate on its own stored grid. Sen2Cor uses B01 at native 60 m; B02/B03/B04/B08 at 10 m; B05/B06/B07/B8A at 20 m. ACOLITE exports all requested bands at 10 m, with the sensor's coarser native resolutions recorded separately. Its metadata contain bilinear warp/output settings, but the exact bandwise upstream interpolation kernel and weights are unverified. The grids are nominally nested in EPSG:32628; their unequal stored footprints are not treated as equivalent optical support. Cell bounds and shared-cell membership are explicit. The 234 satellite rows occupy 208 distinct source cells, including 25 groups shared by multiple stations; spectral bands and nearby stations are not asserted independent.

Sen2Cor metadata supply BOA quantification 10000 and per-band add offset -1000. DN 0 and 65535 are checked before `(DN - 1000)/10000`. ACOLITE `rhos_*` variables are Float32 surface bidirectional reflectance, unit `1`, with NaN NoData and no extra scale/offset. Negative finite values would be retained; none occurred in the present reads. No `Rrs`/water-leaving conversion was applied. Surface quantity names do not establish equal target optical paths or reference representativeness.

Raw QUALIT and DETFOO layers were read over the Sen2Cor stored footprint. The sampled QUALIT codes are all zero and DETFOO codes are 4 or 5. SCL was read over each correction's stored footprint. SCL labels come directly from this product's XML. These are bounded stored-footprint checks, not full effective-footprint clearance or independent ecological classification.

| Stations | Operational cloud/shadow finding |
|---|---|
| AC05, AC08 | Thin cirrus; B01 stored footprint also intersects medium-probability cloud |
| AC06 | Medium-probability cloud |
| D06_A, D06_B, D06_C | Cloud shadow; D06_C coarser cells also include non-vegetated class |
| D06_D | Sen2Cor B01 footprint intersects cloud shadow; other requested stored cells have no cloud/shadow flag |
| AC01, AC02, AC07, D06_E, D06_F, D06_G | No cloud/shadow/invalid SCL code in sampled stored footprints; scientific holds still apply |

ASD uses the original dimensionless 400–900 nm station-average spectra at 1 nm spacing. The supplied S2B SRF v4 is primary; the existing official-v5 workbook is a separately named sensitivity reference. The saved CTR34 union-knot trapezoid method is reused: response-weighted numerator divided by the complete response denominator, at least 0.999 response coverage, no positive-response extrapolation and no missing interval within positive response. All 36 existing B02/B03/B04 references reproduce within 1e-14. B08 coverage is 0.9948579691930339 (v4) and 0.9950095750145522 (v5), below threshold; its positive responses extend to 907 and 906 nm. No truncated or extrapolated B08 substitute was computed. Small coverage deviations around 1 in other rows are floating-point summation effects.

**Reproduction and file contract**

Run from the existing project root with the approved project environment:

```bash
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr42_extract.py
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr42_validate.py
```

The scripts write only `ctr42_*` files within CTR27. They use the existing locked NumPy environment and installed GDAL CLI/C API. No dependency was installed or changed; the project environment check passed. Full source SHA-256 values were streamed without decoding full scenes. Raster calculations read bounded windows only. GDAL auxiliary writes and network projection downloads were disabled. Original tracked CTR27 files, raw source hashes, lockfiles and unrelated CTR39 files passed preservation checks. The saved validation receipt distinguishes author QA from independent scientific review.

| File | Purpose and keys |
|---|---|
| `tables/ctr42_satellite.csv` | 234 rows; unique station/band/correction; raw and decoded values, source hash, coordinate cell, SCL flags, physical holds |
| `tables/ctr42_references.csv` | 234 rows; unique station/band/SRF role; 208 finite values and 26 B08 NA values; numerator, denominator, source identities |
| `tables/ctr42_srf_coverage.csv` | 18 band/version coverage audits, full positive-response limits and reason codes |
| `tables/ctr42_availability.csv` | 117 station/band rows; both corrections and references, common finite indicators, QA and eligibility reasons |
| `tables/ctr42_stations.csv`, `ctr42_exclusions.csv` | All 15 input identities accounted for: 13 retained, two literal mud exclusions |
| `tables/ctr42_band_contract.csv` | Exact paths, quantities, wavelengths, scaling, resolutions and resampling limitations |
| `tables/ctr42_qa.csv`, `ctr42_windows.csv` | Raw QA counts and hashed stored-cell windows, including raw values and geometry indices |
| `tables/ctr42_cell_sharing.csv` | Source-cell membership and dependence caution |
| `tables/ctr42_sources.csv` | Full-file SHA-256, size and modification time for every scientific/method/environment input used |
| `provenance/ctr42_scene_pair.json`, `ctr42_extraction.json`, `ctr42_validation.json` | Scene identity, run environment/counts and author QA evidence |
| `provenance/ctr42_preflight.json` | Recoverable baseline and preserved original-file hashes; workspace guard finding |

CSV missing numeric fields are the literal `NA`, never zero. `common_finite_triple_*` is a numerical availability indicator, not an eligibility flag; `validation_eligible` is false throughout. No comparative performance metrics, confidence intervals, hypothesis tests, rankings or accuracy claims were generated.

**Workspace and review status**

Work extends baseline `51805d91ffdef5cafa81c11fd91a74163eec4d83` on the dedicated branch `ctr-42-march-spectra` in the original checkout. All new files are confined to the existing CTR27 directory. The existing report/QMD/HTML, figures, portable presentation packages, original input evidence, CTR24 dictionary and manuscript are preserved. The path-specific synchronization guard returned `ready` for these analysis-only paths. The clean-workspace preflight refused the pre-existing untracked CTR39 files; none were removed, stashed or bypassed. This is a local committed numerical handoff, not a new PR or a change to draft PR9. Subsequent owners must preserve the same files and coordinate the workspace guard before a PR.

The exact delivery commit and attachment checksum are recorded in the saved CTR42 technical-delivery task document and artifact receipt, outside this file to avoid a self-referential commit hash. Completing CTR42 means the extraction handoff is complete, not that the scientific findings have been approved.
