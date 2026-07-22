# dev-flow Nested-Review Fix — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make dev-flow's per-stage adversarial review always run its model-diverse reviewer subagents (sonnet seeds / fable resolvers) or halt loudly — never silently degrade to a single-model inline review — by editing two skill markdown files, verified by a capability probe.

**Architecture:** Prose edits to two Claude Code skill files. The "never silently inline" guarantee is layered across shared boundaries: the tool grant at the stage-dispatch seam; an integrity clause in the dispatch-prompt preamble (the one channel that reaches a stage subagent regardless of its toolset); model self-report; an orchestrator-checked provenance line; and a mandatory intake capability probe. A resolve-once/thread-always working-dir rule kills ambient-cwd reliance. No code, no test framework — verification is anchor-text grep + internal/cross-file consistency reads; the design's smoke test is end-to-end acceptance.

**Tech Stack:** Markdown skill files under `plugins/dev-flow/skills/`; `git`; the `Agent`/`Skill`/`EnterWorktree` harness tools (for the probe only).

## Global Constraints

- **Design source of truth:** `docs/superpowers/specs/2026-07-22-dev-flow-nested-review-fix-design.md`. Every edit's wording is finalized there; copy it, don't paraphrase loosely.
- **Only edit our own plugin files:** `plugins/dev-flow/skills/dev-flow/SKILL.md` and `plugins/dev-flow/skills/adversarial-review/SKILL.md`. **Never modify `subagent-driven-development`** (a `superpowers` dependency) or any other superpowers skill.
- **The "never inline" guarantee is dual-homed** (adversarial-review Contract *and* dev-flow dispatch preamble). Both are load-bearing; never deduplicate one away.
- **Model policy is unchanged:** seeds on `sonnet`, resolvers on `fable` (or `opus` when the session model is Fable-family). The model self-report *enforces* this policy; it must not alter it.
- **The capability probe is mandatory at every intake** (first run and resume) — not optional, not conditional on which resume row fires.
- **Version floor is documentation** (2.1.217, the verified-working version); enforcement is the capability probe.
- **Provenance line format** (shared interface, defined in Task 2, consumed in Task 6): `seeds: N× <model>; resolvers: M× <model>` — reporting each reviewer's *self-reported* model.
- **Keep spec, plan, and skill in lockstep:** Task 7 syncs the older `2026-07-20` spec + plan.
- **Deployment note (out of plan scope):** these edits are to repo *source*. The installed plugin cache (`taylor-plugins/dev-flow/1.0.0`) is separately stale (older model policy) and must be re-synced for any repo edit to take effect at runtime — a deployment decision the maintainer owns, not a task here.
- **Acceptance:** the design doc's "Smoke test" section (run dev-flow with stops `[post-design, pre-merge]`; confirm provenance names sonnet seeds + fable resolvers; Stage 4 fixers commit in the worktree; loud halt on a no-`Agent` context). It is a manual end-to-end run, gated after all tasks.

---

### Task 1: Verify depth-2 worktree entry (the pending probe)

Confirms the one load-bearing capability the design marks "required before implementation": that a **depth-2** cwd-pinned agent (main → subagent → sub-subagent) can `EnterWorktree(path)` a worktree under `.claude/worktrees/` and commit there. The result decides the mechanism Task 3 writes down. Failure is not a blocker — it selects the `git -C` fallback.

**Files:**
- Modify: `docs/superpowers/specs/2026-07-22-dev-flow-nested-review-fix-design.md` (the "Evidence" section — turn the "Pending probe" note into a recorded result)

**Interfaces:**
- Produces: `PROBE_RESULT` ∈ {`ENTERWORKTREE_OK`, `ENTERWORKTREE_FAILED`} — consumed by Task 3.

- [ ] **Step 1: Create a scratch worktree under `.claude/worktrees/`**

Run from the repo root (`/Users/taylor/dev/claude-plugins`):
```bash
grep -qxF '.claude/worktrees/' .git/info/exclude || echo '.claude/worktrees/' >> .git/info/exclude
git worktree add .claude/worktrees/probe-scratch -b dev-flow-probe-scratch HEAD
```
Expected: `Preparing worktree (new branch 'dev-flow-probe-scratch')` and the directory exists.

- [ ] **Step 2: Run the depth-2 entry+commit probe**

Dispatch a `general-purpose` subagent (the intermediate level). Its prompt instructs it to spawn ONE sub-subagent (`general-purpose`) whose task is, verbatim: "Call `EnterWorktree` with `path` set to the absolute path of `.claude/worktrees/probe-scratch` inside this repo (resolve it as `$(git rev-parse --show-toplevel)/.claude/worktrees/probe-scratch`). Then create a file `probe.txt` containing `depth2-ok` in that worktree and commit it with `git commit -am depth2-probe`. Report verbatim: whether EnterWorktree succeeded, and the commit's short SHA, or the exact error." The intermediate subagent relays the sub-subagent's verbatim report back.

Expected on success: EnterWorktree accepted, a commit SHA returned. Expected on failure: a verbatim error (e.g. tool rejects the path, or entry not permitted at depth 2).

- [ ] **Step 3: Record the result in the design doc's Evidence section**

In `docs/superpowers/specs/2026-07-22-dev-flow-nested-review-fix-design.md`, replace the "**Pending probe (required before implementation).** …" paragraph's status: if the commit succeeded, prepend `**Verified (depth-2 EnterWorktree OK):**` and state fixers under `.claude/worktrees/` use `EnterWorktree(path)`; if it failed, prepend `**Probed — EnterWorktree unavailable at depth-2:**` and state all write-side fixers use the `git -C <path>` fallback uniformly. Set `PROBE_RESULT` accordingly for Task 3.

- [ ] **Step 4: Tear down the scratch worktree**

```bash
git worktree remove --force .claude/worktrees/probe-scratch && git branch -D dev-flow-probe-scratch && git worktree prune
```
Expected: clean removal; `git worktree list` no longer shows `probe-scratch`.

- [ ] **Step 5: Verify + commit**

```bash
git worktree list                 # probe-scratch absent
grep -n "EnterWorktree" docs/superpowers/specs/2026-07-22-dev-flow-nested-review-fix-design.md   # Evidence note updated
git add docs/superpowers/specs/2026-07-22-dev-flow-nested-review-fix-design.md
git commit -m "dev-flow: record depth-2 EnterWorktree probe result"
```

---

### Task 2: adversarial-review — never-inline guarantee + model self-report + provenance

Adds the review-integrity core (Fix 2 first home + Fix 3) to the review skill's Contract and report-back. This is the primary defect fix on the skill side.

**Files:**
- Modify: `plugins/dev-flow/skills/adversarial-review/SKILL.md` (Contract block near line 15; report-back step 6 near line 64)

**Interfaces:**
- Produces: the provenance line format `seeds: N× <model>; resolvers: M× <model>` (consumed by Task 6); the "first line of every reviewer report states its model" convention.

- [ ] **Step 1: Add the review-integrity clause to the Contract**

Locate the paragraph beginning `**Contract:** this skill owns the artifact end-to-end`. Immediately **after** that paragraph (which ends `…is part of the review, not integration.)`), insert a new paragraph:

```markdown
**Review integrity (never inline).** The seed and resolver passes MUST run as separate subagents on their specified models (per Model, below). If they cannot be spawned — no `Agent` tool, or a required model unavailable — halt and report; **never** produce a single-model inline review as a silent substitute. To make the model axis verifiable rather than assumed, every reviewer prompt (seed and resolver) requires the reviewer to state, as the first line of its report, the model its own system prompt names. The review verifies each self-report against the model requested for that tier — a family match (e.g. "Fable 5" satisfies `fable`), honoring the resolver opus-fallback rather than a hardcoded id. A missing or mismatched first line is treated exactly like a failed spawn: halt.
```

- [ ] **Step 2: Verify the clause landed and reads consistently**

```bash
grep -n "Review integrity (never inline)" plugins/dev-flow/skills/adversarial-review/SKILL.md
grep -n "never.*single-model inline review" plugins/dev-flow/skills/adversarial-review/SKILL.md
```
Expected: both match. Read the Contract + Model sections together and confirm the "family match / opus-fallback" wording agrees with the existing Model section (resolvers `fable`, `opus` when session is Fable-family; seeds `sonnet`). No contradiction.

- [ ] **Step 3: Add the provenance field to report-back (step 6)**

Locate step `6. Report back:` (near line 64). Replace it with:

```markdown
6. Report back: the commit(s) made, a summary of applied vs. skipped fixes, the post-fix suite result (diff mode), every new issue filed, and a **provenance** line naming the reviewers actually spawned per tier with their self-reported models, in the form `seeds: N× <model>; resolvers: M× <model>` (e.g. `seeds: 2× sonnet; resolvers: 3× fable`). Provenance reports what the reviewers *reported being*, not what was requested — it is the evidence a caller checks to confirm the review was genuinely model-diverse.
```

- [ ] **Step 4: Verify + commit**

```bash
grep -n "provenance" plugins/dev-flow/skills/adversarial-review/SKILL.md    # in step 6 and the integrity clause
git add plugins/dev-flow/skills/adversarial-review/SKILL.md
git commit -m "adversarial-review: never-inline contract + model self-report + provenance"
```

---

### Task 3: adversarial-review — working-dir resolve-once/thread-always rule

Adds the explicit-cwd seam (Worktree section of the design). Uses `PROBE_RESULT` from Task 1 to state the write-side mechanism.

**Files:**
- Modify: `plugins/dev-flow/skills/adversarial-review/SKILL.md` (Invocation line near line 11; Contract block)

**Interfaces:**
- Consumes: `PROBE_RESULT` from Task 1.

- [ ] **Step 1: Add the optional `working-dir` argument to the Invocation signature**

Locate `**Invocation:** \`adversarial-review(target, mode[, extra findings])\``. Replace with:
```markdown
**Invocation:** `adversarial-review(target, mode[, extra findings][, working-dir])` where `working-dir` is an optional absolute path to the checkout/worktree the review reads and commits in (see the Contract's working-directory rule; absent → the invoking checkout).
```

- [ ] **Step 2: Add the working-directory rule to the Contract**

Immediately after the "**Review integrity (never inline).**" paragraph added in Task 2, insert:

```markdown
**Working directory (resolve once, thread always).** Resolve the working directory exactly once at invocation: the explicit `working-dir` argument if given, else the invoking checkout root (`git rev-parse --show-toplevel`), normalized to an absolute path; resolution failure (not a git repo) is a loud halt at invocation, because the contract requires committing. Thread that absolute path into every spawned agent's prompt — seeds, resolvers, and fixers — so no spawned agent derives its location from inherited cwd (process cwd is global mutable state; parallel fixers make ambient cwd a race). Read-only reviewers receive absolute artifact/diff paths and need no entry. Write-side fixers enter the root explicitly: `EnterWorktree(path)` when it is under `.claude/worktrees/`, else `git -C <path>` with absolute file paths — `EnterWorktree` rejects targets outside `.claude/worktrees/`, so threading + explicit addressing is the only rule that works in both dev-flow and standalone modes; harness entry is an optimization where available. The `working-dir` argument is an override only — omission cannot produce ambient-cwd behavior.
```

If `PROBE_RESULT == ENTERWORKTREE_FAILED`, change "`EnterWorktree(path)` when it is under `.claude/worktrees/`, else `git -C <path>`" to "`git -C <path>` with absolute file paths (the depth-2 `EnterWorktree` probe failed — see Evidence)" and drop the EnterWorktree clause.

- [ ] **Step 3: Verify + commit**

```bash
grep -n "Working directory (resolve once, thread always)" plugins/dev-flow/skills/adversarial-review/SKILL.md
grep -n "working-dir" plugins/dev-flow/skills/adversarial-review/SKILL.md    # Invocation + Contract
git add plugins/dev-flow/skills/adversarial-review/SKILL.md
git commit -m "adversarial-review: resolve-once/thread-always working-dir rule"
```

---

### Task 4: dev-flow — grant the tools at the dispatch seam + integrity clause in the dispatch preamble

Fix 1 (grant) and Fix 2's second home (the clause that survives a no-`Skill` spawn).

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md` (Pipeline preamble near line 125; Dispatching-to-Inherited-Skills blockquote near line 51)

**Interfaces:**
- Produces: the `general-purpose` spawn requirement (referenced by Task 6's Environment Assumptions); the dispatch-preamble integrity clause.

- [ ] **Step 1: Name the spawn type in the Pipeline preamble**

Locate the sentence beginning `Each stage runs in a fresh subagent carrying the inherited-skills preamble`. Replace `Each stage runs in a fresh subagent carrying the inherited-skills preamble` with:
```markdown
Each stage runs in a fresh `general-purpose` subagent (the subagent type verified to carry the `Agent` + `Skill` tools the nested review requires — see Environment Assumptions) carrying the inherited-skills preamble
```
Leave the rest of the sentence (`(see Dispatching to Inherited Skills, above), **begins with the worktree-entry procedure…**`) intact.

- [ ] **Step 2: Add the integrity clause to the carried dispatch preamble**

Locate the blockquote line beginning `> **dev-flow never lets an inherited skill talk to the user.**` (this quote is carried verbatim into every dispatch). Immediately after that blockquote paragraph, add a second blockquoted paragraph:
```markdown
>
> **A stage never performs an adversarial review itself.** If the `Skill` tool cannot load `dev-flow:adversarial-review`, or the `Agent` tool is unavailable for the reviewer subagents it must spawn, halt and report the missing capability. An inline single-model review is a contract violation, never a fallback — this clause rides in the dispatch prompt because it is the only channel that reaches the stage subagent regardless of its toolset.
```

- [ ] **Step 3: Verify + commit**

```bash
grep -n "fresh \`general-purpose\` subagent" plugins/dev-flow/skills/dev-flow/SKILL.md
grep -n "A stage never performs an adversarial review itself" plugins/dev-flow/skills/dev-flow/SKILL.md
git add plugins/dev-flow/skills/dev-flow/SKILL.md
git commit -m "dev-flow: grant Agent+Skill at dispatch seam; add never-review-inline clause"
```

---

### Task 5: dev-flow — mandatory intake Capability gate

Fix 4: the probe that replaces the "version floor" as the enforceable seam.

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md` (add a new `## Capability gate` section immediately after the `## Model Policy` section)

**Interfaces:**
- Consumes: the `general-purpose` + seed/resolver model conventions (Task 4, Task 2).

- [ ] **Step 1: Insert the Capability gate section**

Find the end of the `## Model Policy` section (the line before the next `##` heading). Insert this new section between them:

```markdown
## Capability gate (runs first, every invocation)

Before any drafting, resume routing, or stage dispatch — on first run **and** every resume — dev-flow probes that the environment can run the model-diverse nested review, because the whole pipeline depends on it and the grant can be absent version-independently (restricted spawn type, permission settings, `allowedTools`):

1. Spawn one `general-purpose` subagent. It confirms it holds both `Agent` and `Skill`, then spawns one sub-subagent on the seed model (`sonnet`) and one on the resolver model (`fable`, or `opus` in a Fable-family session), each returning the model its system prompt names.
2. If the subagent lacks either tool, either sub-subagent fails to spawn, or a returned model does not match the tier requested, **halt** with a report naming the missing capability and citing the verified-working version (2.1.217) as a diagnostic hint.

This is a hard gate, not advisory: it turns a capability failure into an intake halt — before any design draft is written and then discarded on resume — rather than a mid-run silent degradation. It runs uniformly on every invocation by design; conditional probing ("only when a review will run") would be a remember-which-resume-rows rule.
```

- [ ] **Step 2: Verify + commit**

```bash
grep -n "## Capability gate" plugins/dev-flow/skills/dev-flow/SKILL.md
grep -n "runs first, every invocation" plugins/dev-flow/skills/dev-flow/SKILL.md
git add plugins/dev-flow/skills/dev-flow/SKILL.md
git commit -m "dev-flow: mandatory intake capability gate (probe replaces version floor)"
```

---

### Task 6: dev-flow — orchestrator provenance check + Environment Assumptions rewrite

Fix 3's orchestrator-side check (consuming Task 2's provenance line) and the rewrite of the removed fallback (Fix 2/4 rationale).

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md` (Cross-Cutting Concerns section; Environment Assumptions "Subagent nesting" bullet near line 185)

**Interfaces:**
- Consumes: the provenance line format from Task 2; the Capability gate from Task 5; the `general-purpose` grant from Task 4.

- [ ] **Step 1: Add the provenance check to Cross-Cutting Concerns**

Locate the `## Cross-Cutting Concerns` section. Add this bullet (after the existing "Context hygiene" bullet):
```markdown
- **Review provenance is checked, not assumed.** Every stage that runs `dev-flow:adversarial-review` (Design, Plan, PR — not Execute) returns the review's provenance line (`seeds: N× <model>; resolvers: M× <model>`) in its stage summary. The orchestrator halts if that line is missing or violates the review's Model policy (e.g. resolvers not on `fable`/`opus`, or seeds not on `sonnet`). The orchestrator is the only observer outside the stage subagent's context, so this check is what makes "the review really ran model-diverse" verifiable rather than assumed.
```

- [ ] **Step 2: Rewrite the Environment Assumptions "Subagent nesting" bullet**

Locate the bullet beginning `- **Subagent nesting.** This architecture requires spawned subagents to hold`. Replace the entire bullet (through `…historically not granted subagents the agent-spawning tool.)`) with:
```markdown
- **Subagent nesting (required; enforced by the Capability gate).** The pipeline requires spawned subagents to hold `Agent` + `Skill`: a stage subagent invokes `dev-flow:adversarial-review` and spawns its seed/resolver agents, and Execute's SDD spawns implementers/reviewers. Verified working on Claude Code 2.1.217 — documentation, not enforcement, since the grant can be lost version-independently. Enforcement is the Capability gate (above), which halts at intake if the environment cannot nest; mid-run degradation is caught by the dispatch-preamble integrity clause and the provenance check. There is **no** inline single-model fallback — a stage that cannot run the model-diverse review halts loudly. (The earlier "run the seed and group agents from the main session" fallback is removed: from inside a stage subagent it is unreachable — the entity that detects the missing tool cannot execute a main-session fallback — and its orchestrator-proactive form is the flatten design this approach rejected.)
```

- [ ] **Step 3: Verify + commit**

```bash
grep -n "Review provenance is checked, not assumed" plugins/dev-flow/skills/dev-flow/SKILL.md
grep -n "Subagent nesting (required; enforced by the Capability gate)" plugins/dev-flow/skills/dev-flow/SKILL.md
grep -n "run the seed and group agents from the main session" plugins/dev-flow/skills/dev-flow/SKILL.md   # expect: ONLY inside the new rewritten bullet (as the named-and-removed fallback), nowhere as live instruction
git add plugins/dev-flow/skills/dev-flow/SKILL.md
git commit -m "dev-flow: orchestrator provenance check; rewrite Environment Assumptions (no silent fallback)"
```

---

### Task 7: Sync the 2026-07-20 spec + plan to match

Keeps spec/plan/skill in lockstep (Global Constraints). The `2026-07-20` docs describe the same pipeline and carry the now-stale nesting/fallback language.

**Files:**
- Modify: `docs/superpowers/specs/2026-07-20-dev-flow-design.md`
- Modify: `docs/superpowers/plans/2026-07-20-dev-flow-plan.md`

- [ ] **Step 1: Locate the stale passages**

```bash
grep -n -i "subagent nesting\|main session instead\|inline\|agent-spawning tool" docs/superpowers/specs/2026-07-20-dev-flow-design.md
grep -n -i "subagent nesting\|main session instead\|inline\|agent-spawning tool" docs/superpowers/plans/2026-07-20-dev-flow-plan.md
```
Read each hit in context.

- [ ] **Step 2: Reconcile each stale passage with this design**

For any passage that describes the old "run from the main session" fallback or an unqualified "spawn a subagent," update it to match this design's substance: stages spawn as `general-purpose` (grant), the review halts loudly rather than inlining, a mandatory intake capability gate enforces nesting, and provenance is checked. Do not restate the full mechanism — one-line pointers plus a header note `> Revised 2026-07-22 by 2026-07-22-dev-flow-nested-review-fix-design.md (nesting fix)`. If a doc has no such passage, add only the header pointer so the linkage is discoverable.

- [ ] **Step 3: Cross-file consistency check across all edited files**

```bash
# The guarantee is dual-homed and consistent everywhere:
grep -rn "never.*inline\|contract violation\|halt" plugins/dev-flow/skills/
# No live instruction anywhere still tells a stage to review inline or fall back to the main session:
grep -rn "run the seed and group agents from the main session" plugins/dev-flow/skills/    # expect only the named-removed reference in Task 6
```
Read the two SKILL.md files once end-to-end; confirm the preamble grant (Task 4), Capability gate (Task 5), Environment Assumptions (Task 6), and adversarial-review Contract (Tasks 2–3) reference each other consistently and nothing contradicts.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/specs/2026-07-20-dev-flow-design.md docs/superpowers/plans/2026-07-20-dev-flow-plan.md
git commit -m "Sync 2026-07-20 dev-flow spec+plan with nested-review fix"
```

---

## Acceptance (manual, after all tasks)

Run the design doc's **Smoke test**: dev-flow on a small change with stops `[post-design, pre-merge]`. Confirm (1) the stage summary's provenance line names separate `sonnet` seeds and `fable` resolvers; (2) resume proceeds through Plan into Execute with SDD dispatching separate subagents; (3) Stage 4's diff-review fixers commit inside the pipeline worktree; (4) the run halts at `pre-merge`; (5) invoked from a no-`Agent` context, the capability gate / dispatch clause halts with a clear message instead of a single-model review. (Requires the installed plugin cache to be re-synced first — see the deployment note.)
