import ctypes as C, struct, subprocess, zlib, unittest
from pathlib import Path
import numpy as np
import test_portal53 as portal
import test_scene52 as base
from tools import classic_sector51 as packer
B,U,P=base.B,base.U,base.P
UPLOAD=C.CFUNCTYPE(None,C.c_void_p,C.c_int,P)
class Tex(C.Structure):
    _fields_=[('idx',P),('len',U),('sectors',U),('material_groups',C.POINTER(C.c_short)),('materials',U)]
class State(C.Structure):
    _fields_=[('slots',C.c_short*64),('map',C.c_short*540),('count',U),('level',C.c_int)]
class Texture(portal.Portal):
    @classmethod
    def setUpClass(cls):
        super().setUpClass();p=Path(cls.tmp.name)/'tex54.so'
        subprocess.run(['gcc','-O2','-shared','-fPIC','-fsanitize=undefined',*[str(base.ROOT/'src'/n) for n in ('texture54.c','portal53.c','scene52.c','sector27.c')],'-o',str(p)],check=True)
        cls.lib=C.CDLL(str(p));cls.lib.scene52_open.argtypes=[C.POINTER(base.Scene),P,U,U,U,U];cls.lib.scene52_init.argtypes=[C.POINTER(base.Cache),P,P]
        cls.lib.transition54.argtypes=[C.POINTER(base.Cache),C.POINTER(portal.Progress),C.POINTER(State),C.POINTER(base.Scene),C.POINTER(Tex),C.POINTER(portal.Spawn),C.c_int,base.READ,C.c_void_p,base.READ,C.c_void_p,P,UPLOAD,C.c_void_p,C.POINTER(portal.Spawn)]
        cls.lib.texture54_validate.argtypes=[C.POINTER(Tex)]
    def setUp(self):
        super().setUp();self.state=State();self.state.level=-1;self.scratch=(B*6144)();self.vram={};self.uploads=[];self.texreads=0
    def textures(self,groups,mapping,seed=1):
        raw=bytearray();idx=bytearray(struct.pack('<4sHHI',b'ETTI',1,12,len(groups)))
        for i,g in enumerate(groups):
            p=bytes([(g+seed)%256])*4608;crc=zlib.crc32(p);idx.extend(struct.pack('<III',g,3*i,crc));raw.extend((struct.pack('<4sHHIIII',b'ETDT',1,g,64,64,4608,crc)+p).ljust(6144,b'\0'))
        ip=(B*len(idx)).from_buffer_copy(idx);mp=(C.c_short*len(mapping))(*mapping);self.refs.extend((ip,mp));return Tex(ip,len(idx),len(raw)//2048,mp,len(mapping)),bytes(raw),ip
    def scene(self,level,count=2,materials=2):
        v=np.array([[-20,3,0],[10,3,0],[10,3,30]],float);f=np.repeat([[0,1,2]],count,axis=0)
        g=dict(vertices=v,faces=f,uv=np.array([[0,0],[1,0],[1,1]]),material=np.arange(count)%materials);c=dict(vertices=v,faces=np.array([[0,1,2]]),flags=np.array([3]));cfg=dict(level=level,world_coordinates_reviewed=True,materials=[dict(id=i,status='resolved',hash=f'{i:x}') for i in range(materials)],objects=[])
        out=self.root/str(len(self.refs));packer.pack(g,c,cfg,out);data=(out/'LEVEL.DAT').read_bytes();raw=(out/'LEVEL.IDX').read_bytes();idx=(B*len(raw)).from_buffer_copy(raw);self.refs.append(idx);s=base.Scene();self.assertTrue(self.lib.scene52_open(C.byref(s),idx,len(idx),len(data)//2048,materials,level));return s,data
    def transition(self,s,data,t,texdata,fail=-1):
        self.reads=self.texreads=0;self.uploads=[]
        @base.READ
        def terrain(_,lba,n,dst):
            self.reads+=1
            if (lba+n)*2048>len(data):return 0
            C.memmove(dst,data[lba*2048:(lba+n)*2048],n*2048);return 1
        @base.READ
        def texture(_,lba,n,dst):
            self.texreads+=1
            if self.texreads==fail or (lba+n)*2048>len(texdata):return 0
            C.memmove(dst,texdata[lba*2048:(lba+n)*2048],n*2048);return 1
        @UPLOAD
        def upload(_,slot,p):
            self.uploads.append(slot);self.vram[slot]=C.string_at(p,4608)
        return self.lib.transition54(C.byref(self.cache),C.byref(self.progress),C.byref(self.state),C.byref(s),C.byref(t),C.byref(self.spawn),0,terrain,None,texture,None,self.scratch,upload,None,C.byref(self.out))
    def first(self):
        s,d=self.scene(0);t,b,_=self.textures([2,8],[2,8]);self.assertEqual(self.transition(s,d,t,b),0);self.assertEqual(self.uploads,[0,1]);self.assertEqual(self.vram[0],bytes([3])*4608);self.flies(6)
    def snapshot(self):return self.frozen(),bytes(self.state),dict(self.vram)
    def test_texture_new_scene(self):
        self.first();s,d=self.scene(2);t,b,_=self.textures([2,8],[2,8],seed=25);self.assertEqual(self.transition(s,d,t,b),0);self.assertEqual(self.state.level,2);self.assertEqual(self.vram[0],bytes([27])*4608);self.assertEqual(self.state.map[8],1);self.assertEqual(self.progress.visited,5)
    def test_texture_only_used(self):
        s,d=self.scene(0,count=1);t,b,_=self.textures([2,8],[2,8]);self.assertEqual(self.transition(s,d,t,b),0);self.assertEqual(self.texreads,1);self.assertEqual(self.state.map[8],-1)
    def test_texture_flat_explicit(self):
        s,d=self.scene(0);t,b,_=self.textures([],[-1,-1]);self.assertEqual(self.transition(s,d,t,b),0);self.assertEqual(self.state.count,0);self.assertEqual(self.texreads,0)
    def test_texture_missing_mapping(self):
        s,d=self.scene(0);t,b,_=self.textures([2],[2,8]);self.assertEqual(self.transition(s,d,t,b),6);self.assertEqual(self.reads,0)
    def test_texture_duplicate_index(self):
        t,_,_=self.textures([2,2],[2]);self.assertFalse(self.lib.texture54_validate(C.byref(t)))
    def test_texture_bad_extent(self):
        t,_,idx=self.textures([2,8],[2,8]);struct.pack_into('<I',idx,16,3);self.assertFalse(self.lib.texture54_validate(C.byref(t)))
    def test_texture_failure_rollback(self):
        self.first();before=self.snapshot();s,d=self.scene(2);t,b,_=self.textures([2,8],[2,8]);self.assertEqual(self.transition(s,d,t,b,fail=2),8);self.assertEqual(self.texreads,2);self.assertEqual(self.uploads,[]);self.assertEqual(before,self.snapshot())
    def test_texture_crc_rollback(self):
        self.first();before=self.snapshot();s,d=self.scene(2);t,b,_=self.textures([2,8],[2,8]);bad=bytearray(b);bad[6144+24]^=1;self.assertEqual(self.transition(s,d,t,bytes(bad)),8);self.assertEqual(self.uploads,[]);self.assertEqual(before,self.snapshot())
    def test_texture_slot_budget(self):
        s,d=self.scene(0,65,65);t,b,_=self.textures(list(range(65)),list(range(65)));self.assertEqual(self.transition(s,d,t,b),7);self.assertEqual(self.texreads,0);self.assertEqual(self.uploads,[])
    def test_texture_arena_budget(self):
        s,d=self.scene(0,12000,64);t,b,_=self.textures(list(range(64)),list(range(64)));self.assertEqual(self.transition(s,d,t,b),7);self.assertEqual(self.texreads,0);self.assertEqual(self.uploads,[])
    def test_texture_locked(self):
        self.first();self.flies(0);s,d=self.scene(2);t,b,_=self.textures([2,8],[2,8]);before=self.snapshot();self.assertEqual(self.transition(s,d,t,b),2);self.assertEqual(self.reads,0);self.assertEqual(self.texreads,0);self.assertEqual(before,self.snapshot())
    def test_texture_shared_group(self):
        s,d=self.scene(0);t,b,_=self.textures([2],[2,2]);self.assertEqual(self.transition(s,d,t,b),0);self.assertEqual(self.texreads,1);self.assertEqual(self.state.count,1)
for name in dir(portal.Portal):
    if name.startswith('test_'):setattr(Texture,name,None)
if __name__=='__main__':unittest.main()
