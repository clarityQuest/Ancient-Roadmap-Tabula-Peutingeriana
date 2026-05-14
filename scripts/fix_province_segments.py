#!/usr/bin/env python3
"""
Fix province/region/people tabula_segment values.

The SOURCE data from tabula-peutingeriana.de list uses 0-indexed segment
numbers (segm=0 = lost Segment I). Our DB uses tabula_segment where 1=lost,
2=first surviving. So: our tabula_segment = SOURCE_seg + 1.

enrich_segments.py mistakenly set tabula_segment = SOURCE_seg (without +1),
and fix_segments.py then overwrote multi-segment region extents using the
MAX rule. This script restores correct values.

Also:
- Merges 7 roman_province/region duplicate pairs
- Adds ULM 1887 (Magaris, city, planquadrat 11B5)
"""
import json, sys, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(BASE, "public", "data", "review_places_db.json")

with open(path, encoding='utf-8') as f:
    db = json.load(f)

# ── SOURCE: tabula-peutingeriana.de segment numbers (0-indexed, +1 = tabula_segment) ──
SOURCE = [
    # REGIONS / PROVINCES  (seg is tabula-peutingeriana.de segm parameter, 0-indexed)
    {'latin':'ACHAIA','seg':6,'row':'b','col':4},
    {'latin':'AFRICA','seg':4,'row':'c','col':3},
    {'latin':'ALAMANNIA','seg':2,'row':'a','col':4},
    {'latin':'ALBANIA','seg':11,'row':'b','col':1},
    {'latin':'APVLIA','seg':5,'row':'b','col':2},
    {'latin':'AQUITANIA','seg':1,'row':'b','col':5},
    {'latin':'ARABIA','seg':9,'row':'c','col':5},
    {'latin':'ARCADIA','seg':6,'row':'c','col':5},
    {'latin':'ARIACTA','seg':7,'row':'b','col':2},
    {'latin':'ASIA','seg':8,'row':'b','col':2},
    {'latin':'ATRAPATENE','seg':11,'row':'a','col':2},
    {'latin':'BABYLONIA','seg':10,'row':'c','col':4},
    {'latin':'BACTRIANOE','seg':11,'row':'a','col':4},
    {'latin':'BELGICA','seg':1,'row':'a','col':1},
    {'latin':'BITHINIA','seg':8,'row':'a','col':2},
    {'latin':'BRITTIVS','seg':6,'row':'b','col':1},
    {'latin':'BVLINIA','seg':5,'row':'a','col':2},
    {'latin':'CALABRIA','seg':5,'row':'b','col':2},  # label location
    {'latin':'CAMPI DESERTI','seg':11,'row':'b','col':1},
    {'latin':'CAPANIA','seg':5,'row':'b','col':1},
    {'latin':'CAPPADOCIA','seg':9,'row':'b','col':1},
    {'latin':'CARIA','seg':9,'row':'b','col':1},
    {'latin':'CASPIANE','seg':11,'row':'a','col':2},
    {'latin':'CASPYRE','seg':11,'row':'b','col':4},
    {'latin':'CERONESOS','seg':7,'row':'b','col':5},
    {'latin':'CILICIA','seg':9,'row':'b','col':3},
    {'latin':'CLENDERITIS','seg':9,'row':'b','col':3},
    {'latin':'COTII REGNVM','seg':2,'row':'b','col':3},
    {'latin':'DALMATIA','seg':5,'row':'a','col':2},
    {'latin':'DAMIRICE','seg':11,'row':'b','col':4},
    {'latin':'DESERTA','seg':10,'row':'c','col':3},
    {'latin':'DESERTVM','seg':10,'row':'c','col':3},
    {'latin':'DIA','seg':3,'row':'c','col':2},
    {'latin':'DIABENE','seg':11,'row':'a','col':2},
    {'latin':'DRANGIANE','seg':11,'row':'b','col':2},
    {'latin':'EGYPTVS','seg':8,'row':'c','col':3},
    {'latin':'AEGYPTUS','seg':8,'row':'c','col':3},
    {'latin':'ETRVRA','seg':4,'row':'b','col':1},
    {'latin':'ETRURIA','seg':4,'row':'b','col':1},
    {'latin':'FRANCIA','seg':1,'row':'a','col':4},
    {'latin':'GALATIA','seg':8,'row':'b','col':3},
    {'latin':'GALLIA COMATA','seg':1,'row':'b','col':3},
    {'latin':'HIBERIA','seg':11,'row':'b','col':1},
    {'latin':'IEPIRVM NOVVM','seg':6,'row':'b','col':3},
    {'latin':'EPIRUS','seg':6,'row':'b','col':3},
    {'latin':'INDIA','seg':11,'row':'b','col':2},
    {'latin':'ISTERIA','seg':4,'row':'a','col':1},
    {'latin':'HISTRIA','seg':4,'row':'a','col':1},
    {'latin':'ITALIA','seg':2,'row':'b','col':5},
    {'latin':'LACONICE','seg':6,'row':'b','col':5},
    {'latin':'LACONIA','seg':6,'row':'b','col':5},
    {'latin':'LIBVRNIA','seg':4,'row':'a','col':1},
    {'latin':'LIBURNIA','seg':4,'row':'a','col':1},
    {'latin':'LIGVRIA','seg':2,'row':'b','col':3},
    {'latin':'LIGURIA','seg':2,'row':'b','col':3},
    {'latin':'LVCCANIA','seg':5,'row':'b','col':5},
    {'latin':'LUCANIA','seg':5,'row':'b','col':5},
    {'latin':'LYCIA','seg':9,'row':'b','col':1},
    {'latin':'MACEDONIA','seg':6,'row':'a','col':3},
    {'latin':'MARDIANE','seg':11,'row':'a','col':1},
    {'latin':'MEDIA','seg':11,'row':'b','col':3},
    {'latin':'MEDIA MAIOR','seg':10,'row':'a','col':4},
    {'latin':'MESOPOTAMIA','seg':10,'row':'b','col':3},
    {'latin':'MOESIA INFERIOR','seg':6,'row':'a','col':2},
    {'latin':'MESIA INFERIOR','seg':6,'row':'a','col':2},
    {'latin':'MOESIA SUPERIOR','seg':5,'row':'a','col':5},
    {'latin':'MESIA SVPERIOR','seg':5,'row':'a','col':5},
    {'latin':'NORICUM','seg':4,'row':'a','col':1},
    {'latin':'NORICO','seg':4,'row':'a','col':1},
    {'latin':'PAFLAGONIA','seg':8,'row':'a','col':5},
    {'latin':'PAPHLAGONIA','seg':8,'row':'a','col':5},
    {'latin':'PALAESTINA','seg':9,'row':'c','col':2},
    {'latin':'PALESTINA','seg':9,'row':'c','col':2},
    {'latin':'PANNONIA INFERIOR','seg':5,'row':'a','col':2},
    {'latin':'PANNONIA SUPERIOR','seg':4,'row':'a','col':3},
    {'latin':'PANNONIA SVPERIOR','seg':4,'row':'a','col':3},
    {'latin':'PARRIA','seg':11,'row':'c','col':1},
    {'latin':'PATAVIA','seg':1,'row':'a','col':1},
    {'latin':'BATAVIA','seg':1,'row':'a','col':1},
    {'latin':'PERSIA','seg':10,'row':'b','col':5},
    {'latin':'PERSIDA','seg':10,'row':'b','col':5},
    {'latin':'SYRIA PHOENIX','seg':9,'row':'c','col':3},
    {'latin':'PHOENIX','seg':9,'row':'c','col':3},
    {'latin':'PHRYGIA','seg':8,'row':'b','col':3},
    {'latin':'PICENUM','seg':4,'row':'b','col':3},
    {'latin':'PICENVM','seg':4,'row':'b','col':3},
    {'latin':'PONTUS','seg':9,'row':'a','col':2},
    {'latin':'PONTVS POLEMONIACVS','seg':9,'row':'a','col':2},
    {'latin':'THRACIA','seg':7,'row':'b','col':2},
    {'latin':'TRHACIA','seg':7,'row':'b','col':2},
    {'latin':'ACHAEA','seg':6,'row':'b','col':4},
    {'latin':'SCYTHIA','seg':11,'row':'c','col':4},
    {'latin':'SCYTIA DYMIRICE','seg':11,'row':'c','col':4},
    # PEOPLES
    {'latin':'ALANI','seg':9,'row':'a','col':3},
    {'latin':'AMAZONES','seg':9,'row':'a','col':5},
    {'latin':'BAGIGETVLI','seg':7,'row':'c','col':2},
    {'latin':'BLASTARNI','seg':8,'row':'a','col':3},
    {'latin':'BOSFORANI','seg':9,'row':'a','col':1},
    {'latin':'BVR','seg':5,'row':'a','col':3},
    {'latin':'CHAMAVI','seg':2,'row':'a','col':1},
    {'latin':'CHACI','seg':2,'row':'a','col':1},
    {'latin':'COLCHI','seg':11,'row':'b','col':2},
    {'latin':'DACPETOPORIANI','seg':8,'row':'a','col':3},
    {'latin':'DAMASCENI','seg':10,'row':'c','col':2},
    {'latin':'DERBICCE','seg':12,'row':'a','col':2},
    {'latin':'ENIOCHI','seg':9,'row':'a','col':3},
    {'latin':'GAETE','seg':8,'row':'a','col':3},
    {'latin':'GAETVLIA','seg':3,'row':'c','col':5},
    {'latin':'GARAMANTES','seg':7,'row':'c','col':4},
    {'latin':'INSVBRES','seg':3,'row':'a','col':5},
    {'latin':'LAZI','seg':9,'row':'a','col':3},
    {'latin':'MARCOMANNI','seg':4,'row':'a','col':3},
    {'latin':'MEDIOMATRICI','seg':3,'row':'a','col':1},
    {'latin':'MEMNOCONES ETHIOPES','seg':8,'row':'c','col':2},
    {'latin':'NABABES','seg':2,'row':'c','col':2},
    {'latin':'PENASTII','seg':8,'row':'b','col':4},
    {'latin':'PENTAPOLITES','seg':8,'row':'c','col':4},
    {'latin':'PSACCANI','seg':9,'row':'a','col':2},
    {'latin':'QVADI','seg':4,'row':'a','col':5},
    {'latin':'QUADI','seg':4,'row':'a','col':5},
    {'latin':'ROXVLANI SARMATE','seg':8,'row':'a','col':5},
    {'latin':'SARMATE VAGI','seg':5,'row':'a','col':5},
    {'latin':'SARMATAE VAGI','seg':5,'row':'a','col':5},
    {'latin':'SALENTINI','seg':6,'row':'b','col':5},
    {'latin':'SYRTITES','seg':8,'row':'c','col':2},
    {'latin':'TREVERI','seg':3,'row':'a','col':1},
    {'latin':'VANDVLI','seg':4,'row':'a','col':3},
    {'latin':'VANDALI','seg':4,'row':'a','col':3},
    {'latin':'VENADI SARMATAE','seg':8,'row':'a','col':1},
    {'latin':'VENEDI','seg':8,'row':'a','col':4},
    {'latin':'VENETI','seg':2,'row':'a','col':2},
    {'latin':'AMAXOBII SARMATE','seg':7,'row':'a','col':2},
    {'latin':'LVPIONES SARMATE','seg':7,'row':'a','col':4},
    {'latin':'SASONE SARMATE','seg':10,'row':'a','col':5},
    {'latin':'SARMATE','seg':7,'row':'a','col':2},
]

def norm(s):
    s = (s or '').upper().strip()
    s = re.sub(r'^PROVINCIA\s+', '', s)
    s = re.sub(r'[^A-Z0-9 ]', '', s)
    return re.sub(r'\s+', ' ', s).strip()

# Build lookup: normalised latin → SOURCE entry
src_map = {}
for e in SOURCE:
    src_map[norm(e['latin'])] = e

TARGET_TYPES = {'roman_province', 'people', 'region', 'modern_state'}

# ── Part 1: Restore correct tabula_segment (SOURCE_seg + 1) ──────────────────
print('=== Part 1: Restore province/region/people segment values ===')
fixed = 0
for r in db['records']:
    if r.get('type') not in TARGET_TYPES:
        continue
    key = norm(r.get('latin_std') or r.get('latin') or '')
    match = src_map.get(key)
    if not match:
        for k, e in src_map.items():
            if k and key and (k in key or key in k) and len(min(k, key, key=len)) > 3:
                match = e
                break
    if not match:
        continue

    correct_seg = match['seg'] + 1   # SOURCE uses 0-indexed segm; our tabula_segment = segm+1
    correct_row = match['row']
    correct_col = match['col']

    old_seg = r.get('tabula_segment')
    if old_seg != correct_seg or r.get('tabula_row') != correct_row or r.get('tabula_col') != correct_col:
        print(f'  FIX  {r.get("latin","")[:40]:40} seg {old_seg}->{correct_seg} {correct_row}{correct_col}')
        r['tabula_segment'] = correct_seg
        r['tabula_row'] = correct_row
        r['tabula_col'] = correct_col
        r['grid_row'] = correct_row
        r['grid_col'] = correct_col
        r['tabula_location'] = f'Seg {correct_seg} {correct_row}{correct_col}'
        fixed += 1

print(f'\nFixed: {fixed} province/region/people entries\n')

# ── Part 2: Merge roman_province/region duplicate pairs ──────────────────────
print('=== Part 2: Merge roman_province/region duplicates ===')

# Pairs: (roman_province data_id, region data_id to keep)
MERGE_PAIRS = [
    (960007, 3158),   # Asia / ASIA
    (960010, 3179),   # Cappadocia / CAPPADOCIA
    (960012, 3198),   # Cilicia / CILICIA
    (960021, 3156),   # Galatia / GALATIA
    (960026, 2910),   # Italia / ITALIA
    (960031, 3213),   # Mesopotamia / MESOPOTAMIA
    (960038, 2980),   # Pannonia inferior / PANNONIA INFERIOR
]

id_map = {r['data_id']: r for r in db['records']}
to_delete = set()

for rp_id, reg_id in MERGE_PAIRS:
    rp = id_map.get(rp_id)
    reg = id_map.get(reg_id)
    if not rp or not reg:
        print(f'  WARN  pair ({rp_id},{reg_id}): one or both not found')
        continue

    # Copy fields from roman_province into region if region has empty values
    for field in ('country', 'province', 'region', 'modern_preferred',
                  'modern_tabula', 'modern_omnesviae', 'lat', 'lng'):
        rp_val = rp.get(field)
        reg_val = reg.get(field)
        if rp_val and not reg_val:
            reg[field] = rp_val

    print(f'  MERGE  rp:{rp_id} ({rp.get("latin","")[:25]}) → reg:{reg_id} ({reg.get("latin","")[:25]})')
    to_delete.add(rp_id)

db['records'] = [r for r in db['records'] if r['data_id'] not in to_delete]
print(f'\nDeleted {len(to_delete)} roman_province duplicates\n')

# ── Part 3: Add ULM 1887 (Magaris, city, India, planquadrat 11B5) ─────────────
print('=== Part 3: Add ULM 1887 (Magaris) ===')

existing_ids = {r['data_id'] for r in db['records']}
if 3001887 not in existing_ids:
    new_entry = {
        'record_id': 'ULM:00001887',
        'source': 'tabula',
        'data_id': 3001887,
        'latin': 'Magaris',
        'latin_std': 'Magaris',
        'modern_omnesviae': '',
        'modern_tabula': '',
        'modern_preferred': '',
        'type': 'city',
        'symbol': 'doppelturm',
        'lat': None,
        'lng': None,
        'px': None,
        'py': None,
        'province': '',
        'country': '',
        'region': '',
        'tabula_segment': 12,
        'tabula_col': 5,
        'tabula_row': 'b',
        'grid_col': 5,
        'grid_row': 'b',
        'tabula_location': 'Seg 12 b5',
        'match_status': 'ulm_only',
        'ulm_id': 1887,
        'ulm_img_url': 'https://tp-online.ku.de/insetimages/TPPlace1887insetneu.png',
        'ulm_planquadrat': '11B5',
    }
    db['records'].append(new_entry)
    print('  Added Magaris (data_id=3001887, ULM 1887, Seg 12 b5)')
else:
    print('  Already exists, skipped')

# Save
tmp = path + '.tmp'
with open(tmp, 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)
os.replace(tmp, path)
print('\nSaved.')
