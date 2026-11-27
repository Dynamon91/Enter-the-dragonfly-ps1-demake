#ifndef SESSION72_H
#define SESSION72_H
/* Session-only state in the region reserved by every original level linker.
 * Each overlay owns its own source-ID arrays; no cross-level ID collisions. */
#define SESSION72_ADDR 0x801ea000u
#define SESSION72_MAGIC 0x45544472u
#define LEVEL72_COUNT 10u
#define SLOT72_SIZE 4096u
#define RETURN72_ADDR 0x801e0010u
#define WORLD72_LOAD 0x80010000u
#define WORLD72_LIMIT 0x801e0000u
typedef unsigned int U72;typedef unsigned char B72;
typedef struct {U72 size,crc,gems,flies;B72 bytes[SLOT72_SIZE];} Slot72;
typedef struct {U72 magic,world,base,sectors,visited;Slot72 slot[LEVEL72_COUNT];} Session72;
#define SESSION72 ((Session72*)SESSION72_ADDR)
static U72 crc72(const B72*p,U72 n){U72 c=~0u;while(n--){c^=*p++;for(int j=0;j<8;j++)c=(c>>1)^(0xedb88320u&-(c&1));}return ~c;}
static void clear72(Session72*s){volatile B72*p=(volatile B72*)s;for(U72 i=0;i<sizeof *s;i++)p[i]=0;s->magic=SESSION72_MAGIC;}
static int valid72(const Slot72*s){return s->size&&s->size<=SLOT72_SIZE&&s->gems<=20000&&s->flies<=90&&(crc72(s->bytes,s->size)^s->gems*0x9e3779b9u^s->flies*0x85ebca6bu^s->size)==s->crc;}
static int save72(Session72*s,U72 w,const B72*p,U72 n,U72 gems,U72 flies){if(s->magic!=SESSION72_MAGIC||w>=LEVEL72_COUNT||!n||n>SLOT72_SIZE||gems>20000||flies>90)return 0;Slot72*d=s->slot+w;d->size=0;for(U72 i=0;i<n;i++)d->bytes[i]=p[i];d->crc=crc72(d->bytes,n)^gems*0x9e3779b9u^flies*0x85ebca6bu^n;d->gems=gems;d->flies=flies;d->size=n;return 1;}
static int load72(const Session72*s,U72 w,B72*p,U72 n){if(s->magic!=SESSION72_MAGIC||w>=LEVEL72_COUNT)return 0;const Slot72*d=s->slot+w;if(d->size!=n||!valid72(d))return 0;for(U72 i=0;i<n;i++)p[i]=d->bytes[i];return 1;}
static U72 total72(const Session72*s,int flies){U72 n=0;for(U72 w=0;w<LEVEL72_COUNT;w++)if(valid72(s->slot+w))n+=flies?s->slot[w].flies:s->slot[w].gems;return n;}
static int translate72(const Session72*s,U72 lba,U72 n,U72*out){if(s->magic!=SESSION72_MAGIC||s->world>=LEVEL72_COUNT||!n||n>32||lba>=s->sectors||n>s->sectors-lba||s->base>=449850u||s->sectors>449850u-s->base)return 0;*out=s->base+lba;return 1;}
/* Verify the PS-X EXE header before overwriting low RAM. All overlays have
 * identical entry/load address and a linker-enforced upper bound. */
static U72 le72(const B72*p){return (U72)p[0]|(U72)p[1]<<8|(U72)p[2]<<16|(U72)p[3]<<24;}
static int exe72(const B72*h,U72 bytes){const char*m="PS-X EXE";for(int i=0;i<8;i++)if(h[i]!=(B72)m[i])return 0;U72 n=le72(h+28);return bytes>=4096&&bytes%2048==0&&le72(h+16)==WORLD72_LOAD&&le72(h+20)==0&&le72(h+24)==WORLD72_LOAD&&n==bytes-2048&&n<=WORLD72_LIMIT-WORLD72_LOAD&&le72(h+0x30)==0x801fff00u;}
#endif
