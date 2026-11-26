#include "../src/cache18.c"
#include "../src/tex19.h"
int validate19(const U8*i,U32 n,U32 s){return texindex19(i,n,s);}
int block19(const U8*p,const U8*e){return texblock19(p,e);}
void init19(Tex19*t){texinit19(t);}
void refreshhost19(Tex19*t,const U8*i,const U32*f,Read18 r,void*rc,Upload19 u,void*uc){U8 buf[6144];texrefresh19(t,i,f,r,rc,u,uc,buf);}
void slot19(int s,U32*out){out[0]=texx19(s);out[1]=texy19(s);out[2]=texclut19(s);out[3]=texpage19(s);out[4]=texwindow19(s);}
int axis19(int a,int b,int c,int*out){return uvaxis19(a,b,c,out);}

/* Exercise the same edge and axis decisions for every original triangle. */
int split19(const int*u,const int*v,int depth,int*maxdepth){int q[3];if(depth>*maxdepth)*maxdepth=depth;if(uvaxis19(u[0],u[1],u[2],q)&&uvaxis19(v[0],v[1],v[2],q))return 1;if(depth>=12)return -1;int a=uvedge19(u,v),b=(a+1)%3,c=(a+2)%3,mu=(u[a]+u[b])/2,mv=(v[a]+v[b])/2;int u0[3]={u[a],mu,u[c]},v0[3]={v[a],mv,v[c]},u1[3]={mu,u[b],u[c]},v1[3]={mv,v[b],v[c]};int x=split19(u0,v0,depth+1,maxdepth),y=split19(u1,v1,depth+1,maxdepth);return x<0||y<0?-1:x+y;}
