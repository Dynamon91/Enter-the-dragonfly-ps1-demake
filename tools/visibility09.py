"""Spatially group source faces without altering their geometry or draw order."""
from pathlib import Path
import numpy as np

def clusters(v,f,cap=48):
 t=v[f];cent=t.sum(1); result=[]
 def split(ids):
  if len(ids)<=cap:
   p=t[ids];result.append((p.min((0,1)),p.max((0,1)),ids));return
  axis=np.ptp(cent[ids],axis=0).argmax();ids=ids[np.argsort(cent[ids,axis],kind='stable')];m=len(ids)//2;split(ids[:m]);split(ids[m:])
 split(np.arange(len(f)));return result

def export(out):
 z=np.load(out/'farm06.npz');c=clusters(z['vertices'],z['faces']);flat=[];rows=[]
 for lo,hi,ids in c:
  rows.append([*lo,*hi,len(flat),len(ids)]);flat.extend(ids)
 (out/'visibility.h').write_text(f'#define CLUSTER_COUNT {len(c)}\nstatic const s16 clusters[CLUSTER_COUNT][8]={{\n'+',\n'.join('{'+','.join(map(str,r))+'}' for r in rows)+'};\nstatic const u16 cluster_faces[WF]={'+','.join(map(str,flat))+'};\n')
 np.savez_compressed(out/'visibility.npz',clusters=np.array(rows),face_ids=np.array(flat));return len(c)
