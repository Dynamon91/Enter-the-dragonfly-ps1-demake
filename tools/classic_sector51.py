"""Pack reviewed Classic geometry into the original ETDS/ETDI sector format.
Inputs are local source-derived assets, never generated replacements. No scene-ready claim.
"""
import argparse, collections, hashlib, json, struct, zlib
from pathlib import Path
import numpy as np

CELL=2048; PAGE=2048; MAX=65536
H=struct.Struct('<4sHHIiiiHHHHII6h12x')
D=struct.Struct('<IIII3i6i3H2x')
STRIDES=(36,24,16)

def require(ok,msg):
    if not ok: raise ValueError(msg)

def array(a,name,cols,integer=False):
    a=np.asarray(a)
    require(a.ndim==2 and a.shape[1]==cols and len(a)>0,'bad '+name+' shape')
    require(a.dtype.kind in ('iu' if integer else 'iuf') and np.isfinite(a).all(),'bad '+name+' values')
    return a

def mesh(z):
    v=array(z['vertices'],'vertices',3).astype(np.float64)
    f=array(z['faces'],'faces',3,True)
    require(np.all(f>=0) and np.all(f<len(v)),'face index outside vertex array')
    require(np.max(np.abs(v))<=199000,'world outside current engine coordinate limit')
    return v,f

def vector(a,n,name):
    a=np.asarray(a)
    require(a.shape==(n,) and a.dtype.kind in 'iu','bad '+name)
    return a

def pack(geometry,collision,config,out):
    out=Path(out);require(not out.exists(),'output already exists')
    require(config.get('world_coordinates_reviewed') is True,'review source world transforms first')
    require(type(config.get('level')) is int and 0<=config['level']<=9,'Classic level ID required (9=Ripto arena)')
    v,f=mesh(geometry); cv,cf=mesh(collision)
    uv=array(geometry['uv'],'UV',2).astype(np.float64);require(len(uv)==len(v),'UV/vertex count mismatch')
    hashes=vector(geometry['material'],len(f),'material hashes');require(np.all(hashes>=0) and np.all(hashes<=0xffffffff),'invalid material hash')
    flags=vector(collision['flags'],len(cf),'collision flags');require(np.isin(flags,[0,3]).all(),'unsupported collision flags')
    mats=config.get('materials');require(isinstance(mats,list) and 0<len(mats)<=65536,'explicit material table required')
    lookup={}
    for i,m in enumerate(mats):
        require(m.get('id')==i and m.get('status')=='resolved','material table not contiguous/resolved')
        h=int(m['hash'],16);require(0<=h<=0xffffffff and h not in lookup,'duplicate or invalid material hash');lookup[h]=i
    require(all(int(h) in lookup for h in hashes),'unresolved source material')
    objects=config.get('objects');require(isinstance(objects,list),'explicit placement list required')
    groups=collections.defaultdict(lambda:[[],[],[]]);seen=set();uv_shifted=0
    def add(points,kind,tail):
        p=np.asarray(points,dtype=np.float64);require(np.isfinite(p).all() and np.max(np.abs(p))<=199000,'placement outside world')
        # Existing runtime uses Y-down; quantize in world coordinates before assigning cell.
        p=np.rint(p*np.array([1,-1,1])).astype(np.int64);k=tuple(int(x)//CELL for x in np.floor(p.mean(0)[[0,2]]));org=np.array([k[0]*CELL+CELL//2,0,k[1]*CELL+CELL//2]);q=p-org
        require(q.min()>=-32768 and q.max()<=32767,'local position overflow')
        if kind!=2:require(np.any(np.cross(q[1]-q[0],q[2]-q[0])),'triangle collapsed by quantization')
        groups[k][kind].append((q.astype('<i2').tobytes()+tail,q))
    for i,ids in enumerate(f):
        q=np.rint(uv[ids]*1024);require(np.max(np.abs(q))<=2**48,'UV outside safe quantization range');q=q.astype(np.int64)
        if q.min()<-32768 or q.max()>32767:
            q-=np.floor_divide(q.min(0)+32768,1024)*1024;uv_shifted+=1
        require(q.min()>=-32768 and q.max()<=32767,'UV span exceeds Q10')
        add(v[ids],0,q.astype('<i2').tobytes()+struct.pack('<HI',lookup[int(hashes[i])],i))
    for i,ids in enumerate(cf):add(cv[ids],1,struct.pack('<HI',int(flags[i]),i))
    for o in objects:
        k,value,sid=o['kind'],o.get('value',0),o['source_id']
        require(all(type(x) is int for x in (k,value,sid)) and 1<=k<=4 and 0<=value<=65535 and 0<=sid<=0xffffffff and sid not in seen,'invalid or duplicate placement ID')
        p=np.asarray(o['source_xyz']);require(p.shape==(3,) and p.dtype.kind in 'iuf','invalid placement coordinates');seen.add(sid);add(p.reshape(1,3),2,struct.pack('<HHHI',k,value,0,sid))
    data=bytearray();entries=[];counts=[0,0,0]
    for k,g in sorted(groups.items()):
        org=np.array([k[0]*CELL+CELL//2,0,k[1]*CELL+CELL//2]);pos=[0]*3
        while any(pos[i]<len(g[i]) for i in range(3)):
            free=MAX-H.size;rows=[];nn=[]
            for i,stride in enumerate(STRIDES):
                n=min(len(g[i])-pos[i],free//stride);rows.extend(g[i][pos[i]:pos[i]+n]);pos[i]+=n;free-=n*stride;nn.append(n);counts[i]+=n
            payload=b''.join(x[0] for x in rows);pts=np.concatenate([x[1] for x in rows]);lo=pts.min(0);hi=pts.max(0);crc=zlib.crc32(payload);i=len(entries);size=H.size+len(payload)
            block=H.pack(b'ETDS',1,H.size,i,*org,*nn,0,len(payload),crc,*lo,*hi)+payload
            entries.append((i,len(data)//PAGE,size,crc,*org,*(lo+org),*(hi+org),*nn));data.extend(block);data.extend(bytes((-len(data))%PAGE))
    require(counts==[len(f),len(cf),len(objects)],'record accounting mismatch')
    idx=struct.pack('<4sHHII',b'ETDI',1,D.size,len(entries),CELL)+b''.join(D.pack(*e) for e in entries)
    # Exact anchor-neighborhood maximum: all 512-unit grid positions covered by an AABB+radius.
    # Sweep events along x, then z. Sum sector-rounded lengths (not raw payload lengths).
    events=collections.defaultdict(list);radius=1792
    for i,e in enumerate(entries):
        xmin,zmin,xmax,zmax=e[7],e[9],e[10],e[12]
        a=(xmin-radius-256+511)//512;b=(xmax+radius-256)//512
        c=(zmin-radius-256+511)//512;d=(zmax+radius-256)//512
        if a<=b and c<=d:
            w=(e[2]+PAGE-1)//PAGE*PAGE;events[a].append((i,c,d,w));events[b+1].append((i,c,d,-w))
    active={};peak=peak_count=0
    for x,changes in sorted(events.items()):
        for i,c,d,w in changes:
            if w>0:active[i]=(c,d,w)
            else:active.pop(i)
        z_events=collections.defaultdict(lambda:[0,0])
        for c,d,w in active.values():
            z_events[c][0]+=w;z_events[c][1]+=1;z_events[d+1][0]-=w;z_events[d+1][1]-=1
        n=total=0
        for _,(dw,dn) in sorted(z_events.items()):
            total+=dw;n+=dn;peak=max(peak,total);peak_count=max(peak_count,n)
    report=dict(level=config['level'],render=counts[0],collision=counts[1],objects=counts[2],materials=len(mats),blocks=len(entries),data_bytes=len(data),index_bytes=len(idx),max_block=max(e[2] for e in entries),uv_shifted=uv_shifted,anchor_radius=radius,peak_neighborhood_bytes=peak,peak_neighborhood_blocks=peak_count,data_sha256=hashlib.sha256(data).hexdigest(),index_sha256=hashlib.sha256(idx).hexdigest(),note='Format-compatible only; material/transform review flags supplied by caller. Runtime budgets and actual level completeness not certified.')
    out.mkdir(parents=True);(out/'LEVEL.DAT').write_bytes(data);(out/'LEVEL.IDX').write_bytes(idx);(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');return report

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('geometry',type=Path);p.add_argument('collision',type=Path);p.add_argument('config',type=Path);p.add_argument('out',type=Path);a=p.parse_args()
    with np.load(a.geometry,allow_pickle=False) as g,np.load(a.collision,allow_pickle=False) as c:print(json.dumps(pack(g,c,json.loads(a.config.read_text()),a.out),indent=2))
if __name__=='__main__':main()
