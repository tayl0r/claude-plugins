---
name: adversarial-review
description: Use to run a rigorous adversarial review on a single artifact — a design doc, a plan doc, or a PR/diff. Seeds with findings-only quality and correctness passes, then groups issues and resolves each to the best long-term design with adversarial self-checks. Triggers on "adversarial review", "review this design/plan/PR properly", or is called internally by dev-flow at each stage.
---

# Adversarial Review

Run a rigorous adversarial review on ONE target artifact and resolve every finding to the best long-term design, applying only fixes that earn their place.

**Invocation:** `adversarial-review(target, mode[, extra findings])` where `mode` is one of `design`, `plan`, `diff`.
- When called by dev-flow, the mode is passed explicitly.
- Standalone, infer the mode: a path under `specs/` -> `design`; under `plans/` -> `plan`; a PR number, branch, or SHA range -> `diff`.
- A caller may pass additional findings (e.g. leftovers from an earlier review); they join the seed findings in Resolution step 1.

**Contract:** this skill owns the artifact end-to-end — it reviews, resolves, applies, and **commits** the improved artifact on the current branch, in every mode. The caller never re-applies or re-commits the review's work. It never pushes, posts review results to a PR, or merges — those integration steps are the caller's. (Filing a new issue via `gh`, per "Where new issues are filed," is part of the review, not integration.)

**Review integrity (never inline).** The seed and resolver passes MUST run as separate subagents on their specified models (per Model, below). If they cannot be spawned — no `Agent` tool, or a required model unavailable — halt and report; **never** produce a single-model inline review as a silent substitute. To make the model axis verifiable, every reviewer prompt (seed and resolver) requires the reviewer to state, as the first line of its report, the model its own system prompt names. The review matches each self-report to the tier requested for it — a **family match** (e.g. a "Fable 5" self-report satisfies the `fable` tier), honoring the resolver opus-fallback rather than a hardcoded id — and canonicalizes it to the tier alias (`sonnet`, `fable`, or `opus`). A missing or mismatched first line is treated exactly like a failed spawn: halt.

## Seed passes

Every mode runs the same two-seed shape: a **quality seed** and a **correctness seed**, both **findings-only** reviewer subagents, run in parallel, on the seed-reviewer model (`sonnet` — see Model, below). Findings-only is a property of the seed prompts themselves — they read and report, they never edit — so no caller has to remember to enforce it separately.

| Mode | Quality seed | Correctness seed |
|---|---|---|
| **diff** | `/simplify`'s four angles, inlined (below), findings-only, run against `BASE..HEAD`. | The superpowers `code-reviewer.md` template, used as designed (already read-only/findings-only) — see "Pinned template," below. |
| **design** | The design rubric (below) *is* the lens, applied adversarially to the proposed approach. | A prose-integrity checklist: placeholders/TBDs, internal contradictions, planning-blocking ambiguity, unstated assumptions, missing or untestable success criteria. |
| **plan** | The rubric applied to the plan's approach *and* to any embedded code sketches. | The prose checklist above, plus plan-specific checks: task ordering/dependencies, whether each task is executable by a fresh context-free subagent, per-task verification steps, and drift from the design doc. |

Do NOT invoke the `/simplify` skill for the diff-mode quality seed. `/simplify` applies fixes and re-derives its own scope, which breaks both findings-only and the model policy (its agents are not pinned to the seed-reviewer model). It is a harness built-in with no readable file to point a subagent at, so its four angles are transcribed verbatim below instead.

**The four `/simplify` angles (verbatim):**
- **Reuse:** does this duplicate an existing utility/abstraction it could call instead? Consolidate the duplication.
- **Simplification:** can the same behavior be expressed more simply — fewer branches, less indirection, dead code removed, clearer control flow?
- **Efficiency:** needless work — redundant calls, repeated computation, avoidable queries/allocations, N+1 patterns.
- **Altitude:** is the change at the right level of abstraction — not hand-rolling what a higher-level seam already handles, not over-abstracting a one-off? Put the logic at the right layer.

**Pinned template for diff / correctness:** use the `code-reviewer.md` found in the superpowers **`requesting-code-review`** skill directory (`.../skills/requesting-code-review/code-reviewer.md`) — it is already read-only/findings-only as designed. Do NOT use any other `code-reviewer.md` (there are others under `feature-dev`, `pr-review-toolkit`, and older superpowers layouts — those are agent templates for a different purpose). Fill its placeholders (`[DESCRIPTION]`, `[PLAN_OR_REQUIREMENTS]`, `[BASE_SHA]`, `[HEAD_SHA]`) from the PR summary, the plan path, and the branch `BASE`/`HEAD`.

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
2. Group similar issues together. For each group, spawn one agent, on the resolver model (`fable` — see Model).
3. Each group-agent:
   - First researches every issue it was assigned.
   - For each issue, determines the **best long-term design** by applying the rubric above, judging the group's findings together rather than in isolation.
   - Performs an **inline** adversarial self-check within its own context — it tries to break its own conclusion (counterexamples, simpler alternatives, hidden coupling) before concluding. **Group-agents never invoke `adversarial-review` or spawn further reviewer agents** — the protocol has exactly two tiers (seed reviewers, group resolvers), and recursion is forbidden.
   - If the best design isn't obvious, or the agent isn't confident, it asks itself: *"what additional research do I need, or what questions do I need answered, to determine the best long-term design?"* — then does that research. If it's still unclear, it files a new issue (see "Where new issues are filed," below) and moves on.
4. Apply each resolved fix — regardless of severity — only if it earns its place (fixer agents, on the main model). Skip a fix that is worse than the wart it addresses, or that is a complicated, hacky, or over-engineered fix for a super-rare edge case or race condition. Leave the artifact better than you found it; nothing more.
5. Commit the improved artifact — this skill owns the commit in every mode. Do not push or merge — those integration steps are the caller's.
   - **Design / plan docs:** rewrite the doc incorporating the resolutions, **preserving the doc's front-matter block unchanged** (front-matter is caller state, not review content), and commit the rewritten doc on the current branch.
   - **PR diff:** commit the applied fixes on the branch. Then, if the project has a test suite, run it — red means the responsible fix is repaired or reverted before this step completes; never leave the branch red. Report the suite result (green, or "no suite exists") to the caller.
6. Report back: the commit(s) made, a summary of applied vs. skipped fixes, the post-fix suite result (diff mode), every new issue filed, and a **provenance** line naming the reviewers actually spawned per tier with their canonicalized tier aliases (from Review integrity's family match), in the form `seeds: N× <tier>; resolvers: M× <tier>` with `<tier>` ∈ {`sonnet`, `fable`, `opus`} (e.g. `seeds: 2× sonnet; resolvers: 3× fable`). Provenance is the evidence a caller checks to confirm the review was genuinely model-diverse.

## Model

**Group-resolution agents** — the tier that determines the best long-term design and adversarially self-checks — run on a capable model **different from the artifact's author**, where cross-model scrutiny matters most. Default to `fable` (a harness alias — never a dated model id — and the most capable model); if the main session model is already in the Fable family, use `opus` instead.

**Seed reviewers** — the findings-only quality and correctness passes — run on `sonnet`: cheaper than Fable, and still typically different from the `opus`-family author. They only surface findings; the resolvers do the judgment, so Fable's premium isn't warranted here.

**Executors, fixers, and the orchestrator** run on the main session model.

## Where new issues are filed

File new issues with `gh issue create` when a GitHub remote exists; otherwise append them to `docs/superpowers/issues/BACKLOG.md`. Surface every filed issue in this skill's report back to the caller — never just a count.
