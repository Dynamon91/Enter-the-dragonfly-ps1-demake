"""Generate a real native GTE test with a source-disc collision mesh, not game visuals."""
import argparse, math, struct, subprocess, json, shutil
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from recover import records,collision_mesh
ROOT=Path(__file__).resolve().parents[1]
def pack(a,b):return (int(a)&65535)|((int(b)&65535)<<16)
def generate(iso,out):
    v,f=collision_mesh(records(iso)[44][1]);v=v.astype(float);v-= (v.min(0)+v.max(0))/2;v[:,1]*=-1;v=np.rint(v*(260/np.max(np.ptp(v,axis=0)))).astype(int)
    matrices=[];rot=[]
    pitch=math.radians(18);rx=np.array([[1,0,0],[0,math.cos(pitch),-math.sin(pitch)],[0,math.sin(pitch),math.cos(pitch)]])
    for k in range(64):
        a=2*math.pi*k/64; ry=np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]]); m=np.rint((rx@ry)*4096).astype(int).ravel();rot.append(m.reshape(3,3));matrices.append([pack(m[0],m[1]),pack(m[2],m[3]),pack(m[4],m[5]),pack(m[6],m[7]),pack(m[8],0),0,0,400,260,160<<16,120<<16])
    norm=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]);ln=np.linalg.norm(norm,axis=1); light=np.array([-.4,-.8,-.4]); shade=.38+.62*np.abs(norm@light)/np.maximum(ln,1);shade=np.clip(shade,0,1); rgb=(shade[:,None]*[221,159,77]).astype(int);colors=[int(r)|(int(g)<<8)|(int(b)<<16) for r,g,b in rgb]
    def arr(rows):return ',\n'.join('{'+','.join(str(int(x))+'u' for x in row)+'}' for row in rows)
    (out/'scene.h').write_text(f'#define NV {len(v)}\n#define NF {len(f)}\nstatic const u32 vertices[NV][2]={{\n'+arr([[pack(x,y),z&0xffffffff] for x,y,z in v])+'};\nstatic const u16 faces[NF][3]={\n'+arr(f)+'};\nstatic const u32 matrices[64][11]={\n'+arr(matrices)+'};\nstatic const u32 colors[NF]={'+','.join(str(c)+'u' for c in colors)+'};\n')
    # Render the same transformed triangles and ordering buckets as the native test (host approximation).
    shots=[]; minz=10000;maxz=0; maxpolys=0
    for k,m in enumerate(rot):
        p=(v@m.T)//4096+np.array([0,0,400]);z=p[:,2];minz=min(minz,int(z.min()));maxz=max(maxz,int(z.max())); xy=np.floor(p[:,:2]*260/z[:,None]+[160,120]).astype(int);depth=z[f].sum(axis=1)//12;order=sorted(range(len(f)),key=lambda j:(depth[j],j),reverse=True);maxpolys=max(maxpolys,len(order));im=Image.new('RGB',(320,240),(32,24,29));d=ImageDraw.Draw(im)
        for j in order:d.polygon([tuple(xy[i]) for i in f[j]],fill=tuple((rgb[j]//8)*8))
        if k in (5,16,32,48):shots.append(im)
    sheet=Image.new('RGB',(640,480));
    for i,im in enumerate(shots):sheet.paste(im,((i%2)*320,(i//2)*240))
    sheet.save(out/'dynamic_preview.png');return {'vertices':len(v),'triangles':len(f),'frames_host_checked':64,'depth_min':minz,'depth_max':maxz,'max_triangles':maxpolys,'framebuffer_bytes':320*240*2*2,'preview':'Host approximation, no emulator execution'}
def build(iso,out):
    out=out.resolve();out.mkdir(parents=True,exist_ok=True);rep=generate(iso,out)
    opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0']
    def run(args):subprocess.run(args,cwd=out,check=True)
    run(opts+['-c',str(ROOT/'src/dynamic_start.s'),'-o','start.o']);run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(out),'-c',str(ROOT/'src/dynamic.c'),'-o','dynamic.o']);run(['ld.lld','-m','elf32ltsmip','-T',str(ROOT/'src/dynamic.ld'),'start.o','dynamic.o','-o','dynamic.elf']);run(['llvm-objcopy','-O','binary','dynamic.elf','dynamic.bin']);data=(out/'dynamic.bin').read_bytes();data+=bytes((-len(data))%2048);header=bytearray(2048);header[:8]=b'PS-X EXE';struct.pack_into('<IIII',header,16,0x80010000,0,0x80010000,len(data));struct.pack_into('<II',header,0x30,0x801fff00,0);(out/'ETD_GTE.EXE').write_bytes(header+data);rep['exe_bytes']=len(data)+2048;rep['native_runtime']='compiled only; no emulator or hardware execution';(out/'dynamic_report.json').write_text(json.dumps(rep,indent=2));print(rep)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('iso',type=Path);p.add_argument('out',type=Path);a=p.parse_args();build(a.iso,a.out)
