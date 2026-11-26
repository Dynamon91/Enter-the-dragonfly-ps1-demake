"""Build v0.36 sampled NPC animation and source dialogue from v0.35."""
from pathlib import Path
import json,struct,shutil,subprocess,re,zlib
import numpy as np
from disc16 import iso,raw,record
from bootbank32 import generate
R=Path(__file__).resolve().parents[1];O=R/'build_m36/play';OLD=R/'build_m35/play'
def build():
 O.mkdir(parents=True,exist_ok=True)
 for p in OLD.iterdir():
  if p.suffix in ('.h','.c','.DAT','.IDX','.json'):shutil.copyfile(p,O/p.name)
 boot=json.loads((O/'bootbank32.json').read_text());bank=(O/'QMOD35.DAT').read_bytes()
 for h in ('questanim36.h','dialogue36.h'):shutil.copyfile(R/'assets_m36'/h,O/h)
 s=(OLD/'play35.c').read_text()
 s=s.replace('static Quest34 quest34;', 'static Quest34 quest34;\n#include "dialogue_state36.h"\n#include "questanim36.h"\n#include "dialogue36.h"\nstatic Dialog36 dialog36; static int qclock36;')
 # Render the exact v35 mesh with original sampled deltas. No pose buffer necessary.
 a=s.index('static void quest_mesh35(');b=s.index('static void renderquest35',a)
 v=s[a:b].replace('int a=sine[h&63],b=sine[(h+16)&63];','int a=sine[h&63],b=sine[(h+16)&63];int talk=dialog_active36(&dialog36)&&dialog36.actor==id;int f0=0,f1=0,frac=0,period=1;const signed char *d0=0,*d1=0;if(id<3){period=qperiod36[id][talk];f0=pose_index36(qclock36,talk,period);f1=(talk?6:0)+((f0-(talk?6:0)+1)%6);frac=((qclock36%period)*6%period)*256/period;d0=qdelta36[id]+f0*m->nv*3;d1=qdelta36[id]+f1*m->nv*3;}')
 v=v.replace('zz=m->v[j][2];pts[j]', 'zz=m->v[j][2];if(d0){int k=j*3;xx+=(d0[k]*(256-frac)+d1[k]*frac+128)>>8;yy+=(d0[k+1]*(256-frac)+d1[k+1]*frac+128)>>8;zz+=(d0[k+2]*(256-frac)+d1[k+2]*frac+128)>>8;}pts[j]')
 s=s[:a]+v+s[b:]
 s=s.replace('static void hudquest34(void)', '#include "dialogue_render36.h"\nstatic void hudquest34(void)')
 s=s.replace('hudquest34();idle();','hudquest34();huddialog36();idle();')
 s=s.replace('quest_reset34(&quest34);','quest_reset34(&quest34);dialog_reset36(&dialog36);qclock36=0;')
 s=s.replace('if(cache.count){if((btn&PAD_TRIANGLE)', 'qclock36=(qclock36+1)%3600;int modal=dialog_active36(&dialog36)&&!reset;if(modal){if((btn&(256|PAD_CROSS))&~p.prev)dialog_next36(&dialog36);p.prev=btn;}else if(cache.count){if((btn&PAD_TRIANGLE)')
 s=s.replace('quest_step34(&quest34,&progress33,&cache,p.x,p.y,p.z,p.grounded,damage);','int oldstage36[3]={quest34.stage[0],quest34.stage[1],quest34.stage[2]},oldseen36=quest34.seen;quest_step34(&quest34,&progress33,&cache,p.x,p.y,p.z,p.grounded,damage);if((quest34.event&2)&&quest34.near>=0){int id=quest34.near;int prior=oldstage36[id];if((quest34.event&4)&&prior==Q34_MOVING)prior=Q34_ARRIVED;dialog_open36(&dialog36,id,prior,(oldseen36>>id)&1,quest34.event,quest34.reward);}')
 s=s.replace('p.x!=ox||p.z!=oz,btn,was','p.x!=ox||p.z!=oz,modal?0:btn,was')
 (O/'play36.c').write_text(s)
 opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0'];run=lambda a:subprocess.run(a,cwd=O,check=True)
 run(opts+['-c',str(R/'src/dynamic13_start.s'),'-o','start.o'])
 for p in [O/'play36.c',R/'src/cd17.c',R/'src/sector27.c',R/'src/resident17.c']:run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(O),'-I',str(R/'src'),'-c',str(p),'-o',p.stem+'.o'])
 run(['ld.lld','-m','elf32ltsmip','-T',str(R/'src/dynamic13.ld'),'start.o','play36.o','cd17.o','sector27.o','resident17.o','-o','play36.elf']);run(['llvm-objcopy','-O','binary','play36.elf','play36.bin']);d=(O/'play36.bin').read_bytes();d+=bytes((-len(d))%2048);h=bytearray(2048);h[:8]=b'PS-X EXE';struct.pack_into('<IIII',h,16,0x80010000,0,0x80010000,len(d));struct.pack_into('<II',h,0x30,0x801fff00,0);e=h+d;(O/'ETD_TALK.EXE').write_bytes(e)
 elf=(O/'play36.elf').read_bytes();off=struct.unpack_from('<I',elf,28)[0];sz,n=struct.unpack_from('<HH',elf,42);high=max(p[2]+p[5] for i in range(n) if (p:=struct.unpack_from('<8I',elf,off+i*sz))[0]==1);rep=dict(exe_bytes=len(e),linked_ram_from_load=high-0x80010000,headroom_to_stack_region=0x801e0000-high,boot_bank_bytes=boot['bytes'],quest_bank_bytes=len(bank),mode='Native compilation; original NPC idle/talk sample playback and English dialogue');assert high<0x801e0000;(O/'report36.json').write_text(json.dumps(rep,indent=2));print(rep,flush=True)
 assets={n:(R/'assets_m16'/n).read_bytes() for n in ('HUBSECT.DAT','HUBSECT.IDX')};assets.update({n:(R/'assets_m20'/n).read_bytes() for n in ('HUBTEX.DAT','HUBTEX.IDX')});assets.update({n:(O/n).read_bytes() for n in ('DOJOSECT.DAT','DOJOSECT.IDX')});assets.update({n:(R/'assets_m27'/n).read_bytes() for n in ('DOJOTEX.DAT','DOJOTEX.IDX')});assets['ETD_POOL.EXE']=(R/'build_m24/play/ETD_POOL.EXE').read_bytes();assets['ETD_AI.EXE']=(R/'build_m31/play/ETD_AI.EXE').read_bytes();assets['ETD_NPCS.EXE']=(OLD/'ETD_NPCS.EXE').read_bytes();assets['QMOD35.DAT']=bank;assets['ETD_BOOT.EXE']=(R/'build_m32/play/ETD_BOOT.EXE').read_bytes();assets['BOOT32.DAT']=(O/'BOOT32.DAT').read_bytes();s=iso(e,assets);root=bytearray();pos=0
 while s[20][pos]:
  n=s[20][pos];rr=s[20][pos:pos+n];name=bytes(rr[33:33+rr[32]])
  if name==b'ETD_SECT.EXE;1':rr=record(b'ETD_TALK.EXE;1',22,len(e))
  if name==b'SYSTEM.CNF;1':
   config=b'BOOT = cdrom:\\ETD_TALK.EXE;1\r\nTCB = 4\r\nEVENT = 10\r\nSTACK = 801FFF00\r\n';s[21][:]=config.ljust(2048,b'\0');rr=record(name,21,len(config))
  root.extend(rr);pos+=n
 s[20][:]=root.ljust(2048,b'\0');(O/'ETD_PSX_M36.bin').write_bytes(b''.join(raw(i,x) for i,x in enumerate(s)));(O/'ETD_PSX_M36.cue').write_text('FILE "ETD_PSX_M36.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
if __name__=='__main__':build()
