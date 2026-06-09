#!/usr/bin/env python3
"""
Enriches review_places_db.json with Wikipedia/Nominatim coordinates
for road_station records that currently lack lat/lng.

Strategies tried in order per record (stops at first hit):
  1. Latin name -> Wikipedia (EN/DE), with suffix variants and "Ad X" -> "X"
  2. modern_tabula -> Wikipedia, then Nominatim/OSM
  3. modern_preferred -> extract proper nouns -> Wikipedia, then Nominatim
  4. Latin name -> Nominatim (country-scoped if known)

Validation gates (must pass ALL):
  A. Geographic bounds: lat 5-65 N, lng -20-105 E (covers TP region)
  B. Short names (<6 chars) or title mismatch: article must contain
     ancient/classical context keywords
  (Nominatim hits skip gate B since they are modern place lookups.)

Usage:
  python scripts/enrich_wiki_coords.py [--dry-run]
"""

import io, json, re, sys, time, urllib.parse, urllib.request, unicodedata
from datetime import date
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              errors="replace", line_buffering=True)

DB_PATH = Path(__file__).parent.parent / "public" / "data" / "review_places_db.json"
WIKI_RATE  = 0.4   # s between Wikipedia requests
NOMIN_RATE = 1.1   # s between Nominatim requests (their policy: 1 req/s)
WIKIS = ["en", "de"]
UA    = "TabulaPeutingerianaBot/1.0 (https://tabula-peutingeriana.de)"

DRY_RUN = "--dry-run" in sys.argv

GEO_LAT_MIN, GEO_LAT_MAX =  5.0, 65.0
GEO_LNG_MIN, GEO_LNG_MAX = -20.0, 105.0

ANCIENT_KW = {
    "ancient", "roman", "romano", "latin", "greek", "classical",
    "antique", "antiquit", "antiken", "antike", "romisch", "romischen",
    "archaeological", "archaeolog", "archaolog", "historisch",
    "byzantine", "hellenistic", "hellenist", "celtic", "iberian",
    "phoenician", "persian", "ottoman", "medieval", "mittelalter",
    "colony", "colonia", "settlement", "founded", "gegründet",
    "ruins", "ruinen", "excavat", "peutinger", "tabula", "itinerarium",
    "antonine", "caravanserai", "miliary",
}

# Map DB country codes -> Nominatim ISO-2 codes
# DB mixes auto-plate codes (I, D, F…), ISO-2, and ISO-3
COUNTRY_MAP = {
    # Auto plate / legacy single-letter
    "A": "at", "B": "be", "D": "de", "E": "es",
    "F": "fr", "H": "hu", "I": "it", "L": "lu",
    "P": "pt",
    # ISO-2
    "AF": "af", "AL": "al", "AM": "am", "AT": "at",
    "AZ": "az", "BA": "ba", "BE": "be", "BG": "bg",
    "CH": "ch", "CN": "cn", "CY": "cy", "DE": "de",
    "DZ": "dz", "EG": "eg", "ES": "es", "ET": "et",
    "FR": "fr", "GB": "gb", "GE": "ge", "GR": "gr",
    "HR": "hr", "HU": "hu", "IL": "il", "IN": "in",
    "IQ": "iq", "IR": "ir", "IT": "it", "JO": "jo",
    "LB": "lb", "LU": "lu", "LY": "ly", "MA": "ma",
    "ME": "me", "MK": "mk", "NL": "nl", "PK": "pk",
    "PT": "pt", "RL": "lb", "RO": "ro", "RS": "rs",
    "RU": "ru", "SI": "si", "SK": "sk", "SY": "sy",
    "TN": "tn", "TR": "tr", "UA": "ua", "UK": "gb",
    "XK": "xk", "YU": "rs",
    # ISO-3 codes used in DB
    "AFG": "af", "ARM": "am", "AUT": "at", "BIH": "ba",
    "IND": "in", "IRQ": "iq", "JOR": "jo", "LAR": "ly",
    "MNE": "me", "RKS": "xk", "RUS": "ru", "SLO": "si",
    "SYR": "sy",
}

_MACRON_MAP = str.maketrans("āēīōūĀĒĪŌŪ", "aeiouAEIOU")

# ── Shared helpers ───────────────────────────────────────────────────────────

def in_bounds(lat, lng):
    return GEO_LAT_MIN <= lat <= GEO_LAT_MAX and GEO_LNG_MIN <= lng <= GEO_LNG_MAX

def has_ancient_context(text):
    low = text.lower()
    return any(kw in low for kw in ANCIENT_KW)

def ascii_norm(s):
    n = s.translate(_MACRON_MAP)
    n = unicodedata.normalize("NFD", n)
    return "".join(c for c in n if unicodedata.category(c) != "Mn").lower()

def http_get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=12) as r:
        return json.loads(r.read().decode("utf-8"))


# ── Wikipedia ────────────────────────────────────────────────────────────────

def _wiki_fetch(lang, title):
    params = urllib.parse.urlencode({
        "action": "query", "format": "json", "redirects": "1",
        "prop": "coordinates|extracts",
        "titles": title,
        "exintro": "1", "exchars": "500", "explaintext": "1",
    })
    return http_get(f"https://{lang}.wikipedia.org/w/api.php?{params}")

def wiki_coords(lang, title, search_clean, require_ancient=False):
    """Return (lat, lng, url) or None. require_ancient skips bounds-only accepts."""
    try:
        data = _wiki_fetch(lang, title)
    except Exception:
        return None
    pages = data.get("query", {}).get("pages", {})
    for pid, page in pages.items():
        if pid == "-1":
            return None
        actual = page.get("title", title)
        coords = page.get("coordinates", [])
        primary = next((c for c in coords if c.get("primary")), None) or (coords[0] if coords else None)
        if not primary:
            return None
        lat, lng = round(primary["lat"], 6), round(primary["lon"], 6)
        if not in_bounds(lat, lng):
            return None
        # Validate for ambiguous cases
        at = ascii_norm(actual)
        sc = ascii_norm(search_clean)
        mismatch = at not in sc and sc not in at
        short    = len(sc) < 6 or len(at) < 6
        if require_ancient or short or mismatch:
            extract = page.get("extract", "")
            if not has_ancient_context(extract):
                return None
        url = f"https://{lang}.wikipedia.org/wiki/{urllib.parse.quote(actual.replace(' ', '_'))}"
        return lat, lng, url
    return None

def try_wiki(title, search_clean, require_ancient=False):
    for lang in WIKIS:
        r = wiki_coords(lang, title, search_clean, require_ancient)
        time.sleep(WIKI_RATE)
        if r:
            return r, f"wiki/{lang}"
    return None, None

def latin_candidates(latin):
    """Yield (title, search_clean) pairs for a Latin place name."""
    clean = re.sub(r'\s*\(\d+\)\s*$', '', latin).strip()
    clean = re.sub(r'\?+', '', clean).strip()
    clean = re.sub(r'\s+', ' ', clean)
    asc = ascii_norm(clean)

    seen = set()
    def emit(t, sc):
        if t not in seen:
            seen.add(t)
            yield t, sc

    for n in dict.fromkeys([clean, clean.title() if clean != clean.title() else None]):
        if not n: continue
        yield from emit(n, n)
        yield from emit(n + " (ancient)", n)
        yield from emit(n + " (city)", n)
        yield from emit(n + " (ancient city)", n)

    m = re.match(r'^(?:Ad|In|Ex)\s+(.+)', clean, re.I)
    if m:
        bare = m.group(1).strip()
        yield from emit(bare, bare)
        yield from emit(bare + " (ancient)", bare)


# ── Nominatim / OSM ──────────────────────────────────────────────────────────

_nomin_last = [0.0]

def nominatim(name, country_code="", require_mapped_country=False):
    """
    Return (lat, lng, osm_url) or None.
    require_mapped_country=True: skip entirely if country_code not in COUNTRY_MAP
    (prevents unscoped searches that match anywhere in the world).
    Rejects administrative boundaries (countries, states) — too coarse.
    """
    iso = COUNTRY_MAP.get((country_code or "").upper(), "")
    if require_mapped_country and not iso:
        return None

    elapsed = time.time() - _nomin_last[0]
    if elapsed < NOMIN_RATE:
        time.sleep(NOMIN_RATE - elapsed)
    _nomin_last[0] = time.time()

    params = {"q": name, "format": "json", "limit": "5",
              "accept-language": "en"}
    if iso:
        params["countrycodes"] = iso
    try:
        results = http_get("https://nominatim.openstreetmap.org/search?" +
                           urllib.parse.urlencode(params))
    except Exception:
        return None
    for r in results:
        # Skip large administrative boundaries (countries, states, regions)
        if r.get("type") == "administrative" and r.get("class") == "boundary":
            rank = int(r.get("place_rank", 0))
            if rank <= 8:   # rank 2=country, 4=state, 6=county, 8=city
                continue
        lat, lng = round(float(r["lat"]), 6), round(float(r["lon"]), 6)
        if in_bounds(lat, lng):
            osm_url = (f"https://www.openstreetmap.org/"
                       f"{r.get('osm_type','node')}/{r.get('osm_id','')}")
            return lat, lng, osm_url
    return None


# ── modern_preferred parser ──────────────────────────────────────────────────

_STOP = {
    "am", "im", "in", "an", "bei", "von", "vom", "des", "der", "die", "das",
    "östl", "westl", "nördl", "südl", "östlich", "westlich",
    "near", "by", "at", "of", "the", "and", "or", "oder", "et",
    "sw", "nw", "ne", "se", "north", "south", "east", "west",
    "fluss", "river", "lake", "see", "km", "di", "de", "du", "le", "la",
    "between", "und", "Fluss", "River",
}

def extract_proper_nouns(text):
    """
    Extract capitalized word sequences from modern_preferred text.
    Handles: "? bei Elecik oder Kalecik ?", "(near Hippo Regius) (Barrington)",
             "Mugnana? (Greve in Chianti) [5] / bei Figline Valdarno [3]"
    """
    # Remove citation markers
    t = re.sub(r'\((?:Barrington|Miller|Tabula|OmnesViae|ItAnt|TIR|RE)\)', '', text, flags=re.I)
    t = re.sub(r'\[\d+(?:,\s*\d+)*\]', '', t)

    # Split alternatives on "/"
    parts = re.split(r'\s*/\s*', t)
    results = []

    for part in parts:
        # Strip content inside parentheses into its own candidate
        paren_contents = re.findall(r'\(([^)]{3,40})\)', part)
        base = re.sub(r'\([^)]*\)', ' ', part)

        for segment in [base] + paren_contents:
            seg = segment.replace('?', '').strip()
            # Remove distance prefix: "3 km östl. von"
            seg = re.sub(r'^\d+\s*km\s+\S+\s+(?:von|of|from)\s+', '', seg, flags=re.I)
            seg = re.sub(r'^\d+\s*km\s+', '', seg, flags=re.I)

            words = seg.split()
            phrase = []
            for w in words:
                clean = re.sub(r'[^\w\-]', '', w)
                wl = clean.lower().rstrip('.')
                if not clean:
                    if phrase:
                        results.append(' '.join(phrase)); phrase = []
                    continue
                if wl in _STOP:
                    if phrase:
                        results.append(' '.join(phrase)); phrase = []
                elif clean[0].isupper() or (phrase and clean[0].islower() and len(clean) > 2):
                    phrase.append(clean)
                else:
                    if phrase:
                        results.append(' '.join(phrase)); phrase = []
            if phrase:
                results.append(' '.join(phrase))

    # Deduplicate, minimum length 4
    seen = set()
    out = []
    for r in results:
        r = r.strip()
        rl = r.lower()
        if len(r) >= 4 and rl not in seen:
            seen.add(rl)
            out.append(r)
    return out


# ── Skip list ────────────────────────────────────────────────────────────────

_SKIP_RE = re.compile(
    r'^\[|^-$'
    r'|^(?:unnamed|illegible|isolated|TPPlace\d)',
    re.I,
)
def should_skip(name):
    return bool(_SKIP_RE.match(name.strip()))


# ── Per-record search orchestrator ──────────────────────────────────────────

def find_coords(rec):
    """
    Return (lat, lng, url, strategy_label) or None.
    Tries all strategies, stops at first validated hit.
    """
    latin      = (rec.get("latin_std") or rec.get("latin") or "").strip()
    mod_tab    = (rec.get("modern_tabula") or "").strip()
    mod_pref   = (rec.get("modern_preferred") or "").strip()
    country    = (rec.get("country") or "").strip()

    # ── Strategy 1: Latin name -> Wikipedia ──────────────────────────────
    for title, sc in latin_candidates(latin):
        r, src = try_wiki(title, sc)
        if r: return (*r, src + "/latin")

    # ── Strategy 2: modern_tabula -> Wikipedia, then Nominatim ───────────
    if mod_tab and mod_tab not in ('?',):
        r, src = try_wiki(mod_tab, mod_tab, require_ancient=False)
        if r: return (*r, src + "/mod_tabula")
        nr = nominatim(mod_tab, country)
        if nr: return (*nr, "osm/mod_tabula")

    # ── Strategy 3: modern_preferred noun mining ─────────────────────────
    if mod_pref and mod_pref not in ('?',):
        nouns = extract_proper_nouns(mod_pref)
        for noun in nouns:
            # Wikipedia first (requires ancient context since these may be modern)
            r, src = try_wiki(noun, noun, require_ancient=True)
            if r: return (*r, src + f"/mod_pref:{noun}")
        for noun in nouns:
            # Nominatim for modern place names
            nr = nominatim(noun, country)
            if nr: return (*nr, f"osm/mod_pref:{noun}")

    # ── Strategy 4: Latin -> Nominatim (only when country is mapped) ─────
    if latin:
        clean_lat = re.sub(r'\s*\(\d+\)\s*$', '', latin).strip()
        clean_lat = ascii_norm(clean_lat)
        nr = nominatim(clean_lat, country, require_mapped_country=True)
        if nr: return (*nr, "osm/latin")

    return None


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    db      = json.loads(DB_PATH.read_text(encoding="utf-8"))
    records = db["records"]

    if not DRY_RUN:
        bak = DB_PATH.parent / f"review_places_db_backup_{date.today()}.json"
        if not bak.exists():
            bak.write_text(json.dumps(db, ensure_ascii=False, separators=(",", ":")),
                           encoding="utf-8")
            print(f"Backup -> {bak.name}")

    targets = [r for r in records
               if r.get("type") == "road_station" and r.get("lat") is None]
    print(f"Unlocated road_stations: {len(targets)}")
    print(f"Bounds: lat {GEO_LAT_MIN}-{GEO_LAT_MAX}, lng {GEO_LNG_MIN}-{GEO_LNG_MAX}")

    updated = skipped = not_found = 0

    for i, rec in enumerate(targets):
        name = (rec.get("latin_std") or rec.get("latin") or "").strip()
        did  = rec["data_id"]
        tag  = f"[{i+1}/{len(targets)}] did={did:7} {name[:30]:<30}"

        if should_skip(name):
            skipped += 1
            continue

        result = find_coords(rec)

        if result:
            lat, lng, url, strategy = result
            is_wiki = strategy.startswith("wiki/")
            # wiki_confidence (1-5): only for Wikipedia article matches
            # geocoding_confidence (1-3): only for Nominatim/OSM matches
            #   3 = via modern_preferred / modern_tabula hint (known modern name)
            #   2 = via mod_pref noun but weaker (single extracted word)
            #   1 = via raw Latin name lookup
            if is_wiki:
                wiki_conf = 3
                geo_conf  = None
            else:
                wiki_conf = None
                if "mod_tabula" in strategy:
                    geo_conf = 3
                elif "mod_pref" in strategy:
                    geo_conf = 3
                else:
                    geo_conf = 1   # osm/latin
            print(f"{tag} -> {lat:.4f},{lng:.4f}  [{strategy}]"
                  f"  {'wiki_conf=' + str(wiki_conf) if wiki_conf else 'geo_conf=' + str(geo_conf)}"
                  f"  {url}")
            if not DRY_RUN:
                rec["lat"]      = lat
                rec["lng"]      = lng
                rec["wiki_url"] = url
                if wiki_conf is not None:
                    rec["wiki_confidence"]     = wiki_conf
                if geo_conf is not None:
                    rec["geocoding_confidence"] = geo_conf
            updated += 1
            if updated % 50 == 0 and not DRY_RUN:
                DB_PATH.write_text(
                    json.dumps(db, ensure_ascii=False, separators=(",", ":")),
                    encoding="utf-8")
                print(f"  -- progress saved ({updated} so far) --")
        else:
            print(f"{tag} -> not found")
            not_found += 1

    if not DRY_RUN:
        DB_PATH.write_text(
            json.dumps(db, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8")

    print(f"\nDone.  updated={updated}  skipped={skipped}  not_found={not_found}")

if __name__ == "__main__":
    main()
