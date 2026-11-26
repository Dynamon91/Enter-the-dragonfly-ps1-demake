import json,subprocess,tempfile,unittest,struct
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];H=ROOT/'build_m05/hub';P=ROOT/'build_m05/play'
class Milestone5(unittest.TestCase):
 def test_exact_matches(self):
  r=json.loads((H/'hub_report.json').read_text());self.assertEqual(r['matched'],465);self.assertFalse(r['unmatched']);self.assertTrue(all(m['bounds_error']<.01 for m in r['meshes']));self.assertEqual(len({m['record'] for m in r['meshes']}),9)
 def test_hub_arrays(self):
  z=np.load(H/'hub.npz');self.assertEqual(z['faces'].shape,(70411,3));self.assertEqual(z['vertices'].shape,(103066,3));self.assertLess(z['faces'].max(),len(z['vertices']));self.assertTrue(np.isfinite(z['uv']).all())
 def test_sector(self):
  z=np.load(P/'farm.npz');self.assertLess(z['faces'].max(),len(z['vertices']));self.assertLess(np.abs(z['vertices']).max(),32768);self.assertEqual(z['floor'].shape,(65,65));x,y,zz=z['spawn'];self.assertEqual(z['floor'][(zz+4096)//128,(x+4096)//128],y)
 def test_native_header(self):
  b=(P/'ETD_PLAY.EXE').read_bytes();self.assertEqual(b[:8],b'PS-X EXE');pc,gp,addr,n=struct.unpack_from('<IIII',b,16);self.assertEqual(pc,0x80010000);self.assertEqual(addr,pc);self.assertEqual(n,len(b)-2048);self.assertEqual(n%2048,0);self.assertLess(n,2*1024*1024-65536)
 def test_player_host_logic(self):
  # Actual C movement logic compiled and run against generated floor data, no emulator.
  c='''#include <assert.h>\ntypedef unsigned int u32;typedef unsigned short u16;typedef signed short s16;\n#include "world.h"\n#include "player.h"\nint main(void){Player p;reset_player(&p);assert(p.grounded);int x=p.x,z=p.z,y=p.y;step_player(&p,PAD_UP,0,0);assert(p.z>z);reset_player(&p);step_player(&p,PAD_SQUARE|PAD_UP,0,0);assert(p.z-z==38);reset_player(&p);step_player(&p,PAD_CROSS,0,0);assert(p.y<y&&!p.grounded);for(int i=0;i<100;i++)step_player(&p,0,0,0);assert(p.y==y&&p.grounded);reset_player(&p);step_player(&p,PAD_CROSS,0,0);for(int i=0;i<20;i++)step_player(&p,PAD_CROSS,0,0);assert(p.vy<=8&&!p.grounded);reset_player(&p);step_player(&p,PAD_R1,0,0);assert(p.camera==1);step_player(&p,PAD_START,0,0);assert(p.x==x&&p.z==z&&p.camera==0);assert(floor_at(5000,0)==32767);return 0;}'''
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);(d/'t.c').write_text(c);subprocess.run(['clang','-I',str(P),'-I',str(ROOT/'src'),str(d/'t.c'),'-o',str(d/'t')],check=True);subprocess.run([str(d/'t')],check=True)
if __name__=='__main__':unittest.main()
