"""Add the original CCC barn rescue to v0.60 traversal."""
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
    shutil.copyfile(sky/'CCCACT.DAT',out/'CCCBRN.DAT');shutil.copyfile(sky/'barndata61.h',out/'barndata61.h')
    for n in ('barn61.h','barn_ui61.h'):shutil.copyfile(HERE/'src'/n,out/n)
    a=(out/'actors59.h').read_text();assert a.count('if(!actor_visible59')==1;a=a.replace('if(!actor_visible59','if(a->model==0&&!herd_visible61())continue;if(!actor_visible59');(out/'actors59.h').write_text(a)
    s=(old/'play60.c').read_text()
    for a,b in [('static U32 actor_extent59[2],voice_extent60[2];','static U32 actor_extent59[2],voice_extent60[2],barn_extent61[2];'),('actor_extent59[1]!=43008','!iso17_find(scratch,"CCCBRN.DAT;1",pvd[0],barn_extent61)||barn_extent61[1]!=18432||actor_extent59[1]!=43008'),('static void step18(','static int doorpass61(int,int,int,int,int);\nstatic void step18('),('if(mid!=NONE18&&f!=NONE18){','if(mid!=NONE18&&f!=NONE18&&doorpass61(p->x,p->y,p->z,nx,nz)){'),('#include "actors59.h"\n#include "talk_ui60.h"','#include "talk_ui60.h"\nstatic int herd_visible61(void){return flag60(talk60.flags[0],7);}\n#include "actors59.h"\n#include "barn_ui61.h"'),('renderactors59(p,cx,cy,cz,sn,cs);','renderactors59(p,cx,cy,cz,sn,cs);barn_draw61(p,cx,cy,cz,sn,cs);'),('id<ACTOR_ID59+7','id<ACTOR_ID59+10'),('hud60(p);idle();','barn_hud61(p);hud60(p);idle();'),('status=mount18()&&actor_upload59()&&reset18','status=mount18()&&actor_upload59()&&barn_upload61()&&reset18'),('reset60(&talk60);','reset60(&talk60);barn_reset61(&barn61,escape61);'),('if(interactions.broken)sfx_play(2);','if(interactions.broken)sfx_play(2);queststep61(&p);')]:
        assert a in s,a;s=s.replace(a,b)
    (out/'play61.c').write_text(s)
    opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0'];run=lambda a:subprocess.run(a,cwd=out,check=True)
    run(opts+['-c',str(root/'src/dynamic13_start.s'),'-o','start.o'])
    for p in [out/'play61.c',root/'src/cd17.c',root/'src/sector27.c',root/'src/resident17.c']:run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(out),'-I',str(root/'src'),'-c',str(p),'-o',p.stem+'.o'])
    run(['ld.lld','-m','elf32ltsmip','-T',str(root/'src/dynamic13.ld'),'start.o','play61.o','cd17.o','sector27.o','resident17.o','-o','play61.elf']);run(['llvm-objcopy','-O','binary','play61.elf','play61.raw']);p=(out/'play61.raw').read_bytes();p+=bytes((-len(p))%2048);h=bytearray(2048);h[:8]=b'PS-X EXE';struct.pack_into('<IIII',h,16,0x80010000,0,0x80010000,len(p));struct.pack_into('<II',h,0x30,0x801fff00,0);exe=h+p;(out/'ETD_C61.EXE').write_bytes(exe)
    sectors=iso(exe,{n:(out/n).read_bytes() for n in ('CCCSECT.DAT','CCCSECT.IDX','CCCTEX.DAT','CCCTEX.IDX','CCCACT.DAT','CCCVOX.DAT','CCCBRN.DAT')});directory=bytearray();pos=0
    while sectors[20][pos]:
        n=sectors[20][pos];rr=sectors[20][pos:pos+n];name=bytes(rr[33:33+rr[32]])
        if name==b'ETD_SECT.EXE;1':rr=record(b'ETD_C61.EXE;1',22,len(exe))
        if name==b'SYSTEM.CNF;1':
            cfg=b'BOOT = cdrom:\\ETD_C61.EXE;1\r\nTCB = 4\r\nEVENT = 10\r\nSTACK = 801FFF00\r\n';sectors[21][:]=cfg.ljust(2048,b'\0');rr=record(name,21,len(cfg))
        directory.extend(rr);pos+=n
    sectors[20][:]=directory.ljust(2048,b'\0');disc=b''.join(raw(i,p) for i,p in enumerate(sectors));(out/'ETD_C61.bin').write_bytes(disc);(out/'ETD_C61.cue').write_text('FILE "ETD_C61.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
    elf=(out/'play61.elf').read_bytes();off=struct.unpack_from('<I',elf,28)[0];sz,n=struct.unpack_from('<HH',elf,42);high=max(p[2]+p[5] for i in range(n) if (p:=struct.unpack_from('<8I',elf,off+i*sz))[0]==1);assert high<0x801e0000
    for i in range(len(sectors)):assert disc[i*2352:(i+1)*2352]==raw(i,sectors[i])
    rep=dict(exe_bytes=len(exe),linked_ram=high-0x80010000,headroom=0x801e0000-high,sectors=len(sectors),exe_sha256=hashlib.sha256(exe).hexdigest(),disc_sha256=hashlib.sha256(disc).hexdigest(),banks={n:hashlib.sha256((out/n).read_bytes()).hexdigest() for n in ('CCCSECT.DAT','CCCSECT.IDX','CCCTEX.DAT','CCCTEX.IDX','CCCACT.DAT','CCCVOX.DAT','CCCBRN.DAT')});(out/'native_report61.json').write_text(json.dumps(rep,indent=2)+'\n');print(rep)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('old',type=Path);p.add_argument('sky',type=Path);p.add_argument('out',type=Path);a=p.parse_args();build(*(v.resolve() for v in (a.root,a.old,a.sky,a.out)))
