"""Integrate recovered Luau sky, indexed water alpha and bounded swimming."""
import argparse,json,struct,subprocess,shutil,sys,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
def build(root,old,visual,out):
    sys.path.insert(0,str(root/'tools'));from disc16 import iso,raw,record
    out.mkdir(parents=True,exist_ok=False)
    for p in old.glob('*.h'):shutil.copyfile(p,out/p.name)
    shutil.copyfile(old/'cache24.c',out/'cache24.c')
    for name in ('LIASECT.DAT','LIASECT.IDX'):shutil.copyfile(old/name,out/name)
    for name in ('LIATEX.DAT','LIATEX.IDX','skydata67.h','watermat67.h'):shutil.copyfile(visual/name,out/name)
    for name in ('sky67.h','swim67.h'):shutil.copyfile(HERE/'src'/name,out/name)
    data=(out/'LIASECT.DAT').read_bytes();idx=(out/'LIASECT.IDX').read_bytes();tex=(out/'LIATEX.DAT').read_bytes();ti=(out/'LIATEX.IDX').read_bytes()
    prev=json.loads((old/'report66.json').read_text());x,y,z=prev['spawn']
    s=(old/'play66.c').read_text()
    for a,b in [('#define NFACE20','#include "swim67.h"\n#include "sky67.h"\n#define NFACE20'),('gp((240<<16)|320);for(int b=', 'gp((240<<16)|320);sky_draw67(sn,cs);for(int b='),('gp(texwindow19(slot));gp(0x24808080);','gp(texwindow19(slot));gp(watermat67(id)?0x26808080:0x24808080);'),('idle();status=mount18()','idle();sky_upload67();swim_reset67();status=mount18()'),('step18(&p,btn,ax,az);','swim_step67(&p,btn,ax,az);'),('btn&PAD_CIRCLE,p.grounded','!swim67.active&&(btn&PAD_CIRCLE),p.grounded'),('anim_step(&a,p.x!=ox||p.z!=oz,btn,was,p.grounded,p.vy,','anim_step(&a,p.x!=ox||p.z!=oz,swim67.active?PAD_CROSS:btn,was,p.grounded,swim67.active?1:p.vy,'),('rect(302,8,10,10,status?0x37bd4a:0x3030ee);','rect(302,8,10,10,status?0x37bd4a:0x3030ee);if(swim67.active){rect(251,40,60,8,0x252027);rect(251,40,60*(p->y-swim67.surface)/(swim67.bed-swim67.surface),8,0xf0b050);}'),('gp(0x02000000|0xd3b98au);','gp(0x02000000|0xd3b98au);')]:
        assert s.count(a)==1,a;s=s.replace(a,b)
    (out/'play67.c').write_text(s)
    opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0'];run=lambda a:subprocess.run(a,cwd=out,check=True)
    run(opts+['-c',str(root/'src/dynamic13_start.s'),'-o','start.o'])
    for p in [out/'play67.c',root/'src/cd17.c',root/'src/sector27.c',root/'src/resident17.c']:run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(out),'-I',str(root/'src'),'-c',str(p),'-o',p.stem+'.o'])
    run(['ld.lld','-m','elf32ltsmip','-T',str(root/'src/dynamic13.ld'),'start.o','play67.o','cd17.o','sector27.o','resident17.o','-o','play67.elf']);run(['llvm-objcopy','-O','binary','play67.elf','play67.raw']);p=(out/'play67.raw').read_bytes();p+=bytes((-len(p))%2048);h=bytearray(2048);h[:8]=b'PS-X EXE';struct.pack_into('<IIII',h,16,0x80010000,0,0x80010000,len(p));struct.pack_into('<II',h,0x30,0x801fff00,0);exe=h+p;(out/'ETD_L67.EXE').write_bytes(exe)
    sectors=iso(exe,{'LIASECT.DAT':data,'LIASECT.IDX':idx,'LIATEX.DAT':tex,'LIATEX.IDX':ti});directory=bytearray();pos=0
    while sectors[20][pos]:
        n=sectors[20][pos];rr=sectors[20][pos:pos+n];name=bytes(rr[33:33+rr[32]])
        if name==b'ETD_SECT.EXE;1':rr=record(b'ETD_L67.EXE;1',22,len(exe))
        if name==b'SYSTEM.CNF;1':
            cfg=b'BOOT = cdrom:\\ETD_L67.EXE;1\r\nTCB = 4\r\nEVENT = 10\r\nSTACK = 801FFF00\r\n';sectors[21][:]=cfg.ljust(2048,b'\0');rr=record(name,21,len(cfg))
        directory.extend(rr);pos+=n
    sectors[20][:]=directory.ljust(2048,b'\0');disc=b''.join(raw(i,p) for i,p in enumerate(sectors));(out/'ETD_L67.bin').write_bytes(disc);(out/'ETD_L67.cue').write_text('FILE "ETD_L67.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
    elf=(out/'play67.elf').read_bytes();off=struct.unpack_from('<I',elf,28)[0];sz,n=struct.unpack_from('<HH',elf,42);high=max(p[2]+p[5] for i in range(n) if (p:=struct.unpack_from('<8I',elf,off+i*sz))[0]==1);assert high<0x801e0000
    rep=dict(spawn=[x,y,z],gems=prev["gems"],gem_value=prev["gem_value"],baskets=prev["baskets"],basket_value=prev["basket_value"],exe_bytes=len(exe),linked_ram=high-0x80010000,headroom=0x801e0000-high,sectors=len(sectors),exe_sha256=hashlib.sha256(exe).hexdigest(),disc_sha256=hashlib.sha256(disc).hexdigest());(out/'report67.json').write_text(json.dumps(rep,indent=2)+'\n');print(rep)
if __name__=='__main__':
 p=argparse.ArgumentParser();[p.add_argument(k,type=Path) for k in ('root','old','visual','out')];a=p.parse_args();build(*(v.resolve() for v in (a.root,a.old,a.visual,a.out)))
