"""Host reconstruction of the sector diagnostic viewport, using disc bytes."""
from pathlib import Path
import json,struct
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'build_m17/view';A=ROOT/'assets_m16'
def build():
 m=json.loads((A/'sector_manifest.json').read_text());t=json.loads((A/'texture_report.json').read_text());rgb={x['group']:tuple(x['average_rgb']) for x in t['entries']};colors=[rgb.get(x['texture_group'],(190,110,155)) for x in m['materials']];data=(A/'HUBSECT.DAT').read_bytes();start=json.loads((P/'report.json').read_text())['start'];ids=[start,min(start+1,173),min(start+10,173)];ids.append(max(m['blocks'],key=lambda b:b['collision'])['id']);im=Image.new('RGB',(700,600),(18,24,32));d=ImageDraw.Draw(im);font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n);d.text((18,10),'Dragon Realms | native sector inspection',font=font(24),fill='white');d.text((18,40),'Host preview of disc-resident data • v0.17',font=font(14),fill=(165,180,196));
 for i,id in enumerate(ids):
  b=m['blocks'][id];p=data[b['lba']*2048:][:b['size']];nr,nc,no=struct.unpack_from('<3H',p,24);loX,_,loZ,hiX,_,hiZ=struct.unpack_from('<6h',p,40);span=max(hiX-loX,hiZ-loZ,1);midX=int((loX+hiX)/2);midZ=int((loZ+hiZ)/2);proj=lambda x,z:(160+int((x-midX)*196/span),128-int((z-midZ)*196/span));v=Image.new('RGB',(320,240),(25,27,36));g=ImageDraw.Draw(v);collision=i==3;stride=24 if collision else 36;off=64+36*nr if collision else 64;n=nc if collision else nr;rows=[p[off+j*stride:off+(j+1)*stride] for j in range(n)]
  for q in sorted(rows,key=lambda q:-sum(struct.unpack_from('<9h',q)[1::3])):
   a=struct.unpack_from('<9h',q);c=(70,156,117) if collision else colors[struct.unpack_from('<H',q,30)[0]];g.polygon([proj(a[k],a[k+2]) for k in (0,3,6)],fill=c)
  for j in range(no):
   x,_,z=struct.unpack_from('<3h',p,64+36*nr+24*nc+16*j);a,b1=proj(x,z);g.rectangle((a-1,b1-1,a+1,b1+1),fill=(237,239,53))
  g.text((10,8),f'{id:04d}',fill='white');g.text((120,8),f'{nr:04d}',fill='white');g.text((230,8),f'{nc:04d}',fill='white');g.rectangle((302,8,311,17),fill=(74,189,55));x=18+342*(i%2);y=65+257*(i//2);im.paste(v,(x,y));d.text((x,y+240),f'Block {id}  |  '+('collision candidates' if collision else 'source terrain')+f'  |  {n} faces',font=font(12),fill=(194,206,219))
 d.text((18,584),'Flat material-average colors; not an emulator screenshot or a playable camera.',font=font(11),fill=(165,180,196));im.save(P/'sector_preview.png')
if __name__=='__main__':build()
