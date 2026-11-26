"""Recover the original Dojo ninja main mesh with source texture centroid colors."""
from pathlib import Path
import json,struct,hashlib
import numpy as np
from dojo25 import records
from recover import shape_metadata,vertex_packets,pxt_groups
from collect12 import geometry,lod
from spyro_mesh import STRIP,UV
from hash08 import fold
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets_m29'
def build(iso):
 r=records(iso);b=r[567][1];g=r[1061][1];s=shape_metadata(b)[-1];assert s['name']=='nr_mainGeoShape';v,f=geometry(b,g,s,len(g));uv=[]
 for p,a in vertex_packets(g,s['offset'],len(g)):
  q=g.find(STRIP,p);u=g.find(UV,q);n=g[q+9];uv.extend(np.frombuffer(g,'<f4',2*n,u+9).reshape(-1,2))
 uv=np.array(uv);assert len(uv)==len(v) and np.isfinite(uv).all();groups=list(pxt_groups(r[577][1]));table=r[296][1];name='38E2DE97.PXT';assert name.encode() in b
 i=next(i for i in range(len(groups)) if struct.unpack_from('<I',table,16+i*16)[0]==fold(name.lower().encode()));off,pal,imgs=groups[i];_,o,size,_=struct.unpack_from('<IIII',table,16+i*16);assert o-len(table)==off and size==groups[i+1][0]-off-16
 w,h,ix=imgs[0];rgb=pal[ix][:,:,:3];v=v*[1,-1,1];t=lod(v,f,23);src=v[f];cent=src.mean(1);colors=[]
 for a in t:
  fi=int(np.argmin(((cent-a.mean(0))**2).sum(1)));u,z=uv[f[fi]].mean(0)%1;px=rgb[int(z*h)%h,int(u*w)%w].astype(int);colors.append(int(px[0]|px[1]<<8|px[2]<<16))
 c=np.array(colors);assert len(t)<700 and np.max(abs(t))<512;np.savez_compressed(OUT/'ninja.npz',triangles=t,colors=c)
 (OUT/'ninjamesh29.h').write_text('static const CollectFace ninja29mesh[]={\n'+',\n'.join('{{'+','.join('{'+','.join(map(str,v))+'}' for v in a)+'},'+str(col)+'u}' for a,col in zip(t,c))+'};\n')
 rep=dict(metadata_record=567,geometry_record=1061,shape=s['name'],source_triangles=len(f),optimized_triangles=len(t),texture=name,texture_group=i,geometry_sha256=hashlib.sha256(g).hexdigest(),limitations='Main body only, centroid color approximation; separate eyeballs and eyelids not bound. Variant scales and AI reconstructed.')
 (OUT/'enemy_report.json').write_text(json.dumps(rep,indent=2));print(rep)
if __name__=='__main__':import sys;build(Path(sys.argv[1]))
