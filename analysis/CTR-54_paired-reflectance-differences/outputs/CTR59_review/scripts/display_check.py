"""Use installed Chrome to measure actual rendered figures at desktop widths."""
import asyncio,base64,json,subprocess,tempfile,time,urllib.request,sys
from pathlib import Path
import websockets
ROOT=Path(sys.argv[1]).resolve()
OLD=Path(sys.argv[2]).resolve()
async def main():
 with tempfile.TemporaryDirectory(prefix='ctr58-chrome-') as tmp:
  p=subprocess.Popen(['/opt/google/chrome/chrome','--headless','--no-sandbox','--disable-dev-shm-usage','--disable-gpu','--hide-scrollbars','--remote-debugging-port=0','--user-data-dir='+tmp,'about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  try:
   portfile=Path(tmp)/'DevToolsActivePort'
   for _ in range(100):
    if portfile.exists(): break
    await asyncio.sleep(.1)
   port=portfile.read_text().splitlines()[0]
   pages=json.load(urllib.request.urlopen('http://127.0.0.1:'+port+'/json'))
   async with websockets.connect(next(page for page in pages if page['type']=='page')['webSocketDebuggerUrl'],max_size=50_000_000) as ws:
    n=0
    async def send(method,params={}):
     nonlocal n;n+=1; id=n
     await ws.send(json.dumps({'id':id,'method':method,'params':params}))
     while True:
      r=json.loads(await asyncio.wait_for(ws.recv(),timeout=30))
      if r.get('id')==id:
       if 'error' in r: raise RuntimeError(r['error'])
       return r.get('result',{})
    async def evaluate(expr):
     r=await send('Runtime.evaluate',{'expression':expr,'returnByValue':True});return r['result'].get('value')
    out=[]
    for width in [1440,1920,390]:
     for label,path in [('previous',OLD),('candidate',ROOT/'report.html')]:
      await send('Emulation.setDeviceMetricsOverride',{'width':width,'height':1080,'deviceScaleFactor':1,'mobile':False})
      await send('Page.navigate',{'url':path.as_uri()})
      for _ in range(100):
       if await evaluate("document.readyState==='complete' && document.images.length>0 && Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)"):break
       await asyncio.sleep(.1)
      await asyncio.sleep(.2)
      metrics=await evaluate("JSON.stringify({viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,images:Array.from(document.querySelectorAll('main img')).map(i=>({alt:i.alt.slice(0,80),width:i.getBoundingClientRect().width,height:i.getBoundingClientRect().height,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight}))})")
      metrics=json.loads(metrics);metrics['label']=label;out.append(metrics)
      if label=='candidate':
       await evaluate("document.querySelector('#fig-maps').scrollIntoView({block:'start'})")
       shot=await send('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})
       (ROOT/f'provenance/ctr59_display_{width}.png').write_bytes(base64.b64decode(shot['data']))
    (ROOT/'provenance/ctr59_display.json').write_text(json.dumps(out,indent=2)+'\n')
    for width in [1440,1920]:
     old=next(r for r in out if r['viewport']==width and r['label']=='previous')['images']
     new=next(r for r in out if r['viewport']==width and r['label']=='candidate')['images']
     assert new[0]['width']>old[-1]['width'], (width,old,new)
    for r in out:
     if r['label']=='candidate': assert r['scrollWidth']<=r['viewport'],r
    print(json.dumps(out,indent=2))
  finally:p.terminate();p.wait(timeout=20)
asyncio.run(main())
