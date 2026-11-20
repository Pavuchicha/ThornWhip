#!/usr/bin/env python3
"""Regenerate CE ThingDefs from 0.7 base, expand calibers without breaking 0.7 defNames.
The C suffix appears only for alternative cartridges. The CE AmmoUser class is chosen by
immutable ThingDef; never mutate AmmoUser/verb defs when equipping a weapon.
"""
from pathlib import Path
import json, subprocess
import xml.etree.ElementTree as ET
root=Path(__file__).resolve().parent
# base generator from 0.6 references preserved graphics; always make old base defs first
subprocess.run(['python',str(root/'build_defs_06.py')],check=True,cwd=root)
cal=json.loads((root/'ThornWhip/Documentation/caliber_profiles.json').read_text())
def read(name):return ET.parse(root/'ThornWhip/Defs'/name)
guns=read('TT_Weapons.xml');recipes=read('TT_Recipes.xml');benches=read('TT_Benches.xml')
base_defs=list(guns.getroot());rec_by_name={r.findtext('defName'):r for r in recipes.getroot().findall('RecipeDef')}
def clone(x):return ET.fromstring(ET.tostring(x))
for gun in base_defs:
  dn=gun.findtext('defName');fam=dn.split('_')[1]
  for idx,profile in enumerate(cal[fam][1:],1):
    g=clone(gun);new=dn+'_C'+str(idx);g.find('defName').text=new
    g.find('description').text='Корпус Терна: сменный калибр '+profile['name']+' с заводской конверсией патронника, затвора и магазина. CE контролирует баллистику.'
    g.find('./comps/li[@Class="CombatExtended.CompProperties_AmmoUser"]/ammoSet').text=profile['ammoSet']
    g.find('./verbs/li/defaultProjectile').text=profile['projectile']
    recoil=g.find('./verbs/li/recoilAmount');recoil.text=str(round(float(recoil.text)*profile['recoil'],3))
    magazine=g.find('./comps/li[@Class="CombatExtended.CompProperties_AmmoUser"]/magazineSize')
    magazine.text=str(max(1,round(int(magazine.text)*profile['magMultiplier'])))
    mass=g.find('./statBases/Mass');mass.text=str(round(float(mass.text)+profile['mass'],3))
    guns.getroot().append(g)
    # Existing naming: Rifle has TT_Craft_R..., others TT_Craft_<family>_R...
    original='TT_Craft_'+dn.removeprefix('TT_') if fam!='Rifle' else 'TT_Craft_'+dn.split('_',2)[2]
    recipe=rec_by_name[original]
    rr=clone(recipe); newrec=original+'_C'+str(idx);rr.find('defName').text=newrec
    for item in rr.find('products'):item.tag=new
    recipes.getroot().append(rr)
    factory=next(b for b in benches.getroot().findall('ThingDef') if b.findtext('defName')=='TT_FactoryTable')
    ET.SubElement(factory.find('recipes'),'li').text=newrec
# Re-attach all armor R&D/crafting bills. The legacy gun generator resets TT_Benches.
armor_recipes=read('TC_ArmorRecipes.xml')
factory=next(b for b in benches.getroot().findall('ThingDef') if b.findtext('defName')=='TT_FactoryTable')
designer=next(b for b in benches.getroot().findall('ThingDef') if b.findtext('defName')=='TT_DesignTable')
known_factory={x.text for x in factory.findall('recipes/li')}
for a in armor_recipes.getroot().findall('RecipeDef'):
    name=a.findtext('defName')
    if name=='TC_DevelopArmor':
        if name not in [x.text for x in designer.findall('recipes/li')]: ET.SubElement(designer.find('recipes'),'li').text=name
    elif name and name not in known_factory:
        ET.SubElement(factory.find('recipes'),'li').text=name
for tree,name in [(guns,'TT_Weapons.xml'),(recipes,'TT_Recipes.xml'),(benches,'TT_Benches.xml')]:
 ET.indent(tree.getroot(),space='  ');tree.write(root/'ThornWhip/Defs'/name,encoding='utf-8',xml_declaration=True)
print('Caliber expansion:',len(guns.getroot()),'weapon defs; alternative profiles:',sum(len(v)-1 for v in cal.values()))
