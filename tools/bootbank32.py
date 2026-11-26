"""Move initialization-only GPU/SPU payloads out of the linked executable.
Keep all payload bytes exactly equal to v0.31 C arrays, aligned for native loads.
The converted headers are generated locally and not original source files."""
from pathlib import Path
import re,struct,zlib,json
R=Path(__file__).resolve().parents[1];OLD=R/'build_m31/play';O=R/'build_m32/play'
ARRAYS=[('scene.h','upload','u32','I'),('firetex11.h','fireupload','u32','I'),('skydata28.h','sky_pal28','u16','H'),('skydata28.h','sky_pix28','U8','B'),('ninja30.h','ninja_pal30','u16','H'),('ninja30.h','ninja_pix30','U8','B'),('sfx14.h','sfx_bank','u16','H')]
def generate(old=OLD,out=O):
 out.mkdir(parents=True,exist_ok=True);bank=bytearray();records={};headers={}
 for name,var,ctype,fmt in ARRAYS:
  src=headers.get(name,(old/name).read_text());pat=rf'static const {ctype} {var}((?:\[[^\]]*\])+)=\s*\{{(.*?)\}};';m=re.search(pat,src,re.S)
  if not m:raise ValueError(var)
  vals=[int(x) for x in re.findall(r'\d+',m[2])];payload=struct.pack('<'+fmt*len(vals),*vals);bank.extend(bytes((-len(bank))%4));off=len(bank);bank.extend(payload)
  dims=re.findall(r'\[([^\]]*)\]',m[1]);cast=f'const {ctype} *' if len(dims)==1 else f'const {ctype} (*)'+''.join('['+d+']' for d in dims[1:]);headers[name]=src[:m.start()]+f'#define {"boot_upload32" if var=="upload" else var} (({cast})(startup32+{off}u))\n'+src[m.end():]
  records[var]=dict(offset=off,bytes=len(payload),crc32=f'{zlib.crc32(payload):08x}',header=name)
 for name,src in headers.items():(out/name).write_text(src)
 padded=(len(bank)+2047)//2048*2048;crc=zlib.crc32(bank);(out/'BOOT32.DAT').write_bytes(bank);(out/'bootbank32.h').write_text(f'#define BOOT_BYTES32 {len(bank)}u\n#define BOOT_PAD32 {padded}u\n#define BOOT_CRC32 0x{crc:08x}u\n');rep=dict(bytes=len(bank),padded=padded,crc32=f'{crc:08x}',arrays=records);(out/'bootbank32.json').write_text(json.dumps(rep,indent=2));return rep
if __name__=='__main__':print(generate())
