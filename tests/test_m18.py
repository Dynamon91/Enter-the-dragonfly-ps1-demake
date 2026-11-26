import ctypes as C,struct,json,unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'build_m18/play';A=ROOT/'assets_m16';sys.path.insert(0,str(ROOT/'tools'))
from disc16 import raw
class Cache(C.Structure):_fields_=[('data',(C.c_ubyte*65536)*16),('meta',(C.c_uint32*7)*16),('ids',C.c_int*16),('active',C.c_int*8),('count',C.c_int),('ax',C.c_int),('az',C.c_int),('reads',C.c_int)]
CB=C.CFUNCTYPE(C.c_int,C.c_void_p,C.c_uint32,C.c_uint32,C.POINTER(C.c_ubyte))
class M18(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.L=C.CDLL(str(P/'cache18_host.so'));cls.disc=(P/'ETD_PSX_M18.bin').read_bytes();cls.n=len(cls.disc)//2352;cls.idx=(A/'HUBSECT.IDX').read_bytes();cls.dat=(A/'HUBSECT.DAT').read_bytes();cls.b=json.loads((A/'sector_manifest.json').read_text())['blocks'];L=cls.L
  L.cache18_init.argtypes=[C.POINTER(Cache)];L.cache18_select.argtypes=[C.c_char_p,C.c_uint32,C.c_int,C.c_int,C.POINTER(C.c_int)];L.cache18_update.argtypes=[C.POINTER(Cache),C.c_char_p,C.c_uint32,C.c_uint32,C.c_int,C.c_int,CB,C.c_void_p];L.cache18_floor.argtypes=[C.POINTER(Cache),C.c_int,C.c_int,C.c_int,C.c_int];L.mock17_setup.argtypes=[C.c_char_p,C.c_uint,C.c_uint];L.cd17_read.argtypes=[C.c_void_p,C.c_uint32,C.c_uint32,C.c_void_p];L.iso17_find.argtypes=[C.c_void_p,C.c_char_p,C.c_uint32,C.POINTER(C.c_uint32)];L.iso17_pvd.argtypes=[C.c_void_p,C.POINTER(C.c_uint32)]
  cls.good=CB(lambda ctx,lba,n,p:(C.memmove(p,cls.dat[lba*2048:(lba+n)*2048],n*2048),1)[1])
 def new(self):c=Cache();self.L.cache18_init(C.byref(c));return c
 def update(self,c,x,z,cb=None):return self.L.cache18_update(C.byref(c),self.idx,len(self.idx),len(self.dat)//2048,x,z,cb or self.good,None)
 def selected(self,c):return [c.ids[c.active[i]] for i in range(c.count)]
 def floor(self,c,x,z,y=800):return self.L.cache18_floor(C.byref(c),x,z,y,110)
 def select(self,x,z):a=(C.c_int*8)();n=self.L.cache18_select(self.idx,len(self.idx),x,z,a);return list(a)[:n] if n>=0 else None
 def test_index_selection(self):
  for b in self.b:
   x,_,z=b['origin'];ax=x//512*512+256;az=z//512*512+256;expect=[i['id'] for i in self.b if i['bounds'][0][0]<=ax+1536 and i['bounds'][1][0]>=ax-1536 and i['bounds'][0][2]<=az+1536 and i['bounds'][1][2]>=az-1536];self.assertEqual(self.select(x,z),expect if len(expect)<=8 else None)
 def test_spawn_and_reuse(self):
  c=self.new();self.assertEqual(self.update(c,36848,-1200),1);self.assertEqual(self.selected(c),[93,141,142,153,154]);self.assertEqual(self.floor(c,36848,-1200),800);r=c.reads;self.assertEqual(self.update(c,36849,-1200),1);self.assertEqual(c.reads,r)
 def test_actual_disc_transport(self):
  L=self.L;L.mock17_setup(self.disc,self.n,0);self.assertEqual(L.cd17_init(),1);buf=C.create_string_buffer(2048);p=(C.c_uint32*2)();ext=(C.c_uint32*2)();self.assertEqual(L.cd17_read(None,16,1,buf),1);self.assertEqual(L.iso17_pvd(buf,p),1);self.assertEqual(L.cd17_read(None,p[1],1,buf),1);self.assertEqual(L.iso17_find(buf,b'HUBSECT.DAT;1',p[0],ext),1);cb=CB(lambda ctx,lba,n,dst:L.cd17_read(None,ext[0]+lba,n,dst));c=self.new();self.assertEqual(self.update(c,36848,-1200,cb),1);self.assertEqual(self.floor(c,36848,-1200),800)
 def test_failed_transaction(self):
  c=self.new();self.assertEqual(self.update(c,36848,-1200),1);ids=self.selected(c);before=[bytes(c.data[c.active[i]]) for i in range(c.count)];ax,az=c.ax,c.az;bad=CB(lambda ctx,lba,n,p:(C.memset(p,0x55,n*2048),1)[1]);target=next((b['origin'] for b in self.b if self.select(b['origin'][0],b['origin'][2]) and set(self.select(b['origin'][0],b['origin'][2]))-set(ids)));self.assertEqual(self.update(c,target[0],target[2],bad),0);self.assertEqual((self.selected(c),c.ax,c.az),(ids,ax,az));self.assertEqual([bytes(c.data[c.active[i]]) for i in range(c.count)],before)
 def test_dense_region_rejection(self):
  c=self.new();self.assertEqual(self.update(c,36848,-1200),1);ids=self.selected(c);target=next(b['origin'] for b in self.b if self.select(b['origin'][0],b['origin'][2]) is None);self.assertEqual(self.update(c,target[0],target[2]),0);self.assertEqual(self.selected(c),ids)
 def test_traverse(self):
  # Run exactly the movement floor gates (38-unit cardinal steps), with original source data.
  best=None
  for dx,dz in [(38,0),(-38,0),(0,38),(0,-38)]:
   c=self.new();x,z,y=36848,-1200,800;self.assertEqual(self.update(c,x,z),1);route=[dict(x=x,z=z,y=y,ids=self.selected(c),reads=c.reads)]
   for _ in range(140):
    nx,nz=x+dx,z+dz;mid=self.floor(c,(x+nx)//2,(z+nz)//2,y);f=self.floor(c,nx,nz,y)
    if mid==32767 or f==32767 or not self.update(c,nx,nz):break
    x,z,y=nx,nz,f;route.append(dict(x=x,z=z,y=y,ids=self.selected(c),reads=c.reads))
   if best is None or len(route)>len(best):best=route
  self.assertGreater(len(best),30);self.assertGreater(len({tuple(s['ids']) for s in best}),1);(P/'route18.json').write_text(json.dumps(best,indent=2));print('M18 route:',len(best)-1,'steps;',best[-1]['reads'],'reads;',len({tuple(s['ids']) for s in best}),'resident sets')
 def test_z_route_register_transport(self):
  route=json.loads((P/'route18.json').read_text());L=self.L;L.mock17_setup(self.disc,self.n,0);self.assertEqual(L.cd17_init(),1);buf=C.create_string_buffer(2048);p=(C.c_uint32*2)();ext=(C.c_uint32*2)();self.assertEqual(L.cd17_read(None,16,1,buf),1);self.assertEqual(L.iso17_pvd(buf,p),1);self.assertEqual(L.cd17_read(None,p[1],1,buf),1);self.assertEqual(L.iso17_find(buf,b'HUBSECT.DAT;1',p[0],ext),1);cb=CB(lambda ctx,lba,n,dst:L.cd17_read(None,ext[0]+lba,n,dst));c=self.new()
  for r in route:
   self.assertEqual(self.update(c,r['x'],r['z'],cb),1);self.assertEqual(self.selected(c),r['ids']);self.assertEqual(self.floor(c,r['x'],r['z'],r['y']),r['y'])
  self.assertEqual(c.reads,route[-1]['reads'])
 def test_disc_readback(self):
  for i in range(self.n):s=self.disc[i*2352:(i+1)*2352];self.assertEqual(s,raw(i,s[24:2072]));
  self.assertIn(b'ETD_WALK.EXE;1',self.disc[21*2352+24:21*2352+2072]);self.assertLess(json.loads((P/'report.json').read_text())['linked_ram_from_load'],0x1d0000)
if __name__=='__main__':unittest.main()
