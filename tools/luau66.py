"""Crop Circle Country: original directory-bounded PXT, material and placement recovery."""
import argparse,collections,hashlib,json,re,struct,zlib
from pathlib import Path
import numpy as np
from PIL import Image
from cnk import entries,u32
from recover import pxt_groups,nodes
from hash08 import fold

def texture_directory(table,data):
    if len(table)<16 or len(table)!=32+u32(table,12)*16:raise ValueError('bad texture table size')
    rows=[struct.unpack_from('<IIII',table,16+i*16) for i in range(u32(table,12))];groups={};reg={};empty=[];pos=0
    for i,(h,o,s,f) in enumerate(rows):
        off=o-len(table);end=rows[i+1][1]-len(table) if i+1<len(rows) else len(data)
        if off!=pos or s>end-off or end-off-s!=16 or end>len(data) or h in reg:raise ValueError(f'bad texture extent {i}')
        pos=end
        if not s:empty.append(i);continue
        parsed=list(pxt_groups(data[off:off+s]))
        if len(parsed)!=1:raise ValueError(f'bad texture group {i}')
        _,pal,imgs=parsed[0];groups[i]=(pal,imgs);reg[h]=dict(group=i,size=s,dimensions=list(imgs[0][:2]) if imgs else None,palette=len(pal))
    if pos!=len(data):raise ValueError('unaccounted texture bytes')
    return reg,groups,empty

def placements(b):
    rows=[]
    for p,n,q in nodes(b,0x2a29015d):
        if q+85>len(b) or b[q+68:q+77]!=b'Character' or u32(b,q+77)!=2:continue
        ln=u32(b,q+81)
        if not 0<ln<256 or q+85+ln>len(b):continue
        try:edf=b[q+85:q+85+ln].decode('ascii')
        except UnicodeDecodeError:continue
        xyz=struct.unpack_from('<3f',b,q)
        if not np.isfinite(xyz).all() or xyz!=struct.unpack_from('<3f',b,q+24):continue
        m=re.fullmatch(r'gem(\d+)\.edf',edf,re.I);rows.append(dict(name=n,edf=edf,source_xyz=list(xyz),source_id=p,kind=1 if m else 4,value=int(m[1]) if m else 0))
    return rows

def collision(b):
    ns=list(nodes(b,0xbf1d6d84));assert len(ns)==1 and ns[0][1]=='LI_COLLShape';_,name,q=ns[0];bounds=np.frombuffer(b,'<f4',6,q).reshape(2,3).copy();v=[];f=[];flags=[];offsets=[];rejected=0;p=q+53
    while p+8<=len(b):
        flag,n=struct.unpack_from('<II',b,p)
        if flag in (0,3) and 3<=n<=32 and p+8+n*12<=len(b):
            a=np.frombuffer(b,'<f4',n*3,p+8).reshape(-1,3).astype(float)
            if np.isfinite(a).all() and np.all(a>=bounds[0]-10) and np.all(a<=bounds[1]+10) and np.max(np.abs(a))>100 and np.min(np.linalg.norm(np.roll(a,1,0)-a,axis=1))>.01:
                sv=np.linalg.svd(a-a.mean(0),compute_uv=False)
                if sv[1]>.01 and sv[2]<max(.02,sv[0]*.015):
                    # Reject nonconvex polygons instead of silently fan-filling them.
                    edges=np.roll(a,-1,axis=0)-a;cross=np.cross(edges,np.roll(edges,-1,axis=0));normal=np.cross(a[1]-a[0],a[2]-a[0]);dots=cross@normal
                    if np.linalg.norm(normal)<.01 or np.any(dots<-.01):rejected+=1;p+=8+n*12;continue
                    base=len(v);v.extend(a)
                    for j in range(1,n-1):
                        if np.linalg.norm(np.cross(a[j]-a[0],a[j+1]-a[0]))>.01:f.append((base,base+j,base+j+1));flags.append(flag);offsets.append(p)
                    p+=8+n*12;continue
        p+=4
    return dict(vertices=np.array(v,dtype=np.float32),faces=np.array(f,dtype=np.int32),flags=np.array(flags,dtype=np.int32),source_offsets=np.array(offsets),bounds=bounds),rejected

def build(cnk,geometry,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);b=Path(cnk).read_bytes();r={i:b[o:o+s] for i,h,o,s,t in entries(b)};reg,groups,empty=texture_directory(r[333],r[612]);meta=r[394];refs=collections.defaultdict(list)
    for p,n,q in nodes(meta,0x47ba46ed):
        if q+100>len(meta):continue
        h=u32(meta,p+4);t=u32(meta,q+96)
        for pp,nn,qq in nodes(meta[q+96:q+800],0xdad78930):
            if u32(meta,q+96+pp+4)!=t:continue
            qq+=q+96;m=re.search(rb'[0-9A-F]{8}\.PXT',meta[qq:qq+150])
            if not m or qq+m.end()+10>len(meta):continue
            w,hh,_,s=struct.unpack_from('<HHHI',meta,qq+m.end());fn=m.group().decode();e=reg.get(fold(fn.lower().encode()))
            if e and e['size']==s and e['dimensions']==[w,hh] and e['palette'] in (16,256):refs[h].append(dict(filename=fn,group=e['group'],name=n,texture_node=nn))
            break
    z=np.load(geometry,allow_pickle=False);hs=collections.Counter(map(int,z['material']));materials=[]
    for i,h in enumerate(sorted(hs)):
        candidates=sorted(set(v['group'] for v in refs[h]));materials.append(dict(id=i,hash=f'{h:08x}',status='resolved' if len(candidates)==1 else 'unresolved',group=candidates[0] if len(candidates)==1 else None,refs=refs[h],faces=hs[h]))
    data=bytearray();idx=[];textures=out/'textures';textures.mkdir(exist_ok=True)
    for i in sorted({m['group'] for m in materials if m['group'] is not None}):
        pal,imgs=groups[i];w,h,ix=imgs[0];rgb=pal.astype(np.uint16);clut=np.maximum((rgb[:,0]>>3)|((rgb[:,1]>>3)<<5)|((rgb[:,2]>>3)<<10),1).astype('<u2');clut=np.pad(clut,(0,256-len(clut)));pix=np.asarray(Image.fromarray(ix).resize((64,64),Image.Resampling.NEAREST));payload=clut.tobytes()+pix.tobytes();crc=zlib.crc32(payload);idx.append((i,len(data)//2048,crc));data.extend((struct.pack('<4sHHIIII',b'ETDT',1,i,w,h,len(payload),crc)+payload).ljust(6144,b'\0'));Image.fromarray(pal[ix][:,:,:3]).save(textures/f'{i:03}.png')
    (out/'LIATEX.DAT').write_bytes(data);(out/'LIATEX.IDX').write_bytes(struct.pack('<4sHHI',b'ETTI',1,12,len(idx))+b''.join(struct.pack('<III',*x) for x in idx))
    a=placements(meta);other={(x['name'],x['edf'],tuple(x['source_xyz'])) for x in placements(r[628])};obj=[x for x in a if (x['name'],x['edf'],tuple(x['source_xyz'])) in other];c,rejected=collision(r[448]);np.savez_compressed(out/'collision.npz',**c)
    (out/'bindings.json').write_text(json.dumps(dict(materials=materials,objects=obj),indent=2));report=dict(source_sha256=hashlib.sha256(b).hexdigest(),texture_groups=len(groups),empty_groups=empty,material_count=len(materials),resolved_materials=sum(m['status']=='resolved' for m in materials),resolved_faces=sum(m['faces'] for m in materials if m['status']=='resolved'),converted_groups=len(idx),texture_bytes=len(data),collision_triangles=len(c['faces']),collision_rejected_polygons=rejected,placements=len(obj),gem_placements=sum(o['kind']==1 for o in obj),gem_value=sum(o['value'] for o in obj),limitations='Opaque base textures only; source layers/transparency unresolved. Collision is heuristic, not decoded BSP. Non-gem placements not implemented. World transforms not independently reviewed.')
    (out/'report66.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('cnk',type=Path);p.add_argument('geometry',type=Path);p.add_argument('out',type=Path);a=p.parse_args();build(a.cnk,a.geometry,a.out)
