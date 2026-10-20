"""CTR-64: retrieve public literature metadata and documentation, never imagery.

Run from any directory with Python's standard library. Failures are retained.
PDFs remain local, outside Git, and are not included in public transfer bundles.
"""
from pathlib import Path
import concurrent.futures as cf
import csv, hashlib, json, subprocess, urllib.request, urllib.parse, datetime

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / 'outputs/sources'
PDFS = ROOT / 'literature/pdfs'
SOURCES.mkdir(parents=True, exist_ok=True)
PDFS.mkdir(parents=True, exist_ok=True)
TODAY = '2026-10-20'
PAPERS = {
 'Pahlevan2021ACIXAqua':'10.1016/j.rse.2021.112366',
 'Doxani2023ACIXLand':'10.1016/j.rse.2022.113412',
 'Warren2019MSI':'10.1016/j.rse.2019.03.018',
 'Vanhellemont2019DSF':'10.1016/j.rse.2019.03.010',
 'Steinmetz2011Polymer':'10.1364/OE.19.009783',
 'DeKeukelaere2018iCOR':'10.1080/22797254.2018.1457937',
 'Yin2022SIAC':'10.5194/gmd-15-7933-2022',
 'Castagna2025RAdCor':'10.1364/AO.546766',
 'Muller2026C2RCC':'10.3389/frsen.2026.1710758',
 'Renosh2020Estuaries':'10.3390/rs12081285',
 'Hagolle2015MAJA':'10.3390/rs70302668',
 'Tavora2023Recipes':'10.34133/remotesensing.0049',
}
URLS = {
 'sen2cor_release':'https://step.esa.int/main/snap-supported-plugins/sen2cor/sen2cor-v2-13/',
 'sen2cor_manual':'https://step.esa.int/thirdparties/sen2cor/2.13.0/docs/OMPC.TPZ.SUM.004%20-%20i1r0%20-%20Sen2Cor%202.13.02%20Configuration%20and%20User%20Manual.pdf',
 'sen2cor_atbd':'https://step.esa.int/thirdparties/sen2cor/2.10.0/docs/S2-PDGS-MPC-L2A-ATBD-V2.10.0.pdf',
 'acolite_readme':'https://raw.githubusercontent.com/acolite/acolite/main/README.md',
 'acolite_license':'https://raw.githubusercontent.com/acolite/acolite/main/LICENCE.txt',
 'acolite_defaults':'https://raw.githubusercontent.com/acolite/acolite/main/config/defaults.txt',
 'acolite_releases':'https://api.github.com/repos/acolite/acolite/releases/latest',
 'acolite_commit':'https://api.github.com/repos/acolite/acolite/commits/main',
 'acolite_manual':'https://raw.githubusercontent.com/acolite/acolite_manual/main/acolite_manual.pdf',
 'polymer_readme':'https://raw.githubusercontent.com/hygeos/polymer/master/README.md',
 'polymer_license':'https://raw.githubusercontent.com/hygeos/polymer/master/LICENCE.TXT',
 'polymer_changelog':'https://raw.githubusercontent.com/hygeos/polymer/master/CHANGELOG.TXT',
 'polymer_commit':'https://api.github.com/repos/hygeos/polymer/commits/master',
 'polymer_ancillary':'https://raw.githubusercontent.com/hygeos/polymer/master/polymer/ancillary.py',
 'polymer_msi':'https://raw.githubusercontent.com/hygeos/polymer/master/polymer/level1_msi.py',
 'maja_home':'https://www.cesbio.cnrs.fr/maja/',
 'maja_start':'https://www.cesbio.cnrs.fr/maja/running-maja-with-start_maja/',
 'maja_install':'https://www.cesbio.cnrs.fr/maja/installing-maja/',
 'maja_output':'https://www.cesbio.cnrs.fr/maja/maja-output-format/',
 'maja_old_license':'https://raw.githubusercontent.com/CNES/MAJA/master/LICENSE',
 'c2rcc_spec':'https://step.esa.int/main/wp-content/help/versions/10.0.0/snap-toolboxes/eu.esa.opt.opttbx.c2rcc/c2rcc/C2RCCAlgorithmSpecification.html',
 'c2rcc_nets':'https://c2rcc.org/neural-nets/',
 'c2rcc_pom':'https://raw.githubusercontent.com/senbox-org/s3tbx/master/s3tbx-c2rcc/pom.xml',
 'c2rcc_source':'https://raw.githubusercontent.com/senbox-org/s3tbx/master/s3tbx-c2rcc/src/main/java/org/esa/s3tbx/c2rcc/msi/C2rccMsiOp.java',
 'c2rcc_commit':'https://api.github.com/repos/senbox-org/s3tbx/commits/master',
 'icor_home':'https://remotesensing.vito.be/services/icor',
 'icor_access':'https://remotesensing.vito.be/icor-download',
 'siac_readme':'https://raw.githubusercontent.com/MarcYin/SIAC/master/README.md',
 'siac_license':'https://raw.githubusercontent.com/MarcYin/SIAC/master/LICENSE.md',
 'siac_commit':'https://api.github.com/repos/MarcYin/SIAC/commits/master',
 'siac_setup':'https://raw.githubusercontent.com/MarcYin/SIAC/master/setup.py',
 'ocsmart_access':'https://www.rtatmocn.com/oc-smart/',
 'Pahlevan2021ACIXAqua_pdf':'https://ntrs.nasa.gov/api/citations/20210011543/downloads/ACIX-Aqua%20A%20global%20assessment%20of%20atmospheric%20correction%20methods%20for%20Landsat-8.pdf',
 'Doxani2023ACIXLand_pdf':'https://elib.dlr.de/196023/1/Doxani2023_1-s2.0-S0034425722005181-main.pdf',
 'Warren2019MSI_pdf':'https://plymsea.ac.uk/id/eprint/8168/1/1-s2.0-S0034425719301099-main%20%281%29.pdf',
 'Yin2022SIAC_pdf':'https://gmd.copernicus.org/articles/15/7933/2022/gmd-15-7933-2022.pdf',
 'Castagna2025RAdCor_pdf':'https://backoffice.biblio.ugent.be/download/01KERP0HTJDXVG85DYJCJJJG6F/01KERPNVRRRZQYV2NM8ECT053A',
 'Muller2026C2RCC_pdf':'https://public-pages-files-2025.frontiersin.org/journals/remote-sensing/articles/10.3389/frsen.2026.1710758/pdf',
 'Renosh2020Estuaries_html':'https://www.mdpi.com/2072-4292/12/8/1285',
 'Hagolle2015MAJA_html':'https://www.mdpi.com/2072-4292/7/3/2668',
 'Tavora2023Recipes_pdf':'https://patrickgray.me/files/2023_tavora_journalremotesensing.pdf',
 'Fan2021OCSMART_pdf':'https://pacesat.marinesciences.uconn.edu/wp-content/uploads/sites/3042/2021/01/Fan_Stamnes_2021_OC-SMART.pdf',
}
def get(item):
 name,url=item
 record={'id':name,'url':url,'checked':TODAY}
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'CtrlSea-LiteratureReview/1.0 (academic metadata and public documentation)'})
  with urllib.request.urlopen(req,timeout=35) as r:
   data=r.read();record.update(status=r.status,final_url=r.url,content_type=r.headers.get('Content-Type',''))
  ispdf=data.startswith(b'%PDF-')
  ext='.pdf' if ispdf else '.json' if 'json' in record['content_type'] else '.txt'
  path=(PDFS if ispdf else SOURCES)/(name+ext)
  if path.exists() and path.read_bytes()!=data:
   raise RuntimeError('Existing source differs; preserve it and retrieve in a fresh review directory: '+path.name)
  if not path.exists():path.write_bytes(data)
  record.update(path=str(path.relative_to(ROOT)),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),valid_pdf=ispdf)
  if ispdf:
   subprocess.run(['pdftotext','-layout',str(path),str(SOURCES/(name+'.txt'))],check=True)
 except Exception as e:record['error']=str(e)
 return record

if __name__=='__main__':
 jobs=dict(URLS)
 for key,doi in PAPERS.items():
  jobs[key+'_crossref']='https://api.crossref.org/works/'+urllib.parse.quote(doi,safe='')
  jobs[key+'_openalex']='https://api.openalex.org/works/https://doi.org/'+doi
 # Bounded discovery queries are stored as full API responses, not just selected hits.
 for service,base in [('crossref','https://api.crossref.org/works?rows=10&query='),('openalex','https://api.openalex.org/works?per-page=10&search=')]:
  jobs[service+'_search']=base+urllib.parse.quote('Sentinel-2 atmospheric correction coastal intertidal adjacency mineral dust')
 jobs['semanticscholar_search']='https://api.semanticscholar.org/graph/v1/paper/search?limit=5&query=Sentinel-2%20atmospheric%20correction%20intertidal'
 with cf.ThreadPoolExecutor(max_workers=8) as pool:results=list(pool.map(get,jobs.items()))
 (ROOT/'outputs/retrieval_log.json').write_text(json.dumps(results,indent=2))
 print(json.dumps({'retrieved':sum('path'in x for x in results),'failed':[{k:x[k] for k in ['id','error']} for x in results if 'error'in x]},indent=2))
