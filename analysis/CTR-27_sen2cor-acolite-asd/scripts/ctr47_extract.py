#!/usr/bin/env python3
"""Read-only target-point extraction. Run from root with .venv/bin/python.

Reuse CTR42's GDAL C reader and metadata contract, never its station values.
Writes only ctr47_* technical records in the existing CTR27 investigation.
"""
import collections
import datetime as D
import hashlib
import json
import math
import platform
import struct
import sys
from pathlib import Path

import numpy as np
import ctr42_extract as m

ROOT, P = m.ROOT, m.P
BANDS = m.BANDS
BAD_SCL = {'0', '1', '2', '3', '8', '9', '10', '11'}


def shp_points(path):
    """Read original IEEE doubles; also check record/header lengths and shape type."""
    buf = path.read_bytes()
    assert struct.unpack_from('>i', buf)[0] == 9994
    assert struct.unpack_from('>i', buf, 24)[0] * 2 == len(buf)
    assert struct.unpack_from('<ii', buf, 28) == (1000, 1)
    pos, out = 100, []
    while pos < len(buf):
        number, words = struct.unpack_from('>ii', buf, pos)
        assert words == 10 and number == len(out) + 1
        assert struct.unpack_from('<i', buf, pos + 8)[0] == 1
        x, y = struct.unpack_from('<dd', buf, pos + 12)
        assert math.isfinite(x) and math.isfinite(y)
        out.append((x, y))
        pos += 8 + 2 * words
    assert pos == len(buf)
    return out


def main():
    started = D.datetime.now(D.timezone.utc).isoformat()
    sources, cache, headers, windows = {}, {}, {}, []
    old_sources = {r['path']: r for r in m.rows(P/'tables/ctr42_sources.csv')}

    def track(path, role):
        path = Path(path)
        n = m.rel(path)
        if n not in sources:
            st = path.stat()
            digest = m.sha(path)
            prior = old_sources.get(n)
            if prior:
                assert digest == prior['sha256'], n
            sources[n] = dict(path=n, role=role, bytes=st.st_size,
                              mtime_ns=st.st_mtime_ns, sha256=digest,
                              hash_scope='full_file_SHA256',
                              matches_ctr42_source=prior is not None)
        return path

    def raster(path, role):
        path = track(path, role)
        n = m.rel(path)
        if n not in cache:
            cache[n] = m.Raster(path)
            headers[n] = cache[n].h
        return cache[n]

    def sample(rr, tid, band, method, kind, c, r, nx=1, ny=1, layer=1):
        v = rr.read(c, r, nx, ny, layer)
        windows.append(dict(target_id=tid, band_id=band, correction=method,
                            kind=kind, source_path=m.rel(rr.path), layer=layer,
                            col_start=c, row_start=r, cols=nx, rows=ny,
                            raw_float64_le_sha256=hashlib.sha256(v.tobytes()).hexdigest(),
                            values_json=json.dumps(v.tolist(), allow_nan=True)))
        return v

    shp = ROOT/'data/raw/SHP/POI_S2C_ACOLITE_targets.shp'
    for ext in ['.shp', '.shx', '.dbf', '.prj', '.cpg']:
        track(shp.with_suffix(ext), 'PI target geometry/attribute sidecar')
    geom = shp_points(shp)
    ogr = json.loads(m.run(['ogr2ogr', '-f', 'GeoJSON', '/vsistdout/', str(shp),
                           '-lco', 'COORDINATE_PRECISION=17']))
    assert ogr['crs']['properties']['name'].endswith('32628')
    features = ogr['features']
    assert len(geom) == len(features) and len(set(geom)) == len(geom)
    dbf = shp.with_suffix('.dbf').read_bytes()
    nrec, hlen, rlen = struct.unpack_from('<IHH', dbf, 4)
    assert nrec == len(geom)
    assert all(dbf[hlen+i*rlen:hlen+i*rlen+1] == b' ' for i in range(nrec))
    shx = shp.with_suffix('.shx').read_bytes()
    assert len(shx) == 100 + 8*len(geom)
    assert all(struct.unpack_from('>ii', shx, 100+8*i) == (50+14*i, 10)
               for i in range(len(geom)))
    assert shp.with_suffix('.cpg').read_text().strip().upper() == 'UTF-8'
    targets = []
    for i, (f, xy) in enumerate(zip(features, geom)):
        assert f['geometry']['type'] == 'Point'
        assert tuple(f['geometry']['coordinates']) == xy
        props = f['properties']
        assert set(props) == {'Name', 'Class'}
        assert props['Name'] and props['Class']
        targets.append(dict(target_id=props['Name'], class_literal=props['Class'],
                            display_label=props['Name']+' — '+props['Class'],
                            source_fid_0based=i, source_record_1based=i+1,
                            x_32628_m=xy[0], y_32628_m=xy[1], crs='EPSG:32628',
                            duplicate_coordinate=False,
                            class_status='supplied target label; not independent habitat verification'))
    assert len({s['target_id'] for s in targets}) == len(targets)
    lonlat = m.run(['gdaltransform', '-s_srs', 'EPSG:32628', '-t_srs', 'EPSG:4326'],
                  '\n'.join(f'{x} {y}' for x, y in geom)).splitlines()
    for s, line in zip(targets, lonlat):
        s['longitude'], s['latitude'] = map(float, line.split()[:2])

    # Establish correspondence from all 15 original GPS identities, including mud.
    cross = m.rows(track(P/'tables/station_crosswalk.csv', 'prior identity crosswalk'))
    gps = track(ROOT/cross[0]['gps_path'], 'original GPS; correspondence only')
    cover = track(ROOT/cross[0]['cover_path'], 'original literal station labels; correspondence only')
    gp = m.workbook(gps)['Sheet1']
    gh = gp[0]['cells']
    records = [{gh[k]: v for k, v in r['cells'].items() if k in gh} for r in gp[1:]]
    import csv
    with cover.open() as handle:
        labels = list(csv.DictReader(handle, delimiter='\t'))
    for s in cross:
        raw = m.only(r for r in records if r.get('station') == s['station_id'])
        lab = m.only(r for r in labels if r['station'] == s['station_id'])
        assert float(raw['lon']) == float(s['lon_raw'])
        assert float(raw['lat']) == float(s['lat_raw'])
        assert lab['comment'] == s['target_class_raw']
    transformed = m.run(['gdaltransform', '-s_srs', 'EPSG:4326', '-t_srs', 'EPSG:32628'],
                        '\n'.join(s['lon_raw']+' '+s['lat_raw'] for s in cross)).splitlines()
    station_xy = {s['station_id']: tuple(map(float, l.split()[:2])) for s, l in zip(cross, transformed)}
    correspondence = []
    for t in targets:
        matches = []
        for s in cross:
            x, y = station_xy[s['station_id']]
            dist = math.hypot(t['x_32628_m']-x, t['y_32628_m']-y)
            equivalent = dist <= 1e-8  # numerical transformation tolerance, not a spatial matching radius
            if equivalent:
                matches.append(s['station_id'])
            correspondence.append(dict(target_id=t['target_id'], station_id=s['station_id'],
                                       station_class_literal=s['target_class_raw'],
                                       station_x_32628_m=x, station_y_32628_m=y,
                                       separation_m=dist, exact_geometry_equivalent=equivalent,
                                       original_mud_exclusion=s['station_id'] in m.EXCLUDED,
                                       identity_inferred_from_proximity=False))
        t['exact_prior_station_ids'] = ';'.join(matches) or 'none'
        nearest = min((r for r in correspondence if r['target_id'] == t['target_id']), key=lambda r:r['separation_m'])
        t['nearest_prior_station_id'] = nearest['station_id']
        t['nearest_prior_station_distance_m'] = nearest['separation_m']
        t['retained'] = not bool(set(matches) & set(m.EXCLUDED))
        t['decision_reason'] = 'mapped_original_mud_exclusion' if not t['retained'] else 'requested_distinct_target; no_mapped_original_mud_identity'
    exclusions = []
    for sid, label in m.EXCLUDED.items():
        assert m.only(s for s in cross if s['station_id'] == sid)['target_class_raw'] == label
        mapped = [t['target_id'] for t in targets if sid in t['exact_prior_station_ids'].split(';')]
        nearest = min((r for r in correspondence if r['station_id'] == sid), key=lambda r:r['separation_m'])
        exclusions.append(dict(station_id=sid, class_literal=label,
                               original_exclusion_preserved=True,
                               exact_mapped_target_ids=';'.join(mapped) or 'none',
                               nearest_target_id=nearest['target_id'],
                               nearest_target_distance_m=nearest['separation_m'],
                               decision='exclude_exact_source_identity_only; no_proximity_or_label_substitution'))

    for name in ['scripts/ctr42_extract.py', 'tables/ctr42_band_contract.csv',
                 'tables/ctr42_sources.csv', 'provenance/ctr42_scene_pair.json',
                 'provenance/ctr42_validation.json', 'scripts/ctr47_extract.py']:
        track(P/name, 'reused method/lineage evidence' if 'ctr42' in name else 'current method')
    for name in ['uv.lock', 'renv.lock', 'pyproject.toml']:
        track(ROOT/name, 'unchanged project environment')
    scene = m.js(P/'provenance/ctr42_scene_pair.json')
    contract = m.rows(P/'tables/ctr42_band_contract.csv')
    assert [c['band_id'] for c in contract] == BANDS
    safe = m.only((ROOT/'data/raw/S2').glob('*20260307*.SAFE'))
    gran = m.only(safe.glob('GRANULE/*'))
    prod = track(safe/'MTD_MSIL2A.xml', 'Sen2Cor product metadata')
    tile = track(gran/'MTD_TL.xml', 'Sen2Cor tile metadata')
    pv, tv = m.xmlvalues(prod), m.xmlvalues(tile)
    assert pv['SPACECRAFT_NAME'] == ['Sentinel-2B']
    assert pv['PROCESSING_BASELINE'] == ['05.12']
    assert pv['BOA_QUANTIFICATION_VALUE'] == ['10000']
    assert pv['BOA_ADD_OFFSET'] == ['-1000']*13
    assert dict(zip(pv['SPECIAL_VALUE_TEXT'], pv['SPECIAL_VALUE_INDEX'])) == {'NODATA': '0', 'SATURATED': '65535'}
    assert tv['SENSING_TIME'] == scene['sen2cor_tile']['SENSING_TIME']
    assert tv['L1C_TILE_ID'] == scene['sen2cor_tile']['L1C_TILE_ID']
    scl = raster(m.only(gran.glob('IMG_DATA/R20m/*_SCL_20m.jp2')), 'Sen2Cor operational scene classification')
    qa, satellite, missing = [], [], []
    for bi, c in enumerate(contract):
        b = c['band_id']
        for method, pathkey in [('Sen2Cor', 'sen2cor_path'), ('ACOLITE', 'acolite_path')]:
            rr = raster(ROOT/c[pathkey], method+' reflectance '+b)
            h, band = rr.h, rr.h['bands'][0]
            assert h['geoTransform'][1] == float(c['sen2cor_stored_resolution_m'] if method == 'Sen2Cor' else c['acolite_stored_resolution_m'])
            if method == 'ACOLITE':
                meta = h['metadata']['']
                assert meta['NC_GLOBAL#sensor'] == 'S2B_MSI'
                assert meta['NC_GLOBAL#granule'] == scene['acolite']['granule']
                assert meta['NC_GLOBAL#isodate'] == scene['acolite']['isodate']
                assert band['type'] == 'Float32' and band['unit'] == '1'
                assert band.get('scale', 1) == 1 and band.get('offset', 0) == 0
                assert band['metadata']['']['NETCDF_VARNAME'] == c['acolite_variable']
                assert float(band['metadata']['']['wave_nm']) == float(c['acolite_wavelength_nm'])
            else:
                # SAFE XML declares special DN values even when the JP2 header omits NoData.
                assert band['type'] == 'UInt16' and band.get('noDataValue', 0) == 0
            for t in targets:
                if not t['retained']:
                    continue
                tid = t['target_id']
                col, row = rr.index(t['x_32628_m'], t['y_32628_m'])
                inside = 0 <= col < h['size'][0] and 0 <= row < h['size'][1]
                raw, value, reason = None, None, 'outside_raster_extent'
                if inside:
                    raw = float(sample(rr, tid, b, method, 'radiometry', col, row)[0, 0])
                    nd = band.get('noDataValue')
                    if not math.isfinite(raw):
                        reason = 'nonfinite_or_nodata'
                    elif method == 'Sen2Cor' and raw in [0, 65535]:
                        reason = 'nodata_DN_0' if raw == 0 else 'saturated_DN_65535'
                    elif nd is not None and str(nd).lower() != 'nan' and raw == float(nd):
                        reason = 'declared_nodata'
                    else:
                        value = (raw+float(c['sen2cor_add_offset_DN']))/float(c['sen2cor_quantification']) if method == 'Sen2Cor' else raw
                        reason = 'available_stored_value'
                bounds = rr.bounds(col, row)
                rec = dict(target_id=tid, class_literal=t['class_literal'], band_id=b,
                           band_order_1based=bi+1, wavelength_nm=float(c['acolite_wavelength_nm']),
                           correction=method, scene_pair_id=scene['scene_pair_id'],
                           sensing_time=tv['SENSING_TIME'][0], source_path=m.rel(rr.path),
                           source_sha256=sources[m.rel(rr.path)]['sha256'],
                           x_32628_m=t['x_32628_m'], y_32628_m=t['y_32628_m'],
                           col_0based=col, row_0based=row, inside_raster_extent=inside,
                           stored_resolution_m=h['geoTransform'][1],
                           sensor_native_resolution_m=c['sensor_native_resolution_m'],
                           cell_bounds_EPSG32628_json=json.dumps(bounds),
                           raw_value=raw if raw is not None and math.isfinite(raw) else None,
                           reflectance=value, unit='1', availability_reason=reason,
                           negative_retained=value is not None and value < 0,
                           accuracy_independently_assessed=False)
                satellite.append(rec)
                qfiles = [('SCL', scl.path), ('CLDPRB', gran/'QI_DATA/MSK_CLDPRB_20m.jp2'),
                          ('SNWPRB', gran/'QI_DATA/MSK_SNWPRB_20m.jp2')]
                if method == 'Sen2Cor':
                    qfiles += [(k, gran/'QI_DATA'/f'MSK_{k}_{b}.jp2') for k in ['QUALIT', 'DETFOO']]
                for kind, path in qfiles:
                    q = dict(target_id=tid, band_id=b, correction=method, kind=kind,
                             source_path=m.rel(path), layer=None, col_start=None,
                             row_start=None, cols=0, rows=0, cell_counts_json='{}',
                             status='missing_QA_file')
                    if not path.exists():
                        missing.append(m.rel(path)); qa.append(q); continue
                    qr = raster(path, 'raw operational QA '+kind)
                    eps = 1e-5
                    c0, r0 = qr.index(bounds[0]+eps, bounds[3]-eps)
                    c1, r1 = qr.index(bounds[2]-eps, bounds[1]+eps)
                    nx, ny = c1-c0+1, r1-r0+1
                    q.update(col_start=c0, row_start=r0, cols=nx, rows=ny)
                    if c0 < 0 or r0 < 0 or c1 >= qr.h['size'][0] or r1 >= qr.h['size'][1]:
                        q['status'] = 'QA_extent_incomplete'; qa.append(q); continue
                    for layer in range(1, len(qr.h['bands'])+1):
                        v = sample(qr, tid, b, method, kind, c0, r0, nx, ny, layer)
                        vals, counts = np.unique(v, return_counts=True)
                        qa.append(dict(q, layer=layer,
                                       cell_counts_json=json.dumps({str(int(a)): int(n) for a, n in zip(vals, counts)}, sort_keys=True),
                                       status='raw_codes_over_stored_cell_footprint; not_effective_optical_support'))
                sq = m.only(q for q in qa if q['target_id'] == tid and q['band_id'] == b and q['correction'] == method and q['kind'] == 'SCL')
                codes = json.loads(sq['cell_counts_json'])
                rec['SCL_counts_json'] = sq['cell_counts_json']
                rec['SCL_labels'] = ';'.join(scene['SCL_labels_from_product_XML'][k] for k in sorted(codes, key=int))
                rec['SCL_cloud_shadow_invalid_flag'] = bool(set(codes) & BAD_SCL)
                rec['SCL_complete'] = sq['status'].startswith('raw_codes')
                rec['quality_disposition'] = 'available values retained with operational QA; no accuracy clearance'
    for rr in cache.values():
        rr.close()
    pairs = []
    for t in targets:
        if not t['retained']:
            continue
        for b in BANDS:
            s = m.only(r for r in satellite if (r['target_id'], r['band_id'], r['correction']) == (t['target_id'], b, 'Sen2Cor'))
            a = m.only(r for r in satellite if (r['target_id'], r['band_id'], r['correction']) == (t['target_id'], b, 'ACOLITE'))
            finite = s['reflectance'] is not None and a['reflectance'] is not None
            pairs.append(dict(target_id=t['target_id'], class_literal=t['class_literal'],
                              band_id=b, band_order_1based=s['band_order_1based'],
                              wavelength_nm=s['wavelength_nm'], Sen2Cor=s['reflectance'],
                              ACOLITE=a['reflectance'], finite_pair=finite,
                              Sen2Cor_minus_ACOLITE=s['reflectance']-a['reflectance'] if finite else None,
                              Sen2Cor_status=s['availability_reason'], ACOLITE_status=a['availability_reason'],
                              Sen2Cor_SCL_flag=s['SCL_cloud_shadow_invalid_flag'],
                              ACOLITE_SCL_flag=a['SCL_cloud_shadow_invalid_flag'], unit='1'))
    groups = collections.defaultdict(list)
    for r in satellite:
        groups[r['source_path'], r['col_0based'], r['row_0based']].append(r)
    sharing = [dict(source_path=k[0], col_0based=k[1], row_0based=k[2],
                    band_id=v[0]['band_id'], correction=v[0]['correction'],
                    target_ids=';'.join(r['target_id'] for r in v), n_targets=len(v))
               for k, v in groups.items()]
    for n, rs in [('targets', targets), ('station_correspondence', correspondence),
                  ('exclusion_mapping', exclusions), ('satellite', satellite),
                  ('pairs', pairs), ('qa', qa), ('windows', windows), ('cell_sharing', sharing)]:
        m.table('ctr47_'+n+'.csv', rs)
    for n, r in sources.items():
        st = (ROOT/n).stat()
        assert (st.st_size, st.st_mtime_ns) == (r['bytes'], r['mtime_ns']), n
    m.table('ctr47_sources.csv', list(sources.values()))
    m.dump('outputs/ctr47_raster_headers.json', headers)
    m.dump('provenance/ctr47_geometry.json', dict(
        requested_path='Data/raw/shp/POI_S2C_ACOLITE_targets.shp',
        resolved_case_sensitive_path=m.rel(shp), geometry='Point', crs='EPSG:32628',
        feature_count=len(targets), source_fields=['Name', 'Class'],
        exact_double_check='OGR coordinates equal binary SHP doubles; SHX and DBF record counts agree; no deleted records',
        duplicate_ids=0, duplicate_geometries=0, targets=targets,
        station_equivalence_tolerance_m=1e-8,
        correspondence_rule='numerical coordinate equivalence only; nearest distance is descriptive, never an identity assignment',
        station_values_reused=False, prior_cloud_flags_reused=False))
    m.dump('provenance/ctr47_scene_pair.json', scene)
    summary = dict(started_utc=started, completed_utc=D.datetime.now(D.timezone.utc).isoformat(),
                   target_count=len(targets), retained_target_count=sum(t['retained'] for t in targets),
                   band_order=BANDS, satellite_rows=len(satellite),
                   finite_values=sum(r['reflectance'] is not None for r in satellite),
                   finite_pairs=sum(r['finite_pair'] for r in pairs),
                   negative_values=sum(r['negative_retained'] for r in satellite),
                   operational_SCL_flagged_values=sum(r['SCL_cloud_shadow_invalid_flag'] for r in satellite),
                   operational_SCL_flagged_target_ids=sorted({r['target_id'] for r in satellite if r['SCL_cloud_shadow_invalid_flag']}),
                   missing_QA_files=sorted(set(missing)),
                   missing_ACOLITE_specific_quality_mask='not supplied; exported rhos metadata l2w_mask=False; SCL/CLDPRB/SNWPRB are shared Sen2Cor operational evidence',
                   radiometric_reads=sum(r['kind'] == 'radiometry' for r in windows),
                   max_window_cells=max(r['cols']*r['rows'] for r in windows),
                   shared_stored_cell_groups=sum(len(v)>1 for v in groups.values()),
                   sources_stat_unchanged=True, software=dict(python=sys.version, numpy=np.__version__,
                       GDAL=m.run(['gdalinfo','--version']).strip(), host=platform.node()),
                   extraction='one containing stored cell per target, band and correction; no resampling or averaging',
                   source_hash_scope='streamed full-file SHA256; raster decoding only bounded windows',
                   scientific_limitations=['unequal stored footprints for coarse Sen2Cor bands and ACOLITE 10m exports',
                       'upstream interpolation weights and effective optical supports unverified',
                       'labels are supplied classes, not independent ecological identification',
                       'no independent reflectance accuracy assessment; differences do not establish superiority',
                       'operational cloud masks do not establish cloud-free conditions',
                       'correlated bands and any shared cells are not independent replicates'],
                   field_comparison=False, ASD_integration=False, prior_physical_validation_holds='unchanged; satellite comparison does not release prior holds',
                   environment_changed=False, scientific_approval='none; author QA then Thomas validation required')
    m.dump('provenance/ctr47_extraction.json', summary)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
