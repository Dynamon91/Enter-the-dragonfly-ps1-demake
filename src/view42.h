#ifndef VIEW42_H
#define VIEW42_H
/* Fixed-camera integer perspective; original diagnostic geometry, not game assets. */
typedef struct {int x,y,z;} V42; /* y is height, z is arena depth coordinate */
typedef struct {int x,y;} P42;
typedef struct {P42 p[3];int depth;unsigned c;} T42;
typedef void (*Tri42)(P42,P42,P42,unsigned);
#define CAP42 384
typedef struct {T42 t[CAP42];int n,dropped;} View42;
static P42 project42(V42 v){int d=360-v.z;return (P42){160+(v.x-160)*236/d,34+(112-v.y)*236/d};}
static void face42(View42*v,V42 a,V42 b,V42 c,unsigned color){
 if(v->n>=CAP42){v->dropped++;return;}
 P42 p=project42(a),q=project42(b),r=project42(c);
 if((q.x-p.x)*(r.y-p.y)==(q.y-p.y)*(r.x-p.x))return;
 v->t[v->n++]=(T42){{p,q,r},a.z+b.z+c.z,color};
}
static void quad42(View42*v,V42 a,V42 b,V42 c,V42 d,unsigned col){face42(v,a,b,c,col);face42(v,a,c,d,col);}
static unsigned shade42(unsigned c,int k){return (((c&255)*k>>8)&255)|(((((c>>8)&255)*k>>8)&255)<<8)|(((((c>>16)&255)*k>>8)&255)<<16);}
static void box42(View42*v,int x,int z,int y,int w,int l,int h,unsigned c){
 V42 a={x-w,y,z-l},b={x+w,y,z-l},d={x-w,y,z+l},e={x+w,y,z+l};
 V42 A={a.x,y+h,a.z},B={b.x,y+h,b.z},D={d.x,y+h,d.z},E={e.x,y+h,e.z};
 quad42(v,A,B,E,D,c);quad42(v,a,A,D,d,shade42(c,164));quad42(v,b,e,E,B,shade42(c,205));quad42(v,d,D,E,e,shade42(c,230));quad42(v,a,b,B,A,shade42(c,145));
}
static void gem42(View42*v,int x,int z,int y,int w,int h,unsigned c){V42 a={x-w,y,z},b={x,y,z-w},d={x+w,y,z},e={x,y,z+w},p={x,y+h,z},q={x,y-h,z};face42(v,a,b,p,c);face42(v,b,d,p,shade42(c,215));face42(v,d,e,p,shade42(c,185));face42(v,e,a,p,shade42(c,238));face42(v,b,a,q,shade42(c,150));face42(v,d,b,q,shade42(c,170));face42(v,e,d,q,shade42(c,190));face42(v,a,e,q,shade42(c,205));}
static V42 orient42(const Arena41*a,int x,int h,int z){int dx=x,dz=z;switch(a->face){case 1:dx=-z;dz=x;break;case 2:dx=-x;dz=-z;break;case 3:dx=z;dz=-x;break;}return(V42){a->px+dx,h,a->py+dz};}
static void dragon42(View42*v,const Arena41*a){
 int x=a->px,z=a->py;unsigned purple=0xe16db5,orange=0x48baff;
 if(a->inv&&(a->inv&4))return;
 box42(v,x,z,4,8,13,12,purple);
 V42 p=orient42(a,0,13,-14);gem42(v,p.x,p.z,17,8,8,purple);
 V42 h=orient42(a,0,9,-20);box42(v,h.x,h.z,9,5,5,5,0xbb70cb);
 for(int s=-1;s<=1;s+=2){V42 f=orient42(a,s*5,4,-7);box42(v,f.x,f.z,0,3,4,6,purple);f=orient42(a,s*5,4,8);box42(v,f.x,f.z,0,3,4,6,purple);V42 k=orient42(a,s*4,23,-13);gem42(v,k.x,k.z,23,2,6,orange);
 face42(v,orient42(a,s*5,13,0),orient42(a,s*22,19,5),orient42(a,s*15,8,16),orange);face42(v,orient42(a,s*5,13,0),orient42(a,s*15,8,16),orient42(a,s*5,10,10),shade42(orange,185));}
 face42(v,orient42(a,-4,8,10),orient42(a,0,5,30),orient42(a,4,8,10),purple);face42(v,orient42(a,0,14,10),orient42(a,0,5,30),orient42(a,-4,8,10),shade42(purple,190));
 if(a->cd>8){unsigned c=a->breath==FIRE40?0x3080ff:a->breath==ICE40?0xffd080:0x60ffff;for(int i=28;i<=76;i+=12){p=orient42(a,0,10,-i);if(p.x>=16&&p.x<=304&&p.z>=40&&p.z<=208)gem42(v,p.x,p.z,10,4,5,c);}}
}
static void boss42(View42*v,const Arena41*a){int x=a->bx,z=a->by,w=a->id==1?21:13,h=a->id==2?29:24;unsigned c=a->state==A41_OPEN?0x72c591:(a->id==2?0x728ce3:a->id==1?0x5896bd:0x79934e);box42(v,x,z,0,w,11,h,c);gem42(v,x,z-3,h+7,w-2,10,c);for(int s=-1;s<=1;s+=2){box42(v,x+s*(w+4),z,7,5,6,h-6,shade42(c,180));gem42(v,x+s*7,z-5,h+16,3,7,0x84d3ed);}}
static void render42(View42*v,const Arena41*a,Rect41 rect,Tri42 tri){
 v->n=v->dropped=0;rect(0,0,320,240,0x684047);rect(0,35,320,205,0x51433d);
 for(int z=40;z<208;z+=24)for(int x=16;x<304;x+=36){int zz=clamp41(z+24,40,208);unsigned c=((x/36+z/24)&1)?0x526c63:0x476059;quad42(v,(V42){x,0,z},(V42){x+36,0,z},(V42){x+36,0,zz},(V42){x,0,zz},c);}
 /* Draw floor first; sort solid geometry far-to-near by centroid depth. */
 for(int i=0;i<v->n;i++)tri(v->t[i].p[0],v->t[i].p[1],v->t[i].p[2],v->t[i].c);v->n=0;
 for(int x=32;x<=288;x+=64)box42(v,x,43,0,7,6,35,0x9b8980);
 box42(v,18,124,0,3,80,9,0x887d70);box42(v,302,124,0,3,80,9,0x887d70);
 dragon42(v,a);boss42(v,a);for(int i=0;i<6;i++)if(a->shot[i].life)gem42(v,a->shot[i].x,a->shot[i].y,9,5,6,0x40b0ff);
 if(a->id==0&&a->state==A41_ATTACK){int r=(24-a->timer)*5;for(int j=0;j<4;j++)for(int i=0;i<r;i+=12){int x=a->bx+(j&1?i:-i),z=a->by+(j&2?r-i:i-r);if(x>=16&&x<=304&&z>=40&&z<=208)quad42(v,(V42){x-2,1,z-2},(V42){x+2,1,z-2},(V42){x+2,1,z+2},(V42){x-2,1,z+2},0x60e0ff);}}
 for(int i=1;i<v->n;i++){T42 t=v->t[i];int j=i;while(j&&v->t[j-1].depth>t.depth){v->t[j]=v->t[j-1];j--;}v->t[j]=t;}
 for(int i=0;i<v->n;i++)tri(v->t[i].p[0],v->t[i].p[1],v->t[i].p[2],v->t[i].c);
 rect(0,0,320,31,0x30251e);for(int i=0;i<5;i++)rect(16+58*i,6,50,6,a->wins&(1<<i)?0x66d070:i==a->id?0x40caff:0x60554a);
 for(int i=0;i<4;i++)rect(16+18*i,18,14,8,i<a->hp?0x5050e0:0x433b33);int hp=a->id==2?a->ripto.hp:a->bhp;for(int i=0;i<7;i++)rect(174+18*i,18,14,8,i<hp?0x60b0e0:0x433b33);
 if(a->id==2){for(int i=0;i<3;i++)rect(102+12*i,18,8,8,i<a->ripto.shield?0xffd080:0x433b33);for(int i=0;i<3;i++)rect(102+12*i,27,8,3,i<a->ripto.cleared?0x66d070:i==a->ripto.phase-1?0x40caff:0x60554a);}
 rect(0,220,320,20,0x30251e);rect(16,225,25,9,a->breath==FIRE40?0x3080ff:a->breath==ICE40?0xffd080:0x60ffff);rect(50,225,120,9,0x60554a);if(a->timer>0)rect(50,225,clamp41(a->timer*2,1,120),9,a->state==A41_OPEN?0x60d080:0x4050e0);if(a->state>=A41_WIN)rect(185,225,119,9,a->state==A41_WIN?0x66d070:0x4050e0);
}
#endif
