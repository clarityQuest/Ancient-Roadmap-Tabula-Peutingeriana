"""
prepare_countries.py
--------------------
Download Natural Earth 110m countries GeoJSON and strip it down to only the
countries that have at least one Tabula Peutingeriana place in the DB.
Keeps only ISO_A2, ISO_A3, NAME properties to minimise file size.

Run once: python scripts/prepare_countries.py
Output:   public/data/countries.geojson
"""
import json, os, urllib.request

NE_URL  = ("https://raw.githubusercontent.com/nvkelso/natural-earth-vector"
           "/master/geojson/ne_110m_admin_0_countries.geojson")
DB_PATH  = "public/data/review_places_db.json"
OUT_PATH = "public/data/countries.geojson"

# Non-standard DB country codes → ISO 3166-1 alpha-2
DB_TO_ISO2 = {
    "D":"DE","I":"IT","F":"FR","A":"AT","AUT":"AT","CH":"CH","GB":"GB",
    "GR":"GR","TR":"TR","BG":"BG","HR":"HR","RS":"RS","HU":"HU","SK":"SK",
    "SI":"SI","SLO":"SI","RO":"RO","TN":"TN","DZ":"DZ","MA":"MA","LY":"LY",
    "LAR":"LY","EG":"EG","ET":"EG","SY":"SY","SYR":"SY","JO":"JO","JOR":"JO",
    "IL":"IL","IQ":"IQ","IRQ":"IQ","IR":"IR","ARM":"AM","AZ":"AZ","GE":"GE",
    "AL":"AL","MK":"MK","ME":"ME","MNE":"ME","BA":"BA","BIH":"BA","NL":"NL",
    "BE":"BE","B":"BE","PL":"PL","UA":"UA","RU":"RU","RUS":"RU","LB":"LB",
    "RL":"LB","XK":"XK","RKS":"XK","CY":"CY","LU":"LU","DK":"DK",
    "E":"ES","P":"PT","IN":"IN","IND":"IN","PK":"PK","PAK":"PK",
    "AF":"AF","AFG":"AF","LK":"LK","KZ":"KZ","TM":"TM","KG":"KG",
    "SD":"SD","CN":"CN","AM":"AM","AT":"AT","DE":"DE","IT":"IT",
    "FR":"FR","ES":"ES","PT":"PT","MD":"MD","YU":"RS","V":"VA","VA":"VA",
}

def db_to_iso2_set(code):
    result = set()
    for p in code.split("|"):
        p = p.strip()
        mapped = DB_TO_ISO2.get(p, p if len(p) == 2 else None)
        if mapped:
            result.add(mapped)
    return result

# ── Collect ISO2 codes that actually appear in the DB ────────────────────────
print("Loading DB …")
with open(DB_PATH, encoding="utf-8") as f:
    db = json.load(f)

iso2_with_places = set()
for r in db["records"]:
    if r.get("type") == "modern_state":
        continue
    if not r.get("lat"):
        continue
    country = r.get("country") or ""
    if country:
        iso2_with_places.update(db_to_iso2_set(country))

print(f"ISO2 codes with Tabula places ({len(iso2_with_places)}): {sorted(iso2_with_places)}")

# ── Download Natural Earth 110m countries ─────────────────────────────────────
print("\nDownloading Natural Earth 110m countries …")
req = urllib.request.Request(
    NE_URL,
    headers={"User-Agent": "TabulaPeutingerianaPrep/1.0 (tabula-peutingeriana.com)"}
)
with urllib.request.urlopen(req, timeout=60) as r:
    raw_geojson = json.loads(r.read().decode("utf-8"))

print(f"Downloaded {len(raw_geojson['features'])} features")

# ── Filter and slim down ──────────────────────────────────────────────────────
kept = []
for f in raw_geojson["features"]:
    props = f.get("properties", {})
    iso2  = props.get("ISO_A2", "") or ""
    iso3  = props.get("ISO_A3", "") or props.get("ADM0_A3", "") or ""
    name  = (props.get("NAME_EN") or props.get("NAME") or
             props.get("ADMIN") or iso2)

    # Kosovo: Natural Earth uses ISO_A2="-99" but ISO_A3="XKX"
    if iso3 in ("KOS", "XKX", "XKK") or props.get("NAME_EN") == "Kosovo":
        iso2 = "XK"

    if not iso2 or iso2 == "-99":
        continue
    if iso2 not in iso2_with_places:
        continue

    kept.append({
        "type": "Feature",
        "properties": {"ISO_A2": iso2, "ISO_A3": iso3, "NAME": name},
        "geometry": f["geometry"],
    })

print(f"Kept {len(kept)} countries")

# ── Write output ──────────────────────────────────────────────────────────────
out = {"type": "FeatureCollection", "features": kept}
with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, separators=(",", ":"))

size_kb = os.path.getsize(OUT_PATH) / 1024
print(f"\nWritten {OUT_PATH}  ({size_kb:.0f} KB)")
