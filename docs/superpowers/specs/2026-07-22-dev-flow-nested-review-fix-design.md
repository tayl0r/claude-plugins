# dev-flow — Guarantee the Model-Diverse Review (never silently inline)

**Date:** 2026-07-22
**Status:** Approved for planning
**Supersedes:** `2026-07-22-dev-flow-flat-fanout-design.md`. That draft flattened all fan-out to the orchestrator on the premise that *subagents cannot spawn subagents*. We empirically disproved that premise (see Evidence), so this design keeps the nested architecture and fixes the actual defect instead.

## Goal

Ensure dev-flow's per-stage adversarial review always runs its model-diverse reviewer subagents (sonnet seeds / fable resolvers) — or **halts loudly** — instead of silently degrading to a single-model inline review, which is the regression observed in a real run.

## Problem and root cause

Observed in a real run: the review *"ran inline on the main model rather than as separate fable reviewer subagents — the stage subagent's context didn't expose an agent-spawning tool,"* and it produced a single-model review with no error. Two distinct defects:

1. **Under-specified spawn.** dev-flow's "spawn a stage subagent" did not guarantee the subagent carried the `Agent` + `Skill` tools the nested review requires.
2. **Silent degradation.** When the review couldn't spawn its model-diverse reviewers, it fell back to an inline single-model review with no signal — the worst outcome, invisibly. The model diversity that `e987265` deliberately added was lost silently.

## Evidence (why we keep nesting)

Empirical probes on **Claude Code 2.1.217**:

- A `general-purpose` subagent spawned from the main session holds **both** `Agent` and `Skill`.
- From inside that subagent, spawning a **`sonnet`** sub-subagent and a **`fable`** sub-subagent both succeeded (returned their tokens). No depth limit, tool restriction, or recursion block.

So the nested, model-diverse review **works when the stage subagent is spawned correctly**. The architecture was sound; the spawn grant and the failure mode were the bugs. The original failure was environmental — an older version at run time, or a stage subagent spawned as a restricted type — not an architectural impossibility.

## Decision: keep the nested architecture; fix the grant and the failure mode

**Rejected — flattening all fan-out to the orchestrator.** Flattening was correct *only* under the false "can't nest" premise. With nesting confirmed, it over-corrects: it pulls every stage's coordination state into the orchestrator's context — the context pollution that Anthropic's multi-agent guidance and the actor/OTP "error-kernel" tradition both warn against, and which is sharpest for a *multi-stage* pipeline like ours (each stage is its own fan-out). It also trades the thin, durable orchestrator (the error-kernel ideal: fragile work at ephemeral leaves, stable coordinator up top) for a heavier one, to work around a capability that exists. Per the design rubric — *a fix must be worth its complexity; if the fix is worse than the wart, leave it* — the proportional fix keeps the thin orchestrator.

Sources consulted: [Anthropic — Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) (simplicity default; extra abstraction layers are a named cost); [Anthropic — multi-agent research system](https://www.anthropic.com/engineering/built-multi-agent-research-system) and [when to use multi-agent systems](https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them) (context pollution rationale); [Akka Actor Systems / error kernel](https://doc.akka.io/libraries/akka-core/2.4/general/actor-systems.html) and [Adopting Erlang — supervision trees](https://adoptingerlang.org/docs/development/supervision_trees/) (thin root; fragile work pushed to leaves; guardian as single point of contention).

## The fixes

1. **Guarantee the spawn grant (correct-by-default).** dev-flow spawns every stage subagent as a type that carries both `Agent` and `Skill` (empirically `general-purpose`). Stated once as a pipeline requirement so every current and future stage inherits it — no per-stage flag to remember.

2. **Never silently inline — halt loudly.** This is the core defect fix, and it lives in the **`adversarial-review` skill's contract** so it protects every caller (dev-flow and standalone). The seed and resolver passes MUST run as separate subagents on their specified models (sonnet seeds, fable resolvers — different from the artifact's author). If the review cannot spawn them — no `Agent` tool, or a required model unavailable — it **halts and reports**; it must never produce a single-model inline review as a silent substitute. A single-model review is not an acceptable degradation of an adversarial review and must never be produced without an explicit, loud stop.

3. **Documented version floor.** dev-flow requires a Claude Code version whose spawned subagents receive `Agent` + `Skill` (verified on 2.1.217). On an unsupported version, fix 2 fires: a clear halt naming the required capability, never a silent single-model review. dev-flow may perform a one-time capability probe at intake to fail fast (before any drafting) rather than at the first review; the mechanism is left to the plan, but the *loud-never-silent* property is required either way. (The user accepted a version floor in exchange for the thinner, more idiomatic nested design over universal-but-heavier flattening.)

## Explicit working-dir (worktree seam) — unchanged, still explicit

The nested stage subagent already enters the pipeline worktree via the existing worktree-entry procedure. Its spawned **write-side** reviewers (fixers / commit) must not rely on inherited or ambient cwd: subagents are cwd-pinned at launch, and process cwd is global mutable state — a concurrency footgun when parallel reviewers run. The stage subagent passes the worktree path explicitly; write-side reviewers `EnterWorktree(path)` (accepted from a pinned subagent because the worktree lives under `.claude/worktrees/`); **read-only** reviewers (seeds, resolvers) read the artifact or diff by absolute path and need no entry. `adversarial-review` gains an optional working-dir argument — absent → current checkout, so standalone use is unchanged. Grounding: [PEP 20 "explicit is better than implicit"](https://peps.python.org/pep-0020/); [zero ambient authority for AI agents](https://grith.ai/blog/zero-ambient-authority-ai-agents).

## What this does NOT change

- **The nested topology** (orchestrator → stage subagent → review reviewers) — preserved; the orchestrator stays thin.
- **Stage 3 (Execute).** Structurally unchanged: the execute-stage subagent runs `subagent-driven-development` nested, and SDD spawns its implementer/reviewer subagents (proven to work). We only ensure the execute-stage subagent carries `Agent` + `Skill`. **SDD is a `superpowers` dependency and is not modified.** `writing-plans` and (inlined) `brainstorming` are single-agent produce activities — also unchanged.
- The review's two-tier seed/resolver protocol and its sonnet/fable model policy, the Artifact Contract, resume table, and stops.

## Edits this implies

- **`dev-flow/SKILL.md`** — (a) state the spawn-grant requirement (stage subagents are spawned as a type carrying `Agent` + `Skill`, e.g. `general-purpose`); (b) rewrite the Environment Assumptions "Subagent nesting" note (`:185`): delete the unreachable "run the seed and group agents from the main session" fallback and replace it with the loud-halt contract + documented version floor; (c) note the explicit worktree-path passing to write-side reviewers.
- **`adversarial-review/SKILL.md`** — add the "reviewer passes run as separate subagents on their models; halt loudly if they can't spawn; never inline a single-model review" contract clause; add the optional working-dir argument with the read-by-absolute-path / write-side-enters split. Leave the two-tier protocol and sonnet/fable policy untouched.
- **`docs/superpowers/specs/2026-07-20-dev-flow-design.md`** and **`docs/superpowers/plans/2026-07-20-dev-flow-plan.md`** — sync these notes (the repo keeps spec, plan, and skill in lockstep).
- **Not modified:** `subagent-driven-development` (superpowers dependency).

## Smoke test

Run dev-flow on a small change and stop at `post-design`. Confirm:

1. The review spawned **separate `sonnet` seed and `fable` resolver subagents** — verified from the run, not merely that a review happened (this is the exact behavior that regressed).
2. The design committed on `dev-flow/<slug>` with its `dev-flow` front-matter intact.
3. `continue dev-flow on <slug>` proceeds through Plan into Execute, and Execute dispatches SDD implementers/reviewers as **separate subagents**.
4. The loud path: under a simulated no-spawn condition, the review **halts with a clear message** rather than producing a single-model review.
