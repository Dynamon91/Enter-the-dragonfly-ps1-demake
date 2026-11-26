from pathlib import Path
from disc16 import iso,raw,record
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build_m21/play';A=ROOT/'assets_m16'
def build():
 e=(OUT/'ETD_HUB.EXE').read_bytes();assets={n:(A/n).read_bytes() for n in ('HUBSECT.DAT','HUBSECT.IDX','HUBTEX.DAT','HUBTEX.IDX')};assets.update({n:(ROOT/'assets_m20'/n).read_bytes() for n in ('HUBTEX.DAT','HUBTEX.IDX')});assets['ETD_GEM.EXE']=(ROOT/'build_m20/play/ETD_GEM.EXE').read_bytes();assets['ETD_TEX.EXE']=(ROOT/'build_m19/play/ETD_TEX.EXE').read_bytes();assets['ETD_FARM.EXE']=(ROOT/'build_m16/play/ETD_SECT.EXE').read_bytes();assets['ETD_WALK.EXE']=(ROOT/'build_m18/play/ETD_WALK.EXE').read_bytes();assets['ETD_CD.EXE']=(ROOT/'build_m17/view/ETD_CD.EXE').read_bytes();s=iso(e,assets)
 root=bytearray();pos=0
 while s[20][pos]:
  n=s[20][pos];r=s[20][pos:pos+n];name=bytes(r[33:33+r[32]])
  if name==b'ETD_SECT.EXE;1':r=record(b'ETD_HUB.EXE;1',22,len(e))
  if name==b'SYSTEM.CNF;1':
   config=b'BOOT = cdrom:\\ETD_HUB.EXE;1\r\nTCB = 4\r\nEVENT = 10\r\nSTACK = 801FFF00\r\n';s[21][:]=config.ljust(2048,b'\0');r=record(name,21,len(config))
  root.extend(r);pos+=n
 s[20][:]=root.ljust(2048,b'\0');(OUT/'ETD_PSX_M21.bin').write_bytes(b''.join(raw(i,x) for i,x in enumerate(s)));(OUT/'ETD_PSX_M21.cue').write_text('FILE "ETD_PSX_M21.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n');print('sectors',len(s))
if __name__=='__main__':build()
