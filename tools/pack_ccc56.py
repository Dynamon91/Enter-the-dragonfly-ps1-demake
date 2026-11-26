"""Diagnostic bank only: explicitly quarantine integer-collapsed source faces."""
import argparse,json
from pathlib import Path
import numpy as np
from classic_sector51 import pack

def build(geometry,assets,out):
    with np.load(geometry,allow_pickle=False) as x: g={k:x[k] for k in ('vertices','faces','uv','material')}
    with np.load(assets/'collision.npz',allow_pickle=False) as x:c={k:x[k] for k in ('vertices','faces','flags')}
    exclusions={}
    for name,z,side in [('render',g,'material'),('collision',c,'flags')]:
        t=np.rint(z['vertices'][z['faces']].astype(np.float64)).astype(np.int64);keep=np.any(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)
        exclusions[name]={'excluded_source_face_ids':np.flatnonzero(~keep).tolist(),'bank_face_to_source':np.flatnonzero(keep).tolist()};z['faces']=z['faces'][keep];z[side]=z[side][keep]
    bindings=json.loads((assets/'bindings.json').read_text());config=dict(level=2,world_coordinates_reviewed=True,materials=bindings['materials'],objects=bindings['objects'])
    # Coordinates used as-is for inspection only, not a reviewed gameplay release.
    report=pack(g,c,config,out);(out/'face_provenance.json').write_text(json.dumps(exclusions,separators=(',',':')));print(json.dumps(report,indent=2));return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('geometry',type=Path);p.add_argument('assets',type=Path);p.add_argument('out',type=Path);a=p.parse_args();build(a.geometry,a.assets,a.out)
