import ctypes as C,json,struct,unittest,sys
from pathlib import Path
import numpy as np
import test_m22 as old
from test_m21 import CB,Inter
R=Path(__file__).resolve().parents[1];P=R/'build_m23/play';A=R/'assets_m16'
class M23(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  L=cls.L=C.CDLL(str(P/'interact23_host.so'));cls.idx=(A/'HUBSECT.IDX').read_bytes();cls.dat=(A/'HUBSECT.DAT').read_bytes();cls.man=json.loads((A/'sector_manifest.json').read_text());cls.b=cls.man['blocks'];cls.sizes=[(struct.unpack_from('<I',cls.idx,16+i*60+8)[0]+2047)//2048*2048 for i in range(174)];cls.good=CB(lambda ctx,lba,n,p:(C.memmove(p,cls.dat[lba*2048:(lba+n)*2048],n*2048),1)[1]);L.cache18_init.argtypes=[C.c_void_p];L.cache18_select.argtypes=[C.c_char_p,C.c_uint32,C.c_int,C.c_int,C.POINTER(C.c_int)];L.cache18_update.argtypes=[C.c_void_p,C.c_char_p,C.c_uint32,C.c_uint32,C.c_int,C.c_int,CB,C.c_void_p];L.cache23_begin.argtypes=[C.c_void_p,C.c_char_p,C.c_uint32,C.c_int,C.c_int];L.cache23_tick.argtypes=[C.c_void_p,C.c_char_p,C.c_uint32,C.c_uint32,CB,C.c_void_p];L.cache23_commit.argtypes=[C.c_void_p,C.c_int,C.c_int];L.cache23_move.argtypes=[C.c_void_p,C.c_char_p,C.c_uint32,C.c_uint32,C.c_int,C.c_int,C.c_int,C.c_int,CB,C.c_void_p];L.cache23_cancel.argtypes=[C.c_void_p];L.cache18_floor.argtypes=[C.c_void_p,C.c_int,C.c_int,C.c_int,C.c_int];L.cache22_size.restype=C.c_uint32
  for n in ('cache22_count','cache22_bytes','cache22_copied','cache22_reads','cache23_pending','cache23_ticks','cache23_cancels'):getattr(L,n).argtypes=[C.c_void_p]
  L.cache22_id.argtypes=[C.c_void_p,C.c_int];L.cache22_data.argtypes=[C.c_void_p,C.c_int];L.cache22_data.restype=C.c_void_p;L.step21.argtypes=[C.POINTER(Inter),C.c_void_p]+[C.c_int]*12;L.reset21.argtypes=[C.POINTER(Inter)]
 def new(self):w=C.create_string_buffer(self.L.cache22_size());self.L.cache18_init(w);return w
 def load(self,w,x,z,cb=None):return self.L.cache18_update(w,self.idx,len(self.idx),len(self.dat)//2048,x,z,cb or self.good,None)
 def ids(self,w):return [self.L.cache22_id(w,i) for i in range(self.L.cache22_count(w))]
 def snapshot(self,w):return [(i,C.string_at(self.L.cache22_data(w,j),self.sizes[i])) for j,i in enumerate(self.ids(w))]
 def begin(self,w,x,z):return self.L.cache23_begin(w,self.idx,len(self.idx),x,z)
 def tick(self,w,cb=None):return self.L.cache23_tick(w,self.idx,len(self.idx),len(self.dat)//2048,cb or self.good,None)
 def move(self,w,x,z,nx,nz):return self.L.cache23_move(w,self.idx,len(self.idx),len(self.dat)//2048,x,z,nx,nz,self.good,None)
 def test_exhaustive(self):
  w=self.new();oldcov=json.loads((R/'build_m22/play/coverage22.json').read_text());lo=np.array([b['bounds'][0] for b in self.b]);hi=np.array([b['bounds'][1] for b in self.b]);seen={}
  for x in range(lo[:,0].min()//512*512-2048,hi[:,0].max()+2048,512):
   for z in range(lo[:,2].min()//512*512-2048,hi[:,2].max()+2048,512):
    a=x+256;c=z+256;ids=tuple(int(i) for i in np.where((lo[:,0]<=a+1536)&(hi[:,0]>=a-1536)&(lo[:,2]<=c+1536)&(hi[:,2]>=c-1536))[0]);
    if ids:seen.setdefault(ids,(a,c))
  self.assertEqual(len(seen),oldcov['sets'])
  for ids,(x,z) in seen.items():
   self.assertTrue(self.load(w,x,z));self.assertEqual(tuple(self.ids(w)),ids)
   for j,i in enumerate(ids):p=self.b[i]['lba']*2048;self.assertEqual(C.string_at(self.L.cache22_data(w,j),self.sizes[i]),self.dat[p:p+self.sizes[i]])
 def test_incremental_atomic(self):
  w=self.new();self.assertTrue(self.load(w,36848,-1200));before=self.snapshot(w);self.assertTrue(self.begin(w,-1280,-1280));self.assertEqual(self.L.cache23_pending(w),16);self.assertFalse(self.L.cache23_commit(w,-1280,-1280))
  for k in range(16):
   r=self.L.cache22_reads(w);t=self.L.cache23_ticks(w);self.assertEqual(self.tick(w),int(k==15));self.assertLessEqual(self.L.cache22_reads(w)-r,1);self.assertEqual(self.L.cache23_ticks(w)-t,1);self.assertEqual(self.snapshot(w),before)
  self.assertFalse(self.L.cache23_commit(w,-768,-1280));self.assertTrue(self.L.cache23_commit(w,-1280,-1280));self.assertEqual(len(self.ids(w)),16);self.assertEqual(self.L.cache22_bytes(w),542720)
 def test_cancel_and_fault(self):
  w=self.new();self.assertTrue(self.load(w,36848,-1200));before=self.snapshot(w);self.assertTrue(self.begin(w,-1280,-1280));self.assertEqual(self.tick(w),0);self.assertTrue(self.begin(w,36848,-1200));self.assertEqual(self.L.cache23_cancels(w),1);self.assertEqual(self.tick(w),1);self.assertTrue(self.L.cache23_commit(w,36848,-1200));self.assertEqual(self.snapshot(w),before)
  self.assertTrue(self.begin(w,-1280,-1280));self.assertEqual(self.tick(w),0)
  def corrupt(ctx,lba,n,p):C.memset(p,0x55,n*2048);return 1
  self.assertEqual(self.tick(w,CB(corrupt)),-1);self.assertFalse(self.L.cache23_commit(w,-1280,-1280));self.assertEqual(self.snapshot(w),before);self.assertTrue(self.load(w,-1280,-1280))
 def test_route(self):
  w=self.new();route=json.loads((R/'build_m18/play/route18.json').read_text());p=route[0];self.assertTrue(self.load(w,p['x'],p['z']));stats=[];waits=0;maxreads=0;maxwork=0
  for q in route[1:]:
   for attempt in range(20):
    nr=self.L.cache22_reads(w);nt=self.L.cache23_ticks(w);oldids=self.ids(w);ok=self.move(w,p['x'],p['z'],q['x'],q['z']);reads=self.L.cache22_reads(w)-nr;work=self.L.cache23_ticks(w)-nt;maxreads=max(maxreads,reads);maxwork=max(maxwork,work);stats.append(dict(x=q['x'] if ok else p['x'],z=q['z'] if ok else p['z'],reads=reads,work=work,pending=self.L.cache23_pending(w),committed=oldids!=self.ids(w),held=not ok))
    if ok:break
    waits+=1;self.assertEqual(oldids,self.ids(w))
   self.assertTrue(ok);self.assertEqual(self.ids(w),q['ids']);self.assertEqual(self.L.cache18_floor(w,q['x'],q['z'],q['y'],110),q['y']);p=q
  self.assertLessEqual(maxreads,1);self.assertLessEqual(maxwork,1);self.assertLessEqual(self.L.cache22_reads(w),route[-1]['reads']+1);report=dict(route_steps=len(route)-1,held_updates=waits,reads_including_startup=self.L.cache22_reads(w),max_reads_per_update=maxreads,max_blocks_per_update=maxwork,copied_bytes=self.L.cache22_copied(w),timeline=stats);(P/'prefetch_report.json').write_text(json.dumps(report,indent=2));print('prefetch route', {k:v for k,v in report.items() if k!='timeline'})
 def test_object_positions(self):
  w=self.new();forbidden=[]
  for o in self.man['objects']:
   x,y,z=[round(v) for v in o['source_xyz']];self.assertTrue(self.load(w,x,z));f=self.L.cache18_floor(w,x,z,-y,110)
   if f==32767:forbidden.append(o['name']);self.assertNotIn(o['kind'],(1,2,3))
  self.assertEqual(len(forbidden),13)
 def test_crc(self):
  a=C.CDLL(str(R/'build_m22/play/interact22_host.so'));b=self.L
  for L in (a,b):L.sector16_validate.argtypes=[C.c_char_p,C.c_uint32,C.c_uint32,C.c_uint32,C.c_uint32,C.POINTER(C.c_uint32)]
  for i in range(174):
   start=self.b[i]['lba']*2048;size=struct.unpack_from('<I',self.idx,16+i*60+8)[0];p=self.dat[start:start+size];m=(C.c_uint32*7)();n=(C.c_uint32*7)();self.assertEqual(a.sector16_validate(p,size,208,75653,6195,m),1);self.assertEqual(b.sector16_validate(p,size,208,75653,6195,n),1);self.assertEqual(list(m),list(n));q=bytearray(p);q[-1]^=1;self.assertEqual(b.sector16_validate(bytes(q),size,208,75653,6195,n),0)
 def test_disc(self):
  d=(P/'ETD_PSX_M23.bin').read_bytes();self.assertIn(b'ETD_PREF.EXE;1',d[21*2352+24:21*2352+2072]);self.assertIn(b'ETD_DENSE.EXE;1',d[20*2352+24:20*2352+2072]);self.assertGreater(json.loads((P/'report.json').read_text())['headroom_to_stack_region'],65536)
  for i in range(len(d)//2352):s=d[i*2352:(i+1)*2352];self.assertEqual(s,old.raw(i,s[24:2072]))
 def test_disc_prefetch(self):
  L=C.CDLL(str(P/'cache23_host.so'));d=(P/'ETD_PSX_M23.bin').read_bytes();L.mock17_setup.argtypes=[C.c_char_p,C.c_uint,C.c_uint];L.cd17_read.argtypes=[C.c_void_p,C.c_uint32,C.c_uint32,C.c_void_p];L.iso17_pvd.argtypes=[C.c_void_p,C.POINTER(C.c_uint32)];L.iso17_find.argtypes=[C.c_void_p,C.c_char_p,C.c_uint32,C.POINTER(C.c_uint32)];L.mock17_setup(d,len(d)//2352,0);self.assertEqual(L.cd17_init(),1);buf=C.create_string_buffer(2048);p=(C.c_uint32*2)();ext=(C.c_uint32*2)();self.assertEqual(L.cd17_read(None,16,1,buf),1);self.assertEqual(L.iso17_pvd(buf,p),1);self.assertEqual(L.cd17_read(None,p[1],1,buf),1);self.assertEqual(L.iso17_find(buf,b'HUBSECT.DAT;1',p[0],ext),1);cb=CB(lambda ctx,lba,n,dst:L.cd17_read(None,ext[0]+lba,n,dst));w=self.new();self.assertTrue(self.load(w,36848,-1200,cb));self.assertTrue(self.begin(w,-1280,-1280));before=self.snapshot(w)
  for k in range(16):self.assertEqual(self.tick(w,cb),int(k==15));self.assertEqual(self.snapshot(w),before)
  self.assertTrue(self.L.cache23_commit(w,-1280,-1280));self.assertEqual(len(self.ids(w)),16)
if __name__=='__main__':unittest.main()
