using System;
using HarmonyLib;
using RimWorld;
using Verse;

namespace ThornWhip
{
    // A single generation-time hook, restricted to three custom pawn kinds.
    // Combat Extended still owns pawn loadouts, inventory, magazine loading and ammunition.
    [HarmonyPatch(typeof(PawnGenerator), nameof(PawnGenerator.GeneratePawn),
        new Type[] { typeof(PawnGenerationRequest) })]
    public static class Patch_ThornGearAtGeneration
    {
        public static void Postfix(Pawn __result)
        {
            if (__result?.kindDef?.defName == null || !__result.kindDef.defName.StartsWith("TC_",StringComparison.Ordinal)) return;
            foreach (Thing weapon in __result.equipment.AllEquipmentListForReading)
            {
                if (weapon?.def == null || !WeaponCatalog.IsOurWeapon(weapon.def.defName)) continue;
                var comp=weapon.TryGetComp<CompWeaponDesign>();
                if (comp==null) continue;
                WeaponBlueprint bp=WeaponBlueprint.BasicFor(weapon.def);
                bp.Title="Корпус Терна / заводская конфигурация " + __result.kindDef.label;
                var slots=WeaponCatalog.RequiredFor(bp);
                for (int i=0; i<slots.Length; i++)
                {
                    if (!slots[i].Required && Rand.Value < .30f) {bp.Parts[i]=-1;continue;}
                    int idx=Rand.Range(0,slots[i].Options.Length);
                    if(WeaponCalibers.For(bp).NeedsHeavyConversion && (i==0||i==2||i==3||i==9))
                    { int[] reinforced={1,3,4};idx=reinforced[Rand.Range(0,reinforced.Length)]; }
                    bp.Parts[i]=idx;
                    bp.Materials[i]=Rand.Value<.30f?1:0;
                }
                for(int i=0;i<3;i++)
                {
                    if(Rand.Value>.27f)continue;
                    int chosen=Rand.Range(0,WeaponCatalog.Specials.Length);
                    bool duplicate=false;for(int j=0;j<i;j++)if(bp.Extra(j)==chosen)duplicate=true;
                    if(!duplicate)bp.Special[i]=chosen;
                }
                if(bp.IsValid)comp.SetBlueprint(bp);
            }
            foreach (Apparel armor in __result.apparel.WornApparel)
            {
                if(armor?.def?.defName == null || !armor.def.defName.StartsWith("TC_Armor_",StringComparison.Ordinal))continue;
                var comp=armor.TryGetComp<CompArmorDesign>();if(comp==null)continue;
                ArmorBlueprint bp=ArmorBlueprint.BasicFor(armor.def);
                bp.Title="Корпус Терна / гарнизонный комплект";
                var slots=ArmorCatalog.Parts(bp);
                for(int i=0;i<slots.Length;i++)
                {
                    if(!slots[i].Required && Rand.Value<.35f){bp.Parts[i]=-1;continue;}
                    int[] allowed=new int[slots[i].Options.Length];int count=0;
                    for(int j=0;j<slots[i].Options.Length;j++)if(slots[i].Options[j].MinTier<=bp.Chassis.Tier)allowed[count++]=j;
                    if(count>0)bp.Parts[i]=allowed[Rand.Range(0,count)];
                    bp.Materials[i]=bp.Chassis.Tier>1 && Rand.Value<.20f?1:0;
                }
                for(int i=0;i<3;i++)
                {
                    if(Rand.Value>.27f)continue;
                    for(int tries=0;tries<8;tries++)
                    {
                        int extra=Rand.Range(0,ArmorCatalog.Specials.Length);
                        var option=ArmorCatalog.Specials[extra];
                        if(option.MinTier>bp.Chassis.Tier || !bp.RegionAllowed(option.Region))continue;
                        bool dupe=false;for(int j=0;j<i;j++)if(bp.Extra(j)==extra)dupe=true;
                        if(!dupe){bp.Specials[i]=extra;break;}
                    }
                }
                if(bp.IsValid)comp.SetBlueprint(bp);
            }
        }
    }
}
