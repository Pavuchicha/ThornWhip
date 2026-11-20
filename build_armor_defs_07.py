#!/usr/bin/env python3
"""Emit nine CE-compatible fixed coverage chassis + one research bill + nine crafting bills."""
from pathlib import Path
from xml.etree import ElementTree as E
import json
R=Path(__file__).parent
D=R/'ThornWhip/Defs'
data=json.loads((R/'ThornWhip/Documentation/armor_catalog.json').read_text())
root=E.Element('Defs');recipes=E.Element('Defs')
def a(parent,tag,val):return E.SubElement(parent,tag).__setattr__('text',str(val))
def group(parent,tag,items):
 el=E.SubElement(parent,tag)
 for i in items:a(el,'li',i)
 return el
for family in data['families']:
 key=family['key'];fid=['Light','Medium','Heavy'].index(key)
 for ch in family['chassis']:
  t=ch['tier']
  d=E.SubElement(root,'ThingDef',ParentName='ApparelBase')
  for tag,val in [('defName',ch['defName']),('label',ch['label']),('description',f"Корпус Терна: модульная броня {key} технологического класса Т{t}. Сложная индивидуальная конструкция, защита зон и нагрузка CE рассчитываются по установленным деталям."),('thingClass','Apparel'),('techLevel',('Industrial','Spacer','Ultra')[t-1]),('tradeability','All'),('generateCommonality','0.14' if t<3 else '0.025'),('smeltable','true')]:a(d,tag,val)
  g=E.SubElement(d,'graphicData');a(g,'texPath',f'Things/Armor/TC_{key}_T{t}');a(g,'graphicClass','Graphic_Single');a(g,'drawSize','(1.0,1.0)')
  group(d,'thingCategories',['ApparelArmor']);group(d,'tradeTags',['Armor'])
  stats=E.SubElement(d,'statBases')
  for tag,val in [('MaxHitPoints',int(ch['price']*.13+140)),('WorkToMake',8500*(t+fid+1)),('MarketValue',ch['price']),('Mass',ch['mass']),('Bulk',ch['bulk']),('WornBulk',ch['wornBulk']),('ArmorRating_Sharp',ch['sharp']),('ArmorRating_Blunt',ch['blunt']),('ArmorRating_Heat',ch['heat']),('Insulation_Cold',8+10*t+5*fid),('Insulation_Heat',3+4*t+4*fid),('EquipDelay',2+fid*3+t*1.5),('Flammability','0.1' if t>1 else '0.35')]:a(stats,tag,val)
  apparel=E.SubElement(d,'apparel');a(apparel,'wornGraphicPath',f'Things/Armor/Worn/TC_{key}_T{t}')
  groups=family['coverage'].copy()
  # CE bodyPartGroups are static; optional Medium gloves and boots have zero dynamic protection
  # until equipped, enforced by the CE PartialStat postfix in ArmorProtection.
  group(apparel,'bodyPartGroups',groups)
  layers=['Shell'] if fid<2 else ['Shell','Overhead']
  group(apparel,'layers',layers)
  group(apparel,'tags',['SpacerMilitary' if t>1 else 'IndustrialMilitary']);group(apparel,'defaultOutfitTags',['Soldier'])
  a(apparel,'useDeflectMetalEffect','true')
  comps=E.SubElement(d,'comps');E.SubElement(comps,'li',Class='CompProperties_Quality');E.SubElement(comps,'li',Class='ThornWhip.CompProperties_ArmorDesign')
  # Fixed joint vulnerability, separate from optional module region modifiers.
  ext=E.SubElement(d,'modExtensions');part=E.SubElement(ext,'li',Class='CombatExtended.PartialArmorExt');st=E.SubElement(part,'stats')
  region_factors={0:[('Torso',1.0)],1:[('Arm',.75),('Leg',.84),('Hand',.25),('Foot',.25),('Head',.69)],2:[('Arm',.88),('Leg',.90),('Hand',.56),('Foot',.62),('Head',.72),('Neck',.50)]}[fid]
  for region,mult in region_factors:
   if mult>=1:continue
   for v in ['Sharp','Blunt']:
    entry=E.SubElement(st,'li');a(entry,'ArmorRating_'+v,mult)
    group(entry,'parts',[region])
  rd=E.SubElement(recipes,'RecipeDef');a(rd,'defName',f'TC_Craft_Armor_{key}_T{t}');a(rd,'label','собрать броню Терна по чертежу')
  a(rd,'description','Списание ресурсов по составу чертежа выполняется при создании заказа.')
  a(rd,'jobString','собирает броню Корпуса Терна');a(rd,'workAmount',10000*(t+fid+1))
  a(rd,'workSpeedStat','GeneralLaborSpeed');a(rd,'workSkill','Crafting');a(rd,'effectWorking','Smith')
  products=E.SubElement(rd,'products');a(products,ch['defName'],1)
  E.SubElement(rd,'ingredients')
research=E.Element('RecipeDef')
for tag,val in [('defName','TC_DevelopArmor'),('label','разработать проект брони Корпуса Терна'),('jobString','разрабатывает бронесистему Терна'),('workAmount',20000),('workSpeedStat','ResearchSpeed'),('workSkill','Intellectual'),('effectWorking','Research')]:a(research,tag,val)
ingredients=E.SubElement(research,'ingredients');el=E.SubElement(ingredients,'li');flt=E.SubElement(el,'filter');group(flt,'thingDefs',['Steel']);a(el,'count',20)
recipes.insert(0,research)
D.mkdir(parents=True,exist_ok=True)
for name,node in [('TC_Armor.xml',root),('TC_ArmorRecipes.xml',recipes)]:
 try:E.indent(node,space='  ')
 except AttributeError:pass
 E.ElementTree(node).write(D/name,encoding='unicode',xml_declaration=True)
# Append recipes only if absent, to preserve other users' bench assignments.
bench=D/'TT_Benches.xml';s=bench.read_text(encoding='utf-8')
s=s.replace('<li>TT_DevelopDesign</li>','<li>TT_DevelopDesign</li>\n      <li>TC_DevelopArmor</li>') if '<li>TC_DevelopArmor</li>' not in s else s
if '<li>TC_Craft_Armor_Light_T1</li>' not in s:
 token='    </recipes>'
 start=s.index('<defName>TT_FactoryTable</defName>')
 end=s.index(token,start)
 inject='\n'.join('      <li>TC_Craft_Armor_'+x['key']+'_T'+str(t)+'</li>' for x in data['families'] for t in (1,2,3))+'\n'
 s=s[:end]+inject+s[end:]
bench.write_text(s,encoding='utf-8')
print('Armor defs and recipes:',len(root),len(recipes))
