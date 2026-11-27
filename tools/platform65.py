"""Recover original platform waypoints and combat vulnerability evidence."""
import argparse,hashlib,json,re,struct
from pathlib import Path
from cnk import entries
from hash08 import fold
NAMES=['CCC_LEVEL_UFO1_SPLINEShape2','CCC_LEVEL_UFO1_SPLINEShape1','CCC_LEVEL_UFO2_SPLINEShape1','CCC_LEVEL_UFO2_SPLINEShape2','CCC_LEVEL_UFO2_SPLINEShape3','CCC_LEVEL_UFO2_SPLINEShape4']
def build(cnk,bindings,out):
 b=cnk.read_bytes();r={i:b[o:o+s] for i,h,o,s,t in entries(b)};tab=r[1125];d={h:(o-len(tab),s) for h,o,s,f in struct.iter_unpack('<4I',tab[16:])}
 def edf(n):
  o,s=d[fold(n.lower().encode())];return r[719][o:o+s].decode('ascii')
 paths=[]
 for name in NAMES:
  copies=[]
  for rec in (379,1012):
   q=r[rec].index(name.encode())+len(name);k=struct.unpack_from('<I',r[rec],q+60)[0];n=struct.unpack_from('<I',r[rec],q+64+4*k)[0];assert 3<=n<=12;copies.append(r[rec][q+68+4*k:q+68+4*k+12*n])
  assert copies[0]==copies[1];paths.append([[round(x),round(-y),round(z)] for x,y,z in struct.iter_unpack('<3f',copies[0])])
 objects=json.loads(bindings.read_text())['objects'];starts=[]
 for i in (1,2):
  name=f'ccc_level_ufo_platform_{i}.edf';s=edf(name);assert 'Type: Walkable' in s and all(n in s for n in NAMES[(0 if i==1 else 2):(2 if i==1 else 6)])
  a=next(o for o in objects if o['edf'].lower()==name);x,y,z=a['source_xyz'];starts.append([round(x),round(-y),round(z)])
 evidence=[]
 for name in ('big_fat_ray_gun_riptoc.edf','space_cow.edf','b_urn.edf','chicken.edf'):
  s=edf(name);v=re.findall(r'Vulnerabilities_Control\s*\{([^}]*)\}',s);sets=[sorted(set(re.findall(r'\b(?:Charge|Flame|Lightning|Super_Flame|Super_Smash)\b',x))) for x in v];evidence.append(dict(edf=name,sha256=hashlib.sha256(s.encode()).hexdigest(),vulnerabilities=sets,treasure=sorted(set(re.findall(r'EDF\s+"(gem\d+\.edf)"',s,re.I)))))
 out.mkdir(exist_ok=False,parents=True);flat=[p for path in paths for p in path];off=[0]
 for p in paths:off.append(off[-1]+len(p))
 arr=lambda p:','.join(map(str,p));(out/'platformdata65.h').write_text('static const short platformpath65[][3]={'+','.join('{'+arr(p)+'}' for p in flat)+'};\nstatic const unsigned char platformoff65[]={'+arr(off)+'};\nstatic const short platformstart65[2][3]={'+','.join('{'+arr(p)+'}' for p in starts)+'};\n');(out/'platform65.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(b).hexdigest(),names=NAMES,paths=paths,starts=starts,combat=evidence),indent=2)+'\n');print('six corroborated splines,',len(flat),'control points',starts,[(e['edf'],e['treasure']) for e in evidence])
if __name__=='__main__':
 p=argparse.ArgumentParser();[p.add_argument(n,type=Path) for n in ('cnk','bindings','out')];a=p.parse_args();build(a.cnk,a.bindings,a.out)
