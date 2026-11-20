#!/usr/bin/env python3
"""Structure and data integrity tests; DOES NOT compile/launch or prove CE 1.7 API compatibility."""
import sys
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET
from PIL import Image
ROOT=Path(__file__).resolve().parent
MOD=ROOT/'ThornWhip'; DEF=MOD/'Defs'; TEX=MOD/'Textures'
import subprocess
r=subprocess.run([sys.executable,str(ROOT/'tests_static_08.py')],cwd=ROOT,text=True,capture_output=True)
assert r.returncode==0, r.stdout+'\n'+r.stderr
family=json.loads((MOD/'Documentation/defense_catalog.json').read_text(encoding='utf-8'))
turrets=ET.parse(DEF/'TC_Turrets.xml').getroot()
weapons=ET.parse(DEF/'TC_TurretGuns.xml').getroot()
assert len(turrets)==21 and len(weapons)==21,(len(turrets),len(weapons))
assert len(family['turrets'])==7
rangedAmmo={x.findtext('defName') for x in ET.parse(DEF/'TC_EnergyAmmo.xml').getroot().findall('CombatExtended.AmmoSetDef')}
rangedAmmo|={x.findtext('defName') for x in ET.parse(DEF/'TC_RocketAmmo.xml').getroot().findall('CombatExtended.AmmoSetDef')}
rangedAmmo|={x.findtext('defName') for x in ET.parse(DEF/'TC_RailAmmo.xml').getroot().findall('CombatExtended.AmmoSetDef')}
assert rangedAmmo=={'TC_AmmoSet_Laser','TC_AmmoSet_Blaster','TC_AmmoSet_ATGM','TC_AmmoSet_MLRS','TC_AmmoSet_RailHeavy'},rangedAmmo
allGuns={x.findtext('defName'):x for x in weapons};allTowerDefs={x.findtext('defName'):x for x in turrets}
assert len(allGuns)==len(weapons) and len(allTowerDefs)==len(turrets)
referenced=[]
for td in turrets:
 name=td.findtext('defName'); gun=td.findtext('./building/turretGunDef');
 assert gun in allGuns,(name,gun)
 assert td.findtext('thingClass')=='CombatExtended.Building_TurretGunCE'
 assert td.find('./comps/li[@Class="ThornWhip.CompProperties_ThornTurret"]') is not None,name
 assert td.find('./comps/li[@Class="CompProperties_Power"]') is not None,name
 tex=td.findtext('./graphicData/texPath')
 file=TEX/(tex+'.png');assert file.is_file(),file
 Image.open(file).verify();referenced.append(tex)
 assert len(td.findall('building/turretGunDef'))==1
for gun in weapons:
 ammo=gun.findtext('./comps/li[@Class="CombatExtended.CompProperties_AmmoUser"]/ammoSet')
 assert ammo in rangedAmmo or ammo.startswith('AmmoSet_'),(gun.findtext('defName'),ammo)
 assert gun.findtext('./verbs/li/verbClass')=='CombatExtended.Verb_ShootCE'
styles=ET.parse(DEF/'TC_Fortifications.xml').getroot()
assert len(styles)==9,len(styles)
for o in styles:
 name=o.findtext('defName'); path=o.findtext('./graphicData/texPath');assert (TEX/(path+'.png')).exists(),(name,path)
 assert (o.findtext('fillPercent') is not None)
 if name=='TC_Fort_Embrasure':
  assert o.findtext('disableImpassableShotOverConfigError')=='true'
for depth in (1,2,3):
 t=[x for x in styles if x.findtext('defName')=='TC_Trench_'+str(depth)][0]
 assert t.find('./comps/li[@Class="ThornWhip.CompProperties_ThornTrench"]') is not None
jobs=ET.parse(DEF/'TC_DefenseJobs.xml').getroot()
assert len(jobs.findall('JobDef'))==3
assert len(jobs.findall('WorkGiverDef'))==1
assert (MOD/'Source/TurretRetrofits.cs').is_file() and (MOD/'Source/ThornMoats.cs').is_file()
source=(MOD/'Source/TurretRetrofits.cs').read_text()
assert 'SyncHolderGun' in source and 'CompFloatMenuOptions' in source
assert 'TC_retrofitMaterials' in source and 'ThingOwner<Thing>' in source
assert 'ThingOwner' in source and 'WorkGiver_ThornRetrofit' in source
assert (ROOT/'Showcase/THORNCORPS_DEFENSE_0.9.png').is_file()
print('PASS 0.9: prior 0.8 data, 7 families, 21 CE turrets+guns, energy/rocket/rail ammo, 9 fortification defs, artwork references, job framework')
print('NOT COVERED: C# compilation, CE 1.7 game loading, actual beam accuracy, projectile armor mechanics, runtime map water pathfinding and TPS')
