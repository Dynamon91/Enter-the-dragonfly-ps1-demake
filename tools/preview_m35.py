"""Reference rasterizer for the four recovered textured quest meshes (not emulator)."""
from pathlib import Path
import numpy as np,json
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];P=R/'build_m35/play';A=R/'assets_m35';z=np.load(A/'questmodels.npz');rep=json.loads((A/'report.json').read_text());pal=z['palettes'];tex=(np.stack([pal&31,(pal>>5)&31,(pal>>10)&31],axis=2)*8).astype(np.uint8);tex=np.array([tex[i][z['pixels'][i]] for i in range(len(pal))]);
def render(i,yaw,w=320,h=224):
 v=z[f'v{i}'].astype(float);f=z[f'f{i}'];u=z[f'u{i}'];m=z[f'm{i}'];a=np.deg2rad(yaw);x=np.cos(a)*v[:,0]+np.sin(a)*v[:,2];dep=-np.sin(a)*v[:,0]+np.cos(a)*v[:,2];y=.96*v[:,1]+.28*dep;dep=.96*dep-.28*v[:,1];xy=np.stack([x,y],1);scale=min((w-30)/max(1,np.ptp(x)),(h-20)/max(1,np.ptp(y)));xy=(xy-(xy.min(0)+xy.max(0))/2)*scale+[w/2,h/2];im=np.zeros((h,w,3),np.uint8);im[:]=[38,50,64];db=np.full((h,w),-np.inf)
 for face,uv,mat in zip(f,u,m):
  a,b,c=xy[face];lo=np.maximum(0,np.floor(xy[face].min(0)).astype(int));hi=np.minimum([w-1,h-1],np.ceil(xy[face].max(0)).astype(int));det=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
  if abs(det)<1e-8 or np.any(hi<lo):continue
  x0,y0=lo;x1,y1=hi;yy,xx=np.mgrid[y0:y1+1,x0:x1+1];p=((xx-a[0])*(c[1]-a[1])-(yy-a[1])*(c[0]-a[0]))/det;q=((b[0]-a[0])*(yy-a[1])-(b[1]-a[1])*(xx-a[0]))/det;t=1-p-q;dd=t*dep[face[0]]+p*dep[face[1]]+q*dep[face[2]];view=db[y0:y1+1,x0:x1+1];mask=(p>=0)&(q>=0)&(t>=0)&(dd>view);uvp=t[...,None]*uv[0]+p[...,None]*uv[1]+q[...,None]*uv[2];im[y0:y1+1,x0:x1+1][mask]=tex[mat][uvp[...,1].astype(int)[mask]%64,uvp[...,0].astype(int)[mask]%64];view[mask]=dd[mask]
 return Image.fromarray(im)
def main():
 im=Image.new('RGB',(1024,690),(20,27,37));d=ImageDraw.Draw(im);font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n);white=(240,245,250);muted=(180,195,210);d.text((16,14),'Dragonfly Dojo | v0.35 recovered quest models',font=font(26),fill=white);d.text((16,49),'Original EDF model associations • original texture palettes • static bind poses',font=font(15),fill=muted)
 for i in range(3):
  x=16+334*i;d.text((x,79),rep['models'][i]['name']+' | '+rep['models'][i]['resource'].upper(),font=font(15),fill=white);im.paste(render(i,25),(x,104));d.text((x,333),f"{rep['models'][i]['triangles']} triangles • two original eyes",font=font(14),fill=muted)
 d.text((16,365),'Shared KITE.MRB | all three quest prop definitions',font=font(17),fill=white);im.paste(render(3,75,480,242),(16,393));im.paste(render(3,160,480,242),(512,393));d.text((16,640),'Original rest geometry including tail, ribbons and string. No recovered motion animation applied yet.',font=font(14),fill=muted);d.text((16,665),'Host reference rasterization with depth buffer; native PS1 ordering-table visuals remain unverified.',font=font(13),fill=muted);im.save(P/'questmodels_preview.png')
if __name__=='__main__':main()
