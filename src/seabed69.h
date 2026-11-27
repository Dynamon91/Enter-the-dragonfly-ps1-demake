/* Fallback only when the source collision bed is absent. Actual source seabed
 * render triangles, restricted to sandedge, sandwater and waterbot materials.
 * This is a collision proxy, not decoded original collision data. */
static int seabed69(const Cache18*c,int x,int z,int w){int best=NONE18;
 for(int j=0;j<c->count;j++){int k=c->active[j];const U32*m=c->meta[k];const U8*t=c->bytes[k]+64;int qx=x-(int)m[4],qz=z-(int)m[6];
 for(U32 i=0;i<m[1];i++,t+=36){int mat=(U16)(t[30]|t[31]<<8);if(mat!=28&&mat!=53&&mat!=59)continue;
 int ax=s18(t),ay=s18(t+2)+(int)m[5],az=s18(t+4),bx=s18(t+6)-ax,by=s18(t+8)+(int)m[5]-ay,bz=s18(t+10)-az,cx=s18(t+12)-ax,cy=s18(t+14)+(int)m[5]-ay,cz=s18(t+16)-az;
 if(ay<w+140||ay+by<w+140||ay+cy<w+140)continue;
 long long d=cross18(bx,bz,cx,cz);if(!d)continue;long long a=d<0?-d:d,nx=cross18(by,bz,cy,cz),nz=cross18(bx,by,cx,cy);if((nx<0?-nx:nx)>2*a||(nz<0?-nz:nz)>2*a)continue;
 long long u=cross18(qx-ax,qz-az,cx,cz),v=cross18(bx,bz,qx-ax,qz-az);if(d<0){d=-d;u=-u;v=-v;}if(u<0||v<0||u+v>d)continue;int y=ay+ratio18(u*by+v*cy,d);if(y<=w+3200&&y<best)best=y;
 }}return best;}
