#!/usr/bin/env python3
"""Deterministically upgrade 0.5's four-family data to 5 distinct variants per core slot and 15 shared specials.
Runs on source snapshots without access to the game. Index positions 0/1 stay stable for old saves.
"""
from pathlib import Path
import json,copy
P=Path(__file__).parent/'ThornWhip/Documentation'
families_path=P/'weapon_families.json'
data=json.loads(families_path.read_text(encoding='utf-8'))
# Three new functional variants in each slot, family-specific for physically distinct mechanisms.
NAMES={
'Rifle':[
('Экономичный кулачковый затвор','Адаптивный сервозатвор','Нейропрограммируемая автоматика'),
('Штампованная коробка','Керамическая силовая коробка','Живая метаматериальная коробка'),
('Карабинный тонкий ствол','Матчевый толстостенный ствол','Активно охлаждаемый наноствол'),
('Простой полусвободный затвор','Титановая затворная группа','Электромагнитный затвор'),
('Газовый кран полевого ремонта','Импульсный газовый блок','Автонастраиваемый плазмоклапан'),
('Полевой механический спуск','Двухступенчатый спуск','Нейросенсорный спуск'),
('Лёгкий буфер','Гидравлический буфер','Магнитореологический демпфер'),
('Каркасный приклад','Матчевый тяжёлый приклад','Гироскопический приклад'),
('Перфорированное цевьё','Углеродный тепловой кожух','Криоканальное цевьё'),
('Скоросъёмный магазин','Усиленный магазин','Смарт-магазин с диагностикой'),
('Открытые резервные прицельные','Оптика переменной кратности','Нейрооптический модуль'),
('Петлевая полевая рукоять','Биомеханическая рукоять','Адаптивная сенсорная рукоять'),
('Двусторонняя рукоятка взвода','Сервовзвод','Бесконтактный привод затвора'),
('Простой дульный тормоз','Многокамерный компенсатор','Активная антиимпульсная насадка')],
'Auto':[
('Бюджетный открытый цикл','Контроллер коротких очередей','Предиктивный контроллер огня'),
('Штампованный нижний корпус','Титановая силовая рама','Плетёный метакорпус'),
('Штурмовой ультракороткий ствол','Тяжёлый средний ствол','Охлаждаемый активный ствол'),
('Упрощённый скоростной затвор','Усиленный затворный привод','Электромагнитный цикл'),
('Газоотвод фиксированного давления','Сервогазоотвод','Плазморегулятор подачи'),
('Штампованный спуск','Двухконтурный спуск','Прогнозирующий нейроспуск'),
('Жёсткий возвратный узел','Гидравлический буфер','Активный импульсный демпфер'),
('Проволочный складной приклад','Тяжёлый тактический приклад','Миниатюрный гироприклад'),
('Короткое перфорированное цевьё','Теплоизоляционное цевьё','Микроканальное охлаждение'),
('Быстросменный магазин','Упрочнённый магазин','Диагностический смарт-магазин'),
('Открытый коллиматор','Штурмовой мультиприцел','Нейрорефлексный прицел'),
('Текстурная рукоять','Сервосцепление рукояти','Биометрическая рукоять'),
('Двусторонний переключатель','Автоматический селектор','Динамический предиктор очереди'),
('Короткий пламегаситель','Многокамерный ДТК','Активный векторный компенсатор')],
'Pistol':[
('Упрощённый ударниковый цикл','Электронный цикл затвора','Программируемый интеллектуальный затвор'),
('Штампованная облегчённая рамка','Титановая рамка','Морфирующая экзорамка'),
('Ультракороткий ствол','Матчевый ствол','Стабилизированный наноствол'),
('Тонкий полусвободный затвор','Упрочнённый затвор','Электромагнитный привод затвора'),
('Простой экстрактор','Двойной экстрактор','Магнитный экстрактор'),
('Стандартный спуск','Матчевый двойной спуск','Биометрический спуск'),
('Жёсткая возвратная пружина','Масляный демпфер','Магнитный амортизатор'),
('Тонкая тыльная накладка','Контурный упор ладони','Активный противооткатный упор'),
('Открытый кожух затвора','Карбоновый термокожух','Криоэкран затвора'),
('Облегчённый магазин','Упрочнённый магазин','Смарт-магазин пистолета'),
('Открытые механические прицельные','Компактная гибридная оптика','Нейросинхронизированная оптика'),
('Рифлёные накладки','Тактическая текстура','Сенсорная подладонная рукоять'),
('Механическая затворная задержка','Самосбрасываемая задержка','Электронная задержка'),
('Простой защитный колпачок','Двухкамерный тормоз','Активный компенсатор пистолета')],
'Launcher':[
('Упрощённый блок подрыва','Управляемый последовательный цикл','Интеллектуальный контроллер залпа'),
('Сварной стальной ресивер','Керамический герморесивер','Наноплетёная ствольная коробка'),
('Укороченный гранатный ствол','Тяжёлый нарезной ствол','Активный гироствол'),
('Простая казённая крышка','Усиленный гермозатвор','Электропривод затвора'),
('Механическая подача','Прецизионный барабанный привод','Предиктивный сервопривод барабана'),
('Рычажный спуск','Электроспуск с блокировкой','Нейроспуск с датчиком цели'),
('Простая возвратная пружина','Тяжёлый гидродемпфер','Магнитный противооткатный блок'),
('Лёгкий рамочный приклад','Жёсткий противооткатный приклад','Гиростабилизирующий приклад'),
('Перфорированный экран','Термокерамический кожух','Криоактивное цевьё'),
('Лёгкий барабан','Усиленный барабан','Барабан с диагностикой камор'),
('Лестничный резервный прицел','Дальномерная оптика','Интеллектуальный баллистический вычислитель'),
('Резиновая полевая рукоять','Противооткатная рукоять','Нейрогироскопическая рукоять'),
('Ручной фиксатор барабана','Сервозамок','Автоматический синхрозамок'),
('Простой защитный раструб','Диффузор отдачи','Активный газовый модулятор')]
}
# slot-specific CE stat deltas for choice 2, 3, 4 (choice 0 and 1 unchanged).
# Small trade-offs deliberately included; more expensive does not always mean stronger.
EFFECTS=[
[dict(cooldown=-.07,recoil=.15,mass=-.11),dict(cooldown=-.025,recoil=-.11,mass=.19,warmup=.025),dict(cooldown=-.065,recoil=-.045,sights=.08,mass=.20,warmup=-.025)],
[dict(mass=-.22,bulk=-.12,spread=.006),dict(mass=.16,bulk=.09,spread=-.006),dict(mass=-.03,sights=.07,spread=-.003,bulk=.06)],
[dict(mass=-.27,bulk=-.2,spread=.017,range=-.07),dict(mass=.43,bulk=.24,spread=-.012,range=.09,sway=.06),dict(mass=.13,spread=-.018,range=.12,bulk=.11)],
[dict(cooldown=-.06,recoil=.14,mass=-.07),dict(cooldown=-.04,recoil=-.075,mass=.13),dict(cooldown=-.075,recoil=-.035,reload=-.055,mass=.18)],
[dict(cooldown=-.04,recoil=.095,mass=-.06),dict(cooldown=.025,recoil=-.11,mass=.14),dict(cooldown=-.02,recoil=-.065,spread=-.004,mass=.17)],
[dict(warmup=-.055,spread=.012),dict(warmup=.015,spread=-.009,sights=.025),dict(warmup=-.095,spread=-.003,sights=.12)],
[dict(cooldown=-.08,recoil=.14,mass=-.07),dict(cooldown=.025,recoil=-.15,mass=.24),dict(cooldown=-.03,recoil=-.14,mass=.21)],
[dict(bulk=-.35,mass=-.25,sway=.15),dict(bulk=.30,mass=.35,sway=-.13,recoil=-.065),dict(bulk=.08,mass=.23,sway=-.115,recoil=-.13)],
[dict(mass=-.23,bulk=-.12,spread=.007),dict(mass=.27,spread=-.01,sway=-.06),dict(mass=.20,spread=-.012,sway=-.045,cooldown=-.035)],
[dict(mass=-.08,bulk=-.09,reload=-.16),dict(mass=.26,bulk=.24,reload=.16),dict(mass=.11,bulk=.06,reload=-.10,cooldown=-.012)],
[dict(sights=-.025,mass=-.07,warmup=-.035),dict(sights=.28,mass=.28,warmup=.055),dict(sights=.20,warmup=-.12,nightVision=.18,mass=.16)],
[dict(mass=-.09,sway=.05),dict(mass=.11,sway=-.11,recoil=-.03),dict(mass=.07,sway=-.12,warmup=-.045)],
[dict(reload=-.06,mass=.02),dict(reload=-.17,mass=.17,bulk=.065),dict(reload=-.11,mass=.085,cooldown=-.04)],
[dict(recoil=-.035,mass=.05,bulk=.035),dict(recoil=-.19,mass=.18,bulk=.10),dict(recoil=-.12,mass=.14,spread=-.005)]
]
SPECIALS=[
('Прицел','Лазерный целеуказатель','Дешёвая помощь при наведении',dict(sights=.13,sway=-.035,mass=.12,warmup=-.075),dict(steel=3,industrial=1,advanced=0,gold=0,value=45)),
('Прицел','Спектральный усилитель','Оптический усилитель в условиях недостаточного света',dict(sights=.09,mass=.19,nightVision=.24),dict(steel=2,industrial=1,advanced=1,gold=0,value=105)),
('Прицел','Нейро-связь оптики','Быстрый прицельный цикл, дорогой в ремонте',dict(sights=.19,sway=-.035,mass=.25,warmup=-.13),dict(steel=2,industrial=1,advanced=2,gold=5,value=170)),
('Коробка','Электронный спуск','Малая задержка между сериями, уязвим к сбоям',dict(cooldown=-.085,mass=.10,warmup=-.015),dict(steel=1,industrial=2,advanced=0,gold=0,value=105)),
('Коробка','Затворный стабилизатор','Снижение отдачи ценой веса',dict(sway=-.035,mass=.18,recoil=-.15),dict(steel=8,industrial=1,advanced=0,gold=0,value=125)),
('Коробка','Система быстрого досылания','Ускорение подготовки патронов',dict(mass=.18,reload=-.16),dict(steel=5,industrial=2,advanced=0,gold=0,value=95)),
('Цевьё','Сервостабилизатор','Снижение раскачивания в позиции',dict(sway=-.17,mass=.30,bulk=.12,recoil=-.06),dict(steel=6,industrial=1,advanced=1,gold=0,value=135)),
('Ствол','Термокомпенсатор','Компенсирует деформацию нагретого ствола',dict(spread=-.014,mass=.28),dict(steel=7,industrial=2,advanced=0,gold=0,value=125)),
('Магазин','Интеллектуальная подача','Ускоряет работу магазина, не меняя баллистику',dict(mass=.12,reload=-.13,cooldown=-.025),dict(steel=2,industrial=2,advanced=1,gold=0,value=110)),
('Прицел','Призменный дальномер','Уверенное считывание дальности на дистанции',dict(sights=.16,range=.05,mass=.24,warmup=.04),dict(steel=4,industrial=2,advanced=1,gold=0,value=126)),
('Прицел','Контурная голограмма','Быстрое ближнее наведение с недостатками вдали',dict(sights=.075,sway=-.10,warmup=-.07,spread=.004,mass=.19),dict(steel=2,industrial=2,advanced=0,gold=0,value=59)),
('Коробка','Система гашения импульса','Мощный тяжелый демпфер для устойчивых серий',dict(recoil=-.25,cooldown=.055,mass=.42,bulk=.18),dict(steel=11,industrial=1,advanced=0,gold=0,value=105)),
('Ствол','Криоканальный охладитель','Прогнозируемое смещение точек попаданий при долгом огне',dict(spread=-.017,sway=-.035,mass=.27,bulk=.14),dict(steel=4,industrial=1,advanced=2,gold=0,value=178)),
('Коробка','Электромагнитный затвор','Стабильное досылание, дорогое энергоснабжение',dict(cooldown=-.09,reload=-.06,recoil=-.045,mass=.22),dict(steel=5,industrial=1,advanced=3,gold=2,value=224)),
('Прицел','Псионический вычислитель','Экспериментальный оптический синхронизатор; не меняет пули CE',dict(sights=.24,sway=-.085,warmup=-.115,mass=.30,nightVision=.22),dict(steel=3,industrial=2,advanced=3,gold=12,value=405)),
]
assert len(SPECIALS)==15
# Industrial/Spacer/Gold expenditures are intentionally not proportional to stat strength.
for entry in data:
 key=entry['family']['key'];factor={'Rifle':1,'Auto':.92,'Pistol':.54,'Launcher':1.15}[key]
 assert len(entry['slots'])==14 and len(NAMES[key])==14
 for i,slot in enumerate(entry['slots']):
  assert len(slot['options']) in (2,5)
  if len(slot['options'])==5:continue
  # The original A/B options are persisted indices and must not be reordered.
  for choice,o in enumerate(slot['options']):
   cost = (dict(steel=2+(i%3),industrial=0 if i%3 else 1,advanced=0,gold=0) if choice==0 else
           dict(steel=3+(i%4),industrial=1+(i%2),advanced=1 if i in (1,10,12) else 0,gold=0))
   o['cost']=cost
  for new_index, (name,effects) in enumerate(zip(NAMES[key][i], EFFECTS[i]),start=2):
   effects=copy.deepcopy(effects)
   for k in ('mass','bulk'): 
    if k in effects:effects[k]=round(effects[k]*factor,5)
   # Focus high-tech on material cost / lifecycle complexity, not just static DPS.
   if new_index==2: cost=dict(steel=1+(i%3),industrial=0 if i%4 else 1,advanced=0,gold=0)
   elif new_index==3:cost=dict(steel=4+(i%5),industrial=1+(i%2),advanced=1 if i%2 else 0,gold=0)
   else:cost=dict(steel=2+(i%3),industrial=1+(i%2),advanced=2+(i%3==0),gold=4 if i%4 else 9)
   slot['options'].append(dict(name=name,effects=effects,cost=cost))
 assert all(len(s['options'])==5 for s in entry['slots'])
families_path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(P/'special_modules.json').write_text(json.dumps([dict(target=a,name=b,description=c,effects=d,cost=e) for a,b,c,d,e in SPECIALS],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(P/'part_catalog.json').write_text(json.dumps(dict(families=[dict(family=e['family']['key'],slots=e['slots']) for e in data],specials=json.loads((P/'special_modules.json').read_text()),specialSlotCount=3,persisted_indices='0/1 unchanged; new options 2/3/4',status='SOURCE ONLY; uncompiled'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Expanded:',sum(len(s['options']) for e in data for s in e['slots']),'core options; specials=',len(SPECIALS))
