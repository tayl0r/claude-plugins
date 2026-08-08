---
dev-flow:
  slug: gh-58-completion-predicate
  stops: []
  docs: commit
---

# gh-58: the execution-complete predicate counts markup, not tasks

**Ruling: SHIPS**, as two replacement lines in each pipeline `SKILL.md` — the **Execution-complete signal** paragraph and the resume-table row that routes a plan back to Execute. Both are re-anchored so the count is over *task boxes* (lines matching `^[[:space:]]*[-*+] \[ \]`, all three markdown bullet markers) rather than over the raw `- [ ]` token wherever it appears in prose. **Defect 1 (the predicate counts markup it should not) ships.** **Defect 2 (real task boxes going unticked) is a no-change call** — the measured data shows it is a historical artifact the defect-1 fix subsumes, not a live bookkeeping failure. The Stage 3 **Bookkeeping** bullet is left exactly as-is.

The change is applied to the **mirrored pipeline `SKILL.md` pair** (`dev-flow` and `dev-flow-worktree`), which `scripts/check-sync.py` does **not** cover — so both copies are edited by hand and cross-verified against something outside the pair (this issue's intent, and the measured plan corpus).

## What was verified before designing

Base captured once and reused: `base=$(git rev-parse origin/main)` (validated non-empty). On this branch `HEAD == origin/main == 60bc8caac61458f29ed5a4e2c99be379389d279a` — the feature branch carries no commits yet, so every number below, measured at `$base`, describes the pre-edit tree. Each claim gives the command that printed it, in the past tense at `$base`.

- **The predicate is unsatisfiable by construction.** `superpowers:writing-plans` emits a fixed blockquote header into every plan whose first line is a `> **For agentic workers:** …` blockquote containing `` `- [ ]` `` inside an inline code span (documentation of the checkbox syntax). `git show "$base:<plan>" | grep -c 'REQUIRED SUB-SKILL'` returned `1` for **all 18** plans under `docs/superpowers/plans/`. So a raw `grep -c -- '- \[ \]'` floors at ≥1 on any plan that still carries the header, and the current predicate ("zero `- [ ]` remain") can never reach zero.
- **How wide the false floor is.** Over the 18 plans at `$base`, `grep -c -- '- \[ \]'` returned ≥1 for **16** of them; the current predicate would report all 16 as never-complete. The **2** exceptions (`2026-08-02-gh-30-flat-topology-plan.md`, `2026-08-03-gh-48-version-collision-plan.md`) return 0 only because their authors *hand-contorted the prose to avoid spelling a literal `- [ ]`* — gh-30's header reads, verbatim, "This sentence deliberately does not spell an empty checkbox: … a literal one here would keep that predicate false forever." That workaround is direct evidence the bug is known and is already costing authors effort; the fix removes the need for it.
- **The line-anchored count is the real signal.** `grep -cE '^[[:space:]]*- \[ \]'` counts a `- [ ]` at line start (optionally indented) and excludes every prose-embedded token — the blockquote header, and `- [ ]` inside inline code spans in prose bullets. Representative measurements at `$base` (`raw` = `grep -c -- '- \[ \]'`, `anchored` = `grep -cE '^[[:space:]]*- \[ \]'`):

  | Plan | raw | anchored | the "extra" raw tokens are |
  |---|---|---|---|
  | `2026-08-02-gh-38-marker-framing-plan.md` | 3 | 0 | header + two prose bullets quoting the predicate in code spans |
  | `2026-08-02-gh-28-29-review-prose-plan.md` | 2 | 0 | header + one prose bullet in a code span |
  | `2026-07-20-dev-flow-plan.md` | 34 | 32 | header + one code-span token; 32 are genuine unticked boxes |
  | `2026-07-22-dev-flow-nested-review-fix.md` | 25 | 24 | header; 24 are genuine unticked boxes |
  | `2026-07-28-gh-16-terminology-collision-plan.md` | 27 | 26 | header; 26 are genuine unticked boxes |

- **Defect 2 is historical, not live.** Exactly **3** plans have any genuinely-unticked task box under the anchored count — `2026-07-20-dev-flow-plan.md` (32), `2026-07-22-dev-flow-nested-review-fix.md` (24), `2026-07-28-gh-16-terminology-collision-plan.md` (26), the three plans that predate the current tick-and-commit discipline — the two that built dev-flow itself, plus the `gh-16` terminology fix. **Every** plan produced under that discipline (all recent `gh-*` plans) has `anchored == 0` *and* a positive count of *ticked* boxes — so its task boxes existed and were checked, not merely never added; only the raw count was wrong. Two commands per plan confirm this: `git show "$base:<plan>" | grep -cE '^[[:space:]]*- \[ \]'` (unticked) returned non-zero for only those three, and `git show "$base:<plan>" | grep -cE '^[[:space:]]*- \[x\]'` (ticked) returned 0 for exactly those same three and a value from 14 to 64 on every disciplined plan (e.g. 27 on `2026-08-02-gh-24-design-block-reader-plan.md`). So the issue's "tick-and-commit bookkeeping isn't firing" is refuted for every disciplined plan; the appearance of unticked tasks was the raw count misattributing prose tokens.
- **The two target sites, per file.** `git grep -nE 'Execution is complete|≥1 unchecked' -- plugins/` returned exactly two lines in each file: the **Execution-complete signal** paragraph and the resume-table row. `plugins/dev-flow/skills/dev-flow/SKILL.md:169` / `:195`; `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md:163` / `:189`. No other site in either file references the count predicate — a claim corrected by gh-63: the sibling "Plan fully checked" resume row directly below the anchored Execute row also expresses the count predicate, in different words that the phrase-grep `Execution is complete|≥1 unchecked` structurally cannot match, so this claim was a measurement blind spot, now fixed. The Stage 3 **Bookkeeping** bullet (`:239` / `:233`) mentions *ticking* (the action) but no count, so it is untouched.
- **The two paragraphs differ only in one parenthetical.** The `dev-flow` paragraph ends its bolded clause with "(it is git-ignored and is **not durable pipeline state**)"; the `dev-flow-worktree` one with "(it is git-ignored and **dies with the worktree**)". They are therefore *not* pure substitution images, so a full replacement paragraph is given for each. The resume-table row is **byte-identical** between the two files: `git show "$base:plugins/dev-flow/skills/dev-flow/SKILL.md" | sed -n '191p'` and the worktree `:185` produced the same bytes.
- **`check-sync.py` does not cover this pair.** `MIRROR_PAIRS` in `scripts/check-sync.py` holds `adversarial-review` (SKILL + two agent bodies) and manifest descriptions only — not the pipeline `SKILL.md` pair. Baseline `python3 scripts/check-sync.py` exits 0 today; this edit touches neither the adversarial-review files nor any `description`, so it stays 0. The pipeline pair is the **hand-mirrored** kind (`CLAUDE.md` / `CONTEXT.md`): a one-sided edit here is caught by nothing mechanical, which is why the mirrored-pair obligation and the cross-checks below exist.
- **Version state.** `$base` is at `dev-flow` **2.12.0** and `dev-flow-worktree` **1.14.0** (`git show "$base:plugins/<name>/.claude-plugin/plugin.json"`); the working tree matches.

## Decomposition check

One issue, one concept (what the completion count is *of*), two files that are hand-mirrors, one version-bump pair. The write side (SDD ticks boxes, Stage 3) and the read side (the resume table and the Execution-complete signal consume the count) are two halves of one contract and move together. Nothing spans independent subsystems. **No split.**

## Root cause

The Artifact Contract defines the execution-complete signal as a count of the raw token `- [ ]` anywhere in the plan text. But `- [ ]` is not exclusive to task checkboxes: `writing-plans` documents the syntax in a blockquote header (`> … checkbox (`- [ ]`) syntax …`), and plan prose routinely quotes the token inside inline code spans. None of those are ticked by anything, so the raw count has a permanent floor of ≥1 on any plan carrying the header — and the predicate "zero `- [ ]` remain" is unsatisfiable by construction. Execute can never report complete. The token is being used as if it were a task marker when it is really a *character sequence that also appears in documentation*.

## Defect 1 — the fix: line-anchor the count

**Chosen: line-anchoring.** Redefine the count as *unchecked task boxes* = lines matching `^[[:space:]]*[-*+] \[ \]` (a task checkbox at line start, optionally indented — markdown's `-`, `*`, and `+` bullets each render a checkbox). `writing-plans` emits every real task step as such a line; every false token measured in the corpus is either blockquote-prefixed (`> …`) or embedded mid-line inside an inline code span, and the `^…[-*+] \[ \]` anchor excludes all of them. This captures the entire observed defect — across all 18 plans, anchoring drops the count to exactly the genuine unticked boxes — with a one-line change to a prose predicate the orchestrator already interprets, and no new tooling in a repo whose only scripts are three tiny checkers.

**Why `[-*+]`, not just `-`.** The corpus is 100% `-` bullets (all 18 plans; `writing-plans` hardcodes `- [ ]` in its template), so the investigation above measured `-` and on today's plans `[-*+]` and `-` count identically — verified on every plan. The marker class is widened anyway, because the under-count a `-`-only anchor risks fails in the *dangerous* direction while the guard against it is free. A real task step written with a `*` or `+` bullet — a future `writing-plans` version, a hand-edited plan, or a plan from another tool — is a genuine unticked box that a `-`-only anchor silently drops; drop the last such box and the count floors at zero, a false "execution complete" that advances the pipeline past Execute with unfinished work (auto-merge of incomplete work is the pipeline's worst failure mode). Widening to `[-*+]` can only ever raise the count, never lower it, so it introduces no new false-complete, and adds no false-positive class — a line-start `* [ ]` / `+ [ ]` renders as a checkbox exactly as `- [ ]` does, and the documented false tokens (blockquote header, inline code spans) are all `-` and all still excluded by the line anchor. This is the same fix-cost-versus-failure-direction test the Residual below applies, reaching the opposite verdict there because that fix is expensive (a parser) and its failure is safe; here the fix is one character class and the failure is dangerous.

**Rejected — full markdown-aware fence/code-span stripping.** A parser that strips fenced code blocks and inline code spans before counting would additionally catch a *line-start* `- [ ]` sitting inside a fenced code block. Rejected: that residual occurs in **zero** current plans (`writing-plans` never emits a task box inside a fence), so the parser buys nothing measurable while adding a real parser to a prose predicate — over-engineering for the one theoretical case, and the case fails safe anyway (see Residual). Line-anchoring is strictly the right altitude here.

**Rejected — edit the upstream `writing-plans` boilerplate.** We do **not** own `superpowers:writing-plans`; we cannot change what header it emits. Even if we could, it would fix only the one blockquote token, leaving the inline-code-span tokens in plan prose (e.g. gh-28-29's "Execution is complete when zero `- [ ]` boxes remain") still inflating the raw count. The predicate must be robust to *any* prose that mentions the token, which only anchoring on our own side achieves.

## Defect 2 — the call: no change

**No prose change, and specifically no change to the Stage 3 Bookkeeping bullet.** The issue frames "real task boxes are going unticked" as a second, separable bookkeeping failure. The data refutes that framing: every plan executed under the current tick-and-commit discipline has `anchored == 0` — the boxes were ticked and committed correctly; the raw count merely misattributed prose tokens to unticked tasks. The only three plans with genuinely-unticked anchored boxes predate the discipline entirely. The tick-and-commit machinery *is* firing. The defect-1 anchored fix subsumes defect 2 for every plan going forward, and there is no live bookkeeping bug to fix. Changing the Bookkeeping bullet would be "fixing" a bug the evidence says does not exist — motion, not improvement. **Recorded call: defect 2 needs no edit; the anchored count is the whole fix.**

## Residual edge case (accepted, documented)

A task checkbox at line start (bullet `-`, `*`, or `+`) *inside a fenced code block* would still match `^[[:space:]]*[-*+] \[ \]`. Accepted as a residual rather than parsed away because: (i) `writing-plans` emits no task box inside a fence and zero current plans contain one; (ii) full fence-awareness needs a parser — the wrong altitude for an orchestrator-interpreted prose predicate; and (iii) the failure direction is safe — an over-count keeps the run *in* Execute (it never reports a false "complete" and never merges unfinished work). The SKILL.md prose names this residual so the orchestrator, reading the predicate, treats such a line as documentation.

## Exact replacement text

Four whole-line replacements. The blocks below are the design's only plain (untagged) fenced blocks, in document order — **shape `[1, 1, 1, 1]`** for `scripts/design_blocks.py`. Each replaces the entire current line at its named anchor; the surrounding paragraph/table is otherwise unchanged.

**Block [0] — replaces `plugins/dev-flow/skills/dev-flow/SKILL.md:165` (the `**Execution-complete signal.**` paragraph):**

```
**Execution-complete signal.** When a task's review comes back clean, the orchestrator (SDD's controller) ticks that task's `- [ ]` checkboxes in the plan file and commits them, alongside SDD's ledger append. **Committed checkboxes are the durable, authoritative cross-session signal; SDD's `.superpowers/sdd/progress.md` ledger stays in-session scratch (it is git-ignored and is not durable pipeline state).** Execution is complete if and only if the plan at branch tip has zero unchecked task boxes — lines matching `^[[:space:]]*[-*+] \[ \]` (a task checkbox at line start, optionally indented; markdown's `-`, `*`, and `+` bullets all render a checkbox, so all three count). The count is line-anchored, not a raw token count: a `- [ ]` inside an inline code span or a blockquote line — such as the `writing-plans` header that documents the checkbox syntax — is documentation of the syntax, not a task, and the anchor excludes it. (A line-start task checkbox inside a fenced code block would still match; `writing-plans` emits none, and even if one appeared, over-counting only keeps Execute running rather than ever signalling a false complete.) Tie-break: if `git log` shows a task's commits but its boxes are unticked (a crash in the gap), verify via `git log`, tick the boxes, and do not re-implement.
```

**Block [1] — replaces `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md:159` (the `**Execution-complete signal.**` paragraph; identical to Block [0] except the bolded parenthetical, per the worktree wording):**

```
**Execution-complete signal.** When a task's review comes back clean, the orchestrator (SDD's controller) ticks that task's `- [ ]` checkboxes in the plan file and commits them, alongside SDD's ledger append. **Committed checkboxes are the durable, authoritative cross-session signal; SDD's `.superpowers/sdd/progress.md` ledger stays in-session scratch (it is git-ignored and dies with the worktree).** Execution is complete if and only if the plan at branch tip has zero unchecked task boxes — lines matching `^[[:space:]]*[-*+] \[ \]` (a task checkbox at line start, optionally indented; markdown's `-`, `*`, and `+` bullets all render a checkbox, so all three count). The count is line-anchored, not a raw token count: a `- [ ]` inside an inline code span or a blockquote line — such as the `writing-plans` header that documents the checkbox syntax — is documentation of the syntax, not a task, and the anchor excludes it. (A line-start task checkbox inside a fenced code block would still match; `writing-plans` emits none, and even if one appeared, over-counting only keeps Execute running rather than ever signalling a false complete.) Tie-break: if `git log` shows a task's commits but its boxes are unticked (a crash in the gap), verify via `git log`, tick the boxes, and do not re-implement.
```

**Block [2] — replaces `plugins/dev-flow/skills/dev-flow/SKILL.md:191` (the resume-table row):**

```
| Plan at tip has ≥1 unchecked task box (a line matching `^[[:space:]]*[-*+] \[ \]`) | Execute — resume at first unchecked task (cross-check ledger + `git log`) |
```

**Block [3] — replaces `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md:185` (the resume-table row; byte-identical to Block [2] — the row is the same in both files):**

```
| Plan at tip has ≥1 unchecked task box (a line matching `^[[:space:]]*[-*+] \[ \]`) | Execute — resume at first unchecked task (cross-check ledger + `git log`) |
```

The second cell of the resume row (`Execute — resume at first unchecked task (cross-check ledger + `git log`)`) is preserved verbatim; only the trigger cell changes. Modulo the one documented parenthetical difference between Blocks [0] and [1], the edit is identical across the two files.

## Version bumps

Both plugin directories are touched (each carries an edited `SKILL.md`), so `scripts/check-version-bump.py` requires a bump ahead of `origin/main`'s tip for each. Bump the **minor** segment, past `origin/main` (not merely past this branch's base — a concurrent branch may have claimed the next number):

- `plugins/dev-flow/.claude-plugin/plugin.json`: `2.12.0` → **`2.13.0`**
- `plugins/dev-flow-worktree/.claude-plugin/plugin.json`: `1.14.0` → **`1.15.0`**

(Re-check both against `origin/main` at execute time; if `origin/main` has advanced past these numbers, bump past whatever it then publishes.)

## Mirrored-pair obligation

The pipeline `SKILL.md` pair is **hand-mirrored**, not machine-checked — `scripts/check-sync.py`'s `MIRROR_PAIRS` does not include it. Therefore **both** files must be edited (Blocks [0]+[2] into `dev-flow`, Blocks [1]+[3] into `dev-flow-worktree`), and the change must be cross-verified against something **outside** the pair, per `CLAUDE.md`'s *Verifying a change*: here that external check is (a) this issue's stated intent (the anchored predicate must exclude the boilerplate token) and (b) the measured plan corpus (the anchored grep returns the genuine unticked-box count on all 18 plans). A doubled-identical mistake would pass any pair-internal comparison, so the corpus demonstration is the load-bearing check.

## Success criteria / verification

No test suite exists in this repo; verification is greps, the design-block re-read, and the two checker scripts. Every git ref a criterion computes is captured, validated non-empty, and quoted (or passed as an `argv` element) — never an unguarded inline substitution (Command discipline). Capture once: `base=$(git rev-parse origin/main)` and halt if empty.

1. **Removed phrasing is gone (scoped to `plugins/`, since dated `docs/` records legitimately quote the old text).** Both return no hits:
   - `git grep -F -- 'Execution is complete if and only if zero' -- plugins/`
   - `git grep -F -- 'unchecked `- [ ]`' -- plugins/`

   (The surviving `` `- [ ]` `` in the Execution-complete paragraph is the *action* verb "ticks that task's `- [ ]` checkboxes", which is intended to remain — so the removal greps target the specific removed phrasings, not the bare token.)

2. **New phrasing landed in both files (design-block re-read, not retyped).** A per-change `python3` check that `sys.path.insert(0, "scripts")`, calls `read_blocks("docs/superpowers/specs/2026-08-03-gh-58-completion-predicate-design.md", [1, 1, 1, 1])` (run `python3 scripts/design_blocks.py <this design>` first to confirm the shape is `[1, 1, 1, 1]`), and asserts: Block [0] appears verbatim in `plugins/dev-flow/skills/dev-flow/SKILL.md`; Block [1] in `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`; Block [2] in the `dev-flow` file; Block [3] in the `dev-flow-worktree` file. Additionally assert each touched file is byte-for-byte its `$base` blob with exactly these two line replacements applied and nothing else changed.

3. **The anchored predicate demonstrably excludes markup on real plans — this validates the predicate's *behavior*, not that the edit landed.** It runs against `$base`, the pre-edit tree, so it returns the same numbers whether or not the SKILL.md replacement is present; criterion #2 is what proves the replacement is in the files, and the shipped-literal criterion below ties the behavior proven here to the string that actually ships. Capture `base` as above; for a representative fully-ticked plan that carries the header — e.g. `p="docs/superpowers/plans/2026-08-02-gh-38-marker-framing-plan.md"` — show `git show "$base:$p" | grep -c -- '- \[ \]'` is `3` (old raw token count, non-zero: never-complete) while `git show "$base:$p" | grep -cE '^[[:space:]]*[-*+] \[ \]'` is `0` (new anchored count: complete). More generally, over all 18 plans the anchored count returns non-zero for exactly the three pre-discipline plans (`2026-07-20-dev-flow`=32, `2026-07-22-dev-flow-nested-review-fix`=24, `2026-07-28-gh-16`=26) and 0 for the rest — and the `[-*+]` marker class returns those identical numbers, since no plan in the corpus uses a `*` or `+` task bullet. This is the external, outside-the-pair check the mirrored edit is cross-verified against.

4. **`python3 scripts/check-sync.py` still exits 0.** The edit touches no `adversarial-review` file and no `description`; the pipeline pair is outside `MIRROR_PAIRS`, so sync is unaffected and must remain green.

5. **`python3 scripts/check-version-bump.py origin/main` exits 0.** Both plugins are touched and both are bumped ahead of `origin/main`'s tip (2.13.0, 1.15.0).

6. **`claude plugin validate .` passes** (the 8 missing-author warnings are expected).

7. **The regex string that ships equals the one criterion #3 validated (pins the literal, not just the block).** `git grep -F -- '^[[:space:]]*[-*+] \[ \]' -- plugins/` returns hits in **both** SKILL.md files — the Execution-complete paragraph and the resume-table row in each (four lines across the two files). That fixed string is character-for-character the anchored regex criterion #3 runs against the corpus, so the predicate that lands in the SKILL.md is the one proven correct on real plans. This closes the gap criteria #1–#3 leave open: criterion #2 proves only block==file (a typo mistyped identically into the design block, and thus into both files, satisfies it), and criterion #3 proves only that the literal *as typed in the criterion* behaves correctly — neither asserts the shipped string equals the validated one. `-F` (fixed-string) is required: the literal is entirely regex metacharacters.

## Out of scope

- No change to `writing-plans` (upstream, unowned) and no change to the blockquote header it emits.
- No change to the Stage 3 **Bookkeeping** bullet or any other paragraph — defect 2 is a no-change call.
- No new tooling: the predicate stays orchestrator-interpreted prose; no fence-parsing script is added.
- The three pre-discipline plans' genuinely-unticked boxes are historical records and are **not** to be retro-ticked.

## Assumptions

- **`writing-plans` continues to emit real task steps as a line-start task checkbox (bullet `-`, `*`, or `+`, optionally indented) and never inside a fenced code block.** Today the corpus is 100% `-` (all 18 plans; the skill's template hardcodes `- [ ]`), but the anchor matches all three markdown bullet markers, so the predicate stays correct — and stays safe in the dangerous direction — if that ever changes. If a future `writing-plans` version emitted task boxes inside fences, the residual above would apply (fail-safe: over-count, stay in Execute).
- **The orchestrator evaluates the predicate by the anchored regex, treating a fenced-block token as documentation.** Consistent with the predicate already being orchestrator-interpreted prose; the mechanical `grep -cE '^[[:space:]]*[-*+] \[ \]'` is the demonstration used in success criteria.
