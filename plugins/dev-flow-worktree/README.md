# dev-flow-worktree

A single-invocation pipeline that carries a change from design through plan,
execute, PR, and merge autonomously, running a rigorous adversarial review at
each artifact boundary. The whole run is isolated in a dedicated git worktree,
so your main checkout is never switched or touched. Default is full-auto to
merge; you can opt into a stop at any boundary. Each stage runs in a fresh
subagent and all pipeline state lives in durable artifacts (branch commits +
the PR), so a run resumes cleanly after any stop or crash.

This is the worktree-isolated variant of `dev-flow`. If you'd rather the
pipeline work directly on a branch in your current checkout (no worktree),
use the `dev-flow` plugin instead.

## Entry point

`dev-flow-worktree` is the only skill you invoke. It calls
`adversarial-review` internally at each stage boundary.

```
# from a bare idea (defaults to stop-after-design):
"run dev-flow-worktree: add rate limiting to the API gateway"

# from an existing design file (full-auto by default):
"run dev-flow-worktree on docs/superpowers/specs/2026-07-20-rate-limit-design.md"

# continue a paused or interrupted run:
"continue dev-flow-worktree on rate-limit"
```

The feature branch is named `<username>/<slug>`, where `<username>` is your
GitHub login (`gh api user`) when available, falling back to your git
`user.email` local-part offline. If you name a task/issue ID in the request
(a Linear/Jira key like `ENG-1421` or a GitHub issue `#42`), it is folded
into the slug for traceability — e.g. `<username>/eng-1421-rate-limit`.

On merge, dev-flow-worktree **deletes no branches**: your repo's
auto-delete-on-merge setting removes the remote branch, and the local branch
is left for you to prune (Cleanup still removes the pipeline's own worktree).
It never touches a branch it can't prove it created (one whose history
carries its design doc), so it halts rather than build on a foreign branch of
the same name.

## Stops

| Stop | Effect |
|---|---|
| `post-design` | Halt after the design is reviewed, rewritten, and committed. |
| `post-plan` | Halt after the plan is reviewed, rewritten, and committed. |
| `pre-merge` | Run everything through the reviewed PR, then halt before `gh pr merge`, with a testing note. |

Bare-idea entry defaults to `post-design` (a guessed design shouldn't go
straight to merge); design-file entry defaults to full-auto (the file you
wrote is your approval). Stops are recorded in the design doc's front-matter
so resume honors them; every halt prints the exact resume invocation.

`adversarial-review` is internal machinery but can also be invoked standalone
on any existing design/plan/PR.

## Design and plan docs: commit or strip

By default, dev-flow-worktree commits its design doc
(`docs/superpowers/specs/…-design.md`) and its plan
(`docs/superpowers/plans/…-plan.md`) on the feature branch, and the squash
merge carries both into your default branch. If your repo deliberately keeps
that scaffolding out of `main`, say so once per checkout in
`.claude/dev-flow.local.md`:

```yaml
---
docs: strip      # commit | strip
---
```

Under `docs: strip` the docs are still written, reviewed, and committed on the
feature branch — the PR shows them, and a `pre-merge` stop leaves them in place
for you to read — but the merge gate removes them in a final commit just before
merging, so nothing under `docs/superpowers/` reaches your default branch. The
removal is scoped to paths **this branch added**: a doc that already existed
when the branch was created is never touched, even if its filename matches.

An absent file, `docs: commit`, or an unrecognized value all resolve to
`commit`, so a checkout with no settings file behaves exactly as it did
before (the unrecognized case also prints a one-line warning naming the bad
value, so a typo'd `strip` doesn't silently commit your docs).

The same file and the same key serve both `dev-flow` and `dev-flow-worktree`:
the question is about your repo's default branch, so it has one answer per
repo, not one per plugin. The file keeps the family name `dev-flow` for that
reason, even here. dev-flow-worktree adds `.claude/dev-flow.local.md` to your
repository's local `info/exclude` at every stage boundary, so it never shows
up in a PR diff — even if you create it mid-run.

Three consequences worth knowing:

- **The policy is per-developer, not per-team.** The settings file is
  git-ignored by definition, so a teammate without it commits the docs. On a
  multi-committer repo the docs tree can become a mix of stripped and
  committed scaffolding with no signal distinguishing policy from accident.
- **Merging outside the pipeline skips the strip.** If you take a `pre-merge`
  stop and then merge in the GitHub UI, the docs land in your default branch.
  The pipeline cannot prevent that.
- **A stripped PR's body links paths that stop existing after merge.** Under
  `docs: strip` the PR body says so: the docs live in the PR's own commit
  history.

## How to smoke-test

1. Run `dev-flow-worktree` on a small real change and let it stop at
   `post-design` (the bare-idea default). Confirm it created the
   `<username>/<slug>` branch and a worktree under
   `.claude/worktrees/dev-flow-<slug>`, a design doc with
   `dev-flow-worktree` front-matter, and that `adversarial-review` ran
   against it.
2. Resume with `continue dev-flow-worktree on <slug>` and confirm it proceeds
   through plan and execute on the same slug.
3. Write `.claude/dev-flow.local.md` with `docs: strip` and run
   dev-flow-worktree full-auto on a small change in a repo that already
   has an unrelated doc under `docs/superpowers/specs/`. Confirm the
   merged commit contains no `docs/superpowers/` paths, the pre-existing
   doc is still on the default branch, and `.claude/dev-flow.local.md`
   never appeared in the PR diff. Then delete the settings file and
   re-run: the docs should be committed and reach the default branch as
   before. Confirm the same run from the linked worktree — the exclude
   and every git command the merge gate runs must work from there, not
   just from the main checkout.
