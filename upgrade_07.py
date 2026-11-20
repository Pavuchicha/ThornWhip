#!/usr/bin/env python3
from pathlib import Path
import json
R=Path(__file__).parent; source=R/'ThornWhip/Source'; dat=R/'ThornWhip/Documentation/weapon_families.json'
x=json.loads(dat.read_text())
for family in x:
 slots=family['slots'];assert len(slots)==14
 for i,s in enumerate(slots):s['required']=i not in (10,13)
 if len(slots)==14:
  names=['Базовая нижняя планка','Облегчённая рельса','Усиленная рельса','Многопозиционный кронштейн','Умная интерфейсная рельса']
  eff=[{'mass':0.04,'bulk':.04},{'mass':-.08,'sway':.02},{'mass':.20,'sway':-.04,'recoil':-.02},{'mass':.16,'sights':.04,'warmup':-.015},{'mass':.10,'sights':.07,'nightVision':.03,'value':140}]
  costs=[{'steel':3},{'steel':2,'industrial':1},{'steel':4,'industrial':2},{'steel':3,'industrial':2,'advanced':1},{'steel':2,'industrial':1,'advanced':3,'gold':5}]
  slots.append({'id':14,'label':'Нижняя аксессуарная планка','required':False,'options':[{'name':name,'effects':e,'cost':c} for name,e,c in zip(names,eff,costs)]})
dat.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
gen=R/'generate_code_06.py';s=gen.read_text()
s=s.replace('public readonly string Label;\n        public readonly ModuleOption[] Options;\n        public ModuleSlot(string label, params ModuleOption[] options) { Label=label; Options=options; }',
            'public readonly string Label; public readonly bool Required;\n        public readonly ModuleOption[] Options;\n        public ModuleSlot(string label, bool required, params ModuleOption[] options) { Label=label; Required=required; Options=options; }')
s=s.replace("'new ModuleSlot('+q(s['label'])+',\\n'", "'new ModuleSlot('+q(s['label'])+','+('true' if s.get('required',True) else 'false')+',\\n'")
s=s.replace("(',' if j<4 else '')", "(',' if j<len(s['options'])-1 else '')")
gen.write_text(s)
# Make the old save format safe: arrays must match the new 15 slots.
p=source/'Blueprints.cs';s=p.read_text()
s=s.replace('public List<int> Parts = Enumerable.Repeat(-1, 14).ToList();','public List<int> Parts = Enumerable.Repeat(-1, 15).ToList();')
s=s.replace('public List<int> Materials = Enumerable.Repeat(0, 14).ToList();','public List<int> Materials = Enumerable.Repeat(0, 15).ToList();')
s=s.replace('if (SelectedPart(i) < 0) n++;','if (WeaponCatalog.RequiredFor(this)[i].Required && SelectedPart(i) < 0) n++;')
s=s.replace('if (Material(i) == 1) n++;','if (SelectedPart(i) >= 0 && Material(i) == 1) n++;')
p.write_text(s)
# Only installed ordinary modules influence the cost; missing optional sight has a penalty.
p=source/'WeaponTuning.cs';s=p.read_text()
s=s.replace('            for (int i = 0; i < 3; i++)','            if (b.SelectedPart(10) < 0) { t.Sights -= .28f; t.Sway += .07f; }\n            for (int i = 0; i < 3; i++)',1)
p.write_text(s)
# Designer layout dynamic for 15 parts.
p=source/'UI.cs';s=p.read_text()
s=s.replace('ПЛЕТЬ ТЕРНА  /  МАРКСАНСКИЙ АРСЕНАЛ','КОРПУС ТЕРНА  /  ОРУЖЕЙНАЯ МАСТЕРСКАЯ')
s=s.replace('float rowHeight = Mathf.Min(50, remaining / 7f);','int rowCount = (WeaponCatalog.RequiredFor(design).Length + 1) / 2;\n            float rowHeight = Mathf.Min(50, remaining / rowCount);')
s=s.replace('"14 ОБЯЗАТЕЛЬНЫХ УЗЛОВ  /  "','"15 УЗЛОВ (ПОМЕЧЕННЫЕ * ОБЯЗАТЕЛЬНЫ)  /  "')
s=s.replace('for (int i = 0; i < 14; i++)','for (int i = 0; i < WeaponCatalog.RequiredFor(design).Length; i++)')
s=s.replace('int col = i / 7, row = i % 7;','int col = i / rowCount, row = i % rowCount;')
s=s.replace('float modsY = top + 7 * rowHeight + 9;','float modsY = top + rowCount * rowHeight + 9;')
s=s.replace('string label = WeaponCatalog.RequiredFor(design)[id].Label;','string label = WeaponCatalog.RequiredFor(design)[id].Label + (WeaponCatalog.RequiredFor(design)[id].Required ? " *" : "");')
s=s.replace('var options = new List<FloatMenuOption> { new FloatMenuOption("[не установлен]", () => design.Parts[index] = -1) };','var options = new List<FloatMenuOption>();\n            if (!WeaponCatalog.RequiredFor(design)[index].Required) options.Add(new FloatMenuOption("[не установлен]", () => design.Parts[index] = -1));')
s=s.replace('"Сначала установи все 14 обязательных узлов и устрани повторы"','"Заполни обязательные узлы и устрани повторы"')
s=s.replace('for (int i = 0; i < WeaponCatalog.RequiredFor(design).Length; i++) design.Parts[i] = 0;',
            'for (int i = 0; i < WeaponCatalog.RequiredFor(design).Length; i++) design.Parts[i] = WeaponCatalog.RequiredFor(design)[i].Required ? 0 : -1;')
p.write_text(s)
# Add new graphic slot at bottom rail; existing layers are unchanged.
p=source/'WeaponVisuals.cs';s=p.read_text()
s=s.replace('8, 9, 10, 11, 12, 13 };','8, 9, 10, 11, 12, 13, 14 };')
s=s.replace('new Rect(390,119,72,31), new Rect(884,128,90,47)','new Rect(390,119,72,31), new Rect(884,128,90,47), new Rect(610,183,120,26)')
s=s.replace('419, 795 };','419, 795, 631 };').replace('122, 132 };','122, 132, 197 };')
p.write_text(s)
# Buttons; file IDs remain stable.
p=source/'BenchComps.cs';s=p.read_text()
s=s.replace('yield return new Command_Action\n            {\n                defaultLabel = "Конструктор оружия",','yield return new Command_Action\n            {\n                defaultLabel = "Конструктор брони", defaultDesc = "3 класса брони × Т1–Т3, обязательные/необязательные узлы, улучшения CE",\n                action = () => Find.WindowStack.Add(new Dialog_ArmorDesign(parent as Building_WorkTable))\n            };\n            yield return new Command_Action\n            {\n                defaultLabel = "Конструктор оружия",')
s=s.replace('yield return new Command_Action\n            {\n                defaultLabel = "Разработанное оружие",','yield return new Command_Action\n            {\n                defaultLabel = "Разработанная броня", defaultDesc = "Заказ исследованных индивидуальных бронекомплектов",\n                action = () => Find.WindowStack.Add(new Dialog_ArmorManufacture(parent as Building_WorkTable))\n            };\n            yield return new Command_Action\n            {\n                defaultLabel = "Разработанное оружие",')
p.write_text(s)
# Extend existing CE event patches, not separate global loops.
p=source/'Events.cs';s=p.read_text()
s=s.replace('            // Render-event only:', '            ArmorProtection.TryInstall(harmony);\n            // Render-event only:')
s=s.replace('            if (__instance is Bill_WeaponManufacture manufacture && manufacture.Prepaid)',
            '            if (__instance is Bill_ArmorResearch ar && ar.Blueprint != null &&\n                ar.recipe?.defName == "TC_DevelopArmor") GameComponent_ArmorLibrary.Current?.Register(ar.Blueprint);\n            if (__instance is Bill_ArmorManufacture am && am.Prepaid)\n            { am.Prepaid = false; am.ResourceIds.Clear(); am.ResourceCounts.Clear(); }\n            if (__instance is Bill_WeaponManufacture manufacture && manufacture.Prepaid)')
s=s.replace('            if (recipeDef?.defName == null || !recipeDef.defName.StartsWith("TT_Craft_", StringComparison.Ordinal)) return;',
            '''            if (recipeDef?.defName == null) return;
            if (recipeDef.defName.StartsWith("TC_Craft_Armor_", StringComparison.Ordinal))
            {
                if (worker?.CurJob?.bill is Bill_ArmorManufacture armor && armor.Blueprint != null)
                    __result=AttachArmorBlueprint(__result,armor.Blueprint.Copy());
                return;
            }
            if (!recipeDef.defName.StartsWith("TT_Craft_", StringComparison.Ordinal)) return;''')
s=s.replace('        private static IEnumerable<Thing> AttachBlueprint',
            '''        private static IEnumerable<Thing> AttachArmorBlueprint(IEnumerable<Thing> result, ArmorBlueprint design)
        {
            foreach (Thing item in result)
            {
                if (item?.TryGetComp<CompArmorDesign>() is CompArmorDesign comp)
                    comp.SetBlueprint(design);
                yield return item;
            }
        }
        private static IEnumerable<Thing> AttachBlueprint''')
p.write_text(s)
# Mixed bill list with refunds for armor.
p=source/'QueueUI.cs';s=p.read_text()
s=s.replace('bill is Bill_WeaponManufacture md ? md.Blueprint?.Title : "Неизвестный заказ"',
            'bill is Bill_WeaponManufacture md ? md.Blueprint?.Title :\n                    bill is Bill_ArmorResearch ar ? ar.Blueprint?.Title :\n                    bill is Bill_ArmorManufacture am ? am.Blueprint?.Title : "Неизвестный заказ"')
s=s.replace('if (bill is Bill_WeaponManufacture manufacturing) WeaponCosts.Refund(bench, manufacturing);',
            'if (bill is Bill_WeaponManufacture manufacturing) WeaponCosts.Refund(bench, manufacturing);\n                    if (bill is Bill_ArmorManufacture armor) ArmorCosts.Refund(bench, armor);')
p.write_text(s)
# Rebrand display, preserve package id, old saved items and DefNames.
p=R/'ThornWhip/About/About.xml';s=p.read_text()
s=s.replace('Плеть Терна — модульный конструктор [0.6 SOURCE]','Корпус Терна — модульный арсенал и бронесистемы [0.7 SOURCE]')
s=s.replace('Thorn Whip Project','Thorn Corps Project')
s=s.replace('Модульный арсенал Combat Extended:', 'Модульный арсенал и бронесистемы Combat Extended:')
s=s.replace('14 обязательных узлов','15 обязательных и необязательных узлов')
s=s.replace('три универсальных дополнительных слота','три универсальных особых слота')
s=s.replace('описание>','описание>')
s=s.replace('Важное: исходная версия требует компиляции DLL.','Также 3 класса брони × 3 базы Т1–Т3 с уникальными деталями и зонами покрытия. Важное: исходная версия требует компиляции DLL.')
p.write_text(s)
print('Applied upgrade to weapons/events/benches/metadata')
