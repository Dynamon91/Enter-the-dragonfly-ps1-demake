import unittest,ctypes,tempfile,subprocess,json,struct
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'build_m07/play';OLD=ROOT/'build_m06/play'
class Milestone7(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();p=Path(cls.tmp.name)/'clip.so';subprocess.run(['clang','-shared','-fPIC','-O2',str(ROOT/'tests/clip07_host.c'),'-o',str(p)],check=True);cls.lib=ctypes.CDLL(str(p));cls.fn=cls.lib.clip07;cls.fn.argtypes=[ctypes.POINTER(ctypes.c_int),ctypes.POINTER(ctypes.c_int)];cls.fn.restype=ctypes.c_int
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def clip(self,points):
  a=np.ascontiguousarray(points,dtype=np.int32);b=np.zeros((16,5),dtype=np.int32);n=self.fn(a.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),b.ctypes.data_as(ctypes.POINTER(ctypes.c_int)));return b[:n]
 def test_inside(self):
  a=[[-50,-20,200,0,0],[30,-10,200,64,0],[0,40,200,32,64]];np.testing.assert_array_equal(self.clip(a),a)
 def test_outside(self):self.assertEqual(len(self.clip([[500,0,200,0,0],[600,40,200,64,0],[700,0,200,0,64]])),0)
 def test_near(self):
  r=self.clip([[-20,0,64,0,0],[20,0,192,64,0],[0,40,192,0,64]]);self.assertEqual(len(r),4);self.assertGreaterEqual(r[:,2].min(),128);self.assertEqual(sum(r[:,2]==128),2);self.assertIn(32,r[r[:,2]==128,3])
 def test_large_triangle(self):
  r=self.clip([[-5000,-5000,256,0,0],[5000,-5000,256,255,0],[0,5000,256,128,255]]);self.assertEqual(len(r),4);xy=r[:,:2]*220/r[:,2,None];self.assertLessEqual(abs(xy[:,0]).max(),161);self.assertLessEqual(abs(xy[:,1]).max(),121)
 def test_random(self):
  rng=np.random.default_rng(724);max_n=0
  for i in range(4000):
   a=np.column_stack([rng.integers(-12000,12000,(3,3)),rng.integers(0,256,(3,2))]);r=self.clip(a);max_n=max(max_n,len(r));self.assertLessEqual(len(r),8)
   if len(r):
    self.assertGreaterEqual(r[:,2].min(),128);self.assertGreaterEqual(r[:,3:].min(),0);self.assertLessEqual(r[:,3:].max(),255)
    # Quantization error in world units: up to a few units at intersecting edges.
    self.assertLessEqual(np.max(np.abs(r[:,0])-160*r[:,2]/220),15);self.assertLessEqual(np.max(np.abs(r[:,1])-120*r[:,2]/220),15)
 def test_sector(self):
  a=np.load(OLD/'farm06.npz');b=np.load(P/'farm06.npz');self.assertGreater(len(b['faces']),len(a['faces']));np.testing.assert_array_equal(a['vertices'][a['faces']],b['vertices'][b['faces'][:len(a['faces'])]]);np.testing.assert_array_equal(a['floor'],b['floor']);self.assertLess(b['faces'].max(),len(b['vertices']))
 def test_alpha(self):
  a=np.load(OLD/'farm06.npz');b=np.load(P/'farm06.npz');r=json.loads((P/'report.json').read_text());k=next(i for i,x in enumerate(r['bindings']) if x['name']=='yellow_T');self.assertTrue(np.all(a['textures'][k]==0));self.assertTrue(np.all(b['textures'][k]!=0));self.assertTrue(all(x['binding'].startswith('visual candidate') for x in r['bindings']))
 def test_native(self):
  r=json.loads((P/'report.json').read_text());e=(P/'ETD_CLIP.EXE').read_bytes();self.assertEqual(e[:8],b'PS-X EXE');self.assertEqual(len(e)-2048,struct.unpack_from('<I',e,28)[0]);self.assertLess(int(r['linked_ram_high'],16),0x801e0000);self.assertGreater(r['headroom_to_stack_region'],0)
 def test_disc(self):
  import sys
  sys.path.insert(0,str(ROOT/'tools'));from cnk import ISO;from disc07 import edc,ecc
  b=(P/'ETD_PSX_M07.bin').read_bytes();self.assertEqual(len(b)%2352,0);self.assertEqual(len(b)//2352,300);cooked=bytearray()
  for i in range(0,len(b),2352):
   s=bytearray(b[i:i+2352]);self.assertEqual(s[:12],b'\0'+b'\xff'*10+b'\0');self.assertEqual(s[15],2);self.assertEqual(s[16:20],s[20:24]);self.assertEqual(struct.unpack_from('<I',s,2072)[0],edc(s[16:2072]));s[12:16]=bytes(4);self.assertEqual(s[2076:2248],ecc(s[12:2076],86,24,2,86));self.assertEqual(s[2248:2352],ecc(s[12:2248],52,43,86,88));cooked.extend(s[24:2072])
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'test.iso';p.write_bytes(cooked)
   with ISO(p) as iso:
    self.assertEqual(iso.file('ETD_CLIP.EXE'),(P/'ETD_CLIP.EXE').read_bytes());self.assertIn(b'cdrom:\\ETD_CLIP.EXE;1',iso.file('SYSTEM.CNF'))
  self.assertIn('TRACK 01 MODE2/2352',(P/'ETD_PSX_M07.cue').read_text())
