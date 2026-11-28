#ifndef VOLUME78_H
#define VOLUME78_H
#include "session72.h"
/* Trusted virtual volume descriptor; CRC covers entire padded EXE. */
typedef struct {U72 base,sectors,crc;const char *boot;} Volume78;
typedef int (*Read78)(void*,U72,B72*);
typedef struct {Read78 read;void*ctx;U72 disc_sectors;} Disc78;
typedef struct {U72 lba,bytes;} Extent78;
static U72 be78(const B72*p){return (U72)p[0]<<24|(U72)p[1]<<16|(U72)p[2]<<8|p[3];}
static int dual78(const B72*p,U72*out){*out=le72(p);return *out==be78(p+4);}
static int bounded78(U72 lba,U72 bytes,U72 sectors){return bytes&&lba<sectors&&1+(bytes-1)/2048<=sectors-lba;}
static int vr78(const Disc78*d,const Volume78*v,U72 lba,B72*p){return lba<v->sectors&&d->read(d->ctx,v->base+lba,p);}
static int ident78(const B72*p,const char*s,U72 n){for(U72 i=0;i<n;i++)if(p[i]!=(B72)s[i])return 0;return 1;}
static U72 crcpart78(U72 c,const B72*p,U72 n){while(n--){c^=*p++;for(unsigned i=0;i<8;i++)c=(c>>1)^(0xedb88320u&-(c&1u));}return c;}
static int probe78(const Disc78*d,const Volume78*v,B72*p,Extent78*out){
 if(!d||!v||!p||!out||!d->read||!v->boot||v->sectors<18||v->base>=d->disc_sectors||v->sectors>d->disc_sectors-v->base||d->disc_sectors>449850u)return 0;
 U72 name=0;while(name<32&&v->boot[name])name++;if(!name||name==32)return 0;
 U72 root,size,vol;if(!vr78(d,v,16,p)||p[0]!=1||!ident78(p+1,"CD001",5)||p[6]!=1||!dual78(p+80,&vol)||vol!=v->sectors||p[128]!=0||p[129]!=8||p[130]!=8||p[131]!=0)return 0;
 if(p[156]<34||p[157]||p[181]!=2||p[182]||p[183]||!dual78(p+158,&root)||!dual78(p+166,&size)||!bounded78(root,size,vol)||size>64*2048u)return 0;
 Extent78 e={0,0};U72 found=0;
 for(U72 pos=0;pos<size;pos+=2048){if(!vr78(d,v,root+pos/2048,p))return 0;U72 limit=size-pos<2048?size-pos:2048;for(U72 i=0;i<limit;){U72 n=p[i];if(!n)break;if(n<34||(n&1u)||n>limit-i)return 0;const B72*r=p+i;U72 len=r[32],lba,bytes;if(!len||len>n-33||r[1]||r[26]||r[27]||(r[25]&0x80)||!dual78(r+2,&lba)||!dual78(r+10,&bytes)||!bounded78(lba,bytes,vol))return 0;
 if(len==name&&ident78(r+33,v->boot,name)){if(r[25]!=0||found++)return 0;e.lba=lba;e.bytes=bytes;}i+=n;}}
 if(found!=1||e.bytes%2048||e.bytes<4096||!vr78(d,v,e.lba,p)||!exe72(p,e.bytes))return 0;
 U72 crc=crcpart78(~0u,p,2048);for(U72 i=1;i<e.bytes/2048;i++){if(!vr78(d,v,e.lba+i,p))return 0;crc=crcpart78(crc,p,2048);}if(~crc!=v->crc)return 0;*out=e;return 1;
}
#endif
