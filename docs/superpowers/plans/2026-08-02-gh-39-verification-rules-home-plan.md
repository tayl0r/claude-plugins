---
dev-flow:
  slug: gh-39-verification-rules-home
  spec: docs/superpowers/specs/2026-08-02-gh-39-verification-rules-home-design.md
---

# gh-39: the verification rules get a repo-wide home, and the mirror bullet keeps its reason — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make one edit to `CLAUDE.md` — replace line 9 in full with the design's block 0, and insert the design's block 1 plus one blank line directly after line 12 — so the two verification prescriptions live in a new repo-wide `## Verifying a change` section and the mirror bullet points forward at it. Nothing else in the repo changes.

**Architecture:** A single **atomic** two-hunk edit to one un-mirrored, un-cached Markdown file. `CLAUDE.md` goes **29 → 34 lines**: the new section lands at lines 13–16, its separating blank at 17, and `## Workflow` moves from 13 to 18. The two hunks are **not** separable — the design's *Verification* step 2 reconstructs the whole file from its merge-base blob and asserts it equals *base with line 9 replaced **and** block 1 inserted*, so a half-applied file has no green state to stop at. One applier therefore writes both hunks in one pass, reconstructing the file from the base blob rather than patching the working tree. **No `scripts/` file, no plugin file, no `plugin.json`, no version bump, no `CONTEXT.md`, no `docs/adr/`, no `.github/`, no `marketplace.json`.**

**Tech Stack:** Markdown. `python3` (stdlib only, plus this repo's `scripts/design_blocks.py`), `git`, `git grep`, `python3 scripts/check-sync.py`, `claude plugin validate .`. **There is no build, no linter, and no test framework in this repo (design A2) — do not run `pytest`, `npm test`, or `ruff`, and do not add one.** The design's `## Verification` section is the entire correctness surface.

**Authoritative source:** `docs/superpowers/specs/2026-08-02-gh-39-verification-rules-home-design.md`. Its two plain fenced blocks are the replacement text and its `## Verification` section holds all five checks (steps 0–4), carried into this plan verbatim as §V0–§V4. **If this plan and the design ever disagree, the design wins — stop and report.**

---

## Global Constraints

Every task's requirements implicitly include this section.

- **Repo root for this run (absolute):** `/Users/taylor/dev/claude-plugins`. **`cd` there before the first command of every task.** Every path in this plan that is not absolute is **repo-relative**, and every command is run from the repo root — that is what makes the design's `## Verification` commands runnable verbatim.
- **Branch `tayl0r/gh-39-verification-rules-home`. Work in place — do not create a git worktree, do not switch branches, do not rebase, do not push, do not open a PR, do not merge, do not invoke any review skill.** The pipeline owns all of those. Committing the edit *is* part of this plan (Task 1 ends with one commit of `CLAUDE.md` by exact path).
- **`§V0`, `§V1`, `§V2`, `§V3` and `§V4` are IDs of fenced blocks carried inside each task's own text.** `subagent-driven-development` briefs **one task at a time** and hands an implementer only the span under its own `## Task N` heading, so every task that runs a script carries that script under its own `### Verification scripts` subsection. A step that says *"Run §V2 … verbatim"* means: find the block carrying that ID in the task text you were given, and run it character for character from the repo root. Never reconstruct one from its expected output and never substitute an equivalent of your own. **If a block a step names is not in the text you were handed, stop and report** rather than improvising a check.
- **NEVER RETYPE EITHER BLOCK.** The design gives the two replacement passages as its only two plain (untagged) fenced blocks, shape `[1, 4]`. The applier obtains them from `read_blocks(DESIGN, [1, 4])`, reading the design **on disk**. Do **not** transcribe a block by hand, do **not** paste one from a chat message, do **not** use the `Edit` tool with a retyped `new_string`, and do **not** reconstruct one from the design's prose. **This plan deliberately contains no reference copy of either block** — a copy here would be one more thing to keep in step with the design and one more thing to be tempted to paste. Block 0 is 1 line of ~1100 characters carrying em dashes (`—`), an arrow (`→`), asterisk emphasis and a dozen backticked code spans; block 1's two bullets are the base line's own prescriptions moved byte-identically. These are precisely the strings a retype gets wrong, and §V2 exists to catch it.
- **The applier types zero bytes of block content.** The only string literals it types are three ASCII/plain guards reproduced verbatim from the design's *Verification* step 2 — `"**Always:**"`, `"**When the change has a design doc**"` and `"## Verifying a change"`. Those are **guards**, never sources: they are compared against, never written into the file.
- **Scope is exactly one file: `CLAUDE.md`.** Nothing else may appear in the branch diff beyond this run's own `docs/superpowers/` design and plan artifacts. Hard-excluded by the design's *Out of scope* — touching any of these is a **HALT and report**, not a judgment call: `plugins/`, `.claude-plugin/` and every `plugin.json`; `.claude-plugin/marketplace.json`; `scripts/` (including `design_blocks.py`, which is *used* and never modified, and `check-sync.py`); `CONTEXT.md`; `docs/adr/`; `.github/`; the `## Changing a plugin` heading itself; the **wording** of either prescription; and **every pre-existing file under `docs/superpowers/`** — meaning the prior records, four of which legitimately contain the phrase this edit removes. This run's own design doc is read-only input; this plan file takes checkbox ticks only.
- **NO VERSION BUMP.** `CLAUDE.md` sits outside `plugins/`, ships into no version-keyed cache, and is read at edit time rather than into any model invocation, so `CLAUDE.md`'s own bump rule does not fire (design A4, *Out of scope*). This is a conclusion, not a deferral. **If any step seems to need a version bump, that is a HALT — stop and report.** §V1's file-scope equality asserts it, because the reflex is to bump: a touched `plugin.json` appears in the changed set and fails the step by name.
- **The design doc is read-only input.** `docs/superpowers/specs/2026-08-02-gh-39-verification-rules-home-design.md` must end this work byte-identical to how it started. Expected blob hash — `git hash-object docs/superpowers/specs/2026-08-02-gh-39-verification-rules-home-design.md` → `809ca485a1ee5c515d2ef0de4181a762253887ae`. If it differs at a task's Step 1, **halt and report** — do not proceed and do not "fix" the design. Editing it would silently change what every conformance check compares against.
- **The base is always computed, never hardcoded:** `git merge-base origin/main HEAD`. It resolves to `0445fb983511fa3ca27badeb9e597b0b3b6ccb3f` today. **Every step that consumes it — the applier, §V1 and §V2 — computes it inside `python3` and passes it to `git` as an `argv` element, never through a shell** (design *Verification* preamble, A10). `git merge-base` writes nothing to stdout when it fails (exit 128 for an unresolvable `origin/main`; exit 1 with no message at all for histories sharing no ancestor), so in a shell an unquoted `$(…)` vanishes by word-splitting and degrades a base comparison into a working-tree-vs-index one — which, on a branch that commits per task, is empty and prints a pass token on an arbitrarily broken tree. `argv` has no word-splitting to exploit. **Do not rewrite any of these into a shell `&&` chain, and do not hardcode a SHA.** If `origin/main` is not fetchable, the step fails as one quotable line naming the command, its exit status and git's message — report that line; do not work around it.
- **Every inline `python3` script below is pure ASCII on purpose**, including its guard strings, so a mistyped copy fails loudly instead of passing. The *content* it moves is not ASCII — but you never type that content, `read_blocks` supplies it. **Copy each script exactly, character for character. Every heredoc fence is unindented on purpose: a `python3` heredoc indented under a list item is an `IndentationError`** (design *Verification* step 2).
- **No new files anywhere, including temp files inside the repo.** Every Python snippet runs as a heredoc piped to `python3 -`.
- **Never stage with `git add -A`, `git add .`, or `git commit -a`.** The one commit stages `CLAUDE.md` by exact path.
- **Text assertions use `git grep`, never bare `grep`** (design A7): under Claude Code's Bash tool bare `grep` is a ugrep-backed shell function whose output layout is not reliable for per-file assertions. Exact assertions are made in `python3`, where they are byte-exact.
- **`claude plugin validate .` exiting 0 with exactly 8 `No author information provided` warnings is a PASS** (design A3, `CLAUDE.md`). Warnings are not failures. Do not add author fields to silence them. §V4 asserts *both* halves, because either alone passes vacuously.
- **Line numbers in this plan are informational, never inputs.** The applier reconstructs the file from its merge-base blob and asserts the base still carries both prescription markers on line 9, so a base that moved fails loudly instead of editing the wrong line (design A1). If any script reports a line number other than the ones predicted here, **stop and report** rather than editing around it.
- **The applier is idempotent.** Re-running it after it has landed prints `already applied: …` and changes nothing, so a re-dispatched task is safe to run from its Step 1.
- **Every check here compares the working tree against a commit**, so every assertion works on uncommitted edits. You never need to commit in order to verify.

---

## File map

| Path (repo-relative) | Change | Lines | Task |
|---|---|---|---|
| `CLAUDE.md` | Line 9 replaced in full by design block 0; design block 1 plus one blank line inserted directly after line 12. | 29 → **34** | 1 |

No file is created, renamed, or deleted. No other file is modified. The two hunks are one atomic edit — see *Architecture*.

Post-edit shape, asserted by §V2 and confirmed by a dry run of the applier against base `0445fb9`:

| Line | Content |
|---|---|
| 9 | the rewritten mirror bullet (block 0) |
| 12 | the blank line closing `## Changing a plugin` (unmoved) |
| 13 | `## Verifying a change` |
| 14 | blank (block 1's own line 2) |
| 15 | the `**Always:**` bullet |
| 16 | the `**When the change has a design doc**` bullet |
| 17 | blank — **supplied by the insertion, not by the block** |
| 18 | `## Workflow` (was 13 at the base) |

## Design block map

The design holds **exactly two** plain (untagged) fenced blocks, shape `[1, 4]`. Every script below asserts that shape through `read_blocks` before using it, so the shape is the contract. Every other fence in the design carries an info string (`sh`, `text`) — that is what keeps this index stable. **Keep it that way.**

| Block | Design heading | Shape | Target | How the applier places it — types no block content |
|---|---|---|---|---|
| 0 | `### Block 0 — the complete new CLAUDE.md line 9` | 1 line, whole-line replace | `CLAUDE.md` line 9 | Positional: index `BULLET_I - 1` of the **base blob's** line list, guarded by the assertion that that base line carries both prescription markers. |
| 1 | `### Block 1 — the new ## Verifying a change section` | 4 lines, insertion | after `CLAUDE.md` line 12 | Positional: spliced in after index `ANCHOR_I` of the base blob's line list, followed by **one blank line the applier supplies** — the block carries no edge blank of its own (design *Block 1*). |

**The inserted span is exactly `block 1 + [""]`.** Do not add a blank line before the heading (line 12's own blank already separates it) and do not let a formatter trim or add one inside the fence. §V2 asserts the span.

---

## Task order and dependencies

- **Task 1** applies the edit and commits it. Its two hunks are one atomic deliverable and cannot be split into two tasks: §V2 asserts the final 34-line reconstruction, so a task delivering only one hunk would have no green check to end on (*Architecture*).
- **Task 2 depends on Task 1, committed.** It is the independent end-to-end sweep of the design's *Verification* steps 0–4 against the committed tree, run by an agent that did not make the edit. It modifies nothing.
- Execution is complete when zero `- [ ]` boxes remain unchecked.

---

## Task 1: Hoist the two prescriptions into `## Verifying a change` and rewrite the mirror bullet's tail

**Files:**
- Modify: `CLAUDE.md` (line 9 replaced; four lines plus one blank inserted after line 12 — 29 → 34 lines)
- Read-only input: `docs/superpowers/specs/2026-08-02-gh-39-verification-rules-home-design.md`, `scripts/design_blocks.py`
- Test: none — this repo has no test framework (design A2). §V2 is the test.

**Interfaces:**
- Consumes: nothing from an earlier task. Design blocks 0 and 1, obtained by `read_blocks(DESIGN, [1, 4])`.
- Produces: a committed `CLAUDE.md` that is 34 lines long, byte-identical to base `0445fb9`'s blob except that line 9 is design block 0 and design block 1 plus one blank line sits directly after line 12. Task 2 asserts exactly that.

**What changes:** one file, two hunks, one commit. Block 0 keeps the base line's head through *"must also verify against something \*outside\* the pair."* byte-identically and replaces everything after it with a forward pointer plus the one mirror-pair-specific reason. Block 1's lines 3 and 4 are the base line 9's two prescription spans, each prefixed with `- ` and otherwise byte-identical — that is what makes *moved, not rewritten* a machine-checked property rather than a reviewer's eye, and it is why **no wording may be improved in passing** (design *Rejected: rewriting the prescriptions while moving them*).

### Verification scripts

**Global Constraints bind this task.** If your dispatch did not include this plan's `## Global Constraints` section verbatim, report `NEEDS_CONTEXT` and ask for it before running Step 1 — do not proceed from the task text alone.

The design's *Verification* steps 0–4, carried here verbatim and given IDs. A step that says *"Run §V2 … verbatim"* means: find the block with that ID **in this task's own text above**, and run it character for character from the repo root. Do **not** retype one, do **not** reconstruct one from its expected output, and do **not** substitute an equivalent of your own — the whole point of §V2 is that it reads the design from disk. **If a block a step names is not in the text you were handed, stop and report** rather than improvising a check. All five are read-only and idempotent, so running one repeatedly is safe.

**Why each task carries its own copy.** `subagent-driven-development` hands an implementer only the span under its own `## Task N` heading — extracted by that skill's `scripts/task-brief`, whose `awk` prints nothing above `## Task 1` and stops at the next task heading. A single shared copy placed before the tasks reaches neither implementer, so **both tasks carry all five, byte-identically**. An edit to one copy is an edit to both.

**Why there is no separate residue step and no separate version-bump step.** Both are subsumed by §V1, and the design rules each out by name (*Verification* step 1). The phrase this edit removes is the junction `pair. **Always:**`, which at `0445fb9` sat in exactly one file outside `docs/superpowers/` — `CLAUDE.md`. §V1 asserts the changed set **equals** `['CLAUDE.md']` and §V2 pins that one file byte for byte against its base blob, so the phrase has nowhere to reappear: a standalone `git grep -F 'pair. **Always:**'` could not fail unless §V1 already had, and it would carry a pass condition no runner reads correctly, since `git grep` exits **1** on no match. The same argument retires a version-bump grep: a bumped `plugin.json` is a second path in §V1's changed set. **Do not add either check.** A criterion that cannot fail is one this repo's own shipped review tier is instructed to report.

#### §V0 — block shape, asserted rather than reported (design *Verification* step 0)

`design_blocks.py`'s CLI is a shape *reporter* that always exits 0; the *guard* is `read_blocks`, where the shape is a required argument and a mismatch is a `SystemExit`. This calls the guard. **The fence is unindented on purpose.**

```sh
python3 - <<'PY'
import sys
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
DESIGN = "docs/superpowers/specs/2026-08-02-gh-39-verification-rules-home-design.md"
for i, b in enumerate(read_blocks(DESIGN, [1, 4])):
    print("  [%d] len=%d: %s" % (i, len(b), b[0][:66]))
print("shape guard: OK")
PY
echo "exit=$?"
```

Expected, exactly — and this output was produced against this checkout while the plan was written:

```text
  [0] len=1: - **Some files are mirrored across `dev-flow` and `dev-flow-worktr
  [1] len=4: ## Verifying a change
shape guard: OK
exit=0
```

Anything else — in particular `design code-block shape is [...], want [1, 4]; stop and re-read the design` on stderr at `exit=1` — means the design was edited after this plan captured its shape. **Stop and report.** Do not "fix" the shape argument.

#### §V1 — file scope: exactly one file, and it is `CLAUDE.md` (design *Verification* step 1)

The `--name-only` set is compared for equality against the authorized list, so a stray edit to `plugins/`, a `plugin.json`, `scripts/`, `CONTEXT.md`, `docs/adr/` or `marketplace.json` fails the step **and names the offending path**. There is deliberately **no `--stat` line and no `--quiet` companion**: `--stat` asserts nothing, and a `--quiet` pathspec list over paths this equality already covers would pass vacuously. The `':!docs/superpowers/'` pathspec is required (design A9): this run's front matter is `docs: commit`, so its own design and plan are committed on this branch and an unfiltered diff necessarily reports them. **The base is computed inside the script and passed to `git` as an `argv` element — do not rewrite this as a shell `&&` chain and do not hardcode the base.** Pure ASCII, unindented fence — copy exactly.

```sh
python3 - <<'PY'
import subprocess, sys
SCOPE = ["--", ".", ":!docs/superpowers/"]
WANT = ["CLAUDE.md"]
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

Green expects a `base:` line carrying a 40-character SHA — `0445fb983511fa3ca27badeb9e597b0b3b6ccb3f` today — then `file scope: OK` and `exit=0`. Run against this checkout **before** the edit it printed:

```text
base: 0445fb983511fa3ca27badeb9e597b0b3b6ccb3f
file scope: FAIL -- changed [], want ['CLAUDE.md']
exit=1
```

A `file scope: FAIL` line naming any path other than `CLAUDE.md` means something outside the authorized set moved → **stop and report**, and if it is a version bump, revert it. A base that cannot be computed fails as one quotable line — `FAILED: git merge-base origin/main HEAD -- exit 1, (no message)` for histories sharing no ancestor, where git itself says nothing.

#### §V2 — reconstruction, design conformance, and the hoist is verbatim (design *Verification* step 2)

This is the check `CLAUDE.md` requires, and it is the one that proves the whole edit. One program, three families of assertion, nothing retyped on either side:

- `CLAUDE.md` is **byte-for-byte its merge-base blob with exactly the intended edit applied** — line 9 replaced by block 0, and block 1 plus one blank line inserted after line 12 — which is what proves no other line moved;
- both blocks are read **from the design on disk** through the shared reader, never retyped, and block 0 occurs exactly once in the file;
- the two prescription spans are extracted **from the base blob** with `partition` and asserted equal to the new section's two bullets, byte for byte — the machine-checkable form of *moved, not rewritten* — while block 0 is asserted to start with the base line's head and to contain neither prescription marker any more.

Both markers are located with `partition`, so a base whose line 9 lost either one reports `MISMATCH:` and exits 1 like every other failure path rather than raising — **do not rewrite either `partition` into `.index`**. Failures of the *producers* (`git`, `read_blocks`) are deliberately left to raise as themselves: they name the failing command, and no traceback can be mistaken for a pass. **The fence is unindented on purpose.**

```sh
python3 - <<'PY'
import subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-02-gh-39-verification-rules-home-design.md"
TARGET = "CLAUDE.md"
BULLET_I, ANCHOR_I = 9, 12          # 1-based, at the base
WANT_LEN = 34                       # after the edit
HEADING = "## Verifying a change"
ALWAYS = "**Always:**"
WHEN = "**When the change has a design doc**"

def git(*args):
    return subprocess.run(("git",) + args, capture_output=True, text=True,
                          check=True).stdout
def split(text):
    out = text.split("\n")
    if out and out[-1] == "":
        out.pop()
    return out
base = git("merge-base", "origin/main", "HEAD").strip()
old = split(git("show", base + ":" + TARGET))
new = split(Path(TARGET).read_text(encoding="utf-8"))
blocks = read_blocks(DESIGN, [1, 4])
b0, sec = blocks[0][0], blocks[1]
bad = []

expected = (old[:BULLET_I - 1] + [b0] + old[BULLET_I:ANCHOR_I] + sec + [""] + old[ANCHOR_I:])
if new != expected:
    bad.append("%s is not its base blob with line %d replaced by block 0 and block 1"
               " plus one blank line inserted directly after line %d"
               % (TARGET, BULLET_I, ANCHOR_I))
if len(new) != WANT_LEN:
    bad.append("%s is %d lines, want %d" % (TARGET, len(new), WANT_LEN))
if new.count(b0) != 1:
    bad.append("%s holds block 0 %d times, want exactly 1" % (TARGET, new.count(b0)))

o9 = old[BULLET_I - 1]
head, m1, rest = o9.partition(ALWAYS)
mid, m2, tail = rest.partition(WHEN)
if not m1 or not m2:
    bad.append("base line %d does not carry both %r and %r -- the base moved"
               % (BULLET_I, ALWAYS, WHEN))
else:
    if sec[2] != "- " + (m1 + mid).rstrip():
        bad.append("the Always: bullet is not the base prescription moved verbatim")
    if sec[3] != "- " + m2 + tail:
        bad.append("the design-doc bullet is not the base prescription moved verbatim")
    if not b0.startswith(head):
        bad.append("block 0 changes text before %r; the hoist must keep the bullet's head"
                   % ALWAYS)
    if ALWAYS in b0 or WHEN in b0:
        bad.append("block 0 still carries a prescription marker; the hoist left a copy behind")

if sec[0] != HEADING:
    bad.append("block 1 line 1 is %r, want %r" % (sec[0], HEADING))
if sec[1] != "":
    bad.append("block 1's blank line moved; the section shape is not heading/blank"
               "/bullet/bullet")

for why in bad:
    print("MISMATCH:", why)
print("reconstruction:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Green expects exactly `reconstruction: OK` and `exit=0`, and nothing else. Run against this checkout **before** the edit it printed:

```text
MISMATCH: CLAUDE.md is not its base blob with line 9 replaced by block 0 and block 1 plus one blank line inserted directly after line 12
MISMATCH: CLAUDE.md is 29 lines, want 34
MISMATCH: CLAUDE.md holds block 0 0 times, want exactly 1
reconstruction: FAIL
exit=1
```

Those are the only three of the program's ten assertions that read the **post-edit tree**; the other seven compare the design's blocks against the base blob or against each other and are green before the edit and after it. Any `MISMATCH:` line other than those three, at any point, is a **stop and report**. If the shape guard trips instead (`design code-block shape is …`), **stop and report**: the design was edited after this plan captured its shape.

#### §V3 — `check-sync.py` (design *Verification* step 3)

A regression guard, not a claim about the edit: `check-sync.py` reads none of the changed files. `.claude-plugin/marketplace.json` is untouched, so Check A is unaffected, and Check B's mirror pair is not in this change at all.

```sh
python3 scripts/check-sync.py
echo "exit=$?"
```

Expected, exactly — produced against this checkout while the plan was written, and identical before and after the change:

```text
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)
check-sync: all checks passed
exit=0
```

#### §V4 — `claude plugin validate .`, exit 0 **and** exactly 8 author warnings (design *Verification* step 4)

Both halves are asserted, because either alone passes vacuously: the command exits 0 while emitting warnings (design A3), and a count assertion alone would pass on a run that errored out. **Do not "fix" the warnings** — they are the documented pass state. Pure ASCII, unindented fence.

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

Expected, exactly — produced against this checkout while the plan was written:

```text
claude plugin validate: exit 0, 8 author warnings
validate: OK
exit=0
```

### Steps

- [x] **Step 1: Confirm the starting state**

```sh
cd /Users/taylor/dev/claude-plugins
git rev-parse --abbrev-ref HEAD
git status --porcelain
git grep -c '' -- CLAUDE.md
git hash-object docs/superpowers/specs/2026-08-02-gh-39-verification-rules-home-design.md
```

Expected:

- `tayl0r/gh-39-verification-rules-home`.
- `git status --porcelain` prints nothing except, possibly, a **modified or untracked** `docs/superpowers/plans/2026-08-02-gh-39-verification-rules-home-plan.md` (this plan's own checkbox ticks; it may be untracked until the pipeline commits it). Any other modified or untracked path → **halt and report**: the tree is not in the state this plan was written against.
- `CLAUDE.md:29`.
- `809ca485a1ee5c515d2ef0de4181a762253887ae`. **Any other value → halt and report "design doc modified".**

- [x] **Step 2: Run §V0 — the block shape guard**

Run **§V0** from *Verification scripts* above, verbatim.

Expected, exactly:

```text
  [0] len=1: - **Some files are mirrored across `dev-flow` and `dev-flow-worktr
  [1] len=4: ## Verifying a change
shape guard: OK
exit=0
```

Anything else → **stop and report**. Every later step indexes off this shape.

- [x] **Step 3: Run §V2 and watch it FAIL (red)**

Run **§V2** from *Verification scripts* above, verbatim. This is the design's *Verification* step 2, run before the edit so you can watch it discriminate.

Expected, exactly:

```text
MISMATCH: CLAUDE.md is not its base blob with line 9 replaced by block 0 and block 1 plus one blank line inserted directly after line 12
MISMATCH: CLAUDE.md is 29 lines, want 34
MISMATCH: CLAUDE.md holds block 0 0 times, want exactly 1
reconstruction: FAIL
exit=1
```

Three MISMATCH lines and no more. If you see `reconstruction: OK`, the edit is already applied — skip to Step 6. Any **fourth** MISMATCH line means one of the seven base-side or block-side assertions is failing, which the tree cannot cause → **stop and report**; the design or the base moved.

- [x] **Step 4: Run §V1 and watch it FAIL (red)**

Run **§V1** from *Verification scripts* above, verbatim.

Expected, exactly:

```text
base: 0445fb983511fa3ca27badeb9e597b0b3b6ccb3f
file scope: FAIL -- changed [], want ['CLAUDE.md']
exit=1
```

`changed []` is the pre-edit state: nothing outside `docs/superpowers/` has moved yet. If `changed` already lists `CLAUDE.md`, the edit is applied — skip to Step 6. If it lists **any other path**, something outside the authorized set is already modified → **halt and report**.

- [x] **Step 5: Apply both hunks with the applier**

Reads both blocks from the design **on disk** through the shared reader and reconstructs `CLAUDE.md` from its **merge-base blob** — it does not patch the working tree, which is what makes it byte-exact and idempotent. It types **no byte of block content**: the only literals are the three ASCII/plain guards `"**Always:**"`, `"**When the change has a design doc**"` and `"## Verifying a change"`, reproduced verbatim from §V2 and only ever compared against. It refuses to write unless the working tree is either already the intended result or byte-identical to the base blob, so it can never silently clobber someone else's edit. The trailing newline is carried over from the base blob's raw bytes rather than reconstructed, so the file's final byte is unchanged. **Unindented fence, pure ASCII — copy exactly.**

```sh
python3 - <<'PY'
import subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-02-gh-39-verification-rules-home-design.md"
TARGET = "CLAUDE.md"
BULLET_I, ANCHOR_I = 9, 12          # 1-based, at the base
HEADING = "## Verifying a change"
ALWAYS = "**Always:**"
WHEN = "**When the change has a design doc**"

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
raw_old = git("show", base + ":" + TARGET)
old = split(raw_old)
blocks = read_blocks(DESIGN, [1, 4])
b0, sec = blocks[0][0], blocks[1]
o9 = old[BULLET_I - 1]
if ALWAYS not in o9 or WHEN not in o9:
    raise SystemExit("base line %d does not carry both prescription markers; the base moved"
                     " -- stop and re-read the design" % BULLET_I)
if sec[0] != HEADING or sec[1] != "":
    raise SystemExit("block 1 is not heading/blank/bullet/bullet; stop and re-read the design")
expected = old[:BULLET_I - 1] + [b0] + old[BULLET_I:ANCHOR_I] + sec + [""] + old[ANCHOR_I:]
raw_new = "\n".join(expected) + ("\n" if raw_old.endswith("\n") else "")
raw_cur = Path(TARGET).read_text(encoding="utf-8")
if raw_cur == raw_new:
    print("already applied: %s is %d lines" % (TARGET, len(expected)))
    sys.exit(0)
if raw_cur != raw_old:
    raise SystemExit("%s is neither its base blob nor the intended result; something else"
                     " edited it -- stop and report" % TARGET)
Path(TARGET).write_text(raw_new, encoding="utf-8")
print("applied: %s, %d -> %d lines" % (TARGET, len(old), len(expected)))
PY
echo "exit=$?"
```

Expected: `applied: CLAUDE.md, 29 -> 34 lines` and `exit=0` (or `already applied: CLAUDE.md is 34 lines` if re-run). This exact output was produced by a dry run of the same program against base `0445fb9` while the plan was written, writing to a scratch path outside the repo. Any `SystemExit` message is a **stop and report** — do not hand-patch `CLAUDE.md` to satisfy it, and never fall back to the `Edit` tool with retyped text.

- [x] **Step 6: Run §V2 and watch it PASS (green)**

Run **§V2** from *Verification scripts* above, verbatim — the same characters as in Step 3.

Expected, exactly:

```text
reconstruction: OK
exit=0
```

and nothing else. This was confirmed green while the plan was written, by running §V2 with `new` read from the applier's dry-run output instead of from `CLAUDE.md`. This is the `CLAUDE.md`-mandated design-sourced check going green, and it is simultaneously this repo's own `Always:` rule run on the change that relocates it: the file is proved to be its merge-base blob with exactly the intended edit applied, both blocks proved to have come from the design on disk, and both hoisted bullets proved byte-identical to the base's prescription spans. Any `MISMATCH:` line is a **stop and report** — do not hand-patch `CLAUDE.md` to satisfy it; re-read the applier's output instead.

- [x] **Step 7: Run §V1 and watch it PASS (green)**

Run **§V1** from *Verification scripts* above, verbatim.

Expected, exactly:

```text
base: 0445fb983511fa3ca27badeb9e597b0b3b6ccb3f
file scope: OK
exit=0
```

Exactly one file changed, and it is not a plugin file. This is also the removed-phrase grep in its stronger form: the junction `pair. **Always:**` sat in exactly one file outside `docs/superpowers/`, and §V1 plus §V2 together leave it nowhere to reappear (*Verification scripts* preamble). A `file scope: FAIL` line names the changed set it found; any path in it other than `CLAUDE.md` → **stop and report**, and if it is a version bump, revert it.

- [x] **Step 8: Run §V3 — `check-sync.py` regression guard**

Run **§V3** from *Verification scripts* above, verbatim.

Expected, exactly:

```text
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)
check-sync: all checks passed
exit=0
```

Identical to before the change. Any difference means a mirrored file or a manifest `description` moved → **stop and report**.

- [x] **Step 9: Run §V4 — `claude plugin validate .`, before committing**

Run **§V4** from *Verification scripts* above, verbatim. `CLAUDE.md` says to validate before committing, which is why this runs here and not only in Task 2.

Expected, exactly:

```text
claude plugin validate: exit 0, 8 author warnings
validate: OK
exit=0
```

The 8 warnings are the pass state (design A3). A `MISMATCH:` line → **stop and report**; do not add author fields.

- [x] **Step 10: Commit**

Stage by exact path — never `git add -A`.

```sh
git add CLAUDE.md
git commit -m "CLAUDE.md: give the verification rules a repo-wide home (#39)"
git show --stat --format=%s HEAD
```

Expected: the commit succeeds and `git show --stat` lists **exactly one** file, `CLAUDE.md`, with **6 insertions and 1 deletion** (measured by diffing the applier's dry-run output against the base while the plan was written). Any second path means something outside the authorized set was staged → **halt and report**. **A differing count is also a halt**, because this is the plan's only *byte-level* comparison: §V2 reads both sides in Python text mode and compares line lists, so a stripped final newline (`split()` pops a lone trailing empty string from either side) and a line-ending change (`read_text()` and `subprocess.run(..., text=True)` both translate `\r\n` to `\n` first) are invisible to it — run verbatim on each it still prints `reconstruction: OK` at `exit=0`, while `git` reports them here as `7 insertions(+), 2 deletions(-)` and `34 insertions(+), 29 deletions(-)`. §V1's *"`--stat` asserts nothing"* is a claim about **file scope**, which is all §V1 asks of it; these counts are asserted. Neither deviation is reachable through this plan — the applier is the only writer and carries the base blob's final byte over verbatim — so this guards a hand-edit the plan already forbids; the underlying gap is filed as **#55** and is not fixed here. Do not push, do not open a PR, do not merge — the pipeline owns those.

---

## Task 2: Full `Verification` sweep — all five steps green on the committed tree

**Depends on:** Task 1, committed.

**Files:** none modified. This task is verification only, and it is the whole correctness surface (design A2 — no test framework exists).

**Interfaces:**
- Consumes: the committed result of Task 1.
- Produces: a pass/fail verdict on every step of the design's `## Verification`, steps 0 through 4.

**Nothing in this task edits a file. If a check fails, stop and report — do not repair by editing the file the check names.** This sweep is deliberately run by an agent that did not make the edit: with no test suite in this repo, an independent re-run of every criterion against the committed tree is the only evidence that the change is what it claims to be.

### Verification scripts

**Global Constraints bind this task.** If your dispatch did not include this plan's `## Global Constraints` section verbatim, report `NEEDS_CONTEXT` and ask for it before running Step 1 — do not proceed from the task text alone.

The design's *Verification* steps 0–4, carried here verbatim and given IDs. A step that says *"Run §V2 … verbatim"* means: find the block with that ID **in this task's own text above**, and run it character for character from the repo root. Do **not** retype one, do **not** reconstruct one from its expected output, and do **not** substitute an equivalent of your own — the whole point of §V2 is that it reads the design from disk. **If a block a step names is not in the text you were handed, stop and report** rather than improvising a check. All five are read-only and idempotent, so running one repeatedly is safe.

**Why each task carries its own copy.** `subagent-driven-development` hands an implementer only the span under its own `## Task N` heading — extracted by that skill's `scripts/task-brief`, whose `awk` prints nothing above `## Task 1` and stops at the next task heading. A single shared copy placed before the tasks reaches neither implementer, so **both tasks carry all five, byte-identically**. An edit to one copy is an edit to both.

**Why there is no separate residue step and no separate version-bump step.** Both are subsumed by §V1, and the design rules each out by name (*Verification* step 1). The phrase this edit removes is the junction `pair. **Always:**`, which at `0445fb9` sat in exactly one file outside `docs/superpowers/` — `CLAUDE.md`. §V1 asserts the changed set **equals** `['CLAUDE.md']` and §V2 pins that one file byte for byte against its base blob, so the phrase has nowhere to reappear: a standalone `git grep -F 'pair. **Always:**'` could not fail unless §V1 already had, and it would carry a pass condition no runner reads correctly, since `git grep` exits **1** on no match. The same argument retires a version-bump grep: a bumped `plugin.json` is a second path in §V1's changed set. **Do not add either check.** A criterion that cannot fail is one this repo's own shipped review tier is instructed to report.

#### §V0 — block shape, asserted rather than reported (design *Verification* step 0)

`design_blocks.py`'s CLI is a shape *reporter* that always exits 0; the *guard* is `read_blocks`, where the shape is a required argument and a mismatch is a `SystemExit`. This calls the guard. **The fence is unindented on purpose.**

```sh
python3 - <<'PY'
import sys
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
DESIGN = "docs/superpowers/specs/2026-08-02-gh-39-verification-rules-home-design.md"
for i, b in enumerate(read_blocks(DESIGN, [1, 4])):
    print("  [%d] len=%d: %s" % (i, len(b), b[0][:66]))
print("shape guard: OK")
PY
echo "exit=$?"
```

Expected, exactly — and this output was produced against this checkout while the plan was written:

```text
  [0] len=1: - **Some files are mirrored across `dev-flow` and `dev-flow-worktr
  [1] len=4: ## Verifying a change
shape guard: OK
exit=0
```

Anything else — in particular `design code-block shape is [...], want [1, 4]; stop and re-read the design` on stderr at `exit=1` — means the design was edited after this plan captured its shape. **Stop and report.** Do not "fix" the shape argument.

#### §V1 — file scope: exactly one file, and it is `CLAUDE.md` (design *Verification* step 1)

The `--name-only` set is compared for equality against the authorized list, so a stray edit to `plugins/`, a `plugin.json`, `scripts/`, `CONTEXT.md`, `docs/adr/` or `marketplace.json` fails the step **and names the offending path**. There is deliberately **no `--stat` line and no `--quiet` companion**: `--stat` asserts nothing, and a `--quiet` pathspec list over paths this equality already covers would pass vacuously. The `':!docs/superpowers/'` pathspec is required (design A9): this run's front matter is `docs: commit`, so its own design and plan are committed on this branch and an unfiltered diff necessarily reports them. **The base is computed inside the script and passed to `git` as an `argv` element — do not rewrite this as a shell `&&` chain and do not hardcode the base.** Pure ASCII, unindented fence — copy exactly.

```sh
python3 - <<'PY'
import subprocess, sys
SCOPE = ["--", ".", ":!docs/superpowers/"]
WANT = ["CLAUDE.md"]
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

Green expects a `base:` line carrying a 40-character SHA — `0445fb983511fa3ca27badeb9e597b0b3b6ccb3f` today — then `file scope: OK` and `exit=0`. Run against this checkout **before** the edit it printed:

```text
base: 0445fb983511fa3ca27badeb9e597b0b3b6ccb3f
file scope: FAIL -- changed [], want ['CLAUDE.md']
exit=1
```

A `file scope: FAIL` line naming any path other than `CLAUDE.md` means something outside the authorized set moved → **stop and report**, and if it is a version bump, revert it. A base that cannot be computed fails as one quotable line — `FAILED: git merge-base origin/main HEAD -- exit 1, (no message)` for histories sharing no ancestor, where git itself says nothing.

#### §V2 — reconstruction, design conformance, and the hoist is verbatim (design *Verification* step 2)

This is the check `CLAUDE.md` requires, and it is the one that proves the whole edit. One program, three families of assertion, nothing retyped on either side:

- `CLAUDE.md` is **byte-for-byte its merge-base blob with exactly the intended edit applied** — line 9 replaced by block 0, and block 1 plus one blank line inserted after line 12 — which is what proves no other line moved;
- both blocks are read **from the design on disk** through the shared reader, never retyped, and block 0 occurs exactly once in the file;
- the two prescription spans are extracted **from the base blob** with `partition` and asserted equal to the new section's two bullets, byte for byte — the machine-checkable form of *moved, not rewritten* — while block 0 is asserted to start with the base line's head and to contain neither prescription marker any more.

Both markers are located with `partition`, so a base whose line 9 lost either one reports `MISMATCH:` and exits 1 like every other failure path rather than raising — **do not rewrite either `partition` into `.index`**. Failures of the *producers* (`git`, `read_blocks`) are deliberately left to raise as themselves: they name the failing command, and no traceback can be mistaken for a pass. **The fence is unindented on purpose.**

```sh
python3 - <<'PY'
import subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-02-gh-39-verification-rules-home-design.md"
TARGET = "CLAUDE.md"
BULLET_I, ANCHOR_I = 9, 12          # 1-based, at the base
WANT_LEN = 34                       # after the edit
HEADING = "## Verifying a change"
ALWAYS = "**Always:**"
WHEN = "**When the change has a design doc**"

def git(*args):
    return subprocess.run(("git",) + args, capture_output=True, text=True,
                          check=True).stdout
def split(text):
    out = text.split("\n")
    if out and out[-1] == "":
        out.pop()
    return out
base = git("merge-base", "origin/main", "HEAD").strip()
old = split(git("show", base + ":" + TARGET))
new = split(Path(TARGET).read_text(encoding="utf-8"))
blocks = read_blocks(DESIGN, [1, 4])
b0, sec = blocks[0][0], blocks[1]
bad = []

expected = (old[:BULLET_I - 1] + [b0] + old[BULLET_I:ANCHOR_I] + sec + [""] + old[ANCHOR_I:])
if new != expected:
    bad.append("%s is not its base blob with line %d replaced by block 0 and block 1"
               " plus one blank line inserted directly after line %d"
               % (TARGET, BULLET_I, ANCHOR_I))
if len(new) != WANT_LEN:
    bad.append("%s is %d lines, want %d" % (TARGET, len(new), WANT_LEN))
if new.count(b0) != 1:
    bad.append("%s holds block 0 %d times, want exactly 1" % (TARGET, new.count(b0)))

o9 = old[BULLET_I - 1]
head, m1, rest = o9.partition(ALWAYS)
mid, m2, tail = rest.partition(WHEN)
if not m1 or not m2:
    bad.append("base line %d does not carry both %r and %r -- the base moved"
               % (BULLET_I, ALWAYS, WHEN))
else:
    if sec[2] != "- " + (m1 + mid).rstrip():
        bad.append("the Always: bullet is not the base prescription moved verbatim")
    if sec[3] != "- " + m2 + tail:
        bad.append("the design-doc bullet is not the base prescription moved verbatim")
    if not b0.startswith(head):
        bad.append("block 0 changes text before %r; the hoist must keep the bullet's head"
                   % ALWAYS)
    if ALWAYS in b0 or WHEN in b0:
        bad.append("block 0 still carries a prescription marker; the hoist left a copy behind")

if sec[0] != HEADING:
    bad.append("block 1 line 1 is %r, want %r" % (sec[0], HEADING))
if sec[1] != "":
    bad.append("block 1's blank line moved; the section shape is not heading/blank"
               "/bullet/bullet")

for why in bad:
    print("MISMATCH:", why)
print("reconstruction:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Green expects exactly `reconstruction: OK` and `exit=0`, and nothing else. Run against this checkout **before** the edit it printed:

```text
MISMATCH: CLAUDE.md is not its base blob with line 9 replaced by block 0 and block 1 plus one blank line inserted directly after line 12
MISMATCH: CLAUDE.md is 29 lines, want 34
MISMATCH: CLAUDE.md holds block 0 0 times, want exactly 1
reconstruction: FAIL
exit=1
```

Those are the only three of the program's ten assertions that read the **post-edit tree**; the other seven compare the design's blocks against the base blob or against each other and are green before the edit and after it. Any `MISMATCH:` line other than those three, at any point, is a **stop and report**. If the shape guard trips instead (`design code-block shape is …`), **stop and report**: the design was edited after this plan captured its shape.

#### §V3 — `check-sync.py` (design *Verification* step 3)

A regression guard, not a claim about the edit: `check-sync.py` reads none of the changed files. `.claude-plugin/marketplace.json` is untouched, so Check A is unaffected, and Check B's mirror pair is not in this change at all.

```sh
python3 scripts/check-sync.py
echo "exit=$?"
```

Expected, exactly — produced against this checkout while the plan was written, and identical before and after the change:

```text
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)
check-sync: all checks passed
exit=0
```

#### §V4 — `claude plugin validate .`, exit 0 **and** exactly 8 author warnings (design *Verification* step 4)

Both halves are asserted, because either alone passes vacuously: the command exits 0 while emitting warnings (design A3), and a count assertion alone would pass on a run that errored out. **Do not "fix" the warnings** — they are the documented pass state. Pure ASCII, unindented fence.

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

Expected, exactly — produced against this checkout while the plan was written:

```text
claude plugin validate: exit 0, 8 author warnings
validate: OK
exit=0
```

### Steps

- [x] **Step 1: Confirm the tree is clean, the edit is committed, and the design doc is intact**

```sh
cd /Users/taylor/dev/claude-plugins
git status --porcelain
git log --oneline -1
git grep -c '' -- CLAUDE.md
git hash-object docs/superpowers/specs/2026-08-02-gh-39-verification-rules-home-design.md
```

Expected: `git status --porcelain` prints nothing except, possibly, a modified or untracked `docs/superpowers/plans/2026-08-02-gh-39-verification-rules-home-plan.md` (this plan's own checkbox ticks); the newest commit's subject is `CLAUDE.md: give the verification rules a repo-wide home (#39)`; `CLAUDE.md:34`; and `809ca485a1ee5c515d2ef0de4181a762253887ae` — **any other hash means the implementation modified the design doc → halt and report.** If `CLAUDE.md:29`, Task 1 has not landed — **halt and report** rather than running Task 1's applier from here.

- [x] **Step 2: Design *Verification* step 0 — block shape**

Run **§V0** from *Verification scripts* above, verbatim.

Expected, exactly:

```text
  [0] len=1: - **Some files are mirrored across `dev-flow` and `dev-flow-worktr
  [1] len=4: ## Verifying a change
shape guard: OK
exit=0
```

- [x] **Step 3: Design *Verification* step 1 — file scope**

Run **§V1** from *Verification scripts* above, verbatim.

Expected, exactly:

```text
base: 0445fb983511fa3ca27badeb9e597b0b3b6ccb3f
file scope: OK
exit=0
```

and no other line. Exactly one file changed, it is `CLAUDE.md`, and no `plugin.json` version moved.

- [x] **Step 4: Design *Verification* step 2 — reconstruction, design conformance, verbatim hoist**

Run **§V2** from *Verification scripts* above, verbatim.

Expected, exactly:

```text
reconstruction: OK
exit=0
```

- [x] **Step 5: Design *Verification* step 3 — `check-sync.py`**

Run **§V3** from *Verification scripts* above, verbatim.

Expected, exactly:

```text
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)
check-sync: all checks passed
exit=0
```

- [x] **Step 6: Design *Verification* step 4 — `claude plugin validate .`**

Run **§V4** from *Verification scripts* above, verbatim.

Expected, exactly:

```text
claude plugin validate: exit 0, 8 author warnings
validate: OK
exit=0
```

- [x] **Step 7: Record the verdict**

Every row must be green:

| Design *Verification* step | ID | Assertion | Where run |
|---|---|---|---|
| 0 | §V0 | `shape guard: OK`, block 0 the mirrored-files bullet, block 1 `## Verifying a change` | Task 1 Step 2; Task 2 Step 2 |
| 1 | §V1 | `base:` + 40-char SHA, `file scope: OK`, `exit=0` | Task 1 Step 4 (red) and Step 7; Task 2 Step 3 |
| 2 | §V2 | `reconstruction: OK`, `exit=0`, no `MISMATCH:` line | Task 1 Step 3 (red) and Step 6; Task 2 Step 4 |
| 3 | §V3 | `check-sync: all checks passed`, `exit=0` | Task 1 Step 8; Task 2 Step 5 |
| 4 | §V4 | `validate: OK`, exit 0, exactly 8 author warnings | Task 1 Step 9; Task 2 Step 6 |

Together, §V1 and §V2 pin the change completely: exactly one file changed, and every one of its 34 lines is either byte-identical to the base blob or came from the design's two blocks read fresh from disk. Report the verdict with the actual output you saw for each step. **Do not open a PR, close issues, file follow-ups, push, merge, or run any review skill** — those are the pipeline's steps.

---

## Not part of this implementation

Recorded so a fresh implementer does not helpfully do them.

- **Closing #39.** Not a no-change ruling — it ships text and closes on merge, and the design's `## PR` section is the PR body, which carries the ruling. There is no separate issue-close comment to write (design A5). The pipeline writes the PR.
- **#54** — *"dev-flow: the removed-phrase grep is the one CLAUDE.md verification rule that names no instrument, and it has no pipeline-general statement"* — is **already filed and open**. It is the severable half of the `Always:` pair, and its only available shape is an **additive echo** into `plugins/` beside the two properties `0445fb9` landed. It would add to `plugins/` rather than remove from `CLAUDE.md`, so it changes this edit byte-for-byte not at all (design ground 4). Do not implement it here and do not re-file it.
- **Editing `scripts/design_blocks.py`.** Its docstring already claims the wider scope; this hoist makes that claim true with no edit (design A6). It is *used* by §V0 and §V2 and never modified.
- **Strengthening §V2.** It is byte-identical to the design's *Verification* step 2 — all five of §V0–§V4 are — and the design is authoritative, so editing one here is plan-vs-design drift, not a fix. Its line-list comparison cannot see a stripped final newline or a line-ending change; **#55** carries that upstream and Task 1 Step 10's counts cover it for this change. Do not rewrite the script, do not add a trailing-byte assertion beside it, and do not re-file the issue.
- **Pushing, opening the PR, reviewing, merging, filing follow-ups.**

Hard-excluded by the design's *Out of scope* — a proposal to touch any of these is a blocker, not a task: `plugins/`, `.claude-plugin/` and every `plugin.json` (**no version is bumped**; option 3 is rejected on the merits, not deferred); `scripts/` (both files); `CONTEXT.md` (this change coins no repo concept — *Mirror pair* and *Hand-mirrored pair* already exist and block 0 uses both in exactly that sense; *verification*, *check* and *prescription* are ordinary vocabulary); `docs/adr/` (no ADR is warranted); `.claude-plugin/marketplace.json` (no `description` changes); `.github/` (no CI change); the `## Changing a plugin` heading (not renamed — the five bullets that remain are all genuinely plugin-scoped); the **wording** of either prescription (moved byte-identically, which is what makes §V2's *moved, not rewritten* assertion possible); and every pre-existing file under `docs/superpowers/`.

## Plan self-review

- **Spec coverage.** *Block 0* and *Block 1* → Task 1 Step 5, one atomic applier. *The edit* (shape `[1, 4]`, both blocks produced from the base blob, never retyped) → *Design block map* plus the retype constraint. *Verification* steps 0–4 → §V0–§V4, each run at least twice per the Task 2 Step 7 table; steps 0–2 additionally run red before the edit so each is watched discriminating. *The phrase this edit removes* → the *Verification scripts* preamble, which records why §V1 subsumes the residue grep rather than a standalone step being added. *Length* (29 → 34) → *File map* and §V2's `WANT_LEN`. *Out of scope* → Global Constraints plus *Not part of this implementation*. A1 → the applier reconstructs from the base blob and guards on the markers, not on line numbers. A2 → Tech Stack. A3 → §V4. A4 → the NO VERSION BUMP constraint, asserted by §V1. A5, A6 → *Not part of this implementation*. A7 → the `git grep` constraint. A8 → §V0 is run first in both tasks and halts on a shape change. A9 → §V1's `':!docs/superpowers/'` pathspec. A10 → §V1's loud `git()` helper, reused by the applier.
- **Placeholder scan.** No TBDs. Every command carries its expected output; every Python snippet is complete and runnable as written. Every red expectation quoted here was produced by running the check against this checkout at base `0445fb9`; §V3's and §V4's green output likewise; §V0's green likewise; the applier's `applied: CLAUDE.md, 29 -> 34 lines` and §V2's `reconstruction: OK` were produced by a dry run that wrote the reconstructed file to a scratch path **outside** the repo and pointed §V2 at it, since a real green requires the edit to exist. The `6 insertions(+), 1 deletion(-)` in Task 1 Step 10 came from diffing that dry-run output against `CLAUDE.md`; its two **failing** counts, `7 insertions(+), 2 deletions(-)` and `34 insertions(+), 29 deletions(-)`, came from a scratch clone outside the repo where the applier was run and the result then had its final newline stripped and, separately, was converted to CRLF — §V2 was run verbatim on both and printed `reconstruction: OK` at `exit=0`, which is why Step 10 asserts its counts and §V2 is not asked to. Every scratch artifact was deleted afterwards.
- **Retype check — the single most important property.** No step in this plan reproduces block 0 or block 1, in whole or in part, and this plan contains no reference copy of either. The applier obtains its bytes from `read_blocks(DESIGN, [1, 4])` and writes them unmodified. The only literals typed anywhere near the blocks are three guards — `"**Always:**"`, `"**When the change has a design doc**"` and `"## Verifying a change"` — each reproduced verbatim from the design's *Verification* step 2, each compared against and never written. A wrong guard cannot corrupt `CLAUDE.md`: it makes the applier raise `SystemExit` before writing, or makes §V2 report `MISMATCH:`.
- **No vacuous criteria.** A standalone residue grep and a standalone version-bump grep were both considered and both refused, on the design's own step-1 reasoning: §V1's set **equality** plus §V2's byte-for-byte pin already imply each, so a separate check could not fail unless one of those had — and `git grep` exits 1 on no match, which is the pass condition a runner most often reads backwards. The *Verification scripts* preamble records this so a reviewer does not read the absence as an oversight.
- **Duplication.** §V0–§V4 have exactly **two** copies each — one under `## Task 1`, one under `## Task 2` — and the two are byte-identical. That is deliberate and it is the only reachable shape: `subagent-driven-development`'s `scripts/task-brief` extracts one task's span and prints nothing from outside it, so a single shared copy above `## Task 1` reaches no implementer at all. Within a task the ID device still holds — Task 1's §V2 red run (Step 3) and green run (Step 6) are literally the same characters. The two copies are this plan's own mirrored pair, and the check outside the pair is `task-brief <plan> N` for N in 1, 2: each brief must contain every block its steps name.
- **Task right-sizing.** Two tasks, and the boundary is real: Task 1's deliverable is the committed edit, Task 2's is an independent verdict from an agent that did not make it. The edit itself is **not** split in two, because §V2 asserts the final 34-line reconstruction and a one-hunk task would have no green state to end on — the failure mode the gh-32/33 plan accepted (a task ending on an expected `FAIL`) is avoidable here and is avoided.
- **Type consistency.** `DESIGN`, `TARGET`, `BULLET_I`, `ANCHOR_I`, `HEADING`, `ALWAYS`, `WHEN`, `b0`, `sec`, `old`, `new`, `expected`, `split()` and the `git()` helper mean the same thing in the applier and in §V2. `read_blocks(DESIGN, [1, 4])` is called with the identical shape argument in all three places it appears (§V0, §V2, the applier).
