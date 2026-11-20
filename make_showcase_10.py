#!/usr/bin/env python3
"""Showcase sheets are assembled strictly from checked-in in-game PNGs."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
T=Path(__file__).resolve().parent/'ThornWhip'/'Textures'
OUT=Path(__file__).resolve().parent/'Showcase'
B='#20242b';FG='#e4e8eb';FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
try:
 f=ImageFont.truetype(FONT,19);h=ImageFont.truetype(FONT.replace('DejaVuSans.ttf','DejaVuSans-Bold.ttf'),24)
except OSError:f=ImageFont.load_default();h=ImageFont.load_default()
def sheet(cols,rows,cell,title):
 a=Image.new('RGB',(cols*cell[0],rows*cell[1]+62),B);d=ImageDraw.Draw(a);d.text((22,12),title,font=h,fill=FG)
 for y in range(rows):
  for x in range(cols):
   xx=x*cell[0];yy=y*cell[1]+62;d.rounded_rectangle((xx+5,yy+5,xx+cell[0]-6,yy+cell[1]-6),radius=9,fill='#2c323b')
 return a
def put(canvas,p,c,r,label,cell,mx):
 im=Image.open(T/p).convert('RGBA');im.thumbnail(mx,Image.Resampling.LANCZOS)
 cx=c*cell[0]+cell[0]//2;cy=r*cell[1]+62+(cell[1]-35)//2
 canvas.paste(im,(cx-im.width//2,cy-im.height//2),im)
 ImageDraw.Draw(canvas).text((c*cell[0]+14,(r+1)*cell[1]+29),label,font=f,fill=FG)
# Turrets 2 palettes, 7 kinds, transparent actual png
names=['Holder','Minigun','Laser','Blaster','Railgun','ATGM','MLRS'];c=(345,250);a=sheet(4,4,c,'КОРПУС ТЕРНА | ТУРЕЛИ — игровые PNG')
for i,n in enumerate(names):
 for st in [0,1]:
  path=('' if st==0 else 'ThornCorps/StyleOrder/')+'ThornCorps/Defense/Turret_'+n+'_north.png'
  put(a,path,i%4,2*(i//4)+st,('Корпус' if st==0 else 'Орден')+' / '+n,c,(230,190))
a.save(OUT/'ACTUAL_TURRETS_10.png')
# Weapons full main in-game png
c=(610,300);a=sheet(2,4,c,'КОРПУС ТЕРНА | ОРУЖИЕ — игровые PNG')
for j,n in enumerate(['Rifle','Auto','Pistol','Launcher']):
 for st in [0,1]:
  path=('' if st==0 else 'ThornCorps/StyleOrder/')+f'Things/Weapons/TW_{n}_R0B0M0.png'
  put(a,path,st,j,n+' / '+('Корпус' if st==0 else 'Орден'),c,(575,218))
a.save(OUT/'ACTUAL_WEAPONS_10.png')
# Armor, 9 x2
c=(225,285);a=sheet(6,3,c,'КОРПУС ТЕРНА | БРОНЯ T1–T3 — игровые PNG')
for row,n in enumerate(['Light','Medium','Heavy']):
 for ti,tier in enumerate([1,2,3]):
  for st in [0,1]:
   path=('' if st==0 else 'ThornCorps/StyleOrder/')+f'Things/Armor/TC_{n}_T{tier}.png'
   put(a,path,ti*2+st,row,n+' T'+str(tier)+' '+('Ч/К' if st==0 else 'Б/К'),c,(200,237))
a.save(OUT/'ACTUAL_ARMOR_10.png')
# Construction rotation proof 2 styles, 4 dirs
c=(270,260);a=sheet(4,4,c,'КОРПУС ТЕРНА | УКРЕПЛЕНИЯ — повороты и стили')
names=['Fort_ReinforcedWall','Fort_Embrasure']
for st in [0,1]:
 for ni,n in enumerate(names):
  row=st*2+ni
  for col,direc in enumerate(['north','east','south','west']):
   path=('' if st==0 else 'ThornCorps/StyleOrder/')+f'ThornCorps/Defense/{n}_{direc}.png'
   put(a,path,col,row,('К' if st==0 else 'О')+'/'+n.removeprefix('Fort_')+'/'+direc,c,(220,203))
a.save(OUT/'ACTUAL_FORT_ROTATIONS_10.png')
# RimWorld About splash made from the exact same PNGs.
a=Image.new('RGB',(1280,720),'#15191f');d=ImageDraw.Draw(a)
d.rectangle((0,0,1280,8),fill='#bf3038');d.text((55,32),'КОРПУС ТЕРНА',font=h,fill=FG);d.text((56,72),'Графический набор: Корпус / Орден',font=f,fill='#adbac6')
items=[('Things/Weapons/TW_Rifle_R0B0M0.png', (24,130,610,320)),('ThornCorps/StyleOrder/Things/Weapons/TW_Rifle_R0B0M0.png',(650,130,1244,320)),('ThornCorps/Defense/Turret_Minigun_north.png',(85,320,590,650)),('ThornCorps/StyleOrder/ThornCorps/Defense/Turret_Minigun_north.png',(680,320,1175,650))]
for path,region in items:
 im=Image.open(T/path).convert('RGBA');x0,y0,x1,y1=region;im.thumbnail((x1-x0,y1-y0),Image.Resampling.LANCZOS);a.paste(im,(x0+(x1-x0-im.width)//2,y0+(y1-y0-im.height)//2),im)
d.text((150,672),'Корпус Терна · чёрный/красный',font=f,fill='#c8cbce');d.text((720,672),'Орден Терна · белый/красный',font=f,fill='#c8cbce')
a.save(Path(__file__).resolve().parent/'ThornWhip'/'About'/'Preview.png')
print('Showcase derived from real source textures')
