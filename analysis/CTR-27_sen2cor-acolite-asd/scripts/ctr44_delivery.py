"""Rebuild the authorized CTR44 presentation from exact CTR43 tables; no statistics."""
from pathlib import Path
from html.parser import HTMLParser
import csv, hashlib, html, importlib.util, json, subprocess, tempfile, zipfile
A=Path(__file__).resolve().parents[1]; ROOT=A.parents[1]
BASE='dc10ebe93e8e5053f4f7fb6aa377ba7fb9a174bd'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(name):
    with (A/'tables'/name).open(newline='') as f:return list(csv.DictReader(f))
def table(headers,rows):
    esc=lambda s:html.escape(str(s))
    return '<table><thead><tr>'+''.join('<th>'+esc(h)+'</th>' for h in headers)+'</tr></thead><tbody>\n'+''.join('<tr>'+''.join('<td>'+esc(v)+'</td>' for v in row)+'</tr>\n' for row in rows)+'</tbody></table>'
def verify_inputs():
    audit=json.loads((A/'provenance/ctr43_computation.json').read_text())
    for n,h in audit['tables_sha256'].items():assert sha(A/'tables'/n)==h,n
    for n,h in json.loads((A/'provenance/ctr44_before.json').read_text())['figure1'].items():assert sha(A/n)==h,n
    for p in (A/'provenance/pi_figure3_20261020').iterdir():
        frozen=subprocess.check_output(['git','show',f'{BASE}:{p.relative_to(ROOT)}'],cwd=ROOT)
        assert p.read_bytes()==frozen,p
    return audit
class Resources(HTMLParser):
    def __init__(self):super().__init__();self.external=[]
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if (k=='src' or (tag=='link' and k=='href')) and v and not v.startswith(('data:','#')):self.external.append(v)
def portable():
    rendered=(A/'report.html').read_text();start=rendered.index('<main');body=rendered[start:rendered.index('</main>',start)+7]
    assert '<script' not in body
    style='body{font:16px/1.6 system-ui,sans-serif;color:#222;margin:24px auto;max-width:1060px;padding:0 24px}img{max-width:100%;height:auto}figure{margin:1.8rem 0}figcaption{font-size:.9rem;color:#444}table{border-collapse:collapse;width:100%;font-size:.85rem}th,td{padding:.35rem;border-bottom:1px solid #ddd;text-align:left}code{overflow-wrap:anywhere}pre{overflow:auto}h2{margin-top:2.2rem}.code-copy-button,.anchorjs-link{display:none}'
    content='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Satellite–ASD reflectance at Banc d’Arguin</title><style>'+style+'</style></head><body>'+body+'</body></html>\n'
    (A/'report-portable.html').write_text(content)
    assert content[content.index('<main'):content.index('</main>')+7]==body
    return {'report_main_preserved_byte_for_byte':True,'source_sha256':sha(A/'report.html'),'portable_sha256':sha(A/'report-portable.html')}
def package():
    paths=[p for p in A.rglob('*') if p.is_file() and '.quarto' not in p.parts and '__pycache__' not in p.parts and p.suffix!='.zip' and 'outputs' not in p.relative_to(A).parts]
    paths += [A/'outputs/ctr43_numerical_delivery.md',A/'outputs/ctr44_author_delivery.md',A/'outputs/ctr44_draft_pr.md']
    # Only the current manifest claims current artifacts; old manifests are frozen history.
    paths=[p for p in paths if p.exists() and p.name!='ctr44_manifest.json']
    manifest=A/'provenance/ctr44_manifest.json'
    manifest.write_text(json.dumps({str(p.relative_to(A)):sha(p) for p in sorted(paths)},indent=2)+'\n')
    helpers=[ROOT/'scripts/figure_io.py',ROOT/'scripts/project-env.sh',ROOT/'scripts/render-analysis.sh',ROOT/'pyproject.toml',ROOT/'uv.lock',ROOT/'renv.lock']
    for name,kind in [('CTR44_complete-delivery.zip','all'),('CTR44_source-and-tables.zip','source'),('CTR44_portable-report.zip','html')]:
        with zipfile.ZipFile(A/'outputs'/name,'w',zipfile.ZIP_DEFLATED) as z:
            for p in sorted(paths+[manifest]):
                if kind=='all' or (kind=='source' and p.suffix in {'.py','.R','.md','.qmd','.yml','.csv','.json','.txt'}) or (kind=='html' and p.name in {'report.html','report-portable.html'}):z.write(p,str(p.relative_to(A)))
            if kind!='html':
                for p in helpers:z.write(p,'repository-context/'+str(p.relative_to(ROOT)))
    print(json.dumps({p.name:sha(p) for p in (A/'outputs').glob('CTR44_*.zip')},indent=2))
def main():
    verify_inputs()
    spec=importlib.util.spec_from_file_location('figure_io',ROOT/'scripts/figure_io.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    with tempfile.TemporaryDirectory(prefix='ctr44_',dir=A/'outputs') as tmp:
        r=subprocess.run([str(ROOT/'scripts/project-env.sh'),'Rscript',str(A/'scripts/ctr44_spectra.R'),str(A),tmp],cwd=ROOT,text=True,capture_output=True)
        (A/'provenance/ctr44_figure_render.txt').write_text(r.stdout+r.stderr)
        r.check_returncode()
        with (Path(tmp)/'ctr44_plot_rows.csv').open(newline='') as f: plotted=list(csv.DictReader(f))
        expected=[r for r in read('ctr43_spectral_long.csv') if r['SRF_role']=='v4_primary']
        assert len(plotted)==len(expected)==351
        import math
        for got,want in zip(plotted,expected):
            for k in ['station_id','band_id','series','segment_id','availability_reason']:assert got[k]==want[k],(k,got,want)
            for k in ['reflectance','plot_wavelength_nm']:
                if want[k]=='NA':assert got[k]=='NA'
                else:assert math.isclose(float(got[k]),float(want[k]),rel_tol=0,abs_tol=1e-12),(k,got,want)
            assert got['SCL_flag'].lower()==want['SCL_flag'].lower()
        (A/'provenance/ctr44_plotted_values.json').write_text(json.dumps({'status':'pass','rows_checked':351,'finite_values':338,'ASD_B08_NA':13,'all_band_keys_segments_flags_preserved':True,'absolute_serialization_tolerance':1e-12,'new_numeric_processing':False},indent=2)+'\n')
        for p in Path(tmp).iterdir():
            if p.suffix in {'.png','.pdf','.svg'}:mod.write_generated_bytes(A,p.name,p.read_bytes())
    md=(A/'scripts/ctr44_report_template.md').read_text()
    availability=[r for r in read('ctr43_band_availability.csv') if r['SRF_role']=='v4_primary']
    wavelengths={r['band_id']:r['plot_wavelength_nm'] for r in read('ctr43_spectral_long.csv')}
    md=md.replace('AVAILABILITY_TABLE',table(['Band','Display wavelength (nm)','Sen2Cor finite','ACOLITE finite','ASD finite','ASD missing reason'],[[r['band_id'],format(float(wavelengths[r['band_id']]),'.1f'),r['Sen2Cor_finite'],r['ACOLITE_finite'],r['ASD_supported'],r['ASD_reason']] for r in availability]))
    display={'dry_sand':'Sand','white_sand':'Sand','algae_mud':'Macroalgae','seagrass':'Seagrass','sand':'Sand','zn':'zn (original label)'}
    md=md.replace('ACCOUNTING_TABLE',table(['Station','Original target','Display class','Status','Satellite values','ASD bands'],[[r['station_id'],r['class_literal'],display.get(r['class_literal'],'excluded'),r['population'],r['satellite_rows'],r['ASD_supported_bands_per_role']] for r in read('ctr43_station_accounting.csv')]))
    (A/'report.qmd').write_text(md)
    r=subprocess.run([str(ROOT/'scripts/render-analysis.sh'),str(A)],cwd=ROOT,text=True,capture_output=True,check=True)
    (A/'provenance/ctr44_quarto.txt').write_text(r.stdout+r.stderr)
    p=Resources();p.feed((A/'report.html').read_text());assert not p.external,p.external
    (A/'provenance/ctr44_portable.json').write_text(json.dumps(portable(),indent=2)+'\n')
    subprocess.run([str(ROOT/'.venv/bin/python'),str(A/'scripts/validate_delivery.py')],cwd=ROOT,check=True)
    package()
if __name__=='__main__':main()
