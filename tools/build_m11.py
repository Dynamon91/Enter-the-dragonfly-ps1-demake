"""Rebuild from the source-derived, validated v0.10 asset exports."""
import argparse,struct,subprocess,shutil,json
from pathlib import Path
from pack_rig11 import pack
ROOT=Path(__file__).resolve().parents[1]
def build(out):
 out=out.resolve();out.mkdir(exist_ok=True,parents=True)
 for n in ('scene.h','world.h','farm06.npz','report.json','texture_registry.json','actor_tex_0.png','actor_tex_1.png','actor_tex_2.png','visibility.h','visibility.npz','visibility_host.so','visibility_report.json','rig.npz','rig_report.json','poses_host.npz'):
  shutil.copyfile(ROOT/'build_m10/play'/n,out/n)
 for n in ('firetex11.h','firetex11.npy','fire_source.png','fire_texture_report.json'):
  shutil.copyfile(ROOT/'assets_m11'/n,out/n)
 pack(out)
 opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0']
 def run(args):subprocess.run(args,cwd=out,check=True)
 run(opts+['-c',str(ROOT/'src/dynamic_start.s'),'-o','start.o']);run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(out),'-c',str(ROOT/'src/play11.c'),'-o','play11.o']);run(['ld.lld','-m','elf32ltsmip','-T',str(ROOT/'src/dynamic.ld'),'start.o','play11.o','-o','play11.elf']);run(['llvm-objcopy','-O','binary','play11.elf','play11.bin'])
 data=(out/'play11.bin').read_bytes();data+=bytes((-len(data))%2048);header=bytearray(2048);header[:8]=b'PS-X EXE';struct.pack_into('<IIII',header,16,0x80010000,0,0x80010000,len(data));struct.pack_into('<II',header,0x30,0x801fff00,0);(out/'ETD_FIRE.EXE').write_bytes(header+data)
 elf=(out/'play11.elf').read_bytes();phoff=struct.unpack_from('<I',elf,28)[0];phsize,phnum=struct.unpack_from('<HH',elf,42);ends=[]
 for i in range(phnum):
  typ,off,va,pa,fs,ms,fl,al=struct.unpack_from('<8I',elf,phoff+i*phsize)
  if typ==1:ends.append(va+ms)
 high=max(ends);assert high<0x801e0000
 old=json.loads((ROOT/'build_m10/play/report.json').read_text());rep=old.copy();rep.update(exe_bytes=len(data)+2048,linked_ram_high=hex(high),linked_ram_from_load=high-0x80010000,headroom_to_stack_region=0x801e0000-high,ram_saved=old['linked_ram_from_load']-(high-0x80010000),native_runtime='compiled; no emulator/hardware execution',animation='lossless checkpoint/delta; same original nine clips and provisional transforms',gameplay='fire particles and 3 synthetic diagnostic targets; no original enemy damage logic',packet_size=22);(out/'report.json').write_text(json.dumps(rep,indent=2));print('EXE',len(data)+2048,'linked RAM',hex(high),'saved',rep['ram_saved'])
 run(['clang','-O2','-shared','-fPIC','-I',str(out),'-I',str(ROOT/'src'),str(ROOT/'tests/rig11_host.c'),'-o','rig11_host.so'])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('out',type=Path);build(p.parse_args().out)
