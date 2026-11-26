"""Native Dojo sector inspection executable; unchanged hub gameplay on same disc."""
from pathlib import Path
import json,struct,subprocess
from disc16 import iso,raw,record
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build_m25/view';A=ROOT/'assets_m25'
def build():
 OUT.mkdir(parents=True,exist_ok=True);m=json.loads((A/'sector_manifest.json').read_text());r=json.loads((A/'sector_report.json').read_text());colors=[x['rgb'] for x in m['materials']];start=min((b for b in m['blocks'] if b['render']),key=lambda b:b['origin'][0]**2+b['origin'][2]**2)['id'];(OUT/'colors17.h').write_text('#define START17 %d\nstatic const unsigned colors17[]={%s};\n'%(start,','.join(str(r|g<<8|b<<16) for r,g,b in colors)))
 s=(ROOT/'src/view17.c').read_text().replace('HUBSECT','DOJOSECT').replace('ext[1]!=10456',f"ext[1]!={r['index_bytes']}").replace('next>=174)next=173',f"next>={r['blocks']})next={r['blocks']-1}").replace('#include "resident17.c"','#include "resident25.c"');(OUT/'view25.c').write_text(s)
 s=(ROOT/'src/resident17.c').read_text().replace('208,75653,6195',f"{r['materials']},{r['render_triangles']},{r['collision_candidates']}");(OUT/'resident25.c').write_text(s)
 opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0'];run=lambda a:subprocess.run(a,cwd=OUT,check=True)
 run(opts+['-c',str(ROOT/'src/dynamic13_start.s'),'-o','start.o'])
 for p in [OUT/'view25.c',ROOT/'src/cd17.c',ROOT/'src/sector16.c']:run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(OUT),'-c',str(p),'-o',p.stem+'.o'])
 run(['ld.lld','-m','elf32ltsmip','-T',str(ROOT/'src/dynamic13.ld'),'start.o','view25.o','cd17.o','sector16.o','-o','view25.elf']);run(['llvm-objcopy','-O','binary','view25.elf','view25.bin']);data=(OUT/'view25.bin').read_bytes();data+=bytes((-len(data))%2048);header=bytearray(2048);header[:8]=b'PS-X EXE';struct.pack_into('<IIII',header,16,0x80010000,0,0x80010000,len(data));struct.pack_into('<II',header,0x30,0x801fff00,0);e=header+data;(OUT/'ETD_DOJO.EXE').write_bytes(e)
 run(['clang','-O2','-shared','-fPIC',str(ROOT/'src/sector16.c'),str(OUT/'resident25.c'),str(ROOT/'src/cd17.c'),str(ROOT/'tests/cd17_mock.c'),'-DCD17_MOCK','-o','dojo25_host.so'])
 elf=(OUT/'view25.elf').read_bytes();off=struct.unpack_from('<I',elf,28)[0];sz,n=struct.unpack_from('<HH',elf,42);high=max(p[2]+p[5] for i in range(n) if (p:=struct.unpack_from('<8I',elf,off+i*sz))[0]==1);rep=dict(start=start,exe_bytes=len(e),linked_ram_from_load=high-0x80010000,headroom_to_stack_region=0x801e0000-high,mode='standalone diagnostic; no emulator execution');(OUT/'report.json').write_text(json.dumps(rep,indent=2));print(rep)
 # Boot Dojo viewer; keep unchanged hub executable and assets as fallback.
 assets={n:(ROOT/'assets_m16'/n).read_bytes() for n in ('HUBSECT.DAT','HUBSECT.IDX')};assets.update({n:(ROOT/'assets_m20'/n).read_bytes() for n in ('HUBTEX.DAT','HUBTEX.IDX')});assets.update({n:(A/n).read_bytes() for n in ('DOJOSECT.DAT','DOJOSECT.IDX','DOJOTEX.DAT','DOJOTEX.IDX')});assets['ETD_POOL.EXE']=(ROOT/'build_m24/play/ETD_POOL.EXE').read_bytes();s=iso(e,assets);root=bytearray();pos=0
 while s[20][pos]:
  n=s[20][pos];rr=s[20][pos:pos+n];name=bytes(rr[33:33+rr[32]])
  if name==b'ETD_SECT.EXE;1':rr=record(b'ETD_DOJO.EXE;1',22,len(e))
  if name==b'SYSTEM.CNF;1':
   config=b'BOOT = cdrom:\\ETD_DOJO.EXE;1\r\nTCB = 4\r\nEVENT = 10\r\nSTACK = 801FFF00\r\n';s[21][:]=config.ljust(2048,b'\0');rr=record(name,21,len(config))
  root.extend(rr);pos+=n
 s[20][:]=root.ljust(2048,b'\0');(OUT/'ETD_PSX_M25.bin').write_bytes(b''.join(raw(i,x) for i,x in enumerate(s)));(OUT/'ETD_PSX_M25.cue').write_text('FILE "ETD_PSX_M25.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n');print('sectors',len(s))
if __name__=='__main__':build()
