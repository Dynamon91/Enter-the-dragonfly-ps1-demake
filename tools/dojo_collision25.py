"""Conservative polygon recovery from the original named hub collision resource.
This is not a complete BSP traversal: candidates are constrained by aligned layout,
world bounds, near-planarity and nondegenerate edges. Preserve source offsets.
"""
import argparse,json,struct,collections
from pathlib import Path
import numpy as np
from dojo25 import records
from recover import nodes
TYPE=0xbf1d6d84

def recover(iso,out):
 r=records(iso);b=r[383][1];matches=list(nodes(b,TYPE));assert len(matches)==1 and matches[0][1]=='ddojo_collShape';p,name,q=matches[0]
 end=len(b);bounds=np.frombuffer(b,'<f4',6,q).reshape(2,3).copy();polys=[];flags=[];offsets=[];verts=[];faces=[];parts=[];p=q+53
 while p+8<=end:
  flag,n=struct.unpack_from('<II',b,p)
  if flag in (0,3) and 3<=n<=32 and p+8+n*12<=end:
   v=np.frombuffer(b,'<f4',n*3,p+8).reshape(-1,3).astype(float)
   if np.isfinite(v).all() and np.all(v>=bounds[0]-10) and np.all(v<=bounds[1]+10) and np.max(np.abs(v))>100 and np.min(np.linalg.norm(np.roll(v,1,0)-v,axis=1))>.01:
    s=np.linalg.svd(v-v.mean(0),compute_uv=False)
    if s[1]>.01 and s[2]<max(.02,s[0]*.015):
     # Reject wildly nonconvex or repeated candidates; fan triangulation is provisional.
     base=len(verts);verts.extend(v);idx=len(polys);polys.append(n);flags.append(flag);offsets.append(p)
     for j in range(1,n-1):
      if np.linalg.norm(np.cross(v[j]-v[0],v[j+1]-v[0]))>.01:faces.append((base,base+j,base+j+1));parts.append(idx)
     p+=8+12*n;continue
  p+=4
 out.mkdir(parents=True,exist_ok=True);np.savez_compressed(out/'collision.npz',vertices=np.array(verts,dtype=np.float32),faces=np.array(faces,dtype=np.int32),polygon_size=np.array(polys),polygon_flags=np.array(flags),polygon_offset=np.array(offsets),part=np.array(parts),bounds=bounds)
 rep=dict(record=383,node=name,source_bytes=len(b),node_data_offset=q,scan_end=end,polygon_candidates=len(polys),triangles=len(faces),flags=dict(collections.Counter(flags)),bounds=bounds.tolist(),limitations='Aligned heuristic scan of polygon records; BSP traversal, polygon flags, completeness, and nonconvex polygons not fully decoded. Fan triangulation; no claim of identical collision.')
 (out/'collision_report.json').write_text(json.dumps(rep,indent=2));print(rep);return rep
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('iso',type=Path);p.add_argument('out',type=Path);a=p.parse_args();recover(a.iso,a.out)
