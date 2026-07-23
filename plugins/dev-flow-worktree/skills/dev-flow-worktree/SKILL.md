---
name: dev-flow-worktree
description: Use when the user wants to run their end-to-end dev flow in an isolated git worktree — carry a change from design to plan to execute to PR to merge autonomously, with adversarial review at each stage. Triggers on "run dev-flow-worktree", "dev-flow-worktree on <design file>", "continue dev-flow-worktree on <slug>", or "take this design to a merged PR in a worktree".
---

# dev-flow-worktree

Carry a change from design -> plan -> execute -> PR -> merge in one invocation, isolated in a dedicated git worktree so your main checkout is never touched. Default is full-auto to merge; the user can opt into a stop at any artifact boundary. The orchestrator (main session) drives the pipeline directly and is the only agent that spawns — so the model-diverse review and the Execute loop work on any Claude Code version, with no nested subagent spawning. All state lives in durable artifacts (the Artifact Contract) so a run resumes cleanly after any stop or crash.

This is the only skill the user invokes. It calls the `dev-flow-worktree:adversarial-review` skill internally at each boundary; if the orchestrator cannot load that skill, it halts and reports — it never improvises a review inline.

## Invocation

Accept these forms:

```
# from a bare idea (defaults to stop-after-design — see Stops, below):
"run dev-flow-worktree: add rate limiting to the API gateway"

# from an existing design file (full-auto by default):
"run dev-flow-worktree on docs/superpowers/specs/2026-07-20-rate-limit-design.md"

# with an opt-in stop / resume:
"run dev-flow-worktree on <design>, but stop after the plan so I can review"
"continue dev-flow-worktree on rate-limit"
```

### Stops

There are exactly three stop boundaries:

| Stop | Effect |
|---|---|
| `post-design` | Halt after the design is reviewed, rewritten, and committed. |
| `post-plan` | Halt after the plan is reviewed, rewritten, and committed. |
| `pre-merge` | Run everything through the reviewed PR, then halt before `gh pr merge`. A testing note (what to check) is part of the halt report, not a separate state. |

- **Default:** none (full-auto to merge) for **design-file entry** — the file the user wrote is their approval. **Bare-idea entry defaults to `post-design`**: a bare idea is one giant unanswered design question, and full-auto-to-merge on a *guessed* design is the pipeline's worst failure mode. The user opts out with "full auto" or "no stops."
- **Persistence:** write stops into the design doc's `dev-flow-worktree` front-matter and commit them, so resume honors them.
- **Precedence:** an explicit stop given in *this* invocation beats a recorded front-matter stop, which beats the full-auto default. So "continue dev-flow-worktree on rate-limit" honors a recorded `pre-merge` stop; "continue to merge, no stops" clears it.
- Every halt report **prints the exact resume invocation** the user should run next.

## Model Policy

The orchestrator spawns produce-subagents and executors on the main session model, and does its own bookkeeping (checkbox commits, front-matter) inline. Reviewer-model selection — the orchestrator spawns the review's seed/resolver leaves directly, on a capable model different from the artifact's author — is owned by `dev-flow-worktree:adversarial-review` and stated once, in its Model section; that rule travels with the review skill wherever it is invoked.

## Model-availability gate (runs first, every invocation)

Before any drafting, resume routing, or stage work — on first run **and** every resume — the orchestrator confirms it can spawn the review's diverse models. No nested spawning is used anywhere in this pipeline; the orchestrator is the only spawner, so this is a one-level check:

1. Spawn one `sonnet` leaf and one `fable` leaf (or `opus` in a Fable-family session, per `dev-flow-worktree:adversarial-review`'s Model section), each returning the model its system prompt names and confirming it holds the `Skill` tool (produce-subagents need `Skill` to load their delegated skill).
2. If either fails to spawn, lacks `Skill`, or reports the wrong tier (by family match — e.g. a "Fable 5" report satisfies `fable`), **halt** with a report naming the missing capability — before any draft is written and later discarded on resume.

This is a hard, fail-fast gate: model availability can fail version-independently (permissions, `allowedTools`, alias changes). It does **not** probe nested spawning — that capability is neither present (removed in Claude Code 2.1.218) nor needed, since the orchestrator spawns every worker at one level.

## Dispatching to Inherited Skills

dev-flow-worktree delegates *produce* work to existing skills (`writing-plans`, the inlined `brainstorming` bones). Those skills contain user-facing decision points that have no answerer in a full-auto run. Carry the following rule as a standard preamble in **every produce-subagent** dispatch (Stages 1–2), so current and future inherited skills are handled correct-by-default. The orchestrator runs the *fan-out* skills — `adversarial-review` and `subagent-driven-development` — itself, in-context, and self-applies these rules directly (there is no dispatch prompt to carry them):

> **dev-flow-worktree never lets an inherited skill talk to the user.** Every user-facing decision point in a delegated skill is handled one of three ways: **(a) pre-answered** — the dispatch states the pipeline's answer as a declared preference; **(b) superseded** — the skill's terminal hand-off steps (integration menus, "what next" offers, follow-on skill invocations, final reviews) are replaced by the dispatch's explicit exit condition, because the pipeline owns all stage transitions; **(c) halted** — any user-directed question not covered by (a) or (b) is a blocker: the subagent stops and reports the question verbatim, and the orchestrator hands back. A subagent never invents an answer to an unanticipated gate. If a produce-subagent's `Skill` tool cannot load its delegated skill (e.g. `writing-plans`), halt and report — never improvise the artifact inline.

Corollaries:
- A skill whose **core mechanism is user dialogue** (`brainstorming`) cannot be dispatched at all — inline its non-interactive parts instead (see Stage 1).
- **Integration** (merge, or any push beyond the feature branch) happens only where a stage explicitly says so — never inside a delegated skill.
- **Red tests at any gate halt the pipeline** (baseline, stage exit, CI).
- **Worktrees are never delegated.** dev-flow-worktree owns the worktree lifecycle itself (see Artifact Contract) — no stage asks a skill to create one. If SDD invokes `superpowers:using-git-worktrees` internally (it lists it as a required workflow skill), that is safe by construction: the orchestrator is inside the pipeline worktree when it invokes SDD in-context, so that skill's Step-0 isolation check finds the pipeline worktree and creates nothing; its setup/baseline steps then land in the right workspace. Its "tests fail -> ask" gate is covered by the red-tests corollary above.
- This rule targets **user**-directed seams only; agent-to-agent interaction (e.g. SDD's controller answering its implementer) is untouched.

---

## Artifact Contract

State lives in artifacts, not a side file. **A dev-flow-worktree feature *is* its branch; every piece of pipeline state is either committed on that branch or attached to that branch's PR, and every resume decision is a mechanical read of one of those two places.**

**Slug.** Fix a kebab-case slug (2-4 words) once at intake — derive it from the design filename when one is given (`2026-07-20-rate-limit-design.md` -> `rate-limit`), else choose one from the idea. Treat it as an opaque, immutable ID: renaming the feature changes prose, never the slug. It threads through:

- spec: `docs/superpowers/specs/YYYY-MM-DD-<slug>-design.md`
- plan: `docs/superpowers/plans/YYYY-MM-DD-<slug>-plan.md`
- branch: `<username>/<slug>` (see Branch identity, below)
- PR: `gh pr list --head <username>/<slug> --state all` (branch->PR mapping is native to `gh`; branch existence is read per Branch identity's dual-prefix probe). Always pass `--state all` — the default listing is open-only and silently hides merged/closed PRs. "Latest PR" = the highest-numbered result.

**Branch identity.** The feature branch is `<username>/<slug>`.

- **`<username>` (resolve once per invocation).** `gh api user --jq .login` when it succeeds (GitHub remote reachable + `gh` authenticated); else a git fallback — the sanitized local-part of `git config user.email` (lowercase; every run of characters outside `[a-z0-9._-]` collapsed to a single `-`; leading/trailing `-` trimmed); else the same sanitization of `git config user.name`; if none yields a non-empty token, halt and report. Design and Plan therefore stay GitHub-free — the fallback needs no remote.
- **Deterministic lookup (resume-safe).** Because the resolver can pick a different source in different environments (gh login online, git email offline), every branch-existence read — the resume table, the intake collision check, and the PR mapping — probes **both** candidate prefixes, the gh-login prefix and the git-fallback prefix, and uses whichever `<prefix>/<slug>` actually exists as a local or origin branch or carries PR history. Branch uniqueness plus the intake collision check guarantee at most one exists; if both exist for *different* committed designs, halt and report the ambiguity. Branch **creation** uses the canonical resolver (gh-login else git-fallback). Once the branch exists, that resolved name is `<username>/<slug>` for the rest of the run.
- **Branch ownership (never adopt or delete a branch we didn't create).** `<username>/<slug>` is a namespace humans use by hand, so a branch of that name may be the user's own unrelated work — or a feature of the sibling `dev-flow` plugin (both plugins share this pattern). dev-flow-worktree owns a branch **iff** its tip carries this pipeline's design doc — `docs/superpowers/specs/*-<slug>-design.md` containing a `dev-flow-worktree:` front-matter block. The only other state it may treat as its own is a branch with **no commits beyond `<base>`** (an empty branch it just created, before Design committed). A branch that has commits beyond `<base>` but does **not** carry our design at tip is **foreign**: never adopt it (no redo-Design), never open a PR from it, and never delete it (Cleanup skips it) — **halt and report** so the user renames the slug or removes the branch. This single predicate gates the intake collision check, the resume table's no-design row, and Cleanup below; it is what replaces the exclusivity the old `dev-flow/<slug>` prefix gave for free.

Intake collision check: before creating `<username>/<slug>`, if it already exists (local or origin) and is **foreign** (per Branch ownership), qualify the new slug (append a disambiguator) or halt — never build on it (and `git worktree add -b` would fail outright on an existing branch anyway); if it already carries our design, this is a resume, routed by the resume table. Also qualify if no branch exists but `gh pr list --head <username>/<slug> --state all` is non-empty — a slug whose PR history belongs to an earlier shipped feature is retired, so the resume table's PR-state reads stay unambiguous forever. (This replaces fuzzy topic-matching with mechanical existence checks.)

**Front-matter (the only new schema).** Design doc:

```yaml
---
dev-flow-worktree:
  slug: rate-limit
  stops: [post-plan, pre-merge]   # [] = full-auto to merge
---
```

Plan doc: `dev-flow-worktree: {slug: rate-limit, spec: docs/superpowers/specs/2026-07-20-rate-limit-design.md}` (linkage only). **Stops live solely in the design doc.** The PR body links both doc paths. `dev-flow-worktree:adversarial-review` preserves front-matter on every rewrite (part of its contract), so this block survives all reviews.

**Doc git lifecycle — branch + worktree at design start.** Creating `<username>/<slug>` and its worktree is the *first* act of Stage 1 (the Create step of the worktree lifecycle, below; design and plan only need a checkout — setup is ensured at entry from Execute onward). Write and commit all docs **in the worktree, on the branch**. A doc's content is committed **only by `dev-flow-worktree:adversarial-review`, as the final step of its rewrite** — so "doc committed at tip" is equivalent to "stage complete" by construction, which removes the need for any separate "reviewed" marker on docs. (dev-flow-worktree itself commits only pipeline-state edits: front-matter `stops` updates and plan-checkbox ticks.) Adopt-existing-file entry: branch from main, copy the file in, stamp front-matter, then review — the review rewrites and commits. On every halt/stop, push the branch if a remote exists. dev-flow-worktree always runs in a dedicated worktree — there is no "work in the main checkout" mode.

**Worktree lifecycle — owned by dev-flow-worktree, plain git.** The contract stakes everything on one invariant: *a worktree on a branch named exactly `<username>/<slug>`, based off the default branch, always exists and is findable by every stage.* No delegated mechanism guarantees that (native tools auto-name branches and take their base from a user setting; `using-git-worktrees` skips creation when already isolated and falls back to working in place on sandbox errors), so dev-flow-worktree creates, enters, and removes the worktree itself with plain git. Fixed path: `<main-root>/.claude/worktrees/dev-flow-<slug>`, where `<main-root>` is the first entry of `git worktree list --porcelain` (the main working tree). This location is deliberate: a fixed, git-ignored path every stage computes and addresses by absolute path — subagents operate on the worktree via `cd`/`git -C`, not harness worktree-entry (see the Enter step).

*Base ref (creation only).* Resolve the default branch mechanically: `git symbolic-ref --short refs/remotes/origin/HEAD` (strip `origin/`); if unset, `git remote set-head origin --auto` and retry; if there is no remote, use `main` if that ref exists, else `master`, else halt and report. Base off `origin/<default>` when it exists (after a best-effort `git fetch origin <default>`), else local `<default>`. Never branch from the invoking checkout's HEAD.

*Worktree entry — the orchestrator runs this at each stage boundary, first run and resume:*
1. **Locate:** in `git worktree list --porcelain`, the entry whose `branch` is `refs/heads/<username>/<slug>`; its `worktree <path>` is the pipeline worktree. (Git allows a branch in at most one worktree, so the match is unique.)
2. **Re-attach** if the branch exists but no worktree lists it (cleanup crash, manual removal): `git worktree add <path> <username>/<slug>` — no `-b`. Branch on origin only: `git fetch origin <username>/<slug>`, then `git worktree add <path> -b <username>/<slug> origin/<username>/<slug>` (upstream is set automatically).
3. **Create** if neither exists — legal only as Stage 1's first act (the resume table routes every other no-branch state to Design; any other stage landing here halts: contract violation). Ensure the container is ignored — add `.claude/worktrees/` to `<main-root>/.git/info/exclude` if absent (`grep -qxF '.claude/worktrees/' <exclude> || echo '.claude/worktrees/' >> <exclude>` — a local exclude, never a committed `.gitignore` edit, which would pollute the PR diff; grep the file rather than `git check-ignore`, which misfires on the not-yet-created directory) — then `git worktree add <path> -b <username>/<slug> <base>`. **If creation fails (sandbox/permission), halt and report; there is no work-in-place fallback.**
4. **Enter:** the orchestrator routes the resume table from the main checkout (reads via `git show <username>/<slug>:<file>`, branch listings, and `gh` — none need entry), then `cd`s into the worktree to *drive* **every stage command whose git/`gh` target derives from cwd or the current branch** — an `adversarial-review` invocation, the Execute SDD loop, and **Stage 4's `gh pr create`, the branch push on any halt/stop, and the `review clean` marker-SHA read** — so all of it (baseline/per-task suites, `HEAD`-relative commands, the review's post-fix suite, PR creation and push) runs against the pipeline tree and branch; it `cd`s back to main only for routing reads. (Any such command that must run from main instead names its target explicitly: `--head <username>/<slug>`, `git push origin <username>/<slug>`, `git rev-parse <username>/<slug>`.) Spawned leaves are pinned to the repo root and cannot inherit cwd, so each is handed the absolute worktree path explicitly: `adversarial-review` via its `working-dir` argument (write-side fixers use `git -C <path>`), and **every** SDD dispatch — implementers, fixers, and task-reviewers — via its `Work from:` field, so any commit, focused test, git fallback, or changed-file Read runs against the pipeline tree (each `cd`s there first; a bare `git commit` would land on the main checkout's branch). Harness worktree-entry (`EnterWorktree`) is not used — the nested-review-fix probe found it rejected from repo-root-pinned subagents (see the flatten design's Evidence).
5. **Ensure runnable (stages that run code — Execute onward):** if project deps are absent (e.g. `package.json` with no `node_modules`), run standard project setup (npm install / cargo build / …). Design and Plan skip this. Living in entry rather than in any one stage means a resume landing at PR review or the merge gate in a re-created worktree still gets a working tree before any post-fix suite run.
6. **Dirty worktree on resume:** untracked scratch is ignored. Uncommitted *tracked* modifications: on an Execute landing, `git stash push -u -m "<username>/<slug>: pre-resume salvage"` and report the stash — resume position was derived from committed state, so the resumed task restarts clean and nothing is lost. On any later landing (PR review, merge gate), halt and report — that is work the pipeline doesn't understand.

**Execution-complete signal.** When a task's review comes back clean, the orchestrator (SDD's controller) ticks that task's `- [ ]` checkboxes in the plan file and commits them, alongside SDD's ledger append. **Committed checkboxes are the durable, authoritative cross-session signal; SDD's `.superpowers/sdd/progress.md` ledger stays in-session scratch (it is git-ignored and dies with the worktree).** Execution is complete if and only if zero `- [ ]` remain in the plan at branch tip. Tie-break: if `git log` shows a task's commits but its boxes are unticked (a crash in the gap), verify via `git log`, tick the boxes, and do not re-implement.

**Review state.** After Stage 4's review has committed its fixes and the stage has pushed, post a PR comment with the marker line `dev-flow-worktree: review clean @ <full-head-sha>`. Detection: marker SHA equals the current head -> merge gate; stale SHA -> re-review (any push, including a CI fix, correctly invalidates the marker); no marker -> PR review. (A label can't carry the SHA and goes silently stale — rejected.)

**Resume table** (checks run top-to-bottom, first match wins; each is mechanical; "latest PR" = the highest-numbered result of `gh pr list --head <username>/<slug> --state all`):

| Check | Start at |
|---|---|
| No `<username>/<slug>` branch (local or origin); bare idea | Design: create branch+worktree, draft |
| No branch; existing design file given | Design: adopt (branch, front-matter, review — which commits) |
| Branch exists; latest PR is `MERGED` | Done — run Stage 5's Cleanup (idempotent), then report; nothing to resume |
| Branch exists; latest PR is `CLOSED` | Halt — a human closed PR #N without merging; report and hand back. Never silently re-create a PR over a human's close. |
| Branch exists; no design doc with `dev-flow-worktree` front-matter at tip | **Foreign** (has commits beyond `<base>`, per Branch ownership) -> **Halt** — never adopt or delete a branch we didn't create. **Empty beyond `<base>`** (our just-created branch, Design crashed before committing) -> Design (redo; uncommitted drafts discarded) |
| Design committed at tip; no plan doc at tip | Plan |
| Plan at tip has ≥1 unchecked `- [ ]` | Execute — resume at first unchecked task (cross-check ledger + `git log`) |
| Plan fully checked; no PR for the branch (`--state all` list empty) | PR: create + review |
| Open PR; no `review clean @ <current head>` marker | PR review |
| Open PR; marker matches head | Merge gate (CI, `stops` from front-matter) |
| No row matches (e.g. resume with an unknown slug) | Nothing to resume — report it. If `gh pr list --head <username>/<slug> --state merged` shows a PR, say "already shipped (PR #N)"; else list `<username>/*` branches (local + origin, both candidate prefixes) as candidates. |

---

## Pipeline

The orchestrator drives every stage, running the worktree-entry procedure (Artifact Contract) at each boundary. Exploratory *produce* work (bare-idea design drafting, `writing-plans`) runs in a fresh `general-purpose` produce-subagent — a leaf carrying the inherited-skills preamble (see Dispatching to Inherited Skills, above) that writes its draft into the worktree by absolute path and returns a short summary. All *fan-out* work — every `adversarial-review` invocation and the Execute SDD loop — the orchestrator runs itself, in-context, from inside the worktree. Only leaf subagents are ever spawned; no subagent spawns a subagent.

### Stage 1 — Design

- **First act:** fix the slug, then create `<username>/<slug>` and its worktree per the worktree lifecycle (Artifact Contract): resolve the default branch, `git worktree add <main-root>/.claude/worktrees/dev-flow-<slug> -b <username>/<slug> <base>`, and enter it. Plain git, not a delegated skill — every resume check and the PR mapping key off that exact branch name and base, and no delegated mechanism guarantees either. Creation failure halts and reports.
- **Design-file entry:** adopt the given file — branch from main, copy the file into the worktree, stamp `dev-flow-worktree` front-matter, then review — which rewrites and commits.
- **Bare-idea entry:** the orchestrator dispatches a produce-subagent to draft a best-judgment design doc (written into the worktree by absolute path) using the inlined non-interactive protocol below. **brainstorming is NOT invoked** — dialogue is its core mechanism, and this pipeline never lets a delegated skill talk to the user. Inline its non-interactive bones instead:
  1. Explore project context.
  2. Scope/decomposition check — if the idea spans independent subsystems, **halt and report** the proposed decomposition rather than forcing it through.
  3. Consider 2-3 approaches, pick one, and record the choice plus rejected alternatives and reasoning.
  4. Record defensible-default assumptions explicitly. A genuinely blocking ambiguity — one with no defensible default — is a halt-and-report, not a guess.
  5. Run brainstorming's spec self-review checklist (placeholders, consistency, scope, ambiguity).
- The **orchestrator** invokes `dev-flow-worktree:adversarial-review` (mode: `design`) in-context from inside the worktree, passing the worktree as `working-dir` — it is the approval gate that substitutes for the user's. The review rewrites the design and commits it on the branch (its contract); the orchestrator then checks the returned provenance line (Cross-Cutting Concerns) before proceeding. No separate apply or commit step.
- **Bare-idea entry defaults to a `post-design` stop** (see Stops, above).

### Stage 2 — Plan

- Spawn a subagent to run `superpowers:writing-plans` against the design, producing `docs/superpowers/plans/YYYY-MM-DD-<slug>-plan.md` (front-matter links the spec).
- The **orchestrator** invokes `dev-flow-worktree:adversarial-review` (mode: `plan`) in-context (worktree as `working-dir`); the review rewrites the plan and commits it on the branch; the orchestrator checks the provenance line. Nothing to apply afterward.
- `post-plan` stop -> halt and report.

### Stage 3 — Execute

The **orchestrator** invokes `superpowers:subagent-driven-development` directly (in-context, cwd = worktree) — it *is* SDD's controller and spawns the implementer/reviewer leaves itself (one level). No execute-stage-subagent wrapper. The orchestrator self-applies these overrides (there is no dispatch prompt to carry them):

- **Baseline:** worktree entry has already ensured setup (deps installed); run the baseline test suite before the first task. **A red baseline halts** — a CI-green merge gate can't be reached from a red baseline. (If SDD invokes `using-git-worktrees` itself, its Step-0 check finds the pipeline worktree and creates nothing — see Dispatching to Inherited Skills.)
- **Exit condition supersedes SDD's terminal:** last task complete, per-task reviews clean, full suite green, on the named branch. Do **not** run SDD's final whole-branch review; do **not** invoke `finishing-a-development-branch` (its interactive menu's option 1 is a local merge to base — the exact self-merge this pipeline exists to prevent). Report: branch, commit range, ledger path, and the ledger's unresolved Minor findings.
- **Pre-answers:** a plan-vs-code conflict is resolved by the **design doc** (the highest-reviewed artifact); if the design doc is silent, halt.
- **Halts:** SDD `BLOCKED` after its own ladder (more context / stronger model / split task) concluding "the plan itself is wrong" -> halt and report.
- **Bookkeeping:** on each task-review-clean, the **orchestrator** (SDD's controller — not SDD's own templates) ticks that task's plan checkboxes and commits them in the worktree, alongside SDD's ledger append (see Artifact Contract).

### Stage 4 — PR

- `gh pr create`; PR body links the spec + plan paths and derives a summary from them. If an open PR already exists for the branch, reuse it — skip create.
- The **orchestrator** invokes `dev-flow-worktree:adversarial-review` (mode: `diff`) in-context (worktree as `working-dir`), passing Stage 3's unresolved Minor-findings list as caller-supplied findings. **This is the pipeline's final whole-branch review** (SDD's was suppressed in Stage 3). The review applies the resolved fixes, commits them on the branch, and (its contract) runs the project's test suite after fixing — from inside the worktree, so it tests the pipeline tree. The orchestrator checks the provenance line.
- **Post-fix test gate:** the marker may be posted only when the review reported the suite green — or reported that no automated suite exists (e.g. a prose-only repo). If for any reason the branch is red at head, halt; never post the marker on red. The marker therefore certifies **reviewed and suite-green (or no suite exists) at this exact SHA** — Stage 5 relies on this when a repo has no CI.
- Push the branch, then post the `dev-flow-worktree: review clean @ <full-head-sha>` marker comment.
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
  2. Remove the pipeline-created worktree: find its path in `git worktree list --porcelain` (the entry whose `branch` is `refs/heads/<username>/<slug>`), then `git worktree remove <path>` and `git worktree prune`. The provenance is the worktree's fixed path under `<main-root>/.claude/worktrees/dev-flow-<slug>` together with its branch: worktree-only mode plus the intake collision check mean the worktree on `refs/heads/<username>/<slug>` at that path is this feature's pipeline worktree — no separate provenance record exists or is needed. Ignored files (e.g. SDD's ledger) don't block removal; if stray *untracked* files do, they are scratch in a merged worktree — use `git worktree remove --force`. If tracked files have *uncommitted modifications*, halt and report instead — that is work the pipeline doesn't understand.
  3. Delete the local branch — **only if it is ours** (its history carries our design doc, per Branch ownership; a legitimately merged feature always does, so this guard only ever refuses a branch the pipeline never owned): `git branch -D <username>/<slug>`. It must be `-D` — after a squash merge the branch is never "fully merged" in ancestry terms, so `-d` always refuses — and it must come after step 2, because git refuses to delete a branch checked out in any worktree.
  4. Delete the remote branch (same branch, ownership confirmed in step 3): `git push origin --delete <username>/<slug>`; treat "remote ref does not exist" as success (GitHub's auto-delete-head-branches may have won the race).
- **Final report:** what shipped + every new issue filed across all stages.

---

## Environment Assumptions

- **Flat topology — the orchestrator is the only spawner.** Every subagent dev-flow-worktree spawns is a leaf; no subagent spawns a subagent. This is required, not a preference: **Claude Code 2.1.218 does not grant spawned subagents the `Agent` tool** (nested spawning was removed; the harness's recommended pattern is top-level orchestration only). So the orchestrator invokes every fan-out skill (`dev-flow-worktree:adversarial-review`, `subagent-driven-development`) in-context and spawns their worker leaves itself — always one level, works on every version. The intake gate above checks model *availability*, not nesting. (Nesting worked on 2.1.217 and was relied on by this plugin's 1.1.0; the 2.1.218 removal is why 1.2.0 flattened.)
- **GitHub remote** is assumed from Stage 4 onward (the pipeline uses `gh` for PR, review marker, CI, and merge). This matches the existing plugins' reliance on `gh`. (The `<username>` resolver *prefers* `gh api user` when a remote is reachable but falls back to git config, so Design and Plan still run with no remote.)

## Cross-Cutting Concerns

- **Context hygiene:** produce-subagents and every spawned review/implementer leaf run in fresh subagents returning short summaries; the orchestrator holds the fan-out controllers' state directly (the review's group loop, SDD's task loop), bounded by file handoffs and summaries and recoverable via resume.
- **Review provenance is checked, not assumed.** The orchestrator runs each review (Design, Plan, PR — not Execute) in-context, then reads the review's returned provenance line (`seeds: N× <tier>; resolvers: M× <tier>`) directly and halts if it is missing or its tiers violate `dev-flow-worktree:adversarial-review`'s Model section (seeds must be the seed tier, resolvers the resolver tier; a `resolvers: 0` line from a no-findings review passes the resolver check vacuously). The tiers are canonicalized by the review's family match, so this is a direct comparison — a cheap self-check that the review actually spawned diverse reviewers.
- **Failure handling:** a stage that cannot proceed cleanly halts and hands back with a clear report and resume invocation; the pipeline never merges work that is worse than what it started with.
- **Idempotent resume:** guaranteed by the Artifact Contract — every resume decision is a mechanical read of the branch tip or the PR.
- **Severity-independent, value-gated:** the protocol acts on issues of any severity but only applies a fix when it genuinely improves the codebase.
