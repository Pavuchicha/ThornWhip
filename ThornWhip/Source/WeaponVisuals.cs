using System;
using System.Collections.Generic;
using System.Reflection;
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
        private static string PartKey(int family, int index, int selected, bool order = false) =>
            WeaponCatalog.Family(family).Key + "/P" + index.ToString("00") + "_V" + selected + (order ? "_Order" : "");
        private static string SpecialKey(int family, int index, bool order = false) =>
            WeaponCatalog.Family(family).Key + "/S" + index.ToString("00") + (order ? "_Order" : "");
        // Access the 1.7 style via reflection to remain compatible with style helper
        // changes across versions of RimWorld. Reflection is only used at draw time.
        private static readonly PropertyInfo StyleProperty = typeof(Thing).GetProperty("StyleDef", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
        private static bool IsOrderStyle(Thing thing)
        {
            if (thing == null) return false;
            try
            {
                var style = StyleProperty?.GetValue(thing) as Def;
                return style?.defName?.StartsWith("TC_Order_", StringComparison.Ordinal) == true;
            }
            catch (Exception) { return false; }
        }
        public static Rect ImageRect(Rect target)
        {
            float aspect = 1024f / 320f;
            float width = Mathf.Min(target.width, target.height * aspect);
            float height = width / aspect;
            return new Rect(target.x + (target.width - width) / 2f,
                target.y + (target.height - height) / 2f, width, height);
        }
        public static void DrawPreview(Rect target, WeaponBlueprint b, bool orderStyle = false)
        {
            if (b == null) return;
            target = ImageRect(target); // never stretch rifle/handgun PNGs into a different aspect ratio
            Color previous = GUI.color;
            GUI.color = Color.white;
            var chassis = Texture(WeaponCatalog.Family(b.FamilyId).Key + (orderStyle ? "/Chassis_Order" : "/Chassis"));
            if (chassis != null) GUI.DrawTexture(target, chassis, ScaleMode.ScaleToFit, true);
            foreach (int i in DrawOrder)
            {
                int option = b.SelectedPart(i);
                if (option < 0) continue; // missing assembly is genuinely missing
                var tex = Texture(PartKey(b.FamilyId, i, option, orderStyle));
                if (tex == null) continue;
                GUI.color = b.Material(i) == 1 ? new Color(.90f, .92f, .95f, 1f) : Color.white;
                Rect layerRect = target;
                // The muzzle follows the configured barrel length instead of hovering
                // at the original rifle's full-length position.
                if (i == 13)
                {
                    float[] lengths = { .75f, 1.08f, .56f, 1.18f, 1.12f };
                    int barrel = b.SelectedPart(2);
                    if (barrel >= 0 && barrel < lengths.Length)
                        layerRect.x += (lengths[barrel] - 1f) * 133f / 1024f * target.width;
                }
                GUI.DrawTexture(layerRect, tex, ScaleMode.ScaleToFit, true);
            }
            GUI.color = Color.white;
            for (int i = 0; i < 3; i++)
            {
                int special = b.Extra(i);
                if (special < 0) continue;
                var tex = Texture(SpecialKey(b.FamilyId, special, orderStyle));
                if (tex != null) GUI.DrawTexture(target, tex, ScaleMode.ScaleToFit, true);
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
            // Render the full chosen construction, not just differences over a prebaked rifle.
            // This is invoked by render events, never every simulation tick.
            int layer = 0;
            bool orderStyle = IsOrderStyle(thing);
            foreach (int i in DrawOrder)
            {
                int variant = b.SelectedPart(i);
                if (variant < 0) continue;
                DrawLayer(PartKey(b.FamilyId, i, variant, orderStyle), drawLoc, aimAngle, layer++, b.FamilyId);
            }
            for (int i = 0; i < 3; i++)
            {
                int extra = b.Extra(i);
                if (extra >= 0) DrawLayer(SpecialKey(b.FamilyId, extra, orderStyle), drawLoc, aimAngle, layer++, b.FamilyId);
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
