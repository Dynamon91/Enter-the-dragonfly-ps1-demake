import ctypes as C,struct,json,unittest,sys,zlib,collections
from pathlib import Path
from test_m18 import Cache,CB
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'build_m20/play';A=ROOT/'assets_m16';B=ROOT/'assets_m20';sys.path.insert(0,str(ROOT/'tools'))
from disc16 import raw
class Collect(C.Structure):_fields_=[('taken',C.c_ubyte*290),('score',C.c_int),('tick',C.c_int),('sx',C.c_int),('sy',C.c_int),('sz',C.c_int),('target',C.c_int),('events',C.c_int),('assist',C.c_int)]
class M20(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.L=C.CDLL(str(P/'collect20_host.so'));L=cls.L;cls.idx=(A/'HUBSECT.IDX').read_bytes();cls.dat=(A/'HUBSECT.DAT').read_bytes();cls.man=json.loads((A/'sector_manifest.json').read_text());cls.gems=sorted((x['record_offset'],x['value']) for x in cls.man['objects'] if x['kind']==1);cls.route=json.loads((P/'route18.json').read_text());cls.good=CB(lambda ctx,lba,n,p:(C.memmove(p,cls.dat[lba*2048:(lba+n)*2048],n*2048),1)[1]);L.cache18_update.argtypes=[C.POINTER(Cache),C.c_char_p,C.c_uint32,C.c_uint32,C.c_int,C.c_int,CB,C.c_void_p];L.reset20.argtypes=[C.POINTER(Collect),C.c_int,C.c_int,C.c_int];L.step20.argtypes=[C.POINTER(Collect),C.POINTER(Cache),C.c_int,C.c_int,C.c_int,C.c_int];L.award20.argtypes=[C.POINTER(Collect),C.c_int,C.c_int]
 def move(self,w,x,z):return self.L.cache18_update(C.byref(w),self.idx,len(self.idx),len(self.dat)//2048,x,z,self.good,None)
 def init(self):w=Cache();c=Collect();self.L.cache18_init(C.byref(w));self.L.reset20(C.byref(c),36848,800,-1200);return w,c
 def test_all_source_ids(self):
  ids=[]
  for b in self.man['blocks']:
   off=b['lba']*2048+64+b['render']*36+b['collision']*24
   for j in range(b['objects']):
    x,y,z,k,v,_,id=struct.unpack_from('<3h3HI',self.dat,off+16*j)
    if k==1:ids.append((id,v));self.assertEqual(self.L.id20(id),self.gems.index((id,v)))
  self.assertEqual(sorted(ids),self.gems);self.assertEqual(sum(v for _,v in ids),773);self.assertEqual(self.L.id20(0),-1)
 def test_award_once_and_reset(self):
  w,c=self.init()
  for i,(_,v) in enumerate(self.gems):self.L.award20(C.byref(c),i,v+1);self.L.award20(C.byref(c),i,v);self.L.award20(C.byref(c),i,v)
  self.assertEqual(c.score,773);self.assertEqual(sum(c.taken),290);self.L.reset20(C.byref(c),0,0,0);self.assertEqual(c.score,0);self.assertFalse(any(c.taken))
 def test_route_and_revisit(self):
  w,c=self.init();records=[]
  for r in self.route:
   self.assertTrue(self.move(w,r['x'],r['z']));self.L.step20(C.byref(c),C.byref(w),r['x'],r['y'],r['z'],48);records.append(dict(score=c.score,sparx=[c.sx,c.sy,c.sz],taken=[self.gems[i][0] for i,v in enumerate(c.taken) if v],events=c.events,assist=c.assist,tick=c.tick))
  self.assertEqual(c.score,2);self.assertEqual(sum(c.taken),1);before=bytes(c.taken)
  for r in reversed(self.route):self.assertTrue(self.move(w,r['x'],r['z']));self.L.step20(C.byref(c),C.byref(w),r['x'],r['y'],r['z'],16)
  self.assertEqual(c.score,2);self.assertEqual(bytes(c.taken),before);(P/'collect_route20.json').write_text(json.dumps(records,indent=2));print('route pickup',[(i,r['score'],r['assist']) for i,r in enumerate(records) if r['events']])
 def test_assist_and_no_cache(self):
  w,c=self.init();self.L.step20(C.byref(c),C.byref(w),36500,800,-1200,48);self.assertEqual(c.score,0);self.assertTrue(self.move(w,36728,-1200));self.L.reset20(C.byref(c),36728,800,-1200)
  for _ in range(30):self.L.step20(C.byref(c),C.byref(w),36728,800,-1200,48)
  self.assertEqual(c.score,2);self.assertEqual(sum(c.taken),1)
 def test_selective_alpha(self):
  old=(A/'HUBTEX.DAT').read_bytes();new=(B/'HUBTEX.DAT').read_bytes();idx=(B/'HUBTEX.IDX').read_bytes();changed=[]
  for i in range(141):
   g,lba,crc=struct.unpack_from('<III',idx,12+12*i);p=lba*2048;self.assertEqual(zlib.crc32(new[p+24:p+4632]),crc);self.assertEqual(new[p+536:p+4632],old[p+536:p+4632]);
   if old[p:p+6144]!=new[p:p+6144]:changed.append(g);pal=struct.unpack_from('<256H',new,p+24);n=sum(pal[v]==0 for v in new[p+536:p+4632]);self.assertGreater(n,0);self.assertLess(n,4096)
  self.assertEqual(set(changed),{84,292,359})
 def test_updated_texture_bank_native_validator(self):
  lib=C.CDLL(str(P/'tex19_host.so'));idx=(B/'HUBTEX.IDX').read_bytes();dat=(B/'HUBTEX.DAT').read_bytes();self.assertEqual(lib.validate19(idx,len(idx),len(dat)//2048),1)
  for i in range(141):
   g,lba,crc=struct.unpack_from('<III',idx,12+12*i);self.assertEqual(lib.block19(dat[lba*2048:(lba+3)*2048],idx[12+12*i:24+12*i]),1)
 def test_disc(self):
  d=(P/'ETD_PSX_M20.bin').read_bytes();self.assertIn(b'ETD_GEM.EXE;1',d[21*2352+24:21*2352+2072]);self.assertIn(b'ETD_TEX.EXE;1',d[20*2352+24:20*2352+2072]);self.assertGreater(json.loads((P/'report.json').read_text())['headroom_to_stack_region'],180000)
  for i in range(len(d)//2352):s=d[i*2352:(i+1)*2352];self.assertEqual(s,raw(i,s[24:2072]))
