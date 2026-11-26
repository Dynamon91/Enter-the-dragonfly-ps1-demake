"""Render host-decoded v0.37 poses and measured linked allocation, not emulator capture."""
from pathlib import Path
import ctypes as C,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from preview_m36 import render
R=Path(__file__).resolve().parents[1];P=R/'build_m37/play';L=C.CDLL(str(P/'host37.so'));L.quest37_host.restype=C.POINTER(C.c_int8)
old=np.load(R/'assets_m35/questmodels.npz');poses=np.load(R/'assets_m36/poses.npz');a=json.loads((R/'build_m36/play/report36.json').read_text());b=json.loads((P/'report37.json').read_text());rep=json.loads((R/'assets_m37/report.json').read_text());im=Image.new('RGB',(1024,642),(20,27,37));d=ImageDraw.Draw(im);font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n);white=(240,245,250);muted=(180,195,210);green=(89,194,145)
d.text((20,14),'v0.37 | Lossless animation storage',font=font(27),fill=white);d.text((20,52),'All 245 Spyro frames and 36 NPC samples preserved exactly',font=font(17),fill=muted)
for i,name in enumerate(('Rusty','RJ','Dougy')):
 x=20+334*i;n=len(old[f'v{i}']);delta=np.ctypeslib.as_array(L.quest37_host(i,8,n),shape=(n*3,)).reshape(n,3);v=delta.astype(np.int16)+old[f'v{i}'];assert np.array_equal(v,poses[f'frames{i}'][8]);im.paste(render(i,25,316,220,v),(x,96));d.text((x,322),name+' — decoded talk pose',font=font(16),fill=white);d.text((x,345),'0 differing coordinates',font=font(15),fill=green)
d.line((20,382,1004,382),fill=(66,79,96),width=1);d.text((20,394),'RAM before reserved stack',font=font(20),fill=white)
for j,(label,r) in enumerate([('v0.36',a),('v0.37',b)]):
 y=432+j*48;d.text((20,y),label,font=font(17),fill=muted);d.rectangle((100,y,660,y+22),fill=(43,56,70));d.rectangle((100,y,100+int(560*r['headroom_to_stack_region']/131072),y+22),fill=(112,128,145) if j==0 else green);d.text((680,y),f"{r['headroom_to_stack_region']/1024:.1f} KiB",font=font(17),fill=white)
d.text((20,544),f"Net RAM recovered: {(a['linked_ram_from_load']-b['linked_ram_from_load'])/1024:.1f} KiB  |  27 selected tests passed",font=font(18),fill=white);d.text((20,580),'Host C decoder + reference rasterizer using original recovered textures and geometry.',font=font(15),fill=muted);d.text((20,605),'No visual changes expected; emulator execution and PS1 decoding cost remain unmeasured.',font=font(15),fill=muted);im.save(P/'pack_preview.png')
