"""Host rendering of the streamed terrain and recovered animated actor; not an emulator."""
from pathlib import Path
import json,struct,subprocess,ctypes as C,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from preview_scene10 import array,signed
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'build_m21/play';A=ROOT/'assets_m16';OLD=ROOT/'build_m16/play'
def build():
 m=json.loads((A/'sector_manifest.json').read_text());t=json.loads((A/'texture_report.json').read_text());rgb={x['group']:tuple(x['average_rgb']) for x in t['entries']};colors=[rgb.get(x['texture_group'],(190,110,155)) for x in m['materials']];data=(A/'HUBSECT.DAT').read_bytes();td=(ROOT/'assets_m20/HUBTEX.DAT').read_bytes();oldtd=(A/'HUBTEX.DAT').read_bytes();tg={};masks={};oldtg={};
 for e in t['entries']:
  o=e['lba']*2048+24;pal=np.frombuffer(td[o:o+512],dtype='<u2');rgb5=np.stack([pal&31,(pal>>5)&31,(pal>>10)&31],axis=1);tg[e['group']]=(rgb5*8).astype(np.uint8)[np.frombuffer(td[o+512:o+4608],dtype=np.uint8).reshape(64,64)]
  masks[e['group']]=(pal[np.frombuffer(td[o+512:o+4608],dtype=np.uint8).reshape(64,64)]!=0);op=np.frombuffer(oldtd[o:o+512],dtype='<u2');oldtg[e['group']]=(np.stack([op&31,(op>>5)&31,(op>>10)&31],axis=1)*8).astype(np.uint8)[np.frombuffer(oldtd[o+512:o+4608],dtype=np.uint8).reshape(64,64)]
 groups=[x['texture_group'] for x in m['materials']];route=json.loads((P/'route18.json').read_text());blocks=m['blocks'];h=(P/'scene.h').read_text();af=array(h,'faces').reshape(-1,3);uv=array(h,'uvwords').reshape(-1,3);clut=(uv[:,0]>>16)>>6;uv=np.stack([uv&255,(uv>>8)&255],axis=2);poses=np.load(OLD/'poses_host.npz')['poses'];tex=[np.asarray(Image.open(OLD/f'actor_tex_{i}.png').convert('RGB'))//8*8 for i in range(3)];so=P/'clip_host.so';subprocess.run(['clang','-O2','-shared','-fPIC',str(ROOT/'tests/clip07_host.c'),'-o',str(so)],check=True);fn=C.CDLL(str(so)).clip07;fn.argtypes=[C.POINTER(C.c_int),C.POINTER(C.c_int)];fn.restype=C.c_int
 def tris(id):
  b=blocks[id];p=data[b['lba']*2048:];return [(np.array(struct.unpack_from('<9h',p,64+j*36)).reshape(3,3)+b['origin'],struct.unpack_from('<H',p,64+j*36+30)[0],np.array(struct.unpack_from('<6h',p,64+j*36+18)).reshape(3,2)) for j in range(b['render'])]
 import re
 h='\n'.join((P/n).read_text() for n in ('collectdata12.h','basketmesh21.h','foddermesh21.h'));meshes={}
 for name,body in re.findall(r'static const CollectFace (\w+)\[\d*\]=\{(.*?)\};',h,re.S):
  nums=np.array([int(a) for a in re.findall(r'-?\d+',body)],dtype=int).reshape(-1,10);meshes[name]=(nums[:,:9].reshape(-1,3,3),nums[:,9])
 states=json.loads((P/'collect_route20.json').read_text());allgems=[o for o in m['objects'] if o['kind']==1]
 def render(r,frame,state=None,alpha=True,diagnostic=None):
  pos=np.array([r['x'],r['y'],r['z']]);yaw=8;sn=2896;cs=2896;cam=pos-np.array([sn*560>>12,300,cs*560>>12]);pack=[]
  def trans(v):
   q=v-cam;x,y,z=q.T;a=(cs*x-sn*z)>>12;b=(sn*x+cs*z)>>12;return np.column_stack([a,(3849*y-1401*b)>>12,(1401*y+3849*b)>>12])
  def add(q,i,depth=0):
   if 0<=i<208 and groups[i] in tg:
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
  av=poses[frame].astype(int);av=av+pos-[0,99,0]
  for j,f in enumerate(af):emit(av[f],uv[j],208+j)
  if state is not None:
   def mesh(name,xyz,angle):
    vv,cc=meshes[name];sn=round(math.sin(angle*math.pi/32)*4096);cs=round(math.cos(angle*math.pi/32)*4096);x,y,z=vv.transpose(2,0,1);v=np.stack([(cs*x+sn*z)>>12,y,(cs*z-sn*x)>>12],axis=2)+np.array(xyz)
    for tri,c in zip(v,cc):emit(tri,np.zeros((3,2),dtype=int),-1-int(c))
   for g in allgems:
    if g['record_offset'] in state['taken']:continue
    xyz=np.rint(np.array(g['source_xyz'])*[1,-1,1]).astype(int);q=xyz-pos
    if abs(q[0])>1200 or abs(q[2])>1200:continue
    mesh('gemmesh'+str(g['value']),xyz-[0,16,0],state['tick']&63)
   mesh('sparxbody',state['sparx'],0);phase=(state['tick']//2)&3;mesh('sparxwing'+str(1 if phase==1 else 2 if phase==3 else 0),state['sparx'],0)
   if diagnostic:
    target=diagnostic['target'];st=diagnostic['state'];kind=diagnostic['kind']
    if kind=='basket':
     if st['state']==0:mesh('basketmesh',target,0)
     elif st['state']==1:mesh('gemmesh1',np.array(target)-[0,66,0],0)
     for x,y,z,life in st['fire']:
      radius=13+(13-life)*3;dx=cs*radius>>12;dz=sn*radius>>12;v=np.array([[x-dx,y-radius,z+dz],[x-dx,y+radius,z+dz],[x+dx,y-radius,z-dz],[x+dx,y+radius,z-dz]])
      for tri in [[0,1,2],[2,1,3]]:emit(v[tri],np.array([[0,0],[0,31],[31,0],[31,31]])[tri],32767)
    elif st['state']==0:mesh('sheepmesh',target,0)
    elif st['state']==1:mesh('buttermesh',st['butterfly'],st['tick']*4)
  for id in r['ids']:
   for v,i,st in tris(id):
    q=v-pos
    if q[:,0].min()>1200 or q[:,0].max()<-1200 or q[:,2].min()>1200 or q[:,2].max()<-1200:continue
    emit(v,st,i)
  firetex=np.array(Image.open(ROOT/'assets_m11/fire_source.png').convert('RGB'))//8*8
  im=Image.new('RGB',(320,240),(84,113,153));d=ImageDraw.Draw(im)
  for _,i,xy,st in sorted(reversed(pack[:10000]),key=lambda p:p[0],reverse=True):
   if i<0:
    c=-1-i;d.polygon([tuple(q) for q in xy],fill=((c&248),((c>>8)&248),((c>>16)&248)));continue
   if i<208 and groups[i] not in tg:d.polygon([tuple(q) for q in xy],fill=colors[i]);continue
   a,b,c=xy;x0=max(0,xy[:,0].min());x1=min(319,xy[:,0].max());y0=max(0,xy[:,1].min());y1=min(239,xy[:,1].max());det=(b[0]-a[0])*(c[1]-a[1])-(c[0]-a[0])*(b[1]-a[1]);
   if not det or x1<x0 or y1<y0:continue
   yy,xx=np.mgrid[y0:y1+1,x0:x1+1];w1=((xx-a[0])*(c[1]-a[1])-(yy-a[1])*(c[0]-a[0]))/det;w2=((b[0]-a[0])*(yy-a[1])-(b[1]-a[1])*(xx-a[0]))/det;w0=1-w1-w2;mask=(w0>=0)&(w1>=0)&(w2>=0);s=w0[...,None]*st[0]+w1[...,None]*st[1]+w2[...,None]*st[2];t=firetex if i==32767 else (tg if alpha else oldtg)[groups[i]] if i<208 else tex[int(clut[i-208])];
   if alpha and i<208:mask&=masks[groups[i]][s[...,1].astype(int)%64,s[...,0].astype(int)%64]
   crop=np.array(im.crop((x0,y0,x1+1,y1+1)));sample=t[s[...,1].astype(int)[mask]%t.shape[0],s[...,0].astype(int)[mask]%t.shape[1]];crop[mask]=np.minimum(255,crop[mask].astype(int)+sample) if i==32767 else sample;im.paste(Image.fromarray(crop),(x0,y0))
  return im,len(pack)
 font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
 im=Image.new('RGB',(1004,635),(19,26,35));d=ImageDraw.Draw(im);d.text((18,10),'Dragon Realms | v0.21 streamed interactions',font=font(25),fill='white');d.text((18,43),'Host tests at original object coordinates — recovered geometry, textures and fire sprite',font=font(15),fill=(175,190,204))
 for row,(name,kind) in enumerate([('fire_route21.json','basket'),('sheep_route21.json','sheep')]):
  q=json.loads((P/name).read_text());st=q['states'];pos=q['position'];r=dict(zip(('x','y','z'),pos),ids=q['ids']);picks=[0,min(2,len(st)-1),len(st)-1] if row==0 else [0,1,len(st)-1];labels=['Fire emitted','Fire approaches basket','Basket broken; gem released'] if row==0 else ['Original sheep; health 2/3','Charge hit; butterfly released','Butterfly consumed; health 3/3']
  for k,index in enumerate(picks):
   x=18+k*329;y=90+row*282;state=dict(taken=[],sparx=[pos[0]-110,pos[1]-190,pos[2]-45],tick=index);img,n=render(r,(207+index if row==0 else 125 if index==1 else 0),state,True,dict(kind=kind,target=q['target'],state=st[index]));hud=ImageDraw.Draw(img);hp=st[index].get("health",3);hud.rectangle((249,4,304,18),fill=(35,32,38));[hud.rectangle((254+j*15,8,264+j*15,14),fill=(248,216,64) if j<hp else (58,58,58)) for j in range(3)];im.paste(img,(x,y));d.text((x,y-21),labels[k],font=font(14),fill='white');print(kind,index,n)
 d.text((18,619),'Reconstructed mechanics; provisional object shading. Not an emulator screenshot.',font=font(13),fill=(175,190,204));im.save(P/'interact_preview.png')
if __name__=='__main__':build()
