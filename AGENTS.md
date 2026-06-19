# AGENTS.md — Standing Brief for Codex

This file is read automatically by Codex at session start.
It is the minimum context needed to work on this repo without conversation history.
For the current task, always read `docs/ai-handoff.md` first.

---

## What This Project Is

**visible.. weight** is a mobile-first OMAD diet and weight tracking app for adults
who want calm, non-shaming tools to manage their health. It is a companion product to
visible.. (finance).

The app tracks:
- Daily weight entries (stone / lbs / kg)
- OMAD meal building with macros
- Custom food database
- Journal entries with health check-in ratings
- BMI, trend rate, and goal projection

Tone: calm, factual, never shaming. Same design philosophy as the finance app.

---

## Key Facts

| Thing | Value |
|---|---|
| Single source file | `index.html` (~114KB, vanilla JS) |
| localStorage key | `weightTrackerData` |
| Firebase project | `paymind-b1d51` (shared with finance app) |
| Firebase URL | `https://paymind-b1d51-default-rtdb.europe-west1.firebasedatabase.app` |
| Firebase path | `/health/{userId}/` — live, contains `weightData`, `journalData`, `omadFoods`, `prefs` |
| App version | V3 |
| Sandbox | `https://physicshack.github.io/visibledotdot.com-weight` |
| Production | `https://visibledotdot.com/weight.html` (Fasthosts FTP) |
| Repo | `https://github.com/physicshack/visibledotdot.com-weight` |

---

## Read First

In order:

1. `docs/ai-handoff.md` — current task, what's done, what's next
2. `docs/spec.md` — full app spec, data schema, maths reference
3. `docs/unattended-ai-workflow.md` — signalling convention, merge gates, execution rules
4. `README.md` — local dev, file structure, deployment (once created)

---

## Roles

You may be acting as implementer, reviewer, documenter, designer/critic, or release operator.
Pick up whatever role the task needs.

The one hard rule: **do not be the only reviewer of a risky change you just made.**

---

## Working Directly With Claude

Coordinate through the shared GitHub PR or issue — the human should not relay messages.

Before acting on an existing PR, branch, or issue, inspect:

1. PR/issue description and conversation comments
2. Review comments and unresolved review threads
3. Changed files and latest diff
4. Current labels and branch state

Use plain text handoff markers (not @mentions):

- `AGENT-CODEX-NEXT` when Codex should act next
- `AGENT-CLAUDE-NEXT` when Claude should act next
- `AGENT-BLOCKED` only when a real human-only decision or safety block exists

For handoff labels on PRs:

- If asking Claude to act: remove `agent:codex-next`, add `agent:claude-next`
- If Codex should act: remove `agent:claude-next`, add `agent:codex-next`
- If human input required: add `agent:blocked`, clear agent-next labels
- If no one needs to act: leave all handoff labels clear

---

## PR Review Gate Protocol

Agent-next labels are **merge gates**, not notifications. Do not merge while any `agent:*-next` label is present.

**Handoff labels:**
- `agent:claude-next` — Claude must act before merge
- `agent:codex-next` — Codex must act before merge
- `agent:blocked` — human decision required; neither agent acts

**Review outcomes** — the reviewing agent posts one of these AND updates labels atomically:
- `REVIEW-PASS` — remove reviewer label; leave all agent-next labels clear (ready to merge)
- `REVIEW-FINDINGS` — remove reviewer label AND add implementer's `agent:*-next` label (findings must not coexist with a clear label state)
- `REVIEW-BLOCKED` — remove all agent-next labels AND add `agent:blocked`

**Before merging a PR:**
- Confirm no `agent:*-next` label remains
- Update the PR test plan — mark untested scenarios explicitly rather than leaving boxes unchecked
- Update `docs/ai-handoff.md` after merge

---

## Hard Constraints

Never do these without explicit instruction:

- Change the `weightTrackerData` localStorage key or data structure
- Add Firebase sync without explicit approval of the data paths
- Commit an API key, secret, or credential
- Push directly to `main`
- Deploy to Fasthosts without human instruction
- Rewrite large sections of the app to fix small problems
- Call `syncToFirebase()` automatically on an interactive username switch — this silently copies
  the current user's data to the new Firebase path (known bug, fix spec'd in `docs/ai-handoff.md`)

---

## Firebase Security Model

Username-as-password: anyone who knows a username can read and write that Firebase path.
The fix for the silent user-switch data upload is part of the next PR (see `docs/ai-handoff.md`).

---

## Encoding

Production file uses UTF-8. **Never use PowerShell `Out-File`** to write `index.html`.

Always use:
```powershell
[System.IO.File]::WriteAllText($path, $content, [System.Text.Encoding]::UTF8)
```

---

## XSS Protection

All user data written to `innerHTML` must go through the `esc()` helper function.
Check existing call sites before adding new `innerHTML` assignments.

---

## Branch and PR Convention

- Branch as `codex/<short-description>`
- Open a PR for all non-trivial changes
- Doc-only fixes may go direct to `main`
- After merge: update `docs/ai-handoff.md`
- Co-author commit messages with: `Co-Authored-By: Codex <noreply@openai.com>`

---

## Sibling Project

The finance app lives at `https://github.com/physicshack/visibledotdot.com-budget`.
The two apps share the Firebase project `paymind-b1d51`. The `.claude/` directory is
excluded from git and contains Claude's local settings — do not modify it.

---

## What Not to Touch (unless explicitly asked)

- `.gitignore` — set deliberately; `.claude/` is intentionally excluded
- Firebase security rules — managed via Firebase console, not in repo
- `HEIGHT_M` / `HEIGHT_FT` / `HEIGHT_IN` constants — tied to user's actual height
- `STORAGE_KEY` value — changing it silently destroys all existing user data
