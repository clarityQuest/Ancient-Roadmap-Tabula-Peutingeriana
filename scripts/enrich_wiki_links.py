"""
enrich_wiki_links.py
--------------------
Add wiki_url + wiki_confidence=3 to road_station records that already have
lat/lng but have no wiki_url.  Coordinates are NOT changed.

Strategy per record:
  1. Try latin_std name on Wikipedia (en + country-language)
  2. Try proper nouns extracted from modern_preferred on Wikipedia
  Accept if Wikipedia article has coords within MAX_DIST_KM of our DB coords.

Usage:
  python scripts/enrich_wiki_links.py [--dry-run] [--limit N]
"""
import json, sys, io, math, re, time, os, urllib.parse, urllib.request, shutil, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

DB_PATH  = "public/data/review_places_db.json"
DRY_RUN  = "--dry-run" in sys.argv
LIMIT    = next((int(sys.argv[sys.argv.index("--limit")+1])
                 for i, a in enumerate(sys.argv) if a == "--limit"), None)
MAX_DIST_KM = 60   # accept Wikipedia article if its coords are within this distance

# ── Country → Wikipedia languages to try (in order) ─────────────────────────
COUNTRY_LANGS = {
    "D":   ["de", "en"],
    "AUT": ["de", "en"],
    "A":   ["de", "en"],
    "CH":  ["de", "fr", "it", "en"],
    "I":   ["it", "en"],
    "IT":  ["it", "en"],
    "F":   ["fr", "en"],
    "FR":  ["fr", "en"],
    "TN":  ["fr", "en"],
    "DZ":  ["fr", "en"],
    "MA":  ["fr", "en"],
    "LAR": ["fr", "en"],
    "LY":  ["en"],
    "GR":  ["el", "en"],
    "TR":  ["tr", "en"],
    "RO":  ["ro", "en"],
    "BG":  ["bg", "en"],
    "HR":  ["hr", "en"],
    "RS":  ["sr", "en"],
    "HU":  ["hu", "en"],
    "SK":  ["sk", "en"],
    "SI":  ["sl", "en"],
    "SYR": ["ar", "en"],
    "SY":  ["ar", "en"],
    "JOR": ["ar", "en"],
    "EG":  ["fr", "ar", "en"],
    "ET":  ["fr", "ar", "en"],
    "IL":  ["he", "en"],
    "IRQ": ["ar", "en"],
    "IR":  ["fa", "en"],
    "ARM": ["hy", "en"],
    "AZ":  ["az", "en"],
    "GE":  ["ka", "en"],
}
DEFAULT_LANGS = ["en"]

UA = "TabulaPeutingerianaEnricher/1.0 (tabula-peutingeriana.com)"


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    d = math.radians
    dlat = d(lat2 - lat1)
    dlon = d(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(d(lat1))*math.cos(d(lat2))*math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(a))


def http_get(url, _retries=3):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(_retries):
        try:
            with urllib.request.urlopen(req, timeout=12) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 3 * (attempt + 1)
                time.sleep(wait)
            else:
                return None
        except Exception:
            time.sleep(1)
    return None


def wiki_search(lang, title):
    """Return (lat, lng, canonical_url) or None for the best Wikipedia match."""
    params = urllib.parse.urlencode({
        "action": "query",
        "titles": title,
        "prop": "coordinates|pageprops",
        "redirects": 1,
        "format": "json",
    })
    data = http_get(f"https://{lang}.wikipedia.org/w/api.php?{params}")
    if not data:
        return None
    pages = data.get("query", {}).get("pages", {})
    for pid, page in pages.items():
        if pid == "-1":
            continue
        coords = page.get("coordinates", [])
        if not coords:
            continue
        lat = coords[0]["lat"]
        lng = coords[0]["lon"]
        actual = page.get("title", title)
        url = f"https://{lang}.wikipedia.org/wiki/{urllib.parse.quote(actual.replace(' ', '_'))}"
        return (lat, lng, url)
    return None


def wiki_search_by_query(lang, query):
    """Full-text search: returns (lat, lng, url) for the first hit with coordinates."""
    params = urllib.parse.urlencode({
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": 3,
        "format": "json",
    })
    data = http_get(f"https://{lang}.wikipedia.org/w/api.php?{params}")
    if not data:
        return None
    hits = data.get("query", {}).get("search", [])
    for hit in hits:
        r = wiki_search(lang, hit["title"])
        if r:
            return r
    return None


def clean_modern(text):
    """Extract clean search candidates from modern_preferred text."""
    # Strip parenthetical sources like (Miller) (Barrington) (?)
    text = re.sub(r'\s*\((Miller|Barrington|DNP|RE|TIR|[A-Z]{1,4}|\?)\)', '', text)
    # Split on / and common separators
    parts = re.split(r'[/·;,]|bei |near |und |and |oder |or |bzw\.|vlt\.?|=|–|-', text)
    # Return non-empty, non-trivial parts
    results = []
    for p in parts:
        p = p.strip().strip('[]().')
        if len(p) > 3 and not p.startswith('zw.'):
            results.append(p)
    return results


def find_wiki(rec):
    """Try to find a Wikipedia URL for a located-but-unlinked road station.
    Returns (url, dist_km) or None.
    """
    lat_db = rec["lat"]
    lng_db = rec["lng"]
    country = rec.get("country", "")
    langs = COUNTRY_LANGS.get(country, DEFAULT_LANGS)

    latin = (rec.get("latin_std") or rec.get("latin") or "").strip()
    mod_pref = (rec.get("modern_preferred") or "").strip()

    candidates = []  # list of (title, lang)

    # Candidate 1: latin name in each language
    if latin and len(latin) > 3:
        for lang in langs:
            candidates.append((latin, lang))

    # Candidate 2: modern_preferred extracts
    for part in clean_modern(mod_pref)[:4]:
        for lang in langs:
            candidates.append((part, lang))

    seen = set()
    for title, lang in candidates:
        key = (title.lower(), lang)
        if key in seen:
            continue
        seen.add(key)

        result = wiki_search(lang, title)
        time.sleep(0.3)
        if result is None:
            continue

        w_lat, w_lng, url = result
        dist = haversine(lat_db, lng_db, w_lat, w_lng)
        if dist <= MAX_DIST_KM:
            return url, dist

    return None


# ── Main ──────────────────────────────────────────────────────────────────────
# Optional: filter to specific countries via --country D,AUT,A
COUNTRY_FILTER = None
for i, a in enumerate(sys.argv):
    if a == "--country" and i + 1 < len(sys.argv):
        COUNTRY_FILTER = set(sys.argv[i + 1].split(","))

with open(DB_PATH, encoding="utf-8") as f:
    raw = json.load(f)

targets = [
    r for r in raw["records"]
    if r.get("type") == "road_station"
    and r.get("lat")
    and not r.get("wiki_url")
    and (r.get("modern_preferred") or r.get("latin_std") or r.get("latin"))
    and (COUNTRY_FILTER is None or r.get("country") in COUNTRY_FILTER)
]

if LIMIT:
    targets = targets[:LIMIT]

print(f"Scanning {len(targets)} located road_stations without wiki_url …\n")

# Make backup once before any writes
if not DRY_RUN and targets:
    ts = datetime.datetime.now().strftime("%Y-%m-%d")
    backup = DB_PATH.replace(".json", f"_backup_{ts}_pre_wikilinks.json")
    if not os.path.exists(backup):
        shutil.copy(DB_PATH, backup)
        print(f"Backup: {backup}\n")

def save_db():
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)

SAVE_EVERY = 10
hits = 0
for i, rec in enumerate(targets):
    name = rec.get("latin_std") or rec.get("latin") or "?"
    country = rec.get("country", "?")

    result = find_wiki(rec)
    time.sleep(1.0)  # 1 s between stations; per-request retry handles 429s

    if result:
        url, dist = result
        print(f"  HIT  {rec['data_id']:6} {name[:26]:26} [{country}] -> {url}  ({dist:.0f} km)")
        if not DRY_RUN:
            rec["wiki_url"] = url
            rec["wiki_confidence"] = 3
        hits += 1
        if not DRY_RUN and hits % SAVE_EVERY == 0:
            save_db()
            print(f"  ── checkpoint: {hits} hits saved ──")
    else:
        if i % 50 == 0:
            print(f"  ...  {i}/{len(targets)} scanned, {hits} hits so far")

print(f"\nDone: {hits} Wikipedia links found out of {len(targets)} stations scanned.")

if not DRY_RUN:
    if hits > 0:
        save_db()
        print("DB written.")
    else:
        print("Nothing to write.")
else:
    print("DRY RUN — no changes written.")
