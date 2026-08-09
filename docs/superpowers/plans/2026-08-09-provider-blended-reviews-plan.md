# Provider-Blended Reviews Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make dev-flow's review tiers (seeds, task-reviewers, fixers) provider-configurable — `session` | `codex` | `ollama-<tier>` | `claude` — so each laptop can blend a small amount of review work onto its $20 Ollama and $20 Codex quotas while writing and judgment stay on Anthropic opus.

**Architecture:** The `providers:` config key in `.claude/dev-flow.local.md` (per-machine, git-ignored) selects each tier's provider. Unset = `session` (current behavior). Non-session providers shell-delegate: the orchestrator runs the codex companion or `claude-ollama <tier> -p` as a one-shot via Bash instead of spawning the Agent-tool subagent. Delegated seed findings join the adversarial review as caller-supplied findings; the review's seed spawn is skipped. Produce and resolvers are untouched (pinned to opus via agent frontmatter).

**Tech Stack:** Markdown skill docs (dev-flow + dev-flow-worktree plugins), the codex companion script, the `claude-ollama` wrapper, Python verification scripts (`scripts/check-sync.py`, `scripts/check-version-bump.py`, `scripts/design_blocks.py`, `scripts/verify_blob.py`).

## Global Constraints

- **Version bump:** any behavior change bumps the **minor** segment of `plugins/<name>/.claude-plugin/plugin.json` — `dev-flow` 2.19.0 → 2.20.0, `dev-flow-worktree` 1.21.0 → 1.22.0. Bump past `origin/main`, not past the branch base.
- **Mirroring:** `skills/adversarial-review/SKILL.md` is machine-checked (line-for-line identical after `dev-flow-worktree` → `dev-flow`); the pipeline SKILL.md pair and the example configs are hand-mirrored. `python3 scripts/check-sync.py` must pass.
- **Verification:** every edit must be byte-for-byte its merge-base blob with exactly the intended edit applied (`verify_blob`); grep for removed phrases expecting no hits; `claude plugin validate .` must pass.
- **Design blocks:** the spec `docs/superpowers/specs/2026-08-09-provider-blended-reviews-design.md` carries the exact insertion text as Blocks A–G. A `design_blocks` check re-reads them (via `read_blocks`, never retyped) and asserts each appears verbatim in its target, directly after its anchor line.
- **Driver model:** the session model is a launch choice, not a config key. Recommended opus driver; sonnet is a cost lever. Not part of this plan's config surface.

---

### Task 1: Provider policy + delegation mechanics in the pipeline SKILL.md (dev-flow)

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md` — insert Block A after the Docs policy section (after the line ending `...this file is input, not an artifact.`), before `**Doc git lifecycle — branch at design start.**`

**Interfaces:**
- Consumes: spec Block A (`docs/superpowers/specs/2026-08-09-provider-blended-reviews-design.md`).
- Produces: the `providers:` config contract and delegation command mappings that Tasks 2–3 rely on.

- [ ] **Step 1: Read the spec's Block A**

Run: `python3 scripts/design_blocks.py docs/superpowers/specs/2026-08-09-provider-blended-reviews-design.md`
Expected: the block shape and indices for Block A (the Provider policy block). This is the source of truth — never retype the block.

- [ ] **Step 2: Insert Block A into the pipeline SKILL.md**

Open `plugins/dev-flow/skills/dev-flow/SKILL.md`. Find the end of the Docs policy section — the paragraph ending `...this file is input, not an artifact.` — and the following line `**Doc git lifecycle — branch at design start.**`. Insert Block A's exact text (from the spec) between them, as its own paragraph block. The block is verbatim from the spec — copy it exactly, including the nested YAML fence and the markdown table.

- [ ] **Step 3: Verify the insertion**

Run: `grep -n "Provider policy" plugins/dev-flow/skills/dev-flow/SKILL.md`
Expected: a hit at the inserted location. Then run: `grep -n "shell-delegate to the codex companion" plugins/dev-flow/skills/dev-flow/SKILL.md` — expected a hit.

- [ ] **Step 4: Commit**

```bash
git add plugins/dev-flow/skills/dev-flow/SKILL.md
git commit -m "feat(dev-flow): provider policy + delegation mechanics for review tiers"
```

---

### Task 2: Task-reviewer routing + provenance in the pipeline SKILL.md (dev-flow)

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md` — append Block B to the Stage 3 "Per-task reviewer routing" bullet; append Block C to the Cross-Cutting Concerns "Review provenance is checked, not assumed" bullet.

**Interfaces:**
- Consumes: Task 1's `providers:` config contract.
- Produces: the routing rule (routine task-reviewers delegable, `risk: high` never) and the provenance format that Task 3's provenance change aligns with.

- [ ] **Step 1: Append Block B to the task-reviewer routing bullet**

In `plugins/dev-flow/skills/dev-flow/SKILL.md`, find the Stage 3 bullet beginning `- **Per-task reviewer routing:**`. Append Block B's exact text (from the spec) as new sentences at the end of that bullet, before the next bullet.

- [ ] **Step 2: Append Block C to the provenance bullet**

Find the Cross-Cutting Concerns bullet beginning `- **Review provenance is checked, not assumed.**`. Append Block C's exact text (from the spec) at the end of that bullet.

- [ ] **Step 3: Verify the insertions**

Run: `grep -n "never delegated" plugins/dev-flow/skills/dev-flow/SKILL.md` and `grep -n "accepts both forms" plugins/dev-flow/skills/dev-flow/SKILL.md`
Expected: one hit each, at the appended locations.

- [ ] **Step 4: Commit**

```bash
git add plugins/dev-flow/skills/dev-flow/SKILL.md
git commit -m "feat(dev-flow): delegate routine task-reviewers, dual-form provenance"
```

---

### Task 3: Adversarial-review SKILL.md changes (dev-flow)

**Files:**
- Modify: `plugins/dev-flow/skills/adversarial-review/SKILL.md` — append Block D to the "Review integrity (never inline)" paragraph; append Block E to the seed-passes section; append Block F to the Resolution step 6 provenance sentence.

**Interfaces:**
- Consumes: Task 1's delegation contract (delegated seed findings arrive as caller-supplied findings with `seeds: skipped`).
- Produces: the amended "never inline" rule and provenance format that the orchestrator's provenance check (Task 2) validates.

- [ ] **Step 1: Append Block D to the never-inline rule**

In `plugins/dev-flow/skills/adversarial-review/SKILL.md`, find the paragraph beginning `**Review integrity (never inline).**`. Append Block D's exact text (from the spec) at the end of that paragraph.

- [ ] **Step 2: Append Block E to the seed-passes section**

Find the seed-passes section (the paragraph ending `...the glossary's own state is never a finding: never flag it, never propose creating one.`). Append Block E's exact text (from the spec) as a new paragraph after it.

- [ ] **Step 3: Append Block F to the provenance sentence**

Find Resolution step 6's provenance sentence (the one beginning `Report back: ... a **provenance** line naming the reviewers actually spawned per tier`). Append Block F's exact text (from the spec) at the end of that sentence.

- [ ] **Step 4: Verify the insertions**

Run: `grep -n "shell-delegated one-shot" plugins/dev-flow/skills/adversarial-review/SKILL.md`, `grep -n "seeds: skipped" plugins/dev-flow/skills/adversarial-review/SKILL.md`, and `grep -n "delegated seed pass reports" plugins/dev-flow/skills/adversarial-review/SKILL.md`
Expected: one hit each.

- [ ] **Step 5: Mirror the insertions into dev-flow-worktree**

Apply the same three insertions (Blocks D, E, F) verbatim to `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md` at the analogous locations. The `adversarial-review/SKILL.md` pair is machine-checked line-for-line identical after `dev-flow-worktree` → `dev-flow`, so the text must match exactly.

- [ ] **Step 6: Verify the mirrored pair agrees**

Run: `python3 scripts/check-sync.py`
Expected: passes (this verifies the `adversarial-review/SKILL.md` pair is identical).

- [ ] **Step 7: Commit**

```bash
git add plugins/dev-flow/skills/adversarial-review/SKILL.md plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
git commit -m "feat(adversarial-review): allow shell-delegated seed passes, dual-form provenance"
```

---

### Task 4: Example configs (dev-flow)

**Files:**
- Create: `plugins/dev-flow/examples/dev-flow.local.work.md`
- Create: `plugins/dev-flow/examples/dev-flow.local.home.md`

**Interfaces:**
- Consumes: spec Block G (the two example configs).
- Produces: the reference configs that Task 5 mirrors and that document the two laptop setups.

- [ ] **Step 1: Create the work-laptop example**

Write `plugins/dev-flow/examples/dev-flow.local.work.md` with Block G's work config verbatim (from the spec): `docs: commit`, `seeds: codex`, `task-reviewers: codex`, `fixers: session`, `risk-high-reviewers: session`.

- [ ] **Step 2: Create the home-laptop example**

Write `plugins/dev-flow/examples/dev-flow.local.home.md` with Block G's home config verbatim (from the spec): `docs: commit`, `seeds: codex`, `task-reviewers: ollama-flash`, `fixers: session`, `risk-high-reviewers: session`.

- [ ] **Step 3: Verify the files**

Run: `cat plugins/dev-flow/examples/dev-flow.local.work.md plugins/dev-flow/examples/dev-flow.local.home.md`
Expected: the two configs, each with the `providers:` block from Block G.

- [ ] **Step 4: Commit**

```bash
git add plugins/dev-flow/examples/
git commit -m "docs(dev-flow): example provider configs for work and home laptops"
```

---

### Task 5: Mirror to dev-flow-worktree

**Files:**
- Modify: `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` — hand-mirror Tasks 1–2's pipeline SKILL.md changes (Blocks A, B, C), adapted to the worktree variant's wording where the two pipeline SKILL.md files already diverge.
- Create: `plugins/dev-flow-worktree/examples/dev-flow.local.work.md`, `plugins/dev-flow-worktree/examples/dev-flow.local.home.md` — byte-identical copies of Task 4's files.

**Interfaces:**
- Consumes: Tasks 1–4's edits.
- Produces: the mirrored plugin, so `check-sync.py` passes and both variants ship the feature.

- [ ] **Step 1: Hand-mirror the pipeline SKILL.md changes**

Open `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`. Apply the same three insertions as Tasks 1–2 (Block A after the Docs policy section; Block B appended to the task-reviewer routing bullet; Block C appended to the provenance bullet), matching the worktree variant's existing wording and section structure. The `providers:` config contract, delegation command mappings, and provenance format are identical to the dev-flow variant.

- [ ] **Step 2: Copy the example configs**

```bash
cp plugins/dev-flow/examples/dev-flow.local.work.md plugins/dev-flow-worktree/examples/dev-flow.local.work.md
cp plugins/dev-flow/examples/dev-flow.local.home.md plugins/dev-flow-worktree/examples/dev-flow.local.home.md
```

- [ ] **Step 3: Verify the mirror**

Run: `python3 scripts/check-sync.py`
Expected: passes. Then run: `grep -n "Provider policy" plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` — expected a hit.

- [ ] **Step 4: Commit**

```bash
git add plugins/dev-flow-worktree/
git commit -m "feat(dev-flow-worktree): mirror provider policy, routing, provenance, examples"
```

---

### Task 6: Version bumps + full verification

**Files:**
- Modify: `plugins/dev-flow/.claude-plugin/plugin.json` — `"version": "2.19.0"` → `"2.20.0"`.
- Modify: `plugins/dev-flow-worktree/.claude-plugin/plugin.json` — `"version": "1.21.0"` → `"1.22.0"`.

**Interfaces:**
- Consumes: all prior tasks' edits.
- Produces: the shippable, verified change.

- [ ] **Step 1: Bump both versions**

Edit both `plugin.json` files to the minor-bumped versions above.

- [ ] **Step 2: Write the design_blocks check**

Write a short `python3` check (e.g. `scripts/check-provider-blocks.py`) that `sys.path.insert(0, "scripts")`, calls `read_blocks(<spec>, <shape>)` (shape from `python3 scripts/design_blocks.py <spec>`), and asserts:
- Blocks A–F appear verbatim in the **dev-flow** files, each directly after its anchor line (end of Docs policy section for A; the routing bullet for B; the provenance bullet for C; the never-inline paragraph for D; the seed-passes section for E; the provenance sentence for F).
- Blocks A, B, C appear verbatim in the **dev-flow-worktree** pipeline SKILL.md, and Blocks D, E, F in the dev-flow-worktree adversarial-review SKILL.md (verbatim, no anchor assertion — the worktree variant's anchors differ).
- Block G's two configs match the two example files byte-for-byte.

Never retype the blocks — read them from the spec.

- [ ] **Step 3: Run the full verification battery**

```bash
python3 scripts/check-sync.py
python3 scripts/check-version-bump.py origin/main
python3 scripts/check-provider-blocks.py
claude plugin validate .
```

Expected: all pass. Then run the removed-phrase grep — for each phrase this change removes (none are removed; this is an insertion-only change, so grep for the new phrases expecting hits, and confirm no pre-existing phrase was dropped by diffing the SKILL.md files against their merge-base blobs with `verify_blob`).

- [ ] **Step 4: Commit**

```bash
git add plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json scripts/check-provider-blocks.py
git commit -m "chore: bump dev-flow to 2.20.0, dev-flow-worktree to 1.22.0"
```

---

## Self-Review

**Spec coverage:**
- `providers:` config (spec "Config") → Task 1 (Block A).
- Delegation command mappings (spec "Delegation mechanics") → Task 1 (Block A).
- Task-reviewer routing (spec "Approach") → Task 2 (Block B).
- Provenance dual-form (spec "Provenance") → Task 2 (Block C) + Task 3 (Block F).
- Never-inline amendment (spec "Skill contract") → Task 3 (Block D).
- Seed-pass skip (spec "Approach") → Task 3 (Block E).
- Example configs (spec "Example configs") → Task 4 + Task 5.
- Mirroring + version bumps (spec "Success criteria") → Task 5 + Task 6.
- Driver model (spec "Driver model") → documented in Global Constraints (launch choice, not config).

**Placeholder scan:** no TBD/TODO; every step names the exact block and location.

**Type consistency:** the `providers:` key names (`seeds`, `task-reviewers`, `fixers`, `risk-high-reviewers`) and provider values (`session`, `codex`, `ollama-<tier>`, `claude`) are identical across Blocks A–G and the spec's Config section.
