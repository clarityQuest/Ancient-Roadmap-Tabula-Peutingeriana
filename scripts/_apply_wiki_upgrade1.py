import sys, json
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'public/data/review_places_db.json'
db = json.loads(DB_PATH.read_text(encoding='utf-8'))
recs = {r['data_id']: r for r in db['records']}

# (data_id, new_wiki_url, new_country_or_None)
# All are genuine upgrades: modern-city link → ancient-name article
# lat/lng kept as-is (already set from earlier runs or manual entry)
UPGRADES = [
    (2404,   'https://de.wikipedia.org/wiki/Kastell_Apsaros',        None),  # Gonio → Kastell Apsaros
    (2464,   'https://it.wikipedia.org/wiki/Artaxata',               None),  # Artashat → Artaxata
    ( 434,   'https://en.wikipedia.org/wiki/Ascalon',                None),  # Ashkelon → Ascalon
    ( 658,   'https://fr.wikipedia.org/wiki/Augustodunum',           None),  # Autun → Augustodunum
    (1947,   'https://en.wikipedia.org/wiki/Axiopolis_(castra)',      None),  # more specific article
    (2634,   'https://en.wikipedia.org/wiki/Edessa,_Mesopotamia',    'TR'),  # Urfa → Edessa + fix SY→TR
    (1585,   'https://en.wikipedia.org/wiki/Emona',                  None),  # Ljubljana → Emona
    (1048,   'https://en.wikipedia.org/wiki/Mediolanum',             None),  # Mediolanum_(Gallia_cisalpina) → Mediolanum
    (2384,   'https://en.wikipedia.org/wiki/Miletus',                'TR'),  # Balat → Miletus + fix GR→TR
    (1849,   'https://en.wikipedia.org/wiki/Nicaea',                 'TR'),  # Capari (wrong!) → Nicaea
    (2129,   'https://en.wikipedia.org/wiki/Nicaea',                 'TR'),  # İznik → Nicaea
    (1475,   'https://en.wikipedia.org/wiki/Oplontis',               None),  # Torre_Annunziata → Oplontis
    ( 527,   'https://en.wikipedia.org/wiki/Palmyra',                None),  # Palmyra,_Syria → Palmyra (cleaner)
    (2204,   'https://en.wikipedia.org/wiki/Pergamon',               'TR'),  # Bergama → Pergamon + fix GR→TR
    (1681,   'https://en.wikipedia.org/wiki/Salona',                 'HR'),  # Solin → Salona + fix BA→HR
    (2415,   'https://en.wikipedia.org/wiki/Satala',                 None),  # Sadak → Satala
    ( 120,   'https://de.wikipedia.org/wiki/Sicca_Veneria',          None),  # Le_Kef → Sicca_Veneria
    (2104,   'https://en.wikipedia.org/wiki/Sinope',                  'TR'),  # Sinop (modern) → Sinope (ancient name)
    (2168,   'https://en.wikipedia.org/wiki/Synnada',                None),  # Şuhut → Synnada
    ( 755,   'https://en.wikipedia.org/wiki/Toulouse',               'FR'),  # fix country ES→FR; Toulouse already correct article
    (1542,   'https://en.wikipedia.org/wiki/Vindobona',              'AT'),  # Vienna → Vindobona + fix HU→AT
    (2000862,'https://en.wikipedia.org/wiki/Prusias_ad_Hypium',      None),  # Gemlik → Prusias ad Hypium
]

saved = 0
for data_id, new_url, new_country in UPGRADES:
    r = recs.get(data_id)
    if r is None:
        print(f'  MISSING {data_id}')
        continue
    old_url = r.get('wiki_url', '')
    r['wiki_url']        = new_url
    r['wiki_confidence'] = 3
    r['wiki_manual']     = True
    if new_country:
        r['country'] = new_country
    saved += 1
    latin = (r.get('latin_std') or r.get('latin', ''))[:30]
    print(f'  OK  {data_id:<10}  {latin:<30}  {old_url[:50]} → {new_url[:50]}')

print(f'\nApplied {saved} upgrades')
tmp = DB_PATH.with_suffix('.tmp')
tmp.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding='utf-8')
tmp.replace(DB_PATH)
print(f'Saved -> {DB_PATH.name}')
