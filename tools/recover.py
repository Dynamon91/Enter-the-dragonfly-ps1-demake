"""ETD PS2 resource recovery. Based on observed source bytes and egartley/game-re-patterns (MRB, GEOM, PXT)."""
import argparse, json, re, struct, hashlib, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from cnk import ISO, entries, u32
HUB='SPYRODAT/CHUNKS3/THE_HUB.CNK'
TYPES={2724436415:('object',76),1418262912:('cluster',76),4213557647:('shape2',80)}
SIG=b'\x20\x40\x40\x40\x40\x01\x80'
PX=struct.pack('<IIII',4,268435456,14,0)
def records(iso):
    with ISO(iso) as d: b=d.file(HUB)
    return {i:(h,b[o:o+s]) for i,h,o,s,t in entries(b)}
def nodes(b,typ):
    for m in re.finditer(re.escape(struct.pack('<I',typ)),b):
        p=m.start()
        if p+20>len(b):continue
        n=u32(b,p+8)
        if not 0<n<128 or p+20+n>len(b):continue
        name=b[p+12:p+12+n]
        if not all(32<=v<127 for v in name):continue
        yield p,name.decode(),p+20+n

def shape_metadata(b):
    result=[]
    for typ,(kind,delta) in TYPES.items():
        for p,name,q in nodes(b,typ):
            q+=delta
            if q+12>len(b):continue
            off,unknown,count,material=struct.unpack_from('<IHHI',b,q)
            if count and off%16==0:result.append(dict(name=name,kind=kind,offset=off,packets=count,material=f'{material:08x}',node_offset=p))
    return sorted(result,key=lambda z:z['offset'])
def vertex_packets(b,offset,end):
    for m in re.finditer(re.escape(SIG),b[offset:end]):
        p=offset+m.start()-1
        if p<offset or p+10>end or b[p+9]!=0x78:continue
        n=b[p+8]; q=p+10+12*n
        if not 3<=n<=64 or q+16>end or b[q+7:q+14]!=b'\x20\x40\x40\x40\x40\x21\x80':continue
        a=np.frombuffer(b,dtype='<f4',count=n*3,offset=p+10).reshape(-1,3).copy()
        if np.isfinite(a).all() and np.max(np.abs(a))<1000000:yield p,a

def collision_mesh(b,name='cmesh_Shape1'):
    for p,n,q in nodes(b,3808459748):
        if n!=name:continue
        q+=49
        if q+8>len(b):continue
        nv,nf=struct.unpack_from('<II',b,q); q+=8
        if not (0<nv<65536 and 0<nf<65536 and q+12*nv+18*nf<=len(b)):continue
        v=np.frombuffer(b,dtype='<f4',count=nv*3,offset=q).reshape(-1,3).copy()
        f=np.frombuffer(b,dtype='<u2',count=nf*3,offset=q+12*nv+12*nf).reshape(-1,3).copy()
        if np.isfinite(v).all() and f.max()<nv:return v,f
    raise ValueError('Collision mesh not validated')

def pxt_groups(b):
    pos=0
    while pos<len(b):
        start=pos
        if b[pos+16:pos+32]!=PX:raise ValueError(f'PXT group header {pos}')
        w,h=struct.unpack_from('<II',b,pos+64); n=w*h
        if n not in (16,256,4096):raise ValueError('PXT CLUT size')
        pos+=112; pal=np.frombuffer(b,dtype=np.uint8,count=n*4,offset=pos).reshape(n,4).copy();pos+=n*4
        # CSM1 palette order for 256 entries: swap the middle 8-entry blocks of every 32.
        if n>=256:
            ids=np.arange(n);pal=pal[(ids&~24)|((ids&8)<<1)|((ids&16)>>1)]
        imgs=[]
        while b[pos:pos+16]==PX:
            w,h=struct.unpack_from('<II',b,pos+48);pos+=96
            if not (0<w<=1024 and 0<h<=1024 and w*h%2==0):raise ValueError('PXT dimensions')
            size=w*h if n>=256 else w*h//2
            if pos+size>len(b):raise ValueError('Truncated PXT')
            raw=np.frombuffer(b,dtype=np.uint8,count=size,offset=pos);pos+=size
            if n==16:
                ix=np.empty(size*2,dtype=np.uint8);ix[::2]=raw&15;ix[1::2]=raw>>4
            else:ix=raw.copy()
            imgs.append((w,h,ix.reshape(h,w)))
        yield start,pal,imgs
        if pos<len(b):pos+=16
    if pos!=len(b):raise ValueError('Trailing PXT data')

def contact_sheet(groups,out):
    cols=12; tile=76; rows=math.ceil(len(groups)/cols); im=Image.new('RGB',(cols*tile,rows*88),(25,28,36));d=ImageDraw.Draw(im)
    for i,(_,pal,imgs) in enumerate(groups):
        if not imgs:
            d.text(((i%cols)*tile+4,(i//cols)*88+30),f"{i:03} CLUT only",fill="white");continue
        w,h,ix=imgs[0]; p=Image.fromarray(pal[ix][:,:,:3]);p.thumbnail((68,68),Image.Resampling.NEAREST);x=(i%cols)*tile;y=(i//cols)*88;im.paste(p,(x+(tile-p.width)//2,y));d.text((x+4,y+69),f'{i:03} {w}x{h}',fill='white')
    im.save(out)

def write_obj(path,v,f=None):
    with path.open('w') as fp:
        fp.write('# Original source coordinates; no world transforms applied\n')
        for x,y,z in v:fp.write(f'v {x:.7g} {y:.7g} {z:.7g}\n')
        if f is None:
            for i in range(len(v)):fp.write(f'p {i+1}\n')
        else:
            for a,b,c in f:fp.write(f'f {int(a)+1} {int(b)+1} {int(c)+1}\n')

def recover(iso,out):
    out.mkdir(exist_ok=True,parents=True);r=records(iso);mh,mb=r[1130];gh,gb=r[1529];shapes=shape_metadata(mb)
    assert len(shapes)==18 and all(gb[s['offset']+23:s['offset']+30]==SIG for s in shapes)
    for i,s in enumerate(shapes):
        end=shapes[i+1]['offset'] if i+1<len(shapes) else len(gb)
        packets=list(vertex_packets(gb,s['offset'],end));s['observed_packets']=len(packets);v=np.concatenate([p[1] for p in packets]);s['vertex_samples']=len(v);s['local_bounds']=[v.min(0).tolist(),v.max(0).tolist()];write_obj(out/(s['name']+'_points.obj'),v)
    boatv,boatf=collision_mesh(r[44][1]);write_obj(out/'boat_collision.obj',boatv,boatf);np.savez(out/'boat_collision.npz',vertices=boatv,faces=boatf)
    ufo=[]
    for name in ('walkable_surface_AShape','cmesh_Shape1'):
        v,f=collision_mesh(r[419][1],name);write_obj(out/('ufo_'+name+'.obj'),v,f);ufo.append(dict(name=name,vertices=len(v),triangles=len(f)))
    groups=list(pxt_groups(r[772][1]));contact_sheet(groups,out/'hub_texture_catalog.png')
    # Pack first mipmap from each group into a PS1-compatible palette+indexed image file.
    # 512px asset is downsampled to 256. Alpha/VRAM layout still need runtime material binding.
    tex=out/'textures';tex.mkdir(exist_ok=True);manifest=[]
    for i,(offset,pal,imgs) in enumerate(groups):
        if len(pal)>256 or not imgs:continue # Multiple CLUT banks require material binding.
        w,h,ix=imgs[0]; ix=ix[::2,::2] if max(w,h)>256 else ix; h,w=ix.shape;n=len(pal)
        rgb=pal.astype(np.uint16); colors=(rgb[:,0]>>3)|((rgb[:,1]>>3)<<5)|((rgb[:,2]>>3)<<10);colors=np.where(colors==0,1,colors);colors=np.where(rgb[:,3]==0,0,colors).astype('<u2')
        raw=ix.tobytes() if n==256 else (ix.ravel()[::2]|(ix.ravel()[1::2]<<4)).tobytes();(tex/f'{i:03}.clut').write_bytes(colors.tobytes());(tex/f'{i:03}.idx').write_bytes(raw)
        manifest.append(dict(id=i,source_offset=offset,width=w,height=h,bpp=8 if n==256 else 4,bytes=len(raw)+2*n,mipmaps=len(imgs)))
    report=dict(source=HUB,spyro_metadata_id=f'{mh:08x}',geometry_id=f'{gh:08x}',geometry_bytes=len(gb),shapes=shapes,boat_collision=dict(vertices=len(boatv),triangles=len(boatf)),ufo_collision=ufo,texture_groups=len(groups),texture_images=sum(len(g[2]) for g in groups),converted_texture_groups=len(manifest),texture_payload_bytes=sum(m['bytes'] for m in manifest),texture_manifest=manifest,limitations='Spyro points only: topology and skeletal transforms not decoded. PXT palette swizzle assumed CSM1; texture-to-material names and alpha semantics not verified. Collision meshes have validated index ranges, not render textures.')
    (out/'recovery.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k not in ('shapes','texture_manifest')}); print([(s['name'],s['packets'],s['observed_packets'],s['vertex_samples']) for s in shapes])
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('iso',type=Path);p.add_argument('out',type=Path);a=p.parse_args();recover(a.iso,a.out)
