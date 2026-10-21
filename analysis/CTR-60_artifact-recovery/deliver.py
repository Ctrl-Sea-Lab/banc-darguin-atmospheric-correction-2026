"""Recover small immutable artifacts using the injected Paperclip API; never retries writes."""
import os, json, hashlib, urllib.request, urllib.error, uuid
from pathlib import Path
OUT=Path(__file__).resolve().parent
BASE=os.environ['PAPERCLIP_API_URL']
TASK=os.environ['PAPERCLIP_TASK_ID']
HEAD={'Authorization':'Bearer '+os.environ['PAPERCLIP_API_KEY'],'X-Paperclip-Run-Id':os.environ['PAPERCLIP_RUN_ID']}
def api(method,path,body=None,content_type='application/json',timeout=30):
    headers=dict(HEAD)
    if body is not None:
        headers['Content-Type']=content_type
        if not isinstance(body,bytes): body=json.dumps(body).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(BASE+path,data=body,headers=headers,method=method),timeout=timeout) as r:
            return {'status':r.status,'body':json.load(r)}
    except urllib.error.HTTPError as e:
        return {'status':e.code,'body':e.read().decode()}
    except Exception as e:
        return {'error':type(e).__name__+': '+str(e),'outcome':'indeterminate' if method!='GET' else 'read_failed'}
def save(name,result):
    (OUT/name).write_text(json.dumps(result,indent=2)+'\n')
    return result
if __name__=='__main__':
    p=OUT/'CTR55_code_tables.zip'
    raw=p.read_bytes(); sha=hashlib.sha256(raw).hexdigest()
    before=save('attachments_before.json',api('GET',f'/api/issues/{TASK}/attachments'))
    assert before['status']==200,before
    matches=[a for a in before['body'] if a.get('sha256')==sha and a.get('byteSize')==len(raw)]
    if matches:
        attach={'status':200,'body':matches[0],'reused':True}
    else:
        boundary='----recovery'+uuid.uuid4().hex
        data=(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{p.name}"\r\nContent-Type: application/zip\r\n\r\n'.encode()+raw+f'\r\n--{boundary}--\r\n'.encode())
        attach=api('POST',f'/api/companies/{os.environ["PAPERCLIP_COMPANY_ID"]}/issues/{TASK}/attachments',data,'multipart/form-data; boundary='+boundary)
    save('code_tables_attachment_receipt.json',attach)
    print(json.dumps(attach),flush=True)
    if attach.get('status') not in (200,201): raise SystemExit(1)
    a=attach['body']; assert a['sha256']==sha and a['byteSize']==len(raw)
    wp=save('code_tables_work_product_receipt.json',api('POST',f'/api/issues/{TASK}/work-products',{'type':'artifact','provider':'paperclip','title':'CTR-55 code, tables and provenance','status':'ready_for_review','reviewState':'needs_board_review','isPrimary':True,'summary':'Compact package of saved code, tables and provenance; no scientific rerun. Independent review and PI approval pending.','metadata':{'attachmentId':a['id']}}))
    print(json.dumps(wp),flush=True)
