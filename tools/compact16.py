"""Remove redundant per-face texture state while preserving every GPU word."""
import re,json
from pathlib import Path
import numpy as np

def compact(out):
 p=out/'world.h';s=p.read_text();z=np.load(out/'farm06.npz');rep=json.loads((out/'report.json').read_text());ids=z['texture_id'];uv=z['uv'];n=len(rep['bindings']);assert n<256 and ids.min()>=0 and ids.max()<n
 def vals(name):return np.array([int(x) for x in re.findall(r'\d+',re.search(r'\b'+name+r'\[[^;=]+\]\s*=\{(.*?)\};',s,re.S).group(1))],dtype=np.uint32)
 old=vals('worlduv').reshape(-1,3);win=vals('worldwindow');low=uv[:,:,0]|(uv[:,:,1]<<8);assert np.array_equal(low,old&65535);states=[]
 for i in range(n):
  x=ids==i;rows=np.column_stack([old[x,0]>>16,old[x,1]>>16,win[x]]);assert len(rows) and np.all(rows==rows[0]);states.append(rows[0].tolist())
  assert np.all(old[x,2]>>16==0)
 def a(rows):return ','.join('{'+','.join(str(int(x))+'u' for x in row)+'}' for row in rows)
 start=s.index('static const u32 worlduv');end=s.index('static const s16 floorgrid',start)
 s=s[:start]+f'static const u16 worlduv[WF][3]={{'+a(low)+'};\nstatic const unsigned char worldmat[WF]={'+','.join(map(str,ids))+'};\nstatic const u32 worldstate['+str(n)+'][3]={'+a(states)+'};\n'+s[end:];p.write_text(s)
 report={'faces':len(ids),'materials':n,'old_bytes':len(ids)*16,'new_bytes':len(ids)*7+n*12,'logical_savings':len(ids)*9-n*12,'gpu_words_preserved':len(ids)*4};(out/'compact_report.json').write_text(json.dumps(report,indent=2));return report
