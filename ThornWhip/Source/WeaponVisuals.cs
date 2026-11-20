using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace ThornWhip
{
    /// <summary>
    /// Immutable, full-canvas transparent layer textures. The designer draws 14 mechanical parts +
    /// 0-3 arbitrary optional attachments. No texture creation or per-tick recomposition.
    /// World overlay draws ONLY deviations from the 8 available default/fallback silhouettes.
    /// At most 14 deviations + 3 chosen specials and only on actual draw events, not game ticks.
    /// </summary>
    public static class WeaponVisuals
    {
        private const string Prefix = "ThornWhip/Parts/";
        private static readonly Dictionary<string, Texture2D> Images = new Dictionary<string, Texture2D>(512);
        private static readonly Dictionary<string, Material> Mats = new Dictionary<string, Material>(512);
        private static readonly int[] DrawOrder = { 7, 6, 2, 0, 1, 3, 4, 5, 8, 9, 10, 11, 12, 13, 14 };

        private static Texture2D Texture(string id)
        {
            if (!Images.TryGetValue(id, out var texture))
            {
                texture = ContentFinder<Texture2D>.Get(Prefix + id, false);
                Images[id] = texture;
            }
            return texture;
        }
        private static Material Material(string id)
        {
            if (!Mats.TryGetValue(id, out var mat))
            {
                mat = GraphicDatabase.Get<Graphic_Single>(Prefix + id, ShaderDatabase.Cutout,
                    new Vector2(1.58f, .50f), Color.white).MatSingle;
                Mats[id] = mat;
            }
            return mat;
        }
        private static string PartKey(int family, int index, int selected) =>
            WeaponCatalog.Family(family).Key + "/P" + index.ToString("00") + "_V" + selected;
        private static string SpecialKey(int family, int index) =>
            WeaponCatalog.Family(family).Key + "/S" + index.ToString("00");
        public static void DrawPreview(Rect target, WeaponBlueprint b)
        {
            if (b == null) return;
            Color previous = GUI.color;
            GUI.color = Color.white;
            var chassis = Texture(WeaponCatalog.Family(b.FamilyId).Key + "/Chassis");
            if (chassis != null) GUI.DrawTexture(target, chassis, ScaleMode.StretchToFill, true);
            foreach (int i in DrawOrder)
            {
                int option = b.SelectedPart(i);
                if (option < 0) continue; // missing assembly is genuinely missing
                var tex = Texture(PartKey(b.FamilyId, i, option));
                if (tex == null) continue;
                GUI.color = b.Material(i) == 1 ? new Color(.78f, .96f, 1f, 1f) : Color.white;
                GUI.DrawTexture(target, tex, ScaleMode.StretchToFill, true);
            }
            GUI.color = Color.white;
            for (int i = 0; i < 3; i++)
            {
                int special = b.Extra(i);
                if (special < 0) continue;
                var tex = Texture(SpecialKey(b.FamilyId, special));
                if (tex != null) GUI.DrawTexture(target, tex, ScaleMode.StretchToFill, true);
            }
            GUI.color = previous;
        }
        // Side-on assembly visualized in the design preview. Hitboxes can be used to select a part.
        // Coordinates are based on the authored 1024 x 320 full-canvas layers.
        private static readonly Rect[] RifleHotspots = {
            new Rect(388,105,255,77), new Rect(448,170,171,54),
            new Rect(645,137,250,38), new Rect(468,150,107,28),
            new Rect(725,126,42,50), new Rect(505,199,48,42),
            new Rect(344,143,108,36), new Rect(130,126,246,81),
            new Rect(633,116,205,70), new Rect(544,197,91,99),
            new Rect(516,78,101,51), new Rect(446,197,68,93),
            new Rect(390,119,72,31), new Rect(884,128,90,47), new Rect(610,183,120,26)
        };
        // The same 14 functional parts are in comparable positions on every weapon family,
        // but a pistol occupies the centre of the sheet rather than the rifle's full width.
        public static Rect[] HotspotsFor(WeaponBlueprint design)
        {
            if (design == null || design.FamilyId == 0) return RifleHotspots;
            Rect[] spots = new Rect[RifleHotspots.Length];
            if (design.FamilyId == 2) // pistol: trigger, grip and slide are closer together
            {
                float[] x = { 400, 438, 692, 490, 728, 545, 409, 416, 680, 470, 513, 454, 419, 795, 631 };
                float[] y = { 121, 171, 142, 141, 140, 185, 168, 195, 157, 213, 90, 210, 122, 132, 197 };
                for (int i=0;i<spots.Length;i++) spots[i] = new Rect(x[i], y[i], 63, 40);
                return spots;
            }
            return RifleHotspots;
        }
        // PostDraw is called for dropped ground items only. For equipped rifles,
        // the optional one-method Harmony postfix (below) handles render events.
        public static void DrawOnGround(Thing thing)
        {
            if (thing == null || !thing.Spawned || thing.def == null || !WeaponCatalog.IsOurWeapon(thing.def.defName)) return;
            DrawWorld(thing, thing.DrawPos + new Vector3(0f, .013f, 0f), 0f);
        }
        public static void DrawWorld(Thing thing, Vector3 drawLoc, float aimAngle)
        {
            var b = thing?.TryGetComp<CompWeaponDesign>()?.Blueprint;
            if (b == null) return;
            // Fallback image is based on CE's compact 0/1 mode/range/magazine Def trio.
            // Each other selected 0..4 module is drawn in its real per-instance variant;
            // only visible weapons trigger this render method, with no ticking or baking.
            int layer = 0;
            foreach (int i in DrawOrder)
            {
                int variant = b.SelectedPart(i);
                if (variant < 0) continue;
                int baked = i == 0 || i == 2 || i == 9 ? b.CoreIndex(i) : 0;
                if (variant == baked) continue;
                DrawLayer(PartKey(b.FamilyId, i, variant), drawLoc, aimAngle, layer++, b.FamilyId);
            }
            for (int i = 0; i < 3; i++)
            {
                int extra = b.Extra(i);
                if (extra >= 0) DrawLayer(SpecialKey(b.FamilyId, extra), drawLoc, aimAngle, layer++, b.FamilyId);
            }
        }
        private static void DrawLayer(string id, Vector3 pos, float angle, int depth, int family)
        {
            Material mat = Material(id);
            if (mat == null) return;
            // No patch on CE firing; these are standard draw calls on visible weapons only.
            var matrix = Matrix4x4.TRS(pos + new Vector3(0f, (depth + 1) * .0006f, 0f),
                Quaternion.AngleAxis(angle, Vector3.up), new Vector3(family == 2 ? .92f : 1.58f, 1f, family == 2 ? .46f : .50f));
            Graphics.DrawMesh(MeshPool.plane10, matrix, mat, 0);
        }
    }
}
