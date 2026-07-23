# dev-flow — Flatten to Orchestrator-Driven Fan-Out

**Date:** 2026-07-22
**Status:** Approved for planning
**Supersedes (architecture):** `2026-07-22-dev-flow-nested-review-fix-design.md`. That design kept a *nested* topology (stage subagent → seed/resolver reviewers) guarded by a capability gate. **Nested subagent spawning was removed in Claude Code 2.1.218** (see Root cause), so the nested topology cannot run. This design flattens: the orchestrator drives all fan-out; no subagent ever spawns a subagent.

## Goal

Make `dev-flow` run its model-diverse adversarial review (sonnet seeds / fable resolvers) and its subagent-driven Execute stage on **any** Claude Code version — specifically without relying on nested subagent spawning, which the harness no longer grants. Preserve model diversity; never silently degrade.

## Root cause (why the nested design broke)

`dev-flow` 1.1.0's per-stage review runs *nested*: the orchestrator spawns a stage subagent, which invokes `adversarial-review`, which spawns seed + resolver sub-subagents on diverse models. That requires a spawned subagent to itself hold the `Agent` tool (2-level spawning).

**Claude Code 2.1.218 does not grant spawned subagents the `Agent` tool.** Confirmed:
- A session freshly launched under 2.1.218 (real user repro, twice, incl. after `/reload-plugins`): a spawned `general-purpose` subagent has `Skill` but **not** `Agent`; `ToolSearch select:Agent` from inside it returns "No matching deferred tools found".
- The only reason this wasn't caught during 1.1.0 development: that session was a **lingering 2.1.217 process** (nesting still worked in-process) while the on-disk binary had already updated to 2.1.218. The verification was real for 2.1.217 and stale for 2.1.218.
- Harness direction (release notes + open issue #60763): nested spawning is **off by default** (env-var-gated at most) and subagents lacking `Agent` is "by design". The recommended pattern is **top-level orchestration only** — workers don't spawn.

So the "nesting is available" premise is false on current and future versions. `dev-flow`'s capability gate correctly refuses to run (loud halt, no silent single-model review) — but that means the pipeline can't run at all. The fix is to stop depending on nesting.

## Decision: flatten (orchestrator drives all fan-out)

**Invariant:** *`dev-flow` spawns only leaf subagents. The orchestrator (main session) is the only spawner — it always holds `Agent`, on every version. Any delegated skill that itself fans out into subagents (`adversarial-review`, `subagent-driven-development`) is invoked by the orchestrator directly, never nested inside a stage subagent.*

This is the harness's recommended pattern and Anthropic's shipped multi-agent shape (a lead + leaf workers). It is also a **net simplification** of 1.1.0: the entire nesting-safety apparatus is deleted, because the failure mode it guarded (a stage subagent that can't spawn) no longer exists — the orchestrator always can.

Rejected: an env-var stopgap (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`) — a per-machine flag the harness defaults off and discourages; a remember-a-flag design that breaks on the next machine. Rejected: a hybrid that keeps a nested fast-path — pure speculation now that nesting is off-by-default and discouraged; it re-adds the complexity flatten removes for zero reliable benefit.

## The design

### Topology

```
orchestrator (main session — always holds Agent)
  ├─ produce-subagent (optional, leaf)  → drafts an artifact, returns a summary
  └─ invoke fan-out skill IN-CONTEXT (adversarial-review / SDD)
       ├─ seed:sonnet ×2      (leaf)
       ├─ resolver:fable ×N   (leaf)
       └─ fixer:main ×N       (leaf)     ← writes/commits in the worktree via `git -C`
Every subagent is a LEAF. No subagent spawns a subagent.
```

### Per-stage

| Stage | Flat flow |
|---|---|
| **1 Design** | Produce the draft (bare-idea: inlined brainstorming bones; adopt-file: copy+stamp) inline or in a produce-subagent. The **orchestrator** then invokes `adversarial-review` (mode `design`). |
| **2 Plan** | Produce the plan draft (`writing-plans`) in a produce-subagent. The **orchestrator** invokes `adversarial-review` (mode `plan`). |
| **3 Execute** | The **orchestrator** invokes `subagent-driven-development` directly — it *is* SDD's controller and spawns implementer/reviewer subagents itself (one level — always works). No execute-stage-subagent wrapper. SDD's terminal steps stay superseded by the existing overrides. |
| **4 PR** | `gh pr create` (orchestrator), then the **orchestrator** invokes `adversarial-review` (mode `diff`). |
| **5 Merge** | Unchanged — no spawning. |

### Worktree seam (unchanged from the probe finding — `git -C`, threaded)

The review's write-side agents are spawned by the orchestrator (in the main checkout), so they cannot inherit a worktree cwd. `adversarial-review` already resolves its working directory once and threads the absolute path to every spawned agent; write-side fixers use `git -C <path>` + absolute file paths (the depth-2 `EnterWorktree` probe found harness entry unavailable). The orchestrator computes the pipeline worktree path (a read-only `git worktree list`) and passes it as `working-dir`. This seam is **already implemented** in 1.1.0 and is exactly what flatten needs.

### Model diversity — preserved

The orchestrator spawns the sonnet seeds and fable resolvers directly (one level — works on 2.1.218). Diversity is *guaranteed by construction*: the orchestrator always holds `Agent`, so the reviewers always spawn on their tiers. There is no degraded path to guard.

## What this REMOVES (simplification vs 1.1.0)

- **The Capability gate** (`## Capability gate` section) — it existed to detect nesting; flatten needs no nesting, and the orchestrator's own spawn capability is a given.
- **The dispatch-preamble "a stage never performs an adversarial review itself / halt on missing Skill/Agent" clause** — stages no longer invoke the review at all (the orchestrator does), so the no-`Skill`/no-`Agent` stage failure mode is gone.
- **Provenance forwarding through the stage summary + the orchestrator's "halt on missing provenance" check** — the orchestrator runs the review itself and sees the reviewers it spawned directly, so there is nothing to forward or re-verify across a stage boundary.
- **The "Subagent nesting (required)" Environment Assumption** — replaced by "the orchestrator is the only spawner; leaf subagents never spawn."

## What this KEEPS

- The `git -C` **working-directory rule** in `adversarial-review`'s Contract (resolve once, thread always).
- **Model diversity** (sonnet seeds / fable resolvers, `opus` resolvers in a Fable-family session) and the two-tier seed/resolver protocol — untouched.
- **Provenance** in `adversarial-review`'s report-back — still useful as the evidence the orchestrator logs that the review ran diverse (now consumed directly, not forwarded).
- The **model self-report + family match** — cheap, still fails safe.
- The Artifact Contract, resume table, stops, and the user-facing invocation — all unchanged.

## The honest tradeoff

Flatten pulls each fan-out step's *controller* context into the orchestrator (the review's group loop; SDD's task loop) — it can't be pushed into a sub-controller, since a sub-controller couldn't spawn. This is the context-pollution flatten is known for. Bounded by: (1) `adversarial-review` and SDD return **summaries + file handoffs**, not raw material; (2) it **degrades to a resume**, since resume keys off committed artifacts, not orchestrator memory. It is unavoidable without nesting, and is the harness's own recommended shape. (1.1.0's promised thin orchestrator was only ever real on the now-gone nested path.)

## Edits this implies

- **`dev-flow/SKILL.md`** — delete the `## Capability gate` section; delete the dispatch-preamble "a stage never performs an adversarial review itself…" clause and the "forward the provenance line" / "pass working-dir" instructions *as stage duties*, relocating "pass the worktree `working-dir`" to the orchestrator's own review invocations; delete the Cross-Cutting "Review provenance is checked" orchestrator-halt bullet (keep a one-line note that the orchestrator logs the review's provenance); rewrite Stages 1/2/4 so the **orchestrator** invokes `adversarial-review` after the produce step; rewrite Stage 3 so the **orchestrator** invokes SDD directly; rewrite the Environment Assumptions nesting bullet to the flat invariant; update the Pipeline preamble (produce-subagent for produce work; fan-out is orchestrator-run).
- **`adversarial-review/SKILL.md`** — keep the working-dir/`git -C` rule and provenance. Soften "Review integrity (never inline)" to reflect that it is invoked from a spawn-capable context (the orchestrator): reviewers spawn on their models; if a required model is unavailable, halt — but the no-`Agent` case no longer arises for its caller.
- **`docs/superpowers/specs/2026-07-20-dev-flow-design.md`** + **`plans/2026-07-20-dev-flow-plan.md`** — sync topology notes.
- **`plugins/dev-flow/.claude-plugin/plugin.json`** — bump `version` to **1.2.0** (architecture change; the version-keyed cache needs it to re-sync).
- **Not modified:** `subagent-driven-development` (superpowers dependency) — invoked at one level from the orchestrator, which works.

## Smoke test

On a fresh 2.1.218 session, run dev-flow on a small change with stops `[post-design, pre-merge]`. Confirm: (1) it does **not** halt at intake (no capability gate); (2) the design review spawned separate `sonnet` seed + `fable` resolver subagents **from the orchestrator**, and the design committed on `dev-flow/<slug>`; (3) resume proceeds through Plan into Execute, and Execute's SDD dispatches implementer/reviewer subagents; (4) Stage 4's diff-review fixers commit in the worktree via `git -C`; (5) it halts at `pre-merge`.
