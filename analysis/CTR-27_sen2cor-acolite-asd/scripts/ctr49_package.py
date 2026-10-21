"""Package exact committed author deliverables and traceable numerical sources."""
from pathlib import Path
import hashlib,json,subprocess,zipfile
A=Path(__file__).resolve().parents[1];ROOT=A.parents[1]
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
assert json.loads((A/'provenance/ctr49_validation.json').read_text())['status']=='pass'
paths=[A/n for n in ['CTR49_HANDOFF.md','CTR48_HANDOFF.md','CTR47_HANDOFF.md','report.qmd','report.html','report-portable.html','report-custom.qmd','report-custom.html','report-custom-portable.html','_quarto.yml','outputs/ctr49_draft_pr.md','outputs/ctr47_raster_headers.json']]
for folder,patterns in {'scripts':['ctr49_*','ctr48_*','ctr47_*','ctr42_extract.py','ctr38_figure3_revision.R'],
  'tables':['ctr48_*.csv','ctr47_*.csv','ctr42_band_contract.csv','ctr42_sources.csv','station_crosswalk.csv','ctr38_figure3_*.csv'],
  'provenance':['ctr49_*','ctr48_*','ctr47_*','ctr42_scene_pair.json','ctr42_validation.json'],
  'figures/generated':['ctr49_*','ctr38_figure3_reference.*'],
  'outputs':['ctr49_*.png']}.items():
    for pattern in patterns:paths.extend((A/folder).glob(pattern))
paths.extend(p for p in (A/'provenance/pi_figure3_20261020').iterdir() if p.is_file())
paths.extend(ROOT/n for n in ['pyproject.toml','uv.lock','renv.lock','.Rprofile','scripts/figure_io.py','scripts/project-env.sh','scripts/render-analysis.sh','scripts/check-env.sh','scripts/bootstrap-env.sh','scripts/bootstrap-renv.R'])
payload={}
for p in sorted(set(paths)):
    if not p.is_file():continue
    name=str(p.relative_to(ROOT));data=p.read_bytes()
    assert subprocess.check_output(['git','show',head+':'+name],cwd=ROOT)==data,name
    payload[name]=data
manifest={'commit':head,'numerical_revision':'c4ac607826d6f1c1f3b0ea6040e6a8775ac6bb5b','presentation_baseline':'3a2bf1b19e7f9f80b6830b8b0f056bbe6add2844','branch':'ctr-49-target-report','scientific_approval':False,'raw_data_included':False,'real_PR_opened':False,'files':{n:{'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest()} for n,d in payload.items()}}
report_names={str((A/f'{s}.html').relative_to(ROOT)) for s in ['report','report-custom']}
figure_names={n for n in payload if '/figures/generated/' in n}
compact_source={n for n in payload if not n.endswith(('.html','.png')) and '/outputs/ctr49_' not in n and ('/figures/generated/' not in n or 'ctr38_figure3_reference.svg' in n)}
compact_reports={str((A/f'{s}-portable.html').relative_to(ROOT)) for s in ['report','report-custom']}
compact_figures={n for n in figure_names if not n.endswith('.png') or n.endswith('_300dpi.png')}
for filename,selected in [('CTR49-source-and-evidence.zip',set(payload)),('CTR49-scientific-reports.zip',report_names),('CTR49-publication-figures.zip',figure_names),('CTR49-compact-source.zip',compact_source),('CTR49-compact-reports.zip',compact_reports),('CTR49-compact-figures.zip',compact_figures)]:
    members={n:payload[n] for n in selected}
    members['CTR49_REVISION_AND_MANIFEST.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    out=A/'outputs'/filename
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n,d in sorted(members.items()):
            info=zipfile.ZipInfo(n,date_time=(2026,10,20,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,d)
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None
        for n,d in members.items():assert z.read(n)==d
    print(json.dumps({'file':filename,'commit':head,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size,'entries':len(members)}))
