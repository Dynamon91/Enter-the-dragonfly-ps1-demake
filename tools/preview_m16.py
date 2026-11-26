"""Overhead map of the real source-derived sector pack, not emulator gameplay."""
from pathlib import Path
import json,struct
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'assets_m16'
def build(out):
 m=json.loads((A/'sector_manifest.json').read_text());r=json.loads((A/'texture_report.json').read_text());rgb={x['group']:tuple(x['average_rgb']) for x in r['entries']};b=(A/'HUBSECT.DAT').read_bytes();tri=[];colors=[]
 for q in m['blocks']:
  off=q['lba']*2048+64;org=np.array(q['origin']);
  for i in range(q['render']):
   p=np.frombuffer(b,'<i2',9,off).reshape(3,3)+org;mi=struct.unpack_from('<H',b,off+30)[0];t=m['materials'][mi];tri.append(p);colors.append(rgb.get(t['texture_group'],(190,110,155)));off+=36
 tri=np.asarray(tri);lo=tri[:,:,[0,2]].min((0,1));hi=tri[:,:,[0,2]].max((0,1));w,h=1000,700;panel=(465,490);scale=min((panel[0]-28)/(hi[0]-lo[0]),(panel[1]-30)/(hi[1]-lo[1]));mid=(lo+hi)/2
 def proj(p,x,y):
  a=np.asarray(p);return np.rint((a-mid)*[scale,-scale]+[x+panel[0]/2,y+panel[1]/2]).astype(int)
 im=Image.new('RGB',(w,h),(20,25,35));d=ImageDraw.Draw(im);font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf';F=lambda n:ImageFont.truetype(font,n);B=lambda n:ImageFont.truetype(bold,n)
 d.text((24,18),'DRAGON REALMS  /  SECTOR ATLAS',font=B(26),fill=(244,247,251));d.text((25,52),'v0.16  •  Original geometry and object locations decoded from the PS2 source',font=F(15),fill=(172,187,202));
 for x,title,sub in [(22,'Recovered geometry','Overhead projection • original texture-average colors'),(512,'Disc sector layout','4,096-unit cells • 174 independently checked blocks')]:
  d.rounded_rectangle((x,88,x+465,635),radius=10,fill=(30,39,51),outline=(64,80,96));d.text((x+13,100),title,font=B(19),fill='white');d.text((x+13,126),sub,font=F(12),fill=(174,191,207))
 # Higher surfaces drawn last in top-down Y-down world.
 a=proj(tri[:,:,[0,2]],22,145)
 for i in np.argsort(-tri[:,:,1].mean(1),kind='stable'):
  d.polygon([tuple(v) for v in a[i]],fill=colors[i]);
 from collections import Counter
 cnt=Counter(tuple(q['cell']) for q in m['blocks']);faces=Counter()
 for q in m['blocks']:faces[tuple(q['cell'])]+=q['render']
 for k,n in cnt.items():
  p=proj([[k[0]*4096,k[1]*4096],[(k[0]+1)*4096,(k[1]+1)*4096]],512,145);x0,y0=p.min(0);x1,y1=p.max(0);v=min(1,faces[k]/1800);col=(int(36+55*v),int(70+88*v),int(89+85*v));d.rectangle((x0,y0,x1,y1),fill=col,outline=(84,116,132));
  if n>1:d.rectangle((x0+2,y0+2,x1-2,y1-2),outline=(239,169,70),width=2)
 # object positions on both views; mark only sheep and original gems to preserve readability.
 for x in [22,512]:
  for p in m['objects']:
   if p['kind'] not in (1,3):continue
   px,py=proj([p['source_xyz'][0],p['source_xyz'][2]],x,145);rr=3 if p['kind']==3 else 1;col=(249,237,215) if p['kind']==3 else (112,225,142);d.ellipse((px-rr,py-rr,px+rr,py+rr),fill=col)
  px,py=proj([36848,-1200],x,145);d.ellipse((px-5,py-5,px+5,py+5),outline=(225,105,255),width=2)
 d.text((26,648),'● Gems   ○ Sheep (white)   ◉ Current farm spawn (purple)',font=F(14),fill=(191,207,220));d.text((515,648),'Amber outline: cell split across two blocks',font=F(14),fill=(228,181,111));d.text((26,674),'Source-data visualization; not a native gameplay screenshot. Missing textures are marked pink.',font=F(12),fill=(150,165,181));im.save(out)
if __name__=='__main__':build(ROOT/'build_m16/play/sector_atlas.png')
