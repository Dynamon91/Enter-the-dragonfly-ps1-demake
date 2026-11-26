"""Conservative alpha conversion for candidate textures. No verified bindings claimed."""
import json,re,struct
from pathlib import Path
import numpy as np
from PIL import Image
from recover import records,pxt_groups

def apply(iso,out):
 r=records(iso);groups=list(pxt_groups(r[772][1]));rep=json.loads((out/'report.json').read_text());z=np.load(out/'farm06.npz');data={k:z[k] for k in z.files};old=data['textures'].copy();h=(out/'world.h').read_text();m=re.search(r'(static const u32 worldupload\[WORLD_UPLOAD_WORDS\]=\{)([^}]+)(\};)',h);words=[int(x) for x in re.findall(r'\d+',m[2])];offset=0
 for k,b in enumerate(rep['bindings']):
  _,pal,imgs=groups[b['group']];ix=np.asarray(Image.fromarray(imgs[0][2]).resize((64,64),Image.Resampling.NEAREST));rgb=pal.astype(np.uint16);color=np.maximum((rgb[:,0]>>3)|((rgb[:,1]>>3)<<5)|((rgb[:,2]>>3)<<10),1)
  # Constant alpha is ambiguous in PS2 data; a mask would be all-or-nothing.
  # Preserve RGB of these candidates for diagnostics; varying-alpha foliage remains masked.
  a=rgb[ix,3];vary=np.ptp(a)>0
  if b['name'] in ('largeivy','wheat','yellow_T','treeygrass_tr','onlyhay') and vary:color=np.where(rgb[:,3]<64,0,color)
  color=color.astype('<u2'); assert words[offset]==0xa0000000 and words[offset+2]==(1<<16)|256;words[offset+3:offset+131]=np.frombuffer(color.tobytes(),'<u4').tolist();offset+=131;assert words[offset]==0xa0000000;offset+=3+1024
  data['textures'][k]=color[ix];b['alpha_policy']='varying alpha mask' if vary and b['name'] in ('largeivy','wheat','yellow_T','treeygrass_tr','onlyhay') else 'opaque candidate diagnostic';b['transparent_pixels_before']=int((old[k]==0).sum());b['transparent_pixels_after']=int((data['textures'][k]==0).sum())
 assert offset==len(words);(out/'world.h').write_text(h[:m.start(2)]+','.join(str(x)+'u' for x in words)+h[m.end(2):]);np.savez_compressed(out/'farm06.npz',**data);(out/'report.json').write_text(json.dumps(rep,indent=2));print([(b['name'],b['transparent_pixels_before'],b['transparent_pixels_after']) for b in rep['bindings'] if b['transparent_pixels_before']!=b['transparent_pixels_after']])
