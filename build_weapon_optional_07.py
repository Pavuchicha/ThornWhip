#!/usr/bin/env python3
"""Fifteenth (ordinary optional) accessory rail for every weapon family."""
from pathlib import Path
from PIL import Image,ImageDraw
import json
R=Path(__file__).parent
families=json.loads((R/'ThornWhip/Documentation/weapon_families.json').read_text())
for family in families:
 key=family['family']['key']
 root=R/'ThornWhip/Textures/ThornWhip/Parts'/key
 root.mkdir(parents=True,exist_ok=True)
 for i in range(5):
  img=Image.new('RGBA',(1024,320),(0,0,0,0));d=ImageDraw.Draw(img)
  if key=='Pistol': x,y=620,188
  elif key=='Launcher':x,y=555,192
  else:x,y=625,194
  shade=(63+25*i,115+21*i,121+10*i,235)
  d.rounded_rectangle([x-6,y-3,x+110+i*4,y+10],radius=3,fill=(14,36,48,245),outline=shade,width=3)
  for k in range(6+i):
   xx=x+k*15
   d.line([(xx,y-5),(xx,y+14)],fill=shade,width=3)
  if i>=3:d.rounded_rectangle([x+48,y-26,x+90,y-6],radius=3,fill=(18,47,54,245),outline=(99,181,173,255),width=2)
  img.save(root/f'P14_V{i}.png')
print('Optional rail images generated: 20')
