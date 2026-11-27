"""Recover exact named UFO/cannon records, source geometry and flight control points."""
import argparse,hashlib,json,struct,re,math,zlib
from pathlib import Path
import numpy as np
from PIL import Image
from cnk import entries
from recover import shape_metadata,nodes
from actors59 import mesh,get_texture
from ccc56 import texture_directory
from hash08 import fold
MODELS=[('cannon','ccc_level_cannon.mrb',446,1230,['pSphereShape1','pTorusShape1','polySurfaceShape24','polySurfaceShape25','polySurfaceShape27','polySurfaceShape31','worp_coreShape','polySurfaceShape29'],35),('ufo','ccc_level_ufo.mrb',716,824,['LightsShape','ShutterShape','BodyShape','CanopyShape'],24),('pole','electric_pole.mrb',863,622,['polySurfaceShape1','pole_surfaceShape'],12)]
def build(cnk,bindings,out):
 b=cnk.read_bytes();ent=list(entries(b));r={i:b[o:o+s] for i,h,o,s,t in ent};hashes={i:h for i,h,o,s,t in ent};reg,groups,_=texture_directory(r[323],r[580]);out.mkdir(exist_ok=False,parents=True)
 tab=r[1125];directory={h:(o-len(tab),s) for h,o,s,f in (struct.unpack_from('<4I',tab,16+i*16) for i in range(104))}
 def edf(name):
  o,s=directory[fold(name.encode())];return r[719][o:o+s]
 rows=[];objects=json.loads(bindings.read_text())['objects'];poses={p:struct.unpack_from('<6f',r[379],q) for p,n,q in nodes(r[379],0x2a29015d)}
 for i in range(1,5):
  name=f'ccc_ufo_cannon_{i}.edf';e=edf(name);assert b'Lightning' in e and all(re.search(rb'WorldFlag_On\s+2 '+str(j).encode()+rb'\b',e) for j in [0]+list(range(3,2+i)))
  script=r[(121,730,665,1029)[i-1]];assert re.search(rb'WorldFlagOn\s+2 '+str(i+2).encode()+rb'\b',script)
  a=next(o for o in objects if o['edf'].lower()==name);p=poses[a['source_id']];rows.append(dict(source_id=a['source_id'],xyz=[round(p[0]),round(-p[1]),round(p[2])],yaw=round(p[4]*32/math.pi)%64,flag=i+2,script=(121,730,665,1029)[i-1],edf_hash=hashlib.sha256(e).hexdigest()))
 poles=[]
 for i in range(1,3):
  name=f'ccc_level_ufo_trigger_{i}.edf';e=edf(name);assert b'Lightning' in e and re.search(rb'Flag_Index\s+2 '+str(13+2*i).encode()+rb'\b',e);a=next(o for o in objects if o['edf'].lower()==name);p=poses[a['source_id']];poles.append([round(p[0]),round(-p[1]),round(p[2]),round(p[4]*32/math.pi)%64])
 a=next(o for o in objects if o['edf'].lower()=='ccc_big_ufo.edf');p=poses[a['source_id']];start=[round(p[0]),round(-p[1]),round(p[2])];e=edf('ccc_big_ufo.edf');assert re.search(rb'Flag_Index\s+2 23\b',e) and re.search(rb'Flag_Index\s+2 995\b',e)
 paths=[]
 for i in range(1,5):
  name=f'SHOTShape{i}'.encode();parts=[]
  for record in (379,1012):
   s=r[record];q=s.index(name)+len(name);k=struct.unpack_from('<I',s,q+60)[0];n=struct.unpack_from('<I',s,q+64+4*k)[0];assert n==k-2 and 3<=n<=10;parts.append(s[q+68+4*k:q+68+4*k+12*n])
  assert parts[0]==parts[1] and name in e;paths.append([[round(x),round(-y),round(z)] for x,y,z in struct.iter_unpack('<3f',parts[0])])
 assert all(paths[i][-1]==paths[i+1][0] for i in range(3))
 header=['typedef struct {short v[3][3];unsigned char uv[6],tex;} UfoFace64;'];bank=bytearray();textures={};crc=[];manifest=[];arrays={}
 for name,filename,mid,gid,selected,step in MODELS:
  assert hashes[mid]==fold(filename.encode());ss=shape_metadata(r[mid]);tri=[];uvs=[];slots=[];parts=[]
  for j,s in enumerate(ss):
   if s['name'] not in selected:continue
   v,f,uv=mesh(r[mid],r[gid],s,ss[j+1]['offset'] if j+1<len(ss) else len(r[gid]));group,fn=get_texture(r[mid],int(s['material'],16),reg,groups)
   if group not in textures:
    slot=len(textures);assert slot<13;textures[group]=slot;pal,imgs=groups[group];w,h,ix=imgs[0];rgb=pal.astype(np.uint16);clut=np.maximum((rgb[:,0]>>3)|((rgb[:,1]>>3)<<5)|((rgb[:,2]>>3)<<10),1).astype('<u2');clut=np.pad(clut,(0,256-len(clut)));pix=np.asarray(Image.fromarray(ix).resize((64,64),Image.Resampling.NEAREST));payload=clut.tobytes()+pix.tobytes();c=zlib.crc32(payload);crc.append(c);bank.extend((struct.pack('<4sHHIIII',b'ETDT',1,slot,w,h,len(payload),c)+payload).ljust(6144,b'\0'))
   v=v*[1,-1,1];_,inv=np.unique(np.rint(v/step).astype(int),axis=0,return_inverse=True);vv=np.zeros((inv.max()+1,3));np.add.at(vv,inv,v);vv=np.rint(vv/np.bincount(inv)[:,None]).astype(int);ff=inv[f];t=vv[ff];ids=np.flatnonzero(np.any(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1));_,keep=np.unique(np.sort(ff[ids],axis=1),axis=0,return_index=True);ids=ids[np.sort(keep)];st=np.rint(uv[f[ids]]*64).astype(int);st-=np.floor_divide(st.min(axis=1,keepdims=True),64)*64
   assert st.min()>=0 and st.max()<256;tri.extend(t[ids]);uvs.extend(st);slots.extend([textures[group]]*len(ids));parts.append(dict(name=s['name'],source=len(f),native=len(ids),group=group))
  arr=lambda a:','.join(map(str,np.asarray(a).reshape(-1).tolist()));header.append('static const UfoFace64 '+name+'64[]={'+','.join('{{'+','.join('{'+arr(x)+'}' for x in t)+'},{'+arr(u)+'},'+str(k)+'}' for t,u,k in zip(tri,uvs,slots))+'};');arrays.update({name:np.array(tri),name+'_uv':np.array(uvs),name+'_tex':np.array(slots)});manifest.append(dict(name=name,metadata=mid,geometry=gid,parts=parts,triangles=len(tri)))
 arr=lambda a:','.join(map(str,a));header+=['#define UFO_TEX64 '+str(len(crc)),'static const unsigned ufo_crc64[]={'+arr(crc)+'};','static const int cannonpos64[4][4]={'+','.join('{'+arr(a['xyz']+[a['yaw']])+'}' for a in rows)+'};','static const int polepos64[2][4]={'+','.join('{'+arr(a)+'}' for a in poles)+'};','static const int ufostart64[3]={'+arr(start)+'};','static const short ufopath64[][3]={'+','.join('{'+arr(a)+'}' for p in paths for a in p)+'};','static const unsigned char ufooff64[5]={'+arr(np.cumsum([0]+list(map(len,paths))).tolist())+'};'];(out/'ufodata64.h').write_text('\n'.join(header)+'\n');(out/'CCCUFO.DAT').write_bytes(bank);np.savez_compressed(out/'ufo64.npz',**arrays);report=dict(source_sha256=hashlib.sha256(b).hexdigest(),cannons=rows,poles=poles,start=start,paths=paths,models=manifest,textures=textures,texture_bytes=len(bank),limits='Selected static source meshes, opaque 64x64 indexed textures; pitch/roll and original animation omitted; source flight control points interpolated linearly. Pole geometry recovered, platform transport not implemented.');(out/'ufo64.json').write_text(json.dumps(report,indent=2)+'\n');print([(m['name'],m['triangles']) for m in manifest],len(textures),[len(p) for p in paths]);return report
if __name__=='__main__':
 p=argparse.ArgumentParser();[p.add_argument(x,type=Path) for x in ('cnk','bindings','out')];a=p.parse_args();build(a.cnk,a.bindings,a.out)
