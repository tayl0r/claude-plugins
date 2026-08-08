---
dev-flow:
  slug: gh-63-fully-checked-row
  spec: docs/superpowers/specs/2026-08-08-gh-63-fully-checked-row-design.md
---

# gh-63 "Plan fully checked" Row (anchored-predicate reword) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reword the "Plan fully checked" resume row in both hand-mirrored pipeline `SKILL.md` files so it names the anchored count predicate (`^[[:space:]]*[-*+] \[ \]`) as the exact negation of the Execute row's predicate directly above it, amend the gh-58 design doc's over-strong "no other site" claim, and bump both plugin versions.

**Architecture:** Two whole-line replacements (one row per `SKILL.md`, byte-identical across the hand-mirrored pair) plus one sentence amendment in the gh-58 design doc and a minor version bump for each plugin. The exact replacement text is fixed by the design as two fenced blocks (shape `[1, 1]`) and is re-read from the design on disk during verification, never retyped. No behavior change; the reword makes the "≥1 unchecked box" / "fully checked" partition explicit in the prose rather than construction-held.

**Tech Stack:** Markdown `SKILL.md` files; `plugin.json` manifests; verification via `git grep`, `git show`, `python3 scripts/design_blocks.py` / `read_blocks`, `python3 scripts/verify_blob.py` / `blob`/`to_lines`/`reconstructed`, `python3 scripts/check-sync.py`, `python3 scripts/check-version-bump.py`, `claude plugin validate .`. No automated test suite exists in this repo.

## About this run (meta note)

This plan's own task checkboxes live in `docs/superpowers/plans/`, outside the `plugins/` scope of every grep this plan runs, so ticking them never affects the verification counts. The design's criterion #4 counts `^[[:space:]]*[-*+] \[ \]` lines in `plugins/` only. The plan's fenced edit blocks quote table rows and prose bullets — none starts with `- [ ]` — so the plan file contributes no stray tokens either.

## Global Constraints

- **No automated test suite.** "Tests" are: the removed-phrase grep (criterion #1), the design-block re-read + issue-text tie (criterion #2), the byte-for-byte blob check (criterion #3), the shipped-literal pin `git grep -F -- '^[[:space:]]*[-*+] \[ \]' -- plugins/` (criterion #4), `python3 scripts/check-sync.py` (#5), `python3 scripts/check-version-bump.py origin/main` (#6), and `claude plugin validate .` (#7, 8 missing-author warnings expected).
- **Design is authoritative.** `docs/superpowers/specs/2026-08-08-gh-63-fully-checked-row-design.md`; block shape `[1, 1]`. Any plan-vs-design conflict resolves to the design.
- **Byte-identical literal.** The regex literal `^[[:space:]]*[-*+] \[ \]` must land character-for-character identical at all three per-file sites — criterion #4 depends on it.
- **Mirrored pair, hand-mirrored.** The pipeline `SKILL.md` pair (`plugins/dev-flow/skills/dev-flow/SKILL.md` and `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`) is **not** in `scripts/check-sync.py`'s `MIRROR_PAIRS`. Both files must be edited with the identical string, and the change cross-verified against something **outside** the pair — here the design-conformance check (one block asserted verbatim in *both* files) and the issue-text tie (criterion #2).
- **Version bump on behavior change.** Bump the **minor** segment of each touched plugin's `version`, ahead of `origin/main`'s tip (not merely past this branch's base). Re-check `origin/main` at execute time.
- **Command discipline.** Every git ref a step computes is captured to a variable, validated non-empty, and quoted (or passed as an `argv` element) — never an unguarded inline substitution. `base=$(git merge-base origin/main HEAD)`, halt if empty.
- **Verification ordering.** A verification step that reads committed `HEAD` (criterion #6's `check-version-bump`, criterion #3's merge-base) runs after the task's commit.

---

## Task 1: Reword the "Plan fully checked" resume row in both mirrored `SKILL.md` files and bump both plugin versions

Applies the Block [0] whole-line replacement to both files (the mirror obligation means the two files move together) and both version bumps as one reviewable unit, then proves locally that exactly the intended lines changed and the mechanical gates stay green.

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md` (line 196 = the "Plan fully checked" resume row)
- Modify: `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` (line 190 = the same row)
- Modify: `plugins/dev-flow/.claude-plugin/plugin.json` (`version` field)
- Modify: `plugins/dev-flow-worktree/.claude-plugin/plugin.json` (`version` field)
- Read (verification source, never edited): `docs/superpowers/specs/2026-08-08-gh-63-fully-checked-row-design.md`, `scripts/design_blocks.py`

**Interfaces:**
- Consumes: the design's two fenced blocks, shape `[1, 1]`, read verbatim from the design doc at `docs/superpowers/specs/2026-08-08-gh-63-fully-checked-row-design.md` via `read_blocks(DESIGN, [1, 1])` (`sys.path.insert(0, "scripts")`; `read_blocks` from `scripts/design_blocks.py`). `b[0][0]` is the new "Plan fully checked" row (inlined in Steps 2-3); `b[1][0]` is the amended gh-58 line, consumed by Task 2. Never reconstruct or substitute either block; if you cannot read the design doc, stop and report.
- Produces: two edited `SKILL.md` files whose lines 196 (dev-flow) and 190 (worktree) equal Block [0]; two bumped `plugin.json` versions. Task 3 consumes these for the verification pass.

- [x] **Step 1: Confirm the design block shape before touching anything**

Run:
```bash
python3 scripts/design_blocks.py docs/superpowers/specs/2026-08-08-gh-63-fully-checked-row-design.md
```
Expected: first line reads `shape: [1, 1]`, with `[0]` starting `| Plan fully checked —` and `[1]` starting `- **The two target sites, per file.**`. If the shape is anything other than `[1, 1]`, STOP — the design's blocks moved and every edit below is misrouted.

- [x] **Step 2: Replace `plugins/dev-flow/skills/dev-flow/SKILL.md` line 196 (the "Plan fully checked" resume row) with Block [0]**

Old line (`old_string`, currently line 196):
```text
| Plan fully checked; no PR for the branch (`--state all` list empty) | PR: create + review |
```
Replace with Block [0] (`new_string`):
```text
| Plan fully checked — no unchecked task box (no line matching `^[[:space:]]*[-*+] \[ \]`); no PR for the branch (`--state all` list empty) | PR: create + review |
```
The new line must be byte-identical to the design's Block [0] (one em dash U+2014 after "checked"; the only asterisks are inside the regex code span). Task 3's design-conformance check re-reads the block from the design and asserts it landed verbatim, so a transcription error here is caught — but do not introduce one.

- [x] **Step 3: Replace `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` line 190 (the same row) with Block [0]**

Block [0] is byte-identical to the dev-flow replacement. Old line (`old_string`, currently line 190):
```text
| Plan fully checked; no PR for the branch (`--state all` list empty) | PR: create + review |
```
Replace with Block [0] (`new_string`):
```text
| Plan fully checked — no unchecked task box (no line matching `^[[:space:]]*[-*+] \[ \]`); no PR for the branch (`--state all` list empty) | PR: create + review |
```

- [x] **Step 4: Bump `plugins/dev-flow/.claude-plugin/plugin.json` version to `2.20.0` (re-checked against `origin/main`)**

First read what `origin/main` publishes and what the working tree currently declares, then bump past `origin/main`:
```bash
base=$(git rev-parse origin/main); [ -n "$base" ] || { echo "empty base"; exit 1; }
git show "$base:plugins/dev-flow/.claude-plugin/plugin.json" | python3 -c "import json,sys; print(json.load(sys.stdin)['version'])"
python3 -c "import json; print(json.load(open('plugins/dev-flow/.claude-plugin/plugin.json'))['version'])"
```
The first line is `origin/main`'s version; the second is the working tree's current version — the edit's `old_string`. If the first prints `2.19.0`, edit the manifest's `version` field from the working tree's current version to `2.20.0` (bump the minor segment). If `origin/main` has advanced past `2.19.0`, bump the minor segment past whatever it now publishes instead (e.g. if it prints `2.20.0`, use `2.21.0`). Edit only the `version` value; leave the rest of the manifest untouched.

- [x] **Step 5: Bump `plugins/dev-flow-worktree/.claude-plugin/plugin.json` version to `1.22.0` (re-checked against `origin/main`)**

Same procedure:
```bash
base=$(git rev-parse origin/main); [ -n "$base" ] || { echo "empty base"; exit 1; }
git show "$base:plugins/dev-flow-worktree/.claude-plugin/plugin.json" | python3 -c "import json,sys; print(json.load(sys.stdin)['version'])"
python3 -c "import json; print(json.load(open('plugins/dev-flow-worktree/.claude-plugin/plugin.json'))['version'])"
```
The first line is `origin/main`'s version; the second is the working tree's current version — the edit's `old_string`. If the first prints `1.21.0`, edit the `version` field from the working tree's current version to `1.22.0`. If `origin/main` has advanced, bump the minor segment past whatever it now publishes.

- [x] **Step 6: Verify the removed phrasing is gone (criterion #1)**

Run — must return **no** output (exit status 1 from grep is expected on no match):
```bash
git grep -F -- 'fully checked;' -- plugins/
```
Expected: no line printed. (At the merge-base this returned exactly the two rows — `dev-flow:196` and `worktree:190`.)

- [x] **Step 7: Verify the shipped anchored literal is present at all three per-file sites (criterion #4)**

Run:
```bash
git grep -F -- '^[[:space:]]*[-*+] \[ \]' -- plugins/
```
Expected: **six** matching lines — three per file (the Execution-complete signal paragraph, the Execute resume row, and the new fully-checked row). `-F` (fixed-string) is required because the literal is entirely regex metacharacters. This pins the character-for-character string that ships to the one the other two sites carry.

- [x] **Step 8: `check-sync.py` still exits 0 (criterion #5)**

Run:
```bash
python3 scripts/check-sync.py; echo "exit=$?"
```
Expected: `exit=0`. The edit touches no `MIRROR_PAIRS` member and no manifest `description`, and the pipeline pair is outside `MIRROR_PAIRS`, so sync is unaffected.

- [x] **Step 9: Commit**

```bash
git add plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
git commit -F - <<'MSG'
gh-63: name the anchored predicate in the "Plan fully checked" resume row

Reword the resume row in both hand-mirrored pipeline SKILL.md files so it
names the anchored count predicate as the exact negation of the Execute row's,
and bump both plugin versions ahead of origin/main's tip.

Co-Authored-By: Claude <noreply@anthropic.com>
MSG
```

- [x] **Step 10: Verify both plugins are bumped ahead of `origin/main` (criterion #6)**

This reads committed `HEAD`, so it runs after Step 9's commit. Run:
```bash
python3 scripts/check-version-bump.py origin/main; echo "exit=$?"
```
Expected: a leading `check-version-bump: base <sha>, head <sha>, merge-base <sha>` line (9-char shas), then two indented `OK` lines with the plugin name padded to 20 columns — `  dev-flow             2.19.0 -> 2.20.0 ... OK` and `  dev-flow-worktree    1.21.0 -> 1.22.0 ... OK` (the version numbers are whatever Steps 4-5 bumped to) — then `check-version-bump: 2 compared, 0 skipped ... OK` and `exit=0`. A `FAIL` line means a bump is missing or `origin/main` advanced onto your number — return to Steps 4-5, bump the minor segment past what it now publishes, and re-commit.

---

## Task 2: Amend the gh-58 design doc's over-strong "no other site" claim

Replaces line 31 of the gh-58 design doc with Block [1] — the same bullet, with the claim amended in place (prefix-preserving) and the line's file citations refreshed to the current tree.

**Files:**
- Modify: `docs/superpowers/specs/2026-08-03-gh-58-completion-predicate-design.md` (line 31)
- Read (verification source, never edited): `docs/superpowers/specs/2026-08-08-gh-63-fully-checked-row-design.md`, `scripts/design_blocks.py`

**Interfaces:**
- Consumes: Block [1] from the design doc at `docs/superpowers/specs/2026-08-08-gh-63-fully-checked-row-design.md`, read verbatim via `read_blocks(DESIGN, [1, 1])` (`sys.path.insert(0, "scripts")`; `read_blocks` from `scripts/design_blocks.py`). `b[1][0]` is the amended gh-58 line (inlined in Step 1). Never reconstruct or substitute it; if you cannot read the design doc, stop and report.
- Produces: the amended gh-58 design line 31. Task 3 consumes it for the verification pass.

- [ ] **Step 1: Replace `docs/superpowers/specs/2026-08-03-gh-58-completion-predicate-design.md` line 31 with Block [1]**

Old line (`old_string`, currently line 31 — the bullet beginning `- **The two target sites, per file.**`):
```text
- **The two target sites, per file.** `git grep -nE 'Execution is complete|≥1 unchecked' -- plugins/` returned exactly two lines in each file: the **Execution-complete signal** paragraph and the resume-table row. `plugins/dev-flow/skills/dev-flow/SKILL.md:165` / `:191`; `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md:159` / `:185`. No other site in either file references the count predicate. The Stage 3 **Bookkeeping** bullet (`:231` / `:225`) mentions *ticking* (the action) but no count, so it is untouched.
```
Replace with Block [1] (`new_string`):
```text
- **The two target sites, per file.** `git grep -nE 'Execution is complete|≥1 unchecked' -- plugins/` returned exactly two lines in each file: the **Execution-complete signal** paragraph and the resume-table row. `plugins/dev-flow/skills/dev-flow/SKILL.md:169` / `:195`; `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md:163` / `:189`. No other site in either file references the count predicate — a claim corrected by gh-63: the sibling "Plan fully checked" resume row directly below the anchored Execute row also expresses the count predicate, in different words that the phrase-grep `Execution is complete|≥1 unchecked` structurally cannot match, so this claim was a measurement blind spot, now fixed. The Stage 3 **Bookkeeping** bullet (`:239` / `:233`) mentions *ticking* (the action) but no count, so it is untouched.
```
The new line must be byte-identical to the design's Block [1]. Task 3's design-conformance check re-reads the block from the design and asserts it landed verbatim.

- [ ] **Step 2: Verify the amendment landed**

Run:
```bash
git grep -F -- 'a claim corrected by gh-63' -- docs/superpowers/specs/2026-08-03-gh-58-completion-predicate-design.md
```
Expected: exactly one line — the amended line 31. And the old claim's sentence-ending period is gone from that line:
```bash
git grep -F -- 'references the count predicate. The Stage 3' -- docs/superpowers/specs/2026-08-03-gh-58-completion-predicate-design.md
```
Expected: no output (the old period is replaced by the em-dash amendment).

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/specs/2026-08-03-gh-58-completion-predicate-design.md
git commit -F - <<'MSG'
gh-63: amend the gh-58 design's over-strong "no other site" claim

The gh-58 design claimed no other site in either file references the count
predicate; the sibling "Plan fully checked" resume row expresses it in words
the phrase-grep cannot match. Amend the claim in place, prefix-preserving,
and refresh the line's file citations to the current tree.

Co-Authored-By: Claude <noreply@anthropic.com>
MSG
```

---

## Task 3: Whole-change verification pass (design-conformance re-read, byte-for-byte blob check, marketplace validate)

Proves the design's remaining success criteria against the committed edits from Tasks 1 and 2. Verification only — no files are modified.

**Files:** none modified — verification only. Reads `docs/superpowers/specs/2026-08-08-gh-63-fully-checked-row-design.md`, the five edited files, `scripts/design_blocks.py`, `scripts/verify_blob.py`, and the whole marketplace via `claude plugin validate .`.

**Interfaces:**
- Consumes: Task 1's and Task 2's committed edits (the working tree).
- Produces: evidence that all seven design success criteria hold. No artifacts.

- [ ] **Step 1: Design-conformance check (criterion #2) — re-read the design's blocks, never retyped**

First confirm the shape:
```bash
python3 scripts/design_blocks.py docs/superpowers/specs/2026-08-08-gh-63-fully-checked-row-design.md
```
Expected: `shape: [1, 1]`.

Then run this inline — a `python3 - <<'PY'` heredoc, so nothing is written into the repo. It re-reads the two blocks from the design on disk (never retyped), asserts Block [0] appears verbatim in both `SKILL.md` files (one block → byte-identical across the pair), asserts Block [1] appears verbatim in the gh-58 design doc, and asserts Block [0] equals, modulo leading whitespace on both sides, the issue's suggested row inside the design's `## Original problem` fenced block (the unique line there whose stripped form begins `| Plan fully checked —`). The issue-text tie closes the single-mistype case: a prose typo in the block can no longer propagate identically to both files and pass every criterion.

```bash
python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-08-gh-63-fully-checked-row-design.md"
b = read_blocks(DESIGN, [1, 1])          # exits non-zero if the shape moved
b0, b1 = b[0][0], b[1][0]

DF = "plugins/dev-flow/skills/dev-flow/SKILL.md"
WT = "plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md"
G58 = "docs/superpowers/specs/2026-08-03-gh-58-completion-predicate-design.md"

for path in (DF, WT):
    text = Path(path).read_text(encoding="utf-8")
    assert b0 in text, f"{path}: Block [0] not found verbatim"
    print(f"OK {path}: Block [0] present verbatim")

g58 = Path(G58).read_text(encoding="utf-8")
assert b1 in g58, f"{G58}: Block [1] not found verbatim"
print(f"OK {G58}: Block [1] present verbatim")

# Issue-text tie: Block [0] equals, modulo leading whitespace on both sides,
# the issue's suggested row inside the design's `## Original problem` fenced
# block -- the unique line there whose stripped form begins `| Plan fully checked —`.
lines = Path(DESIGN).read_text(encoding="utf-8").split("\n")
start = next(i for i, ln in enumerate(lines) if ln.strip() == "## Original problem")
fence = next(i for i in range(start + 1, len(lines)) if lines[i].strip().startswith("```"))
issue_block = []
for ln in lines[fence + 1:]:
    if ln.strip() == "```":
        break
    issue_block.append(ln)
cands = [ln for ln in issue_block if ln.lstrip().startswith("| Plan fully checked —")]
assert len(cands) == 1, f"issue block: expected exactly 1 '| Plan fully checked —' line, got {len(cands)}"
assert b0.lstrip() == cands[0].lstrip(), "Block [0] does not match the issue's suggested row (modulo leading whitespace)"
print("OK: Block [0] matches the issue's suggested row (modulo leading whitespace)")
print("PASS: design-conformance check")
PY
```
Expected: two `OK …: Block [0] present verbatim` lines, one `OK …: Block [1] present verbatim`, the issue-tie `OK`, then `PASS: design-conformance check` (exit 0). Any `AssertionError` or non-zero exit means STOP and fix before proceeding.

- [ ] **Step 2: Byte-for-byte blob check (criterion #3) — every touched file is its merge-base blob with exactly the intended edit**

Run this inline. It captures `base=$(git merge-base origin/main HEAD)` (validated non-empty), then for each of the five touched files reconstructs the expected working-tree bytes from the base blob with exactly the intended edit and asserts the working tree matches byte-for-byte via `verify_blob`'s `blob`/`to_lines`/`reconstructed`. The design doc itself is a newly created file, so its own base is empty and it is not checked here.

```bash
python3 - <<'PY'
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
from verify_blob import blob, to_lines, reconstructed

DESIGN = "docs/superpowers/specs/2026-08-08-gh-63-fully-checked-row-design.md"
b = read_blocks(DESIGN, [1, 1])
b0, b1 = b[0][0], b[1][0]

base = subprocess.run(["git", "merge-base", "origin/main", "HEAD"],
                      capture_output=True, text=True, check=True).stdout.strip()
assert base, "empty merge-base"

def check_line_replaced(path, anchor, new_line):
    base_bytes = blob(base, path)
    old = to_lines(base_bytes)
    hits = [i for i, ln in enumerate(old) if anchor in ln]
    assert len(hits) == 1, f"{path}: base anchor {anchor!r} matched {len(hits)} lines, want 1"
    idx = hits[0]
    new = old[:idx] + [new_line] + old[idx + 1:]
    bad = reconstructed(path, new, base_bytes)
    assert not bad, f"{path}: " + "; ".join(bad)
    print(f"OK {path}: base line {idx + 1} replaced by its design block")

check_line_replaced("plugins/dev-flow/skills/dev-flow/SKILL.md", "| Plan fully checked;", b0)
check_line_replaced("plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md", "| Plan fully checked;", b0)
check_line_replaced("docs/superpowers/specs/2026-08-03-gh-58-completion-predicate-design.md",
                    "No other site in either file references the count predicate", b1)

def check_version(path):
    base_bytes = blob(base, path)
    old = to_lines(base_bytes)
    wt = Path(path).read_text(encoding="utf-8")
    new_version = json.loads(wt)["version"]
    hits = [i for i, ln in enumerate(old) if '"version"' in ln]
    assert len(hits) == 1, f"{path}: base has {len(hits)} version lines, want 1"
    idx = hits[0]
    new = old[:idx] + [f'  "version": "{new_version}",'] + old[idx + 1:]
    bad = reconstructed(path, new, base_bytes)
    assert not bad, f"{path}: " + "; ".join(bad)
    print(f"OK {path}: version line replaced (now {new_version})")

check_version("plugins/dev-flow/.claude-plugin/plugin.json")
check_version("plugins/dev-flow-worktree/.claude-plugin/plugin.json")
print("PASS: all five touched files are byte-for-byte their merge-base blob with exactly the intended edit")
PY
```
Expected: three `OK …: base line N replaced by its design block` lines, two `OK …: version line replaced (now …)` lines, then `PASS: all five touched files are byte-for-byte their merge-base blob with exactly the intended edit` (exit 0). Any `AssertionError` or non-zero exit means STOP and fix.

- [ ] **Step 3: `claude plugin validate .` passes (criterion #7)**

Run:
```bash
claude plugin validate .
```
Expected: validation passes; exactly the **8 missing-author warnings** are expected and acceptable. Any error (not warning) means STOP and fix.

## Self-Review

- **Spec coverage:** Design's two block replacements → Task 1 Steps 2-3 (Block [0] in both files), Task 2 Step 1 (Block [1]). Version bumps (§Version bumps) → Task 1 Steps 4-5. All seven success criteria → criterion #1 (T1 S6), #4 (T1 S7), #5 (T1 S8), #6 (T1 S10), #2 (T3 S1), #3 (T3 S2), #7 (T3 S3). Mirrored-pair obligation → both files edited with the identical string in Task 1 + design-conformance cross-check in Task 3 S1. Out-of-scope items (no change to the anchored Execute row, the Execution-complete paragraph, the Bookkeeping bullet, or any other prose; no `writing-plans` change; no retroactive edit of other dated specs) → nothing in the plan touches them. No gaps.
- **Placeholder scan:** every edit step carries the exact old and new line; every verification step carries the exact command and expected output. No TBD/TODO/"similar to".
- **Consistency:** block indices, line numbers (196 dev-flow / 190 worktree / 31 gh-58), the `[-*+]` literal, the `read_blocks(DESIGN, [1, 1])` API, and the `verify_blob` API (`blob`/`to_lines`/`reconstructed`) match the design and the scripts throughout.
