#!/usr/bin/env python3
"""Verify the canonical CTR24 inputs; export joins only, never agreement metrics.

Uses immutable author values, full small-source hashes and 36 original raster
centre reads (six cached datasets). All writes stay below CTR24. Does not release
physical validation holds. Run with the existing project Python environment.
"""
import csv
import hashlib
import itertools
import json
import platform
import subprocess
import sys
from pathlib import Path

import numpy as np
import ctr34_support as m

P, ROOT = m.P, m.ROOT
PRIMARY = ['AC01', 'AC02', 'AC05', 'AC06', 'AC07', 'AC08']
BANDS = ['B02', 'B03', 'B04']


def validate():
    checks = []

    def check(name, value):
        if not value:
            raise ValueError(name)
        checks.append(name)

    amendment = P / 'outputs/ctr36_matchup_amendment.json'
    check('amendment exists and fixes six stations and three bands',
          json.loads(amendment.read_text())['primary_stations'] == PRIMARY)
    recovery = json.loads((P / 'provenance/ctr36_recovery_manifest.json').read_text())
    for r in recovery['files']:
        check('recovered bytes: ' + r['destination'], m.sha(ROOT / r['destination']) == r['final_sha256'])
    author = json.loads((P / 'provenance/ctr36_author_preservation.json').read_text())
    check('historical author archive is intact', m.sha(P / author['archive']) == author['sha256'])
    original = json.loads((P / 'provenance/ctr36_original_tracked.json').read_text())
    check('every original tracked file including dictionary, lockfiles and manuscript unchanged',
          all(m.sha(ROOT / name) == digest for name, digest in original.items()))
    check('all original raw path/size/mtime records unchanged',
          m.raw_snapshot() == json.loads((P / 'provenance/ctr36_raw_before.json').read_text()))
    for r in m.rows('tables/ctr34_source_identity.csv'):
        check('full small-source identity: ' + r['path'], m.sha(ROOT / r['path']) == r['sha256'])
    for r in json.loads((P / 'outputs/ctr34_sources.json').read_text()):
        s = (ROOT / r['path']).stat()
        check('raster stat identity: ' + r['path'], s.st_size == r['bytes'] and s.st_mtime_ns == r['mtime_ns'])
    held = m.rows('tables/ctr34_held_diagnostics.csv')
    expected = set(itertools.product(PRIMARY, BANDS))
    key = lambda r: (r['station_id'], r['band_id'])
    check('exact 18 unique held station/band keys', len(held) == 18 and {key(r) for r in held} == expected)
    check('physical holds and false inclusion flags retained',
          all(r['included_pair'] == 'False' and r['status'] == 'HELD_DIAGNOSTIC_ONLY' for r in held))
    check('eligible validation table remains empty', not m.rows('tables/ctr34_eligible_pairs.csv'))
    refs = m.rows('tables/ctr34_convolved_references.csv')
    refmap = {(r['station_id'], r['band_id'], r['SRF_role']): r for r in refs}
    check('36 distinct v4/v5 station-band references', len(refs) == len(refmap) == 36)
    for r in held:
        for role, column in [('v4_primary', 'ASD_v4_diagnostic'), ('v5_sensitivity', 'ASD_v5_sensitivity_diagnostic')]:
            ref = refmap[(*key(r), role)]
            check('reference identity/unit/coverage: ' + ':'.join((*key(r), role)),
                  ref['convolved_reflectance'] == r[column] and ref['unit'] == '1'
                  and ref['reference_spectral_validity'] == 'pass' and float(ref['coverage']) >= .999
                  and ref['matchup_included'] == 'False' and m.sha(ROOT / ref['SRF_file']) == ref['SRF_sha256'])
    support = m.rows('tables/ctr34_support.csv')
    raw = m.rows('tables/ctr34_raw_decode.csv')
    locations = {r['station_id']: r for r in m.rows('tables/ctr34_locations.csv')}
    target = {r['station_id']: r for r in m.rows('tables/ctr34_targets.csv')}
    stations = {r['station_id']: r for r in m.rows('tables/station_crosswalk.csv')}
    check('15 one-to-one station, target and coordinate identities', len(locations) == len(target) == len(stations) == 15)
    bc = {r['band']: r for r in m.rows('tables/band_contract.csv')}
    for band in BANDS:
        check('fixed quantity/decode contract: ' + band,
              bc[band]['platform'] == 'S2B' and bc[band]['acolite_units'] == '1'
              and bc[band]['sen2cor_scale'] == '0.0001' and bc[band]['sen2cor_offset'] == '-0.1')
    check('B08 spectral coverage fails and cannot enter fixed rows', bc['B08']['spectral_coverage_pass_if_nm'] == 'False')
    datasets = {}
    try:
        for r in raw:
            path = r['source_id']
            if path not in datasets:
                datasets[path] = m.Raster(ROOT / path)
            ds = datasets[path]
            col, row = int(r['col_0based']), int(r['row_0based'])
            v = ds.read(col, row)
            digest = hashlib.sha256(v.astype('<f8').tobytes()).hexdigest()
            check('original centre byte hash: ' + r['station_id'] + r['method'] + r['band_id'],
                  digest == r['window_sha256_float64'] and float(v[0, 0]) == float(r['raw_value']))
            decoded = float((m.decode(v) if r['method'] == 'L2A' else v)[0, 0])
            hr = next(x for x in held if key(x) == key(r))
            check('decode and diagnostic equality: ' + r['station_id'] + r['method'] + r['band_id'],
                  np.isfinite(decoded) and decoded == float(r['decoded_reflectance']) == float(hr[r['method'] + '_diagnostic']))
            loc = locations[r['station_id']]
            check('WGS84-derived coordinate locates the stored containing cell: ' + r['station_id'] + r['method'] + r['band_id'],
                  ds.index(float(loc['x_m']), float(loc['y_m'])) == (col, row))
        check('36 native centre reads only; six raster datasets', len(raw) == 36 and len(datasets) == 6)
    finally:
        for ds in datasets.values():
            ds.close()
    for sid, band in expected:
        pair = [r for r in support if r['station_id'] == sid and r['band_id'] == band]
        check('common nominal footprint: ' + sid + band,
              len(pair) == 2 and {r['method'] for r in pair} == {'L2A', 'ACOLITE'}
              and all(pair[0][k] == pair[1][k] for k in ['xmin', 'ymin', 'xmax', 'ymax', 'CRS']))
    qa = m.rows('tables/ctr34_qa_cells.csv')
    links = m.rows('tables/ctr34_qa_links.csv')
    check('saved QA cell identities unique and every link resolves',
          len({r['qa_cell_id'] for r in qa}) == len(qa)
          and all(r['qa_cell_id'] in {q['qa_cell_id'] for q in qa} for r in links))
    check('mud exclusions keep original labels', target['AC03']['class_literal'] == 'mbp_mud'
          and target['AC04']['class_literal'] == 'mpb_mud'
          and all(target[s]['role'] == 'PI_mud_excluded' for s in ['AC03', 'AC04']))
    # Export exact author values after checks; strings avoid rounding or filling missing data.
    inputs = []
    for r in held:
        t, loc = target[r['station_id']], locations[r['station_id']]
        inputs.append(dict(station_id=r['station_id'], band_id=r['band_id'], matchup_id=r['matchup_id'],
                           class_literal=t['class_literal'], geographic_group=t['geographic_group'],
                           ASD_v4=r['ASD_v4_diagnostic'], ASD_v5_sensitivity=r['ASD_v5_sensitivity_diagnostic'],
                           L2A=r['L2A_diagnostic'], ACOLITE=r['ACOLITE_diagnostic'], unit='1',
                           latitude=t['latitude'], longitude=t['longitude'], coordinate_CRS=t['CRS'],
                           support_CRS=loc['CRS'], included_pair='False', status=r['status'],
                           physical_reason=r['physical_reason']))
    m.table('tables/ctr36_station_inputs.csv', inputs)
    inventory = []
    supplementary = []
    for sid, t in target.items():
        if t['role'] == 'PI_mud_excluded':
            continue
        has = sid in PRIMARY
        reason = 'held_containing_cell_values_available' if has else 'no_satellite_match_exported_in_CTR34; supplementary_only_not_substituted'
        inventory.append(dict(station_id=sid, class_literal=t['class_literal'], role=t['role'],
                              ASD_column=t['ASD_column_raw'], latitude=t['latitude'], longitude=t['longitude'],
                              coordinate_CRS=t['CRS'], satellite_bands_available=3 if has else 0,
                              satellite_match_status=reason, continuous_ASD_spectrum_available='True',
                              convolved_ASD_reference_status='v4_primary_and_v5_sensitivity' if has else 'NA_not_in_existing_band_reference_export'))
        if not has:
            for b in BANDS:
                supplementary.append(dict(station_id=sid, band_id=b, class_literal=t['class_literal'],
                                          L2A='NA', ACOLITE='NA', ASD_v4='NA', ASD_v5_sensitivity='NA',
                                          unit='1', reason=reason,
                                          ASD_reference_reason='not_in_existing_band_reference_export; continuous_spectrum_retained'))
    check('all 13 nonmud stations accounted for; seven supplementary and 21 NA rows',
          len(inventory) == 13 and len(supplementary) == 21
          and {r['station_id'] for r in supplementary} == {'D06_' + s for s in 'ABCDEFG'})
    m.table('tables/ctr36_nonmud_station_inventory.csv', inventory)
    m.table('tables/ctr36_supplementary_unmatched.csv', supplementary)
    m.table('tables/ctr36_exclusions.csv', [dict(station_id=sid, class_literal=target[sid]['class_literal'],
              reason='PI_mud_microphytobenthos_excluded', included_pair='False') for sid in ['AC03', 'AC04']])
    check('raw files unchanged after bounded native centre reads',
          m.raw_snapshot() == json.loads((P / 'provenance/ctr36_raw_before.json').read_text()))
    output_names = ['ctr36_station_inputs.csv', 'ctr36_nonmud_station_inventory.csv',
                    'ctr36_supplementary_unmatched.csv', 'ctr36_exclusions.csv']
    m.dump('provenance/ctr36_input_validation.json', dict(
        status='pass', completed_utc=m.now(), checks=checks, check_count=len(checks),
        amendment_sha256=m.sha(amendment), python=sys.version, numpy=np.__version__, host=platform.node(),
        GDAL=subprocess.check_output(['gdalinfo', '--version'], text=True).strip(),
        lockfiles={n: m.sha(ROOT / n) for n in ['uv.lock', 'renv.lock']},
        exported_tables={n: m.sha(P / 'tables' / n) for n in output_names},
        primary_triples=18, primary_v4_references=18, v5_sensitivities=18, eligible_validation_pairs=0,
        no_agreement_metrics_computed=True, raster_reads='36 original containing cells, 6 cached rasters; no scene processing',
        identity_limits='full small-file SHA256; original centre byte hashes plus saved diagnostic-window hashes; raster header/path/stat evidence, no full raster hashing',
        scientific_limits='exploratory input/provenance gate only; physical support, exposure and representativeness holds remain; no scientific approval'))
    print(len(checks), 'input checks passed; 18 held triples; 7 unmatched nonmud stations; zero eligible pairs')


if __name__ == '__main__':
    validate()
