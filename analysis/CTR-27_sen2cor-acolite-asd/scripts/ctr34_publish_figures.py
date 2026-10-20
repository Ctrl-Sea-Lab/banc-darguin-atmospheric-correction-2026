#!/usr/bin/env python3
from pathlib import Path
import sys
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from figure_io import write_generated_bytes
for p in sorted(Path('/tmp/ctr34-figures').glob('ctr34-*.png')):
 write_generated_bytes(P,p.name,p.read_bytes())
 print(p.name)
