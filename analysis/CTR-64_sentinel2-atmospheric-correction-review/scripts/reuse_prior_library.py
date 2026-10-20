"""Reuse CTR-39's project-local evidence after verifying its recorded hashes.

The source project path is an argument so the review remains portable. Original
PDFs are read only. Fresh Crossref checks are saved with the reused PDF records.
"""
from pathlib import Path
import csv,hashlib,json,shutil,subprocess,sys
from acquire_evidence import ROOT,SOURCES,PDFS,get

KEYS={'Zoffoli2020','Daggers2020','Jacobs2021','Granadeiro2021','Thuy2022','Colin2023'}
if __name__=='__main__':
 original=Path(sys.argv[1]).resolve()
 prior=original/'analysis/CTR-39_sentinel2-atmospheric-review'
 rows=list(csv.DictReader((prior/'literature/references_index.csv').open()))
 records=[]
 for r in rows:
  if r['citation_key']not in KEYS:continue
  k=r['citation_key'];src=prior/r['pdf_file_path'];data=src.read_bytes()
  digest=hashlib.sha256(data).hexdigest()
  if digest!=r['pdf_sha256']:raise RuntimeError('Prior-library hash mismatch '+k)
  dest=PDFS/(k+'_pdf.pdf')
  if dest.exists()and dest.read_bytes()!=data:raise RuntimeError('Destination collision '+k)
  if not dest.exists():shutil.copy2(src,dest)
  subprocess.run(['pdftotext','-layout',str(dest),str(SOURCES/(k+'_pdf.txt'))],check=True)
  records.append({'id':k+'_pdf','url':r['pdf_retrieval_url'],'checked':'2026-10-20','path':str(dest.relative_to(ROOT)),'sha256':digest,'bytes':len(data),'valid_pdf':True,'retrieval_method':'reused project-local PDF; hash matched prior index','prior_source_path':str(src),'prior_verification':r['verification_date']})
  records.append(get((k+'_crossref','https://api.crossref.org/works/'+r['doi_or_identifier'])))
 (ROOT/'outputs/retrieval_reuse.json').write_text(json.dumps(records,indent=2))
 (ROOT/'outputs/prior_citation_keys.json').write_text(json.dumps({r['doi_or_identifier'].lower():r['citation_key']for r in rows},indent=2))
 print('Reused and reverified',len(KEYS),'project sources')
