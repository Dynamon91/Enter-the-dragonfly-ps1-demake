"""Lossless checkpoint/delta compression of v0.10 Q12 matrix palettes."""
import argparse, json
from pathlib import Path
import numpy as np
STRIDE=8

def pack(out):
    z=np.load(out/'rig.npz'); m=z['matrices'].reshape(len(z['matrices']),-1).astype(np.int32)
    stream=bytearray(); offsets=[]
    for i,row in enumerate(m):
        offsets.append(len(stream))
        if i%STRIDE==0:
            stream.extend(row.astype('<i2').tobytes()); continue
        d=row-m[i-1]; j=0
        while j<len(row):
            if d[j]==0:
                k=j+1
                while k<len(row) and d[k]==0 and k-j<255:k+=1
                stream.extend((0x81,k-j)); j=k; continue
            if -126<=d[j]<=127:
                stream.append(int(d[j])&255)
            else:
                stream.append(0x80);stream.extend(int(row[j]).to_bytes(2,'little',signed=True))
            j+=1
    offsets.append(len(stream))
    def rows(a):return ',\n'.join('{'+','.join(map(str,r))+'}' for r in a)
    def flat(a):return ',\n'.join(','.join(map(str,a[i:i+32])) for i in range(0,len(a),32))
    clips=json.loads((out/'rig_report.json').read_text())['clips']
    (out/'rig11_data.h').write_text(f'#define BONE_COUNT 43\n#define ANIM_COUNT {len(clips)}\n#define ANIM_FRAMES {len(m)}\n#define RIG_STRIDE {STRIDE}\n#define RIG_WORDS {m.shape[1]}\nstatic const unsigned char skinbones[NV][4]={{\n'+rows(z['bones'])+'};\nstatic const u16 skinweights[NV][4]={\n'+rows(z['weights'])+'};\nstatic const u16 animclips[ANIM_COUNT][2]={\n'+rows([[c['start'],c['frames']] for c in clips])+'};\nstatic const u32 rig_offsets[ANIM_FRAMES+1]={\n'+flat(offsets)+'};\nstatic const unsigned char rig_stream[]={\n'+flat(stream)+'};\n')
    report=dict(raw_bytes=m.size*2,stream_bytes=len(stream),offset_bytes=len(offsets)*4,cache_bytes=2*(m.shape[1]*2+4),stride=STRIDE,frames=len(m));report['net_saved_bytes']=report['raw_bytes']-report['stream_bytes']-report['offset_bytes']-report['cache_bytes'];(out/'rig_pack_report.json').write_text(json.dumps(report,indent=2));print(report)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('out',type=Path);pack(p.parse_args().out)
