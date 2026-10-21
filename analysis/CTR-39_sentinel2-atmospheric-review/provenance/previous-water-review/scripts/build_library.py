"""Build a task-local bibliography and evidence index from verified source records."""
import csv
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
NOTES = {
 'Warren2019': ('full text','Methods §3.1 (processor descriptions, printed pp. 269–270; exponential extrapolation p. 270 / PDF p. 4); §3.2 and Table 2 (processing options); §3.3 (field-data filtering); Results; Conclusions', 'Coastal Baltic/Western Channel and European inland validation; Polymer and C2RCC performed comparatively well.', 'Historical implementations; ACOLITE uses exponential extrapolation here, not later DSF; coastal and inland matchup windows differ.'),
 'Pahlevan2021': ('full text','Methods §§2–3; Results §4; Discussion §5.2; Abstract', 'ACIX-Aqua; optical-water-type-dependent performance and propagation to water-quality estimates.', 'Mixed sensors and validation populations; results cannot be pooled into a universal Sentinel-2 coastal ranking.'),
 'Vanhellemont2019': ('full text','Methods §2.3.2 and glint correction; Results; Conclusions §5', 'DSF dark-target and local-atmospheric-homogeneity assumptions; tiled processing and optional SWIR glint correction.', 'Algorithm-development validation; not an independent universal comparison; historic processor settings.'),
 'DeKeukelaere2018': ('full text','Methodology and SIMEC description; adjacency Results/Figures 8–12; Conclusion', 'iCOR land-based aerosol retrieval and SIMEC adjacency treatment; effects on coastal/inland spectra.', 'Availability of suitable land and applicability of NIR-similarity assumptions matter; adjacency benefit is context-specific.'),
 'Steinmetz2011': ('abstract','Publisher/PubMed abstract (PMID 21643235); metadata Crossref', 'POLYMER origin and high-level MERIS sunglint capability only.', 'No local full text obtained; detailed equations and Sentinel-2 performance are not inferred from this abstract.'),
 'MainKnorn2017': ('full text','Processor description §§2–3; atmospheric correction and validation discussion', 'Sen2Cor L1C-to-L2A BOA processor and land-oriented product context.', 'Conference proceedings; describes the 2017 processor, not current performance; BOA is not automatically water-leaving reflectance.'),
 'Fan2021': ('full text','Methods §§2.1–2.7; evaluation; Discussion/Conclusions', 'OC-SMART coupled atmosphere–ocean simulations and neural-network retrieval; MSI support.', 'Development paper spans sensors; positive outputs do not independently prove accuracy; some robustness testing explicitly not documented.'),
 'Harmel2018': ('full text','HAL author manuscript; §§2.3–3 and validation §4', 'SWIR-based sunglint estimation and spectral extrapolation (GRS approach).', 'Needs ancillary atmospheric information and proper separation of aerosol and glint; ordinary deglinting alone is not full atmospheric correction.'),
 'Bui2022': ('full text','Methods/valid matchup Table 4; Discussion §6.1; Conclusions §7', 'French Channel/Guiana coastal comparison supports OC-SMART and NASA-AC within its dataset.', '28 potential individual matchups; NASA-AC has fewer valid retrievals; individual and common-set rankings differ; historical versions.'),
 'PereiraSandoval2019': ('full text','Methods §2.4; Results §4.3; Discussion §5; Conclusions §6', 'Spanish reservoirs/lakes; water-type-dependent comparison, often favorable to Polymer/C2RCC.', 'Freshwater evidence supports method testing but is not direct evidence for Mauritanian marine waters.'),
 'Castagna2025': ('full text','Methods §§2–3; comparison figures; discussion and conclusion; published pp. 2719–2743', 'TSDSF + RAdCor modular atmospheric and adjacency correction; Belgian inland-water validation.', 'Not marine site validation; clear-sky MSI visible deviations exclude 443 nm; red/NIR behavior differs; do not equate RAdCor with ordinary DSF.'),
 'Wu2024': ('full text','Publisher full HTML: Methods §2; Results §3.1/Table 3; Discussion §4; Conclusion §5', 'T-Mart adjacency preprocessing improves subsequent ACOLITE/POLYMER/l2gen retrievals in nearshore validation.', 'HTML inspected; no standalone article PDF obtained. Pooled MSI/OLI statistics, not a universal Sentinel-2-only correction factor.'),
 'Muller2026': ('full text','§2.1 training conditions; §§2.2–2.3; validation scope and Discussion §4', 'C2RCC framework, flags, neural-network assumptions, and explicitly optically deep training model.', 'Main new validation is Sentinel-3 OLCI; describes current v2-2017 framework; cannot be treated as new MSI coastal superiority evidence.'),
 'Vrdoljak2022': ('full text','SDB methods; Results; Discussion and Conclusions §4, pp. 15–17', 'Middle Adriatic empirical bathymetry comparison; application error and valid-scene coverage matter.', 'Locally calibrated depth models can absorb reflectance biases; SDB accuracy is not independent Rrs validation.'),
 'Gordon1994': ('full text','Algorithm development §§2–3; NIR aerosol retrieval and assumptions', 'Foundational NIR-based ocean-color atmospheric correction.', 'SeaWiFS simulation-era study, not direct Sentinel-2 validation; institutional teaching copy retained locally only.'),
 'Lathif2025': ('full text','Methods §II; Results §III; Discussion §IV; Conclusion §V, pp. 1174–1195', 'Atlantic clear/moderately turbid MSI comparison; default-setting and masking effects.', '75 potential matchups; unequal valid subsets; abstract and discussion report inconsistent total scores, so those scores are not reproduced.'),
 'Brockmann2016': ('full text','ESA proceedings §§2–6; normal/extreme nets and out-of-scope tests', 'C2RCC/C2X network families and separate range/spectral-scope checks.', 'Conference proceedings; no DOI verified; persistent ESA-hosted PDF used as identifier.'),
}

def write_csv(path, rows):
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
 records=json.loads((ROOT/'outputs/source_records.json').read_text())
 rows=[];bib=[];evidence=[]
 for r in records:
  m=r['crossref'];key=r['key'];level,sections,relevance,limits=NOTES[key]
  year=m['published']['date-parts'][0][0]
  title=m['title'][0]
  authors=' and '.join(a.get('family','')+', '+a.get('given','') for a in m['author'])
  venue=m['container-title'][0]
  identifier=r['doi'] or 'https://step.esa.int/docs/extra/Evolution%20of%20the%20C2RCC_LPS16.pdf'
  url='https://doi.org/'+r['doi'] if r['doi'] else identifier
  ptype='conference proceedings' if m['type']=='proceedings-article' else 'journal article'
  fields={'author':authors,'title':'{'+title+'}','year':year,('booktitle' if ptype=='conference proceedings' else 'journal'):venue,'url':url}
  if r['doi']:fields['doi']=r['doi']
  for src,out in [('volume','volume'),('issue','number'),('page','pages'),('article-number','eid')]:
   if m.get(src):fields[out]=str(m[src]).replace('–','--')
  # Crossref sometimes supplies only a first page or a proceedings index.
  # These corrections were checked against the publication or primary abstract.
  page_corrections={'Gordon1994':'443--452','Steinmetz2011':'9783--9800','Castagna2025':'2719--2743'}
  if key in page_corrections:fields['pages']=page_corrections[key]
  if key=='MainKnorn2017':
   fields.pop('pages',None);fields['volume']='10427';fields['eid']='1042704'
  if key=='Muller2026':fields['eid']='1710758'
  bib.append('@'+('inproceedings' if ptype=='conference proceedings' else 'article')+'{'+key+',\n'+''.join('  '+k+' = {'+str(v)+'},\n' for k,v in fields.items())+'}\n')
  rows.append(dict(citation_key=key,title=title,authors=authors,year=year,journal_or_source=venue,doi_or_identifier=identifier,publication_type=ptype,pdf_file_path=r.get('pdf_path',''),source_url=url,pdf_retrieval_url=r.get('pdf_url',''),full_text_availability='local PDF' if r.get('pdf_path') else ('publisher HTML; PDF unavailable' if key=='Wu2024' else 'abstract only; PDF unavailable'),verification_level=level,keywords='Sentinel-2; atmospheric correction; marine ecology',relevance=relevance,limitations=limits,inspected_sections=sections,metadata_source=r.get('metadata_source','Crossref DOI record; publication title/author inspection'),verification_date=r['checked'],pdf_sha256=r.get('pdf_sha256',''),storage_and_redistribution='Research library; PDFs excluded from Git and deliverable bundle; use original source for access'))
  evidence.append(dict(citation_key=key,evidence_level=level,inspected_passages=sections,supported_scope=relevance,limitation=limits))
 (ROOT/'library.bib').write_text('\n'.join(bib))
 write_csv(ROOT/'literature/references_index.csv',rows)
 write_csv(ROOT/'tables/evidence_matrix.csv',evidence)
 counts={'references':len(rows),'pdfs':sum(bool(r.get('pdf_path')) for r in records),'full_text_inspected':sum(NOTES[r['key']][0]=='full text' for r in records),'abstract_only':sum(NOTES[r['key']][0]=='abstract' for r in records),'search_date':'2026-10-20'}
 (ROOT/'outputs/library_summary.json').write_text(json.dumps(counts,indent=2))
 print(json.dumps(counts))

if __name__=='__main__':main()
