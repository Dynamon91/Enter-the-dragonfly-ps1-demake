#ifndef BITPACK37_H
#define BITPACK37_H
/* Four-value groups, 4-bit width, little-endian bit order. Bounded input. */
typedef struct {const unsigned char *p,*end;unsigned acc,bits;int bad;} Bits37;
static inline unsigned take37(Bits37*b,unsigned n){
 while(b->bits<n){if(b->p==b->end){b->bad=1;return 0;}b->acc|=(unsigned)*b->p++<<b->bits;b->bits+=8;}
 unsigned v=b->acc&((1u<<n)-1);b->acc>>=n;b->bits-=n;return v;
}
static inline int signed37(unsigned v){return (int)(v>>1)^-(int)(v&1);}
/* Each group has four encoded lanes; consume padding lanes in the last group. */
static int decode37_s16(const unsigned char*p,const unsigned char*end,short*out,int n,int add){
 Bits37 b={p,end,0,0,0};for(int i=0;i<n;i+=4){unsigned w=take37(&b,4);for(int j=0;j<4;j++){int v=signed37(take37(&b,w));if(i+j<n){int a=add?out[i+j]+v:v;if(a<-32768||a>32767)return 0;out[i+j]=(short)a;}}if(b.bad)return 0;}return b.p==b.end&&b.acc==0;
}
static int decode37_s8(const unsigned char*p,const unsigned char*end,signed char*out,int n){
 Bits37 b={p,end,0,0,0};for(int i=0;i<n;i+=4){unsigned w=take37(&b,4);for(int j=0;j<4;j++){int v=signed37(take37(&b,w));if(i+j<n){if(v<-128||v>127)return 0;out[i+j]=(signed char)v;}}if(b.bad)return 0;}return b.p==b.end&&b.acc==0;
}
#endif
