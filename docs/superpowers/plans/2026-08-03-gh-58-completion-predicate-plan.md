---
dev-flow:
  slug: gh-58-completion-predicate
  spec: docs/superpowers/specs/2026-08-03-gh-58-completion-predicate-design.md
---

# gh-58 Completion-Predicate (line-anchored count) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redefine the dev-flow Execute-completion predicate so it counts real task checkboxes (lines matching `^[[:space:]]*[-*+] \[ \]`) instead of every raw `- [ ]` token, which is unsatisfiable because `writing-plans` emits the token in a documentation blockquote header.

**Architecture:** Four whole-line replacements — the **Execution-complete signal** paragraph and the resume-table row — in each of the two mirrored pipeline `SKILL.md` files, plus a minor version bump for each plugin. No new tooling; the predicate stays orchestrator-interpreted prose. The exact replacement text is fixed by the design as four fenced blocks (shape `[1, 1, 1, 1]`) and is re-read from the design on disk during verification, never retyped.

**Tech Stack:** Markdown `SKILL.md` files; `plugin.json` manifests; verification via `git grep`, `git show`, `python3 scripts/design_blocks.py` / `read_blocks`, `python3 scripts/check-sync.py`, `python3 scripts/check-version-bump.py`, `claude plugin validate .`. No automated test suite exists in this repo.

## About this run (meta note)

The predicate this change fixes is the exact one the running orchestrator uses to judge Execute-completion. The orchestrator evaluates completion by the **anchored** count — real line-start task boxes (`^[[:space:]]*[-*+] \[ \]`) — so this plan uses normal task checkboxes and its real tasks (the `- [ ]` steps below) are what get ticked. No contortion of the `writing-plans` boilerplate header is needed: that header's `- [ ]` sits inside an inline code span on a blockquote line (`> …`), which the anchored predicate excludes. Likewise every `- [ ]` quoted inside the fenced blocks below starts with `**` or `|`, never `- [ ]` at line start, so it is not counted either.

## Global Constraints

- **No automated test suite.** "Tests" are: the phrase-removal greps (criterion #1), the design-block re-read + byte-for-byte blob check (criterion #2), the anchored-predicate corpus demonstration (criterion #3), the shipped-literal pin `git grep -F -- '^[[:space:]]*[-*+] \[ \]' -- plugins/` (criterion #7), `python3 scripts/check-sync.py` (#4), `python3 scripts/check-version-bump.py origin/main` (#5), and `claude plugin validate .` (#6, 8 missing-author warnings expected).
- **Design is authoritative.** `docs/superpowers/specs/2026-08-03-gh-58-completion-predicate-design.md`; block shape `[1, 1, 1, 1]`. Any plan-vs-design conflict resolves to the design.
- **Byte-identical literal.** The regex literal `^[[:space:]]*[-*+] \[ \]` must land character-for-character identical at all four edited sites — criterion #7 depends on it.
- **Mirrored pair, hand-mirrored.** The pipeline `SKILL.md` pair (`plugins/dev-flow/skills/dev-flow/SKILL.md` and `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`) is **not** in `scripts/check-sync.py`'s `MIRROR_PAIRS`. Both files must be edited by hand, and the change must be cross-verified against something **outside** the pair — here the measured plan corpus (criterion #3). A doubled-identical mistake passes every pair-internal comparison, so the corpus demonstration is the load-bearing check.
- **Version bump on behavior change.** Bump the **minor** segment of each touched plugin's `version`, ahead of `origin/main`'s tip (not merely past this branch's base). Re-check `origin/main` at execute time.
- **Command discipline.** Every git ref a step computes is captured to a variable, validated non-empty, and quoted (or passed as an `argv` element) — never an unguarded inline substitution. `base=$(git rev-parse origin/main)`, halt if empty.
- **Do NOT commit.** The pipeline's adversarial-review stage commits this work; leave the tree dirty.

---

### Task 1: Land the anchored-predicate edit in both mirrored `SKILL.md` files and bump both plugin versions

Applies all four block replacements and both version bumps as one reviewable unit (the mirror obligation means the two files move together), then proves locally that exactly the intended lines changed to exactly the design's block text.

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md` (line 165 = signal paragraph, line 191 = resume row)
- Modify: `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` (line 159 = signal paragraph, line 185 = resume row)
- Modify: `plugins/dev-flow/.claude-plugin/plugin.json` (`version` field)
- Modify: `plugins/dev-flow-worktree/.claude-plugin/plugin.json` (`version` field)
- Read (verification source, never edited): `docs/superpowers/specs/2026-08-03-gh-58-completion-predicate-design.md`, `scripts/design_blocks.py`

**Interfaces:**
- Consumes: the design's four fenced blocks, shape `[1, 1, 1, 1]`, obtained via `read_blocks(DESIGN, [1, 1, 1, 1])` where `read_blocks` comes from `scripts/design_blocks.py` (`sys.path.insert(0, "scripts")`). `read_blocks` returns a list of four one-element lists; `b[i][0]` is the full replacement line for Block `[i]`.
- Produces: two edited `SKILL.md` files whose lines 165/191 (dev-flow) and 159/185 (worktree) equal Blocks [0]/[2] and [1]/[3] respectively; two bumped `plugin.json` versions. Task 2 consumes these for the repo-wide verification pass.

- [x] **Step 1: Confirm the design block shape before touching anything**

Run:
```bash
python3 scripts/design_blocks.py docs/superpowers/specs/2026-08-03-gh-58-completion-predicate-design.md
```
Expected: first line reads `shape: [1, 1, 1, 1]`, with `[0]`/`[1]` starting `**Execution-complete signal.**` and `[2]`/`[3]` starting `| Plan at tip has ≥1 unchecked task box`. If the shape is anything other than `[1, 1, 1, 1]`, STOP — the design's blocks moved and every edit below is misrouted.

- [x] **Step 2: Replace `plugins/dev-flow/skills/dev-flow/SKILL.md` line 165 (signal paragraph) with Block [0]**

Old line (`old_string`, currently line 165 — note the parenthetical **"is not durable pipeline state"**):
```text
**Execution-complete signal.** When a task's review comes back clean, the orchestrator (SDD's controller) ticks that task's `- [ ]` checkboxes in the plan file and commits them, alongside SDD's ledger append. **Committed checkboxes are the durable, authoritative cross-session signal; SDD's `.superpowers/sdd/progress.md` ledger stays in-session scratch (it is git-ignored and is not durable pipeline state).** Execution is complete if and only if zero `- [ ]` remain in the plan at branch tip. Tie-break: if `git log` shows a task's commits but its boxes are unticked (a crash in the gap), verify via `git log`, tick the boxes, and do not re-implement.
```
Replace with Block [0] (`new_string`):
```text
**Execution-complete signal.** When a task's review comes back clean, the orchestrator (SDD's controller) ticks that task's `- [ ]` checkboxes in the plan file and commits them, alongside SDD's ledger append. **Committed checkboxes are the durable, authoritative cross-session signal; SDD's `.superpowers/sdd/progress.md` ledger stays in-session scratch (it is git-ignored and is not durable pipeline state).** Execution is complete if and only if the plan at branch tip has zero unchecked task boxes — lines matching `^[[:space:]]*[-*+] \[ \]` (a task checkbox at line start, optionally indented; markdown's `-`, `*`, and `+` bullets all render a checkbox, so all three count). The count is line-anchored, not a raw token count: a `- [ ]` inside an inline code span or a blockquote line — such as the `writing-plans` header that documents the checkbox syntax — is documentation of the syntax, not a task, and the anchor excludes it. (A line-start task checkbox inside a fenced code block would still match; `writing-plans` emits none, and even if one appeared, over-counting only keeps Execute running rather than ever signalling a false complete.) Tie-break: if `git log` shows a task's commits but its boxes are unticked (a crash in the gap), verify via `git log`, tick the boxes, and do not re-implement.
```

- [x] **Step 3: Replace `plugins/dev-flow/skills/dev-flow/SKILL.md` line 191 (resume row) with Block [2]**

Old line (`old_string`):
```text
| Plan at tip has ≥1 unchecked `- [ ]` | Execute — resume at first unchecked task (cross-check ledger + `git log`) |
```
Replace with Block [2] (`new_string`):
```text
| Plan at tip has ≥1 unchecked task box (a line matching `^[[:space:]]*[-*+] \[ \]`) | Execute — resume at first unchecked task (cross-check ledger + `git log`) |
```

- [x] **Step 4: Replace `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` line 159 (signal paragraph) with Block [1]**

Old line (`old_string`, currently line 159 — note the parenthetical **"dies with the worktree"**, the only difference from the dev-flow copy):
```text
**Execution-complete signal.** When a task's review comes back clean, the orchestrator (SDD's controller) ticks that task's `- [ ]` checkboxes in the plan file and commits them, alongside SDD's ledger append. **Committed checkboxes are the durable, authoritative cross-session signal; SDD's `.superpowers/sdd/progress.md` ledger stays in-session scratch (it is git-ignored and dies with the worktree).** Execution is complete if and only if zero `- [ ]` remain in the plan at branch tip. Tie-break: if `git log` shows a task's commits but its boxes are unticked (a crash in the gap), verify via `git log`, tick the boxes, and do not re-implement.
```
Replace with Block [1] (`new_string`):
```text
**Execution-complete signal.** When a task's review comes back clean, the orchestrator (SDD's controller) ticks that task's `- [ ]` checkboxes in the plan file and commits them, alongside SDD's ledger append. **Committed checkboxes are the durable, authoritative cross-session signal; SDD's `.superpowers/sdd/progress.md` ledger stays in-session scratch (it is git-ignored and dies with the worktree).** Execution is complete if and only if the plan at branch tip has zero unchecked task boxes — lines matching `^[[:space:]]*[-*+] \[ \]` (a task checkbox at line start, optionally indented; markdown's `-`, `*`, and `+` bullets all render a checkbox, so all three count). The count is line-anchored, not a raw token count: a `- [ ]` inside an inline code span or a blockquote line — such as the `writing-plans` header that documents the checkbox syntax — is documentation of the syntax, not a task, and the anchor excludes it. (A line-start task checkbox inside a fenced code block would still match; `writing-plans` emits none, and even if one appeared, over-counting only keeps Execute running rather than ever signalling a false complete.) Tie-break: if `git log` shows a task's commits but its boxes are unticked (a crash in the gap), verify via `git log`, tick the boxes, and do not re-implement.
```

- [x] **Step 5: Replace `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` line 185 (resume row) with Block [3]**

Block [3] is byte-identical to Block [2]. Old line (`old_string`):
```text
| Plan at tip has ≥1 unchecked `- [ ]` | Execute — resume at first unchecked task (cross-check ledger + `git log`) |
```
Replace with Block [3] (`new_string`):
```text
| Plan at tip has ≥1 unchecked task box (a line matching `^[[:space:]]*[-*+] \[ \]`) | Execute — resume at first unchecked task (cross-check ledger + `git log`) |
```

- [x] **Step 6: Bump `plugins/dev-flow/.claude-plugin/plugin.json` version to `2.13.0` (re-checked against `origin/main`)**

First read what `origin/main` publishes, then bump past it:
```bash
base=$(git rev-parse origin/main); [ -n "$base" ] || { echo "empty base"; exit 1; }
git show "$base:plugins/dev-flow/.claude-plugin/plugin.json" | python3 -c "import json,sys; print(json.load(sys.stdin)['version'])"
```
If it prints `2.12.0`, edit the manifest's `version` field from `2.12.0` to `2.13.0` (bump the minor segment). If `origin/main` has advanced past `2.12.0`, bump the minor segment past whatever it now publishes instead (e.g. if it prints `2.13.0`, use `2.14.0`). Edit only the `version` value; leave the rest of the manifest untouched.

- [x] **Step 7: Bump `plugins/dev-flow-worktree/.claude-plugin/plugin.json` version to `1.15.0` (re-checked against `origin/main`)**

Same procedure:
```bash
base=$(git rev-parse origin/main); [ -n "$base" ] || { echo "empty base"; exit 1; }
git show "$base:plugins/dev-flow-worktree/.claude-plugin/plugin.json" | python3 -c "import json,sys; print(json.load(sys.stdin)['version'])"
```
If it prints `1.14.0`, edit the `version` field from `1.14.0` to `1.15.0`. If `origin/main` has advanced, bump the minor segment past whatever it now publishes.

- [x] **Step 8: Verify the removed phrasing is gone (criterion #1)**

Run — both must return **no** output (exit status 1 from grep is expected on no match):
```bash
git grep -F -- 'Execution is complete if and only if zero' -- plugins/
git grep -F -- 'unchecked `- [ ]`' -- plugins/
```
Expected: neither prints any line. (The surviving `` `- [ ]` `` in each signal paragraph is the *action* verb "ticks that task's `- [ ]` checkboxes", which is intended to remain — these greps target only the removed phrasings, not the bare token.)

- [x] **Step 9: Verify the shipped anchored literal is present in both files (criterion #7)**

Run:
```bash
git grep -F -- '^[[:space:]]*[-*+] \[ \]' -- plugins/
```
Expected: **four** matching lines — the signal paragraph and the resume row in each of the two `SKILL.md` files. `-F` (fixed-string) is required because the literal is entirely regex metacharacters. This pins the character-for-character string that ships to the one the corpus demonstration (Task 2) validates.

- [x] **Step 10: Run the design-block re-read + byte-for-byte blob check (criterion #2)**

Run this inline — a `python3 - <<'PY'` heredoc, so nothing is written into the repo (the old `scratchpad/verify_blocks.py` path does not exist in the repo root and would leave an untracked file an Execute-stage `git add` could sweep in). It re-reads the four blocks from the design on disk (never retyped), **locates each edit site by its old line's anchor in the `origin/main` blob** (so it survives an `origin/main` line-shift above the site instead of asserting a stale hardcoded index), asserts each new block landed verbatim at that site, asserts the two parentheticals landed in the correct files (not swapped — each block is pinned to the base line that held *that* file's signal paragraph), and asserts each touched `SKILL.md` is its `origin/main` blob with **exactly** the two intended line replacements and nothing else:
```bash
python3 - <<'PY'
import subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-03-gh-58-completion-predicate-design.md"
b = read_blocks(DESIGN, [1, 1, 1, 1])          # exits non-zero if the shape moved
b0, b1, b2, b3 = b[0][0], b[1][0], b[2][0], b[3][0]

base = subprocess.run(["git", "rev-parse", "origin/main"],
                      capture_output=True, text=True, check=True).stdout.strip()
assert base, "empty base ref"

DF = "plugins/dev-flow/skills/dev-flow/SKILL.md"
WT = "plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md"

def blob_lines(path):
    out = subprocess.run(["git", "show", f"{base}:{path}"],
                         capture_output=True, text=True, check=True).stdout
    return out.split("\n")

def locate(base_lines, anchor, path):
    """Index of the single base-blob line carrying this anchor -- where the edit
    must land. Located per file so the check survives an origin/main line-shift
    above the site, and so a base that no longer matches (anchor missing or
    duplicated) halts loudly instead of asserting a stale line number."""
    hits = [i for i, ln in enumerate(base_lines) if anchor in ln]
    assert len(hits) == 1, f"{path}: base anchor {anchor!r} matched {len(hits)} lines, want 1"
    return hits[0]

def check(path, sites):
    """sites: [(anchor in the OLD line, its design block)]. Asserts the working
    tree is the base blob with EXACTLY those lines replaced by their blocks and
    nothing else changed. Pinning each block to the base line that held that
    file's signal paragraph is also what catches a swapped parenthetical: b0
    landing in the worktree file fails its cur_lines[idx] == b1 assertion."""
    base_lines = blob_lines(path)
    cur_lines = Path(path).read_text(encoding="utf-8").split("\n")
    assert len(base_lines) == len(cur_lines), \
        f"{path}: line count changed {len(base_lines)} -> {len(cur_lines)}"
    want = {locate(base_lines, anchor, path): blk for anchor, blk in sites}
    diffs = [i for i in range(len(base_lines)) if base_lines[i] != cur_lines[i]]
    assert diffs == sorted(want), \
        f"{path}: changed lines (1-indexed) {[d+1 for d in diffs]}, want " \
        f"{sorted(i+1 for i in want)} (the base lines holding the signal paragraph " \
        f"and resume row; an origin/main line-shift is fine -- the anchors relocate)"
    for idx, blk in want.items():
        assert cur_lines[idx] == blk, f"{path}: line {idx+1} does not equal its design block"
    print(f"OK {path}: exactly lines {sorted(i+1 for i in want)} changed, each to its design block")

check(DF, [("**Execution-complete signal.**", b0), ("Plan at tip has", b2)])
check(WT, [("**Execution-complete signal.**", b1), ("Plan at tip has", b3)])
print("PASS: both files are base + exactly the two intended block replacements; parentheticals correctly placed")
PY
```
Expected: two `OK …` lines then `PASS: …`. Any `AssertionError` or non-zero exit means STOP and fix before Task 2.

---

### Task 2: Whole-change verification pass (repo-wide gates + corpus behavior)

Proves the predicate *behaves* correctly on the real plan corpus (the outside-the-pair cross-check the mirror obligation requires) and that the repo's mechanical gates stay green. Runs against `origin/main` (the pre-edit tree) for the behavior demo, and against the working tree for the gates.

**Files:** none modified — verification only. Reads `docs/superpowers/plans/*.md` at `origin/main`, `scripts/check-sync.py`, `scripts/check-version-bump.py`, and the whole marketplace via `claude plugin validate .`.

**Interfaces:**
- Consumes: Task 1's edited working tree (for the version-bump and sync gates and the shipped literal).
- Produces: evidence that all seven design success criteria hold. No artifacts.

- [ ] **Step 1: Demonstrate the anchored predicate excludes markup on real plans (criterion #3)**

Run:
```bash
base=$(git rev-parse origin/main); [ -n "$base" ] || { echo "empty base"; exit 1; }

# Headline single plan: a fully-ticked plan that still carries the writing-plans header.
p="docs/superpowers/plans/2026-08-02-gh-38-marker-framing-plan.md"
raw=$(git show "$base:$p" | grep -c -- '- \[ \]')
anc=$(git show "$base:$p" | grep -cE '^[[:space:]]*[-*+] \[ \]')
echo "raw=$raw anchored=$anc  ($p)"   # expect: raw=3 (old count: never-complete)  anchored=0 (new count: complete)

# All 18 plans: dash-only and [-*+] anchored counts must agree (corpus has no * or +
# task bullets), and the anchored count is non-zero for exactly the three
# pre-discipline plans. A disagreement is a HARD FAILURE printed on its own line and
# forced to a non-zero exit -- never fed into `sort -rn`, where a non-numeric
# MISMATCH line sorts as 0 and hides *below* the counts. The loop runs in this
# shell (process substitution, not a pipe) so the flag survives it.
mismatch=0
counts=""
while read -r f; do
  a_dash=$(git show "$base:$f" | grep -cE '^[[:space:]]*- \[ \]')
  a_all=$(git show "$base:$f" | grep -cE '^[[:space:]]*[-*+] \[ \]')
  if [ "$a_dash" != "$a_all" ]; then
    echo "MISMATCH dash=$a_dash all=$a_all  $f"
    mismatch=1
  fi
  [ "$a_all" != "0" ] && counts="$counts$a_all  $f
"
done < <(git ls-tree -r --name-only "$base" -- docs/superpowers/plans/ | grep '\.md$')
printf '%s' "$counts" | sort -rn
if [ "$mismatch" != 0 ]; then
  echo "FAIL: a plan's dash-anchored and [-*+]-anchored counts differ (see MISMATCH above)"; exit 1
fi
echo "OK: no dash-vs-[-*+] mismatch on any plan"
```
Expected: `raw=3 anchored=0` for the headline plan; no `MISMATCH …` line; exactly three non-zero count lines — `32  …/2026-07-20-dev-flow-plan.md`, `26  …/2026-07-28-gh-16-terminology-collision-plan.md`, `24  …/2026-07-22-dev-flow-nested-review-fix.md`; then a final `OK: no dash-vs-[-*+] mismatch on any plan` (exit 0). A `MISMATCH`/`FAIL` line + non-zero exit means a plan carries a line-start `* [ ]` or `+ [ ]` task box — stop and reconcile, since the design's `-`-only corpus measurement assumes there are none. This is the load-bearing outside-the-pair check.

- [ ] **Step 2: `check-sync.py` still exits 0 (criterion #4)**

Run:
```bash
python3 scripts/check-sync.py; echo "exit=$?"
```
Expected: `exit=0`. The edit touches no `adversarial-review` file and no manifest `description`, and the pipeline pair is outside `MIRROR_PAIRS`, so sync is unaffected.

- [ ] **Step 3: Verify both plugins are bumped ahead of `origin/main` (criterion #5)**

The load-bearing local check is a **working-tree** version comparison. `scripts/check-version-bump.py` is *vacuous here*: it diffs committed trees (`git diff merge-base HEAD`), but by the Global Constraint the bumps are still uncommitted at Execute time, so it finds no `plugins/` path and prints `no plugin directory touched ... OK` (exit 0) **whether or not the bumps were made**. So assert the bump directly against the working tree, then run the CI command as a parity dry-run.

```bash
base=$(git rev-parse origin/main); [ -n "$base" ] || { echo "empty base"; exit 1; }
python3 - "$base" <<'PY'
import json, subprocess, sys
base = sys.argv[1]
def ver(text, where):
    v = json.loads(text)["version"]
    p = v.split(".")
    assert len(p) == 3 and all(x.isdigit() for x in p), f"{where}: version {v!r} is not X.Y.Z"
    return tuple(int(x) for x in p), v
ok = True
for name in ("dev-flow", "dev-flow-worktree"):
    path = f"plugins/{name}/.claude-plugin/plugin.json"
    wt, wt_s = ver(open(path, encoding="utf-8").read(), f"{name} (working tree)")
    bm, bm_s = ver(subprocess.run(["git", "show", f"{base}:{path}"],
                   capture_output=True, text=True, check=True).stdout, f"{name} (origin/main)")
    if not wt > bm:
        ok = False
    print(f"  {'OK  ' if wt > bm else 'FAIL'} {name}: working tree {wt_s} vs origin/main {bm_s}")
if not ok:
    raise SystemExit("FAIL: a touched plugin is not bumped ahead of origin/main -- fix Task 1 Steps 6-7")
print("OK: both plugins bumped ahead of origin/main in the working tree")
PY
```
Expected: two `OK  …` lines, then `OK: both plugins bumped ahead of origin/main in the working tree` (exit 0). A `FAIL` line + non-zero exit means a bump is missing or `origin/main` advanced onto your number — return to Task 1 Steps 6-7 and bump the minor segment past what it now publishes.

Then run the exact command PR CI runs, as a parity dry-run:
```bash
python3 scripts/check-version-bump.py origin/main; echo "exit=$?"
```
Expected locally: `check-version-bump: no plugin directory touched ... OK` and `exit=0`. This confirms the CI script runs clean but — per the note above — does **not** re-prove the bump here; the working-tree check above is what proves it. PR CI re-runs this same command against the committed tree after the adversarial-review stage commits the work, where it becomes the authoritative gate.

- [ ] **Step 4: `claude plugin validate .` passes (criterion #6)**

Run:
```bash
claude plugin validate .
```
Expected: validation passes; exactly the **8 missing-author warnings** are expected and acceptable. Any error (not warning) means STOP and fix.

## Self-Review

- **Spec coverage:** Design's four block replacements → Task 1 Steps 2-5. Version bumps (§Version bumps) → Task 1 Steps 6-7. All seven success criteria → criterion #1 (T1 S8), #2 (T1 S10), #7 (T1 S9), #3 (T2 S1), #4 (T2 S2), #5 (T2 S3), #6 (T2 S4). Mirrored-pair obligation → both files edited in Task 1 + corpus cross-check in Task 2 S1. Out-of-scope items (no `writing-plans` change, no Bookkeeping-bullet change, no retro-ticking, no new tooling) → nothing in the plan touches them. No gaps.
- **Placeholder scan:** every edit step carries the exact old and new line; every verification step carries the exact command and expected output. No TBD/TODO/"similar to".
- **Consistency:** block indices, line numbers (165/191 dev-flow, 159/185 worktree), the `[-*+]` literal, and the `read_blocks(DESIGN, [1,1,1,1])` API match the design and `scripts/design_blocks.py` throughout.
