import ctypes as C, json, struct, subprocess, unittest
from pathlib import Path
import numpy as np
from test_m29 import M29, Inter, Flame, CB
R=Path(__file__).resolve().parents[1];P=R/'build_m31/play';A=R/'assets_m31'
class Ninja(C.Structure):_fields_=[(k,C.c_int) for k in 'x y z hx hy hz tx tz'.split()]+[(k,C.c_ubyte) for k in 'initialized mode timer heading'.split()]
class M31(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  src=(R/'build_m29/play/host29.c').read_text().split('#include "enemy29.h"')[0]+'''\n#include "enemy31.h"\nvoid reset31(void){enemy_reset31();}\nvoid step31(Interact21*s,const Cache18*c,int x,int y,int z,int ox,int oz,int charge,int grounded){enemy_step31(s,c,x,y,z,ox,oz,charge,grounded,sn);}\nNinja31* get31(int i){return ninjas31+i;}\nint id31(U32 id){return enemy_id29(id);}\nint large31(int i){return enemylarge29[i];}\nint phasehost31(int i,int tick){return phase31(ninjas31+i,tick);}\nint lifthost31(int i){return lift31(ninjas31+i);}\nint movehost31(int i,const Cache18*c,int x,int z){return move31(ninjas31+i,c,x,z);}\ntypedef short s16;typedef unsigned short u16;\n#include "ninja30.h"\nvoid unpack31(int phase,s16*out){int ep=ninja_offsets30[phase-1];for(int l=0;l<NINJA_NV30;l++)for(int j=0;j<3;j++){int d=ninja_delta30[phase-1][l][j];if(d==-128)d=ninja_escape30[ep++];out[l*3+j]=ninja_base30[l][j]+d;}}\n'''
  (P/'host31.c').write_text(src);subprocess.run(['clang','-O2','-shared','-fPIC','-I',str(P),'-I',str(R/'src'),str(P/'host31.c'),str(R/'src/sector27.c'),'-o',str(P/'host31.so')],check=True);L=cls.L=C.CDLL(str(P/'host31.so'));cls.idx=(P/'DOJOSECT.IDX').read_bytes();cls.dat=(P/'DOJOSECT.DAT').read_bytes();cls.good=CB(lambda ctx,lba,n,p:(C.memmove(p,cls.dat[lba*2048:(lba+n)*2048],n*2048),1)[1]);L.cache22_size.restype=C.c_uint32;L.cache18_init.argtypes=[C.c_void_p];L.cache18_update.argtypes=[C.c_void_p,C.c_char_p,C.c_uint32,C.c_uint32,C.c_int,C.c_int,CB,C.c_void_p];L.cache18_floor.argtypes=[C.c_void_p,C.c_int,C.c_int,C.c_int,C.c_int];L.reset21.argtypes=[C.POINTER(Inter)];L.step31.argtypes=[C.POINTER(Inter),C.c_void_p]+[C.c_int]*7;L.get31.restype=C.POINTER(Ninja);L.movehost31.argtypes=[C.c_int,C.c_void_p,C.c_int,C.c_int];L.id31.argtypes=[C.c_uint32];L.unpack31.argtypes=[C.c_int,C.POINTER(C.c_short)];cls.enemies=[o for o in json.loads((R/'assets_m27/sector_manifest.json').read_text())['objects'] if 'ninja_riptoc' in o['edf'].lower()]
 def new(self,o):
  L=self.L;w=C.create_string_buffer(L.cache22_size());L.cache18_init(w);x,y,z=map(round,o['source_xyz']);self.assertTrue(self.load(w,x,z));f=L.cache18_floor(w,x,z,-y,110);self.assertNotEqual(f,32767);s=Inter();L.reset21(C.byref(s));L.reset31();return w,s,L.id31(o['record_offset']),x,f,z
 def load(self,w,x,z):return self.L.cache18_update(w,self.idx,len(self.idx),len(self.dat)//2048,x,z,self.good,None)
 def step(self,w,s,x,y,z,charge=0):self.L.step31(C.byref(s),w,x,y,z,x-19 if charge else x,z,charge,1)
 def test_source_animation(self):
  z=np.load(A/'ninja.npz');old=np.load(R/'assets_m30/ninja.npz');np.testing.assert_array_equal(z['frames'][:19],old['frames']);self.assertEqual(z['frames'].shape,(35,323,3));a=np.empty((323,3),np.int16)
  for i in range(1,35):self.L.unpack31(i,a.ctypes.data_as(C.POINTER(C.c_short)));np.testing.assert_array_equal(a,z['frames'][i])
  self.assertGreater(np.abs(z['frames'][19]-z['frames'][26]).sum(),1000);self.assertGreater(np.abs(z['frames'][27]-z['frames'][34]).sum(),1000)
 def test_attack_trace(self):
  L=self.L; traces=[]
  for o in self.enemies:
   w,s,i,x,f,z=self.new(o)
   for dx,dz in [(250,0),(-250,0),(0,250),(0,-250)]:
    g=L.cache18_floor(w,x+dx,z+dz,f,110)
    if g==32767:continue
    L.reset31();L.reset21(C.byref(s));rows=[]
    for t in range(80):
     self.step(w,s,x+dx,g,z+dz);n=L.get31(i).contents;rows.append(dict(t=t,mode=n.mode,x=n.x,y=n.y,z=n.z,phase=L.phasehost31(i,t),lift=L.lifthost31(i),health=s.health,heading=n.heading));self.assertTrue(1<=rows[-1]['phase']<=34)
     if n.initialized:self.assertLessEqual(max(abs(n.x-x),abs(n.z-z)),460);self.assertNotEqual(L.cache18_floor(w,n.x,n.z,n.y,45),32767)
    if {1,2,3}<=set(r['mode'] for r in rows) and any(r['x']!=x or r['z']!=z for r in rows) and s.health<3:
     self.assertTrue(all(r['health']==3 for r in rows[:18]));traces.append(dict(id=i,large=L.large31(i),player=[x+dx,g,z+dz],home=[x,f,z],rows=rows));break
   if len(traces)>=2 and len({t['large'] for t in traces})==2:break
  self.assertEqual({t['large'] for t in traces},{0,1});(P/'attack_trace.json').write_text(json.dumps(traces,indent=2));print('attack traces:',[(t['id'],t['large']) for t in traces])
 def test_death_persistence(self):
  L=self.L
  for large in (0,1):
   o=next(o for o in self.enemies if L.large31(L.id31(o['record_offset']))==large);w,s,i,x,f,z=self.new(o);self.step(w,s,x,f,z,1);n=L.get31(i).contents
   if large:self.assertNotEqual(n.mode,4);s.fire[0]=Flame(x,f-135,z,0,0,0,10);self.step(w,s,x,f,z)
   self.assertEqual(n.mode,4);self.assertEqual(L.phasehost31(i,0),27);self.assertTrue(self.load(w,10534,-14914))
   for _ in range(60):self.step(w,s,10534,-2075,-14914)
   self.assertEqual(n.mode,5);self.assertTrue(self.load(w,x,z));self.step(w,s,x,f,z);self.assertEqual(n.mode,5);L.reset31();self.assertEqual(n.mode,0);self.assertEqual(n.initialized,0)
 def test_blocked_motion(self):
  o=self.enemies[0];w,s,i,x,f,z=self.new(o);self.step(w,s,x,f,z);n=self.L.get31(i).contents;self.assertFalse(self.L.movehost31(i,w,x+461,z));empty=C.create_string_buffer(self.L.cache22_size());self.L.cache18_init(empty);self.assertFalse(self.L.movehost31(i,empty,x+10,z));self.assertEqual((n.x,n.y,n.z),(x,f,z))
 def test_disc(self):
  from disc16 import raw
  d=(P/'ETD_PSX_M31.bin').read_bytes();self.assertIn(b'ETD_AI.EXE;1',d[21*2352+24:21*2352+2072]);self.assertIn(b'ETD_EYES.EXE;1',d[20*2352+24:20*2352+2072]);self.assertGreater(json.loads((P/'report31.json').read_text())['headroom_to_stack_region'],32768)
  for i in range(len(d)//2352):s=d[i*2352:(i+1)*2352];self.assertEqual(s,raw(i,s[24:2072]))
  for n in ['DOJOSECT.DAT','DOJOSECT.IDX']:self.assertEqual((P/n).read_bytes(),(R/'build_m30/play'/n).read_bytes())
if __name__=='__main__':unittest.main()
