import struct,tempfile,unittest
from pathlib import Path
import numpy as np
from tools import classic_mesh50 as m

def meta(name='terrainShape',bbox=(0,0,0,10,0,10),count=1):
    n=name.encode();q=20+len(n);b=bytearray(q+88);struct.pack_into('<I',b,0,2724436415);struct.pack_into('<I',b,8,len(n));b[12:12+len(n)]=n;struct.pack_into('<6f',b,q,*bbox);struct.pack_into('<IHHI',b,q+76,0,0,count,0x12345678);return bytes(b)

def geom(uvshift=0,bad=False):
    b=bytearray(500);p=22;b[p+1:p+8]=m.SIG;b[p+8:p+10]=bytes([4,0x78]);struct.pack_into('<12f',b,p+10,0,0,0,10,0,0,0,0,10,10,0,10);q=p+10+48;b[q+7:q+14]=m.NORMAL;f=130;b[f:f+9]=m.STRIP;b[f+9:f+25]=bytes([4,11 if bad else 12]+[0]*14);u=160;b[u:u+9]=m.UV;struct.pack_into('<8f',b,u+9,uvshift,0,1,0,0,1,1,1);return bytes(b)

def cnk(*payload):
    b=bytearray(struct.pack('<4I',1,1,0,len(payload)));off=16+16*len(payload)
    for i,p in enumerate(payload):b.extend(struct.pack('<4I',i,off,len(p),0));off+=len(p)
    return bytes(b)+b''.join(payload)

class Mesh(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.p=self.root/'L_TEST.CNK'
    def runmesh(self,*payload,partial=False):self.p.write_bytes(cnk(*payload));return m.recover(self.p,0,'terrain',self.root/'out',partial)
    def test_exact(self):
        r=self.runmesh(meta(),geom());self.assertTrue(r['exported']);self.assertEqual((r['vertices'],r['triangles']),(4,2));a=np.load(self.root/'out/geometry.npz');self.assertEqual(a['faces'].tolist(),[[0,1,2],[2,1,3]]);self.assertEqual(a['material'].tolist(),[0x12345678]*2)
    def test_duplicate_candidates(self):self.assertTrue(self.runmesh(meta(),geom(),geom())['exported'])
    def test_ambiguous(self):self.assertFalse(self.runmesh(meta(),geom(),geom(.5))['exported']);self.assertFalse((self.root/'out/geometry.npz').exists())
    def test_bounds(self):self.assertFalse(self.runmesh(meta(bbox=(0,0,0,9,0,10)),geom())['exported'])
    def test_malformed_strip(self):self.assertFalse(self.runmesh(meta(),geom(bad=True))['exported'])
    def test_missing_packet(self):self.assertFalse(self.runmesh(meta(count=2),geom())['exported'])
    def test_partial(self):
        r=self.runmesh(meta()+meta('terrainOther',bbox=(0,0,0,9,0,10)),geom(),partial=True);self.assertTrue(r['exported']);self.assertEqual(len(r['unmatched']),1)
    def test_inventory(self):
        self.p.write_bytes(cnk(meta(),geom()));a=m.inventory(self.root);self.assertEqual(a[0]['metadata_candidates'][0]['names'],['terrainShape'])
    def test_bad_cnk(self):
        with self.assertRaises(ValueError):m.records(cnk(meta())[:-1])
    def test_no_overwrite(self):
        self.runmesh(meta(),geom())
        with self.assertRaises(FileExistsError):m.recover(self.p,0,'terrain',self.root/'out')
if __name__=='__main__':unittest.main()
