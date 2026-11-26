import ctypes as C, json,struct,unittest,sys,zlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R/'build_m29/play';sys.path.insert(0,str(R/'tools'))
from disc16 import raw
CB=C.CFUNCTYPE(C.c_int,C.c_void_p,C.c_uint32,C.c_uint32,C.POINTER(C.c_ubyte))
class Butterfly(C.Structure):_fields_=[(k,C.c_int) for k in 'x y z age'.split()]
class Flame(C.Structure):_fields_=[(k,C.c_int) for k in 'x y z vx vy vz life'.split()]
class Inter(C.Structure):_fields_=[('state',C.c_ubyte*91),('age',C.c_ubyte*91),('butterfly',Butterfly*1),('fire',Flame*24)]+[(k,C.c_int) for k in 'health score broken pickups healed hit cooldown tick'.split()]
class Collect(C.Structure):_fields_=[("taken",C.c_ubyte*193)]+[(n,C.c_int) for n in "score tick sx sy sz target events assist".split()]
class M29(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  L=cls.L=C.CDLL(str(P/'host29.so'));cls.idx=(P/'DOJOSECT.IDX').read_bytes();cls.dat=(P/'DOJOSECT.DAT').read_bytes();cls.man=json.loads((R/'assets_m27/sector_manifest.json').read_text());cls.good=CB(lambda ctx,lba,n,p:(C.memmove(p,cls.dat[lba*2048:(lba+n)*2048],n*2048),1)[1]);L.cache22_size.restype=C.c_uint32;L.cache18_init.argtypes=[C.c_void_p];L.cache18_update.argtypes=[C.c_void_p,C.c_char_p,C.c_uint32,C.c_uint32,C.c_int,C.c_int,CB,C.c_void_p];L.cache18_floor.argtypes=[C.c_void_p,C.c_int,C.c_int,C.c_int,C.c_int];L.reset21.argtypes=[C.POINTER(Inter)];L.step21.argtypes=[C.POINTER(Inter),C.c_void_p]+[C.c_int]*12;L.estep29.argtypes=[C.POINTER(Inter),C.c_void_p]+[C.c_int]*7;L.id21.argtypes=[C.c_uint32,C.c_int];L.eid29.argtypes=[C.c_uint32];cls.baskets=[o for o in cls.man['objects'] if o['edf'].lower().startswith('basket')];cls.enemies=[o for o in cls.man['objects'] if 'ninja_riptoc' in o['edf'].lower()]
 def new(self):w=C.create_string_buffer(self.L.cache22_size());self.L.cache18_init(w);return w
 def load(self,w,x,z):return self.L.cache18_update(w,self.idx,len(self.idx),len(self.dat)//2048,x,z,self.good,None)
 def at(self,w,o):
  x,y,z=map(round,o['source_xyz']);self.assertTrue(self.load(w,x,z));return x,self.L.cache18_floor(w,x,z,-y,110),z
 def test_ids(self):
  self.assertEqual(len(self.baskets),90);self.assertEqual(len(self.enemies),25);self.assertEqual(len({self.L.id21(o['record_offset'],2) for o in self.baskets}),90);self.assertEqual(len({self.L.eid29(o['record_offset']) for o in self.enemies}),25);self.assertEqual(sum(self.L.bval29(self.L.id21(o['record_offset'],2)) for o in self.baskets),271)
 def test_unchanged_geometry(self):
  old=(R/'build_m28/play/DOJOSECT.DAT').read_bytes();changes=0
  for b in self.man['blocks']:
   a=b['lba']*2048;end=a+64+36*b['render']+24*b['collision'];self.assertEqual(self.dat[a+64:end],old[a+64:end]);self.assertEqual(zlib.crc32(self.dat[a+64:a+b['size']]),struct.unpack_from('<I',self.dat,a+36)[0]);self.assertEqual(struct.unpack_from('<I',self.idx,16+60*b['id']+12)[0],struct.unpack_from('<I',self.dat,a+36)[0]);
   for p in range(end,end+16*b['objects'],16):
    self.assertEqual(self.dat[p:p+6],old[p:p+6]);self.assertEqual(self.dat[p+8:p+16],old[p+8:p+16]);changes+=self.dat[p+6:p+8]!=old[p+6:p+8]
  self.assertEqual(changes,45)
 def test_basket_variants(self):
  w=self.new();L=self.L;tested=[];coverage=0
  for o in self.baskets:
   x,f,z=self.at(w,o);coverage+=f!=32767
  for val in (1,2,5,10):
   for o in self.baskets:
    i=L.id21(o['record_offset'],2)
    if L.bval29(i)!=val:continue
    x,f,z=self.at(w,o)
    if f==32767:continue
    s=Inter();L.reset21(C.byref(s));L.step21(C.byref(s),w,x,f,z,x-19,z,16,1,0,1,x,f-190,z)
    if s.state[i]!=1:continue
    # Unload; revisit and verify reward once.
    self.assertTrue(self.load(w,10534,-14914));self.assertTrue(self.load(w,x,z))
    for _ in range(15):L.step21(C.byref(s),w,x,f,z,x,z,0,0,0,1,x,f-190,z)
    self.assertEqual(s.state[i],2);old=s.score;self.assertGreaterEqual(old,val)
    for _ in range(10):L.step21(C.byref(s),w,x,f,z,x,z,0,0,0,1,x,f-190,z)
    self.assertEqual(s.score,old);tested.append((val,i,x,f,z,old));break
  self.assertEqual(len(tested),4);print('basket coverage',coverage,'/90; variant tests',tested);self.__class__.basket_coverage=coverage
 def test_enemy_combat(self):
  w=self.new();L=self.L;tested=[];coverage=0
  for o in self.enemies:
   x,f,z=self.at(w,o);coverage+=f!=32767
  for large in (0,1):
   for o in self.enemies:
    i=L.eid29(o['record_offset'])
    if L.large29(i)!=large:continue
    x,f,z=self.at(w,o)
    if f==32767:continue
    s=Inter();L.reset21(C.byref(s));L.ereset29();L.estep29(C.byref(s),w,x,f,z,x,z,0,1)
    if s.health!=2:continue
    for _ in range(5):L.estep29(C.byref(s),w,x,f,z,x,z,0,1)
    self.assertEqual(s.health,2)
    L.estep29(C.byref(s),w,x,f,z,x-19,z,1,1)
    self.assertEqual(L.dead29(i),1-large)
    if large:
     # A live fire particle at target height; test interaction, not projectile trajectory.
     s.fire[0]=Flame(x,f-135,z,0,0,0,10);L.estep29(C.byref(s),w,x,f,z,x,z,0,1);self.assertEqual(L.dead29(i),1)
    self.assertTrue(self.load(w,10534,-14914));self.assertTrue(self.load(w,x,z));self.assertEqual(L.dead29(i),1);L.ereset29();self.assertEqual(L.dead29(i),0);tested.append((large,i,x,f,z));break
  self.assertEqual(len(tested),2);print('enemy floor coverage',coverage,'/25; combat tests',tested);(P/'combat_test.json').write_text(json.dumps(dict(enemy_floor=coverage,combat=tested,basket_floor=getattr(self.__class__,'basket_coverage',None)),indent=2))
 def test_gem10(self):
  L=self.L;L.greset21.argtypes=[C.POINTER(Collect),C.c_int,C.c_int,C.c_int];L.gstep21.argtypes=[C.POINTER(Collect),C.c_void_p,C.c_int,C.c_int,C.c_int,C.c_int,C.c_int];w=self.new();o=next(o for o in self.man["objects"] if o.get("value")==10 and o["kind"]==1);x,f,z=self.at(w,o);self.assertNotEqual(f,32767);c=Collect();L.greset21(C.byref(c),x,f,z);L.gstep21(C.byref(c),w,x,f,z,0,0);self.assertGreaterEqual(c.score,10);old=c.score;self.assertTrue(self.load(w,10534,-14914));self.assertTrue(self.load(w,x,z));L.gstep21(C.byref(c),w,x,f,z,0,0);self.assertEqual(c.score,old);self.assertIn("value==10",(P/"play29.c").read_text());print("10-value gem test score",old)
 def test_disc(self):
  d=(P/'ETD_PSX_M29.bin').read_bytes();self.assertIn(b'ETD_NINJ.EXE;1',d[21*2352+24:21*2352+2072]);self.assertIn(b'ETD_SKY.EXE;1',d[20*2352+24:20*2352+2072]);self.assertGreater(json.loads((P/'report.json').read_text())['headroom_to_stack_region'],65536)
  for i in range(len(d)//2352):s=d[i*2352:(i+1)*2352];self.assertEqual(s,raw(i,s[24:2072]))
  root=d[20*2352+24:20*2352+2072];pos=0;files={}
  while root[pos]:
   n=root[pos];r=root[pos:pos+n];name=r[33:33+r[32]];lba,size=struct.unpack_from('<I',r,2)[0],struct.unpack_from('<I',r,10)[0];files[name]=b''.join(d[i*2352+24:i*2352+2072] for i in range(lba,lba+(size+2047)//2048))[:size];pos+=n
  for n in ('DOJOSECT.DAT','DOJOSECT.IDX','ETD_NINJ.EXE'):self.assertEqual(files[(n+';1').encode()],(P/n).read_bytes())
 def test_model(self):
  import numpy as np
  z=np.load(R/'assets_m29/ninja.npz');r=json.loads((R/'assets_m29/enemy_report.json').read_text());self.assertEqual(r['source_triangles'],1070);self.assertEqual(len(z['triangles']),520);self.assertEqual(len(z['colors']),520);self.assertLess(np.abs(z['triangles']).max(),512)
if __name__=='__main__':unittest.main()
