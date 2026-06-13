#!/usr/bin/env python3
"""
Fetches OmnesViae road network data and extracts compact connection list
for use as a Leaflet overlay.

Source: https://github.com/renevoorburg/omnesviae
Output: public/data/omnesviae_roads.json

Schema:
  { "roads": [
      { "f": [lat, lng],   -- from coords
        "t": [lat, lng],   -- to coords
        "fl": "Roma",      -- from Latin label
        "tl": "Capua",     -- to Latin label
        "d": 12,           -- distance in Roman miles (omitted if absent)
        "w": true,         -- overWater (omitted if false)
        "r": true,         -- isReconstructed (omitted if false)
        "m": true,         -- crossesMountains (omitted if false)
        "x": true          -- extrapolated (skips unlocated intermediate places)
      }, ...
  ]}

Road-finding algorithm mirrors OmnesViae's GeoFeatures.php / Roads.php:
  1. Direct: both endpoints have coords (OmnesViae or DB fallback).
             DB-fallback roads capped at MAX_DB_FALLBACK_KM to avoid
             geographic artefacts from approximate coordinates.
  2. Extrapolated: 'from' has OmnesViae coords, 'to' is unlocated.
             Walk forward along linear road segments (stop at junctions)
             until the next OmnesViae-located place is found.
             Marked with "x": true (rendered at reduced opacity in UI).
"""

import json
import math
import os
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path

URL = "https://raw.githubusercontent.com/renevoorburg/omnesviae/master/public/data/omnesviae.json"
OUT = os.path.join(os.path.dirname(__file__), "..", "public", "data", "omnesviae_roads.json")
DB  = os.path.join(os.path.dirname(__file__), "..", "public", "data", "review_places_db.json")

# DB-fallback roads with geographic distance above this threshold are dropped.
# OmnesViae-verified coords are trusted at any distance; DB coords are
# approximate and can zigzag when the modern positions don't match TP road order.
MAX_DB_FALLBACK_KM = 400


def haversine_km(lat1, lng1, lat2, lng2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlng / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


def load_db_coords(db_path):
    """Build TPPlace-URI → {lat, lng, label} from review_places_db.json."""
    db_coords = {}
    try:
        raw = json.loads(Path(db_path).read_text(encoding="utf-8"))
        records = raw["records"] if isinstance(raw, dict) else raw
    except Exception as e:
        print(f"Warning: could not load DB fallback ({e})", file=sys.stderr)
        return db_coords
    for rec in records:
        did = rec.get("data_id")
        if not isinstance(did, int):
            continue
        lat = rec.get("lat")
        lng = rec.get("lng")
        if lat is None or lng is None:
            continue
        uri = f"https://omnesviae.org/#TPPlace{did}"
        label = rec.get("latin_std") or rec.get("latin") or ""
        gc = int(rec.get("geocoding_confidence") or 0)
        db_coords[uri] = {"lat": float(lat), "lng": float(lng), "label": label, "gc": gc}
    return db_coords


def main():
    print(f"Fetching {URL} ...")
    with urllib.request.urlopen(URL, timeout=30) as r:
        raw = r.read().decode("utf-8")
    data = json.loads(raw)
    print(f"Loaded {len(raw):,} bytes")

    # JSON-LD graph may be top-level list or under "@graph"
    if isinstance(data, dict) and "@graph" in data:
        items = data["@graph"]
    elif isinstance(data, list):
        items = data
    else:
        print("Unexpected JSON structure", file=sys.stderr)
        sys.exit(1)

    def resolve(ref):
        return ref["@id"] if isinstance(ref, dict) else str(ref)

    # ── OmnesViae place coords (ground-truth) ─────────────────────────────
    places = {}
    for item in items:
        if item.get("@type") != "Place":
            continue
        pid = item.get("@id", "")
        lat = item.get("lat")
        lng = item.get("lng")
        if not pid or lat is None or lng is None:
            continue
        places[pid] = {
            "lat": float(lat),
            "lng": float(lng),
            "label": item.get("label") or item.get("classic") or "",
        }
    print(f"OmnesViae places with coords: {len(places)}")

    # ── DB fallback coords ────────────────────────────────────────────────
    db_coords = load_db_coords(os.path.normpath(DB))
    db_only = {k: v for k, v in db_coords.items() if k not in places}
    print(f"DB fallback coords available: {len(db_coords)}  "
          f"({len(db_only)} not already in OmnesViae)")

    # ── Bidirectional adjacency from ALL TravelActions ────────────────────
    # Mirrors OmnesViae's routingMatrix used by nextPlaceOnRoad().
    adjacency = defaultdict(set)
    for item in items:
        if item.get("@type") != "TravelAction":
            continue
        from_list = item.get("from", [])
        to_list   = item.get("to",   [])
        if not from_list or not to_list:
            continue
        fid = resolve(from_list[0])
        tid = resolve(to_list[0])
        adjacency[fid].add(tid)
        adjacency[tid].add(fid)

    def next_ov_located_place_on_road(prev_id, curr_id):
        """Walk forward along a linear road until the next OmnesViae-located place.

        Mirrors OmnesViae Roads.php nextLocatedPlaceOnRoad():
          - only advances when current node has exactly 2 neighbors (no junction)
          - stops at dead ends, junctions, and detected loops
          - only considers OmnesViae coords as 'located' (not DB fallback)
        Returns the URI of the next OV-located place, or None.
        """
        prev, curr = prev_id, curr_id
        visited = {prev, curr}
        for _ in range(100):  # safety cap
            neighbors = adjacency.get(curr, set())
            other = neighbors - {prev}
            if len(other) != 1:          # junction or dead end — stop
                return None
            nxt = next(iter(other))
            if nxt in visited:           # loop detected
                return None
            if nxt in places:            # found an OV-located place
                return nxt
            visited.add(nxt)
            prev, curr = curr, nxt
        return None

    # ── Extract road connections ──────────────────────────────────────────
    roads = []
    skipped_ids = {}   # uri → label, for places with no coords at all
    n_direct_ov   = 0  # both endpoints have OV coords
    n_direct_db   = 0  # at least one endpoint uses DB fallback
    n_extrapolated = 0 # walk-forward extrapolated connections
    n_skipped_long = 0 # DB-fallback roads dropped due to distance cap
    n_skipped_nocoord = 0

    for item in items:
        if item.get("@type") != "TravelAction":
            continue
        from_list = item.get("from", [])
        to_list   = item.get("to",   [])
        if not from_list or not to_list:
            continue

        fid = resolve(from_list[0])
        tid = resolve(to_list[0])

        fp_ov = places.get(fid)
        tp_ov = places.get(tid)
        fp_db = db_coords.get(fid)
        tp_db = db_coords.get(tid)

        # Prefer our DB coord when it's high-confidence (gc≥2), even if OV has coords.
        # This ensures re-geocoded places update the road network.
        fp = (fp_db if (fp_db and fp_db.get("gc", 0) >= 2) else fp_ov) or fp_db
        tp = (tp_db if (tp_db and tp_db.get("gc", 0) >= 2) else tp_ov) or tp_db

        if fp and tp:
            # ── Direct connection ────────────────────────────────────────
            # Apply distance cap only for low-confidence DB fallbacks (gc<2).
            # High-confidence DB coords (gc≥2) and pure OV coords are trusted at any distance.
            fp_low_gc_fallback = (fp_ov is None) and fp is fp_db and fp_db.get("gc", 0) < 2
            tp_low_gc_fallback = (tp_ov is None) and tp is tp_db and tp_db.get("gc", 0) < 2
            if fp_low_gc_fallback or tp_low_gc_fallback:
                km = haversine_km(fp["lat"], fp["lng"], tp["lat"], tp["lng"])
                if km > MAX_DB_FALLBACK_KM:
                    n_skipped_long += 1
                    continue
                n_direct_db += 1
            elif (fp_ov is None) or (tp_ov is None):
                n_direct_db += 1
            else:
                n_direct_ov += 1

            road = {
                "f":  [fp["lat"], fp["lng"]],
                "t":  [tp["lat"], tp["lng"]],
                "fl": fp["label"],
                "tl": tp["label"],
            }

        elif fp and not tp:
            # ── Extrapolation: from has coords, to is totally unlocated ──
            # Walk forward along the linear road to the next OV-located place,
            # mirroring OmnesViae GeoFeatures.php / Roads.php logic.
            if not fp_ov:
                # Can only walk the OV graph if OV knows the from-place
                n_skipped_nocoord += 1
                continue
            next_id = next_ov_located_place_on_road(fid, tid)
            if not next_id:
                n_skipped_nocoord += 1
                if tid not in skipped_ids:
                    skipped_ids[tid] = ""
                continue
            np = places[next_id]
            n_extrapolated += 1
            road = {
                "f":  [fp["lat"],  fp["lng"]],
                "t":  [np["lat"],  np["lng"]],
                "fl": fp["label"],
                "tl": np["label"],
                "x":  True,
            }

        else:
            # from has no coords at all (or only DB with to missing) — skip
            n_skipped_nocoord += 1
            for pid in (fid, tid):
                if not (places.get(pid) or db_coords.get(pid)):
                    if pid not in skipped_ids:
                        skipped_ids[pid] = ""
            continue

        dist = item.get("dist")
        if dist is not None:
            road["d"] = dist
        if item.get("overWater"):
            road["w"] = True
        if item.get("isReconstructed"):
            road["r"] = True
        if item.get("crossesMountains"):
            road["m"] = True
        roads.append(road)

    # Enrich skipped_ids labels from OmnesViae Place items
    place_labels = {}
    for item in items:
        if item.get("@type") != "Place":
            continue
        pid = item.get("@id", "")
        if pid in skipped_ids:
            place_labels[pid] = (item.get("label") or item.get("classic")
                                 or item.get("name") or "")
    for pid in skipped_ids:
        skipped_ids[pid] = place_labels.get(pid, "")

    print(f"\nRoads: {len(roads)}")
    print(f"  OV direct:    {n_direct_ov}")
    print(f"  DB direct:    {n_direct_db}  (capped {n_skipped_long} >{MAX_DB_FALLBACK_KM}km)")
    print(f"  Extrapolated: {n_extrapolated}  (walk-forward through unlocated)")
    print(f"  Unresolvable: {n_skipped_nocoord}  ({len(skipped_ids)} unique missing places)")

    if skipped_ids:
        import io, sys as _sys
        out = io.TextIOWrapper(_sys.stdout.buffer, encoding="utf-8", errors="replace")
        out.write(f"\n{'='*60}\n")
        out.write(f"PLACES STILL MISSING COORDS ({len(skipped_ids)} unique IDs)\n")
        out.write(f"{'='*60}\n")
        for uri, label in sorted(skipped_ids.items()):
            if "#TPPlace" in uri:
                place_id = "TPPlace" + uri.split("#TPPlace")[-1]
            elif "#OVPlace" in uri:
                place_id = "OVPlace" + uri.split("#OVPlace")[-1]
            else:
                place_id = uri
            display = label if label else "(no label)"
            out.write(f"  {place_id:<16}  {display}\n")
        out.write(f"{'='*60}\n\n")
        out.flush()

    out_path = os.path.normpath(OUT)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"roads": roads}, f, separators=(",", ":"), ensure_ascii=False)

    size_kb = os.path.getsize(out_path) / 1024
    print(f"Written: {out_path}  ({size_kb:.0f} KB)")


if __name__ == "__main__":
    main()
