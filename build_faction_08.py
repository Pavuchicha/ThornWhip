#!/usr/bin/env python3
"""Small native faction definition. World-layer names are Odyssey's Surface / Orbit.
No requirement for HugsLib, VFE, Custom Base Framework or other settlement mods.
"""
from pathlib import Path
from xml.etree import ElementTree as ET
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parent; d=root/'ThornWhip/Defs';d.mkdir(exist_ok=True)
def sub(parent,name,value=None,**attrs):
 v=ET.SubElement(parent,name,attrs)
 if value is not None:v.text=str(value)
 return v
def listli(parent,name,values,may=None):
 n=sub(parent,name)
 for item in values:
  attrs={'MayRequire':may} if may and item=='Orbit' else {}
  sub(n,'li',item,**attrs)
 return n
source=ET.Element('Defs')
f=sub(source,'FactionDef',ParentName='OutlanderFactionBase')
for k,v in [
 ('defName','TC_ThornCorps'),('label','Корпус Терна'),
 ('description','Военно-промышленный корпус, контролирующий укреплённые производственные поселения на поверхности и орбитальные заводы. Выпускает модульное оружие и броню собственного стандарта.'),
 ('pawnSingular','служащий Корпуса Терна'),('pawnsPlural','служащие Корпуса Терна'),
 ('leaderTitle','командор производственных крепостей'),
 ('techLevel','Spacer'),('canMakeRandomly','true'),('requiredCountAtGameStart','1'),
 ('maxConfigurableAtWorldCreation','1'),('maxCountAtGameStart','1'),('settlementGenerationWeight','1.1'),
 ('canSiege','true'),('canStageAttacks','true'),
 ('factionIconPath','ThornCorps/Faction/Insignia'),('settlementTexturePath','ThornCorps/Faction/FactoryFort'),
 ('factionNameMaker','NamerFactionOutlander'),('settlementNameMaker','NamerSettlementOutlander'),
 ('basicMemberKind','TC_Operator')]:sub(f,k,v)
listli(f,'layerWhitelist',['Surface','Orbit'],may='Ludeon.RimWorld.Odyssey')
colors=listli(f,'colorSpectrum',['(0.18, 0.28, 0.31)','(0.38, 0.46, 0.47)','(0.12, 0.19, 0.22)'])
# leanest possible maker groups; no non-Thorn pawn kinds
groups=sub(f,'pawnGroupMakers',Inherit='False')
for kind,opts in [('Combat',{'TC_Operator':9,'TC_Engineer':3,'TC_Bulwark':2}),
                  ('Peaceful',{'TC_Engineer':8,'TC_Operator':2}),
                  ('Settlement',{'TC_Operator':7,'TC_Engineer':5,'TC_Bulwark':3})]:
 li=sub(groups,'li');sub(li,'kindDef',kind)
 o=sub(li,'options')
 for pawn,weight in opts.items():sub(o,pawn,weight)
# Faction keeps trade options optional; use known vanilla trader defName
listli(f,'baseTraderKinds',['Base_Outlander_Standard'])
# no forced ideology or xenotypes; independent of Ideology/Biotech
pawnroot=ET.Element('Defs')
parent=sub(pawnroot,'PawnKindDef',Name='TC_BaseHuman',ParentName='OutlanderBase',Abstract='True')
for k,v in [('race','Human'),('defaultFactionType','TC_ThornCorps'),('combatPower','115'),
('apparelAllowHeadgearChance','0'),('weaponMoney','1800~4200'),('apparelMoney','5000~18000'),
('apparelColor','(78, 104, 111)'),('gearHealthRange','0.70~1'),('itemQuality','Normal')]:sub(parent,k,v)
listli(parent,'weaponTags',['TC_Weapon']).set('Inherit','False')
for dn,label,power,weapon_tags,armor_tags in [
 ('TC_Operator','стрелок Терна',105,['TC_Weapon'],['TC_Armor_Light','TC_Armor_Medium']),
 ('TC_Engineer','инженер-гарнизонный Терна',95,['TC_Weapon'],['TC_Armor_Light','TC_Armor_Medium']),
 ('TC_Bulwark','тяжёлый страж Терна',250,['TC_Weapon'],['TC_Armor_Heavy'])]:
 li=sub(pawnroot,'PawnKindDef',ParentName='TC_BaseHuman')
 sub(li,'defName',dn);sub(li,'label',label);sub(li,'combatPower',power)
 listli(li,'weaponTags',weapon_tags).set('Inherit','False')
 listli(li,'apparelTags',armor_tags).set('Inherit','False')
 sub(li,'apparelMoney','5500~18500' if dn=='TC_Bulwark' else '1500~6500')
# add faction-only tags to Things; avoid modifying other mods' defs
weapons=ET.parse(d/'TT_Weapons.xml')
for gun in weapons.getroot().findall('ThingDef'):
 tags=gun.find('weaponTags')
 if tags is not None and not any(x.text=='TC_Weapon' for x in tags):sub(tags,'li','TC_Weapon')
ET.indent(weapons.getroot(),space='  ');weapons.write(d/'TT_Weapons.xml',encoding='utf-8',xml_declaration=True)
armors=ET.parse(d/'TC_Armor.xml')
for armor in armors.getroot().findall('ThingDef'):
 nm=armor.findtext('defName');cl=nm.split('_')[2]; tags=armor.find('./apparel/tags')
 if tags is not None and not any(x.text=='TC_Armor_'+cl for x in tags):sub(tags,'li','TC_Armor_'+cl)
ET.indent(armors.getroot(),space='  ');armors.write(d/'TC_Armor.xml',encoding='utf-8',xml_declaration=True)
for data,name in [(source,'TC_Faction.xml'),(pawnroot,'TC_Pawns.xml')]:
 ET.indent(data,space='  ');ET.ElementTree(data).write(d/name,encoding='utf-8',xml_declaration=True)
# small mod-owned world emblem, no other textures edited
path=root/'ThornWhip/Textures/ThornCorps/Faction';path.mkdir(parents=True,exist_ok=True)
im=Image.new('RGBA',(128,128),(0,0,0,0));dr=ImageDraw.Draw(im)
dr.regular_polygon((64,64,58),6,rotation=30,fill=(26,42,47,255),outline=(124,164,158,255),width=5)
dr.rectangle((35,49,93,85),fill=(49,70,72,255),outline=(219,189,119,255),width=3)
for x in [41,56,71,86]:dr.rectangle((x,42,x+6,51),fill=(219,189,119,255))
for x in [42,57,72]:dr.rectangle((x,68,x+10,83),fill=(20,35,40,255))
dr.line([(65,21),(65,42)],fill=(219,189,119,255),width=6)
dr.polygon([(65,13),(52,30),(78,30)],fill=(219,189,119,255))
im.save(path/'Insignia.png')
# Distinct factory-fort map icon; same asset for Surface/Orbit settlement markers.
mark=Image.new('RGBA',(128,128),(0,0,0,0));g=ImageDraw.Draw(mark)
g.polygon([(12,44),(64,10),(116,44),(116,95),(64,118),(12,95)],fill=(25,46,52,245),outline=(135,169,161,255),width=5)
for x in (23,39,82,98):
 g.rectangle((x,33,x+11,90),fill=(70,94,100,255),outline=(187,194,174,255),width=2)
for x in (25,84):
 g.rectangle((x,20,x+14,36),fill=(48,65,69,255),outline=(212,191,121,255),width=2)
g.rectangle((40,56,88,100),fill=(36,63,67,255),outline=(224,191,117,255),width=3)
for x in (48,60,72):g.rectangle((x,65,x+6,80),fill=(157,212,198,255))
g.line([(64,23),(64,48)],fill=(236,192,98,255),width=5)
mark.save(path/'FactoryFort.png')
print('Thorn Corps faction, 3 pawn kinds, Surface/Orbit layer support, mod-only gear tags')
