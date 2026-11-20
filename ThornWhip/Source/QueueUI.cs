using RimWorld;
using UnityEngine;
using Verse;

namespace ThornWhip
{
    // Worktables intentionally do not expose vanilla bill tab with 480 recipe defs.
    public sealed class Dialog_ThornQueue : Window
    {
        private readonly Building_WorkTable bench;
        private Vector2 scroll;
        public override Vector2 InitialSize => new Vector2(730f, 570f);
        public Dialog_ThornQueue(Building_WorkTable source)
        { bench = source; doCloseX = true; absorbInputAroundWindow = true; }
        public override void DoWindowContents(Rect rect)
        {
            Widgets.Label(new Rect(5, 5, rect.width - 12, 30), "ОЧЕРЕДЬ РАБОТ — " + (bench?.Label ?? "стол недоступен"));
            var bills = bench?.billStack?.Bills;
            if (bills == null || bills.Count == 0)
            { Widgets.Label(new Rect(6, 50, rect.width - 12, 35), "Заказов нет"); return; }
            Rect view = new Rect(3, 43, rect.width - 9, rect.height - 50);
            Widgets.BeginScrollView(view, ref scroll, new Rect(0, 0, view.width - 19, bills.Count * 56));
            for (int i = 0; i < bills.Count; i++)
            {
                Bill bill = bills[i];
                float y = i * 56;
                string description = (bill is Bill_WeaponResearch rd ? rd.Blueprint?.Title :
                    bill is Bill_WeaponManufacture md ? md.Blueprint?.Title :
                    bill is Bill_ArmorResearch ar ? ar.Blueprint?.Title :
                    bill is Bill_ArmorManufacture am ? am.Blueprint?.Title : "Неизвестный заказ") ?? "Без названия";
                Widgets.Label(new Rect(4, y + 3, view.width - 170, 24), description);
                Widgets.Label(new Rect(4, y + 27, view.width - 170, 24), bill.recipe?.label ?? "Работа");
                if (Widgets.ButtonText(new Rect(view.width - 161, y + 8, 144, 34), "Отменить"))
                {
                    if (bill is Bill_WeaponManufacture manufacturing) WeaponCosts.Refund(bench, manufacturing);
                    if (bill is Bill_ArmorManufacture armor) ArmorCosts.Refund(bench, armor);
                    bench.billStack.Delete(bill);
                    break;
                }
            }
            Widgets.EndScrollView();
        }
    }
}
