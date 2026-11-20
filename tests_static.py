#!/usr/bin/env python3
"""Static/integration-free validation: honest about zero runtime testing.
    Rebuilds are deterministic; tests assert CE XML constraints, assets and C# data paths.
"""
from pathlib import Path
from xml.etree import ElementTree as ET
from PIL import Image
import json,re,itertools
root=Path(__file__).parent;mod=root/'ThornWhip'
DATA=json.loads((mod/'Documentation/weapon_families.json').read_text())
assert len(DATA)==4
KEYS=['Rifle','Auto','Pistol','Launcher']
assert [x['family']['key'] for x in DATA]==KEYS
assert all(len(x['slots'])==14 and all(len(z['options'])==2 for z in x['slots']) for x in DATA)

def parse(name):return ET.parse(mod/'Defs'/name).getroot()
weapons=parse('TT_Weapons.xml');recipes=parse('TT_Recipes.xml');benches=parse('TT_Benches.xml');wg=parse('TT_WorkGivers.xml')
assert len(weapons)==32,len(weapons)
assert len(recipes)==1921,len(recipes)
assert len(benches)==2 and len(wg)==2
assert '1.7' in (mod/'LoadFolders.xml').read_text()
assert 'CETeam.CombatExtended' in (mod/'About/About.xml').read_text()
parts=mod/'Textures/ThornWhip/Parts';fallback=mod/'Textures/Things/Weapons'
slot_layer_count=0
weapon_names=set()
for entry in DATA:
 f=entry['family'];key=f['key'];assets=parts/key
 assert assets.is_dir(),assets
 for name in ['Chassis.png']+[f'P{i:02}_V{v}.png' for i in range(14) for v in range(2)]+[f'S{j:02}.png' for j in range(9)]:
  path=assets/name;assert path.exists(),path
  with Image.open(path) as img:
   assert img.size==(1024,320) and img.mode=='RGBA'
  slot_layer_count+=1
 for r,b,m in itertools.product([0,1],repeat=3):
  name=f'TT_{key}_R{r}_B{b}_M{m}';weapon_names.add(name)
  assert (fallback/f'TW_{key}_R{r}B{b}M{m}.png').exists()
 for slot in entry['slots']:
  assert len(set(z['name'] for z in slot['options']))==2
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
 assert not any(x.tag.startswith('Accuracy_') for x in w.find('statBases'))
 if fam['key']=='Launcher':
  assert w.findtext('./verbs/li/minRange')=='5'
  assert w.findtext('./verbs/li/ai_IsBuildingDestroyer')=='true'
 if fam['key']=='Pistol':assert 'CE_Sidearm' in [x.text for x in w.findall('./weaponTags/li')]
rec_names=set()
for rec in list(recipes)[1:]:
 name=rec.findtext('defName');assert name not in rec_names;rec_names.add(name)
 mat=re.fullmatch(r'TT_Craft(?:_(Auto|Pistol|Launcher))?_R([01])_B([01])_M([01])_P(\d+)_S([0-3])',name)
 assert mat,name
 short,rr,bb,ma,p,s=mat.groups();key=short or 'Rifle';rr=int(rr);bb=int(bb);ma=int(ma);p=int(p);s=int(s)
 assert p<=14
 fam=next(x['family'] for x in DATA if x['family']['key']==key)
 assert rec.findtext('./products/*')=='1'
 assert rec.find('products')[0].tag==f'TT_{key}_R{rr}_B{bb}_M{ma}'
 ing={i.findtext('./filter/thingDefs/li'):int(i.findtext('count')) for i in rec.findall('./ingredients/li')}
 assert ing['Steel']==round(fam['mass']*13+16)+(14-p)*2
 assert ing.get('Plasteel',0)==p*8
 assert ing['ComponentIndustrial']==fam['component']+s
assert len(rec_names)==1920
assert len(benches[1].findall('./recipes/li'))==1920
assert 'TT_DevelopDesign' in [v.text for v in benches[0].findall('./recipes/li')]
code={p.name:p.read_text() for p in (mod/'Source').glob('*.cs')}
assert 'FamilyId = FamilyId' in code['Blueprints.cs']
assert 'Scribe_Values.Look(ref FamilyId' in code['Blueprints.cs']
assert 'WeaponCatalog.RequiredFor(b)' in code['WeaponTuning.cs']
assert 'WeaponCatalog.Families.Length' in code['UI.cs']
assert 'WeaponCatalog.IsOurWeapon' in code['Events.cs']
assert 'WeaponCatalog.Family(b.FamilyId).Key + "/Chassis"' in code['WeaponVisuals.cs']
assert '3 universal optional slots' in code['Blueprints.cs']
assert 'Specials' in code['WeaponCatalog.cs']
assert len(re.findall(r'new SpecialModule\(',code['WeaponCatalog.cs']))==9
assert len(re.findall(r'new ModuleSlot\(',code['WeaponCatalog.cs']))==56
for name,text in code.items():
 assert 'public override void CompTick' not in text
 assert 'public override void GameComponentTick' not in text
 assert 'CompTickRare' not in text
# no reflection patches of CE shooting, CE projectile or damage classes
assert 'CombatExtended.Verb_ShootCE' not in code['Events.cs']
assert (root/'Showcase/THORNWHIP_FOUR_FAMILIES_0.5.png').exists()
print(f'PASS STATIC: {len(DATA)} families, {56*2} core choices, {3} universal extras from 9 candidates, {len(weapons)} CE weapon defs, {len(rec_names)} recipes, {slot_layer_count} family textures, {len(list(fallback.glob("TW_*_R*B*M*.png")))} fallback sprites')
print('NOT VERIFIED: C# compilation, full CE 1.7 API, loaded game, live TPS, recoil/overlay behaviour in-game')
