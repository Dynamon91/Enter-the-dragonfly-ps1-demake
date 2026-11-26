#!/usr/bin/env python3
"""Read-only ETD ISO9660/CNK indexer. Never modifies the source disc."""
import argparse, collections, csv, hashlib, json, re, struct
from pathlib import Path
SECTOR=2048
U32=struct.Struct('<I')
ENTRY=struct.Struct('<IIII')
EXT=re.compile(rb'(?i)\.(?:mrb|px[ht]|geom|dat1|list|vag|edf|sxt|txt|wav|anm|wdf)\b')
STEM=re.compile(rb'[A-Za-z0-9_-]{2,80}$')
def find_refs(data):
    for m in EXT.finditer(data):
        stem=STEM.search(data[max(0,m.start()-80):m.start()])
        if stem: yield stem.group()+m.group()

def u32(b,o): return U32.unpack_from(b,o)[0]
class ISO:
    def __init__(self,path):
        self.f=open(path,'rb'); self.size=self.f.seek(0,2); self.files={}
        pvd=self.read(16*SECTOR,SECTOR)
        if pvd[:7]!=b'\x01CD001\x01': raise ValueError('Not ISO9660, 2048-byte sectors')
        self.walk(u32(pvd,158),u32(pvd,166),'',set())
    def __enter__(self): return self
    def __exit__(self,*args): self.f.close()
    def read(self,o,n):
        if o<0 or n<0 or o+n>self.size: raise ValueError('ISO extent out of bounds')
        self.f.seek(o); b=self.f.read(n)
        if len(b)!=n: raise EOFError('Short read')
        return b
    def walk(self,lba,size,prefix,ancestors):
        if lba in ancestors: raise ValueError('Directory cycle')
        b=self.read(lba*SECTOR,size); pos=0
        while pos<len(b):
            n=b[pos]
            if not n: pos=(pos//SECTOR+1)*SECTOR; continue
            r=b[pos:pos+n]; pos+=n
            if len(r)<34 or len(r)<33+r[32]: raise ValueError('Truncated directory record')
            name=r[33:33+r[32]]
            if name in (b'\0',b'\1'): continue
            name=name.decode('ascii').split(';')[0]
            if name in ('.','..') or '/' in name or '\\' in name: raise ValueError('Unsafe name')
            path=prefix+name; l,s=u32(r,2),u32(r,10)
            if r[25]&2: self.walk(l,s,path+'/',ancestors|{lba})
            else:
                if s and l*SECTOR+s>self.size: raise ValueError('File outside ISO: '+path)
                self.files[path]=(l*SECTOR,s)
    def file(self,path): return self.read(*self.files[path])

def entries(b):
    if len(b)<16 or struct.unpack_from('<III',b)!=(1,1,0): raise ValueError('Unknown CNK header')
    count=u32(b,12); end=16+count*16
    if end>len(b): raise ValueError('Truncated directory')
    for i in range(count):
        ident,off,size,flags=ENTRY.unpack_from(b,16+i*16)
        if off>len(b) or size>len(b)-off or (size and off<end): raise ValueError(f'Bad CNK record {i}')
        yield i,ident,off,size,flags

def vag_info(b):
    if b[:4]!=b'VAGp' or len(b)<48: return None
    version,_,size,rate=struct.unpack_from('>IIII',b,4)
    if not size or size%16 or size+48>len(b) or not 1000<=rate<=48000: return None
    return dict(version=version,adpcm_bytes=size,rate=rate,name=b[32:48].split(b'\0')[0].decode('ascii','replace'),duration_s=round(size/16*28/rate,4))

def classify(b):
    if not b: return 'empty'
    if b[:4]==b'VAGp': return 'vag' if vag_info(b) else 'vag_header_unverified'
    if b.startswith(b'\x00\x00\x01\xba'): return 'mpeg_pack_candidate'
    sample=b[:4096]
    if b'\0' not in sample and sum(32<=x<127 or x in (9,10,13) for x in sample)>=len(sample)*.97: return 'text_candidate'
    if b[:4]==b'\0'*4 and b'SpotConeTexture' in b[:128]: return 'material_candidate'
    return 'unknown'

def audit(iso,out):
    out.mkdir(parents=True,exist_ok=True); counts=collections.Counter(); unique={}; summaries=[]; refs=0
    with ISO(iso) as d, (out/'records.csv').open('w',newline='',encoding='utf-8') as rf, (out/'references.csv').open('w',newline='',encoding='utf-8') as nf, (out/'audio.csv').open('w',newline='',encoding='utf-8') as af:
        rw=csv.writer(rf); rw.writerow(['container','index','id','offset','size','flags','kind','sha256']); nw=csv.writer(nf); nw.writerow(['container','index','id','reference']); aw=csv.writer(af); aw.writerow(['container','index','id','name','version','rate','adpcm_bytes','duration_s','sha256'])
        for path in sorted(d.files):
            if not path.endswith('.CNK'): continue
            b=d.file(path); local=collections.Counter(); total=0
            for i,h,o,s,t in entries(b):
                x=b[o:o+s]; k=classify(x); sha=hashlib.sha256(x).hexdigest(); counts[k]+=1; local[k]+=1; total+=s; unique.setdefault(sha,(s,k)); rw.writerow([path,i,f'{h:08x}',o,s,t,k,sha]);
                if k=='vag':
                    v=vag_info(x); aw.writerow([path,i,f'{h:08x}',v['name'],v['version'],v['rate'],v['adpcm_bytes'],v['duration_s'],sha])
                if k not in ('vag','empty'):
                    for name in sorted(set(find_refs(x))): nw.writerow([path,i,f'{h:08x}',name.decode('ascii')]); refs+=1
            summaries.append(dict(path=path,bytes=len(b),payload_bytes=total,records=sum(local.values()),kinds=dict(local)))
        (out/'iso_files.json').write_text(json.dumps(d.files,indent=2))
    summary=dict(containers=len(summaries),records=sum(counts.values()),kinds=dict(counts),unique_payloads=len(unique),unique_payload_bytes=sum(s for s,k in unique.values()),references=refs,details=summaries)
    (out/'summary.json').write_text(json.dumps(summary,indent=2)); print(json.dumps({k:v for k,v in summary.items() if k!='details'},indent=2))

def extract(iso,container,out,kind=None):
    out.mkdir(parents=True,exist_ok=True)
    with ISO(iso) as d:
        b=d.file(container); n=0
        for i,h,o,s,t in entries(b):
            x=b[o:o+s]; k=classify(x)
            if kind and k!=kind: continue
            ext={'vag':'vag','text_candidate':'txt'}.get(k,'bin'); (out/f'{i:04d}_{h:08x}.{ext}').write_bytes(x); n+=1
        print(f'Extracted {n} records from {container}')
if __name__=='__main__':
    p=argparse.ArgumentParser(); sp=p.add_subparsers(dest='command',required=True)
    a=sp.add_parser('audit'); a.add_argument('iso',type=Path); a.add_argument('out',type=Path)
    a=sp.add_parser('extract'); a.add_argument('iso',type=Path); a.add_argument('container'); a.add_argument('out',type=Path); a.add_argument('--kind')
    a=p.parse_args()
    if a.command=='audit': audit(a.iso,a.out)
    else: extract(a.iso,a.container,a.out,a.kind)
