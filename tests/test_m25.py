import ctypes as C,struct,json,unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'build_m25/view';A=ROOT/'assets_m25';sys.path.insert(0,str(ROOT/'tools'))
from disc16 import raw
class Resident(C.Structure):_fields_=[('slots',(C.c_ubyte*65536)*2),('meta',C.c_uint32*7),('active',C.c_int)]
CB=C.CFUNCTYPE(C.c_int,C.c_void_p,C.c_uint32,C.c_uint32,C.POINTER(C.c_ubyte))
class M25(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.lib=C.CDLL(str(P/'dojo25_host.so'));cls.disc=(P/'ETD_PSX_M25.bin').read_bytes();cls.n=len(cls.disc)//2352;cls.buf=C.create_string_buffer(65536);cls.idx=(A/'DOJOSECT.IDX').read_bytes();cls.dat=(A/'DOJOSECT.DAT').read_bytes();cls.man=json.loads((A/'sector_manifest.json').read_text());L=cls.lib;L.mock17_setup.argtypes=[C.c_char_p,C.c_uint,C.c_uint];L.cd17_read.argtypes=[C.c_void_p,C.c_uint32,C.c_uint32,C.c_void_p];L.iso17_find.argtypes=[C.c_void_p,C.c_char_p,C.c_uint32,C.POINTER(C.c_uint32)];L.iso17_pvd.argtypes=[C.c_void_p,C.POINTER(C.c_uint32)];L.resident17_switch.argtypes=[C.POINTER(Resident),C.c_char_p,C.c_uint32,C.c_uint32,C.c_uint32,CB,C.c_void_p]
 def setup_read(self,mode=0):self.lib.mock17_setup(self.disc,self.n,mode);return self.lib.cd17_init()
 def mount(self):
  self.assertEqual(self.setup_read(),1);v=(C.c_uint32*2)();self.assertEqual(self.lib.cd17_read(None,16,1,self.buf),1);self.assertEqual(self.lib.iso17_pvd(self.buf,v),1);self.assertEqual(self.lib.cd17_read(None,v[1],1,self.buf),1);a=(C.c_uint32*2)();d=(C.c_uint32*2)();self.assertEqual(self.lib.iso17_find(self.buf,b'DOJOSECT.IDX;1',v[0],a),1);self.assertEqual(self.lib.iso17_find(self.buf,b'DOJOSECT.DAT;1',v[0],d),1);return a,d
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
  a,d=self.mount();v=(C.c_uint32*2)();p=bytearray(self.disc[16*2352+24:16*2352+2072]);p[84]^=1;self.assertEqual(self.lib.iso17_pvd(bytes(p),v),0);root=bytearray(self.disc[20*2352+24:20*2352+2072]);self.assertEqual(self.lib.iso17_find(bytes(root),b'NOPE;1',self.n,v),0);root[0]=10;self.assertEqual(self.lib.iso17_find(bytes(root),b'DOJOSECT.DAT;1',self.n,v),0)
 def test_disc_integrity(self):
  for i in range(self.n):s=self.disc[i*2352:(i+1)*2352];self.assertEqual(s,raw(i,s[24:2072]));
  self.assertIn(b'ETD_DOJO.EXE;1',self.disc[21*2352+24:21*2352+2072]);e=(P/'ETD_DOJO.EXE').read_bytes();self.assertEqual(e[:8],b'PS-X EXE');self.assertEqual(len(e)-2048,struct.unpack_from('<I',e,28)[0]);self.assertLess(json.loads((P/'report.json').read_text())['linked_ram_from_load'],256*1024)

 def test_source_coverage(self):
  import numpy as np
  r=json.loads((A/'dojo_report.json').read_text());m=json.loads((A/'material_report.json').read_text());self.assertEqual(r['matched']+r['duplicate_shapes']+len(r['unmatched']),r['source_shapes']);self.assertEqual(sum(x['render'] for x in self.man['blocks']),r['triangles']);self.assertEqual(sum(x['objects'] for x in self.man['blocks']),m['objects']);self.assertEqual(len({x['record_offset'] for x in self.man['objects']}),m['objects']);self.assertTrue(all(x['bounds_error']<.01 for x in r['meshes']));z=np.load(A/'dojo.npz');self.assertEqual(len(z['faces']),r['triangles']);self.assertEqual(len(z['vertices']),r['vertices'])
 def test_source_ids_and_quantization(self):
  import numpy as np
  z=np.load(A/'dojo.npz');v=z['vertices'][z['faces']]*[1,-1,1];seen=set();cids=set();objects=set();bindings=json.loads((A/'bindings.json').read_text());mids=np.array(bindings['bindings'])[z['part']];uv=z['uv'][z['faces']]
  for b in self.man['blocks']:
   p=self.dat[b['lba']*2048:][:b['size']];nr,nc,no=struct.unpack_from('<3H',p,24);a=np.frombuffer(p,dtype=np.dtype([('v','<i2',(3,3)),('uv','<i2',(3,2)),('m','<u2'),('id','<u4')]),count=nr,offset=64);ids=a['id'];self.assertTrue(np.allclose(a['v']+np.array(b['origin']),v[ids],rtol=0,atol=.501));self.assertTrue(np.array_equal(a['m'],mids[ids]));delta=a['uv'].astype(float)/1024-uv[ids];self.assertTrue(np.max(np.abs(delta-np.rint(delta)),initial=0)<=.00049);self.assertFalse(seen.intersection(ids));seen.update(ids)
   for j in range(nc):cids.add(struct.unpack_from('<I',p,64+36*nr+24*j+20)[0])
   for j in range(no):objects.add(struct.unpack_from('<I',p,64+36*nr+24*nc+16*j+12)[0])
  self.assertEqual(seen,set(range(len(v))));self.assertEqual(len(cids),7035);self.assertEqual(len(objects),351)
 def test_texture_bank_crc(self):
  import zlib
  idx=(A/'DOJOTEX.IDX').read_bytes();dat=(A/'DOJOTEX.DAT').read_bytes();n=struct.unpack_from('<I',idx,8)[0];self.assertEqual(n,52);self.assertEqual(len(dat),n*6144)
  for i in range(n):
   g,lba,crc=struct.unpack_from('<III',idx,12+i*12);p=dat[lba*2048:][:6144];magic,ver,group,w,h,size,c=struct.unpack_from('<4sHHIIII',p);self.assertEqual((magic,ver,group,size,c),(b'ETDT',1,g,4608,crc));self.assertEqual(zlib.crc32(p[24:24+size]),crc)
 def test_hub_fallback_preserved(self):
  root=self.disc[20*2352+24:20*2352+2072];a=(C.c_uint32*2)();self.assertEqual(self.lib.iso17_find(root,b'ETD_POOL.EXE;1',self.n,a),1);data=b''.join(self.disc[i*2352+24:i*2352+2072] for i in range(a[0],a[0]+(a[1]+2047)//2048))[:a[1]];self.assertEqual(data,(ROOT/'build_m24/play/ETD_POOL.EXE').read_bytes())
