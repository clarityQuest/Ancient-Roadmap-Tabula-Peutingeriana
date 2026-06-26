#!/usr/bin/env python3
"""Migrate OVPlace Seg I data_ids to 10,000,000 + numeric_ov_id.

Reason: OVPlace numeric IDs (1–558) collide with TPPlace numeric IDs stored in the same
data_id field. For example, OVPlace79 (Memoriana, Spain, Seg I) and TPPlace79 (Cicisa,
Tunisia, Seg 5) both have data_id=79. JS find(r => r.data_id === 79) returns the wrong
record because TPPlace79 appears earlier in S.allRecords.

This migration updates all OVPlace records in-place, preserving wiki_url and any other
enriched fields. New data_id = 10_000_000 + numeric part of OVPlace ID.

Run once. Safe to re-run — already-migrated records (data_id >= 10_000_000) are skipped.
"""

import json, re
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "public" / "data" / "review_places_db.json"
OFFSET = 10_000_000


def main():
    data = json.loads(DB_PATH.read_text(encoding="utf-8"))
    records = data["records"]

    updated = 0
    skipped_already = 0
    for r in records:
        rid = r.get("record_id", "")
        if "OVPlace" not in rid:
            continue
        if r.get("tabula_segment") != 1:
            continue  # only migrate Seg I OVPlace records

        current_id = r.get("data_id")
        if current_id is not None and current_id >= OFFSET:
            skipped_already += 1
            continue

        m = re.search(r"OVPlace(\d+)", rid)
        if not m:
            print(f"  WARN: cannot parse OVPlace ID from {rid}")
            continue

        new_id = OFFSET + int(m.group(1))
        old_id = r.get("data_id")
        r["data_id"] = new_id
        updated += 1
        if updated <= 10:
            print(f"  {r.get('latin', '?'):35s}: data_id {old_id} -> {new_id}")

    if updated > 10:
        print(f"  ... ({updated} total records updated)")

    if skipped_already:
        print(f"  {skipped_already} records already migrated — skipped.")

    if updated:
        DB_PATH.write_text(
            json.dumps(data, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        print(f"\nDone. {updated} OVPlace Seg I data_ids updated (offset +{OFFSET:,}).")
    else:
        print("Nothing to update.")


if __name__ == "__main__":
    main()
