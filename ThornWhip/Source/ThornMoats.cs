using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace ThornWhip
{
    public sealed class CompProperties_ThornTrench : CompProperties
    { public CompProperties_ThornTrench() {compClass=typeof(CompThornTrench);} }

    public sealed class CompThornTrench : ThingComp
    {
        private bool flooded;
        private string terrainBefore;
        public int Depth
        {
            get
            {
                var name=parent?.def?.defName??"";
                return name.EndsWith("_3_Core")?3:name.EndsWith("_2_Core")?2:1;
            }
        }
        public bool Flooded => flooded;
        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if(!respawningAfterLoad && string.IsNullOrEmpty(terrainBefore))terrainBefore=parent.Position.GetTerrain(parent.Map)?.defName;
            parent.Map?.GetComponent<MapComponent_ThornMoats>()?.Register(this);
        }
        public override void PostDestroy(DestroyMode mode, Map previousMap)
        {
            previousMap?.GetComponent<MapComponent_ThornMoats>()?.Unregister(this);
            if(previousMap!=null && parent.Position.InBounds(previousMap) && flooded)
                Restore(previousMap);
            base.PostDestroy(mode, previousMap);
        }
        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref flooded,"TC_moatFlooded");
            Scribe_Values.Look(ref terrainBefore,"TC_originalTerrain");
        }
        public void SetFlooded(bool value)
        {
            if(value==flooded || !parent.Spawned)return;
            var map=parent.Map;
            if(map==null)return;
            flooded=value;
            if(value)
            {
                var water=DefDatabase<TerrainDef>.GetNamedSilentFail(Depth>=3?"WaterDeep":"WaterShallow");
                if(water!=null) map.terrainGrid.SetTerrain(parent.Position,water);
            }
            else Restore(map);
        }
        private void Restore(Map map)
        {
            if(string.IsNullOrEmpty(terrainBefore))return;
            var terrain=DefDatabase<TerrainDef>.GetNamedSilentFail(terrainBefore);
            if(terrain!=null && parent.Position.InBounds(map))map.terrainGrid.SetTerrain(parent.Position,terrain);
            flooded=false;
        }
        public override string CompInspectStringExtra() => flooded ?
            (Depth==3?"Затоплен: непроходимая глубокая вода":"Затоплен: мелководный ров, глубина "+Depth):
            "Сухой ров, глубина "+Depth+". Соединить с водой для затопления.";
    }

    // Connections are recomputed only when trenches are placed/removed or once per 2500 ticks
    // while trenches exist (to notice new rivers, terrain changes, or filled/depleted lakes).
    // Complexity: O(trench cells + adjacent water checks), not O(map area) each tick.
    public sealed class MapComponent_ThornMoats : MapComponent
    {
        private readonly Dictionary<IntVec3,CompThornTrench> network = new Dictionary<IntVec3,CompThornTrench>();
        private bool dirty;
        private int nextCheck;
        private static readonly IntVec3[] Steps = {new IntVec3(0,0,1),new IntVec3(0,0,-1),new IntVec3(1,0,0),new IntVec3(-1,0,0)};
        public MapComponent_ThornMoats(Map map):base(map){}
        public void Register(CompThornTrench comp)
        {if(comp?.parent!=null){network[comp.parent.Position]=comp;dirty=true;}}
        public void Unregister(CompThornTrench comp)
        {
            if(comp==null)return;
            foreach(var cell in network.Where(entry=>ReferenceEquals(entry.Value,comp))
                .Select(entry=>entry.Key).ToList())
                network.Remove(cell);
            dirty=true;
        }
        public override void MapComponentTick()
        {
            if(network.Count==0)return;
            int now=Find.TickManager.TicksGame;
            if(!dirty && now<nextCheck)return;
            nextCheck=now+2500;dirty=false;Recalculate();
        }
        private static bool IsWater(TerrainDef t)
        {
            string name=t?.defName??"";
            return name.IndexOf("water",StringComparison.OrdinalIgnoreCase)>=0 ||
                name.IndexOf("river",StringComparison.OrdinalIgnoreCase)>=0 ||
                name.IndexOf("ocean",StringComparison.OrdinalIgnoreCase)>=0 ||
                name.IndexOf("sea",StringComparison.OrdinalIgnoreCase)>=0;
        }
        private bool HasExternalWater(IntVec3 cell)
        {
            foreach(var d in Steps)
            {
                var next=cell+d;
                if(!next.InBounds(map) || network.ContainsKey(next))continue;
                if(IsWater(next.GetTerrain(map)))return true;
            }
            return false;
        }
        private void Recalculate()
        {
            // Keep registry correct even after despawn without destruction.
            // Prune the registered trench set, never scan all map cells.
            foreach(var cell in network.Where(entry=>entry.Value?.parent?.Spawned!=true
                || entry.Value.parent.Map!=map || entry.Value.parent.Position!=entry.Key)
                .Select(entry=>entry.Key).ToList())
                network.Remove(cell);
            if(network.Count==0)return;
            var visited=new HashSet<IntVec3>();
            var queue=new Queue<IntVec3>();
            foreach(var root in network.Keys.ToList())
            {
                if(visited.Contains(root))continue;
                var group=new List<CompThornTrench>();
                bool source=false;visited.Add(root);queue.Enqueue(root);
                while(queue.Count>0)
                {
                    var c=queue.Dequeue();
                    if(!network.TryGetValue(c,out var comp) || comp?.parent?.Spawned!=true)continue;
                    group.Add(comp);
                    if(HasExternalWater(c))source=true;
                    foreach(var step in Steps)
                    {
                        var n=c+step;
                        if(!visited.Contains(n) && network.ContainsKey(n)){visited.Add(n);queue.Enqueue(n);}
                    }
                }
                // Flooding respects network connectivity and does not create a permanent
                // 'water source' by looking at its own converted trench cells.
                foreach(var trench in group)trench.SetFlooded(source);
            }
        }
    }
}
