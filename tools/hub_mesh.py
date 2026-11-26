"""Match named world meshes to source GEOM packets using exact per-mesh bounds.
Only export matches that pass all strip/UV/bounds checks. World coordinates retained."""
import argparse,json,bisect,collections
from pathlib import Path
import numpy as np
from recover import records,shape_metadata,vertex_packets,SIG
from spyro_mesh import STRIP,UV

def recover_hub(iso,out):
 r=records(iso);b=r[502][1]; shapes=[s for s in shape_metadata(b) if 'HUB_' in s['name'].upper()]; candidates={};
 for i,(h,g) in r.items():
  if g[23:30]!=SIG:continue
  pp=[]
  for p,v in vertex_packets(g,0,len(g)):
   end=min(len(g),p+1500);f=g.find(STRIP,p,end);u=g.find(UV,p,end)
   if f<0 or u<0:continue
   t=g[f+9:f+25];n=t[0];lens=[x//3 for x in t[1:] if x]
   if not(0<n<=len(v) and sum(lens)==n and min(lens,default=0)>=3 and all(x%3==0 for x in t[1:])):continue
   uv=np.frombuffer(g,'<f4',64,u+9).reshape(-1,2)[:n].copy()
   if not np.isfinite(uv).all():continue
   pp.append((p,v[:n],uv,lens))
  if pp:candidates[i]=([p[0] for p in pp],pp)
 v=[];f=[];uv=[];mat=[];parts=[];meta=[];unmatched=[]
 for s in shapes:
  q=s['node_offset']+20+len(s['name']);bounds=np.frombuffer(b,'<f4',6,q).reshape(2,3);matches=[]
  for i,(pos,pp) in candidates.items():
   k=bisect.bisect_left(pos,s['offset']);p=pp[k:k+s['packets']]
   if len(p)!=s['packets'] or p[0][0]!=s['offset']+22:continue
   a=np.concatenate([x[1] for x in p]);err=float(np.max(np.abs(bounds-np.stack([a.min(0),a.max(0)]))))
   if err<.01:matches.append((i,p,err))
  if len(matches)!=1:unmatched.append(dict(name=s['name'],matches=[x[0] for x in matches]));continue
  i,p,err=matches[0];base=len(v);nf=len(f)
  for _,a,u,lens in p:
   start=len(v);v.extend(a);uv.extend(u);cursor=0
   for length in lens:
    for j in range(2,length):
     ix=[cursor+j-2,cursor+j-1,cursor+j];ix=ix if j%2==0 else [ix[1],ix[0],ix[2]]
     if np.linalg.norm(np.cross(a[ix[1]]-a[ix[0]],a[ix[2]]-a[ix[0]]))<1e-5:continue
     f.append([start+x for x in ix]);mat.append(int(s['material'],16));parts.append(len(meta))
    cursor+=length
  meta.append(dict(name=s['name'],record=i,material=s['material'],offset=s['offset'],packets=s['packets'],bounds_error=err,vertices=len(v)-base,triangles=len(f)-nf,bounds=bounds.tolist()))
 out.mkdir(parents=True,exist_ok=True);v=np.array(v,dtype=np.float32);f=np.array(f,dtype=np.int32);np.savez_compressed(out/'hub.npz',vertices=v,faces=f,uv=np.array(uv),material=np.array(mat,dtype=np.uint32),part=np.array(parts))
 rep=dict(matched=len(meta),unmatched=unmatched,source_shapes=len(shapes),vertices=len(v),triangles=len(f),meshes=meta,limitations='Named render geometry, not collision mesh; texture material hashes unresolved; omitted unmatched or ambiguous shapes.')
 (out/'hub_report.json').write_text(json.dumps(rep,indent=2));print({k:v for k,v in rep.items() if k not in ('meshes','unmatched')});print(collections.Counter(x['record'] for x in meta));return rep
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('iso',type=Path);p.add_argument('out',type=Path);a=p.parse_args();recover_hub(a.iso,a.out)
