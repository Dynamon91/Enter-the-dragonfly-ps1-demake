"""Decode ETD Spyro VIF mesh strips, normals and UV. Provisional rest-pose/material mapping."""
import argparse,json,math
from pathlib import Path
import numpy as np
from PIL import Image
from recover import records,shape_metadata,vertex_packets,pxt_groups,nodes
STRIP=b'\x20\x54\x54\x54\x54\xc1\x80\x10\x72'
UV=b'\x20\x50\x50\x50\x50\x61\x80\x20\x74'
# The named joint local translations are decoded from MRB; parent paths are inferred
# from the serialized skeleton names and validated visually, not an animation decoder.
def joints(mb):
 return {name:np.frombuffer(mb,'<f4',3,q+48).copy() for p,name,q in nodes(mb,0x3d4c8da1)}
def offsets(mb):
 j=joints(mb)
 def chain(*n):return sum((j[k] for k in n),np.zeros(3))
 head=chain('root','belly','chest','neck1','neck2','neck3','head')
 d={'face_objShape':head,'r_hornShape':head,'l_hornShape':head,'r_eyebrowShape':head,'l_eyebrowShape':head,'r_eyelidShape':head,'l_eyelidShape':head,'r_eyeShape':head,'l_eyeShape':head,'finShape':head,'tail_tipShape':chain('root','hip','tail1','tail2','tail3','tail4','tail5')}
 for side in 'rl':
  p=side+'_b_';d[p+'fingersShape']=chain('root','hip',*(p+k for k in ['thigh','knee','foot1','foot2','toe']))
  p=side+'_f_';d[p+'fingersShape']=chain('root','belly','chest',*(p+k for k in ['shoulder','elbow','foot','toe']))
 return d

def decode(mb,gb):
 shapes=shape_metadata(mb);off=offsets(mb); result=[]
 for j,s in enumerate(shapes):
  end=shapes[j+1]['offset'] if j+1<len(shapes) else len(gb);pp=list(vertex_packets(gb,s['offset'],end));assert len(pp)==s['packets'];v=[];norm=[];uv=[];faces=[];strips=0;degenerate=0
  for k,(p,a) in enumerate(pp):
   e=pp[k+1][0] if k+1<len(pp) else end;z=gb[p:e];f=z.find(STRIP);u=z.find(UV);assert f>=0 and u>f and u+9+32*8<=len(z)
   t=z[f+9:f+25];n=t[0]; assert all(x%3==0 for x in t[1:]);lens=[x//3 for x in t[1:] if x];assert 0<n<=len(a) and sum(lens)==n and min(lens)>=3
   ns=np.frombuffer(gb,'<i2',len(a)*3,p+10+len(a)*12+16).reshape(-1,3)[:n].astype(float)/32767
   us=np.frombuffer(z,'<f4',64,u+9).reshape(-1,2)[:n].copy();assert np.isfinite(us).all()
   i0=len(v);v.extend(a[:n]);norm.extend(ns);uv.extend(us);cursor=0
   for length in lens:
    strips+=1
    for i in range(2,length):
     ids=[cursor+i-2,cursor+i-1,cursor+i];ids=ids if i%2==0 else [ids[1],ids[0],ids[2]]
     a0,a1,a2=a[ids];cross=np.cross(a1-a0,a2-a0)
     if np.linalg.norm(cross)<1e-6:degenerate+=1;continue
     # normals determine outward winding even if the strip start parity varies.
     if np.dot(cross,ns[ids].sum(0))<0:ids[0],ids[1]=ids[1],ids[0]
     faces.append([i0+x for x in ids])
    cursor+=length
  v=np.asarray(v);q=s['node_offset']+20+len(s['name']);bbox=np.frombuffer(mb,'<f4',6,q).reshape(2,3);err=float(np.max(np.abs(bbox-np.stack([v.min(0),v.max(0)]))));assert err<0.001,(s['name'],err)
  result.append(dict(name=s['name'],vertices=v,normals=np.asarray(norm),uv=np.asarray(uv),faces=np.asarray(faces,dtype=np.int32),offset=off.get(s['name'],np.zeros(3)),strips=strips,degenerate=degenerate,bounds_error=err,packets=len(pp)))
 return result
# Visual candidates selected from the source PXT catalogue; hash-to-group mapping is not established.
MATERIALS={'wing_objShape':411,'r_eyeShape':429,'l_eyeShape':429,'r_eyelidShape':16,'l_eyelidShape':16}
def export(iso,out):
 out.mkdir(parents=True,exist_ok=True);r=records(iso);shapes=decode(r[1130][1],r[1529][1]);g=list(pxt_groups(r[772][1]));tex={}
 for i in [303,411,429,16]:
  _,pal,imgs=g[i];w,h,ix=imgs[0];tex[i]=pal[ix][:,:,:3];Image.fromarray(tex[i]).save(out/f'tex_{i}.png')
 # collision bounding shape omitted from visuals; eyelids are full overlays, hidden until animation decoded.
 visible=[s for s in shapes if s['name'] not in ('bbcShape','r_eyelidShape','l_eyelidShape')]
 with (out/'spyro_rest.obj').open('w') as f:
  f.write('# Source geometry; inferred rest translation and provisional PXT associations\nmtllib spyro_rest.mtl\n');base=1
  for s in shapes:
   f.write('o '+s['name']+'\n');v=s['vertices']+s['offset'];
   for p in v:f.write('v %.8g %.8g %.8g\n'%tuple(p))
   for p in s['uv']:f.write('vt %.8g %.8g\n'%(p[0],1-p[1]))
   for p in s['normals']:f.write('vn %.8g %.8g %.8g\n'%tuple(p))
   f.write('usemtl tex_'+str(MATERIALS.get(s['name'],303))+'\n')
   for a in s['faces']:
    f.write('f '+' '.join(f'{i+base}/{i+base}/{i+base}' for i in a)+'\n')
   base+=len(v)
 (out/'spyro_rest.mtl').write_text(''.join(f'newmtl tex_{i}\nKd 1 1 1\nmap_Kd tex_{i}.png\n' for i in tex))
 # Native and host share the same source arrays, omit non-rendering geometry and unanimated eyelids.
 v=[];uv=[];faces=[];mat=[];norm=[];part=[]
 for k,s in enumerate(visible):
  part.extend([k]*len(s["vertices"]));faces.extend(s['faces']+len(v));v.extend(s['vertices']+s['offset']);uv.extend(s['uv']);norm.extend(s['normals']);mat.extend([MATERIALS.get(s['name'],303)]*len(s['faces']))
 v=np.array(v);uv=np.array(uv);faces=np.array(faces);mat=np.array(mat);norm=np.array(norm)
 np.savez(out/'spyro_rest.npz',vertices=v,uv=uv,faces=faces,material=mat,normals=norm,part=np.array(part),part_names=np.array([s["name"] for s in visible]))
 rep={'shapes':[{'name':s['name'],'vertices':len(s['vertices']),'triangles':len(s['faces']),'strips':s['strips'],'packets':s['packets'],'degenerate_removed':s['degenerate'],'bounds_error':s['bounds_error'],'rest_offset':s['offset'].tolist()} for s in shapes],'visible_triangles':len(faces),'visible_vertices':len(v),'texture_groups':list(tex),'limitations':'Rest translations inferred from joint paths; no skinning or animations. Material-to-PXT association visual only. Bounding proxy and eyelids excluded from preview/native diagnostic. Full OBJ retains them.'}
 (out/'mesh_report.json').write_text(json.dumps(rep,indent=2));print('total',sum(x['vertices'] for x in rep['shapes']),sum(x['triangles'] for x in rep['shapes']),sum(x['strips'] for x in rep['shapes']), 'visible',len(faces));return rep
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('iso',type=Path);p.add_argument('out',type=Path);a=p.parse_args();export(a.iso,a.out)
