"""Integrate source-textured indexed Ninja Riptoc and baked animation poses into v0.29."""
from pathlib import Path
import json,struct,shutil,subprocess
from disc16 import iso,raw,record
R=Path(__file__).resolve().parents[1];O=R/'build_m30/play';OLD=R/'build_m29/play';A=R/'assets_m30'
def build():
 O.mkdir(parents=True,exist_ok=True)
 for p in OLD.iterdir():
  if p.suffix in ('.h','.c','.DAT','.IDX','.json'):shutil.copyfile(p,O/p.name)
 shutil.copyfile(A/'ninja30.h',O/'ninja30.h')
 s=(OLD/'play29.c').read_text().replace('#include "ninjamesh29.h"','#include "ninja30.h"\n#define NINJA_ID30 0x7ffdu')
 s=s.replace('static void refresh19(void)', '''static void ninja_upload30(void){for(int i=0;i<2;i++){uploadrect19(768,8+i,256,1,(const U8*)ninja_pal30[i]);uploadrect19(832+i*32,320,32,64,ninja_pix30[i]);}gp(0x01000000);idle();}
static void refresh19(void)''')
 a=s.index('for(int f=0;f<NFACE20(ninja29mesh);f++)');b=s.index('\n }}}',a)
 s=s[:a]+'''int near=ab(dx)<420&&ab(dz)<420;int phase=near?13+(collect.tick%40)*6/40:1+(collect.tick%80)*12/80;static Point np[NINJA_NV30];int scale=enemylarge29[id]?5:4;
 int ep=ninja_offsets30[phase-1];for(int l=0;l<NINJA_NV30;l++){int w[3];for(int j=0;j<3;j++){int d=ninja_delta30[phase-1][l][j];if(d==-128)d=ninja_escape30[ep++];w[j]=ninja_base30[l][j]+d;}int xx=w[0]*scale/4,yy=w[1]*scale/4,zz=w[2]*scale/4;np[l]=transform(x+((b*xx+a*zz)>>12),y+yy,z+((b*zz-a*xx)>>12),cx,cy,cz,sn,cs);}
 for(int f=0;f<NINJA_NF30;f++){Point v[3];for(int l=0;l<3;l++){v[l]=np[ninja_faces30[f][l]];v[l].u=ninja_uv30[f][2*l];v[l].v=ninja_uv30[f][2*l+1];}worldtri(v[0],v[1],v[2],NINJA_ID30+ninja_mat30[f]);}'''+s[b:]
 s=s.replace('}else if(id&0x8000){','''}else if(id==NINJA_ID30||id==NINJA_ID30+1){int m=id-NINJA_ID30;gp(0xe2000000u|24|(24<<5)|(m*8<<10)|(8<<15));gp(0x24808080);gp(packetxy(q,0));gp(q->uv[0]|((48|((8+m)<<6))<<16));gp(packetxy(q,1));gp(q->uv[1]|((13|16|128)<<16));gp(packetxy(q,2));gp(q->uv[2]);}else if(id&0x8000){''')
 s=s.replace('sky_upload28();status=', 'sky_upload28();ninja_upload30();status=')
 (O/'play30.c').write_text(s)
 opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0'];run=lambda a:subprocess.run(a,cwd=O,check=True)
 run(opts+['-c',str(R/'src/dynamic13_start.s'),'-o','start.o'])
 for p in [O/'play30.c',R/'src/cd17.c',R/'src/sector27.c',R/'src/resident17.c']:run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(O),'-I',str(R/'src'),'-c',str(p),'-o',p.stem+'.o'])
 run(['ld.lld','-m','elf32ltsmip','-T',str(R/'src/dynamic13.ld'),'start.o','play30.o','cd17.o','sector27.o','resident17.o','-o','play30.elf']);run(['llvm-objcopy','-O','binary','play30.elf','play30.bin']);d=(O/'play30.bin').read_bytes();d+=bytes((-len(d))%2048);h=bytearray(2048);h[:8]=b'PS-X EXE';struct.pack_into('<IIII',h,16,0x80010000,0,0x80010000,len(d));struct.pack_into('<II',h,0x30,0x801fff00,0);e=h+d;(O/'ETD_EYES.EXE').write_bytes(e)
 elf=(O/'play30.elf').read_bytes();off=struct.unpack_from('<I',elf,28)[0];sz,n=struct.unpack_from('<HH',elf,42);high=max(p[2]+p[5] for i in range(n) if (p:=struct.unpack_from('<8I',elf,off+i*sz))[0]==1);rep=dict(exe_bytes=len(e),linked_ram_from_load=high-0x80010000,headroom_to_stack_region=0x801e0000-high,mode='Native compilation; source-textured sampled idle and ready, stationary combat unchanged');assert high<0x801e0000;(O/'report30.json').write_text(json.dumps(rep,indent=2));print(rep,flush=True)
 assets={n:(R/'assets_m16'/n).read_bytes() for n in ('HUBSECT.DAT','HUBSECT.IDX')};assets.update({n:(R/'assets_m20'/n).read_bytes() for n in ('HUBTEX.DAT','HUBTEX.IDX')});assets.update({n:(O/n).read_bytes() for n in ('DOJOSECT.DAT','DOJOSECT.IDX')});assets.update({n:(R/'assets_m27'/n).read_bytes() for n in ('DOJOTEX.DAT','DOJOTEX.IDX')});assets['ETD_POOL.EXE']=(R/'build_m24/play/ETD_POOL.EXE').read_bytes();assets['ETD_NINJ.EXE']=(OLD/'ETD_NINJ.EXE').read_bytes();s=iso(e,assets);root=bytearray();pos=0
 while s[20][pos]:
  n=s[20][pos];rr=s[20][pos:pos+n];name=bytes(rr[33:33+rr[32]])
  if name==b'ETD_SECT.EXE;1':rr=record(b'ETD_EYES.EXE;1',22,len(e))
  if name==b'SYSTEM.CNF;1':
   config=b'BOOT = cdrom:\\ETD_EYES.EXE;1\r\nTCB = 4\r\nEVENT = 10\r\nSTACK = 801FFF00\r\n';s[21][:]=config.ljust(2048,b'\0');rr=record(name,21,len(config))
  root.extend(rr);pos+=n
 s[20][:]=root.ljust(2048,b'\0');(O/'ETD_PSX_M30.bin').write_bytes(b''.join(raw(i,x) for i,x in enumerate(s)));(O/'ETD_PSX_M30.cue').write_text('FILE "ETD_PSX_M30.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
if __name__=='__main__':build()
