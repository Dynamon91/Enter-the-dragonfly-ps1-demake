/* Load a version-specific immutable boot bank into caller-owned scratch space.
 * The caller must upload the verified bytes before reusing scratch for geometry.
 * No hardware writes or pointer publication on incomplete or corrupted reads. */
#ifndef STARTUP32_H
#define STARTUP32_H
#include "bootbank32.h"
static U32 bootcrc32(const U8 *p,U32 n){
 static const U32 tab[16]={0,0x1db71064u,0x3b6e20c8u,0x26d930acu,0x76dc4190u,0x6b6b51f4u,0x4db26158u,0x5005713cu,0xedb88320u,0xf00f9344u,0xd6d6a3e8u,0xcb61b38cu,0x9b64c2b0u,0x86d3d2d4u,0xa00ae278u,0xbdbdf21cu};
 U32 c=~0u;while(n--){c^=*p++;c=(c>>4)^tab[c&15];c=(c>>4)^tab[c&15];}return ~c;
}
static int bootload32(U8 *dst,U32 cap,U32 lba,U32 bytes,Read18 read,void*ctx){
 if(!dst||!read||bytes!=BOOT_BYTES32||cap<BOOT_PAD32||lba>=449850u||BOOT_PAD32/2048u>449850u-lba)return 0;
 for(U32 i=0;i<BOOT_PAD32/2048u;){U32 n=BOOT_PAD32/2048u-i;if(n>32)n=32;if(!read(ctx,lba+i,n,dst+i*2048u))return 0;i+=n;}
 return bootcrc32(dst,BOOT_BYTES32)==BOOT_CRC32;
}
#endif
