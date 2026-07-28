---
dev-flow:
  slug: gh-7-review-depth
  spec: docs/superpowers/specs/2026-07-27-gh-7-review-depth-design.md
---

# gh-7: two depth gaps in `adversarial-review`'s seed passes — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a trigger-gated **input-contract completeness** pass to the design/plan correctness seed and a trigger-gated **seam-placement** angle to the diff quality seed of `adversarial-review`, wire the version bumps that make the change reach a user, correct `CLAUDE.md`'s verification-policy bullet to the rule this change proves is right, and land the `CONTEXT.md` glossary entries the new vocabulary makes true.

**Architecture:** Pure prose-and-manifest change across six files, no code. Two of the files are a `check-sync.py`-enforced **mirror pair** (`adversarial-review/SKILL.md` × 2): three in-place line replacements plus two symmetric two-line insertions, landing byte-identically in both copies, taking both from 81 to 85 lines. `CONTEXT.md` gains the glossary entries this change makes true and — per the design's Scope check — **must land in the same commit as the SKILL.md pair, not merely the same PR**, so those three files are one task with one commit. Two `plugin.json` version bumps are load-bearing (the install cache is version-keyed) and follow once the behavior they gate is in place. `CLAUDE.md` gets one line replaced — not appended — restating a verification rule at its actual root cause.

**Tech Stack:** Markdown, JSON manifests, `python3 scripts/check-sync.py`, `claude plugin validate .`, `git grep`. No build, no test framework, no linter.

**Authoritative source:** `docs/superpowers/specs/2026-07-27-gh-7-review-depth-design.md`. Every replacement/insertion text below is copied verbatim from its `§Exact change list`. **If this plan and the design ever disagree, the design wins** — stop and re-read `§Exact change list` before improvising.

---

## Global Constraints

Every task's requirements implicitly include this section.

- **Repo root:** `/Users/taylor/dev/claude-plugins`. Every path below is relative to it. Work in place on the existing branch `tayl0r/gh-7-review-depth` — **do not create a git worktree, do not switch branches, do not push, do not open a PR, do not merge.**
- **There is no test framework, no build, no linter in this repo.** Do not run `pytest`, `npm test`, `ruff`, or invent one. Every verification step here is an exit code plus stdout from `python3 scripts/check-sync.py`, `claude plugin validate .`, `git grep`, `wc -l`, `git diff --numstat`, or the inline `python3 - <<'PY'` design-conformance checks given verbatim below.
- **`claude plugin validate .` emits 8 missing-author warnings. That is expected and is NOT a failure.** Only a non-zero exit or an explicit error is a failure.
- **Scope is exactly six files:** `plugins/dev-flow/skills/adversarial-review/SKILL.md`, `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md`, `plugins/dev-flow/.claude-plugin/plugin.json`, `plugins/dev-flow-worktree/.claude-plugin/plugin.json`, `CLAUDE.md`, `CONTEXT.md`. Nothing else may appear in the final diff. Do not touch `.claude-plugin/marketplace.json`, `scripts/check-sync.py`, `.github/workflows/`, `docs/agents/*.md`, either `README.md`, `plugins/better-code-review/`, or the design doc itself (`docs/superpowers/specs/2026-07-27-gh-7-review-depth-design.md` is read-only reference material — never edit it).
- **CONTEXT.md must land in the same COMMIT as the `adversarial-review/SKILL.md` pair, not merely the same PR** (design §Scope check, "Does every file belong in the same change?"). Landing the glossary early or late is actively harmful either way (`docs/agents/domain.md` has every skill read the glossary first). This is why Task 1 below bundles all three files into one commit, and why this plan does **not** use a commit-per-task rhythm the way some other plans in this repo do. **Do not commit after only some of Task 1's files are edited.**
- **Anchor every edit on distinctive text, not raw line numbers.** The line numbers quoted below are from the pre-change files (confirmed current as of this plan) and are given only to help you find the edit; locate every target with the `git grep -n` command each step supplies, then replace the line (or insert after it) using that exact text as `old_string`. The design's three in-place replacements do not shift the two insertion points — do the replacements and insertions in any order.
- **Copy replacement/insertion text verbatim, character for character**, including em dashes (`—`), curly quotes, and backticks. The line counts, `check-sync.py`, and the greps test shape and absence only — the same word mangled **identically in both mirror copies** passes every one of them. What catches that is each task's design-conformance script, which re-reads the expected text from the design file on disk and requires a byte-for-byte match. Copy those scripts exactly; they are deliberately pure ASCII, so a mistyped copy fails loudly instead of passing.
- **The shell hook rewrites bare `grep`/`find`/`diff` and can elide path components in their output.** Where exact per-file output matters (the version spot-check), prefix with `rtk proxy` (e.g. `rtk proxy grep -n ...`). `git grep`, `git diff --numstat`, `wc -l`, and `python3` are unaffected — run those as written.
- **`-F` in every grep below is deliberate.** The patterns contain `(`, `)`, `|`, and `*` — a fixed-string match avoids regex interpretation, exactly as the design specifies.
- **`git diff --numstat` is asserted only where the edit replaces a *single* line** — the two `plugin.json` bumps and `CLAUDE.md` line 9, where `1  1` is what a one-line replacement means by definition. **Never assert numstat counts for a multi-line region replacement.** `--numstat` reports git's minimal edit script over the final content, not "N lines in, M lines out": lines recurring verbatim in both the old and new text are matched as unchanged context, so the counts do not equal the region sizes. `wc -l` plus the design-conformance script are what verify a region replacement.

---

## File map

| File | Responsibility in this change | Task |
|---|---|---|
| `plugins/dev-flow/skills/adversarial-review/SKILL.md` | Mirror-pair copy A. Three in-place replacements (lines 28, 29, 34) plus two two-line insertions (after 38, after 40). 81 → **85 lines**. | 1 |
| `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md` | Mirror-pair copy B. The identical five edits — no `dev-flow`/`dev-flow-worktree` token appears in any of the new text. 81 → **85 lines**. | 1 |
| `CONTEXT.md` | Glossary region `**Angle**:` … `**Pass**:` replaced and extended with `**Trigger**:` and `**Reportability rule**:`. 61 → **67 lines**. Must land in the same commit as the two files above. | 1 |
| `plugins/dev-flow/.claude-plugin/plugin.json` | `"version": "2.3.0"` → `"2.4.0"`. Load-bearing: the install cache is version-keyed. | 2 |
| `plugins/dev-flow-worktree/.claude-plugin/plugin.json` | `"version": "1.5.0"` → `"1.6.0"`. Same. | 2 |
| `CLAUDE.md` | Line 9 (the hand-mirroring bullet) **replaced**, not appended, with the root-cause verification rule. Stays at **29 lines**. | 3 |

No file is created, renamed, or deleted.

---

## Task ordering and why

**Task 1 is one task across three files, not three tasks, because the design forbids splitting it.** The two `adversarial-review/SKILL.md` copies are a `check-sync.py`-enforced mirror pair — a one-sided edit is CI-red — and `CONTEXT.md`'s glossary entries must land in the *same commit* as that pair, not merely the same PR (design §Scope check). A task boundary that let CONTEXT.md land separately would violate that requirement by construction, so all three files, and their single commit, are one task.

**Task 2 (version bumps) follows Task 1.** Not a file dependency — disjoint files — but the design's own reasoning: "a bump without the edit means nothing; the edit without a bump never reaches a user" (design §Scope check). Bumping first would ship a version claiming behavior not yet present.

**Task 3 (`CLAUDE.md`) has no content dependency on Tasks 1–2** and edits a fourth, disjoint file. It is sequenced last among the edit tasks only for narrative order, matching the design's `§Exact change list` numbering (5 comes after 3 & 4). It is safe to do first if that's more convenient.

**Task 4 re-runs the design's full six-step §Verification section plus a scope check**, and depends on Tasks 1–3 all being complete and committed — several of its checks (the version grep, the full residue/presence greps, the complete design-conformance script) are only meaningful once every file has landed.

---

### Task 1: Edit the `adversarial-review` mirror pair and `CONTEXT.md`'s glossary — one commit

**Files:**
- Modify: `plugins/dev-flow/skills/adversarial-review/SKILL.md` (lines 28, 29, 34, insert after 38, insert after 40)
- Modify: `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md` (same five edits)
- Modify: `CONTEXT.md` (the six-line region from `**Angle**:` through the blank line before `**Design rubric**:`, currently lines 29–34)
- Test: none — this repo has no test framework. Verification is `check-sync.py`, `wc -l`, scoped residue/presence greps, and a design-conformance script.

**Depends on:** nothing. This is the first task.

**Read `§1 & 2` and `§6` of the design before starting.** The two `SKILL.md` files are a declared `check-sync.py` mirror pair: line-for-line identical after substituting `dev-flow-worktree` → `dev-flow`, except one declared exception at line 12 (the `working-dir` bullet), which is above every edit here and untouched.

- [x] **Step 1: Confirm the starting state**

```bash
cd /Users/taylor/dev/claude-plugins
python3 scripts/check-sync.py
wc -l plugins/dev-flow/skills/adversarial-review/SKILL.md plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md CONTEXT.md
```

Expected: `check-sync: all checks passed` with `mirror pair "adversarial-review" ... OK (81 lines, 1 declared exception)`; `81`, `81`, and `61` for the three files respectively. If any of that differs, stop — the tree is not the state this plan was written against.

- [x] **Step 2: Edit A — Seed passes table, `diff` row (line 28 in both `SKILL.md` files)**

Locate:

```bash
cd /Users/taylor/dev/claude-plugins
git grep -nF 'four angles, inlined (below)' -- 'plugins/*/skills/adversarial-review/SKILL.md'
```

Expected: one hit per file, at line 28. Replace that entire line, **identically in both files**, with:

```
| **diff** | `/simplify`'s four angles plus this skill's seam-placement angle, inlined (below), findings-only, run against `BASE..HEAD`. | The superpowers `code-reviewer.md` template, used as designed (already read-only/findings-only) — see "Pinned template," below. |
```

Only the quality (second) cell changes; the correctness (third) cell is untouched.

- [x] **Step 3: Edit B — Seed passes table, `design` row (line 29 in both `SKILL.md` files)**

Locate:

```bash
cd /Users/taylor/dev/claude-plugins
git grep -nF 'untestable success criteria. |' -- 'plugins/*/skills/adversarial-review/SKILL.md'
```

Expected: one hit per file, at line 29. Replace that entire line, **identically in both files**, with:

```
| **design** | The design rubric (below) *is* the lens, applied adversarially to the proposed approach. | A prose-integrity checklist: placeholders/TBDs, internal contradictions, planning-blocking ambiguity, unstated assumptions, missing or untestable success criteria — plus the input-contract completeness pass (below). |
```

Only the correctness (third) cell changes. **Do not touch the `plan` row (line 30)** — its "The prose checklist above" reference already carries this addition, per the design.

- [x] **Step 4: Edit C — the angles-block header (line 34 in both `SKILL.md` files)**

Locate:

```bash
cd /Users/taylor/dev/claude-plugins
git grep -nF '(verbatim):**' -- 'plugins/*/skills/adversarial-review/SKILL.md'
```

Expected: one hit per file, at line 34. Replace that entire line, **identically in both files**, with:

```
**The four `/simplify` angles (verbatim), then a fifth of this skill's own — all five apply:**
```

Do not touch line 32 or the four bullets themselves (lines 35–38) — the verbatim-transcription claim binds their content, not this header.

- [x] **Step 5: Edit D — insert the fifth angle after the `Altitude` bullet (currently line 38 in both `SKILL.md` files)**

Locate:

```bash
cd /Users/taylor/dev/claude-plugins
git grep -nF -- '- **Altitude:**' 'plugins/*/skills/adversarial-review/SKILL.md'
```

Expected: one hit per file, at line 38, reading:

```
- **Altitude:** is the change at the right level of abstraction — not hand-rolling what a higher-level seam already handles, not over-abstracting a one-off? Put the logic at the right layer.
```

Leave that line itself unchanged. Immediately **after** it, insert exactly two new lines — one empty line, then this line — **identically in both files**:

```

**Seam placement:** applies only where the diff adds a construct that cannot be defined without naming another construct plus a qualifier: a near-copy of an existing type with fields loosened, a `raw`/`validated` variant of one concept, a converter between two shapes of one concept, a flag telling a callee which state its input is in, a newly required call ordering. Each spans a transformation, so "is it necessary as things stand?" is the wrong question — the answer is nearly always yes. Ask instead where the diff performs that transformation, and whether performing it at one *specific* other place deletes the construct outright. Then apply the deletion test to what you propose deleting: if the construct is what keeps a wire, stored, or versioned contract decoupled from the domain type, that reason survives the transformation moving and there is no finding. There is also no finding when the diff already performs the transformation at the place you would move it to — there is nowhere to move it. Report only when you can name the place, the deletion, and that nothing reappears in the construct's stead — this angle proposes removals, never a restructuring whose payoff is a nicer structure.
```

- [x] **Step 6: Edit E — insert the input-contract pass after the `Pinned template` paragraph (currently line 40 in both `SKILL.md` files)**

Locate:

```bash
cd /Users/taylor/dev/claude-plugins
git grep -nF '**Pinned template' -- 'plugins/*/skills/adversarial-review/SKILL.md'
```

Expected: one hit per file, at line 40 — or at line 42 in **both** copies if Step 5 has already landed, since Step 5 inserts two lines above this anchor identically in both. The phrase is what matters, not the number. Leave that paragraph itself unchanged. Immediately **after** it, insert exactly two new lines — one empty line, then this line — **identically in both files**:

```

**Input-contract completeness — the design *and* plan correctness seed:** applies only to fields the artifact newly accepts from outside the code it describes (an operator, an API client, a file, an upstream service). For each, report the gap between what its declared type permits and what the artifact says the domain allows — empty string, negative, fractional, out of range, `NaN`, duplicate within a collection, absent optional — and what each downstream consumer the artifact names does with a degenerate value. A blanket "validate minimally" or "the type is enough" is the claim this pass tests, per field, never an exemption from it. Findings only: which gaps are worth guarding is the resolvers' call.
```

- [x] **Step 7: Verify — both `SKILL.md` copies are 85 lines and the mirror check passes**

```bash
cd /Users/taylor/dev/claude-plugins
wc -l plugins/dev-flow/skills/adversarial-review/SKILL.md plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
python3 scripts/check-sync.py
```

Expected: `85` for each file, and:

```
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... OK (85 lines, 1 declared exception)
check-sync: all checks passed
```

Exit 0. **`85 lines, 1 declared exception` is load-bearing** — a different count is the assertion that an insertion was asymmetric, or a replacement added/removed a line. An undeclared-divergence failure naming a line means that edit landed on one side only — go apply it to the other.

- [x] **Step 8: Edit F — replace `CONTEXT.md`'s `Angle`/`Pass` region (currently lines 29–34)**

Locate:

```bash
cd /Users/taylor/dev/claude-plugins
git grep -nF '**Angle**:' -- CONTEXT.md
```

Expected: one hit, at line 29. The six-line region to replace begins there and ends at the blank line immediately before `**Design rubric**:` (line 35). Read the file to confirm the exact six lines are:

```
**Angle**:
One lens in the diff-mode quality seed's list: reuse, simplification, efficiency, altitude.

**Pass**:
A named check a seed runs over an artifact. An angle is one lens *within* a seed's list; a pass is a whole check.

```

Replace those six lines with this twelve-line block:

```
**Angle**:
One lens in the diff-mode quality seed's list: reuse, simplification, efficiency, altitude, seam placement.

**Pass**:
A named, self-contained check a seed runs over an artifact, carrying its own trigger and stopping conditions. An angle is a lens *within* a seed's list; a pass is a whole check.

**Trigger**:
The precondition deciding whether a pass or angle applies to a given artifact at all. A check without one runs on everything and manufactures false positives.

**Reportability rule**:
The bar a candidate finding must clear before a seed may state it. Where a trigger narrows *which artifacts get asked*, a reportability rule narrows *what may be said*.

```

Do not touch anything above `**Angle**:` or at/after `**Design rubric**:`.

- [x] **Step 9: Verify — `CONTEXT.md` is 67 lines**

```bash
cd /Users/taylor/dev/claude-plugins
wc -l CONTEXT.md
```

Expected: `67` — 61 pre-change, minus the 6-line region, plus the 12-line block. A different count is the whole signal: `73` means the block was appended instead of replacing the region, `55` means the region was removed without its replacement. Deliberately **no `git diff --numstat` assertion here** — `--numstat` reports git's minimal edit script over the final content, not the region swap, and because `**Angle**:`, `**Pass**:` and the blank lines recur verbatim in both the old and the new text, git matches them as unchanged context: a correctly-applied edit reports `8  2`, never `12  6`. What proves the replacement landed exactly is Step 10 (the old `Pass` sentence is absent) and Step 12 (the 12-line block matches the design byte-for-byte, exactly once).

- [x] **Step 10: Verify — scoped residue grep (old text is gone from the three files this task touches)**

```bash
cd /Users/taylor/dev/claude-plugins
git grep -nF -e 'four angles, inlined (below)' -e 'untestable success criteria. |' -e '(verbatim):**' -e 'A named check a seed runs over an artifact' -- plugins/dev-flow/skills/adversarial-review/SKILL.md plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md CONTEXT.md
echo "exit=$?"
```

Expected: **no output**, `exit=1`. This is a scoped preview of the design's full §Verification step 3 — restricted to the files this task touches, since `CLAUDE.md`'s old phrase (the fifth pattern in the design's full grep) is still present until Task 3. Any hit here means one of Edits A–C or F was not applied, or was applied as an append rather than a replacement.

- [x] **Step 11: Verify — scoped presence grep (new text landed in both copies, and in `CONTEXT.md`)**

```bash
cd /Users/taylor/dev/claude-plugins
git grep -nF -e '**Seam placement:**' -e 'all five apply' -e 'Input-contract completeness' -- plugins/dev-flow/skills/adversarial-review/SKILL.md plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
git grep -nF -e '**Trigger**:' -e '**Reportability rule**:' -e 'seam placement' -- CONTEXT.md
```

Expected: the first command prints **exactly six lines** (each of the three phrases once per `SKILL.md` copy); the second prints **exactly three lines** (once each). Fewer lines means an insertion landed in only one copy, or is missing from `CONTEXT.md`.

- [x] **Step 12: Verify — design-conformance subset (blocks this task owns match the design byte-for-byte, in the right place)**

This is the check that catches what line counts and greps cannot: the same word mangled identically in both mirror copies, or the fifth angle inserted *inside* the four-bullet block instead of after it. It reads the expected text from the design file on disk, never retyped. This is a task-scoped subset of the design's own §Verification step 6 script (it omits the `CLAUDE.md` block, which Task 3 has not landed yet) — Task 4 runs the complete, unmodified script. Copy this exactly; it is deliberately pure ASCII, so a mistyped copy fails loudly instead of passing.

```bash
cd /Users/taylor/dev/claude-plugins
python3 - <<'PY'
import sys
from pathlib import Path
DESIGN = "docs/superpowers/specs/2026-07-27-gh-7-review-depth-design.md"
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
assert [len(b) for b in blocks] == [1, 1, 1, 2, 2, 1, 12], "design code-block shape changed; stop and re-read the design"
PAIR = ["plugins/dev-flow/skills/adversarial-review/SKILL.md",
        "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md"]
SPEC = [("line 28, diff row",     blocks[0], None,                PAIR),
        ("line 29, design row",   blocks[1], None,                PAIR),
        ("line 34, block header", blocks[2], None,                PAIR),
        ("fifth angle",           blocks[3], "- **Altitude:**",    PAIR),
        ("input-contract pass",   blocks[4], "**Pinned template",  PAIR),
        ("CONTEXT.md glossary",   blocks[6], None,                 ["CONTEXT.md"])]
bad = []
for name, want, anchor, targets in SPEC:
    for path in targets:
        L = Path(path).read_text(encoding="utf-8").split("\n")
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

Expected: `design-conformance (task 1 subset): OK`, `exit=0`. A `MISMATCH` line names the block and file to re-paste from the design's `§Exact change list`, then re-run Steps 7–12.

- [x] **Step 13: Verify — exactly these three files are modified, nothing else**

```bash
cd /Users/taylor/dev/claude-plugins
git status --porcelain
```

Expected: exactly `plugins/dev-flow/skills/adversarial-review/SKILL.md`, `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md`, and `CONTEXT.md` shown as modified (plus, possibly, this plan's own checkbox commits if using subagent-driven-development's per-file progress tracking — no other content file).

- [x] **Step 14: Commit — all three files together, in one commit**

```bash
cd /Users/taylor/dev/claude-plugins
git add plugins/dev-flow/skills/adversarial-review/SKILL.md plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md CONTEXT.md
git commit -m "adversarial-review: add seam-placement angle and input-contract completeness pass; glossary catches up"
```

**Do not split this into two commits.** The design requires `CONTEXT.md` to land in the same commit as the `SKILL.md` pair, not merely the same PR.

---

### Task 2: Bump both plugin versions

**Files:**
- Modify: `plugins/dev-flow/.claude-plugin/plugin.json` (line 3)
- Modify: `plugins/dev-flow-worktree/.claude-plugin/plugin.json` (line 3)

**Depends on:** Task 1 committed. Not a file conflict — the design frames it as sequencing, not isolation: "a bump without the edit means nothing; the edit without a bump never reaches a user" (design §Scope check).

**This is not cosmetic cleanup.** The install cache is version-keyed (`~/.claude/plugins/cache/taylor-plugins/<plugin>/<version>/`), so Task 1's edits are never picked up on re-sync until this task lands. Minor bumps per the design's §Assumptions: behavior changes, no interface does (invocation signature, contract, provenance format, and mode set are unchanged).

- [x] **Step 1: Bump `dev-flow` from `2.3.0` to `2.4.0`**

In `plugins/dev-flow/.claude-plugin/plugin.json`, replace:

```
  "version": "2.3.0",
```

with:

```
  "version": "2.4.0",
```

Change **only** the `version` field. Do not touch `description` — it is duplicated into `.claude-plugin/marketplace.json` and `check-sync.py` Check A compares them; that file is out of scope for this change.

- [x] **Step 2: Bump `dev-flow-worktree` from `1.5.0` to `1.6.0`**

In `plugins/dev-flow-worktree/.claude-plugin/plugin.json`, replace:

```
  "version": "1.5.0",
```

with:

```
  "version": "1.6.0",
```

Same constraint: `version` only.

- [x] **Step 3: Verify — both version strings read back correctly**

```bash
cd /Users/taylor/dev/claude-plugins
rtk proxy grep -n '"version"' plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
```

Expected: two lines, showing `2.4.0` for `plugins/dev-flow/...` and `1.6.0` for `plugins/dev-flow-worktree/...`. (`rtk proxy` is required here — the bare `grep` is rewritten by the shell hook and elides path components, making it impossible to tell which version belongs to which plugin.)

- [x] **Step 4: Verify — manifests still valid and still in sync, exactly one line changed per file**

```bash
cd /Users/taylor/dev/claude-plugins
python3 scripts/check-sync.py
claude plugin validate .
git diff --numstat -- plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
```

Expected: `check-sync: all checks passed` (Check A is unaffected — it does not read `version`); `claude plugin validate .` succeeds (**8 missing-author warnings are expected, NOT a failure**); `--numstat` showing exactly `1 1` for each manifest. More than one changed line means something besides `version` was touched — revert it.

- [x] **Step 5: Commit**

```bash
cd /Users/taylor/dev/claude-plugins
git add plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
git commit -m "dev-flow 2.4.0, dev-flow-worktree 1.6.0"
```

---

### Task 3: Replace `CLAUDE.md`'s hand-mirroring bullet with the root-cause verification rule

**Files:**
- Modify: `CLAUDE.md` (line 9)

**Depends on:** nothing technically — a disjoint file from Tasks 1–2. Sequenced third only to match the design's `§Exact change list` order; safe to do first or in parallel.

**This is a line REPLACEMENT, not an append.** Appending the new rule after the old sentence would leave both the superseded residue-grep sentence and the new rule in the file — passing `check-sync.py` (which never reads `CLAUDE.md`) and passing Task 4's presence grep (which only checks the new text is *present*, not that the old text is *absent*). Only the residue grep in Step 3 below (and the design's own §Verification step 3) catches an append-instead-of-replace mistake here.

- [x] **Step 1: Locate and replace line 9**

Locate:

```bash
cd /Users/taylor/dev/claude-plugins
git grep -nF 'mirror those by hand' -- CLAUDE.md
```

Expected: one hit, at line 9. Read the file to confirm the full line reads:

```
- **Some files are mirrored across `dev-flow` and `dev-flow-worktree` and must be edited in both.** `python3 scripts/check-sync.py` enforces what can be enforced mechanically — the `adversarial-review/SKILL.md` pair (line-for-line identical after `dev-flow-worktree` → `dev-flow`, minus declared exceptions) and the `description` duplicated between each `plugin.json` and `.claude-plugin/marketplace.json`. It runs on every PR. The pipeline `SKILL.md` pair and the two `README.md`s are too divergent to check mechanically — mirror those by hand. For any hand-mirrored edit, put a residue grep in the change's verification — grep for the exact phrases the edit removes, expecting no hits — since a one-sided miss leaves the old text behind and nothing else catches it.
```

Replace that **entire line** (the whole bullet, all one physical line) with:

```
- **Some files are mirrored across `dev-flow` and `dev-flow-worktree` and must be edited in both.** `python3 scripts/check-sync.py` enforces what can be enforced mechanically — the `adversarial-review/SKILL.md` pair (line-for-line identical after `dev-flow-worktree` → `dev-flow`, minus declared exceptions) and the `description` duplicated between each `plugin.json` and `.claude-plugin/marketplace.json`. It runs on every PR. The pipeline `SKILL.md` pair and the two `README.md`s are too divergent to check mechanically — mirror those by hand. **`check-sync.py` proves the two copies agree with each other, never that either is correct**: text mangled identically in both sides passes it, and so does an edit missed on both. So any change to a mirrored pair, machine-checked or hand-mirrored, must also verify against something *outside* the pair. **Always:** grep for the exact phrases the edit removes, expecting no hits. **When the change has a design doc** that gives replacement or inserted text as fenced blocks: also add a short `python3` check that re-reads those blocks from the design on disk, never retyped, asserting each appears verbatim in its target and, for an insertion, directly after its anchor line. Write that check per change — the block-to-file mapping differs every time, so there is no shared runner to call.
```

- [x] **Step 2: Verify — line count unchanged, exactly one line changed**

```bash
cd /Users/taylor/dev/claude-plugins
wc -l CLAUDE.md
git diff --numstat -- CLAUDE.md
```

Expected: `29` (unchanged — this is a replacement, not an append), and `--numstat` showing exactly `1 1 CLAUDE.md`. `1 0` (pure addition, no removal) means the old sentence was appended to rather than replaced — undo and redo Step 1.

- [x] **Step 3: Verify — old residue sentence is gone, new rule is present**

```bash
cd /Users/taylor/dev/claude-plugins
git grep -nF 'For any hand-mirrored edit' -- CLAUDE.md
echo "exit=$?"
git grep -nF 'proves the two copies agree with each other' -- CLAUDE.md
```

Expected: the first command produces **no output**, `exit=1` — the old sentence `gh-10` appended is gone. The second produces **exactly one line** — the new rule's opening clause is present. This residue check is the load-bearing one the design calls out by name: it is the *only* check in this entire change (scoped or full) that would catch an append-instead-of-replace mistake here, because `check-sync.py` never reads `CLAUDE.md` and a presence-only grep can't tell an append from a replacement.

- [x] **Step 4: Verify — design-conformance subset (the `CLAUDE.md` block matches the design byte-for-byte)**

This is a task-scoped subset of the design's own §Verification step 6 script — it checks only the `CLAUDE.md` block, since Task 1's blocks are that task's business and Task 4 runs the complete, unmodified script over all seven. It reads the expected text from the design file on disk, never retyped, which is what catches a word mangled while transcribing §5's replacement bullet: Step 3's greps match only the new rule's opening clause and the whole of the old sentence, so a mangling further into that long line passes both. Copy this exactly; it is deliberately pure ASCII, so a mistyped copy fails loudly instead of passing, and the fence is unindented on purpose — a `python3` heredoc indented under a list item is an `IndentationError`.

```bash
cd /Users/taylor/dev/claude-plugins
python3 - <<'PY'
import sys
from pathlib import Path
DESIGN = "docs/superpowers/specs/2026-07-27-gh-7-review-depth-design.md"
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
assert [len(b) for b in blocks] == [1, 1, 1, 2, 2, 1, 12], "design code-block shape changed; stop and re-read the design"
want = blocks[5]
L = Path("CLAUDE.md").read_text(encoding="utf-8").split("\n")
at = [i for i in range(len(L) - len(want) + 1) if L[i:i + len(want)] == want]
ok = len(at) == 1
if not ok:
    print("MISMATCH: CLAUDE.md rule -- found %d times, want exactly 1" % len(at))
print("design-conformance (CLAUDE.md subset):", "OK" if ok else "FAIL")
sys.exit(0 if ok else 1)
PY
echo "exit=$?"
```

Expected: `design-conformance (CLAUDE.md subset): OK`, `exit=0`.

- [x] **Step 5: Commit**

```bash
cd /Users/taylor/dev/claude-plugins
git add CLAUDE.md
git commit -m "CLAUDE.md: state the mirrored-pair verification rule at its root cause"
```

---

### Task 4: End-to-end verification — all six of the design's §Verification steps, plus a scope check

**Files:** none modified — **this task must produce an empty diff.** It only reads and reports.

**Depends on:** Tasks 1, 2, and 3 all complete and committed.

Run every step from the repo root. **All of them must pass.**

**You do not fix anything in this task.** You hold none of Tasks 1–3's replacement text — it lives in the design and in those tasks' briefs, not in yours — so any "fix" applied here would be retyped from memory, which is the exact failure Step 6 exists to catch. If any step fails: stop, change no file, and report **BLOCKED**, giving (a) the step number, (b) the command you ran, and (c) its complete output. The controller routes that to the task that owns the file — **Task 1** for the two `SKILL.md` copies and `CONTEXT.md`, **Task 2** for the two `plugin.json` files, **Task 3** for `CLAUDE.md` — as a finding in that task's fix loop, and then re-dispatches this task fresh. A re-dispatched Task 4 begins again at Step 1 and runs **every** step, not only the one that failed: a fix for one can break another.

Steps 1–6 are the design's §Verification steps; Step 7 is this plan's scope check. **Copy every command exactly as written below, character for character.** The assertions are the design's; the one place a command's text departs from the design is Step 5, which carries the `rtk proxy` prefix this plan's Global Constraints require and says so in place. Do not substitute a variant of your own.

- [x] **Step 1: Mirror and manifest sync**

```sh
python3 scripts/check-sync.py
```

Expected: `check-sync: all checks passed`, with the mirror pair reporting **`85 lines, 1 declared exception`**.

- [x] **Step 2: Marketplace validation**

```sh
claude plugin validate .
```

Expected: success. **8 missing-author warnings are expected** and are not a failure.

- [x] **Step 3: Residue grep — the two in-place edits left no old text behind**

```sh
git grep -nF -e 'four angles, inlined (below)' -e 'untestable success criteria. |' -e '(verbatim):**' -e 'A named check a seed runs over an artifact' -e 'For any hand-mirrored edit' -- ':!docs/superpowers'
```

Expect **no output** (exit 1).

- [x] **Step 4: Presence grep — the two insertions landed in both copies**

```sh
git grep -nF -e '**Seam placement:**' -e 'all five apply' -e 'Input-contract completeness' -- ':!docs/superpowers'
```

Expect **exactly six lines**: each phrase once in `plugins/dev-flow/skills/adversarial-review/SKILL.md` and once in `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md`.

- [x] **Step 5: Version spot-check**

```sh
rtk proxy grep -n '"version"' plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
```

Expect exactly two lines: `plugins/dev-flow/.claude-plugin/plugin.json` showing `2.4.0`, and `plugins/dev-flow-worktree/.claude-plugin/plugin.json` showing `1.6.0`.

**The `rtk proxy` prefix is this plan's one deliberate departure from the design's command text**, per Global Constraints. The design's §Verification step 5 writes the bare `grep` and never mentions this environment's shell hook; run in this checkout, the bare form prints one of the two paths as `plugins/.../.claude-plugin/plugin.json`, eliding the very segment that tells the plugins apart — so a swapped version pair reads as a pass. The assertion is the design's; only the invocation changes. **Do not run the bare form.**

- [x] **Step 6: Design conformance — every block landed verbatim, in the right place**

This is the complete, unmodified script from the design's §Verification step 6 — the load-bearing check that Tasks 1 and 3's subset scripts stood in for. It is the only step that catches a word mangled identically in both mirror copies, an edit applied to one file but skipped in another, or the fifth angle inserted inside the four-bullet block instead of after it. Copy it exactly; it is deliberately pure ASCII, and the fence is deliberately unindented — a `python3` heredoc indented under a list item is an `IndentationError`.

```sh
python3 - <<'PY'
import sys
from pathlib import Path
DESIGN = "docs/superpowers/specs/2026-07-27-gh-7-review-depth-design.md"
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
assert [len(b) for b in blocks] == [1, 1, 1, 2, 2, 1, 12], "design code-block shape changed; stop and re-read the design"
PAIR = ["plugins/dev-flow/skills/adversarial-review/SKILL.md",
        "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md"]
SPEC = [("line 28, diff row",     blocks[0], None,                  PAIR),
        ("line 29, design row",   blocks[1], None,                  PAIR),
        ("line 34, block header", blocks[2], None,                  PAIR),
        ("fifth angle",           blocks[3], "- **Altitude:**",     PAIR),
        ("input-contract pass",   blocks[4], "**Pinned template",   PAIR),
        ("CLAUDE.md rule",        blocks[5], None,                  ["CLAUDE.md"]),
        ("CONTEXT.md glossary",   blocks[6], None,                  ["CONTEXT.md"])]
bad = []
for name, want, anchor, targets in SPEC:
    for path in targets:
        L = Path(path).read_text(encoding="utf-8").split("\n")
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

Expected: exactly `design-conformance: OK` and `exit=0`. A `MISMATCH` line names the block and file whose text or position differs — re-paste that block from the design's `§Exact change list` and re-run from Step 1.

- [x] **Step 7: Scope check — the final diff touches exactly six files and nothing else**

```bash
cd /Users/taylor/dev/claude-plugins
git status --porcelain
git diff --stat main...HEAD
```

Expected: `git status --porcelain` prints nothing except, possibly, this design's and this plan's own two `docs/superpowers/` artifacts if not yet committed by the surrounding dev-flow run. `git diff --stat main...HEAD` must list exactly the six files from the File map (plus those two `docs/superpowers/` artifacts if already committed) — **no `.claude-plugin/marketplace.json`, no `scripts/check-sync.py`, no `README.md`, no `plugins/better-code-review/`, nothing under `docs/superpowers/specs/` or `docs/superpowers/plans/` other than this change's own two artifacts.** Anything else means scope leaked; remove it.

---

## Definition of done

- Both `adversarial-review/SKILL.md` copies are 85 lines and carry all five edits from `§Exact change list` §1 & 2, identically.
- `CONTEXT.md` is 67 lines, carries the four-term glossary region, and landed in the same commit as the two `SKILL.md` copies.
- `plugins/dev-flow` is at `2.4.0`; `plugins/dev-flow-worktree` is at `1.6.0`.
- `CLAUDE.md` is 29 lines; its hand-mirroring bullet is the replaced root-cause rule, not the old sentence with the new one appended.
- All six of the design's §Verification steps pass, plus the scope check.
- Nothing has been pushed, no PR opened, no merge performed.
