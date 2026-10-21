from pathlib import Path
import sys,json,hashlib,subprocess,shutil,os,zipfile
sys.path.insert(0,'/tmp/ctr73-evidence')
from check_assets import check
from deliver import ROOT,OUT,N54,N64,git
result=json.loads((OUT/'ctr64-copy-result.json').read_text())
assets=check(ROOT/'analysis'/N64);assert not assets['missing'];(OUT/'ctr64-assets.json').write_text(json.dumps(assets,indent=2)+'\n')
plan=json.loads((OUT/'ctr54-promotion-plan.json').read_text());before=json.loads((OUT/'tracked-and-state-before.json').read_text())
manifest={'task_id':'CTR-73','scope':'delivery correction; no scientific rerun or render','completion':'partial; CTR54 awaiting owner preservation release','ctr64':result,'ctr54':{'source_revision':'7b9232da45c68c82c5f996b37357f15fb7b9ed55','review_revision':'1a7a57ba0b5b36ceaa288d5522eafe74adedd756','source_files':184,'source_bytes':68999663,'destination_files_before_and_after':plan['destination_before_count'],'destination_bytes_before_and_after':plan['destination_before_bytes'],'all_existing_files_byte_identical_after_ctr64_delivery':True,'promotion':'not_started','different_paths':[x for x in plan['files'] if x['action'].startswith('different')],'release_interaction':'74ea77b5-4377-40ce-8172-5850d26ecd5a','blocker_issue':'CTR-63'},'preservation':{'tracked_plus_sync_state_files_verified':len(before),'root_head_before':json.loads((OUT/'git-before.json').read_text())['head'],'root_head_after':git(ROOT,'rev-parse','HEAD').decode().strip(),'root_branch':git(ROOT,'branch','--show-current').decode().strip(),'staging_commit_branch_switch':False,'tracked_content_diff_after':git(ROOT,'diff','--stat').decode(),'root_library_bib_sha256':hashlib.sha256((ROOT/'library.bib').read_bytes()).hexdigest(),'full_raw_dataset_rehash':'not_performed; copy scope confined to the absent CTR64 investigation'},'validation':{'all_197_ctr64_files_verified':True,'all_local_report_assets_resolve':True,'scientific_rerun':False,'quarto_render':False,'protected_paths_modified':False},'approval':{'ctr54_scientific':'authenticated human acceptance verified at interaction 3a4364a2-1650-48f0-ba96-532e7dadad11 for source revision and exact artifacts','ctr64_scientific':'independent review accepted; no PI scientific approval inferred','bibliography':'existing approval separate; protected root bibliography not copied','manuscript_integration_merge_publication':'not_authorized'}}
assert manifest['preservation']['root_head_before']==manifest['preservation']['root_head_after']
(OUT/'delivery-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
files=['delivery-manifest.json','ctr64-copy-result.json','ctr64-assets.json','ctr64-readiness.json','ctr64-readiness-first-attempt.json','ctr54-promotion-plan.json','git-before.json','tracked-and-state-before.json','coordination.json','deliver.py','check_assets.py','finalize64.py','CTR-54-verified-decisions.json','CTR-70-verified-decisions.json',N54+'-source.json',N54+'-before.json',N64+'-source.json',N64+'-before.json',N64+'-after.json']
permanent=ROOT/'analysis'/N64/'outputs/CTR73_delivery'
args=['./scripts/project-env.sh','env','PATH='+str(OUT/'bin')+os.pathsep+os.environ['PATH'],str(ROOT/'.venv/bin/python'),str(ROOT/'scripts/pi_sync.py'),'--repository',str(ROOT),'verify-ready','--task-id','CTR-73','--agent','alan-turing']
for f in files+['evidence-checksums.json','CTR73-delivery-evidence.zip']:args+=['--path',str((permanent/f).relative_to(ROOT))]
r=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);assert r.returncode==0,r.stderr
(OUT/'evidence-readiness.json').write_text(r.stdout);files.append('evidence-readiness.json')
# Verify the readiness log target before writing it too.
r2=subprocess.run(args+['--path',str((permanent/'evidence-readiness.json').relative_to(ROOT))],cwd=ROOT,capture_output=True,text=True);assert r2.returncode==0,r2.stderr
checks={f:{'sha256':hashlib.sha256((OUT/f).read_bytes()).hexdigest(),'bytes':(OUT/f).stat().st_size} for f in files}
(OUT/'evidence-checksums.json').write_text(json.dumps(checks,indent=2)+'\n');files.append('evidence-checksums.json')
with zipfile.ZipFile(OUT/'CTR73-delivery-evidence.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(OUT/f,f)
with zipfile.ZipFile(OUT/'CTR73-delivery-evidence.zip') as z:assert z.testzip() is None
permanent.mkdir(exist_ok=False)
for f in files+['CTR73-delivery-evidence.zip']:
 shutil.copy2(OUT/f,permanent/f);assert (OUT/f).read_bytes()==(permanent/f).read_bytes()
print(json.dumps({'manifest':str(permanent/'delivery-manifest.json'),'bundle':str(permanent/'CTR73-delivery-evidence.zip'),'ctr64_report':str(ROOT/'analysis'/N64/'report.html'),'evidence_files':len(files)+1,'copy_result':result},indent=2))
