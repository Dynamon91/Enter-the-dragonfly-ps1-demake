"""Integrate source seabed fallback and original Luau switches and gates."""
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
    shutil.copyfile(old/'LIAOBJ.DAT',out/'LIAOBJ.DAT')
    for name in ('gatedata69.h','LIAGAT.DAT'):shutil.copyfile(visual/'gates'/name,out/name)
    for name in ('seabed69.h','gates69.h','gates_draw69.h'):shutil.copyfile(HERE/'src'/name,out/name)
    t=(out/'tex19.h').read_text();assert '#define TEXCAP19 62' in t;(out/'tex19.h').write_text(t.replace('#define TEXCAP19 62','#define TEXCAP19 57'))
    t=(out/'swim67.h').read_text();assert t.count('static int wet67(')==1;t=t.replace('static int wet67(', '#include "seabed69.h"\nstatic int wet67(').replace('if(f==NONE18||f<w+140||f>w+3200)return 0;', 'if(f==NONE18)f=seabed69(c,x,z,w);if(f==NONE18||f<w+140||f>w+3200)return 0;');(out/'swim67.h').write_text(t)
    data=(out/'LIASECT.DAT').read_bytes();idx=(out/'LIASECT.IDX').read_bytes();tex=(out/'LIATEX.DAT').read_bytes();ti=(out/'LIATEX.IDX').read_bytes()
    prev=json.loads((old/'report68.json').read_text());x,y,z=prev['spawn']
    s=(old/'play68.c').read_text()
    replacements=[('objextent68[2],textent[2]', 'objextent68[2],gateextent69[2],textent[2]'),('int found=iso17_find','if(!iso17_find(scratch,"LIAGAT.DAT;1",pvd[0],gateextent69)||gateextent69[1]!=30720)return 0;int found=iso17_find'),('static void step18(', 'static int gate_pass69(int,int,int,int,int);\nstatic void step18('),('if(mid!=NONE18&&f!=NONE18){','if(mid!=NONE18&&f!=NONE18&&gate_pass69(p->x,p->y,p->z,nx,nz)){'),('#include "luau_objects68.h"','#include "luau_objects68.h"\n#include "gates69.h"'),('#include "luau_draw68.h"','#include "luau_draw68.h"\n#include "gates_draw69.h"'),('draw_objects68(p,cx,cy,cz,sn,cs);','draw_objects68(p,cx,cy,cz,sn,cs);draw_gates69(p,cx,cy,cz,sn,cs);'),('else if(id>=PROP68_ID','else if(id>=GATE_ID69&&id<GATE_ID69+GATE_TEX69){int slot=57+id-GATE_ID69;gp(texwindow19(slot));gp(0x24808080);gp(packetxy(q,0));gp(q->uv[0]|(texclut19(slot)<<16));gp(packetxy(q,1));gp(q->uv[1]|(texpage19(slot)<<16));gp(packetxy(q,2));gp(q->uv[2]);}else if(id>=PROP68_ID'),('status=mount18()&&upload_props68()&&reset18','reset_gates69();status=mount18()&&upload_props68()&&upload_gates69()&&reset18'),('swim_step67(&p,btn,ax,az);','smash_input69(&p,btn);swim_step67(&p,btn,ax,az);'),('reset_objects68();sfx_stop();','reset_objects68();reset_gates69();sfx_stop();'),('objects_step68(&p,ox,oy,oz,btn,sine);','objects_step68(&p,ox,oy,oz,btn,sine);if(gates_step69(&p,ox,oz,btn,!objects68.mode))sfx_play(2);')]
    for a,b in replacements:
        assert s.count(a)==1,a;s=s.replace(a,b)
    (out/'play69.c').write_text(s)
    opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0'];run=lambda a:subprocess.run(a,cwd=out,check=True)
    run(opts+['-c',str(root/'src/dynamic13_start.s'),'-o','start.o'])
    for p in [out/'play69.c',root/'src/cd17.c',root/'src/sector27.c',root/'src/resident17.c']:run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(out),'-I',str(root/'src'),'-c',str(p),'-o',p.stem+'.o'])
    run(['ld.lld','-m','elf32ltsmip','-T',str(root/'src/dynamic13.ld'),'start.o','play69.o','cd17.o','sector27.o','resident17.o','-o','play69.elf']);run(['llvm-objcopy','-O','binary','play69.elf','play69.raw']);p=(out/'play69.raw').read_bytes();p+=bytes((-len(p))%2048);h=bytearray(2048);h[:8]=b'PS-X EXE';struct.pack_into('<IIII',h,16,0x80010000,0,0x80010000,len(p));struct.pack_into('<II',h,0x30,0x801fff00,0);exe=h+p;(out/'ETD_L69.EXE').write_bytes(exe)
    sectors=iso(exe,{'LIASECT.DAT':data,'LIASECT.IDX':idx,'LIATEX.DAT':tex,'LIATEX.IDX':ti,'LIAOBJ.DAT':(out/'LIAOBJ.DAT').read_bytes(),'LIAGAT.DAT':(out/'LIAGAT.DAT').read_bytes()});directory=bytearray();pos=0
    while sectors[20][pos]:
        n=sectors[20][pos];rr=sectors[20][pos:pos+n];name=bytes(rr[33:33+rr[32]])
        if name==b'ETD_SECT.EXE;1':rr=record(b'ETD_L69.EXE;1',22,len(exe))
        if name==b'SYSTEM.CNF;1':
            cfg=b'BOOT = cdrom:\\ETD_L69.EXE;1\r\nTCB = 4\r\nEVENT = 10\r\nSTACK = 801FFF00\r\n';sectors[21][:]=cfg.ljust(2048,b'\0');rr=record(name,21,len(cfg))
        directory.extend(rr);pos+=n
    sectors[20][:]=directory.ljust(2048,b'\0');disc=b''.join(raw(i,p) for i,p in enumerate(sectors));(out/'ETD_L69.bin').write_bytes(disc);(out/'ETD_L69.cue').write_text('FILE "ETD_L69.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
    elf=(out/'play69.elf').read_bytes();off=struct.unpack_from('<I',elf,28)[0];sz,n=struct.unpack_from('<HH',elf,42);high=max(p[2]+p[5] for i in range(n) if (p:=struct.unpack_from('<8I',elf,off+i*sz))[0]==1);assert high<0x801e0000
    rep=dict(spawn=[x,y,z],gems=prev["gems"],gem_value=prev["gem_value"],baskets=prev["baskets"],basket_value=prev["basket_value"],exe_bytes=len(exe),linked_ram=high-0x80010000,headroom=0x801e0000-high,sectors=len(sectors),exe_sha256=hashlib.sha256(exe).hexdigest(),disc_sha256=hashlib.sha256(disc).hexdigest());(out/'report69.json').write_text(json.dumps(rep,indent=2)+'\n');print(rep)
if __name__=='__main__':
 p=argparse.ArgumentParser();[p.add_argument(k,type=Path) for k in ('root','old','visual','out')];a=p.parse_args();build(*(v.resolve() for v in (a.root,a.old,a.visual,a.out)))
