# Downstream table contract

ΔR = ACOLITE − Sen2Cor; all reflectance and SD values are dimensionless. Bands are B2, B3, B4, B8; B8A is excluded. Scope: the full supplied ACOLITE crop, EPSG:32628, 10 m, E=334050–371680, N=2190240–2209980 m. Primary descriptive tables do not imply scientific approval.

`date_band_summary.csv` has a unique `(pair_id, band, domain)` key. `date` is ISO acquisition date; `sensor` is S2A/S2B/S2C; `tile` is T28QCH. All 22 pairs appear for all four bands and six domains, including empty cases.

| Field | Meaning |
|---|---|
| domain | primary / include_SCL7 / exclude_high_TOA / complete_dates / coverage80 / common_footprint |
| median_delta | Spatial median of paired pixel ΔR within this row's domain; blank if n=0 |
| sd_delta | Spatial sample SD, denominator n−1; blank if n<2 |
| n_valid | Valid paired pixels in this row's domain; spatially dependent |
| n_grid | Fixed rectangular grid cells, 7,428,162 |
| coverage_fraction | n_valid / n_grid for this row's domain |
| n_footprint | Finite paired observations before quality masks, per band/date; primary diagnostic repeated across domains |
| footprint_valid_fraction | Primary n_valid / n_footprint; primary diagnostic repeated across domains |
| n_ac_negative_retained / n_sen_negative_retained | Counts under primary QA, repeated across domains; not domain-specific counts |
| min_delta / max_delta | Full data range in this row's domain, never display-clipped |
| n_ac_encoded_fill | Exact netCDF default fill count in the raw ACOLITE band, excluded despite declared NoData=NaN; repeated across domains |
| flags_available | Whether ACOLITE quality flags were supplied |
| exclusion_reason | Primary-date exclusion if no primary valid pixels; row n_valid separately identifies empty sensitivity domains |

The 80% core requires ≥18 valid dates, not 18 independent observations. Complete-date and 80% cores are band-specific fixed spatial masks; a particular date can still have missing observations in the 80% core. The common-footprint core requires finite observations in all four bands on every date before QA. SCL and high-TOA sensitivity rows retain their own n_valid and spatial summaries; repeated primary diagnostics must not be mistaken for those domains' diagnostics.

`acquisition_inventory.csv` records every candidate and its inclusion/exclusion reason. `band_mapping.csv` records actual wavelengths and decoding. `quality_counts.csv` reports marginal flags/SCL counts on the fixed grid (categories overlap; flag counts do not sum to exclusions). `temporal_coverage.csv` records the histogram of valid temporal counts. `temporal_raster_summary.csv` describes full-resolution map-value distributions, not temporal means or accuracy. `display_limits.csv` audits full-resolution clipping only for visualization.

Modelling should start from domain=primary, retain sensor, baseline/date and coverage information, and assess coverage sensitivity. The spatial SD is not a measurement-error standard deviation, confidence interval, or standard error. The date-level temporal sequence mixes unequal date gaps, sensors, atmospheric states and seasonal/tidal conditions; causal or ecological trends require separate justification.
