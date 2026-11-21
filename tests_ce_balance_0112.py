#!/usr/bin/env python3
"""Game-log-derived CE Def preflight + price/balance contract for Thorn Corps 0.11.2.
This is an OFFLINE check. Passing does NOT certify a clean in-game CE injection.
"""
from pathlib import Path
from lxml import etree
import json,re
p=Path(__file__).resolve().parent
mod=p/'ThornWhip'; defs=mod/'Defs'; docs=mod/'Documentation'; src=mod/'Source'
F=json.loads((docs/'weapon_families.json').read_text())
A=json.loads((docs/'armor_catalog.json').read_text())
assert len(F)==4 and len(A['families'])==3
W=etree.parse(str(defs/'TT_Weapons.xml')).getroot().findall('ThingDef');assert len(W)==72
C=etree.parse(str(defs/'TT_Recipes.xml')).getroot().findall('RecipeDef')
G=etree.parse(str(defs/'TC_Armor.xml')).getroot().findall('ThingDef');assert len(G)==9
issues=[]
ce={'Rifle': {'spread':0.05,'range':75,'bulk':11.92},'Auto': {'spread':0.07,'range':55,'bulk':10.03},'Pistol': {'spread':0.17,'range':12,'bulk':2.10}}
for obj in F:
 family=obj['family'];key=family['key']; variants=[x for x in W if x.findtext('defName','').startswith('TT_'+key+'_')];
 if len(variants)!=(16 if key=='Pistol' else 8 if key=='Launcher' else 24):issues.append(key+': variants count invalid')
 for t in variants:
  name=t.findtext('defName');base=t.find('statBases');verb=t.find('verbs/li');work=float(base.findtext('WorkToMake','0'))
  if work!=family['work']:issues.append(name+': work definition disagrees with family')
  if float(base.findtext('MarketValue','0'))!=family['value']:issues.append(name+': price disagrees with catalog')
  if float(base.findtext('SightsEfficiency','0'))!=family['sights']:issues.append(name+': sights differ')
  if float(base.findtext('ShotSpread','0'))!=family['spread']:issues.append(name+': spread differs')
  if float(base.findtext('Bulk','0'))!=family['bulk']:issues.append(name+': bulk differs')
  if float(verb.findtext('warmupTime','0'))!=family['warmup']:issues.append(name+': warmup differs')
  if float(verb.findtext('range','0')) not in family['range']:issues.append(name+': range differs')
  cost=t.find('costList')
  if t.findtext('smeltable')!='true' or cost is None or int(cost.findtext('Steel','0'))<12 or int(cost.findtext('ComponentIndustrial','0'))<2:
   issues.append(name+': legitimate salvage has been suppressed or lacks material basis')
  if t.get('ParentName')!='BaseGun' or t.find('recipeMaker') is not None:
   issues.append(name+': auto recipe bypass risk')
  if t.find('comps/li[@Class="ThornWhip.CompProperties_WeaponDesign"]') is None:
   issues.append(name+': missing blueprint component')
  name_rec='TT_Craft_'+name.split('TT_',1)[1]
  if key=='Rifle': name_rec='TT_Craft_'+name.split('TT_Rifle_',1)[1]
  recs=[r for r in C if r.findtext('defName')==name_rec]
  if len(recs)!=1 or int(recs[0].findtext('workAmount','0'))!=family['work']:
   issues.append(name+': manufacturing recipe workload mismatch')
 if key=='Rifle':
  if not (0.035 <= family['spread']<=.065 and 62<=family['range'][0]<=70 and 8<=family['bulk']<=13):issues.append('Rifle: power out of CE marksman niche')
 if key=='Auto':
  if not (.055<=family['spread']<=.075 and 52<=family['range'][0]<=60 and 8<=family['bulk']<=12):issues.append('Auto: power out of CE assault rifle niche')
 if key=='Pistol':
  if not (.13<=family['spread']<=.17 and 12<=family['range'][0]<=15 and 2<=family['bulk']<=4):issues.append('Pistol: superior CE sidearm must still have reasonable bulk and accuracy')
for obj in A['families']:
 name=obj['key']; chs=obj['chassis']
 for c in chs:
  matching=[x for x in G if x.findtext('defName')==c['defName']]
  if len(matching)!=1:issues.append(name+': missing armor tier '+str(c['tier']));continue
  x=matching[0]
  for stat,key in [('ArmorRating_Sharp','sharp'),('ArmorRating_Blunt','blunt')]:
   if float(x.findtext('statBases/'+stat,'-1'))!=c[key]:issues.append(name+': conflicting armor stats between game and catalog')
  if x.findtext('smeltable')!='true' or x.find('costList') is None:issues.append(name+': salvage was disabled')
  if not x.find('costList').findall('*'):issues.append(name+': empty materials for smelting')
  if c['sharp']>57 or c['blunt']>99:issues.append(name+': tier defense too high')
  if x.find('comps/li[@Class="ThornWhip.CompProperties_ArmorDesign"]') is None:issues.append(name+': dynamic armor comp missing')
# CE explosive implementation must match the upstream 1.7 RPG-style HEAT contract.
rocket=etree.parse(str(defs/'TC_RocketAmmo.xml')).getroot()
projectiles={n.findtext('defName'):n for n in rocket.findall('ThingDef') if n.findtext('defName')}
heat=projectiles['TC_Missile_HEAT']
if heat.findtext('thingClass')!='CombatExtended.BulletCE' or heat.findtext('projectile/damageDef')!='Bullet':
 issues.append('ATGM HEAT must penetrate as CE bullet, not blast-only ProjectileCE_Explosive')
if heat.find('comps/li[@Class="CombatExtended.CompProperties_ExplosiveCE"]') is None:
 issues.append('ATGM HEAT missing separate CE explosive component')
if not 500 <= float(heat.findtext('projectile/armorPenetrationSharp','0')) <= 540:
 issues.append('ATGM HEAT penetration outside calibrated RPG7+ envelope')
for nm in ('TC_Missile_HE','TC_Rocket_HE'):
 x=projectiles[nm]
 if float(x.findtext('projectile/explosionRadius','99'))>2.2:
  issues.append(nm+': uncontrolled heavy blast radius would overpower CE combat')
for nm,low in [('TC_Ammo_ATGM_HEAT',110),('TC_Ammo_ATGM_HE',100),('TC_Ammo_MLRS_HE',65)]:
 if float(projectiles[nm].findtext('statBases/MarketValue','0'))<low:issues.append(nm+': ammo market price below premium cost floor')

# Runtime check against CE's own AmmoBase naming/fields and the two actual Player.logs.
known_classes={'FullMetalJacket','ArmorPiercing','RocketHEAT','GrenadeHE'}
for path in ('TC_EnergyAmmo.xml','TC_RailAmmo.xml','TC_RocketAmmo.xml'):
 tree=etree.parse(str(defs/path))
 for x in tree.getroot().findall('ThingDef'):
  if x.find('ammoClass') is not None:
   if x.get('Class')!='CombatExtended.AmmoDef':issues.append(path+': CE ammo has wrong class')
   if x.findtext('ammoClass') not in known_classes:issues.append(path+': missing CE ammo category '+str(x.findtext('ammoClass')))
   if x.find('graphicData') is None or x.findtext('graphicData/graphicClass')!='Graphic_Single':issues.append(path+': ammo single PNG incompatible with texture class')
  if x.find('menuHidden') is not None and x.get('Class')!='CombatExtended.AmmoDef':issues.append(path+': menuHidden on vanilla ThingDef')
# All 0.11.1 errors remain guarded by that suite; new CE stat and economy clamps must be present in compiled sources.
wcat=(src/'WeaponCatalog.cs').read_text()
acat=(src/'ArmorCatalog.cs').read_text()
for obj in F:
 f=obj['family'];key=f['key'];ln=next((x for x in wcat.splitlines() if x.strip().startswith('new WeaponFamily("'+key+'"')),None)
 if not ln or f'{f["spread"]}f' not in ln and f'{f["spread"]:.3f}f' not in ln:issues.append(key+': UI family catalog stale')
for obj in A['families']:
 for c in obj['chassis']:
  if not re.search(r'"'+re.escape(c['defName'])+r'",'+str(c['tier'])+r',[0-2],'+str(float(c['sharp']))+r'f,'+str(float(c['blunt']))+r'f',acat):
   issues.append(c['defName']+': C# chassis catalog stale')
s=(src/'StatPart_ThornWeapon.cs').read_text();a=(src/'ArmorStatistics.cs').read_text();ui=(src/'UI.cs').read_text()
for label,srccontent,check in [('weapon stat cap',s,'initial * .78f'),('reload cap',s,'initial * .82f'),('economy floor',s,'EconomyBalance.MinimumFinishedValue'),('armor zone cap',a,'baseline*.16f'),('armor economy',a,'EconomyBalance.MinimumFinishedValue'),('weapon UI cap',ui,'family.Spread * .78f')]:
 if check not in srccontent:issues.append('Missing '+label)
if not (src/'EconomyBalance.cs').exists():issues.append('Economy pricing helper missing')
assert not issues,'CE BALANCE PREFLIGHT FAILED:\n'+'\n'.join(issues[:120])
print('PASS 0.11.2: 72 weapons, 9 armor tiers, CE 1.7 ammo XML, real salvage, matching recipes/catalogs, capped enhancements, cost/value floor')
print('NOT VERIFIED: CE 16.7.4 runtime load/ballistics, effective projectile armor, trader price multipliers, save migration, turrets and TPS')
