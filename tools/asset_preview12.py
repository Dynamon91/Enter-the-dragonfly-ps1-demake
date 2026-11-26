"""Offline actual mesh preview, not emulator output."""
import re,math,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
def render(out):
 s=(ROOT/'assets_m12/collectdata12.h').read_text();rep=json.loads((ROOT/'assets_m12/collect_report.json').read_text());
 def mesh(name):
  a=re.search(r'\b'+name+r'\[\d+\]=\{(.*?)\};',s,re.S).group(1);z=np.array([int(k) for k in re.findall(r'-?\d+',a)]).reshape(-1,10);return z[:,:9].reshape(-1,3,3),z[:,9]
 def panel(parts,size):
  v=np.concatenate([mesh(n)[0] for n in parts]);c=np.concatenate([mesh(n)[1] for n in parts]);v=v.astype(float);yaw=.57;pitch=.40;x,y,z=v.transpose(2,0,1);xx=np.cos(yaw)*x-np.sin(yaw)*z;zz=np.sin(yaw)*x+np.cos(yaw)*z;yy=np.cos(pitch)*y-np.sin(pitch)*zz;depth=np.sin(pitch)*y+np.cos(pitch)*zz;q=np.stack([xx,yy],-1);lo=q.min((0,1));hi=q.max((0,1));sc=min((size[0]-36)/max(hi[0]-lo[0],1),(size[1]-36)/max(hi[1]-lo[1],1));q=(q-(lo+hi)/2)*sc+np.array(size)/2;im=Image.new('RGB',size,(29,34,43));d=ImageDraw.Draw(im)
  for i in np.argsort(depth.mean(1))[::-1]:d.polygon([tuple(p) for p in q[i]],fill=(int(c[i]&255),int(c[i]>>8&255),int(c[i]>>16&255)))
  return im
 im=Image.new('RGB',(800,365),(19,23,31));d=ImageDraw.Draw(im);d.text((12,10),'Extracted original meshes | flat-shaded PS1 conversion preview',fill='white')
 for i,(v,lab) in enumerate([(1,'Red / 1'),(2,'Green / 2'),(5,'Purple / 5'),(25,'Gold / 25')]):
  p=panel(['gemmesh'+str(v)],(190,145));x=5+i*200;im.paste(p,(x,32));d.text((x+8,182),lab,fill='white')
 p=panel(['sparxbody','sparxwing1'],(340,142));im.paste(p,(5,208));d.text((360,238),'Sparx | reduced source mesh',fill='white');d.text((360,258),'149 body/eye + 28 wing triangles',fill='white');d.text((360,278),'Provisional colors and wing poses',fill='white');d.text((360,298),'Not an emulator screenshot',fill='white');im.save(out)
if __name__=='__main__':render(Path(__import__('sys').argv[1]))
