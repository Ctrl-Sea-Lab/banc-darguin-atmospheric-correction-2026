from pathlib import Path
import subprocess,json,hashlib,datetime,importlib.util
root=Path('/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026')
out=Path('/tmp/CTR73-final-verification')
evidence=root/'analysis/CTR-64_sentinel2-atmospheric-correction-review/outputs/CTR73_delivery'
g=['git','-c','safe.directory='+str(root),'-C',str(root)]
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
 return {'bytes':p.stat().st_size,'sha256':h.hexdigest()}
def inventory(p): return [{'path':str(f.relative_to(p)),**digest(f)} for f in sorted(p.rglob('*')) if f.is_file()]
status_before=subprocess.check_output(g+['status','--porcelain=v1','-uall'])
result={'task_id':'CTR-73','verified_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'read-only verification of completed CTR63 placement; no science or rendering','head':subprocess.check_output(g+['rev-parse','HEAD'],text=True).strip(),'delivery_owner_record':'CTR63/local-placement-delivery revision 7d83e3f9-467a-44ad-bc67-b7010d04b194','independent_review':'pending CTR-74; this is author verification only','investigations':[]}
for task,dirname,rev,wt in [('CTR54','CTR-54_paired-reflectance-differences','7b9232da45c68c82c5f996b37357f15fb7b9ed55','CTR-58-review'),('CTR64','CTR-64_sentinel2-atmospheric-correction-review','3138892ee7a40a4b42a0a5696f2623f94845acd7','CTR-64-submission')]:
 rel='analysis/'+dirname;dest=root/rel;source=root/'.task-worktrees'/wt/rel
 listing=subprocess.check_output(g+['ls-tree','-r',rev,'--',rel],text=True).splitlines();rows=[]
 for line in listing:
  meta,path=line.split('\t');blob=meta.split()[2];r=str(Path(path).relative_to(rel));gitbytes=subprocess.check_output(g+['cat-file','blob',blob]);expected={'bytes':len(gitbytes),'sha256':hashlib.sha256(gitbytes).hexdigest()}
  rows.append({'path':r,'git_blob':blob,'expected':expected,'source':digest(source/r),'destination':digest(dest/r)})
 assert all(x['expected']==x['source']==x['destination'] for x in rows)
 (out/(task+'-exact-revision.json')).write_text(json.dumps(rows,indent=2))
 after=inventory(dest);(out/(task+'-root-inventory.json')).write_text(json.dumps(after,indent=2))
 historical=json.loads((evidence/(dirname+('-before.json' if task=='CTR54' else '-source.json'))).read_text())
 before=historical if isinstance(historical,list) else historical['files'];a={x['path']:x for x in after};b={x['path']:x for x in before}
 changed=[x for x in b if x in a and any(a[x][k]!=b[x][k] for k in ['bytes','sha256'])];missing=[x for x in b if x not in a];added=[x for x in a if x not in b]
 assert not missing
 if task=='CTR54':
  assert sorted(changed)==['README.md','report.html','report.qmd','task.yml']
  archive='outputs/CTR63_prior_versions/bd77ad26-7e7b-4ef2-a64b-d17d09330874/'
  preserved=[{'original':x,'prior_record':b[x],'archive_path':archive+x,'archive':a[archive+x]} for x in changed]
  assert all(x['prior_record']['sha256']==x['archive']['sha256'] and x['prior_record']['bytes']==x['archive']['bytes'] for x in preserved)
  (out/'CTR54-prior-preservation.json').write_text(json.dumps(preserved,indent=2))
 else: assert not changed
 # Check report resources using the existing parser; do not execute any scientific routines.
 spec=importlib.util.spec_from_file_location('assets',evidence/'check_assets.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 assets=module.check(dest);(out/(task+'-assets.json')).write_text(json.dumps(assets,indent=2));assert not assets['missing'],assets['missing']
 result['investigations'].append({'task':task,'directory':str(dest),'selected_revision':rev,'selected_files':len(rows),'selected_bytes':sum(x['expected']['bytes'] for x in rows),'all_selected_sources_and_destinations_match_git':True,'root_files':len(after),'root_bytes':sum(x['bytes'] for x in after),'historical_files':len(b),'historical_changed':changed,'historical_missing':missing,'historical_added':added,'historical_unchanged':len(b)-len(changed),'report_html':a['report.html'],'report_qmd':a['report.qmd'],'local_assets_missing':assets['missing']})
 print(task,'verified',len(rows),'selected;',len(after),'root files',flush=True)
prior=json.loads((evidence/'tracked-and-state-before.json').read_text());comparison=[{'path':x['path'],'before':x,'now':digest(root/x['path'])} for x in prior]
changed=[x['path'] for x in comparison if any(x['before'][k]!=x['now'][k] for k in ['bytes','sha256'])]
result['historical_tracked_and_state_records']={'records':len(comparison),'changed':changed}
(out/'tracked-and-state-comparison.json').write_text(json.dumps(comparison,indent=2))
assert not changed,changed
result['git_status_records']=len(status_before.splitlines());result['git_status_unchanged_during_verification']=status_before==subprocess.check_output(g+['status','--porcelain=v1','-uall']);assert result['git_status_unchanged_during_verification']
result['limitations']=['No scientific computations, renders, visual review, Git writes, permission changes or project-file mutations in this continuation.','Prior failed cleanliness preflight and permission/registration limitations remain unresolved outside local placement.','Full hashing covers both delivered investigations and the 639 historical tracked/state records, not all original raw datasets or all source worktree files.','Scientific approval, integration, merge and publication are separate; none inferred.']
(out/'delivery-manifest-final.json').write_text(json.dumps(result,indent=2))
print(json.dumps({**result,'investigations':[{k:v for k,v in x.items() if k!='historical_added'} for x in result['investigations']]},indent=2))
