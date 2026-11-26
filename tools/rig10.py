"""Source rig, channel table and skin weights; bake fixed-point bone palettes at 30 Hz.
Euler XYZ and linear interpolation are provisional. No facial morph playback."""
import argparse,json,struct,math,hashlib
from pathlib import Path
import numpy as np
from recover import records,nodes,shape_metadata,vertex_packets,u32
from spyro_mesh import joints,decode,STRIP
from preview_m09 import array,signed
ROOT=Path(__file__).resolve().parents[1]
CLIPS=['idle','walk','run','charge','jump_start','jump_cycle','jump_land','glide_cycle','fire_breath']
def rig(iso,out):
 r=records(iso);b=r[1130][1];g=r[1529][1];a=r[502][1];namesby={u32(b,p+4):n for p,n,q in nodes(b,0x3d4c8da1)};local=joints(b);clusters={}
 for p,n,q in nodes(b,0x8b591ff2):
  k=u32(b,q+10);s=q+14;mat=np.frombuffer(b,'<f4',16*k,s).reshape(k,4,4).copy();ids=np.frombuffer(b,'<u4',k,s+64*(k+1));assert all(t in namesby for t in ids);assert np.allclose(mat[:,:3,:3],np.eye(3)) and np.allclose(mat[:,:,3],np.tile([0,0,0,1],(k,1)));clusters[n]=(list(map(int,ids)),mat)
 ids,bind=clusters['skinCluster1'];names=[namesby[t] for t in ids];pos=-bind[:,3,:3];parent=[-1];err=[]
 for i,n in enumerate(names[1:],1):
  ds=np.linalg.norm(pos-(pos[i]-local[n]),axis=1);ds[i]=1e9;p=int(ds.argmin());assert p<i and ds[p]<.001;parent.append(p);err.append(float(ds[p]))
 # Locate the channel arrays by the first known joint triple; cross-check all 167 entries against a second metadata copy.
 def channel_table(data):
  p,n,q=next(x for x in nodes(data,0x7f9c7b5a) if x[1]=='spyro_character');nc,nn=struct.unpack_from('<II',data,q);assert (nc,nn)==(106,167)
  start=data.find(struct.pack('<III',*([ids[-1]]*3)),q+8+4*nc,q+2000);assert start>=0
  t=np.frombuffer(data,'<u4',nn,start).copy();at=np.frombuffer(data,'<u4',nn,start+4*nn).copy();assert set(t[:129])==set(ids);assert np.array_equal(at[:129],np.tile([21,20,19],43));assert list(at[129:132])==[17,16,15] and all(x==ids[0] for x in t[129:132]);return t,at,start
 targets,attrs,channeloff=channel_table(a);dup=False
 try:
  dt,da,_=channel_table(r[1641][1]);dup=bool(np.array_equal(dt,targets) and np.array_equal(da,attrs));assert dup
 except StopIteration:pass
 # Read the 4-index/4-weight VIF arrays in every valid skinned packet.
 shapes=shape_metadata(b);mesh=decode(b,g);allw=[];counts={};visible=[s for s in mesh if s['name'] not in ('bbcShape','r_eyelidShape','l_eyelidShape')];maxerr=0
 for s,m in zip(shapes,mesh):
  n=s['name'];weights=np.zeros((len(m['vertices']),43),dtype=float)
  if s['kind']=='cluster':
   cids,cmat=clusters['skinCluster2' if n=='wing_objShape' else 'skinCluster1'];mapping=np.array([ids.index(x) for x in cids]);assert np.allclose(cmat,bind[mapping],atol=.001)
   pps=list(vertex_packets(g,s['offset'],shapes[shapes.index(s)+1]['offset']));cur=0
   for p,v in pps:
    f=g.find(STRIP,p);cnt=g[f+9];assert len(v)==32;wi=np.frombuffer(g,'<f4',128,f-519).reshape(32,4)[:cnt];ix=np.frombuffer(g,'<u4',128,f-1031).reshape(32,4)[:cnt];assert np.all(ix%4==0) and ix.max()//4<=len(mapping) and np.all(ix[wi>0]>=4);assert np.isfinite(wi).all() and wi.min()>=0 and np.max(abs(wi.sum(1)-1))<.001
    maxerr=max(maxerr,float(np.max(abs(wi.sum(1)-1))));np.add.at(weights,(np.repeat(np.arange(cur,cur+cnt),4),mapping[np.maximum(ix.astype(int)//4-1,0)].ravel()),wi.ravel());cur+=cnt
   assert cur==len(weights);counts[n]=cur
  else:
   if n=='tail_tipShape':joint='tail5'
   elif 'fingersShape' in n:joint=n.replace('fingersShape','toe')
   elif n=='bbcShape':joint='root'
   else:joint='head'
   weights[:,names.index(joint)]=1
  if n not in ('bbcShape','r_eyelidShape','l_eyelidShape'):allw.append(weights)
 z=np.load(ROOT/'build_m04/spyro/spyro_rest.npz');orig=z['vertices'].astype(float);center=(orig.min(0)+orig.max(0))/2;scale=250/np.max(np.ptp(orig,axis=0));flip=np.diag([1,-1,1]);v=np.rint((orig-center)@flip*scale).astype(int)
 part=z['part'];pn=z['part_names'];steps=np.array([10 if n=='body_objShape' else 7 if n in ('wing_objShape','finShape','tail_tipShape') else 5 if 'face' in n or 'horn' in n else 4 for n in pn]);step=steps[part];body=part==list(pn).index('body_objShape');step=np.where(body&((v[:,2]<-35)|(v[:,1]>48)),4,step);key=np.column_stack([part,step,np.rint(v/step[:,None]).astype(int)]);_,ix=np.unique(key,axis=0,return_inverse=True);vv=np.zeros((ix.max()+1,3));np.add.at(vv,ix,v);vv=np.rint(vv/np.bincount(ix)[:,None]).astype(int)
 h=(out/'scene.h').read_text();pv=array(h,'vertices').reshape(-1,2);av=np.column_stack([signed(pv[:,0]&65535),signed(pv[:,0]>>16),signed(pv[:,1]&65535)]);np.testing.assert_array_equal(vv,av)
 w=np.zeros((len(vv),43));np.add.at(w,ix,np.concatenate(allw));w/=w.sum(1)[:,None];idx=np.argsort(-w,axis=1,kind='stable')[:,:4];weights=np.take_along_axis(w,idx,1);discard=1-weights.sum(1);weights/=weights.sum(1)[:,None];qw=np.floor(weights*256).astype(int);rem=256-qw.sum(1);frac=weights*256-qw
 for i in range(len(qw)):qw[i,np.argsort(-frac[i],kind='stable')[:rem[i]]]+=1
 assert (qw.sum(1)==256).all()
 anim=json.loads((ROOT/'build_m09/animation/animation.json').read_text());ac={c['name']:c for c in anim['clips']};az=np.load(ROOT/'build_m09/animation/curves.npz');frames=[];clips=[]
 def rotation(x,y,z):
  sx,cx=np.sin(x),np.cos(x);sy,cy=np.sin(y),np.cos(y);sz,cz=np.sin(z),np.cos(z);return np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])@np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])@np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
 for name in CLIPS:
  n='spyro_'+name;c=ac[n];m=c['metadata'];a=az[n];o=az[n+'_offsets'];mapping={h:k for k,h in enumerate(x['id'] for x in m['curves'])};length=max(1,round(c['curve_end']*30));t=np.arange(length)/30;val=np.zeros((len(t),167))
  for ch,h in zip(m['indices'],m['ids']):
   k=mapping[h];val[:,ch]=np.interp(t,a[0,o[k]:o[k+1]],a[1,o[k]:o[k+1]])
  start=len(frames)
  for vs in val:
   rot=np.zeros((43,3));tr=np.array([local[n] for n in names]);
   for ch in range(132):
    k=ids.index(targets[ch]);at=attrs[ch]
    if 19<=at<=21:rot[k,at-19]=vs[ch]
    else:tr[k,at-15]=vs[ch]
   # Player physics owns airborne displacement. Preserve rotations, suppress root translation in airborne states.
   if name in ('jump_start','jump_cycle','jump_land','glide_cycle'):tr[0]=local['root']
   worldR=[];worldT=[];mats=[]
   for k in range(43):
    rr=rotation(*rot[k]);tt=tr[k];p=parent[k]
    if p>=0:tt=worldR[p]@tt+worldT[p];rr=worldR[p]@rr
    worldR.append(rr);worldT.append(tt);rmat=flip@rr@flip;delta=flip@(rr@(center-pos[k])+tt-center)*scale;mats.append(np.column_stack([np.rint(rmat*4096),np.rint(delta)]).astype(int))
   frames.append(mats)
  clips.append(dict(name=name,start=start,frames=length,source_clip=n,source_record=c['source_record']))
 frames=np.array(frames);assert np.max(np.abs(frames))<32768
 def arr(x):return ',\n'.join('{'+','.join(map(str,row))+'}' for row in x.reshape(-1,x.shape[-1]))
 (out/'rig.h').write_text(f'#define BONE_COUNT 43\n#define ANIM_COUNT {len(clips)}\n#define ANIM_FRAMES {len(frames)}\nstatic const unsigned char skinbones[NV][4]={{\n'+arr(idx)+'};\nstatic const u16 skinweights[NV][4]={\n'+arr(qw)+'};\nstatic const s16 bonemats[ANIM_FRAMES][BONE_COUNT][12]={\n'+',\n'.join('{'+arr(f.reshape(43,12))+'}' for f in frames)+'};\nstatic const u16 animclips[ANIM_COUNT][2]={\n'+arr(np.array([[c['start'],c['frames']] for c in clips]))+'};\n')
 np.savez_compressed(out/'rig.npz',vertices=vv,bones=idx,weights=qw,matrices=frames,parents=parent,bind_positions=pos,names=names,targets=targets,attributes=attrs)
 rep=dict(joints=43,parent_max_error=max(err),channel_count=167,duplicate_channels=dup,channel_offset=channeloff,skinned_source_vertices=counts,weight_sum_max_error=maxerr,lod_vertices=len(vv),max_discarded_weight=float(discard.max()),mean_discarded_weight=float(discard.mean()),frames=len(frames),matrix_bytes=frames.size*2,clips=clips,limitations='Source joint IDs, bind matrices, skin weights, channel indices recovered. XYZ Euler convention and linear key interpolation provisional. Source facial morph, ss_scale and eye channels not played. Airborne root translation suppressed to prevent double motion; LOD weights reduced to four and quantized. No emulator verification.')
 (out/'rig_report.json').write_text(json.dumps(rep,indent=2));print(rep)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('iso',type=Path);p.add_argument('out',type=Path);a=p.parse_args();rig(a.iso,a.out)
