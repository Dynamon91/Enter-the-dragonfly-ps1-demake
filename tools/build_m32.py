"""Build v0.32 with initialization-only assets on disc."""
from pathlib import Path
import json,struct,shutil,subprocess
from disc16 import iso,raw,record
from bootbank32 import generate
R=Path(__file__).resolve().parents[1];O=R/'build_m32/play';OLD=R/'build_m31/play'
def build():
 O.mkdir(parents=True,exist_ok=True)
 for p in OLD.iterdir():
  if p.suffix in ('.h','.c','.DAT','.IDX','.json'):shutil.copyfile(p,O/p.name)
 boot=generate(OLD,O)
 s=(OLD/'play31.c').read_text().replace('#include "scene.h"','static const unsigned char *startup32;\n#include "scene.h"').replace('#include "cache24.c"','#include "cache24.c"\n#include "startup32.h"')
 s=s.replace('static U32 ext[2],data[2];','static U32 ext[2],data[2],bootextent32[2];')
 s=s.replace('ext[1]!=26776||data[1]%2048','ext[1]!=26776||data[1]%2048||!iso17_find(scratch,"BOOT32.DAT;1",pvd[0],bootextent32)||bootextent32[1]!=BOOT_BYTES32')
 s=s.replace('for(int i=0;i<UPLOAD_WORDS;i++)gp(upload[i]);','if(!mount18()||!bootload32((U8*)cache.arena,sizeof(cache.arena),bootextent32[0],bootextent32[1],cd17_read,0)){gp(0x020000b0);gp(0);gp((240<<16)|320);idle();GP1=0x05000000;GP1=0x03000000;for(;;)vb();}startup32=(const U8*)cache.arena;for(int i=0;i<UPLOAD_WORDS;i++)gp(boot_upload32[i]);')
 s=s.replace('status=mount18()&&reset18(&p);','sfx_init();startup32=0;status=reset18(&p);').replace('enemy_reset31();sfx_init();int y=0;','enemy_reset31();int y=0;')
 (O/'play32.c').write_text(s)
 opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0'];run=lambda a:subprocess.run(a,cwd=O,check=True)
 run(opts+['-c',str(R/'src/dynamic13_start.s'),'-o','start.o'])
 for p in [O/'play32.c',R/'src/cd17.c',R/'src/sector27.c',R/'src/resident17.c']:run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(O),'-I',str(R/'src'),'-c',str(p),'-o',p.stem+'.o'])
 run(['ld.lld','-m','elf32ltsmip','-T',str(R/'src/dynamic13.ld'),'start.o','play32.o','cd17.o','sector27.o','resident17.o','-o','play32.elf']);run(['llvm-objcopy','-O','binary','play32.elf','play32.bin']);d=(O/'play32.bin').read_bytes();d+=bytes((-len(d))%2048);h=bytearray(2048);h[:8]=b'PS-X EXE';struct.pack_into('<IIII',h,16,0x80010000,0,0x80010000,len(d));struct.pack_into('<II',h,0x30,0x801fff00,0);e=h+d;(O/'ETD_BOOT.EXE').write_bytes(e)
 elf=(O/'play32.elf').read_bytes();off=struct.unpack_from('<I',elf,28)[0];sz,n=struct.unpack_from('<HH',elf,42);high=max(p[2]+p[5] for i in range(n) if (p:=struct.unpack_from('<8I',elf,off+i*sz))[0]==1);rep=dict(exe_bytes=len(e),linked_ram_from_load=high-0x80010000,headroom_to_stack_region=0x801e0000-high,boot_bank_bytes=boot['bytes'],mode='Native compilation; disc-resident startup data; v0.31 AI preserved');assert high<0x801e0000;(O/'report32.json').write_text(json.dumps(rep,indent=2));print(rep,flush=True)
 assets={n:(R/'assets_m16'/n).read_bytes() for n in ('HUBSECT.DAT','HUBSECT.IDX')};assets.update({n:(R/'assets_m20'/n).read_bytes() for n in ('HUBTEX.DAT','HUBTEX.IDX')});assets.update({n:(O/n).read_bytes() for n in ('DOJOSECT.DAT','DOJOSECT.IDX')});assets.update({n:(R/'assets_m27'/n).read_bytes() for n in ('DOJOTEX.DAT','DOJOTEX.IDX')});assets['ETD_POOL.EXE']=(R/'build_m24/play/ETD_POOL.EXE').read_bytes();assets['ETD_AI.EXE']=(OLD/'ETD_AI.EXE').read_bytes();assets['BOOT32.DAT']=(O/'BOOT32.DAT').read_bytes();s=iso(e,assets);root=bytearray();pos=0
 while s[20][pos]:
  n=s[20][pos];rr=s[20][pos:pos+n];name=bytes(rr[33:33+rr[32]])
  if name==b'ETD_SECT.EXE;1':rr=record(b'ETD_BOOT.EXE;1',22,len(e))
  if name==b'SYSTEM.CNF;1':
   config=b'BOOT = cdrom:\\ETD_BOOT.EXE;1\r\nTCB = 4\r\nEVENT = 10\r\nSTACK = 801FFF00\r\n';s[21][:]=config.ljust(2048,b'\0');rr=record(name,21,len(config))
  root.extend(rr);pos+=n
 s[20][:]=root.ljust(2048,b'\0');(O/'ETD_PSX_M32.bin').write_bytes(b''.join(raw(i,x) for i,x in enumerate(s)));(O/'ETD_PSX_M32.cue').write_text('FILE "ETD_PSX_M32.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
if __name__=='__main__':build()
