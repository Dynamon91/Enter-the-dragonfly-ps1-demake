"""Build v0.33 bubble capture prototype from v0.32."""
from pathlib import Path
import json,struct,shutil,subprocess
from disc16 import iso,raw,record
from bootbank32 import generate
R=Path(__file__).resolve().parents[1];O=R/'build_m33/play';OLD=R/'build_m32/play'
def build():
 O.mkdir(parents=True,exist_ok=True)
 for p in OLD.iterdir():
  if p.suffix in ('.h','.c','.DAT','.IDX','.json'):shutil.copyfile(p,O/p.name)
 boot=json.loads((O/'bootbank32.json').read_text())
 for n in ('dragonflydata33.h','dragonflyids33.h'):shutil.copyfile(R/'assets_m33'/n,O/n)
 s=(OLD/'play32.c').read_text().replace('#include "collectdata12.h"','#include "collectdata12.h"\n#include "dragonflydata33.h"\n#include "bubble33.h"\nstatic Progress33 progress33;static Capture33 capture33;')
 s=s.replace('#define PAD_CIRCLE 8192','#define PAD_CIRCLE 8192\n#define PAD_TRIANGLE 4096\n#define PAD_R2 512')
 render=(R/'src/render33.h').read_text();s=s.replace('static void render18(',render+'\nstatic void render18(').replace('renderenemy29(p,cx,cy,cz,sn,cs);','renderenemy29(p,cx,cy,cz,sn,cs);rendercapture33(p,cx,cy,cz,sn,cs);')
 s=s.replace('rect(302,8,10,10,status?', 'rect(251,38,65,15,0x252027);number(255,40,progress33.count);rect(297,40,7,9,capture33.breath?0xffe070:0x3060f0);rect(307,40,7,9,progress33.mode?0x60df60:0x808080);rect(302,8,10,10,status?')
 s=s.replace('enemy_reset31();int y=0;','enemy_reset31();progress_reset33(&progress33,0);progress_visit33(&progress33,1);capture_reset33(&capture33);int y=0;')
 s=s.replace('if(cache.count){step18(&p,btn,ax,az);','if(cache.count){if((btn&PAD_TRIANGLE)&&!(p.prev&PAD_TRIANGLE))capture33.breath^=1;step18(&p,btn,ax,az);')
 s=s.replace('enemy_reset31();sfx_stop();','enemy_reset31();progress_reset33(&progress33,(btn&PAD_R2)?!progress33.mode:progress33.mode);progress_visit33(&progress33,1);capture_reset33(&capture33);sfx_stop();')
 s=s.replace('btn&PAD_CIRCLE,p.grounded,collect.sx','(btn&PAD_CIRCLE)&&!capture33.breath,p.grounded,collect.sx')
 s=s.replace('enemy_step31(&interactions','capture_step33(&capture33,&progress33,&cache,p.x,p.y,p.z,p.heading,btn&PAD_CIRCLE,p.grounded,sine);if(capture33.event)sfx_play(1);enemy_step31(&interactions')
 (O/'play33.c').write_text(s)
 opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0'];run=lambda a:subprocess.run(a,cwd=O,check=True)
 run(opts+['-c',str(R/'src/dynamic13_start.s'),'-o','start.o'])
 for p in [O/'play33.c',R/'src/cd17.c',R/'src/sector27.c',R/'src/resident17.c']:run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(O),'-I',str(R/'src'),'-c',str(p),'-o',p.stem+'.o'])
 run(['ld.lld','-m','elf32ltsmip','-T',str(R/'src/dynamic13.ld'),'start.o','play33.o','cd17.o','sector27.o','resident17.o','-o','play33.elf']);run(['llvm-objcopy','-O','binary','play33.elf','play33.bin']);d=(O/'play33.bin').read_bytes();d+=bytes((-len(d))%2048);h=bytearray(2048);h[:8]=b'PS-X EXE';struct.pack_into('<IIII',h,16,0x80010000,0,0x80010000,len(d));struct.pack_into('<II',h,0x30,0x801fff00,0);e=h+d;(O/'ETD_BUBL.EXE').write_bytes(e)
 elf=(O/'play33.elf').read_bytes();off=struct.unpack_from('<I',elf,28)[0];sz,n=struct.unpack_from('<HH',elf,42);high=max(p[2]+p[5] for i in range(n) if (p:=struct.unpack_from('<8I',elf,off+i*sz))[0]==1);rep=dict(exe_bytes=len(e),linked_ram_from_load=high-0x80010000,headroom_to_stack_region=0x801e0000-high,boot_bank_bytes=boot['bytes'],mode='Native compilation; bubble capture prototype; Classic/Expanded session ledger');assert high<0x801e0000;(O/'report33.json').write_text(json.dumps(rep,indent=2));print(rep,flush=True)
 assets={n:(R/'assets_m16'/n).read_bytes() for n in ('HUBSECT.DAT','HUBSECT.IDX')};assets.update({n:(R/'assets_m20'/n).read_bytes() for n in ('HUBTEX.DAT','HUBTEX.IDX')});assets.update({n:(O/n).read_bytes() for n in ('DOJOSECT.DAT','DOJOSECT.IDX')});assets.update({n:(R/'assets_m27'/n).read_bytes() for n in ('DOJOTEX.DAT','DOJOTEX.IDX')});assets['ETD_POOL.EXE']=(R/'build_m24/play/ETD_POOL.EXE').read_bytes();assets['ETD_AI.EXE']=(R/'build_m31/play/ETD_AI.EXE').read_bytes();assets['ETD_BOOT.EXE']=(OLD/'ETD_BOOT.EXE').read_bytes();assets['BOOT32.DAT']=(O/'BOOT32.DAT').read_bytes();s=iso(e,assets);root=bytearray();pos=0
 while s[20][pos]:
  n=s[20][pos];rr=s[20][pos:pos+n];name=bytes(rr[33:33+rr[32]])
  if name==b'ETD_SECT.EXE;1':rr=record(b'ETD_BUBL.EXE;1',22,len(e))
  if name==b'SYSTEM.CNF;1':
   config=b'BOOT = cdrom:\\ETD_BUBL.EXE;1\r\nTCB = 4\r\nEVENT = 10\r\nSTACK = 801FFF00\r\n';s[21][:]=config.ljust(2048,b'\0');rr=record(name,21,len(config))
  root.extend(rr);pos+=n
 s[20][:]=root.ljust(2048,b'\0');(O/'ETD_PSX_M33.bin').write_bytes(b''.join(raw(i,x) for i,x in enumerate(s)));(O/'ETD_PSX_M33.cue').write_text('FILE "ETD_PSX_M33.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
if __name__=='__main__':build()
