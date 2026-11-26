import ctypes,json,struct,sys,tempfile,unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'build_m12/play';A=ROOT/'assets_m12';sys.path.insert(0,str(ROOT/'tools'))
from disc12 import edc,ecc
from cnk import ISO
I=ctypes.POINTER(ctypes.c_int)
class Milestone12(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.lib=ctypes.CDLL(str(P/'collect12_host.so'));cls.lib.collect_status12.argtypes=[I];cls.lib.collect_mesh12.argtypes=[I];cls.lib.collect_mesh12.restype=ctypes.c_int;cls.report=json.loads((A/'collect_report.json').read_text());cls.active=cls.report['active']
 def status(self):
  a=(ctypes.c_int*8)();self.lib.collect_status12(a);return list(a)
 def test_source_placements(self):
  p=json.loads((A/'placements.json').read_text());g=p['gems'];self.assertEqual(len(g),290);self.assertEqual(len(p['other_characters']),90);self.assertEqual(sum(x['value'] for x in g),773);self.assertEqual(len({x['record_offset'] for x in g}),290);self.assertEqual(len({x['name'] for x in g}),290)
  for x in g:np.testing.assert_array_equal(np.rint((np.array(x['source_xyz'])-[38000,0,2000])*[1,-1,1]),x['sector_xyz'])
 def test_score_once_and_reset(self):
  l=self.lib;l.collect_init12();self.assertEqual(self.status()[0],0);expected=0
  for g in self.active:
   l.collect_pos12(*g['sector_xyz'],0);l.collect_tick12(0);expected+=g['value'];self.assertEqual(self.status()[0],expected)
   for _ in range(20):l.collect_tick12(0)
   self.assertEqual(self.status()[0],expected)
  self.assertEqual(expected,5);self.assertEqual(self.status()[5:],[1,1,1]);l.collect_tick12(8);self.assertEqual(self.status()[0],0);self.assertEqual(self.status()[5:],[0,0,0])
 def test_pickup_radius_and_height(self):
  l=self.lib;l.collect_init12();x,y,z=self.active[1]['sector_xyz'];l.collect_pos12(x,y-200,z,0);l.collect_tick12(0);self.assertEqual(self.status()[0],0);l.collect_pos12(x+200,y,z,0);l.collect_tick12(0);self.assertEqual(self.status()[0],0);l.collect_pos12(x,y,z,0);l.collect_tick12(0);self.assertEqual(self.status()[0],2)
 def test_sparx_mesh_and_follow(self):
  l=self.lib;l.collect_init12();a=np.empty((339,10),np.int32);before=self.status();l.collect_pos12(-1250,800,-3200,16)
  for _ in range(32):
   l.collect_tick12(0);n=l.collect_mesh12(a.ctypes.data_as(I));self.assertGreaterEqual(n,177);self.assertLessEqual(n,339);self.assertTrue(np.all((a[:n,9]>=0)&(a[:n,9]<0x1000000)))
  after=self.status();self.assertNotEqual(before[2:5],after[2:5]);self.assertLess(abs(after[2]+1250),200);self.assertLess(abs(after[4]+3200),200)
 def test_diagnostics_toggle(self):
  l=self.lib;l.diag_reset12();self.assertEqual(l.diag_tick12(0),0);self.assertEqual(l.diag_tick12(4096),2);self.assertEqual(l.diag_tick12(4096),2);self.assertEqual(l.diag_tick12(0),2);self.assertEqual(l.diag_tick12(4096),0);l.diag_tick12(0);self.assertEqual(l.diag_tick12(4096),2);self.assertEqual(l.diag_tick12(8),0)
 def test_original_audio_export(self):
  import hashlib
  for x in self.report['audio']:
   b=(A/x['name']).read_bytes();self.assertEqual(b[:4],b'VAGp');self.assertEqual(struct.unpack_from('>II',b,12),(x['bytes'],22050));self.assertEqual(hashlib.sha256(b[48:]).hexdigest(),x['sha256'])
 def test_unchanged_assets_and_memory(self):
  for n in ['rig.npz','poses_host.npz','scene.h','world.h','farm06.npz','visibility.h','visibility.npz','firetex11.h','rig11_data.h']:
   self.assertEqual((P/n).read_bytes(),(ROOT/'build_m11/play'/n).read_bytes())
  r=json.loads((P/'report.json').read_text());self.assertGreater(r['headroom_to_stack_region'],128*1024);self.assertLess(int(r['linked_ram_high'],16),0x801e0000)
 def test_disc(self):
  e=(P/'ETD_GEMS.EXE').read_bytes();self.assertEqual(e[:8],b'PS-X EXE');self.assertEqual(len(e)-2048,struct.unpack_from('<I',e,28)[0]);b=(P/'ETD_PSX_M12.bin').read_bytes();self.assertEqual(len(b)%2352,0);cooked=bytearray()
  for i in range(0,len(b),2352):
   s=bytearray(b[i:i+2352]);self.assertEqual(s[15],2);self.assertEqual(s[16:20],s[20:24]);self.assertEqual(struct.unpack_from('<I',s,2072)[0],edc(s[16:2072]));s[12:16]=bytes(4);self.assertEqual(s[2076:2248],ecc(s[12:2076],86,24,2,86));self.assertEqual(s[2248:2352],ecc(s[12:2248],52,43,86,88));cooked.extend(s[24:2072])
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'test.iso';p.write_bytes(cooked)
   with ISO(p) as iso:self.assertEqual(iso.file('ETD_GEMS.EXE'),e);self.assertIn(b'cdrom:\\ETD_GEMS.EXE;1',iso.file('SYSTEM.CNF'))
