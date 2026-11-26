from pathlib import Path
import json,struct,subprocess,shutil
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build_m18/play'
def build():
 OUT.mkdir(parents=True,exist_ok=True)
 for n in ['scene.h','rig11_data.h']:shutil.copyfile(ROOT/'build_m16/play'/n,OUT/n)
 shutil.copyfile(ROOT/'build_m17/view/colors17.h',OUT/'colors17.h')
 opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0'];run=lambda a:subprocess.run(a,cwd=OUT,check=True)
 run(opts+['-c',str(ROOT/'src/dynamic13_start.s'),'-o','start.o'])
 for s in ['play18','cd17','sector16','resident17']:run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(OUT),'-c',str(ROOT/f'src/{s}.c'),'-o',s+'.o'])
 run(['ld.lld','-m','elf32ltsmip','-T',str(ROOT/'src/dynamic13.ld'),'start.o','play18.o','cd17.o','sector16.o','resident17.o','-o','play18.elf']);run(['llvm-objcopy','-O','binary','play18.elf','play18.bin']);data=(OUT/'play18.bin').read_bytes();data+=bytes((-len(data))%2048);header=bytearray(2048);header[:8]=b'PS-X EXE';struct.pack_into('<IIII',header,16,0x80010000,0,0x80010000,len(data));struct.pack_into('<II',header,0x30,0x801fff00,0);(OUT/'ETD_WALK.EXE').write_bytes(header+data)
 run(['clang','-O2','-shared','-fPIC','-DCD17_MOCK',str(ROOT/'src/cache18.c'),str(ROOT/'src/cd17.c'),str(ROOT/'src/sector16.c'),str(ROOT/'src/resident17.c'),str(ROOT/'tests/cd17_mock.c'),'-o','cache18_host.so'])
 elf=(OUT/'play18.elf').read_bytes();off=struct.unpack_from('<I',elf,28)[0];sz,n=struct.unpack_from('<HH',elf,42);high=max(p[2]+p[5] for i in range(n) if (p:=struct.unpack_from('<8I',elf,off+i*sz))[0]==1);rep=dict(exe_bytes=len(data)+2048,linked_ram_from_load=high-0x80010000,headroom_to_stack_region=0x801e0000-high,mode='streamed traversal diagnostic; flat terrain; native compile only');(OUT/'report.json').write_text(json.dumps(rep,indent=2));print(rep)
if __name__=='__main__':build()
