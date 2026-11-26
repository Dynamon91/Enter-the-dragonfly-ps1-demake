from pathlib import Path
import struct, subprocess
R=Path(__file__).resolve().parents[1]; O=R/'out44'; O.mkdir(exist_ok=True)
def run(*args): subprocess.run(args,cwd=R,check=True)
run("python3","tools/assets44.py");run("python3","tools/integrate44.py")
opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0']
(O/"arena44.c").write_text((R/"native/arena40.c").read_text().split("void main40(void)")[0].replace("(u32)x|((u32)y<<16)","((u32)x&65535u)|((u32)y<<16)")+(R/"native/main44.inc").read_text())
run(*opts,'-c','native/start40.s','-o',str(O/'start.o'))
run(*opts,'-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I','src','-c',str(O/'arena44.c'),'-o',str(O/'arena.o'))
run('ld.lld','-m','elf32ltsmip','-T','native/arena40.ld',str(O/'start.o'),str(O/'arena.o'),'-o',str(O/'arena.elf'))
run('llvm-objcopy','-O','binary',str(O/'arena.elf'),str(O/'arena.bin'))
d=(O/'arena.bin').read_bytes();d+=bytes((-len(d))%2048);h=bytearray(2048);h[:8]=b'PS-X EXE';struct.pack_into('<IIII',h,16,0x80010000,0,0x80010000,len(d));struct.pack_into('<II',h,0x30,0x801fff00,0);(O/'ETD44.EXE').write_bytes(h+d);print('Native PS-X EXE bytes:',len(h+d))
from disc16 import iso,raw
s=iso(h+d,{})
image=b''.join(raw(i,x) for i,x in enumerate(s))
(O/'ETD44.bin').write_bytes(image)
(O/'ETD44.cue').write_text('FILE "ETD44.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
assert image[16*2352+24:16*2352+31]==b'\x01CD001\x01'
assert b'ETD_SECT.EXE;1' in s[21]
assert b''.join(s[22:22+len(h+d)//2048])==h+d
for i in range(len(s)):
 sector=image[i*2352:(i+1)*2352];assert sector==raw(i,sector[24:2072])
print('Mode 2 Form 1 sectors verified:',len(s))
