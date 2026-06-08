# Spec — visible.. weight (V3)

_Last updated: 2026-06-08. Maintained by Claude / Codex — update after each significant change._

---

## What This App Is

**visible.. weight** is a mobile-first OMAD diet and weight tracking app.
It is a companion product to visible.. (finance).

Target user: an adult who wants calm, factual, non-shaming tools to manage their weight.
No gamification, no streaks, no guilt. Same design philosophy as the finance app.

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

### `weightTrackerData` (localStorage)

```json
{
  "weightData": [
    { "date": "2026-04-27", "stone": 14, "lbs": 3, "frac": 0.2, "kg": 90.1 }
  ],
  "journalData": [
    {
      "date": "2026-04-27",
      "day": "Sun",
      "comment": "Felt good",
      "weight": 90.1,
      "notes": "",
      "checkin": {
        "hunger": 3, "foodNoise": 2, "energy": 4, "focus": 4, "sleep": 3,
        "winTag": "", "omadKept": true, "alcohol": false,
        "exercise": true, "quickWin": false
      }
    }
  ],
  "omadFoods": [ ... ],
  "mealQtys": { "Protein-0": 1.5 },
  "currentUnit": "kg",
  "calTarget": 1500,
  "chartRangeStart": 0,
  "chartRangeEnd": 100,
  "goalStart": 90.1,
  "goalTarget": 76.2
}
```

> **Schema constraint**: Never change `weightTrackerData` key or restructure without explicit
> human instruction. Existing user data would be silently lost on schema change.

### Weight entry with timestamp (added 2026-06-08)
Multiple readings on the same day are now stored with a `time` field (`HH:MM`):
```json
{ "date": "2026-06-08", "time": "08:30", "stone": 14, "lbs": 3, "frac": 0.2, "kg": 90.1 }
```
Legacy entries without `time` are unaffected.

---

## Firebase (planned, not yet implemented)

See `CLAUDE.md` for Firebase project details.

Planned path: `/health/{userId}/weight/`, `/health/{userId}/journal/`, `/health/{userId}/omad/`

Username-only auth (no login screen) — user types a name, data loads/saves under that path.
David's data import target user: `davejfowler`.

---

## Maths Reference

| Metric | Formula | Notes |
|---|---|---|
| BMI | `kg / HEIGHT_M²` | HEIGHT_M = 1.7272m (5'8") |
| BMI goal weight | `24.9 × HEIGHT_M²` = 74.3 kg | Upper edge of "Normal" |
| Trend rate | OLS regression of visible slice, slope scaled to real calendar days | Uses index-based OLS, converts to kg/week via real day-span |
| Weekly rate | `(slope_per_index × 7) / real_days_per_index` | Sign: negative = losing weight |
| Goal date | `today + (goalStart − goalTarget) / weeklyRate × 7` | Weeks needed × 7 days |
| Since Last | `latest.kg − prev.kg` | Negative = lost weight (shown with stat-good green) |
| Total Lost | `oldest.kg − latest.kg` | Positive = net loss since first entry |
| Last 30 Days | `oldest_30d.kg − latest.kg` | Positive = net loss — **note: sign opposite to Since Last** |

### Known maths issues (pending review in task-queue)

- **Sign inconsistency**: "Last 30 Days" uses `oldest − latest` (positive = good) while "Since Last" uses `latest − prev` (negative = good). Both display correctly with colour coding but the sign convention differs. Should be unified.
- **Trend line visual**: OLS uses indices (equally spaced) rather than calendar days for the regression x-axis. After chart x-axis is fixed to `type: 'time'`, the two-point trend line will visually represent calendar time correctly.
- **Goals DOM coupling**: `updateGoals()` reads `weeklyRateVal` text from the DOM using a regex. This is fragile — rate is formatted as `−0.52 kg/wk`. Works while the format is stable.

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
| Storage | localStorage (primary) + Firebase RTDB (planned) |
| Deployment | Fasthosts FTP → `visibledotdot.com/weight.html` |
| Sandbox | `physicshack.github.io/visibledotdot.com-weight` |

---

## Version History

| Version | Date | Notes |
|---|---|---|
| V3 | 2026-06-08 | Repo created, backup imported |
| V3.1 | 2026-06-08 | Chart x-axis fix, OMAD nav fix, multi-record/day support |
