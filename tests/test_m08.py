import unittest, json, struct, tempfile, sys
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'build_m08/play';OLD=ROOT/'build_m07/play';sys.path.insert(0,str(ROOT/'tools'))
from hash08 import md4,fold
from refine08 import subdiv
from disc08 import edc,ecc
from cnk import ISO
class Milestone8(unittest.TestCase):
 def test_md4(self):
  for x,y in [(b'','31d6cfe0d16ae931b73c59d7e0c089c0'),(b'a','bde52cb31de33e46245e05fbdbd6fb24'),(b'abc','a448017aaf21d8525fc10ae87aa6729d'),(b'message digest','d9130a8164549fe818874806e1c7014b'),(b'abcdefghijklmnopqrstuvwxyz','d79e1c308aa5bbcdeea8ed63df412da9')]:self.assertEqual(md4(x).hex(),y)
 def test_registry(self):
  r=json.loads((P/'texture_registry.json').read_text());entries={int(e['hash'],16):e for e in r['entries']};self.assertEqual(len(entries),540);rr=r['resolved_references'];self.assertEqual(len(rr),693);self.assertEqual(len({t['filename'] for t in rr}),476);self.assertEqual(sum(t['dimensions_match'] for t in rr),688)
  for x in rr:
   e=entries[fold(x['filename'].lower().encode('ascii'))];self.assertEqual(x['group'],e['group']);self.assertEqual(x['hash'],e['hash']);self.assertTrue(any(t['filename']==x['filename'] and t['size']==e['size'] for t in r['materials'][x['material']]))
 def test_materials(self):
  r=json.loads((P/'report.json').read_text());self.assertEqual(len(r['bindings']),23);self.assertEqual([x['group'] for x in r['actor_bindings']],[303,21,296]);self.assertEqual(sum(x['previous_group'] is not None and x['previous_group']!=x['group'] for x in r['bindings']),14)
  rect=[]
  for b in r['bindings']:
   self.assertTrue(b['binding'].startswith('verified'));self.assertEqual(b['hash'],f"{fold(b['source_refs'][0]['filename'].lower().encode()):08x}");rect.extend([b['vram'],b['clut']])
  for i,(x,y,w,h) in enumerate(rect):
   self.assertTrue(0<=x<x+w<=1024 and 256<=y<y+h<=512)
   for xx,yy,ww,hh in rect[:i]:self.assertFalse(x<xx+ww and xx<x+w and y<yy+hh and yy<y+h)
 def test_ground_mesh(self):
  r=json.loads((ROOT/'build_m08/shadow/hub_report.json').read_text());self.assertEqual(r['matched'],39);self.assertEqual(r['triangles'],5242);self.assertFalse(r['unmatched']);self.assertLess(max(x['bounds_error'] for x in r['meshes']),.01)
  z=np.load(P/'farm06.npz');self.assertEqual(len(z['faces']),4973);self.assertLess(z['faces'].max(),len(z['vertices']));self.assertLess(z['texture_id'].max(),23)
 def test_subdivision(self):
  t=np.array([[0.,0,0],[1000,0,0],[0,0,1000]]);u=t[:,[0,2]]/20;out=subdiv(t,u,384);area=0
  for v,uv in out:
   np.testing.assert_allclose(uv,v[:,[0,2]]/20);self.assertLessEqual(np.linalg.norm(v-np.roll(v,1,axis=0),axis=1).max(),384.0001);area+=np.linalg.norm(np.cross(v[1]-v[0],v[2]-v[0]))/2
  self.assertAlmostEqual(area,500000)
 def test_collision(self):
  a=np.load(OLD/'farm06.npz')['floor'];b=np.load(P/'farm06.npz')['floor'];np.testing.assert_array_equal(a[a!=32767],b[a!=32767]);self.assertEqual(int((b!=32767).sum()),879);self.assertEqual(int(((a==32767)&(b!=32767)).sum()),652)
 def test_preview_floor(self):
  for v in [OLD,P]:
   im=np.asarray(Image.open(v/'farm_preview.png').convert('RGB'));n=sum(int(np.all(im[y+120:y+240,x:x+320]==[84,113,153],axis=2).sum()) for y in (0,240) for x in (0,320));self.assertTrue(n>80000 if v==OLD else n==0)
 def test_native_and_disc(self):
  r=json.loads((P/'report.json').read_text());e=(P/'ETD_MAT.EXE').read_bytes();self.assertEqual(e[:8],b'PS-X EXE');self.assertEqual(len(e)-2048,struct.unpack_from('<I',e,28)[0]);self.assertLess(int(r['linked_ram_high'],16),0x801e0000)
  b=(P/'ETD_PSX_M08.bin').read_bytes();self.assertEqual(len(b),300*2352);cooked=bytearray()
  for i in range(0,len(b),2352):
   s=bytearray(b[i:i+2352]);self.assertEqual(s[:12],b'\0'+b'\xff'*10+b'\0');self.assertEqual(s[15],2);self.assertEqual(s[16:20],s[20:24]);self.assertEqual(struct.unpack_from('<I',s,2072)[0],edc(s[16:2072]));s[12:16]=bytes(4);self.assertEqual(s[2076:2248],ecc(s[12:2076],86,24,2,86));self.assertEqual(s[2248:2352],ecc(s[12:2248],52,43,86,88));cooked.extend(s[24:2072])
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'test.iso';p.write_bytes(cooked)
   with ISO(p) as iso:self.assertEqual(iso.file('ETD_MAT.EXE'),e);self.assertIn(b'cdrom:\\ETD_MAT.EXE;1',iso.file('SYSTEM.CNF'))
  self.assertIn('TRACK 01 MODE2/2352',(P/'ETD_PSX_M08.cue').read_text())
