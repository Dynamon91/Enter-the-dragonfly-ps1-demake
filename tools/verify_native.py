"""Restricted instruction interpreter: checks compiled code writes exactly the intended packets.
Not a PS1 emulator, no timings, interrupts, GPU behavior or actual screen capture."""
import struct,sys,hashlib,json
from pathlib import Path

def verify(path,packetpath):
    b=Path(path).read_bytes(); assert b[:8]==b'PS-X EXE'
    pc,_,base,n=struct.unpack_from('<IIII',b,16); assert base==pc==0x80010000 and len(b)==2048+n and n%2048==0 and n<=0x1e0000
    p=b[2048:]; regs=[0]*32; gp0=[];gp1=[]; pending=None; load=None
    def sx(x):return x-65536 if x&32768 else x
    def read(a):
        if a==0x1f801814:return 0x14000000 # idealized ready GPU
        assert base<=a<=base+len(p)-4 and a%4==0,hex(a)
        return struct.unpack_from('<I',p,a-base)[0]
    for cycles in range(200000):
        v=read(pc);op=v>>26;rs=(v>>21)&31;rt=(v>>16)&31;rd=(v>>11)&31;imm=v&65535
        next_pc=pending if pending is not None else pc+4; pending=None; old_load=load; load=None; write=None
        if v==0:pass
        elif op==15:write=(rt,imm<<16)
        elif op==13:write=(rt,regs[rs]|imm)
        elif op==9:write=(rt,regs[rs]+sx(imm))
        elif op==35:load=(rt,read((regs[rs]+sx(imm))&0xffffffff))
        elif op==43:
            a=(regs[rs]+sx(imm))&0xffffffff
            if a==0x1f801810:gp0.append(regs[rt])
            elif a==0x1f801814:gp1.append(regs[rt])
            else:raise ValueError(hex(a))
        elif op==0 and (v&63)==36:write=(rd,regs[rs]&regs[rt])
        elif op in (4,5):
            if (regs[rs]==regs[rt])==(op==4):
                pending=pc+4+4*sx(imm)
                if pending==pc and gp1[-1]==0x03000000:break
        else:raise ValueError(f'Unexpected instruction {v:08x}')
        if old_load:regs[old_load[0]]=old_load[1]&0xffffffff
        if write:regs[write[0]]=write[1]&0xffffffff
        regs[0]=0;pc=next_pc
    else:raise RuntimeError('Did not reach idle')
    raw=Path(packetpath).read_bytes(); assert struct.pack('<'+'I'*len(gp0),*gp0)==raw; assert gp1==[0,0x03000001,0x05000000,0x06c60260,0x07042018,0x08000001,0x03000000]
    # Check upload extents, drawing env and polygon packet lengths.
    i=0; uploads=[];triangles=0
    while i<len(gp0):
        cmd=gp0[i]>>24
        if cmd==0xa0:
            x=gp0[i+1]&65535;y=gp0[i+1]>>16;w=gp0[i+2]&65535;h=gp0[i+2]>>16
            assert x+w<=1024 and y+h<=512 and x>=320
            uploads.append([x,y,w,h]);i+=3+(w*h+1)//2
        elif cmd in (0xe1,0xe3,0xe4,0xe5,0xe6):i+=1
        elif cmd==2:i+=3
        elif cmd==0x25:
            for j in (1,3,5):assert 0<=gp0[i+j]&65535<320 and 0<=gp0[i+j]>>16<240
            i+=7;triangles+=1
        else:raise ValueError(hex(cmd))
    assert i==len(gp0) and triangles==444
    return dict(executable_bytes=len(b),gpu_words=len(gp0),triangles=triangles,uploads=uploads,idealized_instruction_steps=cycles+1,sha256=hashlib.sha256(b).hexdigest(),status='PASS: compiled instructions, load/branch delays, GP0 stream, bounds; NOT emulator or hardware tested')
if __name__=='__main__': print(json.dumps(verify(*sys.argv[1:]),indent=2))
