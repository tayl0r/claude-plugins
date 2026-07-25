---
dev-flow:
  slug: gh-6-docs-policy
  stops: [pre-merge]
---

# Per-repo policy for committing vs stripping design/plan scaffolding docs

Closes #6.

## Problem

dev-flow hardcodes one answer to the question *"does design/plan scaffolding land in
`main`?"* — it always commits `docs/superpowers/specs/*-design.md` and
`docs/superpowers/plans/*-plan.md` on the feature branch and carries them into the
merged PR.

That is correct for repos that want their design history in-tree. It is wrong for repos
that deliberately keep plan/design scaffolding out of `main`. Both are legitimate
conventions; the pipeline currently serves only the first, and offers no seam for the
second.

The right model is a **per-repo setting**, not a per-run guess and not a global default
flip.

## Requirements

1. A checkout can declare that dev-flow's scaffolding docs must not reach `main`.
2. Checkouts that say nothing behave exactly as they do today — bit for bit.
3. A strip removes **only this run's** docs. Never a path that predates the branch.
4. An interrupted run in the stripped state resumes correctly, without the user needing
   to know a rule about when it is safe to interrupt.
5. Both `dev-flow` and `dev-flow-worktree` inherit the behavior from one place.

### Non-goals

- Keeping the docs out of the repo tree entirely (never committed on any branch). See
  Rejected Alternatives.
- Unifying the two plugin variants. See Known Consequences — this is not deferred by
  choice, it is precluded by the distribution model, and tracked in #8.

## Decisions

### 0. Command discipline

Items 1–2 are standing rules, not this-design-only rationale: they land as a **Command
discipline** bullet in each SKILL.md's Cross-Cutting Concerns (exact text below), where
they bind every command either pipeline runs — this design's and every future
contributor's. This design is merely their first enforcement site; the previous review
round found six command defects, every one an instance of these two rules — the concrete
demand that earns them a durable home. Item 3 is worktree-specific and keeps its own
durable home: the worktree SKILL.md's worktree-entry enumeration (see Scope of edits).

1. **Git-internal paths are resolved through git** (`git rev-parse --git-path …`), never
   spelled as `.git/...` literals. `.git` is a *file*, not a directory, in any linked
   worktree — including one the user created themselves.
2. **Any output a later command consumes is captured, validated non-empty, and quoted;
   a failed producer halts the run.** It never substitutes an empty string. This is
   load-bearing, not style: an empty `<merge-base>` turns `git cat-file -e :P` into an
   *index* lookup that falsely **succeeds**, and turns `git log <merge-base>..HEAD` into
   the empty range `HEAD..HEAD` that falsely reports "no trailer." Both failures are
   silent and both invert the intended answer.
3. **In `dev-flow-worktree`,** every added command additionally falls under that skill's
   existing worktree-entry addressing rule: driven from inside the pipeline worktree, or
   explicitly addressed via `git -C <worktree-path>` and explicit refs.

The Cross-Cutting Concerns bullet, identical in both SKILL.mds:

> - **Command discipline:** resolve git-internal paths through git
>   (`git rev-parse --git-path …`), never as `.git/...` literals — `.git` is a file, not a
>   directory, in any linked worktree. Capture, validate non-empty, and quote any command
>   output a later command consumes; a failed producer halts the run and never substitutes
>   an empty string — an empty variable silently *inverts* git predicates (an empty
>   `<merge-base>` turns `git log <mb>..HEAD` into the empty range `HEAD..HEAD`, a false
>   "no matches", and turns `git cat-file -e :<path>` into an index lookup that falsely
>   succeeds).

### 1. The setting

`.claude/dev-flow.local.md` — the **plugin-settings pattern** (`.claude/<plugin>.local.md`:
YAML front-matter, user-local, git-ignored by definition), documented in the official
marketplace's `plugin-dev/skills/plugin-settings` skill. `dev-flow` is the family name
both variants share. Keys are bare; in this pattern the filename scopes the settings:

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

The default is `commit` because it is today's behavior and the resume-safe one. The
warning on an unrecognized value exists because a typo'd `strip` silently meaning
`commit` fails in the direction that surprises the user — scaffolding appears in `main`
after they believed they had turned it off.

**Both plugin variants read this same file and this same key.** The keep-vs-strip
question is about the repo's `main` — does scaffolding land there? — and its answer does
not change with the pipeline variant you invoked, so there is one file, not two: parallel
per-variant files would be two things for the same developer to keep in sync for a
question with one answer. Because the file is git-ignored, what it holds is each
developer's local declaration of the repo's convention, not a team-enforced fact — see
Known Consequences.

The strict `dev-flow:` / `dev-flow-worktree:` namespacing rule is untouched, because it
never applied here: it governs plugin-scoped front-matter blocks in *artifacts*, where
the branch-ownership predicate keys off the block name. The settings file is input, not
an artifact — no ownership read ever touches it — so it carries no plugin block at all,
per the pattern's bare-key convention.

One deliberate departure from the pattern is disclosed here: its Best Practices say the
filename should match the plugin name exactly, and for `dev-flow-worktree` this file
matches the *family* name instead. That practice exists so a settings file traces to its
consumer; a per-plugin pair would restore the letter of the rule at the cost of two files
answering one repo-level question — the drift this section already rejects. Both READMEs
name the shared file, which preserves the traceability the practice is for.

**Ignore enforcement.** The file is git-ignored by intent, but the *user* creates it, so
nothing guarantees it actually is. Per Command discipline, the exclude file is resolved
via git — a literal `.git/info/exclude` silently breaks in any linked worktree:

```sh
exclude_file=$(git rev-parse --git-path info/exclude)
grep -qxF '.claude/dev-flow.local.md' "$exclude_file" \
  || echo '.claude/dev-flow.local.md' >> "$exclude_file"
```

`--git-path` resolves to the main repository's shared `info/exclude` from any worktree,
so one write covers the main checkout and every worktree at once.

This runs as **step 0 of the branch-entry procedure** (worktree-entry in the sibling), not
once at intake. Entry runs at every stage boundary and the check is idempotent, so a
settings file created mid-run is excluded before any Execute-stage broad `git add` can
sweep it in. Ordering it ahead of the dirty-checkout gate also keeps a not-yet-excluded
settings file from tripping that gate as an untracked file. A local exclude, never a
committed `.gitignore` edit — which would itself pollute the PR diff.

In `dev-flow-worktree` this is an extension of existing machinery rather than new
machinery: its Create-step exclude-ensure for `.claude/worktrees/` moves to entry step 0
and covers both patterns in one block. Entry step 0 still precedes Create's
`git worktree add`, so the container is ignored before it exists.

### 2. Resolution happens once, at intake

Stage 1 reads the file and stamps the resolved value into the design doc's existing
front-matter block:

```yaml
---
dev-flow:
  slug: gh-6-docs-policy
  stops: []
  docs: strip
---
```

Each variant stamps into **its own** plugin-scoped block — the block that already holds
`slug` and `stops`: `dev-flow:` above, identically `dev-flow-worktree:` for the sibling.
The settings file's bare `docs:` key is shared input; the stamped key is plugin-scoped,
because the Artifact Contract's ownership predicate keys off the block name.

Every later stage reads **the artifact**, never the settings file again.

Precedence: front-matter (present on any resume) > settings file (first run only) >
default `commit`.

This follows the Artifact Contract's existing "state lives in artifacts" rule and mirrors
how `stops` already works. It matters more here than for `stops`: the settings file is
git-ignored, so it may not exist in the checkout where a run resumes, and a resumed run
must not silently flip policy.

`adversarial-review` already preserves front-matter across rewrites (its contract), so
the key survives every review.

### 3. The strip is verified, not trusted

**`<merge-base>` — shared by this decision and Decision 5 — is a validated variable,
never an inline substitution:**

```sh
git fetch origin "+refs/heads/<baseRef>:refs/remotes/origin/<baseRef>"  # failure halts
merge_base=$(git merge-base HEAD "origin/<baseRef>")                    # failure or empty halts
```

`<baseRef>` comes from `gh pr view --json baseRefName`, which is available everywhere
`<merge-base>` is consumed: the strip runs inside Stage 5, and the stripped-resume row
(Decision 5) is reachable only with an open PR — the MERGED and CLOSED resume rows match
first otherwise.

The explicit refspec, rather than a bare `git fetch origin <baseRef>`, is deliberate: in a
single-branch clone a bare fetch updates only `FETCH_HEAD` and leaves `origin/<baseRef>`
unresolvable. A checkout where fetch or merge-base still fails (offline, or shallow
history not containing the base) halts with the failing command's output — honestly,
instead of the silent false success an empty substitution produces.

Remove path `P` if and only if **all** of:

1. `P` matches `docs/superpowers/specs/*-<slug>-design.md` or
   `docs/superpowers/plans/*-<slug>-plan.md`.
2. `P` exists at `HEAD`.
3. `git cat-file -e "$merge_base:$P"` **fails** — i.e. `P` did not exist when this branch
   was created. With `merge_base` validated above the exit code is unambiguous: the ref
   is known-good and we are known to be in a repo, so a non-zero exit can only mean
   path-absent-at-merge-base.

Any path failing any gate is left alone. No `git rm -r` of a directory, ever.

Gate 3 is what actually prevents the failure issue #6 describes. Slug-scoping alone does
not: a previously shipped feature's docs can legitimately match the slug patterns, and
`git rm`-ing those would delete already-merged work.

Merge-base rather than base-tip is deliberate. If another feature added a matching path to
`main` *after* we branched, a base-tip test would report "exists on base" and we would
fail to remove our own copy. Merge-base is precisely "what this branch started from," so
the predicate reads exactly as intended: *this branch added it.*

Gate 1's globs are anchored only on the right, so a slug that is a hyphenated suffix of
another (`docs-policy` vs `gh-6-docs-policy` — realistic under the ticket-prefix slug
convention) glob-matches the longer slug's filename. Left as-is deliberately: gates 2–3
make the collision unreachable — a foreign feature's doc passes "exists at `HEAD` but not
at `<merge-base>`" only if this branch itself committed it, and removing what this branch
added is the predicate's stated intent. Tightening to the dated shape
(`????-??-??-<slug>-…`) would guard nothing reachable while forking from the ownership
predicate's `*-<slug>-design.md` shape — a second pattern to keep aligned. This analysis
covers Decision 4's validity clause too, which reuses these gates.

### 4. Marker validity, and a re-entrant merge gate

A strip commit moves the head, which collides with two existing rules: the
`dev-flow: review clean @ <sha>` marker goes stale, and the Artifact Contract says stale
means re-review. Re-review in the stripped state is incoherent — it would be a
`diff`-mode review of a branch whose design doc *and plan* are deleted, with no artifact
to review against; if it committed anything the head would move again; and Stage 5 could
then no longer read `docs:` at all. It cascades rather than self-correcting.

So marker validity is redefined once, at the shared boundary (the Artifact Contract's
"Review state" rule), and the strip **re-enters the gate** rather than running a private
tail. First run and resume then travel the identical path, and no resume-only entry point
exists anywhere.

Redefined at the boundary means every call site reads the new rule: the resume table's two
`Open PR` rows re-key from "marker SHA equals head" to Marker validity — the same two
generic routes, no new entry point — since with the old wording a crash between the strip
push and the merge routes to "PR review," the spurious re-review Acceptance Criterion 4
forbids.

**Marker validity** (replaces "marker SHA equals head"): the marker is valid iff the
marker SHA equals the current head, **or** every commit in `<marker-sha>..HEAD` carries
the trailer `dev-flow-stripped: <slug>` **and** `git diff --no-renames --name-status <marker-sha> HEAD`
contains only `D` entries (`--no-renames` pins the shape: by default git collapses a
delete-plus-add pair into a single `R` entry — also invalidating, but the only-`D` read
must not vary with the user's `diff.renames`. Judge the full listing, never
`--diff-filter=D`, which silently hides the very entries that invalidate.), each for a path matching Decision 3's slug patterns and failing
the merge-base test. Decision 3's "exists at `HEAD`" gate is evaluated **at the marker
SHA** here — the paths being gone from head is the point.

**The stripped state, defined once.** A branch is **stripped** iff the design doc is
absent at tip **and** at least one commit in `<merge-base>..HEAD` carries the
`dev-flow-stripped: <slug>` trailer (Decision 5's detection, using the validated
`merge_base` from Decision 3). In this state, front-matter reads have **defined answers,
not failed producers**: the recorded `stops` is empty — a recorded `pre-merge` stop halts
at step 3, *before* any strip, so no branch reaches the stripped state with a stop
outstanding — and `docs:` is never consulted, because step 4 short-circuits on the absent doc
before any policy read. This is the same move Decision 3's gate 3
already makes: once the surrounding state is validated (here, the trailer proven in
range), a negative probe is an unambiguous answer, and Decision 0 item 2's halt-on-failure
rule — which otherwise governs every read this design touches — is satisfied, not
suspended: nothing failed to produce. An absent doc **without** the trailer is not the
stripped state and keeps today's meaning exactly: foreign branch, halt.

The trailer conjunct is mechanical, not eyeballed:

```sh
total=$(git rev-list --count "<marker-sha>..HEAD")                                          # failure or empty halts
stripped=$(git rev-list --count --grep='^dev-flow-stripped: <slug>$' "<marker-sha>..HEAD")  # failure or empty halts
[ "$total" -eq "$stripped" ]    # equal <=> every commit in the range carries the trailer
```

Both counts derive from the same range, so equality is exactly "every commit matched"; one
trailer-less commit — a manual push, a merge from main — breaks it. The grep is anchored
both ends, like Decision 5's, so a prefix- or suffix-sharing slug cannot false-match. On
inequality, the offending SHAs step 1 must report come from the same grep inverted:
`git log "<marker-sha>..HEAD" --grep='^dev-flow-stripped: <slug>$' --invert-grep --format=%H`.
Per Command discipline, `<marker-sha>` is validated non-empty before either command — an
empty one collapses the range to `HEAD..HEAD`, where `0 -eq 0` would falsely validate.

**Stage 5, in full** (step 2 unchanged from today):

1. Push the branch (`git push`, a no-op when already up to date — this closes a real
   crash window: a crash between the strip *commit* and its *push* would otherwise merge
   the un-stripped remote head). Then confirm the marker is **valid** per the rule above.
   Invalid → re-review, **unless the design doc is no longer at tip**, where re-review is
   impossible: halt and report the offending SHA(s) and that the doc is gone.
2. Bounded CI wait against the current head → green (or "no checks reported").
3. Consult `stops` from the design doc's front-matter at tip. A `pre-merge` stop halts
   **here** — before any strip, so a halted branch is always intact and fully resumable.
   In the stripped state there is no doc at tip and this read is not attempted: the
   recorded stops are empty by the stripped-state rule above — proceed, never halt. (A
   doc-less tip *without* the trailer cannot reach this step: step 1 already halted it.)
4. If the design doc is absent at tip, this is the stripped state (step 1 halted every
   other doc-less branch) — the strip already ran; no-op. Otherwise read `docs:` from the
   front-matter at tip (the doc step 3 just consulted): `commit` → no-op, with no gate
   evaluation — the default path never runs the base-ref fetch or merge-base, so a shallow
   checkout still merges under `commit` exactly as today (Requirement 2). Only under
   `strip`: validate `merge_base` and evaluate Decision 3's gates; if any path qualifies,
   remove the qualifying paths, commit with the trailer `dev-flow-stripped: <slug>`
   (`git commit -m "<msg>" --trailer "dev-flow-stripped: <slug>"`), push, and **re-enter
   the gate at step 1**. Re-entry terminates by construction: the next pass finds no doc at
   tip and no-ops here.
5. `gh pr merge --squash`.

The strip is verified by the marker rule itself, not by re-posting the marker. Re-posting
would assert "reviewed and suite-green at this SHA" for a SHA nothing reviewed, and would
be fooled by an unrelated commit landing in the gap. The validity clause is a mechanical
proof that the only change since the reviewed head is the intended deletion: any
non-deletion entry, any deletion outside this branch's own scaffolding, or any
trailer-less commit in the range invalidates it. It is unsatisfiable on a `commit`-policy
run (no trailer commits can exist), so "any push, including a CI fix, invalidates the
marker" still holds everywhere it held before.

Re-entering the gate rather than running a private post-strip tail reuses the existing
bounded-wait block. That re-wait is not optional politeness: where branch protection
requires checks, GitHub demands they pass on the new head; where there is no CI, step 2
returns "no checks reported" and proceeds, exactly as before.

### 5. Resume stays correct in the stripped state

Between the strip commit and the merge, the branch tip carries no design doc. Under
today's ownership predicate that reads as **foreign**, and the user gets a halt telling
them to rename the slug or delete the branch — for a branch that is entirely ours and one
command from merging.

Issue #6 proposes documenting this as "once stripped, the branch is merge-only." That is a
rule the user must remember, enforced by nothing, whose violation produces a misleading
error — and it directly contradicts Requirement 4. Fix it instead, with one narrow clause:

> dev-flow also owns a branch if any commit in `<merge-base>..HEAD` carries the trailer
> `dev-flow-stripped: <slug>`.

Detection: `git log "$merge_base..HEAD" --grep='^dev-flow-stripped: <slug>$' --format=%H`
is non-empty, using the validated `merge_base` from Decision 3 (an empty one silently
yields the empty range `HEAD..HEAD`, which would report "no trailer" and produce exactly
the misleading foreign-branch halt this clause exists to prevent). The trailer is
plugin-scoped — `dev-flow-worktree-stripped: <slug>` for the sibling — matching how the
front-matter key is already namespaced.

The resume table's "no design doc at tip" row gains a third outcome:

| Tip state | Route |
|---|---|
| No commits beyond `<base>` | Design (redo) |
| **`dev-flow-stripped: <slug>` trailer in range — the stripped state (Decision 4)** | **Merge gate** |
| Otherwise | Halt — foreign |

Scanning the commit range rather than only the tip commit is free and strictly more
robust: it survives a stripped-state halt that the user pushed a commit on top of.

Ownership was **not** broadened to "the branch's history ever contained our design doc."
That would work, but it is inference, and it weakens a load-bearing safety guard for every
non-strip case in order to serve one. The trailer is explicit and fires only where it is
written.

A resumed stripped branch routes to the merge gate — the same generic target as every
other merge-gate resume, with **no special entry point**, because the gate's ordinary
steps handle the stripped state: step 1's validity clause proves the strip delta, step 2
waits on the stripped head, steps 3 and 4 resolve exactly as Decision 4's stripped-state
rule defines (no recorded stops; nothing qualifies), and step 5 merges. If the branch has
diverged past the strip commit, step 1's validity check fails and — since the design doc is
no longer at tip — the gate halts and reports the offending SHA(s) and that the doc is
gone: a specific, honest halt rather than a misleading "foreign branch" one, and never a
re-review, which the stripped state cannot support.

## Scope of edits

Prose only — these plugins contain no executable code.

| File | Change |
|---|---|
| `plugins/dev-flow/skills/dev-flow/SKILL.md` | Artifact Contract (settings resolution, front-matter schema, ownership clause, resume table rows (the no-design route, and both `Open PR` marker rows re-keyed to Marker validity), **marker-validity clause in Review state**), branch-entry step 0 (ignore enforcement), Stage 1 intake, **Stage 4 PR body** (under `docs: strip`, one line noting the docs live in the PR's commit history and are removed before merge by repo policy), Stage 5 sequencing, **Cross-Cutting Concerns (standing Command-discipline bullet — Decision 0 items 1–2)** |
| `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` | Same, with `dev-flow-worktree:` / `dev-flow-worktree-stripped:` naming — **plus Command discipline item 3**: every git command this design adds (fetch, merge-base, cat-file, `git rm`, the strip commit, `git diff --name-status`, the strip push) is cwd/branch-derived and joins worktree-entry's enumeration of commands driven from inside the pipeline worktree or explicitly addressed. The exclude-ensure moves per Decision 1. The Cross-Cutting Concerns bullet lands here too, identical (Decision 0 items 1–2); only item 3 is worktree-specific. **The port is a mechanism extension, not a rename.** |
| `plugins/dev-flow/README.md` | Document the setting and its consequences |
| `plugins/dev-flow-worktree/README.md` | Same |
| `plugins/dev-flow/.claude-plugin/plugin.json` | `2.1.0` → `2.2.0` |
| `plugins/dev-flow-worktree/.claude-plugin/plugin.json` | `1.3.0` → `1.4.0` |

Version bumps are required, not cosmetic: the plugin cache is version-keyed, so a re-sync
will not pick up behavior changes at an unchanged version.

## Known consequences (accepted)

- **The policy is per-developer, not per-team.** `.claude/dev-flow.local.md` is
  git-ignored by the pattern's definition, so a teammate without the file commits the
  docs. Chosen knowingly over a committed policy file plus a local override. On a
  multi-committer repo the docs tree can become a mix of stripped and committed
  scaffolding with no signal distinguishing policy from accident.
- **Merging outside Stage 5 skips the strip.** A `pre-merge` stop followed by a merge in
  the GitHub UI lands the docs in `main`. The pipeline cannot prevent this; the README
  says so.
- **A stripped PR's body links paths that no longer exist after merge.** Rejected the fix
  (rewrite the body at marker-post time to pin SHA permalinks): it adds a step to Stage 4
  to repair two dead links in a merged PR body — a fix roughly as costly as the wart.
  Instead, under `docs: strip` the PR body carries one free line noting the docs live in
  the PR's commit history and are removed before merge by repo policy.
- **The change lands twice**, and that duplication is forced by the plugin distribution
  model rather than deferred by choice: each variant installs independently into a
  version-keyed cache directory containing only its own files (a user can install one
  without the other), so no runtime path to a shared file exists — and the mirrored prose
  is deliberately namespaced (`dev-flow:` / `dev-flow-stripped:` vs the worktree twins),
  so even a source-level shared file would need a templating step this prose-only repo
  does not have. Drift control is #8; this change lands twice and relies on that issue's
  check to keep the intentionally identical pair identical.

## Rejected alternatives

**Docs never enter the repo tree.** Every resume decision in the Artifact Contract is
"read the doc at branch tip," so this requires replacing the durable state store outright,
and reviewers lose sight of the design entirely. Far more surgery than the problem
justifies.

**Docs on a side ref** (`refs/dev-flow/<slug>/`), pushed to origin, never merged. Preserves
durability and keeps `main` clean, but invents a storage mechanism, and the design still
vanishes from the PR. Rejected for the same reason: cost out of proportion to the problem.

**Strip at the end of Stage 4** instead of at merge. Materially simpler — Stage 5 untouched,
one CI wait. Rejected because the `pre-merge` stop exists precisely so a human can look at
the PR, and this variant shows them a PR with the design already deleted. Simplicity that
degrades the one case where a human is present is not worth it.

**Per-run invocation flag only**, with no settings file. Zero new machinery, but it makes
the choice a per-run decision the user must remember every time — the failure mode the
issue was filed about.

**Patching the resume row to say "enter at step 5"** instead of redefining marker validity.
Leaves the "stale SHA → re-review" rule lying about itself with a silent exception in
another section, and leaves a remembered entry point every future path to the gate must
repeat. The validity clause dissolves the problem instead of routing around it.

**A shared prose file across the two plugins.** Physically impossible under the
distribution model — see Known Consequences and #8.

## Acceptance criteria

1. A checkout with `docs: strip` merges a dev-flow PR whose net diff contains no
   `docs/superpowers/` paths.
2. Scaffolding from previously shipped features on `main` is untouched by that strip,
   including when a prior feature's docs match the slug patterns.
3. A checkout with no settings file, or with `docs: commit`, behaves exactly as it does
   today — Stage 5 steps 1–3 and 5 are identical, and step 4 reads `docs: commit` and
   no-ops without evaluating gates: no base-ref fetch, no merge-base, no strip commit, no
   trailer, no head movement. A shallow checkout that cannot compute a merge-base still
   merges under `commit`.
4. Interrupting a `strip` run anywhere between the strip commit and the merge, then
   resuming, re-enters the merge gate and completes — no foreign-branch halt, no spurious
   re-review, and no rule the user had to know.
5. A `pre-merge` stop under `docs: strip` leaves the branch intact, with both docs at tip.
6. `.claude/dev-flow.local.md` never appears in a PR diff, including when it is created
   mid-run.
7. Every command this design adds behaves correctly when run from a linked worktree.

## Smoke test

Re-sync the installed plugin cache first — the runtime loads
`~/.claude/plugins/cache/.../dev-flow/<version>/`, not this repo.

1. In a scratch repo with CI and a pre-existing `docs/superpowers/specs/` doc from an
   earlier feature (deliberately matching the slug patterns), write
   `.claude/dev-flow.local.md` with `docs: strip`.
2. Run dev-flow full-auto on a small change. Confirm the merged commit contains no
   `docs/superpowers/` paths, and the pre-existing doc is still on `main`.
3. Re-run with `stops: [pre-merge]`. Confirm the halt leaves both docs at tip.
4. Interrupt a `strip` run twice — once killing **after** the strip push, once killing
   **between the strip commit and the push**. Resume each; confirm both re-enter the merge
   gate and merge, and that the second does not merge an un-stripped remote head.
5. Create `.claude/dev-flow.local.md` mid-run (after intake) and confirm it never reaches
   the PR diff.
6. Repeat step 2 under `dev-flow-worktree`, confirming the exclude-ensure and every added
   git command work from the linked worktree.
7. Delete the settings file and re-run. Confirm the docs are committed and reach `main`.
