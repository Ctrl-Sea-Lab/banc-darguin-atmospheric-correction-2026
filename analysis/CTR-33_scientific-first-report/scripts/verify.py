#!/usr/bin/env python3
"""Evidence-preservation and standalone-report checks, without numerical reruns."""
from pathlib import Path
import argparse
import base64
import csv
import hashlib
from html.parser import HTMLParser
import json
import re
import subprocess

P = Path(__file__).resolve().parents[1]
ROOT = P.parents[1]
SOURCE = ROOT / 'analysis/CTR-27_sen2cor-acolite-asd'
BASE = '9f0f06d2b5958b35de82adbca1577e4c384ae846'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--raw-root', type=Path, help='Existing source checkout; read-only small-input hashes and raw stats')
args = parser.parse_args()

def sha(data):
    return hashlib.sha256(data).hexdigest()

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

def rows(name):
    with (SOURCE / 'tables' / name).open() as f:
        return list(csv.DictReader(f))

files = git('ls-tree', '-r', '--name-only', BASE, 'analysis/CTR-27_sen2cor-acolite-asd').decode().splitlines()
preserved = []
for name in files + ['uv.lock', 'renv.lock']:
    old = git('show', f'{BASE}:{name}')
    new = (ROOT / name).read_bytes()
    assert old == new, name
    preserved.append({'path': name, 'bytes': len(new), 'sha256': sha(new), 'baseline_equal': True})
(P / 'outputs/source_preservation.json').write_text(json.dumps(preserved, indent=2) + '\n')

qmd = (P / 'report.qmd').read_text()
source_qmd = (SOURCE / 'report.qmd').read_text()
source_body = source_qmd.split('---', 2)[2].strip()
blocks = {m[2]: m[3].strip() for m in re.finditer(
    r'(?m)^(#{1,3}) (.+)\n([\s\S]*?)(?=^#{1,3} |\Z)', source_body)}
with (P / 'tables/content_map.csv').open() as f:
    mapping = list(csv.DictReader(f))
assert {r['baseline_heading'] for r in mapping} == set(blocks)
assert len(mapping) == len(blocks)
for row in mapping:
    content = blocks[row['baseline_heading']]
    assert sha(content.encode()) == row['body_sha256_before_path_rebase']
    rebased = content.replace('](figures/', '](../CTR-27_sen2cor-acolite-asd/figures/')
    if 'figures/srf-coverage.png)' in rebased:
        without_added_alt = re.sub(r'(srf-coverage\.png\))\{fig-alt="[^"]+"\}', r'\1', qmd)
        assert rebased in without_added_alt, row['baseline_heading']
    else:
        assert rebased in qmd, row['baseline_heading']

summary = qmd.split('## Scientific summary\n\n', 1)[1].split('\n\n[Findings]', 1)[0]
assert 150 <= len(summary.split()) <= 250
diff = rows('aoi_paired_differences.csv')
assert len(diff) == 6
for r in diff:
    token = f"{float(r['mean']):.5f}".replace('-', '−')
    assert token in summary, token
    assert float(r['maximum']) < 0
    assert r['sign'] == 'ACOLITE minus operational L2A'
    assert int(r['n']) == {'Arel': 730, 'Iwik': 733}[r['AOI']]
field = rows('field_spectral_summary.csv')
assert len(field) == 15 and all(int(r['n']) == 501 for r in field)
for station in ['AC05', 'AC06']:
    val = next(r['mean'] for r in field if r['station_id'] == station)
    assert f'{float(val):.5f}' in qmd
assert f"{min(float(r['minimum']) for r in field):.5f}" in summary
assert f"{max(float(r['maximum']) for r in field):.5f}" in summary
ledger = rows('proposed_matchups.csv')
assert len(ledger) == 165
assert all(r['include_primary'] == r['paired_valid'] == 'False' for r in ledger)
assert all(not r[k] for r in ledger for k in [
    'asd_band_reflectance', 'satellite_acolite_reflectance', 'satellite_sen2cor_reflectance'])

class Inventory(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
        self.external_render_assets = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'img':
            self.images.append(attrs)
            if not attrs.get('src', '').startswith('data:'):
                self.external_render_assets.append(attrs.get('src'))
        if tag in ['script', 'link']:
            url = attrs.get('src') if tag == 'script' else attrs.get('href')
            if url and not url.startswith(('data:', '#')):
                self.external_render_assets.append(url)

    def handle_data(self, data):
        self.text.append(data)

html = (P / 'report.html').read_text()
inventory = Inventory(); inventory.feed(html)
assert not inventory.external_render_assets, inventory.external_render_assets
embedded = {}
for img in inventory.images:
    data = base64.b64decode(img['src'].split(',', 1)[1])
    embedded[sha(data)] = img
captions = []
rendered_text = ' '.join(' '.join(inventory.text).split())
for caption, filename in re.findall(r'!\[([^\]]+)\]\((figures/[^)]+)\)', source_qmd):
    path = SOURCE / filename
    digest = sha(path.read_bytes())
    assert digest in embedded, filename
    assert ' '.join(caption.split()) in rendered_text, filename
    captions.append({'source_figure': str(path.relative_to(ROOT)), 'sha256': digest,
                     'embedded_bytes_identical': True, 'original_caption_present': True,
                     'caption': caption, 'html_alt': embedded[digest].get('alt')})
assert len(captions) == len(inventory.images) == 5
assert all(img.get('alt') for img in inventory.images), 'Every figure needs alt text'
(P / 'outputs/figure_checks.json').write_text(json.dumps(captions, indent=2) + '\n')

raw_result = None
if args.raw_root:
    raw_root = args.raw_root.resolve()
    raw_before = json.loads((P / 'provenance/raw_stats_before.json').read_text())
    after = {str(p.relative_to(raw_root)): [p.stat().st_size, p.stat().st_mtime_ns]
             for p in (raw_root / 'data/raw').rglob('*') if p.is_file()}
    assert after == raw_before, 'Raw size/mtime snapshot changed'
    source_run = json.loads((SOURCE / 'provenance/run.json').read_text())
    descriptive = json.loads((SOURCE / 'provenance/descriptive_run.json').read_text())
    expected = {r['path']: r['sha256'] for r in source_run['inputs']
                if r.get('hash_scope') == 'whole_file'}
    expected.update({r['path']: r['sha256'] for r in descriptive['used_input_hashes']})
    checked = []
    for name, expected_sha in expected.items():
        path = raw_root / name
        if not name.startswith('data/raw/'):
            continue
        actual = sha(path.read_bytes())
        assert actual == expected_sha, name
        checked.append({'path': name, 'sha256': actual, 'baseline_equal': True})
    after_hashes = {str(p.relative_to(raw_root)): [p.stat().st_size, p.stat().st_mtime_ns]
                    for p in (raw_root / 'data/raw').rglob('*') if p.is_file()}
    assert after_hashes == raw_before
    raw_result = {'raw_files_stat_unchanged': len(after),
                  'small_input_full_hashes_verified': checked,
                  'raster_reads': 0, 'whole_scene_hashes_computed': False}

previous = P / 'provenance/preservation.json'
if raw_result is None and previous.exists():
    raw_result = json.loads(previous.read_text()).get('read_only_input_checks')
result = {
    'baseline_commit': BASE,
    'source_files_and_locks_byte_identical': len(preserved),
    'all_source_numerical_outputs_preserved': True,
    'source_report_and_generator_unchanged': True,
    'source_body_blocks_preserved': len(blocks),
    'summary_word_count': len(summary.split()),
    'summary_magnitudes_checked_against_existing_tables': True,
    'embedded_images_byte_identical_to_source': len(captions),
    'original_figure_captions_present': True,
    'all_five_images_have_alt_text': True,
    'external_render_assets': inventory.external_render_assets,
    'report_qmd_sha256': sha(qmd.encode()),
    'report_html_sha256': sha(html.encode()),
    'read_only_input_checks': raw_result,
    'scientific_reanalysis': 'none; numerical scripts not rerun',
    'validation_limit': 'author preservation/presentation checks; independent scientific and editorial review pending',
}
previous.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: v for k, v in result.items() if k != 'read_only_input_checks'}, indent=2))
