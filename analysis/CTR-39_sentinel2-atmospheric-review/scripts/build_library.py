"""Rebuild the task-local library, retaining verified original metadata and keys."""
import csv
import json
import pathlib
import runpy

ROOT = pathlib.Path(__file__).resolve().parents[1]

def write_csv(path, rows):
    with path.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

def main():
    notes = runpy.run_path(str(ROOT/'provenance/previous-water-review/scripts/build_library.py'))['NOTES']
    notes.update(json.loads((ROOT/'outputs/intertidal_notes.json').read_text()))
    records = json.loads((ROOT/'outputs/source_records.json').read_text())
    rows, bib, evidence = [], [], []
    for r in records:
        m, key = r['crossref'], r['key']
        level, sections, relevance, limits = notes[key]
        year = m.get('published', m.get('issued', {})).get('date-parts', [['']])[0][0]
        title = m['title'][0]
        authors = ' and '.join(a.get('family','')+', '+a.get('given','') for a in m['author']).rstrip(', ')
        venue = m['container-title'][0]
        webpage = m['type'] == 'webpage'
        identifier = r['doi'] or r.get('source_url', 'https://step.esa.int/docs/extra/Evolution%20of%20the%20C2RCC_LPS16.pdf')
        url = 'https://doi.org/'+r['doi'] if r['doi'] else identifier
        ptype = 'technical web documentation' if webpage else ('conference proceedings' if m['type']=='proceedings-article' else 'journal article')
        fields = {'author': '{Copernicus}' if webpage else authors, 'title':'{'+title+'}', 'url':url}
        if year: fields['year'] = year
        if not webpage: fields['booktitle' if ptype=='conference proceedings' else 'journal'] = venue
        else: fields.update(urldate=r['checked'], note='Undated official technical documentation; accessed 20 October 2026')
        if r['doi']: fields['doi'] = r['doi']
        for src, out in [('volume','volume'),('issue','number'),('page','pages'),('article-number','eid')]:
            if m.get(src): fields[out]=str(m[src]).replace('–','--')
        corrections = {'Gordon1994':'443--452','Steinmetz2011':'9783--9800','Castagna2025':'2719--2743'}
        if key in corrections: fields['pages'] = corrections[key]
        if key=='MainKnorn2017': fields.pop('pages',None); fields.update(volume='10427',eid='1042704')
        if key=='Muller2026': fields['eid']='1710758'
        if key=='Daggers2020': fields['eid']='392'
        entry_type = 'misc' if webpage else ('inproceedings' if ptype=='conference proceedings' else 'article')
        bib.append('@'+entry_type+'{'+key+',\n'+''.join('  '+k+' = {'+str(v)+'},\n' for k,v in fields.items())+'}\n')
        availability = 'local PDF' if r.get('pdf_path') else ('official HTML; page PDF unavailable' if webpage else ('publisher HTML; PDF unavailable' if key=='Wu2024' else 'abstract only; PDF unavailable'))
        rows.append(dict(citation_key=key,title=title,authors=authors,year=year,journal_or_source=venue,doi_or_identifier=identifier,publication_type=ptype,pdf_file_path=r.get('pdf_path',''),source_url=url,pdf_retrieval_url=r.get('pdf_url',''),full_text_availability=availability,verification_level=level,keywords='Sentinel-2; exposed intertidal sediment; atmospheric correction' if r.get('library_role','').startswith('new') or webpage else 'retained original evidence; see relevance and limitations',relevance=relevance,limitations=limits,inspected_sections=sections,metadata_source=r.get('metadata_source','Crossref DOI record; publication inspection'),verification_date=r['checked'],pdf_sha256=r.get('pdf_sha256',''),storage_and_redistribution='Research library; PDFs excluded from Git and source bundles; consult original source',library_role=r.get('library_role','retained original evidence')))
        evidence.append(dict(citation_key=key,evidence_level=level,inspected_passages=sections,supported_scope=relevance,limitation=limits,library_role=r.get('library_role','retained original evidence')))
    (ROOT/'library.bib').write_text('\n'.join(bib))
    write_csv(ROOT/'literature/references_index.csv', rows)
    write_csv(ROOT/'tables/evidence_matrix.csv', evidence)
    counts = dict(references=len(rows),original_references=17,new_research_articles=9,new_technical_web_references=1,pdfs=sum(bool(r.get('pdf_path')) for r in records),full_text_inspected=sum(notes[r['key']][0]=='full text' for r in records),abstract_only=sum(notes[r['key']][0]=='abstract' for r in records),search_date='2026-10-20')
    (ROOT/'outputs/library_summary.json').write_text(json.dumps(counts,indent=2))
    print(json.dumps(counts))

if __name__=='__main__': main()
