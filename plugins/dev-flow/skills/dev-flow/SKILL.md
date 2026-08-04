---
name: dev-flow
description: Use when the user wants to run their end-to-end dev flow — carry a change from design to plan to execute to PR to merge autonomously, with adversarial review at each stage. Triggers on "run dev-flow", "run my dev flow", "dev-flow on <design file>", "continue dev-flow on <slug>", or "take this design to a merged PR".
---

# dev-flow

Carry a change from design -> plan -> execute -> PR -> merge in one invocation. The pipeline works directly on a dedicated feature branch in your current checkout (no worktree). Default is full-auto to merge; the user can opt into a stop at any artifact boundary. The orchestrator (main session) drives the pipeline directly and is the only agent that spawns — so the multi-agent review and the Execute loop work on any Claude Code version, with no nested subagent spawning. All state lives in durable artifacts (the Artifact Contract) so a run resumes cleanly after any stop or crash.

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

The orchestrator spawns produce-subagents and executors on the main session model, and does its own bookkeeping (checkbox commits, front-matter) inline. Reviewer-model selection — which tier the orchestrator spawns each of the review's seed/resolver leaves on — is owned by `dev-flow:adversarial-review` and stated once, in its Model section; that rule travels with the review skill wherever it is invoked, and is deliberately not restated here.

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
- **Deterministic lookup (resume-safe).** Because the resolver can pick a different source in different environments (gh login online, git email offline), every branch-existence read — the resume table, the intake collision check, and the PR mapping — probes **both** candidate prefixes, the gh-login prefix and the git-fallback prefix, and uses whichever `<prefix>/<slug>` actually exists as a local or origin branch or carries PR history. Branch uniqueness plus the intake collision check guarantee at most one exists; if both exist for *different* committed designs, halt and report the ambiguity. Branch **creation** uses the canonical resolver (gh-login else git-fallback). Once the branch exists, that resolved name is `<username>/<slug>` for the rest of the run. **`<branch-ref>` (the routing ref).** When a command must name the branch's commits or files before entry has switched the checkout onto it, it uses `<branch-ref>` — the local branch `<username>/<slug>` when one exists, else `origin/<username>/<slug>` (local-first, matching branch entry's own checkout order; `git rev-parse` does not DWIM remote branches, so the `origin/` prefix is spelled, never assumed) — and never bare `HEAD`, never an argument-less `gh` command that resolves "the current branch": at routing time the checkout can be on any branch, and a `HEAD`-relative probe scans the wrong branch while exiting 0 — a silent wrong answer, not a failed producer, so Command discipline's halt never fires. Post-entry the feature branch is checked out and `<branch-ref>` equals `HEAD`, so a command written against `<branch-ref>` is correct from anywhere; write every new branch-addressed predicate that way.
- **Branch ownership (never adopt or delete a branch we didn't create).** `<username>/<slug>` is a namespace humans use by hand, so a branch of that name may be the user's own unrelated work — or a feature of the sibling `dev-flow-worktree` plugin (both plugins share this pattern). dev-flow owns a branch **iff** its tip carries this pipeline's design doc — `docs/superpowers/specs/*-<slug>-design.md` containing a `dev-flow:` front-matter block. The only other state dev-flow may treat as its own is a branch with **no commits beyond `<base>`** (an empty branch it just created, before Design committed). A branch that has commits beyond `<base>` but does **not** carry our design at tip is **foreign**: never adopt it (no redo-Design) and never open a PR from it — **halt and report** so the user renames the slug or removes the branch. This predicate gates the intake collision check and the resume table's no-design row; it replaces the exclusivity the old `dev-flow/<slug>` prefix gave for free. (The pipeline itself deletes no branches — see Stage 5 — so the only thing to guard is *building on* a branch that isn't ours, never destroying one.) **dev-flow also owns a branch if any commit in `<default-ref>..<branch-ref>` carries the trailer `dev-flow-stripped: <slug>`** — the stripped state (Docs policy), where the design doc is deliberately gone from tip and the branch is one command from merging. Detection: `git log "<default-ref>..<branch-ref>" --grep='^dev-flow-stripped: <slug>$' --format=%H` is non-empty — `<branch-ref>` per Branch identity, `<default-ref>` per the branch lifecycle's Base ref. This predicate runs at routing time (it gates the resume table and the intake collision check), where the checkout may be on any branch, so both range ends are named refs: bare `HEAD` here would scan whatever happens to be checked out and return a silent empty — exit 0, producing exactly the misleading foreign-branch halt this clause exists to prevent — and Docs policy's `merge_base` does not exist yet at that point, being itself `HEAD`-derived and PR-dependent (`gh pr view` resolves the *current* branch's PR; the intake collision check may have no PR at all). The two bounds agree on the trailer verdict wherever both are defined: the trailer commits are this branch's own, outside any base history, and base-side commits that a stale `<default-ref>` lets into the range cannot match the slug-anchored grep. Per Command discipline both refs are validated before substitution — an empty `<branch-ref>` collapses the range back into a `HEAD`-relative scan. Scanning the commit range rather than only the tip commit is free and strictly more robust: it survives a stripped-state halt that the user pushed a commit on top of. Ownership is deliberately **not** broadened to "the branch's history ever contained our design doc" — that would work, but it is inference, and it weakens a load-bearing safety guard for every non-strip case in order to serve one; the trailer is explicit and fires only where it is written.

Intake collision check: before creating `<username>/<slug>`, if it already exists (local or origin) and is **foreign** (per Branch ownership), qualify the new slug (append a disambiguator) or halt — never build on it; if it already carries our design, this is a resume, routed by the resume table. Also qualify if no branch exists but `gh pr list --head <username>/<slug> --state all` is non-empty — a slug whose PR history belongs to an earlier shipped feature is retired, so the resume table's PR-state reads stay unambiguous forever. (This replaces fuzzy topic-matching with mechanical existence checks.)

**Front-matter (the only new schema).** Design doc:

```yaml
---
dev-flow:
  slug: rate-limit
  stops: [post-plan, pre-merge]   # [] = full-auto to merge
  docs: commit                    # commit | strip — resolved and stamped once at intake (see Docs policy)
---
```

Plan doc: `dev-flow: {slug: rate-limit, spec: docs/superpowers/specs/2026-07-20-rate-limit-design.md}` (linkage only). **Stops live solely in the design doc.** The PR body links both doc paths. `dev-flow:adversarial-review` preserves front-matter on every rewrite (part of its contract), so this block survives all reviews.

**Docs policy — commit or strip the scaffolding.** Whether this pipeline's design and plan docs reach the default branch is a **per-repo setting**, resolved once at intake and then carried in the artifact.

*The setting.* `.claude/dev-flow.local.md` — the plugin-settings pattern (`.claude/<plugin>.local.md`: YAML front-matter, user-local, git-ignored by definition). Keys are bare; the filename scopes them, so the file carries no plugin block at all:

```yaml
---
docs: strip      # commit | strip
---
```

| State | Resolves to |
|---|---|
| File absent | `commit` |
| File present, no `docs:` key | `commit` |
| `docs: commit` | `commit` |
| `docs: strip` | `strip` |
| Any other value | `commit`, **and emit a one-line warning naming the bad value** |

The default is `commit` because it is the pre-existing behavior and the resume-safe one. The warning on an unrecognized value exists because a typo'd `strip` silently meaning `commit` fails in the direction that surprises the user — scaffolding appears in the default branch after they believed they had turned it off. **Both plugin variants read this same file and this same key** (`dev-flow` is the family name they share): the keep-vs-strip question is about the repo's default branch, and its answer does not change with the variant you invoked, so there is one file, not two — parallel per-variant files would be two things to keep in sync for a question with one answer. Because the file is git-ignored, what it holds is each developer's local declaration of the repo's convention, not a team-enforced fact. The strict `dev-flow:` front-matter namespacing rule is untouched and never applied here: it governs plugin-scoped blocks in *artifacts*, where the branch-ownership predicate keys off the block name, and this file is input, not an artifact.

*Resolution happens once, at intake.* Stage 1 reads the file and stamps the resolved value into the design doc's `dev-flow` front-matter block, alongside `slug` and `stops`. **Every later stage reads the artifact, never the settings file again.** Precedence: front-matter (present on any resume) > settings file (first run only) > default `commit`. This follows the contract's "state lives in artifacts" rule and mirrors how `stops` already works, and it matters more here than for `stops`: the settings file is git-ignored, so it may not exist in the checkout where a run resumes, and a resumed run must not silently flip policy. `dev-flow:adversarial-review` preserves front-matter across rewrites, so the key survives every review.

*Qualifying paths — what a strip may remove.* `<merge-base>` is a **validated variable, never an inline substitution**:

```sh
git fetch origin "+refs/heads/<baseRef>:refs/remotes/origin/<baseRef>"  # failure halts
merge_base=$(git merge-base HEAD "origin/<baseRef>")                    # failure or empty halts
```

`<baseRef>` comes from `gh pr view <pr> --json baseRefName`, naming the PR explicitly — `<pr>` is the latest PR from the slug's `gh pr list --head` mapping, already in hand wherever this runs; an argument-less `gh pr view` resolves "the PR of the current branch", one more implicit-`HEAD` assumption the routing-ref rule (Branch identity) exists to forbid. It is available everywhere `merge_base` is consumed, because `merge_base` now has only post-entry consumers with an open PR: the strip inside Stage 5 and Marker validity's deletion proof. Routing-time predicates — Branch ownership's trailer scan, the stripped-state resume row, the intake collision check — are bounded by `<default-ref>` instead and never touch `merge_base` or `gh pr view`. The explicit refspec, rather than a bare `git fetch origin <baseRef>`, is deliberate — in a single-branch clone a bare fetch updates only `FETCH_HEAD` and leaves `origin/<baseRef>` unresolvable. A checkout where fetch or merge-base still fails (offline, or shallow history not containing the base) halts with the failing command's output, instead of the silent false success an empty substitution produces.

A path `P` **qualifies** iff **all** of:

1. `P` matches `docs/superpowers/specs/*-<slug>-design.md` or `docs/superpowers/plans/*-<slug>-plan.md`.
2. `P` exists at `HEAD`.
3. `git cat-file -e "$merge_base:$P"` **fails** — i.e. `P` did not exist when this branch was created. With `merge_base` validated above the exit code is unambiguous: the ref is known-good and we are known to be in a repo, so a non-zero exit can only mean path-absent-at-merge-base.

Any path failing any gate is left alone. **No `git rm -r` of a directory, ever.** Gate 3 is the gate that prevents deleting already-merged work — slug-scoping alone does not, because a previously shipped feature's docs can legitimately match the globs. Merge-base rather than base-tip is deliberate: if another feature added a matching path to the default branch *after* we branched, a base-tip test would report "exists on base" and we would fail to remove our own copy. Merge-base is precisely "what this branch started from", so the predicate reads exactly as intended — *this branch added it.* Gate 1's globs are anchored only on the right, so a slug that is a hyphenated suffix of another (`docs-policy` vs `gh-6-docs-policy`) glob-matches the longer slug's filename; that is left as-is deliberately, because gates 2–3 make the collision unreachable — a foreign feature's doc passes "exists at `HEAD` but not at `<merge-base>`" only if this branch itself committed it.

*The stripped state, defined once.* A branch is **stripped** iff the design doc is absent at tip **and** at least one commit in `<default-ref>..<branch-ref>` carries the trailer `dev-flow-stripped: <slug>` — the same routing-safe range Branch ownership's detection command uses, evaluable from any checkout before or after entry, so this definition means one thing everywhere it is consumed. In this state, front-matter reads have **defined answers, not failed producers**: the recorded `stops` is empty — a recorded `pre-merge` stop halts at the merge gate's `stops` consultation (Stage 5), *before* any strip, so no branch reaches the stripped state with a stop outstanding — and `docs:` is never consulted, because the merge gate's strip step short-circuits on the absent doc before any policy read. This is the same move gate 3 already makes: once the surrounding state is validated (here, the trailer proven in range), a negative probe is an unambiguous answer, so Command discipline's halt-on-failure rule is satisfied, not suspended — nothing failed to produce. An absent design doc **without** the trailer is not the stripped state and keeps its existing meaning exactly: foreign branch, halt.

**Doc git lifecycle — branch at design start.** Creating `<username>/<slug>` and checking it out in your working directory is the *first* act of Stage 1 (the Create step of the branch lifecycle, below; design and plan only need the branch checked out — runnable setup is ensured at entry from Execute onward). Write and commit all docs **on the branch, in your checkout**. A doc's content is committed **only by `dev-flow:adversarial-review`, as the final step of its rewrite** — so "doc committed at tip" is equivalent to "stage complete" by construction, which removes the need for any separate "reviewed" marker on docs. (dev-flow itself commits only pipeline-state edits: front-matter `stops` updates and plan-checkbox ticks.) Adopt-existing-file entry: branch from main, copy the file in, stamp front-matter, then review — the review rewrites and commits. On every halt/stop, push the branch if a remote exists.

**Branch lifecycle — owned by dev-flow, plain git.** The contract stakes everything on one invariant: *a branch named exactly `<username>/<slug>`, based off the default branch, exists and is checked out in your working directory whenever a stage runs.* No delegated mechanism guarantees that (native worktree tools auto-name branches and take their base from a user setting), so dev-flow creates and checks out the branch itself with plain git. Because the branch is checked out in the repo root itself, every command — the orchestrator's own and every spawned leaf's (leaves are pinned to the repo root and cannot inherit cwd) — runs against it by default; the cwd-inheritance problem a separate worktree would create simply does not arise, so no `working-dir` argument and no `Work from:` field is needed anywhere in this pipeline. What a delegated skill threads into the leaves *it* spawns is that skill's own rule and is not waived here — `dev-flow:adversarial-review` threads the absolute repo root into every agent it spawns unconditionally (its Working directory section).

*Base ref and `<default-ref>`.* Resolve the default branch mechanically: `git symbolic-ref --short refs/remotes/origin/HEAD` (strip `origin/`); if unset, `git remote set-head origin --auto` and retry; if there is no remote, use `main` if that ref exists, else `master`, else halt and report. **`<default-ref>`** is `origin/<default>` when that ref exists, else local `<default>`; routing predicates use it as the base bound of `<default-ref>..<branch-ref>` ranges, with no fetch required — a stale `origin/<default>` only widens the range with base-side commits the slug-anchored greps cannot match. Branch **creation** — and only creation — turns it into `<base>` (after a best-effort `git fetch origin <default>`) and never branches from the invoking checkout's HEAD.

*Branch entry — the orchestrator runs this at each stage boundary, first run and resume:*
0. **Ensure the settings file is excluded** — idempotent, and first, *before* the dirty-checkout gate, so a not-yet-excluded settings file cannot trip that gate as an untracked file. Per Command discipline the exclude file is resolved through git, never spelled as a `.git/...` literal:

   ```sh
   exclude_file=$(git rev-parse --git-path info/exclude)   # failure or empty halts
   grep -qxF '.claude/dev-flow.local.md' "$exclude_file" || printf '%s\n' '.claude/dev-flow.local.md' >> "$exclude_file"
   ```

   A local exclude, never a committed `.gitignore` edit — which would itself pollute the PR diff. Grep the file rather than `git check-ignore`. Because entry runs at every stage boundary and this check is idempotent, a settings file created mid-run is excluded before any Execute-stage broad `git add` can sweep it in.
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

Routing reads never depend on which branch is currently checked out — this is Branch identity's `<branch-ref>` rule, binding on every routing predicate, not a summary: the orchestrator reads committed state as `git show <branch-ref>:<file>`, `git log "<default-ref>..<branch-ref>" …`, branch listings, and `gh` commands that name `<pr>` or `--head <username>/<slug>` explicitly — never bare `HEAD`, never an argument-less `gh pr view`. The resume table is therefore evaluable before the branch is switched in, even when the branch exists only on origin (`<branch-ref>` is then the remote-tracking ref; a bare branch name would not resolve there at all). Its marker rows need no `HEAD` either: compare the marker SHA to `git rev-parse <branch-ref>`; on inequality, a branch whose ownership scan found no trailer commits fails Marker validity's strip clause with nothing further to compute — a stripped branch never reaches these rows, the no-design row above routed it — and merge-gate step 1 re-proves full Marker validity post-entry before anything merges.

**Execution-complete signal.** When a task's review comes back clean, the orchestrator (SDD's controller) ticks that task's `- [ ]` checkboxes in the plan file and commits them, alongside SDD's ledger append. **Committed checkboxes are the durable, authoritative cross-session signal; SDD's `.superpowers/sdd/progress.md` ledger stays in-session scratch (it is git-ignored and is not durable pipeline state).** Execution is complete if and only if the plan at branch tip has zero unchecked task boxes — lines matching `^[[:space:]]*[-*+] \[ \]` (a task checkbox at line start, optionally indented; markdown's `-`, `*`, and `+` bullets all render a checkbox, so all three count). The count is line-anchored, not a raw token count: a `- [ ]` inside an inline code span or a blockquote line — such as the `writing-plans` header that documents the checkbox syntax — is documentation of the syntax, not a task, and the anchor excludes it. (A line-start task checkbox inside a fenced code block would still match; `writing-plans` emits none, and even if one appeared, over-counting only keeps Execute running rather than ever signalling a false complete.) Tie-break: if `git log` shows a task's commits but its boxes are unticked (a crash in the gap), verify via `git log`, tick the boxes, and do not re-implement.

**Review state.** After Stage 4's review has committed its fixes and the stage has pushed, post a PR comment whose **first line** is exactly the marker `dev-flow: review clean @ <full-head-sha>` — the SHA in full, nothing else on that line — with any report prose on the lines below. A comment is a marker **exactly when its first line has that form**; read the SHA from that line, never from a scan of the body, which also matches a report or comment that merely *quotes* a marker. The **operative** marker, when several match, is the latest by `createdAt` — `gh pr view <pr> --json comments` carries it and lists comments oldest-first, so it is the last match; never order by `id`, an opaque node ID there, not a number like a PR's. Detection: marker **valid** -> merge gate; marker present but **invalid** -> re-review; no marker -> PR review. (A label can't carry the SHA and goes silently stale — rejected.)

**Marker validity.** The marker is valid **iff** the marker SHA equals the current head, **or** every commit in `<marker-sha>..HEAD` carries the trailer `dev-flow-stripped: <slug>` **and** `git diff --no-renames --name-status <marker-sha> HEAD` contains only `D` entries (`--no-renames` pins the shape: by default git collapses a delete-plus-add pair into a single `R` entry — also invalidating, but the only-`D` read must not vary with the user's `diff.renames`. Judge the full listing, never `--diff-filter=D`, which silently hides the very entries that invalidate.), each for a path satisfying Docs policy's qualifying-path gates 1 and 3 — gate 2 ("exists at `HEAD`") is evaluated **at the marker SHA** here, since the paths being gone from head is the point. That second clause is a mechanical proof that the only change since the reviewed head is the intended deletion: any non-deletion entry, any deletion outside this branch's own scaffolding, or any trailer-less commit in the range invalidates it. It is unsatisfiable on a `commit`-policy run (no trailer commits can exist), so "any push, including a CI fix, correctly invalidates the marker" still holds everywhere it held before. The strip is verified by this rule, **not** by re-posting the marker — re-posting would assert "reviewed and suite-green at this SHA" for a SHA nothing reviewed, and would be fooled by an unrelated commit landing in the gap.

The trailer conjunct is mechanical, not eyeballed:

```sh
total=$(git rev-list --count "<marker-sha>..HEAD")                                          # failure or empty halts
stripped=$(git rev-list --count --grep='^dev-flow-stripped: <slug>$' "<marker-sha>..HEAD")  # failure or empty halts
[ "$total" -eq "$stripped" ]    # equal <=> every commit in the range carries the trailer
```

Both counts derive from the same range, so equality is exactly "every commit matched"; one trailer-less commit — a manual push, a merge from the default branch — breaks it. The grep is anchored at both ends so a prefix- or suffix-sharing slug cannot false-match. On inequality, the offending SHAs come from the same grep inverted: `git log "<marker-sha>..HEAD" --grep='^dev-flow-stripped: <slug>$' --invert-grep --format=%H`. Per Command discipline, `<marker-sha>` is validated non-empty before either command — an empty one collapses the range to `HEAD..HEAD`, where `0 -eq 0` would falsely validate.

**Resume table** (checks run top-to-bottom, first match wins; each is mechanical; "latest PR" = the highest-numbered result of `gh pr list --head <username>/<slug> --state all`):

| Check | Start at |
|---|---|
| No `<username>/<slug>` branch (local or origin); bare idea | Design: create+checkout branch, draft |
| No branch; existing design file given | Design: adopt (branch, front-matter, review — which commits) |
| Branch exists; latest PR is `MERGED` | Done — run Stage 5's Cleanup (idempotent), then report; nothing to resume |
| Branch exists; latest PR is `CLOSED` | Halt — a human closed PR #N without merging; report and hand back. Never silently re-create a PR over a human's close. |
| Branch exists; no design doc with `dev-flow` front-matter at tip | **No commits beyond `<base>`** (`git log "<default-ref>..<branch-ref>" --format=%H` empty — the ungrep'd form of the ownership scan; our just-created branch, Design crashed before committing) -> Design (redo; uncommitted drafts discarded). **`dev-flow-stripped: <slug>` trailer in `<default-ref>..<branch-ref>`** (the stripped state, per Docs policy; Branch ownership's detection command) -> **Merge gate** — the gate's ordinary steps handle it; there is no stripped-only entry point. **Otherwise foreign** (has commits beyond `<base>`, per Branch ownership) -> **Halt** — never adopt or delete a branch we didn't create |
| Design committed at tip; no plan doc at tip | Plan |
| Plan at tip has ≥1 unchecked task box (a line matching `^[[:space:]]*[-*+] \[ \]`) | Execute — resume at first unchecked task (cross-check ledger + `git log`) |
| Plan fully checked; no PR for the branch (`--state all` list empty) | PR: create + review |
| Open PR; no `review clean` marker, or the marker is **invalid** (Marker validity) | PR review |
| Open PR; marker **valid** (Marker validity — SHA equals head, or a proven strip since) | Merge gate (CI, `stops` from front-matter) |
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
- **Docs policy (intake):** resolve `docs` per the Artifact Contract's Docs policy — read `.claude/dev-flow.local.md`, apply the resolution table (emitting the one-line warning on an unrecognized value), and stamp the result into the design doc's `dev-flow` front-matter block alongside `slug` and `stops`. Do this **before** the review runs, so the review's rewrite carries it. A `docs` value already present in the front-matter wins outright — a resume never re-reads the settings file.
- The **orchestrator** invokes `dev-flow:adversarial-review` (mode: `design`) in-context on the feature branch — it is the approval gate that substitutes for the user's. The review rewrites the design and commits it on the branch (its contract); the orchestrator then checks the returned provenance line (Cross-Cutting Concerns) before proceeding. No separate apply or commit step.
- **Bare-idea entry defaults to a `post-design` stop** (see Stops, above).

### Stage 2 — Plan

- Spawn a subagent to run `superpowers:writing-plans` against the design, producing `docs/superpowers/plans/YYYY-MM-DD-<slug>-plan.md` (front-matter links the spec).
- **Make each `## Task N` section self-sufficient — instruct `writing-plans` so.** SDD briefs one task at a time: `scripts/task-brief` hands the implementer only the text between `## Task N` and the next task heading, with no plan-file path — so anything a task step leans on from **outside that span** (e.g. a shared verification block, an explicit `§`/`§V` ID, another task's output, or an implicit "the table above" / "as defined earlier") is unresolvable from the brief; what triggers the rule is **structural** — the target is not defined within this `## Task N`→next-task span — not how casually the reference reads. The dispatch requires every such cross-section reference to be **either inlined into the task section, or named there by the plan's absolute path** with this clause: *read the referenced block verbatim from the plan file at `<abs-path>`; never reconstruct or substitute it; if you cannot read the plan file, stop and report.* Putting the pointer anywhere `task-brief` strips — `## Global Constraints`, a `## Verification scripts` preamble, **any** non-`## Task N` section — never reaches the implementer, so stating it once outside the referencing task is insufficient by construction. This doubles as the `writing-plans` subagent's own plan self-review criterion: make each section self-sufficient, and **halt and report** any out-of-section reference that cannot be given an in-section pointer rather than ship the plan — the failure is silent, the implementer running a substituted, weaker check for the ID it cannot resolve while nothing downstream catches it.
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
- **Under `docs: strip`** (front-matter, per Docs policy), the PR body also carries one line noting that the design and plan live in this PR's commit history and are removed before merge by repo policy — so the linked paths will not exist on the default branch after the merge. Under `docs: commit` the body is unchanged.
- The **orchestrator** invokes `dev-flow:adversarial-review` (mode: `diff`) in-context, passing Stage 3's unresolved Minor-findings list as caller-supplied findings. **This is the pipeline's final whole-branch review** (SDD's was suppressed in Stage 3). The review applies the resolved fixes, commits them on the branch, and (its contract) runs the project's test suite after fixing. The orchestrator checks the provenance line.
- **Post-fix test gate:** the marker may be posted only when the review reported the suite green — or reported that no automated suite exists (e.g. a prose-only repo). If for any reason the branch is red at head, halt; never post the marker on red. The marker therefore certifies **reviewed and suite-green (or no suite exists) at this exact SHA** — Stage 5 relies on this when a repo has no CI.
- Push the branch, then post the `dev-flow: review clean @ <full-head-sha>` marker comment.
- `pre-merge` stop -> halt and report (PR open, reviewed, fixes pushed) with the testing note and the resume invocation.

### Stage 5 — Merge

The merge gate is five steps and is **re-entrant**: step 4 can send the run back to step 1, so first run and resume travel the identical path and no resume-only entry point exists anywhere.

1. **Push, then confirm the marker.** `git push` first — a no-op when already up to date, and it closes a real crash window: a crash between a strip *commit* and its *push* would otherwise merge the un-stripped remote head. Then confirm the marker is **valid** per the Artifact Contract's Marker validity rule. Invalid -> re-review, **unless the design doc is no longer at tip**, where re-review is impossible (there is no artifact to review against): halt and report the offending SHA(s) and that the doc is gone. That is what a stripped branch which has diverged past its strip commit gets — a specific, honest halt rather than a misleading foreign-branch one, and never a re-review the stripped state cannot support.
2. **Bounded CI wait** against the current head: run `gh pr checks <pr> --watch` under a hard cap (default 10 minutes, enforced via the Bash tool's `timeout: 600000`, since `gh pr checks --watch` has no native timeout of its own). Exactly four outcomes — distinguish failure from no-checks by output text, not exit code (both exit 1; pending exits 8):
   - **All checks pass** -> proceed.
   - **Any check fails** -> halt and report.
   - **Still pending at the cap** -> halt and report "CI still pending" (resume re-enters the merge gate for free). Never an open-ended block.
   - **Output contains "no checks reported"** (the repo has no CI on this PR) -> proceed. This is safe only because the marker already certifies Stage 4's test gate — suite green at this head, or no suite exists. Never read "no checks" as a green test signal on its own.
3. **Consult `stops`** from the design doc's front-matter at tip; a `pre-merge` stop pauses **here**, with the testing note — before any strip, so a halted branch is always intact and fully resumable with both docs at tip. In the stripped state there is no doc at tip and this read is not attempted: the recorded stops are empty by the stripped-state rule (Docs policy) — proceed, never halt. (A doc-less tip *without* the trailer cannot reach this step; step 1 already halted it.)
4. **Strip, if the policy says so.** If the design doc is absent at tip, this is the stripped state — step 1 halted every other doc-less branch — so the strip already ran: no-op. Otherwise read `docs:` from the front-matter at tip (the doc step 3 just consulted): `commit` -> no-op, with no gate evaluation — the default path never runs the base-ref fetch or `git merge-base`, so it cannot halt on plumbing (a shallow checkout that cannot compute a merge-base still merges under `commit`, exactly as it did before this policy existed). Only under `strip`: validate `merge_base` and evaluate Docs policy's qualifying gates — paths failing a gate are left alone, and if nothing qualifies, proceed. If any path qualifies: `git rm` the qualifying paths, commit with the trailer (`git commit -m "<msg>" --trailer "dev-flow-stripped: <slug>"`), push, and **re-enter this gate at step 1**. Re-entry terminates by construction: the next pass finds no doc at tip and no-ops here. The re-wait at step 2 is not optional politeness — where branch protection requires checks, GitHub demands they pass on the new head; where there is no CI, step 2 returns "no checks reported" and proceeds, exactly as before.
5. **Merge:** `gh pr merge <pr> --squash`. No `--delete-branch`, and no manual branch deletion anywhere — **the pipeline deletes no branches.** The merged **remote** branch is removed by the repository's *automatically delete head branches* setting (the standard GitHub configuration); the **local** `<username>/<slug>` branch is left for you to prune on your own schedule.

- **Cleanup (idempotent — the resume table's Done row runs this same block):**
  1. Return your checkout to the default branch: `git switch <default>` (the resolved default branch; already there on a re-run -> no-op success). Ignored scratch (e.g. SDD's ledger) does not block the switch; if *tracked* files have uncommitted modifications, halt and report instead — that is work the pipeline doesn't understand.

  That is the whole of Cleanup: the pipeline creates a branch but never tears one down. The remote is auto-deleted by the repo's merge setting; the local `<username>/<slug>` branch is left in place. (If a repo has that setting disabled, its merged remote branch simply remains — branch hygiene there is the repo's concern, not the pipeline's.)
- **Final report:** what shipped, the local branch left behind (`<username>/<slug>` — yours to prune), and every new issue filed across all stages.

---

## Environment Assumptions

- **Flat topology — the orchestrator is the only spawner.** Every subagent dev-flow spawns is a leaf; no subagent spawns a subagent. This is required, not a preference: whether a spawned subagent can itself spawn is a harness capability that has been withdrawn and restored across patch releases, and observing that it currently works is not permission to nest. So the orchestrator invokes every fan-out skill (`dev-flow:adversarial-review`, `subagent-driven-development`) in-context and spawns their worker leaves itself — always one level, works on every version.
- **Shared checkout.** Because dev-flow works on the feature branch in your current checkout (no worktree), a run owns that working tree while it is active — don't edit files there mid-run. The dirty-checkout gate (Artifact Contract) protects any uncommitted work you already had when a run starts or resumes. If you want the pipeline to never touch your main checkout, use the `dev-flow-worktree` plugin instead.
- **GitHub remote** is assumed from Stage 4 onward (the pipeline uses `gh` for PR, review marker, CI, and merge). This matches the existing plugins' reliance on `gh`. (The `<username>` resolver *prefers* `gh api user` when a remote is reachable but falls back to git config, so Design and Plan still run with no remote.)

## Cross-Cutting Concerns

- **Context hygiene:** produce-subagents and every spawned review/implementer leaf run in fresh subagents returning short summaries; the orchestrator holds the fan-out controllers' state directly (the review's group loop, SDD's task loop), bounded by file handoffs and summaries and recoverable via resume.
- **Review provenance is checked, not assumed.** The orchestrator runs each review (Design, Plan, PR — not Execute) in-context, then reads the review's returned provenance line (`seeds: N× <model>; resolvers: M× <model>`) directly and halts if it is missing or its models violate `dev-flow:adversarial-review`'s Model section (seeds must be the seed tier's model, resolvers the resolver tier's model, each matched to the dated id its tier pins, ignoring any harness-appended variant suffix; a `resolvers: 0` line from a no-findings review passes the resolver check vacuously). The models are the normalized pins the reviewers matched to, so this is a direct comparison — a cheap self-check that the review actually fanned out to separate reviewer subagents on the specified tiers, rather than folding into a single inline pass.
- **Failure handling:** a stage that cannot proceed cleanly halts and hands back with a clear report and resume invocation; the pipeline never merges work that is worse than what it started with.
- **Idempotent resume:** guaranteed by the Artifact Contract — every resume decision is a mechanical read of the branch tip or the PR.
- **Command discipline:** resolve git-internal paths through git (`git rev-parse --git-path …`), never as `.git/...` literals — `.git` is a file, not a directory, in any linked worktree. Capture, validate non-empty, and quote any command output a later command consumes; a failed producer halts the run and never substitutes an empty string — an empty variable silently *inverts* git predicates (an empty `<marker-sha>` turns `git rev-list <marker-sha>..HEAD` into the empty range `HEAD..HEAD`, a false "every commit matched"; an empty `<branch-ref>` turns `git log <default-ref>..<branch-ref>` back into a `HEAD`-relative scan, a false "no trailer"; an empty `<merge-base>` turns `git cat-file -e :<path>` into an index lookup that falsely succeeds). **This governs the success criteria a design or plan emits as well as the pipeline's own commands** — in a repo with no test suite they are the whole correctness surface. There, a step that consumes a **computed** git ref runs its `git` calls through `python3`/`subprocess` with the ref as an `argv` element rather than a shell chain: `argv` cannot word-split, so an empty ref is `fatal: bad revision ''` rather than a different valid command. Capture-validate-quote stays the rule everywhere else.
- **Measurements are derived, not typed.** Every measurement an artifact states was printed by a command its author ran, or it is cut. A measurement of the artifact's **own replacement text** — a word or line count, "the shortest bullet", "in seven words" — is asserted in that artifact's own success criteria: the text is still under the author's hand, and a later rewrite silently falsifies anything typed beside it. A measurement of the **tree before the edit** is the opposite case — re-deriving it afterwards falsifies a design that is correct — so give the command pinned to the base revision (`git grep … <base> -- …`) beside the claim, state the claim in the past tense at that revision, and state no number its output does not show. A spec self-review names every measurement the artifact states and the command that printed it.
- **Severity-independent, value-gated:** the protocol acts on issues of any severity but only applies a fix when it genuinely improves the codebase.
