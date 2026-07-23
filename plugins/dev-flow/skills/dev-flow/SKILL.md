---
name: dev-flow
description: Use when the user wants to run their end-to-end dev flow — carry a change from design to plan to execute to PR to merge autonomously, with adversarial review at each stage. Triggers on "run dev-flow", "run my dev flow", "dev-flow on <design file>", "continue dev-flow on <slug>", or "take this design to a merged PR".
---

# dev-flow

Carry a change from design -> plan -> execute -> PR -> merge in one invocation. Default is full-auto to merge; the user can opt into a stop at any artifact boundary. Each stage runs in a fresh subagent so this orchestrator's context stays thin, and all state lives in durable artifacts (the Artifact Contract) so a run resumes cleanly after any stop or crash.

This is the only skill the user invokes. It calls the `dev-flow:adversarial-review` skill internally at each boundary.

## Invocation

Accept these forms:

```
# from a bare idea (defaults to stop-after-design — see Stops, below):
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

- **Default:** none (full-auto to merge) for **design-file entry** — the file the user wrote is their approval. **Bare-idea entry defaults to `post-design`**: a bare idea is one giant unanswered design question, and full-auto-to-merge on a *guessed* design is the pipeline's worst failure mode. The user opts out with "full auto" or "no stops."
- **Persistence:** write stops into the design doc's `dev-flow` front-matter and commit them, so resume honors them.
- **Precedence:** an explicit stop given in *this* invocation beats a recorded front-matter stop, which beats the full-auto default. So "continue dev-flow on rate-limit" honors a recorded `pre-merge` stop; "continue to merge, no stops" clears it.
- Every halt report **prints the exact resume invocation** the user should run next.

## Model Policy

Everything this skill spawns directly — stage subagents, executors, bookkeeping agents — runs on the main session model. Reviewer-model selection (adversary-side agents on a capable model different from the artifact's author) is owned by `dev-flow:adversarial-review` and stated once, in its Model section; that rule travels with the review skill wherever it is invoked.

## Capability gate (runs first, every invocation)

Before any drafting, resume routing, or stage dispatch — on first run **and** every resume — dev-flow probes that the environment can run the model-diverse nested review, because the whole pipeline depends on it and the grant can be absent version-independently (restricted spawn type, permission settings, `allowedTools`):

1. Spawn one `general-purpose` subagent. It confirms it holds both `Agent` and `Skill`, then spawns one sub-subagent on the seed model and one on the resolver model — the tiers per `dev-flow:adversarial-review`'s Model section (currently `sonnet` for seeds; `fable`, or `opus` in a Fable-family session, for resolvers) — each returning the model its system prompt names.
2. If the subagent lacks either tool, either sub-subagent fails to spawn, or a returned model does not match the tier requested (by family match per `dev-flow:adversarial-review`'s Review integrity — e.g. a "Fable 5" report satisfies `fable`), **halt** with a report naming the missing capability and citing the verified-working version (2.1.217) as a diagnostic hint.

This is a hard gate, not advisory: it turns a capability failure into an intake halt — before any design draft is written and then discarded on resume — rather than a mid-run silent degradation. It runs uniformly on every invocation by design; conditional probing ("only when a review will run") would be a remember-which-resume-rows rule.

## Dispatching to Inherited Skills

dev-flow delegates stages to existing skills (`subagent-driven-development`, `writing-plans`, …). Those skills contain user-facing decision points that have no answerer in a full-auto run. Carry the following rule as a standard preamble in **every** stage-dispatch prompt, so current and future inherited skills are handled correct-by-default:

> **dev-flow never lets an inherited skill talk to the user.** Every user-facing decision point in a delegated skill is handled one of three ways: **(a) pre-answered** — the dispatch states the pipeline's answer as a declared preference; **(b) superseded** — the skill's terminal hand-off steps (integration menus, "what next" offers, follow-on skill invocations, final reviews) are replaced by the dispatch's explicit exit condition, because the pipeline owns all stage transitions; **(c) halted** — any user-directed question not covered by (a) or (b) is a blocker: the stage stops and reports the question verbatim, and the orchestrator hands back. A subagent never invents an answer to an unanticipated gate.
>
> **A stage never performs an adversarial review itself.** If the `Skill` tool cannot load `dev-flow:adversarial-review`, or the `Agent` tool is unavailable for the reviewer subagents it must spawn, halt and report the missing capability — an inline single-model review is a contract violation, never a fallback (this clause rides in the dispatch prompt because it is the only channel that reaches the stage subagent regardless of its toolset). When you do invoke `dev-flow:adversarial-review`, pass your pipeline worktree's absolute path as its `working-dir`, and copy the review's returned **provenance** line verbatim into your stage summary.

Corollaries:
- A skill whose **core mechanism is user dialogue** (`brainstorming`) cannot be dispatched at all — inline its non-interactive parts instead (see Stage 1).
- **Integration** (merge, or any push beyond the feature branch) happens only where a stage explicitly says so — never inside a delegated skill.
- **Red tests at any gate halt the pipeline** (baseline, stage exit, CI).
- **Worktrees are never delegated.** dev-flow owns the worktree lifecycle itself (see Artifact Contract) — no stage asks a skill to create one. If a delegated skill invokes `superpowers:using-git-worktrees` internally (SDD lists it as a required workflow skill), that is safe by construction: the dispatch already runs inside the pipeline worktree, so that skill's Step-0 isolation check passes and it creates nothing; its setup/baseline steps then land in the right workspace. Its "tests fail -> ask" gate is covered by the red-tests corollary above.
- This rule targets **user**-directed seams only; agent-to-agent interaction (e.g. SDD's controller answering its implementer) is untouched.

---

## Artifact Contract

State lives in artifacts, not a side file. **A dev-flow feature *is* its branch; every piece of pipeline state is either committed on that branch or attached to that branch's PR, and every resume decision is a mechanical read of one of those two places.**

**Slug.** Fix a kebab-case slug (2-4 words) once at intake — derive it from the design filename when one is given (`2026-07-20-rate-limit-design.md` -> `rate-limit`), else choose one from the idea. Treat it as an opaque, immutable ID: renaming the feature changes prose, never the slug. It threads through:

- spec: `docs/superpowers/specs/YYYY-MM-DD-<slug>-design.md`
- plan: `docs/superpowers/plans/YYYY-MM-DD-<slug>-plan.md`
- branch: `dev-flow/<slug>`
- PR: `gh pr list --head dev-flow/<slug> --state all` (branch->PR mapping is native to `gh`). Always pass `--state all` — the default listing is open-only and silently hides merged/closed PRs. "Latest PR" = the highest-numbered result.

Intake collision check: qualify the new slug if `dev-flow/<slug>` already exists (local or origin) with a committed design describing a different feature, **or** if no branch exists but `gh pr list --head dev-flow/<slug> --state all` is non-empty — a slug whose PR history belongs to an earlier shipped feature is retired, so the resume table's PR-state reads stay unambiguous forever. (This replaces fuzzy topic-matching with mechanical existence checks.)

**Front-matter (the only new schema).** Design doc:

```yaml
---
dev-flow:
  slug: rate-limit
  stops: [post-plan, pre-merge]   # [] = full-auto to merge
---
```

Plan doc: `dev-flow: {slug: rate-limit, spec: docs/superpowers/specs/2026-07-20-rate-limit-design.md}` (linkage only). **Stops live solely in the design doc.** The PR body links both doc paths. `dev-flow:adversarial-review` preserves front-matter on every rewrite (part of its contract), so this block survives all reviews.

**Doc git lifecycle — branch + worktree at design start.** Creating `dev-flow/<slug>` and its worktree is the *first* act of Stage 1 (the Create step of the worktree lifecycle, below; design and plan only need a checkout — setup is ensured at entry from Execute onward). Write and commit all docs **in the worktree, on the branch**. A doc's content is committed **only by `dev-flow:adversarial-review`, as the final step of its rewrite** — so "doc committed at tip" is equivalent to "stage complete" by construction, which removes the need for any separate "reviewed" marker on docs. (dev-flow itself commits only pipeline-state edits: front-matter `stops` updates and plan-checkbox ticks.) Adopt-existing-file entry: branch from main, copy the file in, stamp front-matter, then review — the review rewrites and commits. On every halt/stop, push the branch if a remote exists. dev-flow always runs in a dedicated worktree — there is no "work in the main checkout" mode.

**Worktree lifecycle — owned by dev-flow, plain git.** The contract stakes everything on one invariant: *a worktree on a branch named exactly `dev-flow/<slug>`, based off the default branch, always exists and is findable by every stage.* No delegated mechanism guarantees that (native tools auto-name branches and take their base from a user setting; `using-git-worktrees` skips creation when already isolated and falls back to working in place on sandbox errors), so dev-flow creates, enters, and removes the worktree itself with plain git. Fixed path: `<main-root>/.claude/worktrees/dev-flow-<slug>`, where `<main-root>` is the first entry of `git worktree list --porcelain` (the main working tree). This location is deliberate: a fixed, git-ignored path every stage computes and addresses by absolute path — subagents operate on the worktree via `cd`/`git -C`, not harness worktree-entry (see the Enter step).

*Base ref (creation only).* Resolve the default branch mechanically: `git symbolic-ref --short refs/remotes/origin/HEAD` (strip `origin/`); if unset, `git remote set-head origin --auto` and retry; if there is no remote, use `main` if that ref exists, else `master`, else halt and report. Base off `origin/<default>` when it exists (after a best-effort `git fetch origin <default>`), else local `<default>`. Never branch from the invoking checkout's HEAD.

*Worktree entry — every stage dispatch runs this identically, first run and resume:*
1. **Locate:** in `git worktree list --porcelain`, the entry whose `branch` is `refs/heads/dev-flow/<slug>`; its `worktree <path>` is the pipeline worktree. (Git allows a branch in at most one worktree, so the match is unique.)
2. **Re-attach** if the branch exists but no worktree lists it (cleanup crash, manual removal): `git worktree add <path> dev-flow/<slug>` — no `-b`. Branch on origin only: `git fetch origin dev-flow/<slug>`, then `git worktree add <path> -b dev-flow/<slug> origin/dev-flow/<slug>` (upstream is set automatically).
3. **Create** if neither exists — legal only as Stage 1's first act (the resume table routes every other no-branch state to Design; any other stage landing here halts: contract violation). Ensure the container is ignored — add `.claude/worktrees/` to `<main-root>/.git/info/exclude` if absent (`grep -qxF '.claude/worktrees/' <exclude> || echo '.claude/worktrees/' >> <exclude>` — a local exclude, never a committed `.gitignore` edit, which would pollute the PR diff; grep the file rather than `git check-ignore`, which misfires on the not-yet-created directory) — then `git worktree add <path> -b dev-flow/<slug> <base>`. **If creation fails (sandbox/permission), halt and report; there is no work-in-place fallback.**
4. **Enter:** `cd <path>` and use absolute paths thereafter (harness worktree-entry — `EnterWorktree` — is not accepted from repo-root-pinned subagents, per the nested-review-fix probe; it would apply only if a future harness pins subagents inside a worktree). All stage work happens inside the worktree. The orchestrator itself stays in the main checkout — its resume reads are `git show dev-flow/<slug>:<file>`, branch listings, and `gh`, none of which need entry.
5. **Ensure runnable (stages that run code — Execute onward):** if project deps are absent (e.g. `package.json` with no `node_modules`), run standard project setup (npm install / cargo build / …). Design and Plan skip this. Living in entry rather than in any one stage means a resume landing at PR review or the merge gate in a re-created worktree still gets a working tree before any post-fix suite run.
6. **Dirty worktree on resume:** untracked scratch is ignored. Uncommitted *tracked* modifications: on an Execute landing, `git stash push -u -m "dev-flow/<slug>: pre-resume salvage"` and report the stash — resume position was derived from committed state, so the resumed task restarts clean and nothing is lost. On any later landing (PR review, merge gate), halt and report — that is work the pipeline doesn't understand.

**Execution-complete signal.** When a task's review comes back clean, tick that task's `- [ ]` checkboxes in the plan file and commit them, alongside SDD's ledger append. **Committed checkboxes are the durable, authoritative cross-session signal; SDD's `.superpowers/sdd/progress.md` ledger stays in-session scratch (it is git-ignored and dies with the worktree).** Execution is complete if and only if zero `- [ ]` remain in the plan at branch tip. Tie-break: if `git log` shows a task's commits but its boxes are unticked (a crash in the gap), verify via `git log`, tick the boxes, and do not re-implement.

**Review state.** After Stage 4's review has committed its fixes and the stage has pushed, post a PR comment with the marker line `dev-flow: review clean @ <full-head-sha>`. Detection: marker SHA equals the current head -> merge gate; stale SHA -> re-review (any push, including a CI fix, correctly invalidates the marker); no marker -> PR review. (A label can't carry the SHA and goes silently stale — rejected.)

**Resume table** (checks run top-to-bottom, first match wins; each is mechanical; "latest PR" = the highest-numbered result of `gh pr list --head dev-flow/<slug> --state all`):

| Check | Start at |
|---|---|
| No `dev-flow/<slug>` branch (local or origin); bare idea | Design: create branch+worktree, draft |
| No branch; existing design file given | Design: adopt (branch, front-matter, review — which commits) |
| Branch exists; latest PR is `MERGED` | Done — run Stage 5's Cleanup (idempotent), then report; nothing to resume |
| Branch exists; latest PR is `CLOSED` | Halt — a human closed PR #N without merging; report and hand back. Never silently re-create a PR over a human's close. |
| Branch exists; no design doc with `dev-flow` front-matter at tip | Design (redo; uncommitted drafts discarded) |
| Design committed at tip; no plan doc at tip | Plan |
| Plan at tip has ≥1 unchecked `- [ ]` | Execute — resume at first unchecked task (cross-check ledger + `git log`) |
| Plan fully checked; no PR for the branch (`--state all` list empty) | PR: create + review |
| Open PR; no `review clean @ <current head>` marker | PR review |
| Open PR; marker matches head | Merge gate (CI, `stops` from front-matter) |
| No row matches (e.g. resume with an unknown slug) | Nothing to resume — report it. If `gh pr list --head dev-flow/<slug> --state merged` shows a PR, say "already shipped (PR #N)"; else list `dev-flow/*` branches (local + origin) as candidates. |

---

## Pipeline

Each stage runs in a fresh `general-purpose` subagent (the subagent type verified to carry the `Agent` + `Skill` tools the nested review requires — see Environment Assumptions) carrying the inherited-skills preamble (see Dispatching to Inherited Skills, above), **begins with the worktree-entry procedure (Artifact Contract — the dispatch prompt names the slug, and all stage work happens inside the pipeline worktree)**, and returns only a short summary to the orchestrator.

### Stage 1 — Design

- **First act:** fix the slug, then create `dev-flow/<slug>` and its worktree per the worktree lifecycle (Artifact Contract): resolve the default branch, `git worktree add <main-root>/.claude/worktrees/dev-flow-<slug> -b dev-flow/<slug> <base>`, and enter it. Plain git, not a delegated skill — every resume check and the PR mapping key off that exact branch name and base, and no delegated mechanism guarantees either. Creation failure halts and reports.
- **Design-file entry:** adopt the given file — branch from main, copy the file into the worktree, stamp `dev-flow` front-matter, then review — which rewrites and commits.
- **Bare-idea entry:** produce a best-judgment design doc using the inlined non-interactive protocol below. **brainstorming is NOT invoked** — dialogue is its core mechanism, and this pipeline never lets a delegated skill talk to the user. Inline its non-interactive bones instead:
  1. Explore project context.
  2. Scope/decomposition check — if the idea spans independent subsystems, **halt and report** the proposed decomposition rather than forcing it through.
  3. Consider 2-3 approaches, pick one, and record the choice plus rejected alternatives and reasoning.
  4. Record defensible-default assumptions explicitly. A genuinely blocking ambiguity — one with no defensible default — is a halt-and-report, not a guess.
  5. Run brainstorming's spec self-review checklist (placeholders, consistency, scope, ambiguity).
- Run `dev-flow:adversarial-review` (mode: `design`) — it is the approval gate that substitutes for the user's. The review itself rewrites the design and commits it on the branch (its contract); the stage has no apply or commit step of its own.
- **Bare-idea entry defaults to a `post-design` stop** (see Stops, above).

### Stage 2 — Plan

- Spawn a subagent to run `superpowers:writing-plans` against the design, producing `docs/superpowers/plans/YYYY-MM-DD-<slug>-plan.md` (front-matter links the spec).
- Run `dev-flow:adversarial-review` (mode: `plan`). The review rewrites the plan and commits it on the branch; nothing to apply afterward.
- `post-plan` stop -> halt and report.

### Stage 3 — Execute

Dispatch to `superpowers:subagent-driven-development` with these overrides, per the inherited-skills rule:

- **Baseline:** worktree entry has already ensured setup (deps installed); run the baseline test suite before the first task. **A red baseline halts** — a CI-green merge gate can't be reached from a red baseline. (If SDD invokes `using-git-worktrees` itself, its Step-0 check finds the pipeline worktree and creates nothing — see Dispatching to Inherited Skills.)
- **Exit condition supersedes SDD's terminal:** last task complete, per-task reviews clean, full suite green, on the named branch. Do **not** run SDD's final whole-branch review; do **not** invoke `finishing-a-development-branch` (its interactive menu's option 1 is a local merge to base — the exact self-merge this pipeline exists to prevent). Report: branch, commit range, ledger path, and the ledger's unresolved Minor findings.
- **Pre-answers:** a plan-vs-code conflict is resolved by the **design doc** (the highest-reviewed artifact); if the design doc is silent, halt.
- **Halts:** SDD `BLOCKED` after its own ladder (more context / stronger model / split task) concluding "the plan itself is wrong" -> halt and report.
- **Bookkeeping:** on each task-review-clean, **dev-flow's execute-stage wrapper** (not SDD itself) ticks that task's plan checkboxes and commits them, alongside SDD's ledger append (see Artifact Contract).

### Stage 4 — PR

- `gh pr create`; PR body links the spec + plan paths and derives a summary from them. If an open PR already exists for the branch, reuse it — skip create.
- Run `dev-flow:adversarial-review` (mode: `diff`), passing Stage 3's unresolved Minor-findings list as caller-supplied findings. **This is the pipeline's final whole-branch review** (SDD's was suppressed in Stage 3). The review applies the resolved fixes, commits them on the branch, and (its contract) runs the project's test suite after fixing.
- **Post-fix test gate:** the marker may be posted only when the review reported the suite green — or reported that no automated suite exists (e.g. a prose-only repo). If for any reason the branch is red at head, halt; never post the marker on red. The marker therefore certifies **reviewed and suite-green (or no suite exists) at this exact SHA** — Stage 5 relies on this when a repo has no CI.
- Push the branch, then post the `dev-flow: review clean @ <full-head-sha>` marker comment.
- `pre-merge` stop -> halt and report (PR open, reviewed, fixes pushed) with the testing note and the resume invocation.

### Stage 5 — Merge

- Confirm the `review clean` marker SHA equals the current head (else re-review).
- **Bounded CI wait:** run `gh pr checks <pr> --watch` under a hard cap (default 10 minutes, enforced via the Bash tool's `timeout: 600000`, since `gh pr checks --watch` has no native timeout of its own). Exactly four outcomes — distinguish failure from no-checks by output text, not exit code (both exit 1; pending exits 8):
  - **All checks pass** -> proceed.
  - **Any check fails** -> halt and report.
  - **Still pending at the cap** -> halt and report "CI still pending" (resume re-enters the merge gate for free). Never an open-ended block.
  - **Output contains "no checks reported"** (the repo has no CI on this PR) -> proceed. This is safe only because the marker already certifies Stage 4's test gate — suite green at this head, or no suite exists. Never read "no checks" as a green test signal on its own.
- Consult `stops` from front-matter; a `pre-merge` stop pauses here with the testing note.
- **Merge:** `gh pr merge <pr> --squash` — deliberately **without** `--delete-branch`. The local branch is checked out in the pipeline worktree, and git refuses to delete a branch checked out in any worktree; gh's fallback (switch that worktree to the default branch first) also fails, because the default branch is checked out in the main worktree. Branch deletion belongs to Cleanup, below, where the ordering makes it work.
- **Cleanup (idempotent — the resume table's Done row runs this same block; every step treats "already gone" as success):**
  1. `cd` to the main repo root.
  2. Remove the pipeline-created worktree: find its path in `git worktree list --porcelain` (the entry whose `branch` is `refs/heads/dev-flow/<slug>`), then `git worktree remove <path>` and `git worktree prune`. The branch name is the provenance: worktree-only mode plus the intake collision check mean any worktree on `refs/heads/dev-flow/<slug>` is this feature's pipeline worktree — no separate provenance record exists or is needed. Ignored files (e.g. SDD's ledger) don't block removal; if stray *untracked* files do, they are scratch in a merged worktree — use `git worktree remove --force`. If tracked files have *uncommitted modifications*, halt and report instead — that is work the pipeline doesn't understand.
  3. Delete the local branch: `git branch -D dev-flow/<slug>`. It must be `-D` — after a squash merge the branch is never "fully merged" in ancestry terms, so `-d` always refuses — and it must come after step 2, because git refuses to delete a branch checked out in any worktree.
  4. Delete the remote branch: `git push origin --delete dev-flow/<slug>`; treat "remote ref does not exist" as success (GitHub's auto-delete-head-branches may have won the race).
- **Final report:** what shipped + every new issue filed across all stages.

---

## Environment Assumptions

- **Subagent nesting (required; enforced by the Capability gate).** The pipeline requires spawned subagents to hold `Agent` + `Skill`: a stage subagent invokes `dev-flow:adversarial-review` and spawns its seed/resolver agents, and Execute's SDD spawns implementers/reviewers. Verified working on Claude Code 2.1.217 — documentation, not enforcement, since the grant can be lost version-independently. Enforcement is the Capability gate (above), which halts at intake if the environment cannot nest; mid-run degradation is caught by the dispatch-preamble integrity clause and the provenance check (Cross-Cutting Concerns). There is **no** inline single-model fallback — a stage that cannot run the model-diverse review halts loudly. (The earlier "run the seed and group agents from the main session" fallback is removed: from inside a stage subagent it is unreachable — the entity that detects the missing tool cannot execute a main-session fallback — and its orchestrator-proactive form is the flatten design this approach rejected.)
- **GitHub remote** is assumed from Stage 4 onward (the pipeline uses `gh` for PR, review marker, CI, and merge). This matches the existing plugins' reliance on `gh`.

## Cross-Cutting Concerns

- **Context hygiene:** every stage and every review group runs in a fresh subagent; only short summaries return upward.
- **Review provenance is checked, not assumed.** Every stage that runs `dev-flow:adversarial-review` (Design, Plan, PR — not Execute) forwards the review's provenance line (`seeds: N× <tier>; resolvers: M× <tier>`) in its stage summary (per the dispatch preamble). The orchestrator halts if that line is missing or its tiers violate `dev-flow:adversarial-review`'s Model section (seeds must be the seed tier, resolvers the resolver tier; a `resolvers: 0` line from a no-findings review passes the resolver check vacuously). The tiers are already canonicalized by the review's family match, so this is a direct comparison — and the orchestrator is the only observer outside the stage subagent's context, which is what makes "the review really ran model-diverse" verifiable rather than assumed.
- **Failure handling:** a stage that cannot proceed cleanly halts and hands back with a clear report and resume invocation; the pipeline never merges work that is worse than what it started with.
- **Idempotent resume:** guaranteed by the Artifact Contract — every resume decision is a mechanical read of the branch tip or the PR.
- **Severity-independent, value-gated:** the protocol acts on issues of any severity but only applies a fix when it genuinely improves the codebase.
