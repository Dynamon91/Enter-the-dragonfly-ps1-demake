"""Orthographic software preview of the actual reduced mesh, not a screenshot."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
z=np.load(ROOT/'assets_m15/fodder_meshes.npz')
canvas=Image.new('RGB',(720,400),(26,30,41));d=ImageDraw.Draw(canvas)
for idx,(name,yaw,pitch) in enumerate([('sheep',.45,.23),('sheep',2.25,.18),('butterfly',.45,.88)]):
 t=z[name].astype(float);col=z['sheep_colors' if name=='sheep' else 'butterfly_colors'];x,y,zz=t.transpose(2,0,1);a=x*np.cos(yaw)-zz*np.sin(yaw);b=x*np.sin(yaw)+zz*np.cos(yaw);p=np.stack([a,y*np.cos(pitch)-b*np.sin(pitch),y*np.sin(pitch)+b*np.cos(pitch)],-1);xy=p[:,:,:2];lo=xy.min((0,1));hi=xy.max((0,1));scale=min(210/max(1,hi[0]-lo[0]),250/max(1,hi[1]-lo[1]));xy=(xy-(lo+hi)/2)*scale+[120+240*idx,190];
 for i in np.argsort(-p[:,:,2].mean(1)):
  c=int(col[i]);d.polygon([tuple(a) for a in xy[i]],fill=(c&255,(c>>8)&255,(c>>16)&255))
 d.text((12+240*idx,12),f'{name.title()} | {len(t)} triangles',fill='white')
d.text((12,370),'Source geometry and base-texture color samples | provisional rest pose and flat PS1 shading',fill=(192,200,216));canvas.save(ROOT/'build_m15/play/fodder_assets.png')
