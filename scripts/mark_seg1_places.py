#!/usr/bin/env python3
"""Mark Segment I places in review_places_db.json.

Criteria for tabula_segment = 1:
  - Source: tabula (scraped from tabula-peutingeriana.de)
  - No ulm_id (not identified on the surviving parchment by ULM)
  - No miller_rect_x1 (not calibrated on the existing map image)
  - Geographic coordinates in Segment I territory:
      Britain (lat > 50, lng < 3)
      Iberia  (lat 35-45, lng < -3)
      Morocco Atlantic coast (lat < 36, lng < -3)
"""

import json
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "public" / "data" / "review_places_db.json"


def is_seg1_area(lat, lng):
    lat, lng = float(lat), float(lng)
    if lat > 50 and lng < 3:                return True  # Britain
    if lat > 35 and lat < 45 and lng < -3:  return True  # Iberia
    if lat < 36 and lng < -3:               return True  # Morocco Atlantic
    return False


def main():
    data = json.loads(DB_PATH.read_text(encoding="utf-8"))
    records = data["records"]

    updated = 0
    for r in records:
        if not r.get("lat") or not r.get("lng"):
            continue
        if r.get("ulm_id"):
            continue  # in ULM DB = identified on surviving parchment
        if r.get("miller_rect_x1"):
            continue  # calibrated = locatable on existing map image
        if is_seg1_area(r["lat"], r["lng"]):
            if r.get("tabula_segment") != 1:
                r["tabula_segment"] = 1
                updated += 1
                print(f"  * {r.get('latin', '?'):40s} ({r.get('country', '?')})")

    DB_PATH.write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"\nDone. {updated} records marked as tabula_segment=1.")


if __name__ == "__main__":
    main()
