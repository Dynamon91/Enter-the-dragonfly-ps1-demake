#ifndef DRAW41_H
#define DRAW41_H
/* Renderer shared by the PS1 GPU and host reference frame. RGB is PS1 BGR order. */
typedef void (*Rect41)(int,int,int,int,unsigned int);
static void draw41(const Arena41*a,Rect41 r){
 r(0,0,320,240,0x30251e);r(12,36,296,176,0x655744);r(16,40,288,168,0x4b6551);
 for(int x=24;x<304;x+=24)r(x,40,1,168,0x435b49);for(int y=48;y<208;y+=24)r(16,y,288,1,0x435b49);
 for(int i=0;i<5;i++)r(16+58*i,8,50,8,(a->wins&(1<<i))?0x66d070:i==a->id?0x40caff:0x60554a);
 for(int i=0;i<4;i++)r(16+18*i,22,14,8,i<a->hp?0x5050e0:0x433b33);
 int hp=a->id==2?a->ripto.hp:a->bhp;for(int i=0;i<7;i++)r(174+18*i,22,14,8,i<hp?0x60b0e0:0x433b33);
 if(a->id==0&&a->state==A41_ATTACK){int d=(24-a->timer)*5;int x=a->bx-d,y=a->by-d;/* diamond shockwave */for(int i=0;i<=d;i+=4){int xx[4]={x+i,a->bx+i,x+i,a->bx+i};int yy[4]={a->by-i,y+i,a->by+i,a->by+d-i};for(int j=0;j<4;j++)if(xx[j]>=16&&xx[j]<302&&yy[j]>=40&&yy[j]<206)r(xx[j],yy[j],3,3,0x60e0ff);}}
 unsigned int c=a->state==A41_OPEN?0x60d080:a->state==A41_ATTACK?0x4050e0:0x6090b0;
 r(a->bx-15,a->by+10,30,5,0x303c30);r(a->bx-12,a->by-12,24,24,c);r(a->bx-8,a->by-16,6,7,0x9bc0d0);r(a->bx+2,a->by-16,6,7,0x9bc0d0);
 for(int i=0;i<6;i++)if(a->shot[i].life)r(a->shot[i].x-3,a->shot[i].y-3,7,7,0x40b0ff);
 if(!a->inv||!(a->inv&4)){r(a->px-9,a->py+5,18,5,0x303c30);r(a->px-7,a->py-6,14,12,0xc05ca0);r(a->px-12,a->py-3,5,7,0x4080ff);r(a->px+7,a->py-3,5,7,0x4080ff);int x=a->face==1?7:a->face==3?-11:-2,y=a->face==2?6:a->face==0?-10:-2;r(a->px+x,a->py+y,5,5,0x70b0ff);}
 if(a->cd>8){int x=a->face==1?a->px+10:a->face==3?a->px-82:a->px-3,y=a->face==2?a->py+10:a->face==0?a->py-82:a->py-3;int w=(a->face&1)?72:6,h=(a->face&1)?6:72;int x1=clamp41(x,16,304),y1=clamp41(y,40,208),x2=clamp41(x+w,16,304),y2=clamp41(y+h,40,208);if(x2>x1&&y2>y1)r(x1,y1,x2-x1,y2-y1,a->breath==FIRE40?0x3080ff:a->breath==ICE40?0xffd080:0x60ffff);}
 r(16,220,25,10,a->breath==FIRE40?0x3080ff:a->breath==ICE40?0xffd080:0x60ffff);r(50,220,120,10,0x60554a);if(a->timer>0)r(50,220,clamp41(a->timer*2,1,120),10,c);
 if(a->id==2){for(int i=0;i<3;i++)r(102+12*i,22,8,8,i<a->ripto.shield?0xffd080:0x433b33);for(int i=0;i<3;i++)r(185+14*i,234,10,3,i<a->ripto.cleared?0x66d070:i==a->ripto.phase-1?0x40caff:0x60554a);}
 if(a->state>=A41_WIN)r(185,220,119,10,a->state==A41_WIN?0x66d070:0x4050e0);
}
#endif
