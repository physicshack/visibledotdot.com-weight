# AI Handoff — visible.. weight

Use this file as the first stop for Claude, Codex, or any other assistant picking up this repo.
Always read this before doing any work. Update the Current Status section after each merged PR.

---

## Current Status

_Last updated: 2026-06-18 after PR #7 merge._

- App is live on GitHub Pages sandbox: `https://physicshack.github.io/visibledotdot.com-weight/`
- Production deployment (`visibledotdot.com/weight.html`) is manual via Fasthosts FTP — not yet updated
- Firebase sync is live: username-only auth, data at `/health/{userId}/`
- User `davejfowler` has 52 weight entries + 102+ journal entries in Firebase
- localStorage key: `weightTrackerData` (also used as Firebase export mirror)
- No automated tests
- No PWA manifest or service worker yet
- No README yet

### Recent changes (PR #7 — merged 2026-06-18)
Smart chart start date: on first load the Weight Over Time chart now defaults to the
peak weight that initiated the current loss run, rather than all-time history. Falls back
to a 3-month window when in a gaining phase. Slider still covers full history.
See `docs/task-queue.md` for full history.

---

## What's Next

Suggested priorities (in order):

1. **Create `docs/unattended-ai-workflow.md`** — signalling protocol, labels, task queue rules (mirror from budget repo)
2. **Add README** — local dev, file structure, deployment instructions
3. **Deploy PR #1–#3 + #7 to production** — Fasthosts FTP, human must action
4. **PWA setup** — manifest, icons, service worker
5. **Shared journal** — connect journal entries to the finance app (see sibling repo)

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
  Even 10 words of the entry as a subtitle would help scanning 102+ entries.
- "Today" card on Reset tab is mostly empty (just one button). Could show today's log status
  inline: did you log weight? OMAD kept today?
- OMAD Tool tab opens mid-list with no visible heading. A sticky category header or scroll-to-top
  would help orientation.
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
