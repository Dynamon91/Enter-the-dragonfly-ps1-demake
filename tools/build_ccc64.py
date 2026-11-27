"""Add source-defined UFO challenge to v0.63."""
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
    shutil.copyfile(sky/'ufodata64.h',out/'ufodata64.h')
    shutil.copyfile(sky/'CCCUFO.DAT',out/'CCCUFO.DAT')
    for n in ('ufo64.h','ufo_ui64.h'):shutil.copyfile(HERE/'src'/n,out/n)
    c=(out/'capture63.h').read_text();assert c.count('if(s->mode&&firing')==1;(out/'capture63.h').write_text(c.replace('if(s->mode&&firing','if(s->mode==1&&firing'))
    c=(out/'capture_ui63.h').read_text();assert c.count('capture63.mode?"BUBBLE":"FIRE"')==1;(out/'capture_ui63.h').write_text(c.replace('capture63.mode?"BUBBLE":"FIRE"','capture63.mode==2?"LIGHTNING":capture63.mode?"BUBBLE":"FIRE"'))
    s=(old/'play63.c').read_text()
    for a,b in [('barn_extent61[2];','barn_extent61[2],ufo_extent64[2];'),('barn_extent61[1]!=18432','!iso17_find(scratch,"CCCUFO.DAT;1",pvd[0],ufo_extent64)||ufo_extent64[1]!=%d||barn_extent61[1]!=18432'% (out/'CCCUFO.DAT').stat().st_size),('#include "capture_ui63.h"','#include "capture_ui63.h"\n#include "ufo_ui64.h"'),('df_draw63(p,cx,cy,cz,sn,cs);','df_draw63(p,cx,cy,cz,sn,cs);ufo_draw64(p,cx,cy,cz,sn,cs);'),('else if(id>=ACTOR_ID59','else if(id>=UFO_ID64&&id<UFO_ID64+UFO_TEX64){int slot=51+id-UFO_ID64;gp(texwindow19(slot));gp(0x24808080);gp(packetxy(q,0));gp(q->uv[0]|(texclut19(slot)<<16));gp(packetxy(q,1));gp(q->uv[1]|(texpage19(slot)<<16));gp(packetxy(q,2));gp(q->uv[2]);}else if(id>=ACTOR_ID59'),('capture_hud63();hud60(p);','capture_hud63();ufo_hud64(p);hud60(p);'),('barn_upload61()&&reset18','barn_upload61()&&ufo_upload64()&&reset18'),('capture_reset63(&capture63);','capture_reset63(&capture63);reset_ufo64();'),('capture63.mode^=1','capture63.mode=(capture63.mode+1)%3'),('capture_step63(&capture63,','ufo_step64(&p,capture63.mode,btn&PAD_CIRCLE);capture_step63(&capture63,')]:
        assert a in s,a;s=s.replace(a,b)
    (out/'play64.c').write_text(s)
    opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0'];run=lambda a:subprocess.run(a,cwd=out,check=True)
    run(opts+['-c',str(root/'src/dynamic13_start.s'),'-o','start.o'])
    for p in [out/'play64.c',root/'src/cd17.c',root/'src/sector27.c',root/'src/resident17.c']:run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(out),'-I',str(root/'src'),'-c',str(p),'-o',p.stem+'.o'])
    run(['ld.lld','-m','elf32ltsmip','-T',str(root/'src/dynamic13.ld'),'start.o','play64.o','cd17.o','sector27.o','resident17.o','-o','play64.elf']);run(['llvm-objcopy','-O','binary','play64.elf','play64.raw']);p=(out/'play64.raw').read_bytes();p+=bytes((-len(p))%2048);h=bytearray(2048);h[:8]=b'PS-X EXE';struct.pack_into('<IIII',h,16,0x80010000,0,0x80010000,len(p));struct.pack_into('<II',h,0x30,0x801fff00,0);exe=h+p;(out/'ETD_C64.EXE').write_bytes(exe)
    sectors=iso(exe,{n:(out/n).read_bytes() for n in ('CCCSECT.DAT','CCCSECT.IDX','CCCTEX.DAT','CCCTEX.IDX','CCCACT.DAT','CCCVOX.DAT','CCCBRN.DAT','CCCUFO.DAT')});directory=bytearray();pos=0
    while sectors[20][pos]:
        n=sectors[20][pos];rr=sectors[20][pos:pos+n];name=bytes(rr[33:33+rr[32]])
        if name==b'ETD_SECT.EXE;1':rr=record(b'ETD_C64.EXE;1',22,len(exe))
        if name==b'SYSTEM.CNF;1':
            cfg=b'BOOT = cdrom:\\ETD_C64.EXE;1\r\nTCB = 4\r\nEVENT = 10\r\nSTACK = 801FFF00\r\n';sectors[21][:]=cfg.ljust(2048,b'\0');rr=record(name,21,len(cfg))
        directory.extend(rr);pos+=n
    sectors[20][:]=directory.ljust(2048,b'\0');disc=b''.join(raw(i,p) for i,p in enumerate(sectors));(out/'ETD_C64.bin').write_bytes(disc);(out/'ETD_C64.cue').write_text('FILE "ETD_C64.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
    elf=(out/'play64.elf').read_bytes();off=struct.unpack_from('<I',elf,28)[0];sz,n=struct.unpack_from('<HH',elf,42);high=max(p[2]+p[5] for i in range(n) if (p:=struct.unpack_from('<8I',elf,off+i*sz))[0]==1);assert high<0x801e0000
    for i in range(len(sectors)):assert disc[i*2352:(i+1)*2352]==raw(i,sectors[i])
    rep=dict(exe_bytes=len(exe),linked_ram=high-0x80010000,headroom=0x801e0000-high,sectors=len(sectors),exe_sha256=hashlib.sha256(exe).hexdigest(),disc_sha256=hashlib.sha256(disc).hexdigest(),banks={n:hashlib.sha256((out/n).read_bytes()).hexdigest() for n in ('CCCSECT.DAT','CCCSECT.IDX','CCCTEX.DAT','CCCTEX.IDX','CCCACT.DAT','CCCVOX.DAT','CCCBRN.DAT','CCCUFO.DAT')});(out/'native_report64.json').write_text(json.dumps(rep,indent=2)+'\n');print(rep)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('old',type=Path);p.add_argument('sky',type=Path);p.add_argument('out',type=Path);a=p.parse_args();build(*(v.resolve() for v in (a.root,a.old,a.sky,a.out)))
