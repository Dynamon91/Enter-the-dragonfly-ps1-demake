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
 out.mkdir(parents=True,exist_ok=True);reg=json.loads((ROOT/'build_m15/play/texture_registry.json').read_text());byfile={r['filename']:r for r in reg['resolved_references']};groups=collections.defaultdict(lambda:{'r':[],'c':[],'o':[]});materials=[];matid={};meshmeta=[];gaps=collections.Counter();sources=[];n=0
 for path in ['build_m05/hub','build_m08/shadow']:
  z=np.load(ROOT/path/'hub.npz');meta=json.loads((ROOT/path/'hub_report.json').read_text())['meshes'];t=z['vertices'][z['faces']].astype(float)*[1,-1,1];u=z['uv'][z['faces']].astype(float);shapeids=z['part'];srcbase=len(meshmeta);meshmeta.extend(meta);bind=[]
  for m in meta:
   h=m['material'];refs=reg['materials'].get(h,[]);rr=region(m['name']);local=[x for x in refs if x['texture_node'].startswith('the_hub_'+rr+'_')];hub=[x for x in refs if x['texture_node'].startswith('the_hub_')];candidates=local or hub or refs;files=sorted({x['filename'] for x in candidates});status='resolved' if len(files)==1 and byfile[files[0]]['dimensions_match'] else 'ambiguous' if len(files)>1 else 'missing' if not files else 'unsupported';file=files[0] if status=='resolved' else None;key=(h,rr,status,tuple(files))
   if key not in matid:
    matid[key]=len(materials);materials.append(dict(id=matid[key],material=h,region=rr,status=status,filename=file,texture_group=byfile[file]['group'] if file else None,candidates=files))
   bind.append(matid[key])
  for i,(p,uv,sh) in enumerate(zip(t,u,shapeids)):
   k=cell(p.mean(0));org=origin(k);q=quant(p,org);uq=np.rint(uv*1024).astype(np.int64);assert uq.min()>=-32768 and uq.max()<=32767;mi=bind[sh];gaps[materials[mi]['status']]+=1
   rec=q.tobytes()+uq.astype('<i2').tobytes()+struct.pack('<HI',mi,n);assert len(rec)==R;groups[k]['r'].append((rec,q.reshape(3,3)));n+=1
  sources.append(dict(path=path,first_triangle=n-len(t),count=len(t),first_mesh=srcbase,mesh_count=len(meta)))
 z=np.load(ROOT/'build_m06/collision/collision.npz');t=z['vertices'][z['faces']].astype(float)*[1,-1,1];flags=z['polygon_flags'][z['part']]
 for i,(p,flag) in enumerate(zip(t,flags)):
  k=cell(p.mean(0));q=quant(p,origin(k));rec=q.tobytes()+struct.pack('<HI',int(flag),i);assert len(rec)==C;groups[k]['c'].append((rec,q))
 places=json.loads((ROOT/'assets_m12/placements.json').read_text());basket=json.loads((ROOT/'assets_m14/basket_report.json').read_text())['source_placements'];sheep=json.loads((ROOT/'assets_m15/fodder_report.json').read_text())['sheep_placements'];bs={x['record_offset'] for x in basket};ss={x['record_offset'] for x in sheep};obj=[]
 for kind,rows in [(1,places['gems']),(4,places['other_characters']),(2,basket),(3,sheep)]:
  for p in rows:
   off=p['record_offset'];kind1=2 if off in bs else 3 if off in ss else kind
   if any(x['record_offset']==off for x in obj):continue
   obj.append(dict(p,kind=kind1));xyz=np.array(p['source_xyz'])*[1,-1,1];k=cell(xyz);q=quant(xyz,origin(k));rec=q.tobytes()+struct.pack('<HHHI',kind1,p.get('value',0),0,off);assert len(rec)==O;groups[k]['o'].append((rec,q.reshape(1,3)))
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
 (out/'HUBSECT.DAT').write_bytes(blob);idx=bytearray(struct.pack('<4sHHII',b'ETDI',1,D.size,len(directory),CELL))
 for d in directory:idx.extend(D.pack(d['id'],d['lba'],d['size'],d['crc'],*d['origin'],*d['bounds'][0],*d['bounds'][1],d['render'],d['collision'],d['objects']))
 (out/'HUBSECT.IDX').write_bytes(idx)
 rep=dict(render_triangles=n,collision_candidates=len(t),object_placements=len(obj),object_kinds=dict(collections.Counter(x['kind'] for x in obj)),cells=len(groups),blocks=len(directory),max_block=max(d['size'] for d in directory),data_bytes=len(blob),index_bytes=len(idx),materials=len(materials),material_face_counts=dict(gaps),max_cell_blocks=max(collections.Counter(tuple(d['cell']) for d in directory).values()),sources=sources,limitations='Centroid-owned original triangles with full AABBs; quantized original UV Q10 and positions, not final split PS1 GPU primitives. Collision candidates are not verified complete BSP. Ambiguous/missing materials are explicit. No native disc I/O, runtime sector switching, or VRAM streaming yet.')
 (out/'sector_report.json').write_text(json.dumps(rep,indent=2));(out/'sector_manifest.json').write_text(json.dumps(dict(blocks=directory,materials=materials,objects=obj,meshes=meshmeta),indent=2));print(json.dumps(rep,indent=2));return rep
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('out',type=Path);build(p.parse_args().out)
