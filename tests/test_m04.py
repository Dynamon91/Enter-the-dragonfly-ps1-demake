import json,struct,unittest,re
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'build_m04'
class MeshTests(unittest.TestCase):
 def test_packets(self):
  a=json.loads((B/'spyro/mesh_report.json').read_text())['shapes'];self.assertEqual(len(a),18);self.assertEqual(sum(x['packets'] for x in a),159);self.assertEqual(sum(x['strips'] for x in a),622);self.assertEqual(sum(x['vertices'] for x in a),4721);self.assertEqual(sum(x['triangles'] for x in a),3354);self.assertTrue(all(x['bounds_error']<.001 for x in a))
 def test_mesh(self):
  z=np.load(B/'spyro/spyro_rest.npz');v=z['vertices'];f=z['faces'];self.assertTrue(np.isfinite(v).all());self.assertTrue(np.isfinite(z['uv']).all());self.assertTrue(np.isfinite(z['normals']).all());self.assertGreaterEqual(f.min(),0);self.assertLess(f.max(),len(v));self.assertEqual(len(f),3280);self.assertEqual(len(z['uv']),len(v));self.assertEqual(len(z['part']),len(v))
 def test_native(self):
  for name,exe in [('view','ETD_SPYRO.EXE'),('lod','ETD_LOD.EXE')]:
   d=B/name;b=(d/exe).read_bytes();r=json.loads((d/'view_report.json').read_text());self.assertEqual(b[:8],b'PS-X EXE');pc,gp,addr,size=struct.unpack_from('<IIII',b,16);self.assertEqual(pc,addr);self.assertEqual(size,len(b)-2048);self.assertLess(addr+size,0x801e0000);self.assertIn(struct.pack('<I',0x4a180001),b);self.assertEqual(r['frames_host_checked'],64);self.assertGreater(r['depth_min'],128)
 def test_vram_packets(self):
  for folder in ['view','lod']:
   s=(B/folder/'scene.h').read_text();m=re.search(r'upload\[UPLOAD_WORDS\]=\{(.*?)\};',s,re.S);a=[int(x) for x in re.findall(r'(\d+)u',m.group(1))];pos=0;occupied=np.zeros((512,1024),dtype=bool);occupied[:240,:320]=True;occupied[256:496,:320]=True;count=0
   while pos<len(a):
    cmd,xy,wh=a[pos:pos+3];self.assertEqual(cmd,0xa0000000);x,y=xy&65535,xy>>16;w,h=wh&65535,wh>>16;self.assertLessEqual(x+w,1024);self.assertLessEqual(y+h,512);self.assertFalse(occupied[y:y+h,x:x+w].any());occupied[y:y+h,x:x+w]=True;pos+=3+(w*h+1)//2;count+=1
   self.assertEqual(pos,len(a));self.assertEqual(count,6)
 def test_lod(self):
  full=json.loads((B/'view/view_report.json').read_text());lod=json.loads((B/'lod/view_report.json').read_text());self.assertLess(lod['triangles'],full['triangles']);self.assertLess(lod['vertices'],full['vertices']);self.assertEqual(lod['texture_vram_bytes'],full['texture_vram_bytes'])
if __name__=='__main__':unittest.main()
