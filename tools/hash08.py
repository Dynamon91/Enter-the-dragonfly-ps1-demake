"""Folded MD4 used by original PS2 texture lookup. RFC 1320 primitive."""
import struct
MASK=0xffffffff
def md4(data):
 data=bytes(data); n=len(data); data+=b'\x80'+b'\0'*((55-n)%64)+struct.pack('<Q',n*8)
 state=[0x67452301,0xefcdab89,0x98badcfe,0x10325476]
 for i in range(0,len(data),64):
  X=struct.unpack_from('<16I',data,i); a,b,c,d=state
  for k in range(48):
   j=k%16
   if k<16: f=(b&c)|(~b&d); g=j;s=(3,7,11,19)[j%4];v=0
   elif k<32:f=(b&c)|(b&d)|(c&d);g=(j%4)*4+j//4;s=(3,5,9,13)[j%4];v=0x5a827999
   else:f=b^c^d;g=(0,8,4,12,2,10,6,14,1,9,5,13,3,11,7,15)[j];s=(3,9,11,15)[j%4];v=0x6ed9eba1
   t=(a+f+X[g]+v)&MASK;t=((t<<s)|(t>>(32-s)))&MASK;a,b,c,d=d,t,b,c
  state=[(x+y)&MASK for x,y in zip(state,(a,b,c,d))]
 return struct.pack('<4I',*state)
def fold(data):
 a,b,c,d=struct.unpack('<4I',md4(data));return a^b^c^d
if __name__=='__main__':
 assert md4(b'').hex()=='31d6cfe0d16ae931b73c59d7e0c089c0';assert md4(b'abc').hex()=='a448017aaf21d8525fc10ae87aa6729d'
