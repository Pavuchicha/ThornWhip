using System;
using RimWorld;
using Verse;

namespace ThornWhip
{
    // Immutable after crafting; no CompTick, no pawn-wide armor or projectile simulation.
    public sealed class ArmorTuning
    {
        public float Sharp, Blunt, Heat, Mass, Bulk, WornBulk, Move, Carry, CarryBulk, Value;
        private readonly float[] partSharp=new float[7], partBlunt=new float[7];
        public static readonly string[] Regions={"Torso","Arm","Leg","Hand","Foot","Head","All"};
        public static int RegionId(string region)
        {for(int i=0;i<Regions.Length;i++)if(Regions[i]==region)return i;return 6;}
        public void Add(ArmorOption o,int material)
        {
            if(o==null)return;
            int region=RegionId(o.Region);
            if(region==6){Sharp+=o.Sharp;Blunt+=o.Blunt;}
            else {partSharp[region]+=o.Sharp;partBlunt[region]+=o.Blunt;}
            Heat+=o.Heat;Mass+=o.Mass;Bulk+=o.Bulk;WornBulk+=o.WornBulk;
            Move+=o.Move;Carry+=o.Carry;CarryBulk+=o.CarryBulk;Value+=o.Value;
            if(material==1) // plasteel: lighter, moderate protection
            {
                Mass-=.20f;WornBulk-=.06f;Value+=32f;
                if(region==6){Sharp+=.7f;Blunt+=1.2f;}else{partSharp[region]+=.7f;partBlunt[region]+=1.2f;}
            }
            else if(material==2) // uranium: dense, superior penetration resistance
            {
                Mass+=.95f;WornBulk+=.31f;Move-=.014f;Value+=46f;
                if(region==6){Sharp+=1.7f;Blunt+=2.8f;}else{partSharp[region]+=1.7f;partBlunt[region]+=2.8f;}
            }
        }
        public static ArmorTuning Evaluate(ArmorBlueprint b)
        {
            var t=new ArmorTuning();if(b==null)return t;
            var slots=ArmorCatalog.Parts(b);
            for(int i=0;i<slots.Length;i++)
            {int option=b.Part(i);if(option>=0)t.Add(slots[i].Options[option],b.Material(i));}
            for(int i=0;i<3;i++) {int id=b.Extra(i);if(id>=0)t.Add(ArmorCatalog.Specials[id],0);}
            return t;
        }
        public float ExtraForRegion(string region,bool sharp)
        {
            int index=RegionId(region);
            return (sharp?partSharp:partBlunt)[index];
        }
        public float Adjust(float raw,float quality,bool positiveGood)
        {
            bool isGood=positiveGood?raw>0:raw<0;
            return raw*(isGood?quality:1f/quality);
        }
        public static bool OptionalAreaAbsent(ArmorBlueprint b,string region)
        {
            // Medium chassis has soft limb support, but the hand/foot coverage is only real
            // when the corresponding optional protective assembly is installed.
            if(b==null || b.Chassis.FamilyId!=1)return false;
            if(region=="Hand")return b.Part(9)<0;
            if(region=="Foot")return b.Part(10)<0;
            if(region=="Head")return b.Part(12)<0;
            return false;
        }
        public static string RegionOf(BodyPartRecord part)
        {
            if(part==null)return "All";
            for(BodyPartRecord at=part;at!=null;at=at.parent)
            {
                string name=at.def?.defName ?? "";
                if(name=="Hand")return "Hand";
                if(name=="Foot")return "Foot";
                if(name=="Arm" || name=="Shoulder" || name=="UpperArm")return "Arm";
                if(name=="Leg" || name=="Thigh" || name=="Shin")return "Leg";
                if(name=="Head" || name=="Skull" || name=="Neck")return "Head";
                if(name=="Torso")return "Torso";
            }
            return "All";
        }
    }
}
