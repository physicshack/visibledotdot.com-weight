# visible.. weight

A mobile-first OMAD (one meal a day) diet, weight and health-journal tracker. It is a companion to
**visible..** (finance, repo `visibledotdot.com-budget`). It is a static, single-file web app: vanilla
JS, Chart.js from a CDN and optional Firebase Realtime Database sync. There is no build step.

| | |
|---|---|
| Production | `https://visibledotdot.com/weight.html` (Fasthosts, manual FTP upload, see [Deploy](#deploy)) |
| Sandbox | `https://physicshack.github.io/visibledotdot.com-weight/` (GitHub Pages, auto-deploys from `main`) |
| localStorage key | `weightTrackerData` (plus `weightUser` for the signed-in username) |
| Firebase | project `paymind-b1d51`, path `/health/{username}/` |

---

## Files

| File | What it is for |
|---|---|
| `index.html` | **The whole app**: markup, CSS and JS. It is the only file that gets deployed. On the production server it is uploaded **as `weight.html`**. The `index.html` at the production web root is the *budget* app, a different repo, so never overwrite it with this file. |
| `tests/run-tests.js` | Node unit tests for the maths, dates, migration, trend and projection helpers (no dependencies). |
| `tests/load-pure.js` | Pulls the `/* @pure-begin */ … /* @pure-end */` block out of `index.html` so Node can test it. |
| `tests/independent_check.py` + `tests/dump-model.js` | Cross-checks the trend/projection against `numpy.polyfit` on 45 fixtures. |
| `tests/browser_check.py` | Headless Chrome (Playwright) end-to-end checks. Firebase is blocked and mocked. |
| `scripts/import-to-firebase.ps1` | One-off script (June 2026) that imported a JSON backup into Firebase. Not part of the app. |
| `docs/spec.md` | Feature spec, data schema, maths reference. |
| `docs/ai-handoff.md`, `docs/task-queue.md`, `docs/unattended-ai-workflow.md` | Agent coordination docs. |
| `docs/lovable-visual-brief.md` | Visual design brief. |
| `AGENTS.md`, `CLAUDE.md` | Standing briefs for coding agents. |

### Pages inside `index.html`

The app is one HTML page with four tabs (`showPage(id)` toggles `#page-<id>`) and some modals.

| Tab / modal | Element | Purpose |
|---|---|---|
| **Reset** | `#page-reset` | Dashboard: reset day (days since `PHASES[0].start`, counted to *today*), current phase, total lost, target gap, phase strip, latest journal signal and win, next milestones (stone line, healthy BMI, target, next 5 kg), state check (OMAD-kept and alcohol *days* plus food-noise and energy averages over the last 14 check-in days), and quick wins. |
| **📈 Tracker** | `#page-tracker` | Stats cards, BMI gauge, goals (start, target, projected date, progress %), the *Weight Over Time* chart with start/end range sliders, the add-reading form (st/lb or kg), the all-records table (per-reading delete) and CSV export. |
| **📓 Journal** | `#page-journal` | Journal form (date, optional weight, notes, free text, 1–5 ratings for hunger, food noise, energy, focus and sleep, plus tags) and a searchable list. **You can add as many entries per day as you like.** Tap an entry to edit *that* entry; ✕ (tap twice) deletes only that entry. |
| **🍽 OMAD Tool** | `#page-omad` | Meal builder from the food database (± 0.5 steps, category filter, recent meals), calorie and macro totals against the calorie target, and *Log to Journal*, which always creates a new journal entry carrying a meal snapshot. *Edit Foods* opens the food editor modal. |
| Cloud Sync modal | `#userModal` | "Log in" = type a username. Data loads from or syncs to `/health/{username}`. Includes a danger zone (clear local data, delete account). |
| Import modal | `#importModal` | Replace all, or merge (lossless) from a JSON backup. |
| Food editor modal | `#foodEditorModal` | Add, edit and delete foods. |

---

## Data model (v4)

All state is one object saved to `localStorage['weightTrackerData']`, and the same object is what
*Export* downloads:

```jsonc
{
  "version": 4,
  "exported": "2026-10-18T20:00:00.000Z",
  "weightData": [
    { "id": "w-3f2c…", "date": "2026-10-18", "time": "07:10", "ts": 1792303800000,
      "createdAt": "2026-10-18T06:10:00.000Z", "kg": 88.8, "stone": 13, "lbs": 13, "frac": 0.77 }
  ],
  "journalData": [
    { "id": "j-9a1b…", "date": "2026-10-18", "day": "Sun", "time": "07:12", "ts": 1792303920000,
      "createdAt": "…", "updatedAt": "…", "comment": "…", "weight": 88.8, "notes": "",
      "checkin": { "hunger": 3, "foodNoise": 2, "energy": 4, "focus": 4, "sleep": 3, "winTag": "",
                   "omadKept": true, "alcohol": false, "exercise": true, "quickWin": false },
      "mealSnapshot": [ { "key": "POULTRY & MEATS-0", "name": "Chicken Breast (Med)", "qty": 2 } ] }
  ],
  "omadFoods": [ { "cat": "POULTRY & MEATS", "name": "…", "serving": "150g", "cals": 165, "protein": 35, "fat": 2, "carbs": 0, "fibre": 0 } ],
  "mealQtys": { "POULTRY & MEATS-0": 2 },
  "trueStartKg": null,
  "chartRangeStart": 0, "chartRangeEnd": 100, "chartRangeUserSet": false,
  "currentUnit": "st", "goalStart": "105.7", "goalTarget": "74.3", "calTarget": "1500"
}
```

* **Records are identified by `id`, never by date.** Any number of weight readings and journal
  entries can share a date. `date` is the user's local calendar date. `time` (HH:MM local) and `ts`
  (epoch ms) are set only when the entry is made for *today*. Back-dated entries have neither and are
  ordered by `createdAt`.
* Ordering everywhere is: `date`, then `ts` (or `date`+`time`), then `createdAt`, then `id`. Because
  of `ts`, the repeated 01:00–02:00 hour on 25 Oct (when the clocks go back) still sorts correctly.
* `mealQtys` keys are `"<category>-<index within category>"`. They are re-keyed automatically when
  foods are added, edited or deleted. Meal snapshots also store the food `name`, which is used first
  when a snapshot is reloaded.
* **Firebase** (`/health/{username}`) holds `weightData` and `journalData` as objects keyed by record
  id, `omadFoods` keyed `f0000…`, and `prefs` (unit, chart range, true start, goals, calorie target and
  `mealQtys` as a JSON string). The whole path is written with `.set()` on every save.

### Migration from v3 (one record per date)

v3 data had no ids. In v3 the journal was effectively keyed by date (a second save on the same day
replaced the first, and Firebase stored `journalData[<date>]`). Every load path (localStorage, the old
`window.storage` keys, Firebase and JSON import) runs `normalizeJournalEntries` /
`normalizeWeightEntries`, which:

* keep every valid row and drop only rows with no valid `YYYY-MM-DD` date (or, for weights, no
  positive kg);
* give legacy rows **deterministic** ids, `j-<date>-<n>` and `w-<date>-<HHMM|na>-<n>`, so two devices
  that migrate the same old data get the same ids and a later merge doesn't duplicate anything;
* fill missing `stone/lbs/frac` from `kg`, coerce `weight: ""` to `null`, and recompute `day` from the
  date.

Old date-keyed Firebase data loads unchanged. The first save from the new version rewrites that
user's Firebase path keyed by id. **Import → Merge** is lossless: records matched by id *and* content
are skipped, a record with the same id but different content is kept under a new id, and nothing
existing is overwritten.

---

## Maths

All helpers are pure functions in the `@pure` block of `index.html` and are unit-tested.

| Quantity | Definition |
|---|---|
| Units | 1 lb = 0.45359237 kg (exact). 1 st = 14 lb = 6.35029318 kg. Display rounds **total pounds** to 0.1 first, then splits into st + lb (so 95.25 kg = "15st 0.0lb"). Readings typed in st/lb are stored exactly, not via the rounded kg box. |
| BMI | `kg / h²`, h = 5′8″ = 1.7272 m (`HEIGHT_M`). Category from the displayed 1-dp value: < 18.5, < 25, < 30, else obese. Healthy-BMI weight = 24.9·h² = 74.28 kg. Gauge maps BMI 15–40 linearly; the colour stops sit at 14 %, 40 % and 60 %, matching 18.5, 25 and 30. |
| Since last reading | latest − previous reading by timestamp (negative = loss). |
| Total lost | baseline − latest. Baseline = *true start* if set (✎), else the first reading on or after `BASELINE_FROM` (2026-01-01). Tracker and Reset use the same baseline. |
| Last 30 days | readings dated today−29 … today (30 calendar days, inclusive): last − first. With fewer than 2 readings it shows "—" and how long ago the last reading was. |
| State check | the 14 most recent dates that have a check-in. OMAD-kept and alcohol count **days** (a day counts if any entry that day is ticked). Ratings are averaged over all entries in those days. |
| Calories | Σ qty × food value. The bar is calories ÷ target, capped at 100 %, and turns red above 110 %. |
| Progress % | (start − latest) / (start − target), clamped to 0–100 %. |
| Dates | Local calendar dates. Day arithmetic uses UTC day numbers, so DST days count as one day. Default form dates use the **local** date (not the UTC date). |

### Trend and extrapolation

* **Method: ordinary least-squares linear regression of weight against real calendar days**, over the
  readings in the chart's visible range (set by the sliders). Each day contributes **one point, the mean
  of that day's readings**, so three weigh-ins on one day don't count three times. Rate = slope × 7
  (kg/week).
* **Projection** continues the *same* line from its value on the last visible day (the end of the
  trend line, which is the anchor) until it reaches the target. Goal date = the first whole day on or
  after the crossing. The chart draws it only when the visible range ends at the latest reading.
* Edge cases: 0 or 1 reading, or all readings on one day → no rate ("needs readings on 2+ days").
  Losing less than 0.005 kg/wk (flat or rising) → no projection. Latest reading at or below target →
  "Target reached". Trend line already at or below target while the latest reading is above it → no
  projection, "keep logging". More than 730 days away → "more than 2 years" (the axis is not stretched).
  Crossing date before today (stale data) → the date is shown as *already passed* and the line is
  labelled "Projection (stale data)".
* **Graph**: weight readings are plotted at their real timestamps on a time axis (each entry is its own
  point). The y axis covers every plotted value (data, trend, projection and goal) with symmetric
  padding and ticks at whole kg or whole lb (labelled "13st 7lb"). Monotone interpolation stops the
  curve overshooting between readings. The x axis has a small pad so end points aren't clipped.
* Verified against `numpy.polyfit` (`tests/independent_check.py`). Example: the uneven Sep–Oct sample
  gives −0.443 kg/wk and target 85 kg on **19 Dec 2026**. The old index-based regression said
  −0.53 kg/wk and 9 Dec.

### Sliders

`rangeStart` and `rangeEnd` are 0–100 % (step 1) of the *readings* sorted by time. They are kept at
least 5 % apart: dragging either thumb into the other pushes it. Arrow keys, Home/End and touch work
natively. The values are saved (debounced, 500 ms) and restored, and the thumbs are re-synced to the
stored values on every render. Before the user moves them, the start defaults to the peak that began
the current loss run (`computeSmartChartStart`). As readings are added, a fixed percentage points at
a slightly later reading. An end at 100 % always means "latest".

---

## Tests

```bash
node tests/run-tests.js                     # 40 unit tests × 3 time zones (Europe/London, UTC, America/Los_Angeles)
python3 tests/independent_check.py          # numpy cross-check of trend + projection (needs numpy)
python3 -m http.server 8202 &               # then, with playwright installed:
python3 tests/browser_check.py http://localhost:8202/
```

The browser check blocks the Firebase SDK and database hosts and runs the Firebase load/sync code
against an in-page mock, so it never reads or writes live data.

---

## Deploy

Production is a **manual FTP upload** by David. Agents never upload.

1. Take `index.html` from `main`. It is the only file needed, because CSS and JS are inline,
   Chart.js, the date adapter, Firebase and the fonts come from CDNs, and the favicon is a data URI.
2. Upload it to the web root of `visibledotdot.com` (the same folder as the budget app's
   `index.html`) under the name **`weight.html`**. The URL is then
   `https://visibledotdot.com/weight.html`.
   * Do **not** upload it as `index.html` at the root: that would replace the budget app.
   * Do not upload `tests/`, `docs/`, `scripts/`, the `.md` files or `.git*`.
3. There is no base-URL or path config. The page uses no relative URLs, so it works at any path. The
   Firebase URL is a constant (`FIREBASE_URL`), so the same file works on Pages and in production.
   localStorage is per origin: data entered on github.io does not appear on visibledotdot.com and vice
   versa, unless both use the same username (cloud sync).
4. After upload, open `https://visibledotdot.com/weight.html`, hard-refresh once (the budget app's
   service worker has scope `/` but only passes through to the network), then tap 👤 *Guest* and enter a
   username to log in.
