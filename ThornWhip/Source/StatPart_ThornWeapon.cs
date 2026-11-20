using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace ThornWhip
{
    // CE reads weapon-instance GetStatValue for sights, sway, spread, recoil multiplier,
    // reload multiplier, range multiplier, and warmup multiplier. NEVER mutate shared Defs.
    public sealed class StatPart_ThornWeapon : StatPart
    {
        public override void TransformValue(StatRequest req, ref float val)
        {
            if (!req.HasThing || !WeaponCatalog.IsOurWeapon(req.Thing.def.defName)) return;
            var comp = req.Thing.TryGetComp<CompWeaponDesign>();
            if (comp == null) return;
            WeaponTuning t = comp.Tuning;
            float q = WeaponTuning.QualityFactor(req.Thing);
            switch (parentStat.defName)
            {
                case "SightsEfficiency": val = Math.Max(.1f, val + WeaponTuning.Adjust(t.Sights, q, false)); break;
                case "ShotSpread": val = Math.Max(.005f, val + WeaponTuning.Adjust(t.Spread, q, true)); break;
                case "SwayFactor": val = Math.Max(.25f, val + WeaponTuning.Adjust(t.Sway, q, true)); break;
                case "CE_RangedWeapon_RecoilMultiplier": val = Math.Max(.35f, val * (1f + WeaponTuning.Adjust(t.Recoil, q, true))); break;
                case "CE_RangedWeapon_ReloadFactor": val = Math.Max(.55f, val * (1f + WeaponTuning.Adjust(t.Reload, q, true))); break;
                case "RangedWeapon_WarmupMultiplier": val = Math.Max(.55f, val * (1f + WeaponTuning.Adjust(t.Warmup, q, true))); break;
                case "RangedWeapon_RangeMultiplier": val = Math.Max(.75f, val * (1f + WeaponTuning.Adjust(t.Range, q, false))); break;
                case "RangedWeapon_Cooldown": val = Math.Max(.22f, val * (1f + WeaponTuning.Adjust(t.Cooldown, q, true))); break;
                case "NightVisionEfficiency_Weapon": val = Math.Max(0f, val + WeaponTuning.Adjust(t.NightVision, q, false)); break;
                case "Mass": val = Math.Max(.50f, val + t.Mass); break;
                case "Bulk": val = Math.Max(.60f, val + t.Bulk); break;
                case "MarketValue": val = Math.Max(65f, val + t.Value * q); break;
            }
        }
        public override string ExplanationPart(StatRequest req)
        {
            if (!req.HasThing || req.Thing.TryGetComp<CompWeaponDesign>() == null) return null;
            return "Конструкция Терна: детали × материалы × качество; баллистика и типы боеприпасов обрабатываются CE";
        }
    }
    [StaticConstructorOnStartup]
    public static class StatInstaller
    {
        static StatInstaller()
        {
            // Hook only the relevant *stat pipelines*, not CE's projectile or damage functions.
            string[] stats = { "SightsEfficiency", "ShotSpread", "SwayFactor", "CE_RangedWeapon_RecoilMultiplier",
                "CE_RangedWeapon_ReloadFactor", "RangedWeapon_WarmupMultiplier", "RangedWeapon_RangeMultiplier",
                "RangedWeapon_Cooldown", "NightVisionEfficiency_Weapon", "Mass", "Bulk", "MarketValue" };
            foreach (var key in stats)
            {
                StatDef stat = DefDatabase<StatDef>.GetNamedSilentFail(key);
                if (stat == null) { Log.Warning("[ThornWhip] Optional StatDef absent: " + key); continue; }
                stat.parts ??= new List<StatPart>();
                bool installed = false;
                foreach (var p in stat.parts) if (p is StatPart_ThornWeapon) { installed = true; break; }
                if (!installed) stat.parts.Add(new StatPart_ThornWeapon { parentStat = stat });
            }
        }
    }
}
