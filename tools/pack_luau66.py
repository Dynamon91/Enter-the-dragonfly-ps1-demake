"""Exclude separately placed rock wall and preserve quantization provenance."""
import argparse,json
from pathlib import Path
import numpy as np
from classic_sector51 import pack

def select(geometry,report,out):
    with np.load(geometry,allow_pickle=False) as z:
        rows=json.loads(report.read_text())['meshes'];ids=[i for i,m in enumerate(rows) if m['name']=='LI_BWALL_CShape'];assert len(ids)==1
        keep=~np.isin(z['part'],ids);assert int((~keep).sum())==631
        np.savez_compressed(out,vertices=z['vertices'],uv=z['uv'],faces=z['faces'][keep],material=z['material'][keep],part=z['part'][keep])

def build(geometry,assets,out):
    with np.load(geometry,allow_pickle=False) as z:g={k:z[k] for k in ('vertices','faces','uv','material')}
    with np.load(assets/'collision.npz',allow_pickle=False) as z:c={k:z[k] for k in ('vertices','faces','flags')}
    exc={}
    for n,a,side in [('render',g,'material'),('collision',c,'flags')]:
        t=np.rint(a['vertices'][a['faces']]).astype(np.int64);keep=np.any(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1);exc[n]=np.flatnonzero(~keep).tolist();a['faces']=a['faces'][keep];a[side]=a[side][keep]
    b=json.loads((assets/'bindings.json').read_text());report=pack(g,c,dict(level=3,world_coordinates_reviewed=True,**b),out);(out/'exclusions.json').write_text(json.dumps(exc));return report
if __name__=='__main__':
    p=argparse.ArgumentParser();sp=p.add_subparsers(dest='action',required=True);a=sp.add_parser('select');[a.add_argument(k,type=Path) for k in ('geometry','report','out')];a=sp.add_parser('pack');[a.add_argument(k,type=Path) for k in ('geometry','assets','out')];a=p.parse_args()
    if a.action=='select':select(a.geometry,a.report,a.out)
    else:print(build(a.geometry,a.assets,a.out))
