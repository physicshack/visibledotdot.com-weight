# Lovable Visual Brief — visible.. weight

## Core Purpose

This brief guides a visual redesign of **visible.. weight**, a mobile-first OMAD diet and
weight tracking app. The objective is to reimagine the UI from a mobile-first perspective —
improving information hierarchy, daily usability, and calm visual tone — while keeping all
existing functionality intact.

---

## The User and Their Mindset

The user is an adult managing their weight through OMAD (one meal a day). They open this app:

- **First thing in the morning** — to log their weight and see where they stand
- **Before their meal** — to plan what they'll eat and check calories
- **At the end of the day** — to journal how it went

They are not looking for motivation or a pep talk. They want calm, factual information that
helps them make one clear decision: *am I on track today?*

The tone should feel like a trusted, quiet health companion — not a fitness app, not a
calorie counter with a scoreboard, not a weight-loss programme with a streak counter.

**What to avoid:** Progress badges, gamification, guilt-inducing red states, large
motivational text, before/after framing, medical warnings, marketing language.

---

## Design Principles

- **Mobile-first, thumb-friendly** — primary actions reachable without stretching.
  Target viewport: 390px wide (iPhone 15 Pro). Everything should feel native at this size.
- **Dark background, calm palette** — deep navy/charcoal base, not pure black.
  Accent: a single muted green for positive/active states. Avoid neon.
- **Answer first, data second** — lead each screen with a plain-English status,
  then the supporting numbers, then charts. Never lead with a chart.
- **One clear action per screen visit** — each tab should have one obvious next step.
- **Density: compact but breathable** — enough data to be useful, enough whitespace
  to feel calm. No card soup.

---

## Current App Structure (four tabs)

| Tab | Purpose |
|---|---|
| Reset | Mission control — phase progress, milestones, journal previews, today's prompt |
| Tracker | Weight chart, BMI, goal projection, add/edit weight entries |
| Journal | Daily check-in form + searchable entry history |
| OMAD Tool | Food database with quantity inputs → macro/calorie totals → log to journal |

---

## Screen-by-Screen Brief

### Reset Tab (Dashboard) — redesign priority: HIGH

**Current problems:**
- The phase progress timeline (Initial Fast → OMAD Reset → Active Loss → Maintenance) is the
  dominant element but not the most useful thing on a daily visit
- "State Check" (OMAD Kept, Food Noise, Energy, Alcohol) shows dashes — data exists but
  isn't surfacing
- "Today" card is almost empty — just a single button
- "Latest Signal" repeats the most recent journal entry in full, taking up half the screen

**Desired hierarchy for a daily visit:**
1. **Today's status** — did I log weight today? OMAD kept yesterday? One-line summary.
   e.g. *"Day 76 · Active Loss · Down 17.5 kg total"*
2. **State Check** — compact 2×2 grid of recent averages (OMAD adherence, food noise,
   energy, alcohol days). Small numbers, muted labels. Only show if data exists.
3. **Quick log** — inline weight entry (stone/kg) directly on this screen. Saves navigating
   to Tracker just to add today's reading.
4. **Phase progress** — smaller, secondary. A simple horizontal pill showing current phase
   with days elapsed. Not the hero element.
5. **Recent wins** — 2–3 most recent journal quick-wins, compact, positive only.

### Tracker Tab — redesign priority: MEDIUM

**Current problems:**
- Chart defaults to showing all data since 2008 (now fixed with smart start, but still
  opens mid-page on scroll)
- Stat cards (Current Weight, Since Last, Total Lost, Weekly Rate, BMI) are well-structured
  but crowded at mobile width

**Desired improvements:**
- Chart should be the hero — full width, prominent, loads immediately in view
- Stat cards below as a horizontal scroll strip at mobile width (not a wrapping grid)
- BMI gauge: keep but make smaller/secondary
- Add/Edit entry form: clean and minimal — date, weight value, save. That's it.

### Journal Tab — redesign priority: MEDIUM

**Current problems:**
- New entry form and entry list compete for attention — form is always open at top
- Entry rows show no preview text — just date and day name
- 6 numeric rating fields (hunger, food noise, energy, focus, sleep, alcohol) are presented
  as plain text inputs with placeholder "1-5" — not intuitive on mobile

**Desired improvements:**
- Collapse the new entry form behind a prominent "+ New Entry" button
- Entry rows: show first 15 words of journal text as a subtitle
- Replace numeric rating inputs with tap-to-select dot scales (1–5 dots, tap to fill)
  — much more thumb-friendly than typing a number
- Search bar: more prominent, pinned below the header

### OMAD Tool Tab — redesign priority: HIGH

**Current problems:**
- Quantity inputs look like inactive zero counters — not obviously interactive
- All 35 foods visible simultaneously with no filter — overwhelming to scan
- Fixed portion sizes only (e.g. always 150g chicken) — no per-gram adjustment
- No way to repeat yesterday's meal — quantities reset to zero every day
- "Today's Meal" sidebar panel is sticky but mostly empty below the macro totals

**Desired improvements:**
- Quantity controls: clear `−` / `+` buttons either side of the count, or a stepper input
- Category filter bar: horizontal pill tabs at the top (All, Meats, Seafood, Indian, etc.)
  — only show the selected category's foods
- "Repeat last meal" button: prominent, at the top of the food list — fills quantities
  from the most recently logged meal
- Today's Meal panel: show a running ingredient list (what's been added) above the totals,
  not just the macro summary
- Portion flexibility: small "×g" link on each item that opens a gram-entry override

---

## Navigation

Current nav bar: Reset · Tracker · Journal · OMAD Tool + Guest · Export · Import · St/Lb · (user)

At 390px this overflows. Consider:
- Bottom tab bar (native mobile pattern) for the four main sections
- Move Guest/Export/Import/unit toggle into a settings or profile drawer
- Active tab: filled icon + label. Inactive: outline icon only, no label.

---

## Colour and Typography Reference

Companion app (visible.. finance) uses warm off-white with amber accents on a light theme.
This app should feel like its dark-mode sibling — same family, different environment.

| Element | Suggestion |
|---|---|
| Background | `#0f1117` or similar deep navy-charcoal |
| Card surface | `#1a1f2e` |
| Primary accent | Muted teal-green e.g. `#3dd68c` (positive, calm — not neon) |
| Warning/attention | Muted amber `#f59e0b` |
| Negative/alert | Muted rose `#f43f5e` |
| Body text | `#e2e8f0` |
| Muted labels | `#64748b` |
| Font | DM Sans (already in use) — keep |
| Numbers/stats | DM Serif Display (already in use) — keep for hero figures only |

---

## Mockup Scope

Design **three mobile screens** at 390px width:

1. **Reset tab** — showing the redesigned daily dashboard with today's status, state check,
   quick log, and phase progress
2. **OMAD Tool tab** — showing the category filter, cleaner quantity controls, today's meal
   panel with ingredient list, and repeat-last-meal button
3. **Journal tab** — collapsed entry form, entry list with text previews, dot-scale ratings

Use realistic sample data throughout:
- Current weight: 13st 12.3lb (88.1 kg)
- Phase: Active Loss, Day 76
- Total lost: 17.5 kg
- Goal: 74.3 kg (11st 9.8lb)
- Recent OMAD adherence: ~80%

---

## What This Is Not

This is not a restructuring of functionality. All existing features stay. This is a visual
and interaction-pattern reimagining — making the existing app feel native, calm, and
effortless on a phone in someone's hand at 7am.
