"""Restore original Luau background and alpha-aware indexed water textures."""
import argparse,hashlib,json,re,struct,zlib
from pathlib import Path
import numpy as np
from PIL import Image
from cnk import entries,u32
from recover import nodes
from hash08 import fold
from luau66 import texture_directory
SKY=(0x16f39d82,0xfa955495,0x12c2e6ac,0x47f94f8a)
WATER=(0x6ba105a3,0x7aa0c139,0x98194640,0xc0ab07d0,0xc308adc5)
def build(cnk,geometry,assets,out):
    out.mkdir(exist_ok=False,parents=True);b=cnk.read_bytes();r={i:b[o:o+s] for i,h,o,s,t in entries(b)};reg,groups,_=texture_directory(r[333],r[612]);meta=r[394];refs={}
    for p,n,q in nodes(meta,0x47ba46ed):
        h=u32(meta,p+4)
        if h not in SKY+WATER or q+100>len(meta):continue
        for pp,nn,qq in nodes(meta[q+96:q+800],0xdad78930):
            if u32(meta,q+96+pp+4)!=u32(meta,q+96):continue
            qq+=q+96;m=re.search(rb'[0-9A-F]{8}\.PXT',meta[qq:qq+150]);
            if m and qq+m.end()+10<=len(meta):
                w,hh,_,s=struct.unpack_from('<HHHI',meta,qq+m.end());e=reg.get(fold(m.group().lower()))
                if e and e['size']==s and e['dimensions']==[w,hh] and e['palette'] in (16,256):refs.setdefault(h,set()).add(e['group'])
            break
    assert set(refs)==set(SKY+WATER) and all(len(v)==1 for v in refs.values());refs={h:next(iter(v)) for h,v in refs.items()}
    def texture(g,opaque=False,additive=False):
        pal,imgs=groups[g];w,h,ix=imgs[0];p=pal.astype(np.uint16);c=np.maximum((p[:,0]>>3)|((p[:,1]>>3)<<5)|((p[:,2]>>3)<<10),1)
        # PS2 alpha has more levels; transparent zero, 1..127 -> half blend,
        # 128+ opaque. Index zero is not assumed transparent without source alpha.
        if additive:c=np.where((p[:,0]>>3)|(p[:,1]>>3)|(p[:,2]>>3),c|0x8000,0)
        elif not opaque:c=np.where(p[:,3]==0,0,np.where(p[:,3]<128,c|0x8000,c))
        c=np.pad(c.astype('<u2'),(0,256-len(c)));pix=np.asarray(Image.fromarray(ix).resize((64,64),Image.Resampling.NEAREST));return c,pix,dict(group=g,source_size=[w,h],alpha=np.unique(pal[ix][:,:,3]).tolist())
    pal=[];pix=[];details=[]
    for i,h in enumerate(SKY):
        p,t,m=texture(refs[h],i==0,i in (1,2));pal.append(p);pix.append(t);details.append(dict(hash=f'{h:08x}',**m))
    with np.load(geometry,allow_pickle=False) as g:
        xyz=np.rint(g['vertices'][g['faces']]*[1,-1,1]/128).astype(np.int64);uv=np.rint(g['uv'][g['faces']]*1024).astype(np.int64);layers=np.array([SKY.index(int(h)) for h in g['material']]);tri=np.concatenate([xyz,uv],axis=2)
    keep=np.any(np.cross(xyz[:,1]-xyz[:,0],xyz[:,2]-xyz[:,0]),axis=1);order=np.argsort(layers[keep],kind='stable');tri=tri[keep][order].astype(np.int16);layers=layers[keep][order];assert np.max(abs(tri))<8192
    arr=lambda a:','.join(map(str,np.asarray(a).reshape(-1).tolist()));lines=[f'#define SKY_N67 {len(tri)}','typedef struct {s16 v[3][5];u16 layer;} SkyTri67;','static const SkyTri67 sky_triangles67[SKY_N67]={']
    for t,k in zip(tri,layers):lines.append('{{'+','.join('{'+arr(x)+'}' for x in t)+'},'+str(k)+'},')
    lines+=['};','static const u16 sky_pal67[4][256]={'+','.join('{'+arr(x)+'}' for x in pal)+'};','static const U8 sky_pix67[4][4096]={'+','.join('{'+arr(x)+'}' for x in pix)+'};'];(out/'skydata67.h').write_text('\n'.join(lines)+'\n');np.savez_compressed(out/'sky67.npz',triangles=tri,layers=layers,palettes=np.array(pal),pixels=np.array(pix))
    materials=json.loads((assets/'bindings.json').read_text())['materials'];water={m['id']:refs[int(m['hash'],16)] for m in materials if int(m['hash'],16) in WATER};assert set(water.values())=={refs[h] for h in WATER}
    data=bytearray((assets/'LIATEX.DAT').read_bytes());idx=bytearray((assets/'LIATEX.IDX').read_bytes());report=[]
    for i in range((len(idx)-12)//12):
        g,lba,crc=struct.unpack_from('<III',idx,12+i*12)
        if g not in water.values():continue
        p,t,info=texture(g);off=lba*2048;payload=p.tobytes()+t.tobytes();assert data[off+536:off+4632]==t.tobytes();crc=zlib.crc32(payload);data[off+24:off+4632]=payload;struct.pack_into('<I',data,off+20,crc);struct.pack_into('<I',idx,12+i*12+8,crc);report.append(info)
    assert len(report)==5;(out/'LIATEX.DAT').write_bytes(data);(out/'LIATEX.IDX').write_bytes(idx)
    (out/'watermat67.h').write_text('static int watermat67(int m){return '+ '||'.join('m=='+str(k) for k in sorted(water))+';}\nstatic int surface67(int m){return '+ '||'.join('m=='+str(m['id']) for m in materials if m['hash'] in ('7aa0c139','98194640'))+';}\n')
    result=dict(source_sha256=hashlib.sha256(b).hexdigest(),sky_shapes=14,sky_source_faces=len(keep),sky_faces=len(tri),sky_materials=details,water_materials=water,water_textures=report,limitations='Source sky scaled camera-relative; layer ordering, additive sun/rays black key and half-blend approximate. No original alpha equations or animated clouds. Water palette conversion only, no new geometry inserted into terrain.')
    (out/'report67.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();[p.add_argument(k,type=Path) for k in ('cnk','geometry','assets','out')];a=p.parse_args();build(a.cnk,a.geometry,a.assets,a.out)
