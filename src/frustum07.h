/* Camera-space clipping. Fixed-point interpolation, no float or 64-bit arithmetic.
 * Polygon capacity: 3 input vertices + at most one per each of five planes.
 * A triangle clipped to a convex frustum yields <= 6 triangles. */
#define CLIP_CAP 16
#define CLIP_NEAR 128
#define CLIP_H 220
/* Screen center (160,120), clip to an extra 1-pixel guard at right/bottom. */
static int clipdist(Point p,int plane){
 switch(plane){case 0:return p.z-CLIP_NEAR;case 1:return CLIP_H*p.x+160*p.z;case 2:return 160*p.z-CLIP_H*p.x;case 3:return CLIP_H*p.y+120*p.z;default:return 120*p.z-CLIP_H*p.y;}
}
static unsigned clipmask(Point p){unsigned m=0;for(int i=0;i<5;i++)if(clipdist(p,i)<0)m|=1u<<i;return m;}
static int cliplerp(int a,int b,int f){return a+(b-a)*f/4096;}
static Point clipcross(Point a,Point b,int da,int db,int plane){
 /* Always start from the inside endpoint; this makes shared-edge results deterministic. */
 if(da<0){Point q=a;a=b;b=q;int d=da;da=db;db=d;}
 int den=da-db;while(da>524287||den>524287){da>>=1;den>>=1;}
 int f=den?da*4096/den:0;Point p={0};p.x=cliplerp(a.x,b.x,f);p.y=cliplerp(a.y,b.y,f);p.z=cliplerp(a.z,b.z,f);p.u=cliplerp(a.u,b.u,f);p.v=cliplerp(a.v,b.v,f);
 if(plane==0)p.z=CLIP_NEAR;
 return p;
}
static int cliptriangle(Point a,Point b,Point c,Point*out){
 unsigned ma=clipmask(a),mb=clipmask(b),mc=clipmask(c);if(ma&mb&mc)return 0;
 out[0]=a;out[1]=b;out[2]=c;unsigned mask=ma|mb|mc;if(!mask)return 3;
 Point tmp[CLIP_CAP];int n=3;
 for(int plane=0;plane<5;plane++)if(mask&(1u<<plane)){
  int k=0;for(int j=0;j<n;j++){Point p=out[j],q=out[(j+1)%n];int da=clipdist(p,plane),db=clipdist(q,plane);if(da>=0){if(k==CLIP_CAP)return 0;tmp[k++]=p;}if((da<0)!=(db<0)){if(k==CLIP_CAP)return 0;tmp[k++]=clipcross(p,q,da,db,plane);}}
  n=k;if(n<3)return 0;for(int j=0;j<n;j++)out[j]=tmp[j];
 }
 return n<=8?n:0;
}
