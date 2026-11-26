/* Polled CD diagnostic transport. No simultaneous cd17 access allowed. */
typedef unsigned char U8;
#define CD(r) (*(volatile U8*)(0xbf801800u+(r)))
#define SPU(a) (*(volatile unsigned short*)(0xbf801d00u+(a)))
#define LIMIT 4000000u
static int wait47(unsigned mask,int on){for(unsigned i=0;i<LIMIT;i++)if(!!(CD(0)&mask)==on)return 1;return 0;}
static int event47(U8*r,unsigned*len){CD(0)=1;for(unsigned i=0;i<LIMIT;i++){int e=CD(3)&7;if(e){CD(0)=0;*len=0;for(unsigned j=0;j<16&&(CD(0)&0x20);j++)r[(*len)++]=CD(1);CD(0)=1;CD(3)=0x1f;CD(0)=0;return e;}}CD(0)=0;return 0;}
static int cmd47(U8 cmd,const U8*p,unsigned n,U8*r,unsigned*len){CD(0)=0;if(!wait47(0x80,0))return 0;for(unsigned i=0;i<n;i++){if(!wait47(0x10,1))return 0;CD(2)=p[i];}CD(1)=cmd;for(int i=0;i<32;i++){int e=event47(r,len);if(e==3)return 1;if(e!=1)return 0;}return 0;}
static int simple47(U8 cmd,const U8*p,unsigned n){U8 r[16];unsigned l;return cmd47(cmd,p,n,r,&l)&&l&&!(r[0]&1);}
static U8 bcd47(unsigned x){return (U8)((x/10)*16+x%10);}
static int unbcd47(U8 x){return (x>>4)>9||(x&15)>9?-1:(x>>4)*10+(x&15);}
static void mute47(void){SPU(0xb0)=0;SPU(0xb2)=0;}
int cd_start47(unsigned lba,unsigned file,unsigned channel){unsigned t=lba+150;U8 loc[3]={bcd47(t/4500),bcd47(t/75%60),bcd47(t%75)},filter[2]={(U8)file,(U8)channel},mode=0xc8;
 mute47();CD(0)=0;CD(3)=0;CD(0)=1;CD(2)=0;CD(3)=0x5f;CD(0)=0;
 for(int i=0;i<16&&(CD(0)&0x20);i++)(void)CD(1);
 CD(0)=2;CD(2)=0x80;CD(3)=0;CD(0)=3;CD(1)=0x80;CD(2)=0;CD(3)=0x20;CD(0)=0;
 SPU(0x80)=0x3fff;SPU(0x82)=0x3fff;SPU(0xaa)=0xc001;
 if(!simple47(0x0e,&mode,1)||!simple47(0x0d,filter,2)||!simple47(2,loc,3)||!simple47(0x0c,0,0)||!simple47(0x1b,0,0))return 0;
 SPU(0xb0)=0x3000;SPU(0xb2)=0x3000;return 1;
}
int cd_position47(unsigned*p){U8 r[16];unsigned n;if(!cmd47(0x11,0,0,r,&n)||n!=8)return 0;int m=unbcd47(r[5]),s=unbcd47(r[6]),f=unbcd47(r[7]);if(m<0||s<0||s>=60||f<0||f>=75)return 0;unsigned t=(unsigned)(m*4500+s*75+f);if(t<150)return 0;*p=t-150;return 1;}
int cd_stop47(void){U8 r[16],mode=0x80;unsigned n;mute47();if(!simple47(9,0,0))return 0;for(int i=0;i<32;i++){int e=event47(r,&n);if(e==2)return n&&!(r[0]&1)&&simple47(0x0e,&mode,1);if(e!=1)return 0;}return 0;}
