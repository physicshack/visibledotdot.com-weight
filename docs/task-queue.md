# Task Queue — visible.. weight

This is the flight plan. Set by the human before leaving. Agents update status as work progresses.
Live coordination happens via PR comments and labels — see `docs/unattended-ai-workflow.md` (once created).

---

## Pending

- [ ] **Firebase multi-user setup** | branch: `codex/firebase-multi-user` | assigned: codex | risk: medium
  - Add username-only auth (no login screen) to the weight app
  - Data paths: `/health/{userId}/weight/`, `/health/{userId}/journal/`, `/health/{userId}/omad/`
  - Uses shared Firebase project `paymind-b1d51` — update Realtime Database security rules
  - Username stored in localStorage; UI: a small name input shown on first visit and in settings
  - No password, no email — user just types a name. David confirmed the security risk is acceptable.
  - Done when: app reads/writes to Firebase under `/health/{username}/...`; graceful fallback to localStorage if offline

- [ ] **Import backup to Firebase** | branch: `codex/import-davejfowler` | assigned: codex | risk: low
  - Depends on: Firebase multi-user setup (above)
  - Import `weight-tracker-backup-2026-06-08.json` to Firebase under user `davejfowler`
  - File path: `C:\Users\SL2\Desktop\Work\AI\visibledotdot.com-weight\weight-tracker-backup-2026-06-08.json`
  - weightData format: `{date, stone, lbs, frac, kg}` — matches app's data schema
  - Done when: `davejfowler` user in Firebase has all 400+ weight entries and journal data

- [ ] **Enable GitHub Pages** | assigned: human (repo settings) | risk: none
  - Enable GitHub Pages in repo settings → Source: `main` branch, root `/`
  - This makes the app available at `https://physicshack.github.io/visibledotdot.com-weight/`
  - No code changes needed — `index.html` at root will serve directly
  - Done when: URL above loads the weight app

- [ ] **Maths audit** | branch: `claude/maths-audit` | assigned: claude | risk: low
  - Full audit of all stats and their formulas — see `docs/spec.md` maths reference
  - Known issues to check and fix:
    1. **Sign inconsistency**: "Last 30 Days" uses `oldest − latest` (positive = good) but "Since Last" uses `latest − prev` (negative = good). Unify sign convention so both show loss as negative (standard convention), update colour logic accordingly.
    2. **Trend line OLS**: After x-axis time scale fix, verify the two-point trend line plots correctly on uneven date spacing. The visual slope should represent real calendar time.
    3. **Goals DOM coupling**: `updateGoals()` parses `weeklyRateVal` text via regex — consider passing rate value directly instead.
    4. **Total Lost**: verify `oldest.kg − latest.kg` correctly handles all edge cases (e.g. single entry, data out of order)
  - Done when: all formulas verified correct, sign conventions unified, spec.md maths table updated

- [ ] **Start weight / projection consistency** | branch: `claude/goals-audit` | assigned: claude | risk: low
  - Depends on: maths audit above
  - `goalStart` is pre-filled from `latest.kg` once (on first load, only if empty). If user changes it, the projection counts weeks from today at current trend rate.
  - Check: does the UI make it clear that `goalStart` is "starting from this weight, at the current rate, how long to reach target"? Is that the expected behaviour?
  - Consider adding "start from current weight" button to reset goalStart to latest reading
  - Done when: projection logic reviewed, UX clarified, spec.md updated

- [ ] **Unattended AI workflow doc** | branch: direct to main | assigned: claude | risk: none
  - Create `docs/unattended-ai-workflow.md` mirroring the budget repo version
  - Include: signalling protocol, labels, task queue reference, full execution rules
  - Done when: file exists and both agents can reference it for coordination

---

## In Progress

_(none)_

---

## Done

- [x] Repo created and initial `index.html` committed | 2026-06-08
- [x] `CLAUDE.md`, `docs/ai-handoff.md` created | 2026-06-08
- [x] `docs/spec.md`, `AGENTS.md`, `docs/task-queue.md` created | 2026-06-08
- [x] **Chart x-axis fix** (Task 1) | PR: `claude/ux-fixes` | 2026-06-08
  - Added `chartjs-adapter-date-fns`, changed chart x-axis from `type:'category'` to `type:'time'`
  - Data points now correctly spaced by real calendar dates
- [x] **OMAD → Journal navigation fix** (Task 5) | PR: `claude/ux-fixes` | 2026-06-08
  - Fixed `logMealToJournal()` — was navigating to Tracker instead of Journal
  - Now correctly navigates to Journal and pre-fills date + meal comment, scrolls to form
- [x] **Multiple records per day** (Task 6) | PR: `claude/ux-fixes` | 2026-06-08
  - `saveEntry()` now adds a `time` field (HH:MM) to new records
  - Multiple readings on the same day each get their own record (no overwrite)
  - Table shows time for entries that have it

---

## Human-Only Tasks (do not attempt unattended)

- Deploy to Fasthosts live site (`visibledotdot.com/weight.html`)
- Merge any PR to `main`
- Enable GitHub Pages (repo settings, browser action)
- Configure Firebase project billing or security rules that affect the finance app
