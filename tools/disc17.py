from pathlib import Path
from disc16 import iso,raw,record
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build_m17/view';A=ROOT/'assets_m16'
def build():
 e=(OUT/'ETD_CD.EXE').read_bytes();assets={n:(A/n).read_bytes() for n in ('HUBSECT.DAT','HUBSECT.IDX','HUBTEX.DAT','HUBTEX.IDX')};assets['ETD_FARM.EXE']=(ROOT/'build_m16/play/ETD_SECT.EXE').read_bytes();s=iso(e,assets)
 # Rebuild root directory for alternate boot name without altering original builder.
 root=bytearray();pos=0
 while s[20][pos]:
  n=s[20][pos];r=s[20][pos:pos+n];name=bytes(r[33:33+r[32]])
  if name==b'ETD_SECT.EXE;1':r=record(b'ETD_CD.EXE;1',22,len(e))
  if name==b'SYSTEM.CNF;1':
   config=b'BOOT = cdrom:\\ETD_CD.EXE;1\r\nTCB = 4\r\nEVENT = 10\r\nSTACK = 801FFF00\r\n';s[21][:]=config.ljust(2048,b'\0');r=record(name,21,len(config))
  root.extend(r);pos+=n
 s[20][:]=root.ljust(2048,b'\0');(OUT/'ETD_PSX_M17.bin').write_bytes(b''.join(raw(i,x) for i,x in enumerate(s)));(OUT/'ETD_PSX_M17.cue').write_text('FILE "ETD_PSX_M17.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n');print('sectors',len(s))
if __name__=='__main__':build()
