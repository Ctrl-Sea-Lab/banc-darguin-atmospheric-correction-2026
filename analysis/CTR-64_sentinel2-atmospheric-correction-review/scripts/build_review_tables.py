"""Build CTR-64 review tables from verified metadata and curated evidence.

No scientific data are processed. Source text/PDFs stay ignored. The protected
root bibliography is read only; additions are staged beside the report.
"""
from pathlib import Path
import csv, hashlib, json, re, shutil, subprocess, unicodedata

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
SRC=ROOT/'outputs/sources'
TABLES=ROOT/'tables'
LIT=REPO/'literature'
DATE='2026-10-20'

def table(name, headers, rows):
 TABLES.mkdir(exist_ok=True)
 with (TABLES/(name+'.csv')).open('w',newline='') as f:
  w=csv.writer(f);w.writerow(headers);w.writerows(rows)
 def cell(x):return str(x).replace('|','/').replace('\n',' ')
 (TABLES/(name+'.md')).write_text('| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+''.join('| '+' | '.join(map(cell,row))+' |\n' for row in rows))

METHODS=[
 ['Sen2Cor 2.13.02','libRadtran LUTs; surface/atmosphere RT','Vegetation spectral constraints; inversion plus fallback','DDV; CAMS fallback; rural/maritime/auto choices','Single acquisition; spatial interpolation','Land HDRF; not an aquatic bio-optical model','Documented neighborhood capability; exact enabled calibration must be logged','ESA manual §§2.2–2.3; ATBD §§4.5–4.7; current IOD'],
 ['ACOLITE DSF','Atmospheric LUTs; molecular/gas precorrection','Dark spectrum from multiple bands/targets; LUT model/AOT fit','Near-dark observations; limited candidate aerosol models','Estimation region/tile homogeneity; interpolation','Surface reflectance without a restrictive aquatic spectral inversion','Inspected generic adjacency default off; optional separate algorithms','Vanhellemont2019DSF §2; inspected defaults'],
 ['ACOLITE TSDSF + RAdCor','Atmosphere spatial response kernels/LUTs','Adjacency-aware aerosol estimate then spatial surface inversion','TSDSF dark-surface constraints with neighborhood contribution','Surrounding image context; kernel and subscene assumptions','General nonnegative surface retrieval; validation mostly small waters','Explicit spatial correction; separate configuration from DSF','Castagna2025RAdCor §§2–5'],
 ['POLYMER v4.17','Physical precorrections plus polynomial atmospheric/glint terms','Joint constrained spectral optimization','Residual aerosol/glint spectral representation rather than a DDV AOT product','Pixel spectral fit; ancillary atmosphere; optional coastal settings','Aquatic reflectance model; normalization choices','No RAdCor-equivalent spatial correction established','Developer README/changelog; Warren2019MSI processor description'],
 ['MAJA documented 4.x','SOS RT LUT heritage in ACIX table','Cost function combining spectral and temporal constraints','Stable-reference and spectral criteria; CAMS aerosol type optional','Backward initialization and sequential L2A history','Land surface with temporal stability over usable references','Explicit, version/configuration sensitive; filter fix 4.9.3','Hagolle2015MAJA; Doxani2023ACIXLand Table 1; CESBIO startmaja'],
 ['C2RCC MSI networks','Coupled atmosphere/water RT training simulations','Pretrained neural-network inverse mappings and scope tests','Training distribution of atmospheres and water IOPs','Angular/spectral priors embedded in networks; no temporal series required','Aquatic bio-optical domain; bottom/strong glint may be out of scope','No explicit spatial shoreline correction established','C2RCC specification; Muller2026C2RCC §§2–4; source'],
 ['iCOR','MODTRAN5 LUTs','Image-based aerosol retrieval then surface correction','Image constraints; exact current fallback requires package verification','Spatial image constraints; SIMEC neighborhood over water','Unified land/water processing; no direct sun glint in foundational model','SIMEC over water; fixed-range land treatment in paper','DeKeukelaere2018iCOR Methods'],
 ['SIAC','6S/6SV-derived emulators','Bayesian maximum-a-posteriori atmosphere; uncertainty propagation','CAMS priors + MCD43 surface predictions and covariance','Coarse surface/atmosphere priors; spatial smoothing','Land BRF; not a water-column reflectance retrieval','No explicit spatial adjacency correction established; scale PSF is different','Yin2022SIAC §2; current README'],
 ['OC-SMART','Coupled RT simulation training; precorrections','Machine-learning atmospheric/water inversion','Simulation/model domain; ancillary inputs','Spectral training priors; no required temporal series established','Aquatic model; published moderate-glint training','Contamination tolerance claims are not an explicit spatial correction','Fan2021OCSMART §§2–3,6; current package unavailable'],
]

LOCAL=[
 ['Sen2Cor','2.13.02; 2026-09-24; Linux/Windows 64-bit','Standalone bundled runtime; CLI; no current native macOS listed','Mixed package: Apache-2.0 components plus DLR/ATCOR binary terms and third-party notices; freely distributed, not wholly permissive source','M: intact supported L1C SAFE, angles/metadata/LUTs. O/R: DEM, CCI. CAMS fallback from AUX/other supported route','M: cached LUT/runtime. R: DEM/CCI for core-like processing. DEM CDSE access authenticated; exact gas/fallback source logged','Manual: ≥4 GB available for 10 m, historical example. One-job profiling R; no GPU identified','L2A_Process <L1C.SAFE> --resolution 20; inspect installed help; separate outputs/logs','ESA 2.13.02 SUM §§2.5,3,5; release/IOD'],
 ['ACOLITE','Release API: 20260421.0; dated main snapshot separately hashed','Python + GDAL/NumPy/NetCDF/scientific stack; source or binaries; GUI/CLI; binary architecture check required','GNU GPL v3 license file; source public; dependency/auxiliary notices retained','M: L1C metadata/bands and LUTs. R: explicit ROI/output/method. O: gas/meteo/glint/adjacency/terrain routes as applicable','M: first-use LUT retrieval/cache. O: external ancillary; image-based aerosol does not remove physical input defaults','No common current RAM minimum verified; kernels/resolution/exports change demand; CPU route; no GPU required by inspected docs','python launch_acolite.py --cli --settings=settings.txt; save effective settings','README, LICENSE, config/defaults and release API'],
 ['POLYMER','Changelog v4.17 (2025-11-12); v5 preview separate','Python/Cython + compiled build; developer Pixi/Conda source routes; CLI/Python; platform/compiler check; no supported binary matrix verified','Custom POLYMER licence v2.0: free noncommercial scientific use; commercial permission from HYGEOS; source-available is not unrestricted open source','M: L1C granule plus product metadata, static model files and atmosphere. Reader A/B/C; default resolution 60 m','M: auxiliary model files, pressure/ozone/wind source; NASA or embedded ECMWF route. O: DEM/land mask; caches required for offline route','No contemporary per-tile RAM minimum verified; multiprocessing optional/off by default in README; CPU/compiled code; no GPU required','run_atm_corr(Level1_MSI(...), Level2(...)); explicit resolution, ancillary and datasets','README; LICENSE; CHANGELOG; MSI/ancillary code'],
 ['MAJA','CESBIO 4.10/4.11/4.12 notices; newer current release unverified due GitLab challenge','Precompiled Linux self-extracting route; C++/OTB superbuild alternative; startmaja CLI; no native Windows/macOS guarantee','Apache since v4.2; archived CNES identifies Apache-2.0. Current package and bundled notices still need verification','M: intact L1C, GIPP/LUT and formatted tile DTM. M for temporal test: usable series/restart state. One-scene init possible','O: CAMS, paired with appropriate LUT release (49r1 in 4.10). M: DTM/GIPP. R: cached masks/auxiliaries/workplan','No current cross-platform RAM minimum verified; initialization adds workload and storage; thread/strip controls; no GPU requirement identified','startmaja -f folders.txt -t <tile> -s <site> -d <start> -e <end>; optional --cams','CESBIO install/start/terrain/userconf; release information'],
 ['C2RCC in SNAP','SNAP14.0.0 installers; 14.0.2 update announcement 2026-10-08; exact module/network to record','SNAP Optical Toolbox; bundled Java route; GUI and gpt batch; Windows/Linux 64-bit, macOS Intel/ARM installers; esa_snappy optional','Public GPL-3 family; module source GPL v3-or-later notice; network/package notices retained','M: supported MSI L1C spectral/geometry data resampled consistently. M: packaged networks. Land L2A is not equivalent TOA input','M: atmospheric values, but defaults supported; O/R: actual pressure/ozone ancillary and appropriate temperature/salinity/elevation. No temporal history required','No C2RCC-specific contemporary minimum verified; JVM heap/cache and tile size matter; inference CPU route; no GPU training required','gpt c2rcc.msi -h; save/version graph.xml; gpt graph.xml','ESA downloads/update, C2RCC docs, inspected MSI operator/algorithm'],
]

CANDIDATES=[
 ['C2RCC / C2X / C2X-COMPLEX','Preferred fifth','High water relevance; MSI comparisons; trained inversion adds diversity','Aquatic only; OLCI results not MSI validation; bottom/glint/OOS limits','Public GPL source and SNAP batch route; no processor install tested','Directional/normalized/rhow/Rrs choices; limited water output bands','No expensive local training required; inference resource profiling pending','Best combined diversity/access; variants are within-processor sensitivity'],
 ['iCOR','Conditional water/shoreline fallback','Unified land/water + SIMEC; field MSI evidence','Some LUT/image-aerosol overlap; no direct glint correction in foundational model','VITO basic plugin free but download form; exact package/license/platform/baseline unresolved','Land/water product definitions need package verification','Published operational route; current resources and access untested','Adopt only after access/terms/compatibility checks'],
 ['SIAC','Conditional land-priority alternative','Bayesian atmosphere, priors and per-pixel uncertainty; land validation','Water-column use unsupported; coarse priors vulnerable at changing boundary','Public code; LICENSE AGPLv3 vs README GPLv3 discrepancy; GEE/non-GEE auxiliary routes','Land surface reflectance + uncertainty; not aquatic Rrs','Native dependencies, MCD43 time window and service/cache burden','Choose if exposed surfaces become main objective; PI scope trade-off'],
 ['OC-SMART','Reserve; current access failed','Coupled RT-trained aquatic inversion; MSI in paper','Broad inversion family overlaps C2RCC; published performance not current-package support','Website access failed; terms, current distribution and version not verified','Paper describes normalized Rrs and IOPs; current product metadata unverified','Published Python/SNAP routes; present local requirements unresolved','Cannot certify realistic current deployment from paper alone'],
 ['6S/6SV custom implementation','Excluded from five end-user processors','Transparent forward engine could test choices','Engine is not a complete retrieval/masking/validation workflow','No specific supported MSI end-user package/version selected','Custom definitions and uncertainty need design','Adds development/test scope, no verified deployment estimate','Consider only under separate custom-method authorization'],
 ['FLAASH / ATCOR','Excluded from presently accessible recommendation','Potential land/RT parameterization comparison','Paid components/access and aquatic relevance need investigation','No purchase/license accepted; current MSI package/platform not verified','Specific package conventions unverified','Costs and requirements not established','Potential future paid comparison; not ruled scientifically inferior'],
]

OUTPUTS=[
 ['Sen2Cor','Surface HDRF; dimensionless after metadata scaling/offsets','MSI supported output support; not all native bands 10 m','Water classification is not water-leaving Rrs','IOD 2.13.02 §2.3.10'],
 ['ACOLITE','rhos dimensionless; requested Rrs sr⁻¹ with documented aquatic relation ρs=πRrs','Bands/resolution and interface/glint settings recorded','Do not apply aquatic conversion to arbitrary land products','README; DSF paper; effective settings'],
 ['POLYMER','Water-reflectance output; retain normalization/BRDF configuration','Reader default 60 m; request actual support explicitly','Do not infer exact Rrs normalization from rho_w name alone','MSI reader, changelog and output metadata'],
 ['MAJA','Land surface reflectance; distinguish surface and terrain-corrected variants','Sensor output resolution and MUSCATE scaling/masks','Not a water-column Rrs product; bitmasks require decoding','CESBIO output documentation and product metadata'],
 ['C2RCC','Directional rhow default in inspected source; Rrs option and normalized products distinct','Inspected MSI water bands B1–B7/B8A; resample common support','Check outputAsRrs, outputRhown, units and angular normalization before π conversion','MSI operator and algorithm; specification'],
 ['SIAC','Land BRF plus uncertainty; README lists scale 0.0001','Native sensor grids; actual GeoTIFF metadata authoritative','No aquatic interpretation from division by π','SIAC README/paper'],
 ['iCOR / OC-SMART','Paper-level descriptions; current package definitions require verification','Do not assume MSI band/resolution compatibility from older paper','No automatic π conversion; normalized versus directional distinction','Foundational papers; package access gaps'],
]

CLAIMS=[
 ['C01','recommendation','Retain four and add C2RCC for aquatic inversion diversity','Multiple method sources + C2RCC implementation','Method matrix; decision matrix','No empirical Banc d’Arguin ranking; reviewer synthesis'],
 ['C02','documented capability','Sen2Cor 2.13.02 improves CAMS use over water; release 2026-09-24','sen2cor_release','ESA release features/date','Release note claim, not independent accuracy validation'],
 ['C03','documented capability','Sen2Cor libRadtran, DDV, CAMS fallback and aerosol choices','sen2cor_manual','§§2.2–2.3','Finite aerosol model family; no dust guarantee'],
 ['C04','documented capability','Sen2Cor has documented adjacency capability','sen2cor_atbd; sen2cor_manual','ATBD §§4.5–4.7; SUM expert settings','Older ATBD; exact 2.13 executable/default enablement needs retained calibration'],
 ['C05','literature finding','DSF dark spectrum/tile assumptions and aerosol constraints','Vanhellemont2019DSF','§2','Historical configuration; current defaults separately inspected'],
 ['C06','documented capability','ACOLITE inspected tiled AOT, residual-glint/adjacency off','acolite_defaults','dsf_aot_estimate; dsf_residual_glint_correction; adjacency_correction','Snapshot not necessarily released binary defaults'],
 ['C07','literature finding','TSDSF+RAdCor explicit adjacency; band-dependent evidence','Castagna2025RAdCor','§§2,4,5','Belgian small waters; not local intertidal validation'],
 ['C08','documented capability','POLYMER v4.17 and v5 preview coexist; special terms','polymer_changelog; polymer_license','v4.17 entry; Terms v2.0','Use classification/permission not decided'],
 ['C09','documented capability','POLYMER MSI default 60 m, offsets and A/B/C','polymer_msi','Level1_MSI constructor, platform and offset parsing','Source snapshot, not execution test'],
 ['C10','literature finding','MAJA combines spectral and temporal aerosol constraints','Hagolle2015MAJA; Doxani2023ACIXLand','Methods/Conclusions; Table 1','Foundational validation not MSI coastal; newer operational settings differ'],
 ['C11','documented capability','MAJA one-scene init possible; eight default backward products','maja_start','Requirements and Note','Not recommended standard usage; usable series required'],
 ['C12','documented capability','MAJA 4.10 CAMS49r1/S2C; 4.9.3 adjacency fix','maja_home','Release notices','Current GitLab package inaccessible; no current tag claim'],
 ['C13','documented capability','C2RCC coupled RT networks and domain tests','c2rcc_spec; c2rcc_nets','Algorithm Specification; MSI inventory','Network training domain does not guarantee site coverage'],
 ['C14','literature finding','C2RCC shallow-bottom/strong-glint limitations','Muller2026C2RCC','§4','Main quantitative validation concerns OLCI'],
 ['C15','documented capability','C2RCC MSI output defaults and bands','c2rcc_current_operator; c2rcc_current_algorithm','outputAsRrs; NN_SOURCE_BAND_REFL_NAMES','Installed SNAP module must be recorded separately'],
 ['C16','literature finding','iCOR MODTRAN5/SIMEC; direct glint and whitecaps neglected','DeKeukelaere2018iCOR','Methods pp.527–529','Foundational model; current package unverified'],
 ['C17','documented capability','VITO free plugin/access form','icor_home; icor_access','Service and download form','Exact license/source/current package not obtained'],
 ['C18','literature finding','SIAC Bayesian constraints and land uncertainty','Yin2022SIAC','§§2–4','Land validation is not aquatic validation'],
 ['C19','documented capability','SIAC auxiliary route and license inconsistency','siac_readme; siac_license','Auxiliaries; LICENSE heading','AGPLv3 file versus GPLv3 README; resolve before redistribution'],
 ['C20','literature finding','OC-SMART MSI and coupled ML; website access unconfirmed','Fan2021OCSMART; ocsmart_access','§§2–3,6; failed software retrieval','Historical distribution is not current deployment proof'],
 ['C21','literature finding','Warren common matchups 521, ±3h coastal/±24h inland','Warren2019MSI','Abstract; Methods; Conclusions','Older S2A processors and regional/time-window limits'],
 ['C22','literature finding','ACIX Land common sites 79 S2 and 62 L8','Doxani2023ACIXLand','Abstract/Methods','Reference types differ; land only'],
 ['C23','literature finding','ACIX-Aqua performance depends on reference population/water type','Pahlevan2021ACIXAqua','§§3–7','Older algorithms, not universal site ranking'],
 ['C24','literature finding','Gironde comparison uses satellite indirect reference','Renosh2020Estuaries','§5 Conclusions','ACOLITE-corrected L8 reference; no independent coincident radiometry'],
 ['C25','interpretation','Separate water/exposed/mixed pixels and output definitions','All domain and output sources','Output table and proposed design','Proposed future design, not implemented'],
 ['C26','documented capability','Sen2Cor memory guideline 4GB; historical peak 3.5GB','sen2cor_manual','§2.5','Historical hardware, not new benchmark or current macOS support'],
 ['C27','planning estimate','16–32 GB starting workstation envelope','Reviewer estimate','Resource-planning section','Not a documented minimum, performance result or hardware purchase recommendation'],
 ['C28','literature finding','Sen2Cor field spectra for exposed seagrass/bare/mixed surfaces','Zoffoli2020','§§2.3.1,3.3.1 and Fig.5','Limited Bourgneuf scenes; no common processor ranking'],
 ['C29','literature finding','Intertidal Sen2Cor use includes subsequent red/NIR calibration','Daggers2020','Satellite preprocessing','Temporal consistency cannot be attributed to Sen2Cor alone'],
 ['C30','literature finding','Mudflat Sen2Cor+BRDF and migration timing effects','Jacobs2021','Satellite processing; Discussion','Biological endpoint and representativeness limits'],
 ['C31','literature finding','Bijagos ACOLITE DSF exposure application and tidal lags','Granadeiro2021','§§2.2–2.5; Discussion','Relative calibration; exposure endpoint, not absolute AC validation'],
 ['C32','literature finding','Sediment moisture/grain size and empirical calibration','Thuy2022','§§II–IV','Local sediment/calibration domain; no processor superiority test'],
 ['C33','literature finding','MAJA comparison aligned adjacency/terrain treatment','Colin2023','§§2–4','Developer land assessment; not tidal-flat validation'],
]

SEARCHES=[
 ['Crossref API','Sentinel-2 atmospheric correction coastal intertidal adjacency mineral dust','10 returned records; full response retained'],
 ['OpenAlex API','Sentinel-2 atmospheric correction coastal intertidal adjacency mineral dust','10 returned records; full response retained'],
 ['Semantic Scholar API','Sentinel-2 atmospheric correction intertidal','HTTP429; not searched exhaustively'],
 ['Targeted web','Sen2Cor 2.12 2.13 release software user manual license Sentinel 2','ESA 2.13 identified; older release not treated as latest'],
 ['Targeted web','ACOLITE GitHub dark spectrum fitting adjacency RAdCor','Official code, RAdCor paper and release leads'],
 ['Targeted web','POLYMER hygeos github license Sentinel-2','Developer code/license/changelog'],
 ['Targeted web','MAJA 4.9 5.0 user manual license atmospheric correction start mode','CESBIO and archived/current repository leads'],
 ['Targeted web','C2RCC algorithm specification C2X MSI neural networks license SNAP 2026','Algorithm specification, networks and recent synthesis'],
 ['Targeted web','site.remotesensing.vito.be icor download license linux windows Sentinel 2 SIMEC','Service/download; terms unresolved'],
 ['Targeted web','SIAC Sentinel-2 Bayesian atmospheric correction Yin 2022 uncertainty github','Paper/source/license'],
 ['Targeted web','OC-SMART Sentinel-2 software download license atmospheric correction','Foundational paper and failed current access'],
 ['Targeted web','ACIX Aqua Pahlevan 2021 atmospheric correction intercomparison Sentinel-2 2021 112366','NASA repository full text'],
 ['Targeted web','ACIX land II Doxani 2023 Sentinel-2 MAJA Sen2Cor atmospheric correction intercomparison','Publisher/DLR full text'],
 ['Targeted web','Sentinel-2 intertidal atmospheric correction seagrass mudflat ACOLITE Sen2Cor POLYMER validation','No verified site-specific exposed-intertidal validation established'],
 ['Targeted web','"A generalized physics-based correction for adjacency effects"','Institutional full text; DOI checked'],
 ['Targeted web','site.step.esa.int main download SNAP 13 2026 system requirements','SNAP14 installer/update evidence; avoid obsolete assumption'],
 ['Citation chaining','ACIX-Aqua / ACIX-II Land / C2RCC references and ACOLITE developer bibliography','Warren, DSF, iCOR, SIAC, MAJA foundational and recent RAdCor/C2RCC'],
]

def bibliography():
 LIT.mkdir(exist_ok=True); (LIT/'pdfs').mkdir(exist_ok=True)
 (LIT/'pdfs/.gitignore').write_text('*\n!.gitignore\n')
 # Preserve protected bibliography; retain citation keys if DOI already exists.
 existing=(REPO/'library.bib').read_text()
 mapping={}
 prior_keys=ROOT/'outputs/prior_citation_keys.json'
 if prior_keys.exists():mapping.update(json.loads(prior_keys.read_text()))
 for e in re.split(r'(?=@\w+\{)',existing):
  k=re.search(r'@\w+\{([^,]+),',e);d=re.search(r'doi\s*=\s*[{\"]([^}\"]+)',e,re.I)
  if k and d:mapping[d[1].lower()]=k[1]
 entries=[];rows=[]
 for f in sorted(SRC.glob('*_crossref.json')):
  key=f.name.removesuffix('_crossref.json');d=json.loads(f.read_text())['message']
  if 'items' in d:d=d['items'][0]
  doi=d['DOI'];citation=mapping.get(doi.lower(),key)
  title=d['title'][0].replace('  ',' ')
  year=d.get('published-print',d.get('published',{})).get('date-parts',[[None]])[0][0]
  authors=' and '.join(a.get('family','')+', '+a.get('given','') for a in d.get('author',[]))
  venue=d.get('container-title',[''])[0]
  fields={'title':title,'author':authors,'year':str(year),'journal':venue,'doi':doi,'url':'https://doi.org/'+doi}
  for k in ['volume','issue','page']:
   if k in d:fields[{'issue':'number','page':'pages'}.get(k,k)]=str(d[k])
  entries.append('@article{'+citation+',\n'+''.join('  '+k+' = {'+v+'},\n' for k,v in fields.items())+'}\n')
  pdf=next(iter((ROOT/'literature/pdfs').glob(key+'_pdf*.pdf')),None)
  if pdf:
   author=re.sub('[^A-Za-z]','',unicodedata.normalize('NFKD',d['author'][0]['family']).encode('ascii','ignore').decode())
   short=re.sub(r'^[A-Za-z]+[0-9]{4}', '', key)
   filename=f'{author}_{year}_{short}.pdf'
   target=LIT/'pdfs'/filename
   if target.exists() and hashlib.sha256(target.read_bytes()).digest()!=hashlib.sha256(pdf.read_bytes()).digest():raise RuntimeError('PDF collision '+filename)
   if not target.exists():shutil.copy2(pdf,target)
   pdfpath=str(target.relative_to(REPO))
  else:pdfpath=''
  verification='full text' if pdf else 'abstract'
  download_url=''
  if pdf:
   for logname in [f.name for f in (ROOT/'outputs').glob('retrieval*.json')]:
    for record in json.loads((ROOT/'outputs'/logname).read_text()):
     if record['id']==pdf.stem:download_url=record['url']
  notes={'Steinmetz2011Polymer':'Original full text not obtained; no detailed MSI claim attributed to original paper alone','Tavora2023Recipes':'Publisher excerpts inspected; local PDF failed certificate verification; no benchmark extrapolated','Renosh2020Estuaries':'Indirect ACOLITE-corrected Landsat reference, not coincident in situ validation','Muller2026C2RCC':'Detailed validation largely OLCI; do not transfer metrics to MSI','Hagolle2015MAJA':'Foundational FormoSat-2/Landsat method; not direct MSI coastal validation','Zoffoli2020':'Two radiometric-validation scenes; exposed seagrass/bare/mixed surfaces, not a processor ranking','Granadeiro2021':'Bijagos exposure/topography application; subsequent relative calibration, not absolute AC validation','Daggers2020':'Sen2Cor followed by relative calibration; performance not attributable to atmospheric correction alone','Jacobs2021':'Sen2Cor plus BRDF; biological migration/timing confounds validation','Colin2023':'Land developer assessment; configuration-aligned comparisons, not tidal-flat validation','Thuy2022':'Local empirical line and sediment experiment; no cross-processor accuracy ranking'}.get(key,'Relevant methods/conclusions inspected; geographic/version limits in claim table')
  rows.append([citation,title,authors,year,venue,doi,d.get('type',''),pdfpath,'https://doi.org/'+doi,'available locally' if pdf else 'not obtained',verification,'atmospheric correction; Sentinel-2; coastal/intertidal review','See claim table for specific support and limits',DATE,download_url,notes,'Published journal article'])
 (ROOT/'library_additions.bib').write_text('\n'.join(entries))
 headers=['citation_key','title','authors','year','journal','doi','publication_type','pdf_path','source_url','full_text_availability','verification_level','keywords','relevance','verified_date','pdf_retrieval_url','verification_limits','publication_version']
 with (LIT/'references_index.csv').open('w',newline='') as f:w=csv.writer(f);w.writerow(headers);w.writerows(rows)
 shutil.copy2(LIT/'references_index.csv',TABLES/'references_index.csv')
 (LIT/'literature_review.qmd').write_text('---\ntitle: "CTR-64 literature synthesis"\n---\n\nTake-home message: retain Sen2Cor, ACOLITE, POLYMER and MAJA, adding C2RCC for aquatic inversion diversity. No Banc d’Arguin accuracy ranking is established.\n\nThe full critical synthesis is in [the standalone HTML report](../analysis/CTR-64_sentinel2-atmospheric-correction-review/report.html). Method, implementation and evidence matrices distinguish literature findings, documented capabilities and reviewer recommendations.\n\nCross-study disagreements depend on water type, version, reference independence and matchup/coverage selection. Exposed-intertidal evidence remains limited. iCOR is a conditional aquatic fallback; SIAC is a land-priority alternative. Root bibliography additions await the mandatory PI synchronization gate. Independent review of the first submission requested minor revisions; focused reconsideration and PI approval are pending.\n')
 return rows

if __name__=='__main__':
 (ROOT/'.gitignore').write_text('/outputs/sources/\n/literature/pdfs/*\n!literature/pdfs/.gitignore\n/.quarto/\n/*_files/\n\n**/*.quarto_ipynb\n')
 (ROOT/'literature/pdfs/.gitignore').write_text('*\n!.gitignore\n')
 table('method_matrix',['Processor/configuration','Forward model','Inversion','Aerosol constraints','Spatial/temporal priors','Surface model','Adjacency','Evidence'],METHODS)
 table('local_requirements',['Processor','Version/platform','Implementation','License/access','Inputs','Auxiliaries/offline','Resources','Operating outline','Evidence'],LOCAL)
 table('candidate_decision',['Candidate','Disposition','Scientific contribution','Limits/overlap','Availability/license','Output compatibility','Automation/resources','Decision rationale'],CANDIDATES)
 table('output_definitions',['Processor','Quantity','Support','Conversion caution','Evidence'],OUTPUTS)
 table('claim_evidence',['claim_id','evidence_type','claim','source_id','location','limitations'],CLAIMS)
 table('search_log',['source','complete_query_or_chain','outcome'],[[DATE+' '+r[0],r[1],r[2]] for r in SEARCHES])
 refs=bibliography()
 logs=[]
 for logfile in sorted((ROOT/'outputs').glob('retrieval*.json')):
  logs+=json.loads(logfile.read_text())
 source_rows=[];gaps=[]
 for r in logs:
  source_rows.append([r['id'],r['url'],r['checked'],r.get('status',''),r.get('path',''),r.get('sha256',''),r.get('bytes',''),r.get('valid_pdf',''),r.get('error','')])
  if 'error'in r or ('pdf'in r['id'] and not r.get('valid_pdf')):gaps.append([r['id'],r.get('error','Response was not a PDF'),'No bypass; alternative lawful route used when available; see index'])
 gaps += [
  ['MAJA active GitLab','Access challenge','CESBIO public docs/archived code used; no newest-tag claim'],
  ['Root library.bib','verify-ready: requires_pre_task_sync','Addition provided locally; Charles/Ada coordination pending'],
  ['Independent scientific review','CTR-65: Minor Revision on 943ee59; corrections submitted for focused reconsideration','Author validation is not independent review or PI approval'],
  ['Banc d’Arguin five-processor validation','No site-specific common benchmark established','External intertidal field/application evidence is available; no local accuracy inference'],
  ['Processor installation / hardware benchmark','Outside review scope, not performed','All feasibility statements conditional'],
  ['Full systematic coverage','No registered systematic protocol; sources inaccessible','Structured critical review only'],
  ['PDF redistribution','Permissions differ; full-text redistribution not authorized','PDFs and extracted text excluded from Git/archive'],
 ]
 table('source_manifest',['source_id','url','checked','http_status','local_path','sha256','byte_size','valid_pdf','error'],source_rows)
 table('access_gaps',['item','gap','treatment'],gaps)
 nfull=sum(r[10]=='full text' for r in refs)
 table('coverage',['Measure','Count','Interpretation'],[
  ['Verified scholarly references',len(refs),'Crossref metadata checked against publication/developer records'],
  ['Scholarly PDFs retained locally',sum(bool(r[7])for r in refs),'Not redistributed; paths and identities in index'],
  ['Full-text scholarly sources inspected',nfull,'Methods/conclusions or relevant implementation passages'],
  ['Metadata/abstract-only scholarly sources',len(refs)-nfull,'No detailed claim attributed solely to inaccessible full text'],
  ['Document/metadata retrieval attempts',len(logs),'Includes alternatives and failed requests; not a PRISMA study count'],
  ['Actual processor executions',0,'Literature and documentation review only'],
 ])
 software=[]
 for name in ['acolite_commit','polymer_commit','siac_commit','c2rcc_current_commit']:
  d=json.loads((SRC/(name+'.json')).read_text());software.append([name,d['sha'],d['commit']['committer']['date'],DATE])
 table('software_snapshots',['source_id','commit_sha','commit_date','retrieval_date'],software)
 print(json.dumps({'references':len(refs),'full_text':nfull,'retrieval_attempts':len(logs),'tables':len(list(TABLES.glob('*.csv')))},indent=2))
