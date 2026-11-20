#!/usr/bin/env python3
"""Static consistency checks: intentionally do not claim compiled or in-game correctness."""
from pathlib import Path
from xml.etree import ElementTree as ET
from PIL import Image
import json,re,itertools
root=Path(__file__).parent;mod=root/'ThornWhip'
DATA=json.loads((mod/'Documentation/weapon_families.json').read_text())
SPECIAL=json.loads((mod/'Documentation/special_modules.json').read_text())
assert len(DATA)==4 and len(SPECIAL)==15
assert all(len(x['slots'])==14 and all(len(z['options'])==5 for z in x['slots']) for x in DATA)
assert len({sp['name'] for sp in SPECIAL})==15
assert all('cost' in option and 'effects' in option for x in DATA for slot in x['slots'] for option in slot['options'])
assert any(op['cost']['advanced']>0 for x in DATA for sl in x['slots'] for op in sl['options'])
assert all(op['cost']['advanced']==0 for x in DATA for sl in x['slots'] for op in sl['options'][:1])
def parse(name):return ET.parse(mod/'Defs'/name).getroot()
weapons=parse('TT_Weapons.xml');recipes=parse('TT_Recipes.xml');benches=parse('TT_Benches.xml');wg=parse('TT_WorkGivers.xml')
assert len(weapons)==32,len(weapons)
assert len(recipes)==33,len(recipes)
assert len(benches)==2 and len(wg)==2
assert '1.7' in (mod/'LoadFolders.xml').read_text()
assert 'CETeam.CombatExtended' in (mod/'About/About.xml').read_text()
parts=mod/'Textures/ThornWhip/Parts';fallback=mod/'Textures/Things/Weapons'
slot_layer_count=0;weapon_names=set()
for entry in DATA:
 f=entry['family'];key=f['key'];assets=parts/key
 assert assets.is_dir(),assets
 for name in ['Chassis.png']+[f'P{i:02}_V{v}.png' for i in range(14) for v in range(5)]+[f'S{j:02}.png' for j in range(15)]:
  path=assets/name;assert path.exists(),path
  with Image.open(path) as img:assert img.size==(1024,320) and img.mode=='RGBA'
  slot_layer_count+=1
 for r,b,m in itertools.product([0,1],repeat=3):
  name=f'TT_{key}_R{r}_B{b}_M{m}';weapon_names.add(name)
  assert (fallback/f'TW_{key}_R{r}B{b}M{m}.png').exists()
 for slot in entry['slots']:
  assert len(set(z['name'] for z in slot['options']))==5
for w in weapons:
 name=w.findtext('defName');assert name in weapon_names
 fam=next(x['family'] for x in DATA if name.startswith(f'TT_{x["family"]["key"]}_'))
 mm=re.fullmatch(r'TT_(Rifle|Auto|Pistol|Launcher)_R([01])_B([01])_M([01])',name);assert mm
 _,rr,bb,ma=mm.groups();rr=int(rr);bb=int(bb);ma=int(ma)
 assert w.findtext('./verbs/li/verbClass')=='CombatExtended.Verb_ShootCE'
 assert w.findtext('./verbs/li/defaultProjectile')==fam['projectile']
 assert w.findtext('./verbs/li/burstShotCount')==str(fam['burst'][rr])
 assert w.findtext('./verbs/li/range')==str(fam['range'][bb])
 assert w.findtext('./comps/li[@Class="CombatExtended.CompProperties_AmmoUser"]/ammoSet')==fam['ammoSet']
 assert w.findtext('./comps/li[@Class="CombatExtended.CompProperties_AmmoUser"]/magazineSize')==str(fam['magazine'][ma])
 assert w.find('./comps/li[@Class="ThornWhip.CompProperties_WeaponDesign"]') is not None
 assert w.find('./comps/li[@Class="CombatExtended.CompProperties_FireModes"]') is not None
 assert w.findtext('./graphicData/texPath')+'.png' in {str(p.relative_to(mod/'Textures')) for p in fallback.glob('*.png')}
 assert w.findtext('tradeability')=='All'
 if fam['key']=='Launcher':assert w.findtext('./verbs/li/minRange')=='5'
 if fam['key']=='Pistol':assert 'CE_Sidearm' in [x.text for x in w.findall('./weaponTags/li')]
rec_names=set()
for rec in list(recipes)[1:]:
 name=rec.findtext('defName');assert name not in rec_names;rec_names.add(name)
 mat=re.fullmatch(r'TT_Craft(?:_(Auto|Pistol|Launcher))?_R([01])_B([01])_M([01])',name);assert mat,name
 key=mat.group(1) or 'Rifle';rr,bb,ma=map(int,mat.groups()[1:])
 assert rec.find('products')[0].tag==f'TT_{key}_R{rr}_B{bb}_M{ma}'
 assert rec.find('ingredients') is not None and len(rec.find('ingredients'))==0
assert len(rec_names)==32
assert len(benches[1].findall('./recipes/li'))==32
code={p.name:p.read_text() for p in (mod/'Source').glob('*.cs')}
assert 'CoreIndex(int i)' in code['Blueprints.cs']
assert 'WeaponCatalog.RequiredFor(b)' in code['WeaponTuning.cs']
assert 'Scribe_Values.Look(ref FamilyId' in code['Blueprints.cs']
assert 'WeaponCatalog.Families.Length' in code['UI.cs']
assert 'TryPrepay(' in code['UI.cs'] and 'Refund(' in code['QueueUI.cs']
assert 'ComponentSpacer' in code['WeaponCosts.cs']
assert 'GenRecipe.MakeRecipeProducts' in code['Events.cs']
assert 'WeaponCatalog.Family(b.FamilyId).Key + "/Chassis"' in code['WeaponVisuals.cs']
assert len(re.findall(r'new SpecialModule\(',code['WeaponCatalog.cs']))==15
assert len(re.findall(r'new ModuleSlot\(',code['WeaponCatalog.cs']))==56
for name,text in code.items():
 assert 'public override void CompTick' not in text
 assert 'public override void GameComponentTick' not in text
 assert 'CompTickRare' not in text
assert 'CombatExtended.Verb_ShootCE' not in code['Events.cs']
assert (root/'Showcase/THORNWHIP_FIVE_OPTIONS_0.6.png').exists()
assert ('generate_code_06.py' in (root/'.github/workflows/build.yml').read_text())
print(f'PASS STATIC: 4 families, 56 core slots x 5 = 280 choices, 3 flexible slots / 15 specials, {len(weapons)} CE defs, {len(rec_names)} crafting recipes, {slot_layer_count} texture layers, {len(list(fallback.glob("TW_*_R*B*M*.png")))} base sprites')
print('NOT VERIFIED: actual .NET build, CE 1.7 API, live in-game materials, save/reload, visuals on equipped pawns and TPS')
