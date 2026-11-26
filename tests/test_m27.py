import ctypes as C,json,struct,unittest,sys,math,zlib
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];P=R/'build_m27/play';A=R/'assets_m27';sys.path.insert(0,str(R/'tools'))
from disc16 import raw
CB=C.CFUNCTYPE(C.c_int,C.c_void_p,C.c_uint32,C.c_uint32,C.POINTER(C.c_ubyte))
class Collect(C.Structure):_fields_=[('taken',C.c_ubyte*193)]+[(n,C.c_int) for n in 'score tick sx sy sz target events assist'.split()]
class M27(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  L=cls.L=C.CDLL(str(P/'host27.so'));cls.idx=(P/'DOJOSECT.IDX').read_bytes();cls.dat=(P/'DOJOSECT.DAT').read_bytes();cls.man=json.loads((A/'sector_manifest.json').read_text());cls.b=cls.man['blocks'];cls.good=CB(lambda ctx,lba,n,p:(C.memmove(p,cls.dat[lba*2048:(lba+n)*2048],n*2048),1)[1]);L.cache22_size.restype=C.c_uint32;L.cache18_init.argtypes=[C.c_void_p];L.cache18_update.argtypes=[C.c_void_p,C.c_char_p,C.c_uint32,C.c_uint32,C.c_int,C.c_int,CB,C.c_void_p];L.cache23_move.argtypes=[C.c_void_p,C.c_char_p,C.c_uint32,C.c_uint32,C.c_int,C.c_int,C.c_int,C.c_int,CB,C.c_void_p];L.cache18_floor.argtypes=[C.c_void_p,C.c_int,C.c_int,C.c_int,C.c_int];L.cache22_id.argtypes=[C.c_void_p,C.c_int];L.cache22_data.argtypes=[C.c_void_p,C.c_int];L.cache22_data.restype=C.c_void_p
  for n in ['cache22_count','cache22_bytes','cache22_reads']:getattr(L,n).argtypes=[C.c_void_p]
  L.greset21.argtypes=[C.POINTER(Collect),C.c_int,C.c_int,C.c_int];L.gstep21.argtypes=[C.POINTER(Collect),C.c_void_p,C.c_int,C.c_int,C.c_int,C.c_int,C.c_int]
 def new(self):w=C.create_string_buffer(self.L.cache22_size());self.L.cache18_init(w);return w
 def load(self,w,x,z,cb=None):return self.L.cache18_update(w,self.idx,len(self.idx),len(self.dat)//2048,x,z,cb or self.good,None)
 def ids(self,w):return [self.L.cache22_id(w,i) for i in range(self.L.cache22_count(w))]
 def test_neighborhoods(self):
  w=self.new();lo=np.array([b['bounds'][0] for b in self.b]);hi=np.array([b['bounds'][1] for b in self.b]);seen={}
  for x in range(lo[:,0].min()//512*512-2048,hi[:,0].max()+2048,512):
   for z in range(lo[:,2].min()//512*512-2048,hi[:,2].max()+2048,512):
    a=x+256;c=z+256;ids=tuple(int(i) for i in np.where((lo[:,0]<=a+1792)&(hi[:,0]>=a-1792)&(lo[:,2]<=c+1792)&(hi[:,2]>=c-1792))[0]);
    if ids:seen.setdefault(ids,(a,c))
  peak=0
  for ids,(x,z) in seen.items():
   self.assertTrue(self.load(w,x,z));self.assertEqual(tuple(self.ids(w)),ids);peak=max(peak,self.L.cache22_bytes(w))
   for j,i in enumerate(ids):b=self.b[i];p=b['lba']*2048;self.assertEqual(C.string_at(self.L.cache22_data(w,j),b['size']),self.dat[p:p+b['size']])
  print('neighborhoods',len(seen),'peak',peak,'max blocks',max(map(len,seen)));(P/'coverage.json').write_text(json.dumps(dict(sets=len(seen),peak=peak,max_blocks=max(map(len,seen)))))
 def test_objects(self):
  w=self.new();supported={};gems=[]
  for o in self.man['objects']:
   x,y,z=map(round,o['source_xyz']);self.assertTrue(self.load(w,x,z));f=self.L.cache18_floor(w,x,z,-y,110);kind='gem' if o['kind']==1 else 'basket' if o['edf'].lower()=='basket1.edf' else 'other';supported.setdefault(kind,[0,0]);supported[kind][0]+=1;supported[kind][1]+=f!=32767
   if kind=='gem' and f!=32767:gems.append((o,x,f,z))
  self.assertTrue(gems);o,x,y,z=gems[0];self.assertTrue(self.load(w,x,z));s=Collect();self.L.greset21(C.byref(s),x,y,z);self.L.gstep21(C.byref(s),w,x,y,z,0,3);self.assertGreaterEqual(s.score,o['value']);old=s.score;self.assertTrue(self.load(w,10534,-14914));self.assertTrue(self.load(w,x,z));self.L.gstep21(C.byref(s),w,x,y,z,0,0);self.assertEqual(s.score,old);print('object coverage',supported,'gem score',old);(P/'objects.json').write_text(json.dumps(supported))
 def test_spawn_route(self):
  # actual disc transport mock; movement mirrors the native floor and prefetch logic.
  L=self.L;d=(P/'ETD_PSX_M27.bin').read_bytes();L.mock17_setup.argtypes=[C.c_char_p,C.c_uint,C.c_uint];L.cd17_read.argtypes=[C.c_void_p,C.c_uint32,C.c_uint32,C.c_void_p];L.iso17_pvd.argtypes=[C.c_void_p,C.POINTER(C.c_uint32)];L.iso17_find.argtypes=[C.c_void_p,C.c_char_p,C.c_uint32,C.POINTER(C.c_uint32)];L.mock17_setup(d,len(d)//2352,0);self.assertTrue(L.cd17_init());buf=C.create_string_buffer(2048);v=(C.c_uint32*2)();ext=(C.c_uint32*2)();self.assertTrue(L.cd17_read(None,16,1,buf));self.assertTrue(L.iso17_pvd(buf,v));self.assertTrue(L.cd17_read(None,v[1],1,buf));self.assertTrue(L.iso17_find(buf,b'DOJOSECT.DAT;1',v[0],ext));cb=CB(lambda ctx,lba,n,p:L.cd17_read(None,ext[0]+lba,n,p));
  best=[]
  for heading in [0,16,32,48,8,24,40,56]:
   w=self.new();x,z=10534,-14914;self.assertTrue(self.load(w,x,z,cb));y=L.cache18_floor(w,x,z,-2075,110);self.assertNotEqual(y,32767);route=[dict(x=x,y=y,z=z,ids=self.ids(w),heading=heading)];dx=round(math.sin(heading*math.pi/32)*4096)*38>>12;dz=round(math.cos(heading*math.pi/32)*4096)*38>>12
   for i in range(110):
    nx,nz=x+dx,z+dz;mid=L.cache18_floor(w,int((x+nx)/2),int((z+nz)/2),y,110);f=L.cache18_floor(w,nx,nz,y,110)
    if mid==32767 or f==32767:break
    for j in range(16):
     if L.cache23_move(w,self.idx,len(self.idx),len(self.dat)//2048,x,z,nx,nz,cb,None):break
    else:break
    x,y,z=nx,f,nz;route.append(dict(x=x,y=y,z=z,ids=self.ids(w),heading=heading))
   if len(route)>len(best):best=route
  self.assertGreater(len(best),20);self.assertGreater(len({tuple(r['ids']) for r in best}),1);(P/'route.json').write_text(json.dumps(best));print('route',len(best)-1,'sets',len({tuple(r['ids']) for r in best}),'heading',best[0]['heading'])
 def test_assets(self):
  a=(A/'DOJOSECT.DAT').read_bytes();changed=0
  for b in self.b:
   off=b['lba']*2048;end=off+b['size'];n=off+64+36*b['render']+24*b['collision'];self.assertEqual(a[off+64:n],self.dat[off+64:n]);self.assertEqual(zlib.crc32(self.dat[off+64:end]),struct.unpack_from('<I',self.idx,16+60*b['id']+12)[0]);
   for j in range(b['objects']):
    p=n+j*16;self.assertEqual(a[p:p+6]+a[p+8:p+16],self.dat[p:p+6]+self.dat[p+8:p+16]);changed+=a[p+6:p+8]!=self.dat[p+6:p+8]
  self.assertEqual(changed,45)
 def test_repack_equivalence(self):
  def canonical(man,data):
   out=[{}, {}, {}]
   for b in man['blocks']:
    off=b['lba']*2048+64
    for k,(stride,count) in enumerate(zip([36,24,16],[b['render'],b['collision'],b['objects']])):
     for _ in range(count):
      rec=data[off:off+stride];off+=stride;n=1 if k==2 else 3
      pts=struct.unpack_from('<'+'h'*(3*n),rec);xyz=tuple(v+b['origin'][j%3] for j,v in enumerate(pts));key=struct.unpack_from('<I',rec,stride-4)[0];self.assertNotIn(key,out[k]);out[k][key]=(xyz,rec[n*6:])
   return out
  old=R/'assets_m25';a=canonical(json.loads((old/'sector_manifest.json').read_text()),(old/'DOJOSECT.DAT').read_bytes());b=canonical(self.man,(A/'DOJOSECT.DAT').read_bytes());self.assertEqual(a,b);self.assertEqual([len(t) for t in b],[127733,7035,351])
 def test_radius_coverage(self):
  # Each source triangle intersecting the old/new candidate square must have a selected block.
  # The anchor can be up to 256 units away from the player; 1792 covers 1536 + 256.
  for x in range(-1024,1024):
   anchor=(x//512)*512+256;self.assertLessEqual(abs(x-anchor)+1536,1792)
  rep=json.loads((A/'repack_report.json').read_text());self.assertLessEqual(rep['peak_bytes'],460*1024);self.assertLessEqual(rep['max_blocks'],28)
 def test_disc(self):
  d=(P/'ETD_PSX_M27.bin').read_bytes();self.assertIn(b'ETD_WIDE.EXE;1',d[21*2352+24:21*2352+2072]);self.assertIn(b'ETD_POOL.EXE;1',d[20*2352+24:20*2352+2072]);self.assertGreater(json.loads((P/'report.json').read_text())['headroom_to_stack_region'],32768)
  for i in range(len(d)//2352):s=d[i*2352:(i+1)*2352];self.assertEqual(s,raw(i,s[24:2072]))
 def test_texture_cache(self):
  T=C.CDLL(str(P/'tex27_host.so'));idx=(A/'DOJOTEX.IDX').read_bytes();data=(A/'DOJOTEX.DAT').read_bytes();T.validate19.argtypes=[C.c_char_p,C.c_uint32,C.c_uint32];T.block19.argtypes=[C.c_char_p,C.c_char_p];self.assertTrue(T.validate19(idx,len(idx),len(data)//2048));freq=(C.c_uint32*540)();groups=[]
  for i in range(52):
   e=idx[12+12*i:24+12*i];g,lba,crc=struct.unpack('<III',e);groups.append(g);freq[g]=1;self.assertTrue(T.block19(data[lba*2048:lba*2048+6144],e))
  class Tex(C.Structure):_fields_=[('slots',C.c_int*64),('map',C.c_int*540),('reads',C.c_int),('failed',C.c_int),('missing',C.c_int)]
  UP=C.CFUNCTYPE(None,C.c_void_p,C.c_int,C.POINTER(C.c_ubyte));uploads=[];read=CB(lambda ctx,lba,n,p:(C.memmove(p,data[lba*2048:(lba+n)*2048],n*2048),1)[1]);upload=UP(lambda ctx,slot,p:uploads.append((slot,C.string_at(p,4608))));T.init19.argtypes=[C.POINTER(Tex)];T.refreshhost19.argtypes=[C.POINTER(Tex),C.c_char_p,C.POINTER(C.c_uint32),CB,C.c_void_p,UP,C.c_void_p];t=Tex();T.init19(C.byref(t));T.refreshhost19(C.byref(t),idx,freq,read,None,upload,None);self.assertEqual((t.reads,t.failed,t.missing,len(uploads)),(52,0,0,52));self.assertEqual(len({t.map[g] for g in groups}),52);T.refreshhost19(C.byref(t),idx,freq,read,None,upload,None);self.assertEqual(t.reads,52)
 def test_basket_reward(self):
  class Butterfly(C.Structure):_fields_=[(k,C.c_int) for k in 'x y z age'.split()]
  class Flame(C.Structure):_fields_=[(k,C.c_int) for k in 'x y z vx vy vz life'.split()]
  class Inter(C.Structure):_fields_=[('state',C.c_ubyte*46),('age',C.c_ubyte*46),('butterfly',Butterfly*1),('fire',Flame*24)]+[(k,C.c_int) for k in 'health score broken pickups healed hit cooldown tick'.split()]
  L=self.L;L.reset21.argtypes=[C.POINTER(Inter)];L.step21.argtypes=[C.POINTER(Inter),C.c_void_p]+[C.c_int]*12;L.id21.argtypes=[C.c_uint32,C.c_int];w=self.new();s=Inter();L.reset21(C.byref(s));o=next(o for o in self.man['objects'] if o['edf'].lower()=='basket1.edf');x,y,z=map(round,o['source_xyz']);self.assertTrue(self.load(w,x,z));f=L.cache18_floor(w,x,z,-y,110);self.assertNotEqual(f,32767);i=L.id21(o['record_offset'],2);self.assertGreaterEqual(i,0);L.step21(C.byref(s),w,x,f,z,x-19,z,16,1,0,1,x,f-190,z);self.assertEqual(s.state[i],1);self.assertTrue(self.load(w,10534,-14914));self.assertTrue(self.load(w,x,z));
  for _ in range(15):L.step21(C.byref(s),w,x,f,z,x,z,0,0,0,1,x,f-190,z)
  self.assertEqual(s.state[i],2);self.assertGreaterEqual(s.score,1);old=s.score
  for _ in range(10):L.step21(C.byref(s),w,x,f,z,x,z,0,0,0,1,x,f-190,z)
  self.assertEqual(s.score,old)
