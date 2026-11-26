"""Build v0.35 original quest models from v0.34."""
from pathlib import Path
import json,struct,shutil,subprocess,re,zlib
import numpy as np
from disc16 import iso,raw,record
from bootbank32 import generate
R=Path(__file__).resolve().parents[1];O=R/'build_m35/play';OLD=R/'build_m34/play'
def build():
 O.mkdir(parents=True,exist_ok=True)
 for p in OLD.iterdir():
  if p.suffix in ('.h','.c','.DAT','.IDX','.json'):shutil.copyfile(p,O/p.name)
 boot=json.loads((O/'bootbank32.json').read_text())
 a=R/'assets_m35';z=np.load(a/'questmodels.npz');rep=json.loads((a/'report.json').read_text());q=json.loads((R/'assets_m34/report.json').read_text())['quests'];bank=z['palettes'].astype('<u2').tobytes()+z['pixels'].astype('u1').tobytes();(O/'QMOD35.DAT').write_bytes(bank);h=(a/'questmodels35.h').read_text();h=h[:h.index('static const u16 qpal35')];h='#define Q35_MAXV '+str(max(m['vertices'] for m in rep['models']))+'\n'+h;h+='static const int qidle35[3][3]={'+','.join('{'+','.join(str(round(v*s)) for v,s in zip(o['prop']['source_xyz'],(1,-1,1)))+'}' for o in q)+'};\n';h+=f'#define Q35_BYTES {len(bank)}u\n#define Q35_PAD {(len(bank)+2047)//2048*2048}u\n#define Q35_CRC 0x{zlib.crc32(bank):08x}u\n';(O/'questmodels35.h').write_text(h)
 s=(OLD/'play34.c').read_text();s=s.replace('#include "quest34.h"','#include "quest34.h"\ntypedef struct {u16 idx[3];U8 uv[6],mat;} QuestFace35;\ntypedef struct {const s16 (*v)[3];const QuestFace35*f;int nv,nf;} QuestModel35;\n#include "questmodels35.h"\n#include "questbank35.h"');s=s.replace('bootextent32[2]','bootextent32[2],questextent35[2]');s=s.replace('bootextent32[1]!=BOOT_BYTES32','bootextent32[1]!=BOOT_BYTES32||!iso17_find(scratch,"QMOD35.DAT;1",pvd[0],questextent35)||questextent35[1]!=Q35_BYTES');start=s.index('/* Diagnostic markers:');end=s.index('static void hudquest34',start);s=s[:start]+(R/'src/render35.h').read_text()+'\n'+s[end:];s=s.replace('renderquest34(p,cx,cy,cz,sn,cs);','renderquest35(p,cx,cy,cz,sn,cs);');s=s.replace('else if(id&0x8000)','else if(id>=QUEST_ID35&&id<QUEST_ID35+Q35_TEX){quest_packet35(q,id-QUEST_ID35);}else if(id&0x8000)');s=s.replace('startup32=0;status=reset18','startup32=0;if(!quest_load35((U8*)cache.arena,sizeof(cache.arena),questextent35[0],questextent35[1],cd17_read,0)){gp(0x020000b0);gp(0);gp((240<<16)|320);idle();GP1=0x05000000;GP1=0x03000000;for(;;)vb();}quest_upload35((U8*)cache.arena);status=reset18');
 (O/'play35.c').write_text(s)
 opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0'];run=lambda a:subprocess.run(a,cwd=O,check=True)
 run(opts+['-c',str(R/'src/dynamic13_start.s'),'-o','start.o'])
 for p in [O/'play35.c',R/'src/cd17.c',R/'src/sector27.c',R/'src/resident17.c']:run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(O),'-I',str(R/'src'),'-c',str(p),'-o',p.stem+'.o'])
 run(['ld.lld','-m','elf32ltsmip','-T',str(R/'src/dynamic13.ld'),'start.o','play35.o','cd17.o','sector27.o','resident17.o','-o','play35.elf']);run(['llvm-objcopy','-O','binary','play35.elf','play35.bin']);d=(O/'play35.bin').read_bytes();d+=bytes((-len(d))%2048);h=bytearray(2048);h[:8]=b'PS-X EXE';struct.pack_into('<IIII',h,16,0x80010000,0,0x80010000,len(d));struct.pack_into('<II',h,0x30,0x801fff00,0);e=h+d;(O/'ETD_NPCS.EXE').write_bytes(e)
 elf=(O/'play35.elf').read_bytes();off=struct.unpack_from('<I',elf,28)[0];sz,n=struct.unpack_from('<HH',elf,42);high=max(p[2]+p[5] for i in range(n) if (p:=struct.unpack_from('<8I',elf,off+i*sz))[0]==1);rep=dict(exe_bytes=len(e),linked_ram_from_load=high-0x80010000,headroom_to_stack_region=0x801e0000-high,boot_bank_bytes=boot['bytes'],quest_bank_bytes=len(bank),mode='Native compilation; original quest actor meshes and bind poses');assert high<0x801e0000;(O/'report35.json').write_text(json.dumps(rep,indent=2));print(rep,flush=True)
 assets={n:(R/'assets_m16'/n).read_bytes() for n in ('HUBSECT.DAT','HUBSECT.IDX')};assets.update({n:(R/'assets_m20'/n).read_bytes() for n in ('HUBTEX.DAT','HUBTEX.IDX')});assets.update({n:(O/n).read_bytes() for n in ('DOJOSECT.DAT','DOJOSECT.IDX')});assets.update({n:(R/'assets_m27'/n).read_bytes() for n in ('DOJOTEX.DAT','DOJOTEX.IDX')});assets['ETD_POOL.EXE']=(R/'build_m24/play/ETD_POOL.EXE').read_bytes();assets['ETD_AI.EXE']=(R/'build_m31/play/ETD_AI.EXE').read_bytes();assets['ETD_QEST.EXE']=(OLD/'ETD_QEST.EXE').read_bytes();assets['QMOD35.DAT']=bank;assets['ETD_BOOT.EXE']=(R/'build_m32/play/ETD_BOOT.EXE').read_bytes();assets['BOOT32.DAT']=(O/'BOOT32.DAT').read_bytes();s=iso(e,assets);root=bytearray();pos=0
 while s[20][pos]:
  n=s[20][pos];rr=s[20][pos:pos+n];name=bytes(rr[33:33+rr[32]])
  if name==b'ETD_SECT.EXE;1':rr=record(b'ETD_NPCS.EXE;1',22,len(e))
  if name==b'SYSTEM.CNF;1':
   config=b'BOOT = cdrom:\\ETD_NPCS.EXE;1\r\nTCB = 4\r\nEVENT = 10\r\nSTACK = 801FFF00\r\n';s[21][:]=config.ljust(2048,b'\0');rr=record(name,21,len(config))
  root.extend(rr);pos+=n
 s[20][:]=root.ljust(2048,b'\0');(O/'ETD_PSX_M35.bin').write_bytes(b''.join(raw(i,x) for i,x in enumerate(s)));(O/'ETD_PSX_M35.cue').write_text('FILE "ETD_PSX_M35.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
if __name__=='__main__':build()
