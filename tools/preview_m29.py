"""Host rendering of the streamed terrain and recovered animated actor; not an emulator."""
from pathlib import Path
import json,struct,subprocess,ctypes as C,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from preview_scene10 import array,signed
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'build_m29/play';A=ROOT/'assets_m27';OLD=ROOT/'build_m16/play'
def build():
 from preview_sky28 import Sky
 sky=Sky()
 m=json.loads((A/'sector_manifest.json').read_text());colors=[tuple(x['rgb']) for x in m['materials']];data=(P/'DOJOSECT.DAT').read_bytes();td=(A/'DOJOTEX.DAT').read_bytes();ti=(A/'DOJOTEX.IDX').read_bytes();tg={};masks={};oldtg={}
 for i in range(52):
  g,lba,crc=struct.unpack_from('<III',ti,12+i*12);o=lba*2048+24;pal=np.frombuffer(td[o:o+512],dtype='<u2');pix=np.frombuffer(td[o+512:o+4608],dtype=np.uint8).reshape(64,64);tg[g]=(np.stack([pal&31,(pal>>5)&31,(pal>>10)&31],axis=1)*8).astype(np.uint8)[pix];masks[g]=pal[pix]!=0;oldtg[g]=tg[g]
 groups=[x['texture_group'] for x in m['materials']];blocks=m['blocks'];h=(P/'scene.h').read_text();af=array(h,'faces').reshape(-1,3);uv=array(h,'uvwords').reshape(-1,3);clut=(uv[:,0]>>16)>>6;uv=np.stack([uv&255,(uv>>8)&255],axis=2);poses=np.load(OLD/'poses_host.npz')['poses'];tex=[np.asarray(Image.open(OLD/f'actor_tex_{i}.png').convert('RGB'))//8*8 for i in range(3)];so=P/'clip_host.so';subprocess.run(['clang','-O2','-shared','-fPIC',str(ROOT/'tests/clip07_host.c'),'-o',str(so)],check=True);fn=C.CDLL(str(so)).clip07;fn.argtypes=[C.POINTER(C.c_int),C.POINTER(C.c_int)];fn.restype=C.c_int
 def tris(id):
  b=blocks[id];p=data[b['lba']*2048:];return [(np.array(struct.unpack_from('<9h',p,64+j*36)).reshape(3,3)+b['origin'],struct.unpack_from('<H',p,64+j*36+30)[0],np.array(struct.unpack_from('<6h',p,64+j*36+18)).reshape(3,2)) for j in range(b['render'])]
 import re
 h='\n'.join((P/n).read_text() for n in ('collectdata12.h','basketmesh21.h','foddermesh21.h','ninjamesh29.h'));meshes={}
 for name,body in re.findall(r'static const CollectFace (\w+)\[\d*\]=\{(.*?)\};',h,re.S):
  nums=np.array([int(a) for a in re.findall(r'-?\d+',body)],dtype=int).reshape(-1,10);meshes[name]=(nums[:,:9].reshape(-1,3,3),nums[:,9])
 allgems=[o for o in m['objects'] if o['kind']==1]
 def render(r,frame,state=None,alpha=True,diagnostic=None):
  pos=np.array([r['x'],r['y'],r['z']]);yaw=r["heading"];sn=round(math.sin(yaw*math.pi/32)*4096);cs=round(math.cos(yaw*math.pi/32)*4096);cam=pos-np.array([sn*560>>12,300,cs*560>>12]);pack=[]
  def trans(v):
   q=v-cam;x,y,z=q.T;a=(cs*x-sn*z)>>12;b=(sn*x+cs*z)>>12;return np.column_stack([a,(3849*y-1401*b)>>12,(1401*y+3849*b)>>12])
  def add(q,i,depth=0):
   if 0<=i<53 and groups[i] in tg:
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
  av=poses[frame].astype(int);av=np.column_stack([(cs*av[:,0]+sn*av[:,2])>>12,av[:,1],(cs*av[:,2]-sn*av[:,0])>>12])+pos-[0,99,0]
  for j,f in enumerate(af):emit(av[f],uv[j],53+j)
  if state is not None:
   def mesh(name,xyz,angle,scale=4):
    vv,cc=meshes[name];sn=round(math.sin(angle*math.pi/32)*4096);cs=round(math.cos(angle*math.pi/32)*4096);x,y,z=(vv*scale//4).transpose(2,0,1);v=np.stack([(cs*x+sn*z)>>12,y,(cs*z-sn*x)>>12],axis=2)+np.array(xyz)
    for tri,c in zip(v,cc):emit(tri,np.zeros((3,2),dtype=int),-1-int(c))
   for g in allgems:
    if g['record_offset'] in state['taken']:continue
    xyz=np.rint(np.array(g['source_xyz'])*[1,-1,1]).astype(int);q=xyz-pos
    if abs(q[0])>1536 or abs(q[2])>1536:continue
    mesh('gemmesh'+str(g['value']),xyz-[0,16,0],state['tick']&63)
   mesh('sparxbody',state['sparx'],0);phase=(state['tick']//2)&3;mesh('sparxwing'+str(1 if phase==1 else 2 if phase==3 else 0),state['sparx'],0)
   for o in m['objects']:
    if 'ninja_riptoc' not in o['edf'].lower() or o['record_offset'] in state.get('dead',[]):continue
    xyz=np.rint(np.array(o['source_xyz'])*[1,-1,1]).astype(int);q=xyz-pos
    if max(abs(q[0]),abs(q[2]))>1400:continue
    angle=round(math.atan2(-q[0],-q[2])*32/math.pi)%64;mesh('ninja29mesh',xyz,angle,5 if o['edf'].lower().startswith('large') else 4)
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
    if q[:,0].min()>1536 or q[:,0].max()<-1536 or q[:,2].min()>1536 or q[:,2].max()<-1536:continue
    emit(v,st,i)
  firetex=np.array(Image.open(ROOT/'assets_m11/fire_source.png').convert('RGB'))//8*8
  im=sky.render(yaw)[0];d=ImageDraw.Draw(im)
  for _,i,xy,st in sorted(reversed(pack[:12000]),key=lambda p:p[0],reverse=True):
   if i<0:
    c=-1-i;d.polygon([tuple(q) for q in xy],fill=((c&248),((c>>8)&248),((c>>16)&248)));continue
   if i<53 and groups[i] not in tg:d.polygon([tuple(q) for q in xy],fill=colors[i]);continue
   a,b,c=xy;x0=max(0,xy[:,0].min());x1=min(319,xy[:,0].max());y0=max(0,xy[:,1].min());y1=min(239,xy[:,1].max());det=(b[0]-a[0])*(c[1]-a[1])-(c[0]-a[0])*(b[1]-a[1]);
   if not det or x1<x0 or y1<y0:continue
   yy,xx=np.mgrid[y0:y1+1,x0:x1+1];w1=((xx-a[0])*(c[1]-a[1])-(yy-a[1])*(c[0]-a[0]))/det;w2=((b[0]-a[0])*(yy-a[1])-(b[1]-a[1])*(xx-a[0]))/det;w0=1-w1-w2;mask=(w0>=0)&(w1>=0)&(w2>=0);s=w0[...,None]*st[0]+w1[...,None]*st[1]+w2[...,None]*st[2];t=firetex if i==32767 else (tg if alpha else oldtg)[groups[i]] if i<53 else tex[int(clut[i-53])];
   if alpha and i<53:mask&=masks[groups[i]][s[...,1].astype(int)%64,s[...,0].astype(int)%64]
   crop=np.array(im.crop((x0,y0,x1+1,y1+1)));sample=t[s[...,1].astype(int)[mask]%t.shape[0],s[...,0].astype(int)[mask]%t.shape[1]];crop[mask]=np.minimum(255,crop[mask].astype(int)+sample) if i==32767 else sample;im.paste(Image.fromarray(crop),(x0,y0))
  return im,len(pack)
 font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
 import sys
 sys.path.insert(0,str(ROOT/'tests'))
 from test_m29 import M29
 M29.setUpClass();t=M29();w=t.new();L=t.L
 im=Image.new('RGB',(1000,610),(19,26,35));d=ImageDraw.Draw(im);d.text((16,10),'Dragonfly Dojo | v0.29 original Ninja Riptocs',font=font(25),fill='white');d.text((16,43),'Source-positioned encounters • reconstructed stationary combat • host render',font=font(14),fill=(175,190,204))
 for k,case in enumerate(json.loads((P/'combat_test.json').read_text())['combat']):
  large,i,x,f,z=case;o=next(o for o in t.enemies if L.eid29(o['record_offset'])==i)
  choices=[]
  for heading in range(0,64,8):
   px=x-round(math.sin(heading*math.pi/32)*360);pz=z-round(math.cos(heading*math.pi/32)*360)
   if not t.load(w,px,pz):continue
   py=L.cache18_floor(w,px,pz,f,110)
   if py!=32767:choices.append((abs(py-f),heading,px,py,pz))
  _,heading,px,py,pz=min(choices) if choices else (0,0,x,f,z)
  ids=[b['id'] for b in blocks if b['bounds'][0][0]<=((px//512)*512+256)+1792 and b['bounds'][1][0]>=((px//512)*512+256)-1792 and b['bounds'][0][2]<=((pz//512)*512+256)+1792 and b['bounds'][1][2]>=((pz//512)*512+256)-1792]
  r=dict(x=px,y=py,z=pz,heading=heading,ids=ids);state=dict(taken=[],sparx=[px-110,py-190,pz-45],tick=0,dead=[])
  for q in range(2):
   if q:state['dead']=[o['record_offset']]
   img,n=render(r,0,state);xx=16+q*330;yy=77+k*267;im.paste(img,(xx,yy));d.text((xx,yy-18),('Large' if large else 'Small')+' Riptoc | '+('defeated state' if q else 'intact state'),font=font(13),fill='white');print(k,q,n)
 # close-up of actual reduced mesh (orthographic painter's algorithm).
 vv,cc=meshes['ninja29mesh'];
 for k,ang in enumerate([0,24]):
  s0,c0=math.sin(ang*math.pi/32),math.cos(ang*math.pi/32);p=vv.astype(float);xx=p[:,:,0]*c0-p[:,:,2]*s0;zz=p[:,:,0]*s0+p[:,:,2]*c0;yy=p[:,:,1]*.94-zz*.342;depth=p[:,:,1]*.342+zz*.94;xy=np.stack([xx,yy],axis=2);lo=xy.min((0,1));hi=xy.max((0,1));xy=(xy-(lo+hi)/2)*min(275/(hi[0]-lo[0]),200/(hi[1]-lo[1]))+[830,197+k*267];
  for j in np.argsort(depth.mean(1))[::-1]:
   col=int(cc[j]);d.polygon([tuple(v) for v in xy[j]],fill=(col&255,(col>>8)&255,(col>>16)&255))
  d.text((680,66+k*267),'Reduced original main mesh',font=font(13),fill='white')
 d.text((16,594),'Staged host visualization at recovered source positions. Eye meshes, textures and original AI still incomplete.',font=font(11),fill=(175,190,204));im.save(P/'ninja_preview.png')
if __name__=='__main__':build()
