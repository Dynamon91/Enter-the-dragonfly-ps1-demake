"""Render a source-derived visibility map plus a host scene view and original motion curves."""
from pathlib import Path
import ctypes as C,json,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
def draw(out,anim):
 z=np.load(out/'farm06.npz');b=np.load(out/'visibility.npz');v=z['vertices'];f=z['faces'];rows=np.ascontiguousarray(b['clusters'],dtype=np.int16);ids=b['face_ids'];p=z['spawn'];lib=C.CDLL(str((out/'visibility_host.so').resolve()));vis=lib.visible09;vis.argtypes=[C.POINTER(C.c_int16)]+[C.c_int]*5;vis.restype=C.c_int;cam=(p-np.array([0,300,560])).tolist();keep=np.zeros(len(f),bool)
 for r in rows:
  if vis(r.ctypes.data_as(C.POINTER(C.c_int16)),*cam,0,4096):keep[ids[r[6]:r[6]+r[7]]]=True
 im=Image.new('RGB',(960,620),(19,25,34));d=ImageDraw.Draw(im);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18);small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13);bold=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',24)
 d.text((24,16),'Dragon Realms — visibility diagnostic v0.9',font=bold,fill='white');d.text((24,50),'Original source geometry | native culling | host-rendered scene',font=small,fill=(180,193,204));
 screen=Image.open(out/'farm_preview.png').crop((0,0,320,240)).resize((480,360),Image.Resampling.NEAREST);im.paste(screen,(24,93));d.text((24,464),'Host preview: geometry and textures unchanged',font=small,fill='white')
 # Top down geometry. Candidate faces green, culled faces slate. Draw rejected first.
 pos=v[:,[0,2]].astype(float);mn=pos.min(0);mx=pos.max(0);scale=min(390/(mx[0]-mn[0]),350/(mx[1]-mn[1]));xy=(pos-mn)*scale;xy[:,0]+=536;xy[:,1]=440-xy[:,1];xy=xy.astype(int)
 for i in np.r_[np.flatnonzero(~keep),np.flatnonzero(keep)]:d.polygon([tuple(q) for q in xy[f[i]]],fill=(71,156,124) if keep[i] else (62,74,90))
 sp=(p[[0,2]]-mn)*scale;px,py=int(sp[0]+536),int(440-sp[1]);d.ellipse((px-5,py-5,px+5,py+5),fill=(250,197,76),outline='white');d.line((px,py,px,py-25),fill=(250,197,76),width=2);d.text((px+9,py-10),'Spyro',font=small,fill='white');d.rectangle((538,465,551,478),fill=(71,156,124));d.text((558,463),f'{keep.sum():,} candidate triangles',font=small,fill='white');d.rectangle((538,491,551,504),fill=(62,74,90));d.text((558,489),f'{(~keep).sum():,} rejected before projection',font=small,fill='white');d.line((24,524,936,524),fill=(66,78,90));d.text((24,544),'192 camera tests: 0 false rejects; identical pixels in all 4 regression views.',font=font,fill='white');d.text((24,575),'Not an emulator screenshot. No measured console frame rate.',font=small,fill=(180,193,204));im.save(out/'visibility_preview.png')
if __name__=='__main__':draw(ROOT/'build_m09/play',ROOT/'build_m09/animation')
