using System;
using RimWorld;
using Verse;

namespace ThornWhip
{
    // Aggregate once per blueprint instance, never per pawn or game tick. Five alternatives per required assembly.
    public sealed class WeaponTuning
    {
        public float Sights, Spread, Sway, Cooldown, Mass, Bulk, Value;
        public float Recoil, Warmup, Reload, Range, NightVision;
        public static WeaponTuning Evaluate(WeaponBlueprint b)
        {
            var t = new WeaponTuning();
            if (b == null) return t;
            t.Mass += WeaponCalibers.For(b).MassOffset;
            for (int i = 0; i < WeaponCatalog.RequiredFor(b).Length; i++)
            {
                if (b.SelectedPart(i) < 0) continue;
                t.Add(WeaponCatalog.RequiredFor(b)[i].Options[b.Part(i)]);
                if (b.Material(i) == 1)
                {
                    // Plasteel reduces mass, dimensional imprecision and heat distortion.
                    t.Mass -= .055f * WeaponCatalog.Family(b.FamilyId).Mass / 3.7f;
                    t.Bulk -= .025f * WeaponCatalog.Family(b.FamilyId).Bulk / 4.8f;
                    t.Spread -= .0007f;
                    t.Recoil -= .0025f;
                    t.Value += 16f;
                }
            }
            if (b.SelectedPart(10) < 0) { t.Sights -= .28f; t.Sway += .07f; }
            for (int i = 0; i < 3; i++)
            {
                int id = b.Extra(i);
                if (id >= 0) t.Add(WeaponCatalog.Specials[id].Effects);
            }
            return t;
        }
        private void Add(ModuleOption o)
        {
            Sights += o.Sights; Spread += o.Spread; Sway += o.Sway;
            Cooldown += o.Cooldown; Mass += o.Mass; Bulk += o.Bulk;
            Value += o.Value; Recoil += o.Recoil; Warmup += o.Warmup;
            Reload += o.Reload; Range += o.Range; NightVision += o.NightVision;
        }
        public static float QualityFactor(Thing thing)
        {
            var c = thing?.TryGetComp<CompQuality>();
            if (c == null) return 1f;
            switch (c.Quality)
            {
                case QualityCategory.Awful: return .76f;
                case QualityCategory.Poor: return .88f;
                case QualityCategory.Normal: return 1f;
                case QualityCategory.Good: return 1.07f;
                case QualityCategory.Excellent: return 1.13f;
                case QualityCategory.Masterwork: return 1.20f;
                case QualityCategory.Legendary: return 1.27f;
                default: return 1f;
            }
        }
        // Benefits scale up with good craftsmanship; disadvantages scale down.
        public static float Adjust(float delta, float quality, bool lowerIsBetter)
        {
            bool improvement = lowerIsBetter ? delta < 0 : delta > 0;
            return delta * (improvement ? quality : 1f / quality);
        }
    }
}
