"""Compile original CCC conversation branches and English text from local PS2 image."""
import argparse,hashlib,json,re,textwrap
from pathlib import Path
from cnk import ISO,entries,vag_info
from PIL import Image,ImageDraw,ImageFont
SCRIPTS=(668,916,27,372,1088,585) # Dill, Bill, Dean, grab/wait
# 0=end, 1=say, 2=player, 3=sparx, 4=set, 5=clear, 6=check, 7=conditional, 8=reward

def compile_script(raw):
    lines=[s.split('#',1)[0].strip() for s in raw.decode('ascii').splitlines()]
    text='\n'.join(x for x in lines if x); name=int(re.search(r'Name\s*:\s*(\d+)',text)[1]); branches={}; skipped=set(); current=None; depth=0; cond=False
    for l in text.splitlines():
        m=re.fullmatch(r'Branch\s+(\d+)',l)
        if m:
            assert depth==0;current=int(m[1]);assert current not in branches;branches[current]=[];continue
        if l=='{':depth+=1;continue
        if l=='}':
            depth-=1
            if depth==1 and cond:cond=False
            elif depth==0 and current is not None:branches[current].append([0,0,0]);current=None
            continue
        if current is None:continue
        ops=branches[current];p=l.split();k=p[0]
        if k=='Condition':assert not cond;cond=True;ops.append([9,0,0]);continue
        if k in ('Say','Player','Sparx'):assert not cond;ops.append([('Say','Player','Sparx').index(k)+1,int(p[1]),0]);continue
        if k in ('WorldFlagOn','WorldFlagOff'):
            group,flag=map(int,p[1:]);assert group in (2,9) and 0<=flag<1024
            if cond:assert k=='WorldFlagOn';ops.append([6,flag,group])
            else:ops.append([4 if k=='WorldFlagOn' else 5,flag,group])
            continue
        if k=='FailBranch':assert cond;ops.append([10,int(p[1]),0]);continue
        if k=='SuccessBranch':assert cond and ops[-1][0]==10;ops[-1]=[7,ops[-1][1],int(p[1])];continue
        if k=='Give':assert p==['Give','Dragonflies','1'];ops.append([8,1,0]);continue
        if k in ('NonInterruptible','MoveRel','MovePRel','SnapSRel','PlaySound'):skipped.add(k);continue
        raise ValueError('unknown script command: '+l)
    assert depth==0 and 0 in branches
    offset={};program=[]
    for k,ops in sorted(branches.items()):offset[k]=len(program);program.extend(ops)
    for op in program:
        if op[0]==7:op[1]=offset[op[1]];op[2]=offset[op[2]]
        assert op[0]!=10
    return name,program,sorted(skipped)

def build(iso,out):
    out.mkdir(parents=True,exist_ok=False)
    with ISO(iso) as d:
        b=d.file('SPYRODAT/CHUNKS3/L_2_CC.CNK');r={i:b[o:o+s] for i,h,o,s,t in entries(b)}
        title=d.file('SPYRODAT/CHUNKS2/TITLE.CNK');_,h,o,s,t=next(x for x in entries(title) if x[0]==83);table=title[o:o+s]
    lines={}
    for l in table.splitlines():
        m=re.fullmatch(rb'\s*(\d+)\s+(\d+)\s*:\s*"(.*)"\s*',l)
        if m:lines[int(m[1])]=(int(m[2]),m[3].decode('latin1'))
    ids=set();scripts=[];h=[]
    for i,rec in enumerate(SCRIPTS):
        name,program,skipped=compile_script(r[rec]);ids.add(name);ids.update(op[1] for op in program if op[0] in (1,2,3));h.append('static const TalkOp60 ops60_%d[]={%s};'%(i,','.join('{%d,%d,%d}'%tuple(op) for op in program)));scripts.append(dict(record=rec,name=name,sha256=hashlib.sha256(r[rec]).hexdigest(),program=program,skipped=skipped))
    h.append('static const TalkScript60 scripts60[]={'+','.join('{ops60_%d,%d,%d}'%(i,len(s['program']),s['name']) for i,s in enumerate(scripts))+'};')
    voice={};q={}
    for id in sorted(ids):
        v,t=lines[id];wrapped=textwrap.fill(t,48,break_long_words=False,break_on_hyphens=False);assert len(wrapped.splitlines())<=6 and max(map(len,wrapped.splitlines()))<=48 and t.isascii()
        q[id]=dict(voice=v,text=t,wrapped=wrapped);candidates=[]
        for i,s in r.items():
            a=vag_info(s)
            if v and a and re.fullmatch(r'dus'+str(v)+r'(?:b)?(?:\.?wav)?',a['name'],re.I):candidates.append(dict(record=i,sha256=hashlib.sha256(s).hexdigest(),**a))
        if v:voice[id]=candidates
    h.append('static const char *talktext60(int id){switch(id){'+''.join('case %d:return %s;'%(i,json.dumps(q[i]['wrapped'])) for i in sorted(ids))+'default:return "";}}')
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',9);glyph=[]
    for i in range(32,127):
        im=Image.new('L',(6,10));ImageDraw.Draw(im).text((0,-1),chr(i),font=font,fill=255);glyph.append([sum(1<<(5-x) for x in range(6) if im.getpixel((x,y))>=80) for y in range(10)])
    h.append('static const unsigned char talkfont60[95][10]={'+','.join('{'+','.join(map(str,x))+'}' for x in glyph)+'};')
    (out/'talkdata60.h').write_text('\n'.join(h)+'\n');(out/'dialogue60.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(b).hexdigest(),language_sha256=hashlib.sha256(table).hexdigest(),scripts=scripts,lines=q,voice_candidates=voice),indent=2)+'\n');print('scripts',len(scripts),'text entries',len(ids),'unique voice candidates',sum(len(x)==1 for x in voice.values()),'/',len(voice))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('iso',type=Path);p.add_argument('out',type=Path);a=p.parse_args();build(a.iso,a.out)
