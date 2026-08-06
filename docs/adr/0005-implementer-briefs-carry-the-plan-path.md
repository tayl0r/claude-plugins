# dev-flow's Execute stage hands each implementer the plan path, so out-of-section references resolve

Both pipelines execute a plan through `superpowers:subagent-driven-development` (SDD), whose `scripts/task-brief` hands each implementer only the text of its own `## Task N` section — no plan-file path, and nothing from `## Global Constraints` or any shared section. So when a task step leans on something defined outside its section — a shared `§V` verification block, a bare `§`/`§V` ID, "the table above", another task's output — the implementer receives an unresolvable label and silently substitutes a weaker check. The failure is invisible: not a wrong edit a diff catches, but a plausible substitute that passes. This seam was hit by two or more prior plans in this repo.

gh-45 (PR #64) added two prose defenses at plan-authoring time: a Stage 2 rule requiring the plan author to make each `## Task N` section self-sufficient (inline any cross-section reference, or name it in-section by the plan's absolute path with a read-verbatim clause), and a one-line sharpening of the `adversarial-review` plan-mode reviewer. Both are non-mechanical: they rely on the plan author remembering to carry the resolver into every referencing section.

## Decision

Fix the cause, at the seam this repo actually controls. dev-flow's orchestrator is SDD's controller — in Stage 3 it invokes SDD in-context and composes each implementer brief itself. So the Execute stage now instructs the orchestrator to include in every implementer brief the plan's absolute path plus a clause: this brief is an extract of one task section; any step referencing a block, table, ID, or section defined outside it must be resolved verbatim from the plan file at that path, never reconstructed or substituted; if the plan file cannot be read, stop and report. The resolver is thereby present at the point of use on every brief, so correctness no longer depends on the plan author anticipating every reference — the fix is correct-by-default.

This is a deliberate, scoped exception to SDD's "don't make a subagent read the plan file" anti-pattern: the implementer opens the plan only to resolve a specific out-of-section reference, never for general context, so SDD's context isolation holds everywhere else. dev-flow already documents several scoped deviations from SDD — suppressing the final whole-branch review, overriding the exit condition, owning the checkbox bookkeeping — and this is another, recorded here so it reads as intentional rather than a leak.

The rule lives in both pipeline `SKILL.md` files (a hand-mirrored pair, not machine-checked). dev-flow's implementer works in the repo-root checkout and dev-flow-worktree's in the pipeline worktree, so the bullet is phrased tree-agnostically — it names "the tree each implementer works from", true of both — and a single byte-identical bullet serves both files, leaving no per-file wording for the hand-mirror to drift.

## How this composes with gh-45

The Stage 2 self-sufficiency rule and this Stage 3 briefing rule are layered defenses of two different properties, not redundant defenses of one. Stage 2 optimizes context cleanliness: the authored ideal, honoring SDD's deliberate context isolation, is that an implementer needs no plan-file access at all. Stage 3 optimizes correctness: the safety net for when that ideal is not met, so a forgotten reference resolves instead of silently degrading. The two fire at different times (plan authoring versus task dispatch), on different agents, and a run applies both. Stage 2 remains the authored ideal and is left unchanged; the safety net does not license weakening it.

## Considered options

- **A mechanical in-repo linter** that reimplements `task-brief`'s extraction and flags task sections carrying unresolved cross-references — rejected. The reference vocabulary is open-ended natural language, and the same token shapes (`§V`, "Task 3", "the table above") appear constantly in benign dependency documentation and architecture prose. Telling a load-bearing unresolvable instruction from a documented dependency is semantic, not lexical, so a regex gate either floods false positives (tuned loose, training operators to bypass it) or misses novel phrasings (tuned tight). A symptom-detector here is worse than the wart it chases; the correct-by-default guarantee comes from supplying the missing context, not from detecting its absence.
- **Editing `scripts/task-brief` upstream** so every brief carries the plan path (or fails on an unresolved reference) — the platonic fix, since every SDD user would inherit it, and the ideal seam. Rejected as unreachable here: `task-brief` is an external superpowers artifact this repo cannot edit. Escalating it upstream is recorded as a tracked follow-up.
- **ADR-only, or just closing the issue** — rejected: it leaves the latent regression (the plan author must remember) in place when a reachable, correct-by-default fix exists inside dev-flow's own controller.

## Consequences

The correct-by-default fix lives at dev-flow's controller seam, one layer below the platonic `task-brief` seam. The upstream `task-brief` edit remains the ideal home and is a tracked follow-up; until it lands, dev-flow carries the fix for its own runs. The gh-45 Stage 2 self-sufficiency rule remains in place as the authored ideal — this ADR does not retire it. Because the rule is duplicated in a hand-mirrored `SKILL.md` pair, the two copies must move together, and a change touching one carries its own verification per `CLAUDE.md`'s Verifying a change.

## Revisit when

`scripts/task-brief` gains the plan path (or an unresolved-reference gate) upstream. At that point every implementer brief carries the context regardless of controller, and the Stage 3 rule becomes belt-and-braces — keep it only while dev-flow still supports SDD versions whose `task-brief` predates the change.
