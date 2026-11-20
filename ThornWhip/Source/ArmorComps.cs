using System.Collections.Generic;
using RimWorld;
using Verse;

namespace ThornWhip
{
    public sealed class CompProperties_ArmorDesign : CompProperties
    {public CompProperties_ArmorDesign(){compClass=typeof(CompArmorDesign);}}
    public sealed class CompArmorDesign : ThingComp
    {
        public ArmorBlueprint Blueprint;
        private ArmorTuning cache;
        public ArmorTuning Tuning => cache ??= ArmorTuning.Evaluate(Blueprint ?? ArmorBlueprint.BasicFor(parent?.def));
        public void SetBlueprint(ArmorBlueprint blueprint){Blueprint=blueprint?.Copy();cache=null;}
        public override void PostPostMake(){base.PostPostMake();Blueprint ??= ArmorBlueprint.BasicFor(parent?.def);}
        public override void PostExposeData()
        {
            base.PostExposeData();Scribe_Deep.Look(ref Blueprint,"tcArmorBuiltFrom");
            if(Scribe.mode==LoadSaveMode.PostLoadInit){Blueprint ??= ArmorBlueprint.BasicFor(parent?.def);cache=null;}
        }
        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach(var gizmo in base.CompGetGizmosExtra())yield return gizmo;
            yield return new Command_Action
            {
                defaultLabel="Паспорт брони",defaultDesc="Индивидуальная схема, защищённые зоны, набор модулей и показатели CE",
                action=()=>Find.WindowStack.Add(new Dialog_ArmorInspect(parent))
            };
        }
        public override string CompInspectStringExtra()
        {
            var b=Blueprint??ArmorBlueprint.BasicFor(parent?.def);
            return "Корпус Терна: "+b.Title+"\nБаза: "+b.Chassis.Label+
                "\nОбязательных узлов не установлено: "+b.MissingCount+
                "\nОсобых модулей: "+((b.Extra(0)>=0?1:0)+(b.Extra(1)>=0?1:0)+(b.Extra(2)>=0?1:0))+
                "\nCE: защита по поражённой зоне, а не абстрактный общий рейтинг";
        }
    }
}
