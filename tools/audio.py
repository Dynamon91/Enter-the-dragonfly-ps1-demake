"""Extract and decode a VAG record from your own source ISO for auditioning."""
import argparse,struct,wave
from pathlib import Path
from cnk import ISO,entries,vag_info
COEF=((0,0),(60,0),(115,-52),(98,-55),(122,-60))
def decode(data):
    v=vag_info(data)
    if not v:raise ValueError('Invalid VAG header')
    pcm=[];h1=h2=0;flags=[]
    for off in range(48,48+v['adpcm_bytes'],16):
        block=data[off:off+16];filt=block[0]>>4;shift=block[0]&15;flags.append(block[1]);
        if filt>=len(COEF) or shift>12:raise ValueError(f'Unsupported ADPCM block at {off}: filter {filt}, shift {shift}')
        a,b=COEF[filt]
        for byte in block[2:]:
            for nib in (byte&15,byte>>4):
                signed=nib-16 if nib>=8 else nib
                s=((signed<<12)>>shift)+((h1*a+h2*b+32)>>6);s=max(-32768,min(32767,s));pcm.append(s);h2,h1=h1,s
    return v,pcm,flags
def main(iso,container,index,out):
    with ISO(iso) as d:
        b=d.file(container); i,h,o,n,t=next(x for x in entries(b) if x[0]==index);v,pcm,flags=decode(b[o:o+n])
        out.parent.mkdir(parents=True,exist_ok=True)
        with wave.open(str(out),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(v['rate']);w.writeframes(struct.pack('<'+'h'*len(pcm),*pcm))
        print(v,'decoded samples',len(pcm),'flag values',sorted(set(flags)))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('iso',type=Path);p.add_argument('container');p.add_argument('index',type=int);p.add_argument('out',type=Path);a=p.parse_args();main(a.iso,a.container,a.index,a.out)
