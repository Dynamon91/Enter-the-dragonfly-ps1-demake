"""Build v0.34 quest progression prototype from v0.33."""
from pathlib import Path
import json,struct,shutil,subprocess
from disc16 import iso,raw,record
from bootbank32 import generate
R=Path(__file__).resolve().parents[1];O=R/'build_m34/play';OLD=R/'build_m33/play'
def build():
 O.mkdir(parents=True,exist_ok=True)
 for p in OLD.iterdir():
  if p.suffix in ('.h','.c','.DAT','.IDX','.json'):shutil.copyfile(p,O/p.name)
 boot=json.loads((O/'bootbank32.json').read_text())
 shutil.copyfile(R/'assets_m34/questdata34.h',O/'questdata34.h')
 s=(OLD/'play33.c').read_text().replace('static Progress33 progress33;static Capture33 capture33;','static Progress33 progress33;static Capture33 capture33;\n#include "quest34.h"\nstatic Quest34 quest34;')
 s=s.replace('static void render18(', (R/'src/render34.h').read_text()+'\nstatic void render18(').replace('rendercapture33(p,cx,cy,cz,sn,cs);','rendercapture33(p,cx,cy,cz,sn,cs);renderquest34(p,cx,cy,cz,sn,cs);')
 s=s.replace('}idle();}\nint main','}hudquest34();idle();}\nint main')
 s=s.replace('capture_reset33(&capture33);','capture_reset33(&capture33);quest_reset34(&quest34);')
 s=s.replace('if(capture33.event)sfx_play(1);','quest_step34(&quest34,&progress33,&cache,p.x,p.y,p.z,p.grounded,damage);if(capture33.event||(quest34.event&8))sfx_play(1);')
 (O/'play34.c').write_text(s)
 opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0'];run=lambda a:subprocess.run(a,cwd=O,check=True)
 run(opts+['-c',str(R/'src/dynamic13_start.s'),'-o','start.o'])
 for p in [O/'play34.c',R/'src/cd17.c',R/'src/sector27.c',R/'src/resident17.c']:run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(O),'-I',str(R/'src'),'-c',str(p),'-o',p.stem+'.o'])
 run(['ld.lld','-m','elf32ltsmip','-T',str(R/'src/dynamic13.ld'),'start.o','play34.o','cd17.o','sector27.o','resident17.o','-o','play34.elf']);run(['llvm-objcopy','-O','binary','play34.elf','play34.bin']);d=(O/'play34.bin').read_bytes();d+=bytes((-len(d))%2048);h=bytearray(2048);h[:8]=b'PS-X EXE';struct.pack_into('<IIII',h,16,0x80010000,0,0x80010000,len(d));struct.pack_into('<II',h,0x30,0x801fff00,0);e=h+d;(O/'ETD_QEST.EXE').write_bytes(e)
 elf=(O/'play34.elf').read_bytes();off=struct.unpack_from('<I',elf,28)[0];sz,n=struct.unpack_from('<HH',elf,42);high=max(p[2]+p[5] for i in range(n) if (p:=struct.unpack_from('<8I',elf,off+i*sz))[0]==1);rep=dict(exe_bytes=len(e),linked_ram_from_load=high-0x80010000,headroom_to_stack_region=0x801e0000-high,boot_bank_bytes=boot['bytes'],mode='Native compilation; source-derived three-recovery quest; diagnostic markers');assert high<0x801e0000;(O/'report34.json').write_text(json.dumps(rep,indent=2));print(rep,flush=True)
 assets={n:(R/'assets_m16'/n).read_bytes() for n in ('HUBSECT.DAT','HUBSECT.IDX')};assets.update({n:(R/'assets_m20'/n).read_bytes() for n in ('HUBTEX.DAT','HUBTEX.IDX')});assets.update({n:(O/n).read_bytes() for n in ('DOJOSECT.DAT','DOJOSECT.IDX')});assets.update({n:(R/'assets_m27'/n).read_bytes() for n in ('DOJOTEX.DAT','DOJOTEX.IDX')});assets['ETD_POOL.EXE']=(R/'build_m24/play/ETD_POOL.EXE').read_bytes();assets['ETD_AI.EXE']=(R/'build_m31/play/ETD_AI.EXE').read_bytes();assets['ETD_BUBL.EXE']=(OLD/'ETD_BUBL.EXE').read_bytes();assets['ETD_BOOT.EXE']=(R/'build_m32/play/ETD_BOOT.EXE').read_bytes();assets['BOOT32.DAT']=(O/'BOOT32.DAT').read_bytes();s=iso(e,assets);root=bytearray();pos=0
 while s[20][pos]:
  n=s[20][pos];rr=s[20][pos:pos+n];name=bytes(rr[33:33+rr[32]])
  if name==b'ETD_SECT.EXE;1':rr=record(b'ETD_QEST.EXE;1',22,len(e))
  if name==b'SYSTEM.CNF;1':
   config=b'BOOT = cdrom:\\ETD_QEST.EXE;1\r\nTCB = 4\r\nEVENT = 10\r\nSTACK = 801FFF00\r\n';s[21][:]=config.ljust(2048,b'\0');rr=record(name,21,len(config))
  root.extend(rr);pos+=n
 s[20][:]=root.ljust(2048,b'\0');(O/'ETD_PSX_M34.bin').write_bytes(b''.join(raw(i,x) for i,x in enumerate(s)));(O/'ETD_PSX_M34.cue').write_text('FILE "ETD_PSX_M34.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
if __name__=='__main__':build()
