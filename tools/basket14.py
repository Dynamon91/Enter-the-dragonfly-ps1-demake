"""Source basket geometry, placements and original break sound. No guessed reward script."""
import argparse,json,struct,hashlib
from pathlib import Path
import numpy as np
from recover import records,shape_metadata
from collect12 import geometry,lod,colorize
from hash08 import fold
ROOT=Path(__file__).resolve().parents[1]
def extract(iso,out):
 out.mkdir(parents=True,exist_ok=True);r=records(iso);b=r[932][1];g=r[1237][1];s=next(x for x in shape_metadata(b) if x['name']=='basketShape');v,f=geometry(b,g,s,len(g));t=lod(v*[1,-1,1],f,24);c=colorize(t,np.array([173,110,54]));p=json.loads((ROOT/'assets_m12/placements.json').read_text());allp=[x for x in p['other_characters'] if x['edf']=='basket1.edf'];active=[x for x in allp if x['floor'] is not None and x['floor']!=32767 and abs(x['floor']-x['sector_xyz'][1])<=110];assert len(allp)==27 and len(active)==2
 h='static const CollectFace basketmesh[]={\n'+',\n'.join('{{'+','.join('{'+','.join(map(str,v))+'}' for v in a)+'},'+str(col)+'u}' for a,col in zip(t,c))+'};\n';h+=f'#define BASKET_COUNT {len(active)}\n#define BASKET_MESH_MAX (BASKET_COUNT*{len(t)})\nstatic const s16 basketpos[BASKET_COUNT][4]={{'+','.join('{'+','.join(map(str,x['sector_xyz']+[1]))+'}' for x in active)+'};\n';(out/'basketdata14.h').write_text(h)
 assert b'# break basket' in r[1079][1];i=769;k,a=r[i];assert k==fold(b'spy01.vag');size,rate=struct.unpack_from('>II',a,12);d=a[48:];assert size==len(d) and rate==22050 and size%16==0 and d[-31]==1 and d[-15]==7 and all(x==0 for x in d[1:-31:16]);(out/'spy01.vag').write_bytes(a)
 rep=dict(source_metadata_record=932,source_geometry_record=1237,source_triangles=len(f),lod_triangles=len(t),source_placements=allp,active=active,sound_record=i,sound_bytes=size,sound_rate=rate,sound_sha256=hashlib.sha256(d).hexdigest(),limitations='Original placement and mesh; flat facet colors provisional, one red gem per basket is a test reward, exact original treasure script unknown.')
 (out/'basket_report.json').write_text(json.dumps(rep,indent=2));print('basket',len(f),len(t),len(allp),len(active),size)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('iso',type=Path);p.add_argument('out',type=Path);a=p.parse_args();extract(a.iso,a.out)
