using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace ThornWhip
{
    // Flat, pre-authored transparent layers cached by texture path. Only UI draw events.
    // The worn sprite currently shows the selected chassis; the modular overlay appears in
    // designer/inspection. Dynamic per-pawn apparel render requires a verified 1.7 render node.
    public static class ArmorVisuals
    {
        private const string Root="ThornCorps/Armor/";
        private static readonly Dictionary<string,Texture2D> Images=new Dictionary<string,Texture2D>(320);
        private static Texture2D Get(string path)
        {
            if(!Images.TryGetValue(path,out var t))
            {t=ContentFinder<Texture2D>.Get(Root+path,false);Images[path]=t;}
            return t;
        }
        public static void DrawPreview(Rect r,ArmorBlueprint design)
        {
            if(design==null)return;
            string family=design.Chassis.Key;
            Color prior=GUI.color;GUI.color=Color.white;
            Texture2D baseTex=Get(family+"/Chassis_T"+design.Chassis.Tier);
            if(baseTex!=null)GUI.DrawTexture(r,baseTex,ScaleMode.ScaleToFit,true);
            for(int i=0;i<ArmorCatalog.Parts(design).Length;i++)
            {
                int selection=design.Part(i);if(selection<0)continue;
                Texture2D t=Get(family+"/P"+i.ToString("00")+"_V"+selection);
                GUI.color=design.Material(i)==1?new Color(.78f,1f,1f,1f):design.Material(i)==2?new Color(.91f,.77f,.60f,1f):Color.white;
                if(t!=null)GUI.DrawTexture(r,t,ScaleMode.ScaleToFit,true);
            }
            GUI.color=Color.white;
            for(int i=0;i<3;i++)
            {int id=design.Extra(i);if(id<0)continue;Texture2D t=Get(family+"/S"+id.ToString("00"));if(t!=null)GUI.DrawTexture(r,t,ScaleMode.ScaleToFit,true);}
            GUI.color=prior;
        }
    }
}
