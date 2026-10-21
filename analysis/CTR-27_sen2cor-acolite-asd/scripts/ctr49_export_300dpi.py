"""Additional publication PNGs from exact vector PDFs; no data processing."""
from pathlib import Path
import importlib.util,json,subprocess,tempfile
A=Path(__file__).resolve().parents[1];ROOT=A.parents[1]
s=importlib.util.spec_from_file_location('figure_io',ROOT/'scripts/figure_io.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
for mode in ['common','custom']:
    stem=f'ctr49_target_spectra_{mode}'
    with tempfile.TemporaryDirectory(prefix='ctr49_png_',dir=A/'outputs') as t:
        out=Path(t)/stem
        subprocess.run(['pdftoppm','-r','300','-singlefile','-png',str(A/f'figures/generated/{stem}.pdf'),str(out)],check=True)
        m.write_generated_bytes(A,f'{stem}_300dpi.png',out.with_suffix('.png').read_bytes())
print('Additional 300 dpi PNGs exported directly from the exact final vector PDFs.')
