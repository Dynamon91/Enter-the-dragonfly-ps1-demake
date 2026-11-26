"""Resolve Dojo materials and placements against original CNK, then convert textures."""
import json,re,struct,collections,zlib,argparse
from pathlib import Path
import numpy as np
from PIL import Image
from dojo25 import records
from recover import pxt_groups,nodes,u32
from hash08 import fold
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets_m25'
def build(iso,out=OUT):
 r=records(iso);b=r[359][1];groups=list(pxt_groups(r[577][1]));table=r[296][1];assert u32(table,12)==len(groups);reg={}
 for i,(off,pal,imgs) in enumerate(groups):
  h,o,s,t=struct.unpack_from('<IIII',table,16+i*16);end=groups[i+1][0] if i+1<len(groups) else len(r[577][1]);assert o-len(table)==off and s==end-off-16,(i,o,off,s,end)
  reg[h]=dict(group=i,size=s,dimensions=list(imgs[0][:2]) if imgs else None,palette=len(pal))
 refs=collections.defaultdict(list)
 for p,n,q in nodes(b,0x47ba46ed):
  if q+100>len(b):continue
  h=u32(b,p+4);t=u32(b,q+96)
  for pp,nn,qq in nodes(b[q+96:q+800],0xdad78930):
   if u32(b,q+96+pp+4)!=t:continue
   qq+=q+96;m=re.search(rb'[0-9A-F]{8}\.PXT',b[qq:qq+150])
   if not m or qq+m.end()+10>len(b):continue
   w,hh,_,s=struct.unpack_from('<HHHI',b,qq+m.end());fn=m.group().decode();e=reg.get(fold(fn.lower().encode()))
   if e and e['size']==s and e['dimensions']==[w,hh] and e['palette'] in (16,256):refs[f'{h:08x}'].append(dict(filename=fn,group=e['group'],name=n,texture_node=nn))
   break
 meta=json.loads((out/'dojo_report.json').read_text())['meshes'];materials=[];lookup={};bind=[]
 for m in meta:
  h=m['material'];rs=refs[h];ids=sorted({x['group'] for x in rs});g=ids[0] if len(ids)==1 else None
  if h not in lookup:lookup[h]=len(materials);materials.append(dict(id=len(materials),material=h,texture_group=g,candidates=ids,refs=rs,status='resolved' if g is not None else 'ambiguous' if ids else 'missing'))
  bind.append(lookup[h])
 z=np.load(out/'dojo.npz');tids=np.array(bind)[z['part']];data=bytearray();idx=[];colors={}
 for i in sorted({m['texture_group'] for m in materials if m['texture_group'] is not None}):
  _,pal,imgs=groups[i];w,h,ix=imgs[0];p=pal.astype(np.uint16);c=np.maximum((p[:,0]>>3)|((p[:,1]>>3)<<5)|((p[:,2]>>3)<<10),1).astype('<u2');c=np.pad(c,(0,256-len(c)));ix64=np.asarray(Image.fromarray(ix).resize((64,64),Image.Resampling.NEAREST));payload=c.tobytes()+ix64.tobytes();crc=zlib.crc32(payload);block=struct.pack('<4sHHIIII',b'ETDT',1,i,w,h,len(payload),crc)+payload;idx.append((i,len(data)//2048,crc));data.extend(block+bytes(6144-len(block)));colors[i]=np.rint(pal[ix][:,:,:3].mean((0,1))).astype(int).tolist()
 (out/'DOJOTEX.DAT').write_bytes(data);(out/'DOJOTEX.IDX').write_bytes(struct.pack('<4sHHI',b'ETTI',1,12,len(idx))+b''.join(struct.pack('<III',*x) for x in idx))
 for m in materials:m['rgb']=colors.get(m['texture_group'],[185,110,155])
 def placements(b):
  rows=[]
  for p,n,q in nodes(b,0x2a29015d):
   if b[q+68:q+77]!=b'Character' or u32(b,q+77)!=2:continue
   ln=u32(b,q+81);edf=b[q+85:q+85+ln].decode('ascii');xyz=struct.unpack_from('<3f',b,q)
   if not np.isfinite(xyz).all() or xyz!=struct.unpack_from('<3f',b,q+24):continue
   match=re.fullmatch(r'gem(\d+)\.edf',edf,re.I);rows.append(dict(name=n,edf=edf,source_xyz=list(xyz),record_offset=p,kind=1 if match else 4,value=int(match[1]) if match else 0))
  return rows
 rows=placements(b);other={(x['name'],x['edf'],tuple(x['source_xyz'])) for x in placements(r[569][1])};rows=[x for x in rows if (x['name'],x['edf'],tuple(x['source_xyz'])) in other]
 report=dict(texture_groups=len(groups),converted_textures=len(idx),materials=len(materials),status=dict(collections.Counter(m['status'] for m in materials)),resolved_faces=int(sum(materials[i]['status']=='resolved' for i in tids)),objects=len(rows),gems=sum(x['kind']==1 for x in rows),direct_gem_value=sum(x['value'] for x in rows),limitations='Exact unique hash/size/dimensions only. Opaque base palette conversion; alpha/multilayer not decoded. Placements cross-checked against second metadata record.')
 (out/'material_report.json').write_text(json.dumps(report,indent=2));(out/'bindings.json').write_text(json.dumps(dict(materials=materials,bindings=bind,objects=rows),indent=2));print(report)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('iso',type=Path);build(p.parse_args().iso)
