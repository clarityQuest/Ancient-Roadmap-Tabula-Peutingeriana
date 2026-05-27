import sys, json
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'public/data/review_places_db.json'
db = json.loads(DB_PATH.read_text(encoding='utf-8'))
recs = {r['data_id']: r for r in db['records']}

# (data_id, wiki_url, lat, lng, country, conf, manual)
ENTRIES = [
    # ── Conf 3 — exact province/region matches ────────────────────────────────────
    (2937,    'https://en.wikipedia.org/wiki/Numidia',                      36.0,  6.0, 'DZ', 3, True),  # [NVMI]DIA = Numidia
    (3059,    'https://en.wikipedia.org/wiki/Achaia_(Roman_province)',       38.5, 22.5, 'GR', 3, True),  # ACHAIA = Roman province Achaia
    (2897,    'https://en.wikipedia.org/wiki/Alamannia',                    48.5,  9.0, 'DE', 3, True),  # ALAMANNIA = Alamannia (SW Germany)
    (3243,    'https://en.wikipedia.org/wiki/Caucasian_Albania',            40.5, 48.0, 'AZ', 3, True),  # ALBANIA = Caucasian Albania (NOT modern Albania)
    (2984,    'https://en.wikipedia.org/wiki/Apulia',                       41.0, 16.5, 'IT', 3, True),  # APVLIA = Apulia (Puglia)
    (3206,    'https://en.wikipedia.org/wiki/Arabia_Petraea',               30.0, 37.0, 'JO', 3, True),  # ARABIA = Arabia Petraea (Roman province)
    (3249,    'https://en.wikipedia.org/wiki/Atropatene',                   37.5, 46.5, 'IR', 3, True),  # ATRAPATENE = Atropatene / Media Atropatene
    (3273,    'https://en.wikipedia.org/wiki/Bactria',                      37.0, 67.0, 'AF', 3, True),  # BACTRIANOE = Bactria (N Afghanistan)
    (3220,    'https://en.wikipedia.org/wiki/Babylonia',                    32.5, 44.5, 'IQ', 3, True),  # Banylonia = Babylonia (map corruption)
    (3143,    'https://en.wikipedia.org/wiki/Bithynia',                     40.5, 30.0, 'TR', 3, True),  # BITHINIA = Bithynia (NW Anatolia)
    (3250,    'https://en.wikipedia.org/wiki/Caspiane',                     39.5, 49.0, 'AZ', 3, True),  # CASPIANE = ancient SW Caspian region
    (3112,    'https://en.wikipedia.org/wiki/Tauric_Chersonese',            45.0, 34.0, 'UA', 3, True),  # CERONESOS = Tauric Chersonese (Crimea)
    (2892,    'https://en.wikipedia.org/wiki/Alpes_Cottiae',                44.7,  7.0, 'IT', 3, True),  # COTII REGNVM = Alpes Cottiae (Kingdom of Cottius)
    (2981,    'https://en.wikipedia.org/wiki/Dalmatia_(Roman_province)',    44.0, 17.0, 'BA', 3, True),  # DALMATIA = Roman province
    (3252,    'https://en.wikipedia.org/wiki/Adiabene',                     36.5, 44.0, 'IQ', 3, True),  # DIABENE = Adiabene (NE Iraq/Kurdistan)
    (2862,    'https://en.wikipedia.org/wiki/Francia',                      49.0,  8.0, 'FR', 3, True),  # FRANCIA = Frankish realm
    (2882,    'https://en.wikipedia.org/wiki/Ancient_Greece',               39.5, 22.0, 'GR', 3, True),  # GRETIA = Graecia = Ancient Greece
    (3241,    'https://en.wikipedia.org/wiki/Kingdom_of_Iberia',            42.0, 44.5, 'GE', 3, True),  # HIBERIA = Caucasian Iberia (eastern Georgia)
    (3058,    'https://en.wikipedia.org/wiki/Epirus_(Roman_province)',       41.3, 19.8, 'AL', 3, True),  # IEPIRVM NOVVM = Epirus Nova
    (3000,    'https://en.wikipedia.org/wiki/Lucania',                      40.3, 16.0, 'IT', 3, True),  # LVCCANIA = Lucania (S Italy)
    (3181,    'https://en.wikipedia.org/wiki/Lycia',                        36.5, 29.5, 'TR', 3, True),  # LYCIA = Lycia (SW Turkey)
    (3037,    'https://en.wikipedia.org/wiki/Macedonia_(Roman_province)',    41.0, 22.5, 'GR', 3, True),  # MACEDONIA = Roman province
    (3266,    'https://en.wikipedia.org/wiki/Media_(region)',                35.0, 47.5, 'IR', 3, True),  # MEDIA = Media (NW Iran)
    (3218,    'https://en.wikipedia.org/wiki/Media_(region)',                34.5, 47.0, 'IR', 3, True),  # MEDIA MAIOR = Greater Media
    (3021,    'https://en.wikipedia.org/wiki/Moesia',                       43.5, 26.0, 'BG', 3, True),  # MESIA INFERIOR = Moesia Inferior (N Bulgaria)
    (2995,    'https://en.wikipedia.org/wiki/Moesia',                       44.0, 21.0, 'RS', 3, True),  # MESIA SVPERIOR = Moesia Superior (Serbia)
    (3171,    'https://en.wikipedia.org/wiki/Paphlagonia',                  41.5, 33.5, 'TR', 3, True),  # PAFLAGONIA = Paphlagonia (N Turkey)
    (3190,    'https://en.wikipedia.org/wiki/Syria_Palaestina',             31.5, 35.0, 'IL', 3, True),  # PALESTINA = Syria Palaestina
    (2969,    'https://en.wikipedia.org/wiki/Pannonia_Superior',            47.5, 16.0, 'AT', 3, True),  # PANNONIA SVPERIOR = Pannonia Superior
    (3231,    'https://en.wikipedia.org/wiki/Persis',                       29.5, 52.5, 'IR', 3, True),  # PERSIDA = Persis (Fars province, SW Iran)
    (3157,    'https://en.wikipedia.org/wiki/Phrygia',                      39.0, 31.0, 'TR', 3, True),  # PHRYGIA = Phrygia (central Anatolia)
    (3187,    'https://en.wikipedia.org/wiki/Pontus_(region)',               40.5, 37.5, 'TR', 3, True),  # P[O]NTVS POLEMONI[ACVS] = Pontus Polemoniacus
    (2941,    'https://en.wikipedia.org/wiki/Cisalpine_Gaul',               45.5, 10.0, 'IT', 3, True),  # REGIO TR(AN)SPA[DANA] = Transpadana = Cisalpine Gaul
    (2994,    'https://en.wikipedia.org/wiki/Sarmatia',                     50.0, 35.0, 'UA', 3, True),  # SOLITVDINES SARMATARVM = Sarmatia
    (3067,    'https://en.wikipedia.org/wiki/Thracia',                      42.0, 26.0, 'BG', 3, True),  # TRHACIA = Thracia (Roman province)
    (50024,   'https://en.wikipedia.org/wiki/Africa_(Roman_province)',       36.5, 10.0, 'TN', 3, True),  # {PROVINCIA} AFRICA = Roman Africa
    (50025,   'https://en.wikipedia.org/wiki/Phoenice_(Roman_province)',    34.0, 36.5, 'LB', 3, True),  # {SYRRIA} PHOENIX = Syria Phoenice
    (3191,    'https://en.wikipedia.org/wiki/Phoenice_(Roman_province)',    34.0, 36.5, 'LB', 3, True),  # SYRRIA PHOENIX = Syria Phoenice (second label)
    (3066,    'https://en.wikipedia.org/wiki/Aria_(region)',                34.5, 62.0, 'AF', 3, True),  # ARIACTA = Aria (satrapy, W Afghanistan/Herat)
    (3173,    'https://en.wikipedia.org/wiki/Sinai_Peninsula',              29.5, 33.5, 'EG', 3, True),  # Desertum 40 years = Sinai (Israel wandering)
    (2352,    'https://en.wikipedia.org/wiki/Cynocephaly',                  None, None, None, 3, True),  # Hic cenocephali = dog-headed people (Cynocephaly)
    (3002279, 'https://en.wikipedia.org/wiki/Lake_Tritonis',                33.5,  8.5, 'TN', 3, True),  # Hic Lacvs TRiToNvM = Lake Tritonis (Tunisia)
    (3656,    'https://en.wikipedia.org/wiki/Mount_Sinai',                  28.5, 33.9, 'EG', 3, True),  # Hic legem acceperunt in monte Syna = Mount Sinai
    (3657,    'https://en.wikipedia.org/wiki/Nile',                         27.0, 30.5, 'EG', 3, True),  # Flumen... Nilum = the Nile
    (3001952, 'https://en.wikipedia.org/wiki/Siwa_Oasis',                   29.2, 25.5, 'EG', 3, True),  # Hic Alexander Responsum = Siwa oracle

    # ── Conf 2 — probable matches ─────────────────────────────────────────────────
    (2982,    'https://en.wikipedia.org/wiki/Bithynia',                     41.5, 30.5, 'TR', 2, True),  # BVLINIA = Bithynia (second label on TP)
    (3199,    'https://en.wikipedia.org/wiki/Cilicia_Trachaea',             36.8, 33.5, 'TR', 2, True),  # CLENDERITIS = Cilicia Trachea (Rough Cilicia)
    (2860,    'https://en.wikipedia.org/wiki/Gaul',                         47.0,  3.0, 'FR', 2, True),  # GALLIA COMATA = Gaul (article covers Gallia Comata)
    (3251,    'https://en.wikipedia.org/wiki/Amardi',                       36.5, 51.0, 'IR', 2, True),  # MARDIANE = land of the Amardi (S Caspian, Iran)
    (2965,    'https://en.wikipedia.org/wiki/Media_(region)',                34.5, 48.0, 'IR', 2, True),  # ME˙DIA. PROVI = Media Provincia
    (2939,    'https://en.wikipedia.org/wiki/Media_(region)',                34.0, 47.0, 'IR', 2, True),  # MEDIA PROVINCIA = Media as province
    (3262,    'https://en.wikipedia.org/wiki/Atropatene',                   37.5, 46.0, 'IR', 2, True),  # MEDIO MINOR = Media Minor = Atropatene
    (3244,    'https://en.wikipedia.org/wiki/Parthia',                      37.0, 58.0, 'IR', 2, True),  # PARRIA = Parthia (region, NE Iran)
    (2866,    'https://en.wikipedia.org/wiki/Regio_VI_Umbria',              43.5, 12.5, 'IT', 2, True),  # VMBRANICIA = Umbria (Regio VI)
    (3203,    'https://en.wikipedia.org/wiki/Coele_Syria_(Roman_province)', 34.5, 37.0, 'SY', 2, True),  # S˙YR.IACOLE = Coele-Syria (Roman province)
    (3201,    'https://en.wikipedia.org/wiki/Arabia_Petraea',               32.0, 37.5, 'JO', 2, True),  # SYRIA ARABIA = Arabia/Syria border zone
    (3105,    'https://en.wikipedia.org/wiki/Tectosages',                   39.5, 32.5, 'TR', 2, True),  # TANASIS GALATIE = Tectosages area of Galatia
    (3467,    'https://en.wikipedia.org/wiki/Sea_of_Azov',                  46.0, 37.0, 'RU', 2, True),  # Hij montes = mountains near Lake Maeotis (Sea of Azov)
    (211,     'https://en.wikipedia.org/wiki/Dia_(island)',                  35.5, 25.2, 'GR', 2, True),  # DIA = island of Dia (off Crete/Heraklion)
    (3002297, 'https://en.wikipedia.org/wiki/Fossatum_Africae',             34.0,  9.0, 'TN', 2, True),  # Fossa Facta = Fossatum Africae (Roman ditch, N Africa)

    # ── Conf 1 — speculative ──────────────────────────────────────────────────────
    (3081,    'https://en.wikipedia.org/wiki/Raetia',                       47.0, 11.0, 'AT', 1, True),  # RIMESICA = possibly corrupt label near Raetia
    (3118,    'https://en.wikipedia.org/wiki/Sarmatians',                   46.5, 32.0, 'UA', 1, True),  # SAVRICA = possibly Sauromatae/Sarmatians (N Black Sea)
    (3253,    'https://en.wikipedia.org/wiki/Argyria_(Pontus)',             40.5, 38.0, 'TR', 1, True),  # Argene Superioris = possibly Argyria in Pontus
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
    if lat is not None and r.get('lat') is None:
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
