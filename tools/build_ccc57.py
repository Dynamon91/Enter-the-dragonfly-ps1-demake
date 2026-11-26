"""Adapt the authentic m29 traversal engine to the recovered CCC terrain bank.
No Dojo-specific enemy or sky assets. Original spawn and direct gem IDs retained.
"""
import argparse,json,struct,subprocess,zlib,shutil,sys,re,hashlib
from pathlib import Path
import numpy as np

def build(root,assets,bank,out):
    sys.path.insert(0,str(root/'tools'));from disc16 import iso,raw,record
    out.mkdir(parents=True,exist_ok=False);old=root/'build_m29/play';report=json.loads((bank/'report.json').read_text());bindings=json.loads((assets/'bindings.json').read_text());objects=bindings['objects'];materials=bindings['materials']
    for p in old.glob('*.h'):shutil.copyfile(p,out/p.name)
    def replace(text,a,b):
        if a not in text:raise ValueError('missing base token: '+a)
        return text.replace(a,b)
    def edit(name,pairs):
        s=(old/name).read_text()
        for a,b in pairs:s=replace(s,a,b)
        (out/name).write_text(s)
    start=[o for o in objects if o['name']=='__CNODESpyro' and o['edf']=='default.edf'];assert len(start)==1
    x,y,z=map(int,np.rint(np.array(start[0]['source_xyz'])*[1,-1,1]));gems=sorted((o['source_id'],o['value']) for o in objects if o['kind']==1);assert len(gems)==146 and sum(v for _,v in gems)==569
    baskets=sorted((o['source_id'],int(re.fullmatch(r'basket(\d+)\.edf',o['edf'],re.I)[1])) for o in objects if re.fullmatch(r'basket(\d+)\.edf',o['edf'],re.I));nb=len(baskets);bd=dict(baskets)
    arr=lambda a:','.join(map(str,a));(out/'gemids20.h').write_text(f'static const U32 gemids20[{len(gems)}]={{'+arr(i for i,v in gems)+'};\n'+f'static const U8 gemvalues20[{len(gems)}]={{'+arr(v for i,v in gems)+'};\n')
    (out/'objectids21.h').write_text(f'static const U32 objectids21[{nb+1}]={{'+arr(i for i,v in baskets)+',0xffffffffu};\n'+f'static const U8 basketvalue29[{nb}]={{'+arr(v for i,v in baskets)+'};\n')
    edit('collect21.h',[('GEM20_COUNT 193',f'GEM20_COUNT {len(gems)}')]);edit('interact21.h',[('OBJ21 91',f'OBJ21 {nb+1}'),('BASK21 90',f'BASK21 {nb}')])
    idx=bytearray((bank/'LEVEL.IDX').read_bytes());data=bytearray((bank/'LEVEL.DAT').read_bytes());marked=set()
    for i in range(report['blocks']):
        e=struct.unpack_from('<IIII3i6i3H2x',idx,16+60*i);off=e[1]*2048;size=e[2];startobj=off+64+36*e[13]+24*e[14]
        for j in range(e[15]):
            p=startobj+16*j;oid=struct.unpack_from('<I',data,p+12)[0]
            if oid in bd:struct.pack_into('<H',data,p+6,2);marked.add(oid)
        crc=zlib.crc32(data[off+64:off+size]);struct.pack_into('<I',data,off+36,crc);struct.pack_into('<I',idx,16+60*i+12,crc)
    assert marked==set(bd);(out/'CCCSECT.DAT').write_bytes(data);(out/'CCCSECT.IDX').write_bytes(idx)
    # 160 KiB maximum neighborhood in v56, retaining 460 KiB legacy cap.
    edit('cache24.c',[('BLOCKS18 446',f"BLOCKS18 {report['blocks']}"),('MAT18 53',f"MAT18 {report['materials']}"),('MAT18,127733,7035',f"MAT18,{report['render']},{report['collision']}")]);edit('tex19.h',[('TEXCOUNT19 52','TEXCOUNT19 41')])
    tex=(assets/'CCCTEX.DAT').read_bytes();ti=(assets/'CCCTEX.IDX').read_bytes();colors={}
    for i in range((len(ti)-12)//12):
        g,lba,crc=struct.unpack_from('<III',ti,12+i*12);p=tex[lba*2048:lba*2048+6144];assert zlib.crc32(p[24:4632])==crc;pal=np.frombuffer(p[24:536],'<u2');pix=np.frombuffer(p[536:4632],np.uint8);v=pal[pix];rgb=np.rint(np.array([(v&31).mean(),((v>>5)&31).mean(),((v>>10)&31).mean()])*255/31).astype(int);colors[g]=int(rgb[0]|rgb[1]<<8|rgb[2]<<16)
    (out/'colors17.h').write_text('static const unsigned colors17[]={'+arr(colors[m['group']] for m in materials)+'};\n');(out/'groups19.h').write_text('static const short groups19[MAT18]={'+arr(m['group'] for m in materials)+'};\n')
    # Remove original Dojo-specific enemy/sky routines; generic movement/fire/gems remain.
    s=(old/'play29.c').read_text();a=s.index('static void renderenemy29(');b=s.index('static void render18(',a);s=s[:a]+s[b:]
    for a,b in [('#include "enemy29.h"\n',''),('#include "ninjamesh29.h"\n',''),('#include "sky28.h"\n',''),('sky_draw28(sn,cs);',''),('sky_upload28();',''),('renderenemy29(p,cx,cy,cz,sn,cs);',''),('enemy_reset29();',''),('enemy_step29(&interactions,&cache,p.x,p.y,p.z,ox,oz,btn&PAD_SQUARE,p.grounded);',''),('DOJOSECT','CCCSECT'),('DOJOTEX','CCCTEX'),('26776',str(len(idx))),('idx[28672]',f'idx[{(len(idx)+2047)//2048*2048}]'),('10534,-14914,-2075',f'{x},{z},{y}'),('10534,-14914',f'{x},{z}'),('10534,f,-14914',f'{x},f,{z}'),('10534,-2075,-14914,-2075',f'{x},{y},{z},{y}'),('8435960u','0x64513bu')]:s=replace(s,a,b)
    # Strict mount: do not start on missing/invalid original texture bank.
    s=replace(s,'texready=texindex19(tidx,tdir[1],textent[1]/2048);return 1;','texready=texindex19(tidx,tdir[1],textent[1]/2048);return texready;')
    (out/'play57.c').write_text(s)
    opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0'];run=lambda a:subprocess.run(a,cwd=out,check=True)
    run(opts+['-c',str(root/'src/dynamic13_start.s'),'-o','start.o'])
    for p in [out/'play57.c',root/'src/cd17.c',root/'src/sector27.c',root/'src/resident17.c']:run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(out),'-I',str(root/'src'),'-c',str(p),'-o',p.stem+'.o'])
    run(['ld.lld','-m','elf32ltsmip','-T',str(root/'src/dynamic13.ld'),'start.o','play57.o','cd17.o','sector27.o','resident17.o','-o','play57.elf']);run(['llvm-objcopy','-O','binary','play57.elf','play57.raw']);p=(out/'play57.raw').read_bytes();p+=bytes((-len(p))%2048);h=bytearray(2048);h[:8]=b'PS-X EXE';struct.pack_into('<IIII',h,16,0x80010000,0,0x80010000,len(p));struct.pack_into('<II',h,0x30,0x801fff00,0);exe=h+p;(out/'ETD_C57.EXE').write_bytes(exe)
    sectors=iso(exe,{'CCCSECT.DAT':data,'CCCSECT.IDX':idx,'CCCTEX.DAT':tex,'CCCTEX.IDX':ti});directory=bytearray();pos=0
    while sectors[20][pos]:
        n=sectors[20][pos];rr=sectors[20][pos:pos+n];name=bytes(rr[33:33+rr[32]])
        if name==b'ETD_SECT.EXE;1':rr=record(b'ETD_C57.EXE;1',22,len(exe))
        if name==b'SYSTEM.CNF;1':
            cfg=b'BOOT = cdrom:\\ETD_C57.EXE;1\r\nTCB = 4\r\nEVENT = 10\r\nSTACK = 801FFF00\r\n';sectors[21][:]=cfg.ljust(2048,b'\0');rr=record(name,21,len(cfg))
        directory.extend(rr);pos+=n
    sectors[20][:]=directory.ljust(2048,b'\0');(out/'ETD_C57.bin').write_bytes(b''.join(raw(i,p) for i,p in enumerate(sectors)));(out/'ETD_C57.cue').write_text('FILE "ETD_C57.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
    elf=(out/'play57.elf').read_bytes();off=struct.unpack_from('<I',elf,28)[0];sz,n=struct.unpack_from('<HH',elf,42);high=max(p[2]+p[5] for i in range(n) if (p:=struct.unpack_from('<8I',elf,off+i*sz))[0]==1)
    rep=dict(spawn=[x,y,z],direct_gems=len(gems),direct_gem_value=sum(v for i,v in gems),basket_placements=nb,basket_reward_value=sum(v for i,v in baskets),exe_bytes=len(exe),linked_ram=high-0x80010000,headroom=0x801e0000-high,sectors=len(sectors),mode='native traversal prototype, original terrain and opaque base textures; no emulator run');(out/'report57.json').write_text(json.dumps(rep,indent=2));print(rep)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('assets',type=Path);p.add_argument('bank',type=Path);p.add_argument('out',type=Path);a=p.parse_args();build(*(v.resolve() for v in (a.root,a.assets,a.bank,a.out)))
