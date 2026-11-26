"""Pack original English one-shot VAG payloads for PS1 SPU voice 8."""
import argparse,json,struct,zlib,hashlib
from pathlib import Path
from cnk import ISO,entries,vag_info

def build(iso,dialogue,out):
    with ISO(iso) as d:b=d.file('SPYRODAT/CHUNKS3/L_2_CC.CNK')
    r={i:b[o:o+s] for i,h,o,s,t in entries(b)};info=json.loads(dialogue.read_text());out.mkdir(exist_ok=False,parents=True);bank=bytearray();rows=[]
    for key,candidates in sorted(info['voice_candidates'].items(),key=lambda a:int(a[0])):
        if len(candidates)!=1:continue
        v=candidates[0];raw=r[v['record']];assert hashlib.sha256(raw).hexdigest()==v['sha256'];h=vag_info(raw);assert h and h['rate']==22050
        p=raw[48:48+h['adpcm_bytes']];flags=p[1::16];assert flags.count(1)==1;end=flags.index(1);assert not any(flags[:end]) and len(flags)-end<=2 and all(x in (0,7) for x in flags[end+1:]);p=p[:16*(end+1)];assert all(x>>4<=4 and x&15<=12 for x in p[::16]);p+=b'\x00\x07'+bytes(14);assert len(p)<=0x50000
        rows.append(dict(id=int(key),record=v['record'],lba=len(bank)//2048,bytes=len(p),crc=zlib.crc32(p),source_sha256=v['sha256'],audio_sha256=hashlib.sha256(p).hexdigest()));bank.extend(p);bank.extend(bytes((-len(bank))%2048))
    (out/'CCCVOX.DAT').write_bytes(bank);(out/'voicedata60.h').write_text('#define VOICE_BYTES60 %du\nstatic const VoiceEntry60 voices60[]={%s};\n'%(len(bank),','.join('{%d,%d,%d,%du}'%(x['id'],x['lba'],x['bytes'],x['crc']) for x in rows)));(out/'voice60.json').write_text(json.dumps(rows,indent=2)+'\n');print(len(rows),'voices',len(bank),'disc bytes',max(x['bytes'] for x in rows),'max SPU bytes')
if __name__=='__main__':
    p=argparse.ArgumentParser();[p.add_argument(x,type=Path) for x in ('iso','dialogue','out')];a=p.parse_args();build(a.iso,a.dialogue,a.out)
