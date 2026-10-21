#!/usr/bin/env python3
"""Add SAFE band definitions and spreadsheet schema context, reading metadata only.
Run after inventory.py from project root. No raster/feature/observation reads.
"""
import csv,datetime,hashlib,importlib.util,json,zipfile
from pathlib import Path
import xml.etree.ElementTree as E
spec=importlib.util.spec_from_file_location('inventory',Path(__file__).with_name('inventory.py'))
i=importlib.util.module_from_spec(spec);spec.loader.exec_module(i)
O=i.OUT; R=i.ROOT
headers=json.loads((O/'outputs/headers.json').read_text())
rows=[r for r in csv.DictReader((O/'tables/variable_dictionary.csv').open()) if 'SAFE Spectral_Information' not in r.get('description','') and r.get('definition_status')!='metadata_reference_header']
def local(e):return e.tag.split('}')[-1]
def safe(data,source):
 root=E.fromstring(data); extra={'band_definitions':[],'geocoding':[],'scaling_and_quality':[],'product_identity':[]}
 for e in root.iter():
  tag=local(e)
  if tag=='Spectral_Information':
   desc={local(c):c.text.strip() if c.text else '' for c in e if not len(c)}
   for c in e:
    if len(c):desc[local(c)]={local(d):{'value':d.text,'attributes':d.attrib} for d in c}
   desc.update(e.attrib);extra['band_definitions'].append(desc)
  if tag in ['Size','Geoposition','HORIZONTAL_CS_NAME','HORIZONTAL_CS_CODE']:
   extra['geocoding'].append({'tag':tag,'attributes':e.attrib,'text':(e.text or '').strip(),'children':{local(c):c.text for c in e}})
  if tag in ['BOA_QUANTIFICATION_VALUE','AOT_QUANTIFICATION_VALUE','WVP_QUANTIFICATION_VALUE','BOA_ADD_OFFSET','SPECIAL_VALUE_TEXT','SPECIAL_VALUE_INDEX','Scene_Classification_ID','Scene_Classification_TEXT']:
   extra['scaling_and_quality'].append({'tag':tag,'attributes':e.attrib,'text':(e.text or '').strip()})
  if tag in ['PRODUCT_START_TIME','PRODUCT_STOP_TIME','PROCESSING_LEVEL','SPACECRAFT_NAME','SENSING_TIME','GENERATION_TIME','PROCESSING_BASELINE']:
   extra['product_identity'].append({'tag':tag,'attributes':e.attrib,'text':(e.text or '').strip()})
 for b in extra['band_definitions']:
  b.pop('Spectral_Response',None)
  offset=next((x['text'] for x in extra['scaling_and_quality'] if x['tag']=='BOA_ADD_OFFSET' and x['attributes'].get('band_id')==b.get('bandId')),i.UNKNOWN)
  quant=next((x['text'] for x in extra['scaling_and_quality'] if x['tag']=='BOA_QUANTIFICATION_VALUE'),i.UNKNOWN)
  special=[]; label=None
  for x in extra['scaling_and_quality']:
   if x['tag']=='SPECIAL_VALUE_TEXT':label=x['text']
   elif x['tag']=='SPECIAL_VALUE_INDEX' and label:special.append(label+'='+x['text'])
  b['encoding_metadata']=extra['scaling_and_quality']
  i.var(source,b.get('physicalBand',b.get('bandId','unknown')),add_offset=offset,quantification_value=quant,nodata='; '.join(special) if special else i.UNKNOWN,description='SAFE Spectral_Information physicalBand',dimensions='declared native resolution '+str(b.get('RESOLUTION',i.UNKNOWN))+' m',evidence=source+' :: Spectral_Information',attributes_json=json.dumps(b))
 return extra
for source,h in headers.items():
 rootkey,path=source.split(':',1);p=i.roots[rootkey]/path
 if p.suffix=='.zip' and '/S2/' in '/'+path:
  with zipfile.ZipFile(p) as z:
   h['safe_structured_metadata']={e.filename:safe(z.read(e),source+'!'+e.filename) for e in z.infolist() if e.filename.split('/')[-1].startswith('MTD_') and e.filename.endswith('.xml') and e.file_size<=i.LIMIT}
 elif p.name.startswith('MTD_') and p.suffix=='.xml':
  h['safe_structured_metadata']=safe(p.read_bytes(),source)
 if p.suffix=='.nc' and 'ACOLITE' in source:
  h['/']['attributes'].pop('ac_aot_550_mean',None)
 # Remove any cached observation summary fields from GDAL metadata (no summaries computed).
 if isinstance(h,dict) and 'bands' in h:
  for b in h['bands']:
   b.pop('minimum',None);b.pop('maximum',None);b.pop('mean',None);b.pop('stdDev',None)
   for d,m in b.get('metadata',{}).items():
    for k in list(m):
     if k.startswith('STATISTICS_'):del m[k]
 # Attach xlsx number-format definitions + schema types/styles from first data row only.
 if p.suffix=='.xlsx':
  with zipfile.ZipFile(p) as z:
   ns=i.NS;styles=E.fromstring(z.read('xl/styles.xml'));formats={x.get('numFmtId'):x.get('formatCode') for x in styles.findall('m:numFmts/m:numFmt',ns)}
   xfs=styles.findall('m:cellXfs/m:xf',ns)
   h['number_formats']={'custom_formats':formats,'cell_style_numFmtIds':[x.get('numFmtId') for x in xfs],'built_in_formats':'OOXML built-in IDs retained; not decoded'}
   for sh in h['sheets']:
    if sh['schema_strategy'].startswith('first row'):
     with z.open(sh['xml']) as f:
      n=0
      for event,el in E.iterparse(f,events=['end']):
       if local(el)=='row':
        n+=1
        if n==2:
         sh['first_data_row_storage_schema']=[{'column':''.join(filter(str.isalpha,c.get('r',''))),'type':c.get('t','n'),'style':c.get('s','0')} for c in el];break
# Supplemental nonrectangular reference sheets: literal columns from bounded headers.
for source,h in headers.items():
 if not source.endswith('.xlsx') or 'COPE-' not in source:continue
 for col,head in [('B','band identifier'),('C','S2A'),('D','S2B'),('E','S2C')]:
  i.var(source,'Equivalent Wavelengths!'+col+':'+head,'OOXML metadata column',units='nm' if col!='B' else 'identifier',description='supplied equivalent-wavelength reference column; no calculation',evidence=source+' :: Equivalent Wavelengths!C2:E3',definition_status='metadata_reference_header')
 for col,head in [('A','band identifier'),('B','S2A Wa'),('C','S2A Bandwidth'),('D','S2B Wa'),('E','S2B Bandwidth'),('F','S2C Wa'),('G','S2C Bandwidth')]:
  i.var(source,'Bandwidth and mid-wavelength!'+col+':'+head,'OOXML metadata column',units='nm' if col!='A' else 'identifier',description='literal combined header; supplied reference, not recalculated',evidence=source+' :: Bandwidth and mid-wavelength!A3:G5',definition_status='metadata_reference_header')
 for col,head in zip('ABCDEFGHIJK',['band identifier','mid-wavelength min','mid-wavelength avg','mid-wavelength max','mid-wavelength max-min','mid-wavelength std','Bandwidth min','Bandwidth avg','Bandwidth max','Bandwidth max-min','Bandwidth std']):
  i.var(source,'Variation S2C ISRF over pixels!'+col+':'+head,'OOXML metadata column',units='nm' if col!='A' else 'identifier',description='literal supplied reference header; no summary recomputed',evidence=source+' :: Variation  S2C ISRF over pixels!A1:K5',definition_status='metadata_reference_header')
# Improve GDAL band definitions from each band's embedded header metadata.
for r in rows:
 h=headers.get(r['source'],{})
 if 'bands' in h and r['variable'].startswith('band_'):
  b=next(b for b in h['bands'] if str(b['band'])==r['variable'].split('_')[-1]);a=b.get('metadata',{}).get('',{})
  r['description']=b.get('description',a.get('long_name',i.UNKNOWN))
  r['attributes_json']=json.dumps(a,ensure_ascii=False)
# Semantic definitions below deliberately preserve unknown units/codes.
notes={
 'wl':'literal label; wavelength interpretation inferred from abbreviation, unit not declared',
 'station':'literal station identifier; not normalized or joined',
 'cover':'cover field; field log describes seagrass-cover measurements; unit and scoring protocol undocumented',
 'gps':'literal gps field; identifier meaning is source-specific and undocumented',
 'picture':'literal picture reference; referenced photographs not established by this inventory',
 'comment':'free-text/code field; ecological abbreviations have no supplied codebook',
 'cores':'literal cores field; counting/protocol meaning undocumented',
 'loripes':'literal loripes field; meaning, units and missing-code convention undocumented',
 'waypoint':'literal waypoint identifier; coordinate precision/datum not declared in workbook',
 'poskey':'literal poskey field; relationship/key definition undocumented',
 'date':'literal date field; Excel numeric cell type and style retained in headers.json',
 'location':'literal location label; not verified geographic coverage',
 'lat':'literal lat field; latitude interpretation inferred from abbreviation; units and datum undocumented',
 'lon':'literal lon field; longitude interpretation inferred from abbreviation; units and datum undocumented',
 'Zone':'literal Zone label; classification scheme undocumented',
 'Date':'literal date column; supplied script missing_dates_5P.m describes common-date export; result not recomputed'}
for r in rows:
 if r['source'].startswith(('project_raw:ASD/','project_raw:GPS/')) or r['source'].endswith('S2_S5P_common_dates.csv'):
  name=r['variable'].split('!')[-1]
  if name in notes:r['description']=notes[name]
  elif r['source'].endswith('202603_Reflectance_avg.txt'):
   r['description']='literal spectrum/station column; reflectance interpretation inferred from filename and field log; unit, scaling, averaging protocol and link not verified'
  if name=='cover':r['evidence']+='; ASD/202603_Measurement_log.txt (seagrass cover context only)'
rows+=i.variables
# Preserve exact band attributes; do not transfer SAFE scaling onto ACOLITE products.
i.csvout(O/'tables/variable_dictionary.csv',rows)
i.dump(O/'outputs/headers.json',headers)
i.dump(O/'provenance/enrichment_run.json',{'utc':i.UTC(),'script':'scripts/enrich_metadata.py','method':'SAFE XML metadata and OOXML schema only','added_SAFE_band_rows':len(i.variables),'total_variable_rows':len(rows),'observation_values':'not analyzed or exported','cached_raster_statistics':'omitted','inputs_stat_fingerprint':'see inventory_run.json'})
print('Added SAFE band metadata rows:',len(i.variables),'total variable rows:',len(rows))
