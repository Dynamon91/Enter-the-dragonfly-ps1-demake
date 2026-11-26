"""Source-first CNK inventory and named terrain recovery (no generated replacement art).
Based on the verified v0.25 Dojo format; other worlds require source verification.
"""
import argparse, hashlib, json, re, struct
from pathlib import Path
import numpy as np

SIG=b'\x20\x40\x40\x40\x40\x01\x80'
NORMAL=b'\x20\x40\x40\x40\x40\x21\x80'
STRIP=b'\x20\x54\x54\x54\x54\xc1\x80\x10\x72'
UV=b'\x20\x50\x50\x50\x50\x61\x80\x20\x74'
TYPES={2724436415:76,1418262912:76,4213557647:80}

def records(b):
    if len(b)<16 or struct.unpack_from('<III',b)!=(1,1,0):raise ValueError('unknown CNK header')
    count=struct.unpack_from('<I',b,12)[0];end=16+count*16
    if end>len(b):raise ValueError('truncated CNK directory')
    result={}
    for i in range(count):
        ident,off,n,flags=struct.unpack_from('<IIII',b,16+i*16)
        if off>len(b) or n>len(b)-off or (n and off<end):raise ValueError(f'bad CNK record {i}')
        result[i]=(ident,memoryview(b)[off:off+n])
    return result

def shapes(b):
    for tag,delta in TYPES.items():
        for m in re.finditer(re.escape(struct.pack('<I',tag)),b):
            p=m.start()
            if p+20>len(b):continue
            n=struct.unpack_from('<I',b,p+8)[0];q=p+20+n
            if not 0<n<128 or q+delta+12>len(b):continue
            name=bytes(b[p+12:p+12+n])
            if not all(32<=x<127 for x in name):continue
            off,_,count,mat=struct.unpack_from('<IHHI',b,q+delta)
            bounds=np.frombuffer(b,'<f4',6,q).reshape(2,3).copy()
            if not count or off%16 or not np.isfinite(bounds).all() or np.any(bounds[0]>bounds[1]) or np.max(np.abs(bounds))>=1e6:continue
            yield dict(name=name.decode('ascii'),offset=off,packets=count,material=mat,bounds=bounds,node=p)

def packets(b):
    # Bound each packet at the next position signature; never borrow a UV/strip from it.
    starts=[m.start()-1 for m in re.finditer(re.escape(SIG),b) if m.start()>0]
    result={}
    for i,p in enumerate(starts):
        end=min(starts[i+1] if i+1<len(starts) else len(b),p+1500)
        if p+10>end or b[p+9]!=0x78:continue
        nv=b[p+8];q=p+10+12*nv
        if not 3<=nv<=64 or q+16>end or bytes(b[q+7:q+14])!=NORMAL:continue
        v=np.frombuffer(b,'<f4',nv*3,p+10).reshape(-1,3).copy()
        if not np.isfinite(v).all() or np.max(np.abs(v))>=1e6:continue
        z=bytes(b[p:end]);f=z.find(STRIP);u=z.find(UV)
        if f<q-p+16 or u<f+25 or u+9+256>len(z):continue
        t=z[f+9:f+25];n=t[0];lens=[k//3 for k in t[1:] if k]
        if not (0<n<=nv and lens and min(lens)>=3 and sum(lens)==n and all(k%3==0 for k in t[1:])):continue
        uv=np.frombuffer(z,'<f4',64,u+9).reshape(-1,2)[:n].copy()
        if not np.isfinite(uv).all():continue
        result[p]=(v[:n],uv,lens)
    # Keep invalid packet positions: matching cannot silently skip a malformed packet.
    return starts,result

def fingerprint(pp):
    h=hashlib.sha256()
    for v,u,lens in pp:h.update(v.tobytes());h.update(u.tobytes());h.update(bytes(lens))
    return h.hexdigest()

def inventory(root):
    result=[]
    for p in sorted(Path(root).rglob('*')):
        if not p.is_file() or p.suffix.lower()!='.cnk':continue
        try:
            b=p.read_bytes();r=records(b);candidates=[]
            for i,(ident,x) in r.items():
                ss=list(shapes(x))
                if ss:candidates.append(dict(record=i,id=f'{ident:08x}',shape_count=len(ss),names=[s['name'] for s in ss[:20]]))
            result.append(dict(container=str(p.relative_to(root)),records=len(r),metadata_candidates=candidates))
        except (ValueError,OSError) as e:result.append(dict(container=str(p.relative_to(root)),error=str(e)))
    return result

def recover(path,metadata,pattern,out,allow_partial=False):
    b=Path(path).read_bytes();r=records(b)
    if metadata not in r:raise ValueError('metadata record absent')
    selected=[s for s in shapes(r[metadata][1]) if re.search(pattern,s['name'],re.I)]
    if not selected:raise ValueError('no named shapes match; inspect inventory first')
    candidates={}
    for i,(_,g) in r.items():
        if bytes(g[23:30])!=SIG:continue
        starts,pp=packets(g)
        if pp:candidates[i]=(starts,{p:k for k,p in enumerate(starts)},pp)
    vertices=[];uv=[];faces=[];materials=[];parts=[];meta=[];unmatched=[];seen=set();duplicates=0
    for s in selected:
        matches={}
        for i,(starts,positions,pp) in candidates.items():
            start=s['offset']+22;k=positions.get(start)
            if k is None:continue
            seq=starts[k:k+s['packets']]
            if len(seq)!=s['packets'] or any(p not in pp for p in seq):continue
            group=[pp[p] for p in seq];v=np.concatenate([x[0] for x in group]);err=float(np.max(np.abs(s['bounds']-np.stack([v.min(0),v.max(0)]))))
            if err<.01:matches.setdefault(fingerprint(group),(i,group,err))
        if len(matches)!=1:
            unmatched.append(dict(name=s['name'],node=s['node'],matches=[x[0] for x in matches.values()]));continue
        fp,(i,group,err)=next(iter(matches.items()));key=(s['name'],s['material'],fp)
        if key in seen:duplicates+=1;continue
        seen.add(key);base=len(vertices);first=len(faces)
        for v,u,lens in group:
            start=len(vertices);vertices.extend(v);uv.extend(u);cursor=0
            for length in lens:
                for j in range(2,length):
                    ix=[cursor+j-2,cursor+j-1,cursor+j]
                    if j%2:ix[0],ix[1]=ix[1],ix[0]
                    if np.linalg.norm(np.cross(v[ix[1]]-v[ix[0]],v[ix[2]]-v[ix[0]]))<1e-5:continue
                    faces.append([start+x for x in ix]);materials.append(s['material']);parts.append(len(meta))
                cursor+=length
        meta.append(dict(name=s['name'],record=i,material=f"{s['material']:08x}",offset=s['offset'],packets=s['packets'],bounds_error=err,vertices=len(vertices)-base,triangles=len(faces)-first))
    out=Path(out)
    report=dict(container=Path(path).name,source_sha256=hashlib.sha256(b).hexdigest(),metadata_record=metadata,selection=pattern,selected=len(selected),matched=len(meta),duplicate_shapes=duplicates,unmatched=unmatched,vertices=len(vertices),triangles=len(faces),meshes=meta,exported=bool(faces and (allow_partial or not unmatched)),limitations='Source local coordinates and material hashes only; transforms, material binding, collision, placements and runtime not validated. Selection is not full level coverage.')
    out.mkdir(parents=True,exist_ok=False)
    if report['exported']:
        np.savez_compressed(out/'geometry.npz',vertices=np.asarray(vertices,dtype=np.float32).reshape(-1,3),faces=np.asarray(faces,dtype=np.int32).reshape(-1,3),uv=np.asarray(uv,dtype=np.float32).reshape(-1,2),material=np.asarray(materials,dtype=np.uint32),part=np.asarray(parts,dtype=np.int32))
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__);sp=p.add_subparsers(dest='command',required=True)
    a=sp.add_parser('inventory');a.add_argument('root',type=Path)
    a=sp.add_parser('recover');a.add_argument('cnk',type=Path);a.add_argument('metadata',type=int);a.add_argument('pattern');a.add_argument('out',type=Path);a.add_argument('--allow-partial',action='store_true')
    a=p.parse_args()
    if a.command=='inventory':print(json.dumps(inventory(a.root),indent=2));return 0
    report=recover(a.cnk,a.metadata,a.pattern,a.out,a.allow_partial);print(json.dumps({k:v for k,v in report.items() if k!='meshes'},indent=2));return int(not report['exported'])
if __name__=='__main__':raise SystemExit(main())
