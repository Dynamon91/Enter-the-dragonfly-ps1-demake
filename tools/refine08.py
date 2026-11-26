"""Subdivide nearby source ground for ordering-table stability and extend corroborated collision."""
import json,re
import numpy as np
from build_spyro import arr
GROUND={'yelground','yground','onlyhay','haygrass','sand','sdgrass_T','yellow_T'}

def subdiv(t,uv,limit):
 d=np.sum((t-np.roll(t,1,axis=0))**2,axis=1);i=int(d.argmax());j=(i-1)%3;k=3-i-j
 if d[i]<=limit*limit:return [(t,uv)]
 m=(t[i]+t[j])/2;u=(uv[i]+uv[j])/2
 return subdiv(np.array([t[j],m,t[k]]),np.array([uv[j],u,uv[k]]),limit)+subdiv(np.array([m,t[i],t[k]]),np.array([u,uv[i],uv[k]]),limit)

def collision_grid(data,names):
 old=data['floor'];X,Z=np.meshgrid(np.arange(65)*128-4096,np.arange(65)*128-4096);vis=data['vertices'][data['faces']].astype(float);m=np.array([names[k] for k in data['texture_id']]);col=data['collision_triangles'].astype(float)
 def sample(t):
  a,b,c=t;den=(b[0]-a[0])*(c[2]-a[2])-(b[2]-a[2])*(c[0]-a[0]);n=np.cross(b-a,c-a);l=np.linalg.norm(n)
  if l<1e-6 or abs(n[1])/l<.7 or abs(den)<1e-6:return None
  u=((X-a[0])*(c[2]-a[2])-(Z-a[2])*(c[0]-a[0]))/den;w=((b[0]-a[0])*(Z-a[2])-(b[2]-a[2])*(X-a[0]))/den;y=a[1]+u*(b[1]-a[1])+w*(c[1]-a[1]);mask=(u>=-1e-6)&(w>=-1e-6)&(u+w<=1.000001)&(y>-800)&(y<1700);return y,mask
 # Prefer the low ground near existing farm spawn, while matching original collision polygons.
 floor=old.copy();candidate=np.full(old.shape,32767,dtype=np.int16);score=np.full(old.shape,1e9);rv=[]
 for t in vis[np.isin(m,list(GROUND))]:
  res=sample(t)
  if res is not None and res[1].any():rv.append(res)
 for t in col:
  res=sample(t)
  if res is None:continue
  y,mask=res
  if not mask.any():continue
  delta=np.full(old.shape,1e9)
  for h,valid in rv:delta=np.minimum(delta,np.where(valid,abs(h-y),1e9))
  s=abs(y-data['spawn'][1])+delta*2;valid=mask&(delta<=100)&(s<score);candidate[valid]=np.rint(y[valid]).astype(np.int16);score[valid]=s[valid]
 blocked=np.zeros_like(old,dtype=bool)
 for tri in col:
  n=np.cross(tri[1]-tri[0],tri[2]-tri[0]);l=np.linalg.norm(n)
  if not l or abs(n[1])/l>=.4 or np.ptp(tri[:,1])<100:continue
  near=(candidate!=32767)&(tri[:,1].min()<candidate-50)&(tri[:,1].max()>candidate-160)
  for a,b in zip(tri,np.roll(tri,1,axis=0)):
   dx,dz=b[[0,2]]-a[[0,2]];den=dx*dx+dz*dz
   if den<1e-5:continue
   s=np.clip(((X-a[0])*dx+(Z-a[2])*dz)/den,0,1);blocked|=near&((X-a[0]-s*dx)**2+(Z-a[2]-s*dz)**2<70**2)
 # Only new samples meeting render/collision/wall checks; keep previous grid unchanged at valid cells.
 new=(old==32767)&(candidate!=32767)&~blocked;floor[new]=candidate[new]
 return floor,int(new.sum())

def apply(out):
 a=np.load(out/'farm06.npz');d={k:a[k] for k in a.files};a.close();rep=json.loads((out/'report.json').read_text());names=[b['name'] for b in rep['bindings']];t=d['vertices'][d['faces']];uv=d['uv'];ids=d['texture_id'];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n=abs(n[:,1])/np.maximum(np.linalg.norm(n,axis=1),1);g=np.isin(np.array(names)[ids],list(GROUND))&(n>.5);p=t[:,:,[0,2]]-d['spawn'][[0,2]];near=(p.max(1)>=-2500).all(1)&(p.min(1)<=2500).all(1);refine=g&near;vs=[];us=[];ks=[];floor,added=collision_grid(d,names);before=len(t)
 for j,(tri,st,k) in enumerate(zip(t,uv,ids)):
  tris=subdiv(tri.astype(float),st.astype(float),384) if refine[j] else [(tri,st)]
  for tt,uu in tris:
   v=np.rint(tt).astype(int);u=np.rint(uu).astype(int)
   if len(set(map(tuple,v)))<3:continue
   vs.append(v);us.append(u);ks.append(k)
 v,idx=np.unique(np.array(vs).reshape(-1,3),axis=0,return_inverse=True);f=idx.reshape(-1,3);uv=np.asarray(us);ids=np.asarray(ks);assert len(v)<65536 and abs(v).max()<32768
 # compact packet layout in native engine permits more subdivided faces without oversized static memory.
 cluts=[];pages=[];windows=[]
 for b in rep['bindings']:
  x,y,_,_=b['vram'];cx,cy,_,_=b['clut'];cluts.append(cx//16|(cy<<6));pages.append(x//64|16|(1<<7));windows.append(0xe2000000|24|(24<<5)|(((y-256)//8)<<15))
 words=uv[:,:,0]|(uv[:,:,1]<<8);words[:,0]|=np.asarray(cluts)[ids]<<16;words[:,1]|=np.asarray(pages)[ids]<<16
 h=out/'world.h';s=h.read_text();start=s.index('static const s16 world[');end=s.index('static const s16 sine[');s=s[:start]+'static const s16 world[WV][3]={'+','.join('{'+','.join(str(int(x)) for x in row)+'}' for row in v)+'};\nstatic const u16 worldfaces[WF][3]={'+arr(f)+'};\nstatic const u32 worlduv[WF][3]={'+arr(words)+'};\nstatic const u32 worldwindow[WF]={'+','.join(str(windows[k])+'u' for k in ids)+'};\nstatic const s16 floorgrid[GRID*GRID]={'+','.join(str(int(x)) for x in floor.ravel())+'};\n'+s[end:];s=re.sub(r'#define WV \d+',f'#define WV {len(v)}',s);s=re.sub(r'#define WF \d+',f'#define WF {len(f)}',s);h.write_text(s);d.update(vertices=v,faces=f,uv=uv,texture_id=ids,floor=floor);np.savez_compressed(out/'farm06.npz',**d);rep.update(world_vertices=len(v),world_faces=len(f),triangles_before_subdivision=before,refined_ground_input=int(refine.sum()),triangles_added_subdivision=len(f)-before,ground_edge_limit=384,collision_new_samples=added,collision_total_samples=int((floor!=32767).sum()));(out/'report.json').write_text(json.dumps(rep,indent=2));print('Subdivided terrain',before,len(f),'new collision samples',added)
