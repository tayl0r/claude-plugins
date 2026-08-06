---
dev-flow:
  slug: gh-65-brief-plan-path
  stops: [pre-merge]
  docs: commit
---

# gh-65 — the Execute stage hands each implementer the plan path, so an out-of-section reference resolves instead of silently degrading

## Summary

dev-flow's Stage 3 runs a plan through `superpowers:subagent-driven-development` (SDD), which briefs each implementer one task at a time via `scripts/task-brief` — handing over **only** the text between a plan's `## Task N` heading and the next task heading, with **no plan-file path and nothing from `## Global Constraints` or any shared section**. So a task step that references something defined *outside* its own section (a shared `§V` verification block, "the table above", another task's output) reaches the implementer as a bare, unresolvable label, and the implementer **silently substitutes a weaker check**. The failure is invisible — not a wrong edit a diff catches, but a plausible substitute that passes. This seam was hit by 2+ prior plans.

gh-45 (PR #64, shipped) added two **prose** defenses at plan-authoring time: a Stage 2 rule telling the plan author to make each `## Task N` section self-sufficient, and a one-line sharpening of the `adversarial-review` plan-mode reviewer. Both are non-mechanical — they depend on the plan author remembering to carry the read-verbatim clause into every referencing section.

This design records the **cause-fix** at the one seam this repo actually controls: **dev-flow's orchestrator is SDD's controller**, and in Stage 3 it composes each implementer brief itself. So a new Stage 3 override makes the orchestrator include in *every* implementer brief the plan's absolute path plus a resolve-out-of-section-references-verbatim clause. The read-verbatim clause rides on every brief, so correctness stops depending on the plan author anticipating each reference — it is **correct-by-default**.

The change is: one new Stage 3 bullet — byte-identical in both, phrased tree-agnostically — added to each of the two hand-mirrored pipeline `SKILL.md` files after that file's own `Baseline` anchor, a new ADR (0005), and the two plugin version bumps. Stage 2's gh-45 rule is left **verbatim** (reasoning below). No `task-brief` edit — it is external and out of reach.

## The seam (given, not re-derived)

- `superpowers:subagent-driven-development`, `scripts/task-brief`, and `implementer-prompt.md` are **external superpowers-plugin artifacts**, not in this repo, and cannot be edited by this change. gh-45's design confirmed `find . -iname '*task-brief*'` returns nothing.
- `task-brief` extracts only the `## Task N` section; the implementer prompt carries no plan-file path; SDD names "Make subagent read plan file (provide full text instead)" as an anti-pattern. These are the issue's confirmed facts, treated as given.
- gh-45 measured the concrete instance: the gh-32-33 plan's Task 2 brief carried multiple `§V` IDs and **zero** copies of the plan path from which they could be resolved (the resolution instruction lived only in `## Global Constraints` and a `## Verification scripts` preamble — both stripped by `task-brief`). Not re-run here; it is the shipped record in `docs/superpowers/specs/2026-08-03-gh-45-plan-cross-task-refs-design.md`.

## The decision (made; recorded, not re-litigated)

Issue #65 frames a **binary** — either raise the fix upstream in `task-brief`, or accept gh-45's local prose and close. That binary is **false**: it overlooked a third, reachable option. dev-flow's orchestrator *is* SDD's controller — in Stage 3 it invokes SDD in-context and spawns/briefs the implementer leaves itself, composing each brief (the `## Context` and `Work from:` fields of superpowers' `implementer-prompt.md`). So the cause-fix — always hand the implementer the plan's absolute path plus a "resolve any out-of-section reference verbatim from there" instruction — is reachable **inside dev-flow's own Stage 3 override**, with no external edit.

**Chosen — a Stage 3 "Implementer briefing" override in both pipeline `SKILL.md` files.** The orchestrator, as SDD's controller, includes in every implementer brief the plan's absolute path (in the tree that implementer works from) and a clause: this brief is an extract of one task section; any step referencing a block/table/`§`/`§V` ID/section defined outside it must be read verbatim from the plan file at that path, never reconstructed or substituted; if the plan file cannot be read, stop and report. Correct-by-default: the read-verbatim clause is present at the point of use, so correctness no longer depends on the plan author anticipating every reference.

**Rejected — a mechanical in-repo linter** that reimplements `task-brief`'s extraction and flags task sections with unresolved cross-references. The reference vocabulary is open-ended natural language, and the same token shapes (`§V`, "Task 3", "the table above") appear constantly in benign documentation (`- Consumes: … (Task 3)`, architecture prose). Distinguishing a load-bearing unresolvable instruction from dependency documentation is **semantic, not lexical** — a regex gate either floods false positives (tuned loose, training operators to bypass it) or misses novel phrasings (tuned tight). A symptom-detector here is worse than the wart; the correct-by-default guarantee comes from fixing the **cause** (missing context), not detecting the **symptom**.

**Rejected — edit `task-brief` upstream.** It is the platonic shared seam — every SDD user would inherit it, and it is the ideal home — but it is an external superpowers artifact this repo cannot edit. Recorded as the ideal seam; upstream escalation is tracked in #73 (no issue is filed on the superpowers repo itself).

**Rejected — ADR-only / just close #65.** Leaves the latent regression (the author must remember) in place when a reachable, correct-by-default fix exists.

## Composition with gh-45 (a reviewer will probe for redundancy)

The Stage 2 self-sufficiency rule and the new Stage 3 briefing rule are **not redundant defenses of the same property** — they are layered defenses of two different properties.

- **Stage 2 optimizes *context cleanliness*.** The authored ideal — honoring SDD's deliberate context isolation — is that an implementer needs **no** plan-file access at all: every reference is inlined or resolvable within the task section.
- **Stage 3 optimizes *correctness*.** It is the safety net for when the ideal is not met, so a forgotten reference **resolves** instead of silently degrading.

They fire at different times (plan authoring vs. task dispatch), on different agents, and a run applies both — exactly as gh-45 already layers its Stage 2 rule with the independent `adversarial-review` plan-mode check. Both earn their place.

**Decision on Stage 2's text: leave it verbatim — no change.** The smallest justified change is none. Reasoning:

1. Stage 2's rule is complete and correct on its own; its correctness does not *depend* on Stage 3 existing, so it needs no pointer to it.
2. A "by the way, there is also a safety net" cross-reference would couple two rules across two stages in a **hand-mirrored** pair — four insertion points instead of two — enlarging the drift surface for an editorial note that changes no run-time behavior.
3. The redundancy concern a future editor might raise (weaken Stage 2 believing Stage 3 covers it) is answered where durable rationale belongs — **the ADR's Consequences**, which records that the Stage 2 rule remains the authored ideal and is not retired. Per this repo's convention (memory: *maintenance rules go in CLAUDE.md, not SKILL.md*; and the general rule that rationale lives in ADRs), shipping "this is only a safety net" prose into `SKILL.md` would push editorial rationale into every pipeline invocation for no behavior change.

There is also no collision with the existing Stage 3 **Pre-answers** bullet: Pre-answers resolves a *plan-vs-code* conflict by escalating to the design doc; the new bullet resolves a *within-plan* reference the brief failed to carry. Different triggers, no overlap.

## The SDD scoped-exception (stated so it reads as intentional)

Superpowers SDD lists "Make subagent read plan file (provide full text instead)" as an anti-pattern. This fix is a **deliberate, scoped** exception: the implementer opens the plan file **only** to resolve a specific out-of-section reference verbatim — never for general context, so SDD's context isolation holds everywhere else. dev-flow already documents several scoped deviations from SDD (suppressing the final whole-branch review, the exit-condition override, owning the checkbox bookkeeping); this is another, and both the bullet and ADR 0005 name it as such.

## The change — exact `SKILL.md` text and anchors

Two pipeline `SKILL.md` files are edited. They are a **hand-mirrored pair** (`CLAUDE.md`: too divergent to machine-check with `scripts/check-sync.py`), so any divergence between them is silent. The briefing bullet is therefore phrased **tree-agnostically** — it names "the tree each implementer works from", true of both dev-flow's repo-root **checkout** and dev-flow-worktree's **pipeline worktree** — so a **single byte-identical bullet** is inserted into both files, carrying no per-file wording for the hand-mirror to drift. The two insertions still move together, each anchored on its own file's `Baseline` line.

The bullet is inserted as a **new bullet directly after the `## Stage 3 — Execute` `Baseline` bullet** in each file — the first override in that list, so the briefing rule reads before the per-task mechanics. Each insertion is anchored on the content of that file's `Baseline` line (unique in each file — `grep -c` returned 1 for each), not on a line number.

### Anchors — each file's own `Baseline` line

dev-flow (`plugins/dev-flow/skills/dev-flow/SKILL.md`) — insert the shared bullet immediately after this line:

```text
- **Baseline:** branch entry has already ensured setup (deps installed); run the baseline test suite before the first task. **A red baseline halts** — a CI-green merge gate can't be reached from a red baseline. SDD's `using-git-worktrees` workflow skill creates no worktree here — it reads dev-flow's declared "work in place" preference and does its setup/baseline in the current checkout (see Dispatching to Inherited Skills).
```

dev-flow-worktree (`plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`) — insert the shared bullet immediately after this line:

```text
- **Baseline:** worktree entry has already ensured setup (deps installed); run the baseline test suite before the first task. **A red baseline halts** — a CI-green merge gate can't be reached from a red baseline. (If SDD invokes `using-git-worktrees` itself, its Step-0 check finds the pipeline worktree and creates nothing — see Dispatching to Inherited Skills.)
```

### The shared bullet — block 0 (the design's only plain-block bullet)

Inserted verbatim as the next line after each file's `Baseline` anchor above:

```
- **Implementer briefing:** `scripts/task-brief` hands each implementer only its own `## Task N` section — no plan-file path — so, as SDD's controller, include in **every** implementer brief the plan's absolute path in the tree each implementer works from plus this clause: *this brief is an extract of one task section; if any step references a block, table, `§`/`§V` ID, or section defined outside it (including `## Global Constraints` or a shared verification block), read that material verbatim from the plan file at that path — never reconstruct or substitute it; if you cannot read the plan file, stop and report.* This is a deliberate, scoped exception to SDD's "don't make a subagent read the plan file" anti-pattern — the implementer opens the plan **only** to resolve a specific out-of-section reference, never for general context.
```

## The ADR — `docs/adr/0005-implementer-briefs-carry-the-plan-path.md` (created)

Next free ADR number is **0005** (`docs/adr/` holds 0001–0004). The file's full content is the design's **second plain fenced block** (block 1, 31 lines) — the Execute-stage authoring lifts it verbatim into the new file:

```
# dev-flow's Execute stage hands each implementer the plan path, so out-of-section references resolve

Both pipelines execute a plan through `superpowers:subagent-driven-development` (SDD), whose `scripts/task-brief` hands each implementer only the text of its own `## Task N` section — no plan-file path, and nothing from `## Global Constraints` or any shared section. So when a task step leans on something defined outside its section — a shared `§V` verification block, a bare `§`/`§V` ID, "the table above", another task's output — the implementer receives an unresolvable label and silently substitutes a weaker check. The failure is invisible: not a wrong edit a diff catches, but a plausible substitute that passes. This seam was hit by two or more prior plans in this repo.

gh-45 (PR #64) added two prose defenses at plan-authoring time: a Stage 2 rule requiring the plan author to make each `## Task N` section self-sufficient (inline any cross-section reference, or name it in-section by the plan's absolute path with a read-verbatim clause), and a one-line sharpening of the `adversarial-review` plan-mode reviewer. Both are non-mechanical: they rely on the plan author remembering to carry the read-verbatim clause into every referencing section.

## Decision

Fix the cause, at the seam this repo actually controls. dev-flow's orchestrator is SDD's controller — in Stage 3 it invokes SDD in-context and composes each implementer brief itself. So the Execute stage now instructs the orchestrator to include in every implementer brief the plan's absolute path plus a clause: this brief is an extract of one task section; any step referencing a block, table, ID, or section defined outside it must be resolved verbatim from the plan file at that path, never reconstructed or substituted; if the plan file cannot be read, stop and report. The read-verbatim clause is thereby present at the point of use on every brief, so correctness no longer depends on the plan author anticipating every reference — the fix is correct-by-default.

This is a deliberate, scoped exception to SDD's "don't make a subagent read the plan file" anti-pattern: the implementer opens the plan only to resolve a specific out-of-section reference, never for general context, so SDD's context isolation holds everywhere else. dev-flow already documents several scoped deviations from SDD — suppressing the final whole-branch review, overriding the exit condition, owning the checkbox bookkeeping — and this is another, recorded here so it reads as intentional rather than a leak.

The rule lives in both pipeline `SKILL.md` files (a hand-mirrored pair, not machine-checked). dev-flow's implementer works in the repo-root checkout and dev-flow-worktree's in the pipeline worktree, so the bullet is phrased tree-agnostically — it names "the tree each implementer works from", true of both — and a single byte-identical bullet serves both files, leaving no per-file wording for the hand-mirror to drift.

## How this composes with gh-45

The Stage 2 self-sufficiency rule and this Stage 3 briefing rule are layered defenses of two different properties, not redundant defenses of one. Stage 2 optimizes context cleanliness: the authored ideal, honoring SDD's deliberate context isolation, is that an implementer needs no plan-file access at all. Stage 3 optimizes correctness: the safety net for when that ideal is not met, so a forgotten reference resolves instead of silently degrading. The two fire at different times (plan authoring versus task dispatch), on different agents, and a run applies both. Stage 2 remains the authored ideal and is left unchanged; the safety net does not license weakening it.

## Considered options

- **A mechanical in-repo linter** that reimplements `task-brief`'s extraction and flags task sections carrying unresolved cross-references — rejected. The reference vocabulary is open-ended natural language, and the same token shapes (`§V`, "Task 3", "the table above") appear constantly in benign dependency documentation and architecture prose. Telling a load-bearing unresolvable instruction from a documented dependency is semantic, not lexical, so a regex gate either floods false positives (tuned loose, training operators to bypass it) or misses novel phrasings (tuned tight). A symptom-detector here is worse than the wart it chases; the correct-by-default guarantee comes from supplying the missing context, not from detecting its absence.
- **Editing `scripts/task-brief` upstream** so every brief carries the plan path (or fails on an unresolved reference) — the platonic fix, since every SDD user would inherit it, and the ideal seam. Rejected as unreachable here: `task-brief` is an external superpowers artifact this repo cannot edit. Escalating it upstream is tracked in #73.
- **ADR-only, or just closing the issue** — rejected: it leaves the latent regression (the plan author must remember) in place when a reachable, correct-by-default fix exists inside dev-flow's own controller.

## Consequences

The correct-by-default fix lives at dev-flow's controller seam, one layer below the platonic `task-brief` seam. The upstream `task-brief` edit remains the ideal home and is tracked in #73; until it lands, dev-flow carries the fix for its own runs. The gh-45 Stage 2 self-sufficiency rule remains in place as the authored ideal — this ADR does not retire it. Because the rule is duplicated in a hand-mirrored `SKILL.md` pair, the two copies must move together, and a change touching one carries its own verification per `CLAUDE.md`'s Verifying a change.

## Revisit when

`scripts/task-brief` gains the plan path (or an unresolved-reference gate) upstream. At that point every implementer brief carries the context regardless of controller, and the Stage 3 rule becomes belt-and-braces — keep it only while dev-flow still supports SDD versions whose `task-brief` predates the change.
```

## Version bumps

Both edited `SKILL.md` files live inside plugin directories, so **both `plugin.json` versions bump the minor segment, past `origin/main`** (`CLAUDE.md`'s bump rule; the install cache is version-keyed). `scripts/check-version-bump.py origin/main` asks for a bump from every plugin whose directory the change touches — both are touched here. Confirmed current == `origin/main` while drafting (`git show origin/main:plugins/<p>/.claude-plugin/plugin.json | grep '"version"'`): `dev-flow` `2.16.0`, `dev-flow-worktree` `1.18.0`.

- `plugins/dev-flow/.claude-plugin/plugin.json`: `2.16.0` → **`2.17.0`**
- `plugins/dev-flow-worktree/.claude-plugin/plugin.json`: `1.18.0` → **`1.19.0`**

The ADR is under `docs/adr/`, not `plugins/`, so it carries no bump of its own. Re-confirm both targets against `origin/main` at implementation time — a concurrent branch may have published these numbers first; bump past `origin/main`, not past this branch's base.

## Blast radius / files touched

Exactly five files (the design/plan/ADR scaffolding under `docs/superpowers/` is committed by `docs: commit` and excluded from the change-scope check, per the pattern gh-45 uses):

1. `plugins/dev-flow/skills/dev-flow/SKILL.md` — the shared bullet (block 0) inserted after the dev-flow `Baseline` anchor; nothing removed.
2. `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` — the same shared bullet (block 0) inserted after the worktree `Baseline` anchor; nothing removed.
3. `docs/adr/0005-implementer-briefs-carry-the-plan-path.md` — created; content = block 1.
4. `plugins/dev-flow/.claude-plugin/plugin.json` — one line, `2.16.0` → `2.17.0`.
5. `plugins/dev-flow-worktree/.claude-plugin/plugin.json` — one line, `1.18.0` → `1.19.0`.

This is a single coherent change (one seam, one rule, its ADR, its bumps); it does not span independent subsystems, so no decomposition/HALT is warranted.

## Out of scope

- **Editing any external superpowers artifact** — `subagent-driven-development`, `scripts/task-brief`, `implementer-prompt.md`. Not in this repo; cannot be changed here. Upstream `task-brief` escalation is tracked in #73; this change files nothing on the superpowers repo.
- **Changing Stage 2's gh-45 rule text** — left verbatim (Composition analysis above). The gh-45 `adversarial-review` plan-mode sharpening is likewise untouched.
- **A mechanical linter / regex gate** for cross-references — rejected above.
- **`CLAUDE.md`** — this is a run-time pipeline rule, so it lives in `SKILL.md`; the durable rationale lives in the new ADR.

## Assumptions (defensible defaults; none blocking)

- **A1 — Insertion point is directly after the `Baseline` bullet, as the first Stage 3 override.** The briefing rule governs how each task's brief is composed, which precedes the per-task mechanics (Exit condition, Pre-answers, Halts, Bookkeeping). Anchored by the `Baseline` line's unique content, not a line number.
- **A2 — The briefing bullet is byte-identical in both files.** It is phrased tree-agnostically ("the tree each implementer works from"), so no per-file wording differs and the hand-mirrored pair cannot drift on it. `check-sync.py` does not compare this pair, so the byte-for-byte blob check plus the design-conformance check are the outside-the-pair verification.
- **A3 — Stage 2 stays verbatim.** Recorded as the smallest justified change (Composition analysis); the "authored ideal / not retired" record lives in ADR 0005's Consequences.
- **A4 — The clause names "the plan file at that path" generically**; the orchestrator substitutes the run's actual absolute plan path when composing each brief (the same substitution gh-45's Stage 2 rule already relies on). The rule hardcodes no path.
- **A5 — Version targets `2.17.0` / `1.19.0` are re-confirmed against `origin/main` at execute time.** If a concurrent branch published either number first, bump past that; `check-version-bump.py origin/main` is the gate.

## Verification (this repo has no test suite — these mechanical/derived checks are the whole correctness surface)

Run from the repo root on the feature branch. Every computed git ref is captured, validated non-empty, and passed to `git` as an `argv` element (never shell-interpolated) per `CLAUDE.md`'s Command discipline; the base ref for the diff/blob checks is the computed `git merge-base origin/main HEAD`, never a hardcoded SHA.

### 1. Design-block conformance — the two blocks landed verbatim from the design on disk

This design gives its edits as two plain fenced blocks, shape `[1, 31]` (block 0 the shared implementer-briefing bullet inserted into **both** files, block 1 the 31-line ADR). The check re-reads them through `scripts/design_blocks.py` — never retyped — and asserts each lands where intended: block 0 the line **immediately after** the dev-flow `Baseline` anchor **and** the line immediately after the worktree `Baseline` anchor (the same bullet in both), block 1 the full content of the created ADR. `read_blocks(DESIGN, [1, 31])` is itself the shape guard: it exits non-zero if the design's plain-block shape ever moves off `[1, 31]` (e.g. the ADR is re-edited to a different line count). Smoke-test the shape first, then run the check:

```sh
python3 scripts/design_blocks.py docs/superpowers/specs/2026-08-05-gh-65-brief-plan-path-design.md   # expect: shape: [1, 31]
```

```python
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-05-gh-65-brief-plan-path-design.md"
b0, b1 = read_blocks(DESIGN, [1, 31])   # [1,31] guards the shape; b0 is the 1-line shared bullet, b1 is the 31-line ADR
ANCHOR_DF = '- **Baseline:** branch entry has already ensured setup (deps installed); run the baseline test suite before the first task. **A red baseline halts** — a CI-green merge gate can\'t be reached from a red baseline. SDD\'s `using-git-worktrees` workflow skill creates no worktree here — it reads dev-flow\'s declared "work in place" preference and does its setup/baseline in the current checkout (see Dispatching to Inherited Skills).'
ANCHOR_WT = '- **Baseline:** worktree entry has already ensured setup (deps installed); run the baseline test suite before the first task. **A red baseline halts** — a CI-green merge gate can\'t be reached from a red baseline. (If SDD invokes `using-git-worktrees` itself, its Step-0 check finds the pipeline worktree and creates nothing — see Dispatching to Inherited Skills.)'
DF = "plugins/dev-flow/skills/dev-flow/SKILL.md"
WT = "plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md"
ADR = "docs/adr/0005-implementer-briefs-carry-the-plan-path.md"

bad = []
def after_anchor(path, anchor, block_line):
    lines = Path(path).read_text(encoding="utf-8").split("\n")
    at = [i for i, l in enumerate(lines) if l == anchor]
    if len(at) != 1:
        bad.append("%s: anchor found %d times, want 1" % (path, len(at))); return
    nxt = lines[at[0] + 1] if at[0] + 1 < len(lines) else "<EOF>"
    if nxt != block_line:
        i = next((k for k in range(min(len(nxt), len(block_line))) if nxt[k] != block_line[k]),
                 min(len(nxt), len(block_line)))
        lo, hi = max(0, i - 20), i + 40
        bad.append("%s: line after anchor != block (got len=%d, want len=%d; first differ at char %d)\n    want %r\n    got  %r"
                   % (path, len(nxt), len(block_line), i, block_line[lo:hi], nxt[lo:hi]))

after_anchor(DF, ANCHOR_DF, b0[0])
after_anchor(WT, ANCHOR_WT, b0[0])
if not Path(ADR).exists():
    bad.append("%s: file not created" % ADR)
else:
    adr_lines = Path(ADR).read_text(encoding="utf-8").split("\n")
    if adr_lines and adr_lines[-1] == "":
        adr_lines.pop()
    if adr_lines != b1:
        bad.append("%s: file content != design block 1 (%d file lines vs %d block lines)" % (ADR, len(adr_lines), len(b1)))

for why in bad:
    print("MISMATCH:", why)
print("design-conformance:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
```

Expect `design-conformance: OK` and exit 0. Against the base tree (bullets not yet inserted, ADR absent) it reports mismatches and exits 1 — its demonstrated red form. Note what this check does **not** cover: it reads only the line after each anchor, so a stray edit *elsewhere* in a touched file passes it — the no-displacement property is check 2's byte-for-byte reconstruction, and the two compose (check 1: the blocks are right and correctly anchored; check 2: nothing outside them moved).

### 2. Byte-for-byte blob check + file scope — nothing else moved

Every touched file must be its merge-base blob with exactly the intended edit; the created ADR must be absent at the merge-base and equal block 1 byte-for-byte. This is the one check that proves no *other* line moved — the doubled-hunk blind spot the hand-mirrored pair cannot otherwise catch. It reads raw bytes via `verify_blob` (`blob`, `to_lines`, `reconstructed`), reconstructs each existing file as its base blob with the block spliced after its anchor (or the version line swapped), and compares. The changed set (excluding this run's own `docs/superpowers/` artifacts) must equal exactly the five files.

**Runs after the change is committed** (per the Verification-ordering cross-cutting rule): the file-scope check compares the merge-base to `HEAD` — `git diff --name-only <base> HEAD` lists a *created* file (the ADR), which `git diff <base>` against the working tree would not — and the `reconstructed` byte checks read the post-commit working tree, which equals `HEAD`. It is also **guarded onto that branch**: after capturing the merge-base it asserts `merge-base != HEAD` — HEAD must carry a commit beyond `origin/main` — so a stray run from `main` (or any checkout sitting at the merge-base) halts with a named diagnostic instead of a misleading all-five-files-missing scope failure. The assertion names no branch: the `<username>/<slug>` name is not knowable here, and "HEAD is ahead of the merge-base" is what "on the committed feature branch" means mechanically.

```python
import subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
from verify_blob import blob, to_lines, reconstructed

DESIGN = "docs/superpowers/specs/2026-08-05-gh-65-brief-plan-path-design.md"
b0, b1 = read_blocks(DESIGN, [1, 31])
DF = "plugins/dev-flow/skills/dev-flow/SKILL.md"
WT = "plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md"
ADR = "docs/adr/0005-implementer-briefs-carry-the-plan-path.md"
PJ_DF = "plugins/dev-flow/.claude-plugin/plugin.json"
PJ_WT = "plugins/dev-flow-worktree/.claude-plugin/plugin.json"
WANT = sorted([DF, WT, ADR, PJ_DF, PJ_WT])
BUMPS = {PJ_DF: ("2.16.0", "2.17.0"), PJ_WT: ("1.18.0", "1.19.0")}
ANCHOR_DF = '- **Baseline:** branch entry has already ensured setup (deps installed); run the baseline test suite before the first task. **A red baseline halts** — a CI-green merge gate can\'t be reached from a red baseline. SDD\'s `using-git-worktrees` workflow skill creates no worktree here — it reads dev-flow\'s declared "work in place" preference and does its setup/baseline in the current checkout (see Dispatching to Inherited Skills).'
ANCHOR_WT = '- **Baseline:** worktree entry has already ensured setup (deps installed); run the baseline test suite before the first task. **A red baseline halts** — a CI-green merge gate can\'t be reached from a red baseline. (If SDD invokes `using-git-worktrees` itself, its Step-0 check finds the pipeline worktree and creates nothing — see Dispatching to Inherited Skills.)'

def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s" % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout

base = git("merge-base", "origin/main", "HEAD").strip()
if not base:
    raise SystemExit("empty merge-base -- refusing to run a HEAD-relative scope check")
head = git("rev-parse", "HEAD").strip()
if base == head:
    branch = git("rev-parse", "--abbrev-ref", "HEAD").strip()
    raise SystemExit(
        "merge-base equals HEAD -- HEAD carries no commit beyond origin/main, so this "
        "HEAD-relative scope check is not running on the committed feature branch "
        "(currently on %r). Run it from the feature branch after the change is committed." % branch)

fail = []
changed = sorted(p for p in git("diff", "--name-only", base, "HEAD", "--", ".", ":!docs/superpowers/").split("\n") if p)
if changed != WANT:
    for p in sorted(set(changed) - set(WANT)): fail.append("unexpected file: " + p)
    for p in sorted(set(WANT) - set(changed)): fail.append("missing file:   " + p)

def splice_after(base_bytes, anchor, block_line):
    lines = to_lines(base_bytes)
    at = [i for i, l in enumerate(lines) if l == anchor]
    if len(at) != 1:
        raise SystemExit("anchor found %d times at base, want 1" % len(at))
    return lines[:at[0] + 1] + [block_line] + lines[at[0] + 1:]

for path, anchor, block_line in ((DF, ANCHOR_DF, b0[0]), (WT, ANCHOR_WT, b0[0])):
    base_bytes = blob(base, path)
    problems = reconstructed(path, splice_after(base_bytes, anchor, block_line), base_bytes)
    if problems:
        fail.append("%s: %s" % (path, problems[0]))

for path, (old_v, new_v) in BUMPS.items():
    base_bytes = blob(base, path)
    lines = to_lines(base_bytes)
    vlines = [i for i, l in enumerate(lines) if '"version"' in l]
    if len(vlines) != 1:
        raise SystemExit("%s: %d version lines at base, want 1" % (path, len(vlines)))
    i = vlines[0]
    if old_v not in lines[i]:
        raise SystemExit("%s: base version line %r does not contain %r" % (path, lines[i], old_v))
    new_lines = lines[:i] + [lines[i].replace(old_v, new_v)] + lines[i + 1:]
    problems = reconstructed(path, new_lines, base_bytes)
    if problems:
        fail.append("%s: %s" % (path, problems[0]))

# created ADR: absent at base, working tree equals block 1 byte-for-byte
absent = subprocess.run(("git", "cat-file", "-e", "%s:%s" % (base, ADR)), capture_output=True)
if absent.returncode == 0:
    fail.append("%s: expected absent at merge-base, but it exists there" % ADR)
want_bytes = ("\n".join(b1) + "\n").encode("utf-8")
adr_path = Path(ADR)
if not adr_path.exists():
    fail.append("%s: file not created" % ADR)
elif adr_path.read_bytes() != want_bytes:
    fail.append("%s: working-tree bytes != block 1 joined with trailing newline" % ADR)

for why in fail:
    print("SCOPE FAIL:", why)
print("file scope + byte-for-byte:", "FAIL" if fail else "OK")
sys.exit(1 if fail else 0)
```

Expect `file scope + byte-for-byte: OK` and exit 0. A stray edit to any other file, an extra line in any touched file, a mistyped block, or an ADR that differs from block 1 fails and is named.

### 3. Removed-phrase grep

The `SKILL.md` insertions and the ADR are **additive / newly created** — they remove no prose, so the removed-phrase grep is N/A for those three files (stated per `CLAUDE.md`). The only removed strings are the two old version literals; each is file-scoped (version numbers recur in dated `docs/superpowers/` history, so a repo-wide grep would false-positive):

```sh
git grep -F '"version": "2.16.0"' -- plugins/dev-flow/.claude-plugin/plugin.json           # after the edit: expect 0 (it is 1 at base)
git grep -F '"version": "1.18.0"' -- plugins/dev-flow-worktree/.claude-plugin/plugin.json   # after the edit: expect 0 (it is 1 at base)
```

### 4. Sync, version-bump, and marketplace validation

```sh
python3 scripts/check-sync.py                       # expect: pass (adversarial-review pairs + author counts untouched; SKILL pair is hand-mirrored, not compared)
python3 scripts/check-version-bump.py origin/main   # expect: pass (both touched plugins ahead of origin/main)
claude plugin validate .                            # exits 0 with exactly the expected author-less warnings; do NOT add author keys
```

## Spec self-review

- **Placeholders:** none. `<abs-path>`-style wording is deliberate generic prose in the bullets ("the plan file at that path"); the plan author/orchestrator substitutes the run's real path. No stray `TODO`/`<...>`.
- **Internal consistency:** ADR number (0005), filename (`0005-implementer-briefs-carry-the-plan-path.md`), version targets (`2.17.0` / `1.19.0`), the five touched files, the anchors, and the block shape `[1, 31]` agree across Summary, The change, The ADR, Version bumps, Blast radius, and Verification. The two anchors are the two files' own `Baseline` lines (each verified unique with `grep -c` = 1 while drafting).
- **Scope:** bounded and stated (five files; out-of-scope list). Single coherent change — no decomposition/HALT.
- **Ambiguity:** the one real tension (does Stage 2 need a cross-reference?) is resolved explicitly with reasoning; the SDD anti-pattern and the gh-45 redundancy concern are addressed head-on. No blocking ambiguity → no HALT.
- **Every fenced replacement/insertion block is exact and anchored:** block 0 is a single shared line inserted after each file's unique `Baseline` anchor; block 1 is the created ADR's full content. Both are re-read from the design on disk by Verification step 1, never retyped downstream.
- **Measurements are derived:** the block shape `[1, 31]` is a claim about this design's own replacement text, asserted as a success criterion (Verification step 1's smoke-test prints it), not a pre-derived tree measurement. The base versions `2.16.0` / `1.18.0` were printed by `git show origin/main:… | grep '"version"'` while drafting; the anchor uniqueness by `grep -c` = 1. No number appears without the command that produced it.
