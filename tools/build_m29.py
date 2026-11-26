"""Integrate original basket variants and stationary ninja encounter prototype."""
from pathlib import Path
import json,struct,zlib,re,shutil,subprocess
from disc16 import iso,raw,record
R=Path(__file__).resolve().parents[1];O=R/'build_m29/play';OLD=R/'build_m28/play';A=R/'assets_m29'
def build():
 O.mkdir(parents=True,exist_ok=True)
 for p in OLD.iterdir():
  if p.suffix in ('.h','.c','.DAT','.IDX','.json'):shutil.copyfile(p,O/p.name)
 m=json.loads((R/'assets_m27/sector_manifest.json').read_text());baskets=sorted((x['record_offset'],int(re.fullmatch(r'basket(\d+)\.edf',x['edf'],re.I)[1])) for x in m['objects'] if re.fullmatch(r'basket(\d+)\.edf',x['edf'],re.I));enemies=sorted((x['record_offset'],int(x['edf'].lower().startswith('large'))) for x in m['objects'] if x['edf'].lower() in ('small_ninja_riptoc.edf','large_ninja_riptoc.edf'));assert len(baskets)==90 and len(enemies)==25
 arr=lambda a:','.join(map(str,a));(O/'objectids21.h').write_text('static const U32 objectids21[91]={'+arr(x for x,y in baskets)+',0xffffffffu};\nstatic const U8 basketvalue29[90]={'+arr(y for x,y in baskets)+'};\n');(O/'enemyids29.h').write_text('static const U32 enemyids29[25]={'+arr(x for x,y in enemies)+'};\nstatic const U8 enemylarge29[25]={'+arr(y for x,y in enemies)+'};\n');shutil.copyfile(A/'ninjamesh29.h',O/'ninjamesh29.h')
 dat=bytearray((OLD/'DOJOSECT.DAT').read_bytes());idx=bytearray((OLD/'DOJOSECT.IDX').read_bytes());bd=dict(baskets);n=0
 for b in m['blocks']:
  off=b['lba']*2048;start=off+64+36*b['render']+24*b['collision']
  for j in range(b['objects']):
   p=start+16*j;oid=struct.unpack_from('<I',dat,p+12)[0]
   if oid in bd:struct.pack_into('<H',dat,p+6,2);n+=1
  crc=zlib.crc32(dat[off+64:off+b['size']]);struct.pack_into('<I',dat,off+36,crc);struct.pack_into('<I',idx,16+60*b['id']+12,crc)
 assert n==90;(O/'DOJOSECT.DAT').write_bytes(dat);(O/'DOJOSECT.IDX').write_bytes(idx)
 h=(O/'interact21.h').read_text().replace('OBJ21 46','OBJ21 91').replace('BASK21 45','BASK21 90').replace('s->score++;s->pickups++;','s->score+=basketvalue29[id];s->pickups++;');(O/'interact21.h').write_text(h)
 # The 10-value original placement has no decoded dedicated mesh; use existing gem geometry with a provisional blue facet tint.
 h=(O/'collectdata12.h').read_text();part=re.search(r'static const CollectFace gemmesh1\[\d+\]=\{.*?\};',h,re.S).group(0).replace('gemmesh1[','gemmesh10[')
 def tint(m):
  c=int(m[1]);r=c&255;return str((r//3)|((r*2//3)<<8)|(r<<16))+'u'
 part=re.sub(r'(\d+)u',tint,part);(O/'collectdata12.h').write_text(h+'\n'+part+'\n')
 s=(OLD/'play28.c').read_text().replace('#include "firetex11.h"','#include "firetex11.h"\n#include "enemy29.h"\n#include "ninjamesh29.h"')
 # enemy29.h requires Interact21 and Cache18, declared above.
 s=s.replace('else if(value==25){','else if(value==10){f=gemmesh10;n=NFACE20(gemmesh10);}else if(value==25){')
 s=s.replace('else if(kind==2)mesh20(gemmesh1,NFACE20(gemmesh1),x,y-16-(10-interactions.age[id])*5,z,sine[collect.tick&63],sine[(collect.tick+16)&63],cx,cy,cz,sn,cs);','else if(kind==2){const CollectFace*f=gemmesh1;int n=NFACE20(gemmesh1);if(basketvalue29[id]==2){f=gemmesh2;n=NFACE20(gemmesh2);}else if(basketvalue29[id]==5){f=gemmesh5;n=NFACE20(gemmesh5);}else if(basketvalue29[id]==10){f=gemmesh10;n=NFACE20(gemmesh10);}mesh20(f,n,x,y-16-(10-interactions.age[id])*5,z,sine[collect.tick&63],sine[(collect.tick+16)&63],cx,cy,cz,sn,cs);}')
 s=s.replace('static void render18(Player18*p,Anim*a,int y)', '''static void renderenemy29(Player18*p,int cx,int cy,int cz,int sn,int cs){
 for(int j=0;j<cache.count;j++){int k=cache.active[j];const U32*m=cache.meta[k];const U8*t=cache.bytes[k]+64+m[1]*36+m[2]*24;for(U32 i=0;i<m[3];i++,t+=16){if(s18(t+6)!=4)continue;int id=enemy_id29(rd18(t+12));if(id<0||enemy_dead29[id])continue;int x=s18(t)+(int)m[4],y=s18(t+2)+(int)m[5],z=s18(t+4)+(int)m[6];if(ab(x-p->x)>1400||ab(z-p->z)>1400)continue;
 int dx=p->x-x,dz=p->z-z,heading=0,best=-2147483647;for(int q=0;q<64;q++){int d=dx*sine[q]+dz*sine[(q+16)&63];if(d>best){best=d;heading=q;}}int a=sine[heading],b=sine[(heading+16)&63];for(int f=0;f<NFACE20(ninja29mesh);f++){Point v[3];for(int l=0;l<3;l++){const s16*w=ninja29mesh[f].v[l];int scale=enemylarge29[id]?5:4,xx=w[0]*scale/4,yy=w[1]*scale/4,zz=w[2]*scale/4;v[l]=transform(x+((b*xx+a*zz)>>12),y+yy,z+((b*zz-a*xx)>>12),cx,cy,cz,sn,cs);v[l].u=v[l].v=0;}u32 c=ninja29mesh[f].color;worldtri(v[0],v[1],v[2],0x8000|((c>>3)&31)|((c>>6)&0x3e0)|((c>>9)&0x7c00));}
 }}}
static void render18(Player18*p,Anim*a,int y)''')
 s=s.replace('renderinter21(p,cx,cy,cz,sn,cs);','renderinter21(p,cx,cy,cz,sn,cs);renderenemy29(p,cx,cy,cz,sn,cs);')
 s=s.replace('interreset21(&interactions);','interreset21(&interactions);enemy_reset29();')
 s=s.replace('if(collect.events||interactions.pickups)', 'enemy_step29(&interactions,&cache,p.x,p.y,p.z,ox,oz,btn&PAD_SQUARE,p.grounded);if(collect.events||interactions.pickups)')
 # remove simulated damage input: real stationary enemy contact supplies damage now.
 s=s.replace('if(damage)damage21(&interactions);','')
 (O/'play29.c').write_text(s)
 opts=['clang','--target=mipsel-none-elf','-march=mips1','-mabi=32','-mno-abicalls','-fno-pic','-G0'];run=lambda a:subprocess.run(a,cwd=O,check=True)
 run(opts+['-c',str(R/'src/dynamic13_start.s'),'-o','start.o'])
 for p in [O/'play29.c',R/'src/cd17.c',R/'src/sector27.c',R/'src/resident17.c']:run(opts+['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-I',str(O),'-I',str(R/'src'),'-c',str(p),'-o',p.stem+'.o'])
 run(['ld.lld','-m','elf32ltsmip','-T',str(R/'src/dynamic13.ld'),'start.o','play29.o','cd17.o','sector27.o','resident17.o','-o','play29.elf']);run(['llvm-objcopy','-O','binary','play29.elf','play29.bin']);d=(O/'play29.bin').read_bytes();d+=bytes((-len(d))%2048);h=bytearray(2048);h[:8]=b'PS-X EXE';struct.pack_into('<IIII',h,16,0x80010000,0,0x80010000,len(d));struct.pack_into('<II',h,0x30,0x801fff00,0);e=h+d;(O/'ETD_NINJ.EXE').write_bytes(e)
 elf=(O/'play29.elf').read_bytes();off=struct.unpack_from('<I',elf,28)[0];sz,n=struct.unpack_from('<HH',elf,42);high=max(p[2]+p[5] for i in range(n) if (p:=struct.unpack_from('<8I',elf,off+i*sz))[0]==1);rep=dict(exe_bytes=len(e),linked_ram_from_load=high-0x80010000,headroom_to_stack_region=0x801e0000-high,baskets=len(baskets),enemies=len(enemies),basket_reward_value=sum(y for x,y in baskets),mode='Native compilation; provisional stationary encounters');assert high<0x801e0000;(O/'report.json').write_text(json.dumps(rep,indent=2));print(rep,flush=True)
 hs=(R/'tests/interact24_host.c').read_text().replace('../src/cache24.c','cache24.c').replace('../src/collect21.h','collect21.h').replace('../src/interact21.h','interact21.h');hs+='\n#include "enemy29.h"\nvoid ereset29(void){enemy_reset29();}\nint eid29(U32 id){return enemy_id29(id);}\nint dead29(int i){return enemy_dead29[i];}\nint large29(int i){return enemylarge29[i];}\nvoid estep29(Interact21*s,const Cache18*c,int x,int y,int z,int ox,int oz,int charge,int grounded){enemy_step29(s,c,x,y,z,ox,oz,charge,grounded);}\nint bval29(int i){return basketvalue29[i];}\n';(O/'host29.c').write_text(hs);run(['clang','-O2','-shared','-fPIC','-I',str(O),'-I',str(R/'src'),str(O/'host29.c'),str(R/'src/sector27.c'),str(R/'src/cd17.c'),str(R/'src/resident17.c'),str(R/'tests/cd17_mock.c'),'-DCD17_MOCK','-o','host29.so'])
 assets={n:(R/'assets_m16'/n).read_bytes() for n in ('HUBSECT.DAT','HUBSECT.IDX')};assets.update({n:(R/'assets_m20'/n).read_bytes() for n in ('HUBTEX.DAT','HUBTEX.IDX')});assets.update({n:(O/n).read_bytes() for n in ('DOJOSECT.DAT','DOJOSECT.IDX')});assets.update({n:(R/'assets_m27'/n).read_bytes() for n in ('DOJOTEX.DAT','DOJOTEX.IDX')});assets['ETD_POOL.EXE']=(R/'build_m24/play/ETD_POOL.EXE').read_bytes();assets['ETD_SKY.EXE']=(OLD/'ETD_SKY.EXE').read_bytes();s=iso(e,assets);root=bytearray();pos=0
 while s[20][pos]:
  n=s[20][pos];rr=s[20][pos:pos+n];name=bytes(rr[33:33+rr[32]])
  if name==b'ETD_SECT.EXE;1':rr=record(b'ETD_NINJ.EXE;1',22,len(e))
  if name==b'SYSTEM.CNF;1':
   config=b'BOOT = cdrom:\\ETD_NINJ.EXE;1\r\nTCB = 4\r\nEVENT = 10\r\nSTACK = 801FFF00\r\n';s[21][:]=config.ljust(2048,b'\0');rr=record(name,21,len(config))
  root.extend(rr);pos+=n
 s[20][:]=root.ljust(2048,b'\0');(O/'ETD_PSX_M29.bin').write_bytes(b''.join(raw(i,x) for i,x in enumerate(s)));(O/'ETD_PSX_M29.cue').write_text('FILE "ETD_PSX_M29.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
if __name__=='__main__':build()
