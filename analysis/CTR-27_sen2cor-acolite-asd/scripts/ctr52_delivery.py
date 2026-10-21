"""Presentation amendment only; reuse CTR49 plotting and CTR48 validation inputs.

Regenerate only the custom spectral figure and preferred report. Historical
common-axis reports/figures and every numerical table are preserved.
"""
from pathlib import Path
import base64
import hashlib
import importlib.util
import json
import subprocess
import tempfile

import ctr49_delivery as prior

A = prior.A
ROOT = prior.ROOT
BASELINE = '4e4e46b3b05fb30ef11549c28f5e96e7a40f1bcc'


def baseline(path):
    return subprocess.check_output(['git', 'show', f'{BASELINE}:{path.relative_to(ROOT)}'], cwd=ROOT)


def validate():
    prior.inputs()
    # Full serialized drawing rows include original QA fields and missingness.
    for kind in ['rows', 'axes']:
        p = A / f'provenance/ctr49_target_spectra_custom_{kind}.csv'
        assert p.read_bytes() == baseline(p), p
    for suffix in ['qmd', 'html']:
        assert (A / f'report-common.{suffix}').read_bytes() == baseline(A / f'report.{suffix}')
    assert (A / 'report-common-portable.html').read_bytes() == baseline(A / 'report-portable.html')
    for stem in ['report', 'report-custom', 'report-portable', 'report-custom-portable']:
        parser = prior.Resources()
        parser.feed((A / f'{stem}.html').read_text())
        assert parser.figures == len(parser.images) == 2, stem
        assert not parser.external, parser.external
        for src, name in zip(parser.images, ['ctr38_figure3_reference.svg', 'ctr49_target_spectra_custom.svg']):
            assert base64.b64decode(src.split(',', 1)[1]) == (A / 'figures/generated' / name).read_bytes()
    for suffix in ['qmd', 'html']:
        assert (A / f'report.{suffix}').read_bytes() == (A / f'report-custom.{suffix}').read_bytes()
    assert (A / 'report-portable.html').read_bytes() == (A / 'report-custom-portable.html').read_bytes()
    text = subprocess.check_output(['pdftotext', str(A / 'figures/generated/ctr49_target_spectra_custom.pdf'), '-'], text=True)
    assert not any(term in text.lower() for term in ['flag', 'cirrus', 'cloud probability'])
    assert all(f'T{i}' in text for i in range(1, 7))
    assert all(band in text for band in ['B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B8A'])
    assert all(s in text for s in ['Sen2Cor', 'ACOLITE'])
    qmd = (A / 'report-custom.qmd').read_text()
    assert 'thin-cirrus classification conflicts with zero cloud probability' in qmd
    assert 'independent ACOLITE quality mask is unavailable' in qmd
    before = json.loads((A / 'provenance/ctr52_before.json').read_text())
    changes = [name for name, h in before['tracked'].items() if prior.sha(ROOT / name) != h]
    allowed = {str((A / name).relative_to(ROOT)) for name in [
        'README.md', 'scripts/ctr49_spectra.R', 'report.qmd', 'report.html', 'report-portable.html',
        'report-custom.qmd', 'report-custom.html', 'report-custom-portable.html',
        *[f'figures/generated/ctr49_target_spectra_custom{ext}' for ext in ['.png', '.pdf', '.svg', '_300dpi.png']]]}
    assert set(changes) <= allowed, set(changes) - allowed
    for name, h in before['unrelated'].items():
        assert prior.sha(ROOT / name) == h, name
    tables = [p for p in before['tracked'] if p.startswith(str(A.relative_to(ROOT)) + '/tables/')]
    assert all(prior.sha(ROOT / p) == before['tracked'][p] for p in tables)
    # Exact raster comparison proves that plotted content outside the T2 note
    # remains unchanged, including all 6 panels, axes, labels and both curves.
    # Pillow is already available in the worker's system Python, used only for
    # pixel QA; no packages or project dependency files are changed.
    raster = json.loads(subprocess.check_output(['python3', str(A / 'scripts/ctr52_raster_compare.py')], cwd=ROOT, text=True))
    record = {
        'status': 'pass', 'baseline': BASELINE, 'numerical_revision': prior.VERIFIED,
        'changed_existing_paths': changes, 'unchanged_tracked_files': len(before['tracked']) - len(changes),
        'preserved_unrelated_files': len(before['unrelated']), 'unchanged_numerical_tables': len(tables),
        'drawing_rows_and_axes_byte_identical': True, 'figures_per_preferred_report': 2,
        'all_preferred_reports_embed_exact_exports': True, 'all_QA_fields_and_report_caveats_retained': True,
        'figure_flag_text_absent_pdf': True, 'raster_comparison': raster,
        'figure1_sha256': {e: prior.sha(A / f'figures/generated/ctr38_figure3_reference.{e}') for e in ['png', 'pdf', 'svg']},
        'scientific_approval': False, 'CTR50_guard_prerequisite': 'unresolved; unrelated CTR39 files preserved; no PR or push',
    }
    prior.writejson(A / 'provenance/ctr52_validation.json', record)
    print(json.dumps(record, indent=2))


def main():
    prior.inputs()
    spec = importlib.util.spec_from_file_location('figure_io', ROOT / 'scripts/figure_io.py')
    safe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(safe)
    with tempfile.TemporaryDirectory(prefix='ctr52_', dir=A / 'outputs') as tmp:
        result = subprocess.run([str(ROOT / 'scripts/project-env.sh'), 'Rscript', str(A / 'scripts/ctr49_spectra.R'), str(A), tmp, 'custom'], cwd=ROOT, text=True, capture_output=True)
        (A / 'provenance/ctr52_figure_render.txt').write_text(result.stdout + result.stderr)
        result.check_returncode()
        for p in Path(tmp).iterdir():
            if p.suffix in ['.png', '.pdf', '.svg']:
                safe.write_generated_bytes(A, p.name, p.read_bytes())
            elif p.suffix == '.csv':
                assert p.read_bytes() == (A / 'provenance' / p.name).read_bytes(), p
        pdf = A / 'figures/generated/ctr49_target_spectra_custom.pdf'
        out = Path(tmp) / 'custom_300dpi'
        subprocess.run(['pdftoppm', '-r', '300', '-singlefile', '-png', str(pdf), str(out)], check=True)
        safe.write_generated_bytes(A, 'ctr49_target_spectra_custom_300dpi.png', out.with_suffix('.png').read_bytes())
    result = subprocess.run([str(ROOT / 'scripts/project-env.sh'), 'quarto', 'render', 'report-custom.qmd', '--to', 'html'], cwd=A, text=True, capture_output=True)
    (A / 'provenance/ctr52_custom_quarto.txt').write_text(result.stdout + result.stderr)
    result.check_returncode()
    prior.portable('report-custom')
    for suffix in ['qmd', 'html']:
        (A / f'report.{suffix}').write_bytes((A / f'report-custom.{suffix}').read_bytes())
    (A / 'report-portable.html').write_bytes((A / 'report-custom-portable.html').read_bytes())
    validate()


if __name__ == '__main__':
    main()
