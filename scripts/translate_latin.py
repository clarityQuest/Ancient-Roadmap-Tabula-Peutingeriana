#!/usr/bin/env python3
"""
Batch-translates multi-word Latin place names from the Tabula Peutingeriana DB
using Claude API. Adds latin_en and latin_de fields to each record in-place.

Usage:
  python scripts/translate_latin.py            # translate all pending
  python scripts/translate_latin.py --dry-run  # preview without API calls
  python scripts/translate_latin.py --reset    # clear existing translations

Requires: pip install anthropic
API key:  set ANTHROPIC_API_KEY environment variable
"""

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / "public" / "data" / "review_places_db.json"
BATCH_SIZE = 40
MODEL = "claude-haiku-4-5-20251001"


def _get_api_key() -> str:
    """Return ANTHROPIC_API_KEY from env or Claude Code's config as fallback."""
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        return key
    # Fallback: read from Claude Code config (~/.claude/config.json -> primaryApiKey)
    cfg = Path.home() / ".claude" / "config.json"
    if cfg.exists():
        try:
            data = json.loads(cfg.read_text(encoding="utf-8"))
            key = data.get("primaryApiKey", "")
            if key:
                return key
        except Exception:
            pass
    return ""


def clean_latin(text: str) -> str:
    """Mirror of cleanLatinForTranslation() in main.js — strips parenthetical variants."""
    text = re.sub(r'\s*\([^)]*\)', '', text)
    text = re.sub(r'[·̇˙~\[\]]', '', text)
    return re.sub(r'\s+', ' ', text).strip()


def is_multi_word(text: str) -> bool:
    """Mirror of isTranslatableLatin() in main.js — 2+ non-numeral, non-Roman-numeral words."""
    if not text:
        return False
    clean = clean_latin(text)
    if re.search(r'[|/]', clean):
        return False
    words = [
        w for w in clean.split()
        if len(w) > 1
        and not re.match(r'^\d+$', w)
        and not re.match(r'^[IVXLCDM]+\.?$', w, re.IGNORECASE)
    ]
    return len(words) >= 2


def translate_batch(client, items: list) -> dict:
    """
    Translates a batch of Latin items to English and German.
    items: [{"id": data_id, "latin": cleaned_text}, ...]
    Returns: {data_id: {"en": "...", "de": "..."}}
    """
    items_json = json.dumps(items, ensure_ascii=False)
    prompt = (
        "You are an expert in classical Latin and ancient Roman geography. "
        "Translate these Latin names and inscriptions from the Tabula Peutingeriana "
        "(a Roman road map from around 300–400 AD) into English and German.\n\n"
        "Translation rules:\n"
        "- Ad = At/near (Ad Aquas → At the Waters)\n"
        "- In = In/at (In Summo → At the Summit)\n"
        "- Sub = Below/under\n"
        "- Fines = Borders/Territory\n"
        "- For inscriptions: translate faithfully, keep it concise\n"
        "- Proper names (Romanus, Alexander, etc.) stay untranslated\n"
        "- Do not add explanations or brackets in the translation\n\n"
        "Return ONLY a JSON array with this exact structure (no markdown, no extra text):\n"
        '[{"id":<number>,"en":"<english translation>","de":"<german translation>"}]\n\n'
        f"Items to translate:\n{items_json}"
    )

    msg = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    text = msg.content[0].text.strip()
    # Strip markdown code fences if present
    m = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if m:
        text = m.group(1).strip()
    results = json.loads(text)
    return {r["id"]: {"en": r["en"], "de": r["de"]} for r in results}


def main():
    dry_run = "--dry-run" in sys.argv
    reset   = "--reset"   in sys.argv

    print(f"Loading {DB_PATH.name}...")
    db = json.loads(DB_PATH.read_text(encoding="utf-8"))
    records = db["records"]

    if reset:
        cleared = 0
        for r in records:
            if "latin_en" in r or "latin_de" in r:
                r.pop("latin_en", None)
                r.pop("latin_de", None)
                cleared += 1
        DB_PATH.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Cleared translations from {cleared} records.")
        return

    # Collect records that need translation
    to_translate = []
    already_done = 0
    for r in records:
        latin = r.get("latin") or r.get("latin_std") or ""
        if not is_multi_word(latin):
            continue
        if r.get("latin_en") and r.get("latin_de"):
            already_done += 1
            continue
        to_translate.append(r)

    total = len(to_translate)
    print(f"Total DB records : {len(records)}")
    print(f"Multi-word Latin : {total + already_done}")
    print(f"Already done     : {already_done}")
    print(f"To translate     : {total}")

    if not to_translate:
        print("Nothing to do.")
        return

    if dry_run:
        print("\n-- DRY RUN preview (first 10) --")
        for r in to_translate[:10]:
            latin = r.get("latin") or r.get("latin_std") or ""
            print(f"  [{r['data_id']:4d}] {latin!r}")
        print(f"  ... and {max(0, total - 10)} more")
        return

    import anthropic
    api_key = _get_api_key()
    if not api_key:
        print("ERROR: No Anthropic API key found.")
        print("Set ANTHROPIC_API_KEY environment variable or ensure ~/.claude/config.json exists.")
        sys.exit(1)
    client = anthropic.Anthropic(api_key=api_key)

    done   = 0
    errors = 0
    batch_count = (total + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, total, BATCH_SIZE):
        batch = to_translate[i : i + BATCH_SIZE]
        bn    = i // BATCH_SIZE + 1
        print(f"  Batch {bn:3d}/{batch_count}: {len(batch):2d} items...", end="", flush=True)

        items = []
        for r in batch:
            latin = r.get("latin") or r.get("latin_std") or ""
            items.append({"id": r["data_id"], "latin": clean_latin(latin)})

        try:
            translations = translate_batch(client, items)
            batch_done = 0
            for r in batch:
                t = translations.get(r["data_id"])
                if t:
                    r["latin_en"] = t["en"]
                    r["latin_de"] = t["de"]
                    done       += 1
                    batch_done += 1
                else:
                    latin = r.get("latin") or ""
                    print(f"\n    ⚠ No result for id={r['data_id']}: {latin[:40]!r}")
            print(f" {batch_done}/{len(batch)} ok")
        except Exception as e:
            err_str = str(e)
            print(f" ERROR: {e}")
            errors += 1
            # Save progress so far before aborting
            if done > 0:
                _save(db)
                print(f"    (progress saved after error)")
            # Stop immediately on billing or auth errors — no point retrying all batches
            if "credit balance" in err_str or "authentication" in err_str.lower() or "401" in err_str:
                print("Stopping: fix billing/auth then re-run (already-translated records will be skipped).")
                sys.exit(1)

    print(f"\nTranslated: {done}  Batch errors: {errors}")

    if done > 0:
        _save(db)
    else:
        print("Nothing saved.")


def _save(db):
    tmp = DB_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(DB_PATH)
    print(f"Saved -> {DB_PATH.name}")


if __name__ == "__main__":
    main()
