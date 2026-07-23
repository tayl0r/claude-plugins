# dev-flow Plugin Implementation Plan

> Revised 2026-07-22 by `2026-07-22-dev-flow-nested-review-fix-design.md` / `…-plan.md` (nested-review fix): stages spawn as `general-purpose`; the review halts loudly rather than inlining; a mandatory intake capability gate enforces nesting; provenance is forwarded and checked; no main-session fallback.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `dev-flow` plugin — a two-skill Claude Code plugin that carries a change from design → plan → execute → PR → merge autonomously, running a reusable `adversarial-review` protocol at each artifact boundary.

**Architecture:** A flat plugin (`plugins/dev-flow/`) containing two prose skills. `dev-flow/SKILL.md` is the single-entry orchestrator (invocation, stops, model policy, inherited-skills dispatch rule, artifact contract, five pipeline stages). `adversarial-review/SKILL.md` is the reusable, artifact-agnostic review protocol it calls at each stage. There is no code to compile and no test framework — the skills are markdown instructions that a running Claude session follows; verification is JSON validity, front-matter presence, required-section/consistency `grep` checks, and a manual smoke test.

**Tech Stack:** Markdown (`SKILL.md`), JSON (`plugin.json`, `marketplace.json`). Verification via `python3 -m json.tool` and `grep`. No new runtime dependencies.

**Source of truth:** `docs/superpowers/specs/2026-07-20-dev-flow-design.md`. Every skill section is a rendering of a named spec section into imperative skill voice; when in doubt, the spec wins. Work happens on the existing `dev-flow-plugin` branch.

## Global Constraints

These values are copied verbatim from the spec and MUST appear identically wherever they occur across both skills, the spec, and this plan:

- Plugin dir: `plugins/dev-flow/`; skill files at `plugins/dev-flow/skills/<skill>/SKILL.md`; plugin manifest at `plugins/dev-flow/.claude-plugin/plugin.json`.
- Repo conventions: `plugin.json` has `name`, `version` `"1.0.0"`, `description`. Marketplace entries use `"source": "./plugins/<name>"` (relative `./` form).
- Stop names — exactly these three: `post-design`, `post-plan`, `pre-merge`.
- Review modes — exactly these three: `design`, `plan`, `diff`.
- Branch naming: `dev-flow/<slug>` (slug is kebab-case, opaque, immutable).
- Doc paths: spec `docs/superpowers/specs/YYYY-MM-DD-<slug>-design.md`; plan `docs/superpowers/plans/YYYY-MM-DD-<slug>-plan.md`.
- Review marker (literal): `dev-flow: review clean @ <full-head-sha>`.
- Merge command (literal): `gh pr merge --squash --delete-branch`.
- Bounded CI wait: `gh pr checks <pr> --watch` under a hard cap (default 10 minutes; `--watch` has no native timeout, so enforce it with the Bash tool `timeout: 600000`), then halt-and-report on red or still-pending.
- Reviewer model policy: **group-resolution agents** run on `fable` (the adversary tier — different from the author; `opus` if the session model is Fable); **seed reviewers** run on `sonnet`; executors/fixers/orchestrator use the main session model.
- The design rubric text is reproduced **verbatim** from the spec's "The design rubric (verbatim …)" block — do not paraphrase it.
- No emojis in skill files. Match the prose density and structure of the existing `plugins/better-code-review/skills/better-code-review/SKILL.md`.

---

### Task 1: Plugin scaffold + marketplace registration

**Files:**
- Create: `plugins/dev-flow/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json` (append one entry to the `plugins` array)

**Interfaces:**
- Produces: the plugin manifest and marketplace entry that make `dev-flow` discoverable. Later tasks add the two skill files under `plugins/dev-flow/skills/`.

- [ ] **Step 1: Write the manifest**

Create `plugins/dev-flow/.claude-plugin/plugin.json`:

```json
{
  "name": "dev-flow",
  "version": "1.0.0",
  "description": "Autonomous design -> plan -> execute -> PR -> merge pipeline with adversarial review at each artifact boundary"
}
```

- [ ] **Step 2: Register in the marketplace**

In `.claude-plugin/marketplace.json`, append this object to the `plugins` array (keep valid JSON — add a comma after the previous last entry):

```json
    {
      "name": "dev-flow",
      "source": "./plugins/dev-flow",
      "description": "Autonomous design -> plan -> execute -> PR -> merge pipeline with adversarial review at each artifact boundary"
    }
```

- [ ] **Step 3: Verify both JSON files parse**

Run:
```bash
python3 -m json.tool plugins/dev-flow/.claude-plugin/plugin.json >/dev/null && echo PLUGIN_OK
python3 -m json.tool .claude-plugin/marketplace.json >/dev/null && echo MARKETPLACE_OK
```
Expected: `PLUGIN_OK` then `MARKETPLACE_OK` (any parse error means malformed JSON — fix the trailing comma).

- [ ] **Step 4: Verify the marketplace entry is present and well-formed**

Run:
```bash
python3 -c "import json; e=[p for p in json.load(open('.claude-plugin/marketplace.json'))['plugins'] if p['name']=='dev-flow'][0]; assert e['source']=='./plugins/dev-flow', e; print('ENTRY_OK', e['source'])"
```
Expected: `ENTRY_OK ./plugins/dev-flow`

- [ ] **Step 5: Commit**

```bash
git add plugins/dev-flow/.claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "Scaffold dev-flow plugin and register in marketplace"
```

---

### Task 2: `adversarial-review` skill

Build the reusable, artifact-agnostic review protocol first — `dev-flow` (Tasks 3–4) references it, so it should exist and be reviewable on its own.

**Files:**
- Create: `plugins/dev-flow/skills/adversarial-review/SKILL.md`

**Interfaces:**
- Consumes: nothing (self-contained; may reference the harness `/simplify` angles by name and the superpowers `code-reviewer.md` template).
- Produces: a skill invoked as `adversarial-review(target, mode)` with `mode ∈ {design, plan, diff}`. `dev-flow` stages call it and rely on: it is findings-only in its seed phase, it applies value-gated fixes with main-model fixers, it preserves front-matter on doc rewrites, and it reports every new issue filed.

- [ ] **Step 0: Read the source of truth**

Read `docs/superpowers/specs/2026-07-20-dev-flow-design.md` in full (this skill renders its "Seed passes", "The design rubric", "Resolution procedure", and "Where new issues are filed" sections) and the "Global Constraints" section of `docs/superpowers/plans/2026-07-20-dev-flow-plan.md`. The steps below summarize what to transcribe; the spec is the authoritative wording.

- [ ] **Step 1: Create the skill with front-matter and signature**

Create `plugins/dev-flow/skills/adversarial-review/SKILL.md` beginning with:

```markdown
---
name: adversarial-review
description: Use to run a rigorous adversarial review on a single artifact — a design doc, a plan doc, or a PR/diff. Seeds with findings-only quality and correctness passes, then groups issues and resolves each to the best long-term design with adversarial self-checks. Triggers on "adversarial review", "review this design/plan/PR properly", or is called internally by dev-flow at each stage.
---

# Adversarial Review

Run a rigorous adversarial review on ONE target artifact and resolve every finding to the best long-term design, applying only fixes that earn their place.

**Invocation:** `adversarial-review(target, mode)` where `mode` is one of `design`, `plan`, `diff`.
- When called by dev-flow, the mode is passed explicitly.
- Standalone, infer the mode: a path under `specs/` -> `design`; under `plans/` -> `plan`; a PR number, branch, or SHA range -> `diff`.
```

- [ ] **Step 2: Write the "Seed passes" section**

Transcribe the spec's "Seed passes" section (including the mode×seed table) into skill voice. It MUST state:
- Every mode runs two findings-only reviewer subagents in parallel on the reviewer model: a **quality seed** and a **correctness seed**. Findings-only is a property of the seed prompts — they never edit.
- **diff / quality:** inline `/simplify`'s four angles, findings-only, against BASE..HEAD. Do NOT invoke the `/simplify` skill (it applies fixes and re-derives its own scope, breaking findings-only and the model policy); it is a harness built-in with no readable file, so transcribe these one-line angle definitions **verbatim** into the skill:
  - **Reuse:** does this duplicate an existing utility/abstraction it could call instead? Consolidate the duplication.
  - **Simplification:** can the same behavior be expressed more simply — fewer branches, less indirection, dead code removed, clearer control flow?
  - **Efficiency:** needless work — redundant calls, repeated computation, avoidable queries/allocations, N+1 patterns.
  - **Altitude:** is the change at the right level of abstraction — not hand-rolling what a higher-level seam already handles, not over-abstracting a one-off? Put the logic at the right layer.
- **diff / correctness:** the superpowers `code-reviewer.md` template used as designed (already read-only) — specifically the one in the `requesting-code-review` skill directory (`.../skills/requesting-code-review/code-reviewer.md`; **not** the other `code-reviewer.md` files under `feature-dev`/`pr-review-toolkit`/older superpowers versions). Placeholders filled from the PR summary, plan path, and branch BASE/HEAD.
- **design / quality:** the design rubric (Step 3) is the lens, applied adversarially to the proposed approach.
- **design / correctness:** prose-integrity checklist — placeholders/TBDs, internal contradictions, planning-blocking ambiguity, unstated assumptions, missing/untestable success criteria.
- **plan / quality:** the rubric applied to the approach and to embedded code sketches.
- **plan / correctness:** the prose checklist plus task ordering/dependencies, each task executable by a fresh context-free subagent, per-task verification steps, and drift from the design doc.

- [ ] **Step 3: Paste the design rubric verbatim**

Copy the nine-bullet rubric from the spec's "The design rubric (verbatim …)" block into a `## The design rubric` section, unchanged. (This is the exact text starting "Best long-term design over short-term tradeoffs…" and ending "…if the fix is worse than the wart, leave it.")

- [ ] **Step 4: Write the "Resolution procedure" section**

Transcribe the spec's numbered "Resolution procedure" into skill voice. It MUST include, in order:
1. Collect seed findings (plus, in diff mode at dev-flow Stage 4, SDD's unresolved Minor findings).
2. Group similar issues; spawn one reviewer-model agent per group.
3. Each group-agent: research all its issues; determine the best long-term design per issue using the rubric, judging the group's findings together; perform an **inline** adversarial self-check (try to break its own conclusion) — **group-agents never invoke `adversarial-review` or spawn further reviewer agents; exactly two tiers exist (seed reviewers, group resolvers); recursion is forbidden**; if not confident after "what more research do I need?", file a new issue and move on.
4. Apply each resolved fix regardless of severity **only if it earns its place** (fixer agents, main model); skip if the fix is worse than the wart or is an over-engineered fix for a rare edge case.
5. Rewrite the artifact: for design/plan docs, rewrite incorporating resolutions and **preserve the `dev-flow` front-matter block**; for a diff, apply fixes to the branch and commit.
6. Report every new issue filed.

- [ ] **Step 5: Write "Model" and "Where new issues are filed" sections**

- `## Model`: state the model policy verbatim from Global Constraints (group-resolvers on `fable` ≠ author, `opus` if session is Fable; seed reviewers on `sonnet`; executors/fixers/orchestrator on the main model).
- `## Where new issues are filed`: `gh issue create` when a GitHub remote exists, else append to `docs/superpowers/issues/BACKLOG.md`; surface all filed issues in the report.

- [ ] **Step 6: Verify front-matter and required sections**

Run:
```bash
f=plugins/dev-flow/skills/adversarial-review/SKILL.md
head -5 "$f" | grep -q "^name: adversarial-review$" && echo NAME_OK
head -5 "$f" | grep -q "^description:" && echo DESC_OK
grep -q "Best long-term design over short-term tradeoffs" "$f" && echo RUBRIC_OK
grep -Eq "never invoke .?adversarial-review.? or spawn further reviewer" "$f" && echo NORECURSE_OK
grep -q "findings-only" "$f" && echo FINDINGS_ONLY_OK
grep -Eq 'one of .*`design`.*`plan`.*`diff`' "$f" && echo MODES_OK || echo MODES_MISSING
```
Expected: `NAME_OK`, `DESC_OK`, `RUBRIC_OK`, `NORECURSE_OK`, `FINDINGS_ONLY_OK`, `MODES_OK`. (The mode check greps the pinned invocation line from Step 1, not bare words — `\bdesign\b` matches ordinary prose and would never fail.)

- [ ] **Step 7: Commit**

```bash
git add plugins/dev-flow/skills/adversarial-review/SKILL.md
git commit -m "Add adversarial-review skill (reusable per-artifact review protocol)"
```

---

### Task 3: `dev-flow` skill — rules & contract

Create the orchestrator skill file with everything *above* the pipeline stages. Task 4 appends the stages to the same file.

**Files:**
- Create: `plugins/dev-flow/skills/dev-flow/SKILL.md`

**Interfaces:**
- Consumes: the `adversarial-review` skill (Task 2).
- Produces: the front-matter, invocation/stops, model policy, inherited-skills dispatch rule, and Artifact Contract that Task 4's stages reference by name.

- [ ] **Step 0: Read the source of truth**

Read `docs/superpowers/specs/2026-07-20-dev-flow-design.md` in full (this task renders its "Invocation", "Stops", "Model Policy", "Dispatching to Inherited Skills", and "Artifact Contract" sections) and the "Global Constraints" section of this plan. The steps below summarize; the spec is the authoritative wording.

- [ ] **Step 1: Create the file with front-matter and overview**

Create `plugins/dev-flow/skills/dev-flow/SKILL.md` beginning with:

```markdown
---
name: dev-flow
description: Use when the user wants to run their end-to-end dev flow — carry a change from design to plan to execute to PR to merge autonomously, with adversarial review at each stage. Triggers on "run dev-flow", "run my dev flow", "dev-flow on <design file>", "continue dev-flow on <slug>", or "take this design to a merged PR".
---

# dev-flow

Carry a change from design -> plan -> execute -> PR -> merge in one invocation. Default is full-auto to merge; the user can opt into a stop at any artifact boundary. Each stage runs in a fresh subagent so this orchestrator's context stays thin, and all state lives in durable artifacts (the Artifact Contract) so a run resumes cleanly after any stop or crash.

This is the only skill the user invokes. It calls the `adversarial-review` skill internally at each boundary.
```

- [ ] **Step 2: Write "Invocation" and "Stops"**

Transcribe the spec's "Invocation" and "Stops" sections. MUST include: the three stop names `post-design`, `post-plan`, `pre-merge` with their effects; default = none for design-file entry, `post-design` for bare-idea entry (opt out with "full auto"); stops persist to design front-matter; precedence explicit-this-invocation > recorded front-matter > full-auto default; every halt report prints the exact resume invocation.

- [ ] **Step 3: Write "Model Policy" and "Dispatching to Inherited Skills"**

- `## Model Policy`: the reviewer invariant from Global Constraints.
- `## Dispatching to Inherited Skills`: the shared-boundary rule verbatim from the spec — the three dispositions (**pre-answered / superseded / halted**), "never invents an answer to an unanticipated gate", and the four corollaries (brainstorming can't be dispatched; integration only where a stage says; red tests at any gate halt; rule targets user-directed seams only). State that this preamble is carried in every stage-dispatch prompt.

- [ ] **Step 4: Write "Artifact Contract"**

Transcribe the spec's "Artifact Contract" section, including: slug derivation + immutability; `dev-flow/<slug>` branch naming; the intake collision check; the front-matter schema (design: `slug` + `stops`; plan: `slug` + `spec`); the branch+worktree-at-design-start doc lifecycle and adopt-existing-file flow; commit-only-post-review; execution-complete = committed `- [ ]` checkboxes (ledger is scratch) with the tie-break; the `dev-flow: review clean @ <full-head-sha>` PR marker; and the full resume table (reproduce the table rows exactly).

- [ ] **Step 5: Verify front-matter, invariant strings, and resume table**

Run:
```bash
f=plugins/dev-flow/skills/dev-flow/SKILL.md
head -5 "$f" | grep -q "^name: dev-flow$" && echo NAME_OK
head -5 "$f" | grep -q "^description:" && echo DESC_OK
for s in post-design post-plan pre-merge; do grep -q "$s" "$f" || echo "MISSING_STOP:$s"; done; echo STOPS_CHECKED
grep -q "dev-flow/<slug>" "$f" && echo BRANCH_OK
grep -q "dev-flow: review clean @" "$f" && echo MARKER_OK
grep -Eq "pre-answer|pre-answered" "$f" && grep -q "superseded" "$f" && grep -Eq "halt" "$f" && echo DISPATCH_RULE_OK
grep -q "Plan fully checked; no open PR" "$f" && echo RESUME_TABLE_OK
```
Expected: `NAME_OK`, `DESC_OK`, `STOPS_CHECKED` with no `MISSING_STOP:`, `BRANCH_OK`, `MARKER_OK`, `DISPATCH_RULE_OK`, `RESUME_TABLE_OK`.

- [ ] **Step 6: Commit**

```bash
git add plugins/dev-flow/skills/dev-flow/SKILL.md
git commit -m "Add dev-flow skill rules and artifact contract"
```

---

### Task 4: `dev-flow` skill — pipeline stages

Append the five pipeline stages plus environment/cross-cutting notes to the file created in Task 3.

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md` (append after the Artifact Contract)

**Interfaces:**
- Consumes: the Artifact Contract and inherited-skills rule (Task 3); the `adversarial-review` skill (Task 2).
- Produces: the complete orchestrator. No later task depends on new symbols.

- [ ] **Step 0: Read the source of truth**

Read `docs/superpowers/specs/2026-07-20-dev-flow-design.md` in full (this task renders its five "Pipeline" stages plus "Environment Assumptions" and "Cross-Cutting Concerns") and the "Global Constraints" section of this plan. The steps below summarize; the spec is the authoritative wording.

- [ ] **Step 1: Write "Pipeline" intro + Stage 1 (Design)**

Append a `## Pipeline` heading (note: each stage runs in a fresh subagent carrying the inherited-skills preamble and returns only a short summary). Then `### Stage 1 — Design`, transcribing the spec: fix slug + create `dev-flow/<slug>` + worktree (worktree setup/baseline deferred to Stage 3); design-file entry adopts the file; bare-idea entry uses the inlined non-interactive protocol (explore context; scope/decomposition check -> halt-and-report if multi-subsystem; 2–3 approaches with recorded choice; record defensible-default assumptions, halt on genuinely blocking ambiguity; spec self-review checklist) — **brainstorming is NOT invoked**; run `adversarial-review` mode `design`; rewrite preserving front-matter; commit; bare-idea defaults to `post-design`.

- [ ] **Step 2: Write Stage 2 (Plan)**

`### Stage 2 — Plan`: dispatch `superpowers:writing-plans` against the design to `docs/superpowers/plans/YYYY-MM-DD-<slug>-plan.md` (front-matter links the spec); run `adversarial-review` mode `plan`; rewrite; commit on the branch; `post-plan` stop -> halt and report.

- [ ] **Step 3: Write Stage 3 (Execute)**

`### Stage 3 — Execute`: dispatch `superpowers:subagent-driven-development` with the overrides from the spec — run deferred worktree setup + baseline (consent pre-declared yes; **red baseline halts**); **exit condition supersedes SDD's terminal** (tasks done + reviews clean + full suite green + named branch; do NOT run SDD's final whole-branch review; do NOT invoke `finishing-a-development-branch`); plan-vs-code conflicts resolved by the design doc else halt; SDD `BLOCKED` "plan is wrong" -> halt; on each task-review-clean, tick that task's plan checkboxes and commit. Report branch, commit range, ledger path, unresolved Minor findings.

- [ ] **Step 4: Write Stage 4 (PR) + Stage 5 (Merge)**

`### Stage 4 — PR`: `gh pr create` (body links spec + plan); run `adversarial-review` mode `diff` — **this is the pipeline's final whole-branch review** and also ingests Stage 3's Minor-findings list; apply fixes on the branch (main model), commit, push; post the `dev-flow: review clean @ <full-head-sha>` marker comment; `pre-merge` stop -> halt with testing note + resume invocation.

`### Stage 5 — Merge`: confirm marker SHA == head (else re-review); bounded CI wait — run `gh pr checks <pr> --watch` under a hard cap (default 10 minutes, enforced with the Bash tool `timeout: 600000` since `--watch` has no native timeout; on timeout treat as still-pending) (red -> halt; still pending -> halt "CI still pending"); consult `stops` (a `pre-merge` stop pauses with the testing note); else `gh pr merge --squash --delete-branch`; cleanup (remove the pipeline-created worktree, `git worktree prune`, cd to main root first, only worktrees dev-flow created); final report = what shipped + every new issue filed across all stages.

- [ ] **Step 5: Write "Environment Assumptions" and "Cross-Cutting Concerns"**

Transcribe both spec sections: subagent nesting requires `Agent` + `Skill` tools on subagents, enforced by a mandatory intake capability probe that halts loudly rather than degrading — no main-session fallback (see `2026-07-22-dev-flow-nested-review-fix-design.md`); GitHub remote assumed from Stage 4 on; context hygiene; failure handling with resume invocation; idempotent resume via the Artifact Contract; severity-independent but value-gated.

- [ ] **Step 6: Verify all stages and key mechanisms are present**

Run:
```bash
f=plugins/dev-flow/skills/dev-flow/SKILL.md
for s in "Stage 1" "Stage 2" "Stage 3" "Stage 4" "Stage 5"; do grep -q "$s" "$f" || echo "MISSING:$s"; done; echo STAGES_CHECKED
grep -q "finishing-a-development-branch" "$f" && echo SUPPRESS_FINISH_OK
grep -q "gh pr merge --squash --delete-branch" "$f" && echo MERGE_CMD_OK
grep -q "gh pr checks --watch" "$f" && echo CI_WAIT_OK
grep -Eq "tick .*checkbox|checkboxes and commit|tick that task" "$f" && echo CHECKBOX_OK
grep -q "brainstorming is NOT invoked" "$f" || grep -qi "not invoke.*brainstorming\|brainstorming is not invoked" "$f" && echo NO_BRAINSTORM_OK
```
Expected: `STAGES_CHECKED` with no `MISSING:`, `SUPPRESS_FINISH_OK`, `MERGE_CMD_OK`, `CI_WAIT_OK`, `CHECKBOX_OK`, `NO_BRAINSTORM_OK`.

- [ ] **Step 7: Commit**

```bash
git add plugins/dev-flow/skills/dev-flow/SKILL.md
git commit -m "Add dev-flow pipeline stages and environment notes"
```

---

### Task 5: README + cross-file consistency validation

Add a concise plugin README and run the checks that only make sense across the finished files.

**Files:**
- Create: `plugins/dev-flow/README.md`

**Interfaces:**
- Consumes: both finished skills.
- Produces: user-facing docs + a green consistency sweep. Nothing depends on this task.

- [ ] **Step 1: Write the README**

Create `plugins/dev-flow/README.md` — concise (roughly 30–50 lines): what the plugin does (one paragraph), the single entry point and the three invocation forms (bare idea, design file, continue), the three stops and their defaults (bare-idea -> `post-design`, design-file -> full-auto), a one-line note that `adversarial-review` is internal but standalone-invokable, and the "How to smoke-test" procedure from the spec's "How We'll Know It Works" (run to `post-design` on a small change, then resume). No emojis.

- [ ] **Step 2: Cross-file consistency — stop names, modes, marker, branch pattern**

Run (checks the two skills agree with each other and the spec):
```bash
dv=plugins/dev-flow/skills/dev-flow/SKILL.md
ar=plugins/dev-flow/skills/adversarial-review/SKILL.md
spec=docs/superpowers/specs/2026-07-20-dev-flow-design.md
# the three canonical stop names are present; no stray variants
for s in post-design post-plan pre-merge; do grep -q "$s" "$dv" || echo "MISSING_STOP:$s"; done; echo STOPS_PRESENT
grep -Eq "post-pr|post-merge|pre-plan" "$dv" && echo "STRAY_STOP_TOKEN (fix it)" || echo NO_STRAY_STOP
# adversarial-review pins the mode contract line
grep -Eq 'one of .*`design`.*`plan`.*`diff`' "$ar" && echo AR_MODES_OK || echo AR_MODES_MISSING
# marker string identical in skill and spec
grep -q "dev-flow: review clean @" "$dv" && grep -q "dev-flow: review clean @" "$spec" && echo MARKER_CONSISTENT
# dev-flow references adversarial-review by name
grep -q "adversarial-review" "$dv" && echo REFERENCES_REVIEW_SKILL
```
Expected: `STOPS_PRESENT` with no `MISSING_STOP:`, `NO_STRAY_STOP`, `AR_MODES_OK`, `MARKER_CONSISTENT`, `REFERENCES_REVIEW_SKILL`. If `STRAY_STOP_TOKEN` or `AR_MODES_MISSING` appears, fix the offending file and re-run.

- [ ] **Step 3: Whole-plugin JSON + discoverability re-check**

Run:
```bash
python3 -m json.tool plugins/dev-flow/.claude-plugin/plugin.json >/dev/null && echo PLUGIN_JSON_OK
python3 -c "import json; ps=json.load(open('.claude-plugin/marketplace.json'))['plugins']; assert any(p['name']=='dev-flow' and p['source']=='./plugins/dev-flow' for p in ps); print('DISCOVERABLE_OK')"
ls plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow/skills/adversarial-review/SKILL.md && echo BOTH_SKILLS_PRESENT
```
Expected: `PLUGIN_JSON_OK`, `DISCOVERABLE_OK`, both paths listed, `BOTH_SKILLS_PRESENT`.

- [ ] **Step 4: Commit**

```bash
git add plugins/dev-flow/README.md
git commit -m "Add dev-flow README and validate plugin consistency"
```

---

## Manual smoke test (after Task 5, requires a Claude Code session reload to pick up the new plugin)

Not an automated step — this is how the user confirms the plugin works end-to-end:

1. Reload Claude Code so the `dev-flow` and `adversarial-review` skills are listed.
2. On a throwaway idea, invoke: `run dev-flow: <small change>`. Confirm it creates `dev-flow/<slug>` + worktree, drafts a design with `dev-flow` front-matter, runs `adversarial-review`, and **halts at `post-design`** (bare-idea default) printing a resume invocation.
3. `continue dev-flow on <slug>` and confirm it resumes at Plan, then Execute (checkboxes ticked and committed).
4. Confirm the PR gets the `dev-flow: review clean @ <sha>` marker, a `pre-merge` stop pauses with a testing note, and merge uses `--squash --delete-branch` with worktree cleanup.

---

## Self-Review

**Spec coverage:** Packaging (T1), `adversarial-review` incl. seed matrix/rubric/resolution/model/issue-filing (T2), Invocation+Stops+Model+Dispatch rule+Artifact Contract (T3), all five stages + Environment/Cross-Cutting (T4), "How We'll Know It Works" (T5 README + manual smoke test). Non-Goals and "Decisions Locked" are constraints, not build tasks — enforced via Global Constraints. No spec section is left without a task.

**Placeholder scan:** No "TBD"/"handle edge cases"/"similar to Task N". Skill bodies are specified as verbatim transcriptions of named spec sections with the error-prone literal strings pinned in Global Constraints — the spec is the DRY source, deliberately not re-pasted in full here.

**Type consistency:** Invariant strings (`post-design`/`post-plan`/`pre-merge`, `design`/`plan`/`diff`, `dev-flow/<slug>`, `dev-flow: review clean @ <full-head-sha>`, `gh pr merge --squash --delete-branch`) are defined once in Global Constraints and every task's verify step greps for those exact forms; Task 5 cross-checks them between files.
