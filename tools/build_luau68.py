"""Integrate original Luau containers and dragonfly capture into v0.67."""
import argparse,json,struct,subprocess,shutil,sys,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
def build(root,old,visual,out):
    sys.path.insert(0,str(root/'tools'));from disc16 import iso,raw,record
    out.mkdir(parents=True,exist_ok=False)
    for p in old.glob('*.h'):shutil.copyfile(p,out/p.name)
    shutil.copyfile(old/'cache24.c',out/'cache24.c')
    for name in ('LIASECT.DAT','LIASECT.IDX'):shutil.copyfile(old/name,out/name)
    for name in ('LIATEX.DAT','LIATEX.IDX'):shutil.copyfile(old/name,out/name)
    for name in ('propsdata68.h','LIAOBJ.DAT'):shutil.copyfile(visual/'props'/name,out/name)
    shutil.copyfile(visual/'dragonfly'/'dfdata68.h',out/'dfdata68.h')
    for name in ('luau_objects68.h','luau_draw68.h'):shutil.copyfile(HERE/'src'/name,out/name)
    t=(out/'tex19.h').read_text();assert '#define TEXCAP19 64' in t;(out/'tex19.h').write_text(t.replace('#define TEXCAP19 64','#define TEXCAP19 62'))
    data=(out/'LIASECT.DAT').read_bytes();idx=(out/'LIASECT.IDX').read_bytes();tex=(out/'LIATEX.DAT').read_bytes();ti=(out/'LIATEX.IDX').read_bytes()
    prev=json.loads((old/'report67.json').read_text());x,y,z=prev['spawn']
    s=(old/'play67.c').read_text()
    replacements=[('static U32 textent[2]', 'static U32 objextent68[2],textent[2]'),('int found=iso17_find','if(!iso17_find(scratch,"LIAOBJ.DAT;1",pvd[0],objextent68)||objextent68[1]!=12288)return 0;int found=iso17_find'),('#include "sky67.h"','#include "sky67.h"\n#include "luau_objects68.h"'),('static void render18(', '#include "luau_draw68.h"\nstatic void render18('),('renderinter21(p,cx,cy,cz,sn,cs);','renderinter21(p,cx,cy,cz,sn,cs);draw_objects68(p,cx,cy,cz,sn,cs);'),('else if(id&0x8000)', 'else if(id==BUB68_ID){gp(0xe1000400);gp(0x22f0d0a0);for(int j=0;j<3;j++)gp(packetxy(q,j));}else if(id>=PROP68_ID&&id<PROP68_ID+2){int slot=62+id-PROP68_ID;gp(texwindow19(slot));gp(0x24808080);gp(packetxy(q,0));gp(q->uv[0]|(texclut19(slot)<<16));gp(packetxy(q,1));gp(q->uv[1]|(texpage19(slot)<<16));gp(packetxy(q,2));gp(q->uv[2]);}else if(id&0x8000)'),('collect.score+interactions.score','collect.score+interactions.score+objects68.score'),('if(cache.plan_valid){','rect(251,51,60,12,0x252027);number(252,53,objects68.flies);rect(295,53,12,8,objects68.mode?0xf0c080:0x4050d0);if(cache.plan_valid){'),('status=mount18()&&reset18','reset_objects68();status=mount18()&&upload_props68()&&reset18'),('ox=p.x,oz=p.z','ox=p.x,oy=p.y,oz=p.z'),('if(cache.count){swim_step67','if(cache.count){if((btn&512)&&!(p.prev&512))objects68.mode^=1;swim_step67'),('interreset21(&interactions);sfx_stop();','interreset21(&interactions);reset_objects68();sfx_stop();'),('collectstep21(&collect,&cache,p.x,p.y,p.z,p.heading,sine,interactions.health);','collectstep21(&collect,&cache,p.x,p.y,p.z,p.heading,sine,interactions.health);'),('!swim67.active&&(btn&PAD_CIRCLE)','!swim67.active&&!objects68.mode&&(btn&PAD_CIRCLE)'),('if(collect.events||interactions.pickups)','objects_step68(&p,ox,oy,oz,btn,sine);if(collect.events||interactions.pickups||objects68.pickups)'),('if(interactions.broken)sfx_play(2);','if(interactions.broken||objects68.breaks)sfx_play(2);')]
    for a,b in replacements:
        assert s.count(a)==1,a;s=s.replace(a,b)
    (out/'play68.c').write_text(s)
    opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0'];run=lambda a:subprocess.run(a,cwd=out,check=True)
    run(opts+['-c',str(root/'src/dynamic13_start.s'),'-o','start.o'])
    for p in [out/'play68.c',root/'src/cd17.c',root/'src/sector27.c',root/'src/resident17.c']:run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(out),'-I',str(root/'src'),'-c',str(p),'-o',p.stem+'.o'])
    run(['ld.lld','-m','elf32ltsmip','-T',str(root/'src/dynamic13.ld'),'start.o','play68.o','cd17.o','sector27.o','resident17.o','-o','play68.elf']);run(['llvm-objcopy','-O','binary','play68.elf','play68.raw']);p=(out/'play68.raw').read_bytes();p+=bytes((-len(p))%2048);h=bytearray(2048);h[:8]=b'PS-X EXE';struct.pack_into('<IIII',h,16,0x80010000,0,0x80010000,len(p));struct.pack_into('<II',h,0x30,0x801fff00,0);exe=h+p;(out/'ETD_L68.EXE').write_bytes(exe)
    sectors=iso(exe,{'LIASECT.DAT':data,'LIASECT.IDX':idx,'LIATEX.DAT':tex,'LIATEX.IDX':ti,'LIAOBJ.DAT':(out/'LIAOBJ.DAT').read_bytes()});directory=bytearray();pos=0
    while sectors[20][pos]:
        n=sectors[20][pos];rr=sectors[20][pos:pos+n];name=bytes(rr[33:33+rr[32]])
        if name==b'ETD_SECT.EXE;1':rr=record(b'ETD_L68.EXE;1',22,len(exe))
        if name==b'SYSTEM.CNF;1':
            cfg=b'BOOT = cdrom:\\ETD_L68.EXE;1\r\nTCB = 4\r\nEVENT = 10\r\nSTACK = 801FFF00\r\n';sectors[21][:]=cfg.ljust(2048,b'\0');rr=record(name,21,len(cfg))
        directory.extend(rr);pos+=n
    sectors[20][:]=directory.ljust(2048,b'\0');disc=b''.join(raw(i,p) for i,p in enumerate(sectors));(out/'ETD_L68.bin').write_bytes(disc);(out/'ETD_L68.cue').write_text('FILE "ETD_L68.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
    elf=(out/'play68.elf').read_bytes();off=struct.unpack_from('<I',elf,28)[0];sz,n=struct.unpack_from('<HH',elf,42);high=max(p[2]+p[5] for i in range(n) if (p:=struct.unpack_from('<8I',elf,off+i*sz))[0]==1);assert high<0x801e0000
    rep=dict(spawn=[x,y,z],gems=prev["gems"],gem_value=prev["gem_value"],baskets=prev["baskets"],basket_value=prev["basket_value"],exe_bytes=len(exe),linked_ram=high-0x80010000,headroom=0x801e0000-high,sectors=len(sectors),exe_sha256=hashlib.sha256(exe).hexdigest(),disc_sha256=hashlib.sha256(disc).hexdigest());(out/'report68.json').write_text(json.dumps(rep,indent=2)+'\n');print(rep)
if __name__=='__main__':
 p=argparse.ArgumentParser();[p.add_argument(k,type=Path) for k in ('root','old','visual','out')];a=p.parse_args();build(*(v.resolve() for v in (a.root,a.old,a.visual,a.out)))
