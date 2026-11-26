"""Read-only ISO/ZIP recovery for ETD. Never manufacture missing asset banks."""
import argparse, hashlib, json, os, struct, zipfile
from pathlib import Path, PurePosixPath

KNOWN = {'full_m37':'aa9d30787b88f26f37ed36398cbc995b8e79e9f541ef5c23edac6cf108b4de04',
         'disc_m37':'0cef80b137db56a22e09d4246c602c68654cc16776442563fe31a2711943488f'}
# Actual dependencies read by tools/build_m37.py; generated source inputs are separate.
DISC_BANKS = {'HUBSECT.DAT','HUBSECT.IDX','HUBTEX.DAT','HUBTEX.IDX','DOJOSECT.DAT','DOJOSECT.IDX','DOJOTEX.DAT','DOJOTEX.IDX','QMOD35.DAT','BOOT32.DAT','ETD_PACK.EXE','ETD_POOL.EXE','ETD_AI.EXE','ETD_TALK.EXE','ETD_NPCS.EXE','ETD_BOOT.EXE'}
SOURCE_INPUTS = {'build_m36/play/play36.c','build_m36/play/bootbank32.json','assets_m37/rig37_data.h','assets_m37/questpack37.h'}

def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def number(b, off):
    a,c=struct.unpack_from('<I',b,off)[0],struct.unpack_from('>I',b,off+4)[0]
    if a!=c:raise ValueError('inconsistent ISO endian fields')
    return a

class Disc:
    def __init__(self,p):
        self.p=Path(p);self.f=self.p.open('rb')
        try:
            for self.stride,self.offset in ((2048,0),(2352,24),(2352,16)):
                self.f.seek(16*self.stride+self.offset)
                if self.f.read(7)==b'\x01CD001\x01':break
            else:raise ValueError('no supported ISO9660 primary volume')
            self.size=self.p.stat().st_size//self.stride; pvd=self.sector(16)
            self.volume=number(pvd,80)
            if not 21<=self.volume<=self.size:raise ValueError('invalid volume size')
            self.entries={};self.visited=set();self.walk(pvd[156:190],'',0)
        except BaseException:self.f.close();raise
    def __enter__(self):return self
    def __exit__(self,*_):self.f.close()
    def sector(self,lba):
        if not 0<=lba<self.size:raise ValueError('sector out of file')
        self.f.seek(lba*self.stride+self.offset);b=self.f.read(2048)
        if len(b)!=2048:raise ValueError('truncated sector')
        return b
    def record(self,r):
        if len(r)<34 or r[0]>len(r) or r[32]<1 or 33+r[32]>r[0]:raise ValueError('invalid directory record')
        if r[1] or r[26] or r[27] or r[25]&128:raise ValueError('unsupported extent/interleave')
        l,n=number(r,2),number(r,10)
        if l>=self.volume or (n+2047)//2048>self.volume-l:raise ValueError('extent outside volume')
        return l,n,r[25],r[33:33+r[32]]
    def walk(self,r,prefix,depth):
        l,n,flags,_=self.record(r)
        if depth>16 or n>16*1024*1024 or l in self.visited or not flags&2:raise ValueError('directory recursion or size invalid')
        self.visited.add(l)
        for off in range(0,n,2048):
            b=self.sector(l+off//2048);i=0
            while i<min(2048,n-off) and b[i]:
                length=b[i]
                if i+length>min(2048,n-off):raise ValueError('directory record crosses sector')
                rr=b[i:i+length];i+=length;start,size,flag,name=self.record(rr)
                if name in (b'\0',b'\1'):continue
                name=name.decode('ascii').split(';')[0]
                if not name or name in ('.','..') or any(c in name for c in '/\\:') or any(ord(c)<32 for c in name):raise ValueError('unsafe ISO path')
                key=(prefix+name).upper()
                if key in self.entries:raise ValueError('duplicate ISO path')
                if len(self.entries)>=100000:raise ValueError('entry limit')
                self.entries[key]=(start,size,flag)
                if flag&2:self.walk(rr,key+'/',depth+1)
    def copy(self,key,out):
        l,n,flag=self.entries[key]
        if flag&2:raise ValueError('not a file')
        out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
        h=hashlib.sha256()
        with out.open('xb') as f:
            for i in range((n+2047)//2048):
                b=self.sector(l+i)[:min(2048,n-i*2048)];f.write(b);h.update(b)
        return {'path':key,'bytes':n,'sha256':h.hexdigest()}
    def classify(self):
        names=set(self.entries)
        if 'ETD_PACK.EXE' in names and {'DOJOSECT.DAT','QMOD35.DAT'}<=names:return 'm37_compatible_disc'
        if any(k.startswith('SPYRODAT/') and k.endswith('.CNK') for k in names) and any(k.startswith(('SLUS_','SLES_','SCES_')) for k in names):return 'ps2_etd_candidate'
        return 'other_iso'

def zip_report(p):
    with zipfile.ZipFile(p) as z:
        names=set(i.filename.replace('\\','/').rstrip('/') for i in z.infolist() if not i.is_dir())
        found=sorted(k for k in SOURCE_INPUTS if any(n==k or n.endswith('/'+k) for n in names))
        discs=sorted(n for n in names if n.lower().endswith(('.iso','.bin','.cue')))
    sha=digest(p)
    return {'type':next((k for k,v in KNOWN.items() if v==sha),'zip_candidate'), 'sha256':sha,'source_inputs':found,'disc_members':discs[:100]}

def scan(roots):
    results=[];seen=set()
    for root in roots:
        root=Path(root)
        files=[root] if root.is_file() else (p for p in root.rglob('*') if p.is_file() and not p.is_symlink())
        for p in files:
            if p.suffix.lower() not in ('.iso','.bin','.img','.zip','.7z','.rar'):continue
            try:
                key=p.resolve()
                if key in seen:continue
                seen.add(key)
                if zipfile.is_zipfile(p):r=zip_report(p)
                elif p.suffix.lower() in ('.7z','.rar'):r={'type':'archive_requires_local_unpack'}
                else:
                    with Disc(p) as d:r={'type':d.classify(),'files':len(d.entries),'banks':sorted(DISC_BANKS&set(d.entries)), 'cnks':sum(k.endswith('.CNK') and not v[2]&2 for k,v in d.entries.items())}
                results.append({'path':str(p),**r})
            except (OSError,ValueError,UnicodeError,zipfile.BadZipFile) as e:results.append({'path':str(p),'type':'unreadable_or_non_disc','reason':str(e)})
    return results

def extract(image,out):
    out=Path(out)
    if out.exists():raise ValueError('use a new output directory')
    with Disc(image) as d:
        kind=d.classify()
        if kind=='m37_compatible_disc':keys=sorted(DISC_BANKS&set(d.entries))
        elif kind=='ps2_etd_candidate':keys=sorted(k for k,v in d.entries.items() if not v[2]&2 and (k.startswith('SPYRODAT/') or k=='SYSTEM.CNF' or k.startswith(('SLUS_','SLES_','SCES_'))))
        else:raise ValueError('unrecognized disc; no extraction performed')
        out.mkdir(parents=True);records=[d.copy(k,out/k) for k in keys]
        report={'type':kind,'source':str(image),'files':records,'missing_disc_banks':sorted(DISC_BANKS-set(keys)) if kind=='m37_compatible_disc' else [],'note':'Disc recovery is not full build-source recovery; no authenticity claim without source verification.'}
        (out/'recovery.json').write_text(json.dumps(report,indent=2)+'\n');return report

def main():
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='cmd',required=True)
    a=s.add_parser('scan');a.add_argument('roots',nargs='+',type=Path)
    a=s.add_parser('extract');a.add_argument('image',type=Path);a.add_argument('out',type=Path)
    a=p.parse_args();print(json.dumps(scan(a.roots) if a.cmd=='scan' else extract(a.image,a.out),indent=2))
if __name__=='__main__':main()
