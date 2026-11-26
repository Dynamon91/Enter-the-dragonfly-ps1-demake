/* Native-safe bounded sector validation. Transport and residency are separate.
 * Reads little endian bytes without alignment assumptions or libc. */
typedef unsigned char U8;typedef unsigned short U16;typedef unsigned int U32;
static U16 rd16(const U8*p){return (U16)(p[0]|((U16)p[1]<<8));}
static U32 rd32(const U8*p){return (U32)rd16(p)|((U32)rd16(p+2)<<16);}
static int s16(const U8*p){U16 x=rd16(p);return x&0x8000?(int)x-65536:x;}
static U32 crc32(const U8*p,U32 n){U32 c=~0u;while(n--){c^=*p++;for(int i=0;i<8;i++)c=(c>>1)^(0xedb88320u&-(c&1u));}return ~c;}
/* out = id, nr, nc, no, ox, oy, oz. No output is published on rejection. */
int sector16_validate(const U8*p,U32 len,U32 material_count,U32 render_count,U32 collision_count,U32*out){
 if(!p||!out||len<64||len>65536||rd32(p)!=0x53445445u||rd16(p+4)!=1||rd16(p+6)!=64)return 0;
 U32 nr=rd16(p+24),nc=rd16(p+26),no=rd16(p+28),bytes=rd32(p+32);if(rd16(p+30)||(!nr&&!nc&&!no)||bytes!=nr*36u+nc*24u+no*16u||bytes!=len-64||crc32(p+64,bytes)!=rd32(p+36))return 0;
 int lo[3],hi[3];for(int i=0;i<3;i++){lo[i]=s16(p+40+i*2);hi[i]=s16(p+46+i*2);if(lo[i]>hi[i])return 0;}
 const U8*q=p+64;for(U32 kind=0;kind<3;kind++){U32 count=kind==0?nr:kind==1?nc:no;U32 stride=kind==0?36:kind==1?24:16;for(U32 j=0;j<count;j++,q+=stride){for(int v=0;v<(kind==2?1:3);v++)for(int a=0;a<3;a++){int x=s16(q+6*v+2*a);if(x<lo[a]||x>hi[a])return 0;}
 if(kind==0&&(rd16(q+30)>=material_count||rd32(q+32)>=render_count))return 0;
 if(kind==1&&((rd16(q+18)!=0&&rd16(q+18)!=3)||rd32(q+20)>=collision_count))return 0;
 if(kind==2&&(rd16(q+6)<1||rd16(q+6)>4||rd16(q+10)))return 0;
 }}
 out[0]=rd32(p+8);out[1]=nr;out[2]=nc;out[3]=no;for(int i=0;i<3;i++)out[4+i]=rd32(p+12+i*4);return 1;
}
/* Disc transport reads whole 2048-byte sectors relative to HUBSECT.DAT.
 * Caller retains a single 64 KiB staging slot; result is not committed on failure.
 * The transport callback must return 1 only after an exact read. */
typedef int (*SectorRead16)(void*,U32,U32,U8*);
int sector16_load(const U8*idx,U32 ilen,U32 id,U32 data_sectors,U32 mat,U32 nr,U32 nc,U8*slot,U32 cap,SectorRead16 read,void*ctx,U32*out){
 if(!idx||!slot||!read||!out||ilen<16||rd32(idx)!=0x49445445u||rd16(idx+4)!=1||rd16(idx+6)!=60||rd32(idx+12)!=4096)return 0;
 U32 n=rd32(idx+8);if(n!=(ilen-16)/60||(ilen-16)%60||id>=n)return 0;
 const U8*e=idx+16+60*id;U32 lba=rd32(e+4),size=rd32(e+8);if(rd32(e)!=id||size<64||size>65536)return 0;
 U32 sectors=(size+2047)/2048;if(sectors>cap/2048||lba>data_sectors||sectors>data_sectors-lba)return 0;
 if(!read(ctx,lba,sectors,slot))return 0;U32 temp[7];if(!sector16_validate(slot,size,mat,nr,nc,temp)||temp[0]!=id||rd32(slot+36)!=rd32(e+12))return 0;
 for(int i=0;i<3;i++){if(temp[1+i]!=rd16(e+52+i*2)||temp[4+i]!=rd32(e+16+i*4))return 0;
  /* Unsigned addition is defined even for negative signed coordinates. */
  if(temp[4+i]+(U32)s16(slot+40+i*2)!=rd32(e+28+i*4)||temp[4+i]+(U32)s16(slot+46+i*2)!=rd32(e+40+i*4))return 0;
 }
 for(int i=0;i<7;i++)out[i]=temp[i];return 1;
}
