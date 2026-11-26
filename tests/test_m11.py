import ctypes, json, struct, sys, tempfile, unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'build_m11/play';sys.path.insert(0,str(ROOT/'tools'))
from cnk import ISO
from disc11 import edc,ecc
I=ctypes.POINTER(ctypes.c_int); S=ctypes.POINTER(ctypes.c_int16)
class Milestone11(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.lib=ctypes.CDLL(str(P/'rig11_host.so'));cls.lib.matrix11.argtypes=[ctypes.c_int,S];cls.lib.pose11.argtypes=[ctypes.c_int]*3+[I];cls.lib.fire_status11.argtypes=[I];cls.lib.fire_mesh11.argtypes=[ctypes.c_int,ctypes.c_int,I];cls.lib.fire_mesh11.restype=ctypes.c_int;cls.z=np.load(P/'rig.npz');cls.poses=np.load(P/'poses_host.npz')['poses']
 def status(self):
  s=(ctypes.c_int*8)();self.lib.fire_status11(s);return list(s)
 def test_lossless_all_matrices(self):
  m=self.z['matrices'].reshape(245,516);buf=np.zeros(516,dtype=np.int16)
  for i in list(range(245))+np.random.default_rng(11).permutation(245).tolist()+list(reversed(range(245))):
   self.lib.matrix11(i,buf.ctypes.data_as(S));np.testing.assert_array_equal(buf,m[i])
 def test_lossless_pose_and_transition(self):
  p=self.poses;buf=np.empty((1157,3),np.int32)
  for i in range(245):
   j=(i*73+7)%245;k=i%5
   self.lib.pose11(i,j,k,buf.ctypes.data_as(I));np.testing.assert_array_equal(buf,(p[j]*(4-k)+p[i]*k+2)>>2)
   self.lib.pose11(i,i,4,buf.ctypes.data_as(I));np.testing.assert_array_equal(buf,p[i])
 def test_fire_hits_reset(self):
  l=self.lib;l.fire_reset11();self.assertEqual(self.status(),[0,0,2,2,2,800,800,800]);
  for _ in range(30):l.fire_step11(8192)
  self.assertEqual(self.status()[:1],[2]);self.assertEqual(self.status()[2:5],[2,0,2]);l.fire_step11(8);self.assertEqual(self.status(),[0,0,2,2,2,800,800,800])
 def test_fire_lifetime_and_cooldown(self):
  l=self.lib;l.fire_reset11();l.fire_step11(8192);self.assertEqual(self.status()[1],3);l.fire_step11(8192);self.assertEqual(self.status()[1],3);l.fire_step11(0);l.fire_step11(8192);self.assertEqual(self.status()[1],6)
  for _ in range(14):l.fire_step11(0)
  self.assertEqual(self.status()[1],0)
 def test_fire_heading_grounding_and_bounds(self):
  l=self.lib;l.fire_reset11();l.fire_position11(-1152,800,-3200,32,1)
  for _ in range(35):l.fire_step11(8192)
  self.assertEqual(self.status()[0],0);l.fire_reset11();l.fire_position11(-1152,500,-3200,0,0)
  for _ in range(20):l.fire_step11(8192)
  self.assertEqual(self.status()[1],0)
  l.fire_position11(-9000,800,-9000,0,1);l.fire_step11(8192);l.fire_step11(0);self.assertEqual(self.status()[1],0)
 def test_effect_mesh_and_pool(self):
  l=self.lib;l.fire_reset11();a=np.empty((60,10),np.int32)
  for _ in range(500):
   l.fire_step11(8192);n=l.fire_mesh11(0,4096,a.ctypes.data_as(I));self.assertLessEqual(n,60);self.assertLessEqual(self.status()[1],24);self.assertTrue(np.all((a[:n,9]<0x1000000)|(a[:n,9]==0x1000000)|(a[:n,9]==0x2000000)));self.assertTrue(np.all(a[:n,9]>=0))
  self.assertEqual(self.status()[0],2)
 def test_assets_memory(self):
  for n in ['rig.npz','poses_host.npz','scene.h','world.h','farm06.npz','visibility.h','visibility.npz']:
   self.assertEqual((P/n).read_bytes(),(ROOT/'build_m10/play'/n).read_bytes())
  r=json.loads((P/'report.json').read_text());self.assertGreater(r['ram_saved'],100000);self.assertLess(int(r['linked_ram_high'],16),0x801e0000);self.assertEqual(r['packet_size'],22)
 def test_source_fire_texture(self):
  r=json.loads((P/'fire_texture_report.json').read_text());self.assertEqual(r['filename'],'ECFECEFC.PXT');self.assertEqual(r['size'],[32,32]);self.assertEqual(r['bytes'],1536);t=np.load(P/'firetex11.npy');self.assertEqual(t.shape,(32,32));self.assertTrue(np.any(t==0));self.assertTrue(np.any(t!=0));self.assertTrue(np.all((t[t!=0]&0x8000)!=0));
  rects=[r['vram'],r['clut']];existing=[[0,0,320,240],[0,256,320,240],[320,0,128,256],[448,0,32,64],[512,0,32,64],[768,0,256,3]]
  for b in json.loads((P/'report.json').read_text())['bindings']:existing.extend([b['vram'],b['clut']])
  for x,y,w,h in rects:
   self.assertTrue(0<=x<x+w<=1024 and 0<=y<y+h<=512)
   for a,b,c,d in existing:self.assertFalse(x<a+c and a<x+w and y<b+d and b<y+h)
 def test_disc(self):
  e=(P/'ETD_FIRE.EXE').read_bytes();self.assertEqual(e[:8],b'PS-X EXE');self.assertEqual(len(e)-2048,struct.unpack_from('<I',e,28)[0]);b=(P/'ETD_PSX_M11.bin').read_bytes();self.assertEqual(len(b)%2352,0);cooked=bytearray()
  for i in range(0,len(b),2352):
   s=bytearray(b[i:i+2352]);self.assertEqual(s[15],2);self.assertEqual(s[16:20],s[20:24]);self.assertEqual(struct.unpack_from('<I',s,2072)[0],edc(s[16:2072]));s[12:16]=bytes(4);self.assertEqual(s[2076:2248],ecc(s[12:2076],86,24,2,86));self.assertEqual(s[2248:2352],ecc(s[12:2248],52,43,86,88));cooked.extend(s[24:2072])
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'test.iso';p.write_bytes(cooked)
   with ISO(p) as iso:self.assertEqual(iso.file('ETD_FIRE.EXE'),e);self.assertIn(b'cdrom:\\ETD_FIRE.EXE;1',iso.file('SYSTEM.CNF'))
