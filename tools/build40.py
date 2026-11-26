from pathlib import Path
import struct, subprocess
R=Path(__file__).resolve().parents[1]; O=R/'out40'; O.mkdir(exist_ok=True)
def run(*args): subprocess.run(args,cwd=R,check=True)
opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0']
run(*opts,'-c','native/start40.s','-o',str(O/'start.o'))
run(*opts,'-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I','src','-c','native/arena40.c','-o',str(O/'arena.o'))
run('ld.lld','-m','elf32ltsmip','-T','native/arena40.ld',str(O/'start.o'),str(O/'arena.o'),'-o',str(O/'arena.elf'))
run('llvm-objcopy','-O','binary',str(O/'arena.elf'),str(O/'arena.bin'))
d=(O/'arena.bin').read_bytes();d+=bytes((-len(d))%2048);h=bytearray(2048);h[:8]=b'PS-X EXE';struct.pack_into('<IIII',h,16,0x80010000,0,0x80010000,len(d));struct.pack_into('<II',h,0x30,0x801fff00,0);(O/'ETD40.EXE').write_bytes(h+d);print('Native PS-X EXE bytes:',len(h+d))
