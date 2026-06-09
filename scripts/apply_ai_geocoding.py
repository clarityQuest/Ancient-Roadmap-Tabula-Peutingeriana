"""
Apply AI+WebSearch geocoding results to review_places_db.json.
Coordinates found via Claude AI knowledge + WebSearch.
Only sets geocoding_confidence; wiki_confidence is reserved for Wikipedia API finds only.
"""
import json, sys, io, shutil, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

DB_PATH = "public/data/review_places_db.json"
DRY_RUN = "--dry-run" in sys.argv

# fmt: data_id -> (lat, lng, geocoding_confidence, wiki_url, note)
# geocoding_confidence:
#   3 = direct modern name match from modern_preferred hint
#   2 = calculated from distance to anchor, or "near X" without distance
FINDS = {
    # Greece ----------------------------------------------------------------
    2043: (40.961, 24.547, 2, None, "3km E Nea Karvali (calculated)"),
    2053: (41.085, 23.543, 3, "https://en.wikipedia.org/wiki/Serres", "Sarres=Serres Greece"),
    2045: (41.134, 24.888, 2, None, "near Xanthi (uncertain '?')"),
    2058: (41.090, 23.520, 2, None, "Aidonochori, Serres area"),
    1913: (37.450, 22.080, 2, None, "NW Megalopolis, Arcadia"),
    1868: (41.025, 22.574, 2, None, "N of Polykastro/Platamona"),

    # Algeria ---------------------------------------------------------------
    176:  (36.193, 7.655,  3, "https://en.wikipedia.org/wiki/Khamissa", "Khamissa=Thubursicum Numidarium"),
    98:   (36.313, 5.856,  2, None, "7mi E Djemila (calculated)"),
    99:   (36.380, 6.005,  2, None, "midpoint Mila-Djemila (calculated)"),
    173:  (35.488, 6.683,  2, None, "13mi E Timgad (calculated)"),
    172:  (35.488, 6.617,  2, None, "9mi E Timgad (calculated)"),
    166:  (35.488, 6.978,  2, None, "31mi E Timgad (calculated)"),
    174:  (35.488, 7.208,  2, None, "45mi E Timgad (calculated)"),
    3526: (35.570, 6.820,  2, None, "near Gadiaufala/Ksar Sbahi"),
    3527: (35.580, 6.825,  2, None, "near Gadiaufala/Ksar Sbahi"),
    3528: (35.530, 6.850,  2, None, "SE Gadiaufala/Ksar Sbahi"),
    3516: (36.094, 6.342,  2, None, "26mi W Sigus (calculated)"),
    3517: (36.094, 6.540,  2, None, "14mi W Sigus (calculated)"),

    # Tunisia ---------------------------------------------------------------
    270:  (34.299, 10.070, 3, None, "Skhira/La Skirra, Tunisia"),
    237:  (33.350, 9.650,  2, None, "S Djebel Tebaga, Tunisia"),
    238:  (33.250, 9.750,  2, None, "S Djebel Tebaga, Tunisia (2nd station)"),
    269:  (34.361, 10.097, 2, None, "36mi N Gabes coast (calculated)"),
    277:  (35.200, 10.800, 2, None, "SE El Djem/Augemmi, Tunisia"),
    279:  (35.150, 10.850, 2, None, "SE Augemmi, Tunisia"),
    3001925: (35.130, 10.880, 2, None, "SE Augemmi, Tunisia (Laminie)"),

    # Libya -----------------------------------------------------------------
    311:  (32.891, 13.274, 2, None, "Mellaha E of Tripoli, Libya"),
    296:  (32.870, 13.250, 2, None, "SE Oea/Tripoli, Libya"),
    313:  (31.700, 15.250, 2, None, "S side Sebkha Tauorgha, Libya"),
    356:  (31.700, 24.500, 2, None, "between Catabathmus and Antipyrgos, Libya"),

    # Egypt / Libya border --------------------------------------------------
    358:  (31.440, 26.180, 2, None, "between Paraetonium and Catabathmus"),
    417:  (29.417, 31.217, 3, "https://en.wikipedia.org/wiki/Atfih", "Atfih near Memphis, Egypt"),

    # Syria -----------------------------------------------------------------
    507:  (34.880, 36.370, 2, "https://en.wikipedia.org/wiki/Raphanea", "S of Raphanea, Syria"),

    # Jordan/Syria border ---------------------------------------------------
    481:  (32.493, 36.471, 2, "https://en.wikipedia.org/wiki/Bosra", "near Bosra/Bostra"),

    # Turkey ----------------------------------------------------------------
    2120: (41.016, 34.040, 3, "https://en.wikipedia.org/wiki/Tosya", "Tosya, Turkey"),
    2169: (38.583, 31.033, 3, None, "Cay, Afyonkarahisar, Turkey"),
    2529: (39.234, 37.391, 3, "https://en.wikipedia.org/wiki/Kangal", "Kangal, Sivas, Turkey"),
    2250: (40.015, 34.619, 3, "https://en.wikipedia.org/wiki/Bo%C4%9Fazkale", "Bogazkale/Hattusa, Turkey"),
    2525: (39.261, 38.497, 3, "https://en.wikipedia.org/wiki/Kemaliye", "Kemaliye/Egin, Turkey"),
    2112: (40.799, 30.751, 3, "https://en.wikipedia.org/wiki/Hendek", "Hendek, Sakarya, Turkey"),
    2111: (40.688, 30.265, 2, None, "Sapanca Golü area, Turkey"),
    2355: (37.423, 29.363, 2, None, "Acipayam/Karahüyük area, Turkey"),
    2545: (38.203, 37.196, 2, "https://en.wikipedia.org/wiki/Elbistan", "Elbistan, Turkey (Sevdilli Hani)"),
    2547: (38.350, 38.250, 2, None, "SW Eski Malatya, Turkey"),
    2552: (37.949, 42.045, 2, "https://en.wikipedia.org/wiki/Tillo", "Tillo, Siirt, Turkey"),
    2337: (36.960, 34.586, 2, None, "Namlun Kalesi/Camliiyayla, Turkey"),
    2171: (38.227, 30.533, 2, None, "Kinik, 3km N Tatarli, Dinar, Turkey"),
    3001668: (39.937, 38.568, 3, None, "Gölova/Agvanis, Sivas, Turkey"),
    3002023: (37.500, 30.700, 2, None, "SW Pisidia, Turkey (approx)"),

    # Iran ------------------------------------------------------------------
    2776: (31.160, 52.651, 3, "https://en.wikipedia.org/wiki/Abadeh", "Abadeh, Iran"),
    2750: (33.897, 48.752, 3, "https://en.wikipedia.org/wiki/Borujerd", "Borujerd, Iran"),
    2749: (33.376, 52.369, 3, "https://en.wikipedia.org/wiki/Ardestan", "Ardestan, Iran"),
    2704: (34.516, 45.578, 3, "https://en.wikipedia.org/wiki/Qasr-e_Shirin", "Qasr-e Shirin, Iran"),

    # Afghanistan -----------------------------------------------------------
    2743: (35.011, 69.163, 3, "https://en.wikipedia.org/wiki/Charikar", "Charikar, Parwan, Afghanistan"),
    2745: (37.137, 69.491, 3, "https://en.wikipedia.org/wiki/Ai-Khanoum", "Ai-Khanoum, Afghanistan"),

    # Balkans / former Yugoslavia -------------------------------------------
    1823: (41.843, 21.575, 2, None, "17mp SE Skopje (calculated)"),
    1647: (44.812, 20.399, 2, None, "Novi Beograd/Belgrade confluence"),
    2000: (42.170, 24.540, 2, None, "between Bessapara and Philippopolis"),
    3001950: (42.490, 20.860, 2, None, "Velinje/Vilinjam, Kosovo area"),

    # Crimea / Black Sea ----------------------------------------------------
    3001960: (45.038, 35.381, 3, "https://en.wikipedia.org/wiki/Feodosiya", "Feodosiya/Theodosia, Crimea"),
    3001962: (45.216, 36.726, 3, "https://en.wikipedia.org/wiki/Hermonassa", "Hermonasa, Taman Peninsula"),

    # Italy -----------------------------------------------------------------
    1237: (42.157, 12.245, 3, "https://en.wikipedia.org/wiki/Trevignano_Romano", "Trevignano Romano, Italy"),
    1486: (38.926, 16.302, 2, None, "Sant'Eufemia Vetere, Calabria, Italy"),
    1325: (41.550, 13.790, 2, None, "Melfa river, Frosinone province, Italy"),
    1060: (42.700, 12.200, 2, None, "near Graffignano, Viterbo, Italy"),

    # Austria / Danube area ------------------------------------------------
    1514: (48.176, 14.842, 2, None, "Strengberg, Lower Austria"),
    1539: (48.179, 15.831, 2, None, "Murstetten bei Perschling, Lower Austria"),

    # France ----------------------------------------------------------------
    802:     (44.388, 5.704,  2, None, "Montmaur, Hautes-Alpes, France"),
    3003203: (43.731, 0.866,  2, None, "Sarrant, Gers, France"),
    3003230: (43.633, 3.911,  2, None, "near Castelnau-le-Lez, France"),
    3155:    (45.090, 0.500,  2, None, "St-Germain-du-Salembre, Dordogne, France"),

    # Germany ---------------------------------------------------------------
    3003351: (50.639, 6.714,  3, None, "Billig/Euskirchen, Germany"),

    # UK --------------------------------------------------------------------
    545:  (51.338, 0.742,  3, "https://en.wikipedia.org/wiki/Teynham", "Teynham, Kent, UK"),

    # Egypt / Nile Delta ---------------------------------------------------
    3002805: (30.065, 31.217, 2, None, "el-Warrak, S Nile Delta, Egypt"),
}

def in_bounds(lat, lng):
    return 5.0 <= lat <= 65.0 and -20.0 <= lng <= 105.0

with open(DB_PATH, encoding='utf-8') as f:
    raw = json.load(f)

data = raw['records']
by_id = {r['data_id']: r for r in data}

hits = 0
skipped = 0
for data_id, (lat, lng, conf, url, note) in FINDS.items():
    rec = by_id.get(data_id)
    if rec is None:
        print(f"  WARN: data_id={data_id} not found in DB")
        continue
    if rec.get('lat'):
        print(f"  SKIP: {data_id} {rec.get('latin_std',rec.get('latin',''))} already has coords {rec['lat']},{rec['lng']}")
        skipped += 1
        continue
    if not in_bounds(lat, lng):
        print(f"  SKIP: {data_id} out of bounds {lat},{lng}")
        continue

    print(f"  SET:  {str(data_id):10} {rec.get('latin_std',rec.get('latin',''))[:28]:28s} -> {lat},{lng}  gc={conf}  [{note}]")
    if not DRY_RUN:
        rec['lat'] = lat
        rec['lng'] = lng
        rec['geocoding_confidence'] = conf
        if url:
            rec['wiki_url'] = url
    hits += 1

print(f"\nTotal: {hits} records updated, {skipped} skipped (already located)")

if not DRY_RUN and hits > 0:
    # Backup
    ts = datetime.datetime.now().strftime("%Y-%m-%d")
    backup = DB_PATH.replace('.json', f'_backup_{ts}_pre_ai.json')
    shutil.copy(DB_PATH, backup)
    print(f"Backup: {backup}")
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)
    print("DB written.")
else:
    print("DRY RUN - no changes written.")
