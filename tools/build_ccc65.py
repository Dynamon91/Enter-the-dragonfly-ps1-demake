"""Add source-defined platforms and combat to v0.64."""
import argparse,hashlib,json,struct,subprocess,sys,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
def build(root,old,sky,out):
    sys.path.insert(0,str(root/'tools'));from disc16 import iso,raw,record
    out.mkdir(parents=True,exist_ok=False)
    for p in old.glob('*.h'):shutil.copyfile(p,out/p.name)
    for p in old.glob('*.c'):
        if p.name=='cache24.c':shutil.copyfile(p,out/p.name)
    for n in ('CCCSECT.DAT','CCCSECT.IDX'):shutil.copyfile(old/n,out/n)
    for n in ('CCCTEX.DAT','CCCTEX.IDX'):shutil.copyfile(old/n,out/n)
    for n in ('CCCACT.DAT','CCCVOX.DAT'):shutil.copyfile(old/n,out/n)
    shutil.copyfile(old/'CCCBRN.DAT',out/'CCCBRN.DAT')
    shutil.copyfile(old/'CCCUFO.DAT',out/'CCCUFO.DAT')
    shutil.copyfile(sky/'platformdata65.h',out/'platformdata65.h')
    for n in ('platform65.h','platform_ui65.h','combat65.h','combat_ui65.h'):shutil.copyfile(HERE/'src'/n,out/n)
    c=(out/'actors59.h').read_text();c=c.replace('if(a->model==0)continue;','if(a->model==0||a->model==6||!actor_alive65(i))continue;').replace('sine[a->yaw],ac=sine[(a->yaw+16)&63]','sine[actor_yaw65(i)],ac=sine[(actor_yaw65(i)+16)&63]');(out/'actors59.h').write_text(c)
    s=(old/'play64.c').read_text()
    for a,b in [('static void step18(', 'static int player_floor65(int,int,int,int);static int landing65(int,int,int,int,int);\nstatic void step18('),('cache18_floor(&cache,(p->x+nx)/2,(p->z+nz)/2,p->ground,110)','player_floor65((p->x+nx)/2,(p->z+nz)/2,p->ground,110)'),('cache18_floor(&cache,nx,nz,p->ground,110)','player_floor65(nx,nz,p->ground,110)'),('p->x=nx;p->z=nz;p->ground=f;', 'p->x=nx;p->z=nz;if(f>p->ground+110&&p->grounded){p->grounded=0;p->vy=0;}p->ground=f;'),('p->y+=p->vy;if(p->y>=p->ground)', 'p->y+=p->vy;if(p->vy>=0)p->ground=landing65(p->x,p->z,p->y-p->vy,p->y,p->ground);if(p->y>=p->ground)'),('#include "actors59.h"','static int actor_alive65(unsigned);static int actor_yaw65(unsigned);\n#include "actors59.h"'),('#include "ufo_ui64.h"','#include "ufo_ui64.h"\n#include "platform_ui65.h"\n#include "combat_ui65.h"'),('ufo_draw64(p,cx,cy,cz,sn,cs);','ufo_draw64(p,cx,cy,cz,sn,cs);lifts_draw65(p,cx,cy,cz,sn,cs);combat_draw65(p,cx,cy,cz,sn,cs);'),('reset_ufo64();','reset_ufo64();reset_lifts65();combat_reset65();'),('step18(&p,btn,ax,az);','if(!reset)lifts_step65(&p,capture63.mode,btn&PAD_CIRCLE);step18(&p,btn,ax,az);'),('if(capture63.event)sfx_play(1);','if(capture63.event)sfx_play(1);combat_step65(&p,ox,oz,btn&PAD_SQUARE,capture63.mode,btn&PAD_CIRCLE);if(dead65&&reset18(&p)){interactions.health=3;dead65=0;hurt65=90;for(int i=0;i<12;i++)shots65[i].life=0;for(int i=0;i<FIRE21;i++)interactions.fire[i].life=0;for(int i=0;i<BUB_COUNT63;i++)capture63.b[i].life=0;}')]:
        assert a in s,a;s=s.replace(a,b)
    (out/'play65.c').write_text(s)
    opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0'];run=lambda a:subprocess.run(a,cwd=out,check=True)
    run(opts+['-c',str(root/'src/dynamic13_start.s'),'-o','start.o'])
    for p in [out/'play65.c',root/'src/cd17.c',root/'src/sector27.c',root/'src/resident17.c']:run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(out),'-I',str(root/'src'),'-c',str(p),'-o',p.stem+'.o'])
    run(['ld.lld','-m','elf32ltsmip','-T',str(root/'src/dynamic13.ld'),'start.o','play65.o','cd17.o','sector27.o','resident17.o','-o','play65.elf']);run(['llvm-objcopy','-O','binary','play65.elf','play65.raw']);p=(out/'play65.raw').read_bytes();p+=bytes((-len(p))%2048);h=bytearray(2048);h[:8]=b'PS-X EXE';struct.pack_into('<IIII',h,16,0x80010000,0,0x80010000,len(p));struct.pack_into('<II',h,0x30,0x801fff00,0);exe=h+p;(out/'ETD_C65.EXE').write_bytes(exe)
    sectors=iso(exe,{n:(out/n).read_bytes() for n in ('CCCSECT.DAT','CCCSECT.IDX','CCCTEX.DAT','CCCTEX.IDX','CCCACT.DAT','CCCVOX.DAT','CCCBRN.DAT','CCCUFO.DAT')});directory=bytearray();pos=0
    while sectors[20][pos]:
        n=sectors[20][pos];rr=sectors[20][pos:pos+n];name=bytes(rr[33:33+rr[32]])
        if name==b'ETD_SECT.EXE;1':rr=record(b'ETD_C65.EXE;1',22,len(exe))
        if name==b'SYSTEM.CNF;1':
            cfg=b'BOOT = cdrom:\\ETD_C65.EXE;1\r\nTCB = 4\r\nEVENT = 10\r\nSTACK = 801FFF00\r\n';sectors[21][:]=cfg.ljust(2048,b'\0');rr=record(name,21,len(cfg))
        directory.extend(rr);pos+=n
    sectors[20][:]=directory.ljust(2048,b'\0');disc=b''.join(raw(i,p) for i,p in enumerate(sectors));(out/'ETD_C65.bin').write_bytes(disc);(out/'ETD_C65.cue').write_text('FILE "ETD_C65.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
    elf=(out/'play65.elf').read_bytes();off=struct.unpack_from('<I',elf,28)[0];sz,n=struct.unpack_from('<HH',elf,42);high=max(p[2]+p[5] for i in range(n) if (p:=struct.unpack_from('<8I',elf,off+i*sz))[0]==1);assert high<0x801e0000
    for i in range(len(sectors)):assert disc[i*2352:(i+1)*2352]==raw(i,sectors[i])
    rep=dict(exe_bytes=len(exe),linked_ram=high-0x80010000,headroom=0x801e0000-high,sectors=len(sectors),exe_sha256=hashlib.sha256(exe).hexdigest(),disc_sha256=hashlib.sha256(disc).hexdigest(),banks={n:hashlib.sha256((out/n).read_bytes()).hexdigest() for n in ('CCCSECT.DAT','CCCSECT.IDX','CCCTEX.DAT','CCCTEX.IDX','CCCACT.DAT','CCCVOX.DAT','CCCBRN.DAT','CCCUFO.DAT')});(out/'native_report65.json').write_text(json.dumps(rep,indent=2)+'\n');print(rep)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('old',type=Path);p.add_argument('sky',type=Path);p.add_argument('out',type=Path);a=p.parse_args();build(*(v.resolve() for v in (a.root,a.old,a.sky,a.out)))
