"""Source-collision farm prototype with provisional source-texture bindings."""
import argparse,collections,json,math,re,struct,subprocess
from pathlib import Path
import numpy as np
from PIL import Image
from recover import records,nodes,pxt_groups,u32
from build_spyro import arr
import build_play,hub_collision
ROOT=Path(__file__).resolve().parents[1]
CENTER=np.array([38000,0,2000]);R=4096;STEP=128;SIZE=65
# Visual candidates, not exact filename-hash associations. Each is an extracted source texture.
CANDIDATES={'largeivy':86,'yellow_T':121,'wheat':68,'litwood':294,'sdgrass_T':191,'yground':341,'hay':199,'wallgrass':213,'nredwood':237,'vtree':115,'trunk':217,'wall':46,'treeygrass_tr':170,'onlyhay':292,'carkey':222,'housewood':219,'broof':286}

def source_registry(r,out):
 b=r[502][1];table=r[442][1];pxt=r[772][1];groups=list(pxt_groups(pxt));count=u32(table,12);assert count==len(groups)==540
 registry=[]
 for i,(offset,pal,imgs) in enumerate(groups):
  h,o,s,t=struct.unpack_from('<IIII',table,16+i*16);end=groups[i+1][0] if i+1<count else len(pxt);assert o-len(table)==offset and s==end-offset-16
  registry.append(dict(group=i,hash=f'{h:08x}',offset=offset,size=s,type=t,dimensions=list(imgs[0][:2]) if imgs else None,palette=len(pal)))
 texnodes={u32(b,p+4):(n,q) for p,n,q in nodes(b,0xdad78930)};materials=collections.defaultdict(list)
 for p,n,q in nodes(b,0x47ba46ed):
  h=u32(b,p+4);t=u32(b,q+96)
  # Find the following texture node directly, rather than a last-name-wins guess.
  for pp,nn,qq in nodes(b[q+96:q+800],0xdad78930):
   if u32(b,q+96+pp+4)!=t:continue
   qq+=q+96;m=re.search(rb'[0-9A-F]{8}\.PXT',b[qq:qq+150]);
   if not m:continue
   w,hh,_,s=struct.unpack_from('<HHHI',b,qq+m.end());materials[h].append(dict(name=n,texture_node=nn,filename=m.group().decode(),width=w,height=hh,size=s));break
 (out/'texture_registry.json').write_text(json.dumps({'directory_record':442,'payload_record':772,'entries':registry,'materials':{f'{h:08x}':v for h,v in materials.items()},'limitation':'Directory offsets/sizes validated. Filename hash unresolved; visually selected candidates remain provisional.'},indent=2));return groups,registry,materials

def collision(iso,out):
 col=out.parent/'collision'
 if not (col/'collision.npz').exists():hub_collision.recover(iso,col)
 z=np.load(col/'collision.npz');t=z['vertices'][z['faces']].astype(float)-CENTER;t[:,:,1]*=-1;keep=(np.min(t[:,:,[0,2]],axis=1)<=R).all(1)&(np.max(t[:,:,[0,2]],axis=1)>=-R).all(1);t=t[keep]
 n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n=n/np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-9)
 old=np.load(out/'farm.npz')['floor'];X,Z=np.meshgrid(np.arange(SIZE)*STEP-R,np.arange(SIZE)*STEP-R);floor=np.full((SIZE,SIZE),32767,dtype=np.int16);best=np.full((SIZE,SIZE),1e9)
 for a,b,c in t[abs(n[:,1])>.7]:
  den=(b[0]-a[0])*(c[2]-a[2])-(b[2]-a[2])*(c[0]-a[0]);u=((X-a[0])*(c[2]-a[2])-(Z-a[2])*(c[0]-a[0]))/den;w=((b[0]-a[0])*(Z-a[2])-(b[2]-a[2])*(X-a[0]))/den;y=a[1]+u*(b[1]-a[1])+w*(c[1]-a[1]);score=np.where(old!=32767,abs(y-old),abs(y-650));mask=(u>=-1e-6)&(w>=-1e-6)&(u+w<=1.000001)&(y>-800)&(y<1700)&(score<best);floor[mask]=np.rint(y[mask]).astype(np.int16);best[mask]=score[mask]
 # Only admit candidates corroborated by the visual floor; do not silently substitute guesses.
 corroborated=(floor!=32767)&(old!=32767)&(best<120);source_count=int((floor!=32767).sum());floor[~corroborated]=32767
 # Grid samples touching vertical source walls at player height are blocked. Use a conservative
 # 70-unit radius around projected edges; only apply when vertical interval overlaps the body.
 blocked=np.zeros_like(corroborated)
 for tri in t[abs(n[:,1])<.4]:
  if tri[:,1].max()-tri[:,1].min()<100:continue
  near=(floor!=32767)&(tri[:,1].min()<floor-50)&(tri[:,1].max()>floor-160)
  for a,b in zip(tri,np.roll(tri,1,axis=0)):
   dx,dz=b[[0,2]]-a[[0,2]];den=dx*dx+dz*dz
   if den<1e-5:continue
   s=np.clip(((X-a[0])*dx+(Z-a[2])*dz)/den,0,1);blocked|=near&((X-a[0]-s*dx)**2+(Z-a[2]-s*dz)**2<70**2)
 floor[blocked]=32767
 cand=[]
 for iz in range(2,SIZE-2):
  for ix in range(2,SIZE-2):
   p=floor[iz-1:iz+2,ix-1:ix+2];
   if np.all(p!=32767) and np.ptp(p.astype(int))<100:cand.append(((int(floor[iz,ix])<0,(ix-SIZE//2)**2+(iz-SIZE//2)**2),ix,iz))
 assert cand,'No corroborated spawn';_,ix,iz=min(cand);spawn=[ix*STEP-R,int(floor[iz,ix]),iz*STEP-R]
 return floor,spawn,dict(local_collision_triangles=len(t),source_floor_samples=source_count,corroborated_samples=int(corroborated.sum()),wall_blocked=int(blocked.sum()),walkable_samples=int((floor!=32767).sum()),safe_spawn_candidates=len(cand),source_vs_visual_median_delta=float(np.median(best[corroborated]))),t

def split(t,uv,depth=0):
 # PS1 UV is 8-bit; keep all repeated UV values within one 256-coordinate span.
 st=uv-np.floor(uv.min(0));
 if np.max(st)*64<255.5:return [(t,st)]
 assert depth<10
 i,j=max([(0,1),(1,2),(2,0)],key=lambda ij:np.linalg.norm(uv[ij[0]]-uv[ij[1]]));k=3-i-j;tm=(t[i]+t[j])*.5;um=(uv[i]+uv[j])*.5
 return split(np.array([t[i],tm,t[k]]),np.array([uv[i],um,uv[k]]),depth+1)+split(np.array([tm,t[j],t[k]]),np.array([um,uv[j],uv[k]]),depth+1)

def prepare(iso,out):
 out.mkdir(parents=True,exist_ok=True);r=records(iso);groups,registry,materials=source_registry(r,out);build_play.CENTER=CENTER
 # previous exact geometry data is retained; regenerate it if the local ISO is supplied alone
 hub=ROOT/'build_m05/hub';from hub_mesh import recover_hub
 if not (hub/'hub.npz').exists():recover_hub(iso,hub)
 import shutil
 if not (out.parent/'hub').exists():shutil.copytree(hub,out.parent/'hub')
 build_play.prepare(iso,out);floor,spawn,crep,collision_tri=collision(iso,out)
 z=np.load(hub/'hub.npz');v=z['vertices'].astype(float)-CENTER;f=z['faces'];m=z['material'];uv=z['uv'];tri=v[f];c=tri.mean(1);keep=(np.max(np.abs(c[:,[0,2]]),axis=1)<R+900)&(np.max(np.abs(tri[:,:,[0,2]]),axis=(1,2))<R+5500);f=f[keep];m=m[keep];tri=tri[keep];tri[:,:,1]*=-1
 b=r[502][1];names={u32(b,p+4):n for p,n,q in nodes(b,0x47ba46ed)}
 unique=sorted(set(int(x) for x in m));tex=[];upload=[];windows=[];cluts=[];pages=[];bindings=[]
 for k,h in enumerate(unique):
  name=names[h];i=CANDIDATES[name];_,pal,imgs=groups[i];w,hh,ix=imgs[0];assert len(pal)==256 and w in (64,128) and hh==w
  # Verify candidate dimensions/payload size against at least one named source reference when possible.
  refs=materials.get(h,[]);same=[x for x in refs if x['width']==w and x['height']==hh and x['size']==registry[i]['size']];
  ix=np.asarray(Image.fromarray(ix).resize((64,64),Image.Resampling.NEAREST));rgb=pal.astype(np.uint16);color=(rgb[:,0]>>3)|((rgb[:,1]>>3)<<5)|((rgb[:,2]>>3)<<10);color=np.maximum(color,1);# alpha threshold for foliage only
  if name in ('largeivy','wheat','yellow_T','treeygrass_tr','onlyhay'):color=np.where(rgb[:,3]<64,0,color)
  color=color.astype('<u2');x=320+64*(k//4);y=256+64*(k%4);cy=256+k;assert x+32<=768 and cy<512
  upload.extend([0xa0000000,768|(cy<<16),(1<<16)|256]);upload.extend(np.frombuffer(color.tobytes(),'<u4').tolist());upload.extend([0xa0000000,x|(y<<16),(64<<16)|32]);upload.extend(np.frombuffer(ix.tobytes(),'<u4').tolist());cluts.append((768//16)|(cy<<6));pages.append((x//64)|16|(1<<7));windows.append(0xe2000000|24|(24<<5)|(((y-256)//8)<<15));
  tex.append(color[ix]);bindings.append(dict(material=f'{h:08x}',name=name,group=i,source_refs=refs,matching_metadata_signatures=len(same),binding='visual candidate, unverified filename hash',vram=[x,y,32,64],clut=[768,cy,256,1]))
 # retain actual source UVs and split triangles that exceed the 8-bit UV span
 vs=[];fs=[];uvs=[];ids=[];seen=set()
 for t,idx,h in zip(tri,f,m):
  key=tuple(sorted(tuple(x) for x in np.rint(t).astype(int)))
  if key in seen:continue
  seen.add(key);k=unique.index(int(h));
  for tt,st in split(t,uv[idx].astype(float)):
   vv=np.rint(tt).astype(int);st=np.clip(np.rint(st*64),0,255).astype(int)
   if len(set(map(tuple,vv)))<3:continue
   base=len(vs);vs.extend(vv);fs.append([base,base+1,base+2]);uvs.append(st);ids.append(k)
 vv,ii=np.unique(np.array(vs),axis=0,return_inverse=True);ff=ii[np.array(fs)];uvs=np.array(uvs);ids=np.array(ids);words=uvs[:,:,0]|(uvs[:,:,1]<<8);words[:,0]|=np.asarray(cluts)[ids]<<16;words[:,1]|=np.asarray(pages)[ids]<<16
 # UV-interpolated clipped triangles are textured in the runtime renderer.
 hdr=f'#define WV {len(vv)}\n#define WF {len(ff)}\n#define GRID {SIZE}\n#define GRID_STEP {STEP}\n#define GRID_RADIUS {R}\n#define SPAWN_X {spawn[0]}\n#define SPAWN_Y {spawn[1]}\n#define SPAWN_Z {spawn[2]}\n'
 hdr+='static const s16 world[WV][3]={'+','.join('{'+','.join(str(int(x)) for x in row)+'}' for row in vv)+'};\nstatic const u16 worldfaces[WF][3]={'+arr(ff)+'};\nstatic const u32 worlduv[WF][3]={'+arr(words)+'};\nstatic const u32 worldwindow[WF]={'+','.join(str(windows[k])+'u' for k in ids)+'};\nstatic const s16 floorgrid[GRID*GRID]={'+','.join(str(int(x)) for x in floor.ravel())+'};\nstatic const s16 sine[64]={'+','.join(str(int(x)) for x in np.rint(np.sin(np.arange(64)*2*np.pi/64)*4096))+'};\n#define WORLD_UPLOAD_WORDS '+str(len(upload))+'\nstatic const u32 worldupload[WORLD_UPLOAD_WORDS]={'+','.join(str(x)+'u' for x in upload)+'};\n'
 (out/'world.h').write_text(hdr);np.savez_compressed(out/'farm06.npz',vertices=vv,faces=ff,uv=uvs,texture_id=ids,textures=np.array(tex),floor=floor,spawn=spawn,source_origin=CENTER,collision_triangles=collision_tri)
 rep=dict(world_vertices=len(vv),world_faces=len(ff),material_candidates=len(bindings),candidate_metadata_matches=sum(bool(x['matching_metadata_signatures']) for x in bindings),texture_vram_bytes=len(bindings)*(4096+512),texture_window='64x64 repeating texture, 8-bit CLUT; split UV spans offline',spawn=spawn,source_origin=CENTER.tolist(),collision=crep,bindings=bindings,limitations='Source terrain geometry and UVs; source texture visual candidates, not verified associations. Collision is heuristic polygon scan, corroborated grid, not original BSP; test sector intentionally restricted. No original animations or streaming.')
 (out/'report.json').write_text(json.dumps(rep,indent=2));print({k:v for k,v in rep.items() if k!='bindings'});return rep

def build(iso,out):
 out=out.resolve();rep=prepare(iso,out);opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0']
 def run(args):subprocess.run(args,cwd=out,check=True)
 run(opts+['-c',str(ROOT/'src/dynamic_start.s'),'-o','start.o']);run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(out),'-c',str(ROOT/'src/play06.c'),'-o','play06.o']);run(['ld.lld','-m','elf32ltsmip','-T',str(ROOT/'src/dynamic.ld'),'start.o','play06.o','-o','play06.elf']);run(['llvm-objcopy','-O','binary','play06.elf','play06.bin']);data=(out/'play06.bin').read_bytes();data+=bytes((-len(data))%2048);header=bytearray(2048);header[:8]=b'PS-X EXE';struct.pack_into('<IIII',header,16,0x80010000,0,0x80010000,len(data));struct.pack_into('<II',header,0x30,0x801fff00,0);(out/'ETD_FARM.EXE').write_bytes(header+data);rep['exe_bytes']=len(data)+2048;rep['native_runtime']='compiled; no emulator/hardware execution';(out/'report.json').write_text(json.dumps(rep,indent=2));print('EXE',rep['exe_bytes'])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('iso',type=Path);p.add_argument('out',type=Path);a=p.parse_args();build(a.iso,a.out)
