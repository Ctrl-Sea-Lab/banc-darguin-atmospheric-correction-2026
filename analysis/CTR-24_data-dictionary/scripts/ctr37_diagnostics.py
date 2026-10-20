#!/usr/bin/env python3
"""Audit frozen exports, then compute exploratory discrepancies; never extract rasters.

Run with the canonical project .venv/bin/python. Only Python standard library is
needed; R independently verifies the outputs. Existing author inputs are read-only.
"""
import csv
import hashlib
import itertools
import json
import math
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

P = Path(__file__).resolve().parents[1]
ROOT = P.parents[1]
STATIONS = ['AC01', 'AC02', 'AC05', 'AC06', 'AC07', 'AC08']
BANDS = ['B02', 'B03', 'B04']
METHODS = ['L2A', 'ACOLITE']
ROLES = {'v4_primary': 'ASD_v4', 'v5_sensitivity': 'ASD_v5_sensitivity'}
LABELS = {'L2A': 'Sen2Cor (operational L2A)', 'ACOLITE': 'ACOLITE DSF'}
STATUS = 'EXPLORATORY_DIAGNOSTIC_PHYSICAL_HOLD'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    with (P / name).open(newline='') as f:
        return list(csv.DictReader(f))


def js(name):
    return json.loads((P / name).read_text())


def dump(name, obj):
    (P / name).write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n')


def table(name, rows, fields=None):
    with (P / 'tables' / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields or list(rows[0]))
        w.writeheader()
        w.writerows({k: 'NA' if v is None else v for k, v in r.items()} for r in rows)


def key(r):
    return r['station_id'], r['band_id']


def finite(v):
    try:
        return math.isfinite(float(v))
    except (TypeError, ValueError):
        return False


def metrics(errors):
    if not errors:
        return None, None, None
    n = len(errors)
    return (math.fsum(errors) / n, math.fsum(map(abs, errors)) / n,
            math.sqrt(math.fsum(e * e for e in errors) / n))


def audit():
    checks = []

    def check(name, ok):
        if not ok:
            dump('provenance/ctr37_input_audit.json', {'status': 'failed', 'failure': name, 'passed': checks})
            raise RuntimeError('Input audit failed: ' + name + '; no new metrics computed')
        checks.append(name)

    c = js('outputs/ctr37_contract.json')
    check('frozen station/band population', c['primary_stations'] == STATIONS and c['bands'] == BANDS)
    for name, digest in c['inputs'].items():
        check('frozen input ' + name, sha(P / name) == digest)
    manifest = js('provenance/ctr36_delivery_manifest.json')
    for name, info in manifest.items():
        check('consolidated evidence bytes ' + name, sha(ROOT / name) == info['sha256'])
    receipt = js('provenance/ctr36_input_validation.json')
    legacy = js('provenance/ctr36_legacy_validation.json')
    check('saved bounded native-cell/coordinate audit passed', receipt['status'] == 'pass' and receipt['check_count'] == 256)
    check('saved independent quadrature/schema audit passed', legacy['status'] == 'pass' and legacy['check_count'] == 128)
    check('environment lock identities', receipt['lockfiles'] == {n: sha(ROOT / n) for n in ['uv.lock', 'renv.lock']})
    for r in read('tables/ctr34_source_identity.csv'):
        check('small source identity ' + r['path'], sha(ROOT / r['path']) == r['sha256'])
    for r in js('outputs/ctr34_sources.json'):
        st = (ROOT / r['path']).stat()
        check('raster path/stat unchanged ' + r['path'], st.st_size == r['bytes'] and st.st_mtime_ns == r['mtime_ns'])
    rows = read('tables/ctr36_station_inputs.csv')
    held = {key(r): r for r in read('tables/ctr34_held_diagnostics.csv')}
    expected = set(itertools.product(STATIONS, BANDS))
    check('18 unique fixed triples', len(rows) == len(held) == 18 and {key(r) for r in rows} == set(held) == expected)
    check('no eligible validation pairs', not read('tables/ctr34_eligible_pairs.csv'))
    target = {r['station_id']: r for r in read('tables/ctr34_targets.csv')}
    locations = {r['station_id']: r for r in read('tables/ctr34_locations.csv')}
    refrows = read('tables/ctr34_convolved_references.csv')
    refs = {(r['station_id'], r['band_id'], r['SRF_role']): r for r in refrows}
    check('unique v4/v5 references', len(refrows) == len(refs) == 36)
    bc = {r['band']: r for r in read('tables/band_contract.csv')}
    design = js('outputs/normalized_design.json')
    scene = design['scene_pairs'][0]
    check('one documented scene pair', len(design['scene_pairs']) == 1 and 'S2B_MSIL2A_20260327T113319_N0512_R080_T28QCH' in scene['operational_L2A'] and '2026_03_27' in scene['ACOLITE'])
    sources = {r['path']: r for r in design['sources']}
    occasions = js('outputs/ctr34_references_occasions.json')
    fieldrefs = {r['target_id']: r for r in occasions['references']}
    ledger = {key(r): r for r in read('tables/ctr34_candidate_ledger.csv')}
    raw = {(r['station_id'], r['band_id'], r['method']): r for r in read('tables/ctr34_raw_decode.csv')}
    check('36 unique saved native-cell decodes', len(raw) == 36)
    for r in rows:
        sid, band = key(r)
        t, loc, h = target[sid], locations[sid], held[key(r)]
        check('hold retained ' + sid + band, r['included_pair'] == 'False' and r['status'] == 'HELD_DIAGNOSTIC_ONLY' and r['physical_reason'] == h['physical_reason'])
        check('identity/coordinate join ' + sid + band, t['crosswalk_cardinality'] == '1:1:1' and float(r['longitude']) == float(loc['lon']) == float(t['longitude']) and float(r['latitude']) == float(loc['lat']) == float(t['latitude']) and r['coordinate_CRS'] == 'EPSG:4326' and loc['CRS'] == 'EPSG:32628' and ledger[key(r)]['scene_pair_id'] == scene['scene_pair_id'])
        fr = fieldrefs[t['target_id']]
        check('documented field quantity/units ' + sid, fr['unit'] == '1' and fr['wavelength_unit'] == 'nm' and fr['conversion'] == 'identity' and fr['source_column'] == t['ASD_column_raw'] and bool(fr['field_units_and_geometry_evidence']))
        check('matching surface quantity contract ' + band, bc[band]['platform'] == 'S2B' and bc[band]['acolite_variable'].startswith('rhos_') and bc[band]['acolite_units'] == '1' and bc[band]['sen2cor_scale'] == '0.0001' and bc[band]['sen2cor_offset'] == '-0.1' and 'surface bidirectional reflectance' in bc[band]['reflectance_definition'])
        for role, column in ROLES.items():
            ref = refs[(sid, band, role)]
            check('reference unit/identity/convolution ' + sid + band + role, ref['convolved_reflectance'] == r[column] and ref['unit'] == r['unit'] == '1' and ref['reference_spectral_validity'] == 'pass' and float(ref['coverage']) >= .999 and ref['ASD_column'] == t['ASD_column_raw'] and abs(float(ref['response_weighted_numerator']) / float(ref['response_denominator']) - float(r[column])) < 1e-14 and sha(ROOT / ref['SRF_file']) == ref['SRF_sha256'] and sha(ROOT / ref['ASD_source']) == ref['ASD_sha256'])
        for method in METHODS:
            d = raw[(sid, band, method)]
            rv = float(d['raw_value'])
            decoded = (rv - 1000) / 10000 if method == 'L2A' else rv
            check('native decode/no missing-code substitution ' + sid + band + method, d['special_value'] == 'False' and d['finite_decoded'] == 'True' and (method != 'L2A' or rv not in [0, 65535]) and math.isfinite(decoded) and abs(decoded - float(r[method])) < 1e-14 and r[method] == h[method + '_diagnostic'] and d['source_id'] == bc[band]['sen2cor_path' if method == 'L2A' else 'acolite_path'])
            src = sources[d['source_id']]
            check('source decoded quantity ' + sid + band + method, src['decoded_unit'] == '1' and 'reflectance' in src['quantity'])
    inv = read('tables/ctr36_nonmud_station_inventory.csv')
    missing = read('tables/ctr36_supplementary_unmatched.csv')
    check('13 nonmud stations and 21 explicit missing supplementary rows', len(inv) == 13 and len(missing) == 21 and {r['station_id'] for r in inv} == set(STATIONS) | {'D06_' + s for s in 'ABCDEFG'} and all(r[k] == 'NA' for r in missing for k in ['L2A', 'ACOLITE', *ROLES.values()]))
    check('literal PI exclusions retained', {r['station_id']: r['class_literal'] for r in read('tables/ctr36_exclusions.csv')} == {'AC03': 'mbp_mud', 'AC04': 'mpb_mud'})
    dump('provenance/ctr37_input_audit.json', {
        'status': 'pass', 'checks': checks, 'check_count': len(checks),
        'completed_utc': datetime.now(timezone.utc).isoformat(),
        'contract_sha256': sha(P / 'outputs/ctr37_contract.json'),
        'input_commit': c['input_commit'], 'inputs': c['inputs'],
        'raster_access': 'stat only; reused hashed centre/coordinate audit, no extraction rerun',
        'quantity_scope': 'dimensionless field reflectance vs surface reflectance products; optical/support equivalence remains held',
        'scene_scope': 'documented S2B 2026-03-27 T28QCH scene; byte-identical upstream L1C ancestry unestablished',
        'approval': 'author input audit, not independent review or physical validation'})
    return rows, missing, refs, inv


def run():
    rows, missing, refs, inventory = audit()  # Persisted pass precedes all numerical comparisons.
    for r in missing:
        r['reason'] += ';ASD:' + r['ASD_reference_reason']
    metrics_rows, long_rows, spectral, coverage = [], [], [], []
    for role, refcolumn in ROLES.items():
        for sid in [r['station_id'] for r in inventory]:
            rr = sorted([r for r in rows + missing if r['station_id'] == sid], key=lambda r: r['band_id'])
            good = [r for r in rr if all(finite(r[k]) for k in [refcolumn, *METHODS])]
            n = len(good)
            completeness = 'complete' if n == 3 else ('partial' if n else 'unavailable')
            reasons = ';'.join(r['band_id'] + ':' + r.get('reason', 'nonfinite_common_triple') for r in rr if r not in good)
            if role == 'v4_primary':
                coverage.append(dict(station_id=sid, class_literal=rr[0]['class_literal'], population='primary' if sid in STATIONS else 'supplementary', n_expected_bands=3, n_common_bands=n, completeness=completeness, missing_band_reasons=reasons or 'none', validation_eligible_pairs=0))
            for method in METHODS:
                err = [float(r[method]) - float(r[refcolumn]) for r in good]
                bias, mae, rmse = metrics(err)
                if n:
                    assert rmse + 1e-14 >= mae >= abs(bias) - 1e-14
                metrics_rows.append(dict(station_id=sid, class_literal=rr[0]['class_literal'], correction=method, correction_label=LABELS[method], SRF_role=role, population='primary' if sid in STATIONS else 'supplementary', completeness=completeness, n_paired_bands=n, bands=';'.join(r['band_id'] for r in good) or 'none', missing_band_reasons=reasons or 'none', bias=bias, MAE=mae, RMSE=rmse, unit='1', within_station_band_weight=1/n if n else None, status=STATUS if n else 'UNAVAILABLE_NOT_SUBSTITUTED', included_validation_pair=False))
                for r in rr:
                    common = r in good
                    ref = float(r[refcolumn]) if finite(r[refcolumn]) else None
                    sat = float(r[method]) if finite(r[method]) else None
                    long_rows.append(dict(station_id=sid, band_id=r['band_id'], class_literal=r['class_literal'], correction=method, correction_label=LABELS[method], SRF_role=role, ASD_reflectance=ref, satellite_reflectance=sat, signed_difference=sat-ref if common else None, common_finite_triple=common, station_completeness=completeness, n_paired_bands=n, unit='1', status=STATUS if common else 'UNAVAILABLE_NOT_SUBSTITUTED', physical_reason=r.get('physical_reason', 'no_existing_match_export'), missing_reason='none' if common else r.get('reason', 'nonfinite_common_triple'), included_validation_pair=False, matchup_id=r.get('matchup_id', 'NA')))
            for r in rr:
                for series, column in [('ASD', refcolumn), *[(m, m) for m in METHODS]]:
                    spectral.append(dict(station_id=sid, band_id=r['band_id'], class_literal=r['class_literal'], SRF_role=role, series=series, reflectance=float(r[column]) if finite(r[column]) else None, unit='1', common_finite_triple=r in good, status=STATUS if r in good else 'UNAVAILABLE_NOT_SUBSTITUTED', physical_reason=r.get('physical_reason', 'no_existing_match_export'), missing_reason='none' if r in good else r.get('reason', 'nonfinite_common_triple'), included_validation_pair=False))
    primary = [r for r in metrics_rows if r['SRF_role'] == 'v4_primary' and r['population'] == 'primary' and r['completeness'] == 'complete']
    table('ctr37_station_metrics.csv', primary, list(metrics_rows[0]))
    table('ctr37_supplementary_metrics.csv', [r for r in metrics_rows if r['SRF_role'] == 'v4_primary' and r not in primary], list(metrics_rows[0]))
    table('ctr37_v5_sensitivity_metrics.csv', [r for r in metrics_rows if r['SRF_role'] == 'v5_sensitivity'], list(metrics_rows[0]))
    table('ctr37_figure_pairs.csv', [r for r in long_rows if r['SRF_role'] == 'v4_primary'])
    table('ctr37_v5_sensitivity_pairs.csv', [r for r in long_rows if r['SRF_role'] == 'v5_sensitivity'])
    table('ctr37_spectral_long.csv', [r for r in spectral if r['SRF_role'] == 'v4_primary'])
    table('ctr37_v5_spectral_long.csv', [r for r in spectral if r['SRF_role'] == 'v5_sensitivity'])
    table('ctr37_station_coverage.csv', coverage)
    differences = []
    for r in rows:
        differences.append(dict(station_id=r['station_id'], band_id=r['band_id'], ASD_v4=float(r['ASD_v4']), ASD_v5=float(r['ASD_v5_sensitivity']), v5_minus_v4=float(r['ASD_v5_sensitivity'])-float(r['ASD_v4']), unit='1', status=STATUS))
    table('ctr37_srf_sensitivity.csv', differences)
    # Unique exported figure keys; NA quantities never use zero placeholders.
    assert len({(r['station_id'], r['band_id'], r['correction'], r['SRF_role']) for r in long_rows}) == len(long_rows)
    assert len(primary) == 12 and all(r['n_paired_bands'] == 3 for r in primary)
    assert all(r['bias'] is None and r['MAE'] is None and r['RMSE'] is None for r in metrics_rows if not r['n_paired_bands'])
    summary = {
        'primary_complete_stations': 6, 'partial_primary_stations': 0,
        'primary_triples': 18, 'primary_correction_rows': 36,
        'unavailable_supplementary_stations': 7, 'eligible_validation_pairs': 0,
        'max_abs_v5_minus_v4_reference': max(abs(r['v5_minus_v4']) for r in differences),
        'unit': '1', 'scope': STATUS,
        'software': {'python': sys.version, 'host': platform.node(), 'packages': 'standard library only'},
        'inputs_sha256': js('outputs/ctr37_contract.json')['inputs'],
        'output_tables_sha256': {f.name: sha(f) for f in sorted((P/'tables').glob('ctr37_*.csv'))},
        'source_sha256': sha(Path(__file__)),
        'input_audit_sha256': sha(P/'provenance/ctr37_input_audit.json'),
        'no_model_fitted': True, 'no_random_sampling': True,
        'review': 'awaiting independent review and PI approval'}
    dump('provenance/ctr37_computation.json', summary)
    print(json.dumps({k: v for k, v in summary.items() if k not in ['software','inputs_sha256','output_tables_sha256']}, indent=2))
    for r in primary:
        print(r['station_id'], r['correction'], r['n_paired_bands'], *(f'{r[k]:.8f}' for k in ['bias','MAE','RMSE']))


if __name__ == '__main__':
    run()
