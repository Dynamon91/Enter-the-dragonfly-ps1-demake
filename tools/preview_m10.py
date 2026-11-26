"""Host raster preview using the actual C fixed-point skinning function."""
import argparse,ctypes,subprocess,json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from preview_m09 import array
ROOT=Path(__file__).resolve().parents[1]
def preview(out):
 out=out.resolve();so=out/'rig_host.so';subprocess.run(['clang','-O2','-shared','-fPIC','-I',str(out),'-I',str(ROOT/'src'),str(ROOT/'tests/rig10_host.c'),'-o',str(so)],check=True);lib=ctypes.CDLL(str(so));lib.pose10.argtypes=[ctypes.c_int,ctypes.POINTER(ctypes.c_int)];z=np.load(out/'rig.npz');h=(out/'scene.h').read_text();faces=array(h,'faces').reshape(-1,3);uv=array(h,'uvwords').reshape(-1,3);clut=(uv[:,0]>>16)>>6;uv=np.stack([uv&255,(uv>>8)&255],axis=2);tex=[np.asarray(Image.open(out/f'actor_tex_{i}.png').convert('RGB'))//8*8 for i in range(3)];rep=json.loads((out/'rig_report.json').read_text());poses=np.empty((rep['frames'],len(z['vertices']),3),np.int32)
 for i in range(len(poses)):lib.pose10(i,poses[i].ctypes.data_as(ctypes.POINTER(ctypes.c_int)))
 np.savez_compressed(out/'poses_host.npz',poses=poses)
 def render(i,yaw=13):
  a=yaw*math.pi/32;rr=np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]]);p=poses[i]@rr.T+[0,0,440];xy=np.floor(p[:,:2]*280/p[:,2,None]+[160,120]).astype(int);im=np.empty((240,320,3),np.uint8);im[:]=[30,40,58];dep=p[faces,2].sum(1)//24
  for j in sorted(range(len(faces)),key=lambda j:(dep[j],j),reverse=True):
   a,b,c=xy[faces[j]];x0=max(0,min(a[0],b[0],c[0]));x1=min(319,max(a[0],b[0],c[0]));y0=max(0,min(a[1],b[1],c[1]));y1=min(239,max(a[1],b[1],c[1]));det=(b[0]-a[0])*(c[1]-a[1])-(c[0]-a[0])*(b[1]-a[1]);
   if det==0 or x1<x0 or y1<y0:continue
   yy,xx=np.mgrid[y0:y1+1,x0:x1+1];w1=((xx-a[0])*(c[1]-a[1])-(yy-a[1])*(c[0]-a[0]))/det;w2=((b[0]-a[0])*(yy-a[1])-(b[1]-a[1])*(xx-a[0]))/det;w0=1-w1-w2;mask=(w0>=-1e-6)&(w1>=-1e-6)&(w2>=-1e-6);st=w0[...,None]*uv[j,0]+w1[...,None]*uv[j,1]+w2[...,None]*uv[j,2];t=tex[int(clut[j])];ix=np.clip(st[...,0].astype(int),0,t.shape[1]-1);iy=np.clip(st[...,1].astype(int),0,t.shape[0]-1);im[y0:y1+1,x0:x1+1][mask]=t[iy[mask],ix[mask]]
  return Image.fromarray(im)
 sheet=Image.new('RGB',(960,3*266),(21,27,40));d=ImageDraw.Draw(sheet)
 for k,c in enumerate(rep['clips']):
  i=c['start']+c['frames']//2; x=k%3*320;y=k//3*266;sheet.paste(render(i),(x,y));d.text((x+10,y+246),c['name'].replace('_',' ').upper()+'  |  original curve data',fill='white')
 sheet.save(out/'animation_preview.png')
 # 30 Hz source poses shown at 15 fps, every other frame; loop only the idle animation.
 c=rep['clips'][0];imgs=[render(i) for i in range(c['start'],c['start']+c['frames'],2)];imgs[0].save(out/'idle_preview.gif',save_all=True,append_images=imgs[1:],duration=67,loop=0,disposal=2)
 print('host poses',poses.shape,'bounds',poses.min(),poses.max())
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('out',type=Path);preview(p.parse_args().out)
