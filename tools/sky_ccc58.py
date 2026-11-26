"""Recover the original CCC sky from CNK 510/484 and generate fixed VRAM assets."""
import argparse,hashlib,json,re,struct
from pathlib import Path
import numpy as np
from PIL import Image
from cnk import entries,u32
from recover import nodes
from hash08 import fold
from ccc56 import texture_directory
from classic_mesh50 import recover
# Opaque night dome, distant hills, then original alpha materials.
ORDER=(0x1149d210,0x7c8270e4,0xcaa82006,0x6a30639a,0x6d113cdb,0x7e947116,0x47f94f8a)
BLEND=(0,0,0,0,0,1,1)
def build(cnk,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    report=recover(cnk,510,'.*',out/'geometry');assert report['selected']==report['matched']==23 and not report['unmatched']
    b=Path(cnk).read_bytes();r={i:b[o:o+s] for i,h,o,s,t in entries(b)};reg,groups,empty=texture_directory(r[323],r[580]);meta=r[510];refs={}
    for p,n,q in nodes(meta,0x47ba46ed):
        if q+100>len(meta):continue
        h=u32(meta,p+4);t=u32(meta,q+96)
        if h not in ORDER:continue
        for pp,nn,qq in nodes(meta,0xdad78930):
            if u32(meta,pp+4)!=t:continue
            m=re.search(rb'[0-9A-F]{8}\.PXT',meta[qq:qq+150])
            if not m or qq+m.end()+10>len(meta):continue
            fn=m.group().decode();w,hh,_,s=struct.unpack_from('<HHHI',meta,qq+m.end());e=reg.get(fold(fn.lower().encode()))
            if e and e['size']==s and e['dimensions']==[w,hh] and e['palette'] in (16,256):refs.setdefault(h,set()).add((e['group'],fn))
    assert set(refs)==set(ORDER) and all(len(v)==1 for v in refs.values())
    palettes=[];pixels=[];textures=[]
    for k,h in enumerate(ORDER):
        i,fn=next(iter(refs[h]));pal,imgs=groups[i];w,hh,ix=imgs[0];p=pal.astype(np.uint16);c=(p[:,0]>>3)|((p[:,1]>>3)<<5)|((p[:,2]>>3)<<10)
        c=np.maximum(c,1);c=c|0x8000 if BLEND[k] else c
        c=np.pad(c.astype('<u2'),(0,256-len(c)));pix=np.asarray(Image.fromarray(ix).resize((64,64),Image.Resampling.NEAREST));palettes.append(c);pixels.append(pix)
        Image.fromarray(pal[ix][:,:,:3]).save(out/f'source_{k}.png');textures.append(dict(layer=k,hash=f'{h:08x}',group=i,filename=fn,width=w,height=hh,alpha_used=np.unique(pal[ix][:,:,3]).tolist(),blend=BLEND[k]))
    with np.load(out/'geometry/geometry.npz',allow_pickle=False) as z:
        v=z['vertices'][z['faces']].astype(float);uv=z['uv'][z['faces']].astype(float);layers=np.array([ORDER.index(int(h)) for h in z['material']]);xyz=np.rint(v*[1,-1,1]/64).astype(np.int64);st=np.rint(uv*1024).astype(np.int64);tri=np.concatenate([xyz,st],axis=2)
    assert np.max(abs(tri))<8192 and set(layers)==set(range(7))
    keep=np.any(np.cross(xyz[:,1]-xyz[:,0],xyz[:,2]-xyz[:,0]),axis=1);order=np.argsort(layers[keep],kind='stable');tri=tri[keep][order].astype(np.int16);layers=layers[keep][order].astype(np.uint8)
    np.savez_compressed(out/'sky.npz',triangles=tri,layers=layers,palettes=np.array(palettes),pixels=np.array(pixels))
    arr=lambda a:','.join(map(str,np.asarray(a).reshape(-1).tolist()));lines=[f'#define SKY_N58 {len(tri)}','typedef struct {s16 v[3][5];u16 layer;} SkyTri58;','static const SkyTri58 sky_triangles58[SKY_N58]={']
    for t,k in zip(tri,layers):lines.append('{{'+','.join('{'+arr(x)+'}' for x in t)+'},'+str(k)+'},')
    lines+=['};','static const u16 sky_pal58[7][256]={'+','.join('{'+arr(x)+'}' for x in palettes)+'};','static const U8 sky_pix58[7][4096]={'+','.join('{'+arr(x)+'}' for x in pixels)+'};'];(out/'skydata58.h').write_text('\n'.join(lines)+'\n')
    rep=dict(source_sha256=hashlib.sha256(b).hexdigest(),metadata_record=510,geometry_records=sorted(set(x['record'] for x in report['meshes'])),meshes=23,source_triangles=report['triangles'],packed_triangles=len(tri),collapsed_ids=np.flatnonzero(~keep).tolist(),textures=textures,texture_bytes=7*4608,scale=64,layer_counts=np.bincount(layers).tolist(),limitations='Camera-relative source sky; no animation; source blend modes approximated, opaque dome and half-blend alpha layers, 64x64 resampling, source transforms not independently verified.')
    (out/'report58.json').write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps(rep,indent=2));return rep
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('cnk',type=Path);p.add_argument('out',type=Path);a=p.parse_args();build(a.cnk,a.out)
