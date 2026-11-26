import ctypes as C,json,struct,sys,tempfile,unittest,zlib,re
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'build_m16/play';A=ROOT/'assets_m16';sys.path.insert(0,str(ROOT/'tools'))
from sectors16 import H,D,MAX,SECTOR
from disc16 import raw
from cnk import ISO
class Milestone16(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.man=json.loads((A/'sector_manifest.json').read_text());cls.rep=json.loads((A/'sector_report.json').read_text());cls.blob=(A/'HUBSECT.DAT').read_bytes();cls.idx=(A/'HUBSECT.IDX').read_bytes();cls.lib=C.CDLL(str(P/'sector16_host.so'));cls.buf=(C.c_ubyte*65536)();cls.out=(C.c_uint32*7)();cls.CB=C.CFUNCTYPE(C.c_int,C.c_void_p,C.c_uint32,C.c_uint32,C.POINTER(C.c_ubyte));cls.lib.sector16_load.argtypes=[C.c_char_p,C.c_uint32,C.c_uint32,C.c_uint32,C.c_uint32,C.c_uint32,C.c_uint32,C.POINTER(C.c_ubyte),C.c_uint32,cls.CB,C.c_void_p,C.POINTER(C.c_uint32)];cls.lib.sector16_validate.argtypes=[C.c_char_p,C.c_uint32,C.c_uint32,C.c_uint32,C.c_uint32,C.POINTER(C.c_uint32)]
 def load(self,i,index=None,blob=None,cap=65536,fail=False):
  idx=self.idx if index is None else index;b=self.blob if blob is None else blob
  def read(ctx,lba,n,p):
   chunk=b[lba*2048:(lba+n)*2048]
   if fail or len(chunk)!=n*2048:return 0
   C.memmove(p,chunk,len(chunk));return 1
  return self.lib.sector16_load(idx,len(idx),i,len(b)//2048,self.rep['materials'],self.rep['render_triangles'],self.rep['collision_candidates'],self.buf,cap,self.CB(read),None,self.out)
 def test_all_native_sector_reads(self):
  for d in self.man['blocks']:
   self.assertEqual(self.load(d['id']),1,d);self.assertEqual(list(self.out)[:4],[d['id'],d['render'],d['collision'],d['objects']]);self.assertEqual(bytes(self.buf[:d['size']]),self.blob[d['lba']*2048:d['lba']*2048+d['size']])
 def test_loader_bounds_and_faults(self):
  d=max(self.man['blocks'],key=lambda d:d['size']);i=d['id'];self.assertEqual(self.load(i),1);old=list(self.out);self.assertEqual(self.load(i,cap=32768),0);self.assertEqual(self.load(i,fail=True),0);self.assertEqual(self.load(9999),0);self.assertEqual(list(self.out),old)
  for offset in (16+60*i+4,16+60*i+12,16+60*i+28):
   ix=bytearray(self.idx);ix[offset]^=0x80;self.assertEqual(self.load(i,index=bytes(ix)),0)
  b=bytearray(self.blob);b[d['lba']*2048+64]^=1;self.assertEqual(self.load(i,blob=bytes(b)),0);self.assertEqual(list(self.out),old)
 def test_invalid_payload_with_valid_crc(self):
  d=next(d for d in self.man['blocks'] if d['render']);p=bytearray(self.blob[d['lba']*2048:d['lba']*2048+d['size']]);struct.pack_into('<H',p,64+30,65535);struct.pack_into('<I',p,36,zlib.crc32(p[64:]));self.assertEqual(self.lib.sector16_validate(bytes(p),len(p),self.rep['materials'],self.rep['render_triangles'],self.rep['collision_candidates'],self.out),0)
 def test_roundtrip_geometry_and_source_ids(self):
  ts=[];uv=[];m=[];col=[];flags=[];obj={};render_seen=set();col_seen=set()
  for path in ['build_m05/hub','build_m08/shadow']:
   z=np.load(ROOT/path/'hub.npz');ts.extend(z['vertices'][z['faces']]*[1,-1,1]);uv.extend(z['uv'][z['faces']]);m.extend(z['material'])
  z=np.load(ROOT/'build_m06/collision/collision.npz');col=z['vertices'][z['faces']]*[1,-1,1];flags=z['polygon_flags'][z['part']];ts=np.asarray(ts);uv=np.asarray(uv);m=np.asarray(m)
  for d in self.man['blocks']:
   p=self.blob[d['lba']*2048:d['lba']*2048+d['size']];org=np.array(d['origin']);off=64
   for _ in range(d['render']):
    v=np.frombuffer(p,'<i2',9,off).reshape(3,3)+org;u=np.frombuffer(p,'<i2',6,off+18).reshape(3,2)/1024;mi,i=struct.unpack_from('<HI',p,off+30);self.assertNotIn(i,render_seen);render_seen.add(i);self.assertTrue(np.max(abs(v-ts[i]))<=.5);self.assertTrue(np.max(abs(u-uv[i]))<=1/2048);self.assertEqual(int(self.man['materials'][mi]['material'],16),m[i]);off+=36
   for _ in range(d['collision']):
    v=np.frombuffer(p,'<i2',9,off).reshape(3,3)+org;flag,i=struct.unpack_from('<HI',p,off+18);self.assertNotIn(i,col_seen);col_seen.add(i);self.assertTrue(np.max(abs(v-col[i]))<=.5);self.assertEqual(flag,flags[i]);off+=24
   for _ in range(d['objects']):
    v=np.frombuffer(p,'<i2',3,off)+org;k,val,_,i=struct.unpack_from('<HHHI',p,off+6);self.assertNotIn(i,obj);obj[i]=(v,k,val);off+=16
   self.assertEqual(off,len(p))
  self.assertEqual(render_seen,set(range(len(ts))));self.assertEqual(col_seen,set(range(len(col))));self.assertEqual(len(obj),380)
  for o in self.man['objects']:
   v,k,val=obj[o['record_offset']];self.assertTrue(np.max(abs(v-np.array(o['source_xyz'])*[1,-1,1]))<=.5);self.assertEqual(k,o['kind']);self.assertEqual(val,o.get('value',0))
 def test_sector_alignment_and_index(self):
  last=0;self.assertEqual(len(self.idx),16+60*len(self.man['blocks']));self.assertEqual(len(self.blob)%2048,0)
  for i,d in enumerate(self.man['blocks']):
   self.assertEqual(d['lba']*2048,last);self.assertLessEqual(d['size'],65536);self.assertEqual(D.unpack_from(self.idx,16+i*60)[:4],(i,d['lba'],d['size'],d['crc']));last=(last+d['size']+2047)//2048*2048
  self.assertEqual(last,len(self.blob))
 def test_texture_bank(self):
  tr=json.loads((A/'texture_report.json').read_text());b=(A/'HUBTEX.DAT').read_bytes();idx=(A/'HUBTEX.IDX').read_bytes();self.assertEqual(len(tr['entries']),141);self.assertEqual(len(b),141*6144);self.assertEqual(len(idx),12+141*12);self.assertEqual({e['group'] for e in tr['entries']},{e['texture_group'] for e in self.man['materials'] if e['texture_group'] is not None})
  for i,e in enumerate(tr['entries']):
   p=b[i*6144:(i+1)*6144];magic,ver,g,w,h,n,crc=struct.unpack_from('<4sHHIIII',p);self.assertEqual((magic,ver,g,w,h,n),(b'ETDT',1,e['group'],e['width'],e['height'],4608));self.assertEqual(zlib.crc32(p[24:24+n]),crc);self.assertEqual(struct.unpack_from('<III',idx,12+i*12),(g,i*3,crc));self.assertTrue(not any(p[24+n:]))
 def test_renderer_state_equivalence(self):
  old=(ROOT/'build_m15/play/world.h').read_text();new=(P/'world.h').read_text()
  def a(s,n):return np.array([int(x) for x in re.findall(r'\d+',re.search(r'\b'+n+r'\[[^;=]+\]\s*=\{(.*?)\};',s,re.S).group(1))],dtype=np.uint32)
  uv=a(new,'worlduv').reshape(-1,3);mat=a(new,'worldmat');st=a(new,'worldstate').reshape(-1,3)[mat];uv[:,0]|=st[:,0]<<16;uv[:,1]|=st[:,1]<<16;self.assertTrue(np.array_equal(uv,a(old,'worlduv').reshape(-1,3)));self.assertTrue(np.array_equal(st[:,2],a(old,'worldwindow')));self.assertTrue(np.array_equal(a(new,'worldupload'),a(old,'worldupload')))
 def test_native_memory_and_assets(self):
  r=json.loads((P/'report.json').read_text());old=json.loads((ROOT/'build_m15/play/report.json').read_text());self.assertGreaterEqual(old['linked_ram_from_load']-r['linked_ram_from_load'],44000);self.assertGreaterEqual(r['headroom_to_stack_region'],65536+10456);e=(P/'ETD_SECT.EXE').read_bytes();self.assertEqual(e[:8],b'PS-X EXE');self.assertEqual(len(e)-2048,struct.unpack_from('<I',e,28)[0]);self.assertEqual((P/'sector16.o').read_bytes()[:4],b'\x7fELF');self.assertEqual(struct.unpack_from('<H',(P/'sector16.o').read_bytes(),18)[0],8)
  for n in ('scene.h','farm06.npz','rig11_data.h','collectdata12.h','basketdata14.h','fodderdata15.h','sfx_bank.bin','visibility.h'):self.assertEqual((P/n).read_bytes(),(ROOT/'build_m15/play'/n).read_bytes())
 def test_disc_all_files(self):
  b=(P/'ETD_PSX_M16.bin').read_bytes();self.assertEqual(len(b)%2352,0);cooked=bytearray()
  for i in range(0,len(b),2352):
   s=b[i:i+2352];data=s[24:2072];self.assertEqual(s,raw(i//2352,data));cooked.extend(data)
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'test.iso';p.write_bytes(cooked)
   with ISO(p) as iso:
    self.assertEqual(iso.file('ETD_SECT.EXE'),(P/'ETD_SECT.EXE').read_bytes());self.assertIn(b'cdrom:\\ETD_SECT.EXE;1',iso.file('SYSTEM.CNF'))
    for n in ('HUBSECT.DAT','HUBSECT.IDX','HUBTEX.DAT','HUBTEX.IDX'):self.assertEqual(iso.file(n),(A/n).read_bytes())
