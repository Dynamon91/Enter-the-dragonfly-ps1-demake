import ctypes as C,struct,json,unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'build_m17/view';A=ROOT/'assets_m16';sys.path.insert(0,str(ROOT/'tools'))
from disc16 import raw
class Resident(C.Structure):_fields_=[('slots',(C.c_ubyte*65536)*2),('meta',C.c_uint32*7),('active',C.c_int)]
CB=C.CFUNCTYPE(C.c_int,C.c_void_p,C.c_uint32,C.c_uint32,C.POINTER(C.c_ubyte))
class M17(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.lib=C.CDLL(str(P/'cd17_host.so'));cls.disc=(P/'ETD_PSX_M17.bin').read_bytes();cls.n=len(cls.disc)//2352;cls.buf=C.create_string_buffer(65536);cls.idx=(A/'HUBSECT.IDX').read_bytes();cls.dat=(A/'HUBSECT.DAT').read_bytes();cls.man=json.loads((A/'sector_manifest.json').read_text());L=cls.lib;L.mock17_setup.argtypes=[C.c_char_p,C.c_uint,C.c_uint];L.cd17_read.argtypes=[C.c_void_p,C.c_uint32,C.c_uint32,C.c_void_p];L.iso17_find.argtypes=[C.c_void_p,C.c_char_p,C.c_uint32,C.POINTER(C.c_uint32)];L.iso17_pvd.argtypes=[C.c_void_p,C.POINTER(C.c_uint32)];L.resident17_switch.argtypes=[C.POINTER(Resident),C.c_char_p,C.c_uint32,C.c_uint32,C.c_uint32,CB,C.c_void_p]
 def setup_read(self,mode=0):self.lib.mock17_setup(self.disc,self.n,mode);return self.lib.cd17_init()
 def mount(self):
  self.assertEqual(self.setup_read(),1);v=(C.c_uint32*2)();self.assertEqual(self.lib.cd17_read(None,16,1,self.buf),1);self.assertEqual(self.lib.iso17_pvd(self.buf,v),1);self.assertEqual(self.lib.cd17_read(None,v[1],1,self.buf),1);a=(C.c_uint32*2)();d=(C.c_uint32*2)();self.assertEqual(self.lib.iso17_find(self.buf,b'HUBSECT.IDX;1',v[0],a),1);self.assertEqual(self.lib.iso17_find(self.buf,b'HUBSECT.DAT;1',v[0],d),1);return a,d
 def test_all_blocks_via_register_mock(self):
  a,d=self.mount();self.assertEqual(self.lib.cd17_read(None,a[0],(a[1]+2047)//2048,self.buf),1);self.assertEqual(self.buf.raw[:a[1]],self.idx);r=Resident();self.lib.resident17_init(C.byref(r));cb=CB(lambda ctx,lba,n,p:self.lib.cd17_read(None,d[0]+lba,n,p));
  for b in self.man['blocks']:
   old=r.active;self.assertEqual(self.lib.resident17_switch(C.byref(r),self.idx,len(self.idx),b['id'],d[1]//2048,cb,None),1);self.assertNotEqual(old,r.active);self.assertEqual(list(r.meta)[:4],[b['id'],b['render'],b['collision'],b['objects']]);self.assertEqual(bytes(r.slots[r.active][:b['size']]),self.dat[b['lba']*2048:b['lba']*2048+b['size']]);
 def test_transactional_bad_read(self):
  r=Resident();self.lib.resident17_init(C.byref(r));good=CB(lambda ctx,lba,n,p:(C.memmove(p,self.dat[lba*2048:(lba+n)*2048],n*2048),1)[1]);bad=CB(lambda ctx,lba,n,p:(C.memset(p,0xaa,n*2048),1)[1]);args=(C.byref(r),self.idx,len(self.idx));self.assertEqual(self.lib.resident17_switch(*args,0,len(self.dat)//2048,good,None),1);before=bytes(r.slots[r.active]);meta=list(r.meta);active=r.active;self.assertEqual(self.lib.resident17_switch(*args,1,len(self.dat)//2048,bad,None),0);self.assertEqual((r.active,list(r.meta),bytes(r.slots[r.active])),(active,meta,before))
 def test_cd_timeouts_and_fault_latch(self):
  self.assertEqual(self.setup_read(1),0);self.assertEqual(self.lib.cd17_read(None,16,1,self.buf),0)
  for mode in (2,3):
   self.assertEqual(self.setup_read(mode),1);self.assertEqual(self.lib.cd17_read(None,16,1,self.buf),0);cmd=self.lib.mock17_commands();self.assertEqual(self.lib.cd17_read(None,16,1,self.buf),0);self.assertEqual(self.lib.mock17_commands(),cmd)
 def test_bounds(self):
  self.assertEqual(self.setup_read(),1)
  for l,n in [(0,0),(0,33),(449850,1),(449849,2)]:self.assertEqual(self.lib.cd17_read(None,l,n,self.buf),0)
 def test_iso_parser_rejects_corruption(self):
  a,d=self.mount();v=(C.c_uint32*2)();p=bytearray(self.disc[16*2352+24:16*2352+2072]);p[84]^=1;self.assertEqual(self.lib.iso17_pvd(bytes(p),v),0);root=bytearray(self.disc[20*2352+24:20*2352+2072]);self.assertEqual(self.lib.iso17_find(bytes(root),b'NOPE;1',self.n,v),0);root[0]=10;self.assertEqual(self.lib.iso17_find(bytes(root),b'HUBSECT.DAT;1',self.n,v),0)
 def test_disc_integrity(self):
  for i in range(self.n):s=self.disc[i*2352:(i+1)*2352];self.assertEqual(s,raw(i,s[24:2072]));
  self.assertIn(b'ETD_CD.EXE;1',self.disc[21*2352+24:21*2352+2072]);e=(P/'ETD_CD.EXE').read_bytes();self.assertEqual(e[:8],b'PS-X EXE');self.assertEqual(len(e)-2048,struct.unpack_from('<I',e,28)[0]);self.assertLess(json.loads((P/'report.json').read_text())['linked_ram_from_load'],256*1024)
