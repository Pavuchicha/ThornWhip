#!/usr/bin/env python3
"""Procedural original transparent per-assembly assets, rather than a single 'variant' picture.
    Western military visual DNA: modular receivers, controls, handguards, sight rails;
    distinctive invented sci-fi shapes, no trademark or 1:1 copies.
"""
from pathlib import Path
import shutil, json
from PIL import Image, ImageDraw, ImageFont
from build_visuals_legacy_rifle import write as write_old
ROOT=Path(__file__).parent
T=ROOT/'ThornWhip/Textures'
DATA=json.loads((ROOT/'ThornWhip/Documentation/weapon_families.json').read_text())
BASE=T/'ThornWhip/Parts'; FALL=T/'Things/Weapons'
# RGBA at large resolution, displayed as full-canvas layer on the weapon.
SIZE=(1024,320)
C={"outline":"#152127","metal":"#34484c","light":"#849b98","dark":"#223136","mid":"#51666a","bright":"#52c7b5","amber":"#bd9565","poly":"#2d3e41"}
def canvas():
 im=Image.new('RGBA', SIZE,(0,0,0,0));return im,ImageDraw.Draw(im)
def rect(d,xy,fill='metal',r=6,edge='outline',w=3):
 d.rounded_rectangle(xy,radius=r,fill=C.get(fill,fill),outline=C.get(edge,edge),width=w)
def poly(d,pts,fill='metal',edge='outline',w=3):
 d.polygon(pts,fill=C.get(fill,fill));d.line(pts+[pts[0]],fill=C.get(edge,edge),width=w,joint='curve')
def line(d,pts,fill='bright',w=3):d.line(pts,fill=C.get(fill,fill),width=w,joint='curve')
def dot(d,x,y,r=4,fill='bright'):
 d.ellipse((x-r,y-r,x+r,y+r),fill=C.get(fill,fill))

def frame(f):
 if f=='Auto':return dict(recv=(380,117,633,198),bolt=(460,145,589,170),lower=(432,176,628,218),bar=(631,146,892,164),stock=(133,130,373,198),guard=(620,127,822,184),mag=(550,200,611,290),sight=(502,94,592,122),grip=(459,197,507,289),muzzle=(881,137,947,172),trigger=(503,212,548,237),recoil=(350,146,423,170),charger=(392,122,453,143),gas=(745,132,772,170),label='AUTO')
 if f=='Pistol':return dict(recv=(398,130,724,175),bolt=(484,138,638,156),lower=(425,165,691,212),bar=(690,147,807,160),stock=(429,200,484,270),guard=(675,163,741,181),mag=(475,203,530,295),sight=(505,110,610,136),grip=(450,188,535,299),muzzle=(799,136,852,170),trigger=(543,190,594,226),recoil=(405,173,490,191),charger=(413,126,467,143),gas=(735,142,759,167),label='PISTOL')
 return dict(recv=(386,128,652,206),bolt=(463,147,594,180),lower=(417,189,653,230),bar=(646,146,916,170),stock=(132,136,399,213),guard=(638,129,816,197),mag=(473,174,641,259),sight=(514,92,610,128),grip=(472,212,529,293),muzzle=(895,132,969,180),trigger=(524,208,575,238),recoil=(354,152,425,182),charger=(395,113,450,136),gas=(737,126,768,177),label='LAUNCHER')

def chassis(f):
 im,d=canvas();p=frame(f)
 x0,y0,x1,y1=p['recv']
 # outline-free internal spine, only background hooks and core rivet points
 rect(d,(x0+10,y0+24,x1-10,y1-16),'dark',5,'metal',3)
 line(d,[(x0+18,y0+34),(x1-19,y0+34)],'mid',4)
 for x in range(x0+35,x1-20,47):dot(d,x,y0+39,3,'amber')
 return im

def part(f,i,v):
 im,d=canvas();p=frame(f)
 def box(key):return p[key]
 if i==0: # receiver exterior, mechanically distinct and visually massive
    x,y,X,Y=box('recv')
    if f=='Pistol':
      poly(d,[(x+7,y+16),(x+34,y-6),(X-15,y-6),(X+7,y+26),(X-4,Y-4),(x+5,Y-5)],'metal' if v==0 else 'mid')
      for k in range(7):line(d,[(X-20-k*9,y+5),(X-23-k*9,y+27)],'dark',3)
    else:
      poly(d,[(x,y+12),(x+33,y-6 if v else y),(X-29,y-6),(X+13,y+14),(X-9,Y-12),(x+18,Y)],'metal' if v==0 else 'mid')
      rect(d,(x+30,y+22,X-33,y+48),'dark')
      for k in range(9):line(d,[(x+30+k*22,y+2),(x+35+k*22,y+2)],'bright' if v else 'light',2)
    line(d,[(x+34,y+13),(X-36,y+12)],'bright' if v else 'light',3)
 if i==1:
    x,y,X,Y=box('lower');poly(d,[(x,y+3),(X,y+2),(X-25,Y),(x+26,Y)],'poly' if v==0 else 'mid')
    line(d,[(x+25,Y-10),(X-18,Y-10)],'amber' if v else 'light',4)
 if i==2:
    x,y,X,Y=box('bar')
    X=X+24 if v else X-37
    rect(d,(x,y,X,y+15),'dark' if v==0 else 'metal',2)
    line(d,[(x+12,y+8),(X-9,y+8)],'light' if v==0 else 'amber',3)
    if v: 
      for k in range(7): line(d,[(x+20+k*33,y-5),(x+28+k*33,y-5)],'bright',3)
 if i==3:
    x,y,X,Y=box('bolt')
    rect(d,(x,y,X,Y),'dark' if v else 'mid',4)
    rect(d,(x+18,y+7,X-20,Y-7),'mid' if v else 'metal',4,'bright' if v else 'outline',2)
    line(d,[(x+28,y+13),(X-31,y+13)],'bright' if v else 'light',3)
 if i==4:
    x,y,X,Y=box('gas')
    rect(d,(x,y,X,Y),'metal' if v==0 else 'mid',5)
    if v:
      line(d,[(x+5,y+8),(X-4,y+8)],'bright',4);dot(d,x+15,y+23,4,'amber')
    else:dot(d,x+11,y+21,4,'light')
 if i==5:
    x,y,X,Y=box('trigger')
    poly(d,[(x+4,y),(X-3,y),(X-12,Y),(x+16,Y)],'dark' if v==0 else 'mid')
    line(d,[(x+11,y+5),(X-13,y+5)],'bright' if v else 'light',3)
 if i==6:
    x,y,X,Y=box('recoil')
    rect(d,(x,y,X,Y),'poly' if v==0 else 'mid',4)
    for k in range(5):line(d,[(x+14+k*12,y+5),(x+14+k*12,Y-5)],'bright' if v else 'light',2)
 if i==7:
    x,y,X,Y=box('stock')
    if f=='Pistol':
      # Backstrap: not a rifle stock; follows the pistol grip.
      poly(d,[(x+20,y-4),(X-5,y),(X-14,Y-4),(x+12,Y+3)],'poly' if v==0 else 'metal')
      for k in range(3):line(d,[(x+23,y+14+k*13),(X-13,y+14+k*13)],'light' if v==0 else 'bright',2)
    else:
      poly(d,[(x+6,y+11),(x+48,y-11),(X-6,y+3),(X+4,y+34),(X-35,Y),(x+12,Y-2)],'poly' if v==0 else 'metal')
      rect(d,(x+3,y+13,x+27,Y-4),'dark',4)
      line(d,[(x+60,y+21),(X-24,y+24)],'light' if v==0 else 'bright',5)
      if v:poly(d,[(x+71,Y-20),(X-61,Y-17),(X-50,Y-4),(x+63,Y-3)],'mid')
 if i==8:
    x,y,X,Y=box('guard')
    poly(d,[(x+2,y+9),(X-25,y),(X,y+29),(X-8,Y-7),(x+12,Y)],'metal' if v==0 else 'mid')
    for k in range(7):
      z=x+18+k*21
      line(d,[(z,y+19),(z+10,y+19)],'dark' if v==0 else 'bright',3)
    line(d,[(x+18,Y-12),(X-24,Y-14)],'light' if v==0 else 'amber',4)
 if i==9:
    x,y,X,Y=box('mag')
    if f=='Launcher':
      # Rotating 40 mm cylinder, visible chambers with versions 3 / 6; drawn below breech.
      cx=(x+X)//2;cy=(y+Y)//2-8;R=73 if v else 58
      d.ellipse((cx-R,cy-R,cx+R,cy+R),fill=C['mid'] if v else C['metal'],outline=C['outline'],width=7)
      n=6 if v else 3
      import math
      for j in range(n):
        phi=2*math.pi*j/n
        xx=cx+int(math.cos(phi)*R*.53);yy=cy+int(math.sin(phi)*R*.53)
        d.ellipse((xx-15,yy-15,xx+15,yy+15),fill=C['dark'],outline=C['bright'] if v else C['light'],width=3)
      d.ellipse((cx-12,cy-12,cx+12,cy+12),fill=C['amber'])
    else:
      xmid=(x+X)//2
      if f=='Pistol':
        # Pistol magazine sits inside the grip; only the bottom base plate is visible.
        rect(d,(x+3,Y-13,X-10,Y+4 if v else Y-1),'mid' if v else 'metal',2)
        if v:line(d,[(x+8,Y-7),(X-16,Y-7)],'bright',3)
      else:
        poly(d,[(x+2,y),(X-4,y),(X+20,Y+12 if v else Y-12),(x+15,Y+13 if v else Y-12)],'mid' if v else 'metal')
      if f!='Pistol':
       for yy in range(y+22,Y-18,14):line(d,[(x+16,yy),(X-14,yy)],'dark',4)
      if f!='Pistol':line(d,[(x+10,Y-18),(X,Y-19)],'bright' if v else 'amber',3)
 if i==10:
    x,y,X,Y=box('sight')
    if v:
      poly(d,[(x+8,Y),(x+24,y-28),(X-27,y-28),(X-8,Y)],'metal')
      rect(d,(x+31,y-22,X-30,y+1),'dark',6,'bright',3)
      dot(d,(x+X)//2,y-10,5,'bright')
    else:
      rect(d,(x+12,Y-15,X-10,Y-8),'mid',3)
      for xx in (x+20,X-20):rect(d,(xx,y,xx+8,Y-11),'dark',3)
 if i==11:
    x,y,X,Y=box('grip')
    poly(d,[(x+8,y),(X-4,y+3),(X-16,Y),(x+2,Y+2)],'poly' if v==0 else 'metal')
    for j in range(4):line(d,[(x+17,y+23+j*14),(X-21,y+22+j*14)],'light' if v==0 else 'bright',2)
 if i==12:
    x,y,X,Y=box('charger')
    rect(d,(x,y,X,Y),'metal' if v else 'dark',3)
    line(d,[(x+8,y+7),(X-7,y+7)],'bright' if v else 'light',3)
    if v:dot(d,X-15,Y-6,4,'amber')
 if i==13:
    x,y,X,Y=box('muzzle')
    rect(d,(x,y,X,Y),'metal' if v==0 else 'mid',4)
    for j in range(3):
      xx=x+13+j*17
      line(d,[(xx,y+7),(xx+5,Y-7)],'dark',4)
    if v:line(d,[(x+11,y+3),(X-6,y+3)],'bright',3)
 return im

def special(f,n):
 im,d=canvas();p=frame(f)
 r=p['sight'];u=p['recv'];g=p['guard'];b=p['bar'];m=p['mag']
 if n in (0,1,2):
    x=r[0]+6+n*36;y=r[1]-26+(n%2)*8
    rect(d,(x,y,x+49,y+18),'dark',3,'bright' if n!=1 else 'amber',3)
    if n==0:dot(d,x+47,y+9,5)
    elif n==1:rect(d,(x+15,y+2,x+29,y+16),'mid',3)
    else:line(d,[(x+10,y+5),(x+38,y+5)],'bright',3)
 if n in (3,4,5):
    x=u[0]+58+(n-3)*50;y=u[1]+45+(n%2)*12
    rect(d,(x,y,x+47,y+19),'dark',3,'amber' if n==4 else 'bright',2)
    for j in range(3):dot(d,x+10+j*13,y+9,2)
 if n==6:
    x,y,X,Y=g;rect(d,(x+36,Y-3,X-23,Y+16),'dark',4,'bright',3)
    for xx in range(x+49,X-24,24):line(d,[(xx,Y+3),(xx+9,Y+3)],'light',2)
 if n==7:
    x,y,X,Y=b;rect(d,(x+50,y-12,x+98,y+27),'mid',4,'amber',3)
    for j in range(4):line(d,[(x+62+j*9,y-6),(x+62+j*9,y+19)],'bright',2)
 if n==8:
    x,y,X,Y=m;rect(d,(X-12,y+6,X+25,y+34),'dark',5,'bright',3);dot(d,X+6,y+18,6,'amber')
 return im

def write():
 # Rebuild the rifle assets with v0.4 exact chassis and parts, then namespace them.
 write_old()
 rdir=BASE/'Rifle';rdir.mkdir(parents=True,exist_ok=True)
 for p in BASE.glob('*.png'):
  shutil.copyfile(p,rdir/p.name)
  p.unlink()  # do not ship redundant root layers
 for r in range(2):
  for b in range(2):
   for m in range(2):
    path=FALL/f'TW_R{r}B{b}M{m}.png'
    shutil.copyfile(path,FALL/f'TW_Rifle_R{r}B{b}M{m}.png')
    path.unlink()
 order=[7,6,2,0,1,3,4,5,8,9,10,11,12,13]
 for entry in DATA[1:]:
  f=entry['family']['key'];fd=BASE/f;fd.mkdir(parents=True,exist_ok=True)
  stock=chassis(f);stock.save(fd/'Chassis.png',optimize=True)
  for i in range(14):
   for v in range(2):part(f,i,v).save(fd/f'P{i:02}_V{v}.png',optimize=True)
  for j in range(9):special(f,j).save(fd/f'S{j:02}.png',optimize=True)
  for r in range(2):
   for b in range(2):
    for m in range(2):
     im=stock.copy()
     for i in order:
      vv={0:r,2:b,9:m}.get(i,0)
      im.alpha_composite(part(f,i,vv))
     im.save(FALL/f'TW_{f}_R{r}B{b}M{m}.png',optimize=True)
 # Contact sheet for visually checking each family & option (not in-game screenshot).
 w=1300;h=4*295+95
 sheet=Image.new('RGB',(w,h),'#101c23');d=ImageDraw.Draw(sheet)
 try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',25)
 except:font=ImageFont.load_default()
 d.text((35,23),'THORN WHIP / FOUR PLATFORMS / REFERENCE RENDERS',font=font,fill='#ddf3ec')
 for z,entry in enumerate(DATA):
  f=entry['family']['key']; y=80+z*295
  d.rounded_rectangle((30,y,1270,y+278),radius=17,fill='#1d3038',outline='#40666c',width=2)
  d.text((50,y+12),entry['family']['label']+'     '+entry['family']['caliber'],font=font,fill='#7ae6ce')
  pic=Image.open(FALL/f'TW_{f}_R1B1M1.png').convert('RGBA')
  pic.thumbnail((1170,200))
  sheet.paste(pic,((w-pic.width)//2,y+60),pic)
 showcase=ROOT/'Showcase';showcase.mkdir(exist_ok=True)
 sheet.save(showcase/'THORNWHIP_FOUR_FAMILIES_0.5.png',optimize=True)
 print('visual families:',[d['family']['key'] for d in DATA], 'per-family layers:',len(list((BASE/'Auto').glob('*.png'))),'fallback:',len(list(FALL.glob('TW_*_R*B*M*.png'))))
if __name__=='__main__':write()
