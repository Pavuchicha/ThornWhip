#!/usr/bin/env python3
"""Reproducible game texture pass for Thorn Corps 1.0.
Source images bundled in Showcase/Input_1_0. Rebuilds real texture assets, style palettes,
rotation sprites, and Ideology style defs; does not claim to compile or test CE.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageEnhance
from xml.etree import ElementTree as ET
import math, random, re, shutil

ROOT=Path(__file__).parent
MOD=ROOT/'ThornWhip'
TEX=MOD/'Textures'
INPUT=ROOT/'Showcase'/'Input_1_0'
TRANSPARENT=(0,0,0,0)

STYLES={
 'Corps': {'dark':(32,33,38),'top':(67,70,77),'edge':(116,121,129),'red':(166,39,47),'redlight':(244,74,75),'deep':(12,14,18),'steel':(95,102,112)},
 'Order': {'dark':(93,92,94),'top':(216,214,209),'edge':(243,242,236),'red':(165,39,44),'redlight':(251,80,80),'deep':(36,34,38),'steel':(177,179,181)},
}

def save(im, p):
 p.parent.mkdir(parents=True,exist_ok=True)
 im.save(p, compress_level=1)

def remap(img, style, strength=1):
    """Vectorized embossed paint: old masks keep exactly their original placement."""
    import numpy as np
    s=STYLES[style]
    o=img.convert('RGBA')
    arr=np.asarray(o).copy()
    rgb=arr[:,:,:3].astype(np.float32)
    alpha=arr[:,:,3]
    gray=(rgb[:,:,0]*.30+rgb[:,:,1]*.59+rgb[:,:,2]*.11)/255.
    accent=((rgb[:,:,2]>rgb[:,:,0]*1.20)&(rgb[:,:,1]>rgb[:,:,0]*1.12)&((rgb[:,:,1]+rgb[:,:,2])>145))|((rgb[:,:,0]>rgb[:,:,1]*1.35)&(rgb[:,:,0]>rgb[:,:,2]*1.25)&(rgb[:,:,0]>90))
    t=np.clip((gray-.1)*1.3,0,1)
    lo=np.array(s['dark'],dtype=np.float32);hi=np.array(s['top'],dtype=np.float32)
    neutral=lo[None,None,:]*(1-t[:,:,None])+hi[None,None,:]*t[:,:,None]
    light=np.array(s['redlight'],dtype=np.float32);red=np.array(s['red'],dtype=np.float32)
    accents=np.where((gray>.62)[:,:,None],light,red)
    arr[:,:,:3]=np.where(accent[:,:,None],accents,neutral).astype('uint8')
    arr[alpha<4,:3]=0
    base=Image.fromarray(arr,'RGBA')
    # Subpixel top-edge highlights, bottom-edge black shading.
    if max(o.size)>50:
        a=o.getchannel('A');sx=ImageChops.offset(a,-1,-1);sy=ImageChops.offset(a,1,1)
        top=ImageChops.subtract(a,sx).point(lambda v:int(v*.32))
        bottom=ImageChops.subtract(a,sy).point(lambda v:int(v*.38))
        shine=Image.new('RGBA',o.size,s['edge']+(0,));shine.putalpha(top)
        dark=Image.new('RGBA',o.size,s['deep']+(0,));dark.putalpha(bottom)
        base=Image.alpha_composite(Image.alpha_composite(base,shine),dark)
    return base

def poly(d, pts, fill, outline=(13,14,17),width=3):
 d.polygon(pts,fill=fill)
 if outline:d.line(pts+[pts[0]],fill=outline,width=width,joint='curve')

def led(d,x,y,w,h,s):
 d.rounded_rectangle((x,y,x+w,y+h),radius=max(1,h//3),fill=s['deep'])
 d.rounded_rectangle((x+2,y+2,x+w-2,y+h-2),radius=max(1,h//4),fill=s['redlight'])

def rivet(d,x,y,s,r=3):
 d.ellipse((x-r,y-r,x+r,y+r),fill=s['deep'],outline=s['edge'],width=1)
 d.line((x-r//2,y,x+r//2,y),fill=s['steel'],width=1)

def armor(style,typ,tier,size=(256,288),facing='south'):
 s=STYLES[style];K=3
 img=Image.new('RGBA',(256*K,288*K));d=ImageDraw.Draw(img)
 b=s['dark'];p=s['top'];edge=s['edge'];red=s['red'];deep=s['deep'];steel=s['steel']
 # Draw design at 256x288 then supersample; geometry coordinates multiplied by K via function.
 def P(v):return [(int(x*K),int(y*K)) for x,y in v]
 def Q(box):return tuple(int(v*K) for v in box)
 def shape(points,fill,outline=deep,w=3): poly(d,P(points),fill,outline,int(w*K))
 def rect(box,fill,outline=deep,w=3,r=0):
  if r:d.rounded_rectangle(Q(box),int(r*K),fill,outline,width=int(w*K))
  else:d.rectangle(Q(box),fill,outline,width=int(w*K))
 def light(box):
  d.rounded_rectangle(Q(box),radius=int(3*K),fill=s['redlight'],outline=deep,width=2*K)
 def bolt(x,y):rivet(d,int(x*K),int(y*K),s,2*K)
 # On chest-forward view, layered suit anatomy with actual body part silhouette difference.
 if typ=='Light':
  shape([(86,66),(109,55),(151,55),(171,66),(187,114),(173,183),(83,183),(69,116)],deep)
  shape([(86,69),(109,61),(151,61),(172,72),(178,113),(168,168),(88,168),(78,115)],b)
  shape([(101,77),(154,77),(170,116),(156,148),(97,148),(84,116)],p)
  rect((98,150,156,181),b,deep,r=4)
  for x in [103,132,157]:bolt(x,154)
  rect((82,101,89,154),red,deep,r=2)
  rect((168,101,175,154),red,deep,r=2)
  rect((109,87,147,95),steel,deep,r=2)
  if tier>=2:
   rect((115,100,142,117),red,deep,r=4);light((122,104,137,108))
  if tier==3:
   rect((103,156,151,169),steel,deep,r=4);light((114,160,142,164))
 else:
  h=typ=='Heavy'
  shoulder=29 if h else 42
  armend=198 if h else 181
  shape([(80,57),(101,50),(155,50),(178,57),(201,77),(214,154),(196,195),(176,194),(172,171),(160,184),(94,184),(79,169),(74,195),(55,196),(41,145),(47,84)],deep)
  # legs two distinct boots, no body painter shortcuts
  shape([(87,170),(123,172),(126,253),(113,271),(79,270),(73,252)],deep)
  shape([(132,172),(171,170),(182,251),(172,270),(140,270),(129,253)],deep)
  shape([(88,175),(119,176),(122,248),(111,260),(83,261),(80,248)],b)
  shape([(136,176),(166,174),(173,248),(164,260),(141,261),(135,249)],b)
  for x in [92,145]:
   rect((x,205,x+22,221),p,deep,r=3)
   rect((x,235,x+23,248),red if tier>=2 else steel,deep,r=2)
   bolt(x+4,213);bolt(x+17,213)
  shape([(62,81),(86,68),(96,90),(89,159),(75,185),(52,178),(45,148)],p if h else b)
  shape([(172,89),(186,68),(202,81),(213,148),(203,178),(178,183),(167,160)],p if h else b)
  shape([(75,61),(104,52),(152,52),(181,61),(183,125),(166,185),(91,185),(74,124)],b)
  shape([(95,72),(160,72),(171,108),(163,164),(92,164),(84,108)],p)
  shape([(103,79),(153,79),(160,113),(151,136),(105,136),(96,113)],red)
  shape([(106,143),(151,143),(160,160),(149,175),(106,175),(96,160)],p)
  rect((108,152,149,158),deep,deep,r=2);light((115,153,142,158))
  # helmet distinct faceplate & back panel; tiered tech.
  shape([(105,21),(151,21),(164,36),(166,66),(156,84),(103,84),(91,67),(92,40)],deep)
  shape([(108,25),(149,25),(158,40),(157,63),(150,74),(106,74),(100,62),(100,39)],p if tier>1 else b)
  rect((106,47,151,62),deep,deep,r=5)
  light((113,52,144,57))
  if h:
   shape([(53,77),(67,64),(92,69),(90,111),(65,128),(43,115)],red)
   shape([(164,69),(188,65),(205,77),(215,115),(194,129),(166,112)],red)
   rect((84,177,104,195),steel,deep,r=4);rect((152,177,172,195),steel,deep,r=4)
   for x in [57,194]:bolt(x,101)
  else:
   rect((64,91,79,116),red,deep,r=3);rect((177,91,192,116),red,deep,r=3)
  if tier==3:
   light((111,83,147,91));light((105,169,150,174))
 # Faint top-edge facing relief for RimWorld slight angled view.
 if facing=='north':
  # Show technical backpack instead of face visor: opaque top plate and harness.
  rect((109,49,146,68),b,deep,r=3)
  for i in range(4):rect((111,50+i*4,145,51+i*4),steel,None,1)
  rect((103,94,154,120),b,deep,r=6)
  light((116,101,143,108))
 elif facing in ('east','west'):
  # side directional offsets: 3/4 armor appears narrower, still on correct body.
  pass
 if facing=='west':img=img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
 if facing=='east':img=img.transform(img.size, Image.Transform.AFFINE,(1,0,-9*K,0,1,0),fillcolor=TRANSPARENT)
 if facing=='west':img=img.transform(img.size, Image.Transform.AFFINE,(1,0,9*K,0,1,0),fillcolor=TRANSPARENT)
 return img.resize(size,Image.Resampling.LANCZOS)

def weapon_fallback(family,style):
 # Should be used only for pistol and launcher when no authored isolated source exists.
 s=STYLES[style]
 im=Image.new('RGBA',(1024,320));d=ImageDraw.Draw(im)
 if family=='Pistol':
  poly(d,[(350,143),(702,143),(745,160),(727,190),(451,189),(420,196),(430,231),(474,277),(403,286),(368,204),(344,199)],s['dark'],s['deep'],6)
  poly(d,[(369,128),(724,128),(731,151),(363,154)],s['top'],s['deep'],5)
  poly(d,[(435,157),(596,157),(599,193),(446,193)],s['red'],s['deep'],5)
  poly(d,[(410,186),(484,186),(494,275),(425,276)],s['top'],s['deep'],5)
  led(d,490,137,69,11,s)
  for x in [392,430,620,691]:rivet(d,x,141,s,4)
 elif family=='Launcher':
  poly(d,[(120,156),(230,138),(325,140),(357,176),(283,208),(132,205)],s['dark'],s['deep'],6)
  poly(d,[(290,136),(883,114),(912,148),(891,197),(319,202)],s['top'],s['deep'],6)
  d.rounded_rectangle((413,136,830,177),radius=19,fill=s['dark'],outline=s['deep'],width=6)
  d.rounded_rectangle((780,126,929,187),radius=20,fill=s['red'],outline=s['deep'],width=6)
  poly(d,[(364,185),(460,186),(467,283),(397,285)],s['dark'],s['deep'],6)
  led(d,510,139,126,11,s)
  for x in [456,537,626,705,852]:rivet(d,x,157,s,4)
 return im

def composite_gun_source(family,style):
 sources={
 'Rifle':INPUT/'rifle_original.png',
 'Auto':INPUT/'auto_original.png'
 }
 if family not in sources: return weapon_fallback(family,style)
 src=Image.open(sources[family]).convert('RGBA')
 # Crop actual alpha rather than imagegen transparent canvas with fringe pixels.
 alpha=src.getchannel('A').point(lambda a:255 if a>72 else 0)
 b=alpha.getbbox()
 crop=src.crop(b)
 # Resize with consistent full-canvas world alignment; subtle tilt already on source.
 nw=974 if family=='Rifle' else 898;nh=304 if family=='Rifle' else 292
 crop=crop.resize((nw,nh),Image.Resampling.LANCZOS)
 out=Image.new('RGBA',(1024,320));out.alpha_composite(crop,((1024-nw)//2,(320-nh)//2))
 # Remap grayscale family appearance using palette with preserve red, relief, metallic details.
 if style=='Corps':return out
 # White panels: mask original medium grey, keep black outlines/red accents.
 import numpy as np
 A=np.array(out)
 RGB=A[:,:,:3].astype('int16')
 val=(RGB[:,:,0]+RGB[:,:,1]+RGB[:,:,2])/3
 red=(RGB[:,:,0]>RGB[:,:,1]*1.24)&(RGB[:,:,0]>RGB[:,:,2]*1.19)&(RGB[:,:,0]>65)
 neutral=(val>65)&(~red)&(A[:,:,3]>30)
 # map neutral dark metal -> ivory with shading and preserve deep outlines
 v=np.clip((val-55)/160,0,1)
 for i in range(3):
  target=STYLES['Order']['dark'][i]*(1-v)+STYLES['Order']['top'][i]*v
  RGB[:,:,i]=np.where(neutral,target,RGB[:,:,i])
 A[:,:,:3]=np.clip(RGB,0,255).astype('uint8')
 return Image.fromarray(A,'RGBA')

def part_image(source,style,family,index,variant):
 """Retain precisely authored full-canvas silhouettes/hitbox positions and repaint/rivet."""
 orig=Image.open(source).convert('RGBA').resize((512,160),Image.Resampling.LANCZOS)
 out=remap(orig,style)
 a=out.getchannel('A')
 box=a.point(lambda v:255 if v>100 else 0).getbbox()
 if not box:return out
 x0,y0,x1,y1=box
 d=ImageDraw.Draw(out)
 s=STYLES[style]
 if x1-x0>15 and y1-y0>8:
  # low-cost industrial bolt accents on larger module footprint
  rr=max(2,min(4,(y1-y0)//14))
  for x in [x0+9,x1-10]:
   for y in [y0+max(8,rr+2),y1-max(8,rr+2)]:
    if x0<x<x1 and y0<y<y1:rivet(d,x,y,s,rr)
  if variant>=2 and x1-x0>85:
   led(d,int(x0+(x1-x0)*.4),int(y0+(y1-y0)*.41),min(32,(x1-x0)//5),max(5,(y1-y0)//8),s)
 out.putalpha(out.getchannel('A').point(lambda v: int(v*0.57)))
 return out

def rot_variants(im,path):
 save(im,path.with_suffix('.png'))
 for direction,deg in [('north',0),('east',-90),('south',180),('west',90)]:
  res=im.rotate(deg,Image.Resampling.BICUBIC,expand=False)
  save(res,path.parent/(path.name+'_'+direction+'.png'))

def turret_assets():
 sheet=Image.open(INPUT/'turrets_atlas.png').convert('RGBA')
 # The 4x2 source has square cells; no output should include a neighboring cell.
 cw=sheet.width//4;ch=sheet.height//2
 mapping={'Holder':0,'Minigun':1,'Laser':2,'Blaster':3,'Railgun':4,'ATGM':5,'MLRS':6}
 defs=list((MOD/'Defs'/'TC_Turrets.xml').read_text().splitlines())
 target_paths=[]
 root=ET.parse(MOD/'Defs'/'TC_Turrets.xml').getroot()
 for t in root.findall('ThingDef'):
  p=t.findtext('graphicData/texPath')
  if p: target_paths.append(p)
 for p in target_paths:
  name=Path(p).name
  mm=re.match(r'Turret_([^_]+)',name)
  if not mm: continue
  kind=mm.group(1)
  i=mapping.get(kind)
  if i is None:continue
  col=i%4;row=i//4
  tile=sheet.crop((col*cw,row*ch,(col+1)*cw,(row+1)*ch))
  # identify alpha bbox and crop small margin to preserve cannon nose
  a=tile.getchannel('A');bb=a.point(lambda v:255 if v>35 else 0).getbbox()
  if not bb:continue
  tile=tile.crop(bb)
  side=256 if kind not in ('Railgun','MLRS') else 320
  scale=min((side-12)/tile.width,(side-12)/tile.height)
  tile=tile.resize((round(tile.width*scale),round(tile.height*scale)),Image.Resampling.LANCZOS)
  art=Image.new('RGBA',(side,side));art.alpha_composite(tile,((side-tile.width)//2,(side-tile.height)//2))
  # Variant mods: tiny physical sensors / barrels, not only filename clone.
  vhash=sum(ord(c) for c in name)
  if name not in ('Turret_'+kind,):
   d=ImageDraw.Draw(art);s=STYLES['Corps'];x=side//2
   if 'Heavy' in name or '762' in name:d.rounded_rectangle((x-40,side-72,x+40,side-64),fill=s['red'],outline=s['deep'],width=2)
   elif 'Dual' in name or '56x6' in name:d.ellipse((x+26,side//2-70,x+39,side//2-57),fill=s['redlight'],outline=s['deep'])
   elif 'Cooling' in name:d.line((x-16,50,x+16,50),fill=s['redlight'],width=4)
   else:rivet(d,x+40,side//2+18,s,3)
  rot_variants(art,TEX/p)
  # Both color schemes: not altering crimson armor plates / sensors.
  white=remap_turret_order(art)
  rot_variants(white,TEX/('ThornCorps/StyleOrder/'+p))

def remap_turret_order(img):
 from PIL import Image
 import numpy as np
 A=np.array(img.convert('RGBA'))
 x=A[:,:,:3].astype('int16');avg=x.mean(axis=2)
 # paint neutral plate cores ivory, keep deep mechanics and crimson armor untouched
 red=(x[:,:,0]>x[:,:,1]*1.18)&(x[:,:,0]>x[:,:,2]*1.18)&(x[:,:,0]>42)
 mask=(avg>40)&(~red)&(A[:,:,3]>10)
 v=np.clip((avg-36)/72,0,1)
 for z in range(3):
  target=(162,159,155)[z]+v*((247,244,238)[z]-(162,159,155)[z])
  A[:,:,z]=np.where(mask,np.clip(target,0,255),A[:,:,z])
 return Image.fromarray(A,'RGBA')

def make_guns():
 base_dir=INPUT/'LegacyParts'
 choices=['Rifle','Auto','Pistol','Launcher']
 for family in choices:
  for style in STYLES:
   base=composite_gun_source(family,style)
   target=TEX/('ThornWhip/Parts/'+family if style=='Corps' else 'ThornCorps/StyleOrder/ThornWhip/Parts/'+family)
   save(base,target/'Chassis.png')
   layers={}
   for slot in range(15):
    for variant in range(5):
     key='P%02d_V%d'%(slot,variant)
     source=base_dir/family/(key+'.png')
     if source.exists():
      im=part_image(source,style,family,slot,variant)
      save(im,target/(key+'.png'))
      layers[key]=im
   for extra in range(15):
    key='S%02d'%extra
    source=base_dir/family/(key+'.png')
    if source.exists():save(part_image(source,style,family,extra,2),target/(key+'.png'))
   # Build all 8 technical base variants using composed variants of physically different parts
   if style=='Corps':out_dir=TEX/'Things'/'Weapons'
   else:out_dir=TEX/'ThornCorps'/'StyleOrder'/'Things'/'Weapons'
   for r in (0,1):
    for b in (0,1):
     for m in (0,1):
      out=base.copy()
      for key in ['P00_V%d'%r,'P02_V%d'%b,'P09_V%d'%m]:
       im=layers.get(key)
       if im:out.alpha_composite(im.resize(out.size,Image.Resampling.LANCZOS))
      save(out,out_dir/(f'TW_{family}_R{r}B{b}M{m}.png'))

# Armor icon + directional graphics: individual armoring designs 3 classes x 3 tiers.
def make_armor():
 for typ in ['Light','Medium','Heavy']:
  for tier in (1,2,3):
   for style in STYLES:
    icon=armor(style,typ,tier)
    bname=f'TC_{typ}_T{tier}'
    if style=='Corps':iconp=TEX/'Things'/'Armor'/f'{bname}.png';worn=TEX/'Things'/'Armor'/'Worn';layer=TEX/'ThornCorps'/'Armor'/typ
    else:iconp=TEX/'ThornCorps'/'StyleOrder'/'Things'/'Armor'/f'{bname}.png';worn=TEX/'ThornCorps'/'StyleOrder'/'Things'/'Armor'/'Worn';layer=TEX/'ThornCorps'/'StyleOrder'/'ThornCorps'/'Armor'/typ
    save(icon,iconp)
    for facing in ['north','south','east','west']:
     save(armor(style,typ,tier,facing=facing),worn/f'{bname}_{facing}.png')
    # Designer chassis 640x720 matches existing module canvas.
    save(icon,layer/f'Chassis_T{tier}.png')
    for x in range({'Light':10,'Medium':13,'Heavy':14}[typ]):
     for v in range(5):
      ref=INPUT/'LegacyArmor'/typ/f'P{x:02d}_V{v}.png'
      if ref.exists():
       out=remap(Image.open(ref).resize((256,288),Image.Resampling.LANCZOS),style)
       save(out,layer/f'P{x:02d}_V{v}.png')
    for x in range(15):
     ref=INPUT/'LegacyArmor'/typ/f'S{x:02d}.png'
     if ref.exists():save(remap(Image.open(ref).resize((256,288),Image.Resampling.LANCZOS),style),layer/f'S{x:02d}.png')

# Fortifications + benches: richly shaded plan-view tiles and mechanical structures.
def add_steel_detail(im,style,name):
 s=STYLES[style];art=remap(im,style);d=ImageDraw.Draw(art)
 W,H=art.size
 key=name.lower()
 if 'trench' in key or 'foxhole' in key:
  # Earth trench keeps brown earth even in military color palettes; metallic side braces get paint.
  orig=im.convert('RGBA')
  a=orig.getchannel('A'); bbox=a.getbbox()
  if bbox:
   x0,y0,x1,y1=bbox
   d.rectangle((x0+W*.21,y0+H*.18,x1-W*.21,y1-H*.18),fill=(68,52,41,245),outline=s['steel'],width=max(2,W//55))
   if 'trench_3' in key:
    d.rectangle((x0+W*.29,y0+H*.24,x1-W*.29,y1-H*.24),fill=(25,77,84,255),outline=s['edge'],width=2)
   for y in range(int(y0+H*.19),int(y1-H*.20),max(12,H//8)):
    d.line((x0+W*.17,y,x0+W*.26,y),fill=s['edge'],width=3)
    d.line((x1-W*.26,y,x1-W*.17,y),fill=s['edge'],width=3)
  return art
 if 'wall' in key or 'embrasure' in key or 'bunker' in key or 'gate' in key:
  d.line((W*.15,H*.17,W*.81,H*.17),fill=s['edge'],width=max(2,W//64))
  d.line((W*.14,H*.80,W*.82,H*.80),fill=s['deep'],width=max(2,W//64))
  for x in [W*.19,W*.82]:
   for y in [H*.19,H*.82]:rivet(d,int(x),int(y),s,max(2,W//84))
  if 'embrasure' in key:
   d.rounded_rectangle((W*.25,H*.43,W*.75,H*.55),radius=3,fill=s['deep'],outline=s['red'],width=max(2,W//60))
  if 'gate' in key:
   for x in [W*.25,W*.5,W*.75]:d.line((x,H*.32,x,H*.66),fill=s['edge'],width=4)
  led(d,int(W*.43),int(H*.2),max(12,W//7),max(5,H//30),s)
 elif 'sandbag' in key:
  for y in [H*.33,H*.52,H*.71]:
   d.line((W*.15,y,W*.85,y),fill=s['edge'],width=max(2,H//35))
 elif 'table' in key:
  d.rounded_rectangle((W*.34,H*.18,W*.74,H*.51),radius=12,fill=s['deep'],outline=s['edge'],width=5)
  for j in range(6):d.line((W*.4+j*W*.05,H*.28,W*.4+j*W*.05,H*.42),fill=s['red'],width=3)
 return art

def make_defense_items():
 for p in list((TEX/'ThornCorps'/'Defense').glob('*.png')):
  if p.stem.endswith(('_north','_south','_east','_west')):continue
  if p.stem.startswith('Turret_'):continue
  orig=Image.open(INPUT/'LegacyDefense'/p.name)
  for style in STYLES:
   art=add_steel_detail(orig,style,p.stem)
   target=(p if style=='Corps' else TEX/'ThornCorps'/'StyleOrder'/'ThornCorps'/'Defense'/p.name)
   if p.stem.startswith(('Fort_','Trench_')):rot_variants(art,target.with_suffix(''))
   else:save(art,target)
 for p in (TEX/'Things'/'Buildings').glob('*.png'):
  orig=Image.open(INPUT/'LegacyBuildings'/p.name)
  for style in STYLES:
   t=add_steel_detail(orig,style,p.stem)
   target=p if style=='Corps' else TEX/'ThornCorps'/'StyleOrder'/'Things'/'Buildings'/p.name
   rot_variants(t,target.with_suffix(''))

# Native Ideology choices; keeps style choice in game defs, no global forced recolor.
def make_style_defs():
 catalogs=[]
 for f in (MOD/'Defs').glob('*.xml'):
  try:root=ET.parse(f).getroot()
  except Exception:continue
  for td in root.findall('ThingDef'):
   name=td.findtext('defName');gd=td.find('graphicData')
   tex=td.findtext('graphicData/texPath')
   if not name or not tex:continue
   if not (name.startswith(('TC_Turret_','TC_Fort_','TC_Trench_','TC_Armor_','TT_'))):continue
   if tex.startswith(('Things/Weapons/TW_','Things/Armor/TC_','Things/Buildings/TW_','ThornCorps/Defense/')):
    # Need the item base texture to exist for both colorways.
    if not (TEX/(tex+'.png')).exists():continue
    if not (TEX/('ThornCorps/StyleOrder/'+tex+'.png')).exists():continue
    gc=td.findtext('graphicData/graphicClass') or 'Graphic_Single'
    ds=td.findtext('graphicData/drawSize')
    catalogs.append((name,tex,gc,ds,td.findtext('apparel/wornGraphicPath')))
 # A category maps a defName to style. Avoid replacing core styles.
 out=ET.Element('Defs')
 for style in ('Corps','Order'):
  cat=ET.SubElement(out,'StyleCategoryDef',{'MayRequire':'Ludeon.RimWorld.Ideology'})
  ET.SubElement(cat,'defName').text='TC_Style'+style
  ET.SubElement(cat,'label').text='Корпус Терна' if style=='Corps' else 'Орден Терна'
  ET.SubElement(cat,'description').text=('Чёрные броневые панели, красная индустриальная разметка.' if style=='Corps' else 'Белые броневые панели, красная церемониальная разметка.')
  tds=ET.SubElement(cat,'thingDefStyles')
  for name,tex,gc,ds,worn in catalogs:
   sid=f'TC_{style}_{name}'
   node=ET.SubElement(tds,'li');ET.SubElement(node,'thingDef').text=name;ET.SubElement(node,'styleDef').text=sid
   elem=ET.SubElement(out,'ThingStyleDef',{'MayRequire':'Ludeon.RimWorld.Ideology'})
   ET.SubElement(elem,'defName').text=sid
   gd=ET.SubElement(elem,'graphicData')
   pp=tex if style=='Corps' else 'ThornCorps/StyleOrder/'+tex
   ET.SubElement(gd,'texPath').text=pp
   ET.SubElement(gd,'graphicClass').text=gc
   if ds: ET.SubElement(gd,'drawSize').text=ds
   if worn:
    ET.SubElement(elem,'wornGraphicPath').text=worn if style=='Corps' else 'ThornCorps/StyleOrder/'+worn
 new=MOD/'Defs'/'TC_IdeologyStyles.xml'
 ET.indent(out,space='  ')
 ET.ElementTree(out).write(new,encoding='utf-8',xml_declaration=True)
 return len(catalogs)

def change_rotation_defs():
 # Texture basis four directions. Graphic_Multi needs directional PNGs.
 for xml in ['TC_Fortifications.xml','TC_Turrets.xml','TT_Benches.xml']:
  p=MOD/'Defs'/xml
  root=ET.parse(p).getroot()
  changed=0
  for e in root.findall('ThingDef'):
   path=e.findtext('graphicData/texPath')
   if path and ((TEX/(path+'_south.png')).exists()):
    gd=e.find('graphicData');gr=gd.find('graphicClass')
    if gr is None:gr=ET.SubElement(gd,'graphicClass')
    gr.text='Graphic_Multi'
    rotate=e.find('rotatable')
    if rotate is None:rotate=ET.SubElement(e,'rotatable')
    rotate.text='true'
    changed+=1
  ET.indent(root,space='  ')
  ET.ElementTree(root).write(p,encoding='utf-8',xml_declaration=True)
  print('ROTATE',xml,changed)

def enable_styleable_comps():
    """Apply built-in style system only to own actual equipment and placeable buildings."""
    changed=0
    for p in (MOD/'Defs').glob('*.xml'):
        if p.name=='TC_IdeologyStyles.xml':continue
        rt=ET.parse(p).getroot()
        modified=False
        for td in rt.findall('ThingDef'):
            name=td.findtext('defName')
            if not name or not name.startswith(('TC_Turret_','TC_Fort_','TC_Trench_','TC_Armor_','TT_')):continue
            tp=td.findtext('graphicData/texPath')
            if not tp or not tp.startswith(('Things/Weapons/TW_','Things/Armor/TC_','Things/Buildings/TW_','ThornCorps/Defense/')):continue
            # Avoid adding the special comp to gun and projectile defs.
            if '/Projectile_' in tp or '/Ammo_' in tp:continue
            cp=td.find('comps')
            if cp is None: cp=ET.SubElement(td,'comps')
            if any(c.attrib.get('Class')=='CompProperties_Styleable' for c in cp.findall('li')):continue
            ET.SubElement(cp,'li',{'Class':'CompProperties_Styleable'})
            modified=True;changed+=1
        if modified:
            ET.indent(rt,space='  ')
            ET.ElementTree(rt).write(p,encoding='utf-8',xml_declaration=True)
    print('Styles enabled for',changed,'concrete ThingDefs')

def audit():
 import glob
 from collections import Counter
 refs=[];bad=[]
 for p in (MOD/'Defs').glob('*.xml'):
  r=ET.parse(p).getroot()
  for e in r.iter():
   if e.tag=='texPath' and e.text:
    # Base and style references, skip paths not owned by our mod.
    path=e.text
    if path.startswith(('ThornWhip/','ThornCorps/','Things/Armor/TC_','Things/Weapons/TW_','Things/Buildings/TW_')):
     if not (TEX/(path+'.png')).exists() and not (TEX/(path+'_north.png')).exists():bad.append((str(p.name),path))
     else:refs.append(path)
 if bad:print('MISSING',bad[:20]);raise RuntimeError(str(len(bad))+' referenced sprites missing')
 print('XML paths verified:',len(set(refs)),'PNG files',len(list(TEX.rglob('*.png'))))


def main():
 for f,n in [('a_clean_transparent_background_sprite_sheet_no_te.png','turrets_atlas.png'),('футуристическая_винтовка_торн.png','rifle_original.png'),('футуристическая_штурмовая_винтовка.png','auto_original.png')]:
  src=Path('/mnt/data')/f;dest=INPUT/n
  if not dest.exists():
   if not src.exists():raise FileNotFoundError('Missing bundled input asset: '+str(dest))
   dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
 print('1 Turrets...');turret_assets()
 print('2 Weapons...');make_guns()
 print('3 Armor...');make_armor()
 print('4 Fortifications...');make_defense_items()
 print('5 Graphic rotation defs...');change_rotation_defs()
 print('6 Enable built-in styles...');enable_styleable_comps()
 print('7 Ideology style defs...');print('style mappings per category',make_style_defs())
 print('8 Audit...');audit()
 print('DONE')

if __name__=='__main__':main()
