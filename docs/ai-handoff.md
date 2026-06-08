# AI Handoff — visible.. weight

Use this file as the first stop for Claude, Codex, or any other assistant picking up this repo.

---

## Current Status

Repo just created. `index.html` is the live V3 app, copied from production.

No Firebase sync yet — app currently uses localStorage only.
No automated tests.
No PWA manifest or service worker yet.

---

## What's Next

Suggested priorities (in order):

1. **Add README** — document the app, file structure, and deployment process
2. **Identify localStorage key** — document the current data schema
3. **Firebase sync** — add health data sync using the shared `paymind-b1d51` project
   - Proposed paths: `/health/{userId}/weight/`, `/health/{userId}/omad/`, `/health/{userId}/journal/`
4. **Shared journal** — connect journal entries to the finance app
5. **PWA setup** — manifest, icons, service worker

---

## Read First

1. `docs/ai-handoff.md` (this file)
2. `CLAUDE.md`
3. `README.md` (once created)
