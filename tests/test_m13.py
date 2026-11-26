import ctypes,json,struct,sys,tempfile,unittest,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'build_m13/play';sys.path.insert(0,str(ROOT/'tools'))
from disc13 import edc,ecc
from cnk import ISO
class Milestone13(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.c=ctypes.CDLL(str(P/'collect13_host.so'));cls.s=ctypes.CDLL(str(P/'spu13_host.so'));cls.a=json.loads((P/'audio_report.json').read_text());cls.g=json.loads((ROOT/'assets_m12/collect_report.json').read_text())['active']
 def state(self):
  a=(ctypes.c_int*8)();e=(ctypes.c_int*4)();self.c.collect_status13(a);self.c.collect_events13(e);return list(a),list(e)
 def test_bank_source_bytes(self):
  bank=(P/'sfx_bank.bin').read_bytes();self.assertEqual(len(bank),self.a['bank_bytes']);self.assertEqual(bank[1],7);self.assertEqual(len(bank)%64,0);self.assertLess(self.a['limit'],512*1024)
  for row in self.a['samples']:
   i=row['spu_byte_address']-self.a['base'];d=bank[i:i+row['size']];self.assertEqual(d,(ROOT/'assets_m12'/row['name']).read_bytes()[48:]);self.assertEqual(hashlib.sha256(d).hexdigest(),row['sha256']);self.assertEqual(row['pitch'],2048);self.assertEqual(i%64,0)
 def test_spu_upload_mock(self):
  s=self.s;self.assertEqual(s.mock_init13(0),1);self.assertEqual(s.mock_reg13(0x1ac),4);self.assertEqual(s.mock_reg13(0x1aa),0xc000);self.assertEqual(s.mock_info13(2),self.a['bank_bytes']//2);self.assertEqual(s.mock_info13(3),0);b=ctypes.create_string_buffer(self.a['bank_bytes']);s.mock_bank13(b);self.assertEqual(b.raw,(P/'sfx_bank.bin').read_bytes())
 def test_spu_voices_and_reset(self):
  s=self.s;s.mock_init13(0)
  for i in range(9):
   sample=i%2;s.mock_play13(sample);v=4+i%4;self.assertEqual(s.mock_reg13(0x188),1<<v);self.assertEqual(s.mock_reg13(v*16+4),2048);self.assertEqual(s.mock_reg13(v*16+6),self.a['samples'][sample]['spu_byte_address']//8)
  s.mock_play13(-1);s.mock_play13(2);self.assertEqual(s.mock_info13(0),9);s.mock_stop13();self.assertEqual(s.mock_reg13(0x18c),0xf0);s.mock_play13(1);self.assertEqual(s.mock_reg13(0x188),16)
 def test_spu_timeout(self):
  s=self.s;self.assertEqual(s.mock_init13(1),0);s.mock_play13(0);self.assertEqual(s.mock_info13(0),0);self.assertEqual(s.mock_info13(4),0)
 def test_direct_event_once(self):
  c=self.c;c.collect_init13();expected=0
  for g in self.g:
   c.collect_pos13(*g['sector_xyz'],0);c.collect_tick13(0);expected+=g['value'];a,e=self.state();self.assertEqual(a[0],expected);self.assertEqual(e[:3],[1,1,0]);c.collect_tick13(0);self.assertEqual(self.state()[1][:3],[0,0,0])
  c.collect_tick13(8);self.assertEqual(self.state()[0][0],0);self.assertEqual(self.state()[1],[0,0,0,-1])
 def test_assist_all_three(self):
  c=self.c
  for i,g in enumerate(self.g):
   c.collect_init13();x,y,z=g['sector_xyz'];c.collect_pos13(x,y,z-290,0);events=[];c.collect_tick13(0);self.assertEqual(self.state()[1],[0,0,0,i]);self.assertEqual(self.state()[0][0],0)
   for _ in range(24):
    c.collect_tick13(0);a,e=self.state();events.append(e[:3])
   self.assertEqual(events.count([1,0,1]),1);self.assertEqual(a[0],g['value']);self.assertEqual(a[5+i],1)
 def test_blocked_or_airborne_assist(self):
  c=self.c;x,y,z=self.g[0]['sector_xyz'];c.collect_init13();self.assertEqual(c.collect_floor13(x-290,z),32767);c.collect_pos13(x-290,y,z,0)
  for _ in range(24):c.collect_tick13(0)
  self.assertEqual(self.state()[0][0],0);self.assertEqual(self.state()[1][3],-1)
  x,y,z=self.g[1]['sector_xyz'];c.collect_init13();c.collect_pos13(x,y-200,z-290,0)
  for _ in range(24):c.collect_tick13(0)
  self.assertEqual(self.state()[0][0],0)
 def test_cancel_assist(self):
  c=self.c;c.collect_init13();x,y,z=self.g[1]['sector_xyz'];c.collect_pos13(x,y,z-290,0);c.collect_tick13(0);self.assertEqual(self.state()[1][3],1);c.collect_pos13(x,y,z-800,0)
  for _ in range(25):c.collect_tick13(0)
  self.assertEqual(self.state()[0][0],0);self.assertEqual(self.state()[1][3],-1)
 def test_native_and_unchanged_assets(self):
  r=json.loads((P/'report.json').read_text());self.assertGreater(r['headroom_to_stack_region'],128*1024);e=(P/'ETD_SFX.EXE').read_bytes();self.assertEqual(e[:8],b'PS-X EXE');self.assertEqual(len(e)-2048,struct.unpack_from('<I',e,28)[0]);self.assertIn((P/'sfx_bank.bin').read_bytes(),e)
  for n in ['rig.npz','poses_host.npz','scene.h','world.h','farm06.npz','visibility.h','visibility.npz','firetex11.h','rig11_data.h','collectdata12.h']:self.assertEqual((P/n).read_bytes(),(ROOT/'build_m12/play'/n).read_bytes())
 def test_disc(self):
  e=(P/'ETD_SFX.EXE').read_bytes();b=(P/'ETD_PSX_M13.bin').read_bytes();self.assertEqual(len(b)%2352,0);cooked=bytearray()
  for i in range(0,len(b),2352):
   s=bytearray(b[i:i+2352]);self.assertEqual(s[15],2);self.assertEqual(s[16:20],s[20:24]);self.assertEqual(struct.unpack_from('<I',s,2072)[0],edc(s[16:2072]));s[12:16]=bytes(4);self.assertEqual(s[2076:2248],ecc(s[12:2076],86,24,2,86));self.assertEqual(s[2248:2352],ecc(s[12:2248],52,43,86,88));cooked.extend(s[24:2072])
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'test.iso';p.write_bytes(cooked)
   with ISO(p) as iso:self.assertEqual(iso.file('ETD_SFX.EXE'),e);self.assertIn(b'cdrom:\\ETD_SFX.EXE;1',iso.file('SYSTEM.CNF'))
