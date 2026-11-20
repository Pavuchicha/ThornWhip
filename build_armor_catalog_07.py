#!/usr/bin/env python3
"""Generates reproducible and explicit Thorn Corps armor module data and C# catalog."""
from pathlib import Path
import json
R=Path(__file__).parent; doc=R/'ThornWhip/Documentation'; src=R/'ThornWhip/Source'
classes=[
 dict(key='Light',label='Лёгкий жилет',short='ЖИЛЕТ',coverage=['Torso'],base=[(7,12,.09,6,7,2,-.08,170),(13,24,.18,5.2,6.6,1.7,.04,600),(22,38,.29,4.3,5.9,1.1,.13,1700)],slots=[
 ('Баллистическая подкладка','Torso',1),('Передняя плита','Torso',1),('Задняя плита','Torso',1),('Подвесная система','All',1),('Боковые плиты','Torso',0),('Противоосколочный фартук','Torso',0),('Травматический демпфер','Torso',0),('Термовкладыш','All',0),('Кабельный жгут','All',0),('Навесной каркас','All',0)]),
 dict(key='Medium',label='Штурмовой комплект',short='ШТУРМ',coverage=['Torso','Arms','Legs','Hands','Feet','FullHead'],base=[(10,19,.12,21,25,6,-.47,340),(22,39,.26,18,24,5,-.20,1150),(36,60,.40,15,21,3.5,.08,2800)],slots=[
 ('Защитный поддоспешник','All',1),('Нагрудная плита','Torso',1),('Спинная плита','Torso',1),('Плечевые панели','Arm',1),('Брюшной пакет','Torso',1),('Бедренные панели','Leg',1),('Несущая разгрузка','All',1),('Наколенники','Leg',0),('Налокотники','Arm',0),('Перчатки','Hand',0),('Ботинки','Foot',0),('Система вентиляции','All',0),('Баллистический шлем','Head',0)]),
 dict(key='Heavy',label='Экзоскафандр',short='ЭКЗОСКАФ',coverage=['Torso','Arms','Legs','Hands','Feet','FullHead','Neck'],base=[(15,29,.18,78,95,29,-1.32,870),(35,64,.38,54,75,17,-.38,3200),(65,110,.56,42,64,11,.12,8900)],slots=[
 ('Силовой каркас','All',1),('Энергоблок','All',1),('Центральная бронекапсула','Torso',1),('Спинной бронеблок','Torso',1),('Шлем и гермоконтур','Head',1),('Приводы плеча','Arm',1),('Приводы ног','Leg',1),('Кистевые кожухи','Hand',1),('Защита стоп','Foot',1),('Накладные плиты корпуса','Torso',0),('Гаситель ударных импульсов','All',0),('Дополнительные сервоприводы','All',0),('Охлаждающий модуль','All',0),('Спинная грузовая рама','All',0)])
]
# Five options per physical slot; not a linear power/cost ladder.
styles=[
 dict(prefix='Серийный',tier=1,sh=.6,bl=1.2,heat=0,mass=.30,bulk=.25,worn=.05,move=-.012,carry=0,cbulk=0,cost=(4,1,0,0),value=12),
 dict(prefix='Упрощённый',tier=1,sh=.05,bl=.5,heat=0,mass=-.32,bulk=-.19,worn=-.12,move=.012,carry=0,cbulk=0,cost=(2,0,0,0),value=6),
 dict(prefix='Упрочнённый',tier=2,sh=2.1,bl=4.2,heat=.01,mass=.95,bulk=.55,worn=.25,move=-.027,carry=0,cbulk=0,cost=(7,2,1,0),value=65),
 dict(prefix='Композитный',tier=2,sh=1.4,bl=2.8,heat=.02,mass=-.45,bulk=-.22,worn=-.13,move=.021,carry=0,cbulk=0,cost=(3,2,2,0),value=105),
 dict(prefix='Метаматериальный',tier=3,sh=3.5,bl=6.4,heat=.04,mass=-.75,bulk=-.35,worn=-.17,move=.031,carry=0,cbulk=0,cost=(2,3,5,8),value=360),
]
# Slot-specific modifiers: armor plate adds protection, harness trades carrying, actuation trades speed etc.
variants=[]
for fam in classes:
 slotjson=[]
 for index,(name,region,required) in enumerate(fam['slots']):
  opts=[]
  for j,v in enumerate(styles):
   plate=('плита' in name.lower() or 'панел' in name.lower() or 'кожух' in name.lower() or 'брон' in name.lower() or 'защита' in name.lower())
   power=any(t in name.lower() for t in ('привод','каркас','энергоблок','вентиляц','охлажден','жгут','рама','разгруз','подвес'))
   isall=region=='All'
   protection_mult=1.30 if plate else .65 if power else 1.0
   sharp=round(v['sh']*protection_mult,3) if not isall else round(v['sh']*.34,3)
   blunt=round(v['bl']*protection_mult,3) if not isall else round(v['bl']*.34,3)
   move=round(v['move']*(1.7 if power else .55),4)
   carry = (2,5,9,8,15)[j] if power else 0
   cbulk = (0.3,0.5,1.3,1.0,2.8)[j] if power else 0
   if fam['key']=='Heavy' and power: move+= (0.07,0.14,0.10,0.20,0.32)[j]
   if fam['key']=='Light' and plate: move-= .012 if j in (2,4) else 0
   w=v['cost']; factor=3 if fam['key']=='Heavy' else 2 if fam['key']=='Medium' else 1
   cost={'Steel':w[0]*factor,'ComponentIndustrial':w[1]*(2 if power else 1),'ComponentSpacer':w[2]*(2 if fam['key']=='Heavy' else 1),'Gold':w[3]}
   effect=dict(sharp=sharp,blunt=blunt,heat=v['heat'],mass=round(v['mass']*(1.8 if fam['key']=='Heavy' else 1.35 if fam['key']=='Medium' else 1),3),bulk=v['bulk'],wornBulk=v['worn'],move=round(move,3),carry=carry,carryBulk=cbulk,value=v['value']*(2 if fam['key']=='Heavy' else 1),region=region)
   opts.append(dict(id=f'{fam["key"]}_{index:02}_V{j}',name=f'{v["prefix"]} — {name.lower()}',minTier=v['tier'],cost=cost,effects=effect))
  slotjson.append(dict(id=index,label=name,region=region,required=bool(required),options=opts))
 fam['slots']=slotjson
 variants.extend(slotjson)
specialnames=[
 ('Реактивный усилитель сервоприводов','All',2,dict(move=.42,wornBulk=1.3,mass=3.1,carry=8)),
 ('Противотанковый пакет корпуса','Torso',2,dict(sharp=18,blunt=32,mass=12,wornBulk=7,move=-.75)),
 ('Гибкие амортизаторы суставов','Arm',1,dict(blunt=5,mass=.8,move=.08)),
 ('Баллистическая юбка','Leg',1,dict(sharp=4,blunt=7,mass=4,wornBulk=2,move=-.11)),
 ('Модуль защиты от ОМП','All',2,dict(heat=.22,mass=2,move=-.08)),
 ('Умная перераспределяемая плита','Torso',3,dict(sharp=13,blunt=17,mass=4,move=-.09)),
 ('Нейросервопривод передвижения','All',3,dict(move=.75,mass=1.2,carry=12)),
 ('Система разгрузки CE','All',2,dict(carry=27,carryBulk=8,mass=2.5,wornBulk=1.5)),
 ('Керамотканевое демпфирование','All',1,dict(blunt=3,sharp=1.5,mass=1.4)),
 ('Контур термостабилизации','All',2,dict(heat=.23,mass=1.9)),
 ('Многослойные композитные пластины','Torso',1,dict(sharp=6,blunt=8,mass=7,wornBulk=3,move=-.24)),
 ('Автоподстройка креплений','All',3,dict(move=.12,wornBulk=-1,carryBulk=3)),
 ('Локальная защита головы','Head',2,dict(sharp=11,blunt=14,mass=3.5)),
 ('Поглощающий импульс подслой','All',3,dict(blunt=12,mass=5.4,wornBulk=3,move=-.29)),
 ('Транспортный походный контур','All',1,dict(move=.23,carry=13,carryBulk=4,mass=2.6,sharp=-1.4)),
]
specials=[]
for i,(name,reg,tier,eff) in enumerate(specialnames):
 c={'Steel': (3+2*i) if tier<=2 else 4,'ComponentIndustrial':1+(i%3),'ComponentSpacer': (0 if tier==1 else 2 if tier==2 else 5),'Gold':(0 if tier<3 else 9+i)}
 special=dict(id=f'ArmorSpecial_{i:02}',name=name,region=reg,minTier=tier,cost=c,effects={**dict(sharp=0,blunt=0,heat=0,mass=0,bulk=0,wornBulk=0,move=0,carry=0,carryBulk=0,value=40+25*i,region=reg),**eff})
 specials.append(special)
for f in classes:
 for t,(sh,bl,heat,mass,bulk,worn,move,price) in enumerate(f['base'],1):
  f.setdefault('chassis',[]).append(dict(tier=t,defName=f'TC_Armor_{f["key"]}_T{t}',label=f'{f["label"]} Т{t}',sharp=sh,blunt=bl,heat=heat,mass=mass,bulk=bulk,wornBulk=worn,move=move,price=price))
 del f['base']
output={'schema':1,'families':classes,'specials':specials,'notes':'Coverage is defined by the chassis and CE PartialStat. Optional regions without pads are suppressed by the per-hit CE hook.'}
(doc/'armor_catalog.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
# Emit stable, explicit, compiled-in C# catalog. Avoid runtime JSON and XML scans entirely.
def q(s):return json.dumps(s,ensure_ascii=False)
def f(x):
 st=str(float(x));return st+'f'
def option(o):
 e=o['effects']; c=o['cost'];fields=['sharp','blunt','heat','mass','bulk','wornBulk','move','carry','carryBulk','value'];
 return 'new ArmorOption('+', '.join([q(o['name']),str(o['minTier']),q(e['region'])]+[f(e.get(k,0)) for k in fields]+[str(c.get(k,0)) for k in ['Steel','ComponentIndustrial','ComponentSpacer','Gold']])+')'
lines=['''using System;
namespace ThornWhip
{
    public sealed class ArmorOption
    {
        public readonly string Name, Region;
        public readonly int MinTier, Steel, Industrial, Advanced, Gold;
        public readonly float Sharp, Blunt, Heat, Mass, Bulk, WornBulk, Move, Carry, CarryBulk, Value;
        public ArmorOption(string name,int minTier,string region,float sharp,float blunt,float heat,float mass,float bulk,float wornBulk,float move,float carry,float carryBulk,float value,int steel,int industrial,int advanced,int gold)
        { Name=name;MinTier=minTier;Region=region;Sharp=sharp;Blunt=blunt;Heat=heat;Mass=mass;Bulk=bulk;WornBulk=wornBulk;Move=move;Carry=carry;CarryBulk=carryBulk;Value=value;Steel=steel;Industrial=industrial;Advanced=advanced;Gold=gold;}
    }
    public sealed class ArmorSlot
    {
        public readonly string Name,Region; public readonly bool Required; public readonly ArmorOption[] Options;
        public ArmorSlot(string name,string region,bool required, params ArmorOption[] options){ Name=name;Region=region;Required=required;Options=options; }
    }
    public sealed class ArmorChassis
    {
        public readonly string Key,Label,DefName; public readonly int Tier,FamilyId;
        public readonly float Sharp,Blunt,Heat,Mass,Bulk,WornBulk,Move,Price;
        public ArmorChassis(string key,string label,string defName,int tier,int familyId,float sharp,float blunt,float heat,float mass,float bulk,float wornBulk,float move,float price)
        {Key=key;Label=label;DefName=defName;Tier=tier;FamilyId=familyId;Sharp=sharp;Blunt=blunt;Heat=heat;Mass=mass;Bulk=bulk;WornBulk=wornBulk;Move=move;Price=price;}
    }
    public static class ArmorCatalog
    {
        public static readonly ArmorChassis[] Chassis={
''']
for fi,fam in enumerate(classes):
 for ch in fam['chassis']:
  fields=['sharp','blunt','heat','mass','bulk','wornBulk','move','price']
  lines.append('            new ArmorChassis('+','.join([q(fam['key']),q(ch['label']),q(ch['defName']),str(ch['tier']),str(fi)]+[f(ch[k]) for k in fields])+'),\n')
lines.append('        };\n        public static readonly ArmorSlot[][] Slots = {\n')
for fam in classes:
 lines.append('            new ArmorSlot[] {\n')
 for s in fam['slots']:
  lines.append('                new ArmorSlot('+q(s['label'])+','+q(s['region'])+','+('true' if s['required'] else 'false')+',\n')
  for i,o in enumerate(s['options']):lines.append('                    '+option(o)+(',' if i<4 else '')+'\n')
  lines.append('                ),\n')
 lines.append('            },\n')
lines.append('        };\n        public static readonly ArmorOption[] Specials={\n')
for s in specials: lines.append('            '+option(s)+',\n')
lines.append('''        };
        public static ArmorChassis Base(int index) => Chassis[index>=0 && index<Chassis.Length?index:0];
        public static ArmorSlot[] Parts(int familyId) => Slots[familyId>=0 && familyId<Slots.Length?familyId:0];
        public static ArmorSlot[] Parts(ArmorBlueprint b) => Parts(Base(b?.ChassisId ?? 0).FamilyId);
        public static bool IsArmor(string name) => name!=null && name.StartsWith("TC_Armor_",StringComparison.Ordinal);
        public static int IndexOf(string defName)
        {for(int i=0;i<Chassis.Length;i++)if(Chassis[i].DefName==defName)return i;return -1;}
    }
}
''')
(src/'ArmorCatalog.cs').write_text(''.join(lines),encoding='utf-8')
print('Generated armor data',len(variants),'slots',sum(len(s['options']) for s in variants),'options',len(specials),'specials')
