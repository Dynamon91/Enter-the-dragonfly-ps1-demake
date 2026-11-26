"""Combine up to eight validated 2x XA streams into one channel-filtered bank.
Raw sectors only; ISO directory placement and CD playback control are separate.
"""
import argparse, hashlib, json, struct
from contextlib import ExitStack
from pathlib import Path
try:
    from . import xa46 as x
except ImportError:
    import xa46 as x

def digest(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def validate_meta(path,m):
    if not isinstance(m,dict):raise ValueError('metadata must be an object')
    for k in ('sample_rate','channels','source_frames','padding_frames','audio_sectors','physical_sectors','first_lba','file','channel','interleave'):
        if type(m.get(k)) is not int:raise ValueError('invalid metadata '+k)
    n=m['audio_sectors'];a=m['first_lba'];frames=m['source_frames'];pad=m['padding_frames']
    if (m['sample_rate'],m['channels'],m['interleave'])!=(x.RATE,2,8) or n<1 or m['physical_sectors']!=n*8 or frames<1 or not 0<=pad<x.FRAMES or frames+pad!=n*x.FRAMES or not 1<=m['file']<=255 or not 0<=m['channel']<=31:raise ValueError('inconsistent stream metadata')
    x.address(a);x.address(a+n*8-1)
    loop=m.get('loop_frames')
    if loop is not None and (not isinstance(loop,list) or len(loop)!=2 or not all(type(v)is int for v in loop) or not 0<=loop[0]<loop[1]<=frames or any(v%x.FRAMES for v in loop)):raise ValueError('invalid source loop')
    if Path(path).stat().st_size!=n*8*2352 or digest(path)!=m.get('sha256'):raise ValueError('source length or SHA256 mismatch')

def pack(tracks,dest,start_lba=0):
    """tracks is [(raw_path, metadata), ...]; metadata output has absolute LBAs."""
    dest=Path(dest)
    if not 1<=len(tracks)<=8 or dest.exists() or any(Path(p).resolve()==dest.resolve() for p,_ in tracks):raise ValueError('need 1–8 tracks and a new output path')
    for p,m in tracks:validate_meta(p,m)
    groups=max(m['audio_sectors'] for _,m in tracks);x.address(start_lba);x.address(start_lba+groups*8-1)
    temp=dest.with_suffix(dest.suffix+'.partial')
    if temp.exists():raise ValueError('partial output already exists')
    info=[]
    for slot,(p,m) in enumerate(tracks):
        first=start_lba+slot;loop=m.get('loop_frames');n=m['audio_sectors']
        info.append(dict(source_sha256=m['sha256'],file=1,channel=slot,first_audio_lba=first,last_audio_lba=first+(n-1)*8,audio_sectors=n,source_frames=m['source_frames'],padding_frames=m['padding_frames'],loop_frames=loop,loop_start_lba=None if loop is None else first+loop[0]//x.FRAMES*8,loop_last_lba=None if loop is None else first+(loop[1]//x.FRAMES-1)*8))
    try:
        with ExitStack() as stack:
            ins=[stack.enter_context(Path(p).open('rb')) for p,_ in tracks];out=stack.enter_context(temp.open('xb'))
            for g in range(groups):
                for slot in range(8):
                    lba=start_lba+8*g+slot
                    if slot>=len(tracks) or g>=tracks[slot][1]['audio_sectors']:
                        out.write(x.filler(lba));continue
                    m=tracks[slot][1];src_lba=m['first_lba']+g*8;f=ins[slot];s=bytearray(f.read(2352))
                    if x.inspect_sector(s,src_lba)!='audio' or (s[16],s[17])!=(m['file'],m['channel']) or s[18]!=(0xe5 if g==m['audio_sectors']-1 else 0x64):raise ValueError('source audio routing or end flag mismatch')
                    for k in range(1,8):
                        if f.read(2352)!=x.filler(src_lba+k):raise ValueError('source filler mismatch')
                    s[12:16]=x.address(lba);s[16]=s[20]=1;s[17]=s[21]=slot;struct.pack_into('<I',s,2348,x.edc(s[16:2348]));x.inspect_sector(s,lba);out.write(s)
        temp.rename(dest)
    except BaseException:
        temp.unlink(missing_ok=True);raise
    return dict(sample_rate=x.RATE,channels_per_track=2,interleave=8,first_lba=start_lba,physical_sectors=groups*8,sha256=digest(dest),tracks=info)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);p.add_argument('--track',nargs=2,action='append',required=True,metavar=('BIN','JSON'));p.add_argument('--lba',type=int,default=0);a=p.parse_args()
    tracks=[(Path(b),json.loads(Path(j).read_text())) for b,j in a.track];print(json.dumps(pack(tracks,a.output,a.lba),indent=2))
if __name__=='__main__':main()
