# CLAUDE.md — Standing Brief for Claude Code

This file is read automatically by Claude Code at session start.
For the current task, always read `docs/ai-handoff.md` first.
For the unattended working protocol, read `docs/unattended-ai-workflow.md`.

---

## What This Project Is

**visible.. weight** is a mobile-first OMAD diet and weight tracking app for adults who want
calm, non-shaming tools to manage their health. It is a companion product to visible.. (finance).

The app tracks:
- Daily weight entries with stone/lbs/kg support
- OMAD meal building with macro tracking
- Custom food database
- Journal entries with hunger, energy, sleep, and exercise notes
- BMI monitoring and goal projection

Tone: calm, factual, never shaming. Same design philosophy as the finance app.

---

## Key Facts

| Thing | Value |
|---|---|
| Single source file | `index.html` (~114KB, vanilla JS) |
| localStorage key | TBD — check current code |
| Firebase project | `paymind-b1d51` (shared with finance app) |
| Firebase URL | `https://paymind-b1d51-default-rtdb.europe-west1.firebasedatabase.app` |
| Firebase path | `/health/{userId}/...` (planned, not yet implemented) |
| App version | V3 |
| Production | `https://visibledotdot.com/weight.html` (Fasthosts FTP) |
| Repo | `https://github.com/physicshack/visibledotdot.com-weight` |

---

## Read First

In order:

1. `docs/ai-handoff.md` — current task, what's done, what's next
2. `README.md` — local dev, file structure, deployment

---

## Sibling Project

The finance app lives at `https://github.com/physicshack/visibledotdot.com-budget`.
The two apps share a Firebase project. A shared journal connecting health and finance
data is planned — see `docs/ai-handoff.md` for current status.

---

## Hard Constraints

Never do these without explicit instruction:

- Change the localStorage schema or key
- Add Firebase sync without explicit approval of the data structure
- Commit an API key, secret, or credential
- Push directly to `main`
- Rewrite large sections of the app to fix small problems
- Deploy to Fasthosts without human instruction

---

## Encoding

Production file uses UTF-8. Never use PowerShell `Out-File` to write `index.html`.

Always use:
```powershell
[System.IO.File]::WriteAllText($path, $content, [System.Text.Encoding]::UTF8)
```

---

## Branch and PR Convention

- Branch as `claude/<short-description>`
- Open a PR for all non-trivial changes
- Doc-only fixes may go direct to `main`
- After merge: update `docs/ai-handoff.md`

---

## Unattended Workflow

See `docs/unattended-ai-workflow.md` for the full agent signalling protocol.
Signalling labels: `agent:claude-next`, `agent:codex-next`, `agent:blocked`.
