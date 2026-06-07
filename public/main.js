/**
 * Tabula Peutingeriana — Segment IV Interactive Viewer
 *
 * Features:
 * - OpenSeadragon deep-zoom with two tile sources:
 *   · Original (Miller 1887 facsimile, segment IV viewport) — no markers
 *   · Readable (Weber Kopie, 150dpi) — with color-coded markers
 * - 320 places scraped from tabula-peutingeriana.de
 * - Latin / English label toggle
 * - Hover tooltips and click info panel
 * - Search by Latin or modern name
 * - Zoom-dependent marker visibility
 * - Canvas-overlay marker rendering
 */

"use strict";

/* ============================================================
   Constants
   ============================================================ */

// Weber 150dpi segment IV image
const IMG_W = 4371;
const IMG_H = 2105;
const DEFAULT_SEGMENT = 4;

// Miller full image
const MILLER_W = 46380;
const MILLER_H = 2953;
const SEGMENT_COUNT = 11;

const TYPE_COLORS = {
  city:           "#8B0000",
  port:           "#1D4ED8",
  road_station:   "#92400E",
  river:          "#0e7490",
  lake:           "#0369a1",
  island:         "#15803d",
  region:         "#7c3aed",
  roman_province: "#a16207",
  modern_state:   "#475569",
  water:          "#164e63",
  spa:            "#0891b2",
  temple:         "#9333ea",
  mountain:       "#78716c",
  people:         "#9d174d",
};

// Draw order: lower = rendered first (background). Regions/rivers behind everything else.
const TYPE_DRAW_ORDER = {
  region: 0,
  water: 1, river: 1, lake: 1,
  roman_province: 2, modern_state: 2, mountain: 2, island: 2,
  people: 3,
  road_station: 4, spa: 5, temple: 5, port: 6, city: 7,
};

// Lower number = label allocated first (higher priority)
const TYPE_LABEL_PRIORITY = {
  city: 0, temple: 0, spa: 0, port: 1,
  mountain: 2, island: 2, water: 2, river: 2, lake: 2, people: 2,
  road_station: 3,
};

const TYPE_LABELS = {
  city:           "City",
  port:           "Port",
  road_station:   "Road Station",
  river:          "River",
  lake:           "Lake",
  island:         "Island",
  region:         "Region",
  roman_province: "Roman Province",
  modern_state:   "Modern State",
  water:          "Water",
  spa:            "Spa",
  temple:         "Temple",
  mountain:       "Mountain",
  people:         "People",
};

const TYPE_ICONS = {
  city: "🏛", port: "⚓", road_station: "🛣",
  river: "〰", lake: "💧", island: "🏝", region: "📍",
  roman_province: "🗺", modern_state: "🌍", water: "🌊",
  spa: "♨", temple: "⛩", mountain: "⛰", people: "👥",
};

const I18N = {
  en: {
    city: "City", port: "Port", road_station: "Road Station",
    river: "River", lake: "Lake", island: "Island", region: "Region",
    roman_province: "Roman Province", modern_state: "Modern State",
    water: "Water", spa: "Spa", temple: "Temple", mountain: "Mountain",
    people: "People",
    province: "Province",
    wiki_link: "Wikipedia ↗", ulm_link: "Scientific Info/Ulm DB ↗",
    unknown_modern: "(unknown modern name)",
    wiki_lang: "en",
    tabula_view_label: "Original Tabula Peutingeriana view",
    about_subtitle: "The Road Map of the Ancient World",
    about_intro: "The Tabula Peutingeriana is one of the most remarkable surviving documents of antiquity — a medieval copy of a Roman road map that charts the entire known world, from the Atlantic coast of Britain to the Indian subcontinent, in extraordinary detail.",
    about_glance_h: "At a Glance",
    about_orig_date: "Original date", about_orig_date_v: "c. 4th – 5th century AD",
    about_copy: "Surviving copy",     about_copy_v: "c. 1200 AD (Colmar scriptorium)",
    about_dims: "Dimensions",         about_dims_v: "6.75 m long · 34 cm tall (scroll)",
    about_cities: "Cities & places",  about_cities_v: "~3,500 names across 12 segments",
    about_preserved: "Preserved at",  about_preserved_v: "Österreichische Nationalbibliothek, Vienna",
    about_unesco: "UNESCO status",    about_unesco_v: "Memory of the World (2007)",
    about_named: "Named after",       about_named_v: "Konrad Peutinger (1465–1547), German humanist",
    about_map_h: "A Map Unlike Any Other",
    about_map_p1: "This is not a geographic map in the modern sense. The scroll format forced the cartographer to compress the north-south dimension dramatically — the Mediterranean Sea appears as a narrow strip, and Italy is rotated almost horizontally. What matters is <em>connectivity</em>: roads, distances in Roman miles (<em>milia passuum</em>), and the cities they link.",
    about_map_p2: "Three cities receive special pictorial treatment — <strong>Rome</strong>, <strong>Constantinople</strong>, and <strong>Antioch</strong> — each shown as an enthroned figure, reflecting their supreme importance in the late Roman world.",
    about_lost_h: "The Lost Segment",
    about_lost_p: "Segment I — covering Britain (except the southeast), the Iberian Peninsula, and the Atlantic coast of Morocco — has been lost since at least the 16th century. The remaining eleven segments survive intact, making this viewer's collection complete for Segments II through XII.",
    about_hist_h: "History of the Document",
    about_hist_p: "The map was copied around 1200 AD by a monk in Colmar (Alsace), likely from an earlier Carolingian copy of a late antique original. Konrad Celtes discovered it in 1494 and passed it to Konrad Peutinger of Augsburg, who gave it its modern name. After Peutinger's death it passed through various hands before entering the Imperial Library in Vienna in 1738, where it remains today.",
    about_learn_h: "Learn More",
  },
  de: {
    city: "Stadt", port: "Hafen", road_station: "Straßenstation",
    river: "Fluss", lake: "See", island: "Insel", region: "Region",
    roman_province: "Römische Provinz", modern_state: "Moderner Staat",
    water: "Gewässer", spa: "Heilbad", temple: "Tempel", mountain: "Berg",
    people: "Volk",
    province: "Provinz",
    wiki_link: "Wikipedia ↗", ulm_link: "Wiss. Info/Ulm DB ↗",
    unknown_modern: "(moderner Name unbekannt)",
    wiki_lang: "de",
    tabula_view_label: "Originalansicht der Tabula Peutingeriana",
    about_subtitle: "Die Straßenkarte der antiken Welt",
    about_intro: "Die Tabula Peutingeriana ist eines der bemerkenswertesten erhaltenen Dokumente der Antike — eine mittelalterliche Kopie einer römischen Straßenkarte, die die gesamte bekannte Welt von der Atlantikküste Britanniens bis zum indischen Subkontinent in außerordentlicher Detailtreue erfasst.",
    about_glance_h: "Auf einen Blick",
    about_orig_date: "Ursprüngliches Datum", about_orig_date_v: "ca. 4.–5. Jahrhundert n. Chr.",
    about_copy: "Erhaltene Kopie",           about_copy_v: "ca. 1200 n. Chr. (Skriptorium Colmar)",
    about_dims: "Abmessungen",               about_dims_v: "6,75 m lang · 34 cm hoch (Rolle)",
    about_cities: "Städte & Orte",           about_cities_v: "ca. 3.500 Namen auf 12 Segmenten",
    about_preserved: "Aufbewahrt in",        about_preserved_v: "Österreichische Nationalbibliothek, Wien",
    about_unesco: "UNESCO-Status",           about_unesco_v: "Memory of the World (2007)",
    about_named: "Benannt nach",             about_named_v: "Konrad Peutinger (1465–1547), deutscher Humanist",
    about_map_h: "Eine Karte wie keine andere",
    about_map_p1: "Dies ist keine geographische Karte im modernen Sinne. Das Rollenformat zwang den Kartographen, die Nord-Süd-Ausdehnung dramatisch zu komprimieren — das Mittelmeer erscheint als schmaler Streifen, und Italien ist fast horizontal gedreht. Entscheidend ist die <em>Vernetzung</em>: Straßen, Entfernungen in römischen Meilen (<em>milia passuum</em>) und die Städte, die sie verbinden.",
    about_map_p2: "Drei Städte erhalten eine besondere bildliche Darstellung — <strong>Rom</strong>, <strong>Konstantinopel</strong> und <strong>Antiochien</strong> — jeweils als thronende Figur, was ihre überragende Bedeutung in der spätrömischen Welt widerspiegelt.",
    about_lost_h: "Das verlorene Segment",
    about_lost_p: "Segment I — das Britannien (außer dem Südosten), die iberische Halbinsel und die atlantische Küste Marokkos umfasste — ist seit mindestens dem 16. Jahrhundert verloren. Die übrigen elf Segmente sind vollständig erhalten, sodass diese Sammlung für die Segmente II bis XII vollständig ist.",
    about_hist_h: "Geschichte des Dokuments",
    about_hist_p: "Die Karte wurde um 1200 n. Chr. von einem Mönch in Colmar (Elsass) kopiert, wahrscheinlich nach einer früheren karolingischen Kopie eines spätantiken Originals. Konrad Celtes entdeckte sie 1494 und übergab sie Konrad Peutinger aus Augsburg, der ihr ihren heutigen Namen gab. Nach Peutingers Tod gelangte sie über verschiedene Hände in die Kaiserliche Bibliothek in Wien (1738), wo sie bis heute aufbewahrt wird.",
    about_learn_h: "Mehr erfahren",
  },
};

const DRAFT_STORAGE_KEY = "tp_calibrate_seg4_rectangles_v1";
const MAP_RUNTIME_TYPES = new Set(Object.keys(TYPE_COLORS));

// Label rendering parameters — tunable via the settings panel, saved to label_params.json
const LP_KEY = "tp_label_params_v1";
const LP_DEFAULTS = {
  markerAlpha:       1.0,   // marker fill/stroke opacity multiplier
  fontScale:         1.0,   // marker screen size × fontScale = secondary font ceiling
  maxFontDesktop:  999,    // effectively uncapped — zoom curve drives max font
  maxFontMobile:   999,    // same
  minFontThreshold:  0,    // no threshold — always show if font > 0
  fadeRate:          1.0,  // with threshold=0 this is always opaque; not exposed in UI
  maxLabelsDesktop:  80,   // hard cap on simultaneous labels (desktop)
  maxLabelsMobile:   10,   // hard cap on simultaneous labels (mobile)
  minFontMobile:     0,    // mobile labels hidden if scaled font falls below this px
  labelPad:          4,    // px padding around each label's overlap bounding box
  labelPadZoomThresh: 8,        // above this zoom (desktop), skip overlap detection
  labelPadZoomThreshMobile: 8, // above this zoom (mobile), skip overlap detection
  zoomThreshMid:     0.8,  // road_station hidden below this OSD zoom
  zoomThreshAll:     2.5,  // all types visible above this OSD zoom
  // Zoom → font curve: 4 control points (piecewise linear). Font = min(curve, markerCap).
  zfZ1: 0.3,  zfF1:  4,   // point 1 (low zoom)
  zfZ2: 1.0,  zfF2:  5,   // point 2
  zfZ3: 3.0,  zfF3: 14,   // point 3
  zfZ4: 8.0,  zfF4: 22,   // point 4 (high zoom)
};
let LP = { ...LP_DEFAULTS };

function truncWords(s, n) {
  if (!s) return s;
  const main = s.split(" / ")[0].trim();  // drop alternative names after " / "
  const w = main.split(" ");
  return w.length <= n ? main : w.slice(0, n).join(" ") + "…";
}

function fontFromZoom(zoom) {
  const pts = [[LP.zfZ1, LP.zfF1], [LP.zfZ2, LP.zfF2],
               [LP.zfZ3, LP.zfF3], [LP.zfZ4, LP.zfF4]];
  if (zoom <= pts[0][0]) return pts[0][1];
  for (let i = 0; i < 3; i++) {
    if (zoom <= pts[i + 1][0]) {
      const t = (zoom - pts[i][0]) / Math.max(0.0001, pts[i + 1][0] - pts[i][0]);
      return pts[i][1] + t * (pts[i + 1][1] - pts[i][1]);
    }
  }
  return pts[3][1];
}

function computeFont(zoom) {
  const raw = fontFromZoom(zoom);
  if (!S.isMobile) return raw;
  // Scale the curve's full range [zfF1..zfF4] → [minFontMobile..maxFontMobile]
  const rawMin = LP.zfF1;
  const rawMax = Math.max(LP.zfF1 + 1, LP.zfF4);
  const t = Math.max(0, Math.min(1, (raw - rawMin) / (rawMax - rawMin)));
  return LP.minFontMobile + t * (LP.maxFontMobile - LP.minFontMobile);
}

/* ============================================================
   State
   ============================================================ */
const S = {
  viewer:       null,
  places:       [],
  allRecords:   [],
  segments:     [],
  mapMode:      "old",       // "old" | "new"
  selectedSegment: DEFAULT_SEGMENT,
  newSourceKind: "readable-seg4", // "readable-seg4" | "stitched"
  markersOn:      true,
  labelsOn:       true,
  activeTypes:    new Set(["city", "temple", "spa"]),
  regionSolo:     false,
  savedActiveTypes: null,
  millerOverlayOn: true,
  millerCalib:    [],   // loaded from miller_rect_* fields in review_places_db.json
  millerCalibHit: [],   // same records, sorted cities-first for hit-testing
  selectedPlace:  null,
  selectedDataId: null,
  highlightDataId: null,
  highlightUntil:  0,
  highlightVp:     null,  // {vx,vy} viewport centre stored by panToPlace for fallback ring
  userLocVp:      null,   // {vx,vy} viewport coords where crosshair is drawn
  userLocLat:     null,
  userLocLng:     null,
  userLocLabel:   "",     // short label drawn near the crosshair
  userLocOutside: false,  // true when projected to Tabula edge
  userLocCentVp:  null,   // centroid viewport position (used for outside arrow direction)
  lang: (() => { try { return localStorage.getItem("tp_lang") || "sys"; } catch { return "sys"; } })(),
  defaultLat: (() => { try { const v = Number(localStorage.getItem("tp_defaultLat")); return Number.isFinite(v) && v !== 0 ? v : 41.8902; } catch { return 41.8902; } })(),
  defaultLng: (() => { try { const v = Number(localStorage.getItem("tp_defaultLng")); return Number.isFinite(v) && v !== 0 ? v : 12.4922; } catch { return 12.4922; } })(),
  isMobile: window.matchMedia("(pointer: coarse), (max-width: 600px)").matches,
  canvas:       null,
  ctx:          null,
  readableTile: null,
  originalTile: null,
  stitchedTile: null,
  boundsBySource: {
    old: {},
    stitched: {},
    readableSeg4: {},
  },
};

let infoPanelOpenedAt = 0;
const wikiCache = new Map(); // session cache for Wikipedia API results
let wikiRequestId = 0;       // incremented on each panel open to abort stale fetches

/* ============================================================
   i18n helpers
   ============================================================ */
function getLang() {
  if (S.lang === "de") return "de";
  if (S.lang === "en") return "en";
  return (navigator.language || "en").toLowerCase().startsWith("de") ? "de" : "en";
}

function getText(key) {
  const lang = getLang();
  return (I18N[lang] || I18N.en)[key] ?? I18N.en[key] ?? key;
}

function setLang(lang) {
  S.lang = lang;
  try { localStorage.setItem("tp_lang", lang); } catch {}
  updateLangButtons();
  if (S.selectedPlace) showInfoPanel(S.selectedPlace);
}

function applyI18n() {
  const dict = I18N[getLang()] || I18N.en;
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const v = dict[el.dataset.i18n];
    if (v != null) el.textContent = v;
  });
  document.querySelectorAll("[data-i18n-html]").forEach(el => {
    const v = dict[el.dataset.i18nHtml];
    if (v != null) el.innerHTML = v;
  });
  document.querySelectorAll(".lang-btn").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.lang === S.lang);
  });
  document.querySelectorAll(".type-filter-btn[data-type]").forEach(btn => {
    const type = btn.dataset.type;
    const label = dict[type] || TYPE_LABELS[type] || type;
    btn.innerHTML = `<span class="tf-dot" style="background:${TYPE_COLORS[type]}"></span>${label}`;
    btn.title = label;
  });
}
function updateLangButtons() { applyI18n(); }

/* ============================================================
   Data loading
   ============================================================ */
async function loadJSON(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${url}: ${r.status}`);
  return r.json();
}

async function loadJSONOptional(url, fallback) {
  try {
    return await loadJSON(url);
  } catch {
    return fallback;
  }
}

function loadCalibrateDraftMap() {
  try {
    const raw = localStorage.getItem(DRAFT_STORAGE_KEY);
    if (!raw) return new Map();
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object") return new Map();

    const out = new Map();
    for (const [did, rec] of Object.entries(parsed)) {
      const nDid = Number(did);
      if (!Number.isFinite(nDid) || !rec || typeof rec !== "object") continue;
      if (!(Number.isFinite(rec.rect_x1) && Number.isFinite(rec.rect_y1) && Number.isFinite(rec.rect_x2) && Number.isFinite(rec.rect_y2))) continue;
      out.set(nDid, {
        rect_x1: Number(rec.rect_x1),
        rect_y1: Number(rec.rect_y1),
        rect_x2: Number(rec.rect_x2),
        rect_y2: Number(rec.rect_y2),
        rect_w: Number.isFinite(rec.rect_w) ? Number(rec.rect_w) : undefined,
        rect_h: Number.isFinite(rec.rect_h) ? Number(rec.rect_h) : undefined,
        rect_user_set: true,
      });
    }
    return out;
  } catch (e) {
    console.warn("Could not read calibrate draft rectangles:", e);
    return new Map();
  }
}

/* ============================================================
   Coordinate helpers
   ============================================================ */
function viewportToCanvas(vx, vy) {
  const vp = S.viewer.viewport;
  const p = vp.viewportToViewerElementCoordinates(new OpenSeadragon.Point(vx, vy));
  return { cx: p.x, cy: p.y };
}

function imageToCanvas(ix, iy) {
  const vp = S.viewer.viewport;
  const v = vp.imageToViewportCoordinates(new OpenSeadragon.Point(ix, iy));
  const p = vp.viewportToViewerElementCoordinates(v);
  return { cx: p.x, cy: p.y };
}

function buildUniformBounds(segmentNumbers) {
  const out = {};
  const width = 1 / Math.max(segmentNumbers.length, 1);
  segmentNumbers.forEach((n, idx) => {
    const x0 = idx * width;
    const x1 = idx === segmentNumbers.length - 1 ? 1 : (idx + 1) * width;
    out[String(n)] = { x0, y0: 0, x1, y1: 1 };
  });
  return out;
}

function activeBoundsKey() {
  if (S.mapMode === "old") return "old";
  return S.newSourceKind === "stitched" ? "stitched" : "readableSeg4";
}

function boundsKeyForMode(mode) {
  if (mode === "old") return "old";
  return S.newSourceKind === "stitched" ? "stitched" : "readableSeg4";
}

function getSegmentBounds(segmentNumber, boundsKey = activeBoundsKey()) {
  const key = String(segmentNumber);
  return S.boundsBySource[boundsKey]?.[key] || null;
}

function applySegmentUIState() {
  const container = document.getElementById("segment-buttons");
  if (!container) return;
  container.querySelectorAll(".seg-btn").forEach((btn) => {
    btn.classList.toggle("active", Number(btn.dataset.seg) === S.selectedSegment);
  });
}

function focusSegment(segmentNumber, immediate = false) {
  const n = Number(segmentNumber);
  const bounds = getSegmentBounds(n);
  if (!bounds) {
    applySegmentUIState();
    const statusEl = document.getElementById("status");
    if (statusEl && S.mapMode === "new" && S.newSourceKind === "readable-seg4") {
      statusEl.textContent = "Readable fallback only supports segment IV until stitched assets are generated.";
    }
    return false;
  }

  S.selectedSegment = n;
  applySegmentUIState();
  const segW = Math.max(0.00001, bounds.x1 - bounds.x0);
  const segH = Math.max(0.00001, bounds.y1 - bounds.y0);

  // OSD normalises coordinates to image WIDTH (x: 0..1, y: 0..1/imageAspect).
  // bounds.y values are in image-height-fraction (0..1), so divide by imageAspect.
  const imageEl = S.viewer.world.getItemAt(0);
  const imageAspect = imageEl
    ? imageEl.getContentSize().x / Math.max(1, imageEl.getContentSize().y)
    : (S.stitchedTile?.Image?.Size
        ? Number(S.stitchedTile.Image.Size.Width) / Math.max(1, Number(S.stitchedTile.Image.Size.Height))
        : 16);

  // Expand bounds by 10% on each side for breathing room (~83% fill).
  const pad = 0.10;
  const osdRect = new OpenSeadragon.Rect(
    bounds.x0 - segW * pad,
    (bounds.y0 - segH * pad) / imageAspect,
    segW * (1 + 2 * pad),
    segH * (1 + 2 * pad) / imageAspect
  );

  // fitBounds is atomic (no pan/zoom race) and handles both axes correctly.
  S.viewer.viewport.fitBounds(osdRect, immediate);
  return true;
}

function focusStartup(immediate = false) {
  // Miller map: same fitBounds approach as focusSegment, centered at seg V/VI boundary (Rome)
  if (S.mapMode === "old" && S.viewer.viewport) {
    const millerAspect = MILLER_H / MILLER_W;
    const segW = 1 / SEGMENT_COUNT; // width of one segment in OSD coords
    const cx = 0.363636;            // seg 5/6 boundary where Rome sits
    S.viewer.viewport.fitBounds(
      new OpenSeadragon.Rect(cx - segW / 2, 0, segW, millerAspect),
      immediate
    );
    return;
  }
  focusSegment(S.selectedSegment, immediate);
}

function setupSegmentSelector() {
  const container = document.getElementById("segment-buttons");
  if (!container) return;
  container.innerHTML = S.segments.map((seg) => {
    const n = Number(seg.number);
    const roman = String(seg.roman || n);
    return `<button class="seg-btn" data-seg="${n}" title="${roman}: ${seg.label || roman}">${roman}</button>`;
  }).join("");
  applySegmentUIState();
  container.addEventListener("click", (e) => {
    const btn = e.target.closest(".seg-btn");
    if (!btn) return;
    focusSegment(Number(btn.dataset.seg));
  });
}

/* ============================================================
   Marker rendering (canvas overlay)
   ============================================================ */
function sizeCanvas() {
  const el = S.viewer.element;
  const dpr = window.devicePixelRatio || 1;
  S.canvas.width  = el.clientWidth  * dpr;
  S.canvas.height = el.clientHeight * dpr;
  S.canvas.style.width  = el.clientWidth  + "px";
  S.canvas.style.height = el.clientHeight + "px";
  S.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
}

function markerRadius(zoom, type) {
  const base = type === "city" ? 5.5 :
               type === "port" ? 4 : 3;
  return Math.min(base * Math.sqrt(zoom + 0.5), 20);
}

function defaultRectSize(type) {
  if (type === "city") return { w: 11, h: 11 };
  if (type === "port") return { w: 8, h: 8 };
  return { w: 6, h: 6 };
}

function placeRectCorners(place) {
  const d = defaultRectSize(place.type);
  const w = Number.isFinite(place.rect_w) && place.rect_w > 0 ? place.rect_w : d.w;
  const h = Number.isFinite(place.rect_h) && place.rect_h > 0 ? place.rect_h : d.h;

  let x1 = place.rect_x1;
  let y1 = place.rect_y1;
  let x2 = place.rect_x2;
  let y2 = place.rect_y2;

  const hasCorners = Number.isFinite(x1) && Number.isFinite(y1) && Number.isFinite(x2) && Number.isFinite(y2);
  if (!hasCorners) {
    const cx = Number(place.px);
    const cy = Number(place.py);
    x1 = cx - w / 2;
    y1 = cy - h / 2;
    x2 = cx + w / 2;
    y2 = cy + h / 2;
  }

  // If user explicitly set a rectangle, trust the provided corners exactly.
  // Do not substitute with defaults for user-set records.
  if (place.rect_user_set && !hasCorners) {
    const cx = Number(place.px);
    const cy = Number(place.py);
    x1 = cx - w / 2;
    y1 = cy - h / 2;
    x2 = cx + w / 2;
    y2 = cy + h / 2;
  }

  if (x1 > x2) [x1, x2] = [x2, x1];
  if (y1 > y2) [y1, y2] = [y2, y1];

  x1 = Math.max(0, Math.min(IMG_W, x1));
  y1 = Math.max(0, Math.min(IMG_H, y1));
  x2 = Math.max(0, Math.min(IMG_W, x2));
  y2 = Math.max(0, Math.min(IMG_H, y2));

  return { x1, y1, x2, y2, w: Math.max(1, x2 - x1), h: Math.max(1, y2 - y1) };
}

function isVisibleAtZoom(type, zoom) {
  if (zoom >= LP.zoomThreshAll) return true;
  if (zoom >= LP.zoomThreshMid) return type !== "road_station";
  return type === "city";
}

/* ============================================================
   Miller calibration overlay
   ============================================================ */
function loadMillerCalib(allRecords) {
  try {
    const result = [];
    for (const r of allRecords) {
      const did = Number(r.data_id);
      if (!Number.isFinite(did)) continue;
      const x1 = Number(r.miller_rect_x1);
      const y1 = Number(r.miller_rect_y1);
      const x2 = Number(r.miller_rect_x2);
      const y2 = Number(r.miller_rect_y2);
      if (!(Number.isFinite(x1) && Number.isFinite(y1) &&
            Number.isFinite(x2) && Number.isFinite(y2))) continue;
      result.push({
        data_id:   did,
        record_id: r.record_id || null,
        ulm_id:    r.ulm_id    || null,
        source:    r.source    || null,
        rect_x1:   x1, rect_y1: y1,
        rect_x2:   x2, rect_y2: y2,
        type:      r.type || "road_station",
        latin_std: r.latin_std || r.latin || "",
        modern:    r.modern_preferred || r.modern_tabula || r.modern_omnesviae || "",
        province:  r.province || r.region || "",
        country:   r.country || guessCountryFromLatLng(r.lat, r.lng) || "",
        wiki_url:  r.wiki_url || null,
        lat:       r.lat != null ? Number(r.lat) : null,
        lng:       r.lng != null ? Number(r.lng) : null,
        tabula_segment: r.tabula_segment,
        tabula_row:     r.tabula_row,
        tabula_col:     r.tabula_col,
      });
    }
    return result;
  } catch (e) {
    console.warn("Could not load Miller calibration overlay:", e);
    return [];
  }
}

function startHighlight(place) {
  S.highlightDataId = Number(place.data_id);
  S.highlightUntil  = Date.now() + 20000;
  function tick() {
    renderMarkers();
    if (Date.now() < S.highlightUntil) requestAnimationFrame(tick);
    else { S.highlightDataId = null; renderMarkers(); }
  }
  requestAnimationFrame(tick);
}

function drawUserCrosshairWithLabel(ctx, cx, cy, outsideAngle = null) {
  if (outsideAngle !== null) drawOutsideCrosshair(ctx, cx, cy, outsideAngle);
  else drawUserCrosshair(ctx, cx, cy);
  if (!S.userLocLabel) return;
  ctx.save();
  ctx.font = "bold 11px 'Segoe UI', Arial, sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "top";
  const tw = ctx.measureText(S.userLocLabel).width;
  const px = cx, py = cy + 42; // push label below arrow when outside
  ctx.fillStyle = outsideAngle !== null ? "rgba(80,40,0,0.85)" : "rgba(0,0,0,0.72)";
  ctx.fillRect(px - tw / 2 - 5, py - 2, tw + 10, 16);
  ctx.shadowColor = "rgba(0,0,0,0.0)";
  ctx.fillStyle = outsideAngle !== null ? "#FFB040" : "#ffffff";
  ctx.fillText(S.userLocLabel, px, py);
  ctx.restore();
}

function drawOutsideCrosshair(ctx, cx, cy, arrowAngle) {
  const R = 14, arm = 24;
  ctx.save();
  ctx.globalAlpha = 0.92;
  // White halo
  ctx.strokeStyle = "rgba(255,255,255,0.75)"; ctx.lineWidth = 5;
  ctx.shadowColor = "rgba(0,0,0,0.0)"; ctx.shadowBlur = 0;
  ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2); ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(cx - arm, cy); ctx.lineTo(cx - R - 2, cy);
  ctx.moveTo(cx + R + 2, cy); ctx.lineTo(cx + arm, cy);
  ctx.moveTo(cx, cy - arm); ctx.lineTo(cx, cy - R - 2);
  ctx.moveTo(cx, cy + R + 2); ctx.lineTo(cx, cy + arm);
  ctx.stroke();
  // Orange ring + arms
  ctx.strokeStyle = "#FF8800"; ctx.lineWidth = 2.5;
  ctx.shadowColor = "rgba(0,0,0,0.8)"; ctx.shadowBlur = 6;
  ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2); ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(cx - arm, cy); ctx.lineTo(cx - R - 2, cy);
  ctx.moveTo(cx + R + 2, cy); ctx.lineTo(cx + arm, cy);
  ctx.moveTo(cx, cy - arm); ctx.lineTo(cx, cy - R - 2);
  ctx.moveTo(cx, cy + R + 2); ctx.lineTo(cx, cy + arm);
  ctx.stroke();
  // Outward direction arrow
  const ax = Math.cos(arrowAngle), ay = Math.sin(arrowAngle);
  const aLen = 28, aHead = 10, aSpread = 0.42;
  const sx = cx + ax * (R + 4), sy = cy + ay * (R + 4);
  const ex = cx + ax * (R + aLen), ey = cy + ay * (R + aLen);
  ctx.shadowBlur = 0;
  ctx.strokeStyle = "rgba(255,255,255,0.75)"; ctx.lineWidth = 5;
  ctx.beginPath(); ctx.moveTo(sx, sy); ctx.lineTo(ex, ey); ctx.stroke();
  ctx.strokeStyle = "#FF8800"; ctx.lineWidth = 2.5;
  ctx.beginPath(); ctx.moveTo(sx, sy); ctx.lineTo(ex, ey); ctx.stroke();
  ctx.fillStyle = "#FF8800";
  ctx.beginPath();
  ctx.moveTo(ex, ey);
  ctx.lineTo(ex - aHead * Math.cos(arrowAngle - aSpread), ey - aHead * Math.sin(arrowAngle - aSpread));
  ctx.lineTo(ex - aHead * Math.cos(arrowAngle + aSpread), ey - aHead * Math.sin(arrowAngle + aSpread));
  ctx.closePath(); ctx.fill();
  // Center dot
  ctx.fillStyle = "#fff"; ctx.beginPath(); ctx.arc(cx, cy, 4, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = "#FF8800"; ctx.beginPath(); ctx.arc(cx, cy, 3, 0, Math.PI * 2); ctx.fill();
  ctx.restore();
}

function drawUserCrosshair(ctx, cx, cy) {
  const R = 14, arm = 24;
  ctx.save();
  ctx.globalAlpha = 0.92;

  // White halo for contrast against any background
  ctx.strokeStyle = "rgba(255,255,255,0.75)";
  ctx.lineWidth = 5;
  ctx.shadowColor = "rgba(0,0,0,0.0)";
  ctx.shadowBlur = 0;
  ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2); ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(cx - arm, cy); ctx.lineTo(cx - R - 2, cy);
  ctx.moveTo(cx + R + 2, cy); ctx.lineTo(cx + arm, cy);
  ctx.moveTo(cx, cy - arm); ctx.lineTo(cx, cy - R - 2);
  ctx.moveTo(cx, cy + R + 2); ctx.lineTo(cx, cy + arm);
  ctx.stroke();

  // Red crosshair on top
  ctx.strokeStyle = "#FF2222";
  ctx.lineWidth = 2.5;
  ctx.shadowColor = "rgba(0,0,0,0.8)";
  ctx.shadowBlur = 6;
  ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2); ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(cx - arm, cy); ctx.lineTo(cx - R - 2, cy);
  ctx.moveTo(cx + R + 2, cy); ctx.lineTo(cx + arm, cy);
  ctx.moveTo(cx, cy - arm); ctx.lineTo(cx, cy - R - 2);
  ctx.moveTo(cx, cy + R + 2); ctx.lineTo(cx, cy + arm);
  ctx.stroke();

  // Center dot
  ctx.shadowBlur = 0;
  ctx.fillStyle = "#fff";
  ctx.beginPath(); ctx.arc(cx, cy, 4, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = "#FF2222";
  ctx.beginPath(); ctx.arc(cx, cy, 3, 0, Math.PI * 2); ctx.fill();

  ctx.restore();
}

function drawHighlightRing(ctx, cx, cy, baseR) {
  const now = Date.now();
  ctx.save();
  for (let i = 0; i < 2; i++) {
    const t = ((now + i * 500) % 1000) / 1000;
    ctx.globalAlpha = (1 - t) * 0.85;
    ctx.beginPath();
    ctx.arc(cx, cy, baseR + t * baseR * 2.5, 0, Math.PI * 2);
    ctx.strokeStyle = "#FFD700";
    ctx.lineWidth = 2.5;
    ctx.stroke();
  }
  ctx.restore();
}

function drawSelectionFrame(ctx, x, y, w, h) {
  const pad = 3;
  ctx.save();
  ctx.globalAlpha = 0.9;
  ctx.strokeStyle = "#FFD700";
  ctx.lineWidth = 2.5;
  ctx.strokeRect(x - pad, y - pad, w + pad * 2, h + pad * 2);
  ctx.globalAlpha = 0.18;
  ctx.fillStyle = "#FFD700";
  ctx.fillRect(x - pad, y - pad, w + pad * 2, h + pad * 2);
  ctx.restore();
}

function renderMillerOverlay(ctx) {
  if (!S.viewer || !S.viewer.viewport) return false;
  const vp = S.viewer.viewport;
  const bounds = vp.getBounds(true);
  const zoom = vp.getZoom(true);

  const maxMLabels = S.isMobile ? LP.maxLabelsMobile : LP.maxLabelsDesktop;
  const MPAD = LP.labelPad;

  // Pass 1: draw markers in z-order, collect label candidates with geometry
  let highlightDrawn = false;
  const mLabelCandidates = [];
  const renderCalib = [...S.millerCalib].sort(
    (a, b) => (TYPE_DRAW_ORDER[a.type] ?? 4) - (TYPE_DRAW_ORDER[b.type] ?? 4)
  );
  for (const item of renderCalib) {
    if (!S.activeTypes.has(item.type)) continue;
    const vx1 = item.rect_x1 / MILLER_W;
    const vx2 = item.rect_x2 / MILLER_W;
    const vy1 = item.rect_y1 / MILLER_W;
    const vy2 = item.rect_y2 / MILLER_W;
    if (vx2 < bounds.x || vx1 > bounds.x + bounds.width) continue;
    if (vy2 < bounds.y || vy1 > bounds.y + bounds.height) continue;

    const p1 = imageToCanvas(item.rect_x1, item.rect_y1);
    const p2 = imageToCanvas(item.rect_x2, item.rect_y2);
    const x = Math.min(p1.cx, p2.cx);
    const y = Math.min(p1.cy, p2.cy);
    const w = Math.max(1, Math.abs(p2.cx - p1.cx));
    const h = Math.max(1, Math.abs(p2.cy - p1.cy));
    const color = TYPE_COLORS[item.type] || "#92400E";

    if (S.markersOn) {
      const ma = LP.markerAlpha ?? 1.0;
      const isArea = ["region", "roman_province", "modern_state", "people"].includes(item.type);
      if (isArea) {
        ctx.fillStyle = color;
        ctx.globalAlpha = 0.15 * ma;
        ctx.fillRect(x, y, w, h);
        ctx.globalAlpha = 0.6 * ma;
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.setLineDash([8, 5]);
        ctx.strokeRect(x, y, w, h);
        ctx.setLineDash([]);
        ctx.globalAlpha = 1;
      } else {
        ctx.fillStyle = color;
        ctx.globalAlpha = 0.23 * ma;
        ctx.fillRect(x, y, w, h);
        ctx.globalAlpha = 0.65 * ma;
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.5;
        ctx.strokeRect(x, y, w, h);
        ctx.globalAlpha = 1;
      }
    }

    if (item.data_id === S.selectedDataId) {
      drawSelectionFrame(ctx, x, y, w, h);
    }
    if (item.data_id === S.highlightDataId && Date.now() < S.highlightUntil) {
      drawHighlightRing(ctx, x + w / 2, y + h / 2, Math.max(w, h) / 2 + 4);
      highlightDrawn = true;
    }

    if (S.labelsOn) {
      const txt2 = item.latin_std || "";
      const txt1 = truncWords(item.modern, 4) || "";
      if (txt1 || txt2) mLabelCandidates.push({ item, x, y, w, h, txt1, txt2 });
    }
  }
  ctx.globalAlpha = 1;

  // Pass 2: draw labels in priority order (cities/temples/spas first)
  if (S.labelsOn && mLabelCandidates.length) {
    const mfs = computeFont(zoom);
    if (mfs > 0) {
      mLabelCandidates.sort(
        (a, b) => (TYPE_LABEL_PRIORITY[a.item.type] ?? 2) - (TYPE_LABEL_PRIORITY[b.item.type] ?? 2)
      );
      const charW = mfs * 0.55;
      const lineH = mfs * 1.3;
      const fsBold = Math.round(mfs);
      const fsNorm = Math.max(6, fsBold - 1);
      const skipOverlap = zoom >= (S.isMobile ? LP.labelPadZoomThreshMobile : LP.labelPadZoomThresh);
      const mLabelRects = [];
      let mLabelCount = 0;
      for (const { x, y, w, h, txt1, txt2 } of mLabelCandidates) {
        if (mLabelCount >= maxMLabels) break;
        const boxW = Math.max(txt1.length, txt2.length) * charW;
        const boxH = (txt2 ? lineH : 0) + (txt1 ? lineH : 0);
        const bx = x + 2;
        const by = y + Math.max(2, h - boxH - 2) + lineH * 0.3;
        let overlaps = false;
        if (!skipOverlap) {
          for (const r of mLabelRects) {
            if (bx < r.x2 && bx + boxW > r.x1 && by < r.y2 && by + boxH > r.y1) {
              overlaps = true; break;
            }
          }
        }
        if (!overlaps) {
          mLabelRects.push({ x1: bx - MPAD, y1: by - MPAD,
                             x2: bx + Math.min(boxW, w) + MPAD, y2: by + boxH + MPAD });
          mLabelCount++;
          ctx.save();
          ctx.strokeStyle = "rgba(0,0,0,0.8)";
          ctx.lineWidth = 3;
          ctx.lineJoin = "round";
          let dy = by;
          if (txt2) {
            ctx.font = `${fsNorm}px 'Segoe UI', system-ui, sans-serif`;
            ctx.textBaseline = "top";
            ctx.strokeText(txt2, bx, dy);
            ctx.fillStyle = "#e5e7eb";
            ctx.fillText(txt2, bx, dy);
            dy += lineH;
          }
          if (txt1) {
            ctx.font = `bold ${fsBold}px 'Segoe UI', system-ui, sans-serif`;
            ctx.textBaseline = "top";
            ctx.strokeText(txt1, bx, dy);
            ctx.fillStyle = "#ffffff";
            ctx.fillText(txt1, bx, dy);
          }
          ctx.restore();
        }
      }
    }
  }

  return highlightDrawn;
}

function renderMarkers() {
  if (!S.viewer || !S.ctx) return;
  const ctx = S.ctx;
  const el = S.viewer.element;
  // Re-sync canvas if the element has been resized (catches startup layout settle on large screens)
  const dpr = window.devicePixelRatio || 1;
  if (S.canvas.width !== el.clientWidth * dpr || S.canvas.height !== el.clientHeight * dpr) {
    sizeCanvas();
  }
  ctx.clearRect(0, 0, S.canvas.width, S.canvas.height);

  let highlightDrawn = false;
  if (S.millerOverlayOn && S.millerCalib.length && S.mapMode === "old")
    highlightDrawn = renderMillerOverlay(ctx) || false;

  // User location crosshair (old map / stitched path)
  if (S.mapMode === "old" || S.newSourceKind === "stitched" || !S.places.length) {
    if (S.userLocVp) {
      const { cx, cy } = viewportToCanvas(S.userLocVp.vx, S.userLocVp.vy);
      let outsideAngle = null;
      if (S.userLocOutside && S.userLocCentVp) {
        const { cx: ccx, cy: ccy } = viewportToCanvas(S.userLocCentVp.vx, S.userLocCentVp.vy);
        outsideAngle = Math.atan2(cy - ccy, cx - ccx);
      }
      drawUserCrosshairWithLabel(ctx, cx, cy, outsideAngle);
    }
    return;
  }

  const vp = S.viewer.viewport;
  const zoom = vp.getZoom(true);
  const bounds = vp.getBounds(true);

  const bx0 = bounds.x;
  const bx1 = bounds.x + bounds.width;
  const by0 = bounds.y;
  const by1 = bounds.y + bounds.height;

  const MAX_LABELS  = S.isMobile ? LP.maxLabelsMobile : LP.maxLabelsDesktop;
  const LABEL_PAD   = LP.labelPad;
  let rendered = 0;

  // Pass 1: draw markers in z-order, collect label + region candidates with cached geometry
  const renderPlaces = [...S.places].sort(
    (a, b) => (TYPE_DRAW_ORDER[a.type] ?? 4) - (TYPE_DRAW_ORDER[b.type] ?? 4)
  );

  const labelCandidates = [];

  for (const p of renderPlaces) {
    if (!S.activeTypes.has(p.type)) continue;
    if (p.vx < bx0 || p.vx > bx1 || p.vy < by0 || p.vy > by1) continue;
    if (!isVisibleAtZoom(p.type, zoom)) continue;

    const rr = placeRectCorners(p);
    const p1 = imageToCanvas(rr.x1, rr.y1);
    const p2 = imageToCanvas(rr.x2, rr.y2);
    const x = Math.min(p1.cx, p2.cx);
    const y = Math.min(p1.cy, p2.cy);
    const w = Math.max(1, Math.abs(p2.cx - p1.cx));
    const h = Math.max(1, Math.abs(p2.cy - p1.cy));
    const cx = (p1.cx + p2.cx) / 2;
    const cy = (p1.cy + p2.cy) / 2;
    const color = TYPE_COLORS[p.type] || "#92400E";
    const isRegion = p.type === "region";

    if (S.markersOn) {
      const ma = LP.markerAlpha ?? 1.0;
      if (isRegion) {
        ctx.fillStyle = color;
        ctx.globalAlpha = 0.07 * ma;
        ctx.fillRect(x, y, w, h);
        ctx.globalAlpha = 0.35 * ma;
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.5;
        ctx.setLineDash([7, 5]);
        ctx.strokeRect(x, y, w, h);
        ctx.setLineDash([]);
        ctx.globalAlpha = 1;
      } else {
        ctx.fillStyle = color;
        ctx.globalAlpha = 0.23 * ma;
        ctx.fillRect(x, y, w, h);
        ctx.globalAlpha = 0.65 * ma;
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.5;
        ctx.strokeRect(x, y, w, h);
        ctx.globalAlpha = 1;
      }
    }

    if (p.data_id === S.selectedDataId) {
      drawSelectionFrame(ctx, x, y, w, h);
    }
    if (p.data_id === S.highlightDataId && Date.now() < S.highlightUntil) {
      drawHighlightRing(ctx, cx, cy, Math.max(w, h) / 2 + 4);
      highlightDrawn = true;
    }

    if (S.labelsOn) {
      const latin  = p.latin_std || p.latin || null;
      const modern = truncWords(p.modern, 4) || null;
      if (latin || modern) labelCandidates.push({ p, x, y, w, h, cx, cy, color, isRegion, latin, modern });
    }
    rendered++;
  }

  // Pass 2: draw labels — regions inline (no budget), point features in priority order
  if (S.labelsOn && labelCandidates.length) {
    const fontSize = computeFont(zoom);
    if (fontSize > 0) {
      const regionFs  = Math.max(7, Math.round(fontSize * 1.4));
      const fsBold    = Math.round(fontSize);
      const fsNorm    = Math.max(6, fsBold - 1);
      const charW     = fontSize * 0.55;
      const lineH     = fontSize * 1.3;
      const skipOverlap = zoom >= (S.isMobile ? LP.labelPadZoomThreshMobile : LP.labelPadZoomThresh);
      const labelRects2 = [];
      let labelCount2 = 0;

      // Region labels first (always shown, no budget limit)
      for (const { cx, cy, color, latin, modern, isRegion } of labelCandidates) {
        if (!isRegion) continue;
        const label = (latin || modern || "").toUpperCase();
        ctx.save();
        ctx.font = `italic ${regionFs}px 'Segoe UI', system-ui, sans-serif`;
        ctx.textBaseline = "middle";
        ctx.textAlign = "center";
        ctx.strokeStyle = "rgba(0,0,0,0.7)";
        ctx.lineWidth = 3;
        ctx.lineJoin = "round";
        ctx.strokeText(label, cx, cy);
        ctx.fillStyle = color;
        ctx.globalAlpha = 0.85;
        ctx.fillText(label, cx, cy);
        ctx.globalAlpha = 1;
        ctx.restore();
      }

      // Point-feature labels in priority order (city/temple/spa first)
      const pointCandidates = labelCandidates.filter(c => !c.isRegion)
        .sort((a, b) => (TYPE_LABEL_PRIORITY[a.p.type] ?? 2) - (TYPE_LABEL_PRIORITY[b.p.type] ?? 2));
      for (const { x, y, w, h, latin, modern } of pointCandidates) {
        if (labelCount2 >= MAX_LABELS) break;
        const boxW = Math.max(modern ? modern.length * charW : 0, latin ? latin.length * charW : 0);
        const boxH = (latin ? lineH : 0) + (modern ? lineH : 0);
        const bx = x + 2;
        const by = y + Math.max(2, h - boxH - 2) + lineH * 0.3;
        let overlaps = false;
        if (!skipOverlap) {
          for (const r of labelRects2) {
            if (bx < r.x2 && bx + boxW > r.x1 && by < r.y2 && by + boxH > r.y1) {
              overlaps = true; break;
            }
          }
        }
        if (!overlaps) {
          labelRects2.push({ x1: bx - LABEL_PAD, y1: by - LABEL_PAD,
                             x2: bx + Math.min(boxW, w) + LABEL_PAD, y2: by + boxH + LABEL_PAD });
          labelCount2++;
          ctx.save();
          ctx.strokeStyle = "rgba(0,0,0,0.8)";
          ctx.lineWidth = 3;
          ctx.lineJoin = "round";
          let dy = by;
          if (latin) {
            ctx.font = `${fsNorm}px 'Segoe UI', system-ui, sans-serif`;
            ctx.textBaseline = "top";
            ctx.strokeText(latin, bx, dy);
            ctx.fillStyle = "#e5e7eb";
            ctx.fillText(latin, bx, dy);
            dy += lineH;
          }
          if (modern) {
            ctx.font = `bold ${fsBold}px 'Segoe UI', system-ui, sans-serif`;
            ctx.textBaseline = "top";
            ctx.strokeText(modern, bx, dy);
            ctx.fillStyle = "#ffffff";
            ctx.fillText(modern, bx, dy);
          }
          ctx.restore();
        }
      }
    }
  }

  // Fallback: draw a dot + ring at the estimated position when no real marker was rendered
  if (!highlightDrawn && S.highlightDataId && Date.now() < S.highlightUntil && S.highlightVp) {
    const { cx, cy } = viewportToCanvas(S.highlightVp.vx, S.highlightVp.vy);
    const hlPlace = S.places.find(p => p.data_id === S.highlightDataId);
    const color = hlPlace ? (TYPE_COLORS[hlPlace.type] || "#92400E") : "#92400E";
    ctx.save();
    ctx.globalAlpha = 0.9;
    ctx.beginPath();
    ctx.arc(cx, cy, 7, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();
    ctx.strokeStyle = "rgba(255,255,255,0.7)";
    ctx.lineWidth = 1.5;
    ctx.stroke();
    ctx.restore();
    drawHighlightRing(ctx, cx, cy, 11);
  }

  // User location crosshair (seg4 path)
  if (S.userLocVp) {
    const { cx, cy } = viewportToCanvas(S.userLocVp.vx, S.userLocVp.vy);
    let outsideAngle = null;
    if (S.userLocOutside && S.userLocCentVp) {
      const { cx: ccx, cy: ccy } = viewportToCanvas(S.userLocCentVp.vx, S.userLocCentVp.vy);
      outsideAngle = Math.atan2(cy - ccy, cx - ccx);
    }
    drawUserCrosshairWithLabel(ctx, cx, cy, outsideAngle);
  }
}

/* ============================================================
   Hit-test (find place under cursor)
   ============================================================ */
function hitTest(clientX, clientY) {
  if (!S.viewer || !S.markersOn || S.mapMode === "old" || S.newSourceKind === "stitched") return null;
  const vp = S.viewer.viewport;
  const zoom = vp.getZoom(true);
  const elRect = S.viewer.element.getBoundingClientRect();
  const ex = clientX - elRect.left;
  const ey = clientY - elRect.top;

  let best = null;
  let bestDist = Infinity;
  const threshold = 6;

  for (const p of S.places) {
    if (!S.activeTypes.has(p.type)) continue;
    if (!isVisibleAtZoom(p.type, zoom)) continue;
    const rr = placeRectCorners(p);
    const p1 = imageToCanvas(rr.x1, rr.y1);
    const p2 = imageToCanvas(rr.x2, rr.y2);
    const x0 = Math.min(p1.cx, p2.cx) - threshold;
    const x1 = Math.max(p1.cx, p2.cx) + threshold;
    const y0 = Math.min(p1.cy, p2.cy) - threshold;
    const y1 = Math.max(p1.cy, p2.cy) + threshold;
    const cx = (p1.cx + p2.cx) / 2;
    const cy = (p1.cy + p2.cy) / 2;

    if (ex >= x0 && ex <= x1 && ey >= y0 && ey <= y1) {
      const dx = cx - ex;
      const dy = cy - ey;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < bestDist) {
        bestDist = dist;
        best = p;
      }
    }
  }
  return best;
}

/* ============================================================
   Tooltip
   ============================================================ */
function showTooltip(place, x, y) {
  const tt = document.getElementById("tooltip");
  const color = TYPE_COLORS[place.type] || "#92400E";
  const typeLabel = TYPE_LABELS[place.type] || place.type;
  const typeIcon = TYPE_ICONS[place.type] || "📍";
  const displayLatin = place.latin_std || place.latin;
  const flagHtml = countryFlagHtml(place.country);
  const segNum = Number(place.tabula_segment ?? place.segment);
  const segMeta = Number.isFinite(segNum) ? S.segments.find(s => Number(s.number) === segNum) : null;
  const segLine = segMeta ? `<div class="tt-detail">Segment: <span>${escHtml(segMeta.roman + " – " + segMeta.label)}</span></div>` : "";
  const provLine = place.province ? `<div class="tt-detail">Province: <span>${escHtml(place.province)}</span></div>` : "";
  tt.innerHTML = `
    <div class="tt-latin">${escHtml(displayLatin)}</div>
    ${place.modern ? `<div class="tt-modern">${escHtml(place.modern)}</div>` : ""}
    ${flagHtml ? `<div class="tt-country">${flagHtml}<span class="tt-country-name">${escHtml(place.country || "")}</span></div>` : ""}
    <div class="tt-type"><span class="dot" style="background:${color}"></span><span class="tt-type-icon">${typeIcon}</span>${typeLabel}</div>
    ${provLine}${segLine}
  `;
  tt.style.left = (x + 18) + "px";
  tt.style.top  = (y - 12) + "px";
  tt.classList.remove("hidden");

  const rect = tt.getBoundingClientRect();
  if (rect.right > window.innerWidth - 8) tt.style.left = (x - rect.width - 12) + "px";
  if (rect.bottom > window.innerHeight - 8) tt.style.top = (y - rect.height - 4) + "px";
}

function hideTooltip() {
  const tt = document.getElementById("tooltip");
  tt.classList.add("hidden");
  tt.classList.remove("tt-rich");
}

/* ============================================================
   Miller overlay hit-test & rich tooltip
   ============================================================ */
function hitTestMillerOverlay(clientX, clientY) {
  if (!S.millerOverlayOn || !S.millerCalib.length || !S.viewer || S.mapMode !== "old") return null;
  const elRect = S.viewer.element.getBoundingClientRect();
  const ex = clientX - elRect.left;
  const ey = clientY - elRect.top;
  const pad = 4;

  // Two-pass hit-test: point types always win over area types.
  // All markers are hittable regardless of which type filters are active.
  const AREA_TYPES = new Set(["region", "roman_province", "modern_state", "people"]);
  const inBounds = (item) => {
    const p1 = imageToCanvas(item.rect_x1, item.rect_y1);
    const p2 = imageToCanvas(item.rect_x2, item.rect_y2);
    return ex >= Math.min(p1.cx, p2.cx) - pad && ex <= Math.max(p1.cx, p2.cx) + pad &&
           ey >= Math.min(p1.cy, p2.cy) - pad && ey <= Math.max(p1.cy, p2.cy) + pad;
  };
  // Pass 1: point types (cities, road_stations, etc.) — always take priority
  for (const item of S.millerCalibHit) {
    if (!AREA_TYPES.has(item.type) && inBounds(item)) return item;
  }
  // Pass 2: area types (regions, people) — only when no point type was at this position
  for (const item of S.millerCalibHit) {
    if (AREA_TYPES.has(item.type) && inBounds(item)) return item;
  }
  return null;
}

function showMillerTooltip(item, x, y) {
  const tt = document.getElementById("tooltip");
  const color = TYPE_COLORS[item.type] || "#92400E";
  const typeLabel = TYPE_LABELS[item.type] || item.type;
  const typeIcon = TYPE_ICONS[item.type] || "📍";
  const flagHtml = countryFlagHtml(item.country);

  tt.innerHTML = `
    <div class="tt-latin">${escHtml(item.latin_std || String(item.data_id))}</div>
    ${item.modern   ? `<div class="tt-modern">${escHtml(item.modern)}</div>` : ""}
    ${flagHtml ? `<div class="tt-country">${flagHtml}<span class="tt-country-name">${escHtml(item.country || "")}</span></div>` : ""}
    <div class="tt-type"><span class="dot" style="background:${color}"></span><span class="tt-type-icon">${typeIcon}</span>${typeLabel}</div>
    ${item.province ? `<div class="tt-detail">Province: <span>${escHtml(item.province)}</span></div>` : ""}
  `;
  tt.classList.add("tt-rich");
  tt.style.left = (x + 80) + "px";
  tt.style.top  = (y - 8) + "px";
  tt.classList.remove("hidden");

  // Reposition if off-screen
  const rect = tt.getBoundingClientRect();
  if (rect.right  > window.innerWidth)  tt.style.left = (x - rect.width  - 60) + "px";
  if (rect.bottom > window.innerHeight) tt.style.top  = (y - rect.height - 8) + "px";
}

/* ============================================================
   Info Panel
   ============================================================ */
function showInfoPanel(place) {
  S.selectedPlace = place;
  S.selectedDataId = place.data_id != null ? Number(place.data_id) : null;
  renderMarkers();
  infoPanelOpenedAt = Date.now();

  // Enrich with allRecords data (places.json lacks ulm_img_url / ulm_id)
  if (S.allRecords.length && (!place.ulm_img_url || !place.ulm_id)) {
    const rec = S.allRecords.find(r =>
      (place.data_id != null && r.data_id === place.data_id) ||
      (place.id      && (r.record_id === place.id || r.id === place.id))
    );
    if (rec) {
      if (!place.ulm_img_url && rec.ulm_img_url) place = { ...place, ulm_img_url: rec.ulm_img_url };
      if (!place.ulm_id      && rec.ulm_id)      place = { ...place, ulm_id: rec.ulm_id };
    }
  }

  const panel = document.getElementById("info-panel");
  document.getElementById("panel-latin").textContent = place.latin_std || place.latin;
  document.getElementById("panel-modern").textContent = place.modern || getText("unknown_modern");

  const color = TYPE_COLORS[place.type] || "#92400E";
  const typeLabel = getText(place.type) || TYPE_LABELS[place.type] || place.type;
  panel.querySelector(".type-dot").style.background = color;
  panel.querySelector(".type-label").textContent = typeLabel;
  const typeIconEl = panel.querySelector(".type-icon");
  if (typeIconEl) typeIconEl.textContent = TYPE_ICONS[place.type] || "📍";

  // Country shown in header, right after modern name
  const panelCountry = document.getElementById("panel-country");
  if (panelCountry) {
    if (place.country) {
      const flagHtml = countryFlagHtml(place.country);
      const names = place.country.split("|").map(c => countryName(c)).filter(Boolean).join(" / ");
      panelCountry.innerHTML = (flagHtml ? flagHtml + " " : "") + escHtml(names);
      panelCountry.classList.remove("hidden");
    } else {
      panelCountry.innerHTML = "";
      panelCountry.classList.add("hidden");
    }
  }

  const dl = document.getElementById("panel-details");
  dl.innerHTML = "";

  const segNum = Number(place.tabula_segment ?? place.segment ?? S.selectedSegment);
  const segMeta = S.segments.find((s) => Number(s.number) === segNum);
  const segLabel = segMeta ? `${segMeta.roman} - ${segMeta.label}` : (Number.isFinite(segNum) ? `Segment ${segNum}` : "");

  const segBadge = document.getElementById("panel-segment-badge");
  if (segBadge) {
    if (segLabel) {
      segBadge.textContent = segLabel;
      segBadge.classList.remove("hidden");
    } else {
      segBadge.classList.add("hidden");
    }
  }

  const items = [
    [getText("province"), place.province],
  ];

  for (const [label, value] of items) {
    if (!value) continue;
    const dt = document.createElement("dt");
    dt.textContent = label;
    const dd = document.createElement("dd");
    dd.textContent = value;
    dl.appendChild(dt);
    dl.appendChild(dd);
  }

  // OSM map (interactive — placed in panel so user can zoom/pan it)
  const panelMap = document.getElementById("panel-map");
  const lat = Number(place.lat), lng = Number(place.lng);
  if (panelMap) {
    const hasCoords = place.lat != null && place.lng != null &&
                      Number.isFinite(lat) && Number.isFinite(lng) &&
                      lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180;
    if (hasCoords) {
      const dLon = 0.9, dLat = 0.55;
      const bbox = `${(lng-dLon).toFixed(4)},${(lat-dLat).toFixed(4)},${(lng+dLon).toFixed(4)},${(lat+dLat).toFixed(4)}`;
      const src = `https://www.openstreetmap.org/export/embed.html?bbox=${bbox}&layer=mapnik&marker=${lat.toFixed(5)},${lng.toFixed(5)}`;
      panelMap.innerHTML = `<iframe loading="lazy" src="${escHtml(src)}" title="Location on OpenStreetMap"></iframe>`;
      panelMap.classList.remove("hidden");
    } else {
      panelMap.innerHTML = "";
      panelMap.classList.add("hidden");
    }
  }

  // ULM image preview (desktop only — hidden via CSS on mobile)
  const ulmSection = document.getElementById("panel-ulm-section");
  const ulmLabel = document.getElementById("panel-ulm-label");
  if (ulmSection) {
    const ulmHref = tpOnlineHref(place);
    const ulmImg = document.getElementById("panel-ulm-img");
    const ulmLinkEl = document.getElementById("panel-ulm-link");
    if (place.ulm_img_url) {
      if (ulmImg) ulmImg.src = place.ulm_img_url;
      if (ulmLinkEl) ulmLinkEl.href = ulmHref || "#";
      ulmSection.classList.remove("hidden");
      if (ulmLabel) ulmLabel.classList.remove("hidden");
    } else {
      if (ulmImg) ulmImg.src = "";
      ulmSection.classList.add("hidden");
      if (ulmLabel) ulmLabel.classList.add("hidden");
    }
  }

  // Wikipedia link: only show when a verified wiki_url is in the DB
  const wikiLink = document.getElementById("panel-wiki-link");
  const wikiSummary = document.getElementById("panel-wiki-summary");
  const wikiImg = document.getElementById("panel-wiki-img");
  if (wikiSummary) { wikiSummary.textContent = ""; wikiSummary.classList.add("hidden"); }
  if (wikiImg) { wikiImg.src = ""; wikiImg.classList.add("hidden"); }
  const wikiSection = document.getElementById("panel-wiki-section");
  if (wikiSection) wikiSection.classList.remove("has-image");
  const reqId = ++wikiRequestId;
  if (wikiLink) {
    if (place.wiki_url) {
      wikiLink.textContent = getText("wiki_link");
      wikiLink.href = place.wiki_url;
      wikiLink.classList.remove("hidden");
      resolveWikiSummaryFromUrl(reqId, wikiSummary, place.wiki_url);
    } else {
      wikiLink.classList.add("hidden");
    }
  }

  // tp-online (Ulm database)
  const tpLink = document.getElementById("panel-tp-link");
  if (tpLink) {
    const href = tpOnlineHref(place);
    if (href) {
      tpLink.href = href;
      tpLink.textContent = getText("ulm_link");
      tpLink.classList.remove("hidden");
    } else {
      tpLink.classList.add("hidden");
    }
  }

  updateLangButtons();

  // Email button — pre-fill subject/body with place details
  const emailBtn = document.getElementById("panel-email-btn");
  if (emailBtn) {
    const placeName = place.latin_std || place.latin || place.modern || "this place";
    const modern = place.modern ? ` (${place.modern})` : "";
    const subject = encodeURIComponent(`Tabula Peutingeriana — ${placeName}${modern}`);
    const body = encodeURIComponent(
      `I found this entry in the Tabula Peutingeriana index:\n\nLatin: ${placeName}${modern}\nType: ${place.type || "—"}\nLocation: ${place.tabula_location || "—"}\n`
      + (place.wiki_url ? `Wikipedia: ${place.wiki_url}\n` : "")
    );
    emailBtn.href = `mailto:info@three-mills.com?subject=${subject}&body=${body}`;
  }

  panel.classList.remove("hidden");
}

function hideInfoPanel() {
  document.getElementById("info-panel").classList.add("hidden");
  S.selectedPlace = null;
  S.selectedDataId = null;
  renderMarkers();
}

/* ============================================================
   Search
   ============================================================ */
function setupSearch() {
  const input = document.getElementById("search-input");
  const results = document.getElementById("search-results");
  let debounce = null;

  input.addEventListener("input", () => {
    clearTimeout(debounce);
    debounce = setTimeout(() => {
      const q = input.value.trim().toLowerCase();
      if (q.length < 2) { results.classList.add("hidden"); return; }

      const pool = S.allRecords.length ? S.allRecords : S.places;
      const matches = pool.filter(p => {
        const lat = (p.latin_std || p.latin || "").toLowerCase();
        const latRaw = (p.latin || "").toLowerCase();
        const mod = (p.modern || "").toLowerCase();
        return lat.includes(q) || latRaw.includes(q) || mod.includes(q);
      }).slice(0, 30);

      if (!matches.length) { results.classList.add("hidden"); return; }

      results.innerHTML = matches.map(p => {
        const color = TYPE_COLORS[p.type] || "#92400E";
        return `<div class="search-item" data-id="${p.id}">
          <span class="dot" style="background:${color}"></span>
          <span class="si-latin">${escHtml(p.latin_std || p.latin)}</span>
          <span class="si-modern">${escHtml(p.modern || "")}</span>
        </div>`;
      }).join("");
      results.classList.remove("hidden");
    }, 200);
  });

  results.addEventListener("click", (e) => {
    const item = e.target.closest(".search-item");
    if (!item) return;
    const id = item.dataset.id;
    const pool = S.allRecords.length ? S.allRecords : S.places;
    const place = pool.find(p => String(p.id) === id);
    if (!place) return;

    // Ensure the place's type is visible before navigating
    if (place.type && !S.activeTypes.has(place.type)) {
      S.activeTypes.add(place.type);
      document.querySelectorAll(`.type-filter-btn[data-type="${place.type}"]`)
        .forEach(b => b.classList.add("active"));
    }

    panToPlace(place);
    startHighlight(place);
    showInfoPanel(place);
    renderMarkers();

    results.classList.add("hidden");
    input.value = "";
  });

  document.addEventListener("click", (e) => {
    if (!e.target.closest("#search-container")) {
      results.classList.add("hidden");
    }
  });
}

// Returns viewport {vx,vy} of a place without any panning side-effect.
function placeVp(place) {
  if (S.mapMode === "old") {
    const mc = S.millerCalib.find(m => m.data_id === place.data_id);
    if (mc) return { vx: (Number(mc.rect_x1) + Number(mc.rect_x2)) / 2 / MILLER_W,
                    vy: (Number(mc.rect_y1) + Number(mc.rect_y2)) / 2 / MILLER_W };
    const millerAspect = MILLER_H / MILLER_W;
    const seg = Number(place.tabula_segment), segIdx = Number.isFinite(seg) ? seg - 2 : 5;
    const rowMap = { a: 1 / 6, b: 1 / 2, c: 5 / 6 };
    return { vx: (segIdx + 0.5) / 11, vy: (rowMap[place.tabula_row] ?? 0.5) * millerAspect };
  }
  const vx = Number(place.vx), vy = Number(place.vy);
  return { vx: Number.isFinite(vx) ? vx : 0.5, vy: Number.isFinite(vy) ? vy : 0.5 };
}

function panToPlace(place, hw = null) {
  if (S.mapMode === "old") {
    const millerAspect = MILLER_H / MILLER_W;
    const mhw = hw ?? (S.isMobile ? 0.008 : 0.02);
    const mc = S.millerCalib.find(m => m.data_id === place.data_id);
    if (mc) {
      const cx = (mc.rect_x1 + mc.rect_x2) / 2 / MILLER_W;
      const cy = (mc.rect_y1 + mc.rect_y2) / 2 / MILLER_W;
      S.highlightVp = { vx: cx, vy: cy };
      S.viewer.viewport.fitBounds(
        new OpenSeadragon.Rect(cx - mhw, cy - mhw * millerAspect, mhw * 2, mhw * 2 * millerAspect)
      );
    } else {
      // Estimate from tabula segment/row when no calibration exists
      const seg = Number(place.tabula_segment);
      const segIdx = Number.isFinite(seg) ? (seg - 2) : 5;
      const estVx = (segIdx + 0.5) / 11;
      const rowMap = { a: 1 / 6, b: 1 / 2, c: 5 / 6 };
      const estVy = (rowMap[place.tabula_row] ?? 0.5) * millerAspect;
      S.highlightVp = { vx: estVx, vy: estVy };
      S.viewer.viewport.fitBounds(
        new OpenSeadragon.Rect(estVx - mhw, estVy - mhw * millerAspect, mhw * 2, mhw * 2 * millerAspect)
      );
    }
    return;
  }
  if (S.newSourceKind === "stitched") {
    const statusEl = document.getElementById("status");
    if (statusEl) statusEl.textContent = "Place overlays are calibrated for the readable 150dpi segment IV source.";
    return;
  }
  const aspect = IMG_H / IMG_W;
  const vx = Number.isFinite(place.vx) ? place.vx : 0.5;
  const vy = Number.isFinite(place.vy) ? place.vy : 0.5;
  S.highlightVp = { vx, vy };
  const usedHw = hw ?? (S.isMobile ? 0.008 : 0.02);
  S.viewer.viewport.fitBounds(
    new OpenSeadragon.Rect(vx - usedHw, vy - usedHw * aspect, usedHw * 2, usedHw * 2 * aspect)
  );
}

/* ============================================================
   Locate Me — crosshair + location popup
   ============================================================ */
let _leafletMap = null;
let _leafletMarker = null;

const LOCATE_SNAP_KM    = 15;   // snap to nearest place within this distance
const LOCATE_MAX_DIST_KM = 500;  // beyond this: show crosshair at edge of coverage

function locDistKm(lat1, lng1, lat2, lng2) {
  const dlat = lat1 - lat2;
  const dlng = (lng1 - lng2) * Math.cos((lat1 + lat2) / 2 * Math.PI / 180);
  return Math.sqrt(dlat * dlat + dlng * dlng) * 111.32;
}

// maxDistKm: when set, only use places within that radius for IDW (B: keeps edge crosshair
// on the map's visual perimeter by excluding distant interior places from the weight pool).
function interpolateTabulaVp(lat, lng, maxDistKm = Infinity) {
  const millerAspect = MILLER_H / MILLER_W;
  const candidates = [];

  if (S.mapMode === "old") {
    // Primary: calibrated places (precise positions, full weight)
    for (const p of S.millerCalib) {
      const plat = Number(p.lat), plng = Number(p.lng);
      if (!Number.isFinite(plat) || !Number.isFinite(plng)) continue;
      if (!Number.isFinite(Number(p.rect_x1))) continue;
      const vx = (Number(p.rect_x1) + Number(p.rect_x2)) / 2 / MILLER_W;
      const vy = (Number(p.rect_y1) + Number(p.rect_y2)) / 2 / MILLER_W;
      const d = locDistKm(lat, lng, plat, plng);
      candidates.push({ d, vx, vy, w: 1.0 });
    }
    // Secondary: segment/row estimates from all records (coarse but covers all segments)
    // Weight 0.15 — dominant only when no calibrated places are nearby.
    if (S.allRecords.length) {
      const rowMap = { a: 1 / 6, b: 1 / 2, c: 5 / 6 };
      for (const p of S.allRecords) {
        const plat = Number(p.lat), plng = Number(p.lng);
        if (!Number.isFinite(plat) || !Number.isFinite(plng)) continue;
        const seg = Number(p.tabula_segment);
        if (!Number.isFinite(seg) || seg < 2 || seg > 12) continue;
        const vx = ((seg - 2) + 0.5) / 11;
        const vy = (rowMap[p.tabula_row] ?? 0.5) * millerAspect;
        const d = locDistKm(lat, lng, plat, plng);
        candidates.push({ d, vx, vy, w: 0.15 });
      }
    }
  } else {
    for (const p of S.places) {
      const plat = Number(p.lat), plng = Number(p.lng);
      if (!Number.isFinite(plat) || !Number.isFinite(plng)) continue;
      const vx = Number(p.vx), vy = Number(p.vy);
      if (!Number.isFinite(vx) || !Number.isFinite(vy)) continue;
      const d = locDistKm(lat, lng, plat, plng);
      candidates.push({ d, vx, vy, w: 1.0 });
    }
  }

  if (!candidates.length) return null;
  candidates.sort((a, b) => a.d - b.d);
  let top;
  if (maxDistKm < Infinity) {
    const nearby = candidates.filter(c => c.d <= maxDistKm);
    top = nearby.length >= 3 ? nearby.slice(0, 8) : candidates.slice(0, Math.min(3, candidates.length));
  } else {
    top = candidates.slice(0, 8);
  }
  let sumW = 0, sumVx = 0, sumVy = 0;
  for (const c of top) {
    const w = c.w / Math.max(c.d, 0.1) ** 2;
    sumW += w; sumVx += w * c.vx; sumVy += w * c.vy;
  }
  return sumW > 0 ? { vx: sumVx / sumW, vy: sumVy / sumW } : null;
}

// Projects a real-world location onto the edge of the Tabula's geographic bbox.
// Returns { vp, centVp, cLat, cLng, edgeLat, edgeLng } — edge viewport position,
// centroid VP, and centroid lat/lng for compass/arrow direction.
function projectToTabulaEdge(userLat, userLng) {
  const vpPool = S.mapMode === "old" ? S.millerCalib : S.places;
  // Use all known Roman places for the geographic bbox — gives full Tabula coverage
  // (including uncalibrated segments like Iberia) for correct edge projection.
  const geoPool = S.allRecords.length ? S.allRecords : vpPool;
  const millerAspect = MILLER_H / MILLER_W;

  // Geographic bbox from all records
  let minLat = Infinity, maxLat = -Infinity, minLng = Infinity, maxLng = -Infinity;
  let sumLat = 0, sumLng = 0, count = 0;
  for (const p of geoPool) {
    const lat = Number(p.lat), lng = Number(p.lng);
    if (!Number.isFinite(lat) || !Number.isFinite(lng)) continue;
    minLat = Math.min(minLat, lat); maxLat = Math.max(maxLat, lat);
    minLng = Math.min(minLng, lng); maxLng = Math.max(maxLng, lng);
    sumLat += lat; sumLng += lng; count++;
  }
  if (!count) return { vp: null, centVp: null, cLat: 0, cLng: 0, edgeLat: 0, edgeLng: 0 };

  // Viewport bbox: calibrated/placed positions (C — edge clamping)
  let minVx = Infinity, maxVx = -Infinity, minVy = Infinity, maxVy = -Infinity;
  for (const p of vpPool) {
    let vx, vy;
    if (S.mapMode === "old") {
      if (!Number.isFinite(Number(p.rect_x1))) continue;
      vx = (Number(p.rect_x1) + Number(p.rect_x2)) / 2 / MILLER_W;
      vy = (Number(p.rect_y1) + Number(p.rect_y2)) / 2 / MILLER_W;
    } else {
      vx = Number(p.vx); vy = Number(p.vy);
      if (!Number.isFinite(vx) || !Number.isFinite(vy)) continue;
    }
    minVx = Math.min(minVx, vx); maxVx = Math.max(maxVx, vx);
    minVy = Math.min(minVy, vy); maxVy = Math.max(maxVy, vy);
  }
  // Extend viewport bbox with segment/row estimates (Miller mode) so edge clamping
  // reaches uncalibrated segments like Iberia or the far east.
  if (S.mapMode === "old" && S.allRecords.length) {
    const rowMap = { a: 1 / 6, b: 1 / 2, c: 5 / 6 };
    for (const p of S.allRecords) {
      const seg = Number(p.tabula_segment);
      if (!Number.isFinite(seg) || seg < 2 || seg > 12) continue;
      const vx = ((seg - 2) + 0.5) / 11;
      const vy = (rowMap[p.tabula_row] ?? 0.5) * millerAspect;
      minVx = Math.min(minVx, vx); maxVx = Math.max(maxVx, vx);
      minVy = Math.min(minVy, vy); maxVy = Math.max(maxVy, vy);
    }
  }

  const cLat = sumLat / count, cLng = sumLng / count;
  const centVp = interpolateTabulaVp(cLat, cLng);
  const dLat = userLat - cLat, dLng = userLng - cLng;
  let t = Infinity, hitBoundary = "none";
  if (dLat > 0) { const tv = (maxLat - cLat) / dLat; if (tv < t) { t = tv; hitBoundary = "N"; } }
  else if (dLat < 0) { const tv = (minLat - cLat) / dLat; if (tv < t) { t = tv; hitBoundary = "S"; } }
  if (dLng > 0) { const tv = (maxLng - cLng) / dLng; if (tv < t) { t = tv; hitBoundary = "E"; } }
  else if (dLng < 0) { const tv = (minLng - cLng) / dLng; if (tv < t) { t = tv; hitBoundary = "W"; } }
  if (!Number.isFinite(t)) return { vp: centVp, centVp, cLat, cLng, edgeLat: cLat, edgeLng: cLng };
  const edgeLat = Math.max(minLat, Math.min(maxLat, cLat + t * dLat));
  const edgeLng = Math.max(minLng, Math.min(maxLng, cLng + t * dLng));
  let vp = interpolateTabulaVp(edgeLat, edgeLng, 500);
  // C: clamp to actual viewport boundary so crosshair lands on the visual map edge
  if (vp && Number.isFinite(minVx)) {
    vp = { ...vp };
    if (hitBoundary === "N") vp.vy = minVy;
    else if (hitBoundary === "S") vp.vy = maxVy;
    else if (hitBoundary === "E") vp.vx = maxVx;
    else if (hitBoundary === "W") vp.vx = minVx;
  }
  return { vp, centVp, cLat, cLng, edgeLat, edgeLng };
}

function compassBearing(fromLat, fromLng, toLat, toLng) {
  const dLat = toLat - fromLat, dLng = toLng - fromLng;
  const angle = Math.atan2(dLng, dLat) * 180 / Math.PI;
  return ['N','NE','E','SE','S','SW','W','NW'][Math.round(((angle + 360) % 360) / 45) % 8];
}

// Pan + zoom to a viewport position with location-appropriate zoom level.
function panToLocVp(vx, vy) {
  if (!S.viewer?.viewport) return;
  S.highlightVp = { vx, vy };
  const hw = S.isMobile ? 0.011 : 0.033;
  if (S.mapMode === "old") {
    const millerAspect = MILLER_H / MILLER_W;
    S.viewer.viewport.fitBounds(
      new OpenSeadragon.Rect(vx - hw, vy - hw * millerAspect, hw * 2, hw * 2 * millerAspect)
    );
  } else {
    const aspect = IMG_H / IMG_W;
    S.viewer.viewport.fitBounds(
      new OpenSeadragon.Rect(vx - hw, vy - hw * aspect, hw * 2, hw * 2 * aspect)
    );
  }
}

function setUserLocation(lat, lng, isDefault = false) {
  const vpPool = S.mapMode === "old" ? S.millerCalib : S.places;
  // Use all known Roman places for geographic proximity check — this covers all Tabula
  // segments (including uncalibrated Iberia, etc.) so the inside/outside decision is
  // based on real coverage, not just which places happen to be calibrated.
  const geoPool = S.allRecords.length ? S.allRecords : vpPool;
  const AREA_TYPES_LOC = new Set(["region", "roman_province", "modern_state", "people"]);

  // best/bestPoint from vpPool — used for navigation (needs valid vx/vy for highlight)
  let best = null, bestDist = Infinity;
  let bestPoint = null, bestPointDist = Infinity;
  for (const p of vpPool) {
    const plat = Number(p.lat), plng = Number(p.lng);
    if (!Number.isFinite(plat) || !Number.isFinite(plng)) continue;
    const d = (lat - plat) ** 2 + (lng - plng) ** 2;
    if (d < bestDist) { bestDist = d; best = p; }
    if (!AREA_TYPES_LOC.has(p.type) && d < bestPointDist) { bestPointDist = d; bestPoint = p; }
  }
  // geoPoint from allRecords — nearest non-area place by real geography (for coverage decision + info panel)
  let geoPoint = null, geoPointDist = Infinity;
  for (const p of geoPool) {
    const plat = Number(p.lat), plng = Number(p.lng);
    if (!Number.isFinite(plat) || !Number.isFinite(plng)) continue;
    if (AREA_TYPES_LOC.has(p.type)) continue;
    const d = locDistKm(lat, lng, plat, plng);
    if (d < geoPointDist) { geoPointDist = d; geoPoint = p; }
  }

  S.userLocLat = lat;
  S.userLocLng = lng;

  const statusEl = document.getElementById("status");
  const hint = document.getElementById("locate-map-hint");
  const prefix = isDefault ? "Default location — " : "";

  if (best || geoPoint) {
    const refPlace = best || geoPoint;
    const name = (geoPoint || best).latin_std || (geoPoint || best).latin || "";
    const distKm = locDistKm(lat, lng, Number(refPlace.lat), Number(refPlace.lng));
    const distRound = Math.round(distKm);
    // Coverage decision uses geographic distance to nearest known place (any segment)
    const coverDist = geoPointDist < Infinity ? geoPointDist : distKm;

    if (distKm <= LOCATE_SNAP_KM) {
      S.userLocVp = placeVp(best);
      S.userLocLabel = name;
      S.userLocOutside = false; S.userLocCentVp = null;
      startHighlight(best);
      panToLocVp(S.userLocVp.vx, S.userLocVp.vy);
      if (!S.isMobile) showInfoPanel(best);
      if (statusEl) { statusEl.textContent = prefix + `At ${name} (~${distRound} km)`; setTimeout(() => { statusEl.textContent = ""; }, 6000); }
      if (hint) hint.textContent = "Click map or drag marker to set location";
      showLocateMarkerPopup(`${name} (~${distRound} km)`);

    } else if (coverDist <= LOCATE_MAX_DIST_KM) {
      S.userLocVp = interpolateTabulaVp(lat, lng);
      S.userLocLabel = `~${name}`;
      S.userLocOutside = false; S.userLocCentVp = null;
      if (S.userLocVp) panToLocVp(S.userLocVp.vx, S.userLocVp.vy);
      if (!S.isMobile) showInfoPanel(geoPoint || best);
      if (statusEl) { statusEl.textContent = prefix + `Interpolated — nearest: ${name} (~${distRound} km)`; setTimeout(() => { statusEl.textContent = ""; }, 6000); }
      if (hint) hint.textContent = "Click map or drag marker to set location";
      showLocateMarkerPopup(`~${name} (~${distRound} km)`);

    } else {
      const edgeResult = projectToTabulaEdge(lat, lng);
      S.userLocVp = edgeResult.vp;
      S.userLocCentVp = edgeResult.centVp;
      S.userLocOutside = true;
      S.userLocLabel = `${compassBearing(edgeResult.cLat, edgeResult.cLng, lat, lng)} of map`;
      if (S.userLocVp) panToLocVp(S.userLocVp.vx, S.userLocVp.vy);
      // A: find nearest point-type place to the edge position (use geoPool for full coverage)
      let edgeBest = null, edgeBestDist = Infinity;
      for (const p of geoPool) {
        const plat = Number(p.lat), plng = Number(p.lng);
        if (!Number.isFinite(plat) || !Number.isFinite(plng)) continue;
        if (AREA_TYPES_LOC.has(p.type)) continue;
        const d = locDistKm(edgeResult.edgeLat, edgeResult.edgeLng, plat, plng);
        if (d < edgeBestDist) { edgeBestDist = d; edgeBest = p; }
      }
      showInfoPanel(edgeBest || geoPoint || best);
      if (statusEl) { statusEl.textContent = `Outside Tabula coverage — nearest: ${name} (~${distRound} km)`; setTimeout(() => { statusEl.textContent = ""; }, 8000); }
      if (hint) hint.textContent = "Outside Tabula area — click inside the orange box";
      showLocateMarkerPopup(`Outside (~${distRound} km)`);
    }
  }

  renderMarkers();

  if (_leafletMap && _leafletMarker) {
    _leafletMarker.setLatLng([lat, lng]);
  }
}

function showLocateMarkerPopup(text) {
  if (!_leafletMap || !_leafletMarker) return;
  _leafletMarker.bindPopup(text, { closeButton: false, offset: [0, -8], className: "locate-popup", autoPan: false }).openPopup();
}

function loadLeaflet() {
  if (window.L) return Promise.resolve(window.L);
  return new Promise((resolve, reject) => {
    if (!document.getElementById("leaflet-css")) {
      const link = document.createElement("link");
      link.id = "leaflet-css";
      link.rel = "stylesheet";
      link.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
      document.head.appendChild(link);
    }
    const script = document.createElement("script");
    script.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
    script.onload = () => resolve(window.L);
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

async function openLocatePopup() {
  const popup = document.getElementById("locate-map-popup");
  popup.classList.remove("hidden");

  const L = await loadLeaflet();
  const lat = S.userLocLat ?? S.defaultLat;
  const lng = S.userLocLng ?? S.defaultLng;

  const locateZoom = window.innerWidth >= 1000 ? 10 : 9;
  if (!_leafletMap) {
    _leafletMap = L.map("locate-leaflet-map").setView([lat, lng], locateZoom);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a>",
      maxZoom: 19,
    }).addTo(_leafletMap);
    // Tabula coverage bounding box: lat 20–58°N, lng -15–105°E
    L.rectangle([[20, -15], [58, 105]], {
      color: "#c8a050", weight: 1.5,
      fillColor: "#c8a050", fillOpacity: 0.08,
      dashArray: "6 4", interactive: false,
    }).addTo(_leafletMap)
      .bindTooltip("Tabula Peutingeriana coverage area", { sticky: true });

    _leafletMarker = L.marker([lat, lng], { draggable: true }).addTo(_leafletMap);
    _leafletMarker.on("dragend", () => {
      const pos = _leafletMarker.getLatLng();
      setUserLocation(pos.lat, pos.lng);
    });
    _leafletMap.on("click", (e) => {
      _leafletMarker.setLatLng(e.latlng);
      setUserLocation(e.latlng.lat, e.latlng.lng);
    });
  } else {
    _leafletMarker.setLatLng([lat, lng]);
    _leafletMap.panTo([lat, lng]); // preserve user's zoom level on reopen
  }
  setTimeout(() => _leafletMap.invalidateSize(), 60);
}

function closeLocatePopup() {
  document.getElementById("locate-map-popup").classList.add("hidden");
}

function acquireGps(openAfter = false) {
  const done = () => { if (openAfter) openLocatePopup(); };
  const statusEl = document.getElementById("status");
  if (statusEl) statusEl.textContent = "Locating…";
  if (!navigator.geolocation) {
    setUserLocation(S.defaultLat, S.defaultLng, true);
    done();
    return;
  }
  navigator.geolocation.getCurrentPosition(
    pos => { setUserLocation(pos.coords.latitude, pos.coords.longitude); done(); },
    ()  => { setUserLocation(S.defaultLat, S.defaultLng, true); done(); },
    { timeout: 8000 }
  );
}

function locateMe() {
  const statusEl = document.getElementById("status");
  if (statusEl) statusEl.textContent = "Locating…";
  acquireGps(true);
}

/* ============================================================
   Controls
   ============================================================ */

function setupControls() {
  document.getElementById("control-zoom-in").addEventListener("click", () => {
    S.viewer.viewport.zoomBy(1.4);
    S.viewer.viewport.applyConstraints();
  });
  document.getElementById("control-zoom-out").addEventListener("click", () => {
    S.viewer.viewport.zoomBy(0.7);
    S.viewer.viewport.applyConstraints();
  });
  document.getElementById("control-home").addEventListener("click", () => {
    focusStartup();
  });
  document.getElementById("control-fullpage").addEventListener("click", () => {
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else {
      document.documentElement.requestFullscreen();
    }
  });
  document.getElementById("control-locate").addEventListener("click", locateMe);
  document.getElementById("locate-map-close").addEventListener("click", closeLocatePopup);
  document.getElementById("locate-gps-btn").addEventListener("click", acquireGps);
  document.addEventListener("fullscreenchange", () => {
    // Let OSD adapt to the new size after fullscreen transition
    setTimeout(() => renderMarkers(), 150);
  });

  // Calibration overlay toggle
  const overlayBtn = document.getElementById("toggle-overlay");
  if (overlayBtn) {
    overlayBtn.addEventListener("click", () => {
      S.millerOverlayOn = !S.millerOverlayOn;
      overlayBtn.classList.toggle("active", S.millerOverlayOn);
      renderMarkers();
    });
  }

  // Lang selector inside about panel
  document.getElementById("about-panel").addEventListener("click", (e) => {
    const lb = e.target.closest(".lang-btn");
    if (!lb) return;
    setLang(lb.dataset.lang);
  });

  // Close info panel
  document.getElementById("close-panel").addEventListener("click", hideInfoPanel);
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      hideInfoPanel();
      document.getElementById("about-panel")?.classList.add("hidden");
      document.getElementById("about-modal-backdrop")?.classList.add("hidden");
    }
  });
  document.addEventListener("click", (e) => {
    const panel = document.getElementById("info-panel");
    if (!panel.classList.contains("hidden")) {
      if (Date.now() - infoPanelOpenedAt < 150) return;
      if (!e.target.closest("#info-panel")) hideInfoPanel();
    }
  });

  // Swipe-down to close info panel on mobile
  if (S.isMobile) {
    const panel = document.getElementById("info-panel");
    let swipeStartX = null;
    panel.addEventListener("touchstart", (e) => {
      swipeStartX = e.touches[0].clientX;
    }, { passive: true });
    panel.addEventListener("touchend", (e) => {
      if (swipeStartX === null) return;
      const dx = e.changedTouches[0].clientX - swipeStartX;
      if (dx < -60) hideInfoPanel();
      swipeStartX = null;
    }, { passive: true });
  }

  // Mobile menu
  setupMobileMenu();
}

function exitRegionSolo() {
  if (!S.regionSolo) return;
  S.regionSolo = false;
  if (S.savedActiveTypes) {
    S.activeTypes = S.savedActiveTypes;
    S.savedActiveTypes = null;
  }
  document.getElementById("region-solo-btn")?.classList.remove("active");
  document.querySelectorAll("#type-filter-buttons .type-filter-btn").forEach(b => {
    b.classList.toggle("active", S.activeTypes.has(b.dataset.type));
  });
}

function setupTypeFilters() {
  const container = document.getElementById("type-filter-buttons");
  if (!container) return;
  // 'region' and 'roman_province' handled via region-solo button; not used as individual filters
  const types = Object.keys(TYPE_COLORS).filter(t => t !== "region" && t !== "roman_province");
  container.innerHTML = types.map(t => {
    const color = TYPE_COLORS[t];
    const label = TYPE_LABELS[t];
    const active = S.activeTypes.has(t) ? " active" : "";
    return `<button class="type-filter-btn${active}" data-type="${t}" title="${label}">
      <span class="tf-dot" style="background:${color}"></span>${label}
    </button>`;
  }).join("");
  container.addEventListener("click", (e) => {
    const btn = e.target.closest(".type-filter-btn");
    if (!btn) return;
    // Exit region solo if active so standard filters take effect
    if (S.regionSolo) exitRegionSolo();
    const type = btn.dataset.type;
    if (S.activeTypes.has(type)) {
      S.activeTypes.delete(type);
      btn.classList.remove("active");
    } else {
      S.activeTypes.add(type);
      btn.classList.add("active");
    }
    renderMarkers();
  });

  const toggleAllBtn = document.getElementById("toggle-all-types");
  if (toggleAllBtn) {
    toggleAllBtn.addEventListener("click", () => {
      if (S.regionSolo) exitRegionSolo();
      const allActive = types.every(t => S.activeTypes.has(t));
      if (allActive) {
        types.forEach(t => S.activeTypes.delete(t));
        container.querySelectorAll(".type-filter-btn").forEach(b => b.classList.remove("active"));
        toggleAllBtn.classList.remove("active");
      } else {
        types.forEach(t => S.activeTypes.add(t));
        container.querySelectorAll(".type-filter-btn").forEach(b => b.classList.add("active"));
        toggleAllBtn.classList.add("active");
      }
      renderMarkers();
    });
  }

  // Region solo button
  const regionSoloBtn = document.getElementById("region-solo-btn");
  if (regionSoloBtn) {
    regionSoloBtn.addEventListener("click", () => {
      if (S.regionSolo) {
        exitRegionSolo();
      } else {
        S.regionSolo = true;
        S.savedActiveTypes = new Set(S.activeTypes);
        S.activeTypes = new Set(["region", "roman_province", "people"]);
        regionSoloBtn.classList.add("active");
        container.querySelectorAll(".type-filter-btn").forEach(b => b.classList.remove("active"));
      }
      renderMarkers();
    });
  }

  const markersBtn = document.getElementById("toggle-markers");
  if (markersBtn) {
    markersBtn.addEventListener("click", () => {
      S.markersOn = !S.markersOn;
      markersBtn.classList.toggle("active", S.markersOn);
      renderMarkers();
    });
  }

  const labelsBtn = document.getElementById("toggle-labels");
  if (labelsBtn) {
    labelsBtn.addEventListener("click", () => {
      S.labelsOn = !S.labelsOn;
      labelsBtn.classList.toggle("active", S.labelsOn);
      renderMarkers();
    });
  }

  // About panel
  const aboutBtn = document.getElementById("about-btn");
  const aboutPanel = document.getElementById("about-panel");
  const closeAbout = document.getElementById("close-about");
  const aboutBackdrop = document.getElementById("about-modal-backdrop");
  function openAboutPanel() {
    aboutPanel.classList.remove("hidden");
    aboutBackdrop?.classList.remove("hidden");
  }
  function closeAboutPanel() {
    aboutPanel.classList.add("hidden");
    aboutBackdrop?.classList.add("hidden");
  }
  if (aboutBtn && aboutPanel) {
    aboutBtn.addEventListener("click", () => {
      if (aboutPanel.classList.contains("hidden")) openAboutPanel();
      else closeAboutPanel();
    });
    closeAbout?.addEventListener("click", closeAboutPanel);
    aboutBackdrop?.addEventListener("click", closeAboutPanel);
  }
}

function setupMobileMenu() {
  const btn = document.getElementById("mobile-menu-btn");
  const menu = document.getElementById("mobile-menu");
  const backdrop = document.getElementById("mobile-menu-backdrop");
  if (!menu) return;

  function openMenu() {
    // Sync type filter buttons (region excluded — handled by region-solo button)
    const typeContainer = document.getElementById("mobile-type-filter-buttons");
    const types = Object.keys(TYPE_COLORS).filter(t => t !== "region");
    const allOn = types.every(t => S.activeTypes.has(t));
    typeContainer.innerHTML =
      `<button class="ctrl-btn toggle-btn${allOn ? " active" : ""}" id="mobile-toggle-all" style="width:100%;margin-bottom:6px">Select All</button>` +
      types.map(t => {
        const color = TYPE_COLORS[t];
        const label = TYPE_LABELS[t];
        const active = S.activeTypes.has(t) ? " active" : "";
        return `<button class="type-filter-btn${active}" data-type="${t}" title="${label}">
          <span class="tf-dot" style="background:${color}"></span>${label}
        </button>`;
      }).join("");

    typeContainer.querySelector("#mobile-toggle-all").addEventListener("click", (e) => {
      if (S.regionSolo) exitRegionSolo();
      const allActive = types.every(t => S.activeTypes.has(t));
      if (allActive) {
        types.forEach(t => S.activeTypes.delete(t));
        typeContainer.querySelectorAll(".type-filter-btn").forEach(b => b.classList.remove("active"));
        e.currentTarget.classList.remove("active");
        document.querySelectorAll("#type-filter-buttons .type-filter-btn").forEach(b => b.classList.remove("active"));
        document.getElementById("toggle-all-types")?.classList.remove("active");
      } else {
        types.forEach(t => S.activeTypes.add(t));
        typeContainer.querySelectorAll(".type-filter-btn").forEach(b => b.classList.add("active"));
        e.currentTarget.classList.add("active");
        document.querySelectorAll("#type-filter-buttons .type-filter-btn").forEach(b => b.classList.add("active"));
        document.getElementById("toggle-all-types")?.classList.add("active");
      }
      renderMarkers();
    });

    typeContainer.addEventListener("click", (e) => {
      const b = e.target.closest(".type-filter-btn");
      if (!b) return;
      if (S.regionSolo) exitRegionSolo();
      const t = b.dataset.type;
      if (S.activeTypes.has(t)) { S.activeTypes.delete(t); b.classList.remove("active"); }
      else { S.activeTypes.add(t); b.classList.add("active"); }
      // Mirror to desktop buttons
      document.querySelectorAll(`#type-filter-buttons .type-filter-btn[data-type="${t}"]`)
        .forEach(db => db.classList.toggle("active", S.activeTypes.has(t)));
      renderMarkers();
    });

    // Sync segment buttons
    const segContainer = document.getElementById("mobile-segment-buttons");
    segContainer.innerHTML = document.getElementById("segment-buttons").innerHTML;
    segContainer.addEventListener("click", (e) => {
      const b = e.target.closest(".seg-btn");
      if (!b) return;
      const seg = Number(b.dataset.seg);
      focusSegment(seg);
      closeMenu();
    });

    // Labels toggle + Label Settings shortcut
    const dispContainer = document.getElementById("mobile-display-controls");
    dispContainer.innerHTML = `
      <button class="ctrl-btn toggle-btn${S.markersOn ? " active" : ""}" id="mobile-toggle-markers">Markers</button>
      <button class="ctrl-btn toggle-btn${S.labelsOn ? " active" : ""}" id="mobile-toggle-labels">Labels</button>
      <button class="ctrl-btn" id="mobile-settings-open">Developer Settings</button>
    `;
    dispContainer.querySelector("#mobile-toggle-markers").addEventListener("click", (e) => {
      S.markersOn = !S.markersOn;
      e.currentTarget.classList.toggle("active", S.markersOn);
      document.getElementById("toggle-markers")?.classList.toggle("active", S.markersOn);
      renderMarkers();
    });
    dispContainer.querySelector("#mobile-toggle-labels").addEventListener("click", (e) => {
      S.labelsOn = !S.labelsOn;
      e.currentTarget.classList.toggle("active", S.labelsOn);
      document.getElementById("toggle-labels")?.classList.toggle("active", S.labelsOn);
      renderMarkers();
    });
    dispContainer.querySelector("#mobile-settings-open").addEventListener("click", () => {
      closeMenu();
      document.getElementById("settings-panel")?.classList.remove("hidden");
    });

    menu.classList.remove("hidden");
  }

  function closeMenu() { menu.classList.add("hidden"); }

  btn?.addEventListener("click", openMenu);
  document.getElementById("bottom-filter-btn")?.addEventListener("click", openMenu);
  backdrop.addEventListener("click", closeMenu);
}

function activeTileSource() {
  return S.originalTile;
}

/* ============================================================
   Tile source swap (old ↔ new)
   ============================================================ */
function swapTileSource(callback, previousMode = S.mapMode) {
  const vp = S.viewer.viewport;
  const center = vp.getCenter();
  const zoom = vp.getZoom();

  const oldBounds = getSegmentBounds(S.selectedSegment, boundsKeyForMode(previousMode));
  const oldRx = oldBounds ? (center.x - oldBounds.x0) / Math.max(oldBounds.x1 - oldBounds.x0, 0.00001) : 0.5;
  const oldRy = oldBounds ? (center.y - oldBounds.y0) / Math.max(oldBounds.y1 - oldBounds.y0, 0.00001) : 0.5;

  const source = activeTileSource();
  S.viewer.open(source);

  S.viewer.addOnceHandler("open", () => {
    const newBounds = getSegmentBounds(S.selectedSegment, activeBoundsKey());
    if (newBounds) {
      const nx = newBounds.x0 + oldRx * Math.max(newBounds.x1 - newBounds.x0, 0.00001);
      const ny = newBounds.y0 + oldRy * Math.max(newBounds.y1 - newBounds.y0, 0.00001);
      vp.zoomTo(zoom, null, true);
      vp.panTo(new OpenSeadragon.Point(nx, ny), true);
    } else {
      focusSegment(DEFAULT_SEGMENT, true);
    }
    renderMarkers();
    if (callback) callback();
  });
}

/* ============================================================
   Mouse / touch events
   ============================================================ */
function setupInteraction() {
  let lastHovered = null;

  new OpenSeadragon.MouseTracker({
    element: S.viewer.element,
    moveHandler: (e) => {
      if (S.isMobile) return;
      const pos = e.position;
      const elRect = S.viewer.element.getBoundingClientRect();
      const clientX = elRect.left + pos.x;
      const clientY = elRect.top + pos.y;

      // Don't show tooltip when cursor is over the info panel
      const panel = document.getElementById("info-panel");
      if (panel && !panel.classList.contains("hidden")) {
        const pr = panel.getBoundingClientRect();
        if (clientX >= pr.left && clientX <= pr.right && clientY >= pr.top && clientY <= pr.bottom) {
          hideTooltip();
          return;
        }
      }

      const tt = document.getElementById("tooltip");

      // SegIV markers (new map mode)
      const place = hitTest(clientX, clientY);
      if (place) {
        S.viewer.element.style.cursor = "pointer";
        if (place !== lastHovered) {
          showTooltip(place, clientX, clientY);
          lastHovered = place;
        } else {
          tt.style.left = (clientX + 18) + "px";
          tt.style.top  = (clientY - 12) + "px";
        }
        return;
      }

      // Miller calibration overlay rects (old map mode)
      const millerItem = hitTestMillerOverlay(clientX, clientY);
      if (millerItem) {
        S.viewer.element.style.cursor = "pointer";
        if (millerItem !== lastHovered) {
          showMillerTooltip(millerItem, clientX, clientY);
          lastHovered = millerItem;
        }
        // Don't reposition the rich tooltip while it's shown — the iframe would reload
        return;
      }

      S.viewer.element.style.cursor = "default";
      hideTooltip();
      lastHovered = null;
    },
    leaveHandler: () => { if (!S.isMobile) { hideTooltip(); lastHovered = null; } },
  });

  S.viewer.addHandler("canvas-click", (e) => {
    if (!e.quick) return;  // ignore pans and long-press (applies to all devices)
    e.preventDefaultAction = true;
    const pos = e.position;
    const elRect = S.viewer.element.getBoundingClientRect();
    const clientX = elRect.left + pos.x;
    const clientY = elRect.top + pos.y;

    // SegIV marker click
    const place = hitTest(clientX, clientY);
    if (place) {
      showInfoPanel(place);
      return;
    }

    // Miller overlay click — open info panel with available data
    const millerItem = hitTestMillerOverlay(clientX, clientY);
    if (millerItem) {
      showInfoPanel({
        latin_std:      millerItem.latin_std,
        latin:          millerItem.latin_std,
        modern:         millerItem.modern,
        type:           millerItem.type,
        province:       millerItem.province,
        country:        millerItem.country,
        lat:            millerItem.lat,
        lng:            millerItem.lng,
        data_id:        millerItem.data_id,
        record_id:      millerItem.record_id,
        ulm_id:         millerItem.ulm_id,
        wiki_url:       millerItem.wiki_url || null,
        tabula_segment: millerItem.tabula_segment,
        tabula_row:     millerItem.tabula_row,
        tabula_col:     millerItem.tabula_col,
        grid_col:       millerItem.tabula_col,
        grid_row:       millerItem.tabula_row,
        source:         millerItem.source || "tabula",
      });
      return;
    }

    // Nothing hit — close info panel if open
    const panel = document.getElementById("info-panel");
    if (!panel.classList.contains("hidden")) hideInfoPanel();
  });
}

/* ============================================================
   Utility
   ============================================================ */
const COUNTRY_TO_ISO2 = {
  D:"DE",A:"AT",I:"IT",IT:"IT",Italy:"IT",F:"FR",E:"ES",P:"PT",H:"HU",B:"BE",
  NL:"NL",CH:"CH",CY:"CY",GB:"GB",GR:"GR",TR:"TR",BG:"BG",RO:"RO",HR:"HR",
  AL:"AL",MK:"MK",MNE:"ME",BIH:"BA",YU:"RS",SLO:"SI",RKS:"XK",V:"VA",
  TN:"TN",DZ:"DZ",MA:"MA",LAR:"LY",IL:"IL",RL:"LB",SYR:"SY",IRQ:"IQ",
  IR:"IR",JOR:"JO",GE:"GE",ARM:"AM",AZ:"AZ",RUS:"RU",UA:"UA",TM:"TM",
  PAK:"PK",AFG:"AF",IND:"IN",ET:"EG",IRE:"IE",
};

const ISO2_COUNTRY_NAME = {
  en: { DE:"Germany",AT:"Austria",IT:"Italy",FR:"France",ES:"Spain",PT:"Portugal",HU:"Hungary",BE:"Belgium",NL:"Netherlands",CH:"Switzerland",CY:"Cyprus",GB:"United Kingdom",GR:"Greece",TR:"Turkey",BG:"Bulgaria",RO:"Romania",HR:"Croatia",AL:"Albania",MK:"North Macedonia",ME:"Montenegro",BA:"Bosnia & Herzegovina",RS:"Serbia",SI:"Slovenia",XK:"Kosovo",VA:"Vatican",TN:"Tunisia",DZ:"Algeria",MA:"Morocco",LY:"Libya",IL:"Israel",LB:"Lebanon",SY:"Syria",IQ:"Iraq",IR:"Iran",JO:"Jordan",GE:"Georgia",AM:"Armenia",AZ:"Azerbaijan",RU:"Russia",UA:"Ukraine",TM:"Turkmenistan",PK:"Pakistan",AF:"Afghanistan",IN:"India",EG:"Egypt",IE:"Ireland" },
  de: { DE:"Deutschland",AT:"Österreich",IT:"Italien",FR:"Frankreich",ES:"Spanien",PT:"Portugal",HU:"Ungarn",BE:"Belgien",NL:"Niederlande",CH:"Schweiz",CY:"Zypern",GB:"Großbritannien",GR:"Griechenland",TR:"Türkei",BG:"Bulgarien",RO:"Rumänien",HR:"Kroatien",AL:"Albanien",MK:"Nordmazedonien",ME:"Montenegro",BA:"Bosnien-Herzegowina",RS:"Serbien",SI:"Slowenien",XK:"Kosovo",VA:"Vatikan",TN:"Tunesien",DZ:"Algerien",MA:"Marokko",LY:"Libyen",IL:"Israel",LB:"Libanon",SY:"Syrien",IQ:"Irak",IR:"Iran",JO:"Jordanien",GE:"Georgien",AM:"Armenien",AZ:"Aserbaidschan",RU:"Russland",UA:"Ukraine",TM:"Turkmenistan",PK:"Pakistan",AF:"Afghanistan",IN:"Indien",EG:"Ägypten",IE:"Irland" },
};

function normalizeLatinV(s) {
  if (!s) return s;
  return s.replace(/v/gi, (ch, offset, str) => {
    const prev = str[offset - 1];
    if (!prev || /[\s\-_]/.test(prev)) return ch; // word-initial V = consonant, keep
    return ch === ch.toUpperCase() ? 'U' : 'u';   // non-initial V = vowel → U
  });
}

function cleanOnePart(s) {
  s = s.trim();
  const nearParen = s.match(/^\((?:near|bei|b\.|prope)\s+([^),]+)/i);
  if (nearParen) return nearParen[1].trim();
  s = s.replace(/\s*\([^)]*\)/g, '').trim();
  s = s.replace(/,\s+\S.*$/, '').trim();
  s = s.replace(/\s+(?:near|bei|b\.|prope|am|an\s+der|an\s+dem)\s+\S.*/i, '').trim();
  if (s.startsWith('(') || s.endsWith(')')) return '';
  return s;
}

// Returns the cleaned first alternative (kept for callers that only need one).
function cleanModernForWiki(modern) {
  if (!modern) return '';
  return cleanOnePart(modern.split(/\s*\/\s*/)[0]);
}

// Returns ALL cleaned alternatives from a modern name string ("Vienna/Wien/Vienne" → ["Vienna","Wien","Vienne"]).
function modernAlternatives(modern) {
  if (!modern) return [];
  const seen = new Set();
  return modern.split(/\s*\/\s*/)
    .map(p => cleanOnePart(p))
    .filter(p => p && !seen.has(p) && seen.add(p));
}

// Returns an ordered list of Wikipedia search terms to try for a given place.
// resolveWikiArticle() tries each in turn via the opensearch API.
function buildWikiSearchTerms(place) {
  const modern   = place.modern || '';
  const latin    = place.latin_std || place.latin || '';
  const type     = place.type || '';
  const wikiLang = getText('wiki_lang');

  const cleanLatin = latin.split('/')[0].replace(/[\[\]~]/g, '').trim();
  const normLatin  = normalizeLatinV(cleanLatin);
  // All cleaned alternatives from the modern name ("Vienna/Wien/Vienne" → ["Vienna","Wien","Vienne"])
  const modAlts    = modernAlternatives(modern);
  const cleanMod   = modAlts[0] || '';
  const norm = s => s.toLowerCase().replace(/[^a-z]/g, '');
  const hasUsefulModern = cleanMod.length > 0 && norm(cleanMod) !== norm(cleanLatin);
  // Additional alternatives beyond the first (e.g. "Wien", "Vienne")
  const extraAlts  = modAlts.slice(1).filter(a => norm(a) !== norm(cleanLatin));

  if (type === 'region' || type === 'roman_province') {
    if (wikiLang === 'en') {
      return [
        cleanLatin ? `Roman ${cleanLatin}` : null,
        cleanLatin || null,
        hasUsefulModern ? cleanMod : null,
        ...extraAlts,
        cleanLatin ? `${cleanLatin} Roman province` : null,
      ].filter(Boolean);
    }
    return [
      cleanLatin || null,
      cleanLatin ? `${cleanLatin} Provinz` : null,
      hasUsefulModern ? cleanMod : null,
      ...extraAlts,
    ].filter(Boolean);
  }

  if (type === 'people') {
    return [
      normLatin || null,
      normLatin ? `${normLatin} ancient people` : null,
      hasUsefulModern ? cleanMod : null,
      ...extraAlts,
    ].filter(Boolean);
  }

  if (type === 'temple') {
    return [
      normLatin || null,
      hasUsefulModern ? cleanMod : null,
      ...extraAlts,
      (cleanLatin && cleanLatin !== normLatin) ? cleanLatin : null,
    ].filter(Boolean);
  }

  // Regular places (city, port, road_station, …): all modern alternatives, then Latin
  return [
    hasUsefulModern ? cleanMod : null,
    ...extraAlts,
    normLatin || null,
    (cleanLatin && cleanLatin !== normLatin) ? cleanLatin : null,
  ].filter(Boolean);
}

// Returns true if the article title is plausibly relevant to the search term.
// Rejects clearly wrong results: off-topic titles (no word overlap) and media/disambiguation articles.
function wikiTitleRelevant(title, term) {
  // Parenthetical qualifiers that indicate a non-place article
  if (/\((?:Album|Single|EP|Film|Lied|Song|Band|Buch|Roman|série|Begriffsklärung|disambiguation|Domaine|Winery|Château|Weingut)\)/i.test(title)) return false;
  const tWords = new Set((title.toLowerCase().match(/[a-zÀ-ɏ]{3,}/g) || []));
  const qWords = (term.toLowerCase().match(/[a-zÀ-ɏ]{3,}/g) || []);
  return qWords.some(w => tWords.has(w));
}

// Wikipedia opensearch API: tries each term in order, returns {title, url} of the first relevant hit.
async function resolveWikiArticle(terms, lang) {
  for (const term of terms) {
    const key = `${lang}\x00${term}`;
    if (wikiCache.has(key)) {
      const v = wikiCache.get(key);
      if (v) return v;
      continue; // null = already tried, nothing found
    }
    try {
      const url = `https://${lang}.wikipedia.org/w/api.php?action=opensearch&search=${encodeURIComponent(term)}&limit=1&format=json&origin=*`;
      const r = await fetch(url);
      const d = await r.json();
      if (Array.isArray(d[1]) && d[1].length) {
        const title = d[1][0];
        if (wikiTitleRelevant(title, term)) {
          const result = { title, url: d[3][0] };
          wikiCache.set(key, result);
          return result;
        }
        // Title looks irrelevant — skip this term but don't cache as null
        // so a re-search in a different session still tries it
      } else {
        wikiCache.set(key, null); // term produced no hits at all
      }
    } catch (_) { /* network error — skip this term */ }
  }
  if (lang === 'de') {
    const enResult = await resolveWikiArticle(terms, 'en');
    if (enResult) return enResult;
  }
  if (lang !== 'it') {
    const itResult = await resolveWikiArticle(terms, 'it');
    if (itResult) return itResult;
  }
  return null;
}

// Wikipedia REST summary API: returns { extract, thumbnail } for a resolved title.
async function fetchWikiData(title, lang) {
  const key = `data\x00${lang}\x00${title}`;
  if (wikiCache.has(key)) return wikiCache.get(key);
  try {
    const encodedTitle = encodeURIComponent(title.replace(/ /g, '_'));
    const url = `https://${lang}.wikipedia.org/api/rest_v1/page/summary/${encodedTitle}`;
    const r = await fetch(url);
    if (!r.ok) { wikiCache.set(key, null); return null; }
    const d = await r.json();
    const result = { extract: d.extract || null, thumbnail: d.thumbnail?.source || null };
    wikiCache.set(key, result);
    wikiCache.set(`sum\x00${lang}\x00${title}`, result.extract); // backward-compat key
    return result;
  } catch (_) { return null; }
}

async function fetchWikiSummary(title, lang) {
  const data = await fetchWikiData(title, lang);
  return data?.extract || null;
}

function applyWikiData(data, summaryEl) {
  if (!data?.extract) return;
  let text = data.extract;
  if (text.length > 300) {
    const m = text.match(/^.{60,280}[.!?]/);
    text = m ? m[0] : text.slice(0, 280).replace(/\s+\S*$/, '') + '…';
  }
  summaryEl.textContent = text;
  summaryEl.classList.remove("hidden");
  const imgEl = document.getElementById("panel-wiki-img");
  const section = document.getElementById("panel-wiki-section");
  if (imgEl && data.thumbnail) {
    imgEl.src = data.thumbnail;
    imgEl.classList.remove("hidden");
    if (section) section.classList.add("has-image");
  } else if (imgEl) {
    imgEl.src = "";
    imgEl.classList.add("hidden");
    if (section) section.classList.remove("has-image");
  }
}

// Fetches Wikipedia summary directly from a known wiki_url in the DB.
async function resolveWikiSummaryFromUrl(reqId, summaryEl, url) {
  if (!summaryEl) return;
  const m = url.match(/https?:\/\/([a-z]+)\.wikipedia\.org\/wiki\/(.+)/);
  if (!m) return;
  const lang = m[1], title = decodeURIComponent(m[2].replace(/_/g, ' '));
  const data = await fetchWikiData(title, lang);
  if (wikiRequestId !== reqId) return;
  applyWikiData(data, summaryEl);
}

// Async: resolves Wikipedia article URL and fetches summary + thumbnail, updating the panel live.
async function resolveWikiAndUpdate(reqId, linkEl, summaryEl, terms, lang) {
  const article = await resolveWikiArticle(terms, lang);
  if (wikiRequestId !== reqId) return;
  if (!article) return;
  linkEl.href = article.url;
  if (!summaryEl) return;
  const data = await fetchWikiData(article.title, lang);
  if (wikiRequestId !== reqId) return;
  applyWikiData(data, summaryEl);
}

// Rough bounding boxes (minLat, maxLat, minLng, maxLng) ordered smallest→largest so
// the most specific country wins when multiple boxes match.
const COUNTRY_BBOX = [
  ["MT",35.78,36.08,14.18,14.58], ["CY",34.56,35.71,32.26,34.60],
  ["LU",49.45,50.18,5.73,6.53],   ["XK",41.86,43.27,20.01,21.79],
  ["ME",41.85,43.55,18.43,20.36], ["SI",45.42,46.88,13.38,16.61],
  ["AL",39.64,42.66,19.27,21.07], ["MK",40.85,42.37,20.45,23.04],
  ["BA",42.56,45.27,15.75,19.62], ["PT",36.96,42.15,-9.50,-6.19],
  ["IE",51.44,55.38,-10.48,-5.99],["LB",33.05,34.69,35.10,36.63],
  ["IL",29.50,33.34,34.27,35.90], ["CH",45.83,47.81,5.96,10.49],
  ["AT",46.37,49.02,9.53,17.16],  ["HR",42.39,46.55,13.50,19.43],
  ["RS",42.23,46.19,18.82,22.99], ["BG",41.24,44.22,22.36,28.61],
  ["SK",47.73,49.61,16.84,22.56], ["HU",45.74,48.59,16.11,22.90],
  ["AM",38.84,41.30,43.45,46.63], ["AZ",38.39,41.90,44.77,50.39],
  ["GE",41.05,43.59,40.00,46.64], ["JO",29.19,33.38,35.00,39.30],
  ["TN",30.24,37.55,7.52,11.60],  ["GR",34.80,41.75,19.37,29.65],
  ["RO",43.62,48.27,22.15,30.05], ["NL",50.75,53.56,3.36,7.23],
  ["BE",49.50,51.51,2.55,6.40],   ["CZ",48.55,51.06,12.09,18.86],
  ["GB",49.87,60.86,-8.65,1.76],  ["DE",47.27,55.06,6.02,15.04],
  ["PL",49.00,54.84,14.12,24.15], ["FR",42.33,51.09,-4.79,8.24],
  ["IT",36.62,47.09,6.63,18.52],  ["ES",35.17,43.79,-9.30,3.33],
  ["SY",32.31,37.32,35.73,42.38], ["IQ",29.07,37.39,38.79,48.57],
  ["UA",44.39,52.38,22.14,40.09], ["EG",21.98,31.67,24.70,36.90],
  ["LY",19.50,33.17,9.32,25.16],  ["MA",27.67,35.92,-13.17,-0.99],
  ["DZ",18.97,37.09,-8.68,11.99], ["TR",35.82,42.10,26.04,44.79],
  ["IR",25.06,39.78,44.02,63.32], ["TM",35.14,42.80,52.44,66.69],
  ["AF",29.40,38.49,60.52,74.89], ["PK",23.69,37.10,60.87,77.84],
  ["IN",8.09,35.68,68.11,97.41],
];

function guessCountryFromLatLng(lat, lng) {
  if (lat == null || lng == null) return null;
  const la = Number(lat), lo = Number(lng);
  if (!Number.isFinite(la) || !Number.isFinite(lo)) return null;
  let best = null, bestArea = Infinity;
  for (const [iso, la1, la2, lo1, lo2] of COUNTRY_BBOX) {
    if (la >= la1 && la <= la2 && lo >= lo1 && lo <= lo2) {
      const area = (la2 - la1) * (lo2 - lo1);
      if (area < bestArea) { bestArea = area; best = iso; }
    }
  }
  return best;
}

function countryName(rawCode) {
  const t = (rawCode || "").trim();
  const iso = COUNTRY_TO_ISO2[t] || (t.length === 2 ? t.toUpperCase() : null);
  if (!iso) return t;
  return (ISO2_COUNTRY_NAME[getLang()] || ISO2_COUNTRY_NAME.en)[iso] || iso;
}

function countryFlags(raw) {
  if (!raw) return "";
  return raw.split("|").map(c => {
    const t = c.trim();
    const iso = COUNTRY_TO_ISO2[t] || (t.length === 2 ? t.toUpperCase() : null);
    if (!iso || iso.length !== 2) return "";
    return String.fromCodePoint(0x1F1E6 + iso.charCodeAt(0) - 65, 0x1F1E6 + iso.charCodeAt(1) - 65);
  }).filter(Boolean).join("");
}

function countryFlagHtml(raw) {
  if (!raw) return "";
  return raw.split("|").map(c => {
    const t = c.trim();
    const iso = COUNTRY_TO_ISO2[t] || (t.length === 2 ? t.toUpperCase() : null);
    if (!iso || iso.length !== 2) return "";
    return `<img src="https://flagcdn.com/24x18/${iso.toLowerCase()}.png" alt="${escHtml(t)}" title="${escHtml(t)}" style="height:1.2em;vertical-align:middle;border-radius:1px">`;
  }).filter(Boolean).join(" ");
}

function tpOnlineHref(place) {
  if (place.ulm_id) return `https://tp-online.ku.de/trefferanzeige.php?id=${place.ulm_id}`;
  // Only use record_id when it's the plain TP:XXXX format — that number IS the ULM ID.
  // TP:WL:XXXX and other prefixed formats use a different ID space.
  const rid = String(place.record_id || place.id || "");
  const m = /^TP:(\d+)$/.exec(rid);
  if (m && Number(m[1]) < 2000000) return `https://tp-online.ku.de/trefferanzeige.php?id=${m[1]}`;
  return "";
}

function escHtml(s) {
  const d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}

function tabulaSectionHref(place) {
  const segment = Number(place.tabula_segment ?? place.segment);
  const row = String(place.tabula_row ?? place.grid_row ?? "").trim().toLowerCase();
  const col = Number(place.tabula_col ?? place.grid_col);
  if (!Number.isFinite(segment) || segment < 1 || !/^[abc]$/.test(row) || !Number.isFinite(col) || col < 1) {
    return "";
  }
  const segmValue = Math.max(segment - 1, 0).toString(16);
  return `https://www.tabula-peutingeriana.de/tp/tabula.html?segm=${segmValue}#${row}${Math.trunc(col)}`;
}

function tabulaSourceHref(place) {
  const sectionHref = tabulaSectionHref(place);
  if (sectionHref) {
    return sectionHref;
  }
  const dataId = Number(place.data_id);
  if (place.source === "tabula" && Number.isFinite(dataId) && dataId > 0) {
    return `https://www.tabula-peutingeriana.de/tp/${Math.trunc(dataId)}.html`;
  }
  return "";
}

/* ============================================================
   Developer settings — persistence and panel UI
   ============================================================ */
async function loadLabelParams() {
  // Prefer the project file (written by Save button via server)
  try {
    const r = await fetch("data/label_params.json?" + Date.now());
    if (r.ok) {
      const saved = await r.json();
      if (saved && typeof saved === "object") { Object.assign(LP, saved); return; }
    }
  } catch {}
  // Fallback: browser localStorage
  try {
    const raw = localStorage.getItem(LP_KEY);
    if (raw) {
      const saved = JSON.parse(raw);
      if (saved && typeof saved === "object") Object.assign(LP, saved);
    }
  } catch {}
}

async function saveLabelParams() {
  // Try to persist to project file via dev server
  try {
    const r = await fetch("/api/save-label-params", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(LP),
    });
    if (r.ok) { localStorage.setItem(LP_KEY, JSON.stringify(LP)); return; }
  } catch {}
  // Fallback: browser localStorage
  localStorage.setItem(LP_KEY, JSON.stringify(LP));
}

const SP_DEFS = [
  { section: "Markers",       label: "Marker opacity",           key: "markerAlpha",
    min: 0,   max: 1,    step: 0.05, fmt: v => Math.round(v * 100) + "%",
    desc: "Transparency of marker rectangles. 100% = fully opaque, 0% = invisible." },
  { section: "Label Density",  label: "Label spacing",          key: "labelPad",
    min: -10, max: 20,   step: 1,   fmt: v => v + "px",
    desc: "Padding around each label's collision box. Negative values allow labels to overlap, increasing density. 0 = labels touch edge-to-edge." },
  { section: "Label Density",  label: "Show all above zoom",    key: "labelPadZoomThresh",
    min: 0,   max: 50,   step: 0.25, fmt: v => v >= 50 ? "never" : "z " + v.toFixed(2).replace(/0+$/, "").replace(/\.$/, ""),
    desc: "Above this zoom level, overlap detection is disabled and all labels are shown regardless of spacing." },
  { section: "Label Limits",   label: "Max font — mobile",      key: "maxFontMobile",
    min: 4,   max: 100,  step: 1,   fmt: v => v + "px",
    desc: "Hard ceiling on label font size on mobile screens. Keeps labels readable even when the zoom curve would produce larger text." },
  { section: "Label Limits",   label: "Max labels — desktop",   key: "maxLabelsDesktop",
    min: 5,   max: 500,  step: 5,   fmt: v => v >= 500 ? "∞" : String(v),
    desc: "Maximum labels drawn at once on desktop. Overlap detection may reduce the actual count further." },
  { section: "Label Limits",   label: "Max labels — mobile",    key: "maxLabelsMobile",
    min: 1,   max: 100,  step: 1,   fmt: v => String(v),
    desc: "Maximum labels drawn at once on mobile." },
  { section: "Label Limits",   label: "Show all above zoom — mobile", key: "labelPadZoomThreshMobile",
    min: 0,   max: 50,   step: 0.25, fmt: v => v >= 50 ? "never" : "z " + v.toFixed(2).replace(/0+$/, "").replace(/\.$/, ""),
    desc: "Above this zoom level on mobile, overlap detection is disabled and all labels are shown." },
  { section: "Label Limits",   label: "Min font — mobile",      key: "minFontMobile",
    min: 0,   max: 20,   step: 0.5, fmt: v => v + "px",
    desc: "Sets the floor of the mobile font curve. The curve range [Point1..Point4] is rescaled to [min..max font mobile], so labels never shrink below this size." },
  // Zoom → font curve (4 control points, piecewise linear)
  { section: "Zoom → Font Curve", type: "curve-point", pointLabel: "Point 1 (low zoom)",
    keyZ: "zfZ1", keyF: "zfF1",
    minZ: 0.05, maxZ: 50, stepZ: 0.25, minF: 0, maxF: 100, stepF: 1,
    desc: "Leftmost anchor. Below this zoom, font stays at this size." },
  { section: "Zoom → Font Curve", type: "curve-point", pointLabel: "Point 2",
    keyZ: "zfZ2", keyF: "zfF2",
    minZ: 0.05, maxZ: 50, stepZ: 0.25, minF: 0, maxF: 100, stepF: 1,
    desc: "Second control point — interpolated linearly between neighbours." },
  { section: "Zoom → Font Curve", type: "curve-point", pointLabel: "Point 3",
    keyZ: "zfZ3", keyF: "zfF3",
    minZ: 0.05, maxZ: 50, stepZ: 0.25, minF: 0, maxF: 100, stepF: 1,
    desc: "Third control point." },
  { section: "Zoom → Font Curve", type: "curve-point", pointLabel: "Point 4 (high zoom)",
    keyZ: "zfZ4", keyF: "zfF4",
    minZ: 0.05, maxZ: 50, stepZ: 0.25, minF: 0, maxF: 100, stepF: 1,
    desc: "Rightmost anchor. Above this zoom, font stays at this size." },
];

function buildSettingsPanelBody() {
  const body = document.getElementById("settings-body");
  if (!body) return;
  body.innerHTML = "";
  function makeSlider(id, min, max, step, value, onChange) {
    const inp = document.createElement("input");
    inp.type = "range"; inp.id = id; inp.className = "sp-slider";
    inp.min = String(min); inp.max = String(max);
    inp.step = String(step); inp.value = String(value);
    inp.addEventListener("input", onChange);
    return inp;
  }
  function makeStepBtn(symbol, inp, dir, onChange) {
    const btn = document.createElement("button");
    btn.type = "button"; btn.className = "sp-step-btn";
    btn.textContent = symbol;
    btn.addEventListener("click", () => {
      dir < 0 ? inp.stepDown() : inp.stepUp();
      onChange();
    });
    return btn;
  }
  function wrapWithSteps(inp, onChange) {
    const wrap = document.createElement("div");
    wrap.className = "sp-slider-wrap";
    wrap.appendChild(makeStepBtn("−", inp, -1, onChange));
    wrap.appendChild(inp);
    wrap.appendChild(makeStepBtn("+", inp, 1, onChange));
    return wrap;
  }

  // Location section
  const locHWrap = document.createElement("div");
  locHWrap.className = "sp-section-row";
  const locH = document.createElement("h4");
  locH.className = "sp-section";
  locH.textContent = "Location";
  locHWrap.appendChild(locH);
  body.appendChild(locHWrap);

  function makeCoordRow(labelText, id, min, max, currentVal, onSave) {
    const row = document.createElement("div");
    row.className = "sp-row";
    const lbl = document.createElement("label");
    lbl.className = "sp-label";
    lbl.htmlFor = id;
    lbl.textContent = labelText;
    const inp = document.createElement("input");
    inp.type = "number"; inp.id = id; inp.className = "sp-coord-input";
    inp.min = String(min); inp.max = String(max); inp.step = "0.0001";
    inp.value = currentVal.toFixed(4);
    inp.addEventListener("change", () => {
      const v = Number(inp.value);
      if (Number.isFinite(v) && v >= min && v <= max) onSave(v);
    });
    row.appendChild(lbl); row.appendChild(inp);
    return row;
  }
  body.appendChild(makeCoordRow("Default lat", "sp-default-lat", -90, 90, S.defaultLat, v => {
    S.defaultLat = v;
    try { localStorage.setItem("tp_defaultLat", v); } catch {}
  }));
  body.appendChild(makeCoordRow("Default lng", "sp-default-lng", -180, 180, S.defaultLng, v => {
    S.defaultLng = v;
    try { localStorage.setItem("tp_defaultLng", v); } catch {}
  }));
  const locDesc = document.createElement("p");
  locDesc.className = "sp-desc";
  locDesc.textContent = 'Fallback coordinates used by "Locate Me" when device GPS is unavailable. Default: Novara (45.4473, 8.6191).';
  body.appendChild(locDesc);

  let lastSection = null;
  for (const def of SP_DEFS) {
    if (def.section !== lastSection) {
      const hWrap = document.createElement("div");
      hWrap.className = "sp-section-row";
      const h = document.createElement("h4");
      h.className = "sp-section";
      h.textContent = def.section;
      hWrap.appendChild(h);
      if (def.section === "Zoom → Font Curve") {
        const zoomBadge = document.createElement("span");
        zoomBadge.className = "sp-zoom-badge";
        zoomBadge.id = "sp-zoom-badge";
        zoomBadge.textContent = "zoom: —";
        hWrap.appendChild(zoomBadge);
      }
      body.appendChild(hWrap);
      lastSection = def.section;
    }

    if (def.type === "curve-point") {
      // Compact two-slider row: zoom on left, font on right
      const hdr = document.createElement("div");
      hdr.className = "sp-curve-pt-label";
      hdr.textContent = def.pointLabel;
      body.appendChild(hdr);

      function makeCurveRow(subLabel, key, min, max, step, fmtFn) {
        const row = document.createElement("div");
        row.className = "sp-row sp-subrow";
        const lbl = document.createElement("label");
        lbl.className = "sp-label";
        lbl.htmlFor = `sp-${key}`;
        lbl.textContent = subLabel;
        const right = document.createElement("div");
        right.className = "sp-right";
        const val = document.createElement("span");
        val.className = "sp-val";
        val.id = `sp-val-${key}`;
        val.textContent = fmtFn(LP[key]);
        const onChange = () => { LP[key] = Number(inp.value); val.textContent = fmtFn(LP[key]); renderMarkers(); };
        const inp = makeSlider(`sp-${key}`, min, max, step, LP[key], onChange);
        right.appendChild(wrapWithSteps(inp, onChange)); right.appendChild(val);
        row.appendChild(lbl); row.appendChild(right);
        return row;
      }

      body.appendChild(makeCurveRow("Zoom", def.keyZ, def.minZ, def.maxZ, def.stepZ,
        v => v.toFixed(2)));
      body.appendChild(makeCurveRow("Font", def.keyF, def.minF, def.maxF, def.stepF,
        v => v % 1 === 0 ? v + "px" : v.toFixed(1) + "px"));
    } else {
      const row = document.createElement("div");
      row.className = "sp-row";
      const lbl = document.createElement("label");
      lbl.className = "sp-label";
      lbl.htmlFor = `sp-${def.key}`;
      lbl.textContent = def.label;
      const right = document.createElement("div");
      right.className = "sp-right";
      const val = document.createElement("span");
      val.className = "sp-val";
      val.textContent = def.fmt(LP[def.key]);
      const onChange = () => { LP[def.key] = Number(inp.value); val.textContent = def.fmt(LP[def.key]); renderMarkers(); };
      const inp = makeSlider(`sp-${def.key}`, def.min, def.max, def.step, LP[def.key], onChange);
      right.appendChild(wrapWithSteps(inp, onChange)); right.appendChild(val);
      row.appendChild(lbl); row.appendChild(right);
      body.appendChild(row);
    }

    if (def.desc) {
      const desc = document.createElement("p");
      desc.className = "sp-desc";
      desc.textContent = def.desc;
      body.appendChild(desc);
    }
  }
}

function initSettingsPanel() {
  buildSettingsPanelBody();

  document.getElementById("settings-btn").addEventListener("click", () => {
    document.getElementById("settings-panel").classList.toggle("hidden");
    // Close info panel when settings opens to avoid z-index collision
    if (!document.getElementById("settings-panel").classList.contains("hidden")) {
      hideInfoPanel();
    }
  });

  document.getElementById("close-settings").addEventListener("click", () => {
    document.getElementById("settings-panel").classList.add("hidden");
  });

  document.getElementById("settings-reset").addEventListener("click", () => {
    Object.assign(LP, LP_DEFAULTS);
    buildSettingsPanelBody();
    renderMarkers();
  });

  document.getElementById("settings-save").addEventListener("click", async () => {
    const btn = document.getElementById("settings-save");
    btn.disabled = true;
    await saveLabelParams();
    btn.textContent = "Saved!";
    btn.disabled = false;
    setTimeout(() => { btn.textContent = "Save"; }, 1400);
  });

  // Live zoom readout in the curve section
  function updateZoomBadge() {
    const badge = document.getElementById("sp-zoom-badge");
    if (!badge || !S.viewer?.viewport) return;
    badge.textContent = "zoom: " + S.viewer.viewport.getZoom(true).toFixed(2);
  }
  S.viewer.addHandler("animation", updateZoomBadge);
  S.viewer.addHandler("animation-finish", updateZoomBadge);
  updateZoomBadge();
}

/* ============================================================
   Resizable panels
   ============================================================ */
function initResizablePanels() {
  function makeHandle(panel, cls, minW, minH, onResize) {
    const h = document.createElement("div");
    h.className = "resize-handle " + cls;
    panel.appendChild(h);
    h.addEventListener("mousedown", e => {
      e.preventDefault();
      const sx = e.clientX, sy = e.clientY;
      const sw = panel.offsetWidth, sh = panel.offsetHeight;
      const onMove = e => {
        const dx = e.clientX - sx, dy = e.clientY - sy;
        const newW = Math.max(minW, cls === "resize-bl" ? sw - dx : sw + dx);
        const newH = Math.max(minH, sh + dy);
        panel.style.width  = newW + "px";
        panel.style.height = newH + "px";
        if (onResize) onResize();
      };
      const onUp = () => {
        document.removeEventListener("mousemove", onMove);
        document.removeEventListener("mouseup",   onUp);
      };
      document.addEventListener("mousemove", onMove);
      document.addEventListener("mouseup",   onUp);
    });
  }

  function makeDraggable(panel, handle) {
    handle.addEventListener("mousedown", e => {
      if (e.target.closest("button, a, input, select")) return;
      e.preventDefault();
      const pr = panel.getBoundingClientRect();
      const cr = (panel.offsetParent || document.documentElement).getBoundingClientRect();
      const initLeft = pr.left - cr.left, initTop = pr.top - cr.top;
      const sx = e.clientX, sy = e.clientY;
      // Convert from right-anchored to left-anchored once
      panel.style.left  = initLeft + "px";
      panel.style.right = "auto";
      panel.style.top   = initTop  + "px";
      const onMove = e => {
        panel.style.left = Math.max(0, initLeft + e.clientX - sx) + "px";
        panel.style.top  = Math.max(0, initTop  + e.clientY - sy) + "px";
      };
      const onUp = () => {
        document.removeEventListener("mousemove", onMove);
        document.removeEventListener("mouseup",   onUp);
      };
      document.addEventListener("mousemove", onMove);
      document.addEventListener("mouseup",   onUp);
    });
  }

  const locPopup = document.getElementById("locate-map-popup");
  if (locPopup) {
    makeHandle(locPopup, "resize-br", 220, 200, () => { if (_leafletMap) _leafletMap.invalidateSize(); });
    const locHeader = document.getElementById("locate-map-header");
    if (locHeader) makeDraggable(locPopup, locHeader);
  }
  const infoPanel = document.getElementById("info-panel");
  if (infoPanel) {
    makeHandle(infoPanel, "resize-bl", 260, 120, null);
    const dragBar = document.getElementById("panel-drag-bar");
    if (dragBar) makeDraggable(infoPanel, dragBar);
  }
}

/* ============================================================
   Initialisation
   ============================================================ */
async function init() {
  const segmentsMeta = await loadJSONOptional("data/segments.json", null);
  const segmentList = Array.isArray(segmentsMeta?.segments) ? segmentsMeta.segments : [];
  S.segments = segmentList.length ? segmentList : [
    { number: 2, roman: "II", label: "Segment II" },
    { number: 3, roman: "III", label: "Segment III" },
    { number: 4, roman: "IV", label: "Segment IV" },
    { number: 5, roman: "V", label: "Segment V" },
    { number: 6, roman: "VI", label: "Segment VI" },
    { number: 7, roman: "VII", label: "Segment VII" },
    { number: 8, roman: "VIII", label: "Segment VIII" },
    { number: 9, roman: "IX", label: "Segment IX" },
    { number: 10, roman: "X", label: "Segment X" },
    { number: 11, roman: "XI", label: "Segment XI" },
    { number: 12, roman: "XII", label: "Segment XII" },
  ];

  const segmentNumbers = S.segments.map((s) => Number(s.number)).filter((n) => Number.isFinite(n));
  if (!segmentNumbers.includes(S.selectedSegment)) {
    S.selectedSegment = segmentNumbers[0] || DEFAULT_SEGMENT;
  }

  const boundsConfig = await loadJSONOptional("data/map_segment_bounds.json", null);
  const oldDefaultBounds = buildUniformBounds(segmentNumbers);
  const stitchedDefaultBounds = buildUniformBounds(segmentNumbers);
  S.boundsBySource.old = boundsConfig?.maps?.old?.segments || oldDefaultBounds;
  S.boundsBySource.stitched = boundsConfig?.maps?.stitched?.segments || stitchedDefaultBounds;
  S.boundsBySource.readableSeg4 = boundsConfig?.maps?.readableSeg4?.segments || { "4": { x0: 0, y0: 0, x1: 1, y1: 1 } };

  await reloadDb();

  // Readable tile source (Weber segment IV DZI)
  const isFile = window.location.protocol === "file:";
  S.readableTile = isFile ? {
    Image: {
      xmlns: "http://schemas.microsoft.com/deepzoom/2008",
      Url: "Readable_SegIV_files/",
      Format: "jpeg", Overlap: "1", TileSize: "254",
      Size: { Width: "4371", Height: "2105" }
    }
  } : "Readable_SegIV.dzi";

  // Original tile source (Miller full image)
  S.originalTile = isFile ? {
    Image: {
      xmlns: "http://schemas.microsoft.com/deepzoom/2008",
      Url: "Tabula_Peutingeriana_-_Miller_files/",
      Format: "jpeg", Overlap: "1", TileSize: "254",
      Size: { Width: "46380", Height: "2953" }
    }
  } : "Tabula_Peutingeriana_-_Miller.dzi";

  const stitchedEnabled = Boolean(boundsConfig?.maps?.stitched?.enabled);
  if (stitchedEnabled) {
    const stitchedSize = boundsConfig?.maps?.stitched?.size || {};
    if (isFile && Number.isFinite(Number(stitchedSize.width)) && Number.isFinite(Number(stitchedSize.height))) {
      const tileFolder = String(boundsConfig?.maps?.stitched?.tileFolder || "Tabula_Peutingeriana_150dpi_Stitched_files/");
      S.stitchedTile = {
        Image: {
          xmlns: "http://schemas.microsoft.com/deepzoom/2008",
          Url: tileFolder,
          Format: "jpeg", Overlap: "1", TileSize: "254",
          Size: { Width: String(Math.trunc(Number(stitchedSize.width))), Height: String(Math.trunc(Number(stitchedSize.height))) }
        }
      };
    } else {
      S.stitchedTile = String(boundsConfig?.maps?.stitched?.dzi || "Tabula_Peutingeriana_150dpi_Stitched.dzi");
    }
    S.newSourceKind = "stitched";
  } else {
    S.newSourceKind = "readable-seg4";
  }

  // Start on new map mode.
  S.viewer = OpenSeadragon({
    id: "openseadragon1",
    prefixUrl: "https://cdnjs.cloudflare.com/ajax/libs/openseadragon/4.1.0/images/",
    showNavigationControl: false,
    tileSources: activeTileSource(),
    showNavigator: true,
    navigatorPosition: "BOTTOM_RIGHT",
    navigatorAutoFade: true,
    defaultZoomLevel: 0,
    minZoomLevel: 0,
    maxZoomLevel: 80,
    visibilityRatio: 0.05,
    constrainDuringPan: false,
    blendTime: 0.1,
    animationTime: 0.5,
    backgroundColor: "#0f1117",
  });

  // Canvas setup
  S.canvas = document.getElementById("marker-canvas");
  S.ctx = S.canvas.getContext("2d");

  let initialFocused = false;

  S.viewer.addHandler("animation", renderMarkers);
  S.viewer.addHandler("animation-finish", renderMarkers);
  S.viewer.addHandler("resize", () => { sizeCanvas(); renderMarkers(); });
  function showAboutPanelOnStartup() {
    const ap = document.getElementById("about-panel");
    const bd = document.getElementById("about-modal-backdrop");
    ap?.classList.remove("hidden");
    bd?.classList.remove("hidden");
  }

  S.viewer.addHandler("open", () => {
    sizeCanvas();
    // OSD calls goHome(true) right after firing "open" — we override that in the
    // next animation frame once layout has also settled.
    requestAnimationFrame(() => {
      sizeCanvas();
      if (!initialFocused) {
        focusStartup(true);
        initialFocused = true;
        showAboutPanelOnStartup();
      }
      renderMarkers();
    });
  });

  // ResizeObserver keeps the canvas sized correctly on window resize.
  const ro = new ResizeObserver(() => {
    const w = S.viewer.element.clientWidth;
    const h = S.viewer.element.clientHeight;
    if (!w || !h || !S.viewer.viewport) return;
    sizeCanvas();
    renderMarkers();
  });
  ro.observe(S.viewer.element);

  // Fallback: if "open" never fires within 500 ms (very rare), force init.
  setTimeout(() => {
    if (initialFocused || !S.viewer.viewport) return;
    focusStartup(true);
    initialFocused = true;
    showAboutPanelOnStartup();
    renderMarkers();
  }, 500);

  window.addEventListener("resize", () => { sizeCanvas(); renderMarkers(); if (_leafletMap) _leafletMap.invalidateSize(); });

  // Setup UI
  await loadLabelParams();
  setupSegmentSelector();
  setupTypeFilters();
  setupControls();
  setupSearch();
  setupInteraction();
  initSettingsPanel();
  initResizablePanels();
  applyI18n(); // apply language to About panel content and type filter labels

  console.log(`Tabula Peutingeriana loaded: ${S.places.length} seg4 places, ${S.millerCalib.length} Miller calibrations`);

  // Listen for calibrate saves on the same local server and hot-reload the DB.
  try {
    new BroadcastChannel("tp_db_updated").onmessage = async () => {
      await reloadDb();
      renderMarkers();
      console.log("[TP] DB hot-reloaded from calibrate save");
    };
  } catch {}
}

async function reloadDb() {
  const db = await loadJSON("data/review_places_db.json?" + Date.now());
  const rawRecords = Array.isArray(db) ? db : (Array.isArray(db.records) ? db.records : []);
  console.log(`[TP] DB loaded: ${rawRecords.length} records, ` +
    `${rawRecords.filter(r => r.miller_rect_x1 != null).length} with Miller calibrations`);
  const placeData = rawRecords
    .filter((r) => {
      if (!r || typeof r !== "object") return false;
      if (!MAP_RUNTIME_TYPES.has(r.type)) return false;
      return r.px != null && r.py != null && Number.isFinite(Number(r.px)) && Number.isFinite(Number(r.py));
    })
    .map((r, idx) => ({
      ...r,
      id: r.id ?? r.record_id ?? `${r.source || "r"}-${r.data_id ?? idx}`,
      latin_std: r.latin_std || r.latin,
      modern: r.modern_preferred || r.modern_tabula || r.modern_omnesviae || "",
      province: r.province || r.region || "",
      country: r.country || guessCountryFromLatLng(r.lat, r.lng) || "",
      wiki_url: r.wiki_url || null,
      grid_col: r.grid_col ?? r.tabula_col,
      grid_row: r.grid_row ?? r.tabula_row,
      px: Number(r.px),
      py: Number(r.py),
      data_id: Number.isFinite(Number(r.data_id)) ? Number(r.data_id) : r.data_id,
    }));
  S.allRecords = rawRecords.map((r, idx) => ({
    ...r,
    id: r.id ?? r.record_id ?? `${r.source || "r"}-${r.data_id ?? idx}`,
    latin_std: r.latin_std || r.latin || "",
    modern: r.modern_preferred || r.modern_tabula || r.modern_omnesviae || "",
    province: r.province || r.region || "",
    country: r.country || guessCountryFromLatLng(r.lat, r.lng) || "",
    data_id: Number.isFinite(Number(r.data_id)) ? Number(r.data_id) : r.data_id,
  }));
  const draftMap = loadCalibrateDraftMap();
  S.millerCalib = loadMillerCalib(rawRecords);
  S.millerCalibHit = [...S.millerCalib].sort(
    (a, b) => (TYPE_DRAW_ORDER[b.type] ?? 4) - (TYPE_DRAW_ORDER[a.type] ?? 4)
  );
  S.places = placeData.map(p => ({
    ...p,
    ...(Number.isFinite(Number(p.data_id)) ? (draftMap.get(Number(p.data_id)) || {}) : {}),
    vx: p.px / IMG_W,
    vy: p.py / IMG_W,
  }));
}

// ── Landscape/fullscreen tip for mobile portrait ────────────────────────────
(function () {
  const tip    = document.getElementById("landscape-tip");
  const fsBtn  = document.getElementById("landscape-tip-fs");
  const closeB = document.getElementById("landscape-tip-close");
  if (!tip) return;

  function isPortraitTouch() {
    return window.matchMedia("(pointer: coarse) and (orientation: portrait)").matches;
  }
  function dismiss() {
    tip.classList.add("hidden");
    sessionStorage.setItem("landscapeTipDismissed", "1");
  }

  function maybeShow() {
    if (sessionStorage.getItem("landscapeTipDismissed")) return;
    if (isPortraitTouch()) tip.classList.remove("hidden");
    else                   tip.classList.add("hidden");
  }

  if (fsBtn) {
    fsBtn.addEventListener("click", () => {
      const el = document.documentElement;
      if (el.requestFullscreen)             el.requestFullscreen();
      else if (el.webkitRequestFullscreen)  el.webkitRequestFullscreen();
      dismiss();
    });
  }
  if (closeB) closeB.addEventListener("click", dismiss);

  // Hide automatically when the user rotates to landscape
  window.addEventListener("orientationchange", () => {
    setTimeout(() => { if (!isPortraitTouch()) dismiss(); }, 200);
  });
  window.matchMedia("(orientation: portrait)").addEventListener("change", e => {
    if (!e.matches) dismiss();
  });

  // Show on first load if portrait touch
  maybeShow();
})();

window.addEventListener("DOMContentLoaded", init);
