"""Fast host model rasterization and measured capture trace, not emulator output."""
from pathlib import Path
import numpy as np,json
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];P=R/'build_m33/play';z=np.load(R/'assets_m33/dragonfly.npz')
def model(phase,yaw):
 t=np.concatenate([z['dfbody33'],z[f'dfwing{phase}33']]).astype(float);col=np.concatenate([z['dfbody33_color'],z[f'dfwing{phase}33_color']]);a=np.deg2rad(yaw);x=np.cos(a)*t[...,0]+np.sin(a)*t[...,2];depth=-np.sin(a)*t[...,0]+np.cos(a)*t[...,2];y=.96*t[...,1]+.28*depth;depth=.96*depth-.28*t[...,1];xy=np.stack([x*1.6+160,y*1.6+215],axis=2);im=np.zeros((240,320,3),np.uint8);im[:]=[36,48,62];db=np.full((240,320),-np.inf)
 for tri,dep,c in zip(xy,depth,col):
  a,b,d=tri;lo=np.maximum(0,np.floor(tri.min(0)).astype(int));hi=np.minimum([319,239],np.ceil(tri.max(0)).astype(int));det=np.cross(b-a,d-a)
  if abs(det)<1e-8 or np.any(hi<lo):continue
  x0,y0=lo;x1,y1=hi;yy,xx=np.mgrid[y0:y1+1,x0:x1+1];u=((xx-a[0])*(d[1]-a[1])-(yy-a[1])*(d[0]-a[0]))/det;v=((b[0]-a[0])*(yy-a[1])-(b[1]-a[1])*(xx-a[0]))/det;w=1-u-v;zz=w*dep[0]+u*dep[1]+v*dep[2];view=db[y0:y1+1,x0:x1+1];mask=(u>=0)&(v>=0)&(w>=0)&(zz>view);view[mask]=zz[mask];im[y0:y1+1,x0:x1+1][mask]=[c&248,(c>>8)&248,(c>>16)&248]
 return Image.fromarray(im)
def main():
 im=Image.new('RGB',(1016,628),(19,26,35));d=ImageDraw.Draw(im);font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n);white=(240,245,250);muted=(176,194,211)
 d.text((16,12),'Dragonfly Dojo | v0.33 bubble capture',font=font(26),fill=white);d.text((16,48),'Recovered shared character geometry and palette samples; three original wing poses',font=font(15),fill=muted)
 for i,(p,yaw) in enumerate([(0,0),(1,25),(2,-35)]):
  x=16+i*334;im.paste(model(p,yaw),(x,92));d.text((x,72),f'Wing pose {p+1} | {yaw}°',font=font(13),fill=white)
 traces=json.loads((P/'capture_trace.json').read_text());d.text((16,350),'Measured host capture traces (top-down, relative to player)',font=font(18),fill=white)
 for i,t in enumerate(traces):
  x=16+i*500;y=386;d.rounded_rectangle((x,y,x+484,y+196),radius=8,fill=(34,45,58));d.text((x+12,y+10),f"Source placement {i+1} | captured on update 4",font=font(15),fill=white);base=x+35;yy=y+103;d.line((base,yy,base+408,yy),fill=(105,124,144),width=2);d.ellipse((base-7,yy-7,base+7,yy+7),fill=(168,110,214));d.text((base-8,yy+22),'Spyro',font=font(12),fill=muted);dist=t['source'][2]-t['player'][2];end=base+int(dist*1.55);d.ellipse((end-8,yy-8,end+8,yy+8),outline=(255,180,100),width=3);d.text((end-75,yy+22),'Dragonfly',font=font(12),fill=muted)
  for st in t['rows'][:-1]:
   b=st['bubbles'][0];xx=base+int((b[2]-t['player'][2])*1.55);d.ellipse((xx-9,yy-9,xx+9,yy+9),outline=(126,218,248),width=2);d.text((xx-5,yy-30),str(st['t']+1),font=font(12),fill=white)
  d.text((x+12,y+163),'Capture persists across sector reload.',font=font(13),fill=muted)
 d.text((16,604),'Host model rasterizer and actual test traces; not a gameplay screenshot. Materials and flight are provisional.',font=font(12),fill=muted);im.save(P/'capture33_preview.png')
if __name__=='__main__':main()
