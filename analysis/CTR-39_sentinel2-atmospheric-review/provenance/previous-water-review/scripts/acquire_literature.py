"""Retrieve public bibliographic records and lawfully hosted full texts; no access bypass."""
import concurrent.futures as cf
import hashlib
import json
import pathlib
import subprocess
import urllib.request
import urllib.parse
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATE = datetime.now(timezone.utc).date().isoformat()
SOURCES = [
 ('Warren2019', '10.1016/j.rse.2019.03.018', 'Assessment', ['https://plymsea.ac.uk/id/eprint/8168/1/1-s2.0-S0034425719301099-main%20%281%29.pdf']),
 ('Pahlevan2021', '10.1016/j.rse.2021.112366', 'ACIXAqua', ['https://ntrs.nasa.gov/api/citations/20210011543/downloads/ACIX-Aqua%20A%20global%20assessment%20of%20atmospheric%20correction%20methods%20for%20Landsat-8.pdf']),
 ('Vanhellemont2019', '10.1016/j.rse.2019.03.010', 'DarkSpectrumFitting', ['https://www.vliz.be/imisdocs/publications/ocrd/343844.pdf']),
 ('DeKeukelaere2018', '10.1080/22797254.2018.1457937', 'iCOR', ['https://www.tandfonline.com/doi/pdf/10.1080/22797254.2018.1457937','https://www.vliz.be/imisdocs/publications/330081.pdf']),
 ('Steinmetz2011', '10.1364/OE.19.009783', 'POLYMER', ['https://opg.optica.org/oe/viewmedia.cfm?uri=oe-19-10-9783&seq=0']),
 ('MainKnorn2017', '10.1117/12.2278218', 'Sen2Cor', ['https://elib.dlr.de/117678/1/1042704_Main-Knorn_et_al.pdf']),
 ('Fan2021', '10.1016/j.rse.2020.112236', 'OCSMART', ['https://pacesat.marinesciences.uconn.edu/wp-content/uploads/sites/3042/2021/01/Fan_Stamnes_2021_OC-SMART.pdf']),
 ('Harmel2018', '10.1016/j.rse.2017.10.022', 'Sunglint', []),
 ('Bui2022', '10.3390/rs14051099', 'FrenchCoastalWaters', ['https://mdpi-res.com/d_attachment/remotesensing/remotesensing-14-01099/article_deploy/remotesensing-14-01099.pdf']),
 ('PereiraSandoval2019', '10.3390/rs11121469', 'SpanishInlandWaters', ['https://mdpi-res.com/d_attachment/remotesensing/remotesensing-11-01469/article_deploy/remotesensing-11-01469.pdf']),
 ('Castagna2025', '10.1364/AO.546766', 'RAdCor', ['https://biblio.ugent.be/publication/01KERP0HTJDXVG85DYJCJJJG6F/file/01KERPNVRRRZQYV2NM8ECT053A.pdf']),
 ('Wu2024', '10.1016/j.rse.2024.114433', 'AdjacencyCorrection', []),
 ('Muller2026', '10.3389/frsen.2026.1710758', 'C2RCC', ['https://www.frontiersin.org/journals/remote-sensing/articles/10.3389/frsen.2026.1710758/pdf']),
 ('Vrdoljak2022', '10.3390/hydrology9120215', 'Bathymetry', ['https://mdpi-res.com/d_attachment/hydrology/hydrology-09-00215/article_deploy/hydrology-09-00215.pdf']),
 ('Gordon1994', '10.1364/AO.33.000443', 'SeaWiFSAtmosphericCorrection', ['https://opg.optica.org/ao/viewmedia.cfm?uri=ao-33-3-443&seq=0']),
 ('Lathif2025', '10.1109/JSTARS.2024.3492322', 'ClearTurbidWaters', []),
]

def get(url):
 req = urllib.request.Request(url, headers={'User-Agent':'CtrlSea-LiteratureReview/1.0 (public scientific literature)'})
 with urllib.request.urlopen(req, timeout=35) as r:
  return r.read(), r.geturl(), r.headers.get('Content-Type','')

def run(source):
 key, doi, short, urls = source
 record = {'key':key, 'doi':doi, 'checked':DATE, 'attempts':[]}
 try:
  raw, _, _ = get('https://api.crossref.org/works/'+urllib.parse.quote(doi,safe=''))
  meta=json.loads(raw)['message']; record['crossref']=meta
 except Exception as e:
  record['metadata_error']=str(e); return record
 try:
  raw, _, _=get('https://api.openalex.org/works/https://doi.org/'+urllib.parse.quote(doi,safe=''))
  oa=json.loads(raw); record['openalex']=oa
  for loc in [oa.get('best_oa_location')] + oa.get('locations',[]):
   if loc and loc.get('is_oa') and loc.get('pdf_url'):
    urls.append(loc['pdf_url'])
 except Exception as e:
  record['oa_error']=str(e)
 for url in dict.fromkeys(urls):
  try:
   data, final, ctype=get(url)
   if not data.startswith(b'%PDF-'):
    record['attempts'].append({'url':url,'result':'not a PDF','content_type':ctype}); continue
   year=str((meta.get('published') or meta['issued'])['date-parts'][0][0])
   name=key.rstrip('0123456789')+'_'+year+'_'+short+'.pdf'
   path=ROOT/'literature/pdfs'/name
   if path.exists() and path.read_bytes()!=data:
    raise RuntimeError('Existing PDF differs: refusing overwrite')
   path.write_bytes(data)
   txt=ROOT/'literature/texts'/(path.stem+'.txt')
   p=subprocess.run(['pdftotext','-layout',str(path),str(txt)],capture_output=True,text=True)
   if p.returncode:
    path.unlink(); raise RuntimeError('PDF parse failed '+p.stderr[:200])
   record.update(pdf_path=str(path.relative_to(ROOT)),text_path=str(txt.relative_to(ROOT)),pdf_url=final,pdf_sha256=hashlib.sha256(data).hexdigest(),pdf_bytes=len(data))
   record['attempts'].append({'url':url,'result':'valid PDF; identity requires manual text check'})
   break
  except Exception as e:
   record['attempts'].append({'url':url,'result':str(e)[:250]})
 return record

if __name__=='__main__':
 # Preserve the curated final manifest, including later discovery and inspection.
 # Use restore_pdfs.py to restore downloaded files from that manifest.
 if (ROOT/'outputs/source_records.json').exists():
  print('Curated source manifest already exists; preserved. Use restore_pdfs.py for PDF restoration.')
  raise SystemExit(0)
 for sub in ['literature/pdfs','literature/texts','outputs']:
  (ROOT/sub).mkdir(parents=True,exist_ok=True)
 with cf.ThreadPoolExecutor(max_workers=5) as pool:
  records=list(pool.map(run,SOURCES))
 (ROOT/'outputs/source_records.json').write_text(json.dumps(records,indent=2,ensure_ascii=False))
 for r in records:
  m=r.get('crossref',{}); print(r['key'],m.get('title'),m.get('published'),r.get('pdf_path','NO PDF'),r.get('metadata_error',''))
