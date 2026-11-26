import ctypes as C, struct, subprocess, tempfile, unittest
from pathlib import Path
import numpy as np
from tools import classic_sector51 as packer
ROOT=Path(__file__).resolve().parents[1]
U=C.c_uint32; B=C.c_ubyte; P=C.POINTER(B); SIZE=460*1024
READ=C.CFUNCTYPE(C.c_int,C.c_void_p,U,U,P)
class Scene(C.Structure):
    _fields_=[('idx',P)]+[(n,U) for n in 'len sectors materials render collision objects blocks level'.split()]
class Page(C.Structure):
    _fields_=[('count',U),('bytes',U),('id',U*28),('offset',U*28),('meta',(U*7)*28)]
class Cache(C.Structure):
    _fields_=[('pages',Page*2),('buf',P*2),('scene',Scene*2),('active',C.c_int)]
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();p=Path(cls.tmp.name)/'scene.so'
        subprocess.run(['gcc','-O2','-shared','-fPIC','-Wall','-Wextra',str(ROOT/'src/scene52.c'),str(ROOT/'src/sector27.c'),'-o',str(p)],check=True)
        cls.lib=C.CDLL(str(p));cls.lib.scene52_open.argtypes=[C.POINTER(Scene),P,U,U,U,U];cls.lib.scene52_init.argtypes=[C.POINTER(Cache),P,P];cls.lib.scene52_switch.argtypes=[C.POINTER(Cache),C.POINTER(Scene),C.c_int,C.c_int,READ,C.c_void_p]
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.cache=Cache();self.a=(B*SIZE)();self.b=(B*SIZE)();self.assertTrue(self.lib.scene52_init(C.byref(self.cache),self.a,self.b));self.refs=[];self.reads=0
    def bank(self,level,repeat=1,far=0):
        v=np.array([[-20,3,0],[10,3,0],[10,3,30],[2100+far,3,0],[2130+far,3,0],[2130+far,3,30]],float);f=np.array([[0,1,2],[3,4,5]])
        g=dict(vertices=v,faces=np.repeat(f,repeat,axis=0),uv=np.array([[0,0],[1,0],[1,1]]*2),material=np.repeat(0xab,2*repeat));c=dict(vertices=v,faces=f,flags=np.array([0,3]));cfg=dict(level=level,world_coordinates_reviewed=True,materials=[dict(id=0,status='resolved',hash='ab')],objects=[])
        out=self.root/str(len(self.refs));rep=packer.pack(g,c,cfg,out);data=(out/'LEVEL.DAT').read_bytes();raw=(out/'LEVEL.IDX').read_bytes();idx=(B*len(raw)).from_buffer_copy(raw);self.refs.append(idx);s=Scene();self.assertTrue(self.lib.scene52_open(C.byref(s),idx,len(idx),len(data)//2048,1,level));return s,data,idx
    def switch(self,s,data,x=0,z=0,fail=-1):
        self.reads=0
        @READ
        def reader(_,lba,n,dst):
            self.reads+=1
            if self.reads==fail or (lba+n)*2048>len(data):return 0
            C.memmove(dst,data[lba*2048:(lba+n)*2048],n*2048);return 1
        return self.lib.scene52_switch(C.byref(self.cache),C.byref(s),x,z,reader,None)
    def snap(self):
        c=self.cache;return c.active,bytes(c.pages[c.active]),bytes(c.scene[c.active]),C.string_at(c.buf[c.active],c.pages[c.active].bytes)
    def test_dynamic_scene_switch(self):
        a,d,_=self.bank(0);b,e,_=self.bank(2,repeat=3);self.assertTrue(self.switch(a,d));self.assertEqual(self.cache.scene[self.cache.active].render,2);self.assertTrue(self.switch(b,e,2100));self.assertEqual(self.cache.scene[self.cache.active].render,6);self.assertEqual(self.cache.scene[self.cache.active].level,2)
    def test_second_read_fails(self):
        a,d,_=self.bank(0);b,e,_=self.bank(2);self.assertTrue(self.switch(a,d));before=self.snap();self.assertFalse(self.switch(b,e,1000,fail=2));self.assertEqual(self.reads,2);self.assertEqual(before,self.snap())
    def test_corrupt_payload(self):
        a,d,_=self.bank(0);self.assertTrue(self.switch(a,d));before=self.snap();bad=bytearray(d);bad[64]^=1;self.assertFalse(self.switch(a,bytes(bad)));self.assertEqual(before,self.snap())
    def test_outside_scene(self):
        a,d,_=self.bank(0);self.assertFalse(self.switch(a,d,100000));self.assertEqual(self.reads,0);self.assertEqual(self.cache.active,-1)
    def test_bounds_overflow(self):
        a,d,idx=self.bank(0);struct.pack_into('<i',idx,16+28,-300000);self.assertFalse(self.switch(a,d));self.assertEqual(self.reads,0)
    def test_bad_extent(self):
        a,d,idx=self.bank(0);struct.pack_into('<I',idx,20,1);self.assertFalse(self.switch(a,d));self.assertEqual(self.reads,0)
    def test_budget(self):
        a,d,_=self.bank(2,repeat=7000);self.assertFalse(self.switch(a,d,1000));self.assertEqual(self.reads,0);self.assertEqual(self.cache.active,-1)
    def test_index_failure_no_publish(self):
        a,d,idx=self.bank(0);before=bytes(a);self.assertFalse(self.lib.scene52_open(C.byref(a),idx,len(idx)-1,len(d)//2048,1,0));self.assertEqual(bytes(a),before)
    def test_expanded_rejected(self):
        a,d,_=self.bank(0);a.level=10;self.assertFalse(self.switch(a,d));self.assertEqual(self.reads,0)
    def test_buffer_overlap(self):self.assertFalse(self.lib.scene52_init(C.byref(self.cache),self.a,self.a))
if __name__=='__main__':unittest.main()
