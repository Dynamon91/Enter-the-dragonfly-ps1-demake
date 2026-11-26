"""Build a small farm-region movement diagnostic from exact source hub geometry."""
import argparse,json,struct,subprocess,math,re
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from hub_mesh import recover_hub
from recover import records,nodes,u32
from build_spyro import arr,pack
ROOT=Path(__file__).resolve().parents[1]
CENTER=np.array([40000,0,4000]);STEP=128;SIZE=65;R=4096

def prepare(iso,out):
 hub=out.parent/'hub'
 if not (hub/'hub.npz').exists():recover_hub(iso,hub)
 z=np.load(hub/'hub.npz');v=z['vertices'].astype(float)-CENTER;f=z['faces'];m=z['material'];tri=v[f];c=tri.mean(1);b=records(iso)[502][1];names={u32(b,p+4):n for p,n,q in nodes(b,0x47ba46ed)}
 n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);ln=np.linalg.norm(n,axis=1);n=n/np.maximum(ln[:,None],1e-9)
 keep=(np.max(np.abs(c[:,[0,2]]),axis=1)<R+900)&(np.max(np.abs(tri[:,:,[0,2]]),axis=(1,2))<R+5500)
 f=f[keep];m=m[keep];tri=tri[keep];n=n[keep];c=c[keep]
 # Generate approximate floor samples from upward-facing/near-horizontal render surfaces only.
 floor=np.full((SIZE,SIZE),32767,dtype=np.int16);best=np.full((SIZE,SIZE),1e9);X,Z=np.meshgrid(np.arange(SIZE)*STEP-R,np.arange(SIZE)*STEP-R)
 for t,n0,mat in zip(tri,n,m):
  name=names.get(mat,'').lower()
  if abs(n0[1])<.78 or any(q in name for q in ['tree','ivy']):continue
  a,bb,cc=t;d=(bb[0]-a[0])*(cc[2]-a[2])-(bb[2]-a[2])*(cc[0]-a[0]);
  if abs(d)<1e-5:continue
  u=((X-a[0])*(cc[2]-a[2])-(Z-a[2])*(cc[0]-a[0]))/d;w=((bb[0]-a[0])*(Z-a[2])-(bb[2]-a[2])*(X-a[0]))/d;y=a[1]+u*(bb[1]-a[1])+w*(cc[1]-a[1]);score=abs(y+650)
  mask=(u>=-1e-6)&(w>=-1e-6)&(u+w<=1.000001)&(y>-1700)&(y<800)&(score<best);floor[mask]=-np.rint(y[mask]).astype(np.int16);best[mask]=score[mask]
 # Find a spawn in a connected patch with gentle floor within 3 cells.
 good=floor!=32767; candidates=[]
 for iz in range(4,SIZE-4):
  for ix in range(4,SIZE-4):
   q=floor[iz-1:iz+2,ix-1:ix+2];
   if np.all(q!=32767) and np.ptp(q.astype(int))<180:candidates.append(((ix-SIZE//2)**2+(iz-SIZE//2)**2,ix,iz))
 print("valid floor",good.sum(),"spawn candidates",len(candidates));
 if not candidates:raise ValueError('no safe spawn')
 _,ix,iz=min(candidates);spawn=[ix*STEP-R,int(floor[iz,ix]),iz*STEP-R];
 # Deduplicate fixed-point geometry, discard collapsed/duplicate triangles.
 v=np.rint(v).astype(int);v[:,1]*=-1;vv,idx=np.unique(v[f].reshape(-1,3),axis=0,return_inverse=True);ff=idx.reshape(-1,3);k=np.all(np.diff(np.sort(ff,axis=1),axis=1)!=0,axis=1);ff=ff[k];m=m[k];n=n[k];_,u=np.unique(np.sort(ff,axis=1),axis=0,return_index=True);u=np.sort(u);ff=ff[u];m=m[u];n=n[u]
 def color(name):
  name=name.lower()
  for term,col in [('wheat',(174,154,80)),('hay',(193,171,89)),('water',(58,117,167)),('tree',(81,127,68)),('ivy',(82,125,61)),('grass',(102,145,75)),('wood',(126,94,59)),('ground',(140,119,73)),('lightb',(167,140,98))]:
   if term in name:return col
  return (132,124,105)
 colors=[]
 for mat,nn in zip(m,n):
  # Illustrative material-name colors, not source texture mapping.
  shade=.62+.38*abs(float(nn[1]));colors.append(np.rint(np.array(color(names.get(mat,'')))*shade).astype(int))
 colors=np.array(colors);actor=(ROOT/'build_m04/lod/scene.h').read_text();(out/'scene.h').write_text(actor)
 sins=np.rint(np.sin(np.arange(64)*2*np.pi/64)*4096).astype(int)
 hdr=f'#define WV {len(vv)}\n#define WF {len(ff)}\n#define GRID {SIZE}\n#define GRID_STEP {STEP}\n#define GRID_RADIUS {R}\n#define SPAWN_X {spawn[0]}\n#define SPAWN_Y {spawn[1]}\n#define SPAWN_Z {spawn[2]}\n'
 hdr+='static const s16 world[WV][3]={\n'+','.join('{'+','.join(str(int(x)) for x in row)+'}' for row in vv)+'};\nstatic const u16 worldfaces[WF][3]={\n'+arr(ff)+'};\nstatic const u32 worldcolor[WF]={'+','.join(str(int(r)|(int(g)<<8)|(int(b)<<16))+'u' for r,g,b in colors)+'};\nstatic const s16 floorgrid[GRID*GRID]={'+','.join(str(int(x)) for x in floor.ravel())+'};\nstatic const s16 sine[64]={'+','.join(str(int(x)) for x in sins)+'};\n'
 (out/'world.h').write_text(hdr);np.savez(out/'farm.npz',vertices=vv,faces=ff,colors=colors,floor=floor,spawn=spawn)
 report=dict(world_vertices=len(vv),world_faces=len(ff),floor_cells_valid=int(good.sum()),floor_cells_total=SIZE*SIZE,spawn_local=spawn,source_origin=CENTER.tolist(),world_materials=len(set(m.tolist())),world_textures='flat debug colors selected from original material names, not texture binding')
 (out/'farm_report.json').write_text(json.dumps(report,indent=2));print(report)
 return report

def build(iso,out):
 out=out.resolve();out.mkdir(parents=True,exist_ok=True);rep=prepare(iso,out);opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0']
 def run(args):subprocess.run(args,cwd=out,check=True)
 run(opts+['-c',str(ROOT/'src/dynamic_start.s'),'-o','start.o']);run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(out),'-c',str(ROOT/'src/play.c'),'-o','play.o']);run(['ld.lld','-m','elf32ltsmip','-T',str(ROOT/'src/dynamic.ld'),'start.o','play.o','-o','play.elf']);run(['llvm-objcopy','-O','binary','play.elf','play.bin']);data=(out/'play.bin').read_bytes();data+=bytes((-len(data))%2048);header=bytearray(2048);header[:8]=b'PS-X EXE';struct.pack_into('<IIII',header,16,0x80010000,0,0x80010000,len(data));struct.pack_into('<II',header,0x30,0x801fff00,0);(out/'ETD_PLAY.EXE').write_bytes(header+data);rep['exe_bytes']=len(data)+2048;rep['native_runtime']='compiled; no emulator or console execution';(out/'farm_report.json').write_text(json.dumps(rep,indent=2));print(rep)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('iso',type=Path);p.add_argument('out',type=Path);a=p.parse_args();build(a.iso,a.out)
