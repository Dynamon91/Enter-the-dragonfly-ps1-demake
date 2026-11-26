"""Recover exact EDF-associated Dojo baby dragon variants and shared kite bind meshes."""
from pathlib import Path
import hashlib,json,re,sys
import numpy as np
from dojo25 import records
from recover import shape_metadata,vertex_packets,pxt_groups,nodes,u32
from collect12 import geometry
from spyro_mesh import STRIP,UV
from hash08 import fold
R=Path(__file__).resolve().parents[1];O=R/'assets_m35'
MODELS=[('Tootie','baby_dragon_c.mrb',97,353,'Tootie.scr'),('Huey','baby_dragon_b.mrb',553,117,'Huey.scr'),('Dooie','baby_dragon_a.mrb',1022,105,'Dooie.scr'),('Kite','kite.mrb',419,311,'KITE_SPLINEShape')]
def build(iso):
 O.mkdir(exist_ok=True);r=records(iso);edf=r[734][1];prop_refs=[]
 for spline in ('TOOTIE_DFLYSPLINEShape','KITE_SPLINEShape','BOOK_SPLINEShape'):
  p=edf.lower().index(spline.lower().encode());a=edf.rfind(b'Geometry_File',0,p);assert b'kite.mrb' in edf[a:a+70].lower();prop_refs.append(dict(spline=spline,edf_offset=a,resource='KITE.MRB'))
 groups=list(pxt_groups(r[577][1]));reg={u32(r[296][1],16+i*16):i for i in range(len(groups))};tex=[];report=[];arrays={};header='/* Generated locally from original Dojo models. */\n';pal=[];pix=[]
 def arr(a):return ',\n'.join('{'+','.join(map(str,row))+'}' for row in a.reshape(-1,a.shape[-1]))
 for mi,(name,fn,mid,gid,script) in enumerate(MODELS):
  p=edf.lower().index(script.lower().encode());start=edf.rfind(b'Geometry_File',0,p);assert fn.encode() in edf[start:start+70].lower();assert r[mid][0]==fold(fn.encode());b,g=r[mid][1],r[gid][1];ss=shape_metadata(b);refs={}
  for p,n,q in nodes(b,0x47ba46ed):
   h=f'{u32(b,p+4):08x}';t=u32(b,q+96)
   for pp,nn,qq in nodes(b[q+96:q+800],0xdad78930):
    if u32(b,q+96+pp+4)!=t:continue
    m=re.search(rb'[0-9A-F]{8}\.PXT',b[q+96+qq:q+96+qq+150]);assert m;refs[h]=(reg[fold(m.group().lower())],m.group().decode());break
  if mi<3:
   p,n,q=next(nodes(b,0x8b591ff2));k=u32(b,q+10);bind=np.frombuffer(b,'<f4',16*k,q+14).reshape(k,4,4);ids=np.frombuffer(b,'<u4',k,q+14+64*(k+1));names={u32(b,p+4):n for p,n,q in nodes(b,0x3d4c8da1)};head=-bind[[names[i] for i in ids].index('bdgn_head'),3,:3];assert k==30
  V=[];F=[];U=[];M=[];parts=[]
  for i,s in enumerate(ss):
   n=s['name'];end=ss[i+1]['offset'] if i+1<len(ss) else len(g);v,f=geometry(b,g,s,end)
   if n in ('bbcShape','walk_boxShape'):continue
   uv=[]
   for p,a in vertex_packets(g,s['offset'],end):
    q=g.find(STRIP,p);u=g.find(UV,q);cnt=g[q+9];uv.extend(np.frombuffer(g,'<f4',2*cnt,u+9).reshape(-1,2))
   uv=np.array(uv);assert len(uv)==len(v)
   if mi<3 and s['kind']=='object':v=v+head
   step=5 if 'main' in n else 8 if mi==3 and 'head' in n else 2
   key=np.rint(v/step).astype(int);_,ix=np.unique(key,axis=0,return_inverse=True);vv=np.zeros((ix.max()+1,3));np.add.at(vv,ix,v);vv/=np.bincount(ix)[:,None];vv=np.rint(vv*[1,-1,1]).astype(int);ff=ix[f];valid=np.array([len(set(a))==3 for a in ff]);ff=ff[valid];sf=f[valid];_,keep=np.unique(np.sort(ff,axis=1),axis=0,return_index=True);keep=np.sort(keep);ff=ff[keep];sf=sf[keep];st=uv[sf];st=np.rint((st-np.floor(st.min(axis=1,keepdims=True)))*64).astype(int);assert st.min()>=0 and st.max()<256,(n,st.max());group,filename=refs[s['material']]
   if group not in [t['group'] for t in tex]:
    _,p,imgs=groups[group];w,h,im=imgs[0];assert (w,h)==(64,64) and len(p)==256;p=p.astype(np.uint16);c=np.maximum((p[:,0]>>3)|((p[:,1]>>3)<<5)|((p[:,2]>>3)<<10),1);pal.append(c);pix.append(im);tex.append(dict(group=group,filename=filename))
   slot=[t['group'] for t in tex].index(group);F.extend(ff+len(V));V.extend(vv);U.extend(st);M.extend([slot]*len(ff));parts.append(dict(name=n,source=len(f),optimized=len(ff),texture_group=group))
  v=np.array(V,dtype=np.int16);f=np.array(F,dtype=np.uint16);uv=np.array(U,dtype=np.uint8);m=np.array(M,dtype=np.uint8);assert v.shape[0]<65536;arrays.update({f'v{mi}':v,f'f{mi}':f,f'u{mi}':uv,f'm{mi}':m});header+=f'static const s16 qv35_{mi}[{len(v)}][3]={{'+arr(v)+'};\n';header+=f'static const QuestFace35 qf35_{mi}[{len(f)}]={{'+',\n'.join('{{'+','.join(map(str,a))+'},{'+','.join(map(str,t.ravel()))+'},'+str(c)+'}' for a,t,c in zip(f,uv,m))+'};\n';report.append(dict(name=name,resource=fn,metadata=mid,geometry=gid,metadata_sha256=hashlib.sha256(b).hexdigest(),geometry_sha256=hashlib.sha256(g).hexdigest(),vertices=len(v),triangles=len(f),source_triangles=sum(p['source'] for p in parts),parts=parts,bounds=[v.min(0).tolist(),v.max(0).tolist()]))
 assert len(tex)==11
 header+='static const QuestModel35 qmodels35[]={'+','.join('{qv35_'+str(i)+',qf35_'+str(i)+','+str(x['vertices'])+','+str(x['triangles'])+'}' for i,x in enumerate(report))+'};\n';header+=f'#define Q35_TEX {len(tex)}\nstatic const u16 qpal35[Q35_TEX][256]={{'+arr(np.array(pal))+'};\nstatic const U8 qpix35[Q35_TEX][4096]={{'+arr(np.array(pix).reshape(len(tex),-1))+'};\n';(O/'questmodels35.h').write_text(header);np.savez_compressed(O/'questmodels.npz',**arrays,palettes=pal,pixels=pix);rep=dict(models=report,textures=tex,prop_refs=prop_refs,limitations='NPC bind pose, head-local eye/eyebrow/lash translation, reconstructed player-facing yaw. Shared KITE.MRB for all three props, rest geometry; exact animation and alpha blending pending. Opaque CLUT conversion, vertex clustering.');(O/'report.json').write_text(json.dumps(rep,indent=2));print([(x['name'],x['vertices'],x['triangles'],x['bounds']) for x in report])
if __name__=='__main__':build(Path(sys.argv[1]))
