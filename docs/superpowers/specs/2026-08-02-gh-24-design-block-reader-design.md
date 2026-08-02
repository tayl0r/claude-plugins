---
dev-flow:
  slug: gh-24-design-block-reader
  stops: [pre-merge]
  docs: commit
---

# gh-24: share the design-block reader, keep the mapping per change

## Goal

Close issue #24 by moving the one part of the design-conformance check that never varies — the fenced-block reader and the shape guard that immediately follows it in all 23 measured instances — into `scripts/design_blocks.py`, and rewriting the final sentence of `CLAUDE.md` line 9 so it keeps the per-change ruling for the parts that do vary while naming the reader.

Three files change: a new `scripts/design_blocks.py`, one line of `CLAUDE.md`, and a new root `.gitignore` — the repo's first, because making `scripts/` importable makes it the first directory here that CPython writes build output into. **No plugin file is touched and no version is bumped** — nothing here ships into a plugin cache, so the version-keyed-cache rule does not apply. That is a conclusion, not a deferral: there is no HALT in this design.

The 23 existing copies are **not** rewritten. See *Question 2*.

## Scope check — one subsystem, three files

One subsystem: this repo's own verification convention for hand-edited Markdown. `scripts/design_blocks.py` is new, imported by nothing that exists today. `CLAUDE.md` is enrolled in no mirror pair, ships nowhere, and `scripts/check-sync.py` never reads it. The `.gitignore` is not a second subsystem: it exists solely because this change makes `scripts/` importable, and it names only the artifact that import creates (*The `.gitignore`*). There is nothing else to split off and nothing to decompose.

## What is actually duplicated (measured on `main` @ `c8b2182`)

Issue #24 counts 23 instances across 9 documents and 5 issues. Re-measured here, with three findings the issue does not have:

**One signature, 23 members, 16 lines each.** Normalizing only the `DESIGN = "..."` line, dropping the per-change constants interleaved into it (`TARGET`, `ANCHOR`, `OLD`, `PAIR`), and hashing the span from `import sys` through the loop body yields a single hash with 23 members. Zero drift.

**All 23 are followed immediately by a shape assert — 23 of 23, no exceptions.** The one instance that does anything else first (the gh-20 plan's pre-flight probe) prints the shape and then asserts it. There is no measured call site that reads blocks without declaring the shape it expects.

**That adjacent assert line has three spellings.** Measured with `git grep -h -o 'assert \[len([bx]) for [bx] in blocks\].*'`, normalizing the shape literal:

| Count | Spelling |
|---|---|
| 17 | `[len(b) for b in blocks]`, message `design code-block shape changed; stop and re-read the design` |
| 3 | `[len(x) for x in blocks]` (gh-10), same message |
| 3 | `[len(b) for b in blocks]`, message `design plain-fence shape changed; stop and re-read the design` (gh-26) |

**All 23 sit inside tagged fences** — 14 with the info string `bash`, 9 with `sh` — never inside a plain one. That fact matters for *Question 2* and is measured, not assumed.

The inference that decides where the seam goes: **drift is exactly zero in the 16 lines that get copied wholesale, and non-zero in the single line below them that gets retyped with a per-change literal.** The line that varies is the line that drifted. Whatever else is true about this duplication, the guard is not safely left to retyping — so the seam takes the guard with it.

## Decision

Build `scripts/design_blocks.py`, exposing:

- `read_blocks(design_path, shape) -> list[list[str]]` — the design's plain (untagged) fenced blocks, in document order, as lists of lines, returned only after their shape matches the shape the caller declares. `shape` is a **required positional argument**, not an option a caller must remember; a mismatch exits non-zero with the actual and wanted shapes.
- `python3 scripts/design_blocks.py <design-path>` — prints that shape and one preview line per block.

The CLI is kept, but not on the claim it first invites. The *shape* is obtainable without it — `read_blocks(<design>, [])` fails and names the actual shape in its message — so "the only way to get the shape" would be false, and nothing here rests on it. What nothing else supplies is *which block is which*. `read_blocks` guards a list of block lengths, so two blocks of equal length are interchangeable to it: the gh-20 design's shape is `[1, 1, 1, 2, 1, 1, 1, 1, 1, 1]`, and mistaking `blocks[5]` for `blocks[6]` there passes the guard, writes the wrong text into the wrong target, and is then confirmed by the assertion written from that same wrong index — silent, self-consistent, and invisible to every guard in this design. Counting plain fences by eye in a document that also carries a dozen tagged ones is where that off-by-one comes from, and under dev-flow the plan author is not the design author, so the mapping must be recovered rather than remembered. That it is recovered by hand today is on the record: the gh-20 plan's edit table carries a hand-written label column — `("block 5, rubric bullet 3", blocks[5], …)` — which is the CLI's preview output, reconstructed manually. `b[0][:70]` per block is the one defence against the only failure class a required `shape` argument cannot cover. Its price is four docstring lines, `import sys`, and `main` with its dunder. Worth it.

Everything below the guard stays exactly where it is: which block goes to which file, the anchor each edit resolves against, whether the script applies or verifies, what each target must satisfy. `CLAUDE.md`'s ruling that those are per change is untouched and restated.

### Why the seam sits precisely there

The invariant/variant boundary is measured, not guessed. Above it: 23 of 23 byte-identical readers and 23 of 23 immediate shape guards. Below it: four distinct shape literals, appliers versus verifiers, and a different tuple schema every time. The extracted side takes exactly one argument beyond the path — `shape` — and that argument is a literal the caller already writes today, on the very next line. **Nothing is parameterized that was not already a per-call literal.** That is the test that separates this from a runner.

### The call site

```python
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
DESIGN = "docs/superpowers/specs/<design>.md"
blocks = read_blocks(DESIGN, [1, 1, 2])
```

Six lines replacing seventeen (the 16-line reader plus its assert): **11 lines saved per instance**, and — the part that matters more — its 13 lines of parsing logic and one hand-typed guard stop being something an author produces and a reviewer reads.

The function is named `read_blocks`, not `blocks` as issue #24 sketches, for a measured reason: all 23 instances bind their result to the local name `blocks` and index it downstream as `blocks[3]`. Importing a function called `blocks` would shadow that name at every call site, forcing either a rename of the local or `blocks = blocks(...)`, which breaks on a second call. `read_blocks` leaves every line below the call unchanged.

## The new file

Block 0 is `scripts/design_blocks.py` in full. It is deliberately pure ASCII — a mistyped copy fails loudly rather than passing — and it spells the fence as `chr(96) * 3` for the same reason the inline readers do: the source is quoted inside Markdown fences in this document and in the plan, and a literal fence would terminate them.

```
#!/usr/bin/env python3
"""Read a design doc's plain fenced blocks, for design-conformance checks.

CLAUDE.md requires every change carrying a design doc to add a python3 check
that re-reads the design's replacement text from disk rather than retyping it.
The block-to-file mapping and the assertions each target must satisfy differ
per change and stay in that check; only the reader is shared.

    import sys
    from pathlib import Path
    sys.path.insert(0, "scripts")
    from design_blocks import read_blocks
    DESIGN = "docs/superpowers/specs/<design>.md"
    blocks = read_blocks(DESIGN, [1, 1, 2])

read_blocks returns the plain (untagged) fenced blocks in document order, as
lists of lines, having first checked they have the shape the caller indexed
its edits against. A mismatch exits non-zero rather than returning: a design
whose blocks moved silently misroutes every edit indexed off them. The shape
is a required argument, not an option to remember.

Run this file as a script to obtain that shape and the block indices:

    python3 scripts/design_blocks.py <design-path>

Paths are taken as given, so a relative one resolves against the current
directory -- like the inline reader this replaces, and like every target path
in the same check. Every failure detected here -- a design that cannot be
read, a fence that cannot be parsed, a shape that moved -- exits non-zero with
one line on stderr rather than a traceback.

Fence detection matches the inline reader exactly on well-formed input: a line
whose stripped form opens with three backticks, an empty info string for a
plain block. Three-backtick fences are the only ones parsed, so the two inputs
that would otherwise shift every block index unnoticed are refused rather than
guessed at: a longer fence, and a fence that is never closed. It follows that
a plain block cannot hold a line that is exactly three backticks -- that line
closes it -- so a design must give text containing fences as a tagged block,
or build the fence in code the way this file does.

Design: docs/superpowers/specs/2026-08-02-gh-24-design-block-reader-design.md
"""

import sys
from pathlib import Path

FENCE = chr(96) * 3


def _blocks(design_path):
    """Every plain (untagged) fenced block, in document order, as lists of lines."""
    try:
        text = Path(design_path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise SystemExit("cannot read design %s: %s" % (design_path, e))
    blocks, cur, mode, opened = [], None, None, 0
    for n, line in enumerate(text.split("\n"), 1):
        s = line.strip()
        if s.startswith(FENCE + FENCE[0]):
            raise SystemExit("%s line %d: this reader parses three-backtick"
                             " fences only; a longer one mis-indexes every"
                             " block after it" % (design_path, n))
        if mode is None:
            if s.startswith(FENCE):
                mode, cur, opened = s[3:], [], n
        elif s == FENCE:
            if mode == "":
                blocks.append(cur)
            mode, cur = None, None
        else:
            cur.append(line)
    if mode is not None:
        raise SystemExit("%s: the fence opened at line %d is never closed; a plain"
                         " block cannot contain a three-backtick line"
                         % (design_path, opened))
    return blocks


def read_blocks(design_path, shape):
    """_blocks, guarded by the shape the caller indexed its edits against."""
    blocks = _blocks(design_path)
    actual = [len(b) for b in blocks]
    if actual != list(shape):
        raise SystemExit(
            "design code-block shape is %s, want %r; stop and re-read the design"
            % (actual, shape))
    return blocks


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 scripts/design_blocks.py <design-path>")
    blocks = _blocks(sys.argv[1])
    print("shape: %s" % [len(b) for b in blocks])
    for i, b in enumerate(blocks):
        print("  [%d] len=%d: %s" % (i, len(b), b[0][:70] if b else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Four details are deliberate and would be wrong to "clean up":

- **`raise SystemExit`, not `assert`.** The contract these checks have with their caller is an exit code plus a legible message, and `assert` is a no-op under `python3 -O`. Every failure the file detects — a design it cannot read, a fence it cannot parse, a shape that moved — gives exit 1 and one line on stderr instead of a traceback. That is not a new standard: `scripts/check-sync.py` already states it for its own reads (*"never let them escape as a traceback"*, at `READ_ERRORS`), and this file catches the same `(OSError, UnicodeDecodeError)` tuple with the same `cannot read <path>: <exc>` message shape. The shape message names the actual shape, which the `assert` it replaces never did, and renders the wanted one with `%r`, so a `shape` mistyped as the string `"11"` reads back as `'11'` rather than being silently iterated into a list of characters. One failure is deliberately left as a traceback: a `shape` that is not iterable at all raises `TypeError` at the caller's own line, which is where a wrong caller literal belongs.
- **`_blocks` is private and unguarded; `read_blocks` is public and required-guarded.** The only unguarded read in the repo is the discovery CLI — which is precisely the "I do not know the shape yet" case. Every programmatic read declares its expectation. That is the correct-by-default seam the design rubric asks for, and it is what makes the guard un-forgettable rather than merely conventional.
- **`sys.path.insert(0, ...)`, not `append`.** A conformance check must be certain it loaded *this repo's* reader; position 0 guarantees that. The cost is that any future module in `scripts/` shadows a same-named stdlib module inside these heredocs — bounded, since `scripts/` holds one importable module, and stated here so it is a known cost rather than a surprise.
- **The reader refuses input it cannot parse, rather than dropping it.** Two inputs shift every block index without changing anything the shape guard can see, because the author derives the shape literal from the same mis-parse: a fence longer than three backticks, and a fence that is never closed. Both are refused, by line number. This is the one place the helper does *not* reproduce the 23 inline readers — they dropped an unterminated final fence silently, a behaviour inherited rather than chosen — and it closes the only path by which this helper could hand back wrong blocks and still report OK: an applier writes the block it is given (`plans/2026-08-02-gh-26-family-name-plan.md`, `lines[i:i + 1] = want`) and the verifier then compares that same block against what the applier wrote. It is not hypothetical. `plans/2026-07-24-gh-6-docs-policy-plan.md` wraps replacement text containing fences in four-backtick fences — correct Markdown, which this parser mis-closes at the first three-backtick line inside — so its plain blocks bear no relation to its author's intent. Measured across every Markdown file in the repo: that plan is the only one affected, and none has an unterminated fence. The refusal costs nothing today and the five differential designs in *Question 3* parse to exactly the shapes recorded there.

## The `CLAUDE.md` sentence

Block 1 is the complete new line 9 of `CLAUDE.md` — the whole bullet, not just the replaced tail. Whole-line replacement is what gh-7 used for this same line (`plans/2026-07-27-gh-7-review-depth-plan.md`, Step 4), and it is the stronger check: an exact whole-line match at a known index cannot be satisfied by a fragment landing in the wrong bullet.

Only the final sentence differs from the current text. It keeps the runner ruling verbatim — issue #24's own analysis is that that half holds — sharpens what "differs every time" ranges over, and names the reader with both the discovery command and the call form.

```
- **Some files are mirrored across `dev-flow` and `dev-flow-worktree` and must be edited in both.** `python3 scripts/check-sync.py` enforces what can be enforced mechanically — the `adversarial-review/SKILL.md` pair (line-for-line identical after `dev-flow-worktree` → `dev-flow`, minus declared exceptions) and the `description` duplicated between each `plugin.json` and `.claude-plugin/marketplace.json`. It runs on every PR. The pipeline `SKILL.md` pair and the two `README.md`s are too divergent to check mechanically — mirror those by hand. **`check-sync.py` proves the two copies agree with each other, never that either is correct**: text mangled identically in both sides passes it, and so does an edit missed on both. So any change to a mirrored pair, machine-checked or hand-mirrored, must also verify against something *outside* the pair. **Always:** grep for the exact phrases the edit removes, expecting no hits. **When the change has a design doc** that gives replacement or inserted text as fenced blocks: also add a short `python3` check that re-reads those blocks from the design on disk, never retyped, asserting each appears verbatim in its target and, for an insertion, directly after its anchor line. Write that check per change — the block-to-file mapping and the assertions differ every time, so there is no shared runner to call. The *reader* is not per change: run `python3 scripts/design_blocks.py <design>` to get the block shape and indices, then have the check `sys.path.insert(0, "scripts")` and call `read_blocks(<design>, <shape>)` — it re-reads the blocks and exits non-zero if the shape moved — instead of re-typing the reader.
```

The exact phrase this edit removes, for the residue grep, is `the block-to-file mapping differs every time` — pure ASCII and unique.

## The `.gitignore`

`scripts/design_blocks.py` is the first module in this repo meant to be *imported*. The call form above — `sys.path.insert(0, "scripts")` then `from design_blocks import read_blocks` — makes CPython write `scripts/__pycache__/design_blocks.cpython-3XX.pyc` into the working tree, every time any conformance check runs, in every checkout, forever. Measured, not assumed: the file appears on the first import, `git check-ignore` reports it as not ignored, and this repo has never had a `.gitignore` — `git log --all -- .gitignore` is empty, so none was ever removed on principle either.

The artifact is untidy, but the harm is not confined to this change:

- **It never reaches `git diff --stat`,** because it is untracked — step 1 is blind to it unless something stages it. What stages it is a broad `git add -A`, which dev-flow's own contract names as a live hazard it cannot prevent: *"it cannot stop an Execute-stage implementer's broad `git add` from sweeping in files it touches"*. Step 1 would then catch it as an extra row — but only for *this* change, whose step 1 was written knowing to look.
- **It trips dev-flow's dirty-checkout gate on every later run.** That gate inspects `git status --porcelain`, which reports untracked non-ignored files, and on any output the orchestrator halts and asks the user — by its own description the only place the pipeline interrupts a run. A leftover `.pyc` therefore turns this repo's default workflow from autonomous into interrupting, permanently; and the gate's *proceed as-is* answer is precisely the one that lets the next change's broad `git add` commit it into an unrelated PR whose step 1 is not looking for it.

So the fix has to be a property of the repo, not a note in this change. Three candidates, against the rubric's preference for correct-by-default seams:

- **`sys.dont_write_bytecode = True` at the call site, or `python3 -B`.** Works — measured — but every future author must remember it, in every heredoc, forever, with no signal when they forget. It would have to be written into the `CLAUDE.md` sentence and repeated in all 3–7 checks per change, taxing the very call site whose brevity is this change's justification. That is the "each caller must remember a manual step" failure mode the rubric names — the same shape as the hand-typed guard this design is extracting.
- **The same flag inside `design_blocks.py` itself.** This would be the ideal fix — repo-wide, no new file, nothing to remember — and it **does not work.** Measured: CPython's loader writes the `.pyc` in `get_code()`, before the module body executes, so a module cannot suppress its own caching. `scripts/__pycache__/` appears anyway. Recorded so it is not re-proposed.
- **A `.git/info/exclude` entry.** Per-clone and per-machine, so nobody inherits it: it cannot appear in this change's diff, cannot be reviewed, and cannot be verified — a `git check-ignore` assertion would pass on the author's machine and fail in a fresh clone, which is worse than no assertion at all. dev-flow does write to that file, and its stated reason — *"a local exclude, never a committed `.gitignore` edit — which would itself pollute the PR diff"* — is a rule about a **tool editing a host repo it does not own**. This repo owns its own diff, and the artifact is created by this repo's own committed convention.

**Decision: a committed root `.gitignore`, block 2, naming only that artifact.** One file, zero per-author memory, effective in every clone and every linked worktree, and it makes both failure paths above unreachable rather than merely detectable.

```
# Bytecode from importing scripts/design_blocks.py in design-conformance checks.
__pycache__/
*.pyc
```

`*.pyc` is not redundant with `__pycache__/`: it covers `compileall -b` and any legacy sibling `.pyc`, for one line. Nothing else is listed. dev-flow's own scaffolding paths (`.claude/worktrees/`, `.claude/dev-flow.local.md`) stay in `.git/info/exclude`, where dev-flow puts them itself — duplicating them here would add a second owner for a question that already has one — and a speculative ignore list for tooling this repo does not use would be scope creep.

## Engaging the counter-argument

### "Zero drift across 23 copies, so the safety argument is a prediction, not an observation"

Largely conceded, and worth pricing exactly rather than waving at. What would a mistyped hand-copy actually do?

- **Most mistypes do not parse.** A dropped colon, a mangled indent, `blcoks` — `SyntaxError`, `IndentationError`, `NameError`. Loud, immediate, unmissable.
- **Mistypes that parse but change the block *count* are caught by the following shape assert.** `s[3:]` → `s[2:]` leaves every info string non-empty, so no block is ever collected and the shape is `[]`. `if mode == ""` → a truthiness test collects tagged blocks too. Dropping the `mode, cur = None, None` reset inverts every fence boundary after the first. All three change the shape and the assert fires.
- **Exactly one class is silent: a mistype that changes block *content* without changing the count.** `cur.append(line)` → `cur.append(s)` is the realistic instance — it strips each block line, so the count is identical and the assert passes. It is inert wherever a design's blocks start at column 0, which is most of them; it is not inert where a block is indented, and indented blocks do occur (`specs/2026-07-29-gh-20-diff-terminology-design.md` block 8 is `   - Performs an **inline**`). A so-mistyped applier writes a dedented line into a shipped file, and `check-sync.py` cannot see it, because both mirror copies would be dedented identically — the exact hole `CLAUDE.md` already warns about in the sentence before this one.

So: the assert is a near-total guard with one narrow residual hole, and 23 of 23 copies are clean. **The safety argument is real but small, and it is not what this change rests on.** Anyone weighing this design should discount it accordingly.

What the change rests on is a different property. This is not maintained duplication — the 23 copies never need to change together and never will. It is **re-derivation**: the reader's 16 subtle lines, which an author must produce correctly and a reviewer must read and confirm, once per instance, forever. The design rubric's bullet is about exactly that shape of problem — *"if the thing touched is one of a known kind (connectors, handlers, jobs…), put the fix at the shared seam so current and future members inherit it"* — with the demand bar at *"planned siblings, 2+ instances"* (`~/.claude/plugins/cache/taylor-plugins/dev-flow/2.6.0/skills/adversarial-review/SKILL.md`). The demand is 23 instances across 5 changes, and it recurs **once per change regardless of the change's size**: gh-26 was a one-line Markdown edit and paid the tax three times. The growth rate tracks how often dev-flow runs, and dev-flow is this repo's default workflow.

(Issue #24 quotes that rubric bullet as *"one of a known family"*. That spelling was superseded by `0c05098`; the shipped text says **kind**, and `CONTEXT.md`'s **Family** entry reserves *family* for a product line. These 23 copies are a *kind*, not a family. This design uses the shipped vocabulary throughout.)

### "These are plan documents, not runtime code"

Fully accepted — and it has two consequences, both taken.

First, it is the reason the 23 are not rewritten (*Question 2*). Second, it means the payoff is **future-only**, and the issue's arithmetic overstates it. *"~260 lines across the family"* counts historical documents that will not be edited. The honest figure is 11 lines × instances-per-future-change — and the unit has to be named or the range is unreadable. **One dev-flow run produces one design and one plan and commits both, so a run's cost is its design and its plan added together.** On that basis the five measured runs are gh-10 3 (0 design + 3 plan), gh-26 3 (1 + 2), gh-7 4 (1 + 3), gh-16 6 (1 + 5), gh-20 7 (1 + 6): a range of **3–7 instances per run, so 33–77 lines per future dev-flow run**, median run 4 instances and 44 lines. The low end is 3, not 2 — 2 is gh-26's *plan* alone, and pricing a plan-only low against a design-plus-plan high is the same basis switch this paragraph faults *"~260 lines"* for. Add one fewer reader to author and one fewer to review per instance. That is the number this decision should be judged on.

### "dev-flow executes plans task-by-task, so the executor only ever sees one copy"

Accepted without qualification: there is **no executor-context saving**. The saving accrues to the plan author, who must produce the reader; to the plan reviewer, who reads 2–6 copies of it inside one plan document (gh-26 2, gh-7 3, gh-10 3, gh-16 5, gh-20 6 — this is the per-*document* unit, not the per-run unit above); and to the design reviewer, since four of the five designs carry a copy too. Issue #24 records that gh-26's plan-stage review deleted a would-be 24th copy — evidence that a reviewer is already spending attention on this and that the review is acting as a partial, within-document-only brake.

### "A partial seam may be the worst of both worlds"

It is not, and the distinction is precise. Worst-of-both-worlds is what happens when a seam is placed *inside* the variation, so the shared thing must grow parameters that encode the variants — which is exactly what a runner would need (a machine-readable annotation schema on every design doc) and exactly why option D stays rejected. Here the seam is placed on a measured boundary with 23 of 23 identical on one side and four distinct shape literals and a different tuple schema on the other, and the extracted side gains no parameter that was not already a literal at the call site. A partial seam is the *right* answer whenever the invariant part has a clean edge; this one's edge was measured.

## The questions this design must answer

### Question 1 — bootstrap and self-application

**Yes: this change's own design-conformance check imports the helper**, and #18's objection does not apply.

#18's recorded reasoning (`specs/2026-07-27-gh-7-review-depth-design.md`) was that gh-7 could not extract because the extraction would have had to happen inside a plan whose subject was something else, making the helper's existence an incidental side effect that a later task then silently depended on. Here the helper **is** the plan's subject and Task 1's whole deliverable. A later task consuming an earlier task's deliverable is not a hidden coupling — it is what a plan is. The plan states the dependency in the brief, so no task infers it.

The circularity is worth checking rather than asserting, because the check that proves `CLAUDE.md` landed correctly would itself run through the new reader. It is benign: `read_blocks` only reads and guards. A bug in it yields a wrong expected block, and a wrong expected block *fails* the byte-for-byte comparison against `CLAUDE.md` — it does not silently pass. The only way a helper bug produces a false OK is if it returned some other block that happens to match the target exactly, which still proves the target matches a fenced block of this design. There is no failure mode in which a broken reader hides a mismatched `CLAUDE.md`.

The upside is real: the change's own conformance check becomes the helper's first end-to-end exercise, at zero extra cost. It is backed by the differential check in *Question 3*, which is what actually establishes that the helper reproduces the readers it replaces.

### Question 2 — the 23 existing copies are not rewritten

**Decision: leave all 23 exactly as they are.** Deliberately, for these reasons, in this order.

**They are records of what was executed.** `plans/2026-07-27-gh-7-review-depth-plan.md` Step 4 says *"Copy this exactly."* Rewriting it to import `scripts/design_blocks.py` would make that instruction name a file that did not exist on 2026-07-27 — the record would then claim a check was run in a form that could not have been run at the time. That is falsifying a record, and it is the decisive reason on its own.

**A rewritten record acquires a dependency it never had.** Today each of the 23 scripts is self-contained: it runs in any checkout of its own era. Rewritten, it runs only in a checkout that already has the helper. Records should be runnable as of their time, or not at all.

**One argument against rewriting turns out not to hold, and is dropped rather than kept for effect.** It would be natural to worry that editing a design doc's fenced blocks perturbs that document's own recorded assertions. Measured: it does not. All 23 prologues sit inside fences whose info string is `bash` or `sh`, so none of them is counted by any plain-fence shape assert; and no document under `docs/superpowers/` asserts its own line count — every line-count assertion in the corpus targets `SKILL.md`, `CONTEXT.md`, or `CLAUDE.md`. A rewrite would be mechanically safe. It is still wrong, for the two reasons above.

**Accepted cost.** Issue #24's measurement command — `git grep -c 'for line in Path(DESIGN).read_text' -- 'docs/superpowers/*'` — will still sum to 23 after this lands — but only once this run's own design and plan, which quote the pattern in prose, are excluded. Unexcluded it sums to more than 23: `git grep -c` counts matching *lines*, not documents, and this design alone contributes two. So a naive re-measurement could read as "the change did not happen". The mitigation is that the count is now a **fixed historical constant rather than a growing one**: this change adds no 24th copy, and *Verification* step 8 asserts exactly that, with the exclusion pathspec that makes the assertion mean what it says. Any future re-measurement should be scoped to documents created after this commit.

**The second accepted cost, and what carries adoption.** Leaving the 23 alone leaves 23 documents that carry no hint their reader is superseded, and this repo's authoring habit is demonstrably imitative: 23 byte-identical copies written across five changes on five separate days were not independently derived, and this design does precedent lookup itself at *The `CLAUDE.md` sentence*. So a future author skimming a recent plan for structure finds the old form. What outranks it is the rule, not a marker in those files — and the evidence that the rule reaches plan authors is the duplication itself: **all 23 copies exist because their authors read `CLAUDE.md` line 9 and obeyed it.** The sentence that manufactured them is the sentence this change edits, and the replacement is imperative, ending *"instead of re-typing the reader."* It is also auto-loaded rather than looked up — dev-flow drafts plans in a `general-purpose` produce-subagent pinned to the repo root (`dev-flow/SKILL.md`, Stage 2 and the branch lifecycle), so the new line 9 is in context before any prior plan is opened. Precedent then reinforces instead of fighting: this run commits its own design and plan in the import form, every later run adds two more, and the inline count stays frozen at 23. What is **not** guaranteed is attention — a rule at the tail of a long bullet can lose to a freshly-read prior plan. That residual is accepted, not engineered away: the mechanical alternative is a `scripts/check-sync.py` grep guard, which would need a maintained exemption list for the 9 historical documents and for every future document that quotes the pattern (this design and its plan already do), and would give a script that exists to check pair agreement a second, unrelated style duty. That costs more than the risk.

### Question 3 — is a self-test warranted?

**Not a test framework, and not an `if __name__ == "__main__"` self-test that nothing runs. A differential check against history, run once, in the plan.**

The precedent is `scripts/check-sync.py`: 451 lines, no self-test, no framework — because it runs on every PR against real inputs, so its correctness is continuously exercised. `design_blocks.py` inherits that property from its second caller onward. The one moment it is *not* exercised is now, before any caller exists, and that gap is closed by running the CLI against five already-merged designs whose block shapes were independently asserted by their own executed plans:

| Design | Expected `shape:` | Asserted by |
|---|---|---|
| `specs/2026-07-27-gh-10-opus-resolver-design.md` | `[1, 1, 1, 1, 1, 1, 1, 1]` | gh-10 plan, as `[1] * 8` |
| `specs/2026-07-27-gh-7-review-depth-design.md` | `[1, 1, 1, 2, 2, 1, 12]` | gh-7 plan |
| `specs/2026-07-28-gh-16-terminology-collision-design.md` | `[1, 1, 2, 1]` | gh-16 plan |
| `specs/2026-07-29-gh-20-diff-terminology-design.md` | `[1, 1, 1, 2, 1, 1, 1, 1, 1, 1]` | gh-20 plan |
| `specs/2026-07-31-gh-26-family-name-design.md` | `[1]` | gh-26 plan |

Five real inputs, four distinct shapes, every expectation recorded on `main` before this change existed. That is a stronger statement than any test this repo could write from scratch, and it costs five commands. A negative case — a deliberately wrong shape, to see the guard exit non-zero with the right message — completes it. Both live in *Verification*, not in the file.

### Question 4 — the replacement text

Block 1, above: the complete new `CLAUDE.md` line 9, given as a plain fenced block so the plan's conformance check re-reads it from this document on disk rather than retyping it.

### Question 5 — does `sys.path.insert(0, "scripts")` add a new fragility class?

**No. It merges an existing dependency into a single earlier, louder failure.**

Every one of the 23 scripts already requires the current directory to be the repo root, and not only for `DESIGN`: their target paths are relative too (`Path("CLAUDE.md")`, `Path("plugins/dev-flow/skills/adversarial-review/SKILL.md")`). Repo-root cwd is already a precondition of the whole script, not a new one the import introduces. What changes is only *where* a wrong cwd is detected: `ModuleNotFoundError: No module named 'design_blocks'` at the import, two lines earlier than today's `FileNotFoundError` on the design path. Same class, same loudness, strictly earlier — and the import failure names the cause more directly than a missing-file error does.

Resolving the design path against the script's own location — `check-sync.py`'s `REPO_ROOT = Path(__file__).resolve().parent.parent` — was considered and rejected. It would make the design path cwd-independent while the target paths in the same check stayed cwd-relative, so the script would still require repo-root cwd; the only effect would be to hide one of several identical dependencies, making a wrong-cwd run fail later and less legibly instead of not at all. `check-sync.py` can do it because it resolves *every* path it touches that way; a heredoc cannot.

## Rejected alternatives

- **(B) Record a ruling, change nothing (or only reword `CLAUDE.md`).** The strongest rejected option, and it survives every safety argument: zero measured drift, historical documents, no executor-context cost. It fails on the one argument that does not depend on defects — the tax is charged once per change, not once per unit of work, and the invariant part has a clean measured edge. Rewording alone is strictly worse than either acting or leaving it: it would document the duplication as permanent while the count keeps climbing.
- **(A) as sketched in #24 — `blocks(path)`, shape assert left inline.** Rejected on measurement. All 23 call sites assert the shape immediately, and that adjacent line is the *only* place drift actually occurred (three spellings). Leaving the guard outside the seam leaves the drift outside the seam, and makes the guard forgettable — a caller who omits it loses the protection with no signal, which is the "each caller must remember a manual step" failure mode the rubric names. A required `shape` argument costs nothing extra and is correct by default. The `blocks` name is also rejected: it shadows the local name all 23 call sites use.
- **(C-wide) A helper that also absorbs the anchor resolution and the apply/verify step.** Rejected: anchors vary in matching rule (`startswith` versus exact), in count per script (1 to 9), in per-file abort semantics, and in whether the edit replaces or inserts. Absorbing them needs parameters that encode the variants, which is where a partial seam really would become the worst of both worlds. This is option D wearing a smaller hat.
- **(D) A full runner.** Rejected, as #18 and #24 both rejected it: applying a whole change from a design requires a machine-readable annotation schema on every design doc mapping block → file → anchor → operation. The mapping genuinely differs every time; `CLAUDE.md` is right about that and keeps saying so.
- **Rewriting the 23 historical copies.** Rejected — see *Question 2*.
- **A `Design block` glossary entry in `CONTEXT.md`.** Out of scope by constraint, and not warranted anyway: "block" here describes duplicated text, not a concept the repo reasons about. `CONTEXT.md` defines shapes, not one row per word.

## Assumptions

- **Python 3 with `pathlib` is available and is how every check in this repo runs.** Established by `scripts/check-sync.py` and by all 23 instances.
- **`scripts/` is the right home.** It is the repo's only script directory and already holds the only other repo-level tool.
- **The plan's tasks run in order in a single checkout.** dev-flow's contract; Task 1 must land the helper before any later task imports it, and the plan states that dependency explicitly rather than leaving it inferred.
- **No number derived from this design's own blocks is written in this design.** *Verification* carries them as **B0**, **B1** and **B2** and step 0 derives them, so review may edit blocks 0, 1 and 2 without leaving a stale number behind. The plan substitutes concrete values, derived from this document **as committed**. This is deliberate rather than fastidious: the loud shape guard protects step 5's literal and nothing else, and step 1's numbers are eyeballed — a stale one there does not halt anything, it teaches the reader to discount the step that catches a swept-in build artifact.
- **Text assertions use `git grep`, not bare `grep`.** Under Claude Code's Bash tool bare `grep` is a ugrep-backed shell function whose output layout and ordering are not reliable for per-file assertions. Whole-line and index assertions are made in `python3`, where they are exact.

## Out of scope

- **The 23 existing copies.** *Question 2*.
- **`plugins/`, `.claude-plugin/`, and every `plugin.json`.** Nothing here ships into a plugin, so no version moves. `scripts/check-sync.py` reads none of the changed files and its output is unchanged.
- **`docs/adr/` and `CONTEXT.md`.** Out of scope by constraint. An ADR is not warranted: the rule lives in `CLAUDE.md` and its reasoning lives here, and ADR 0001 already covers the repo's duplication policy at the level that matters. If a follow-up is wanted, the honest form is a one-line consequence note on ADR 0001 — worth an issue, not worth an ADR of its own.
- **Issue #19.** This design does not discharge it, but it supplies the measurement #19 asks for and one verdict it can use: the plan-stage simplification lens firing on this duplication would have been *right*, and the fix it should have proposed is this one — a shared reader, not a shared runner. #19's open question was whether the duplication was correct both times; the answer is that it was correct as far as any single plan could see, and wrong across the corpus, which is precisely the gap a plan-stage lens cannot close on its own. Record that on #19; do not change this design because of it.
- **`scripts/check-sync.py`.** Not extended to cover `docs/superpowers/` or these blocks. It checks pairs that must agree; there is no pair here.
- **Ignoring anything but this change's own build artifact.** The new `.gitignore` lists `__pycache__/` and `*.pyc` and nothing else. `scripts/check-sync.py` is unaffected (it globs only `plugins/*/.claude-plugin/plugin.json`) and so is `claude plugin validate .`.

## Verification

Every command runs from the repo root — a precondition of these checks before and after this change alike (*Question 5*). Base commit for every diff below is `c8b2182`. Step 0 derives this design's own numbers, step 1 checks scope, steps 2–4 exercise the helper, steps 5–7 the edit, steps 8–10 the tree.

**Derived numbers — this design writes none of them down.** Three expectations below are functions of this design's own plain fenced blocks, so any review edit to block 0, 1 or 2 moves them. They appear only as **B0**, **B1** and **B2** — the line counts of blocks 0, 1 and 2 — and never as literals, so there is no number here that a block edit can leave stale, and review may rewrite the blocks freely. The **plan** substitutes concrete values, derived from this design *as committed*; that is also what makes step 5's shape guard meaningful rather than tautological — the shape is captured once, at plan-writing time, and checked later, at execute time. A verifier who runs step 5's script without substituting gets `NameError: name 'B0' is not defined`, which is loud and points back here. Two literals remain and neither can be moved by a block edit: step 5's `shape` argument, which *is* the declaration the guard checks, and `CLAUDE.md`'s line count **at `c8b2182`**, a frozen fact about the base commit from which the post-change count is *computed* rather than typed.

0. **Derive B0, B1 and B2.** Run the change's own CLI against this design and read the `shape:` line; its three entries are B0, B1 and B2 in order. If the shape has other than three entries, **stop and report** — this design was edited and the plan is out of date:

   ```sh
   python3 scripts/design_blocks.py docs/superpowers/specs/2026-08-02-gh-24-design-block-reader-design.md
   ```

   This is the CLI's sixth real input and the only one whose expected shape is not a historical record. Before Task 1 has landed the helper — which is when the plan author needs these numbers — the same command works from a scratch copy of block 0, since block 0 *is* the CLI's source: write it to a scratch path and run it from there.

1. **Exactly three files changed, none of them a plugin file.** In git's path order, expect a `.gitignore` row reading `B2 +`, a `CLAUDE.md` row reading `B1 + 1 +-` (B1 lines inserted plus the one deleted), a `scripts/design_blocks.py` row reading `B0 +`, the summary `3 files changed, B0 + B1 + B2 insertions(+), 1 deletion(-)`, and no other row; then `plugins/ untouched: OK`. Read the numbers, not the bar widths, which git scales. **A `scripts/__pycache__/` row means the `.gitignore` did not land, or something staged the artifact before it did — stop and report** (*The `.gitignore`*):

   ```sh
   git diff --stat c8b2182 -- . ':!docs/superpowers/'
   git diff --quiet c8b2182 -- plugins/ .claude-plugin/ && echo "plugins/ untouched: OK"
   ```

   The `':!docs/superpowers/'` pathspec is required: this design's front-matter sets `docs: commit`, so this run's own design and plan are committed on this branch and an unfiltered diff necessarily reports them.

2. **The helper reproduces the readers it replaces, on five real inputs.** Each expected shape was asserted by that design's own merged plan, before this change existed. Expect the `shape:` line of each run to match the *Question 3* table, followed by one `[i] len=N: ...` preview line per block:

   ```sh
   python3 scripts/design_blocks.py docs/superpowers/specs/2026-07-27-gh-10-opus-resolver-design.md
   python3 scripts/design_blocks.py docs/superpowers/specs/2026-07-27-gh-7-review-depth-design.md
   python3 scripts/design_blocks.py docs/superpowers/specs/2026-07-28-gh-16-terminology-collision-design.md
   python3 scripts/design_blocks.py docs/superpowers/specs/2026-07-29-gh-20-diff-terminology-design.md
   python3 scripts/design_blocks.py docs/superpowers/specs/2026-07-31-gh-26-family-name-design.md
   ```

3. **The guard fires, and says what it found.** Expect `design code-block shape is [1], want [9, 9]; stop and re-read the design` and `exit=1`. **The fence is unindented on purpose** — a `python3` heredoc indented under a list item is an `IndentationError`.

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

   And the fence refusals fire. The first is on the one document in the repo that trips it — expect a refusal naming the file and the line of its first four-backtick fence (`line 154` as of `c8b2182`; the number is informative, the refusal is the assertion) and `exit=1`:

   ```sh
   python3 scripts/design_blocks.py docs/superpowers/plans/2026-07-24-gh-6-docs-policy-plan.md; echo "exit=$?"
   ```

   Measured output: `docs/superpowers/plans/2026-07-24-gh-6-docs-policy-plan.md line 154: this reader parses three-backtick fences only; a longer one mis-indexes every block after it`

   The second has no instance in the repo, so it is exercised on a synthetic design in a temp directory; nothing is written under the repo. Expect `... the fence opened at line 6 is never closed; a plain block cannot contain a three-backtick line` and `exit=1`. **The fence is unindented on purpose** — a `python3` heredoc indented under a list item is an `IndentationError`.

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

4. **The CLI rejects a wrong argument count.** Expect `usage: python3 scripts/design_blocks.py <design-path>` and `exit=1`:

   ```sh
   python3 scripts/design_blocks.py; echo "exit=$?"
   ```

5. **Design conformance — all three blocks landed verbatim, in the right place, through the new reader.** This is the check `CLAUDE.md` requires, and it is also the helper's first end-to-end use (*Question 1*). It re-reads all three blocks from this design on disk — never retyped — and requires block 0 to be `scripts/design_blocks.py` byte for byte, block 1 to be `CLAUDE.md` line 9 exactly and uniquely, and block 2 to be `.gitignore` byte for byte. Substitute B0, B1 and B2 from step 0 into the `shape` argument; `CLAUDE.md`'s expected length is **computed** from block 1's actual length, so a block-1 edit cannot leave it stale, and `BASE_LINES` is a frozen fact about `c8b2182`. The script is pure ASCII on purpose; the non-ASCII lives only in the blocks it reads. **The fence is unindented on purpose** — a `python3` heredoc indented under a list item is an `IndentationError`.

```sh
python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
DESIGN = "docs/superpowers/specs/2026-08-02-gh-24-design-block-reader-design.md"
OLD = "the block-to-file mapping differs every time"
BASE_LINES = 29  # CLAUDE.md at c8b2182 -- a fact about the base commit, not about any block
blocks = read_blocks(DESIGN, [B0, B1, B2])
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

   Expect exactly `design-conformance: OK` and `exit=0`. Run it once *before* the `CLAUDE.md` edit — after Task 1 has landed the helper **and the `.gitignore`**, which the plan lands together so this red run isolates the `CLAUDE.md` edit — to watch it discriminate. The red output is exactly:

   ```text
   MISMATCH: the mirror-pair bullet matches design block 1 at lines [], want exactly [9]
   MISMATCH: the pre-change per-change-runner clause survives in CLAUDE.md
   design-conformance: FAIL
   exit=1
   ```

   Both red and green were run against a scratch copy of the post-change tree while this design was written, so the expectations above are measured, not predicted. If the shape guard trips instead (`design code-block shape is ...`), **stop and report**: this design was edited after the plan captured its shape. Re-read the changed block before touching the number — the blocks are what every assertion below indexes, so a moved shape can mean more than a moved count.

6. **Residue — the phrase this edit removes is gone from shipped text.** Expect no output and a non-zero exit:

   ```sh
   git grep -n -F 'the block-to-file mapping differs every time' -- . ':!docs/superpowers/'
   ```

   The pathspec is required: this design quotes the phrase.

7. **Presence — `CLAUDE.md` names the helper.** Expect `CLAUDE.md:1` for each:

   ```sh
   git grep -c -F 'scripts/design_blocks.py' -- CLAUDE.md
   git grep -c -F 'read_blocks(<design>, <shape>)' -- CLAUDE.md
   ```

8. **No 24th copy, and the 9 historical documents are byte-identical to `c8b2182`.** The first command must still print the same 9 lines summing to **23** — this is the first dev-flow change in five to add none. The second must print `records untouched: OK`:

   ```sh
   git grep -c 'for line in Path(DESIGN).read_text' -- 'docs/superpowers/*' ':!docs/superpowers/*gh-24-design-block-reader*'
   git diff --quiet c8b2182 -- docs/superpowers/plans/2026-07-27-gh-10-opus-resolver-plan.md docs/superpowers/plans/2026-07-27-gh-7-review-depth-plan.md docs/superpowers/plans/2026-07-28-gh-16-terminology-collision-plan.md docs/superpowers/plans/2026-07-29-gh-20-diff-terminology-plan.md docs/superpowers/plans/2026-08-02-gh-26-family-name-plan.md docs/superpowers/specs/2026-07-27-gh-7-review-depth-design.md docs/superpowers/specs/2026-07-28-gh-16-terminology-collision-design.md docs/superpowers/specs/2026-07-29-gh-20-diff-terminology-design.md docs/superpowers/specs/2026-07-31-gh-26-family-name-design.md && echo "records untouched: OK"
   ```

   The exclusion pathspec is required and is the whole point of the assertion: this design and its plan both quote the search pattern inside this very command, so without it the count reports more than 23 — `git grep -c` counts matching *lines*, and this design alone contributes two — and says nothing about the 9 historical documents. The glob covers both regardless of their date prefixes.

9. **`python3 scripts/check-sync.py`** — passes, with output identical to before the change. Expect `check-sync: all checks passed` and `mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)`. It reads none of the changed files.

10. **`claude plugin validate .`** — passes; exactly 8 "No author information provided" warnings, exit 0. And versions did not move — expect `dev-flow` at `2.6.0`, `dev-flow-worktree` at `1.8.0`, each labelled with its own path:

   ```sh
   git grep '"version"' -- plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
   ```

## Files the plan will touch

- **Create:** `scripts/design_blocks.py` (block 0, verbatim).
- **Modify:** `CLAUDE.md` line 9 only (block 1, verbatim, whole-line replacement).
- **Create:** `.gitignore` at the repo root (block 2, verbatim) — the repo's first (*The `.gitignore`*). Lands in Task 1 alongside the helper, so *Verification* step 5's red run isolates the `CLAUDE.md` edit.
- **Committed by dev-flow per `docs: commit`:** this design and its plan under `docs/superpowers/`.

Nothing else. No plugin file, no `plugin.json`, no `CONTEXT.md`, no `docs/adr/`, and none of the 9 documents holding the 23 copies.

## PR

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
