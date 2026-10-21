#!/usr/bin/env python3
"""Author QA via separate GDAL CLI point reads; no scientific approval."""
import collections
import hashlib
import itertools
import json
import math
import subprocess

import numpy as np
import ctr42_extract as m

ROOT, P = m.ROOT, m.P


def main():
    checks = []
    def check(name, condition):
        if not condition:
            m.dump('provenance/ctr47_validation.json', dict(status='failed', failure=name, passed_checks=checks))
            raise AssertionError(name)
        checks.append(name)
    def read(name):
        return m.rows(P/'tables'/('ctr47_'+name+'.csv'))
    targets, sat, pairs, qa, windows, sources, correspondence, exclusions, sharing = [
        read(n) for n in ['targets', 'satellite', 'pairs', 'qa', 'windows', 'sources',
                         'station_correspondence', 'exclusion_mapping', 'cell_sharing']]
    tids = {r['target_id'] for r in targets}
    bands = ['B01','B02','B03','B04','B05','B06','B07','B08','B8A']
    expected = set(itertools.product(tids, bands, ['Sen2Cor','ACOLITE']))
    check('six distinct requested targets T1 through T6', len(targets) == 6 and tids == {'T'+str(i) for i in range(1,7)})
    check('unique native point coordinates', len({(r['x_32628_m'], r['y_32628_m']) for r in targets}) == 6)
    check('all six targets retained without reusing old station IDs', all(r['retained']=='True' and r['exact_prior_station_ids']=='none' for r in targets))
    shape = ROOT/'data/raw/SHP/POI_S2C_ACOLITE_targets.shp'
    ogr = json.loads(m.run(['ogr2ogr','-f','GeoJSON','/vsistdout/',str(shape),'-lco','COORDINATE_PRECISION=17']))
    check('OGR independently confirms six Point features and EPSG32628', len(ogr['features']) == 6 and ogr['crs']['properties']['name'].endswith('32628') and all(f['geometry']['type']=='Point' for f in ogr['features']))
    for r, f in zip(targets, ogr['features']):
        check('exact OGR coordinate and attribute correspondence '+r['target_id'],
              [float(r['x_32628_m']),float(r['y_32628_m'])] == f['geometry']['coordinates'] and
              r['target_id'] == f['properties']['Name'] and r['class_literal'] == f['properties']['Class'])
    check('all 90 original-station/target distances accounted for', len(correspondence)==90 and len({(r['target_id'],r['station_id']) for r in correspondence})==90)
    for r in correspondence:
        t = m.only(t for t in targets if t['target_id']==r['target_id'])
        d = math.hypot(float(t['x_32628_m'])-float(r['station_x_32628_m']),float(t['y_32628_m'])-float(r['station_y_32628_m']))
        check('correspondence distance arithmetic '+r['target_id']+r['station_id'], d==float(r['separation_m']) and (d<=1e-8)==(r['exact_geometry_equivalent']=='True'))
    check('no requested point is an original station; no proximity identity assigned', all(r['exact_geometry_equivalent']=='False' and r['identity_inferred_from_proximity']=='False' for r in correspondence))
    check('original AC03 mbp_mud and AC04 mpb_mud exclusions preserved without guessed mapping', {r['station_id']:r['class_literal'] for r in exclusions}==m.EXCLUDED and all(r['original_exclusion_preserved']=='True' and r['exact_mapped_target_ids']=='none' for r in exclusions))
    check('108 unique satellite rows cover 6 targets x 9 bands x 2 corrections', len(sat)==108 and {(r['target_id'],r['band_id'],r['correction']) for r in sat}==expected)
    check('54 pair rows use exactly the same point-band identities', len(pairs)==54 and {(r['target_id'],r['band_id']) for r in pairs}==set(itertools.product(tids,bands)))
    for source in sources:
        path=ROOT/source['path']
        check('input source SHA256 unchanged '+source['path'], m.sha(path)==source['sha256'])
        check('input source size and modification time unchanged '+source['path'], path.stat().st_size==int(source['bytes']) and path.stat().st_mtime_ns==int(source['mtime_ns']))
    check('all five target sidecars hashed', {str(shape.with_suffix(e).relative_to(ROOT)) for e in ['.shp','.shx','.dbf','.prj','.cpg']} <= {r['path'] for r in sources})
    srcmap={r['path']:r for r in sources}
    for r in sat:
        key=r['target_id']+r['band_id']+r['correction']
        x,y=float(r['x_32628_m']),float(r['y_32628_m'])
        x0,y0,x1,y1=json.loads(r['cell_bounds_EPSG32628_json'])
        check('coordinate inside stored footprint '+key, x0<=x<x1 and y0<y<=y1 and x1-x0==y1-y0==float(r['stored_resolution_m']))
        # GDAL CLI independently finds the cell from native coordinates, not saved indices.
        raw=float(m.run(['gdallocationinfo','-valonly','-geoloc',str(ROOT/r['source_path']),str(x),str(y)]).strip())
        check('separate CLI raw point read '+key, abs(raw-float(r['raw_value']))<1e-12)
        value=(raw-1000.)/10000. if r['correction']=='Sen2Cor' else raw
        check('separate unit/offset decode '+key, abs(value-float(r['reflectance']))<1e-12 and r['unit']=='1')
        check('no missing or invalid source substitution '+key, r['availability_reason']=='available_stored_value' and math.isfinite(value) and (r['correction']!='Sen2Cor' or raw not in [0,65535]))
        check('negative value retained without clipping '+key, (value<0)==(r['negative_retained']=='True'))
        check('exact source and band order '+key, r['source_sha256']==srcmap[r['source_path']]['sha256'] and int(r['band_order_1based'])==bands.index(r['band_id'])+1)
        check('no independent accuracy claim '+key, r['accuracy_independently_assessed']=='False')
    satmap={(r['target_id'],r['band_id'],r['correction']):r for r in sat}
    for p in pairs:
        key=p['target_id'],p['band_id']
        s,a=(satmap[(*key,c)] for c in ['Sen2Cor','ACOLITE'])
        check('paired signed difference and shared finite mask '+' '.join(key), p['finite_pair']=='True' and float(p['Sen2Cor'])==float(s['reflectance']) and float(p['ACOLITE'])==float(a['reflectance']) and float(p['Sen2Cor_minus_ACOLITE'])==float(s['reflectance'])-float(a['reflectance']))
    wmap={}
    for w in windows:
        v=np.asarray(json.loads(w['values_json']),dtype='<f8')
        check('bounded window shape/hash '+str(len(wmap)), v.shape==(int(w['rows']),int(w['cols'])) and hashlib.sha256(v.tobytes()).hexdigest()==w['raw_float64_le_sha256'] and v.size<=9)
        wmap[(w['target_id'],w['band_id'],w['correction'],w['kind'],w['layer'])]=w
    check('all 108 radiometry windows contain exactly one cell', sum(w['kind']=='radiometry' for w in windows)==108 and all(w['rows']==w['cols']=='1' for w in windows if w['kind']=='radiometry'))
    unique_scl={}
    for q in qa:
        check('QA file and full stored footprint available '+q['target_id']+q['band_id']+q['correction']+q['kind']+q['layer'], q['status'].startswith('raw_codes'))
        w=wmap[(q['target_id'],q['band_id'],q['correction'],q['kind'],q['layer'])]
        counts=dict(collections.Counter(str(int(x)) for row in json.loads(w['values_json']) for x in row))
        check('QA counts equal saved window '+str(len(checks)), counts==json.loads(q['cell_counts_json']))
        if q['kind']=='SCL':
            r=satmap[(q['target_id'],q['band_id'],q['correction'])]
            check('point-specific SCL flag is derived from actual footprint '+str(len(checks)), r['SCL_counts_json']==q['cell_counts_json'] and (bool(set(counts)&{'0','1','2','3','8','9','10','11'}))==(r['SCL_cloud_shadow_invalid_flag']=='True') and r['SCL_complete']=='True')
            unique_scl[q['source_path'],q['col_start'],q['row_start'],q['cols'],q['rows']]=q
    for (path,c,r,nx,ny),q in unique_scl.items():
        vals=[]
        for row in range(int(r),int(r)+int(ny)):
            for col in range(int(c),int(c)+int(nx)):
                vals.append(str(int(float(m.run(['gdallocationinfo','-valonly',str(ROOT/path),str(col),str(row)]).strip()))))
        check('CLI re-read of unique operational SCL footprint '+str((c,r,nx,ny)), dict(collections.Counter(vals))==json.loads(q['cell_counts_json']))
    check('cell sharing explicitly audited; none among these targets', len(sharing)==108 and all(r['n_targets']=='1' for r in sharing))
    roundtrip=m.run(['gdaltransform','-s_srs','EPSG:4326','-t_srs','EPSG:32628'], '\n'.join(t['longitude']+' '+t['latitude'] for t in targets)).splitlines()
    check('longitude latitude axis order roundtrip within 1e-7m', all(math.hypot(float(l.split()[0])-float(t['x_32628_m']),float(l.split()[1])-float(t['y_32628_m']))<1e-7 for t,l in zip(targets,roundtrip)))
    before=m.js(P/'provenance/ctr47_preflight.json')
    for group in ['prior_tracked_sha256','unrelated_ctr39_sha256']:
        for n,h in before[group].items():
            check('preserved baseline '+n,m.sha(ROOT/n)==h)
    check('no tracked baseline file modified',subprocess.check_output(['git','diff','HEAD','--name-only'],cwd=ROOT,text=True).strip()=='')
    summary=dict(status='pass',check_count=len(checks),checks=checks,
                 independent_GDAL_CLI_radiometric_reads=108,
                 independent_SCL_footprints=len(unique_scl),
                 finite_pairs=54,negative_values=sum(r['negative_retained']=='True' for r in sat),
                 SCL_flagged_target_ids=sorted({r['target_id'] for r in sat if r['SCL_cloud_shadow_invalid_flag']=='True'}),
                 baseline_and_unrelated_files_preserved=True,
                 scientific_review='author QA only; Thomas independent numerical validation and subsequent review still required',
                 script_sha256=m.sha(__file__),
                 output_sha256={str(p.relative_to(P)):m.sha(p) for p in sorted((P/'tables').glob('ctr47_*.csv'))})
    m.dump('provenance/ctr47_validation.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k not in ['checks','output_sha256']},indent=2))


if __name__=='__main__':
    main()
