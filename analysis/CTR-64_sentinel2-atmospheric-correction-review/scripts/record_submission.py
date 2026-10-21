"""Explicitly record corrected submission inputs; validation never refreshes them.

The final exact commit is bound outside this record in the delivery receipt.
No root lockfile or protected path is modified.
"""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
if __name__=='__main__':
 source='943ee59d36d3e2b77eda44e8d8d2694658195966'
 files=[p for p in ROOT.rglob('*') if p.is_file() and (p.parent==ROOT and p.name!='report.html' or p.parent==ROOT/'scripts' and p.suffix=='.py' or p.parent==ROOT/'tables' or p==ROOT/'provenance/environment.json')]
 files += [REPO/'literature/references_index.csv',REPO/'literature/literature_review.qmd']
 record={'task':'CTR-64','record_role':'Corrected submission inputs and observed verification environment; historical development record is separate',
 'initial_submitted_revision':source,'initial_submitted_parent':subprocess.check_output(['git','rev-parse',source+'^'],cwd=REPO,text=True).strip(),
 'correction_parent':source,'submission_branch':'ctr-64-review-submission','exact_revision_binding':'Source-file SHA-256 manifest below; final exact commit and rendered-output hashes are in the external delivery receipt',
 'uv_lock_sha256':sha(REPO/'uv.lock'),'renv_lock_sha256':sha(REPO/'renv.lock'),
 'verification_environment':{'python':subprocess.check_output([sys.executable,'--version'],text=True).strip(),'quarto':subprocess.check_output(['quarto','--version'],text=True).strip(),'python_executable':sys.executable,'report_execution':'disabled; no scientific Python/R chunks','environment_scope':'Validation uses Python standard library and local pdftotext/pdfinfo; renderer uses scripts/project-env.sh. No R or atmospheric processor execution.'},
 'commands':['python3 '+str((ROOT/'scripts/validate_review.py').relative_to(REPO)),'scripts/render-analysis.sh '+str(ROOT.relative_to(REPO)),'python3 '+str((ROOT/'scripts/build_review_tables.py').relative_to(REPO))],
 'source_file_sha256':{str(p.relative_to(REPO)):sha(p) for p in sorted(files)}}
 (ROOT/'provenance/submission.json').write_text(json.dumps(record,indent=2)+'\n')
 print('Recorded',len(files),'source hashes; locks',record['uv_lock_sha256'],record['renv_lock_sha256'])
