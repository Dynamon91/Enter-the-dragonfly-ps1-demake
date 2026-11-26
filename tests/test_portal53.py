import ctypes as C, unittest, subprocess
from pathlib import Path
import test_scene52 as base

class Progress(C.Structure):
    _fields_=[('caught',base.B*15),('mode',base.B),('count',base.B),('bosses',base.B),('visited',base.U)]
class Spawn(C.Structure):
    _fields_=[(n,C.c_int) for n in ('x','y','z','heading')]

class Portal(base.Tests):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        p=Path(cls.tmp.name)/'portal.so'
        subprocess.run(['gcc','-O2','-shared','-fPIC','-fsanitize=undefined',*[str(base.ROOT/'src'/n) for n in ('portal53.c','scene52.c','sector27.c')],'-o',str(p)],check=True)
        cls.lib=C.CDLL(str(p));cls.lib.scene52_open.argtypes=[C.POINTER(base.Scene),base.P,base.U,base.U,base.U,base.U];cls.lib.scene52_init.argtypes=[C.POINTER(base.Cache),base.P,base.P];cls.lib.scene52_switch.argtypes=[C.POINTER(base.Cache),C.POINTER(base.Scene),C.c_int,C.c_int,base.READ,C.c_void_p]
        cls.lib.portal53_gate.argtypes=[C.POINTER(Progress),C.c_int,C.c_int,C.c_int]
        cls.lib.portal53_enter.argtypes=[C.POINTER(base.Cache),C.POINTER(Progress),C.POINTER(base.Scene),C.POINTER(Spawn),C.c_int,base.READ,C.c_void_p,C.POINTER(Spawn)]
    def setUp(self):
        super().setUp();self.progress=Progress();self.spawn=Spawn(0,-3,5,16);self.out=Spawn(99,99,99,99)
    def flies(self,n):
        self.progress.count=n
        for i in range(15):self.progress.caught[i]=0
        for i in range(n):self.progress.caught[i//8]|=1<<(i%8)
    def gate(self,a,b,pct=0):return self.lib.portal53_gate(C.byref(self.progress),a,b,pct)
    def enter(self,s,data,spawn=None,pct=0,fail=-1):
        self.reads=0
        @base.READ
        def reader(_,lba,n,dst):
            self.reads+=1
            if self.reads==fail or (lba+n)*2048>len(data):return 0
            C.memmove(dst,data[lba*2048:(lba+n)*2048],n*2048);return 1
        return self.lib.portal53_enter(C.byref(self.cache),C.byref(self.progress),C.byref(s),C.byref(spawn or self.spawn),pct,reader,None,C.byref(self.out))
    def boot(self):
        s,d,_=self.bank(0);self.assertEqual(self.enter(s,d),0);self.assertEqual(self.progress.visited,1);return s,d
    def frozen(self):return self.snap(),bytes(self.progress),bytes(self.out)
    def test_portal_all_thresholds(self):
        for i,n in enumerate((1,6,15,25,35,45,55,65),1):
            self.flies(n-1);self.assertEqual(self.gate(0,i),2)
            self.flies(n);self.assertEqual(self.gate(0,i),0)
    def test_portal_routes(self):
        self.flies(90);self.assertEqual(self.gate(-1,0),0);self.assertEqual(self.gate(-1,1),3);self.assertEqual(self.gate(1,2),3);self.assertEqual(self.gate(2,0),0);self.assertEqual(self.gate(0,0),3);self.assertEqual(self.gate(9,0),0)
    def test_portal_ripto(self):
        self.flies(90);self.assertEqual(self.gate(0,9,69),2);self.assertEqual(self.gate(0,9,70),0);self.assertEqual(self.gate(0,9,101),1)
    def test_portal_ledger(self):
        self.flies(90);self.progress.caught[11]|=4;self.assertEqual(self.gate(0,1),1);self.progress.caught[11]&=~4;self.progress.count=89;self.assertEqual(self.gate(0,1),1);self.flies(90);self.progress.mode=1;self.assertEqual(self.gate(0,1),1)
    def test_portal_boot_return(self):
        hub,hd=self.boot();self.flies(6);s,d,_=self.bank(2,3);self.assertEqual(self.enter(s,d,Spawn(0,0,5,32)),0);self.assertEqual((self.out.y,self.out.heading),(-3,32));self.assertEqual(self.progress.visited,5);self.assertEqual(self.enter(hub,hd),0);self.assertEqual(self.progress.visited,5)
    def test_portal_locked_no_reads(self):
        self.boot();s,d,_=self.bank(2);before=self.frozen();self.assertEqual(self.enter(s,d),2);self.assertEqual(self.reads,0);self.assertEqual(self.frozen(),before)
    def test_portal_no_floor(self):
        self.boot();self.flies(6);s,d,_=self.bank(2);before=self.frozen();self.assertEqual(self.enter(s,d,Spawn(0,-3,100,16)),5);self.assertGreater(self.reads,0);self.assertEqual(self.frozen(),before)
    def test_portal_height(self):
        self.boot();self.flies(6);s,d,_=self.bank(2);before=self.frozen();self.assertEqual(self.enter(s,d,Spawn(0,108,5,16)),5);self.assertEqual(self.frozen(),before);self.assertEqual(self.enter(s,d,Spawn(0,107,5,16)),0);self.assertEqual(self.out.y,-3)
    def test_portal_corrupt(self):
        self.boot();self.flies(6);s,d,_=self.bank(2);bad=bytearray(d);bad[64]^=1;before=self.frozen();self.assertEqual(self.enter(s,bytes(bad)),4);self.assertEqual(self.frozen(),before)
    def test_portal_read_failure(self):
        self.boot();self.flies(6);s,d,_=self.bank(2,repeat=2000);before=self.frozen();self.assertEqual(self.enter(s,d,fail=2),4);self.assertEqual(self.reads,2);self.assertEqual(self.frozen(),before)
    def test_portal_boss_no_reward(self):
        hub,hd=self.boot();self.flies(90);s,d,_=self.bank(9);self.assertEqual(self.enter(s,d,pct=70),0);self.assertEqual(self.progress.bosses,0);self.assertEqual(self.progress.visited,1);self.assertEqual(self.enter(hub,hd,pct=70),0)
    def test_portal_bad_spawn(self):
        self.boot();self.flies(6);s,d,_=self.bank(2);before=self.frozen();self.assertEqual(self.enter(s,d,Spawn(0,-3,5,64)),1);self.assertEqual(self.reads,0);self.assertEqual(self.frozen(),before)

# Run only newly defined portal cases; base tests are separately discovered.
for _name in list(vars(base.Tests)):
    if _name.startswith('test_'):setattr(Portal,_name,None)
# unittest considers callable test attributes only.
if __name__=='__main__':unittest.main()
