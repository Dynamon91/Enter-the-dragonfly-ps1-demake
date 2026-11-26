"""Host reference rasterization of actual PS1-converted enemy meshes and poses."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];A=R/'assets_m30';P=R/'build_m30/play'
z=np.load(A/'ninja.npz');faces=z['faces'];uv=z['uv'];mat=z['materials'];pal=z['palettes'];pix=z['pixels'];tex=(np.stack([pal&31,(pal>>5)&31,(pal>>10)&31],axis=2)*8).astype(np.uint8);tex=np.array([tex[i][pix[i]] for i in range(2)])
def render(frame,angle,scale=0.64):
 v=z['frames'][frame].astype(float);a=np.deg2rad(angle);x=np.cos(a)*v[:,0]+np.sin(a)*v[:,2];d=-np.sin(a)*v[:,0]+np.cos(a)*v[:,2];y=v[:,1]*.96+d*.28;depth=-v[:,1]*.28+d*.96;xy=np.stack([x*scale+160,y*scale+214],axis=1);im=np.zeros((240,320,3),np.uint8);im[:]=[30,42,56];db=np.full((240,320),-np.inf)
 for f,st,m in zip(faces,uv,mat):
  a,b,c=xy[f];x0=max(0,int(np.floor(min(a[0],b[0],c[0]))));x1=min(319,int(np.ceil(max(a[0],b[0],c[0]))));y0=max(0,int(np.floor(min(a[1],b[1],c[1]))));y1=min(239,int(np.ceil(max(a[1],b[1],c[1]))));det=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
  if abs(det)<1e-8 or x1<x0 or y1<y0:continue
  yy,xx=np.mgrid[y0:y1+1,x0:x1+1];w1=((xx-a[0])*(c[1]-a[1])-(yy-a[1])*(c[0]-a[0]))/det;w2=((b[0]-a[0])*(yy-a[1])-(b[1]-a[1])*(xx-a[0]))/det;w0=1-w1-w2;dep=w0*depth[f[0]]+w1*depth[f[1]]+w2*depth[f[2]];dview=db[y0:y1+1,x0:x1+1];mask=(w0>=0)&(w1>=0)&(w2>=0)&(dep>dview);t=w0[...,None]*st[0]+w1[...,None]*st[1]+w2[...,None]*st[2];im[y0:y1+1,x0:x1+1][mask]=tex[m][t[...,1].astype(int)[mask]%64,t[...,0].astype(int)[mask]%64];dview[mask]=dep[mask]
 return Image.fromarray(im)
def main():
 canvas=Image.new('RGB',(1000,610),(19,26,35));d=ImageDraw.Draw(canvas);font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n);d.text((16,12),'Ninja Riptoc | v0.30 original eyes, UVs and animation',font=font(25),fill='white');d.text((16,45),'Host reference rasterizer (depth buffer) • PS1 8-bit texture palettes • original pose data',font=font(14),fill=(180,195,210));
 for i,(f,a,label) in enumerate([(0,0,'Rest pose | front'),(0,45,'Rest pose | three-quarter'),(0,180,'Rest pose | back'),(4,0,'Idle sample 4'),(8,30,'Idle sample 8'),(15,25,'Ready sample 3')]):
  x=16+i%3*330;y=84+i//3*265;canvas.paste(render(f,a),(x,y));d.text((x,y-18),label,font=font(13),fill='white')
 d.text((16,591),'Eyelids and specular layer omitted; native ordering-table rendering remains unverified.',font=font(12),fill=(180,195,210));canvas.save(P/'ninja30_preview.png')
if __name__=='__main__':main()
