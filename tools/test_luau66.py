"""Run the exact generated movement/collection code on recovered CCC banks, host CD callback."""
import argparse,ctypes as C,json,struct,subprocess,tempfile,hashlib,zlib,sys
from pathlib import Path

def verify(root,out,assets):
    sys.path.insert(0,str(root/'tools'));from disc16 import raw
    rep=json.loads((out/'report66.json').read_text());x,y,z=rep['spawn'];src=(out/'play66.c').read_text();sine=src[src.index('static const s16 sine['):src.index('#define GP0')];pad=src[src.index('#define PAD_SELECT'):src.index('#include "rig11.h"')];step=src[src.index('typedef struct {int x,y,z,ground,vy,grounded,heading,camera,prev;} Player18;'):src.index('#define NFACE20')];step=step.replace('static int update18','static int update18')
    host='''typedef signed short s16;
#include "cache24.c"
#include "collect21.h"
#include "interact21.h"
'''+pad+sine+'''static Cache18 cache;static PlayerDummy; /* removed below */
static U8 idx[32768];static U32 ext[2],data[2];static int status;static const U8* disk;static int fail;
static int relative(void*ctx,U32 lba,U32 n,U8*dst){(void)ctx;if(fail||lba>data[1]/2048||n>data[1]/2048-lba)return 0;for(U32 i=0;i<n*2048;i++)dst[i]=disk[lba*2048+i];return 1;}
'''+step+'''
static Player18 p;static Collect20 collect;static Interact21 inter;
int boot(const U8*ix,U32 len,const U8*d,U32 bytes){if(len>sizeof idx)return 0;for(U32 i=0;i<len;i++)idx[i]=ix[i];ext[1]=len;data[1]=bytes;disk=d;fail=0;cache18_init(&cache);status=reset18(&p);collectreset20(&collect,p.x,p.y,p.z);interreset21(&inter);return status;}
void tick(int btn){int ox=p.x,oz=p.z;step18(&p,btn,0,0);collectstep21(&collect,&cache,p.x,p.y,p.z,p.heading,sine,inter.health);interstep21(&inter,&cache,p.x,p.y,p.z,ox,oz,p.heading,btn&PAD_SQUARE,btn&PAD_CIRCLE,p.grounded,collect.sx,collect.sy,collect.sz,sine);}
void snapshot(int *o){o[0]=p.x;o[1]=p.y;o[2]=p.z;o[3]=p.ground;o[4]=p.grounded;o[5]=collect.score+inter.score;o[6]=cache.count;o[7]=cache.reads;o[8]=status;o[9]=cache.used_bytes;}
int hasgem(U32 id){return gemid20(id);}
int basket(U32 id){return objectid21(id,2);}
int floor_at(int x,int z,int y){return cache18_floor(&cache,x,z,y,110);}
''';host=host.replace('static PlayerDummy; /* removed below */','')
    (out/'host66.c').write_text(host)
    subprocess.run(['gcc','-shared','-fPIC','-O2','-fsanitize=undefined','-I',str(out),str(out/'host66.c'),str(root/'src/sector27.c'),'-o',str(out/'host66.so')],check=True)
    l=C.CDLL(str(out/'host66.so'));B=C.c_ubyte;P=C.POINTER(B);U=C.c_uint32;l.boot.argtypes=[P,U,P,U];l.snapshot.argtypes=[C.POINTER(C.c_int)];l.hasgem.argtypes=[U];l.basket.argtypes=[U];ix=(out/'LIASECT.IDX').read_bytes();dat=(out/'LIASECT.DAT').read_bytes();ib=(B*len(ix)).from_buffer_copy(ix);db=(B*len(dat)).from_buffer_copy(dat)
    def boot():assert l.boot(ib,len(ix),db,len(dat))==1
    def snap():a=(C.c_int*10)();l.snapshot(a);return list(a)
    boot();initial=snap();assert initial[0]==x and initial[2]==z and abs(initial[1]-y)<=110,initial; y=initial[1]
    traces=[]
    for name,btn in [('forward',16),('right',32),('back',64),('left',128),('charge forward',16|32768)]:
        boot();route=[snap()];
        for i in range(120):l.tick(btn);route.append(snap())
        assert any(p[:3]!=route[0][:3] for p in route[1:]),name
        assert all(0<p[6]<=28 and p[9]<=416*1024 for p in route),name
        assert all(p[1]==p[3] for p in route),name
        traces.append(dict(name=name,frames=120,start=route[0],end=route[-1],positions=[p[:3] for p in route],peak_bytes=max(p[9] for p in route)))
    boot();l.tick(16384);jump=snap();assert jump[1]<y and not jump[4];
    for _ in range(80):l.tick(0)
    assert snap()[1]==y and snap()[4]
    objects=json.loads((assets/'bindings.json').read_text())['objects'];gs=[l.hasgem(o['source_id']) for o in objects if o['kind']==1];bs=[l.basket(o['source_id']) for o in objects if o['edf'].lower().startswith('basket')];assert sorted(gs)==list(range(142));assert sorted(bs)==list(range(39))
    disc=(out/'ETD_L66.bin').read_bytes();assert len(disc)%2352==0
    for i in range(len(disc)//2352):p=disc[i*2352:(i+1)*2352];assert p==raw(i,p[24:2072])
    # verify all mutated bank CRCs and identity counts
    ids=[set(),set(),set()]
    for i in range((len(ix)-16)//60):
        e=struct.unpack_from('<IIII3i6i3H2x',ix,16+60*i);b=dat[e[1]*2048:e[1]*2048+e[2]];assert zlib.crc32(b[64:])==e[3]==struct.unpack_from('<I',b,36)[0];off=64
        for k,(n,stride) in enumerate(zip(e[13:16],(36,24,16))):
            for _ in range(n):sid=struct.unpack_from('<I',b,off+stride-4)[0];assert sid not in ids[k];ids[k].add(sid);off+=stride
    assert list(map(len,ids))==[90812,7601,326]
    result=dict(initial=initial,traces=traces,jump_landed=True,gem_ids=len(gs),basket_ids=len(bs),blocks=(len(ix)-16)//60,raw_sectors=len(disc)//2352,exe_sha256=hashlib.sha256((out/'ETD_L66.EXE').read_bytes()).hexdigest(),disc_sha256=hashlib.sha256(disc).hexdigest())
    (out/'verification66.json').write_text(json.dumps(result,indent=2));print(json.dumps({**result,'traces':[{k:v for k,v in t.items() if k!='positions'} for t in traces]},indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('out',type=Path);p.add_argument('assets',type=Path);a=p.parse_args();verify(*(v.resolve() for v in (a.root,a.out,a.assets)))
