#!/usr/bin/env python3
"""Read-only filesystem and header inventory. No observation arrays are read.
Run from project root: .venv/bin/python analysis/CTR-24_data-dictionary/scripts/inventory.py
Uses Python stdlib, installed libnetcdf, and gdalinfo; never installs packages.
"""
import csv,ctypes as C,ctypes.util,datetime as D,hashlib,io,json,os,platform,struct,subprocess,sys,zipfile
from pathlib import Path
from collections import Counter
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parents[1]
UTC=lambda:D.datetime.now(D.timezone.utc).isoformat()
UNKNOWN='undocumented'
LIMIT=4*1024*1024
roots={'project_raw':ROOT/'data/raw','project_processed':ROOT/'data/processed',
'nas_raw':Path('/mnt/PaperClip_Projects/data/raw/banc-darguin-atmospheric-correction-2026'),
'nas_processed':Path('/mnt/PaperClip_Projects/data/processed/banc-darguin-atmospheric-correction-2026')}
files=[];archives=[];variables=[];headers={};errors=[];commands=[]
def dump(path,obj):
 path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,default=str)+'\n')
def run(args):
 commands.append(args)
 e=os.environ.copy();e.update(GDAL_PAM_ENABLED='NO',CPL_TMPDIR='/tmp',PROJ_NETWORK='OFF')
 p=subprocess.run(args,capture_output=True,text=True,env=e,timeout=45)
 if p.returncode: raise RuntimeError(p.stderr[:1500])
 return p.stdout

def group(rel):
 s=rel.split('/')
 if s[0]=='S2':
  return '/'.join(s[:2]) if s[1] in ['ACOLITE','Sen2Cor'] else 'S2/expanded_SAFE'
 return s[0] if len(s)>1 else ('spectral_response_reference' if rel.endswith('.xlsx') else 'placeholder')
def role(p):
 if p.name=='.gitkeep':return 'repository_placeholder'
 if p.suffix=='.m':return 'supplied_code_not_executed'
 if p.suffix.lower() in ['.png','.jpg','.html','.xsl']:return 'supplied_preview_or_documentation'
 if p.suffix.lower() in ['.prj','.cpg','.shx','.dbf','.xml','.xsd','.safe','.qmd']:return 'metadata_or_vector_sidecar'
 if p.suffix=='.txt' and ('log' in p.name.lower() or 'settings' in p.name.lower()):return 'supplied_processing_or_field_documentation'
 return 'supplied_data_or_reference'
def scan():
 result=[]
 for key,base in roots.items():
  if not base.exists(): errors.append({'source':str(base),'error':'root missing'});continue
  def walk(d):
   try: children=sorted(d.iterdir())
   except OSError as e: errors.append({'source':str(d),'error':str(e)});return
   for p in children:
    # No symlink directories are followed: conservative, no aliases counted twice.
    if p.is_symlink():
     st=p.lstat();result.append({'root':key,'path':str(p.relative_to(base)),'size_bytes':st.st_size,'mtime_ns':st.st_mtime_ns,'mode':oct(st.st_mode&0o7777),'uid':st.st_uid,'gid':st.st_gid,'kind':'symlink','target':os.readlink(p)})
    elif p.is_dir():walk(p)
    else:
     st=p.stat();result.append({'root':key,'path':str(p.relative_to(base)),'size_bytes':st.st_size,'mtime_ns':st.st_mtime_ns,'mode':oct(st.st_mode&0o7777),'uid':st.st_uid,'gid':st.st_gid,'kind':'file','target':''})
  walk(base)
 return result

def var(source,name,dtype=UNKNOWN,units=UNKNOWN,description=UNKNOWN,**kw):
 rec=dict(source=source,variable=name,storage_type=dtype,units=units,description=description,dimensions=UNKNOWN,scale_factor=UNKNOWN,add_offset=UNKNOWN,nodata=UNKNOWN,quality_flags=UNKNOWN,evidence=source,definition_status='header_or_schema; meanings absent unless explicitly stated')
 rec.update(kw);variables.append(rec)

def xml_metadata(data):
 root=E.fromstring(data); result={}
 def walk(el,path):
  tag=el.tag.split('}')[-1]; here=path+'/'+tag
  if tag in ['Values_List','VALUES','EXT_POS_LIST','MASK_VALUES','Pixel_Level_QI']:return
  if len(el)==0 and el.text and el.text.strip() and len(el.text)<1500:
   result.setdefault(here,[]).append({'text':el.text.strip(),'attributes':el.attrib})
  elif len(el):
   for child in el:walk(child,here)
 walk(root,'');return result

# netCDF C API: only nc_inq_* and nc_get_att_* are allowed; no nc_get_var* calls.
class NC:
 def __init__(self):
  lib=ctypes.util.find_library('netcdf')
  if not lib:raise RuntimeError('libnetcdf unavailable')
  self.l=C.CDLL(lib);self.l.nc_strerror.restype=C.c_char_p
  self.l.nc_inq_libvers.restype=C.c_char_p
 def check(self,r):
  if r:raise RuntimeError(self.l.nc_strerror(r).decode())
 def attrs(self,g,v,n):
  result={}
  for a in range(n):
   name=C.create_string_buffer(257);self.check(self.l.nc_inq_attname(g,v,a,name));t=C.c_int();length=C.c_size_t()
   self.check(self.l.nc_inq_att(g,v,name,C.byref(t),C.byref(length)))
   if length.value>65536:result[name.value.decode()]={'omitted_length':length.value};continue
   if t.value==2:
    buf=C.create_string_buffer(length.value+1);self.check(self.l.nc_get_att_text(g,v,name,buf));val=buf.raw[:length.value].decode('utf-8','replace')
   elif t.value==12:
    buf=(C.c_char_p*length.value)();self.check(self.l.nc_get_att_string(g,v,name,buf));val=[x.decode('utf-8','replace') if x else '' for x in buf];self.l.nc_free_string(C.c_size_t(length.value),buf)
   else:
    buf=(C.c_double*length.value)();self.check(self.l.nc_get_att_double(g,v,name,buf));val=list(buf)
    if len(val)==1:val=val[0]
   result[name.value.decode()]=val
  return result
 def read(self,p,source):
  n=C.c_int();self.check(self.l.nc_open(os.fsencode(p),0,C.byref(n)))
  types={1:'byte',2:'char',3:'short',4:'int',5:'float',6:'double',7:'ubyte',8:'ushort',9:'uint',10:'int64',11:'uint64',12:'string'}
  result={}
  def walk(g,path):
   na=C.c_int();self.check(self.l.nc_inq_natts(g,C.byref(na)));a=self.attrs(g,-1,na.value)
   result[path]={'attributes':a,'variables':[]}
   count=C.c_int();self.check(self.l.nc_inq_varids(g,C.byref(count),None));ids=(C.c_int*count.value)();self.check(self.l.nc_inq_varids(g,C.byref(count),ids))
   for vid in ids:
    name=C.create_string_buffer(257);t=C.c_int();nd=C.c_int();na=C.c_int();dims=(C.c_int*1024)()
    self.check(self.l.nc_inq_var(g,vid,name,C.byref(t),C.byref(nd),dims,C.byref(na)))
    shape=[]
    for d in list(dims)[:nd.value]:
     dn=C.create_string_buffer(257);dl=C.c_size_t();self.check(self.l.nc_inq_dim(g,d,dn,C.byref(dl)));shape.append([dn.value.decode(),dl.value])
    at=self.attrs(g,vid,na.value);vn=path.rstrip('/')+'/'+name.value.decode()
    info=dict(name=vn,type=types.get(t.value,str(t.value)),dimensions=shape,attributes=at);result[path]['variables'].append(info)
    var(source,vn,info['type'],at.get('units',UNKNOWN),at.get('long_name',at.get('standard_name',UNKNOWN)),dimensions=json.dumps(shape),scale_factor=at.get('scale_factor',UNKNOWN),add_offset=at.get('add_offset',UNKNOWN),nodata=at.get('_FillValue',at.get('missing_value',UNKNOWN)),quality_flags=json.dumps({k:v for k,v in at.items() if k.startswith('flag_') or k in ['valid_min','valid_max','valid_range']}),evidence=source+' :: netCDF '+vn+' attributes',attributes_json=json.dumps(at,ensure_ascii=False))
   self.check(self.l.nc_inq_grps(g,C.byref(count),None));children=(C.c_int*count.value)();self.check(self.l.nc_inq_grps(g,C.byref(count),children))
   for child in children:
    gn=C.create_string_buffer(257);self.check(self.l.nc_inq_grpname(child,gn));walk(child,path.rstrip('/')+'/'+gn.value.decode())
  try:walk(n.value,'/')
  finally:self.l.nc_close(n.value)
  return result

NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def workbook(p,source):
 with zipfile.ZipFile(p) as z:
  for ent in z.infolist():
   if ent.file_size>20*LIMIT:raise RuntimeError('oversize workbook XML member')
  strings=[]
  if 'xl/sharedStrings.xml' in z.namelist():
   strings=[''.join(el.itertext()) for el in E.fromstring(z.read('xl/sharedStrings.xml'))]
  wb=E.fromstring(z.read('xl/workbook.xml'));rels={r.get('Id'):r.get('Target') for r in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
  result={'sheets':[],'properties':{}}
  for pr in ['docProps/core.xml','docProps/app.xml']:
   if pr in z.namelist():result['properties'][pr]=xml_metadata(z.read(pr))
  for sh in wb.find('m:sheets',NS):
   name=sh.get('name');target=rels[sh.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')];target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
   rows=[];dimension=None
   # Only header rows and declared dimensions: stop before the data body.
   cap=35 if name=='Overview' else (5 if name in ['Equivalent Wavelengths','Bandwidth and mid-wavelength','Variation  S2C ISRF over pixels'] else 2)
   with z.open(target) as stream:
    for ev,el in E.iterparse(stream,events=['end']):
     local=el.tag.split('}')[-1]
     if local=='dimension':dimension=el.get('ref')
     if local=='row':
      row=[]
      for c in el:
       v=c.find('m:v',NS);value=v.text if v is not None else ''.join(c.itertext())
       if c.get('t')=='s' and value:value=strings[int(value)]
       row.append({'cell':c.get('r'),'value':value,'type':c.get('t','n'),'style':c.get('s')})
      rows.append(row)
      if len(rows)>=cap:break
   # For GPS and spectral response data, retain only header labels + first row types, no observation values.
   structured=name=='Sheet1' or name.startswith('Spectral Responses')
   if structured and rows:
    typing={''.join(filter(str.isalpha,c['cell'])):c['type'] for c in (rows[1] if len(rows)>1 else [])}
    for c in rows[0]:
     if not c['value']:continue
     col=''.join(filter(str.isalpha,c['cell']));dtype=typing.get(col,UNKNOWN)
     var(source,name+'!'+c['value'],'xlsx cell '+dtype+' (first data row only)',description='literal column label; meaning/units not declared in header',dimensions=dimension,evidence=source+' :: '+name+'!'+c['cell'])
    rows=rows[:1]
   result['sheets'].append({'name':name,'xml':target,'declared_used_range':dimension,'header_rows':rows,'schema_strategy':'first row labels + first data row storage types' if structured else 'bounded metadata/header rows; not rectangular data'})
  return result

def shp(p,source):
 with p.open('rb') as f:h=f.read(100)
 result={'shape_type_code':struct.unpack('<i',h[32:36])[0],'header_bounds_xy':struct.unpack('<4d',h[36:68]),'fields':[]}
 for suffix in ['.prj','.cpg']:
  side=p.with_suffix(suffix)
  result[suffix]=side.read_text() if side.exists() else UNKNOWN
 db=p.with_suffix('.dbf')
 with db.open('rb') as f:
  h=f.read(32);length=struct.unpack('<H',h[8:10])[0];result['declared_records']=struct.unpack('<I',h[4:8])[0]
  while f.tell()<length:
   desc=f.read(32)
   if not desc or desc[0]==13:break
   name=desc[:11].split(b'\x00')[0].decode('utf-8','replace');t=chr(desc[11]);width=desc[16];dec=desc[17]
   result['fields'].append({'name':name,'dbf_type':t,'width':width,'decimals':dec})
   var(source,name,f'DBF {t} width={width} decimals={dec}',evidence=str(db.relative_to(ROOT))+' :: field descriptor '+name)
 return result

def csvout(path,rows,required=()):
 keys=list(dict.fromkeys(list(required)+[k for r in rows for k in r]))
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,keys,lineterminator="\n");w.writeheader();w.writerows(rows)

def main():
 start=UTC();before=scan();nc=NC()
 for rec in before:
  key=rec['root'];rel=rec['path'];p=roots[key]/rel;source=key+':'+rel
  rec.update(group=group(rel),format=p.suffix.lower().lstrip('.') or 'no_extension',role=role(p),metadata_status='inventory_only',source_snapshot=start)
  if rec['kind']=='symlink':rec['metadata_status']='symlink_not_followed';files.append(rec);continue
  try:
   result=None
   if p.suffix.lower()=='.zip':
    with zipfile.ZipFile(p) as z:
     md={}
     for e in z.infolist():
      archives.append(dict(source=source,member=e.filename,uncompressed_bytes=e.file_size,compressed_bytes=e.compress_size,crc32=f'{e.CRC:08x}',is_directory=e.is_dir(),compression=e.compress_type))
      if e.filename.endswith(('.xml','.prj','.cpg','.qmd')) and e.file_size<=LIMIT:
       if e.filename.endswith(('.prj','.cpg')):md[e.filename]=z.read(e).decode('utf-8','replace')
       elif e.filename.split('/')[-1].startswith(('MTD_','manifest')):md[e.filename]=xml_metadata(z.read(e))
      if e.filename.endswith('.dbf'):
       with z.open(e) as stream:
        dbhead=stream.read(32);length=struct.unpack('<H',dbhead[8:10])[0];fielddata=stream.read(min(length-32,65536));fields=[]
        for off in range(0,len(fielddata),32):
         d=fielddata[off:off+32]
         if len(d)<32 or d[0]==13:break
         name=d[:11].split(b'\x00')[0].decode('utf-8','replace');fields.append(name)
         var(source+'!'+e.filename,name,f'DBF {chr(d[11])} width={d[16]} decimals={d[17]}',evidence='ZIP member DBF field descriptor')
        md[e.filename]={'declared_records':struct.unpack('<I',dbhead[4:8])[0],'fields':fields}
     result={'members':len(z.infolist()),'selected_metadata':md,'method':'central directory; bounded XML and DBF headers; no extraction'}
   elif p.suffix.lower()=='.xlsx':result=workbook(p,source)
   elif p.suffix.lower()=='.nc':result=nc.read(p,source)
   elif p.suffix.lower() in ['.tif','.tiff','.jp2']:
    # PAM disabled prohibits auxiliary sidecar creation. Never use -stats/-hist/-checksum.
    result=json.loads(run(['gdalinfo','-json','-noct','-nogcp',str(p)]))
    result.pop('stac',None)
    for band in result.get('bands',[]):
     var(source,'band_'+str(band['band']),band.get('type',UNKNOWN),band.get('unit',UNKNOWN),band.get('description',UNKNOWN),dimensions=json.dumps(result.get('size')),scale_factor=band.get('scale',UNKNOWN),add_offset=band.get('offset',UNKNOWN),nodata=band.get('noDataValue',UNKNOWN),quality_flags=json.dumps(band.get('mask',{})),evidence=source+' :: GDAL band '+str(band['band']))
   elif p.suffix.lower()=='.shp':result=shp(p,source)
   elif p.suffix.lower() in ['.txt','.csv']:
    with p.open('r',errors='replace') as f:first=f.readline(65536).rstrip('\r\n')
    if rec['group']=='ASD' and 'log' not in p.name.lower() or p.suffix=='.csv':
     fields=next(csv.reader([first],delimiter='\t' if '\t' in first else (',' if ',' in first else ' ')))
     fields=[x for x in fields if x];result={'literal_fields':fields,'separator':'tab' if '\t' in first else (',' if ',' in first else 'whitespace'),'rows':'not counted; observation body not read'}
     for name in fields:var(source,name,'text serialization; declared column type absent',evidence=source+' :: first-line header')
    elif p.stat().st_size<=65536:result={'supplied_documentation_text':p.read_text(errors='replace')}
    else:result={'first_line':first,'body':'not read'}
   elif p.suffix.lower()=='.xml' and p.stat().st_size<=LIMIT:
    if p.name.startswith(('MTD_','manifest')) or p.name.endswith('.aux.xml'):result=xml_metadata(p.read_bytes())
   elif p.suffix.lower() in ['.prj','.cpg','.qmd'] and p.stat().st_size<=65536:
    result={'metadata_text':p.read_text(errors='replace')}
   if result is not None:headers[source]=result;rec['metadata_status']='header_or_metadata_read'
  except Exception as e:rec['metadata_status']='header_error';errors.append({'source':source,'error':str(e)})
  files.append(rec)
 after=scan();projected=lambda rows:[{k:r[k] for k in ['root','path','size_bytes','mtime_ns','mode','uid','gid','kind','target']} for r in rows]
 stable=projected(before)==after
 snapshot={'started_utc':start,'ended_utc':UTC(),'roots':{k:str(p) for k,p in roots.items()},'root_status':{k:{'exists':p.exists(),'is_symlink':p.is_symlink(),'physical_file_count':sum(r['root']==k and r['kind']=='file' for r in files)} for k,p in roots.items()},'source_snapshot_sha256':hashlib.sha256(json.dumps(projected(before),sort_keys=True).encode()).hexdigest(),'fingerprint_method':'sorted file stat tuples (root/path/bytes/mtime_ns/mode/uid/gid/kind/target); not file-content hashes','stat_snapshot_unchanged':stable,'errors':errors,'physical_files':len(files),'archive_members':len(archives),'variables':len(variables),'python':sys.version,'libnetcdf':nc.l.nc_inq_libvers().decode(),'gdal':run(['gdalinfo','--version']).strip(),'git_head':run(['git','-C',str(ROOT),'rev-parse','HEAD']).strip(),'git_branch':run(['git','-C',str(ROOT),'branch','--show-current']).strip(),'dependency_changes':'none; Python stdlib + installed system GDAL/libnetcdf','source_data_protection':'read-only opens; GDAL_PAM_ENABLED=NO; no permission changes; no full-data checksums','symlink_policy':'symlink entries inventoried, never traversed; root symlinks explicitly reported','commands':commands,'group_file_counts':dict(Counter(r['group'] for r in files))}
 for folder in ['tables','outputs','provenance']: (OUT/folder).mkdir(exist_ok=True)
 csvout(OUT/'tables/file_inventory.csv',files)
 csvout(OUT/'tables/archive_inventory.csv',archives,('source','member','uncompressed_bytes','compressed_bytes','crc32'))
 csvout(OUT/'tables/variable_dictionary.csv',variables,('source','variable','storage_type','units','description','dimensions','scale_factor','add_offset','nodata','quality_flags','evidence'))
 dump(OUT/'outputs/headers.json',headers);dump(OUT/'provenance/inventory_run.json',snapshot)
 print(json.dumps({k:v for k,v in snapshot.items() if k not in ['commands']},indent=2))
 if not stable or errors:print('Inventory has gaps or changed source metadata; inspect provenance.',file=sys.stderr)
if __name__=='__main__':main()
