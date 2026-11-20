using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace ThornWhip
{
    [StaticConstructorOnStartup]
    public static class HarmonyStartup
    {
        private static bool overlaysEnabled = true;
        static HarmonyStartup()
        {
            // Only 2 narrow event hooks. No Tick(), no global pawn/world scans.
            var harmony = new Harmony("thornwhip.marksman.rifles");
            harmony.PatchAll(typeof(HarmonyStartup).Assembly);
            ArmorProtection.TryInstall(harmony);
            ThornFortressGeneration.Install(harmony);
            ThornTurretCombatGate.Install(harmony);
            // Render-event only: never change CE projectiles, verbs, ammo, damage or AI.
            // On 1.7, the historic entrypoint may be renamed by other rendering mods;
            // in that case the designer/inspect preview still works and the error is logged.
            try
            {
                var method = AccessTools.Method(typeof(PawnRenderUtility), "DrawEquipmentAiming");
                if (method != null && method.GetParameters().Length == 3)
                    harmony.Patch(method, postfix: new HarmonyMethod(typeof(HarmonyStartup), nameof(DrawWeaponPostfix)));
                else Log.Warning("[ThornWhip] Weapon draw entrypoint signature changed; overlays in hands are disabled, preview and ground visuals remain.");
            }
            catch (Exception error) { Log.Warning("[ThornWhip] Equipment overlay hook disabled: " + error.Message); }
        }
        public static void DrawWeaponPostfix(Thing eq, Vector3 drawLoc, float aimAngle)
        {
            if (!overlaysEnabled || eq == null || eq.def == null || !WeaponCatalog.IsOurWeapon(eq.def.defName)) return;
            try { WeaponVisuals.DrawWorld(eq, drawLoc, aimAngle); }
            catch (Exception failure)
            {
                overlaysEnabled = false;
                Log.Warning("[ThornWhip] World overlay disabled after rendering error: " + failure.Message);
            }
        }
    }
    [HarmonyPatch(typeof(Bill_Production), nameof(Bill_Production.Notify_IterationCompleted))]
    public static class Patch_ResearchCompleted
    {
        public static void Postfix(Bill_Production __instance, Pawn billDoer, List<Thing> ingredients)
        {
            if (__instance is Bill_WeaponResearch research && research.Blueprint != null &&
                research.recipe?.defName == "TT_DevelopDesign")
                GameComponent_WeaponLibrary.Current?.Register(research.Blueprint);
            if (__instance is Bill_ArmorResearch ar && ar.Blueprint != null &&
                ar.recipe?.defName == "TC_DevelopArmor") GameComponent_ArmorLibrary.Current?.Register(ar.Blueprint);
            if (__instance is Bill_ArmorManufacture am && am.Prepaid)
            { am.Prepaid = false; am.ResourceIds.Clear(); am.ResourceCounts.Clear(); }
            if (__instance is Bill_WeaponManufacture manufacture && manufacture.Prepaid)
            {
                // Completed bills must never refund their prepaid materials.
                manufacture.Prepaid = false;
                manufacture.PaidResourceIds.Clear();
                manufacture.PaidResourceCounts.Clear();
            }
        }
    }
    [HarmonyPatch(typeof(GenRecipe), nameof(GenRecipe.MakeRecipeProducts))]
    public static class Patch_WeaponCrafted
    {
        public static void Postfix(ref IEnumerable<Thing> __result, RecipeDef recipeDef, Pawn worker, IBillGiver billGiver)
        {
            if (recipeDef?.defName == null) return;
            if (recipeDef.defName.StartsWith("TC_Craft_Armor_", StringComparison.Ordinal))
            {
                if (worker?.CurJob?.bill is Bill_ArmorManufacture armor && armor.Blueprint != null)
                    __result=AttachArmorBlueprint(__result,armor.Blueprint.Copy());
                return;
            }
            if (!recipeDef.defName.StartsWith("TT_Craft_", StringComparison.Ordinal)) return;
            if (worker?.CurJob?.bill is not Bill_WeaponManufacture order || order.Blueprint == null) return;
            // Materializing at enumeration-time preserves normal CE+RimWorld quality crafting.
            __result = AttachBlueprint(__result, order.Blueprint.Copy());
        }
        private static IEnumerable<Thing> AttachArmorBlueprint(IEnumerable<Thing> result, ArmorBlueprint design)
        {
            foreach (Thing item in result)
            {
                if (item?.TryGetComp<CompArmorDesign>() is CompArmorDesign comp)
                    comp.SetBlueprint(design);
                yield return item;
            }
        }
        private static IEnumerable<Thing> AttachBlueprint(IEnumerable<Thing> result, WeaponBlueprint design)
        {
            foreach (Thing item in result)
            {
                if (item?.TryGetComp<CompWeaponDesign>() is CompWeaponDesign comp)
                    comp.SetBlueprint(design);
                yield return item;
            }
        }
    }
}
