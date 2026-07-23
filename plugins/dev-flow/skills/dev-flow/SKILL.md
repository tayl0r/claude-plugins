---
name: dev-flow
description: Use when the user wants to run their end-to-end dev flow — carry a change from design to plan to execute to PR to merge autonomously, with adversarial review at each stage. Triggers on "run dev-flow", "run my dev flow", "dev-flow on <design file>", "continue dev-flow on <slug>", or "take this design to a merged PR".
---

# dev-flow

Carry a change from design -> plan -> execute -> PR -> merge in one invocation. The pipeline works directly on a dedicated feature branch in your current checkout (no worktree). Default is full-auto to merge; the user can opt into a stop at any artifact boundary. The orchestrator (main session) drives the pipeline directly and is the only agent that spawns — so the model-diverse review and the Execute loop work on any Claude Code version, with no nested subagent spawning. All state lives in durable artifacts (the Artifact Contract) so a run resumes cleanly after any stop or crash.

This is the only skill the user invokes. It calls the `dev-flow:adversarial-review` skill internally at each boundary; if the orchestrator cannot load that skill, it halts and reports — it never improvises a review inline.

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
- The **dirty-checkout gate** (Artifact Contract) is **not** a stop: it is an in-turn precondition prompt (proceed / stash / revert) resolved immediately, persists nothing to front-matter, and is not a resume boundary. "Exactly three stop boundaries" and "every halt report prints a resume invocation" describe the pipeline's *stop* boundaries — the gate is a separate, self-resolving interaction (see its corollary under Dispatching to Inherited Skills).

## Model Policy

The orchestrator spawns produce-subagents and executors on the main session model, and does its own bookkeeping (checkbox commits, front-matter) inline. Reviewer-model selection — the orchestrator spawns the review's seed/resolver leaves directly, on a capable model different from the artifact's author — is owned by `dev-flow:adversarial-review` and stated once, in its Model section; that rule travels with the review skill wherever it is invoked.

## Model-availability gate (runs first, every invocation)

Before any drafting, resume routing, or stage work — on first run **and** every resume — the orchestrator confirms it can spawn the review's diverse models. No nested spawning is used anywhere in this pipeline; the orchestrator is the only spawner, so this is a one-level check:

1. Spawn one `sonnet` leaf and one `fable` leaf (or `opus` in a Fable-family session, per `dev-flow:adversarial-review`'s Model section), each returning the model its system prompt names and confirming it holds the `Skill` tool (produce-subagents need `Skill` to load their delegated skill).
2. If either fails to spawn, lacks `Skill`, or reports the wrong tier (by family match — e.g. a "Fable 5" report satisfies `fable`), **halt** with a report naming the missing capability — before any draft is written and later discarded on resume.

This is a hard, fail-fast gate: model availability can fail version-independently (permissions, `allowedTools`, alias changes). It does **not** probe nested spawning — that capability is neither present (removed in Claude Code 2.1.218) nor needed, since the orchestrator spawns every worker at one level.

## Dispatching to Inherited Skills

dev-flow delegates *produce* work to existing skills (`writing-plans`, the inlined `brainstorming` bones). Those skills contain user-facing decision points that have no answerer in a full-auto run. Carry the following rule as a standard preamble in **every produce-subagent** dispatch (Stages 1–2), so current and future inherited skills are handled correct-by-default. The orchestrator runs the *fan-out* skills — `adversarial-review` and `subagent-driven-development` — itself, in-context, and self-applies these rules directly (there is no dispatch prompt to carry them):

> **dev-flow never lets an inherited skill talk to the user.** Every user-facing decision point in a delegated skill is handled one of three ways: **(a) pre-answered** — the dispatch states the pipeline's answer as a declared preference; **(b) superseded** — the skill's terminal hand-off steps (integration menus, "what next" offers, follow-on skill invocations, final reviews) are replaced by the dispatch's explicit exit condition, because the pipeline owns all stage transitions; **(c) halted** — any user-directed question not covered by (a) or (b) is a blocker: the subagent stops and reports the question verbatim, and the orchestrator hands back. A subagent never invents an answer to an unanticipated gate. If a produce-subagent's `Skill` tool cannot load its delegated skill (e.g. `writing-plans`), halt and report — never improvise the artifact inline.

Corollaries:
- A skill whose **core mechanism is user dialogue** (`brainstorming`) cannot be dispatched at all — inline its non-interactive parts instead (see Stage 1).
- **Integration** (merge, or any push beyond the feature branch) happens only where a stage explicitly says so — never inside a delegated skill.
- **Red tests at any gate halt the pipeline** (baseline, stage exit, CI).
- **Isolation is the feature branch, not a worktree.** dev-flow does not use git worktrees — it checks the `<username>/<slug>` branch out in your current working directory and works there (see Artifact Contract). No stage creates a worktree. SDD lists `superpowers:using-git-worktrees` as a required workflow skill; dev-flow satisfies it through **that skill's own Step-0 seam** rather than by relying on the orchestrator to intercept it: dev-flow declares the worktree preference Step 0 reads — *work in place in the current checkout; do not create a worktree* — which Step 0 honors **without prompting** (its "honor any existing declared preference without asking" / "declines consent → work in place → Step 2" path). So `using-git-worktrees`, wherever it runs, does project setup in place and never asks the user; the feature branch is the isolation. Its "tests fail -> ask" gate is covered by the red-tests corollary above.
- The one deliberate exception to "never talk to the user" is the **dirty-checkout gate** (Artifact Contract): before switching your checkout onto the feature branch, the orchestrator itself asks how to handle your pre-existing uncommitted changes. That is your own work and your call — not a delegated skill improvising.
- This rule targets **user**-directed seams only; agent-to-agent interaction (e.g. SDD's controller answering its implementer) is untouched.

---

## Artifact Contract

State lives in artifacts, not a side file. **A dev-flow feature *is* its branch; every piece of pipeline state is either committed on that branch or attached to that branch's PR, and every resume decision is a mechanical read of one of those two places.**

**Slug.** Fix a short kebab-case slug once at intake — derive it from the design filename when one is given (`2026-07-20-rate-limit-design.md` -> `rate-limit`), else choose one from the idea. **If the run references a task/issue ID — a Linear or Jira key like `ENG-1421`, or a GitHub issue like `#42` — fold it into the slug as a lowercased kebab prefix: `<ticket>-<topic>` (e.g. `eng-1421-rate-limit`, `gh-42-rate-limit`).** The ID comes from the invocation (you name it) or the design doc; because it lives inside the opaque slug it threads through the branch, filenames, and PR unchanged — giving ticket traceability and making accidental branch collisions rarer (never impossible, though: humans use ticket-prefixed branch names too, which is why Branch ownership, below, is the actual safety guard, not the naming). Treat the slug as an opaque, immutable ID: renaming the feature changes prose, never the slug. It threads through:

- spec: `docs/superpowers/specs/YYYY-MM-DD-<slug>-design.md`
- plan: `docs/superpowers/plans/YYYY-MM-DD-<slug>-plan.md`
- branch: `<username>/<slug>` (see Branch identity, below)
- PR: `gh pr list --head <username>/<slug> --state all` (branch->PR mapping is native to `gh`; branch existence is read per Branch identity's dual-prefix probe). Always pass `--state all` — the default listing is open-only and silently hides merged/closed PRs. "Latest PR" = the highest-numbered result.

**Branch identity.** The feature branch is `<username>/<slug>`.

- **`<username>` (resolve once per invocation).** `gh api user --jq .login` when it succeeds (GitHub remote reachable + `gh` authenticated); else a git fallback — the sanitized local-part of `git config user.email` (lowercase; every run of characters outside `[a-z0-9._-]` collapsed to a single `-`; leading/trailing `-` trimmed); else the same sanitization of `git config user.name`; if none yields a non-empty token, halt and report. Design and Plan therefore stay GitHub-free — the fallback needs no remote.
- **Deterministic lookup (resume-safe).** Because the resolver can pick a different source in different environments (gh login online, git email offline), every branch-existence read — the resume table, the intake collision check, and the PR mapping — probes **both** candidate prefixes, the gh-login prefix and the git-fallback prefix, and uses whichever `<prefix>/<slug>` actually exists as a local or origin branch or carries PR history. Branch uniqueness plus the intake collision check guarantee at most one exists; if both exist for *different* committed designs, halt and report the ambiguity. Branch **creation** uses the canonical resolver (gh-login else git-fallback). Once the branch exists, that resolved name is `<username>/<slug>` for the rest of the run.
- **Branch ownership (never adopt or delete a branch we didn't create).** `<username>/<slug>` is a namespace humans use by hand, so a branch of that name may be the user's own unrelated work — or a feature of the sibling `dev-flow-worktree` plugin (both plugins share this pattern). dev-flow owns a branch **iff** its tip carries this pipeline's design doc — `docs/superpowers/specs/*-<slug>-design.md` containing a `dev-flow:` front-matter block. The only other state dev-flow may treat as its own is a branch with **no commits beyond `<base>`** (an empty branch it just created, before Design committed). A branch that has commits beyond `<base>` but does **not** carry our design at tip is **foreign**: never adopt it (no redo-Design) and never open a PR from it — **halt and report** so the user renames the slug or removes the branch. This predicate gates the intake collision check and the resume table's no-design row; it replaces the exclusivity the old `dev-flow/<slug>` prefix gave for free. (The pipeline itself deletes no branches — see Stage 5 — so the only thing to guard is *building on* a branch that isn't ours, never destroying one.)

Intake collision check: before creating `<username>/<slug>`, if it already exists (local or origin) and is **foreign** (per Branch ownership), qualify the new slug (append a disambiguator) or halt — never build on it; if it already carries our design, this is a resume, routed by the resume table. Also qualify if no branch exists but `gh pr list --head <username>/<slug> --state all` is non-empty — a slug whose PR history belongs to an earlier shipped feature is retired, so the resume table's PR-state reads stay unambiguous forever. (This replaces fuzzy topic-matching with mechanical existence checks.)

**Front-matter (the only new schema).** Design doc:

```yaml
---
dev-flow:
  slug: rate-limit
  stops: [post-plan, pre-merge]   # [] = full-auto to merge
---
```

Plan doc: `dev-flow: {slug: rate-limit, spec: docs/superpowers/specs/2026-07-20-rate-limit-design.md}` (linkage only). **Stops live solely in the design doc.** The PR body links both doc paths. `dev-flow:adversarial-review` preserves front-matter on every rewrite (part of its contract), so this block survives all reviews.

**Doc git lifecycle — branch at design start.** Creating `<username>/<slug>` and checking it out in your working directory is the *first* act of Stage 1 (the Create step of the branch lifecycle, below; design and plan only need the branch checked out — runnable setup is ensured at entry from Execute onward). Write and commit all docs **on the branch, in your checkout**. A doc's content is committed **only by `dev-flow:adversarial-review`, as the final step of its rewrite** — so "doc committed at tip" is equivalent to "stage complete" by construction, which removes the need for any separate "reviewed" marker on docs. (dev-flow itself commits only pipeline-state edits: front-matter `stops` updates and plan-checkbox ticks.) Adopt-existing-file entry: branch from main, copy the file in, stamp front-matter, then review — the review rewrites and commits. On every halt/stop, push the branch if a remote exists.

**Branch lifecycle — owned by dev-flow, plain git.** The contract stakes everything on one invariant: *a branch named exactly `<username>/<slug>`, based off the default branch, exists and is checked out in your working directory whenever a stage runs.* No delegated mechanism guarantees that (native worktree tools auto-name branches and take their base from a user setting), so dev-flow creates and checks out the branch itself with plain git. Because the branch is checked out in the repo root itself, every command — the orchestrator's own and every spawned leaf's (leaves are pinned to the repo root and cannot inherit cwd) — runs against it by default; the cwd-inheritance problem a separate worktree would create simply does not arise, so no `working-dir` argument, no `Work from:` field, and no absolute-path threading is needed anywhere in this pipeline.

*Base ref (creation only).* Resolve the default branch mechanically: `git symbolic-ref --short refs/remotes/origin/HEAD` (strip `origin/`); if unset, `git remote set-head origin --auto` and retry; if there is no remote, use `main` if that ref exists, else `master`, else halt and report. Base off `origin/<default>` when it exists (after a best-effort `git fetch origin <default>`), else local `<default>`. Never branch from the invoking checkout's HEAD.

*Branch entry — the orchestrator runs this at each stage boundary, first run and resume:*
1. **Already there:** if the current branch is `<username>/<slug>`, no switch is needed — skip to step 5 (ensure runnable) / step 6 (resume dirtiness).
2. **Dirty-checkout gate (before any switch).** A switch onto the feature branch — creating it (step 3) or checking it out (step 4) — first inspects `git status --porcelain` (which already excludes git-ignored files). If it reports **anything** — tracked modifications, staged changes, or untracked non-ignored files — the orchestrator **halts and asks the user** how to proceed with those pre-existing changes, offering exactly three choices, then acts and switches:
   - **proceed as-is** — carry the changes into the working tree onto the feature branch. If git reports the switch would overwrite or conflict, they cannot be cleanly carried: re-present *stash* / *revert*. These carried changes stay **uncommitted** and are **not pipeline state** — the Artifact Contract's "committed or on the PR" guarantee covers only what the pipeline itself commits. dev-flow never deliberately commits them, but it cannot stop an Execute-stage implementer's broad `git add` from sweeping in files it touches, so choose this **only for changes on paths unrelated to the feature**; otherwise prefer *stash*. This is the one category of pre-existing uncommitted state the pipeline knowingly tolerates (at the user's explicit direction); step 6's stricter treatment governs uncommitted state that appears *after* the pipeline has taken over.
   - **stash** — `git stash push -u -m "<username>/<slug>: pre-switch stash"` (the `-u` also stashes untracked non-ignored files), **report the stash ref**, then switch. The user restores it later with `git stash pop`.
   - **revert** — discard the changes (`git reset --hard` and, for untracked non-ignored files, `git clean -fd`), then switch. Destructive — only on explicit choice.
   If `git status --porcelain` is empty, switch directly. This gate is the price of working in your shared checkout instead of an isolated worktree; it is the only place the orchestrator itself asks the user a question mid-run.
3. **Create** if the branch exists nowhere (per Branch identity's dual-prefix probe) — legal only as Stage 1's first act (the resume table routes every other no-branch state to Design; any other stage landing here halts: contract violation). `git switch -c <username>/<slug> <base>`.
4. **Checkout** if the branch exists: local -> `git switch <username>/<slug>`; origin only -> `git fetch origin <username>/<slug>` then `git switch -c <username>/<slug> --track origin/<username>/<slug>`.
5. **Ensure runnable (stages that run code — Execute onward):** if project deps are absent (e.g. `package.json` with no `node_modules`), run standard project setup (npm install / cargo build / …). Design and Plan skip this. Living in entry rather than in any one stage means a resume landing at PR review or the merge gate still gets a working tree before any post-fix suite run.
6. **Dirty working tree on resume (already on the branch — pipeline's own mid-task state, not a switch):** untracked scratch is ignored. Uncommitted *tracked* modifications: on an Execute landing, `git stash push -u -m "<username>/<slug>: pre-resume salvage"` and report the stash — resume position was derived from committed state, so the resumed task restarts clean and nothing is lost. On any later landing (PR review, merge gate), halt and report — that is work the pipeline doesn't understand.

Routing reads never depend on which branch is currently checked out: the orchestrator reads committed state branch-qualified (`git show <username>/<slug>:<file>`, branch listings, and `gh`), so the resume table can be evaluated before the branch is switched in.

**Execution-complete signal.** When a task's review comes back clean, the orchestrator (SDD's controller) ticks that task's `- [ ]` checkboxes in the plan file and commits them, alongside SDD's ledger append. **Committed checkboxes are the durable, authoritative cross-session signal; SDD's `.superpowers/sdd/progress.md` ledger stays in-session scratch (it is git-ignored and is not durable pipeline state).** Execution is complete if and only if zero `- [ ]` remain in the plan at branch tip. Tie-break: if `git log` shows a task's commits but its boxes are unticked (a crash in the gap), verify via `git log`, tick the boxes, and do not re-implement.

**Review state.** After Stage 4's review has committed its fixes and the stage has pushed, post a PR comment with the marker line `dev-flow: review clean @ <full-head-sha>`. Detection: marker SHA equals the current head -> merge gate; stale SHA -> re-review (any push, including a CI fix, correctly invalidates the marker); no marker -> PR review. (A label can't carry the SHA and goes silently stale — rejected.)

**Resume table** (checks run top-to-bottom, first match wins; each is mechanical; "latest PR" = the highest-numbered result of `gh pr list --head <username>/<slug> --state all`):

| Check | Start at |
|---|---|
| No `<username>/<slug>` branch (local or origin); bare idea | Design: create+checkout branch, draft |
| No branch; existing design file given | Design: adopt (branch, front-matter, review — which commits) |
| Branch exists; latest PR is `MERGED` | Done — run Stage 5's Cleanup (idempotent), then report; nothing to resume |
| Branch exists; latest PR is `CLOSED` | Halt — a human closed PR #N without merging; report and hand back. Never silently re-create a PR over a human's close. |
| Branch exists; no design doc with `dev-flow` front-matter at tip | **Foreign** (has commits beyond `<base>`, per Branch ownership) -> **Halt** — never adopt or delete a branch we didn't create. **Empty beyond `<base>`** (our just-created branch, Design crashed before committing) -> Design (redo; uncommitted drafts discarded) |
| Design committed at tip; no plan doc at tip | Plan |
| Plan at tip has ≥1 unchecked `- [ ]` | Execute — resume at first unchecked task (cross-check ledger + `git log`) |
| Plan fully checked; no PR for the branch (`--state all` list empty) | PR: create + review |
| Open PR; no `review clean @ <current head>` marker | PR review |
| Open PR; marker matches head | Merge gate (CI, `stops` from front-matter) |
| No row matches (e.g. resume with an unknown slug) | Nothing to resume — report it. If `gh pr list --head <username>/<slug> --state merged` shows a PR, say "already shipped (PR #N)"; else list `<username>/*` branches (local + origin, both candidate prefixes) as candidates. |

---

## Pipeline

The orchestrator drives every stage, running the branch-entry procedure (Artifact Contract) at each boundary. Exploratory *produce* work (bare-idea design drafting, `writing-plans`) runs in a fresh `general-purpose` produce-subagent — a leaf carrying the inherited-skills preamble (see Dispatching to Inherited Skills, above) that writes its draft into the working checkout (repo root, which is on the feature branch) and returns a short summary. All *fan-out* work — every `adversarial-review` invocation and the Execute SDD loop — the orchestrator runs itself, in-context, on the feature branch. Only leaf subagents are ever spawned; no subagent spawns a subagent.

### Stage 1 — Design

- **First act:** fix the slug, then create `<username>/<slug>` and check it out per the branch lifecycle (Artifact Contract): resolve the default branch, run the dirty-checkout gate, `git switch -c <username>/<slug> <base>`. Plain git, not a delegated skill — every resume check and the PR mapping key off that exact branch name and base, and no delegated mechanism guarantees either. Creation failure halts and reports.
- **Design-file entry:** adopt the given file — branch from main, copy the file into the checkout, stamp `dev-flow` front-matter, then review — which rewrites and commits.
- **Bare-idea entry:** the orchestrator dispatches a produce-subagent to draft a best-judgment design doc (written into the working checkout on the feature branch) using the inlined non-interactive protocol below. **brainstorming is NOT invoked** — dialogue is its core mechanism, and this pipeline never lets a delegated skill talk to the user. Inline its non-interactive bones instead:
  1. Explore project context.
  2. Scope/decomposition check — if the idea spans independent subsystems, **halt and report** the proposed decomposition rather than forcing it through.
  3. Consider 2-3 approaches, pick one, and record the choice plus rejected alternatives and reasoning.
  4. Record defensible-default assumptions explicitly. A genuinely blocking ambiguity — one with no defensible default — is a halt-and-report, not a guess.
  5. Run brainstorming's spec self-review checklist (placeholders, consistency, scope, ambiguity).
- The **orchestrator** invokes `dev-flow:adversarial-review` (mode: `design`) in-context on the feature branch — it is the approval gate that substitutes for the user's. The review rewrites the design and commits it on the branch (its contract); the orchestrator then checks the returned provenance line (Cross-Cutting Concerns) before proceeding. No separate apply or commit step.
- **Bare-idea entry defaults to a `post-design` stop** (see Stops, above).

### Stage 2 — Plan

- Spawn a subagent to run `superpowers:writing-plans` against the design, producing `docs/superpowers/plans/YYYY-MM-DD-<slug>-plan.md` (front-matter links the spec).
- The **orchestrator** invokes `dev-flow:adversarial-review` (mode: `plan`) in-context; the review rewrites the plan and commits it on the branch; the orchestrator checks the provenance line. Nothing to apply afterward.
- `post-plan` stop -> halt and report.

### Stage 3 — Execute

The **orchestrator** invokes `superpowers:subagent-driven-development` directly (in-context, on the feature branch) — it *is* SDD's controller and spawns the implementer/reviewer leaves itself (one level). No execute-stage-subagent wrapper. The orchestrator self-applies these overrides (there is no dispatch prompt to carry them):

- **Baseline:** branch entry has already ensured setup (deps installed); run the baseline test suite before the first task. **A red baseline halts** — a CI-green merge gate can't be reached from a red baseline. SDD's `using-git-worktrees` workflow skill creates no worktree here — it reads dev-flow's declared "work in place" preference and does its setup/baseline in the current checkout (see Dispatching to Inherited Skills).
- **Exit condition supersedes SDD's terminal:** last task complete, per-task reviews clean, full suite green, on the named branch. Do **not** run SDD's final whole-branch review; do **not** invoke `finishing-a-development-branch` (its interactive menu's option 1 is a local merge to base — the exact self-merge this pipeline exists to prevent). Report: branch, commit range, ledger path, and the ledger's unresolved Minor findings.
- **Pre-answers:** a plan-vs-code conflict is resolved by the **design doc** (the highest-reviewed artifact); if the design doc is silent, halt.
- **Halts:** SDD `BLOCKED` after its own ladder (more context / stronger model / split task) concluding "the plan itself is wrong" -> halt and report.
- **Bookkeeping:** on each task-review-clean, the **orchestrator** (SDD's controller — not SDD's own templates) ticks that task's plan checkboxes and commits them on the branch, alongside SDD's ledger append (see Artifact Contract).

### Stage 4 — PR

- `gh pr create`; PR body links the spec + plan paths and derives a summary from them. When the slug carries a task/issue ID (see Slug), reference it in the PR body — `Closes #42` for a GitHub issue, or the plain Linear/Jira key for those trackers. If an open PR already exists for the branch, reuse it — skip create.
- The **orchestrator** invokes `dev-flow:adversarial-review` (mode: `diff`) in-context, passing Stage 3's unresolved Minor-findings list as caller-supplied findings. **This is the pipeline's final whole-branch review** (SDD's was suppressed in Stage 3). The review applies the resolved fixes, commits them on the branch, and (its contract) runs the project's test suite after fixing. The orchestrator checks the provenance line.
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
- **Merge:** `gh pr merge <pr> --squash`. No `--delete-branch`, and no manual branch deletion anywhere — **the pipeline deletes no branches.** The merged **remote** branch is removed by the repository's *automatically delete head branches* setting (the standard GitHub configuration); the **local** `<username>/<slug>` branch is left for you to prune on your own schedule.
- **Cleanup (idempotent — the resume table's Done row runs this same block):**
  1. Return your checkout to the default branch: `git switch <default>` (the resolved default branch; already there on a re-run -> no-op success). Ignored scratch (e.g. SDD's ledger) does not block the switch; if *tracked* files have uncommitted modifications, halt and report instead — that is work the pipeline doesn't understand.

  That is the whole of Cleanup: the pipeline creates a branch but never tears one down. The remote is auto-deleted by the repo's merge setting; the local `<username>/<slug>` branch is left in place. (If a repo has that setting disabled, its merged remote branch simply remains — branch hygiene there is the repo's concern, not the pipeline's.)
- **Final report:** what shipped, the local branch left behind (`<username>/<slug>` — yours to prune), and every new issue filed across all stages.

---

## Environment Assumptions

- **Flat topology — the orchestrator is the only spawner.** Every subagent dev-flow spawns is a leaf; no subagent spawns a subagent. This is required, not a preference: **Claude Code 2.1.218 does not grant spawned subagents the `Agent` tool** (nested spawning was removed; the harness's recommended pattern is top-level orchestration only). So the orchestrator invokes every fan-out skill (`dev-flow:adversarial-review`, `subagent-driven-development`) in-context and spawns their worker leaves itself — always one level, works on every version. The intake gate above checks model *availability*, not nesting. (Nesting worked on 2.1.217 and was relied on by this plugin's 1.1.0; the 2.1.218 removal is why 1.2.0 flattened.)
- **Shared checkout.** Because dev-flow works on the feature branch in your current checkout (no worktree), a run owns that working tree while it is active — don't edit files there mid-run. The dirty-checkout gate (Artifact Contract) protects any uncommitted work you already had when a run starts or resumes. If you want the pipeline to never touch your main checkout, use the `dev-flow-worktree` plugin instead.
- **GitHub remote** is assumed from Stage 4 onward (the pipeline uses `gh` for PR, review marker, CI, and merge). This matches the existing plugins' reliance on `gh`. (The `<username>` resolver *prefers* `gh api user` when a remote is reachable but falls back to git config, so Design and Plan still run with no remote.)

## Cross-Cutting Concerns

- **Context hygiene:** produce-subagents and every spawned review/implementer leaf run in fresh subagents returning short summaries; the orchestrator holds the fan-out controllers' state directly (the review's group loop, SDD's task loop), bounded by file handoffs and summaries and recoverable via resume.
- **Review provenance is checked, not assumed.** The orchestrator runs each review (Design, Plan, PR — not Execute) in-context, then reads the review's returned provenance line (`seeds: N× <tier>; resolvers: M× <tier>`) directly and halts if it is missing or its tiers violate `dev-flow:adversarial-review`'s Model section (seeds must be the seed tier, resolvers the resolver tier; a `resolvers: 0` line from a no-findings review passes the resolver check vacuously). The tiers are canonicalized by the review's family match, so this is a direct comparison — a cheap self-check that the review actually spawned diverse reviewers.
- **Failure handling:** a stage that cannot proceed cleanly halts and hands back with a clear report and resume invocation; the pipeline never merges work that is worse than what it started with.
- **Idempotent resume:** guaranteed by the Artifact Contract — every resume decision is a mechanical read of the branch tip or the PR.
- **Severity-independent, value-gated:** the protocol acts on issues of any severity but only applies a fix when it genuinely improves the codebase.
