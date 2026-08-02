---
dev-flow:
  slug: gh-24-design-block-reader
  spec: docs/superpowers/specs/2026-08-02-gh-24-design-block-reader-design.md
---

# gh-24: Shared Design-Block Reader Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the one invariant part of this repo's design-conformance checks — the fenced-block reader and the shape guard that always follows it — into a new `scripts/design_blocks.py`, reword `CLAUDE.md` line 9 to name it, and add the repo's first `.gitignore` for the bytecode that importing it creates.

**Architecture:** Three files change, and **all three of their contents already exist, complete and literal, inside the design document** at `docs/superpowers/specs/2026-08-02-gh-24-design-block-reader-design.md`. They are that document's three **plain fenced blocks** — fences with *no* info string; every other fence in that document is tagged ` ```sh `, ` ```python ` or ` ```text `. Task 1 slices blocks 0 and 2 out of the design **as committed at `bc72fac`** into `scripts/design_blocks.py` and `.gitignore` — `git show` piped through `sed`, never typed — then immediately proves the result byte-for-byte against the design on disk, using the file it just wrote. Task 2 replaces `CLAUDE.md` line 9 with block 1 using an applier that re-reads that block from the design through the new helper — the replacement text is never retyped. Task 3 runs the design's whole Verification section.

**Tech Stack:** Markdown, `python3` (stdlib only: `sys`, `pathlib`), `git`, `claude plugin validate`.

## Global Constraints

- **Repo root:** `/Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ac82daf37a62b0035`. **Every relative path below is relative to it, and every command below is run from it.** Repo-root cwd is a hard precondition of every check in this plan — the design paths, the target paths and the `sys.path.insert(0, "scripts")` import are all cwd-relative, exactly as they were before this change (design, *Question 5*).
- **Branch:** `tayl0r/gh-24-design-block-reader`, already checked out. Base commit for every diff in this plan is **`c8b2182`**. **Do not create a git worktree, do not switch branches, do not commit, do not push, do not open a PR, do not merge, do not invoke a review skill.** The pipeline owns every one of those.
- **The design is authoritative.** `docs/superpowers/specs/2026-08-02-gh-24-design-block-reader-design.md`, committed at `bc72fac`. Where this plan and the design appear to disagree, stop and report rather than choosing.
- **Never retype the payload text — no exceptions, in any task.** Block 1 is applied by re-reading it from the design on disk. Blocks 0 and 2 are sliced out of the design as committed at `bc72fac`, by Task 1, and then proved byte-for-byte against the design on disk. **No step in this plan asks you to reproduce payload text from what you have read; if one appears to, you have misread it.** A hand-typed or model-paraphrased copy is a defect even if it looks identical — Task 1 Step 5 and Task 3 Step 5 exist specifically to catch that.
- **This plan adds no inline copy of the fenced-block reader, and neither may you.** The whole point of this change is to stop hand-copying that 16-line prologue; the repo carries **23** historical copies and this is the first dev-flow change in five to add none. Every conformance check here starts with `sys.path.insert(0, "scripts")` and `from design_blocks import read_blocks`. **If a step seems to need its own inline reader, stop and report — do not write one.**
- **Files in scope — nothing else may be created or edited:**
  - **Create** `scripts/design_blocks.py` — design block 0, verbatim, **101 lines**.
  - **Create** `.gitignore` at the repo root — design block 2, verbatim, **3 lines**.
  - **Modify** `CLAUDE.md` **line 9 only** — whole-line replacement with design block 1, **1 line**. The file stays **29 lines**.
- **Forbidden files — if a step appears to need one of these, STOP and report it as a blocker; do not work around it:** anything under `plugins/`, any `plugin.json`, `.claude-plugin/marketplace.json`, `CONTEXT.md`, `docs/adr/`, `scripts/check-sync.py`, and all 9 historical documents under `docs/superpowers/` that hold the 23 inline readers. **No version is bumped.** Nothing here ships into a plugin cache, so the version-keyed-cache rule in `CLAUDE.md` does not apply. That is the design's conclusion, not a deferral.
- **The derived numbers, already measured.** The design deliberately writes no literal derived from its own blocks; its Verification carries the symbols **B0**, **B1**, **B2**. Measured against the design **as committed at `bc72fac`**: **B0 = 101, B1 = 1, B2 = 3**, so the design's own block shape is **`[101, 1, 3]`**. Every occurrence below is already substituted. **If any command reports a different shape, STOP and report** — the design was edited after this plan captured it, and every block index in this plan is then suspect.
- **This repo has no test framework.** There is nothing to `pytest` or `npm test`. The "suite" is exactly two commands: `python3 scripts/check-sync.py` (expect `check-sync: all checks passed`) and `claude plugin validate .` (expect **exactly 8** `No author information provided` warnings and exit 0 — **that is success, not failure**).
- **`python3 - <<'PY'` heredoc fences in this plan are unindented on purpose.** A heredoc indented under a list item is an `IndentationError`. Copy the fenced block as written; do not re-indent it to line up with its bullet.
- **Text assertions use `git grep`, not bare `grep`.** Under Claude Code's Bash tool bare `grep` is a ugrep-backed shell function whose output layout and ordering are not reliable for per-file assertions. Whole-line and index assertions are made in `python3`, where they are exact.

## File Structure

| Path | Change | Source | Responsibility |
|---|---|---|---|
| `scripts/design_blocks.py` | **Create** (101 lines) | design block 0 | The shared reader: `read_blocks(design_path, shape)` returns the design's plain fenced blocks after checking the caller's declared shape; `python3 scripts/design_blocks.py <design>` prints that shape and one preview line per block. |
| `.gitignore` | **Create** (3 lines) | design block 2 | Repo's first. Ignores `__pycache__/` and `*.pyc` — the bytecode CPython writes into `scripts/` the moment any conformance check imports the helper. Nothing else is listed. |
| `CLAUDE.md` | **Modify line 9 only** | design block 1 | Keeps the per-change ruling for the block-to-file mapping and the per-target assertions, and adds that the *reader* is not per change — naming the discovery command and the call form. |

Everything below the shape guard — which block goes to which file, the anchors, whether a check applies or verifies, what each target must satisfy — stays per change. That is what `CLAUDE.md` keeps saying and what this plan's own Task 2 demonstrates.

**Deliberately not a task here.** The design's *Out of scope* section ends with a note that issue #19 should record this change's measurement and verdict. That is a remark for the maintainer, not a file change: this plan touches no issue tracker and no task below should run `gh issue comment`. It is called out so the note is not silently lost.

## Task order and dependencies

**The tasks are strictly ordered and run in one checkout.**

- **Task 1 is a hard prerequisite of Tasks 2 and 3.** Every conformance check in this plan imports `read_blocks` from `scripts/design_blocks.py`, which does not exist until Task 1 creates it. A later task consuming an earlier task's deliverable is not a hidden coupling here — the helper *is* Task 1's whole deliverable (design, *Question 1*). Do not attempt Task 2 or Task 3 before Task 1's verification is green.
- **Task 1 cannot use the helper to create the helper.** It slices blocks 0 and 2 straight out of the design as committed at `bc72fac`, then verifies both with the file it just wrote. No payload text is produced by hand at any point, so the classic bootstrap failure — quietly "improving" `sys.path.insert(0, ...)` to `.append`, or `raise SystemExit` to `assert`, on the way through — cannot occur at all, rather than merely being caught afterwards. What the verification still has to catch is a wrong *slice*, and it does: either the file does not parse (the CLI exits non-zero, naming the fence line the slice swallowed) or the byte-for-byte comparison fails. There is no failure mode in which a broken reader hides a mismatched target — a wrong expected block *fails* the comparison, it does not silently pass it.
- **Task 1 lands `.gitignore` together with the helper, deliberately.** That way Task 2's red run of the design-conformance check isolates the `CLAUDE.md` edit: the two file-comparison branches are already green, so the only mismatches reported are the two `CLAUDE.md` ones.
- **Task 2 must run the design-conformance check red before its edit and green after**, so the check is *seen* to discriminate rather than merely asserted to.

---

### Task 1: Create the shared reader and the `.gitignore`

**Files:**
- Create: `scripts/design_blocks.py` (design block 0, verbatim, 101 lines)
- Create: `.gitignore` (design block 2, verbatim, 3 lines)
- Read only: `docs/superpowers/specs/2026-08-02-gh-24-design-block-reader-design.md`
- Test: none — this repo has no test framework. Verification is Steps 4–7 below.

**Interfaces:**
- Consumes: nothing. This is the first task.
- Produces, for every later task and every future change in this repo:
  - `read_blocks(design_path, shape) -> list[list[str]]` — importable as `from design_blocks import read_blocks` after `sys.path.insert(0, "scripts")`. Returns the design's plain (untagged) fenced blocks, in document order, as lists of lines (newlines stripped), **after** checking that `[len(b) for b in blocks]` equals `list(shape)`. `shape` is a **required positional argument**. On mismatch it raises `SystemExit` with `design code-block shape is <actual>, want <shape!r>; stop and re-read the design` — exit 1, one line on stderr, no traceback.
  - `python3 scripts/design_blocks.py <design-path>` — prints `shape: [...]` then one `  [i] len=N: <first 70 chars of the block's first line>` line per block. Exit 1 with a usage line if the argument count is not exactly 1.
  - Refusals, both exit 1 with one line on stderr: a fence longer than three backticks (`<path> line <N>: this reader parses three-backtick fences only; a longer one mis-indexes every block after it`) and a fence that is never closed (`<path>: the fence opened at line <N> is never closed; a plain block cannot contain a three-backtick line`).

- [x] **Step 1: Locate the two blocks in the design**

Open `docs/superpowers/specs/2026-08-02-gh-24-design-block-reader-design.md` and find its **plain fenced blocks** — the fences whose opening line is exactly three backticks with **no** info string after them. There are exactly three. You need the first (block 0) and the third (block 2).

- **Block 0** lives under the heading `## The new file`. As committed at `bc72fac` its opening fence is at design **line 76** and its closing fence at design **line 178**, so its content is design **lines 77–177 inclusive — 101 lines**. Its first line is:

```text
#!/usr/bin/env python3
```

  and its last line is (four leading spaces):

```text
    sys.exit(main())
```

- **Block 2** is the design's **third and last** plain fenced block — the three-line ignore list, in the design section that argues for the new root ignore file. As committed at `bc72fac` its content is design **lines 217–219 inclusive — 3 lines**:

```text
# Bytecode from importing scripts/design_blocks.py in design-conformance checks.
__pycache__/
*.pyc
```

Those line numbers are the coordinates Steps 2 and 3 slice on, and they are safe to slice on because they are read off the design **as committed at `bc72fac`**, which `git show` reproduces byte for byte forever. **The enclosing fence lines are not part of the block** — each slice starts one line after the opening fence and ends one line before the closing one. Measured on `bc72fac`: no line anywhere in `77–177` or in `217–219` is a fence — there is no line in either range whose stripped form starts with three backticks — so neither slice can straddle one. You do not have to take that on trust: Step 4 refuses to run a file that carries a stray fence line, and Step 5 compares both slices, line by line, against the blocks the *fences* delimit in the design **on disk**. If Step 4 or Step 5 disagrees with these numbers, **STOP and report** — the design moved after this plan captured it and every substituted literal here is suspect. **Do not re-slice on adjusted coordinates**, which would silently absorb the change instead of surfacing it.

- [x] **Step 2: Extract `scripts/design_blocks.py` from the design — do not type it**

Run this exactly, from the repo root. `scripts/` already exists (it holds `check-sync.py`).

```sh
git show bc72fac:docs/superpowers/specs/2026-08-02-gh-24-design-block-reader-design.md | sed -n '77,177p' > scripts/design_blocks.py
wc -l scripts/design_blocks.py
```

`wc -l` must report **101** (BSD `wc` pads the number with spaces; read the number, not the layout). Anything else means the extraction did not happen — most likely **0**, which is what a failed `git show` leaves behind, because a pipeline's exit status is `sed`'s and not `git`'s. **STOP and report; do not proceed to Step 4**, which prints nothing and exits 0 on an empty file, and do **not** fall back to reading the design out of the working tree.

**Do not open the file and retype, reformat, reflow, re-wrap, or "fix" any of it. The slice is the deliverable.** Four details in that file look like cleanup opportunities, are deliberate, and would be a defect to introduce by hand or to correct by hand: `raise SystemExit` rather than `assert` (an `assert` is a no-op under `python3 -O`); `_blocks` private and unguarded while `read_blocks` is public and shape-required; `sys.path.insert(0, ...)` rather than `append`; and the reader **refusing** a longer-than-three-backtick fence and an unclosed fence rather than dropping them. The file is deliberately pure ASCII and spells the fence as `chr(96) * 3`.

`git show <sha>:<path>` is used rather than reading the design out of the working tree on purpose, and it is the reason Step 5 means something. It pins the bytes to the commit this plan measured, so if the design has moved since `bc72fac` this step still writes what the plan reviewed, and Step 5 — which reads the design **on disk** — reports the divergence. The shape guard alone would not: an edit that leaves block 0 at 101 lines is invisible to it. Slicing the working-tree copy would absorb such an edit silently and go green.

- [x] **Step 3: Extract `.gitignore` from the design — do not type it**

Same mechanism, same commit, the other block. Run from the repo root:

```sh
git show bc72fac:docs/superpowers/specs/2026-08-02-gh-24-design-block-reader-design.md | sed -n '217,219p' > .gitignore
cat .gitignore
```

`cat` must print exactly these three lines, and nothing else:

```text
# Bytecode from importing scripts/design_blocks.py in design-conformance checks.
__pycache__/
*.pyc
```

Empty or short output means the extraction failed — **STOP and report**, and do not type the lines in by hand. This is the repo's first `.gitignore`; do not add anything to it. In particular do **not** add `.claude/worktrees/` or `.claude/dev-flow.local.md` — dev-flow puts those in `.git/info/exclude` itself, and duplicating them here would add a second owner for a question that already has one.

- [x] **Step 4: Run the new CLI against the design — the extraction's first, loudest check**

```sh
python3 scripts/design_blocks.py docs/superpowers/specs/2026-08-02-gh-24-design-block-reader-design.md
```

Expected output, exactly (the `[1]` preview line is truncated at 70 characters and therefore ends in a space):

```text
shape: [101, 1, 3]
  [0] len=101: #!/usr/bin/env python3
  [1] len=1: - **Some files are mirrored across `dev-flow` and `dev-flow-worktree` 
  [2] len=3: # Bytecode from importing scripts/design_blocks.py in design-conforman
```

A `SyntaxError` or `IndentationError` pointing at a line that is three backticks means the Step 2 slice swallowed a fence line — the Step 1 coordinates are off by one. **No output at all with `exit=0`** means the file is empty and Step 2's `wc -l` was not read. Any other traceback, or any other shape, means the file is not design block 0. In every case: re-run Step 2's command once, verbatim, to rule out a truncated write; if the same failure repeats, **STOP and report** — the extraction is deterministic, so a repeat means the design moved after `bc72fac`. **Do not adjust this expected output, do not edit the design, and do not hand-correct `scripts/design_blocks.py`.**

- [x] **Step 5: Prove both files byte-for-byte against the design, using the file just written**

This is the bootstrap closing on itself: the helper reads the design **on disk** and hands back the very blocks the two new files were sliced from. It is not a tautology, because the two sides are derived differently — Steps 2 and 3 sliced the design *as committed at `bc72fac`* on fixed line coordinates, and this step checks that against the blocks the *fences* delimit in the design as it stands now. It therefore discriminates on three independent things: a slice whose coordinates were wrong but which still parsed as Python (dropping the shebang does exactly that, and Step 4 passes it), a design that moved after `bc72fac` without changing any block's length, and a reader whose fence parsing disagrees with the fences a human read — which is this helper's first end-to-end exercise (design, *Question 1*). Run from the repo root. **The fence is unindented on purpose** — a `python3` heredoc indented under a list item is an `IndentationError`.

```sh
python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
DESIGN = "docs/superpowers/specs/2026-08-02-gh-24-design-block-reader-design.md"
blocks = read_blocks(DESIGN, [101, 1, 3])
bad = []

def lines(path):
    ls = Path(path).read_text(encoding="utf-8").split("\n")
    if ls and ls[-1] == "":
        ls.pop()
    return ls

for path, i in (("scripts/design_blocks.py", 0), (".gitignore", 2)):
    disk = lines(path)
    if disk != blocks[i]:
        bad.append("%s differs from design block %d (%d lines on disk, %d in the design)"
                   % (path, i, len(disk), len(blocks[i])))
        for n, (a, b) in enumerate(zip(disk, blocks[i]), 1):
            if a != b:
                bad.append("  first difference at %s line %d: on disk %r, in design %r" % (path, n, a, b))
                break
for why in bad:
    print("MISMATCH:", why)
print("bootstrap-conformance:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected output, exactly:

```text
bootstrap-conformance: OK
exit=0
```

Any `MISMATCH:` line names the file, the block and the first differing line. Because Steps 2 and 3 are deterministic, re-running them cannot change the result, so a mismatch here means one of two things: the Step 1 coordinates are wrong, or the design on disk is no longer the design at `bc72fac`. **STOP and report**, quoting the `first difference at ...` line — do not hand-edit either file to make this pass, and do not re-slice on adjusted coordinates. Same if the script exits with `design code-block shape is ...`: the design's block shape moved and this plan's indices are stale.

- [x] **Step 6: Prove the `.gitignore` actually suppresses the bytecode**

Step 5 imported `design_blocks`, so CPython has just written `scripts/__pycache__/design_blocks.cpython-3XX.pyc` into the working tree. That artifact is the entire reason `.gitignore` exists: untracked, it never reaches `git diff --stat`, it trips dev-flow's dirty-checkout gate on every later run, and it is one broad `git add` away from an unrelated PR.

```sh
ls scripts/__pycache__
git check-ignore -v scripts/__pycache__
git status --porcelain --untracked-files=all -- scripts/
```

Expected:
- `ls` lists at least one `design_blocks.cpython-3XX.pyc` (the exact version suffix depends on the local CPython and is not asserted). If the directory does not exist, Step 5 did not actually import the module — re-run it.
- `git check-ignore -v` prints exactly one line and exits 0:

```text
.gitignore:2:__pycache__/	scripts/__pycache__
```

  (the separator is a tab). `.gitignore` line 2 is `__pycache__/`. A **non-zero exit with no output** means the artifact is *not* ignored — the `.gitignore` did not land, or landed with the wrong content. **STOP and report.**
- `git status --porcelain --untracked-files=all -- scripts/` shows a line for `scripts/design_blocks.py` and **no line mentioning `__pycache__` or `.pyc`**. A `__pycache__` line here is the same failure. **STOP and report.**

- [x] **Step 7: Confirm nothing else in the tree changed**

```sh
git status --porcelain -- CLAUDE.md
git diff --quiet c8b2182 -- plugins/ .claude-plugin/ && echo "plugins/ untouched: OK"
```

Expected: the first command prints **nothing** — Task 1 does not touch `CLAUDE.md`; that is Task 2's job. The second prints `plugins/ untouched: OK`.

- [x] **Step 8: Do not commit**

Leave both new files in the working tree. The pipeline commits. Report that Task 1 is complete, that the CLI printed `shape: [101, 1, 3]`, and that `bootstrap-conformance: OK`.

---

### Task 2: Replace `CLAUDE.md` line 9 with design block 1

**Files:**
- Modify: `CLAUDE.md` line 9 only (whole-line replacement; the file stays 29 lines)
- Read only: `docs/superpowers/specs/2026-08-02-gh-24-design-block-reader-design.md`, `scripts/design_blocks.py`

**Interfaces:**
- Consumes: `read_blocks(design_path, shape)` from `scripts/design_blocks.py`, created by Task 1 — imported as `sys.path.insert(0, "scripts")` then `from design_blocks import read_blocks`. **Task 1 must be complete and green before this task starts.** Also consumes `.gitignore`, created by Task 1, so that Step 1's red run reports only the two `CLAUDE.md` mismatches.
- Produces: `CLAUDE.md` line 9 equal to design block 1, byte for byte. Nothing later in this plan depends on the applier itself.

**What is being replaced, and why whole-line.** `CLAUDE.md` line 9 is the mirror-pair bullet. Only its **final sentence** differs between the old and new text; the design nonetheless gives the **complete new line** as block 1, and this task replaces the whole line. That is what gh-7 did for this same line (`docs/superpowers/plans/2026-07-27-gh-7-review-depth-plan.md`, Step 4) and it is the stronger check: an exact whole-line match at a known index cannot be satisfied by a fragment landing in the wrong bullet. The phrase the edit removes, for the residue grep, is `the block-to-file mapping differs every time` — pure ASCII and unique.

- [x] **Step 1: Run the design-conformance check and watch it FAIL (red)**

Run this **before** touching `CLAUDE.md`. It is the design's Verification step 5 verbatim, with B0/B1/B2 substituted. Run from the repo root. **The fence is unindented on purpose** — a `python3` heredoc indented under a list item is an `IndentationError`.

```sh
python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
DESIGN = "docs/superpowers/specs/2026-08-02-gh-24-design-block-reader-design.md"
OLD = "the block-to-file mapping differs every time"
BASE_LINES = 29  # CLAUDE.md at c8b2182 -- a fact about the base commit, not about any block
blocks = read_blocks(DESIGN, [101, 1, 3])
bad = []

def lines(path):
    ls = Path(path).read_text(encoding="utf-8").split("\n")
    if ls and ls[-1] == "":
        ls.pop()
    return ls

for path, i in (("scripts/design_blocks.py", 0), (".gitignore", 2)):
    disk = lines(path)
    if disk != blocks[i]:
        bad.append("%s differs from design block %d (%d lines on disk, %d in the design)"
                   % (path, i, len(disk), len(blocks[i])))
claude = lines("CLAUDE.md")
want = BASE_LINES - 1 + len(blocks[1])
if len(claude) != want:
    bad.append("CLAUDE.md is %d lines, want %d" % (len(claude), want))
at = [i + 1 for i, l in enumerate(claude) if l == blocks[1][0]]
if at != [9]:
    bad.append("the mirror-pair bullet matches design block 1 at lines %s, want exactly [9]" % at)
if any(OLD in l for l in claude):
    bad.append("the pre-change per-change-runner clause survives in CLAUDE.md")
for why in bad:
    print("MISMATCH:", why)
print("design-conformance:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected output, exactly — **two** mismatches and no more:

```text
MISMATCH: the mirror-pair bullet matches design block 1 at lines [], want exactly [9]
MISMATCH: the pre-change per-change-runner clause survives in CLAUDE.md
design-conformance: FAIL
exit=1
```

This is measured, not predicted. Note what is **absent**: no `scripts/design_blocks.py` mismatch, no `.gitignore` mismatch, no line-count mismatch — Task 1 landed both files and the whole-line replacement leaves the count at 29. If you see any of those extra lines, **STOP and report** — the tree is not in the state this task requires, and this task modifies `CLAUDE.md` line 9 and nothing else, so it cannot repair `scripts/design_blocks.py` or `.gitignore`. A `scripts/design_blocks.py` mismatch in particular means the applier in Step 2 would import a reader that does not match the design. If you see `design-conformance: OK` here, `CLAUDE.md` was edited before this step ran — **STOP and report**, the check has not been shown to discriminate. If the script exits with `design code-block shape is ...`, **STOP and report**: the design was edited after this plan captured its shape.

- [x] **Step 2: Apply the edit, re-reading block 1 from the design**

The replacement text is **never retyped**. This applier reads block 1 through `read_blocks`, asserts the target line is where and what it expects, and writes it. Run from the repo root. **The fence is unindented on purpose.**

```sh
python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
DESIGN = "docs/superpowers/specs/2026-08-02-gh-24-design-block-reader-design.md"
TARGET = "CLAUDE.md"
OLD = "the block-to-file mapping differs every time"
HEAD = "- **Some files are mirrored across "
blocks = read_blocks(DESIGN, [101, 1, 3])
text = Path(TARGET).read_text(encoding="utf-8")
lines = text.split("\n")
at = [i for i, l in enumerate(lines) if OLD in l]
if at != [8]:
    raise SystemExit("%s: the clause to replace is at 0-based lines %s, want exactly [8]"
                     " (line 9); stop and re-read the file" % (TARGET, at))
if not lines[8].startswith(HEAD):
    raise SystemExit("%s line 9 is not the mirror-pair bullet: %r" % (TARGET, lines[8][:60]))
lines[8] = blocks[1][0]
Path(TARGET).write_text("\n".join(lines), encoding="utf-8")
print("CLAUDE.md line 9 replaced from design block 1")
PY
echo "exit=$?"
```

Expected output, exactly:

```text
CLAUDE.md line 9 replaced from design block 1
exit=0
```

The applier is deliberately single-shot: run it twice and the second run exits 1 with `the clause to replace is at 0-based lines [], want exactly [8] (line 9)`, because the phrase it anchors on is gone. That is correct behaviour, not a bug — if you see it, the edit already landed; go to Step 3 rather than re-applying. `split("\n")` / `"\n".join` round-trips the trailing newline exactly, so the file keeps its final newline and its 29 lines.

- [x] **Step 3: Re-run the design-conformance check and watch it PASS (green)**

Run **the identical script from Step 1 again** — same text, unchanged. Do not edit it.

Expected output, exactly:

```text
design-conformance: OK
exit=0
```

Red in Step 1, green here, with nothing between them but the applier: the check is now demonstrated to discriminate. If any `MISMATCH:` line survives, do not edit the check — fix `CLAUDE.md` by re-running Step 2's applier against a `CLAUDE.md` restored to its base state (`git checkout c8b2182 -- CLAUDE.md`).

- [x] **Step 4: Residue — the removed phrase is gone from shipped text**

```sh
git grep -n -F 'the block-to-file mapping differs every time' -- . ':!docs/superpowers/'
```

Expected: **no output**, non-zero exit. The `':!docs/superpowers/'` pathspec is required — the design quotes the phrase, legitimately, and this plan quotes it too.

- [x] **Step 5: Presence — `CLAUDE.md` names the helper**

```sh
git grep -c -F 'scripts/design_blocks.py' -- CLAUDE.md
git grep -c -F 'read_blocks(<design>, <shape>)' -- CLAUDE.md
```

Expected: each prints exactly `CLAUDE.md:1`.

- [x] **Step 6: One line changed, and only in `CLAUDE.md`**

```sh
git diff --stat c8b2182 -- CLAUDE.md
git diff --quiet c8b2182 -- plugins/ .claude-plugin/ CONTEXT.md docs/adr/ scripts/check-sync.py && echo "out-of-scope untouched: OK"
```

Expected: the first prints a row reading ` CLAUDE.md | 2 +-` (one insertion, one deletion) and the summary `1 file changed, 1 insertion(+), 1 deletion(-)`. Read the numbers, not the bar widths, which git scales. The second prints `out-of-scope untouched: OK`.

- [x] **Step 7: Do not commit**

Leave the change in the working tree. Report that Task 2 is complete, quoting the red output from Step 1 and the green output from Step 3.

---

### Task 3: Run the design's full Verification section

**Files:** none created or modified. This task only reads and runs commands.

**Interfaces:**
- Consumes: `scripts/design_blocks.py` and `.gitignore` from Task 1, the edited `CLAUDE.md` from Task 2. **Both earlier tasks must be complete before this task starts.**
- Produces: nothing. Its output is the evidence the change is correct and in scope.

This is the design's Verification section, steps 0–10, with **B0 = 101, B1 = 1, B2 = 3** substituted throughout. Every command runs from the repo root. Base commit for every diff is `c8b2182`. **Run all eleven verification steps — 0 through 10 — and report each one's actual output**; do not stop at the first green. Step 11 is this task's own hand-off.

- [x] **Step 0: Derive the design's own block shape and confirm it still matches this plan**

```sh
python3 scripts/design_blocks.py docs/superpowers/specs/2026-08-02-gh-24-design-block-reader-design.md
```

Expected output, exactly (the `[1]` preview line is truncated at 70 characters and ends in a space):

```text
shape: [101, 1, 3]
  [0] len=101: #!/usr/bin/env python3
  [1] len=1: - **Some files are mirrored across `dev-flow` and `dev-flow-worktree` 
  [2] len=3: # Bytecode from importing scripts/design_blocks.py in design-conforman
```

The three entries are B0, B1 and B2 in order. **If the shape has other than three entries, or any entry differs, STOP and report** — the design was edited after this plan captured its numbers, and every substituted literal in this plan is stale.

- [x] **Step 1: Exactly three files changed, none of them a plugin file**

```sh
git add -N .gitignore scripts/design_blocks.py
git diff --stat c8b2182 -- . ':!docs/superpowers/'
git diff --quiet c8b2182 -- plugins/ .claude-plugin/ && echo "plugins/ untouched: OK"
```

`git diff` only sees paths git tracks, and `.gitignore` and `scripts/design_blocks.py` are new. `git add -N` (`--intent-to-add`) records those two paths in the index **without staging any content**, so the stat can see them; it is a harmless no-op if the pipeline has already committed them. It names exactly the two intended paths, so it cannot sweep in `scripts/__pycache__/` — **never use `git add -A` here.**

Expected, in git's path order:

```text
 .gitignore               |   3 ++
 CLAUDE.md                |   2 +-
 scripts/design_blocks.py | 101 +++++++++++++++++++++++++++++++++++++++++++++++
 3 files changed, 105 insertions(+), 1 deletion(-)
plugins/ untouched: OK
```

Read the numbers, not the bar widths, which git scales; the column alignment also varies with the widest path. There must be **no other row**. **A `scripts/__pycache__/` row means the `.gitignore` did not land, or something staged the artifact before it did — STOP and report.** Leave the artifact exactly as you found it and quote the row verbatim in your report — this task creates and modifies nothing, and un-staging or deleting the artifact would erase the evidence of how it reached the index.

The `':!docs/superpowers/'` pathspec is required: this run's front-matter sets `docs: commit`, so this design and this plan are committed on this branch and an unfiltered diff necessarily reports them.

- [x] **Step 2: The helper reproduces the readers it replaces, on five real inputs**

Each expected shape was asserted by that design's own merged plan, before this change existed. Five real inputs, four distinct shapes.

```sh
python3 scripts/design_blocks.py docs/superpowers/specs/2026-07-27-gh-10-opus-resolver-design.md
python3 scripts/design_blocks.py docs/superpowers/specs/2026-07-27-gh-7-review-depth-design.md
python3 scripts/design_blocks.py docs/superpowers/specs/2026-07-28-gh-16-terminology-collision-design.md
python3 scripts/design_blocks.py docs/superpowers/specs/2026-07-29-gh-20-diff-terminology-design.md
python3 scripts/design_blocks.py docs/superpowers/specs/2026-07-31-gh-26-family-name-design.md
```

Expected `shape:` line from each run, in order — each followed by one `  [i] len=N: ...` preview line per block (previews are informative, not asserted):

```text
shape: [1, 1, 1, 1, 1, 1, 1, 1]
shape: [1, 1, 1, 2, 2, 1, 12]
shape: [1, 1, 2, 1]
shape: [1, 1, 1, 2, 1, 1, 1, 1, 1, 1]
shape: [1]
```

Any deviation means the copy of block 0 that Task 1 installed is not block 0 — the Step 2 slice was wrong, or the design moved after `bc72fac`. **STOP and report** — do not edit these expectations, which are historical records from merged plans.

- [x] **Step 3: The guard fires, and both fence refusals fire**

First the shape guard. **The fence is unindented on purpose** — a `python3` heredoc indented under a list item is an `IndentationError`.

```sh
python3 - <<'PY'
import sys
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
read_blocks("docs/superpowers/specs/2026-07-31-gh-26-family-name-design.md", [9, 9])
print("guard did not fire")
PY
echo "exit=$?"
```

Expected, exactly — and **`guard did not fire` must not appear**:

```text
design code-block shape is [1], want [9, 9]; stop and re-read the design
exit=1
```

Then the **longer-fence refusal**, on the one document in the repo that trips it:

```sh
python3 scripts/design_blocks.py docs/superpowers/plans/2026-07-24-gh-6-docs-policy-plan.md; echo "exit=$?"
```

Expected, exactly (the line number is informative — the *refusal* is the assertion):

```text
docs/superpowers/plans/2026-07-24-gh-6-docs-policy-plan.md line 154: this reader parses three-backtick fences only; a longer one mis-indexes every block after it
exit=1
```

That plan wraps replacement text containing fences in four-backtick fences — correct Markdown, which this reader would mis-close at the first three-backtick line inside, so its plain blocks would bear no relation to its author's intent. Refusing is the point.

Then the **unclosed-fence refusal**. It has no instance in the repo, so it runs against a synthetic design in a temp directory; **nothing is written under the repo.** **The fence is unindented on purpose.**

```sh
python3 - <<'PY'
import sys, tempfile, pathlib
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
F = chr(96) * 3
p = pathlib.Path(tempfile.mkdtemp()) / "d.md"
p.write_text("x\n%s\nA\n%s\nB\n%s\n" % (F, F, F), encoding="utf-8")
read_blocks(str(p), [1])
PY
echo "exit=$?"
```

Expected — the temp path varies, the rest is exact:

```text
/var/folders/.../d.md: the fence opened at line 6 is never closed; a plain block cannot contain a three-backtick line
exit=1
```

- [x] **Step 4: The CLI rejects a wrong argument count**

```sh
python3 scripts/design_blocks.py; echo "exit=$?"
```

Expected, exactly:

```text
usage: python3 scripts/design_blocks.py <design-path>
exit=1
```

- [x] **Step 5: Design conformance — all three blocks landed verbatim, in the right place, through the new reader**

This is the check `CLAUDE.md` requires, and it is also the helper's first end-to-end use. It re-reads all three blocks from the design on disk — never retyped — and requires block 0 to be `scripts/design_blocks.py` byte for byte, block 1 to be `CLAUDE.md` line 9 exactly and uniquely, and block 2 to be `.gitignore` byte for byte. `CLAUDE.md`'s expected length is **computed** from block 1's actual length, so a block-1 edit cannot leave it stale; `BASE_LINES = 29` is a frozen fact about `c8b2182`, not about any block. The script is pure ASCII on purpose; the non-ASCII lives only in the blocks it reads.

Run **the identical script Task 2 ran** — reproduced here in full so this task is self-contained. **The fence is unindented on purpose.**

```sh
python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
DESIGN = "docs/superpowers/specs/2026-08-02-gh-24-design-block-reader-design.md"
OLD = "the block-to-file mapping differs every time"
BASE_LINES = 29  # CLAUDE.md at c8b2182 -- a fact about the base commit, not about any block
blocks = read_blocks(DESIGN, [101, 1, 3])
bad = []

def lines(path):
    ls = Path(path).read_text(encoding="utf-8").split("\n")
    if ls and ls[-1] == "":
        ls.pop()
    return ls

for path, i in (("scripts/design_blocks.py", 0), (".gitignore", 2)):
    disk = lines(path)
    if disk != blocks[i]:
        bad.append("%s differs from design block %d (%d lines on disk, %d in the design)"
                   % (path, i, len(disk), len(blocks[i])))
claude = lines("CLAUDE.md")
want = BASE_LINES - 1 + len(blocks[1])
if len(claude) != want:
    bad.append("CLAUDE.md is %d lines, want %d" % (len(claude), want))
at = [i + 1 for i, l in enumerate(claude) if l == blocks[1][0]]
if at != [9]:
    bad.append("the mirror-pair bullet matches design block 1 at lines %s, want exactly [9]" % at)
if any(OLD in l for l in claude):
    bad.append("the pre-change per-change-runner clause survives in CLAUDE.md")
for why in bad:
    print("MISMATCH:", why)
print("design-conformance:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected, exactly:

```text
design-conformance: OK
exit=0
```

Its discriminating power was demonstrated in Task 2, where the identical script printed, before the `CLAUDE.md` edit and after `.gitignore` and the helper had landed:

```text
MISMATCH: the mirror-pair bullet matches design block 1 at lines [], want exactly [9]
MISMATCH: the pre-change per-change-runner clause survives in CLAUDE.md
design-conformance: FAIL
exit=1
```

Both red and green were run against a scratch copy of the post-change tree while the design was written, so both expectations are measured, not predicted. If the shape guard trips instead (`design code-block shape is ...`), **STOP and report**: the design was edited after this plan captured its shape. Re-read the changed block before touching any number — the blocks are what every assertion in this plan indexes, so a moved shape can mean more than a moved count.

- [x] **Step 6: Residue — the phrase this edit removes is gone from shipped text**

```sh
git grep -n -F 'the block-to-file mapping differs every time' -- . ':!docs/superpowers/'
```

Expected: **no output**, non-zero exit. The pathspec is required — the design quotes the phrase, and so does this plan.

- [x] **Step 7: Presence — `CLAUDE.md` names the helper**

```sh
git grep -c -F 'scripts/design_blocks.py' -- CLAUDE.md
git grep -c -F 'read_blocks(<design>, <shape>)' -- CLAUDE.md
```

Expected: each prints exactly `CLAUDE.md:1`.

- [x] **Step 8: No 24th copy, and the 9 historical documents are byte-identical to `c8b2182`**

```sh
git grep -c 'for line in Path(DESIGN)\.read_text' -- 'docs/superpowers/*' ':!docs/superpowers/*gh-24-design-block-reader*'
```

Expected: exactly these 9 lines, summing to **23** — this is the first dev-flow change in five to add none:

```text
docs/superpowers/plans/2026-07-27-gh-10-opus-resolver-plan.md:3
docs/superpowers/plans/2026-07-27-gh-7-review-depth-plan.md:3
docs/superpowers/plans/2026-07-28-gh-16-terminology-collision-plan.md:5
docs/superpowers/plans/2026-07-29-gh-20-diff-terminology-plan.md:6
docs/superpowers/plans/2026-08-02-gh-26-family-name-plan.md:2
docs/superpowers/specs/2026-07-27-gh-7-review-depth-design.md:1
docs/superpowers/specs/2026-07-28-gh-16-terminology-collision-design.md:1
docs/superpowers/specs/2026-07-29-gh-20-diff-terminology-design.md:1
docs/superpowers/specs/2026-07-31-gh-26-family-name-design.md:1
```

Two details of that command are deliberate and must not be "simplified":

- **The `\.` is escaped.** In git's basic regex an unescaped `.` matches any character, so the escaped form is if anything stricter, and it returns the identical 9 lines — measured. It also keeps *this plan* out of a naive literal search for the inline-reader signature, which is exactly the property this whole change exists to establish.
- **The exclusion pathspec is required and is the whole point of the assertion.** The design quotes the search pattern twice in prose, and `git grep -c` counts matching *lines*, not documents — so without the exclusion the count reports more than 23 and says nothing about the 9 historical documents. The glob covers this run's design and plan regardless of their date prefixes.

Then prove the records themselves were not touched:

```sh
git diff --quiet c8b2182 -- docs/superpowers/plans/2026-07-27-gh-10-opus-resolver-plan.md docs/superpowers/plans/2026-07-27-gh-7-review-depth-plan.md docs/superpowers/plans/2026-07-28-gh-16-terminology-collision-plan.md docs/superpowers/plans/2026-07-29-gh-20-diff-terminology-plan.md docs/superpowers/plans/2026-08-02-gh-26-family-name-plan.md docs/superpowers/specs/2026-07-27-gh-7-review-depth-design.md docs/superpowers/specs/2026-07-28-gh-16-terminology-collision-design.md docs/superpowers/specs/2026-07-29-gh-20-diff-terminology-design.md docs/superpowers/specs/2026-07-31-gh-26-family-name-design.md && echo "records untouched: OK"
```

Expected: `records untouched: OK`. The 23 existing copies are deliberately left exactly as they are — they are records of what was executed, and rewriting them to import a file that did not exist at the time would make them claim a check was run in a form that could not have been run.

- [x] **Step 9: `check-sync.py` passes, with output identical to before the change**

```sh
python3 scripts/check-sync.py; echo "exit=$?"
```

Expected, exactly:

```text
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)
check-sync: all checks passed
exit=0
```

It reads none of the changed files: `CLAUDE.md` is enrolled in no mirror pair, and `check-sync.py` globs only `plugins/*/.claude-plugin/plugin.json`.

- [x] **Step 10: `claude plugin validate .` passes, and no version moved**

```sh
claude plugin validate .
```

Expected: `⚠ Found 8 warnings:` followed by exactly 8 lines reading `plugins[N] plugin.json → author: No author information provided. Consider adding author details for plugin attribution` (N = 0..7), then `✔ Validation passed with warnings`, exit 0. **Eight author warnings and a warning-passed verdict is the expected, documented success state for this repo — it is not a failure and nothing should be "fixed" in response to it.**

```sh
git grep '"version"' -- plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
```

Expected, exactly — unchanged from base `c8b2182`:

```text
plugins/dev-flow-worktree/.claude-plugin/plugin.json:  "version": "1.8.0",
plugins/dev-flow/.claude-plugin/plugin.json:  "version": "2.6.0",
```

- [x] **Step 11: Report, do not commit**

Leave everything in the working tree. The pipeline commits, pushes and opens the PR. Report:
- the derived shape from Step 0 (`[101, 1, 3]`),
- the Step 1 stat summary (`3 files changed, 105 insertions(+), 1 deletion(-)`),
- that Steps 2–4 exercised the helper on five real inputs plus three refusals,
- that Step 5 is `design-conformance: OK`,
- the Step 8 count (9 lines summing to 23) and `records untouched: OK`,
- that Steps 9 and 10 are green.

**Do not open a PR, do not push, do not merge, do not invoke a review skill.**

## PR body (for the pipeline — do not create the PR from this task)

```text
Close #24 by extracting the one invariant part of the design-conformance check.

23 byte-identical fenced-block readers across 9 documents and 5 issues, each
followed by a shape assert that has drifted into three spellings. The reader and
the guard move to scripts/design_blocks.py as read_blocks(design, shape), with a
CLI that prints a design's block shape and indices. Everything that genuinely
differs per change -- which block goes to which file, the anchors, the per-target
assertions -- stays in the check, and CLAUDE.md keeps saying so.

The 23 existing copies are deliberately left alone: they are records of executed
plans, and rewriting them to import a file that did not exist at the time would
make them claim a check was run in a form that could not have been run.

Making scripts/ importable makes it the first directory here that CPython writes
into, so this also adds the repo's first .gitignore -- __pycache__/ and *.pyc,
nothing else. Without it a stray .pyc trips dev-flow's dirty-checkout gate on
every later run and is one broad `git add` away from an unrelated PR.

Closes #24
```
