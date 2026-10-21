"""Pixel preservation QA with already-installed worker system Pillow."""
from pathlib import Path
from PIL import Image, ImageChops, __version__
import io
import json
import subprocess

A = Path(__file__).resolve().parents[1]
ROOT = A.parents[1]
p = A / 'figures/generated/ctr49_target_spectra_custom.png'
old_bytes = subprocess.check_output(['git', 'show', '4e4e46b3b05fb30ef11549c28f5e96e7a40f1bcc:' + str(p.relative_to(ROOT))], cwd=ROOT)
old = Image.open(io.BytesIO(old_bytes)).convert('RGB')
new = Image.open(p).convert('RGB')
assert old.size == new.size
box = ImageChops.difference(old, new).getbbox()
assert box is not None
assert box[0] > new.width / 2 and box[3] < new.height / 4, box
# Only the removed T2 note may differ, leaving blank white background.
assert new.crop(box).getextrema() == ((255, 255), (255, 255), (255, 255))
print(json.dumps({'only_changed_pixels_bbox': box, 'png_size': old.size, 'changed_region_is_white': True, 'Pillow_version': __version__}))
