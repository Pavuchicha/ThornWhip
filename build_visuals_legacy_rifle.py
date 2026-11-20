#!/usr/bin/env python3
"""Original layered pixel-art for the Thorn Whip rifle. No third-party game assets."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math
root=Path(__file__).resolve().parent
out=root/'ThornWhip/Textures/ThornWhip/Parts';out.mkdir(parents=True,exist_ok=True)
W,H=1024,320
outline='#101c1f';line='#172829';gun='#415750';mid='#60786d';light='#85998a';teal='#4be2cd';rust='#cfa86d';dark='#283a37'

def canvas():
    im=Image.new('RGBA',(W,H),(0,0,0,0));return im,ImageDraw.Draw(im)
def poly(d,xy,fill=gun,wd=5):d.polygon(xy,fill=fill);d.line(xy+[xy[0]],fill=outline,width=wd,joint='curve')
def rr(d,xy,rad=7,fill=gun,stroke=outline,w=4):d.rounded_rectangle(xy,radius=rad,fill=fill,outline=stroke,width=w)
def trace(d,pts,col=teal,wd=5):d.line(pts,fill=col,width=wd,joint='curve')
def dot(d,x,y,c=teal,r=4):d.ellipse([x-r,y-r,x+r,y+r],fill=c)
def slot(n,v):
    im,d=canvas()
    if n==0: # upper receiver
        if v==0:
            poly(d,[(392,118),(632,118),(642,152),(629,178),(400,179)],gun)
            rr(d,(425,126,601,146),5,dark);trace(d,[(446,137),(527,137)],light,4)
            for x in range(420,615,18):d.line((x,118,x+6,118),fill=light,width=3)
        else:
            poly(d,[(392,114),(627,107),(652,142),(638,177),(393,177)],mid)
            rr(d,(427,120,609,146),5,dark);trace(d,[(460,134),(599,134)],teal,4)
            for x in range(425,610,19):d.line((x,113,x+7,112),fill=teal,width=2)
    elif n==1: # lower
        if v==0:
            poly(d,[(440,178),(619,179),(594,217),(489,218),(477,204),(437,201)],gun)
            rr(d,(493,182,550,195),3,mid)
        else:
            poly(d,[(442,177),(621,178),(599,214),(486,218),(457,206)],mid)
            trace(d,[(473,198),(532,198),(571,184)],teal,4);trace(d,[(548,206),(587,206)],light,2)
    elif n==2: # barrel
        if v==0:
            rr(d,(630,142,895,159),3,dark);trace(d,[(645,150),(875,150)],light,2)
        else:
            rr(d,(632,143,938,157),3,gun);trace(d,[(650,148),(918,148)],rust,2)
            for x in range(672,915,34):d.line((x,140,x+9,140),fill=light,width=2)
    elif n==3: # bolt group viewing port
        rr(d,(467,152,572,176),5,dark)
        if v==0:rr(d,(482,158,545,169),3,light,outline,2);rr(d,(554,158,564,169),2,mid,outline,1)
        else:
            rr(d,(479,158,561,170),4,mid,teal,2);trace(d,[(492,165),(552,165)],teal,2)
    elif n==4: # gas block
        if v==0:rr(d,(728,136,753,162),4,gun);dot(d,739,142,light,2)
        else:rr(d,(728,132,760,165),3,mid);trace(d,[(733,139),(755,139)],teal,3);dot(d,745,151,rust,3)
    elif n==5: # fire control
        if v==0:
            poly(d,[(517,206),(532,208),(527,238),(518,236)],dark)
            trace(d,[(510,215),(528,218)],light,3)
        else:
            poly(d,[(518,207),(534,207),(535,233),(524,237)],mid)
            trace(d,[(514,210),(536,210)],teal,3);dot(d,523,223,teal,3)
    elif n==6: # buffer assembly
        if v==0:
            rr(d,(352,152,445,167),4,dark)
            for x in range(364,434,12):d.line((x,155,x,164),fill=light,width=2)
        else:
            rr(d,(348,148,448,173),5,gun);rr(d,(362,154,423,166),4,mid)
            trace(d,[(365,159),(430,159)],rust,2)
    elif n==7: # stock
        if v==0:
            poly(d,[(135,138),(171,128),(348,145),(356,183),(180,204),(134,183)],gun)
            rr(d,(130,137,150,192),5,mid)
            poly(d,[(190,148),(303,150),(329,171),(182,184)],dark,2)
        else:
            poly(d,[(133,143),(193,129),(349,142),(367,179),(323,195),(186,198),(130,181)],mid)
            rr(d,(128,137,152,190),5,dark)
            trace(d,[(180,150),(286,150),(328,165)],teal,5)
            rr(d,(194,182,297,190),4,dark)
    elif n==8: # handguard
        if v==0:
            poly(d,[(628,125),(808,124),(827,177),(633,175)],gun)
            rr(d,(659,137,796,154),4,dark)
            for x in range(668,796,24):d.line((x,137,x+12,137),fill=light,width=5)
        else:
            poly(d,[(629,122),(826,126),(842,174),(630,178)],mid)
            rr(d,(648,134,815,153),4,dark)
            for x in range(659,805,18):d.line((x,138,x+8,138),fill=teal,width=3)
            trace(d,[(656,164),(817,164)],rust,4)
    elif n==9: # magazine
        if v==0:
            poly(d,[(551,202),(601,198),(610,269),(562,272)],gun)
            rr(d,(563,210,594,251),4,dark);trace(d,[(572,256),(600,256)],light,2)
        else:
            poly(d,[(548,202),(607,197),(625,286),(557,291)],mid)
            for y in range(218,270,14):trace(d,[(567,y),(605,y-3)],dark,4)
            trace(d,[(567,277),(616,272)],teal,3)
    elif n==10: # sight
        if v==0:
            rr(d,(514,107,611,119),3,mid)
            for x in [526,591]:rr(d,(x,98,x+8,108),2,dark)
        else:
            poly(d,[(522,118),(536,82),(587,82),(604,118)],gun)
            rr(d,(543,88,582,111),5,dark,teal,3)
            rr(d,(525,113,606,122),3,mid)
            dot(d,562,101,r=3)
    elif n==11: # grip
        if v==0:
            poly(d,[(452,201),(504,203),(489,284),(451,286)],gun)
            for y in range(230,275,13):trace(d,[(462,y),(484,y)],dark,3)
        else:
            poly(d,[(455,201),(508,205),(484,286),(446,286)],mid)
            trace(d,[(461,215),(486,230),(467,269)],teal,3)
            rr(d,(455,266,481,277),3,dark)
    elif n==12: # charging handle
        if v==0:
            rr(d,(397,129,436,136),2,light,outline,2);rr(d,(395,125,405,144),3,dark)
        else:
            rr(d,(392,126,450,139),3,mid);trace(d,[(408,128),(441,128)],teal,3);rr(d,(391,122,402,143),3,dark)
    elif n==13: # muzzle
        if v==0:
            rr(d,(890,139,952,164),4,gun)
            for x in [905,925,943]:d.line((x,145,x,157),fill=outline,width=5)
        else:
            poly(d,[(892,135),(966,135),(969,156),(947,168),(892,166)],mid)
            for x in [907,926,947]:d.line((x,140,x+4,162),fill=dark,width=5)
            trace(d,[(911,134),(951,134)],teal,3)
    return im

def special(n):
    im,d=canvas()
    if n==0: # laser
        rr(d,(739,178,806,192),4,dark,teal,3);dot(d,807,184,r=5)
        trace(d,[(782,192),(782,204)],gun,5)
    if n==1: # spectral
        poly(d,[(626,116),(639,77),(672,72),(705,95),(710,117)],mid)
        rr(d,(646,83,684,110),8,dark,teal,3);dot(d,671,98,teal,4)
    if n==2: # optic neurolink
        rr(d,(491,77,536,108),5,dark,teal,3)
        trace(d,[(503,85),(528,85),(522,96),(510,96)],teal,3)
        trace(d,[(520,108),(530,118)],rust,2)
    if n==3: # electronic trigger
        rr(d,(493,185,548,201),4,dark,rust,3)
        for x in (507,522,537):dot(d,x,193,teal,2)
    if n==4: # bolt stabilizer
        rr(d,(398,180,462,205),5,dark,rust,2)
        trace(d,[(408,194),(420,187),(434,196),(451,187)],teal,3)
    if n==5: # assisted feeding
        rr(d,(606,221,639,262),4,gun,teal,3)
        trace(d,[(615,230),(630,230),(630,248)],rust,3)
    if n==6: # servo on underside
        rr(d,(678,185,814,200),6,dark,teal,3)
        for x in [692,722,752,782]:d.line((x,189,x,197),fill=light,width=3)
    if n==7: # barrel thermal regulator
        rr(d,(838,130,873,171),4,gun,rust,3)
        for x in [845,852,859,866]:d.line((x,135,x,165),fill=teal,width=2)
    if n==8: # magazine intelligent feed
        rr(d,(600,210,640,242),4,dark,teal,3)
        dot(d,621,226,r=5)
    return im

def write():
    for i in range(14):
        for v in range(2):slot(i,v).save(out/f'P{i:02}_V{v}.png',optimize=True)
    for i in range(9):special(i).save(out/f'S{i:02}.png',optimize=True)
    base,d=canvas()
    # tiny structural mounting spine behind modular components
    rr(d,(353,146,635,178),7,'#243531','#162625',5)
    trace(d,[(367,158),(613,158)],'#44605a',3)
    base.save(out/'Chassis.png',optimize=True)
    # Full representative 8 default variants are a visual fallback if dynamic drawing is unsupported.
    fallback=root/'ThornWhip/Textures/Things/Weapons'
    for r in range(2):
        for b in range(2):
            for m in range(2):
                im=base.copy()
                # Composite every mandatory component for fallback; other 11 parts stock by default.
                order=[7,6,2,0,1,3,4,5,8,9,10,11,12,13]
                for i in order:
                    v={0:r,2:b,9:m}.get(i,0)
                    im.alpha_composite(slot(i,v))
                im.save(fallback/f'TW_R{r}B{b}M{m}.png',optimize=True)
    # Showcase image, styled mock of first frame of user-facing workshop UI. Contains no fake runtime claims.
    chosen=base.copy()
    choices={0:1,1:1,2:1,3:1,4:1,5:1,6:1,7:1,8:1,9:1,10:1,11:1,12:1,13:1}
    for i in [7,6,2,0,1,3,4,5,8,9,10,11,12,13]:chosen.alpha_composite(slot(i,choices[i]))
    for s in [2,0,7]:chosen.alpha_composite(special(s))
    big=Image.new('RGB',(1400,860),'#111b22');d=ImageDraw.Draw(big)
    d.rounded_rectangle((20,20,1380,840),radius=22,fill='#1a2931',outline='#35535a',width=3)
    def font(size,bold=False):
        roots=['/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if bold else '')+'.ttf','/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf']
        for p in roots:
            try:return ImageFont.truetype(p,size)
            except:pass
        return ImageFont.load_default()
    d.text((52,42),'ПЛЕТЬ ТЕРНА',font=font(40,True),fill='#e4ece5')
    d.text((56,105),'МАРКСАНСКАЯ ВИНТОВКА  /  СИСТЕМА РАЗРАБОТКИ',font=font(17),fill='#74aca6')
    d.rounded_rectangle((47,158,926,514),radius=13,fill='#10191e',outline='#38585e',width=2)
    d.text((74,177),'КОНФИГУРАЦИЯ  /  ТЕХНИЧЕСКИЙ ВИД',font=font(18,True),fill='#59dbca')
    copy=chosen.resize((824,258),Image.Resampling.LANCZOS)
    big.paste(copy,(74,226),copy)
    d.rounded_rectangle((945,158,1350,514),radius=12,fill='#142129',outline='#38585e',width=2)
    d.text((971,181),'БОЕВЫЕ ПАРАМЕТРЫ  ·  CE',font=font(20,True),fill='#e9ecde')
    rows=[('ПРИЦЕЛ / SIGHTS','1.53',True),('РАЗБРОС / SPREAD','0.027°',False),('КОЛЕБАНИЕ / SWAY','0.53',False),('МАГАЗИН','30 патронов',True),('КАЛИБР','5,56×45 NATO',True)]
    for i,(a,b,good) in enumerate(rows):
        y=230+i*51;d.text((969,y),a,font=font(15),fill='#96a6a6');d.text((1235,y),b,font=font(17,True),fill='#5bd8c5' if good else '#e8c18b',anchor='ra')
    d.text((58,552),'14  ОБЯЗАТЕЛЬНЫХ  УЗЛОВ',font=font(23,True),fill='#eff3ea')
    cats=['КОРОБКА','СТВОЛ','ЗАТВОР','ПРИКЛАД','ЦЕВЬЁ','МАГАЗИН','ПРИЦЕЛ']
    for j,c in enumerate(cats):
        x=54+(j%4)*219;y=606+(j//4)*57
        d.rounded_rectangle((x,y,x+202,y+45),radius=8,fill='#253942',outline='#3b5a60',width=1)
        d.text((x+13,y+10),c,font=font(17,True),fill='#b8ded6')
    d.text((955,558),'3  УНИВЕРСАЛЬНЫХ СЛОТА',font=font(21,True),fill='#eff3ea')
    for j,t in enumerate(['01   Нейросвязь оптики','02   Лазерный целеуказатель','03   Термокомпенсатор']):
        y=606+j*58;d.rounded_rectangle((946,y,1351,y+45),radius=8,fill='#293f47',outline='#3f6d70',width=1)
        d.text((966,y+10),t,font=font(15),fill='#e5ede3')
    big.save(root/'Showcase/THORNWHIP_WORKSHOP_CONCEPT.png',optimize=True)
    print('Visual parts:',len(list(out.glob('*.png'))),'world defaults:',len(list(fallback.glob('*.png'))))
if __name__=='__main__':write()
