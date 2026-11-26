"""Extract original hub placement nodes and source gem/Sparx meshes.
Only collision-supported placements are enabled in the current farm test.
"""
import argparse,json,struct,re,hashlib,collections,wave
from pathlib import Path
import numpy as np
from recover import records,nodes,shape_metadata,vertex_packets
from spyro_mesh import STRIP
from hash08 import fold
ROOT=Path(__file__).resolve().parents[1]
def geometry(b,g,s,end):
 q=s['node_offset']+20+len(s['name']); bounds=np.frombuffer(b,'<f4',6,q).reshape(2,3);vs=[];faces=[]
 pp=list(vertex_packets(g,s['offset'],end));assert len(pp)==s['packets']
 for p,a in pp:
  j=g.find(STRIP,p);n=g[j+9];ls=[k//3 for k in g[j+10:j+25] if k];assert sum(ls)==n and 0<n<=len(a);cur=0;off=len(vs);vs.extend(a[:n])
  for l in ls:
   for k in range(2,l):
    ids=[cur+k-2,cur+k-1,cur+k];t=a[ids]
    if np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0]))>1e-5:faces.append([off+x for x in ids])
   cur+=l
 v=np.array(vs);assert np.max(abs(bounds-np.stack([v.min(0),v.max(0)])))<.01
 return v,np.array(faces)
def lod(v,f,step):
 key=np.rint(v/step).astype(int);_,ix=np.unique(key,axis=0,return_inverse=True);vv=np.zeros((ix.max()+1,3));np.add.at(vv,ix,v);vv=np.rint(vv/np.bincount(ix)[:,None]).astype(int);ff=ix[f];ff=ff[np.array([len(set(x))==3 for x in ff])];_,idx=np.unique(np.sort(ff,axis=1),axis=0,return_index=True);ff=ff[np.sort(idx)];return vv[ff]
def colorize(tri,base):
 # Facet color, approximating the original PS2 specular materials; no exact shader claim.
 n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);norm=np.maximum(np.linalg.norm(n,axis=1),1);n=n/norm[:,None];s=.58+.42*np.abs(n@np.array([.34,-.88,.33]));rgb=np.clip(np.rint(s[:,None]*base),0,255).astype(int);return rgb[:,0]|rgb[:,1]<<8|rgb[:,2]<<16
def extract(iso,out):
 out.mkdir(parents=True,exist_ok=True);r=records(iso);b=r[1402][1];z=np.load(ROOT/'build_m11/play/farm06.npz');grid=z['floor'];origin=z['source_origin'];placements=[];others=[]
 for p,n,q in nodes(b,0x2a29015d):
  if b[q+68:q+77]!=b'Character' or struct.unpack_from('<I',b,q+77)[0]!=2:continue
  ln=struct.unpack_from('<I',b,q+81)[0];edf=b[q+85:q+85+ln].decode('ascii');pos=struct.unpack_from('<3f',b,q);assert pos==struct.unpack_from('<3f',b,q+24) and np.isfinite(pos).all();v=np.rint((np.array(pos)-origin)*[1,-1,1]).astype(int);x,y,zz=map(int,v);floor=None
  if max(abs(x),abs(zz))<=4096:floor=int(grid[(zz+4160)//128,(x+4160)//128])
  row=dict(name=n.removeprefix('__CNODE'),edf=edf,record_offset=p,source_xyz=list(pos),sector_xyz=v.tolist(),floor=floor)
  m=re.fullmatch(r'gem(\d+)\.edf',edf,re.I)
  if m:row.update(value=int(m[1]),enabled=floor is not None and floor!=32767 and abs(y-floor)<=110);placements.append(row)
  else:others.append(row)
 assert len(placements)==290 and len({p['name'] for p in placements})==290
 active=[p for p in placements if p['enabled']];assert len(active)==3
 assert r[711][1]==r[874][1]
 meshes={};meta=[]
 for val,mi,gi,base in [(1,490,711,[255,48,45]),(2,353,638,[50,245,70]),(5,798,1387,[165,75,245]),(25,1201,326,[255,211,42])]:
  ss=shape_metadata(r[mi][1]);assert len(ss)==1;v,f=geometry(r[mi][1],r[gi][1],ss[0],len(r[gi][1]));t=np.rint(v[f]*[1,-1,1]).astype(int);meshes[val]=(t,colorize(t,np.array(base)));meta.append(dict(value=val,metadata_record=mi,geometry_record=gi,triangles=len(t),name=ss[0]['name']))
 # Sparx geometry: actual rest vertices, with source wing poses switched as a simple approximation.
 b=r[274][1];g=r[365][1];ss=shape_metadata(b);sparx={};sparxmeta=[]
 for i,s in enumerate(ss):
  v,f=geometry(b,g,s,ss[i+1]['offset'] if i+1<len(ss) else len(g));n=s['name'];wing='wing' in n;eyecore='eyecore' in n;white='eyeball_w' in n;base=[207,224,255] if wing else [35,25,45] if eyecore else [245,245,238] if white else [255,194,38];t=lod(v*[1,-1,1],f,1 if wing or eyecore else 4 if white else 6);sparx[n]=(t,colorize(t,np.array(base)));sparxmeta.append(dict(name=n,source_triangles=len(f),lod_triangles=len(t)))
 # Eyeball shells cover the eyes; omit those two shells in the provisional flat-shaded model.
 body=[n for n in sparx if 'wing' not in n and ('eyeball_' not in n or 'eyeball_w' in n)]
 def cmesh(name,parts):
  tris=np.concatenate([x[0] for x in parts]);colors=np.concatenate([x[1] for x in parts]);return f'static const CollectFace {name}[{len(tris)}]={{\n'+',\n'.join('{{'+','.join('{'+','.join(map(str,v))+'}' for v in t)+'},'+str(c)+'u}' for t,c in zip(tris,colors))+'};\n',len(tris)
 h='typedef struct {s16 v[3][3];u32 color;} CollectFace;\n';nums={}
 for val in meshes:
  s,n=cmesh('gemmesh'+str(val),[meshes[val]]);h+=s;nums[val]=n
 s,bodycount=cmesh('sparxbody',[sparx[n] for n in body]);h+=s
 wings=[]
 for j,pair in enumerate(['fc','eb','da']):
  s,n=cmesh('sparxwing'+str(j),[sparx['spx_wing_'+k+'Shape'] for k in pair]);h+=s;wings.append(n)
 cap=sum(nums[p['value']] for p in active)+bodycount+max(wings);h+=f'#define GEM_COUNT {len(active)}\n#define COLLECT_MESH_MAX {cap}\nstatic const s16 gempos[GEM_COUNT][4]={{'+','.join('{'+','.join(map(str,p['sector_xyz']+[p['value']]))+'}' for p in active)+'};\n';(out/'collectdata12.h').write_text(h)
 audio=[]
 for name in ['gemhit1.vag','csprxpu.vag']:
  k=fold(name.encode());i,b=next((i,b) for i,(h,b) in r.items() if h==k);size,rate=struct.unpack_from('>II',b,12);data=b[48:];assert size==len(data) and size%16==0 and rate==22050;assert all((x>>4)<=4 and (x&15)<=12 for x in data[::16]);head=bytearray(b[:48]);head[:4]=b'VAGp';struct.pack_into('>I',head,4,0x20);head[32:48]=name.split('.')[0].encode().ljust(16,b'\0');(out/name).write_bytes(head+data);audio.append(dict(name=name,record=i,bytes=size,rate=rate,sha256=hashlib.sha256(data).hexdigest(),note='Original ADPCM payload; standard VAG header reconstructed. Not yet wired to SPU.'))
 rep=dict(source_record=1402,source_hash='daf98a3f',gem_count=len(placements),denominations=dict(collections.Counter(x['value'] for x in placements)),direct_gem_value=sum(x['value'] for x in placements),active=active,other_character_count=len(others),gem_meshes=meta,sparx_meshes=sparxmeta,sparx_body_triangles=bodycount,sparx_wing_triangles=wings,collect_mesh_capacity=cap,audio=audio,limitations='Original positions; enabled only collision-confirmed farm points. No breakable-container treasure or enemy AI. Gem and Sparx flat facet colors, approximate wing switching and follow behavior; no original Sparx skinning or material shaders.')
 (out/'placements.json').write_text(json.dumps(dict(gems=placements,other_characters=others),indent=2));(out/'collect_report.json').write_text(json.dumps(rep,indent=2));print('placements',len(placements),len(others),'active',len(active),'cap',cap,'sparx',bodycount,wings)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('iso',type=Path);p.add_argument('out',type=Path);a=p.parse_args();extract(a.iso,a.out)
