import sys,unittest,struct,hashlib,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from cnk import entries,vag_info,find_refs
class Tests(unittest.TestCase):
    def test_cnk_bounds(self):
        b=struct.pack('<8I',1,1,0,1,5,32,4,2)+b'test'
        self.assertEqual(list(entries(b)),[(0,5,32,4,2)])
        with self.assertRaises(ValueError):list(entries(b[:-1]))
    def test_vag(self):
        b=b'VAGp'+struct.pack('>IIII',32,0,16,22050)+bytes(12)+b'test'+bytes(12)+bytes(16)
        self.assertEqual(vag_info(b)['adpcm_bytes'],16); self.assertIsNone(vag_info(b[:-1]))
    def test_refs(self):self.assertEqual(list(find_refs(b'"spyro.mrb" aaaa.PXT')), [b'spyro.mrb',b'aaaa.PXT'])
    def test_reports(self):
        p=Path(__file__).resolve().parents[1]/'reports/summary.json'; s=json.loads(p.read_text());self.assertEqual(s['records'],sum(s['kinds'].values()));self.assertEqual(s['containers'],len(s['details']))
if __name__=='__main__':unittest.main()
