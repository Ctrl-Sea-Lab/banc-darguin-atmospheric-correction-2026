from pathlib import Path
import hashlib,subprocess,json,importlib.util
A=Path(__file__).resolve().parents[1];R=A.parents[1]
def snapshot():
 return {p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in subprocess.check_output(['git','ls-files'],text=True).splitlines() if (R/p).is_file()}
before=snapshot()
subprocess.run(['python3',str(A/'scripts/build_review_tables.py')],check=True)
after=snapshot();assert before==after, [p for p in before if before[p]!=after[p]]
assert (A/'.gitignore').read_bytes()==subprocess.check_output(['git','show','943ee59:'+str((A/'.gitignore').relative_to(R))])
spec=importlib.util.spec_from_file_location('review_validator',A/'scripts/validate_review.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def check(ok,msg):
 if not ok:raise AssertionError(msg)
p=A/'provenance/submission.json';original=p.read_bytes();record=json.loads(original);tests=[]
try:
 for target in ['uv_lock_sha256','source_file_sha256']:
  bad=json.loads(original)
  if target=='uv_lock_sha256':bad[target]='0'*64
  else:bad[target][str((A/'review.md').relative_to(R))]='0'*64
  p.write_text(json.dumps(bad))
  try:m.validate_submission(check)
  except AssertionError as e:tests.append({'case':target,'result':'rejected as required','message':str(e)})
  else:raise AssertionError('Stale record accepted: '+target)
finally:p.write_bytes(original)
m.validate_submission(check)
receipt={'table_rebuild':'all tracked file bytes unchanged','notebook_ignore':'identical to initial submission','stale_provenance_negative_tests':tests,'restored_record_validation':'passed'}
(A/'outputs/focused_verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
