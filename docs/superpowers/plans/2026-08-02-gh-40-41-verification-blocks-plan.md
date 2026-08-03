---
dev-flow:
  slug: gh-40-41-verification-blocks
  spec: docs/superpowers/specs/2026-08-02-gh-40-41-verification-blocks-design.md
---

# gh-40/41 verification blocks — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land three passages of markdown — one replaced line in the machine-checked `adversarial-review` mirror pair, and one appended sentence-group plus one new Cross-Cutting bullet in each hand-mirrored pipeline `SKILL.md` — plus the two minor version bumps those edits oblige.

**Architecture:** The design (`docs/superpowers/specs/2026-08-02-gh-40-41-verification-blocks-design.md`) gives all three passages as plain fenced blocks and decides every placement, anchor line and version target. **No task retypes any of that text.** The three passages are singled out because they are the only text here whose drift is *silent*: a byte retyped wrong ships into a plugin file, and `check-sync.py` passes on two identically-mangled copies. Everything else the plan carries over from the design — the anchor lines, the post-edit lengths, the version floors, the six-file scope list, and Task 4's verbatim copy of the design's `## Verification` commands — is executed against the real tree, so a stale copy fails a step here rather than shipping a wrong byte. Every task obtains its replacement text by reading the blocks off the design on disk through the shared reader, applies it positionally, and then re-derives from git that each edited file is byte-for-byte its merge-base blob with exactly the intended edit applied. Tasks are grouped so that a mirror pair is never left one-sided at a commit boundary: the two `adversarial-review` copies move together (`check-sync.py` fails otherwise), and the two pipeline copies move together (nothing mechanical would catch a one-sided edit there, so Task 2 asserts the substitution-image property by hand).

**Tech Stack:** Markdown, plus Python 3 helper scripts (`scripts/design_blocks.py`, `scripts/check-sync.py`). **There is no test framework in this repo.** The whole check suite is `python3 scripts/check-sync.py` and `claude plugin validate .` (exit 0 with exactly 8 `No author information provided` warnings), and the design's `## Verification` section, which Task 4 runs in full.

## Global Constraints

Every task's requirements implicitly include this section.

**1. Six files, and no seventh.** These are the only files any task may create or modify:

| # | File | Edit |
|---|---|---|
| 1 | `plugins/dev-flow/skills/adversarial-review/SKILL.md` | line 29 replaced by block 0 |
| 2 | `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md` | line 29 replaced by block 0 (the identical line) |
| 3 | `plugins/dev-flow/skills/dev-flow/SKILL.md` | line 276 replaced by block 1; block 2 inserted as the new line 277 |
| 4 | `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` | line 270 replaced by block 1; block 2 inserted as the new line 271 |
| 5 | `plugins/dev-flow/.claude-plugin/plugin.json` | `"version"` `2.9.0` → `2.10.0` |
| 6 | `plugins/dev-flow-worktree/.claude-plugin/plugin.json` | `"version"` `1.11.0` → `1.12.0` |

The design and this plan under `docs/superpowers/` are committed by the pipeline (`docs: commit`); **no task edits them either**, and every scope check below excludes that directory with a `':!docs/superpowers/'` pathspec.

**Hard-excluded, per the design's *Out of scope*:** `CLAUDE.md`, `CONTEXT.md`, anything under `scripts/`, anything under `.github/`, both plugin `README.md`s, anything under `docs/adr/`, and `.claude-plugin/marketplace.json`. Each is a decided conclusion in the design, not a deferral. **A task that appears to need one of them is a blocker to report — stop and report it; do not work around it, and do not edit the file.** `scripts/design_blocks.py` is *used* by every task and *modified* by none.

**2. Replacement text is read, never retyped.** The three passages live only in the design. Every task that applies or checks one obtains it by:

```sh
python3 scripts/design_blocks.py docs/superpowers/specs/2026-08-02-gh-40-41-verification-blocks-design.md
```

to confirm the shape, and then, inside its own program, `sys.path.insert(0, "scripts")` followed by `read_blocks(DESIGN, [1, 1, 1])`. The design's plain fenced blocks are indices **0, 1, 2** with shape **`[1, 1, 1]`** — three single-line blocks. `read_blocks` takes the shape as a required argument and exits non-zero if it moved; the CLI above only *reports* the shape and always exits 0, so it is a convenience, never the guard. Identifying prefixes only, so you know which is which:

- **block 0** starts `| **design** | The design rubric` — the `adversarial-review` table row.
- **block 1** starts `- **Command discipline:**` — the complete new pipeline bullet.
- **block 2** starts `- **Measurements are derived, not typed.**` — the new Cross-Cutting bullet.

If `read_blocks` raises `design code-block shape is …, want [1, 1, 1]`, **stop and report**: the design was edited after this plan captured its shape, and every anchor index below is unreliable.

**3. Every verification obeys the rules this change lands.** This is the first work done under them, so compliance is the deliverable, not a formality:

- **A criterion must be able to fail.** No `--stat`. No human-read output standing in for an assertion. No scope that excludes everything it would catch. No step unreachable behind an earlier short-circuit — every program below collects all mismatches into a list and prints them before exiting.
- **A step consuming a computed git ref passes it to `git` as an `argv` element from `python3`/`subprocess`.** **No command in this plan uses an inline `$(git …)` substitution** — the form appears only where this sentence and its restatement under *Self-review* quote it. The runner refuses a command substitution inside a multi-command line, and `git merge-base` prints nothing on failure — an unquoted `$(…)` silently degrades a base comparison into a working-tree-vs-index one that passes on a branch committed per task. A grep pinned to a **literal** SHA is not a computed ref and stays writable as one line of shell.
- **Every measurement stated is printed by a command given beside it**, and no number is stated that the output does not show.

**4. Setup, branch and integration.** Work in place in the current checkout. **Do not create a git worktree** and do not invoke `superpowers:using-git-worktrees`. The branch `tayl0r/gh-40-41-verification-blocks` already exists and is checked out — do not create or switch branches. Do not push, do not open a PR, do not merge, do not run a final review. The pipeline owns every stage transition.

**5. Versions bump the minor segment** (`CLAUDE.md`): `2.9.0` → `2.10.0` and `1.11.0` → `1.12.0`. `2.9.0` → `2.10.0` *is* a minor bump — the segments are numbers, not decimals. Neither `description` changes, so `marketplace.json` stays untouched.

## Base facts, pinned to `bf7676b`

`bf7676b` is this branch's base; `git merge-base origin/main HEAD` resolved to it when this plan was written. Every constant used below was printed at that revision by the command beside it, and the claims are past-tense at that revision. Tasks compute the base rather than hardcoding it, so a base that moved and shifted the lines fails loudly instead of editing the wrong line.

**Anchor lines** — `adversarial-review` line 29 in both copies, `dev-flow/skills/dev-flow/SKILL.md` line 276, `dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` line 270:

```sh
git grep -n -F -e '- **Command discipline:**' -e '| **design** | The design rubric' bf7676b -- plugins/
```

**File lengths before the edit** — 89, 271, 89, 277:

```sh
git grep -c '' bf7676b -- plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md plugins/dev-flow/skills/adversarial-review/SKILL.md plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
```

```text
bf7676b:plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md:89
bf7676b:plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md:271
bf7676b:plugins/dev-flow/skills/adversarial-review/SKILL.md:89
bf7676b:plugins/dev-flow/skills/dev-flow/SKILL.md:277
```

**Versions before the bump** — `2.9.0` and `1.11.0`:

```sh
git grep -n -F '"version"' bf7676b -- plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
```

```text
bf7676b:plugins/dev-flow-worktree/.claude-plugin/plugin.json:3:  "version": "1.11.0",
bf7676b:plugins/dev-flow/.claude-plugin/plugin.json:3:  "version": "2.9.0",
```

**The phrase block 0 removes**, present in exactly the two `adversarial-review` copies outside `docs/superpowers/`:

```sh
git grep -c -F 'success criteria — plus the input-contract' bf7676b -- . ':!docs/superpowers/'
```

```text
bf7676b:plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md:1
bf7676b:plugins/dev-flow/skills/adversarial-review/SKILL.md:1
```

**No file in the tree contained a carriage return** at `bf7676b`, so the line-based reads and the `"\n".join(...) + "\n"` writes below cannot flip a line ending:

```sh
git grep -c -P '\r' bf7676b -- .
```

No output, exit 1. It is falsifiable, and was falsified rather than asserted: run in a `git clone` of this branch outside the repo with one CRLF line injected into `plugins/dev-flow/skills/adversarial-review/SKILL.md` and committed, the same command — against that commit — printed `plugins/dev-flow/skills/adversarial-review/SKILL.md:1`, prefixed by the scratch commit's SHA, and exited 0. The clone was deleted afterwards.

The post-edit numbers — **278 / 272 / 89 / 89** lines and the **`2.10.0` / `1.12.0`** floors — are *asserted rather than measured here*: Task 2's, Task 3's and Task 4's programs fail if any is wrong.

## File Structure

No file is created. Six files are modified, in three groups drawn so that no mirror pair is ever left one-sided at a commit boundary:

- **Group A — `adversarial-review/SKILL.md` × 2 (Task 1).** A machine-checked mirror pair: `scripts/check-sync.py` requires the two copies to be line-for-line identical after canonicalizing `dev-flow-worktree` → `dev-flow`. Editing one without the other fails the repo's own check, so they cannot be separate tasks. This is also the only group whose edit **removes** a phrase, so the residue grep lives here.
- **Group B — the two pipeline `SKILL.md`s (Task 2).** A hand-mirrored pair: `check-sync.py` does not know it exists (at `bf7676b` the two files did not even have the same length, which its schema requires), so a one-sided edit is caught by **nothing mechanical**. They must move in one task, and that task asserts the substitution-image property itself.
- **Group C — the two `plugin.json`s (Task 3).** Each plugin ships *both* a pipeline `SKILL.md` and its own copy of `adversarial-review/SKILL.md`, so both plugins bump and each bump covers both of its plugin's text edits. Bumping once after Groups A and B is what keeps that a single bump per plugin rather than two.

**Task 4** adds no file change. It is the acceptance gate: it runs the design's `## Verification` section in full — the six-file scope equality no per-task check makes, and every reconstruction assertion again over the finished tree — and it carries the `pre-merge` hand-off.

---

### Task 1: Block 0 into both `adversarial-review/SKILL.md` copies

**Files:**
- Modify: `plugins/dev-flow/skills/adversarial-review/SKILL.md:29`
- Modify: `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md:29`
- Test: none — this repo has no test framework. The checks are the programs in Steps 3–5.

**Interfaces:**
- Consumes: block 0 of `docs/superpowers/specs/2026-08-02-gh-40-41-verification-blocks-design.md`, read through `read_blocks(DESIGN, [1, 1, 1])[0][0]`; anchor line `AR_I = 29`, 1-based, at the merge base.
- Produces: both copies at 89 lines with line 29 equal to block 0. Task 2 relies on nothing from this task except that the working tree is otherwise clean; Task 4's scope equality relies on exactly these two paths having changed.

- [ ] **Step 1: Confirm the design's block shape**

Run:

```sh
python3 scripts/design_blocks.py docs/superpowers/specs/2026-08-02-gh-40-41-verification-blocks-design.md
```

Expected: `shape: [1, 1, 1]`, then three `[i] len=1: …` preview lines whose prefixes are `| **design** | The design rubric`, `- **Command discipline:**` and `- **Measurements are derived, not typed.**`. **Anything else: stop and report** — the design moved and every anchor in this plan is unreliable.

- [ ] **Step 2: Apply block 0 to both copies**

The program reads block 0 from the design and refuses to write if the line it is about to replace already differs from the merge-base blob — which is what a moved base, a hand edit, or a second run of this program looks like. Run:

```sh
python3 - <<'PY'
import subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-02-gh-40-41-verification-blocks-design.md"
AR = ["plugins/dev-flow/skills/adversarial-review/SKILL.md",
      "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md"]
AR_I = 29

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

b0 = read_blocks(DESIGN, [1, 1, 1])[0][0]
base = git("merge-base", "origin/main", "HEAD").strip()
print("base:", base)
for path in AR:
    disk = split(Path(path).read_text(encoding="utf-8"))
    old = split(git("show", base + ":" + path))
    if disk[AR_I - 1] != old[AR_I - 1]:
        raise SystemExit("%s line %d already differs from the base blob -- already applied,"
                         " hand-edited, or the base moved; stop and report" % (path, AR_I))
    disk[AR_I - 1] = b0
    Path(path).write_text("\n".join(disk) + "\n", encoding="utf-8")
    print("applied block 0 to %s line %d" % (path, AR_I))
PY
echo "exit=$?"
```

Expected: a `base:` line carrying a 40-character SHA, then one `applied block 0 to … line 29` line per file, and `exit=0`.

- [ ] **Step 3: Verify reconstruction, mirror-identity and scope**

Every mismatch is collected and printed before exit, so a first failure never hides a second. Run:

```sh
python3 - <<'PY'
import subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-02-gh-40-41-verification-blocks-design.md"
AR_DF = "plugins/dev-flow/skills/adversarial-review/SKILL.md"
AR_WT = "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md"
AR_I, WANT_LEN = 29, 89
SCOPE = ["--", ".", ":!docs/superpowers/"]
WANT_SCOPE = sorted([AR_DF, AR_WT])

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

b0 = read_blocks(DESIGN, [1, 1, 1])[0][0]
base = git("merge-base", "origin/main", "HEAD").strip()
print("base:", base)
print("block 0 'dev-flow' occurrences:", b0.count("dev-flow"))
bad = []
if b0.count("dev-flow") != 0:
    bad.append("block 0 names a plugin variant, so the two copies are no longer byte-identical")
for path in (AR_DF, AR_WT):
    o = split(git("show", base + ":" + path))
    n = split(Path(path).read_text(encoding="utf-8"))
    print("%s: %d lines" % (path, len(n)))
    if n != o[:AR_I - 1] + [b0] + o[AR_I:]:
        bad.append("%s is not its base blob with line %d replaced by block 0" % (path, AR_I))
    if n.count(b0) != 1:
        bad.append("%s holds block 0 %d times, want exactly 1" % (path, n.count(b0)))
    if len(n) != WANT_LEN:
        bad.append("%s is %d lines, want %d" % (path, len(n), WANT_LEN))
changed = sorted(p for p in git("diff", "--name-only", base, *SCOPE).split("\n") if p)
print("changed:", changed)
if changed != WANT_SCOPE:
    bad.append("file scope: changed %s, want %s" % (changed, WANT_SCOPE))
for why in bad:
    print("MISMATCH:", why)
print("task 1:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected: `block 0 'dev-flow' occurrences: 0`, then `plugins/dev-flow/skills/adversarial-review/SKILL.md: 89 lines` and the matching `plugins/dev-flow-worktree/…: 89 lines`, a `changed:` line listing exactly the two `adversarial-review` paths, then `task 1: OK` and `exit=0`. Run before Step 2, the same program prints `MISMATCH:` lines for both files' reconstruction and for `changed []` and exits 1.

- [ ] **Step 4: Verify the removed phrase is gone from shipped text**

Block 0 splits the junction `success criteria — plus the input-contract`, so it must no longer appear outside `docs/superpowers/`. The pathspec is required: four prior records and the design itself legitimately contain it. Run:

```sh
git grep -n -F 'success criteria — plus the input-contract' -- . ':!docs/superpowers/'
echo "exit=$?"
```

Expected: **no output** and `exit=1`. Before Step 2 this same command printed both copies of line 29 and exited 0, which is its red run.

- [ ] **Step 5: Verify the machine-checked mirror pair**

Run:

```sh
python3 scripts/check-sync.py
echo "exit=$?"
```

Expected — unchanged from before the edit, because block 0 replaces a line rather than adding one:

```text
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)
check-sync: all checks passed
exit=0
```

A one-sided edit prints `mirror pair "adversarial-review" ... FAIL`, names `line 29` and both sides, and exits 1.

- [ ] **Step 6: Commit**

```sh
git add plugins/dev-flow/skills/adversarial-review/SKILL.md plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
git commit -m "adversarial-review: a criterion that cannot fail is untestable, and unprinted measurements (#40, #41)"
```

---

### Task 2: Blocks 1 and 2 into both pipeline `SKILL.md`s

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md:276` (replace) and insert a new line 277
- Modify: `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md:270` (replace) and insert a new line 271
- Test: none — the checks are the programs in Steps 3–4.

**Interfaces:**
- Consumes: blocks 1 and 2 of the design, read through `read_blocks(DESIGN, [1, 1, 1])` as `blocks[1][0]` and `blocks[2][0]`; anchor lines `DF_I = 276` and `WT_I = 270`, 1-based, at the merge base. Depends on Task 1 only for the working tree being otherwise clean.
- Produces: `plugins/dev-flow/skills/dev-flow/SKILL.md` at 278 lines and `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` at 272 lines, each with block 1 at its anchor and block 2 directly after it.

**Why this pair is one task:** `check-sync.py` does not know this pair exists — at `bf7676b` the two files were 277 and 271 lines, which its line-parallel schema cannot accept — so a one-sided edit is caught by nothing mechanical. Step 4 asserts the substitution-image property that `check-sync.py` would otherwise provide.

**Why there is no removed-phrase grep here:** block 1 is a **pure append** — every byte of the base bullet is carried over unchanged — and block 2 is entirely new, so this edit removes no phrase. Step 4 makes the stronger assertion in its place: that the base line is a *strict prefix* of block 1.

- [ ] **Step 1: Confirm the design's block shape**

Run:

```sh
python3 scripts/design_blocks.py docs/superpowers/specs/2026-08-02-gh-40-41-verification-blocks-design.md
```

Expected: `shape: [1, 1, 1]` and the three preview lines. **Anything else: stop and report.**

- [ ] **Step 2: Apply block 1 and insert block 2 in both files**

Run:

```sh
python3 - <<'PY'
import subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-02-gh-40-41-verification-blocks-design.md"
TARGETS = [("plugins/dev-flow/skills/dev-flow/SKILL.md", 276),
           ("plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md", 270)]

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

blocks = read_blocks(DESIGN, [1, 1, 1])
b1, b2 = blocks[1][0], blocks[2][0]
base = git("merge-base", "origin/main", "HEAD").strip()
print("base:", base)
for path, i in TARGETS:
    disk = split(Path(path).read_text(encoding="utf-8"))
    old = split(git("show", base + ":" + path))
    if disk[i - 1] != old[i - 1]:
        raise SystemExit("%s line %d already differs from the base blob -- already applied,"
                         " hand-edited, or the base moved; stop and report" % (path, i))
    if not b1.startswith(old[i - 1]) or b1 == old[i - 1]:
        raise SystemExit("%s: block 1 is not a strict extension of base line %d; this edit"
                         " removes no phrase, so every existing byte must survive" % (path, i))
    disk[i - 1:i] = [b1, b2]
    Path(path).write_text("\n".join(disk) + "\n", encoding="utf-8")
    print("applied block 1 at %s line %d, inserted block 2 as line %d" % (path, i, i + 1))
PY
echo "exit=$?"
```

Expected: a `base:` line, then `applied block 1 at plugins/dev-flow/skills/dev-flow/SKILL.md line 276, inserted block 2 as line 277` and the matching `… line 270, inserted block 2 as line 271`, and `exit=0`.

- [ ] **Step 3: Verify reconstruction, strict-prefix, hand-mirror and scope**

Four families of assertion, all mismatches collected before exit. Run:

```sh
python3 - <<'PY'
import subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-02-gh-40-41-verification-blocks-design.md"
AR_DF = "plugins/dev-flow/skills/adversarial-review/SKILL.md"
AR_WT = "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md"
DF = "plugins/dev-flow/skills/dev-flow/SKILL.md"
WT = "plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md"
DF_I, WT_I = 276, 270
WANT_LEN = {DF: 278, WT: 272}
SCOPE = ["--", ".", ":!docs/superpowers/"]
WANT_SCOPE = sorted([AR_DF, AR_WT, DF, WT])

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
print("base:", base)
old = {p: split(git("show", base + ":" + p)) for p in (DF, WT)}
now = {p: split(Path(p).read_text(encoding="utf-8")) for p in (DF, WT)}

blocks = read_blocks(DESIGN, [1, 1, 1])
b1, b2 = blocks[1][0], blocks[2][0]
counts = [b1.count("dev-flow"), b2.count("dev-flow")]
print("'dev-flow' occurrences in blocks 1 and 2:", counts)
bad = []
if counts != [0, 0]:
    bad.append("a block names a plugin variant, so its two copies are no longer byte-identical")

for path, i in ((DF, DF_I), (WT, WT_I)):
    o, n = old[path], now[path]
    print("%s: %d lines" % (path, len(n)))
    if n != o[:i - 1] + [b1, b2] + o[i:]:
        bad.append("%s is not its base blob with line %d replaced by block 1 and block 2"
                   " inserted directly after it" % (path, i))
    if n.count(b2) != 1:
        bad.append("%s holds block 2 %d times, want exactly 1" % (path, n.count(b2)))
    if not b1.startswith(o[i - 1]) or b1 == o[i - 1]:
        bad.append("%s: block 1 is not a strict extension of base line %d; this edit removes"
                   " no phrase, so every existing byte must survive" % (path, i))
    if len(n) != WANT_LEN[path]:
        bad.append("%s is %d lines, want %d" % (path, len(n), WANT_LEN[path]))

sub = lambda s: s.replace("dev-flow-worktree", "dev-flow")
if sub(now[WT][WT_I - 1]) != now[DF][DF_I - 1]:
    bad.append("the edited Command discipline lines are not substitution images")
if sub(now[WT][WT_I]) != now[DF][DF_I]:
    bad.append("the inserted Measurements bullets are not substitution images")
if sub(old[WT][WT_I - 1]) != old[DF][DF_I - 1]:
    bad.append("the two Command discipline lines were not images at the base either -- the"
               " anchor line numbers are wrong")

changed = sorted(p for p in git("diff", "--name-only", base, *SCOPE).split("\n") if p)
print("changed:", changed)
if changed != WANT_SCOPE:
    bad.append("file scope: changed %s, want %s" % (changed, WANT_SCOPE))
for why in bad:
    print("MISMATCH:", why)
print("task 2:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected: `'dev-flow' occurrences in blocks 1 and 2: [0, 0]`, then `plugins/dev-flow/skills/dev-flow/SKILL.md: 278 lines` and `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md: 272 lines`, a `changed:` line listing the four markdown paths, then `task 2: OK` and `exit=0`. Run before Step 2 it prints reconstruction, `holds block 2 0 times` and line-count mismatches for both files, plus a scope mismatch, and exits 1.

- [ ] **Step 4: Verify the machine-checked pair is still clean**

Task 1's pair is untouched here, so this must still pass — and it fails if a stray edit landed in either `adversarial-review` copy. Run:

```sh
python3 scripts/check-sync.py
echo "exit=$?"
```

Expected: `check-sync: mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)`, then `check-sync: all checks passed` and `exit=0`.

- [ ] **Step 5: Commit**

```sh
git add plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
git commit -m "dev-flow: Command discipline governs emitted success criteria; measurements are derived (#40, #41)"
```

---

### Task 3: Version bumps

**Files:**
- Modify: `plugins/dev-flow/.claude-plugin/plugin.json:3`
- Modify: `plugins/dev-flow-worktree/.claude-plugin/plugin.json:3`
- Test: none — the checks are the programs in Steps 2–3.

**Interfaces:**
- Consumes: nothing from Tasks 1–2 except that both plugins' shipped text has already changed, which is what obliges the bump. Both plugins bump because `adversarial-review/SKILL.md` exists inside *both* plugin directories, so Task 1 alone already changed both shipped plugins.
- Produces: `plugins/dev-flow/.claude-plugin/plugin.json` at `"version": "2.10.0"` and `plugins/dev-flow-worktree/.claude-plugin/plugin.json` at `"version": "1.12.0"`. Task 4's step 6a asserts both as a **floor** and asserts strict inequality against `origin/main`.

**Ordering:** this task runs **after** Tasks 1 and 2. One bump per plugin covers both of that plugin's text edits; bumping inside each text task would double-bump.

**Do not reformat the JSON.** The edit is a single-line string replacement; re-serializing with `json.dump` would rewrite the whole file and put a stray path into scope.

- [ ] **Step 1: Apply both bumps**

The program asserts each old `"version"` line appears exactly once before replacing it, so a file already bumped or unexpectedly shaped halts rather than being written. Run:

```sh
python3 - <<'PY'
import sys
from pathlib import Path

BUMPS = {
    "plugins/dev-flow/.claude-plugin/plugin.json": ('"version": "2.9.0",', '"version": "2.10.0",'),
    "plugins/dev-flow-worktree/.claude-plugin/plugin.json": ('"version": "1.11.0",', '"version": "1.12.0",'),
}
for path, (old, new) in sorted(BUMPS.items()):
    text = Path(path).read_text(encoding="utf-8")
    n = text.count(old)
    print("%s: %d occurrences of %s" % (path, n, old))
    if n != 1:
        raise SystemExit("%s: want exactly 1 occurrence of %s; stop and report" % (path, old))
    Path(path).write_text(text.replace(old, new), encoding="utf-8")
    print("bumped %s -> %s" % (path, new))
PY
echo "exit=$?"
```

Expected: one `… 1 occurrences of "version": "2.9.0",` line and one `… 1 occurrences of "version": "1.11.0",` line, each followed by its `bumped …` line, and `exit=0`.

- [ ] **Step 2: Verify versions are strictly greater than published, and the six-file scope**

The comparison is a **tuple of integers**, not a string — `"2.10.0" > "2.9.0"` is false lexicographically, and this is the first change in the repo's history where that bites. `WANT` is a floor, never an equality, so re-targeting upward leaves it green. Run:

```sh
python3 - <<'PY'
import json, subprocess, sys
from pathlib import Path

JSON_DF = "plugins/dev-flow/.claude-plugin/plugin.json"
JSON_WT = "plugins/dev-flow-worktree/.claude-plugin/plugin.json"
WANT = {JSON_DF: (2, 10, 0), JSON_WT: (1, 12, 0)}     # a floor, never an equality
SCOPE = ["--", ".", ":!docs/superpowers/"]
WANT_SCOPE = sorted([
    JSON_DF, JSON_WT,
    "plugins/dev-flow/skills/adversarial-review/SKILL.md",
    "plugins/dev-flow/skills/dev-flow/SKILL.md",
    "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md",
    "plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md",
])

def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout

def ver(text):
    return tuple(int(p) for p in json.loads(text)["version"].split("."))

git("fetch", "origin", "main")
bad = []
for path, want in sorted(WANT.items()):
    mine = ver(Path(path).read_text(encoding="utf-8"))
    published = ver(git("show", "origin/main:" + path))
    print("%s: mine %s, origin/main %s" % (path, mine, published))
    if mine < want:
        bad.append("%s is %s, below the designed floor %s" % (path, mine, want))
    if mine <= published:
        bad.append("%s is %s, not strictly greater than origin/main's %s"
                   % (path, mine, published))
base = git("merge-base", "origin/main", "HEAD").strip()
changed = sorted(p for p in git("diff", "--name-only", base, *SCOPE).split("\n") if p)
print("changed:", changed)
if changed != WANT_SCOPE:
    bad.append("file scope: changed %s, want %s" % (changed, WANT_SCOPE))
for why in bad:
    print("MISMATCH:", why)
print("task 3:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected: two `… mine (…), origin/main (…)` lines, a `changed:` line listing all six paths, then `task 3: OK` and `exit=0`. Run before Step 1 it prints four `MISMATCH:` lines — one *below the designed floor* and one *not strictly greater* per plugin — plus a scope mismatch, and exits 1.

- [ ] **Step 3: Verify the manifests still validate**

Both halves are asserted, because either alone passes vacuously: the command exits 0 *while* emitting the warnings, and a count assertion alone would pass on a run that errored out. Run:

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
    bad.append("%d 'No author information provided' warnings, want exactly %d"
               % (n, WANT_WARNINGS))
for why in bad:
    print("MISMATCH:", why)
print("validate:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected:

```text
claude plugin validate: exit 0, 8 author warnings
validate: OK
exit=0
```

- [ ] **Step 4: Commit**

```sh
git add plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
git commit -m "dev-flow 2.10.0, dev-flow-worktree 1.12.0"
```

---

### Task 4: Run the design's `## Verification` in full, then hand off 6b

**Files:** none modified. This task is the acceptance gate.

**Interfaces:**
- Consumes: the finished tree from Tasks 1–3, and blocks 0–2 of the design, re-read from disk by steps 0 and 2 below.
- Produces: the pass evidence the pipeline's Execute-stage report carries, plus the `pre-merge` hand-off in *After the last task*.

The seven commands below are the design's `## Verification` steps 0 through 6a, **verbatim and runnable as written** — byte-for-byte the design's, so what passes here is the design's own criteria rather than a paraphrase of them. **Do not restyle them.** That is why steps 2 and 6a wrap `git` in `subprocess.run(…, check=True)` where Tasks 1–3's own programs wrap it with a `FAILED: git …` message: the design's reason, carried here, is that failures of the *producers* — `git`, `read_blocks` — are left to raise as themselves, since they name the failing command and no traceback can be mistaken for a pass. Normalizing the style would put this task out of step with the design it quotes, which is the drift this change is about.

They are not a re-statement of the per-task checks. Step 1 is the only place the **six-file scope equality** is asserted over the finished tree. Step 2 is the only place all four markdown files are reconstructed **in one program over the finished tree** — which is not what Tasks 1 and 2 proved: each ran before the next task's edits, and `git diff --name-only` equality catches a *seventh path*, never a second edit to one of the six. Only step 2 can still see a markdown file that was correct when its own task verified it and has moved since. Run them in order and read each expected output before moving on.

- [ ] **Step 0 — Block shape, asserted rather than reported**

`design_blocks.py`'s CLI is a shape *reporter*: it prints the shape and unconditionally returns 0, so running it can never fail on a mismatch. The **guard** is `read_blocks`, where the shape is a required argument and a mismatch is a `SystemExit`. This step calls the guard.

```sh
python3 - <<'PY'
import sys
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
DESIGN = "docs/superpowers/specs/2026-08-02-gh-40-41-verification-blocks-design.md"
for i, b in enumerate(read_blocks(DESIGN, [1, 1, 1])):
    print("  [%d] %s" % (i, b[0][:70]))
print("shape guard: OK")
PY
echo "exit=$?"
```

Expected: three preview lines — block 0 the `| **design** |` table row, block 1 the *Command discipline* bullet, block 2 the *Measurements* bullet — then `shape guard: OK` and `exit=0`. Anything else, in particular `design code-block shape is …`, means the design was edited after this plan captured its shape: **stop and report**.

- [ ] **Step 1 — File scope: exactly six files, and no seventh**

The `--name-only` set is compared for *equality* against the authorized list, so a stray edit to `CLAUDE.md`, `CONTEXT.md`, `scripts/`, `.github/`, a `README.md` or `marketplace.json` fails the step **and names the offending path**. There is deliberately no `--stat` line and no `--quiet` companion.

```sh
python3 - <<'PY'
import subprocess, sys
SCOPE = ["--", ".", ":!docs/superpowers/"]
WANT = sorted([
    "plugins/dev-flow/.claude-plugin/plugin.json",
    "plugins/dev-flow/skills/adversarial-review/SKILL.md",
    "plugins/dev-flow/skills/dev-flow/SKILL.md",
    "plugins/dev-flow-worktree/.claude-plugin/plugin.json",
    "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md",
    "plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md",
])
def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
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

Expected: a `base:` line carrying a 40-character SHA, then `file scope: OK` and `exit=0`. A base that cannot be computed fails as one quotable line naming the command, its exit status and git's message.

- [ ] **Step 2 — Reconstruction and design conformance**

Four assertion families: each edited line is the block read from the design on disk; each target file is byte-for-byte its merge-base blob with exactly the intended edit applied; the two hand-mirrored files' edited passages are exact substitution images of one another, after the edit *and* at the base; and the one measurement the design states about its own replacement text is re-derived here rather than trusted.

```sh
python3 - <<'PY'
import subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-02-gh-40-41-verification-blocks-design.md"
AR_DF = "plugins/dev-flow/skills/adversarial-review/SKILL.md"
AR_WT = "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md"
DF = "plugins/dev-flow/skills/dev-flow/SKILL.md"
WT = "plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md"
AR_I, DF_I, WT_I = 29, 276, 270          # 1-based anchor lines, at the base
WANT_LEN = {DF: 278, WT: 272, AR_DF: 89, AR_WT: 89}   # after the edit

def git(*args):
    return subprocess.run(("git",) + args, capture_output=True, text=True,
                          check=True).stdout
def split(text):
    out = text.split("\n")
    if out and out[-1] == "":
        out.pop()
    return out
base = git("merge-base", "origin/main", "HEAD").strip()
def old(path):
    return split(git("show", base + ":" + path))
def now(path):
    return split(Path(path).read_text(encoding="utf-8"))

b0, b1, b2 = (b[0] for b in read_blocks(DESIGN, [1, 1, 1]))
bad = []

for path in (AR_DF, AR_WT):
    o, n = old(path), now(path)
    if n != o[:AR_I - 1] + [b0] + o[AR_I:]:
        bad.append("%s is not its base blob with line %d replaced by block 0" % (path, AR_I))
    if n.count(b0) != 1:
        bad.append("%s holds block 0 %d times, want exactly 1" % (path, n.count(b0)))

for path, i in ((DF, DF_I), (WT, WT_I)):
    o, n = old(path), now(path)
    if n != o[:i - 1] + [b1, b2] + o[i:]:
        bad.append("%s is not its base blob with line %d replaced by block 1 and block 2"
                   " inserted directly after it" % (path, i))
    if n.count(b2) != 1:
        bad.append("%s holds block 2 %d times, want exactly 1" % (path, n.count(b2)))
    if not b1.startswith(o[i - 1]) or b1 == o[i - 1]:
        bad.append("%s: block 1 is not a strict extension of base line %d; this edit removes"
                   " no phrase, so every existing byte must survive" % (path, i))

sub = lambda s: s.replace("dev-flow-worktree", "dev-flow")
if sub(now(WT)[WT_I - 1]) != now(DF)[DF_I - 1]:
    bad.append("the edited Command discipline lines are not substitution images")
if sub(now(WT)[WT_I]) != now(DF)[DF_I]:
    bad.append("the inserted Measurements bullets are not substitution images")
if sub(old(WT)[WT_I - 1]) != old(DF)[DF_I - 1]:
    bad.append("the two Command discipline lines were not images at the base either -- the"
               " anchor line numbers are wrong")

counts = [b.count("dev-flow") for b in (b0, b1, b2)]
print("dev-flow occurrences per block:", counts)
if counts != [0, 0, 0]:
    bad.append("a block names a plugin variant, so its two copies are no longer byte-identical")

for path, want in sorted(WANT_LEN.items()):
    if len(now(path)) != want:
        bad.append("%s is %d lines, want %d" % (path, len(now(path)), want))

for why in bad:
    print("MISMATCH:", why)
print("reconstruction:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected: `dev-flow occurrences per block: [0, 0, 0]`, then `reconstruction: OK` and `exit=0`. If the shape guard trips instead, **stop and report**.

- [ ] **Step 3 — Residue: the split junction is gone from shipped text**

Expect no output and a non-zero exit. The pathspec is required: four prior records under `docs/superpowers/`, and the design itself, legitimately contain the phrase.

```sh
git grep -n -F 'success criteria — plus the input-contract' -- . ':!docs/superpowers/'
```

- [ ] **Step 4 — Mirror-pair sync**

```sh
python3 scripts/check-sync.py
echo "exit=$?"
```

Expected:

```text
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)
check-sync: all checks passed
exit=0
```

- [ ] **Step 5 — `claude plugin validate .`: exit 0 *and* exactly 8 author warnings**

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
    bad.append("%d 'No author information provided' warnings, want exactly %d"
               % (n, WANT_WARNINGS))
for why in bad:
    print("MISMATCH:", why)
print("validate:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected:

```text
claude plugin validate: exit 0, 8 author warnings
validate: OK
exit=0
```

- [ ] **Step 6a — Versions strictly greater than published, at implementation**

```sh
python3 - <<'PY'
import json, subprocess, sys
from pathlib import Path
JSON_DF = "plugins/dev-flow/.claude-plugin/plugin.json"
JSON_WT = "plugins/dev-flow-worktree/.claude-plugin/plugin.json"
WANT = {JSON_DF: (2, 10, 0), JSON_WT: (1, 12, 0)}     # a floor, never an equality
def git(*args):
    return subprocess.run(("git",) + args, capture_output=True, text=True,
                          check=True).stdout
def ver(text):
    return tuple(int(p) for p in json.loads(text)["version"].split("."))
git("fetch", "origin", "main")
bad = []
for path, want in sorted(WANT.items()):
    mine = ver(Path(path).read_text(encoding="utf-8"))
    published = ver(git("show", "origin/main:" + path))
    print("%s: mine %s, origin/main %s" % (path, mine, published))
    if mine < want:
        bad.append("%s is %s, below the designed floor %s" % (path, mine, want))
    if mine <= published:
        bad.append("%s is %s, not strictly greater than origin/main's %s"
                   % (path, mine, published))
for why in bad:
    print("MISMATCH:", why)
print("versions:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected: two `mine … origin/main …` lines, then `versions: OK` and `exit=0`.

- [ ] **Step 7 — Confirm nothing is uncommitted outside `docs/superpowers/`**

Tasks 1–3 each committed their own files; the design and this plan are the pipeline's to commit. Run:

```sh
git status --porcelain -- . ':!docs/superpowers/'
echo "exit=$?"
```

Expected: **no output** and `exit=0`. Any line printed here is an uncommitted or untracked file inside the change's scope — report it rather than committing it, since the six authorized files are already committed.

- [ ] **Step 8 — Hand the `pre-merge` version re-check to the orchestrator**

This is the last checkbox in the plan. Do **not** attempt step 6b yourself — it cannot run yet, because it must run after an integration that has not happened. Report to the orchestrator, in the Execute-stage completion report, the whole of the *After the last task* section below, and say plainly that it is outstanding.

---

## After the last task: the `pre-merge` version re-check (step 6b)

**This is prose addressed to the orchestrator, and it is deliberately not a `- [ ]` checkbox.** Every checkbox in this plan is completable inside the Execute stage; this is not. It runs at a **stage boundary** — after the *last* merge or rebase of `origin/main` into this branch, and immediately before the pipeline halts at `pre-merge`. A checkbox cannot express "after the next integration, before the halt", which is exactly the first of the two pipeline-vocabulary gaps issue #43 records and the design names in *Out of scope*. **Nothing mechanically detects 6b being skipped.** There is no CI check for it, no hook, and no artifact whose absence is noticed; the only thing standing between a skipped 6b and a silently version-less release is this paragraph being read and acted on. Treat a criteria pass reported without 6b as incomplete.

**What to run:** Task 4's Step 6a command, unchanged — the same program, re-fetching `origin/main` and re-comparing. It is idempotent and re-runnable.

**Why re-running it is not redundant.** 6a and 6b do not substitute for each other. 6b is the only check anywhere that notices a concurrent PR having landed `2.10.0` or `1.12.0` first, because two branches writing the byte-identical `"version"` line **auto-resolve on merge with no conflict** and produce no version change at all — the incident #43 records against PRs #35/#36/#37. A string-equality assertion against a literal target would not catch it either; what catches it is the `>` comparison against a re-fetched `origin/main`, on a tuple of integers rather than a string.

**If it fails:** the remediation the criterion prescribes is to re-target both versions upward and re-run. `WANT` is a **floor**, not an equality, so a higher version leaves the check green. Re-running Task 4's steps 1 and 2 after such a re-target is worthwhile — the version files are in scope for both.

**Where it must be reported:** in the `pre-merge` halt report, named as run with its output, or named as outstanding. Do not report the criteria pass as complete without it.

---

## Self-review

**Spec coverage.** Every file in the design's *Files the plan will touch* has a task: block 0 × 2 → Task 1; block 1 + block 2 × 2 → Task 2; both `plugin.json`s → Task 3. Every step of the design's `## Verification` is carried: steps 0–6a verbatim in Task 4, and step 6b as prose in *After the last task*. The design's *Out of scope* list is carried as Global Constraint 1. The design decides everything else — placement, wording, anchor lines, version targets — and no task re-opens any of it.

**Placeholders.** None. Every step is a runnable command with its expected output; the only text not spelled out is the three replacement passages, and that is deliberate — they are read from the design on disk by every program that needs them, which is the defect this whole change is about.

**Consistency.** The anchor constants (`AR_I = 29`, `DF_I = 276`, `WT_I = 270`), the block shape `[1, 1, 1]`, the block-to-file mapping, the post-edit lengths (278 / 272 / 89 / 89), the six-file scope list and the two version floors agree in every task and match the design. Each task's scope assertion is **cumulative** — Task 1 expects 2 changed paths, Task 2 expects 4, Task 3 and Task 4 expect all 6 — which is correct for tasks run in order and is itself an ordering check.

**Justified rather than assumed.** Three things this plan left implicit now carry their reason. Why only the three passages are read from the design while every other carried constant is typed here: those three are the only bytes whose drift is *silent*, and the rest — anchors, lengths, floors, the scope list, Task 4's copy of the design's commands — are executed against the real tree, so a stale one fails a step (*Architecture*). Why Task 4 is not a repeat of the per-task checks: each per-task verifier ran before the next task's edits, so only step 2 reconstructs all four markdown files over the *finished* tree, and only step 1 asserts the six-file scope equality there (*Task 4*). And the CR-free premise the line-based reads and `"\n".join(...) + "\n"` writes rest on is now a pinned, past-tense base fact with its command beside it and a recorded red run, not an assumption (*Base facts*).

**The programs were run, not just written.** Every apply and verify program in Tasks 1–4, and the design's seven verification commands spliced into Task 4, were executed in order in a throwaway `git clone` of this branch outside the repo while this plan was written: each task's verifier was run *before* its apply and printed `MISMATCH:` lines at `exit=1`, then again after and printed `OK` at `exit=0`. The clone was deleted afterwards. That establishes the programs run and discriminate; it establishes nothing about this checkout, where no edit has been applied.

**Compliance with the rules this change lands.** No `--stat` and no human-read output stands in for an assertion anywhere; every program collects all mismatches and prints them before exiting, so no assertion sits behind a short-circuit. Every step that consumes the computed merge base passes it to `git` as an `argv` element from `python3`/`subprocess`; **no command in this document uses a `$(git …)` substitution**, the form appearing only in this sentence and in Global Constraint 3, which quote it; and the `bf7676b`-pinned greps in *Base facts* take a literal SHA, which is not a computed ref. Every number stated in *Base facts* is printed by the command given beside it, in the past tense at `bf7676b`; the post-edit numbers are asserted by Tasks 2–4 rather than certified here.
