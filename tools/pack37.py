"""Lossless four-value zigzag bit packing for local animation banks.
Each group stores a 4-bit width followed by four unsigned zigzag values.
Frames are independently byte padded. Rig checkpoints use identity prediction;
intervening frames use previous-frame prediction. No source asset bytes committed.
"""
from pathlib import Path
import re,json
import numpy as np
R=Path(__file__).resolve().parents[1]; OLD=R/'build_m36/play'; A=R/'assets_m37'; STRIDE=8

def encode(values):
    vals=[int(x) for x in values]; vals+= [0]*(-len(vals)%4)
    stream=bytearray(); acc=bits=0
    def put(v,n):
        nonlocal acc,bits
        acc|=v<<bits; bits+=n
        while bits>=8:
            stream.append(acc&255);acc>>=8;bits-=8
    for i in range(0,len(vals),4):
        z=[2*x if x>=0 else -2*x-1 for x in vals[i:i+4]]
        width=max(z).bit_length(); assert width<=15
        put(width,4)
        for v in z:put(v,width)
    if bits:stream.append(acc)
    return bytes(stream)

def decode(data,n):
    acc=bits=pos=0; out=[]
    def get(k):
        nonlocal acc,bits,pos
        while bits<k:acc|=data[pos]<<bits;bits+=8;pos+=1
        v=acc&((1<<k)-1);acc>>=k;bits-=k;return v
    for i in range(0,n,4):
        w=get(4)
        for j in range(4):
            v=get(w);out.append((v>>1)^-(v&1))
    return np.array(out[:n],dtype=np.int32)

def flat(v):return ',\n'.join(','.join(map(str,v[i:i+32])) for i in range(0,len(v),32))
def pack_frames(rows):
    data=bytearray(); offsets=[0]
    for r in rows:
        b=encode(r); assert np.array_equal(decode(b,len(r)),r)
        data.extend(b);offsets.append(len(data))
    return data,offsets

def arrays(name,data,off):
    return f'static const unsigned int {name}_off[]={{\n{flat(off)}\n}};\nstatic const unsigned char {name}_bits[]={{\n{flat(data)}\n}};\n'

def build():
    A.mkdir(exist_ok=True); s=(OLD/'rig11_data.h').read_text(); old=np.load(R/'build_m11/play/rig.npz')['matrices'].reshape(245,-1).astype(np.int32)
    # Decode the actual v36 stream independently and require exact equality to recovered matrix source.
    off=list(map(int,re.findall(r'\d+',re.search(r'rig_offsets[^=]*=\{(.*?)\};',s,re.S)[1])));raw=bytes(map(int,re.findall(r'\d+',re.search(r'rig_stream[^=]*=\{(.*?)\};',s,re.S)[1])))
    row=None
    for i in range(len(old)):
        b=raw[off[i]:off[i+1]]
        if i%STRIDE==0:row=np.frombuffer(b,dtype='<i2').astype(np.int32)
        else:
            j=k=0
            while j<len(row):
                t=b[k];k+=1
                if t==0x80:row[j]=int.from_bytes(b[k:k+2],'little',signed=True);k+=2;j+=1
                elif t==0x81:j+=b[k];k+=1
                else:row[j]+=t if t<128 else t-256;j+=1
            assert k==len(b)
        assert np.array_equal(row,old[i])
    delta=old.copy();delta[1:]-=old[:-1];base=np.tile([4096,0,0,0,0,4096,0,0,0,0,4096,0],43);delta[::STRIDE]=old[::STRIDE]-base
    data,o=pack_frames(delta);prefix=s[:s.index('static const u32 rig_offsets')];(A/'rig37_data.h').write_text(prefix+arrays('rig37',data,o))
    q=np.load(R/'assets_m36/poses.npz');h='/* Generated locally; exact v0.36 NPC deltas. */\n'; stats=[]
    for i in range(3):
        d=q[f'delta{i}'].reshape(12,-1);qd,qo=pack_frames(d);h+=arrays(f'quest37_{i}',qd,qo);stats.append(dict(model=i,values=d.size,old_bytes=d.nbytes,new_bytes=len(qd)+len(qo)*4))
    h+='static const unsigned char * const qbits37[]={quest37_0_bits,quest37_1_bits,quest37_2_bits};\nstatic const unsigned int * const qoffs37[]={quest37_0_off,quest37_1_off,quest37_2_off};\n'
    h+='static const int qperiod36'+(OLD/'questanim36.h').read_text().split('static const int qperiod36',1)[1]
    h+='static const int qnv37[]={'+','.join(str(q[f'delta{i}'].shape[1]) for i in range(3))+'};\n'
    (A/'questpack37.h').write_text(h)
    report=dict(rig_frames=len(old),rig_words=old.shape[1],checkpoint_stride=STRIDE,rig_old_bytes=len(raw)+len(off)*4,rig_new_bytes=len(data)+len(o)*4,npc_poses=36,npcs=stats,npc_cache_bytes=3*2*1539,rig_cache_unchanged=True)
    (A/'report.json').write_text(json.dumps(report,indent=2));print(report)
if __name__=='__main__':build()
