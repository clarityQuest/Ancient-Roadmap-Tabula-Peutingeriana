"""
DB data corrections for Tabula Peutingeriana.
Run from project root: python scripts/db_updates.py
"""
import json
import os
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REVIEW_DB = os.path.join(ROOT, "public", "data", "review_places_db.json")
PLACES_DB = os.path.join(ROOT, "public", "data", "places.json")


def atomic_write(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def unwrap_records(data):
    """Return (records_list, wrapper_dict_or_None)."""
    if isinstance(data, list):
        return data, None
    if isinstance(data, dict) and "records" in data:
        return data["records"], data
    raise ValueError(f"Unexpected top-level JSON structure: {list(data.keys())[:5]}")


def update_review_db(records):
    changed = {
        "item4_fons":            0,
        "item5_spa":             0,
        "item6_city":            0,
        "item7_location":        0,
        "item8_presidio":        0,
        "item10_vbartum":        0,
        "item11_major_city":     0,
        "item14_port":           0,
    }
    new_records = []

    for r in records:
        did = r.get("data_id")
        typ = r.get("type", "")
        lat = (r.get("latin_std") or r.get("latin") or "").strip()

        # Item 4 — enrich "fons" (data_id 2041) → spa
        if did == 2041 and typ == "road_station":
            r["type"] = "spa"
            changed["item4_fons"] += 1

        # Item 5 — Ad Aquas (1741) and Aqve Ange (1400) → spa
        if did in (1741, 1400) and typ == "road_station":
            r["type"] = "spa"
            changed["item5_spa"] += 1

        # Item 6 — Turribus (2934) A-type vignette → city
        if did == 2934 and typ == "road_station":
            r["type"] = "city"
            changed["item6_city"] += 1

        # Item 7 — Coloniam Arcilaida (2150) wrong location
        if did == 2150:
            r["tabula_segment"] = 10
            r["tabula_row"]     = "b"
            r["tabula_col"]     = 1
            r["tabula_location"] = "Seg 10 b1"
            if "grid_col" in r: r["grid_col"] = 1
            if "grid_row" in r: r["grid_row"] = "b"
            changed["item7_location"] += 1

        # Item 8 — Presidio Silvani (269) temple → road_station
        if did == 269 and typ == "temple":
            r["type"] = "road_station"
            changed["item8_presidio"] += 1

        # Item 10 — Fluvius Vbartum (91588) simplify latin
        if did == 91588:
            r["latin"] = "Fluvius Vbartum"
            if r.get("latin_std") == "Fluvius Vbartum (Fluvius Ubartum)":
                r["latin_std"] = "Fluvius Vbartum"
            changed["item10_vbartum"] += 1

        # Item 11 — major_city → city (bulk)
        if typ == "major_city":
            r["type"] = "city"
            changed["item11_major_city"] += 1

        # Item 14 — Port* latin names → port
        if typ != "port" and lat.lower().startswith("port"):
            r["type"] = "port"
            changed["item14_port"] += 1

        new_records.append(r)

    # Determine next available data_id for new records
    max_id = max((r.get("data_id") or 0) for r in new_records if isinstance(r.get("data_id"), int))

    # Item 3 — Add "Ad Dianam" (ULM 922)
    existing_ulm_ids = {r.get("ulm_id") for r in new_records}
    if 922 not in existing_ulm_ids:
        max_id += 1
        new_records.append({
            "record_id": "TP:ULM:922",
            "source": "tabula",
            "data_id": max_id,
            "latin": "Ad Dianam",
            "latin_std": "Ad Dianam",
            "type": "temple",
            "ulm_id": 922,
            "tabula_segment": 6,
            "tabula_row": "b",
            "tabula_col": 3,
            "tabula_location": "Seg 6 b3",
            "match_status": "manual_add",
            "country": "AL",
            "ulm_img_url": "https://tp-online.ku.de/insetimages/TPPlace922insetneu.png",
        })
        print(f"  [item3] Added 'Ad Dianam' as data_id={max_id}")
    else:
        print("  [item3] 'Ad Dianam' (ulm_id=922) already present — skipped")

    # Item 15 — Add "Fluvius Ticenum" (ULM 2517)
    if 2517 not in existing_ulm_ids:
        max_id += 1
        new_records.append({
            "record_id": "TP:ULM:2517",
            "source": "tabula",
            "data_id": max_id,
            "latin": "Fluvius Ticenum",
            "latin_std": "Fluvius Ticenum",
            "modern_preferred": "Ticino",
            "type": "river",
            "ulm_id": 2517,
            "tabula_segment": 3,
            "tabula_row": "a",
            "tabula_col": 2,
            "tabula_location": "Seg 3 a2",
            "match_status": "manual_add",
            "country": "I",
            "ulm_img_url": "https://tp-online.ku.de/insetimages/TPPlace2517insetneu.png",
        })
        print(f"  [item15] Added 'Fluvius Ticenum' as data_id={max_id}")
    else:
        print("  [item15] 'Fluvius Ticenum' (ulm_id=2517) already present — skipped")

    return new_records, changed


def update_places_db(records):
    changed = {
        "item4_fons":        0,
        "item5_spa":         0,
        "item6_city":        0,
        "item11_major_city": 0,
        "item14_port":       0,
    }
    for r in records:
        lat = (r.get("latin") or "").strip()
        typ = r.get("type", "")

        # Item 4 — fons → spa
        if lat.lower() == "fons" and typ == "road_station":
            r["type"] = "spa"
            changed["item4_fons"] += 1

        # Item 5 — Ad Aquas / Aqve Ange → spa
        if lat in ("Ad Aquas", "Aqve Ange") and typ not in ("spa",):
            r["type"] = "spa"
            changed["item5_spa"] += 1

        # Item 6 — Turribus → city
        if lat in ("Turribus", "Tvrribus", "Tvrribvs") and typ == "road_station":
            r["type"] = "city"
            changed["item6_city"] += 1

        # Item 11 — major_city → city
        if typ == "major_city":
            r["type"] = "city"
            changed["item11_major_city"] += 1

        # Item 14 — Port* → port
        if typ != "port" and lat.lower().startswith("port"):
            r["type"] = "port"
            changed["item14_port"] += 1

    return records, changed


def main():
    print("Loading review_places_db.json …")
    review_raw = load(REVIEW_DB)
    review, review_wrapper = unwrap_records(review_raw)
    print(f"  {len(review)} records loaded")

    print("Loading places.json …")
    places_raw = load(PLACES_DB)
    places, places_wrapper = unwrap_records(places_raw)
    print(f"  {len(places)} records loaded")

    print("\nApplying review_places_db changes …")
    review, rc = update_review_db(review)
    for k, v in rc.items():
        if v:
            print(f"  [{k}] {v} record(s) changed")

    print("\nApplying places.json changes …")
    places, pc = update_places_db(places)
    for k, v in pc.items():
        if v:
            print(f"  [{k}] {v} record(s) changed")

    # Re-wrap and write
    if review_wrapper is not None:
        review_wrapper["records"] = review
        review_out = review_wrapper
    else:
        review_out = review

    if places_wrapper is not None:
        places_wrapper["records"] = places
        places_out = places_wrapper
    else:
        places_out = places

    print(f"\nWriting review_places_db.json ({len(review)} records) …")
    atomic_write(REVIEW_DB, review_out)

    print(f"Writing places.json ({len(places)} records) …")
    atomic_write(PLACES_DB, places_out)

    print("\nDone.")


if __name__ == "__main__":
    main()
