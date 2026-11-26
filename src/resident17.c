/* Two-slot transactional residency; no overwriting currently visible data. */
typedef unsigned char U8;typedef unsigned int U32;
typedef int (*Read17)(void*,U32,U32,U8*);
extern int sector16_load(const U8*,U32,U32,U32,U32,U32,U32,U8*,U32,Read17,void*,U32*);
static U32 r32(const U8*p){return (U32)p[0]|((U32)p[1]<<8)|((U32)p[2]<<16)|((U32)p[3]<<24);}
static U32 be32(const U8*p){return (U32)p[3]|((U32)p[2]<<8)|((U32)p[1]<<16)|((U32)p[0]<<24);}
static int eq(const U8*p,const char*s,U32 n){for(U32 i=0;i<n;i++)if(!s[i]||p[i]!=(U8)s[i])return 0;return !s[n];}
/* This authored disc has a single-sector root directory. Reject unsupported layouts. */
int iso17_find(const U8*p,const char*name,U32 volume,U32*out){for(U32 i=0;i<2048&&p[i];){U32 n=p[i];if(n<34||n>2048-i||p[i+32]>n-33)return 0;U32 a=r32(p+i+2),b=r32(p+i+10);if(!(p[i+25]&0x82)&&eq(p+i+33,name,p[i+32])){if(a!=be32(p+i+6)||b!=be32(p+i+14)||!b||a>=volume||((b-1)/2048+1)>volume-a)return 0;out[0]=a;out[1]=b;return 1;}i+=n;}return 0;}
int iso17_pvd(const U8*p,U32*out){if(p[0]!=1||!eq(p+1,"CD001",5)||p[6]!=1||p[128]!=0||p[129]!=8||p[130]!=8||p[131]!=0)return 0;U32 v=r32(p+80),root=r32(p+158);if(v!=be32(p+84)||v<22||root>=v||root!=be32(p+162)||r32(p+166)!=2048||be32(p+170)!=2048||p[156]<34)return 0;out[0]=v;out[1]=root;return 1;}
typedef struct {U8 slots[2][65536];U32 meta[7];int active;} Resident17;
void resident17_init(Resident17*r){r->active=-1;}
int resident17_switch(Resident17*r,const U8*idx,U32 len,U32 id,U32 sectors,Read17 read,void*ctx){int next=r->active==0?1:0;U32 tmp[7];if(!sector16_load(idx,len,id,sectors,208,75653,6195,r->slots[next],65536,read,ctx,tmp))return 0;for(int i=0;i<7;i++)r->meta[i]=tmp[i];r->active=next;return 1;}
