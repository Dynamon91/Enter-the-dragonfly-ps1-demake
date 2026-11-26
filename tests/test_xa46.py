import hashlib, math, struct, tempfile, unittest, wave
from pathlib import Path
from tools import xa46 as x

class XA(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.wav=self.root/'source.wav';self.out=self.root/'track.bin'
    def source(self,n=2*x.FRAMES,rate=x.RATE,ch=2,silent=False):
        frames=[(0,0) if silent else (int(15000*math.sin(2*math.pi*441*i/rate)),int(6000*math.sin(2*math.pi*882*i/rate))) for i in range(n)]
        with wave.open(str(self.wav),'wb') as w:
            w.setparams((ch,2,rate,0,'NONE','not compressed'));w.writeframes(b''.join(struct.pack('<'+'h'*ch,*p[:ch]) for p in frames))
        return frames
    def test_roundtrip(self):
        src=self.source();m=x.encode(self.wav,self.out,120,7,3,[0,2*x.FRAMES]);data=self.out.read_bytes();hist=[(0,0),(0,0)];dec=[]
        self.assertEqual(len(data),16*2352);self.assertEqual(m['loop_end_lba_exclusive'],136)
        for i in range(16):
            s=data[i*2352:(i+1)*2352];self.assertEqual(x.inspect_sector(s,120+i),'audio' if i%8==0 else 'filler')
            if i%8==0:
                self.assertEqual((s[16],s[17]),(7,3));dec+=x.decode_sector(s,hist)
        self.assertEqual(len(dec),len(src));self.assertLess(m['decoded_rmse'],350);self.assertEqual(m['sha256'],hashlib.sha256(data).hexdigest());self.assertEqual(data[18],0x64);self.assertEqual(data[8*2352+18],0xe5)
        # distinct frequencies and amplitudes must remain in their original channels
        for ch in range(2):self.assertLess(sum((a[ch]-b[ch])**2 for a,b in zip(src,dec))/len(src),350**2)
    def test_padding(self):
        self.source(x.FRAMES+13);m=x.encode(self.wav,self.out);self.assertEqual(m['padding_frames'],x.FRAMES-13)
    def test_loop_no_rounding(self):
        self.source();self.assertRaises(ValueError,x.encode,self.wav,self.out,loop=[1,x.FRAMES]);self.assertFalse(self.out.exists())
    def test_loop_reset(self):
        self.source(3*x.FRAMES);x.encode(self.wav,self.out,loop=[x.FRAMES,3*x.FRAMES]);s=self.out.read_bytes()[8*2352:9*2352];self.assertEqual(s[28]>>4,0);self.assertEqual(s[29]>>4,0);a=x.decode_sector(s,[(0,0),(0,0)]);b=x.decode_sector(s,[(12000,-9000),(-20000,3000)]);self.assertEqual(a,b)
    def test_wrong_format(self):
        self.source(rate=44100);self.assertRaises(ValueError,x.encode,self.wav,self.out);self.source(ch=1);self.assertRaises(ValueError,x.encode,self.wav,self.out)
    def test_silence_and_partial_cleanup(self):
        self.source(silent=True);self.assertRaises(ValueError,x.encode,self.wav,self.out);self.assertFalse(self.out.exists());self.assertFalse(self.out.with_suffix('.bin.partial').exists())
    def test_truncated(self):
        self.source();self.wav.write_bytes(self.wav.read_bytes()[:-4]);self.assertRaises(ValueError,x.encode,self.wav,self.out);self.assertFalse(self.out.exists())
    def test_corruption(self):
        self.source();x.encode(self.wav,self.out);s=bytearray(self.out.read_bytes()[:2352]);s[42]^=1;self.assertRaises(ValueError,x.inspect_sector,s,0)
    def test_duplicate_header(self):
        self.source();x.encode(self.wav,self.out);s=bytearray(self.out.read_bytes()[:2352]);s[24]^=1;struct.pack_into('<I',s,2348,x.edc(s[16:2348]));self.assertRaises(ValueError,x.inspect_sector,s,0)
    def test_bad_address_and_filter(self):
        self.source();self.assertRaises(ValueError,x.encode,self.wav,self.out,start_lba=-1);self.assertRaises(ValueError,x.encode,self.wav,self.out,channel=32)
    def test_preserve_existing(self):
        self.source();self.out.write_bytes(b'keep');self.assertRaises(ValueError,x.encode,self.wav,self.out);self.assertEqual(self.out.read_bytes(),b'keep')
if __name__=='__main__':unittest.main()
