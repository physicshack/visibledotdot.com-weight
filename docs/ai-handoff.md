# AI Handoff — visible.. weight

Use this file as the first stop for Claude, Codex, or any other assistant picking up this repo.
Always read this before doing any work. Update the Current Status section after each merged PR.

---

## Current Status

_Last updated: 2026-06-19 after PR #9 merge._

- App is live on GitHub Pages sandbox: `https://physicshack.github.io/visibledotdot.com-weight/`
- Production deployment (`visibledotdot.com/weight.html`) is manual via Fasthosts FTP — not yet updated
- Firebase sync is live: username-only auth, data at `/health/{userId}/`
- User `davejfowler` has 52 weight entries + 102+ journal entries in Firebase
- localStorage key: `weightTrackerData` (also used as Firebase export mirror)
- No automated tests
- No PWA manifest or service worker yet
- No README yet

### Recent changes (PR #9 — merged 2026-06-18)
visible.. design system integration: new SVG logo with animated rising sun, sunrise/horizon
CSS token palette (hex baselines + oklch overrides via @supports), sunrise gradient on the
three primary commit buttons only (Save weight, Save Entry, Log to Journal), text-sunrise
on Reset Day and Total Lost hero numbers, horizon-divider on nav, favicon updated, page
title changed to "visible.. weight". Reduced-motion respected in CSS and JS.

### PR #7 — merged 2026-06-18
Smart chart start date: on first load the Weight Over Time chart defaults to the
peak weight that initiated the current loss run, rather than all-time history. Falls back
to a 3-month window when in a gaining phase. Slider still covers full history.

---

## What's Next

Priority order agreed with Dave (2026-06-19):

1. **PR #10 — OMAD UX + Firebase user management** (in progress, branch: `claude/omad-and-user-management`)
   - See full spec below
2. **Deploy to production** — Fasthosts FTP, human must action after each merged PR
3. **PWA setup** — manifest, icons, service worker
4. **Add README** — local dev, file structure, deployment instructions
5. **Shared journal** — connect journal entries to the finance app (see sibling repo)

**Bigger lift / later:**
- Reset tab hierarchy reorder (today's status first, state check second, quick inline weight log)
- Tracker tab: chart as hero, stat cards as horizontal scroll strip
- Journal tab: collapsed entry form, dot-scale tap inputs for ratings
- Nav: bottom tab bar pattern, settings drawer for Guest/Export/Import/unit toggle

---

## Next PR Spec — OMAD UX + Firebase User Management

### OMAD Tool changes

**1. Quantity steppers (0.5 increments)**
Replace the current bare `0` click-counter buttons with explicit `−` / `+` buttons either side
of the quantity display. Step size: 0.5. Show one decimal place when non-integer (e.g. `1.5`),
whole number when integer (e.g. `2`). Minimum: 0. No maximum enforced.

**2. Last meals panel — top 5 + full history**
Above the food list, add a "Recent Meals" row showing the last 5 logged meals as selectable
chips/cards (date + calorie total). Tapping one fills all quantities from that meal.
A "Show all" control expands to a scrollable list of all logged meals. Meal history is derived
from journal entries that contain OMAD macro data (already stored via "Log to Journal").

**3. Category filter pills**
Horizontal pill bar above the food list. Pills: All (default active) + one per category
(Poultry & Meats, Indian, Seafood, etc. — derived from the food data, not hardcoded).
Default state: All selected, full list visible. Pressing a category pill filters to that
category only. Pressing the active pill again cancels the filter (returns to All).
Only one category active at a time. Pills are cancellable — pressing the active non-All
pill deselects it and returns to All.

### Journal changes

**4. Entry text previews**
Each journal entry row currently shows only `Day · YYYY-MM-DD`. Add a subtitle line showing
the first ~12 words of the entry text field, truncated with ellipsis. If no entry text,
show nothing (don't show a blank subtitle row). Style: muted, smaller than the date.

### Firebase user management changes

**5. Fix: user-switch silent data upload**
Bug: when a user types a new username and Firebase has no data for that path, the app
currently calls `syncToFirebase()` silently, pushing the current user's local data to the
new username's Firebase path. This is a data exposure risk (e.g. typing "guest" creates a
copy of the real user's data at `/health/guest/`).

Fix: on interactive username switch (`setUsername()`), if Firebase returns no data for the
new path, show a confirmation modal:
- "No cloud data found for '[username]'. What would you like to do?"
- [Upload my current data to this account] — existing behaviour, now explicit
- [Start fresh — clear local data] — wipes localStorage, starts empty
Do NOT call `syncToFirebase()` automatically. This does not affect the on-startup reconnect
path (`init()`) which can continue to auto-push for genuine new account creation.

**6. Clear local data action**
Add to the username modal (below the sign-out option, in a "Danger zone" section):
"Clear local data" — wipes `weightTrackerData` from localStorage and signs out.
Firebase data is untouched. Requires a single confirmation click ("Are you sure?").
Use case: device-local cache is stale or wrong; re-signing in will repopulate from Firebase.

**7. Delete account action**
Add to the username modal danger zone:
"Delete account" — deletes `/health/{userId}/` from Firebase AND clears localStorage AND
signs out. Permanent and irreversible. Requires the user to type their username to confirm
before the delete fires. Only available when signed in (fbUser is set).

**8. Username modal copy**
Add to the existing warning text: "Choose something non-guessable — anyone who knows your
username can read and overwrite your data."

---

## Known Issues & Feedback

_This section captures observations from Claude and Codex reviews. Codex: please add your own findings._

### From Claude (2026-06-18 app review)

**Bugs / data issues**
- "Last 30 Days" shows 0.0 kg / 0 readings — most recent entry is 52 days old so the window is
  working correctly, but the card gives no indication of this. Should say something like
  "last entry: 52 days ago" rather than silently showing zero.
- "State Check" dashes on Reset tab (OMAD Kept, Food Noise, Energy, Alcohol Days all `—`)
  despite 102 journal entries. Likely a date-range or calculation bug — data exists but isn't
  being surfaced.
- Weekly Rate (Trend) shows 0.00 kg/wk despite 7.1 kg total lost — possibly because the
  chart's visible slice (post smart-start fix) needs more recent data points to calculate slope.

**UX improvements**
- Journal entry rows show no content preview — just `Sat · 2026-05-23` with no text hint.
  Even 12 words of the entry as a subtitle would help scanning 102+ entries. _(spec'd for next PR)_
- "Today" card on Reset tab is mostly empty (just one button). Could show today's log status
  inline: did you log weight? OMAD kept today?
- The right side of the nav bar (Guest, Export, Import, St/Lb) feels tight at ~960px and will
  likely overflow on real mobile (~375px).

**Feature ideas**
- OMAD adherence streak indicator on Reset dashboard — simple, motivating
- Quick inline weight entry on the Reset dashboard "Today" card — saves a tab navigation
- Journal search box is easy to miss (top-right corner) — more prominent placement would help

### From Codex
_(add findings here)_

---

## Read First

1. `docs/ai-handoff.md` (this file)
2. `CLAUDE.md` (Claude) or `AGENTS.md` (Codex)
3. `docs/spec.md` — full app spec, data schema, maths reference
4. `docs/task-queue.md` — what's done, what's pending
