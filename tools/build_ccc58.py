"""Add original CCC sky pass to the previously built v0.57 traversal checkpoint."""
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
    # Recover the byte-identical CCC texture banks directly from prior authored disc.
    from cnk import ISO
    image=(old/'ETD_C57.bin').read_bytes();logical=out/'prior.iso';logical.write_bytes(b''.join(image[i+24:i+2072] for i in range(0,len(image),2352)))
    with ISO(logical) as d:
        for n in ('CCCTEX.DAT','CCCTEX.IDX'):(out/n).write_bytes(d.file(n))
    logical.unlink()
    shutil.copyfile(sky/'skydata58.h',out/'skydata58.h');shutil.copyfile(HERE/'src/sky58.h',out/'sky58.h')
    s=(old/'play57.c').read_text()
    for a,b in [('static void refresh19(void)','#include "sky58.h"\nstatic void refresh19(void)'),('gp((240<<16)|320);for(int b=','gp((240<<16)|320);sky_draw58(sn,cs);for(int b='),('gp(0x02000000|0x64513bu);','gp(0x02000000|0x180804u);'),('idle();status=mount18()','idle();sky_upload58();status=mount18()')]:
        assert s.count(a)==1,a;s=s.replace(a,b)
    (out/'play58.c').write_text(s)
    opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0'];run=lambda a:subprocess.run(a,cwd=out,check=True)
    run(opts+['-c',str(root/'src/dynamic13_start.s'),'-o','start.o'])
    for p in [out/'play58.c',root/'src/cd17.c',root/'src/sector27.c',root/'src/resident17.c']:run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(out),'-I',str(root/'src'),'-c',str(p),'-o',p.stem+'.o'])
    run(['ld.lld','-m','elf32ltsmip','-T',str(root/'src/dynamic13.ld'),'start.o','play58.o','cd17.o','sector27.o','resident17.o','-o','play58.elf']);run(['llvm-objcopy','-O','binary','play58.elf','play58.raw']);p=(out/'play58.raw').read_bytes();p+=bytes((-len(p))%2048);h=bytearray(2048);h[:8]=b'PS-X EXE';struct.pack_into('<IIII',h,16,0x80010000,0,0x80010000,len(p));struct.pack_into('<II',h,0x30,0x801fff00,0);exe=h+p;(out/'ETD_C58.EXE').write_bytes(exe)
    sectors=iso(exe,{n:(out/n).read_bytes() for n in ('CCCSECT.DAT','CCCSECT.IDX','CCCTEX.DAT','CCCTEX.IDX')});directory=bytearray();pos=0
    while sectors[20][pos]:
        n=sectors[20][pos];rr=sectors[20][pos:pos+n];name=bytes(rr[33:33+rr[32]])
        if name==b'ETD_SECT.EXE;1':rr=record(b'ETD_C58.EXE;1',22,len(exe))
        if name==b'SYSTEM.CNF;1':
            cfg=b'BOOT = cdrom:\\ETD_C58.EXE;1\r\nTCB = 4\r\nEVENT = 10\r\nSTACK = 801FFF00\r\n';sectors[21][:]=cfg.ljust(2048,b'\0');rr=record(name,21,len(cfg))
        directory.extend(rr);pos+=n
    sectors[20][:]=directory.ljust(2048,b'\0');disc=b''.join(raw(i,p) for i,p in enumerate(sectors));(out/'ETD_C58.bin').write_bytes(disc);(out/'ETD_C58.cue').write_text('FILE "ETD_C58.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
    elf=(out/'play58.elf').read_bytes();off=struct.unpack_from('<I',elf,28)[0];sz,n=struct.unpack_from('<HH',elf,42);high=max(p[2]+p[5] for i in range(n) if (p:=struct.unpack_from('<8I',elf,off+i*sz))[0]==1);assert high<0x801e0000
    for i in range(len(sectors)):assert disc[i*2352:(i+1)*2352]==raw(i,sectors[i])
    rep=dict(exe_bytes=len(exe),linked_ram=high-0x80010000,headroom=0x801e0000-high,sectors=len(sectors),exe_sha256=hashlib.sha256(exe).hexdigest(),disc_sha256=hashlib.sha256(disc).hexdigest(),banks={n:hashlib.sha256((out/n).read_bytes()).hexdigest() for n in ('CCCSECT.DAT','CCCSECT.IDX','CCCTEX.DAT','CCCTEX.IDX')});(out/'native_report58.json').write_text(json.dumps(rep,indent=2)+'\n');print(rep)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('old',type=Path);p.add_argument('sky',type=Path);p.add_argument('out',type=Path);a=p.parse_args();build(*(v.resolve() for v in (a.root,a.old,a.sky,a.out)))
