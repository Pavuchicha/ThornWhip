"""Generate deterministic Thorn Corps defense defs (0.9). Run from project root.
This generator creates source XML only; game-load validation still requires the real CE 1.7 runtime.
"""
from pathlib import Path
from xml.etree import ElementTree as E
import json
ROOT=Path(__file__).resolve().parent
MOD=ROOT/'ThornWhip'; DEF=MOD/'Defs'

def sub(p,key,val=None,**kwargs):
    e=E.SubElement(p,key,kwargs)
    if val is not None:e.text=str(val)
    return e

def pretty(root,path):
    E.indent(root,space='  ')
    E.ElementTree(root).write(path, encoding='utf-8', xml_declaration=True)

# 7 physical platform families. Each has at least one baseline, upgrades are combinations of body+gun profiles.
FAMILIES=[
 dict(id='Holder',name='держатель вооружения',size=1,hp=310,power=90,steel=100,plasteel=10,industrial=4,adv=0,tech='Industrial',research='Gunsmithing',profiles=[('Empty', 'TC_Gun_HolderDummy', 'пустая рама')]),
 dict(id='Minigun',name='роторная пулемётная турель',size=2,hp=500,power=410,steel=195,plasteel=35,industrial=8,adv=2,tech='Spacer',research='HeavyTurrets',profiles=[('56x4','TC_Gun_Minigun_56x4','5,56 / 4 ствола'),('56x6','TC_Gun_Minigun_56x6','5,56 / 6 стволов'),('762x6','TC_Gun_Minigun_762x6','7,62 / 6 стволов'),('762x8','TC_Gun_Minigun_762x8','7,62 / 8 стволов'),('20x6','TC_Gun_Minigun_20x6','20 мм / 6 стволов')]),
 dict(id='Laser',name='лазерная турель',size=2,hp=450,power=650,steel=175,plasteel=55,industrial=6,adv=5,tech='Spacer',research='ChargedShot',profiles=[('Focus','TC_Gun_Laser_Focus','фокусирующая линза'),('Cooling','TC_Gun_Laser_Cooling','криоконтур'),('Pulse','TC_Gun_Laser_Pulse','быстрый импульс')]),
 dict(id='Blaster',name='бластерная турель',size=2,hp=520,power=790,steel=210,plasteel=65,industrial=8,adv=6,tech='Spacer',research='ChargedShot',profiles=[('Scatter','TC_Gun_Blaster_Scatter','рассеивание'),('Pierce','TC_Gun_Blaster_Pierce','бронебойный пакет'),('Fury','TC_Gun_Blaster_Fury','скоростной пакет')]),
 dict(id='Railgun',name='рейлган',size=2,hp=750,power=1250,steel=280,plasteel=95,industrial=12,adv=8,tech='Ultra',research='Fabrication',profiles=[('Light','TC_Gun_Railgun_Light','лёгкий'),('Medium','TC_Gun_Railgun_Medium','средний'),('Heavy','TC_Gun_Railgun_Heavy','тяжёлый')]),
 dict(id='ATGM',name='автоматическая ПТУР',size=2,hp=440,power=360,steel=210,plasteel=40,industrial=8,adv=3,tech='Spacer',research='CE_Launchers',profiles=[('HEAT','TC_Gun_ATGM_HEAT','ПТУР / HEAT или HE'),('Dual','TC_Gun_ATGM_Dual','двойная пусковая'),('Guided','TC_Gun_ATGM_Guided','улучшенное сопровождение')]),
 dict(id='MLRS',name='пакетная РСЗО',size=3,hp=700,power=450,steel=335,plasteel=75,industrial=13,adv=4,tech='Spacer',research='CE_Launchers',profiles=[('Light','TC_Gun_MLRS_Light','облегчённый блок'),('Swarm','TC_Gun_MLRS_Swarm','залп 12 ракет'),('Heavy','TC_Gun_MLRS_Heavy','утяжелённый блок')]),
]
GUNS={
'TC_Gun_HolderDummy': ('AmmoSet_556x45mmNATO','Bullet_556x45mmNATO_FMJ',1,1,8,0,0.45,1,0.5,0.8),
'TC_Gun_Minigun_56x4':('AmmoSet_556x45mmNATO','Bullet_556x45mmNATO_FMJ',55,10,62,1.0,0.18,4,1.3,0.2),
'TC_Gun_Minigun_56x6':('AmmoSet_556x45mmNATO','Bullet_556x45mmNATO_FMJ',62,16,90,1.15,0.22,3,1.5,0.25),
'TC_Gun_Minigun_762x6':('AmmoSet_762x51mmNATO','Bullet_762x51mmNATO_FMJ',64,12,75,1.6,0.24,5,1.6,0.4),
'TC_Gun_Minigun_762x8':('AmmoSet_762x51mmNATO','Bullet_762x51mmNATO_FMJ',65,18,125,2.0,0.26,4,1.8,0.45),
'TC_Gun_Minigun_20x6':('AmmoSet_20x128mmOerlikon','Bullet_20x128mmOerlikon_AP',73,7,42,2.3,0.21,9,2.2,0.85),
'TC_Gun_Laser_Focus':('TC_AmmoSet_Laser','TC_Beam_Standard',58,1,36,1.6,0.001,1,0.05,0.1),
'TC_Gun_Laser_Cooling':('TC_AmmoSet_Laser','TC_Beam_Standard',58,1,55,1.05,0.001,1,0.05,0.1),
'TC_Gun_Laser_Pulse':('TC_AmmoSet_Laser','TC_Beam_Standard',54,3,48,1.3,0.004,7,0.07,0.2),
'TC_Gun_Blaster_Scatter':('TC_AmmoSet_Blaster','TC_Bolt_Standard',50,5,65,1.7,0.12,5,0.15,0.4),
'TC_Gun_Blaster_Pierce':('TC_AmmoSet_Blaster','TC_Bolt_Piercing',57,3,48,2.0,0.065,8,0.1,0.4),
'TC_Gun_Blaster_Fury':('TC_AmmoSet_Blaster','TC_Bolt_Standard',43,8,85,1.7,0.2,3,0.2,0.5),
'TC_Gun_Railgun_Light':('AmmoSet_762x51mmNATO','Bullet_762x51mmNATO_FMJ',85,1,20,2.5,0.025,8,0.4,1.8),
'TC_Gun_Railgun_Medium':('AmmoSet_20x128mmOerlikon','Bullet_20x128mmOerlikon_AP',106,1,12,4.4,0.018,12,0.6,3.8),
'TC_Gun_Railgun_Heavy':('TC_AmmoSet_RailHeavy','TC_Slug_Rail30',128,1,8,6.0,0.014,18,0.7,5.0),
'TC_Gun_ATGM_HEAT':('TC_AmmoSet_ATGM','TC_Missile_HEAT',92,1,4,5.0,0.024,10,0.2,4),
'TC_Gun_ATGM_Dual':('TC_AmmoSet_ATGM','TC_Missile_HEAT',91,2,6,6.0,0.035,14,0.3,4),
'TC_Gun_ATGM_Guided':('TC_AmmoSet_ATGM','TC_Missile_HEAT',100,1,6,5.5,0.008,10,0.2,5),
'TC_Gun_MLRS_Light':('TC_AmmoSet_MLRS','TC_Rocket_HE',88,6,24,5.5,0.7,6,0.75,4),
'TC_Gun_MLRS_Swarm':('TC_AmmoSet_MLRS','TC_Rocket_HE',90,12,48,6.8,0.85,5,0.85,4),
'TC_Gun_MLRS_Heavy':('TC_AmmoSet_MLRS','TC_Rocket_HE',105,9,36,7.3,0.9,6,0.8,4),
}

def emit_guns():
    root=E.Element('Defs')
    for name,(ammo,proj,ran,burst,mag,reload,spread,between,sway,cooldown) in GUNS.items():
        gun=E.SubElement(root,'ThingDef',{'ParentName':'BaseGun_CE'})
        sub(gun,'defName',name);sub(gun,'label',name.replace('TC_Gun_','').replace('_',' '))
        sub(gun,'description','Внутренний CE-механизм «Корпуса Терна». Боеприпасы, перезарядка и баллистика управляются CE.')
        sub(gun,'thingClass','ThingWithComps');sub(gun,'tradeability','None')
        g=sub(gun,'graphicData');sub(g,'texPath','ThornCorps/Defense/GunMount');sub(g,'graphicClass','Graphic_Single')
        tags=sub(gun,'weaponTags');sub(tags,'li','TurretGun')
        stats=sub(gun,'statBases');sub(stats,'Mass','12');sub(stats,'Bulk','20');sub(stats,'SightsEfficiency','1.9' if 'Railgun' in name or 'ATGM' in name else '1.1');sub(stats,'ShotSpread',spread);sub(stats,'SwayFactor',sway);sub(stats,'RangedWeapon_Cooldown',cooldown)
        verbs=sub(gun,'verbs');v=E.SubElement(verbs,'li',{'Class':'CombatExtended.VerbPropertiesCE'});sub(v,'verbClass','CombatExtended.Verb_ShootCE');sub(v,'hasStandardCommand','true');sub(v,'defaultProjectile',proj);sub(v,'warmupTime','1.2' if 'Minigun' in name else '2.1');sub(v,'range',ran);sub(v,'burstShotCount',burst);sub(v,'ticksBetweenBurstShots',between);sub(v,'recoilAmount','0.2' if 'Laser' in name else '1.7');sub(v,'soundCast','Shot_ChargeRifle' if 'Laser' in name or 'Blaster' in name else 'Shot_AssaultRifle');sub(v,'muzzleFlashScale','12');sub(v,'soundCastTail','GunTail_Heavy')
        if 'ATGM' in name or 'MLRS' in name:sub(v,'minRange','12')
        tp=sub(v,'targetParams');sub(tp,'canTargetLocations','true')
        comps=sub(gun,'comps');a=E.SubElement(comps,'li',{'Class':'CombatExtended.CompProperties_AmmoUser'});sub(a,'magazineSize',mag);sub(a,'reloadTime',reload);sub(a,'ammoSet',ammo)
        fm=E.SubElement(comps,'li',{'Class':'CombatExtended.CompProperties_FireModes'});sub(fm,'aiUseBurstMode','true');sub(fm,'aiAimMode','AimedShot')
    pretty(root,DEF/'TC_TurretGuns.xml')

def emit_turrets():
    root=E.Element('Defs')
    for family in FAMILIES:
        for pnum,(profile,gun,desc) in enumerate(family['profiles']):
            specialSize=(2 if profile=='Light' else 3 if profile=='Medium' else 4) if family['id']=='Railgun' else family['size']
            suffix='' if pnum==0 else '_'+profile
            defname='TC_Turret_'+family['id']+suffix
            b=E.SubElement(root,'ThingDef',{'ParentName':'BuildingBase'})
            sub(b,'defName',defname);sub(b,'label',family['name']+(' — '+desc if pnum else ''))
            sub(b,'description','Тяжёлый промышленный оборонительный комплекс. Модификации требуют ресурсов, доставки материалов и строительных работ. CE-боеприпасы и баллистика.')
            sub(b,'category','Building');sub(b,'thingClass','CombatExtended.Building_TurretGunCE');sub(b,'tickerType','Normal');sub(b,'techLevel',family['tech']);sub(b,'tradeability','None')
            if pnum==0:sub(b,'designationCategory','Security')
            if pnum>0:sub(b,'menuHidden','true')
            size=specialSize;sub(b,'size',f'({size},{size})');sub(b,'rotatable','false');sub(b,'passability','PassThroughOnly');sub(b,'fillPercent','0.78');sub(b,'altitudeLayer','Building');sub(b,'terrainAffordanceNeeded','Medium');sub(b,'drawerType','MapMeshAndRealTime');sub(b,'selectable','true');sub(b,'leaveResourcesWhenKilled','true')
            sub(b,'constructionSkillPrerequisite',5 if family['id'] in ('Holder','Minigun') else 9)
            graphics=sub(b,'graphicData');sub(graphics,'texPath','ThornCorps/Defense/Turret_'+family['id']+(('_'+profile) if pnum>0 else ''));sub(graphics,'graphicClass','Graphic_Single');sub(graphics,'drawSize',f'({size},{size})')
            stats=sub(b,'statBases');sub(stats,'MaxHitPoints',family['hp']);sub(stats,'WorkToBuild',15000+3000*(size-1));sub(stats,'Mass',80*size);sub(stats,'Flammability','0.06');sub(stats,'ShootingAccuracyTurret','1.0');sub(stats,'Beauty','-3')
            cost=sub(b,'costList');sub(cost,'Steel',family['steel']);sub(cost,'ComponentIndustrial',family['industrial']);
            if family['plasteel']:sub(cost,'Plasteel',family['plasteel'])
            if family['adv']:sub(cost,'ComponentSpacer',family['adv'])
            bb=sub(b,'building');sub(bb,'turretGunDef',gun);sub(bb,'turretTopDrawSize',size);sub(bb,'turretBurstCooldownTime','1.3' if family['id'] in ('Minigun','Blaster') else '3');sub(bb,'ai_combatDangerous','true');sub(bb,'combatPower','35' if family['id']=='Holder' else str(75+30*size))
            cw=sub(b,'comps'); E.SubElement(cw,'li',{'Class':'ThornWhip.CompProperties_ThornTurret'}); power=E.SubElement(cw,'li',{'Class':'CompProperties_Power'});sub(power,'compClass','CompPowerTrader');sub(power,'basePowerConsumption',family['power']+(size-family['size'])*480);E.SubElement(cw,'li',{'Class':'CompProperties_Flickable'});E.SubElement(cw,'li',{'Class':'CompProperties_Breakdownable'})
            workers=sub(b,'placeWorkers');sub(workers,'li','PlaceWorker_ShowTurretRadius');sub(workers,'li','PlaceWorker_TurretTop')
            research=sub(b,'researchPrerequisites');sub(research,'li',family['research'])
    pretty(root,DEF/'TC_Turrets.xml')

def emit_energy_ammo():
    root=E.Element('Defs')
    for spec in [dict(id='Laser',label='лазерные конденсаторные кассеты',items=[('Standard','TC_Beam_Standard',14,0.2)],steel=10,plas=2,comps=1),dict(id='Blaster',label='бластерные плазмокассеты',items=[('Standard','TC_Bolt_Standard',18,1.8),('Piercing','TC_Bolt_Piercing',14,8.0)],steel=12,plas=5,comps=1)]:
        id=spec['id']; category=sub(root,'ThingCategoryDef');sub(category,'defName','TC_Ammo'+id);sub(category,'label',spec['label']);sub(category,'parent','AmmoAdvanced')
        ammoset=sub(root,'CombatExtended.AmmoSetDef');sub(ammoset,'defName','TC_AmmoSet_'+id);sub(ammoset,'label',spec['label']);at=sub(ammoset,'ammoTypes')
        for suf,bullet,dmg,pen in spec['items']:sub(at,'TC_Ammo_'+id+'_'+suf,bullet)
        base=E.SubElement(root,'ThingDef',{'Name':'TC_Ammo'+id+'Base','ParentName':'SmallAmmoBase','Abstract':'True'});sub(base,'description',spec['label']);stat=sub(base,'statBases');sub(stat,'Mass','.08');sub(stat,'Bulk','.08');sub(stat,'MarketValue','4.2');tags=sub(base,'tradeTags');sub(tags,'li','CE_AutoEnableTrade');categorylist=sub(base,'thingCategories');sub(categorylist,'li','TC_Ammo'+id);sub(base,'stackLimit',300)
        for suffix,bullet,dmg,pen in spec['items']:
            ab=E.SubElement(root,'ThingDef',{'ParentName':'TC_Ammo'+id+'Base'});sub(ab,'defName','TC_Ammo_'+id+'_'+suffix);sub(ab,'label',spec['label']+' '+suffix.lower());gd=sub(ab,'graphicData');sub(gd,'texPath','ThornCorps/Defense/Ammo_'+id);sub(gd,'graphicClass','Graphic_StackCount');sub(ab,'ammoClass','FullMetalJacket' if id=='Laser' else 'ArmorPiercing');sub(ab,'cookOffProjectile',bullet)
            projectile=E.SubElement(root,'ThingDef',{'ParentName':'BaseBullet'});sub(projectile,'defName',bullet);sub(projectile,'label',id+' '+suffix);gd=sub(projectile,'graphicData');sub(gd,'texPath','ThornCorps/Defense/Projectile_'+id);sub(gd,'graphicClass','Graphic_Single');pj=E.SubElement(projectile,'projectile',{'Class':'CombatExtended.ProjectilePropertiesCE'});sub(pj,'damageDef','Burn' if id=='Laser' else 'Bullet');sub(pj,'speed',300 if id=='Laser' else 180);sub(pj,'damageAmountBase',dmg);sub(pj,'armorPenetration',pen)
            # Explicit fixed recipe avoids reliance on auto-register heuristics on CE 1.7.
            recipe=E.SubElement(root,'RecipeDef',{'ParentName':'AdvancedAmmoRecipeBase'});sub(recipe,'defName','TC_MakeAmmo_'+id+'_'+suffix);sub(recipe,'label','производить '+spec['label']+' ('+suffix+')');sub(recipe,'jobString','Сборка энергокассет...');ings=sub(recipe,'ingredients')
            for thing,n in [('Steel',spec['steel']),('Plasteel',spec['plas']),('ComponentIndustrial',spec['comps'])]:
                li=sub(ings,'li');f=sub(li,'filter');ts=sub(f,'thingDefs');sub(ts,'li',thing);sub(li,'count',n)
            fixed=sub(recipe,'fixedIngredientFilter');defs=sub(fixed,'thingDefs');[sub(defs,'li',k) for k in ('Steel','Plasteel','ComponentIndustrial')]
            prods=sub(recipe,'products');sub(prods,'TC_Ammo_'+id+'_'+suffix,50);sub(recipe,'workAmount',4000)
    pretty(root,DEF/'TC_EnergyAmmo.xml')

def emit_rail_ammo():
    root=E.Element('Defs')
    cat=sub(root,'ThingCategoryDef');sub(cat,'defName','TC_AmmoRail30');sub(cat,'label','электромагнитные сердечники 30 мм');sub(cat,'parent','AmmoHighCaliber')
    ammo=sub(root,'CombatExtended.AmmoSetDef');sub(ammo,'defName','TC_AmmoSet_RailHeavy');sub(ammo,'label','30 мм электромагнитный сердечник')
    tags=sub(ammo,'ammoTypes');sub(tags,'TC_Ammo_Rail30','TC_Slug_Rail30')
    item=E.SubElement(root,'ThingDef',{'Class':'CombatExtended.AmmoDef','ParentName':'MediumAmmoBase'});sub(item,'defName','TC_Ammo_Rail30');sub(item,'label','электромагнитный сердечник 30 мм')
    gd=sub(item,'graphicData');sub(gd,'texPath','ThornCorps/Defense/Ammo_Railgun');sub(gd,'graphicClass','Graphic_StackCount')
    stat=sub(item,'statBases');sub(stat,'Mass','.58');sub(stat,'Bulk','.75');sub(stat,'MarketValue','16')
    catlist=sub(item,'thingCategories');sub(catlist,'li','TC_AmmoRail30')
    trade=sub(item,'tradeTags');sub(trade,'li','CE_AutoEnableTrade');sub(item,'stackLimit','100');sub(item,'ammoClass','ArmorPiercing');sub(item,'cookOffProjectile','TC_Slug_Rail30')
    projectile=E.SubElement(root,'ThingDef',{'ParentName':'BaseBullet'});sub(projectile,'defName','TC_Slug_Rail30');sub(projectile,'label','магнитный сердечник 30 мм')
    gd=sub(projectile,'graphicData');sub(gd,'texPath','ThornCorps/Defense/Projectile_Railgun');sub(gd,'graphicClass','Graphic_Single')
    proj=E.SubElement(projectile,'projectile',{'Class':'CombatExtended.ProjectilePropertiesCE'});sub(proj,'damageDef','Bullet');sub(proj,'speed',320);sub(proj,'damageAmountBase',52);sub(proj,'armorPenetration',38)
    r=E.SubElement(root,'RecipeDef',{'ParentName':'AdvancedAmmoRecipeBase'});sub(r,'defName','TC_MakeAmmo_Rail30');sub(r,'label','изготовить 30-мм сердечники');sub(r,'jobString','Точение сердечников...')
    ingredients=sub(r,'ingredients')
    for thing,qty in [('Steel',70),('Uranium',8),('ComponentIndustrial',2)]:
        li=sub(ingredients,'li');f=sub(li,'filter');defs=sub(f,'thingDefs');sub(defs,'li',thing);sub(li,'count',qty)
    fixed=sub(r,'fixedIngredientFilter');defs=sub(fixed,'thingDefs')
    for thing in ['Steel','Uranium','ComponentIndustrial']:sub(defs,'li',thing)
    products=sub(r,'products');sub(products,'TC_Ammo_Rail30',25);sub(r,'workAmount',7200)
    pretty(root,DEF/'TC_RailAmmo.xml')

def emit_rocket_ammo():
    root=E.Element('Defs')
    specs=[
       ('ATGM','ПТУР Терна','AmmoMissiles', [('HEAT','TC_Missile_HEAT',"GrenadeHEAT",175,2.3,11),('HE','TC_Missile_HE',"GrenadeHE",135,4.3,4)]),
       ('MLRS','Ракеты Терна','AmmoRockets',[('HE','TC_Rocket_HE',"GrenadeHE",92,3.7,3)])
    ]
    for family,label,category,ammo in specs:
        cat=sub(root,'ThingCategoryDef');sub(cat,'defName','TC_Category_'+family);sub(cat,'label',label);sub(cat,'parent',category)
        aa=sub(root,'CombatExtended.AmmoSetDef');sub(aa,'defName','TC_AmmoSet_'+family);sub(aa,'label',label)
        types=sub(aa,'ammoTypes')
        for suffix,proj,ammoClass,damage,radius,ap in ammo:sub(types,'TC_Ammo_'+family+'_'+suffix,proj)
        for suffix,proj,ammoClass,damage,radius,ap in ammo:
            item=E.SubElement(root,'ThingDef',{'Class':'CombatExtended.AmmoDef','ParentName':'MediumAmmoBase'})
            sub(item,'defName','TC_Ammo_'+family+'_'+suffix);sub(item,'label',label+' ('+suffix+')');sub(item,'description','Одноразовая управляемая ракета для оборонительных систем Корпуса Терна.')
            gd=sub(item,'graphicData');sub(gd,'texPath','ThornCorps/Defense/Ammo_'+family);sub(gd,'graphicClass','Graphic_StackCount')
            stats=sub(item,'statBases');sub(stats,'Mass',3.4 if family=='ATGM' else 2.1);sub(stats,'Bulk',4.0);sub(stats,'MarketValue',23)
            catlist=sub(item,'thingCategories');sub(catlist,'li','TC_Category_'+family)
            tags=sub(item,'tradeTags');sub(tags,'li','CE_AutoEnableTrade');sub(item,'stackLimit',24);sub(item,'ammoClass',ammoClass)
            projectile=E.SubElement(root,'ThingDef',{'ParentName':'BaseExplosiveBullet'})
            sub(projectile,'defName',proj);sub(projectile,'label',label+' / '+suffix);sub(projectile,'thingClass','CombatExtended.ProjectileCE_Explosive')
            gd=sub(projectile,'graphicData');sub(gd,'texPath','ThornCorps/Defense/Projectile_'+family);sub(gd,'graphicClass','Graphic_Single')
            px=E.SubElement(projectile,'projectile',{'Class':'CombatExtended.ProjectilePropertiesCE'})
            sub(px,'speed',72 if family=='ATGM' else 42);sub(px,'damageDef','Bomb');sub(px,'damageAmountBase',damage)
            sub(px,'explosionRadius',radius);sub(px,'armorPenetration',ap);sub(px,'soundExplode','MortarBomb_Explode')
            sub(px,'applyDamageToExplosionCellsNeighbors','true')
            r=E.SubElement(root,'RecipeDef',{'ParentName':'AdvancedAmmoRecipeBase'});sub(r,'defName','TC_MakeAmmo_'+family+'_'+suffix);sub(r,'label','собрать '+label+' ('+suffix+')');sub(r,'jobString','Изготовление ракет Терна...')
            ings=sub(r,'ingredients')
            resources=[('Steel',14),('ComponentIndustrial',2),('Chemfuel',5)]
            if family=='ATGM':resources.append(('Plasteel',6))
            for thing,num in resources:
                li=sub(ings,'li');f=sub(li,'filter');defs=sub(f,'thingDefs');sub(defs,'li',thing);sub(li,'count',num)
            fixed=sub(r,'fixedIngredientFilter');ds=sub(fixed,'thingDefs')
            for thing,num in resources:sub(ds,'li',thing)
            prod=sub(r,'products');sub(prod,'TC_Ammo_'+family+'_'+suffix,4);sub(r,'workAmount',6500)
    pretty(root,DEF/'TC_RocketAmmo.xml')

def emit_forts():
    root=E.Element('Defs')
    for key,label,fill,passab,size,cost,hp in [
      ('ReinforcedWall','армированная стена Терна',1.0,'Impassable',1,45,850),
      ('Embrasure','амбразура Терна',0.68,'Impassable',1,45,440),
      ('Bunker','модульный бастион Терна',0.90,'Impassable',1,85,850),
      ('Sandbag','инженерная огневая позиция',0.44,'PassThroughOnly',1,30,220),
      ('Foxhole','окоп Терна',0.29,'Standable',1,15,180),
      ('ArmoredGate','ворота укреплённого завода',0.92,'Impassable',1,90,900),
    ]:
        thing=E.SubElement(root,'ThingDef',{'ParentName':'BuildingBase'});sub(thing,'defName','TC_Fort_'+key);sub(thing,'label',label);sub(thing,'description','Укрепление Корпуса Терна с массивными бронеплитами и датчиками. Амбразуры предназначены для огня сквозь укрытие; их CE-LoS требует отдельного теста.')
        sub(thing,'category','Building');sub(thing,'thingClass','Building');sub(thing,'designationCategory','Security');sub(thing,'altitudeLayer','Building');sub(thing,'passability',passab);sub(thing,'fillPercent',fill);sub(thing,'size',f'({size},{size})');sub(thing,'terrainAffordanceNeeded','Light');sub(thing,'holdsRoof',str(key in ('ReinforcedWall','ArmoredGate')).lower());sub(thing,'leaveResourcesWhenKilled','true')
        gd=sub(thing,'graphicData');sub(gd,'texPath','ThornCorps/Defense/Fort_'+key);sub(gd,'graphicClass','Graphic_Single');sub(gd,'drawSize',f'({size},{size})')
        stats=sub(thing,'statBases');sub(stats,'MaxHitPoints',hp);sub(stats,'WorkToBuild',4500);sub(stats,'Flammability','0.05')
        co=sub(thing,'costList');sub(co,'Steel',cost)
        if key in ('Bunker','ArmoredGate'):sub(co,'ComponentIndustrial',3)
        sub(thing,'constructionSkillPrerequisite',4)
        if key=='Embrasure':
            sub(thing,'disableImpassableShotOverConfigError','true')
            sub(thing,'blockLight','false')
            sub(thing,'coversFloor','true')
    for depth in (1,2,3):
        t=E.SubElement(root,'ThingDef',{'ParentName':'BuildingBase'});sub(t,'defName','TC_Trench_'+str(depth));sub(t,'label','ров Терна — глубина '+str(depth));sub(t,'description','Разработанная траншея глубины '+str(depth)+'. При подключении к водоёму связанные рвы заполняются. Глубина 3 после затопления становится непроходимой.')
        sub(t,'category','Building');sub(t,'thingClass','Building');sub(t,'designationCategory','Security');sub(t,'altitudeLayer','Floor');sub(t,'passability','Standable');sub(t,'fillPercent','0');sub(t,'terrainAffordanceNeeded','Light');sub(t,'tickerType','Rare')
        gd=sub(t,'graphicData');sub(gd,'texPath','ThornCorps/Defense/Trench_'+str(depth));sub(gd,'graphicClass','Graphic_Single')
        stats=sub(t,'statBases');sub(stats,'MaxHitPoints',220+depth*100);sub(stats,'WorkToBuild',4500+depth*4500);sub(stats,'Flammability','0')
        cost=sub(t,'costList');sub(cost,'Steel',12+depth*12)
        comp=sub(t,'comps');E.SubElement(comp,'li',{'Class':'ThornWhip.CompProperties_ThornTrench'})
    pretty(root,DEF/'TC_Fortifications.xml')

if __name__=='__main__':
    emit_guns();emit_turrets();emit_energy_ammo();emit_rocket_ammo();emit_rail_ammo();emit_forts()
    js={'turrets':FAMILIES,'guns':{k:{'ammoSet':v[0],'projectile':v[1],'range':v[2],'burst':v[3],'magazine':v[4]} for k,v in GUNS.items()}, 'status':'Uncompiled. Energy projectile profiles approximate; perfect-hit continuous CE beams pending runtime integration.'}
    (MOD/'Documentation'/'defense_catalog.json').write_text(json.dumps(js,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Defense defs generated:',sum(len(x['profiles']) for x in FAMILIES),'turret defs /',len(GUNS),'gun defs')
