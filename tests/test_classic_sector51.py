import ctypes as C, struct, subprocess, tempfile, unittest
from pathlib import Path
import numpy as np
from tools import classic_sector51 as s
ROOT=Path(__file__).resolve().parents[1]
U=C.c_uint32; B=C.c_ubyte; PTR=C.POINTER(B)
READ=C.CFUNCTYPE(C.c_int,C.c_void_p,U,U,PTR)

class Sector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();p=Path(cls.tmp.name)/'reader.so'
        subprocess.run(['gcc','-shared','-fPIC','-O2',str(ROOT/'src/sector27.c'),'-o',str(p)],check=True)
        cls.lib=C.CDLL(str(p));cls.lib.sector16_load.argtypes=[PTR,U,U,U,U,U,U,PTR,U,READ,C.c_void_p,C.POINTER(U)]
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.out=Path(self.tmp.name)/'out'
        v=np.array([[-20,3,0],[10,3,0],[10,3,30],[2100,3,0],[2130,3,0],[2130,3,30]],dtype=float);f=np.array([[0,1,2],[3,4,5]])
        self.g=dict(vertices=v,faces=f,uv=np.array([[0,0],[1,0],[1,1]]*2),material=np.array([0xab,0xab]));self.c=dict(vertices=v.copy(),faces=f.copy(),flags=np.array([0,3]))
        self.cfg=dict(level=2,world_coordinates_reviewed=True,materials=[dict(id=0,status='resolved',hash='000000ab')],objects=[dict(kind=1,value=2,source_id=543,source_xyz=[-20,3,15])])
    def pack(self):return s.pack(self.g,self.c,self.cfg,self.out)
    def verify(self,rep,corrupt=False):
        idx=(self.out/'LEVEL.IDX').read_bytes();data=bytearray((self.out/'LEVEL.DAT').read_bytes());ib=(B*len(idx)).from_buffer_copy(idx);slot=(B*65536)();out=(U*7)(*([0xfeed]*7));rows=[]
        @READ
        def read(_,lba,n,dst):
            if (lba+n)*2048>len(data):return 0
            C.memmove(dst,bytes(data[lba*2048:(lba+n)*2048]),n*2048);return 1
        if corrupt:data[64]^=1
        for i in range(rep['blocks']):
            ok=self.lib.sector16_load(ib,len(idx),i,len(data)//2048,rep['materials'],rep['render'],rep['collision'],slot,len(slot),read,None,out)
            if corrupt and i==0:self.assertEqual(ok,0);self.assertEqual(list(out),[0xfeed]*7);return
            self.assertEqual(ok,1);self.assertEqual(out[0],i);org=tuple(C.c_int32(out[k]).value for k in (4,5,6));off=64
            for kind,n,stride in zip(range(3),out[1:4],s.STRIDES):
                for _ in range(n):
                    rec=bytes(slot[off:off+stride]);off+=stride;xyz=np.array(struct.unpack_from('<'+('h'* (3 if kind==2 else 9)),rec)).reshape(-1,3)+org
                    sid=struct.unpack_from('<I',rec,stride-4)[0];rows.append((kind,sid,xyz))
        for kind in (0,1):
            a=self.g if kind==0 else self.c;subset=sorted((sid,xyz) for k,sid,xyz in rows if k==kind)
            self.assertEqual([sid for sid,_ in subset],list(range(len(a['faces']))))
            for sid,xyz in subset:np.testing.assert_array_equal(xyz,np.rint(a['vertices'][a['faces'][sid]]*[1,-1,1]))
        self.assertEqual([sid for k,sid,_ in rows if k==2],[543])
    def test_native_roundtrip(self):self.verify(self.pack())
    def test_native_corruption(self):self.verify(self.pack(),True)
    def test_block_split(self):
        self.g['faces']=np.repeat(self.g['faces'][:1],4000,axis=0);self.g['material']=np.repeat(0xab,4000);r=self.pack();self.assertGreater(r['blocks'],2);self.assertLessEqual(r['max_block'],65536);self.verify(r)
    def test_peak_exact(self):
        r=self.pack();idx=(self.out/'LEVEL.IDX').read_bytes();e=[s.D.unpack_from(idx,16+i*60) for i in range(r['blocks'])];peak=count=0
        for x in range(-4096,6144,512):
            for z in range(-4096,4096,512):
                a=[v for v in e if v[7]<=x+256+1792 and v[10]>=x+256-1792 and v[9]<=z+256+1792 and v[12]>=z+256-1792];peak=max(peak,sum((v[2]+2047)//2048*2048 for v in a));count=max(count,len(a))
        self.assertEqual((peak,count),(r['peak_neighborhood_bytes'],r['peak_neighborhood_blocks']))
    def test_no_unreviewed(self):self.cfg['world_coordinates_reviewed']=False;self.assertRaises(ValueError,self.pack)
    def test_unresolved_material(self):self.g['material'][0]=0xcd;self.assertRaises(ValueError,self.pack)
    def test_bad_face(self):self.g['faces'][0,0]=-1;self.assertRaises(ValueError,self.pack)
    def test_unsupported_collision(self):self.c['flags'][0]=2;self.assertRaises(ValueError,self.pack)
    def test_duplicate_placement(self):self.cfg['objects']*=2;self.assertRaises(ValueError,self.pack)
    def test_quantization_collapse(self):self.g['vertices'][:3]*=.0001;self.assertRaises(ValueError,self.pack)
    def test_uv_repeat(self):self.g['uv']+=40;r=self.pack();self.assertEqual(r['uv_shifted'],2);self.verify(r)
    def test_uv_span(self):self.g['uv'][0,0]=100;self.assertRaises(ValueError,self.pack)
    def test_no_overwrite(self):self.pack();self.assertRaises(ValueError,self.pack)
    def test_no_expanded(self):self.cfg['level']=10;self.assertRaises(ValueError,self.pack)
if __name__=='__main__':unittest.main()
