/* Register/FIFO contract mock, not an SPU emulator. */
#include <string.h>
typedef unsigned short u16;
static u16 regs[256],ram[0x80000/2],fifo[32];static int cursor,n,fail,kon,kof,writes,overflow;
static void write_reg(int o,u16 v){regs[o/2]=v;if(o==0x1a6){cursor=v*4;n=0;}if(o==0x1a8){if(n<32)fifo[n++]=v;else overflow++;}if(o==0x1aa&&(v&0x30)==0x10){if(cursor+n<=0x80000/2){memcpy(ram+cursor,fifo,n*2);writes+=n;cursor+=n;n=0;}else overflow++;}if(o==0x188)kon++;if(o==0x18c)kof++;}
static u16 read_reg(int o){if(o==0x1ae)return fail?0x3f:regs[0x1aa/2]&0x3f;return regs[o/2];}
#define SPU_WRITE(o,v) write_reg(o,v)
#define SPU_READ(o) read_reg(o)
#define SPU_DELAY() ((void)0)
#define SPU_POLL_LIMIT 32
#include "spu13.h"
int mock_init13(int fault){memset(regs,0,sizeof(regs));memset(ram,0,sizeof(ram));cursor=n=kon=kof=writes=overflow=0;fail=fault;return sfx_init();}
void mock_play13(int sample){sfx_play(sample);}
void mock_stop13(void){sfx_stop();}
int mock_reg13(int o){return regs[o/2];}
int mock_info13(int i){int a[]={kon,kof,writes,overflow,sfx_ready};return a[i];}
void mock_bank13(void*out){memcpy(out,(char*)ram+SFX_BANK_ADDR,SFX_BANK_BYTES);}
