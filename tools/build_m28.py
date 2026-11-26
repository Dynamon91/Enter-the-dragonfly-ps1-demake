"""Build native sky-enabled Dojo executable from v0.27 assets and original extracted sky."""
from pathlib import Path
import numpy as np,json,struct,subprocess,shutil
from disc16 import iso,raw,record
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build_m28/play';OLD=ROOT/'build_m27/play';A=ROOT/'assets_m28'
def build():
 OUT.mkdir(parents=True,exist_ok=True)
 for n in ('scene.h','rig11_data.h','collectdata12.h','sfx14.h','firetex11.h','basketmesh21.h','foddermesh21.h','gemids20.h','objectids21.h','colors17.h','groups19.h','cache24.c','collect21.h','interact21.h','tex19.h','DOJOSECT.DAT','DOJOSECT.IDX','route.json'):shutil.copyfile(OLD/n,OUT/n)
 z=np.load(A/'sky.npz');tri=z['triangles'];layers=z['layers'];pal=z['palettes'];pix=z['pixels'];arr=lambda a:','.join(map(str,a.reshape(-1).tolist()));lines=['#define SKY_N28 '+str(len(tri)), 'typedef struct {s16 v[3][5];u16 layer;} SkyTri28;', 'static const SkyTri28 sky_triangles28[SKY_N28]={']
 for v,l in zip(tri,layers):lines.append('{{'+','.join('{'+arr(x)+'}' for x in v)+'},'+str(l)+'},')
 lines+=['};','static const u16 sky_pal28[4][256]={'+','.join('{'+arr(x)+'}' for x in pal)+'};','static const U8 sky_pix28[4][4096]={'+','.join('{'+arr(x)+'}' for x in pix)+'};'];(OUT/'skydata28.h').write_text('\n'.join(lines)+'\n')
 s=(OLD/'play24.c').read_text();s=s.replace('static void refresh19(void)', '#include "sky28.h"\nstatic void refresh19(void)');assert s.count('sky28.h')==1
 # Clear to a source-derived lower dome color, then draw sky before world packets.
 c=int(pal[0,pix[0,-1,32]])&0x7fff;rgb=(c&31)<<3|((c>>5)&31)<<11|((c>>10)&31)<<19
 s=s.replace('gp(0x02997154);gp(y<<16);gp((240<<16)|320);for(int b=',f'gp(0x02000000|{rgb}u);gp(y<<16);gp((240<<16)|320);sky_draw28(sn,cs);for(int b=')
 assert 'sky_draw28(sn,cs)' in s
 s=s.replace('gp(fireupload[i]);idle();status=', 'gp(fireupload[i]);idle();sky_upload28();status=');assert 'sky_upload28();status' in s
 (OUT/'play28.c').write_text(s)
 opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0'];run=lambda a:subprocess.run(a,cwd=OUT,check=True)
 run(opts+['-c',str(ROOT/'src/dynamic13_start.s'),'-o','start.o'])
 for p in [OUT/'play28.c',ROOT/'src/cd17.c',ROOT/'src/sector27.c',ROOT/'src/resident17.c']:run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(OUT),'-I',str(ROOT/'src'),'-c',str(p),'-o',p.stem+'.o'])
 run(['ld.lld','-m','elf32ltsmip','-T',str(ROOT/'src/dynamic13.ld'),'start.o','play28.o','cd17.o','sector27.o','resident17.o','-o','play28.elf']);run(['llvm-objcopy','-O','binary','play28.elf','play28.bin']);d=(OUT/'play28.bin').read_bytes();d+=bytes((-len(d))%2048);h=bytearray(2048);h[:8]=b'PS-X EXE';struct.pack_into('<IIII',h,16,0x80010000,0,0x80010000,len(d));struct.pack_into('<II',h,0x30,0x801fff00,0);e=h+d;(OUT/'ETD_SKY.EXE').write_bytes(e)
 elf=(OUT/'play28.elf').read_bytes();off=struct.unpack_from('<I',elf,28)[0];sz,n=struct.unpack_from('<HH',elf,42);high=max(p[2]+p[5] for i in range(n) if (p:=struct.unpack_from('<8I',elf,off+i*sz))[0]==1);rep=dict(exe_bytes=len(e),linked_ram_from_load=high-0x80010000,headroom_to_stack_region=0x801e0000-high,sky_triangles=len(tri),sky_vram_bytes=4*4608,sky_clear_rgb=rgb,mode='Dojo native sky pass; compilation only');assert high<0x801e0000;(OUT/'report.json').write_text(json.dumps(rep,indent=2));print(rep,flush=True)
 assets={n:(ROOT/'assets_m16'/n).read_bytes() for n in ('HUBSECT.DAT','HUBSECT.IDX')};assets.update({n:(ROOT/'assets_m20'/n).read_bytes() for n in ('HUBTEX.DAT','HUBTEX.IDX')});assets.update({n:(OUT/n).read_bytes() for n in ('DOJOSECT.DAT','DOJOSECT.IDX')});assets.update({n:(ROOT/'assets_m27'/n).read_bytes() for n in ('DOJOTEX.DAT','DOJOTEX.IDX')});assets['ETD_POOL.EXE']=(ROOT/'build_m24/play/ETD_POOL.EXE').read_bytes();assets['ETD_WIDE.EXE']=(OLD/'ETD_WIDE.EXE').read_bytes();s=iso(e,assets);root=bytearray();pos=0
 while s[20][pos]:
  n=s[20][pos];rr=s[20][pos:pos+n];name=bytes(rr[33:33+rr[32]])
  if name==b'ETD_SECT.EXE;1':rr=record(b'ETD_SKY.EXE;1',22,len(e))
  if name==b'SYSTEM.CNF;1':
   config=b'BOOT = cdrom:\\ETD_SKY.EXE;1\r\nTCB = 4\r\nEVENT = 10\r\nSTACK = 801FFF00\r\n';s[21][:]=config.ljust(2048,b'\0');rr=record(name,21,len(config))
  root.extend(rr);pos+=n
 s[20][:]=root.ljust(2048,b'\0');(OUT/'ETD_PSX_M28.bin').write_bytes(b''.join(raw(i,x) for i,x in enumerate(s)));(OUT/'ETD_PSX_M28.cue').write_text('FILE "ETD_PSX_M28.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
if __name__=='__main__':build()
