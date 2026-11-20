using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace ThornWhip
{
    public static class DesignerUI
    {
        public static readonly Color Back = new Color(.065f, .103f, .128f, 1f);
        public static readonly Color Pane = new Color(.100f, .162f, .190f, 1f);
        public static readonly Color Card = new Color(.135f, .220f, .251f, 1f);
        public static readonly Color Border = new Color(.215f, .367f, .390f, 1f);
        public static readonly Color Accent = new Color(.292f, .883f, .790f, 1f);
        public static readonly Color Brass = new Color(.910f, .715f, .432f, 1f);
        public static readonly Color Muted = new Color(.590f, .688f, .697f, 1f);
        public static readonly Color White = new Color(.908f, .948f, .928f, 1f);
        public static void Panel(Rect r, Color color) { Widgets.DrawBoxSolid(r, color); Widgets.DrawBox(r, 1); }
        public static void Txt(Rect r, string content, Color color, GameFont size = GameFont.Small, bool centered = false)
        {
            Color old = GUI.color; var prev = Text.Font; var align = Text.Anchor;
            GUI.color = color; Text.Font = size;
            if (centered) Text.Anchor = TextAnchor.MiddleCenter;
            Widgets.Label(r, content);
            Text.Font = prev; Text.Anchor = align; GUI.color = old;
        }
        public static bool Action(Rect r, string title, bool active = false)
        {
            Widgets.DrawBoxSolid(r, active ? new Color(.16f, .39f, .39f) : Card);
            if (Mouse.IsOver(r)) Widgets.DrawHighlight(r);
            Txt(r.ContractedBy(2f), title, active ? Accent : White, GameFont.Small, true);
            return Widgets.ButtonInvisible(r);
        }
        public static string Stats(WeaponBlueprint b, float quality)
        {
            WeaponTuning t = WeaponTuning.Evaluate(b);
            var family = WeaponCatalog.Family(b.FamilyId);
            float sights = Math.Max(.1f, family.Sights + WeaponTuning.Adjust(t.Sights, quality, false));
            float spread = Math.Max(.005f, family.Spread + WeaponTuning.Adjust(t.Spread, quality, true));
            float sway = Math.Max(.25f, family.Sway + WeaponTuning.Adjust(t.Sway, quality, true));
            float recoil = Math.Max(.35f, WeaponCalibers.For(b).RecoilFactor * (1f + WeaponTuning.Adjust(t.Recoil, quality, true)));
            float reload = Math.Max(.55f, 1f + WeaponTuning.Adjust(t.Reload, quality, true));
            float warmup = Math.Max(.55f, 1f + WeaponTuning.Adjust(t.Warmup, quality, true));
            float cooldown = Math.Max(.22f, family.Cooldown * (1f + WeaponTuning.Adjust(t.Cooldown, quality, true)));
            float effectiveRange = Math.Max(1f, family.Ranges[b.CoreIndex(2)] *
                Math.Max(.75f, 1f + WeaponTuning.Adjust(t.Range, quality, false)));
            float mass = Math.Max(.50f, family.Mass + t.Mass);
            float bulk = Math.Max(.60f, family.Bulk + t.Bulk);
            return $"CE ПРИЦЕЛ: {sights:F2}  |  УГЛОВОЙ РАЗБРОС: {spread:F3}\n" +
                $"КОЛЕБАНИЕ: {sway:F2}  |  ОТДАЧА: ×{recoil:F2}\n" +
                $"ПЕРЕЗАРЯДКА: ×{reload:F2}  |  ПРИЦЕЛИВАНИЕ: ×{warmup:F2}\n" +
                $"ПАУЗА: {cooldown:F2} с  |  МАССА: {mass:F2} кг\n" +
                $"ГАБАРИТ: {bulk:F2}  |  МАГАЗИН: {WeaponCalibers.Capacity(b)}\n" +
                $"ДАЛЬНОСТЬ: {effectiveRange:F0}  |  ОЧЕРЕДЬ: {family.Burst[b.CoreIndex(0)]}\n" +
                "КАЛИБР: " + WeaponCalibers.For(b).Label + "  |  урон/пробитие — от боеприпаса CE";
        }
        public static string Materials(WeaponBlueprint b) => WeaponCosts.Display(b);
        public static string Effects(ModuleOption o)
        {
            if (o == null) return "";
            var list = new List<string>();
            if (o.Sights != 0) list.Add($"CE эффективность прицела: {o.Sights:+0.000;-0.000} (+ лучше)");
            if (o.Spread != 0) list.Add($"Угловой разброс: {o.Spread:+0.000;-0.000} (− точнее)");
            if (o.Sway != 0) list.Add($"Колебание при наведении: {o.Sway:+0.000;-0.000} (− лучше)");
            if (o.Recoil != 0) list.Add($"Отдача: {o.Recoil*100:+0.0;-0.0}% (− лучше)");
            if (o.Warmup != 0) list.Add($"Прицеливание: {o.Warmup*100:+0.0;-0.0}% времени (− быстрее)");
            if (o.Reload != 0) list.Add($"Перезарядка: {o.Reload*100:+0.0;-0.0}% времени (− быстрее)");
            if (o.Cooldown != 0) list.Add($"Перерыв: {o.Cooldown*100:+0.0;-0.0}% базовой паузы (− быстрее)");
            if (o.Mass != 0) list.Add($"Масса: {o.Mass:+0.00;-0.00}");
            if (o.Bulk != 0) list.Add($"Габарит: {o.Bulk:+0.00;-0.00}");
            if (o.NightVision != 0) list.Add($"Ночное зрение: {o.NightVision:+0.000;-0.000}");
            if (o.Range != 0) list.Add($"Дальность: {o.Range:+0.000;-0.000}");
            if (o.Value != 0) list.Add($"Стоимость: {o.Value:+0.0;-0.0}");
            return string.Join("\n", list);
        }
    }
    public sealed class Dialog_WeaponDesign : Window
    {
        private readonly Building_WorkTable bench;
        private readonly WeaponBlueprint design;
        private int selectedPart = 0;
        private bool previewOrderStyle;
        private int qualityIndex = 2;
        private int showKind = 0; // 0=part, 1=extra
        private int selectedSpecialSlot = 0;
        private Vector2 rightInfoScroll;
        private string titleBuffer;
        private readonly float[] qualities = { .76f, .88f, 1f, 1.07f, 1.13f, 1.20f, 1.27f };
        private readonly string[] qualityLabels = { "Отвратительное", "Плохое", "Обычное", "Хорошее", "Отличное", "Шедевр", "Легендарное" };
        public override Vector2 InitialSize => new Vector2(Mathf.Min(1420, UI.screenWidth - 42), Mathf.Min(930, UI.screenHeight - 42));
        public Dialog_WeaponDesign(Building_WorkTable workBench, WeaponBlueprint existing = null)
        {
            bench = workBench; design = existing?.Copy() ?? new WeaponBlueprint();
            titleBuffer = design.Title;
            doCloseX = true; absorbInputAroundWindow = true; closeOnClickedOutside = false;
        }
        public override void DoWindowContents(Rect r)
        {
            Widgets.DrawBoxSolid(r, DesignerUI.Back);
            float rightWidth = Mathf.Min(362f, r.width * .28f);
            float leftWidth = r.width - rightWidth - 28f;
            float rightX = leftWidth + 18f;
            // Header / live project identity.
            DesignerUI.Txt(new Rect(20, 11, 465, 35), "КОРПУС ТЕРНА  /  ОРУЖЕЙНАЯ МАСТЕРСКАЯ", DesignerUI.White, GameFont.Medium);
            DesignerUI.Txt(new Rect(21, 49, 142, 24), "ИМЯ ЧЕРТЕЖА", DesignerUI.Muted);
            titleBuffer = Widgets.TextField(new Rect(157, 46, Mathf.Min(460f, leftWidth - 170), 27f), titleBuffer);
            design.Title = titleBuffer;
            if (DesignerUI.Action(new Rect(rightX, 20, rightWidth - 14, 44), "КАЧЕСТВО ПРЕВЬЮ  ◇  " + qualityLabels[qualityIndex]))
                qualityIndex = (qualityIndex + 1) % qualities.Length;
            // Four weapon families. One shared researched blueprint data model.
            float tabWidth = (leftWidth - 18f) / 4f;
            for (int f = 0; f < WeaponCatalog.Families.Length; f++)
            {
                int target = f;
                var fam = WeaponCatalog.Families[f];
                if (DesignerUI.Action(new Rect(13f + f * tabWidth, 80f, tabWidth - 4f, 32f), fam.Label, design.FamilyId == f))
                {
                    if (design.FamilyId != target)
                    {
                        design.FamilyId = target;
                        design.CaliberId = 0;
                        // A different platform requires consciously selecting its assembly components.
                        for (int i = 0; i < WeaponCatalog.RequiredFor(design).Length; i++) { design.Parts[i] = -1; design.Materials[i] = 0; }
                        for (int i = 0; i < 3; i++) design.Special[i] = -1;
                        selectedPart = 0;
                        design.Title = fam.Label;
                        titleBuffer = design.Title;
                    }
                }
            }
            // A conversion stays on the SAME base; individual weapon instances are backed by a CE ammoSet.
            var calibers=WeaponCalibers.Options(design.FamilyId);
            DesignerUI.Txt(new Rect(17, 115, 125, 30), "ПАТРОН CE", DesignerUI.Brass);
            if (DesignerUI.Action(new Rect(142, 114, Mathf.Min(265, leftWidth-153), 32),
                WeaponCalibers.For(design).Label+"  ▾"))
            {
                var choices=new List<FloatMenuOption>();
                for(int ci=0;ci<calibers.Length;ci++)
                {
                    int chosen=ci;
                    choices.Add(new FloatMenuOption(calibers[ci].Label,()=>design.CaliberId=chosen));
                }
                Find.WindowStack.Add(new FloatMenu(choices));
            }
            // Technical preview / layers.
            Rect viewport = new Rect(13, 151, leftWidth, 202);
            DesignerUI.Panel(viewport, DesignerUI.Pane);
            DesignerUI.Txt(new Rect(viewport.x + 16, viewport.y + 11, viewport.width - 191, 22),
                "КОНСТРУКТОР  /  НАЖМИ НА ДЕТАЛЬ", DesignerUI.Accent);
            if (DesignerUI.Action(new Rect(viewport.xMax - 160f, viewport.y + 5f, 148f, 26f),
                previewOrderStyle ? "СТИЛЬ: ОРДЕН" : "СТИЛЬ: КОРПУС")) previewOrderStyle = !previewOrderStyle;
            Rect weaponRect = WeaponVisuals.ImageRect(new Rect(viewport.x + 11, viewport.y + 36, viewport.width - 22, 153));
            WeaponVisuals.DrawPreview(weaponRect, design, previewOrderStyle);
            var hotspots = WeaponVisuals.HotspotsFor(design);
            for (int i = 0; i < hotspots.Length; i++)
            {
                Rect rel = hotspots[i];
                Rect hot = new Rect(weaponRect.x + rel.x / 1024f * weaponRect.width,
                    weaponRect.y + rel.y / 320f * weaponRect.height,
                    rel.width / 1024f * weaponRect.width,
                    rel.height / 320f * weaponRect.height);
                if (Widgets.ButtonInvisible(hot)) { selectedPart = i; showKind = 0; }
                if (Mouse.IsOver(hot) || (showKind == 0 && selectedPart == i))
                    Widgets.DrawBox(hot, 1);
            }
            // Main 2-column assembly list.
            float top = 365;
            float remaining = r.height - top - 195;
            int rowCount = (WeaponCatalog.RequiredFor(design).Length + 1) / 2;
            float rowHeight = Mathf.Min(50, remaining / rowCount);
            DesignerUI.Txt(new Rect(21, top, 450, 23), "15 УЗЛОВ (ПОМЕЧЕННЫЕ * ОБЯЗАТЕЛЬНЫ)  /  " + WeaponCalibers.For(design).Label, DesignerUI.White, GameFont.Medium);
            top += 26;
            for (int i = 0; i < WeaponCatalog.RequiredFor(design).Length; i++)
            {
                int col = i / rowCount, row = i % rowCount;
                float half = (leftWidth - 14) / 2f;
                float x = 14 + col * (half + 8f), y = top + row * rowHeight;
                DrawRequiredRow(i, new Rect(x, y, half, rowHeight - 3));
            }
            float modsY = top + rowCount * rowHeight + 9;
            DesignerUI.Txt(new Rect(22, modsY, leftWidth - 8, 23),
                "3 УНИВЕРСАЛЬНЫХ СЛОТА  ·  ЛЮБЫЕ СОВМЕСТИМЫЕ УЛУЧШЕНИЯ", DesignerUI.White, GameFont.Medium);
            float buttonY = modsY + 28;
            for (int i = 0; i < 3; i++)
            {
                int sp = design.Extra(i);
                string name = sp >= 0 ? WeaponCatalog.Specials[sp].Name : "+  добавить модификацию";
                float x = 17 + i * (leftWidth - 10) / 3f;
                if (DesignerUI.Action(new Rect(x, buttonY, (leftWidth - 24) / 3f, 43), $"0{i+1}  {name}", showKind == 1 && selectedSpecialSlot == i))
                { showKind = 1; selectedSpecialSlot = i; ShowSpecialMenu(i); }
            }
            // Right-side information / selections.
            DesignerUI.Panel(new Rect(rightX, 82, rightWidth - 8, r.height - 165), DesignerUI.Pane);
            DrawRightInfo(new Rect(rightX + 13, 95, rightWidth - 34, r.height - 192));
            // Footer / quick actions.
            Rect foot = new Rect(13, r.height - 77, r.width - 26, 69);
            DesignerUI.Panel(foot, DesignerUI.Pane);
            if (DesignerUI.Action(new Rect(24, foot.y + 12, 131, 45), "БАЗОВАЯ СБОРКА"))
                for (int i = 0; i < WeaponCatalog.RequiredFor(design).Length; i++) design.Parts[i] = WeaponCatalog.RequiredFor(design)[i].Required ? 0 : -1;
            if (DesignerUI.Action(new Rect(161, foot.y + 12, 96, 45), "ОЧИСТИТЬ"))
            {
                for (int i = 0; i < WeaponCatalog.RequiredFor(design).Length; i++) { design.Parts[i] = -1; design.Materials[i] = 0; }
                for (int i = 0; i < 3; i++) design.Special[i] = -1;
            }
            DesignerUI.Txt(new Rect(268, foot.y + 9, r.width - 621, 24),
                "МАТЕРИАЛЫ: " + DesignerUI.Materials(design), DesignerUI.Muted);
            DesignerUI.Txt(new Rect(268, foot.y + 34, r.width - 621, 24),
                design.MissingCount > 0 ? "Не хватает обязательных узлов: " + design.MissingCount :
                design.IsValid ? "ПРОЕКТ ГОТОВ К РАЗРАБОТКЕ" : design.ValidationProblem,
                design.IsValid ? DesignerUI.Accent : DesignerUI.Brass);
            if (DesignerUI.Action(new Rect(r.width - 335, foot.y + 11, 308, 47), "НАЧАТЬ РАЗРАБОТКУ  ›", design.IsValid))
                EnqueueResearch();
        }
        private void DrawRequiredRow(int id, Rect r)
        {
            bool selected = showKind == 0 && selectedPart == id;
            Widgets.DrawBoxSolid(r, selected ? new Color(.15f, .35f, .35f, 1f) : DesignerUI.Card);
            string label = WeaponCatalog.RequiredFor(design)[id].Label + (WeaponCatalog.RequiredFor(design)[id].Required ? " *" : "");
            int selectedId = design.SelectedPart(id);
            if (DesignerUI.Action(new Rect(r.x + 3, r.y + 3, r.width * .385f, r.height - 6),
                (id + 1).ToString("00") + "  " + label, selected))
            { selectedPart = id; showKind = 0; }
            var opts = WeaponCatalog.RequiredFor(design)[id].Options;
            string selectedName = selectedId >= 0 ? (selectedId + 1) + "/" + opts.Length + "  " + opts[selectedId].Name : "УСТАНОВИТЬ  ▾";
            if (DesignerUI.Action(new Rect(r.x + r.width * .40f, r.y + 3, r.width * .36f, r.height - 6), selectedName, selectedId >= 0))
            { selectedPart = id; showKind = 0; ShowPartMenu(id); }
            if (DesignerUI.Action(new Rect(r.x + r.width * .775f, r.y + 3, r.width * .22f, r.height - 6),
                design.Material(id) == 1 ? "ПЛАСТАЛЬ" : "СТАЛЬ"))
            { design.Materials[id] = 1 - design.Material(id); selectedPart = id; showKind = 0; }
        }
        private void ShowPartMenu(int index)
        {
            var options = new List<FloatMenuOption>();
            if (!WeaponCatalog.RequiredFor(design)[index].Required) options.Add(new FloatMenuOption("[не установлен]", () => design.Parts[index] = -1));
            var slot = WeaponCatalog.RequiredFor(design)[index];
            for (int i = 0; i < slot.Options.Length; i++)
            {
                int chosen = i;
                var part = slot.Options[i];
                options.Add(new FloatMenuOption((i + 1) + ". " + part.Name + "  [" + WeaponCosts.Display(part) + "]",
                    () => { design.Parts[index] = chosen; selectedPart = index; showKind = 0; }));
            }
            Find.WindowStack.Add(new FloatMenu(options));
        }
        private void DrawRightInfo(Rect r)
        {
            Rect body = new Rect(r.x, r.y, r.width, r.height);
            Rect canvas = new Rect(0, 0, r.width - 18f, 1650f);
            Widgets.BeginScrollView(body, ref rightInfoScroll, canvas);
            r = canvas;
            DesignerUI.Txt(new Rect(r.x, r.y, r.width, 28), "ДАННЫЕ COMBAT EXTENDED", DesignerUI.Accent, GameFont.Medium);
            float infoY = r.y + 36;
            string[] lines = DesignerUI.Stats(design, qualities[qualityIndex]).Split('\n');
            foreach (string line in lines)
            { DesignerUI.Txt(new Rect(r.x + 2, infoY, r.width - 6, 32), line, DesignerUI.White); infoY += 40; }
            infoY += 8;
            DesignerUI.Txt(new Rect(r.x + 2, infoY, r.width - 6, 76),
                "×1.00 = без изменения; ×0.90 = на 10% быстрее. Пауза указана в СЕКУНДАХ. Меньшие разброс, отдача и колебание — лучше. Результат зависит от патрона CE и стрелка.",
                DesignerUI.Muted);
            infoY += 84;
            Widgets.DrawLineHorizontal(r.x, infoY, r.width);
            infoY += 14;
            if (showKind == 0)
            {
                ModuleSlot slot = WeaponCatalog.RequiredFor(design)[selectedPart];
                DesignerUI.Txt(new Rect(r.x, infoY, r.width, 26), "УЗЕЛ  " + (selectedPart + 1).ToString("00"), DesignerUI.Accent);
                infoY += 26;
                DesignerUI.Txt(new Rect(r.x, infoY, r.width, 36), slot.Label.ToUpperInvariant(), DesignerUI.White, GameFont.Medium);
                infoY += 42;
                for (int v = 0; v < slot.Options.Length; v++)
                {
                    DesignerUI.Txt(new Rect(r.x + 3, infoY, r.width - 6, 27),
                        (v + 1) + " / " + slot.Options.Length + " · " + slot.Options[v].Name,
                        design.SelectedPart(selectedPart) == v ? DesignerUI.Accent : DesignerUI.White);
                    infoY += 25;
                    DesignerUI.Txt(new Rect(r.x + 8, infoY, r.width - 15, 105),
                        WeaponCosts.Display(slot.Options[v]) + "\n" + DesignerUI.Effects(slot.Options[v]), DesignerUI.Muted);
                    infoY += 110;
                }
            }
            else
            {
                int id = design.Extra(selectedSpecialSlot);
                DesignerUI.Txt(new Rect(r.x, infoY, r.width, 27),
                    "ДОПОЛНИТЕЛЬНЫЙ СЛОТ 0" + (selectedSpecialSlot + 1), DesignerUI.Accent);
                infoY += 31;
                if (id < 0) DesignerUI.Txt(new Rect(r.x, infoY, r.width, 72),
                    "Пустой. Здесь можно установить улучшение любого узла.", DesignerUI.Muted);
                else
                {
                    var sp = WeaponCatalog.Specials[id];
                    DesignerUI.Txt(new Rect(r.x, infoY, r.width, 28), sp.Name, DesignerUI.White, GameFont.Medium);
                    infoY += 37;
                    DesignerUI.Txt(new Rect(r.x, infoY, r.width, 72), sp.Details, DesignerUI.Muted);
                    infoY += 80;
                    DesignerUI.Txt(new Rect(r.x, infoY, r.width, 180),
                        "Ресурсы: " + WeaponCosts.Display(sp.Effects) + "\n" + DesignerUI.Effects(sp.Effects), DesignerUI.Accent);
                }
            }
            Widgets.EndScrollView();
        }
        private void ShowSpecialMenu(int index)
        {
            var opts = new List<FloatMenuOption> { new FloatMenuOption("[пустой слот]", () => design.Special[index] = -1) };
            for (int j = 0; j < WeaponCatalog.Specials.Length; j++)
            {
                bool taken = false;
                for (int k = 0; k < 3; k++) if (k != index && design.Extra(k) == j) taken = true;
                if (taken) continue;
                int id = j;
                var sp = WeaponCatalog.Specials[id];
                opts.Add(new FloatMenuOption(sp.Target + " / " + sp.Name + " | " + DesignerUI.Effects(sp.Effects).Split('\n')[0] + "  [" + WeaponCosts.Display(sp.Effects) + "]", () => { design.Special[index] = id; showKind = 1; selectedSpecialSlot = index; }));
            }
            Find.WindowStack.Add(new FloatMenu(opts));
        }
        private void EnqueueResearch()
        {
            if (!design.IsValid) { Messages.Message(design.ValidationProblem, MessageTypeDefOf.RejectInput, false); return; }
            RecipeDef recipe = DefDatabase<RecipeDef>.GetNamedSilentFail("TT_DevelopDesign");
            if (recipe == null || bench?.billStack == null) { Messages.Message("Стол разработки недоступен", MessageTypeDefOf.RejectInput, false); return; }
            bench.billStack.AddBill(new Bill_WeaponResearch(recipe, design));
            Messages.Message("Разработка в очереди: " + design.Title, MessageTypeDefOf.NeutralEvent, false);
            Close();
        }
    }
    public sealed class Dialog_WeaponManufacture : Window
    {
        private readonly Building_WorkTable bench;
        private Vector2 scroll;
        private int selectedId = -1;
        public override Vector2 InitialSize => new Vector2(Mathf.Min(1100, UI.screenWidth - 40), Mathf.Min(740, UI.screenHeight - 40));
        public Dialog_WeaponManufacture(Building_WorkTable b)
        { bench = b; doCloseX = true; absorbInputAroundWindow = true; }
        public override void DoWindowContents(Rect r)
        {
            Widgets.DrawBoxSolid(r, DesignerUI.Back);
            DesignerUI.Txt(new Rect(18, 11, r.width - 34, 35), "ОРУЖЕЙНАЯ БИБЛИОТЕКА  /  4 СЕМЕЙСТВА  /  РАЗРАБОТАННЫЕ ЧЕРТЕЖИ", DesignerUI.White, GameFont.Medium);
            var list = GameComponent_WeaponLibrary.Current?.Developed;
            if (list == null || list.Count == 0)
            { DesignerUI.Txt(new Rect(26, 78, r.width - 45, 90), "Нет разработанных проектов. Сначала закончи исследование на столе разработки.", DesignerUI.Brass); return; }
            float left = Mathf.Min(r.width * .42f, 385);
            Rect listArea = new Rect(12, 64, left, r.height - 81);
            DesignerUI.Panel(listArea, DesignerUI.Pane);
            Rect content = new Rect(0, 0, listArea.width - 20, list.Count * 68 + 14);
            Widgets.BeginScrollView(new Rect(listArea.x + 5, listArea.y + 5, listArea.width - 10, listArea.height - 10), ref scroll, content);
            for (int i = 0; i < list.Count; i++)
            {
                var b = list[i]; float y = 6 + i * 68;
                if (DesignerUI.Action(new Rect(4, y, content.width - 9, 60),
                    "№" + b.Identifier + "  " + b.Title + "\n" + b.SpecialCount + " улучшения / пласталь: " + b.PlasteelCount,
                    b.Identifier == selectedId)) selectedId = b.Identifier;
            }
            Widgets.EndScrollView();
            WeaponBlueprint chosen = list[0];
            foreach (var b in list) if (b.Identifier == selectedId) { chosen = b; break; }
            float x = left + 25, w = r.width - x - 13;
            DesignerUI.Panel(new Rect(x, 64, w, r.height - 81), DesignerUI.Pane);
            DesignerUI.Txt(new Rect(x + 15, 79, w - 30, 27), chosen.Title, DesignerUI.Accent, GameFont.Medium);
            WeaponVisuals.DrawPreview(new Rect(x + 7, 116, w - 14, 202), chosen);
            DesignerUI.Txt(new Rect(x + 16, 330, w - 30, 195), DesignerUI.Stats(chosen, 1f), DesignerUI.White);
            DesignerUI.Txt(new Rect(x + 16, r.height - 148, w - 30, 58),
                WeaponCatalog.Family(chosen.FamilyId).Label + " | МАТЕРИАЛЫ: " + DesignerUI.Materials(chosen) + "\nИтоговое качество определяется изготовителем.", DesignerUI.Muted);
            if (DesignerUI.Action(new Rect(x + 15, r.height - 81, w - 30, 48), "ЗАКАЗАТЬ ПРОИЗВОДСТВО  ›"))
            {
                if (!chosen.IsValid) { Messages.Message("Недействительная схема", MessageTypeDefOf.RejectInput, false); return; }
                RecipeDef recipe = DefDatabase<RecipeDef>.GetNamedSilentFail(WeaponCatalog.RecipeName(chosen));
                if (recipe == null || bench?.billStack == null)
                { Messages.Message("Рецепт этого чертежа отсутствует", MessageTypeDefOf.RejectInput, false); return; }
                var bill = new Bill_WeaponManufacture(recipe, chosen);
                if (!WeaponCosts.TryPrepay(bench, bill, out string paymentError))
                { Messages.Message(paymentError, MessageTypeDefOf.RejectInput, false); return; }
                bench.billStack.AddBill(bill);
                Messages.Message("Заказана сборка: " + chosen.Title + ". Ресурсы зарезервированы.", MessageTypeDefOf.NeutralEvent, false);
            }
        }
    }
    public sealed class Dialog_WeaponInspect : Window
    {
        private readonly Thing rifle;
        public override Vector2 InitialSize => new Vector2(Mathf.Min(890, UI.screenWidth - 50), Mathf.Min(570, UI.screenHeight - 50));
        public Dialog_WeaponInspect(Thing t) { rifle = t; doCloseX = true; absorbInputAroundWindow = true; }
        public override void DoWindowContents(Rect r)
        {
            Widgets.DrawBoxSolid(r, DesignerUI.Back);
            var comp = rifle?.TryGetComp<CompWeaponDesign>(); var b = comp?.Blueprint;
            if (b == null) return;
            DesignerUI.Txt(new Rect(17, 15, r.width - 35, 38), "ТЕХНИЧЕСКИЙ ПАСПОРТ  /  " + b.Title, DesignerUI.White, GameFont.Medium);
            DesignerUI.Panel(new Rect(13, 66, r.width - 26, 245), DesignerUI.Pane);
            WeaponVisuals.DrawPreview(new Rect(26, 77, r.width - 52, 218), b);
            DesignerUI.Txt(new Rect(28, 324, r.width - 47, 192),
                DesignerUI.Stats(b, WeaponTuning.QualityFactor(rifle)), DesignerUI.Accent);
        }
    }
}
