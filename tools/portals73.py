"""Recover hub travel node coordinates, EDF gates and dialogue thresholds."""
import argparse,hashlib,json,re,struct,math
from pathlib import Path
from cnk import entries
from recover import nodes
from hash08 import fold
CODES=['DD','CCC','LI','C9','MM','HM','TD','JJ','BOSS']
SCRIPTS=[1273,1406,669,195,789,1368,393,218,None]
def build(path,out):
 b=path.read_bytes();r={i:b[o:o+s] for i,h,o,s,t in entries(b)};tab=r[1500];d={h:(o-len(tab),s) for h,o,s,f in struct.iter_unpack('<4I',tab[16:])};assert max(o+n for o,n in d.values())==len(r[968]);
 def pose(name):
  arr=[]
  for rec in [502,1402]:
   v=[(p,struct.unpack_from('<6f',r[rec],q)) for p,n,q in nodes(r[rec],0x2a29015d) if n.upper()==name];assert len(v)==1;arr.append(v[0])
  assert arr[0][1]==arr[1][1];p=arr[0][1];return {'source_id':arr[0][0],'xyz':[round(p[0]),round(-p[1]),round(p[2])],'yaw':round(p[4]*32/math.pi)%64}
 rows=[]
 for i,code in enumerate(CODES):
  o,n=d[fold((code.lower()+'_from_hub.edf').encode())];e=r[968][o:o+n];flag=int(re.search(rb'WorldFlag:\s*0\s+(\d+)',e)[1]);transition,=re.findall(rb'TransitionInfo:\s*"([^"]+)"',e);dest,point=re.search(rb'ExitInfo:\s*"([^"]+)"\s*"([^"]+)"',e).groups();sc=SCRIPTS[i];threshold=None if sc is None else int(re.search(rb'DragonFlies\s+(\d+)',r[sc])[1]);assert sc is None or re.search(rb'WorldFlagOn\s+0\s+'+str(flag).encode()+rb'\b',r[sc]);rows.append(dict(world=i+1,code=code,entry=pose('__CNODEPORTAL_T_'+code),return_point=None if code=='BOSS' else pose('__CNODEPORTAL_F_'+code),flag=flag,threshold=threshold,script=sc,transition=transition.decode(),destination=dest.decode(),point=point.decode(),edf_sha256=hashlib.sha256(e).hexdigest()))
 spawn=pose('__CNODESPYRO');out.mkdir(parents=True,exist_ok=True);(out/'portals73.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(b).hexdigest(),spawn=spawn,portals=rows),indent=2)+'\n');print([(x['code'],x['threshold'],x['entry']['xyz']) for x in rows],spawn)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('cnk',type=Path);p.add_argument('out',type=Path);a=p.parse_args();build(a.cnk,a.out)
