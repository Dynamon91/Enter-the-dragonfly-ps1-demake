import unittest,struct,json,subprocess,ctypes as C,sys
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];P=R/'build_m30/play';A=R/'assets_m30';sys.path.insert(0,str(R/'tools'))
from disc16 import raw
from preview_scene10 import array
class M30(unittest.TestCase):
 def test_source_curves(self):
  z=np.load(A/'curves.npz');r=json.loads((A/'report.json').read_text());self.assertEqual(len(r['clips']),10);self.assertEqual(sum(c['keys'] for c in r['clips']),5054);self.assertEqual(len(set(c['record'] for c in r['clips'])),10)
  for c in r['clips']:
   a=z[c['name']];o=z[c['name']+'_offsets'];self.assertEqual(a.shape,(4,c['keys']));self.assertEqual(len(o),102)
   for i,m in enumerate(c['curves']):
    t=a[0,o[i]:o[i+1]];self.assertTrue(np.all(np.diff(t)>0));self.assertAlmostEqual(float(t[0]),m['start'],4);self.assertAlmostEqual(float(t[-1]),m['end'],4)
 def test_mesh_and_rig(self):
  z=np.load(A/'ninja.npz');self.assertEqual(z['frames'].shape,(19,323,3));self.assertEqual(z['faces'].shape,(596,3));self.assertTrue(np.all(z['faces']<323));self.assertEqual(int((z['materials']==1).sum()),76);self.assertTrue(np.allclose(z['weights'].sum(1),1));self.assertTrue(np.all(z['parents'][1:]<np.arange(1,27)));self.assertTrue(np.all(z['uv']<64));self.assertGreater(np.abs(z['frames'][4]-z['frames'][1]).sum(),1000);self.assertGreater(np.abs(z['frames'][15]-z['frames'][13]).sum(),100)
 def test_compression_native_c(self):
  f=P/'pose30_host.c';f.write_text('typedef short s16; typedef unsigned short u16; typedef unsigned char U8;\n#include "ninja30.h"\nvoid unpack(int phase,s16*out){int ep=ninja_offsets30[phase-1];for(int l=0;l<NINJA_NV30;l++)for(int j=0;j<3;j++){int d=ninja_delta30[phase-1][l][j];if(d==-128)d=ninja_escape30[ep++];out[l*3+j]=ninja_base30[l][j]+d;}}\n');subprocess.run(['clang','-O2','-shared','-fPIC',str(f),'-o',str(P/'pose30_host.so')],check=True);L=C.CDLL(str(P/'pose30_host.so'));L.unpack.argtypes=[C.c_int,C.POINTER(C.c_short)];z=np.load(A/'ninja.npz');a=np.empty((323,3),dtype=np.int16)
  for i in range(1,19):L.unpack(i,a.ctypes.data_as(C.POINTER(C.c_short)));np.testing.assert_array_equal(a,z['frames'][i])
 def test_vram(self):
  rects=[(0,0,320,240),(0,256,320,240),(320,256,512,256),(768,16,256,64),(832,256,128,64),(768,4,256,4)]
  for f,n in [('scene.h','upload'),('firetex11.h','fireupload')]:
   a=array((P/f).read_text(),n);i=0
   while i<len(a):self.assertEqual(a[i],0xa0000000);xy=int(a[i+1]);wh=int(a[i+2]);w,h=wh&65535,wh>>16;rects.append((xy&65535,xy>>16,w,h));i+=3+(w*h+1)//2
  for a in [(832,320,32,64),(864,320,32,64),(768,8,256,1),(768,9,256,1)]:
   x,y,w,h=a;self.assertLessEqual(x+w,1024);self.assertLessEqual(y+h,512)
   for xx,yy,ww,hh in rects:self.assertTrue(x+w<=xx or xx+ww<=x or y+h<=yy or yy+hh<=y,(a,(xx,yy,ww,hh)))
   rects.append(a)
 def test_unchanged_assets(self):
  for n in ('DOJOSECT.DAT','DOJOSECT.IDX','enemyids29.h','interact21.h','objectids21.h','skydata28.h'):
   self.assertEqual((P/n).read_bytes(),(R/'build_m29/play'/n).read_bytes())
 def test_disc(self):
  d=(P/'ETD_PSX_M30.bin').read_bytes();self.assertIn(b'ETD_EYES.EXE;1',d[21*2352+24:21*2352+2072]);self.assertIn(b'ETD_NINJ.EXE;1',d[20*2352+24:20*2352+2072]);self.assertGreater(json.loads((P/'report30.json').read_text())['headroom_to_stack_region'],65536)
  for i in range(len(d)//2352):s=d[i*2352:(i+1)*2352];self.assertEqual(s,raw(i,s[24:2072]))
  root=d[20*2352+24:20*2352+2072];pos=0;files={}
  while root[pos]:
   n=root[pos];r=root[pos:pos+n];name=r[33:33+r[32]];lba,size=struct.unpack_from('<I',r,2)[0],struct.unpack_from('<I',r,10)[0];files[name]=b''.join(d[i*2352+24:i*2352+2072] for i in range(lba,lba+(size+2047)//2048))[:size];pos+=n
  for n in ('DOJOSECT.DAT','DOJOSECT.IDX','ETD_EYES.EXE'):self.assertEqual(files[(n+';1').encode()],(P/n).read_bytes())
if __name__=='__main__':unittest.main()
