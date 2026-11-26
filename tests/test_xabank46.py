import math,struct,tempfile,unittest,wave
from pathlib import Path
from tools import xa46 as x,xabank46 as bank
class Bank(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.out=self.root/'bank.bin';self.tracks=[]
        for i,n in enumerate((2,3)):
            wav=self.root/f'{i}.wav';raw=self.root/f'{i}.bin'
            with wave.open(str(wav),'wb') as w:
                w.setparams((2,2,x.RATE,0,'NONE','not compressed'));w.writeframes(b''.join(struct.pack('<hh',int(8000*math.sin(j*(i+1)*.04)),int(5000*math.sin(j*.07))) for j in range(n*x.FRAMES)))
            self.tracks.append((raw,x.encode(wav,raw,start_lba=20+i*40,file_no=2+i,channel=3+i,loop=[0,n*x.FRAMES])))
    def test_mux(self):
        m=bank.pack(self.tracks,self.out,120);data=self.out.read_bytes();self.assertEqual(m['physical_sectors'],24);self.assertEqual(len(data),24*2352);self.assertEqual(m['tracks'][1]['loop_last_lba'],137)
        for i in range(24):
            s=data[i*2352:(i+1)*2352];slot=i%8;g=i//8
            if slot<2 and g<self.tracks[slot][1]['audio_sectors']:
                self.assertEqual(x.inspect_sector(s,120+i),'audio');self.assertEqual((s[16],s[17]),(1,slot));original=self.tracks[slot][0].read_bytes()[g*8*2352:g*8*2352+2352];self.assertEqual(s[24:2348],original[24:2348])
            else:self.assertEqual(s,x.filler(120+i))
    def test_reject_corruption(self):
        p,m=self.tracks[0];p.write_bytes(p.read_bytes()[:-1]);self.assertRaises(ValueError,bank.pack,self.tracks,self.out);self.assertFalse(self.out.exists())
    def test_reject_route(self):
        p,m=self.tracks[0];m['channel']=15;self.assertRaises(ValueError,bank.pack,self.tracks,self.out);self.assertFalse(self.out.exists());self.assertFalse(self.out.with_suffix('.bin.partial').exists())
    def test_preserve_existing(self):
        self.out.write_bytes(b'keep');self.assertRaises(ValueError,bank.pack,self.tracks,self.out);self.assertEqual(self.out.read_bytes(),b'keep')
if __name__=='__main__':unittest.main()
