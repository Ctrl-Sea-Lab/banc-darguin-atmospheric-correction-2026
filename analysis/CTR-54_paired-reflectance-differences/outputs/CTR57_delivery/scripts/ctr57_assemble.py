"""Verify consumed revisions and assemble report tables; never rewrite scientific products."""
import csv
import hashlib
import io
import json
from pathlib import Path
import statistics
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PREFIX = ROOT.relative_to(REPO).as_posix() + '/'
STAT = 'f1ae24ad409ae31f82cad4fd1767ed9861145fbf'
MAP = '8dc80d7141d8c4482b8e36ee00f4cee4c9bf8e04'

def read(name):
    with (ROOT / name).open(newline='') as f:
        return list(csv.DictReader(f))

def sha(data):
    return hashlib.sha256(data).hexdigest()

consumed = []
stat_files = ['tables/date_band_summary.csv','tables/temporal_raster_summary.csv',
 'tables/temporal_coverage.csv','tables/ctr56_observed_summary.csv',
 'tables/ctr56_endpoint_contrasts.csv','tables/ctr56_diagnostics.csv',
 'tables/ctr56_domain_sensitivity.csv','tables/ctr56_quality_coverage_diagnostics.csv',
 'tables/ctr56_leave_one_date_out.csv','tables/ctr56_date_design.csv',
 'figures/generated/ctr56_temporal_gam.png','figures/generated/ctr56_temporal_gam.pdf',
 'provenance/input_hashes.csv','provenance/output_hashes.csv','provenance/ctr56_output_hashes.csv']
map_files = ['tables/display_limits_v2.csv','tables/color_anchors_v2.csv',
 'figures/generated/paired_reflectance_maps_v2.png','figures/generated/paired_reflectance_maps_v2.pdf',
 'figures/generated/paired_reflectance_maps_v2_preview.png']
for revision, names in [(STAT, stat_files),(MAP,map_files),('2f69c2311f1ca9956845e3896d25d678619e597e',['provenance/figure_v2_files.csv'])]:
    for name in names:
        expected = subprocess.check_output(['git','show',revision+':'+PREFIX+name],cwd=REPO)
        actual = (ROOT/name).read_bytes()
        assert sha(actual)==sha(expected), name
        consumed.append({'path':name,'source_revision':revision,'bytes':len(actual),'sha256':sha(actual)})

rows=read('tables/date_band_summary.csv')
assert len(rows)==528
assert len({(r['pair_id'],r['band'],r['domain']) for r in rows})==528
primary=[r for r in rows if r['domain']=='primary']
obs=read('tables/ctr56_observed_summary.csv')
spatial=read('tables/temporal_raster_summary.csv')
coverage=read('tables/temporal_coverage.csv')
contrasts=read('tables/ctr56_endpoint_contrasts.csv')
ledger=[]

def record(claim, band, value, source, selector, operation):
    ledger.append(dict(claim=claim,band=band,value=value,units='dimensionless reflectance unless count/ratio stated',source=source,selector=selector,operation=operation))

lines=['| Band | Median of pixel temporal medians | Median of pixel temporal SDs | Median across date spatial medians | Dates with negative spatial median |',
'|---|---:|---:|---:|---:|']
for b in ['B2','B3','B4','B8']:
    p=[r for r in primary if r['band']==b]
    assert len(p)==22
    # Author tables use full-resolution spatial summaries, not pooled pixel/date values.
    med=statistics.median(float(r['median_delta']) for r in p)
    o=next(r for r in obs if r['band']==b and r['statistic']=='median_delta')
    assert abs(med-float(o['median_across_dates']))<1e-14
    nneg=sum(float(r['median_delta'])<0 for r in p)
    assert nneg==int(o['n_negative'])
    sm=next(r for r in spatial if r['band']==b and r['statistic']=='median')
    ss=next(r for r in spatial if r['band']==b and r['statistic']=='sd')
    assert int(sm['n_valid'])==int(ss['n_valid'])==7309566
    cv=[r for r in coverage if r['band']==b]
    assert sum(int(r['n_pixels']) for r in cv)==7428162
    valid=[int(r['valid_dates']) for r in cv if int(r['n_pixels']) and int(r['valid_dates'])]
    assert min(valid)==4 and max(valid)==22
    lines.append(f"| {b} | {float(sm['median_delta']):.5f} | {float(ss['median_delta']):.5f} | {med:.5f} | {nneg}/22 |")
    for claim,val,src,sel,op in [
      ('median across date spatial medians',med,'tables/date_band_summary.csv',f'primary; {b}','median(median_delta)'),
      ('negative date count',nneg,'tables/date_band_summary.csv',f'primary; {b}','count median_delta < 0'),
      ('median of pixel temporal medians',sm['median_delta'],'tables/temporal_raster_summary.csv',f'{b}; median','median_delta'),
      ('median of pixel temporal SDs',ss['median_delta'],'tables/temporal_raster_summary.csv',f'{b}; sd','median_delta')]:
        record(claim,b,val,src,sel,op)
    for stat in ['median_delta','sd_delta']:
        o=next(r for r in obs if r['band']==b and r['statistic']==stat)
        for field in ['min','max']:
            calculated=(min if field=='min' else max)(float(r[stat]) for r in p)
            assert abs(calculated-float(o[field]))<1e-14
            record(stat+' '+field,b,calculated,'tables/date_band_summary.csv',f'primary; {b}',field+'('+stat+')')
lines += ['', ': Table 1. Distinct spatial and temporal summaries, all in dimensionless reflectance except date counts. Each map statistic weights eligible pixels once; date summaries weight acquisitions once. Source: `temporal_raster_summary.csv`, `date_band_summary.csv` and `ctr56_observed_summary.csv`.', '']
(ROOT/'outputs/ctr57-summary-table.md').write_text('\n'.join(lines))
lines=['| Band | Fitted median change (approximate 95% interval) | Fitted typical SD ratio (approximate 95% interval) |', '|---|---:|---:|']
for b in ['B2','B3','B4','B8']:
    vals=[]
    for s in ['median_delta','sd_delta']:
        c=next(r for r in contrasts if r['band']==b and r['statistic']==s)
        nums=[float(c[f]) for f in ['estimate','lower','upper']]
        assert nums[1] <= (0 if s=='median_delta' else 1) <= nums[2]
        digits=5 if s=='median_delta' else 3
        vals.append(f'{nums[0]:.{digits}f} ({nums[1]:.{digits}f}, {nums[2]:.{digits}f})')
        for f in ['estimate','lower','upper']:
            record('endpoint '+s+' '+f,b,c[f],'tables/ctr56_endpoint_contrasts.csv',f'{b}; {s}',f)
    lines.append('| '+b+' | '+' | '.join(vals)+' |')
lines += ['', ': Table 2. Fitted 27 March 2026 versus 6 January 2025: additive change for spatial medians (reflectance units), ratio for typical spatial SD (dimensionless). Intervals are illustrative pointwise working-model contrasts; residual departures prevent calibrated trend inference. Source: `ctr56_endpoint_contrasts.csv`.', '']
(ROOT/'outputs/ctr57-contrast-table.md').write_text('\n'.join(lines))
# Record all tabulated diagnostics/sensitivities used in prose, retaining exact values.
for name,fields in [
 ('ctr56_domain_sensitivity.csv',['min_pixels','observed_median_change','observed_correlation','curve_max_change']),
 ('ctr56_quality_coverage_diagnostics.csv',['no_missing_flags_max_curve_change']),
 ('ctr56_diagnostics.csv',['edf','adjacent_residual_correlation','k10_max_absolute_curve_change']),
 ('display_limits_v2.csv',['display_min','display_max','fraction_clipped_low','fraction_clipped_high'])]:
    for r in read('tables/'+name):
        for f in fields:
            record(f,r['band'],r[f],'tables/'+name,'; '.join(r.get(k,'') for k in ['domain','statistic']),f)
# Check the acquisition design and largest influences reported in the narrative.
design=read('tables/ctr56_date_design.csv')
assert len(design)==22
from collections import Counter
assert Counter(r['sensor'] for r in design)=={'S2A':3,'S2B':11,'S2C':8}
gaps=[int(float(design[i]['t'])-float(design[i-1]['t'])) for i in range(1,22)]
assert (min(gaps),max(gaps))==(2,70)
assert [r['date'] for r in design if r['flags_available']=='False']==['2026-03-07','2026-03-27']
influence=read('tables/ctr56_leave_one_date_out.csv')
assert len(influence)==176
for b in ['B2','B3','B4','B8']:
    for stat,date in [('median_delta','2025-03-22'),('sd_delta','2026-03-07')]:
        selected=[r for r in influence if r['band']==b and r['statistic']==stat]
        largest=max(selected,key=lambda r:float(r['max_curve_change']))
        assert largest['omitted_date']==date
        record('largest omission influence',b,largest['max_curve_change'],'tables/ctr56_leave_one_date_out.csv',stat+'; '+date,'max(max_curve_change)')
for name,val in [('minimum acquisition gap in days',min(gaps)),('maximum acquisition gap in days',max(gaps)),('matched acquisitions',len(design))]:
    record(name,'all',val,'tables/ctr56_date_design.csv','all dates','acquisition design check')
with (ROOT/'tables/ctr57_claim_ledger.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=ledger[0].keys());writer.writeheader();writer.writerows(ledger)
report={'status':'passed','scope':'Writer assembly and tabular checks; no raster processing/model reruns or independent scientific approval',
 'consumed_files':consumed,'table_rows':528,'primary_rows':88,'bands':['B2','B3','B4','B8'],
 'checks':['Exact consumed bytes match source revisions','Unique table keys','Per-band observations and signs recomputed','Map counts and temporal coverage checked','Date extrema recomputed','Endpoint intervals include null','All prose diagnostic values retained in claim ledger'],
 'manuscript_changed':False,'dependencies_changed':False,'scientific_review':'pending CTR-59','pi_approval':'pending'}
(ROOT/'provenance/ctr57_assembly.json').write_text(json.dumps(report,indent=2)+'\n')
print('Passed: source hashes, 528 keys, 88 primary rows, summary tables and claim ledger.')
