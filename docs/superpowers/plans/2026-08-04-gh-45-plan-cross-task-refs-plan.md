---
dev-flow:
  slug: gh-45-plan-cross-task-refs
  spec: docs/superpowers/specs/2026-08-03-gh-45-plan-cross-task-refs-design.md
---

# gh-45: carry a plan's cross-task resolver inside each `## Task N` section — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add one dev-flow Stage 2 rule (block 0) to both pipeline `SKILL.md` files and sharpen the `adversarial-review` plan-mode reviewer row (block 1) in both review `SKILL.md` files, then bump both plugin versions — so a generated plan's `## Task N` sections are self-sufficient under `scripts/task-brief`.

**Architecture:** Six edits across six files, sourced from the design's two plain fenced blocks (shape `[1, 1]`). Block 0 is inserted verbatim after a byte-identical anchor line in each of the two pipeline `SKILL.md`s; block 1 replaces the unique `| **plan** |` row in each of the two `adversarial-review/SKILL.md`s (a `scripts/check-sync.py`-checked pair); each plugin's `plugin.json` `version` bumps one minor past `origin/main`. There is no source code and no test framework — the design's mechanical/derived checks are the entire correctness surface.

**Tech Stack:** Markdown skill files, two small JSON manifests, and `python3` helper scripts (`scripts/design_blocks.py`, `scripts/check-sync.py`, `scripts/check-version-bump.py`); `git` and `claude plugin validate` for verification.

## Global Constraints

> **This plan dogfoods gh-45's own rule.** `scripts/task-brief` hands each implementer ONLY the text between its `## Task N` heading and the next `## Task` heading — so this `## Global Constraints` section is stripped and never reaches an implementer. Nothing here is load-bearing for any task: every task below re-states, inside its own body, every path, block, command, and clause it needs. Treat this section as orientation for a human reader only.

- **Repo:** a Claude Code plugin marketplace — Markdown plus a couple of `python3` scripts, **no test framework**. There is no red/green TDD; each task's "test" is the design's mechanical/derived check, run red before the edit and green after.
- **CWD:** every command in every task runs from the repo root `/Users/taylor/dev/claude-plugins`.
- **Design doc (authoritative source of the two edit blocks):** `/Users/taylor/dev/claude-plugins/docs/superpowers/specs/2026-08-03-gh-45-plan-cross-task-refs-design.md`. Its plain fenced blocks are shape `[1, 1]`: **block 0** is the pipeline rule bullet, **block 1** is the `adversarial-review` plan-mode row.
- **Never retype block 0 or block 1.** Obtain their exact bytes only via `read_blocks(DESIGN, [1, 1])[k][0]` (`k` = 0 or 1). Retyping either block is a defect.
- **Command discipline:** compute the merge base inside `python3`/`subprocess` and pass it to `git` as an `argv` element — never an inline `$(git …)`, which word-splits an empty ref into a different valid command.
- **Baseline (currently green, must stay green):** `claude plugin validate .` (exactly 8 expected missing-author warnings) and `python3 scripts/check-sync.py`.
- **Version bump:** both touched plugins bump their `version` minor segment **past `origin/main`** — expected `dev-flow` `2.13.0 → 2.14.0` and `dev-flow-worktree` `1.15.0 → 1.16.0`, re-derived from `origin/main` at apply time (a concurrent branch may have published these numbers first).

---

## Task 1: Insert the self-sufficiency rule (block 0) into both pipeline `SKILL.md` files

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md` (insert one line after the anchor)
- Modify: `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` (same insert, same anchor)

**Run every command in this task from the repo root `/Users/taylor/dev/claude-plugins`.** The `python3` blocks below resolve `sys.path.insert(0, "scripts")` and their `docs/…` and `plugins/…` paths relative to it; from any other directory they fail to resolve.

**Design blocks — read from source, never retype.** This task inserts **block 0**, read from the design doc at `/Users/taylor/dev/claude-plugins/docs/superpowers/specs/2026-08-03-gh-45-plan-cross-task-refs-design.md`. Read the referenced block verbatim from the design file at that path; never reconstruct or substitute it; if you cannot read the design file, stop and report. The scripts below do this via `read_blocks(DESIGN, [1, 1])[0][0]`; do not paste block text by hand.

**What the edit is:** block 0 becomes a new bullet immediately after this byte-identical anchor line (present exactly once in each file): the line containing `` Spawn a subagent to run `superpowers:writing-plans` against the design ``. The insertion is content-anchored (located by full-line exact match — the same predicate Task 3's sweep and the design use), never by line number; the applier asserts the anchor is unique before writing, and is idempotent (a re-run that finds block 0 already after the anchor makes no change).

- [x] **Step 1: Run the red check — confirm block 0 is NOT yet after the anchor.**

Run from the repo root. Expect `task1 conformance: FAIL` and `exit=1` (the demonstrated red form: the line after the anchor is not block 0, and the diff is empty).

```bash
python3 - <<'PY'
import subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-03-gh-45-plan-cross-task-refs-design.md"
b0 = read_blocks(DESIGN, [1, 1])[0][0]        # block 0, read from the design; never retyped
ANCHOR = "- Spawn a subagent to run `superpowers:writing-plans` against the design, producing `docs/superpowers/plans/YYYY-MM-DD-<slug>-plan.md` (front-matter links the spec)."
PIPELINE = ["plugins/dev-flow/skills/dev-flow/SKILL.md",
            "plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md"]

def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- %s" % (" ".join(args), r.stderr.strip() or "(no message)"))
    return r.stdout

base = git("merge-base", "origin/main", "HEAD").strip()
if not base:
    raise SystemExit("empty merge-base -- refusing to run a HEAD-relative check")

bad = []
for f in PIPELINE:
    lines = Path(f).read_text(encoding="utf-8").split("\n")
    at = [i for i, l in enumerate(lines) if l == ANCHOR]
    if len(at) != 1:
        bad.append("%s: anchor found %d times, want 1" % (f, len(at))); continue
    nxt = lines[at[0] + 1] if at[0] + 1 < len(lines) else "<EOF>"
    if nxt != b0:
        bad.append("%s: line after anchor != block 0" % f)
    out = git("diff", "--no-renames", base, "--", f).split("\n")
    add = [l[1:] for l in out if l.startswith("+") and not l.startswith("+++")]
    rem = [l[1:] for l in out if l.startswith("-") and not l.startswith("---")]
    if add != [b0] or rem != []:
        bad.append("%s: hunk != (add block 0, remove nothing); add=%r rem=%r" % (f, add, rem))
for why in bad:
    print("FAIL:", why)
print("task1 conformance:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

- [x] **Step 2: Apply the edit — insert block 0 after the anchor in both files.**

Run the applier. Expect one `inserted block 0 immediately after the anchor line` line per file.

```bash
python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-03-gh-45-plan-cross-task-refs-design.md"
b0 = read_blocks(DESIGN, [1, 1])[0][0]        # block 0, read from the design; never retyped
ANCHOR = "- Spawn a subagent to run `superpowers:writing-plans` against the design, producing `docs/superpowers/plans/YYYY-MM-DD-<slug>-plan.md` (front-matter links the spec)."
PIPELINE = ["plugins/dev-flow/skills/dev-flow/SKILL.md",
            "plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md"]

for f in PIPELINE:
    lines = Path(f).read_text(encoding="utf-8").split("\n")
    at = [i for i, l in enumerate(lines) if l == ANCHOR]
    if len(at) != 1:
        raise SystemExit("%s: anchor found %d times, want exactly 1" % (f, len(at)))
    i = at[0]
    if i + 1 < len(lines) and lines[i + 1] == b0:
        print("%s: block 0 already present after anchor; leaving as-is" % f)
        continue
    lines.insert(i + 1, b0)
    Path(f).write_text("\n".join(lines), encoding="utf-8")
    print("%s: inserted block 0 immediately after the anchor line" % f)
PY
```

- [x] **Step 3: Run the green check — re-run the Step 1 block verbatim.**

Re-run the exact `python3 - <<'PY' … PY` block from Step 1. Expect `task1 conformance: OK` and `exit=0`. This proves, per file: block 0 is the line immediately after the (unique) anchor, and the only change vs the merge base is that one added line — nothing removed, nothing else touched.

- [x] **Step 4: Commit.**

```bash
git add plugins/dev-flow/skills/dev-flow/SKILL.md \
        plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
git commit -m "gh-45: add task self-sufficiency rule to both pipeline SKILL.md files" \
           -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 2: Replace the plan-mode reviewer row (block 1) in both `adversarial-review/SKILL.md` files

**Files:**
- Modify: `plugins/dev-flow/skills/adversarial-review/SKILL.md` (replace the `| **plan** |` row)
- Modify: `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md` (same replacement — this pair is machine-checked by `scripts/check-sync.py`)

**Run every command in this task from the repo root `/Users/taylor/dev/claude-plugins`.** The `python3` blocks below resolve `sys.path.insert(0, "scripts")` and their `docs/…` and `plugins/…` paths relative to it; from any other directory they fail to resolve.

**Design blocks — read from source, never retype.** This task installs **block 1**, read from the design doc at `/Users/taylor/dev/claude-plugins/docs/superpowers/specs/2026-08-03-gh-45-plan-cross-task-refs-design.md`. Read the referenced block verbatim from the design file at that path; never reconstruct or substitute it; if you cannot read the design file, stop and report. The scripts below do this via `read_blocks(DESIGN, [1, 1])[1][0]`; do not paste block text by hand.

**What the edit is:** block 1 **replaces** the single existing line beginning `| **plan** |` (present exactly once in each file). The row is selected by content (`startswith("| **plan** |")`), never by line number; the applier asserts uniqueness before writing, and is idempotent (a re-run that finds the row already equal to block 1 makes no change). Block 1 itself begins `| **plan** |`, so the replaced row stays unique. Both files must stay byte-identical after this edit (`check-sync.py` canonicalizes `dev-flow-worktree` → `dev-flow`; block 1 names neither plugin, so canonicalization is a no-op).

- [x] **Step 1: Run the red check — confirm the plan row is NOT yet block 1.**

Run from the repo root. Expect `task2 conformance: FAIL` and `exit=1` (the plan row still equals the merge-base row, not block 1).

```bash
python3 - <<'PY'
import subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-03-gh-45-plan-cross-task-refs-design.md"
b1 = read_blocks(DESIGN, [1, 1])[1][0]        # block 1, read from the design; never retyped
ROW_PREFIX = "| **plan** |"
REVIEW = ["plugins/dev-flow/skills/adversarial-review/SKILL.md",
          "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md"]

def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- %s" % (" ".join(args), r.stderr.strip() or "(no message)"))
    return r.stdout

base = git("merge-base", "origin/main", "HEAD").strip()
if not base:
    raise SystemExit("empty merge-base -- refusing to run a HEAD-relative check")

def base_row(f):
    for l in git("show", "%s:%s" % (base, f)).split("\n"):
        if l.startswith(ROW_PREFIX):
            return l
    raise SystemExit("%s: no '%s' row at merge-base" % (f, ROW_PREFIX))

bad = []
for f in REVIEW:
    lines = Path(f).read_text(encoding="utf-8").split("\n")
    rows = [i for i, l in enumerate(lines) if l.startswith(ROW_PREFIX)]
    if len(rows) != 1:
        bad.append("%s: plan row found %d times, want 1" % (f, len(rows))); continue
    if lines[rows[0]] != b1:
        bad.append("%s: plan row != block 1" % f)
    out = git("diff", "--no-renames", base, "--", f).split("\n")
    add = [l[1:] for l in out if l.startswith("+") and not l.startswith("+++")]
    rem = [l[1:] for l in out if l.startswith("-") and not l.startswith("---")]
    if add != [b1] or rem != [base_row(f)]:
        bad.append("%s: hunk != (add block 1, remove base plan row); add=%r rem=%r" % (f, add, rem))
for why in bad:
    print("FAIL:", why)
print("task2 conformance:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

- [x] **Step 2: Apply the edit — replace the plan row with block 1 in both files.**

Run the applier. Expect one `replaced the plan-mode row with block 1` line per file.

```bash
python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-03-gh-45-plan-cross-task-refs-design.md"
b1 = read_blocks(DESIGN, [1, 1])[1][0]        # block 1, read from the design; never retyped
ROW_PREFIX = "| **plan** |"
REVIEW = ["plugins/dev-flow/skills/adversarial-review/SKILL.md",
          "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md"]

for f in REVIEW:
    lines = Path(f).read_text(encoding="utf-8").split("\n")
    rows = [i for i, l in enumerate(lines) if l.startswith(ROW_PREFIX)]
    if len(rows) != 1:
        raise SystemExit("%s: '%s' row found %d times, want exactly 1" % (f, ROW_PREFIX, len(rows)))
    i = rows[0]
    if lines[i] == b1:
        print("%s: plan-mode row already equals block 1; leaving as-is" % f)
        continue
    lines[i] = b1
    Path(f).write_text("\n".join(lines), encoding="utf-8")
    print("%s: replaced the plan-mode row with block 1" % f)
PY
```

- [x] **Step 3: Run the green check — re-run the Step 1 block verbatim.**

Re-run the exact `python3 - <<'PY' … PY` block from Step 1. Expect `task2 conformance: OK` and `exit=0`. Uniqueness plus equality proves the old row is gone (the removed-phrase check) and block 1 landed; the per-file hunk proves nothing else moved.

- [x] **Step 4: Run the pair-agreement and presence checks.**

`check-sync.py` proves the two review files still agree; the grep proves the load-bearing boundary phrase is present in each (one match per file). Expect `check-sync.py` to pass, and each `git grep -c` line to end in `:1`.

```bash
python3 scripts/check-sync.py
git grep -c 'with no plan-file path' -- \
  plugins/dev-flow/skills/adversarial-review/SKILL.md \
  plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
```

- [x] **Step 5: Commit.**

```bash
git add plugins/dev-flow/skills/adversarial-review/SKILL.md \
        plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
git commit -m "gh-45: sharpen adversarial-review plan-mode row with task-brief boundary fact" \
           -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 3: Bump both plugin versions and run the full verification sweep

**Files:**
- Modify: `plugins/dev-flow/.claude-plugin/plugin.json` (one `"version"` line)
- Modify: `plugins/dev-flow-worktree/.claude-plugin/plugin.json` (one `"version"` line)

**Run every command in this task from the repo root `/Users/taylor/dev/claude-plugins`.** The `python3` blocks, `scripts/…` helpers, and `git`/`claude` calls below resolve `sys.path.insert(0, "scripts")` and their `docs/…` and `plugins/…` paths relative to it; from any other directory they fail to resolve.

**Refresh `origin/main` first** so the version bump derives from and validates against the true remote tip: a straight-through run fetched it at branch creation, but a resumed Task 3 may see a stale ref, against which a number a concurrent branch has already published would still pass both the bumper and `check-version-bump.py`.

```bash
git fetch origin main
```

**Run this task only after Tasks 1 and 2 are committed** — the whole-change sweep below verifies all six files at once and will name any that is missing. This task reads no other task's text: the sweep re-derives everything from the tree and the design.

**Design blocks — read from source, never retype.** The sweep's design-conformance and scope checks re-read **blocks 0 and 1** from the design doc at `/Users/taylor/dev/claude-plugins/docs/superpowers/specs/2026-08-03-gh-45-plan-cross-task-refs-design.md`. Read the referenced blocks verbatim from the design file at that path; never reconstruct or substitute them; if you cannot read the design file, stop and report.

**What the edit is:** each `plugin.json`'s `version` bumps its **minor** segment by one, derived at apply time from that plugin's `origin/main` version (not hardcoded), so it is guaranteed to be past `origin/main` even if a concurrent branch already advanced it. Expected result: `dev-flow` `2.13.0 → 2.14.0`, `dev-flow-worktree` `1.15.0 → 1.16.0`. The bumper selects the unique `"version"` line by content, edits only that line (JSON is not round-tripped, so no other line reformats), and is idempotent.

- [x] **Step 1: Bump both versions.**

Run the bumper. Expect two `… -> …` lines, e.g. `plugins/dev-flow/.claude-plugin/plugin.json: 2.13.0 -> 2.14.0` and `plugins/dev-flow-worktree/.claude-plugin/plugin.json: 1.15.0 -> 1.16.0` (the exact numbers are whatever `origin/main + 1 minor` yields at apply time).

```bash
python3 - <<'PY'
import subprocess, json, re, sys
from pathlib import Path

def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- %s" % (" ".join(args), r.stderr.strip() or "(no message)"))
    return r.stdout

PLUGINS = ["plugins/dev-flow/.claude-plugin/plugin.json",
           "plugins/dev-flow-worktree/.claude-plugin/plugin.json"]

for f in PLUGINS:
    base_ver = json.loads(git("show", "origin/main:%s" % f))["version"]   # derive target from origin/main
    a, b, c = base_ver.split(".")
    new_ver = "%s.%d.%s" % (a, int(b) + 1, c)                             # bump the minor segment, past origin/main
    text = Path(f).read_text(encoding="utf-8")
    cur_ver = json.loads(text)["version"]
    if tuple(map(int, cur_ver.split("."))) >= tuple(map(int, new_ver.split("."))):   # never lower a version
        print("%s: already at %s (>= target %s); leaving" % (f, cur_ver, new_ver)); continue
    lines = text.split("\n")
    vlines = [i for i, l in enumerate(lines) if '"version"' in l]
    if len(vlines) != 1:
        raise SystemExit("%s: found %d '\"version\"' lines, want exactly 1" % (f, len(vlines)))
    i = vlines[0]
    new_line = re.sub(r'("version"\s*:\s*")[^"]*(")',
                      lambda m: m.group(1) + new_ver + m.group(2), lines[i])
    if new_line == lines[i]:
        raise SystemExit("%s: version substitution changed nothing" % f)
    lines[i] = new_line
    Path(f).write_text("\n".join(lines), encoding="utf-8")
    print("%s: %s -> %s" % (f, base_ver, new_ver))
PY
```

- [x] **Step 2: Sweep check A — block shape smoke-test.**

```bash
python3 scripts/design_blocks.py docs/superpowers/specs/2026-08-03-gh-45-plan-cross-task-refs-design.md
```

Expect `shape: [1, 1]`. (If the shape ever moved, the conformance and scope checks below would `SystemExit` inside `read_blocks` rather than mis-route an edit.)

**Steps 3–4 are the design's `## Verification` steps 1 and 2, inlined here so this task is self-contained** (the design's copies are indented under list items, and a quoted heredoc preserves leading spaces — inlined and dedented, they run as-is). Both re-read blocks 0 and 1 from the design via `read_blocks`; neither block is retyped.

- [x] **Step 3: Sweep check B — design-conformance (both blocks landed verbatim, old plan row gone).**

Run from the repo root. Block 0 must be the line immediately after the (unique) anchor in each pipeline file; block 1 must be the unique `| **plan** |` row in each review file (uniqueness + equality proves the base row is gone). Expect `design-conformance: OK` and `exit=0`.

```bash
python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
DESIGN = "docs/superpowers/specs/2026-08-03-gh-45-plan-cross-task-refs-design.md"
b0, b1 = (b[0] for b in read_blocks(DESIGN, [1, 1]))   # [1,1] guards the shape; each block is one line
ANCHOR = "- Spawn a subagent to run `superpowers:writing-plans` against the design, producing `docs/superpowers/plans/YYYY-MM-DD-<slug>-plan.md` (front-matter links the spec)."
PIPELINE = ["plugins/dev-flow/skills/dev-flow/SKILL.md",
            "plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md"]
REVIEW = ["plugins/dev-flow/skills/adversarial-review/SKILL.md",
          "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md"]
bad = []
for f in PIPELINE:                                    # block 0: line immediately after the anchor
    lines = Path(f).read_text(encoding="utf-8").split("\n")
    at = [i for i, l in enumerate(lines) if l == ANCHOR]
    if len(at) != 1:
        bad.append("%s: anchor found %d times, want 1" % (f, len(at))); continue
    nxt = lines[at[0] + 1] if at[0] + 1 < len(lines) else "<EOF>"
    if nxt != b0:
        bad.append("%s: line after anchor != rule bullet\n    want %r\n    got  %r" % (f, b0[:60], nxt[:60]))
for f in REVIEW:                                      # block 1: the unique plan-mode row
    lines = Path(f).read_text(encoding="utf-8").split("\n")
    rows = [i for i, l in enumerate(lines) if l.startswith("| **plan** |")]
    if len(rows) != 1:
        bad.append("%s: '| **plan** |' row found %d times, want 1" % (f, len(rows))); continue
    if lines[rows[0]] != b1:
        bad.append("%s: plan-mode row != design block 1\n    want %r\n    got  %r" % (f, b1[:60], lines[rows[0]][:60]))
for why in bad:
    print("MISMATCH:", why)
print("design-conformance:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

- [x] **Step 4: Sweep check C — scope + per-file hunks (nothing else changed).**

Run from the repo root. Asserts the changed set, excluding `docs/superpowers/`, is exactly the six files, and that each file's hunk vs the merge base is precisely its intended edit — block 0 added to each pipeline file with nothing removed; block 1 added and the base `| **plan** |` row removed in each review file; exactly one `"version"` line changed in each `plugin.json`. Expect `file scope + hunks: OK` and `exit=0`.

```bash
python3 - <<'PY'
import subprocess, sys
sys.path.insert(0, "scripts")
from design_blocks import read_blocks   # only to fetch the two blocks from the design
DESIGN = "docs/superpowers/specs/2026-08-03-gh-45-plan-cross-task-refs-design.md"
b0, b1 = (b[0] for b in read_blocks(DESIGN, [1, 1]))
PIPELINE = ["plugins/dev-flow/skills/dev-flow/SKILL.md",
            "plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md"]
REVIEW = ["plugins/dev-flow/skills/adversarial-review/SKILL.md",
          "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md"]
PLUGINJSON = ["plugins/dev-flow/.claude-plugin/plugin.json",
              "plugins/dev-flow-worktree/.claude-plugin/plugin.json"]
WANT = sorted(PIPELINE + REVIEW + PLUGINJSON)
def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout
base = git("merge-base", "origin/main", "HEAD").strip()
if not base:
    raise SystemExit("empty merge-base -- refusing to run a HEAD-relative scope check")
changed = sorted(p for p in git("diff", "--name-only", base, "--", ".", ":!docs/superpowers/").split("\n") if p)
fail = []
if changed != WANT:
    for p in sorted(set(changed) - set(WANT)): fail.append("unexpected file: " + p)
    for p in sorted(set(WANT) - set(changed)): fail.append("missing file:   " + p)
def hunk(f):                                          # added/removed content lines vs merge-base
    out = git("diff", "--no-renames", base, "--", f).split("\n")
    add = [l[1:] for l in out if l.startswith("+") and not l.startswith("+++")]
    rem = [l[1:] for l in out if l.startswith("-") and not l.startswith("---")]
    return add, rem
def baseline_plan_row(f):
    for l in git("show", "%s:%s" % (base, f)).split("\n"):
        if l.startswith("| **plan** |"): return l
    raise SystemExit("%s: no '| **plan** |' row at merge-base" % f)
for f in PIPELINE:
    add, rem = hunk(f)
    if add != [b0] or rem != []:
        fail.append("%s: hunk != (add block0, remove nothing); add=%r rem=%r" % (f, add, rem))
for f in REVIEW:
    add, rem = hunk(f)
    if add != [b1] or rem != [baseline_plan_row(f)]:
        fail.append("%s: hunk != (add block1, remove base plan-row); add=%r rem=%r" % (f, add, rem))
for f in PLUGINJSON:
    add, rem = hunk(f)
    if not (len(add) == 1 and len(rem) == 1 and '"version"' in add[0] and '"version"' in rem[0]):
        fail.append("%s: expected exactly one \"version\" line changed; add=%r rem=%r" % (f, add, rem))
for why in fail:
    print("SCOPE FAIL:", why)
print("file scope + hunks:", "FAIL" if fail else "OK")
sys.exit(1 if fail else 0)
PY
echo "exit=$?"
```

- [x] **Step 5: Sweep check D — pair agreement and boundary-phrase presence.**

```bash
python3 scripts/check-sync.py
git grep -c 'with no plan-file path' -- \
  plugins/dev-flow/skills/adversarial-review/SKILL.md \
  plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
```

Expect `check-sync.py` to pass and each `git grep -c` line to end in `:1`.

- [x] **Step 6: Sweep check E — marketplace still validates.**

```bash
claude plugin validate .
```

Expect exit 0 with exactly the 8 expected missing-author warnings (a PASS, not a regression).

- [x] **Step 7: Commit.**

```bash
git add plugins/dev-flow/.claude-plugin/plugin.json \
        plugins/dev-flow-worktree/.claude-plugin/plugin.json
git commit -m "gh-45: bump dev-flow and dev-flow-worktree minor versions" \
           -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

- [x] **Step 8: Sweep check F — both versions bumped past origin/main (runs after the Step 7 commit).**

`check-version-bump.py` reads each plugin's committed version via `git show HEAD:…plugin.json`, not the working tree, so it can only see the bump once it is committed — it must run *after* the Step 7 commit, not in the pre-commit sweep. (Run before committing, it compares `origin/main`'s version against the still-unbumped committed HEAD and reports FAIL; that FAIL is a staleness artifact of the uncommitted bump, not a real version collision.)

```bash
python3 scripts/check-version-bump.py origin/main
```

Expect it to pass (both touched plugins now ahead of `origin/main`).

**Expected end-state (whole change):** ignoring this run's own `docs/superpowers/` artifacts, the branch touches exactly these six files — proven by Step 4's scope assertion:

- `plugins/dev-flow/skills/dev-flow/SKILL.md`
- `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`
- `plugins/dev-flow/skills/adversarial-review/SKILL.md`
- `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md`
- `plugins/dev-flow/.claude-plugin/plugin.json`
- `plugins/dev-flow-worktree/.claude-plugin/plugin.json`
