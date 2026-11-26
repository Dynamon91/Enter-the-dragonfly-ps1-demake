"""Restore omitted source ground passes, including named *_SHADOW_* meshes."""
import json,re
from pathlib import Path
import numpy as np
from build_m06 import split
from build_spyro import arr
from shadow08 import recover_hub

def apply(iso,out):
 p=out.parent/'shadow';recover_hub(iso,p)
 z=np.load(p/'hub.npz');meta=json.loads((p/'hub_report.json').read_text())['meshes'];a=np.load(out/'farm06.npz');data={k:a[k] for k in a.files};old_face_count=len(data['faces']);a.close();rep=json.loads((out/'report.json').read_text());reg=json.loads((out/'texture_registry.json').read_text());t=(z['vertices'][z['faces']].astype(float)-data['source_origin'])*[1,-1,1];b=t[:,:,[0,2]];keep=(b.max(1)>=-6000).all(1)&(b.min(1)<=6000).all(1)&(np.max(np.abs(b),axis=(1,2))<16000);lookup={int(m['material'],16):i for i,m in enumerate(rep['bindings'])};new=[];vs=data['vertices'].tolist();fs=data['faces'].tolist();uvs=data['uv'].tolist();ids=data['texture_id'].tolist();seen={(int(k),tuple(sorted(map(tuple,v)))) for k,v in zip(ids,data['vertices'][data['faces']])};source=0
 for i in np.where(keep)[0]:
  h=int(z['material'][i]);m=meta[z['part'][i]];region='beach' if m['name'].startswith('BEACH_') else 'farm'
  if h not in lookup:
   k=len(rep['bindings']);refs=reg['materials'][f'{h:08x}'];name=refs[0]['name'];x=320+64*(k//4);y=256+64*(k%4);cy=256+k;assert x+32<=768
   rep['bindings'].append(dict(material=f'{h:08x}',name=name,region=region,vram=[x,y,32,64],clut=[768,cy,256,1]));lookup[h]=k;new.append(name)
  k=lookup[h];source+=1
  for tt,st in split(t[i],z['uv'][z['faces'][i]].astype(float)):
   v=np.rint(tt).astype(int);st=np.clip(np.rint(st*64),0,255).astype(int);key=(k,tuple(sorted(map(tuple,v))))
   if len(set(map(tuple,v)))<3 or key in seen:continue
   seen.add(key);base=len(vs);vs.extend(v);fs.append([base,base+1,base+2]);uvs.append(st);ids.append(k)
 vv,ii=np.unique(np.array(vs),axis=0,return_inverse=True);ff=ii[np.array(fs)];uvs=np.array(uvs);ids=np.array(ids);assert abs(vv).max()<32768 and len(vv)<65536;cluts=[];pages=[];windows=[]
 for b in rep['bindings']:
  x,y,_,_=b['vram'];cx,cy,_,_=b['clut'];cluts.append(cx//16|(cy<<6));pages.append(x//64|16|(1<<7));windows.append(0xe2000000|24|(24<<5)|(((y-256)//8)<<15))
 words=uvs[:,:,0]|(uvs[:,:,1]<<8);words[:,0]|=np.asarray(cluts)[ids]<<16;words[:,1]|=np.asarray(pages)[ids]<<16
 p=out/'world.h';s=p.read_text();start=s.index('static const s16 world[');end=s.index('static const s16 floorgrid[');s=s[:start]+'static const s16 world[WV][3]={'+','.join('{'+','.join(str(int(x)) for x in row)+'}' for row in vv)+'};\nstatic const u16 worldfaces[WF][3]={'+arr(ff)+'};\nstatic const u32 worlduv[WF][3]={'+arr(words)+'};\nstatic const u32 worldwindow[WF]={'+','.join(str(windows[k])+'u' for k in ids)+'};\n'+s[end:];s=re.sub(r'#define WV \d+',f'#define WV {len(vv)}',s);s=re.sub(r'#define WF \d+',f'#define WF {len(ff)}',s);p.write_text(s);data.update(vertices=vv,faces=ff,uv=uvs,texture_id=ids);np.savez_compressed(out/'farm06.npz',**data);rep.update(world_vertices=len(vv),world_faces=len(ff),restored_hub_meshes=len(meta),restored_hub_triangles=len(z['faces']),restored_sector_source_triangles=source,restored_sector_render_triangles=len(ff)-old_face_count,restored_sector_new_materials=new);(out/'report.json').write_text(json.dumps(rep,indent=2));print('Restored source ground',source,'final triangles',len(ff),'new materials',new)
