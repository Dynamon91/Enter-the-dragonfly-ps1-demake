import sys,unittest,json,struct,math,hashlib
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];P=R/'build_m28/play';A=R/'assets_m28';sys.path.insert(0,str(R/'tools'))
from preview_sky28 import Sky
from preview_scene10 import array
from disc16 import raw
class M28(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.z=np.load(A/'sky.npz');cls.sky=Sky()
 def test_recovery(self):
  r=json.loads((A/'sky_report.json').read_text());self.assertEqual(len(r['meshes']),14);self.assertEqual(sum(m['triangles'] for m in r['meshes']),1080);self.assertEqual(sum(m['packets'] for m in r['meshes']),59);self.assertEqual([t['group'] for t in r['textures']],[122,38,134,335]);self.assertEqual(np.bincount(self.z['layers']).tolist(),[228,36,2,814]);self.assertTrue(np.all(np.abs(self.z['triangles'].astype(int))<8192))
 def test_palette_modes(self):
  p=self.z['palettes'];ix=self.z['pixels'];self.assertEqual(p.shape,(4,256));self.assertEqual(ix.shape,(4,64,64));self.assertTrue(np.all(p[0,ix[0]]!=0));self.assertTrue(np.all(p[0,ix[0]]<32768));self.assertTrue(np.all(p[3,ix[3]]>=32768));self.assertTrue(np.all((p[1:3]==0)|(p[1:3]>=32768)))
 def test_vram(self):
  v=np.zeros((512,1024),np.uint8)
  def reserve(x,y,w,h):
   self.assertTrue(0<=x and x+w<=1024 and 0<=y and y+h<=512);self.assertFalse(v[y:y+h,x:x+w].any(),(x,y,w,h));v[y:y+h,x:x+w]=1
  reserve(0,0,320,240);reserve(0,256,320,240)
  for name,var in [('scene.h','upload'),('firetex11.h','fireupload')]:
   a=array((P/name).read_text(),var);i=0
   while i<len(a):
    self.assertEqual(a[i],0xa0000000);x,y=int(a[i+1])&65535,int(a[i+1])>>16;w,h=int(a[i+2])&65535,int(a[i+2])>>16;reserve(x,y,w,h);i+=3+w*h//2
  for slot in range(64):reserve(768,16+slot,256,1);reserve(320+128*(slot//16)+32*(slot%4),256+64*(slot//4%4),32,64)
  for layer in range(4):reserve(768,4+layer,256,1);reserve(832+32*layer,256,32,64)
 def test_gpu_packets_all_yaws(self):
  counts=[]
  for yaw in range(64):
   pp=list(self.sky.packets(yaw));counts.append(len(pp));self.assertTrue(any(p[0]==0 for p in pp));self.assertEqual([p[0] for p in pp],sorted(p[0] for p in pp))
   for l,xy,uv,p in pp:
    self.assertTrue(np.all(xy>=-2));self.assertTrue(np.all(xy<=[322,242]));self.assertTrue(np.all(uv>=0));self.assertTrue(np.all(uv<=255));self.assertEqual(int(p[3])>>16,48|((4+l)<<6));self.assertEqual(int(p[5])>>16,13|16|128|(32 if l in (1,2) else 0))
  (P/'sky_packet_report.json').write_text(json.dumps(dict(minimum=min(counts),maximum=max(counts),mean=sum(counts)/64,views=64)));print('sky packets',min(counts),max(counts),sum(counts)/64)
 def test_coverage(self):
  counts=[]
  for yaw in range(0,64,8):
   _,c=self.sky.render(yaw);counts.append(int(c.sum()));self.assertGreater(c.mean(),.98)
  print('opaque background coverage',min(counts),'/76800')
 def test_preserved_gameplay(self):
  old=R/'build_m27/play';
  for n in ('DOJOSECT.DAT','DOJOSECT.IDX','cache24.c','tex19.h','collect21.h','interact21.h','scene.h','rig11_data.h'):
   self.assertEqual((P/n).read_bytes(),(old/n).read_bytes())
  s=(P/'play28.c').read_text();self.assertIn('sky_draw28(sn,cs);for(int b=',s);self.assertIn('sky_upload28();status=',s)
 def test_disc(self):
  d=(P/'ETD_PSX_M28.bin').read_bytes();self.assertIn(b'ETD_SKY.EXE;1',d[21*2352+24:21*2352+2072]);self.assertIn(b'ETD_WIDE.EXE;1',d[20*2352+24:20*2352+2072]);self.assertIn(b'ETD_POOL.EXE;1',d[20*2352+24:20*2352+2072]);self.assertGreater(json.loads((P/'report.json').read_text())['headroom_to_stack_region'],32768)
  for i in range(len(d)//2352):s=d[i*2352:(i+1)*2352];self.assertEqual(s,raw(i,s[24:2072]))
  root=d[20*2352+24:20*2352+2072];pos=0;files={}
  while root[pos]:
   n=root[pos];r=root[pos:pos+n];name=r[33:33+r[32]];lba,size=struct.unpack_from('<I',r,2)[0],struct.unpack_from('<I',r,10)[0];files[name]=b''.join(d[i*2352+24:i*2352+2072] for i in range(lba,lba+(size+2047)//2048))[:size];pos+=n
  expected={'ETD_SKY.EXE':P/'ETD_SKY.EXE','ETD_WIDE.EXE':R/'build_m27/play/ETD_WIDE.EXE','ETD_POOL.EXE':R/'build_m24/play/ETD_POOL.EXE','DOJOSECT.DAT':P/'DOJOSECT.DAT','DOJOSECT.IDX':P/'DOJOSECT.IDX','DOJOTEX.DAT':R/'assets_m27/DOJOTEX.DAT','DOJOTEX.IDX':R/'assets_m27/DOJOTEX.IDX','HUBSECT.DAT':R/'assets_m16/HUBSECT.DAT','HUBSECT.IDX':R/'assets_m16/HUBSECT.IDX','HUBTEX.DAT':R/'assets_m20/HUBTEX.DAT','HUBTEX.IDX':R/'assets_m20/HUBTEX.IDX'}
  for name,path in expected.items():self.assertEqual(files[(name+';1').encode()],path.read_bytes())
if __name__=='__main__':unittest.main()
