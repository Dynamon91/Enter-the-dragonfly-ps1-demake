"""Exact occupied-anchor texture and terrain pressure; verifies all six banks."""
import json,struct,collections,argparse
from pathlib import Path

def audit(p):
 ix=(p/'native/LIASECT.IDX').read_bytes();d=(p/'native/LIASECT.DAT').read_bytes();m=json.loads((p/'assets/bindings_resolved.json').read_text())['materials'];events=collections.defaultdict(list)
 for i in range((len(ix)-16)//60):
  e=struct.unpack_from('<IIII3i6i3H2x',ix,16+i*60);o=e[1]*2048;g=0
  for j in range(e[13]):g|=1<<m[struct.unpack_from('<H',d,o+64+j*36+30)[0]]['group']
  a,b=(e[7]-1792-256+511)//512,(e[10]+1792-256)//512;c,f=(e[9]-1792-256+511)//512,(e[12]+1792-256)//512;size=(e[2]+2047)//2048*2048
  if a<=b and c<=f:events[a].append((i,c,f,g,size,1));events[b+1].append((i,c,f,g,size,-1))
 active={};peak=pc=pt=occ=overflow=0;keys=sorted(events)
 for index,x in enumerate(keys):
  for i,c,f,g,size,sign in events[x]:
   if sign==1:active[i]=(c,f,g,size)
   else:active.pop(i)
  if not active:continue
  ze=collections.defaultdict(list)
  for i,(c,f,g,size) in active.items():ze[c].append((i,g,size,1));ze[f+1].append((i,g,size,-1))
  za={};zs=sorted(ze);sz=0
  for j,z in enumerate(zs[:-1]):
   for i,g,size,sg in ze[z]:
    if sg==1:za[i]=g;sz+=size
    else:za.pop(i);sz-=size
   if za:
    n=(keys[index+1]-x)*(zs[j+1]-z);occ+=n;mask=0
    for g in za.values():mask|=g
    count=mask.bit_count();peak=max(peak,sz);pc=max(pc,len(za));pt=max(pt,count);overflow+=n*(count>64)
 r=dict(anchors=occ,peak_bytes=peak,peak_blocks=pc,peak_texture_groups=pt,anchors_over_64_textures=overflow);pr=json.loads((p/'summary.json').read_text())['packed'];assert peak==pr['peak_neighborhood_bytes'] and pc==pr['peak_neighborhood_blocks'];(p/'budget70.json').write_text(json.dumps(r,indent=2));return r
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();
 for k in ('C9','MM','HM','TD','JJ','BOSS'):print(k,audit(a.root/k))
