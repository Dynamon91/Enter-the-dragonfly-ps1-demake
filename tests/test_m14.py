import ctypes,json,struct,sys,tempfile,unittest,hashlib,random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'build_m14/play';sys.path.insert(0,str(ROOT/'tools'))
from disc14 import edc,ecc
from cnk import ISO
class Milestone14(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.b=ctypes.CDLL(str(P/'basket14_host.so'));cls.s=ctypes.CDLL(str(P/'spu14_host.so'));cls.r=json.loads((ROOT/'assets_m14/basket_report.json').read_text())
 def state(self):
  a=(ctypes.c_int*10)();self.b.basket_status14(a);return list(a)
 def setup_at(self,i,dist=260):
  self.b.basket_init14();x,y,z=self.r['active'][i]['sector_xyz'];self.b.basket_pos14(x,self.b.basket_floor14(x,z-dist),z-dist,0)
 def test_source(self):
  self.assertEqual(len(self.r['source_placements']),27);self.assertEqual(self.r['source_triangles'],554);self.assertEqual(self.r['lod_triangles'],158);self.assertEqual(len(self.r['active']),2)
  for g in self.r['active']:self.assertLessEqual(abs(self.b.basket_floor14(g['sector_xyz'][0],g['sector_xyz'][2])-g['sector_xyz'][1]),110)
 def test_charge_and_reward_once(self):
  for i in range(2):
   self.setup_at(i);events=[]
   for _ in range(30):self.b.basket_tick14(32784);events.append(self.state())
   self.assertEqual(sum(a[1] for a in events),1);self.assertEqual(sum(a[2] for a in events),1);self.assertEqual(events[-1][0],1);self.assertEqual(events[-1][6+i],2)
   self.b.basket_tick14(8);self.assertEqual(self.state()[0:3],[0,0,0]);self.assertEqual(self.state()[6:8],[0,0])
 def test_fire_and_delayed_pickup(self):
  for i in range(2):
   self.setup_at(i);events=[]
   for _ in range(18):self.b.basket_tick14(8192);events.append(self.state())
   self.assertEqual(sum(a[1] for a in events),1);self.assertEqual(events[-1][6+i],1);self.assertEqual(events[-1][0],0)
   for _ in range(9):self.b.basket_tick14(16)
   self.assertEqual(self.state()[6+i],2);self.assertEqual(self.state()[0],1)
 def test_no_walk_damage_or_stationary_charge(self):
  self.setup_at(0)
  for _ in range(20):self.b.basket_tick14(16)
  self.assertEqual(self.state()[6:8],[0,0]);self.b.basket_tick14(32768);self.assertEqual(self.state()[6:8],[0,0])
 def test_render_bounds(self):
  self.setup_at(0);a=(ctypes.c_int*3160)();self.assertEqual(self.b.basket_mesh14(a),316)
  for _ in range(18):self.b.basket_tick14(8192)
  self.assertLess(self.b.basket_mesh14(a),316)
 def test_packed_coordinates(self):
  rng=random.Random(14);c=(ctypes.c_uint32*3)();d=(ctypes.c_uint32*3)()
  # Every 11-bit signed coordinate, mixed signs and random combinations.
  for x in range(-1024,1024):
   v=[x,-1024,1023]+[rng.randrange(-1024,1024) for _ in range(3)]
   for k in range(3):c[k]=(v[2*k]&65535)|((v[2*k+1]&65535)<<16)
   self.b.packet_roundtrip14(c,d);self.assertEqual(list(c),list(d))
 def test_sound_bank_and_third_voice(self):
  a=json.loads((P/'audio_report.json').read_text());bank=(P/'sfx_bank.bin').read_bytes();self.assertEqual(len(a['samples']),3);self.assertEqual(a['samples'][2]['sha256'],self.r['sound_sha256']);self.assertLess(a['limit'],512*1024)
  for row in a['samples']:
   i=row['spu_byte_address']-a['base'];src=ROOT/('assets_m14' if row['name']=='spy01.vag' else 'assets_m12')/row['name'];self.assertEqual(bank[i:i+row['size']],src.read_bytes()[48:])
  s=self.s;self.assertEqual(s.mock_init13(0),1);b=ctypes.create_string_buffer(len(bank));s.mock_bank13(b);self.assertEqual(b.raw,bank);s.mock_play13(2);self.assertEqual(s.mock_reg13(4*16+6),a['samples'][2]['spu_byte_address']//8);s.mock_play13(3);self.assertEqual(s.mock_info13(0),1)
 def test_native_and_previous_assets(self):
  e=(P/'ETD_BASK.EXE').read_bytes();r=json.loads((P/'report.json').read_text());self.assertEqual(e[:8],b'PS-X EXE');self.assertEqual(len(e)-2048,struct.unpack_from('<I',e,28)[0]);self.assertGreater(r['headroom_to_stack_region'],128*1024);self.assertEqual(r['packet_size'],20);self.assertIn((P/'sfx_bank.bin').read_bytes(),e)
  for n in ['rig.npz','poses_host.npz','scene.h','world.h','farm06.npz','visibility.h','visibility.npz','firetex11.h','rig11_data.h','collectdata12.h']:self.assertEqual((P/n).read_bytes(),(ROOT/'build_m13/play'/n).read_bytes())
 def test_disc(self):
  e=(P/'ETD_BASK.EXE').read_bytes();b=(P/'ETD_PSX_M14.bin').read_bytes();self.assertEqual(len(b)%2352,0);cooked=bytearray()
  for i in range(0,len(b),2352):
   s=bytearray(b[i:i+2352]);self.assertEqual(s[15],2);self.assertEqual(s[16:20],s[20:24]);self.assertEqual(struct.unpack_from('<I',s,2072)[0],edc(s[16:2072]));s[12:16]=bytes(4);self.assertEqual(s[2076:2248],ecc(s[12:2076],86,24,2,86));self.assertEqual(s[2248:2352],ecc(s[12:2248],52,43,86,88));cooked.extend(s[24:2072])
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'test.iso';p.write_bytes(cooked)
   with ISO(p) as iso:self.assertEqual(iso.file('ETD_BASK.EXE'),e);self.assertIn(b'cdrom:\\ETD_BASK.EXE;1',iso.file('SYSTEM.CNF'))
