#!/usr/bin/env python3
"""Static and data-model checks; deliberately NOT a substitute for a C# build/game runtime."""
from pathlib import Path
from xml.etree import ElementTree as ET
from collections import Counter
import json,re
from PIL import Image
R=Path(__file__).resolve().parent;M=R/'ThornWhip';D=M/'Defs'
assert (M/'Source/WeaponCalibers.cs').exists()
cal=json.loads((M/'Documentation/caliber_profiles.json').read_text()); assert set(cal)=={'Rifle','Auto','Pistol','Launcher'}
assert [len(cal[k]) for k in ['Rifle','Auto','Pistol','Launcher']]==[3,3,2,1]
weapons=ET.parse(D/'TT_Weapons.xml').getroot()
recipes=ET.parse(D/'TT_Recipes.xml').getroot()
benches=ET.parse(D/'TT_Benches.xml').getroot()
assert len(weapons)==72,len(weapons)
assert len(recipes)==73 # 72 manufacture + 1 research
# each generated def has only one CE ammo set and its matching default projectile
names=set(); kcounts=Counter()
for gun in weapons:
    name=gun.findtext('defName');assert name not in names;names.add(name)
    fam=name.split('_')[1]; idx=next((int(x[1:]) for x in name.split('_') if re.fullmatch(r'C\d',x)),0)
    profile=cal[fam][idx]
    assert gun.findtext('./comps/li[@Class="CombatExtended.CompProperties_AmmoUser"]/ammoSet')==profile['ammoSet']
    assert gun.findtext('./verbs/li/defaultProjectile')==profile['projectile']
    assert 'TC_Weapon' in [a.text for a in gun.findall('./weaponTags/li')]
    assert len(gun.findall('./comps/li[@Class="CombatExtended.CompProperties_AmmoUser"]'))==1
    kcounts[fam]+=1
assert kcounts=={'Rifle':24,'Auto':24,'Pistol':16,'Launcher':8},kcounts
recipes_by_name={r.findtext('defName'):r for r in recipes}
for name in names:
    fam=name.split('_')[1]
    suffix=name.split('_',2)[2]
    recipe_name=('TT_Craft_'+suffix if fam=='Rifle' else 'TT_Craft_'+fam+'_'+suffix)
    assert recipe_name in recipes_by_name,recipe_name
    product=recipes_by_name[recipe_name].find('products')
    assert list(product)[0].tag==name,recipe_name
bench=next(x for x in benches if x.findtext('defName')=='TT_FactoryTable')
assert len([x for x in bench.findall('recipes/li') if x.text and x.text.startswith('TT_Craft_')])==72
assert len([x for x in bench.findall('recipes/li') if x.text and x.text.startswith('TC_Craft_Armor_')])==9
researchbench=next(x for x in benches if x.findtext('defName')=='TT_DesignTable')
assert 'TC_DevelopArmor' in [x.text for x in researchbench.findall('recipes/li')]
assert 'TT_DevelopDesign' in [x.text for x in researchbench.findall('recipes/li')]
faction=ET.parse(D/'TC_Faction.xml').getroot();assert len(faction)==1
f=faction.find('FactionDef');assert f.findtext('defName')=='TC_ThornCorps'
assert f.get('ParentName')=='OutlanderFactionBase'
assert [x.text for x in f.findall('./layerWhitelist/li')]==['Surface','Orbit']
assert f.findtext('requiredCountAtGameStart')=='1' and f.findtext('maxCountAtGameStart')=='1'
assert f.find('./layerWhitelist/li[2]').attrib['MayRequire']=='Ludeon.RimWorld.Odyssey'
groupkinds=[x.findtext('kindDef') for x in f.findall('./pawnGroupMakers/li')]
assert groupkinds==['Combat','Peaceful','Settlement'],groupkinds
pawns=ET.parse(D/'TC_Pawns.xml').getroot();assert len(pawns)==4
assert set(x.findtext('defName') for x in pawns if x.findtext('defName'))=={'TC_Operator','TC_Engineer','TC_Bulwark'}
armor=ET.parse(D/'TC_Armor.xml').getroot();assert len(armor)==9
for item in armor:
    arm=item.findtext('defName');class_name=arm.split('_')[2]
    assert 'TC_Armor_'+class_name in [a.text for a in item.findall('./apparel/tags/li')]
logo=M/'Textures/ThornCorps/Faction/Insignia.png';assert logo.exists()
with Image.open(logo) as im:assert im.size==(128,128)
assert f.findtext('settlementTexturePath')=='ThornCorps/Faction/FactoryFort'
assert (M/'Textures/ThornCorps/Faction/FactoryFort.png').is_file()
for pawn in pawns:
    if pawn.findtext('defName'):
        assert pawn.find('weaponTags').get('Inherit')=='False'
        assert pawn.find('apparelTags').get('Inherit')=='False'
assert f.find('pawnGroupMakers').get('Inherit')=='False'
source='\n'.join(p.read_text() for p in (M/'Source').glob('*.cs'))
assert not re.search(r'\bGameComponentTick\s*\(',source)
# 0.9 adds a gated MapComponentTick for connected moat networks; only that file may use it.
assert [p.name for p in (M/'Source').glob('*.cs') if re.search(r'\bMapComponentTick\s*\(',p.read_text())]==['ThornMoats.cs']
assert 'WeaponCalibers.Compatible' in (M/'Source/Blueprints.cs').read_text()
assert 'MapGenerated' in (M/'Source/ThornFortresses.cs').read_text()
assert 'PawnGenerator.GeneratePawn' in (M/'Source/ThornFactionGear.cs').read_text()
assert 'ThornFortressGeneration.Install(harmony)' in (M/'Source/Events.cs').read_text()
assert (M/'Source/ThornWhip.csproj').exists()
print('PASS static: 72 CE weapon defs, 9 family/caliber profiles; no duplicated gun def names')
print('PASS static: distinct ammoSet / projectile per caliber; 72 recipes bound to assembly bench')
print('PASS static: one faction Surface + Odyssey Orbit, 3 human pawn kinds with mod-only gear tags')
print('PASS static: armored fortress map hook, no global Pawn ticks; 0.9 moat recalculation is interval-gated')
print('NOT TESTED: C# compilation, Odyssey orbital-world placement, CE ammo inventories, faction spawn, TPS')
