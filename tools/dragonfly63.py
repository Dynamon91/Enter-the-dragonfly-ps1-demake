"""Recover shared CCC dragonfly mesh, variant source palette colors and EDF flags."""
import argparse, json, struct, re, hashlib
from pathlib import Path
import numpy as np
from cnk import entries,u32
from recover import shape_metadata, nodes
from spyro_mesh import joints
from actors59 import get_texture,mesh
from ccc56 import texture_directory
from hash08 import fold

def build(cnk,bindings,out):
 b=cnk.read_bytes();r={i:b[o:o+s] for i,h,o,s,t in entries(b)};reg,groups,_=texture_directory(r[323],r[580]);g=r[353];assert all(r[i]==g for i in (404,590,906,1149));meta=(487,273,710);base=r[meta[0]];ss=shape_metadata(base);p,n,q=next(nodes(base,0x8b591ff2));k=u32(base,q+10);bind=np.frombuffer(base,'<f4',16*k,q+14).reshape(k,4,4);ids=np.frombuffer(base,'<u4',k,q+14+64*(k+1));names={u32(base,p+4):n for p,n,q in nodes(base,0x3d4c8da1)};pos={names[i]:-v[3,:3] for i,v in zip(ids,bind)};local=joints(base)
 parts={};partrep=[];arrays={}
 for i,s in enumerate(ss):
  n=s['name']
  if not n.startswith('df_') or 'eyelid' in n:continue
  v,f,uv=mesh(base,g,s,ss[i+1]['offset'] if i+1<len(ss) else len(g))
  if 'wing' in n:v=v+pos['df_belly']+local['df_wing_'+n[8]]
  elif s['kind']!='cluster':v=v+pos['df_head']
  step=4 if 'main' in n else 2;_,ix=np.unique(np.rint(v/step).astype(int),axis=0,return_inverse=True);vv=np.zeros((ix.max()+1,3));np.add.at(vv,ix,v);vv/=np.bincount(ix)[:,None];ff=ix[f];valid=np.array([len(set(a))==3 for a in ff]);ff=ff[valid];sf=f[valid];_,keep=np.unique(np.sort(ff,axis=1),axis=0,return_index=True);keep=np.sort(keep);ff=ff[keep];sf=sf[keep];tri=np.rint(vv[ff]*[1,-1,1]).astype(int);valid=np.any(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1);tri=tri[valid];sf=sf[valid];colors=[];refs=[]
  for m in meta:
   group,fn=get_texture(r[m],int(s['material'],16),reg,groups);pal,imgs=groups[group];w,h,ix=imgs[0];u=uv[sf].mean(1)%1;rgb=pal[ix[(u[:,1]*h).astype(int),(u[:,0]*w).astype(int)],:3].astype(int);colors.append((rgb[:,0]>>3)|((rgb[:,1]>>3)<<5)|((rgb[:,2]>>3)<<10));refs.append(group)
  parts[n]=(tri,np.array(colors).T);partrep.append(dict(name=n,source=len(f),native=len(tri),groups=refs))
 def combine(names):return tuple(np.concatenate([parts[n][i] for n in names]) for i in range(2))
 meshes={'dfbody63':combine([n for n in parts if 'wing' not in n])}
 for i,a in enumerate('abc'):meshes['dfwing'+str(i)+'63']=combine(['df_wing_r'+a+'Shape','df_wing_l'+a+'Shape'])
 h='typedef struct {short v[3][3];unsigned short col[3];} DfFace63;\n'
 for name,(tri,col) in meshes.items():
  assert abs(tri).max()<8192;h+=f'static const DfFace63 {name}[]={{\n'+',\n'.join('{{'+','.join('{'+','.join(map(str,v))+'}' for v in t)+'},{'+','.join(map(str,c))+'}}' for t,c in zip(tri,col))+'};\n';arrays[name]=tri;arrays[name+'_color']=col
 tab=r[1125]; rows={h:(o-len(tab),n) for h,o,n,f in (struct.unpack_from('<4I',tab,16+16*i) for i in range(104))};placements=[]
 for o in json.loads(bindings.read_text())['objects']:
  if 'DFLY' not in o['edf'].upper():continue
  off,size=rows[fold(o['edf'].lower().encode())];edf=r[719][off:off+size];caught=int(re.search(rb'CaughtFlag:\s*2\s+(\d+)',edf)[1]);found=int(re.search(rb'FoundFlag:\s*2\s+(\d+)',edf)[1]);gate=re.search(rb'OnFlag:\s*2\s+(\d+)',edf);geo=re.search(rb'Geometry_File:\s*"(\w+)\.mrb"',edf,re.I)[1].decode().lower();variant=['green','yellow','red'].index(geo.split('_')[0]);xyz=np.rint(np.array(o['source_xyz'])*[1,-1,1]).astype(int).tolist();placements.append(dict(source_id=o['source_id'],edf=o['edf'],xyz=xyz,caught=caught,found=found,gate=int(gate[1]) if gate else 0,variant=variant,edf_sha256=hashlib.sha256(edf).hexdigest()))
 placements.sort(key=lambda p:p['caught']);assert [p['caught'] for p in placements]==[200,201,203,205];h+='typedef struct {int x,y,z;unsigned short caught,found,gate,variant;} DfPlacement63;\nstatic const DfPlacement63 dfplace63[]={'+','.join('{'+','.join(map(str,p['xyz']+[p['caught'],p['found'],p['gate'],p['variant']]))+'}' for p in placements)+'};\n'
 out.mkdir(exist_ok=False,parents=True);(out/'dfdata63.h').write_text(h);np.savez_compressed(out/'df63.npz',**arrays);rep=dict(source_sha256=hashlib.sha256(b).hexdigest(),geometry_record=353,metadata_records=meta,parts=partrep,placements=placements,triangles={n:len(t) for n,(t,c) in meshes.items()},notes='Source mesh and sampled palette colors; variant identified by body texture RGB and EDF name; bind translation approximated, eyelids omitted.');(out/'dragonfly63.json').write_text(json.dumps(rep,indent=2)+'\n');print(rep['triangles'],placements)
if __name__=='__main__':
 p=argparse.ArgumentParser();[p.add_argument(n,type=Path) for n in ('cnk','bindings','out')];a=p.parse_args();build(a.cnk,a.bindings,a.out)
