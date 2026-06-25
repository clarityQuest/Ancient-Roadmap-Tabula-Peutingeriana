#!/usr/bin/env python3
"""Import OmnesViae OVPlace Segment I entries into review_places_db.json.

Criteria:
  - OVPlace entries (not TPPlace) — reconstructed from non-Tabula ancient sources
  - Geographic Segment I area:
      Britain (lat > 50, lng < 3)
      Iberia  (lat 35-45, lng < -3)
      Morocco Atlantic (lat < 36, lng < -3)
  - Not already in DB by record_id
  - Not a duplicate of an existing Seg I tabula-source record by name
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OV_PATH = ROOT / "scripts" / "omnesviae_sample.json"
DB_PATH = ROOT / "public" / "data" / "review_places_db.json"


def is_seg1_area(lat, lng):
    """All geographic territory on the lost Tabula Segment I.
    OmnesViae marks these places grey (OVPlace = reconstructed, not on surviving parchment).
    Covers all of Iberia (including Mediterranean coast), Britain, Mauretania Tingitana (Morocco),
    Pyrenees passes, and SW France (Aquitania). Algeria (Mauretania Caesariensis) excluded —
    that region appears on the surviving Tabula Segment II.
    """
    lat, lng = float(lat), float(lng)
    if lat > 49 and lng < 3:                return True  # Britain
    if lat > 35 and lat < 49 and lng < 4:   return True  # All Iberia + Pyrenees + SW France
    if lat < 36 and lng < -2:               return True  # Morocco / Mauretania Tingitana
    return False


def derive_type(symbol):
    s = (symbol or "").strip()
    if s == "Q":  return "spa"
    if s == "O":  return "major_city"
    return "road_station"


def guess_country(lat, lng):
    lat, lng = float(lat), float(lng)
    if lat > 49 and lng < 3:               return "GB"
    if lat > 43 and lat < 49 and lng < 4:  return "FR"
    if lat > 35 and lat < 44 and lng < -9: return "PT"
    if lat > 35 and lat < 44:              return "ES"
    if lat < 36:                           return "MA"
    return ""


def main():
    ov_data = json.loads(OV_PATH.read_text(encoding="utf-8"))
    db_data = json.loads(DB_PATH.read_text(encoding="utf-8"))
    records = db_data["records"]

    db_ids = {r.get("record_id", "") for r in records}
    existing_seg1_names = set()
    for r in records:
        if r.get("tabula_segment") == 1:
            n = (r.get("latin_std") or r.get("latin") or "").strip().lower()
            if n:
                existing_seg1_names.add(n)

    added = 0
    skipped_dup = 0
    for entry in ov_data.get("@graph", []):
        if "OVPlace" not in entry.get("@id", ""):
            continue
        lat = entry.get("lat")
        lng = entry.get("lng")
        if lat is None or lng is None:
            continue
        if not is_seg1_area(lat, lng):
            continue

        record_id = "OV:" + entry["@id"]
        if record_id in db_ids:
            skipped_dup += 1
            continue

        label = (entry.get("label") or "").strip()
        if label.lower() in existing_seg1_names:
            skipped_dup += 1
            continue

        modern = entry.get("modern") or entry.get("classic") or None
        if modern and modern.strip() in ("?", ""):
            modern = None

        # Extract numeric ID from OVPlace123
        ov_id_str = entry["@id"].split("OVPlace")[-1]
        try:
            data_id = int(ov_id_str)
        except ValueError:
            data_id = None

        rec = {
            "record_id": record_id,
            "source": "omnesviae",
            "data_id": data_id,
            "latin": label,
            "latin_std": label,
            "modern_preferred": modern,
            "type": derive_type(entry.get("symbol")),
            "lat": lat,
            "lng": lng,
            "tabula_segment": 1,
            "country": guess_country(lat, lng),
        }
        records.append(rec)
        db_ids.add(record_id)
        existing_seg1_names.add(label.lower())
        added += 1

    db_data["records"] = records
    if "meta" in db_data:
        db_data["meta"]["total"] = len(records)

    DB_PATH.write_text(
        json.dumps(db_data, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"Done. {added} records added, {skipped_dup} duplicates skipped.")
    seg1_total = sum(1 for r in records if r.get("tabula_segment") == 1)
    print(f"Total Segment I records in DB: {seg1_total}")


if __name__ == "__main__":
    main()
