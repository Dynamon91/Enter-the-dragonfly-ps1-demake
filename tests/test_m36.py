"""NPC animation and English conversation regression tests."""
from pathlib import Path
import ctypes as C, json,struct,unittest,subprocess,re,hashlib
import numpy as np
from disc16 import raw
R=Path(__file__).resolve().parents[1];P=R/'build_m36/play';A=R/'assets_m36';OLD=R/'build_m35/play'
class Dialog(C.Structure):_fields_=[('actor',C.c_int),('at',C.c_int),('count',C.c_int),('ids',C.c_int*3),('dooie_seen',C.c_int)]
class M36(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  s='''typedef unsigned char U8;typedef unsigned int u32;
#define Q34_ARRIVED 2
#include "dialogue_state36.h"
#include "dialogue36.h"
static Dialog36 dialog36;
static int pixels,bad;
static void rect(int x,int y,int w,int h,u32 c){if(x<5||y<159||x+w>315||y+h>235)bad++;pixels+=w*h;}
#include "dialogue_render36.h"
void reset36(Dialog36*d){dialog_reset36(d);}
void open36(Dialog36*d,int a,int s,int seen,int e,int reward){dialog_open36(d,a,s,seen,e,reward);}
void next36(Dialog36*d){dialog_next36(d);}
int id36(Dialog36*d){return dialog_id36(d);}
int frame36(int t,int talk,int p){return pose_index36(t,talk,p);}
const char* textid36(int i){return qtext36(i);}
int bounds36(Dialog36*d){dialog36=*d;pixels=bad=0;huddialog36();return bad? -bad:pixels;}
''';(P/'host36.c').write_text(s);subprocess.run(['clang','-shared','-fPIC','-O2','-I',str(R/'src'),'-I',str(P),str(P/'host36.c'),'-o',str(P/'host36.so')],check=True);L=cls.L=C.CDLL(str(P/'host36.so'));L.reset36.argtypes=[C.POINTER(Dialog)];L.open36.argtypes=[C.POINTER(Dialog)]+[C.c_int]*5;L.next36.argtypes=[C.POINTER(Dialog)];L.id36.argtypes=[C.POINTER(Dialog)];L.bounds36.argtypes=[C.POINTER(Dialog)];L.textid36.restype=C.c_char_p
 def test_all_source_clips(self):
  r=json.loads((A/'report.json').read_text());self.assertEqual(sum(len(x['clips']) for x in r['models']),18);self.assertEqual(sum(c['keys'] for x in r['models'] for c in x['clips']),10824);self.assertEqual([m['joints'] for m in r['models']],[30]*3);self.assertEqual(len({c['record'] for x in r['models'] for c in x['clips']}),18)
 def test_pose_deltas(self):
  z=np.load(A/'poses.npz');old=np.load(R/'assets_m35/questmodels.npz');h=(P/'questanim36.h').read_text()
  for i in range(3):
   a=z[f'frames{i}'];d=z[f'delta{i}'];self.assertEqual(a.shape,(12,len(old[f'v{i}']),3));self.assertTrue(np.array_equal(d.astype(np.int16)+old[f'v{i}'],a));self.assertLessEqual(np.max(abs(d)),43);self.assertGreater(np.count_nonzero(a[0]!=a[3]),20);self.assertGreater(np.count_nonzero(a[0]!=a[7]),20);x=re.search(r'qdelta36_'+str(i)+r'\[12\]\[\d+\]\[3\]=\{(.*?)\};',h,re.S);v=np.array(list(map(int,re.findall(r'-?\d+',x[1])))).reshape(a.shape);self.assertTrue(np.array_equal(v,d))
  for talk in (0,1):
   for t in range(180):self.assertEqual(self.L.frame36(t,talk,60),6*talk+(t%60)//10)
 def test_source_text(self):
  r=json.loads((A/'dialogue_report.json').read_text());self.assertEqual(r['source_record'],83);self.assertEqual([x['name'] for x in r['actors']],['Rusty','RJ','Dougy']);self.assertEqual(len(r['lines']),18)
  for id,x in r['lines'].items():
   self.assertEqual(self.L.textid36(int(id)).decode(),x['wrapped']);self.assertEqual(' '.join(x['wrapped'].split()),' '.join(x['text'].split()));self.assertLessEqual(max(map(len,x['wrapped'].splitlines())),48);self.assertLessEqual(len(x['wrapped'].splitlines()),5)
 def test_conversations(self):
  d=Dialog();self.L.reset36(C.byref(d));self.assertEqual(d.actor,-1)
  def check(actor,stage,seen,event,reward,expected):
   self.L.open36(C.byref(d),actor,stage,seen,event,reward);got=[]
   while d.actor>=0:
    got.append(self.L.id36(C.byref(d)));self.assertGreater(self.L.bounds36(C.byref(d)),0);self.L.next36(C.byref(d))
   self.assertEqual(got,expected)
  for i,(g,h,t,o,c) in enumerate([(430,431,432,467,468),(420,421,428,423,422),(426,427,422,0,466)]):
   check(i,0,0,2,0,[g,h]);check(i,1,1,2,0,[h]);check(i,2,1,6,0,[t]+([o] if o else []));check(i,2,1,14,1,[t,418]);check(i,3,1,2,1,[c])
  check(2,3,1,2,1,[465]);self.L.reset36(C.byref(d));check(2,3,1,2,1,[466]);check(-1,0,0,2,0,[]);check(0,0,0,0,0,[])
 def test_disc_and_native(self):
  b=(P/'ETD_PSX_M36.bin').read_bytes();self.assertIn(b'ETD_TALK.EXE;1',b[21*2352+24:21*2352+2072]);root=b[20*2352+24:20*2352+2072];files={};i=0
  while root[i]:
   rr=root[i:i+root[i]];l,n=struct.unpack_from('<I',rr,2)[0],struct.unpack_from('<I',rr,10)[0];files[rr[33:33+rr[32]].decode()]=b''.join(b[j*2352+24:j*2352+2072] for j in range(l,l+(n+2047)//2048))[:n];i+=len(rr)
  for n in ('QMOD35.DAT','BOOT32.DAT','DOJOSECT.IDX','DOJOSECT.DAT','ETD_NPCS.EXE'):self.assertEqual(files[n+';1'],(OLD/n).read_bytes())
  self.assertEqual(files['ETD_TALK.EXE;1'],(P/'ETD_TALK.EXE').read_bytes());self.assertGreater(json.loads((P/'report36.json').read_text())['headroom_to_stack_region'],32768)
  for i in range(len(b)//2352):s=b[i*2352:(i+1)*2352];self.assertEqual(s,raw(i,s[24:2072]))
 def test_native_wiring(self):
  s=(P/'play36.c').read_text();self.assertIn('dialog_open36(&dialog36',s);self.assertIn('dialog_next36(&dialog36)',s);self.assertIn('if(modal){',s);self.assertIn('qdelta36[id]+f0*m->nv*3',s);self.assertIn('huddialog36();idle()',s);self.assertIn('quest_step34(&quest34',s)
if __name__=='__main__':unittest.main()
