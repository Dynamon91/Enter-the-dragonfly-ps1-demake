"""Generate renderer variants while retaining v0.42/v0.43 sources unchanged."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]; S=R/'src'
v=(S/'view42.h').read_text().replace('VIEW42_H','VIEW44_H').replace('#define CAP42 384','#define CAP42 768')
a=v.index('static void dragon42(');b=v.index('static void render42(',a);v=v[:a]+'#include "mesh44.h"\n'+v[b:];(S/'view44.h').write_text(v)
s=(S/'screen43.h').read_text().replace('SCREEN43_H','SCREEN44_H').replace('"view42.h"','"view44.h"').replace('screen43(', 'screen44(')
a=s.index(' for(int x=32;x<=288;x+=64)');b=s.index(' dragon42(v,a);',a)
s=s[:a]+''' mesh44(v,&m44_portal,160,0,45,0,16,0,0);
 const Model44*prop=(l==10||l==16||l==17||l==18)?&m44_crystal:&m44_tree;
 for(int x=35;x<=285;x+=250)mesh44(v,prop,x,0,43,0,12,0,0);
 WpRange39 rr=wp_slots39[l];for(int i=0;i<rr.count;i++)if(!progress_has33(&s->p,rr.first+i)){int x,y;spot43(l,i,&x,&y);fly44(v,x,y,i);}
'''+s[b:];s=s.replace('if(s->error)text43(rect,248,214,"LOCKED",0x6070ff);','if(s->error)rect(304,214,8,10,0x6070ff);') # avoid text overlap
(S/'screen44.h').write_text(s)
T=R/'tests'; (T/'test_view44.c').write_text((T/'test_view42.c').read_text().replace('"view42.h"','"view44.h"'))
