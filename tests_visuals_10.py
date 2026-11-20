#!/usr/bin/env python3
"""Visual artifact consistency checks, without assuming that C# or RimWorld have run."""
from pathlib import Path
from collections import Counter
from xml.etree import ElementTree as ET
from PIL import Image
R=Path(__file__).resolve().parent
T=R/'ThornWhip'/'Textures'
D=R/'ThornWhip'/'Defs'

def exists(rel):return (T/(rel+'.png')).is_file()
styles=ET.parse(D/'TC_IdeologyStyles.xml').getroot()
cats=styles.findall('StyleCategoryDef');assert len(cats)==2
maps=[c.find('thingDefStyles').findall('li') for c in cats]
assert len(maps[0])==len(maps[1])>=100, [len(x) for x in maps]
for cat in cats:
 assert cat.findtext('defName') in ('TC_StyleCorps','TC_StyleOrder')
 for e in cat.findall('thingDefStyles/li'):
  assert e.findtext('thingDef') and e.findtext('styleDef')
styles_by_name={e.findtext('defName'):e for e in styles.findall('ThingStyleDef')}
for sd in styles_by_name.values():
 path=sd.findtext('graphicData/texPath');assert path
 gc=sd.findtext('graphicData/graphicClass')
 if gc=='Graphic_Multi':
  for direction in ('north','south','east','west'):assert exists(path+'_'+direction),(path,direction)
 else:assert exists(path),path
 worn=sd.findtext('wornGraphicPath')
 if worn:
  for direction in ('north','south','east','west'):assert exists(worn+'_'+direction),(worn,direction)
# One game texture for every listed key/mode, independent of special/module overlays.
for weapon in ('Rifle','Auto','Pistol','Launcher'):
 for a in (0,1):
  for b in (0,1):
   for c in (0,1):
    path=f'Things/Weapons/TW_{weapon}_R{a}B{b}M{c}'
    for style in ('','ThornCorps/StyleOrder/'):
     assert exists(style+path),style+path
 for style in ('ThornWhip/Parts/','ThornCorps/StyleOrder/ThornWhip/Parts/'):
  prefix=style+weapon+'/'
  assert exists(prefix+'Chassis')
  for part in range(15):
   for v in range(5):assert exists(prefix+f'P{part:02d}_V{v}')
  for extra in range(15):assert exists(prefix+f'S{extra:02d}')
for typ in ('Light','Medium','Heavy'):
 for tier in (1,2,3):
  for style in ('','ThornCorps/StyleOrder/'):
   path=style+f'Things/Armor/TC_{typ}_T{tier}'
   assert exists(path)
   for direction in ('north','south','east','west'):
    assert exists(style+f'Things/Armor/Worn/TC_{typ}_T{tier}_{direction}')
for family in ('Holder','Minigun','Laser','Blaster','Railgun','ATGM','MLRS'):
 for sty in ('','ThornCorps/StyleOrder/'):
  for direction in ('north','south','east','west'):
   assert exists(sty+f'ThornCorps/Defense/Turret_{family}_{direction}')
for f in ('TC_Fortifications.xml','TC_Turrets.xml','TT_Benches.xml'):
 for td in ET.parse(D/f).getroot().findall('ThingDef'):
  gd=td.find('graphicData');p=gd.findtext('texPath') if gd is not None else None
  if p and p.startswith(('Things/Buildings/TW_','ThornCorps/Defense/Turret_','ThornCorps/Defense/Fort_','ThornCorps/Defense/Trench_')):
   assert gd.findtext('graphicClass')=='Graphic_Multi',(f,p)
   assert td.findtext('rotatable')=='true',(f,p)
   for direction in ('north','south','east','west'):assert exists(p+'_'+direction),(f,p,direction)
# All linked source textures should load & have non-zero alpha. Pillow also checks truncation.
count=0
for p in T.rglob('*.png'):
 with Image.open(p) as check:check.verify()
 with Image.open(p) as im:
  assert im.mode in ('RGBA','RGB'),str(p)
  assert im.width>4 and im.height>4,str(p)
  if im.mode=='RGBA':assert im.getchannel('A').getbbox(),str(p)
  count+=1
print(f'PASS VISUALS v0.10: {count} readable PNG, {len(maps[0])} native Ideology style mappings per palette, 4 rotation assets for relevant buildings, four modular gun families, 9 armor sets')
print('NOT COVERED: .NET DLL build, CE render runtime, turret top overlap, styled overlay on equipped pawn, TPS')
