using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace ThornWhip
{
    // A family/chassis stays the same. The chamber/barrel, bolt and feeding system
    // determine whether a particular CE ammunition set is physically supported.
    // Projectiles, armor penetration, damage and ammo effects always come from CE.
    public sealed class CaliberProfile
    {
        public readonly string Label, AmmoSetName, ProjectileName;
        public readonly float MassOffset, RecoilFactor, MagazineFactor;
        public readonly int ExtraSteel, ExtraComponents;
        public readonly bool NeedsHeavyConversion;
        public CaliberProfile(string label, string ammo, string projectile, float mass, float recoil,
            float magazine, int steel, int components, bool heavy)
        {
            Label=label; AmmoSetName=ammo; ProjectileName=projectile;
            MassOffset=mass; RecoilFactor=recoil; MagazineFactor=magazine;
            ExtraSteel=steel; ExtraComponents=components; NeedsHeavyConversion=heavy;
        }
    }
    public static class WeaponCalibers
    {
        private static readonly CaliberProfile[][] Presets = {
            new[] {
                new CaliberProfile("5,56×45 NATO", "AmmoSet_556x45mmNATO", "Bullet_556x45mmNATO_FMJ",0f,1f,1f,0,0,false),
                new CaliberProfile("7,62×39 Soviet", "AmmoSet_762x39mmSoviet", "Bullet_762x39mmSoviet_FMJ",.16f,1.40f,.90f,6,1,false),
                new CaliberProfile("7,62×51 NATO", "AmmoSet_762x51mmNATO", "Bullet_762x51mmNATO_FMJ",.48f,1.70f,.73f,14,3,true)
            },
            new[] {
                new CaliberProfile("5,56×45 NATO", "AmmoSet_556x45mmNATO", "Bullet_556x45mmNATO_FMJ",0f,1f,1f,0,0,false),
                new CaliberProfile("5,45×39 Soviet", "AmmoSet_545x39mmSoviet", "Bullet_545x39mmSoviet_FMJ",-.12f,.90f,1f,4,1,false),
                new CaliberProfile("7,62×39 Soviet", "AmmoSet_762x39mmSoviet", "Bullet_762x39mmSoviet_FMJ",.31f,1.45f,.82f,9,2,true)
            },
            new[] {
                new CaliberProfile("9×19 Parabellum", "AmmoSet_9x19mmPara", "Bullet_9x19mmPara_FMJ",0f,1f,1f,0,0,false),
                new CaliberProfile(".45 ACP", "AmmoSet_45ACP", "Bullet_45ACP_FMJ",.15f,1.25f,.75f,5,1,true)
            },
            new[] { new CaliberProfile("40×46 LV CE", "AmmoSet_40x46mmGrenade", "Bullet_40x46mmGrenade_HE",0f,1f,1f,0,0,false) }
        };
        public static CaliberProfile[] Options(int family) => Presets[Math.Max(0,Math.Min(Presets.Length-1,family))];
        public static CaliberProfile For(WeaponBlueprint blueprint)
        {
            var variants=Options(blueprint?.FamilyId ?? 0);
            int id=blueprint?.CaliberId ?? 0;
            return variants[id>=0 && id<variants.Length?id:0];
        }
        public static int Capacity(WeaponBlueprint bp)
        {
            int baseSize=WeaponCatalog.Family(bp.FamilyId).Magazine[bp.CoreIndex(9)];
            return Math.Max(1,(int)Math.Round(baseSize*For(bp).MagazineFactor));
        }
        public static bool Compatible(WeaponBlueprint bp)
        {
            if (bp == null || bp.CaliberId < 0 || bp.CaliberId >= Options(bp.FamilyId).Length) return false;
            // Heavy pressure/size conversions require a reinforced upper, barrel, bolt and magazine.
            // Selection indices are stable across 0.7 saves and all four weapon families.
            if (!For(bp).NeedsHeavyConversion) return true;
            int[] stress={0,2,3,9};
            foreach (int slot in stress)
            {
                int index=bp.SelectedPart(slot);
                if (index!=1 && index!=3 && index!=4) return false;
            }
            return true;
        }
        public static string Problem(WeaponBlueprint bp) => Compatible(bp) ? "" :
            "Для этого калибра нужны усиленные коробка, ствол, затвор и магазин (варианты 2, 4 или 5).";
        public static int IdFromDefName(string name)
        {
            if (string.IsNullOrEmpty(name)) return 0;
            var fields=name.Split('_');
            foreach (string field in fields)
                if (field.Length == 2 && field[0]=='C' && char.IsDigit(field[1])) return field[1]-'0';
            return 0; // old 0.7 def names contain no caliber suffix
        }
    }
}
