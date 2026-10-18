# Spec — visible.. weight (V3)

_Last updated: 2026-06-18. Maintained by Claude / Codex — update after each significant change._

---

## What This App Is

**visible.. weight** is a mobile-first OMAD diet and weight tracking app.
It is a companion product to visible.. (finance).

Target user: an adult who wants calm, factual, non-shaming tools to manage their weight.
No gamification, no streaks, no guilt. (There is no streak logic in the app.) Same design philosophy as the finance app.

---

## Core Features

### Weight Tracker
- Enter daily weight in stone/lbs or kg (converts automatically)
- Chart with configurable date range (range sliders)
- Linear trend line + projected goal date
- Weekly rate stat (kg/wk, derived from chart's visible slice)
- BMI gauge (height: 5'8" / 1.7272m, hardcoded constant `HEIGHT_M`)
- Total lost, Since Last, Last 30 Days stat cards

### Journal
- Daily check-in: comment, optional weight reading, hunger/energy/sleep/focus ratings (1–5)
- Tags: OMAD kept, alcohol, exercise, quick win, custom win tag
- Searchable list of past entries
- Journal entries may have a weight reading separate from the main tracker

### OMAD Meal Builder
- Food database (hardcoded array, editable in-app via food editor modal)
- Quantity entry with auto-calculated macros and calorie total
- Calorie target bar
- Log meal to journal (navigates to Journal, pre-fills comment with meal summary)

### Goals
- User sets start weight and target weight
- App projects goal date using current trend rate
- Goal line overlaid on chart

### Data Management
- All data stored in `localStorage` key: `weightTrackerData`
- Export to JSON (full backup)
- Import from JSON backup
- Export to CSV
- Reset / wipe data

---

## Data Schema

**See `README.md` → "Data model (v4)" for the full schema and the v3 → v4 migration.** Summary:

- `localStorage['weightTrackerData']` holds `{version: 4, weightData[], journalData[], omadFoods[], mealQtys, trueStartKg, chartRange*, currentUnit, goalStart, goalTarget, calTarget}`.
- Every weight reading and journal record has a unique `id` (plus `createdAt`, and `time`/`ts` when entered for today). **The date is not a key**: any number of records per day.
- v3 records (no id; journal one-per-date) are migrated losslessly on load with deterministic ids `j-<date>-<n>` / `w-<date>-<HHMM|na>-<n>`.

> **Schema constraint**: never change the `weightTrackerData` key. Structural changes must be additive and migrated in `normalizeWeightEntries` / `normalizeJournalEntries`.

---

## Firebase (live as of PR #3, 2026-06-08)

See `CLAUDE.md` for Firebase project details.

Path: `/health/{userId}/` — contains `weightData`, `journalData`, `omadFoods`, `prefs`

Username-only auth (no login screen) — user clicks Guest button, types a name, data loads/saves
under that path. User `davejfowler` has 52 weight entries + 100+ journal entries imported.

---

## Maths Reference

Full definitions are in `README.md` → "Maths". All helpers live in the `@pure` block of `index.html` and are covered by `tests/run-tests.js`.

| Metric | Formula |
|---|---|
| BMI | `kg / HEIGHT_M²`, HEIGHT_M = 1.7272 m; category from the displayed 1-dp value |
| Trend rate | OLS of daily-mean kg on **real calendar days** over the visible slider range; kg/wk = slope × 7 |
| Goal date | extend the same regression line from its end point (last visible day) to the target; first whole day on/after the crossing |
| Since Last | latest − previous reading by timestamp (negative = loss) |
| Total Lost | baseline − latest; baseline = true start, else first reading on/after `BASELINE_FROM` (2026-01-01). Same on Tracker and Reset |
| Last 30 Days | readings dated today−29 … today: last − first (negative = loss) |
| Progress | (start − latest)/(start − target), clamped 0–100 % |

Audit of 18 Oct 2026 (PR #11) replaced the index-based regression, the projection that was drawn from the first trend point to goal date + 7 days, and the DOM-parsed goal rate. The "known issues" listed here before are fixed.

---

## Key Constants (index.html)

| Constant | Line | Value |
|---|---|---|
| `HEIGHT_FT` | ~992 | 5 |
| `HEIGHT_IN` | ~992 | 8 |
| `HEIGHT_M` | ~993 | `((5×12)+8) × 0.0254 = 1.7272m` |
| `STORAGE_KEY` | near top of JS | `'weightTrackerData'` |

---

## Tech Stack

| Thing | Detail |
|---|---|
| Framework | None — vanilla JS, single HTML file |
| Charts | Chart.js 4.4.0 (CDN) + chartjs-adapter-date-fns 3.x |
| Fonts | DM Serif Display, DM Sans (Google Fonts) |
| Storage | localStorage (primary) + Firebase RTDB (live, username sync) |
| Deployment | Fasthosts FTP → `visibledotdot.com/weight.html` |
| Sandbox | `physicshack.github.io/visibledotdot.com-weight` |

---

## Version History

| Version | Date | Notes |
|---|---|---|
| V3 | 2026-06-08 | Repo created, backup imported |
| V3.1 | 2026-06-08 | Chart x-axis fix, OMAD nav fix, multi-record/day support |
| V3.2 | 2026-06-08 | Firebase sync live, username auth, davejfowler data imported |
| V3.3 | 2026-06-18 | Smart chart start date — auto-detects peak weight for default view |
| V4 | 2026-10-18 | Unique-id records: unlimited journal entries per day + migration; time-based trend/projection; tests |
