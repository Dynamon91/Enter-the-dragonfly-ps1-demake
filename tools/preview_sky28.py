"""Rasterize the exact native sky command stream with a host projection and affine sampling."""
from pathlib import Path
import ctypes as C, math,subprocess,json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'build_m28/play';A=ROOT/'assets_m28';CAP=100000
class Sky:
 def __init__(self):
  so=P/'skyhost28.so';subprocess.run(['clang','-O2','-shared','-fPIC','-DSKY_HOST_CAP=100000','-I',str(P),'-I',str(ROOT/'src'),str(ROOT/'tests/sky28_host.c'),'-o',str(so)],check=True);self.fn=C.CDLL(str(so)).skyhost28;self.fn.argtypes=[C.c_int,C.c_int,C.POINTER(C.c_uint32)];self.fn.restype=C.c_int;z=np.load(A/'sky.npz');self.pal=z['palettes'];self.pix=z['pixels'];c=json.loads((P/'report.json').read_text())['sky_clear_rgb'];self.clear=np.array([c&255,(c>>8)&255,(c>>16)&255]);self.sine=[round(math.sin(i*math.pi/32)*4096) for i in range(64)]
 def packets(self,yaw):
  b=np.empty(CAP,dtype=np.uint32);n=self.fn(self.sine[yaw%64],self.sine[(yaw+16)%64],b.ctypes.data_as(C.POINTER(C.c_uint32)));assert 0<n<CAP and (n-1)%8==0 and b[n-1]==0xe2000000
  for p in b[:n-1].reshape(-1,8):
   layer=(int(p[0])>>10&31)//8;assert layer in range(4);assert int(p[1])>>24==(0x25 if layer==0 else 0x27);xy=np.stack([p[[2,4,6]]&65535,p[[2,4,6]]>>16],axis=1).astype(np.int16).astype(int);uv=np.stack([p[[3,5,7]]&255,(p[[3,5,7]]>>8)&255],axis=1).astype(int);yield layer,xy,uv,p
 def render(self,yaw):
  img=np.broadcast_to(self.clear,(240,320,3)).copy().astype(np.uint8);coverage=np.zeros((240,320),bool)
  for layer,xy,uv,p in self.packets(yaw):
   a,b,c=xy;det=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);x0=max(0,xy[:,0].min());x1=min(319,xy[:,0].max());y0=max(0,xy[:,1].min());y1=min(239,xy[:,1].max());
   if not det or x0>x1 or y0>y1:continue
   yy,xx=np.mgrid[y0:y1+1,x0:x1+1];w1=((xx-a[0])*(c[1]-a[1])-(yy-a[1])*(c[0]-a[0]))/det;w2=((b[0]-a[0])*(yy-a[1])-(b[1]-a[1])*(xx-a[0]))/det;w0=1-w1-w2;mask=(w0>=0)&(w1>=0)&(w2>=0);st=(w0[...,None]*uv[0]+w1[...,None]*uv[1]+w2[...,None]*uv[2]).astype(int);pc=self.pal[layer,self.pix[layer,st[...,1]%64,st[...,0]%64]];mask&=pc!=0;rgb=np.stack([pc&31,(pc>>5)&31,(pc>>10)&31],axis=-1).astype(int)*8;crop=img[y0:y1+1,x0:x1+1];sample=rgb[mask];old=crop[mask].astype(int)
   if layer==0:coverage[y0:y1+1,x0:x1+1]|=mask
   crop[mask]=sample if layer==0 else (old+sample)//2 if layer==3 else np.minimum(248,old+sample)
  return Image.fromarray(img),coverage
if __name__=='__main__':
 s=Sky();im=Image.new('RGB',(1280,480));counts=[]
 for k,y in enumerate(range(0,64,8)):
  a,c=s.render(y);im.paste(a,((k%4)*320,(k//4)*240));counts.append((y,int(c.sum()),len(list(s.packets(y)))))
 im.save(P/'sky_angles.png');print(counts)
