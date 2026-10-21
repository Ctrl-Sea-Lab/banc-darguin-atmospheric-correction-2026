"""Create a compact offline copy of the full Quarto report without altering its content."""
from pathlib import Path
import hashlib
import json
import re
import zipfile
from html.parser import HTMLParser

A = Path(__file__).resolve().parents[1]
source = A / 'report.html'
rendered = source.read_text()
start = re.search(r'<main\b[^>]*>', rendered).start()
body = rendered[start:rendered.index('</main>', start)+7]
assert '<script' not in body
style = '''body{margin:0;background:#f4f6f7;color:#222;font:16px/1.6 system-ui,sans-serif}
main{max-width:1040px;padding:42px 48px;margin:20px auto;background:white}
h1{font-size:2rem;line-height:1.2}h2{margin-top:2.2rem;border-bottom:1px solid #ddd}
.subtitle{font-size:1.15rem;color:#555}.quarto-title-meta{font-size:.9rem;color:#555}
figure{margin:1.5rem 0}img,svg{max-width:100%;height:auto}figcaption{color:#555;font-size:.88rem}
table{border-collapse:collapse;width:100%;font-size:.86rem;font-variant-numeric:tabular-nums}
th,td{padding:.4rem;text-align:left;border-bottom:1px solid #ddd}code{overflow-wrap:anywhere}
pre{overflow:auto;background:#f5f5f5;padding:1rem}a{color:#1765a6}.code-copy-button,.anchorjs-link{display:none}
@media(max-width:700px){main{padding:20px 14px;margin:0}table{font-size:.7rem}}
@media print{body{background:white}main{padding:0;margin:0}}'''
portable = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Satellite–ASD reflectance matchups at Banc d’Arguin</title><style>'+style+'</style></head><body>'+body+'</body></html>\n'
target = A / 'report-portable.html'
target.write_text(portable)

class Audit(HTMLParser):
    def __init__(self): super().__init__(); self.text=[]; self.resources=[]
    def handle_data(self, data): self.text.append(data)
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if (k=='src' or (tag=='link' and k=='href')) and v and not v.startswith(('data:','#')):
                self.resources.append(v)

original=Audit();original.feed(body)
copy=Audit();copy.feed(portable[portable.index('<main'):portable.index('</main>')+7])
assert original.text==copy.text and not copy.resources
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record=dict(source='report.html',source_sha256=sha(source),
    portable='report-portable.html',portable_sha256=sha(target),
    report_main_content_preserved_byte_for_byte=True,report_text_identical=True,
    external_rendering_resources=copy.resources,scope='static offline presentation copy; no scientific changes')
audit=A/'provenance/ctr38_figure3_portable.json'
audit.write_text(json.dumps(record,indent=2)+'\n')
with zipfile.ZipFile(A/'outputs/CTR41_portable-final-report.zip','w',zipfile.ZIP_DEFLATED) as z:
    z.write(target,target.name)
    z.write(Path(__file__),'ctr38_figure3_portable.py')
    z.write(audit,audit.name)
print(json.dumps(record,indent=2))
