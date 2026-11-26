"""Build from existing v0.6 generated headers, preserving earlier results."""
import argparse,struct,subprocess,shutil,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def build(out,iso):
 out=out.resolve();out.mkdir(exist_ok=True,parents=True)
 for n in ('scene.h','world.h','farm06.npz','report.json','texture_registry.json'):
  shutil.copyfile(ROOT/'build_m06/play'/n,out/n)
 from material07 import apply
 apply(iso,out)
 from sector07 import apply as sector_apply
 sector_apply(iso,out)
 opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0']
 def run(args):subprocess.run(args,cwd=out,check=True)
 run(opts+['-c',str(ROOT/'src/dynamic_start.s'),'-o','start.o']);run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(out),'-c',str(ROOT/'src/play07.c'),'-o','play07.o']);run(['ld.lld','-m','elf32ltsmip','-T',str(ROOT/'src/dynamic.ld'),'start.o','play07.o','-o','play07.elf']);run(['llvm-objcopy','-O','binary','play07.elf','play07.bin'])
 data=(out/'play07.bin').read_bytes();data+=bytes((-len(data))%2048);header=bytearray(2048);header[:8]=b'PS-X EXE';struct.pack_into('<IIII',header,16,0x80010000,0,0x80010000,len(data));struct.pack_into('<II',header,0x30,0x801fff00,0);(out/'ETD_CLIP.EXE').write_bytes(header+data)
 elf=(out/'play07.elf').read_bytes();phoff=struct.unpack_from('<I',elf,28)[0];phsize,phnum=struct.unpack_from('<HH',elf,42);ends=[]
 for i in range(phnum):
  typ,off,va,pa,fs,ms,fl,al=struct.unpack_from('<8I',elf,phoff+i*phsize)
  if typ==1:ends.append(va+ms)
 high=max(ends);assert high<0x801e0000
 rep=json.loads((out/'report.json').read_text());rep.update(exe_bytes=len(data)+2048,linked_ram_high=hex(high),linked_ram_from_load=high-0x80010000,headroom_to_stack_region=0x801e0000-high,native_runtime='compiled; no emulator/hardware execution',renderer='five-plane camera-space clipping with UV interpolation on terrain and actor');(out/'report.json').write_text(json.dumps(rep,indent=2));print('EXE',len(data)+2048,'linked RAM',hex(high))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('iso',type=Path);p.add_argument('out',type=Path);a=p.parse_args();build(a.out,a.iso)
