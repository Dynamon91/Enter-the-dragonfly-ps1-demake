/* Polled PS1 CD controller, 2048-byte Mode 2 Form 1 reads. No BIOS IRQ dependency.
 * Fail closed on transport error: no further commands until reset/reboot. */
typedef unsigned char U8; typedef unsigned int U32;
#ifdef CD17_MOCK
extern U8 cd17_in(unsigned reg);extern void cd17_out(unsigned reg,U8 value);
#define IN(r) cd17_in(r)
#define OUT(r,v) cd17_out(r,v)
#define LIMIT 1000u
#else
#define IN(r) (*(volatile U8*)(0xbf801800u+(r)))
#define OUT(r,v) (*(volatile U8*)(0xbf801800u+(r))=(U8)(v))
#define LIMIT 8000000u
#endif
static int fault;
static int waitbit(U8 mask,int set){for(U32 i=0;i<LIMIT;i++)if(!!(IN(0)&mask)==set)return 1;return 0;}
static void ack(void){OUT(0,1);OUT(3,0x1f);OUT(0,0);}
static int event(void){OUT(0,1);for(U32 i=0;i<LIMIT;i++){int t=IN(3)&7;if(t){OUT(0,0);for(int j=0;j<16&&(IN(0)&0x20);j++)(void)IN(1);return t;}}OUT(0,0);return 0;}
static int command(U8 cmd,const U8*p,unsigned n){OUT(0,0);if(!waitbit(0x80,0))return 0;for(unsigned i=0;i<n;i++){if(!waitbit(0x10,1))return 0;OUT(2,p[i]);}OUT(1,cmd);return 1;}
static int expect(int t){int got=event();if(got)ack();return got==t;}
static U8 bcd(U32 n){return (U8)(((n/10)<<4)|(n%10));}
int cd17_init(void){fault=1;OUT(0,0);OUT(3,0);OUT(0,1);OUT(2,0);OUT(3,0x5f);OUT(0,0);for(int j=0;j<16&&(IN(0)&0x20);j++)(void)IN(1);U8 mode=0x80;/* double speed, 2048-byte sectors */
 if(!command(0x0e,&mode,1)||!expect(3))return 0;fault=0;return 1;}
int cd17_read(void*unused,U32 lba,U32 n,U8*dst){(void)unused;if(fault||!dst||!n||n>32||lba>=449850u||n>449850u-lba)return 0;U32 t=lba+150;U8 loc[3]={bcd(t/4500),bcd(t/75%60),bcd(t%75)};
 if(!command(2,loc,3)||!expect(3)||!command(6,0,0)||!expect(3))goto fail;
 for(U32 s=0;s<n;s++){int e=event();if(e!=1){if(e)ack();goto fail;}OUT(0,0);OUT(3,0);OUT(3,0x80);if(!waitbit(0x40,1)){ack();goto fail;}for(int j=0;j<2048;j++)*dst++=IN(2);OUT(3,0);ack();}
 /* Pause can race with the next DataReady; discard extra notifications before ACK. */
 if(!command(9,0,0))goto fail;int phase=0;for(int k=0;k<8;k++){int e=event();if(!e)goto fail;ack();if(e==3&&!phase)phase=1;else if(e==2&&phase)return 1;else if(e!=1)goto fail;}
 fail:OUT(0,0);OUT(3,0);fault=1;return 0;
}
