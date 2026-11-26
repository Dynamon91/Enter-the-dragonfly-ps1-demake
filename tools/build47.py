"""Build a standalone native XA transport diagnostic; no proprietary content."""
import math,struct,subprocess,wave,json,hashlib
from pathlib import Path
import xa46 as x,xabank46 as bank
from disc16 import iso,raw,both32
R=Path(__file__).resolve().parents[1];O=R/'out47';O.mkdir(exist_ok=True)
def run(*a):subprocess.run(a,cwd=R,check=True)
tracks=[];count=24*x.FRAMES
for i in range(2):
 w=O/f'tone{i}.wav';b=O/f'tone{i}.bin';b.unlink(missing_ok=True)
 with wave.open(str(w),'wb') as f:
  f.setparams((2,2,x.RATE,0,'NONE','not compressed'));f.writeframes(b''.join(struct.pack('<hh',int(4500*math.sin(2*math.pi*(300+150*i)*j/x.RATE)),int(4500*math.sin(2*math.pi*(450+150*i)*j/x.RATE))) for j in range(count)))
 tracks.append((b,x.encode(w,b,loop=[0,count])))
start=300;dest=O/'bank.bin';dest.unlink(missing_ok=True);m=bank.pack(tracks,dest,start)
(O/'tracks47.h').write_text('static const Track47 tracks47[]={\n'+''.join('{%d,%d,%d,%d,%d,%d,1},\n'%(t['first_audio_lba'],t['last_audio_lba'],t['loop_start_lba'],t['loop_last_lba'],t['file'],t['channel']) for t in m['tracks'])+'};\n')
(O/'native47.c').write_text((R/'native/arena40.c').read_text().split('void main40(void)')[0]+(R/'native/main47.inc').read_text())
opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0']
run(*opts,'-c','native/start40.s','-o',str(O/'start.o'))
for src,name in [(O/'native47.c','main'),(R/'src/xa47_cd.c','cd')]:run(*opts,'-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I','src','-I',str(O),'-c',str(src),'-o',str(O/(name+'.o')))
run('ld.lld','-m','elf32ltsmip','-T','native/arena40.ld',*[str(O/(n+'.o')) for n in ('start','main','cd')],'-o',str(O/'xa47.elf'))
run('llvm-objcopy','-O','binary',str(O/'xa47.elf'),str(O/'xa47.raw'))
d=(O/'xa47.raw').read_bytes();d+=bytes((-len(d))%2048);h=bytearray(2048);h[:8]=b'PS-X EXE';struct.pack_into('<IIII',h,16,0x80010000,0,0x80010000,len(d));struct.pack_into('<II',h,0x30,0x801fff00,0);e=h+d;(O/'ETD47.EXE').write_bytes(e)
s=iso(e,{});assert len(s)==start;end=start+m['physical_sectors'];total=end+48;s[16][80:88]=both32(total)
image=b''.join(raw(i,p) for i,p in enumerate(s))+dest.read_bytes()+b''.join(x.filler(i) for i in range(end,total))
assert len(image)==total*2352
for i in range(total):x.inspect_sector(image[i*2352:(i+1)*2352],i)
assert b''.join(image[i*2352+24:i*2352+2072] for i in range(22,22+len(e)//2048))==e
(O/'ETD47.bin').write_bytes(image);(O/'ETD47.cue').write_text('FILE "ETD47.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n');(O/'bank.json').write_text(json.dumps(m,indent=2)+'\n')
print(f'{len(e)} EXE bytes; {total} sectors verified; {2*24} XA audio sectors; 48 guard sectors')
