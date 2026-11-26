from pathlib import Path
import json,struct,subprocess,shutil
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build_m24/play'
def build():
 OUT.mkdir(parents=True,exist_ok=True)
 for n in ['scene.h','rig11_data.h']:shutil.copyfile(ROOT/'build_m16/play'/n,OUT/n)
 shutil.copyfile(ROOT/'build_m17/view/colors17.h',OUT/'colors17.h')
 m=json.loads((ROOT/'assets_m16/sector_manifest.json').read_text())['materials'];(OUT/'groups19.h').write_text('static const short groups19[MAT18]={'+','.join(str(-1 if a['texture_group'] is None else a['texture_group']) for a in m)+'};\n')
 shutil.copyfile(ROOT/'assets_m12/collectdata12.h',OUT/'collectdata12.h')
 shutil.copyfile(ROOT/'build_m14/play/sfx14.h',OUT/'sfx14.h')
 shutil.copyfile(ROOT/'assets_m11/firetex11.h',OUT/'firetex11.h')
 (OUT/'basketmesh21.h').write_text((ROOT/'assets_m14/basketdata14.h').read_text().split('#define BASKET_COUNT')[0])
 shutil.copyfile(ROOT/'assets_m15/fodderdata15.h',OUT/'foddermesh21.h')
 objects=sorted((x['kind'],x['record_offset']) for x in json.loads((ROOT/'assets_m16/sector_manifest.json').read_text())['objects'] if x['kind'] in (2,3));assert len(objects)==39 and len({x[1] for x in objects})==39
 (OUT/'objectids21.h').write_text('static const U32 objectids21[39]={'+','.join(str(b) for a,b in objects)+'};\n')
 gems=sorted((x['record_offset'],x['value']) for x in json.loads((ROOT/'assets_m16/sector_manifest.json').read_text())['objects'] if x['kind']==1);assert len(gems)==290 and len({a for a,b in gems})==290
 (OUT/'gemids20.h').write_text('static const U32 gemids20[290]={'+','.join(str(a) for a,b in gems)+'};\nstatic const U8 gemvalues20[290]={'+','.join(str(b) for a,b in gems)+'};\n')
 opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0'];run=lambda a:subprocess.run(a,cwd=OUT,check=True)
 run(opts+['-c',str(ROOT/'src/dynamic13_start.s'),'-o','start.o'])
 for s in ['play24','cd17','sector23','resident17']:run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(OUT),'-c',str(ROOT/f'src/{s}.c'),'-o',s+'.o'])
 run(['ld.lld','-m','elf32ltsmip','-T',str(ROOT/'src/dynamic13.ld'),'start.o','play24.o','cd17.o','sector23.o','resident17.o','-o','play24.elf']);run(['llvm-objcopy','-O','binary','play24.elf','play24.bin']);data=(OUT/'play24.bin').read_bytes();data+=bytes((-len(data))%2048);header=bytearray(2048);header[:8]=b'PS-X EXE';struct.pack_into('<IIII',header,16,0x80010000,0,0x80010000,len(data));struct.pack_into('<II',header,0x30,0x801fff00,0);(OUT/'ETD_POOL.EXE').write_bytes(header+data)
 run(['clang','-O2','-shared','-fPIC','-DCD17_MOCK',str(ROOT/'src/cache24.c'),str(ROOT/'src/cd17.c'),str(ROOT/'src/sector23.c'),str(ROOT/'src/resident17.c'),str(ROOT/'tests/cd17_mock.c'),'-o','cache24_host.so'])
 run(['clang','-O2','-shared','-fPIC','-DCD17_MOCK',str(ROOT/'tests/tex19_host.c'),str(ROOT/'src/cd17.c'),str(ROOT/'src/sector23.c'),str(ROOT/'src/resident17.c'),str(ROOT/'tests/cd17_mock.c'),'-o','tex19_host.so'])
 run(['clang','-O2','-shared','-fPIC','-I',str(OUT),str(ROOT/'tests/interact24_host.c'),str(ROOT/'src/sector23.c'),'-o','interact24_host.so'])
 elf=(OUT/'play24.elf').read_bytes();off=struct.unpack_from('<I',elf,28)[0];sz,n=struct.unpack_from('<HH',elf,42);high=max(p[2]+p[5] for i in range(n) if (p:=struct.unpack_from('<8I',elf,off+i*sz))[0]==1);rep=dict(exe_bytes=len(data)+2048,linked_ram_from_load=high-0x80010000,headroom_to_stack_region=0x801e0000-high,mode='shared residency predictive cache; native compile only');(OUT/'report.json').write_text(json.dumps(rep,indent=2));print(rep)
if __name__=='__main__':build()
