using System.Collections.Generic;
using RimWorld;
using Verse;

namespace ThornWhip
{
    public sealed class CompProperties_DesignTable : CompProperties
    { public CompProperties_DesignTable() { compClass = typeof(CompDesignTable); } }
    public sealed class CompProperties_FactoryTable : CompProperties
    { public CompProperties_FactoryTable() { compClass = typeof(CompFactoryTable); } }
    public sealed class CompDesignTable : ThingComp
    {
        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo item in base.CompGetGizmosExtra()) yield return item;
            yield return new Command_Action
            {
                defaultLabel = "Очередь исследований",
                defaultDesc = "Просмотреть и отменить исследования",
                action = () => Find.WindowStack.Add(new Dialog_ThornQueue(parent as Building_WorkTable))
            };
            yield return new Command_Action
            {
                defaultLabel = "Конструктор брони", defaultDesc = "3 класса брони × Т1–Т3, обязательные/необязательные узлы, улучшения CE",
                action = () => Find.WindowStack.Add(new Dialog_ArmorDesign(parent as Building_WorkTable))
            };
            yield return new Command_Action
            {
                defaultLabel = "Конструктор оружия",
                defaultDesc = "Выбрать оружейное семейство, 14 обязательных узлов × 5 вариантов, материалы и три универсальных слота (15 общих модулей).",
                action = () => Find.WindowStack.Add(new Dialog_WeaponDesign(parent as Building_WorkTable))
            };
        }
    }
    public sealed class CompFactoryTable : ThingComp
    {
        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo item in base.CompGetGizmosExtra()) yield return item;
            yield return new Command_Action
            {
                defaultLabel = "Очередь сборки",
                defaultDesc = "Просмотреть и отменить сборочные заказы",
                action = () => Find.WindowStack.Add(new Dialog_ThornQueue(parent as Building_WorkTable))
            };
            yield return new Command_Action
            {
                defaultLabel = "Разработанная броня", defaultDesc = "Заказ исследованных индивидуальных бронекомплектов",
                action = () => Find.WindowStack.Add(new Dialog_ArmorManufacture(parent as Building_WorkTable))
            };
            yield return new Command_Action
            {
                defaultLabel = "Разработанное оружие",
                defaultDesc = "Производить только законченные и исследованные проекты.",
                action = () => Find.WindowStack.Add(new Dialog_WeaponManufacture(parent as Building_WorkTable))
            };
        }
    }
    public sealed class CompProperties_WeaponDesign : CompProperties
    { public CompProperties_WeaponDesign() { compClass = typeof(CompWeaponDesign); } }
    public sealed class CompWeaponDesign : ThingComp
    {
        public override void PostDraw()
        {
            base.PostDraw();
            WeaponVisuals.DrawOnGround(parent);
        }
        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo original in base.CompGetGizmosExtra()) yield return original;
            yield return new Command_Action
            {
                defaultLabel = "Паспорт сборки",
                defaultDesc = "Визуальная схема именно этого оружия, установленные модули и параметры Combat Extended",
                action = () => Find.WindowStack.Add(new Dialog_WeaponInspect(parent))
            };
        }
        public WeaponBlueprint Blueprint;
        private WeaponTuning cached;
        public WeaponTuning Tuning => cached ??= WeaponTuning.Evaluate(Blueprint ?? WeaponBlueprint.BasicFor(parent?.def));
        public void SetBlueprint(WeaponBlueprint b) { Blueprint = b?.Copy(); cached = null; }
        public override void PostPostMake()
        {
            base.PostPostMake();
            Blueprint ??= WeaponBlueprint.BasicFor(parent?.def);
        }
        public override void PostExposeData()
        {
            base.PostExposeData(); Scribe_Deep.Look(ref Blueprint, "thornBuiltFrom");
            if (Scribe.mode == LoadSaveMode.PostLoadInit) { Blueprint ??= WeaponBlueprint.BasicFor(parent?.def); cached = null; }
        }
        public override string CompInspectStringExtra()
        {
            var b = Blueprint;
            if (b == null) return "Сборка: заводская (Combat Extended)";
            string mods = "";
            for (int i = 0; i < 3; i++) if (b.Extra(i) >= 0) mods += "\n  • " + WeaponCatalog.Specials[b.Extra(i)].Name;
            return "Сборка: " + b.Title + " (" + WeaponCalibers.For(b).Label + ")\nУзлов из пластали: " + b.PlasteelCount +
                "\nОсобых модификаций: " + b.SpecialCount + mods +
                "\nCE: пробитие/урон зависят от выбранного патрона";
        }
    }
}
