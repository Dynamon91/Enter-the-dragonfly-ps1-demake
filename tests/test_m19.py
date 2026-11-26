import ctypes as C,struct,json,unittest,sys,random,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'build_m19/play';A=ROOT/'assets_m16';sys.path.insert(0,str(ROOT/'tools'))
from disc16 import raw
from test_m18 import CB
UP=C.CFUNCTYPE(None,C.c_void_p,C.c_int,C.POINTER(C.c_ubyte))
class Tex(C.Structure):_fields_=[('slots',C.c_int*64),('map',C.c_int*540),('reads',C.c_int),('failed',C.c_int),('missing',C.c_int)]
class M19(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.L=C.CDLL(str(P/'tex19_host.so'));L=cls.L;cls.idx=(A/'HUBTEX.IDX').read_bytes();cls.dat=(A/'HUBTEX.DAT').read_bytes();cls.m=json.loads((A/'sector_manifest.json').read_text());cls.groups=[x['texture_group'] for x in cls.m['materials']];cls.entries=[struct.unpack_from('<III',cls.idx,12+12*i) for i in range(141)];cls.groupdata={g:cls.dat[lba*2048+24:lba*2048+24+4608] for g,lba,_ in cls.entries};cls.route=json.loads((P/'route18.json').read_text());cls.disc=(P/'ETD_PSX_M19.bin').read_bytes();cls.n=len(cls.disc)//2352
  L.refreshhost19.argtypes=[C.POINTER(Tex),C.c_char_p,C.POINTER(C.c_uint32),CB,C.c_void_p,UP,C.c_void_p];L.axis19.argtypes=[C.c_int,C.c_int,C.c_int,C.POINTER(C.c_int)];L.mock17_setup.argtypes=[C.c_char_p,C.c_uint,C.c_uint];L.cd17_read.argtypes=[C.c_void_p,C.c_uint32,C.c_uint32,C.c_void_p];L.iso17_find.argtypes=[C.c_void_p,C.c_char_p,C.c_uint32,C.POINTER(C.c_uint32)]
  cls.good=CB(lambda ctx,lba,n,p:(C.memmove(p,cls.dat[lba*2048:(lba+n)*2048],n*2048),1)[1]);d=(A/'HUBSECT.DAT').read_bytes();cls.freq={}
  for b in cls.m['blocks']:
   off=b['lba']*2048+64;gs=[cls.groups[struct.unpack_from('<H',d,off+36*j+30)[0]] for j in range(b['render'])];cls.freq[b['id']]=collections.Counter(g for g in gs if g is not None)
 def test_index_and_all_blocks(self):
  L=self.L;self.assertEqual(L.validate19(self.idx,len(self.idx),len(self.dat)//2048),1)
  for i,(g,lba,c) in enumerate(self.entries):
   b=self.dat[lba*2048:(lba+3)*2048];e=self.idx[12+i*12:24+i*12];self.assertEqual(L.block19(b,e),1);bad=bytearray(b);bad[30]^=1;self.assertEqual(L.block19(bytes(bad),e),0)
  bad=bytearray(self.idx);bad[16]=255;self.assertEqual(L.validate19(bytes(bad),len(bad),423),0)
 def test_vram_layout(self):
  occupied=set();actor=[(768,0,256,1),(768,1,256,1),(768,2,256,1),(320,0,128,256),(448,0,32,64),(512,0,32,64),(0,0,320,240),(0,256,320,240)]
  def put(x,y,w,h):
   self.assertTrue(x>=0 and y>=0 and x+w<=1024 and y+h<=512);s={(xx,yy) for yy in range(y,y+h) for xx in range(x,x+w)};self.assertFalse(occupied&s);occupied.update(s)
  for r in actor:put(*r)
  for k in range(64):
   a=(C.c_uint32*5)();self.L.slot19(k,a);x,y,cl,p,w=a;put(x,y,32,64);put((cl&63)*16,cl>>6,256,1)
   for u in [0,63,64,127,255]:
    for v in [0,63,64,127,255]:
     ux=(u&~((w&31)*8))|(((w>>10)&31)*8 & ((w&31)*8));vy=(v&~(((w>>5)&31)*8))|(((w>>15)&31)*8 & (((w>>5)&31)*8));self.assertEqual((p&15)*64+ux//2,x+(u%64)//2);self.assertEqual(((p>>4)&1)*256+vy,y+v%64)
 def test_uv_normalization(self):
  rng=random.Random(19);out=(C.c_int*3)()
  for _ in range(12000):
   v=[rng.randint(-32768,32767) for i in range(3)];base=min(v)//1024*1024;ok=max(v)-base<4096;self.assertEqual(bool(self.L.axis19(*v,out)),ok)
   if ok:self.assertEqual(list(out),[(x-base)//16 for x in v]);self.assertEqual([x%64 for x in out],[(x//16)%64 for x in v])
 def test_full_source_uv_subdivision(self):
  d=(A/'HUBSECT.DAT').read_bytes();L=self.L;L.split19.argtypes=[C.POINTER(C.c_int),C.POINTER(C.c_int),C.c_int,C.POINTER(C.c_int)];a=C.c_int(0);n=0;sub=0
  for b in self.m['blocks']:
   for j in range(b['render']):
    v=struct.unpack_from('<6h',d,b['lba']*2048+64+36*j+18);u=(C.c_int*3)(*v[::2]);w=(C.c_int*3)(*v[1::2]);k=L.split19(u,w,0,C.byref(a));self.assertGreater(k,0);n+=1;sub+=k
  self.assertEqual(n,75653);print('source UV split:',n,'source triangles,',sub,'unclipped output triangles, max depth',a.value)
  (P/'uv_report19.json').write_text(json.dumps(dict(source_triangles=n,unclipped_subdivided=sub,max_depth=a.value),indent=2))
 def freqarr(self,ids):
  f=collections.Counter();[f.update(self.freq[i]) for i in ids];return (C.c_uint32*540)(*(f[g] for g in range(540)))
 def replay(self,cb):
  L=self.L;t=Tex();L.init19(C.byref(t));uploads={};u=UP(lambda ctx,s,p:uploads.__setitem__(s,C.string_at(p,4608)));peak=0;records=[]
  for r in self.route:
   f=self.freqarr(r['ids']);L.refreshhost19(C.byref(t),self.idx,f,cb,None,u,None);groups=[g for g in range(540) if f[g]];peak=max(peak,len(groups));self.assertEqual(t.missing,0);self.assertEqual(t.failed,0)
   for g in groups:self.assertEqual(uploads[t.map[g]],self.groupdata[g]);self.assertEqual(t.slots[t.map[g]],g)
   records.append({'reads':t.reads,'needed':len(groups),'resident':sum(g>=0 for g in t.slots)})
  return dict(peak_needed=peak,total_texture_reads=t.reads,records=records)
 def test_route(self):
  r=self.replay(self.good);(P/'tex_route19.json').write_text(json.dumps(r,indent=2));print('texture route',r['peak_needed'],r['total_texture_reads'])
 def test_route_disc_mock(self):
  L=self.L;L.mock17_setup(self.disc,self.n,0);self.assertEqual(L.cd17_init(),1);buf=C.create_string_buffer(2048);p=(C.c_uint32*2)();e=(C.c_uint32*2)();self.assertEqual(L.cd17_read(None,16,1,buf),1);self.assertEqual(L.iso17_pvd(buf,p),1);self.assertEqual(L.cd17_read(None,p[1],1,buf),1);self.assertEqual(L.iso17_find(buf,b'HUBTEX.DAT;1',p[0],e),1);cb=CB(lambda ctx,lba,n,dst:L.cd17_read(None,e[0]+lba,n,dst));self.replay(cb)
 def test_eviction_and_corruption(self):
  t=Tex();L=self.L;L.init19(C.byref(t));u=UP(lambda *_:None);g=[x[0] for x in self.entries];f=(C.c_uint32*540)();
  for x in g[:64]:f[x]=1
  L.refreshhost19(C.byref(t),self.idx,f,self.good,None,u,None);self.assertEqual(t.reads,64);before=list(t.slots);f[g[0]]=0;f[g[64]]=3;bad=CB(lambda ctx,lba,n,dst:(C.memset(dst,0,n*2048),1)[1]);L.refreshhost19(C.byref(t),self.idx,f,bad,None,u,None);self.assertEqual(list(t.slots),before);self.assertEqual(t.failed,1);self.assertEqual(t.missing,1);L.refreshhost19(C.byref(t),self.idx,f,self.good,None,u,None);self.assertEqual(t.map[g[0]],-1);self.assertGreaterEqual(t.map[g[64]],0);self.assertEqual(t.missing,0)
 def test_overcapacity(self):
  t=Tex();self.L.init19(C.byref(t));u=UP(lambda *_:None);f=(C.c_uint32*540)();g=[x[0] for x in self.entries];
  for i,x in enumerate(g):f[x]=i+1
  self.L.refreshhost19(C.byref(t),self.idx,f,self.good,None,u,None);self.assertEqual(t.missing,77);self.assertEqual(set(t.slots),set(g[-64:]));self.assertEqual(t.reads,64)
 def test_disc(self):
  self.assertIn(b'ETD_TEX.EXE;1',self.disc[21*2352+24:21*2352+2072]);self.assertIn(b'ETD_WALK.EXE;1',self.disc[20*2352+24:20*2352+2072]);
  for i in range(self.n):s=self.disc[i*2352:(i+1)*2352];self.assertEqual(s,raw(i,s[24:2072]))
  self.assertGreater(json.loads((P/'report.json').read_text())['headroom_to_stack_region'],200000)
if __name__=='__main__':unittest.main()
