# Unattended AI Workflow — visible.. weight

Adapted from the finance repo version. Covers overnight / unattended work conventions
for Claude and Codex on this repository.

---

## Purpose

Enable Claude and Codex to keep useful work moving while the human is unavailable,
without needing the human to relay messages between agents or approve every step.

---

## What Agents May Do Unattended

- Read any repo file, PR, issue, or comment
- Create a branch (`claude/<name>` or `codex/<name>`)
- Edit files on the working branch
- Commit and push the working branch
- Open a draft PR
- Post PR and issue comments
- Apply or remove `agent:*` labels
- Make small corrective commits on a working branch during review

## What Agents Must Not Do Unattended

- Merge any PR
- Deploy to Fasthosts or any live site
- Delete branches
- Force push or rewrite git history
- Change production Firebase data or security rules
- Hard-code or expose secrets or API keys
- Change the `weightTrackerData` localStorage key or data structure
- Edit unrelated areas of code opportunistically

---

## Signalling Protocol

Labels are the **machine-readable state**. PR/issue comments are the **human-readable instruction**.
Both are written together on every handoff.

### Claude → Codex handoff
1. Post comment ending with `AGENT-CODEX-NEXT`
2. Remove `agent:claude-next`, add `agent:codex-next`

### Codex → Claude handoff
1. Post comment ending with `AGENT-CLAUDE-NEXT`
2. Remove `agent:codex-next`, add `agent:claude-next`

### Blocked state
Post comment with `AGENT-BLOCKED` and reason. Add `agent:blocked`, remove any agent-next label.
Neither agent acts until the human resolves it.

---

## Review Gate

`agent:*-next` labels are **merge gates**. Do not merge while any is present.

The reviewing agent must post one of these outcomes AND remove their label before merge:

| Outcome | Meaning |
|---|---|
| `REVIEW-PASS` | Remove reviewer label; leave all agent-next labels clear. Ready to merge. |
| `REVIEW-FINDINGS` | Remove reviewer label AND add implementer's `agent:*-next` label. List findings. |
| `REVIEW-BLOCKED` | Remove all agent-next labels AND add `agent:blocked`. Neither agent acts until human resolves. |

Before any merge:
- No `agent:*-next` label remains
- PR test plan updated — untested scenarios marked explicitly (not left as unchecked boxes)
- `docs/ai-handoff.md` updated after merge

---

## Stop Conditions

Stop and post `AGENT-BLOCKED` if:

- A product decision is needed and not covered by the brief or spec
- Two agents are likely to conflict on the same section of `index.html` (check for open PRs first)
- A security-sensitive choice arises
- A schema or localStorage change is needed but not pre-approved
- Checks fail and the cause is unclear after one reasonable fix attempt
- The task expands beyond its original scope

---

## Coordination Layers

| Layer | Format | Purpose |
|---|---|---|
| Flight plan | `docs/task-queue.md` | Human sets tasks before leaving; stable during session |
| Live state | PR/issue labels + comments | Agent-to-agent handoffs and review outcomes |
| Standing rules | `AGENTS.md`, `CLAUDE.md` | Loaded automatically each session; rarely changes |

---

## Task Queue Format

```markdown
## Pending
- [ ] Task description | branch: claude/branch-name | risk: low/medium/high | assigned: claude

## In Progress
- [ ] Task description | branch: claude/branch-name | assigned: claude

## Done
- [x] Task description | PR: #N | merged: YYYY-MM-DD
```

---

## Before Leaving (Human Checklist)

1. Populate `docs/task-queue.md` with tasks, risk levels, and "done" criteria
2. Mark which tasks are worker (Claude), reviewer (Codex), or human-only
3. Confirm no `agent:*-next` label is currently set (clear any stale ones)
4. Confirm Claude Code app will remain open on PC
5. Confirm no merge or deployment will happen unattended

---

## Role Defaults

**Claude — primary implementer**
Best for: editing `index.html`, feature changes, following a checklist, writing PR summaries.
Avoid: reviewing its own risky changes as the sole reviewer, merging, deploying.

**Codex — primary reviewer**
Best for: inspecting PRs, finding regressions, checking calculations/XSS/sync changes,
small corrective commits on the working branch.
May become worker if Claude hits a usage limit or is blocked.

**Hard rule:** the same agent must not be the only reviewer of a risky change it just made.

---

## `index.html` Conflict Guard

Before starting any task that touches `index.html`, check for open PRs that also touch it.
If one exists, pause and post `AGENT-BLOCKED` rather than risk a merge conflict on the
human's return.
