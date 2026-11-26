"""Decode source sheep and normal butterfly geometry; bake original base texture colors per reduced face."""
import argparse,json,struct,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
from recover import records,shape_metadata,vertex_packets,pxt_groups,nodes
from collect12 import geometry,lod
from spyro_mesh import STRIP,UV,joints
from hash08 import fold
ROOT=Path(__file__).resolve().parents[1]
def extract(iso,out):
 out.mkdir(parents=True,exist_ok=True);r=records(iso);reg=json.loads((ROOT/'build_m14/play/texture_registry.json').read_text());H={int(e['hash'],16):e for e in reg['entries']};groups=list(pxt_groups(r[772][1]));bindings={};meta=[]
 def texture(name,mb):
  assert name.encode() in mb; e=H[fold(name.lower().encode())];_,pal,imgs=groups[e['group']];w,h,ix=imgs[0];assert e['dimensions']==[w,h] and len(pal)==256;rgb=pal[ix][:,:,:3];Image.fromarray(rgb).save(out/(name+'.png'));bindings[name]=dict(group=e['group'],hash=e['hash'],size=e['size'],dimensions=[w,h]);return rgb
 def decode(mi,gi,kind):
  b=r[mi][1];g=r[gi][1];ss=shape_metadata(b);joints0=joints(b);parts=[]
  for k,s in enumerate(ss):
   name=s['name'];end=ss[k+1]['offset'] if k+1<len(ss) else len(g);v,f=geometry(b,g,s,end);row=dict(name=name,source_triangles=len(f),source_vertices=len(v),included=False);meta.append(row)
   if name.startswith(('DAMAGE','csph')) or 'eyelid' in name:continue
   if kind=='sheep':
    tex='DAAC78E8.PXT' if name=='bodyShape' else '8BDC29A1.PXT';offset=np.zeros(3) if name=='bodyShape' else sum((joints0[x] for x in ['sheep_root','sheep_chest','sheep_head']),np.zeros(3));step=27 if name=='bodyShape' else 10
   else:tex='DDE7E699.PXT' if name=='bodyShape' else '08E0B5F3.PXT';offset=np.zeros(3);step=4 if name=='bodyShape' else 1
   uv=[]
   for p,a in vertex_packets(g,s['offset'],end):
    q=g.find(STRIP,p,end);u=g.find(UV,q,end);n=g[q+9];assert u>=0 and u+9+8*n<=end;uv.extend(np.frombuffer(g,'<f4',2*n,u+9).reshape(-1,2))
   uv=np.array(uv);assert len(uv)==len(v) and np.isfinite(uv).all();v=(v+offset)*[1,-1,1];t=lod(v,f,step);src=v[f];rgb=texture(tex,b);cent=src.mean(1);col=[]
   # Assign each simplified face the nearest original face's UV centroid color.
   for a in t:
    fi=int(np.argmin(((cent-a.mean(0))**2).sum(1)));u,w=uv[f[fi]].mean(0)%1;px=rgb[min(int(w*rgb.shape[0]),rgb.shape[0]-1),min(int(u*rgb.shape[1]),rgb.shape[1]-1)].astype(float);col.append(np.clip(np.rint(px),0,255).astype(int))
   col=np.array(col);color=col[:,0]|col[:,1]<<8|col[:,2]<<16;row.update(included=True,lod_triangles=len(t),texture=tex,offset=offset.tolist());parts.append((t,color))
  return np.concatenate([x[0] for x in parts]),np.concatenate([x[1] for x in parts])
 sheep,sc=decode(1318,1531,'sheep');butter,bc=decode(280,270,'butterfly');assert np.max(abs(sheep))<512 and np.max(abs(butter))<128
 def cmesh(name,t,c):return 'static const CollectFace '+name+'[]={\n'+',\n'.join('{{'+','.join('{'+','.join(map(str,v))+'}' for v in a)+'},'+str(col)+'u}' for a,col in zip(t,c))+'};\n'
 h=cmesh('sheepmesh',sheep,sc)+cmesh('buttermesh',butter,bc)+f'#define FODDER_MESH_MAX {max(len(sheep),len(butter))}\n';(out/'fodderdata15.h').write_text(h);np.savez_compressed(out/'fodder_meshes.npz',sheep=sheep,sheep_colors=sc,butterfly=butter,butterfly_colors=bc)
 p=json.loads((ROOT/'assets_m12/placements.json').read_text())['other_characters'];p=[x for x in p if x['edf'].lower()=='sheep.edf'];assert len(p)==12 and all(x['floor'] is None for x in p);report=dict(sheep_metadata=1318,sheep_geometry=1531,butterfly_metadata=280,butterfly_geometry=270,sheep_placements=p,source_placement_count=len(p),source_placements_active=0,sheep_triangles=len(sheep),butterfly_triangles=len(butter),shapes=meta,texture_bindings=bindings,limitations='Texture centroid colors baked; UV orientation, facial offsets, and PS2 material blending provisional. Collision proxy meshes and closed eyelids omitted. Original positions outside current sector; separate optional diagnostic spawn.');(out/'fodder_report.json').write_text(json.dumps(report,indent=2));print('sheep',len(sheep),'butterfly',len(butter),'source positions',len(p))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('iso',type=Path);p.add_argument('out',type=Path);a=p.parse_args();extract(a.iso,a.out)
