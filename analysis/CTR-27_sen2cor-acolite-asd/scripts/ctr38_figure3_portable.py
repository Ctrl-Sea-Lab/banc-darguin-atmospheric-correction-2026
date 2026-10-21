"""Compatibility entry point for the current offline report, without old packages."""
from ctr44_delivery import A, portable
import json
if __name__=='__main__':
    result=portable()
    (A/'provenance/ctr44_portable.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
