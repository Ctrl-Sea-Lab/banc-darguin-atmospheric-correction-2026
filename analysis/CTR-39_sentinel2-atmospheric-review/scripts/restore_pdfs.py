"""Restore manifest-listed public PDFs without overwriting existing files."""
import hashlib
import json
import pathlib
import subprocess
import urllib.request

ROOT=pathlib.Path(__file__).resolve().parents[1]
records=json.loads((ROOT/'outputs/source_records.json').read_text())
for r in records:
 if not r.get('pdf_path'):continue
 path=ROOT/r['pdf_path'];path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists():
  assert hashlib.sha256(path.read_bytes()).hexdigest()==r['pdf_sha256'],'Existing file differs; preserve and investigate: '+str(path)
 else:
  request=urllib.request.Request(r['pdf_url'],headers={'User-Agent':'CtrlSea-LiteratureReview/1.0'})
  try:
   with urllib.request.urlopen(request,timeout=35) as response:data=response.read()
   assert data.startswith(b'%PDF-'),'Response is not a PDF'
   assert hashlib.sha256(data).hexdigest()==r['pdf_sha256'],'Source changed; identity and version require review'
   with path.open('xb') as f:f.write(data)
  except Exception as e:
   print(r['key'],'UNAVAILABLE',str(e));continue
 text=ROOT/r['text_path'];text.parent.mkdir(parents=True,exist_ok=True)
 if not text.exists():subprocess.run(['pdftotext','-layout',str(path),str(text)],check=True)
 print(r['key'],'verified')
