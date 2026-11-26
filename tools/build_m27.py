from pathlib import Path
import json,struct,subprocess,shutil,zlib
from disc16 import iso,raw,record
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build_m27/play';A=ROOT/'assets_m27'
def build():
 OUT.mkdir(parents=True,exist_ok=True);m=json.loads((A/'sector_manifest.json').read_text());old=ROOT/'build_m24/play'
 for n in ('scene.h','rig11_data.h','collectdata12.h','sfx14.h','firetex11.h','basketmesh21.h','foddermesh21.h'):shutil.copyfile(old/n,OUT/n)
 baskets=sorted(o['record_offset'] for o in m['objects'] if o['edf'].lower()=='basket1.edf');gems=sorted((o['record_offset'],o['value']) for o in m['objects'] if o['kind']==1);assert len(baskets)==45 and len(gems)==193
 (OUT/'gemids20.h').write_text('static const U32 gemids20[193]={'+','.join(str(a) for a,b in gems)+'};\nstatic const U8 gemvalues20[193]={'+','.join(str(b) for a,b in gems)+'};\n')
 (OUT/'objectids21.h').write_text('static const U32 objectids21[46]={'+','.join(map(str,baskets))+',0xffffffffu};\n')
 dat=bytearray((A/'DOJOSECT.DAT').read_bytes());idx=bytearray((A/'DOJOSECT.IDX').read_bytes());changed=0
 for b in m['blocks']:
  off=b['lba']*2048;start=off+64+36*b['render']+24*b['collision']
  for j in range(b['objects']):
   p=start+16*j;oid=struct.unpack_from('<I',dat,p+12)[0]
   if oid in baskets:struct.pack_into('<H',dat,p+6,2);changed+=1
  crc=zlib.crc32(dat[off+64:off+b['size']]);struct.pack_into('<I',dat,off+36,crc);struct.pack_into('<I',idx,16+60*b['id']+12,crc)
 assert changed==45
 (OUT/'DOJOSECT.DAT').write_bytes(dat);(OUT/'DOJOSECT.IDX').write_bytes(idx)
 (OUT/'colors17.h').write_text('static const unsigned colors17[]={'+','.join(str(a|b<<8|c<<16) for a,b,c in (x['rgb'] for x in m['materials']))+'};\n');(OUT/'groups19.h').write_text('static const short groups19[MAT18]={'+','.join(str(-1 if a['texture_group'] is None else a['texture_group']) for a in m['materials'])+'};\n')
 for name,repl in {'cache24.c':{'RADIUS18 1536':'RADIUS18 1792','CAP18 16':'CAP18 28','rd18(idx+12)!=4096':'rd18(idx+12)!=2048','BLOCKS18 174':'BLOCKS18 446','MAT18 208':'MAT18 53','536*1024':'460*1024','MAT18,75653,6195':'MAT18,127733,7035'},'collect21.h':{'GEM20_COUNT 290':'GEM20_COUNT 193'},'interact21.h':{'OBJ21 39':'OBJ21 46','BASK21 27':'BASK21 45','SHEEP21 12':'SHEEP21 1'},'tex19.h':{'TEXCOUNT19 141':'TEXCOUNT19 52'},'play24.c':{'HUBSECT':'DOJOSECT','HUBTEX':'DOJOTEX','10456':'26776','idx[12288]':'idx[28672]','36848,-1200,800':'10534,-14914,-2075','36848,-1200':'10534,-14914','36848,f,-1200':'10534,f,-14914','36848,800,-1200,800':'10534,-2075,-14914,-2075','dx<-1200':'dx<-1536','dx>1200':'dx>1536','dz<-1200':'dz<-1536','dz>1200':'dz>1536','MAXT 10000':'MAXT 12000'}}.items():
  s=(ROOT/'src'/name).read_text()
  for a,b in repl.items():s=s.replace(a,b)
  (OUT/name).write_text(s)
 assert 'cache18_floor(&cache,10534,-14914,-2075,110)' in (OUT/'play24.c').read_text()
 opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0'];run=lambda a:subprocess.run(a,cwd=OUT,check=True)
 run(opts+['-c',str(ROOT/'src/dynamic13_start.s'),'-o','start.o'])
 for p in [OUT/'play24.c',ROOT/'src/cd17.c',ROOT/'src/sector27.c',ROOT/'src/resident17.c']:run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(OUT),'-I',str(ROOT/'src'),'-c',str(p),'-o',p.stem+'.o'])
 run(['ld.lld','-m','elf32ltsmip','-T',str(ROOT/'src/dynamic13.ld'),'start.o','play24.o','cd17.o','sector27.o','resident17.o','-o','play27.elf']);run(['llvm-objcopy','-O','binary','play27.elf','play27.bin']);d=(OUT/'play27.bin').read_bytes();d+=bytes((-len(d))%2048);h=bytearray(2048);h[:8]=b'PS-X EXE';struct.pack_into('<IIII',h,16,0x80010000,0,0x80010000,len(d));struct.pack_into('<II',h,0x30,0x801fff00,0);e=h+d;(OUT/'ETD_WIDE.EXE').write_bytes(e)
 s=(ROOT/'tests/interact24_host.c').read_text().replace('../src/cache24.c','cache24.c').replace('../src/collect21.h','collect21.h').replace('../src/interact21.h','interact21.h');(OUT/'host27.c').write_text(s);run(['clang','-O2','-shared','-fPIC','-I',str(OUT),str(OUT/'host27.c'),str(ROOT/'src/sector27.c'),str(ROOT/'src/cd17.c'),str(ROOT/'src/resident17.c'),str(ROOT/'tests/cd17_mock.c'),'-DCD17_MOCK','-o','host27.so'])
 ts=(ROOT/'tests/tex19_host.c').read_text().replace('../src/cache18.c','cache24.c').replace('../src/tex19.h','tex19.h');(OUT/'tex27_host.c').write_text(ts);run(['clang','-O2','-shared','-fPIC','-I',str(OUT),str(OUT/'tex27_host.c'),str(ROOT/'src/sector27.c'),'-o','tex27_host.so'])
 elf=(OUT/'play27.elf').read_bytes();off=struct.unpack_from('<I',elf,28)[0];sz,n=struct.unpack_from('<HH',elf,42);high=max(p[2]+p[5] for i in range(n) if (p:=struct.unpack_from('<8I',elf,off+i*sz))[0]==1);rep=dict(exe_bytes=len(e),linked_ram_from_load=high-0x80010000,headroom_to_stack_region=0x801e0000-high,spawn=[10534,-2075,-14914],gems=193,baskets=45,mode='Dojo traversal; native compile only');assert high<0x801e0000;(OUT/'report.json').write_text(json.dumps(rep,indent=2));print(rep,flush=True)
 assets={n:(ROOT/'assets_m16'/n).read_bytes() for n in ('HUBSECT.DAT','HUBSECT.IDX')};assets.update({n:(ROOT/'assets_m20'/n).read_bytes() for n in ('HUBTEX.DAT','HUBTEX.IDX')});assets.update({n:(OUT/n).read_bytes() for n in ('DOJOSECT.DAT','DOJOSECT.IDX')});assets.update({n:(A/n).read_bytes() for n in ('DOJOTEX.DAT','DOJOTEX.IDX')});assets['ETD_POOL.EXE']=(old/'ETD_POOL.EXE').read_bytes();s=iso(e,assets);root=bytearray();pos=0
 while s[20][pos]:
  n=s[20][pos];rr=s[20][pos:pos+n];name=bytes(rr[33:33+rr[32]])
  if name==b'ETD_SECT.EXE;1':rr=record(b'ETD_WIDE.EXE;1',22,len(e))
  if name==b'SYSTEM.CNF;1':
   config=b'BOOT = cdrom:\\ETD_WIDE.EXE;1\r\nTCB = 4\r\nEVENT = 10\r\nSTACK = 801FFF00\r\n';s[21][:]=config.ljust(2048,b'\0');rr=record(name,21,len(config))
  root.extend(rr);pos+=n
 s[20][:]=root.ljust(2048,b'\0');(OUT/'ETD_PSX_M27.bin').write_bytes(b''.join(raw(i,x) for i,x in enumerate(s)));(OUT/'ETD_PSX_M27.cue').write_text('FILE "ETD_PSX_M27.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
if __name__=='__main__':build()
