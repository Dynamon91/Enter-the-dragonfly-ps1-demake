"""Plan source-derived cow routes over packed collision; not the original AI solver."""
import argparse,heapq,json,math,struct
from pathlib import Path
import numpy as np

def build(native,barn,out):
    ix=(native/'CCCSECT.IDX').read_bytes();data=(native/'CCCSECT.DAT').read_bytes();ts=[]
    for i in range((len(ix)-16)//60):
        e=struct.unpack_from('<IIII3i6i3H2x',ix,16+60*i);o=e[1]*2048+64+e[13]*36
        for j in range(e[14]):ts.append(np.array(struct.unpack_from('<9h',data,o+j*24)).reshape(3,3)+e[4:7])
    t=np.array(ts);a=t[:,0];b=t[:,1]-a;c=t[:,2]-a;d=b[:,0]*c[:,2]-b[:,2]*c[:,0];ok=(d!=0)&(abs(b[:,1]*c[:,2]-b[:,2]*c[:,1])<=2*abs(d))&(abs(b[:,0]*c[:,1]-b[:,1]*c[:,0])<=2*abs(d));a,b,c,d=[x[ok] for x in (a,b,c,d)]
    from functools import lru_cache
    @lru_cache(None)
    def floors(x,z):
        u=(x-a[:,0])*c[:,2]-(z-a[:,2])*c[:,0];v=b[:,0]*(z-a[:,2])-b[:,2]*(x-a[:,0]);sign=np.sign(d);u*=sign;v*=sign;dd=abs(d);hit=(u>=0)&(v>=0)&(u+v<=dd);return tuple(np.unique(a[hit,1]+np.trunc((u[hit]*b[hit,1]+v[hit]*c[hit,1])/dd[hit]).astype(int)))
    def walk(x,y,z,xx,zz):
        n=max(1,(max(abs(xx-x),abs(zz-z))+31)//32)
        for i in range(1,n+1):
            q=floors(x+int((xx-x)*i/n),z+int((zz-z)*i/n));q=[int(k) for k in q if abs(k-y)<=70]
            if not q:return None
            y=min(q,key=lambda k:abs(k-y))
        return y
    goal=(14394,-192,-5061);routes=[];step=128
    def h(x,z):return max(0,math.hypot(x-goal[0],z-goal[2])-600)
    for cow in json.loads(barn.read_text())['herding_cows']:
        start=tuple(cow['xyz']);queue=[(h(start[0],start[2]),0,start)];cost={start:0};prev={};target=None
        while queue:
            _,g,node=heapq.heappop(queue)
            if g!=cost[node]:continue
            x,y,z=node
            if h(x,z)==0 and abs(y-goal[1])<=100 and walk(x,y,z,goal[0],goal[2]) is not None:target=node;break
            for dx,dz in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
                xx,zz=x+step*dx,z+step*dz
                if not 8000<=xx<=19000 or not -11000<=zz<=1500:continue
                yy=walk(x,y,z,xx,zz)
                if yy is None:continue
                v=(xx,yy,zz);ng=g+math.hypot(step*dx,step*dz)+abs(yy-y)*.5
                if ng>=cost.get(v,float('inf')):continue
                cost[v]=ng;prev[v]=node;heapq.heappush(queue,(ng+h(xx,zz),ng,v))
        if target is None:raise ValueError('no verified floor route '+str(start))
        route=[target]
        while route[-1]!=start:route.append(prev[route[-1]])
        route.reverse();routes.append(route);print(cow['flag'],len(route),route[-1],flush=True)
    out.mkdir(exist_ok=False,parents=True);(out/'routes62.json').write_text(json.dumps(dict(dean=goal,routes=routes,step=step,notes='Reconstructed floor-following waypoint routes, not original pathfinding; no dynamic obstacle test.'),indent=2)+'\n');s='static const short herdpoints62[][3]={'+','.join('{%d,%d,%d}'%tuple(p) for r in routes for p in r)+'};\n';s+='static const unsigned short herdoff62[6]={'+','.join(map(str,np.cumsum([0]+list(map(len,routes))).tolist()))+'};\n';(out/'herddata62.h').write_text(s)
if __name__=='__main__':
    p=argparse.ArgumentParser();[p.add_argument(k,type=Path) for k in ('native','barn','out')];a=p.parse_args();build(a.native,a.barn,a.out)
