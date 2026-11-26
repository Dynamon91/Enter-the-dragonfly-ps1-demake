"""Host tests against the unchanged original Dojo sector bank."""
import ctypes as C,json,subprocess,unittest,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R/'build_m33/play';A=R/'assets_m33';OLD=R/'build_m32/play'
CB=C.CFUNCTYPE(C.c_int,C.c_void_p,C.c_uint32,C.c_uint32,C.c_void_p)
class Progress(C.Structure):_fields_=[('caught',C.c_ubyte*15),('mode',C.c_ubyte),('count',C.c_ubyte),('bosses',C.c_ubyte),('visited',C.c_uint32)]
class Bubble(C.Structure):_fields_=[(n,C.c_int) for n in 'x y z vx vz ground life'.split()]
class Capture(C.Structure):_fields_=[('b',Bubble*12)]+[(n,C.c_int) for n in 'tick cooldown breath event'.split()]
class M33(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  s=(OLD/'host31.c').read_text().split('#include "enemy31.h"')[0]+'''
#include "bubble33.h"
void reset33(Capture33*s,Progress33*p,int mode){capture_reset33(s);progress_reset33(p,mode);}
int take33(Progress33*p,int id){return progress_take33(p,id);}
int has33(Progress33*p,int id){return progress_has33(p,id);}
int visit33(Progress33*p,int id){return progress_visit33(p,id);}
int boss33(Progress33*p,int id){return progress_boss33(p,id);}
void step33(Capture33*s,Progress33*p,Cache18*c,int x,int y,int z,int h,int f,int g){capture_step33(s,p,c,x,y,z,h,f,g,sn);}
'''
  (P/'host33.c').write_text(s);subprocess.run(['clang','-O2','-shared','-fPIC','-I',str(P),'-I',str(R/'src'),str(P/'host33.c'),str(R/'src/sector27.c'),'-o',str(P/'host33.so')],check=True);L=cls.L=C.CDLL(str(P/'host33.so'));cls.idx=(P/'DOJOSECT.IDX').read_bytes();cls.dat=(P/'DOJOSECT.DAT').read_bytes();cls.good=CB(lambda ctx,lba,n,p:(C.memmove(p,cls.dat[lba*2048:(lba+n)*2048],n*2048),1)[1]);L.cache22_size.restype=C.c_uint32;L.cache18_init.argtypes=[C.c_void_p];L.cache18_update.argtypes=[C.c_void_p,C.c_char_p,C.c_uint32,C.c_uint32,C.c_int,C.c_int,CB,C.c_void_p];L.cache18_floor.argtypes=[C.c_void_p,C.c_int,C.c_int,C.c_int,C.c_int];L.step33.argtypes=[C.POINTER(Capture),C.POINTER(Progress),C.c_void_p]+[C.c_int]*6;L.reset33.argtypes=[C.POINTER(Capture),C.POINTER(Progress),C.c_int];L.take33.argtypes=L.has33.argtypes=L.visit33.argtypes=L.boss33.argtypes=[C.POINTER(Progress),C.c_int];cls.objects=json.loads((A/'report.json').read_text())['objects']
 def load(self,w,x,z):return self.L.cache18_update(w,self.idx,len(self.idx),len(self.dat)//2048,x,z,self.good,None)
 def new(self,o):
  w=C.create_string_buffer(self.L.cache22_size());self.L.cache18_init(w);x,y,z=map(round,o['source_xyz']);self.assertTrue(self.load(w,x,z));f=self.L.cache18_floor(w,x,z,-y,180);s=Capture();p=Progress();self.L.reset33(C.byref(s),C.byref(p),0);return w,s,p,x,f,z
 def step(self,w,s,p,x,y,z,h=0,firing=1,grounded=1):self.L.step33(C.byref(s),C.byref(p),w,x,y,z,h,firing,grounded)
 def test_ledger_limits_and_reset(self):
  s=Capture();p=Progress()
  for mode,cap in ((0,90),(1,120)):
   self.L.reset33(C.byref(s),C.byref(p),mode)
   for n in range(cap):self.assertTrue(self.L.take33(C.byref(p),n));self.assertFalse(self.L.take33(C.byref(p),n))
   self.assertEqual(p.count,cap);self.assertFalse(self.L.take33(C.byref(p),cap));self.assertFalse(self.L.take33(C.byref(p),-1));self.assertEqual(self.L.visit33(C.byref(p),25),mode)
 def test_campaign_registry(self):
  a=json.loads((R/'campaign33.json').read_text());levels=a['levels'];self.assertEqual(len([l for l in levels if l['kind']=='adventure']),26);self.assertEqual(len([l for l in levels if l['kind']=='homeworld']),4);self.assertEqual(len({l['id'] for l in levels}),len(levels));self.assertTrue(all(l['id']<32 for l in levels));s=Capture();p=Progress()
  for mode in (0,1):
   self.L.reset33(C.byref(s),C.byref(p),mode)
   for l in levels:self.assertEqual(bool(self.L.visit33(C.byref(p),l['id'])),mode or l['mode']=='both')
   for b in a['bosses']:
    self.assertEqual(bool(self.L.boss33(C.byref(p),b['id'])),mode or b['mode']=='both');self.assertFalse(self.L.boss33(C.byref(p),b['id']))
   self.assertEqual(p.bosses,31 if mode else 4)
 def test_actual_capture_and_reload(self):
  traces=[]
  for o in self.objects:
   if not o['enabled']:continue
   w,s,p,x,f,z=self.new(o);self.assertNotEqual(f,32767,o);ok=False
   for dx,dz,h in [(0,-250,0),(-250,0,16),(0,250,32),(250,0,48),(0,-150,0),(-150,0,16),(0,150,32),(150,0,48)]:
    g=self.L.cache18_floor(w,x+dx,z+dz,f,110)
    if g==32767:continue
    self.L.reset33(C.byref(s),C.byref(p),0);s.breath=1;rows=[]
    for t in range(30):
     self.step(w,s,p,x+dx,g,z+dz,h);rows.append(dict(t=t,count=p.count,bubbles=[list((b.x,b.y,b.z,b.life)) for b in s.b if b.life]))
     if p.count:break
    if p.count:ok=True;break
   self.assertTrue(ok,o);self.assertEqual(p.count,1);self.assertTrue(self.L.has33(C.byref(p),o['slot']));self.assertTrue(self.load(w,10534,-14914));self.assertTrue(self.load(w,x,z));
   for t in range(30):self.step(w,s,p,x+dx,g,z+dz,h)
   self.assertEqual(p.count,1);traces.append(dict(id=o['slot'],source=[x,f,z],player=[x+dx,g,z+dz],heading=h,rows=rows));
  (P/'capture_trace.json').write_text(json.dumps(traces,indent=2));self.assertEqual(len(traces),2)
 def test_fire_and_unloaded_guard(self):
  w,s,p,x,f,z=self.new(self.objects[0]);self.assertNotEqual(f,32767)
  for _ in range(20):self.step(w,s,p,x,f,z)
  self.assertEqual(p.count,0);self.assertFalse(any(b.life for b in s.b));s.breath=1
  for _ in range(20):self.step(w,s,p,x,f,z,grounded=0)
  self.assertFalse(any(b.life for b in s.b));self.L.cache18_init(w);s.b[0]=Bubble(x,f-125,z,31,0,f,10);self.step(w,s,p,x,f,z);self.assertEqual(s.b[0].life,0);self.assertEqual(p.count,0)
 def test_scripted_placements_reserved(self):
  for o in self.objects:
   if o['enabled']:continue
   w,s,p,x,f,z=self.new(o);s.b[0]=Bubble(x,f-125,z,0,0,f,10);self.step(w,s,p,x,f,z,firing=0);self.assertEqual(p.count,0)
 def test_disc(self):
  from disc16 import raw
  d=(P/'ETD_PSX_M33.bin').read_bytes();self.assertIn(b'ETD_BUBL.EXE;1',d[21*2352+24:21*2352+2072]);root=d[20*2352+24:20*2352+2072];records={};i=0
  while root[i]:
   r=root[i:i+root[i]];records[r[33:33+r[32]].decode()]=struct.unpack_from('<I',r,2)[0],struct.unpack_from('<I',r,10)[0];i+=len(r)
  for n in ('BOOT32.DAT','DOJOSECT.DAT','DOJOSECT.IDX','ETD_BOOT.EXE'):
   l,size=records[n+';1'];self.assertEqual(b''.join(d[j*2352+24:j*2352+2072] for j in range(l,l+(size+2047)//2048))[:size],(OLD/n).read_bytes())
  for i in range(len(d)//2352):s=d[i*2352:(i+1)*2352];self.assertEqual(s,raw(i,s[24:2072]))
  self.assertGreater(json.loads((P/'report33.json').read_text())['headroom_to_stack_region'],150000)
if __name__=='__main__':unittest.main()
