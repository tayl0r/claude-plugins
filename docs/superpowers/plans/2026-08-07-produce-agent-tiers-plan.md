---
dev-flow:
  slug: produce-agent-tiers
  spec: docs/superpowers/specs/2026-08-07-produce-agent-tiers-design.md
---
# Produce-Agent Tiers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give dev-flow's produce work (design drafting, plan writing) and its risky-task per-task review a pinned opus-tier agent definition, so the two highest-leverage artifacts and the subtle-task gate run on the strongest model while the driver, executors, routine per-task reviewers, and seed stay on the workhorse.

**Architecture:** Two new agent definitions, both pinned `claude-opus-4-8`: `produce-subagent`, dispatched for both Stage 1 (design) and Stage 2 (plan), replacing the bare `general-purpose` produce-subagent; and `task-reviewer`, the per-task review gate the orchestrator spawns for plan-marked `risk: high` tasks (replacing the earlier `model: opus` routing). The SKILL.md Model Policy, pipeline intro, Stage 1/2 dispatch sites, Stage 3 per-task reviewer routing (with the self-report verification), and the adversarial-review plan-preservation/backstop edits are updated in both plugin variants. Each agent self-reports its model so the orchestrator can verify the pin held. Two mirror pairs in `check-sync.py` enforce the two agent copies agree.

**Tech Stack:** Markdown skill/agent definitions, Python (`check-sync.py`, `check-version-bump.py`, `design_blocks.py`), Claude Code plugin system.

## Global Constraints

- **Version bumps (minor segment only):** `dev-flow` 2.18.0 → 2.19.0; `dev-flow-worktree` 1.20.0 → 1.21.0. Verified by `python3 scripts/check-version-bump.py origin/main`.
- **Mirroring:** the `produce-subagent` and `task-reviewer` agent files are machine-checked mirror pairs (dev-flow ↔ dev-flow-worktree) in `scripts/check-sync.py`; SKILL.md edits are hand-mirrored (the two SKILL.md files are too divergent for check-sync), except the adversarial-review SKILL.md pair, which is already a machine-checked pair.
- **Plugin-qualified spawn names:** `dev-flow:produce-subagent`, `dev-flow:task-reviewer`, and their `dev-flow-worktree:` counterparts (the bare name does not resolve). Never pass a `model` parameter at the produce or risky-task-reviewer spawn sites — it overrides the frontmatter pin.
- **Pin:** the produce-subagent and task-reviewer both pin the dated id `claude-opus-4-8` (per ADR 0004 — frontmatter is the only place a dated id survives).
- **Removed-phrase grep (both variants):** `spawns produce-subagents and executors on the main session model`, `runs in a fresh \`general-purpose\` produce-subagent`, `writes its draft into the working checkout`, and `written into the working checkout on the feature branch` must return no hits. (The fragment `on the main session model` is intentionally kept for executors — grep the full combined clause, not the fragment.)
- **Design-conformance:** the produce-subagent and task-reviewer blocks in the design doc must appear verbatim in their dev-flow agent files, re-read from the design (never retyped). Each worktree copy must equal its dev-flow copy after the two plugin-name substitutions (`dev-flow` → `dev-flow-worktree` in the description and body) — line-for-line identical after canonicalization, which is what check-sync enforces.

---

### Task 1: Create the produce-subagent and task-reviewer agent definitions (dev-flow)

**Files:**
- Modify: `docs/superpowers/specs/2026-08-07-produce-agent-tiers-design.md` (fences of the two agent blocks: ` ```markdown ` → ` ``` `, so `design_blocks.py` reads them)
- Create: `plugins/dev-flow/agents/produce-subagent.md`
- Create: `plugins/dev-flow/agents/task-reviewer.md`

**Interfaces:**
- Consumes: the produce-subagent and task-reviewer blocks from the design doc (the agent file contents).
- Produces: `plugins/dev-flow/agents/produce-subagent.md` and `plugins/dev-flow/agents/task-reviewer.md` — the agent definitions the SKILL.md dispatches as `dev-flow:produce-subagent` and `dev-flow:task-reviewer`.

- [ ] **Step 1: Change both agent-block fences to untagged**

In `docs/superpowers/specs/2026-08-07-produce-agent-tiers-design.md`, change the fences that open the produce-subagent block (currently ` ```markdown `, the block whose frontmatter names `produce-subagent`) and the task-reviewer block (the block whose frontmatter names `task-reviewer`) to plain ` ``` `. The closing fences are already plain. This lets `design_blocks.py` read both blocks for the conformance check.

- [ ] **Step 2: Get the block shapes**

Run: `python3 scripts/design_blocks.py docs/superpowers/specs/2026-08-07-produce-agent-tiers-design.md`
Expected: prints a shape like `[19, 17]` (the two agent blocks' line counts). Note the values — the conformance check in Step 4 uses them.

- [ ] **Step 3: Create the agent files**

Create `plugins/dev-flow/agents/produce-subagent.md` with exactly the produce-subagent block content from the design doc:

```markdown
---
name: produce-subagent
description: Drafts a best-judgment design doc (Stage 1) or a self-sufficient task plan (Stage 2) for dev-flow's produce work, following the dispatch's inlined protocol or skill. Pinned to claude-opus-4-8.
model: claude-opus-4-8
---

You are a **produce-subagent** for dev-flow — the leaf that drafts the pipeline's
output-sensitive artifacts.

The dispatch names which: it carries the inlined non-interactive brainstorming
protocol (Stage 1 design) or the `superpowers:writing-plans` skill (Stage 2 plan),
plus the absolute working-directory path and the absolute output path. Follow it
exactly. Write your draft to the absolute path given — never to inherited cwd.
Carry the inherited-skills preamble the dispatch hands you. Do not invoke
`adversarial-review` or spawn further agents.

**The first line of your summary must be the model your own system prompt names**
(e.g. `claude-opus-4-8`), so the orchestrator can verify the tier you ran on. A
missing or wrong first line halts the pipeline.
```

Create `plugins/dev-flow/agents/task-reviewer.md` with exactly the task-reviewer block content from the design doc:

```markdown
---
name: task-reviewer
description: Per-task review gate for dev-flow's Execute stage, spawned by the orchestrator (SDD's controller) for plan-marked risky tasks. Pinned to claude-opus-4-8.
model: claude-opus-4-8
---

You are a **task-reviewer** for dev-flow — the per-task review gate SDD's controller
spawns after a `risk: high` task. You check the task's own verification command and
report pass/fail plus findings; you do not fix, rewrite, or implement.

The dispatch names the task, its verification command, and the absolute working-directory
path. Run the verification, check the diff against the task's `## Task N` section, and
report. Address the absolute working-directory path explicitly — with `git -C <path>`
and absolute file paths — and never rely on inherited cwd.

**The first line of your summary must be the model your own system prompt names**
(e.g. `claude-opus-4-8`), so the orchestrator can verify the tier you ran on.
```

- [ ] **Step 4: Verify the files match the design blocks verbatim**

Run this conformance check (re-reads the blocks from the design, never retyped):

```python
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
DESIGN = "docs/superpowers/specs/2026-08-07-produce-agent-tiers-design.md"
blocks = read_blocks(DESIGN, [19, 17])  # use the shapes from Step 2
produce = Path("plugins/dev-flow/agents/produce-subagent.md").read_text()
task_reviewer = Path("plugins/dev-flow/agents/task-reviewer.md").read_text()
assert produce == "\n".join(blocks[0]) + "\n", "produce-subagent file must equal the design block verbatim"
assert task_reviewer == "\n".join(blocks[1]) + "\n", "task-reviewer file must equal the design block verbatim"
print("OK: agent files match design blocks")
```

Expected: prints `OK: agent files match design blocks`.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/specs/2026-08-07-produce-agent-tiers-design.md plugins/dev-flow/agents/produce-subagent.md plugins/dev-flow/agents/task-reviewer.md
git commit -m "feat: add produce-subagent and task-reviewer agent definitions pinned to claude-opus-4-8"
```

---

### Task 2: Mirror the agent definitions + register the check-sync pairs

**Files:**
- Create: `plugins/dev-flow-worktree/agents/produce-subagent.md`
- Create: `plugins/dev-flow-worktree/agents/task-reviewer.md`
- Modify: `scripts/check-sync.py` (add the two mirror pairs to `MIRROR_PAIRS`)

**Interfaces:**
- Consumes: the dev-flow agent files from Task 1 (each worktree copy must be identical after canonicalization).
- Produces: the `produce-subagent` and `task-reviewer` mirror pairs in `MIRROR_PAIRS`, so `check-sync.py` enforces the two copies of each agree.

- [ ] **Step 1: Create the mirrored agent files**

Copy `plugins/dev-flow/agents/produce-subagent.md` to `plugins/dev-flow-worktree/agents/produce-subagent.md`, then change the two plugin-naming occurrences to name the worktree plugin: in the description, `for dev-flow's produce work` → `for dev-flow-worktree's produce work`; in the body, `for dev-flow` → `for dev-flow-worktree`. Do the same for `task-reviewer.md` (its description and body name `dev-flow` in the same two places). The `canonicalize: [("dev-flow-worktree", "dev-flow")]` entries map those back, so each pair is line-for-line identical after canonicalization. The entries are load-bearing here, not decorative: a byte-for-byte copy would leave the worktree agents naming `dev-flow` (the wrong plugin) and the canonicalize entries would map nothing — `check-sync.py` would pass it.

- [ ] **Step 2: Register the mirror pairs**

In `scripts/check-sync.py`, add a fourth and fifth entry to `MIRROR_PAIRS` (after the `adversarial-review-resolver agent` entry, which ends at line 85), following the exact pattern of the existing agent pairs:

```python
    {
        "name": "produce-subagent agent",
        "a": "plugins/dev-flow/agents/produce-subagent.md",
        "b": "plugins/dev-flow-worktree/agents/produce-subagent.md",
        # Same canonicalization as the SKILL.md pair: each variant's agent
        # description and body may name its own plugin, and both register
        # under their own qualified name, so "dev-flow-worktree" there is
        # correct rather than drift.
        "canonicalize": [("dev-flow-worktree", "dev-flow")],
        "exceptions": [],
    },
    {
        "name": "task-reviewer agent",
        "a": "plugins/dev-flow/agents/task-reviewer.md",
        "b": "plugins/dev-flow-worktree/agents/task-reviewer.md",
        "canonicalize": [("dev-flow-worktree", "dev-flow")],
        "exceptions": [],
    },
```

- [ ] **Step 3: Verify check-sync passes**

Run: `python3 scripts/check-sync.py`
Expected: exits 0; the report shows mirror pair "produce-subagent agent" and "task-reviewer agent" passing (identical after canonicalization).

- [ ] **Step 4: Commit**

```bash
git add plugins/dev-flow-worktree/agents/produce-subagent.md plugins/dev-flow-worktree/agents/task-reviewer.md scripts/check-sync.py
git commit -m "feat: mirror produce-subagent and task-reviewer agents and register their check-sync pairs"
```

---

### Task 3: Edit dev-flow SKILL.md

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md` (Model Policy line 46, pipeline intro line 205, Stage 1 lines 211-212, Stage 2 line 224, Stage 3 after line 234, Cross-Cutting Concerns after line 280)

**Interfaces:**
- Consumes: the `dev-flow:produce-subagent` and `dev-flow:task-reviewer` agents from Task 1.
- Produces: the updated Model Policy, dispatch sites, Stage 3 reviewer routing, and Cross-Cutting Concerns provenance bullet that the worktree variant mirrors in Task 4.

- [ ] **Step 1: Model Policy (line 46)**

Replace:
`The orchestrator spawns produce-subagents and executors on the main session model, and does its own bookkeeping`
with:
`The orchestrator spawns produce-subagents on the opus tier via their agent pin, and executors on the main session model, and does its own bookkeeping`

- [ ] **Step 2: Pipeline intro (line 205)**

Replace:
`runs in a fresh \`general-purpose\` produce-subagent — a leaf carrying the inherited-skills preamble (see Dispatching to Inherited Skills, above) that writes its draft into the working checkout (repo root, which is on the feature branch) and returns a short summary`
with:
`runs in a fresh \`dev-flow:produce-subagent\` (the pinned opus-tier leaf) — a leaf carrying the inherited-skills preamble (see Dispatching to Inherited Skills, above) that writes its draft to the absolute output path the dispatch names (the design/plan doc path under the repo root, which is on the feature branch) and returns a short summary`

- [ ] **Step 3: Stage 1 Issue entry (line 211)**

Replace:
`no design file to adopt — dispatch the produce-subagent per the Artifact Contract's Issue-driven intake`
with:
`no design file to adopt — dispatch \`dev-flow:produce-subagent\` per the Artifact Contract's Issue-driven intake, carrying the absolute working-directory path and the absolute output path (the design doc path)`

- [ ] **Step 4: Stage 1 Bare-idea entry (line 212)**

Replace:
`the orchestrator dispatches a produce-subagent to draft a best-judgment design doc (written into the working checkout on the feature branch)`
with:
`the orchestrator dispatches \`dev-flow:produce-subagent\` to draft a best-judgment design doc (written to the absolute output path the dispatch names — under the repo root on the feature branch), carrying the absolute working-directory path and the absolute output path (the design doc path)`

- [ ] **Step 5: Stage 2 (line 224)**

Replace:
`- Spawn a subagent to run \`superpowers:writing-plans\` against the design, producing \`docs/superpowers/plans/YYYY-MM-DD-<slug>-plan.md\` (front-matter links the spec).`
with:
`- Spawn \`dev-flow:produce-subagent\` to run \`superpowers:writing-plans\` against the design, carrying the absolute working-directory path and the absolute output path (the plan doc path), producing \`docs/superpowers/plans/YYYY-MM-DD-<slug>-plan.md\` (front-matter links the spec). Instruct it to **mark risky tasks**: a \`risk: high\` line in any \`## Task N\` section whose work touches concurrency, auth, state machines, or other subtle invariants, so Stage 3 can route that task's reviewer to the opus tier. The marker's contract: a line \`risk: high\` (lowercase, single space after the colon) anywhere in the \`## Task N\` section; the orchestrator treats the task as risky iff its section — the span \`task-brief\` extracts, the text between \`## Task N\` and the next task heading — contains a line matching \`risk: high\` (case-insensitive on the value). A \`risk:\` line with any other value, or in a non-task section, is ignored by the orchestrator and flagged by the plan review's correctness seed; a task with multiple \`risk:\` lines is risky iff any is \`risk: high\`. The self-sufficiency instruction is unchanged.`

- [ ] **Step 6: Stage 3 — add per-task reviewer routing**

After the **Implementer briefing** bullet (line 234), insert:

`- **Per-task reviewer routing:** as SDD's controller, the orchestrator spawns each per-task reviewer on the session model, except for a task whose \`## Task N\` section carries \`risk: high\` (per the marker contract in the Stage 2 edit), whose reviewer it spawns as \`dev-flow:task-reviewer\` (the pinned opus-tier leaf). Require the per-task reviewer to state its model as the first line of its report, and verify it against the expected tier — the session model for routine tasks, the opus tier for \`risk: high\` tasks — halting on a mismatch. Fix-loop escalation: SDD's ladder says "a model at least one tier above the implementer that got stuck"; on Ollama the sonnet tier *is* flash, so dev-flow resolves the ladder to \`model: opus\` at the spawn site — a new, concrete decision, not a restatement of today's intent (today's Stage 3 Halts bullet defers to SDD's generic ladder).`

- [ ] **Step 7: Cross-Cutting Concerns — add produce-tier provenance**

After the **Review provenance is checked, not assumed** bullet (line 280), insert:

`- **Produce-tier provenance is checked, not assumed.** The orchestrator reads the produce-subagent's returned summary's first line — the model the agent's own system prompt names — and halts if it is missing or does not match \`claude-opus-4-8\`, ignoring any harness-appended variant suffix (the same normalization the review provenance check uses). This catches a launch that silently defeats the pin (e.g. \`CLAUDE_CODE_SUBAGENT_MODEL\` set) in-pipeline, not just at a one-time live check.`

- [ ] **Step 8: Verify the removed phrases are gone**

Run: `grep -nE "spawns produce-subagents and executors on the main session model|runs in a fresh \`general-purpose\` produce-subagent|writes its draft into the working checkout|written into the working checkout on the feature branch" plugins/dev-flow/skills/dev-flow/SKILL.md`
Expected: no output (exit 1).

- [ ] **Step 9: Commit**

```bash
git add plugins/dev-flow/skills/dev-flow/SKILL.md
git commit -m "feat: route dev-flow produce work through the pinned produce-subagent"
```

---

### Task 4: Hand-mirror SKILL.md edits to dev-flow-worktree

**Files:**
- Modify: `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` (Model Policy line 45, pipeline intro line 199, Stage 1 lines 205-206, Stage 2 line 218, Stage 3 after line 228, Cross-Cutting Concerns after line 274)

**Interfaces:**
- Consumes: the dev-flow SKILL.md edits from Task 3 (mirrored by hand — the two SKILL.md files are too divergent for check-sync).
- Produces: the worktree variant's equivalent edits, using the `dev-flow-worktree:produce-subagent` and `dev-flow-worktree:task-reviewer` qualified names.

- [ ] **Step 1: Model Policy (line 45)**

Replace:
`The orchestrator spawns produce-subagents and executors on the main session model, and does its own bookkeeping`
with:
`The orchestrator spawns produce-subagents on the opus tier via their agent pin, and executors on the main session model, and does its own bookkeeping`
(The sentence is identical to the dev-flow variant; the ownership note naming `dev-flow-worktree:adversarial-review` is unchanged.)

- [ ] **Step 2: Pipeline intro (line 199)**

Replace:
`runs in a fresh \`general-purpose\` produce-subagent — a leaf carrying the inherited-skills preamble (see Dispatching to Inherited Skills, above) that writes its draft into the worktree by absolute path and returns a short summary`
with:
`runs in a fresh \`dev-flow-worktree:produce-subagent\` (the pinned opus-tier leaf) — a leaf carrying the inherited-skills preamble (see Dispatching to Inherited Skills, above) that writes its draft to the absolute output path the dispatch names (the design/plan doc path in the worktree) and returns a short summary`

- [ ] **Step 3: Stage 1 Issue entry (line 205)**

Replace:
`no design file to adopt — dispatch the produce-subagent per the Artifact Contract's Issue-driven intake`
with:
`no design file to adopt — dispatch \`dev-flow-worktree:produce-subagent\` per the Artifact Contract's Issue-driven intake, carrying the absolute working-directory path and the absolute output path (the design doc path)`

- [ ] **Step 4: Stage 1 Bare-idea entry (line 206)**

Replace:
`the orchestrator dispatches a produce-subagent to draft a best-judgment design doc (written into the worktree by absolute path)`
with:
`the orchestrator dispatches \`dev-flow-worktree:produce-subagent\` to draft a best-judgment design doc (written to the absolute output path the dispatch names — in the worktree), carrying the absolute working-directory path and the absolute output path (the design doc path)`

- [ ] **Step 5: Stage 2 (line 218)**

Replace:
`- Spawn a subagent to run \`superpowers:writing-plans\` against the design, producing \`docs/superpowers/plans/YYYY-MM-DD-<slug>-plan.md\` (front-matter links the spec).`
with:
`- Spawn \`dev-flow-worktree:produce-subagent\` to run \`superpowers:writing-plans\` against the design, carrying the absolute working-directory path and the absolute output path (the plan doc path), producing \`docs/superpowers/plans/YYYY-MM-DD-<slug>-plan.md\` (front-matter links the spec). Instruct it to **mark risky tasks**: a \`risk: high\` line in any \`## Task N\` section whose work touches concurrency, auth, state machines, or other subtle invariants, so Stage 3 can route that task's reviewer to the opus tier. The marker's contract: a line \`risk: high\` (lowercase, single space after the colon) anywhere in the \`## Task N\` section; the orchestrator treats the task as risky iff its section — the span \`task-brief\` extracts, the text between \`## Task N\` and the next task heading — contains a line matching \`risk: high\` (case-insensitive on the value). A \`risk:\` line with any other value, or in a non-task section, is ignored by the orchestrator and flagged by the plan review's correctness seed; a task with multiple \`risk:\` lines is risky iff any is \`risk: high\`. The self-sufficiency instruction is unchanged.`

- [ ] **Step 6: Stage 3 — add per-task reviewer routing**

After the **Implementer briefing** bullet (line 228), insert:

`- **Per-task reviewer routing:** as SDD's controller, the orchestrator spawns each per-task reviewer on the session model, except for a task whose \`## Task N\` section carries \`risk: high\` (per the marker contract in the Stage 2 edit), whose reviewer it spawns as \`dev-flow-worktree:task-reviewer\` (the pinned opus-tier leaf). Require the per-task reviewer to state its model as the first line of its report, and verify it against the expected tier — the session model for routine tasks, the opus tier for \`risk: high\` tasks — halting on a mismatch. Fix-loop escalation: SDD's ladder says "a model at least one tier above the implementer that got stuck"; on Ollama the sonnet tier *is* flash, so dev-flow resolves the ladder to \`model: opus\` at the spawn site — a new, concrete decision, not a restatement of today's intent (today's Stage 3 Halts bullet defers to SDD's generic ladder).`

- [ ] **Step 7: Cross-Cutting Concerns — add produce-tier provenance**

After the **Review provenance is checked, not assumed** bullet (line 274), insert the same produce-tier provenance bullet as Task 3 Step 7.

- [ ] **Step 8: Verify the removed phrases are gone**

Run: `grep -nE "spawns produce-subagents and executors on the main session model|runs in a fresh \`general-purpose\` produce-subagent|writes its draft into the working checkout|written into the working checkout on the feature branch|writes its draft into the worktree by absolute path|written into the worktree by absolute path" plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`
Expected: no output (exit 1).

- [ ] **Step 9: Commit**

```bash
git add plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
git commit -m "feat: mirror produce-subagent routing into dev-flow-worktree"
```

---

### Task 5: Edit the adversarial-review SKILL.md pair (plan-review preservation + marker backstop)

**Files:**
- Modify: `plugins/dev-flow/skills/adversarial-review/SKILL.md` (rewrite contract, line 75; plan correctness seed, Seed passes table line 30)
- Modify: `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md` (same two edits)

**Interfaces:**
- Consumes: the marker contract from Task 3 Step 5 (the correctness seed checks it).
- Produces: both edits in both copies — a machine-checked mirror pair already registered in `check-sync.py`, so the pair check proves the copies agree.

- [ ] **Step 1: Extend the rewrite contract (dev-flow copy)**

In `plugins/dev-flow/skills/adversarial-review/SKILL.md`, line 75, replace:
`**Design / plan docs:** rewrite the doc incorporating the resolutions, **preserving the doc's front-matter block and its \`## Original problem\` section unchanged** (caller state, not review content), and commit the rewritten doc on the working directory's branch.`
with:
`**Design / plan docs:** rewrite the doc incorporating the resolutions, **preserving the doc's front-matter block, its \`## Original problem\` section, and every \`risk:\` line in \`## Task N\` sections unchanged** (caller state, not review content), and commit the rewritten doc on the working directory's branch.`

- [ ] **Step 2: Add the marker backstop to the plan correctness seed (dev-flow copy)**

In the same file, the **plan** row of the Seed passes table (line 30), append to the correctness-seed cell:

`and the \`risk:\` marker contract: a \`## Task N\` section whose work touches concurrency, auth, state machines, or other subtle invariants must carry a \`risk: high\` line (lowercase, single space after the colon) — a risky task missing the marker, a \`risk:\` line with any other value, or a \`risk:\` line in a non-task section is a finding.`

- [ ] **Step 3: Mirror both edits to the worktree copy**

Apply the identical two edits to `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md` (the pair is line-for-line identical after canonicalization; neither edit names a plugin).

- [ ] **Step 4: Verify check-sync passes**

Run: `python3 scripts/check-sync.py`
Expected: exits 0; the `adversarial-review` mirror pair passes.

- [ ] **Step 5: Commit**

```bash
git add plugins/dev-flow/skills/adversarial-review/SKILL.md plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
git commit -m "feat: preserve risk markers in plan review and backstop them in the correctness seed"
```

---

### Task 6: Version bumps + CONTEXT.md glossary

**Files:**
- Modify: `plugins/dev-flow/.claude-plugin/plugin.json` (version 2.18.0 → 2.19.0)
- Modify: `plugins/dev-flow-worktree/.claude-plugin/plugin.json` (version 1.20.0 → 1.21.0)
- Modify: `CONTEXT.md` (Tier entry, lines 17-18)

**Interfaces:**
- Consumes: the behavior changes from Tasks 1-5 (new agents shipped, new spawn targets, Stage 3 reviewer routing, plan-review preservation).
- Produces: version bumps that the install cache (version-keyed) will pick up on re-sync, and a Tier glossary entry that covers any pinned agent.

- [ ] **Step 1: Bump dev-flow**

In `plugins/dev-flow/.claude-plugin/plugin.json`, change `"version": "2.18.0"` to `"version": "2.19.0"`.

- [ ] **Step 2: Bump dev-flow-worktree**

In `plugins/dev-flow-worktree/.claude-plugin/plugin.json`, change `"version": "1.20.0"` to `"version": "1.21.0"`.

- [ ] **Step 3: Broaden the CONTEXT.md Tier entry**

In `CONTEXT.md`, replace the Tier entry's first sentence:
`The model a reviewer is spawned on — \`claude-sonnet-4-6\` for seeds, \`claude-opus-4-8\` for resolvers.`
with:
`The model a pinned agent is spawned on — \`claude-sonnet-4-6\` for seeds, \`claude-opus-4-8\` for resolvers, the produce-subagent, and the risky-task reviewer.`
The rest of the entry is unchanged.

- [ ] **Step 4: Verify the bump check passes**

Run: `python3 scripts/check-version-bump.py origin/main`
Expected: exits 0 (both plugins bumped past origin/main).

- [ ] **Step 5: Commit**

```bash
git add plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json CONTEXT.md
git commit -m "chore: bump dev-flow to 2.19.0 and dev-flow-worktree to 1.21.0; broaden the Tier glossary entry"
```

---

### Task 7: Full verification

**Files:**
- None (verification only).

**Interfaces:**
- Consumes: all changes from Tasks 1-6.

- [ ] **Step 1: Plugin validation**

Run: `claude plugin validate .`
Expected: exits 0 (warnings about missing author info are expected and allowed — the author check is enforced separately by check-sync).

- [ ] **Step 2: Mirror sync**

Run: `python3 scripts/check-sync.py`
Expected: exits 0; the `produce-subagent agent` and `task-reviewer agent` pairs pass.

- [ ] **Step 3: Version bump check**

Run: `python3 scripts/check-version-bump.py origin/main`
Expected: exits 0.

- [ ] **Step 4: Removed-phrase grep (both variants)**

Run:
`grep -nE "spawns produce-subagents and executors on the main session model|runs in a fresh \`general-purpose\` produce-subagent|writes its draft into the working checkout|written into the working checkout on the feature branch|writes its draft into the worktree by absolute path|written into the worktree by absolute path" plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`
Expected: no output (exit 1).

- [ ] **Step 5: Design-conformance check**

Re-run the Task 1 Step 4 conformance check (asserts the dev-flow agent files equal the design blocks; check-sync already proved the worktree copies are identical after canonicalization — the two plugin-name substitutions are the only differences).

- [ ] **Step 6: Commit any stragglers**

If any file changed in the verification steps, commit it. Otherwise no commit needed.

---

## Post-implementation validation (manual, after install)

These require a relaunch per the design's Launch reference and are not automatable in this repo:

- Re-sync the marketplace and update both plugins, then restart: `claude plugin marketplace update taylor-plugins`, `claude plugin update dev-flow@taylor-plugins`, `claude plugin update dev-flow-worktree@taylor-plugins`.
- `claude plugin details dev-flow` lists the new `produce-subagent` and `task-reviewer` agents (note: it reports the marketplace-synced version, not the running install).
- Live check (Anthropic): run dev-flow Stage 1, confirm the produce-subagent self-reports `claude-opus-4-8` (ignoring any harness-appended variant suffix); run Stage 2, confirm the same.
- Provenance check: run Stage 1 + Stage 2 with `CLAUDE_CODE_SUBAGENT_MODEL` set to a wrong model, confirm the orchestrator halts on the produce-tier self-report mismatch.
- Live check (Ollama): launch per the Launch reference, confirm produce-subagent and resolver run on the opus alias target (`deepseek-v4-pro`), the seed on the sonnet alias target (`flash`), and the driver on `flash`; for a `risk: high` task, confirm its per-task reviewer self-reports `claude-opus-4-8` as the first line of its report, and that a routine task's reviewer self-reports the session model; confirm the orchestrator halts on a mismatch.
- Plan-review preservation check: run a plan carrying a `risk: high` marker through `dev-flow:adversarial-review` (mode: plan) with a finding that touches the marked task's section, and confirm the rewritten plan still carries the marker.
