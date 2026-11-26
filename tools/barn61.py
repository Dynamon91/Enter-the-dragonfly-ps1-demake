"""Recover original barn props, escape spline control points, and EDF flag semantics."""
import argparse,hashlib,json,re,struct,math
from pathlib import Path
from cnk import entries
from recover import nodes
from hash08 import fold
import actors59

def build(cnk,bindings,old,out):
    b=cnk.read_bytes();r={i:b[o:o+s] for i,h,o,s,t in entries(b)}
    table=r[1125];assert len(table)==16+16*104
    def edf(name):
        h=fold(name.lower().encode());a=[struct.unpack_from('<4I',table,16+i*16) for i in range(104)];matches=[(o,n) for k,o,n,f in a if k==h];assert len(matches)==1
        o,n=matches[0];o-=len(table);assert 0<=o<o+n<=len(r[719]);return r[719][o:o+n]
    assert b'Flag_Index\t2 48' in edf('ccc_door_explosive.edf') or re.search(rb'Flag_Index\s+2 48',edf('ccc_door_explosive.edf'))
    assert b'CCC_DOOR_EXPLOSIVE.scr' in edf('ccc_door_trigger.edf') and re.search(rb'WorldFlagOn\s+2 0',r[159]) and re.search(rb'Flag_Index\s+2 1',edf('barn_door_left.edf'))
    def pos(record,name):
        a=[(p,struct.unpack_from('<6f',record,q)) for p,n,q in nodes(record,0x2a29015d) if n.lower()==name.lower()];assert len(a)==1;return a[0]
    paths=[];herd=[];flags=[];barn=[]
    for i in range(1,6):
        name=f'__CNODEccc_BARN_COW_{i}';sid,p=pos(r[379],name);_,p2=pos(r[1012],name);assert p==p2
        name=f'COW{i}_SPLINEShape'.encode();raw=[]
        for rec in (379,1012):
            s=r[rec];q=s.index(name)+len(name);assert s[q+60:q+64]==struct.pack('<I',8);assert struct.unpack_from('<I',s,q+96)[0]==6 and struct.unpack_from('<I',s,q+172)[0]==3;raw.append(s[q+64:q+176])
        assert raw[0]==raw[1];pts=[struct.unpack_from('<3f',raw[0],36+12*j) for j in range(6)];assert all(math.isfinite(v) for a in pts for v in a)
        script=edf(f'ccc_barn_cow_{i}.edf');assert name in script and b'Run_On_Spline_From' in script and re.search(rb'WorldFlag_On\s+2 1',script)
        # Source control points are 67.7 units above the barn's placed cow floor.
        points=[[round(p[0]),round(-p[1]),round(p[2])]]+[[round(x),round(-y+68),round(z)] for x,y,z in pts];paths.append(points);barn.append(dict(id=sid,source_xyz=list(p[:3]),spline=name.decode(),control_points=pts,edf_sha256=hashlib.sha256(script).hexdigest()))
        s=edf(f'ccc_herding_cow_{i}.edf');flag=int(re.search(rb'CountableEnemy2\s+2\s+(\d+)',s)[1]);assert flag==7+i and re.search(rb'Target_Range\s+0\s+850',s) and b'Find_And_Go_EDF "FARMER_DEAN"' in s;flags.append(flag)
        sid,p=pos(r[379],f'__CNODECCC_HERDING_COW_{i}');assert p==pos(r[1012],f'__CNODECCC_HERDING_COW_{i}')[1];herd.append(dict(id=sid,xyz=[round(p[0]),round(-p[1]),round(p[2])],flag=flag,edf_sha256=hashlib.sha256(s).hexdigest()))
    assert re.search(rb'Flag_Index\s+2 7',edf('ccc_barn_cow_3.edf'))
    # Reuse verified model extractor for three actual original props.
    actors59.MODELS=[('leftdoor',392,499,['frame_lShape','plate_lShape','nob_lShape'],4,r'BARN_DOOR_LEFT\.edf'),('rightdoor',649,445,['frame_rShape','plate_rShape','nob_rShape'],4,r'BARN_DOOR_RIGHT\.edf'),('fuse',662,835,['fuseShape'],3,r'CCC_DOOR_EXPLOSIVE\.edf')]
    report=actors59.build(cnk,bindings,out)
    h=(out/'actorsdata59.h').read_text();h=h.replace('ActorFace59','ActorFace61').replace('ActorModel59','ActorModel61').replace('ActorPlacement59','ActorPlacement61').replace('models59','barnmodels61').replace('actors59','barnprops61')
    (out/'barndata61.h').write_text(h+'\nstatic const short escape61[5][7][3]={'+','.join('{'+','.join('{'+','.join(map(str,p))+'}' for p in route)+'}' for route in paths)+'};\n')
    assert len(report['placements'])==3 and [a['model'] for a in report['placements']]==[0,1,2]
    # Actual fuse extends from the source explosive placement toward the exterior.
    # Local fuse tip min Z at yaw 48; hit proxy at its exposed end.
    data=dict(source_sha256=hashlib.sha256(b).hexdigest(),barn_cows=barn,herding_cows=herd,escape_paths=paths,props=report['placements'],models=report['models'],source_flags={'fuse':48,'rescue':0,'doors_open':1,'escape_complete':7,'herded':flags,'dean_reward':204,'bill_reward':206},notes='Original source spline control points used as linear waypoints, Y shifted 68 units to match source cow root. Door opening rotation, timer and flame hit radius approximated. Herding navigation is separate.')
    (out/'barn61.json').write_text(json.dumps(data,indent=2)+'\n');print('5 barn paths, 5 herding definitions, 3 props; exact source flags verified')
if __name__=='__main__':
    p=argparse.ArgumentParser();[p.add_argument(k,type=Path) for k in ('cnk','bindings','old','out')];a=p.parse_args();build(a.cnk,a.bindings,a.old,a.out)
