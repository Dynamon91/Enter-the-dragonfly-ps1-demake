"""Mono PCM -> PS1 SPU ADPCM. Keep original master; no resampling/downmix."""
import argparse, hashlib, json, math, struct, wave
from pathlib import Path
FILTERS=((0,0),(60,0),(115,-52),(98,-55),(122,-60))
BASE=0x1000; LIMIT=0x70000; MAX_SAMPLES=512

def clamp(v,lo,hi):return max(lo,min(hi,v))

def block(samples,hist,flags=0,reset=False):
    best=None
    for f,(a,b) in enumerate(FILTERS):
        if reset and f:break
        h,k=hist;peak=0
        for s in samples:
            peak=max(peak,abs(s-((a*h+b*k+32)>>6)));h,k=s,h
        shift=clamp(12-max(0,(max(1,(peak+6)//7)-1).bit_length()),0,12)
        for sh in range(max(0,shift-2),min(12,shift+1)+1):
            step=1<<(12-sh);h,k=hist;err=0;codes=[]
            for s in samples:
                pred=(a*h+b*k+32)>>6;q=clamp((s-pred+step//2)//step,-8,7)
                y=clamp(pred+q*step,-32768,32767);h,k=y,h;err+=(s-y)**2;codes.append(q&15)
            if best is None or err<best[0]:best=(err,f<<4|sh,codes,(h,k))
    _,header,codes,h=best
    return bytes([header,flags]+[codes[i]|codes[i+1]<<4 for i in range(0,28,2)]),h

def decode(data):
    if not data or len(data)%16:raise ValueError('invalid ADPCM length')
    h=k=0;out=[]
    for i in range(0,len(data),16):
        b=data[i:i+16];f,sh=b[0]>>4,b[0]&15
        if f>4 or sh>12 or b[1]>7:raise ValueError('invalid ADPCM header')
        a,c=FILTERS[f]
        for v in b[2:]:
            for n in (v&15,v>>4):
                n=n-16 if n>=8 else n;y=clamp((n<<(12-sh))+((a*h+c*k+32)>>6),-32768,32767);h,k=y,h;out.append(y)
    return out

def encode(path,loop=None):
    with wave.open(str(path),'rb') as w:
        n,rate=w.getnframes(),w.getframerate()
        if w.getnchannels()!=1 or w.getsampwidth()!=2 or not 8000<=rate<=44100 or not 0<n<=((LIMIT-BASE)//16-1)*28:raise ValueError('expected bounded mono PCM16 8–44.1 kHz')
        raw=w.readframes(n)
        if len(raw)!=2*n:raise ValueError('truncated PCM')
    pcm=list(struct.unpack('<%dh'%n,raw))
    if not any(pcm):raise ValueError('silent source')
    if loop is not None and (type(loop) is not int or not 0<=loop<n or loop%28 or n%28):raise ValueError('loop must start on a 28-frame boundary and end at exact EOF')
    pad=(-n)%28;pcm.extend([0]*pad);out=bytearray();h=(0,0)
    for i in range(0,len(pcm),28):
        last=i+28==len(pcm);flags=0
        if loop is not None and i>=loop:flags=2|(4 if i==loop else 0)|(1 if last else 0)
        elif last:flags=1
        b,h=block(pcm[i:i+28],h,flags,i==0 or i==loop);out.extend(b)
    # one-shot terminal dummy; end without repeat mutes envelope on SPU
    if loop is None:out.extend(bytes([0,7])+bytes(14))
    dec=decode(out)[:n];rmse=math.sqrt(sum((a-b)**2 for a,b in zip(pcm,dec))/n)
    return bytes(out),dict(rate=rate,frames=n,padding=pad,loop=loop,pitch=(rate*4096+22050)//44100,rmse=round(rmse,3),source_sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest())

def vag(data,rate,name='ETD49'):
    return struct.pack('>4sIII I 12s16s',b'VAGp',0x20,0,len(data),rate,bytes(12),name.encode('ascii')[:16].ljust(16,b'\0'))+data

def pack(entries):
    if not 1<=len(entries)<=MAX_SAMPLES:raise ValueError('invalid sample count')
    blob=bytearray();index=[];seen=set()
    for name,path,loop in entries:
        if not isinstance(name,str) or not name or name in seen:raise ValueError('invalid or duplicate name')
        seen.add(name);data,m=encode(path,loop);addr=BASE+len(blob)
        if addr+len(data)>LIMIT:raise ValueError('SPU bank exceeds reserved RAM window')
        index.append(dict(name=name,address=addr,bytes=len(data),**m));blob.extend(data)
    # Manual upload chunks of 64 bytes; zero padding not indexed.
    blob.extend(bytes((-len(blob))%64))
    if BASE+len(blob)>LIMIT:raise ValueError('SPU bank padding exceeds RAM window')
    return bytes(blob),index

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('manifest',type=Path);p.add_argument('out',type=Path);a=p.parse_args()
    items=json.loads(a.manifest.read_text());blob,index=pack([(v['name'],a.manifest.parent/v['wav'],v.get('loop')) for v in items]);a.out.mkdir(exist_ok=False,parents=True)
    (a.out/'SFX49.DAT').write_bytes(blob);(a.out/'SFX49.json').write_text(json.dumps(index,indent=2)+'\n')
    (a.out/'SFX49.IDX').write_bytes(b'SFX9'+struct.pack('<I',len(index))+b''.join(struct.pack('<5I',m['address'],m['bytes'],m['pitch'],m['frames'],0xffffffff if m['loop'] is None else m['loop']) for m in index))
    print(f'{len(index)} samples, {len(blob)} bytes of {LIMIT-BASE} budget')
if __name__=='__main__':main()
