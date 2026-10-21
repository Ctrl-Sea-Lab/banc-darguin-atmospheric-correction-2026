"""Save the recovery receipt document and explicit infrastructure dependency."""
import os,json,sys,shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from deliver import api,save,OUT,TASK
manifest=json.loads((OUT/'file_manifest.json').read_text())
body='''# CTR-55 delivery recovery

The saved scientific outputs are intact. Code, all tables, methods and provenance are now downloadable from CTR-60, and the downloaded package matches its local SHA-256. Full report, full-resolution figures and the raster archive remain preserved on the NAS; board access to those larger files is still unconfirmed. CTR-60 cannot yet be marked complete.

**Recovered artifact:** [CTR-55 code, tables and provenance](/api/attachments/2e1cae0f-f4cf-4279-b591-64531f13c23a/content?download=1). Attachment `2e1cae0f-f4cf-4279-b591-64531f13c23a`; work product `8d705646-554f-41b2-b287-9bba2b96d07a`. Upload HTTP 201; work-product creation HTTP 201; independent HTTP 200 download matched 113955 bytes and SHA-256 `f547770309135c6b8cd35ad9b1533376ccacc415460f9275df55152253112561`. The ZIP contains saved code, report source, methods, table contract, all tables, top-level provenance and hash manifests; it omits duplicated metadata snapshots, outputs/pairs.json, rendered report, images and rasters. Omitted files remain in the original investigation.

The existing [modelling CSV on CTR-55](/api/attachments/abea9a9d-32d8-445d-9d12-45cf99db513f/content?download=1) was confirmed by reading CTR-55 attachment and work-product records. Its work product is `4be3b355-24cc-44fe-aef6-660aa6c58cea`. No duplicate upload was made.

**Access blocker and action:** [CTR-61](/CTR/issues/CTR-61), assigned to Alan Turing, must restore a supported access path and return verified receipts for the full report, PNG/PDF and archive. Its initial plan is saved as revision `3bc3952f-352a-4d25-9f34-bb8fd6e12466`. The current project has `workspaces: []`, `primaryWorkspace: null`, and `codebase.workspaceId: null`; the recovery task has no execution workspace. Attempting to register the existing NAS root returned HTTP 403: `{"error":"Route not allowed: POST /api/projects/5fc298b7-b03d-4a03-b14f-25b3e66ccf85/workspaces"}`. No workspace binding or permission was changed; the denied operation was not retried. No invented workspace ID or unconfirmed file registration is used. This is an access-configuration blocker; the small artifact API is functioning.

Canonical investigation: `/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026/analysis/CTR-54_paired-reflectance-differences/`.

Scientific revision `1bbb23b3b94e775a60aa921f8c9c4f86f51926cb`, branch `ctr-55-paired-reflectance`; isolated worktree `/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026/.task-worktrees/CTR-55`. All file hashes below were recomputed during recovery, including the complete 2 GB raster archive. No scientific computations, dependency changes or raw-data writes occurred.

Exact file inventory (relative scientific paths resolve under the canonical investigation):

| File | Bytes | SHA-256 |
| --- | ---: | --- |
'''
for row in manifest:
 body+=f'| `{row["relativePath"]}` | {row["byteSize"]} | `{row["sha256"]}` |\n'
body+='''
The compact ZIP's absolute recovery path is `'''+str((OUT/'CTR55_code_tables.zip').resolve())+'''`. A durable copy of recovery evidence is stored under `/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026/analysis/CTR-60_artifact-recovery/`. The file_manifest.json there records every absolute path listed above. Existing scientific output manifests cover all individual raster/table/figure/source products.

The saved scientific handoff reports 22 paired acquisitions, 113 raster products, 12 source checks, 96 independent base-R temporal checks, full-grid validity and the 88-source exact-fill audit. These validations were not rerun in recovery. The saved descriptive differences do not establish atmospheric-correction accuracy or ecological change; missing March 2026 ACOLITE flags and lack of independent reference validation remain limitations.

Next: after CTR-61 returns real access receipts, record those receipts here, mark CTR-60 done and let automatic child/blocker completion wake CTR-55. Do not write across the task boundary to complete CTR-55 from CTR-60. CTR-55 will save its final handoff and release the existing modelling/writing/assembly chain. Scientific review remains CTR-59 after CTR-58. PI scientific approval is pending; no manuscript integration, merge or publication is authorized.

Delivery implementation: the supplied upload helper stopped before any request because `jq` was absent; the dependency-free Python uploader used the documented attachment and work-product endpoints with the run audit header, checked existing attachments, and performed no blind retry. No package was installed. Receipt and download verification JSON files are preserved with the recovery scripts.
'''
(OUT/'RECOVERY.md').write_text(body)
r=save('recovery_document_receipt.json',api('PUT',f'/api/issues/{TASK}/documents/recovery-delivery',{'title':'CTR-55 verified recovery receipts and remaining access blocker','format':'markdown','body':body,'baseRevisionId':None}))
assert r.get('status') in (200,201),r
b=r['body']; assert b.get('body')==body and b.get('latestRevisionId'),b
print(json.dumps({'status':r['status'],'key':b['key'],'latestRevisionId':b['latestRevisionId']}),flush=True)
comment='Recovered and download-verified [code, tables and provenance](/api/attachments/2e1cae0f-f4cf-4279-b591-64531f13c23a/content?download=1). Exact hashes, paths and receipts are saved in [recovery delivery](/CTR/issues/CTR-60#document-'+b['key']+'). Full report, figures and rasters remain preserved, but their board-access registration is blocked: this project has no workspace binding and this run is denied permission to create it (HTTP 403). [CTR-61](/CTR/issues/CTR-61), assigned to Alan, owns the verified access recovery. CTR-60 remains blocked until those receipts exist, then will complete to wake CTR-55. No scientific rerun or permission change; independent review and PI approval remain pending.'
s=save('blocked_status_receipt.json',api('PATCH',f'/api/issues/{TASK}',{'status':'blocked','blockedByIssueIds':['6f4a556f-9f40-40ea-bdb8-42b5f88143b3'],'comment':comment}))
assert s.get('status')==200,s
print(json.dumps({'status':s['status'],'issueStatus':s['body']['status'],'blockedBy':s['body'].get('blockedBy')}),flush=True)
durable=Path('/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026/analysis/CTR-60_artifact-recovery')
shutil.copytree(OUT,durable,dirs_exist_ok=True)
print('Saved durable recovery evidence: '+str(durable))
