---
dev-flow:
  slug: gh-31-34-glossary-contents
  spec: docs/superpowers/specs/2026-08-02-gh-31-34-glossary-contents-design.md
---

# gh-31 / gh-34: what `CONTEXT.md` should contain — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make two edits to one file — `CONTEXT.md` — adding `group-resolution agent` to the **Resolver** `_Avoid_:` line (#31) and inserting a four-entry `### Topology` section after the **Slug** definition (#34), taking the glossary from 67 to 81 lines, 17 to 21 entries, 4 to 5 sections, and 6 to 7 avoided names.

**Architecture:** Both replacement texts already exist, complete and literal, as the design's **two plain fenced blocks** — fences with *no* info string; every other fence in that document is tagged ` ```bash `, ` ```python ` or ` ```text `. Block 0 is 1 line and replaces the **Resolver** `_Avoid_:` line; block 1 is 14 lines and is inserted directly after the **Slug** definition. The blocks are **never retyped**: one applier reads both through `read_blocks` from `scripts/design_blocks.py`, locates each site by **anchor text** rather than by line index, and refuses to write if an anchor is missing or not unique. The result is then proved by a total reconstruction — the design's criterion 6 asserts the post-change file is *exactly* the pre-change file with block 0 substituted and block 1 inserted, which is simultaneously the proof that nothing else in the file moved.

**Tech Stack:** Markdown, `python3` (stdlib only: `sys`, `difflib`, `subprocess`, `pathlib`), `git`, `claude` CLI. No build, no test framework (design **A6**) — the design's eight success criteria are the entire verification surface.

## Global Constraints

Every task's requirements implicitly include this section.

- **Working directory (absolute, always):** `/Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ab7c57714912b7b5e`. Branch `tayl0r/gh-31-34-glossary-contents`, already checked out. **Address git as `git -C <that path>` and write every path in full; never rely on inherited cwd** — agent threads reset cwd between calls. **Do not create a git worktree; do not switch branches.**
- **Authorized file set — nothing else may be created, modified, or deleted:**
  - `CONTEXT.md` — the only file whose content this change alters.
  - `docs/superpowers/plans/2026-08-02-gh-31-34-glossary-contents-plan.md` (this file — **checkbox ticks only**).
- **Hard-excluded — a step that appears to need one of these is a BLOCKER, not a judgment call. Stop and report; do not work around it.** `CLAUDE.md`, anything under `scripts/` (including `design_blocks.py`, which is **used** and never modified, and `check-sync.py`), anything under `plugins/` (both plugins, every file), `docs/adr/`, `docs/agents/`, `.claude-plugin/`, both `README.md`s, and **every pre-existing file under `docs/superpowers/`** — meaning the prior records, plus this change's own design doc, which is read-only input. Concurrent agents own several of these. (Design *Out of scope*.)
- **No version bump.** `CONTEXT.md` sits at the repo root, outside `plugins/`, so it enters no version-keyed install cache and `CLAUDE.md`'s bump rule — which is scoped to `plugins/<name>/.claude-plugin/plugin.json` and justified by that cache — does not apply (design **A2**; precedent `4049d23`, `c8b2182`). **Editing any `plugin.json` is a scope violation**, not a helpful extra.
- **The design doc is read-only input, and every snippet that reads it re-asserts that.** `docs/superpowers/specs/2026-08-02-gh-31-34-glossary-contents-design.md` must end this work byte-identical to how it started. Expected blob hash (`git -C <root> hash-object <design path>`): `f9d44e2aea5d9deab6e4118fafea624ba60f44db`, committed at `919a3d3`. Task 1 Step 1 checks it, and **both snippets that call `read_blocks` — Task 1 Step 3's applier and the conformance check run at Steps 2 and 4 — re-check it immediately before the call.** This plan is resumable across sessions: a design edited in the gap between Step 1 and Step 3 would otherwise be spliced in and then *blessed* by a check that read the same edited file, and `read_blocks`'s shape guard cannot see a reword that preserves line counts. A mismatch anywhere is **HALT and report** — do not proceed and do not "fix" the design. **Any snippet added to this plan that reads the design inherits this rule.** The redundancy at Step 2 (seconds after Step 1) is the price of Steps 2 and 4 running the identical script; do not "simplify" it away. If the design is legitimately rewritten before execution, recompute the hash with `git hash-object` — never retype it — and update every literal: `grep -c f9d44e2aea5d9deab6e4118fafea624ba60f44db` over this plan must return `4`.
- **Never retype the design's blocks — no exceptions, in any task.** Every write of block 0 or block 1 goes through `read_blocks(<design>, [1, 14])`, which re-reads them from the design **on disk**. No step below asks you to reproduce block text from what you have read; if one appears to, you have misread it. A hand-typed or model-paraphrased copy is a defect even if it looks identical. (`CLAUDE.md`'s design-block rule; design criterion 6.)
- **Both edits are located by anchor text, never by line index.** The line numbers quoted throughout (15, 53) are *descriptive*, and every applier and check asserts them rather than trusting them. A text-matched edit that cannot find its anchor fails without writing; a line-indexed one corrupts the wrong line and leaves criterion 6 to discover it afterwards (design **A1**).
- **`scripts/design_blocks.py` is imported, never edited.** Call it as `sys.path.insert(0, f"{ROOT}/scripts")` then `from design_blocks import read_blocks` — with the **absolute** scripts directory, so the check has no cwd dependency. **If a step seems to need its own inline fenced-block reader, stop and report — do not write one.**
- **Do not commit, push, open a PR, merge, close an issue, or invoke a review skill.** The pipeline owns every one of those (design **A5**). Criterion 8 is written to read `BASE` → *working tree* precisely so it is meaningful on an uncommitted implementation.
- **`BASE` is always computed, never hardcoded:** `BASE=$(git -C <root> merge-base origin/main HEAD)`. It resolved to `b4b5d1ca5d19b36e992f9ff1f3d2ff7a1b989037` when this plan was written. It is the **merge-base**, not `origin/main`'s tip, and **no `git fetch` is required**: a concurrent PR landing on `main` advances the tip but not the merge-base, so freshening the remote-tracking ref cannot change what the reconstruction compares against.
- **No new files anywhere, including temp files inside the repo.** Every Python snippet below runs as a heredoc piped to `python3 -`, so nothing is written to disk. Importing `design_blocks` makes CPython write `scripts/__pycache__/`; that is expected and is already ignored by the repo's `.gitignore` (verified: `git check-ignore -v scripts/__pycache__` → `.gitignore:2:__pycache__/`). **Leave it alone — do not delete it, do not stage it, never use `git add -A` or `git add .`.**
- **`python3 - <<'PY'` heredoc fences in this plan are unindented on purpose.** A heredoc indented under a list item is an `IndentationError`. Copy each fenced block as written; do not re-indent it to line up with its bullet.
- **`git grep` reads the working tree** for tracked files, so criteria 1, 2, 5 and 8 are meaningful before any commit exists. Bare `grep` is used only where the design uses it, and only for whole-line or count assertions whose output was measured in this checkout.
- **`claude plugin validate .` exiting 0 with exactly 8 `No author information provided` warnings is a PASS** (design **A4**, `CLAUDE.md`). Warnings are not failures. Do not add author fields to silence them.
- **Nothing about this change touches shipped text.** Neither `scripts/check-sync.py` nor `claude plugin validate .` reads `CONTEXT.md` (design **A3**, verified: `grep -n 'CONTEXT' scripts/check-sync.py` → no output, exit 1). They prove the change broke nothing; **criterion 6 is the only mechanical guard that proves it is right.**

---

## File Structure

| Path (repo-relative) | Change |
|---|---|
| `CONTEXT.md` | Line 15 replaced by design block 0 (1 line); design block 1 (14 lines) inserted after line 53. 67 → **81** lines, 17 → **21** entries, 4 → **5** sections, 3 `_Avoid_:` lines (unchanged) carrying 6 → **7** names. The **Seam** entry's `_Avoid_: boundary` moves from line 67 to line 81 and stays the file's last line. |
| `docs/superpowers/plans/2026-08-02-gh-31-34-glossary-contents-plan.md` | This file. Checkbox ticks only. |

No file is created. No file is deleted. No `plugin.json` is edited. No `check-sync.py` exception is added — `CONTEXT.md` is not enrolled in any mirror pair.

Two regions of `CONTEXT.md` are called out because they must **not** move (design *Out of scope*, last bullet):

- The **Provenance** entry keeps its `fan-out` **byte-identical** at line 27. The new **Fan-out** entry supplies the definition that was missing; no byte of **Provenance** needs to change, and none may.
- The **Resolver** *definition* line (14) is unchanged. Only its `_Avoid_:` line (15) is replaced.

## Success-criteria map

All eight criteria come from the design's *Success criteria* section. Every one has an executable step below.

| # | Criterion | Owned by |
|---|---|---|
| 1 | The removed `_Avoid_:` line is gone from `CONTEXT.md` | **Task 2, Step 1** |
| 2 | No rejected name (`nested`, `depth-2`, `stage subagent`) entered the glossary | **Task 2, Step 2** |
| 3 | The three `_Avoid_:` lines read exactly, at 11 / 15 / 81 | **Task 2, Step 3** |
| 4 | Structure: 81 lines, 21 entries, 5 sections, 3 `_Avoid_:` lines | **Task 2, Step 4** |
| 5 | New entries present at their pinned lines; **Provenance** untouched | **Task 2, Step 5** |
| 6 | **Design conformance** — total reconstruction from the design's blocks read off disk | **Task 1, Step 4** (demonstrated red at **Task 1, Step 2**) |
| 7 | `check-sync.py` and `claude plugin validate .` still pass | **Task 2, Steps 6–7** |
| 8 | Scope — only `CONTEXT.md` and `docs/superpowers/` paths changed | **Task 2, Step 8** |

Criteria 3, 4 and 5 are deliberately **retyped** from the design's *rulings*, not read from its blocks; criterion 6 is read from the blocks. That asymmetry is the design's own (criterion 6's closing paragraph): a block silently reworded in the design would still pass criterion 6, and criteria 3–5 are what fail loudly in that case. **Do not "simplify" criteria 3–5 into re-reads of the blocks** — that would delete the only independent pin this change has.

## Task order and dependencies

- **Task 1 must complete before Task 2.** This is the ordering constraint the design makes explicit: **criterion 6 reconstructs the file from *both* blocks at once, so it can only run after both edits land.** There is no intermediate state in which it is meaningful — after edit 0 alone it fails on the missing section, after edit 1 alone it fails on the `_Avoid_:` line. Task 1 therefore applies both edits in one step and verifies them in the next.
- **There are exactly two tasks, and the boundary is writer/verifier.** Task 1 is the only task that writes; Task 2 is the only task that verifies, and it runs every criterion the writer's own criterion 6 cannot vouch for — 1–5, retyped from the design's *rulings* rather than read from its blocks, plus 7 and 8. Its eight check steps are all read-only greps, counts and tool invocations against the one artifact Task 1 produced, under one dependency. A third task would split them across a second briefing that buys no independence the writer/verifier boundary does not already buy, and would strand the Step 9 verdict in an agent that never watched criteria 1–5 run.
- **No task commits.** The working tree at the end of Task 2 is the deliverable; the pipeline commits it.
- Execution is complete when zero `- [ ]` boxes remain unchecked.

---

## Task 1: Apply both edits to `CONTEXT.md`

**Files:**
- Modify: `CONTEXT.md` — line 15 replaced, 14 lines inserted after line 53
- Read-only input: `docs/superpowers/specs/2026-08-02-gh-31-34-glossary-contents-design.md`
- Imported, never modified: `scripts/design_blocks.py`
- Test: none — this repo has no test framework (design **A6**)

**Interfaces:**
- Consumes: `read_blocks(design_path, shape) -> list[list[str]]` from `scripts/design_blocks.py`, imported as `sys.path.insert(0, f"{ROOT}/scripts")` then `from design_blocks import read_blocks`. It returns the design's plain (untagged) fenced blocks in document order, as lists of lines, **after** checking `[len(b) for b in blocks] == list(shape)`; on mismatch it raises `SystemExit` (exit 1, one line on stderr) rather than returning. The shape for this design is **`[1, 14]`**: block 0 is the 1-line replacement `_Avoid_:` line, block 1 the 14-line `### Topology` section whose **first line is empty** and which has **no** trailing blank line.
- Produces: `CONTEXT.md` at 81 lines, which Task 2 verifies. Nothing later depends on the applier itself.

- [ ] **Step 1: Pre-flight — confirm the tree, the design, and both anchors**

This is the design's *The edit* pre-flight, which **runs before any write**. Run each command separately.

```bash
git -C /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ab7c57714912b7b5e status --porcelain
git -C /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ab7c57714912b7b5e hash-object docs/superpowers/specs/2026-08-02-gh-31-34-glossary-contents-design.md
python3 /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ab7c57714912b7b5e/scripts/design_blocks.py /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ab7c57714912b7b5e/docs/superpowers/specs/2026-08-02-gh-31-34-glossary-contents-design.md
git -C /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ab7c57714912b7b5e merge-base origin/main HEAD
```

Expected:
- `status --porcelain` prints nothing except, possibly, this plan file — `docs/superpowers/plans/2026-08-02-gh-31-34-glossary-contents-plan.md`, in **either** state: `??` if the pipeline has not committed it yet, or ` M` once it is committed and checkboxes are being ticked. Both are expected; neither is a halt. **Any other modified or untracked path → HALT and report**: the tree is not in the state this plan was written against. In particular `CONTEXT.md` must not already be modified, and the design doc must not appear at all — a modified design contradicts the hash pin.
- `hash-object` prints `f9d44e2aea5d9deab6e4118fafea624ba60f44db`. **Any other value → HALT and report "design doc modified".**
- `design_blocks.py` prints `shape: [1, 14]` followed by one preview line per block. **Any other shape → HALT and report** — every index in this plan is then stale, and per the design a third plain block would shift them all.
- `merge-base` prints a 40-hex commit id and exits 0 — it was `b4b5d1ca5d19b36e992f9ff1f3d2ff7a1b989037` when this plan was written. **A different value is not a halt** (a rebase onto a `main` that left `CONTEXT.md` alone moves it legitimately; the conformance check's `assert len(old) == 67` is what rules on that). **A failure — `fatal: Not a valid object name` — is a HALT and report:** the ref every later `BASE` is computed from does not resolve in this checkout, and the conformance check and criterion 8 would both die inside `subprocess.run(..., check=True)` before reading anything.

Then the two anchors, from the working directory. These are the design's own pre-flight commands, verbatim:

```bash
cd /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ab7c57714912b7b5e
wc -l < CONTEXT.md
grep -n '^_Avoid_: group agent, judge, arbiter$' CONTEXT.md
grep -n '^The short, opaque, immutable identifier for one pipeline run,' CONTEXT.md
```

Expected, measured in this checkout at `b4b5d1c`:
- `wc -l` prints `67` (BSD `wc` pads with spaces; read the number, not the layout).
- the second command prints exactly one line: `15:_Avoid_: group agent, judge, arbiter`
- the third prints exactly one line beginning `53:The short, opaque, immutable identifier for one pipeline run,`

**Any other result — no hit, more than one hit, a different line number — means the file has drifted from the base this design measured: STOP and re-derive, do not edit.** Do not adjust the numbers to match what you see.

- [ ] **Step 2: Run the design-conformance check and watch it FAIL (red)**

Run this **before** touching `CONTEXT.md`. It is the design's criterion 6 verbatim, with `<wd, absolute>` substituted. Running it red first is what shows the check discriminates, rather than merely asserting that it does. **The fence is unindented on purpose.**

```bash
python3 - <<'PY'
import difflib, subprocess, sys

ROOT = "/Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ab7c57714912b7b5e"
sys.path.insert(0, f"{ROOT}/scripts")     # absolute: this check has no other cwd dependency
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-02-gh-31-34-glossary-contents-design.md"
DESIGN_SHA = "f9d44e2aea5d9deab6e4118fafea624ba60f44db"
got = subprocess.run(["git", "-C", ROOT, "hash-object", DESIGN],
                     capture_output=True, text=True, check=True).stdout.strip()
if got != DESIGN_SHA:
    raise SystemExit("design doc is %s, want %s; HALT and report" % (got, DESIGN_SHA))
BASE = subprocess.run(["git", "-C", ROOT, "merge-base", "origin/main", "HEAD"],
                      capture_output=True, text=True, check=True).stdout.strip()

def split_lines(text):            # check-sync.py's rule; agrees with `wc -l` when the file ends in a newline
    out = text.split("\n")
    if out and out[-1] == "":
        out.pop()
    return out

old = split_lines(subprocess.run(["git", "-C", ROOT, "show", f"{BASE}:CONTEXT.md"],
                                 capture_output=True, text=True, check=True).stdout)
new = split_lines(open(f"{ROOT}/CONTEXT.md", encoding="utf-8").read())
blocks = read_blocks(f"{ROOT}/{DESIGN}", [1, 14])

assert len(old) == 67, len(old)
assert old[14] == "_Avoid_: group agent, judge, arbiter", old[14]
assert old[52].startswith("The short, opaque, immutable identifier"), old[52]
want = old[:14] + blocks[0] + old[15:53] + blocks[1] + old[53:]
assert new == want, "\n".join(difflib.unified_diff(want, new, "want", "got", lineterm=""))
assert len(new) == 81, len(new)
print("design-conformance: OK")
PY
echo "exit=$?"
```

Expected, **measured** against the unedited file: `exit=1`, and an `AssertionError` on the `assert new == want` line whose message is a unified diff with **exactly two hunks** — one at `@@ -12,7 +12,7 @@` showing the wanted `_Avoid_:` line against the current one, and one at `@@ -52,20 +52,6 @@` showing the 14 wanted `### Topology` lines as absent. **`design-conformance: OK` must not appear.**

If instead it fails on one of the three earlier asserts (`len(old)`, `old[14]`, `old[52]`), the branch's base is not what this plan measured → **HALT and report**. If it exits with `design doc is …`, the design changed since Step 1 → **HALT and report**; if with `design code-block shape is …`, the design's blocks moved → **HALT and report**. If it prints `design-conformance: OK`, `CONTEXT.md` was edited before this step ran → **HALT and report**; the check has not been shown to discriminate.

- [ ] **Step 3: Apply both edits, reading both blocks from the design**

One applier, both edits, **no replacement text retyped**. It reads block 0 and block 1 through `read_blocks`, locates each site by **anchor text**, asserts both anchors are unique and where the design says they are, and only then writes. The two strings it does type are *pre-edit* anchors — a typo in either makes it refuse to write rather than misroute the edit. **The fence is unindented on purpose.**

```bash
python3 - <<'PY'
import subprocess, sys
from pathlib import Path

ROOT = "/Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ab7c57714912b7b5e"
sys.path.insert(0, f"{ROOT}/scripts")
from design_blocks import read_blocks

DESIGN = f"{ROOT}/docs/superpowers/specs/2026-08-02-gh-31-34-glossary-contents-design.md"
TARGET = f"{ROOT}/CONTEXT.md"
OLD_AVOID = "_Avoid_: group agent, judge, arbiter"
SLUG_PREFIX = "The short, opaque, immutable identifier for one pipeline run,"

DESIGN_SHA = "f9d44e2aea5d9deab6e4118fafea624ba60f44db"
got = subprocess.run(["git", "-C", ROOT, "hash-object", DESIGN],
                     capture_output=True, text=True, check=True).stdout.strip()
if got != DESIGN_SHA:
    raise SystemExit("design doc is %s, want %s; HALT and report" % (got, DESIGN_SHA))

blocks = read_blocks(DESIGN, [1, 14])

text = Path(TARGET).read_text(encoding="utf-8")
lines = text.split("\n")
tail = ""
if lines and lines[-1] == "":            # round-trip the final newline exactly
    lines.pop()
    tail = "\n"

if len(lines) != 67:
    raise SystemExit("CONTEXT.md is %d lines, want 67; stop and re-derive" % len(lines))
at_avoid = [i for i, l in enumerate(lines) if l == OLD_AVOID]
if at_avoid != [14]:
    raise SystemExit("the Resolver _Avoid_ line is at 0-based %s, want exactly [14]"
                     " (line 15); stop and re-derive" % at_avoid)
at_slug = [i for i, l in enumerate(lines) if l.startswith(SLUG_PREFIX)]
if at_slug != [52]:
    raise SystemExit("the Slug definition is at 0-based %s, want exactly [52]"
                     " (line 53); stop and re-derive" % at_slug)

lines[14:15] = blocks[0]                 # block 0 replaces the Resolver _Avoid_ line
lines[53:53] = blocks[1]                 # block 1 goes directly after the Slug definition
Path(TARGET).write_text("\n".join(lines) + tail, encoding="utf-8")
print("CONTEXT.md: block 0 replaced line 15, block 1 inserted after line 53 -> %d lines" % len(lines))
PY
echo "exit=$?"
```

Expected output, exactly:

```text
CONTEXT.md: block 0 replaced line 15, block 1 inserted after line 53 -> 81 lines
exit=0
```

Block 0 is one line, so replacing line 15 shifts no index and the **Slug** anchor is still at 0-based 52 when the insertion runs — which is why the two edits are safe in one pass and why the applier locates both sites before mutating either.

The applier is deliberately single-shot: run it twice and the second run exits 1 with `CONTEXT.md is 81 lines, want 67`. That is correct behaviour, not a bug — if you see it, the edit already landed; go to Step 4 rather than re-applying. **Do not hand-edit around a refusal, and do not paste block text into an `Edit` call to "finish the job".** If the applier refuses for any reason, **HALT and report its message verbatim.**

- [ ] **Step 4: Re-run the design-conformance check and watch it PASS (green) — success criterion 6**

Run **the identical script from Step 2 again** — same text, unchanged. Do not edit it, do not substitute an equivalent of your own: its whole point is that it re-reads the design's blocks from disk rather than trusting any transcription.

Expected output, exactly:

```text
design-conformance: OK
exit=0
```

Red in Step 2, green here, with nothing between them but the applier. Because `assert new == want` reconstructs **all 81 lines**, this single assertion also discharges "nothing else in the file moved" — including that **Provenance** at line 27 and the **Resolver** definition at line 14 are byte-identical to base. There is no separate check for those and none is needed.

If the check still fails, **read which failure fired before doing anything** — three of the four must not be retried.

- A `SystemExit` whose message begins `design doc is ` (the hash pin) or `design code-block shape is ` — **the design changed under this plan. HALT and report.** Do **not** restore and re-run: the applier would splice the changed design and this check, reading the same changed file, would then agree with it. That is the drift the pin exists to catch, and retrying is what would hide it.
- An `AssertionError` on `len(old)`, `old[14]` or `old[52]` — the branch's base moved (a rebase). **HALT and report**; every line number this plan is written against is stale.
- An `AssertionError` on `assert new == want` — this one, and only this one, means the write is bad. Restore `CONTEXT.md` from this branch's committed state and re-run Step 3's applier **once**:

```bash
git -C /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ab7c57714912b7b5e checkout HEAD -- CONTEXT.md
```

The source is `HEAD`, not `BASE`, and it is a **ref rather than a value** — nothing is hardcoded and nothing needs computing, so the Global Constraints' "`BASE` is always computed" rule is not in tension with it: this is not a `BASE` operation. The working-tree edit was made against this branch's committed `CONTEXT.md`, so `HEAD` is exactly what undoes it. Restoring to `BASE` would be wrong twice over — a literal SHA cannot survive a rebase at all, and even recomputed it would silently revert a `main` that had changed `CONTEXT.md` and leave the revert **staged** (`git status --porcelain` → `M  CONTEXT.md`). `git restore CONTEXT.md` is rejected for a different reason: it restores from the index, so a file staged by mistake would be "restored" to the bad copy. The pathspec form (`-- CONTEXT.md`) touches one path and does not switch branches, and it overwrites the working tree unconditionally, so it works on a half-written file.

**If the check fails again after one restore-and-re-apply, HALT and report both failures.** The applier is deterministic; a second identical failure is not a transient, and re-running it a third time is a loop, not a recovery.

- [ ] **Step 5: Report — do not commit**

Leave the change in the working tree. Report that Task 1 is complete, quoting the Step 2 red result (two diff hunks, `exit=1`), the Step 3 applier line, and the Step 4 green result. **Do not commit, do not push, do not open a PR, do not close an issue, do not invoke a review skill.**

---

## Task 2: Independent verification — criteria 1–5 and 7–8

**Depends on:** Task 1, complete and green.

**Files:** none created or modified. This task only reads and runs commands.

**Interfaces:**
- Consumes: the edited `CONTEXT.md` from Task 1, in the working tree — **uncommitted is expected and fine**.
- Produces: the final verdict on all eight of the design's success criteria.

**Why this task exists separately from criterion 6.** Every expectation in Steps 1–5 is retyped from the design's *rulings* — which terms are defined, which names are avoided, how many of each — rather than read from the design's blocks. Criterion 6 draws its expected text from the same document a rewrite of the blocks would have changed, so a block reworded inside the design (at the same line count) passes it. These five are what fail loudly in that case. Steps 6–8 sit in this task rather than a third one because they read the same artifact under the same single dependency, write nothing, and feed the same verdict: Step 9 covers all eight criteria, so only the agent that watched all eight run can record it honestly. Run all eight checks and report each one's actual output; do not stop at the first green.

- [ ] **Step 1: Criterion 1 — the removed line is gone**

```bash
git -C /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ab7c57714912b7b5e grep -n '^_Avoid_: group agent, judge, arbiter$' -- CONTEXT.md ; echo "exit=$?"
```

Expected: **no output**, `exit=1`. This is the grep-for-what-you-removed discipline `CLAUDE.md` requires of mirrored pairs, adopted here on its own merits: `CONTEXT.md` is not a mirrored pair, and nothing else in the repo would notice a stale copy of the old line.

The pathspec `-- CONTEXT.md` is required and must not be widened: the old line legitimately survives in `docs/superpowers/` records and in this change's own design doc.

- [ ] **Step 2: Criterion 2 — no rejected name entered the glossary**

```bash
git -C /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ab7c57714912b7b5e grep -in -e 'nested' -e 'depth-2' -e 'stage subagent' -- CONTEXT.md ; echo "exit=$?"
```

Expected: **no output**, `exit=1`. These are the three `_Avoid_:` names issue #34 proposed and the design rejected — all three failed the `_Avoid_:` gate as antonyms or as the name of a deleted construct. If any appears, the implementation did not use the design's blocks → **HALT and report**.

The pathspec is again required: all three names legitimately appear in `docs/adr/`, in `docs/superpowers/` records, and in shipped text under `plugins/` — none of which this change touches.

- [ ] **Step 3: Criterion 3 — the three `_Avoid_:` lines read exactly**

```bash
cd /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ab7c57714912b7b5e
grep -n '^_Avoid_:' CONTEXT.md
```

Expected — exactly these three lines, in this order, and no others:

```text
11:_Avoid_: finder, first-pass reviewer
15:_Avoid_: group agent, group-resolution agent, judge, arbiter
81:_Avoid_: boundary
```

Line 15 is issue #31's whole ruling, with the new name placed **second** so the two `group`-prefixed forms sit together. Line 81 is the **Seam** entry's avoid line, which moves from 67 to 81 and stays the file's last line. Line 11 must be untouched.

- [ ] **Step 4: Criterion 4 — structure**

```bash
cd /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ab7c57714912b7b5e
wc -l < CONTEXT.md
grep -c '^\*\*' CONTEXT.md
grep -c '^### ' CONTEXT.md
grep -c '^_Avoid_:' CONTEXT.md
```

Expected, in order: `81`, `21`, `5`, `3`. (BSD `wc` pads its number with spaces; read the number, not the layout. Measured at base these were `67`, `17`, `4`, `3`.)

`wc -l` and criterion 6's `len(new)` are **not redundant** — `split_lines` treats a missing final newline as invisible and `wc -l` does not, so the two together are what pin it. Neither may be dropped.

- [ ] **Step 5: Criterion 5 — the new entries are present and Provenance is untouched**

```bash
cd /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ab7c57714912b7b5e
git grep -c -i 'orchestrator' -- CONTEXT.md
git grep -n '^### Topology$' -- CONTEXT.md
git grep -n 'Evidence of fan-out and tier conformance' -- CONTEXT.md
grep -nE '^\*\*(Orchestrator|Leaf|Fan-out|Flat topology)\*\*:$' CONTEXT.md
```

Expected:
- the first prints exactly `CONTEXT.md:3` — three lines mention `orchestrator`, case-insensitively. (`git grep -c` counts matching *lines* and prefixes the filename even for a single path.)
- the second prints exactly one line: `CONTEXT.md:55:### Topology`
- the third prints exactly one line beginning `CONTEXT.md:27:` — the **Provenance** entry, still at line 27 and still byte-identical. The new **Fan-out** entry supplies the definition that line was missing; **no byte of Provenance moves.**
- the fourth prints exactly these four lines:

```text
57:**Orchestrator**:
60:**Leaf**:
63:**Fan-out**:
66:**Flat topology**:
```

Those line numbers fall out of the design's arithmetic: block 1's 14 lines occupy 54–67, so its blank first line is 54, `### Topology` lands at 55, and the four headwords at 57 / 60 / 63 / 66. All four were measured against the reconstructed file while this plan was written.

- [ ] **Step 6: Criterion 7a — `check-sync.py`**

```bash
python3 /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ab7c57714912b7b5e/scripts/check-sync.py ; echo "exit=$?"
```

Expected: `exit=0`, with the final line reading exactly:

```text
check-sync: all checks passed
```

**The per-pair summary counts are deliberately not pinned.** The `mirror pair "adversarial-review" ... OK (N lines, 1 declared exception)` line describes hard-excluded files that concurrent changes own; a legitimate edit there would change `N` for a reason that has nothing to do with this change. Assert the exit status and the final line, not the counts.

This script reads nothing in `CONTEXT.md` (design **A3**, verified) and will pass identically before and after the edit, having proved nothing about it. It is here to prove the change broke nothing. **Never edit `scripts/check-sync.py` — it is hard-excluded and concurrently owned.** If it fails, **HALT and report**; the failure is not this change's to fix.

- [ ] **Step 7: Criterion 7b — `claude plugin validate .`**

```bash
cd /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ab7c57714912b7b5e
claude plugin validate . ; echo "exit=$?"
```

Expected: `exit=0`, `⚠ Found 8 warnings:`, eight `author: No author information provided…` lines, and `✔ Validation passed with warnings`. **This is a PASS** (design **A4**, `CLAUDE.md`). Zero *errors* is the requirement; the 8 warnings are expected and must not be "fixed" by adding author fields. Any error, a different warning count, or a non-zero exit → **HALT and report**.

- [ ] **Step 8: Criterion 8 — file-level scope**

First look at it, then assert it. `BASE` is computed, never hardcoded, and the diff runs `BASE` → **working tree** (not `BASE..HEAD`), because `..HEAD` sees committed work only and would pass vacuously on the uncommitted implementation criterion 6 read.

```bash
cd /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ab7c57714912b7b5e
git diff --stat "$(git merge-base origin/main HEAD)"
git status --porcelain
```

Between them these must name **only** `CONTEXT.md` and paths under `docs/superpowers/`. Expected in practice: `CONTEXT.md`, this change's design doc (committed on this branch after `BASE`), and this plan file. **`scripts/__pycache__/` must not appear** — it is gitignored; if it does, report it and leave it exactly as found rather than deleting or unstaging it.

Never read `--stat`'s bar or leading integer literally: that integer is insertions *plus* deletions, and its column scales with terminal width. Compare the file *set*. Now assert it mechanically. **The fence is unindented on purpose.**

```bash
python3 - <<'PY'
import subprocess

ROOT = "/Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ab7c57714912b7b5e"
BASE = subprocess.run(["git", "-C", ROOT, "merge-base", "origin/main", "HEAD"],
                      capture_output=True, text=True, check=True).stdout.strip()
print("BASE =", BASE)

diff = subprocess.run(["git", "-C", ROOT, "diff", "--name-only", BASE],
                      capture_output=True, text=True, check=True).stdout.splitlines()
status = subprocess.run(["git", "-C", ROOT, "status", "--porcelain"],
                        capture_output=True, text=True, check=True).stdout.splitlines()
paths = {p for p in diff if p} | {l[3:].strip() for l in status if l.strip()}

bad = sorted(p for p in paths if p != "CONTEXT.md" and not p.startswith("docs/superpowers/"))
for p in sorted(paths):
    print("  in scope:", p)
assert "CONTEXT.md" in paths, "CONTEXT.md is not in the diff -- the edit did not land"
assert not bad, "SCOPE VIOLATION: %s" % bad
print("criterion 8: PASS")
PY
echo "exit=$?"
```

Expected: the `BASE =` line, one `in scope:` line per path, then `criterion 8: PASS`, `exit=0`.

Any printed `SCOPE VIOLATION` — in particular anything under `plugins/`, `scripts/`, `docs/adr/`, `docs/agents/`, `.claude-plugin/`, or `CLAUDE.md` — is a scope violation: **HALT and report the path.** Do not revert it silently; the pipeline needs to know how it got there. Line-level scope is criterion 6's `assert new == want`, which pins all 81 lines and needs no separate check here.

- [ ] **Step 9: Record the verdict — do not commit**

Report each of the eight results, quoting its actual output. All eight criteria must be green:

| # | Criterion | Where checked | Expected |
|---|---|---|---|
| 1 | Removed `_Avoid_:` line gone from `CONTEXT.md` | Task 2 Step 1 | no output, exit 1 |
| 2 | No `nested` / `depth-2` / `stage subagent` in `CONTEXT.md` | Task 2 Step 2 | no output, exit 1 |
| 3 | Three `_Avoid_:` lines at 11 / 15 / 81, exact text | Task 2 Step 3 | three lines as quoted |
| 4 | 81 lines, 21 entries, 5 sections, 3 `_Avoid_:` lines | Task 2 Step 4 | `81`, `21`, `5`, `3` |
| 5 | `### Topology` at 55, headwords at 57/60/63/66, Provenance at 27, 3 `orchestrator` lines | Task 2 Step 5 | as quoted |
| 6 | Design conformance — total reconstruction from the design's blocks | Task 1 Step 4 | `design-conformance: OK`, exit 0 |
| 7 | `check-sync.py` exit 0 + final line; `claude plugin validate .` exit 0, 8 warnings, 0 errors | Task 2 Steps 6–7 | as quoted |
| 8 | Only `CONTEXT.md` and `docs/superpowers/` paths changed | Task 2 Step 8 | `criterion 8: PASS` |

If every row is green, execution is complete. Report the verdict. **Do not commit, do not push, do not open a PR, do not merge, do not close an issue, do not file a follow-up, do not invoke a review skill** — those are the pipeline's steps.

---

## Not part of this implementation

Recorded so a fresh implementer does not helpfully do them.

- **Committing, pushing, opening the PR, merging.** The pipeline's, in every case. Criterion 8 is written to be meaningful on an uncommitted tree precisely so this task boundary holds.
- **Closing issues #31 and #34.** The pipeline's integration step (design **A5**). Both issues ship, so both close on merge. **#34's closing comment must carry the design's *The three `_Avoid_:` names #34 proposes* section** — that sub-question is a recorded no-change, and without it the three rejected names (`nested`, `depth-2`, `stage subagent`) will be re-proposed by the next reader of the issue. **#31 closes with a pointer to the design's *Issue #31* section.** No follow-up issues are filed by this change.
- **Filing the design's two recorded residues** (**A7**). (i) `worker`, `subagent`, `run` and `stage` remain unglossed — deliberate; none has a measured second sense, and an entry added so a section looks complete is the glossary serving itself. (ii) `execute-stage-subagent` survives in both pipeline copies as the name of a *denied* construct — correct prose, and a cost only under an `_Avoid_: stage subagent` rule this change declines to create. **Filing an issue for a non-defect manufactures the re-derivation these two issues were filed to end.**
- **Bumping any plugin version** (**A2**). `CONTEXT.md` enters no version-keyed cache. Editing a `plugin.json` is a scope violation.
- **Extending `scripts/check-sync.py` to validate `CONTEXT.md`'s structure.** Rejected on the merits in the design, not merely on scope — the glossary's format is not a mirror-pair invariant and shares nothing with what that script checks. `scripts/` is hard-excluded in any case.
- **Repairing `execute-stage-subagent`, or anything else, in `plugins/`.** Hard-excluded, concurrently owned, and there is no defect there to repair.
- **Editing `docs/adr/0002-…`** (says `group-resolution tier`, a different string no grep for the agent form reaches) or any pre-existing `docs/superpowers/` record. Both are dated records; shipped prose moving past an ADR's wording is normal and is not drift.

## Plan self-review

- **Spec coverage.** *The edit*'s pre-flight → Task 1 Step 1; its two anchor-matched edits → Task 1 Step 3. *Success criteria* 1–8 → the Task 2 Step 9 table, each row naming the step that runs it; criterion 6 additionally runs **red** at Task 1 Step 2 so it is seen to discriminate. *Out of scope* → Global Constraints' hard-excluded list plus *Not part of this implementation*. **A1** → Global Constraints' anchor-text rule and Task 1 Step 3's applier, which refuses rather than writes when an anchor is absent or not unique. **A2** → Global Constraints (no version bump) and *Not part of this implementation*. **A3** → Task 2 Step 6's note that `check-sync.py` proves nothing about the new text. **A4** → Task 2 Step 7. **A5** and **A7** → *Not part of this implementation*. **A6** → Tech Stack and each task's *Files: Test: none*.
- **Placeholder scan.** No TBDs. Every command carries its absolute path and its expected output; every Python snippet is complete and runnable as written. Every expected value was measured in this checkout at `b4b5d1c` — including the criterion 6 red result, the post-change line numbers 55 / 57 / 60 / 63 / 66 / 27 / 81, and the counts 81 / 21 / 5 / 3 — by reconstructing the post-change file from the design's blocks rather than by prediction.
- **Retype check.** No step restates block 0 or block 1. Task 1 Step 3 writes both through `read_blocks`; Task 1 Steps 2 and 4 verify both through `read_blocks`. The only block-derived literal typed anywhere is block 0's text in **Task 2 Step 3**, and that is deliberate and load-bearing: the design designates criteria 3–5 as the independent pins that are written from the rulings rather than read from the blocks, and they are the only thing that would catch a block reworded inside the design at an unchanged line count. The other literals typed are *pre-edit* anchors (`_Avoid_: group agent, judge, arbiter`, the **Slug** prefix), each checked against the base revision, so a typo fails an assert instead of blessing a misrouted edit.
- **Type consistency.** `read_blocks(<design>, [1, 14])` is called with the same shape in all three places it appears (Task 1 Steps 2, 3, 4); `split_lines` has one definition, repeated verbatim in the two places it appears, and the `DESIGN_SHA` pin has one, repeated verbatim in the two snippets that call `read_blocks` — process isolation, not context isolation, is the reason: each snippet is a separate `python3 -` heredoc and Global Constraints forbid writing a shared module to disk. The *reader* itself is not copied: every snippet imports `scripts/design_blocks.py` per `CLAUDE.md`, so this plan adds no new inline fenced-block reader. Block indices (`blocks[0]` → the `_Avoid_:` line, `blocks[1]` → the section) and the 0-based anchor indices (`14`, `52`) are used identically in the applier and the conformance check.
