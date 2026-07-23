# dev-flow Plugin — Design Spec

> Revised 2026-07-22 by `2026-07-22-dev-flow-flatten-design.md` (flatten — current authority): nested spawning was removed in Claude Code 2.1.218, so the **orchestrator drives all fan-out** (reviews + Execute) itself, spawning only leaf workers; an intake gate checks model availability, not nesting. Supersedes the interim `2026-07-22-dev-flow-nested-review-fix-design.md`. **The body below predates the flatten pivot** — where it describes stage subagents, a fresh subagent per stage, or `EnterWorktree` entry, the flatten design governs.

**Date:** 2026-07-20
**Status:** Approved for planning (revised after adversarial design review)

## Goal

A single-invocation "dev flow" that carries a change from `design → plan → execute → PR → merge` autonomously, running a rigorous adversarial review at each artifact boundary. Default is full-auto to merge; the user can opt into a stop at any boundary. Each stage runs in a fresh subagent so the orchestrator's context stays thin, and all pipeline state lives in durable artifacts (see the Artifact Contract) so a run resumes cleanly after any stop or crash.

## Non-Goals (YAGNI)

- **Not** a new review methodology. The review reuses the `/simplify` quality lens (its four angles inlined — see Seed Passes) and the superpowers code-review template. It does **not** literally invoke the `/simplify` skill (that skill applies fixes and re-derives its own scope, which conflicts with findings-only seeds and the model policy).
- **Not** a `Workflow`-based orchestrator. We use prose skills + main-session orchestration + parallel `Agent` fan-out (build approach A). The review skill is structured so it *could* be promoted to a `Workflow` later without touching the pipeline, but that is out of scope now.
- **Not** multi-subsystem decomposition in one run. If a design spans independent subsystems, the design stage's scope check (and writing-plans' scope check) surfaces it and halts rather than forcing it through.
- **Not** merging broken work. Any stage that cannot proceed cleanly (red tests at any gate, unresolvable blocker) halts and hands back. "Leave it better than we found it" applies to the pipeline itself.

## Packaging

One plugin, **two skills**, **one entry point**.

```
plugins/dev-flow/
  .claude-plugin/plugin.json
  skills/dev-flow/SKILL.md            # orchestrator — the ONLY thing the user invokes
  skills/adversarial-review/SKILL.md  # reusable protocol — called internally per stage
```

Also register the plugin in `.claude-plugin/marketplace.json`.

**Why two skills, one invocation.** The user only ever invokes `dev-flow`. `adversarial-review` is internal machinery `dev-flow` calls at each boundary. Splitting it out serves three goals: **context hygiene** (a reviewer subagent loads only the review protocol, not the whole pipeline prose), **DRY** (the protocol is defined once and pointed at three artifacts), and **standalone reuse** (`adversarial-review` can be invoked directly on any existing design/plan/PR).

## Invocation

```
# from a bare idea (defaults to stop-after-design — see below):
"run dev-flow: add rate limiting to the API gateway"

# from an existing design file (full-auto by default):
"run dev-flow on docs/superpowers/specs/2026-07-20-rate-limit-design.md"

# with an opt-in stop / resume:
"run dev-flow on <design>, but stop after the plan so I can review"
"continue dev-flow on rate-limit"
```

### Stops

There are exactly three stop boundaries:

| Stop | Effect |
|---|---|
| `post-design` | Halt after the design is reviewed, rewritten, and committed. |
| `post-plan` | Halt after the plan is reviewed, rewritten, and committed. |
| `pre-merge` | Run everything through the reviewed PR, then halt before `gh pr merge`. A testing note (what to check) is part of the halt report, not a separate state. |

- **Default:** none (full-auto to merge) for **design-file entry** — the file the user wrote is their approval. **Bare-idea entry defaults to `post-design`**, because a bare idea is one giant unanswered design question and full-auto-to-merge on a *guessed* design is the pipeline's worst failure mode. Opt out with "full auto / no stops."
- **Persistence & precedence:** stops are written into the design doc's front-matter and committed, so resume honors them. Precedence: explicit stop in *this* invocation > recorded front-matter > full-auto default. So "continue dev-flow on rate-limit" honors a recorded `pre-merge` testing pause; "continue to merge, no stops" clears it.
- Every halt report **prints the exact resume invocation.**

## Model Policy

Express the invariant, not a constant:

- **Group-resolution agents** (the best-long-term-design + adversarial-self-check tier) run on a capable model **different from the artifact's author** — the load-bearing cross-model check. Default: `fable` (harness alias, most capable); `opus` if the session model is already Fable.
- **Seed reviewers** (the findings-only quality + correctness passes) run on `sonnet` — cheaper than Fable and still different from the typical `opus` author; the resolvers do the judgment, so Fable's premium isn't warranted on the seeds.
- **Executors, fixers, and the orchestrator** run on the main session model.

## Dispatching to Inherited Skills

dev-flow delegates stages to existing skills (subagent-driven-development, writing-plans, …). Those skills contain user-facing decision points that have no answerer in a full-auto run. One rule — carried as a standard preamble in **every** stage-dispatch prompt — governs all of them, so current and future inherited skills are handled correct-by-default:

> **dev-flow never lets an inherited skill talk to the user.** Every user-facing decision point in a delegated skill is handled one of three ways: **(a) pre-answered** — the dispatch states the pipeline's answer as a declared preference; **(b) superseded** — the skill's terminal hand-off steps (integration menus, "what next" offers, follow-on skill invocations, final reviews) are replaced by the dispatch's explicit exit condition, because the pipeline owns all stage transitions; **(c) halted** — any user-directed question not covered by (a) or (b) is a blocker: the stage stops and reports the question verbatim, and the orchestrator hands back. A subagent never invents an answer to an unanticipated gate.

Corollaries:
- A skill whose **core mechanism is user dialogue** (`brainstorming`) cannot be dispatched at all — its non-interactive parts are inlined instead (see Stage 1).
- **Integration** (merge, or any push beyond the feature branch) happens only where a stage explicitly says so — never inside a delegated skill.
- **Red tests at any gate halt the pipeline** (baseline, stage exit, CI).
- **Worktrees are never delegated.** dev-flow owns the worktree lifecycle itself — no stage asks a skill to create one. If a delegated skill invokes `using-git-worktrees` internally (SDD requires it), that is safe: the dispatch already runs inside the pipeline worktree, so its Step-0 isolation check creates nothing.
- The rule targets **user**-directed seams only; agent-to-agent interaction (e.g. SDD's controller answering its implementer) is untouched.

---

## Artifact Contract

State lives in artifacts, not a side file. **A dev-flow feature *is* its branch; every piece of pipeline state is either committed on that branch or attached to that branch's PR, and every resume decision is a mechanical read of one of those two places.**

**Slug.** The orchestrator fixes a kebab-case slug (2–4 words) once at intake — derived from the design filename if given (`2026-07-20-rate-limit-design.md` → `rate-limit`), else chosen from the idea. It is an opaque, immutable ID (renaming the feature changes prose, never the slug). It threads through:

- spec: `docs/superpowers/specs/YYYY-MM-DD-<slug>-design.md`
- plan: `docs/superpowers/plans/YYYY-MM-DD-<slug>-plan.md`
- branch: `dev-flow/<slug>`
- PR: `gh pr list --head dev-flow/<slug> --state all` (branch→PR mapping is native to gh). Always pass `--state all` — the default listing is open-only and hides merged/closed PRs. "Latest PR" = the highest-numbered result.

Intake collision check: qualify the new slug if `dev-flow/<slug>` exists (local or origin) with a committed design describing a different feature, **or** if no branch exists but `gh pr list --head dev-flow/<slug> --state all` is non-empty — a slug whose PR history belongs to an earlier shipped feature is retired, keeping the resume table's PR-state reads unambiguous forever. (This replaces fuzzy topic-matching with mechanical existence checks.)

**Front-matter (the only new schema).** Design doc:

```yaml
---
dev-flow:
  slug: rate-limit
  stops: [post-plan, pre-merge]   # [] = full-auto to merge
---
```

Plan doc: `dev-flow: {slug: rate-limit, spec: docs/superpowers/specs/2026-07-20-rate-limit-design.md}` (linkage only). **Stops live solely in the design doc.** The PR body links both doc paths. `adversarial-review` preserves the front-matter block on every rewrite (part of its contract).

**Doc git lifecycle — branch + worktree at design start.** Creating `dev-flow/<slug>` and its worktree is the *first* act of Stage 1 (the worktree lifecycle's Create step, below; design/plan only need a checkout — setup is ensured at entry from Execute onward). All docs are written and committed **in the worktree, on the branch**. A doc's content is committed **only by `adversarial-review`, as the final step of its rewrite** — so "doc committed at tip" ≡ "stage complete" by construction, removing the need for any separate "reviewed" marker on docs. (dev-flow itself commits only pipeline-state edits: front-matter `stops` updates and plan-checkbox ticks.) Adopt-existing-file entry: branch from main, copy the file in, stamp front-matter, then review — which rewrites and commits. On every halt/stop, push the branch if a remote exists. dev-flow always runs in a dedicated worktree — there is no "work in the main checkout" mode. **Worktree lifecycle (dev-flow-owned, plain git):** the contract needs a worktree on a branch named exactly `dev-flow/<slug>`, based off the default branch, at a findable path — none of which a delegated mechanism guarantees (native tools auto-name the branch and take their base from a setting; using-git-worktrees skips creation when already isolated and works in place on sandbox errors). So dev-flow creates/enters/removes it itself with plain git, at `<main-root>/.claude/worktrees/dev-flow-<slug>` (the only path a native entry tool accepts from a pinned subagent). Base = the default branch (`git symbolic-ref --short refs/remotes/origin/HEAD`, else `main`/`master`, else halt); never the invoking HEAD. Every stage dispatch (first run and resume) runs one entry procedure: locate the worktree by branch; re-attach (`git worktree add <path> dev-flow/<slug>`, no `-b`) if the branch exists but no worktree does; create only as Stage 1's first act (else halt — contract violation), halting on sandbox/permission failure with no work-in-place fallback; enter (native path-mode tool or `cd`); ensure deps are installed for code-running stages; and on a dirty Execute resume, stash-and-report tracked changes (halt on later landings).

**Execution-complete signal.** When a task's review comes back clean, dev-flow's SDD wrapper ticks that task's `- [ ]` checkboxes in the plan file and commits them, alongside SDD's ledger append. **Committed checkboxes are the durable, authoritative cross-session signal; SDD's `.superpowers/sdd/progress.md` ledger stays in-session scratch (it is git-ignored and dies with the worktree).** Execute is complete ⇔ zero `- [ ]` remain in the plan at branch tip. Tie-break: if `git log` shows a task's commits but its boxes are unticked (crash in the gap), verify via `git log`, tick, don't re-implement.

**Review state.** After Stage 4's review has committed its fixes and the stage has pushed, post a PR comment with the marker line `dev-flow: review clean @ <full-head-sha>`. Detection: marker SHA == current head → merge gate; stale SHA → re-review (any push, including a CI fix, correctly invalidates); no marker → PR review. (A label can't carry the SHA and goes silently stale — rejected.)

**Resume table** (checks run top-to-bottom, first match wins; each is mechanical; "latest PR" = the highest-numbered result of `gh pr list --head dev-flow/<slug> --state all`):

| Check | Start at |
|---|---|
| No `dev-flow/<slug>` branch (local or origin); bare idea | Design: create branch+worktree, draft |
| No branch; existing design file given | Design: adopt (branch, front-matter, review — which commits) |
| Branch exists; latest PR is `MERGED` | Done — run Stage 5's Cleanup (idempotent), then report; nothing to resume |
| Branch exists; latest PR is `CLOSED` | Halt — a human closed PR #N without merging; report and hand back |
| Branch exists; no design doc with `dev-flow` front-matter at tip | Design (redo; uncommitted drafts discarded) |
| Design committed at tip; no plan doc at tip | Plan |
| Plan at tip has ≥1 unchecked `- [ ]` | Execute — resume at first unchecked task (cross-check ledger + `git log`) |
| Plan fully checked; no PR for the branch (`--state all` empty) | PR: create + review |
| Open PR; no `review clean @ <current head>` marker | PR review |
| Open PR; marker matches head | Merge gate (CI, `stops` from front-matter) |
| No row matches (e.g. unknown slug) | Nothing to resume — report; if a merged PR exists say "already shipped (PR #N)", else list `dev-flow/*` branches |

---

## Pipeline (`dev-flow` skill)

Each stage is run by a fresh subagent carrying the inherited-skills preamble, begins with the worktree-entry procedure (Artifact Contract), and returns only a short summary to the orchestrator.

### Stage 1 — Design

- **First:** fix the slug, then create `dev-flow/<slug>` and its worktree per the worktree lifecycle (Artifact Contract) — plain git (`git worktree add <main-root>/.claude/worktrees/dev-flow-<slug> -b dev-flow/<slug> <default-branch>`), not a delegated skill, since no delegated mechanism guarantees the exact branch name or base that every resume check and the PR mapping key off. Creation failure halts.
- **Given a design-file path:** adopt it (branch, copy in, stamp front-matter, …).
- **Given a bare idea:** produce a best-judgment design doc. `brainstorming` is **not** invoked (dialogue is its core mechanism); its bones are inlined non-interactively: (1) explore project context; (2) scope/decomposition check — if the idea spans independent subsystems, **halt and report** the proposed decomposition; (3) consider 2–3 approaches, pick one, record the choice + rejected alternatives + reasoning; (4) record defensible-default assumptions explicitly — a *genuinely blocking* ambiguity (no defensible default) is a **halt-and-report**, not a guess; (5) run brainstorming's spec self-review checklist (placeholders, consistency, scope, ambiguity).
- Run `adversarial-review` (mode: design) — it is the approval gate that substitutes for the user's. The review itself rewrites the design and commits it on the branch (its contract); the stage has no apply or commit step of its own.
- Bare-idea entry defaults to a `post-design` stop.

### Stage 2 — Plan

- Spawn a subagent to run `superpowers:writing-plans` against the design, producing `docs/superpowers/plans/YYYY-MM-DD-<slug>-plan.md` (front-matter links the spec).
- Run `adversarial-review` (mode: plan). The review rewrites the plan and commits it on the branch; nothing to apply afterward.
- `post-plan` stop → halt and report.

### Stage 3 — Execute

Dispatch to `superpowers:subagent-driven-development` with these overrides (per the inherited-skills rule):

- **Baseline:** worktree entry already ensured setup; run the baseline suite before the first task. A **red baseline halts** (a CI-green merge gate can't be reached from a red baseline).
- **Exit condition (supersedes SDD's terminal):** last task complete, per-task reviews clean, full suite green, on the named branch. **Do not** run SDD's final whole-branch review; **do not** invoke `finishing-a-development-branch` (its interactive menu's option 1 is a local merge to base — the exact self-merge the pipeline exists to prevent). Report: branch, commit range, ledger path, and the ledger's unresolved Minor findings.
- **Pre-answers:** a plan-vs-code conflict is resolved by the **design doc** (the highest-reviewed artifact); if it's silent, halt.
- **Halts:** SDD `BLOCKED` after its own ladder (more context / stronger model / split task) with "the plan itself is wrong" → halt and report.
- **Bookkeeping:** on each task-review-clean, tick that task's plan checkboxes and commit (see Artifact Contract).

### Stage 4 — PR

- `gh pr create`; PR body links the spec + plan paths and derives a summary from them. Reuse an existing open PR for the branch rather than creating a duplicate.
- Run `adversarial-review` (mode: diff), passing Stage 3's unresolved Minor-findings list as caller-supplied findings. **This *is* the pipeline's final whole-branch review** (SDD's was suppressed in Stage 3). The review applies the resolved fixes, commits them on the branch, and (its contract) runs the project's test suite after fixing.
- **Post-fix test gate:** post the marker only when the review reported the suite green, or reported that no automated suite exists (e.g. a prose-only repo). Never post the marker on a red branch. The marker certifies **reviewed and suite-green (or no suite exists) at this exact SHA** — Stage 5 relies on this when a repo has no CI.
- Push the branch, then post the `dev-flow: review clean @ <full-head-sha>` marker comment.
- `pre-merge` stop → halt and report (PR open, reviewed, fixes pushed) with the testing note and resume invocation.

### Stage 5 — Merge

- Confirm the `review clean` marker SHA == current head (else re-review).
- **Bounded CI wait:** `gh pr checks <pr> --watch` under a hard cap (default 10 minutes; `--watch` has no native timeout, so the runner enforces the cap via its command timeout). Four outcomes, distinguished by output text (failure and no-checks both exit 1; pending exits 8): all pass → proceed; any fail → halt and report; still pending at the cap → **halt and report "CI still pending"** (resume re-enters the merge gate for free); output contains **"no checks reported"** (no CI on this PR) → proceed, safe only because the marker already certifies Stage 4's test gate. Never an open-ended block, and never read "no checks" as a green test signal on its own.
- Consult `stops` from front-matter; a `pre-merge` stop pauses here with the testing note.
- **Merge:** `gh pr merge <pr> --squash` — **without** `--delete-branch` (git refuses to delete a branch checked out in the pipeline worktree; gh's fallback also fails since the default branch is checked out in the main worktree). Branch deletion is Cleanup's job, ordered so it works.
- **Cleanup (idempotent — the resume table's Done row runs this same block; each step treats "already gone" as success):** (1) `cd` to the main repo root; (2) remove the pipeline-created worktree (`git worktree list --porcelain` → the entry for `refs/heads/dev-flow/<slug>`, then `git worktree remove` + `git worktree prune`; the branch name is the provenance — any worktree on it is this feature's; `--force` only for stray untracked scratch, halt on uncommitted *tracked* changes); (3) `git branch -D dev-flow/<slug>` — must be `-D` (a squash-merged branch is never "fully merged" so `-d` refuses) and must follow (2); (4) `git push origin --delete dev-flow/<slug>`, treating "remote ref does not exist" as success.
- **Final report:** what shipped + every new issue filed across all stages.

---

## The Reusable Protocol (`adversarial-review` skill)

Invoked as `adversarial-review(target, mode[, extra findings])` where `mode ∈ {design, plan, diff}`. dev-flow passes the mode; standalone use infers it (path under `specs/` → design, `plans/` → plan, PR/branch/SHA-range → diff); a caller may pass additional findings that join the seed findings. **Contract:** the skill owns the artifact end-to-end — reviews, resolves, applies, and **commits** the improved artifact on the current branch in every mode; it never pushes, posts to a PR, or merges (those are the caller's).

### Seed passes

Every mode runs the **same two-seed shape** — a **quality seed** and a **correctness seed**, both **findings-only** reviewer subagents on the seed-reviewer model (`sonnet`), in parallel. Findings-only is a property of the seed prompts themselves, so no caller has to remember to enforce it.

| Mode | Quality seed | Correctness seed |
|---|---|---|
| **diff** | `/simplify`'s four angles **inlined** (Reuse / Simplification / Efficiency / Altitude), findings-only, against BASE..HEAD. *(The `/simplify` skill is not invoked — its apply step and self-derived scope would break findings-only and the model policy.)* | superpowers `code-reviewer.md` template used as designed (already read-only/findings-only); placeholders filled by the pipeline (description from PR summary, requirements = plan path, BASE/HEAD from the branch). |
| **design** | the design rubric (below) *is* the lens, applied adversarially to the proposed approach. | prose-integrity checklist: placeholders/TBDs, internal contradictions, planning-blocking ambiguity, unstated assumptions, missing/untestable success criteria. |
| **plan** | the rubric applied to the plan's approach **and to embedded code sketches**. | the prose checklist **plus** plan-specific checks: task ordering/dependencies, each task executable by a fresh context-free subagent, per-task verification steps, drift from the design doc. |

The four `/simplify` angles (inlined verbatim into the diff-mode quality seed): **Reuse** — duplicates an existing utility/abstraction it could call instead; **Simplification** — same behavior expressible with fewer branches, less indirection, less dead code; **Efficiency** — redundant calls, repeated computation, avoidable queries/allocations, N+1 patterns; **Altitude** — right level of abstraction, neither hand-rolling what a higher-level seam handles nor over-abstracting a one-off.

### The design rubric (verbatim — the judgment the review agents apply)

- Best long-term design over short-term tradeoffs; we care about codebase quality and maintainability, not effort or severity.
- OK to change adjacent code if it gets us to the better design.
- Before fixing at the point of failure, zoom out one level: if the thing touched is one of a known family (connectors, handlers, jobs…), put the fix at the shared boundary so current and future members inherit it — a per-instance fix the next person must remember to repeat is a latent regression.
- Prefer correct-by-default seams over designs where each caller must remember a flag, ordering, or manual step.
- When reusing shared infrastructure, question whether each inherited behavior belongs in the new context — inherited-but-irrelevant behavior is a wart even when harmless.
- Judge findings together, not in isolation — the best design often only appears when several concerns plus known upcoming work are held at once.
- Value simplicity; widen the lens only against concrete demand (planned siblings, 2+ instances), never speculation — zooming out finds the right boundary, it doesn't add layers.
- A fix must be worth its complexity: skip super-rare edge cases and race conditions unless the fix is essentially free.
- Every change must earn its place; if the fix is worse than the wart, leave it.

### Resolution procedure

1. Collect findings from the seed passes, plus any additional findings the caller supplied with the invocation.
2. **Group similar issues together.** For each group, spawn one agent (resolver model — `fable`).
3. Each group-agent:
   - First **researches all issues** it was assigned.
   - For each issue, determines the **best long-term design** (applying the rubric; judging the group's findings together).
   - Performs an **inline adversarial self-check within its own context** — it tries to break its own conclusion (counterexamples, simpler alternatives, hidden coupling) before concluding. Group-agents **never invoke `adversarial-review` or spawn further reviewer agents** — the protocol has exactly two tiers (seed reviewers, group resolvers); recursion is forbidden.
   - If the best design is not obvious or the agent is not confident, it asks: *"what additional research do I need, or what questions do I need answered, to determine the best long-term design?"* — then does that research. If still unclear, **file a new issue and move on.**
4. **Apply** each resolved fix — *regardless of severity* — **only if it earns its place** (fixer agents, main model). Skip if the fix is worse than the wart, or is a super-rare edge case / race whose fix is complicated, hacky, or over-engineered. Leave the code better than we found it; nothing else.
5. After resolution, **commit the improved artifact** — this skill owns the commit in every mode; it never pushes (that's the caller's):
   - **Design / plan docs:** rewrite the doc incorporating resolutions (preserving front-matter), and commit it on the branch.
   - **PR diff:** commit the applied fixes on the branch; then, if the project has a test suite, run it (repair or revert any fix that leaves it red) and report the suite result (green, or "no suite exists") to the caller.
6. **Report every new issue filed.**

### Where new issues are filed

`gh issue create` when a GitHub remote exists; otherwise append to `docs/superpowers/issues/BACKLOG.md`. All filed issues are surfaced in the stage report and again in the final pipeline report.

---

## Environment Assumptions

- **Flat topology — the orchestrator is the only spawner.** Every subagent is a leaf; no subagent spawns a subagent. Required: Claude Code 2.1.218 removed spawned subagents' `Agent` tool (nesting gone; the harness recommends top-level orchestration only). The orchestrator invokes all fan-out skills (`adversarial-review`, SDD) in-context and spawns their workers itself — one level, any version. An intake gate checks model *availability*. (Details in `2026-07-22-dev-flow-flatten-design.md`.)
- **GitHub remote** from Stage 4 onward (the pipeline uses `gh` for PR, review marker, CI, merge). This matches the existing plugins' reliance on `gh`.

## Cross-Cutting Concerns

- **Context hygiene:** every stage and every review group runs in a fresh subagent; only short summaries return upward.
- **Failure handling:** a stage that cannot proceed cleanly halts and hands back with a clear report and resume invocation; the pipeline never merges work that is worse than what it started with.
- **Idempotent resume:** guaranteed by the Artifact Contract — every resume decision is a mechanical read of the branch tip or the PR.
- **Severity-independent, value-gated:** the protocol acts on issues of any severity but only when the fix genuinely improves the codebase.

## How We'll Know It Works

- Plugin structure validates: `plugin.json` well-formed, registered in `marketplace.json`, both skills load and their descriptions trigger appropriately.
- Smoke test: run `dev-flow` on a small real change to `post-design`, confirm the branch/worktree, front-matter, design doc, and adversarial-review behave; then resume through plan and execute on the same slug.
- End-to-end dry run on a trivial PR confirms the SHA-pinned review marker, bounded CI wait **including the no-CI "no checks reported" outcome**, `pre-merge` pause, and squash-merge + full cleanup (worktree removed, local branch `-D`-deleted, remote branch gone) before trusting full-auto merge.

## Decisions Locked During Review

- Bare-idea entry defaults to `post-design`; design-file entry is full-auto. (Open Question 1 — resolved yes.)
- New issues: `gh issue create`, local-backlog fallback. (Open Question 2.)
- Merge method: `--squash`; branch deletion is the pipeline's ordered cleanup (worktree removal, then local `-D`, then remote delete) — `--delete-branch` can't delete a branch checked out in the pipeline worktree. (Open Question 3, revised.)
