"""Extract Dojo quest evidence and fixed-point spline control points from user-owned disc."""
from pathlib import Path
import json,re,struct,hashlib
from dojo25 import records
from hash08 import fold
R=Path(__file__).resolve().parents[1]; O=R/'assets_m34'
DEFS=[('Tootie','DD_TOOTIE.edf','DD_TOOTIE_DFLY.edf','DD_TOOTIE_DFLY_TRIGGER.edf','TOOTIE_DFLYSPLINEShape','Tootiedfly.scr',20,21,22,23),('Huey','DD_HUEY.edf','DD_HUEY_KITE.edf','DD_HUEY_KITE_TRIGGER.edf','KITE_SPLINEShape','Hueykite.scr',26,27,28,29),('Dooie','DD_DOOIE.edf','DD_DOOIE_RIPTOC_DECODER.edf','DD_DOOIE_RIPTOC_DECODER_TRIGGER.edf','BOOK_SPLINEShape','Dooiedecoder.scr',32,33,34,35)]
def build(iso):
 r=records(iso);b=r[569][1];edf=r[734][1];objects=json.loads((R/'assets_m25/sector_manifest.json').read_text())['objects'];out=[]
 for name,npc,prop,trigger,spline,motion,start,moving,arrived,recovered in DEFS:
  def rec(n):
   h=fold(n.lower().encode()); matches=[(i,v) for i,(k,v) in r.items() if k==h];assert len(matches)==1;return matches[0]
  i,c=rec(name+'.scr');j,d=rec(motion);assert b'Give Dragonflies\t1' in c and b'1 204' in c and f'1 {recovered}'.encode() in c
  assert f'1 {start}'.encode() in d and f'1 {moving}'.encode() in d
  assert re.search(rb'Flag_Index\s+1\s+'+str(start).encode()+rb'\b',edf)
  assert spline.encode() in edf
  duration=float(re.search(rb'Pause\s+([0-9.]+)',d).group(1));p=b.index(spline.encode())+len(spline);nk=struct.unpack_from('<I',b,p+60)[0]; # knot count field after node header
  # Locate count by validating first control point against exact source object placement.
  obs=[next(o for o in objects if o['edf'].lower()==n.lower()) for n in (npc,prop,trigger)]
  matches=[]
  for off in range(64,121,4):
   count=struct.unpack_from('<I',b,p+off)[0]
   if not 4<=count<=16:continue
   pts=[struct.unpack_from('<3f',b,p+off+4+k*12) for k in range(count)]
   if min(max(abs(a-z) for a,z in zip(pts[0],o['source_xyz'])) for o in obs[1:])<1:matches.append((off,pts))
  assert len(matches)==1,(name,matches);off,pts=matches[0]
  assert max(abs(pts[-1][k]-obs[0]['source_xyz'][k]) for k in (0,2))<1 and abs(pts[-1][1]-obs[0]['source_xyz'][1])<100,(name,pts[-1],obs[0])
  out.append(dict(name=name,conversation_record=i,motion_record=j,conversation_sha256=hashlib.sha256(c).hexdigest(),motion_sha256=hashlib.sha256(d).hexdigest(),flags=[start,moving,arrived,recovered],duration_seconds=duration,duration_ticks=round(duration*30),npc=obs[0],prop=obs[1],trigger=obs[2],spline=spline,spline_offset=p+off,control_points=pts))
 O.mkdir(exist_ok=True);(O/'report.json').write_text(json.dumps(dict(quests=out,source_reward_flag=204,reward_slot=3,source_edf_record=734,source_spline_record=569,limitations='Source script flags and timings recovered; linear control-point traversal, manual L2 interaction, diagnostic markers and ledger slot mapping are adaptations. No original NPC/prop render or dialogue yet.'),indent=2))
 h='/* Generated source placement IDs, timings and control points. */\n';h+='static const U32 qnpc34[]={'+','.join(str(q['npc']['record_offset']) for q in out)+'};\n';h+='static const U32 qtrigger34[]={'+','.join(str(q['trigger']['record_offset']) for q in out)+'};\n';h+='static const U32 qprop34[]={'+','.join(str(q['prop']['record_offset']) for q in out)+'};\n';h+='static const int qduration34[]={'+','.join(str(q['duration_ticks']) for q in out)+'};\n';h+='static const int qcount34[]={'+','.join(str(len(q['control_points'])) for q in out)+'};\n';h+='static const int qpoints34[3][8][3]={'+','.join('{'+','.join('{'+','.join(str(round(v*s)) for v,s in zip(pt,(1,-1,1)))+'}' for pt in q['control_points'])+'}' for q in out)+'};\n';(O/'questdata34.h').write_text(h)
if __name__=='__main__':
 import sys;build(Path(sys.argv[1]))
