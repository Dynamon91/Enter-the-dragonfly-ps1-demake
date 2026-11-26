"""Build separate native sector inspection executable; preserve v0.16 farm runtime."""
from pathlib import Path
import json,struct,subprocess
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build_m17/view';A=ROOT/'assets_m16'
def build():
 OUT.mkdir(parents=True,exist_ok=True);m=json.loads((A/'sector_manifest.json').read_text());t=json.loads((A/'texture_report.json').read_text());rgb={x['group']:x['average_rgb'] for x in t['entries']};colors=[rgb.get(x['texture_group'],[190,110,155]) for x in m['materials']];start=min((b for b in m['blocks'] if b['render']),key=lambda b:(b['origin'][0]-36848)**2+(b['origin'][2]+1200)**2)['id'];(OUT/'colors17.h').write_text('#define START17 %d\nstatic const unsigned colors17[]={%s};\n'%(start,','.join(str(r|g<<8|b<<16) for r,g,b in colors)))
 opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0'];run=lambda a:subprocess.run(a,cwd=OUT,check=True)
 run(opts+['-c',str(ROOT/'src/dynamic13_start.s'),'-o','start.o'])
 for s in ['view17','cd17','sector16']:run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(OUT),'-c',str(ROOT/f'src/{s}.c'),'-o',s+'.o'])
 run(['ld.lld','-m','elf32ltsmip','-T',str(ROOT/'src/dynamic13.ld'),'start.o','view17.o','cd17.o','sector16.o','-o','view17.elf']);run(['llvm-objcopy','-O','binary','view17.elf','view17.bin']);data=(OUT/'view17.bin').read_bytes();data+=bytes((-len(data))%2048);header=bytearray(2048);header[:8]=b'PS-X EXE';struct.pack_into('<IIII',header,16,0x80010000,0,0x80010000,len(data));struct.pack_into('<II',header,0x30,0x801fff00,0);(OUT/'ETD_CD.EXE').write_bytes(header+data)
 run(['clang','-O2','-shared','-fPIC','-DCD17_MOCK',str(ROOT/'src/cd17.c'),str(ROOT/'src/sector16.c'),str(ROOT/'src/resident17.c'),str(ROOT/'tests/cd17_mock.c'),'-o','cd17_host.so']);
 elf=(OUT/'view17.elf').read_bytes();off=struct.unpack_from('<I',elf,28)[0];sz,n=struct.unpack_from('<HH',elf,42);high=max(p[2]+p[5] for i in range(n) if (p:=struct.unpack_from('<8I',elf,off+i*sz))[0]==1);rep=dict(start=start,exe_bytes=len(data)+2048,linked_ram_from_load=high-0x80010000,headroom_to_stack_region=0x801e0000-high,mode='standalone diagnostic; no emulator execution');(OUT/'report.json').write_text(json.dumps(rep,indent=2));print(rep)
if __name__=='__main__':build()
