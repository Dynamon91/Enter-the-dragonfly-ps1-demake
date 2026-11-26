"""Source texture bank for offline streamed hub blocks. 64x64 8-bit CLUT.
Each entry is three 2048-byte sectors, with 256 RGB555 opaque palette words.
Cutout/PS2 blend mode is intentionally not inferred here.
"""
from pathlib import Path
import argparse,json,struct,zlib
import numpy as np
from PIL import Image
from recover import records,pxt_groups
from hash08 import fold
ROOT=Path(__file__).resolve().parents[1]
def build(iso,out):
 m=json.loads((out/'sector_manifest.json').read_text())['materials'];r=json.loads((ROOT/'build_m15/play/texture_registry.json').read_text());source={e['group']:e for e in r['entries']};ids=sorted({x['texture_group'] for x in m if x['texture_group'] is not None});g=list(pxt_groups(records(iso)[772][1]));data=bytearray();entries=[]
 for i in ids:
  e=source[i];_,pal,imgs=g[i];w,h,ix=imgs[0];assert [w,h]==e['dimensions'] and len(pal) in (16,256)
  pal=pal.astype(np.uint16);c=np.maximum((pal[:,0]>>3)|((pal[:,1]>>3)<<5)|((pal[:,2]>>3)<<10),1).astype('<u2');c=np.pad(c,(0,256-len(c)));q=np.asarray(Image.fromarray(ix).resize((64,64),Image.Resampling.NEAREST),dtype=np.uint8);payload=c.tobytes()+q.tobytes();crc=zlib.crc32(payload);header=struct.pack('<4sHHIIII',b'ETDT',1,i,w,h,len(payload),crc);block=header+payload;assert len(block)<6144;entries.append(dict(group=i,lba=len(data)//2048,crc=crc,width=w,height=h,average_rgb=np.rint(pal[ix][:,:,:3].mean((0,1))).astype(int).tolist()));data.extend(block+bytes(6144-len(block)))
 (out/'HUBTEX.DAT').write_bytes(data);idx=bytearray(struct.pack('<4sHHI',b'ETTI',1,12,len(entries)))
 for e in entries:idx.extend(struct.pack('<III',e['group'],e['lba'],e['crc']))
 (out/'HUBTEX.IDX').write_bytes(idx);(out/'texture_report.json').write_text(json.dumps(dict(textures=len(entries),data_bytes=len(data),entries=entries,limitations='Opaque base texture conversion; original alpha and multilayer blending not represented, no native VRAM streaming yet.'),indent=2));print('texture bank',len(entries),len(data))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('iso',type=Path);p.add_argument('out',type=Path);a=p.parse_args();build(a.iso,a.out)
