import tempfile, unittest, zipfile
from pathlib import Path
from tools import recover48 as r, disc16 as d

class Recovery(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
    def m37(self,raw=False):
        assets={k:('fixture '+k).encode() for k in r.DISC_BANKS if k!='ETD_PACK.EXE'}
        s=d.iso(b'fixture exe',assets);s[20][:]=b'\0'*2048
        root=d.record(b'\0',20,2048,2)+d.record(b'\1',20,2048,2)+d.record(b'ETD_PACK.EXE;1',22,11)
        for i,(k,v) in enumerate(assets.items()):root+=d.record((k+';1').encode(),23+i,len(v))
        s[20][:len(root)]=root
        p=self.root/('renamed.bin' if raw else 'renamed.iso');p.write_bytes(b''.join(d.raw(i,b) if raw else b for i,b in enumerate(s)));return p,assets
    def test_recover_m37(self):
        p,assets=self.m37();out=self.root/'recovered';report=r.extract(p,out);self.assertEqual(report['missing_disc_banks'],[])
        for k,v in assets.items():self.assertEqual((out/k).read_bytes(),v)
        self.assertEqual((out/'ETD_PACK.EXE').read_bytes(),b'fixture exe')
    def test_raw_sectors(self):
        p,_=self.m37(True);self.assertEqual(r.scan([p])[0]['type'],'m37_compatible_disc')
        self.assertEqual(len(r.extract(p,self.root/'raw')['files']),16)
    def test_ps2_tree(self):
        s=d.iso(b'fixture',{});s[20][:]=bytes(2048)
        root=d.record(b'\0',20,2048,2)+d.record(b'\1',20,2048,2)+d.record(b'SLUS_203.15;1',23,3)+d.record(b'SPYRODAT',24,2048,2)
        sub=d.record(b'\0',24,2048,2)+d.record(b'\1',20,2048,2)+d.record(b'CHUNKS',25,2048,2)
        nested=d.record(b'\0',25,2048,2)+d.record(b'\1',24,2048,2)+d.record(b'TEST.CNK;1',26,5)
        for l,b in [(20,root),(24,sub),(25,nested),(23,b'ELF'),(26,b'chunk')]:s[l][:len(b)]=b
        p=self.root/'ps2.iso';p.write_bytes(b''.join(s));out=self.root/'ps2out';report=r.extract(p,out)
        self.assertEqual(report['type'],'ps2_etd_candidate');self.assertEqual((out/'SPYRODAT/CHUNKS/TEST.CNK').read_bytes(),b'chunk')
    def test_invalid_extent(self):
        p,_=self.m37();b=bytearray(p.read_bytes());b[20*2048+2:20*2048+10]=d.both32(999999);p.write_bytes(b)
        with self.assertRaises(ValueError):r.extract(p,self.root/'bad')
        self.assertFalse((self.root/'bad').exists())
    def test_refuse_other_disc(self):
        p=self.root/'other.iso';p.write_bytes(b''.join(d.iso(b'test',{})))
        with self.assertRaises(ValueError):r.extract(p,self.root/'bad')
    def test_no_overwrite(self):
        p,_=self.m37();out=self.root/'exists';out.mkdir()
        with self.assertRaises(ValueError):r.extract(p,out)
    def test_zip_inventory(self):
        p=self.root/'renamed.zip'
        with zipfile.ZipFile(p,'w') as z:z.writestr('prefix/build_m36/play/play36.c','fixture');z.writestr('disc.bin','fixture')
        a=r.scan([p])[0];self.assertEqual(a['source_inputs'],['build_m36/play/play36.c']);self.assertEqual(a['disc_members'],['disc.bin'])
    def test_unsafe_directory(self):
        s=d.iso(b'x',{});s[20][:]=bytes(2048);rr=d.record(b'../BAD;1',23,1);s[20][:len(rr)]=rr
        p=self.root/'bad.iso';p.write_bytes(b''.join(s));self.assertEqual(r.scan([p])[0]['type'],'unreadable_or_non_disc')
if __name__=='__main__':unittest.main()
