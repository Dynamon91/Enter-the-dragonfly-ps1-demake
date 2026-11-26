"""Host rendering of the streamed terrain and recovered animated actor; not an emulator."""
from pathlib import Path
import json,struct,subprocess,ctypes as C,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from preview_scene10 import array,signed
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'build_m19/play';A=ROOT/'assets_m16';OLD=ROOT/'build_m16/play'
def build():
 m=json.loads((A/'sector_manifest.json').read_text());t=json.loads((A/'texture_report.json').read_text());rgb={x['group']:tuple(x['average_rgb']) for x in t['entries']};colors=[rgb.get(x['texture_group'],(190,110,155)) for x in m['materials']];data=(A/'HUBSECT.DAT').read_bytes();td=(A/'HUBTEX.DAT').read_bytes();tg={};
 for e in t['entries']:
  o=e['lba']*2048+24;pal=np.frombuffer(td[o:o+512],dtype='<u2');rgb5=np.stack([pal&31,(pal>>5)&31,(pal>>10)&31],axis=1);tg[e['group']]=(rgb5*8).astype(np.uint8)[np.frombuffer(td[o+512:o+4608],dtype=np.uint8).reshape(64,64)]
 groups=[x['texture_group'] for x in m['materials']];route=json.loads((P/'route18.json').read_text());blocks=m['blocks'];h=(P/'scene.h').read_text();af=array(h,'faces').reshape(-1,3);uv=array(h,'uvwords').reshape(-1,3);clut=(uv[:,0]>>16)>>6;uv=np.stack([uv&255,(uv>>8)&255],axis=2);poses=np.load(OLD/'poses_host.npz')['poses'];tex=[np.asarray(Image.open(OLD/f'actor_tex_{i}.png').convert('RGB'))//8*8 for i in range(3)];so=P/'clip_host.so';subprocess.run(['clang','-O2','-shared','-fPIC',str(ROOT/'tests/clip07_host.c'),'-o',str(so)],check=True);fn=C.CDLL(str(so)).clip07;fn.argtypes=[C.POINTER(C.c_int),C.POINTER(C.c_int)];fn.restype=C.c_int
 def tris(id):
  b=blocks[id];p=data[b['lba']*2048:];return [(np.array(struct.unpack_from('<9h',p,64+j*36)).reshape(3,3)+b['origin'],struct.unpack_from('<H',p,64+j*36+30)[0],np.array(struct.unpack_from('<6h',p,64+j*36+18)).reshape(3,2)) for j in range(b['render'])]
 def render(r,frame):
  pos=np.array([r['x'],r['y'],r['z']]);yaw=48;sn=-4096;cs=0;cam=pos-np.array([sn*560>>12,300,cs*560>>12]);pack=[]
  def trans(v):
   q=v-cam;x,y,z=q.T;a=(cs*x-sn*z)>>12;b=(sn*x+cs*z)>>12;return np.column_stack([a,(3849*y-1401*b)>>12,(1401*y+3849*b)>>12])
  def add(q,i,depth=0):
   if i<208 and groups[i] in tg:
    base=(q[:,3:].min(0)//1024)*1024
    if np.any(q[:,3:].max(0)-base>=4096):
     if depth>=12:return
     edge=max(range(3),key=lambda j:np.abs(q[j,3:]-q[(j+1)%3,3:]).sum());a,b,c=q[[edge,(edge+1)%3,(edge+2)%3]];mid=np.trunc((a+b)/2).astype(int);add(np.array([a,mid,c]),i,depth+1);add(np.array([mid,b,c]),i,depth+1);return
    q=q.copy();q[:,3:]=(q[:,3:]-base)//16
   xy=np.clip(np.floor(q[:,:2]*220/q[:,2,None]+[160,120]),-1024,1023).astype(int);aa,bb,cc=xy;det=(bb[0]-aa[0])*(cc[1]-aa[1])-(bb[1]-aa[1])*(cc[0]-aa[0])
   if det and xy[:,0].max()>=0 and xy[:,0].min()<=319 and xy[:,1].max()>=0 and xy[:,1].min()<=239:pack.append((min(1023,int(q[:,2].sum()/24)),i,xy,q[:,3:]))
  def emit(v,st,i):
   a=np.ascontiguousarray(np.column_stack([trans(v),st]),dtype=np.int32);b=np.empty((16,5),dtype=np.int32);n=fn(a.ctypes.data_as(C.POINTER(C.c_int)),b.ctypes.data_as(C.POINTER(C.c_int)))
   for k in range(1,n-1):add(b[[0,k,k+1]].copy(),i)
  av=poses[frame].astype(int);av=np.column_stack([-av[:,2],av[:,1],av[:,0]])+pos-[0,99,0]
  for j,f in enumerate(af):emit(av[f],uv[j],208+j)
  for id in r['ids']:
   for v,i,st in tris(id):
    q=v-pos
    if q[:,0].min()>1200 or q[:,0].max()<-1200 or q[:,2].min()>1200 or q[:,2].max()<-1200:continue
    emit(v,st,i)
  im=Image.new('RGB',(320,240),(84,113,153));d=ImageDraw.Draw(im)
  for _,i,xy,st in sorted(pack[:10000],key=lambda p:p[0],reverse=True):
   if i<208 and groups[i] not in tg:d.polygon([tuple(q) for q in xy],fill=colors[i]);continue
   a,b,c=xy;x0=max(0,xy[:,0].min());x1=min(319,xy[:,0].max());y0=max(0,xy[:,1].min());y1=min(239,xy[:,1].max());det=(b[0]-a[0])*(c[1]-a[1])-(c[0]-a[0])*(b[1]-a[1]);
   if not det or x1<x0 or y1<y0:continue
   yy,xx=np.mgrid[y0:y1+1,x0:x1+1];w1=((xx-a[0])*(c[1]-a[1])-(yy-a[1])*(c[0]-a[0]))/det;w2=((b[0]-a[0])*(yy-a[1])-(b[1]-a[1])*(xx-a[0]))/det;w0=1-w1-w2;mask=(w0>=0)&(w1>=0)&(w2>=0);s=w0[...,None]*st[0]+w1[...,None]*st[1]+w2[...,None]*st[2];t=tg[groups[i]] if i<208 else tex[int(clut[i-208])];crop=np.array(im.crop((x0,y0,x1+1,y1+1)));crop[mask]=t[s[...,1].astype(int)[mask]%t.shape[0],s[...,0].astype(int)[mask]%t.shape[1]];im.paste(Image.fromarray(crop),(x0,y0))
  return im,len(pack)
 font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n);im=Image.new('RGB',(1004,625),(19,26,35));d=ImageDraw.Draw(im);d.text((18,10),'Dragon Realms | textured streaming v0.19',font=font(25),fill='white');d.text((18,42),'Host reconstruction of disc-resident terrain, original textures and animated Spyro',font=font(15),fill=(175,190,204));counts=[]
 for k,index in enumerate([0,38,77]):
  r=route[index];v,n=render(r,30+index%8);counts.append(n);x=18+k*329;im.paste(v,(x,75));d.text((x,320),f'Step {index:02}  |  {len(r["ids"])} blocks  |  {r["reads"]} reads',font=font(13),fill='white');d.text((x,338),', '.join(map(str,r['ids'])),font=font(12),fill=(175,190,204))
 # actual top-down terrain, with source path overlaid
 ids=sorted({i for r in route for i in r['ids']});rows=[q for i in ids for q in tris(i)];points=np.array([[r['x'],r['z']] for r in route]);xmin,xmax=points[:,0].min()-800,points[:,0].max()+800;zmin,zmax=points[:,1].min()-1100,points[:,1].max()+1100;scale=min(930/(xmax-xmin),200/(zmax-zmin));project=lambda x,z:(int(502+(x-(xmin+xmax)/2)*scale),int(487-(z-(zmin+zmax)/2)*scale));mp=Image.new('RGB',(968,220),(29,39,50));g=ImageDraw.Draw(mp);pp=lambda x,z:tuple(np.array(project(x,z))-[18,377]);
 for v,i,_ in sorted(rows,key=lambda q:-q[0][:,1].sum()):g.polygon([pp(x,z) for x,y,z in v],fill=colors[i]);
 path=[pp(x,z) for x,z in points];g.line(path,fill=(255,240,90),width=4)
 for index in [0,38,77]:x,z=path[index];g.ellipse((x-5,z-5,x+5,z+5),fill=(255,240,90),outline=(25,20,25),width=2);g.text((x+9,z-18),str(index),fill='white',font=font(13))
 im.paste(mp,(18,377));d.text((18,359),'Verified traversal route (2,926 world units)',font=font(14),fill='white');d.text((18,602),'Original base textures; opaque conversion and affine projection. Host diagnostic, not an emulator screenshot.',font=font(12),fill=(175,190,204));im.save(P/'textured_preview.png');print('host projected packet counts',counts)
if __name__=='__main__':build()
