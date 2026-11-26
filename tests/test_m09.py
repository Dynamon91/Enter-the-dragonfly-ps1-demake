import sys, unittest, struct,json,hashlib,tempfile
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'build_m09/play';A=ROOT/'build_m09/animation';sys.path.insert(0,str(ROOT/'tools'))
from cnk import ISO
from disc09 import edc,ecc
class Milestone9(unittest.TestCase):
 def test_curves(self):
  r=json.loads((A/'animation.json').read_text());z=np.load(A/'curves.npz');self.assertEqual(r['resolved_clips'],105);self.assertEqual(r['keys'],43885);self.assertEqual(r['duplicate_confirmed'],104);self.assertEqual(len(r['unresolved']),2)
  for c in r['clips']:
   a=z[c['name']];o=z[c['name']+'_offsets'];m=c['metadata'];self.assertEqual(a.shape,(4,c['key_count']));self.assertEqual(len(o),c['curve_count']+1);self.assertTrue(np.isfinite(a[:2]).all());self.assertTrue(np.all(np.isfinite(a[2:])|(a[2:].view('<u4')==0xffffffff)))
   self.assertEqual(int((a[2:].view('<u4')==0xffffffff).sum()),c['sentinel_words']);raw=[]
   for k,t in enumerate(m['curves']):
    v=a[:,o[k]:o[k+1]];self.assertEqual(v.shape[1],t['keys']);self.assertTrue(np.all(np.diff(v[0])>0));self.assertAlmostEqual(float(v[0,0]),t['start'],places=4);self.assertAlmostEqual(float(v[0,-1]),t['end'],places=4);raw.append(v.astype('<f4').tobytes())
   self.assertEqual(hashlib.sha256(b''.join(raw)).hexdigest(),c['sha256'])
 def test_essential_clips(self):
  r=json.loads((A/'animation.json').read_text());d={c['name']:c for c in r['clips']};
  for name in ['idle','walk','run','jump_start','jump_cycle','jump_land','glide_cycle','charge','fire_breath','swim','hover_cycle']:self.assertIn('spyro_'+name,d)
  self.assertGreater(d['spyro_jump_start']['sentinel_words'],0)
 def test_spatial_partition(self):
  z=np.load(P/'farm06.npz');v=np.load(P/'visibility.npz');f=z['faces'];t=z['vertices'][f];ids=v['face_ids'];rows=v['clusters'];np.testing.assert_array_equal(np.sort(ids),np.arange(len(f)));self.assertEqual(len(rows),128)
  for x in rows:
   q=t[ids[x[6]:x[6]+x[7]]];self.assertTrue(np.all(q>=x[:3]));self.assertTrue(np.all(q<=x[3:6]));self.assertLessEqual(x[7],48)
 def test_geometry_preserved(self):
  a=np.load(ROOT/'build_m08/play/farm06.npz');b=np.load(P/'farm06.npz');self.assertEqual(a.files,b.files)
  for k in a.files:np.testing.assert_array_equal(a[k],b[k])
 def test_visibility(self):
  from check_visibility09 import check
  r=check(P,full=True);self.assertEqual(r['views'],192);self.assertEqual(r['false_rejects'],0);self.assertLess(r['avg_candidate_faces'],r['baseline_faces']/2);self.assertLess(r['avg_transformed_vertices'],r['baseline_vertices']/2)
 def test_preview(self):
  np.testing.assert_array_equal(np.array(Image.open(ROOT/'build_m08/play/farm_preview.png')),np.array(Image.open(P/'farm_preview.png')))
 def test_native_disc(self):
  e=(P/'ETD_VIS.EXE').read_bytes();r=json.loads((P/'report.json').read_text());self.assertEqual(e[:8],b'PS-X EXE');self.assertEqual(len(e)-2048,struct.unpack_from('<I',e,28)[0]);self.assertLess(int(r['linked_ram_high'],16),0x801e0000);b=(P/'ETD_PSX_M09.bin').read_bytes();self.assertEqual(len(b),300*2352);cooked=bytearray()
  for i in range(0,len(b),2352):
   s=bytearray(b[i:i+2352]);self.assertEqual(s[:12],b'\0'+b'\xff'*10+b'\0');self.assertEqual(s[15],2);self.assertEqual(s[16:20],s[20:24]);self.assertEqual(struct.unpack_from('<I',s,2072)[0],edc(s[16:2072]));s[12:16]=bytes(4);self.assertEqual(s[2076:2248],ecc(s[12:2076],86,24,2,86));self.assertEqual(s[2248:2352],ecc(s[12:2248],52,43,86,88));cooked.extend(s[24:2072])
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'test.iso';p.write_bytes(cooked)
   with ISO(p) as iso:self.assertEqual(iso.file('ETD_VIS.EXE'),e);self.assertIn(b'cdrom:\\ETD_VIS.EXE;1',iso.file('SYSTEM.CNF'))
