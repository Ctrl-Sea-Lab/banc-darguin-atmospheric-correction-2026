#!/usr/bin/env python3
"""Technical consistency checks; these do not constitute independent scientific review."""
from pathlib import Path
import csv,json,hashlib
from collections import Counter
P=Path(__file__).resolve().parents[1]
def read(n):return list(csv.DictReader((P/'tables'/n).open()))
st=read('station_crosswalk.csv');m=read('proposed_matchups.csv');b=read('band_contract.csv');s=read('srf_coverage.csv');v=read('srf_v5_sensitivity.csv');d=read('conditional_spatial_diagnostics.csv')
assert len(st)==15 and len(m)==165 and len(b)==11 and len(s)==len(v)==13
assert len({r['station_id'] for r in st})==15 and len({(r['station_id'],r['band']) for r in m})==165
assert all(r['field_date']=='2026-03-27' and r['gps_date_serial']=='46108' and r['finite_values']=='501' for r in st)
assert next(r for r in st if r['station_id']=='AC03')['target_class_raw']=='mbp_mud'
assert next(r for r in st if r['station_id']=='AC04')['target_class_raw']=='mpb_mud'
assert all(r['field_crs']=='' and r['asd_units']=='' and r['field_time_utc']=='' for r in st)
assert all(r['include_primary']=='False' and r['paired_valid']=='False' for r in m)
assert all(not r[k] for r in m for k in ['asd_band_reflectance','satellite_acolite_reflectance','satellite_sen2cor_reflectance'])
assert {r['band'] for r in b if r['spatial_role']=='primary_candidate_10m'}=={'B02','B03','B04'}
assert next(r for r in s if r['band']=='B08')['coverage_pass_if_nm']=='False'
assert next(r for r in v if r['band']=='B08')['v5_fraction_400_900'] and float(next(r for r in v if r['band']=='B08')['v5_fraction_400_900'])<.999
assert all(r['acolite_inside']==r['sen2cor_inside']=='True' for r in d)
assert next(r for r in d if r['station_id']=='D06_A')['hypothetical_10m_pixel_cluster']==next(r for r in d if r['station_id']=='D06_B')['hypothetical_10m_pixel_cluster']
h=json.loads((P/'outputs/raster_headers.json').read_text());a=next(v for k,v in h.items() if '/ACOLITE/' in k);g=next(v for k,v in h.items() if k.endswith('B04_10m.jp2'))
assert a['metadata']['']['NC_GLOBAL#isodate']=='2026-03-27T11:45:53.975343+00:00'
assert (a['geoTransform'][0]-g['geoTransform'][0])/10==3405
assert (g['geoTransform'][3]-a['geoTransform'][3])/10==9006
assert json.loads((P/'provenance/run.json').read_text())['raw_stat_unchanged']
for name in ['report.html','report.qmd','report.md','task.yml','figures/srf-coverage.png','outputs/data_contract.json']:
 assert (P/name).is_file() and (P/name).stat().st_size>0,name
html=(P/'report.html').read_text();assert 'blocked for scientific extraction' in html and '99.4857969' in html
out={'technical_consistency':'passed','source_integrity':'source stat tuples unchanged; small source hashes recorded; rasters not fully hashed','scientific_validation':'not complete; required field metadata unresolved','independent_review':'pending','PI_scientific_approval':'pending','manifest_rows':len(m),'included_pairs':0,'candidate_primary_max_before_holds':24,'hypothetical_primary_10m_pixels':len({r['hypothetical_10m_pixel_cluster'] for r in d if r['station_id'].startswith('AC')})}
(P/'provenance/validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
