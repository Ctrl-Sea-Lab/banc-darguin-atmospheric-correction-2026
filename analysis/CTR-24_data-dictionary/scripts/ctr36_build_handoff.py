#!/usr/bin/env python3
"""Build the CTR24 engineering handoff amendment from saved checks and inputs."""
import json
from pathlib import Path
import ctr34_support as m

P, ROOT = m.P, m.ROOT


def mdtable(rows, columns):
    def cell(v):
        return str(v).replace('|', '\\|').replace('\n', ' ')
    return '\n'.join(['| ' + ' | '.join(columns) + ' |',
                       '| ' + ' | '.join(['---'] * len(columns)) + ' |'] +
                      ['| ' + ' | '.join(cell(r.get(c, 'NA')) for c in columns) + ' |' for r in rows])


def main():
    validation = json.loads((P / 'provenance/ctr36_input_validation.json').read_text())
    legacy = json.loads((P / 'provenance/ctr36_legacy_validation.json').read_text())
    removal = json.loads((P / 'provenance/ctr36_deletion_receipt.json').read_text())
    archive = json.loads((P / 'provenance/ctr36_author_preservation.json').read_text())
    amendment = P / 'outputs/ctr36_matchup_amendment.json'
    inputs = m.rows('tables/ctr36_station_inputs.csv')
    inventory = m.rows('tables/ctr36_nonmud_station_inventory.csv')
    display = [{**r, **{k:format(float(r[k]), '.8f') for k in ['ASD_v4', 'ASD_v5_sensitivity', 'L2A', 'ACOLITE']}} for r in inputs]
    unmatched = [dict(station_id=r['station_id'], class_literal=r['class_literal'], L2A='NA', ACOLITE='NA',
                      ASD_band_reference='NA (continuous spectrum retained)') for r in inventory if r['satellite_bands_available'] == '0']
    receipt_table = [dict(path=Path(r['path']).name, existed_before='yes', exists_after='no', registered_after='no') for r in removal['before']]
    text = '''---
title: "CTR24 station matchup input handoff"
subtitle: "CTR-36 consolidation amendment under CTR-35"
author: "Alan Turing — Research Software Engineer"
date: 2026-10-20
format:
  html:
    embed-resources: true
    toc: true
    number-sections: false
execute:
  enabled: false
---

The two authorized sibling worktrees have been removed. The canonical station inputs now live in the existing **CTR24** analysis, with **18 held containing-cell triples**, **18 primary v4 ASD band references**, and **18 separately identified v5 sensitivities**. Seven supplementary non-mud stations have no exported satellite matches. The eligible-validation table still has **zero rows**.

This is an engineering handoff for Thomas's subsequent exploratory diagnostics. No satellite–ASD agreement metric was computed in CTR-36. The physical support, exposure and representativeness holds remain in force. These checks establish technical consistency within the stated identity limits; they do not establish correction accuracy or scientific approval.

[Open the unchanged reviewed data dictionary](report.html) · [Editable dictionary source](report.qmd) · [CTR-36 task](/CTR/issues/CTR-36) · [CTR-35 coordination and authorization](/CTR/issues/CTR-35)

## Canonical location and reproduction

```text
/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026/
  analysis/CTR-24_data-dictionary/
Branch: ctr-36-ctr24-consolidation
```

The exact final commit is recorded in the saved Paperclip handoff and draft pull request. These local commands run from the original checkout using its existing locked environment:

```bash
.venv/bin/python analysis/CTR-24_data-dictionary/scripts/ctr34_validate.py
.venv/bin/python analysis/CTR-24_data-dictionary/scripts/ctr36_validate_handoff.py
.venv/bin/python analysis/CTR-24_data-dictionary/scripts/ctr36_build_handoff.py
(cd analysis/CTR-24_data-dictionary && ../../scripts/project-env.sh quarto render matchup-amendment.qmd --to html)
```

The input validator reads six original rasters at the 36 already defined single-cell positions and checks small source files; it does not process whole scenes. It exports joins and missingness tables, never agreement metrics. The adapted original bounded replay script is retained for source reproducibility, but is not needed for this input handoff. The original freeze generator is historical and must not be rerun to redefine decisions.

Use `tables/ctr36_station_inputs.csv` for the convenient joined primary inputs. Its numerical strings equal the held author table exactly. Use `tables/ctr34_convolved_references.csv` for reference identities and separate SRF roles. Keep `tables/ctr34_eligible_pairs.csv` as the distinct empty scientific-validation population.

## Input gate

'''
    text += f"The relocated author validator passed **{legacy['check_count']} checks**. The input handoff validator passed **{validation['check_count']} checks**, including exact source/copy hashes, unique keys, station identity, containing-cell coordinates, common nominal boundaries, reflectance units, decoding, native centre byte hashes, reference provenance, exclusions, missingness inventory, and preservation of original tracked files and raw path/size/mtime records.\n\n"
    text += '''The saved native QA witnesses and links are retained separately. A clear analyst-selected QA neighbourhood is not proof of the unknown full radiometric support. Source identity uses full small-file SHA-256, original centre bytes, saved decoded-window hashes, and raster header/path/stat evidence. Full raster bytes were not hashed. No claim of whole-scene byte identity is made.

All 34 existing repository preservation tests passed. Any guard refusal or simulated GitHub authorization printed in that test log belongs to the test fixtures, not a decision on this delivery.

The project lockfiles are unchanged. Existing software versions and processing parameters are saved in `provenance/ctr36_input_validation.json`, the original author receipts, and the frozen contracts. No random procedure or dependency installation was used.

## Fixed primary inputs

Values below are dimensionless reflectance (unit **1**), rounded for display only. The downloadable CSV retains the original full precision. L2A means the supplied operational L2A product; ACOLITE values are supplied `rhos` values. L2A uses `(DN - 1000) / 10000` after masking special codes 0 and 65535; ACOLITE Float32 values are used directly. Valid negative values are not clipped. Both products use the same station/band rows and the fixed containing cell; neither uses an AOI mean or a nearest CSV cell.

'''
    text += mdtable(display, ['station_id','band_id','class_literal','ASD_v4','ASD_v5_sensitivity','L2A','ACOLITE']) + '\n\n'
    text += '''V4 supplied S2B spectral responses remain primary. V5 is a separate sensitivity and is not substituted into the primary reference. ASD spectra span 400–900 nm; B08 fails the existing spectral-coverage test and remains excluded. The full station crosswalk, source GPS/ASD identities and EPSG:4326 coordinates remain accessible. Containing-cell coordinates and boundaries use EPSG:32628.

The six stations are AC01, AC02, AC05, AC06, AC07 and AC08. The existing CTR34 target metadata records AC01/02 as Iwik using the cited PI testimony, while preserving the obsolete literal location text in the historical crosswalk. No original field record was edited.

## All non-mud stations and explicit missingness

The seven stations below have retained continuous ASD spectra but no satellite-match export or band-integrated reference in the existing CTR34 delivery. Each has three explicit NA rows in `tables/ctr36_supplementary_unmatched.csv`. They are not substituted into the six-station population. `tables/ctr36_nonmud_station_inventory.csv` accounts for all 13 non-mud stations. A zero in its *count of available bands* is an inventory count; missing reflectance values are always NA.

'''
    text += mdtable(unmatched, ['station_id','class_literal','L2A','ACOLITE','ASD_band_reference']) + '\n\n'
    text += '''AC03 **mbp_mud** and AC04 **mpb_mud** are excluded from all new analysis under the PI instruction. Both spellings remain in `tables/ctr36_exclusions.csv` and the full original candidate/exclusion ledger. Their metadata is retained solely to audit exclusion.

## Frozen scope for subsequent numerical work

The saved amendment is `outputs/ctr36_matchup_amendment.json`; it links CTR24, CTR-35 and CTR-36 and was written before downstream comparisons. It preserves the earlier empty scientific-validation table. Thomas must verify the saved input/provenance gate before computing any later station-level descriptive bias (satellite minus ASD), MAE or RMSE across B02/B03/B04 and report the number of finite paired bands. If a quantity, identity, coordinate, decode or unit essential fails, the relevant metric is NA with a reason.

Where these essentials hold but physical representativeness or exposure remains uncertain, subsequent numerical agreement is exploratory. No independent-n interpretation of bands, population inference, p-values, confidence intervals, guessed error bars, correction accuracy claim, superiority claim or method ranking is authorized. Both corrections use identical rows. Any overall summary must explicitly disclose equal station/band weighting and its diagnostic scope. Scientific approval, manuscript integration, merge and public publication remain separate decisions.

## Actual removal and preservation

'''
    text += mdtable(receipt_table, ['path','existed_before','exists_after','registered_after']) + '\n\n'
    text += '''Each exact path was a real directory and a registered worktree, rather than a top-level link. Pre-removal checks confirmed the supplied heads, clean tracked files, unchanged inventories, and no unpreserved source work. `git worktree remove --force <exact-path>` removed the known ignored files and symlink entries. No link target was traversed. The original raw directories and project environment remain present, and all original tracked files plus raw inventory records passed preservation checks afterward.

The local pre-removal process scan found no other visible working process referencing the original or sibling checkouts through cwd, open files or mapped files. Process details for other users and three known session daemons were inaccessible without privileges; this is recorded explicitly, and there is no claim of NAS-wide process surveillance. No privileges or infrastructure settings were changed.

Both original branch refs and their commits remain in the original shared Git repository. No remote branch, PR, repository or task record was deleted. Required scripts, tables and provenance are selectively recovered in CTR24. Original CTR33 and CTR34 report revisions and source changes are preserved byte-for-byte in `outputs/CTR36_author-preservation.zip` with an internal per-file manifest. Only path/import adaptations are active; the exact relocation diff and source/destination hashes are saved. The official v5 cache was copied and hash-verified. Reproducible package and render caches were discarded with the copies.

'''
    text += f"Preservation archive: **{archive['files']} files**, SHA-256 `{archive['sha256']}`.\n\nAmendment SHA-256: `{m.sha(amendment)}`.\n\n"
    text += '''Original author evidence (unreviewed for this new amendment): CTR33 `86e0d6cd6663a80691fd52d050776bf0c790c8bf`; CTR34 `3df21a9ee9bdd37d4b9d6f48d990a1a1837bb35d` (scientific files `92f06560bbb9b227a4db98dd240651a6db849e7d`). Historical review labels and commands in archived author products are preserved as history and do not approve this delivery or authorize recreating sibling worktrees.

## Handoff files and review status

- `tables/ctr36_station_inputs.csv`: 18 exact primary input rows.
- `tables/ctr34_convolved_references.csv`: 18 primary v4 and 18 v5 reference rows with source/SRF identities.
- `tables/ctr36_nonmud_station_inventory.csv`: all 13 non-mud stations.
- `tables/ctr36_supplementary_unmatched.csv`: 21 explicit missing station/band rows.
- `tables/ctr36_exclusions.csv` and `tables/ctr34_candidate_ledger.csv`: excluded labels and historical dispositions.
- `tables/ctr34_raw_decode.csv`, support, locations, QA cells/links, source identity, band contract and reference occasions: technical provenance.
- `provenance/ctr36_recovery_manifest.json`, relocation diff, pre-removal inventory, deletion receipt and validation receipts: preservation and checks.
- `report.qmd` and `report.html`: unchanged dictionary; this editable/rendered amendment accompanies them.

CTR-37 performs the subsequent descriptive numerical work; CTR-38 handles the station figures and final report. Their dependency order serializes changes to the original checkout. The final revision still requires the assigned independent scientific and presentation reviews, followed by Charles's coordination and the PI's exact-revision scientific decision. The author cannot approve this work.
'''
    (P / 'matchup-amendment.qmd').write_text(text)
    (P / 'CTR36_HANDOFF.md').write_text(text.split('---\n', 2)[-1])
    m.dump('provenance/ctr36_report_build.json', dict(status='pass', qmd_sha256=m.sha(P / 'matchup-amendment.qmd'),
           input_gate_sha256=m.sha(P / 'provenance/ctr36_input_validation.json'),
           deletion_receipt_sha256=m.sha(P / 'provenance/ctr36_deletion_receipt.json'),
           scope='deterministic engineering report; no scientific values recomputed'))
    print('Built CTR24 matchup-amendment.qmd and CTR36_HANDOFF.md')


if __name__ == '__main__':
    main()
