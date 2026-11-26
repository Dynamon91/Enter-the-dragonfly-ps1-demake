"""Compare the actual native codec (host-compiled) with every v0.36 pose."""
from pathlib import Path
import ctypes as C,json,struct,unittest,subprocess,random
import numpy as np
from disc16 import raw
from pack37 import encode
R=Path(__file__).resolve().parents[1];P=R/'build_m37/play';OLD=R/'build_m36/play'
class M37(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  (P/'host37.c').write_text('''typedef unsigned short u16;typedef signed short s16;typedef unsigned int u32;
#define NV 1157
#include "rig37_data.h"
#include "rig37_decode.h"
#include "questpose37.h"
const short* rig37_host(int frame){rig_seek(&rig_current,frame);return rig_current.frame==frame&&frame>=0?rig_current.words:0;}
const short* old37_host(int frame,int from,int blend){rig_prepare(frame,from,blend);return rig_previous.frame==from?rig_previous.words:0;}
const signed char* quest37_host(int id,int frame,int nv){return qpose37(id,frame,nv);}
int test16(const unsigned char*b,int size,short*out,int n,int add){return decode37_s16(b,b+size,out,n,add);}
int test8(const unsigned char*b,int size,signed char*out,int n){return decode37_s8(b,b+size,out,n);}
''')
  subprocess.run(['clang','-shared','-fPIC','-O2','-I',str(P),'-I',str(R/'src'),str(P/'host37.c'),'-o',str(P/'host37.so')],check=True)
  L=cls.L=C.CDLL(str(P/'host37.so'));L.rig37_host.restype=C.POINTER(C.c_int16);L.old37_host.restype=C.POINTER(C.c_int16);L.quest37_host.restype=C.POINTER(C.c_int8)
  L.test16.argtypes=[C.c_void_p,C.c_int,C.POINTER(C.c_int16),C.c_int,C.c_int];L.test8.argtypes=[C.c_void_p,C.c_int,C.POINTER(C.c_int8),C.c_int]
  cls.rig=np.load(R/'build_m11/play/rig.npz')['matrices'].reshape(245,516);cls.poses=np.load(R/'assets_m36/poses.npz')
 def test_all_rig_frames(self):
  for f in range(245):np.testing.assert_array_equal(np.ctypeslib.as_array(self.L.rig37_host(f),shape=(516,)),self.rig[f])
 def test_random_seek_and_blend(self):
  rng=random.Random(37)
  for i in range(1200):
   f,prev=rng.randrange(245),rng.randrange(245);self.L.rig37_host(prev);p=self.L.old37_host(f,prev,2);np.testing.assert_array_equal(np.ctypeslib.as_array(p,shape=(516,)),self.rig[prev]);np.testing.assert_array_equal(np.ctypeslib.as_array(self.L.rig37_host(f),shape=(516,)),self.rig[f])
  self.assertFalse(self.L.rig37_host(-1));self.assertFalse(self.L.rig37_host(245));np.testing.assert_array_equal(np.ctypeslib.as_array(self.L.rig37_host(244),shape=(516,)),self.rig[244])
 def test_all_npc_poses_and_parity_cache(self):
  for i in range(3):
   d=self.poses[f'delta{i}'];n=d.shape[1];base=np.load(R/'assets_m35/questmodels.npz')[f'v{i}'];frames=self.poses[f'frames{i}']
   for f in list(range(12))+[5,0,11,6,0,1,0,1]:
    nxt=(f//6)*6+(f+1)%6;p=self.L.quest37_host(i,f,n);q=self.L.quest37_host(i,nxt,n);self.assertTrue(p and q)
    np.testing.assert_array_equal(np.ctypeslib.as_array(p,shape=(n*3,)).reshape(n,3),d[f]);np.testing.assert_array_equal(np.ctypeslib.as_array(p,shape=(n*3,)).reshape(n,3).astype(np.int16)+base,frames[f]);np.testing.assert_array_equal(np.ctypeslib.as_array(q,shape=(n*3,)).reshape(n,3),d[nxt])
   self.assertFalse(self.L.quest37_host(i,0,n-1));self.assertFalse(self.L.quest37_host(i,12,n))
 def test_bounded_codec(self):
  v=[0,0,0,0,-8192,8191,4096,-4096,0,-127,127,1,7];data=encode(v);out=(C.c_int16*len(v))();self.assertTrue(self.L.test16(data,len(data),out,len(v),0));self.assertEqual(list(out),v)
  for k in range(len(data)):self.assertFalse(self.L.test16(data,k,out,len(v),0))
  self.assertFalse(self.L.test16(data+b'\x00',len(data)+1,out,len(v),0));small=(C.c_int8*len(v))();self.assertFalse(self.L.test8(data,len(data),small,len(v)))
  v=[-128,127,0,1,-5];data=encode(v);small=(C.c_int8*len(v))();self.assertTrue(self.L.test8(data,len(data),small,len(v)));self.assertEqual(list(small),v);self.assertFalse(self.L.test8(data[:-1],len(data)-1,small,len(v)))
 def test_native_memory_and_wiring(self):
  n=json.loads((P/'report37.json').read_text());o=json.loads((OLD/'report36.json').read_text());self.assertGreaterEqual(o['linked_ram_from_load']-n['linked_ram_from_load'],64*1024);self.assertGreater(n['headroom_to_stack_region'],96*1024)
  s=(P/'play37.c').read_text();self.assertIn('#include "rig37.h"',s);self.assertIn('d0=qpose37(id,f0,m->nv)',s);self.assertNotIn('qdelta36[id]',s)
  self.assertEqual((P/'BOOT32.DAT').read_bytes(),(OLD/'BOOT32.DAT').read_bytes());self.assertEqual((P/'QMOD35.DAT').read_bytes(),(OLD/'QMOD35.DAT').read_bytes())
 def test_disc_integrity(self):
  b=(P/'ETD_PSX_M37.bin').read_bytes();self.assertIn(b'ETD_PACK.EXE;1',b[21*2352+24:21*2352+2072]);root=b[20*2352+24:20*2352+2072];files={};i=0
  while root[i]:
   rr=root[i:i+root[i]];l,n=struct.unpack_from('<I',rr,2)[0],struct.unpack_from('<I',rr,10)[0];files[rr[33:33+rr[32]].decode()]=b''.join(b[j*2352+24:j*2352+2072] for j in range(l,l+(n+2047)//2048))[:n];i+=len(rr)
  for n in ('QMOD35.DAT','BOOT32.DAT','DOJOSECT.IDX','DOJOSECT.DAT','ETD_TALK.EXE'):self.assertEqual(files[n+';1'],(OLD/n).read_bytes())
  self.assertEqual(files['ETD_PACK.EXE;1'],(P/'ETD_PACK.EXE').read_bytes())
  for i in range(len(b)//2352):s=b[i*2352:(i+1)*2352];self.assertEqual(s,raw(i,s[24:2072]))
if __name__=='__main__':unittest.main()
