#!/usr/bin/env python3
"""Generate data-only C# tables from JSON, preserving 0.5 option indices 0/1."""
from pathlib import Path
import json
R=Path(__file__).parent
D=R/'ThornWhip/Documentation'
DATA=json.loads((D/'weapon_families.json').read_text())
SPECIALS=json.loads((D/'special_modules.json').read_text())
C=R/'ThornWhip/Source/WeaponCatalog.cs'
keys=['sights','spread','sway','cooldown','mass','bulk','value','recoil','warmup','reload','range','nightVision']
costs=['steel','industrial','advanced','gold']

def q(s):return json.dumps(s,ensure_ascii=False).replace('\\/','/')
def fl(x):
 s=f'{float(x):.6f}'.rstrip('0').rstrip('.')
 return ('0' if not s else s)+'f'
def opt(o):
 e=o.get('effects',{});c=o.get('cost',{})
 args=[q(o['name'])]+[f'{k}: {fl(e[k])}' for k in keys if e.get(k,0)]+[f'{k}: {int(c[k])}' for k in costs if c.get(k,0)]
 return 'new ModuleOption('+', '.join(args)+')'
rows=[]
rows.append('''using System;

namespace ThornWhip
{
    // Source-generated catalog. Never reorder options 0/1; saved blueprints use integer indices.
    public sealed class ModuleOption
    {
        public readonly string Name;
        public readonly float Sights, Spread, Sway, Cooldown, Mass, Bulk, Value;
        public readonly float Recoil, Warmup, Reload, Range, NightVision;
        public readonly int Steel, Industrial, Advanced, Gold;
        public ModuleOption(string name, float sights=0, float spread=0, float sway=0,
            float cooldown=0, float mass=0, float bulk=0, float value=0,
            float recoil=0, float warmup=0, float reload=0, float range=0,
            float nightVision=0, int steel=0, int industrial=0, int advanced=0, int gold=0)
        {
            Name=name; Sights=sights; Spread=spread; Sway=sway; Cooldown=cooldown;
            Mass=mass; Bulk=bulk; Value=value; Recoil=recoil; Warmup=warmup;
            Reload=reload; Range=range; NightVision=nightVision;
            Steel=steel; Industrial=industrial; Advanced=advanced; Gold=gold;
        }
    }
    public sealed class ModuleSlot
    {
        public readonly string Label; public readonly bool Required;
        public readonly ModuleOption[] Options;
        public ModuleSlot(string label, bool required, params ModuleOption[] options) { Label=label; Required=required; Options=options; }
    }
    public sealed class SpecialModule
    {
        public readonly string Target, Name, Details;
        public readonly ModuleOption Effects;
        public SpecialModule(string target, string name, string details, ModuleOption effects)
        { Target=target; Name=name; Details=details; Effects=effects; }
    }
    public sealed class WeaponFamily
    {
        public readonly string Key, Label, Caliber;
        public readonly float Sights, Spread, Sway, Cooldown, Mass, Bulk, MarketValue;
        public readonly int[] Magazine, Burst, Ranges;
        public WeaponFamily(string key, string label, string caliber, float sights, float spread, float sway,
            float cooldown, float mass, float bulk, float marketValue, int mag0, int mag1,
            int burst0, int burst1, int range0, int range1)
        { Key=key; Label=label; Caliber=caliber; Sights=sights; Spread=spread; Sway=sway;
          Cooldown=cooldown; Mass=mass; Bulk=bulk; MarketValue=marketValue; Magazine=new[]{mag0,mag1};
          Burst=new[]{burst0,burst1}; Ranges=new[]{range0,range1}; }
    }
    public static class WeaponCatalog
    {
        public static readonly WeaponFamily[] Families = {
''')
for e in DATA:
 f=e['family'];rows.append('            new WeaponFamily('+', '.join([q(f['key']),q(f['label']),q(f['caliber'])]+[fl(f[k]) for k in ['sights','spread','sway','cooldown','mass','bulk','value']]+[str(i) for k in ['magazine','burst','range'] for i in f[k]])+'),\n')
rows.append('        };\n        private static readonly ModuleSlot[][] Slots = {\n')
for e in DATA:
 rows.append('            new ModuleSlot[] {\n')
 for s in e['slots']:
  rows.append('                new ModuleSlot('+q(s['label'])+','+('true' if s.get('required',True) else 'false')+',\n')
  for j,o in enumerate(s['options']):rows.append('                    '+opt(o)+(',' if j<len(s['options'])-1 else '')+'\n')
  rows.append('                ),\n')
 rows.append('            },\n')
rows.append('''        };
        public static WeaponFamily Family(int id) => Families[id>=0 && id<Families.Length ? id : 0];
        public static ModuleSlot[] RequiredFor(int id) => Slots[id>=0 && id<Slots.Length ? id : 0];
        public static ModuleSlot[] RequiredFor(WeaponBlueprint b) => RequiredFor(b?.FamilyId ?? 0);
        public static bool IsOurWeapon(string name) => name!=null &&
           (name.StartsWith("TT_Rifle_R", StringComparison.Ordinal) || name.StartsWith("TT_Auto_R", StringComparison.Ordinal) ||
            name.StartsWith("TT_Pistol_R", StringComparison.Ordinal) || name.StartsWith("TT_Launcher_R", StringComparison.Ordinal));
        public static int FamilyFromDef(string name)
        {
            if (name!=null) for(int i=0;i<Families.Length;i++)
                if(name.StartsWith("TT_"+Families[i].Key+"_R", StringComparison.Ordinal))return i;
            return 0;
        }
        // Three identical optional slots; different modules may affect the same assembly.
        public static readonly SpecialModule[] Specials = {
''')
for s in SPECIALS:
 o=dict(name=s['name'],effects=s['effects'],cost=s['cost']);o['effects']['value']=s['cost'].get('value',0)
 rows.append('            new SpecialModule('+', '.join([q(s['target']),q(s['name']),q(s['description']),opt(o)])+'),\n')
rows.append('''        };
        public static string WeaponDefName(WeaponBlueprint b) =>
            $"TT_{Family(b.FamilyId).Key}_R{b.CoreIndex(0)}_B{b.CoreIndex(2)}_M{b.CoreIndex(9)}";
        // One production RecipeDef per underlying CE structural variant (32 total); material
        // requirements are exact per blueprint and escrowed when the user queues the bill.
        public static string RecipeName(WeaponBlueprint b)
        {
            string prefix=b.FamilyId==0 ? "TT_Craft" : "TT_Craft_"+Family(b.FamilyId).Key;
            return $"{prefix}_R{b.CoreIndex(0)}_B{b.CoreIndex(2)}_M{b.CoreIndex(9)}";
        }
    }
}
''')
C.write_text(''.join(rows),encoding='utf-8')
print(C,'lines=',len(C.read_text().splitlines()))
