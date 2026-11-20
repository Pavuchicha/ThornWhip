#!/usr/bin/env python3
"""Runtime-log-derived 1.7 preflight. Data validation only, not game-load verification."""
from pathlib import Path
from lxml import etree
from collections import Counter
import re
root=Path(__file__).resolve().parent
mod=root/'ThornWhip'
defs=mod/'Defs'
allfiles={p.name:etree.parse(str(p)).getroot() for p in defs.glob('*.xml')}
issues=[]
names=Counter()
for fn,d in allfiles.items():
    for node in d.findall('ThingDef'):
        name=node.findtext('defName')
        if not name:continue
        names[name]+=1
        if name[-1].isdigit():issues.append(f'{fn}: ThingDef {name} ends with digit')
        if node.find('menuHidden') is not None:issues.append(f'{fn}: ThingDef {name} uses invalid menuHidden field')
        for comp in node.findall('./comps/li'):
            if comp.get('Class')=='CompProperties_Quality':issues.append(f'{fn}: {name} uses invalid CompProperties_Quality')
        if node.find('ammoClass') is not None or node.find('cookOffProjectile') is not None:
            if node.get('Class')!='CombatExtended.AmmoDef':issues.append(f'{fn}: {name} CE ammo lacks AmmoDef class')
            if node.findtext('ammoClass')=='GrenadeHEAT':issues.append(f'{fn}: {name} GrenadeHEAT category unresolved in CE')
        graphic=node.find('graphicData')
        if graphic is not None and name.startswith('TC_Ammo_'):
            if graphic.findtext('graphicClass')!='Graphic_Single':issues.append(f'{fn}: {name} uses unbundled Graphic_StackCount textures')
        if node.findtext('smeltable')=='true' and node.find('costList') is None and node.find('costStuffCount') is None:
            issues.append(f'{fn}: {name} can smelt without a defined resource yield')
        if node.get('ParentName')=='BaseHumanMakeableGun' and node.find('costList') is None and node.find('costStuffCount') is None:
            issues.append(f'{fn}: {name} inherits a bill recipe without cost')
        if node.findtext('passability')=='Impassable' and float(node.findtext('fillPercent','1'))<1 and node.findtext('disableImpassableShotOverConfigError')!='true':
            issues.append(f'{fn}: {name} impassable building can be shot over')
        if node.get('ParentName')=='BaseGun' and node.findtext('smeltable')!='false' and name.startswith('TC_Gun_'):
            issues.append(f'{fn}: {name} turret gun has inherited smeltable setting')
assert all(c==1 for c in names.values()),'Duplicate definitions: '+str([n for n,c in names.items() if c>1])
about=etree.parse(str(mod/'About/About.xml')).getroot()
if about.find('downloadUrl') is not None:issues.append('About.xml uses unsupported top-level downloadUrl')
for n in allfiles['TC_Pawns.xml'].findall('PawnKindDef'):
    if n.get('Name')=='TC_BaseHuman' and (n.find('initialWillRange') is None or n.find('initialResistanceRange') is None):
        issues.append('TC_BaseHuman missing initialWillRange/initialResistanceRange')
for key in ['TC_AmmoSet_Laser','TC_AmmoSet_Blaster','TC_AmmoSet_RailHeavy','TC_AmmoSet_ATGM','TC_AmmoSet_MLRS']:
    ammo_sets=[n for r in allfiles.values() for n in r.findall('CombatExtended.AmmoSetDef') if n.findtext('defName')==key]
    if len(ammo_sets)!=1:issues.append(f'{key}: missing or duplicate ammo set')
    for ammo in ammo_sets:
        for li in ammo.findall('./ammoTypes/*'):
            if li.tag not in names:issues.append(f'{key}: missing custom ammo {li.tag}')
            if li.text not in names:issues.append(f'{key}: missing custom projectile {li.text}')

# Core runtime constructs the names of the ThingDef and the RecipeDef dynamically.
# Both must use the same suffix as their rewritten definitions or no blueprints can be manufactured.
catalog=(mod/'Source/WeaponCatalog.cs').read_text(encoding='utf-8')
if catalog.count('b.CaliberId) + "_Core";')!=2:
    issues.append('WeaponCatalog dynamic def and recipe names must end with _Core')

assert not issues,'\n'.join(issues)
print(f'PASS runtime 0.11.1: {len(names)} ThingDefs, 5 CE ammo sets, no known XML/Config errors from Player.log')
print('NOT VERIFIED: CE DLL semantics, save migration, runtime turret/ammo behavior, map generation, TPS')
