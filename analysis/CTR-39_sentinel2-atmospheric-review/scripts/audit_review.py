"""Audit the revision without treating the previous scientific verdict as current."""
import csv
import hashlib
import json
import pathlib
import re
import subprocess
import unicodedata
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]

def normalized(value):
    return re.sub(r'[^a-z0-9 ]', ' ', unicodedata.normalize('NFKD',value).encode('ascii','ignore').decode().lower())

def main():
    records=json.loads((ROOT/'outputs/source_records.json').read_text())
    index=list(csv.DictReader((ROOT/'literature/references_index.csv').open()))
    keys=[r['key'] for r in records]
    assert len(keys)==len(set(keys))==27
    dois=[r['doi'].lower() for r in records if r['doi']]
    assert len(dois)==len(set(dois))
    assert set(keys)=={r['citation_key'] for r in index}
    bibkeys=set(re.findall(r'@\w+\s*\{([^,]+),',(ROOT/'library.bib').read_text()))
    assert bibkeys==set(keys)
    body=(ROOT/'literature/literature_review.qmd').read_text()
    cited=set(re.findall(r'@([A-Za-z][A-Za-z0-9]+)',body))
    assert cited<=bibkeys, cited-bibkeys
    assert set(json.loads((ROOT/'outputs/intertidal_notes.json').read_text()))<=cited
    html=(ROOT/'report.html').read_text()
    for key in cited: assert 'id="ref-'+key+'"' in html,key
    assert 'citation-not-found' not in html
    assert 'exposed intertidal sediment' in html.lower()
    pdf_checks=[]
    for r in records:
        assert r['crossref']['author'] and r['crossref']['title']
        if not r.get('pdf_path'): continue
        path=ROOT/r['pdf_path']; data=path.read_bytes()
        assert data.startswith(b'%PDF-')
        assert hashlib.sha256(data).hexdigest()==r['pdf_sha256']
        first=' '.join((ROOT/r['text_path']).read_text().split('\f')[:3])
        title_words={w for w in normalized(r['crossref']['title'][0]).split() if len(w)>3}
        observed=set(normalized(first).split())
        overlap=len(title_words&observed)/len(title_words)
        assert overlap>.70,(r['key'],overlap)
        assert subprocess.run(['git','check-ignore',str(path.relative_to(REPO))],cwd=REPO,capture_output=True).returncode==0
        pdf_checks.append(dict(key=r['key'],pdf=r['pdf_path'],sha256=r['pdf_sha256'],title_token_overlap=round(overlap,3),git_ignored=True))
    assert len(pdf_checks)==24
    for rel,sha in json.loads((ROOT/'provenance/protected_before.json').read_text()).items():
        assert hashlib.sha256((REPO/rel).read_bytes()).hexdigest()==sha,rel
        assert (REPO/rel).read_bytes()==subprocess.check_output(['git','show','HEAD:'+rel],cwd=REPO),rel
    for rel,sha in json.loads((ROOT/'provenance/previous-water-review/snapshot_hashes.json').read_text()).items():
        assert hashlib.sha256((ROOT/'provenance/previous-water-review'/rel).read_bytes()).hexdigest()==sha,rel
    class InspectHTML(HTMLParser):
        def __init__(self): super().__init__();self.tables=0
        def handle_starttag(self,tag,attrs):
            if tag=='table': self.tables+=1
    parser=InspectHTML();parser.feed(html);assert parser.tables==2,parser.tables
    result=dict(result='passed',citations_resolved=len(cited),library_references=len(records),unique_dois=len(dois),valid_identity_checked_ignored_pdfs=len(pdf_checks),new_article_pdfs=9,rendered_comparison_tables=parser.tables,protected_root_files_unchanged=True,previous_snapshot_hashes_verified=True,pdf_checks=pdf_checks,limitations='Automated consistency checks supplement critical source inspection. New intertidal revision requires independent review; earlier CTR-40 verdict does not cover it. No PI scientific approval, integration, merge or publication is implied.')
    (ROOT/'outputs/audit_results.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k!='pdf_checks'},indent=2))

if __name__=='__main__': main()
