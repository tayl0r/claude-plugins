# dev-flow — Flatten to Orchestrator-Driven Fan-Out

**Date:** 2026-07-22
**Status:** Approved for planning
**Supersedes (architecture):** `2026-07-22-dev-flow-nested-review-fix-design.md` and its plan `2026-07-22-dev-flow-nested-review-fix.md`. Those kept a *nested* topology (stage subagent → seed/resolver reviewers) guarded by a capability gate. **Nested subagent spawning was removed in Claude Code 2.1.218** (see Root cause), so the nested topology cannot run. This design flattens: the orchestrator drives all fan-out; no subagent ever spawns a subagent. Those two superseded docs get a one-line "superseded by flatten" banner (see Edits).

## Goal

Make `dev-flow` run its model-diverse adversarial review (sonnet seeds / fable resolvers) and its subagent-driven Execute stage on **any** Claude Code version — without relying on nested subagent spawning, which the harness no longer grants. Preserve model diversity; never silently degrade.

## Root cause (why the nested design broke)

`dev-flow` 1.1.0's per-stage review runs *nested*: the orchestrator spawns a stage subagent, which invokes `adversarial-review`, which spawns seed + resolver sub-subagents on diverse models. That requires a spawned subagent to itself hold the `Agent` tool (2-level spawning).

**Claude Code 2.1.218 does not grant spawned subagents the `Agent` tool.** Confirmed:
- A session freshly launched under 2.1.218 (real user repro, twice, incl. after `/reload-plugins`): a spawned `general-purpose` subagent has `Skill` but **not** `Agent`; `ToolSearch select:Agent` from inside it returns "No matching deferred tools found".
- Why 1.1.0 development missed it: that session was a **lingering 2.1.217 process** (nesting still worked in-process) while the on-disk binary had already updated to 2.1.218. The verification was real for 2.1.217 and stale for 2.1.218.
- Harness direction (release notes + open issue #60763): nested spawning is **off by default** (env-var-gated at most) and subagents lacking `Agent` is "by design". Recommended pattern: **top-level orchestration only** — workers don't spawn.

So the "nesting is available" premise is false on current and future versions. 1.1.0's capability gate correctly refuses to run (loud halt) — but that means the pipeline can't run at all. The fix is to stop depending on nesting.

## Decision: flatten (orchestrator drives all fan-out)

**Invariant:** *`dev-flow` spawns only leaf subagents. The orchestrator (main session) is the only spawner — it always holds `Agent`, on every version. Any delegated skill that itself fans out into subagents (`adversarial-review`, `subagent-driven-development`) is invoked by the orchestrator directly, in-context — never nested inside a stage subagent.*

This is the harness's recommended pattern and Anthropic's shipped multi-agent shape (a lead + leaf workers). Rejected: an env-var stopgap (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`) — a per-machine flag the harness defaults off and discourages. Rejected: a hybrid keeping a nested fast-path — pure speculation now that nesting is off-by-default; it re-adds the complexity flatten removes for no reliable benefit.

## The orchestrator owns the worktree, end-to-end

This is the load-bearing consequence of flatten and the source of its subtlety. In 1.1.0 each stage ran in a subagent that first entered the worktree, so all stage work (produce, review commits, SDD, suites) happened inside `dev-flow/<slug>`'s tree by construction. Flatten deletes those stage subagents, so **the orchestrator must own the worktree lifecycle and operate within it** — otherwise in-context work silently runs against the main checkout's default-branch tree.

Rules (they replace 1.1.0's per-stage-dispatch entry and its "the orchestrator stays in the main checkout" line):

1. **Resolve once.** The orchestrator resolves the pipeline worktree path once per invocation (`git worktree list --porcelain`, the entry for `refs/heads/dev-flow/<slug>`).
2. **Create / re-attach / (Stage 1) create-first-act, dep-install, dirty-resume stash** — all the worktree-lifecycle steps 1.1.0 assigned to "every stage dispatch" are now performed by the orchestrator at each stage boundary. Stage-5 cleanup already belongs to the orchestrator.
3. **Route from main, drive from the worktree.** The orchestrator does its *resume-table routing* from the main checkout (reads via `git show dev-flow/<slug>:<file>`, branch listings, `gh` — no worktree needed). To *drive* a stage's in-context work (an `adversarial-review` invocation, the Execute SDD loop), it `cd`s into the worktree for the duration, so in-context git and scripts (SDD's baseline + per-task suites and `HEAD`-relative commands, `adversarial-review`'s post-fix suite) run against the correct tree. The `review clean` marker therefore certifies a suite run in the pipeline tree, not the default branch.
4. **Thread the absolute path to every leaf.** Spawned agents are pinned to the repo root and cannot inherit cwd:
   - `adversarial-review` is passed the worktree path as `working-dir`; its write-side fixers use `git -C <path>` + absolute file paths (the depth-2 `EnterWorktree` probe found harness entry unavailable — already implemented in the review skill).
   - SDD's implementer/reviewer/fix dispatches get the worktree path in their `Work from:` field, and each such agent `cd`s there (or uses `git -C`) before writing/committing — never a bare `git commit`, which the probe showed lands on the main checkout's branch.
5. **SDD's `using-git-worktrees` stays safe by construction** — but now because the *orchestrator* is inside the worktree when it invokes SDD in-context, so SDD's Step-0 isolation check finds the pipeline worktree and creates nothing (in 1.1.0 it was the stage subagent that provided this; the guarantee moves to the orchestrator).
6. **Execute bookkeeping** (ticking plan checkboxes and committing them — the durable resume key) was 1.1.0's "execute-stage wrapper"; it is now the orchestrator, which is SDD's controller.

## The design

### Topology

```
orchestrator (main session — always holds Agent; owns & enters the worktree)
  ├─ produce-subagent (leaf) → writes a draft into the worktree (abs path), returns a summary
  └─ invoke fan-out skill IN-CONTEXT (adversarial-review / SDD), cwd = worktree
       ├─ seed:sonnet ×2      (leaf)
       ├─ resolver:fable ×N   (leaf)
       └─ fixer:main ×N       (leaf, `git -C <worktree>`)
Every subagent is a LEAF. No subagent spawns a subagent.
```

### Per-stage

| Stage | Flat flow (vehicle explicit) |
|---|---|
| **1 Design** | Bare-idea: draft in a **produce-subagent** (keeps exploratory reads out of the orchestrator). Adopt-file: the orchestrator copies+stamps inline (trivial). Then the **orchestrator** invokes `adversarial-review` (mode `design`) in-context, cwd = worktree. |
| **2 Plan** | Draft via `writing-plans` in a **produce-subagent**. Then the **orchestrator** invokes `adversarial-review` (mode `plan`) in-context. |
| **3 Execute** | The **orchestrator** (cwd = worktree) invokes `subagent-driven-development` directly — it *is* SDD's controller and spawns implementer/reviewer subagents itself (one level — always works). No execute-stage-subagent wrapper. The orchestrator **self-applies** SDD's dev-flow overrides (baseline, suppressed terminal review, pre-answers, halts, checkbox bookkeeping) — those were carried in the old dispatch preamble, which no longer exists for an in-context invocation. |
| **4 PR** | `gh pr create` (orchestrator), then the **orchestrator** invokes `adversarial-review` (mode `diff`) in-context, cwd = worktree. |
| **5 Merge** | **Inline in the orchestrator** — `gh` + `git` only, no spawning. |

Produce-subagents (Stages 1–2) are true leaves needing only `Skill` (retained on 2.1.218) and file writes by absolute path; they never spawn.

### Model diversity + fail-safes (kept, not over-removed)

- The orchestrator spawns sonnet seeds and fable resolvers directly (one level — works on 2.1.218). The construction guarantees the *capability*; the fail-safes below guarantee *compliance*.
- **Keep `adversarial-review`'s "Review integrity (never inline)" clause verbatim.** It still protects standalone and any-other-caller use (a main session can also lack `Agent` via `allowedTools`/permissions — "the orchestrator always holds Agent" is the common case, not a law). At most add a parenthetical that dev-flow's orchestrator invocation normally satisfies it trivially.
- **Keep provenance as an orchestrator self-check.** After each in-context review the orchestrator reads the review's provenance line (`seeds: N× <tier>; resolvers: M× <tier>`) and halts if it is missing or its tiers violate the Model section. This is self-attestation (weaker than 1.1.0's external observer) but nearly free and still catches a review that failed to spawn diverse reviewers. Only the *forwarding through a stage summary* is obsolete.
- **Slim intake gate (model availability, not nesting).** Before drafting, the orchestrator spawns **one** `sonnet` leaf and **one** `fable` leaf (one level — no nesting) and family-matches their self-reported models; halt if either can't spawn or reports the wrong tier. This preserves the old gate's model-availability + fail-fast-before-drafting value (a bare-idea draft discarded on a late halt is the cost the gate's own rationale cited) while dropping the obsolete nesting probe.

## What this REMOVES vs 1.1.0

- **The nesting probe inside the Capability gate** (the 2-level sub-subagent spawn) — obsolete. (The gate itself survives in slimmed, one-level form; see above.)
- **The dispatch-preamble "a stage never performs an adversarial review itself / halt on missing Skill/Agent" clause, and the "forward the provenance line / pass working-dir" *stage duties*** — stages no longer invoke the review; the orchestrator does, and owns the worktree path directly. (A one-line "halt if a produce-subagent can't load its `Skill`-delegated skill" is retained in the produce-dispatch preamble.)
- **Provenance forwarding + the Cross-Cutting "orchestrator halts on missing forwarded provenance" bullet** — replaced by the in-context self-check above.

## Edits this implies

- **`dev-flow/SKILL.md`:**
  - Intro (`:8`) "Each stage runs in a fresh subagent so this orchestrator's context stays thin" → reword to the flat model (orchestrator drives fan-out; context tradeoff is real).
  - Model Policy (`:45`) "Everything this skill spawns directly … runs on the main session model" → the orchestrator now *directly* spawns sonnet seeds / fable resolvers; reviewer-model selection stays owned by `adversarial-review`.
  - Dispatching to Inherited Skills (`:58` intro + blockquote `:60` + gate clause): the preamble now targets **produce-subagents only**; delete the "a stage never performs an adversarial review itself" clause; retain the "never talk to the user" (a)/(b)/(c) rule for produce-subagents; the orchestrator self-applies delegated-skill overrides for in-context invocations.
  - Replace the `## Capability gate` section with the slim one-level model-availability gate.
  - Artifact Contract: add the "orchestrator owns & enters the worktree" rules; rewrite the worktree-entry step 4 (`:108`, "the orchestrator itself stays in the main checkout") to "routes from main, `cd`s into the worktree to drive in-context fan-out"; reassign the execute-stage checkbox bookkeeping (`:165`) and lifecycle steps to the orchestrator; update the `using-git-worktrees` "safe by construction" corollary (`:68`).
  - Rewrite Pipeline preamble + Stages 1–5 to the per-stage table above.
  - Cross-Cutting "Context hygiene: every stage and every review group runs in a fresh subagent" (`:201`) → true only for leaf spawns; reword. Replace the "Review provenance is checked" forwarded-halt bullet with the in-context self-check.
  - Environment Assumptions nesting bullet → the flat invariant.
- **`adversarial-review/SKILL.md`:** keep the `git -C` working-dir rule and provenance. Reword report-back line (`:69`) "evidence a caller checks" → "evidence the invoking orchestrator checks directly". Fix the dangling Invocation bullet (`:12`) "see dev-flow's stage-dispatch preamble" → point at dev-flow's orchestrator worktree rule. Leave "Review integrity (never inline)" verbatim (optionally a trivially-satisfied parenthetical).
- **`docs/superpowers/specs/2026-07-20-dev-flow-design.md`** + **`plans/2026-07-20-dev-flow-plan.md`** — sync the nesting/topology passages to flat; add the header pointer.
- **`docs/superpowers/specs/2026-07-22-dev-flow-nested-review-fix-design.md`** + **`plans/2026-07-22-dev-flow-nested-review-fix.md`** — add a top banner: "> Superseded 2026-07-22 by `2026-07-22-dev-flow-flatten-design.md` (nesting removed in Claude Code 2.1.218)."
- **`plugins/dev-flow/.claude-plugin/plugin.json`** — bump `version` 1.1.0 → **1.2.0**.
- **Not modified:** `subagent-driven-development` (superpowers dependency) — invoked at one level from the orchestrator; it receives the worktree path via `Work from:`.

## What does NOT change

The user-facing invocation, stops, the resume table's *decisions* (still mechanical reads of branch/PR), and `adversarial-review`'s two-tier seed/resolver protocol and sonnet/fable model policy.

## The honest tradeoff

Flatten pulls each fan-out step's *controller* context into the orchestrator (the review's group loop; SDD's task loop) — unavoidable, since a sub-controller couldn't spawn. Bounded by: `adversarial-review` and SDD return summaries + file handoffs, not raw material; and it **degrades to a resume** (resume keys off committed artifacts — the plan checkboxes the orchestrator now commits — not orchestrator memory). It is the harness's own recommended shape.

## Smoke test

On a **fresh 2.1.218 session**, run dev-flow on a small change with stops `[post-design, pre-merge]`. Confirm: (1) it does **not** halt (no nesting gate); the slim model gate passes. (2) The design review spawned separate `sonnet` seed + `fable` resolver subagents **from the orchestrator**, its provenance self-check passed, and the design committed on `dev-flow/<slug>`. (3) Resume proceeds through Plan into Execute; Execute's SDD dispatches implementer/reviewer subagents, and **its commits land on `dev-flow/<slug>` in the pipeline worktree, not the main checkout** (the sharpest new risk). (4) Stage 4's diff-review fixers commit in the worktree via `git -C`, and the `review clean` marker's suite ran against the pipeline tree. (5) It halts at `pre-merge`.
