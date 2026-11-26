"""Repack exact v25 quantized world records into tighter 2048-unit cells.
Only local vertex origins change. Original IDs, UVs, material and flags remain intact."""
import collections,json,struct,zlib,shutil
from pathlib import Path
import numpy as np
from dojo_sectors25 import H,D
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT/'assets_m25';OUT=ROOT/'assets_m27';CELL=2048

def build():
 OUT.mkdir(exist_ok=True);m=json.loads((OLD/'sector_manifest.json').read_text());data=(OLD/'DOJOSECT.DAT').read_bytes();groups=collections.defaultdict(lambda:[[],[],[]]);sizes=[36,24,16];counts=[0,0,0]
 for b in m['blocks']:
  off=b['lba']*2048+64
  for k,(stride,count) in enumerate(zip(sizes,[b['render'],b['collision'],b['objects']])):
   for i in range(count):
    rec=data[off:off+stride];off+=stride;n=1 if k==2 else 3
    pts=np.array(struct.unpack_from('<'+'h'*(3*n),rec)).reshape(n,3)+b['origin'];center=pts.mean(0);cell=tuple(np.floor(center[[0,2]]/CELL).astype(int));origin=np.array([cell[0]*CELL+CELL//2,0,cell[1]*CELL+CELL//2]);p=pts-origin;assert p.min()>=-32768 and p.max()<=32767
    groups[cell][k].append((center[0],center[2],p.astype('<i2').tobytes()+rec[n*6:],p));counts[k]+=1
 blob=bytearray();blocks=[]
 for cell,g in sorted(groups.items()):
  origin=[int(cell[0]*CELL+CELL//2),0,int(cell[1]*CELL+CELL//2)];g=[sorted(a,key=lambda x:(x[0],x[1])) for a in g];pos=[0]*3
  while any(pos[k]<len(g[k]) for k in range(3)):
   free=65536-64;nn=[];parts=[];points=[]
   for k,s in enumerate(sizes):
    n=min(len(g[k])-pos[k],free//s);rows=g[k][pos[k]:pos[k]+n];pos[k]+=n;free-=n*s;nn.append(n);parts.extend(row[2] for row in rows);points.extend(row[3] for row in rows)
   p=np.concatenate(points);lo=p.min(0);hi=p.max(0);payload=b''.join(parts);crc=zlib.crc32(payload);i=len(blocks);h=H.pack(b'ETDS',1,64,i,*origin,*nn,0,len(payload),crc,*map(int,lo),*map(int,hi));b=h+payload
   blocks.append(dict(id=i,cell=list(map(int,cell)),lba=len(blob)//2048,size=len(b),crc=crc,origin=origin,bounds=[(lo+origin).tolist(),(hi+origin).tolist()],render=nn[0],collision=nn[1],objects=nn[2]));blob.extend(b);blob.extend(bytes((-len(blob))%2048))
 idx=bytearray(struct.pack('<4sHHII',b'ETDI',1,D.size,len(blocks),CELL))
 for b in blocks:idx.extend(D.pack(b['id'],b['lba'],b['size'],b['crc'],*b['origin'],*b['bounds'][0],*b['bounds'][1],b['render'],b['collision'],b['objects']))
 m['blocks']=blocks;(OUT/'sector_manifest.json').write_text(json.dumps(m,indent=2));(OUT/'DOJOSECT.DAT').write_bytes(blob);(OUT/'DOJOSECT.IDX').write_bytes(idx)
 for n in ['DOJOTEX.DAT','DOJOTEX.IDX']:shutil.copyfile(OLD/n,OUT/n)
 lo=np.array([b['bounds'][0] for b in blocks]);hi=np.array([b['bounds'][1] for b in blocks]);sizes=np.array([(b['size']+2047)//2048*2048 for b in blocks]);radius=1792;sets=set();peak=cap=0
 for x in range(lo[:,0].min()//512*512-2048,hi[:,0].max()+2048,512):
  for z in range(lo[:,2].min()//512*512-2048,hi[:,2].max()+2048,512):
   x1,z1=x+256,z+256;ids=tuple(np.flatnonzero((lo[:,0]<=x1+radius)&(hi[:,0]>=x1-radius)&(lo[:,2]<=z1+radius)&(hi[:,2]>=z1-radius)))
   if ids:sets.add(ids);peak=max(peak,int(sizes[list(ids)].sum()));cap=max(cap,len(ids))
 rep=dict(blocks=len(blocks),cells=len(groups),counts=counts,index_bytes=len(idx),disc_bytes=len(blob),peak_bytes=peak,max_blocks=cap,neighborhoods=len(sets),radius=radius);(OUT/'repack_report.json').write_text(json.dumps(rep,indent=2));print(rep)
if __name__=='__main__':build()
