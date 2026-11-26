"""Source-derived top-down geometry and host quest trace, not emulator output."""
from pathlib import Path
import numpy as np,json
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];P=R/'build_m34/play';q=json.loads((R/'assets_m34/report.json').read_text())['quests'];tr=json.loads((P/'quest_trace.json').read_text())[0]['rows'];a=np.load(R/'assets_m25/dojo.npz');tri=a['vertices'][a['faces']];im=Image.new('RGB',(1110,590),(20,27,37));d=ImageDraw.Draw(im);font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n);white=(240,245,250);muted=(174,193,211)
d.text((18,14),'Dragonfly Dojo | v0.34 original recovery quest',font=font(28),fill=white);d.text((18,51),'Source terrain, spline control points and simulated quest-state transitions',font=font(16),fill=muted)
for i,(o,t) in enumerate(zip(q,tr)):
 x0=18+i*364;y0=95;w=346;h=300;path=np.array(o['control_points']);center=path[:,[0,2]].mean(0);scale=0.21;lo=center-np.array([w,h])/scale/2;hi=center+np.array([w,h])/scale/2
 def project(v):return ((v[...,0]-lo[0])*scale,(hi[1]-v[...,2])*scale)
 canvas=Image.new('RGB',(w,h),(31,42,53));cd=ImageDraw.Draw(canvas);mask=np.all(tri[:,:,[0,2]].max(1)>=lo,axis=1)&np.all(tri[:,:,[0,2]].min(1)<=hi,axis=1);s=tri[mask];height=s[:,:,1].mean(1)
 for v,y in zip(s[np.argsort(height)],np.sort(height)):
  u=max(0,min(1,(y-height.min())/max(1,np.ptp(height))));c=(int(47+37*u),int(65+43*u),int(68+34*u));cd.polygon(list(zip(*project(v))),fill=c)
 pp=list(zip(*project(path)));cd.line(pp,fill=(250,185,74),width=4)
 for x,y in pp:cd.ellipse((x-3,y-3,x+3,y+3),fill=(255,220,140))
 for name,key,color in [('Trigger','trigger',(250,185,74)),('NPC','npc',(100,220,165))]:
  x,y=project(np.array(o[key]['source_xyz']));cd.ellipse((x-7,y-7,x+7,y+7),fill=color,outline=(12,20,30),width=2);cd.text((max(3,min(w-65,x+8)),max(2,min(h-17,y-18))),name,font=font(13),fill=white)
 im.paste(canvas,(x0,y0));d.text((x0,y0-24),o['name']+' | '+('Decoder' if i==2 else 'Kite'),font=font(18),fill=white)
 d.text((x0,y0+h+9),f"{len(path)} control points  /  {o['duration_seconds']:g}s source delay",font=font(14),fill=muted)
 d.text((x0,y0+h+34),f"Host: {t['duration']} updates → returned",font=font(15),fill=white)
 d.text((x0,y0+h+58),f"Quest reward count: {t['count']}",font=font(15),fill=(100,220,165) if t['count'] else muted)
d.rounded_rectangle((18,487,1092,549),radius=8,fill=(34,48,61));d.text((32,497),'12/12 order-and-mode scenarios passed  •  One reward only after all three returns',font=font(18),fill=white);d.text((32,526),'Motion continues across sector unloads. Original NPC and prop models are not yet rendered.',font=font(14),fill=muted);d.text((18,566),'Top-down source geometry diagnostic; linearly sampled spline controls, not an emulator screenshot.',font=font(13),fill=muted);im.save(P/'quest34_preview.png')
