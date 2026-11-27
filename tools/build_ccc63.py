"""Add original dragonfly models, capture and reward accounting to v0.62."""
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
    shutil.copyfile(sky/'dfdata63.h',out/'dfdata63.h')
    for n in ('capture63.h','capture_ui63.h'):shutil.copyfile(HERE/'src'/n,out/n)
    c=(out/'cache24.c').read_text();assert c.count('ARENA22 (460*1024)')==1;(out/'cache24.c').write_text(c.replace('ARENA22 (460*1024)','ARENA22 (192*1024)'))
    # Keep the source control points, insert one collision-proven waypoint for cow 2.
    barn=(out/'barn61.h').read_text()
    for a,b in [('segment,tick,steps,yaw;', 'segment,tick,steps,yaw,detour;'),('c->segment=c->tick=c->steps=0;', 'c->segment=c->tick=c->steps=c->detour=0;'),('int dx=d[0]-a[0],dy=d[1]-a[1],dz=d[2]-a[2];','static const short gapfix[3]={3840,-400,3770};if(i==1&&c->segment==3){if(c->detour)a=gapfix;else d=gapfix;}int dx=d[0]-a[0],dy=d[1]-a[1],dz=d[2]-a[2];'),('c->segment++;c->tick=c->steps=0;','if(i==1&&c->segment==3&&!c->detour)c->detour=1;else c->segment++;c->tick=c->steps=0;')]:
        assert barn.count(a)==1,a;barn=barn.replace(a,b)
    (out/'barn61.h').write_text(barn)
    s=(old/'play62.c').read_text()
    for a,b in [('#include "herd_ui62.h"','#include "herd_ui62.h"\n#include "capture_ui63.h"'),('herd_draw62(p,cx,cy,cz,sn,cs);','herd_draw62(p,cx,cy,cz,sn,cs);df_draw63(p,cx,cy,cz,sn,cs);'),('else if(id>=ACTOR_ID59','else if(id==BUB_ID63){gp(0xe1000400);gp(0x22f0d0a0);for(int j=0;j<3;j++)gp(packetxy(q,j));}else if(id>=ACTOR_ID59'),('herd_hud62(p);hud60(p);','herd_hud62(p);capture_hud63();hud60(p);'),('herd_reset62(&herd62);','herd_reset62(&herd62);capture_reset63(&capture63);'),('if(reset||!control60(&p,btn)){step18','if(reset||!control60(&p,btn)){if(!reset&&(btn&512)&&!(p.prev&512))capture63.mode^=1;step18'),('btn&PAD_CIRCLE,p.grounded,collect.sx','!capture63.mode&&(btn&PAD_CIRCLE),p.grounded,collect.sx'),('herd_step62(&p,ox,oz,btn&PAD_SQUARE);','herd_step62(&p,ox,oz,btn&PAD_SQUARE);capture_step63(&capture63,&talk60,&cache,p.x,p.y,p.z,p.ground,p.heading,btn&PAD_CIRCLE,sine);if(capture63.event)sfx_play(1);')]:
        assert a in s,a;s=s.replace(a,b)
    (out/'play63.c').write_text(s)
    opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0'];run=lambda a:subprocess.run(a,cwd=out,check=True)
    run(opts+['-c',str(root/'src/dynamic13_start.s'),'-o','start.o'])
    for p in [out/'play63.c',root/'src/cd17.c',root/'src/sector27.c',root/'src/resident17.c']:run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(out),'-I',str(root/'src'),'-c',str(p),'-o',p.stem+'.o'])
    run(['ld.lld','-m','elf32ltsmip','-T',str(root/'src/dynamic13.ld'),'start.o','play63.o','cd17.o','sector27.o','resident17.o','-o','play63.elf']);run(['llvm-objcopy','-O','binary','play63.elf','play63.raw']);p=(out/'play63.raw').read_bytes();p+=bytes((-len(p))%2048);h=bytearray(2048);h[:8]=b'PS-X EXE';struct.pack_into('<IIII',h,16,0x80010000,0,0x80010000,len(p));struct.pack_into('<II',h,0x30,0x801fff00,0);exe=h+p;(out/'ETD_C63.EXE').write_bytes(exe)
    sectors=iso(exe,{n:(out/n).read_bytes() for n in ('CCCSECT.DAT','CCCSECT.IDX','CCCTEX.DAT','CCCTEX.IDX','CCCACT.DAT','CCCVOX.DAT','CCCBRN.DAT')});directory=bytearray();pos=0
    while sectors[20][pos]:
        n=sectors[20][pos];rr=sectors[20][pos:pos+n];name=bytes(rr[33:33+rr[32]])
        if name==b'ETD_SECT.EXE;1':rr=record(b'ETD_C63.EXE;1',22,len(exe))
        if name==b'SYSTEM.CNF;1':
            cfg=b'BOOT = cdrom:\\ETD_C63.EXE;1\r\nTCB = 4\r\nEVENT = 10\r\nSTACK = 801FFF00\r\n';sectors[21][:]=cfg.ljust(2048,b'\0');rr=record(name,21,len(cfg))
        directory.extend(rr);pos+=n
    sectors[20][:]=directory.ljust(2048,b'\0');disc=b''.join(raw(i,p) for i,p in enumerate(sectors));(out/'ETD_C63.bin').write_bytes(disc);(out/'ETD_C63.cue').write_text('FILE "ETD_C63.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
    elf=(out/'play63.elf').read_bytes();off=struct.unpack_from('<I',elf,28)[0];sz,n=struct.unpack_from('<HH',elf,42);high=max(p[2]+p[5] for i in range(n) if (p:=struct.unpack_from('<8I',elf,off+i*sz))[0]==1);assert high<0x801e0000
    for i in range(len(sectors)):assert disc[i*2352:(i+1)*2352]==raw(i,sectors[i])
    rep=dict(exe_bytes=len(exe),linked_ram=high-0x80010000,headroom=0x801e0000-high,sectors=len(sectors),exe_sha256=hashlib.sha256(exe).hexdigest(),disc_sha256=hashlib.sha256(disc).hexdigest(),banks={n:hashlib.sha256((out/n).read_bytes()).hexdigest() for n in ('CCCSECT.DAT','CCCSECT.IDX','CCCTEX.DAT','CCCTEX.IDX','CCCACT.DAT','CCCVOX.DAT','CCCBRN.DAT')});(out/'native_report63.json').write_text(json.dumps(rep,indent=2)+'\n');print(rep)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('old',type=Path);p.add_argument('sky',type=Path);p.add_argument('out',type=Path);a=p.parse_args();build(*(v.resolve() for v in (a.root,a.old,a.sky,a.out)))
