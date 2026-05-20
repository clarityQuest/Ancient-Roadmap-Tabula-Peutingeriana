import sys, json
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'public/data/review_places_db.json'
db = json.loads(DB_PATH.read_text(encoding='utf-8'))
recs = {r['data_id']: r for r in db['records']}

# (data_id, wiki_url, lat, lng, country, conf, manual)
ENTRIES = [
    (2854, 'https://en.wikipedia.org/wiki/Bituriges_Cubi',    45.167766,  0.700, 'FR', 3, True),  # Beturiges = Bituriges Cubi (confirmed by user)
    (2879, 'https://en.wikipedia.org/wiki/Mediomatrici',      49.294037,  6.175, 'FR', 2, True),  # ME˙DIO MATRICI = Mediomatrici (Metz area) — fix DE→FR
    (2839, 'https://en.wikipedia.org/wiki/Chauci',            53.337481,  8.500, 'DE', 2, True),  # Haci = Chauci (North Sea coast, by position)
    (2875, 'https://en.wikipedia.org/wiki/Numidians',         36.150940,  4.500, 'DZ', 2, True),  # Numidarum = Numidians
    (2831, 'https://en.wikipedia.org/wiki/Zichia',            43.813910, 39.500, 'RU', 2, True),  # Achei = eastern Black Sea coast tribe (Achaei_(Caucasian) 404→Zichia)
    (3020, 'https://en.wikipedia.org/wiki/Amaxobii',          48.000000, 40.000, 'UA', 2, True),  # AMAXOBIISARMATE = Amaxobii (wagon-dwelling Sarmatians)
    (3075, 'https://en.wikipedia.org/wiki/Bastarnae',         46.000000, 30.000, 'MD', 2, True),  # Blastarni = Bastarnae (Pontic steppe/Dacia border)
    (3233, 'https://en.wikipedia.org/wiki/Saka',              42.000000, 70.000, 'KZ', 2, True),  # SaGaes cytHae = Sacae/Saka (Central Asian Scythians)
    (3272, 'https://en.wikipedia.org/wiki/Saka',              42.000000, 70.000, 'KZ', 2, True),  # Sagae Scythae = Saka (second label)
    (3268, 'https://en.wikipedia.org/wiki/Ichthyophagi',      24.000000, 57.000, 'PK', 2, True),  # ICTHyofaGi = Ichthyophagi (fish-eaters, Makran coast)
    (3046, 'https://en.wikipedia.org/wiki/Sarmatians',        51.527063, 22.000, 'PL', 2, True),  # Lupiones Sarmatae = Sarmatians (no dedicated article for Lupiones)
    (2976, 'https://en.wikipedia.org/wiki/Sarmatians',        47.270778, 27.000, 'RO', 2, True),  # SARMATEVAGI = wandering Sarmatians
    (3110, 'https://en.wikipedia.org/wiki/Byzantium',         41.005902, 28.980, 'TR', 2, True),  # Byzantini = people of Byzantium — fix GR→TR
    (3192, 'https://en.wikipedia.org/wiki/Damascus',          33.511612, 36.292, 'SY', 2, True),  # Damasceni = people of Damascus — fix LB→SY
    (3178, 'https://en.wikipedia.org/wiki/Pontus',            40.221357, 36.000, 'TR', 2, True),  # Pontici = people of Pontus
    (3036, 'https://en.wikipedia.org/wiki/Gaetuli',           33.500000,  9.000, 'TN', 2, True),  # Bagigetuli = sub-tribe of Gaetuli
    (3071, 'https://en.wikipedia.org/wiki/Syrtes',            30.294708, 16.000, 'LY', 2, True),  # Syrtites = people of the Syrtic coast
]

saved = 0
for data_id, wiki_url, lat, lng, country, conf, manual in ENTRIES:
    r = recs.get(data_id)
    if r is None:
        print(f'  MISSING {data_id}')
        continue
    if r.get('wiki_url'):
        print(f'  SKIP (already has wiki_url) {data_id}')
        continue
    r['wiki_url']        = wiki_url
    r['wiki_confidence'] = conf
    r['wiki_manual']     = manual
    if r.get('lat') is None and lat is not None:
        r['lat'] = lat
        r['lng'] = lng
    if country:
        r['country'] = country
    saved += 1
    print(f'  OK  {data_id:<12}  {(r.get("latin_std") or r.get("latin",""))[:45]}')

print(f'\nApplied {saved} wiki_url entries')
tmp = DB_PATH.with_suffix('.tmp')
tmp.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding='utf-8')
tmp.replace(DB_PATH)
print(f'Saved -> {DB_PATH.name}')
