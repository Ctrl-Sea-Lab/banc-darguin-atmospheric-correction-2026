#!/usr/bin/env python3
"""Capture first page and exact embedded figure/caption fragments with Firefox."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import tempfile

P = Path(__file__).resolve().parents[1]
html_path = P / 'report.html'
html = html_path.read_text()
figures = re.findall(r'<figure\b.*?</figure>', html, re.S)
assert len(figures) == 5
styles = ''.join(re.findall(r'<style\b.*?</style>', html, re.S))
out = P / 'outputs/browser-checks'
out.mkdir(exist_ok=True)

def capture(url, name):
    subprocess.run(['firefox', '--headless', '--screenshot', str(out / name),
                    '--window-size', '1400,1100', url], check=True, timeout=45)

capture(html_path.as_uri(), 'first-page.png')
with tempfile.TemporaryDirectory(prefix='ctr33-browser-') as directory:
    for name, figure in zip(['paired-differences', 'product-scatter', 'field-spectra', 'station-map'], figures[:4]):
        check = Path(directory) / (name + '.html')
        check.write_text('<!doctype html><html><head>' + styles + '</head><body>'
                         '<h2>Retained figure and caption: ' + name + '</h2>' + figure + '</body></html>')
        capture(check.as_uri(), name + '.png')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

result = {
    'report_html_sha256': digest(html_path),
    'viewport': [1400, 1100],
    'browser': subprocess.check_output(['firefox', '--version'], text=True).strip(),
    'first_page': 'Full final report opened locally; summary visible before research question',
    'principal_figures': 'Four exact embedded figure/caption DOM fragments, with report CSS; no image changes',
    'limitation': 'Fragment images verify rendering; this is not automated full-page scrolling or independent editorial review',
    'screenshots': [{'path': str(p.relative_to(P)), 'sha256': digest(p)} for p in sorted(out.glob('*.png'))],
}
(P / 'provenance/browser_checks.json').write_text(json.dumps(result, indent=2) + '\n')
print('Captured final report first page and four exact figure/caption fragments')
