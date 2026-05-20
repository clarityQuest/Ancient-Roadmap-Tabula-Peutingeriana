import sys, json
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'public/data/review_places_db.json'
db = json.loads(DB_PATH.read_text(encoding='utf-8'))
recs = {r['data_id']: r for r in db['records']}

# (data_id, wiki_url, lat, lng, country, conf, manual)
ENTRIES = [
    # ── GALLIC TRIBES (conf=3) ────────────────────────────────────────────────────
    (2873, 'https://en.wikipedia.org/wiki/Bituriges',        47.064442, 2.397, 'FR', 3, True),  # Bituriges = Bituriges Cubi (Bourges/Avaricum)
    (2880, 'https://en.wikipedia.org/wiki/Vocontii',         44.160503, 5.350, 'FR', 3, True),  # Bocontii = Vocontii (Provençal Alps)
    (2858, 'https://en.wikipedia.org/wiki/Cadurci',          44.415927, 1.441, 'FR', 3, True),  # Cadurcii = Cadurci (Cahors/Divona)
    (2885, 'https://en.wikipedia.org/wiki/Caturiges',        44.504321, 6.490, 'FR', 3, True),  # Caturiges (Embrun area, Alps)
    (2881, 'https://en.wikipedia.org/wiki/Cavares',          43.907435, 4.810, 'FR', 3, True),  # Cavares (Rhône valley, Provence)
    (2863, 'https://en.wikipedia.org/wiki/Nitiobroges',      44.281904, 0.620, 'FR', 3, True),  # Nitiobro = Nitiobroges (Agen/Agennum)
    (2871, 'https://en.wikipedia.org/wiki/Parisii_(Gaul)',   48.755457, 2.340, 'FR', 3, True),  # Parisi = Parisii (Paris/Lutetia)
    (2859, 'https://en.wikipedia.org/wiki/Ruteni',           44.182947, 2.573, 'FR', 3, True),  # Ruteni (Rodez/Segodunum)
    (2878, 'https://en.wikipedia.org/wiki/Treveri',          49.752969, 6.637, 'LU', 3, True),  # Treveri (Trier/Augusta Treverorum)
    (2846, 'https://en.wikipedia.org/wiki/Veneti_(Gaul)',    47.769306, -2.76, 'FR', 3, True),  # Veneti (Armorica/Brittany)
    (2865, 'https://en.wikipedia.org/wiki/Volcae',           43.176032,  1.89, 'FR', 3, True),  # Volcae Tectosages (Toulouse/Narbo area) — fix ES→FR
    (2845, 'https://en.wikipedia.org/wiki/Osismii',          48.331073, -4.09, 'FR', 3, True),  # Osismi/Osismii (Finistère, Brittany)
    (2894, 'https://en.wikipedia.org/wiki/Nantuates',        46.202704,  7.09, 'CH', 3, True),  # Nantuani = Nantuates (Valais, Alps)
    (2891, 'https://en.wikipedia.org/wiki/Rauraci',          47.530000,  7.720, 'CH', 3, True),  # Rauraci (Augusta Raurica, near Basel)

    # ── GERMANIC TRIBES (conf=3) ──────────────────────────────────────────────────
    (2944, 'https://en.wikipedia.org/wiki/Marcomanni',       50.000000, 14.000, 'CZ', 3, True),  # MARCOMANNI (Bohemia)
    (2951, 'https://en.wikipedia.org/wiki/Quadi',            48.500000, 17.500, 'SK', 3, True),  # QVADI = Quadi (Moravia/Slovakia)
    (2945, 'https://en.wikipedia.org/wiki/Vandals',          52.000000, 15.000, 'PL', 3, True),  # VANDVLI = Vandals (original northern homeland)
    (2842, 'https://en.wikipedia.org/wiki/Chamavi',          51.977112,  6.290, 'NL', 3, True),  # CHAMAVI QVI et FRANCI = Chamavi (Lower Rhine)
    (3090, 'https://en.wikipedia.org/wiki/Venedi',           52.500000, 21.000, 'PL', 3, True),  # Venedi (Vistula area, Baltic Slavic people)

    # ── NORTH AFRICAN PEOPLES (conf=3) ───────────────────────────────────────────
    (2913, 'https://en.wikipedia.org/wiki/Gaetuli',          35.525629,  3.200, 'DZ', 3, True),  # Gaetuli (Numidian steppe people)
    (3052, 'https://en.wikipedia.org/wiki/Garamantes',       27.500000,  9.000, 'LY', 3, True),  # Garamantes (Fezzan/Saharan civilization)
    (2876, 'https://en.wikipedia.org/wiki/Musulamii',        35.521608,  8.700, 'TN', 3, True),  # Musulamiorum = Musulamii (Tunisia/Algeria)
    (3072, 'https://en.wikipedia.org/wiki/Nasamones',        30.568379, 20.000, 'LY', 3, True),  # Nesamones = Nasamones (Libyan desert people)
    (3098, 'https://en.wikipedia.org/wiki/Pentapolis_(North_Africa)', 32.471545, 21.000, 'LY', 3, True),  # Pentapolites = people of Cyrenaean Pentapolis

    # ── CAUCASIAN / BLACK SEA PEOPLES (conf=3) ────────────────────────────────────
    (3208, 'https://en.wikipedia.org/wiki/Colchians',        42.201755, 42.000, 'GE', 3, True),  # Colchi = Colchians (ancient Colchis, Georgia)
    (3128, 'https://en.wikipedia.org/wiki/Lazs',             42.201755, 41.500, 'GE', 3, True),  # Lazi = Lazs (Lazica, Colchis coast)
    (2834, 'https://en.wikipedia.org/wiki/Svans',            42.736102, 43.050, 'GE', 3, True),  # Suani = Svans (Svaneti, Georgia)
    (3127, 'https://en.wikipedia.org/wiki/Alans',            47.000000, 43.000, 'RU', 3, True),  # Alani = Alans (North Caucasus steppe)
    (3119, 'https://en.wikipedia.org/wiki/Maeotae',          45.250000, 37.000, 'UA', 3, True),  # Meote = Maeotae (people of Lake Maeotis/Sea of Azov)
    (3107, 'https://en.wikipedia.org/wiki/Roxolani',         47.000000, 36.000, 'UA', 3, True),  # Roxulani Sarmatae = Roxolani (Pontic steppe)
    (3129, 'https://en.wikipedia.org/wiki/Heniochi',         43.000000, 41.500, 'GE', 3, True),  # Eniochi = Heniochi (eastern Black Sea coast, Colchis)
    (3122, 'https://en.wikipedia.org/wiki/Bosporan_Kingdom', 45.300000, 36.500, 'UA', 3, True),  # Bosforani = Bosporans (Cimmerian Bosporus/Kerch Strait)
    (3126, 'https://en.wikipedia.org/wiki/Aspurgiani',       45.000000, 37.500, 'RU', 3, True),  # Aspurgiani (Taman Peninsula, Bosporan clients)

    # ── ITALIAN PEOPLES (conf=3) ──────────────────────────────────────────────────
    (2949, 'https://en.wikipedia.org/wiki/Etruscans',        42.673438, 11.500, 'IT', 3, True),  # TVSCI = Etruscans/Tusci (Etruria/Tuscany)
    (2999, 'https://en.wikipedia.org/wiki/Salentini',        40.007106, 18.100, 'IT', 3, True),  # Salentini (Salento/heel of Italy, Messapia)

    # ── DANUBIAN / BALKAN PEOPLES (conf=3) ────────────────────────────────────────
    (3078, 'https://en.wikipedia.org/wiki/Getae',            45.829650, 27.500, 'RO', 3, True),  # Gaete = Getae (Dacian/Thracian people, Dobrudja/Wallachia)

    # ── MYTHOLOGICAL / LEGENDARY (conf=3) ─────────────────────────────────────────
    (3168, 'https://en.wikipedia.org/wiki/Amazons',          40.500000, 37.000, 'TR', 3, True),  # Amazones (traditional Pontic placement)

    # ── SCYTHIAN PEOPLES (conf=3) ─────────────────────────────────────────────────
    (3260, 'https://en.wikipedia.org/wiki/Issedones',        55.000000, 73.000, 'KZ', 3, True),  # Essedones Scythae = Issedones (Central Asian Scythians)

    # ── INDIAN / EASTERN PEOPLES (conf=3) ─────────────────────────────────────────
    (3265, 'https://en.wikipedia.org/wiki/Gandhara',         33.490006, 71.780, 'AF', 3, True),  # Gandari Indi = Gandhara (ancient NW Indian civilization)
    (3267, 'https://en.wikipedia.org/wiki/Gedrosia',         26.608330, 63.500, 'PK', 3, True),  # Cedrosiani = Gedrosia (Balochistan, ancient Gedrosia)
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
