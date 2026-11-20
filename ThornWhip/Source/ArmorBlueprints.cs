using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace ThornWhip
{
    // A blueprint stores *specific parts*, not the nearest preset's aggregate stats.
    // ChassisId maps to one of nine immutable CE ThingDefs; per-item choices are deep-saved.
    public static class ArmorTechnology
    {
        public static bool Available(int tier)
        {
            ResearchProjectDef project = DefDatabase<ResearchProjectDef>.GetNamedSilentFail("TC_ArmorTech" + tier);
            return project != null && project.IsFinished;
        }
    }
    public sealed class ArmorBlueprint : IExposable
    {
        public string Title = "Корпус Терна — бронепроект";
        public int Identifier;
        public int ChassisId;
        public List<int> Parts = new List<int>();
        public List<int> Materials = new List<int>();
        public List<int> Specials = new List<int> { -1, -1, -1 };
        public ArmorChassis Chassis => ArmorCatalog.Base(ChassisId);
        public int Count => ArmorCatalog.Parts(this).Length;
        public ArmorBlueprint() { Resize(); }
        public void Resize()
        {
            var slots = ArmorCatalog.Parts(this);
            Parts ??= new List<int>(); Materials ??= new List<int>(); Specials ??= new List<int>();
            while (Parts.Count < slots.Length) Parts.Add(-1);
            while (Materials.Count < slots.Length) Materials.Add(0);
            while (Specials.Count < 3) Specials.Add(-1);
        }
        public void ChangeChassis(int id)
        {
            ChassisId = Math.Max(0,Math.Min(ArmorCatalog.Chassis.Length-1,id));
            Parts = new List<int>(); Materials = new List<int>(); Specials = new List<int>{-1,-1,-1};
            Resize(); Title = Chassis.Label + " — проект";
        }
        public int Part(int i)
        {
            var slots=ArmorCatalog.Parts(this);
            return i>=0 && i<slots.Length && i<Parts.Count && Parts[i]>=0 && Parts[i]<slots[i].Options.Length ? Parts[i] : -1;
        }
        public int Material(int i) => i>=0 && i<Materials.Count && Materials[i]>=0 && Materials[i]<=2 ? Materials[i] : 0;
        public int Extra(int i) => i>=0 && i<Specials.Count && Specials[i]>=0 && Specials[i]<ArmorCatalog.Specials.Length ? Specials[i] : -1;
        public int MissingCount
        {
            get {int n=0;var slots=ArmorCatalog.Parts(this);for(int i=0;i<slots.Length;i++)if(slots[i].Required && Part(i)<0)n++;return n;}
        }
        public bool RegionAllowed(string region)
        {
            if (region=="All" || region=="Torso") return true;
            if (Chassis.FamilyId==0) return false;
            if (region=="Head") return Chassis.FamilyId>=1;
            return true;
        }
        public bool IsValid
        {
            get
            {
                if(MissingCount>0) return false;
                var slots=ArmorCatalog.Parts(this);
                for(int i=0;i<slots.Length;i++)
                {
                    int id=Part(i); if(id<0)continue;
                    if(slots[i].Options[id].MinTier>Chassis.Tier || (Chassis.Tier==1 && Material(i)!=0))return false;
                }
                for(int i=0;i<3;i++)
                {
                    int id=Extra(i); if(id<0)continue;
                    ArmorOption o=ArmorCatalog.Specials[id];
                    if(o.MinTier>Chassis.Tier || !RegionAllowed(o.Region))return false;
                    for(int j=i+1;j<3;j++)if(id==Extra(j))return false;
                }
                return true;
            }
        }
        public ArmorBlueprint Copy() => new ArmorBlueprint { Title=Title,Identifier=Identifier,ChassisId=ChassisId,
            Parts=new List<int>(Parts),Materials=new List<int>(Materials),Specials=new List<int>(Specials) };
        public static ArmorBlueprint BasicFor(ThingDef def)
        {
            int id=ArmorCatalog.IndexOf(def?.defName);
            var b=new ArmorBlueprint();b.ChangeChassis(Math.Max(0,id));
            var slots=ArmorCatalog.Parts(b);
            for(int i=0;i<slots.Length;i++) if(slots[i].Required) b.Parts[i]=0;
            return b;
        }
        public void ExposeData()
        {
            Scribe_Values.Look(ref Title,"tcTitle","Корпус Терна — бронепроект");
            Scribe_Values.Look(ref Identifier,"tcId",0);
            Scribe_Values.Look(ref ChassisId,"tcChassis",0);
            Scribe_Collections.Look(ref Parts,"tcParts",LookMode.Value);
            Scribe_Collections.Look(ref Materials,"tcMaterials",LookMode.Value);
            Scribe_Collections.Look(ref Specials,"tcSpecials",LookMode.Value);
            if(Scribe.mode==LoadSaveMode.PostLoadInit) { ChassisId=Math.Max(0,Math.Min(8,ChassisId));Resize(); }
        }
    }
    public sealed class GameComponent_ArmorLibrary : GameComponent
    {
        public List<ArmorBlueprint> Developed=new List<ArmorBlueprint>();
        private int nextId=1;
        public GameComponent_ArmorLibrary(Game game) {}
        public void Register(ArmorBlueprint design)
        {
            if(design==null || !design.IsValid) return;
            ArmorBlueprint saved=design.Copy();saved.Identifier=nextId++;Developed.Add(saved);
            Messages.Message("Бронепроект разработан: "+saved.Title,MessageTypeDefOf.PositiveEvent,false);
        }
        public override void ExposeData()
        {
            Scribe_Collections.Look(ref Developed,"tcArmorDeveloped",LookMode.Deep);
            Scribe_Values.Look(ref nextId,"tcArmorNextId",1);
            if(Scribe.mode==LoadSaveMode.PostLoadInit) Developed ??= new List<ArmorBlueprint>();
        }
        public static GameComponent_ArmorLibrary Current => Verse.Current.Game?.GetComponent<GameComponent_ArmorLibrary>();
    }
    public sealed class Bill_ArmorResearch : Bill_Production
    {
        public ArmorBlueprint Blueprint;
        public Bill_ArmorResearch() {}
        public Bill_ArmorResearch(RecipeDef recipe,ArmorBlueprint blueprint):base(recipe)
        {Blueprint=blueprint.Copy();repeatMode=BillRepeatModeDefOf.RepeatCount;repeatCount=1;}
        public override void ExposeData(){base.ExposeData();Scribe_Deep.Look(ref Blueprint,"tcArmorResearch");}
    }
    public sealed class Bill_ArmorManufacture : Bill_Production
    {
        public ArmorBlueprint Blueprint;
        public bool Prepaid;
        public List<string> ResourceIds=new List<string>();
        public List<int> ResourceCounts=new List<int>();
        public Bill_ArmorManufacture() {}
        public Bill_ArmorManufacture(RecipeDef recipe,ArmorBlueprint blueprint):base(recipe)
        {Blueprint=blueprint.Copy();repeatMode=BillRepeatModeDefOf.RepeatCount;repeatCount=1;}
        public override void ExposeData()
        {
            base.ExposeData();Scribe_Deep.Look(ref Blueprint,"tcArmorCraft");
            Scribe_Values.Look(ref Prepaid,"tcArmorPrepaid",false);
            Scribe_Collections.Look(ref ResourceIds,"tcArmorResourceIds",LookMode.Value);
            Scribe_Collections.Look(ref ResourceCounts,"tcArmorResourceCounts",LookMode.Value);
            if(Scribe.mode==LoadSaveMode.PostLoadInit){ResourceIds ??= new List<string>();ResourceCounts ??= new List<int>();}
        }
    }
}
