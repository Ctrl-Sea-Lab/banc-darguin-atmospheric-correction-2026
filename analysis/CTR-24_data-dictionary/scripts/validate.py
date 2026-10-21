#!/usr/bin/env python3
"""Validate metadata coverage, source stat preservation and output schemas only."""
import csv,json,hashlib,importlib.util,sys,zipfile
from collections import Counter
from pathlib import Path
spec=importlib.util.spec_from_file_location('inventory',Path(__file__).with_name('inventory.py'))
i=importlib.util.module_from_spec(spec);spec.loader.exec_module(i)
P=i.OUT
F=list(csv.DictReader((P/'tables/file_inventory.csv').open())); V=list(csv.DictReader((P/'tables/variable_dictionary.csv').open())); A=list(csv.DictReader((P/'tables/archive_inventory.csv').open())); H=json.loads((P/'outputs/headers.json').read_text());S=json.loads((P/'provenance/inventory_run.json').read_text())
checks={};details={}
physical={(f['root']+':'+f['path']):f for f in F}
checks['unique_file_paths']=len(physical)==len(F)
checks['all_variable_sources_in_inventory']=all(v['source'].split('!',1)[0] in physical for v in V)
checks['all_archive_sources_in_inventory']=all(a['source'] in physical for a in A)
checks['all_fields_have_evidence']=all(v['evidence'] and v['units'] and v['storage_type'] and v['nodata'] for v in V)
checks['unique_source_variable_pairs']=len({(v['source'],v['variable']) for v in V})==len(V)
for ext in ['.nc','.tif','.jp2','.shp','.xlsx','.zip']:
 sources=[s for s,f in physical.items() if f['kind']=='file' and Path(f['path']).suffix==ext]
 checks['header_coverage_'+ext]=all(s in H for s in sources)
 details[ext]={'physical_files':len(sources),'captured_headers':sum(s in H for s in sources)}
by_source=Counter(v['source'] for v in V)
checks['netcdf_variable_count_matches_headers']=all(by_source[s]==sum(len(g['variables']) for g in h.values()) for s,h in H.items() if s.endswith('.nc'))
checks['raster_band_count_matches_headers']=all(by_source[s]==len(h['bands']) for s,h in H.items() if s.endswith(('.tif','.jp2')))
checks['shapefile_fields_match_dbf_descriptors']=all(by_source[s]==len(h['fields']) for s,h in H.items() if s.endswith('.shp'))
checks['zip_member_count_matches_central_directory']=all(sum(a['source']==s for a in A)==h['members'] for s,h in H.items() if s.endswith('.zip'))
now=i.scan(); expected=[]
for f in F:
 rec={k:f[k] for k in ['root','path','size_bytes','mtime_ns','mode','uid','gid','kind','target']}
 for key in ['size_bytes','mtime_ns','uid','gid']:rec[key]=int(rec[key])
 expected.append(rec)
checks['source_stat_records_still_unchanged']=expected==now
checks['source_snapshot_fingerprint_matches']=hashlib.sha256(json.dumps(expected,sort_keys=True).encode()).hexdigest()==S['source_snapshot_sha256']
checks['only_documentation_paths_changed']=all(line.startswith('analysis/CTR-24_data-dictionary/') for line in i.run(['git','-C',str(i.ROOT),'ls-files','--others','--exclude-standard']).splitlines()) and all(line.startswith('analysis/CTR-24_data-dictionary/') for line in i.run(['git','-C',str(i.ROOT),'diff','--name-only',S['git_head']]).splitlines())
checks['known_errors_explicitly_recorded']=len(S['errors'])==2 and all(e['source'].endswith('.aux.xml') for e in S['errors'])
checks['no_netCDF_array_read_calls']='.nc_get_var' not in Path(__file__).with_name('inventory.py').read_text().replace('no nc_get_var* calls','')
checks['no_raster_statistic_flags']=not any(x in ['-stats','-hist','-checksum','-mm'] for cmd in S['commands'] for x in cmd)
result={'utc':i.UTC(),'checks':checks,'all_checks_pass':all(checks.values()),'coverage':details,'files':len(F),'variable_rows':len(V),'archive_entries':len(A),'dataset_index_rows':sum(1 for _ in csv.DictReader((P/'tables/dataset_metadata.csv').open())),'metadata_read_gaps':S['errors'],'scope':'documentation consistency and source stat preservation; no scientific validation'}
i.dump(P/'provenance/validation.json',result)
print(json.dumps(result,indent=2))
if not result['all_checks_pass']:sys.exit(1)
