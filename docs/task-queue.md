# Task Queue — visible.. weight

This is the flight plan. Set by the human before leaving. Agents update status as work progresses.
Live coordination happens via PR comments and labels — see `docs/unattended-ai-workflow.md` (once created).

---

## Pending

- [ ] **Unattended AI workflow doc** | branch: direct to main | assigned: claude | risk: none
  - Create `docs/unattended-ai-workflow.md` mirroring the budget repo version
  - Include: signalling protocol, labels, task queue reference, full execution rules
  - Done when: file exists and both agents can reference it for coordination

---

## In Progress

_(none — all 8 tasks from the initial brief are in PRs, see Done below)_

---

## Done

- [x] Repo created and initial `index.html` committed | 2026-06-08
- [x] `CLAUDE.md`, `docs/ai-handoff.md` created | 2026-06-08
- [x] `docs/spec.md`, `AGENTS.md`, `docs/task-queue.md` created | 2026-06-08

- [x] **Task 1 — Chart x-axis continuous time scale** | PR #1 `claude/ux-fixes-and-docs` | 2026-06-08
  - Added `chartjs-adapter-date-fns`; changed `type:'category'` to `type:'time'`
  - Data points now spaced by real calendar dates

- [x] **Task 2 — GitHub Pages** | 2026-06-08
  - Enabled via GitHub API; live at `https://physicshack.github.io/visibledotdot.com-weight/`

- [x] **Task 3 — Firebase multi-user with username** | PR #3 `claude/firebase-sync` | 2026-06-08
  - Firebase compat SDK 9.23.0 added; username-only auth (no login/password)
  - Header button: click Guest, enter username, data loads from / syncs to Firebase
  - Path: `/health/{username}/weightData` + `/health/{username}/journalData`
  - Firebase security rules updated and published: `/health/$userId` open read/write

- [x] **Task 4 — Import davejfowler backup to Firebase** | PR #3 `claude/firebase-sync` | 2026-06-08
  - `scripts/import-to-firebase.ps1` created and executed successfully
  - 52 weight entries + 104 journal entries written to `/health/davejfowler`
  - To use: open app, click Guest, type `davejfowler`

- [x] **Task 5 — OMAD save navigates to journal** | PR #1 `claude/ux-fixes-and-docs` | 2026-06-08
  - Fixed nav button index bug (was going to Tracker, not Journal)
  - Now: sets today date, pre-fills comment, stays on Journal, scrolls to entry form

- [x] **Task 6 — Multiple records per day** | PR #1 `claude/ux-fixes-and-docs` | 2026-06-08
  - `saveEntry()` stamps HH:MM time field; same-date entries no longer overwrite
  - Table shows time beneath date for timestamped entries

- [x] **Task 7 — Maths audit** | PR #2 `claude/maths-and-goals` | 2026-06-08
  - Fixed sign inconsistency: Last 30 Days now matches Since Last (negative = loss = green)
  - Added lb sub-line with arrow to Last 30 Days
  - BMI, weekly rate, total lost, trend regression all verified correct

- [x] **Task 8 — Start weight / projection logic** | PR #2 `claude/maths-and-goals` | 2026-06-08
  - Added "Reset to now" button beside goalStart field
  - Added sub-label clarifying projection always counts weeks from today
  - Formula confirmed correct and intentional

---

- [x] **Task 9 — Smart chart start date** | PR #7 `claude/smart-chart-start-date` | 2026-06-18
  - On first load, chart defaults to the peak weight that started the current loss run
  - Algorithm: walk back through monthly maxima; stop when gradient drops >1kg; find peak date
  - Falls back to 3-month window when gaining
  - Slider range still covers full history; user's manual position persisted via `chartRangeUserSet` flag
  - Reviewed by Codex across 2 rounds; 4 issues found and fixed before merge

---

## Human-Only Tasks (do not attempt unattended)

- Deploy to Fasthosts live site (`visibledotdot.com/weight.html`) — includes all merged PRs #1–#7
