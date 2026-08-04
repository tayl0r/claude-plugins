---
dev-flow:
  slug: gh-66-verify-after-commit
  stops: [pre-merge]
  docs: commit
---

# gh-66 — a committed-HEAD-relative verification step runs after the commit, not in the pre-commit sweep

Close **#66** by adding one **Verification ordering** bullet to dev-flow's Cross-Cutting Concerns: a verification step that reads committed HEAD (`git show HEAD:…`) must run **after** the task's commit, never before it, because before the commit HEAD still carries the pre-edit state and the check reports a spurious FAIL. The bullet names only plain git — no repo-local instrument — so it is a pipeline-general property and belongs in the plugin's `SKILL.md`, mirrored in `dev-flow-worktree`.

Four files change: the same new bullet is inserted, **byte-identically**, directly after the Command discipline bullet in `plugins/dev-flow/skills/dev-flow/SKILL.md` and `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` (a hand-mirrored pair, absent from `check-sync.py`'s `MIRROR_PAIRS`), and both plugins bump a minor version because their behaviour text changed — `dev-flow` 2.14.0 → 2.15.0 and `dev-flow-worktree` 1.16.0 → 1.17.0. `marketplace.json` carries `description`, not `version`, and no description changes, so it is untouched. `CLAUDE.md` is untouched, on the merits (*The decision*, *Rejected: CLAUDE.md*).

## Scope check — one subsystem, one change

One subsystem: dev-flow's verification guidance, the pipeline-general layer that gh-39 (`2026-08-02-gh-39-verification-rules-home-design.md`) placed in the plugin `SKILL.md`'s Cross-Cutting Concerns. #66 asks exactly one question — *does the ordering rule get written down, and where?* — and the answer is one new bullet inserted into one existing list, mirrored into the sibling plugin, plus the version bump that any plugin-text change carries in this repo. There is no ordering dependency between the four file edits and nothing decomposes further: the two `SKILL.md` edits are the same bytes, the two `plugin.json` edits are the mechanical consequence, and none can land without the others being a partial change. This is not two subsystems wearing one hat — the version bumps are not an independent change, they are this repo's cost of editing plugin prose at all (`CLAUDE.md`, *Changing a plugin*).

## What is true today, measured at `origin/main`

Every measurement here is of the tree **before** this change, pinned to `origin/main`, given with the command that printed it, run while this document was written. `origin/main` resolved to `bd7b2be6d455839928fdff3f011f085a231a6c54`, and this branch's `git merge-base origin/main HEAD` is that same commit — the branch sits at the base with no commits yet. No number appears that its command's output does not show.

### The two plugins' current versions

```sh
git show origin/main:plugins/dev-flow/.claude-plugin/plugin.json
git show origin/main:plugins/dev-flow-worktree/.claude-plugin/plugin.json
```

```text
{
  "name": "dev-flow",
  "version": "2.14.0",
  "description": "Autonomous design -> plan -> execute -> PR -> merge pipeline (works on a feature branch in your checkout) with adversarial review at each artifact boundary"
}
{
  "name": "dev-flow-worktree",
  "version": "1.16.0",
  "description": "Autonomous design -> plan -> execute -> PR -> merge pipeline, isolated in a dedicated git worktree, with adversarial review at each artifact boundary"
}
```

`dev-flow` is at 2.14.0, `dev-flow-worktree` at 1.16.0. The bump targets are 2.15.0 and 1.17.0 — the next minor past `origin/main`, per `CLAUDE.md`'s bump rule.

### The Command discipline bullet: where it sits, and that it is byte-identical across the pair

```sh
git grep -n -F '- **Command discipline:**' origin/main -- plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
```

```text
origin/main:plugins/dev-flow/skills/dev-flow/SKILL.md:277:- **Command discipline:** resolve git-internal paths through git (`git rev-parse --git-path …`), never as `.git/...` literals ...
origin/main:plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md:271:- **Command discipline:** resolve git-internal paths through git (`git rev-parse --git-path …`), never as `.git/...` literals ...
```

The bullet is line 277 in `dev-flow` and line 271 in `dev-flow-worktree`; the bullet-opener `- **Command discipline:**` occurs exactly once in each file (every other `Command discipline` mention is an inline reference, not a bold-label bullet). The two whole bullets are **byte-identical** — this is the fact that lets one identical bullet insert after the same anchor line in both files:

```sh
diff <(git show origin/main:plugins/dev-flow/skills/dev-flow/SKILL.md | sed -n '277p') <(git show origin/main:plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md | sed -n '271p') && echo IDENTICAL
```

```text
IDENTICAL
```

The Command discipline bullet already declares a verification-criteria reach — it governs not just the pipeline's own commands but the success criteria a design or plan emits — which is the reach the new bullet's own scope clause mirrors rather than borrows:

```sh
git show origin/main:plugins/dev-flow/skills/dev-flow/SKILL.md | sed -n '277p' | grep -o 'This governs the success criteria a design or plan emits as well as the pipeline'"'"'s own commands'
```

```text
This governs the success criteria a design or plan emits as well as the pipeline's own commands
```

### Line counts, and that `git show HEAD` appears nowhere in either file

```sh
git grep -c '' origin/main -- plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
git grep -c -F 'git show HEAD' origin/main -- plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md; echo "exit=$?"
```

```text
origin/main:plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md:273
origin/main:plugins/dev-flow/skills/dev-flow/SKILL.md:279
exit=1
```

`dev-flow`'s file was 279 lines, `dev-flow-worktree`'s 273. The second command printed nothing and exited 1: the string `git show HEAD` occurs in **neither** file today, so the added content is genuinely new, not a duplicate of existing text. This edit inserts one bullet line, so each count grows by exactly one — 279 → 280 and 273 → 274 — which *Verification* step 2 asserts rather than trusting it.

### The pipeline `SKILL.md` pair is not machine-checked

```sh
git grep -n -F 'skills/dev-flow/SKILL.md' origin/main -- scripts/check-sync.py; echo "exit=$?"
```

```text
exit=1
```

Nothing. `check-sync.py`'s `MIRROR_PAIRS` enrols only the `adversarial-review/SKILL.md` pair and the two agent pairs (`git grep -n '"name":' origin/main -- scripts/check-sync.py` names its three `"name":` entries — `adversarial-review`, `adversarial-review-seed agent`, `adversarial-review-resolver agent`). `CLAUDE.md` says the pipeline `SKILL.md` pair is *"too divergent to check mechanically — mirror those by hand."* So the identical bullet must be inserted into **both** files by hand, and *Verification* step 2 reconstructs **both** from their `origin/main` blobs — the check outside the pair that `CLAUDE.md`'s *Verifying a change* requires precisely because `check-sync.py` cannot see this pair.

### The check that motivated the issue reads committed HEAD, not the working tree

`scripts/check-version-bump.py` — the check `CLAUDE.md` names for the version-bump rule, run on every PR — reads each plugin's version through `git show <head>:<manifest>` with `<head>` defaulting to `HEAD`, and compares it as a tuple against the base ref's:

```sh
git show origin/main:scripts/check-version-bump.py | sed -n '58,72p;107,133p'
```

```text
def version_at(rev, name):
    """The plugin's declared version at rev, or None if it has no manifest there."""
    path = MANIFEST % name
    result = subprocess.run(("git", "show", "%s:%s" % (rev, path)),
                            capture_output=True, text=True)
    ...
    head_sha = resolve(sys.argv[2] if len(sys.argv) == 3 else "HEAD", "head")
    ...
        ahead = key(head_version, head_sha, name) > key(base_version, base_sha, name)
```

`version_at` reads the **committed** blob at a revision; `head` is `HEAD` unless overridden; `ahead` is strict `>`; and the comparison runs only after `touched()` finds the plugin directory in `git diff merge-base..HEAD`. So when a prior commit has already contributed a path under `plugins/<name>/` but not yet the version bump — gh-45's shape (PR #64) — `touched()` sees the directory, the comparison runs, `head_version == base_version`, `>` is false, and the check prints FAIL: exactly the spurious FAIL the rule generalizes. (This change lands as a single commit, so pre-commit its own `merge-base..HEAD` is empty, `touched()` finds nothing, and the script passes *vacuously* rather than FAILing — the ordering constraint still binds it, because the check is only meaningful once the bump is committed; *Verification*, step 6.)

## The decision

**Add one new sibling bullet — labelled *Verification ordering* — to the Cross-Cutting Concerns list in `plugins/dev-flow/skills/dev-flow/SKILL.md`, directly after the byte-identical Command discipline bullet, and the byte-identical bullet in `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`.** The bullet states the ordering rule. It names only plain git (`git show HEAD:…`) and the word *commit* — no plugin name, no repo-local instrument — so a single identical bullet goes into both files, inserted after the same text-anchored line (the Command discipline opener), and *Verification* proves them identical by reconstructing each from its own base blob against the same block.

This is the answer gh-39's framework produces when applied to #66's rule, and the issue already assumes it: *"Mirrored in dev-flow-worktree"* is an instruction that only makes sense for the `SKILL.md` home, because `CLAUDE.md` is a single un-mirrored file with nothing to mirror into.

### Why Cross-Cutting Concerns, and why a sibling bullet rather than extending Command discipline

gh-39 drew the line this design sits on: **repo-local instruments** — text naming `scripts/check-sync.py`, `design_blocks.py`, `read_blocks`, the merge-base-blob assertion — live in `CLAUDE.md`'s `## Verifying a change`, because they are specific to this one repo; **pipeline-general properties** — Command discipline's criteria-scope rule, *Measurements are derived, not typed* — live in the plugin `SKILL.md`'s Cross-Cutting Concerns, because they ship with the plugin into every repo dev-flow runs in.

#66's rule sits cleanly on the pipeline-general side. Its only concrete token is `git show HEAD:…`, plain git available in every repo; it names no repo-local instrument (never `check-version-bump.py` — that script is the *instance* that surfaced the bug, and the rule is written one level up from it). So it belongs in Cross-Cutting Concerns, mirrored into `dev-flow-worktree`.

Within that section it is a **new sibling bullet**, not an extension of Command discipline:

- **It is a distinct concern — *when* a step runs, not *how* a command is built.** Command discipline is about command *construction*: resolve git-internal paths through git, capture-validate-quote, run computed refs through `subprocess` — every hazard it names is *wrong input → wrong command → wrong verdict*. #66 is a correctly-built command that returns a wrong verdict because of *when* it runs relative to the commit. The two share a family (*wrong verdict from unpinned state*), but a reader who opens the bullet labelled **Command discipline** for construction guidance does not expect a scheduling rule at its end, and Command discipline is already the longest, densest bullet in the file.
- **The section already gives verification-integrity properties their own bullets.** *Measurements are derived, not typed* is a sibling of Command discipline, not nested inside it, though it is the same wrong-output-from-unpinned-state family (a typed measurement goes stale). #66's ordering rule is another verification-integrity property at that exact granularity, so the placement consistent with the section's own structure is a sibling beside *Measurements are derived*, not a clause buried in Command discipline.
- **A sibling inherits the section's scope; it duplicates nothing.** None of the section's other bullets — Context hygiene, Review provenance, Failure handling, Idempotent resume, *Measurements are derived* — restate Command discipline's *"success criteria a design or plan emits"* scope to stand alone; each inherits its reach from the section and its own subject. The new bullet does the same, and states the one reach it needs in a single clause of its own, exactly as *Measurements are derived* states its own subject. The kinship to Command discipline is carried by one back-reference (*"the temporal case of Command discipline's wrong-verdict hazard"*), not by copying its scope sentence.
- **It leaves Command discipline byte-for-byte untouched.** *Rejected: re-flowing the Command discipline bullet* notes that bullet is the one line in this repo where a stray identical edit to both copies cannot be caught by reading the diff. A sibling adds a new line and changes that bullet not at all, so *Verification* step 2 asserts `new[i] == old[i]` for the Command discipline line and the mirror-hotspot bullet is never re-touched.

## Rejected alternatives

### Rejected: CLAUDE.md

The tempting home, because `check-version-bump.py` is *documented* in `CLAUDE.md` (line 7, the version-bump bullet) and the bug bit that exact script. Refused, on gh-39's framework and two independent grounds:

- **The rule is pipeline-general, not a repo-local instrument.** gh-39's `CLAUDE.md` section is for text that names this repo's instruments. #66's rule names none — only `git show HEAD:…`. Filing a pipeline-general property in `CLAUDE.md` would leave every *other* repo dev-flow runs in without it, which is the precise mistake gh-39's split exists to prevent, viewed from the other direction.
- **`CLAUDE.md` is not mirrored, and the issue says "Mirrored in dev-flow-worktree".** `CLAUDE.md` is one file; there is nothing to mirror. The issue's own disposition assumes a home that has a `dev-flow-worktree` twin — which is the `SKILL.md` pair, not `CLAUDE.md`.

**Does `check-version-bump.py`'s existing `CLAUDE.md` documentation need any touch?** No — out of scope, with a reason. `CLAUDE.md` line 7 documents *what* the check does and *that* it runs on every PR; it says nothing about where a verification step sits relative to a task's commit inside a dev-flow plan, and it should not. That ordering guidance is pipeline-general and now lives in the `SKILL.md` bullet; repeating it in `CLAUDE.md` would duplicate a general property into a repo-local file and re-introduce exactly the two-homes contradiction gh-39 spent a whole design removing. The version-bump bullet stays byte-for-byte as it is.

### Rejected: a Stage 2 (Plan) or Stage 3 (Execute) guidance edit rather than Cross-Cutting Concerns

The gh-45 failure happened in a **plan's** Task 3 pre-commit sweep, so localizing the rule to Stage 2 (Plan) guidance looks apt. Rejected: the hazard is genuinely cross-stage. A committed-HEAD-relative check can appear in a **design's** Verification section (Stage 1), in a **plan's** per-task sweep (Stage 2), or among the **pipeline's own** commands. gh-39 put pipeline-general properties in Cross-Cutting Concerns precisely so they bind every stage at once rather than being restated per stage, and Command discipline already declares that cross-stage reach (*"the success criteria a design or plan emits as well as the pipeline's own commands"*). A Stage 2-only note would under-cover — silent on the design's own Verification section — and would fragment a property that Command discipline already holds whole. Cross-Cutting Concerns is the correct altitude; Stage guidance is the wrong one.

### Rejected: extending the Command discipline bullet

The design's first instinct, because the ordering rule is kin to Command discipline's wrong-verdict family and that bullet already claims a *"success criteria a design or plan emits"* reach the rule can borrow. Refused on the four grounds in *Why … a sibling bullet rather than extending Command discipline*: the rule is a distinct *when*-not-*how* concern; the section already sibling-lists a verification-integrity property (*Measurements are derived*) of the same family rather than nesting it; a sibling inherits the section's scope so nothing is duplicated (the appeal to "a sibling would restate the scope" is false — no other sibling restates it); and a sibling leaves Command discipline, the repo's one un-diff-checkable mirror line, byte-for-byte untouched. The only thing extension would save is one list item, and the section is a list of exactly such distinct properties.

### Rejected: re-flowing the Command discipline bullet to sit the rule beside its kin

Tempting to move the new rule *into* Command discipline beside the computed-ref clause it is kin to. Refused, and the sibling placement makes the refusal machine-checkable: this change adds a new line and touches Command discipline **not at all**, so *Verification* step 2 asserts the Command discipline line is byte-for-byte its base blob (`new[i] == old[i]`) while a new bullet is inserted after it. Any re-flow of Command discipline would destroy that assertion and put a reviewer's eye over a 400-word line — the one line-shape in this repo where a stray identical edit to both copies cannot be caught by reading the diff.

### Rejected: an ADR

`docs/adr/` records architecture decisions with live consequences — a duplication policy, a tier pin, a topology invariant. *Where one verification rule is written down* has no consequence beyond the bullet it is written in. Same disposition gh-39 reached for the same reason.

## The edit

**One plain (untagged) fenced block, shape `[1]`** — a single line, the new bullet. It is inserted as a new line **directly after** the Command discipline bullet in **both** `SKILL.md` files. Because the block names no plugin, the same bytes go into both; because the two Command discipline bullets are byte-identical at the base (*What is true today*), the anchor line is identical in both and the inserted bullet lands in the same structural place.

Every other fenced block in this document carries an info string (`sh`, `text`), so `read_blocks` sees only this one.

### Block 0 — the new Verification ordering bullet

**Anchor:** the Command discipline bullet, whose opener is `- **Command discipline:**` (line 277 in `dev-flow`, line 271 in `dev-flow-worktree` at `origin/main`). Block 0 is inserted as the **next line** after that bullet; it adds exactly one line and leaves the Command discipline bullet unchanged. *Verification* locates the anchor by the opener text, not the line number.

```
- **Verification ordering:** a verification step that reads committed HEAD (`git show HEAD:…`) must run **after** the task's commit, never before it. Before the commit, HEAD does not yet carry the edit, so the step reads the old committed state and reports a spurious FAIL even though the working-tree edit is correct; forcing that FAIL green by re-applying the edit double-applies it — a second version bump, say — and corrupts the committed value the step exists to check. Commit first, then run it. This is the temporal case of **Command discipline**'s wrong-verdict hazard — a correctly built command run at the wrong moment — and it governs the verification steps a design or plan emits as much as the pipeline's own commands.
```

After the edit the Cross-Cutting Concerns list reads: *"… Command discipline: … Capture-validate-quote stays the rule everywhere else."* then the new **Verification ordering** bullet, then *"Measurements are derived, not typed. …"* — the new rule sits between its two kin, Command discipline and Measurements are derived.

### The version bumps

Whole-value replacements in each manifest, no design block needed — the bumped values are asserted directly by *Verification* step 3:

- `plugins/dev-flow/.claude-plugin/plugin.json` — `"version": "2.14.0"` → `"version": "2.15.0"`.
- `plugins/dev-flow-worktree/.claude-plugin/plugin.json` — `"version": "1.16.0"` → `"version": "1.17.0"`.

Nothing else in either manifest changes; both `description` fields stay byte-for-byte.

## The ordering constraint on this change's own Verification

Step 3 and `check-version-bump.py` both read committed HEAD (*What is true today*), so this change's **own** verification obeys the rule it adds. The steps below split by what they read:

- **Pre- or post-commit, either works** — step 1 (file scope, `git diff` base vs working tree), step 2 (reconstruction, working tree vs base blob), step 4 (`check-sync.py`), step 5 (`claude plugin validate .`). These read the working tree or the base, not committed HEAD.
- **Post-commit only** — step 3 (both bumped versions and unchanged descriptions, read via `git show HEAD:…`) and step 6 (`python3 scripts/check-version-bump.py origin/main`). Both read committed `HEAD`, so both are meaningless before the version-bump commit — but they behave differently, and only one is a live demonstration of the rule here. **Step 3 is the demonstration:** run before the commit it reads the still-unbumped `HEAD`, its assertion that `HEAD` carries the bumped version fails, and that spurious FAIL would tempt the second bump that corrupts the version — exactly the hazard the rule names, on this change. **Step 6 does not reproduce it here:** this change lands as a single commit, so before that commit `git diff merge-base..HEAD` is empty, `touched()` finds no plugin directory, and the script short-circuits to `no plugin directory touched ... OK` (exit 0) — a *vacuous* pass that has checked no bump at all, not a FAIL. `check-version-bump.py` reproduces the spurious FAIL only in the multi-commit shape the rule generalizes from (gh-45, PR #64: a prior task's commit already touched the plugin directory while the bump was still missing). Either way both steps must run **after** the commit: step 3 to avoid the spurious FAIL, step 6 so the touched set is non-empty and the check is meaningful rather than vacuous.

## Verification

Every command runs from the repo root. The base is `git merge-base origin/main HEAD` — computed, never hardcoded — and resolves to `bd7b2be6d455839928fdff3f011f085a231a6c54` today. Per **Command discipline**, every step that consumes the computed base passes it to `git` as an `argv` element from `python3`, never through a shell `$( )`: `git merge-base` prints nothing and exits non-zero on an unresolvable or unrelated ref, so an unquoted substitution would silently degrade a base comparison into a working-tree-vs-index one. There is no `$(git …)` anywhere below; the `origin/main`-pinned greps elsewhere in this document take a symbolic ref git resolves itself, not a captured value.

This change **removes no text** — it is a pure insertion — so *Verifying a change*'s removed-phrase grep is vacuous by construction; the meaningful direction is that the added content was **not already present**, which step 2 asserts (the base blob carries the bullet zero times) and *What is true today* corroborates (`git show HEAD` occurs in neither file at the base).

**0. Block shape — asserted, not reported.** `design_blocks.py`'s CLI reports shape and always exits 0; the guard is `read_blocks`, where the shape is required and a mismatch is a `SystemExit`.

```sh
python3 - <<'PY'
import sys
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
DESIGN = "docs/superpowers/specs/2026-08-04-gh-66-verify-after-commit-design.md"
for i, b in enumerate(read_blocks(DESIGN, [1])):
    print("  [%d] len=%d: %s" % (i, len(b), b[0][:70]))
print("shape guard: OK")
PY
echo "exit=$?"
```

Expect the one block previewing the new bullet, then `shape guard: OK` and `exit=0`. Run against this document it printed:

```text
  [0] len=1: - **Verification ordering:** a verification step that reads committed 
shape guard: OK
exit=0
```

The red run was produced by copying this document to a scratch path outside the repo, splitting block 0's single line into two there, and pointing the same program at the copy: it printed nothing on stdout and this on stderr, at `exit=1`:

```text
design code-block shape is [2], want [1]; stop and re-read the design
```

**1. File scope — exactly the four intended files.** The `--name-only` set against the working tree, `docs/superpowers/` excluded (this design and its plan quote nothing that would otherwise widen the set, but the exclusion matches gh-39's discipline for the committed artifacts), is compared for equality against the authorized list, so any stray path — another plugin, `scripts/`, `CONTEXT.md`, `marketplace.json`, `CLAUDE.md` — fails the step and is named.

```sh
python3 - <<'PY'
import subprocess, sys
SCOPE = ["--", ".", ":!docs/superpowers/"]
WANT = sorted([
    "plugins/dev-flow/.claude-plugin/plugin.json",
    "plugins/dev-flow/skills/dev-flow/SKILL.md",
    "plugins/dev-flow-worktree/.claude-plugin/plugin.json",
    "plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md",
])
def git(*a):
    r = subprocess.run(("git",) + a, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(a), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout
base = git("merge-base", "origin/main", "HEAD").strip()
print("base:", base)
changed = sorted(p for p in git("diff", "--name-only", base, *SCOPE).split("\n") if p)
if changed != WANT:
    print("file scope: FAIL -- changed %s, want %s" % (changed, WANT))
    sys.exit(1)
print("file scope: OK")
PY
echo "exit=$?"
```

Expect a `base:` line with the 40-character SHA, then `file scope: OK` and `exit=0`. Run at the base with no edit applied it printed:

```text
base: bd7b2be6d455839928fdff3f011f085a231a6c54
file scope: FAIL -- changed [], want ['plugins/dev-flow-worktree/.claude-plugin/plugin.json', 'plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md', 'plugins/dev-flow/.claude-plugin/plugin.json', 'plugins/dev-flow/skills/dev-flow/SKILL.md']
```

**2. Reconstruction — each `SKILL.md` is its base blob with exactly the new bullet inserted after the Command discipline bullet, from the design on disk, and the two files stay identical.** One program over both targets, nothing retyped on either side: the new bullet is read from this design through the shared reader; each file's expected content is its `origin/main` blob with block 0 inserted directly after the located Command discipline line; and the file must equal it exactly. This is `CLAUDE.md`'s `Always:` byte-for-byte assertion run on the change, the block-conformance check, and the *"inserted, not rewritten"* proof in one. The insert adds exactly one line (`len(new) == len(old) + 1`), leaves the Command discipline line byte-for-byte (`new[i] == old[i]`), the bullet appears exactly once after the edit and zero times at the base, and the same `bullet` object reconstructs both files — so if the two edits diverged by a byte, one file's reconstruction fails.

```sh
python3 - <<'PY'
import subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-04-gh-66-verify-after-commit-design.md"
TARGETS = ["plugins/dev-flow/skills/dev-flow/SKILL.md",
           "plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md"]
OPENER = "- **Command discipline:**"

def git(*a):
    return subprocess.run(("git",) + a, capture_output=True, text=True, check=True).stdout
def split(t):
    o = t.split("\n")
    if o and o[-1] == "":
        o.pop()
    return o

base = git("merge-base", "origin/main", "HEAD").strip()
bullet = read_blocks(DESIGN, [1])[0][0]
bad = []
for path in TARGETS:
    old = split(git("show", base + ":" + path))
    new = split(Path(path).read_text(encoding="utf-8"))
    idx = [i for i, ln in enumerate(old) if ln.startswith(OPENER)]
    if len(idx) != 1:
        bad.append("%s: base has %d Command discipline openers, want exactly 1" % (path, len(idx)))
        continue
    i = idx[0]
    expected = old[:i + 1] + [bullet] + old[i + 1:]
    if new != expected:
        bad.append("%s is not its base blob with the Verification ordering bullet inserted after the Command discipline bullet" % path)
    if len(new) != len(old) + 1:
        bad.append("%s changed line count %d -> %d; the insert must add exactly one line" % (path, len(old), len(new)))
    if i >= len(new) or new[i] != old[i]:
        bad.append("%s changed the Command discipline bullet; the insert must leave it byte-for-byte" % path)
    if new.count(bullet) != 1:
        bad.append("%s holds the inserted bullet %d times after the edit, want exactly 1" % (path, new.count(bullet)))
    if any(bullet == ln for ln in old):
        bad.append("%s already carried the inserted bullet at the base" % path)
for why in bad:
    print("MISMATCH:", why)
print("reconstruction:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expect exactly `reconstruction: OK` and `exit=0`. Run at the base with no edit applied — `new == old` for both files — it printed **six** mismatches, three per file, and `exit=1`:

```text
MISMATCH: plugins/dev-flow/skills/dev-flow/SKILL.md is not its base blob with the Verification ordering bullet inserted after the Command discipline bullet
MISMATCH: plugins/dev-flow/skills/dev-flow/SKILL.md changed line count 279 -> 279; the insert must add exactly one line
MISMATCH: plugins/dev-flow/skills/dev-flow/SKILL.md holds the inserted bullet 0 times after the edit, want exactly 1
MISMATCH: plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md is not its base blob with the Verification ordering bullet inserted after the Command discipline bullet
MISMATCH: plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md changed line count 273 -> 273; the insert must add exactly one line
MISMATCH: plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md holds the inserted bullet 0 times after the edit, want exactly 1
reconstruction: FAIL
exit=1
```

Three of the five assertions per file fired: the reconstruction-equality one, the line-count one (an unedited file is 279/273 lines while the insert wants 280/274, so `len(new) != len(old) + 1`), and the once-count one (an unedited file holds the new bullet zero times, and `0 != 1`). The Command-discipline-unchanged assertion and the *already-carried-at-base* assertion did **not** fire — an unedited file's Command discipline line is its own blob's, and it holds the bullet zero times, so it did not carry it at the base. The three that fired are exactly what the insert satisfies. The green run cannot be produced before the edit exists; what was produced instead, while this document was written, is the same program with `new` computed as the intended post-edit content rather than read from disk — every assertion green, `reconstruction: OK`, the two files 280 and 274 lines. If the shape guard trips instead (`design code-block shape is …`), **stop and report**: this design was edited after the plan captured its shape.

**3. Both versions bumped, both descriptions unchanged, `marketplace.json` untouched — post-commit.** Reads committed `HEAD` (`git show HEAD:…`), so per this change's own rule it runs **after** the version-bump commit. Each half is asserted: a bump with a silently-edited description, or a `marketplace.json` drift, fails and is named.

```sh
python3 - <<'PY'
import json, subprocess, sys
WANT = {"dev-flow": ("2.14.0", "2.15.0"), "dev-flow-worktree": ("1.16.0", "1.17.0")}
MAN = "plugins/%s/.claude-plugin/plugin.json"
def git(*a):
    return subprocess.run(("git",) + a, capture_output=True, text=True, check=True).stdout
def field(rev, name, key):
    return json.loads(git("show", "%s:%s" % (rev, MAN % name)))[key]
base = git("merge-base", "origin/main", "HEAD").strip()
bad = []
for name, (b, h) in WANT.items():
    if field(base, name, "version") != b:
        bad.append("%s base version %s, want %s" % (name, field(base, name, "version"), b))
    if field("HEAD", name, "version") != h:
        bad.append("%s HEAD version %s, want %s" % (name, field("HEAD", name, "version"), h))
    if field("HEAD", name, "description") != field(base, name, "description"):
        bad.append("%s description changed" % name)
if git("show", base + ":.claude-plugin/marketplace.json") != git("show", "HEAD:.claude-plugin/marketplace.json"):
    bad.append(".claude-plugin/marketplace.json changed")
for why in bad:
    print("MISMATCH:", why)
print("versions:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expect `versions: OK` and `exit=0`. Run at the base with no commit — `HEAD` still carries 2.14.0 / 1.16.0 — it printed (this is the pre-commit spurious failure the issue is about, reproduced here on purpose):

```text
MISMATCH: dev-flow HEAD version 2.14.0, want 2.15.0
MISMATCH: dev-flow-worktree HEAD version 1.16.0, want 1.17.0
versions: FAIL
exit=1
```

**4. `python3 scripts/check-sync.py`** — passes, output identical to before the change. It reads none of the four edited files (the pipeline `SKILL.md` pair is not in `MIRROR_PAIRS`, and no `description` moved), so this is a regression guard.

```sh
python3 scripts/check-sync.py
echo "exit=$?"
```

Run against the base tree it printed (and the post-edit run must match it byte-for-byte):

```text
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)
check-sync: mirror pair "adversarial-review-seed agent" ... OK (19 lines, 0 declared exceptions)
check-sync: mirror pair "adversarial-review-resolver agent" ... OK (25 lines, 0 declared exceptions)
check-sync: all checks passed
exit=0
```

**5. `claude plugin validate .` — exit 0 and exactly 8 author warnings.** Both halves asserted, because either alone passes vacuously.

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
    bad.append("exit %d, want 0" % r.returncode)
if n != WANT_WARNINGS:
    bad.append("%d author warnings, want exactly %d" % (n, WANT_WARNINGS))
for why in bad:
    print("MISMATCH:", why)
print("validate:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Run against the base tree it printed:

```text
claude plugin validate: exit 0, 8 author warnings
validate: OK
exit=0
```

**6. `python3 scripts/check-version-bump.py origin/main` — passes, and MUST run after the version-bump commit.** The script reads `git show HEAD:<manifest>`, but only for plugins its `touched()` gate finds in `git diff merge-base..HEAD` (*What is true today*). Pre-commit this single-commit change has committed nothing, so that diff is empty, no plugin is "touched", and the script passes *vacuously* — `no plugin directory touched ... OK` — having checked no bump; only after the commit is the touched set non-empty and the version comparison meaningful. (The spurious-FAIL form of the hazard is gh-45's multi-commit shape, where a prior commit already touched the plugin directory while the bump was missing.) Pass `origin/main` as a symbolic ref git resolves itself — not a captured `$( )`.

```sh
python3 scripts/check-version-bump.py origin/main
echo "exit=$?"
```

After the commit, expect both plugins reported ahead and `exit=0`:

```text
check-version-bump: base <sha>, head <sha>, merge-base <sha>
  dev-flow             2.14.0 -> 2.15.0 ... OK
  dev-flow-worktree    1.16.0 -> 1.17.0 ... OK
check-version-bump: 2 compared, 0 skipped ... OK
exit=0
```

Run **before** the commit, this single-commit change has committed nothing, so `git diff merge-base..HEAD` is empty, `touched()` finds no plugin directory, and the script prints `check-version-bump: no plugin directory touched ... OK` at `exit=0` — a *vacuous* pass that has verified no bump. It reaches the `head_version == base_version → ... FAIL` path only when a prior commit has already touched the plugin directory while the bump is still missing — gh-45's multi-commit shape. Either way, run pre-commit it tells you nothing about the bump: commit first, then run it against a non-empty touched set. If a version check ever does FAIL, do **not** "fix" it by bumping a second time.

## Out of scope

Hard-excluded. A proposal touching any of these is a blocker, not a design.

- **`CLAUDE.md`** — untouched, on the merits (*Rejected: CLAUDE.md*). The rule is pipeline-general and `CLAUDE.md` is not mirrored; `check-version-bump.py`'s existing documentation there needs no edit, because it documents the check, not verification-sweep ordering inside a plan.
- **`scripts/`** — no change. `check-version-bump.py` and `design_blocks.py` are *used* by *Verification*, not modified; `check-sync.py`'s `MIRROR_PAIRS` is unchanged (this pair was never in it).
- **`.claude-plugin/marketplace.json`** — untouched; no `description` changes, and it carries no `version`. *Verification* step 3 asserts it is byte-identical to its base.
- **`CONTEXT.md`** — untouched, no edit implied. This change coins no repo concept; *wrong-verdict*, *temporal case*, *committed HEAD* are ordinary description, not shapes this repo reasons about, and the glossary defines shapes rather than one row per phrase.
- **`docs/adr/`** — no ADR warranted (*Rejected: an ADR*).
- **`.github/`** — no CI change.
- **The Command discipline bullet's existing text and the `Measurements are derived` bullet** — not re-flowed or re-worded (*Rejected: re-flowing the Command discipline bullet to sit the rule beside its kin*). The edit inserts one new bullet between them and leaves both byte-for-byte.
- **Every other plugin, and every other bullet in Cross-Cutting Concerns** — the change adds one new bullet after Command discipline in the two pipeline plugins and modifies no existing bullet.

## Assumptions

- **A1. `origin/main` is the base and is fetchable at implementation time.** Today `git merge-base origin/main HEAD` is `bd7b2be6d455839928fdff3f011f085a231a6c54`, equal to `origin/main`; the branch sits at the base with no commits. Every base-consuming step resolves it live and fails loudly — naming the command, its exit status and git's message — rather than comparing against a stale ref (A7).
- **A2. The implementation matches on text, not line number.** Line 277 (`dev-flow`) and 271 (`dev-flow-worktree`) are stated for orientation; *Verification* step 2 locates the bullet by the opener `- **Command discipline:**` and reconstructs the whole file from its blob, so a base that shifted the lines fails loudly instead of editing the wrong one.
- **A3. Editing plugin prose bumps the plugin's version, minor segment, past `origin/main`.** Both plugins' `SKILL.md` change, so both bump: 2.14.0 → 2.15.0 and 1.16.0 → 1.17.0 (`CLAUDE.md`, *Changing a plugin*). A conclusion, not a deferral; step 3 asserts both, and step 1's scope equality expects both manifests in the changed set.
- **A4. The new bullet names no plugin, so one identical block serves both files.** This is a deliberate design property, not a coincidence: the rule is about plain git and the commit boundary, neither of which differs between the two plugins. Step 2 reconstructs both files from the same `bullet` object, so a plugin-specific word slipping in would fail one file.
- **A5. The two Command discipline bullets are byte-identical at the base** (*What is true today*), which is what makes the identical bullet land in the same place in both files. If a concurrent change makes them diverge before this lands, step 2 fails on whichever file no longer matches its blob-plus-bullet, and the implementer reconciles before proceeding.
- **A6. No test framework exists in this repo.** *Verification* is the whole correctness surface (`CLAUDE.md` line 3).
- **A7. Text and reconstruction assertions run in `python3` against `git show`/`git diff`, not bare `grep`.** Under Claude Code's Bash tool bare `grep` is a ugrep-backed function whose layout is not reliable for per-file byte assertions; the `git grep` measurements above are for human-readable evidence, and every load-bearing equality is byte-exact in `python3`.
- **A8. `claude plugin validate .` emits exactly 8 `No author information provided` warnings and exits 0** — the expected pass state per `CLAUDE.md`.
- **A9. The design and plan are committed on this branch** (`docs: commit`), so step 1's scope equality excludes `docs/superpowers/` with a pathspec.
- **A10. This change's own post-commit Verification (steps 3 and 6) must run after the version-bump commit.** Not a caveat bolted on: step 3 is the rule this change writes down, exercised on itself — a `git show HEAD:` version assertion that spuriously FAILs pre-commit. Step 6 reads committed HEAD too, but for this single-commit change it passes *vacuously* pre-commit (empty touched set), so it too is only meaningful post-commit (*The ordering constraint on this change's own Verification*).
- **A11. This design's only plain fenced block is block 0, shape `[1]`.** No expectation below depends on the block's character content except through step 2, which derives the expected side from the base blob; a review that rewrites the bullet's prose leaves every check runnable as written, and a review that adds or removes a line in the block changes the shape and trips step 0.

## Files the plan will touch

- **Modify:** `plugins/dev-flow/skills/dev-flow/SKILL.md` — block 0 inserted as a new bullet directly after the Command discipline bullet; nothing else.
- **Modify:** `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` — the **same** block 0 inserted after the same bullet; nothing else. Hand-mirrored: `check-sync.py` does not cover this pair, so both edits are by hand and step 2 reconstructs both.
- **Modify:** `plugins/dev-flow/.claude-plugin/plugin.json` — `version` 2.14.0 → 2.15.0.
- **Modify:** `plugins/dev-flow-worktree/.claude-plugin/plugin.json` — `version` 1.16.0 → 1.17.0.
- **Committed by dev-flow per `docs: commit`:** this design and its plan under `docs/superpowers/`.

Nothing else. No `CLAUDE.md`, no `scripts/`, no `CONTEXT.md`, no `docs/adr/`, no `.github/`, no `marketplace.json`.

## PR

```text
Close #66 by writing down one ordering rule dev-flow's verification guidance
was missing: a verification step that reads committed HEAD (git show HEAD:...)
must run after the task's commit, never in the pre-commit sweep.

Surfaced by gh-45 (PR #64): a generated plan placed
`python3 scripts/check-version-bump.py origin/main` in Task 3's pre-commit
sweep, but that script reads each plugin's committed version via
git show HEAD:...plugin.json. Pre-commit, HEAD still carried the unbumped
versions, so the check compared against an equal committed HEAD and printed
FAIL -- contradicting the step's own "expect it to pass", and tempting the
over-bump "fix" that corrupts the version. Any future plan touching a plugin
regenerates a similar sweep and can re-place a committed-HEAD-relative check
before its commit.

The rule names only plain git and the commit boundary -- no repo-local
instrument -- so by gh-39's framework it is a pipeline-general property and
belongs in the plugin SKILL.md's Cross-Cutting Concerns, not in CLAUDE.md
(which is not mirrored; the issue says "Mirrored in dev-flow-worktree"). It
lands as a new sibling bullet -- Verification ordering -- directly after
Command discipline, not as a clause appended to it: the ordering hazard is a
distinct when-not-how concern, and the section already gives a kin
verification-integrity property (Measurements are derived, not typed) its own
bullet rather than nesting it in Command discipline. The new bullet
back-references Command discipline for the wrong-verdict kinship and leaves
that bullet -- the repo's one un-diff-checkable mirror line -- byte for byte
untouched. One identical bullet is inserted in both plugins; the pair is
hand-mirrored (absent from check-sync.py's MIRROR_PAIRS), so the verification
reconstructs both files from their origin/main blobs.

Both plugins bump a minor version because their behaviour text changed:
dev-flow 2.14.0 -> 2.15.0, dev-flow-worktree 1.16.0 -> 1.17.0. marketplace.json
carries description, not version, and no description changes, so it is
untouched.

This change eats its own dog food: its own version check reads committed HEAD
(git show HEAD:...plugin.json), so run before the bump commit it reads the
still-unbumped HEAD and FAILs against the bump it expects -- exactly the rule
being added, so that check runs after the commit. check-version-bump reads
committed HEAD too, but this PR lands as one commit, so pre-commit its touched
set is empty and it passes vacuously rather than FAILing (the spurious FAIL is
gh-45's multi-commit shape); it too is meaningful only once the bump is
committed.

Closes #66
```

## Spec self-review

- **Placeholders / TBDs:** none. The one replacement passage is given in full as a plain fenced block; every criterion is runnable as written, with its expected green output and its recorded red output. Step 6's green output shows `<sha>` where `check-version-bump.py` prints live short SHAs — that is the program's own variable output, not a placeholder in this document.

- **Every measurement this document states, and the command that printed it.** *Measurements are derived, not typed* requires the whole list, so this is the whole list. All are of the tree at `origin/main` (`bd7b2be6d455839928fdff3f011f085a231a6c54`), re-run while this document was written:

  | Measurement | Command |
  |---|---|
  | `dev-flow` 2.14.0, `dev-flow-worktree` 1.16.0 | the two `git show origin/main:…plugin.json` under *The two plugins' current versions* |
  | Command discipline is line 277 (`dev-flow`) / 271 (`dev-flow-worktree`), opener occurs once each | `git grep -n -F '- **Command discipline:**' origin/main -- <both>` |
  | the two Command discipline bullets are byte-identical | the `diff <(… sed -n 277p) <(… sed -n 271p) && echo IDENTICAL` |
  | the bullet already claims the success-criteria scope | the `git show … | sed -n 277p | grep -o 'This governs …'` |
  | `dev-flow` SKILL.md 279 lines, `dev-flow-worktree` 273 | `git grep -c '' origin/main -- <both>` |
  | `git show HEAD` in neither SKILL.md — no output, exit 1 | `git grep -c -F 'git show HEAD' origin/main -- <both>` |
  | the pipeline SKILL.md pair is not in `MIRROR_PAIRS` — no output, exit 1 | `git grep -n -F 'skills/dev-flow/SKILL.md' origin/main -- scripts/check-sync.py` |
  | `MIRROR_PAIRS` names `adversarial-review` + two agent pairs | `git grep -n '"name":' origin/main -- scripts/check-sync.py` (cited inline) |
  | `check-version-bump.py` reads `git show <head>:…`, `head` defaults to HEAD, `ahead` is strict `>` | `git show origin/main:scripts/check-version-bump.py | sed -n '58,72p;107,133p'` |
  | base resolves to `bd7b2be…`, branch sits at base | `git merge-base origin/main HEAD`; `git rev-parse origin/main`; `git log --oneline origin/main..HEAD` (empty) |

  **Of this document's own replacement text:** only the `[1]` shape, printed by step 0's guard, and the post-edit line counts 280 / 274, asserted by step 2 (the insert adds exactly one line). **No word count or character count of the new bullet is stated anywhere** — its length is under the author's hand and a later rewrite would falsify any such number, so the own-text branch of *Measurements are derived, not typed* is satisfied without a check a review rewrite would break (A11).

  **Recorded command output:** steps 0 (green), 4 and 5's green runs were produced against this tree while the document was written; step 0's red by copying this document to a scratch path outside the repo and splitting block 0's line there. Steps 1, 2 and 3's red runs were produced at the base with no edit (step 1 `changed []`; step 2 six mismatches — the reconstruction-equality, line-count, and once-count assertions, three per file; step 3 the two unbumped-HEAD mismatches, which is the very pre-commit spurious FAIL the change is about). Step 2's green path was exercised by computing `new` as the intended post-edit content instead of reading from disk — the only form available before the edit exists. Step 6's outputs are described from `check-version-bump.py`'s own control flow (read above): post-commit both rows `... OK` exit 0; pre-commit, this single-commit change's `merge-base..HEAD` is empty, so `touched()` finds nothing and it prints `no plugin directory touched ... OK` exit 0 — a vacuous pass, not the `... FAIL` the multi-commit gh-45 shape produces. The scratch artifact for step 0's red was deleted afterwards.

- **Internal consistency:** block 0 is inserted directly after the Command discipline bullet; step 2 asserts the reconstruction equals the base blob with exactly that bullet inserted, adds exactly one line, leaves the Command discipline line unchanged, and holds the bullet once (zero at base). The one-block `[1]` shape, the four-file scope, the 2.14.0 → 2.15.0 / 1.16.0 → 1.17.0 bumps, and the 279 → 280 / 273 → 274 counts agree everywhere they appear. The claim that steps 3 and 6 must run post-commit agrees with *What is true today*'s reading of `check-version-bump.py` and with A10.

- **Scope:** four files. Step 1 checks the set by path; step 2 checks each SKILL.md line-by-line against its blob; step 3 checks each manifest's version and description and that `marketplace.json` did not move. `CLAUDE.md`, `scripts/`, `CONTEXT.md`, `docs/adr/`, `.github/`, `marketplace.json`, the bullet's existing wording and every other Cross-Cutting bullet are each named in *Out of scope* with a reason, each a conclusion rather than a deferral.

- **Ambiguity:** the one place a fresh implementer could go wrong is applying the insert to only one file, or letting the two copies drift — step 2 reconstructs **both** from the same `bullet` object, so a one-file edit or any divergence fails. The second is running the committed-HEAD checks too early — called out in a dedicated section and in A10, and the steps themselves are labelled post-commit.

- **Positions taken:** the rule gets a pipeline-general home in the plugin `SKILL.md`'s Cross-Cutting Concerns, as a new sibling bullet (Verification ordering) directly after Command discipline rather than as a clause appended to it, mirrored byte-identically into `dev-flow-worktree`. `CLAUDE.md` is rejected as the home (pipeline-general property, un-mirrored file) and needs no consequential edit to its `check-version-bump.py` documentation; a Stage 2/3-local edit is rejected (the hazard is cross-stage); extending the Command discipline bullet is rejected (a distinct when-not-how concern; the section sibling-lists its kin *Measurements are derived*), and re-flowing it is rejected (it would forfeit the machine-checked *inserted, not rewritten* property); no ADR. Both plugins bump; `marketplace.json` does not move. Nothing is left for the implementer to decide.
