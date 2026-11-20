#!/usr/bin/env python3
"""Version 0.11 contract tests; requires Pillow but NOT a RimWorld runtime."""
from pathlib import Path
from PIL import Image
import xml.etree.ElementTree as ET
R=Path(__file__).resolve().parent;M=R/'ThornWhip';D=M/'Defs';T=M/'Textures'
base=ET.parse(D/'TT_Weapons.xml').getroot()
assert len(base)==72
for thing in base:
    name=thing.findtext('defName')
    family='Auto' if name.startswith('TT_Auto_') else 'Pistol' if name.startswith('TT_Pistol_') else 'Launcher' if name.startswith('TT_Launcher_') else 'Rifle'
    assert thing.findtext('graphicData/texPath')=='ThornWhip/Parts/'+family+'/Chassis'
styles=ET.parse(D/'TC_IdeologyStyles.xml').getroot()
for cat in (x for x in styles if x.tag=='StyleCategoryDef'):
    icon=cat.findtext('iconPath');assert icon and (T/(icon+'.png')).is_file()
for sty in (x for x in styles if x.tag=='ThingStyleDef'):
    image=sty.findtext('graphicData/texPath');assert image
    assert (T/(image+'.png')).is_file() or (T/(image+'_south.png')).is_file(),image
for fam in ['Rifle','Auto','Pistol','Launcher']:
    root=T/'ThornWhip/Parts'/fam
    with Image.open(root/'Chassis.png') as im:
        assert im.mode=='RGBA' and im.getchannel('A').getbbox()
    for suffix in ['', '_Order']:
        assert (root/('Chassis'+suffix+'.png')).is_file()
        for i in range(15):
            for j in range(5):
                file=root/(f'P{i:02d}_V{j}{suffix}.png')
                with Image.open(file) as im: assert im.getchannel('A').getbbox(),str(file)
        for i in range(15):
            file=root/(f'S{i:02d}{suffix}.png')
            with Image.open(file) as im: assert im.getchannel('A').getbbox(),str(file)
for bench in ['TW_DesignTable','TW_FactoryTable']:
    for style in ['', '_Order']:
        for direction in ['north','south','east','west']:
            file=T/'Things/Buildings'/f'{bench}{style}_{direction}.png'
            assert file.is_file(),str(file)
for depth in [1,2,3]:
    img=Image.open(T/'ThornCorps/Defense'/f'Trench_{depth}.png').convert('RGBA')
    # Empty dry ditches never contain painted-in cyan water or concrete walls.
    colors=list(img.getdata())
    blue=sum(1 for r,g,b,a in colors if a>100 and b>g*1.35 and b>r*1.35)
    assert blue==0,(depth,blue)
ui=(M/'Source/UI.cs').read_text();comp=(M/'Source/TurretRetrofits.cs').read_text()
assert 'ValidationProblem' in ui and 'previewOrderStyle' in ui
assert 'FilterHostileGizmos' in comp and 'Faction.OfPlayer' in comp
assert 'PostDeSpawn' not in comp
print('PASS 0.11: separated gun graphics, all module variants nonblank, both style icons, rotating benches, dry ditches, hostile turret command gate')
print('NOT TESTED: CE firing / accuracy, native Ideology popup behavior, RimWorld placement/pathing, dynamic world draw, C# compiler and TPS')
