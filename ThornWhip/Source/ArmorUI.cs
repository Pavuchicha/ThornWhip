using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace ThornWhip
{
    // Research interface: discrete class, base tier and per-slot choices. No preset substitution.
    public sealed class Dialog_ArmorDesign : Window
    {
        private readonly Building_WorkTable bench;
        private ArmorBlueprint b;
        private int selectedPart=0,selectedSpecial=0,mode=0,previewQuality=2;
        private Vector2 partScroll,infoScroll;
        private string title;
        private static readonly float[] Quality={.76f,.88f,1f,1.07f,1.13f,1.2f,1.27f};
        public override Vector2 InitialSize=>new Vector2(Mathf.Min(1370,UI.screenWidth-36),Mathf.Min(920,UI.screenHeight-36));
        public Dialog_ArmorDesign(Building_WorkTable station)
        {bench=station;b=new ArmorBlueprint();b.ChangeChassis(0);title=b.Title;doCloseX=true;absorbInputAroundWindow=true;}
        public override void DoWindowContents(Rect r)
        {
            Widgets.DrawBoxSolid(r,DesignerUI.Back);
            DesignerUI.Txt(new Rect(17,10,r.width-36,33),"КОРПУС ТЕРНА   /   АРХИТЕКТУРА БРОНЕЗАЩИТЫ",DesignerUI.White,GameFont.Medium);
            DesignerUI.Txt(new Rect(17,48,123,25),"ЧЕРТЁЖ",DesignerUI.Accent);
            title=Widgets.TextField(new Rect(137,44,r.width*.55f,29),title);b.Title=title;
            float leftWidth=r.width*.55f-15;
            for(int family=0;family<3;family++)
            {
                int id=family;
                int chassis=family*3+(b.Chassis.Tier-1);
                if(DesignerUI.Action(new Rect(16+family*(leftWidth-15)/3,85,(leftWidth-20)/3-4,39),
                    new[]{"ЛЁГКАЯ  /  ЖИЛЕТ","СРЕДНЯЯ  /  ШТУРМ","ТЯЖЁЛАЯ  /  ЭКЗО"}[family],b.Chassis.FamilyId==family))
                {if(b.ChassisId!=chassis){b.ChangeChassis(chassis);selectedPart=0;title=b.Title;}}
            }
            for(int tier=1;tier<=3;tier++)
            {
                int chassis=b.Chassis.FamilyId*3+tier-1;
                if(DesignerUI.Action(new Rect(16+(tier-1)*(leftWidth-15)/3,128,(leftWidth-20)/3-4,34),
                    "Т"+tier+"  /  "+new[]{"","ИНДУСТРИАЛ","КОСМИЧЕСКИЙ","УЛЬТРАТЕХ"}[tier],b.ChassisId==chassis))
                {if(b.ChassisId!=chassis){b.ChangeChassis(chassis);selectedPart=0;title=b.Title;}}
            }
            DesignerUI.Panel(new Rect(15,171,leftWidth-4,190),DesignerUI.Pane);
            ArmorVisuals.DrawPreview(new Rect(32,175,leftWidth-35,181),b);
            DesignerUI.Txt(new Rect(19,370,leftWidth-10,25),"УЗЛЫ  /  ОБЯЗАТЕЛЬНЫЕ *  ·  ПУСТЫЕ НЕОБЯЗАТЕЛЬНЫЕ ДОПУСТИМЫ",DesignerUI.Accent);
            Rect area=new Rect(17,399,leftWidth-6,Mathf.Max(80,r.height-590));
            var slots=ArmorCatalog.Parts(b);
            float rowHeight=51,contentHeight=slots.Length*rowHeight;
            Widgets.BeginScrollView(area,ref partScroll,new Rect(0,0,area.width-20,contentHeight));
            for(int i=0;i<slots.Length;i++)
            {
                int index=i;ArmorSlot slot=slots[i];float y=i*rowHeight;
                bool active=mode==0 && selectedPart==i;
                Widgets.DrawBoxSolid(new Rect(0,y,area.width-22,rowHeight-3),active?DesignerUI.Card:DesignerUI.Pane);
                string label=(i+1).ToString("00")+"  "+slot.Name+(slot.Required?" *":"");
                if(DesignerUI.Action(new Rect(3,y+4,area.width*.43f,rowHeight-11),label,active))
                {selectedPart=index;mode=0;}
                int chosen=b.Part(i);
                string option=chosen<0?"ПУСТО / + установить":slot.Options[chosen].Name;
                if(DesignerUI.Action(new Rect(area.width*.43f+6,y+4,area.width*.39f-2,rowHeight-11),option,chosen>=0))
                {selectedPart=index;mode=0;MenuPart(index);}
                if(DesignerUI.Action(new Rect(area.width*.82f+6,y+4,area.width*.16f-21,rowHeight-11),
                    new[]{"СТ","ПЛ","УР"}[b.Material(i)]))
                {
                    if(b.Chassis.Tier>1){b.Materials[i]=(b.Material(i)+1)%3;selectedPart=index;mode=0;}
                }
            }
            Widgets.EndScrollView();
            float spY=r.height-173;
            DesignerUI.Txt(new Rect(20,spY,leftWidth-10,23),"3 УНИВЕРСАЛЬНЫХ ОСОБЫХ СЛОТА  /  ОБЩИЙ ПУЛ 15",DesignerUI.Accent);
            for(int i=0;i<3;i++)
            {
                int special=b.Extra(i);
                string text=special<0?"+ ДОБАВИТЬ":ArmorCatalog.Specials[special].Name;
                if(DesignerUI.Action(new Rect(17+i*(leftWidth-8)/3,spY+27,(leftWidth-16)/3-3,41),text,mode==1 && selectedSpecial==i))
                {selectedSpecial=i;mode=1;MenuSpecial(i);}
            }
            if(DesignerUI.Action(new Rect(18,r.height-88,120,53),"БАЗОВЫЙ НАБОР"))
            {
                for(int i=0;i<slots.Length;i++)b.Parts[i]=slots[i].Required?0:-1;
            }
            DesignerUI.Txt(new Rect(146,r.height-89,leftWidth-283,51),
                !ArmorTechnology.Available(b.Chassis.Tier)?"НУЖНО ИССЛЕДОВАНИЕ Т"+b.Chassis.Tier:(b.IsValid?"РАЗРАБОТКА ДОСТУПНА":("НЕ ГОТОВО: "+b.MissingCount+" узлов / проверь Т-ограничения")),
                b.IsValid && ArmorTechnology.Available(b.Chassis.Tier)?DesignerUI.Accent:DesignerUI.Brass);
            if(DesignerUI.Action(new Rect(leftWidth-142,r.height-88,132,53),"ИССЛЕДОВАТЬ  ›",b.IsValid && ArmorTechnology.Available(b.Chassis.Tier)))Research();
            // Engineering report, with true per-area CE values, not a generic hit chance.
            float right=leftWidth+14,width=r.width-right-13;
            DesignerUI.Panel(new Rect(right,84,width,r.height-107),DesignerUI.Pane);
            Rect info=new Rect(right+12,93,width-24,r.height-123);
            Widgets.BeginScrollView(info,ref infoScroll,new Rect(0,0,info.width-20,950));
            DesignerUI.Txt(new Rect(0,0,info.width-22,32),"ПАСПОРТ CE  /  "+b.Chassis.Label,DesignerUI.Accent,GameFont.Medium);
            ArmorTuning t=ArmorTuning.Evaluate(b);float q=Quality[previewQuality];
            var c=b.Chassis;
            float sharp=Math.Max(0,c.Sharp+t.Adjust(t.Sharp,q,true));
            float blunt=Math.Max(0,c.Blunt+t.Adjust(t.Blunt,q,true));
            float heat=Math.Max(0,Math.Min(1,c.Heat+t.Adjust(t.Heat,q,true)));
            string lines=$"БАЗОВАЯ ЗАЩИТА (до региональных пластин)\n\n"+
                $"CE Sharp: {sharp:F1} мм RHA\nCE Blunt: {blunt:F1} МПа\nCE Heat: {heat:F2}\n"+
                $"МАССА: {Math.Max(.1,c.Mass+t.Mass):F1} кг\nГабарит: {Math.Max(0,c.Bulk+t.Bulk):F1}\nWornBulk: {Math.Max(0,c.WornBulk+t.WornBulk):F1}\n"+
                $"Движение: {c.Move+t.Adjust(t.Move,q,true):+0.00;-0.00} кл./с\n"+
                $"Грузоподъёмность: {t.Carry:+0.0;-0.0}\nДопустимый объём CE: {t.CarryBulk:+0.0;-0.0}\n\n"+
                "ЗОНЫ: "+(c.FamilyId==0?"ТОЛЬКО ТОРС":c.FamilyId==1?"ТОРС, РУКИ, НОГИ (+ ПЕРЧАТКИ/БОТИНКИ/ШЛЕМ)":"ТОРС, КОНЕЧНОСТИ, КИСТИ, СТОПЫ, ГОЛОВА")+"\n\n"+
                "СМЕТА: "+ArmorCosts.Display(b)+"\n";
            DesignerUI.Txt(new Rect(4,39,info.width-30,360),lines,DesignerUI.White);
            if(DesignerUI.Action(new Rect(5,415,info.width-27,38),"ПРЕВЬЮ КАЧЕСТВА  /  "+(previewQuality+1)+" ИЗ 7"))previewQuality=(previewQuality+1)%Quality.Length;
            int lineY=469;
            if(mode==0 && selectedPart<slots.Length)
            {
                var slot=slots[selectedPart];
                DesignerUI.Txt(new Rect(6,lineY,info.width-20,30),"УЗЕЛ  /  "+slot.Name,DesignerUI.Accent,GameFont.Medium);
                lineY+=39;
                for(int i=0;i<5;i++)
                {
                    var opt=slot.Options[i];
                    DesignerUI.Txt(new Rect(10,lineY,info.width-22,30),
                        (i+1)+". Т"+opt.MinTier+" "+opt.Name, b.Part(selectedPart)==i?DesignerUI.Accent:DesignerUI.White);
                    lineY+=28;
                    DesignerUI.Txt(new Rect(17,lineY,info.width-27,40),
                        $"Sharp {opt.Sharp:+0.0;-0.0} / Blunt {opt.Blunt:+0.0;-0.0} / масса {opt.Mass:+0.0;-0.0}\n"+ArmorCosts.Display(opt),DesignerUI.Muted);
                    lineY+=60;
                }
            }
            else if(mode==1 && b.Extra(selectedSpecial)>=0)
            {
                var opt=ArmorCatalog.Specials[b.Extra(selectedSpecial)];
                DesignerUI.Txt(new Rect(6,lineY,info.width-20,30),"ОСОБЫЙ  /  "+opt.Name,DesignerUI.Accent);
                DesignerUI.Txt(new Rect(6,lineY+39,info.width-20,90),ArmorCosts.Display(opt),DesignerUI.Muted);
            }
            Widgets.EndScrollView();
        }
        private void MenuPart(int i)
        {
            var opts=new List<FloatMenuOption>();var slot=ArmorCatalog.Parts(b)[i];
            if(!slot.Required)opts.Add(new FloatMenuOption("[не устанавливать]",()=>b.Parts[i]=-1));
            for(int j=0;j<slot.Options.Length;j++)
            {
                int id=j;var o=slot.Options[j];
                if(o.MinTier>b.Chassis.Tier)continue;
                opts.Add(new FloatMenuOption("Т"+o.MinTier+" · "+o.Name+" ["+ArmorCosts.Display(o)+"]",()=>b.Parts[i]=id));
            }
            Find.WindowStack.Add(new FloatMenu(opts));
        }
        private void MenuSpecial(int slot)
        {
            var options=new List<FloatMenuOption>{new FloatMenuOption("[пусто]",()=>b.Specials[slot]=-1)};
            for(int j=0;j<ArmorCatalog.Specials.Length;j++)
            {
                int id=j;var o=ArmorCatalog.Specials[j];
                if(o.MinTier>b.Chassis.Tier || !b.RegionAllowed(o.Region))continue;
                bool taken=false;for(int k=0;k<3;k++)if(k!=slot && b.Extra(k)==j)taken=true;
                if(taken)continue;
                options.Add(new FloatMenuOption("Т"+o.MinTier+" / "+o.Name,()=>b.Specials[slot]=id));
            }
            Find.WindowStack.Add(new FloatMenu(options));
        }
        private void Research()
        {
            if(!b.IsValid || !ArmorTechnology.Available(b.Chassis.Tier) || bench?.billStack==null)return;
            var recipe=DefDatabase<RecipeDef>.GetNamedSilentFail("TC_DevelopArmor");
            if(recipe==null)return;
            bench.billStack.AddBill(new Bill_ArmorResearch(recipe,b));
            Messages.Message("Бронепроект поставлен в очередь: "+b.Title,MessageTypeDefOf.NeutralEvent,false);Close();
        }
    }
    public sealed class Dialog_ArmorManufacture:Window
    {
        private readonly Building_WorkTable bench;private Vector2 scroll;private int selected=-1;
        public override Vector2 InitialSize=>new Vector2(Mathf.Min(1110,UI.screenWidth-40),Mathf.Min(750,UI.screenHeight-40));
        public Dialog_ArmorManufacture(Building_WorkTable table){bench=table;doCloseX=true;absorbInputAroundWindow=true;}
        public override void DoWindowContents(Rect r)
        {
            Widgets.DrawBoxSolid(r,DesignerUI.Back);
            DesignerUI.Txt(new Rect(15,12,r.width-30,32),"КОРПУС ТЕРНА  /  ИССЛЕДОВАННЫЕ БРОНЕПРОЕКТЫ",DesignerUI.White,GameFont.Medium);
            var list=GameComponent_ArmorLibrary.Current?.Developed;
            if(list==null || list.Count==0){Widgets.Label(new Rect(22,78,r.width-40,65),"Нет завершённых проектов. Создай броню на столе разработки.");return;}
            float left=r.width*.40f;
            Rect view=new Rect(13,58,left,r.height-73);
            Widgets.BeginScrollView(view,ref scroll,new Rect(0,0,left-20,list.Count*61+8));
            for(int i=0;i<list.Count;i++)
            {var item=list[i];if(DesignerUI.Action(new Rect(4,i*61,left-33,56),item.Title+"  /  "+item.Chassis.Label,item.Identifier==selected))selected=item.Identifier;}
            Widgets.EndScrollView();
            ArmorBlueprint b=list[0];foreach(var item in list)if(item.Identifier==selected)b=item;
            float x=left+35,w=r.width-x-18;
            DesignerUI.Panel(new Rect(x,60,w,r.height-76),DesignerUI.Pane);
            DesignerUI.Txt(new Rect(x+15,69,w-28,31),b.Title,DesignerUI.Accent,GameFont.Medium);
            ArmorVisuals.DrawPreview(new Rect(x+11,108,w-22,256),b);
            var c=b.Chassis;var t=ArmorTuning.Evaluate(b);
            string stats=$"CE Sharp: {c.Sharp+t.Sharp:F1} / CE Blunt: {c.Blunt+t.Blunt:F1}\n"+
                $"Масса: {c.Mass+t.Mass:F1} кг / WornBulk: {c.WornBulk+t.WornBulk:F1}\n"+
                "Набор: "+ArmorCosts.Display(b);
            DesignerUI.Txt(new Rect(x+19,380,w-42,150),stats,DesignerUI.White);
            if(DesignerUI.Action(new Rect(x+19,r.height-95,w-37,58),"ЗАКАЗАТЬ ИЗГОТОВЛЕНИЕ"))
            {
                if(!b.IsValid || !ArmorTechnology.Available(b.Chassis.Tier))
                {Messages.Message("Требуется исследование бронесистем Т"+b.Chassis.Tier,MessageTypeDefOf.RejectInput,false);return;}
                var recipe=DefDatabase<RecipeDef>.GetNamedSilentFail("TC_Craft_Armor_"+c.Key+"_T"+c.Tier);
                if(recipe==null || bench?.billStack==null)return;
                var order=new Bill_ArmorManufacture(recipe,b);
                if(!ArmorCosts.TryPrepay(bench,order,out string error))
                {Messages.Message(error,MessageTypeDefOf.RejectInput,false);return;}
                bench.billStack.AddBill(order);
                Messages.Message("Сборка бронекомплекта заказана: "+b.Title,MessageTypeDefOf.NeutralEvent,false);
            }
        }
    }
    public sealed class Dialog_ArmorInspect:Window
    {
        private readonly Thing item;
        public override Vector2 InitialSize=>new Vector2(Mathf.Min(900,UI.screenWidth-30),Mathf.Min(700,UI.screenHeight-30));
        public Dialog_ArmorInspect(Thing armor){item=armor;doCloseX=true;absorbInputAroundWindow=true;}
        public override void DoWindowContents(Rect r)
        {
            Widgets.DrawBoxSolid(r,DesignerUI.Back);
            var b=item?.TryGetComp<CompArmorDesign>()?.Blueprint;if(b==null)return;
            DesignerUI.Txt(new Rect(14,12,r.width-28,35),"ПАСПОРТ БРОНЕСИСТЕМЫ / "+b.Title,DesignerUI.White,GameFont.Medium);
            ArmorVisuals.DrawPreview(new Rect(26,55,r.width-52,320),b);
            var c=b.Chassis;var t=ArmorTuning.Evaluate(b);float q=WeaponTuning.QualityFactor(item);
            DesignerUI.Txt(new Rect(25,385,r.width-48,170),
                $"База: {c.Label} / качество: ×{q:F2}\n"+
                $"CE Sharp {c.Sharp+t.Adjust(t.Sharp,q,true):F1}, Blunt {c.Blunt+t.Adjust(t.Blunt,q,true):F1}, Heat {c.Heat+t.Heat:F2}\n"+
                $"Масса {c.Mass+t.Mass:F1} кг, WornBulk {c.WornBulk+t.WornBulk:F1}, движение {c.Move+t.Move:+0.00;-0.00}\n"+
                "Материалы: "+ArmorCosts.Display(b),DesignerUI.White);
        }
    }
}
