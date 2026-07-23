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

## How to smoke-test

1. Run `dev-flow-worktree` on a small real change and let it stop at
   `post-design` (the bare-idea default). Confirm it created the
   `<username>/<slug>` branch and a worktree under
   `.claude/worktrees/dev-flow-<slug>`, a design doc with
   `dev-flow-worktree` front-matter, and that `adversarial-review` ran
   against it.
2. Resume with `continue dev-flow-worktree on <slug>` and confirm it proceeds
   through plan and execute on the same slug.
