# dev-flow — Guarantee the Model-Diverse Review (never silently inline)

> **Superseded 2026-07-22 by `2026-07-22-dev-flow-flatten-design.md`** — nested subagent spawning was removed in Claude Code 2.1.218, so dev-flow 1.2.0 flattened to orchestrator-driven fan-out. This nested design is retained for history.

**Date:** 2026-07-22
**Status:** Approved for planning
**Supersedes:** the flatten draft `2026-07-22-dev-flow-flat-fanout-design.md` (deleted in commit `efe5477`; see git history). That draft flattened all fan-out to the orchestrator on the premise that *subagents cannot spawn subagents*. We empirically disproved that premise (see Evidence), so this design keeps the nested architecture and fixes the actual defect instead.

## Goal

Ensure dev-flow's per-stage adversarial review always runs its model-diverse reviewer subagents (sonnet seeds / fable resolvers — opus resolvers when the session model is Fable-family, per adversarial-review's Model section) — or **halts loudly** — instead of silently degrading to a single-model inline review, the regression observed in a real run.

## Problem and root cause

Observed in a real run: the review *"ran inline on the main model rather than as separate fable reviewer subagents — the stage subagent's context didn't expose an agent-spawning tool,"* and it produced a single-model review with no error. Two distinct defects:

1. **Under-specified spawn.** dev-flow's "spawn a stage subagent" did not guarantee the subagent carried the `Agent` + `Skill` tools the nested review requires.
2. **Silent degradation.** When the review couldn't spawn its model-diverse reviewers, it fell back to an inline single-model review with no signal — the worst outcome, invisibly. The model diversity that `e987265` deliberately added was lost silently.

## Evidence (why we keep nesting)

Empirical probes on **Claude Code 2.1.217**:

- A `general-purpose` subagent spawned from the main session holds **both** `Agent` and `Skill`.
- From inside that subagent, spawning a **`sonnet`** sub-subagent and a **`fable`** sub-subagent both succeeded (each returned its token). No depth limit, tool restriction, or recursion block.

So the nested, model-diverse review **works when the stage subagent is spawned correctly**. The architecture was sound; the spawn grant and the failure mode were the bugs. The original failure was environmental — an older version at run time, or a stage subagent spawned as a restricted type — not an architectural impossibility.

**Probed — `EnterWorktree` unavailable at depth-2 (2026-07-22).** The load-bearing question was whether `EnterWorktree(path)` is accepted from a depth-2 cwd-pinned agent (main → stage subagent → fixer). It is **not**. Probed live: `EnterWorktree` failed at both the intermediate and fixer levels with *"the current working directory … is the repository root, not an isolated worktree — switching is only available to sessions whose working directory is inside a worktree."* dev-flow's subagents are pinned at the repo root, so `EnterWorktree` is unavailable to them — its documented "works from pinned agents" contract does not hold here, exactly the doc-vs-runtime drift this design's empirical-verification method guards against. The probe also showed the hazard directly: a fixer running bare `git commit` (no `git -C`) committed to the *session's* branch, not the worktree — the ambient-cwd footgun the working-dir rule prevents. **Consequence:** write-side fixers address the worktree with `git -C <path>` and absolute file paths **uniformly**; the `EnterWorktree` mechanism is dropped. The architecture is unaffected — only the mechanism. (`PROBE_RESULT = ENTERWORKTREE_FAILED` for the plan's Task 3.)

## Decision: keep the nested architecture; fix the grant and the failure mode

**Rejected — flattening all fan-out to the orchestrator.** Flattening was correct *only* under the false "can't nest" premise. With nesting confirmed, it over-corrects: it pulls every stage's coordination state into the orchestrator's context — the context pollution that Anthropic's multi-agent guidance and the actor/OTP "error-kernel" tradition both warn against, and which is sharpest for a *multi-stage* pipeline like ours (each stage is its own fan-out). It also trades the thin, durable orchestrator (the error-kernel ideal: fragile work at ephemeral leaves, a stable coordinator up top) for a heavier one, to work around a capability that exists. Per the design rubric — *a fix must be worth its complexity; if the fix is worse than the wart, leave it* — the proportional fix keeps the thin orchestrator.

Sources consulted: [Anthropic — Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents); [Anthropic — multi-agent research system](https://www.anthropic.com/engineering/built-multi-agent-research-system) and [when to use multi-agent systems](https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them) (context-pollution rationale); [Akka Actor Systems / error kernel](https://doc.akka.io/libraries/akka-core/2.4/general/actor-systems.html) and [Adopting Erlang — supervision trees](https://adoptingerlang.org/docs/development/supervision_trees/).

## The fixes — a layered "never silently inline" guarantee

The guarantee is not one clause but a small set of one-sentence layers, each landing at a **shared boundary** that survives a distinct failure mode. None is speculative — each closes a failure path the analysis names concretely.

**Fix 1 — Grant the tools at the dispatch seam (correct-by-default).** dev-flow spawns every stage subagent as `general-purpose` — the type verified to carry `Agent` + `Skill`. This lands in the **one sentence that already governs every stage dispatch**: the Pipeline preamble (dev-flow `SKILL.md` ~`:125`, "Each stage runs in a fresh subagent…"), amended to name the type. It is the *operative dispatch instruction*; Environment Assumptions carries only the rationale and the verified version. Stated once, inherited by every current and future stage — never restated per stage.

**Fix 2 — Never inline; halt loudly, on *every* path (dual-homed).** The grant (Fix 1) and a halt clause in the review skill's contract share a joint failure mode: a stage subagent spawned as a restricted type has no `Skill` tool, so `adversarial-review`'s contract never enters its context, and it improvises an inline review from the dispatch prompt — the exact regression, on the path the contract clause cannot reach. So the guarantee is dual-homed:
- **In `adversarial-review`'s Contract:** the seed and resolver passes MUST run as separate subagents on their specified models; if they cannot be spawned, halt and report — never produce a single-model inline review as a silent substitute. (Protects every caller who loads the skill, including standalone use.)
- **In dev-flow's dispatch-prompt preamble** (the "Dispatching to Inherited Skills" blockquote ~`:51`, carried verbatim in every dispatch — the one channel that reaches the stage subagent *regardless of its toolset*): *"A stage never performs an adversarial review itself. If the `Skill` tool cannot load `dev-flow:adversarial-review`, or the `Agent` tool is unavailable for its reviewers, halt and report the missing capability. An inline single-model review is a contract violation, never a fallback."*

Both homes are load-bearing; a future editor must not "deduplicate" one away.

**Fix 3 — Positive evidence: model self-report + provenance, checked by the orchestrator.** Behavioral detection ("if it can't spawn, halt") is invisible when it *doesn't* halt — nobody can tell a real model-diverse review from a degraded one. Add positive evidence:
- Every reviewer prompt (seeds and resolvers) requires the reviewer to state, as the first line of its report, the model its own system prompt names. The review verifies each self-report against the model requested for that tier per adversarial-review's **Model section** (family match — "Fable 5" satisfies `fable`; the *requested* model, so the opus-fallback for resolvers is honored, not hardcoded). A mismatch or missing line is treated exactly like a failed spawn — halt. (This also closes silent model substitution, and fails safe: if the harness ever stops naming the model, the line goes missing and the review halts rather than passing.)
- `adversarial-review`'s report-back (contract step 6) gains a **provenance** field: reviewers spawned per tier with their self-reported models (e.g. "seeds: 2× sonnet; resolvers: 3× fable"). For any stage that ran a review (Stages 1, 2, 4 — not Execute), the stage summary returned to the orchestrator carries that provenance line, and **the orchestrator halts if it is missing or violates the Model policy.** The orchestrator is the only observer living *outside* the potentially-degraded stage context, which is what makes this check trustworthy.

**Fix 4 — A mandatory intake capability probe (replaces the "version floor").** A version number cannot be the enforceable seam: the grant is lost version-*independently* (restricted spawn type, permission settings, `allowedTools`), so a version check (or `claude --version` parsing) tests the wrong axis. The enforceable seam is a capability probe, and it is **required, not optional**:

> At intake of **every** invocation — first run and resume alike, before any drafting or stage dispatch — dev-flow spawns one `general-purpose` subagent that (a) confirms it holds `Agent` + `Skill`, and (b) spawns one sub-subagent on the seed model and one on the resolver model, each returning its self-reported model identity. Any failure or mismatch halts with a report naming the missing capability, citing the verified version (2.1.217) as a diagnostic hint.

This lands as a short **"Capability gate"** step at intake (before Stage 1 / the resume-table dispatch). Rationale: the probe is ~2 agent round-trips (the Evidence probe, mechanized); leaving it optional collides with the resume table — a floor violation surfacing at the first review discards an entire uncommitted draft (bare-idea entry re-lands at "Design (redo; uncommitted drafts discarded)"). It is uniform per-invocation *by design* — conditional probing ("only when a review will run") is a remember-which-rows rule the rubric forbids, and per-invocation covers cross-session environment drift (resume is a new invocation). One probe tests the whole chain: grant → nesting → model identity.

## Explicit working-dir (worktree seam)

The nested stage subagent enters the pipeline worktree via the existing worktree-entry procedure. Its spawned reviewers must not rely on inherited or ambient cwd (process cwd is global mutable state — a concurrency footgun when parallel fixers run). The correct-by-default rule, landing in **`adversarial-review`'s Contract**:

1. The review **resolves its working directory exactly once** at invocation: the explicit `working-dir` argument if given, else the invoking checkout root (`git rev-parse --show-toplevel`), always normalized to an absolute path. Resolution failure (not a git repo) is a loud halt at the door — the contract requires committing, so it fails at invocation, not at commit time.
2. That absolute path is threaded **unconditionally into every spawned agent's prompt** — seeds, resolvers, and fixers. No spawned agent derives its location from inherited cwd.
3. **Read-only** reviewers (seeds, resolvers) receive absolute artifact/diff paths derived from the resolved root and need no entry. **Write-side** fixers address the root explicitly with `git -C <path>` and absolute file paths — **uniformly**, in both the dev-flow and standalone cases. (`EnterWorktree` is not used: the probe found it unavailable to dev-flow's repo-root-pinned subagents — see Evidence — and it rejects non-`.claude/worktrees/` targets anyway, so explicit `git -C` addressing is the one rule that works everywhere. This is why the working-dir must be *threaded*, never inherited.)
4. The caller's `working-dir` argument is **merely an override** — omission cannot produce ambient-cwd behavior, so it is impossible to get wrong by omission. dev-flow's stage subagent passes the worktree path explicitly (zero coupling to its own entry state); standalone omission resolves to the current checkout, so standalone use is unchanged *in effect*.

Grounding: [PEP 20 "explicit is better than implicit"](https://peps.python.org/pep-0020/); [zero ambient authority for AI agents](https://grith.ai/blog/zero-ambient-authority-ai-agents).

## What this does NOT change

- **The nested topology** (orchestrator → stage subagent → review reviewers) — preserved; the orchestrator stays thin.
- **Stage 3 (Execute).** Structurally unchanged: the execute-stage subagent runs `subagent-driven-development` nested, and SDD spawns its implementer/reviewer subagents (proven to work). We only ensure the execute-stage subagent carries `Agent` + `Skill` (Fix 1's grant covers it). **SDD is a `superpowers` dependency and is not modified.** `writing-plans` and (inlined) `brainstorming` are single-agent produce activities — also unchanged.
- The review's two-tier seed/resolver protocol and its sonnet/fable(/opus) model policy, the Artifact Contract, resume table, and stops. (Fix 3's self-report *enforces* the existing Model policy; it does not alter it.)

## Edits this implies

- **`dev-flow/SKILL.md`** —
  - (a) **Pipeline preamble ~`:125`**: name the spawn type — "…a fresh `general-purpose` subagent (the type carrying `Agent` + `Skill`, required for the nested review)…" (Fix 1).
  - (b) **Dispatch-prompt preamble blockquote ~`:51`**: add the "a stage never reviews itself; halt on missing `Skill`/`Agent`; inline review is a contract violation" clause (Fix 2, second home).
  - (c) **New "Capability gate" step at intake** (before Stage 1 / resume-table dispatch): the mandatory probe (Fix 4).
  - (d) **Provenance requirement**: stages that ran a review carry the provenance line in their stage summary; the orchestrator halts on missing/violating provenance (Fix 3).
  - (e) **Environment Assumptions ~`:185`**: delete the "run the seed and group agents from the main session" fallback — from a stage subagent it is unreachable (the entity that detects the missing tool cannot execute a main-session fallback), and its orchestrator-proactive form *is* the flatten design we rejected. Replace with: nested spawn is required; the intake probe enforces it; verified on 2.1.217 (documentation, not enforcement); mid-run degradation is caught by (b) and (d).
- **`adversarial-review/SKILL.md`** — add to the **Contract**: (i) reviewer passes run as separate subagents on their models, halt if unspawnable, never inline (Fix 2, first home); (ii) reviewer model self-report + verification, and the provenance field in report-back (Fix 3); (iii) the working-dir rule — resolve once (arg, else invoking checkout root, absolute), thread to every spawned agent, write-side addresses the root via `git -C` uniformly (the probe found `EnterWorktree` unavailable — see Evidence), argument is an override not the mechanism (Worktree seam). Leave the two-tier protocol and model policy otherwise untouched.
- **`docs/superpowers/specs/2026-07-20-dev-flow-design.md`** and **`docs/superpowers/plans/2026-07-20-dev-flow-plan.md`** — sync these notes (the repo keeps spec, plan, and skill in lockstep).
- **Not modified:** `subagent-driven-development` (superpowers dependency).

## Rejected as not worth their complexity

- **Harness-level enforcement** (PreToolUse hooks validating `Agent` calls, transcript-JSONL model auditing) — couples the plugin to harness internals, breaks portability, heavy relative to prompt-level layers plus a probe. A determined-to-confabulate model could fake a provenance line, but that wart is unfixable at any prompt level; the observed regression was *accidental* degradation, which every layer here targets.
- **Inlining `adversarial-review`'s text into every dispatch prompt** (to make `Skill`-lessness harmless) — forks the source of truth and bloats every dispatch; the one-line preamble clause (Fix 2b) gets the same protection.
- **Committing drafts before review** (to make a mid-run probe failure non-destructive) — breaks the Artifact Contract's "committed at tip ⇔ stage complete" invariant to save a case the intake probe already prevents.
- **Re-probing before every stage** within one invocation — mid-invocation environment drift is the super-rare case; intake-per-invocation covers the real (cross-session) drift.
- **Provenance beyond model names** (tokens, transcript excerpts) — count-per-tier plus self-reported model is sufficient evidence; more is ceremony.

## Smoke test

Run dev-flow on a small change with recorded stops `[post-design, pre-merge]` (stamped in front-matter at intake — this also smoke-tests stop persistence and precedence). Confirm:

1. The stage summary's **provenance line names separate `sonnet` seeds and `fable` resolvers** (opus resolvers if the session is Fable-family), and the review committed on `dev-flow/<slug>` with `dev-flow` front-matter intact — the exact behavior that regressed, now checkable on every run rather than by manual inspection.
2. `continue dev-flow on <slug>` proceeds through Plan into Execute; Execute dispatches SDD implementers/reviewers as **separate subagents**.
3. The continuation proceeds through Stage 4: the diff-mode review runs and its **write-side fixers operate in the pipeline worktree** — at least one fixer entered via `EnterWorktree(path)` (or `git -C`, per the Evidence probe outcome) and its fix commit landed on `dev-flow/<slug>`; the `review clean` marker posted at head. If the organic diff review yields no findings, seed one caller-supplied finding so at least one fixer actually runs — an empty review verifies nothing.
4. The run **halts at the recorded `pre-merge` stop — the smoke run never merges.** Teardown: `gh pr close`, then Stage 5's cleanup block (worktree remove, branch delete), leaving no residue.
5. **The loud path:** invoked from a subagent type without the `Agent` tool (e.g. a probe dispatched into a restricted context), the intake capability gate — or the dispatch-preamble clause — **halts with a clear message** rather than producing a single-model review.
