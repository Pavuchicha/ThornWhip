#!/usr/bin/env python3
"""Generate only 32 base Combat Extended gun defs and 32 manufacturing recipes.
Exact material budget is reserved by WeaponCosts when the player queues the order.
"""
from pathlib import Path
from xml.etree import ElementTree as ET
import itertools,json
ROOT=Path(__file__).parent
D=ROOT/'ThornWhip/Defs'
DATA=json.loads((ROOT/'ThornWhip/Documentation/weapon_families.json').read_text())
def element(parent,name,value=None,**attrs):
 node=ET.SubElement(parent,name,attrs)
 if value is not None:node.text=str(value).lower() if isinstance(value,bool) else str(value)
 return node
def write(root, filename):
 ET.indent(root,space='  ');ET.ElementTree(root).write(D/filename,encoding='utf-8',xml_declaration=True)
def variants():return itertools.product((0,1),repeat=3)
def weapon_name(f,r,b,m):return f'TT_{f["key"]}_R{r}_B{b}_M{m}'
def recipe_name(f,r,b,m):
 base='TT_Craft' if f['key']=='Rifle' else 'TT_Craft_'+f['key']
 return f'{base}_R{r}_B{b}_M{m}'
root=ET.Element('Defs')
for entry in DATA:
 f=entry['family']
 for r,b,m in variants():
  n=element(root,'ThingDef',ParentName='BaseHumanMakeableGun')
  props=[('defName',weapon_name(f,r,b,m)),('label',f['label']),('description',
         f'Персональная марксанская конструкция ({f["caliber"]}). 14 обязательных деталей × пять вариантов и три универсальных слота × 15 улучшений. Боеприпасы и баллистика — Combat Extended.'),
         ('thingClass','ThingWithComps'),('techLevel','Spacer'),('tradeability','All')]
  for key,val in props:element(n,key,val)
  gd=element(n,'graphicData');element(gd,'texPath',f'Things/Weapons/TW_{f["key"]}_R{r}B{b}M{m}')
  element(gd,'graphicClass','Graphic_Single');element(gd,'drawSize','(1.58,0.50)' if f['key']!='Pistol' else '(0.92,0.46)')
  element(n,'uiIconScale','1.1');cats=element(n,'tradeTags');element(cats,'li','WeaponRanged')
  cats=element(n,'thingCategories');element(cats,'li','WeaponsRanged');tags=element(n,'weaponTags')
  for tag in (['GunHeavy','CE_AI_AOE','Gun'] if f['key']=='Launcher' else
              ['CE_Sidearm','CE_AI_Pistol','CE_OneHandedWeapon','Gun'] if f['key']=='Pistol' else ['CE_AI_AR','Gun']):element(tags,'li',tag)
  sb=element(n,'statBases')
  for key,val in [('WorkToMake',f['work']),('MarketValue',f['value']),('Mass',f['mass']),('Bulk',f['bulk']),
                  ('SightsEfficiency',f['sights']),('ShotSpread',f['spread']),('SwayFactor',f['sway']),
                  ('RangedWeapon_Cooldown',f['cooldown']),('CE_RangedWeapon_RecoilMultiplier',1),
                  ('CE_RangedWeapon_ReloadFactor',1),('RangedWeapon_WarmupMultiplier',1),
                  ('RangedWeapon_RangeMultiplier',1),('NightVisionEfficiency_Weapon',.08)]:element(sb,key,val)
  verbs=element(n,'verbs');v=element(verbs,'li',Class='CombatExtended.VerbPropertiesCE')
  verb=[('verbClass','CombatExtended.Verb_ShootCE'),('hasStandardCommand',True),('defaultProjectile',f['projectile']),
        ('warmupTime',f['warmup']),('range',f['range'][b]),('burstShotCount',f['burst'][r]),
        ('ticksBetweenBurstShots',f['between']),('recoilAmount',f['recoil']),('soundCast',f['sound']),
        ('muzzleFlashScale',14 if f['key']=='Launcher' else 9)]
  if f['minRange']:verb.append(('minRange',f['minRange']))
  if f['tail']:verb.append(('soundCastTail',f['tail']))
  if f['key']=='Launcher':verb += [('ai_IsBuildingDestroyer',True),('ignorePartialLoSBlocker',True)]
  for key,val in verb:element(v,key,val)
  tgt=element(v,'targetParams');element(tgt,'canTargetLocations',True)
  comps=element(n,'comps');ammo=element(comps,'li',Class='CombatExtended.CompProperties_AmmoUser')
  element(ammo,'magazineSize',f['magazine'][m]);element(ammo,'reloadTime',f['reload']);element(ammo,'ammoSet',f['ammoSet'])
  fm=element(comps,'li',Class='CombatExtended.CompProperties_FireModes')
  element(fm,'aiUseBurstMode',True if f['key']=='Auto' else False)
  element(fm,'aiAimMode','SuppressFire' if f['key']=='Launcher' else 'AimedShot')
  element(fm,'aimedBurstShotCount',min(f['burst'][r],3))
  element(comps,'li',Class='ThornWhip.CompProperties_WeaponDesign')
write(root,'TT_Weapons.xml')
root=ET.Element('Defs')
research=element(root,'RecipeDef')
for k,val in [('defName','TT_DevelopDesign'),('label','разработать чертёж оружия Терна'),
              ('description','Исследовать оружие одного из четырёх семейств.'),('jobString','разрабатывает оружие Терна'),
              ('workAmount',15000),('workSpeedStat','ResearchSpeed'),('workSkill','Intellectual'),
              ('workSkillLearnFactor',1),('effectWorking','Research')]:element(research,k,val)
ing=element(research,'ingredients');line=element(ing,'li');fil=element(line,'filter');defs=element(fil,'thingDefs');element(defs,'li','Steel');element(line,'count',12)
for entry in DATA:
 f=entry['family']
 for r,b,m in variants():
  rec=element(root,'RecipeDef')
  for k,val in [('defName',recipe_name(f,r,b,m)),('label','собрать оружие Терна (чертёж)'),
        ('description','Стоимость каждой детали внесена в заказ и резервируется при его создании.'),
        ('jobString','собирает оружие Терна'),('workAmount',f['work']),('workSpeedStat','GeneralLaborSpeed'),
        ('workSkill','Crafting'),('effectWorking','Smith')]:element(rec,k,val)
  products=element(rec,'products');element(products,weapon_name(f,r,b,m),1)
  element(rec,'ingredients')
write(root,'TT_Recipes.xml')
root=ET.Element('Defs')
for isdesign in (True,False):
 bench=element(root,'ThingDef',ParentName='BenchBase')
 for key,val in [('defName','TT_DesignTable' if isdesign else 'TT_FactoryTable'),
                 ('label','стол разработки вооружения' if isdesign else 'сборочный верстак Терна'),
                 ('description','Проектирование и исследование модульного оружия.' if isdesign else 'Изготовление по персональным чертежам; ресурсы резервируются при постановке заказа.'),
                 ('thingClass','Building_WorkTable'),('designationCategory','Production'),('hasInteractionCell',True),
                 ('interactionCellOffset','(0,0,-1)'),('size','(2,1)')]:element(bench,key,val)
 gd=element(bench,'graphicData');element(gd,'texPath','Things/Buildings/TW_DesignTable' if isdesign else 'Things/Buildings/TW_FactoryTable');element(gd,'graphicClass','Graphic_Single');element(gd,'drawSize','(2,1)')
 cl=element(bench,'costList');element(cl,'Steel',95 if isdesign else 120);element(cl,'ComponentIndustrial',4 if isdesign else 5)
 pr=element(bench,'researchPrerequisites');element(pr,'li','Gunsmithing')
 sb=element(bench,'statBases');element(sb,'WorkToBuild',9000 if isdesign else 11000);element(sb,'MaxHitPoints',190 if isdesign else 220);element(sb,'Flammability',.40)
 recipes=element(bench,'recipes')
 if isdesign:element(recipes,'li','TT_DevelopDesign')
 else:
  for entry in DATA:
   f=entry['family']
   for r,b,m in variants():element(recipes,'li',recipe_name(f,r,b,m))
 element(bench,'inspectorTabs',Inherit='False')
 comps=element(bench,'comps');element(comps,'li',Class='ThornWhip.CompProperties_DesignTable' if isdesign else 'ThornWhip.CompProperties_FactoryTable')
write(root,'TT_Benches.xml')
print('Generated 32 CE weapon Defs and 32 assembly recipes (not 1920+)')
