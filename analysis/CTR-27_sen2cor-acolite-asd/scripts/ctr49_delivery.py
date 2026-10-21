"""Render two science reports from verified values, using the CTR44 framework.
No extraction, radiometric transformation, or new inferential analysis.
"""
from pathlib import Path
from html.parser import HTMLParser
import csv, hashlib, html, importlib.util, json, math, subprocess, tempfile
A=Path(__file__).resolve().parents[1]; ROOT=A.parents[1]
VERIFIED='c4ac607826d6f1c1f3b0ea6040e6a8775ac6bb5b'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    with p.open(newline='') as f:return list(csv.DictReader(f))
def writejson(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def inputs():
    audit=json.loads((A/'provenance/ctr48_validation.json').read_text())
    for name,h in audit['output_sha256'].items():assert sha(A/'tables'/name)==h,name
    for p in [A/'tables'/n for n in audit['output_sha256']]+[A/'provenance/ctr48_validation.json',A/'CTR48_HANDOFF.md']:
        assert p.read_bytes()==subprocess.check_output(['git','show',f'{VERIFIED}:{p.relative_to(ROOT)}'],cwd=ROOT),p
    for ext in ['png','pdf','svg']:
        p=A/f'figures/generated/ctr38_figure3_reference.{ext}'
        assert p.read_bytes()==subprocess.check_output(['git','show',f'3a2bf1b19e7f9f80b6830b8b0f056bbe6add2844:{p.relative_to(ROOT)}'],cwd=ROOT)
    return audit
def summary_table():
    rows=read(A/'tables/ctr48_target_summary.csv')
    labels={r['target_id']:r['class_literal'] for r in read(A/'tables/ctr48_accounting.csv')}
    for r in rows:r['class_literal']=labels[r['target_id']]
    return rows
class Resources(HTMLParser):
    def __init__(self):super().__init__();self.external=[];self.images=[];self.figures=0
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='figure':self.figures+=1
        if tag=='img':self.images.append(attrs.get('src',''))
        for k,v in attrs.items():
            if (k=='src' or (tag=='link' and k=='href')) and v and not v.startswith(('data:','#')):self.external.append(v)
def portable(stem):
    content=(A/f'{stem}.html').read_text();start=content.index('<main');body=content[start:content.index('</main>',start)+7]
    style='body{font:16px/1.6 system-ui,sans-serif;color:#222;margin:24px auto;max-width:1060px;padding:0 24px}img{max-width:100%;height:auto}figure{margin:1.8rem 0}figcaption{font-size:.9rem;color:#444}table{border-collapse:collapse;width:100%;font-size:.85rem}th,td{padding:.35rem;border-bottom:1px solid #ddd;text-align:left}h2{margin-top:2.2rem}.anchorjs-link{display:none}'
    (A/f'{stem}-portable.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Reflectance differences at Banc d’Arguin</title><style>'+style+'</style></head><body>'+body+'</body></html>\n')
def validate():
    audit=inputs();expected=read(A/'tables/ctr48_plot_values.csv');checks=[]
    for mode in ['common','custom']:
        p=A/f'provenance/ctr49_target_spectra_{mode}_rows.csv';got=read(p)
        assert len(got)==len(expected)==108
        for g,e in zip(got,expected):
            assert g.keys()==e.keys()
            for k in e:
                if k in ['reflectance','wavelength_nm']:
                    assert math.isclose(float(g[k]),float(e[k]),rel_tol=0,abs_tol=1e-12)
                elif k in ['finite','SCL_flag']:assert g[k].lower()==e[k].lower()
                else:assert g[k]==e[k],(k,g,e)
        axes=read(A/f'provenance/ctr49_target_spectra_{mode}_axes.csv')
        assert {r['target_id'] for r in axes}=={f'T{i}' for i in range(1,7)}
        for ax in axes:
            values=[float(r['reflectance']) for r in expected if r['target_id']==ax['target_id']]
            assert float(ax['ymin'])<min(values)<=max(values)<float(ax['ymax'])
        if mode=='common':assert len({(r['ymin'],r['ymax']) for r in axes})==1
        else:assert len({(r['ymin'],r['ymax']) for r in axes})==6
        checks.append(f'{mode}: 108 original values, six panels, nine bands, both curves, all values inside limits')
    assert (A/'provenance/ctr49_target_spectra_common_rows.csv').read_bytes()==(A/'provenance/ctr49_target_spectra_custom_rows.csv').read_bytes()
    import base64,re
    for stem in ['report','report-custom','report-portable','report-custom-portable']:
        content=(A/f'{stem}.html').read_text();p=Resources();p.feed(content)
        assert not p.external,p.external
        assert p.figures==2 and len(p.images)==2,(stem,p.figures,len(p.images))
        assert base64.b64decode(p.images[0].split(',',1)[1])==(A/'figures/generated/ctr38_figure3_reference.svg').read_bytes()
        for term in ['CTR-','ctr4','SAFE','T28QCH','reproduc','processing log','source image','Appendix','20-day','B08: NA']:
            # Exclude embedded image bytes and HTML IDs/attributes from scientific prose audit.
            plain=re.sub('<[^>]*>',' ',content[content.index('<main'):content.index('</main>')])
            assert term.lower() not in plain.lower(),(stem,term)
        checks.append(f'{stem}: exactly two figures; self-contained; exact Figure 1 bytes; science-only prose')
    before=json.loads((A/'provenance/ctr49_before.json').read_text())
    changed=[]
    for name,h in before['tracked'].items():
        if sha(ROOT/name)!=h:changed.append(name)
    allowed={str((A/n).relative_to(ROOT)) for n in ['report.qmd','report.html','report-portable.html']}
    assert set(changed)==allowed,changed
    for name,h in before['unrelated'].items():assert sha(ROOT/name)==h,name
    checks.append(f'Preserved {len(before["tracked"])-len(changed)} prior tracked files and {len(before["unrelated"])} unrelated files; only three intended existing reports changed')
    writejson(A/'provenance/ctr49_validation.json',{'status':'pass','verified_revision':VERIFIED,'checks':checks,'counts':audit['counts'],'changed_existing_paths':changed,'input_sha256':audit['output_sha256'],'figure1_sha256':{ext:sha(A/f'figures/generated/ctr38_figure3_reference.{ext}') for ext in ['png','pdf','svg']},'serialization_absolute_tolerance':1e-12,'scientific_approval':False})
    print('\n'.join(checks))
def main():
    inputs()
    spec=importlib.util.spec_from_file_location('figure_io',ROOT/'scripts/figure_io.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    with tempfile.TemporaryDirectory(prefix='ctr49_',dir=A/'outputs') as tmp:
        r=subprocess.run([str(ROOT/'scripts/project-env.sh'),'Rscript',str(A/'scripts/ctr49_spectra.R'),str(A),tmp],cwd=ROOT,text=True,capture_output=True)
        (A/'provenance/ctr49_figure_render.txt').write_text(r.stdout+r.stderr);r.check_returncode()
        for p in Path(tmp).iterdir():
            if p.suffix in ['.svg','.pdf','.png']:mod.write_generated_bytes(A,p.name,p.read_bytes())
            elif p.suffix=='.csv':(A/'provenance'/p.name).write_bytes(p.read_bytes())
    rows=summary_table()
    keys=['target_id','class_literal','mean_signed','mean_absolute_difference','min_signed','max_signed']
    labels=['Target','Supplied class','Mean signed difference','Mean absolute difference','Minimum difference','Maximum difference']
    table='| '+' | '.join(labels)+' |\n|---|---|---:|---:|---:|---:|\n'
    for r in rows:
        table+='| '+' | '.join([r[keys[0]],r[keys[1]]]+[f'{float(r[k]):.6f}' for k in keys[2:]])+' |\n'
    template=(A/'scripts/ctr49_report_template.md').read_text().replace('SUMMARY_TABLE',table)
    variants={
      'common':('report','Common scale across target spectra','Every panel shares the same y-axis range for direct comparison of absolute magnitudes.','The common scale supports comparison of absolute reflectance and discrepancy among targets; small within-target features may be less prominent.'),
      'custom':('report-custom','Alternative: separate scale for each target','Separate y-axis ranges are used for each target; both curves share one range within each panel. Smaller absolute differences are visually magnified, so panel heights cannot be compared as magnitudes.','This alternative uses separate panel scales to show within-target shape. Smaller absolute differences are visually magnified. Use the common-scale report for direct comparisons of magnitude among targets.')}
    for mode,(stem,subtitle,caption,limitation) in variants.items():
        md=template.replace('SCALE_SUBTITLE',subtitle).replace('SCALE_CAPTION',caption).replace('SCALE_LIMITATION',limitation).replace('SCALE',mode)
        (A/f'{stem}.qmd').write_text(md)
        cmd=[str(ROOT/'scripts/render-analysis.sh'),str(A)] if mode=='common' else [str(ROOT/'scripts/project-env.sh'),'quarto','render',f'{stem}.qmd','--to','html']
        result=subprocess.run(cmd,cwd=ROOT if mode=='common' else A,text=True,capture_output=True)
        (A/f'provenance/ctr49_{mode}_quarto.txt').write_text(result.stdout+result.stderr);result.check_returncode()
        portable(stem)
    validate()
if __name__=='__main__':main()
