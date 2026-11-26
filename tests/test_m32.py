"""Validate disc startup bank, unchanged assets and SPU upload lifetime."""
import ctypes as C,json,re,struct,subprocess,unittest,zlib
from pathlib import Path
from bootbank32 import ARRAYS
from disc16 import raw
R=Path(__file__).resolve().parents[1];P=R/'build_m32/play';OLD=R/'build_m31/play'
CB=C.CFUNCTYPE(C.c_int,C.c_void_p,C.c_uint32,C.c_uint32,C.c_void_p)
class M32(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.rep=json.loads((P/'bootbank32.json').read_text());cls.bank=(P/'BOOT32.DAT').read_bytes();cls.padded=cls.bank.ljust(cls.rep['padded'],b'\0')
  src='''typedef unsigned char U8;typedef unsigned int U32;typedef unsigned short u16;
typedef int (*Read18)(void*,U32,U32,U8*);
#include "startup32.h"
static const U8 *startup32;
static u16 regs[256],payload[26304];static U32 pos;static int overflow;
static void write32(int o,u16 v){regs[o/2]=v;if(o==0x1aa)regs[0x1ae/2]=v&0x3f;if(o==0x1a8){if(pos<26304)payload[pos++]=v;else overflow=1;}}
#define SPU_WRITE(o,v) write32(o,v)
#define SPU_READ(o) regs[(o)/2]
#define SPU_DELAY() do{}while(0)
#include "spu14.h"
int hostload(U8*d,U32 c,U32 l,U32 n,Read18 r,void*x){return bootload32(d,c,l,n,r,x);}
int hostspu(const U8*d){startup32=d;pos=0;overflow=0;int ok=sfx_init();startup32=0;return ok&&!overflow&&pos==26304;}
const u16 *hostpayload(void){return payload;}
int hostplay(void){sfx_play(2);sfx_stop();return sfx_ready;}
'''
  (P/'host32.c').write_text(src);subprocess.run(['clang','-O2','-shared','-fPIC','-I',str(P),'-I',str(R/'src'),str(P/'host32.c'),'-o',str(P/'host32.so')],check=True);cls.L=C.CDLL(str(P/'host32.so'));cls.L.hostload.argtypes=[C.c_void_p,C.c_uint32,C.c_uint32,C.c_uint32,CB,C.c_void_p];cls.L.hostspu.argtypes=[C.c_void_p];cls.L.hostpayload.restype=C.c_void_p
 def test_exact_original_arrays(self):
  self.assertEqual(zlib.crc32(self.bank),int(self.rep['crc32'],16));end=0
  for name,var,ctype,fmt in ARRAYS:
   m=re.search(rf'static const {ctype} {var}(?:\[[^\]]*\])+=\s*\{{(.*?)\}};',(OLD/name).read_text(),re.S);self.assertIsNotNone(m);vals=[int(x) for x in re.findall(r'\d+',m[1])];rawbytes=struct.pack('<'+fmt*len(vals),*vals);a=self.rep['arrays'][var];off=a['offset'];self.assertEqual(off%4,0);self.assertGreaterEqual(off,end);self.assertEqual(rawbytes,self.bank[off:off+a['bytes']]);self.assertEqual(zlib.crc32(rawbytes),int(a['crc32'],16));end=off+a['bytes']
  self.assertEqual(end,len(self.bank))
 def load(self,payload=None,fail=-1,cap=None,n=None,lba=500):
  payload=self.padded if payload is None else payload;calls=[];buf=C.create_string_buffer(len(self.padded)+32);C.memset(buf,0xAB,len(buf))
  def read(ctx,l,c,p):
   calls.append((l,c));off=(l-lba)*2048
   if len(calls)==fail:return 0
   self.assertTrue(0<c<=32);C.memmove(p,payload[off:off+c*2048],c*2048);return 1
  ok=self.L.hostload(buf,len(self.padded) if cap is None else cap,lba,len(self.bank) if n is None else n,CB(read),None);self.assertEqual(buf.raw[-32:],b'\xab'*32);return ok,calls,buf
 def test_bounded_transport(self):
  ok,calls,buf=self.load();self.assertTrue(ok);self.assertEqual(calls,[(500,32),(532,32),(564,13)]);self.assertEqual(buf.raw[:len(self.bank)],self.bank)
 def test_invalid_input_and_crc(self):
  for cap,n,lba in [(len(self.padded)-1,len(self.bank),500),(len(self.padded),len(self.bank)-1,500),(len(self.padded),len(self.bank),449800)]:
   ok,calls,_=self.load(cap=cap,n=n,lba=lba);self.assertFalse(ok);self.assertEqual(calls,[])
  for block in range(1,4):self.assertFalse(self.load(fail=block)[0])
  for pos in (0,75336,95328,len(self.bank)-1):
   damaged=bytearray(self.padded);damaged[pos]^=1;self.assertFalse(self.load(bytes(damaged))[0])
 def test_spu_upload_then_reuse(self):
  ok,_,buf=self.load();self.assertTrue(ok);self.assertTrue(self.L.hostspu(buf));a=self.rep['arrays']['sfx_bank'];self.assertEqual(C.string_at(self.L.hostpayload(),a['bytes']),self.bank[a['offset']:a['offset']+a['bytes']]);C.memset(buf,0x99,len(self.padded));self.assertTrue(self.L.hostplay());self.assertEqual(C.string_at(self.L.hostpayload(),a['bytes']),self.bank[a['offset']:a['offset']+a['bytes']])
 def test_link_and_lifetime(self):
  a=json.loads((P/'report32.json').read_text());b=json.loads((OLD/'report31.json').read_text());self.assertGreater(b['linked_ram_from_load']-a['linked_ram_from_load'],150000);self.assertGreater(a['headroom_to_stack_region'],190000)
  syms=subprocess.check_output(['nm',str(P/'play32.elf')],text=True).splitlines();names={s.split()[-1] for s in syms if s.split()};self.assertFalse(set(x[1] for x in ARRAYS)&names)
  s=(P/'play32.c').read_text().split('int main(void)')[1];self.assertLess(s.index('mount18()'),s.index('bootload32('));self.assertLess(s.index('bootload32('),s.index('startup32=(const U8*)cache.arena'));self.assertLess(s.index('sfx_init()'),s.index('startup32=0'));self.assertLess(s.index('startup32=0'),s.index('reset18(&p)'));self.assertNotIn('startup32',s.split('startup32=0')[1])
 def test_disc_and_fallback(self):
  d=(P/'ETD_PSX_M32.bin').read_bytes();root=d[20*2352+24:20*2352+2072];records={};i=0
  while root[i]:
   r=root[i:i+root[i]];records[r[33:33+r[32]].decode('ascii')]=struct.unpack_from('<I',r,2)[0],struct.unpack_from('<I',r,10)[0];i+=len(r)
  def extract(name):
   l,n=records[name+';1'];return b''.join(d[j*2352+24:j*2352+2072] for j in range(l,l+(n+2047)//2048))[:n]
  self.assertEqual(extract('BOOT32.DAT'),self.bank);self.assertEqual(extract('ETD_BOOT.EXE'),(P/'ETD_BOOT.EXE').read_bytes());self.assertEqual(extract('ETD_AI.EXE'),(OLD/'ETD_AI.EXE').read_bytes());self.assertIn(b'ETD_BOOT.EXE;1',extract('SYSTEM.CNF'))
  for n in ('DOJOSECT.DAT','DOJOSECT.IDX'):self.assertEqual(extract(n),(OLD/n).read_bytes())
  for i in range(len(d)//2352):s=d[i*2352:(i+1)*2352];self.assertEqual(s,raw(i,s[24:2072]))
if __name__=='__main__':unittest.main()
