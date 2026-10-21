# Verified target-point comparison: numerical and scientific handoff

**Take-home message:** The six requested targets have complete paired reflectance in all nine bands. The difference between corrections depends on target and band, and cannot be described by a single common offset. These observations describe the delivered products; they do not establish which correction is more accurate.

**Meaningful results:** Sen2Cor is higher in every band at T1, T4 and T6, lower in every band at T2 and T5, and lower through B05 but higher from B06 onward at T3. The largest positive difference is 0.085140 at T1/B08; the most negative is −0.054332 at T2/B04. Nine negative Sen2Cor values are retained. There are no missing target–band pairs.

**Issues and limitations:** T2 is labelled thin cirrus by scene classification despite zero cloud probability. This discrepancy prevents treating zero probability as proof of clear conditions. The coarser bands represent different stored areas in the two products, and effective optical support is unverified. Supplied target classes are not independently verified habitat identities. No independent accuracy reference or sampling design supports a correction ranking, population inference or confidence interval.

**Implications and next steps:** The values are ready for Edward's two spectral-scale versions. Preserve the flagged target and negative values. The unchanged first figure has its own evidence and must not be attributed to these targets or this acquisition. Rachel's presentation stage, Karl's independent scientific review and Charles's exact-revision submission to the PI remain required. This specialist validation is not scientific approval.

## Scientific text available for the report

Across six targets and nine bands, all 54 paired comparisons were available. Sen2Cor exceeded ACOLITE throughout the spectrum at T1, T4 and T6, and was lower throughout at T2 and T5. At T3, the ordering reversed between B05 and B06. Signed differences, defined as Sen2Cor minus ACOLITE, ranged from −0.054332 to 0.085140 in dimensionless reflectance. Thus, the corrections differ in both reflectance magnitude and their relationship across bands; a single offset would not represent all targets.

Some broad spectral features were shared. Both products increased from B01 through B08 at T1 and then declined at B8A. At T3, both rose from B04 through B8A, despite the reversal in their relative ordering. Both had their highest sampled reflectance at B05 for T5 and T6. Other features differed: the highest sampled reflectance at T2 occurred at B02 for Sen2Cor and B03 for ACOLITE, while at T4 it occurred at B08 and B8A, respectively. These are features of the sampled bands; no continuous-spectrum maximum or ecological mechanism is inferred.

Negative reflectance occurred in nine Sen2Cor samples: six bands at T2, two at T3 and one at T5. These values are retained as delivered. T2 also had a thin-cirrus scene-classification flag despite zero cloud probability; the disagreement between indicators limits interpretation of this target. The products represent different stored areas for the coarser bands, so their differences cannot be attributed solely to atmospheric correction. Differences do not establish accuracy or superiority. Correlated bands are not independent replicates, and the selected targets do not support class-wide conclusions. Separate panel scales reveal within-target shape but visually magnify smaller absolute differences; the common-scale figure is needed for direct comparisons of magnitude among targets.

## Descriptive numerical results

Each row below summarises the same nine finite paired bands at one target. Values are rounded to six decimal places for reading. Signed difference is Sen2Cor minus ACOLITE; mean absolute difference measures discrepancy between products, not error against truth. Means weight the nine requested bands equally, not by spectral width. Minimum and maximum are observed extrema, not uncertainty bounds.

| Target | Supplied class | Mean signed difference | Mean absolute difference | Minimum | Maximum |
|---|---|---:|---:|---:|---:|
| T1 | Terrestrial soil | 0.067266 | 0.067266 | 0.042381 | 0.085140 |
| T2 | Water | −0.042896 | 0.042896 | −0.054332 | −0.026372 |
| T3 | Seagrass | −0.016096 | 0.024724 | −0.046423 | 0.017395 |
| T4 | Intertidal Sediment | 0.037992 | 0.037992 | 0.022808 | 0.048643 |
| T5 | Underwater Vegetation | −0.015158 | 0.015158 | −0.024315 | −0.005627 |
| T6 | Underwater Sand | 0.028302 | 0.028302 | 0.012922 | 0.047605 |

The full tables also contain band-specific summaries across the same six targets and all 48 adjacent-band steps. Thirty-one signed differences are positive and 23 negative. The pooled mean signed difference is 0.009901673148462065, whereas the mean absolute difference is 0.03605631059524086. Opposite signs cancel in the pooled mean, so it should not replace the target-specific findings. These are fixed-set descriptive summaries; there are no p-values, confidence/credible intervals, fitted models, stochastic sampling or accuracy rankings. Numerical precision does not quantify scientific uncertainty.

## Exact input, identity and units

Validated predecessor: local commit `82ca0df0b699e51135afc680b23eda9def5bbfe2` (Roger's completed CTR47 handoff), extending baseline `3a2bf1b19e7f9f80b6830b8b0f056bbe6add2844`. Its 54-pair CSV SHA-256 is `d1a49dc0f6da1049614bc45f33a0e289feb65c86bd0835fca869721f9f327a8f`. The final CTR48 revision is recorded in the task delivery document and package manifest, outside this self-referential source file.

Independent binary SHP/DBF parsing recovered six original Name/Class records and exact coordinate doubles. All coordinates are unique Points in EPSG:32628. All 90 supplied target/station distances were recalculated. No target maps to an old station; the smallest separation is 1296.575570130791 m. Original AC03 `mbp_mud` and AC04 `mpb_mud` exclusions remain preserved by source identity and map to none of these targets. No habitat-name substitution or inherited station cloud flag was used; all six targets are retained.

Band order is B01, B02, B03, B04, B05, B06, B07, B08, B8A. Wavelengths come from the existing ACOLITE sensor-band contract and are used identically for both curves. Pairing is by original target ID and band, not row position. Sen2Cor uses `(DN − 1000)/10000`, confirmed against original product XML; DN 0 and 65535 are special values, not reflectance. None occurs in the sampled rows. ACOLITE's Float32 rhos exports are surface bidirectional reflectance in unit 1, scale 1, offset 0, with NaN NoData; no π conversion is applied. These are delivered reflectance quantities, without proof of identical retrieval assumptions or physical accuracy.

The raw Sen2Cor tile metadata and recorded ACOLITE headers agree on Sentinel-2B, tile T28QCH and sensing time 7 March 2026 at 11:45:54.425534 UTC. Original upstream L1C bytes remain unavailable; byte-identical ancestry is not claimed. Sen2Cor stored cells are 60 m for B01, 10 m for B02/B03/B04/B08 and 20 m for B05/B06/B07/B8A; ACOLITE exports are 10 m for every band. All containing cells and bounds were recomputed from stored affine transforms. No requested targets share the same stored source cell within a correction/band; this does not prove ecological independence.

## Independent validation and limitations of the audit

The independent Python implementation imports no extraction code. It passed 4,443 assertions covering exact predecessor bytes, source identities, raw target geometry and attributes, station correspondence/exclusions, raw metadata decode, every saved radiometric/QA window hash, cell indexing and bounds, all 108 decoded values, all 54 paired differences, and prior-file preservation. Its source integrity checks re-read small sidecars/XML and verify every source's recorded size/time. The full raster hashes and separate GDAL CLI samples from Roger's completed author QA are reused; this task did not rehash all rasters or rerun extraction. That distinction is explicit in the validation record.

A separate base-R implementation joins Roger's long table independently, recomputes all differences, target/band summaries and 48 adjacent-band steps, and compares them with the successor tables. Its largest numerical discrepancy is 6.94 × 10⁻¹⁸, below the absolute check tolerance of 10⁻¹⁴. This tolerance concerns floating-point arithmetic, not measurement uncertainty. The first R check stopped because CSV values `True`/`False` were strings rather than R logical values; explicit boolean parsing fixed the checker. No source values changed, and the complete check then passed. The project environment check passed without installation or dependency changes; its pre-existing temporary-home normalization warning is recorded.

Operational SCL flags were recomputed from saved footprint counts. All 18 T2 correction/band rows carry the thin-cirrus code; all corresponding cloud-probability footprints contain zero. T3's coarse B01 Sen2Cor footprint includes multiple scene classes, as documented by Roger. An ACOLITE-specific quality mask is not supplied. Availability of all 108 values is not quality clearance. Physical-validation holds remain unchanged. ASD coverage and field/satellite time mismatch are not limitations of this satellite-only comparison. They must not be attached to the renewed spectra.

## Successor files and plotting contract

All paths below are relative to this existing investigation. No report, figure or prior metric file was edited.

| File | Purpose |
|---|---|
| `tables/ctr48_plot_values.csv` | 108 full-precision plotting rows; original labels, ordered bands, wavelengths, correction, reflectance, finite mask and point QA flag |
| `tables/ctr48_pairs.csv` | 54 independently rebuilt finite pairs, with signed Sen2Cor minus ACOLITE differences |
| `tables/ctr48_accounting.csv` | Every target, requested/available/missing band counts and negative-value counts |
| `tables/ctr48_target_summary.csv` | Descriptive within-target differences across nine bands |
| `tables/ctr48_band_summary.csv` | Descriptive within-band differences across six targets |
| `tables/ctr48_spectral_steps.csv` | All 48 adjacent-band steps in both curves; full-precision shape evidence |
| `tables/ctr48_scale_ranges.csv` | Exact data extrema and optional 5%-padding limits, globally and per target |
| `tables/ctr48_R_crosscheck.csv` | Independent R-versus-Python numerical residuals and tolerance |
| `provenance/ctr48_validation.json` | Assertion results, input/output hashes and audit scope |
| `provenance/ctr48_R_validation.txt` | R checks and actual software/session versions |
| `provenance/ctr48_preflight.json` | Baseline preservation hashes, environment/readiness and ownership evidence |

Use the same 108 plotting values for both versions. All six targets, both corrections and all nine bands must remain. The global observed reflectance range is −0.0313 to 0.5938; all axes must contain their applicable valid values. The optional limits include 5% padding and are suggestions, not a required aesthetic choice. Within each target's alternative panel both correction curves share one y-axis range. `segment_id=1` applies only because this exact delivery has no missing bands; if missingness ever changes, break segments rather than connecting through unavailable values. Keep the same band order, labels, colours and values between versions. Clearly identify the alternative as separately scaled panels; only y-limits change.

Preserve Figure 1 unchanged and retain the renewed spectrum as Figure 3, with exactly two scientific figures in each report. No ASD spectrum, scatter or extra plate is authorized. Scientific report prose should use the findings and limitations above, without task IDs, paths, logs, metadata or reproduction commands. Technical detail belongs in this supporting handoff and the source package. Keep Figure 1's existing provenance and metric evidence separate from the new target comparison.

## Reproduction and preservation

From the original project root, with existing locked environments and original sources available:

```bash
./scripts/check-env.sh
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr48_validate.py
./scripts/project-env.sh Rscript analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr48_check.R
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr48_package.py
```

No seed is needed because the analysis is deterministic. The Python checks preserve 488 prior tracked files and all 123 unrelated CTR39 files by SHA-256, including Figure 1, prior values and metric evidence, all reports/figures, manuscript, CTR24 dictionary and lockfiles. Raw data were read only. The analysis-only path readiness gate passed. The pre-existing clean-workspace guard refusal due to unrelated untracked CTR39 files remains; none was deleted, stashed or staged and no guard was bypassed. The local task branch is `ctr-48-target-validation`; no pushed branch or PR is claimed. This closes only the assigned numerical handoff, not the independent review or PI approval gates.
