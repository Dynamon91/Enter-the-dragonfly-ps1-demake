#include "ufo64.h"
#define UFO_ID64 0x7020
static Ufo64 ufostate64;
static int ufo_ready64,light_ticks64,light_x64,light_y64,light_z64,light_ex64,light_ey64,light_ez64;
static int ufo_upload64(void){ufo_ready64=0;for(int i=0;i<UFO_TEX64;i++){
 if(!cd17_read(0,ufo_extent64[0]+3*i,3,tbuf)||rd18(tbuf)!=0x54445445u||s18(tbuf+4)!=1||s18(tbuf+6)!=i||!rd18(tbuf+8)||rd18(tbuf+8)>1024||!rd18(tbuf+12)||rd18(tbuf+12)>1024||rd18(tbuf+16)!=4608||rd18(tbuf+20)!=ufo_crc64[i]||texcrc19(tbuf+24,4608)!=ufo_crc64[i])return 0;
 uploadtex19(0,51+i,tbuf+24);}idle();ufo_ready64=1;return 1;}
static void reset_ufo64(void){ufo_reset64(&ufostate64);light_ticks64=0;}
/* Aimed lightning from the original player position, floor checked along the
 * ray. Cannon contact uses a conservative base collision proxy. */
static int lightning_hit64(const Cache18*c,int x,int y,int z,int ground,int heading,const int*target,const short*sn){
 int tx=target[0],tz=target[2],ty=target[1];if(abs18(tx-x)>1050||abs18(tz-z)>1050||abs18(ty-y)>300)return 0;
 int g=cache18_floor(c,tx,tz,ty,300);if(g==NONE18||!path20(c,x,ground,z,tx,g,tz,1100))return 0;
 int a=sn[heading&63],b=sn[(heading+16)&63];for(int d=95;d<=800;d+=45){int xx=x+(a*d>>12),zz=z+(b*d>>12);int dx=tx-xx,dz=tz-zz;if(abs18(dx)<=220&&abs18(dz)<=220&&dx*dx+dz*dz<=220*220)return 1;}return 0;
}
static void ufo_step64(Player18*p,int mode,int fire){if(!ufo_ready64)return;if(light_ticks64)light_ticks64--;
 if(mode==2&&fire&&!active60(&talk60)&&!light_ticks64){light_ticks64=6;light_x64=p->x+(sine[p->heading]*95>>12);light_y64=p->y-125;light_z64=p->z+(sine[(p->heading+16)&63]*95>>12);light_ex64=p->x+(sine[p->heading]*800>>12);light_ey64=light_y64;light_ez64=p->z+(sine[(p->heading+16)&63]*800>>12);
  for(int i=0;i<4;i++)if(ufo_available64(&ufostate64,&talk60,i)&&lightning_hit64(&cache,p->x,p->y,p->z,p->ground,p->heading,cannonpos64[i],sine)){if(ufo_trigger64(&ufostate64,&talk60,i,mode)){light_ex64=cannonpos64[i][0];light_ey64=cannonpos64[i][1]-125;light_ez64=cannonpos64[i][2];sfx_play(2);}break;}}
 ufo_tick64(&ufostate64,&talk60);
}
static void ufo_mesh64(const UfoFace64*f,int n,int x,int y,int z,int yaw,int cx,int cy,int cz,int sn,int cs){int a=sine[yaw&63],b=sine[(yaw+16)&63];for(int i=0;i<n;i++){Point q[3];for(int j=0;j<3;j++){const short*v=f[i].v[j];q[j]=transform(x+((b*v[0]+a*v[2])>>12),y+v[1],z+((b*v[2]-a*v[0])>>12),cx,cy,cz,sn,cs);q[j].u=f[i].uv[2*j];q[j].v=f[i].uv[2*j+1];}worldtri(q[0],q[1],q[2],UFO_ID64+f[i].tex);}}
static void ufo_draw64(Player18*p,int cx,int cy,int cz,int sn,int cs){if(!ufo_ready64)return;
 if(flag60(talk60.flags[0],0)){for(int i=0;i<4;i++){const int*a=cannonpos64[i];if(flag60(talk60.flags[0],i+3)||ab(p->x-a[0])>2700||ab(p->z-a[2])>2700)continue;ufo_mesh64(cannon64,NFACE20(cannon64),a[0],a[1],a[2],a[3],cx,cy,cz,sn,cs);}if(ufostate64.phase!=4&&ab(p->x-ufostate64.x)<5000&&ab(p->z-ufostate64.z)<5000)ufo_mesh64(ufo64,NFACE20(ufo64),ufostate64.x,ufostate64.y,ufostate64.z,ufostate64.yaw,cx,cy,cz,sn,cs);}
 for(int i=0;i<2;i++){const int*a=polepos64[i];if(ab(p->x-a[0])<1600&&ab(p->z-a[2])<1600)ufo_mesh64(pole64,NFACE20(pole64),a[0],a[1],a[2],a[3],cx,cy,cz,sn,cs);}
 if(light_ticks64){for(int i=0;i<8;i++){Point q[4];for(int j=0;j<4;j++){int t=i+(j&1),x=light_x64+(light_ex64-light_x64)*t/8,y=light_y64+(light_ey64-light_y64)*t/8,z=light_z64+(light_ez64-light_z64)*t/8;int w=(j&2)?7:-7;y+=(t==0||t==8?0:(t&1?18:-18))+w;q[j]=transform(x,y,z,cx,cy,cz,sn,cs);q[j].u=q[j].v=0;}worldtri(q[0],q[1],q[2],0xffff);worldtri(q[1],q[3],q[2],0xffff);}}
}
static void ufo_hud64(Player18*p){if(active60(&talk60)||!flag60(talk60.flags[0],0))return;for(int i=0;i<4;i++)if(ab(p->x-cannonpos64[i][0])<2100&&ab(p->z-cannonpos64[i][2])<2100){rect(5,180,220,13,0x201c28);text60(10,181,ufostate64.phase==4?"UFO DOWN - CATCH THE DRAGONFLY":ufostate64.phase?"UFO IN FLIGHT":i==ufostate64.stage?"LIGHTNING: FIRE CANNON":"FOLLOW THE UFO",0xffffff);break;}}
