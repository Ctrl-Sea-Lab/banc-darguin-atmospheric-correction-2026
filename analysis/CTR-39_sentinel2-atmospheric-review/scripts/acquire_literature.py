"""Stage bibliographic refreshes without replacing verified records.

The authoritative saved manifest is outputs/source_records.json. To restore
manifest-listed public PDFs, run restore_pdfs.py; existing files and changed
remote versions are never silently overwritten. This script is optional and
writes fresh Crossref records to a separate candidate directory for inspection.
"""
import json
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]

def main():
    destination = ROOT/'outputs/metadata_refresh_candidates'
    destination.mkdir(exist_ok=True)
    for record in json.loads((ROOT/'outputs/source_records.json').read_text()):
        if not record['doi']: continue
        path=destination/(record['key']+'.json')
        if path.exists():
            print(record['key'], 'candidate exists; preserved')
            continue
        try:
            request=urllib.request.Request('https://api.crossref.org/works/'+record['doi'],headers={'User-Agent':'CtrlSea-LiteratureReview/1.0'})
            with urllib.request.urlopen(request,timeout=30) as response:
                result=json.load(response)['message']
            assert result['DOI'].lower()==record['doi'].lower()
            with path.open('x') as handle:json.dump(result,handle,indent=2)
            print(record['key'], 'candidate staged; source manifest unchanged')
        except Exception as exc:
            print(record['key'], 'unavailable:',str(exc))

if __name__=='__main__':main()
