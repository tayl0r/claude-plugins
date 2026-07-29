---
dev-flow:
  slug: gh-16-terminology-collision
  spec: docs/superpowers/specs/2026-07-28-gh-16-terminology-collision-design.md
---

# gh-16: terminology collisions are invisible to stage reviews — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a trigger-gated **terminology-collision** pass to `adversarial-review`'s design/plan correctness seed, make the working-directory rule promise read-only reviewers the repo root that pass depends on, correct the one false clause in `dev-flow`'s pipeline `SKILL.md` that contradicts that promise, and bump both plugin versions so the change reaches a user.

**Architecture:** Pure prose-and-manifest change across five files, no code. Two of the files are a `check-sync.py`-enforced **mirror pair** (`adversarial-review/SKILL.md` × 2): two in-place line replacements plus one symmetric two-line insertion, landing byte-identically in both copies, taking both from 85 to **87 lines**. A third file, `plugins/dev-flow/skills/dev-flow/SKILL.md`, gets one in-place line replacement and stays at **277 lines** — this edit is deliberately **one-sided**, because `dev-flow-worktree`'s counterpart paragraph already states the correct thing and needs no change. Two `plugin.json` version bumps are load-bearing (the install cache is version-keyed) and follow once the behavior they gate is in place.

**Tech Stack:** Markdown, JSON manifests, `python3 scripts/check-sync.py`, `claude plugin validate .`, `git grep`, inline `python3 - <<'PY'` scripts. No build, no test framework, no linter.

**Authoritative source:** `docs/superpowers/specs/2026-07-28-gh-16-terminology-collision-design.md`. **Every character of every replacement lives in that file and is applied by reading it from disk — this plan deliberately does not restate any of it.** If this plan and the design ever disagree, the design wins — stop and re-read `§Exact change list`.

---

## Global Constraints

Every task's requirements implicitly include this section.

- **Repo root:** `/Users/taylor/dev/claude-plugins`. Every path below is relative to it. Work in place on the existing branch `tayl0r/gh-16-terminology-collision` — **do not create a git worktree, do not switch branches, do not push, do not open a PR, do not merge.**
- **NEVER RETYPE THE REPLACEMENT TEXT.** The design's `§Exact change list` gives its four replacement/insertion blocks as plain fenced code blocks. Every edit in this plan is applied by a supplied `python3` **applier script** that parses those blocks out of the design file on disk and writes them into the target. Do **not** transcribe the text by hand, do **not** paste it from a chat message, do **not** use `Edit` with a retyped `new_string`. The design's own verification (Task 4, Step 4) re-reads those same blocks and demands a byte-for-byte line match, so any hand-transcription that drifts by one character fails loudly — and one that drifts *identically in both mirror copies* passes `check-sync.py` at the correct 87 lines and is caught by nothing else.
- **Every line number in this plan and in the design is PRE-CHANGE and is not to be trusted.** The design says so in its `§Assumptions recorded`. Every applier locates its target by **content match on a distinctive anchor prefix** and asserts that anchor occurs **exactly once** in the file; the line number it prints is a cross-check, not an input. If an applier prints a line number different from the one this plan predicts, that is not a failure — note it in your report and keep going; the conformance script is the authority.
- **Every applier is idempotent.** Re-running one that has already landed prints `already applied: <block>, in <path>` — one line per block, since an applier may carry several — and changes nothing. A task re-dispatched after a partial run is safe to run from Step 1.
- **The mirror pair is edited byte-identically in both copies, always in the same step.** `plugins/dev-flow/skills/adversarial-review/SKILL.md` and `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md` are a declared `check-sync.py` mirror pair (line-for-line identical after substituting `dev-flow-worktree` → `dev-flow`, minus one declared exception at line 12, which is above every edit here and does not move). None of the new or edited text contains a `dev-flow` or `dev-flow-worktree` token, so the two copies compare equal in every touched region. A one-sided edit is CI-red.
- **There is no test framework, no build, no linter in this repo.** Do not run `pytest`, `npm test`, `ruff`, or invent one. Every verification step here is an exit code plus stdout from `python3 scripts/check-sync.py`, `claude plugin validate .`, `git grep`, `wc -l`, `git diff --numstat`, or an inline `python3` script given in full below.
- **`claude plugin validate .` emits 8 missing-author warnings. That is expected and is NOT a failure.** Only a non-zero exit or an explicit error is a failure.
- **Scope is exactly five files:** `plugins/dev-flow/skills/adversarial-review/SKILL.md`, `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md`, `plugins/dev-flow/skills/dev-flow/SKILL.md`, `plugins/dev-flow/.claude-plugin/plugin.json`, `plugins/dev-flow-worktree/.claude-plugin/plugin.json`. Nothing else may appear in the final diff. Do **not** touch `.claude-plugin/marketplace.json` (Check A does not read `version`), `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` (design `§5`: it already says the correct thing), `CONTEXT.md` (design `§Out of scope`: no entry is added), `CLAUDE.md` (design `§Blast radius`: the existing rule already covers this change), `scripts/check-sync.py`, `.github/workflows/`, `docs/agents/*.md`, either `README.md`, or any other plugin.
- **The design doc is read-only reference material.** `docs/superpowers/specs/2026-07-28-gh-16-terminology-collision-design.md` is never edited — every script here only *reads* it. Editing it would silently change what the conformance check compares against.
- **Every inline `python3` script below is pure ASCII on purpose**, including its anchor strings, so that a mistyped copy fails loudly instead of passing. The *content* it moves is full of em dashes and backticks — but you never type that content, the script copies it. **Copy each script exactly, character for character.** The heredoc fences are unindented on purpose: a `python3` heredoc indented under a list item is an `IndentationError`.
- **The shell hook (`rtk hook claude`, a `PreToolUse` Bash hook) rewrites bare `grep`, `wc`, `git diff`, and `git status` into `rtk` equivalents.** Two consequences bind every step below. (1) **Never use a bare `grep`.** `rtk grep` replaces the distinguishing segment of a path with `...` (`plugins/.../.claude-plugin/plugin.json`), reorders its output, and strips leading whitespace, so a per-file assertion cannot be read off it. Every text assertion in this plan is `git grep`, which the hook does not touch and which searches the working tree including unstaged edits. (2) **On a clean tree `git status --porcelain` prints `ok`, not nothing** — that is `rtk`'s empty-output marker and it is a pass, not a failure. `rtk wc -l` and `rtk git diff` preserve every number this plan asserts (`rtk wc -l` drops the `plugins/` prefix and appends a `Σ` total; `git diff --numstat` and `--stat` are passthrough) — run those as written and read the numbers, not the layout. `python3` and `claude plugin validate` are untouched.
- **`git diff --numstat` is asserted only where an edit replaces a *single* line** — the two `plugin.json` bumps and the pipeline `SKILL.md` line, where `1  1` is what a one-line replacement means by definition. **Never assert numstat counts for the mirror pair**, which takes two replacements plus an insertion in one file: `--numstat` reports git's minimal edit script over the final content, not "N lines in, M lines out". `wc -l` plus the design-conformance script are what verify those.
- **A presence assertion is one `git grep -cF` per pattern — never one multi-pattern `git grep` with a line-count expectation.** `git grep` prints a matching line *once* however many `-e` patterns hit it, and every design block's substantive content here is a single long line, so two patterns quoted from one block always land on the same physical line: a multi-pattern grep then reports that one line whether both patterns matched or only one, and the count reveals nothing. `git grep -cF '<pattern>' -- <paths>` prints `path:count` for each *matching* file and omits non-matching files, so "one line per target file, each reading `:1`" is an assertion that actually fails when a pattern is missing, and it names which file is short. Residue greps are the opposite case and stay multi-pattern: they expect **no** output, so any hit is a failure whichever pattern produced it.

---

## File map

| File | Responsibility in this change | Lines | Task |
|---|---|---|---|
| `plugins/dev-flow/skills/adversarial-review/SKILL.md` | Mirror-pair copy A. Design block **0** replaces the Working directory line (pre-change line 20); block **1** replaces the `design` seed row (pre-change line 29); block **2** inserts the terminology-collision pass after the input-contract pass (pre-change line 44). | 85 → **87** | 1 |
| `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md` | Mirror-pair copy B. The identical three edits, byte-for-byte. | 85 → **87** | 1 |
| `plugins/dev-flow/skills/dev-flow/SKILL.md` | Design block **3** replaces the Branch lifecycle paragraph (pre-change line 139), deleting the false "no absolute-path threading" clause. **One-sided by design** — the `dev-flow-worktree` counterpart is not edited. | 277 → **277** | 2 |
| `plugins/dev-flow/.claude-plugin/plugin.json` | `"version": "2.4.0"` → `"2.5.0"`. Load-bearing: the install cache is version-keyed. | unchanged | 3 |
| `plugins/dev-flow-worktree/.claude-plugin/plugin.json` | `"version": "1.6.0"` → `"1.7.0"`. Same. | unchanged | 3 |

No file is created, renamed, or deleted. The design's four fenced blocks map one-to-one onto the four content edits: blocks 0, 1, 2 → Task 1; block 3 → Task 2.

---

## Task ordering and why

**Task 1 is one task across two files, not two tasks**, because the two `adversarial-review/SKILL.md` copies are a `check-sync.py`-enforced mirror pair: a commit that edits one side and not the other is CI-red by construction. Its three edits are one task rather than three because they share a single deliverable — the pair at 87 lines, mirror-check green — and no reviewer can meaningfully approve the new pass while rejecting the seed-table cell that makes it reachable (design `§1 & 2`: "a second is added, so the cell must name both or the new one is unreachable by a prompt-builder that resolves the cell").

**Task 2 (the pipeline file) is separate from Task 1** — different file, no mechanical coupling, and a genuinely separable claim: it corrects a false sentence in the review's primary caller. The design's own reasoning ties them in *direction* but not in *commit*: "Shipping the line-20 clarification while leaving this sentence in the review's primary caller would put two files of one plugin in contradiction" (design `§5`). Same PR, and Task 1 first so the guarantee exists before the sentence claiming it is written.

**Task 3 (version bumps) follows Tasks 1 and 2.** Disjoint files, so this is sequencing rather than isolation: a bump that ships before the behavior claims a version that does not have it. `dev-flow` 2.5.0 covers both Task 1's copy A and Task 2's pipeline edit; `dev-flow-worktree` 1.7.0 covers Task 1's copy B.

**Task 4 runs the design's full `§Verification` steps 1–6 plus a scope check**, and depends on Tasks 1–3 all being complete and committed — the version grep, the full residue grep, and the complete conformance script (which asserts all three file lengths and all four blocks at once) are only meaningful once every file has landed.

---

### Task 1: The `adversarial-review` mirror pair — three edits, one commit

**Files:**
- Modify: `plugins/dev-flow/skills/adversarial-review/SKILL.md` (pre-change lines 20 and 29 replaced; two lines inserted after pre-change line 44)
- Modify: `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md` (the identical three edits)
- Test: none — this repo has no test framework. Verification is `check-sync.py`, `wc -l`, a scoped residue grep, and a scoped design-conformance script.

**Interfaces:**
- Consumes: nothing. This is the first task.
- Produces: both mirror copies at **87 lines**, carrying design blocks 0, 1 and 2 verbatim. Task 2's residue grep and Task 4's full conformance script assume this landed; Task 3's `dev-flow-worktree` bump is the version this task's copy B ships under.

**Read the design's `§1 & 2. plugins/dev-flow/skills/adversarial-review/SKILL.md and plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md` and `§Sync constraint` before starting.** You do not need to transcribe anything from them — the appliers below read the text themselves — but you do need to know why every edit lands twice.

- [ ] **Step 1: Confirm the starting state**

```bash
cd /Users/taylor/dev/claude-plugins
git rev-parse --abbrev-ref HEAD
python3 scripts/check-sync.py
wc -l plugins/dev-flow/skills/adversarial-review/SKILL.md plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md plugins/dev-flow/skills/dev-flow/SKILL.md
```

Expected: branch `tayl0r/gh-16-terminology-collision`; `check-sync: all checks passed` with `mirror pair "adversarial-review" ... OK (85 lines, 1 declared exception)`; and `85`, `85`, `277`. If any of that differs, **stop and report** — the tree is not the state this plan was written against, and the design's `§Assumptions recorded` pins these numbers to commit `4e32e0e`.

- [ ] **Step 2: Apply design blocks 0, 1 and 2 — all three edits, both copies, one script**

One applier carries all three edits, and each target file is written **once**, after all three of its anchors have resolved. **Block 0** replaces the read-only-reviewer sentence so seeds are promised the repo root (design `§Working directory`). For orientation only, it begins `**Working directory (resolve once, thread always).** Resolve the working directory exactly once…` — **do not type it; the script below copies it.**

**Block 1** makes the correctness cell name both below-table passes, so the new one is reachable by a prompt-builder that resolves the cell. Only the correctness (third) cell changes; the quality cell is byte-identical to today. **The `plan` row is not edited** — its "The prose checklist above" reference carries the addition, and the new pass names both modes in its own heading.

**Block 2** is **two lines**: one empty line, then the pass. It is inserted **directly after** the `**Input-contract completeness …` paragraph, keeping the two design/plan notes contiguous and last in the section. The anchor position is load-bearing and Task 4's conformance script asserts it: the same pass inserted after the `Pinned template` paragraph instead would leave a diff-mode note trailing the two design/plan notes and would pass every other check.

A missing or duplicated anchor prints `ABORT`, leaves that file **exactly as it was**, and still exits non-zero after the other file is processed: every edit is computed against an in-memory copy and the write happens only once all three anchors have resolved, so **no file is ever left carrying part of the change**. Three separate appliers, one per block, could not promise that — the second can fail after the first has already written.

```bash
cd /Users/taylor/dev/claude-plugins
python3 - <<'PY'
import sys
from pathlib import Path
DESIGN = "docs/superpowers/specs/2026-07-28-gh-16-terminology-collision-design.md"
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
assert [len(b) for b in blocks] == [1, 1, 2, 1], "design code-block shape changed; stop and re-read the design"
TARGETS = ["plugins/dev-flow/skills/adversarial-review/SKILL.md",
           "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md"]
EDITS = [("block 0, working directory", blocks[0], "**Working directory (resolve once, thread always).**", "replace"),
         ("block 1, design row",        blocks[1], "| **design** | The design rubric",                     "replace"),
         ("block 2, terminology pass",  blocks[2], "**Input-contract completeness",                        "insert")]
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

Expected: six lines, in this order —

```
replace: block 0, working directory at line 20 in plugins/dev-flow/skills/adversarial-review/SKILL.md
replace: block 1, design row at line 29 in plugins/dev-flow/skills/adversarial-review/SKILL.md
insert: block 2, terminology pass at line 45 in plugins/dev-flow/skills/adversarial-review/SKILL.md
replace: block 0, working directory at line 20 in plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
replace: block 1, design row at line 29 in plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
insert: block 2, terminology pass at line 45 in plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
```

— then `exit=0`. **The insertion line reads `45`, not 44:** it is the line the inserted block now occupies, not the anchor line it follows. An `ABORT` line means an anchor is missing or duplicated — stop and report; do not edit by hand.

- [ ] **Step 3: Verify — both copies are 87 lines and the mirror check passes**

```bash
cd /Users/taylor/dev/claude-plugins
wc -l plugins/dev-flow/skills/adversarial-review/SKILL.md plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
python3 scripts/check-sync.py
echo "exit=$?"
```

Expected: `87` for each file, and:

```
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... OK (87 lines, 1 declared exception)
check-sync: all checks passed
```

`exit=0`. **`87 lines, 1 declared exception` is load-bearing.** A `LINE_COUNT_FIX` failure means the insertion landed asymmetrically; an undeclared-divergence failure naming a line means a replacement landed on one side only — re-run the applier in Step 2, which fixes exactly the missing side and no-ops the other. `1 declared exception` still reading `1` confirms the line-12 exception did not go stale (it sits above every edit and does not move).

- [ ] **Step 4: Verify — scoped residue grep (the replaced text is gone; no stale draft was applied)**

```bash
cd /Users/taylor/dev/claude-plugins
git grep -n -e 'input-contract completeness pass (below)' \
           -e 'Read-only reviewers receive absolute artifact/diff paths' \
           -e 'never flag its absence or propose creating one' \
           -- plugins/dev-flow/skills/adversarial-review/SKILL.md plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
echo "exit=$?"
```

Expected: **no output**, `exit=1`. This is three of the four patterns in the design's `§Verification` step 3, scoped to this task's two files (the fourth belongs to Task 2's file). The first two are the exact phrases this task's replacements delete, and a hit on either means one side of the mirror pair was missed. **The third never existed in any shipped file** — it is the pre-review draft of the pass's final sentence, so a hit means a stale block was applied instead of the one in the design's `§Exact change list`; the applier above cannot produce that, but a hand-edit can, which is why it is checked here.

- [ ] **Step 5: Verify — design conformance, this task's three blocks**

This is the check that catches what line counts and greps cannot: text mangled *identically in both* mirror copies, or the pass inserted at the wrong anchor. It reads the expected text from the design file on disk, never retyped. This is a task-scoped subset of the design's `§Verification` step 4 — it omits the pipeline block and the pipeline file's length, which Task 2 owns. **Task 4 runs the complete, unmodified script.** Copy this exactly.

```bash
cd /Users/taylor/dev/claude-plugins
python3 - <<'PY'
import sys
from pathlib import Path
DESIGN = "docs/superpowers/specs/2026-07-28-gh-16-terminology-collision-design.md"
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
assert [len(b) for b in blocks] == [1, 1, 2, 1], "design code-block shape changed; stop and re-read the design"
PAIR = ["plugins/dev-flow/skills/adversarial-review/SKILL.md",
        "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md"]
WANT = {PAIR[0]: 87, PAIR[1]: 87}
SPEC = [("line 20, working directory", blocks[0], None, PAIR),
        ("line 29, design row",        blocks[1], None, PAIR),
        ("terminology-collision pass", blocks[2], "**Input-contract completeness", PAIR)]
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

Expected: `design-conformance (task 1 subset): OK`, `exit=0`. A `MISMATCH` line names the block and the file whose text or position differs — re-run the applier in Step 2 and re-run Steps 3–5. Never "fix" a mismatch by editing the target by hand.

- [ ] **Step 6: Verify — exactly these two files are modified**

```bash
cd /Users/taylor/dev/claude-plugins
git status --porcelain
```

Expected: exactly `plugins/dev-flow/skills/adversarial-review/SKILL.md` and `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md` as modified — plus, possibly, this change's own `docs/superpowers/` design and plan artifacts if the surrounding dev-flow run has not committed them yet. No other content file. In particular the design doc must **not** be modified.

- [ ] **Step 7: Commit — both copies together, in one commit**

```bash
cd /Users/taylor/dev/claude-plugins
git add plugins/dev-flow/skills/adversarial-review/SKILL.md plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
git commit -m "adversarial-review: add the terminology-collision pass to the design/plan correctness seed"
```

**Do not split this into two commits.** A commit that carries one side of the mirror pair is CI-red on its own.

---

### Task 2: Correct the pipeline `SKILL.md`'s false absolute-path-threading clause

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md` (pre-change line 139, the Branch lifecycle paragraph — one line, replaced in place)
- Test: none. Verification is `wc -l`, `git diff --numstat`, a residue grep, a presence grep, and a scoped design-conformance script.

**Interfaces:**
- Consumes: Task 1's landed guarantee — the replacement sentence points at `adversarial-review`'s Working directory section, which Task 1 made say the thing being cited.
- Produces: `plugins/dev-flow/skills/dev-flow/SKILL.md` still at **277 lines**, carrying design block 3 verbatim. Task 3's `dev-flow` bump to 2.5.0 is the version this ships under; Task 4's full conformance script asserts both.

**Read the design's `§5. plugins/dev-flow/skills/dev-flow/SKILL.md — a false clause about the guarantee this change establishes` before starting.** The line's old third clause — *"and no absolute-path threading is needed anywhere in this pipeline"* — is false as a universal: `adversarial-review` is invoked in-context by this pipeline and threads the absolute root into every leaf it spawns unconditionally. A pipeline does not get to waive a delegated skill's internal rule.

**This edit is deliberately ONE-SIDED, and that is correct.** `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` is **not** edited: its counterpart is a *Worktree lifecycle* paragraph that already states the opposite, correctly (leaves "are pinned to the repo root and cannot inherit cwd, so each is handed the absolute worktree path explicitly"). There is no sibling claim to fix. The pipeline `SKILL.md` pair is hand-mirrored, not machine-checked — `check-sync.py` never reads these two files — so **the residue grep in Step 4 is the only mechanical check standing behind this edit.** Do not skip it.

- [ ] **Step 1: Confirm the starting state**

```bash
cd /Users/taylor/dev/claude-plugins
wc -l plugins/dev-flow/skills/dev-flow/SKILL.md
git grep -n 'no absolute-path threading' -- plugins/
```

Expected: `277`, and **exactly one hit** — `plugins/dev-flow/skills/dev-flow/SKILL.md:139`. Two hits would mean the `dev-flow-worktree` sibling carries the same false clause and the design's one-sided ruling needs re-reading; zero means the edit already landed. Either way, stop and report rather than improvising.

- [ ] **Step 2: Apply design block 3 — the Branch lifecycle paragraph**

For orientation only, the block begins `**Branch lifecycle — owned by dev-flow, plain git.** The contract stakes everything on one invariant…` and ends by naming `dev-flow:adversarial-review`'s Working directory section — **do not type it; the script below copies it.**

```bash
cd /Users/taylor/dev/claude-plugins
python3 - <<'PY'
import sys
from pathlib import Path
DESIGN = "docs/superpowers/specs/2026-07-28-gh-16-terminology-collision-design.md"
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
assert [len(b) for b in blocks] == [1, 1, 2, 1], "design code-block shape changed; stop and re-read the design"
NEW = blocks[3]
ANCHOR = "**Branch lifecycle"
TARGETS = ["plugins/dev-flow/skills/dev-flow/SKILL.md"]
for path in TARGETS:
    p = Path(path)
    L = p.read_text(encoding="utf-8").split("\n")
    at = [i for i, x in enumerate(L) if x.startswith(ANCHOR)]
    if len(at) != 1:
        print("ABORT:", path, "anchor found", len(at), "times, want 1")
        sys.exit(1)
    i = at[0]
    if L[i:i + len(NEW)] == NEW:
        print("already applied:", path)
        continue
    L[i:i + 1] = NEW
    p.write_text("\n".join(L), encoding="utf-8")
    print("replaced line %d in %s" % (i + 1, path))
PY
echo "exit=$?"
```

Expected: `replaced line 139 in plugins/dev-flow/skills/dev-flow/SKILL.md`, `exit=0`. The `TARGETS` list holds one path on purpose — **do not add the `dev-flow-worktree` pipeline file to it.**

- [ ] **Step 3: Verify — file length unchanged, exactly one line changed**

```bash
cd /Users/taylor/dev/claude-plugins
wc -l plugins/dev-flow/skills/dev-flow/SKILL.md
git diff --numstat -- plugins/dev-flow/skills/dev-flow/SKILL.md
```

Expected: `277` (this is an in-place, one-line replacement, so the count must not move), and `--numstat` showing exactly `1	1`. `1	0` means the new paragraph was appended rather than replacing the old one — re-run Step 2 after `git checkout -- plugins/dev-flow/skills/dev-flow/SKILL.md`.

- [ ] **Step 4: Verify — residue grep (the false clause is gone) and presence grep (the correction landed)**

```bash
cd /Users/taylor/dev/claude-plugins
git grep -n 'no absolute-path threading' -- plugins/
echo "exit=$?"
git grep -cF 'own rule and is not waived here' -- plugins/dev-flow/skills/dev-flow/SKILL.md
git grep -cF 'threads the absolute repo root into every agent it spawns unconditionally' -- plugins/dev-flow/skills/dev-flow/SKILL.md
```

Expected: the first command produces **no output**, `exit=1` — this is the design's `§Verification` step 3 pattern that covers this file, and per `CLAUDE.md` it is the mandatory residue check for a hand-mirrored edit. Each of the two presence greps then produces **exactly one line**, `plugins/dev-flow/skills/dev-flow/SKILL.md:1`, `exit=0`. **One grep per clause, per Global Constraints:** both clauses live on the *same* physical line — design block 3 is a single line, and these are its middle and its end — so a single multi-pattern `git grep` would print that one line even if only one clause had landed, which is exactly what a truncated hand-edit produces. A presence grep of either shape cannot tell an append from a replacement, which is why the residue grep runs first and Step 3 asserts the line count.

- [ ] **Step 5: Verify — design conformance, this task's block**

```bash
cd /Users/taylor/dev/claude-plugins
python3 - <<'PY'
import sys
from pathlib import Path
DESIGN = "docs/superpowers/specs/2026-07-28-gh-16-terminology-collision-design.md"
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
assert [len(b) for b in blocks] == [1, 1, 2, 1], "design code-block shape changed; stop and re-read the design"
PIPE = "plugins/dev-flow/skills/dev-flow/SKILL.md"
want = blocks[3]
L = Path(PIPE).read_text(encoding="utf-8").split("\n")
if L and L[-1] == "":
    L.pop()
bad = []
if len(L) != 277:
    bad.append(("file length", "%d lines, want 277" % len(L)))
at = [i for i in range(len(L) - len(want) + 1) if L[i:i + len(want)] == want]
if len(at) != 1:
    bad.append(("pipeline line 139, branch lifecycle", "found %d times, want exactly 1" % len(at)))
for name, why in bad:
    print("MISMATCH:", name, "in", PIPE, "--", why)
print("design-conformance (task 2 subset):", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected: `design-conformance (task 2 subset): OK`, `exit=0`. This is what catches a mangled word inside a 600-character paragraph that both greps in Step 4 would sail past.

- [ ] **Step 6: Verify — the `dev-flow-worktree` pipeline file was NOT touched**

```bash
cd /Users/taylor/dev/claude-plugins
git status --porcelain
git diff --stat -- plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
```

Expected: `git status --porcelain` shows `plugins/dev-flow/skills/dev-flow/SKILL.md` as the only modified content file (plus this change's own uncommitted `docs/superpowers/` artifacts, if any); the second command prints **nothing**. Any output from the second command means the one-sided edit was mirrored by mistake — revert that file.

- [ ] **Step 7: Commit**

```bash
cd /Users/taylor/dev/claude-plugins
git add plugins/dev-flow/skills/dev-flow/SKILL.md
git commit -m "dev-flow: drop the false no-absolute-path-threading clause from the branch lifecycle"
```

---

### Task 3: Bump both plugin versions

**Files:**
- Modify: `plugins/dev-flow/.claude-plugin/plugin.json` (the `version` line)
- Modify: `plugins/dev-flow-worktree/.claude-plugin/plugin.json` (the `version` line)

**Interfaces:**
- Consumes: Tasks 1 and 2 committed — these bumps are what makes their edits reachable.
- Produces: `dev-flow` at `2.5.0`, `dev-flow-worktree` at `1.7.0`; Task 4 Step 5 asserts both.

**This is not cosmetic cleanup.** The install cache is version-keyed (`~/.claude/plugins/cache/taylor-plugins/<plugin>/<version>/`), so Tasks 1–2's edits are never picked up on re-sync until this task lands. **Minor rather than major** per the design's `§3 & 4`: the skill's invocation signature, contract, provenance format, and mode set are unchanged; only seed content and one clause each of the working-directory rule and the branch lifecycle change.

- [ ] **Step 1: Bump `dev-flow` from `2.4.0` to `2.5.0`**

In `plugins/dev-flow/.claude-plugin/plugin.json`, replace the line:

```
  "version": "2.4.0",
```

with:

```
  "version": "2.5.0",
```

Change **only** the `version` field. Do **not** touch `description` — it is duplicated into `.claude-plugin/marketplace.json` and `check-sync.py` Check A compares them; that file is out of scope for this change.

- [ ] **Step 2: Bump `dev-flow-worktree` from `1.6.0` to `1.7.0`**

In `plugins/dev-flow-worktree/.claude-plugin/plugin.json`, replace the line:

```
  "version": "1.6.0",
```

with:

```
  "version": "1.7.0",
```

Same constraint: `version` only.

- [ ] **Step 3: Verify — both version strings read back correctly**

```bash
cd /Users/taylor/dev/claude-plugins
git grep -cF '"version": "2.5.0"' -- plugins/dev-flow/.claude-plugin/plugin.json
git grep -cF '"version": "1.7.0"' -- plugins/dev-flow-worktree/.claude-plugin/plugin.json
```

Expected: each command prints exactly one line — `plugins/dev-flow/.claude-plugin/plugin.json:1` and `plugins/dev-flow-worktree/.claude-plugin/plugin.json:1` — with `exit=0`. Each pattern is scoped to the single file it belongs in, so a swapped pair produces no output and `exit=1` from both rather than something an executor has to eyeball. `git grep` is used rather than a bare `grep` per Global Constraints.

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
git commit -m "dev-flow 2.5.0, dev-flow-worktree 1.7.0"
```

---

### Task 4: End-to-end verification — the design's `§Verification` steps 1–6, plus a scope check

**Files:** none modified — **this task must produce an empty diff.** It only reads and reports.

**Interfaces:**
- Consumes: Tasks 1, 2 and 3 all complete and committed.
- Produces: nothing but a pass/fail report.

**You do not fix anything in this task.** You hold none of the replacement text — it lives in the design, and the appliers that move it live in Tasks 1 and 2 — so any "fix" applied here would be retyped from memory, which is exactly the failure Step 4 exists to catch. If any step fails: **stop, change no file, and report BLOCKED**, giving (a) the step number, (b) the command you ran, and (c) its complete output. The controller routes that to the task that owns the file — **Task 1** for the two `adversarial-review/SKILL.md` copies, **Task 2** for `plugins/dev-flow/skills/dev-flow/SKILL.md`, **Task 3** for the two `plugin.json` files — as a finding in that task's fix loop, then re-dispatches this task fresh. A re-dispatched Task 4 begins again at Step 1 and runs **every** step, not only the one that failed: a fix for one can break another.

Run every step from the repo root. Steps 1–5 are the design's `§Verification` steps 1–5; Step 6 carries the design's step 6, which is a judgment bar rather than a command, plus two greps this plan adds to give it a mechanical spine; Step 7 is this plan's scope check. **Copy every command exactly as written.** Where the design states an assertion but supplies no command — steps 5 and 6 — this plan supplies the invocation and says so in place.

- [ ] **Step 1: Mirror and manifest sync**

```sh
python3 scripts/check-sync.py
```

Expected: `check-sync: all checks passed`, with the mirror pair reporting **`87 lines, 1 declared exception`**.

- [ ] **Step 2: Marketplace validation**

```sh
claude plugin validate .
```

Expected: success. **8 missing-author warnings are expected** and are not a failure.

- [ ] **Step 3: Residue grep — all four patterns return no hits**

```sh
git grep -n -e 'input-contract completeness pass (below)' \
           -e 'Read-only reviewers receive absolute artifact/diff paths' \
           -e 'no absolute-path threading' \
           -e 'never flag its absence or propose creating one' -- plugins/
```

Expect **no output** (exit 1). The first three are exact phrases this change deletes — the two in-place replacements in the mirror pair, and Task 2's one-sided edit to the hand-mirrored pipeline file, which is the one with no mechanical check behind it. A hit on the first two means one side of the mirror pair was missed. The fourth never existed in any shipped file: it is the pre-review draft of the pass's final sentence, and a hit means a stale block was applied instead of the one in the design's `§Exact change list`.

- [ ] **Step 4: Design conformance — all four blocks landed verbatim, in the right place**

This is the complete, unmodified script from the design's `§Verification` step 4 — the check Tasks 1 and 2's subset scripts stood in for, and the one step Steps 1–3 structurally cannot provide. Step 3's residue grep is tied to the in-place replacements and says nothing about the insertion; `check-sync.py` compares the two mirror copies only to *each other*, so a word mangled identically in both passes it at the correct 87 lines — and it never reads the pipeline file at all. Copy this exactly; it is deliberately pure ASCII, so a mistyped copy fails loudly instead of passing. **The fence is unindented on purpose** — a `python3` heredoc indented under a list item is an `IndentationError`.

```sh
python3 - <<'PY'
import sys
from pathlib import Path
DESIGN = "docs/superpowers/specs/2026-07-28-gh-16-terminology-collision-design.md"
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
assert [len(b) for b in blocks] == [1, 1, 2, 1], "design code-block shape changed; stop and re-read the design"
PAIR = ["plugins/dev-flow/skills/adversarial-review/SKILL.md",
        "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md"]
PIPE = ["plugins/dev-flow/skills/dev-flow/SKILL.md"]
WANT = {PAIR[0]: 87, PAIR[1]: 87, PIPE[0]: 277}
SPEC = [("line 20, working directory",          blocks[0], None, PAIR),
        ("line 29, design row",                 blocks[1], None, PAIR),
        ("terminology-collision pass",          blocks[2], "**Input-contract completeness", PAIR),
        ("pipeline line 139, branch lifecycle", blocks[3], None, PIPE)]
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

Expected: exactly `design-conformance: OK` and `exit=0`. A `MISMATCH` line names the block and the file whose text or position differs — report BLOCKED naming that block; the owning task re-runs its applier. The shape assertion (`[1, 1, 2, 1]`) fires if the design's plain-fenced blocks are ever added to, removed, or reflowed: that is deliberate, because the blocks are indexed positionally. The script's own fence carries the `sh` info string and is therefore skipped by the `mode == ""` filter, so adding or editing a verification step never disturbs that index.

- [ ] **Step 5: Version spot-check**

```sh
git grep -cF '"version": "2.5.0"' -- plugins/dev-flow/.claude-plugin/plugin.json
git grep -cF '"version": "1.7.0"' -- plugins/dev-flow-worktree/.claude-plugin/plugin.json
```

Expect each command to print exactly one line — `plugins/dev-flow/.claude-plugin/plugin.json:1` and `plugins/dev-flow-worktree/.claude-plugin/plugin.json:1` — with `exit=0`.

The design's `§Verification` step 5 states this as a bare assertion — *"Both `plugin.json` versions read `2.5.0` and `1.7.0`"* — and supplies no command, so the invocation above is this plan **supplying** one, not departing from one. Each pattern is scoped to the single file it belongs in, so a swapped pair fails with `exit=1` and no output instead of requiring the executor to read two lines correctly. `git grep` rather than a bare `grep`, per Global Constraints.

- [ ] **Step 6: Behavioural check — record the acceptance bar for the pass's first real run**

The design's `§Verification` step 6 is a **judgment bar, not a shell command**: the pass is meant to fire on documents like the design itself, and during that design's own review it did — twice, on `family` and `pass` (design `§Applying the pass to itself`). Nothing at implementation time can execute a future review, so this step has two parts, both concrete:

1. Confirm the shipped pass carries the two gates the bar depends on — its reportability rule and its glossary-state clause:

```sh
git grep -cF 'Report only what you can quote' -- plugins/
git grep -cF 'own state is never a finding' -- plugins/
```

Expect **two lines from each command** — one per `adversarial-review/SKILL.md` copy, each reporting `1`. Two separate greps on purpose: both clauses live on the *same* physical line (the pass is one line), and `git grep -c` counts matching **lines**, not occurrences, so a single multi-pattern grep would report `1` even if one clause were missing. Neither pattern contains an apostrophe, so single-quoting is safe. (Step 4 already proved the whole pass matches the design byte-for-byte; this makes the two load-bearing clauses visible in the verification record.)

2. **State this bar verbatim in your task report**, so the surrounding dev-flow run's own design/plan reviews are judged against it: *a reported collision must quote the artifact's sense, the colliding sense, and where the colliding one lives; a run that reports "consider defining your terms" is evidence the reportability rule is too weak to have shipped.*

There is nothing to fix here at implementation time. Do not treat part 2 as a blocker.

- [ ] **Step 7: Scope check — the final diff touches exactly five files and nothing else**

```bash
cd /Users/taylor/dev/claude-plugins
git status --porcelain
git diff --stat main...HEAD
```

Expected: `git status --porcelain` prints nothing — or `ok`, `rtk`'s empty-output marker, per Global Constraints — except, possibly, this change's own design and plan artifacts under `docs/superpowers/` if the surrounding dev-flow run has not committed them yet. `git diff --stat main...HEAD` must list exactly the five files from the File map, plus those two `docs/superpowers/` artifacts once committed — **no `.claude-plugin/marketplace.json`, no `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`, no `CONTEXT.md`, no `CLAUDE.md`, no `scripts/check-sync.py`, no `README.md`, nothing under `plugins/` outside `dev-flow` and `dev-flow-worktree`.** Anything else means scope leaked; report BLOCKED.

---

## Definition of done

- Both `adversarial-review/SKILL.md` copies are **87 lines** and carry design blocks 0, 1 and 2 byte-identically, with the terminology-collision pass sitting directly after the input-contract completeness pass.
- `plugins/dev-flow/skills/dev-flow/SKILL.md` is still **277 lines** and carries design block 3; `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` is untouched.
- `plugins/dev-flow` is at `2.5.0`; `plugins/dev-flow-worktree` is at `1.7.0`.
- `python3 scripts/check-sync.py` reports `mirror pair "adversarial-review" ... OK (87 lines, 1 declared exception)` and `all checks passed`; `claude plugin validate .` succeeds with the expected 8 warnings.
- The design's `§Verification` steps 1–6 all pass, including `design-conformance: OK`, plus the scope check.
- Nothing has been pushed, no PR opened, no merge performed.
