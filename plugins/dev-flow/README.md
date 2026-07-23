# dev-flow

A single-invocation pipeline that carries a change from design through plan,
execute, PR, and merge autonomously, running a rigorous adversarial review at
each artifact boundary. The pipeline works directly on a dedicated feature
branch in your current checkout (no worktree). Default is full-auto to merge;
you can opt into a stop at any boundary. Each stage runs in a fresh subagent
and all pipeline state lives in durable artifacts (branch commits + the PR),
so a run resumes cleanly after any stop or crash.

Because it works in your current checkout, dev-flow switches you onto the
feature branch when a run starts. If you have uncommitted changes at that
moment, it stops and asks whether to proceed as-is, stash, or revert them —
it never silently touches your work. If you'd rather the pipeline never touch
your main checkout, use the `dev-flow-worktree` plugin, which runs the whole
flow in an isolated git worktree instead.

## Entry point

`dev-flow` is the only skill you invoke. It calls `adversarial-review`
internally at each stage boundary.

```
# from a bare idea (defaults to stop-after-design):
"run dev-flow: add rate limiting to the API gateway"

# from an existing design file (full-auto by default):
"run dev-flow on docs/superpowers/specs/2026-07-20-rate-limit-design.md"

# continue a paused or interrupted run:
"continue dev-flow on rate-limit"
```

The feature branch is named `<username>/<slug>`, where `<username>` is your
GitHub login (`gh api user`) when available, falling back to your git
`user.email` local-part offline.

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

1. Run `dev-flow` on a small real change and let it stop at `post-design`
   (the bare-idea default). Confirm it created and checked out the
   `<username>/<slug>` branch in your checkout, a design doc with `dev-flow`
   front-matter, and that `adversarial-review` ran against it.
2. Resume with `continue dev-flow on <slug>` and confirm it proceeds through
   plan and execute on the same slug.
