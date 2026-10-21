#!/usr/bin/env python3
"""Repeat bounded source computations and require byte-identical scientific artifacts.
Timestamped provenance receipts are intentionally excluded from the comparison.
The frozen decision contract is an input and is never regenerated.
"""
import json
import ctr34_support as m
import ctr34_extract as e
import ctr34_validate as v
P=m.P
paths=sorted(list((P/'tables').glob('ctr34_*.csv'))+list((P/'outputs').glob('ctr34_*.json')))
before={str(p.relative_to(P)):m.sha(p) for p in paths}
m.inspect();e.main();v.main()
after={str(p.relative_to(P)):m.sha(p) for p in paths}
assert before==after,{k:(before[k],after[k]) for k in before if before[k]!=after[k]}
m.dump('provenance/ctr34_reproduction.json',{'completed_utc':m.now(),'status':'pass','scientific_artifact_count':len(paths),'before_after_sha256':before,'timestamp_provenance_excluded':True,'frozen_contract_regenerated':False,'raw_source_reads':'repeat of same bounded windows only','meaning':'deterministic replay; not independent scientific review'})
print('Byte-identical replay:',len(paths),'scientific artifacts')
