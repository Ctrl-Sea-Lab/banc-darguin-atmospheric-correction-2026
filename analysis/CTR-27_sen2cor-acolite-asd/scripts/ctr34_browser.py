#!/usr/bin/env python3
"""Bounded Firefox rendering checks for current report and exact embedded figure/caption fragments."""
import re,json,subprocess,tempfile,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];html=(P/'report.html').read_text();figs=re.findall(r'<figure\b.*?</figure>',html,re.S);assert len(figs)==3
assert html.count('data:image/png;base64,')==3
assert not re.search(r'<(?:script|link)[^>]*(?:src|href)="https?://',html)
styles=''.join(re.findall(r'<style\b.*?</style>',html,re.S));out=P/'outputs/ctr34_browser';out.mkdir(exist_ok=True)
def capture(url,name):
 with tempfile.TemporaryDirectory(prefix='ctr34-firefox-') as profile:
  subprocess.run(['firefox','--headless','--no-remote','--profile',profile,'--screenshot',str(out/name),'--window-size','1400,1100',url],check=True,timeout=45,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
capture((P/'report.html').as_uri(),'first-page.png')
with tempfile.TemporaryDirectory(prefix='ctr34-fragments-') as tmp:
 for name,fig in zip(['local-imagery','scl','current-spectra'],figs):
  p=Path(tmp)/(name+'.html');p.write_text('<!doctype html><html><head>'+styles+'</head><body>'+fig+'</body></html>');capture(p.as_uri(),name+'.png')
(P/'provenance/ctr34_browser.json').write_text(json.dumps({'report_html_sha256':hashlib.sha256((P/'report.html').read_bytes()).hexdigest(),'status':'rendered; manual visual inspection required','viewport':[1400,1100],'browser':subprocess.check_output(['firefox','--version'],text=True).strip(),'self_contained_images':3,'no_external_script_stylesheet':True,'screenshots':[{ 'path':str(p.relative_to(P)), 'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.glob('*.png'))],'scope':'first page and exact embedded image/caption fragments; not full-page automated usability or scientific review'},indent=2)+'\n')
print('Rendered first page and three exact figure/caption fragments')
