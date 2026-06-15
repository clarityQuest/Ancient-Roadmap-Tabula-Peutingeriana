# Tabula Peutingeriana — Interactive Map Viewer

**See your country on the ancient Roman road map!**

The [Tabula Peutingeriana](https://en.wikipedia.org/wiki/Tabula_Peutingeriana) is a medieval copy of an ancient Roman road map (*cursus publicus*), charting the entire known world from Britain to India as it appeared around 300–400 AD. This project provides an interactive web viewer with a georeferenced place database of 3,900+ annotated locations.

## Live Viewer

- **[Map Viewer](https://clarityquest.github.io/Ancient-Roadmap-Tabula-Peutingeriana/public/index.html)**
- **[Database Viewer](https://clarityquest.github.io/Ancient-Roadmap-Tabula-Peutingeriana/public/database_viewer.html)**
- **[Calibration Tool](https://clarityquest.github.io/Ancient-Roadmap-Tabula-Peutingeriana/public/calibrate.html)** *(requires local server for saving)*

## Features

### Explore the Ancient World
- **3,900+ place database** sourced from [tabula-peutingeriana.de](https://www.tabula-peutingeriana.de/) (M. Weber) and the Ulm tp-online database
- **Category filters** — Major City, City, Port, Road Station, River, Lake, Island, Spa/Bath, Mountain, People/Tribes, Region, Roman Province, and more
- **Place labels** — modern name and Latin name rendered on the map; toggle on/off via the category popup
- **Search** by Latin or modern place name
- **Info panel** — click any place for details: Wikipedia summary + thumbnail, Latin translation, modern equivalent, and a link to the Ulm database entry

### See Your Country on the Ancient Map!
- **Country Mode** — click the crosshair button, then *Countries* to overlay coloured country polygons on the interactive Leaflet map; click any country to instantly highlight all its ancient Roman places on the Tabula Peutingeriana and zoom the map to fit
- **GPS country detection** — tap *My Country* to auto-select your current country based on GPS location
- Supports 58 countries from Portugal to India, including all Roman-era nations

### Locate Yourself in Antiquity
- **Locate Me** — press the crosshair button (⊕) to place yourself on the ancient map using GPS or by clicking the interactive map; the viewer navigates to the nearest Roman road station, city, or province with a Wikipedia preview
- Users outside the Tabula's coverage area (Americas, Australia, East Asia) see a direction marker at the corresponding edge of the map

### Latin Inscriptions — AI Translated
- **1,100+ Latin translations** — multi-word Latin place names and inscriptions are translated into English and German by Claude AI (claude-haiku) and stored in the database; translations appear instantly in the hover tooltip and info panel without any runtime API call
- Famous inscriptions include: *"Hic Alexander responsum accepit: usque quo Alexander?"* (Here Alexander received the answer: How far, Alexander?) and *"In his locis scorpiones nascuntur"* (In these places scorpions are born)

### Tools
- **Calibration tool** (`calibrate.html`) — mark precise pixel positions of places on the Miller map; auto-saves to the database via the local dev server
- **Database viewer** (`database_viewer.html`) — browse, filter, and inspect all records

## Repository Structure

```
public/
  index.html                          Main viewer
  calibrate.html                      Calibration tool (requires local server)
  database_viewer.html                Place database browser
  main.js                             Viewer logic
  styles.css                          Styles
  data/
    review_places_db.json             Primary place database (~3,900 records, with latin_en/latin_de)
    countries.geojson                 Country polygons for country-mode filter (58 countries)
    map_segment_bounds.json           Segment viewport bounds
    places.json                       Derived place positions (SegIV)
    segments.json                     Segment metadata
  Tabula_Peutingeriana_-_Miller.dzi   Miller map DZI descriptor
  Tabula_Peutingeriana_-_Miller_files/ Miller map tiles
  Readable_SegIV.dzi                  Readable SegIV descriptor
  Readable_SegIV_files/               Readable SegIV tiles
  Tabula_Peutingeriana_150dpi_Stitched.dzi  Stitched map descriptor
  Tabula_Peutingeriana_150dpi_Stitched_files/ Stitched map tiles

scripts/
  server.py                           Local dev server (port 8080)
  translate_latin.py                  Batch Latin→EN/DE translation via Claude API
  build_places.py                     Build place position data
  build_review_db.py                  Build/update the place database
  weber_list.json                     Weber place list reference data
```

## Running Locally

The calibration tool and database saves require a local server (browser security blocks file writes).

```bash
python scripts/server.py
# → http://localhost:8080/
```

The main viewer (`index.html`) and database viewer work directly via `file://` or any static server.

## Latin Translations

To regenerate or extend Latin translations:

```bash
pip install anthropic
# Set ANTHROPIC_API_KEY or use Claude Code (key auto-detected from ~/.claude/config.json)
python scripts/translate_latin.py           # translate all pending 2+ word Latin names
python scripts/translate_latin.py --dry-run # preview without API calls
```

Translations are stored as `latin_en` / `latin_de` fields in `review_places_db.json` and served to the browser statically — no runtime API calls needed.

## Place Database

`public/data/review_places_db.json` contains ~3,900 records with fields:

| Field | Description |
|---|---|
| `data_id` | Weber/tp-online numeric ID |
| `latin` / `latin_std` | Latin name as on map / standardised |
| `latin_en` / `latin_de` | AI-translated English / German |
| `modern_preferred` | Modern place name |
| `type` | Category (see below) |
| `lat` / `lng` | Geographic coordinates |
| `country` | Country code(s) (ISO2 or DB code, pipe-separated) |
| `wiki_url` | Wikipedia article URL |
| `tabula_segment` / `tabula_row` / `tabula_col` | Grid position on the Tabula |
| `miller_rect_x1/y1/x2/y2` | Calibrated pixel bounds on the Miller image |

**Place types:** `major_city`, `city`, `port`, `road_station`, `river`, `lake`, `island`, `spa`, `mountain`, `people`, `region`, `roman_province`, `modern_state`, `water`

## Credits

- Map image: K. Miller, 1887 facsimile — public domain, via Wikimedia Commons
- Place data: [tabula-peutingeriana.de](https://www.tabula-peutingeriana.de/) (M. Weber) and [tp-online.ku.de](https://tp-online.ku.de/) (Universität Ulm)
- Road network: [OmnesViae](https://omnesviae.org)
- Viewer: [OpenSeadragon](https://openseadragon.github.io/) · Maps: [Leaflet](https://leafletjs.com/) / OpenStreetMap
- Latin translations: [Anthropic Claude](https://www.anthropic.com/) (claude-haiku-4-5)
