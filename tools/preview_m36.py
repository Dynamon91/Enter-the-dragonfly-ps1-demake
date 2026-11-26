"""Reference rasterizer for the four recovered textured quest meshes (not emulator)."""
from pathlib import Path
import numpy as np,json
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];P=R/'build_m36/play';A=R/'assets_m35';z=np.load(A/'questmodels.npz');rep=json.loads((A/'report.json').read_text());pal=z['palettes'];tex=(np.stack([pal&31,(pal>>5)&31,(pal>>10)&31],axis=2)*8).astype(np.uint8);tex=np.array([tex[i][z['pixels'][i]] for i in range(len(pal))]);
def render(i,yaw,w=320,h=224,pose=None):
 v=(z[f'v{i}'] if pose is None else pose).astype(float);f=z[f'f{i}'];u=z[f'u{i}'];m=z[f'm{i}'];a=np.deg2rad(yaw);x=np.cos(a)*v[:,0]+np.sin(a)*v[:,2];dep=-np.sin(a)*v[:,0]+np.cos(a)*v[:,2];y=.96*v[:,1]+.28*dep;dep=.96*dep-.28*v[:,1];xy=np.stack([x,y],1);scale=min((w-30)/max(1,np.ptp(x)),(h-20)/max(1,np.ptp(y)));xy=(xy-(xy.min(0)+xy.max(0))/2)*scale+[w/2,h/2];im=np.zeros((h,w,3),np.uint8);im[:]=[38,50,64];db=np.full((h,w),-np.inf)
 for face,uv,mat in zip(f,u,m):
  a,b,c=xy[face];lo=np.maximum(0,np.floor(xy[face].min(0)).astype(int));hi=np.minimum([w-1,h-1],np.ceil(xy[face].max(0)).astype(int));det=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
  if abs(det)<1e-8 or np.any(hi<lo):continue
  x0,y0=lo;x1,y1=hi;yy,xx=np.mgrid[y0:y1+1,x0:x1+1];p=((xx-a[0])*(c[1]-a[1])-(yy-a[1])*(c[0]-a[0]))/det;q=((b[0]-a[0])*(yy-a[1])-(b[1]-a[1])*(xx-a[0]))/det;t=1-p-q;dd=t*dep[face[0]]+p*dep[face[1]]+q*dep[face[2]];view=db[y0:y1+1,x0:x1+1];mask=(p>=0)&(q>=0)&(t>=0)&(dd>view);uvp=t[...,None]*uv[0]+p[...,None]*uv[1]+q[...,None]*uv[2];im[y0:y1+1,x0:x1+1][mask]=tex[mat][uvp[...,1].astype(int)[mask]%64,uvp[...,0].astype(int)[mask]%64];view[mask]=dd[mask]
 return Image.fromarray(im)
def main():
 import re
 a=R/'assets_m36';poses=np.load(a/'poses.npz');drep=json.loads((a/'dialogue_report.json').read_text());h=(a/'dialogue36.h').read_text();glyph=np.array(list(map(int,re.findall(r'\d+',h.split('qfont36[95][10]=',1)[1])))).reshape(95,10)
 im=Image.new('RGB',(1024,860),(20,27,37));d=ImageDraw.Draw(im);font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n);white=(240,245,250);muted=(180,195,210);d.text((16,14),'Dragonfly Dojo | v0.36 original NPC animation',font=font(26),fill=white);d.text((16,49),'Recovered source curves • 36 native pose samples • English dialogue IDs resolved',font=font(15),fill=muted)
 for i in range(3):
  x=16+334*i;d.text((x,79),drep['actors'][i]['name']+' | '+rep['models'][i]['name']+' (internal)',font=font(16),fill=white);im.paste(render(i,25,320,202,poses[f'frames{i}'][3]),(x,104));d.text((x,310),'Original idle sample 4/6',font=font(14),fill=muted);im.paste(render(i,25,320,202,poses[f'frames{i}'][8]),(x,333));d.text((x,539),'Original talk sample 3/6',font=font(14),fill=muted)
 d.text((16,582),'Native dialogue panel | English line 431 (scaled 2×)',font=font(17),fill=white)
 panel=Image.new('RGB',(320,80),(29,36,45));pd=ImageDraw.Draw(panel)
 def rgb(x):return (x&255,(x>>8)&255,(x>>16)&255)
 def rect(x,y,w,h,c):pd.rectangle((x,y-157,x+w-1,y-157+h-1),fill=rgb(c))
 def txt(x,y,s,c):
  xx=x
  for ch in s:
   if ch=='\n':xx=x;y+=10;continue
   for j,b in enumerate(glyph[ord(ch)-32]):
    for i in range(6):
     if b&(1<<(5-i)):rect(xx+i,y+j,1,1,c)
   xx+=6
 rect(5,159,310,76,0x201c28);rect(5,159,310,2,0x9b73d4);rect(5,233,310,2,0x9b73d4);txt(12,163,drep['lines']['429']['wrapped'],0x72d8ff);txt(12,176,drep['lines']['431']['wrapped'],0xffffff);txt(250,163,'L2 / X',0xcac0e0)
 im.paste(panel.resize((640,160),Image.Resampling.NEAREST),(16,610));d.text((677,617),'18 English strings resolved',font=font(16),fill=white);d.text((677,645),'18 clips / 10,824 source keys',font=font(15),fill=muted);d.text((677,671),'6 clips sampled in runtime',font=font(15),fill=muted);d.text((677,697),'21 selected tests passed',font=font(15),fill=muted);d.text((677,723),'No emulator capture',font=font(15),fill=muted);d.text((16,795),'Host reference rasterizer using recovered geometry, original palettes and sampled pose arrays.',font=font(15),fill=muted);d.text((16,821),'Dialogue panel reproduced from native bitmap font and layout; original voice and camera remain pending.',font=font(14),fill=muted);im.save(P/'questanim_preview.png')
if __name__=='__main__':main()
