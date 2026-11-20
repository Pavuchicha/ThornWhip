#!/usr/bin/env python3
"""Audit internal references and known bypasses; compile and real CE must still be tested."""
from pathlib import Path
import re
from xml.etree import ElementTree as ET
root=Path(__file__).resolve().parent
mod=root/'ThornWhip';defs=mod/'Defs';source=mod/'Source';textures=mod/'Textures'
errors=[]
xml={}
for path in sorted(defs.glob('*.xml')):
    try: xml[path.name]=ET.parse(path).getroot()
    except ET.ParseError as e: errors.append(f'XML syntax {path.name}: {e}')
assert len(xml)>=15, f'Missing definition files: {len(xml)}'
all_defs={}
for fn,doc in xml.items():
    for defnode in doc:
        name=defnode.findtext('defName')
        if not name: continue
        if name in all_defs: errors.append(f'duplicate defName {name}: {all_defs[name]} vs {fn}')
        all_defs[name]=fn
for fn,doc in xml.items():
    for item in doc.iter():
        if item.text is None:continue
        value=item.text.strip()
        if value.startswith(('TC_','TT_')) and re.fullmatch(r'[A-Za-z0-9_]+',value):
            if value not in all_defs:
                # Custom pawn/apparel tags are intentional categorical labels, not Def refs.
                if item.tag not in ('li', 'label', 'description', 'jobString') and not item.tag.startswith('TC_'):
                    errors.append(f'undefined custom Def {fn}: <{item.tag}>{value}</{item.tag}>')
        if item.tag.startswith(('TC_','TT_')) and item.tag not in all_defs:
            # A product tag is a def name, not a new XML symbol.
            errors.append(f'undefined XML product {fn}: {item.tag}')
# Materialize texture refs from XML; root may be regular or multi-dir
for fn,doc in xml.items():
    for d in doc:
        g=d.find('./graphicData')
        if g is None: continue
        tex=g.findtext('texPath');gc=g.findtext('graphicClass')
        if not tex:continue
        if gc=='Graphic_Multi':
            for direction in ('north','south','east','west'):
                if not (textures/(tex+'_'+direction+'.png')).is_file():errors.append(f'{fn}: missing multi PNG {tex}_{direction}')
        elif not (textures/(tex+'.png')).is_file(): errors.append(f'{fn}: missing PNG {tex}')
# Custom source classes referenced by XML actually exist.
all_cs='\n'.join(x.read_text(encoding='utf-8') for x in sorted(source.glob('*.cs')))
classes=set(re.findall(r'\bclass\s+([A-Za-z_][A-Za-z0-9_]*)',all_cs))
for fn,doc in xml.items():
    for elt in doc.iter():
        c=elt.get('Class')
        if c and c.startswith('ThornWhip.') and c.split('.')[-1] not in classes:
            errors.append(f'{fn}: XML references missing C# class {c}')
        if elt.tag in ('driverClass','giverClass','thingClass') and elt.text and elt.text.strip().startswith('ThornWhip.'):
            cl=elt.text.strip().split('.')[-1]
            if cl not in classes:errors.append(f'{fn}: references missing C# class {cl}')
# Critical known RimWorld 1.7 compile issues & free crafted-item exploit
for filename in ('ThornMoats.cs','TurretRetrofits.cs'):
    if 'override void PostDeSpawn(' in (source/filename).read_text():errors.append(f'{filename} invalid 1.7 PostDeSpawn override')
if 'next.def.building' in (source/'TurretRetrofits.cs').read_text():errors.append('TurretRetrofits ThingDef.next.def compile error')
if 't.verbs!=null' in (source/'ThornFortresses.cs').read_text():errors.append('ThornFortresses ThingDef.verbs compile error')
event=(source/'Events.cs').read_text()
if 'Blocked weapon crafting without a valid paid blueprint' not in event or 'Blocked armor crafting without a valid paid blueprint' not in event:
    errors.append('vanilla bill permits free modular weapon/armor manufacture')
assert not errors,'\n'.join(errors[:70])+'\n(total '+str(len(errors))+')'
print('PASS integrity: '+str(len(xml))+' Def files / '+str(len(all_defs))+' defNames; no internal duplicate/undefined references')
print('PASS integrity: all XML graphic paths and custom ThingComp/JobDriver C# references')
print('PASS integrity: known 1.7 compile typos, prohibited PostDeSpawn overrides and zero-ingredient billing bypass')
print('NOT VERIFIED: actual Combat Extended Def names, game runtime, energy/missile mechanics, Odyssey orbital generation, TPS')
