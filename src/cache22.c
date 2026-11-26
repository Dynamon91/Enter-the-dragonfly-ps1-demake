/* Compact double-arena cache. Current arena is immutable until all new blocks validate. */
typedef unsigned char U8;typedef unsigned int U32;typedef unsigned short U16;
typedef int (*Read18)(void*,U32,U32,U8*);
extern int sector16_load(const U8*,U32,U32,U32,U32,U32,U32,U8*,U32,Read18,void*,U32*);
#define CAP18 16
#define SLOTS18 (CAP18*2)
#define RADIUS18 1536
#define ANCHOR18 512
#define NONE18 32767
#define BLOCKS18 174
#define MAT18 208
#define CACHE_BYTES18 65536
#define ARENA22 (536*1024)
static U32 rd18(const U8*p){return (U32)p[0]|(U32)p[1]<<8|(U32)p[2]<<16|(U32)p[3]<<24;}
static int s18(const U8*p){return (short)(p[0]|p[1]<<8);}
static int abs18(int x){return x<0?-x:x;}
static int anchor18(int x){return (x>=0?x/ANCHOR18:-((-x+ANCHOR18-1)/ANCHOR18))*ANCHOR18+ANCHOR18/2;}
typedef struct {U32 arena[2][ARENA22/4];U8 *bytes[SLOTS18];U32 meta[SLOTS18][7];int ids[SLOTS18],active[CAP18],count,ax,az,reads;int bank;U32 used_bytes,copied_bytes;} Cache18;
void cache18_init(Cache18*c){c->count=0;c->ax=c->az=0;c->reads=0;c->bank=0;c->used_bytes=c->copied_bytes=0;for(int i=0;i<SLOTS18;i++){c->ids[i]=-1;c->bytes[i]=0;}}
int cache18_select(const U8*idx,U32 len,int x,int z,int*out){if(!idx||!out||len!=16+BLOCKS18*60||rd18(idx)!=0x49445445u||rd18(idx+8)!=BLOCKS18||rd18(idx+12)!=4096||x<-200000||x>200000||z<-200000||z>200000)return -1;int ax=anchor18(x),az=anchor18(z),n=0;for(int i=0;i<BLOCKS18;i++){const U8*e=idx+16+i*60;if((int)rd18(e+28)>ax+RADIUS18||(int)rd18(e+40)<ax-RADIUS18||(int)rd18(e+36)>az+RADIUS18||(int)rd18(e+48)<az-RADIUS18)continue;if(n==CAP18)return -1;out[n++]=i;}return n;}
/* All sizes are rounded to CD sectors; pointer alignment allows word copies. */
static U32 blocksize22(const U8*idx,int id){U32 n=rd18(idx+16+id*60+8);return n>=64&&n<=CACHE_BYTES18?(n+2047)&~2047u:0;}
int cache18_update(Cache18*c,const U8*idx,U32 len,U32 sectors,int x,int z,Read18 read,void*ctx){
 if(x<-200000||x>200000||z<-200000||z>200000)return 0;
 int ax=anchor18(x),az=anchor18(z);if(c->count&&c->ax==ax&&c->az==az)return 1;
 int ids[CAP18],n=cache18_select(idx,len,x,z,ids);if(n<=0)return 0;
 int same=n==c->count;U32 sizes[CAP18],total=0;
 for(int j=0;j<n;j++){if(!same||ids[j]!=c->ids[c->active[j]])same=0;sizes[j]=blocksize22(idx,ids[j]);if(!sizes[j]||sizes[j]>ARENA22-total)return 0;total+=sizes[j];}
 if(same){c->ax=ax;c->az=az;return 1;}
 int bank=c->bank^1;U32 offset=0,copied=0;
 for(int j=0;j<n;j++){int k=bank*CAP18+j,old=-1;U8*dst=(U8*)c->arena[bank]+offset;
  for(int i=0;i<c->count;i++)if(c->ids[c->active[i]]==ids[j]){old=c->active[i];break;}
  c->ids[k]=-1;c->bytes[k]=dst;
  if(old>=0){const U32*src=(const U32*)c->bytes[old];U32*d=(U32*)dst;for(U32 i=0;i<sizes[j]/4;i++)d[i]=src[i];for(int i=0;i<7;i++)c->meta[k][i]=c->meta[old][i];copied+=sizes[j];}
  else{c->reads++;if(!sector16_load(idx,len,ids[j],sectors,MAT18,75653,6195,dst,sizes[j],read,ctx,c->meta[k]))return 0;}
  c->ids[k]=ids[j];offset+=sizes[j];
 }
 for(int j=0;j<n;j++)c->active[j]=bank*CAP18+j;c->bank=bank;c->count=n;c->ax=ax;c->az=az;c->used_bytes=total;c->copied_bytes+=copied;return 1;
}
/* Signed 64-bit quotient with bounded world-height result, no runtime division helper. */
static int ratio18(long long a,long long b){int neg=(a<0)!=(b<0);unsigned long long n=a<0?-a:a,d=b<0?-b:b;unsigned q=0;if(!d)return 0;for(int i=15;i>=0;i--)if(n>=(d<<i)){n-=d<<i;q|=1u<<i;}return neg?-(int)q:(int)q;}
static long long cross18(int ax,int az,int bx,int bz){return (long long)ax*bz-(long long)az*bx;}
/* Source collision candidates, not the original BSP: select the nearest reasonably horizontal surface. */
int cache18_floor(const Cache18*c,int x,int z,int ref,int limit){int best=NONE18,dist=limit+1;for(int j=0;j<c->count;j++){int k=c->active[j];const U32*m=c->meta[k];const U8*p=c->bytes[k]+64+36*m[1];int qx=x-(int)m[4],qz=z-(int)m[6];for(U32 i=0;i<m[2];i++,p+=24){int ax=s18(p),ay=s18(p+2)+(int)m[5],az=s18(p+4),bx=s18(p+6)-ax,by=s18(p+8)+(int)m[5]-ay,bz=s18(p+10)-az,cx=s18(p+12)-ax,cy=s18(p+14)+(int)m[5]-ay,cz=s18(p+16)-az;long long d=cross18(bx,bz,cx,cz);if(!d)continue;long long nx=cross18(by,bz,cy,cz),nz=cross18(bx,by,cx,cy);long long ad=d<0?-d:d;if((nx<0?-nx:nx)>ad*2||(nz<0?-nz:nz)>ad*2)continue;long long u=cross18(qx-ax,qz-az,cx,cz),v=cross18(bx,bz,qx-ax,qz-az);if(d<0){u=-u;v=-v;d=-d;}if(u<0||v<0||u+v>d)continue;int y=ay+ratio18(u*by+v*cy,d),dd=abs18(y-ref);if(dd<dist){dist=dd;best=y;}}}return best;}
