---
dev-flow:
  slug: gh-48-version-collision
  stops: [post-design]
  docs: commit
---

# gh-48 — a PR check that every touched plugin's version is ahead of what `main` published

Close **#48** with a new `scripts/check-version-bump.py`, a new `.github/workflows/check-version-bump.yml` that runs it on every pull request against the base branch's tip, and one appended sentence on `CLAUDE.md` line 7 telling contributors what the number must be ahead of.

Three files change, two of them new. **No plugin file, no `plugin.json`, no version bump** — each a conclusion, not a deferral (*Out of scope*).

The issue's decisive question — *CI or dev-flow's merge gate?* — is answered **CI**, on evidence gathered below and summarised here: dev-flow ships into arbitrary repos where `plugins/*/.claude-plugin/plugin.json` does not exist, so a marketplace-shaped check has no home in its `SKILL.md`; dev-flow's merge gate **already consumes CI** (*"**Any check fails** -> halt and report"*), so a CI check enforces itself inside every dev-flow run with no dev-flow change at all; and CI additionally binds the paths dev-flow does not — a hand-merged PR, a `gh pr merge` typed by hand, a PR merged from the web UI. The one thing the merge gate would have bought — evaluation strictly at merge time — it would have bought only for dev-flow's own merges, which are the least likely to need it (*Rejected: dev-flow's merge gate*).

## Scope check — one subsystem, three files

One subsystem: this repo's mechanical pre-merge checks, the same subsystem `2d59aeb` (#13) created when it added `scripts/check-sync.py` and the workflow that runs it. #48 asks one question — *where does the published-version comparison live, and what exactly does it compare?* — and the answer is one script, one workflow, one appended sentence, with no ordering dependency on anything else. Nothing decomposes further.

The issue's cross-link to #33 (*always the minor segment*) is context, not a second change: #33's ruling is what makes this collision deterministic, and the issue itself already rules that this is not an argument against the rule. Nothing here touches the minor-always convention.

## What is true today, measured at `52c3883`

Every measurement in this section is of the tree **before** this change, pinned to `52c3883` (this branch's base, `origin/main`), given with the command that printed it, run while this document was written. No number appears that its command's output does not show.

### The incident, verified in-tree

All four commits the issue names exist and say what it says they say.

```sh
git log -1 --format='%h %ad %s' --date=iso 4e672e2
git log -1 --format='%h %ad %s' --date=iso 9a5cab2
git log -1 --format='%h %ad %s' --date=iso 963a66c
git log -1 --format='%h %ad %s' --date=iso 5f99cf2
git log -1 --format='%h %ad %s' --date=iso 84d8cc9
git log -1 --format='%h %ad %s' --date=iso 02ffb7b
```

```text
4e672e2 2026-08-02 13:30:06 -0700 Bump dev-flow to 2.7.0 and dev-flow-worktree to 1.9.0
9a5cab2 2026-08-02 14:46:13 -0700 dev-flow: re-anchor the flat-topology bullet to a version-independent reason; record ADR-0003 (#35)
963a66c 2026-08-02 14:58:22 -0700 Share the design-block reader, keep the mapping per change (#24) (#36)
5f99cf2 2026-08-02 15:05:03 -0700 dev-flow 2.7.0, dev-flow-worktree 1.9.0
84d8cc9 2026-08-02 15:21:30 -0700 Merge remote-tracking branch 'origin/main' into tayl0r/gh-28-29-review-prose
02ffb7b 2026-08-02 15:23:43 -0700 dev-flow 2.8.0, dev-flow-worktree 1.10.0 — re-target past merged bumps
```

The ordering is worth stating precisely, because it is stronger than the issue claims. `9a5cab2` is the squash of `4e672e2`'s branch onto `main`, so **`main` published `2.7.0` / `1.9.0` at 14:46**. Branch `tayl0r/gh-28-29-review-prose` wrote its own `2.7.0` / `1.9.0` at **15:05**, after that. The number was already stale when it was typed — not only when it was merged.

Both branches made the identical change:

```sh
git show 4e672e2 -- plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json | grep -E '^[+-].*version'
git show 5f99cf2 -- plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json | grep -E '^[+-].*version'
```

```text
-  "version": "1.8.0",
+  "version": "1.9.0",
-  "version": "2.6.0",
+  "version": "2.7.0",
-  "version": "1.8.0",
+  "version": "1.9.0",
-  "version": "2.6.0",
+  "version": "2.7.0",
```

And the merge produced no reviewable row:

```sh
git show 84d8cc9 --format='parents=%P' --stat -- plugins/
git show 84d8cc9:plugins/dev-flow/.claude-plugin/plugin.json
```

```text
parents=9447d389f532bddefbb138e7225ac98dd81f6110 963a66c1949dc38d82077bab6701e17147f8e5d3

 plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md | 2 +-
 plugins/dev-flow/skills/dev-flow/SKILL.md                   | 2 +-
 2 files changed, 2 insertions(+), 2 deletions(-)
{
  "name": "dev-flow",
  "version": "2.7.0",
  "description": "Autonomous design -> plan -> execute -> PR -> merge pipeline (works on a feature branch in your checkout) with adversarial review at each artifact boundary"
}
```

Two plugin files in the merge's diff against its first parent, and **no `plugin.json` row** — exactly the issue's report. The version at that tip is `2.7.0`, a number `main` had carried since 14:46.

### The proposed check, run against the incident

The predicate is: *for every plugin directory this change contributes a path under, the version at the head is strictly greater than the version at the base ref's **tip***. Run against `84d8cc9` with `963a66c` — `origin/main` as it stood at 14:58, three minutes before the merge-in — the prototype of the script this design ships printed:

```text
check-version-bump: base 963a66c19, head 84d8cc9c8, merge-base 963a66c19
  dev-flow             2.7.0 -> 2.7.0 ... FAIL
  dev-flow-worktree    1.9.0 -> 1.9.0 ... FAIL

dev-flow: version "2.7.0" is not ahead of the base ref's "2.7.0", and this change
touches plugins/dev-flow/. The install cache is keyed on the version string, so
the new text would never be picked up on re-sync.

  plugins/dev-flow/.claude-plugin/plugin.json

dev-flow-worktree: version "1.9.0" is not ahead of the base ref's "1.9.0", and this change
touches plugins/dev-flow-worktree/. The install cache is keyed on the version string, so
the new text would never be picked up on re-sync.

  plugins/dev-flow-worktree/.claude-plugin/plugin.json

Bump past the base ref's version, not past your branch's. A concurrent change
may have published your next number already, and the merge has nothing to flag
-- both sides made the identical change, so there is no conflict to resolve.
check-version-bump: 2 of 2 compared plugin directories failed
```

exiting `1`, and transcribed exactly as printed. Two properties of that run are load-bearing and neither is obvious:

- **The touched set survives the merge-in.** The merge's diff against its first parent has no `plugin.json` row, but the *merge-base* diff still contributes `plugins/dev-flow/…` and `plugins/dev-flow-worktree/…` paths, so both directories count as touched. A check triggered on *"the PR changes a `plugin.json`"* would have seen nothing and passed. This is the single most important design detail here.
- **The comparison is against the base's tip, not the merge base.** At `84d8cc9` the merge base *is* `963a66c`, so the two coincide; at `5f99cf2`, before the merge-in, they do not — and the check still fires, because the tip is what published `2.7.0`:

  ```text
  check-version-bump: base 963a66c19, head 5f99cf286, merge-base c8b2182a4
    dev-flow             2.7.0 -> 2.7.0 ... FAIL
    dev-flow-worktree    1.9.0 -> 1.9.0 ... FAIL
  ```

  So the check fires at the **15:05 push**, not merely at the 15:21 merge-in. The window it needs is not narrow.

Against the actual fix, `02ffb7b`, it printed:

```text
check-version-bump: base 963a66c19, head 02ffb7bca, merge-base 963a66c19
  dev-flow             2.7.0 -> 2.8.0 ... OK
  dev-flow-worktree    1.9.0 -> 1.10.0 ... OK
check-version-bump: 2 compared, 0 skipped ... OK
```

exiting `0`. That row also shows why the comparison cannot be a string comparison: `1.9.0 -> 1.10.0` is a legal bump, and `"1.10.0" < "1.9.0"` as strings. This is not hypothetical — the marketplace already ships past a two-digit minor:

```sh
git grep -h -F '"version"' 52c3883 -- 'plugins/*/.claude-plugin/plugin.json' | sort | uniq -c
```

```text
   6   "version": "1.0.0",
   1   "version": "1.12.0",
   1   "version": "2.10.0",
```

### What the check would have done to everything already merged

Every commit on `main` is a squash, so each one's parent **is** `main`'s tip at the moment it merged. Running the check with `(base = C^, head = C)` over `main`'s history is therefore an exact replay of what it would have concluded at each merge:

```sh
python3 - <<'PY'
import subprocess
def git(*a): return subprocess.run(("git",)+a, capture_output=True, text=True, check=True).stdout
rejected, n = [], 0
for line in git("log", "--first-parent", "--format=%H %s", "52c3883").strip().split("\n"):
    sha, subj = line.split(" ", 1)
    parents = git("rev-parse", sha + "^@").split()
    if len(parents) != 1:
        continue
    n += 1
    if subprocess.run(["python3", "scripts/check-version-bump.py", parents[0], sha],
                      capture_output=True, text=True).returncode:
        rejected.append((sha[:7], subj[:52]))
print("commits with exactly one parent, at 52c3883:", n)
print("rejected by the check:", len(rejected))
for row in rejected:
    print("   %s  %s" % row)
PY
```

```text
commits with exactly one parent, at 52c3883: 32
rejected by the check: 3
   95dfd3d  dev-flow: guarantee the model-diverse review (never 
   e987265  Split dev-flow reviewer tiers: seeds on sonnet, reso
   b900f61  Add --prune to fetch commands in sync-latest-git ski
```

All three are **true positives from before the convention existed**. They edited a plugin's shipped text at an unchanged version — `95dfd3d` and `e987265` both left `dev-flow` at `1.0.0` while rewriting its `SKILL.md`s, `b900f61` left `sync-latest-git` at `1.0.0` while editing its skill — which is the cache-invisibility failure `CLAUDE.md` line 7 was later written to prevent. It was written at `1f359e2`:

```sh
git log --oneline -S'Bump `version` in' 52c3883 -- CLAUDE.md
```

```text
1f359e2 CLAUDE.md: document repo layout, plugin gotchas, and validation (#12)
```

Restricting the same replay to `1f359e2^..52c3883` printed:

```text
commits at or after 1f359e2 (the commit that wrote the bump rule): 17
rejected: 0 []
```

**Zero false positives across every change merged since the rule was written down.** That is the friction measurement the touched-set rule needs, and it is the reason that rule can be the blunt one (*Assumption A2*).

### Where a check could live, measured

The repo has exactly one workflow, and it runs exactly one thing:

```sh
git ls-tree -r --name-only 52c3883 -- .github/
git show 52c3883:.github/workflows/check-sync.yml
```

```text
.github/workflows/check-sync.yml
name: check-sync
on:
  pull_request:
  push:
    branches: [main]
permissions:
  contents: read
jobs:
  check-sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python3 scripts/check-sync.py
```

CI exists, runs on `pull_request`, and needs no secrets. Nothing named `check-version` exists anywhere in the tree:

```sh
git grep -c -F 'check-version' 52c3883
```

That command printed nothing and exited 1.

### dev-flow's merge gate already consumes CI

This is the fact that settles the CI-versus-merge-gate question, and it ships in both pipelines today:

```sh
git grep -c -F '**Any check fails** -> halt and report.' 52c3883 -- plugins/
```

```text
52c3883:plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md:1
52c3883:plugins/dev-flow/skills/dev-flow/SKILL.md:1
```

Merge-gate step 2 runs `gh pr checks <pr> --watch` and halts on any failing check. So a red CI check **is** a dev-flow merge-gate halt, in both variants, with no edit to either `SKILL.md` and no version bump. Everything the merge-gate option would have bought inside a dev-flow run, the CI option already has.

### Nothing is *required* today

```sh
gh api repos/tayl0r/claude-plugins/branches/main/protection
gh api repos/tayl0r/claude-plugins/rulesets
gh api repos/tayl0r/claude-plugins --jq '{allow_update_branch, delete_branch_on_merge}'
```

```text
{"message":"Branch not protected","documentation_url":"https://docs.github.com/rest/branches/branch-protection#get-branch-protection","status":"404"}
[]
{"allow_update_branch":false,"delete_branch_on_merge":true}
```

No branch protection, no rulesets. `check-sync` is advisory to a human and binding only on a dev-flow run, via the merge gate above. **The new check inherits exactly that posture** — which is a fact to state, not a gap this change opens (*The residual*).

## The decision

**A CI check on the pull request: a new `scripts/check-version-bump.py` invoked by a new `.github/workflows/check-version-bump.yml`, plus one appended sentence on `CLAUDE.md` line 7.**

The predicate, stated once:

> For every plugin directory `plugins/<name>/` that the change contributes at least one path under — computed as `git diff --name-only -z --no-renames $(git merge-base <base> <head>) <head>`, so that neither a path's own bytes nor a git config can shrink that set — the `version` in `plugins/<name>/.claude-plugin/plugin.json` at `<head>` must be strictly greater, compared as a tuple of integers, than the `version` at the **tip of `<base>`**. Both versions must be `X.Y.Z`; any other shape halts rather than being ordered. A plugin with no manifest at the base (newly added) or none at the head (removed) is skipped.

Four consequences worth naming, because each answers a question the issue or its reviewers will ask:

- **A PR that touches no plugin directory passes vacuously.** That includes this very change, and every `CLAUDE.md` / `CONTEXT.md` / `docs/` / `scripts/` change in the repo's recent history.
- **The mirrored `dev-flow` / `dev-flow-worktree` pair is handled by construction.** They are two plugin directories with two manifests, so a change touching both must bump both — which is precisely what the incident needed, and what every post-`1f359e2` merge touching both already did — the replay rejected none of them.
- **The check enforces `CLAUDE.md` line 7's bump rule as well as collision-freedom.** You cannot ask *"is this ahead of what `main` published?"* without also asking *"was it bumped?"* — they are one predicate. The replay above measures the cost of that at zero for every change merged since the rule was written, and the issue itself frames the defect as *"precisely the consequence `CLAUDE.md:7`'s existing sentence exists to prevent."*
- **The version number is the whole check.** No comparison of *content* is attempted — no "the plugin's tree changed, therefore…". The install cache is keyed on the version string alone, so the version string is the entire correctness surface, and a content comparison would only add a way to be wrong.

### Rejected: a check inside dev-flow's merge gate

The issue names this as one of two plausible homes. It is the wrong one, on four grounds; the first is decisive on its own.

**1. dev-flow ships into arbitrary repos, and `plugins/*/.claude-plugin/plugin.json` exists in one of them.** A `SKILL.md` is read into every invocation of that skill in whatever repo it runs. A rule about *this marketplace's* manifest layout, run in a Rails app or a Rust crate, is at best inert text costing context and at worst a step that halts a pipeline on a path that will never exist. This repo has already ruled exactly this way once, in `52c3883`'s own design (#39), rejecting a move of repo-local instruments into `plugins/` because *"dev-flow ships into arbitrary repos"* and *"none of the three exists in any repo but this one."* The same ground reaches here unchanged, and it is the reason the merge gate cannot host the check even in principle.

**2. It would bind fewer paths, not more.** dev-flow's merge gate governs a dev-flow run. A hand-typed `gh pr merge`, a PR merged from the GitHub web UI, a branch someone finished by hand after a `pre-merge` stop — none of them pass through it. CI runs on `pull_request` regardless of who or what opened the PR.

**3. Its one genuine advantage is narrow, and it misses the merges that need it most.** The merge gate runs immediately before `gh pr merge`, so a check there is evaluated at merge time and closes the staleness window a push-time check leaves open (*The residual*). That advantage is real and is stated rather than argued away. But it closes the window only for merges that go through dev-flow — and those are the *least* likely to be stale, because a dev-flow run pushes review fixes at Stage 4 and its marker certifies a SHA, so reaching the merge gate on a head that predates the base's advance takes a run in which nothing was pushed after it. The merge most likely to trust a stale green check is the hand-typed one, and the merge gate never sees it. Closing the window for every path is one branch-protection setting, and that setting closes it for a CI check too.

**4. It costs a version bump on the mirrored pair — in the change that exists to fix version collisions.** The two pipeline `SKILL.md`s are a hand-mirrored pair, so this option means two hand-mirrored edits and two `plugin.json` bumps, both of which are exposed to the very race being fixed and neither of which any check yet covers. The CI option touches nothing under `plugins/` and moves no version.

### Rejected: both, with CI primary

Considered because the dispatch asks for it, and because "defence in depth" is superficially attractive. Refused: ground 1 above is not a cost to be weighed against a benefit, it is a correctness objection, and it applies to the merge-gate half whether or not the CI half also exists. Adding a second copy of the rule in a place where it is wrong does not become right because a correct copy exists elsewhere. What is genuinely wanted from "both" — a dev-flow run refusing to merge on this failure — is already delivered by the CI option through merge-gate step 2 (*dev-flow's merge gate already consumes CI*), with no second copy of anything.

### Rejected: inside `scripts/check-sync.py`

The issue rules this out and its reasons hold: `check-sync.py` documents itself as *"Two independent checks, one command, no flags"* over in-tree facts, has no remote, and would fail in a fresh clone with nothing fetched. A **sibling** script sidesteps all three — the base ref arrives as `argv`, so the script has no opinion about remotes and no default to be wrong about — but it stays a sibling, not a third check inside `check-sync.py`, because `check-sync.py`'s contract is that it runs anywhere with no arguments and this one cannot.

### Rejected: a second job inside `.github/workflows/check-sync.yml`

Fewer files, but a worse seam. `check-sync.yml` triggers on `pull_request` **and** `push: branches: [main]`, and on `main` the version legitimately equals `origin/main`'s — the issue names this case explicitly. Sharing the file means guarding the new job with `if: github.event_name == 'pull_request'`, and a job that does not run reports as skipped, which does not fail a PR. So the failure mode of getting that expression wrong is *the check silently disappears while the PR stays green* — the exact class of silent pass this issue is about. A separate file with `on: pull_request` has no expression to get wrong. It also lets the new job take `fetch-depth: 0` without slowing the push-to-`main` run of `check-sync`, and keeps `check-sync.yml` byte-identical so its green history is untouched.

Running the check on `main` anyway was considered and refused for a second reason: there, head and base are the same commit, the touched set is always empty, and the result is unconditionally green. A criterion that cannot fail is one this repo's own review tier is instructed to report.

### Rejected: triggering on a change to `plugin.json` rather than to the plugin directory

The natural first guess, and it **misses the reported bug entirely**. After the merge-in at `84d8cc9`, the branch's `plugin.json` differs from neither side — that is the whole point of the issue. Measured above: the merge's diff against its first parent contains two `SKILL.md` rows and no `plugin.json` row. The touched set has to be computed from the directory.

### Rejected: comparing against the merge base rather than the base tip

Equally natural, equally wrong, and wrong in the direction that produces a silent pass. Against the merge base, branch B's `2.6.0 -> 2.7.0` is a perfectly good bump; it is only against `main`'s *tip* that `2.7.0` is already taken. "Strictly greater than `origin/main`'s" is the issue's own phrasing and it means the tip.

### Rejected: excluding `plugins/<name>/README.md` from the touched set

A README edit is arguably not a behaviour change, so the blunt rule asks for a bump it does not strictly need. Refused, on three grounds: the exclusion list is a thing to maintain and to get wrong; the cost of an unnecessary bump is zero, since `CLAUDE.md` line 7 already says *"Nothing reads the segment (the cache keys the whole string)"*; and a README-only edit at an unchanged version would have been rejected by the replay, which rejected **none** of the seventeen post-convention merges, so the case has never arisen here; so the exclusion would be maintained for a situation that has never arisen. If it ever does, adding an exclusion is a smaller change than removing one.

### Rejected: an ADR

`docs/adr/` records decisions with live consequences that constrain later changes — a duplication policy, a reviewer-tier rule, a topology invariant. The boundary this change draws (*a repo-specific mechanical check goes in CI, never in a shipped plugin's `SKILL.md`*) is real, but it has exactly one consumer today and its reasoning is already stated in shipped text, in `52c3883`'s design. Recording a pattern with one instance is how an ADR becomes a changelog. If a second repo-specific check ever needs a home, that is when the pattern is worth an ADR.

### Rejected: a `CONTEXT.md` glossary entry

`CONTEXT.md` defines shapes this repo reasons about, not one row per new word. This change coins no concept: *version*, *base ref* and *published* are ordinary git and packaging vocabulary, used here in their ordinary senses. The nearest existing entries — **Mirror pair**, **Hand-mirrored pair** — are untouched and unaffected.

## The residual: the base can advance after the last run

Stated plainly, because it is the one thing this design does not close.

The workflow runs on a `pull_request` event — `opened`, `synchronize` (a push to the head branch), `reopened`. If the base advances *after* the last such event and the PR is merged with no further push, the recorded green result was computed against an older base. That reproduces the original failure shape.

Three things bound it, and one would close it:

- **It is narrower than the incident it fixes.** In the actual case, the collision existed at the branch's own next push: `main` published `2.7.0` at 14:46, the branch wrote `2.7.0` at 15:05, and the check fires there (*The proposed check, run against the incident*). The uncovered window is only "base advanced, and nobody pushed again."
- **A dev-flow run narrows it further.** Stage 4 pushes review fixes and the marker certifies a SHA; merging on a base that moved past a stale green check requires a run in which nothing was pushed after the base moved.
- **What would close it is a repo setting, not a file.** A branch ruleset requiring the `check-version-bump` check *and* "Require branches to be up to date before merging" (or a merge queue) converts push-time evaluation into merge-time evaluation. Rulesets are configured through the API or UI; they are not expressible in the repository, so they are outside what this design can commit. Measured above: no protection and no rulesets exist today, so **no** check is required today — this one is exactly as binding as `check-sync` already is, which is the honest comparison. Strengthening that is one settings change covering both checks at once, and it is a different decision from where the check lives.

## The edit

Three plain (untagged) fenced blocks, shape `[155, 18, 1]`. **Blocks 0 and 1 are whole new files, given in full; block 2 is a whole-line replacement.** Block 0's content was written to a scratch path outside the repo and run to produce every recorded output in this document — it is not a sketch. Every other fenced block in this document carries an info string (`sh`, `text`), so `read_blocks` cannot see it.

### Block 0 — the complete new `scripts/check-version-bump.py`

```
#!/usr/bin/env python3
"""Every plugin a change touches carries a version ahead of the base ref's.

    python3 scripts/check-version-bump.py <base-ref> [<head-ref>]

<head-ref> defaults to HEAD. A plugin is *touched* when the change contributes
at least one path under plugins/<name>/ -- computed from the merge base, so a
branch that has already merged the base in is judged on what it adds, not on
what its last commit happened to touch. That is the case this check exists for:
two branches derive the same next version from the same base, the second merges
the first's release in without a conflict (both made the identical change), and
its diff against its own last commit shows no plugin.json row at all.

The comparison is against the base ref's *tip*, never the merge base: the
question is whether this number was already published, and only the tip knows
that. Versions compare as tuples of integers -- "2.10.0" is ahead of "2.9.0",
which a string comparison gets backwards, and both plugins in this marketplace
have passed a two-digit minor.

A plugin absent at the base (newly added) or absent at the head (removed) is
skipped: neither can reuse a published version.

Exit 0 iff every touched plugin passed, 1 otherwise. Python 3 stdlib only.

Design: docs/superpowers/specs/2026-08-03-gh-48-version-collision-design.md
"""

import json
import subprocess
import sys

MANIFEST = "plugins/%s/.claude-plugin/plugin.json"

FIX = """\
Bump past the base ref's version, not past your branch's. A concurrent change
may have published your next number already, and the merge has nothing to flag
-- both sides made the identical change, so there is no conflict to resolve."""


def git(*args):
    """Run git with args as argv elements -- never a shell string, so an empty
    ref is a loud "bad revision" rather than a different valid command."""
    result = subprocess.run(("git",) + args, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit("check-version-bump: FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), result.returncode,
                            result.stderr.strip() or "(no message)"))
    return result.stdout


def resolve(ref, label):
    sha = git("rev-parse", "--verify", ref + "^{commit}").strip()
    if not sha:
        raise SystemExit("check-version-bump: %s ref %r resolved to nothing" % (label, ref))
    return sha


def version_at(rev, name):
    """The plugin's declared version at rev, or None if it has no manifest there."""
    path = MANIFEST % name
    result = subprocess.run(("git", "show", "%s:%s" % (rev, path)),
                            capture_output=True, text=True)
    if result.returncode != 0:
        return None
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit("check-version-bump: cannot parse %s at %s: %s" % (path, rev, exc))
    version = data.get("version") if isinstance(data, dict) else None
    if not isinstance(version, str):
        raise SystemExit('check-version-bump: %s at %s has no "version" string' % (path, rev))
    return version


def key(version, rev, name):
    """The version as an orderable tuple. The shape is pinned rather than padded:
    tuples of unequal length do not order the way anyone means them to -- (1, 0)
    sorts below (1, 0, 0) though nothing moved -- and X.Y.Z is the only shape
    CLAUDE.md's bump rule describes. Nothing else in the repo enforces it."""
    parts = version.split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        raise SystemExit("check-version-bump: %s at %s has version %r, which is not "
                         "three dotted-numeric segments (X.Y.Z); this check cannot "
                         "order it" % (MANIFEST % name, rev, version))
    return tuple(int(part) for part in parts)


def touched(base_sha, head_sha):
    """(merge base, the plugin directories this change contributes a path under)."""
    merge_base = git("merge-base", base_sha, head_sha).strip()
    if not merge_base:
        raise SystemExit("check-version-bump: git merge-base printed nothing")
    names = set()
    # -z and --no-renames pin this diff's output, so neither a path's own bytes
    # nor a git config can shrink the set: without -z a newline or non-ASCII
    # path arrives C-quoted as '"plugins/...' and stops matching, and rename
    # detection reports a file moved *out* of plugins/<name>/ only at its
    # destination. Either one is a silent pass on a touched plugin.
    for path in git("diff", "--name-only", "-z", "--no-renames",
                    merge_base, head_sha).split("\0"):
        parts = path.split("/")
        if len(parts) > 2 and parts[0] == "plugins":
            names.add(parts[1])
    return merge_base, sorted(names)


def main():
    if not 2 <= len(sys.argv) <= 3:
        raise SystemExit("usage: python3 scripts/check-version-bump.py <base-ref> [<head-ref>]")
    base_sha = resolve(sys.argv[1], "base")
    head_sha = resolve(sys.argv[2] if len(sys.argv) == 3 else "HEAD", "head")
    merge_base, names = touched(base_sha, head_sha)
    print("check-version-bump: base %s, head %s, merge-base %s"
          % (base_sha[:9], head_sha[:9], merge_base[:9]))
    if not names:
        print("check-version-bump: no plugin directory touched ... OK")
        return 0

    problems, compared = [], 0
    for name in names:
        head_version = version_at(head_sha, name)
        base_version = version_at(base_sha, name)
        if head_version is None:
            print("  %-20s removed at head ... skipped" % name)
            continue
        if base_version is None:
            print("  %-20s new at head (%s) ... skipped" % (name, head_version))
            continue
        compared += 1
        ahead = key(head_version, head_sha, name) > key(base_version, base_sha, name)
        print("  %-20s %s -> %s ... %s"
              % (name, base_version, head_version, "OK" if ahead else "FAIL"))
        if not ahead:
            problems.append(
                '%s: version "%s" is not ahead of the base ref\'s "%s", and this change\n'
                "touches plugins/%s/. The install cache is keyed on the version string, so\n"
                "the new text would never be picked up on re-sync.\n\n"
                "  %s" % (name, head_version, base_version, name, MANIFEST % name))

    if not problems:
        print("check-version-bump: %d compared, %d skipped ... OK"
              % (compared, len(names) - compared))
        return 0
    for block in problems:
        print()
        print(block)
    print()
    print(FIX)
    print("check-version-bump: %d of %d compared plugin directories failed"
          % (len(problems), compared))
    return 1


if __name__ == "__main__":
    sys.exit(main())
```

Five choices in that file are deliberate and are the ones a reviewer should push on:

- **`<head-ref>` is an optional second argument.** It is what makes the check falsifiable: without it, the only way to exercise a red run is to break the tree. With it, *Success criteria* 3 and 5 point the shipped script at `84d8cc9` and at every commit merged since the bump rule was written, and assert the verdicts, which is the only evidence available that the check catches the bug it was written for. A default of `HEAD` keeps the CI invocation one argument, and the workflow pins its checkout to the PR's head sha so that `HEAD` there is a branch tip — the same kind of head criteria 3 and 5 name explicitly (*Block 1*).
- **Every `git` call goes through `subprocess` with refs as `argv` elements**, never a shell string — *Command discipline*'s rule for computed refs. An empty or unresolvable ref is a loud `git rev-parse` failure, never a different valid command; a failed producer raises `SystemExit` naming the command, its exit status and git's message. Both refs are also resolved exactly once, through `rev-parse --verify <ref>^{commit}`, and every later command takes the resulting 40-character SHA — so no argument can be read as a pathspec or a tree where a revision was meant. `^{commit}` is what carries that: `git rev-parse --verify HEAD:plugins` succeeds and yields a tree, `HEAD:plugins^{commit}` fails, and *Success criteria* 4 asserts the failure rather than leaving the property to be rediscovered.
- **The diff that computes the touched set is pinned: `-z` and `--no-renames`.** Both close a *silent* false negative — a genuinely touched plugin dropping out of the set, which is the one failure this check exists to prevent. Without `-z`, `git diff --name-only` C-quotes any path holding a newline or a non-ASCII byte, so `"plugins/foo/skills/café.md"` splits to a first component of `'"plugins'` and stops matching; `-c core.quotePath=false` fixes only the non-ASCII half and leaves the newline, measured. With rename detection on, a file moved *out* of `plugins/<name>/` is reported only at its destination, so the plugin that lost it never counts as touched — and rename detection is a `diff.renames` config setting, so without `--no-renames` the verdict depends on the runner's git config rather than on the change. *Success criteria* 10 asserts all three cases and is red against a copy of this file with either flag removed.
- **`version_at` returning `None` is a *defined answer*, not a swallowed failure.** It fires only for a manifest that is absent at that revision, which is exactly the new-plugin and removed-plugin cases; the surrounding state is already validated (the ref resolved, the directory was touched), so a negative probe is unambiguous. A manifest that exists but has no `version` string, or a version that is not three dotted-numeric segments, halts instead of being guessed at.
- **`compared` is reported separately from `len(names)`**, so an all-skipped run prints `0 compared, 1 skipped ... OK` rather than claiming it verified something.

### Block 1 — the complete new `.github/workflows/check-version-bump.yml`

```
name: check-version-bump
on: pull_request
permissions:
  contents: read
jobs:
  check-version-bump:
    runs-on: ubuntu-latest
    env:
      BASE: ${{ github.event.pull_request.base.ref }}
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}
          fetch-depth: 0
      - name: Fetch the base branch
        run: git fetch --no-tags origin "+refs/heads/$BASE:refs/remotes/origin/$BASE"
      - name: Every touched plugin is ahead of the base
        run: python3 scripts/check-version-bump.py "origin/$BASE"
```

Each line that is not boilerplate answers a question:

- **`on: pull_request`, with no `push`.** The check is meaningless on `main` and must not be a job-level `if:` (*Rejected: a second job inside `check-sync.yml`*).
- **`ref: ${{ github.event.pull_request.head.sha }}`.** Without it `actions/checkout` takes `github.sha`, which on a `pull_request` event is *"the last merge commit of the pull request merge branch"* — `refs/pull/<n>/merge`, a merge of the branch into a base snapshot GitHub recomputes in the background, not the branch's own tip. That is a different head from the one the predicate names, and the difference is measurable: against the merge commit, a branch whose only contribution under `plugins/<name>/` is a bump `main` has already published reports `no plugin directory touched ... OK`, where the branch tip reports `FAIL`; and a branch that edits a plugin without bumping is reported `2.7.0 -> 2.7.0`, a number its own `plugin.json` does not contain. The pin makes CI, the one-argument local run `CLAUDE.md` line 7 names, and the heads criteria 3 and 5 exercise the same revision. It also drops a dependency on a ref that exists only while the PR merges cleanly — the re-target this check asks for leaves `plugin.json` changed differently on the two sides, which conflicts, which is exactly when that ref goes stale or missing. `${{ }}` here is an action input, not a splice into a `run:` string, so the reservation two bullets below does not reach it.
- **`fetch-depth: 0`.** `git merge-base` needs the history the two refs share; the default shallow checkout does not have it, and this is the one place a shallow clone would make the script halt. The cost is the whole repository: `git rev-list --count 52c3883` printed `33` and `du -sh .git` printed `10M`.
- **The explicit refspec on the fetch**, rather than a bare `git fetch origin "$BASE"`. This is the pattern dev-flow's own Docs policy already ships and states the reason for: *"in a single-branch clone a bare fetch updates only `FETCH_HEAD` and leaves `origin/<baseRef>` unresolvable."* It also means the design makes no claim about which remote-tracking refs `actions/checkout` happens to create — after this step `origin/$BASE` exists and is current, whatever the checkout did.
- **`BASE` passed as an environment variable, quoted at use**, rather than interpolated into the `run:` string. `${{ }}` interpolation splices a value into the shell before it runs; `"$BASE"` is one argument whatever it contains. Cheap here, correct everywhere.
- **`permissions: contents: read`**, matching `check-sync.yml`. The check needs no token beyond the checkout.

### Block 2 — the complete new `CLAUDE.md` line 7

Replaces line 7 in full. Everything through `Major only when a plugin is split (\`dev-flow\` 1.x → 2.0.0).` is byte-identical to the base; two sentences are appended and nothing is removed, so the file's line count does not change.

```
- **Bump `version` in `plugins/<name>/.claude-plugin/plugin.json` on any behavior change.** The install cache is version-keyed (`~/.claude/plugins/cache/taylor-plugins/<plugin>/<version>/`), so an edit at an unchanged version is never picked up on re-sync. **Always the minor segment** — `1.4.0 → 1.5.0`. Nothing reads the segment (the cache keys the whole string), and for prose that a model reads, there is no stable editorial-versus-behavioural line for a patch to mark. Major only when a plugin is split (`dev-flow` 1.x → 2.0.0). **Bump past `origin/main`, not past your branch's base** — a concurrent branch may have published your next number already, and the merge has nothing to flag, because both sides made the identical change. `python3 scripts/check-version-bump.py origin/main` is that check; it runs on every PR and asks for a bump from every plugin whose directory the change touches at all.
```

The sentence exists because the rule as written is ambiguous under concurrency — *bump the minor segment* does not say **of what**, and "of my branch's base" is the reading that produced the incident. Naming the script is the other half: a contributor who sees the check fail needs to know it is runnable locally, and the resolution (*re-target past the merged bump*, not *bump again from your base*) is carried by the script's own failure message, where it is read at the moment it is needed.

Two things about that line look like defects and are neither. **It restates block 0's `FIX` message.** The rationale — *a concurrent change may have published your next number, and the merge has nothing to flag* — is stated in `CLAUDE.md` and again in `FIX`, and it has to be: `CLAUDE.md` is read at authoring time by someone who has no CI output in front of them, and `FIX` is read from a failed run by someone who may never have read `CLAUDE.md` — a fork contributor, or anyone reading the Actions log. Neither copy can reach the other's reader, so a pointer in place of the second copy would land where it cannot be followed. They are not a *hand-mirrored pair* in `CONTEXT.md`'s sense: nothing requires the two wordings to match, only that both stay true, and both are true of one predicate implemented in one place — if that predicate ever changes, the script is what changes, and `CLAUDE.md` is where this repo's conventions live. **And it names `origin/main` where the workflow takes `github.event.pull_request.base.ref`** — whatever branch the PR targets. Also deliberate: `CLAUDE.md`'s own *Workflow* section already states that changes land via PR against `main`, so `origin/main` is the concrete, copy-pasteable command for every contributor here, and a generic phrasing would trade that for a case this repo does not have. The mechanism stays general; the instruction is specific on purpose.

## Assumptions

- **A1. Targets as of `52c3883`.** `CLAUDE.md` line 7 is the version-bump bullet; `scripts/check-version-bump.py` and `.github/workflows/check-version-bump.yml` do not exist. The implementation matches on **text, not line number**: *Success criteria* 2 reconstructs `CLAUDE.md` from its merge-base blob, so a base that moved fails loudly instead of editing the wrong line.
- **A2. A plugin is *touched* by any path under `plugins/<name>/`, deliberately wider than "behavior change".** A script cannot read intent, and the replay measured zero post-convention changes that would have been asked for an unnecessary bump. A README-only edit would be asked for one; the cost is zero (*Rejected: excluding `plugins/<name>/README.md`*).
- **A3. Every merge to `main` is a squash**, which is what makes the historical replay an exact simulation. Measured: of `main`'s 33 commits at `52c3883`, 32 have exactly one parent and the remaining one is the root. `allow_squash_merge` is true and dev-flow's Stage 5 runs `gh pr merge <pr> --squash`. If a merge commit ever lands on `main`, the replay loop skips it and the check itself is unaffected — it never reads `main`'s shape.
- **A4. `GITHUB_TOKEN`'s default `contents: read` is enough**, and the check needs no API call. A PR from a fork gets a read-only token and a normal checkout, which is all this workflow uses.
- **A5. This change touches no plugin directory, so no version is bumped and its own new check passes vacuously.** That is a conclusion, not a deferral — and it means the check cannot be validated by this PR's own green run, which is why *Success criteria* 3 and 5 exercise it against history instead.
- **A6. `claude plugin validate .` emitting exactly 8 `No author information provided` warnings and exiting 0 is the expected pass state**, per `CLAUDE.md`. This change adds no plugin, so the count is unchanged.
- **A7. Text assertions use `git grep` or `python3`, not bare `grep`** — under Claude Code's Bash tool bare `grep` is a ugrep-backed shell function whose output layout is not reliable for per-file assertions.
- **A8. This design's own plain fenced blocks are 0, 1 and 2, shape `[155, 18, 1]`.** A review that adds or removes a **line** in any of them changes the shape and trips *Success criteria* 0, which halts. No criterion below depends on a block's *character* content except through assertions that read the block from this document on disk, so a review that rewrites block 2's appended sentence or a comment in block 0 leaves every criterion runnable as written.
- **A9. `origin/main` is fetchable at implementation time.** *Success criteria* 1, 2, 5 and 6 resolve a ref from it and fail loudly — naming the command, its exit status and git's message — rather than comparing against a stale ref. Criteria 1, 2 and 5 each carry the same `git` wrapper for that; criterion 6 inherits it from the shipped script.
- **A10. The design and plan are committed on this branch** (`docs: commit`), so *Success criteria* 1's file-scope equality excludes `docs/superpowers/` with a pathspec.
- **A11. The `pull_request` payload supplies both refs the job uses, and neither is inferred.** `github.event.pull_request.head.sha` is the PR's tip and the checkout pins it, so `HEAD` in CI is what the predicate and the one-argument local run mean by *head*, rather than `github.sha`'s merge commit (*Block 1*). `github.event.pull_request.base.ref` is a non-empty branch name that exists on `origin`; GitHub populates it on every `pull_request` event, and it is trusted at runtime rather than guarded, because a job-level guard's failure mode is a skipped job that reports green (*Rejected: a second job inside `check-sync.yml`*). Both consumers fail loudly if it were ever empty, probed directly: the fetch step exits 128 on `fatal: invalid refspec '+refs/heads/:refs/remotes/origin/'`, and the script halts at exit 1 with `check-version-bump: FAILED: git rev-parse --verify origin/^{commit} -- exit 128, fatal: Needed a single revision`. This is the workflow-runtime counterpart of A9, which records the same trust for the local, success-criteria-time run.
- **A12. The filesystem accepts a newline and a non-ASCII byte in a filename**, which macOS and `ubuntu-latest` both do. *Success criteria* 10 writes both into a temporary repository; on a filesystem that refuses them the step fails loudly at the write rather than passing vacuously.

## Out of scope

Hard-excluded. A proposal touching any of these is a blocker, not a design.

- **`plugins/`, `.claude-plugin/`, and every `plugin.json`** — no plugin text changes and no version moves (A5). The merge-gate option is rejected on the merits, not deferred (*Rejected: a check inside dev-flow's merge gate*), so this is a conclusion.
- **`scripts/check-sync.py`** — untouched. No `MIRROR_PAIRS` entry, no `description` change, no third check inside it (*Rejected: inside `scripts/check-sync.py`*). Its output is asserted unchanged as a regression guard.
- **`scripts/design_blocks.py`** — used by *Success criteria* 0 and 2, not modified.
- **`.github/workflows/check-sync.yml`** — byte-identical after this change. The new workflow is a separate file (*Rejected: a second job*).
- **`.claude-plugin/marketplace.json`** — untouched, because no `description` changes and no plugin is added.
- **`CONTEXT.md`** and **`docs/adr/`** — no entry and no ADR is warranted, each for a stated reason.
- **Branch protection, rulesets, and merge queues** — a repo-settings change, not expressible in the repository (*The residual*). Recommending one is not the same as making it, and this design makes none.
- **The minor-always convention (#33)** — untouched. The issue already rules that this defect is not an argument against it.
- **Comparing plugin *content* between head and base** — explicitly not attempted (*The decision*).

## Success criteria

Every command runs from the repo root, after the edit unless stated. The base is `git merge-base origin/main HEAD` — computed, never hardcoded, so it stays correct if `main` advances or the branch is rebased; it resolves to `52c3883` today.

**Every step that consumes the computed base — 1 and 2 — passes it to `git` as an `argv` element from `python3`, never through a shell.** There is no `$(git …)` substitution anywhere below; the `52c3883`-pinned greps elsewhere in this document take a **literal** SHA, which is not a computed ref. Steps 3–6 name literal SHAs and a literal ref for the same reason.

Each step collects every mismatch and prints them all before exiting; no assertion sits behind an earlier short-circuit, and no step's output is human-read in place of an assertion.

**0. Block shape — asserted, not reported.** `design_blocks.py`'s CLI is a shape *reporter* that always exits 0; the *guard* is `read_blocks`, where the shape is a required argument and a mismatch is a `SystemExit`.

```sh
python3 - <<'PY'
import sys
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
DESIGN = "docs/superpowers/specs/2026-08-03-gh-48-version-collision-design.md"
for i, b in enumerate(read_blocks(DESIGN, [155, 18, 1])):
    print("  [%d] len=%d: %s" % (i, len(b), b[0][:66]))
print("shape guard: OK")
PY
echo "exit=$?"
```

Expect block 0 previewing `#!/usr/bin/env python3`, block 1 previewing `name: check-version-bump`, block 2 previewing the version-bump bullet, then `shape guard: OK` and `exit=0`. Anything else means this design was edited after the plan captured its shape — **stop and report**.

**1. File scope — exactly three files, and they are the three named.** The `--name-only` set is compared for equality against the authorized list, so a stray edit to `plugins/`, a `plugin.json`, `check-sync.yml`, `check-sync.py`, `CONTEXT.md`, `docs/adr/` or `marketplace.json` fails the step **and names the offending path**. **This equality is also the `Always:` rule's removed-phrase grep:** block 2 appends to line 7 and removes nothing, so there is no phrase to grep for — the assertion that replaces it is step 2's, which requires the base line to be a *prefix* of the new one, making removal detectable rather than merely unsearched-for.

```sh
python3 - <<'PY'
import subprocess, sys
SCOPE = ["--", ".", ":!docs/superpowers/"]
WANT = [".github/workflows/check-version-bump.yml", "CLAUDE.md",
        "scripts/check-version-bump.py"]
def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout
base = git("merge-base", "origin/main", "HEAD").strip()
print("base:", base)
changed = sorted(p for p in git("diff", "--name-only", base, *SCOPE).split("\n") if p)
if changed != sorted(WANT):
    print("file scope: FAIL -- changed %s, want %s" % (changed, sorted(WANT)))
    sys.exit(1)
print("file scope: OK")
PY
echo "exit=$?"
```

Expect a `base:` line carrying a 40-character SHA, then `file scope: OK` and `exit=0`.

**2. Design conformance — both new files are their blocks byte for byte, and `CLAUDE.md` is its merge-base blob with exactly line 7 replaced.** One program, nothing retyped on either side: the blocks are read **from this design on disk** through the shared reader, and `CLAUDE.md`'s expected content is reconstructed **from the base blob**.

```sh
python3 - <<'PY'
import subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-03-gh-48-version-collision-design.md"
SCRIPT = "scripts/check-version-bump.py"
WORKFLOW = ".github/workflows/check-version-bump.yml"
TARGET = "CLAUDE.md"
BULLET_I = 7                        # 1-based, at the base
WANT_LEN = 34                       # unchanged: block 2 appends, it does not add a line

def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout
def split(text):
    out = text.split("\n")
    if out and out[-1] == "":
        out.pop()
    return out

base = git("merge-base", "origin/main", "HEAD").strip()
blocks = read_blocks(DESIGN, [155, 18, 1])
script, workflow, bullet = blocks[0], blocks[1], blocks[2][0]
bad = []

for path, block in ((SCRIPT, script), (WORKFLOW, workflow)):
    if subprocess.run(("git", "cat-file", "-e", "%s:%s" % (base, path)),
                      capture_output=True).returncode == 0:
        bad.append("%s already existed at the base; this change creates it" % path)
    if not Path(path).is_file():
        bad.append("%s does not exist on disk; this change creates it from its design block"
                   % path)
        continue
    on_disk = split(Path(path).read_text(encoding="utf-8"))
    if on_disk != block:
        bad.append("%s is not its design block verbatim (%d lines on disk, %d in the block)"
                   % (path, len(on_disk), len(block)))

old = split(git("show", base + ":" + TARGET))
new = split(Path(TARGET).read_text(encoding="utf-8"))
expected = old[:BULLET_I - 1] + [bullet] + old[BULLET_I:]
if new != expected:
    bad.append("%s is not its base blob with line %d replaced by block 2"
               % (TARGET, BULLET_I))
if len(new) != WANT_LEN:
    bad.append("%s is %d lines, want %d" % (TARGET, len(new), WANT_LEN))
if new.count(bullet) != 1:
    bad.append("%s holds block 2 %d times, want exactly 1" % (TARGET, new.count(bullet)))
if not bullet.startswith(old[BULLET_I - 1]):
    bad.append("block 2 does not start with the base line %d; the edit must append, "
               "never rewrite" % BULLET_I)
if SCRIPT not in bullet:
    bad.append("block 2 does not name %s; the appended sentence must point at the check"
               % SCRIPT)

for why in bad:
    print("MISMATCH:", why)
print("conformance:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expect exactly `conformance: OK` and `exit=0`. Run at `52c3883` with no edit applied it printed four `MISMATCH:` lines — `scripts/check-version-bump.py` and `.github/workflows/check-version-bump.yml` each not existing on disk, `CLAUDE.md is not its base blob with line 7 replaced by block 2`, and `CLAUDE.md holds block 2 0 times, want exactly 1` — then `conformance: FAIL` and `exit=1`. That is the red form, and the `is_file` guard is what makes it one: without it the first `read_text` raises `FileNotFoundError` and the step reports nothing at all, which is the state a half-applied edit leaves it in.

**3. The check rejects the incident.** The criterion the whole change exists for, and the only one that exercises a red path of the shipped script.

```sh
python3 - <<'PY'
import subprocess, sys
CASES = [
    # (base, head, want_exit, why)
    ("963a66c", "84d8cc9", 1, "the merge that reused main's published 2.7.0/1.9.0"),
    ("963a66c", "5f99cf2", 1, "the same branch before it merged main in"),
    ("963a66c", "02ffb7b", 0, "the fix that re-targeted to 2.8.0/1.10.0"),
    ("c28a613^", "c28a613", 0, "a plugin added for the first time -- skipped, not failed"),
]
bad = []
for base, head, want, why in CASES:
    r = subprocess.run(["python3", "scripts/check-version-bump.py", base, head],
                       capture_output=True, text=True)
    print("%s..%s exit=%d want=%d  (%s)" % (base, head, r.returncode, want, why))
    if r.returncode != want:
        bad.append("%s..%s exited %d, want %d\n%s" % (base, head, r.returncode, want,
                                                      r.stdout + r.stderr))
    if want == 1:
        for name in ("dev-flow", "dev-flow-worktree"):
            if ("  %-20s" % name) + " " not in r.stdout:
                bad.append("%s..%s does not name %s in its report" % (base, head, name))
for why in bad:
    print("MISMATCH:", why)
print("incident:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expect four rows with `exit` equal to `want`, then `incident: OK` and `exit=0`. Run against the prototype while this document was written, the four cases printed exit `1`, `1`, `0`, `0` in that order.

**4. Failed producers halt, and the usage line is real.**

```sh
python3 - <<'PY'
import subprocess, sys
CASES = [([], "usage:"), (["no-such-ref"], "FAILED: git rev-parse"),
         ([""], "FAILED: git rev-parse"),
         (["HEAD:plugins"], "FAILED: git rev-parse"),
         (["origin/main", "HEAD", "extra"], "usage:")]
bad = []
for args, needle in CASES:
    r = subprocess.run(["python3", "scripts/check-version-bump.py"] + args,
                       capture_output=True, text=True)
    out = r.stdout + r.stderr
    print("argv=%r exit=%d first-line=%r" % (args, r.returncode, out.strip().split("\n")[0][:72]))
    if r.returncode == 0:
        bad.append("argv=%r exited 0; a failed producer must halt" % (args,))
    if needle not in out:
        bad.append("argv=%r did not report %r" % (args, needle))
for why in bad:
    print("MISMATCH:", why)
print("producers:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expect five non-zero exits, then `producers: OK` and `exit=0`. The `HEAD:plugins` row is the one that fails if `resolve` ever stops appending `^{commit}`: `git rev-parse --verify HEAD:plugins` succeeds and yields a tree.

**5. The check rejects nothing merged since the bump rule was written.** The false-positive bound, replayed against the shipped script rather than the prototype.

```sh
python3 - <<'PY'
import subprocess, sys
def git(*a):
    r = subprocess.run(("git",) + a, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(a), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout
rejected, n = [], 0
for line in git("log", "--first-parent", "--format=%H %s", "1f359e2^..origin/main").strip().split("\n"):
    sha, subj = line.split(" ", 1)
    parents = git("rev-parse", sha + "^@").split()
    if len(parents) != 1:
        continue
    n += 1
    if subprocess.run(["python3", "scripts/check-version-bump.py", parents[0], sha],
                      capture_output=True, text=True).returncode:
        rejected.append((sha[:7], subj[:52]))
print("commits replayed:", n)
print("rejected:", len(rejected))
for row in rejected:
    print("   %s  %s" % row)
sys.exit(1 if rejected else 0)
PY
echo "exit=$?"
```

Expect `commits replayed:` at least 17 (it grows as `main` advances), `rejected: 0`, and `exit=0`. Run against the prototype at `52c3883` it printed `17` and `0`.

**6. The check passes this change's own PR, vacuously and visibly.**

```sh
python3 scripts/check-version-bump.py origin/main
echo "exit=$?"
```

Expect a `base … head … merge-base` line, then `check-version-bump: no plugin directory touched ... OK` and `exit=0`. The word *vacuously* is the point (A5), which is why criteria 3 and 5 exist.

**7. The workflow is valid, wired up, and green on this PR.** No YAML parser is available (`python3 -c 'import yaml'` fails on this machine), so the assertion that the file is well-formed is GitHub's: a workflow that does not parse never appears in the PR's checks. That case — *no checks reported* — is one `gh pr checks` signals by exiting **1**, the same code it uses for a check that failed, which is why this step takes its verdict from the JSON and never from the exit code; this repo's own pipeline `SKILL.md` states the conflation (*"distinguish failure from no-checks by output text, not exit code (both exit 1; pending exits 8)"*). Run after Stage 4 has opened the PR.

```sh
python3 - <<'PY'
import json, subprocess, sys
BRANCH = "tayl0r/gh-48-version-collision"
WANT = "check-version-bump"
def sh(*a, ok=(0,)):
    r = subprocess.run(a, capture_output=True, text=True)
    if r.returncode not in ok:
        raise SystemExit("FAILED: %s -- exit %d, %s" % (" ".join(a), r.returncode,
                                                        r.stderr.strip() or "(no message)"))
    if r.returncode != 0:              # tolerated, but never silently
        print("note: %s exited %d -- %s" % (" ".join(a), r.returncode,
                                            r.stderr.strip() or "(no message)"))
    return r.stdout
prs = json.loads(sh("gh", "pr", "list", "--head", BRANCH, "--state", "all", "--json", "number"))
if not prs:
    raise SystemExit("FAILED: no PR for %s" % BRANCH)
pr = str(max(p["number"] for p in prs))
# gh pr checks exits 1 for a failing check *and* for no checks at all, and 8 while
# they are pending -- the three outcomes this step exists to report, not crash on.
# The JSON is the verdict, never the exit code; on the no-checks path stdout is empty.
checks = json.loads(sh("gh", "pr", "checks", pr, "--json", "name,state",
                       ok=(0, 1, 8)).strip() or "[]")
print("checks on PR #%s: %s" % (pr, sorted(c["name"] for c in checks)))
bad = []
rows = [c for c in checks if c["name"] == WANT]
if not rows:
    bad.append("%r is not among the PR's checks; the workflow did not parse or did not run"
               % WANT)
for c in rows:
    if c["state"] != "SUCCESS":
        bad.append("%s is %s, want SUCCESS" % (c["name"], c["state"]))
if not [c for c in checks if c["name"] == "check-sync"]:
    bad.append("check-sync is missing; the new workflow must not disturb the existing one")
for why in bad:
    print("MISMATCH:", why)
print("pr checks:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expect a checks list containing both `check-sync` and `check-version-bump`, then `pr checks: OK` and `exit=0`.

**8. `python3 scripts/check-sync.py` — passes, with output identical to before the change.** It reads none of the changed files; this is a regression guard, not a claim about the edit.

```sh
python3 scripts/check-sync.py
echo "exit=$?"
```

Run against this tree at `52c3883` it printed:

```text
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)
check-sync: all checks passed
exit=0
```

**9. `claude plugin validate .` — exit 0 *and* exactly 8 author warnings.** Both halves are asserted, because either alone passes vacuously: the command exits 0 while emitting warnings (A6), and a count assertion alone would pass on a run that errored out.

```sh
python3 - <<'PY'
import shutil, subprocess, sys
WANT_WARNINGS = 8
NEEDLE = "No author information provided"
if shutil.which("claude") is None:
    raise SystemExit("FAILED: claude is not on PATH; this step cannot run")
r = subprocess.run(["claude", "plugin", "validate", "."], capture_output=True, text=True)
n = (r.stdout + r.stderr).count(NEEDLE)
print("claude plugin validate: exit %d, %d author warnings" % (r.returncode, n))
bad = []
if r.returncode != 0:
    bad.append("claude plugin validate . exited %d, want 0" % r.returncode)
if n != WANT_WARNINGS:
    bad.append("%d %r warnings, want exactly %d" % (n, NEEDLE, WANT_WARNINGS))
for why in bad:
    print("MISMATCH:", why)
print("validate:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Run against this tree at `52c3883` it printed `claude plugin validate: exit 0, 8 author warnings`, `validate: OK`, `exit=0`.

**10. The check sees a touched plugin whose path git would otherwise hide.** The falsifier for `-z` and `--no-renames`: without either flag every row below exits 0 and reports `no plugin directory touched`, which is the silent pass this whole change exists to prevent. Run from the repo root; the probe repository is built in a temporary directory and removed.

```sh
python3 - <<'PY'
import os, pathlib, shutil, subprocess, sys, tempfile
SCRIPT = os.path.abspath("scripts/check-version-bump.py")
tmp = tempfile.mkdtemp(prefix="check-version-bump-")
root = pathlib.Path(tmp)
def git(*a):
    return subprocess.run(("git", "-C", tmp) + a, capture_output=True, text=True,
                          check=True).stdout
git("init", "-q")
git("config", "user.email", "t@example.invalid")
git("config", "user.name", "t")
(root / "plugins/foo/skills").mkdir(parents=True)
(root / "plugins/foo/.claude-plugin").mkdir(parents=True)
(root / "plugins/foo/.claude-plugin/plugin.json").write_text('{"name": "foo", "version": "1.0.0"}\n')
(root / "plugins/foo/skills/a.md").write_text("x\n" * 40)
git("add", "-A"), git("commit", "-qm", "base")
base = git("rev-parse", "HEAD").strip()
CASES = [
    ("a newline in the path", lambda: (root / "plugins/foo/skills/we\nird.md").write_text("y\n")),
    ("a non-ASCII path", lambda: (root / "plugins/foo/skills/café.md").write_text("y\n")),
    ("a file moved out of the plugin", lambda: git("mv", "plugins/foo/skills/a.md", "moved.md")),
]
bad = []
for why, make in CASES:
    git("checkout", "-q", "-B", "probe", base), git("clean", "-qfd")
    make()
    git("add", "-A"), git("commit", "-qm", why)
    head = git("rev-parse", "HEAD").strip()
    r = subprocess.run(["python3", SCRIPT, base, head], capture_output=True, text=True, cwd=tmp)
    print("%-32s exit=%d" % (why, r.returncode))
    if r.returncode != 1 or "foo" not in r.stdout:
        bad.append("%s: exit %d, want 1 naming foo\n%s" % (why, r.returncode, r.stdout + r.stderr))
shutil.rmtree(tmp)
for w in bad:
    print("MISMATCH:", w)
print("hidden paths:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expect three rows at `exit=1`, then `hidden paths: OK` and `exit=0`. Run against block 0 without the two flags it printed three rows at `exit=0` and `hidden paths: FAIL`, which is the red form.

**11. CI evaluated the PR's own tip, not a merge commit.** Criterion 7 proves the workflow ran and was green — and would prove exactly that with the checkout unpinned, because it reads only check names and states. This reads the run's log and asserts the head the script printed is the PR's head sha (A11, *Block 1*). Run after criterion 7.

```sh
python3 - <<'PY'
import json, subprocess, sys
BRANCH = "tayl0r/gh-48-version-collision"
WORKFLOW = "check-version-bump.yml"
def sh(*a):
    r = subprocess.run(a, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: %s -- exit %d, %s"
                         % (" ".join(a), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout
head = json.loads(sh("gh", "pr", "view", BRANCH, "--json", "headRefOid"))["headRefOid"]
runs = json.loads(sh("gh", "run", "list", "--workflow", WORKFLOW, "--branch", BRANCH,
                     "--status", "completed", "--limit", "1",
                     "--json", "databaseId,conclusion"))
if not runs:
    raise SystemExit("FAILED: no completed %s run on %s" % (WORKFLOW, BRANCH))
run = runs[0]
log = sh("gh", "run", "view", str(run["databaseId"]), "--log")
needle = "head %s," % head[:9]
print("PR head %s, run %s concluded %s" % (head[:9], run["databaseId"], run["conclusion"]))
bad = []
if run["conclusion"] != "success":
    bad.append("run %s concluded %s, want success" % (run["databaseId"], run["conclusion"]))
if needle not in log:
    bad.append("the log does not report %r; CI resolved some other head -- the checkout "
               "is not pinned to the PR's head sha" % needle)
if "no plugin directory touched ... OK" not in log:
    bad.append("the log does not carry the script's own verdict line")
for why in bad:
    print("MISMATCH:", why)
print("ci head:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expect a `PR head … run … concluded success` line, then `ci head: OK` and `exit=0`.

## Files the plan will touch

- **Create:** `scripts/check-version-bump.py` — block 0 verbatim, 155 lines.
- **Create:** `.github/workflows/check-version-bump.yml` — block 1 verbatim, 18 lines.
- **Modify:** `CLAUDE.md` — line 7 replaced by block 2 (verbatim, whole-line replacement). Nothing else in the file; the line count is unchanged at 34.
- **Committed by dev-flow per `docs: commit`:** this design and its plan under `docs/superpowers/`.

Nothing else. No plugin file, no `plugin.json`, no `.claude-plugin/marketplace.json`, no `scripts/check-sync.py`, no `scripts/design_blocks.py`, no `.github/workflows/check-sync.yml`, no `CONTEXT.md`, no `docs/adr/`.

## PR

```text
Close #48 by checking, on every pull request, that each plugin the change
touches carries a version strictly ahead of the base branch's tip.

A version bump was derived from the branch's base, not from what main had
already published. Verified in-tree: main published dev-flow 2.7.0 and
dev-flow-worktree 1.9.0 at 9a5cab2 (14:46 on 2026-08-02); branch
tayl0r/gh-28-29-review-prose wrote the same two numbers at 5f99cf2 (15:05),
after that. When it merged main in at 84d8cc9 there was no conflict -- both
sides had made the identical change -- and the merge's diff against its first
parent carries two SKILL.md rows and no plugin.json row at all. The install
cache is keyed on the version string, so that change would have shipped
invisible. 02ffb7b re-targeted it once someone noticed.

New scripts/check-version-bump.py, run by a new
.github/workflows/check-version-bump.yml on pull_request. For every plugin
directory the change contributes a path under -- computed from the merge base,
so the touched set survives a merge-in that leaves no plugin.json row -- the
version at the head must be strictly greater than the version at the base
ref's *tip*, compared as a tuple of integers. Against the merge base, branch
B's 2.6.0 -> 2.7.0 is a perfectly good bump; only the tip knows 2.7.0 was
taken. Tuples rather than strings because "1.10.0" < "1.9.0" as strings and
this marketplace already ships 1.12.0 and 2.10.0.

Pointed at 84d8cc9 with 963a66c as the base, the script exits 1 and names both
plugins. Pointed at 5f99cf2 -- the same branch *before* the merge-in -- it also
exits 1, so the check fires at the push, not only at the merge. Pointed at
02ffb7b it exits 0. Replayed over every squash on main (each one's parent is
main's tip at the moment it merged, so the replay is exact) it rejects three
commits, all of them from before 1f359e2 wrote the bump rule down, and zero of
the seventeen merged since.

CI rather than dev-flow's merge gate, which the issue named as the other
candidate. dev-flow ships into arbitrary repos where
plugins/*/.claude-plugin/plugin.json does not exist, so a marketplace-shaped
rule has no home in its SKILL.md -- the same ground #39 used to keep this
repo's instruments out of plugins/. It would also bind fewer paths than CI, not
more: a hand-typed gh pr merge never passes through it. And it buys nothing,
because the merge gate already halts on any failing check ("**Any check
fails** -> halt and report", one occurrence in each pipeline SKILL.md), so a
red CI check is a dev-flow halt with no dev-flow edit and no version bump.

A separate workflow file rather than a second job in check-sync.yml:
check-sync.yml also runs on push to main, where the version legitimately equals
origin/main's, so sharing the file means an `if:` guard whose failure mode is a
silently skipped job on a green PR.

CLAUDE.md line 7 gains two sentences and no new line. "Always the minor
segment" never said *of what*, and "of my branch's base" is the reading that
produced this bug.

Three files, two of them new. No plugin file is touched and no version is
bumped -- which also means this PR's own new check passes vacuously, so the
evidence that it works is the replay against history, not this green run.

Closes #48
```

## Spec self-review

- **Placeholders / TBDs:** none. Both new files are given in full as plain fenced blocks; the `CLAUDE.md` change is given as a complete replacement line; every criterion is runnable as written.

- **Every measurement this document states, and the command that printed it.** *Measurements are derived, not typed* requires the whole list, not a selection, so this is the whole list.

  **Of the tree at `52c3883`, each with its command given beside the claim and run while this document was written:**

  | Measurement | Command |
  |---|---|
  | the six commit SHAs, dates and subjects in the timeline; `9a5cab2` at 14:46 precedes `5f99cf2` at 15:05 | the six `git log -1 --format='%h %ad %s' --date=iso` calls under *The incident, verified in-tree* |
  | both branches changed `2.6.0 → 2.7.0` and `1.8.0 → 1.9.0` | the two `git show … \| grep -E '^[+-].*version'` calls in the same section |
  | `84d8cc9` has two parents, two `plugins/` rows in its first-parent diff and none for `plugin.json`; its `dev-flow` version is `2.7.0` | `git show 84d8cc9 --format='parents=%P' --stat -- plugins/` and `git show 84d8cc9:plugins/dev-flow/.claude-plugin/plugin.json` |
  | six `1.0.0`s, one `1.12.0`, one `2.10.0` | `git grep -h -F '"version"' 52c3883 -- 'plugins/*/.claude-plugin/plugin.json' \| sort \| uniq -c` |
  | 32 single-parent commits on `main`; 3 rejected, named; 17 at or after `1f359e2`, 0 rejected | the replay program under *What the check would have done*, run twice with the two ranges |
  | the bump rule was written at `1f359e2` | `git log --oneline -S'Bump \`version\` in' 52c3883 -- CLAUDE.md` |
  | one workflow file, and its exact contents | `git ls-tree -r --name-only 52c3883 -- .github/` and `git show 52c3883:.github/workflows/check-sync.yml` |
  | nothing named `check-version` exists — no output, exit 1 | `git grep -c -F 'check-version' 52c3883` |
  | the merge gate's halt-on-failing-check line, one occurrence in each pipeline `SKILL.md` | `git grep -c -F '**Any check fails** -> halt and report.' 52c3883 -- plugins/` |
  | no branch protection (404), no rulesets (`[]`), `allow_update_branch: false` | the three `gh api` calls under *Nothing is required today* |
  | `main` is 33 commits; `.git` is 10M | `git rev-list --count 52c3883` (printed `33`) and `du -sh .git` (printed `10M`) |
  | `CLAUDE.md` is 34 lines | `git grep -c '' 52c3883 -- CLAUDE.md` (printed `52c3883:CLAUDE.md:34`) |
  | `python3 scripts/check-sync.py` and `claude plugin validate .` baselines | criteria 8 and 9, run against this tree |
  | no PyYAML on this machine | `python3 -c 'import yaml'` (raised `ModuleNotFoundError`), which is why criterion 7 asserts the workflow through `gh pr checks` instead |

  **Of this change's own replacement text:** the `[155, 18, 1]` shape, asserted by criterion 0; the 155- and 18-line file lengths, asserted by criterion 2 through block equality; the post-edit `CLAUDE.md` length of 34 lines, asserted by criterion 2. **No word count of this change's own replacement text is stated anywhere** (A8), so there is nothing here a review rewriting a block's prose can leave stale.

  **Recorded command output:** every `text` block in *What is true today* was produced by the `sh` block immediately above it, run from the repo root against this tree, and transcribed exactly as printed.

  The three check-run transcripts in *The proposed check, run against the incident* — `84d8cc9`, `5f99cf2`, `02ffb7b` — came from running **block 0's content**, written to a scratch path outside the repo, with the base and head SHAs shown. The same scratch copy produced criteria 3, 4 and 5's stated results: criterion 3's four rows printed exits `1, 1, 0, 0` matching their `want` values with `incident: OK`; criterion 4's five rows printed five non-zero exits with `producers: OK`; criterion 5 printed `commits replayed: 17` and `rejected: 0`. That the scratch file is what block 0 says it is was then asserted rather than assumed — `read_blocks` was pointed at this document and its block 0 compared line-for-line against the scratch file, and they are equal at 155 lines. The two hunks review added to `touched` and `key` were then re-run against all four of criterion 3's cases and the full historical replay: stdout, stderr and exit status byte-identical, and the same three pre-convention rejections. The scratch file is not part of the change; the implementation must create `scripts/check-version-bump.py` from block 0, which criterion 2 asserts byte for byte.

  The merge-commit numbers in *Block 1*'s `ref:` bullet came from the same scratch copy of block 0, run in a throwaway repository outside this one that reproduces the incident shape — `main` and a branch each bump `plugins/P` from `2.6.0` to `2.7.0` and edit different hunks of one `SKILL.md`, and a merge of the branch into `main`'s tip, base as first parent, stands in for what an unpinned checkout resolves. The incident itself is rejected either way: branch tip and merge commit both print `2.7.0 -> 2.7.0 ... FAIL` and exit 1, because `git merge-base` against the merge commit lands on the base tip and the diff is the branch's net contribution. The two divergences are the ones the bullet states, and the re-target the failure asks for — `2.8.0` while `main` publishes `2.7.0` — printed `CONFLICT (content): Merge conflict in plugins/P/.claude-plugin/plugin.json`, which is why the pin drops the dependency on that ref rather than documenting it.

  Criteria 0, 8 and 9's green runs were produced against this tree. **Criterion 2's green run cannot be produced at design time**, because producing it means applying the edit. What was produced instead is the same program with the three files' post-edit content **computed** — the two new files as their blocks, `CLAUDE.md` as its base blob with line 7 replaced by block 2 — rather than read from disk: every assertion green, `conformance: OK`, and the resulting `CLAUDE.md` 34 lines. Criterion 2's **red** run was produced directly, by running the step verbatim against this tree with no edit applied: the four `MISMATCH:` lines quoted under the step, `conformance: FAIL`, `exit=1`. Criterion 7 cannot run until Stage 4 has opened the PR; its `gh pr checks` handling was exercised against two existing pull requests instead — one carrying only `check-sync`, one carrying no checks at all — and reported both, rather than halting, in each.

  Two corrections are worth recording. A first draft of the historical replay reported the three rejections without dating them; adding the `1f359e2` probe showed all three predate the convention and turned an apparent false-positive rate into a zero. A first draft of *The edit* stated the shape as `[145, 15, 1]`; running `python3 scripts/design_blocks.py` on this document corrected block 1's length to 17. Review then pinned block 1's checkout to the PR's head sha, taking the workflow to 18 lines, and added six lines to block 0's `touched` and four to its `key`, taking the script to 155; the number recorded in *The edit*, A8, criteria 0 and 2, and *Files the plan will touch* is the one `design_blocks.py` printed afterwards: `[155, 18, 1]`.

- **Internal consistency:** the shape `[155, 18, 1]` appears in *The edit*, in A8, and in criteria 0 and 2, and the two file lengths it implies appear in *Files the plan will touch*. `CLAUDE.md` stays 34 lines in *Block 2*, in *Files the plan will touch*, and in criterion 2's `WANT_LEN`. The three-file scope in criterion 1's `WANT` matches *Files the plan will touch* and the complement in *Out of scope*. The predicate stated in *The decision* is the one block 0 implements: merge-base touched set over a pinned diff, tip comparison, integer-tuple ordering over `X.Y.Z`, skip-on-absent.

- **Scope:** three files. Criterion 1 checks it by file; criterion 2 checks each of the three against its block or its base blob. `plugins/`, `check-sync.py`, `design_blocks.py`, `check-sync.yml`, `marketplace.json`, `CONTEXT.md`, `docs/adr/`, repo settings and the #33 convention are each named in *Out of scope* with a reason, and each is a conclusion rather than a deferral.

- **Ambiguity:** two places a fresh implementer could go wrong, both closed. The first is that block 0 must be created at `scripts/check-version-bump.py` and not confused with the scratch copy the outputs came from — criterion 2 asserts the on-disk file equals the block and that neither new path existed at the base. The second is the direction of the `CLAUDE.md` edit: block 2 **appends**, so criterion 2 asserts the base line 7 is a prefix of it, which is also what stands in for the removed-phrase grep (nothing is removed).

- **Scope creep checked:** the temptation here is to also close *The residual* by proposing a branch ruleset, or to strengthen dev-flow's merge gate to refuse a behind-base merge. Both are named, one is rejected on the merits and the other is out of scope as a settings change; neither is in the edit.

- **Positions taken:** the check lives in CI, as its own script and its own workflow file; it counts a plugin as touched on any path under its directory and compares against the base ref's tip as integer tuples; the diff that computes the touched set is pinned with `-z` and `--no-renames`, and a version that is not `X.Y.Z` halts rather than being ordered; the workflow pins its checkout to the PR's head sha; new and removed plugins are skipped; `README.md` is not excluded; no ADR, no `CONTEXT.md` entry, no dev-flow change, no version bump, no repo-settings change. The staleness residual is recorded rather than closed, with the one mechanism that would close it named. Nothing is left for the implementer to decide.
