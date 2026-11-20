using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace ThornWhip
{
    public sealed class StatPart_ThornArmor : StatPart
    {
        public override void TransformValue(StatRequest req,ref float value)
        {
            if(!req.HasThing || !ArmorCatalog.IsArmor(req.Thing.def?.defName))return;
            var comp=req.Thing.TryGetComp<CompArmorDesign>();if(comp==null)return;
            var t=comp.Tuning;float q=WeaponTuning.QualityFactor(req.Thing);
            switch(parentStat.defName)
            {
                case "ArmorRating_Sharp":value=Math.Max(0f,value+t.Adjust(t.Sharp,q,true));break;
                case "ArmorRating_Blunt":value=Math.Max(0f,value+t.Adjust(t.Blunt,q,true));break;
                case "ArmorRating_Heat":value=Math.Max(0f,Math.Min(1f,value+t.Adjust(t.Heat,q,true)));break;
                case "Mass":value=Math.Max(.1f,value+t.Mass);break;
                case "Bulk":value=Math.Max(0f,value+t.Bulk);break;
                case "WornBulk":value=Math.Max(0f,value+t.WornBulk);break;
                case "MarketValue":value=Math.Max(1f,value+t.Value*q);break;
            }
        }
        public override string ExplanationPart(StatRequest req)
        {
            return req.HasThing && req.Thing.TryGetComp<CompArmorDesign>()!=null?
                "Корпус Терна: параметры экземпляра × материалы × качество; пробитие и попадания рассчитывает Combat Extended":null;
        }
    }
    public sealed class StatPart_ThornWorn : StatPart
    {
        public override void TransformValue(StatRequest req,ref float value)
        {
            if(!req.HasThing || req.Thing is not Pawn pawn || pawn.apparel==null)return;
            float delta=0;
            foreach(Apparel apparel in pawn.apparel.WornApparel)
            {
                var comp=apparel.TryGetComp<CompArmorDesign>();if(comp==null)continue;
                ArmorChassis baseArmor=(comp.Blueprint??ArmorBlueprint.BasicFor(apparel.def)).Chassis;
                float q=WeaponTuning.QualityFactor(apparel);var tuning=comp.Tuning;
                switch(parentStat.defName)
                {
                    case "MoveSpeed":delta+=baseArmor.Move+tuning.Adjust(tuning.Move,q,true);break;
                    case "CarryWeight":delta+=tuning.Adjust(tuning.Carry,q,true);break;
                    case "CarryBulk":delta+=tuning.Adjust(tuning.CarryBulk,q,true);break;
                }
            }
            value=parentStat.defName=="MoveSpeed"?Math.Max(.15f,value+delta):Math.Max(0,value+delta);
        }
        public override string ExplanationPart(StatRequest req) => null;
    }
    [StaticConstructorOnStartup]
    public static class ArmorStatInstaller
    {
        static ArmorStatInstaller()
        {
            foreach(string name in new[]{"ArmorRating_Sharp","ArmorRating_Blunt","ArmorRating_Heat","Mass","Bulk","WornBulk","MarketValue"})
            {
                var stat=DefDatabase<StatDef>.GetNamedSilentFail(name);if(stat==null)continue;
                stat.parts ??= new List<StatPart>();
                bool found=false;foreach(StatPart part in stat.parts)if(part is StatPart_ThornArmor){found=true;break;}
                if(!found)stat.parts.Add(new StatPart_ThornArmor{parentStat=stat});
            }
            foreach(string name in new[]{"MoveSpeed","CarryWeight","CarryBulk"})
            {
                var stat=DefDatabase<StatDef>.GetNamedSilentFail(name);if(stat==null)continue;
                stat.parts ??= new List<StatPart>();
                bool found=false;foreach(StatPart part in stat.parts)if(part is StatPart_ThornWorn){found=true;break;}
                if(!found)stat.parts.Add(new StatPart_ThornWorn{parentStat=stat});
            }
        }
    }
    // Hook only CE's per-part armor value. Do NOT replace armor penetration, projectile,
    // bullet damage, or CE's armor-layer loop. No extra work without Thorn armor equipped.
    public static class ArmorProtection
    {
        public static void TryInstall(Harmony harmony)
        {
            try
            {
                Type ce=AccessTools.TypeByName("CombatExtended.ArmorUtilityCE");
                if(ce==null){Log.Warning("[ThornCorps] CE armor utility unavailable; partial module protection disabled");return;}
                var part=AccessTools.Method(ce,"PartialStat",new[]{typeof(Apparel),typeof(StatDef),typeof(BodyPartRecord)});
                if(part==null){Log.Warning("[ThornCorps] CE PartialStat signature changed");return;}
                harmony.Patch(part,postfix:new HarmonyMethod(typeof(ArmorProtection),nameof(AfterCEPartialArmor)));
            }
            catch(Exception error){Log.Warning("[ThornCorps] CE armor partial hook disabled: "+error.Message);}
        }
        public static void AfterCEPartialArmor(Apparel apparel,StatDef stat,BodyPartRecord part,ref float __result)
        {
            if(apparel==null || !ArmorCatalog.IsArmor(apparel.def?.defName) || part==null)return;
            if(stat!=StatDefOf.ArmorRating_Sharp && stat!=StatDefOf.ArmorRating_Blunt)return;
            var comp=apparel.TryGetComp<CompArmorDesign>();if(comp==null)return;
            ArmorBlueprint b=comp.Blueprint ?? ArmorBlueprint.BasicFor(apparel.def);
            string area=ArmorTuning.RegionOf(part);
            if(ArmorTuning.OptionalAreaAbsent(b,area)){__result=0;return;}
            float q=WeaponTuning.QualityFactor(apparel);
            float bonus=comp.Tuning.ExtraForRegion(area,stat==StatDefOf.ArmorRating_Sharp);
            __result=Math.Max(0f,__result+comp.Tuning.Adjust(bonus,q,true));
        }
    }
}
