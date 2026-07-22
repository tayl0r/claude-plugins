# dev-flow — Flatten Fan-Out Delegations to the Orchestrator

**Date:** 2026-07-22
**Status:** Approved for planning
**Revises:** `2026-07-20-dev-flow-design.md` (topology only — the Artifact Contract, resume table, stops, and review protocol are unchanged)

## Goal

Make dev-flow's per-stage adversarial review actually run its model-diverse subagents (sonnet seeds / fable resolvers, per commit `e987265`) instead of silently collapsing to a single-model inline review — and fix the same latent break in Stage 3 (Execute). Achieve this by flattening the subagent topology so that every delegated skill that fans out into subagents is invoked by the orchestrator directly, never nested under a stage subagent.

## Problem

The current pipeline assumes a three-level spawn chain:

```
orchestrator (main session) → stage subagent → fan-out leaves (seed/resolver/fixer, or SDD implementers)
```

The middle→bottom hop is structurally impossible in Claude Code: **Task-spawned subagents do not receive the `Agent` tool**, so a stage subagent cannot spawn the review's seed/resolver agents. The documented "run them from the main session" fallback (`dev-flow/SKILL.md:185`) is unreachable — by the time `adversarial-review` runs, control is already inside a stage subagent with no way to hand spawning back up to the orchestrator. The observed result: the review degrades to fully-inline single-model, discarding the sonnet/fable diversity the model-tier split just added.

Stage 3 (Execute) carries the identical latent break: it wraps `subagent-driven-development` — itself a controller whose entire mechanism is spawning implementer/reviewer/fix subagents — inside a stage subagent (`dev-flow/SKILL.md:148`). The same wall applies; Execute would silently degrade to single-agent inline implementation.

## Root cause and the invariant

**Only the orchestrator (main session) can spawn subagents.** Therefore any delegated skill that *fans out into subagents to do its job* must run in the orchestrator's context. This is a family, not a special case; its members today are `adversarial-review` (design/plan/PR) and `subagent-driven-development` (execute). State it once as a pipeline invariant that every current and future member inherits:

> **dev-flow spawns only leaf subagents.** A delegated skill that itself spawns subagents to do its job — `adversarial-review`, `subagent-driven-development` — is invoked by the orchestrator directly, never nested under a stage subagent. Single-agent *produce* work (drafting a bare-idea design, a plan) may still run in a produce-subagent for context hygiene.

This is a **simplification**, not an added layer: it deletes the broken middle tier and the dead fallback, leaving `orchestrator + leaves`. It also makes dev-flow's use of `adversarial-review` identical to standalone human use — both invoke it from a spawn-capable session. The nested design was the anomaly that dropped the review somewhere it could not spawn.

## Topology

```
BEFORE (broken):                          AFTER (flat):
orchestrator                              orchestrator ───────────────┐
  └─ stage subagent                         ├─ produce-subagent (optional, main)
       └─ adversarial-review  ✗ can't       │    └─ drafts artifact, returns
            └─ seed/resolver/fixer          └─ invoke fan-out skill IN-CONTEXT
                                                 ├─ seed:sonnet ×2    (leaf)
                                                 ├─ resolver:fable ×N (leaf)
                                                 └─ fixer:main ×N      (leaf)
                                            Every subagent is a LEAF.
```

## Per-stage changes

| Stage | Change |
|---|---|
| **1 Design** | Produce the draft (bare-idea: inlined brainstorming bones; adopt-file: copy in + stamp front-matter) in a produce-subagent or inline. The **orchestrator** then invokes `adversarial-review` (mode `design`). |
| **2 Plan** | Produce the plan draft (`writing-plans`) in a produce-subagent. The **orchestrator** then invokes `adversarial-review` (mode `plan`). |
| **3 Execute** | The **orchestrator** invokes `subagent-driven-development` directly — it *becomes* SDD's controller. No execute-stage-subagent wrapper. SDD's terminal steps stay superseded by the existing Stage 3 overrides (final whole-branch review suppressed; `finishing-a-development-branch` not invoked). |
| **4 PR** | `gh pr create` (orchestrator), then the **orchestrator** invokes `adversarial-review` (mode `diff`), passing Stage 3's unresolved Minor findings. |
| **5 Merge** | Unchanged — no spawning. |

## Worktree seam

With no stage subagent to establish cwd, the fan-out skills' write agents must land in the pipeline worktree on `dev-flow/<slug>`. Resolved seam: **a generic working-dir argument, with write-side entry only.**

- **Reads need no entry.** Seed reviewers, resolvers, and SDD's task-reviewer read the artifact/diff **by absolute path** (`Read`, `git show dev-flow/<slug>:<file>`, or a review-package file) — a worktree is an ordinary directory on disk. SDD's task-reviewer already works this way (`task-reviewer-prompt.md:35`).
- **Write-side agents enter by path.** Fixer / commit agents call `EnterWorktree(<path>)` before writing. This is documented to work from cwd-pinned subagents *precisely because* dev-flow's worktree lives at `<main-root>/.claude/worktrees/dev-flow-<slug>` — the one location the native entry tool accepts from a pinned agent, and the switch affects only that agent.
- **dev-flow passes the path.** The orchestrator computes it via the existing read-only **Locate** step (`git worktree list --porcelain`) and hands it to the fan-out skill as its working-dir. SDD's implementer/fix template already carries `Work from: [directory]`; `adversarial-review` gains an optional working-dir argument — **absent → current checkout**, so standalone use is unchanged. This keeps both skills generic and keeps dev-flow owning worktrees (consistent with "worktrees are never delegated").
- **Execute's cwd.** SDD's controller runs `HEAD`-relative git and scripts (`git merge-base <default> HEAD`, `scripts/review-package BASE HEAD`), so for Stage 3 the **orchestrator itself enters the worktree** (`EnterWorktree(path)`) for the stage's duration and returns with `ExitWorktree(keep)` afterward — SDD then runs unmodified in a feature-branch checkout. Reviews do not require this: the orchestrator stays in main and reads via `git show`; only the fixer leaves enter. The "orchestrator stays in the main checkout" rule is refined to mean *for routing and resume reads* — the orchestrator may enter a worktree to drive a stage it owns, then return.

## The cost (honest)

The orchestrator now absorbs the **controller-level** context of each fan-out skill it drives (SDD's task loop; the review's group loop). This is unavoidable: model diversity ⇒ multiple subagents ⇒ orchestrator-spawned. Three things bound it:

1. Those skills return **summaries and file handoffs**, not raw diffs or full artifacts — SDD engineers a thin controller by explicit design (task briefs, review packages, and reports all move as files).
2. The nested design's promised context hygiene was **fictional** — it required nested spawn that never existed. This design pays the constraint's true cost for the first time rather than pretending it away.
3. It **degrades to a resume, not a failure** — resume keys off committed artifacts (plan checkboxes at branch tip), so if the orchestrator's context runs hot the run halts cleanly and `continue dev-flow` picks up from the branch.

## Edits this implies

- **`dev-flow/SKILL.md`** — rewrite the Pipeline preamble and Stages 1–4 to the flat topology; delete the "Subagent nesting" fallback under Environment Assumptions (`:185`) and replace it with the invariant above; update the Model Policy note (fan-out skills own their own model selection; the orchestrator directly spawns only produce-subagents, on main); document the orchestrator's worktree entry for Execute and the working-dir passing for reviews.
- **`adversarial-review/SKILL.md`** — add the optional working-dir argument and state the read-by-absolute-path / write-side-enters split; leave the two-tier seed/resolver protocol and its sonnet/fable model policy untouched.
- **`docs/superpowers/specs/2026-07-20-dev-flow-design.md`** and **`docs/superpowers/plans/2026-07-20-dev-flow-plan.md`** — sync the topology sections to match (the repo keeps spec, plan, and skill in lockstep).

## What does not change

The Artifact Contract, resume table, stops, worktree lifecycle ownership, the review's two-tier seed/resolver structure and its sonnet/fable model policy, and standalone `adversarial-review` behavior. Only the *dispatch topology* — who invokes the fan-out skills, and how they reach the worktree — changes.

## Smoke test

Run dev-flow on a small change and stop at `post-design`. Confirm:

1. `adversarial-review` spawned **separate sonnet seed reviewers and fable resolver agents** (the exact behavior that regressed — verify from the run, not just that a review happened).
2. The design doc was committed on `dev-flow/<slug>` with its `dev-flow` front-matter intact.
3. `continue dev-flow on <slug>` proceeds through Plan and into Execute, and Execute dispatches SDD implementers/reviewers as separate subagents (not inline).
