#!/usr/bin/env python3
"""Independent target/metadata/window/arithmetic audit; no raster re-extraction.
Python standard library only, in the existing project environment. R provides a
separate arithmetic implementation. Outputs are descriptive, never accuracy tests.
"""
import collections
import csv
import hashlib
import json
import math
import platform
import statistics
import struct
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

P = Path(__file__).resolve().parents[1]
ROOT = P.parents[1]
INPUT_REV = '82ca0df0b699e51135afc680b23eda9def5bbfe2'
BANDS = ['B01','B02','B03','B04','B05','B06','B07','B08','B8A']
CHECKS = []

def check(name, condition):
    if not condition:
        raise AssertionError(name)
    CHECKS.append(name)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(name):
    with (P/'tables'/name).open(newline='') as f:
        return list(csv.DictReader(f))

def write(name, rows):
    with (P/'tables'/name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

def dump(name, obj):
    (P/'provenance'/name).write_text(json.dumps(obj, indent=2, allow_nan=False)+'\n')

def main():
    before = json.loads((P/'provenance/ctr48_preflight.json').read_text())
    # Preserve and bind every prior tracked byte, including Figure 1 and metrics.
    for group in ['tracked_sha256','unrelated_ctr39_sha256']:
        for n,h in before[group].items():
            check('preservation '+n, sha(ROOT/n)==h)
    tracked = subprocess.check_output(['git','ls-tree','-r','--name-only',INPUT_REV],cwd=ROOT,text=True).splitlines()
    input_hashes = {}
    for n in tracked:
        if ('ctr47_' in n or 'CTR47_HANDOFF' in n or n.endswith('ctr42_band_contract.csv')):
            data=subprocess.check_output(['git','show',INPUT_REV+':'+n],cwd=ROOT)
            check('exact predecessor revision '+n, data==(ROOT/n).read_bytes())
            input_hashes[n]=hashlib.sha256(data).hexdigest()
    targets=read('ctr47_targets.csv'); sat=read('ctr47_satellite.csv')
    old=read('ctr47_pairs.csv'); sources=read('ctr47_sources.csv')
    windows=read('ctr47_windows.csv'); qa=read('ctr47_qa.csv')
    contract={r['band_id']:r for r in read('ctr42_band_contract.csv')}
    tmap={r['target_id']:r for r in targets}
    check('six unique retained targets',len(targets)==len(tmap)==6 and all(t['retained']=='True' for t in targets))
    check('distinct coordinates',len({(t['x_32628_m'],t['y_32628_m']) for t in targets})==6)
    smap={r['path']:r for r in sources}
    for s in sources:
        path=ROOT/s['path']; st=path.stat()
        check('source size and timestamp unchanged '+s['path'],st.st_size==int(s['bytes']) and st.st_mtime_ns==int(s['mtime_ns']))
        if path.suffix.lower() in ['.shp','.shx','.dbf','.prj','.cpg','.xml']:
            check('fresh small-source hash '+s['path'],sha(path)==s['sha256'])
    # Independently parse original SHP point doubles and DBF Name/Class records.
    base=ROOT/'data/raw/SHP/POI_S2C_ACOLITE_targets'
    raw=base.with_suffix('.shp').read_bytes(); points=[]; pos=100
    check('SHP point header',struct.unpack_from('<i',raw,32)[0]==1)
    while pos<len(raw):
        rid, words=struct.unpack_from('>ii',raw,pos)
        kind,x,y=struct.unpack_from('<idd',raw,pos+8)
        check('point geometry '+str(rid),kind==1 and math.isfinite(x) and math.isfinite(y))
        points.append((rid,x,y));pos+=8+words*2
    dbf=base.with_suffix('.dbf').read_bytes()
    count,hlen,rlen=struct.unpack_from('<IHH',dbf,4); fields=[];off=32
    while dbf[off]!=13:
        desc=dbf[off:off+32]; fields.append((desc[:11].split(b'\0')[0].decode(),desc[16]));off+=32
    check('SHP SHX DBF counts',len(points)==count==6 and (len(base.with_suffix('.shx').read_bytes())-100)//8==6)
    for i,(rid,x,y) in enumerate(points):
        rec=dbf[hlen+i*rlen:hlen+(i+1)*rlen];check('active DBF '+str(i),rec[0]==32)
        attrs={};off=1
        for name,size in fields:attrs[name]=rec[off:off+size].decode('utf-8').strip();off+=size
        t=tmap[attrs['Name']]
        check('raw identity geometry '+attrs['Name'],(x,y)==(float(t['x_32628_m']),float(t['y_32628_m'])) and attrs['Class']==t['class_literal'] and rid==int(t['source_record_1based']))
    check('raw CRS sidecar', 'WGS_1984_UTM_Zone_28N' in base.with_suffix('.prj').read_text())
    correspondence=read('ctr47_station_correspondence.csv')
    check('90 unique correspondence rows',len(correspondence)==len({(r['target_id'],r['station_id']) for r in correspondence})==90)
    for r in correspondence:
        t=tmap[r['target_id']]
        d=math.hypot(float(t['x_32628_m'])-float(r['station_x_32628_m']),float(t['y_32628_m'])-float(r['station_y_32628_m']))
        check('station distance '+r['target_id']+r['station_id'],abs(d-float(r['separation_m']))<1e-8 and d>1e-8 and r['exact_geometry_equivalent']=='False')
    ex=read('ctr47_exclusion_mapping.csv')
    check('source exclusions unmapped and preserved',{(r['station_id'],r['class_literal']) for r in ex}=={('AC03','mbp_mud'),('AC04','mpb_mud')} and all(r['exact_mapped_target_ids']=='none' and r['original_exclusion_preserved']=='True' for r in ex))
    for r in ex:
        nearest=min((x for x in correspondence if x['station_id']==r['station_id']),key=lambda x:float(x['separation_m']))
        check('nearest excluded station '+r['station_id'],nearest['target_id']==r['nearest_target_id'] and float(nearest['separation_m'])==float(r['nearest_target_distance_m']))
    # Re-read product XML, not only the previous numerical contract.
    xml=ET.parse(ROOT/next(s['path'] for s in sources if s['path'].endswith('MTD_MSIL2A.xml')))
    tags=collections.defaultdict(list)
    for el in xml.iter():tags[el.tag.split('}')[-1]].append(el)
    check('BOA quantification XML',float(tags['BOA_QUANTIFICATION_VALUE'][0].text)==10000)
    check('BOA offsets XML',all(float(e.text)==-1000 for e in tags['BOA_ADD_OFFSET']))
    check('special values XML',{int(e.text) for e in tags['SPECIAL_VALUE_INDEX']}=={0,65535})
    check('product platform and baseline',tags['SPACECRAFT_NAME'][0].text=='Sentinel-2B' and tags['PROCESSING_BASELINE'][0].text=='05.12')
    tile=ET.parse(ROOT/next(s['path'] for s in sources if s['path'].endswith('MTD_TL.xml')))
    tile_values={e.tag.split('}')[-1]:e.text for e in tile.iter()}
    check('raw tile CRS and sensing time',tile_values['HORIZONTAL_CS_CODE']=='EPSG:32628' and tile_values['SENSING_TIME']=='2026-03-07T11:45:54.425534Z')
    headers=json.loads((P/'outputs/ctr47_raster_headers.json').read_text())
    wm={}
    for w in windows:
        vals=json.loads(w['values_json']);flat=[v for row in vals for v in row]
        check('window shape/hash '+str(len(CHECKS)),len(vals)==int(w['rows']) and all(len(row)==int(w['cols']) for row in vals) and hashlib.sha256(struct.pack('<'+'d'*len(flat),*flat)).hexdigest()==w['raw_float64_le_sha256'])
        key=tuple(w[k] for k in ['target_id','band_id','correction','kind','layer'])
        check('unique window '+str(key),key not in wm);wm[key]=w
    satmap={tuple(r[k] for k in ['target_id','band_id','correction']):r for r in sat}
    expected={(t,b,c) for t in tmap for b in BANDS for c in ['Sen2Cor','ACOLITE']}
    check('108 exact target band correction keys',len(sat)==108 and set(satmap)==expected)
    plot=[]
    for key in sorted(expected,key=lambda x:(x[0],BANDS.index(x[1]),x[2])):
        r=satmap[key];t=tmap[key[0]];c=contract[key[1]];h=headers[r['source_path']]
        rawv=float(r['raw_value']);value=float(r['reflectance']);gt=h['geoTransform']
        x,y=float(t['x_32628_m']),float(t['y_32628_m'])
        col=math.floor((x-gt[0])/gt[1]);row=math.floor((y-gt[3])/gt[5])
        check('grid correspondence '+str(key),gt[2]==gt[4]==0 and (col,row)==(int(r['col_0based']),int(r['row_0based'])) and 0<=col<h['size'][0] and 0<=row<h['size'][1])
        bounds=[gt[0]+col*gt[1],gt[3]+(row+1)*gt[5],gt[0]+(col+1)*gt[1],gt[3]+row*gt[5]]
        check('cell bounds '+str(key),bounds==json.loads(r['cell_bounds_EPSG32628_json']) and float(r['stored_resolution_m'])==gt[1])
        check('target label coordinates units '+str(key),r['class_literal']==t['class_literal'] and r['x_32628_m']==t['x_32628_m'] and r['y_32628_m']==t['y_32628_m'] and r['unit']=='1')
        check('band and source contract '+str(key),int(r['band_order_1based'])==BANDS.index(key[1])+1 and r['wavelength_nm']==c['acolite_wavelength_nm'] and r['source_path']==c['sen2cor_path' if key[2]=='Sen2Cor' else 'acolite_path'] and r['source_sha256']==smap[r['source_path']]['sha256'])
        w=wm[(*key,'radiometry','1')]
        check('raw window correspondence '+str(key),json.loads(w['values_json'])==[[rawv]] and int(w['col_start'])==col and int(w['row_start'])==row and w['source_path']==r['source_path'])
        if key[2]=='Sen2Cor':
            decoded=(rawv-1000)/10000
            check('valid Sen2Cor DN '+str(key),rawv not in [0,65535] and rawv==int(rawv) and h['bands'][0]['type']=='UInt16')
        else:
            global_meta=h['metadata']['']
            check('ACOLITE acquisition metadata '+str(key),global_meta['NC_GLOBAL#isodate']=='2026-03-07T11:45:54.425534+00:00' and global_meta['NC_GLOBAL#sensor']=='S2B_MSI' and global_meta['NC_GLOBAL#tile_code']=='T28QCH')
            decoded=rawv;band=h['bands'][0];meta=band['metadata']['']
            check('ACOLITE quantity scale '+str(key),band['type']=='Float32' and band['unit']=='1' and band.get('scale',1)==1 and band.get('offset',0)==0 and band['noDataValue']=='NaN' and meta['standard_name']=='surface_bidirectional_reflectance' and meta['NETCDF_VARNAME']==c['acolite_variable'])
        check('independent decode '+str(key),math.isfinite(value) and decoded==value and r['availability_reason']=='available_stored_value' and (value<0)==(r['negative_retained']=='True'))
        plot.append(dict(target_id=key[0],class_literal=t['class_literal'],display_label=t['display_label'],band_id=key[1],band_order_1based=BANDS.index(key[1])+1,wavelength_nm=float(r['wavelength_nm']),correction=key[2],reflectance=value,finite=True,unit='1',SCL_flag=r['SCL_cloud_shadow_invalid_flag'],segment_id=1))
    for q in qa:
        w=wm[tuple(q[k] for k in ['target_id','band_id','correction','kind','layer'])]
        counts=dict(collections.Counter(str(int(v)) for row in json.loads(w['values_json']) for v in row))
        check('QA raw counts '+str(len(CHECKS)),counts==json.loads(q['cell_counts_json']))
        if q['kind']=='SCL':
            r=satmap[q['target_id'],q['band_id'],q['correction']]
            check('SCL flag correspondence '+str(len(CHECKS)),counts==json.loads(r['SCL_counts_json']) and (bool(set(counts)&{'0','1','2','3','8','9','10','11'}))==(r['SCL_cloud_shadow_invalid_flag']=='True'))
    check('T2 cirrus indicator all footprints',all(set(json.loads(q['cell_counts_json']))=={'10'} for q in qa if q['target_id']=='T2' and q['kind']=='SCL'))
    check('T2 cloud probability zero all footprints',any(q['kind']=='CLDPRB' for q in qa) and all(set(json.loads(q['cell_counts_json']))=={'0'} for q in qa if q['target_id']=='T2' and q['kind']=='CLDPRB'))
    cells=collections.Counter((r['source_path'],r['col_0based'],r['row_0based']) for r in sat)
    check('no targets share stored source cells',max(cells.values())==1)
    scene=json.loads((P/'provenance/ctr47_scene_pair.json').read_text())
    check('same sensing time recorded',scene['sen2cor_tile']['SENSING_TIME'][0].replace('Z','+00:00')==scene['acolite']['isodate'])
    # Rebuild pairs from long input rather than trusting author differences.
    oldmap={(r['target_id'],r['band_id']):r for r in old};pairs=[]
    check('54 unique author pairs',len(old)==len(oldmap)==54)
    for t in sorted(tmap):
        for i,b in enumerate(BANDS,1):
            s=float(satmap[t,b,'Sen2Cor']['reflectance']);a=float(satmap[t,b,'ACOLITE']['reflectance']);d=s-a;o=oldmap[t,b]
            check('independent pair '+t+b,s==float(o['Sen2Cor']) and a==float(o['ACOLITE']) and d==float(o['Sen2Cor_minus_ACOLITE']) and o['finite_pair']=='True')
            pairs.append(dict(target_id=t,class_literal=tmap[t]['class_literal'],band_id=b,band_order_1based=i,wavelength_nm=float(contract[b]['acolite_wavelength_nm']),Sen2Cor=s,ACOLITE=a,Sen2Cor_minus_ACOLITE=d,finite_pair=True,unit='1',SCL_flag=t=='T2'))
    def summary(rows):
        ds=[r['Sen2Cor_minus_ACOLITE'] for r in rows]
        return dict(n_pairs=len(ds),mean_signed=statistics.fmean(ds),median_signed=statistics.median(ds),mean_absolute_difference=statistics.fmean(abs(d) for d in ds),min_signed=min(ds),max_signed=max(ds),n_positive=sum(d>0 for d in ds),n_negative=sum(d<0 for d in ds),n_zero=sum(d==0 for d in ds))
    ts=[dict(target_id=t,**summary([r for r in pairs if r['target_id']==t])) for t in sorted(tmap)]
    bs=[dict(band_id=b,**summary([r for r in pairs if r['band_id']==b])) for b in BANDS]
    # Adjacent steps describe shape without normalisation or model assumptions.
    steps=[]
    for t in sorted(tmap):
        for i in range(8):
            b0,b1=BANDS[i:i+2];s0=float(satmap[t,b0,'Sen2Cor']['reflectance']);s1=float(satmap[t,b1,'Sen2Cor']['reflectance']);a0=float(satmap[t,b0,'ACOLITE']['reflectance']);a1=float(satmap[t,b1,'ACOLITE']['reflectance'])
            steps.append(dict(target_id=t,from_band=b0,to_band=b1,Sen2Cor_step=s1-s0,ACOLITE_step=a1-a0,step_difference=(s1-s0)-(a1-a0),same_direction=((s1>s0)-(s1<s0))==((a1>a0)-(a1<a0))))
    scales=[]
    for t in ['ALL']+sorted(tmap):
        vals=[r['reflectance'] for r in plot if t=='ALL' or r['target_id']==t];lo,hi=min(vals),max(vals);pad=.05*(hi-lo)
        scales.append(dict(target_id=t,data_min=lo,data_max=hi,suggested_ymin=lo-pad,suggested_ymax=hi+pad))
    for name,rows in [('plot_values',plot),('pairs',pairs),('target_summary',ts),('band_summary',bs),('spectral_steps',steps),('scale_ranges',scales)]:write('ctr48_'+name+'.csv',rows)
    write('ctr48_accounting.csv',[dict(target_id=t,class_literal=tmap[t]['class_literal'],requested_bands=9,finite_Sen2Cor=9,finite_ACOLITE=9,finite_pairs=9,missing_pairs=0,negative_Sen2Cor=sum(r['reflectance']<0 for r in plot if r['target_id']==t and r['correction']=='Sen2Cor'),negative_ACOLITE=0,SCL_flag=t=='T2',retained=True) for t in sorted(tmap)])
    result=dict(status='pass',input_revision=INPUT_REV,check_count=len(CHECKS),checks=CHECKS,input_sha256=input_hashes,script_sha256=sha(Path(__file__)),python=platform.python_version(),counts=dict(targets=6,bands=9,values=len(plot),finite_pairs=len(pairs),negative_values=sum(r['reflectance']<0 for r in plot),missing_pairs=0),global_observed_range=[min(r['reflectance'] for r in plot),max(r['reflectance'] for r in plot)],summary=summary(pairs),preservation=dict(tracked_files=len(before['tracked_sha256']),unrelated_files=len(before['unrelated_ctr39_sha256'])),raster_reads_performed=0,source_integrity_scope='exact committed predecessor hashes; current source stat checks and fresh small-sidecar/XML hashes; full raster hashes and independent CLI samples reused from CTR47',scientific_approval=False,output_sha256={f.name:sha(f) for f in sorted((P/'tables').glob('ctr48_*.csv'))})
    dump('ctr48_validation.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['checks','input_sha256','output_sha256']},indent=2))

if __name__=='__main__':main()
