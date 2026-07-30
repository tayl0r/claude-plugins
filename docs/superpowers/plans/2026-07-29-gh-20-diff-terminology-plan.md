---
dev-flow:
  slug: gh-20-diff-terminology
  spec: docs/superpowers/specs/2026-07-29-gh-20-diff-terminology-design.md
---

# gh-20 + gh-22: terminology coverage for diffs, and drift coverage for designs and plans — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a trigger-gated **glossary-conformance** angle to `adversarial-review`'s `diff`-mode quality seed, extend the existing terminology pass on the `design`/`plan` correctness seed with a **drift** clause (renaming it *Terminology collision and drift*), repair the four shipped lines that name a glossary concept by a name `CONTEXT.md` rejects, refresh `CONTEXT.md`'s **Angle** enumeration, and bump both plugin versions so the change reaches a user.

**Architecture:** Pure prose-and-manifest change across five files, no code. Two of the files are a `check-sync.py`-enforced **mirror pair** (`adversarial-review/SKILL.md` × 2): **nine edits each** — eight in-place line replacements plus one symmetric two-line insertion — landing byte-identically in both copies, taking both from 87 to **89 lines**. A third file, `CONTEXT.md`, gets one in-place line replacement and stays at **67 lines**. Two `plugin.json` version bumps are load-bearing (the install cache is version-keyed) and follow once the behavior they gate is in place.

**Tech Stack:** Markdown, JSON manifests, `python3 scripts/check-sync.py`, `claude plugin validate .`, `git grep`, inline `python3 - <<'PY'` scripts. No build, no test framework, no linter.

**Authoritative source:** `docs/superpowers/specs/2026-07-29-gh-20-diff-terminology-design.md`. **Every character of every replacement lives in that file and is applied by reading it from disk — this plan deliberately does not restate any of it.** If this plan and the design ever disagree, the design wins — stop and re-read `§Exact change list`.

---

## Global Constraints

Every task's requirements implicitly include this section.

- **Repo root:** `/Users/taylor/dev/claude-plugins`. Every path below is relative to it. Work in place on the existing branch `tayl0r/gh-20-diff-terminology` — **do not create a git worktree, do not switch branches, do not push, do not open a PR, do not merge.**
- **NEVER RETYPE THE REPLACEMENT TEXT.** The design's `§Exact change list` gives its ten replacement/insertion blocks as plain fenced code blocks. Every content edit in this plan is applied by a supplied `python3` **applier script** that parses those blocks out of the design file on disk and writes them into the target. Do **not** transcribe the text by hand, do **not** paste it from a chat message, do **not** use `Edit` with a retyped `new_string`. The design's own verification (Task 4, Step 5) re-reads those same blocks and demands a byte-for-byte line match, so any hand-transcription that drifts by one character fails loudly — and one that drifts *identically in both mirror copies* passes `check-sync.py` at the correct 89 lines and is caught by nothing else. `CLAUDE.md` requires exactly this check for any change to a mirrored pair, because `check-sync.py` proves the two copies agree with **each other**, never that either is correct.
- **Every line number in this plan and in the design is PRE-CHANGE and is not to be trusted.** The design says so in its `§Assumptions recorded`, and `§Exact change list` says "apply the replacements by content match, never by number". Every applier locates its target by **content match on a distinctive ASCII anchor prefix** and asserts that anchor occurs **exactly once** in the file; the line number it prints is a cross-check, not an input. If an applier prints a line number different from the one this plan predicts, that is not a failure — note it in your report and keep going; the conformance script is the authority.
- **Every applier is idempotent.** Re-running one that has already landed prints `already applied: <block>, in <path>` — one line per block, since an applier may carry several — and changes nothing. A task re-dispatched after a partial run is safe to run from Step 1. Every anchor in this plan is a prefix that survives its own replacement, which is what makes that possible.
- **The mirror pair is edited byte-identically in both copies, always in the same step.** `plugins/dev-flow/skills/adversarial-review/SKILL.md` and `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md` are a declared `check-sync.py` mirror pair (line-for-line identical after substituting `dev-flow-worktree` → `dev-flow`, minus one declared exception at line 12, which is above every edit here and does not move). None of the new or edited text contains a `dev-flow` or `dev-flow-worktree` token, so the two copies compare equal in every touched region before canonicalization does anything. A one-sided edit is CI-red.
- **There is no test framework, no build, no linter in this repo.** Do not run `pytest`, `npm test`, `ruff`, or invent one. Every verification step here is an exit code plus stdout from `python3 scripts/check-sync.py`, `claude plugin validate .`, `git grep`, `wc -l`, `git diff --numstat`, or an inline `python3` script given in full below.
- **`claude plugin validate .` emits 8 missing-author warnings. That is expected and is NOT a failure.** Only a non-zero exit or an explicit error is a failure.
- **Scope is exactly five files:** `plugins/dev-flow/skills/adversarial-review/SKILL.md`, `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md`, `CONTEXT.md`, `plugins/dev-flow/.claude-plugin/plugin.json`, `plugins/dev-flow-worktree/.claude-plugin/plugin.json`. Nothing else may appear in the final diff, beyond this run's own `docs/superpowers/` design and plan artifacts. Do **not** touch `.claude-plugin/marketplace.json` (no `description` changes, and Check A does not read `version`), either pipeline `SKILL.md`, either `README.md`, `CLAUDE.md`, `docs/agents/*.md`, `docs/adr/`, `scripts/check-sync.py`, `.github/workflows/`, or any other plugin. The design's `§Blast radius` confirms each of those is untouched, and several of them **do** contain the word `boundary` in its stage-transition sense, which this change deliberately leaves alone.
- **`CONTEXT.md` is edited on exactly one line — the **Angle** definition.** The **Seam** entry and its `_Avoid_: boundary` line, and the **Resolver** entry's `_Avoid_: group agent, judge, arbiter` line, are kept byte-identical on purpose (design `§3. CONTEXT.md`). Do not "also fix" them; the design's whole argument is that those entries are correct and the *shipped text* was wrong.
- **The design doc is read-only reference material.** `docs/superpowers/specs/2026-07-29-gh-20-diff-terminology-design.md` is never edited — every script here only *reads* it. Editing it would silently change what the conformance check compares against.
- **Every inline `python3` script below is pure ASCII on purpose**, including its anchor strings, so that a mistyped copy fails loudly instead of passing. The *content* it moves is full of em dashes and backticks — but you never type that content, the script copies it. **Copy each script exactly, character for character.** The heredoc fences are unindented on purpose: a `python3` heredoc indented under a list item is an `IndentationError`. The `git grep` patterns are the one place where non-ASCII must be typed — three of them carry a U+2014 em dash (`—`), never a hyphen; copy those lines exactly too.
- **The shell hook (`rtk hook claude`, a `PreToolUse` Bash hook) rewrites bare `grep`, `wc`, `git diff`, and `git status` into `rtk` equivalents.** Two consequences bind every step below. (1) **Never use a bare `grep`.** `rtk grep` replaces the distinguishing segment of a path with `...`, reorders its output, and strips leading whitespace, so a per-file assertion cannot be read off it — and a bare `grep` for a `"version"` line returns `rtk grep --help` instead of an answer. Every text assertion in this plan is `git grep`, which the hook does not touch and which searches the working tree including unstaged edits. (2) **On a clean tree `git status --porcelain` prints `ok`, not nothing** — that is `rtk`'s empty-output marker and it is a pass, not a failure. `rtk wc -l` and `rtk git diff` preserve every number this plan asserts (`rtk wc -l` may append a `Σ` total line; `git diff --numstat` and `--stat` are passthrough) — run those as written and read the numbers, not the layout. `python3` and `claude plugin validate` are untouched.
- **`git diff --numstat` is asserted only where an edit replaces a *single* line** — the two `plugin.json` bumps and the `CONTEXT.md` line, where `1  1` is what a one-line replacement means by definition. **Never assert numstat counts for the mirror pair**, which takes eight replacements plus an insertion per file: `--numstat` reports git's minimal edit script over the final content, not "N lines in, M lines out". `wc -l` plus the design-conformance script are what verify those.
- **A presence assertion is one `git grep -cF` per pattern — never one multi-pattern `git grep` with a line-count expectation.** `git grep` prints a matching line *once* however many `-e` patterns hit it, and every design block's substantive content here is a single long line, so two patterns quoted from one block always land on the same physical line: a multi-pattern grep then reports that one line whether both patterns matched or only one, and the count reveals nothing. `git grep -cF '<pattern>' -- <paths>` prints `path:count` for each *matching* file and omits non-matching files, so "one line per target file, each reading `:1`" is an assertion that actually fails when a pattern is missing, and it names which file is short. Residue greps are the opposite case and stay multi-pattern: they expect **no** output, so any hit is a failure whichever pattern produced it.

---

## File map

| File | Responsibility in this change | Lines | Task |
|---|---|---|---|
| `plugins/dev-flow/skills/adversarial-review/SKILL.md` | Mirror-pair copy A. Design blocks **0–8**: the `diff` seed row, the `design` seed row, the angles-block header, the inserted glossary-conformance angle, the renamed-and-extended terminology pass, rubric bullets 3 and 7, and the two Resolution-procedure lines. | 87 → **89** | 1 |
| `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md` | Mirror-pair copy B. The identical nine edits, byte-for-byte. | 87 → **89** | 1 |
| `CONTEXT.md` | Design block **9** replaces the **Angle** definition line (pre-change line 30) so the enumeration names the sixth angle. One line replaced, none added. | 67 → **67** | 2 |
| `plugins/dev-flow/.claude-plugin/plugin.json` | `"version": "2.5.0"` → `"2.6.0"`. Load-bearing: the install cache is version-keyed. | unchanged | 3 |
| `plugins/dev-flow-worktree/.claude-plugin/plugin.json` | `"version": "1.7.0"` → `"1.8.0"`. Same. | unchanged | 3 |

No file is created, renamed, or deleted.

## Design block map

The design's `§Exact change list` holds **ten** plain-fenced blocks. They are indexed **positionally** by every script in this plan, so the index is the contract:

| Block | Design heading | Shape | Target | Anchor (ASCII, matched with `startswith`) | Task |
|---|---|---|---|---|---|
| 0 | Line 28 — `diff` row | 1 line, replace | mirror pair | `\| **diff** \|` | 1 |
| 1 | Line 29 — `design` row | 1 line, replace | mirror pair | `\| **design** \|` | 1 |
| 2 | Line 34 — angles-block header | 1 line, replace | mirror pair | `**The four ` | 1 |
| 3 | Insert after line 40 — the sixth angle | **2 lines** (blank, then the angle), insert | mirror pair | `**Seam placement:**` (block goes *after* it) | 1 |
| 4 | Line 46 — terminology pass | 1 line, replace | mirror pair | `**Terminology collision` | 1 |
| 5 | Line 54 — rubric bullet 3 | 1 line, replace | mirror pair | `- Before fixing at the point of failure` | 1 |
| 6 | Line 58 — rubric bullet 7 | 1 line, replace | mirror pair | `- Value simplicity; widen the lens` | 1 |
| 7 | Line 66 — Resolution procedure, step 3 | 1 line, replace | mirror pair | `3. Each ` | 1 |
| 8 | Line 69 — no-recursion clause | 1 line, replace | mirror pair | `   - Performs an **inline**` (three leading spaces) | 1 |
| 9 | `§3.` — `CONTEXT.md` **Angle** entry | 1 line, replace | `CONTEXT.md` | `**Angle**:` (block goes *after* it) | 2 |

The shape assertion every script carries is `[1, 1, 1, 2, 1, 1, 1, 1, 1, 1]`. **Verified against the design on disk while this plan was written.** If it fires, the design's fenced blocks were added to, removed, reordered, or reflowed — stop and re-read the design; do not renumber the scripts.

**Two anchors deserve their own note.** Block 7's anchor is `3. Each ` — with the trailing space and nothing more — because the replacement changes `3. Each group-agent:` into `3. Each resolver:`, so an anchor containing `group-agent` would not survive its own edit and the applier could not be idempotent. Block 8's anchor carries **three leading spaces**; it is a nested list item. Both were confirmed to occur exactly once per copy, at pre-change lines 66 and 69.

---

## Task ordering and why

**What task ordering buys, and what it does not.** The pipeline merges this PR with `gh pr merge <pr> --squash` — both pipeline `SKILL.md` copies specify that command, and every commit on `main` is a single-parent squash of one PR — so every commit below collapses into one commit on `main`. Nothing installs from this branch either: the marketplace is a GitHub clone of this repo tracking `main`, so the version-keyed cache only ever sees what `main` has. Ordering therefore buys review legibility and a branch that still reads correctly if a run halts partway. It never buys a shipping guarantee, and nothing below is built on one.

**Task 1 is one task across two files, not two tasks**, because the two `adversarial-review/SKILL.md` copies are a `check-sync.py`-enforced mirror pair: a commit that edits one side and not the other is CI-red by construction. Its nine edits are one task rather than nine because they share a single deliverable — the pair at 89 lines, mirror-check green, both new checks reachable — and no reviewer can meaningfully approve the new angle while rejecting the seed-table cell that makes it reachable (design `§1 & 2`: "a sixth is added, so the cell must name it or a prompt-builder resolving the cell ships five"). The two rubric repairs and the two Resolution-procedure repairs are in the same task for the reason the design gives them: they are the defects the drift clause finds in this repo, and shipping the clause without them makes it fire, correctly, on essentially every future artifact.

**Task 2 (`CONTEXT.md`) is separate from Task 1** — different file, no mechanical coupling (`check-sync.py` never reads `CONTEXT.md`), and a separably reviewable claim: the **Angle** entry enumerates its instances, so it goes stale the moment a sixth ships. It stays in **this PR**, never a follow-up — the design's `§3` cites gh-7's ruling that "the glossary changes with the thing it defines", and gh-7's own PR landed as the single squashed commit `4e32e0e`, carrying its `CONTEXT.md` edit and its `SKILL.md` change together. **Same PR is the whole of that constraint**: this PR squashes the same way, so any split into commits satisfies it and only a follow-up PR would not. (gh-7's plan read that ruling as "must land in the same commit as the SKILL.md pair, not merely the same PR" and made three files one task on that basis; under squash the two are one requirement.) Task 2 runs after Task 1 so the enumeration never names an angle that is not yet in the file.

**Task 3 (version bumps) follows Tasks 1 and 2.** Disjoint files, so this is sequencing rather than isolation — and, per the note above, not a shipping guarantee: no ordering of these commits can put a bump in front of the behavior on `main`. What it buys is that the bump is a claim about Tasks 1 and 2, written only once they are true, so a run that halts partway never leaves the branch advertising a version whose behavior is not in it. `dev-flow` 2.6.0 covers copy A, `dev-flow-worktree` 1.8.0 covers copy B; `CONTEXT.md` ships into no plugin and is not gated by either.

**Task 4 runs the design's full `§Verification` steps 1–8 plus a scope check**, and depends on Tasks 1–3 all being complete and committed — the version grep, the full nine-pattern residue grep, and the complete conformance script (which asserts all three file lengths and all ten blocks at once) are only meaningful once every file has landed.

---

### Task 1: The `adversarial-review` mirror pair — nine edits, one commit

**Files:**
- Modify: `plugins/dev-flow/skills/adversarial-review/SKILL.md` (pre-change lines 28, 29, 34, 46, 54, 58, 66, 69 replaced; two lines inserted after pre-change line 40)
- Modify: `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md` (the identical nine edits)
- Test: none — this repo has no test framework. Verification is `check-sync.py`, `wc -l`, scoped residue greps, a scoped design-conformance script, and three byte-identity counts.

**Interfaces:**
- Consumes: nothing. This is the first task.
- Produces: both mirror copies at **89 lines**, carrying design blocks 0–8 verbatim, with the glossary-conformance angle sitting directly after the `**Seam placement:**` paragraph. Task 2's `CONTEXT.md` enumeration describes the angle this task ships; Task 3's bumps are the versions these copies ship under; Task 4's full conformance script re-checks every block.

**Read the design's `§1 & 2. plugins/dev-flow/skills/adversarial-review/SKILL.md and plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md`, its `§Resulting file shape` table, and `§Sync constraint — how check-sync.py still passes` before starting.** You do not need to transcribe anything from them — the applier below reads the text itself — but you do need to know why every edit lands twice and why the insertion must be symmetric.

**What the nine edits are, for orientation only — do not type any of this text:**

- **Blocks 0–2** make the new angle reachable and countable: the `diff` row's quality cell names it, the `design` row's correctness cell names the renamed pass, and the angles-block header goes from "a fifth … all five" to "two … all six". The `plan` row is **not** edited — it refers to "the prose checklist above" and names no pass.
- **Block 3** is **two lines**: one empty line, then the `**Glossary conformance:**` angle. It goes **directly after** the `**Seam placement:**` paragraph. The anchor position is load-bearing and Step 5 asserts it: the same angle inserted after the `Pinned template` paragraph instead would separate it from the header that introduces it, leave a `diff`-mode angle trailing the two `design`/`plan` notes, and pass every other check here.
- **Block 4** replaces the terminology pass with its renamed, extended form. Every sentence #16 shipped survives; the glossary read is hoisted to the front, the existing trigger gains a `**Collision**` prefix, and a `**Drift**` clause is added.
- **Blocks 5–6** repair the design rubric's two Seam-sense `boundary` bullets to `seam`. **One word each; the bullets are the same length before and after** (54 and 27 words). No obligation, concept or bullet is added — that standard is the design's `§Does the rubric edit violate "nothing lands in the design rubric"?`.
- **Blocks 7–8** repair `3. Each group-agent:` → `3. Each resolver:` and `**Group-agents never invoke …**` → `**Resolvers never invoke …**`. `group-resolution agent` on pre-change lines 50 and 79 is **deliberately not repaired** — it is not a name any glossary entry rejects. Do not touch it.

- [x] **Step 1: Confirm the starting state**

```bash
cd /Users/taylor/dev/claude-plugins
git rev-parse --abbrev-ref HEAD
python3 scripts/check-sync.py
wc -l plugins/dev-flow/skills/adversarial-review/SKILL.md plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md CONTEXT.md
```

Expected: branch `tayl0r/gh-20-diff-terminology`; `check-sync: all checks passed` with `mirror pair "adversarial-review" ... OK (87 lines, 1 declared exception)`; and `87`, `87`, `67`. If any of that differs, **stop and report** — the tree is not the state this plan was written against.

- [x] **Step 2: Pre-flight — the design's block shape and every anchor, before anything is written**

This probe writes nothing. It fails loudly if the design's fenced blocks moved (which would silently misroute every edit, since blocks are indexed positionally) or if any anchor is missing or duplicated (which would misplace an edit inside a 15 KB file).

```bash
cd /Users/taylor/dev/claude-plugins
python3 - <<'PY'
import sys
from pathlib import Path
DESIGN = "docs/superpowers/specs/2026-07-29-gh-20-diff-terminology-design.md"
FENCE = chr(96) * 3
blocks, cur, mode = [], None, None
for line in Path(DESIGN).read_text(encoding="utf-8").split("\n"):
    s = line.strip()
    if mode is None:
        if s.startswith(FENCE):
            mode, cur = s[3:], []
    elif s == FENCE:
        if mode == "":
            blocks.append(cur)
        mode, cur = None, None
    else:
        cur.append(line)
print("block shape:", [len(b) for b in blocks])
assert [len(b) for b in blocks] == [1, 1, 1, 2, 1, 1, 1, 1, 1, 1], "design code-block shape changed; stop and re-read the design"
ANCHORS = ["| **diff** |", "| **design** |", "**The four ", "**Seam placement:**",
           "**Terminology collision", "- Before fixing at the point of failure",
           "- Value simplicity; widen the lens", "3. Each ", "   - Performs an **inline**"]
rc = 0
for path in ["plugins/dev-flow/skills/adversarial-review/SKILL.md",
             "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md"]:
    L = Path(path).read_text(encoding="utf-8").split("\n")
    at = [[i + 1 for i, x in enumerate(L) if x.startswith(a)] for a in ANCHORS]
    print(path, "->", [n for hits in at for n in hits])
    for a, hits in zip(ANCHORS, at):
        if len(hits) != 1:
            print("ABORT: anchor", repr(a), "found", len(hits), "times in", path, "-- want 1")
            rc = 1
sys.exit(rc)
PY
echo "exit=$?"
```

Expected: `block shape: [1, 1, 1, 2, 1, 1, 1, 1, 1, 1]`, then one line per copy reading `[28, 29, 34, 40, 46, 54, 58, 66, 69]`, then `exit=0`. Any `ABORT` line, an `AssertionError`, or a different list of numbers means **stop and report** — do not proceed to Step 3.

- [x] **Step 3: Apply design blocks 0–8 — all nine edits, both copies, one script**

One applier carries all nine edits, and each target file is written **once**, after all nine of its anchors have resolved. A missing or duplicated anchor prints `ABORT`, leaves that file **exactly as it was**, and still exits non-zero after the other file is processed: every edit is computed against an in-memory copy and the write happens only once all nine anchors have resolved, so **no file is ever left carrying part of the change**. Nine separate appliers could not promise that — the second can fail after the first has already written. Each edit re-scans the in-memory list for its own anchor, so the insertion's shift of every later line is absorbed automatically.

```bash
cd /Users/taylor/dev/claude-plugins
python3 - <<'PY'
import sys
from pathlib import Path
DESIGN = "docs/superpowers/specs/2026-07-29-gh-20-diff-terminology-design.md"
FENCE = chr(96) * 3
blocks, cur, mode = [], None, None
for line in Path(DESIGN).read_text(encoding="utf-8").split("\n"):
    s = line.strip()
    if mode is None:
        if s.startswith(FENCE):
            mode, cur = s[3:], []
    elif s == FENCE:
        if mode == "":
            blocks.append(cur)
        mode, cur = None, None
    else:
        cur.append(line)
assert [len(b) for b in blocks] == [1, 1, 1, 2, 1, 1, 1, 1, 1, 1], "design code-block shape changed; stop and re-read the design"
TARGETS = ["plugins/dev-flow/skills/adversarial-review/SKILL.md",
           "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md"]
EDITS = [("block 0, diff row",            blocks[0], "| **diff** |",                            "replace"),
         ("block 1, design row",          blocks[1], "| **design** |",                          "replace"),
         ("block 2, angles header",       blocks[2], "**The four ",                             "replace"),
         ("block 3, glossary angle",      blocks[3], "**Seam placement:**",                     "insert"),
         ("block 4, terminology pass",    blocks[4], "**Terminology collision",                 "replace"),
         ("block 5, rubric bullet 3",     blocks[5], "- Before fixing at the point of failure", "replace"),
         ("block 6, rubric bullet 7",     blocks[6], "- Value simplicity; widen the lens",      "replace"),
         ("block 7, resolution step 3",   blocks[7], "3. Each ",                                "replace"),
         ("block 8, no-recursion clause", blocks[8], "   - Performs an **inline**",             "replace")]
rc = 0
for path in TARGETS:
    p = Path(path)
    L = p.read_text(encoding="utf-8").split("\n")
    abort = False
    for name, new, anchor, how in EDITS:
        at = [i for i, x in enumerate(L) if x.startswith(anchor)]
        if len(at) != 1:
            print("ABORT:", name, "in", path, "-- anchor found", len(at), "times, want 1")
            abort = True
            break
        i = at[0] + 1 if how == "insert" else at[0]
        if L[i:i + len(new)] == new:
            print("already applied:", name, "in", path)
            continue
        L[i:i + (0 if how == "insert" else 1)] = new
        print("%s: %s at line %d in %s" % (how, name, i + 1, path))
    if abort:
        print("ABORT:", path, "not written; no edit applied to this file")
        rc = 1
        continue
    p.write_text("\n".join(L), encoding="utf-8")
sys.exit(rc)
PY
echo "exit=$?"
```

Expected: eighteen lines — nine per copy, copy A first, in block order — then `exit=0`. For copy A:

```
replace: block 0, diff row at line 28 in plugins/dev-flow/skills/adversarial-review/SKILL.md
replace: block 1, design row at line 29 in plugins/dev-flow/skills/adversarial-review/SKILL.md
replace: block 2, angles header at line 34 in plugins/dev-flow/skills/adversarial-review/SKILL.md
insert: block 3, glossary angle at line 41 in plugins/dev-flow/skills/adversarial-review/SKILL.md
replace: block 4, terminology pass at line 48 in plugins/dev-flow/skills/adversarial-review/SKILL.md
replace: block 5, rubric bullet 3 at line 56 in plugins/dev-flow/skills/adversarial-review/SKILL.md
replace: block 6, rubric bullet 7 at line 60 in plugins/dev-flow/skills/adversarial-review/SKILL.md
replace: block 7, resolution step 3 at line 68 in plugins/dev-flow/skills/adversarial-review/SKILL.md
replace: block 8, no-recursion clause at line 71 in plugins/dev-flow/skills/adversarial-review/SKILL.md
```

— and the same nine lines for `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md`. These are exactly the post-change numbers in the design's `§Resulting file shape` table. **The insertion line reads `41`, not 40:** it is the blank line the inserted block now occupies, not the anchor line it follows. Blocks 4–8 print their *post-insertion* numbers (48, 56, 60, 68, 71) because the two inserted lines shifted them. An `ABORT` line means an anchor is missing or duplicated — stop and report; do not edit by hand.

- [x] **Step 4: Verify — both copies are 89 lines and the mirror check passes**

```bash
cd /Users/taylor/dev/claude-plugins
wc -l plugins/dev-flow/skills/adversarial-review/SKILL.md plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
python3 scripts/check-sync.py
echo "exit=$?"
```

Expected: `89` for each file, and:

```
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)
check-sync: all checks passed
```

`exit=0`. **`89 lines, 1 declared exception` is load-bearing.** A `LINE_COUNT_FIX` failure means the insertion landed asymmetrically — and the design notes that an asymmetric insertion could not be declared as an exception even deliberately, since the schema declares only same-index, one-line-for-one-line divergences. An undeclared-divergence failure naming a line means a replacement landed on one side only — re-run the applier in Step 3, which fixes exactly the missing side and no-ops the other. `1 declared exception` still reading `1` confirms the line-12 exception did not go stale (it sits above every edit and does not move).

- [x] **Step 5: Verify — scoped residue grep (all eight replaced strings are gone from both copies)**

```bash
cd /Users/taylor/dev/claude-plugins
git grep -n -F -e 'seam-placement angle, inlined' \
               -e "then a fifth of this skill" \
               -e 'and terminology-collision passes' \
               -e '**Terminology collision — the design' \
               -e 'put the fix at the shared boundary' \
               -e 'finds the right boundary' \
               -e 'Each group-agent:' \
               -e 'Group-agents never invoke' \
               -- plugins/dev-flow/skills/adversarial-review/SKILL.md plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
echo "exit=$?"
```

Expected: **no output**, `exit=1`. These are eight of the nine patterns in the design's `§Verification` step 3, scoped to this task's two files; the ninth (`'altitude, seam placement.'`) belongs to Task 2's `CONTEXT.md`. Each is an exact phrase this task's replacements delete, and each returns **2 hits today** (one per copy) — so a surviving hit means one side of the mirror pair was missed, which is the failure `check-sync.py` catches only if the *other* side changed. `-F` is required: the patterns contain `*`, `.` and `-`. The fourth pattern carries a **U+2014 em dash**, not a hyphen; copy the line exactly. The pathspec is required — this plan and the design both quote all eight strings in prose.

- [x] **Step 6: Verify — design conformance, this task's nine blocks**

This is the check that catches what line counts and greps cannot: text mangled *identically in both* mirror copies, or the angle inserted at the wrong anchor. It reads the expected text from the design file on disk, never retyped — the check `CLAUDE.md` requires for exactly this kind of change. This is a task-scoped subset of the design's `§Verification` step 5 — it omits the `CONTEXT.md` block and that file's length, which Task 2 owns. **Task 4 runs the complete, unmodified script.** Copy this exactly.

```bash
cd /Users/taylor/dev/claude-plugins
python3 - <<'PY'
import sys
from pathlib import Path
DESIGN = "docs/superpowers/specs/2026-07-29-gh-20-diff-terminology-design.md"
FENCE = chr(96) * 3
blocks, cur, mode = [], None, None
for line in Path(DESIGN).read_text(encoding="utf-8").split("\n"):
    s = line.strip()
    if mode is None:
        if s.startswith(FENCE):
            mode, cur = s[3:], []
    elif s == FENCE:
        if mode == "":
            blocks.append(cur)
        mode, cur = None, None
    else:
        cur.append(line)
assert [len(b) for b in blocks] == [1, 1, 1, 2, 1, 1, 1, 1, 1, 1], "design code-block shape changed; stop and re-read the design"
PAIR = ["plugins/dev-flow/skills/adversarial-review/SKILL.md",
        "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md"]
WANT = {PAIR[0]: 89, PAIR[1]: 89}
SPEC = [("line 28, diff row",          blocks[0], None,                  PAIR),
        ("line 29, design row",        blocks[1], None,                  PAIR),
        ("line 34, angles header",     blocks[2], None,                  PAIR),
        ("glossary-conformance angle", blocks[3], "**Seam placement:**", PAIR),
        ("terminology pass",           blocks[4], None,                  PAIR),
        ("rubric bullet 3",            blocks[5], None,                  PAIR),
        ("rubric bullet 7",            blocks[6], None,                  PAIR),
        ("resolution step 3",          blocks[7], None,                  PAIR),
        ("no-recursion clause",        blocks[8], None,                  PAIR)]
bad, text = [], {}
for path, want in WANT.items():
    L = Path(path).read_text(encoding="utf-8").split("\n")
    if L and L[-1] == "":
        L.pop()
    text[path] = L
    if len(L) != want:
        bad.append(("file length", path, "%d lines, want %d" % (len(L), want)))
for name, want, anchor, paths in SPEC:
    for path in paths:
        L = text[path]
        at = [i for i in range(len(L) - len(want) + 1) if L[i:i + len(want)] == want]
        if len(at) != 1:
            bad.append((name, path, "found %d times, want exactly 1" % len(at)))
        elif anchor is not None and not L[at[0] - 1].startswith(anchor):
            bad.append((name, path, "sits after %r, want %r" % (L[at[0] - 1][:40], anchor)))
for name, path, why in bad:
    print("MISMATCH:", name, "in", path, "--", why)
print("design-conformance (task 1 subset):", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected: `design-conformance (task 1 subset): OK`, `exit=0`. A `MISMATCH` line names the block and the file whose text or position differs — re-run the applier in Step 3 and re-run Steps 4–6. Never "fix" a mismatch by editing the target by hand.

- [x] **Step 7: Verify — the two glossary repairs are complete across the whole repo**

This is the design's `§Verification` step 4, both halves, and it is deliberately **broader than Step 5's exact strings**: it also fails if a fixer "helpfully" reflows one of the two rubric bullets while keeping the word.

```bash
cd /Users/taylor/dev/claude-plugins
git grep -n -i -e 'shared boundary' -e 'shared-boundary' -e 'right boundary' -- . ':!docs/superpowers/'
echo "exit=$?"
git grep -n -i -e 'group.agent' -- . ':!docs/superpowers/'
echo "exit=$?"
```

Expected: the first command prints **no output**, `exit=1` (today it reports 2 hits in each mirror copy). The second prints **exactly one line** — `CONTEXT.md:15:_Avoid_: group agent, judge, arbiter` — and `exit=0`; today it prints **5** (that line plus lines 66 and 69 in both copies). After the repair, every remaining `boundary` in shipped text names a stage transition, and the only `group agent` left is the glossary's own `_Avoid_:` line, which the never-flag clause puts outside every finding. `-i` and the `.` wildcard in the second pattern are load-bearing — they are what the spaced-spelling grep that produced the design's first census lacked. **`group-resolution agent` on lines 50 and 79 does not match this pattern and is deliberately not repaired.**

- [x] **Step 8: Verify — the three byte-identical duplicated spans**

The design's `§Verification` step 7. Each span is duplicated *inside* one file as well as across the mirror pair, and `check-sync.py` only ever compares the two copies to **each other**, so nothing else covers these.

```bash
cd /Users/taylor/dev/claude-plugins
for s in "proceed silently — the glossary's own state is never a finding: never flag it, never propose creating one." \
         "The same term carrying its ordinary-English meaning inside a sentence names nothing and is not a candidate." \
         "\`CONTEXT.md\` at the repo root, or the per-context files a root \`CONTEXT-MAP.md\` names"; do
  git grep -c -F "$s" -- plugins/ | awk -F: '{s+=$2} END {print s+0}'
done
```

Expected: `4`, `4`, `4` — two passages × two mirror copies. Today they are `2`, `0`, `2`; a `2` after the change means the new passage paraphrases instead of repeating, and a `3` means one mirror copy is short. The first span carries a **U+2014 em dash**; the third's backticks are backslash-escaped because the whole pattern is double-quoted. **The third span deliberately stops short of its delimiters** — the pass parenthesizes it and the angle sets it off with an em dash, so a pattern including either delimiter would return 2 on a correct tree and prove nothing about the other passage.

- [x] **Step 9: Verify — exactly these two files are modified**

```bash
cd /Users/taylor/dev/claude-plugins
git status --porcelain
```

Expected: exactly `plugins/dev-flow/skills/adversarial-review/SKILL.md` and `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md` as modified — plus, possibly, this change's own `docs/superpowers/` design and plan artifacts if the surrounding dev-flow run has not committed them yet. No other content file. In particular the design doc must **not** be modified, and `CONTEXT.md` must not appear yet — it is Task 2's.

- [x] **Step 10: Commit — both copies together, in one commit**

```bash
cd /Users/taylor/dev/claude-plugins
git add plugins/dev-flow/skills/adversarial-review/SKILL.md plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
git commit -m "adversarial-review: glossary-conformance angle, terminology drift clause, and the two glossary repairs"
```

**Do not split this into two commits.** A commit that carries one side of the mirror pair is CI-red on its own.

---

### Task 2: `CONTEXT.md` — name the sixth angle in the **Angle** entry

**Files:**
- Modify: `CONTEXT.md` (pre-change line 30, the definition line under `**Angle**:` — one line, replaced in place)
- Test: none. Verification is `wc -l`, `git diff --numstat`, a residue grep, and a scoped design-conformance script.

**Interfaces:**
- Consumes: Task 1 committed — the angle this entry now enumerates must exist in the mirror pair first.
- Produces: `CONTEXT.md` still at **67 lines**, carrying design block 9 verbatim directly after the `**Angle**:` term line. Task 4's full conformance script asserts both.

**Read the design's `§3. CONTEXT.md — the glossary entry this change makes true` before starting.** The **Angle** entry enumerates its instances, unlike **Pass**, so it goes stale the moment a sixth ships — and `docs/agents/domain.md` has every skill read the glossary before exploring, so a stale enumeration sends an agent looking for a five-item list that no longer exists.

**Exactly one line changes, and everything else in the file is deliberate.** The **Seam** entry and its `_Avoid_: boundary` line stay byte-identical — the design's whole `§Does CONTEXT.md's _Avoid_: boundary entry survive a check that enforces it?` argues that this entry is correct and the *shipped text* was wrong. The **Resolver** entry's `_Avoid_: group agent, judge, arbiter` line stays byte-identical for the same reason, and Task 1's Step 7 expects it to still be there as the single surviving `group agent` hit. The **Pass** entry is not edited (it defines the shape, not the instances), the **Design rubric** entry still reads "nine-bullet" (still true), and **no new entry is added**. `CONTEXT.md` ships into no plugin and `check-sync.py` never reads it — this file has **no** mechanical mirror check behind it, which is why the residue grep and the conformance script in Steps 4 and 5 are the only things standing behind this edit.

- [ ] **Step 1: Confirm the starting state**

```bash
cd /Users/taylor/dev/claude-plugins
wc -l CONTEXT.md
git grep -n -F 'altitude, seam placement.' -- CONTEXT.md
git grep -n -F '**Angle**:' -- CONTEXT.md
```

Expected: `67`; **exactly one hit** at `CONTEXT.md:30` for the stale enumeration (its line ends `… efficiency, altitude, seam placement.`); and **exactly one hit** at `CONTEXT.md:29` for the anchor. Zero hits on the enumeration means the edit already landed; two hits on either means the file is not the one this plan was written against — either way, stop and report rather than improvising.

- [ ] **Step 2: Apply design block 9 — the **Angle** definition line**

The applier replaces the line **directly after** the `**Angle**:` term line — the same anchor relationship the design's conformance script asserts. For orientation only, the replacement begins `One lens in the diff-mode quality seed's list: reuse, simplification, …` — **do not type it; the script below copies it.**

```bash
cd /Users/taylor/dev/claude-plugins
python3 - <<'PY'
import sys
from pathlib import Path
DESIGN = "docs/superpowers/specs/2026-07-29-gh-20-diff-terminology-design.md"
FENCE = chr(96) * 3
blocks, cur, mode = [], None, None
for line in Path(DESIGN).read_text(encoding="utf-8").split("\n"):
    s = line.strip()
    if mode is None:
        if s.startswith(FENCE):
            mode, cur = s[3:], []
    elif s == FENCE:
        if mode == "":
            blocks.append(cur)
        mode, cur = None, None
    else:
        cur.append(line)
assert [len(b) for b in blocks] == [1, 1, 1, 2, 1, 1, 1, 1, 1, 1], "design code-block shape changed; stop and re-read the design"
PATH, NEW, ANCHOR = "CONTEXT.md", blocks[9], "**Angle**:"
p = Path(PATH)
L = p.read_text(encoding="utf-8").split("\n")
at = [i for i, x in enumerate(L) if x.startswith(ANCHOR)]
if len(at) != 1:
    print("ABORT: block 9, Angle entry in", PATH, "-- anchor found", len(at), "times, want 1")
    sys.exit(1)
i = at[0] + 1
if L[i:i + len(NEW)] == NEW:
    print("already applied: block 9, Angle entry in", PATH)
else:
    L[i:i + 1] = NEW
    p.write_text("\n".join(L), encoding="utf-8")
    print("replace: block 9, Angle entry at line %d in %s" % (i + 1, PATH))
PY
echo "exit=$?"
```

Expected: `replace: block 9, Angle entry at line 30 in CONTEXT.md`, then `exit=0`. An `ABORT` means the anchor is missing or duplicated — stop and report.

- [ ] **Step 3: Verify — still 67 lines, exactly one line changed**

```bash
cd /Users/taylor/dev/claude-plugins
wc -l CONTEXT.md
git diff --numstat -- CONTEXT.md
```

Expected: `67`, and `1	1	CONTEXT.md`. **This is a replacement, not an append** — a 68-line file means the block was inserted instead of replacing, and `2	1` or more means something besides the **Angle** definition was touched. Either way, `git checkout -- CONTEXT.md` and re-run Step 2.

- [ ] **Step 4: Verify — residue grep, the stale five-item enumeration is gone**

```bash
cd /Users/taylor/dev/claude-plugins
git grep -n -F -e 'altitude, seam placement.' -- plugins/ CONTEXT.md
echo "exit=$?"
git grep -c -F 'altitude, seam placement, glossary conformance.' -- CONTEXT.md
```

Expected: the first command prints **no output**, `exit=1` — this is the ninth pattern from the design's `§Verification` step 3, the one Task 1's scoped grep left out, and it has exactly 1 hit today. The second prints `CONTEXT.md:1`, confirming the six-item enumeration is present. Two separate greps on purpose: a hit-count assertion and an absence assertion cannot share a command.

- [ ] **Step 5: Verify — design conformance, this task's one block**

A task-scoped subset of the design's `§Verification` step 5. It re-reads block 9 from the design on disk and demands a byte-for-byte line match at the right anchor — the check that catches a word mangled inside a 120-character line, which every grep above would sail past. Copy this exactly.

```bash
cd /Users/taylor/dev/claude-plugins
python3 - <<'PY'
import sys
from pathlib import Path
DESIGN = "docs/superpowers/specs/2026-07-29-gh-20-diff-terminology-design.md"
FENCE = chr(96) * 3
blocks, cur, mode = [], None, None
for line in Path(DESIGN).read_text(encoding="utf-8").split("\n"):
    s = line.strip()
    if mode is None:
        if s.startswith(FENCE):
            mode, cur = s[3:], []
    elif s == FENCE:
        if mode == "":
            blocks.append(cur)
        mode, cur = None, None
    else:
        cur.append(line)
assert [len(b) for b in blocks] == [1, 1, 1, 2, 1, 1, 1, 1, 1, 1], "design code-block shape changed; stop and re-read the design"
PATH, want, ANCHOR = "CONTEXT.md", blocks[9], "**Angle**:"
L = Path(PATH).read_text(encoding="utf-8").split("\n")
if L and L[-1] == "":
    L.pop()
bad = []
if len(L) != 67:
    bad.append(("file length", "%d lines, want 67" % len(L)))
at = [i for i in range(len(L) - len(want) + 1) if L[i:i + len(want)] == want]
if len(at) != 1:
    bad.append(("CONTEXT.md Angle entry", "found %d times, want exactly 1" % len(at)))
elif not L[at[0] - 1].startswith(ANCHOR):
    bad.append(("CONTEXT.md Angle entry", "sits after %r, want %r" % (L[at[0] - 1][:40], ANCHOR)))
for name, why in bad:
    print("MISMATCH:", name, "in", PATH, "--", why)
print("design-conformance (task 2 subset):", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected: `design-conformance (task 2 subset): OK`, `exit=0`.

- [ ] **Step 6: Verify — nothing else moved, and `check-sync.py` is unaffected**

```bash
cd /Users/taylor/dev/claude-plugins
python3 scripts/check-sync.py
git status --porcelain
```

Expected: `check-sync: all checks passed` with `mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)` — unchanged by this task, since neither check reads `CONTEXT.md`; and `CONTEXT.md` as the only modified content file (plus this run's own uncommitted `docs/superpowers/` artifacts, if any).

- [ ] **Step 7: Commit**

```bash
cd /Users/taylor/dev/claude-plugins
git add CONTEXT.md
git commit -m "CONTEXT.md: name glossary conformance in the Angle entry"
```

---

### Task 3: Bump both plugin versions

**Files:**
- Modify: `plugins/dev-flow/.claude-plugin/plugin.json` (the `version` line)
- Modify: `plugins/dev-flow-worktree/.claude-plugin/plugin.json` (the `version` line)

**Interfaces:**
- Consumes: Tasks 1 and 2 committed — these bumps are what makes Task 1's edits reachable on re-sync.
- Produces: `dev-flow` at `2.6.0`, `dev-flow-worktree` at `1.8.0`; Task 4 Step 6 asserts both.

**This is not cosmetic cleanup.** The install cache is version-keyed (`~/.claude/plugins/cache/taylor-plugins/<plugin>/<version>/`), so Task 1's edits are never picked up on re-sync until this task lands. **Minor rather than major** per the design's `§4 & 5`: the invocation signature, the contract, the provenance format, the mode set and the model policy are all unchanged — only seed content changes. Same bump shape as gh-7 and gh-16.

- [ ] **Step 1: Bump `dev-flow` from `2.5.0` to `2.6.0`**

In `plugins/dev-flow/.claude-plugin/plugin.json`, replace the line:

```
  "version": "2.5.0",
```

with:

```
  "version": "2.6.0",
```

Change **only** the `version` field. Do **not** touch `description` — it is duplicated into `.claude-plugin/marketplace.json` and `check-sync.py` Check A compares them; that file is out of scope for this change.

- [ ] **Step 2: Bump `dev-flow-worktree` from `1.7.0` to `1.8.0`**

In `plugins/dev-flow-worktree/.claude-plugin/plugin.json`, replace the line:

```
  "version": "1.7.0",
```

with:

```
  "version": "1.8.0",
```

Same constraint: `version` only.

- [ ] **Step 3: Verify — both version strings read back correctly**

```bash
cd /Users/taylor/dev/claude-plugins
git grep -cF '"version": "2.6.0"' -- plugins/dev-flow/.claude-plugin/plugin.json
git grep -cF '"version": "1.8.0"' -- plugins/dev-flow-worktree/.claude-plugin/plugin.json
```

Expected: each command prints exactly one line — `plugins/dev-flow/.claude-plugin/plugin.json:1` and `plugins/dev-flow-worktree/.claude-plugin/plugin.json:1` — with `exit=0`. Each pattern is scoped to the single file it belongs in, so a swapped pair produces no output and `exit=1` from both rather than something an executor has to eyeball. `git grep` rather than a bare `grep`, per Global Constraints — a bare `grep` here returns `rtk grep --help`, not an answer.

- [ ] **Step 4: Verify — manifests still valid and in sync, exactly one line changed per file**

```bash
cd /Users/taylor/dev/claude-plugins
python3 scripts/check-sync.py
claude plugin validate .
git diff --numstat -- plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
```

Expected: `check-sync: all checks passed` (Check A is unaffected — it compares `name`, `source`, and `description`, and does not read `version`, which is why `.claude-plugin/marketplace.json` is not touched by this change); `claude plugin validate .` succeeds (**8 missing-author warnings are expected, NOT a failure**); `--numstat` showing exactly `1	1` for each manifest. More than one changed line means something besides `version` was touched — revert it.

- [ ] **Step 5: Commit**

```bash
cd /Users/taylor/dev/claude-plugins
git add plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
git commit -m "dev-flow 2.6.0, dev-flow-worktree 1.8.0"
```

---

### Task 4: End-to-end verification — the design's `§Verification` steps 1–8, plus a scope check

**Files:** none modified — **this task must produce an empty diff.** It only reads and reports.

**Interfaces:**
- Consumes: Tasks 1, 2 and 3 all complete and committed.
- Produces: nothing but a pass/fail report.

**You do not fix anything in this task.** You hold none of the replacement text — it lives in the design, and the appliers that move it live in Tasks 1 and 2 — so any "fix" applied here would be retyped from memory, which is exactly the failure Step 5 exists to catch. If any step fails: **stop, change no file, and report BLOCKED**, giving (a) the step number, (b) the command you ran, and (c) its complete output. The controller routes that to the task that owns the file — **Task 1** for the two `adversarial-review/SKILL.md` copies, **Task 2** for `CONTEXT.md`, **Task 3** for the two `plugin.json` files — as a finding in that task's fix loop, then re-dispatches this task fresh. A re-dispatched Task 4 begins again at Step 1 and runs **every** step, not only the one that failed: a fix for one can break another.

Run every step from the repo root. Steps 1–8 are the design's `§Verification` steps 1–8, unmodified; Step 9 is this plan's scope check. **Copy every command exactly as written.** Where the design states an assertion but supplies no command — steps 6 and 8 — this plan supplies the invocation and says so in place.

- [ ] **Step 1: Mirror and manifest sync**

```sh
python3 scripts/check-sync.py
```

Expected: `check-sync: all checks passed`, with the mirror pair reporting **`89 lines, 1 declared exception`**.

- [ ] **Step 2: Marketplace validation**

```sh
claude plugin validate .
```

Expected: success. **8 missing-author warnings are expected** and are not a failure.

- [ ] **Step 3: Residue grep — all nine patterns return no hits**

```sh
git grep -n -F -e 'seam-placement angle, inlined' \
               -e "then a fifth of this skill" \
               -e 'altitude, seam placement.' \
               -e 'and terminology-collision passes' \
               -e '**Terminology collision — the design' \
               -e 'put the fix at the shared boundary' \
               -e 'finds the right boundary' \
               -e 'Each group-agent:' \
               -e 'Group-agents never invoke' -- plugins/ CONTEXT.md
```

Expect **no output** (exit 1). Every one is text this change deletes: eight are the in-place replacements in the mirror pair (2 hits each today, one per copy), and `'altitude, seam placement.'` is `CONTEXT.md`'s stale five-item enumeration (1 hit today). A surviving hit on any mirror-pair string means one side was missed — the failure `check-sync.py` catches only if the *other* side changed. The pathspec is required: the design and this plan both quote all nine strings in prose, and `docs/superpowers/` must not be searched. The fifth pattern carries a **U+2014 em dash**.

- [ ] **Step 4: The two glossary repairs are complete**

```sh
git grep -n -i -e 'shared boundary' -e 'shared-boundary' -e 'right boundary' -- . ':!docs/superpowers/'
```

Expect **no hits**. Broader than step 3's exact strings on purpose: it also fails if a fixer reflowed one of the two rubric bullets while keeping the word. Every remaining `boundary` in shipped text — 27 occurrences — must be the stage-transition sense, which this search does not match.

```sh
git grep -n -i -e 'group.agent' -- . ':!docs/superpowers/'
```

Expect **exactly one hit**, `CONTEXT.md:15` — the `_Avoid_:` line, which the never-flag clause puts outside every finding. Today it returns 5. `-i` and the `.` wildcard are load-bearing. `group-resolution agent` does not match this pattern and is deliberately not repaired.

- [ ] **Step 5: Design conformance — all ten blocks landed verbatim, in the right place**

This is the complete, unmodified script from the design's `§Verification` step 5 — the check Tasks 1 and 2's subset scripts stood in for, and the one step Steps 1–4 structurally cannot provide. Step 3's residue grep is tied to the in-place replacements and says nothing about the insertion; `check-sync.py` compares the two mirror copies only to *each other*, so a word mangled identically in both passes it at the correct 89 lines — and it never reads `CONTEXT.md` at all. Copy this exactly; it is deliberately pure ASCII, so a mistyped copy fails loudly instead of passing. **The fence is unindented on purpose** — a `python3` heredoc indented under a list item is an `IndentationError`.

```sh
python3 - <<'PY'
import sys
from pathlib import Path
DESIGN = "docs/superpowers/specs/2026-07-29-gh-20-diff-terminology-design.md"
FENCE = chr(96) * 3
blocks, cur, mode = [], None, None
for line in Path(DESIGN).read_text(encoding="utf-8").split("\n"):
    s = line.strip()
    if mode is None:
        if s.startswith(FENCE):
            mode, cur = s[3:], []
    elif s == FENCE:
        if mode == "":
            blocks.append(cur)
        mode, cur = None, None
    else:
        cur.append(line)
assert [len(b) for b in blocks] == [1, 1, 1, 2, 1, 1, 1, 1, 1, 1], "design code-block shape changed; stop and re-read the design"
PAIR = ["plugins/dev-flow/skills/adversarial-review/SKILL.md",
        "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md"]
GLOSS = ["CONTEXT.md"]
WANT = {PAIR[0]: 89, PAIR[1]: 89, GLOSS[0]: 67}
SPEC = [("line 28, diff row",            blocks[0], None,                    PAIR),
        ("line 29, design row",          blocks[1], None,                    PAIR),
        ("line 34, angles header",       blocks[2], None,                    PAIR),
        ("glossary-conformance angle",   blocks[3], "**Seam placement:**",   PAIR),
        ("terminology pass",             blocks[4], None,                    PAIR),
        ("rubric bullet 3",              blocks[5], None,                    PAIR),
        ("rubric bullet 7",              blocks[6], None,                    PAIR),
        ("resolution step 3",            blocks[7], None,                    PAIR),
        ("no-recursion clause",          blocks[8], None,                    PAIR),
        ("CONTEXT.md Angle entry",       blocks[9], "**Angle**:",            GLOSS)]
bad, text = [], {}
for path, want in WANT.items():
    L = Path(path).read_text(encoding="utf-8").split("\n")
    if L and L[-1] == "":
        L.pop()
    text[path] = L
    if len(L) != want:
        bad.append(("file length", path, "%d lines, want %d" % (len(L), want)))
for name, want, anchor, paths in SPEC:
    for path in paths:
        L = text[path]
        at = [i for i in range(len(L) - len(want) + 1) if L[i:i + len(want)] == want]
        if len(at) != 1:
            bad.append((name, path, "found %d times, want exactly 1" % len(at)))
        elif anchor is not None and not L[at[0] - 1].startswith(anchor):
            bad.append((name, path, "sits after %r, want %r" % (L[at[0] - 1][:40], anchor)))
for name, path, why in bad:
    print("MISMATCH:", name, "in", path, "--", why)
print("design-conformance:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected: exactly `design-conformance: OK` and `exit=0`. A `MISMATCH` line names the block and the file whose text or position differs — report BLOCKED naming that block; the owning task re-runs its applier. The shape assertion fires if the design's plain-fenced blocks are ever added to, removed, reordered, or reflowed: that is deliberate, because the blocks are indexed positionally. Every other fenced block in the design carries an info string (`text`, `sh`) and is therefore skipped by the `mode == ""` filter.

- [ ] **Step 6: Version spot-check**

```sh
git grep -cF '"version": "2.6.0"' -- plugins/dev-flow/.claude-plugin/plugin.json
git grep -cF '"version": "1.8.0"' -- plugins/dev-flow-worktree/.claude-plugin/plugin.json
```

Expect each command to print exactly one line — `plugins/dev-flow/.claude-plugin/plugin.json:1` and `plugins/dev-flow-worktree/.claude-plugin/plugin.json:1` — with `exit=0`.

The design's `§Verification` step 6 states this as a bare assertion — *"Both `plugin.json` versions read `2.6.0` and `1.8.0`"* — and supplies no command, so the invocation above is this plan **supplying** one, not departing from one. Each pattern is scoped to the single file it belongs in, so a swapped pair fails with `exit=1` and no output instead of requiring the executor to read two lines correctly.

- [ ] **Step 7: The three duplicated spans are byte-identical, not paraphrased**

```sh
for s in "proceed silently — the glossary's own state is never a finding: never flag it, never propose creating one." \
         "The same term carrying its ordinary-English meaning inside a sentence names nothing and is not a candidate." \
         "\`CONTEXT.md\` at the repo root, or the per-context files a root \`CONTEXT-MAP.md\` names"; do
  git grep -c -F "$s" -- plugins/ | awk -F: '{s+=$2} END {print s+0}'
done
```

Expect `4`, `4`, `4` — two passages × two mirror copies. Today they are `2`, `0`, `2`. No mechanical check covers a duplication living twice inside one file; `check-sync.py` only ever compares the two mirror copies to each other. The pathspec is required, because the design quotes all three in prose, and the third span carries **no surrounding parenthesis or dash** on purpose — the pass parenthesizes it and the angle sets it off with an em dash, so a pattern including either delimiter returns 2 on a correct tree and proves nothing about the other passage.

- [ ] **Step 8: Behavioural check — the acceptance bar is tracked on #23, not run here**

The design's `§Verification` step 8 is a **post-installation** check, not a shell command: "the running review loads the *installed* skill, not the branch's copy, so this step is meaningful only after `claude plugin marketplace update taylor-plugins` and a restart — during this change's own pipeline run the reviews still execute the pre-change text." **Do not run the marketplace update and do not restart anything from this task.**

**It is in fact later than post-installation — it is post-merge — and this plan states the mechanics the design leaves implicit**, the same way it supplies step 6's missing invocation. As `taylor-plugins` is registered today, `~/.claude/plugins/known_marketplaces.json` records it as a **GitHub** source (`{"source": "github", "repo": "tayl0r/claude-plugins"}`) installed at `~/.claude/plugins/marketplaces/taylor-plugins`, which is a clone of `origin/main` and **not this checkout**. So `claude plugin marketplace update taylor-plugins` re-reads `main`: run before the PR merges, it reinstalls the *pre-change* text. Measured on this machine: the version-keyed cache `~/.claude/plugins/cache/taylor-plugins/dev-flow/` holds `1.0.0 … 2.5.0` and no `2.6.0`; `installed_plugins.json` pins `dev-flow@taylor-plugins` to `2.5.0` at `gitCommitSha 0a8a158`; and that cached `adversarial-review/SKILL.md` is 87 lines, byte-identical to this branch's pre-change copy. `dev-flow-worktree` is not installed at all, so only copy A is ever exercised here. The sequence that reaches the bar is therefore **merge → `claude plugin marketplace update taylor-plugins` → restart → run**, and **nothing this branch can do makes it runnable earlier** — which is why it is tracked rather than merely reported. Do two concrete things:

1. Confirm the shipped text carries the gates the bar depends on:

```sh
git grep -cF 'Report only what you can quote' -- plugins/
git grep -cF 'is never a finding' -- plugins/
```

Expect **two lines from each command** — one per `adversarial-review/SKILL.md` copy — and every line must read `:2`. Both counts are 2 because both clauses are restated in each of the two passages: the reportability rule and the never-flag clause each appear once in the glossary-conformance angle and once in the terminology pass. A `:1` means one passage lost its clause; a missing file line means a whole copy did. Two separate greps on purpose: `git grep -c` counts matching **lines**, not occurrences, so a single multi-pattern grep would report the same number whether both clauses were present or only one. (Step 5 already proved both passages match the design byte-for-byte; this makes the load-bearing clauses visible in the verification record.)

2. **State this bar verbatim in your task report, and name the issue that owns it — #23**, *"adversarial-review: run the gh-20/gh-22 behavioural acceptance bar after the next plugin install"*, which carries the bar, the post-merge mechanics above, and the outcomes to record when it is discharged. The bar: *in `diff` mode on this change's branch the correct outcome is **no finding** — a finding whose `file:line` falls under `docs/superpowers/` is evidence the scope clause is too weak to have shipped, and a finding on the repaired rubric bullets' `seam` is evidence the second clause is. In `design` mode on this change's design document the correct outcome is **no finding** — a finding on any of its 28 Seam-sense `boundary` occurrences means the mention-versus-use sentence is too weak, and one on a stage-transition occurrence means "only where it names the very concept its entry defines" is. In both modes, a report of "several identifiers overlap glossary terms" with no location is evidence the reportability rule is too weak to have shipped.*

**Why an issue rather than only a report line.** This bar is the only **outcome-level** check the change has: every other verification here — the design-conformance script, the residue greps, the span counts, `check-sync.py`, `claude plugin validate` — proves the target text matches what the design specified, and none proves the shipped check *behaves* correctly when it runs. A task report is consumed by the controller and gone, so a bar that lives only there is owned by nobody the moment this run ends; a GitHub issue is this repo's declared mechanism for work that cannot land inside the change that discovers it (`docs/agents/issue-tracker.md`; `adversarial-review`'s own Contract, which calls `gh issue create` part of a review rather than integration; dev-flow's Stage 5 final report, which enumerates every issue filed across all stages). #23 also names the cheap way to discharge most of it: the drift clause ships into the `design` **and** `plan` correctness seed and the angle into the Stage 4 `diff` quality seed, so the **next full dev-flow run in this repo** after the update and restart exercises both halves at zero marginal cost — the two runs named above are the harder, deliberately adversarial corpus, not the only opportunity.

There is nothing to fix here at implementation time, and nothing here is a gate: **do not** run the marketplace update, restart, merge, or launch a review to satisfy the bar. Part 1's two greps plus naming #23 is the whole of this step.

- [ ] **Step 9: Scope check — the final diff touches exactly five files and nothing else**

```bash
cd /Users/taylor/dev/claude-plugins
git status --porcelain
git diff --stat main...HEAD
```

Expected: `git status --porcelain` prints nothing — or `ok`, `rtk`'s empty-output marker, per Global Constraints — except, possibly, this change's own design and plan artifacts under `docs/superpowers/` if the surrounding dev-flow run has not committed them yet. `git diff --stat main...HEAD` must list exactly the five files from the File map, plus those two `docs/superpowers/` artifacts once committed — **no `.claude-plugin/marketplace.json`, no pipeline `SKILL.md`, no `README.md`, no `CLAUDE.md`, no `docs/agents/`, no `docs/adr/`, no `scripts/check-sync.py`, nothing under `plugins/` outside `dev-flow` and `dev-flow-worktree`.** The design document itself must **not** appear as modified. Anything else means scope leaked; report BLOCKED.

---

## Definition of done

- Both `adversarial-review/SKILL.md` copies are **89 lines** and carry design blocks 0–8 byte-identically, with the glossary-conformance angle sitting directly after the `**Seam placement:**` paragraph.
- `CONTEXT.md` is still **67 lines** and carries design block 9 directly after `**Angle**:`; its **Seam** and **Resolver** entries are byte-identical to `main`.
- `plugins/dev-flow` is at `2.6.0`; `plugins/dev-flow-worktree` is at `1.8.0`.
- `python3 scripts/check-sync.py` reports `mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)` and `all checks passed`; `claude plugin validate .` succeeds with the expected 8 warnings.
- The design's `§Verification` steps 1–8 all pass, including `design-conformance: OK`, the nine-pattern residue grep with no hits, the two repair greps (`shared/right boundary` empty, `group.agent` exactly `CONTEXT.md:15`), and the three span counts at `4`, `4`, `4` — plus the scope check.
- Step 8's behavioural acceptance bar is **recorded on #23, not discharged** — it is unrunnable until the PR merges and the marketplace is updated and restarted, and #23 is what owns it afterwards.
- Nothing has been pushed, no PR opened, no merge performed. When the surrounding dev-flow run does open the PR, its body closes **#20** and **#22** (design `§PR`).
