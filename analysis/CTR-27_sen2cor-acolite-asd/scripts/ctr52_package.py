"""Package committed editable sources; record exact source revision and hashes."""
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile

A = Path(__file__).resolve().parents[1]
ROOT = A.parents[1]
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
assert json.loads((A / 'provenance/ctr52_validation.json').read_text())['status'] == 'pass'
paths = [A / n for n in ['README.md', 'CTR52_HANDOFF.md', 'CTR49_HANDOFF.md', 'CTR48_HANDOFF.md',
                         'report.qmd', 'report-custom.qmd', 'report-common.qmd', '_quarto.yml']]
for folder, patterns in {
    'scripts': ['ctr52_*.py', 'ctr49_delivery.py', 'ctr49_spectra.R'],
    'tables': ['ctr48_*.csv', 'ctr47_*.csv', 'ctr42_band_contract.csv', 'ctr42_sources.csv'],
    'provenance': ['ctr52_*', 'ctr48_*', 'ctr49_target_spectra_custom_*.csv', 'ctr42_scene_pair.json'],
    'figures/generated': ['ctr38_figure3_reference.*'],
}.items():
    for pattern in patterns:
        paths.extend(p for p in (A / folder).glob(pattern) if p.is_file())
paths.extend(ROOT / n for n in ['pyproject.toml', 'uv.lock', 'renv.lock', '.Rprofile',
                                'scripts/figure_io.py', 'scripts/project-env.sh',
                                'scripts/render-analysis.sh', 'scripts/check-env.sh'])
payload = {}
for p in sorted(set(paths)):
    name = str(p.relative_to(ROOT))
    data = p.read_bytes()
    assert data == subprocess.check_output(['git', 'show', f'{head}:{name}'], cwd=ROOT), name
    payload[name] = data
files = {name: {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()} for name, data in payload.items()}
delivery = [A / 'report-custom-portable.html', A / 'report-custom.html', A / 'report.html',
            A / 'report-common.html', A / 'report-common-portable.html']
delivery += list((A / 'figures/generated').glob('ctr49_target_spectra_custom*.*'))
for p in delivery:
    name = str(p.relative_to(ROOT))
    data = p.read_bytes()
    assert data == subprocess.check_output(['git', 'show', f'{head}:{name}'], cwd=ROOT), name
    files[name] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
manifest = {
    'source_commit': head, 'baseline': '4e4e46b3b05fb30ef11549c28f5e96e7a40f1bcc',
    'numerical_revision': 'c4ac607826d6f1c1f3b0ea6040e6a8775ac6bb5b',
    'primary_report': 'report-custom-portable.html', 'canonical_report': 'report.html',
    'historical_alternative': 'report-common.html',
    'reproduction_scope': 'Existing authorized project Git checkout with baseline objects and existing locked environments; system Python Pillow 10.2.0 for raster QA only.',
    'raw_data_included': False, 'scientific_approval': False,
    'CTR50_PR_guard': 'unresolved; no push, PR, bypass, merge or publication', 'files': files,
}
manifest_bytes = (json.dumps(manifest, indent=2) + '\n').encode()
for filename, members in [
    ('CTR52-editable-source-and-evidence.zip', payload),
    # Existing-repository transfer copy; the preserved Figure 1 PNG/PDF stay
    # in the full package and checkout, while its exact SVG is retained here.
    ('CTR52-compact-editable-source.zip', {n: data for n, data in payload.items()
                                        if not n.endswith(('ctr38_figure3_reference.png', 'ctr38_figure3_reference.pdf'))}),
    ('CTR52-reports.zip', {p.name: p.read_bytes() for p in delivery[:5]}),
]:
    members = dict(members)
    members['CTR52_REVISION_AND_MANIFEST.json'] = manifest_bytes
    out = A / 'outputs' / filename
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for n, data in sorted(members.items()):
            info = zipfile.ZipInfo(n, date_time=(2026, 10, 20, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, data)
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None
        assert all(z.read(n) == data for n, data in members.items())
    files[str(out.relative_to(ROOT))] = {'bytes': out.stat().st_size, 'sha256': hashlib.sha256(out.read_bytes()).hexdigest()}
    print(json.dumps({'file': filename, **files[str(out.relative_to(ROOT))]}))
manifest['files'] = files
(A / 'outputs/CTR52_DELIVERY_HASHES.json').write_text(json.dumps(manifest, indent=2) + '\n')
