"""Validate model data, boot upload address map, preserved quest state and native disc."""
from pathlib import Path
import ctypes as C, json,struct,unittest,subprocess,zlib
import numpy as np
from test_m28 import array
from test_m34 import M34
from disc16 import raw
R=Path(__file__).resolve().parents[1];P=R/'build_m35/play';A=R/'assets_m35';OLD=R/'build_m34/play'
class M35(unittest.TestCase):
 def test_source_mapping(self):
  r=json.loads((A/'report.json').read_text());z=np.load(A/'questmodels.npz');self.assertEqual([(m['name'],m['metadata'],m['geometry']) for m in r['models']],[('Tootie',97,353),('Huey',553,117),('Dooie',1022,105),('Kite',419,311)]);self.assertEqual(len(r['textures']),11);self.assertEqual([p['resource'] for p in r['prop_refs']],['KITE.MRB']*3);self.assertEqual(len({m['group'] for m in r['textures']}),11)
  for i,m in enumerate(r['models']):
   v,f,u,g=(z[k+str(i)] for k in 'vfum');self.assertEqual(len(v),m['vertices']);self.assertEqual(len(f),m['triangles']);self.assertTrue(np.all(f<len(v)));self.assertEqual(u.shape,(len(f),3,2));self.assertTrue(np.all(g<11));self.assertGreater(m['source_triangles'],m['triangles']);self.assertTrue(np.all(np.any(v[f[:,0]]!=v[f[:,1]],axis=1)))
   if i<3:self.assertEqual(sum('eyeball' in p['name'] for p in m['parts']),2)
  self.assertEqual(z['palettes'].shape,(11,256));self.assertTrue(np.all(z['palettes']!=0));self.assertEqual(z['pixels'].shape,(11,64,64));self.assertEqual(sum(m['triangles'] for m in r['models']),3571)
 def test_vram(self):
  v=np.zeros((512,1024),np.uint8)
  def reserve(x,y,w,h):
   self.assertTrue(x>=0 and y>=0 and x+w<=1024 and y+h<=512);self.assertFalse(v[y:y+h,x:x+w].any(),(x,y,w,h));v[y:y+h,x:x+w]=1
  for q in [(0,0,320,240),(0,256,320,240),(320,256,512,256),(768,16,256,64),(832,256,128,64),(768,4,256,4),(832,320,64,64),(768,8,256,2)]:reserve(*q)
  for name,var in [('scene.h','upload'),('firetex11.h','fireupload')]:
   a=array((R/'build_m31/play'/name).read_text(),var);i=0
   while i<len(a):
    x,y=int(a[i+1])&65535,int(a[i+1])>>16;w,h=int(a[i+2])&65535,int(a[i+2])>>16;reserve(x,y,w,h);i+=3+w*h//2
  for m in range(11):
   col,row=m%6,m//6;x,y=832+col*32,384+row*64;reserve(x,y,32,64);reserve(768,80+m,256,1)
   page=13+2*(col//4);self.assertEqual(page*64+(col%4)*32,x);self.assertEqual(256+(2+row)*64,y)
 def test_bank(self):
  z=np.load(A/'questmodels.npz');d=(P/'QMOD35.DAT').read_bytes();self.assertEqual(d,z['palettes'].astype('<u2').tobytes()+z['pixels'].tobytes());self.assertEqual(len(d),50688)
  import re
  h=(P/'questmodels35.h').read_text();const='\n'.join(l for l in h.splitlines() if l.startswith(('#define Q35_BYTES','#define Q35_PAD','#define Q35_CRC')));self.assertIn(f'0x{zlib.crc32(d):08x}',const);f=P/'hostbank35.c';f.write_text('typedef unsigned int U32;typedef unsigned char U8;typedef int (*Read18)(void*,U32,U32,U8*);\n#include "startup32.h"\n'+const+'\n#include "questbank35.h"\nint load35(U8*p,U32 cap,U32 lba,U32 size,Read18 rd){return quest_load35(p,cap,lba,size,rd,0);}\n');subprocess.run(['clang','-shared','-fPIC','-O2','-I',str(R/'src'),'-I',str(P),str(f),'-o',str(P/'hostbank35.so')],check=True);L=C.CDLL(str(P/'hostbank35.so'));CB=C.CFUNCTYPE(C.c_int,C.c_void_p,C.c_uint,C.c_uint,C.c_void_p);L.load35.argtypes=[C.c_void_p,C.c_uint,C.c_uint,C.c_uint,CB];buf=C.create_string_buffer(51200);calls=[]
  def read(ctx,lba,n,p):calls.append((lba,n));C.memmove(p,d.ljust(51200,b'\0'),n*2048);return 1
  cb=CB(read);self.assertTrue(L.load35(buf,len(buf),0,len(d),cb));self.assertEqual(calls,[(0,25)]);self.assertEqual(buf.raw[:len(d)],d);self.assertFalse(L.load35(buf,len(buf)-1,0,len(d),cb));self.assertFalse(L.load35(buf,len(buf),0,len(d)-1,cb));bad=CB(lambda ctx,lba,n,p:(C.memset(p,0,n*2048),1)[1]);self.assertFalse(L.load35(buf,len(buf),0,len(d),bad));fail=CB(lambda *a:0);self.assertFalse(L.load35(buf,len(buf),0,len(d),fail))
 def test_disc(self):
  d=(P/'ETD_PSX_M35.bin').read_bytes();self.assertIn(b'ETD_NPCS.EXE;1',d[21*2352+24:21*2352+2072]);root=d[20*2352+24:20*2352+2072];files={};i=0
  while root[i]:
   rr=root[i:i+root[i]];l,n=struct.unpack_from('<I',rr,2)[0],struct.unpack_from('<I',rr,10)[0];files[rr[33:33+rr[32]].decode()]=b''.join(d[j*2352+24:j*2352+2072] for j in range(l,l+(n+2047)//2048))[:n];i+=len(rr)
  for n in ('BOOT32.DAT','DOJOSECT.DAT','DOJOSECT.IDX','ETD_QEST.EXE'):self.assertEqual(files[n+';1'],(OLD/n).read_bytes())
  for n in ('QMOD35.DAT','ETD_NPCS.EXE'):self.assertEqual(files[n+';1'],(P/n).read_bytes())
  for i in range(len(d)//2352):s=d[i*2352:(i+1)*2352];self.assertEqual(s,raw(i,s[24:2072]))
  self.assertGreater(json.loads((P/'report35.json').read_text())['headroom_to_stack_region'],90000)
 def test_runtime_wiring(self):
  s=(P/'play35.c').read_text();self.assertIn('quest_upload35((U8*)cache.arena);status=reset18',s);self.assertIn('quest_step34(&quest34',s);self.assertIn('renderquest35(p,cx,cy,cz,sn,cs)',s);self.assertNotIn('marker34(',s);self.assertIn('qidle35[i][j]',s);self.assertIn('quest_pos34(&quest34,i,v)',s)
if __name__=='__main__':unittest.main()
