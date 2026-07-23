# dev-flow Nested-Review Fix — Implementation Plan

> **Superseded 2026-07-22 by `2026-07-22-dev-flow-flatten-design.md`** — nesting removed in Claude Code 2.1.218; dev-flow 1.2.0 flattened to orchestrator-driven fan-out. Retained for history.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. **Exception:** Task 1 must be run by the orchestrator/main session directly (see its note), not dispatched as an implementer subagent.

**Goal:** Make dev-flow's per-stage adversarial review always run its model-diverse reviewer subagents (sonnet seeds / fable resolvers) or halt loudly — never silently degrade to a single-model inline review — by editing two skill markdown files, verified by a capability probe.

**Architecture:** Prose edits to two Claude Code skill files. The "never silently inline" guarantee is layered across shared boundaries: the tool grant at the stage-dispatch seam; an integrity clause in the dispatch-prompt preamble (the one channel that reaches a stage subagent regardless of its toolset); model self-report; an orchestrator-checked provenance line forwarded through the dispatch seam; and a mandatory intake capability probe. A resolve-once/thread-always working-dir rule kills ambient-cwd reliance. No code, no test framework — verification is anchor-text grep + internal/cross-file consistency reads; the design's smoke test is end-to-end acceptance.

**Tech Stack:** Markdown skill files under `plugins/dev-flow/skills/`; `git`; the `Agent`/`Skill`/`EnterWorktree` harness tools (for the probe only).

## Global Constraints

- **Design source of truth:** `docs/superpowers/specs/2026-07-22-dev-flow-nested-review-fix-design.md`. Every edit's wording is finalized there; copy it, don't paraphrase loosely.
- **Skill edits touch only our own plugin:** `plugins/dev-flow/skills/dev-flow/SKILL.md` and `plugins/dev-flow/skills/adversarial-review/SKILL.md`. **Never modify `subagent-driven-development`** or any other `superpowers` skill. Doc edits are limited to the design/spec/plan files named in Tasks 1 and 7.
- **The "never inline" guarantee is dual-homed** (adversarial-review Contract *and* dev-flow dispatch preamble). Both are load-bearing; never deduplicate one away.
- **Model policy is unchanged and owned by adversarial-review's Model section:** seeds on `sonnet`, resolvers on `fable` (or `opus` when the session model is Fable-family). dev-flow refers to it *by reference*; it never redefines the selection. The model self-report *enforces* this policy; it must not alter it.
- **The capability probe is mandatory at every intake** (first run and resume) — not optional, not conditional on which resume row fires.
- **Version floor is documentation** (2.1.217, the verified-working version); enforcement is the capability probe.
- **Provenance line format** (shared interface — defined in Task 2, forwarded by Task 5's dispatch clause, checked in Task 6): `seeds: N× <tier>; resolvers: M× <tier>` where `<tier>` ∈ {`sonnet`, `fable`, `opus`} — the tier alias the review canonicalizes each reviewer's *self-reported* model to via its family match. Downstream checks are then trivial equality against the tier, not fuzzy name matching.
- **Keep spec, plan, and skill in lockstep:** Task 7 syncs the older `2026-07-20` spec + plan.
- **Acceptance:** the design doc's "Smoke test" (below, in Acceptance). It is a manual end-to-end run, gated after all tasks and after the installed plugin cache is re-synced.

---

### Task 1: Verify depth-2 worktree entry (the pending probe)

Confirms the one load-bearing capability the design marks "required before implementation": that a **depth-2** cwd-pinned agent (main → stage subagent → fixer) can enter the pipeline worktree and commit there. The result decides the mechanism Task 3 writes down; failure selects the `git -C` fallback (not a blocker).

> **Run this task from the main session (the orchestrator) directly — do NOT dispatch it as an implementer subagent.** The design's question is depth-2 (main → subagent → sub-subagent). If an already-dispatched SDD subagent ran it, the chain would be depth-3 and a depth-3 result cannot prove the depth-2 case.

**Files:**
- Modify: `docs/superpowers/specs/2026-07-22-dev-flow-nested-review-fix-design.md` (the "Evidence" section — turn the "Pending probe" note into a recorded result)

**Interfaces:**
- Produces: `PROBE_RESULT` ∈ {`ENTERWORKTREE_OK`, `ENTERWORKTREE_FAILED`} — consumed by Task 3.

- [ ] **Step 1: Create a scratch worktree under `.claude/worktrees/`**

Run from the repo root (`/Users/taylor/dev/claude-plugins`):
```bash
grep -qxF '.claude/worktrees/' .git/info/exclude || echo '.claude/worktrees/' >> .git/info/exclude
git worktree add .claude/worktrees/probe-scratch -b dev-flow-probe-scratch HEAD
git worktree list   # confirm probe-scratch present
```
Expected: `Preparing worktree (new branch 'dev-flow-probe-scratch')`; the directory and worktree entry exist. (The `.git/info/exclude` line is intentional and left in place — dev-flow's own worktree lifecycle relies on it.)

- [ ] **Step 2: Run the depth-2 entry+commit probe, mirroring production topology**

From the main session, dispatch a `general-purpose` subagent (the intermediate = "stage subagent" level). Its prompt: "First call `EnterWorktree` with `path` = `$(git rev-parse --show-toplevel)/.claude/worktrees/probe-scratch` (mirroring a stage subagent that has entered the pipeline worktree). Then spawn ONE `general-purpose` sub-subagent (the 'fixer' level) whose task is, verbatim: `Call EnterWorktree with path set to <ABS>/.claude/worktrees/probe-scratch. Then run: printf depth2-ok > probe.txt && git add probe.txt && git commit -m depth2-probe. Report three things separately and verbatim: (a) did EnterWorktree succeed? yes/no + any error; (b) did the commit succeed? the short SHA, or the exact error; (c) the output of git rev-parse --abbrev-ref HEAD.` Substitute `<ABS>` with the absolute repo root. Relay the sub-subagent's verbatim (a)/(b)/(c) back to me."

Note the commit uses `git add` then `git commit` — `git commit -am` would fail on the untracked `probe.txt` regardless of entry success.

- [ ] **Step 3: Record the result in the design doc's Evidence section**

In `docs/superpowers/specs/2026-07-22-dev-flow-nested-review-fix-design.md`, find the paragraph whose lead-in is `**Pending probe (required before implementation).**` and **replace that bold lead-in and the paragraph body** with the verdict:
- If (a) EnterWorktree succeeded **and** (b) the commit succeeded on branch `dev-flow-probe-scratch`: lead-in `**Verified (depth-2 EnterWorktree OK):**`, and state write-side fixers under `.claude/worktrees/` use `EnterWorktree(path)`. Set `PROBE_RESULT = ENTERWORKTREE_OK`.
- If (a) EnterWorktree failed: lead-in `**Probed — EnterWorktree unavailable at depth-2:**`, state all write-side fixers use the `git -C <path>` fallback uniformly. Set `PROBE_RESULT = ENTERWORKTREE_FAILED`.
- If (a) succeeded but (b) failed for an unrelated reason (not an entry problem): do NOT record FAILED — re-run Step 2 after fixing the commit mechanics; a commit-mechanics error must never be recorded as a capability gap.

- [ ] **Step 4: Tear down the scratch worktree**

```bash
git worktree remove --force .claude/worktrees/probe-scratch && git branch -D dev-flow-probe-scratch && git worktree prune
git worktree list   # probe-scratch absent
```

- [ ] **Step 5: Verify + commit**

```bash
grep -n "Verified (depth-2 EnterWorktree OK)\|Probed — EnterWorktree unavailable at depth-2" docs/superpowers/specs/2026-07-22-dev-flow-nested-review-fix-design.md   # sentinel present
git add docs/superpowers/specs/2026-07-22-dev-flow-nested-review-fix-design.md
git commit -m "dev-flow: record depth-2 EnterWorktree probe result"
```
Expected: the sentinel grep matches exactly one of the two verdict lead-ins.

---

### Task 2: adversarial-review — never-inline guarantee + model self-report + provenance

Adds the review-integrity core (design Fix 2 first home + Fix 3) to the review skill's Contract and report-back.

**Files:**
- Modify: `plugins/dev-flow/skills/adversarial-review/SKILL.md` (Contract block at line 15; report-back step 6 at line 64)

**Interfaces:**
- Produces: the provenance format `seeds: N× <tier>; resolvers: M× <tier>` (`<tier>` canonicalized via family match); the "first line of every reviewer report states its model" convention.

- [ ] **Step 1: Add the review-integrity clause to the Contract**

Locate the paragraph beginning `**Contract:** this skill owns the artifact end-to-end`. Immediately **after** it (it ends `…is part of the review, not integration.)`), insert:

```markdown
**Review integrity (never inline).** The seed and resolver passes MUST run as separate subagents on their specified models (per Model, below). If they cannot be spawned — no `Agent` tool, or a required model unavailable — halt and report; **never** produce a single-model inline review as a silent substitute. To make the model axis verifiable, every reviewer prompt (seed and resolver) requires the reviewer to state, as the first line of its report, the model its own system prompt names. The review matches each self-report to the tier requested for it — a **family match** (e.g. a "Fable 5" self-report satisfies the `fable` tier), honoring the resolver opus-fallback rather than a hardcoded id — and canonicalizes it to the tier alias (`sonnet`, `fable`, or `opus`). A missing or mismatched first line is treated exactly like a failed spawn: halt.
```

- [ ] **Step 2: Verify the clause landed and reads consistently**

```bash
grep -n "Review integrity (never inline)" plugins/dev-flow/skills/adversarial-review/SKILL.md
grep -n "never.*single-model inline review" plugins/dev-flow/skills/adversarial-review/SKILL.md
```
Expected: both match. Read Contract + Model sections together; confirm the family-match/opus-fallback wording agrees with the Model section (resolvers `fable`, `opus` when Fable-family; seeds `sonnet`). No contradiction.

- [ ] **Step 3: Add the provenance field to report-back (step 6)**

Locate step `6. Report back:` (line 64). Replace the whole step with:

```markdown
6. Report back: the commit(s) made, a summary of applied vs. skipped fixes, the post-fix suite result (diff mode), every new issue filed, and a **provenance** line naming the reviewers actually spawned per tier with their canonicalized tier aliases (from Review integrity's family match), in the form `seeds: N× <tier>; resolvers: M× <tier>` with `<tier>` ∈ {`sonnet`, `fable`, `opus`} (e.g. `seeds: 2× sonnet; resolvers: 3× fable`). Provenance is the evidence a caller checks to confirm the review was genuinely model-diverse.
```

- [ ] **Step 4: Verify + commit**

```bash
grep -n "provenance" plugins/dev-flow/skills/adversarial-review/SKILL.md   # expect the match in step 6
grep -n "seeds: N× <tier>; resolvers: M× <tier>" plugins/dev-flow/skills/adversarial-review/SKILL.md
git add plugins/dev-flow/skills/adversarial-review/SKILL.md
git commit -m "adversarial-review: never-inline contract + model self-report + provenance"
```

---

### Task 3: adversarial-review — working-dir resolve-once/thread-always rule

Adds the explicit-cwd seam (design's Worktree section). Uses `PROBE_RESULT` from Task 1 for the write-side mechanism.

**Files:**
- Modify: `plugins/dev-flow/skills/adversarial-review/SKILL.md` (Invocation line 10 + its bullets; Contract block)

**Interfaces:**
- Consumes: `PROBE_RESULT` from Task 1.
- Produces: the `working-dir` argument (dev-flow passes the worktree path — Task 5 consumes this contract).

- [ ] **Step 1: Extend the Invocation signature (full-line replacement) and add the dev-flow bullet**

Replace the entire current line ``**Invocation:** `adversarial-review(target, mode[, extra findings])` where `mode` is one of `design`, `plan`, `diff`.`` with:
```markdown
**Invocation:** `adversarial-review(target, mode[, extra findings][, working-dir])` where `mode` is one of `design`, `plan`, `diff`, and `working-dir` is an optional absolute path to the checkout/worktree the review reads and commits in (see the Contract's working-directory rule; absent → the invoking checkout).
```
Then, in the bullet list that follows, immediately after the bullet `- When called by dev-flow, the mode is passed explicitly.`, add:
```markdown
- When called by dev-flow, `working-dir` is the pipeline worktree's absolute path (dev-flow passes it explicitly — see dev-flow's stage-dispatch preamble).
```

- [ ] **Step 2: Add the working-directory rule to the Contract**

Immediately after the "**Review integrity (never inline).**" paragraph (Task 2), insert **one** of the following, per `PROBE_RESULT`.

If `PROBE_RESULT == ENTERWORKTREE_OK`:
```markdown
**Working directory (resolve once, thread always).** Resolve the working directory exactly once at invocation: the explicit `working-dir` argument if given, else the invoking checkout root (`git rev-parse --show-toplevel`), normalized to an absolute path; resolution failure (not a git repo) is a loud halt at invocation, because the contract requires committing. Thread that absolute path into every spawned agent's prompt — seeds, resolvers, and fixers — so no spawned agent derives its location from inherited cwd (process cwd is global mutable state; parallel fixers make ambient cwd a race). Read-only reviewers receive absolute artifact/diff paths and need no entry. Write-side fixers enter the root explicitly: `EnterWorktree(path)` when it is under `.claude/worktrees/` (the dev-flow case), else `git -C <path>` with absolute file paths (the standalone case — `EnterWorktree` rejects targets outside `.claude/worktrees/`, so threading + explicit addressing is the rule that works in both modes; harness entry is an optimization where available). The `working-dir` argument is an override only — omission cannot produce ambient-cwd behavior.
```

If `PROBE_RESULT == ENTERWORKTREE_FAILED`:
```markdown
**Working directory (resolve once, thread always).** Resolve the working directory exactly once at invocation: the explicit `working-dir` argument if given, else the invoking checkout root (`git rev-parse --show-toplevel`), normalized to an absolute path; resolution failure (not a git repo) is a loud halt at invocation, because the contract requires committing. Thread that absolute path into every spawned agent's prompt — seeds, resolvers, and fixers — so no spawned agent derives its location from inherited cwd (process cwd is global mutable state; parallel fixers make ambient cwd a race). Read-only reviewers receive absolute artifact/diff paths and need no entry. Write-side fixers address the root explicitly with `git -C <path>` and absolute file paths (a depth-2 `EnterWorktree` probe found harness worktree-entry unavailable at that depth — see the design spec's Evidence section — and explicit addressing is also the only mechanism that works for standalone reviews of checkouts outside `.claude/worktrees/`). The `working-dir` argument is an override only — omission cannot produce ambient-cwd behavior.
```

- [ ] **Step 3: Verify + commit**

```bash
grep -n "Working directory (resolve once, thread always)" plugins/dev-flow/skills/adversarial-review/SKILL.md
grep -n "one of \`design\`, \`plan\`, \`diff\`" plugins/dev-flow/skills/adversarial-review/SKILL.md   # mode enum preserved
grep -n "When called by dev-flow, \`working-dir\`" plugins/dev-flow/skills/adversarial-review/SKILL.md
git add plugins/dev-flow/skills/adversarial-review/SKILL.md
git commit -m "adversarial-review: resolve-once/thread-always working-dir rule"
```
Expected: all three match; the `mode` enumeration is still present in the Invocation line.

---

### Task 4: dev-flow — mandatory intake Capability gate

Design Fix 4: the probe that replaces the "version floor" as the enforceable seam. Done **before** Task 5 so Task 5's Environment-Assumptions rewrite can reference an already-present gate.

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md` (insert a new `## Capability gate` section between `## Model Policy` (line 43) and `## Dispatching to Inherited Skills` (line 47))

- [ ] **Step 1: Insert the Capability gate section**

Between the end of the `## Model Policy` section and the `## Dispatching to Inherited Skills` heading, insert:

```markdown
## Capability gate (runs first, every invocation)

Before any drafting, resume routing, or stage dispatch — on first run **and** every resume — dev-flow probes that the environment can run the model-diverse nested review, because the whole pipeline depends on it and the grant can be absent version-independently (restricted spawn type, permission settings, `allowedTools`):

1. Spawn one `general-purpose` subagent. It confirms it holds both `Agent` and `Skill`, then spawns one sub-subagent on the seed model and one on the resolver model — the tiers per `dev-flow:adversarial-review`'s Model section (currently `sonnet` for seeds; `fable`, or `opus` in a Fable-family session, for resolvers) — each returning the model its system prompt names.
2. If the subagent lacks either tool, either sub-subagent fails to spawn, or a returned model does not match the tier requested, **halt** with a report naming the missing capability and citing the verified-working version (2.1.217) as a diagnostic hint.

This is a hard gate, not advisory: it turns a capability failure into an intake halt — before any design draft is written and then discarded on resume — rather than a mid-run silent degradation. It runs uniformly on every invocation by design; conditional probing ("only when a review will run") would be a remember-which-resume-rows rule.
```

- [ ] **Step 2: Verify + commit**

```bash
grep -n "## Capability gate" plugins/dev-flow/skills/dev-flow/SKILL.md
grep -n "per .dev-flow:adversarial-review..s Model section" plugins/dev-flow/skills/dev-flow/SKILL.md   # by-reference, not hardcoded-as-policy
git add plugins/dev-flow/skills/dev-flow/SKILL.md
git commit -m "dev-flow: mandatory intake capability gate (probe replaces version floor)"
```

---

### Task 5: dev-flow — grant + dispatch-preamble clauses + Environment Assumptions rewrite

Design Fix 1 (grant), Fix 2 second home (integrity clause), plus the two seam requirements the design mandates: the stage passes `working-dir` and forwards the provenance line. Done in **one commit** with the Environment-Assumptions rewrite so no committed state is self-contradictory.

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md` (Pipeline preamble line 125; Dispatching-to-Inherited-Skills blockquote line 51; Environment Assumptions "Subagent nesting" bullet line 185)

**Interfaces:**
- Consumes: the Capability gate (Task 4); adversarial-review's `working-dir` argument (Task 3) and provenance line (Task 2).

- [ ] **Step 1: Name the spawn type in the Pipeline preamble**

Locate the sentence beginning `Each stage runs in a fresh subagent carrying the inherited-skills preamble`. Replace the fragment `Each stage runs in a fresh subagent carrying the inherited-skills preamble` with:
```markdown
Each stage runs in a fresh `general-purpose` subagent (the subagent type verified to carry the `Agent` + `Skill` tools the nested review requires — see Environment Assumptions) carrying the inherited-skills preamble
```
Leave the remainder of the sentence intact.

- [ ] **Step 2: Extend the carried dispatch preamble (integrity + working-dir + provenance)**

Locate the blockquote line beginning `> **dev-flow never lets an inherited skill talk to the user.**`. Immediately after that blockquote paragraph, add a second blockquoted paragraph:
```markdown
>
> **A stage never performs an adversarial review itself.** If the `Skill` tool cannot load `dev-flow:adversarial-review`, or the `Agent` tool is unavailable for the reviewer subagents it must spawn, halt and report the missing capability — an inline single-model review is a contract violation, never a fallback (this clause rides in the dispatch prompt because it is the only channel that reaches the stage subagent regardless of its toolset). When you do invoke `dev-flow:adversarial-review`, pass your pipeline worktree's absolute path as its `working-dir`, and copy the review's returned **provenance** line verbatim into your stage summary.
```

- [ ] **Step 3: Rewrite the Environment Assumptions "Subagent nesting" bullet**

Locate the bullet beginning `- **Subagent nesting.** This architecture requires spawned subagents to hold`. Replace the entire bullet (through `…historically not granted subagents the agent-spawning tool.)`) with:
```markdown
- **Subagent nesting (required; enforced by the Capability gate).** The pipeline requires spawned subagents to hold `Agent` + `Skill`: a stage subagent invokes `dev-flow:adversarial-review` and spawns its seed/resolver agents, and Execute's SDD spawns implementers/reviewers. Verified working on Claude Code 2.1.217 — documentation, not enforcement, since the grant can be lost version-independently. Enforcement is the Capability gate (above), which halts at intake if the environment cannot nest; mid-run degradation is caught by the dispatch-preamble integrity clause and the provenance check (Cross-Cutting Concerns). There is **no** inline single-model fallback — a stage that cannot run the model-diverse review halts loudly. (The earlier "run the seed and group agents from the main session" fallback is removed: from inside a stage subagent it is unreachable — the entity that detects the missing tool cannot execute a main-session fallback — and its orchestrator-proactive form is the flatten design this approach rejected.)
```

- [ ] **Step 4: Verify + commit**

```bash
grep -n "fresh \`general-purpose\` subagent" plugins/dev-flow/skills/dev-flow/SKILL.md
grep -n "A stage never performs an adversarial review itself" plugins/dev-flow/skills/dev-flow/SKILL.md
grep -n "pass your pipeline worktree's absolute path as its \`working-dir\`" plugins/dev-flow/skills/dev-flow/SKILL.md
grep -n "Subagent nesting (required; enforced by the Capability gate)" plugins/dev-flow/skills/dev-flow/SKILL.md
grep -c "run the seed and group agents from the main session" plugins/dev-flow/skills/dev-flow/SKILL.md   # expect 1 (only the named-and-removed reference in the rewritten bullet)
git add plugins/dev-flow/skills/dev-flow/SKILL.md
git commit -m "dev-flow: grant Agent+Skill; never-review-inline + working-dir + provenance in dispatch; rewrite Environment Assumptions"
```
Expected: the first four grep, and the last returns `1`. After this commit the file is internally consistent (no live main-session fallback alongside the new clause).

---

### Task 6: dev-flow — orchestrator provenance check

Design Fix 3's orchestrator-side check, consuming Task 2's provenance line (forwarded by Task 5's dispatch clause).

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md` (`## Cross-Cutting Concerns` section, line 188)

**Interfaces:**
- Consumes: the provenance format from Task 2; the forwarding requirement from Task 5.

- [ ] **Step 1: Add the provenance check to Cross-Cutting Concerns**

In the `## Cross-Cutting Concerns` section, after the existing "Context hygiene" bullet, add:
```markdown
- **Review provenance is checked, not assumed.** Every stage that runs `dev-flow:adversarial-review` (Design, Plan, PR — not Execute) forwards the review's provenance line (`seeds: N× <tier>; resolvers: M× <tier>`) in its stage summary (per the dispatch preamble). The orchestrator halts if that line is missing or its tiers violate `dev-flow:adversarial-review`'s Model section (seeds must be the seed tier, resolvers the resolver tier). The tiers are already canonicalized by the review's family match, so this is a direct comparison — and the orchestrator is the only observer outside the stage subagent's context, which is what makes "the review really ran model-diverse" verifiable rather than assumed.
```

- [ ] **Step 2: Verify + commit**

```bash
grep -n "Review provenance is checked, not assumed" plugins/dev-flow/skills/dev-flow/SKILL.md
git add plugins/dev-flow/skills/dev-flow/SKILL.md
git commit -m "dev-flow: orchestrator provenance check"
```

---

### Task 7: Sync the 2026-07-20 spec + plan to match

Keeps spec/plan/skill in lockstep. The stale passages are known and enumerated below.

**Files:**
- Modify: `docs/superpowers/specs/2026-07-20-dev-flow-design.md`
- Modify: `docs/superpowers/plans/2026-07-20-dev-flow-plan.md`

- [ ] **Step 1: Open the known stale passages**

These carry the old main-session fallback / unqualified-subagent language (confirmed present):
- `docs/superpowers/specs/2026-07-20-dev-flow-design.md` — the "Subagent nesting" passage (~line 230) and the unqualified "fresh subagent" mention (~line 134).
- `docs/superpowers/plans/2026-07-20-dev-flow-plan.md` — the "run seed/group agents from the main session" passage (~line 286) and the unqualified "fresh subagent" mention (~line 268).

Read each in context. (A broad `grep -ni "main session\|subagent\|inline" <file>` is a completeness sweep only — **`/simplify`-inlining passages are intentional and NOT stale**; do not "reconcile" them.)

- [ ] **Step 2: Reconcile each stale passage with this design**

Update each to match this design's substance — stages spawn as `general-purpose` (grant); the review halts loudly rather than inlining; a mandatory intake Capability gate enforces nesting; provenance is forwarded and checked; no main-session fallback. Keep it to one-line pointers plus a header note near the top of each doc:
```markdown
> Revised 2026-07-22 by `2026-07-22-dev-flow-nested-review-fix-design.md` (nested-review fix).
```
If a doc lacks any stale passage, add only the header pointer so the linkage is discoverable.

- [ ] **Step 3: Cross-file consistency read (the real check)**

Read both edited SKILL.md files once end-to-end. Confirm: the preamble grant (Task 5), Capability gate (Task 4), Environment Assumptions (Task 5), provenance check (Task 6), and the adversarial-review Contract additions (Tasks 2–3) reference each other consistently; the provenance format string is identical in adversarial-review report-back, the dispatch clause, and the Cross-Cutting check; and no live instruction anywhere tells a stage to review inline or fall back to the main session:
```bash
grep -c "run the seed and group agents from the main session" plugins/dev-flow/skills/dev-flow/SKILL.md   # expect 1 (the named-removed reference only)
```

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/specs/2026-07-20-dev-flow-design.md docs/superpowers/plans/2026-07-20-dev-flow-plan.md
git commit -m "Sync 2026-07-20 dev-flow spec+plan with nested-review fix"
```

---

## Acceptance (manual, after all tasks)

First **re-sync the installed plugin cache** — the runtime loads `~/.claude/plugins/cache/taylor-plugins/dev-flow/1.0.0/`, not the repo, so update it via the plugin's normal install/update path (re-add/update the `taylor-plugins` marketplace entry, or copy the repo's `plugins/dev-flow/` over that cache path). Then run the design doc's **Smoke test**: dev-flow on a small change with stops `[post-design, pre-merge]`. Confirm (1) the stage summary's provenance line names separate `sonnet` seeds and `fable` resolvers; (2) resume proceeds through Plan into Execute with SDD dispatching separate subagents; (3) Stage 4's diff-review fixers commit inside the pipeline worktree; (4) the run halts at `pre-merge` and never merges (teardown: `gh pr close`, then Stage 5 cleanup); (5) invoked from a no-`Agent` context, the Capability gate / dispatch clause halts with a clear message instead of a single-model review.
