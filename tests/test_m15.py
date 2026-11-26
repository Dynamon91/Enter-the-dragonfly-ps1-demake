import ctypes,json,struct,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'build_m15/play';sys.path.insert(0,str(ROOT/'tools'))
from disc15 import edc,ecc
from cnk import ISO
class Milestone15(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.f=ctypes.CDLL(str(P/'fodder15_host.so'));cls.r=json.loads((ROOT/'assets_m15/fodder_report.json').read_text())
 def state(self):
  a=(ctypes.c_int*14)();self.f.fodder_status15(a);return list(a)
 def setup(self):self.f.fodder_init15();self.f.fodder_tick15(768)
 def test_original_assets(self):
  r=self.r;self.assertEqual(r['source_placement_count'],12);self.assertEqual(r['source_placements_active'],0);self.assertEqual(len(r['texture_bindings']),4);self.assertTrue(all(p['floor'] is None for p in r['sheep_placements']));self.assertEqual(r['sheep_triangles'],353);self.assertEqual(r['butterfly_triangles'],49)
 def test_diagnostic_toggle_edges(self):
  self.f.fodder_init15();self.assertEqual(self.state()[:2],[0,3]);self.f.fodder_tick15(512);self.assertEqual(self.state()[0],1);self.f.fodder_tick15(512);self.assertEqual(self.state()[0],1);self.f.fodder_tick15(0);self.f.fodder_tick15(512);self.assertEqual(self.state()[0],0)
 def test_fire_and_charge_heal_once(self):
  for attack in (8192,32784):
   self.setup();events=[]
   for i in range(65):self.f.fodder_tick15(attack if i<15 else 0);events.append(self.state())
   self.assertEqual(sum(a[2] for a in events),1);self.assertEqual(sum(a[3] for a in events),1);self.assertEqual(events[-1][:2],[3,3]);self.assertEqual(events[-1][11],0)
 def test_health_edges_and_zero_recovery(self):
  self.setup();self.f.fodder_tick15(256);self.assertEqual(self.state()[1],2)
  for i in range(4):self.f.fodder_tick15(0);self.f.fodder_tick15(256)
  self.assertEqual(self.state()[1],0)
  for i in range(65):self.f.fodder_tick15(8192 if i<15 else 0)
  self.assertEqual(self.state()[:2],[3,1]);self.f.fodder_tick15(8);self.assertEqual(self.state()[:2],[0,3])
 def test_full_health_no_overflow(self):
  self.f.fodder_init15();self.f.fodder_tick15(512);events=[]
  for i in range(65):self.f.fodder_tick15(8192 if i<15 else 0);events.append(self.state())
  self.assertEqual(events[-1][:2],[3,3]);self.assertEqual(sum(a[3] for a in events),0)
 def test_butterfly_expiry_outside_range(self):
  self.setup()
  for _ in range(8):self.f.fodder_tick15(8192)
  self.assertEqual(self.state()[0],2);x,z=-3312,-1037;self.f.fodder_pos15(x,self.f.fodder_floor15(x,z),z,0)
  for _ in range(190):self.f.fodder_tick15(0)
  self.assertEqual(self.state()[:2],[3,2])
 def test_mesh_capacity_and_health_visibility(self):
  self.setup();a=(ctypes.c_int*3530)();self.assertEqual(self.f.fodder_mesh15(a),353)
  for _ in range(8):self.f.fodder_tick15(8192)
  self.assertEqual(self.f.fodder_mesh15(a),49);n=self.f.fodder_collect15(a)
  for _ in range(3):self.f.fodder_tick15(0);self.f.fodder_tick15(256)
  self.assertEqual(self.state()[1],0);self.assertLess(self.f.fodder_collect15(a),n)
 def test_native_assets(self):
  e=(P/'ETD_FODR.EXE').read_bytes();r=json.loads((P/'report.json').read_text());self.assertEqual(e[:8],b'PS-X EXE');self.assertEqual(len(e)-2048,struct.unpack_from('<I',e,28)[0]);self.assertGreater(r['headroom_to_stack_region'],65536);self.assertEqual(r['fodder_mesh_capacity'],353)
  for n in ['rig.npz','poses_host.npz','scene.h','world.h','farm06.npz','visibility.h','visibility.npz','firetex11.h','rig11_data.h','collectdata12.h','basketdata14.h','sfx_bank.bin']:self.assertEqual((P/n).read_bytes(),(ROOT/'build_m14/play'/n).read_bytes())
 def test_disc(self):
  e=(P/'ETD_FODR.EXE').read_bytes();b=(P/'ETD_PSX_M15.bin').read_bytes();self.assertEqual(len(b)%2352,0);cooked=bytearray()
  for i in range(0,len(b),2352):
   s=bytearray(b[i:i+2352]);self.assertEqual(s[15],2);self.assertEqual(s[16:20],s[20:24]);self.assertEqual(struct.unpack_from('<I',s,2072)[0],edc(s[16:2072]));s[12:16]=bytes(4);self.assertEqual(s[2076:2248],ecc(s[12:2076],86,24,2,86));self.assertEqual(s[2248:2352],ecc(s[12:2248],52,43,86,88));cooked.extend(s[24:2072])
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'test.iso';p.write_bytes(cooked)
   with ISO(p) as iso:self.assertEqual(iso.file('ETD_FODR.EXE'),e);self.assertIn(b'cdrom:\\ETD_FODR.EXE;1',iso.file('SYSTEM.CNF'))
