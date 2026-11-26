"""Recover original Ninja Riptoc mesh, UVs, bone weights and animation curves."""
from pathlib import Path
import struct,json,hashlib,collections,re,sys
import numpy as np
from PIL import Image
from dojo25 import records
from recover import shape_metadata,vertex_packets,pxt_groups,nodes,u32
from spyro_mesh import STRIP,UV,joints
from collect12 import geometry
from animation09 import decode
from hash08 import fold
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets_m30'
def build(iso):
 r=records(iso);b=r[567][1];g=r[1061][1];sh=shape_metadata(b);local=joints(b)
 p,n,q=next(nodes(b,0x8b591ff2));k=u32(b,q+10);bind=np.frombuffer(b,'<f4',16*k,q+14).reshape(k,4,4);ids=np.frombuffer(b,'<u4',k,q+14+64*(k+1));namesby={u32(b,p+4):n for p,n,q in nodes(b,0x3d4c8da1)};names=[namesby[i] for i in ids];pos=-bind[:,3,:3];assert k==27 and np.allclose(bind[:,:3,:3],np.eye(3));parent=[-1]
 for i,n in enumerate(names[1:],1):
  d=np.linalg.norm(pos-(pos[i]-local[n]),axis=1);d[i]=1e9;j=int(d.argmin());assert j<i and d[j]<.001;parent.append(j)
 p,n,q=next(nodes(b,0x7f9c7b5a));nc,nn=struct.unpack_from('<II',b,q);assert (nc,nn)==(10,102);start=q+8+4*nc+30;targets=np.frombuffer(b,'<u4',nn,start);attrs=np.frombuffer(b,'<u4',nn,start+4*nn);assert set(ids)<=set(targets) and all(x in (15,16,17,19,20,21,24,25,37) for x in attrs)
 clips={};arrays={};meta=[]
 for p,n,q in nodes(b,0x07d16200):
  N=struct.unpack_from('<H',b,q)[0];ci=struct.unpack_from(f'<{N}I',b,q+4);ix=struct.unpack_from(f'<{N}I',b,q+4+N*4);s=q+4+8*N+16;cs=[]
  for pp,nn,qq in nodes(b[s:s+N*120+50],0x2d5e8c2f):
   if len(cs)==N:break
   a,z,l,t,o=struct.unpack_from('<ffHHI',b,s+qq-8);cs.append(dict(name=nn,id=u32(b,s+pp+4),start=a,end=z,keys=l,type=t,offset=o))
  cs.sort(key=lambda c:c['offset']);assert len(cs)==N and set(ci)=={c['id'] for c in cs} and [c['offset'] for c in cs]==list(np.cumsum([0]+[c['keys']*16 for c in cs[:-1]]));m=dict(curves=cs,bytes=sum(c['keys']*16 for c in cs));hits=[(i,decode(d,m)) for i,(h,d) in r.items() if len(d)==m['bytes']];hits=[h for h in hits if h[1] is not None];assert len(hits)==1;i,a=hits[0];cur={c['id']:v for c,v in zip(cs,a)};clips[n]={j:cur[h] for j,h in zip(ix,ci)};arrays[n]=np.concatenate(a,axis=1);arrays[n+'_offsets']=np.cumsum([0]+[v.shape[1] for v in a]);meta.append(dict(name=n,record=i,keys=sum(v.shape[1] for v in a),duration=max(c['end'] for c in cs),indices=ix,ids=ci,curves=cs))
 np.savez_compressed(OUT/'curves.npz',**arrays)
 # Body and eyes. Eye geometry is local to the head, whose translation is recovered from the bind matrix.
 V=[];W=[];F=[];UVs=[];M=[];parts=[];allsh={}
 for s in sh[3:]:
  end=sh[sh.index(s)+1]['offset'] if sh.index(s)+1<len(sh) else len(g);v,f=geometry(b,g,s,end);uv=[];weights=np.zeros((len(v),k));cursor=0
  for p,a in vertex_packets(g,s['offset'],end):
   q=g.find(STRIP,p);u=g.find(UV,q);n=g[q+9];uv.extend(np.frombuffer(g,'<f4',2*n,u+9).reshape(-1,2));
   if s['kind']=='cluster':
    wi=np.frombuffer(g,'<f4',128,q-519).reshape(32,4)[:n];ix=np.frombuffer(g,'<u4',128,q-1031).reshape(32,4)[:n];assert np.all(ix%4==0) and np.all(ix[wi>0]>=4) and ix.max()//4<=k and np.max(abs(wi.sum(1)-1))<.001;np.add.at(weights,(np.repeat(np.arange(cursor,cursor+n),4),np.maximum(ix.astype(int)//4-1,0).ravel()),wi.ravel())
   cursor+=n
  if s['kind']!='cluster':v=v+pos[names.index('nr_head')];weights[:,names.index('nr_head')]=1
  uv=np.array(uv);allsh[s['name']]=dict(vertices=len(v),triangles=len(f),bounds=v.min(0).tolist()+v.max(0).tolist())
  if 'eyelid' in s['name']:continue
  step=23 if s['kind']=='cluster' else 4
  # Position-only clustering, preserving each source triangle's UVs separately.
  key=np.rint(v/step).astype(int);_,ix=np.unique(key,axis=0,return_inverse=True);vv=np.zeros((ix.max()+1,3));ww=np.zeros((len(vv),k));np.add.at(vv,ix,v);np.add.at(ww,ix,weights);vv/=np.bincount(ix)[:,None];ww/=np.bincount(ix)[:,None];ff=ix[f];valid=np.array([len(set(x))==3 for x in ff]);ff=ff[valid];sf=f[valid];_,keep=np.unique(np.sort(ff,axis=1),axis=0,return_index=True);keep=np.sort(keep);ff=ff[keep];sf=sf[keep];st=uv[sf];# normalize per triangle into repeated 64px texture domain
  st=np.rint((st-np.floor(st.min(axis=1,keepdims=True)))*64).astype(int);assert st.min()>=0 and st.max()<256
  F.extend(ff+len(V));UVs.extend(st);V.extend(vv);W.extend(ww);M.extend([int('eyeball' in s['name'])]*len(ff));parts.append(dict(name=s['name'],source=len(f),optimized=len(ff)))
 V=np.array(V);W=np.array(W);F=np.array(F);UVs=np.array(UVs);M=np.array(M);assert np.max(abs(W.sum(1)-1))<.001
 def rot(x,y,z):
  sx,cx=np.sin(x),np.cos(x);sy,cy=np.sin(y),np.cos(y);sz,cz=np.sin(z),np.cos(z);return np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])@np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])@np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
 frames=[np.rint(V*[1,-1,1]).astype(int)];ranges=[]
 for name,nframes in [('nr_idle',12),('nr_loop_ready',6)]:
  curves=clips[name];dur=max(float(c[0,-1]) for c in curves.values());start=len(frames)
  for t in np.arange(nframes)*dur/nframes:
   tr=np.array([local[n] for n in names]);rr=np.zeros((k,3));
   for ch,c in curves.items():
    if targets[ch] not in ids:continue
    j=list(ids).index(targets[ch]);at=attrs[ch];v=np.interp(t,c[0],c[1]);
    if 19<=at<=21:rr[j,at-19]=v
    elif 15<=at<=17:tr[j,at-15]=v
   tr[0]=local[names[0]];worldR=[];worldT=[];vout=np.zeros_like(V)
   for j in range(k):
    a=rot(*rr[j]);p=parent[j];o=tr[j];
    if p>=0:o=worldR[p]@o+worldT[p];a=worldR[p]@a
    worldR.append(a);worldT.append(o);vout+=((V-pos[j])@a.T+o)*W[:,j,None]
   frames.append(np.rint(vout*[1,-1,1]).astype(int))
  ranges.append(dict(name=name,start=start,frames=nframes,duration=dur))
 frames=np.array(frames);assert np.max(abs(frames))<512
 groups=list(pxt_groups(r[577][1]));table=r[296][1];reg={u32(table,16+i*16):i for i in range(len(groups))};pal=[];pix=[];texmeta=[]
 for fn in ['38E2DE97.PXT','686C40AE.PXT']:
  i=reg[fold(fn.lower().encode())];off,p,im=groups[i];w,h,ix=im[0];_,o,size,_=struct.unpack_from('<IIII',table,16+i*16);assert o-len(table)==off and size==groups[i+1][0]-off-16 and (w,h)==(64,64);p=p.astype(np.uint16);c=np.maximum((p[:,0]>>3)|((p[:,1]>>3)<<5)|((p[:,2]>>3)<<10),1);pal.append(c);pix.append(ix);texmeta.append(dict(name=fn,group=i));Image.fromarray(p[ix][:,:,:3].astype(np.uint8)).save(OUT/f'texture_{len(pal)-1}.png')
 np.savez_compressed(OUT/'ninja.npz',frames=frames,faces=F,uv=UVs,materials=M,palettes=pal,pixels=pix,weights=W,parents=parent,bind=pos)
 def arr(a):return ',\n'.join('{'+','.join(map(str,row))+'}' for row in a.reshape(-1,a.shape[-1]))
 delta=frames[1:]-frames[0];esc=(delta<-127)|(delta>127);small=np.where(esc,-128,delta);large=delta[esc];offsets=np.cumsum([0]+list(esc.sum((1,2))));rebuilt=small.copy();rebuilt[esc]=large;assert np.array_equal(rebuilt+frames[0],frames[1:])
 h=f'#define NINJA_NV30 {len(V)}\n#define NINJA_NF30 {len(F)}\nstatic const s16 ninja_base30[NINJA_NV30][3]={{'+arr(frames[0])+'};\n';h+=f'static const signed char ninja_delta30[{len(delta)}][NINJA_NV30][3]={{'+','.join('{'+arr(f)+'}' for f in small)+'};\n';h+='static const s16 ninja_escape30[]={'+','.join(map(str,large))+'};\nstatic const u16 ninja_offsets30[]={'+','.join(map(str,offsets))+'};\n';h+='static const u16 ninja_faces30[NINJA_NF30][3]={'+arr(F)+'};\nstatic const U8 ninja_uv30[NINJA_NF30][6]={'+arr(UVs.reshape(-1,6))+'};\nstatic const U8 ninja_mat30[NINJA_NF30]={'+','.join(map(str,M))+'};\n';h+='static const u16 ninja_pal30[2][256]={'+arr(np.array(pal))+'};\nstatic const U8 ninja_pix30[2][4096]={'+arr(np.array(pix).reshape(2,-1))+'};\n';(OUT/'ninja30.h').write_text(h)
 rep=dict(joints=k,clips=meta,frames=ranges,vertices=len(V),triangles=len(F),parts=parts,all_shapes=allsh,textures=texmeta,limitations='Original body and eye meshes; eyelids decoded but omitted pending facial animation. Provisional Euler XYZ, linear curve interpolation, root translation suppressed. Body and eyes use opaque 8-bit CLUT, no specular highlight layer. Animation clips sampled at low rates; original AI not reproduced.')
 (OUT/'report.json').write_text(json.dumps(rep,indent=2));print('joints',k,'clips',len(meta),'keys',sum(c['keys'] for c in meta),'parts',parts,'vertices',len(V),'frames',len(frames),'ranges',ranges)
if __name__=='__main__':build(sys.argv[1])
