import unittest,json,struct,sys,ctypes,tempfile
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'build_m10/play';sys.path.insert(0,str(ROOT/'tools'))
from cnk import ISO
from disc10 import edc,ecc
class Anim(ctypes.Structure):_fields_=[(k,ctypes.c_int) for k in ['clip','tick','frame','fromframe','blend']]
class Milestone10(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.r=json.loads((P/'rig_report.json').read_text());cls.z=np.load(P/'rig.npz');cls.lib=ctypes.CDLL(str(P/'rig_host.so'));cls.lib.pose10.argtypes=[ctypes.c_int,ctypes.POINTER(ctypes.c_int)];cls.lib.reset10.argtypes=[ctypes.POINTER(Anim)];cls.lib.step10.argtypes=[ctypes.POINTER(Anim)]+[ctypes.c_int]*6
 def test_rig(self):
  z=self.z;self.assertEqual(self.r['joints'],43);self.assertTrue(self.r['duplicate_channels']);self.assertLess(self.r['parent_max_error'],.0001);self.assertTrue(np.all(z['parents'][1:]<np.arange(1,43)));self.assertEqual(len(z['targets']),167);self.assertEqual(sum(self.r['skinned_source_vertices'].values()),2481)
 def test_weights(self):
  z=self.z;self.assertTrue(np.all(z['weights'].sum(1)==256));self.assertTrue(np.all(z['bones']<43));self.assertLess(self.r['max_discarded_weight'],.001);self.assertLess(self.r['weight_sum_max_error'],.000001)
 def test_all_poses(self):
  z=self.z;v=z['vertices'];bones=z['bones'];w=z['weights'];ms=z['matrices'];host=np.load(P/'poses_host.npz')['poses'];self.assertEqual(host.shape,(245,1157,3));self.assertLess(np.abs(host).max(),300)
  for i,m in enumerate(ms):
   mats=m[bones];q=((np.einsum('vijk,vk->vij',mats[...,:3],v)+2048)>>12)+mats[...,3];expected=(np.sum(q*w[:,:,None],axis=1)+128)>>8;np.testing.assert_array_equal(expected,host[i])
  for c in self.r['clips']:self.assertGreater(np.abs(np.diff(host[c['start']:c['start']+c['frames']],axis=0)).max(),0)
 def test_animation_state_machine(self):
  a=Anim();self.lib.reset10(ctypes.byref(a));self.assertEqual(a.clip,0)
  def step(moved=0,btn=0,was=1,grounded=1,vy=0,analog=0):
   self.lib.step10(ctypes.byref(a),moved,btn,was,grounded,vy,analog);c=self.r['clips'][a.clip];self.assertTrue(c['start']<=a.frame<c['start']+c['frames']);self.assertTrue(0<=a.blend<=4)
  step(1,analog=50);self.assertEqual(a.clip,1);step(1,analog=127);self.assertEqual(a.clip,2);step(1,32768,analog=127);self.assertEqual(a.clip,3);step(1,16384,1,0,-30);self.assertEqual(a.clip,4);step(1,16384,0,0,4);self.assertEqual(a.clip,7);step(1,0,0,0,5);self.assertEqual(a.clip,5);step(0,0,0,1);self.assertEqual(a.clip,6)
  for _ in range(20):step()
  self.assertEqual(a.clip,0);step(btn=8192);self.assertEqual(a.clip,8)
  for _ in range(100):step(btn=8192)
  self.assertEqual(a.clip,8)
 def test_world_preserved(self):
  for n in ['scene.h','world.h','farm06.npz','visibility.h','visibility.npz']:
   self.assertEqual((P/n).read_bytes(),(ROOT/'build_m09/play'/n).read_bytes())
 def test_native_disc(self):
  e=(P/'ETD_ANIM.EXE').read_bytes();r=json.loads((P/'report.json').read_text());self.assertEqual(e[:8],b'PS-X EXE');self.assertEqual(len(e)-2048,struct.unpack_from('<I',e,28)[0]);self.assertLess(int(r['linked_ram_high'],16),0x801e0000);b=(P/'ETD_PSX_M10.bin').read_bytes();self.assertEqual(len(b)%2352,0);cooked=bytearray()
  for i in range(0,len(b),2352):
   s=bytearray(b[i:i+2352]);self.assertEqual(s[:12],b'\0'+b'\xff'*10+b'\0');self.assertEqual(s[15],2);self.assertEqual(s[16:20],s[20:24]);self.assertEqual(struct.unpack_from('<I',s,2072)[0],edc(s[16:2072]));s[12:16]=bytes(4);self.assertEqual(s[2076:2248],ecc(s[12:2076],86,24,2,86));self.assertEqual(s[2248:2352],ecc(s[12:2248],52,43,86,88));cooked.extend(s[24:2072])
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'test.iso';p.write_bytes(cooked)
   with ISO(p) as iso:self.assertEqual(iso.file('ETD_ANIM.EXE'),e);self.assertIn(b'cdrom:\\ETD_ANIM.EXE;1',iso.file('SYSTEM.CNF'))
