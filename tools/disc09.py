"""Minimal ISO9660 + CD-ROM XA Mode 2 Form 1 diagnostic disc.
No Sony license/security data. Test with an emulator or authorized homebrew loader.
"""
import argparse,struct,math,json
from pathlib import Path
SECTOR=2048

def both16(v):return struct.pack('<H',v)+struct.pack('>H',v)
def both32(v):return struct.pack('<I',v)+struct.pack('>I',v)
def record(name,lba,length,flags=0):
 n=34+len(name)-1+(len(name)%2==0);b=bytearray(n);b[0]=n;b[2:10]=both32(lba);b[10:18]=both32(length);b[18:25]=bytes([126,11,25,0,0,0,0]);b[25]=flags;b[28:32]=both16(1);b[32]=len(name);b[33:33+len(name)]=name;return b

def iso(exe):
 config=b'BOOT = cdrom:\\ETD_VIS.EXE;1\r\nTCB = 4\r\nEVENT = 10\r\nSTACK = 801FFF00\r\n';total=max(300,22+math.ceil(len(exe)/SECTOR));s=[bytearray(SECTOR) for _ in range(total)];p=s[16];p[:7]=b'\x01CD001\x01';p[8:40]=b'PLAYSTATION'.ljust(32);p[40:72]=b'ETD_PSX_DIAGNOSTIC'.ljust(32);p[80:88]=both32(total);p[120:124]=both16(1);p[124:128]=both16(1);p[128:132]=both16(SECTOR);p[132:140]=both32(10);p[140:144]=struct.pack('<I',18);p[148:152]=struct.pack('>I',19);p[156:190]=record(b'\0',20,SECTOR,2);p[190:813]=b' '*623
 for off in [813,830,847]:p[off:off+17]=b'2026112500000000\0'
 p[864:881]=b'0000000000000000\0';p[881]=1;s[17][:7]=b'\xffCD001\x01';s[18][:10]=b'\x01\0'+struct.pack('<IH',20,1)+b'\0\0';s[19][:10]=b'\x01\0'+struct.pack('>IH',20,1)+b'\0\0';root=record(b'\0',20,SECTOR,2)+record(b'\x01',20,SECTOR,2)+record(b'ETD_VIS.EXE;1',22,len(exe))+record(b'SYSTEM.CNF;1',21,len(config));s[20][:len(root)]=root;s[21][:len(config)]=config
 for i in range(math.ceil(len(exe)/SECTOR)):
  chunk=exe[i*SECTOR:(i+1)*SECTOR];s[22+i][:len(chunk)]=chunk
 return s

EDC=[];F=[];B=[0]*256
for i in range(256):
 x=i
 for _ in range(8):x=(x>>1)^(0xd8018001 if x&1 else 0)
 EDC.append(x);j=(i<<1)^(0x11d if i&128 else 0);F.append(j);B[i^j]=i

def edc(buf):
 x=0
 for b in buf:x=(x>>8)^EDC[(x^b)&255]
 return x

def ecc(src,major,minor,mult,inc):
 size=major*minor;out=bytearray(major*2)
 for m in range(major):
  idx=(m>>1)*mult+(m&1);a=b=0
  for _ in range(minor):
   x=src[idx];idx=(idx+inc)%size;a^=x;b^=x;a=F[a]
  a=B[F[a]^b];out[m]=a;out[m+major]=a^b
 return out

def bcd(x):return ((x//10)<<4)|(x%10)
def raw(lba,data):
 b=bytearray(2352);b[:12]=b'\0'+b'\xff'*10+b'\0';t=lba+150;addr=bytes([bcd(t//4500),bcd(t//75%60),bcd(t%75),2]);b[16:24]=b'\0\0\x08\0'*2;b[24:2072]=data;b[2072:2076]=struct.pack('<I',edc(b[16:2072]));b[2076:2248]=ecc(b[12:2076],86,24,2,86);b[2248:2352]=ecc(b[12:2248],52,43,86,88);b[12:16]=addr;return b

def build(out):
 e=(out/'ETD_VIS.EXE').read_bytes();s=iso(e);(out/'ETD_PSX_M09.bin').write_bytes(b''.join(raw(i,x) for i,x in enumerate(s)));(out/'ETD_PSX_M09.cue').write_text('FILE "ETD_PSX_M09.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n');return len(s)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('out',type=Path);print('sectors:',build(p.parse_args().out))
