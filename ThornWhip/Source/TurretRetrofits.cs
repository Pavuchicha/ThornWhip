using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace ThornWhip
{
    // Dedicated data source for the retrofit system. Only deployed turrets enter the work queue.
    public sealed class CompProperties_ThornTurret : CompProperties
    { public CompProperties_ThornTurret() { compClass = typeof(CompThornTurret); } }

    public sealed class CompThornTurret : ThingComp, IThingHolder
    {
        private string targetDef;
        private int workLeft;
        private ThingOwner<Thing> delivered;
        private ThingOwner<Thing> mounted;
        private string pendingHolderWeapon;
        private bool holderAdapterReady;
        private static bool warnedMissingGunField;

        public string Family
        {
            get
            {
                string n = parent?.def?.defName ?? "";
                if (!n.StartsWith("TC_Turret_", StringComparison.Ordinal)) return "";
                string body = n.Substring("TC_Turret_".Length);
                int underscore = body.IndexOf('_');
                return underscore < 0 ? body : body.Substring(0, underscore);
            }
        }
        public bool IsPending => !string.IsNullOrEmpty(targetDef);
        public bool IsReady => IsPending && MaterialOutstanding() == null;
        public int WorkLeft => workLeft;
        public ThingWithComps MountedWeapon => mounted?.FirstOrDefault() as ThingWithComps;
        public bool HolderAdapterReady => holderAdapterReady;

        public override void Initialize(CompProperties props)
        {
            base.Initialize(props);
            delivered = new ThingOwner<Thing>(this);
            mounted = new ThingOwner<Thing>(this);
        }
        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            parent.Map?.GetComponent<MapComponent_ThornDefenseJobs>()?.Register(this);
            if (Family == "Holder") SyncHolderGun();
        }
        public override void PostDestroy(DestroyMode mode, Map previousMap)
        {
            previousMap?.GetComponent<MapComponent_ThornDefenseJobs>()?.Unregister(this);
            // Never silently delete expensive delivered upgrade resources or the mounted gun.
            if (previousMap != null && parent.Position.IsValid)
            {
                delivered?.TryDropAll(parent.Position, previousMap, ThingPlaceMode.Near);
                mounted?.TryDropAll(parent.Position, previousMap, ThingPlaceMode.Near);
            }
            base.PostDestroy(mode, previousMap);
        }
        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref targetDef, "TC_retrofitTarget");
            Scribe_Values.Look(ref workLeft, "TC_retrofitWork", 0);
            Scribe_Values.Look(ref pendingHolderWeapon, "TC_holderIntent");
            Scribe_Deep.Look(ref delivered, "TC_retrofitMaterials", this);
            Scribe_Deep.Look(ref mounted, "TC_mountedWeapon", this);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                delivered ??= new ThingOwner<Thing>(this);
                mounted ??= new ThingOwner<Thing>(this);
            }
        }
        public ThingOwner GetDirectlyHeldThings() => delivered;
        public void GetChildHolders(List<IThingHolder> outChildren)
        {
            ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, delivered);
            ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, mounted);
        }
        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            if (parent.Faction != Faction.OfPlayer) yield break;
            foreach (var original in base.CompGetGizmosExtra()) yield return original;
            yield return new Command_Action
            {
                defaultLabel = "Модифицировать турель",
                defaultDesc = "Выбор профиля; доставка материалов и строительная модернизация на месте. Пока проект не закончен, орудие отключено.",
                action = OpenRetrofit
            };
            if (Family == "Holder")
                yield return new Command_Action
                {
                    defaultLabel = "Оружие на станине",
                    defaultDesc = "Экспериментальная универсальная станина для личного стрелкового оружия. Оружие должно быть доставлено оператором.",
                    action = () => Find.WindowStack.Add(new Dialog_ThornHolder(this))
                };
            if (IsPending)
                yield return new Command_Action
                {
                    defaultLabel = "Отменить модернизацию",
                    defaultDesc = "Прерывает строительный заказ и выгружает доставленные материалы рядом с турелью.",
                    action = Cancel
                };
        }
        // RimWorld routes right-click orders on a Thing through ThingComp.
        public override IEnumerable<FloatMenuOption> CompFloatMenuOptions(Pawn selPawn)
        {
            foreach (var option in base.CompFloatMenuOptions(selPawn)) yield return option;
            if (selPawn == null || selPawn.Faction != Faction.OfPlayer || parent.Faction != Faction.OfPlayer) yield break;
            yield return new FloatMenuOption("Корпус Терна: изменить турель", OpenRetrofit);
            if (Family == "Holder" && selPawn.equipment?.Primary != null)
            {
                var gun = selPawn.equipment.Primary;
                yield return new FloatMenuOption("Корпус Терна: вставить «" + gun.LabelShort + "»", () => QueueMount(selPawn, gun));
            }
        }
        private void OpenRetrofit() => Find.WindowStack.Add(new Dialog_ThornRetrofit(this));

        public IEnumerable<ThingDef> UpgradeChoices()
        {
            string prefix = "TC_Turret_" + Family;
            // DefDatabase is scanned only when UI is open; never each tick.
            return DefDatabase<ThingDef>.AllDefsListForReading.Where(d => d.defName == prefix || d.defName.StartsWith(prefix + "_", StringComparison.Ordinal));
        }
        private bool CanFit(ThingDef next)
        {
            var map=parent.Map;
            if (next==null || map==null)return false;
            var at=parent.Position;
            for(int x=0;x<next.size.x;x++)
            for(int z=0;z<next.size.z;z++)
            {
                var c=new IntVec3(at.x+x,0,at.z+z);
                if(!c.InBounds(map))return false;
                foreach(var other in map.thingGrid.ThingsListAtFast(c))
                    if(other!=parent && (other.def.category==ThingCategory.Building || other is Pawn))return false;
            }
            return true;
        }
        public bool Request(ThingDef next)
        {
            if (!parent.Spawned || parent.Faction != Faction.OfPlayer || next == null || next == parent.def || next.building?.turretGunDef == null) return false;
            if (!UpgradeChoices().Contains(next) || !CanFit(next)) return false;
            Cancel(); targetDef = next.defName;
            var current = parent.def.building?.turretGunDef;
            var incoming = next.building?.turretGunDef;
            // Building cost is already paid; only differences between weapon modules are charged.
            workLeft = 1700 + (Family == "Railgun" || Family == "MLRS" ? 2400 : 750);
            parent.Map?.GetComponent<MapComponent_ThornDefenseJobs>()?.Register(this);
            return true;
        }
        public Dictionary<ThingDef,int> RequiredMaterials()
        {
            var result = new Dictionary<ThingDef,int>();
            if (!IsPending) return result;
            void Add(string name,int qty) { var d=DefDatabase<ThingDef>.GetNamedSilentFail(name); if(d!=null && qty>0) result[d]=qty; }
            Add("Steel", Family == "Railgun" || Family == "MLRS" ? 90 : 40);
            Add("ComponentIndustrial", Family == "Holder" ? 1 : 3);
            if(Family != "Holder") Add("Plasteel", Family == "Minigun" ? 15 : 27);
            if(Family == "Laser" || Family == "Blaster" || Family == "Railgun") Add("ComponentSpacer", 2);
            return result;
        }
        public ThingDef MaterialOutstanding()
        {
            foreach (var pair in RequiredMaterials())
                if (Required(pair.Key) > Delivered(pair.Key)) return pair.Key;
            return null;
        }
        public int Required(ThingDef d) => RequiredMaterials().TryGetValue(d,out var count) ? count : 0;
        public int Delivered(ThingDef def)
        {
            if (delivered == null) return 0;
            int count = 0; foreach(Thing x in delivered) if(x.def==def) count+=x.stackCount;
            return count;
        }
        public int Needed(ThingDef def) => Math.Max(0, Required(def) - Delivered(def));
        public int Deposit(Thing thing, int limit)
        {
            if (!IsPending || thing == null || thing.stackCount <= 0) return 0;
            int take = Math.Min(Math.Min(thing.stackCount,limit), Needed(thing.def));
            if (take <= 0) return 0;
            Thing piece = thing.stackCount == take ? thing : thing.SplitOff(take);
            return delivered.TryAdd(piece, true) ? take : 0;
        }
        public void Work(int ticks) { if(IsReady) workLeft = Math.Max(0, workLeft - ticks); if(IsReady && workLeft==0) Finish(); }
        public void Cancel()
        {
            targetDef = null; workLeft = 0;
            if(parent.Spawned && delivered != null) delivered.TryDropAll(parent.Position,parent.Map,ThingPlaceMode.Near);
        }
        private void Finish()
        {
            var replacement = DefDatabase<ThingDef>.GetNamedSilentFail(targetDef);
            if (replacement == null || !parent.Spawned || !CanFit(replacement)) { Cancel(); return; }
            var map = parent.Map; var pos = parent.Position; var faction = parent.Faction;
            int hp = parent.HitPoints; int oldMax=parent.MaxHitPoints;
            var savedGun=MountedWeapon;
            if (savedGun != null) mounted.Remove(savedGun);
            var prev=parent;
            // Never mutate ThingDef at runtime: replacing the Thing preserves CE's gun-profile integrity.
            prev.DeSpawn(DestroyMode.Vanish);
            Thing next=null;
            try
            {
                next=ThingMaker.MakeThing(replacement);
                next.SetFaction(faction);
                GenSpawn.Spawn(next,pos,map,WipeMode.Vanish);
                next.HitPoints = Math.Max(1,Math.Min(next.MaxHitPoints, (int)Math.Round((float)hp / Math.Max(1,oldMax) * next.MaxHitPoints)));
                var comp=next.TryGetComp<CompThornTurret>();
                if(savedGun != null && comp != null) {comp.mounted.TryAdd(savedGun,true);comp.SyncHolderGun();}
                delivered.ClearAndDestroyContents();
            }
            catch(Exception ex)
            {
                Log.Error("[ThornCorps] turret retrofit replacement failed: " + ex);
                if (next?.Spawned == true) next.DeSpawn(DestroyMode.Vanish);
                try{GenSpawn.Spawn(prev,pos,map,WipeMode.Vanish);}catch(Exception restore){Log.Error("[ThornCorps] cannot restore prior turret: " + restore);}
                if(savedGun != null) mounted.TryAdd(savedGun,true);
                Cancel();
            }
        }
        public bool QueueMount(Pawn pawn, ThingWithComps weapon)
        {
            if (pawn == null || weapon == null || Family != "Holder" || !parent.Spawned || pawn.Faction != Faction.OfPlayer || parent.Faction != Faction.OfPlayer) return false;
            // No weapon deletion: the actual pawn-held weapon is transferred to a ThingOwner by an explicit job.
            JobDef def=DefDatabase<JobDef>.GetNamedSilentFail("TC_MountWeapon");if(def==null)return false;
            pawn.jobs.TryTakeOrderedJob(JobMaker.MakeJob(def,parent));return true;
        }
        public bool MountFrom(Pawn pawn)
        {
            if (Family != "Holder" || pawn.equipment?.Primary == null) return false;
            ThingWithComps weapon=pawn.equipment.Primary;
            if(mounted.Count>0) mounted.TryDropAll(parent.Position,parent.Map,ThingPlaceMode.Near);
            pawn.equipment.Remove(weapon);
            if (!mounted.TryAdd(weapon,true)) return false;
            SyncHolderGun();return true;
        }
        public bool MountFactoryWeapon(ThingWithComps weapon)
        {
            if (weapon == null || Family != "Holder" || mounted.Count > 0) return false;
            if(!mounted.TryAdd(weapon,true)) return false;
            SyncHolderGun(); return true;
        }
        public bool RemoveMounted()
        {
            if(Family!="Holder" || MountedWeapon==null || !parent.Spawned)return false;
            mounted.TryDropAll(parent.Position,parent.Map,ThingPlaceMode.Near);
            SyncHolderGun();return true;
        }
        public void SyncHolderGun()
        {
            if(Family!="Holder")return;
            holderAdapterReady=false;
            try
            {
                var ce=AccessTools.TypeByName("CombatExtended.Building_TurretGunCE");
                if(ce==null)return;
                FieldInfo field=null;
                for (Type t=parent.GetType(); t!=null; t=t.BaseType)
                {
                    field=t.GetField("gun",BindingFlags.Instance|BindingFlags.NonPublic|BindingFlags.Public) ?? t.GetField("turretGun",BindingFlags.Instance|BindingFlags.NonPublic|BindingFlags.Public);
                    if(field!=null)break;
                }
                if (field==null)
                {
                    if (!warnedMissingGunField){warnedMissingGunField=true; Log.Warning("[ThornCorps] CE gun field unavailable: arbitrary-weapon holder stays disabled until CE adapter is updated");}
                    return;
                }
                if (MountedWeapon != null && field.FieldType.IsAssignableFrom(MountedWeapon.GetType()))
                {
                    field.SetValue(parent,MountedWeapon);
                    holderAdapterReady=ReferenceEquals(field.GetValue(parent),MountedWeapon);
                }
            }
            catch(Exception e){Log.Warning("[ThornCorps] holder CE-weapon handoff failed, firing disabled: " + e.Message);}
        }
        public override string CompInspectStringExtra()
        {
            if (IsPending)
            {
                string remaining = string.Join(", ",RequiredMaterials().Select(p=>p.Key.LabelCap+" "+Delivered(p.Key)+"/"+p.Value));
                return "РЕКОНСТРУКЦИЯ: оружие отключено\n"+remaining+"\nРабота: "+Math.Max(0,workLeft)+" тиков";
            }
            if(Family=="Holder")return "Оружие на станине: "+(MountedWeapon?.LabelCap??"отсутствует")+"\nБоевой режим: "+(MountedWeapon==null?"выключен":(holderAdapterReady?"CE адаптер подключён":"CE адаптер недоступен"));
            return "Корпус Терна / " + Family + "\nПереоснащение: доступно";
        }
    }

    // One registry per map; only retrofit orders are enumerated. Zero continuous scanning.
    public sealed class MapComponent_ThornDefenseJobs : MapComponent
    {
        private readonly HashSet<CompThornTurret> registered = new HashSet<CompThornTurret>();
        public MapComponent_ThornDefenseJobs(Map map):base(map){}
        public void Register(CompThornTurret comp){if(comp!=null)registered.Add(comp);}
        public void Unregister(CompThornTurret comp){registered.Remove(comp);}
        // Periodically prune only registered turrets. Avoid per-tick object scans.
        public override void MapComponentTick()
        {
            if(registered.Count == 0 || Find.TickManager.TicksGame % 2500 != 0)return;
            registered.RemoveWhere(c=>c?.parent?.Spawned!=true || c.parent.Map!=map);
        }
        public IEnumerable<Thing> Pending => registered.Where(c=>c.parent?.Spawned == true && c.IsPending).Select(c=>c.parent);
    }

    public sealed class Dialog_ThornRetrofit : Window
    {
        private readonly CompThornTurret turret;
        public override Vector2 InitialSize=>new Vector2(670f,570f);
        public Dialog_ThornRetrofit(CompThornTurret turret) {this.turret=turret;doCloseX=true;absorbInputAroundWindow=true;}
        public override void DoWindowContents(Rect inRect)
        {
            var listing=new Listing_Standard();listing.Begin(inRect);
            listing.Label("КОРПУС ТЕРНА  /  РЕКОНФИГУРАЦИЯ СТАЦИОНАРНОЙ СИСТЕМЫ");
            listing.GapLine();listing.Label(turret.parent.LabelCap);
            listing.Label("Все профили сначала резервируют материалы, затем требуют доставки и работы строителей. Во время работ турель не стреляет.");listing.Gap(12f);
            foreach(ThingDef choice in turret.UpgradeChoices().OrderBy(x=>x.defName))
            {
                if(choice == turret.parent.def)continue;
                if(listing.ButtonText(choice.LabelCap + "  |  " + (choice.building?.turretGunDef?.LabelCap??"CE")))
                {if(turret.Request(choice)) Close();
                  else Messages.Message("Для изменения размера освободите соседние клетки турели.", MessageTypeDefOf.RejectInput, false);}
            }
            if(turret.IsPending && listing.ButtonText("ОТМЕНИТЬ МОДИФИКАЦИЮ")){turret.Cancel();Close();}
            listing.End();
        }
    }
    public sealed class Dialog_ThornHolder : Window
    {
        private readonly CompThornTurret holder;
        public override Vector2 InitialSize => new Vector2(470f,240f);
        public Dialog_ThornHolder(CompThornTurret c){holder=c;doCloseX=true;}
        public override void DoWindowContents(Rect r)
        {
            var l=new Listing_Standard();l.Begin(r);l.Label("УНИВЕРСАЛЬНАЯ ОРУЖЕЙНАЯ СТАНИНА");l.Label(holder.MountedWeapon?.LabelCap??"Оружие не установлено");
            if(holder.MountedWeapon!=null && l.ButtonText("Снять оружие на землю")){holder.RemoveMounted();Close();}
            l.Label("Для установки выбери вооружённого бойца и нажми ПКМ на станине.");l.End();
        }
    }

    // Narrow runtime gate: only our turrets are affected, CE bullets and AI are not replaced.
    public static class ThornTurretCombatGate
    {
        public static void Install(Harmony h)
        {
            var type=AccessTools.TypeByName("CombatExtended.Building_TurretGunCE");
            if(type==null)return;
            // CE may expose a forced-target gizmo even on a hostile turret.
            // Only our hostile installations have those command gizmos suppressed.
            try
            {
                var gizmos=AccessTools.Method(type,"GetGizmos");
                if(gizmos!=null) h.Patch(gizmos,
                    postfix:new HarmonyMethod(typeof(ThornTurretCombatGate),nameof(FilterHostileGizmos)));
            }
            catch(Exception ex){Log.Warning("[ThornCorps] hostile gizmo safety gate unavailable: "+ex.Message);}
            foreach(string n in new[]{"TryStartShootSomething","BeginBurst"})
            {
                try {var method=AccessTools.Method(type,n);if(method!=null)h.Patch(method,prefix:new HarmonyMethod(typeof(ThornTurretCombatGate),nameof(Gate)));}
                catch(Exception ex){Log.Warning("[ThornCorps] CE turret gate not patched ("+n+"): "+ex.Message);}
            }
        }
        public static void FilterHostileGizmos(Thing __instance, ref IEnumerable<Gizmo> __result)
        {
            if(__instance?.def?.defName?.StartsWith("TC_Turret_",StringComparison.Ordinal)!=true)return;
            if(__instance.Faction != Faction.OfPlayer) __result = Enumerable.Empty<Gizmo>();
        }
        public static bool Gate(Thing __instance)
        {
            var comp=__instance?.TryGetComp<CompThornTurret>();
            return comp==null || (!comp.IsPending && (comp.Family!="Holder" || (comp.MountedWeapon!=null && comp.HolderAdapterReady)));
        }
    }

    public class WorkGiver_ThornRetrofit : WorkGiver_Scanner
    {
        public override ThingRequest PotentialWorkThingRequest => ThingRequest.ForUndefined();
        public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn) => pawn.Map?.GetComponent<MapComponent_ThornDefenseJobs>()?.Pending ?? Enumerable.Empty<Thing>();
        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false) => JobOnThing(pawn,t,forced)!=null;
        public override Job JobOnThing(Pawn pawn, Thing t,bool forced=false)
        {
            var comp=t.TryGetComp<CompThornTurret>();if(comp==null || !comp.IsPending || !pawn.CanReserve(t))return null;
            var shortage=comp.MaterialOutstanding();
            if(shortage != null)
            {
                foreach (Thing item in pawn.Map.listerThings.ThingsOfDef(shortage))
                {
                    if(item?.Spawned != true || item.stackCount<=0 || !pawn.CanReserve(item))continue;
                    JobDef job=DefDatabase<JobDef>.GetNamedSilentFail("TC_HaulRetrofitPart");if(job==null)return null;
                    var j=JobMaker.MakeJob(job,t,item);j.count=Math.Min(item.stackCount,comp.Needed(shortage));return j;
                }
                return null;
            }
            var work=DefDatabase<JobDef>.GetNamedSilentFail("TC_WorkRetrofit");return work==null?null:JobMaker.MakeJob(work,t);
        }
    }
    public class JobDriver_ThornDeliver : JobDriver
    {
        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.GetTarget(TargetIndex.A), job, errorOnFailed: errorOnFailed) &&
                   pawn.Reserve(job.GetTarget(TargetIndex.B), job, stackCount:job.count,errorOnFailed:errorOnFailed);
        }
        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            yield return Toils_Goto.GotoThing(TargetIndex.B,PathEndMode.ClosestTouch);
            yield return Toils_Haul.StartCarryThing(TargetIndex.B);
            yield return Toils_Goto.GotoThing(TargetIndex.A,PathEndMode.Touch);
            var deliver=new Toil { defaultCompleteMode=ToilCompleteMode.Instant };
            deliver.initAction=()=>
            {
                var comp=job.GetTarget(TargetIndex.A).Thing?.TryGetComp<CompThornTurret>();
                var held=pawn.carryTracker.CarriedThing;
                if(comp!=null && held!=null)comp.Deposit(held,job.count);
            };
            yield return deliver;
        }
    }
    public class JobDriver_ThornRetrofitWork : JobDriver
    {
        public override bool TryMakePreToilReservations(bool errorOnFailed) => pawn.Reserve(job.GetTarget(TargetIndex.A),job,errorOnFailed:errorOnFailed);
        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            yield return Toils_Goto.GotoThing(TargetIndex.A,PathEndMode.Touch);
            var toil=new Toil {defaultCompleteMode=ToilCompleteMode.Never};
            toil.tickAction=()=>
            {
                var comp=job.GetTarget(TargetIndex.A).Thing?.TryGetComp<CompThornTurret>();
                if(comp==null || !comp.IsReady) {ReadyForNextToil();return;}
                comp.Work(1);
                if(!comp.IsPending)ReadyForNextToil();
            };
            yield return toil;
        }
    }
    public class JobDriver_ThornMount : JobDriver
    {
        public override bool TryMakePreToilReservations(bool errorOnFailed) => pawn.Reserve(job.GetTarget(TargetIndex.A),job,errorOnFailed:errorOnFailed);
        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            yield return Toils_Goto.GotoThing(TargetIndex.A,PathEndMode.Touch);
            var finish=new Toil {defaultCompleteMode=ToilCompleteMode.Instant};
            finish.initAction=()=>job.GetTarget(TargetIndex.A).Thing?.TryGetComp<CompThornTurret>()?.MountFrom(pawn);
            yield return finish;
        }
    }
}
