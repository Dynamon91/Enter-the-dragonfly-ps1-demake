"""Recover baby-dragon skeletal animation samples using validated original curves and v35 vertex clustering."""
from pathlib import Path
import struct,json,sys,hashlib
import numpy as np
from dojo25 import records
from recover import nodes,u32,shape_metadata,vertex_packets
from spyro_mesh import joints,STRIP
from collect12 import geometry
from animation09 import decode
R=Path(__file__).resolve().parents[1]; A=R/'assets_m36'
MODELS=[(97,353,'c'),(553,117,'b'),(1022,105,'a')]
PARENTS=[-1,0,1,2,3,4,5,4,2,8,9,2,11,12,2,14,15,2,17,18,1,20,21,22,0,24,25,0,27,28]
def curves(b,r):
 out={}; meta=[]
 for p,n,q in nodes(b,0x07d16200):
  N=struct.unpack_from('<H',b,q)[0];ci=struct.unpack_from(f'<{N}I',b,q+4);ix=struct.unpack_from(f'<{N}I',b,q+4+N*4);s=q+4+8*N+16;cs=[]
  for pp,nn,qq in nodes(b[s:s+N*120+50],0x2d5e8c2f):
   if len(cs)==N:break
   a,z,l,t,o=struct.unpack_from('<ffHHI',b,s+qq-8);cs.append(dict(name=nn,id=u32(b,s+pp+4),start=a,end=z,keys=l,type=t,offset=o))
  cs.sort(key=lambda c:c['offset']);assert len(cs)==N and set(ci)=={c['id'] for c in cs} and [c['offset'] for c in cs]==list(np.cumsum([0]+[c['keys']*16 for c in cs[:-1]]));m=dict(curves=cs,bytes=sum(c['keys']*16 for c in cs));hits=[(i,decode(d,m)) for i,(h,d) in r.items() if len(d)==m['bytes']];hits=[h for h in hits if h[1] is not None];assert len(hits)==1,(n,len(hits));i,a=hits[0];cur={c['id']:v for c,v in zip(cs,a)};out[n]={j:cur[h] for j,h in zip(ix,ci)};meta.append(dict(name=n,record=i,sha256=hashlib.sha256(r[i][1]).hexdigest(),keys=sum(c['keys'] for c in cs),duration=max(c['end'] for c in cs),curves=N))
 return out,meta

def rot(x,y,z):
 sx,cx=np.sin(x),np.cos(x);sy,cy=np.sin(y),np.cos(y);sz,cz=np.sin(z),np.cos(z);return np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])@np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])@np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
def build(iso):
 A.mkdir(exist_ok=True);r=records(iso);old=np.load(R/'assets_m35/questmodels.npz');rep=[];arrs={};header='/* Locally generated original idle and talk pose deltas. */\n#define Q36_IDLE 6\n#define Q36_TALK 6\n';
 for mi,(mid,gid,suffix) in enumerate(MODELS):
  b=r[mid][1];g=r[gid][1];local=joints(b);p,n,q=next(nodes(b,0x8b591ff2));k=u32(b,q+10);bind=np.frombuffer(b,'<f4',16*k,q+14).reshape(k,4,4);ids=np.frombuffer(b,'<u4',k,q+14+64*(k+1));namesby={u32(b,p+4):n for p,n,q in nodes(b,0x3d4c8da1)};names=[namesby[i] for i in ids];pos=-bind[:,3,:3];assert k==30 and np.allclose(bind[:,:3,:3],np.eye(3));assert all(np.linalg.norm(pos[j]-pos[PARENTS[j]]-local[names[j]])<.001 for j in range(1,k));p,n,q=next(nodes(b,0x7f9c7b5a));nc,nn=struct.unpack_from('<II',b,q);start=q+8+4*nc+18;targets=np.frombuffer(b,'<u4',nn,start);attrs=np.frombuffer(b,'<u4',nn,start+4*nn);assert set(ids)<=set(targets) and set(attrs)<={15,16,17,19,20,21,23,24,25,37};clips,meta=curves(b,r);V=[];W=[];ss=shape_metadata(b)
  for i,s in enumerate(ss):
   n=s['name'];end=ss[i+1]['offset'] if i+1<len(ss) else len(g);v,f=geometry(b,g,s,end)
   if n in ('bbcShape','walk_boxShape'):continue
   weights=np.zeros((len(v),k));cursor=0
   if s['kind']=='cluster':
    for p,a in vertex_packets(g,s['offset'],end):
     q=g.find(STRIP,p);cnt=g[q+9];wi=np.frombuffer(g,'<f4',128,q-519).reshape(32,4)[:cnt];ix=np.frombuffer(g,'<u4',128,q-1031).reshape(32,4)[:cnt];assert np.all(ix%4==0) and np.all(ix[wi>0]>=4) and ix.max()//4<=k and np.max(abs(wi.sum(1)-1))<.001;np.add.at(weights,(np.repeat(np.arange(cursor,cursor+cnt),4),np.maximum(ix.astype(int)//4-1,0).ravel()),wi.ravel());cursor+=cnt
    assert cursor==len(v)
   else:v=v+pos[names.index('bdgn_head')];weights[:,names.index('bdgn_head')]=1
   step=5 if 'main' in n else 2;key=np.rint(v/step).astype(int);_,ix=np.unique(key,axis=0,return_inverse=True);vv=np.zeros((ix.max()+1,3));ww=np.zeros((len(vv),k));np.add.at(vv,ix,v);np.add.at(ww,ix,weights);vv/=np.bincount(ix)[:,None];ww/=np.bincount(ix)[:,None];V.extend(vv);W.extend(ww)
  V=np.array(V);W=np.array(W);assert np.max(abs(W.sum(1)-1))<.001;base=old[f'v{mi}'];assert np.array_equal(np.rint(V*[1,-1,1]).astype(np.int16),base);frames=[];ranges=[]
  for kind in ['idle','talk']:
   name='bdgn_'+kind+'_'+suffix;clip=clips[name];dur=max(float(c[0,-1]) for c in clip.values());start=len(frames)
   for t in np.arange(6)*dur/6:
    tr=np.array([local[n] for n in names]);rr=np.zeros((k,3));sc=np.ones((k,3))
    for ch,c in clip.items():
     if targets[ch] not in ids:continue
     j=list(ids).index(targets[ch]);at=attrs[ch];v=np.interp(t,c[0],c[1]);
     if 19<=at<=21:rr[j,at-19]=v
     elif 15<=at<=17:tr[j,at-15]=v
     elif 23<=at<=25:sc[j,at-23]=v
    tr[0]=local[names[0]];worldR=[];worldT=[];vout=np.zeros_like(V)
    for j in range(k):
     a=rot(*rr[j])@np.diag(sc[j]);p=PARENTS[j];o=tr[j];
     if p>=0:o=worldR[p]@o+worldT[p];a=worldR[p]@a
     worldR.append(a);worldT.append(o);vout+=((V-pos[j])@a.T+o)*W[:,j,None]
    frames.append(np.rint(vout*[1,-1,1]).astype(int))
   ranges.append(dict(name=name,start=start,frames=6,duration=dur,ticks=max(1,round(dur*30))))
  frames=np.array(frames);delta=frames-base;print(mi,'delta',delta.min(),delta.max(),'bounds',frames.min(),frames.max());assert np.max(abs(frames))<512;assert np.max(abs(delta))<=127;arrs[f'frames{mi}']=frames.astype(np.int16);arrs[f'delta{mi}']=delta.astype(np.int8);header+=f'static const signed char qdelta36_{mi}[12][{len(base)}][3]={{'+','.join('{'+','.join('{'+','.join(map(str,v))+'}' for v in frame)+'}' for frame in delta)+'};\n';rep.append(dict(model=mi,metadata=mid,joints=k,vertices=len(base),clips=meta,ranges=ranges,max_delta=int(np.max(abs(delta)))))
 header+='static const signed char * const qdelta36[]={'+','.join(f'&qdelta36_{i}[0][0][0]' for i in range(3))+'};\n';header+='static const int qperiod36[3][2]={'+','.join('{'+','.join(str(x['ticks']) for x in m['ranges'])+'}' for m in rep)+'};\n';(A/'questanim36.h').write_text(header);np.savez_compressed(A/'poses.npz',**arrs);(A/'report.json').write_text(json.dumps(dict(models=rep,limitations='Source curves, provisional Euler and linear interpolation, root translation suppressed, facial objects rigid to head; kite animations not integrated.'),indent=2));print('clips',sum(len(x['clips']) for x in rep),'keyframes',sum(c['keys'] for x in rep for c in x['clips']))
if __name__=='__main__':build(Path(sys.argv[1]))
