"""Build v0.10 from the validated v0.9 scene. No external SDK required."""
import argparse,struct,subprocess,shutil,json
from pathlib import Path
from rig10 import rig
ROOT=Path(__file__).resolve().parents[1]
def build(out,iso):
 out=out.resolve();out.mkdir(exist_ok=True,parents=True)
 for n in ('scene.h','world.h','farm06.npz','report.json','texture_registry.json','actor_tex_0.png','actor_tex_1.png','actor_tex_2.png','visibility.h','visibility.npz','visibility_host.so','visibility_report.json'):
  shutil.copyfile(ROOT/'build_m09/play'/n,out/n)
 rig(iso,out);n=128
 opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0']
 def run(args):subprocess.run(args,cwd=out,check=True)
 run(opts+['-c',str(ROOT/'src/dynamic_start.s'),'-o','start.o']);run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(out),'-c',str(ROOT/'src/play10.c'),'-o','play10.o']);run(['ld.lld','-m','elf32ltsmip','-T',str(ROOT/'src/dynamic.ld'),'start.o','play10.o','-o','play10.elf']);run(['llvm-objcopy','-O','binary','play10.elf','play10.bin'])
 data=(out/'play10.bin').read_bytes();data+=bytes((-len(data))%2048);header=bytearray(2048);header[:8]=b'PS-X EXE';struct.pack_into('<IIII',header,16,0x80010000,0,0x80010000,len(data));struct.pack_into('<II',header,0x30,0x801fff00,0);(out/'ETD_ANIM.EXE').write_bytes(header+data)
 elf=(out/'play10.elf').read_bytes();phoff=struct.unpack_from('<I',elf,28)[0];phsize,phnum=struct.unpack_from('<HH',elf,42);ends=[]
 for i in range(phnum):
  typ,off,va,pa,fs,ms,fl,al=struct.unpack_from('<8I',elf,phoff+i*phsize)
  if typ==1:ends.append(va+ms)
 high=max(ends);assert high<0x801e0000
 rep=json.loads((out/'report.json').read_text());rep.update(exe_bytes=len(data)+2048,linked_ram_high=hex(high),linked_ram_from_load=high-0x80010000,headroom_to_stack_region=0x801e0000-high,native_runtime='compiled; no emulator/hardware execution',renderer='conservative spatial cluster culling, lazy world projection, original face ordering',clusters=n,animation='9 source clips, fixed-point skinning, provisional transforms');(out/'report.json').write_text(json.dumps(rep,indent=2));print('EXE',len(data)+2048,'linked RAM',hex(high),'clusters',n)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('iso',type=Path);p.add_argument('out',type=Path);a=p.parse_args();build(a.out,a.iso)
