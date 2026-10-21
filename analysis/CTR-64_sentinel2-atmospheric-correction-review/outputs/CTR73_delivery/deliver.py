from pathlib import Path
import os,sys,json,hashlib,subprocess,shutil,time
ROOT=Path('/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026')
OUT=Path('/tmp/ctr73-evidence')
N54='CTR-54_paired-reflectance-differences'; N64='CTR-64_sentinel2-atmospheric-correction-review'
def git(repo,*args):
 return subprocess.check_output(['git','-c','safe.directory='+str(repo),'-c','core.filemode=false','-C',str(repo),*args])
def inventory(path):
 rows=[]
 if not path.exists():return rows
 for f in sorted(path.rglob('*')):
  if f.is_symlink(): raise RuntimeError('Symlink requires explicit resolution: '+str(f))
  if not f.is_file():continue
  h=hashlib.sha256()
  with f.open('rb') as s:
   for b in iter(lambda:s.read(8*1024*1024),b''):h.update(b)
  rows.append({'path':f.relative_to(path).as_posix(),'bytes':f.stat().st_size,'sha256':h.hexdigest()})
 return rows
def save(name,data):
 (OUT/name).write_text(json.dumps(data,indent=2)+'\n')
def source(name,wt,rev):
 repo=ROOT/'.task-worktrees'/wt
 assert git(repo,'rev-parse','HEAD').decode().strip()==rev
 prefix='analysis/'+name+'/'
 blobs={}
 for row in git(repo,'ls-tree','-rz','HEAD','--','analysis/'+name).split(b'\0'):
  if not row:continue
  meta,path=row.split(b'\t',1); mode,kind,oid=meta.split()
  assert kind==b'blob'
  blobs[path.decode()[len(prefix):]]=oid.decode()
 rows=inventory(repo/'analysis'/name)
 for row in rows:
  rel=row['path']; expected=blobs.get(rel)
  row['git_status']='tracked_exact' if expected else 'source_local_evidence'
  if expected:
   d=(repo/'analysis'/name/rel).read_bytes()
   actual=hashlib.sha1(b'blob '+str(len(d)).encode()+b'\0'+d).hexdigest()
   assert actual==expected,(rel,expected,actual)
   row['git_blob']=actual
 assert set(blobs)<=set(x['path'] for x in rows)
 return {'source_revision':rev,'source_worktree':str(repo),'investigation':prefix.rstrip('/'),'files':rows,'file_count':len(rows),'byte_count':sum(x['bytes'] for x in rows)}
def snapshot():
 for name,wt,rev in [(N54,'CTR-58-review','7b9232da45c68c82c5f996b37357f15fb7b9ed55'),(N64,'CTR-64-submission','e1f7b4bc5f81c61bf8eba0f891ba1abc7a949048')]:
  d=source(name,wt,rev);save(name+'-source.json',d);print('Source verified',name,d['file_count'],d['byte_count'],flush=True)
  rows=inventory(ROOT/'analysis'/name);save(name+'-before.json',rows);print('Destination before',name,len(rows),sum(x['bytes'] for x in rows),flush=True)
 save('git-before.json',{'head':git(ROOT,'rev-parse','HEAD').decode().strip(),'branch':git(ROOT,'branch','--show-current').decode().strip(),'status':git(ROOT,'status','--porcelain').decode(),'diff':git(ROOT,'diff','--stat').decode()})
 paths=git(ROOT,'ls-files','-z').decode().split('\0');rows=[]
 for rel in paths:
  if not rel:continue
  p=ROOT/rel
  if p.is_file():rows.append({'path':rel,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 for rel in ['pre-build/.pi-sync/state.json']:
  p=ROOT/rel
  if p.is_file() and rel not in paths:rows.append({'path':rel,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 save('tracked-and-state-before.json',rows);print('Preservation snapshot',len(rows),'files',flush=True)
def deliver64():
 d=json.loads((OUT/(N64+'-source.json')).read_text()); src=Path(d['source_worktree'])/'analysis'/N64;dst=ROOT/'analysis'/N64
 assert not dst.exists(),'Destination appeared; reconcile before copying'
 args=['./scripts/project-env.sh','env','PATH='+str(OUT/'bin')+os.pathsep+os.environ['PATH'],str(ROOT/'.venv/bin/python'),str(ROOT/'scripts/pi_sync.py'),'--repository',str(ROOT),'verify-ready','--task-id','CTR-73','--agent','alan-turing']
 for row in d['files']: args+=['--path','analysis/'+N64+'/'+row['path']]
 env=os.environ.copy(); env['PATH']=str(OUT/'bin')+os.pathsep+env['PATH']
 result=subprocess.run(args,cwd=ROOT,env=env,capture_output=True,text=True);save('ctr64-readiness.json',{'command':args,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr});assert result.returncode==0,result.stdout+result.stderr
 assert json.loads(result.stdout)['result']=='ready'
 assert inventory(src)==[{k:r[k] for k in ['path','bytes','sha256']} for r in d['files']]
 # Destination is absent and every final target has passed readiness. Copy no repository-root files.
 shutil.copytree(src,dst,copy_function=shutil.copy2)
 after=inventory(dst);save(N64+'-after.json',after)
 assert after==[{k:r[k] for k in ['path','bytes','sha256']} for r in d['files']]
 for row in json.loads((OUT/'tracked-and-state-before.json').read_text()):
  p=ROOT/row['path'];assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'], 'Pre-existing tracked/state content changed: '+row['path']
 assert inventory(ROOT/'analysis'/N54)==json.loads((OUT/(N54+'-before.json')).read_text()),'CTR54 changed concurrently'
 save('ctr64-copy-result.json',{'task':'CTR-73','time_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'source_revision':d['source_revision'],'reviewed_scientific_revision':'3138892ee7a40a4b42a0a5696f2623f94845acd7','destination':str(dst),'files_verified':len(after),'bytes_verified':sum(r['bytes'] for r in after),'all_source_files_byte_identical':True,'existing_tracked_and_sync_state_preserved':True,'ctr54_unchanged':True,'scientific_approval':'not_inferred','integration_merge_publication':'not_authorized','root_bibliography':'not_copied_or_modified'})
 print('CTR64 delivered and verified',len(after),sum(r['bytes'] for r in after),flush=True)
if __name__=='__main__':
 {'snapshot':snapshot,'deliver64':deliver64}[sys.argv[1]]()
