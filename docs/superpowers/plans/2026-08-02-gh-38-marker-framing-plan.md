---
dev-flow:
  slug: gh-38-marker-framing
  spec: docs/superpowers/specs/2026-08-02-gh-38-marker-framing-design.md
---

# gh-38 Marker Framing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. **The implementation is Tasks 1–3, and every checkbox in this plan is inside them; § *Run 7b* is a pipeline step addressed to the orchestrator and deliberately carries none** — see the Global Constraint *No checkbox outside Tasks 1–3*.

**Goal:** Pin how the `review clean` marker is framed on the write side and extracted on the read side, by replacing one line in each pipeline `SKILL.md`'s **Review state** paragraph and bumping both plugin versions.

**Architecture:** Four line-level edits and nothing else. Two `SKILL.md` files hold hand-mirrored copies of one `**Review state.**` paragraph; each gets its single line replaced with the corresponding fenced block copied off the design document on disk. Two `plugin.json` files get their `version` bumped so the version-keyed install cache picks the text up. There is no code and no test framework — the design's *Success criteria* are the entire verification surface, and most of this plan is running them.

**Tech Stack:** Markdown, JSON, `python3` (stdlib only), `git`, `gh`-free. Helper already in the repo: `scripts/design_blocks.py` (`read_blocks`). Repo checks: `scripts/check-sync.py`, `claude plugin validate .`.

## Global Constraints

Every task's requirements implicitly include this section.

- **Working directory (absolute), referred to below as `ROOT`:** `/Users/taylor/dev/claude-plugins/.claude/worktrees/agent-a6f97b9ce555b8410`. Branch: `tayl0r/gh-38-marker-framing`. Work in place; do **not** create a worktree. **Every shell block introduced by "Run from `ROOT`" needs that directory as the shell's working directory** — those commands use repo-relative paths. If your shell does not carry a `cd` from one call to the next (subagent threads generally do not), prefix each such block with `cd /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-a6f97b9ce555b8410 && `. The Python programs hardcode `ROOT` and are cwd-independent.
- **Design document (`DESIGN`), the authority for every replacement byte:** `ROOT/docs/superpowers/specs/2026-08-02-gh-38-marker-framing-design.md`
- **Authorized file set — nothing else may change.** Exactly: `plugins/dev-flow/skills/dev-flow/SKILL.md`, `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`, `plugins/dev-flow/.claude-plugin/plugin.json`, `plugins/dev-flow-worktree/.claude-plugin/plugin.json`, and paths under `docs/superpowers/` (this plan and its design). **Forbidden:** `CONTEXT.md`, `CLAUDE.md`, anything under `scripts/`. Concurrent agents own those; touching one is a **blocker to report, not a fix to apply** (design, *Out of scope* and criterion 8).
- **Never retype the replacement text.** The two replacement lines exist only in the design's *The edit* section as plain (untagged) fenced blocks. Every step that needs those bytes obtains them by calling `read_blocks(DESIGN, [1, 1])`. This plan deliberately does not quote them.
- **Match on line TEXT, not line number.** Both target lines currently begin `**Review state.** After Stage 4's review has committed its fixes`. Line 167 (`dev-flow`) and line 161 (`dev-flow-worktree`) are the expected positions, but the anchor text is what identifies the line. If a target line's current text does not start with that anchor, **halt and report** — do not search for a better line.
- **Line counts are preserved.** `plugins/dev-flow/skills/dev-flow/SKILL.md` stays **277** lines; `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` stays **271** lines. The edit replaces one line and adds none.
- **Version floors:** `plugins/dev-flow/.claude-plugin/plugin.json` `2.8.0` → **`2.9.0`**; `plugins/dev-flow-worktree/.claude-plugin/plugin.json` `1.10.0` → **`1.11.0`**. These are floors, not equalities (design, criterion 7).
- **`scripts/check-sync.py` does NOT cover this pair.** Its `MIRROR_PAIRS` holds only `adversarial-review`. This pipeline `SKILL.md` pair is the **hand-mirrored** kind: **a one-sided edit here is caught by nothing except this plan's criteria 4 and 5.** Per `CLAUDE.md`, the change must be verified against something *outside* the pair — that is what criterion 3 (removed-phrase grep) and criterion 4 (design-block conformance) are.
- **Criteria 4–7 are ONE Python program**, run top-to-bottom in a single interpreter. Do not re-split it, do not run a criterion on its own, and do not re-derive `BASE` per criterion. It is reproduced whole in Task 3.
- **No test framework exists in this repo.** Do not add one. Do not write tests.
- **Do not open a PR, merge, or push beyond the branch** from this plan. Stage transitions belong to the pipeline.
- **No checkbox outside Tasks 1–3 — a `dev-flow` mechanical constraint, not a style preference.** In `plugins/dev-flow/skills/dev-flow/SKILL.md`: `:165` reads "Execution is complete if and only if zero `- [ ]` remain in the plan at branch tip"; `:228` makes Stage 3's exit condition "last task complete"; and `:191`'s resume-table row — the one routing a plan with any unchecked box to **Execute** — is evaluated **above** `:193`/`:194`'s marker rows, first match wins. A box whose step cannot run until Stage 4 or 5 is therefore wrong in **both** settings. Left unticked, it makes Stage 3's exit condition unsatisfiable on the first pass, and on this run's certain `pre-merge` resume (front-matter `stops: [pre-merge]`) `:191` routes back into Execute with the PR, review, marker, and CI all ready. Ticked where its step actually runs, the tick is a commit (`:165`) landing **after** `:239` posted the marker; under this run's `docs: commit` policy Marker validity's strip clause is unsatisfiable (`:169`), so the branch halts with an **invalid** marker and `:193` routes the resume to a full re-review of an already-clean PR. **Anything this plan needs done after Task 3 goes in a prose section addressed to the orchestrator, never in a box.** (Task 1 preserves both line counts, so every `SKILL.md` line number cited here stays valid after the edit.)

---

## File Structure

| File | Change | Owner task |
|---|---|---|
| `plugins/dev-flow/skills/dev-flow/SKILL.md` | line 167 replaced (design block 0) | Task 1 |
| `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` | line 161 replaced (design block 1) | Task 1 |
| `plugins/dev-flow/.claude-plugin/plugin.json` | `"version"` `2.8.0` → `2.9.0` | Task 2 |
| `plugins/dev-flow-worktree/.claude-plugin/plugin.json` | `"version"` `1.10.0` → `1.11.0` | Task 2 |
| *(scratch only, never committed)* | verification scripts under the session scratchpad | Tasks 1 and 3, and § *Run 7b* |

Both `SKILL.md` edits must land in the **same** task and the **same** commit: the substitution-image proof (criterion 5) compares the two edited lines against each other, so a one-sided edit is not merely incomplete, it is unverifiable. The version bumps (Task 2) must be in the working tree before the criteria program (Task 3) can reach criterion 7.

**Dependency order:** Task 1 → Task 2 → Task 3. Those three are the whole implementation, and Stage 3 (Execute) exits when Task 3's last box is ticked — at which point zero checkboxes remain and `SKILL.md:228`'s exit condition is satisfied without qualification.

Run **7b** is deliberately **not a fourth task.** It is a pipeline step, specified in full in § *Run 7b — an orchestrator step at the `pre-merge` halt* below, and handed to the orchestrator by Task 3 Step 9. The design places it at a pipeline moment, not an implementation moment ("immediately before the pipeline **halts** at `pre-merge`", criterion 7), and the Global Constraint *No checkbox outside Tasks 1–3* gives the mechanical reason a fourth task could not express it.

---

## Task 1: Replace the `**Review state.**` line in both pipeline `SKILL.md` files

**Files:**
- Modify: `/Users/taylor/dev/claude-plugins/.claude/worktrees/agent-a6f97b9ce555b8410/plugins/dev-flow/skills/dev-flow/SKILL.md:167`
- Modify: `/Users/taylor/dev/claude-plugins/.claude/worktrees/agent-a6f97b9ce555b8410/plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md:161`
- Read only: `/Users/taylor/dev/claude-plugins/.claude/worktrees/agent-a6f97b9ce555b8410/docs/superpowers/specs/2026-08-02-gh-38-marker-framing-design.md`, `/Users/taylor/dev/claude-plugins/.claude/worktrees/agent-a6f97b9ce555b8410/scripts/design_blocks.py`
- Test: none — this repo has no test framework. The verification is the design's criteria, run in Task 3.

**Interfaces:**
- Consumes: `read_blocks(design_path, shape)` from `scripts/design_blocks.py`. Signature: takes an absolute-or-relative design path and a required shape list; returns the design's plain (untagged) fenced blocks in document order as lists of lines; raises `SystemExit` (non-zero) if the shape moved.
- Produces: both target files at their final text. Task 3's criteria 4, 5, and 6 read those two lines.

- [ ] **Step 1: Confirm the pre-edit state — the anchor is where it should be and the edit has not been applied**

Write this to `/private/tmp/claude-501/-Users-taylor-dev-claude-plugins/bab62c20-63f5-4951-b1c6-d34b0e5ae74e/scratchpad/precheck.py` and run it. It is the "failing test": on a fresh branch every `NOT-YET` line below must print, proving the edit is genuinely absent before it is applied. This is the only step that can tell "I made this change" from "it was already here" — every criterion in Task 3 passes identically on a pre-existing edit.

```python
import sys

ROOT = "/Users/taylor/dev/claude-plugins/.claude/worktrees/agent-a6f97b9ce555b8410"
sys.path.insert(0, f"{ROOT}/scripts")
from design_blocks import read_blocks

DESIGN = f"{ROOT}/docs/superpowers/specs/2026-08-02-gh-38-marker-framing-design.md"
ANCHOR = "**Review state.** After Stage 4's review has committed its fixes"
TARGETS = [
    (f"{ROOT}/plugins/dev-flow/skills/dev-flow/SKILL.md", 167, 277),
    (f"{ROOT}/plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md", 161, 271),
]

blocks = read_blocks(DESIGN, [1, 1])
for (path, lineno, total), block in zip(TARGETS, blocks):
    assert len(block) == 1, (path, "design block is not a single line", len(block))
    lines = open(path, encoding="utf-8").read().split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    assert len(lines) == total, (path, "unexpected line count", len(lines), total)
    hits = [i + 1 for i, l in enumerate(lines) if l.startswith(ANCHOR)]
    assert hits == [lineno], (path, "anchor text not uniquely at the expected line", hits)
    applied = lines[lineno - 1] == block[0]
    print(f"{'ALREADY' if applied else 'NOT-YET'} {path}:{lineno} anchor unique, "
          f"replacement {'present' if applied else 'absent'}")
print("precheck ok")
```

Run: `python3 /private/tmp/claude-501/-Users-taylor-dev-claude-plugins/bab62c20-63f5-4951-b1c6-d34b0e5ae74e/scratchpad/precheck.py`

Expected on a fresh branch, exit 0:

```text
NOT-YET /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-a6f97b9ce555b8410/plugins/dev-flow/skills/dev-flow/SKILL.md:167 anchor unique, replacement absent
NOT-YET /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-a6f97b9ce555b8410/plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md:161 anchor unique, replacement absent
precheck ok
```

Any `AssertionError`, or a `design code-block shape is ...` `SystemExit` from `read_blocks`, is a **blocker: stop and report the exact message.** Do not "fix" the design, do not relocate the anchor, do not adjust the shape.

An `ALREADY` line in place of `NOT-YET` is **not** a failure — that file already carries the replacement, which is what a resumed run looks like. Continue to Step 2 either way: the replacement line still begins with `ANCHOR`, so Step 2's anchor check passes and it rewrites the same bytes, and running it is what makes a half-applied pair whole. Report a mixed result (one `ALREADY`, one `NOT-YET`) explicitly — it means a prior run stopped mid-task, and it is the one-sided state criterion 5 exists to catch.

- [ ] **Step 2: Apply both replacements**

Write this to `/private/tmp/claude-501/-Users-taylor-dev-claude-plugins/bab62c20-63f5-4951-b1c6-d34b0e5ae74e/scratchpad/apply.py` and run it. It re-reads the blocks from the design on disk — the replacement bytes are never retyped — and re-checks the anchor before writing. It touches only the two `SKILL.md` files.

```python
import sys

ROOT = "/Users/taylor/dev/claude-plugins/.claude/worktrees/agent-a6f97b9ce555b8410"
sys.path.insert(0, f"{ROOT}/scripts")
from design_blocks import read_blocks

DESIGN = f"{ROOT}/docs/superpowers/specs/2026-08-02-gh-38-marker-framing-design.md"
ANCHOR = "**Review state.** After Stage 4's review has committed its fixes"
TARGETS = [
    (f"{ROOT}/plugins/dev-flow/skills/dev-flow/SKILL.md", 167, 277),
    (f"{ROOT}/plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md", 161, 271),
]

blocks = read_blocks(DESIGN, [1, 1])
for (path, lineno, total), block in zip(TARGETS, blocks):
    assert len(block) == 1, (path, "design block is not a single line", len(block))
    lines = open(path, encoding="utf-8").read().split("\n")
    trailing_newline = bool(lines) and lines[-1] == ""
    if trailing_newline:
        lines.pop()
    assert len(lines) == total, (path, "unexpected line count", len(lines), total)
    hits = [i + 1 for i, l in enumerate(lines) if l.startswith(ANCHOR)]
    assert hits == [lineno], (path, "anchor text not uniquely at the expected line", hits)
    lines[lineno - 1] = block[0]
    assert len(lines) == total, (path, "line count changed", len(lines), total)
    out = "\n".join(lines) + ("\n" if trailing_newline else "")
    open(path, "w", encoding="utf-8").write(out)
    print(f"replaced {path}:{lineno}")
print("apply ok")
```

Run: `python3 /private/tmp/claude-501/-Users-taylor-dev-claude-plugins/bab62c20-63f5-4951-b1c6-d34b0e5ae74e/scratchpad/apply.py`

Expected, exit 0:

```text
replaced /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-a6f97b9ce555b8410/plugins/dev-flow/skills/dev-flow/SKILL.md:167
replaced /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-a6f97b9ce555b8410/plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md:161
apply ok
```

- [ ] **Step 3: Verify the line counts are unchanged**

Run from `ROOT`:

```bash
wc -l plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
```

Expected: `277` and `271` respectively. Anything else is a blocker.

- [ ] **Step 4: Criterion 3 — the removed phrase is gone from `plugins/`**

This is one of the two checks *outside* the hand-mirrored pair, and it is the one `CLAUDE.md` requires unconditionally. Run from `ROOT`:

```bash
git grep -n 'with the marker line' -- plugins/ ; echo "exit=$?"
```

Expected: **no output**, `exit=1`. (Before the edit this printed both target lines with `exit=0`.)

Scope matters: **do not drop the `-- plugins/`.** Unscoped, the phrase still hits four `docs/superpowers/` records (`2026-07-20-dev-flow-design.md:114`, `2026-07-24-gh-6-docs-policy-plan.md:643/649/669`). Those are dated records and are **not** to be "also fixed" (design, *What was verified* and *Removed phrase*).

- [ ] **Step 5: Confirm the working tree touched only the two `SKILL.md` files**

Run from `ROOT`:

```bash
git status --short
```

Expected exactly two modified paths:

```text
 M plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
 M plugins/dev-flow/skills/dev-flow/SKILL.md
```

Any other path — in particular `CONTEXT.md`, `CLAUDE.md`, or anything under `scripts/` — is a **scope violation and a blocker.** Revert the stray change and report it; do not commit it.

- [ ] **Step 6: Commit**

Run from `ROOT`:

```bash
git add plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
git commit -m "dev-flow: pin the review marker's framing and extraction (#38)"
```

---

## Task 2: Bump both plugin versions

**Files:**
- Modify: `/Users/taylor/dev/claude-plugins/.claude/worktrees/agent-a6f97b9ce555b8410/plugins/dev-flow/.claude-plugin/plugin.json` (the `"version"` line, currently line 3)
- Modify: `/Users/taylor/dev/claude-plugins/.claude/worktrees/agent-a6f97b9ce555b8410/plugins/dev-flow-worktree/.claude-plugin/plugin.json` (the `"version"` line, currently line 3)

**Interfaces:**
- Consumes: nothing from Task 1 mechanically, but Task 1's text edit is *why* this bump exists — the install cache is version-keyed, so an edit at an unchanged version is never picked up on re-sync (`CLAUDE.md`).
- Produces: `"version": "2.9.0"` and `"version": "1.11.0"`. Task 3's criteria 6 and 7 read both.

Minor, not patch, is deliberate: no version either plugin has ever shipped has a nonzero patch segment, and choosing a minor-vs-patch *convention* would be a `CLAUDE.md` edit, which is out of scope (design, *Version bumps*).

- [ ] **Step 1: Confirm the pre-bump versions**

Run from `ROOT`:

```bash
grep -n '"version"' plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
```

Expected:

```text
plugins/dev-flow/.claude-plugin/plugin.json:3:  "version": "2.8.0",
plugins/dev-flow-worktree/.claude-plugin/plugin.json:3:  "version": "1.10.0",
```

If either differs from `2.8.0` / `1.10.0`, **halt and report** — the design's floors were computed against these (design, *Version state*).

- [ ] **Step 2: Edit `plugins/dev-flow/.claude-plugin/plugin.json`**

Use the Edit tool on `/Users/taylor/dev/claude-plugins/.claude/worktrees/agent-a6f97b9ce555b8410/plugins/dev-flow/.claude-plugin/plugin.json`.

Replace the exact string:

```text
  "version": "2.8.0",
```

with:

```text
  "version": "2.9.0",
```

Change nothing else in the file — not formatting, not key order, not the trailing newline.

- [ ] **Step 3: Edit `plugins/dev-flow-worktree/.claude-plugin/plugin.json`**

Use the Edit tool on `/Users/taylor/dev/claude-plugins/.claude/worktrees/agent-a6f97b9ce555b8410/plugins/dev-flow-worktree/.claude-plugin/plugin.json`.

Replace the exact string:

```text
  "version": "1.10.0",
```

with:

```text
  "version": "1.11.0",
```

Change nothing else in the file.

- [ ] **Step 4: Verify both bumps and that the JSON still parses**

Run from `ROOT`:

```bash
python3 -c "import json;print(json.load(open('plugins/dev-flow/.claude-plugin/plugin.json'))['version'],json.load(open('plugins/dev-flow-worktree/.claude-plugin/plugin.json'))['version'])"
```

Expected: `2.9.0 1.11.0`

- [ ] **Step 5: Verify exactly one line moved in each manifest**

Run from `ROOT`:

```bash
git diff --numstat plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
```

Expected — one added, one deleted, per file:

```text
1	1	plugins/dev-flow-worktree/.claude-plugin/plugin.json
1	1	plugins/dev-flow/.claude-plugin/plugin.json
```

Then confirm scope with `git status --short` from `ROOT`: the only modified paths must be the two manifests (Task 1's `SKILL.md` edits are already committed). Anything else is a blocker.

- [ ] **Step 6: Commit**

Run from `ROOT`:

```bash
git add plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
git commit -m "dev-flow 2.9.0, dev-flow-worktree 1.11.0 (#38)"
```

---

## Task 3: Run the design's success criteria (1–8, including run 7a)

**Files:**
- Modify: none. This task changes no repo file. If it makes you want to change one, that is a finding to report, not an edit to make.
- Test: `/private/tmp/claude-501/-Users-taylor-dev-claude-plugins/bab62c20-63f5-4951-b1c6-d34b0e5ae74e/scratchpad/criteria.py` (scratch, never committed)

**Interfaces:**
- Consumes: the four edited files from Tasks 1 and 2, both committed; `read_blocks` from `scripts/design_blocks.py`.
- Produces: a recorded criteria pass, **and** the hand-off of run 7b (Step 9). The identical program is re-run unmodified at the `pre-merge` halt to obtain 7b — see § *Run 7b — an orchestrator step at the `pre-merge` halt*.

This is the substance of the change. There is no test framework in this repo; these criteria are the entire verification surface (design, A5).

- [ ] **Step 1: Criterion 1 — `check-sync.py`**

Run from `ROOT`:

```bash
python3 scripts/check-sync.py ; echo "exit=$?"
```

Expected, verbatim, `exit=0`:

```text
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)
check-sync: all checks passed
```

The mirror-pair line must be **unchanged** — this change touches neither member of the `adversarial-review` pair, and the criterion exists to prove it did not perturb them. Remember what this does **not** prove: `check-sync.py` has no knowledge of the pipeline `SKILL.md` pair this change edits. Criteria 3, 4, and 5 are what cover that.

- [ ] **Step 2: Criterion 2 — `claude plugin validate .`**

Run from `ROOT`:

```bash
claude plugin validate . > /private/tmp/claude-501/-Users-taylor-dev-claude-plugins/bab62c20-63f5-4951-b1c6-d34b0e5ae74e/scratchpad/validate.txt 2>&1 ; echo "exit=$?"
grep -c 'No author information provided' /private/tmp/claude-501/-Users-taylor-dev-claude-plugins/bab62c20-63f5-4951-b1c6-d34b0e5ae74e/scratchpad/validate.txt
grep -ci 'error' /private/tmp/claude-501/-Users-taylor-dev-claude-plugins/bab62c20-63f5-4951-b1c6-d34b0e5ae74e/scratchpad/validate.txt
```

Expected: `exit=0`, then `8`, then `0`. Exactly 8 `No author information provided` warnings and no errors is the documented pass state (`CLAUDE.md`; design, A5).

- [ ] **Step 3: Criterion 3 — removed phrase, re-run post-commit**

Run from `ROOT`:

```bash
git grep -n 'with the marker line' -- plugins/ ; echo "exit=$?"
```

Expected: no output, `exit=1`. Keep the `-- plugins/` scope (see Task 1 Step 4).

- [ ] **Step 4: Refresh `origin/main`, then confirm the design's plain-fence shape — both are preconditions of the program**

**Refresh first.** The program's preamble fixes `BASE = git merge-base origin/main HEAD` from the *local* `refs/remotes/origin/main`; the program's own `git fetch` does not run until criterion 7, long after `BASE` is fixed. A stale tracking ref makes `BASE` an older ancestor than the true fork point, so every line `origin/main` itself moved in between counts as changed and criterion 6 fails as `('…/SKILL.md', {167, <some other line>})` — which reads exactly like a scope violation and is not one. Measured: with `origin/main` only three commits behind, `changed(DF)` is `{167, 266}` and `changed(WT)` is `{161, 261}`. Fetching before the program starts removes the failure mode instead of leaving it to be diagnosed. Run from `ROOT`:

```bash
git fetch origin main
```

`git fetch <remote> <branch>` opportunistically updates `refs/remotes/origin/main` under this repo's `+refs/heads/*:refs/remotes/origin/*` refspec — the same property criterion 7 already relies on.

**Then confirm the shape.** The criteria program indexes the design's two replacement blocks by position among its *plain* (untagged) fences. Confirm that shape is still `[1, 1]` before trusting the indexing. Run from `ROOT`:

```bash
python3 scripts/design_blocks.py docs/superpowers/specs/2026-08-02-gh-38-marker-framing-design.md
```

Expected:

```text
shape: [1, 1]
  [0] len=1: **Review state.** After Stage 4's review has committed its fixes and t
  [1] len=1: **Review state.** After Stage 4's review has committed its fixes and t
```

Any other shape means a rewrite added or removed a plain fence in the design. **That is a blocker: stop and report it.** Do not adjust the shape argument to match.

- [ ] **Step 5: Write the criteria 4–7 program**

Write **exactly** this to `/private/tmp/claude-501/-Users-taylor-dev-claude-plugins/bab62c20-63f5-4951-b1c6-d34b0e5ae74e/scratchpad/criteria.py`.

This is the design's *Success criteria* preamble followed by criteria 4, 5, 6, and 7, in that order — **one program, run top-to-bottom in a single interpreter.** Do not re-split it into four scripts, do not reorder it, do not re-derive `BASE` per criterion: the preamble is the only place `ROOT` is substituted, the only place `BASE` is computed, and the sole definition of every helper the four criteria share.

**Provenance, stated precisely enough to re-check.** These 76 lines are the design's five `python`-tagged fences under *Success criteria*, each dedented to column 0 and concatenated in document order with one blank line at each of the four seams. **Exactly one line differs from the design:** its `ROOT = "<working-dir, absolute>"   # the one substitution the implementation supplies` becomes the bare assignment below — the substitution the design leaves to the implementation, its now-spent comment dropped with it. Every other line is the design's, byte for byte.

```python
import json, subprocess, sys

ROOT = "/Users/taylor/dev/claude-plugins/.claude/worktrees/agent-a6f97b9ce555b8410"
sys.path.insert(0, f"{ROOT}/scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-02-gh-38-marker-framing-design.md"
DF = "plugins/dev-flow/skills/dev-flow/SKILL.md"
WT = "plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md"
JSON_DF = "plugins/dev-flow/.claude-plugin/plugin.json"
JSON_WT = "plugins/dev-flow-worktree/.claude-plugin/plugin.json"
TARGETS = [(DF, 167, 277), (WT, 161, 271)]      # path, 1-based anchor line, total lines
(_, DF_LINE, _), (_, WT_LINE, _) = TARGETS      # the only copy of the two line numbers

def run(*args):                   # every git call: same repo, non-zero fails loud
    return subprocess.run(["git", "-C", ROOT, *args],
                          capture_output=True, text=True, check=True).stdout

def split_lines(text):            # check-sync.py's rule; agrees with `wc -l`
    out = text.split("\n")
    if out and out[-1] == "":
        out.pop()
    return out

def blob(path, rev):              # a file's bytes as of <rev>, never the working tree
    return run("show", f"{rev}:{path}")

def here(path):                   # a file's bytes as they stand now
    return open(f"{ROOT}/{path}", encoding="utf-8").read()

BASE = run("merge-base", "origin/main", "HEAD").strip()   # computed, never pasted
old_df, old_wt = split_lines(blob(DF, BASE)), split_lines(blob(WT, BASE))
new_df, new_wt = split_lines(here(DF)), split_lines(here(WT))

blocks = read_blocks(f"{ROOT}/{DESIGN}", [1, 1])   # shape guards the indexing
for (path, lineno, total), block in zip(TARGETS, blocks):
    assert len(block) == 1, (path, len(block))
    lines = split_lines(here(path))
    assert len(lines) == total, (path, len(lines), total)
    assert lines[lineno - 1] == block[0], (path, lineno)
    assert lines.count(block[0]) == 1, (path, "block text is not unique")
print("design blocks ok")

b0, b1 = blocks[0][0], blocks[1][0]                 # the blocks criterion 4 read
assert b1.replace("dev-flow-worktree", "dev-flow") == b0        # the two design blocks
assert b0.count("dev-flow") == 1 and b1.count("dev-flow-worktree") == 1
# the same correspondence, in the files, after the edit:
assert new_wt[WT_LINE - 1].replace("dev-flow-worktree", "dev-flow") == new_df[DF_LINE - 1]
# and it is not newly created — it held at BASE too:
assert old_wt[WT_LINE - 1].replace("dev-flow-worktree", "dev-flow") == old_df[DF_LINE - 1]
print("substitution image ok")

def changed(path):                # 1-based line numbers whose text differs from BASE
    old = split_lines(blob(path, BASE))
    new = split_lines(here(path))
    assert len(old) == len(new), (path, len(old), len(new))
    return {i + 1 for i, (a, b) in enumerate(zip(old, new)) if a != b}

assert changed(DF) == {DF_LINE}, (DF, changed(DF))
assert changed(WT) == {WT_LINE}, (WT, changed(WT))
for path in (JSON_DF, JSON_WT):
    moved = changed(path)
    assert len(moved) == 1, (path, moved)
    assert '"version"' in split_lines(here(path))[next(iter(moved)) - 1], path
print("changed-line set ok")

WANT = {JSON_DF: (2, 9, 0), JSON_WT: (1, 11, 0)}   # the designed floor, not an equality
def ver(text):
    return tuple(int(p) for p in json.loads(text)["version"].split("."))
run("fetch", "origin", "main")     # refreshes refs/remotes/origin/main
for path, want in WANT.items():
    mine = ver(here(path))
    published = ver(blob(path, "origin/main"))
    assert mine >= want, (path, "below the designed version", mine, want)
    assert mine > published, (path, "not ahead of origin/main", mine, published)
print("versions ok")
```

- [ ] **Step 6: Run it — criteria 4, 5, 6, and run 7a**

Run: `python3 /private/tmp/claude-501/-Users-taylor-dev-claude-plugins/bab62c20-63f5-4951-b1c6-d34b0e5ae74e/scratchpad/criteria.py ; echo "exit=$?"`

Expected, in this order, `exit=0`:

```text
design blocks ok
substitution image ok
changed-line set ok
versions ok
```

What each line means, and what its failure means:

- `design blocks ok` (**criterion 4**) — both replacement lines landed verbatim, at their anchor lines, once each, with both files still at 277 and 271 lines. This is the second check *outside* the hand-mirrored pair. Failure here means the wrong bytes or the wrong line: re-run Task 1 Step 2, do not hand-patch.
- `substitution image ok` (**criterion 5**) — the hand-mirror actually mirrored. **This is the criterion a one-sided edit fails**, and it is the only thing in the repo that catches one; `check-sync.py` does not know this pair exists. Failure means one file got the edit and the other did not, or the two design blocks are not mirrors of each other — the latter is a design defect: **report it, do not repair the design.**
- `changed-line set ok` (**criterion 6**) — nothing outside the four intended lines moved, compared against `BASE` by line index. Each `plugin.json` is pinned to exactly one changed line containing `"version"`, with the line *number* deliberately unpinned.
- `versions ok` (**run 7a**) — both versions are at or above the designed floor **and strictly greater than `origin/main`'s**.

Note `run("fetch", "origin", "main")` at the top of criterion 7: it updates `refs/remotes/origin/main` so the comparison is against the published tip, and `check=True` means a failed fetch halts rather than silently comparing against a stale ref.

If criterion 7 fails with `not ahead of origin/main`, a concurrent PR published your target version. **Remediation (design, criterion 7):** re-target both versions upward — bump each to the next minor above the published one — then re-run the whole program from Step 6. `WANT` is a floor, not an equality, precisely so the criterion stays green through that remediation.

- [ ] **Step 7: Criterion 8 — file scope**

Run from `ROOT`:

```bash
git diff --stat $(git merge-base origin/main HEAD)..HEAD
```

Expected: **only** these paths appear —

- `plugins/dev-flow/skills/dev-flow/SKILL.md`
- `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`
- `plugins/dev-flow/.claude-plugin/plugin.json`
- `plugins/dev-flow-worktree/.claude-plugin/plugin.json`
- paths under `docs/superpowers/` (this plan and its design)

Any other path — **in particular `CONTEXT.md`, `CLAUDE.md`, or anything under `scripts/`** — is a scope violation and a **blocker, not a fix to apply.**

- [ ] **Step 8: Confirm the working tree is clean and nothing was left uncommitted**

Run from `ROOT`:

```bash
git status --short
```

Expected: no output. The scratchpad scripts live outside the repo and must never be added.

- [ ] **Step 9: Record the pass, and hand run 7b to the orchestrator**

No commit is needed — this task changed no file. Report the criteria pass as: criteria 1, 2, 3, 8 green (shell); criteria 4, 5, 6 and **run 7a** green (one Python program).

**This step is not complete until the report also carries the hand-off below.** A criteria pass reported without 7b is incomplete (design, criterion 7); 7b is not a task in this plan; and this report — which the orchestrator reads before it may proceed to Stage 4 — is the only place 7b is delivered to the agent that must run it. Ticking this box with the criteria results but without the hand-off is a **failed** step, not a partial one. The report must carry, in these terms:

> **Run 7b is outstanding, and it is not a plan task.** It is an orchestrator step at the `pre-merge` halt, specified in full in this plan's § *Run 7b — an orchestrator step at the `pre-merge` halt*. The `pre-merge` halt report is incomplete without 7b's output, and **any future `gh pr merge` on this branch must be preceded by a fresh 7b** — the merge gate (`SKILL.md:244`–`:254`) re-runs the marker check and CI and nothing else, so nothing between the halt and the merge would notice a version that went stale during the pause.

With this box ticked, nothing else in this plan is left to do: zero checkboxes remain, Stage 3's exit condition (`SKILL.md:228`) is satisfied, and the pipeline proceeds to Stage 4.

---

## Run 7b — an orchestrator step at the `pre-merge` halt

**This section is not a task and contains no checkboxes.** It is addressed to the orchestrator running `dev-flow`, and it is discharged inside **Stage 4**, after the PR is pushed and the marker is posted (`SKILL.md:239`), immediately before the `pre-merge` halt (`SKILL.md:240`).

It is prose for a mechanical reason, not a stylistic one: see the Global Constraint *No checkbox outside Tasks 1–3*. The design agrees with this placement — criterion 7 locates 7b "immediately before the pipeline **halts** at `pre-merge`", which is a pipeline moment — and the *Notes* section below already records two other design items (**A6**, **A8**) that belong to the pipeline's integration step rather than to the implementation. 7b carries more weight than those two, because it is a success criterion, which is why Task 3 Step 9's hand-off is a mandatory Stage-3 delivery of this section rather than a passing note.

**When:** after the last merge or rebase of `origin/main` into this branch, after the PR is pushed and reviewed and the marker is posted, and **immediately before** the pipeline halts at `pre-merge`. Not earlier. Its whole value is *when* it runs.

**Files:** none, unless remediation is needed (then: the two `plugin.json` files only).

**Program:** the same `/private/tmp/claude-501/-Users-taylor-dev-claude-plugins/bab62c20-63f5-4951-b1c6-d34b0e5ae74e/scratchpad/criteria.py` written in Task 3 Step 5, **unmodified**. Re-running it whole satisfies the design's requirement that criterion 6 be re-run before 7b, without re-splitting the program.

**Why this exists.** This bit a real pipeline. PR #37 was designed against versions `2.7.0`/`1.9.0`; PRs #35 and #36 merged while it was in flight and took exactly those numbers. Merging `origin/main` into the branch **auto-resolved with no conflict** — both sides moved the same line in the same direction, so git saw nothing to ask about — which would have shipped the change's text at an already-published version the cache would never pick up. `check-sync.py` does not see it. `claude plugin validate .` does not see it. A criterion asserting `"version": "2.9.0"` as a literal does not see it either. **Run 7b is the only check in the entire set that notices.**

### Steps

1. **Confirm the branch is at its final pre-merge state.** Run from `ROOT`:

   ```bash
   git fetch origin main
   git status --short
   git log --oneline -1
   ```

   Expected: clean working tree, and `HEAD` at the commit that will be merged. If `origin/main` has not yet been merged or rebased in for the last time, **do that first** — running 7b before the last integration proves nothing. The fetch leads for the reason given in Task 3 Step 4, and here it matters for the integration itself: `git merge origin/main` reads the *local* tracking ref, so an unfetched one merges a tip that is not the published one — the precise blindness run 7b exists to catch.

2. **Confirm `criteria.py` still exists and is unmodified.** If the file is missing (a fresh session, a cleared scratchpad), re-create it from Task 3 Step 5 verbatim. Do not write a reduced version that runs criterion 7 alone — the program is not splittable.

   ```bash
   ls -l /private/tmp/claude-501/-Users-taylor-dev-claude-plugins/bab62c20-63f5-4951-b1c6-d34b0e5ae74e/scratchpad/criteria.py
   ```

3. **Re-run the program — this yields run 7b.**

   ```bash
   python3 /private/tmp/claude-501/-Users-taylor-dev-claude-plugins/bab62c20-63f5-4951-b1c6-d34b0e5ae74e/scratchpad/criteria.py ; echo "exit=$?"
   ```

   Expected, `exit=0`:

   ```text
   design blocks ok
   substitution image ok
   changed-line set ok
   versions ok
   ```

   The final `versions ok` **is run 7b.** Its `assert mine > published` now compares against the `origin/main` tip as of this moment, freshly fetched.

4. **Handle a 7b failure.** If it fails with `not ahead of origin/main`: a concurrent PR landed your version number and the merge auto-resolved silently. **Remediate, do not override.** Bump each affected `plugin.json` to the next minor above the published version (e.g. published `2.9.0` → set `2.10.0`; published `1.11.0` → set `1.12.0`), commit with a message naming the reason, push, then **return to step 3 and re-run the whole program.** `WANT` is a floor, so the criterion stays green through this remediation. Note that this commit moves head and therefore invalidates the marker (`SKILL.md:169`); that is correct and expected — the pipeline's own Stage 4 re-review and re-post is the right response, not a hand-edited marker.

   If instead `changed-line set ok` fails after the merge for a reason unrelated to the version lines — `changed(DF)` returning more than `{167}` — rule out the cheap cause first: **a stale `refs/remotes/origin/main` produces exactly this failure**, because `BASE` is then an older ancestor than the true fork point and every line `origin/main` moved in between counts as changed. Run `git fetch origin main` and re-run the program once. If it still fails, `origin/main` really has moved other lines in one of the two `SKILL.md` files, and that is **a blocker: stop and report it verbatim.** Do not silently loosen the assertion; a concurrent edit to the same paragraph needs a human or a re-review, not an adjusted criterion.

5. **Put 7b in the halt report, and bind the merge.** The `pre-merge` halt report (`SKILL.md:240`, whose testing note `SKILL.md:36` makes a mandatory part of the report rather than a separate state) must carry the complete criteria status: 1, 2, 3, 8 green; 4, 5, 6 green; **7a** green (Task 3) **and 7b** green (this section), with 7b's timing stated — "re-run after the final `origin/main` integration, immediately before the halt". Then halt at `pre-merge`. Do **not** merge.

   The testing note must additionally carry this precondition, verbatim:

   > **Before any `gh pr merge` on this branch, re-run `criteria.py` (§ *Run 7b*, step 3) and require `versions ok`.** 7b was green at the halt, but a `pre-merge` stop is a human-review pause that can last days, and the merge gate re-verifies nothing that would catch a version that went stale during it: `SKILL.md:244`–`:254` steps 1–5 are push + marker, bounded CI wait, `stops`, strip (a no-op under `docs: commit`), and `gh pr merge --squash`. The marker stays valid the whole time, correctly — it certifies "reviewed and suite-green at this exact SHA" and the SHA did not change. This repo's only CI (`.github/workflows/check-sync.yml` → `scripts/check-sync.py`) checks manifest descriptions and the `adversarial-review` mirror pair, not versions. And `gh pr merge` cannot refuse the collision, because both sides write the byte-identical `"version"` line: the merge auto-resolves silently and the squash produces no version change at all. Insert the re-run **before merge-gate step 5**; on failure, remediate per step 4 above rather than merging.

   This precondition is more than the design's criterion 7 asks for — it requires a third run, not two — and it is applied deliberately, not by drift. It is the design's own stated reason ("only if it is re-run **after** the last merge or rebase, immediately before the halt") applied to a run that halts and does **not** merge, where the latest point before the merge is the resume rather than the halt. It is surfaced as an observation in the *Notes* section below rather than escalated as a design conflict, because nothing in the design forbids it and it points in the design's own direction. That the plan can only state this precondition and not enforce it is a gap in the pipeline spec, not in this plan — see the *Notes* section's recommended follow-up issue.

---

## Notes for the reviewer of this plan

- **The design is the higher-reviewed artifact.** If any step here appears to conflict with `docs/superpowers/specs/2026-08-02-gh-38-marker-framing-design.md`, the design wins — report the conflict rather than deciding.
- **Design items deliberately not tasks here, because the design assigns them to the pipeline, not to the implementation.** Recorded so they do not read as dropped. The load-bearing one is **run 7b**: it is a success criterion, so it is specified in full in its own section above (§ *Run 7b — an orchestrator step at the `pre-merge` halt*) and handed to the orchestrator by a mandatory, Stage-3-completable checkbox (Task 3 Step 9), rather than merely noted here. Two others touch no file in the authorized set: **A6** — file a follow-up GitHub issue asking whether `CONTEXT.md` should carry a `Marker` glossary entry, after first checking no equivalent open issue exists; **A8** — issue #38 closes on merge, with *The edit* and the design's ruling as the closing reference. **A7** is recorded in the design, not filed, and needs no action at all.
- **Two things this plan does that the design does not require, both surfaced rather than smuggled.** (i) § *Run 7b* step 5 requires a **third** version re-check immediately before any future `gh pr merge`, where criterion 7 requires two. This is the design's own rationale ("only if it is re-run after the last merge or rebase, immediately before the halt") applied to a run that halts and does not merge — the latest point before the merge is then the resume, not the halt — and the merge gate provably re-verifies nothing else (`SKILL.md:244`–`:254`). Not treated as a design conflict: nothing in the design forbids it and it strictly strengthens the criterion in the design's own direction. (ii) Run 7b is carried as an orchestrator instruction rather than a plan task; that is a correction toward the design, which places 7b at a pipeline moment, not a `- [ ]` moment.
- **Recommended follow-up GitHub issue (file at integration, alongside A6; check first that no equivalent open issue exists).** Both of the above are workarounds for the same missing pipeline vocabulary, and the durable fix belongs in `SKILL.md`, which is out of scope for this branch (its authorized edit is exactly one line per file): *"dev-flow: a check that must run after Execute has nowhere to live, and the merge gate re-verifies nothing but the marker and CI."*
- **Nothing in this plan writes a `.md` report file.** Findings go back as text.
- **All four scratchpad scripts are disposable.** They live outside the repo by design; `git status --short` must never show them.
