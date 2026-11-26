"""Improve source sector selection: use triangle bounds, not centroid alone."""
import json
from pathlib import Path
import numpy as np
import build_m06 as previous
from recover import records,nodes,u32
from build_spyro import arr

def apply(iso,out):
 # Reuse known materials and world upload, avoid adding unknown textures.
 z=np.load(out/'farm06.npz');data={k:z[k] for k in z.files};rep=json.loads((out/'report.json').read_text());r=records(iso);b=r[502][1];names={u32(b,p+4):n for p,n,q in nodes(b,0x47ba46ed)};lookup={int(x['material'],16):k for k,x in enumerate(rep['bindings'])};h=np.load(previous.ROOT/'build_m05/hub/hub.npz');tri=h['vertices'][h['faces']].astype(float)-data['source_origin'];m=h['material'];uv=h['uv'];f=h['faces'];cen=tri.mean(1);old=(np.max(np.abs(cen[:,[0,2]]),axis=1)<4996)&(np.max(np.abs(tri[:,:,[0,2]]),axis=(1,2))<9596);rad=6000;new=(tri[:,:,[0,2]].max(1)>=-rad).all(1)&(tri[:,:,[0,2]].min(1)<=rad).all(1)&(np.max(np.abs(tri[:,:,[0,2]]),axis=(1,2))<16000);extra=np.where(new&~old)[0];# retain already decoded materials, midwood uses diagnostic fallback of litwood
 # Add an independent material slot for the original midwood geometry.
 mid=[k for k in set(m[extra]) if k not in lookup];assert len(mid)==1 and names[mid[0]]=='midwood';h0=int(mid[0]);k=len(rep['bindings']);lookup[h0]=k
 x=320+64*(k//4);y=256+64*(k%4);cy=256+k
 rep['bindings'].append(dict(material=f'{h0:08x}',name='midwood',vram=[x,y,32,64],clut=[768,cy,256,1]));fallback={}

 vs=data['vertices'].tolist();fs=data['faces'].tolist();uvs=data['uv'].tolist();ids=data['texture_id'].tolist();seen={tuple(sorted(tuple(x) for x in np.rint(t*np.array([1,-1,1])).astype(int))) for t in tri[old]};added=0;fallback_count=0
 for i in extra:
  t=tri[i]*[1,-1,1];key=tuple(sorted(tuple(x) for x in np.rint(t).astype(int)))
  if key in seen:continue
  seen.add(key);k=lookup.get(int(m[i]),fallback.get(int(m[i])));added+=1;fallback_count+=int(int(m[i]) in fallback)
  for tt,st in previous.split(t,uv[f[i]].astype(float)):
   vv=np.rint(tt).astype(int);st=np.clip(np.rint(st*64),0,255).astype(int)
   if len(set(map(tuple,vv)))<3:continue
   base=len(vs);vs.extend(vv);fs.append([base,base+1,base+2]);uvs.append(st);ids.append(k)
 vv,ii=np.unique(np.array(vs),axis=0,return_inverse=True);ff=ii[np.array(fs)];uvs=np.array(uvs);ids=np.array(ids);assert abs(vv).max()<32768 and len(vv)<65536
 cluts=[];pages=[];windows=[]
 for b in rep['bindings']:
  x,y,_,_=b['vram'];cx,cy,_,_=b['clut'];cluts.append(cx//16|(cy<<6));pages.append(x//64|16|(1<<7));windows.append(0xe2000000|24|(24<<5)|(((y-256)//8)<<15))
 words=uvs[:,:,0]|(uvs[:,:,1]<<8);words[:,0]|=np.asarray(cluts)[ids]<<16;words[:,1]|=np.asarray(pages)[ids]<<16
 p=out/'world.h';s=p.read_text();start=s.index('static const s16 world[');end=s.index('static const s16 floorgrid[');s=s[:start]+'static const s16 world[WV][3]={'+arr(vv).replace('u','')+'};\nstatic const u16 worldfaces[WF][3]={'+arr(ff)+'};\nstatic const u32 worlduv[WF][3]={'+arr(words)+'};\nstatic const u32 worldwindow[WF]={'+','.join(str(windows[k])+'u' for k in ids)+'};\n'+s[end:];import re;s=re.sub(r'#define WV \d+',f'#define WV {len(vv)}',s);s=re.sub(r'#define WF \d+',f'#define WF {len(ff)}',s);p.write_text(s);data.update(vertices=vv,faces=ff,uv=uvs,texture_id=ids);np.savez_compressed(out/'farm06.npz',**data);rep.update(world_vertices=len(vv),world_faces=len(ff),sector_source_triangles_added=added,sector_midwood_fallback_triangles=fallback_count,sector_radius=rad,sector_selection='triangle AABB intersection, original coordinates; independent midwood slot');(out/'report.json').write_text(json.dumps(rep,indent=2));print('Sector extended',added,len(ff),fallback_count)
