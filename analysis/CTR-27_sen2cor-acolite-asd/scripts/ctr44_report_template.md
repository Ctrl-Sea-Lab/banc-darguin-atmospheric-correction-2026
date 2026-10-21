---
title: "Satellite–ASD reflectance at Banc d’Arguin"
subtitle: "Retained supplied-table matchup and 7 March 2026 station spectra"
author: "Ctrl+Sea · Edward Tufte · verified numerical handoff by Thomas Bayes and Roger Tomlinson"
format:
  html:
    embed-resources: true
    toc: true
    toc-depth: 2
    number-sections: false
    theme: cosmo
    include-in-header:
      text: |
        <style>
        body {color:#222;} table {width:100%;font-size:.85rem;font-variant-numeric:tabular-nums;border-collapse:collapse;}
        th,td {padding:.35rem .45rem;border-bottom:1px solid #e0e4e7;text-align:left;}
        figcaption {line-height:1.45;font-size:.9rem;color:#444;margin-top:.7rem;}
        figure {margin:1.5rem 0;} figure img {max-width:100%;height:auto;} code {overflow-wrap:anywhere;}
        </style>
execute:
  enabled: false
---

## Take-home message

Both Sen2Cor and ACOLITE have all nine requested satellite bands at 13 retained stations for **7 March 2026**. ASD spectra measured on **27 March 2026**, 20 days later, support eight band-integrated references at each station. **ASD B08 remains NA because of insufficient response coverage.** The new spectra show available satellite values without filling that reference gap. These are exploratory cross-date comparisons: **zero pairs are validation-eligible**, and the figures do not establish correction accuracy or superiority.

Figure 1 retains the supplied-table matchup, its values, symbols and legends unchanged. Its source context is the preceding 27 March report; the supplied CSV has no acquisition-date column and is not reattributed to 7 March. The new station spectra have their own verified acquisition date and provenance.

## Meaningful results

### Figure 1 — retained supplied-table matchup

<figure id="fig-retained">
<img src="figures/generated/ctr38_figure3_reference.svg" alt="Unchanged supplied-table matchup: Sen2Cor and ACOLITE, surface shapes and nine band colours." style="width:183mm">
<figcaption><strong>Figure 1.</strong> Retained reproduction of the PI-supplied nine-band table, originally delivered in revision 51805d91ffdef5cafa81c11fd91a74163eec4d83. Each correction contains 54 values (six stations × nine bands); the dashed line is 1:1 and axes have equal aspect. Colours identify bands; the surface legend sits bottom-right in Sen2Cor and the band legend in ACOLITE. Sand uses one symbol for dry_sand and white_sand; AC05 algae_mud is displayed as Macroalgae; Seagrass is unchanged. B7/B8/B8A share the supplied black colour. Printed RMSD/bias remain 0.066/+0.050 (Sen2Cor) and 0.042/+0.020 (ACOLITE), with dimensionless reflectance. These are supplied-table display summaries, not new March7 results or validation errors. The added supplied bands, including B08, have not been established as physically eligible matchups. AC03 mbp_mud and AC04 mpb_mud remain excluded.</figcaption>
</figure>

The original attachments in `provenance/pi_figure3_20261020/` are preserved byte-for-byte. Their supplied script expects 144 rows and an unattached metrics file, while the CSV contains 126 rows; the retained graphic uses the previously documented direct reproduction. It adds no regression or confidence interval. The source table is not changed by the new acquisition analysis.

### Figure 3 — early-March station spectra

The verified scene pair is Sentinel-2B, tile T28QCH, orbit A047010/R080, sensed **7 March 2026 at 11:45:54.425534 UTC**. Both corrections have 117 finite values (13 stations × nine bands). The primary v4 ASD reference has 104 finite values and 13 B08 NA entries. No satellite band is missing in this handoff.

<figure id="fig-march-primary">
<img src="figures/generated/ctr44_march_primary.svg" alt="Six primary station spectra across all nine bands, showing ASD B08 as missing and satellite cloud or shadow flags." style="width:183mm">
<figcaption><strong>Figure 3.</strong> A–F: AC01, AC02, AC05, AC06, AC07 and AC08. ASD band-integrated references (black squares; supplied S2B SRF v4) were measured on 27 March; Sen2Cor (blue circles) and ACOLITE (orange triangles) represent 7 March. Axes show dimensionless reflectance and the nine band positions at common metadata wavelengths, with unequal wavelength spacing. All primary and supplementary panels share the same y range. Lines guide the eye only within the supplied availability segments: the ASD line stops at B07 and B8A is an isolated point, with no bridge across unsupported B08. “NA [COV]” denotes insufficient ASD response coverage, never zero. Outer rings identify stored-cell SCL cloud/shadow context; finite flagged values remain visible. ACOLITE context is transferred geometrically from same-acquisition Sen2Cor SCL, not independent ACOLITE QA. No old three-band metric annotations are reused. Exclusions remain AC03 mbp_mud and AC04 mpb_mud.</figcaption>
</figure>

<figure id="fig-march-supplementary">
<img src="figures/generated/ctr44_march_supplementary.svg" alt="Seven supplementary D06 station spectra with both correction series, eight supported ASD bands and B08 NA." style="width:183mm">
<figcaption><strong>Figure S1.</strong> A–G: D06_A through D06_G, retaining supplementary status. The series, dates, scales, missingness and flag symbols follow Figure 3. The original label zn is preserved without assigning a new ecological class; D06_G sand is displayed as Sand. Newly available numerical extraction does not establish physical representativeness or validation eligibility.</figcaption>
</figure>

### Availability and station accounting

AVAILABILITY_TABLE

Counts are per primary SRF role (`v4_primary`), not independent replicates. Eight bands have 13 shared finite triples each. The 0.999 response-coverage rule uses the complete-response denominator: B08 has coverage 0.9948579691930339 (v4; response extends to 907 nm) against measured ASD support of 400–900 nm. Saved official v5 sensitivity also fails B08 (0.9950095750145522; extends to 906 nm). No threshold relaxation, extrapolation or truncated denominator is used. All other band references pass. The small v4/v5 sensitivity does not resolve physical or temporal holds.

ACCOUNTING_TABLE

The two original exclusions account for the remaining stations. D06 stations remain supplementary; their available March7 satellite values and supported ASD references now appear explicitly. Previous statements that all supplementary satellite values were unavailable do not describe this new handoff.

## Issues and limitations

**Different dates and physical support.** The 20-day gap precludes a coincident validation claim. Exact station clocks/timezones, overpass exposure and optical state, effective footprint, registration accuracy and target representativeness remain unresolved. Existing material-patch and exposure holds are retained. Containing cells are unequal: Sen2Cor B01 is 60 m, B02/B03/B04/B08 are 10 m, and B05/B06/B07/B8A are 20 m; ACOLITE exports all bands at 10 m. Stored-cell size does not establish equivalent optical support. Shared cells and spectral bands are dependent.

**Operational quality context.** Of 234 satellite rows, 109 carry stored-footprint SCL cloud/shadow flags: 55 Sen2Cor and 54 ACOLITE contexts. Finite values are retained and ringed, not silently screened. ACOLITE declares masking disabled. Transferred SCL flags are not an ACOLITE classification, and unflagged stored cells do not demonstrate complete optical-footprint clearance. AC05, AC06, AC08, D06_A, D06_B and D06_C have all eight supported metric bands flagged for both corrections; D06_D also has a Sen2Cor B01 flag. Even the 55 jointly unflagged finite triples remain ineligible for validation.

**Missingness and reason codes.** `COV` is the compact plot label for the exact table reason `insufficient_coverage`; B08 ASD values remain literal NA. Both satellite series retain their B08 values. No other satellite/reference missingness occurs among retained stations for the eight supported bands. `original_PI_mud_exclusion` identifies AC03/AC04, and `cross_date_and_physical_holds` identifies retained stations. Exact per-row availability and hold reasons, QA and dates remain in the unchanged CTR43 tables. A numerically finite triple is not scientific eligibility.

**Interpretation.** No confidence intervals, fitted model, significance tests, population accuracy estimate or correction ranking are inferred. The supplied Figure 1 and March7 spectra use different provenance and must not share metric annotations. The current figures do not show a contextual full ASD curve; no unsupported integration is implied.

## Implications and next steps

The new spectra permit inspection of bandwise differences for both correction products while making temporal mismatch, flagged cells and missing ASD support visible. Resolving B08 requires additional measured spectral support. Validation requires evidence addressing date, exposure, spatial support and QA, followed by independent review. Charles Darwin will route this exact revision through Rachel Carson’s presentation review and Karl Popper’s independent scientific review before PI submission.

## Short methods

**Question and inputs.** How do the available ASD station references compare descriptively with both correction products from the verified early-March acquisition? This presentation consumes the exact CTR43 handoff at `dc10ebe93e8e5053f4f7fb6aa377ba7fb9a174bd`, based on Roger’s CTR42 extraction at `51eeaf86353e895d18ee8f0747642d45d612909e`. It performs no extraction, spectral integration or new statistics. Supplied Figure 1 uses the original authenticated attachments from comment `e6a042c8-55d1-433d-afce-18a6b2f9ec0d`; these do not carry a verified new March7 date.

**Upstream processing.** Sen2Cor L2A `S2B_MSIL2A_20260307T113319_N0512_R080_T28QCH_20260307T154921.SAFE` is decoded as (DN − 1000)/10000 after excluding DN 0/65535. ACOLITE rhos is dimensionless Float32 surface bidirectional reflectance without another scale/offset or Rrs conversion. Its recorded L1C identity agrees with the L2A L1C tile metadata; identical upstream L1C bytes remain unverified. ASD integrations use supplied v4 response functions, full denominators, union-knot trapezoidal integration and no extrapolation. Saved official v5 is sensitivity only; it is not mixed into the primary plotted series.

**Plotting.** Exact `plot_wavelength_nm`, `band_order`, `reflectance` and `segment_id` fields are read from `ctr43_spectral_long.csv`, selecting only `v4_primary`. Common x positions follow ACOLITE S2B metadata wavelengths and do not resample the values. All nine rows per series are retained, including NA. Finite negative values would be retained by the common limits; none occur here. No metrics are recomputed; Figure 1 rounding is checked against its retained saved summaries. Base R/grDevices in the approved project environment exports 600 dpi PNG and vector PDF/SVG at 183 × 200 mm (primary) and 183 × 250 mm (supplementary). Figure 1 remains 183 × 100 mm.

## Review and approval status

This author revision is ready for the existing exact-revision review route on CTR38. It has not received Rachel’s or Karl’s review, or PI approval. Prior presentation acceptance and relocation authorization do not approve the new March results. No manuscript integration, merge or public publication is authorized.

## Appendix: reproduction and files

From the original authorized Linux Mint repository root:

```bash
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr44_delivery.py
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/validate_delivery.py
```

The first command verifies the frozen input and retained-figure hashes, generates the spectra through the safe figure writer, rebuilds this QMD from its template, renders standalone HTML under the investigation configuration, and creates a compact offline report and packages. The validator checks every plotted row against the frozen handoff, NA segments, counts, dates, exclusions, rounding, resources, links and preserved Figure 1 values. It never runs CTR42 extraction or CTR43 numerical preparation. The compatibility entry point `ctr38_figure3_revision.py` now routes to this presentation, so it cannot recreate the removed scatter.

`CTR44_complete-delivery.zip` contains the editable QMD, both HTML versions, PNG/PDF/SVG graphics, input tables, original attachments, sources, provenance and a hash manifest. `CTR44_source-and-tables.zip` provides editable sources and numerical evidence; `CTR44_portable-report.zip` contains both standalone HTML reports. Local reproduction also uses the repository’s existing `scripts/figure_io.py`, `scripts/project-env.sh` and `scripts/render-analysis.sh`, and approved lockfiles. The package includes copies of these helpers for inspection, without replacing repository configuration. Package timestamps and PDF creation metadata can vary while plotted rows and graphics remain unchanged.

Historical raw/shared supporting tables and evidence remain protected. The removed scatter, dedicated metrics, captions, narrative, earlier station plots and renderers are recoverable from Git revision `51805d91ffdef5cafa81c11fd91a74163eec4d83`; historical provenance manifests describe that older delivery and are not current validation receipts. The current manifest and QA are `provenance/ctr44_manifest.json` and `provenance/ctr44_validation.json`. The exact final commit and archive hashes are recorded in the saved figure-delivery task document, avoiding self-referential hashes. No external scientific literature was needed for this presentation-only revision.
