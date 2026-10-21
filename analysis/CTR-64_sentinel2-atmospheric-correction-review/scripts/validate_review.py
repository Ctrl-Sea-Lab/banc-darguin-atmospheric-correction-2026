"""Audit reference/file identity, numerical traceability and standalone report.

This is author verification, not independent scientific review. Reproduction
of source-hash checks requires the local source cache, not distributed full text.
"""
from pathlib import Path
import csv,hashlib,json,re,subprocess,sys,unicodedata

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
def norm(s):return ''.join(c for c in unicodedata.normalize('NFKD',s.lower()) if c.isalnum())
def check(ok,msg):
 if not ok:raise AssertionError(msg)
 checks.append(msg)

def validate_submission(check_fn):
 record=json.loads((ROOT/'provenance/submission.json').read_text())
 for field,path in [('uv_lock_sha256','uv.lock'),('renv_lock_sha256','renv.lock')]:
  check_fn(hashlib.sha256((REPO/path).read_bytes()).hexdigest()==record[field], 'Submitted lockfile hash matches: '+path)
 for rel,sha in record['source_file_sha256'].items():
  check_fn(hashlib.sha256((REPO/rel).read_bytes()).hexdigest()==sha, 'Submission provenance source hash matches: '+rel)
 source=record['initial_submitted_revision']
 parent=subprocess.check_output(['git','rev-parse',source+'^'],cwd=REPO,text=True).strip()
 check_fn(parent==record['initial_submitted_parent'], 'Initial submitted parent matches Git history')
 check_fn(subprocess.run(['git','merge-base','--is-ancestor',source,'HEAD'],cwd=REPO).returncode==0, 'Initial reviewed revision is an ancestor of this checkout')
 check_fn(subprocess.check_output([sys.executable,'--version'],text=True).strip()==record['verification_environment']['python'], 'Validation Python version matches submission record')
 check_fn(subprocess.check_output(['quarto','--version'],text=True).strip()==record['verification_environment']['quarto'], 'Render Quarto version matches submission record')

if __name__=='__main__':
 checks=[];pdfchecks=[]
 validate_submission(check)
 refs=list(csv.DictReader((ROOT/'tables/references_index.csv').open()))
 keys=[r['citation_key']for r in refs];dois=[r['doi'].lower()for r in refs]
 check(len(keys)==len(set(keys)),'Unique citation keys')
 check(len(dois)==len(set(dois)),'Unique scholarly DOIs')
 bib=(ROOT/'library_additions.bib').read_text();body=(ROOT/'review.md').read_text()
 cited=set(re.findall(r'@([A-Za-z][A-Za-z0-9]+)',body))
 check(cited<=set(keys),'Every report citation resolves in supplied bibliography')
 check(all('@article{'+k+','in bib for k in keys),'Every reference-index entry has BibTeX entry')
 for r in refs:
  if not r['pdf_path']:continue
  p=REPO/r['pdf_path'];check(p.exists(),'PDF path exists: '+p.name)
  check(p.read_bytes().startswith(b'%PDF-'),'PDF signature: '+p.name)
  t=subprocess.check_output(['pdftotext',str(p),'-'],text=True)
  # Both persistent ID and substantial title match; hyphenation can vary.
  idok=norm(r['doi'])in norm(t)
  words=[norm(x)for x in r['title'].split() if len(norm(x))>4]
  identity=sum(w in norm(t[:12000]) for w in words)/max(len(words),1)
  check(idok and identity>=0.8,'PDF publication identity: '+r['citation_key'])
  pdfchecks.append({'citation_key':r['citation_key'],'filename':p.name,'doi_found':idok,'title_word_fraction':identity,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'pdfinfo':subprocess.check_output(['pdfinfo',str(p)],text=True).splitlines()[:4]})
 logs=[]
 for logfile in sorted((ROOT/'outputs').glob('retrieval*.json')):logs+=json.loads(logfile.read_text())
 missing=[];hashed=0
 for r in logs:
  if 'path'not in r:continue
  p=ROOT/r['path']
  if not p.exists():missing.append(str(p));continue
  check(hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'],'Source hash matches '+r['id']);hashed+=1
 # Trace the few historical numerical claims to inspected sources.
 s=(ROOT/'outputs/sources/Warren2019MSI_pdf.txt').read_text()
 check('521'in s and bool(re.search(r'24\s*h',s)),'Warren matchup count and inland window trace to full text')
 s=(ROOT/'outputs/sources/Doxani2023ACIXLand_pdf.txt').read_text()
 check('79 and 62'in s,'ACIX Land site counts trace to full text')
 check('4 GB'in (ROOT/'outputs/sources/sen2cor_manual.txt').read_text(),'Sen2Cor published memory guideline traced')
 for name in ['method_matrix','local_requirements','candidate_decision','output_definitions','claim_evidence','access_gaps','search_log','software_snapshots']:
  check((ROOT/'tables'/f'{name}.csv').exists()and(ROOT/'tables'/f'{name}.md').exists(),'Machine/human readable table: '+name)
 check((ROOT/'report.html').exists(),'Standalone HTML exists')
 html=(ROOT/'report.html').read_text()
 check('Executive summary'in html and 'C2RCC'in html,'HTML contains intended review')
 check('citation not found'not in html.lower()and'{{< include'not in html,'No unresolved citation/include markers in HTML')
 check(not missing,'All locally logged source files retained')
 # A protected-file diff is not authorized by this task.
 changed=subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=REPO,text=True).splitlines()
 check(not any(p in ['index.qmd','library.bib','_quarto.yml']or p.startswith(('pre-build/','manuscript/','docs/','.pi-preservation/','R/','python/','figures/'))for p in changed),'No protected tracked file modified')
 out={'author_validation':'passed','independent_review':'initial submission minor revision; focused reconsideration pending','pi_approval':'pending','checks_passed':len(checks),'references':len(refs),'full_text_pdfs':len(pdfchecks),'source_hashes':hashed,'checks':checks,'pdf_identity':pdfchecks}
 (ROOT/'outputs/validation.json').write_text(json.dumps(out,indent=2))
 print(json.dumps({k:v for k,v in out.items()if k not in ['checks','pdf_identity']},indent=2))
