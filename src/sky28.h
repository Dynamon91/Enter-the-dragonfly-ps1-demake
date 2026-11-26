/* Camera-relative background, submitted before terrain. Uses separate fixed VRAM slots.
 * Opaque globe, additive sun, then half-blended clouds. No sector or collision state. */
#include "skydata28.h"
static void sky_upload28(void){for(int i=0;i<4;i++){uploadrect19(768,4+i,256,1,(const U8*)sky_pal28[i]);uploadrect19(832+i*32,256,32,64,sky_pix28[i]);}gp(0x01000000);idle();}
static void sky_tri28(Point a,Point b,Point c,int layer){
 int u[3],v[3];if(layer==1||layer==2){Point *p[3]={&a,&b,&c};for(int i=0;i<3;i++){int x=p[i]->u,y=p[i]->v;u[i]=x<0?0:x>=1024?63:x>>4;v[i]=y<0?0:y>=1024?63:y>>4;}}
 else if(layer==0){if(!uvaxis19(a.u,b.u,c.u,u))return;int vv[3]={a.v,b.v,c.v};for(int i=0;i<3;i++)v[i]=vv[i]<0?0:vv[i]>=1024?63:vv[i]>>4;}
 else {if(!uvaxis19(a.u,b.u,c.u,u)||!uvaxis19(a.v,b.v,c.v,v))return;}
 Point q[3]={a,b,c};int sx[3],sy[3];for(int i=0;i<3;i++){q[i].screen=project(q[i].x,q[i].y,q[i].z).screen;sx[i]=(s16)q[i].screen;sy[i]=(s16)(q[i].screen>>16);}
 if((sx[1]-sx[0])*(sy[2]-sy[0])==(sx[2]-sx[0])*(sy[1]-sy[0]))return;
 /* Window masks 64x64. Semi-transparency mode: 0 average (cloud), 1 add (sun). */
 gp(0xe2000000u|24|(24<<5)|(layer*8<<10));gp(layer==0?0x25808080u:0x27808080u);
 gp(q[0].screen);gp((u[0]&255)|((v[0]&255)<<8)|((48|((4+layer)<<6))<<16));
 gp(q[1].screen);gp((u[1]&255)|((v[1]&255)<<8)|((13|16|128|((layer==1||layer==2)?32:0))<<16));
 gp(q[2].screen);gp((u[2]&255)|((v[2]&255)<<8));
}
static void sky_draw28(int sn,int cs){
 for(int i=0;i<SKY_N28;i++){const SkyTri28*t=&sky_triangles28[i];Point p[3],out[CLIP_CAP];for(int j=0;j<3;j++){const s16*v=t->v[j];p[j]=camera_space(v[0],v[1],v[2],0,0,0,sn,cs);p[j].u=v[3];p[j].v=v[4];}int n=cliptriangle(p[0],p[1],p[2],out);for(int j=1;j+1<n;j++)sky_tri28(out[0],out[j],out[j+1],t->layer);}
 gp(0xe2000000u);
}
