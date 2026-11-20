from pathlib import Path
root=Path(__file__).resolve().parent
s=root/'ThornWhip/Source'
def edit(name,before,after):
 p=s/name; text=p.read_text(); assert before in text,(name,before[:90]); p.write_text(text.replace(before,after))
edit('Blueprints.cs','public int FamilyId = 0; // V0.4 saves default to the rifle','public int FamilyId = 0; // V0.4 saves default to the rifle\n        public int CaliberId = 0; // 0.8 CE conversion; old 0.7 designs keep the original caliber')
edit('Blueprints.cs','public bool IsValid => MissingCount == 0 && !HasDuplicateSpecials;', 'public bool IsValid => MissingCount == 0 && !HasDuplicateSpecials && WeaponCalibers.Compatible(this);')
edit('Blueprints.cs','Identifier = Identifier, FamilyId = FamilyId,','Identifier = Identifier, FamilyId = FamilyId, CaliberId = CaliberId,')
edit('Blueprints.cs','FamilyId = WeaponCatalog.FamilyFromDef(def?.defName) };','FamilyId = WeaponCatalog.FamilyFromDef(def?.defName), CaliberId=WeaponCalibers.IdFromDefName(def?.defName) };')
edit('Blueprints.cs','Scribe_Values.Look(ref FamilyId, "weaponFamily", 0);','Scribe_Values.Look(ref FamilyId, "weaponFamily", 0);\n            Scribe_Values.Look(ref CaliberId, "ceCaliber", 0);')
edit('Blueprints.cs','if (FamilyId < 0 || FamilyId >= WeaponCatalog.Families.Length) FamilyId = 0;', 'if (FamilyId < 0 || FamilyId >= WeaponCatalog.Families.Length) FamilyId = 0;\n                if (CaliberId < 0 || CaliberId >= WeaponCalibers.Options(FamilyId).Length) CaliberId = 0;')
edit('WeaponCatalog.cs','public static string WeaponDefName(WeaponBlueprint b) =>\n            $"TT_{Family(b.FamilyId).Key}_R{b.CoreIndex(0)}_B{b.CoreIndex(2)}_M{b.CoreIndex(9)}";', 'public static string WeaponDefName(WeaponBlueprint b) =>\n            $"TT_{Family(b.FamilyId).Key}_R{b.CoreIndex(0)}_B{b.CoreIndex(2)}_M{b.CoreIndex(9)}" + (b.CaliberId==0 ? "" : "_C"+b.CaliberId);')
edit('WeaponCatalog.cs','return $"{prefix}_R{b.CoreIndex(0)}_B{b.CoreIndex(2)}_M{b.CoreIndex(9)}";', 'return $"{prefix}_R{b.CoreIndex(0)}_B{b.CoreIndex(2)}_M{b.CoreIndex(9)}" + (b.CaliberId==0 ? "" : "_C"+b.CaliberId);')
edit('WeaponCosts.cs','Add(result, "Steel", Math.Max(15, (int)Math.Round(family.Mass * 13f + 16f)));','Add(result, "Steel", Math.Max(15, (int)Math.Round(family.Mass * 13f + 16f)));\n            Add(result, "Steel", WeaponCalibers.For(b).ExtraSteel);\n            Add(result, "ComponentIndustrial", WeaponCalibers.For(b).ExtraComponents);')
edit('WeaponTuning.cs','var t = new WeaponTuning();\n            if (b == null) return t;', 'var t = new WeaponTuning();\n            if (b == null) return t;\n            t.Mass += WeaponCalibers.For(b).MassOffset;')
edit('BenchComps.cs','WeaponCatalog.Family(b.FamilyId).Caliber + ")\\nУзлов', 'WeaponCalibers.For(b).Label + ")\\nУзлов')
edit('UI.cs','family.Magazine[b.CoreIndex(9)]','WeaponCalibers.Capacity(b)')
edit('UI.cs','"КАЛИБР: " + family.Caliber + "  |  урон/пробитие — от боеприпаса CE"','"КАЛИБР: " + WeaponCalibers.For(b).Label + "  |  урон/пробитие — от боеприпаса CE"')
edit('UI.cs','design.FamilyId = target;','design.FamilyId = target;\n                        design.CaliberId = 0;')
# selection menu between family tabs and viewport; move viewport 42px down, reduce tall UI area? preserve existing layout but overlay selection beneath tabs with viewport slightly lower.
edit('UI.cs','// Technical preview / layers.\n            Rect viewport = new Rect(13, 116, leftWidth, 237);', '''// A conversion stays on the SAME base; individual weapon instances are backed by a CE ammoSet.
            var calibers=WeaponCalibers.Options(design.FamilyId);
            DesignerUI.Txt(new Rect(17, 115, 125, 30), "ПАТРОН CE", DesignerUI.Brass);
            if (DesignerUI.Action(new Rect(142, 114, Mathf.Min(265, leftWidth-153), 32),
                WeaponCalibers.For(design).Label+"  ▾"))
            {
                var choices=new List<FloatMenuOption>();
                for(int ci=0;ci<calibers.Length;ci++)
                {
                    int chosen=ci;
                    choices.Add(new FloatMenuOption(calibers[ci].Label,()=>design.CaliberId=chosen));
                }
                Find.WindowStack.Add(new FloatMenu(choices));
            }
            // Technical preview / layers.
            Rect viewport = new Rect(13, 151, leftWidth, 202);''')
edit('UI.cs','design.IsValid ? "ПРОЕКТ ГОТОВ К РАЗРАБОТКЕ" : "ОШИБКА: ПОВТОР ОДНОЙ МОДИФИКАЦИИ",','design.IsValid ? "ПРОЕКТ ГОТОВ К РАЗРАБОТКЕ" :\n                (!WeaponCalibers.Compatible(design) ? WeaponCalibers.Problem(design) : "ОШИБКА: ПОВТОР ОДНОЙ МОДИФИКАЦИИ"),')
# if a gun is fired with CE recoilAmount def, profile changes recoil via per-instance stat factor
edit('UI.cs','float recoil = Math.Max(.35f, 1f + WeaponTuning.Adjust(t.Recoil, quality, true));','float recoil = Math.Max(.35f, WeaponCalibers.For(b).RecoilFactor * (1f + WeaponTuning.Adjust(t.Recoil, quality, true)));')
p=s/'StatPart_ThornWeapon.cs';text=p.read_text();print('StatPart contains',text[:1400]);
