import copy, math, struct, tempfile, unittest, wave
from pathlib import Path
from tools.asset_gate45 import audit, audit_wav, inventory, sha256, REVIEWS

class GateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.audio = self.root/'tone.wav'
        with wave.open(str(self.audio),'wb') as w:
            w.setparams((1,2,22050,0,'NONE','not compressed'))
            w.writeframes(b''.join(struct.pack('<h',int(2000*math.sin(i*math.pi/16))) for i in range(320)))
        (self.root/'data').write_bytes(b'test fixture, not a real PS1 asset')
        self.m = {'assets': []}
        for key,(kind,scope) in inventory().items():
            f = 'tone.wav' if kind in ('music','sfx') else 'data'
            self.m['assets'].append(dict(id=key,kind=kind,scope=scope,source='etd_retail',status='verified',source_ref='synthetic test fixture',input_path=f,input_sha256=sha256(self.root/f),output_path='data',output_sha256=sha256(self.root/'data'),reviews={r:True for r in REVIEWS[kind]},loop_frames=[0,320]))
    def check(self, mode='expanded'):
        return audit(self.m,self.root,mode)[0]
    def test_valid_fixture(self): self.assertEqual(self.check(),[])
    def test_missing_inventory(self):
        self.m['assets'].pop(); self.assertTrue(any('absent' in e for e in self.check()))
    def test_scope_relabel(self):
        self.m['assets'][0]['scope']='expanded'; self.assertTrue(self.check('classic'))
    def test_retail_replacement(self):
        self.m['assets'][0]['source']='fan_original';self.assertTrue(self.check())
    def test_unused_music_expanded_only(self):
        a=next(a for a in self.m['assets'] if a['scope']=='expanded' and a['kind']=='music');a['source']='etd_unused_music';self.assertFalse(self.check())
    def test_bad_donor_music(self):
        a=next(a for a in self.m['assets'] if a['scope']=='expanded' and a['kind']=='music');a['source']='spyro_ps1';self.assertTrue(self.check())
    def test_classic_independent(self):
        for a in self.m['assets']:
            if a['scope']=='expanded': a['status']='missing'
        self.assertFalse(self.check('classic'));self.assertTrue(self.check())
    def test_malformed_fields(self):
        self.m['assets'][0]['kind']=[]; self.assertTrue(self.check())
        self.m['assets'][0]['kind']='scene'; self.m['assets'][0]['source']={}; self.assertTrue(self.check())
    def test_bad_hash(self):
        self.m['assets'][0]['output_sha256']='0'*64;self.assertTrue(self.check())
    def test_bad_path(self):
        self.m['assets'][0]['input_path']='../outside';self.assertTrue(self.check())
    def test_duplicate(self):
        self.m['assets'].append(copy.deepcopy(self.m['assets'][0]));self.assertTrue(self.check())
    def test_missing_review(self):
        self.m['assets'][0]['reviews']={};self.assertTrue(self.check())
    def test_loop(self):
        a=next(a for a in self.m['assets'] if a['kind']=='music');a['loop_frames']=[0,321];self.assertTrue(self.check())
    def test_silence(self):
        with wave.open(str(self.audio),'wb') as w:
            w.setparams((1,2,22050,0,'NONE','not compressed'));w.writeframes(bytes(640))
        self.assertTrue(audit_wav(self.audio)[0])
    def test_truncated(self):
        self.audio.write_bytes(self.audio.read_bytes()[:-4]);self.assertTrue(audit_wav(self.audio)[0])
    def test_click_warning(self):
        with wave.open(str(self.audio),'wb') as w:
            w.setparams((1,2,22050,0,'NONE','not compressed'));w.writeframes(struct.pack('<hh',10000,-10000))
        e,w=audit_wav(self.audio,[0,2]);self.assertFalse(e);self.assertTrue(w)
if __name__=='__main__': unittest.main()
