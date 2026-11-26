"""Integrate source-textured indexed Ninja Riptoc and baked animation poses into v0.29."""
from pathlib import Path
import json,struct,shutil,subprocess
from disc16 import iso,raw,record
R=Path(__file__).resolve().parents[1];O=R/'build_m31/play';OLD=R/'build_m30/play';A=R/'assets_m31'
def build():
 O.mkdir(parents=True,exist_ok=True)
 for p in OLD.iterdir():
  if p.suffix in ('.h','.c','.DAT','.IDX','.json'):shutil.copyfile(p,O/p.name)
 shutil.copyfile(A/'ninja30.h',O/'ninja30.h')
 s=(OLD/'play30.c').read_text().replace('#include "enemy29.h"','#include "enemy31.h"').replace('enemy_reset29()','enemy_reset31()').replace('enemy_step29(&interactions,&cache,p.x,p.y,p.z,ox,oz,btn&PAD_SQUARE,p.grounded)','enemy_step31(&interactions,&cache,p.x,p.y,p.z,ox,oz,btn&PAD_SQUARE,p.grounded,sine)')
 a=s.index('if(id<0||enemy_dead29[id])');b=s.index('static Point np[NINJA_NV30]',a)
 s=s[:a]+'if(id<0)continue;Ninja31*n=ninjas31+id;if(n->mode==N_GONE31)continue;int x=n->initialized?n->x:s18(t)+(int)m[4],y=n->initialized?n->y:s18(t+2)+(int)m[5],z=n->initialized?n->z:s18(t+4)+(int)m[6];if(ab(x-p->x)>1400||ab(z-p->z)>1400)continue;y-=lift31(n);int a=sine[n->heading],b=sine[(n->heading+16)&63];int phase=phase31(n,collect.tick);'+s[b:]
 (O/'play31.c').write_text(s)
 opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0'];run=lambda a:subprocess.run(a,cwd=O,check=True)
 run(opts+['-c',str(R/'src/dynamic13_start.s'),'-o','start.o'])
 for p in [O/'play31.c',R/'src/cd17.c',R/'src/sector27.c',R/'src/resident17.c']:run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(O),'-I',str(R/'src'),'-c',str(p),'-o',p.stem+'.o'])
 run(['ld.lld','-m','elf32ltsmip','-T',str(R/'src/dynamic13.ld'),'start.o','play31.o','cd17.o','sector27.o','resident17.o','-o','play31.elf']);run(['llvm-objcopy','-O','binary','play31.elf','play31.bin']);d=(O/'play31.bin').read_bytes();d+=bytes((-len(d))%2048);h=bytearray(2048);h[:8]=b'PS-X EXE';struct.pack_into('<IIII',h,16,0x80010000,0,0x80010000,len(d));struct.pack_into('<II',h,0x30,0x801fff00,0);e=h+d;(O/'ETD_AI.EXE').write_bytes(e)
 elf=(O/'play31.elf').read_bytes();off=struct.unpack_from('<I',elf,28)[0];sz,n=struct.unpack_from('<HH',elf,42);high=max(p[2]+p[5] for i in range(n) if (p:=struct.unpack_from('<8I',elf,off+i*sz))[0]==1);rep=dict(exe_bytes=len(e),linked_ram_from_load=high-0x80010000,headroom_to_stack_region=0x801e0000-high,mode='Native compilation; source-textured idle, ready, jump and defeat; reconstructed AI');assert high<0x801e0000;(O/'report31.json').write_text(json.dumps(rep,indent=2));print(rep,flush=True)
 assets={n:(R/'assets_m16'/n).read_bytes() for n in ('HUBSECT.DAT','HUBSECT.IDX')};assets.update({n:(R/'assets_m20'/n).read_bytes() for n in ('HUBTEX.DAT','HUBTEX.IDX')});assets.update({n:(O/n).read_bytes() for n in ('DOJOSECT.DAT','DOJOSECT.IDX')});assets.update({n:(R/'assets_m27'/n).read_bytes() for n in ('DOJOTEX.DAT','DOJOTEX.IDX')});assets['ETD_POOL.EXE']=(R/'build_m24/play/ETD_POOL.EXE').read_bytes();assets['ETD_EYES.EXE']=(OLD/'ETD_EYES.EXE').read_bytes();s=iso(e,assets);root=bytearray();pos=0
 while s[20][pos]:
  n=s[20][pos];rr=s[20][pos:pos+n];name=bytes(rr[33:33+rr[32]])
  if name==b'ETD_SECT.EXE;1':rr=record(b'ETD_AI.EXE;1',22,len(e))
  if name==b'SYSTEM.CNF;1':
   config=b'BOOT = cdrom:\\ETD_AI.EXE;1\r\nTCB = 4\r\nEVENT = 10\r\nSTACK = 801FFF00\r\n';s[21][:]=config.ljust(2048,b'\0');rr=record(name,21,len(config))
  root.extend(rr);pos+=n
 s[20][:]=root.ljust(2048,b'\0');(O/'ETD_PSX_M31.bin').write_bytes(b''.join(raw(i,x) for i,x in enumerate(s)));(O/'ETD_PSX_M31.cue').write_text('FILE "ETD_PSX_M31.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
if __name__=='__main__':build()
