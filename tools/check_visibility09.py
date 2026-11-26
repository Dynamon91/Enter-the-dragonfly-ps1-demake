"""Measure native culling on source scene; compare against exact per-vertex clip masks."""
import ctypes as C, math, json, subprocess
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]

def check(out,full=True):
 z=np.load(out/'farm06.npz');b=np.load(out/'visibility.npz');v=z['vertices'];f=z['faces'];rows=b['clusters'];ids=b['face_ids'];so=out/'visibility_host.so';subprocess.run(['clang','-O2','-shared','-fPIC',str(ROOT/'tests/visibility09_host.c'),'-o',str(so)],check=True);lib=C.CDLL(str(so.resolve()));visible=lib.visible09;visible.argtypes=[C.POINTER(C.c_int16)]+[C.c_int]*5;visible.restype=C.c_int;mask=lib.mask09;mask.argtypes=[C.c_int]*8;mask.restype=C.c_int
 bounds=np.ascontiguousarray(rows,dtype=np.int16);positions=[z['spawn']];floor=z['floor'];g=np.argwhere(floor!=32767);positions += [np.array([x*128-4096,int(floor[y,x]),y*128-4096]) for y,x in g[np.linspace(0,len(g)-1,11,dtype=int)]] if full else []
 result=[]
 for p in positions:
  for yaw in range(0,64,4 if full else 16):
   sn=round(math.sin(yaw*math.pi/32)*4096);cs=round(math.cos(yaw*math.pi/32)*4096);cx,cy,cz=(p-np.array([sn*560>>12,300,cs*560>>12])).tolist();cam=[cx,cy,cz,sn,cs];keep=np.zeros(len(f),dtype=bool)
   for row in bounds:
    if visible(row.ctypes.data_as(C.POINTER(C.c_int16)),*cam):keep[ids[row[6]:row[6]+row[7]]]=True
   masks=np.array([mask(*map(int,x),*cam) for x in v]);trivial=np.bitwise_and.reduce(masks[f],axis=1)!=0
   assert np.all(trivial[~keep]),(p,yaw,'false reject')
   result.append(dict(position=p.tolist(),yaw=yaw,faces=int(keep.sum()),vertices=int(len(np.unique(f[keep]))),rejected_faces=int((~keep).sum())))
 return dict(views=len(result),baseline_faces=len(f),baseline_vertices=len(v),avg_candidate_faces=round(float(np.mean([x['faces'] for x in result])),1),avg_transformed_vertices=round(float(np.mean([x['vertices'] for x in result])),1),minimum_faces=min(x['faces'] for x in result),maximum_faces=max(x['faces'] for x in result),false_rejects=0,results=result)
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();r=check(a.out);(a.out/'visibility_report.json').write_text(json.dumps(r,indent=2));print({k:v for k,v in r.items() if k!='results'})
