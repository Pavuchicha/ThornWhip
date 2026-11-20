#!/usr/bin/env python3
"""Extend the existing original sprite-layer set, preserving 0/1 art for old blueprints.
New parts contain different physical contour/sensors/ribbing, not merely icon changes.
"""
from pathlib import Path
import math
from PIL import Image,ImageDraw,ImageFont
from build_visuals import frame, C
R=Path(__file__).parent
P=R/'ThornWhip/Textures/ThornWhip/Parts';S=R/'Showcase'
REGIONS=['recv','lower','bar','bolt','gas','trigger','recoil','stock','guard','mag','sight','grip','charger','muzzle']
RIFLE=dict(recv=(388,105,645,186),lower=(448,170,621,224),bar=(645,137,896,166),bolt=(465,145,590,176),
 gas=(722,124,769,178),trigger=(503,200,553,241),recoil=(340,144,450,180),stock=(133,126,377,210),
 guard=(630,116,830,186),mag=(544,197,643,298),sight=(516,78,622,131),grip=(440,195,517,291),
 charger=(387,118,466,155),muzzle=(877,128,973,177))

def reg(f,i):return (RIFLE if f=='Rifle' else frame(f))[REGIONS[i]]

def draw_new_part(f,i,v):
 base=Image.open(P/f/f'P{i:02}_V{0 if v==2 else 1}.png').convert('RGBA')
 d=ImageDraw.Draw(base)
 x,y,X,Y=reg(f,i)
 w=max(18,X-x);h=max(14,Y-y)
 # staggered silhouette appendages: remove/add 1–4 physical assemblies
 if v==2:
  # exposed low-tech shell: holes, seam line and old service catches
  p=[(x+8,y+7),(X-9,y+9),(X-13,Y-9),(x+12,Y-12)]
  d.line(p,fill='#b0aaa1',width=3,joint='curve')
  for j in range(3):
   xx=x+int(w*(.23+j*.24));yy=y+int(h*.34)
   d.ellipse((xx-5,yy-5,xx+5,yy+5),fill='#162126',outline='#92a0a0',width=2)
 elif v==3:
  # thick armour, machine-milled ribs, dual fixtures
  x0=x+int(w*.10);x1=X-int(w*.10);yy=y+int(h*.13)
  d.rounded_rectangle((x0,yy,x1,yy+max(7,int(h*.21))),radius=3,fill='#485a5d',outline='#92b3b2',width=3)
  for j in range(4):
   xx=x0+int((x1-x0)*(j+1)/5)
   d.line(((xx,yy+3),(xx+4,yy+max(5,int(h*.19)))),fill='#1c2a2f',width=3)
  d.line(((x+int(w*.19),Y-7),(X-int(w*.16),Y-7)),fill='#b7a37d',width=4)
 elif v==4:
  # self-diagnostic module, recessed luminous conductors and neural ports
  ymid=y+int(h*.42)
  d.line([(x+int(w*.08),ymid),(x+int(w*.24),ymid-6),(x+int(w*.48),ymid+4),
          (X-int(w*.21),ymid-6),(X-int(w*.10),ymid)],fill='#3cedc8',width=4)
  bx=x+int(w*.76);by=y+int(h*.25)
  d.rounded_rectangle((bx-13,by-9,bx+15,by+9),radius=4,fill='#0b2225',outline='#57f9da',width=3)
  d.ellipse((bx-4,by-4,bx+5,by+5),fill='#72e6d4')
  for j in range(3):
   yy=y+int(h*(.15+.18*j));d.line(((x+7,yy),(x+int(w*.13),yy)),fill='#d8b175',width=3)
 return base

def make_special(f,n):
 im=Image.new('RGBA',(1024,320),(0,0,0,0));d=ImageDraw.Draw(im)
 p=RIFLE if f=='Rifle' else frame(f)
 x,y,X,Y=p['sight']
 if n==9:  # angular prism atop the sight plane
  px=x+35;py=y-39
  d.polygon([(px,py+30),(px+10,py+2),(px+57,py+4),(px+68,py+29)],fill='#56676c')
  d.rectangle((px+16,py+10,px+49,py+24),fill='#102c35',outline='#63dfcf',width=3)
  d.line([(px+8,py+34),(px+67,py+34)],fill='#c9a77c',width=5)
 if n==10: # small holo-array / segmented emitter
  px=x+43;py=y-22
  d.rounded_rectangle((px,py,px+45,py+12),radius=4,fill='#33494d',outline='#64dfcb',width=3)
  for k in range(4):
   xx=px+7+k*10;d.line([(xx,py-12),(xx+3,py-20)],fill='#46d9ca',width=3)
 if n==11: # heavy receiver recoil bracket
  x,y,X,Y=p['recv'];px=x+int((X-x)*.32);py=y+int((Y-y)*.72)
  d.rounded_rectangle((px,py,px+95,py+27),radius=6,fill='#3e5559',outline='#c4a47a',width=3)
  for xx in range(px+10,px+93,21):d.ellipse((xx,py+7,xx+7,py+14),fill='#111e25')
 if n==12: # cooled barrel cartridge, integrated pipe above barrel
  x,y,X,Y=p['bar'];px=x+int((X-x)*.20);py=y-20
  d.rounded_rectangle((px,py,px+102,py+24),radius=7,fill='#294d53',outline='#48ddca',width=3)
  for xx in range(px+12,px+98,17):d.line([(xx,py+5),(xx,py+19)],fill='#b6ad85',width=2)
 if n==13: # magazine diagnostic display
  x,y,X,Y=p['mag'];px=X-19;py=y+int((Y-y)*.26)
  d.rounded_rectangle((px,py,px+32,py+41),radius=4,fill='#203a3d',outline='#45ddbc',width=3)
  for j in range(3):d.line([(px+8,py+9+j*10),(px+23-j*3,py+9+j*10)],fill='#97dcc8',width=3)
 if n==14: # paired neural sentinels flanking top rail
  x,y,X,Y=p['sight'];px=x+15;py=y-21
  for dxx in (0,67):
   d.rounded_rectangle((px+dxx,py,px+dxx+29,py+25),radius=5,fill='#2a4647',outline='#65efce',width=3)
   d.ellipse((px+dxx+9,py+6,px+dxx+19,py+16),fill='#b6f5d7')
  d.line([(px+27,py+12),(px+67,py+12)],fill='#64dbc7',width=3)
 return im

if __name__=='__main__':
 for f in ['Rifle','Auto','Pistol','Launcher']:
  path=P/f
  for i in range(14):
   for v in (2,3,4):draw_new_part(f,i,v).save(path/f'P{i:02}_V{v}.png',optimize=True)
  for n in range(9,15):make_special(f,n).save(path/f'S{n:02}.png',optimize=True)
 # Sprite showcase: all five variants of one receiver, and full weapon with 3 special attachments
 sheet=Image.new('RGB',(1230,4*272+80),'#101e26');d=ImageDraw.Draw(sheet)
 try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',25)
 except:font=ImageFont.load_default()
 d.text((26,20),'THORN WHIP 0.6 — 5 MODULE CHOICES · 15 SPECIALS',font=font,fill='#b4f7e3')
 from PIL import ImageOps
 texroot=R/'ThornWhip/Textures/Things/Weapons'
 for fi,f in enumerate(['Rifle','Auto','Pistol','Launcher']):
  y=63+272*fi
  d.rounded_rectangle((23,y,1202,y+258),radius=15,fill='#1d3239',outline='#438d89',width=3)
  d.text((40,y+6),f.upper()+' — BASE / FIELD / HEAVY / NEURAL',font=font,fill='#82f1d8')
  for v in range(5):
   weapon=Image.open(texroot/f'TW_{f}_R0B0M0.png').convert('RGBA')
   for ix in (0,2,7,9,10,13):
    layer=Image.open(P/f/f'P{ix:02}_V{v}.png').convert('RGBA')
    weapon.alpha_composite(layer)
   if v==4:
    for sp in (9,11,14):weapon.alpha_composite(Image.open(P/f/f'S{sp:02}.png').convert('RGBA'))
   weapon.thumbnail((218,165))
   sheet.paste(weapon,(45+233*v,y+72),weapon)
   d.text((66+233*v,y+224),f'ASSEMBLY {v+1:02}',font=font,fill='#b8d8d5')
 S.mkdir(exist_ok=True)
 sheet.save(S/'THORNWHIP_FIVE_OPTIONS_0.6.png',optimize=True)
 print('Generated',4*(14*3+6),'new sprites; 4x',14*5,'part choices and 15 special sprites')
