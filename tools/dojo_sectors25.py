"""Offline hub streaming format, preserving source triangle identity and placement IDs.
Each block <= 64 KiB. Spatial ownership by centroid; directory bounds include entire
geometry, including cross-cell faces. This is NOT the final native level representation.
"""
from pathlib import Path
import argparse, collections, json, struct, zlib
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
CELL=4096; SECTOR=2048; MAX=65536; HDR=64; R=36; C=24; O=16
# Header: magic/version/header bytes/id/cell center xyz/counts/payload bytes/crc/bounds xyz min,max
H=struct.Struct('<4sHHIiiiHHHHII6h12x'); assert H.size==HDR
# Directory entry: id, LBA-relative, byte count, CRC, center, full world AABB, counts
D=struct.Struct('<IIII3i6i3H2x'); assert D.size==60

def cell(p):return tuple(np.floor(np.asarray(p)[[0,2]]/CELL).astype(int))
def origin(k):return np.array([k[0]*CELL+CELL//2,0,k[1]*CELL+CELL//2],dtype=np.int64)
def quant(t,org):
 a=np.rint(np.asarray(t)-org).astype(np.int64);assert a.min()>=-32768 and a.max()<=32767;return a.astype('<i2')
def region(name):
 n=name.lower();return next((b for a,b in [('beach','beach'),('farm','farm'),('river','river'),('castle','castle'),('wood','woods'),('mtn','mountains'),('mountain','mountains'),('always','always')] if a in n),'unknown')
def build(out):
 out.mkdir(parents=True,exist_ok=True);z=np.load(out/'dojo.npz');meta=json.loads((out/'dojo_report.json').read_text())['meshes'];reg=json.loads((out/'bindings.json').read_text());materials=reg['materials'];meshmeta=meta;groups=collections.defaultdict(lambda:{'r':[],'c':[],'o':[]});gaps=collections.Counter();sources=['L_1_DD.CNK'];n=0
 t=z['vertices'][z['faces']].astype(float)*[1,-1,1];u=z['uv'][z['faces']].astype(float);bind=reg['bindings'];shifted=0
 for p,uv,sh in zip(t,u,z['part']):
  k=cell(p.mean(0));q=quant(p,origin(k));uq=np.rint(uv*1024).astype(np.int64)
  if uq.min()<-32768 or uq.max()>32767:
   uq-=np.floor_divide(uq.min(0)+32768,1024)*1024;shifted+=1
  assert uq.min()>=-32768 and uq.max()<=32767,(n,uq)
  mi=bind[sh];gaps[materials[mi]['status']]+=1;rec=q.tobytes()+uq.astype('<i2').tobytes()+struct.pack('<HI',mi,n);groups[k]['r'].append((rec,q));n+=1
 z=np.load(out/'collision.npz');t=z['vertices'][z['faces']].astype(float)*[1,-1,1];flags=z['polygon_flags'][z['part']]
 for i,(p,flag) in enumerate(zip(t,flags)):
  k=cell(p.mean(0));q=quant(p,origin(k));rec=q.tobytes()+struct.pack('<HI',int(flag),i);groups[k]['c'].append((rec,q))
 obj=reg['objects']
 for p in obj:
  xyz=np.array(p['source_xyz'])*[1,-1,1];k=cell(xyz);q=quant(xyz,origin(k));rec=q.tobytes()+struct.pack('<HHHI',p['kind'],p.get('value',0),0,p['record_offset']);groups[k]['o'].append((rec,q.reshape(1,3)))
 # Blocks bounded to 64 KiB, contiguous by spatial cell; no triangle loss or duplication.
 blob=bytearray();directory=[];stats=collections.Counter()
 for k,g in sorted(groups.items()):
  pos={a:0 for a in 'rco'};org=origin(k)
  while any(pos[a]<len(g[a]) for a in pos):
   avail=MAX-HDR;sets={};counts=[];points=[]
   for a,size in [('r',R),('c',C),('o',O)]:
    take=min(len(g[a])-pos[a],avail//size);sets[a]=g[a][pos[a]:pos[a]+take];pos[a]+=take;avail-=take*size;counts.append(take);points.extend(x[1] for x in sets[a])
   payload=b''.join(x[0] for a in 'rco' for x in sets[a]);p=np.concatenate(points);lo=p.min(0);hi=p.max(0);crc=zlib.crc32(payload);idx=len(directory);header=H.pack(b'ETDS',1,HDR,idx,*map(int,org),*counts,0,len(payload),crc,*map(int,lo),*map(int,hi));block=header+payload;assert len(block)<=MAX
   directory.append(dict(id=idx,cell=list(map(int,k)),lba=len(blob)//SECTOR,size=len(block),crc=crc,origin=org.tolist(),bounds=[(lo+org).tolist(),(hi+org).tolist()],render=counts[0],collision=counts[1],objects=counts[2]));blob.extend(block);blob.extend(bytes((-len(blob))%SECTOR))
   for a,c in zip('rco',counts):stats[a]+=c
 assert stats['r']==n and stats['c']==len(t) and stats['o']==len(obj)
 (out/'DOJOSECT.DAT').write_bytes(blob);idx=bytearray(struct.pack('<4sHHII',b'ETDI',1,D.size,len(directory),CELL))
 for d in directory:idx.extend(D.pack(d['id'],d['lba'],d['size'],d['crc'],*d['origin'],*d['bounds'][0],*d['bounds'][1],d['render'],d['collision'],d['objects']))
 (out/'DOJOSECT.IDX').write_bytes(idx)
 rep=dict(uv_shifted=shifted,render_triangles=n,collision_candidates=len(t),object_placements=len(obj),object_kinds=dict(collections.Counter(x['kind'] for x in obj)),cells=len(groups),blocks=len(directory),max_block=max(d['size'] for d in directory),data_bytes=len(blob),index_bytes=len(idx),materials=len(materials),material_face_counts=dict(gaps),max_cell_blocks=max(collections.Counter(tuple(d['cell']) for d in directory).values()),sources=sources,limitations='Centroid-owned original triangles with full AABBs; quantized original UV Q10 and positions, not final split PS1 GPU primitives. Collision candidates are not verified complete BSP. Ambiguous/missing materials are explicit. Offline Dojo sector package; no gameplay integration.')
 (out/'sector_report.json').write_text(json.dumps(rep,indent=2));(out/'sector_manifest.json').write_text(json.dumps(dict(blocks=directory,materials=materials,objects=obj,meshes=meshmeta),indent=2));print(json.dumps(rep,indent=2));return rep
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('out',type=Path);build(p.parse_args().out)
