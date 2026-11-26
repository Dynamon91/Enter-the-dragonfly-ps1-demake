"""Build v0.37 losslessly packed animation data from v0.36."""
from pathlib import Path
import json,struct,shutil,subprocess,re,zlib
import numpy as np
from disc16 import iso,raw,record
from bootbank32 import generate
R=Path(__file__).resolve().parents[1];O=R/'build_m37/play';OLD=R/'build_m36/play'
def build():
 O.mkdir(parents=True,exist_ok=True)
 for p in OLD.iterdir():
  if p.suffix in ('.h','.c','.DAT','.IDX','.json'):shutil.copyfile(p,O/p.name)
 boot=json.loads((O/'bootbank32.json').read_text());bank=(O/'QMOD35.DAT').read_bytes()
 for h in ('rig37_data.h','questpack37.h'):shutil.copyfile(R/'assets_m37'/h,O/h)
 s=(OLD/'play36.c').read_text().replace('"rig11.h"','"rig37.h"').replace('"questanim36.h"','"questpose37.h"')
 s=s.replace('d0=qdelta36[id]+f0*m->nv*3;d1=qdelta36[id]+f1*m->nv*3;', 'd0=qpose37(id,f0,m->nv);d1=qpose37(id,f1,m->nv);if(!d1)d0=0;')
 (O/'play37.c').write_text(s)
 opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0'];run=lambda a:subprocess.run(a,cwd=O,check=True)
 run(opts+['-c',str(R/'src/dynamic13_start.s'),'-o','start.o'])
 for p in [O/'play37.c',R/'src/cd17.c',R/'src/sector27.c',R/'src/resident17.c']:run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(O),'-I',str(R/'src'),'-c',str(p),'-o',p.stem+'.o'])
 run(['ld.lld','-m','elf32ltsmip','-T',str(R/'src/dynamic13.ld'),'start.o','play37.o','cd17.o','sector27.o','resident17.o','-o','play37.elf']);run(['llvm-objcopy','-O','binary','play37.elf','play37.bin']);d=(O/'play37.bin').read_bytes();d+=bytes((-len(d))%2048);h=bytearray(2048);h[:8]=b'PS-X EXE';struct.pack_into('<IIII',h,16,0x80010000,0,0x80010000,len(d));struct.pack_into('<II',h,0x30,0x801fff00,0);e=h+d;(O/'ETD_PACK.EXE').write_bytes(e)
 elf=(O/'play37.elf').read_bytes();off=struct.unpack_from('<I',elf,28)[0];sz,n=struct.unpack_from('<HH',elf,42);high=max(p[2]+p[5] for i in range(n) if (p:=struct.unpack_from('<8I',elf,off+i*sz))[0]==1);rep=dict(exe_bytes=len(e),linked_ram_from_load=high-0x80010000,headroom_to_stack_region=0x801e0000-high,boot_bank_bytes=boot['bytes'],quest_bank_bytes=len(bank),mode='Native compilation; lossless grouped animation compression');assert high<0x801e0000;(O/'report37.json').write_text(json.dumps(rep,indent=2));print(rep,flush=True)
 assets={n:(R/'assets_m16'/n).read_bytes() for n in ('HUBSECT.DAT','HUBSECT.IDX')};assets.update({n:(R/'assets_m20'/n).read_bytes() for n in ('HUBTEX.DAT','HUBTEX.IDX')});assets.update({n:(O/n).read_bytes() for n in ('DOJOSECT.DAT','DOJOSECT.IDX')});assets.update({n:(R/'assets_m27'/n).read_bytes() for n in ('DOJOTEX.DAT','DOJOTEX.IDX')});assets['ETD_POOL.EXE']=(R/'build_m24/play/ETD_POOL.EXE').read_bytes();assets['ETD_AI.EXE']=(R/'build_m31/play/ETD_AI.EXE').read_bytes();assets['ETD_TALK.EXE']=(OLD/'ETD_TALK.EXE').read_bytes();assets['ETD_NPCS.EXE']=(R/'build_m35/play/ETD_NPCS.EXE').read_bytes();assets['QMOD35.DAT']=bank;assets['ETD_BOOT.EXE']=(R/'build_m32/play/ETD_BOOT.EXE').read_bytes();assets['BOOT32.DAT']=(O/'BOOT32.DAT').read_bytes();s=iso(e,assets);root=bytearray();pos=0
 while s[20][pos]:
  n=s[20][pos];rr=s[20][pos:pos+n];name=bytes(rr[33:33+rr[32]])
  if name==b'ETD_SECT.EXE;1':rr=record(b'ETD_PACK.EXE;1',22,len(e))
  if name==b'SYSTEM.CNF;1':
   config=b'BOOT = cdrom:\\ETD_PACK.EXE;1\r\nTCB = 4\r\nEVENT = 10\r\nSTACK = 801FFF00\r\n';s[21][:]=config.ljust(2048,b'\0');rr=record(name,21,len(config))
  root.extend(rr);pos+=n
 s[20][:]=root.ljust(2048,b'\0');(O/'ETD_PSX_M37.bin').write_bytes(b''.join(raw(i,x) for i,x in enumerate(s)));(O/'ETD_PSX_M37.cue').write_text('FILE "ETD_PSX_M37.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
if __name__=='__main__':build()
