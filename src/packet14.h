/* GTE SXY outputs are signed 11-bit coordinates. Preserve all six coordinates exactly. */
typedef struct {u16 low[3],high[2];u16 uv[3];u16 id,next;} Packet;
_Static_assert(sizeof(Packet)==20,"Packet budget");
static void packet_coords(Packet*q,u32 a,u32 b,u32 c){u32 v[3]={a,b,c};for(int i=0;i<3;i++){u32 x=v[i]&2047u,y=(v[i]>>16)&2047u;q->low[i]=x|((y&31u)<<11);if(i==0)q->high[0]=y>>5;else if(i==1)q->high[0]|=(y>>5)<<6;else q->high[1]=y>>5;}}
static u32 packetxy(const Packet*q,int i){u32 x=q->low[i]&2047u,y=(q->low[i]>>11)|(((i==2?q->high[1]:q->high[0]>>(i*6))&63u)<<5);return (x&1024u?x|0xf800u:x)|((y&1024u?y|0xf800u:y)<<16);}
