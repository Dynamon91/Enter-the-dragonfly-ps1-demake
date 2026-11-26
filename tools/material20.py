"""Selective PS2 source alpha conversion; preserve opaque zero-alpha PS2 palettes."""
from pathlib import Path
import json,struct,zlib,sys
import numpy as np
from recover import records,pxt_groups
ROOT=Path(__file__).resolve().parents[1]; OLD=ROOT/'assets_m16'; OUT=ROOT/'assets_m20'
MASK={84,359,292};THRESHOLD=32

def build(iso):
 OUT.mkdir(exist_ok=True);idx=bytearray((OLD/'HUBTEX.IDX').read_bytes());dat=bytearray((OLD/'HUBTEX.DAT').read_bytes());groups=list(pxt_groups(records(iso)[772][1]));report=[]
 for i in range(141):
  g,lba,crc=struct.unpack_from('<III',idx,12+12*i)
  if g not in MASK:continue
  p=lba*2048;_,pal,imgs=groups[g];assert 0<np.max(pal[imgs[0][2],3])<=255
  q=np.frombuffer(bytes(dat[p+24:p+536]),dtype='<u2').copy();before=q.copy();q[:len(pal)][pal[:,3]<THRESHOLD]=0;ix=np.frombuffer(dat[p+536:p+4632],dtype=np.uint8);n=int((q[ix]==0).sum());assert 0<n<4096
  dat[p+24:p+536]=q.tobytes();crc=zlib.crc32(dat[p+24:p+4632]);struct.pack_into('<I',dat,p+20,crc);struct.pack_into('<I',idx,12+12*i+8,crc);report.append(dict(group=g,transparent_texels=n,opaque_texels=4096-n,palette_entries_changed=int((q!=before).sum())))
 (OUT/'HUBTEX.IDX').write_bytes(idx);(OUT/'HUBTEX.DAT').write_bytes(dat);(OUT/'alpha_report.json').write_text(json.dumps(dict(threshold=THRESHOLD,groups=report,limitations='Binary cutout approximation; partial alpha and original blend equations not reconstructed.'),indent=2));print(report)
if __name__=='__main__':build(Path(sys.argv[1]))
