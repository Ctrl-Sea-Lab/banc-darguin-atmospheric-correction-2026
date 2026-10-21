"""Generate the output manifest after rendering; record its commit in the handoff."""
from common import *
import platform
# Exclude self-referential handoff records, receipts, caches and regenerable drawing bridges.
v=json.loads((A/'provenance/validation.json').read_text())
r=list(csv.DictReader((A/'tables/R_temporal_crosscheck.csv').open()))
assert r and max(float(x['absolute_error']) for x in r)<2e-7
(A/'QA.md').write_text(f"""# Remote-sensing QA summary

**Take-home message:** Computational checks pass for the paired reflectance delivery. They do not establish atmospheric-correction accuracy or constitute independent scientific approval.

**Meaningful results:** 22 matched sensor/datatake/orbit/tile acquisitions; B2/B3/B4/B8 dimensionless ΔR = ACOLITE − Sen2Cor; exact native 10 m comparison grid in EPSG:32628. {v['rasters_checked']} rasters pass grid/type/NoData checks, {v['source_checks']} source-pixel comparisons pass (maximum absolute discrepancy {v['max_source_absolute_error']:.3g}), and {v['temporal_checks']} temporal checks agree with base R. Full-grid validity masks match n≥1 for median and n≥2 for sample SD. Input manifests cover 142 physical files and 22.2 GB.

**Issues and limitations:** Every ACOLITE band contains 118,596 encoded default-fill cells despite NoData=NaN; the exact sentinel is explicitly rejected and separately audited in all 88 source bands. March 2026 lacks ACOLITE flags. Masks and ecological interpretations have no independent field validation; temporal and spatial dependence and changing support remain relevant.

**Implications and next steps:** Use the coverage sensitivities and downstream table contract. Submit this bounded geospatial delivery through the existing CTR-54 review chain. Independent review and PI approval remain pending.

Input metadata, wavelength/units/offset verification, all source/output grid checks, masks, exclusions, resampling, numerical checks and versions are retained in tables/ and provenance/. See METHODS.md for detail. Raw inputs are read only; their sizes/mtimes still match the hash pass. No manuscript changes, integration, merge or publication are authorized by this delivery.
""")
rows=[]
for p in sorted(A.rglob('*')):
    if not p.is_file():continue
    rel=p.relative_to(A).as_posix()
    if rel in ['HANDOFF.md','provenance/handoff.json','provenance/output_hashes.csv'] or '__pycache__' in rel or '/.quarto/' in rel or 'receipt' in rel or rel.endswith('_display.bin'):continue
    rows.append(dict(path=rel,bytes=p.stat().st_size,sha256=sha(p)))
table(A/'provenance/output_hashes.csv',rows)
# Confirm input sizes and mtimes still match the recorded hash pass after all computation.
for r in csv.DictReader((A/'provenance/input_hashes.csv').open()):
    st=Path(r['path']).stat();assert st.st_size==int(r['bytes']) and st.st_mtime_ns==int(r['mtime_ns'])
print('Output manifest:',len(rows),'files; source stat stability confirmed')
