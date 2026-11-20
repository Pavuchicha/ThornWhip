from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import math,random
ROOT=Path(__file__).resolve().parent
out=ROOT/'ThornWhip/Textures/ThornCorps/Defense'
out.mkdir(parents=True,exist_ok=True)
random.seed(23)
S=256
OUTLINE='#111920'; ARMOR='#323c42'; DEEP='#172329'; PLATE='#49575d'; METAL='#677279'; HILITE='#8a9a9e'; RED='#a53f3b'; DARKRED='#592c2f'; GLOW='#6fc8db'; ORANGE='#e3a15e'

def poly(d,points,fill,outline=OUTLINE,w=4):d.polygon(points,fill=fill); d.line(points+[points[0]],fill=outline,width=w,joint='curve')
def rivet(d,x,y,r=3):d.ellipse((x-r,y-r,x+r,y+r),fill=HILITE,outline=DEEP,width=1)
def line(d,xy,fill=HILITE,w=3):d.line(xy,fill=fill,width=w,joint='curve')
def base(d,mode='standard'):
    d.ellipse((24,27,232,233),fill=DEEP,outline=OUTLINE,width=8)
    for i in range(8):
        ang=2*math.pi*i/8
        x=128+94*math.sin(ang);y=128+94*math.cos(ang)
        d.ellipse((x-10,y-10,x+10,y+10),fill=PLATE,outline=OUTLINE,width=2)
        rivet(d,x,y)
    poly(d,[(56,39),(199,39),(221,70),(223,182),(195,214),(57,214),(34,185),(34,72)],ARMOR)
    poly(d,[(67,48),(189,48),(207,75),(207,181),(189,201),(68,201),(49,179),(49,78)],PLATE)
    d.rounded_rectangle((75,68,180,194),radius=17,fill=ARMOR,outline=OUTLINE,width=5)
    for x in (48,200):
        d.rectangle((x-4,97,x+4,151),fill=DARKRED)
    for x in (70,187):
        for y in (73,178):rivet(d,x,y,4)
    if mode=='heavy':
        poly(d,[(10,78),(53,50),(53,207),(16,186)],DEEP)
        poly(d,[(204,48),(248,78),(239,188),(207,207)],DEEP)
    if mode=='light':
        d.rectangle((49,82,61,169),fill=RED)

def turret(fam):
 im=Image.new('RGBA',(S,S),(0,0,0,0));d=ImageDraw.Draw(im)
 base(d,'heavy' if fam in ('Railgun','MLRS') else 'light' if fam=='Holder' else 'standard')
 if fam=='Holder':
  d.ellipse((90,90,166,166),fill=DEEP,outline=METAL,width=7)
  for a,b in [((64,79),(95,115)),((192,79),(161,115)),((64,180),(95,140)),((192,180),(161,140))]:
   line(d,[*a,*b],HILITE,10)
  d.rectangle((91,94,165,163),outline=GLOW,width=3)
  for x in (76,180):d.rectangle((x-7,105,x+7,150),fill=RED,outline=OUTLINE,width=3)
 elif fam=='Minigun':
  poly(d,[(82,84),(171,84),(197,105),(197,152),(171,171),(82,171),(59,153),(59,102)],ARMOR)
  d.rectangle((104,54,152,136),fill=DEEP,outline=OUTLINE,width=5)
  for x in (111,124,137,150):
   d.rounded_rectangle((x-7,6,x-1,75),radius=2,fill=METAL,outline=OUTLINE,width=2)
   d.ellipse((x-8,5,x,14),fill=HILITE,outline=OUTLINE,width=1)
  d.ellipse((90,103,167,177),fill=PLATE,outline=OUTLINE,width=5)
  for a in range(8):
   angle=2*math.pi*a/8;x=129+27*math.cos(angle);y=140+27*math.sin(angle)
   rivet(d,x,y,3)
 elif fam=='Laser':
  poly(d,[(75,83),(181,83),(199,112),(185,167),(71,167),(56,113)],DEEP)
  poly(d,[(93,35),(165,35),(176,119),(155,162),(100,162),(80,111)],PLATE)
  d.rectangle((113,5,146,115),fill=ARMOR,outline=OUTLINE,width=5)
  d.line((130,5,130,128),fill=RED,width=10)
  d.ellipse((113,109,147,146),fill='#e04343',outline='#ff9c8e',width=4)
  for x in (76,174):
   for y in (94,122,150):d.rounded_rectangle((x-8,y-6,x+8,y+5),radius=3,fill=GLOW,outline=OUTLINE,width=1)
 elif fam=='Blaster':
  poly(d,[(55,84),(200,84),(216,111),(201,160),(56,160),(39,110)],ARMOR)
  for x in (90,128,166):
   d.rectangle((x-14,12,x+14,123),fill=DEEP,outline=OUTLINE,width=4)
   d.ellipse((x-12,9,x+12,41),fill=GLOW,outline=RED,width=4)
  d.rounded_rectangle((72,119,182,174),radius=12,fill=PLATE,outline=OUTLINE,width=4)
  for x in (88,104,120,136,152):d.rectangle((x,143,x+7,159),fill=RED)
 elif fam=='Railgun':
  base(d,'heavy')
  poly(d,[(94,82),(161,82),(182,145),(158,186),(93,186),(72,145)],DEEP)
  for x in (106,150):
   d.rounded_rectangle((x-12,0,x+12,165),radius=5,fill=DEEP,outline=METAL,width=5)
   for y in range(12,126,18):line(d,[(x-12,y),(x+12,y)],GLOW,4)
  d.rectangle((113,0,145,160),fill=ARMOR,outline=OUTLINE,width=5)
  d.line((128,0,128,139),fill=ORANGE,width=5)
  d.rectangle((78,146,181,175),fill=RED,outline=OUTLINE,width=4)
 elif fam=='ATGM':
  poly(d,[(55,68),(207,68),(213,177),(55,177)],ARMOR)
  for x in (85,167):
   d.rectangle((x-34,22,x+34,137),fill=DEEP,outline=OUTLINE,width=5)
   d.ellipse((x-19,15,x+19,64),fill=METAL,outline=RED,width=5)
   d.ellipse((x-9,23,x+9,51),fill='#a9b1b5',outline=DEEP,width=2)
   poly(d,[(x-11,68),(x+11,68),(x+4,111),(x-4,111)],DARKRED)
  d.rounded_rectangle((71,130,190,177),radius=7,fill=PLATE,outline=OUTLINE,width=5)
  for x in (115,133,151):d.ellipse((x-3,146,x+3,152),fill=ORANGE)
 elif fam=='MLRS':
  base(d,'heavy')
  poly(d,[(39,47),(216,47),(231,78),(231,191),(213,220),(42,220),(25,189),(25,75)],PLATE)
  for row in range(3):
   for col in range(4):
    x=66+col*40;y=72+row*49
    d.ellipse((x-14,y-14,x+14,y+14),fill=OUTLINE,outline=RED,width=5)
    d.ellipse((x-7,y-7,x+7,y+7),fill=DEEP)
  line(d,[(47,189),(209,189)],ORANGE,5)
 im.save(out/f'Turret_{fam}.png')
 return im

def fort(name):
 im=Image.new('RGBA',(S,S),(0,0,0,0));d=ImageDraw.Draw(im)
 d.rectangle((4,8,252,248),fill=DEEP,outline=OUTLINE,width=5)
 for y in (18,64,110,156,202):
  d.rectangle((12,y,244,y+39),fill=PLATE,outline=OUTLINE,width=5)
  d.line((19,y+6,236,y+6),fill=HILITE,width=3)
  d.rectangle((21,y+29,236,y+35),fill=ARMOR)
  for x in (26,79,131,185,226):rivet(d,x,y+17,3)
 if name=='Embrasure':
  d.rectangle((20,107,236,148),fill=OUTLINE,outline=METAL,width=7)
  d.rectangle((33,116,225,136),fill='#070f12')
  d.line((34,104,222,104),fill=RED,width=6)
 if name=='Foxhole':
  d.ellipse((25,22,230,234),fill='#30271e',outline='#66645b',width=14)
  d.ellipse((61,50,199,215),fill='#171e24',outline=METAL,width=8)
  for a in range(12):
   x=128+86*math.cos(a*math.pi/6);y=128+90*math.sin(a*math.pi/6);rivet(d,x,y,4)
 if name=='Sandbag':
  d.rectangle((4,7,253,252),fill=(0,0,0,0))
  for i in range(4):
   for j in range(4):
    x=15+j*56;y=12+i*59
    d.ellipse((x,y,x+66,y+49),fill=PLATE,outline=DEEP,width=5)
    d.arc((x+8,y+4,x+58,y+38),0,180,fill=HILITE,width=2)
 if name=='Bunker':
  d.rectangle((25,44,231,213),fill=ARMOR,outline=OUTLINE,width=9)
  d.rectangle((75,60,180,188),fill=DEEP,outline=METAL,width=6)
  d.rectangle((74,102,182,125),fill=OUTLINE)
  d.line((75,98,180,98),fill=RED,width=5)
  for x in (45,214):
   for y in (62,193):rivet(d,x,y,5)
 if name=='ArmoredGate':
  d.rectangle((30,20,228,235),fill=ARMOR,outline=OUTLINE,width=8)
  d.line((128,19,128,237),fill=OUTLINE,width=9)
  for x in (62,167):
   d.rectangle((x,41,x+29,200),fill=DEEP,outline=METAL,width=5)
   d.rectangle((x+5,77,x+24,169),fill=RED)
  for y in (23,206):
   for x in (45,209):rivet(d,x,y,6)
 im.save(out/f'Fort_{name}.png')
 return im

def trench(depth):
 im=Image.new('RGBA',(S,S),(0,0,0,0));d=ImageDraw.Draw(im)
 d.rectangle((0,0,256,256),fill='#403e34')
 d.polygon([(10,0),(246,0),(219,256),(31,256)],fill='#241f1b')
 d.rectangle((36,0,220,256),fill='#181f25' if depth==3 else '#292c30')
 for x in (28,222):
  line(d,[(x,0),(x,256)],METAL,8)
  for y in range(14,256,31):riv=3;d.ellipse((x-3,y-3,x+3,y+3),fill=ORANGE)
 for y in range(25,255,57):
  d.line((38,y,217,y),fill=DARKRED,width=5)
  d.line((52,y-6,202,y-6),fill=HILITE,width=2)
 if depth==3:d.rectangle((55,0,201,256),fill='#0e1b21')
 im.save(out/f'Trench_{depth}.png')
 return im

# Variant textures follow the *actual* chosen mounted configuration.
PROFILE_VARIANTS={
  'Minigun':['56x6','762x6','762x8','20x6'],
  'Laser':['Cooling','Pulse'],
  'Blaster':['Pierce','Fury'],
  'Railgun':['Medium','Heavy'],
  'ATGM':['Dual','Guided'],
  'MLRS':['Swarm','Heavy']
}

def profile_sprite(family,variant):
    im=turret(family).copy(); d=ImageDraw.Draw(im)
    if family=='Minigun':
        n=8 if variant=='762x8' else 6
        y=7
        for x in range(128-((n-1)*13)//2,128+((n-1)*13)//2+1,13):
            d.rounded_rectangle((x-5,3,x+5,68),radius=3,fill=DEEP,outline=HILITE,width=2)
        if variant=='20x6':
            d.rectangle((96,76,159,93),fill=RED,outline=OUTLINE,width=3)
    elif family=='Laser':
        if variant=='Cooling':
            for x in (55,198):
                for y in (91,111,131):d.rectangle((x-8,y-4,x+8,y+4),fill=GLOW,outline=DEEP,width=2)
        else:
            for i in (0,1,2):
                x=115+i*13;d.ellipse((x,18,x+11,34),fill=ORANGE,outline=RED,width=2)
    elif family=='Blaster':
        if variant=='Pierce':
            d.rectangle((103,2,152,101),outline=ORANGE,width=5)
            d.rectangle((116,2,138,100),fill=DEEP,outline=RED,width=3)
        else:
            for x in (65,82,99,116,133,150,167):d.ellipse((x,14,x+10,25),fill=GLOW,outline=DEEP,width=2)
    elif family=='Railgun':
        n=4 if variant=='Heavy' else 2
        for i in range(n):
            y=16+23*i; d.line((105,y,152,y),fill=ORANGE if variant=='Heavy' else GLOW,width=7)
        if variant=='Heavy':d.rectangle((63,152,191,184),fill=RED,outline=DEEP,width=6)
    elif family=='ATGM':
        if variant=='Dual':
            d.rectangle((48,10,207,57),outline=RED,width=5)
            for x in (86,167):d.ellipse((x-21,4,x+21,54),fill=HILITE,outline=DEEP,width=5)
        else:
            d.rectangle((98,114,159,139),fill=DEEP,outline=RED,width=4)
            d.ellipse((110,120,145,146),fill=GLOW,outline=DEEP,width=4)
    elif family=='MLRS':
        if variant=='Swarm':
            for x in range(60,202,24):
                d.ellipse((x-7,13,x+7,27),fill=ORANGE,outline=RED,width=3)
        else:
            d.rectangle((39,39,218,56),fill=RED,outline=OUTLINE,width=4)
            d.rectangle((39,201,218,219),fill=RED,outline=OUTLINE,width=4)
    im.save(out/f'Turret_{family}_{variant}.png')

for family, variants in PROFILE_VARIANTS.items():
    for variant in variants:profile_sprite(family,variant)

imgs={f:turret(f) for f in ['Holder','Minigun','Laser','Blaster','Railgun','ATGM','MLRS']}
for n in ['ReinforcedWall','Embrasure','Bunker','Sandbag','Foxhole','ArmoredGate']:imgs['Fort '+n]=fort(n)
for j in (1,2,3):imgs['Trench '+str(j)]=trench(j)
for name,col in [('Laser',GLOW),('Blaster',ORANGE),('ATGM',RED),('MLRS',ORANGE),('Railgun',HILITE)]:
 for prefix in ('Ammo_','Projectile_'):
  im=Image.new('RGBA',(128,128),(0,0,0,0));d=ImageDraw.Draw(im)
  d.rounded_rectangle((32,14,96,116),radius=12,fill=ARMOR,outline=METAL,width=7)
  d.rectangle((49,23,79,99),fill=col,outline=OUTLINE,width=4)
  d.line((31,42,97,42),fill=RED,width=5)
  im.save(out/(prefix+name+'.png'))
imgs['GunMount']=Image.new('RGBA',(S,S),(0,0,0,0));d=ImageDraw.Draw(imgs['GunMount']);d.rectangle((80,80,175,175),fill=PLATE,outline=DEEP,width=5);imgs['GunMount'].save(out/'GunMount.png')
# Source-game assets preview, not a screenshot, printable and inspectable without the game.
W,H=1560,1020
sheet=Image.new('RGB',(W,H),'#10171e');p=ImageDraw.Draw(sheet)
try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22);title=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',38)
except:font=ImageFont.load_default();title=font
p.text((44,25),'КОРПУС ТЕРНА  /  ОБОРОНИТЕЛЬНЫЙ КОМПЛЕКС 0.9',font=title,fill='#e5f0f3')
for i,(k,im) in enumerate(imgs.items()):
 if i>=15:break
 col=i%5;row=i//5; x=35+col*310;y=94+row*295
 p.rounded_rectangle((x,y,x+290,y+270),radius=11,fill='#1d2731',outline='#394854',width=3)
 icon=im.copy();icon.thumbnail((236,221))
 if icon.mode=='RGBA':sheet.paste(icon,(x+(290-icon.width)//2,y+10),icon)
 else:sheet.paste(icon,(x+(290-icon.width)//2,y+10))
 p.text((x+14,y+232),k,font=font,fill='#b9d9df')
sheet.save(ROOT/'Showcase'/'THORNCORPS_DEFENSE_0.9.png')
print('Generated',len(imgs)+4,'defense PNG files')
