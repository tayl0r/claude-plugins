---
name: dev-flow-worktree
description: Use when the user wants to run their end-to-end dev flow in an isolated git worktree — carry a change from design to plan to execute to PR to merge autonomously, with adversarial review at each stage. Triggers on "run dev-flow-worktree", "dev-flow-worktree on <design file>", "continue dev-flow-worktree on <slug>", or "take this design to a merged PR in a worktree".
---

# dev-flow-worktree

Carry a change from design -> plan -> execute -> PR -> merge in one invocation, isolated in a dedicated git worktree so your main checkout is never touched. Default is full-auto to merge; the user can opt into a stop at any artifact boundary. The orchestrator (main session) drives the pipeline directly and is the only agent that spawns — so the multi-agent review and the Execute loop work on any Claude Code version, with no nested subagent spawning. All state lives in durable artifacts (the Artifact Contract) so a run resumes cleanly after any stop or crash.

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

The orchestrator spawns produce-subagents and executors on the main session model, and does its own bookkeeping (checkbox commits, front-matter) inline. Reviewer-model selection — which tier the orchestrator spawns each of the review's seed/resolver leaves on — is owned by `dev-flow-worktree:adversarial-review` and stated once, in its Model section; that rule travels with the review skill wherever it is invoked, and is deliberately not restated here.

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

**Slug.** Fix a short kebab-case slug once at intake — derive it from the design filename when one is given (`2026-07-20-rate-limit-design.md` -> `rate-limit`), else choose one from the idea. **If the run references a task/issue ID — a Linear or Jira key like `ENG-1421`, or a GitHub issue like `#42` — fold it into the slug as a lowercased kebab prefix: `<ticket>-<topic>` (e.g. `eng-1421-rate-limit`, `gh-42-rate-limit`).** The ID comes from the invocation (you name it) or the design doc; because it lives inside the opaque slug it threads through the branch, filenames, and PR unchanged — giving ticket traceability and making accidental branch collisions rarer (never impossible, though: humans use ticket-prefixed branch names too, which is why Branch ownership, below, is the actual safety guard, not the naming). Treat the slug as an opaque, immutable ID: renaming the feature changes prose, never the slug. It threads through:

- spec: `docs/superpowers/specs/YYYY-MM-DD-<slug>-design.md`
- plan: `docs/superpowers/plans/YYYY-MM-DD-<slug>-plan.md`
- branch: `<username>/<slug>` (see Branch identity, below)
- PR: `gh pr list --head <username>/<slug> --state all` (branch->PR mapping is native to `gh`; branch existence is read per Branch identity's dual-prefix probe). Always pass `--state all` — the default listing is open-only and silently hides merged/closed PRs. "Latest PR" = the highest-numbered result.

**Branch identity.** The feature branch is `<username>/<slug>`.

- **`<username>` (resolve once per invocation).** `gh api user --jq .login` when it succeeds (GitHub remote reachable + `gh` authenticated); else a git fallback — the sanitized local-part of `git config user.email` (lowercase; every run of characters outside `[a-z0-9._-]` collapsed to a single `-`; leading/trailing `-` trimmed); else the same sanitization of `git config user.name`; if none yields a non-empty token, halt and report. Design and Plan therefore stay GitHub-free — the fallback needs no remote.
- **Deterministic lookup (resume-safe).** Because the resolver can pick a different source in different environments (gh login online, git email offline), every branch-existence read — the resume table, the intake collision check, and the PR mapping — probes **both** candidate prefixes, the gh-login prefix and the git-fallback prefix, and uses whichever `<prefix>/<slug>` actually exists as a local or origin branch or carries PR history. Branch uniqueness plus the intake collision check guarantee at most one exists; if both exist for *different* committed designs, halt and report the ambiguity. Branch **creation** uses the canonical resolver (gh-login else git-fallback). Once the branch exists, that resolved name is `<username>/<slug>` for the rest of the run. **`<branch-ref>` (the routing ref).** When a command must name the branch's commits or files from outside the pipeline worktree, it uses `<branch-ref>` — the local branch `<username>/<slug>` when one exists, else `origin/<username>/<slug>` (local-first, matching the Re-attach step's own order; `git rev-parse` does not DWIM remote branches, so the `origin/` prefix is spelled, never assumed) — and never bare `HEAD`, never an argument-less `gh` command that resolves "the current branch": routing runs from the main checkout, whose `HEAD` is *never* the feature branch (the linked worktree holds it, and git refuses a second checkout), so a `HEAD`-relative probe deterministically scans the wrong branch while exiting 0 — a silent wrong answer, not a failed producer, so Command discipline's halt never fires. Inside the worktree `<branch-ref>` equals `HEAD`, so a command written against `<branch-ref>` is correct from anywhere; write every new branch-addressed predicate that way.
- **Branch ownership (never adopt or delete a branch we didn't create).** `<username>/<slug>` is a namespace humans use by hand, so a branch of that name may be the user's own unrelated work — or a feature of the sibling `dev-flow` plugin (both plugins share this pattern). dev-flow-worktree owns a branch **iff** its tip carries this pipeline's design doc — `docs/superpowers/specs/*-<slug>-design.md` containing a `dev-flow-worktree:` front-matter block. The only other state it may treat as its own is a branch with **no commits beyond `<base>`** (an empty branch it just created, before Design committed). A branch that has commits beyond `<base>` but does **not** carry our design at tip is **foreign**: never adopt it (no redo-Design) and never open a PR from it — **halt and report** so the user renames the slug or removes the branch. This predicate gates the intake collision check and the resume table's no-design row; it replaces the exclusivity the old `dev-flow/<slug>` prefix gave for free. (The pipeline itself deletes no branches — see Stage 5 — so the only thing to guard is *building on* a branch that isn't ours, never destroying one.) **dev-flow-worktree also owns a branch if any commit in `<default-ref>..<branch-ref>` carries the trailer `dev-flow-worktree-stripped: <slug>`** — the stripped state (Docs policy), where the design doc is deliberately gone from tip and the branch is one command from merging. Detection: `git log "<default-ref>..<branch-ref>" --grep='^dev-flow-worktree-stripped: <slug>$' --format=%H` is non-empty — `<branch-ref>` per Branch identity, `<default-ref>` per the worktree lifecycle's Base ref. This predicate runs at routing time (it gates the resume table and the intake collision check), where the checkout is the main checkout — never the feature branch, which the linked worktree holds — so both range ends are named refs: bare `HEAD` here would scan whatever happens to be checked out and return a silent empty — exit 0, producing exactly the misleading foreign-branch halt this clause exists to prevent — and Docs policy's `merge_base` does not exist yet at that point, being itself `HEAD`-derived and PR-dependent (`gh pr view` resolves the *current* branch's PR; the intake collision check may have no PR at all). The two bounds agree on the trailer verdict wherever both are defined: the trailer commits are this branch's own, outside any base history, and base-side commits that a stale `<default-ref>` lets into the range cannot match the slug-anchored grep. Per Command discipline both refs are validated before substitution — an empty `<branch-ref>` collapses the range back into a `HEAD`-relative scan. Scanning the commit range rather than only the tip commit is free and strictly more robust: it survives a stripped-state halt that the user pushed a commit on top of. Ownership is deliberately **not** broadened to "the branch's history ever contained our design doc" — that would work, but it is inference, and it weakens a load-bearing safety guard for every non-strip case in order to serve one; the trailer is explicit and fires only where it is written.

Intake collision check: before creating `<username>/<slug>`, if it already exists (local or origin) and is **foreign** (per Branch ownership), qualify the new slug (append a disambiguator) or halt — never build on it (and `git worktree add -b` would fail outright on an existing branch anyway); if it already carries our design, this is a resume, routed by the resume table. Also qualify if no branch exists but `gh pr list --head <username>/<slug> --state all` is non-empty — a slug whose PR history belongs to an earlier shipped feature is retired, so the resume table's PR-state reads stay unambiguous forever. (This replaces fuzzy topic-matching with mechanical existence checks.)

**Front-matter (the only new schema).** Design doc:

```yaml
---
dev-flow-worktree:
  slug: rate-limit
  stops: [post-plan, pre-merge]   # [] = full-auto to merge
  docs: commit                    # commit | strip — resolved and stamped once at intake (see Docs policy)
---
```

Plan doc: `dev-flow-worktree: {slug: rate-limit, spec: docs/superpowers/specs/2026-07-20-rate-limit-design.md}` (linkage only). **Stops live solely in the design doc.** The PR body links both doc paths. `dev-flow-worktree:adversarial-review` preserves front-matter on every rewrite (part of its contract), so this block survives all reviews.

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

The default is `commit` because it is the pre-existing behavior and the resume-safe one. The warning on an unrecognized value exists because a typo'd `strip` silently meaning `commit` fails in the direction that surprises the user — scaffolding appears in the default branch after they believed they had turned it off. **Both plugin variants read this same file and this same key** (`dev-flow` is the family name they share): the keep-vs-strip question is about the repo's default branch, and its answer does not change with the variant you invoked, so there is one file, not two — parallel per-variant files would be two things to keep in sync for a question with one answer. Because the file is git-ignored, what it holds is each developer's local declaration of the repo's convention, not a team-enforced fact. The strict `dev-flow-worktree:` front-matter namespacing rule is untouched and never applied here: it governs plugin-scoped blocks in *artifacts*, where the branch-ownership predicate keys off the block name, and this file is input, not an artifact.

*Resolution happens once, at intake.* Stage 1 reads the file and stamps the resolved value into the design doc's `dev-flow-worktree` front-matter block, alongside `slug` and `stops`. **Every later stage reads the artifact, never the settings file again.** Precedence: front-matter (present on any resume) > settings file (first run only) > default `commit`. This follows the contract's "state lives in artifacts" rule and mirrors how `stops` already works, and it matters more here than for `stops`: the settings file is git-ignored, so it may not exist in the checkout where a run resumes, and a resumed run must not silently flip policy. `dev-flow-worktree:adversarial-review` preserves front-matter across rewrites, so the key survives every review.

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

*The stripped state, defined once.* A branch is **stripped** iff the design doc is absent at tip **and** at least one commit in `<default-ref>..<branch-ref>` carries the trailer `dev-flow-worktree-stripped: <slug>` — the same routing-safe range Branch ownership's detection command uses, evaluable from any checkout before or after entry, so this definition means one thing everywhere it is consumed. In this state, front-matter reads have **defined answers, not failed producers**: the recorded `stops` is empty — a recorded `pre-merge` stop halts at the merge gate's `stops` consultation (Stage 5), *before* any strip, so no branch reaches the stripped state with a stop outstanding — and `docs:` is never consulted, because the merge gate's strip step short-circuits on the absent doc before any policy read. This is the same move gate 3 already makes: once the surrounding state is validated (here, the trailer proven in range), a negative probe is an unambiguous answer, so Command discipline's halt-on-failure rule is satisfied, not suspended — nothing failed to produce. An absent design doc **without** the trailer is not the stripped state and keeps its existing meaning exactly: foreign branch, halt.

**Doc git lifecycle — branch + worktree at design start.** Creating `<username>/<slug>` and its worktree is the *first* act of Stage 1 (the Create step of the worktree lifecycle, below; design and plan only need a checkout — setup is ensured at entry from Execute onward). Write and commit all docs **in the worktree, on the branch**. A doc's content is committed **only by `dev-flow-worktree:adversarial-review`, as the final step of its rewrite** — so "doc committed at tip" is equivalent to "stage complete" by construction, which removes the need for any separate "reviewed" marker on docs. (dev-flow-worktree itself commits only pipeline-state edits: front-matter `stops` updates and plan-checkbox ticks.) Adopt-existing-file entry: branch from main, copy the file in, stamp front-matter, then review — the review rewrites and commits. On every halt/stop, push the branch if a remote exists. dev-flow-worktree always runs in a dedicated worktree — there is no "work in the main checkout" mode.

**Worktree lifecycle — owned by dev-flow-worktree, plain git.** The contract stakes everything on one invariant: *a worktree on a branch named exactly `<username>/<slug>`, based off the default branch, always exists and is findable by every stage.* No delegated mechanism guarantees that (native tools auto-name branches and take their base from a user setting; `using-git-worktrees` skips creation when already isolated and falls back to working in place on sandbox errors), so dev-flow-worktree creates, enters, and removes the worktree itself with plain git. Fixed path: `<main-root>/.claude/worktrees/dev-flow-<slug>`, where `<main-root>` is the first entry of `git worktree list --porcelain` (the main working tree). This location is deliberate: a fixed, git-ignored path every stage computes and addresses by absolute path — subagents operate on the worktree via `cd`/`git -C`, not harness worktree-entry (see the Enter step).

*Base ref and `<default-ref>`.* Resolve the default branch mechanically: `git symbolic-ref --short refs/remotes/origin/HEAD` (strip `origin/`); if unset, `git remote set-head origin --auto` and retry; if there is no remote, use `main` if that ref exists, else `master`, else halt and report. **`<default-ref>`** is `origin/<default>` when that ref exists, else local `<default>`; routing predicates use it as the base bound of `<default-ref>..<branch-ref>` ranges, with no fetch required — a stale `origin/<default>` only widens the range with base-side commits the slug-anchored greps cannot match. Branch **creation** — and only creation — turns it into `<base>` (after a best-effort `git fetch origin <default>`) and never branches from the invoking checkout's HEAD.

*Worktree entry — the orchestrator runs this at each stage boundary, first run and resume:*
0. **Ensure the pipeline's local paths are excluded** — idempotent, and first, so the worktree container is ignored before it exists and a settings file created mid-run is excluded before any Execute-stage broad `git add` can sweep it in. Per Command discipline the exclude file is resolved through git, never spelled as a `.git/...` literal — `.git` is a file, not a directory, in any linked worktree:

   ```sh
   exclude_file=$(git rev-parse --git-path info/exclude)   # failure or empty halts
   for pat in '.claude/worktrees/' '.claude/dev-flow.local.md'; do
     grep -qxF "$pat" "$exclude_file" || printf '%s\n' "$pat" >> "$exclude_file"
   done
   ```

   `--git-path` resolves to the main repository's shared `info/exclude` from any worktree, so one write covers the main checkout and every worktree at once. A local exclude, never a committed `.gitignore` edit — which would itself pollute the PR diff. Grep the file rather than `git check-ignore`, which misfires on the not-yet-created directory. This step precedes step 3's `git worktree add`, so the container is ignored before it is created.
1. **Locate:** in `git worktree list --porcelain`, the entry whose `branch` is `refs/heads/<username>/<slug>`; its `worktree <path>` is the pipeline worktree. (Git allows a branch in at most one worktree, so the match is unique.)
2. **Re-attach** if the branch exists but no worktree lists it (cleanup crash, manual removal): `git worktree add <path> <username>/<slug>` — no `-b`. Branch on origin only: `git fetch origin <username>/<slug>`, then `git worktree add <path> -b <username>/<slug> origin/<username>/<slug>` (upstream is set automatically).
3. **Create** if neither exists — legal only as Stage 1's first act (the resume table routes every other no-branch state to Design; any other stage landing here halts: contract violation). The container is already ignored by step 0, which always precedes this step: `git worktree add <path> -b <username>/<slug> <base>`. **If creation fails (sandbox/permission), halt and report; there is no work-in-place fallback.**
4. **Enter:** the orchestrator routes the resume table from the main checkout (reads per Branch identity's `<branch-ref>` rule, binding on every routing predicate: `git show <branch-ref>:<file>`, `git log "<default-ref>..<branch-ref>" …`, branch listings, and `gh` commands naming `<pr>` or `--head <username>/<slug>` explicitly — none need entry, and none may use bare `HEAD` or an argument-less `gh pr view`, since the main checkout's `HEAD` is *never* the feature branch; the marker rows compare the marker SHA to `git rev-parse <branch-ref>`, and on inequality a branch whose ownership scan found no trailer commits fails Marker validity's strip clause with nothing further to compute — full Marker validity is re-proven post-entry at merge-gate step 1), then `cd`s into the worktree to *drive* **every stage command whose git/`gh` target derives from cwd or the current branch** — an `adversarial-review` invocation, the Execute SDD loop, and **Stage 4's `gh pr create`, the branch push on any halt/stop, the `review clean` marker-SHA read, and every command the merge gate runs — its `git push`, the base-ref `git fetch`, `git merge-base`, `git cat-file -e`, `git rev-list`, `git diff --name-status`, `git rm`, the strip commit, and the strip push** — so all of it (baseline/per-task suites, `HEAD`-relative commands, the review's post-fix suite, PR creation and push, the strip) runs against the pipeline tree and branch; it `cd`s back to main only for routing reads. (Any such command that must run from main instead names its target explicitly: `--head <username>/<slug>`, `git push origin <username>/<slug>`, `git rev-parse <username>/<slug>`.) Spawned leaves are pinned to the repo root and cannot inherit cwd, so each is handed the absolute worktree path explicitly: `adversarial-review` via its `working-dir` argument (write-side fixers use `git -C <path>`), and **every** SDD dispatch — implementers, fixers, and task-reviewers — via its `Work from:` field, so any commit, focused test, git fallback, or changed-file Read runs against the pipeline tree (each `cd`s there first; a bare `git commit` would land on the main checkout's branch). Harness worktree-entry (`EnterWorktree`) is not used — the nested-review-fix probe found it rejected from repo-root-pinned subagents (see the flatten design's Evidence).
5. **Ensure runnable (stages that run code — Execute onward):** if project deps are absent (e.g. `package.json` with no `node_modules`), run standard project setup (npm install / cargo build / …). Design and Plan skip this. Living in entry rather than in any one stage means a resume landing at PR review or the merge gate in a re-created worktree still gets a working tree before any post-fix suite run.
6. **Dirty worktree on resume:** untracked scratch is ignored. Uncommitted *tracked* modifications: on an Execute landing, `git stash push -u -m "<username>/<slug>: pre-resume salvage"` and report the stash — resume position was derived from committed state, so the resumed task restarts clean and nothing is lost. On any later landing (PR review, merge gate), halt and report — that is work the pipeline doesn't understand.

**Execution-complete signal.** When a task's review comes back clean, the orchestrator (SDD's controller) ticks that task's `- [ ]` checkboxes in the plan file and commits them, alongside SDD's ledger append. **Committed checkboxes are the durable, authoritative cross-session signal; SDD's `.superpowers/sdd/progress.md` ledger stays in-session scratch (it is git-ignored and dies with the worktree).** Execution is complete if and only if zero `- [ ]` remain in the plan at branch tip. Tie-break: if `git log` shows a task's commits but its boxes are unticked (a crash in the gap), verify via `git log`, tick the boxes, and do not re-implement.

**Review state.** After Stage 4's review has committed its fixes and the stage has pushed, post a PR comment whose **first line** is exactly the marker `dev-flow-worktree: review clean @ <full-head-sha>` — the SHA in full, nothing else on that line — with any report prose on the lines below. A comment is a marker **exactly when its first line has that form**; read the SHA from that line, never from a scan of the body, which also matches a report or comment that merely *quotes* a marker. The **operative** marker, when several match, is the latest by `createdAt` — `gh pr view <pr> --json comments` carries it and lists comments oldest-first, so it is the last match; never order by `id`, an opaque node ID there, not a number like a PR's. Detection: marker **valid** -> merge gate; marker present but **invalid** -> re-review; no marker -> PR review. (A label can't carry the SHA and goes silently stale — rejected.)

**Marker validity.** The marker is valid **iff** the marker SHA equals the current head, **or** every commit in `<marker-sha>..HEAD` carries the trailer `dev-flow-worktree-stripped: <slug>` **and** `git diff --no-renames --name-status <marker-sha> HEAD` contains only `D` entries (`--no-renames` pins the shape: by default git collapses a delete-plus-add pair into a single `R` entry — also invalidating, but the only-`D` read must not vary with the user's `diff.renames`. Judge the full listing, never `--diff-filter=D`, which silently hides the very entries that invalidate.), each for a path satisfying Docs policy's qualifying-path gates 1 and 3 — gate 2 ("exists at `HEAD`") is evaluated **at the marker SHA** here, since the paths being gone from head is the point. That second clause is a mechanical proof that the only change since the reviewed head is the intended deletion: any non-deletion entry, any deletion outside this branch's own scaffolding, or any trailer-less commit in the range invalidates it. It is unsatisfiable on a `commit`-policy run (no trailer commits can exist), so "any push, including a CI fix, correctly invalidates the marker" still holds everywhere it held before. The strip is verified by this rule, **not** by re-posting the marker — re-posting would assert "reviewed and suite-green at this SHA" for a SHA nothing reviewed, and would be fooled by an unrelated commit landing in the gap.

The trailer conjunct is mechanical, not eyeballed:

```sh
total=$(git rev-list --count "<marker-sha>..HEAD")                                          # failure or empty halts
stripped=$(git rev-list --count --grep='^dev-flow-worktree-stripped: <slug>$' "<marker-sha>..HEAD")  # failure or empty halts
[ "$total" -eq "$stripped" ]    # equal <=> every commit in the range carries the trailer
```

Both counts derive from the same range, so equality is exactly "every commit matched"; one trailer-less commit — a manual push, a merge from the default branch — breaks it. The grep is anchored at both ends so a prefix- or suffix-sharing slug cannot false-match. On inequality, the offending SHAs come from the same grep inverted: `git log "<marker-sha>..HEAD" --grep='^dev-flow-worktree-stripped: <slug>$' --invert-grep --format=%H`. Per Command discipline, `<marker-sha>` is validated non-empty before either command — an empty one collapses the range to `HEAD..HEAD`, where `0 -eq 0` would falsely validate.

**Resume table** (checks run top-to-bottom, first match wins; each is mechanical; "latest PR" = the highest-numbered result of `gh pr list --head <username>/<slug> --state all`):

| Check | Start at |
|---|---|
| No `<username>/<slug>` branch (local or origin); bare idea | Design: create branch+worktree, draft |
| No branch; existing design file given | Design: adopt (branch, front-matter, review — which commits) |
| Branch exists; latest PR is `MERGED` | Done — run Stage 5's Cleanup (idempotent), then report; nothing to resume |
| Branch exists; latest PR is `CLOSED` | Halt — a human closed PR #N without merging; report and hand back. Never silently re-create a PR over a human's close. |
| Branch exists; no design doc with `dev-flow-worktree` front-matter at tip | **No commits beyond `<base>`** (`git log "<default-ref>..<branch-ref>" --format=%H` empty — the ungrep'd form of the ownership scan; our just-created branch, Design crashed before committing) -> Design (redo; uncommitted drafts discarded). **`dev-flow-worktree-stripped: <slug>` trailer in `<default-ref>..<branch-ref>`** (the stripped state, per Docs policy; Branch ownership's detection command) -> **Merge gate** — the gate's ordinary steps handle it; there is no stripped-only entry point. **Otherwise foreign** (has commits beyond `<base>`, per Branch ownership) -> **Halt** — never adopt or delete a branch we didn't create |
| Design committed at tip; no plan doc at tip | Plan |
| Plan at tip has ≥1 unchecked `- [ ]` | Execute — resume at first unchecked task (cross-check ledger + `git log`) |
| Plan fully checked; no PR for the branch (`--state all` list empty) | PR: create + review |
| Open PR; no `review clean` marker, or the marker is **invalid** (Marker validity) | PR review |
| Open PR; marker **valid** (Marker validity — SHA equals head, or a proven strip since) | Merge gate (CI, `stops` from front-matter) |
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
- **Docs policy (intake):** resolve `docs` per the Artifact Contract's Docs policy — read `.claude/dev-flow.local.md`, apply the resolution table (emitting the one-line warning on an unrecognized value), and stamp the result into the design doc's `dev-flow-worktree` front-matter block alongside `slug` and `stops`. Do this **before** the review runs, so the review's rewrite carries it. A `docs` value already present in the front-matter wins outright — a resume never re-reads the settings file.
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

- `gh pr create`; PR body links the spec + plan paths and derives a summary from them. When the slug carries a task/issue ID (see Slug), reference it in the PR body — `Closes #42` for a GitHub issue, or the plain Linear/Jira key for those trackers. If an open PR already exists for the branch, reuse it — skip create.
- **Under `docs: strip`** (front-matter, per Docs policy), the PR body also carries one line noting that the design and plan live in this PR's commit history and are removed before merge by repo policy — so the linked paths will not exist on the default branch after the merge. Under `docs: commit` the body is unchanged.
- The **orchestrator** invokes `dev-flow-worktree:adversarial-review` (mode: `diff`) in-context (worktree as `working-dir`), passing Stage 3's unresolved Minor-findings list as caller-supplied findings. **This is the pipeline's final whole-branch review** (SDD's was suppressed in Stage 3). The review applies the resolved fixes, commits them on the branch, and (its contract) runs the project's test suite after fixing — from inside the worktree, so it tests the pipeline tree. The orchestrator checks the provenance line.
- **Post-fix test gate:** the marker may be posted only when the review reported the suite green — or reported that no automated suite exists (e.g. a prose-only repo). If for any reason the branch is red at head, halt; never post the marker on red. The marker therefore certifies **reviewed and suite-green (or no suite exists) at this exact SHA** — Stage 5 relies on this when a repo has no CI.
- Push the branch, then post the `dev-flow-worktree: review clean @ <full-head-sha>` marker comment.
- `pre-merge` stop -> halt and report (PR open, reviewed, fixes pushed) with the testing note and the resume invocation.

### Stage 5 — Merge

The merge gate is five steps and is **re-entrant**: step 4 can send the run back to step 1, so first run and resume travel the identical path and no resume-only entry point exists anywhere. Every git command in this gate is driven from inside the pipeline worktree (worktree entry, step 4).

1. **Push, then confirm the marker.** `git push` first — a no-op when already up to date, and it closes a real crash window: a crash between a strip *commit* and its *push* would otherwise merge the un-stripped remote head. Then confirm the marker is **valid** per the Artifact Contract's Marker validity rule. Invalid -> re-review, **unless the design doc is no longer at tip**, where re-review is impossible (there is no artifact to review against): halt and report the offending SHA(s) and that the doc is gone. That is what a stripped branch which has diverged past its strip commit gets — a specific, honest halt rather than a misleading foreign-branch one, and never a re-review the stripped state cannot support.
2. **Bounded CI wait** against the current head: run `gh pr checks <pr> --watch` under a hard cap (default 10 minutes, enforced via the Bash tool's `timeout: 600000`, since `gh pr checks --watch` has no native timeout of its own). Exactly four outcomes — distinguish failure from no-checks by output text, not exit code (both exit 1; pending exits 8):
   - **All checks pass** -> proceed.
   - **Any check fails** -> halt and report.
   - **Still pending at the cap** -> halt and report "CI still pending" (resume re-enters the merge gate for free). Never an open-ended block.
   - **Output contains "no checks reported"** (the repo has no CI on this PR) -> proceed. This is safe only because the marker already certifies Stage 4's test gate — suite green at this head, or no suite exists. Never read "no checks" as a green test signal on its own.
3. **Consult `stops`** from the design doc's front-matter at tip; a `pre-merge` stop pauses **here**, with the testing note — before any strip, so a halted branch is always intact and fully resumable with both docs at tip. In the stripped state there is no doc at tip and this read is not attempted: the recorded stops are empty by the stripped-state rule (Docs policy) — proceed, never halt. (A doc-less tip *without* the trailer cannot reach this step; step 1 already halted it.)
4. **Strip, if the policy says so.** If the design doc is absent at tip, this is the stripped state — step 1 halted every other doc-less branch — so the strip already ran: no-op. Otherwise read `docs:` from the front-matter at tip (the doc step 3 just consulted): `commit` -> no-op, with no gate evaluation — the default path never runs the base-ref fetch or `git merge-base`, so it cannot halt on plumbing (a shallow checkout that cannot compute a merge-base still merges under `commit`, exactly as it did before this policy existed). Only under `strip`: validate `merge_base` and evaluate Docs policy's qualifying gates — paths failing a gate are left alone, and if nothing qualifies, proceed. If any path qualifies: `git rm` the qualifying paths, commit with the trailer (`git commit -m "<msg>" --trailer "dev-flow-worktree-stripped: <slug>"`), push, and **re-enter this gate at step 1**. Re-entry terminates by construction: the next pass finds no doc at tip and no-ops here. The re-wait at step 2 is not optional politeness — where branch protection requires checks, GitHub demands they pass on the new head; where there is no CI, step 2 returns "no checks reported" and proceeds, exactly as before.
5. **Merge:** `gh pr merge <pr> --squash`. No `--delete-branch`, and no manual branch deletion — **the pipeline deletes no branches.** The merged **remote** branch is removed by the repository's *automatically delete head branches* setting (the standard GitHub configuration); the **local** `<username>/<slug>` branch is left for you to prune on your own schedule. (Cleanup below still removes the pipeline's own *worktree* — that is the pipeline's artifact, not your branch.)

- **Cleanup (idempotent — the resume table's Done row runs this same block; every step treats "already gone" as success):**
  1. `cd` to the main repo root.
  2. Remove the pipeline-created worktree: find its path in `git worktree list --porcelain` (the entry whose `branch` is `refs/heads/<username>/<slug>`), then `git worktree remove <path>` and `git worktree prune`. The provenance is the worktree's fixed path under `<main-root>/.claude/worktrees/dev-flow-<slug>` together with its branch: worktree-only mode plus the intake collision check mean the worktree on `refs/heads/<username>/<slug>` at that path is this feature's pipeline worktree — no separate provenance record exists or is needed. Ignored files (e.g. SDD's ledger) don't block removal; if stray *untracked* files do, they are scratch in a merged worktree — use `git worktree remove --force`. If tracked files have *uncommitted modifications*, halt and report instead — that is work the pipeline doesn't understand.

  Removing the worktree frees the branch (it is no longer checked out anywhere); the pipeline leaves the branch itself alone. The merged remote branch is auto-deleted by the repo's merge setting; the local `<username>/<slug>` branch remains for you to prune. (If a repo has that setting disabled, its merged remote branch simply remains — branch hygiene there is the repo's concern, not the pipeline's.)
- **Final report:** what shipped, the local branch left behind (`<username>/<slug>` — yours to prune), and every new issue filed across all stages.

---

## Environment Assumptions

- **Flat topology — the orchestrator is the only spawner.** Every subagent dev-flow-worktree spawns is a leaf; no subagent spawns a subagent. This is required, not a preference: whether a spawned subagent can itself spawn is a harness capability that has been withdrawn and restored across patch releases, and observing that it currently works is not permission to nest. So the orchestrator invokes every fan-out skill (`dev-flow-worktree:adversarial-review`, `subagent-driven-development`) in-context and spawns their worker leaves itself — always one level, works on every version.
- **GitHub remote** is assumed from Stage 4 onward (the pipeline uses `gh` for PR, review marker, CI, and merge). This matches the existing plugins' reliance on `gh`. (The `<username>` resolver *prefers* `gh api user` when a remote is reachable but falls back to git config, so Design and Plan still run with no remote.)

## Cross-Cutting Concerns

- **Context hygiene:** produce-subagents and every spawned review/implementer leaf run in fresh subagents returning short summaries; the orchestrator holds the fan-out controllers' state directly (the review's group loop, SDD's task loop), bounded by file handoffs and summaries and recoverable via resume.
- **Review provenance is checked, not assumed.** The orchestrator runs each review (Design, Plan, PR — not Execute) in-context, then reads the review's returned provenance line (`seeds: N× <tier>; resolvers: M× <tier>`) directly and halts if it is missing or its tiers violate `dev-flow-worktree:adversarial-review`'s Model section (seeds must be the seed tier, resolvers the resolver tier; a `resolvers: 0` line from a no-findings review passes the resolver check vacuously). The tiers are canonicalized by the review's family match, so this is a direct comparison — a cheap self-check that the review actually fanned out to separate reviewer subagents on the specified tiers, rather than folding into a single inline pass.
- **Failure handling:** a stage that cannot proceed cleanly halts and hands back with a clear report and resume invocation; the pipeline never merges work that is worse than what it started with.
- **Idempotent resume:** guaranteed by the Artifact Contract — every resume decision is a mechanical read of the branch tip or the PR.
- **Command discipline:** resolve git-internal paths through git (`git rev-parse --git-path …`), never as `.git/...` literals — `.git` is a file, not a directory, in any linked worktree. Capture, validate non-empty, and quote any command output a later command consumes; a failed producer halts the run and never substitutes an empty string — an empty variable silently *inverts* git predicates (an empty `<marker-sha>` turns `git rev-list <marker-sha>..HEAD` into the empty range `HEAD..HEAD`, a false "every commit matched"; an empty `<branch-ref>` turns `git log <default-ref>..<branch-ref>` back into a `HEAD`-relative scan, a false "no trailer"; an empty `<merge-base>` turns `git cat-file -e :<path>` into an index lookup that falsely succeeds).
- **Severity-independent, value-gated:** the protocol acts on issues of any severity but only applies a fix when it genuinely improves the codebase.
