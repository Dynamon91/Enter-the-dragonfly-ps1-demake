import argparse,subprocess,struct,shutil
from pathlib import Path
from icon import make
ROOT=Path(__file__).resolve().parents[1]
def run(a,cwd):subprocess.run(a,cwd=cwd,check=True)
def build(iso,out):
    out=out.resolve();out.mkdir(parents=True,exist_ok=True);make(iso,out,35)
    for tool in ('clang','ld.lld','llvm-objcopy'):
        if not shutil.which(tool): raise RuntimeError('Missing '+tool)
    run(['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-c',str(ROOT/'src/start.s'),'-o','start.o'],out)
    run(['ld.lld','-m','elf32ltsmip','-T',str(ROOT/'src/psx.ld'),'start.o','-o','demo.elf'],out)
    run(['llvm-objcopy','-O','binary','demo.elf','payload.bin'],out)
    payload=(out/'payload.bin').read_bytes();payload+=bytes((-len(payload))%2048)
    if len(payload)>0x1e0000: raise ValueError('Too large for PS1 main RAM')
    header=bytearray(2048);header[:8]=b'PS-X EXE';struct.pack_into('<IIII',header,0x10,0x80010000,0,0x80010000,len(payload));struct.pack_into('<II',header,0x30,0x801fff00,0)
    (out/'ETD_ICON.EXE').write_bytes(header+payload); print('PS-X EXE bytes:',len(payload)+2048)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('iso',type=Path);p.add_argument('out',type=Path);a=p.parse_args();build(a.iso.resolve(),a.out)
