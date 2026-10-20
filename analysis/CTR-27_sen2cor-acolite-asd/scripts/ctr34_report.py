#!/usr/bin/env python3
"""Assemble the current scientific-first CTR-34 amendment in the parent investigation."""
import json,sys,csv,subprocess
from pathlib import Path
import ctr34_support as m
P=m.P;ROOT=m.ROOT

def mdtable(rs,cols):
 def clean(x):return str(x).replace('|','/').replace('\n',' ')
 return '| '+' | '.join(cols)+' |\n| '+' | '.join('---' for _ in cols)+' |\n'+''.join('| '+' | '.join(clean(r.get(k,'')) for k in cols)+' |\n' for r in rs)+'\n'
def main():
 c=json.loads((P/'outputs/ctr34_release_contract.json').read_text());v=json.loads((P/'provenance/ctr34_validation.json').read_text());primary=m.PRIMARY;dec=m.rows('tables/ctr34_target_decisions.csv');qa=m.rows('tables/ctr34_local_qa.csv');summ=m.rows('tables/ctr34_current_spectral_summary.csv');sup=m.rows('tables/ctr34_support.csv');lg=m.rows('tables/ctr34_candidate_ledger.csv')
 masks=[]
 for r in lg:
  if r['station_id'] in primary and r['band_id'] in m.BANDS:
   centre=next(x for x in qa if x['station_id']==r['station_id'] and x['kind']=='SCL' and x['dx']==x['dy']=='0')
   masks.append({'matchup_id':r['matchup_id'],'station_id':r['station_id'],'band_id':r['band_id'],'L2A_stored_finite':True,'ACOLITE_stored_finite':True,'L2A_special_codes_absent':True,'QUALIT_5x5_all_zero':True,'DETFOO_5x5_valid':True,'SCL_centre':centre['raw'],'SCL_common_eligibility':'conditional_physical_evidence_required','common_effective_support_QA':'unknown','physical_match':'unknown_material','common_inclusion':False,'same_decision_both_methods':True,'rule_version':m.VERSION})
 m.table('tables/ctr34_common_masks.csv',masks)
 schema={'version':m.VERSION,'csv_null':'empty means unknown/not evaluated/not applicable according to status/reason; never zero or pass','csv_boolean':'True or False; parse explicitly','primary_key':{'candidate_ledger':'matchup_id','targets':'target_id','support':'support_id','qa_cells':'qa_cell_id','qa_links':['matchup_id','qa_cell_id'],'held_diagnostics':'matchup_id','eligible_pairs':'matchup_id'},'natural_matchup_key':['target_id','occasion_id','band_id','extraction_version'],'source_identity':'qualified source/path and grid; existing full-file small-input IDs in outputs/normalized_design.json; new raster sources use path IDs with separate grid/window identities','source_id_namespaces':'References/occasions retain accepted IDs and link to accepted normalized sources; current support/QA path IDs resolve in ctr34_sources.json','support_semantics':'stored-cell contributors have numerical weight1; upstream native contributors/effective bounds null and held; statistical weights null. QA cells never radiometric contributors','qa_cell_station_dx_dy':'one witness inspection record after deduplication; NOT exclusive ownership or all target memberships. qa_links carries many-to-many membership; local_qa contains every window-relative observation','qa_layers':['ANC_LOST','ANC_DEG','MSI_LOST','MSI_DEG','DEFECT','NODATA','PARTIALLY_CORRECTED','SATURATED'],'validity':'pass/fail/unknown_material/not_evaluated/excluded states; included booleans false throughout','graph':'actual union across primary targets and B02-B04/both corrections; null components; nominal, QA and diagnostic relations separately recorded','weight_formulas':c['weights'],'scene_pairs':json.loads((P/'outputs/normalized_design.json').read_text())['scene_pairs'],'current_table_prefix':'ctr34_; legacy unprefixed tables/figures/outputs are CTR28 historical evidence'}
 m.dump('outputs/ctr34_schema.json',schema)
 lead='''---
title: "March 27 ASD–satellite matchups: support and exposure remain unresolved"
subtitle: "CTR-34 execution amendment to CTR-27 • technical submission for independent review"
author: "Roger Tomlinson"
format: html
execute:
  enabled: false
---

## Scientific findings

**No primary ASD–satellite matchup is justified under the frozen release contract.** The six intended non-mud targets provide at most 18 candidate B02–B04 pairs; all 18 remain held. Every per-band paired set and their complete-spectrum intersection P* is empty. No pooled estimate, ASD error metric or correction ranking is available. This is a physical-comparability result, not a finding of zero error or equivalent correction performance.

Source rasters cover the stations and nominal 10 m grids align. All eight native quality layers are clear, and valid detector IDs are present in the inspected 5×5 windows. The remaining obstacle is more specific than missing raster values: these windows do not establish the effective native radiometric support, its complete QA, or the representativeness of a few cm² ASD measurement at the observed local image transitions. At three stations, SCL water labels also leave an unresolved exposed-target optical comparison. Neither SCL nor RGB proves submergence or ecological identity.

The PI confirms AC01/02 near Iwik on sand, other AC stations offshore, approximate acquisition-window timing, and field measurements in patches considered homogeneous at Sentinel-2 scale. That testimony is retained as supporting evidence. The intrinsic ASD support remains a few cm² at GPS; it has not been enlarged to a pixel. Numerical GPS error, precise field intervals/timezone and reference variance remain unknown, and are not automatic holds by themselves.

**AC03 (`mbp_mud`) and AC04 (`mpb_mud`) are excluded from every new analytical summary and figure.** AC03 is conservatively treated as a spelling alias of the PI-excluded mud microphytobenthos class, with its raw label preserved. The metadata scan of the full supplied cover table, GPS workbook and field log found no other explicitly documented mud-microphytobenthos target. `algae_mud`, sand and seagrass remain intended targets.

## Station decisions and population coverage

The table distinguishes successful checks from the remaining physical decision. Every station has clear inspected native defect/detector masks. The zero retained targets include losses from **both geographic groups and all four literal intended classes**: `dry_sand`, `algae_mud`, `white_sand`, `seagrass`. Even a later nonempty subset cannot support a population-wide ranking without Charles's metadata coverage reconciliation.

'''
 stationrows=[]
 st={r['station_id']:r for r in m.rows('tables/ctr34_targets.csv')}
 for d in dec:
  s=d['station_id'];scl=next(x['raw'] for x in qa if x['station_id']==s and x['kind']=='SCL' and x['dx']==x['dy']=='0');stationrows.append({'Station':s,'Group':st[s]['geographic_group'],'Literal class':st[s]['class_literal'],'SCL centre':scl,'Included bands / intended':'0 / 3','Physical decision':d['primary_reason']})
 text=lead+mdtable(stationrows,['Station','Group','Literal class','SCL centre','Included bands / intended','Physical decision'])
 text+='''AC01/02 have SCL5 and a bare-surface appearance consistent with the PI's sand testimony. Their local RGB brightness boundary is consequential: L2A B04 varies by 0.1590 and 0.1607 across the analyst-selected 3×3 scenarios. These ranges describe spatial variation, not GPS accuracy or reference uncertainty. They do not disprove uniformity inside a single pixel, but prevent asserting a sufficiently bounded representative patch where effective support and ground registration are unverified.

AC05 has relatively uniform RGB appearance and all 25 inspected SCL cells labeled water. It is held for optical-state ambiguity rather than a demonstrated RGB heterogeneity failure. AC06 has a bright sand-like centre, yet nearby SCL5/6 and RGB transitions, with a 5×5 B04 range of 0.2420. Centre brightness cannot distinguish exposed sand from shallow/wet substrate with the available evidence. AC07 has centre SCL4 and textured vegetation-like imagery; AC08 crosses a SCL4/6 and RGB transition. These judgments use local physical evidence and the shared support limitation, without an invented universal heterogeneity threshold.

### Local imagery and QA

![Original-source B04/B03/B02 RGB windows at the six intended primary stations. Each panel covers 110×110 m. The white square and cross identify the containing 10 m cell and its centre, not the exact GPS point or ASD footprint. The yellow square marks an analyst-selected 3×3 scenario; it is not a verified support bound. Both products use the same fixed 0–0.6 reflectance stretch with square-root display; no image shift or reflectance fit was applied. North is up.](figures/generated/ctr34-local-imagery.png){fig-alt="Six non-mud stations in paired source RGB windows showing local brightness boundaries and vegetation texture; no accuracy assessment."}

![Native SCL context, using a 5×5 array of 20 m cells centred on each station's containing QA cell. The white square is the centre QA cell, not the ASD footprint or primary radiometric support. Green is SCL4, tan SCL5 and blue SCL6. The map shows QA ambiguity; these classes do not identify habitat or prove exposure.](figures/generated/ctr34-scl.png){fig-alt="SCL bare labels at Iwik; water labels and vegetation/bare transitions at offshore targets."}

A separate texture comparison found the highest local cross-product correlation at zero tested offset for all 18 station-band windows among the nine ±1-pixel offsets. This supports nominal relative alignment only. The two products share nominal imagery ancestry, and this is not independent ground registration or a measure of GPS error. No offset was fitted or applied. Original numeric diagnostics are in `ctr34_relative_registration.csv`.

### Current non-mud field spectra

![Thirteen current non-mud station-average spectra: six intended primary targets with all matchups held, and seven supplementary targets outside the primary population. AC03/04 are absent. Curves describe supplied station averages over 400–900 nm; no repeat-level uncertainty is available.](figures/generated/ctr34-current-spectra.png){fig-alt="Six intended and seven supplementary non-mud station-average spectra, excluding AC03 and AC04."}

Each spectrum has 501 wavelength channels. The means and SD below describe variation across channels; channels are not field replicates and SD is not uncertainty of a station average. Supplementary targets are displayed separately and cannot replace held primary stations.

'''
 sr=[]
 for s in summ:sr.append({'Station':s['station_id'],'Literal class':s['class_literal'],'Role':'intended; held' if s['station_id'] in primary else 'supplementary','Channel mean':f"{float(s['mean_across_channels']):.5f}",'Channel SD':f"{float(s['SD_across_channels_ddof1']):.5f}",'Min':f"{float(s['minimum']):.5f}",'Max':f"{float(s['maximum']):.5f}"})
 text+=mdtable(sr,['Station','Literal class','Role','Channel mean','Channel SD','Min','Max'])
 text+='''## Interpretation, limitations and next decisions

The supplied products and field testimony establish date, location, stated reflectance units and a route to original raster values. They do not fully establish the optical and spatial identity of the sampled surface. Nominal alignment cannot resolve native interpolation footprints or empirical image-to-ground registration. Pixel-scale texture and nearby boundaries make the unbounded support material; comparatively uniform RGB at AC05 does not resolve its exposed-versus-water optical path. Tide/wetness, shallow water, patch composition and adjacency remain possible confounders, not demonstrated causes.

This amendment does not declare the missing information permanently unrecoverable. Karl should independently assess whether a defensible native-support envelope and target-specific exposed/representative comparison can be justified from this evidence. Charles then reconciles that technical judgment and any dated amendment. A changed release decision must preserve the old contract and document its timing. Precise GPS accuracy or clocks must not be invented, and resolved PI questions should not be repeated. No new statistical-design assignment is needed.

P* is empty: pooled quantities are unavailable. D06 targets, B08, coarser bands, method-specific masks or altered weights cannot be used to populate it. If a subset is later released, a missing intended site/class or systematic exposure/support loss restricts it to a selected-subset description. Any replacement display or estimand requires Charles's dated amendment. PI approval of the earlier feasibility deliverable does not approve this execution amendment.

## Materials and methods

This is the CTR-34 execution amendment within the existing CTR-27 investigation, using the accepted CTR-28 audit and Thomas's existing contract. The fixed primary population is AC01, AC02, AC05, AC06, AC07, AC08; fixed bands are B02/B03/B04. The supplied S2B March 27 operational L2A SAFE and ACOLITE DSF `rhos` TIFFs are compared as supplied products. There is no atmospheric-correction rerun or controlled processor benchmark. Original raw datasets remain unchanged.

WGS84 longitude/latitude (EPSG:4326, traditional GIS coordinate order) is transformed to EPSG:32628. Stored-cell locations use floor indexing from original geotransforms, with zero-based rows/columns. B02–B04 have 10 m sensor sampling and stored grids. The L2A–ACOLITE integer crop offset is 3,405 columns and 9,006 rows. No primary raster resampling, AOI average or nearest-CSV substitution is used. The earlier 1,463 paired AOI cells have zero containing-cell joins to the 15 historical stations and remain historical context.

The read limits are 11×11 B02–B04 source windows at the six intended targets, 5×5 native defect/detector windows per band/target, and 5×5 native 20 m SCL windows. These are 198 read windows; 36 further one-cell reads export held diagnostics after the release freeze. The 3×3/5×5 offset scenarios are selected by the analyst; they are neither estimated GPS errors nor actual primary contributors. At the stored level, each held diagnostic uses one cell with numerical extraction weight 1. Upstream native counts/weights and effective-support bounds stay null.

L2A DN0 and DN65535 are masked before `(DN−1000)/10000`; ACOLITE `rhos` is already unitless Float32 and receives no extra scale or pi conversion. Valid negatives are retained. All eight MSK_QUALIT layers must be zero and MSK_DETFOO must contain detector IDs 1–12 over the common full support. SCL0/1/2/3/7/8/9/10/11 are excluded; SCL4/5/6 require compatible physical evidence. ACOLITE declares `l2w_mask=False`; separate flags are absent. Native SAFE flags provide a common same-scene diagnostic, with full-byte L1C ancestry unverified. Passing inspected masks does not pass unknown full support.

The supplied v4 S2B SRF remains primary; official v5 is a separate sensitivity. Convolution uses the trapezoidal integral of field reflectance times response divided by the full response integral, on the union of ASD/SRF knots. Linear interpolation is limited to adjacent finite ASD samples ≤1 nm apart. The response-coverage requirement is 99.9%; no missing/noisy interval may intersect positive response, and no positive response is extrapolated or truncated-renormalized. No independently documented noisy interval was supplied; none is invented or filtered post hoc. All 18 current v4 and 18 separate v5 references have complete response coverage and are exported only as held-reference diagnostics. B08 stays excluded under the accepted insufficient-coverage decision.

### Dependence and weights

The primary graph domain is all six intended targets, both corrections and all three fixed bands before exclusions. The actual union of field/radiometric overlap remains unresolved because representative field-patch and upstream support bounds are unavailable. `connected_components`, final unit IDs and G remain null; singleton units are not fabricated from distinct output cells. Shared QA and overlapping diagnostic windows are typed separately and do not automatically connect radiometric units. No components are split by band, correction or exclusion.

P_b requires valid reference, both methods and common physical/full-support QA. P* intersects the three fixed P_b. All sets are empty, so represented unit counts are zero and statistical weights are null. The unchanged future weights are `1/(G*T_g*3)` on P* and `1/(G_b*T_gb)` within a band; they are separate from numerical cell-extraction weights and QA links. No ASD error metric, pooled score, regression, p-value, confidence interval or correction ranking was calculated.

## Technical evidence and reproducibility appendix

'''
 text+=f"The release contract was frozen at **{c['created_utc']}**, SHA-256 `{m.sha(P/'outputs/ctr34_release_contract.json')}`, in commit `1f14a2d369a62498bd81de6813fe036e1ed49794`. It was also saved as [CTR-34 release-contract](/CTR/issues/CTR-34#document-release-contract), revision `93ceeeeb-41b8-4734-b977-36208ab764ff`, before centre export/convolution. The preinspection rule commit is `8ac444c`; metadata inspection commit is `c937101`. Git and task-document timestamps establish the sequence. No ASD errors were inspected at any stage.\n\n"
 text+='''The task-specific branch `ctr-34-source-matchups` starts at editorial baseline `86e0d6cd6663a80691fd52d050776bf0c790c8bf`. Its scientific-first order and compact CSS are reused in the parent report; the CTR-33 branch and files are unchanged. Its review does not cover this science amendment. The accepted audit is `9f0f06d2b5958b35de82adbca1577e4c384ae846`, author-document revision `7f45ae7b-2969-4c9e-8b83-51250fc21432`, with independent review `19a802d4-b1fa-4e67-b376-570dc689d939`. Thomas's concurrence is `1f9de7bb-a5fb-4c73-ad90-7444529f2189`. Latest PI field clarification is interaction `3c05849a-edf3-4362-a995-4ef2d44fde42`, answered 20 October 2026, 08:50:25.591 UTC; earlier confirmed metadata remain in `provenance/field_evidence.json`.

Every current table/output has the `ctr34_` prefix. Legacy unprefixed files and figures, the earlier CTR-28 report in Git history, and the separate CTR-33 presentation are **historical evidence**, not the current eligible-population report. In particular the old eight-primary/24-candidate counts and all-15 spectra include subsequently excluded mud targets. They are not reused in current scientific summaries. The current totals are six intended primary stations, seven supplementary stations, two PI-excluded stations, 18 intended band candidates, zero included pairs, and 165 retained historical dispositions.

### Deliverable tables and schema

'''
 products=[{'File':'ctr34_candidate_ledger.csv','Contents':'All 165 rows; stable normalized identities; 22 PI mud exclusions, 77 supplementary rows, 48 other-band rows at intended targets, 18 physical holds; included fields empty.'},{'File':'ctr34_eligible_pairs.csv','Contents':'Header-only eligible-pair table; P_b and P* empty.'},{'File':'ctr34_targets.csv / ctr34_references_occasions.json','Contents':'Original IDs, classes, roles, sites, intrinsic footprint versus representativeness, explicit unknown time/repeat/variance fields.'},{'File':'ctr34_support.csv','Contents':'36 stored-cell locators, exact bounds, numerical weight1; upstream support/weights unknown; statistical weights null.'},{'File':'ctr34_qa_cells.csv / ctr34_qa_links.csv / ctr34_common_masks.csv','Contents':'3,740 unique native QA cell/layer IDs; many-to-many matchup links; 18 common held decisions. Witness station/dx/dy in deduplicated QA cells are not exclusive ownership; use links for membership.'},{'File':'ctr34_target_decisions.csv / ctr34_coverage.csv','Contents':'Reason-bearing physical decisions and loss across all six stations, both geographic groups and four literal classes.'},{'File':'ctr34_dependence_edges.csv / ctr34_dependence_graph.json / ctr34_weights.csv','Contents':'Actual graph unresolved; nominal/QA/diagnostic relations separate; frozen formulas, no invented units/weights.'},{'File':'ctr34_held_diagnostics.csv / ctr34_raw_decode.csv','Contents':'18 held reference/correction triples and 36 original one-cell decodes; never included pairs.'},{'File':'ctr34_convolved_references.csv','Contents':'18 v4 held references and 18 separately identified v5 sensitivities; numerator, denominator, coverage, full SRF hashes and column provenance.'},{'File':'ctr34_current_spectra.csv / ctr34_current_spectral_summary.csv','Contents':'13 non-mud station spectra/descriptions; supplementary status retained.'},{'File':'ctr34_sources.json / ctr34_source_identity.csv / ctr34_window_hashes.csv','Contents':'13 raster header/path/stat identities; 198 decoded window hashes; full small-file hashes; no full-raster identity claim.'},{'File':'ctr34_schema.json','Contents':'Keys, null/boolean conventions, identity namespaces, source/scene links, support-versus-QA-versus-statistical-weight semantics.'}]
 text+=mdtable(products,['File','Contents'])
 text+='''### Held numerical diagnostics

These values are supplied-product centre-cell and spectral diagnostics for review only. They are not admitted matchups and cannot support errors, pooled scores or ranking. Table values are rounded to six decimals; CSV retains precision. V5 sensitivity values remain in their separate labeled column/file.

'''
 dr=[]
 for r in m.rows('tables/ctr34_held_diagnostics.csv'):dr.append({'Station':r['station_id'],'Band':r['band_id'],'ASD v4 (held)':f"{float(r['ASD_v4_diagnostic']):.6f}",'L2A (held)':f"{float(r['L2A_diagnostic']):.6f}",'ACOLITE (held)':f"{float(r['ACOLITE_diagnostic']):.6f}"})
 text+=mdtable(dr,['Station','Band','ASD v4 (held)','L2A (held)','ACOLITE (held)'])
 text+='''### Reproduction and checks

Run from the isolated checkout with access to the authorized raw-data paths. The project uses its existing locked Python/numpy environment and installed GDAL C API/CLI; base R generates figures. No dependency or system change was made. The worktree reuses the repository's Python environment; its initial R-library symlink failed the path-containment check and was removed. The canonical project environment passed `scripts/check-env.sh`; static report rendering does not require a second R library. The clean branch passed `pi_guard.py preflight`; `verify-ready` returned ready with unaffected analysis paths. No protected manuscript path was changed.

```bash
# Read the committed contract first; never overwrite a frozen decision.
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr34_validate.py
# Re-run source inspection and post-freeze diagnostics with the same inputs/rules:
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr34_support.py
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr34_extract.py
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr34_validate.py
# Generate figures in local SSD scratch; then publish through figure_io:
Rscript --vanilla analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr34_figures.R analysis/CTR-27_sen2cor-acolite-asd /tmp/ctr34-figures
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr34_publish_figures.py
.venv/bin/python analysis/CTR-27_sen2cor-acolite-asd/scripts/ctr34_report.py
./scripts/render-analysis.sh analysis/CTR-27_sen2cor-acolite-asd
```

`ctr34_freeze.py` creates the initial contract and refuses to overwrite it. It is not part of a routine numerical rerun. The timestamped contract and manual metadata judgments are immutable source inputs for reproduction, not newly recalculated decisions. The separate v5 workbook is an ignored official reference cache, pinned by URL/hash in `provenance/official_sources.json`; it is retained in the artifact bundle and can be copied from the accepted checkout after verifying SHA-256 `42be3ebd8bfcbde11c37caeb2e2fdda65fefa8d2b6f8329559b7806d02cdc9e2`.

'''
 text+=f"**{v['check_count']} technical validation checks passed** at report assembly. They cover all ledger keys/foreign keys, counts, exclusions, support alignment/weight separation, mask layer/detector rules, null grouping, empty paired sets, special-value decode, retained negatives, original-window/centre consistency, analytic convolution fixtures, independent actual-data quadrature, coordinate roundtrip, contract hashes/timing, lockfiles and raw preservation. Check receipts are in `provenance/ctr34_validation.json`; rendering and preservation checks are recorded separately. Repeated computations are used only to verify determinism; timestamps are provenance, not numerical inputs.\n\n"
 text+='''The raw inventory contains 894 path/size/mtime records and is unchanged. Small scientific/reference inputs have full SHA-256 identity. Raster files have header/path/stat evidence and decoded-window hashes only; no 91 GB full-byte hash is claimed. Scientific validation is limited by the physical holds even though numerical checks pass.

### External method context

The [official Sentinel-2 processing documentation](https://sentiwiki.copernicus.eu/web/s2-processing) describes native quality/detector masks and cubic-spline source-geometry interpolation. Those generic descriptions do not recover exact contributors for this supplied product. The [ACOLITE Sentinel-2 source](https://github.com/acolite/acolite/blob/main/acolite/sentinel2/l1_convert.py) provides implementation context; its current version does not identify the exact supplied April 2026 clone. Product-specific statements above come from the supplied headers. Contemporary documentation is contextual, not substituted source provenance.

## Review and approval status

This is Roger's technical submission, with the no-valid-matchup judgments and held numerical exports awaiting Karl Popper's exact-revision independent review, followed by Charles Darwin's reconciliation. The human PI retains scientific authority. Independent review of the assembled investigation and PI scientific approval remain pending. Manuscript integration, protected merge and public publication are not authorized.
'''
 (P/'report.qmd').write_text(text);(P/'report.md').write_text(text.split('---',2)[2].strip()+'\n')
 # Presentation-only reuse of CTR33; never change that branch or report.
 (P/'report.css').write_text((ROOT/'analysis/CTR-33_scientific-first-report/report.css').read_text())
 print('Scientific-first report assembled')
if __name__=='__main__':main()
