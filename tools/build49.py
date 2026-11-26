"""Standalone SPU test disc with synthetic fixtures, no game assets."""
import math,struct,subprocess,wave,json
from pathlib import Path
import spu49 as s
from disc16 import iso,raw
R=Path(__file__).resolve().parents[1];O=R/'out49';O.mkdir(exist_ok=True)
def run(*a):subprocess.run(a,cwd=R,check=True)
entries=[]
for i,n in enumerate((5600,2800)):
 p=O/f'tone{i}.wav';rate=22050
 with wave.open(str(p),'wb') as w:
  w.setparams((1,2,rate,0,'NONE',''));w.writeframes(b''.join(struct.pack('<h',int(9000*math.sin(2*math.pi*(315 if i else 441)*j/rate)*(1 if i else (n-j)/n))) for j in range(n)))
 entries.append((f'tone{i}',p,0 if i else None));d,m=s.encode(p,0 if i else None);(O/f'tone{i}.vag').write_bytes(s.vag(d,m['rate']));
b,m=s.pack(entries);(O/'SFX49.DAT').write_bytes(b);(O/'SFX49.json').write_text(json.dumps(m,indent=2)+'\n')
(O/'sfx49_data.h').write_text('static const unsigned char sfx49[]={'+','.join(map(str,b))+'};\nstatic const Sample49 entries49[]={'+','.join('{%d,%d,%d,%d,%du}'%(v['address'],v['bytes'],v['pitch'],v['frames'],0xffffffff if v['loop'] is None else v['loop']) for v in m)+'};\n')
(O/'main49.c').write_text((R/'native/arena40.c').read_text().split('void main40(void)')[0]+(R/'native/main49.inc').read_text())
opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0']
run(*opts,'-c','native/start40.s','-o',str(O/'start.o'))
for p,n in [(O/'main49.c','main'),(R/'src/spu49.c','spu')]:run(*opts,'-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I','src','-I',str(O),'-c',str(p),'-o',str(O/(n+'.o')))
run('ld.lld','-m','elf32ltsmip','-T','native/arena40.ld',*[str(O/(n+'.o')) for n in ('start','main','spu')],'-o',str(O/'sfx49.elf'))
run('llvm-objcopy','-O','binary',str(O/'sfx49.elf'),str(O/'sfx49.raw'))
d=(O/'sfx49.raw').read_bytes();d+=bytes((-len(d))%2048);h=bytearray(2048);h[:8]=b'PS-X EXE';struct.pack_into('<IIII',h,16,0x80010000,0,0x80010000,len(d));struct.pack_into('<II',h,0x30,0x801fff00,0);e=h+d;(O/'ETD49.EXE').write_bytes(e)
sectors=iso(e,{});image=b''.join(raw(i,p) for i,p in enumerate(sectors));assert all(image[i*2352:(i+1)*2352]==raw(i,p) for i,p in enumerate(sectors));assert b''.join(sectors[22:22+len(e)//2048])==e
(O/'ETD49.bin').write_bytes(image);(O/'ETD49.cue').write_text('FILE "ETD49.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n');print(f'{len(e)} EXE bytes; {len(sectors)} sectors; {len(b)} bytes SPU sample bank')
