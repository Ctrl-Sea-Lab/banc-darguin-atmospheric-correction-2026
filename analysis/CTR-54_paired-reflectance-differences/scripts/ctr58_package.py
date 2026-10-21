"""Check embedded HTML or package a clean exact candidate without scientific reruns."""
from pathlib import Path
import argparse, csv, hashlib, json, shutil, subprocess, zipfile
from html.parser import HTMLParser
from urllib.parse import unquote

A=Path(__file__).resolve().parents[1]
REPO=A.parents[1]

def digest(data): return hashlib.sha256(data).hexdigest()

class Audit(HTMLParser):
    def __init__(self): super().__init__(); self.images=[];self.assets=[];self.links=[];self.ids=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='img':self.images.append(a)
        if tag in ['img','script'] and a.get('src'):self.assets.append(a['src'])
        if tag=='link' and a.get('rel')=='stylesheet':self.assets.append(a['href'])
        if tag=='a' and a.get('href'):self.links.append(a['href'])

def check_html():
    data=(A/'report.html').read_bytes();p=Audit();p.feed(data.decode())
    assert len(p.images)==2 and all(i.get('alt') for i in p.images)
    assert all(x.startswith('data:') for x in p.assets),p.assets
    local=[]
    for link in p.links:
        if link.startswith(('http:','https:','mailto:','#','data:','javascript:')):continue
        path=unquote(link.split('#')[0]);assert (A/path).is_file(),path;local.append(path)
    citations=[i for i in p.ids if i.startswith('ref-')];assert len(citations)==6
    assert not any(x in data.decode() for x in ['<span class="quarto-unresolved-ref"','@fig-','@tbl-'])
    assert digest(data)=='a1ba565a3729a1b64e25f62c2c40979d9eaa4a71e8814be76d5e01fa38c0db84'
    result={'status':'pass','html_sha256':digest(data),'embedded_images':2,'all_images_have_alt':True,'external_or_relative_render_assets':0,'bibliography_entries':len(citations),'full_resolution_links_verified':local,'standalone_scope':'Both displayed figures, styles and scripts embedded; optional full-resolution downloads are separate files also included in review archive.'}
    (A/'provenance/ctr58_html_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--check-only',action='store_true');ap.add_argument('--output',type=Path);ap.add_argument('--guard-report',type=Path);args=ap.parse_args()
    if args.check_only:print(json.dumps(check_html(),indent=2));return
    assert args.output is not None,'--output is required'
    # Packaging never mutates the source candidate.
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=REPO).strip(),'Commit candidate first'
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()
    assert args.guard_report is not None,'--guard-report is required for final packaging'
    guard=json.loads(args.guard_report.read_text())
    assert guard['candidate_commit']==head and guard['status']=='pass'
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    prefix=A.relative_to(REPO).as_posix()
    files=subprocess.check_output(['git','ls-files',prefix],cwd=REPO,text=True).splitlines()
    # Include exact repository environment and restore/render tooling, excluding manuscript.
    support=['pyproject.toml','uv.lock','renv.lock','.python-version','.Rprofile','renv/activate.R','renv/settings.json','config/toolchain.yml','scripts/bootstrap-env.sh','scripts/bootstrap-renv.R','scripts/check-env.sh','scripts/project-env.sh','scripts/render-analysis.sh','scripts/figure_io.py','tests/environment/validate_lockfiles.py']
    files=sorted(set(files+support)); manifest=[]
    for rel in files:
        p=REPO/rel;data=p.read_bytes()
        gitdata=subprocess.check_output(['git','show',head+':'+rel],cwd=REPO)
        assert data==gitdata,rel
        assert not any(s in rel.split('/') for s in ['raw','.venv','.cache','.quarto'])
        assert p.suffix not in ['.tif','.bin','.zip','.rds'] or rel.endswith('ctr56_gam_models.rds'),rel
        manifest.append({'path':rel,'bytes':len(data),'sha256':digest(data)})
    record={'schema':'ctr58.review-package.v1','candidate_commit':head,'pi_contribution_guard':guard,'pr_base_branch':'ctr-22-project-initialization','source_audit_commit':'6b943796215162440368c8d8ace3539eefbd7827','writer_commit':'f79b98cdd810c2ffada1479dd0bddc3d34e22341','files':manifest,'raw_data_included':False,'scientific_rasters_included':False,'scientific_products':'Permanent NAS investigation outputs/paired_differences and outputs/temporal; 113 file hashes verified in provenance/ctr58_validation.json','review':'pending CTR-59','pi_scientific_approval':'pending','integration_merge_publication':'not authorized'}
    for rel in files:
        p=Path(rel)
        if rel.startswith(prefix+'/'):
            target=out/p.relative_to(prefix);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(REPO/rel,target)
    (out/'delivery.json').write_text(json.dumps(record,indent=2)+'\n')
    # ZIP keeps repository-relative paths so reproduction tools retain their context.
    for name, selected in [('CTR58_review_package.zip',files),('CTR58_source_provenance.zip',[r for r in files if not r.endswith(('.png','.pdf','.html','.rds'))])]:
        with zipfile.ZipFile(out/name,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for rel in selected:
                info=zipfile.ZipInfo(rel,date_time=(2026,10,20,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(0o100755 if rel.endswith('.sh') else 0o100644)<<16;z.writestr(info,(REPO/rel).read_bytes())
            z.writestr('CTR58_delivery.json',json.dumps(record,indent=2)+'\n')
        with zipfile.ZipFile(out/name) as z:assert z.testzip() is None
    deliverables=[]
    for name in ['report.html','CTR58_review_package.zip','CTR58_source_provenance.zip','figures/generated/paired_reflectance_maps_v2.png','figures/generated/paired_reflectance_maps_v2.pdf','figures/generated/ctr56_temporal_gam.png','figures/generated/ctr56_temporal_gam.pdf','delivery.json']:
        p=out/name;deliverables.append({'path':name,'bytes':p.stat().st_size,'sha256':digest(p.read_bytes())})
    receipt={'candidate_commit':head,'deliverables':deliverables,'source_and_output_manifest':'delivery.json'}
    (out/'artifact_hashes.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
