#ifndef SPU49_H
#define SPU49_H
/* Resident bank: offset is absolute SPU byte address, never a CPU pointer. */
#define SPU49_BASE 0x1000u
#define SPU49_LIMIT 0x70000u
#define SPU49_MAX 512u
typedef struct {unsigned address,bytes,pitch,frames,loop;} Sample49;
static int valid_sample49(const Sample49*s,unsigned bank_bytes){
 if(!s||bank_bytes>SPU49_LIMIT-SPU49_BASE||s->address<SPU49_BASE||s->address%16||s->bytes<16||s->bytes%16||s->pitch<743||s->pitch>4096||!s->frames)return 0;
 unsigned off=s->address-SPU49_BASE;if(off>bank_bytes||s->bytes>bank_bytes-off)return 0;
 if(s->frames>(s->bytes/16)*28)return 0;
 unsigned blocks=(s->frames+27)/28;
 if(s->loop==0xffffffffu)return s->bytes==(blocks+1)*16;
 return s->loop<s->frames&&s->loop%28==0&&s->frames%28==0&&s->bytes==blocks*16;
}
/* Strict contiguous layout; validate all sample flags and dummy data before upload. */
static int valid_bank49(const unsigned char*b,unsigned n,const Sample49*s,unsigned count){
 if(!b||!s||!count||count>SPU49_MAX||!n||n%64||n>SPU49_LIMIT-SPU49_BASE)return 0;
 unsigned addr=SPU49_BASE;
 for(unsigned i=0;i<count;i++){
  if(!valid_sample49(s+i,n)||s[i].address!=addr)return 0;
  unsigned blocks=(s[i].frames+27)/28;const unsigned char*p=b+addr-SPU49_BASE;
  for(unsigned j=0;j<blocks;j++,p+=16){unsigned f=0,loop=s[i].loop;
   if(loop!=0xffffffffu&&j*28>=loop)f=2u|(j*28==loop?4u:0u)|(j+1==blocks?1u:0u);else if(j+1==blocks)f=1;
   if((p[0]>>4)>4||(p[0]&15)>12||p[1]!=f||((j==0||j*28==loop)&&(p[0]>>4)))return 0;
  }
  if(s[i].loop==0xffffffffu){if(p[0]||p[1]!=7)return 0;for(unsigned j=2;j<16;j++)if(p[j])return 0;}
  addr+=s[i].bytes;
 }
 for(unsigned i=addr-SPU49_BASE;i<n;i++)if(b[i])return 0;
 return 1;
}
#endif
