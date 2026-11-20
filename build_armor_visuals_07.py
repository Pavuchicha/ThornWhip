#!/usr/bin/env python3
"""Generate per-part transparent armor overlays and nine vanilla-compatible worn chassis sprites."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageEnhance
import json,math
R=Path(__file__).parent; data=json.loads((R/'ThornWhip/Documentation/armor_catalog.json').read_text());
textures=R/'ThornWhip/Textures';previewRoot=textures/'ThornCorps/Armor';icons=textures/'Things/Armor';worn=icons/'Worn';show=R/'Showcase';
for root in (previewRoot,icons,worn,show):root.mkdir(parents=True,exist_ok=True)
SZ=(640,720)
INK=(12,23,32,255);SHADOW=(17,44,56,255)
PALETTES={1:[(53,72,77),(87,107,108),(28,53,64)],2:[(39,66,80),(70,110,118),(19,42,52)],3:[(30,61,80),(45,135,146),(13,33,51)]}

def poly(d,xy,fill,outline=(8,23,28,255),w=5):
 d.polygon(xy,fill=tuple(fill)+(255,) if len(fill)==3 else fill)
 d.line(xy+[xy[0]],fill=outline,width=w,joint='curve')
def line(d,xy,fill=(87,180,186,255),width=4):d.line(xy,fill=fill,width=width,joint='curve')

def chassis_image(kind,tier):
 im=Image.new('RGBA',SZ,(0,0,0,0));d=ImageDraw.Draw(im);c=PALETTES[tier];primary,highlight,dark=c
 if kind=='Light':
  poly(d,[(207,133),(272,121),(327,125),(402,144),(417,327),(359,364),(245,361),(195,335)],primary)
  poly(d,[(235,171),(279,150),(332,153),(379,177),(380,309),(353,331),(253,330),(228,302)],highlight)
  poly(d,[(232,179),(272,170),(285,284),(235,284)],dark)
  poly(d,[(354,169),(386,188),(385,287),(351,287)],dark)
  line(d,[(302,151),(304,323)],(10,27,37,255),8)
  for x in [239,359]:line(d,[(x,145),(x,332)],(140,144,130,255),9)
 elif kind=='Medium':
  # man-shaped multi-layer assault rig: torso, shoulders, arm guards, ballistic trousers
  poly(d,[(207,145),(261,126),(344,130),(399,151),(410,353),(372,389),(230,388),(193,348)],primary)
  poly(d,[(179,149),(209,146),(231,188),(214,320),(170,351),(140,315)],dark)
  poly(d,[(400,145),(431,157),(474,317),(446,355),(406,316),(389,187)],dark)
  poly(d,[(238,361),(296,375),(282,581),(243,590),(215,571)],dark)
  poly(d,[(306,375),(365,361),(390,570),(362,590),(317,581)],dark)
  poly(d,[(225,167),(273,154),(331,154),(380,172),(368,331),(318,353),(250,344)],highlight)
  poly(d,[(251,192),(299,182),(301,305),(262,318)],dark)
  poly(d,[(309,182),(355,192),(349,320),(306,308)],primary)
  for x in [250,350]:line(d,[(x,350),(x+8,374)],(153,177,180,255),8)
 else:
  # reinforced servo-assisted full-body shell, heavy joints, visible exoskeleton struts
  poly(d,[(251,49),(290,30),(345,43),(374,96),(354,154),(271,151),(238,100)],dark)
  poly(d,[(250,90),(282,68),(342,72),(361,105),(335,122),(268,120)],highlight)
  poly(d,[(184,143),(242,126),(351,126),(418,149),(451,373),(390,411),(220,410),(160,374)],primary)
  poly(d,[(157,158),(210,148),(232,209),(203,343),(142,380),(112,331)],dark)
  poly(d,[(415,148),(457,171),(494,340),(466,390),(418,337),(390,207)],dark)
  poly(d,[(214,371),(292,386),(285,605),(230,632),(193,593)],dark)
  poly(d,[(311,385),(391,372),(428,592),(390,633),(332,606)],dark)
  poly(d,[(223,178),(280,159),(336,161),(387,181),(373,356),(304,391),(225,355)],highlight)
  poly(d,[(235,180),(301,201),(294,332),(237,345)],primary)
  poly(d,[(303,201),(374,178),(371,340),(309,335)],primary)
  for x in [205,430]:line(d,[(x,180),(x-10 if x<320 else x+10,336)],(105,167,182,255),9)
  for x in [249,355]:line(d,[(x,402),(x,580)],(104,150,170,255),12)
  d.ellipse((272,84,339,107),fill=(77,187,194,255))
 # lines/rivets, accent markings
 for x,y in [(266,186),(339,185),(253,318),(360,320)]:
  d.ellipse((x-4,y-4,x+4,y+4),fill=(168,179,150,255))
 return im

# Each texture is deliberately a transparent full-canvas layer to avoid runtime compositing cost.
def overlay_image(kind,slot,opt,tier=2):
 im=Image.new('RGBA',SZ,(0,0,0,0));d=ImageDraw.Draw(im)
 c=(63+opt*18,105+opt*13,112+opt*12,235)
 edge=(7,27,33,255)
 # different physical assemblies occupy distinct zones; variation changes silhouette/shape
 region=slot['region'];i=slot['id'];v=opt
 offset=(i%4)*8-(v%2)*5
 if region=='Torso':
  y=183+(i%4)*30+offset;x=252+((i*9)%24)
  poly(d,[(x-35-v*2,y),(x+60+v*2,y+5),(x+68,y+53),(x-39,y+49)],c,edge,3)
  if v>=2:line(d,[(x-31,y+16),(x+52,y+17)],(132,195,185,255),3)
 elif region=='Arm':
  y=198+(i%3)*20+offset
  for x in (173,429):
   poly(d,[(x-21,y),(x+23,y+4),(x+13,y+67),(x-21,y+54)],c,edge,3)
 elif region=='Leg':
  y=394+(i%3)*46+offset
  for x in (245,352):poly(d,[(x-27,y),(x+22,y),(x+25,y+63),(x-25,y+70)],c,edge,3)
 elif region=='Hand':
  for x in (130,457):poly(d,[(x-30,325),(x+19,328),(x+25,372),(x-19,387)],c,edge,3)
 elif region=='Foot':
  for x in (240,363):poly(d,[(x-33,575),(x+29,577),(x+39,635),(x-26,640)],c,edge,3)
 elif region=='Head':
  poly(d,[(256,70-v*2),(313,46-v*2),(357,74),(351,130),(260,132)],c,edge,3)
  line(d,[(267,104),(345,105)],(105,211,221,255),5)
 else:
  x=207+(i%4)*55;y=155+(i%4)*70
  poly(d,[(x,y),(x+28+v*3,y+3),(x+34+v*3,y+53),(x-7,y+49)],c,edge,3)
  if v>=3:d.ellipse((x+3,y+10,x+25,y+29),fill=(104,210,213,255))
 return im

def special_image(region,i):
 im=Image.new('RGBA',SZ,(0,0,0,0));d=ImageDraw.Draw(im)
 glow=(107+min(i*4,90),172+min(i*3,50),164,240)
 x=238+(i%5)*23;y=164+(i%4)*35
 if region=='Head':x=285;y=94
 if region=='Arm':x=155;y=210
 if region=='Leg':x=252;y=467
 poly(d,[(x-22,y-10),(x+25,y-11),(x+33,y+28),(x-26,y+29)],(27,74,85,244),(7,24,27,255),3)
 d.ellipse((x-10,y-5,x+15,y+19),fill=glow)
 line(d,[(x-5,y+2),(x+8,y+15)],(212,238,222,255),2)
 return im

for fam in data['families']:
 key=fam['key'];out=previewRoot/key;out.mkdir(parents=True,exist_ok=True)
 for ch in fam['chassis']:
  t=ch['tier'];base=chassis_image(key,t)
  base.save(out/f'Chassis_T{t}.png')
  # ground inventory sprite / worn graphics. Worn direction images use the standard RimWorld naming.
  base.resize((256,288),Image.Resampling.LANCZOS).save(icons/f'TC_{key}_T{t}.png')
  base.resize((256,288),Image.Resampling.LANCZOS).save(worn/f'TC_{key}_T{t}_south.png')
  base.resize((256,288),Image.Resampling.LANCZOS).save(worn/f'TC_{key}_T{t}_north.png')
  base.resize((256,288),Image.Resampling.LANCZOS).save(worn/f'TC_{key}_T{t}_east.png')
 for slot in fam['slots']:
  for i in range(5):overlay_image(key,slot,i).save(out/f'P{slot["id"]:02}_V{i}.png')
 for i,s in enumerate(data['specials']):special_image(s['region'],i).save(out/f'S{i:02}.png')
# Nine chassis at uniform scale for comparison
sheet=Image.new('RGB',(1650,1630),(13,26,36));d=ImageDraw.Draw(sheet)
try: font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',24)
except OSError:font=ImageFont.load_default()
for fi,fam in enumerate(data['families']):
 for ti,ch in enumerate(fam['chassis']):
  base=chassis_image(fam['key'],ti+1).resize((370,420),Image.Resampling.LANCZOS)
  x=50+ti*540;y=50+fi*520
  sheet.paste(base,(x,y),base)
  d.text((x+45,y+425),ch['label'],fill=(175,228,221),font=font)
  d.text((x+45,y+463),f'Sharp {ch["sharp"]} / Blunt {ch["blunt"]} / {ch["mass"]}kg',fill=(145,172,175),font=font)
sheet.save(show/'THORN_CORPS_9_CHASSIS_0.7.png')
print('Armor art generated',sum(1 for _ in previewRoot.rglob('*.png')),'module layers + chassis')
