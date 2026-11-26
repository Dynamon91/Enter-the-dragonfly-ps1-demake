import json,struct,subprocess,tempfile,unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'build_m06/play';C=ROOT/'build_m06/collision'
class Milestone6(unittest.TestCase):
 def test_registry(self):
  r=json.loads((P/'texture_registry.json').read_text());self.assertEqual(len(r['entries']),540);self.assertEqual(len({x['offset'] for x in r['entries']}),540);self.assertTrue(all(x['size']>0 for x in r['entries']))
 def test_collision_candidates(self):
  r=json.loads((C/'collision_report.json').read_text());z=np.load(C/'collision.npz');self.assertEqual(r['polygon_candidates'],3776);self.assertEqual(z['faces'].shape,(6195,3));self.assertTrue(np.isfinite(z['vertices']).all());self.assertLess(z['faces'].max(),len(z['vertices']))
 def test_corroborated_floor(self):
  z=np.load(P/'farm06.npz');old=np.load(P/'farm.npz')['floor'];f=z['floor'];good=f!=32767;self.assertEqual(int(good.sum()),227);self.assertTrue(np.all(old[good]!=32767));self.assertLess(np.abs(f[good].astype(int)-old[good].astype(int)).max(),120);x,y,zz=z['spawn'];self.assertEqual(f[(zz+4096)//128,(x+4096)//128],y);self.assertGreaterEqual(y,0)
 def test_texture_geometry(self):
  z=np.load(P/'farm06.npz');self.assertEqual(z['faces'].shape,(2211,3));self.assertEqual(z['uv'].shape,(2211,3,2));self.assertLessEqual(z['uv'].max(),255);self.assertGreaterEqual(z['uv'].min(),0);self.assertLess(z['faces'].max(),len(z['vertices']));self.assertEqual(z['textures'].shape,(17,64,64));self.assertLess(z['texture_id'].max(),17)
 def test_vram(self):
  r=json.loads((P/'report.json').read_text());rect=[(0,0,320,240),(0,256,320,240)];rect.extend(x[k] for x in r['bindings'] for k in ('vram','clut'))
  for i,(x,y,w,h) in enumerate(rect):
   self.assertTrue(0<=x<x+w<=1024 and 0<=y<y+h<=512)
   for a,b,c,d in rect[:i]:self.assertFalse(x<a+c and x+w>a and y<b+d and y+h>b)
  self.assertTrue(all(x['binding'].startswith('visual candidate') for x in r['bindings']))
 def test_native(self):
  b=(P/'ETD_FARM.EXE').read_bytes();self.assertEqual(b[:8],b'PS-X EXE');pc,gp,addr,n=struct.unpack_from('<IIII',b,16);self.assertEqual((pc,addr),(0x80010000,0x80010000));self.assertEqual(n,len(b)-2048);self.assertEqual(n%2048,0);self.assertLess(n,2*1024*1024-65536)
 def test_movement(self):
  c='''#include <assert.h>\ntypedef unsigned int u32;typedef unsigned short u16;typedef signed short s16;\n#include "world.h"\n#include "player06.h"\nint main(void){Player p;reset_player(&p);int y=p.y,x=p.x,z=p.z;assert(p.grounded&&floor_at(x,z)==y);step_player(&p,PAD_UP,0,0);assert(p.z>z);reset_player(&p);step_player(&p,PAD_CROSS,0,0);assert(p.y<y&&!p.grounded);for(int i=0;i<100;i++)step_player(&p,0,0,0);assert(p.y==y&&p.grounded);reset_player(&p);step_player(&p,PAD_CROSS,0,0);for(int i=0;i<20;i++)step_player(&p,PAD_CROSS,0,0);assert(p.vy<=8&&!p.grounded);reset_player(&p);step_player(&p,PAD_R1,0,0);assert(p.camera==1);for(int i=0;i<500;i++){step_player(&p,PAD_UP|PAD_SQUARE,0,0);assert(floor_at(p.x,p.z)!=32767);}step_player(&p,PAD_START,0,0);assert(p.x==x&&p.z==z&&p.camera==0);assert(floor_at(5000,0)==32767);return 0;}'''
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);(d/'t.c').write_text(c);subprocess.run(['clang','-I',str(P),'-I',str(ROOT/'src'),str(d/'t.c'),'-o',str(d/'t')],check=True);subprocess.run([str(d/'t')],check=True)
if __name__=='__main__':unittest.main()
