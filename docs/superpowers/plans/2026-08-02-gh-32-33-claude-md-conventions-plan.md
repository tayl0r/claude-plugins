---
dev-flow:
  slug: gh-32-33-claude-md-conventions
  spec: docs/superpowers/specs/2026-08-02-gh-32-33-claude-md-conventions-design.md
---

# gh-32 / gh-33: write down the two conventions `CLAUDE.md` leaves to judgment — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace two whole lines of `CLAUDE.md` — line 7 (issue #33, the version-bump segment rule) and line 9 (issue #32, the mirrored-pair `Always:` clause) — with the two plain fenced blocks the design gives, read from the design on disk. Nothing else in the repo changes.

**Architecture:** Two independent whole-line replacements in one un-mirrored, un-cached Markdown file. `CLAUDE.md` is **29 lines before and after** — replacements, not appends to the file. Neither edit shifts the other's line index, so the two are order-independent; this plan runs line 7 first only to match the design's block order. Line 7 goes 28 → 75 words and line 9 goes 246 → 286 (design *Length budget*, informational — no check asserts a word count). **No `scripts/` file, no plugin file, no `plugin.json`, no `CONTEXT.md`, no `docs/adr/`, and no version bump.**

**Tech Stack:** Markdown. `python3` (stdlib only, plus this repo's `scripts/design_blocks.py`), `git`, `git grep`, `git diff`, `python3 scripts/check-sync.py`, `claude plugin validate .`. **There is no build, no linter, and no test framework in this repo (design A3) — do not run `pytest`, `npm test`, or `ruff`, and do not add one.** The design's `## Verification` section is the entire verification surface.

**Authoritative source:** `docs/superpowers/specs/2026-08-02-gh-32-33-claude-md-conventions-design.md`. Its two plain fenced blocks are the replacement text and its `## Verification` section holds all nine checks (steps 0–8), distributed across the tasks below. **If this plan and the design ever disagree, the design wins — stop and report.**

---

## Global Constraints

Every task's requirements implicitly include this section.

- **Repo root for this run (absolute):** `/Users/taylor/dev/claude-plugins/.claude/worktrees/agent-a4ba04cbf6e3a28ca`. **`cd` there before the first command of every task.** Every path in this plan that is not absolute is **repo-relative**, and every command is run from the repo root — that is what makes the design's `## Verification` commands runnable verbatim. If your checkout is at a different absolute path, only the initial `cd` changes; every command below stays byte-identical.
- **`§V1`, `§V2` and `§V5` are IDs, not text you have been handed.** Each names a fenced block under `## Verification scripts` in **this plan file** — `/Users/taylor/dev/claude-plugins/.claude/worktrees/agent-a4ba04cbf6e3a28ca/docs/superpowers/plans/2026-08-02-gh-32-33-claude-md-conventions-plan.md`. A step that says *"Run §V2 … verbatim"* means: open that file, find the block carrying that ID, and run it character for character from the repo root. `subagent-driven-development` briefs **one task at a time**, so those blocks are **not** in the task text you were given — read them from the plan file rather than reconstructing them, and never substitute an equivalent of your own. **If you cannot read the plan file, stop and report** rather than improvising a check.
- **Branch `tayl0r/gh-32-33-claude-md-conventions`. Work in place — do not create a git worktree, do not switch branches, do not rebase, do not push, do not open a PR, do not merge, do not invoke any review skill.** The pipeline owns all of those. Committing the two edits *is* part of this plan (each edit task ends with one commit of `CLAUDE.md` by exact path).
- **NEVER RETYPE EITHER REPLACEMENT LINE.** The design gives them as its only two plain (untagged) fenced blocks, shape `[1, 1]`. Every step that writes bytes into `CLAUDE.md` obtains them from `read_blocks(DESIGN, [1, 1])`, reading the design **on disk**. Do **not** transcribe a block by hand, do **not** paste one from a chat message, do **not** use the `Edit` tool with a retyped `new_string`, and do **not** reconstruct one from the design's prose. **This plan deliberately contains no reference copy of either block** — a copy here would be one more thing to keep in step with the design and one more thing to be tempted to paste. Both lines carry em dashes (`—`), a right arrow (`→`) and backticked code spans: precisely the characters a retype gets wrong. `CLAUDE.md` mandates the design-sourced check for exactly this reason, and here it is the only thing standing between the design and a paraphrase — `scripts/check-sync.py` never reads `CLAUDE.md`, and no mirror pair is involved.
- **The two appliers type zero bytes of block content.** Each locates its target line by a property of the block itself (see *Design block map*) and writes `want` — the block, straight from `read_blocks`. The only string literals either applier types are ASCII markers reproduced verbatim from the design's *Verification* step 2: `"**Always:**"`, `"**When the change has a design doc**"`, and `" **Always the minor segment**"`. Those are **guards**, never sources: they are compared against, never written.
- **Scope is exactly one file: `CLAUDE.md`.** Nothing else may appear in the branch diff beyond this run's own `docs/superpowers/` design and plan artifacts. Hard-excluded by the design's *Out of scope* — touching any of these is a **HALT and report**, not a judgment call: `plugins/` and every `plugin.json`, `.claude-plugin/marketplace.json`, `scripts/` (including `design_blocks.py`, which is *used* and never modified, and `check-sync.py`), `CONTEXT.md`, `docs/adr/`, `docs/agents/`, `.gitignore`, either `README.md`, and **every pre-existing file under `docs/superpowers/`** — meaning the prior records. This run's own design doc is read-only input; this plan file takes checkbox ticks only.
- **NO VERSION BUMP.** `dev-flow` stays `2.8.0` and `dev-flow-worktree` stays `1.10.0`. `CLAUDE.md` sits outside `plugins/`, ships into no version-keyed cache, and is read at edit time rather than into any model invocation, so `CLAUDE.md`'s own bump rule does not fire (design *Out of scope*). This is a conclusion, not a deferral. **If any step seems to need a version bump, that is a HALT — stop and report.** Verification step 8 asserts it because the reflex is to bump.
- **The design doc is read-only input.** `docs/superpowers/specs/2026-08-02-gh-32-33-claude-md-conventions-design.md` must end this work byte-identical to how it started. Expected blob hash — `git hash-object docs/superpowers/specs/2026-08-02-gh-32-33-claude-md-conventions-design.md` → `a4f1e3d146a8b197c6fbb65236e40ceb177658b1`. If it differs at a task's Step 1, **halt and report** — do not proceed and do not "fix" the design. Editing it would silently change what every conformance check compares against.
- **The base is always computed, never hardcoded:** `git merge-base origin/main HEAD`. It resolves to `b4b5d1ca5d19b36e992f9ff1f3d2ff7a1b989037` today. **Every step that consumes it — §V1, §V2 and §V5 — computes it inside `python3` and passes it to `git` as an `argv` element, never through a shell.** `git merge-base` writes nothing to stdout when it fails (exit 128 for an unresolvable `origin/main`; exit 1 with no message at all for histories sharing no ancestor), so in a shell an unquoted `$(…)` vanishes by word-splitting and degrades a base comparison into a working-tree-vs-index one, which in a repo that commits per task is empty and prints a pass token on an arbitrarily broken branch. `argv` has no word-splitting to exploit. **Do not rewrite any of these three into a shell `&&` chain, and do not hardcode a SHA.**
- **Every inline `python3` script below is pure ASCII on purpose**, including its guard strings, so a mistyped copy fails loudly instead of passing. The *content* it moves is not ASCII — but you never type that content, `read_blocks` supplies it. **Copy each script exactly, character for character. Every heredoc fence is unindented on purpose: a `python3` heredoc indented under a list item is an `IndentationError`.**
- **No new files anywhere, including temp files inside the repo.** Every Python snippet runs as a heredoc piped to `python3 -`.
- **Never stage with `git add -A`, `git add .`, or `git commit -a`.** Each commit stages `CLAUDE.md` by exact path.
- **Text assertions use `git grep`, never bare `grep`** (design A7): under Claude Code's Bash tool bare `grep` is a ugrep-backed shell function whose output layout is not reliable for per-file assertions. Whole-line and index assertions are made in `python3`, where they are exact.
- **`claude plugin validate .` exiting 0 with exactly 8 `No author information provided` warnings is a PASS** (design A4, `CLAUDE.md`). Warnings are not failures. Do not add author fields to silence them.
- **Line numbers in this plan are informational, never inputs.** Every applier locates its target by content and asserts the match is unique (design A1). If an applier prints a line number other than the one predicted here, **stop and report** rather than editing around it.
- **Both appliers are idempotent.** Re-running one after it has landed prints `already applied: …` and changes nothing, so a re-dispatched task is safe to run from its Step 1.
- **Every check here compares the working tree against a commit**, so every assertion works on uncommitted edits. You never need to commit in order to verify.

---

## File map

| Path (repo-relative) | Change | Lines | Task |
|---|---|---|---|
| `CLAUDE.md` | Line 7 replaced in full by design block 0 (issue #33). | 29 → **29** | 1 |
| `CLAUDE.md` | Line 9 replaced in full by design block 1 (issue #32). | 29 → **29** | 2 |

No file is created, renamed, or deleted. No other file is modified. Whole-line replacement is the gh-7 and gh-24 precedent for this file and is the stronger check: an exact whole-line match at a known index cannot be satisfied by a fragment landing in the wrong bullet (design *The edit*).

## Design block map

The design holds **exactly two** plain (untagged) fenced blocks, shape `[1, 1]`. Every script below asserts that shape through `read_blocks` before using it, so the shape is the contract. Every other fence in the design carries an info string (`sh`, `text`) — that is what keeps this index stable. **Keep it that way.**

| Block | Design heading | Shape | Target | How the applier finds the target — types no block content |
|---|---|---|---|---|
| 0 | `### Block 0 — the complete new CLAUDE.md line 7 (issue #33)` | 1 line, whole-line replace | `CLAUDE.md` line 7 | The unique non-empty line of `CLAUDE.md` that is a **prefix of block 0**. Block 0 is a pure append to the existing bullet, so exactly one line has that property. |
| 1 | `### Block 1 — the complete new CLAUDE.md line 9 (issue #32)` | 1 line, whole-line replace | `CLAUDE.md` line 9 | The unique line that **starts with block 1's head** (everything before `**Always:**`) **and ends with block 1's tail** (`**When the change has a design doc**` onward). Block 1 rewrites only the span between those two markers, so exactly one line has that property. |

Both selectors were dry-run against the working tree at base `b4b5d1c` and each matched exactly one line — 7 and 9 respectively.

---

## Verification scripts

The design's *Verification* steps 1, 2 and 5 are `python3` heredocs used by all three tasks. They are written out **once, here**, and every task points at them by ID. One copy is the check; three copies are three things to keep in step — the same reasoning `CLAUDE.md` applies to mirrored text.

**How to run one:** read this plan file at
`/Users/taylor/dev/claude-plugins/.claude/worktrees/agent-a4ba04cbf6e3a28ca/docs/superpowers/plans/2026-08-02-gh-32-33-claude-md-conventions-plan.md`,
find the block below with the matching ID, and run it **verbatim** from the repo root. Do not retype it, do not reconstruct it, and do not substitute an equivalent of your own — the whole point of §V2 is that it reads the design from disk. All three scripts are read-only and idempotent, so running one repeatedly is safe.

### §V2 — design conformance, through the shared reader (design *Verification* step 2)

This is the check `CLAUDE.md` requires. It re-reads both blocks from the design on disk — never retyped — and re-reads the *pre-change* lines from git, so nothing in it is typed twice. It asserts: block 0 is `CLAUDE.md` line 7 exactly and uniquely; block 1 is line 9 exactly and uniquely; the file gained and lost no lines; the base line 7 is a strict prefix of block 0 (the append kept every existing byte); and the base line 9's head and tail both survive in block 1 (the rewrite touched only the span between the two markers). Both markers are located with `partition`, so a base whose line 9 lost either one reports `MISMATCH:` and exits 1 like every other failure path rather than raising — **do not rewrite either `partition` back to `.index`**, which raised an uncaught `ValueError` instead. Failures of the *producers* (`git`, `read_blocks`) are deliberately left to raise as themselves: they name the failing command, and no traceback can be mistaken for a pass. **The fence is unindented on purpose.**

```sh
python3 - <<'PY'
import subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
DESIGN = "docs/superpowers/specs/2026-08-02-gh-32-33-claude-md-conventions-design.md"
HEAD_END = "**Always:**"
TAIL_START = "**When the change has a design doc**"
base = subprocess.run(["git", "merge-base", "origin/main", "HEAD"],
                      capture_output=True, text=True, check=True).stdout.strip()
old = subprocess.run(["git", "show", base + ":CLAUDE.md"],
                     capture_output=True, text=True, check=True).stdout.split("\n")
new = Path("CLAUDE.md").read_text(encoding="utf-8").split("\n")
b0, b1 = read_blocks(DESIGN, [1, 1])
bad = []
if len(new) != len(old):
    bad.append("CLAUDE.md gained or lost lines: %d against the base's %d" % (len(new), len(old)))
for label, block, want in (("block 0", b0[0], 7), ("block 1", b1[0], 9)):
    at = [i + 1 for i, l in enumerate(new) if l == block]
    if at != [want]:
        bad.append("%s matches CLAUDE.md at lines %s, want exactly [%d]" % (label, at, want))
if not b0[0].startswith(old[6]):
    bad.append("base line 7 is not a prefix of block 0; the bump bullet is not a pure append")
if not b0[0][len(old[6]):].startswith(" **Always the minor segment**"):
    bad.append("block 0 appends something other than the minor-segment clause")
head, sep, tail = old[8].partition(TAIL_START)
pre, always, _ = head.partition(HEAD_END)
if not sep:
    bad.append("base line 9 does not contain %r" % TAIL_START)
elif not always:
    bad.append("base line 9 does not contain %r before %r" % (HEAD_END, TAIL_START))
else:
    if not b1[0].startswith(pre):
        bad.append("block 1 changes text before the Always: sentence")
    if not b1[0].endswith(sep + tail):
        bad.append("block 1 changes text from %r onward" % TAIL_START)
for why in bad:
    print("MISMATCH:", why)
print("design-conformance:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

If the shape guard trips instead (`design code-block shape is …`), **stop and report**: the design was edited after this plan captured its shape (design A9).

### §V5 — the change's own changed-line set (design *Verification* step 5)

One instrument satisfying the property block 1 states — the clause names none — run on this change's own edit. It is **voluntary**: `CLAUDE.md` is in no mirror pair, so the new clause does not bind this change (design A8). It is run anyway, as the rule's first exercise. Plain `split("\n")` is used on both sides deliberately, with no `split_lines` helper: the trailing element is present on both sides and compares equal, and a trailing-newline change trips the length assert rather than being hidden (design *The `split_lines` question*). The set is printed `sorted`, since a Python set of small integers prints in hash order. **The fence is unindented on purpose.**

```sh
python3 - <<'PY'
import subprocess, sys
from pathlib import Path
base = subprocess.run(["git", "merge-base", "origin/main", "HEAD"],
                      capture_output=True, text=True, check=True).stdout.strip()
old = subprocess.run(["git", "show", base + ":CLAUDE.md"],
                     capture_output=True, text=True, check=True).stdout.split("\n")
new = Path("CLAUDE.md").read_text(encoding="utf-8").split("\n")
if len(old) != len(new):
    print("LENGTH: base %d lines, working %d" % (len(old), len(new)))
    sys.exit(1)
changed = {i + 1 for i, (a, b) in enumerate(zip(old, new)) if a != b}
print("changed lines:", sorted(changed))
print("line-set:", "OK" if changed == {7, 9} else "FAIL")
sys.exit(0 if changed == {7, 9} else 1)
PY
echo "exit=$?"
```

### §V1 — file scope (design *Verification* step 1)

Also written out once, because three tasks run it. **This step is a `python3` heredoc, not a shell chain, and that is load-bearing** — see Global Constraints and the design's *Verification* step 1. The base is computed inside the script and passed to `git` as an `argv` element, so nothing can word-split and a failed `git merge-base` raises with the failing command, its exit status and git's own message instead of silently degrading into a working-tree-vs-index comparison. The `--name-only` equality is the machine-checked form of this step's headline claim and prints the set it found, so a failure names the offending path; `--stat` is for reading, since its column widths shift when a second file appears. There is deliberately **no `--quiet` assertion** over the hard-excluded paths: all of them lie inside `. ':!docs/superpowers/'`, so the equality already implies each is untouched, and `--quiet` prints nothing at all on success or failure. The `':!docs/superpowers/'` pathspec is required: this run's front-matter sets `docs: commit`, so its own design and plan are committed on this branch and an unfiltered diff necessarily reports them. **Pure ASCII, unindented fence — copy exactly.**

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
print(git("diff", "--stat", base, *SCOPE), end="")
changed = [p for p in git("diff", "--name-only", base, *SCOPE).split("\n") if p]
if changed != WANT:
    print("file scope: FAIL -- changed %s, want %s" % (changed, WANT))
    sys.exit(1)
print("file scope: OK")
PY
echo "exit=$?"
```

The single pass token is `file scope: OK`, and the `base:` line must carry a 40-character SHA (`b4b5d1ca5d19b36e992f9ff1f3d2ff7a1b989037` today). **Do not rewrite this step as a shell `&&` chain and do not hardcode the base.** A chain that captures the base with `BASE=$(…)` and reuses it across `&&`-joined `git` commands is refused unrun by Claude Code's Bash tool under worktree isolation — *"too complex to verify that it stays inside the worktree"* — and this run's repo root **is** a linked git worktree, so that refusal is the expected outcome for the chain form, not a signal that anything is wrong with the run. Prefixing `git -C <repo root>` does not lift it. The heredoc above is never refused. Dropping the base capture instead — running `git diff` with an unquoted `$(git merge-base …)` — is the degradation the design's step 1 prose names: it prints a pass token and exits 0 on an arbitrarily broken tree.

---

## Task order and dependencies

- **Task 1** (block 0 → line 7, issue #33) and **Task 2** (block 1 → line 9, issue #32) are independent whole-line replacements on non-adjacent lines, with no shared text and no ordering dependency (design *Scope check*); neither shifts the other's line index. They are ordered 1 then 2 only to match the design's block order, and a reviewer may meaningfully reject one while approving the other (design A5).
- **Task 2 depends on Task 1** only for its stated intermediate expectations. Its applier works standalone; if Tasks 1 and 2 are ever run out of order, the appliers still land correctly, but the intermediate outputs quoted in each task's steps will be the other task's.
- **Task 3 depends on Tasks 1 and 2**, both committed. It is the full end-to-end sweep of the design's *Verification* steps 0–8.
- Execution is complete when zero `- [ ]` boxes remain unchecked.

---

## Task 1: Replace `CLAUDE.md` line 7 with design block 0 — issue #33, always the minor segment

**Files:**
- Modify: `CLAUDE.md` (line 7 only)
- Read-only input: `docs/superpowers/specs/2026-08-02-gh-32-33-claude-md-conventions-design.md`, `scripts/design_blocks.py`
- Test: none — this repo has no test framework (design A3). §V2 is the test.

**Interfaces:**
- Consumes: nothing from an earlier task. Design block 0, obtained by `read_blocks(DESIGN, [1, 1])[0][0]`.
- Produces: a `CLAUDE.md` that is 29 lines long and whose line 7 is byte-identical to design block 0, with lines 1–6 and 8–29 byte-identical to base `b4b5d1c`. Tasks 2 and 3 depend on exactly that.

**What changes:** one line. Block 0 is a **pure append** — the bullet's two existing sentences are unchanged and everything from `**Always the minor segment**` onward is new. That is why the applier's selector is "the unique line that is a prefix of block 0", and why §V2 asserts the base line 7 is a strict prefix of block 0 rather than grepping for a removed phrase: **this edit removes no phrase**, so the residue grep has nothing to search for on this line (design *Block 0*).

- [x] **Step 1: Confirm the starting state and the block shape** (design *Verification* step 0)

```sh
cd /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-a4ba04cbf6e3a28ca
git rev-parse --abbrev-ref HEAD
git status --porcelain
wc -l CLAUDE.md
git hash-object docs/superpowers/specs/2026-08-02-gh-32-33-claude-md-conventions-design.md
python3 scripts/design_blocks.py docs/superpowers/specs/2026-08-02-gh-32-33-claude-md-conventions-design.md
```

Expected:

- `tayl0r/gh-32-33-claude-md-conventions`.
- `git status --porcelain` prints nothing except, possibly, a **modified or untracked** `docs/superpowers/plans/2026-08-02-gh-32-33-claude-md-conventions-plan.md` (this plan's own checkbox ticks; it is untracked until the pipeline commits it). Any other modified or untracked path → **halt and report**: the tree is not in the state this plan was written against.
- `29 CLAUDE.md`.
- `a4f1e3d146a8b197c6fbb65236e40ceb177658b1`. **Any other value → halt and report "design doc modified".**
- Then, from `design_blocks.py`:

```text
shape: [1, 1]
  [0] len=1: - **Bump `version` in `plugins/<name>/.claude-plugin/plugin.json` on a
  [1] len=1: - **Some files are mirrored across `dev-flow` and `dev-flow-worktree`
```

Anything other than two entries of one line each means the design was edited after this plan captured its shape — **stop and report** (design A9).

- [x] **Step 2: Run §V2 and watch it FAIL (red)**

Run **§V2** from *Verification scripts* above, verbatim. This is the design's *Verification* step 2, run before the edit so you can watch it discriminate.

Expected, exactly:

```text
MISMATCH: block 0 matches CLAUDE.md at lines [], want exactly [7]
MISMATCH: block 1 matches CLAUDE.md at lines [], want exactly [9]
design-conformance: FAIL
exit=1
```

Both blocks are absent because neither edit has been applied yet. If you instead see only the `block 1` line, block 0 is already applied — skip to Step 4. If you see `design-conformance: OK`, both edits are already applied — skip to Step 7.

- [x] **Step 3: Apply block 0 with the applier**

Reads block 0 from the design **on disk** through the shared reader and writes it into `CLAUDE.md`, selecting the target as the unique non-empty line that block 0 extends. It types **no byte of block 0** — the only literal is the ASCII guard `" **Always the minor segment**"`, reproduced verbatim from the design's *Verification* step 2 and only ever compared against. Idempotent. **Unindented fence, pure ASCII — copy exactly.**

```sh
python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
DESIGN = "docs/superpowers/specs/2026-08-02-gh-32-33-claude-md-conventions-design.md"
TARGET = "CLAUDE.md"
APPEND_HEAD = " **Always the minor segment**"
b0, b1 = read_blocks(DESIGN, [1, 1])
want = b0[0]
lines = Path(TARGET).read_text(encoding="utf-8").split("\n")
if want in lines:
    print("already applied: block 0, at line %d of %s" % (lines.index(want) + 1, TARGET))
    sys.exit(0)
at = [i for i, l in enumerate(lines) if l and want.startswith(l)]
if len(at) != 1:
    raise SystemExit("expected exactly 1 line that block 0 extends, found %d: %s"
                     % (len(at), [i + 1 for i in at]))
i = at[0]
if not want[len(lines[i]):].startswith(APPEND_HEAD):
    raise SystemExit("line %d is a prefix of block 0 but the appended text does not open"
                     " with the minor-segment clause; stop and re-read the design" % (i + 1))
lines[i] = want
Path(TARGET).write_text("\n".join(lines), encoding="utf-8")
print("applied: block 0, at line %d of %s" % (i + 1, TARGET))
PY
echo "exit=$?"
```

Expected: `applied: block 0, at line 7 of CLAUDE.md` and `exit=0` (or the `already applied:` line if re-run). Any `SystemExit` message is a **stop and report** — do not hand-patch `CLAUDE.md` to satisfy it.

- [x] **Step 4: Presence — the new clause is in `CLAUDE.md`, once** (design *Verification* step 4, first command)

```sh
git grep -c -F 'Always the minor segment' -- CLAUDE.md
```

Expected, exactly `CLAUDE.md:1`. Before Step 3 this printed nothing and exited 1.

- [x] **Step 5: Run §V2 again — one MISMATCH must remain, and it must name block 1**

Run **§V2** verbatim again.

Expected, exactly:

```text
MISMATCH: block 1 matches CLAUDE.md at lines [], want exactly [9]
design-conformance: FAIL
exit=1
```

**This FAIL is the expected mid-change state, not a defect** — block 1 is Task 2's deliverable. What matters is that the `block 0` MISMATCH is **gone** and that no *new* MISMATCH line has appeared. Any line other than the single `block 1` one — in particular `CLAUDE.md gained or lost lines`, `base line 7 is not a prefix of block 0`, or `block 0 appends something other than the minor-segment clause` — is a **stop and report**.

- [x] **Step 6: Run §V5 — the changed-line set must be exactly `[7]`**

Run **§V5** from *Verification scripts* above, verbatim.

Expected, exactly:

```text
changed lines: [7]
line-set: FAIL
exit=1
```

**This FAIL is expected mid-change**: §V5 asserts the *final* set `{7, 9}` and line 9 is Task 2's. The assertion this task owns is the printed set — `[7]` and nothing else. `[]` means Step 3 did not write; anything containing a line other than 7 means a stray edit landed → **stop and report**. A `LENGTH:` line means `CLAUDE.md` gained or lost a line → **stop and report**.

- [x] **Step 7: Run §V1 — file scope** (design *Verification* step 1)

Run **§V1** from *Verification scripts* above, verbatim.

Expected, exactly:

```text
base: b4b5d1ca5d19b36e992f9ff1f3d2ff7a1b989037
 CLAUDE.md | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
file scope: OK
exit=0
```

The `--stat` rows differ from the design's stated end state (` CLAUDE.md | 4 ++--`, `2 insertions(+), 2 deletions(-)`) because only one of the two lines has changed so far; Task 2 Step 8 and Task 3 assert the end-state form. `--stat` is for reading — **the assertion is `file scope: OK`**. A `file scope: FAIL` line names the changed set it found; any path in it other than `CLAUDE.md` means something outside the authorized set moved → **stop and report**, and if it is a version bump, revert it (Global Constraints).

- [x] **Step 8: Commit**

Stage by exact path — never `git add -A`.

```sh
git add CLAUDE.md
git commit -m "CLAUDE.md: bump the minor segment, always (#33)"
git show --stat --format=%s HEAD
```

Expected: the commit succeeds and `git show --stat` lists **exactly one** file, `CLAUDE.md`, with 1 insertion and 1 deletion. Any second path means something outside the authorized set was staged → **halt and report**.

---

## Task 2: Replace `CLAUDE.md` line 9 with design block 1 — issue #32, prove nothing else moved

**Depends on:** Task 1, committed.

**Files:**
- Modify: `CLAUDE.md` (line 9 only)
- Read-only input: `docs/superpowers/specs/2026-08-02-gh-32-33-claude-md-conventions-design.md`, `scripts/design_blocks.py`
- Test: none — this repo has no test framework (design A3). §V2 is the test.

**Interfaces:**
- Consumes: Task 1's committed line 7. Design block 1, obtained by `read_blocks(DESIGN, [1, 1])[1][0]`.
- Produces: a `CLAUDE.md` that is 29 lines long with lines 7 and 9 replaced and every other line byte-identical to base `b4b5d1c`. Task 3 asserts exactly that.

**What changes:** one line. Everything before `**Always:**` and everything from `**When the change has a design doc**` onward is byte-identical to the line #24 landed at `963a66c`; the span between those two markers is a single sentence in the base, and block 1 replaces it with a longer sentence plus one new one (design *Block 1*). Unlike block 0, **this edit does remove a phrase** — the sentence junction `expecting no hits. **When the change` — so the residue grep in Step 4 has something to search for.

- [x] **Step 1: Confirm the starting state**

```sh
cd /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-a4ba04cbf6e3a28ca
git status --porcelain
wc -l CLAUDE.md
git hash-object docs/superpowers/specs/2026-08-02-gh-32-33-claude-md-conventions-design.md
git grep -c -F 'Always the minor segment' -- CLAUDE.md
```

Expected: `git status --porcelain` prints nothing except, possibly, a modified or untracked plan file (checkbox ticks); `29 CLAUDE.md`; `a4f1e3d146a8b197c6fbb65236e40ceb177658b1` (**any other value → halt and report "design doc modified"**); and `CLAUDE.md:1`, which is Task 1's committed result. If that last command prints nothing, Task 1 has not landed — **halt and report** rather than running Task 1's applier from here.

- [x] **Step 2: Confirm the junction this edit removes is present (red for the residue check)**

```sh
git grep -n -F 'expecting no hits. **When the change' -- . ':!docs/superpowers/'
echo "exit=$?"
```

Expected: **exactly one hit**, on `CLAUDE.md:9`, then `exit=0`. That is the phrase Step 4 will require to be gone. If there is no hit, the edit is already applied — skip to Step 4. The `':!docs/superpowers/'` pathspec is required: the design quotes this phrase.

- [x] **Step 3: Apply block 1 with the applier**

Reads block 1 from the design **on disk** through the shared reader and writes it into `CLAUDE.md`, selecting the target as the unique line sharing block 1's head and tail. It types **no byte of block 1** — the only literals are the two ASCII markers `"**Always:**"` and `"**When the change has a design doc**"`, reproduced verbatim from the design's *Verification* step 2 and only ever compared against. Idempotent. **Unindented fence, pure ASCII — copy exactly.**

```sh
python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
DESIGN = "docs/superpowers/specs/2026-08-02-gh-32-33-claude-md-conventions-design.md"
TARGET = "CLAUDE.md"
HEAD_END = "**Always:**"
TAIL_START = "**When the change has a design doc**"
b0, b1 = read_blocks(DESIGN, [1, 1])
want = b1[0]
pre, sep_head, _ = want.partition(HEAD_END)
_, sep_tail, tail = want.partition(TAIL_START)
if not sep_head or not sep_tail:
    raise SystemExit("block 1 no longer contains %r and %r; stop and re-read the design"
                     % (HEAD_END, TAIL_START))
lines = Path(TARGET).read_text(encoding="utf-8").split("\n")
if want in lines:
    print("already applied: block 1, at line %d of %s" % (lines.index(want) + 1, TARGET))
    sys.exit(0)
at = [i for i, l in enumerate(lines)
      if l.startswith(pre) and l.endswith(sep_tail + tail)]
if len(at) != 1:
    raise SystemExit("expected exactly 1 line sharing block 1's head and tail, found %d: %s"
                     % (len(at), [i + 1 for i in at]))
i = at[0]
lines[i] = want
Path(TARGET).write_text("\n".join(lines), encoding="utf-8")
print("applied: block 1, at line %d of %s" % (i + 1, TARGET))
PY
echo "exit=$?"
```

Expected: `applied: block 1, at line 9 of CLAUDE.md` and `exit=0` (or the `already applied:` line if re-run). Any `SystemExit` message is a **stop and report** — do not hand-patch `CLAUDE.md` to satisfy it.

- [x] **Step 4: Residue — the removed junction is gone from the tree** (design *Verification* step 3)

```sh
git grep -n -F 'expecting no hits. **When the change' -- . ':!docs/superpowers/'
```

Expected: **no output** and a non-zero exit (`git grep` exits 1 on no match — that is the pass here). The pathspec is required: the design quotes the phrase, and without the exclusion this reports the design doc and this plan is impossible to satisfy. Any hit outside `docs/superpowers/` means the old junction survives → **stop and report**.

- [x] **Step 5: Presence — the new clause is in `CLAUDE.md`, once** (design *Verification* step 4, second command)

```sh
git grep -c -F 'byte-for-byte its merge-base blob' -- CLAUDE.md
```

Expected, exactly `CLAUDE.md:1`. Before Step 3 this printed nothing and exited 1.

- [x] **Step 6: Run §V2 and watch it PASS (green)**

Run **§V2** from *Verification scripts* above, verbatim — the same characters as in Tasks 1 Steps 2 and 5.

Expected, exactly:

```text
design-conformance: OK
exit=0
```

Any `MISMATCH:` line is a **stop and report** — do not hand-patch `CLAUDE.md` to satisfy it; re-run Step 3 instead. This is the `CLAUDE.md`-mandated design-sourced check going green: both blocks are proved to be at lines 7 and 9 byte-for-byte, uniquely, with every untouched span re-derived from git rather than trusted.

- [x] **Step 7: Run §V5 and watch it PASS (green)**

Run **§V5** from *Verification scripts* above, verbatim.

Expected, exactly:

```text
changed lines: [7, 9]
line-set: OK
exit=0
```

Steps 6 and 7 together are exactly the reconstruction the new clause asks for — §V2 proves the intended edit is what landed on lines 7 and 9, §V5 proves no other line moved — so this change exercises its own new rule end to end (design A8). Any other set, or a `LENGTH:` line, is a **stop and report**.

- [x] **Step 8: Run §V1 — file scope, end-state form** (design *Verification* step 1)

Run **§V1** from *Verification scripts* above, verbatim.

Expected, exactly:

```text
base: b4b5d1ca5d19b36e992f9ff1f3d2ff7a1b989037
 CLAUDE.md | 4 ++--
 1 file changed, 2 insertions(+), 2 deletions(-)
file scope: OK
exit=0
```

This is now the design's stated end state. `--stat` is for reading; **the assertion is `file scope: OK`**.

- [x] **Step 9: Commit**

Stage by exact path — never `git add -A`.

```sh
git add CLAUDE.md
git commit -m "CLAUDE.md: prove nothing else moved in a mirrored-pair change (#32)"
git show --stat --format=%s HEAD
```

Expected: the commit succeeds and `git show --stat` lists **exactly one** file, `CLAUDE.md`, with 1 insertion and 1 deletion (this commit's own delta — the branch total against the base is 2 and 2). Any second path means something outside the authorized set was staged → **halt and report**.

---

## Task 3: Full `Verification` sweep — all nine steps green, end to end

**Depends on:** Tasks 1 and 2, both committed.

**Files:** none modified. This task is verification only, and it is the whole verification surface (design A3 — no test framework exists).

**Interfaces:**
- Consumes: the committed result of Tasks 1 and 2.
- Produces: a pass/fail verdict on every step of the design's `## Verification`, steps 0 through 8.

**Nothing in this task edits a file. If a check fails, stop and report — do not repair by editing the file the check names.**

- [x] **Step 1: Confirm the tree is clean and the design doc is intact**

```sh
cd /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-a4ba04cbf6e3a28ca
git status --porcelain
git hash-object docs/superpowers/specs/2026-08-02-gh-32-33-claude-md-conventions-design.md
wc -l CLAUDE.md
```

Expected: `git status --porcelain` prints nothing except, possibly, a modified or untracked `docs/superpowers/plans/2026-08-02-gh-32-33-claude-md-conventions-plan.md` (this plan's own checkbox ticks); `a4f1e3d146a8b197c6fbb65236e40ceb177658b1` — **any other value means the implementation modified the design doc → halt and report**; and `29 CLAUDE.md`, unchanged from before the change.

- [x] **Step 2: Design *Verification* step 0 — block shape**

```sh
python3 scripts/design_blocks.py docs/superpowers/specs/2026-08-02-gh-32-33-claude-md-conventions-design.md
```

Expected, exactly:

```text
shape: [1, 1]
  [0] len=1: - **Bump `version` in `plugins/<name>/.claude-plugin/plugin.json` on a
  [1] len=1: - **Some files are mirrored across `dev-flow` and `dev-flow-worktree`
```

Anything other than two entries means the design was edited after this plan captured its shape — **stop and report**.

- [x] **Step 3: Design *Verification* step 1 — file scope**

Run **§V1** from *Verification scripts* above, verbatim.

Expected, exactly:

```text
base: b4b5d1ca5d19b36e992f9ff1f3d2ff7a1b989037
 CLAUDE.md | 4 ++--
 1 file changed, 2 insertions(+), 2 deletions(-)
file scope: OK
exit=0
```

and no other stat row. Exactly one file changed, and it is not a plugin file.

- [x] **Step 4: Design *Verification* step 2 — design conformance, through the shared reader**

Run **§V2** from *Verification scripts* above, verbatim.

Expected, exactly:

```text
design-conformance: OK
exit=0
```

- [x] **Step 5: Design *Verification* step 3 — residue**

```sh
git grep -n -F 'expecting no hits. **When the change' -- . ':!docs/superpowers/'
```

Expected: no output and a non-zero exit.

- [x] **Step 6: Design *Verification* step 4 — presence, both new clauses, once each**

```sh
git grep -c -F 'Always the minor segment' -- CLAUDE.md
git grep -c -F 'byte-for-byte its merge-base blob' -- CLAUDE.md
```

Expected: `CLAUDE.md:1` from each.

- [x] **Step 7: Design *Verification* step 5 — the changed-line set is exactly `{7, 9}`**

Run **§V5** from *Verification scripts* above, verbatim.

Expected, exactly:

```text
changed lines: [7, 9]
line-set: OK
exit=0
```

- [x] **Step 8: Design *Verification* step 6 — `check-sync.py`**

```sh
python3 scripts/check-sync.py
echo "exit=$?"
```

Expected, exactly:

```text
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)
check-sync: all checks passed
exit=0
```

Identical to before the change — it reads none of the changed files. `.claude-plugin/marketplace.json` is untouched, so Check A is unaffected, and Check B's mirror pair is not in this change at all.

- [x] **Step 9: Design *Verification* step 7 — `claude plugin validate .`**

```sh
claude plugin validate .
echo "exit=$?"
```

Expected: `⚠ Found 8 warnings:`, eight `author: No author information provided…` lines, `✔ Validation passed with warnings`, and `exit=0`. **The 8 warnings are expected and are NOT a failure** (design A4). A non-zero exit, any error, or a warning count other than 8 is a failure.

- [x] **Step 10: Design *Verification* step 8 — no version moved**

```sh
git grep '"version"' -- plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
```

Expected, exactly:

```text
plugins/dev-flow-worktree/.claude-plugin/plugin.json:  "version": "1.10.0",
plugins/dev-flow/.claude-plugin/plugin.json:  "version": "2.8.0",
```

`git grep` rather than bare `grep`, because the assertion is *which plugin is at which version* and only the per-file labels carry it. **If either version moved, revert the bump** — `CLAUDE.md` ships into no version-keyed cache, so no bump is warranted (Global Constraints, design *Out of scope*).

- [x] **Step 11: Record the verdict**

Every row must be green:

| Design *Verification* step | Assertion | Where run |
|---|---|---|
| 0 | `shape: [1, 1]`, block 0 the bump bullet, block 1 the mirrored-pair bullet | Task 1 Step 1; Task 3 Step 2 |
| 1 | one stat row ` CLAUDE.md \| 4 ++--`, `file scope: OK`, `exit=0` | Task 1 Step 7; Task 2 Step 8; Task 3 Step 3 |
| 2 | `design-conformance: OK`, `exit=0` | Task 1 Steps 2/5 (red); Task 2 Step 6; Task 3 Step 4 |
| 3 | no hit for `expecting no hits. **When the change` outside `docs/superpowers/` | Task 2 Steps 2 (red) / 4; Task 3 Step 5 |
| 4 | `CLAUDE.md:1` for each new clause | Task 1 Step 4; Task 2 Step 5; Task 3 Step 6 |
| 5 | `changed lines: [7, 9]`, `line-set: OK` | Task 1 Step 6 (red); Task 2 Step 7; Task 3 Step 7 |
| 6 | `check-sync: all checks passed`, exit 0 | Task 3 Step 8 |
| 7 | `claude plugin validate .` exit 0, exactly 8 author warnings, 0 errors | Task 3 Step 9 |
| 8 | `dev-flow` `2.8.0`, `dev-flow-worktree` `1.10.0` | Task 3 Step 10 |

Together, steps 2 and 5 pin `CLAUDE.md` completely: every one of its 29 lines is either byte-identical to the base blob or one of the design's two blocks read fresh from disk. Report the verdict with the actual output you saw for each step. **Do not open a PR, close issues, file follow-ups, push, merge, or run any review skill** — those are the pipeline's steps.

---

## Not part of this implementation

Recorded so a fresh implementer does not helpfully do them.

- **Closing #32 and #33.** Neither is a no-change ruling — both ship text and both close on merge, and the PR body carries both rulings, so there is no separate issue-close comment for either (design A5). The design's `## PR` section is the PR body; the pipeline writes it.
- **Filing the concurrent-bump collision issue** (design A6) — two concurrent branches deriving their version bump from the branch base, so a merge can silently reuse a published version. The pipeline files it at integration from *The concurrent-bump collision is a separate concern*, deduping against open issues first, and it must carry the cross-link that minor-always makes the collision deterministic. It touches no file in the authorized set, and nothing about this change's own edits touches a version, so the collision cannot bite this branch.
- **Issues #39, #40 and #41** — filed by this design's own review, none of them implemented here and none touching a file in the authorized set (design A10).
- **Pushing, opening the PR, reviewing, merging.**

Hard-excluded by the design's *Out of scope* — a proposal to touch any of these is a blocker, not a task: `CONTEXT.md` (this change coins no repo concept; *minor segment*, *merge-base blob* and *line-index comparison* are standard vocabulary), `plugins/` and `.claude-plugin/` and every `plugin.json` (**no version is bumped**), `scripts/` (`design_blocks.py` is *used*, never modified; `check-sync.py` is not touched — adding the copies' unreachable `out and` guard would make the source worse), the five existing `split_lines` copies in the gh-28/29 design and plan (records of what was executed), `docs/adr/` (no ADR is warranted for either ruling), `.claude-plugin/marketplace.json`, and every pre-existing file under `docs/superpowers/`.

## Plan self-review

- **Spec coverage.** *Block 0* → Task 1. *Block 1* → Task 2. *Verification* steps 0–8 → the Task 3 Step 11 table, each row naming every step that runs it; steps 1–5 additionally run inside Tasks 1–2 so a failure is caught before the commit. *The edit* (whole-line replacement, gh-7/gh-24 precedent) → *File map*. *Out of scope* → Global Constraints plus *Not part of this implementation*. *Length budget* → the Architecture paragraph, informational only, per A9. A1 → both appliers select by content and assert uniqueness. A3 → Tech Stack. A4 → Task 3 Step 9. A7 → the `git grep` constraint. A8 → §V5's preamble and Task 2 Step 7. A9 → Task 1 Step 1 and Task 3 Step 2. A2, A5, A6, A10 → *Not part of this implementation*. The design's `## PR` body is the pipeline's, not a task's.
- **Placeholder scan.** No TBDs. Every command carries its expected output; every Python snippet is complete and runnable as written; every red/green expectation quoted here was produced by running the check against this checkout at base `b4b5d1c` (red directly, green by applying both blocks to an in-memory copy of the file).
- **Retype check — the single most important property.** No step in this plan reproduces block 0 or block 1, in whole or in part, and this plan contains no reference copy of either. Both appliers obtain their bytes from `read_blocks(DESIGN, [1, 1])` and write `want` unmodified. The only literals typed anywhere near the blocks are four ASCII guard strings — `" **Always the minor segment**"`, `"**Always:**"`, `"**When the change has a design doc**"`, and the residue phrase `'expecting no hits. **When the change'` — each reproduced verbatim from the design's *Verification* section, each compared against and never written. A wrong guard string cannot corrupt `CLAUDE.md`: it makes the applier raise `SystemExit` before writing, or makes §V2 report `MISMATCH:`.
- **Duplication.** §V1, §V2 and §V5 each have exactly one copy in this plan; the three tasks point at them by ID and absolute path rather than re-pasting, so there is nothing to keep in step. That is the same reasoning `CLAUDE.md` applies to mirrored text, and the precedent set by the gh-28/29 plan. The two appliers are genuinely different programs (different selectors, different guards) and are correctly not shared.
- **Type consistency.** `DESIGN`, `TARGET`, `HEAD_END`, `TAIL_START`, `want`, `b0`/`b1`, `pre`/`tail` and `at` mean the same thing in every snippet. `read_blocks(DESIGN, [1, 1])` is called with the identical shape argument in all four places it appears.
- **Intermediate-state honesty.** Task 1 ends with §V2 and §V5 both reporting `FAIL`, by construction — they assert the *final* two-line state and Task 1 delivers one of the two lines. Each of those steps states the exact expected output, names which failure is expected, and enumerates the failure lines that would instead mean a stray edit. Task 2 takes both to green.
