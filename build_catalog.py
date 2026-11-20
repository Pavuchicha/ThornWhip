#!/usr/bin/env python3
"""Declarative family catalog -> C# module definition; deterministic source of truth.
    The CE numerical baselines are design targets, not confirmed runtime results.
"""
import json
from pathlib import Path
root=Path(__file__).parent
p=root/'ThornWhip/Documentation/weapon_families.json'
# Part indices 0 receiver/mode, 2 barrel, 9 magazine are deliberate for compatibility with 0.4.
family_data=[
 dict(key='Rifle',label='Марксанская винтовка «Плеть Терна»',short='ВИНТОВКА',caliber='5,56×45 NATO',ammoSet='AmmoSet_556x45mmNATO',projectile='Bullet_556x45mmNATO_FMJ',sound='Shot_AssaultRifle',tail='GunTail_Medium',
      sights=.85,spread=.09,sway=1.45,cooldown=.88,mass=3.7,bulk=4.8,value=420,range=[55,70],magazine=[20,30],burst=[2,1],between=8,warmup=1.2,recoil=.76,reload=3.8,minRange=0,steel=65,component=4,work=16500,visual='M16-inspired high-tech long rifle'),
 dict(key='Auto',label='Автомат «Гнев Терна»',short='АВТОМАТ',caliber='5,56×45 NATO',ammoSet='AmmoSet_556x45mmNATO',projectile='Bullet_556x45mmNATO_FMJ',sound='Shot_AssaultRifle',tail='GunTail_Medium',
      sights=.92,spread=.135,sway=1.21,cooldown=.40,mass=3.25,bulk=4.3,value=455,range=[40,51],magazine=[25,40],burst=[5,3],between=5,warmup=.65,recoil=1.28,reload=3.3,minRange=0,steel=62,component=5,work=18200,visual='modular NATO bullpup / HK416 silhouette, angular compact receiver'),
 dict(key='Pistol',label='Пистолет «Клык Терна»',short='ПИСТОЛЕТ',caliber='9×19 Parabellum',ammoSet='AmmoSet_9x19mmPara',projectile='Bullet_9x19mmPara_FMJ',sound='Shot_Autopistol',tail='GunTail_Light',
      sights=.70,spread=.18,sway=.87,cooldown=.39,mass=1.15,bulk=1.9,value=260,range=[17,23],magazine=[12,20],burst=[1,3],between=6,warmup=.43,recoil=1.5,reload=2.5,minRange=0,steel=35,component=3,work=9900,visual='futuristic western service pistol slide and compact polymer frame'),
 dict(key='Launcher',label='Гранатомёт «Гром Терна»',short='ГРАНАТОМЁТ',caliber='40×46 mm LV',ammoSet='AmmoSet_40x46mmGrenade',projectile='Bullet_40x46mmGrenade_HE',sound='InfernoCannon_Fire',tail=None,
      sights=1.10,spread=.18,sway=1.31,cooldown=.62,mass=5.3,bulk=5.65,value=850,range=[34,40],magazine=[3,6],burst=[1,2],between=23,warmup=1.05,recoil=2.93,reload=5.1,minRange=5,steel=85,component=8,work=25500,visual='rotating multi-shot 40mm launcher like MGL silhouette with sci-fi stock'),
]
# 14 pieces per family; each pair modifies CE stats with tradeoffs, no arbitrary armour penetration.
base_rifle=[
 ('Верхняя ствольная коробка','Двухимпульсная автоматика','Одиночный точный цикл'),
 ('Нижняя ствольная коробка','Стандартная','Нейрокомпозитная'),
 ('Ствол','Короткий','Удлинённый'),
 ('Затворная группа','Усиленная','Облегчённая'),
 ('Газовый блок','Фиксированный','Регулируемый'),
 ('Ударно-спусковой механизм','Военный','Прецизионный'),
 ('Возвратный механизм','Усиленная пружина','Инерционный демпфер'),
 ('Приклад','Складной','Стабилизированный'),
 ('Цевьё','Лёгкое','Охлаждаемое'),
 ('Магазин','20 патронов','30 патронов'),
 ('Прицельная система','Механическая','Цифровая'),
 ('Пистолетная рукоять','Полимерная','Сенсорная'),
 ('Рукоятка взвода','Ручная','Электроассистент'),
 ('Дульное устройство','Пламегаситель','Умный компенсатор')]
parts={
 'Rifle':base_rifle,
 'Auto':[
 ('Ствольная коробка','Скорострельный цикл','Контролируемые очереди'),('Нижний корпус','Лёгкий полимер','Экзосплавный'),
 ('Ствол','Штурмовой короткий','Средний утолщённый'),('Затвор','Высокоскоростной','Демпфированный'),('Газоотвод','Форсированный','Адаптивный'),
 ('Спуск','Боевой','Электронный'),('Возвратная пружина','Жёсткая','Стабилизирующая'),('Приклад','Телескопический','Гироскопический'),
 ('Цевьё','Открытая вентиляция','Тепловой кожух'),('Магазин','25 патронов','40 патронов'),
 ('Прицел','Голографический','Нейрорефлексный'),('Рукоять','Тактическая','Датчиковая'),
 ('Переводчик огня','Механический','Программируемый'),('Дульное устройство','Пламегаситель','Активный компенсатор')],
 'Pistol':[
 ('Затворная рама','Одиночный цикл','Трёхвыстрельная отсечка'),('Рамка','Полимерная','Армированная'),
 ('Ствол','Компактный','Удлинённый'),('Затвор','Облегчённый','Утяжелённый'),('Экстрактор','Пружинный','Электромагнитный'),
 ('Спуск','Двойного действия','Сенсорный'),('Возвратная пружина','Компактная','Мягкая'),('Задняя панель рукояти','Обтекаемая','Стабилизирующая'),
 ('Кожух затвора','Открытый','Термокожух'),('Магазин','12 патронов','20 патронов'),
 ('Прицел','Тритиевый','Компактный коллиматор'),('Накладки рукояти','Шероховатые','Биометрические'),
 ('Затворная задержка','Ручная','Автоматическая'),('Насадка на ствол','Защитная','Компенсирующая')],
 'Launcher':[
 ('Блок управления','Одиночный подрывной цикл','Двойной последовательный залп'),('Ствольная коробка','Усиленная стальная','Композитная'),
 ('Ствол','Короткий гранатомётный','Длинный стабилизированный'),('Затвор','Механическая казённая часть','Герметизированный блок'),
 ('Механизм подачи','Храповик','Сервопривод'),('Спуск','Механический','Дистанционный электро-спуск'),
 ('Возврат/амортизатор','Пружинный','Гидравлический'),('Приклад','Откидной','Противооткатный'),
 ('Цевьё','Сетчатое','Изолированное'),('Барабан','3 гранаты','6 гранат'),
 ('Прицельный комплекс','Лестничный','Дальномерный'),('Рукоять','Резиновая','Экзоприводная'),
 ('Замок барабана','Ручной','Автосброс'),('Надульный узел','Раструб','Газовый диффузор')]
}
# Explicit effects per slot class, low-tradeoff options (- = better in spread/sway/recoil).
def effect(i,v,family):
    # Both variants have a meaningful mechanical consequence. All effects are per-item, quality scaled.
    changes=[
      [dict(sway=.045,cooldown=-.03,mass=-.06), dict(sights=.09,spread=-.004,recoil=-.06,cooldown=.03,mass=.11)],
      [dict(mass=-.13,bulk=-.10,sway=.045),dict(mass=.10,bulk=.05,spread=-.003,sights=.04,value=36)],
      [dict(spread=.010,sway=-.04,mass=-.18,bulk=-.14,cooldown=-.03),dict(spread=-.010,sway=.04,mass=.28,bulk=.19,value=30)],
      [dict(cooldown=-.04,recoil=.075,mass=-.08),dict(cooldown=.04,recoil=-.10,mass=.16,value=25)],
      [dict(recoil=.055,cooldown=-.03,mass=-.07),dict(recoil=-.08,cooldown=.025,mass=.11,value=38)],
      [dict(warmup=-.04,spread=.004,mass=-.02),dict(warmup=.015,spread=-.008,sights=.07,value=36)],
      [dict(cooldown=-.045,recoil=.06),dict(cooldown=.05,recoil=-.12,mass=.15,value=30)],
      [dict(sway=.10,bulk=-.28,mass=-.23),dict(sway=-.09,recoil=-.07,bulk=.22,mass=.22,value=29)],
      [dict(mass=-.20,cooldown=-.02,spread=.006),dict(mass=.24,spread=-.008,sway=-.07,value=40)],
      [dict(mass=-.07,bulk=-.07,reload=-.07),dict(mass=.17,bulk=.18,reload=.10,value=30)],
      [dict(sights=-.05,mass=-.05),dict(sights=.22,warmup=-.075,mass=.13,value=66,nightVision=.10)],
      [dict(sway=.03,mass=-.07),dict(sway=-.05,recoil=-.04,mass=.055,value=26)],
      [dict(reload=-.03,cooldown=.01),dict(reload=-.12,mass=.09,value=30)],
      [dict(mass=-.05,recoil=.055),dict(recoil=-.12,spread=-.006,mass=.16,bulk=.06,value=34)]
    ]
    x=changes[i][v].copy()
    if family=='Launcher':
        if 'recoil' in x: x['recoil']*=1.16
        if 'spread' in x: x['spread']*=1.20
    if family=='Pistol':
        if 'mass' in x: x['mass']*=.45
        if 'bulk' in x: x['bulk']*=.50
    if family=='Auto':
        if 'cooldown' in x: x['cooldown']*=.85
    # Slot 0/2/9 also change physical CE defs (burst/range/magazine), not just stats.
    return {k:round(val,6) for k,val in x.items()}
catalog=[]
for f in family_data:
    sl=[]
    for i,(label,a,b) in enumerate(parts[f['key']]):
        sl.append({'id':i,'label':label,'options':[{'name':a,'effects':effect(i,0,f['key'])},{'name':b,'effects':effect(i,1,f['key'])}]})
    catalog.append({'family':f,'slots':sl})
p.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
# Generate code in one place, preserve rifle suffixes for backwards compatibility.
base=(root/'ThornWhip/Source/WeaponCatalog.cs').read_text()
specials=base[base.index('        // Slots 0,1,2 are IDENTICAL.'):base.index('        public static string WeaponDefName')]
header=base[:base.index('    public static class WeaponCatalog')]
def q(s):return json.dumps(s,ensure_ascii=False)
keys=['sights','spread','sway','cooldown','mass','bulk','value','recoil','warmup','reload','range','nightVision']
lines=[header, '    public sealed class WeaponFamily\n    {\n',
 '''        public readonly string Key, Label, Caliber;
        public readonly float Sights, Spread, Sway, Cooldown, Mass, Bulk, MarketValue;
        public readonly int[] Magazine, Burst, Ranges;
        public WeaponFamily(string key, string label, string caliber, float sights, float spread, float sway,
            float cooldown, float mass, float bulk, float marketValue, int mag0, int mag1,
            int burst0, int burst1, int range0, int range1)
        { Key=key; Label=label; Caliber=caliber; Sights=sights; Spread=spread; Sway=sway; Cooldown=cooldown;
          Mass=mass; Bulk=bulk; MarketValue=marketValue; Magazine=new[]{mag0,mag1};
          Burst=new[]{burst0,burst1}; Ranges=new[]{range0,range1}; }
    }
    public static class WeaponCatalog
    {
        public static readonly WeaponFamily[] Families = {
''']
for f in family_data:
    lines.append(f'            new WeaponFamily({q(f["key"])},{q(f["label"])},{q(f["caliber"])},{f["sights"]}f,{f["spread"]}f,{f["sway"]}f,{f["cooldown"]}f,{f["mass"]}f,{f["bulk"]}f,{f["value"]}f,{f["magazine"][0]},{f["magazine"][1]},{f["burst"][0]},{f["burst"][1]},{f["range"][0]},{f["range"][1]}),\n')
lines.append('        };\n        private static readonly ModuleSlot[][] Slots = {\n')
for data in catalog:
    lines.append('            new ModuleSlot[] {\n')
    for sl in data['slots']:
        a,b=sl['options']
        def make(opt):
            eff=opt['effects']; params=','.join(f'{k}: {v}f' for k,v in eff.items()); return f'new ModuleOption({q(opt["name"])}{","+params if params else ""})'
        lines.append(f'                new ModuleSlot({q(sl["label"])}, {make(a)}, {make(b)}),\n')
    lines.append('            },\n')
lines.append('        };\n')
lines.append('''        public static WeaponFamily Family(int id) => Families[id >= 0 && id < Families.Length ? id : 0];
        public static ModuleSlot[] RequiredFor(int id) => Slots[id >= 0 && id < Slots.Length ? id : 0];
        public static ModuleSlot[] RequiredFor(WeaponBlueprint b) => RequiredFor(b?.FamilyId ?? 0);
        public static bool IsOurWeapon(string name) => name != null &&
            (name.StartsWith("TT_Rifle_R", StringComparison.Ordinal) || name.StartsWith("TT_Auto_R", StringComparison.Ordinal) ||
             name.StartsWith("TT_Pistol_R", StringComparison.Ordinal) || name.StartsWith("TT_Launcher_R", StringComparison.Ordinal));
        public static int FamilyFromDef(string name)
        {
            if (name != null) for (int i = 0; i < Families.Length; i++)
                if (name.StartsWith("TT_" + Families[i].Key + "_R", StringComparison.Ordinal)) return i;
            return 0;
        }
''')
lines.append(specials)
lines.append('''        public static string WeaponDefName(WeaponBlueprint b) => $"TT_{Family(b.FamilyId).Key}_R{b.Part(0)}_B{b.Part(2)}_M{b.Part(9)}";
        public static string RecipeName(WeaponBlueprint b)
        {
            string prefix = b.FamilyId == 0 ? "TT_Craft" : "TT_Craft_" + Family(b.FamilyId).Key;
            return $"{prefix}_R{b.Part(0)}_B{b.Part(2)}_M{b.Part(9)}_P{b.PlasteelCount}_S{b.SpecialCount}";
        }
    }
}
''')
(root/'ThornWhip/Source/WeaponCatalog.cs').write_text(''.join(lines))
print('Generated families:',len(catalog),'slots:',sum(len(x['slots']) for x in catalog),'options:',sum(len(x['slots'])*2 for x in catalog))
