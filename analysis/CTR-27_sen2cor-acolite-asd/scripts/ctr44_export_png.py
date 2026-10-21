"""Export additional 300 dpi PNGs from the exact committed scientific PDFs.

The canonical 600 dpi exports remain untouched. These smaller exports facilitate
artifact transfer; no coordinates, values, labels, page dimensions or styles change.
"""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,tempfile
A=Path(__file__).resolve().parents[1]; ROOT=A.parents[1]
SOURCE='3d881f57530b90a093aa695c6157c899ee475e38'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    spec=importlib.util.spec_from_file_location('figure_io',ROOT/'scripts/figure_io.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    records=[]
    with tempfile.TemporaryDirectory(prefix='ctr44_png300_',dir=A/'outputs') as tmp:
        for stem in ['ctr44_march_primary','ctr44_march_supplementary']:
            source=A/'figures/generated'/f'{stem}.pdf'
            frozen=subprocess.check_output(['git','show',f'{SOURCE}:{source.relative_to(ROOT)}'],cwd=ROOT)
            assert source.read_bytes()==frozen,source
            output=Path(tmp)/stem
            subprocess.run(['pdftoppm','-r','300','-f','1','-singlefile','-png',str(source),str(output)],check=True,capture_output=True)
            target=mod.write_generated_bytes(A,f'{stem}_300dpi.png',output.with_suffix('.png').read_bytes())
            records.append({'file':str(target.relative_to(A)),'dpi':300,'source_pdf':str(source.relative_to(A)),
                'source_pdf_sha256':digest(source),'sha256':digest(target),'bytes':target.stat().st_size,
                'source_commit':SOURCE,'command':'pdftoppm -r 300 -f 1 -singlefile -png <source_pdf> <output_stem>',
                'canonical_600dpi_PNG_unchanged':True,'new_scientific_computation':False})
    (A/'provenance/ctr44_additional_png_exports.json').write_text(json.dumps(records,indent=2)+'\n')
    print(json.dumps(records,indent=2))
if __name__=='__main__':main()
