"""CTR-38 display pipeline. Run from any directory; reads only saved small tables."""
from pathlib import Path
import csv
import hashlib
import html
import importlib.util
import json
import platform
import shutil
import struct
import xml.etree.ElementTree as ET
import subprocess
import sys
import zipfile

A = Path(__file__).resolve().parents[1]
ROOT = A.parents[1]
INPUT_COMMIT = '9a4ec93fc412736fda85b44a1aab56ed6e2c2beb'
STATIONS = ['AC01', 'AC02', 'AC05', 'AC06', 'AC07', 'AC08']
BANDS = ['B02', 'B03', 'B04']
CAP1 = ('Band-integrated ASD station averages (black circles), supplied operational Sen2Cor L2A '
        '(orange triangles) and ACOLITE DSF (blue squares) for six primary non-mud stations, '
        'Banc d’Arguin, 27 March 2026. S2B v4 response functions define the ASD references; '
        'B02/B03/B04 are ordered bands, not a common effective-wavelength scale. Lines guide '
        'the eye across bands only. Reflectance and discrepancies are dimensionless (1). '
        'Each table uses the same three bands: bias = mean(satellite − ASD), MAE = mean absolute '
        'difference, RMSE = root mean squared difference. Values are rounded to six decimals; '
        'N is a band count, not independent replication. The containing satellite cells and '
        'ASD footprints have unresolved spatial-support and exposure limitations; uncertainty '
        'is not estimated. All 18 triples remain exploratory and physically held; zero '
        'validation-eligible pairs. AC03 mbp_mud and AC04 mpb_mud are PI-excluded (original '
        'labels retained); AC05 algae_mud remains included. Supplementary D06_A–D06_G have '
        'unavailable matched exports and are listed explicitly below. B08 fails spectral coverage.')
CAP2 = ('Exploratory numerical agreement for exactly the same 18 station–band triples in each '
        'correction panel. ASD band-integrated reflectance is on x and satellite reflectance '
        'on y; scales are identical and each panel has equal aspect. The dashed line is 1:1. '
        'Colors identify B02/B03/B04; shapes retain literal target classes dry_sand, algae_mud, '
        'white_sand and seagrass. Points are repeated spectral measurements, not independent '
        'replicates. Spatial-support and exposure holds remain, uncertainty is not estimated '
        'and zero pairs are validation-eligible. No fitted trend or correction ranking is '
        'implied. AC03 mbp_mud and AC04 mpb_mud are excluded; supplementary D06_A–D06_G '
        'have unavailable matched exports and are omitted from this scatter, with NA recorded '
        'in the station ledger. B08 is unsupported; only primary v4 references are shown.')


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(n):
    with (A / 'tables' / n).open(newline='') as f:
        return list(csv.DictReader(f))


def dump(p, x):
    p.write_text(json.dumps(x, indent=2, ensure_ascii=False) + '\n')


def table(headers, rows):
    esc = lambda x: html.escape(str(x))
    return '<table><thead><tr>' + ''.join('<th>'+esc(x)+'</th>' for x in headers) + '</tr></thead><tbody>\n' + '\n'.join('<tr>' + ''.join('<td>'+esc(x)+'</td>' for x in r) + '</tr>' for r in rows) + '\n</tbody></table>'


def main():
    # Verify the saved numerical delivery before using any of its values.
    manifest = json.loads((A/'provenance/ctr37_delivery_manifest.json').read_text())
    for name, record in manifest.items():
        assert digest(A/name) == record['sha256'], name
    audit = json.loads((A/'provenance/ctr37_input_audit.json').read_text())
    validation = json.loads((A/'provenance/ctr37_delivery_validation.json').read_text())
    assert audit['status'] == validation['status'] == 'pass'
    for name, expected in json.loads((A/'outputs/ctr37_contract.json').read_text())['inputs'].items():
        assert digest(A/name) == expected, name
    spectral = load('ctr37_spectral_long.csv')
    pairs = load('ctr37_figure_pairs.csv')
    metrics = load('ctr37_station_metrics.csv')
    supp = load('ctr37_supplementary_metrics.csv')
    coverage = load('ctr37_station_coverage.csv')
    assert len(metrics) == 12 and len(supp) == 14 and len(coverage) == 13
    used = [r for r in pairs if r['common_finite_triple'] == 'True']
    assert len(used) == 36
    keys = [{(r['station_id'],r['band_id'],r['matchup_id']) for r in used if r['correction']==c} for c in ['L2A','ACOLITE']]
    assert keys[0] == keys[1] and len(keys[0]) == 18
    assert {(r['station_id'],r['band_id']) for r in used} == {(s,b) for s in STATIONS for b in BANDS}
    values = {(r['station_id'],r['band_id'],r['series']):r['reflectance'] for r in spectral}
    for r in used:
        assert r['SRF_role'] == 'v4_primary' and r['station_completeness'] == 'complete'
        assert r['included_validation_pair'] == 'False' and r['unit'] == '1'
        assert r['ASD_reflectance'] == values[r['station_id'],r['band_id'],'ASD']
        assert r['satellite_reflectance'] == values[r['station_id'],r['band_id'],r['correction']]
    assert all(r['included_validation_pair']=='False' for r in spectral+pairs+metrics+supp)
    assert all(r['n_paired_bands']=='0' and all(r[k]=='NA' for k in ['bias','MAE','RMSE']) for r in supp)
    assert all(r['ASD_reflectance']==r['satellite_reflectance']=='NA' for r in pairs if r['station_id'] not in STATIONS)
    assert len(load('ctr34_eligible_pairs.csv')) == 0
    assert set(r['station_id'] for r in coverage) == set(r['station_id'] for r in pairs)
    stage = A/'outputs/ctr38_stage'
    stage.mkdir(exist_ok=True)
    log = subprocess.run([str(ROOT/'scripts/project-env.sh'),'Rscript',str(A/'scripts/ctr38_figures.R'),str(A),str(stage)],cwd=ROOT,text=True,capture_output=True,check=True)
    (A/'provenance/ctr38_render.txt').write_text(log.stdout+log.stderr)
    # Reuse the repository's safe writer, scoped to this existing analysis.
    spec = importlib.util.spec_from_file_location('figure_io', ROOT/'scripts/figure_io.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    for p in sorted(stage.iterdir()):
        module.write_generated_bytes(A, p.name, p.read_bytes())
    shutil.rmtree(stage)
    headers = ['Station','Literal target','Correction','N bands','Bias (1)','MAE (1)','RMSE (1)']
    display = [[r['station_id'],r['class_literal'],{'L2A':'Sen2Cor L2A','ACOLITE':'ACOLITE DSF'}[r['correction']],r['n_paired_bands']]+[format(float(r[k]),'.6f') for k in ['bias','MAE','RMSE']] for r in metrics]
    with (A/'tables/ctr38_display_metrics.csv').open('w',newline='') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(headers);w.writerows(display)
    missing = [[r['station_id'],r['class_literal'],'B02, B03, B04','NA','NA','0','NA'] for r in coverage if r['population']=='supplementary']
    hashes = {n:record['sha256'] for n,record in manifest.items() if n.startswith('tables/')}
    repro = '.venv/bin/python analysis/CTR-24_data-dictionary/scripts/ctr38_build.py'
    qmd = '''---
title: "Station reflectance: ASD, Sen2Cor and ACOLITE"
subtitle: "Banc d’Arguin · 27 March 2026"
author: "Edward Tufte · numerical analysis by Thomas Bayes · Ctrl+Sea"
format:
  html:
    embed-resources: true
    toc: true
    toc-depth: 2
    number-sections: false
    theme: cosmo
    fig-cap-location: bottom
    include-in-header:
      text: |
        <style>
        body { color: #262626; } .quarto-title h1 { font-weight: 650; }
        table { width:100%; font-variant-numeric:tabular-nums; font-size:0.9rem; margin:1rem 0; }
        th,td { padding:0.35rem 0.5rem; border-bottom:1px solid #e4e7e9; }
        th { text-align:left; } td:nth-last-child(-n+3) { text-align:right; }
        figcaption { line-height:1.45; } code { overflow-wrap:anywhere; }
        </style>
execute:
  enabled: false
---

## Station comparison

How do the supplied satellite reflectances differ from the band-integrated ASD station averages at each station? Six primary stations have complete B02/B03/B04 values for both correction products. The figures and metrics describe **exploratory numerical discrepancies in dimensionless reflectance (1)**. All 18 station–band triples retain physical holds; **zero pairs are eligible for validation**.

![CAPTION1](figures/generated/ctr38_station_spectra.svg){#fig-stations width=180mm}

### Numerical observations

Sen2Cor L2A station biases range from +0.009023 to +0.107728. ACOLITE DSF station biases range from −0.001827 to +0.064366. These ranges describe the fixed diagnostic set and do not establish correction accuracy or a preferred correction. The relatively large satellite–ASD separation at AC06 in the Sen2Cor panel is visible on the same vertical scale used for every station.

At AC06, ACOLITE has signed bias −0.001827, MAE 0.007502 and RMSE 0.008342. Opposite-signed band differences partly cancel in the bias, so near-zero mean bias does not imply agreement in every band. All displayed values below are taken directly from the saved numerical handoff and rounded to six decimals. Machine-readable source CSVs retain full computation precision.

METRICTABLE

Positive bias means satellite reflectance exceeds ASD. N bands is a denominator count, not an independent sample size. Every primary station has the same three available bands and each has weight 1/3 within that station. No pooled summary or population inference is reported.

## The same pairs viewed against 1:1

![CAPTION2](figures/generated/ctr38_agreement_scatter.svg){#fig-agreement width=180mm}

## Station coverage and exclusions

The seven supplementary non-mud stations below have retained continuous ASD spectra, but neither satellite match values nor band-integrated ASD references were exported in the handoff. These are unavailable values, not zeros. Their metrics are NA for both corrections. Continuous spectra are not drawn here because they cannot supply missing satellite matches.

MISSINGTABLE

N common bands applies to each correction. The full reasons and the 14 station–correction rows are preserved in `tables/ctr37_supplementary_metrics.csv`; every missing station–band value is retained as NA in the plotting tables.

The authenticated PI exclusions remain **AC03 mbp_mud** and **AC04 mpb_mud**, preserving the original labels in `tables/ctr36_exclusions.csv`. AC05 **algae_mud** remains in the authorized primary population; the PI exclusions are station-specific. B08 is excluded for inadequate ASD spectral coverage. No station or band is substituted.

## Short methods

The study area is Banc d’Arguin, Mauritania. This figure delivery reuses Thomas’s exact validated diagnostic tables at commit `INPUTCOMMIT`, derived from the consolidated CTR24 handoff. It performs no raster extraction, spectral integration, metric estimation or atmospheric processing. The reviewed dictionary and earlier reports remain separate and unchanged.

The documented scene is S2B, T28QCH, 27 March 2026; the metadata acquisition time is 11:45:53.975343 UTC. Supplied Sen2Cor operational L2A PB05.12 was decoded as (DN − 1000)/10000 after masking DN 0 and 65535. Supplied ACOLITE DSF rhos is dimensionless Float32 surface reflectance. Valid negative values are retained; none of the finite plotted primary reflectances is negative. A negative signed difference is retained at AC06. These are supplied products; their processors were not rerun.

Existing ASD references use supplied S2B v4 response functions, normalized response-weighted trapezoidal integration on union knots, no extrapolation, finite interpolation across gaps no larger than 1 nm and minimum response coverage 0.999. Only supported B02/B03/B04 are matched. Their ordered band axis avoids assigning a shared effective wavelength to different responses. V5 remains a separate sensitivity analysis: the saved maximum absolute v5−v4 reference change is 0.0000155204 (AC06 B02); no v5 values are mixed into these figures.

Bias is mean(satellite − ASD); MAE is mean(abs(satellite − ASD)); RMSE is sqrt(mean((satellite − ASD)^2)), each across the fixed three common finite bands. Both corrections use exactly identical station–band keys. The six-station set is the frozen descriptive population, not a representative validation sample.

## Interpretation and limitations

ASD samples a small field footprint, while satellite values describe stored containing cells. Effective radiometric contributors, common full-support QA and representative patch support remain unresolved. Material patch representativeness remains a concern at AC01/02/06/07/08; exposure or optical-path ambiguity also remains at AC05/06/08. Effective-support bounds are unverified at all six stations. Numerical identity and unit checks support these diagnostics; physical equivalence remains unproven.

Field timing is described as around acquisition, but precise station clock/timezone, station-average membership, calibration variance and scan variance are unavailable. Shared scene identity is documented; byte-identical upstream L1C ancestry is unestablished. No confidence intervals, guessed error bars, fitted trends, p-values, correlation coefficients or algorithm ranking are supplied. These discrepancy measures do not quantify the unresolved support/exposure uncertainty. Bands are repeated spectral observations, not independent replicates.

## Review and approval status

This is the author-checked figure revision submitted for Rachel Carson’s presentation review and then Karl Popper’s independent scientific review through CTR-38’s native stages. Their decisions and exact reviewed commit are recorded on the task. Internal review is not PI approval. Charles Darwin coordinates submission for PI scientific approval. Final-manuscript integration, protected merge and public publication remain unauthorized.

## Appendix: reproducibility and provenance

The exact input revision is `INPUTCOMMIT`; the containing delivery commit and downloadable bundle hash are recorded in the saved CTR-38 figure-delivery document. This avoids embedding a commit hash inside its own committed output. The build records source/table/output SHA-256 hashes in `provenance/ctr38_manifest.json` and author checks in `provenance/ctr38_validation.json`.

From the canonical repository root on the Linux Mint Research Worker, run:

```bash
REPRO
```

This builds plots from saved tables using base R graphics/grDevices in the approved project environment, promotes outputs through `scripts/figure_io.py` scoped to this analysis, generates this editable Quarto source and renders only `station-matchups.qmd` using the existing investigation configuration. It intentionally does not invoke `scripts/render-analysis.sh`, whose fixed `report.qmd` target would rebuild the preserved dictionary. No packages are installed. PNGs are 600 dpi at 180 mm width; vector PDFs and SVGs use the same sizes. The station figure is 220 mm high; the scatter is 116 mm high. The source uses an 8 pt base font and colorblind-safe categorical colors, with redundant symbols and line types. SVG glyphs are vector paths; PDF text is embedded/selectable.

The pipeline checks all saved CTR-37 delivery hashes, the frozen input-contract hashes and passed audit states before plotting. It checks identical scatter keys, exact long/wide plotted-value correspondence, dimensionless units, validation holds, supplementary missingness and empty validation eligibility. It compares displayed rounding against the saved tables and checks self-contained HTML resources. No new statistical calculations are needed for this figure delivery. All exported panels must additionally be opened for author visual inspection; that record is saved separately in `provenance/ctr38_visual_inspection.md`.

Input table SHA-256 hashes:

HASHTABLE

Author input audit: 308 checks and 74 independent arithmetic checks were saved in CTR-37; these are numerical QA, not independent scientific review. The original empty `tables/ctr34_eligible_pairs.csv`, reviewed dictionary and all historical reports are retained. The deliverable bundle includes the editable report, both figure sets, plotting/build sources, full metric and missingness tables, captions, provenance and reproduction instructions, without original raw datasets.
'''
    for old,new in [('CAPTION1',CAP1),('CAPTION2',CAP2),('METRICTABLE',table(headers,display)),('MISSINGTABLE',table(['Station','Literal target','Expected bands','ASD band reference','Satellite values','N common bands','Metrics'],missing)),('INPUTCOMMIT',INPUT_COMMIT),('REPRO',repro),('HASHTABLE',table(['Input table','SHA-256'],hashes.items()))]:
        qmd=qmd.replace(old,new)
    (A/'station-matchups.qmd').write_text(qmd)
    (A/'outputs/ctr38_captions.md').write_text('Figure 1. '+CAP1+'\n\nFigure 2. '+CAP2+'\n')
    rendered=subprocess.run([str(ROOT/'scripts/project-env.sh'),'quarto','render','station-matchups.qmd','--to','html'],cwd=A,capture_output=True,text=True,check=True)
    (A/'provenance/ctr38_quarto_render.txt').write_text(rendered.stdout+rendered.stderr)
    report=(A/'station-matchups.html').read_text()
    for row in display:
        for value in row: assert html.escape(value) in report, value
    from html.parser import HTMLParser
    class Resources(HTMLParser):
        external=[]
        def handle_starttag(self,tag,attrs):
            attrs=dict(attrs)
            for k in ('src','href'):
                v=attrs.get(k,'')
                if v and tag in ('script','link','img') and not v.startswith(('data:','#')):
                    self.external.append((tag,k,v))
    parser=Resources();parser.feed(report);assert not parser.external, parser.external
    assert report.count('data:image/svg+xml')>=2
    pdf_text = subprocess.check_output(['pdftotext','-layout',str(A/'figures/generated/ctr38_station_spectra.pdf'),'-'],text=True)
    for row in display:
        assert row[0] in pdf_text
        for value in row[-3:]: assert value in pdf_text, value
    sizes = {}
    for name,height in [('ctr38_station_spectra',220),('ctr38_agreement_scatter',116)]:
        png=(A/'figures/generated'/f'{name}.png').read_bytes()
        assert png[:8]==b'\x89PNG\r\n\x1a\n'
        width_px,height_px=struct.unpack('>II',png[16:24])
        assert abs(width_px-180/25.4*600)<1 and abs(height_px-height/25.4*600)<1
        sizes[name]=[width_px,height_px]
        ET.parse(A/'figures/generated'/f'{name}.svg')
    result={'status':'pass' ,'input_commit':INPUT_COMMIT,'ctr37_manifest_entries_verified':len(manifest),'frozen_contract_inputs_verified':11,'primary_spectral_values':54,'identical_scatter_keys_per_correction':18,'primary_metric_rows':12,'all_36_metric_annotations_found_in_PDF_text':True,'PNG_dimensions_pixels':sizes,'supplementary_stations':7,'supplementary_metrics_NA_rows':14,'validation_eligible_pairs':0,'all_displayed_metrics_match_saved_table_rounding':True,'external_render_resources':parser.external,'unit':'1','PNG_dpi':600,'dimensions_mm':{'station_spectra':[180,220],'agreement_scatter':[180,116]},'software':{'python':sys.version,'platform':platform.platform(),'R':'see ctr38_render.txt','quarto':subprocess.check_output(['quarto','--version'],text=True).strip()},'scope':'Author display QA only; native presentation and independent reviews pending'}
    dump(A/'provenance/ctr38_validation.json',result)
    files=[A/'station-matchups.qmd',A/'station-matchups.html',*sorted((A/'figures/generated').glob('ctr38_*')),*sorted((A/'scripts').glob('ctr38_*')),*sorted((A/'provenance').glob('ctr38_*')),*sorted((A/'tables').glob('ctr38_*')),A/'outputs/ctr38_captions.md']
    files=[p for p in files if p.is_file() and p.name!='ctr38_manifest.json']
    dump(A/'provenance/ctr38_manifest.json',{str(p.relative_to(A)):{'sha256':digest(p),'bytes':p.stat().st_size} for p in files})
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
