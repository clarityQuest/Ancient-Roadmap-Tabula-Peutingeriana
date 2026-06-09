"""
Second batch of AI+WebSearch geocoding for review_places_db.json.
"""
import json, sys, io, shutil, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

DB_PATH = "public/data/review_places_db.json"
DRY_RUN = "--dry-run" in sys.argv

FINDS = {
    # Italy -----------------------------------------------------------------
    1160: (43.602, 13.325, 3, None, "Chiaravalle, E of Jesi/Iesi, Marche, Italy"),
    1110: (43.150, 10.910, 2, None, "between Populonium and Siena, Via Aurelia, Italy"),
    1352: (43.350, 11.020, 2, None, "Viglione, Siena area, Tuscany, Italy"),  # Svblvbatia
    1607: (45.722, 15.944, 2, None, "road Neviodunum-Siscia, midpoint, Slovenia/Croatia"),

    # Slovenia / Croatia
    # (1607 already above)

    # Greece ----------------------------------------------------------------
    190:  (36.260, 9.170,  2, None, "between Uzappa and Zama Regia, Tunisia"),  # Seggo

    # Tunisia ---------------------------------------------------------------
    # 190 is Seggo in Tunisia (misplaced in Greece block above - corrected)

    # Turkey ----------------------------------------------------------------
    2519: (40.050, 39.100, 2, None, "W of Satala/Sadak, Gumushane, Turkey"),
    2101: (37.660, 30.380, 2, None, "Burnuk area, Burdur, Turkey"),
    2292: (40.190, 31.650, 2, None, "Devekse/Ekinli/Demiryurt area, Turkey"),  # Doganis
    2517: (41.750, 33.200, 2, None, "Ogutlu/Iskilor area, Kastamonu, Turkey"),  # Ziziola

    # Iran ------------------------------------------------------------------
    2508: (37.553, 45.076, 2, "https://en.wikipedia.org/wiki/Urmia", "Urmia/Orumiyeh, Iran"),
    2732: (37.447, 59.106, 2, "https://en.wikipedia.org/wiki/Dargaz", "Dargaz, Khorasan, Iran"),
    2748: (35.021, 50.357, 2, None, "Saveh (='Sewah' Miller), Iran"),

    # Libya -----------------------------------------------------------------
    3002763: (31.700, 24.000, 2, None, "between Catabathmus and Antipyrgos, Libya"),
    38:   (36.780, 7.050,  2, None, "SE Skikda/Rusicade, Algeria"),

    # Egypt -----------------------------------------------------------------
    365:  (30.780, 30.980, 2, None, "Gharbia/el-Qasaba el-Garbiya, Nile Delta, Egypt"),
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
        print(f"  SKIP: {data_id} {rec.get('latin_std',rec.get('latin',''))} already located")
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

print(f"\nTotal: {hits} records updated, {skipped} skipped")

if not DRY_RUN and hits > 0:
    ts = datetime.datetime.now().strftime("%Y-%m-%d")
    backup = DB_PATH.replace('.json', f'_backup_{ts}_pre_ai2.json')
    shutil.copy(DB_PATH, backup)
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)
    print(f"DB written. Backup: {backup}")
else:
    print("DRY RUN" if DRY_RUN else "Nothing to write.")
