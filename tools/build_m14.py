"""Rebuild from the source-derived, validated v0.10 asset exports."""
import argparse,struct,subprocess,shutil,json
from pathlib import Path
from pack_rig11 import pack
from audio14 import pack as audio_pack
ROOT=Path(__file__).resolve().parents[1]
def build(out):
 out=out.resolve();out.mkdir(exist_ok=True,parents=True)
 for n in ('scene.h','world.h','farm06.npz','report.json','texture_registry.json','actor_tex_0.png','actor_tex_1.png','actor_tex_2.png','visibility.h','visibility.npz','visibility_host.so','visibility_report.json','rig.npz','rig_report.json','poses_host.npz'):
  shutil.copyfile(ROOT/'build_m10/play'/n,out/n)
 for n in ('firetex11.h','firetex11.npy','fire_source.png','fire_texture_report.json'):
  shutil.copyfile(ROOT/'assets_m11'/n,out/n)
 pack(out)
 audio_pack(out)
 shutil.copyfile(ROOT/'assets_m12/collectdata12.h',out/'collectdata12.h')
 shutil.copyfile(ROOT/'assets_m14/basketdata14.h',out/'basketdata14.h')
 opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0']
 def run(args):subprocess.run(args,cwd=out,check=True)
 run(opts+['-c',str(ROOT/'src/dynamic13_start.s'),'-o','start.o']);run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(out),'-c',str(ROOT/'src/play14.c'),'-o','play14.o']);run(['ld.lld','-m','elf32ltsmip','-T',str(ROOT/'src/dynamic13.ld'),'start.o','play14.o','-o','play14.elf']);run(['llvm-objcopy','-O','binary','play14.elf','play14.bin'])
 data=(out/'play14.bin').read_bytes();data+=bytes((-len(data))%2048);header=bytearray(2048);header[:8]=b'PS-X EXE';struct.pack_into('<IIII',header,16,0x80010000,0,0x80010000,len(data));struct.pack_into('<II',header,0x30,0x801fff00,0);(out/'ETD_BASK.EXE').write_bytes(header+data)
 elf=(out/'play14.elf').read_bytes();phoff=struct.unpack_from('<I',elf,28)[0];phsize,phnum=struct.unpack_from('<HH',elf,42);ends=[]
 for i in range(phnum):
  typ,off,va,pa,fs,ms,fl,al=struct.unpack_from('<8I',elf,phoff+i*phsize)
  if typ==1:ends.append(va+ms)
 high=max(ends);assert high<0x801e0000
 old=json.loads((ROOT/'build_m10/play/report.json').read_text());rep=old.copy();rep.update(exe_bytes=len(data)+2048,linked_ram_high=hex(high),linked_ram_from_load=high-0x80010000,headroom_to_stack_region=0x801e0000-high,ram_saved=old['linked_ram_from_load']-(high-0x80010000),native_runtime='compiled; no emulator/hardware execution',animation='lossless checkpoint/delta; same original nine clips and provisional transforms',gameplay='fire, three source gems, Sparx, two source baskets with provisional red gem rewards, three original SPU sounds',collect_mesh_capacity=339,packet_size=20);(out/'report.json').write_text(json.dumps(rep,indent=2));print('EXE',len(data)+2048,'linked RAM',hex(high),'saved',rep['ram_saved'])
 run(['clang','-O2','-shared','-fPIC','-I',str(out),'-I',str(ROOT/'src'),str(ROOT/'tests/rig11_host.c'),'-o','rig11_host.so'])
 run(['clang','-O2','-shared','-fPIC','-I',str(out),'-I',str(ROOT/'src'),str(ROOT/'tests/collect13_host.c'),'-o','collect13_host.so'])
 run(['clang','-O2','-shared','-fPIC','-I',str(out),'-I',str(ROOT/'src'),str(ROOT/'tests/spu14_host.c'),'-o','spu14_host.so'])
 run(["clang","-O2","-shared","-fPIC","-I",str(out),"-I",str(ROOT/"src"),str(ROOT/"tests/basket14_host.c"),"-o","basket14_host.so"])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('out',type=Path);build(p.parse_args().out)
