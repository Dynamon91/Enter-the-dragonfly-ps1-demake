/* Cooperative lookahead: active arena stays immutable until a complete validated plan commits. */
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
/* Shared sector arena. A slot is live if size != 0. Active slots are pinned;
 * a pending plan references retained slots directly and reserves space for new blocks.
 * In-place compaction is only a fallback for fragmentation, never for every transition. */
#define POOL24 (ARENA22*2u)
#define PAGE24 2048u
#define PAGES24 (POOL24/PAGE24)
typedef struct {U32 arena[POOL24/4];U8 *bytes[SLOTS18];U32 meta[SLOTS18][7];int ids[SLOTS18],active[CAP18],count,ax,az,reads;U32 used_bytes,copied_bytes; int plan_valid,plan_ax,plan_az,plan_count,plan_done; int plan_ids[CAP18],plan_slots[CAP18]; U32 sizes[SLOTS18],plan_total; U32 ticks,commits,cancels,failures,compactions;} Cache18;
void cache18_init(Cache18*c){c->plan_valid=0;c->ticks=c->commits=c->cancels=c->failures=c->compactions=0;c->count=0;c->ax=c->az=0;c->reads=0;c->used_bytes=c->copied_bytes=0;for(int i=0;i<SLOTS18;i++){c->ids[i]=-1;c->bytes[i]=0;c->sizes[i]=0;}}
int cache18_select(const U8*idx,U32 len,int x,int z,int*out){if(!idx||!out||len!=16+BLOCKS18*60||rd18(idx)!=0x49445445u||rd18(idx+8)!=BLOCKS18||rd18(idx+12)!=4096||x<-200000||x>200000||z<-200000||z>200000)return -1;int ax=anchor18(x),az=anchor18(z),n=0;for(int i=0;i<BLOCKS18;i++){const U8*e=idx+16+i*60;if((int)rd18(e+28)>ax+RADIUS18||(int)rd18(e+40)<ax-RADIUS18||(int)rd18(e+36)>az+RADIUS18||(int)rd18(e+48)<az-RADIUS18)continue;if(n==CAP18)return -1;out[n++]=i;}return n;}
static U32 blocksize22(const U8*idx,int id){U32 n=rd18(idx+16+id*60+8);return n>=64&&n<=CACHE_BYTES18?(n+2047)&~2047u:0;}
static int pinned24(const Cache18*c,int k){for(int i=0;i<c->count;i++)if(c->active[i]==k)return 1;return 0;}
static void discard24(Cache18*c){for(int k=0;k<SLOTS18;k++)if(!pinned24(c,k)){c->sizes[k]=0;c->bytes[k]=0;c->ids[k]=-1;}}
void cache23_cancel(Cache18*c){if(c->plan_valid)c->cancels++;c->plan_valid=0;discard24(c);}
static U8* alloc24(Cache18*c,U32 n){U8 busy[PAGES24];U8*base=(U8*)c->arena;for(U32 i=0;i<PAGES24;i++)busy[i]=0;
 for(int k=0;k<SLOTS18;k++)if(c->sizes[k]){U32 a=(U32)(c->bytes[k]-base)/PAGE24,b=a+c->sizes[k]/PAGE24;for(U32 i=a;i<b;i++)busy[i]=1;}
 U32 run=0;for(U32 i=0;i<PAGES24;i++){run=busy[i]?0:run+1;if(run==n/PAGE24)return base+(i+1-run)*PAGE24;}return 0;}
/* Pack active extents down in address order. Forward copy is overlap-safe because
 * every destination starts at or below its source. Update all slot pointers. */
static void compact24(Cache18*c){U8*base=(U8*)c->arena;U32 off=0;int order[CAP18];for(int i=0;i<c->count;i++){int k=c->active[i],j=i;while(j&&c->bytes[order[j-1]]>c->bytes[k]){order[j]=order[j-1];j--;}order[j]=k;}
 for(int i=0;i<c->count;i++){int k=order[i];U8*dst=base+off;if(dst!=c->bytes[k]){U32*d=(U32*)dst;const U32*s=(const U32*)c->bytes[k];for(U32 j=0;j<c->sizes[k]/4;j++)d[j]=s[j];c->copied_bytes+=c->sizes[k];c->bytes[k]=dst;}off+=c->sizes[k];}c->compactions++;}
static int reserve24(Cache18*c,const U8*idx,int n){for(int j=0;j<n;j++){int id=c->plan_ids[j],k=-1;for(int i=0;i<c->count;i++)if(c->ids[c->active[i]]==id){k=c->active[i];break;}if(k<0){for(int i=0;i<SLOTS18;i++)if(!c->sizes[i]){k=i;break;}if(k<0)return 0;U32 size=blocksize22(idx,id);U8*p=alloc24(c,size);if(!p)return 0;c->bytes[k]=p;c->sizes[k]=size;c->ids[k]=-1;}c->plan_slots[j]=k;}return 1;}
static void advance24(Cache18*c){while(c->plan_done<c->plan_count&&c->ids[c->plan_slots[c->plan_done]]==c->plan_ids[c->plan_done])c->plan_done++;}
int cache23_begin(Cache18*c,const U8*idx,U32 len,int x,int z){if(x<-200000||x>200000||z<-200000||z>200000)return 0;int ax=anchor18(x),az=anchor18(z);if(c->plan_valid&&c->plan_ax==ax&&c->plan_az==az)return 1;cache23_cancel(c);int n=cache18_select(idx,len,x,z,c->plan_ids);if(n<=0)return 0;U32 total=0;for(int j=0;j<n;j++){U32 s=blocksize22(idx,c->plan_ids[j]);if(!s||s>ARENA22-total)return 0;total+=s;}if(!reserve24(c,idx,n)){discard24(c);compact24(c);if(!reserve24(c,idx,n)){discard24(c);return 0;}}c->plan_ax=ax;c->plan_az=az;c->plan_count=n;c->plan_done=0;c->plan_total=total;c->plan_valid=1;advance24(c);return 1;}
int cache23_tick(Cache18*c,const U8*idx,U32 len,U32 sectors,Read18 read,void*ctx){if(!c->plan_valid)return -1;if(c->plan_done==c->plan_count)return 1;int j=c->plan_done,k=c->plan_slots[j],id=c->plan_ids[j];c->ticks++;c->reads++;if(!sector16_load(idx,len,id,sectors,MAT18,75653,6195,c->bytes[k],c->sizes[k],read,ctx,c->meta[k])){c->failures++;cache23_cancel(c);return -1;}c->ids[k]=id;advance24(c);return c->plan_done==c->plan_count;}
int cache23_commit(Cache18*c,int x,int z){if(!c->plan_valid||c->plan_ax!=anchor18(x)||c->plan_az!=anchor18(z)||c->plan_done!=c->plan_count)return 0;for(int j=0;j<c->plan_count;j++)c->active[j]=c->plan_slots[j];c->count=c->plan_count;c->used_bytes=c->plan_total;c->ax=c->plan_ax;c->az=c->plan_az;c->plan_valid=0;discard24(c);c->commits++;return 1;}
/* Blocking startup/reset path, shares the same validation and commit logic. */
int cache18_update(Cache18*c,const U8*idx,U32 len,U32 sectors,int x,int z,Read18 read,void*ctx){
 if(x<-200000||x>200000||z<-200000||z>200000)return 0;
 if(c->count&&c->ax==anchor18(x)&&c->az==anchor18(z)){cache23_cancel(c);return 1;}
 if(!cache23_begin(c,idx,len,x,z))return 0;
 int r;do{r=cache23_tick(c,idx,len,sectors,read,ctx);}while(r==0);
 return r>0&&cache23_commit(c,x,z);
}
/* Movement path. Predict 8 frames ahead, but prioritize the actual boundary.
 * Never publish ahead of player crossing; hold position while target is incomplete. */
int cache23_move(Cache18*c,const U8*idx,U32 len,U32 sectors,int x,int z,int nx,int nz,Read18 read,void*ctx){
 int crossing=anchor18(nx)!=c->ax||anchor18(nz)!=c->az;
 int tx=crossing?nx:x+8*(nx-x),tz=crossing?nz:z+8*(nz-z);
 if(anchor18(tx)==c->ax&&anchor18(tz)==c->az){cache23_cancel(c);return 1;}
 if(!cache23_begin(c,idx,len,tx,tz))return !crossing;
 int r=cache23_tick(c,idx,len,sectors,read,ctx);
 if(!crossing)return 1;
 return r>0&&cache23_commit(c,nx,nz);
}
/* Signed 64-bit quotient with bounded world-height result, no runtime division helper. */
static int ratio18(long long a,long long b){int neg=(a<0)!=(b<0);unsigned long long n=a<0?-a:a,d=b<0?-b:b;unsigned q=0;if(!d)return 0;for(int i=15;i>=0;i--)if(n>=(d<<i)){n-=d<<i;q|=1u<<i;}return neg?-(int)q:(int)q;}
static long long cross18(int ax,int az,int bx,int bz){return (long long)ax*bz-(long long)az*bx;}
/* Source collision candidates, not the original BSP: select the nearest reasonably horizontal surface. */
int cache18_floor(const Cache18*c,int x,int z,int ref,int limit){int best=NONE18,dist=limit+1;for(int j=0;j<c->count;j++){int k=c->active[j];const U32*m=c->meta[k];const U8*p=c->bytes[k]+64+36*m[1];int qx=x-(int)m[4],qz=z-(int)m[6];for(U32 i=0;i<m[2];i++,p+=24){int ax=s18(p),ay=s18(p+2)+(int)m[5],az=s18(p+4),bx=s18(p+6)-ax,by=s18(p+8)+(int)m[5]-ay,bz=s18(p+10)-az,cx=s18(p+12)-ax,cy=s18(p+14)+(int)m[5]-ay,cz=s18(p+16)-az;long long d=cross18(bx,bz,cx,cz);if(!d)continue;long long nx=cross18(by,bz,cy,cz),nz=cross18(bx,by,cx,cy);long long ad=d<0?-d:d;if((nx<0?-nx:nx)>ad*2||(nz<0?-nz:nz)>ad*2)continue;long long u=cross18(qx-ax,qz-az,cx,cz),v=cross18(bx,bz,qx-ax,qz-az);if(d<0){u=-u;v=-v;d=-d;}if(u<0||v<0||u+v>d)continue;int y=ay+ratio18(u*by+v*cy,d),dd=abs18(y-ref);if(dd<dist){dist=dd;best=y;}}}return best;}
