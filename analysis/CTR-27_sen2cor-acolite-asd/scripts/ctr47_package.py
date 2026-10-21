#!/usr/bin/env python3
"""Package exact committed specialist handoff; never include original raw data."""
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
P = Path(__file__).resolve().parents[1]


def main():
    paths = [P/'CTR47_HANDOFF.md']
    for folder, pattern in [('scripts','ctr47_*.py'), ('tables','ctr47_*.csv'),
                            ('provenance','ctr47_*.json'), ('outputs','ctr47_*.json')]:
        paths.extend((P/folder).glob(pattern))
    paths += [P/n for n in ['scripts/ctr42_extract.py', 'tables/ctr42_band_contract.csv',
                           'tables/ctr42_sources.csv', 'tables/station_crosswalk.csv',
                           'provenance/ctr42_scene_pair.json', 'provenance/ctr42_validation.json']]
    paths += [ROOT/n for n in ['pyproject.toml','uv.lock','renv.lock','scripts/check-env.sh',
                              'scripts/project-env.sh','scripts/bootstrap-env.sh','scripts/bootstrap-renv.R']]
    head = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    payload = {}
    for path in sorted(set(paths)):
        name = str(path.relative_to(ROOT))
        data = path.read_bytes()
        # Do not attach an uncommitted or modified scientific source as an exact revision.
        committed = subprocess.check_output(['git','show',head+':'+name],cwd=ROOT)
        assert committed == data, name
        payload[name] = data
    validation = json.loads((P/'provenance/ctr47_validation.json').read_text())
    assert validation['status'] == 'pass'
    manifest = dict(commit=head, branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),
                    baseline='3a2bf1b19e7f9f80b6830b8b0f056bbe6add2844',
                    scientific_approval='none; specialist handoff for independent validation',
                    original_raw_data_included=False,
                    files={n:dict(bytes=len(v),sha256=hashlib.sha256(v).hexdigest()) for n,v in payload.items()})
    payload['CTR47_REVISION_AND_MANIFEST.json'] = (json.dumps(manifest,indent=2)+'\n').encode()
    output = P/'outputs/CTR47-target-handoff.zip'
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name, data in sorted(payload.items()):
            entry=zipfile.ZipInfo(name,date_time=(2026,10,20,0,0,0))
            entry.compress_type=zipfile.ZIP_DEFLATED
            entry.external_attr=0o100644 << 16
            archive.writestr(entry,data)
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        for name, record in manifest['files'].items():
            assert hashlib.sha256(archive.read(name)).hexdigest()==record['sha256']
    print(json.dumps(dict(commit=head, path=str(output), bytes=output.stat().st_size,
                          sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                          verified_archive_files=len(payload)),indent=2))


if __name__=='__main__':
    main()
