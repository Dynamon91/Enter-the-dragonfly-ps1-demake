"""Extract original Dojo sky environment, match shape bounds and texture directory.
PS1 conversion: scale world coordinates, quantize UVs, 64x64 8-bit CLUT.
Cloud half blend and sun additive are approximations of PS2 material equations.
"""
import argparse, bisect, json, re, struct, hashlib
from pathlib import Path
import numpy as np
from PIL import Image
from dojo25 import records
from recover import shape_metadata,vertex_packets,pxt_groups,nodes,u32
from spyro_mesh import STRIP,UV
from hash08 import fold
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets_m28'
LAYER=[0x16f39d82,0x12c2e6ac,0xfa955495,0x47f94f8a]
def build(iso,out=OUT):
 out.mkdir(parents=True,exist_ok=True);r=records(iso);b=r[1049][1];g=r[1080][1];pack=[]
 for p,v in vertex_packets(g,0,len(g)):
  f=g.find(STRIP,p,p+1500);u=g.find(UV,p,p+1500);assert f>=0 and u>=0
  t=g[f+9:f+25];n=t[0];lens=[x//3 for x in t[1:] if x];assert 0<n<=len(v) and sum(lens)==n and min(lens)>=3 and all(x%3==0 for x in t[1:]);pack.append((p,v[:n],np.frombuffer(g,'<f4',64,u+9).reshape(-1,2)[:n],lens))
 pos=[p[0] for p in pack];tris=[];meta=[];used=[]
 for s in shape_metadata(b):
  k=bisect.bisect_left(pos,s['offset']);pp=pack[k:k+s['packets']];assert pp[0][0]==s['offset']+22 and len(pp)==s['packets'];used.extend(range(k,k+len(pp)))
  q=s['node_offset']+20+len(s['name']);bounds=np.frombuffer(b,'<f4',6,q).reshape(2,3);v=np.concatenate([p[1] for p in pp]);assert np.max(np.abs(bounds-np.stack([v.min(0),v.max(0)])))<.01
  layer=LAYER.index(int(s['material'],16));start=len(tris)
  for _,v,uv,lens in pp:
   c=0
   for n in lens:
    for j in range(2,n):
     ix=[c+j-2,c+j-1,c+j];ix=ix if j%2==0 else [ix[1],ix[0],ix[2]];a=v[ix];t=uv[ix]
     if np.linalg.norm(np.cross(a[1]-a[0],a[2]-a[0]))<1e-5:continue
     xyz=np.rint(a*np.array([1,-1,1])/64).astype(int);st=np.rint(t*1024).astype(int);tris.append((layer,np.column_stack([xyz,st])))
    c+=n
  meta.append(dict(name=s['name'],layer=layer,packets=len(pp),triangles=len(tris)-start,bounds=bounds.tolist()))
 assert len(meta)==14 and sorted(used)==list(range(len(pack)))
 groups=list(pxt_groups(r[577][1]));table=r[296][1];reg={u32(table,16+i*16):i for i in range(len(groups))};textures=[];palettes=[];pixels=[]
 for layer,h in enumerate(LAYER):
  matches=[]
  for p,n,q in nodes(b,0x47ba46ed):
   if u32(b,p+4)!=h:continue
   t=u32(b,q+96)
   for pp,nn,qq in nodes(b,0xdad78930):
    if u32(b,pp+4)!=t:continue
    m=re.search(rb'[0-9A-F]{8}\.PXT',b[qq:qq+150]);assert m
    fn=m.group().decode();i=reg[fold(fn.lower().encode())];off,pal,imgs=groups[i];w,hh,ix=imgs[0];_,o,size,_=struct.unpack_from('<IIII',table,16+i*16);end=groups[i+1][0] if i+1<len(groups) else len(r[577][1]);sw,sh,_,ss=struct.unpack_from('<HHHI',b,qq+m.end());assert (w,hh,size)==(sw,sh,ss) and o-len(table)==off and size==end-off-16
    matches.append((i,fn,nn,pal,ix,w,hh))
  assert len(matches)==1
  i,fn,nn,pal,ix,w,hh=matches[0];p=pal.astype(np.uint16);c=(p[:,0]>>3)|((p[:,1]>>3)<<5)|((p[:,2]>>3)<<10)
  if layer==0:c=np.maximum(c,1)
  elif layer==3:c=np.maximum(c,1)|0x8000
  else:c=np.where(c,c|0x8000,0)
  c=np.pad(c.astype('<u2'),(0,256-len(c)));ix64=np.asarray(Image.fromarray(ix).resize((64,64),Image.Resampling.NEAREST));palettes.append(c);pixels.append(ix64);Image.fromarray(pal[ix][:,:,:3]).save(out/f'source_{layer}.png');textures.append(dict(layer=layer,group=i,filename=fn,node=nn,width=w,height=hh,alpha_used=sorted(map(int,np.unique(pal[ix][:,:,3])))))
 order=sorted(range(len(tris)),key=lambda i:tris[i][0]);v=np.array([tris[i][1] for i in order],dtype=np.int16);l=np.array([tris[i][0] for i in order],dtype=np.uint8);assert np.max(abs(v.astype(int)))<8192
 np.savez_compressed(out/'sky.npz',triangles=v,layers=l,palettes=np.array(palettes),pixels=np.array(pixels));rep=dict(meshes=meta,triangles=len(v),packets=len(pack),textures=textures,geometry_record=1080,metadata_record=1049,geometry_sha256=hashlib.sha256(g).hexdigest(),metadata_sha256=hashlib.sha256(b).hexdigest(),scale=64,notes='Rotation-only sky pass. Cloud half-blend; sun additive; source animation and PS2 blending not yet exact.')
 (out/'sky_report.json').write_text(json.dumps(rep,indent=2));print(len(v),len(pack),[(t['group'],t['filename']) for t in textures])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('iso');build(p.parse_args().iso)
