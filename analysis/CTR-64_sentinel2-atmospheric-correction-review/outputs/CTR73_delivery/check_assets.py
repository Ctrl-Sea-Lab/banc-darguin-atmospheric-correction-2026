from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit,unquote
import re,json
ROOT=Path('/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026')
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.ids=set()
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.add(a['id'])
  for attr in ['href','src','poster']:
   if attr in a:self.links.append({'tag':tag,'attribute':attr,'url':a[attr]})
def check(folder):
 p=Parser();p.feed((folder/'report.html').read_text());rows=[]
 for x in p.links:
  u=urlsplit(x['url'])
  if u.scheme or u.netloc or not u.path:continue
  path=(folder/unquote(u.path)).resolve();rows.append({**x,'resolved':str(path),'exists':path.is_file()})
 source=[]
 for f in ['report.qmd','review.md']:
  if not (folder/f).exists():continue
  s=(folder/f).read_text()
  urls=re.findall(r'\]\(([^\s)]+)',s)+re.findall(r'{{<\s*include\s+([^\s>]+)',s)
  for url in urls:
   u=urlsplit(url)
   if u.scheme or u.netloc or not u.path:continue
   path=(folder/unquote(u.path)).resolve();source.append({'source':f,'url':url,'resolved':str(path),'exists':path.is_file()})
 for f in ['_quarto.yml','report.qmd','task.yml','report.css']:
  if f=='report.css' and not (folder/f).exists():continue
  assert (folder/f).is_file(),f
 for d in ['scripts','figures','tables','outputs','provenance']:assert (folder/d).is_dir(),d
 return {'directory':str(folder),'html_local_assets':rows,'source_local_assets':source,'missing':[x for x in rows+source if not x['exists']],'html_resources_embedded':not any(x['tag'] in ['img','script','link'] for x in rows)}
if __name__=='__main__':
 import sys
 folder=ROOT/sys.argv[1];d=check(folder);print(json.dumps(d,indent=2));sys.exit(bool(d['missing']))
