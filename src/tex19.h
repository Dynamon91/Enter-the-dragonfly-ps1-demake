/* 64 opaque 64x64 8-bit slots. No eviction while a frame is submitted.
 * Four 128-word pages at x=320..831,y=256; CLUTs x=768,y=16..79. */
#define TEXCAP19 64
#define GROUPCAP19 540
#define TEXCOUNT19 141
#define TEXIDX19 (12+TEXCOUNT19*12)
static U32 texcrc19(const U8*p,U32 n){U32 c=~0u;while(n--){c^=*p++;for(int i=0;i<8;i++)c=(c>>1)^(0xedb88320u&-(c&1));}return ~c;}
static int texindex19(const U8*p,U32 len,U32 sectors){if(len!=TEXIDX19||sectors!=TEXCOUNT19*3||rd18(p)!=0x49545445u||s18(p+4)!=1||s18(p+6)!=12||rd18(p+8)!=TEXCOUNT19)return 0;int last=-1;for(int i=0;i<TEXCOUNT19;i++){const U8*e=p+12+12*i;U32 g=rd18(e);if(g>=GROUPCAP19||(int)g<=last||rd18(e+4)!=(U32)(i*3))return 0;last=g;}return 1;}
static int texblock19(const U8*p,const U8*e){return rd18(p)==0x54445445u&&s18(p+4)==1&&(U32)s18(p+6)==rd18(e)&&rd18(p+8)>0&&rd18(p+8)<=1024&&rd18(p+12)>0&&rd18(p+12)<=1024&&rd18(p+16)==4608&&rd18(p+20)==rd18(e+8)&&texcrc19(p+24,4608)==rd18(e+8);}
static unsigned texpage19(int slot){return (5+2*(slot/16))|16|128;}
static unsigned texclut19(int slot){return 48|((16+slot)<<6);}
static unsigned texwindow19(int slot){return 0xe2000000u|24|(24<<5)|((slot%4*8)<<10)|((slot/4%4*8)<<15);}
static int texx19(int slot){return 320+128*(slot/16)+32*(slot%4);}
static int texy19(int slot){return 256+64*(slot/4%4);}
/* Normalize all three UVs together, preserving interpolation across repeated tiles. */
static int uvaxis19(int a,int b,int c,int*out){int lo=a<b?a:b;if(c<lo)lo=c;int hi=a>b?a:b;if(c>hi)hi=c;int base=(lo>>10)*1024;if(hi-base>=4096)return 0;out[0]=(a-base)>>4;out[1]=(b-base)>>4;out[2]=(c-base)>>4;return 1;}
/* Pick the longest UV edge; midpoint subdivision preserves repeated texture phase. */
static int uvedge19(const int*u,const int*v){int edge=0,best=-1;for(int i=0;i<3;i++){int j=(i+1)%3,x=u[i]-u[j],y=v[i]-v[j];int n=(x<0?-x:x)+(y<0?-y:y);if(n>best){best=n;edge=i;}}return edge;}
typedef struct {int slots[TEXCAP19],map[GROUPCAP19],reads,failed,missing;} Tex19;
static void texinit19(Tex19*t){for(int i=0;i<TEXCAP19;i++)t->slots[i]=-1;for(int i=0;i<GROUPCAP19;i++)t->map[i]=-1;t->reads=t->failed=t->missing=0;}
typedef void (*Upload19)(void*,int,const U8*);
/* Deterministic highest-use selection; preserve slots of retained groups. A failed read
 * cannot change a slot's valid tag or overwrite VRAM. Unavailable groups use flat color. */
static void texrefresh19(Tex19*t,const U8*idx,const U32*freq,Read18 read,void*rc,Upload19 upload,void*uc,U8*buf){
 U8 keep[GROUPCAP19];for(int g=0;g<GROUPCAP19;g++)keep[g]=0;t->missing=0;
 for(int k=0;k<TEXCAP19;k++){int best=-1;U32 n=0;for(int i=0;i<TEXCOUNT19;i++){int g=rd18(idx+12+12*i);if(!keep[g]&&freq[g]>n){best=g;n=freq[g];}}if(best<0)break;keep[best]=1;}
 for(int i=0;i<TEXCOUNT19;i++){const U8*e=idx+12+12*i;int g=rd18(e);if(!keep[g]||t->map[g]>=0)continue;int s=-1;for(int k=0;k<TEXCAP19;k++)if(t->slots[k]<0||!keep[t->slots[k]]){s=k;break;}if(s<0)continue;t->reads++;
  if(!read(rc,rd18(e+4),3,buf)||!texblock19(buf,e)){t->failed++;break;}upload(uc,s,buf+24);if(t->slots[s]>=0)t->map[t->slots[s]]=-1;t->slots[s]=g;t->map[g]=s;
 }
 for(int g=0;g<GROUPCAP19;g++)if(freq[g]&&t->map[g]<0)t->missing++;
}
