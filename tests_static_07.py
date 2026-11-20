#!/usr/bin/env python3
"""Static consistency only, not a compiler or RimWorld/CE runtime test."""
import json,re,zipfile,math
from pathlib import Path
from xml.etree import ElementTree as ET
from PIL import Image
root=Path(__file__).resolve().parent;mod=root/'ThornWhip';src=mod/'Source'
weapons=json.loads((mod/'Documentation/weapon_families.json').read_text())
armor=json.loads((mod/'Documentation/armor_catalog.json').read_text())
extras=json.loads((mod/'Documentation/special_modules.json').read_text())
assert len(weapons)==4 and len(extras)==15
assert all(len(f['slots'])==15 and all(len(slot['options'])==5 for slot in f['slots']) for f in weapons)
assert all([not x['slots'][i]['required'] for x in weapons for i in (10,13,14)])
assert all(all(s['required'] for s in f['slots'][:10]) for f in weapons)
assert len(armor['families'])==3 and len(armor['specials'])==15
counts=[len(x['slots']) for x in armor['families']];assert counts==[10,13,14],counts
assert all(len(s['options'])==5 for family in armor['families'] for s in family['slots'])
assert sum(counts)*5==185
assert all(len(f['chassis'])==3 for f in armor['families'])
assert [x['family']['key'] for x in weapons]==['Rifle','Auto','Pistol','Launcher']
assert any(a['effects'].get('sharp',0)<0 for a in armor['specials'])
assert any(a['effects'].get('move',0)>0 for a in armor['specials'])
assert any(a['effects'].get('sharp',0)>=18 for a in armor['specials'])
# Not linear in power or component costs; tech locks are explicit.
for f in armor['families']:
 for s in f['slots']:
  assert [x['minTier'] for x in s['options']]==[1,1,2,2,3]
  assert all(x['cost']['ComponentSpacer']==0 for x in s['options'][:2])
  assert all(x['cost']['ComponentSpacer']>0 for x in s['options'][2:])
  assert all(x['effects']['region']==s['region'] for x in s['options'])
assert all(x['effects']['region'] in ['All','Torso','Arm','Leg','Hand','Foot','Head'] for x in armor['specials'])
# Assets: source layers and in-game item/worn art.
for family in armor['families']:
 key=family['key'];path=mod/'Textures/ThornCorps/Armor'/key
 for tier in [1,2,3]:
  ch=next(c for c in family['chassis'] if c['tier']==tier)
  for ext in [path/f'Chassis_T{tier}.png',mod/f'Textures/Things/Armor/TC_{key}_T{tier}.png'] + [mod/f'Textures/Things/Armor/Worn/TC_{key}_T{tier}_{rot}.png' for rot in ['north','south','east']]:
   assert ext.exists(),ext
   with Image.open(ext) as im:assert im.mode=='RGBA'
 for s in family['slots']:
  for v in range(5):
   asset=path/f'P{s["id"]:02}_V{v}.png';assert asset.exists(),asset
   with Image.open(asset) as im:assert im.size==(640,720)
 for v in range(15):assert (path/f'S{v:02}.png').exists()
for f in weapons:
 key=f['family']['key']
 for v in range(5):assert (mod/f'Textures/ThornWhip/Parts/{key}/P14_V{v}.png').exists()
assert (root/'Showcase/THORN_CORPS_9_CHASSIS_0.7.png').exists()
# Definitions: one apparel ThingDef per family/tier, with physically distinct coverage.
a_defs=ET.parse(mod/'Defs/TC_Armor.xml').getroot()
a_recipes=ET.parse(mod/'Defs/TC_ArmorRecipes.xml').getroot()
assert len(a_defs)==9 and len(a_recipes)==10
technology=ET.parse(mod/'Defs/TC_ArmorResearch.xml').getroot()
assert len(technology)==3
assert [x.findtext('defName') for x in technology]==['TC_ArmorTech1','TC_ArmorTech2','TC_ArmorTech3']
assert 'ArmorTechnology.Available' in (src/'ArmorUI.cs').read_text()
names=[]
for d in a_defs:
 name=d.findtext('defName');names.append(name)
 assert d.attrib['ParentName']=='ApparelBase'
 assert d.findtext('thingClass')=='Apparel'
 assert d.findtext('tradeability')=='All'
 assert d.find('./comps/li[@Class="ThornWhip.CompProperties_ArmorDesign"]') is not None
 assert d.find('./modExtensions/li[@Class="CombatExtended.PartialArmorExt"]') is not None
 assert d.findtext('statBases/Bulk') is not None and d.findtext('statBases/WornBulk') is not None
 partgroups=[x.text for x in d.findall('apparel/bodyPartGroups/li')]
 if '_Light_' in name:assert partgroups==['Torso']
 if '_Medium_' in name:assert {'Torso','Arms','Legs','Hands','Feet'}<=set(partgroups) and 'FullHead' in partgroups
 if '_Heavy_' in name:assert {'FullHead','Feet','Neck'} <= set(partgroups)
for rec in list(a_recipes)[1:]:
 assert len(rec.find('products'))==1
 assert rec.find('products')[0].tag in names
 assert rec.find('ingredients') is not None
assert set(x.findtext('defName') for x in list(a_recipes)[1:])=={'TC_Craft_Armor_'+k+'_T'+str(t) for k in ['Light','Medium','Heavy'] for t in (1,2,3)}
benches=ET.parse(mod/'Defs/TT_Benches.xml').getroot()
assert 'TC_DevelopArmor' in [x.text for x in benches[0].findall('recipes/li')]
assert len([x for x in benches[1].findall('recipes/li') if x.text.startswith('TC_Craft_Armor_')])==9
assert len(ET.parse(mod/'Defs/TT_Weapons.xml').getroot())==32
code={p.name:p.read_text() for p in src.glob('*.cs')}
assert len(re.findall(r'new ArmorChassis\(',code['ArmorCatalog.cs']))==9
assert len(re.findall(r'new ArmorSlot\(',code['ArmorCatalog.cs']))==37
assert len(re.findall(r'new ArmorOption\(',code['ArmorCatalog.cs']))==200
assert len(re.findall(r'new ModuleSlot\(',code['WeaponCatalog.cs']))==60
assert 'bool Required' in code['WeaponCatalog.cs']
assert 'TryInstall(harmony)' in code['Events.cs']
assert 'AfterCEPartialArmor' in code['ArmorStatistics.cs']
assert 'OptionalAreaAbsent' in code['ArmorStatistics.cs']
assert 'GameComponent_ArmorLibrary' in code['ArmorBlueprints.cs']
assert 'Bill_ArmorManufacture' in code['Events.cs']
assert 'TC_DevelopArmor' in code['Events.cs']
assert 'ArmorCosts.Refund' in code['QueueUI.cs']
assert 'Dialog_ArmorDesign' in code['BenchComps.cs']
assert 'Dialog_ArmorManufacture' in code['BenchComps.cs']
assert 'ArmorVisuals.DrawPreview' in code['ArmorUI.cs']
assert all('public override void CompTick' not in text for text in code.values())
for fname in ['TT_Benches.xml','TC_Armor.xml','TC_ArmorRecipes.xml','TT_Recipes.xml','TT_Weapons.xml','TT_WorkGivers.xml','TC_ArmorResearch.xml']:
 ET.parse(mod/'Defs'/fname)
assert 'Корпус Терна' in (mod/'About/About.xml').read_text()
assert '<packageId>thornwhip.marksman.rifles</packageId>' in (mod/'About/About.xml').read_text()
print('PASS (STATIC ONLY): 4 weapon families × 15 slots × 5 = 300 variants; 15 weapon specials')
print('PASS (STATIC ONLY): 3 armor classes × 3 tech bases = 9; 37 armor slots × 5 = 185 armor modules; 15 armor specials')
print('PASS (STATIC ONLY): 9 armor XML defs, 10 armor recipes, 239 armor preview layers, 20 rail layers, item and worn graphics')
print('NOT TESTED: .NET compilation, CE 1.7 runtime, body coverage edge cases, worn-per-module renderer, manufacturing, TPS, live trading')
