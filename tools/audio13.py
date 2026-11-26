"""Pack original VAG ADPCM unchanged into aligned native SPU sample bank."""
import hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def pack(out):
 out.mkdir(parents=True,exist_ok=True); bank=bytearray(64);bank[1]=7 # silent looping dummy block
 rows=[]
 for name in ['gemhit1.vag','csprxpu.vag']:
  b=(ROOT/'assets_m12'/name).read_bytes();size,rate=struct.unpack_from('>II',b,12);d=b[48:];assert b[:4]==b'VAGp' and size==len(d) and size%16==0 and rate==22050
  assert all(x>>4<=4 and (x&15)<=12 for x in d[::16]);assert d[-31]==1 and all(x==0 for x in d[1:-31:16]);offset=len(bank)+0x1000;bank.extend(d);bank.extend(bytes((-len(bank))%64));rows.append(dict(name=name,spu_byte_address=offset,size=size,pitch=round(rate*4096/44100),sha256=hashlib.sha256(d).hexdigest()))
 assert 0x1000+len(bank)<=0x80000
 h='#define SFX_BANK_ADDR 0x1000\n#define SFX_BANK_BYTES '+str(len(bank))+'\nstatic const u16 sfx_bank[SFX_BANK_BYTES/2]={\n'
 w=struct.unpack('<%dH'%(len(bank)//2),bank);h+=',\n'.join(','.join(str(x) for x in w[i:i+24]) for i in range(0,len(w),24))+'};\nstatic const u16 sfx_start[2]={'+','.join(str(x['spu_byte_address']//8) for x in rows)+'};\nstatic const u16 sfx_pitch[2]={'+','.join(str(x['pitch']) for x in rows)+'};\n'
 (out/'sfx13.h').write_text(h);(out/'sfx_bank.bin').write_bytes(bank);(out/'audio_report.json').write_text(json.dumps(dict(bank_bytes=len(bank),base=0x1000,limit=0x1000+len(bank),samples=rows),indent=2))
if __name__=='__main__':pack(ROOT/'assets_m13')
