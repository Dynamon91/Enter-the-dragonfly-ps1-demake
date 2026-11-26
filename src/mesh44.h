#ifndef MESH44_H
#define MESH44_H
#include "models44.h"
/* local y up, z depth. Four headings, integer wing posing, per-face palette lighting. */
static unsigned anim44;
static V42 pose44(Vertex44 p,int x,int y,int z,int dir,int scale,int flap){
 int a=p.x,b=p.y,c=p.z;
 if(p.group){int d=a<0?-a:a;if(d>5)b+=(d-5)*flap/8;}
 a=a*scale/16;b=b*scale/16;c=c*scale/16;
 switch(dir&3){case 1:return(V42){x-c,y+b,z+a};case 2:return(V42){x-a,y+b,z-c};case 3:return(V42){x+c,y+b,z-a};default:return(V42){x+a,y+b,z+c};}
}
static void mesh44(View42*v,const Model44*m,int x,int y,int z,int dir,int scale,int flap,int flash){
 V42 p[256];for(unsigned i=0;i<m->nv;i++)p[i]=pose44(m->v[i],x,y,z,dir,scale,flap);
 for(unsigned i=0;i<m->nf;i++){Face44 f=m->f[i];V42 a=p[f.a],b=p[f.b],c=p[f.c];
  int ux=b.x-a.x,uy=b.y-a.y,uz=b.z-a.z,vx=c.x-a.x,vy=c.y-a.y,vz=c.z-a.z;
  int nx=uy*vz-uz*vy,ny=uz*vx-ux*vz,nz=ux*vy-uy*vx;
  int d=abs41(nx)+abs41(ny)+abs41(nz);if(!d)continue;
  int light=196+(ny*40-nx*20+nz*12)/d;
  unsigned color=flash?0x80e8a0:palette44[f.mat];face42(v,a,b,c,shade42(color,light));
 }
}
static int flap44(int phase){int t=phase&7;return t<4?t-2:5-t;}
static void dragon42(View42*v,const Arena41*a){
 if(a->inv&&(a->inv&4))return;
 mesh44(v,&m44_spyro,a->px,0,a->py,a->face,16,flap44(anim44),0);
 if(a->cd>8){unsigned c=a->breath==FIRE40?0x3080ff:a->breath==ICE40?0xffd080:0x60ffff;for(int i=28;i<=76;i+=12){V42 p=orient42(a,0,10,-i);if(p.x>=16&&p.x<=304&&p.z>=40&&p.z<=208)gem42(v,p.x,p.z,10,4,5,c);}}
}
static void boss42(View42*v,const Arena41*a){
 const Model44*const bosses[]={&m44_crush,&m44_gulp,&m44_ripto,&m44_gnasty,&m44_gnasty};
 int scale=a->id==2&&a->ripto.phase==3?20:13;
 mesh44(v,bosses[a->id],a->bx,0,a->by,2,scale,0,a->state==A41_OPEN);
 /* Alliance second visual actor only; encounter logic remains one collider. */
 if(a->id==4)mesh44(v,&m44_ripto,a->bx+(a->bx<160?32:-32),0,a->by,2,11,0,0);
}
static void fly44(View42*v,int x,int z,int id){int phase=(anim44+id*3)&7;mesh44(v,&m44_dragonfly,x,13+flap44(phase),z,0,16,flap44(phase)*3,0);}
#endif
