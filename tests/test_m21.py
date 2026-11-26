import ctypes as C,struct,json,unittest,sys
from pathlib import Path
from test_m18 import Cache,CB
from test_m20 import Collect
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'build_m21/play';A=ROOT/'assets_m16';sys.path.insert(0,str(ROOT/'tools'));from disc16 import raw
class Flame(C.Structure):_fields_=[(k,C.c_int) for k in ('x','y','z','vx','vy','vz','life')]
class Butterfly(C.Structure):_fields_=[(k,C.c_int) for k in ('x','y','z','age')]
class Inter(C.Structure):_fields_=[('state',C.c_ubyte*39),('age',C.c_ubyte*39),('butterfly',Butterfly*12),('fire',Flame*24)]+[(k,C.c_int) for k in ('health','score','broken','pickups','healed','hit','cooldown','tick')]
class M21(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.L=C.CDLL(str(P/'interact21_host.so'));L=cls.L;cls.idx=(A/'HUBSECT.IDX').read_bytes();cls.dat=(A/'HUBSECT.DAT').read_bytes();cls.man=json.loads((A/'sector_manifest.json').read_text());cls.objects=sorted([o for o in cls.man['objects'] if o['kind'] in (2,3)],key=lambda o:(o['kind'],o['record_offset']));cls.good=CB(lambda ctx,lba,n,p:(C.memmove(p,cls.dat[lba*2048:(lba+n)*2048],n*2048),1)[1]);L.cache18_update.argtypes=[C.POINTER(Cache),C.c_char_p,C.c_uint32,C.c_uint32,C.c_int,C.c_int,CB,C.c_void_p];L.cache18_floor.argtypes=[C.POINTER(Cache),C.c_int,C.c_int,C.c_int,C.c_int];L.step21.argtypes=[C.POINTER(Inter),C.POINTER(Cache)]+[C.c_int]*12;L.reset21.argtypes=[C.POINTER(Inter)];L.hurt21.argtypes=[C.POINTER(Inter)];L.greset21.argtypes=[C.POINTER(Collect)]+[C.c_int]*3;L.gstep21.argtypes=[C.POINTER(Collect),C.POINTER(Cache)]+[C.c_int]*5
 def new(self):
  w=Cache();self.L.cache18_init(C.byref(w));s=Inter();self.L.reset21(C.byref(s));return w,s
 def move(self,w,x,z):return self.L.cache18_update(C.byref(w),self.idx,len(self.idx),len(self.dat)//2048,x,z,self.good,None)
 def obj(self,w,name):
  i,o=next((i,o) for i,o in enumerate(self.objects) if o['name']==name);x,y,z=(round(v) for v in o['source_xyz']);y=-y;self.assertTrue(self.move(w,x,z));return i,x,y,z
 def step(self,s,w,x,y,z,ox=None,oz=None,heading=0,charge=0,firing=0,grounded=1,sparx=None):
  self.L.step21(C.byref(s),C.byref(w),x,y,z,x if ox is None else ox,z if oz is None else oz,heading,charge,firing,grounded,*(sparx or (x,y-190,z)))
 def test_source_ids(self):
  ids=[]
  for b in self.man['blocks']:
   off=b['lba']*2048+64+b['render']*36+b['collision']*24
   for j in range(b['objects']):
    x,y,z,k,v,_,i=struct.unpack_from('<3h3HI',self.dat,off+16*j)
    if k not in (2,3):continue
    n=self.L.id21(i,k);self.assertGreaterEqual(n,0);self.assertEqual(self.L.id21(i,5-k),-1);self.assertEqual(self.objects[n]['record_offset'],i);self.assertEqual([x+b['origin'][0],y+b['origin'][1],z+b['origin'][2]],[round(a*b) for a,b in zip(self.objects[n]['source_xyz'],(1,-1,1))]);ids.append(n)
  self.assertEqual(sorted(ids),list(range(39)));self.assertEqual(self.L.id21(0,2),-1)
 def test_charge_reward_persists(self):
  w,s=self.new();i,x,y,z=self.obj(w,'Farm_Basket1_2');self.step(s,w,x,y,z-105,oz=z-143,charge=1);self.assertEqual((s.state[i],s.broken),(1,1));self.assertTrue(self.move(w,36848,-1200));
  for _ in range(12):self.step(s,w,36848,800,-1200)
  self.assertEqual((s.state[i],s.score),(1,0));self.assertTrue(self.move(w,x,z));self.step(s,w,x,y,z-105);self.assertEqual((s.state[i],s.score,s.pickups),(2,1,1));self.assertTrue(self.move(w,36848,-1200));self.assertTrue(self.move(w,x,z));self.step(s,w,x,y,z-105,oz=z-140,charge=1);self.assertEqual((s.state[i],s.score,s.broken,s.pickups),(2,1,0,0));self.L.reset21(C.byref(s));self.assertEqual((s.state[i],s.score,s.health),(0,0,3))
 def test_fire_original_basket(self):
  w,s=self.new();i,x,y,z=self.obj(w,'Farm_Basket1_1');states=[]
  for f in range(20):
   self.step(s,w,x,y,z-300,firing=1);states.append(dict(frame=f,state=s.state[i],fire=[[v.x,v.y,v.z,v.life] for v in s.fire if v.life],broken=s.broken))
   if s.state[i]:break
  self.assertEqual((s.state[i],s.broken),(1,1));self.assertGreater(len(states),1);(P/'fire_route21.json').write_text(json.dumps(dict(name='Farm_Basket1_1',position=[x,y,z-300],target=[x,y,z],ids=[w.ids[w.active[j]] for j in range(w.count)],states=states),indent=2));print('fire broke original basket at frame',states[-1]['frame'])
 def test_sheep_health(self):
  w,s=self.new();i,x,y,z=self.obj(w,'SHEEP4');self.L.hurt21(C.byref(s));self.assertEqual(s.health,2);self.step(s,w,x,y,z-100,oz=z-138,charge=1);self.assertEqual(s.state[i],1);self.assertEqual(s.hit,1);self.assertEqual(s.health,2)
  for _ in range(40):self.step(s,w,x,y,z-100)
  self.assertEqual((s.state[i],s.health),(2,3));self.L.hurt21(C.byref(s));self.step(s,w,x,y,z-100,oz=z-138,charge=1);self.assertEqual((s.state[i],s.health),(2,2))
 def test_zero_health_recovery_and_expiry(self):
  w,s=self.new();i,x,y,z=self.obj(w,'SHEEP4');
  for _ in range(5):self.L.hurt21(C.byref(s))
  self.assertEqual(s.health,0);self.step(s,w,x,y,z-100,oz=z-138,charge=1)
  for _ in range(40):self.step(s,w,x,y,z-100,sparx=(x+700,y-190,z))
  self.assertEqual((s.state[i],s.health),(2,1));self.L.reset21(C.byref(s));self.step(s,w,x,y,z-100,oz=z-138,charge=1);self.assertEqual(s.state[i],1);self.assertTrue(self.move(w,36848,-1200));
  for _ in range(180):self.step(s,w,36848,800,-1200)
  self.assertEqual(s.state[i],2);self.assertEqual(s.health,3)
 def test_coverage_and_preview(self):
  coverage=[]
  for o in self.objects:
   w,s=self.new();x,y,z=[round(v) for v in o['source_xyz']];y=-y;ok=self.move(w,x,z);floor=self.L.cache18_floor(C.byref(w),x,z,y,110) if ok else 32767;coverage.append(dict(name=o['name'],loadable=bool(ok),floor=floor))
  self.assertEqual(sum(o['loadable'] for o in coverage),34);(P/'coverage21.json').write_text(json.dumps(coverage,indent=2))
  w,s=self.new();i,x,y,z=self.obj(w,'SHEEP4');self.L.hurt21(C.byref(s));records=[];pos=[x,y,z-100]
  def capture():return dict(health=s.health,state=s.state[i],butterfly=[s.butterfly[i-27].x,s.butterfly[i-27].y,s.butterfly[i-27].z],tick=s.tick)
  records.append(capture());self.step(s,w,*pos,oz=z-138,charge=1);records.append(capture())
  for _ in range(40):
   self.step(s,w,*pos);records.append(capture())
   if s.healed:break
  self.assertEqual(records[-1]['health'],3);(P/'sheep_route21.json').write_text(json.dumps(dict(name='SHEEP4',position=pos,target=[x,y,z],ids=[w.ids[w.active[j]] for j in range(w.count)],states=records),indent=2))
 def test_no_airborne_charge_or_unloaded_fire(self):
  w,s=self.new();i,x,y,z=self.obj(w,'Farm_Basket1_2');self.step(s,w,x,y,z-105,oz=z-143,charge=1,grounded=0);self.assertEqual(s.state[i],0);self.step(s,w,x,y,z-105,charge=1);self.assertEqual(s.state[i],0);self.step(s,w,x,y,z-105,firing=1,grounded=0);self.assertFalse(any(f.life for f in s.fire));w,s=self.new();self.step(s,w,x,y,z-105,firing=1);self.assertFalse(any(f.life for f in s.fire))
 def test_sparx_disabled_at_zero(self):
  w,s=self.new();c=Collect();self.assertTrue(self.move(w,36728,-1200));self.L.greset21(C.byref(c),36728,800,-1200)
  for _ in range(30):self.L.gstep21(C.byref(c),C.byref(w),36728,800,-1200,48,0)
  self.assertEqual(c.score,0)
  for _ in range(30):self.L.gstep21(C.byref(c),C.byref(w),36728,800,-1200,48,1)
  self.assertEqual(c.score,2)
 def test_disc_and_budget(self):
  d=(P/'ETD_PSX_M21.bin').read_bytes();self.assertIn(b'ETD_HUB.EXE;1',d[21*2352+24:21*2352+2072]);self.assertIn(b'ETD_GEM.EXE;1',d[20*2352+24:20*2352+2072]);self.assertGreater(json.loads((P/'report.json').read_text())['headroom_to_stack_region'],120000)
  for i in range(len(d)//2352):s=d[i*2352:(i+1)*2352];self.assertEqual(s,raw(i,s[24:2072]))
