import ctypes as C,json,struct,unittest,sys
import numpy as np
from pathlib import Path
from test_m21 import Inter,CB
R=Path(__file__).resolve().parents[1];P=R/'build_m22/play';A=R/'assets_m16';sys.path.insert(0,str(R/'tools'));from disc16 import raw
class M22(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  L=cls.L=C.CDLL(str(P/'interact22_host.so'));cls.idx=(A/'HUBSECT.IDX').read_bytes();cls.dat=(A/'HUBSECT.DAT').read_bytes();cls.man=json.loads((A/'sector_manifest.json').read_text());cls.b=cls.man['blocks'];cls.sizes=[(struct.unpack_from('<I',cls.idx,16+i*60+8)[0]+2047)//2048*2048 for i in range(174)];cls.good=CB(lambda ctx,lba,n,p:(C.memmove(p,cls.dat[lba*2048:(lba+n)*2048],n*2048),1)[1]);L.cache18_init.argtypes=[C.c_void_p];L.cache18_select.argtypes=[C.c_char_p,C.c_uint32,C.c_int,C.c_int,C.POINTER(C.c_int)];L.cache18_update.argtypes=[C.c_void_p,C.c_char_p,C.c_uint32,C.c_uint32,C.c_int,C.c_int,CB,C.c_void_p];L.cache18_floor.argtypes=[C.c_void_p,C.c_int,C.c_int,C.c_int,C.c_int];L.cache22_size.restype=C.c_uint32
  for name in ('count','bytes','copied','reads'):getattr(L,'cache22_'+name).argtypes=[C.c_void_p]
  L.cache22_id.argtypes=[C.c_void_p,C.c_int];L.cache22_data.argtypes=[C.c_void_p,C.c_int];L.cache22_data.restype=C.c_void_p;L.step21.argtypes=[C.POINTER(Inter),C.c_void_p]+[C.c_int]*12;L.reset21.argtypes=[C.POINTER(Inter)]
 def new(self):w=C.create_string_buffer(self.L.cache22_size());self.L.cache18_init(w);return w
 def load(self,w,x,z,cb=None):return self.L.cache18_update(w,self.idx,len(self.idx),len(self.dat)//2048,x,z,cb or self.good,None)
 def ids(self,w):return [self.L.cache22_id(w,i) for i in range(self.L.cache22_count(w))]
 def test_all_neighborhoods(self):
  lo=np.array([b['bounds'][0] for b in self.b]);hi=np.array([b['bounds'][1] for b in self.b]);seen={};anchors=0;groups=[a['texture_group'] for a in self.man['materials']];g=[]
  for b in self.b:g.append({groups[struct.unpack_from('<H',self.dat,b['lba']*2048+64+36*j+30)[0]] for j in range(b['render'])}-{None})
  for x in range(lo[:,0].min()//512*512-2048,hi[:,0].max()+2048,512):
   for z in range(lo[:,2].min()//512*512-2048,hi[:,2].max()+2048,512):
    a=x+256;c=z+256;expected=tuple(int(i) for i in np.where((lo[:,0]<=a+1536)&(hi[:,0]>=a-1536)&(lo[:,2]<=c+1536)&(hi[:,2]>=c-1536))[0]);ids=(C.c_int*16)();n=self.L.cache18_select(self.idx,len(self.idx),a,c,ids);self.assertEqual(n,len(expected));self.assertEqual(tuple(ids[:n]),expected)
    if expected:anchors+=1;seen.setdefault(expected,(a,c))
  w=self.new();mx=mt=mc=0
  for ids,(x,z) in seen.items():
   self.assertTrue(self.load(w,x,z));self.assertEqual(self.ids(w),list(ids));sz=sum(self.sizes[i] for i in ids);self.assertEqual(self.L.cache22_bytes(w),sz);mx=max(mx,sz);mc=max(mc,len(ids));mt=max(mt,len(set().union(*(g[i] for i in ids))))
   for j,i in enumerate(ids):
    p=self.b[i]['lba']*2048;self.assertEqual(C.string_at(self.L.cache22_data(w,j),self.sizes[i]),self.dat[p:p+self.sizes[i]])
  self.assertEqual((anchors,len(seen),mc,mx,mt),(11515,1021,16,542720,47));(P/'coverage22.json').write_text(json.dumps(dict(anchors=anchors,sets=len(seen),max_blocks=mc,max_bytes=mx,max_textures=mt),indent=2))
 def test_objects(self):
  w=self.new();o=[]
  for x in self.man['objects']:
   px,py,pz=[round(v) for v in x['source_xyz']];self.assertTrue(self.load(w,px,pz),x['name']);floor=self.L.cache18_floor(w,px,pz,-py,110);o.append(dict(name=x['name'],kind=x['kind'],xyz=[px,-py,pz],ids=self.ids(w),floor=floor,bytes=self.L.cache22_bytes(w)))
  self.assertEqual(len(o),380);self.assertTrue(all(a['floor']!=32767 for a in o if a['kind'] in (1,2,3)));(P/'objects22.json').write_text(json.dumps(o,indent=2))
 def test_rollback(self):
  w=self.new();self.assertTrue(self.load(w,36848,-1200));old=self.ids(w);before=[C.string_at(self.L.cache22_data(w,j),self.sizes[i]) for j,i in enumerate(old)];calls=0
  def fail(ctx,lba,n,p):
   nonlocal calls;calls+=1
   if calls==3:C.memset(p,0x55,n*2048);return 1
   return self.good(ctx,lba,n,p)
  self.assertFalse(self.load(w,-1280,-1280,CB(fail)));self.assertEqual(calls,3);self.assertEqual(self.ids(w),old);self.assertEqual([C.string_at(self.L.cache22_data(w,j),self.sizes[i]) for j,i in enumerate(old)],before);self.assertEqual(self.L.cache18_floor(w,36848,-1200,800,110),800);self.assertTrue(self.load(w,-1280,-1280));self.assertEqual(len(self.ids(w)),16)
 def test_route(self):
  w=self.new();route=json.loads((R/'build_m18/play/route18.json').read_text())
  for r in route:
   self.assertTrue(self.load(w,r['x'],r['z']));self.assertEqual(self.ids(w),r['ids']);self.assertEqual(self.L.cache18_floor(w,r['x'],r['z'],r['y'],110),r['y'])
  self.assertEqual(self.L.cache22_reads(w),route[-1]['reads']);print('route reads',self.L.cache22_reads(w),'copied bytes',self.L.cache22_copied(w))
 def test_disc(self):
  d=(P/'ETD_PSX_M22.bin').read_bytes();self.assertIn(b'ETD_DENSE.EXE;1',d[21*2352+24:21*2352+2072]);self.assertIn(b'ETD_HUB.EXE;1',d[20*2352+24:20*2352+2072]);self.assertGreater(json.loads((P/'report.json').read_text())['headroom_to_stack_region'],65536)
  for i in range(len(d)//2352):s=d[i*2352:(i+1)*2352];self.assertEqual(s,raw(i,s[24:2072]))
 def test_dense_disc_transport(self):
  L=C.CDLL(str(P/'cache22_host.so'));d=(P/'ETD_PSX_M22.bin').read_bytes();L.mock17_setup.argtypes=[C.c_char_p,C.c_uint,C.c_uint];L.cd17_read.argtypes=[C.c_void_p,C.c_uint32,C.c_uint32,C.c_void_p];L.iso17_pvd.argtypes=[C.c_void_p,C.POINTER(C.c_uint32)];L.iso17_find.argtypes=[C.c_void_p,C.c_char_p,C.c_uint32,C.POINTER(C.c_uint32)];L.mock17_setup(d,len(d)//2352,0);self.assertEqual(L.cd17_init(),1);buf=C.create_string_buffer(2048);p=(C.c_uint32*2)();ext=(C.c_uint32*2)();self.assertEqual(L.cd17_read(None,16,1,buf),1);self.assertEqual(L.iso17_pvd(buf,p),1);self.assertEqual(L.cd17_read(None,p[1],1,buf),1);self.assertEqual(L.iso17_find(buf,b'HUBSECT.DAT;1',p[0],ext),1);cb=CB(lambda ctx,lba,n,dst:L.cd17_read(None,ext[0]+lba,n,dst));w=self.new();self.assertTrue(self.load(w,36848,-1200,cb));self.assertTrue(self.load(w,-1280,-1280,cb));self.assertEqual(len(self.ids(w)),16);self.assertEqual(self.L.cache22_bytes(w),542720)
 def test_interactions(self):
  w=self.new();s=Inter();self.L.reset21(C.byref(s));o=next(a for a in self.man['objects'] if a['name']=='Farm_Basket1_1');x,y,z=[round(v) for v in o['source_xyz']];y=-y;self.assertTrue(self.load(w,x,z))
  for _ in range(20):
   self.L.step21(C.byref(s),w,x,y,z-300,x,z-300,0,0,1,1,x,y-190,z-300)
   if s.broken:break
  self.assertEqual(s.broken,1);self.assertTrue(self.load(w,-1280,-1280));self.assertTrue(self.load(w,x,z));self.assertEqual(sum(s.state),1)
if __name__=='__main__':unittest.main()
