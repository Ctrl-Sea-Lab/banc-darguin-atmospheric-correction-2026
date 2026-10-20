"""Verify display contract and immutability against the completed delivery."""
from common import *
import math, struct
j=json.loads((A/'provenance/figure_v2.json').read_text())
with (A/'provenance/output_hashes.csv').open() as f: old={r['path']:r for r in csv.DictReader(f)}
checked=[]
for r in j['raster_hashes']:
    p=A/r['path']; assert sha(p)==r['sha256']==old[r['path']]['sha256']
    m=info(p)
    assert m['size']==[3763,1974] and m['geoTransform']==[334050,10,0,2209980,0,-10]
    assert m['coordinateSystem']['wkt'].endswith('ID["EPSG",32628]]')
    assert m['bands'][0]['noDataValue']==-9999 and m['bands'][0]['unit']=='1'
    checked.append(r['path'])
for p in ['tables/date_band_summary.csv','provenance/input_hashes.csv','provenance/validation.json','provenance/processing.json','figures/generated/paired_reflectance_maps.png','figures/generated/paired_reflectance_maps.pdf']:
    assert sha(A/p)==old[p]['sha256']; checked.append(p)
with (A/'tables/color_anchors_v2.csv').open() as f: anchors=list(csv.DictReader(f))
assert [(float(r['sd']),r['hex']) for r in anchors]==[(0,'#2166AC'),(.01,'#FFFFFF'),(.02,'#B2182B')]
for r in anchors: assert int(r['index'])==1+math.floor(float(r['sd'])/.02*256+.5) and r['pass']=='TRUE'
with (A/'tables/panel_geometry_v2.csv').open() as f: geom=list(csv.DictReader(f))
assert len(geom)==8
for r in geom:
    assert math.isclose(float(r['width_inches'])/float(r['height_inches']),3763/1974,rel_tol=1e-10)
    assert float(r['width_inches'])>14/4.32 # exceeds even the old layout's gross panel allocation
    assert [int(r[k]) for k in ['xmin','xmax','ymin','ymax']]==[334050,371680,2190240,2209980]
for r in j['outputs']:
    assert sha(A/r['path'])==r['sha256']
png=A/'figures/generated/paired_reflectance_maps_v2.png'
assert struct.unpack('>II',png.read_bytes()[16:24])==(8000,2440)
result=dict(result='pass',immutable_completed_products_checked=checked,rasters_metadata_checked=8,color_anchors_checked=3,panels_checked=8,panel_width_inches=4.42,panel_height_inches=float(geom[0]['height_inches']),geographic_aspect_ratio_preserved=True,full_extent_preserved=True,PNG_dimensions=[8000,2440],scientific_processing_repeated=False,independent_scientific_review='pending CTR-59',PI_scientific_approval='pending',report_display_verification='assigned to Alan on CTR-58 after Rachel integration on CTR-57')
save(A/'provenance/figure_v2_validation.json',result)
print(json.dumps(result,indent=2))
