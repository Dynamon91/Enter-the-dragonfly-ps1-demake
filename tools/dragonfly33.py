"""Recover Dojo dragonfly rest geometry, source palette samples and three wing poses."""
from pathlib import Path
import json,hashlib,re,struct
import numpy as np
from dojo25 import records
from recover import shape_metadata,vertex_packets,pxt_groups,nodes,u32
from spyro_mesh import STRIP,UV,joints
from collect12 import geometry
from hash08 import fold
R=Path(__file__).resolve().parents[1]; O=R/'assets_m33'
def build(iso):
 O.mkdir(exist_ok=True);r=records(iso);b=r[717][1];g=r[328][1];assert all(r[i][1]==g for i in [590,926,1153]);ss=shape_metadata(b);groups=list(pxt_groups(r[577][1]));tab=r[296][1];reg={u32(tab,16+i*16):i for i in range(len(groups))}
 # Match material nodes and first texture reference. Color is sampled from original base palette, not the PS2 shader.
 refs={}
 for p,n,q in nodes(b,0x47ba46ed):
  h=f'{u32(b,p+4):08x}';t=u32(b,q+96)
  for pp,nn,qq in nodes(b[q+96:q+800],0xdad78930):
   if u32(b,q+96+pp+4)!=t:continue
   m=re.search(rb'[0-9A-F]{8}\.PXT',b[q+96+qq:q+96+qq+150])
   if m and fold(m.group().lower()) in reg:refs[h]=reg[fold(m.group().lower())]
   break
 p,n,q=next(nodes(b,0x8b591ff2));k=u32(b,q+10);bind=np.frombuffer(b,'<f4',16*k,q+14).reshape(k,4,4);ids=np.frombuffer(b,'<u4',k,q+14+64*(k+1));names={u32(b,p+4):n for p,n,q in nodes(b,0x3d4c8da1)};pos={names[i]:-v[3,:3] for i,v in zip(ids,bind)};local=joints(b)
 parts={};meta=[]
 for i,s in enumerate(ss):
  n=s['name'];
  if not n.startswith('df_') or 'eyelid' in n:continue
  end=ss[i+1]['offset'] if i+1<len(ss) else len(g);v,f=geometry(b,g,s,end);uv=[]
  for p,a in vertex_packets(g,s['offset'],end):
   q=g.find(STRIP,p);u=g.find(UV,q);cnt=g[q+9];uv.extend(np.frombuffer(g,'<f4',2*cnt,u+9).reshape(-1,2))
  uv=np.array(uv);assert len(uv)==len(v)
  if 'wing' in n:v=v+pos['df_belly']+local['df_wing_'+n[8]]
  elif s['kind']!='cluster':v=v+pos['df_head']
  # Cluster vertices by small grid, preserve source face UV for centroid palette sampling.
  step=4 if 'main' in n else 2;key=np.rint(v/step).astype(int);_,ix=np.unique(key,axis=0,return_inverse=True);vv=np.zeros((ix.max()+1,3));np.add.at(vv,ix,v);vv/=np.bincount(ix)[:,None];ff=ix[f];valid=np.array([len(set(a))==3 for a in ff]);ff=ff[valid];sf=f[valid];_,keep=np.unique(np.sort(ff,axis=1),axis=0,return_index=True);keep=np.sort(keep);ff=ff[keep];sf=sf[keep];tri=np.rint(vv[ff]*[1,-1,1]).astype(int);group=refs[s['material']];_,pal,imgs=groups[group];w,h,ix=imgs[0];u=uv[sf].mean(1)%1;rgb=pal[ix[(u[:,1]*h).astype(int),(u[:,0]*w).astype(int)],:3].astype(int);c=rgb[:,0]|rgb[:,1]<<8|rgb[:,2]<<16;parts[n]=(tri,c);meta.append(dict(name=n,source=len(f),optimized=len(ff),texture_group=group))
 def combine(names):return tuple(np.concatenate([parts[n][i] for n in names]) for i in range(2))
 meshes={'dfbody33':combine([n for n in parts if 'wing' not in n])}
 for i,a in enumerate('abc'):meshes['dfwing'+str(i)+'33']=combine(['df_wing_r'+a+'Shape','df_wing_l'+a+'Shape'])
 h='';arrays={}
 for name,(tri,col) in meshes.items():
  h+=f'static const CollectFace {name}[]={{\n'+',\n'.join('{{'+','.join('{'+','.join(map(str,v))+'}' for v in t)+'},'+str(c)+'u}' for t,c in zip(tri,col))+'};\n';arrays[name]=tri;arrays[name+'_color']=col
 objects=json.loads((R/'assets_m25/sector_manifest.json').read_text())['objects'];d=[o for o in objects if 'dfly' in o['edf'].lower() and 'trigger' not in o['edf'].lower()];assert len(d)==4;d.sort(key=lambda o:o['record_offset']);
 for i,o in enumerate(d):o.update(slot=i,enabled='RDFLY_END' in o['edf'] or 'RED_DFLY2' in o['edf'])
 ids='static const U32 df_ids33[]={'+','.join(str(o['record_offset']) for o in d)+'};\nstatic const U8 df_enabled33[]={'+','.join(str(int(o['enabled'])) for o in d)+'};\n';(O/'dragonflydata33.h').write_text(h);(O/'dragonflyids33.h').write_text(ids);np.savez_compressed(O/'dragonfly.npz',**arrays);rep=dict(metadata=717,geometry=328,geometry_sha256=hashlib.sha256(g).hexdigest(),identical_records=[328,590,926,1153],parts=meta,objects=d,triangles={n:len(t) for n,(t,c) in meshes.items()},limitations='Shared variant geometry; source palette centroid colors from metadata 717 (red-orange), variant assignment unverified. Head bind translation, wing attachment approximated, eyelids omitted. Scripted captures reserved.');(O/'report.json').write_text(json.dumps(rep,indent=2));print(rep)
if __name__=='__main__':import sys;build(Path(sys.argv[1]))
