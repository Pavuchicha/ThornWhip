using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace ThornWhip
{
    public sealed class WeaponBlueprint : IExposable
    {
        public string Title = "Плеть Терна — проект";
        public int Identifier;
        public int FamilyId = 0; // V0.4 saves default to the rifle
        public int CaliberId = 0; // 0.8 CE conversion; old 0.7 designs keep the original caliber
        public List<int> Parts = Enumerable.Repeat(-1, 15).ToList();
        public List<int> Materials = Enumerable.Repeat(0, 15).ToList();
        // 3 universal optional slots; each value indexes WeaponCatalog.Specials, -1 means empty.
        public List<int> Special = Enumerable.Repeat(-1, 3).ToList();
        public int SelectedPart(int i) => Parts != null && i >= 0 && i < Parts.Count ? Math.Max(-1, Math.Min(WeaponCatalog.RequiredFor(this)[i].Options.Length-1, Parts[i])) : -1;
        public int Part(int i) => Math.Max(0, SelectedPart(i));
        // CE structural defs remain 0/1 for burst, barrel and magazine; other variants
        // vary the per-instance stats, costs and sprite, not the AmmoUser class itself.
        public int CoreIndex(int i) { int p = Part(i); return p == 1 || p == 3 || p == 4 ? 1 : 0; }
        public int Material(int i) => Materials != null && i >= 0 && i < Materials.Count && Materials[i] == 1 ? 1 : 0;
        public int Extra(int i) => Special != null && i >= 0 && i < Special.Count && Special[i] >= 0 && Special[i] < WeaponCatalog.Specials.Length ? Special[i] : -1;
        public int MissingCount { get { int n = 0; for (int i = 0; i < WeaponCatalog.RequiredFor(this).Length; i++) if (WeaponCatalog.RequiredFor(this)[i].Required && SelectedPart(i) < 0) n++; return n; } }
        public int PlasteelCount { get { int n = 0; for (int i = 0; i < WeaponCatalog.RequiredFor(this).Length; i++) if (SelectedPart(i) >= 0 && Material(i) == 1) n++; return n; } }
        public int SpecialCount { get { int n = 0; for (int i = 0; i < 3; i++) if (Extra(i) >= 0) n++; return n; } }
        public bool HasDuplicateSpecials
        {
            get { for (int i = 0; i < 3; i++) for (int j = i + 1; j < 3; j++) if (Extra(i) >= 0 && Extra(i) == Extra(j)) return true; return false; }
        }
        public string ValidationProblem
        {
            get
            {
                if (MissingCount > 0)
                {
                    var missing = new List<string>();
                    var slots = WeaponCatalog.RequiredFor(this);
                    for (int i = 0; i < slots.Length; i++)
                        if (slots[i].Required && SelectedPart(i) < 0) missing.Add(slots[i].Label);
                    return "Не установлены: " + string.Join(", ", missing);
                }
                if (HasDuplicateSpecials) return "Нельзя повторять одну и ту же уникальную модификацию.";
                if (!WeaponCalibers.Compatible(this)) return WeaponCalibers.Problem(this);
                return "";
            }
        }
        public bool IsValid => string.IsNullOrEmpty(ValidationProblem);
        public WeaponBlueprint Copy() => new WeaponBlueprint { Title = Title, Identifier = Identifier, FamilyId = FamilyId, CaliberId = CaliberId,
            Parts = new List<int>(Parts), Materials = new List<int>(Materials), Special = new List<int>(Special) };
        public static WeaponBlueprint BasicFor(ThingDef def)
        {
            // Trading/generation fallback: unresearched stock rifle. No partially completed firearms in combat.
            var b = new WeaponBlueprint { Title = "Терна — заводская", FamilyId = WeaponCatalog.FamilyFromDef(def?.defName), CaliberId=WeaponCalibers.IdFromDefName(def?.defName) };
            for (int i = 0; i < b.Parts.Count; i++) b.Parts[i] = 0;
            if (def != null && WeaponCatalog.IsOurWeapon(def.defName))
            {
                string[] s = def.defName.Split('_');
                foreach (string v in s)
                {
                    if (v.Length == 2 && v[0] == 'R') b.Parts[0] = v[1] == '1' ? 1 : 0;
                    if (v.Length == 2 && v[0] == 'B') b.Parts[2] = v[1] == '1' ? 1 : 0;
                    if (v.Length == 2 && v[0] == 'M') b.Parts[9] = v[1] == '1' ? 1 : 0;
                }
            }
            if (WeaponCalibers.For(b).NeedsHeavyConversion)
            {
                // Loaded from a trade/faction-generated CE ThingDef: the receiver,
                // barrel, bolt and magazine must form a physically consistent kit.
                foreach (int slot in new[] { 0, 2, 3, 9 })
                    if (b.SelectedPart(slot) != 1 && b.SelectedPart(slot) != 3 && b.SelectedPart(slot) != 4)
                        b.Parts[slot] = 1;
            }
            return b;
        }
        public void ExposeData()
        {
            Scribe_Values.Look(ref Title, "title", "Плеть Терна — проект");
            Scribe_Values.Look(ref Identifier, "identifier", 0);
            Scribe_Values.Look(ref FamilyId, "weaponFamily", 0);
            Scribe_Values.Look(ref CaliberId, "ceCaliber", 0);
            Scribe_Collections.Look(ref Parts, "partIndices", LookMode.Value);
            Scribe_Collections.Look(ref Materials, "partMaterials", LookMode.Value);
            Scribe_Collections.Look(ref Special, "specialIndices", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                Parts ??= new List<int>(); Materials ??= new List<int>(); Special ??= new List<int>();
                if (FamilyId < 0 || FamilyId >= WeaponCatalog.Families.Length) FamilyId = 0;
                if (CaliberId < 0 || CaliberId >= WeaponCalibers.Options(FamilyId).Length) CaliberId = 0;
                while (Parts.Count < WeaponCatalog.RequiredFor(this).Length) Parts.Add(-1);
                while (Materials.Count < WeaponCatalog.RequiredFor(this).Length) Materials.Add(0);
                while (Special.Count < 3) Special.Add(-1);
            }
        }
    }
    public sealed class GameComponent_WeaponLibrary : GameComponent
    {
        public List<WeaponBlueprint> Developed = new List<WeaponBlueprint>();
        private int nextId = 1;
        public GameComponent_WeaponLibrary(Game game) { }
        public void Register(WeaponBlueprint b)
        {
            if (b == null || !b.IsValid) { Log.Warning("[ThornWhip] Rejected incomplete research blueprint"); return; }
            var stored = b.Copy(); stored.Identifier = nextId++;
            Developed.Add(stored);
            Messages.Message("Разработка завершена: " + stored.Title, MessageTypeDefOf.PositiveEvent, false);
        }
        public override void ExposeData()
        {
            Scribe_Collections.Look(ref Developed, "developedBlueprints", LookMode.Deep);
            Scribe_Values.Look(ref nextId, "nextWeaponBlueprintId", 1);
            if (Scribe.mode == LoadSaveMode.PostLoadInit) Developed ??= new List<WeaponBlueprint>();
        }
        public static GameComponent_WeaponLibrary Current => Verse.Current.Game?.GetComponent<GameComponent_WeaponLibrary>();
    }
    public sealed class Bill_WeaponResearch : Bill_Production
    {
        public WeaponBlueprint Blueprint;
        public Bill_WeaponResearch() { }
        public Bill_WeaponResearch(RecipeDef recipe, WeaponBlueprint b) : base(recipe)
        { Blueprint = b.Copy(); repeatMode = BillRepeatModeDefOf.RepeatCount; repeatCount = 1; }
        public override void ExposeData() { base.ExposeData(); Scribe_Deep.Look(ref Blueprint, "thornBlueprint"); }
    }
    public sealed class Bill_WeaponManufacture : Bill_Production
    {
        public WeaponBlueprint Blueprint;
        public bool Prepaid;
        public List<string> PaidResourceIds = new List<string>();
        public List<int> PaidResourceCounts = new List<int>();
        public Bill_WeaponManufacture() { }
        public Bill_WeaponManufacture(RecipeDef recipe, WeaponBlueprint b) : base(recipe)
        { Blueprint = b.Copy(); repeatMode = BillRepeatModeDefOf.RepeatCount; repeatCount = 1; }
        public override void ExposeData()
        {
            base.ExposeData(); Scribe_Deep.Look(ref Blueprint, "thornBlueprint");
            Scribe_Values.Look(ref Prepaid, "thornResourcePrepaid", false);
            Scribe_Collections.Look(ref PaidResourceIds, "thornPaidIds", LookMode.Value);
            Scribe_Collections.Look(ref PaidResourceCounts, "thornPaidAmounts", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                PaidResourceIds ??= new List<string>(); PaidResourceCounts ??= new List<int>();
            }
        }
    }
}
