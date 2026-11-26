"""Host approximation of the native farm renderer. Not an emulator."""
import argparse,re,math,ctypes,subprocess,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
def array(h,name):
 s=re.search(r'\b'+name+r'\[[^;=]+\]\s*=\{(.*?)\};',h,re.S).group(1);return np.array([int(x) for x in re.findall(r'\d+',s)],dtype=np.uint32)
def signed(x):return (x.astype(np.int64)+32768)%65536-32768
def preview(out):
 collect=ctypes.CDLL(str((out/"collect12_host.so").resolve()));I=ctypes.POINTER(ctypes.c_int);collect.collect_mesh12.argtypes=[I];collect.collect_status12.argtypes=[I];collect.collect_mesh12.restype=ctypes.c_int;positions=json.loads((ROOT/"assets_m12/collect_report.json").read_text())["active"]
 fire=ctypes.CDLL(str((out/"rig11_host.so").resolve()));I=ctypes.POINTER(ctypes.c_int);fire.fire_mesh11.argtypes=[ctypes.c_int,ctypes.c_int,I];fire.fire_mesh11.restype=ctypes.c_int;fire.pose11.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_int,I];fire.fire_status11.argtypes=[I]
 so=out/'clip_host.so';subprocess.run(['clang','-O2','-shared','-fPIC',str(ROOT/'tests/clip07_host.c'),'-o',str(so)],check=True);lib=ctypes.CDLL(str(so.resolve()));clipfn=lib.clip07;clipfn.argtypes=[ctypes.POINTER(ctypes.c_int),ctypes.POINTER(ctypes.c_int)];clipfn.restype=ctypes.c_int;
 z=np.load(out/'farm06.npz');v=z['vertices'];f=z['faces'];wuv=z['uv'];wtid=z['texture_id'];raw=z['textures'];wtex=np.stack([(raw&31)*8,((raw>>5)&31)*8,((raw>>10)&31)*8],axis=-1).astype(np.uint8);spawn=z['spawn'];h=(out/'scene.h').read_text();pv=array(h,'vertices').reshape(-1,2);av=np.column_stack([signed(pv[:,0]&65535),signed(pv[:,0]>>16),signed(pv[:,1]&65535)]);af=array(h,'faces').reshape(-1,3);uv=array(h,'uvwords').reshape(-1,3);texs=[np.asarray(Image.open(out/f'actor_tex_{i}.png').convert('RGB'))//8*8 for i in range(3)];clut=(uv[:,0]>>16)>>6;uv=np.stack([uv&255,(uv>>8)&255],axis=2).astype(float)
 def transform(v,p,yaw):
  sn=int(round(math.sin(yaw*math.pi/32)*4096));cs=int(round(math.cos(yaw*math.pi/32)*4096));cam=p-np.array([sn*560>>12,300,cs*560>>12]);q=v-cam;x,y,z=q.T;a=(cs*x-sn*z)>>12;b=(sn*x+cs*z)>>12;return np.column_stack([a,(3849*y-1401*b)>>12,(1401*y+3849*b)>>12])
 def clip(tri):
  a=np.ascontiguousarray(tri,dtype=np.int32);b=np.empty((16,5),dtype=np.int32);n=clipfn(a.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),b.ctypes.data_as(ctypes.POINTER(ctypes.c_int)))
  return [b[[0,i,i+1]].copy() for i in range(1,n-1)]
 def project(t):return np.clip(np.floor(t[:,:2]*220/t[:,2,None]+[160,120]),-1024,1023).astype(int)
 b=np.load(out/'visibility.npz');bounds=np.ascontiguousarray(b['clusters'],dtype=np.int16);ids=b['face_ids'];vlib=ctypes.CDLL(str((out/'visibility_host.so').resolve()));vis=vlib.visible09;vis.argtypes=[ctypes.POINTER(ctypes.c_int16)]+[ctypes.c_int]*5;vis.restype=ctypes.c_int
 def render(yaw,tick,mode):
  spawn=z["spawn"].copy();collect.collect_init12();
  if mode in (1,2):
   gem=np.array(positions[1]["sector_xyz"]);spawn=gem.copy();spawn[2]-=290 if mode==1 else 0;
   if mode==2:spawn[2]-=0
  collect.collect_pos12(*map(int,spawn),yaw)
  for _ in range(16):collect.collect_tick12(0)
  state=(ctypes.c_int*8)();collect.collect_status12(state)
  fire.fire_reset11()
  for _ in range(tick):fire.fire_step11(8192)
  av=np.zeros((len(pv),3),np.int32);fire.pose11(207+(tick-1)%38 if tick else 0,0,min(4,max(0,tick-1)) if tick else 4,av.ctypes.data_as(I))
  w=transform(v,spawn,yaw);p=transform(av+spawn-[0,99,0],spawn,yaw);packets=[]
  sn=round(math.sin(yaw*math.pi/32)*4096);cs=round(math.cos(yaw*math.pi/32)*4096);cam=(spawn-np.array([sn*560>>12,300,cs*560>>12])).tolist();keep=np.zeros(len(f),dtype=bool)
  for row in bounds:
   if vis(row.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),*cam,sn,cs):keep[ids[row[6]:row[6]+row[7]]]=True
  for j in np.flatnonzero(keep):
   idx=f[j]
   for t in clip(np.column_stack([w[idx],wuv[j]]).astype(float)):
    xy=project(t);packets.append((int(t[:,2].sum()/24),j,xy,t[:,3:]))
  for j,idx in enumerate(af):
   t=p[idx];
   for tt in clip(np.column_stack([t,uv[j]])):packets.append((int(tt[:,2].sum()/24),len(f)+j,project(tt),tt[:,3:]))
  ef=np.zeros((60,10),np.int32);ne=fire.fire_mesh11(sn,cs,ef.ctypes.data_as(I));ce=np.zeros((339,10),np.int32);nc=collect.collect_mesh12(ce.ctypes.data_as(I));ef=np.concatenate([ef[:ne][ef[:ne,9]>=0x01000000],ce[:nc]]);ne=len(ef);colors=ef[:ne,9].copy();ep=transform(ef[:ne,:9].reshape(-1,3),spawn,yaw).reshape(ne,3,3)
  for j,t in enumerate(ep):
   for tt in clip(np.column_stack([t,[[31,31] if colors[j]==0x02000000 else [0,0],[0,31],[31,0]]])):packets.append((int(tt[:,2].sum()/24),len(f)+len(af)+j,project(tt),tt[:,3:]))
  im=Image.new('RGB',(320,240),(84,113,153));d=ImageDraw.Draw(im);visible=0
  for _,i,xy,j in sorted(packets,key=lambda a:(a[0],a[1]),reverse=True):
   a,b,c=xy;x0=max(0,xy[:,0].min());x1=min(319,xy[:,0].max());y0=max(0,xy[:,1].min());y1=min(239,xy[:,1].max());det=(b[0]-a[0])*(c[1]-a[1])-(c[0]-a[0])*(b[1]-a[1]);
   if x1<x0 or y1<y0 or not det or np.ptp(xy[:,0])>=1024 or np.ptp(xy[:,1])>=512:continue
   visible+=1
   if i>=len(f)+len(af):
    rgb=int(colors[i-len(f)-len(af)])
    if rgb<0x01000000:d.polygon([tuple(q) for q in xy],fill=(rgb&255,(rgb>>8)&255,(rgb>>16)&255));continue
    yy,xx=np.mgrid[y0:y1+1,x0:x1+1];w1=((xx-a[0])*(c[1]-a[1])-(yy-a[1])*(c[0]-a[0]))/det;w2=((b[0]-a[0])*(yy-a[1])-(b[1]-a[1])*(xx-a[0]))/det;w0=1-w1-w2;mask=(w0>=-1e-6)&(w1>=-1e-6)&(w2>=-1e-6);st=w0[...,None]*j[0]+w1[...,None]*j[1]+w2[...,None]*j[2];src=np.load(out/'firetex11.npy')[np.clip(st[...,1].astype(int),0,31),np.clip(st[...,0].astype(int),0,31)];rgb=np.stack([(src&31)*8,((src>>5)&31)*8,((src>>10)&31)*8],-1);mask &= src!=0;crop=np.array(im.crop((x0,y0,x1+1,y1+1)));crop[mask]=np.minimum(248,crop[mask].astype(int)+rgb[mask]);im.paste(Image.fromarray(crop),(x0,y0));continue
   
   yy,xx=np.mgrid[y0:y1+1,x0:x1+1];w1=((xx-a[0])*(c[1]-a[1])-(yy-a[1])*(c[0]-a[0]))/det;w2=((b[0]-a[0])*(yy-a[1])-(b[1]-a[1])*(xx-a[0]))/det;w0=1-w1-w2;mask=(w0>=-1e-6)&(w1>=-1e-6)&(w2>=-1e-6);st=w0[...,None]*j[0]+w1[...,None]*j[1]+w2[...,None]*j[2];t=wtex[wtid[i]] if i<len(f) else texs[int(clut[i-len(f)])];ix=st[...,0].astype(int)%t.shape[1];iy=st[...,1].astype(int)%t.shape[0];
   if i<len(f):mask &= raw[wtid[i],iy,ix]!=0
   crop=np.array(im.crop((x0,y0,x1+1,y1+1)));crop[mask]=t[iy[mask],ix[mask]];im.paste(Image.fromarray(crop),(x0,y0));
  d=ImageDraw.Draw(im);d.rectangle((8,8,54,23),fill=(38,22,44));d.rectangle((13,13,18,18),fill=(72,232,56));d.text((23,10),f"{state[0]:03d}",fill="white");return im,visible,list(state)
 sheet=Image.new('RGB',(640,520),(19,23,31));d=ImageDraw.Draw(sheet);counts=[]
 for k,(yaw,tick,mode) in enumerate([(0,0,0),(0,0,1),(0,0,2),(8,10,0)]):
  im,n,status=render(yaw,tick,mode);counts.append({'tick':tick,'packets':n,'score':status[0],'collected':status[5:]});x=k%2*320;y=k//2*260;sheet.paste(im,(x,y+20));d.text((x+7,y+4),f'Gem score {status[0]:03d} | collected {sum(status[5:])}/3 | view {k+1}',fill='white')
 sheet.save(out/'collect_preview.png');print('preview',counts);(out/'collect_preview_counts.json').write_text(json.dumps(counts,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('out',type=Path);preview(p.parse_args().out)
