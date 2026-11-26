"""Host approximation of the native farm renderer. Not an emulator."""
import argparse,re,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
def array(h,name):
 s=re.search(r'\b'+name+r'\[[^;=]+\]\s*=\{(.*?)\};',h,re.S).group(1);return np.array([int(x) for x in re.findall(r'\d+',s)],dtype=np.uint32)
def signed(x):return (x.astype(np.int64)+32768)%65536-32768
def preview(out):
 z=np.load(out/'farm.npz');v=z['vertices'];f=z['faces'];colors=z['colors'];spawn=z['spawn'];h=(out/'scene.h').read_text();pv=array(h,'vertices').reshape(-1,2);av=np.column_stack([signed(pv[:,0]&65535),signed(pv[:,0]>>16),signed(pv[:,1]&65535)]);af=array(h,'faces').reshape(-1,3);uv=array(h,'uvwords').reshape(-1,3);texs=[np.asarray(Image.open(ROOT/'build_m04/spyro'/f'tex_{i}.png').convert('RGB'))//8*8 for i in [303,411,429]];clut=(uv[:,0]>>16)>>6;uv=np.stack([uv&255,(uv>>8)&255],axis=2).astype(float)
 def transform(v,p,yaw):
  sn=int(round(math.sin(yaw*math.pi/32)*4096));cs=int(round(math.cos(yaw*math.pi/32)*4096));cam=p-np.array([sn*560>>12,300,cs*560>>12]);q=v-cam;x,y,z=q.T;a=(cs*x-sn*z)>>12;b=(sn*x+cs*z)>>12;return np.column_stack([a,(3849*y-1401*b)>>12,(1401*y+3849*b)>>12])
 def clip(tri):
  out=[]
  for a,b in zip(tri,np.roll(tri,-1,axis=0)):
   if a[2]>=128:out.append(a)
   if (a[2]>=128)!=(b[2]>=128):out.append(a+(b-a)*((128-a[2])/(b[2]-a[2])))
  return [np.array([out[0],out[1],out[2]])]+([np.array([out[0],out[2],out[3]])] if len(out)==4 else []) if len(out)>=3 else []
 def project(t):return np.clip(np.floor(t[:,:2]*220/t[:,2,None]+[160,120]),-1024,1023).astype(int)
 def render(yaw):
  w=transform(v,spawn,yaw);p=transform(av+spawn-[0,99,0],spawn,yaw);packets=[]
  for j,idx in enumerate(f):
   for t in clip(w[idx].astype(float)):
    xy=project(t);packets.append((int(t[:,2].sum()/24),j,xy,None))
  for j,idx in enumerate(af):
   t=p[idx];
   if np.min(t[:,2])>=128:packets.append((int(t[:,2].sum()/24),len(f)+j,project(t),j))
  im=Image.new('RGB',(320,240),(84,113,153));d=ImageDraw.Draw(im);visible=0
  for _,i,xy,j in sorted(packets,key=lambda a:(a[0],a[1]),reverse=True):
   a,b,c=xy;x0=max(0,xy[:,0].min());x1=min(319,xy[:,0].max());y0=max(0,xy[:,1].min());y1=min(239,xy[:,1].max());det=(b[0]-a[0])*(c[1]-a[1])-(c[0]-a[0])*(b[1]-a[1]);
   if x1<x0 or y1<y0 or not det or np.ptp(xy[:,0])>=1024 or np.ptp(xy[:,1])>=512:continue
   visible+=1
   if j is None:d.polygon([tuple(q) for q in xy],fill=tuple(colors[i]));continue
   yy,xx=np.mgrid[y0:y1+1,x0:x1+1];w1=((xx-a[0])*(c[1]-a[1])-(yy-a[1])*(c[0]-a[0]))/det;w2=((b[0]-a[0])*(yy-a[1])-(b[1]-a[1])*(xx-a[0]))/det;w0=1-w1-w2;mask=(w0>=-1e-6)&(w1>=-1e-6)&(w2>=-1e-6);st=w0[...,None]*uv[j,0]+w1[...,None]*uv[j,1]+w2[...,None]*uv[j,2];t=texs[int(clut[j])];ix=np.clip(st[...,0].astype(int),0,t.shape[1]-1);iy=np.clip(st[...,1].astype(int),0,t.shape[0]-1);crop=np.array(im.crop((x0,y0,x1+1,y1+1)));crop[mask]=t[iy[mask],ix[mask]];im.paste(Image.fromarray(crop),(x0,y0));
  return im,visible
 sheet=Image.new('RGB',(640,480));counts=[]
 for k,yaw in enumerate([0,16,32,48]):
  im,n=render(yaw);counts.append(n);sheet.paste(im,(k%2*320,k//2*240))
 sheet.save(out/'farm_preview.png');print('visible packets',counts)
 # Source geometry map (all regions); top view draws triangles colored by region metadata.
 hub=np.load(out.parent/'hub'/'hub.npz');vv=hub['vertices'];ff=hub['faces'];parts=hub['part'];import json
 meta=json.loads((out.parent/'hub'/'hub_report.json').read_text())['meshes'];col={'CASTLE':(156,166,203),'RIVER':(90,166,210),'WOOD':(78,145,97),'FARM':(213,177,92),'BEACH':(222,195,145),'ALWAYS':(150,145,160),'THE':(123,133,127)};mn=vv[:,[0,2]].min(0);mx=vv[:,[0,2]].max(0);xy=((vv[:,[0,2]]-mn)/(mx-mn)*[870,650]+[25,25]).astype(int);xy[:,1]=700-xy[:,1];im=Image.new('RGB',(920,730),(22,29,40));d=ImageDraw.Draw(im)
 for i in np.argsort(vv[ff,1].mean(1)):
  name=meta[parts[i]]['name'];key=name.split('_')[1] if name.startswith('HUB_') else 'THE';d.polygon([tuple(q) for q in xy[ff[i]]],fill=col.get(key,(150,150,150)))
 origin=np.array([40000,4000]);corn=np.array([origin-4096,origin+4096]);rect=((corn-mn)/(mx-mn)*[870,650]+[25,25]).astype(int);rect[:,1]=700-rect[:,1];d.rectangle((rect[0,0],rect[1,1],rect[1,0],rect[0,1]),outline=(255,255,255),width=2);d.text((rect[0,0],rect[1,1]-15),'TEST SECTOR',fill='white');d.text((25,705),'Original Dragon Realms render geometry / region colors are diagnostic',fill='white');im.save(out/'hub_map.png')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('out',type=Path);preview(p.parse_args().out)
