using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace ThornWhip
{
    // Cost attribution is per selected module, not proportional to stat strength.
    // Payment is reserved on bill creation. It is refunded only if the work is cancelled
    // before completion. This avoids generating combinatorial RecipeDefs for every design.
    // IMPORTANT: material reservation is immediate from available map stocks and does not
    // simulate hauling. An iteration of manufacturing still consumes normal work time.
    public static class WeaponCosts
    {
        public static SortedDictionary<string, int> ForBlueprint(WeaponBlueprint b)
        {
            var result = new SortedDictionary<string, int>(StringComparer.Ordinal);
            if (b == null) return result;
            var family = WeaponCatalog.Family(b.FamilyId);
            Add(result, "Steel", Math.Max(15, (int)Math.Round(family.Mass * 13f + 16f)));
            Add(result, "Steel", WeaponCalibers.For(b).ExtraSteel);
            Add(result, "ComponentIndustrial", WeaponCalibers.For(b).ExtraComponents);
            Add(result, "ComponentIndustrial", b.FamilyId == 2 ? 3 : b.FamilyId == 3 ? 8 : b.FamilyId == 1 ? 5 : 4);
            var slots = WeaponCatalog.RequiredFor(b);
            for (int i = 0; i < slots.Length; i++)
            {
                int index = b.SelectedPart(i);
                if (index < 0) continue;
                var option = slots[i].Options[index];
                AddOption(result, option);
                if (b.Material(i) == 1)
                {
                    // Plasteel replaces part of the steel in precisely this component.
                    Add(result, "Steel", -Math.Min(4, option.Steel));
                    Add(result, "Plasteel", 7 + (i == 2 || i == 9 ? 3 : 0));
                }
            }
            for (int i = 0; i < 3; i++)
            {
                int j = b.Extra(i);
                if (j >= 0) AddOption(result, WeaponCatalog.Specials[j].Effects);
            }
            return result;
        }
        private static void AddOption(IDictionary<string, int> c, ModuleOption o)
        {
            Add(c, "Steel", o.Steel);
            Add(c, "ComponentIndustrial", o.Industrial);
            Add(c, "ComponentSpacer", o.Advanced);
            Add(c, "Gold", o.Gold);
        }
        private static void Add(IDictionary<string, int> map, string key, int delta)
        {
            if (delta == 0) return;
            map.TryGetValue(key, out int old);
            map[key] = Math.Max(0, old + delta);
        }
        public static string Display(WeaponBlueprint b)
        {
            string[] names = { "Steel", "Plasteel", "ComponentIndustrial", "ComponentSpacer", "Gold" };
            string[] localized = { "сталь", "пласталь", "комп.", "продв. комп.", "золото" };
            var cost = ForBlueprint(b);
            var lines = new List<string>();
            for (int i = 0; i < names.Length; i++)
                if (cost.TryGetValue(names[i], out int count) && count > 0)
                    lines.Add(localized[i] + " " + count);
            return string.Join(" · ", lines);
        }
        public static string Display(ModuleOption o)
        {
            var labels = new List<string>();
            if (o.Steel > 0) labels.Add("сталь " + o.Steel);
            if (o.Industrial > 0) labels.Add("комп. " + o.Industrial);
            if (o.Advanced > 0) labels.Add("продв. " + o.Advanced);
            if (o.Gold > 0) labels.Add("золото " + o.Gold);
            return string.Join(" · ", labels);
        }
        // Single transaction: ensure all resources exist before changing any stacks.
        // Called only by a player's click, never in a Tick or a repeated pawn scan.
        public static bool TryPrepay(Building_WorkTable bench, Bill_WeaponManufacture bill, out string error)
        {
            error = null;
            if (bench?.Map == null || bill?.Blueprint == null) { error = "Верстак недоступен"; return false; }
            var map = bench.Map;
            var items = ForBlueprint(bill.Blueprint);
            foreach (var pair in items)
            {
                if (pair.Value <= 0) continue;
                var def = DefDatabase<ThingDef>.GetNamedSilentFail(pair.Key);
                if (def == null) { error = "Неизвестный ресурс: " + pair.Key; return false; }
                int available = 0;
                foreach (Thing t in map.listerThings.ThingsOfDef(def))
                    if (t != null && t.Spawned && !t.IsForbidden(Faction.OfPlayer)) available += t.stackCount;
                if (available < pair.Value)
                { error = "Не хватает ресурса «" + def.label + "»: " + available + "/" + pair.Value; return false; }
            }
            foreach (var pair in items)
            {
                if (pair.Value <= 0) continue;
                var def = DefDatabase<ThingDef>.GetNamedSilentFail(pair.Key);
                int remaining = pair.Value;
                // Copy: SplitOff may remove stacks from listerThings during iteration.
                var stacks = map.listerThings.ThingsOfDef(def).ToList();
                foreach (Thing t in stacks)
                {
                    if (remaining == 0) break;
                    if (t == null || !t.Spawned || t.IsForbidden(Faction.OfPlayer)) continue;
                    int taken = Math.Min(remaining, t.stackCount);
                    Thing reserved = t.SplitOff(taken);
                    reserved.Destroy(DestroyMode.Vanish);
                    remaining -= taken;
                }
                if (remaining != 0) { Log.Error("[ThornWhip] Reservation race for " + pair.Key); return false; }
                bill.PaidResourceIds.Add(pair.Key);
                bill.PaidResourceCounts.Add(pair.Value);
            }
            bill.Prepaid = true;
            return true;
        }
        public static void Refund(Building_WorkTable bench, Bill_WeaponManufacture bill)
        {
            if (bill == null || !bill.Prepaid || bench?.Map == null) return;
            for (int i = 0; i < bill.PaidResourceIds.Count && i < bill.PaidResourceCounts.Count; i++)
            {
                ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(bill.PaidResourceIds[i]);
                if (def == null || bill.PaidResourceCounts[i] <= 0) continue;
                int left = bill.PaidResourceCounts[i];
                while (left > 0)
                {
                    Thing item = ThingMaker.MakeThing(def);
                    int n = Math.Min(left, Math.Max(1, def.stackLimit));
                    item.stackCount = n;
                    GenPlace.TryPlaceThing(item, bench.Position, bench.Map, ThingPlaceMode.Near);
                    left -= n;
                }
            }
            bill.Prepaid = false;
            bill.PaidResourceCounts.Clear(); bill.PaidResourceIds.Clear();
        }
    }
}
