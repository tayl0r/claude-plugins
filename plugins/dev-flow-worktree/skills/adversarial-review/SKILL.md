---
name: adversarial-review
description: Use to run a rigorous adversarial review on a single artifact — a design doc, a plan doc, or a PR/diff. Seeds with findings-only quality and correctness passes, then groups issues and resolves each to the best long-term design with adversarial self-checks. Triggers on "adversarial review", "review this design/plan/PR properly", or is called internally by dev-flow-worktree at each stage.
---

# Adversarial Review

Run a rigorous adversarial review on ONE target artifact and resolve every finding to the best long-term design, applying only fixes that earn their place.

**Invocation:** `adversarial-review(target, mode[, extra findings][, working-dir])` where `mode` is one of `design`, `plan`, `diff`, and `working-dir` is an optional absolute path to the checkout/worktree the review reads and commits in (see the Contract's working-directory rule; absent → the invoking checkout).
- When called by dev-flow-worktree, the mode is passed explicitly.
- When called by dev-flow-worktree, `working-dir` is the pipeline worktree's absolute path — the orchestrator passes it explicitly and invokes the review in-context (see dev-flow-worktree's worktree-entry rule).
- Standalone, infer the mode: a path under `specs/` -> `design`; under `plans/` -> `plan`; a PR number, branch, or SHA range -> `diff`.
- A caller may pass additional findings (e.g. leftovers from an earlier review); they join the seed findings in Resolution step 1.

**Contract:** this skill owns the artifact end-to-end — it reviews, resolves, applies, and **commits** the improved artifact on the working directory's branch (see Working directory, below), in every mode. The caller never re-applies or re-commits the review's work. It never pushes, posts review results to a PR, or merges — those integration steps are the caller's. (Filing a new issue via `gh`, per "Where new issues are filed," is part of the review, not integration.)

**Review integrity (never inline).** The seed and resolver passes MUST run as separate subagents on their specified models (per Model, below). If they cannot be spawned — no `Agent` tool, or a required model unavailable — halt and report; **never** produce a single-model inline review as a silent substitute. To make the model axis verifiable, every reviewer prompt (seed and resolver) requires the reviewer to state, as the first line of its report, the model its own system prompt names. The review matches each self-report to the tier requested for it — a **family match** (e.g. an "Opus 5" self-report satisfies the `opus` tier) rather than a hardcoded dated id, because a self-report names a product and dated ids drift — and canonicalizes it to that tier's alias. A missing or mismatched first line is treated exactly like a failed spawn: halt.

**Working directory (resolve once, thread always).** Resolve the working directory exactly once at invocation: the explicit `working-dir` argument if given, else the invoking checkout root (`git rev-parse --show-toplevel`), normalized to an absolute path; resolution failure (not a git repo) is a loud halt at invocation, because the contract requires committing. Thread that absolute path into every spawned agent's prompt — seeds, resolvers, and fixers — so no spawned agent derives its location from inherited cwd (process cwd is global mutable state; parallel fixers make ambient cwd a race). Read-only reviewers receive that root as well as absolute paths for every file the review hands them — they address it explicitly, and need no entry. Write-side fixers address the root explicitly with `git -C <path>` and absolute file paths (harness worktree-entry via `EnterWorktree` is not accepted from these cwd-pinned subagents, and explicit addressing is in any case the only mechanism that works for standalone reviews of checkouts outside `.claude/worktrees/`, which `EnterWorktree` rejects). The `working-dir` argument is an override only — omission cannot produce ambient-cwd behavior.

## Seed passes

Every mode runs the same two-seed shape: a **quality seed** and a **correctness seed**, both **findings-only** reviewer subagents, run in parallel, on the seed-reviewer model (see Model, below). Findings-only is a property of the seed prompts themselves — they read and report, they never edit — so no caller has to remember to enforce it separately.

| Mode | Quality seed | Correctness seed |
|---|---|---|
| **diff** | `/simplify`'s four angles plus this skill's seam-placement angle, inlined (below), findings-only, run against `BASE..HEAD`. | The superpowers `code-reviewer.md` template, used as designed (already read-only/findings-only) — see "Pinned template," below. |
| **design** | The design rubric (below) *is* the lens, applied adversarially to the proposed approach. | A prose-integrity checklist: placeholders/TBDs, internal contradictions, planning-blocking ambiguity, unstated assumptions, missing or untestable success criteria — plus the input-contract completeness and terminology-collision passes (below). |
| **plan** | The rubric applied to the plan's approach *and* to any embedded code sketches. | The prose checklist above, plus plan-specific checks: task ordering/dependencies, whether each task is executable by a fresh context-free subagent, per-task verification steps, and drift from the design doc. |

Do NOT invoke the `/simplify` skill for the diff-mode quality seed. `/simplify` applies fixes and re-derives its own scope, which breaks both findings-only and the model policy (its agents are not pinned to the seed-reviewer model). It is a harness built-in with no readable file to point a subagent at, so its four angles are transcribed verbatim below instead.

**The four `/simplify` angles (verbatim), then a fifth of this skill's own — all five apply:**
- **Reuse:** does this duplicate an existing utility/abstraction it could call instead? Consolidate the duplication.
- **Simplification:** can the same behavior be expressed more simply — fewer branches, less indirection, dead code removed, clearer control flow?
- **Efficiency:** needless work — redundant calls, repeated computation, avoidable queries/allocations, N+1 patterns.
- **Altitude:** is the change at the right level of abstraction — not hand-rolling what a higher-level seam already handles, not over-abstracting a one-off? Put the logic at the right layer.

**Seam placement:** applies only where the diff adds a construct that cannot be defined without naming another construct plus a qualifier: a near-copy of an existing type with fields loosened, a `raw`/`validated` variant of one concept, a converter between two shapes of one concept, a flag telling a callee which state its input is in, a newly required call ordering. Each spans a transformation, so "is it necessary as things stand?" is the wrong question — the answer is nearly always yes. Ask instead where the diff performs that transformation, and whether performing it at one *specific* other place deletes the construct outright. Then apply the deletion test to what you propose deleting: if the construct is what keeps a wire, stored, or versioned contract decoupled from the domain type, that reason survives the transformation moving and there is no finding. There is also no finding when the diff already performs the transformation at the place you would move it to — there is nowhere to move it. Report only when you can name the place, the deletion, and that nothing reappears in the construct's stead — this angle proposes removals, never a restructuring whose payoff is a nicer structure.

**Pinned template for diff / correctness:** use the `code-reviewer.md` found in the superpowers **`requesting-code-review`** skill directory (`.../skills/requesting-code-review/code-reviewer.md`) — it is already read-only/findings-only as designed. Do NOT use any other `code-reviewer.md` (there are others under `feature-dev`, `pr-review-toolkit`, and older superpowers layouts — those are agent templates for a different purpose). Fill its placeholders (`[DESCRIPTION]`, `[PLAN_OR_REQUIREMENTS]`, `[BASE_SHA]`, `[HEAD_SHA]`) from the PR summary, the plan path, and the branch `BASE`/`HEAD`.

**Input-contract completeness — the design *and* plan correctness seed:** applies only to fields the artifact newly accepts from outside the code it describes (an operator, an API client, a file, an upstream service). For each, report the gap between what its declared type permits and what the artifact says the domain allows — empty string, negative, fractional, out of range, `NaN`, duplicate within a collection, absent optional — and what each downstream consumer the artifact names does with a degenerate value. A blanket "validate minimally" or "the type is enough" is the claim this pass tests, per field, never an exemption from it. Findings only: which gaps are worth guarding is the resolvers' call.

**Terminology collision — the design *and* plan correctness seed:** applies only to words the artifact introduces or adopts as the name of a concept — one it defines, coins, or borrows from another source — never to the repo's vocabulary at large, and never to a word the artifact uses in the sense the repo already has. For each, check twice. **Against the repo:** read the domain glossary first (`CONTEXT.md` at the repo root, or the per-context files a root `CONTEXT-MAP.md` names), then grep the review's working directory for any term the glossary does not settle — a sense that lives only in shipped prose is still a collision. Grep shipped prose only: skip the artifact itself, and skip prior design/plan records (`docs/superpowers/`) — history, not shipped text. **Against itself:** one word carrying two senses, or two words carrying one. Report only what you can quote: the artifact's sense, the colliding sense, and where the colliding one lives; "define your terms" is not a finding. Findings only — a collision does not imply a rename, so report it either way; the fix is the resolvers' call. If the glossary is missing or settles nothing about the term, grep and proceed silently — the glossary's own state is never a finding: never flag it, never propose creating one.

## The design rubric

Every group-resolution agent (see Resolution procedure, below) applies this rubric, unchanged, as its judgment of what "best long-term design" means:

- Best long-term design over short-term tradeoffs; we care about codebase quality and maintainability, not effort or severity.
- OK to change adjacent code if it gets us to the better design.
- Before fixing at the point of failure, zoom out one level: if the thing touched is one of a known family (connectors, handlers, jobs…), put the fix at the shared boundary so current and future members inherit it — a per-instance fix the next person must remember to repeat is a latent regression.
- Prefer correct-by-default seams over designs where each caller must remember a flag, ordering, or manual step.
- When reusing shared infrastructure, question whether each inherited behavior belongs in the new context — inherited-but-irrelevant behavior is a wart even when harmless.
- Judge findings together, not in isolation — the best design often only appears when several concerns plus known upcoming work are held at once.
- Value simplicity; widen the lens only against concrete demand (planned siblings, 2+ instances), never speculation — zooming out finds the right boundary, it doesn't add layers.
- A fix must be worth its complexity: skip super-rare edge cases and race conditions unless the fix is essentially free.
- Every change must earn its place; if the fix is worse than the wart, leave it.

## Resolution procedure

1. Collect all findings from the seed passes, plus any additional findings the caller supplied with the invocation.
2. Group similar issues together. For each group, spawn one agent, on the resolver model (see Model).
3. Each group-agent:
   - First researches every issue it was assigned.
   - For each issue, determines the **best long-term design** by applying the rubric above, judging the group's findings together rather than in isolation.
   - Performs an **inline** adversarial self-check within its own context — it tries to break its own conclusion (counterexamples, simpler alternatives, hidden coupling) before concluding. **Group-agents never invoke `adversarial-review` or spawn further reviewer agents** — the protocol has exactly two tiers (seed reviewers, group resolvers), and recursion is forbidden.
   - If the best design isn't obvious, or the agent isn't confident, it asks itself: *"what additional research do I need, or what questions do I need answered, to determine the best long-term design?"* — then does that research. If it's still unclear, it files a new issue (see "Where new issues are filed," below) and moves on.
4. Apply each resolved fix — regardless of severity — only if it earns its place (fixer agents, on the main model). Skip a fix that is worse than the wart it addresses, or that is a complicated, hacky, or over-engineered fix for a super-rare edge case or race condition. Leave the artifact better than you found it; nothing more.
5. Commit the improved artifact — this skill owns the commit in every mode. Do not push or merge — those integration steps are the caller's.
   - **Design / plan docs:** rewrite the doc incorporating the resolutions, **preserving the doc's front-matter block unchanged** (front-matter is caller state, not review content), and commit the rewritten doc on the working directory's branch.
   - **PR diff:** commit the applied fixes on the branch. Then, if the project has a test suite, run it — red means the responsible fix is repaired or reverted before this step completes; never leave the branch red. Report the suite result (green, or "no suite exists") to the caller.
6. Report back: the commit(s) made, a summary of applied vs. skipped fixes, the post-fix suite result (diff mode), every new issue filed, and a **provenance** line naming the reviewers actually spawned per tier with their canonicalized tier aliases (from Review integrity's family match), in the form `seeds: N× <tier>; resolvers: M× <tier>` with `<tier>` ∈ {`sonnet`, `opus`} (e.g. `seeds: 2× sonnet; resolvers: 3× opus`; a review that surfaces no findings spawns no resolvers and reports `resolvers: 0`, tierless). Provenance is the evidence the invoking caller (dev-flow-worktree's orchestrator, when called by dev-flow-worktree) checks directly to confirm the review really fanned out to separate reviewer subagents on the tiers this section specifies — never a single inline pass.

## Model

**Group-resolution agents** — the tier that determines the best long-term design and adversarially self-checks — run on `opus` (a harness alias, never a dated model id), unconditionally, with no session-model-dependent fallback. Their independence from the artifact's author is **contextual, not cross-family**: a fresh context window with no memory of authoring, an explicitly adversarial prompt, and a spawn that provenance verifies out of band. A session-model-conditional tier would buy back family separation only by making the resolver tier depend on ambient state, which the provenance check could no longer compare against a fixed expectation.

**Seed reviewers** — the findings-only quality and correctness passes — run on `sonnet`: cheaper than `opus`, and in the common case a different family from the author, which is a bonus on what gets *noticed* rather than a guarantee this protocol enforces. They only surface findings; the resolvers do the judgment, so the resolver tier's cost isn't warranted here.

**Executors, fixers, and the orchestrator** run on the main session model.

## Where new issues are filed

File new issues with `gh issue create` when a GitHub remote exists; otherwise append them to `docs/superpowers/issues/BACKLOG.md`. Surface every filed issue in this skill's report back to the caller — never just a count.
