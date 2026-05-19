import sys, json
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'public/data/review_places_db.json'
db = json.loads(DB_PATH.read_text(encoding='utf-8'))
recs = {r['data_id']: r for r in db['records']}

# (data_id, wiki_url, lat, lng, country, conf, manual)
# lat/lng only applied if record has none; country corrects wrong values
ENTRIES = [
    # ── Conf 3 — clear ancient-name match ──────────────────────────────────
    (1857,   'https://en.wikipedia.org/wiki/Nicopolis',           39.0265, 20.7334, 'GR', 3, True),  # Actanicopoli = Actia Nicopolis (Epirus)
    (2354,   'https://en.wikipedia.org/wiki/Laodicea_on_the_Lycus', 37.834, 29.113,'TR', 3, True),  # Lavdicivm pilycvm
    (1917,   'https://en.wikipedia.org/wiki/Methoni,_Messenia',   36.8180, 21.7073, 'GR', 3, True),  # Mothone
    (1769,   'https://en.wikipedia.org/wiki/Ratiaria',            43.7694, 22.8699, 'BG', 3, True),  # Ratiaris
    ( 548,   'https://en.wikipedia.org/wiki/Richborough',         51.2920,  1.3367, 'GB', 3, True),  # Ratvpis = Rutupiae
    (2360,   'https://en.wikipedia.org/wiki/Selinus,_Cilicia',    36.2713, 32.3125, 'TR', 3, True),  # Selinvnte
    (1725,   'https://en.wikipedia.org/wiki/Tibiscum',            45.4591, 22.1865, 'RO', 3, True),  # Tivisco
    (2099,   'https://en.wikipedia.org/wiki/Tium',                41.5541, 32.0222, 'TR', 3, True),  # Tivm
    (1951,   'https://en.wikipedia.org/wiki/Troesmis',            45.1006, 28.1804, 'RO', 3, True),  # Troesmis
    ( 215,   'https://en.wikipedia.org/wiki/Thelepte',            34.9792,  8.5941, 'TN', 3, True),  # Theleote col.
    (3000685,'https://en.wikipedia.org/wiki/Burnum',              44.0200, 16.0500, 'HR', 3, True),  # Burno = Burnum (Dalmatia)
    (2144,   'https://en.wikipedia.org/wiki/Tavium',              39.8583, 34.5179, 'TR', 3, True),  # Tavio = Tavium (Galatia)
    ( 505,   'https://en.wikipedia.org/wiki/Raphanea',            34.9664, 36.3930, 'SY', 3, True),  # Raphanis = Raphanea (Syria) + fix SYR→SY
    (2369,   'https://en.wikipedia.org/wiki/Aegeae_(Cilicia)',    36.7667, 35.7833, 'TR', 3, True),  # Aregea = Aegeae (Yumurtalık)
    (2076,   'https://en.wikipedia.org/wiki/Hierapytna',          35.0103, 25.7405, 'GR', 3, True),  # Hiera = Hierapytna (Crete)
    ( 388,   'https://en.wikipedia.org/wiki/Maharraqa',           23.0491, 32.7369, 'EG', 3, True),  # Herasicamina = Hiera Sycaminos; fix ET→EG
    (1922,   'https://en.wikipedia.org/wiki/Boiai',               36.5000, 23.0667, 'GR', 3, True),  # Boas = Boiai (Laconia), modern Neapoli Vion

    # ── Conf 2 — probable match ─────────────────────────────────────────────
    (2134,   'https://en.wikipedia.org/wiki/Juliopolis',          40.0752, 31.3985, 'TR', 2, True),  # Ivliopoli = Juliopolis (Bithynia)
    (1981,   'https://en.wikipedia.org/wiki/Apros',               40.9699, 27.0699, 'TR', 2, True),  # Apris = Apros (Thrace)
    (2200,   'https://en.wikipedia.org/wiki/Miletopolis',         40.0835, 28.3165, 'TR', 2, True),  # Mileopoli = Miletopolis (Mysia)
    (2242,   'https://en.wikipedia.org/wiki/Polemonion',          41.0345, 37.5955, 'TR', 2, True),  # Polemonio = Polemonion (Pontus)
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
    print(f'  OK  {data_id:<10}  {(r.get("latin_std") or r.get("latin",""))[:35]}')

print(f'\nApplied {saved} wiki_url entries')
tmp = DB_PATH.with_suffix('.tmp')
tmp.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding='utf-8')
tmp.replace(DB_PATH)
print(f'Saved -> {DB_PATH.name}')
