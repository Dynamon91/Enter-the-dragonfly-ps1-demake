"""Extract original PS2 save icon and make a PS1 GPU packet demo, not gameplay."""
import argparse, struct, json, math
from pathlib import Path
from cnk import ISO
import numpy as np
from PIL import Image, ImageDraw

def parse(b):
    magic,shapes,kind,_,n=struct.unpack_from('<5I',b)
    if magic!=0x10000 or not 1<=shapes<=32 or not n or n%3: raise ValueError('Bad icon')
    stride=8*shapes+16; end=20+n*stride
    if end+20>len(b): raise ValueError('Truncated vertices')
    v=np.frombuffer(b[20:end],dtype='<i2').reshape(n,stride//2)
    pos=v[:,:3].astype(float); uv=v[:,4*shapes+4:4*shapes+6].astype(float)/4096
    a,frames,speed,play,count=struct.unpack_from('<IIfII',b,end); p=end+20
    if a!=1 or count>shapes: raise ValueError('Bad animation')
    for _ in range(count):
        shape,keys=struct.unpack_from('<II',b,p); p+=8+8*keys
        if p>len(b) or shape>=shapes: raise ValueError('Bad animation keys')
    if kind&8:
        size=struct.unpack_from('<I',b,p)[0]; p+=4; limit=p+size; pixels=[]
        if limit!=len(b): raise ValueError('Compressed texture length mismatch')
        while p<limit:
            run=struct.unpack_from('<h',b,p)[0]; p+=2
            if run<0:
                if p-2*run>limit: raise ValueError('Truncated literal')
                pixels.extend(struct.unpack_from('<'+str(-run)+'H',b,p)); p-=2*run
            elif run>0:
                if p+2>limit: raise ValueError('Truncated repeat')
                val=struct.unpack_from('<H',b,p)[0];p+=2; pixels.extend([val]*run)
            else: raise ValueError('Zero RLE run')
            if len(pixels)>16384: raise ValueError('Texture overflow')
        if len(pixels)!=16384: raise ValueError('Texture size mismatch')
        tex=np.array(pixels,dtype=np.uint16).reshape(128,128)
    else:
        if len(b)-p!=32768: raise ValueError('Bad uncompressed texture')
        tex=np.frombuffer(b[p:],dtype='<u2').reshape(128,128)
    rgb=np.stack([(tex&31)*255//31,((tex>>5)&31)*255//31,((tex>>10)&31)*255//31],axis=-1).astype(np.uint8)
    return pos,uv,rgb,dict(vertices=n,triangles=n//3,shapes=shapes,texture_type=kind,animation_frames=frames,texture_bytes=32768)

def geometry(pos,uv,yaw):
    # Icon coordinate convention: camera-space positive y goes down.
    a=math.radians(yaw); c,s=math.cos(a),math.sin(a)
    x=pos[:,0]*c+pos[:,2]*s; z=-pos[:,0]*s+pos[:,2]*c; y=pos[:,1]
    pitch=math.radians(-12); y,z=y*math.cos(pitch)-z*math.sin(pitch),y*math.sin(pitch)+z*math.cos(pitch)
    scale=min(258/max(np.ptp(x),1),182/max(np.ptp(y),1)); x=(x-(x.max()+x.min())/2)*scale+160;y=(y-(y.max()+y.min())/2)*scale+120
    xy=np.rint(np.stack([x,y],axis=1)).astype(int); tex=np.clip(np.rint(uv*127),0,127).astype(int)
    # far to near, using camera looking along +Z
    order=np.argsort(-z.reshape(-1,3).mean(axis=1),kind='stable')
    return xy,tex,order

def render(xy,uv,order,rgb):
    img=np.zeros((240,320,3),np.uint8);img[:]=[22,27,47]
    for i in order:
        pts=xy[i*3:i*3+3]; t=uv[i*3:i*3+3]; x0,y0=pts.min(axis=0);x1,y1=pts.max(axis=0)
        x0=max(0,x0);y0=max(0,y0);x1=min(319,x1);y1=min(239,y1)
        if x1<x0 or y1<y0: continue
        x,y=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5)
        a,b,c=pts; d=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1]);
        if not d:continue
        w0=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/d; w1=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/d; w2=1-w0-w1
        mask=(w0>=0)&(w1>=0)&(w2>=0); u=np.clip((w0*t[0,0]+w1*t[1,0]+w2*t[2,0]).astype(int),0,127);v=np.clip((w0*t[0,1]+w1*t[1,1]+w2*t[2,1]).astype(int),0,127)
        img[y0:y1+1,x0:x1+1][mask]=rgb[v,u][mask]
    return Image.fromarray(img)

def make(iso,out,yaw):
    out.mkdir(parents=True,exist_ok=True)
    with ISO(iso) as d: pos,uv,rgb,meta=parse(d.file('SPYRO1.ICO'))
    xy,uv,order=geometry(pos,uv,yaw)
    # 8-bit CLUT, texture at (384,0), CLUT at (384,128) in VRAM words.
    q=Image.fromarray(rgb).quantize(colors=256,dither=Image.Dither.NONE); palette=np.array(q.getpalette(),dtype=np.uint16).reshape(-1,3)[:256]; words=(palette[:,0]>>3)|((palette[:,1]>>3)<<5)|((palette[:,2]>>3)<<10); words[words==0]=0x8000 # opaque black, no semi-transparent primitive
    indices=np.array(q,dtype=np.uint8); pal_rgb=np.stack([(words&31)*255//31,((words>>5)&31)*255//31,((words>>10)&31)*255//31],axis=1).astype(np.uint8)
    # GPU data transfer commands plus texture-page / CLUT selectors.
    def xyword(x,y):return (int(x)&0xffff)|((int(y)&0xffff)<<16)
    def upload(x,y,w,h,data):return [0xa0000000,xyword(x,y),xyword(w,h),*struct.unpack('<'+'I'*(len(data)//4),data)]
    cmds=upload(384,0,64,128,indices.tobytes())+upload(384,128,256,1,words.astype('<u2').tobytes())
    cmds += [0xe1000000,0xe3000000,0xe4000000|319|(239<<10),0xe5000000,0xe6000000,0x02000000|22|(27<<8)|(47<<16),0,xyword(320,240)]
    clut=(384//16)|(128<<6); page=(384//64)|(1<<7)
    for i in order:
        p=xy[i*3:i*3+3]; t=uv[i*3:i*3+3]; cmds.append(0x25000000) # raw textured triangle
        for j in range(3):cmds.extend([xyword(*p[j]),int(t[j,0])|(int(t[j,1])<<8)|((clut if j==0 else page if j==1 else 0)<<16)])
    (out/'packets.bin').write_bytes(struct.pack('<'+'I'*len(cmds),*cmds)); (out/'packets.h').write_text('static const unsigned packets[] = {\n'+',\n'.join(','.join(f'0x{x:08x}u' for x in cmds[i:i+8]) for i in range(0,len(cmds),8))+'\n};\n')
    preview=render(xy,uv,order,pal_rgb[indices]); preview.resize((640,480),Image.Resampling.NEAREST).save(out/'preview.png')
    meta.update(yaw=yaw,packet_bytes=len(cmds)*4,texture_vram_bytes=16384,palette_vram_bytes=512,framebuffer_bytes=320*240*2,format='8-bit CLUT, static painter-sorted GPU packets',source='SPYRO1.ICO (save icon, not in-game player model)')
    (out/'icon.json').write_text(json.dumps(meta,indent=2));print(meta)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('iso',type=Path);p.add_argument('out',type=Path);p.add_argument('--yaw',type=float,default=35);a=p.parse_args();make(a.iso,a.out,a.yaw)
