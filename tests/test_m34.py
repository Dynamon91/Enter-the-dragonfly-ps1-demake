"""Source-coordinate quest tests with actual Dojo disc banks."""
import ctypes as C,json,subprocess,unittest,itertools,struct
from pathlib import Path
from test_m33 import M33,Progress,Capture,CB
R=Path(__file__).resolve().parents[1];P=R/'build_m34/play';A=R/'assets_m34';OLD=R/'build_m33/play'
class Quest(C.Structure):_fields_=[('stage',C.c_int*3),('timer',C.c_int*3)]+[(n,C.c_int) for n in ('seen','near','event','reward')]
class M34(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  s=(OLD/'host33.c').read_text()+'''\n#include "quest34.h"
void qreset(Quest34*q){quest_reset34(q);}
void qstep(Quest34*q,Progress33*p,Cache18*c,int x,int y,int z,int g,int talk){quest_step34(q,p,c,x,y,z,g,talk);}
void qpos(Quest34*q,int i,int*xyz){quest_pos34(q,i,xyz);}
''';(P/'host34.c').write_text(s);subprocess.run(['clang','-O2','-shared','-fPIC','-I',str(P),'-I',str(R/'src'),str(P/'host34.c'),str(R/'src/sector27.c'),'-o',str(P/'host34.so')],check=True)
  L=cls.L=C.CDLL(str(P/'host34.so'));cls.idx=(P/'DOJOSECT.IDX').read_bytes();cls.dat=(P/'DOJOSECT.DAT').read_bytes();cls.good=CB(lambda ctx,lba,n,p:(C.memmove(p,cls.dat[lba*2048:(lba+n)*2048],n*2048),1)[1]);L.cache22_size.restype=C.c_uint32;L.cache18_init.argtypes=[C.c_void_p];L.cache18_update.argtypes=[C.c_void_p,C.c_char_p,C.c_uint32,C.c_uint32,C.c_int,C.c_int,CB,C.c_void_p];L.cache18_floor.argtypes=[C.c_void_p,C.c_int,C.c_int,C.c_int,C.c_int];L.qreset.argtypes=[C.POINTER(Quest)];L.qstep.argtypes=[C.POINTER(Quest),C.POINTER(Progress),C.c_void_p]+[C.c_int]*5;L.qpos.argtypes=[C.POINTER(Quest),C.c_int,C.POINTER(C.c_int)];L.reset33.argtypes=[C.POINTER(Capture),C.POINTER(Progress),C.c_int];L.has33.argtypes=[C.POINTER(Progress),C.c_int];cls.quests=json.loads((A/'report.json').read_text())['quests']
 def new(self,mode=0):
  w=C.create_string_buffer(self.L.cache22_size());self.L.cache18_init(w);s=Capture();p=Progress();q=Quest();self.L.reset33(C.byref(s),C.byref(p),mode);self.L.qreset(C.byref(q));return w,p,q
 def load(self,w,x,z):self.assertTrue(self.L.cache18_update(w,self.idx,len(self.idx),len(self.dat)//2048,x,z,self.good,None))
 def position(self,w,o):
  x,y,z=map(round,o['source_xyz']);self.load(w,x,z);f=self.L.cache18_floor(w,x,z,-y,180);self.assertNotEqual(f,32767,o);return x,f,z
 def step(self,w,p,q,xyz,g=1,talk=0):self.L.qstep(C.byref(q),C.byref(p),w,*xyz,g,talk)
 def test_all_orders_and_modes(self):
  traces=[]
  for mode in (0,1):
   for order in itertools.permutations(range(3)):
    w,p,q=self.new(mode);rows=[]
    for i in order:
     d=self.quests[i];xyz=self.position(w,d['npc']);self.step(w,p,q,xyz,talk=1);self.assertEqual(q.stage[i],0);self.assertEqual(p.count,0)
     xyz=self.position(w,d['trigger']);self.step(w,p,q,xyz,g=0);self.assertEqual(q.stage[i],0);self.step(w,p,q,xyz);self.assertEqual(q.stage[i],1);self.assertEqual(q.timer[i],0)
     self.load(w,10534,-14914) # timer continues while sector absent
     a=(C.c_int*3)();path=[]
     for t in range(d['duration_ticks']):
      self.L.qpos(C.byref(q),i,a);path.append(list(a));self.step(w,p,q,(10534,-2075,-14914));self.assertEqual(q.stage[i],1 if t<d['duration_ticks']-1 else 2)
     self.L.qpos(C.byref(q),i,a);path.append(list(a));self.assertEqual(list(a),[round(v*s) for v,s in zip(d['control_points'][-1],(1,-1,1))]);self.assertEqual(p.count,0)
     xyz=self.position(w,d['npc']);self.step(w,p,q,xyz,talk=1);self.assertEqual(q.stage[i],3);self.assertEqual(p.count,int(all(v==3 for v in q.stage)));rows.append(dict(name=d['name'],duration=d['duration_ticks'],stage=list(q.stage),count=p.count,path=path))
     self.step(w,p,q,xyz,talk=1);self.assertEqual(p.count,int(all(v==3 for v in q.stage)))
    self.assertEqual(p.count,1);self.assertEqual(q.reward,1);self.assertTrue(self.L.has33(C.byref(p),3));self.assertFalse(self.L.has33(C.byref(p),2));self.load(w,10534,-14914);self.assertEqual(list(q.stage),[3]*3)
    traces.append(dict(mode=mode,order=list(order),rows=rows))
  (P/'quest_trace.json').write_text(json.dumps(traces,indent=2))
 def test_range_and_reset(self):
  w,p,q=self.new();xyz=self.position(w,self.quests[0]['trigger']);self.step(w,p,q,(xyz[0],xyz[1]-400,xyz[2]));self.assertEqual(q.stage[0],0);self.step(w,p,q,xyz);self.assertEqual(q.stage[0],1);self.L.qreset(C.byref(q));self.assertEqual(list(q.stage),[0]*3);self.assertEqual(q.near,-1)
 def test_source_mapping(self):
  self.assertEqual([d['flags'] for d in self.quests],[[20,21,22,23],[26,27,28,29],[32,33,34,35]]);self.assertEqual([d['duration_ticks'] for d in self.quests],[180,135,188]);self.assertEqual([len(d['control_points']) for d in self.quests],[7,7,8]);self.assertEqual(len({d[k]['record_offset'] for d in self.quests for k in ['npc','trigger','prop']}),9)
 def test_disc_and_native(self):
  from disc16 import raw
  d=(P/'ETD_PSX_M34.bin').read_bytes();self.assertIn(b'ETD_QEST.EXE;1',d[21*2352+24:21*2352+2072]);root=d[20*2352+24:20*2352+2072];records={};i=0
  while root[i]:
   r=root[i:i+root[i]];records[r[33:33+r[32]].decode()]=struct.unpack_from('<I',r,2)[0],struct.unpack_from('<I',r,10)[0];i+=len(r)
  for n in ('BOOT32.DAT','DOJOSECT.DAT','DOJOSECT.IDX','ETD_BUBL.EXE'):
   l,size=records[n+';1'];self.assertEqual(b''.join(d[j*2352+24:j*2352+2072] for j in range(l,l+(size+2047)//2048))[:size],(OLD/n).read_bytes())
  for i in range(len(d)//2352):s=d[i*2352:(i+1)*2352];self.assertEqual(s,raw(i,s[24:2072]))
  self.assertGreater(json.loads((P/'report34.json').read_text())['headroom_to_stack_region'],150000)
if __name__=='__main__':unittest.main()
