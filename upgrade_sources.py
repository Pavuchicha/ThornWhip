from pathlib import Path
src=Path('ThornWhip/Source')
def mod(file,old,new):
 p=src/file; text=p.read_text(); count=text.count(old)
 if count==0:raise Exception(f'NOT FOUND {file}: {old[:140]}')
 p.write_text(text.replace(old,new));print(file,'patch matches',count)
# Persist family and factory provenance. 0.4 saves automatically migrate to rifle family.
mod('Blueprints.cs','public int Identifier;','public int Identifier;\n        public int FamilyId = 0; // V0.4 saves default to the rifle')
mod('Blueprints.cs','WeaponCatalog.Required.Length','WeaponCatalog.RequiredFor(this).Length')
mod('Blueprints.cs','Title = Title, Identifier = Identifier,','Title = Title, Identifier = Identifier, FamilyId = FamilyId,')
mod('Blueprints.cs','var b = new WeaponBlueprint { Title = "Плеть Терна — заводская" };','var b = new WeaponBlueprint { Title = "Терна — заводская", FamilyId = WeaponCatalog.FamilyFromDef(def?.defName) };')
mod('Blueprints.cs','if (def != null && def.defName.StartsWith("TT_Rifle_", StringComparison.Ordinal))','if (def != null && WeaponCatalog.IsOurWeapon(def.defName))')
mod('Blueprints.cs','Scribe_Values.Look(ref Identifier, "identifier", 0);','Scribe_Values.Look(ref Identifier, "identifier", 0);\n            Scribe_Values.Look(ref FamilyId, "weaponFamily", 0);')
mod('Blueprints.cs','Parts ??= new List<int>(); Materials ??= new List<int>(); Special ??= new List<int>();','Parts ??= new List<int>(); Materials ??= new List<int>(); Special ??= new List<int>();\n                if (FamilyId < 0 || FamilyId >= WeaponCatalog.Families.Length) FamilyId = 0;')
# Stat evaluation, quality are by item; materials relative to platform mass.
mod('WeaponTuning.cs','WeaponCatalog.Required.Length','WeaponCatalog.RequiredFor(b).Length')
mod('WeaponTuning.cs','WeaponCatalog.Required[i].Options','WeaponCatalog.RequiredFor(b)[i].Options')
mod('WeaponTuning.cs','t.Mass -= .055f;','t.Mass -= .055f * WeaponCatalog.Family(b.FamilyId).Mass / 3.7f;')
mod('WeaponTuning.cs','t.Bulk -= .025f;','t.Bulk -= .025f * WeaponCatalog.Family(b.FamilyId).Bulk / 4.8f;')
mod('StatPart_ThornWeapon.cs','!req.Thing.def.defName.StartsWith("TT_Rifle_", StringComparison.Ordinal)','!WeaponCatalog.IsOurWeapon(req.Thing.def.defName)')
mod('StatPart_ThornWeapon.cs','case "Mass": val = Math.Max(1.4f, val + t.Mass); break;','case "Mass": val = Math.Max(.50f, val + t.Mass); break;')
mod('StatPart_ThornWeapon.cs','case "Bulk": val = Math.Max(1.0f, val + t.Bulk); break;','case "Bulk": val = Math.Max(.60f, val + t.Bulk); break;')
mod('StatPart_ThornWeapon.cs','case "MarketValue": val = Math.Max(80f, val + t.Value * q); break;','case "MarketValue": val = Math.Max(65f, val + t.Value * q); break;')
mod('StatPart_ThornWeapon.cs','Марксанская конструкция:', 'Конструкция Терна:')
mod('BenchComps.cs','Выбрать 14 обязательных узлов, материалы и три универсальных слота улучшений.', 'Выбрать оружейное семейство, 14 обязательных узлов, материалы и три универсальных слота.')
mod('BenchComps.cs','Разработанные винтовки','Разработанное оружие')
mod('BenchComps.cs','именно этой винтовки','именно этого оружия')
mod('BenchComps.cs','Сборка: заводская (5,56×45 NATO, Combat Extended)','Сборка: заводская (Combat Extended)')
mod('Events.cs','"thornwhip.marksman.rifles"','"thornwhip.marksman.rifles"') # keep package & existing data, no-op
mod('Events.cs','!eq.def.defName.StartsWith("TT_Rifle_", StringComparison.Ordinal)','!WeaponCatalog.IsOurWeapon(eq.def.defName)')
# Window arsenal adaptation
mod('UI.cs', 'float sights = Math.Max(.1f, .85f + WeaponTuning.Adjust(t.Sights, quality, false));',
    'var family = WeaponCatalog.Family(b.FamilyId);\n            float sights = Math.Max(.1f, family.Sights + WeaponTuning.Adjust(t.Sights, quality, false));')
for a,b in [(' .09f +',' family.Spread +'),(' 1.45f +',' family.Sway +'),(' .88f *',' family.Cooldown *'),(' 3.7f +',' family.Mass +'),(' 4.8f +',' family.Bulk +')]:
    mod('UI.cs',a,b)
mod('UI.cs','Math.Max(1.4f, family.Mass + t.Mass)','Math.Max(.50f, family.Mass + t.Mass)')
mod('UI.cs','Math.Max(1f, family.Bulk + t.Bulk)','Math.Max(.60f, family.Bulk + t.Bulk)')
mod('UI.cs','(b.Part(9) == 0 ? 20 : 30)','family.Magazine[b.Part(9)]')
mod('UI.cs','(b.Part(2) == 0 ? 55 : 70)','family.Ranges[b.Part(2)]')
mod('UI.cs','(b.Part(0) == 0 ? 2 : 1)','family.Burst[b.Part(0)]')
mod('UI.cs','"КАЛИБР: 5,56×45 NATO  |  бронепробитие — от патрона CE"','"КАЛИБР: " + family.Caliber + "  |  урон/пробитие — от боеприпаса CE"')
mod('UI.cs','int p = b.PlasteelCount, s = b.SpecialCount;\n            return $"Сталь {65 + (14 - p) * 2} · Пласталь {p * 8} · Компоненты {4 + s}";',
    '''int p = b.PlasteelCount, s = b.SpecialCount;
            int baseSteel = (int)Math.Round(WeaponCatalog.Family(b.FamilyId).Mass * 13f + 16f);
            int components = b.FamilyId == 2 ? 3 : b.FamilyId == 3 ? 8 : b.FamilyId == 1 ? 5 : 4;
            return $"Сталь {baseSteel + (14 - p) * 2} · Пласталь {p * 8} · Компоненты {components + s}";''')
# Header: select family before working; reassign title only if untouched project default.
needle='''            // Technical preview / layers.
            Rect viewport = new Rect(13, 86, leftWidth, 265);'''
replacement='''            // Four weapon families. One shared researched blueprint data model.
            float tabWidth = (leftWidth - 18f) / 4f;
            for (int f = 0; f < WeaponCatalog.Families.Length; f++)
            {
                int target = f;
                var fam = WeaponCatalog.Families[f];
                if (DesignerUI.Action(new Rect(13f + f * tabWidth, 80f, tabWidth - 4f, 32f), fam.Label, design.FamilyId == f))
                {
                    if (design.FamilyId != target)
                    {
                        design.FamilyId = target;
                        // A different platform requires consciously selecting its assembly components.
                        for (int i = 0; i < WeaponCatalog.RequiredFor(design).Length; i++) { design.Parts[i] = -1; design.Materials[i] = 0; }
                        for (int i = 0; i < 3; i++) design.Special[i] = -1;
                        selectedPart = 0;
                        design.Title = fam.Label;
                        titleBuffer = design.Title;
                    }
                }
            }
            // Technical preview / layers.
            Rect viewport = new Rect(13, 116, leftWidth, 237);'''
mod('UI.cs',needle,replacement)
mod('UI.cs','new Rect(viewport.x + 11, viewport.y + 36, viewport.width - 22, 218)','new Rect(viewport.x + 11, viewport.y + 36, viewport.width - 22, 185)')
mod('UI.cs','WeaponCatalog.Required[id].Label','WeaponCatalog.RequiredFor(design)[id].Label')
mod('UI.cs','ModuleSlot slot = WeaponCatalog.Required[selectedPart];','ModuleSlot slot = WeaponCatalog.RequiredFor(design)[selectedPart];')
mod('UI.cs','"14 ОБЯЗАТЕЛЬНЫХ УЗЛОВ"','"14 ОБЯЗАТЕЛЬНЫХ УЗЛОВ  /  " + WeaponCatalog.Family(design.FamilyId).Caliber')
mod('UI.cs','"МАТЕРИАЛЫ: " + DesignerUI.Materials(chosen)','WeaponCatalog.Family(chosen.FamilyId).Label + " | МАТЕРИАЛЫ: " + DesignerUI.Materials(chosen)')
mod('UI.cs','"ОРУЖЕЙНАЯ БИБЛИОТЕКА  /  РАЗРАБОТАННЫЕ ЧЕРТЕЖИ"','"ОРУЖЕЙНАЯ БИБЛИОТЕКА  /  4 СЕМЕЙСТВА  /  РАЗРАБОТАННЫЕ ЧЕРТЕЖИ"')
mod('UI.cs','"Не хватает обязательных узлов: " + design.MissingCount','"Не хватает обязательных узлов: " + design.MissingCount') # no op
# Ensure research title and family visible in preview.
mod('BenchComps.cs','return "Сборка: " + b.Title + "\\nУзлов из пластали: "','return "Сборка: " + b.Title + " (" + WeaponCatalog.Family(b.FamilyId).Caliber + ")\\nУзлов из пластали: "')
