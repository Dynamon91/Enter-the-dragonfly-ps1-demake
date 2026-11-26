"""Extract original type-2 float curve arrays; strict length, time and duplicated metadata checks.
No curve-to-joint binding or tangent interpretation claimed."""
import argparse,collections,struct,json,hashlib
from pathlib import Path
import numpy as np
from recover import records,nodes
from hash08 import fold
CLIP=0x07d16200; CURVE=0x2d5e8c2f

def metadata(b):
 for p,name,q in nodes(b,CLIP):
  if not name.startswith('spyro_'):continue
  n,flag=struct.unpack_from('<HH',b,q)
  if not 0<n<=400:continue
  ids=struct.unpack_from(f'<{n}I',b,q+4); idx=struct.unpack_from(f'<{n}I',b,q+4+4*n); start=q+4+8*n+16
  curves=[]
  for pp,nn,qq in nodes(b[start:start+n*120+50],CURVE):
   if len(curves)==n:break
   a,z,k,t,off=struct.unpack_from('<ffHHI',b,start+qq-8); h=struct.unpack_from('<I',b,start+pp+4)[0]
   curves.append(dict(name=nn,id=h,start=a,end=z,keys=k,type=t,offset=off))
  if len(curves)!=n or set(x['id'] for x in curves)!=set(ids) or len(set(ids))!=n:continue
  if any(x['type']!=2 or x['keys']<2 for x in curves):continue
  curves.sort(key=lambda x:x['offset']); pos=0
  for x in curves:
   if x['offset']!=pos:break
   pos+=x['keys']*16
  else:
   yield name,dict(clip_id=struct.unpack_from('<I',b,p+4)[0],header_duration=struct.unpack_from('<f',b,q-4)[0],ids=ids,indices=idx,curves=curves,bytes=pos)

def decode(buf,meta):
 if len(buf)!=meta['bytes']:return None
 out=[]
 for c in meta['curves']:
  v=np.frombuffer(buf,'<f4',c['keys']*4,c['offset']).reshape(4,-1); t=v[0]
  if not np.isfinite(v[:2]).all() or np.any(~np.isfinite(v[2:]) & (v[2:].view("<u4")!=0xffffffff)) or abs(float(t[0])-c['start'])>1e-4 or abs(float(t[-1])-c['end'])>1e-4 or (np.diff(t)<=0).any():return None
  out.append(v.copy())
 return out

def extract(iso,out):
 out.mkdir(parents=True,exist_ok=True);r=records(iso);meta=dict(metadata(r[502][1]));dup=dict(metadata(r[1641][1])); bysize=collections.defaultdict(list)
 for i,(h,b) in r.items():bysize[len(b)].append((i,h,b))
 clips=[]; arrays={}; unresolved=[]
 for name,m in meta.items():
  hits=[]
  for i,h,b in bysize[m['bytes']]:
   v=decode(b,m)
   if v is not None:hits.append((i,h,b,v))
  if len(hits)!=1:
   unresolved.append(dict(name=name,candidates=[i for i,h,b,v in hits],bytes=m['bytes']));continue
  i,h,b,v=hits[0]; packed=np.concatenate(v,axis=1); offsets=np.cumsum([0]+[x.shape[1] for x in v]); arrays[name]=packed; arrays[name+'_offsets']=offsets
  clips.append(dict(name=name,source_record=i,source_id=f'{h:08x}',sha256=hashlib.sha256(b).hexdigest(),duplicate_metadata=dup.get(name)==m,curve_count=len(v),key_count=int(offsets[-1]),sentinel_words=int((packed[2:].view("<u4")==0xffffffff).sum()),curve_start=min(c['start'] for c in m['curves']),curve_end=max(c['end'] for c in m['curves']),metadata=m))
 np.savez_compressed(out/'curves.npz',**arrays)
 report=dict(metadata_record=502,duplicate_metadata_record=1641,metadata_clips=len(meta),resolved_clips=len(clips),duplicate_confirmed=sum(c['duplicate_metadata'] for c in clips),curves=sum(c['curve_count'] for c in clips),keys=sum(c['key_count'] for c in clips),clips=clips,unresolved=unresolved,limitations='Unique matches by contiguous type-2 payload size and all curve time bounds; four 32-bit arrays per curve (time, value, two candidate tangent arrays). Original 0xffffffff words preserved in candidate tangent arrays; their meaning remains unknown. No bone/channel binding or tangent interpolation semantics verified. Not integrated into native playback.')
 (out/'animation.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k not in ('clips','unresolved')});print('unresolved',unresolved)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('iso',type=Path);p.add_argument('out',type=Path);a=p.parse_args();extract(a.iso,a.out)
