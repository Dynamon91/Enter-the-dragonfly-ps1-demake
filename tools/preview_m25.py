"""Orthographic source-geometry atlas, not an emulated frame."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'assets_m25';OUT=ROOT/'build_m25/view'
def build():
 z=np.load(A/'dojo.npz');m=json.loads((A/'bindings.json').read_text());r=json.loads((A/'dojo_report.json').read_text());t=z['vertices'][z['faces']].astype(float)*[1,-1,1];ids=np.array(m['bindings'])[z['part']];rgb=np.array([x['rgb'] for x in m['materials']])[ids];c=np.load(A/'collision.npz');ct=c['vertices'][c['faces']].astype(float)*[1,-1,1]
 im=Image.new('RGB',(1440,850),(22,27,35));d=ImageDraw.Draw(im);font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
 d.text((28,17),'DRAGONFLY DOJO',font=font(32),fill=(246,247,249));d.text((28,58),'v0.25  /  Original PS2 geometry converted to PS1 sector data',font=font(19),fill=(180,194,209));d.line((28,94,1412,94),fill=(70,83,95),width=1)
 # Isometric view: transform world coordinates and sort back to front by view depth.
 a=np.deg2rad(27);e=np.deg2rad(58);right=np.array([np.cos(a),0,-np.sin(a)]);forward=np.array([np.sin(a),0,np.cos(a)]);up=np.array([0,-1,0])*np.cos(e)-forward*np.sin(e);depth=forward*np.cos(e)+np.array([0,-1,0])*np.sin(e)
 def iso(p):return np.stack([p@right,p@up],-1)
 p=iso(t);lo=p.min((0,1));hi=p.max((0,1));scale=min(660/(hi[0]-lo[0]),630/(hi[1]-lo[1]));p=(p-(lo+hi)/2)*[scale,-scale]+[360,453];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1,keepdims=True),1e-8);sh=.60+.40*abs(n@np.array([.28,-.91,.30]));color=np.clip(rgb*sh[:,None],0,255).astype(int)
 for j in np.argsort(-(t@depth).mean(1)):d.polygon([tuple(q) for q in p[j]],fill=tuple(color[j]))
 d.text((28,108),'01  Recovered terrain / material-average shading',font=font(17),fill=(220,229,237));
 # Top-down collision and object positions use common world coordinates.
 xz=ct[:,:,[0,2]];lo=np.minimum(t[:,:,[0,2]].min((0,1)),xz.min((0,1)));hi=np.maximum(t[:,:,[0,2]].max((0,1)),xz.max((0,1)));scale=min(630/(hi[0]-lo[0]),630/(hi[1]-lo[1]));p=(xz-(lo+hi)/2)*[scale,-scale]+[1080,453]
 for j in np.argsort(-ct[:,:,1].mean(1)):d.polygon([tuple(q) for q in p[j]],fill=(68,121,105),outline=(42,79,69))
 for o in m['objects']:
  x,y=(np.array(o['source_xyz'])[[0,2]]-(lo+hi)/2)*[scale,-scale]+[1080,453];d.ellipse((x-2.1,y-2.1,x+2.1,y+2.1),fill=(244,203,82) if o['kind']==1 else (232,120,157))
 d.line((720,108,720,750),fill=(70,83,95));d.text((744,108),'02  Collision candidates / original object placements',font=font(17),fill=(220,229,237));d.text((28,777),f'{len(t):,} triangles  •  {r["matched"]} unique meshes',font=font(19),fill=(227,235,242));d.text((744,777),f'{len(ct):,} collision triangles  •  {len(m["objects"])} placements',font=font(19),fill=(227,235,242));d.text((28,813),'Host diagnostic • original world coordinates • not emulator output',font=font(14),fill=(172,184,198));d.ellipse((744,815,754,825),fill=(244,203,82));d.text((760,811),'Gems',font=font(14),fill='white');d.ellipse((828,815,838,825),fill=(232,120,157));d.text((844,811),'Other characters and objects',font=font(14),fill='white');im.save(OUT/'dojo_preview.png')
if __name__=='__main__':build()
