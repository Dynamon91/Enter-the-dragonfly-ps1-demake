"""Resolve original Dojo conversation IDs against the English title language table."""
from pathlib import Path
from cnk import ISO,entries
from dojo25 import records
from PIL import Image,ImageDraw,ImageFont
import json,re,hashlib,textwrap,sys
R=Path(__file__).resolve().parents[1];A=R/'assets_m36'
# internal Tootie/Huey/Dooie; greeting, help, thanks, other, completed, alternate
TABLE=[(259,429,[430,431,432,467,468,468]),(982,419,[420,421,428,423,422,422]),(271,425,[426,427,422,0,466,465])]
def build(iso):
 A.mkdir(exist_ok=True);r=records(iso);path='SPYRODAT/CHUNKS2/TITLE.CNK';idx=83
 with ISO(iso) as d:b=d.file(path)
 _,h,o,s,t=next(x for x in entries(b) if x[0]==idx);data=b[o:o+s];lines={}
 for l in data.splitlines():
  m=re.fullmatch(rb'\s*(\d+)\s+(\d+)\s*:\s*"(.*)"\s*',l)
  if m:lines[int(m[1])]=(int(m[2]),m[3].decode('latin1'))
 wanted={418};rep=[]
 for rec,name,ids in TABLE:
  script=r[rec][1];assert int(re.search(rb'Name\s*:\s*(\d+)',script)[1])==name;actual=set(map(int,re.findall(rb'\bSay\s+(\d+)',script)));assert actual==set(ids)-{0}|{418};wanted.update([name]+[i for i in ids if i]);rep.append(dict(script_record=rec,script_sha256=hashlib.sha256(script).hexdigest(),name_id=name,name=lines[name][1],line_ids=ids))
 assert all(i in lines for i in wanted);q={i:dict(voice=lines[i][0],text=lines[i][1],wrapped=textwrap.fill(lines[i][1],48,break_long_words=False,break_on_hyphens=False)) for i in sorted(wanted)};assert max(max(map(len,x['wrapped'].splitlines())) for x in q.values())<=48;assert max(len(x['wrapped'].splitlines()) for x in q.values())<=5
 out=dict(source_container=path,source_record=idx,source_sha256=hashlib.sha256(data).hexdigest(),actors=rep,lines=q,limitations='Title English text; LANG_SEL copy differs in punctuation. Dialogue state presentation reconstructed; source flag 4 999 shortcut and exact cameras/voice not implemented.');(A/'dialogue_report.json').write_text(json.dumps(out,indent=2));
 # font glyphs from installed DejaVu Mono, small native bitmap, not original game font.
 f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',9);glyph=[]
 for i in range(32,127):
  im=Image.new('L',(6,10));d=ImageDraw.Draw(im);d.text((0,-1),chr(i),font=f,fill=255,stroke_width=0);glyph.append([sum((1<<(5-x)) for x in range(6) if im.getpixel((x,y))>=80) for y in range(10)])
 h='/* Generated from local English table and independent bitmap font. */\nstatic const char *qtext36(int id){switch(id){\n'+''.join(f'case {i}:return '+json.dumps(x['wrapped'],ensure_ascii=True)+';\n' for i,x in q.items())+'default:return "";}}\n';h+='static const U8 qfont36[95][10]={'+','.join('{'+','.join(map(str,x))+'}' for x in glyph)+'};\n';(A/'dialogue36.h').write_text(h);print('lines',len(q),'names',[x['name'] for x in rep]);
if __name__=='__main__':build(Path(sys.argv[1]))
