import math, struct, tempfile, unittest, wave
from pathlib import Path
from tools import spu49 as s
class Test(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.p=Path(self.tmp.name)/'a.wav'
 def wav(self,n=2800,rate=22050,ch=1,silent=False):
  v=[0 if silent else int(14000*math.sin(i*.13)) for i in range(n)]
  with wave.open(str(self.p),'wb') as w:w.setparams((ch,2,rate,0,'NONE',''));w.writeframes(struct.pack('<%dh'%(n*ch),*[x for a in v for x in [a]*ch]))
  return v
 def test_roundtrip(self):
  self.wav();d,m=s.encode(self.p);self.assertEqual(m['pitch'],2048);self.assertLess(m['rmse'],250);self.assertEqual(len(d),1616);self.assertEqual(d[-15],7);self.assertEqual(d[-31],1);self.assertEqual(len(s.vag(d,m['rate'])),len(d)+48)
 def test_loop(self):
  self.wav();d,m=s.encode(self.p,28);self.assertEqual(d[17],6);self.assertEqual(d[16]>>4,0);self.assertEqual(d[-15],3);self.assertEqual(len(d),1600)
 def test_one_block_loop(self):
  self.wav(28);d,_=s.encode(self.p,0);self.assertEqual(d[1],7)
 def test_padding(self):
  self.wav(29);d,m=s.encode(self.p);self.assertEqual(m['padding'],27);self.assertEqual(len(d),48)
 def test_loop_alignment(self):
  self.wav(29);self.assertRaises(ValueError,s.encode,self.p,0);self.wav();self.assertRaises(ValueError,s.encode,self.p,1)
 def test_bad_format(self):
  self.wav(ch=2);self.assertRaises(ValueError,s.encode,self.p);self.wav(rate=48000);self.assertRaises(ValueError,s.encode,self.p)
 def test_silent_truncated(self):
  self.wav(silent=True);self.assertRaises(ValueError,s.encode,self.p);self.wav();self.p.write_bytes(self.p.read_bytes()[:-2]);self.assertRaises(ValueError,s.encode,self.p)
 def test_bank(self):
  self.wav();b,m=s.pack([('voice',self.p,None),('effect',self.p,0)]);self.assertEqual(m[0]['address'],s.BASE);self.assertEqual(m[1]['address'],s.BASE+m[0]['bytes']);self.assertEqual(len(b)%64,0);self.assertRaises(ValueError,s.pack,[('dup',self.p,None),('dup',self.p,None)])
 def test_capacity(self):
  from unittest.mock import patch
  with patch.object(s,'encode',return_value=(bytes(s.LIMIT-s.BASE),{})):
   self.assertRaises(ValueError,s.pack,[('a',self.p,None),('b',self.p,None)])
 def test_header_corrupt(self):
  self.assertRaises(ValueError,s.decode,bytes([0x50,0])+bytes(14));self.assertRaises(ValueError,s.decode,b'x')
if __name__=='__main__':unittest.main()
