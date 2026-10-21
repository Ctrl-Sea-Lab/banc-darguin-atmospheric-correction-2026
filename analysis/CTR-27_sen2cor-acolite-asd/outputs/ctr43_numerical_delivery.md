**Take-home message:** The 7 March 2026 Sen2Cor and ACOLITE station spectra are numerically ready for the requested nine-band presentation. All 234 satellite values are available. ASD supports eight of the nine bands at each of 13 retained stations; B08 remains missing. These are cross-date exploratory comparisons, with zero validation-eligible pairs.

**Meaningful results:** Both corrections use exactly the same 104 station–band rows per SRF version for descriptive differences: B01, B02, B03, B04, B05, B06, B07 and B8A at each station. Satellite B08 remains available as spectral context. Independent arithmetic confirms the exported values and summaries. Supplied SRF v4 is primary; saved official v5 is sensitivity only. The largest absolute change between supported v4/v5 ASD references is 0.00007710803728627758 dimensionless reflectance. This small numerical sensitivity does not establish reference representativeness or correction accuracy.

**Issues and limitations:** The field spectra were measured on 27 March, 20 days after the satellite acquisition. Operational Sen2Cor SCL cloud/shadow flags affect 109 of 234 satellite rows (55 Sen2Cor and 54 ACOLITE stored-footprint contexts). Stored finite values are retained with their flags. ACOLITE flags are transferred from the same-acquisition Sen2Cor SCL geometrically, not independent ACOLITE quality classifications; the supplied ACOLITE product declares masking disabled. Unflagged stored cells are not evidence of full optical-footprint clearance. Exposure, target representativeness, effective footprint, registration and supplementary-station support remain unresolved. Repeated bands and shared cells are not independent replicates. No model, confidence interval, hypothesis test or superiority ranking is justified by this handoff.

**Implications and next steps:** Edward can use the new tables to replace the station spectra, preserving Figure 1's supplied-table values and actual provenance/date and removing the old three-band scatter and its dedicated presentation. The optional new eight-band summaries should be labelled cross-date descriptive discrepancies, with count, band set and QA context; they are not validation errors. The final report revision still requires Rachel's presentation review, Karl's independent scientific review and PI approval through the existing parent task. Completion of this numerical handoff is not scientific approval.

## Scope and acquisition verification

This work is confined to the existing `analysis/CTR-27_sen2cor-acolite-asd/` in the original Linux Mint project checkout. It extends Roger's exact handoff commit `51eeaf86353e895d18ee8f0747642d45d612909e`, whose parent delivery baseline is `51805d91ffdef5cafa81c11fd91a74163eec4d83`. Nineteen `ctr42_*` evidence files were checked byte-for-byte against that commit. All 57 listed source files were rehashed, including imagery, metadata, field inputs, response functions, methods and environment locks. Numerical verification reused Roger's exact hashed evidence of 234 GDAL point rereads; it independently checked window values/hashes, decoding, cell indices and source identity without re-extracting imagery.

The same-acquisition identity is Sentinel-2B, tile T28QCH, orbit A047010/R080, tile sensing time `2026-03-07T11:45:54.425534Z`. The L2A product is `S2B_MSIL2A_20260307T113319_N0512_R080_T28QCH_20260307T154921.SAFE`. ACOLITE identifies the corresponding L1C input `S2B_MSIL1C_20260307T113319_N0512_R080_T28QCH_20260307T153536.SAFE`, matching the L2A L1C tile metadata. Live product XML and hashed ACOLITE headers agree. Identical upstream L1C bytes remain unverified; processor equality is not asserted. No 2025 or 27 March satellite scene was substituted.

Sen2Cor reflectance is `(DN - 1000)/10000`, with DN 0 and 65535 excluded before scaling. ACOLITE `rhos` Float32 values are dimensionless surface bidirectional reflectance without another scale or offset. No water-leaving or Rrs conversion is used. Negative finite reflectance is accepted by the method and plotting masks; none occurred in these extracted values. Unequal stored-cell support is retained: Sen2Cor B01 is 60 m, B02/B03/B04/B08 10 m and B05/B06/B07/B8A 20 m; ACOLITE exports every band at 10 m. These do not establish equivalent effective optical support.

## Reference coverage and accounting

The original measured ASD grid is 400–900 nm at 1 nm spacing. All 208 supported station/band/version integrals were independently recomputed by summing the original SRF knots with `math.fsum`, separately from Roger's union-knot convolution. Complete-response denominators are retained. Coverage must be at least 0.999, with no positive-response extrapolation or missing positive-response intervals.

B08 coverage is 0.9948579691930339 for v4 and 0.9950095750145522 for v5; positive response extends to 907 and 906 nm respectively. All 26 B08 ASD references remain literal `NA`; the two satellite series retain their B08 values. Resolving this requires measured spectral support beyond the current range, rather than a relaxed threshold, truncated denominator or extrapolation. No essential input for the eight supported bands is missing.

The 13 retained identities are AC01, AC02, AC05, AC06, AC07, AC08 and D06_A–D06_G. The seven D06 stations retain supplementary status, even though new numerical extraction is now available. The exclusions are exactly `AC03 mbp_mud` and `AC04 mpb_mud`; no new values were computed for them. The full 15-station accounting is explicit. Original labels and the prior authenticated Iwik location correction remain as supplied; no new ecological interpretation of `zn` is introduced.

There are 55 supported station–band rows per SRF version with neither correction's stored footprint operationally flagged, but **none becomes validation eligible**. B01 contributes 6 of these, and each other supported band contributes 7. The all-finite descriptive summaries retain flagged rows and disclose their counts; they do not silently select a different set for each correction. Six stations have all eight metric bands flagged for both corrections (AC05, AC06, AC08, D06_A, D06_B, D06_C); D06_D has an additional Sen2Cor B01 flag. This distinction must remain visible if metrics are displayed.

## Numerical and plotting contract

| File in `tables/` | Contents and key |
|---|---|
| `ctr43_spectral_long.csv` | 702 rows: station/band/SRF_role/series; select `v4_primary` for 351 primary rows, with 338 finite reflectances. Both satellite series have nine bands; ASD has eight. |
| `ctr43_pair_masks.csv` | 234 rows: station/band/SRF_role, complete numeric values, shared finite mask, individual and joint SCL flags, coverage, dates and hold reasons. |
| `ctr43_comparison_long.csv` | 468 rows: station/band/SRF_role/correction; 416 finite signed differences and 52 NA B08 differences. This is numerical evidence, not an instruction to recreate the deleted scatter. |
| `ctr43_station_metrics.csv` | 52 rows: station/SRF_role/correction; 8 paired bands each, exact band list and shared-row hash, bias/MAE/RMSE and operational flag counts. |
| `ctr43_band_availability.csv` | 18 rows: band/SRF_role, both satellite availability counts, ASD support, shared masks, QA and zero eligible counts. |
| `ctr43_station_accounting.csv` | All 15 identities, including both original exclusions and supplementary status. |
| `ctr43_srf_sensitivity.csv` | 117 station/band rows; v4/v5 differences for supported references, B08 NA. |

Bias is the mean of satellite minus ASD reflectance; MAE is the mean absolute difference; RMSE is the square root of mean squared difference. Each station's eight supported bands receive equal weight 1/8. These summaries describe discrepancies between different dates and spatial supports. Bands do not become replication units, and the sums are not integrated spectral distance measures. No pooled accuracy or uncertainty estimate is produced.

For plotting, filter one SRF role explicitly; satellite rows repeat across the two reference-role views and must not be counted twice. Use the three `series` values `ASD`, `Sen2Cor`, `ACOLITE`. Use `band_order` and the supplied common display wavelength positions, which follow the ACOLITE metadata S2B band wavelengths; these positions do not interpolate data. Retain all nine rows, including NA. If connecting band points, group by station, series, SRF role **and `segment_id`**. ASD B01–B07 have segment 1; B08 has NA value/segment; B8A has segment 2. Thus filtering finite values cannot create a measured-looking bridge over B08. Points should remain visible for isolated segments.

ASD `observation_date` is 27 March; satellite `observation_date` is 7 March. The preserved `ctr34_current_spectra.csv` may be used only as a contextual full field curve from 27 March, not as coincident March7 observations or evidence of B08 support. `common_finite_triple` is a numerical mask. `common_finite_without_operational_SCL_flag` is an optional inspection mask, not scientific eligibility. `validation_eligible` is false throughout. Numeric NA fields are the literal `NA`, never zero. Presentation should preserve readable flag and missingness explanations, original display mapping and source provenance.

## Reproduction and checks

From the original project root, with its already approved environments:

```bash
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr43_prepare.py
./scripts/project-env.sh Rscript analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr43_verify.R
```

The preparer reads the frozen CTR42 handoff and writes only `ctr43_*` tables and provenance. It requires the existing project sources and Git input commit; the downloadable archive is an inspectable evidence package, not a substitute for the raw-data project. Python uses the locked environment and saved workbook parser; R uses base R 4.3.3. Environment checks passed without installations or lockfile edits. There is no stochastic calculation and no seed-dependent output.

The input audit passed 1,954 checks, including 57 full source hashes, 208 separate supported quadratures and preservation of all previously tracked CTR27 files and recorded unrelated CTR39 files. The separate base-R verifier passed 212 checks of exact input/output joins, masks, source values, metric arithmetic and bounds, denominators, missingness, line segments, dates and station accounting. A development-only R parse error was corrected before any R verification result was produced; the final verifier completed successfully. Python checks also cover negative-value retention, missing common inputs and empty summaries. All generated values have been checked; these numerical checks do not replace independent scientific review.

Detailed evidence: `provenance/ctr43_input_audit.json`, `ctr43_computation.json`, `ctr43_R_verification.txt`, and `ctr43_preservation.json`. Code and table hashes are recorded; the exact final commit and archive checksum are recorded in the saved numerical-delivery task document and archive manifest to avoid self-referential hashes.

## Preservation and downstream ownership

No existing figures, QMD, HTML, source values, raw data, CTR24 dictionary, final manuscript, lockfiles or unrelated CTR39 files were edited. Existing March27 historical metrics remain in the historical source files for Edward's scoped removal from active presentation; none was copied into the new March7 table set. Figure 1 is unchanged. No report render was attempted because the final presentation is explicitly owned by Edward.

The branch `ctr-43-march-numerics` extends the exact extraction handoff in the original checkout. The analysis-path synchronization gate returned ready. The clean-workspace preflight still refuses the pre-existing untracked CTR39 files, as it did for Roger. Those files were neither deleted nor stashed, and no guard was bypassed. This delivery is a local committed handoff; no push, PR update, merge, manuscript integration or public publication occurred. Edward/Charles must coordinate the existing workspace guard before proposing the final PR revision.
