"""Recover the original spyro_fire sprite from the verified PXT directory.
PS1 conversion: black transparent; nonzero RGB555 uses STP/additive blend.
The source alpha is uniformly zero, so the blend mode is an approximation.
"""
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image
from recover import records,pxt_groups
from material08 import upload
ROOT=Path(__file__).resolve().parents[1]
def extract(iso,out):
 out.mkdir(parents=True,exist_ok=True);r=json.loads((ROOT/'build_m10/play/texture_registry.json').read_text());e=next(t for t in r['resolved_references'] if t['filename']=='ECFECEFC.PXT');assert e['dimensions_match'];_,pal,imgs=list(pxt_groups(records(iso)[772][1]))[e['group']];w,h,ix=imgs[0];assert (w,h)==(32,32) and len(pal)==256;assert not np.any(pal[ix,3]);rgb=pal.astype(np.uint16);c=(rgb[:,0]>>3)|((rgb[:,1]>>3)<<5)|((rgb[:,2]>>3)<<10);c=np.where(c,c|32768,0).astype('<u2');words=[];upload(words,c,ix,[704,0,16,32],[768,3,256,1]);(out/'firetex11.h').write_text('#define FIRE_TPAGE 171u\n#define FIRE_CLUT 240u\n#define FIRE_UPLOAD_WORDS '+str(len(words))+'\nstatic const u32 fireupload[FIRE_UPLOAD_WORDS]={'+','.join(str(x)+'u' for x in words)+'};\n');np.save(out/'firetex11.npy',c[ix]);Image.fromarray(pal[ix,:3],'RGB').save(out/'fire_source.png');(out/'fire_texture_report.json').write_text(json.dumps(dict(filename=e['filename'],group=e['group'],hash=e['hash'],size=[w,h],source_alpha='uniformly zero',blend='PS1 additive approximation, black transparent',vram=[704,0,16,32],clut=[768,3,256,1],bytes=1536),indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('iso',type=Path);p.add_argument('out',type=Path);a=p.parse_args();extract(a.iso,a.out)
