---
dev-flow:
  slug: gh-10-opus-resolver
  spec: docs/superpowers/specs/2026-07-27-gh-10-opus-resolver-design.md
---

# Swap the `fable` resolver tier for `opus` — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `opus` the unconditional group-resolver tier in `adversarial-review` — removing the `fable` alias and its session-model-dependent fallback from the protocol entirely — and restate every clause in both `adversarial-review` copies and both pipeline copies that claimed "model diversity", so the prose asserts only what the protocol delivers and what the provenance check mechanically verifies.

**Architecture:** Pure prose-and-manifest change across seven files, no code. Two of the files are a `check-sync.py`-enforced **mirror pair** (`adversarial-review/SKILL.md` × 2) where every edit must land in both copies at the same line index and no line may be added or removed. Two more are a **hand-mirrored pair** (the pipeline `SKILL.md` × 2) that no mechanical check covers, backstopped only by a residue grep for the phrases the edits remove. Two are version bumps that are load-bearing (the install cache is version-keyed). One is a `CLAUDE.md` sentence recording the residue-grep backstop as standing policy.

**Tech Stack:** Markdown, JSON manifests, `python3 scripts/check-sync.py`, `claude plugin validate .`, `git grep`. No build, no test framework, no linter.

**Authoritative source:** `docs/superpowers/specs/2026-07-27-gh-10-opus-resolver-design.md`. Where this plan quotes replacement prose, it reproduces the design's literal text. **If this plan and the design ever disagree, the design wins** — stop and re-read `§Exact change list` before improvising.

---

## Global Constraints

Every task's requirements implicitly include this section.

- **Repo root:** `/Users/taylor/dev/claude-plugins`. Every path below is relative to it. Work in place on the existing branch `tayl0r/gh-10-opus-resolver` — **do not create a git worktree, do not switch branches, do not push, do not open a PR, do not merge.** Per-task `git commit` is expected; nothing beyond it.
- **There is no test framework, no build, no linter in this repo.** Do not run `pytest`, `npm test`, `ruff`, or invent one. Every verification step in this plan is an exit code plus stdout from `python3 scripts/check-sync.py`, `claude plugin validate .`, `git grep`, `git diff --numstat`, or the inline `python3 - <<'PY'` design-conformance checks given verbatim in Tasks 1, 2, and 5.
- **`claude plugin validate .` emits 8 missing-author warnings. That is expected and is NOT a failure.** Only a non-zero exit or an explicit error is a failure.
- **Scope is exactly seven files.** `plugins/dev-flow/skills/adversarial-review/SKILL.md`, `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md`, `plugins/dev-flow/skills/dev-flow/SKILL.md`, `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`, `plugins/dev-flow/.claude-plugin/plugin.json`, `plugins/dev-flow-worktree/.claude-plugin/plugin.json`, `CLAUDE.md`. Nothing else may appear in the final diff.
- **Explicitly do NOT edit** (design §Blast radius / §Out of scope): `.claude-plugin/marketplace.json`, `scripts/check-sync.py`, `.github/workflows/check-sync.yml`, `docs/agents/*.md`, either `plugins/dev-flow*/README.md`, anything under `docs/superpowers/specs/` or `docs/superpowers/plans/` other than ticking this plan's own checkboxes, or the git-ignored `.superpowers/` scratch tree.
- **Benign residual hits that must be left alone.** After the change, `sonnet` still appears on line 24 of both `adversarial-review` copies (seeds stay `sonnet` — correct) and at `plugins/better-code-review/skills/better-code-review/SKILL.md:13` (an unrelated plugin). `resolver` still appears on unchanged lines 20 and 63 of both `adversarial-review` copies, and in a completely unrelated sense (the branch/`<username>` resolver) at `plugins/dev-flow/skills/dev-flow/SKILL.md` lines 78 and 268 and `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` lines 76 and 262. **None of these is an edit target.**
- **Anchor on text, not line numbers.** The line numbers in this plan and in the design are from the pre-change files and are given only to help you find the line. Locate every edit target with the `grep -n` command the task supplies, then replace the line that grep found. Never edit "line 73" by counting.
- **Every replacement below is a single line.** Markdown here is one paragraph per physical line; the code blocks in this plan are shown unwrapped for readability but MUST be pasted as **one line with no internal newline**. Adding a newline changes the file's line count and breaks the mirror check (`LINE_COUNT_FIX`).
- **Copy replacement prose verbatim, character for character.** These strings contain em dashes (`—`), the multiplication sign (`×`), the set-membership sign (`∈`), and backticks. The mirror check, the line counts, and the residue greps test shape and absence only — the same character mangled **identically in both copies** passes every one of them. What catches that is each prose task's design-conformance check, which re-reads the replacement text from the design file on disk and requires a byte-for-byte match. Copy those check scripts exactly as written: they are deliberately pure ASCII, so a mistyped copy fails loudly instead of passing.
- **The shell hook rewrites bare `grep`/`find`/`diff` and can elide path components in their output.** Where exact output matters, prefix with `rtk proxy` (e.g. `rtk proxy grep -n ...`). `git grep`, `git diff --numstat`, and `python3` are unaffected — run those as written.
- **Never write the `fable` residue grep as `-E '\bfable\b'`.** `\b` is not honored by git's regex engine here; the command silently matches nothing and looks like a pass no matter what the tree contains. Use the literal form given in the tasks.

---

## File map

| File | Responsibility in this change | Task |
|---|---|---|
| `plugins/dev-flow/skills/adversarial-review/SKILL.md` | Mirror-pair copy A. Five in-place single-line replacements (lines 18, 59, 69, 73, 75). Stays at **81 lines**. | 1 |
| `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md` | Mirror-pair copy B. The identical five replacements, with the `dev-flow-worktree` variant tokens preserved on line 69. Stays at **81 lines**. | 1 |
| `plugins/dev-flow/skills/dev-flow/SKILL.md` | Hand-mirrored pipeline copy A. Three edits (lines 8, 46, 273). Stays at **277 lines**. | 2 |
| `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` | Hand-mirrored pipeline copy B. The same three edits (lines 8, 45, 267), with `dev-flow-worktree:adversarial-review` skill references. Stays at **271 lines**. | 2 |
| `plugins/dev-flow/.claude-plugin/plugin.json` | `"version": "2.2.0"` → `"2.3.0"`. Load-bearing: the install cache is version-keyed. | 3 |
| `plugins/dev-flow-worktree/.claude-plugin/plugin.json` | `"version": "1.4.0"` → `"1.5.0"`. Same. | 3 |
| `CLAUDE.md` | One sentence appended to the "Changing a plugin" hand-mirroring bullet, making the residue-grep backstop standing policy. | 4 |

No file is created, renamed, or deleted.

---

## Task ordering and why

Tasks 1 and 2 are each **atomic across a file pair** — the whole point of the task boundary is that a task which edits one copy and not the other leaves the repo broken (Task 1 red in CI, Task 2 silently wrong). Do not split either task by file. Task 3 (version bumps) comes after both prose tasks because each plugin's single `version` covers both of that plugin's skills, so it can only be bumped once all of that plugin's prose is final. Task 4 is independent and could run anywhere; it is placed after the code-adjacent work so the repo-policy sentence lands last. Task 5 re-runs the design's full §Verification suite against the finished tree.

---

### Task 1: Rewrite the `adversarial-review` mirror pair (both copies, five lines each)

**Files:**
- Modify: `plugins/dev-flow/skills/adversarial-review/SKILL.md` (lines 18, 59, 69, 73, 75)
- Modify: `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md` (lines 18, 59, 69, 73, 75)
- Test: none — this repo has no test framework. Verification is `scripts/check-sync.py` plus greps.

**Depends on:** nothing. This is the first task.

**Read `§1 & 2` of the design before starting.** These two files are a declared `check-sync.py` **mirror pair**: they must stay line-for-line identical after substituting `dev-flow-worktree` → `dev-flow` on both sides, except for one declared exception at line 12 (the `working-dir` bullet), which this task does not touch.

Three hard requirements, from the design's §Sync constraint:

1. **All five edits land in BOTH files.** A one-sided edit is an undeclared-divergence failure naming the line.
2. **No line is added or removed in either file.** All five edits are in-place single-line replacements; both files must still be **81 lines** afterwards. A line-count mismatch is a distinct, harder-to-read failure (`LINE_COUNT_FIX`), and the pair's schema cannot express a one-sided extra line even as an exception.
3. **The variant tokens on line 69 stay in place.** Four of the five replacements are byte-identical in both copies. Only edit C (line 69) differs: the `dev-flow` copy keeps `dev-flow's orchestrator, when called by dev-flow`, the worktree copy keeps `dev-flow-worktree's orchestrator, when called by dev-flow-worktree`. Those canonicalize to the same string, so the line still compares equal.

For each edit below: run the `grep -n` command to locate the line in **both** files, `Read` each located line in full, use that full line text as the exact `old_string`, and replace it with the single-line `new_string` shown. Do not reflow, do not wrap, do not add a trailing space.

- [x] **Step 1: Confirm the starting state**

```bash
cd /Users/taylor/dev/claude-plugins
python3 scripts/check-sync.py
wc -l plugins/dev-flow/skills/adversarial-review/SKILL.md plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
git grep -nic 'fable' -- ':!docs/superpowers'
```

Expected: `check-sync: all checks passed` with `mirror pair "adversarial-review" ... OK (81 lines, 1 declared exception)`; `81` for each file; and exactly two `fable` count lines, `5` for each `adversarial-review` copy and no other file. If any of that differs, stop — the tree is not the state this plan was written against.

- [x] **Step 2: Edit A — Review integrity, family-match clause (line 18 in both files)**

Locate:

```bash
cd /Users/taylor/dev/claude-plugins
git grep -n 'Review integrity (never inline)' -- 'plugins/*/skills/adversarial-review/SKILL.md'
```

Expected: one hit per file, at line 18. Replace that entire line, **identically in both files**, with:

```
**Review integrity (never inline).** The seed and resolver passes MUST run as separate subagents on their specified models (per Model, below). If they cannot be spawned — no `Agent` tool, or a required model unavailable — halt and report; **never** produce a single-model inline review as a silent substitute. To make the model axis verifiable, every reviewer prompt (seed and resolver) requires the reviewer to state, as the first line of its report, the model its own system prompt names. The review matches each self-report to the tier requested for it — a **family match** (e.g. an "Opus 5" self-report satisfies the `opus` tier) rather than a hardcoded dated id, because a self-report names a product and dated ids drift — and canonicalizes it to that tier's alias. A missing or mismatched first line is treated exactly like a failed spawn: halt.
```

What changed, so you can sanity-check the paste: the example moved from `"Fable 5"` / `` `fable` `` to `"Opus 5"` / `` `opus` ``; `honoring the resolver opus-fallback` was replaced by the durable reason family matching is used at all; and the canonicalization no longer restates the alias roster (`(`sonnet`, `fable`, or `opus`)` is gone) — it now maps to "that tier's alias".

- [x] **Step 3: Edit B — Resolution procedure, step 2 (line 59 in both files)**

Locate:

```bash
cd /Users/taylor/dev/claude-plugins
git grep -n 'Group similar issues together' -- 'plugins/*/skills/adversarial-review/SKILL.md'
```

Expected: one hit per file, at line 59. Replace that entire line, **identically in both files**, with:

```
2. Group similar issues together. For each group, spawn one agent, on the resolver model (see Model).
```

- [x] **Step 4: Edit C — Report-back, step 6 (line 69 in both files) — THIS ONE DIFFERS PER COPY**

Locate:

```bash
cd /Users/taylor/dev/claude-plugins
git grep -n '6. Report back: the commit' -- 'plugins/*/skills/adversarial-review/SKILL.md'
```

Expected: one hit per file, at line 69.

In `plugins/dev-flow/skills/adversarial-review/SKILL.md`, replace that entire line with:

```
6. Report back: the commit(s) made, a summary of applied vs. skipped fixes, the post-fix suite result (diff mode), every new issue filed, and a **provenance** line naming the reviewers actually spawned per tier with their canonicalized tier aliases (from Review integrity's family match), in the form `seeds: N× <tier>; resolvers: M× <tier>` with `<tier>` ∈ {`sonnet`, `opus`} (e.g. `seeds: 2× sonnet; resolvers: 3× opus`; a review that surfaces no findings spawns no resolvers and reports `resolvers: 0`, tierless). Provenance is the evidence the invoking caller (dev-flow's orchestrator, when called by dev-flow) checks directly to confirm the review really fanned out to separate reviewer subagents on the tiers this section specifies — never a single inline pass.
```

In `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md`, replace that entire line with the same text except that **both** occurrences of `dev-flow` in the final parenthetical read `dev-flow-worktree`, exactly as they do today — i.e.:

```
6. Report back: the commit(s) made, a summary of applied vs. skipped fixes, the post-fix suite result (diff mode), every new issue filed, and a **provenance** line naming the reviewers actually spawned per tier with their canonicalized tier aliases (from Review integrity's family match), in the form `seeds: N× <tier>; resolvers: M× <tier>` with `<tier>` ∈ {`sonnet`, `opus`} (e.g. `seeds: 2× sonnet; resolvers: 3× opus`; a review that surfaces no findings spawns no resolvers and reports `resolvers: 0`, tierless). Provenance is the evidence the invoking caller (dev-flow-worktree's orchestrator, when called by dev-flow-worktree) checks directly to confirm the review really fanned out to separate reviewer subagents on the tiers this section specifies — never a single inline pass.
```

What changed: the `<tier>` enum drops `fable` (it is now exactly `{`sonnet`, `opus`}`); the example resolver tier becomes `opus`; and the closing claim changes from "genuinely model-diverse" to the fan-out / tier-conformance property the check actually establishes.

- [x] **Step 5: Edit D — Model, group-resolution agents (line 73 in both files)**

Locate:

```bash
cd /Users/taylor/dev/claude-plugins
git grep -n '^\*\*Group-resolution agents\*\*' -- 'plugins/*/skills/adversarial-review/SKILL.md'
```

Expected: one hit per file, at line 73. Replace that entire line, **identically in both files**, with:

```
**Group-resolution agents** — the tier that determines the best long-term design and adversarially self-checks — run on `opus` (a harness alias, never a dated model id), unconditionally, with no session-model-dependent fallback. Their independence from the artifact's author is **contextual, not cross-family**: a fresh context window with no memory of authoring, an explicitly adversarial prompt, and a spawn that provenance verifies out of band. A session-model-conditional tier would buy back family separation only by making the resolver tier depend on ambient state, which the provenance check could no longer compare against a fixed expectation.
```

- [x] **Step 6: Edit E — Model, seed reviewers (line 75 in both files)**

Locate:

```bash
cd /Users/taylor/dev/claude-plugins
git grep -n '^\*\*Seed reviewers\*\*' -- 'plugins/*/skills/adversarial-review/SKILL.md'
```

Expected: one hit per file, at line 75. Replace that entire line, **identically in both files**, with:

```
**Seed reviewers** — the findings-only quality and correctness passes — run on `sonnet`: cheaper than `opus`, and in the common case a different family from the author, which is a bonus on what gets *noticed* rather than a guarantee this protocol enforces. They only surface findings; the resolvers do the judgment, so the resolver tier's cost isn't warranted here.
```

Line 77 (`**Executors, fixers, and the orchestrator** run on the main session model.`) is **unchanged** — do not touch it.

- [x] **Step 7: Verify — line counts unchanged and exactly five lines changed per file**

```bash
cd /Users/taylor/dev/claude-plugins
wc -l plugins/dev-flow/skills/adversarial-review/SKILL.md plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
git diff --numstat -- plugins/dev-flow/skills/adversarial-review/SKILL.md plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
```

Expected: `81` for each file, and `--numstat` showing exactly `5	5` for each of the two paths. Any other number means an edit was missed, doubled, or split a line — fix it before continuing. **`5	5` is the single clearest signal that all five in-place replacements landed on both sides.**

- [x] **Step 8: Verify — the mirror check passes**

```bash
cd /Users/taylor/dev/claude-plugins
python3 scripts/check-sync.py
```

Expected, exactly:

```
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... OK (81 lines, 1 declared exception)
check-sync: all checks passed
```

Exit code 0. **`81 lines, 1 declared exception` is load-bearing** — a different line count, or a stale/missing exception, is a failure even if the word "OK" appears elsewhere. An undeclared-divergence failure naming a line number means that line was edited in one copy and not the other: go back and apply the matching edit.

- [x] **Step 9: Verify — no `fable` survives in these two files**

```bash
cd /Users/taylor/dev/claude-plugins
git grep -ni 'fable' -- ':!docs/superpowers'
echo "exit=$?"
```

Expected: **no output at all**, `exit=1`. (Every `fable` reference in tracked files outside `docs/superpowers` lived on the five lines this task replaced.) Any hit names a line you missed. Do not rewrite this grep with `\b`.

- [x] **Step 9b: Verify — the five replacement lines match the design byte-for-byte**

Steps 7–9 test shape and absence only: an em dash retyped as a hyphen, or a mangled `×` or `∈`, **identically in both copies**, passes all three — and `check-sync.py` canonicalizes the variant tokens away, so it also cannot see the `dev-flow` variant pasted into the worktree copy of line 69. This check is the content backstop. It re-reads the five replacement lines from the design file on disk — never from your own paste — and requires each to appear verbatim in both copies (with the worktree variant derived for line 69). Copy the script exactly; it is deliberately pure ASCII, so a mistyped copy crashes loudly instead of passing.

```bash
cd /Users/taylor/dev/claude-plugins
python3 - <<'PY'
import sys
from pathlib import Path
DESIGN = "docs/superpowers/specs/2026-07-27-gh-10-opus-resolver-design.md"
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
assert [len(x) for x in blocks] == [1] * 8, "design code-block shape changed; stop and re-read the design"
b = [x[0] for x in blocks]
W = lambda s: s.replace("dev-flow", "dev-flow-worktree")
A = Path("plugins/dev-flow/skills/adversarial-review/SKILL.md").read_text(encoding="utf-8").split("\n")
B = Path("plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md").read_text(encoding="utf-8").split("\n")
bad = [name for name, copy, want in [
    ("edit A, dev-flow copy", A, b[0]), ("edit A, worktree copy", B, b[0]),
    ("edit B, dev-flow copy", A, b[1]), ("edit B, worktree copy", B, b[1]),
    ("edit C, dev-flow copy", A, b[2]), ("edit C, worktree copy", B, W(b[2])),
    ("edit D, dev-flow copy", A, b[3]), ("edit D, worktree copy", B, b[3]),
    ("edit E, dev-flow copy", A, b[4]), ("edit E, worktree copy", B, b[4]),
] if copy.count(want) != 1]
for name in bad:
    print("MISMATCH:", name, "-- no line matches the design's block byte-for-byte; re-paste from the design")
print("design-conformance (adversarial-review pair):", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected: `design-conformance (adversarial-review pair): OK`, `exit=0`. A `MISMATCH` line names the edit and copy whose text differs from the design's literal block — re-do that edit by copying the design's fenced block again (the worktree copy of edit C carries `dev-flow-worktree` where the block says `dev-flow`), then re-run Steps 7–9b.

- [x] **Step 10: Commit**

```bash
cd /Users/taylor/dev/claude-plugins
git add plugins/dev-flow/skills/adversarial-review/SKILL.md plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
git commit -m "adversarial-review: make opus the unconditional resolver tier"
```

---

### Task 2: Rewrite the hand-mirrored pipeline pair (both copies, three edits each)

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md` (lines 8, 46, 273)
- Modify: `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` (lines 8, 45, 267)
- Test: none. Verification is the residue grep plus the design-conformance check in Step 6.

**Depends on:** Task 1 only for ordering hygiene (both tasks are prose edits in disjoint files; running Task 2 first would work — the only interaction is that Step 1's residue grep also hits lines 69 and 73 of both `adversarial-review` copies until Task 1 lands, which Step 1's expected-state note already covers). No content dependency.

**Read `§3 & 4` of the design before starting.** These two files are **NOT** a mechanically checked mirror pair — they differ in length (277 vs 271 lines) and `check-sync.py` never reads them. `claude plugin validate .` reads manifests, not skill prose. The `fable` grep is no help either: **none of the three edits below contains the word `fable`.** Two mechanical backstops cover this pair. Step 5's residue grep catches leftover *old* text: each edit removes a distinctive phrase which afterwards must appear nowhere in tracked files outside `docs/superpowers`, so a one-sided miss fails loudly. Step 6's design-conformance check catches a botched *new* paste: it re-reads the design's literal replacement blocks from disk and requires each edited line to match byte-for-byte — including the `dev-flow-worktree` variant tokens, which no other check sees.

- [x] **Step 1: Confirm the starting state**

```bash
cd /Users/taylor/dev/claude-plugins
wc -l plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
git grep -niE 'model-diverse|diverse reviewers|different from the artifact' -- ':!docs/superpowers'
```

Expected: `277` and `271`; and six hits — three in the pipeline pair per side is the target set, i.e. `dev-flow/skills/dev-flow/SKILL.md` lines 8, 46, 273 and `dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` lines 8, 45, 267. (If Task 1 is already committed, the two `adversarial-review` hits at lines 69 and 73 are gone; if it is not, they will also appear — that is fine, Task 1 removes them.)

- [x] **Step 2: Edit F — intro paragraph, "the model-diverse review" (line 8 in both files)**

Locate:

```bash
cd /Users/taylor/dev/claude-plugins
git grep -n 'the model-diverse review' -- 'plugins/dev-flow/skills/dev-flow/SKILL.md' 'plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md'
```

Expected: one hit per file, at line 8 in each. This is a **phrase-level** edit, not a whole-line replacement — the two surrounding sentences differ between the copies and must be preserved. In each file, replace exactly:

```
the model-diverse review
```

with exactly:

```
the multi-agent review
```

Nothing else on the line changes. The sentence's point is that the fan-out survives the flat-topology constraint, which is still exactly true; only the "diverse" adjective is a claim the protocol no longer makes.

- [x] **Step 3: Edit G — Model Policy (line 46 in `dev-flow`, line 45 in `dev-flow-worktree`)**

Locate:

```bash
cd /Users/taylor/dev/claude-plugins
git grep -n 'Reviewer-model selection' -- 'plugins/dev-flow/skills/dev-flow/SKILL.md' 'plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md'
```

Expected: one hit per file (line 46 / line 45). The current text claims reviewer-model selection is "stated once, in its Model section" and then restates it inline ("on a capable model different from the artifact's author") — a self-contradiction today, and the restated half becomes false with this change. The fix removes the restatement rather than updating it.

In `plugins/dev-flow/skills/dev-flow/SKILL.md`, replace that entire line with:

```
The orchestrator spawns produce-subagents and executors on the main session model, and does its own bookkeeping (checkbox commits, front-matter) inline. Reviewer-model selection — which tier the orchestrator spawns each of the review's seed/resolver leaves on — is owned by `dev-flow:adversarial-review` and stated once, in its Model section; that rule travels with the review skill wherever it is invoked, and is deliberately not restated here.
```

In `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`, replace that entire line with the same text except that the skill reference reads `dev-flow-worktree:adversarial-review`, exactly as it does today — i.e.:

```
The orchestrator spawns produce-subagents and executors on the main session model, and does its own bookkeeping (checkbox commits, front-matter) inline. Reviewer-model selection — which tier the orchestrator spawns each of the review's seed/resolver leaves on — is owned by `dev-flow-worktree:adversarial-review` and stated once, in its Model section; that rule travels with the review skill wherever it is invoked, and is deliberately not restated here.
```

- [x] **Step 4: Edit H — Cross-Cutting Concerns, "Review provenance is checked, not assumed" (line 273 in `dev-flow`, line 267 in `dev-flow-worktree`)**

Locate:

```bash
cd /Users/taylor/dev/claude-plugins
git grep -n 'Review provenance is checked, not assumed' -- 'plugins/dev-flow/skills/dev-flow/SKILL.md' 'plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md'
```

Expected: one hit per file (line 273 / line 267). Only the bullet's **final sentence** changes; the mechanical description earlier in the bullet ("seeds must be the seed tier, resolvers the resolver tier") is already tier-relative and stays verbatim. Replace the whole line anyway, using the text below, so there is no ambiguity about what the finished line reads.

In `plugins/dev-flow/skills/dev-flow/SKILL.md`:

```
- **Review provenance is checked, not assumed.** The orchestrator runs each review (Design, Plan, PR — not Execute) in-context, then reads the review's returned provenance line (`seeds: N× <tier>; resolvers: M× <tier>`) directly and halts if it is missing or its tiers violate `dev-flow:adversarial-review`'s Model section (seeds must be the seed tier, resolvers the resolver tier; a `resolvers: 0` line from a no-findings review passes the resolver check vacuously). The tiers are canonicalized by the review's family match, so this is a direct comparison — a cheap self-check that the review actually fanned out to separate reviewer subagents on the specified tiers, rather than folding into a single inline pass.
```

In `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`, the same text with the skill reference reading `dev-flow-worktree:adversarial-review`, exactly as it does today — i.e.:

```
- **Review provenance is checked, not assumed.** The orchestrator runs each review (Design, Plan, PR — not Execute) in-context, then reads the review's returned provenance line (`seeds: N× <tier>; resolvers: M× <tier>`) directly and halts if it is missing or its tiers violate `dev-flow-worktree:adversarial-review`'s Model section (seeds must be the seed tier, resolvers the resolver tier; a `resolvers: 0` line from a no-findings review passes the resolver check vacuously). The tiers are canonicalized by the review's family match, so this is a direct comparison — a cheap self-check that the review actually fanned out to separate reviewer subagents on the specified tiers, rather than folding into a single inline pass.
```

- [x] **Step 5: Verify — the residue grep (the ONLY mechanical backstop for this pair)**

```bash
cd /Users/taylor/dev/claude-plugins
git grep -niE 'model-diverse|diverse reviewers|different from the artifact' -- ':!docs/superpowers'
echo "exit=$?"
```

Expected: **no output at all**, `exit=1`. Any hit is an unedited side of the pipeline pair (or an `adversarial-review` line Task 1 missed) — go fix the named file and line. Do not proceed with a non-empty result; nothing downstream will catch it.

- [x] **Step 6: Verify — line counts unchanged, three lines changed per file, and the new prose matches the design byte-for-byte**

```bash
cd /Users/taylor/dev/claude-plugins
wc -l plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
git diff --numstat -- plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
```

Expected: `277` and `271` (unchanged), and `--numstat` showing exactly `3	3` for each path.

Then run the design-conformance check. It reads the replacement text from the design file on disk — never from your own paste — so it catches what the counts and greps cannot: the same character mangled identically in both copies, and a variant token pasted the wrong way. Copy the script exactly; it is deliberately pure ASCII, so a mistyped copy crashes loudly instead of passing.

```bash
cd /Users/taylor/dev/claude-plugins
python3 - <<'PY'
import sys
from pathlib import Path
DESIGN = "docs/superpowers/specs/2026-07-27-gh-10-opus-resolver-design.md"
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
assert [len(x) for x in blocks] == [1] * 8, "design code-block shape changed; stop and re-read the design"
b = [x[0] for x in blocks]
W = lambda s: s.replace("dev-flow", "dev-flow-worktree")
PA = Path("plugins/dev-flow/skills/dev-flow/SKILL.md").read_text(encoding="utf-8")
PB = Path("plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md").read_text(encoding="utf-8")
bad = [name for name, text, want in [
    ("edit G, dev-flow copy", PA, b[5]), ("edit G, worktree copy", PB, W(b[5])),
    ("edit H, dev-flow copy", PA, b[6]), ("edit H, worktree copy", PB, W(b[6])),
] if text.split("\n").count(want) != 1]
bad += [name for name, text in [("edit F, dev-flow copy", PA), ("edit F, worktree copy", PB)]
        if text.count("the multi-agent review") != 1]
for name in bad:
    print("MISMATCH:", name, "-- edited line differs from the design (or edit F's phrase is not present exactly once)")
print("design-conformance (pipeline pair):", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected: `design-conformance (pipeline pair): OK`, `exit=0`. A `MISMATCH` line names the edit and copy that differs from the design — re-paste that edit from the design's fenced block (the worktree copy carries the `dev-flow-worktree:adversarial-review` skill reference), then re-run Steps 5 and 6. Line 8's surrounding prose legitimately differs between the copies and is deliberately not whole-line-checked; edit F is verified by the phrase count.

- [x] **Step 7: Commit**

```bash
cd /Users/taylor/dev/claude-plugins
git add plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
git commit -m "dev-flow: stop claiming model diversity in the pipeline prose"
```

---

### Task 3: Bump both plugin versions

**Files:**
- Modify: `plugins/dev-flow/.claude-plugin/plugin.json` (line 3)
- Modify: `plugins/dev-flow-worktree/.claude-plugin/plugin.json` (line 3)

**Depends on:** Tasks 1 and 2 must both be complete. Each plugin's single `version` covers all of that plugin's skills — `dev-flow` ships both `adversarial-review` and `dev-flow`, and `dev-flow-worktree` ships both `adversarial-review` and `dev-flow-worktree` — so the bump is only correct once every prose edit in that plugin is final.

**This is not cosmetic cleanup.** The install cache is version-keyed (`~/.claude/plugins/cache/taylor-plugins/<plugin>/<version>/`), so an edit shipped at an unchanged version is **never picked up on re-sync** — Tasks 1 and 2 have no effect on any installed copy until this task lands. Minor bumps per the design's §Assumptions: behavior changes but no interface does (invocation signature, provenance line format, and contract are unchanged).

- [x] **Step 1: Bump `dev-flow` from `2.2.0` to `2.3.0`**

In `plugins/dev-flow/.claude-plugin/plugin.json`, replace:

```
  "version": "2.2.0",
```

with:

```
  "version": "2.3.0",
```

Change **only** the `version` field. Do not touch `description` — it is duplicated into `.claude-plugin/marketplace.json` and `check-sync.py` Check A compares them; the marketplace file is out of scope for this change.

- [x] **Step 2: Bump `dev-flow-worktree` from `1.4.0` to `1.5.0`**

In `plugins/dev-flow-worktree/.claude-plugin/plugin.json`, replace:

```
  "version": "1.4.0",
```

with:

```
  "version": "1.5.0",
```

Same constraint: `version` only.

- [x] **Step 3: Verify — both version strings read back correctly**

```bash
cd /Users/taylor/dev/claude-plugins
rtk proxy grep -n '"version"' plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
```

Expected: two lines, showing `2.3.0` for `plugins/dev-flow/...` and `1.5.0` for `plugins/dev-flow-worktree/...`. (`rtk proxy` is required here — the bare `grep` is rewritten by the shell hook and elides path components, which makes it impossible to tell which version belongs to which plugin.)

- [x] **Step 4: Verify — manifests still valid and still in sync**

```bash
cd /Users/taylor/dev/claude-plugins
python3 scripts/check-sync.py
claude plugin validate .
git diff --numstat -- plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
```

Expected: `check-sync: all checks passed`; `claude plugin validate .` succeeds (**8 missing-author warnings are expected and are not a failure**); and `--numstat` showing exactly `1	1` for each manifest. More than one changed line per manifest means something other than `version` was edited — revert it. `check-sync.py` Check A does not read `version` at all, so it must still pass unchanged.

- [x] **Step 5: Commit**

```bash
cd /Users/taylor/dev/claude-plugins
git add plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
git commit -m "dev-flow 2.3.0, dev-flow-worktree 1.5.0"
```

---

### Task 4: Record the residue-grep backstop as standing policy in `CLAUDE.md`

**Files:**
- Modify: `CLAUDE.md` (the "Changing a plugin" bullet at line 9)

**Depends on:** nothing technically; sequenced last among the edit tasks so the repo-policy sentence lands after the change it generalizes from.

This earns its place because the next person doing a hand-mirrored edit reads the auto-loaded `CLAUDE.md`, not the design doc. It puts the backstop at the shared boundary so every future hand-mirrored edit inherits the pattern instead of reinventing it — which is exactly what Task 2 had to do.

- [ ] **Step 1: Append the sentence to the hand-mirroring bullet**

Locate:

```bash
cd /Users/taylor/dev/claude-plugins
git grep -n 'mirror those by hand' -- CLAUDE.md
```

Expected: one hit, at line 9 — the bullet that ends `…too divergent to check mechanically — mirror those by hand.`

**Append** (on the same line, after a single space following that final period) exactly:

```
For any hand-mirrored edit, put a residue grep in the change's verification — grep for the exact phrases the edit removes, expecting no hits — since a one-sided miss leaves the old text behind and nothing else catches it.
```

Do not start a new line, a new bullet, or a new paragraph — this is one sentence appended to the existing bullet.

- [ ] **Step 2: Verify — the sentence landed, on the right line, with no line added**

```bash
cd /Users/taylor/dev/claude-plugins
git grep -n 'residue grep' -- CLAUDE.md
git diff --numstat -- CLAUDE.md
```

Expected: exactly one hit, on **line 9** (the same line as `mirror those by hand`), and `--numstat` showing exactly `1	1	CLAUDE.md`. A hit on any other line number, or `1	0`, means the sentence was added as a new line instead of appended — fix it.

- [ ] **Step 3: Commit**

```bash
cd /Users/taylor/dev/claude-plugins
git add CLAUDE.md
git commit -m "CLAUDE.md: require a residue grep for hand-mirrored edits"
```

---

### Task 5: End-to-end verification — run all five of the design's §Verification steps

**Files:** none modified. This task only reads.

**Depends on:** Tasks 1, 2, 3, and 4 must all be complete and committed.

Run every step from the repo root. **All of them must pass before the change is considered done.** Steps 1–5 are the design's §Verification steps, reproduced in order; Step 4b is this plan's own design-conformance check, and Step 6 its scope check. If any step fails, fix the cause in the owning task's files and re-run **all of them** from the top — a fix for one can break another.

- [ ] **Step 1: Mirror and manifest sync**

```bash
cd /Users/taylor/dev/claude-plugins
python3 scripts/check-sync.py
```

Expected:

```
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... OK (81 lines, 1 declared exception)
check-sync: all checks passed
```

Exit 0. The `81 lines` figure is the same as before the change and is what confirms no line was added or removed in either mirror-pair copy.

- [ ] **Step 2: Marketplace validation**

```bash
cd /Users/taylor/dev/claude-plugins
claude plugin validate .
```

Expected: success. **8 missing-author warnings are expected and are NOT a failure.** Any error, or a non-zero exit, is.

- [ ] **Step 3: No stale `fable` resolver references survive outside `docs/`**

```bash
cd /Users/taylor/dev/claude-plugins
git grep -ni 'fable' -- ':!docs/superpowers'
echo "exit=$?"
```

Expected: **no output**, `exit=1`. `git grep` searches tracked files only, so the git-ignored `.superpowers/` scratch tree is excluded automatically; the pathspec excludes the immutable historical specs and plans, which contain `fable` references that are correct as history and must not be edited. **Do not rewrite this as `-E '\bfable\b'`** — `\b` is not honored by git's regex engine here and the command silently matches nothing, which would look like a pass no matter what the tree contains.

- [ ] **Step 4: No one-sided pipeline-pair edit survives**

```bash
cd /Users/taylor/dev/claude-plugins
git grep -niE 'model-diverse|diverse reviewers|different from the artifact' -- ':!docs/superpowers'
echo "exit=$?"
```

Expected: **no output**, `exit=1`. Each of the three hand-mirrored pipeline edits removes one of these phrases; after the change they appear nowhere in tracked files outside the immutable history. Any hit is an unedited side of the pipeline pair — this is the backstop `check-sync.py` structurally cannot provide for that pair. Like step 3, it detects leftover old text, not a botched replacement.

- [ ] **Step 4b: Design-conformance — every replacement landed byte-for-byte in all seven files**

Steps 3 and 4 detect leftover old text; this detects a botched replacement — including the same character mangled identically in both copies of a pair, which every other check in this plan passes. Expected text is read from the design file on disk, never retyped. Copy the script exactly; it is deliberately pure ASCII.

```bash
cd /Users/taylor/dev/claude-plugins
python3 - <<'PY'
import sys
from pathlib import Path
DESIGN = "docs/superpowers/specs/2026-07-27-gh-10-opus-resolver-design.md"
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
assert [len(x) for x in blocks] == [1] * 8, "design code-block shape changed; stop and re-read the design"
b = [x[0] for x in blocks]
W = lambda s: s.replace("dev-flow", "dev-flow-worktree")
def rd(p):
    return Path(p).read_text(encoding="utf-8")
A = rd("plugins/dev-flow/skills/adversarial-review/SKILL.md").split("\n")
B = rd("plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md").split("\n")
PA = rd("plugins/dev-flow/skills/dev-flow/SKILL.md")
PB = rd("plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md")
bad = [name for name, copy, want in [
    ("edit A, dev-flow copy", A, b[0]), ("edit A, worktree copy", B, b[0]),
    ("edit B, dev-flow copy", A, b[1]), ("edit B, worktree copy", B, b[1]),
    ("edit C, dev-flow copy", A, b[2]), ("edit C, worktree copy", B, W(b[2])),
    ("edit D, dev-flow copy", A, b[3]), ("edit D, worktree copy", B, b[3]),
    ("edit E, dev-flow copy", A, b[4]), ("edit E, worktree copy", B, b[4]),
    ("edit G, dev-flow copy", PA.split("\n"), b[5]), ("edit G, worktree copy", PB.split("\n"), W(b[5])),
    ("edit H, dev-flow copy", PA.split("\n"), b[6]), ("edit H, worktree copy", PB.split("\n"), W(b[6])),
] if copy.count(want) != 1]
bad += [name for name, text in [("edit F, dev-flow copy", PA), ("edit F, worktree copy", PB)]
        if text.count("the multi-agent review") != 1]
if rd("CLAUDE.md").count(b[7]) != 1:
    bad.append("CLAUDE.md residue-grep sentence")
for name in bad:
    print("MISMATCH:", name, "-- differs from the design's literal text; re-paste from the design")
print("design-conformance (all seven files):", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected: `design-conformance (all seven files): OK`, `exit=0`. A `MISMATCH` names the edit and file; fix it in the owning task (Task 1: edits A–E; Task 2: edits F–H; Task 4: the `CLAUDE.md` sentence), then re-run all steps from the top.

- [ ] **Step 5: Spot-check the two version strings**

```bash
cd /Users/taylor/dev/claude-plugins
rtk proxy grep -n '"version"' plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
```

Expected: `2.3.0` for `plugins/dev-flow` and `1.5.0` for `plugins/dev-flow-worktree`.

- [ ] **Step 6: Confirm the final diff touches exactly seven files and nothing else**

```bash
cd /Users/taylor/dev/claude-plugins
git status --porcelain
git diff --stat main...HEAD
```

Expected: `git status --porcelain` prints nothing except, possibly, the untracked/uncommitted `docs/superpowers/specs/2026-07-27-gh-10-opus-resolver-design.md` and `docs/superpowers/plans/2026-07-27-gh-10-opus-resolver-plan.md` if the pipeline has not yet committed them. `git diff --stat main...HEAD` must list exactly the seven files from the File map (plus those two `docs/superpowers/` artifacts if already committed) — **no `.claude-plugin/marketplace.json`, no `scripts/check-sync.py`, no `README.md`, nothing under `docs/superpowers/specs/` or `docs/superpowers/plans/` other than this change's own two artifacts.** Anything else means scope leaked; remove it.

---

## Definition of done

- Both `adversarial-review/SKILL.md` copies are 81 lines and carry all five replacements identically (modulo line 69's variant tokens).
- Both pipeline `SKILL.md` copies are 277 / 271 lines and carry all three edits.
- `plugins/dev-flow` is at `2.3.0`; `plugins/dev-flow-worktree` is at `1.5.0`.
- `CLAUDE.md`'s hand-mirroring bullet ends with the residue-grep sentence.
- All five of the design's §Verification steps pass, plus the design-conformance check (Task 5 Step 4b) and the scope check.
- Nothing has been pushed, no PR opened, no merge performed.
