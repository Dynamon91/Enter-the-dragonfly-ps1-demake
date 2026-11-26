"""Recover selected original CCC main meshes and source placement transforms."""
import argparse,json,math,re,struct,hashlib,zlib
from pathlib import Path
import numpy as np
from cnk import entries,u32
from recover import nodes,shape_metadata,vertex_packets
from collect12 import geometry
from spyro_mesh import STRIP,UV
from hash08 import fold
from ccc56 import texture_directory
from PIL import Image
# explicit verified metadata / geometry pairs; original material hashes resolved below
MODELS=[('cow',393,938,['cow_bodyShape'],30,r'CCC_HERDING_COW_\d+\.edf'),('farmer',823,86,['FarmerShape'],40,r'CCC_FARMER_\w+\.edf'),('chicken',429,152,['chicken_objShape'],18,r'CHICKEN\.edf'),('riptoc',701,1033,['bigfat_raygun_riptoc1Shape'],55,r'BIG_FAT_RAY_GUN_RIPTOC\.edf'),('spacecow',160,1157,['Space_Cow_BodyShape'],45,r'SPACE_COW\.edf'),('urn',344,None,['Blue_urnShape'],22,r'B_URN\.edf'),('platform',1201,None,['ufo_toShape','ufo_bottomShape'],90,r'CCC_LEVEL_UFO_PLATFORM_\d+\.edf')]
def get_texture(b,h,reg,groups):
    matches=set()
    for p,n,q in nodes(b,0x47ba46ed):
        if u32(b,p+4)!=h or q+100>len(b):continue
        for pp,nn,qq in nodes(b,0xdad78930):
            if u32(b,pp+4)!=u32(b,q+96):continue
            m=re.search(rb'[0-9A-F]{8}\.PXT',b[qq:qq+150]);
            if not m or qq+m.end()+10>len(b):continue
            w,hh,_,size=struct.unpack_from('<HHHI',b,qq+m.end());name=m.group();e=reg.get(fold(name.lower()))
            if e and e['size']==size and e['dimensions']==[w,hh] and e['palette'] in (16,256):matches.add((e['group'],name.decode()))
    if len(matches)!=1:raise ValueError(('material ambiguous',hex(h),matches))
    return next(iter(matches))
def mesh(b,g,s,end):
    v,f=geometry(b,g,s,end);uv=[];pp=list(vertex_packets(g,s['offset'],end))
    for i,(p,a) in enumerate(pp):
        stop=pp[i+1][0] if i+1<len(pp) else end;q=g.find(STRIP,p,stop);u=g.find(UV,q,stop);n=g[q+9]
        assert q>=p and u>q and u+9+8*n<=stop
        uv.extend(np.frombuffer(g,'<f4',2*n,u+9).reshape(-1,2))
    uv=np.asarray(uv);assert len(v)==len(uv) and np.isfinite(uv).all()
    return v,f,uv

def build(cnk,bindings,out):
    out.mkdir(parents=True,exist_ok=False);b=cnk.read_bytes();r={i:b[o:o+s] for i,h,o,s,t in entries(b)};reg,groups,_=texture_directory(r[323],r[580]);obj=json.loads(bindings.read_text())['objects'];placements={p:(n,q) for p,n,q in nodes(r[379],0x2a29015d)};models=[];rows=[];arrays={};header=[];bank=bytearray()
    for mi,(name,metadata,gi,names,step,pattern) in enumerate(MODELS):
        mb=r[metadata];ss=shape_metadata(mb);parts=[];tex=set();report=[]
        for n in names:
            j,s=next((j,s) for j,s in enumerate(ss) if s['name']==n);cand=[]
            for k,g in ([(gi,r[gi])] if gi is not None else r.items()):
                if g[s['offset']+23:s['offset']+30]!=b'\x20\x40\x40\x40\x40\x01\x80':continue
                end=ss[j+1]['offset'] if j+1<len(ss) else len(g)
                try:v,f,uv=mesh(mb,g,s,end);cand.append((k,v,f,uv))
                except (AssertionError,ValueError,IndexError):continue
            assert len(cand)==1,(name,n,[x[0] for x in cand]);k,v,f,uv=cand[0];group,fn=get_texture(mb,int(s['material'],16),reg,groups);tex.add((group,fn));parts.append((v,f,uv));report.append(dict(shape=n,geometry_record=k,source_triangles=len(f),bounds=[v.min(0).tolist(),v.max(0).tolist()],group=group))
        assert len(tex)==1;group,fn=next(iter(tex));pal,imgs=groups[group];w,h,ix=imgs[0];rgb=pal.astype(np.uint16);clut=np.maximum((rgb[:,0]>>3)|((rgb[:,1]>>3)<<5)|((rgb[:,2]>>3)<<10),1).astype('<u2');clut=np.pad(clut,(0,256-len(clut)));pix=np.asarray(Image.fromarray(ix).resize((64,64),Image.Resampling.NEAREST))
        vv=[];ff=[];uvv=[];source=0
        for v,f,uv in parts:
            # Cluster positions; preserve UV per original face corner, no welding across UV seams.
            v=v*[1,-1,1];key=np.rint(v/step).astype(int);_,inv=np.unique(key,axis=0,return_inverse=True);verts=np.zeros((inv.max()+1,3));np.add.at(verts,inv,v);verts=np.rint(verts/np.bincount(inv)[:,None]).astype(np.int16);f2=inv[f];keep=np.array([len(set(a))==3 for a in f2]);keep &= np.any(np.cross(verts[f2[:,1]].astype(int)-verts[f2[:,0]],verts[f2[:,2]].astype(int)-verts[f2[:,0]]),axis=1);ids=np.flatnonzero(keep);_,uniq=np.unique(np.sort(f2[ids],axis=1),axis=0,return_index=True);ids=ids[np.sort(uniq)];source+=len(f);ff.extend(f2[ids]+len(vv));vv.extend(verts);st=np.rint(uv[f[ids]]*1024).astype(int);st-=np.floor_divide(st.min(axis=1,keepdims=True),1024)*1024;assert st.min()>=0 and st.max()<4096,(name,st.max());uvv.extend(st)
        v=np.array(vv,dtype=np.int16);f=np.array(ff,dtype=np.uint16);uv=(np.array(uvv,dtype=np.int16)//16).astype(np.uint8);assert len(v)<65536 and np.max(np.abs(v))<8192
        arrays.update({name+'_v':v,name+'_f':f,name+'_uv':uv,name+'_pal':clut,name+'_pix':pix});
        arr=lambda a:','.join(map(str,np.asarray(a).reshape(-1).tolist()));header.append(f'static const s16 {name}v59[{len(v)}][3]={{'+','.join('{'+arr(x)+'}' for x in v)+'};');header.append(f'static const ActorFace59 {name}f59[{len(f)}]={{'+','.join('{{'+arr(face)+'},{'+arr(st)+'}}' for face,st in zip(f,uv))+'};');payload=clut.tobytes()+pix.tobytes();crc=zlib.crc32(payload);bank.extend((struct.pack('<4sHHIIII',b'ETDT',1,mi,w,h,len(payload),crc)+payload).ljust(6144,b'\0'));
        count=0
        for o in obj:
            if not re.fullmatch(pattern,o['edf'],re.I):continue
            n,q=placements[o['source_id']];assert n==o['name'];angles=struct.unpack_from('<3f',r[379],q+12);assert all(math.isfinite(a) for a in angles);xyz=np.rint(np.array(o['source_xyz'])*[1,-1,1]).astype(int);yaw=int(round(angles[1]*32/math.pi))%64;rows.append(dict(source_id=o['source_id'],name=n,edf=o['edf'],xyz=xyz.tolist(),angles=list(angles),yaw=yaw,model=mi));count+=1
        models.append(dict(name=name,metadata_record=metadata,parts=report,texture=fn,group=group,source_triangles=source,vertices=len(v),native_triangles=len(f),placements=count,cluster_step=step,texture_crc=crc));print(name,source,len(f),len(v),count,flush=True)
    header.insert(0,'typedef struct {u16 ix[3];U8 uv[6];} ActorFace59;');header.append('typedef struct {const s16 (*v)[3];const ActorFace59*f;int nf;U32 crc;} ActorModel59;');header.append('static const ActorModel59 models59[]={'+','.join('{'+f'{m["name"]}v59,{m["name"]}f59,{m["native_triangles"]},{m["texture_crc"]}u'+'}' for m in models)+'};');header.append('typedef struct {int x,y,z;U8 model,yaw;} ActorPlacement59;');header.append('static const ActorPlacement59 actors59[]={'+','.join('{'+arr(a['xyz']+[a['model'],a['yaw']])+'}' for a in rows)+'};');(out/'actorsdata59.h').write_text('\n'.join(header)+'\n');np.savez_compressed(out/'actors59.npz',**arrays);(out/'CCCACT.DAT').write_bytes(bank)
    # preserve original conversation command references, no invented dialogue/rewards
    scripts=[]
    for i,s in r.items():
        if b'conversation script for a talking character' in s:
            t=s.decode('ascii',errors='replace');scripts.append(dict(record=i,sha256=hashlib.sha256(s).hexdigest(),name_ids=re.findall(r'^\s*Name\s*:\s*(\d+)',t,re.M),branches=re.findall(r'^\s*Branch\s+(\d+)',t,re.M),dialogue_ids=re.findall(r'^\s*(?:Say|Player|Sparx)\s+(\d+)',t,re.M)))
    rep=dict(source_sha256=hashlib.sha256(b).hexdigest(),models=models,placements=rows,conversation_scripts=scripts,limitations='Main body only, missing face/accessory submeshes and skeletal animation; static yaw quantized from original placement radians; X/Z Euler rotations not applied; original 64x64 resampled opaque textures; no interaction or AI yet. UFO platform model mapping based on original texture node name and placement class.')
    (out/'report59.json').write_text(json.dumps(rep,indent=2)+'\n');return rep
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('cnk',type=Path);p.add_argument('bindings',type=Path);p.add_argument('out',type=Path);a=p.parse_args();build(a.cnk,a.bindings,a.out)
