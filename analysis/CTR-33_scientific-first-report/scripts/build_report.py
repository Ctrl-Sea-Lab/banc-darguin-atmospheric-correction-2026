#!/usr/bin/env python3
"""Presentation only: reorder pinned report blocks without recalculating science.

The CTR-28 generator still owns the original report. It cannot overwrite this
separate CTR-33 report. All scientific scripts and results stay at their source
paths; run this script after the historical workflow to rebuild this presentation.
"""
from pathlib import Path
import csv
import hashlib
import json
import re
import subprocess

P = Path(__file__).resolve().parents[1]
ROOT = P.parents[1]
SOURCE = ROOT / 'analysis/CTR-27_sen2cor-acolite-asd'
BASE = '9f0f06d2b5958b35de82adbca1577e4c384ae846'
SOURCE_PATH = str((SOURCE / 'report.qmd').relative_to(ROOT))
original = (SOURCE / 'report.qmd').read_text()
assert original.encode() == subprocess.check_output(
    ['git', 'show', f'{BASE}:{SOURCE_PATH}'], cwd=ROOT), 'Source changed: reconcile first'
body = original.split('---', 2)[2].strip()
blocks = {}
for match in re.finditer(r'(?m)^(#{1,3}) (.+)\n([\s\S]*?)(?=^#{1,3} |\Z)', body):
    level, heading, content = match.groups()
    assert heading not in blocks
    blocks[heading] = (level, content.strip())

mapping = []
used = set()

def take(heading, destination, level='###'):
    assert heading not in used
    used.add(heading)
    content = blocks[heading][1]
    mapping.append({
        'baseline_heading': heading,
        'destination': destination,
        'body_sha256_before_path_rebase': hashlib.sha256(content.encode()).hexdigest(),
        'operation': 'verbatim body; heading level and relative figure path only; legacy SRF alt text added where applicable',
    })
    content = content.replace('](figures/', '](../CTR-27_sen2cor-acolite-asd/figures/')
    content = content.replace('](../CTR-27_sen2cor-acolite-asd/figures/srf-coverage.png)',
                              '](../CTR-27_sen2cor-acolite-asd/figures/srf-coverage.png)'
                              '{fig-alt="S2B spectral-response coverage for field wavelengths 400–900 nm; '
                              'B08 is below the 99.9% threshold. Coverage does not establish spatial or QA eligibility."}')
    return f'{level} {heading}\n\n{content}\n\n'

summary = '''The supplied March 27 products differ consistently, but their accuracy against field reflectance cannot yet be assessed. Across the retained B02–B04 AOI records, ACOLITE reflectance is lower than operational Level-2A in every saved pair. Mean differences (ACOLITE minus L2A, dimensionless) are −0.11131, −0.10185 and −0.10373 in Arel, and −0.03386, −0.02884 and −0.02804 in Iwik, respectively. The discrepancy is larger in Arel in these supplied records; it does not establish processor superiority or a causal explanation.

The 15 station-average field spectra span 400–900 nm and pooled reflectance 0.02937–0.57363. Eight stations are primary candidates and seven supplementary. The product comparison retains 1,463 paired AOI cells (730 Arel; 733 Iwik), but none contains a field station: zero ASD-validation pairs are admitted. Nearby AOI pixels cannot replace station measurements. Pixel counts and wavelength channels are not independent field replicates; reported SD and quartiles describe spread, not estimation uncertainty.

Field footprints and positional support, the AC01/02 location discrepancy, overpass exposure/timing, QA and independent grouping remain unresolved; B08 remains held. Spectral resemblance does not establish ecological identity. Next steps are to resolve these physical and QA conditions and freeze support/grouping rules before station extraction. The present results support descriptive exploration only. This rewritten report awaits its own editorial/scientific reviews and PI consideration.'''
assert 150 <= len(summary.split()) <= 250

text = '## Scientific summary\n\n' + summary + '\n\n'
text += ('[Findings](#main-scientific-findings) · [Interpretation](#methodological-and-environmental-interpretation) · '
         '[Limitations and next steps](#limitations-and-next-steps) · [Methods](#materials-and-methods) · '
         '[Technical appendix](#technical-methods-quality-assurance-reproducibility-appendix)\n\n')
text += '''## Research question and objectives

Can the supplied 27 March 2026 field spectra be compared fairly with the supplied operational Sentinel-2 Level-2A and ACOLITE surface reflectance? The objectives are to describe the existing field spectra and paired AOI product differences, establish what is comparable, and identify why accuracy against ASD remains not estimable. This editorial revision changes the order and framing of the existing evidence; it releases no scientific hold.

## Main scientific findings

### Observed magnitudes and their scope

In B02, B03 and B04 order, the mean paired differences are **−0.11131, −0.10185, −0.10373 in Arel**, and **−0.03386, −0.02884, −0.02804 in Iwik** (dimensionless reflectance). These are discrepancies between supplied products, without admitted ASD validation. Among the field spectra, AC06 has channel mean **0.42340** and AC05 **0.12420** over 400–900 nm; these describe station-average spectral curves, without repeat-level uncertainty or inferred ecological identity.

'''
for heading in [
    'Paired differences: ACOLITE minus operational L2A',
    'Exploratory paired AOI product comparison',
    'Station-average field spectra',
    'Field locations and actual supplied AOI support',
    'Feasibility counts and denominators',
]:
    text += take(heading, 'Main scientific findings / ' + heading)

text += '''## Methodological and environmental interpretation

The negative product differences and their larger magnitudes in Arel describe these supplied AOIs. They do not identify the more accurate correction, because no physically admitted station matchups exist. Spatial dependence, selected AOIs and unvalidated QA prevent population-level inference. Exposed sediment/moisture, tidal state, adjacency and differences in processing or effective support remain potential confounders. No causal attribution, equivalence test or correction ranking is supported.

The spectral curves document variation in the supplied station averages. Channels are not repeated field measurements, and spectral similarity cannot resolve literal labels such as `mbp_mud` or identify species. The map establishes the support mismatch and preserves the AC01/02 discrepancy; nominal grid agreement does not validate image registration or field footprints.

## Limitations and next steps

**ASD-based bias, MAE, RMSE and R² remain not estimable: zero admitted field matchups.** B08 and material support/location/overpass/QA/grouping holds remain. Nearby pixels, supplementary candidates and diagnostic neighborhoods cannot silently replace the intended primary sample. SD/IQR describe spectral or pixel spread, without inferential uncertainty. The retained next-step record follows unchanged.

'''
text += take('Remaining evidence and questions', 'Limitations and next steps / retained evidence requirements')
text += '''## Materials and Methods

The existing analysis uses 15 supplied March 27 station-average ASD spectra (501 channels at 1 nm spacing over 400–900 nm), their evidenced station/date crosswalk, and paired supplied AOI CSV records for operational Sentinel-2B Level-2A and ACOLITE DSF. Reflectance is dimensionless. The CSVs are already decoded; no second scaling was applied. Pairing uses `(AOI, pixel_id)` at identical nominal 10 m centres. B02–B04 descriptive retention requires both values finite and excludes recognized decoded L2A special codes; zero such exclusions occurred. This rule does not authenticate QA.

Existing summaries use arithmetic means, sample SD and linearly interpolated quartiles (R type 7). No resampling, clipping, convolution, new extraction, correction run or inferential analysis was added. The original methods, source identities, units, CRS, masks, support specifications and complete held extraction–statistics contract are preserved below. Source scripts, tables, figures, outputs and provenance remain under `analysis/CTR-27_sen2cor-acolite-asd/` and are retained byte-for-byte.

## Technical Methods, Quality Assurance & Reproducibility appendix

### Revision and review boundary

This CTR-33 presentation is pinned to source code revision `9f0f06d2b5958b35de82adbca1577e4c384ae846`, associated with CTR-28 author document revision `7f45ae7b-2969-4c9e-8b83-51250fc21432`. It depends on draft PR #3 and targets that source branch in a distinct PR. The older independent-review revision `41b37e06-40fd-471b-b7de-ef3e2d339803` covers amendment `30bf024d129b70191b0ba90193eedc45dfc69b6a`; it does not cover the expanded source or this rewrite.

During this editorial task, Karl accepted the exact expanded source in [CTR-28 independent review](/CTR/issues/CTR-28#document-independent-review), revision `19a802d4-b1fa-4e67-b376-570dc689d939`, without unresolved critical or major findings in its bounded feasibility/descriptive scope. The authenticated [PI comment of 20 October 2026, 08:30:46.535 UTC](/CTR/issues/CTR-28#comment-22aa93c7-ae6a-4bd4-8bb5-970069b954c8) approves that submitted source deliverable; [the decision record](/CTR/issues/CTR-28#document-pi-decision), revision `69563c8a-c599-4898-a7ba-e644c54a4d48`, records its exact-source association and limits. Charles's source coordination stage remains pending. These decisions do not approve this CTR-33 revision, release field-validation holds, or authorize integration, merge or publication.

The source review's two non-blocking editorial points are addressed here: historical pending-status labels are explicitly superseded for the source by the decisions above, and concise alt text is added to the legacy SRF image in this presentation. Image bytes and visible caption are unchanged. All historical records below retain their original tense, paths, commands and status labels for provenance; they are not new execution claims or the current source decision state. No substantive scientific changes were requested by the new source review, and none has been introduced here.

`tables/content_map.csv` maps every original heading/body to this presentation. `tables/claim_evidence.csv` traces the new summary and framing to existing evidence. `provenance/preservation.json` records baseline comparisons and the checks actually performed for this editorial change. Historical numerical checks are retained separately and are not claimed as rerun here. If CTR-28 review changes substantive science or source files, reconcile the exact dependency and recheck affected CTR-33 claims before final review.

### Rebuild this presentation only

From the project root, run:

```bash
python3 analysis/CTR-33_scientific-first-report/scripts/build_report.py
./scripts/render-analysis.sh analysis/CTR-33_scientific-first-report
python3 analysis/CTR-33_scientific-first-report/scripts/verify.py
```

This generator reads saved report text and tables without accessing raw data. It writes only CTR-33 presentation files. The historical generator below continues to own the separate CTR-28 report and cannot overwrite this rewrite. `report.qmd` is editable; rebuilding restores the deterministic presentation, so intentional edits belong in this task's presentation generator as well.

### Retained historical technical and review record

Relative paths in the historical text refer to the original investigation unless a project-root command is shown. Figure paths are rebased for embedding and legacy SRF alt text is added. The following source content otherwise retains its original bodies, with heading levels changed.

'''
for heading in blocks:
    if heading not in used:
        text += take(heading, 'Technical appendix / historical record / ' + heading,
                     level='####' if blocks[heading][0] == '###' else '###')
assert used == set(blocks)

text += '''### CTR-33 review status

This editorial submission awaits Rachel Carson's exact-revision editorial read, Karl Popper's independent evidence-fidelity and reproducibility review, and Charles Darwin's check of both verdicts and PI-review package. The author cannot approve this analysis. PI scientific approval, manuscript integration, merge and public publication remain separate and unauthorized here.
'''
front = '''---
title: "March 27 ASD–Sentinel-2 feasibility and descriptive results"
subtitle: "CTR-33 scientific-first presentation of CTR-28; ASD validation held"
author: "Roger Tomlinson"
format: html
execute:
  enabled: false
---

'''
(P / 'report.qmd').write_text(front + text)
(P / 'report.md').write_text(text)
with (P / 'tables/content_map.csv').open('w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(mapping[0]), lineterminator='\n')
    w.writeheader(); w.writerows(mapping)

claims = [
    ('Arel mean differences B02/B03/B04', '-0.11131; -0.10185; -0.10373', 'tables/aoi_paired_differences.csv', 'AOI=Arel, band=B02/B03/B04, mean', '5-decimal display only; product differences'),
    ('Iwik mean differences B02/B03/B04', '-0.03386; -0.02884; -0.02804', 'tables/aoi_paired_differences.csv', 'AOI=Iwik, band=B02/B03/B04, mean', '5-decimal display only; product differences'),
    ('All saved paired differences negative; larger discrepancy in Arel', 'six negative maxima; Arel mean magnitudes larger', 'tables/aoi_paired_differences.csv', 'all six maximum and mean fields', 'selected AOIs; spatial dependence; no ASD accuracy or causal attribution'),
    ('Field range 400–900 nm; pooled reflectance 0.02937–0.57363', '501 channels; 0.0293690581–0.5736308287 in source narrative', 'report.qmd; tables/field_spectral_summary.csv', 'ASD quantity and sampling limitations; n/minimum/maximum', 'channel spread is not station uncertainty'),
    ('AC06/AC05 spectral channel means', '0.42340; 0.12420', 'tables/field_spectral_summary.csv', 'station_id=AC06/AC05, mean', 'no ecological identity or repeat uncertainty inferred'),
    ('15 spectra; 8 primary; 7 supplementary', '15; 8; 7', 'tables/feasibility_counts.csv; tables/station_crosswalk.csv', 'candidate roles/counts', 'candidates, not admitted validation sample'),
    ('1463 paired cells: 730 Arel/733 Iwik; zero containing-cell joins', '1463; 730; 733; 0', 'tables/feasibility_counts.csv; tables/aoi_station_join.csv', 'paired cells; station containing-cell joins', 'no nearby cell substitution; effective support unverified'),
    ('Zero admitted ASD-validation pairs; accuracy not estimable', '0/165 held design rows', 'tables/proposed_matchups.csv; outputs/normalized_design.json', 'all inclusion flags false; reflectance fields null', 'no bias/MAE/RMSE/R2 or processor ranking'),
    ('Support/location/overpass/QA/grouping and B08 holds persist', 'unchanged source holds', 'outputs/data_contract.json; tables/band_contract.csv; report.qmd', 'contract; spectral coverage; Remaining evidence and questions', 'no release; AC01/02 preserved; grouping unknown'),
    ('No independent replication/uncertainty from pixels or channels', 'SD sample ddof=1; linear/type-7 quantiles', 'provenance/descriptive_run.json; outputs/data_contract.json', 'field_summary; AOI_summary; quantile; grouping rules', 'SD/IQR descriptive; no inference'),
    ('Methods summary: source encoding, identical centres, no exclusions/resampling', 'B02-B04; zero nonfinite/special exclusions', 'provenance/descriptive_run.json; tables/descriptive_exclusions.csv', 'source_encoding; resampling; exclusion and count fields', 'CSV QA lineage unvalidated; no second scaling'),
    ('Environmental confounding and spectral identity limits', 'retained interpretation, no new mechanism attributed', 'report.qmd', 'Paired differences; Spatial and temporal extraction specification; Field evidence', 'observational differences do not establish causation or species'),
    ('Source accepted by Karl and approved by PI; CTR-33 review remains pending', 'source 9f0f06d; review 19a802d4; PI comment 22aa93c7; decision 69563c8a', 'CTR-28 documents, authenticated user comment and execution state', 'recorded in provenance/source_state.json', 'no approval inherited by rewrite; physical holds and separate gates retained'),
]
with (P / 'tables/claim_evidence.csv').open('w', newline='') as f:
    w = csv.writer(f, lineterminator='\n')
    w.writerow(['claim', 'existing_value_or_status', 'source_relative_to_original_investigation', 'selector', 'interpretation_limit'])
    w.writerows(claims)
(P / 'outputs/presentation.json').write_text(json.dumps({
    'baseline_commit': BASE,
    'source_report': SOURCE_PATH,
    'source_qmd_sha256': hashlib.sha256(original.encode()).hexdigest(),
    'summary_word_count': len(summary.split()),
    'source_body_blocks_retained': len(blocks),
    'scientific_outputs_recomputed': False,
    'new_literature': False,
}, indent=2) + '\n')
print(f'Built CTR-33 presentation: {len(blocks)} retained blocks; {len(summary.split())}-word summary')
