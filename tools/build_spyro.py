"""Native textured GTE model viewer from recovered source geometry; no emulator claims."""
import argparse,math,json,struct,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from recover import records,pxt_groups
from spyro_mesh import export
ROOT=Path(__file__).resolve().parents[1]
IDS=[303,411,429]
TEX_X=[320,448,512]
def pack(a,b):return (int(a)&65535)|((int(b)&65535)<<16)
def arr(rows):return ',\n'.join('{'+','.join(str(int(x))+'u' for x in row)+'}' for row in rows)
def words(data):return np.frombuffer(data,dtype='<u4')
def build_scene(iso,out,lod=False):
 mesh=out.parent/'spyro';export(iso,mesh);z=np.load(mesh/'spyro_rest.npz');v=z['vertices'].astype(float);f=z['faces'];uv=z['uv'];mat=z['material'];n=z['normals'];
 v-= (v.min(0)+v.max(0))/2;v[:,1]*=-1;v=np.rint(v*(250/np.max(np.ptp(v,axis=0)))).astype(int)
 # Optional adaptive voxel LOD: preserve facial detail and separate model components.
 if lod:
  part=z["part"];names=z["part_names"];steps=np.array([10 if name=="body_objShape" else 7 if name in ("wing_objShape","finShape","tail_tipShape") else 5 if "face" in name or "horn" in name else 4 for name in names]);step=steps[part];body=part==list(names).index("body_objShape");step=np.where(body & ((v[:,2]<-35)|(v[:,1]>48)),4,step);key=np.column_stack([part,step,np.rint(v/step[:,None]).astype(int)]);_,idx=np.unique(key,axis=0,return_inverse=True);vv=np.zeros((idx.max()+1,3));np.add.at(vv,idx,v);vv=np.rint(vv/np.bincount(idx)[:,None]).astype(int)
 else:vv,idx=np.unique(v,axis=0,return_inverse=True);
 ff=idx[f];keep=np.all(np.diff(np.sort(ff,axis=1),axis=1)!=0,axis=1);f=f[keep];ff=ff[keep];mat=mat[keep];n=n[f].mean(1)
 _,unique=np.unique(np.sort(ff,axis=1),axis=0,return_index=True);unique=np.sort(unique);f=f[unique];ff=ff[unique];mat=mat[unique];n=n[unique]
 groups=list(pxt_groups(records(iso)[772][1]));tex=[];upload=[];uvs=[];tpages=[];cluts=[]
 for k,i in enumerate(IDS):
  _,pal,imgs=groups[i];w,h,ix=imgs[0];assert len(pal)==256; rgb=pal.astype(np.uint16);colors=(rgb[:,0]>>3)|((rgb[:,1]>>3)<<5)|((rgb[:,2]>>3)<<10);colors=np.maximum(colors,1).astype('<u2');tex.append(((pal[ix][:,:,:3]//8)*8).astype(np.uint8));x=TEX_X[k];assert x%64==0 and x+w//2<=768 and h<=256
  upload.extend([0xa0000000,768|(k<<16),(1<<16)|256]);upload.extend(words(colors.tobytes()).tolist());upload.extend([0xa0000000,x,(h<<16)|(w//2)]);upload.extend(words(ix.tobytes()).tolist());tpages.append((x//64)|0x80);cluts.append((768//16)|(k<<6))
 uvbytes=[];texid=[]
 for face,m in zip(f,mat):
  k=IDS.index(m);texid.append(k);h,w,_=tex[k].shape;uvbytes.append(np.clip(np.rint(uv[face]*[w-1,h-1]),0,[w-1,h-1]).astype(np.uint8))
 uvbytes=np.asarray(uvbytes);texid=np.asarray(texid);matrices=[];rot=[]
 pitch=math.radians(12);rx=np.array([[1,0,0],[0,math.cos(pitch),-math.sin(pitch)],[0,math.sin(pitch),math.cos(pitch)]])
 for k in range(64):
  a=2*math.pi*k/64;ry=np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]]);m=np.rint((rx@ry)*4096).astype(int).ravel();rot.append(m.reshape(3,3));matrices.append([pack(m[0],m[1]),pack(m[2],m[3]),pack(m[4],m[5]),pack(m[6],m[7]),pack(m[8],0),0,0,395,255,160<<16,120<<16])
 # Texture modulation kept neutral. Use original source texture (with quantization).
 packetuv=[]
 for a,k in zip(uvbytes,texid):
  p=[int(x)|(int(y)<<8) for x,y in a];packetuv.append([p[0]|(cluts[k]<<16),p[1]|(tpages[k]<<16),p[2]])
 (out/'scene.h').write_text(f'#define NV {len(vv)}\n#define NF {len(ff)}\n#define UPLOAD_WORDS {len(upload)}\nstatic const u32 vertices[NV][2]={{\n'+arr([[pack(x,y),zz&0xffffffff] for x,y,zz in vv])+'};\nstatic const u16 faces[NF][3]={\n'+arr(ff)+'};\nstatic const u32 matrices[64][11]={\n'+arr(matrices)+'};\nstatic const u32 uvwords[NF][3]={\n'+arr(packetuv)+'};\nstatic const u32 upload[UPLOAD_WORDS]={'+','.join(str(c)+'u' for c in upload)+'};\n')
 # Host approximates native painter's algorithm and affine texture sampling (no zbuffer).
 shots=[];mind=10000;maxd=0
 for frame,m in enumerate(rot):
  p=(vv@m.T)//4096+[0,0,395];d=p[:,2];mind=min(mind,int(d.min()));maxd=max(maxd,int(d.max()));xy=np.floor(p[:,:2]*255/d[:,None]+[160,120]).astype(int)
  if frame not in [5,16,27,48]:continue
  im=np.zeros((240,320,3),dtype=np.uint8);im[:]=[24,32,48];depth=d[ff].sum(1)//3
  for j in sorted(range(len(ff)),key=lambda j:(depth[j],j),reverse=True):
   a,b,c=xy[ff[j]];x0=max(0,min(a[0],b[0],c[0]));x1=min(319,max(a[0],b[0],c[0]));y0=max(0,min(a[1],b[1],c[1]));y1=min(239,max(a[1],b[1],c[1]));det=(b[0]-a[0])*(c[1]-a[1])-(c[0]-a[0])*(b[1]-a[1]);
   if det==0 or x1<x0 or y1<y0:continue
   yy,xx=np.mgrid[y0:y1+1,x0:x1+1];w1=((xx-a[0])*(c[1]-a[1])-(yy-a[1])*(c[0]-a[0]))/det;w2=((b[0]-a[0])*(yy-a[1])-(b[1]-a[1])*(xx-a[0]))/det;w0=1-w1-w2;mask=(w0>=-1e-6)&(w1>=-1e-6)&(w2>=-1e-6)
   tuv=uvbytes[j].astype(float);st=w0[...,None]*tuv[0]+w1[...,None]*tuv[1]+w2[...,None]*tuv[2];t=tex[texid[j]];iy=np.clip(st[...,1].astype(int),0,t.shape[0]-1);ix=np.clip(st[...,0].astype(int),0,t.shape[1]-1);im[y0:y1+1,x0:x1+1][mask]=t[iy[mask],ix[mask]]
  shots.append(Image.fromarray(im))
 sheet=Image.new('RGB',(640,480));
 for i,im in enumerate(shots):sheet.paste(im,((i%2)*320,(i//2)*240))
 sheet.save(out/'spyro_preview.png');return {'lod':lod,'vertices':len(vv),'triangles':len(ff),'upload_words':len(upload),'texture_vram_bytes':sum(x.shape[0]*x.shape[1]+512 for x in tex),'depth_min':mind,'depth_max':maxd,'frames_host_checked':64,'preview':'Host approximation of affine GPU packets; not emulator screenshot','limitations':'Static inferred rest pose, provisional textures, no gameplay/rig; no measured performance.'}
def build(iso,out,lod=False):
 out=out.resolve();out.mkdir(parents=True,exist_ok=True);rep=build_scene(iso,out,lod);opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0']
 def run(args):subprocess.run(args,cwd=out,check=True)
 run(opts+['-c',str(ROOT/'src/dynamic_start.s'),'-o','start.o']);run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(out),'-c',str(ROOT/'src/spyro_view.c'),'-o','view.o']);run(['ld.lld','-m','elf32ltsmip','-T',str(ROOT/'src/dynamic.ld'),'start.o','view.o','-o','view.elf']);run(['llvm-objcopy','-O','binary','view.elf','view.bin']);data=(out/'view.bin').read_bytes();data+=bytes((-len(data))%2048);header=bytearray(2048);header[:8]=b'PS-X EXE';struct.pack_into('<IIII',header,16,0x80010000,0,0x80010000,len(data));struct.pack_into('<II',header,0x30,0x801fff00,0);(out/('ETD_LOD.EXE' if lod else 'ETD_SPYRO.EXE')).write_bytes(header+data);rep['exe_bytes']=len(data)+2048;rep['native_runtime']='compiled, not executed in emulator/hardware';(out/'view_report.json').write_text(json.dumps(rep,indent=2));print(rep)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('iso',type=Path);p.add_argument('out',type=Path);p.add_argument('--lod',action='store_true');a=p.parse_args();build(a.iso,a.out,a.lod)
