import unittest, json, struct, sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from recover import pxt_groups, PX, collision_mesh, shape_metadata, vertex_packets
class RecoveryTests(unittest.TestCase):
    def test_pxt_4bit_fixture(self):
        def header(w,h):
            b=bytearray(96);b[:16]=PX;struct.pack_into('<II',b,48,w,h);return b
        blob=bytes(16)+header(8,2)+bytes(range(64))+header(4,2)+bytes([0x10,0x32,0x54,0x76])
        groups=list(pxt_groups(blob));self.assertEqual(len(groups),1);self.assertEqual(groups[0][2][0][2].ravel().tolist(),list(range(8)))
    def test_pxt_bad_header(self):
        with self.assertRaises(ValueError):list(pxt_groups(bytes(128)))
    def test_geometry_report(self):
        b=ROOT/'build_m03/recovered';r=json.loads((b/'recovery.json').read_text());self.assertEqual(len(r['shapes']),18);self.assertEqual(sum(x['packets'] for x in r['shapes']),159)
        self.assertTrue(all(x['packets']==x['observed_packets'] for x in r['shapes']));self.assertEqual(sum(x['vertex_samples'] for x in r['shapes']),5088)
        self.assertEqual(r['converted_texture_groups'],536);self.assertEqual(r['texture_images'],1839)
        for t in r['texture_manifest']:
            i=t['id'];clut=b/'textures'/f'{i:03}.clut';idx=b/'textures'/f'{i:03}.idx';self.assertEqual(clut.stat().st_size,2*(1<<t['bpp']));self.assertEqual(idx.stat().st_size,t['width']*t['height']*t['bpp']//8);self.assertLessEqual(max(t['width'],t['height']),256)
    def test_collision_indices(self):
        a=np.load(ROOT/'build_m03/recovered/boat_collision.npz');self.assertEqual(a['vertices'].shape,(326,3));self.assertEqual(a['faces'].shape,(612,3));self.assertLess(a['faces'].max(),len(a['vertices']))
    def test_executable(self):
        d=ROOT/'build_m03/dynamic';b=(d/'ETD_GTE.EXE').read_bytes();r=json.loads((d/'dynamic_report.json').read_text());self.assertEqual(b[:8],b'PS-X EXE');pc,gp,addr,size=struct.unpack_from('<IIII',b,16);self.assertEqual(pc,addr);self.assertEqual(size,len(b)-2048);self.assertEqual(size%2048,0);self.assertLess(addr+size,0x801e0000);self.assertIn(struct.pack('<I',0x4a180001),b);self.assertEqual(r['frames_host_checked'],64);self.assertGreater(r['depth_min'],260//2);self.assertLessEqual(r['framebuffer_bytes'],1024*1024)
if __name__=='__main__':unittest.main()
