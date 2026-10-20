---
title: "Satellite–ASD reflectance matchups at Banc d’Arguin"
subtitle: "Final analysis report for CTR24 · Figure 3 revision requested 20 October 2026"
author: "Ctrl+Sea · report revision by Rachel Carson · prior figures by Edward Tufte · validated numerical tables by Thomas Bayes"
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
        body {color:#222;} .quarto-title h1 {font-weight:650;}
        table {width:100%;font-variant-numeric:tabular-nums;font-size:.88rem;margin:1.2rem 0;}
        th,td {padding:.35rem .45rem;border-bottom:1px solid #e0e4e7;}
        th {text-align:left;} figcaption {line-height:1.45;}
        code {overflow-wrap:anywhere;} .cell-output-display {overflow-x:auto;}
        </style>
execute:
  enabled: false
---

## Take-home message

The six-station comparison identifies satellite–ASD reflectance discrepancies, but does not establish atmospheric-correction accuracy. In the supported B02/B03/B04 set, pooled RMSD is 0.065747 for Sen2Cor and 0.036927 for ACOLITE, with positive signed biases of +0.051881 and +0.022718, respectively. These are arithmetic descriptions of the fixed 18 station–band values per correction. **All 18 triples retain physical holds; zero pairs are validation-eligible.** Differences in spatial support and surface exposure prevent interpreting the smaller numerical discrepancy as evidence of a superior correction.

The requested Figure 3 style is reproduced below from the supplied nine-band table. Its annotations reproduce the example’s rounding exactly. That broader table is presented as a **supplied-table reproduction**, separate from the supported three-band analysis; its additional bands have not been established as valid matchups by this task.

## Meaningful results

### The requested Figure 3 reproduction

![Reproduction of the supplied Figure 3 numerical content and visual style: ASD on x, satellite on y, Sen2Cor and ACOLITE in adjacent panels, identical equal-aspect axes and a dashed 1:1 line. Colours follow the supplied band palette; symbols identify surface classes. The supplied CSV contains seven stations and nine bands per correction. Excluding AC04, with AC03 already absent, leaves six stations × nine bands = 54 values in each panel. Annotations are recomputed descriptive RMSD and signed bias, rounded to three decimals. This reproduces the example’s displayed values: Sen2Cor 0.066 / +0.050; ACOLITE 0.042 / +0.020. The legend includes Algal mud (AC05), which remains in the plotted set and is not renamed Macroalgae. Reproduction does not establish spectral coverage or physical equivalence for the added bands. No regression, confidence interval or error bar is inferred.](figures/generated/ctr38_figure3_reference.svg){#fig-reference width=183mm}

The reproduction retains the original example’s band colours, black point outlines, surface symbols and restrained axes. It uses equal ranges on x and y to preserve the geometry of the 1:1 comparison. It adds a complete four-class legend: the example’s three-class legend does not account explicitly for the included AC05 Algal mud values. B7, B8 and B8A retain the supplied black colour; their individual identities cannot be distinguished by colour in this reproduction, so this view supports overall discrepancy inspection rather than identification of those three individual bands. The source table preserves every band label.

### The supported three-band comparison in the same style

![Exploratory comparison of exactly the same 18 station–band triples in both correction panels: AC01, AC02, AC05, AC06, AC07 and AC08 × B02/B03/B04. Band labels B2/B3/B4 in the legend correspond to B02/B03/B04 in the saved analysis tables. Values come directly from the exact CTR-37 numerical handoff. Both axes have identical limits and equal aspect; the dashed line is 1:1. Bias is satellite minus ASD. Pooled annotations weight each station and each band equally; N is a count of repeated spectral values, not independent replication. Units are dimensionless reflectance (1). Physical support and exposure holds remain; zero validation-eligible pairs. AC03 mbp_mud and AC04 mpb_mud are excluded, with original labels preserved in the ledger. AC05 algae_mud is included and displayed as Algal mud.](figures/generated/ctr38_figure3_primary.svg){#fig-primary width=183mm}

The supported data overlap the supplied CSV in all 36 correction-specific values. Absolute differences are below 1 × 10⁻¹² for both ASD and satellite reflectance; these are decimal serialization differences, not changed inputs. The source-audit CSV records every overlapping comparison. The nine-band reproduction and three-band analysis have different denominators and therefore different pooled statistics; their annotations must not be interchanged.

SUMMARY_TABLE

Here **primary** means the supported three-band exploratory set; **reference** means the supplied-table nine-band reproduction. RMSD and RMSE denote the same square-root mean squared difference here. All metrics use dimensionless reflectance (1). Each pooled value has weight 1/18 in the primary set or 1/54 in the reference reproduction. Because every station has the same band count within each set, weighting is equal across stations and bands. These counts are not independent sample sizes. The reference rows are display summaries only and cannot extend the scientific scope of the primary rows.

### Which stations contribute the discrepancies?

Sen2Cor station biases are positive at all six primary stations, ranging from +0.009023 at AC07 to +0.107728 at AC06. ACOLITE biases range from −0.001827 at AC06 to +0.064366 at AC08. These differences describe this fixed set of locations and bands; they do not demonstrate a general correction ranking.

At AC06, the ACOLITE bias of −0.001827 accompanies MAE 0.007502 and RMSD 0.008342. Opposite-signed band discrepancies partly cancel in the bias, so a near-zero bias does not imply agreement in every band. The station panels retain the magnitude and spectral pattern of these differences on a common vertical scale.

![Station-level band-integrated ASD reference, Sen2Cor operational L2A and ACOLITE DSF reflectance, reusing the previously delivered station figure without rerendering or modifying its numerical content. The six panels use consistent axes. Lines connect the supported bands only as visual guides. Per-station bias, MAE and RMSE use three bands, with no independent-replication interpretation. Reflectance is dimensionless (1); all 18 triples remain exploratory with unresolved physical holds and zero validation-eligible pairs. AC03 mbp_mud and AC04 mpb_mud are excluded; AC05 algae_mud remains included.](figures/generated/ctr38_station_spectra.svg){#fig-stations width=180mm}

STATION_TABLE

Station metrics are copied from the saved full-precision CTR-37 table and rounded here to six decimals. Pooled metrics are arithmetic summaries of its exact paired values and are independently checked against the saved station metrics. RMSD pooling uses the square root of the mean station squared RMSDs, not the mean station RMSD.

## Issues and limitations

The supported ASD references describe small field footprints; the satellite values describe stored containing cells. Effective radiometric contributors and representative material-patch support have not been resolved. Material-patch representativeness remains uncertain at AC01, AC02, AC06, AC07 and AC08; exposure or optical-path ambiguity also remains at AC05, AC06 and AC08. Effective-support bounds remain unverified at all six stations. These restrictions are carried forward from the existing analysis and are not removed by reproducing the example.

Field observations are described as around acquisition, but exact station clock/timezone, station-average membership, scan variance and calibration variance are unavailable. Shared scene identity is documented; byte-identical upstream L1C ancestry has not been established. Consequently, no confidence intervals, p-values, independent-replicate interpretation, fitted regression or population-level accuracy claim is reported.

The supplied CSV adds B1, B5, B6, B7, B8 and B8A to the supported B2/B3/B4 overlap. These added values lack the complete source-to-reference eligibility verification used for the primary set. **B08 fails spectral coverage in the existing analysis.** Rendering a supplied B8 value does not reverse that finding. The broader reproduction is therefore excluded from conclusions about correction performance. Its numbers are traceable to the supplied table, but their physical validity is not established here.

The supplied R script cannot run unchanged against the attachments: it expects 144 rows and 72 values per correction, whereas the supplied CSV has 126 rows and 63 values per correction. It also requires an unattached `figure3_metrics.csv`, with an “AC03 included” sensitivity and confidence intervals. AC03 is absent from the supplied CSV. The revised renderer uses transparent direct arithmetic for point annotations, retains the original script unchanged, and adds no uncertainty estimates. The original script’s regression and confidence ribbon are also absent from the supplied example and are not used.

### Station coverage and exclusions

The project exclusion ledger retains the authenticated labels **AC03 mbp_mud** and **AC04 mpb_mud**. The supplied CSV has no AC03 rows and has AC04 labelled “Microphytobenthos mud”; those AC04 rows remain in the preserved source CSV but are omitted from both new figures. No source value is deleted. AC05 retains the original project label **algae_mud** and remains included; its supplied-table display label is **Algal mud**. This task makes no taxonomic reclassification.

Seven supplementary stations have no exported matched satellite values or band-integrated ASD references in the saved handoff. Their missing values remain NA, with zero common bands for each correction; continuous ASD spectra do not fill the missing matchups.

MISSING_TABLE

The existing empty validation-eligible table and the 14 station–correction supplementary metric rows are retained separately. No supplementary station is silently replaced or assigned a zero reflectance.

## Implications and next steps

The figures identify where the supplied products diverge from station references and show how pooled discrepancies change when additional supplied bands are displayed. They are useful for diagnosing follow-up needs, especially spatial-support and exposure verification. They do not establish which correction should be preferred for ecological inference.

The supported three-band view and station metrics should carry the scientific interpretation. The nine-band view records the requested example reproduction. Before any wider-band validation claim, the added bands require their own identity, integration coverage, quantity, decode and physical-matchup checks. Independent review of this exact revision must precede PI submission. Scientific approval, manuscript integration, merge and publication are separate gates.

## Short methods

**Question.** How do supplied Sen2Cor and ACOLITE reflectances differ from the available ASD station references, and can the requested Figure 3 style be reproduced transparently?

**Study system and saved data.** The documented scene is Sentinel-2B, tile T28QCH, Banc d’Arguin, Mauritania, 27 March 2026, acquired at 11:45:53.975343 UTC. The primary figure reuses CTR-37 numerical tables at commit `9a4ec93fc412736fda85b44a1aab56ed6e2c2beb`, as delivered within CTR-38 author revision `dd00258982cd3050d74d9a41291a1bf6fb061abc`. Its saved audit and file hashes are checked before plotting. The example reproduction uses the PI’s authenticated attachments from comment `e6a042c8-55d1-433d-afce-18a6b2f9ec0d` (20 October 2026).

**Existing processing, reused here.** Supplied Sen2Cor operational L2A PB05.12 was decoded as (DN − 1000)/10000 after masking DN 0 and 65535. ACOLITE DSF rhos is dimensionless Float32 surface reflectance. The supported ASD references use supplied S2B v4 spectral response functions and normalized response-weighted trapezoidal integration on union knots, with no extrapolation, finite interpolation across gaps no larger than 1 nm and minimum response coverage 0.999. V5 sensitivity remains separate and is not mixed into these figures. These are documented upstream methods; this revision performs no raster extraction, atmospheric processing or spectral integration.

**Summaries and rendering.** For difference d = satellite − ASD, bias = mean(d), MAE = mean(|d|), and RMSD = √mean(d²). Summaries use identical station–band keys in each correction. Arithmetic annotations are recalculated from saved or supplied small tables under the latest reproduction request; no statistical model is fitted. Valid negative reflectance would be retained by extending the plotting limits; no plotted finite reflectance is negative in these inputs. Signed negative discrepancies are retained.

The renderer uses base R graphics and grDevices in the approved repository environment, because the attached script’s plotting packages are not present there. No package or system installation is needed. Both new figure sets are 183 × 124 mm, with 600 dpi PNG and vector SVG/PDF. Source figures use colour plus shape; their legends retain literal surface meanings. The retained station figure is the earlier 180 × 220 mm vector output. Only this standalone report is rendered under the existing CTR24 configuration; the reviewed dictionary and final manuscript are not rebuilt.

## Review and approval status

This is the completed report draft and figure revision prepared for author confirmation, presentation review and Karl Popper’s independent scientific review. It is not an approved scientific result. Rachel Carson prepared this report revision and does not claim independent review of her own additions. The earlier author QA does not automatically approve this changed revision. Native stage decisions and the exact delivery commit must be recorded on CTR-38. Charles Darwin coordinates PI submission after substantive findings are resolved. No manuscript integration, merge or publication is authorized by this report.

## Appendix: reproducibility and files

From the canonical repository root on the Linux Mint Research Worker:

```bash
.venv/bin/python analysis/CTR-24_data-dictionary/scripts/ctr38_figure3_revision.py
```

The command checks original attachment hashes, saved numerical manifest hashes, overlapping values, identical correction keys, exclusion membership, finite values, and the empty eligible-validation table. It verifies primary pooled arithmetic against saved per-station metrics, checks the example’s displayed rounding, renders both new figures through the repository’s safe figure writer, generates this editable QMD, and renders self-contained HTML. It writes only new revision-specific paths inside the existing CTR24 analysis. It preserves the prior report and figures. Reproduction regenerates these candidate outputs; PDF metadata may vary even when the displayed content is identical.

Source and table hashes are recorded in `provenance/ctr38_figure3_manifest.json`; machine-readable QA is in `provenance/ctr38_figure3_revision.json`. The exact containing commit, bundle SHA-256 and review findings are saved in the CTR-38 task document rather than embedded in their own hashed files. Full-precision summary metrics, station metrics, source-overlap checks, paired plotting values, the original attachments and the adapted renderer are included in the source/table bundle. The complete bundle also includes the self-contained HTML and both new figure sets. The report adds no external scientific references; scene and method statements are attributed to the preserved task analysis rather than to unverified literature.

INPUT_HASH_TABLE
