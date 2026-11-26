/* Conservative cluster AABB rejection in the exact native fixed-point camera space.
 * Corner transform rounding can shift a point by up to two units relative to
 * the affine hull. 1024 plane-distance units bound that error conservatively.
 * No far clipping; no changes to the original triangle ordering. */
static Point camera_space(int x,int y,int z,int cx,int cy,int cz,int sn,int cs){
 x-=cx;y-=cy;z-=cz;int a=(cs*x-sn*z)>>12,b=(sn*x+cs*z)>>12;
 Point p={a,(3849*y-1401*b)>>12,(1401*y+3849*b)>>12,0,0,0};return p;
}
static int cluster_visible(const s16*b,int cx,int cy,int cz,int sn,int cs){
 unsigned all=31;
 for(int k=0;k<8;k++){
  Point p=camera_space(b[(k&1)?3:0],b[(k&2)?4:1],b[(k&4)?5:2],cx,cy,cz,sn,cs);
  unsigned m=0;for(int i=0;i<5;i++)if(clipdist(p,i)<-1024)m|=1u<<i;
  all&=m;if(!all)return 1;
 }
 return 0;
}
