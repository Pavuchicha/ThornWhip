using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace ThornWhip
{
    // Costs are module-specific and deliberately not proportional to protection.
    // Escrow preserves the weapon v0.6 workflow, including its known hauling limitations.
    public static class ArmorCosts
    {
        private static void Add(IDictionary<string,int> a,string key,int count)
        {if(count==0)return;a.TryGetValue(key,out int old);a[key]=Math.Max(0,old+count);}
        private static void AddOption(IDictionary<string,int> result,ArmorOption o)
        {Add(result,"Steel",o.Steel);Add(result,"ComponentIndustrial",o.Industrial);
         Add(result,"ComponentSpacer",o.Advanced);Add(result,"Gold",o.Gold);}
        public static SortedDictionary<string,int> For(ArmorBlueprint b)
        {
            var cost=new SortedDictionary<string,int>(StringComparer.Ordinal);
            if(b==null)return cost;
            ArmorChassis c=b.Chassis;
            int m=c.FamilyId==0?18:c.FamilyId==1?55:130;
            Add(cost,"Steel",m*(c.Tier==1?1:0));
            Add(cost,"Plasteel",c.Tier==1?0:c.Tier==2?m/2:m);
            Add(cost,"ComponentIndustrial",c.FamilyId==0?2:c.FamilyId==1?7:18);
            Add(cost,"ComponentSpacer",c.Tier==1?0:c.Tier==2?2+c.FamilyId*3:7+c.FamilyId*6);
            if(c.Tier==3)Add(cost,"Gold",15+c.FamilyId*12);
            var slots=ArmorCatalog.Parts(b);
            for(int i=0;i<slots.Length;i++)
            {
                int j=b.Part(i);if(j<0)continue;
                var o=slots[i].Options[j];AddOption(cost,o);
                if(b.Material(i)==1){Add(cost,"Plasteel",8);Add(cost,"Steel",-Math.Min(3,o.Steel));}
                if(b.Material(i)==2){Add(cost,"Uranium",6);Add(cost,"Steel",-Math.Min(2,o.Steel));}
            }
            for(int i=0;i<3;i++){int id=b.Extra(i);if(id>=0)AddOption(cost,ArmorCatalog.Specials[id]);}
            return cost;
        }
        public static string Display(ArmorBlueprint b)
        {
            return string.Join(" · ",For(b).Where(p=>p.Value>0).Select(p=>p.Key+" ×"+p.Value));
        }
        public static string Display(ArmorOption o)
        {return "сталь "+o.Steel+" · комп. "+o.Industrial+" · продв. "+o.Advanced+" · золото "+o.Gold;}
        public static bool TryPrepay(Building_WorkTable bench,Bill_ArmorManufacture bill,out string error)
        {
            error=null;
            if(bench?.Map==null || bill?.Blueprint==null || !bill.Blueprint.IsValid){error="Неверный проект или верстак";return false;}
            var map=bench.Map;var required=For(bill.Blueprint);
            foreach(var pair in required)
            {
                if(pair.Value<=0)continue;
                ThingDef def=DefDatabase<ThingDef>.GetNamedSilentFail(pair.Key);
                if(def==null){error="Неизвестный ресурс: "+pair.Key;return false;}
                int available=0;
                foreach(Thing t in map.listerThings.ThingsOfDef(def))
                    if(t!=null && t.Spawned && !t.IsForbidden(Faction.OfPlayer))available+=t.stackCount;
                if(available<pair.Value){error="Не хватает: "+def.label+" ("+available+"/"+pair.Value+")";return false;}
            }
            foreach(var pair in required)
            {
                if(pair.Value<=0)continue;
                var def=DefDatabase<ThingDef>.GetNamedSilentFail(pair.Key);
                int left=pair.Value;
                foreach(Thing stack in map.listerThings.ThingsOfDef(def).ToList())
                {
                    if(left==0)break;
                    if(stack==null || !stack.Spawned || stack.IsForbidden(Faction.OfPlayer))continue;
                    int take=Math.Min(stack.stackCount,left);
                    Thing split=stack.SplitOff(take);split.Destroy(DestroyMode.Vanish);left-=take;
                }
                if(left!=0){Log.Error("[ThornCorps] Armor escrow race on "+pair.Key);return false;}
                bill.ResourceIds.Add(pair.Key);bill.ResourceCounts.Add(pair.Value);
            }
            bill.Prepaid=true;return true;
        }
        public static void Refund(Building_WorkTable bench,Bill_ArmorManufacture bill)
        {
            if(bill==null || !bill.Prepaid || bench?.Map==null)return;
            for(int i=0;i<bill.ResourceIds.Count && i<bill.ResourceCounts.Count;i++)
            {
                var def=DefDatabase<ThingDef>.GetNamedSilentFail(bill.ResourceIds[i]);
                if(def==null)continue;
                int count=bill.ResourceCounts[i];
                while(count>0)
                {
                    int take=Math.Min(count,def.stackLimit);
                    Thing thing=ThingMaker.MakeThing(def);
                    thing.stackCount=take;
                    GenPlace.TryPlaceThing(thing,bench.Position,bench.Map,ThingPlaceMode.Near);
                    count-=take;
                }
            }
            bill.Prepaid=false;bill.ResourceIds.Clear();bill.ResourceCounts.Clear();
        }
    }
}
