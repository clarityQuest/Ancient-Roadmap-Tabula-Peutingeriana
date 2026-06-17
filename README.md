# Tabula Peutingeriana — Ancient Map × Modern Technology

**Experience the 1,700-year-old Roman road map with GPS, AI, and modern interactivity.**

The [Tabula Peutingeriana](https://en.wikipedia.org/wiki/Tabula_Peutingeriana) is a medieval copy of a late-Roman road map (*cursus publicus*) showing the entire known world — from Britain to India — as it appeared around 300–400 AD. This viewer brings it into the present with GPS location, country-mode overlays, AI-translated Latin inscriptions, and a searchable database of 3,900+ annotated ancient places.

**Live:** [tabula-peutingeriana.com](https://tabula-peutingeriana.com/)

---

## What You Can Do

### Find Yourself in Antiquity
Press the crosshair button to open the location panel. The viewer uses your GPS (or lets you click any point on an interactive modern map) to find the nearest ancient Roman road station, city, or province — and navigates directly to it on the Tabula. Works for any location on Earth; people outside the Roman Empire's extent see a directional marker at the map edge.

### See Your Country on the Ancient Map
Activate **Country Mode** to overlay 58 modern country polygons on the location map. Click or tap any country — or pick from a dropdown — and the Tabula instantly highlights all of that country's ancient places in colour and zooms to fit them. Tap **My Country** for automatic GPS-based country detection. Then toggle labels to read the Latin place names in context.

> *Germany, France, Egypt, India, Palestine — click your country and see what it looked like in 300 AD.*

### Read AI-Translated Latin Inscriptions
Over 1,100 multi-word Latin inscriptions have been translated into English and German by Claude AI and stored in the database. Translations appear instantly on hover and in the info panel — no API calls at runtime. Famous inscriptions include:
- *"Hic Alexander responsum accepit: usque quo Alexander?"* — Here Alexander received the answer: how far, Alexander?
- *"In his locis scorpiones nascuntur"* — In these places scorpions are born.

### Explore 3,900+ Annotated Places
Every annotated place links to Wikipedia (with inline summary and thumbnail), shows its Latin name, modern equivalent, and its position in the Tabula's grid. Filter by 14 category types: major city, city, port, road station, river, lake, island, spa/bath, mountain, people/tribes, region, Roman province, and more.

---

## Features at a Glance

| Feature | Detail |
|---|---|
| Deep-zoom map viewer | K. Miller 1887 facsimile via OpenSeadragon; 11 segments |
| Place database | 3,974 records; 81% georeferenced with lat/lng |
| Country mode | 58 countries, coloured polygon overlay, GPS auto-select |
| GPS location | Find nearest ancient place from your real-world position |
| AI translations | 1,100+ Latin inscriptions → English + German (offline) |
| Wikipedia integration | Inline summary + thumbnail for all linked places |
| Search | Latin name or modern name |
| Category filters | 14 place types, persistent filter state |
| Label toggles | Latin names, modern names — persisted across sessions |
| Mobile | Portrait (bottom sheet) + landscape (side panel) layouts |
| Free | No login, no tracking, open source |

---

## Repository Structure

```
public/
  index.html                          Main viewer
  calibrate.html                      Calibration tool (requires local server)
  database_viewer.html                Place database browser
  main.js                             Viewer logic (single file, ~4400 lines)
  styles.css                          Styles
  data/
    review_places_db.json             Primary place database (~3,974 records)
    countries.geojson                 Country polygons for country mode (58 countries)
    map_segment_bounds.json           Segment viewport bounds
    label_params.json                 Persisted label / opacity settings
    places.json                       Derived place positions (SegIV)
    segments.json                     Segment metadata
  Tabula_Peutingeriana_-_Miller.dzi   Miller map DZI descriptor
  Tabula_Peutingeriana_-_Miller_files/ Miller map tiles
  Readable_SegIV.dzi                  Readable SegIV descriptor (zoom focus segment)
  Readable_SegIV_files/               Readable SegIV tiles

scripts/
  server.py                           Local dev server (port 8080) — required for calibration saves
  translate_latin.py                  Batch Latin→EN/DE translation via Claude API
  build_places.py                     Build place position data from calibration
  build_review_db.py                  Build/update the place database
  prepare_countries.py                Download and filter Natural Earth GeoJSON
  weber_list.json                     Weber place list reference data
```

---

## Running Locally

The calibration tool and database saves require a local server (browsers block file writes from `file://`).

```bash
python scripts/server.py
# → http://localhost:8080/
```

The main viewer and database viewer work with any static server or directly from `file://`.

---

## Latin Translations

Translations are generated once and stored in the database — no runtime API calls needed.

```bash
pip install anthropic
python scripts/translate_latin.py           # translate all pending 2+ word Latin names
python scripts/translate_latin.py --dry-run # preview without API calls
```

Requires `ANTHROPIC_API_KEY` (or set via Claude Code / `~/.claude/config.json`).

---

## Place Database Schema

`public/data/review_places_db.json` — one JSON object per place:

| Field | Description |
|---|---|
| `data_id` | Weber/tp-online numeric ID |
| `latin` / `latin_std` | Latin name as on map / standardised spelling |
| `latin_en` / `latin_de` | AI-translated English / German |
| `modern_preferred` | Modern place name |
| `type` | Category (see below) |
| `lat` / `lng` | Geographic coordinates (WGS84) |
| `country` | Country code(s) — ISO2 or DB code, pipe-separated for multiple |
| `wiki_url` | Wikipedia article URL |
| `tabula_segment` / `tabula_row` / `tabula_col` | Grid position on the Tabula |
| `miller_rect_x1/y1/x2/y2` | Calibrated pixel bounds on the Miller image |

**Place types:** `major_city`, `city`, `port`, `road_station`, `river`, `lake`, `island`, `spa`, `mountain`, `people`, `region`, `roman_province`, `modern_state`, `water`

---

## Credits

- Map image: K. Miller, *Itineraria Romana* 1887 facsimile — public domain, via Wikimedia Commons
- Original parchment: Österreichische Nationalbibliothek, Vienna — UNESCO Memory of the World (2007)
- Place data: [tabula-peutingeriana.de](https://www.tabula-peutingeriana.de/) (M. Weber) · [tp-online.ku.de](https://tp-online.ku.de/) (Universität Ulm)
- Road network: [OmnesViae](https://omnesviae.org)
- Viewer: [OpenSeadragon](https://openseadragon.github.io/) · [Leaflet](https://leafletjs.com/) / OpenStreetMap
- Country polygons: Natural Earth 110m
- AI translations: [Anthropic Claude](https://www.anthropic.com/) (claude-haiku-4-5)
