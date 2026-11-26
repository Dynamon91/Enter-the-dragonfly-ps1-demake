"""Encode local 37.8 kHz stereo PCM to PS1 CD-XA, 2x / 1:8 interleave.
Standalone raw sectors, not yet a mounted ISO or a playback driver.
No automatic resampling, cropping, normalization, or loop rounding.
"""
import argparse, hashlib, json, struct, wave
from pathlib import Path
try:
    from .disc16 import edc, raw, bcd
except ImportError:
    from disc16 import edc, raw, bcd

RATE = 37800
FRAMES = 2016
STRIDE = 8
FILTERS = ((0, 0), (60, 0), (115, -52), (98, -55))
SYNC = b'\0' + b'\xff'*10 + b'\0'

def clamp(n, lo, hi):
    return max(lo, min(hi, n))

def encode_unit(samples, hist, reset=False):
    """Choose predictor and quantizer by simulated closed-loop squared error."""
    assert len(samples) == 28
    best = None
    for f, (a,b) in enumerate(FILTERS):
        if reset and f: break
        h,k = hist
        peak = 0
        for s in samples:
            peak = max(peak, abs(s-((a*h+b*k+32)>>6)))
            h,k = s,h
        shift = clamp(12-max(0,(max(1,(peak+6)//7)-1).bit_length()),0,12)
        for sh in range(max(0,shift-2),min(12,shift+1)+1):
            step = 1 << (12-sh)
            h,k = hist; error = 0; codes = []
            for s in samples:
                pred = (a*h+b*k+32)>>6
                q = clamp((s-pred+step//2)//step,-8,7)
                y = clamp(pred+q*step,-32768,32767)
                codes.append(q&15); error += (s-y)**2; h,k = y,h
            if best is None or error < best[0]: best = error,(f<<4)|sh,codes,(h,k)
    return best[1:]

def encode_group(frames, histories, reset=False):
    assert len(frames) == 112
    out = bytearray(128)
    for block in range(4):
        for ch in range(2):
            unit=block*2+ch
            header,codes,histories[ch]=encode_unit([p[ch] for p in frames[block*28:(block+1)*28]],histories[ch],reset and block==0)
            out[4+unit]=header
            for j,q in enumerate(codes): out[16+j*4+block] |= q << (4*ch)
    out[:4]=out[4:8]; out[12:16]=out[8:12]
    return out

def address(lba):
    t=lba+150
    if not 0<=lba or t>=100*60*75: raise ValueError('LBA outside 2-digit BCD address range')
    return bytes((bcd(t//4500), bcd(t//75%60), bcd(t%75), 2))

def audio_sector(lba, frames, histories, file_no, channel, final=False, reset=False):
    out=bytearray(2352);out[:12]=SYNC;out[12:16]=address(lba)
    sub=bytes((file_no,channel,0x64|(0x81 if final else 0),1))
    out[16:24]=sub*2
    for g in range(18):out[24+128*g:24+128*(g+1)]=encode_group(frames[g*112:(g+1)*112],histories,reset and g==0)
    struct.pack_into('<I',out,2348,edc(out[16:2348]));return out

FILLER = bytes(raw(0, bytes(2048)))

def filler(lba):
    return FILLER[:12]+address(lba)+FILLER[16:]

def inspect_sector(s, lba):
    if len(s)!=2352 or s[:12]!=SYNC or s[12:16]!=address(lba) or s[16:20]!=s[20:24]: raise ValueError('sector header mismatch')
    if s[18]&0x20:
        if s[18] not in (0x64,0xe5) or s[19]!=1 or not 1<=s[16]<=255 or s[17]>31 or any(s[2328:2348]): raise ValueError('bad XA coding or padding')
        if struct.unpack_from('<I',s,2348)[0]!=edc(s[16:2348]):raise ValueError('bad XA EDC')
        for g in range(18):
            p=s[24+g*128:152+g*128]
            if p[:4]!=p[4:8] or p[8:12]!=p[12:16] or any(h>>4>3 or h&15>12 for h in p[:16]):raise ValueError('invalid XA sound group')
        return 'audio'
    if s!=raw(lba,s[24:2072]):raise ValueError('bad filler sector')
    return 'filler'

def decode_sector(s, histories):
    frames=[]
    for g in range(18):
        p=s[24+g*128:152+g*128]
        for block in range(4):
            pair=[]
            for ch in range(2):
                header=p[4+block*2+ch];a,b=FILTERS[header>>4];shift=12-(header&15);h,k=histories[ch];samples=[]
                for j in range(28):
                    n=(p[16+j*4+block]>>(4*ch))&15;n=n-16 if n>=8 else n
                    y=clamp((n<<shift)+((a*h+b*k+32)>>6),-32768,32767);samples.append(y);h,k=y,h
                histories[ch]=(h,k);pair.append(samples)
            frames.extend(zip(*pair))
    return frames

def encode(wav, dest, start_lba=0, file_no=1, channel=0, loop=None):
    """Create raw stream and return cue metadata. Exact loop positions only."""
    wav=Path(wav);dest=Path(dest)
    if wav.resolve()==dest.resolve() or dest.exists():raise ValueError('output exists or aliases input')
    if not 1<=file_no<=255 or not 0<=channel<=31:raise ValueError('invalid XA file/channel')
    with wave.open(str(wav),'rb') as w:
        n=w.getnframes()
        if (w.getframerate(),w.getnchannels(),w.getsampwidth())!=(RATE,2,2) or n<=0:raise ValueError('expected nonempty 37800 Hz stereo signed 16-bit PCM')
        sectors=(n+FRAMES-1)//FRAMES
        if loop is not None:
            if len(loop)!=2 or not all(type(x)is int for x in loop) or not 0<=loop[0]<loop[1]<=n or any(x%FRAMES for x in loop):raise ValueError('loop must be exact sector-aligned [start,end) frames')
        address(start_lba);address(start_lba+sectors*STRIDE-1)
        temp=dest.with_suffix(dest.suffix+'.partial')
        if temp.exists():raise ValueError('partial output already exists')
        h=[(0,0),(0,0)];dec=[(0,0),(0,0)];peak=err=0
        try:
            with temp.open('xb') as out:
                for i in range(sectors):
                    count=min(FRAMES,n-i*FRAMES);buf=w.readframes(count)
                    if len(buf)!=count*4:raise ValueError('truncated WAV')
                    frames=list(struct.iter_unpack('<hh',buf));peak=max(peak,max(abs(v) for p in frames for v in p));frames.extend([(0,0)]*(FRAMES-count))
                    lba=start_lba+i*STRIDE;s=audio_sector(lba,frames,h,file_no,channel,i==sectors-1,i==0 or (loop is not None and i*FRAMES==loop[0]))
                    inspect_sector(s,lba);decoded=decode_sector(s,dec)
                    err+=sum((a-b)**2 for p,q in zip(frames[:count],decoded[:count]) for a,b in zip(p,q));out.write(s)
                    for k in range(1,STRIDE):out.write(filler(lba+k))
            if not peak:raise ValueError('silent source')
            temp.rename(dest)
        except BaseException:
            temp.unlink(missing_ok=True);raise
    with dest.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
    return dict(sample_rate=RATE,channels=2,source_frames=n,padding_frames=sectors*FRAMES-n,audio_sectors=sectors,physical_sectors=sectors*STRIDE,first_lba=start_lba,file=file_no,channel=channel,interleave=STRIDE,loop_frames=loop,loop_start_lba=None if loop is None else start_lba+loop[0]//FRAMES*STRIDE,loop_end_lba_exclusive=None if loop is None else start_lba+loop[1]//FRAMES*STRIDE,decoded_rmse=round((err/(2*n))**0.5,3),sha256=digest)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('wav',type=Path);p.add_argument('output',type=Path);p.add_argument('--lba',type=int,default=0);p.add_argument('--file',type=int,default=1);p.add_argument('--channel',type=int,default=0);p.add_argument('--loop',nargs=2,type=int)
    a=p.parse_args();m=encode(a.wav,a.output,a.lba,a.file,a.channel,a.loop);print(json.dumps(m,indent=2))
if __name__=='__main__':main()
