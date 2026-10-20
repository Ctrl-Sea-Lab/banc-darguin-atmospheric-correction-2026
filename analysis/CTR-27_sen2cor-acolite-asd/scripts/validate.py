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
assert all(r['field_crs']=='EPSG:4326' and r['asd_units']=='dimensionless 0-1' and r['field_time_utc']=='' for r in st)
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
out={'technical_consistency':'passed','source_integrity':'source stat tuples unchanged; small source hashes recorded; rasters not fully hashed','scientific_validation':'not complete; field support/overpass/QA unresolved; units and datum confirmed','independent_review':'pending','PI_scientific_approval':'pending','manifest_rows':len(m),'included_pairs':0,'candidate_primary_max_before_holds':24,'hypothetical_primary_10m_pixels':len({r['hypothetical_10m_pixel_cluster'] for r in d if r['station_id'].startswith('AC')})}
# Cross-artifact normalization, provenance and exclusion checks, independent of row order.
n=json.loads((P/'outputs/normalized_design.json').read_text());c=json.loads((P/'outputs/data_contract.json').read_text());g=json.loads((P/'outputs/dependence_graph.json').read_text());a=json.loads((P/'outputs/aoi_intake.json').read_text())
assert n['schema']==c['schema']=='ctrlsea.matchup-feasibility.v2'
keys={'sources':'source_id','targets':'target_id','references':'reference_id','occasions':'occasion_id','scene_pairs':'scene_pair_id','matchups':'matchup_id','qa_cells':'qa_cell_id','spectral_references':'spectral_reference_id'}
lookup={}
for table,key in keys.items():
 lookup[table]={x[key]:x for x in n[table]};assert len(lookup[table])==len(n[table]),table
assert len(n['targets'])==len(n['references'])==len(n['occasions'])==15 and len(n['matchups'])==165
assert len({tuple(x[k] for k in c['normalized_key']) for x in n['matchups']})==165
assert {r['matchup_id'] for r in m}==set(lookup['matchups'])
for x in n['matchups']:
 for field,table in [('target_id','targets'),('reference_id','references'),('occasion_id','occasions'),('scene_pair_id','scene_pairs'),('spectral_reference_id','spectral_references')]:assert x[field] in lookup[table]
 assert all(i in lookup['sources'] for i in x['source_ids'])
 assert x['target_id']==lookup['references'][x['reference_id']]['target_id']==lookup['occasions'][x['occasion_id']]['target_id']
 assert not x['include_primary'] and not x['paired_valid'] and x['statistical_weight'] is None and x['component_id'] is None and x['resampling_unit_id'] is None
 assert x['all_reasons'] and x['primary_reason']==x['all_reasons'][0]
 assert all(x[k] is None for k in ['ASD_reflectance','Sen2Cor_reflectance','ACOLITE_reflectance'])
 assert x['physical_validity']=='unknown' and x['paired_validity']=='not_evaluated'
 if x['band_id']=='B08':assert x['spectral_validity']=='fail'
counts=Counter(x['matchup_id'] for x in n['radiometric_support_candidates']);assert set(counts)==set(lookup['matchups']) and set(counts.values())=={2}
for x in n['radiometric_support_candidates']:
 assert x['source_id'] in lookup['sources'] and not x['actual_primary_contributor']
 assert x['extraction_weight'] is None and x['total_contributor_count'] is None
for x in n['matchup_qa_links']:assert x['matchup_id'] in lookup['matchups'] and x['qa_cell_id'] in lookup['qa_cells']
assert len(n['matchup_qa_links'])==165 and len(n['target_complete_spectrum'])==15
assert all(not x['complete_valid'] for x in n['target_complete_spectrum'])
for x in n['sources']:
 if x.get('sha256'):assert hashlib.sha256((P.parents[1]/x['path']).read_bytes()).hexdigest()==x['sha256'],x['path']
assert a['all_row_checks']['station_containing_cell_matches']==0 and a['all_row_checks']['paired_AOI_pixel_keys']==1463
assert all(x['exact_centre_set_match'] for x in a['polygon_checks'])
assert a['spotchecks']['primary_band_checks']==a['spotchecks']['primary_band_matches']==36
assert a['spotchecks']['B01_20m_followup_matches']==6 and a['spotchecks']['scalar_read_count']==144
assert len(read('aoi_station_join.csv'))==15 and all(x['exact_containing_cell_matches']=='0' for x in read('aoi_station_join.csv'))
graph_hash=g.pop('sha256');assert hashlib.sha256(json.dumps(g,sort_keys=True).encode()).hexdigest()==graph_hash
assert n['analysis_manifest']['graph_sha256']==graph_hash and g['components'] is None
assert all(not e['merge_if_admitted'] for e in g['edges'] if e['type']=='shared_QA_cell')
assert any({e['from_station'],e['to_station']}=={'D06_A','D06_B'} and e['type']=='shared_candidate_native_10m_cell' for e in g['edges'])
assert json.loads((P/'provenance/amendment_run.json').read_text())['raw_stat_unchanged']
assert 'unknown field datum' not in (P/'report.md').read_text()
out.update(normalized_keys_and_foreign_keys='passed',new_input_hashes='verified against current files',AOI_rows_each=1463,station_CSV_cell_matches=0,primary_source_encoding_checks='36/36',AOI_scalar_raster_reads=144,final_independent_units=None,scientific_validation='held: footprint/location/overpass, native QA/support/grouping unresolved; PI units/CRS/field exposure incorporated')
(P/'provenance/validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))

# Expanded report consistency and standalone image checks.
import base64
from html.parser import HTMLParser
class Images(HTMLParser):
 def __init__(self): super().__init__(); self.images=[]
 def handle_starttag(self,tag,attrs):
  if tag=='img': self.images.append(dict(attrs))
im=Images();im.feed(html)
assert len(im.images)==5 and all(x['src'].startswith('data:image/png;base64,') for x in im.images)
expected=[P/'figures/generated'/f'{name}.png' for name in ['field-spectra','station-aoi-map','aoi-correction-comparison','aoi-paired-differences']]+[P/'figures/srf-coverage.png']
assert [hashlib.sha256(base64.b64decode(x['src'].split(',',1)[1])).hexdigest() for x in im.images]==[hashlib.sha256(q.read_bytes()).hexdigest() for q in expected]
assert all(x.get('alt') for x in im.images[:4])
assert len(read('field_spectral_summary.csv'))==15 and len(read('aoi_descriptive.csv'))==12 and len(read('aoi_paired_differences.csv'))==6
assert all(int(r['excluded_pairs'])==0 and int(r['retained_pairs'])==int(r['total_pairs']) for r in read('descriptive_exclusions.csv'))
assert 'not estimable: zero admitted field matchups' in html
exp=json.loads((P/'provenance/descriptive_run.json').read_text()); assert exp['raw_stat_unchanged'] and exp['new_raster_reads']==0
for name,hsh in exp['scripts'].items(): assert hashlib.sha256((P/name).read_bytes()).hexdigest()==hsh
for x in exp['used_input_hashes']: assert hashlib.sha256((P.parents[1]/x['path']).read_bytes()).hexdigest()==x['sha256']
for name,hsh in exp['locks'].items(): assert hashlib.sha256((P.parents[1]/name).read_bytes()).hexdigest()==hsh
checks={'standalone_embedded_images':5,'PNG_contents_match_delivered_files':True,'new_figures_have_alt_text':True,'field_summary_rows':15,'product_summary_rows':12,'paired_difference_rows':6,'cross_language_numeric_check':'R recalculated all 33 rows from source; agrees within 1e-12 during descriptive.py','raw_stat_unchanged':True,'preservation_tests':(P/'provenance/expansion_preservation_tests.txt').read_text().strip(),'field_validation':'not estimable: zero admitted field matchups','review':'independent Karl review pending; PI scientific approval pending'}
(P/'provenance/expansion_validation.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks))
