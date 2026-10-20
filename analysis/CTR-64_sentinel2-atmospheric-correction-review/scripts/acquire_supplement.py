"""Replay the lawful follow-up retrievals used in CTR-64; no access bypass."""
import concurrent.futures as cf
import json
from acquire_evidence import get,ROOT

GROUPS={
 'retrieval_supplement.json':{
 'Vanhellemont2019DSF_pdf':'https://www.vliz.be/imisdocs/publications/343844.pdf',
 'DeKeukelaere2018iCOR_pdf':'https://www.vliz.be/imisdocs/publications/330081.pdf',
 'Steinmetz2011Polymer_pdf':'https://opg.optica.org/oe/viewmedia.cfm?uri=oe-19-10-9783&seq=0',
 'Hagolle2015MAJA_pdf':'https://www.mdpi.com/2072-4292/7/3/2668/pdf',
 'Renosh2020Estuaries_pdf':'https://www.mdpi.com/2072-4292/12/8/1285/pdf',
 'snap_download':'https://step.esa.int/main/download/snap-download/',
 'snap_update':'https://step.esa.int/main/snap-14-0-2-update-is-now-available/',
 'opttbx_tree':'https://api.github.com/repos/senbox-org/optical-toolbox/git/trees/master?recursive=1',
 's3tbx_tree':'https://api.github.com/repos/senbox-org/s3tbx/git/trees/master?recursive=1',
 'Fan2021OCSMART_crossref':'https://api.crossref.org/works?query.title=OC-SMART%3A%20A%20machine%20learning%20based%20data%20analysis%20platform%20for%20satellite%20ocean%20color%20sensors&rows=1'},
 'retrieval_supplement2.json':{
 'c2rcc_current_operator':'https://raw.githubusercontent.com/senbox-org/optical-toolbox/master/opttbx-c2rcc/src/main/java/eu/esa/opt/c2rcc/msi/C2rccMsiOperator.java',
 'c2rcc_current_algorithm':'https://raw.githubusercontent.com/senbox-org/optical-toolbox/master/opttbx-c2rcc/src/main/java/eu/esa/opt/c2rcc/msi/C2rccMsiAlgorithm.java',
 'c2rcc_current_commit':'https://api.github.com/repos/senbox-org/optical-toolbox/commits/master',
 'c2rcc_license':'https://raw.githubusercontent.com/senbox-org/s3tbx/master/s3tbx-c2rcc/LICENSE.txt',
 'sen2cor_iod':'https://step.esa.int/thirdparties/sen2cor/2.13.0/docs/OMPC.TPZG.IOD.004%20-%20i1r0%20-%20Sen2Cor%202.13.02%20Input%20Output%20Data%20Definition.pdf',
 'Hagolle2015MAJA_pdf_alternative':'https://mdpi-res.com/d_attachment/remotesensing/remotesensing-07-02668/article_deploy/remotesensing-07-02668.pdf',
 'Renosh2020Estuaries_pdf_alternative':'https://mdpi-res.com/d_attachment/remotesensing/remotesensing-12-01285/article_deploy/remotesensing-12-01285.pdf',
 'maja_license':'https://raw.githubusercontent.com/CNES/MAJA/master/LICENSE.TXT',
 'acolite_manual_tree':'https://api.github.com/repos/acolite/acolite/git/trees/main?recursive=1'},
}
if __name__=='__main__':
 for name,urls in GROUPS.items():
  with cf.ThreadPoolExecutor(max_workers=6) as pool:results=list(pool.map(get,urls.items()))
  (ROOT/'outputs'/name).write_text(json.dumps(results,indent=2))
  print(name,len(results))
