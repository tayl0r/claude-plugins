---
dev-flow:
  slug: produce-agent-tiers
  stops: [pre-merge]
  docs: commit
---
# Produce-subagents get their own pinned model tier

## Status

Revised 2026-08-07 after adversarial review. Changes from the first draft: the **opus tier resolves to `deepseek-v4-pro:cloud` on Ollama** (not `glm-5.2`), the **flash driver is a defended choice** rather than an accident, the two frontmatter-identical produce agents collapse to **one** dispatched twice, the SDD per-task reviewer is **risk-scaled** rather than blanket-session-model (the risky-task reviewer pinned as a second agent, the `risk: high` marker given a contract and plan-review preservation), and the Launch contract is reframed as a **reference** whose guard is the in-pipeline provenance check (pins hold today). Approved for implementation. Maps onto the output-per-cost goal: better output where it pays, cheaper where it does not.

## Problem

The dev-flow pipeline's **produce** work — bare-idea design drafting (Stage 1) and plan writing (Stage 2) — runs in a fresh `general-purpose` produce-subagent on **the main session model** (Model Policy, `SKILL.md:46`; pipeline intro, `SKILL.md:205`; Stage 2, `SKILL.md:224`). That couples two independent choices:

- **What the driver runs on** is a launch-time choice the user makes per session (Ollama: `deepseek-v4-flash` workhorse; Anthropic: `claude-sonnet`).
- **What drafts the design and plan** is then forced to be the same model — so on an Ollama flash session, the two most output-sensitive artifacts in the pipeline (the spec that every later stage and the review judge against, and the plan that SDD implements verbatim) get drafted by the cheapest workhorse in the stack.

Meanwhile the review stages already have per-tier pins via agent definitions (ADR 0004): seeds `claude-sonnet-4-6`, resolvers `claude-opus-4-8`. Produce work has no tier — it inherits whatever the driver was launched with.

The goal is **better or equal output at lower or equal cost** across the pipeline. Design and plan drafting is where a stronger model buys the most (they shape everything downstream); the driver, executors, and fixers are where the workhorse is fine. Today both share the driver's model, so the stronger tier is unavailable on a flash session.

## Current model layout

| Stage / role | Model today | Runs as |
|---|---|---|
| Driver (orchestrator) | session model (Ollama: flash; Anthropic: sonnet) | in-context |
| Produce-subagent — design draft (Stage 1) | **session model** (`general-purpose`) | spawned leaf |
| Produce-subagent — plan write (Stage 2) | **session model** (`general-purpose`) | spawned leaf |
| Review seed | `claude-sonnet-4-6` (agent pin) | spawned leaf |
| Review resolver | `claude-opus-4-8` (agent pin) | spawned leaf |
| Executor / fixer (SDD leaves) | session model | spawned leaf |
| SDD per-task reviewer (gate) | orchestrator's per-task choice (SDD Model Selection) | spawned leaf |

On an Ollama session the session model is the flash workhorse, so today **design and plan are drafted by flash** — the same cheap tier the review *seed* runs on, *not* the opus tier the *resolver* runs on (the resolver is pinned to `claude-opus-4-8` and resolves through the opus alias regardless of the driver). That is the waste: the highest-leverage artifacts get the cheapest model, and the stack has no way to spend more there.

## Design

Give the produce-subagent its own dedicated agent definition, pinned to the existing review **opus tier** (like the resolver), and dispatch it for both Stage 1 and Stage 2. The risky-task reviewer — the one SDD role whose model was an unexamined per-task choice — gets the same pinning treatment (§1). This follows SDD's Model Selection rubric (`subagent-driven-development/SKILL.md:157-192`): architecture and design tasks take the most capable model, and the plan is the contract the most expensive stage implements verbatim — the artifact that makes cheap executors viable. Then let the launch environment (Ollama `ollama cp` aliases / Anthropic session model) decide what each tier actually resolves to.

### 1. Two new agent definitions

`plugins/dev-flow/agents/produce-subagent.md`:

```
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

One agent, dispatched twice. The first draft proposed two agents (`design-drafter`, `plan-writer`); they were frontmatter-identical (both `claude-opus-4-8`, no `tools`, no per-stage body), differing only in the skill the dispatch carries. Two files would have been a mirror pair maintained for no behavioral divergence. One agent with a generic body and two dispatches is simpler and removes a mirror pair — widen only against concrete demand, and no planned divergence exists (rubric: value simplicity; widen only against concrete demand, never speculation).

The risky-task reviewer gets the same pinning treatment — a second agent, `plugins/dev-flow/agents/task-reviewer.md`:

```
---
name: task-reviewer
description: Per-task review gate for dev-flow's Execute stage, spawned by the orchestrator (SDD's controller) for plan-marked risky tasks. Pinned to claude-opus-4-8.
model: claude-opus-4-8
---

You are a **task-reviewer** for dev-flow — the per-task review gate SDD's controller
spawns after a `risk: high` task. You check the task's own verification command and
report pass/fail plus findings; you do not fix, rewrite, or implement.

The dispatch names the task (its `## Task N` section text), its verification command, and the absolute working-directory
path. Run the verification, check the diff against the task's `## Task N` section, and
report. Address the absolute working-directory path explicitly — with `git -C <path>`
and absolute file paths — and never rely on inherited cwd.

**The first line of your summary must be the model your own system prompt names**
(e.g. `claude-opus-4-8`), so the orchestrator can verify the tier you ran on.
```

The produce-subagent pins `claude-opus-4-8` — the same dated id as the review resolver — and the risky-task reviewer pins the same id, so the **opus tier** spans produce-subagent (both stages), resolver, and risky-task reviewer, and all are tuned against the same model on Anthropic and resolve through the same `ollama cp claude-opus-4-8 → <model>` alias on Ollama. The fix-loop escalation is not a pinned tier: it deliberately targets the family alias `model: opus` (strongest available), a defended divergence from ADR 0004, which pins review tiers, not implementer escalations. The **sonnet tier** (the `claude-sonnet-4-6` pin) is left with a single role — the review seed, a findings-only pass that SDD's rubric puts on a cheap-to-mid tier. (On Ollama the flash model that pin resolves to also serves the driver, executors, and routine per-task reviewer — but those are session-model roles, not the sonnet pin.) Pinning is per ADR 0004: agent frontmatter is the only place a dated id survives, the spawn must use the **plugin-qualified** name (`dev-flow:produce-subagent`), and the skill must **not** pass a `model` parameter at the produce spawn sites (that would silently un-pin).

**Why pin produce, not let it inherit like the executors?** Executors do bulk-token, mostly-mechanical work where the workhorse is fine and the turn count dominates cost — inheritance is correct there. Produce does the opposite: few tokens, outsized downstream leverage (the spec gates every later stage; the plan is implemented verbatim), and it must be reproducible — a design or plan that drifts with the driver's launch is a silent correctness variable. A dated-id pin makes the produce tier a fixed, verifiable quantity, independent of whatever the user launched the driver on, and couples it to the resolver so the artifacts and the judgment that reviews them come from the same tier. The coupling is a cost as well as a feature: the final judgment tier now shares the author's training blind spots, a stronger coupling than the same-family review ADR 0002 accepted — accepted here for the same reason ADR 0002 accepted same-family review, that the independence which survives is contextual (fresh context, adversarial prompt, cross-family sonnet seeds).

Two SDD roles get their model routing **named and decided** — the per-task reviewer's was an unexamined per-task choice under SDD's Model Selection, not session-model inheritance:

- **SDD per-task reviewer** (the gate the orchestrator, as SDD's controller, spawns after each task — `SKILL.md` Stage 3) — **session model by default; opus tier for plan-marked risky tasks.** This is a triage gate ("did the task's own verification command pass?"), not a judgment call: same-model review of a routine task is fine because the gate is mechanical, and cross-model judgment is centralized at the Stage 4 opus resolver, where shared-bias-breaking belongs. The one place same-model review is dangerous is a subtle task (concurrency, auth, state machines, subtle invariants) where the implementer's blind spot is the reviewer's — so the plan-writer marks those tasks at plan time (a `risk: high` line in the `## Task N` section), and the orchestrator spawns that task's reviewer as `dev-flow:task-reviewer` — a new pinned opus-tier leaf (above), the same dated id as the resolver, so the risky-task review and the final resolver judgment come from the same tier. This follows SDD's own model-selection logic, which already escalates the implementer for subtle tasks ("a small mechanical diff does not need the most capable model; a subtle concurrency change does") — the reviewer escalates on the same signal. The previous "at least as capable as the implementers it reviews" justification is dropped: it was a capability-floor claim about a gate that isn't a capability problem.
- **Fix-loop escalation** (SDD rounds 4-5: "a model at least one tier above the implementer that got stuck") — on Ollama the sonnet tier *is* flash, so the ladder must escalate to the **opus alias**: `model: opus` at the spawn site, resolving via `ANTHROPIC_DEFAULT_OPUS_MODEL`. On Anthropic, escalate to opus. This is a deliberate family-alias escalation, not a pinned tier: the point is the strongest available model, and ADR 0004 pins review tiers, not implementer escalations — so on Anthropic the fix-loop may land on a newer Opus than the pinned `claude-opus-4-8` review tier, and that is intended.

### 2. Skill edits (dev-flow `SKILL.md`)

- **Model Policy (line 46):** `The orchestrator spawns produce-subagents and executors on the main session model` becomes `The orchestrator spawns produce-subagents on the opus tier via their agent pin, and executors on the main session model`. The bookkeeping sentence and the reviewer-selection-ownership note (delegated to `adversarial-review`) are unchanged.
- **Pipeline intro (line 205):** the "runs in a fresh `general-purpose` produce-subagent" clause becomes "runs in a fresh `dev-flow:produce-subagent` (the pinned opus-tier leaf)", and the "writes its draft into the working checkout (repo root, which is on the feature branch)" clause becomes "writes its draft to the absolute output path the dispatch names (the design/plan doc path under the repo root, which is on the feature branch)" — the dispatch now carries the absolute working-directory path and the absolute output path (per the agent body), so the leaf never relies on inherited cwd. The leaf still carries the inherited-skills preamble, still returns a short summary.
- **Stage 1 issue entry (line 211) and bare-idea entry (line 212):** dispatch `dev-flow:produce-subagent` instead of a bare produce-subagent, carrying the absolute working-directory path and the absolute output path (the design doc path). The bare-idea entry's "written into the working checkout on the feature branch" becomes "written to the absolute output path the dispatch names (under the repo root on the feature branch)". The inlined non-interactive brainstorming protocol and docs policy are unchanged.
- **Stage 2 (line 224):** spawn `dev-flow:produce-subagent` (which runs `superpowers:writing-plans`) instead of a bare subagent, carrying the absolute working-directory path and the absolute output path (the plan doc path). Add to the writing-plans instruction: **mark risky tasks** — a `risk: high` line in any `## Task N` section whose work touches concurrency, auth, state machines, or other subtle invariants, so Stage 3 can route its reviewer to the opus tier. The marker's contract: a line `risk: high` (lowercase, single space after the colon) anywhere in the `## Task N` section; the orchestrator treats the task as risky iff its section — the span `task-brief` extracts, the text between `## Task N` and the next task heading — contains a line matching `risk: high` (case-insensitive on the value). A `risk:` line with any other value, or in a non-task section, is ignored by the orchestrator and flagged by the plan review's correctness seed; a task with multiple `risk:` lines is risky iff any is `risk: high`. The self-sufficiency instruction is unchanged.
- **Stage 3 (Execute):** as SDD's controller, the orchestrator spawns each per-task reviewer on the session model, except for a task whose `## Task N` section carries `risk: high` (per the marker contract in the Stage 2 edit), whose reviewer it spawns as `dev-flow:task-reviewer` (the pinned opus-tier leaf). Require the per-task reviewer to state its model as the first line of its report, and verify it against the expected tier — the session model for routine tasks, the opus tier for `risk: high` tasks — halting on a mismatch. This is the same self-report seam the produce-subagent and review leaves use, and it makes the per-task reviewer's model observable for the live check. Fix-loop escalation: SDD's ladder says "a model at least one tier above the implementer that got stuck"; on Ollama the sonnet tier *is* flash, so dev-flow resolves the ladder to `model: opus` at the spawn site — a new, concrete decision, not a restatement of today's intent (today's Stage 3 Halts bullet defers to SDD's generic ladder).
- **Produce-tier provenance (Stages 1-2):** the produce-subagent self-reports its model as the first line of its summary (built into the agent body, so both dispatches carry it without a per-dispatch reminder), and the orchestrator verifies it against `claude-opus-4-8`, ignoring any harness-appended variant suffix (the same normalization the review provenance check uses), halting on a mismatch. Add the orchestrator-side instruction to Cross-Cutting Concerns as a sibling of the review provenance check — so a launch that silently defeats the pin (e.g. `CLAUDE_CODE_SUBAGENT_MODEL` set) is caught in-pipeline, not just at a one-time live check.
- **Plan-review preservation:** the adversarial-review rewrite contract (line 75) currently preserves only "the doc's front-matter block and its `## Original problem` section unchanged" — extend it to also preserve `risk:` lines in `## Task N` sections, so a plan review that touches a marked task's section cannot silently drop the marker. The preservation yields only where the review resolves a finding about the marker itself (a wrong value, or a marker on a task the review finds not risky) — without that carve-out the rewrite contract and the correctness-seed backstop would contradict. (The preservation clause is the only protection for a dropped marker: the correctness seed runs on the plan under review, before the rewrite, so it flags a risky task missing the marker or a wrong-value `risk:` line — not a marker the rewrite drops.)
- **Plan-review marker backstop:** the plan review's correctness seed checks that every `## Task N` section of a dev-flow-family plan (one carrying a `dev-flow:` or `dev-flow-worktree:` front-matter block) whose work touches concurrency, auth, state machines, or other subtle invariants carries a `risk: high` marker — so a produce-subagent that forgets to mark a risky task is caught at the plan review, not at Execute.

### 3. Launch reference

`CLAUDE_CODE_SUBAGENT_MODEL` overrides **every** frontmatter pin (resolution order: env var > `Agent` tool `model` param > frontmatter > inherit). If it were set, it would force the seed, resolver, produce-subagent, and risky-task reviewer onto whatever it names. **It is not set by today's launch** — reviews do not halt on Ollama, so the resolver's self-report still matches its pin and the pin is holding. So this is not a current break the design repairs; it is a defeat the design **guards against**. The guard is the in-pipeline provenance check (§2), which is automatic and correct-by-default: a launch that sets the env var changes every self-report, the orchestrator halts, and no silent degradation ships. The launch blocks below are **reference** — what a correct dev-flow launch looks like — not a "remember not to set this" rule.

Reference launch blocks live in the Model Policy section:

**Ollama** (`ollama launch claude` equivalent, env set manually):

```sh
export ANTHROPIC_BASE_URL=http://localhost:11434
export ANTHROPIC_AUTH_TOKEN=ollama
export ANTHROPIC_API_KEY=""
export ANTHROPIC_MODEL=deepseek-v4-flash:cloud        # driver — control loop (mid-tier)
export ANTHROPIC_DEFAULT_SONNET_MODEL=deepseek-v4-flash:cloud   # sonnet tier — seed
export ANTHROPIC_DEFAULT_OPUS_MODEL=deepseek-v4-pro:cloud       # opus tier — fix-loop escalation (family-alias spawn); pinned roles (produce-subagent, resolver, risky-task reviewer) resolve via ollama cp aliases
export ANTHROPIC_DEFAULT_HAIKU_MODEL=nemotron-3-nano:30b-cloud  # defensive completeness only — no spawn in this design targets haiku
claude
```

`ANTHROPIC_DEFAULT_SONNET_MODEL` and `_HAIKU_MODEL` are **defensive completeness**, not load-bearing for this design's spawns: the seed, produce-subagent, resolver, and risky-task reviewer are pinned by dated id (resolved through `ollama cp` aliases), and the fix-loop escalation targets `model: opus` (the `_OPUS` var). The sonnet var covers any `model: sonnet` alias spawn Claude Code itself emits; the haiku var covers cheap background spawns. The haiku var deviates from `docs/ollama-models.md`'s `qwen3-coder:30b` recommendation, which targets a local setup; this launch is cloud-based, so the haiku tier resolves to a cloud model (`nemotron-3-nano:30b-cloud`). They cost nothing to set and prevent a future alias spawn from landing on an undefined tier.

Model resolution on Ollama stays external via `ollama cp` aliases, so the pinned dated ids resolve to the desired cloud models without any skill edit:

- `claude-sonnet-4-6` → `deepseek-v4-flash:cloud` (sonnet tier: seed)
- `claude-opus-4-8` → `deepseek-v4-pro:cloud` (opus tier: produce-subagent, resolver, risky-task reviewer; the fix-loop escalation resolves via `ANTHROPIC_DEFAULT_OPUS_MODEL`, not this alias — same target on Ollama)
- `claude-haiku-4-5` → `nemotron-3-nano:30b-cloud` (cheap background tier)

**Anthropic** (`claude --model sonnet`): driver and seed on sonnet (the seed's pin is already correct), produce-subagent, resolver, and risky-task reviewer on opus. No env vars.

#### Why a mid-tier flash driver, not a strong one

`docs/ollama-models.md` recommends `deepseek-v4-pro:cloud` for the driver — but that recommendation is for a **non-delegating** session, where the one model does the user's work directly and its reasoning quality is the ceiling on output. dev-flow's driver is a **delegating controller**: it runs the branch-entry bookkeeping, fans out to leaves, and checks provenance — the actual design, plan, implementation, and judgment work happens in the opus-tier leaves (produce-subagent, resolver) and the session-model executors. The driver's job is control flow, not reasoning, so a mid-tier model is the right class for it, and three things make flash the right pick specifically:

- **Cost lever.** Ollama Cloud bills GPU-time by subscription tier, not per-token: a flat-rate subscription plus a metered usage allowance that each model consumes at its level (flash at Level 2, pro at Level 4). The driver is the one role that runs for the *entire* session — every leaf is short-lived, the driver never stops — so the driver's tier sets the consumption rate on the session-long GPU-time, the dominant usage term. Running the driver on the heaviest model (Level 4) would consume the whole session at Level-4 rates for control-loop work a mid-tier model does fine; the pro-tier leaves (produce-subagent, resolver) are short-lived, so their Level-4 consumption is negligible.
- **Precedent.** The Codex agentic-pod pattern puts the orchestrator on `o3-MEDIUM` while the planner and reviewer go on `o3-high` — mid-tier driver, strong thinkers — exactly this split.
- **Rubric floor.** SDD's model-selection rubric puts orchestration/fan-out on the cheap-to-mid tier and reserves the most capable model for architecture, design, and review. The driver is fan-out; produce and the resolver are the architecture/review work.

For an **interactive** session (no pipeline, the model does your work directly), the non-delegating reasoning applies — use a strong driver. dev-flow is not that session.

### 4. Mirroring + version bumps

- The new agent files are added to both plugins: `plugins/dev-flow/agents/{produce-subagent,task-reviewer}.md` and `plugins/dev-flow-worktree/agents/{produce-subagent,task-reviewer}.md`. Each becomes a **machine-checked mirror pair** in `scripts/check-sync.py`'s `MIRROR_PAIRS`, exactly like the `adversarial-review-{seed,resolver}` agent pairs: `"canonicalize": [("dev-flow-worktree", "dev-flow")]` and `"exceptions": []`. The description and body name the plugin (`for dev-flow's produce work` / `for dev-flow`), so the worktree copy must name `dev-flow-worktree` in those two places and the canonicalize entry maps it back — the pair is line-for-line identical after canonicalization. The entry is load-bearing here, not decorative: a byte-for-byte copy would leave the worktree agent naming the wrong plugin, and `check-sync.py` would pass it.
- SKILL.md edits are **hand-mirrored** into `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` (Model Policy, pipeline intro, Stage 1, Stage 2, Stage 3 reviewer routing), since the two SKILL.md files are too divergent for `check-sync.py` (per CLAUDE.md). The adversarial-review SKILL.md edits (rewrite-contract preservation + plan correctness-seed marker check) are a **machine-checked mirror pair** — `plugins/dev-flow/skills/adversarial-review/SKILL.md` ↔ `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md`, already registered in `check-sync.py` — so they are edited in both copies and the pair check proves they agree.
- Version bumps: `dev-flow` 2.18.0 → 2.19.0; `dev-flow-worktree` 1.20.0 → 1.21.0. Both are behavior changes (new spawn target, new agents shipped, Stage 3 reviewer routing).
- CONTEXT.md glossary: broaden the **Tier** entry — currently "The model a reviewer is spawned on" — to cover any pinned agent, since the produce-subagent joins the resolver on the opus tier and the design introduces a "produce tier". Suggested wording: "The model a pinned agent is spawned on — `claude-sonnet-4-6` for seeds, `claude-opus-4-8` for resolvers and the produce-subagent."

## Cost / output effect

- **Design and plan move off flash** onto the opus tier — `deepseek-v4-pro` on Ollama (the strongest reasoning model there, per `docs/ollama-models.md`), `claude-opus-4-8` on Anthropic. The design is the highest-leverage artifact (SDD's rubric puts architecture/design on the most capable model); the plan is the contract the most expensive stage implements verbatim and the artifact that makes cheap executors viable. Both are short-lived (a few thousand tokens each), so the absolute cost is negligible, and on Ollama they are the same model the resolver already uses.
- **Driver, executors, fixers, the per-task reviewer (routine tasks), and the seed stay on flash** — the workhorse does the bulk-token work (fan-out orchestration in-context, SDD loop) where it is already good enough, the routine per-task reviewer is a mechanical gate, and the seed is a findings-only first pass that the opus resolver gates. Subtle tasks get an opus reviewer at the per-task gate; the final judgment is always the opus resolver.
- Net: the high-leverage artifacts and the final (and risky-task) judgment get the strong tier; the high-volume work stays cheap. Same-or-better output, lower blended cost than running the whole session on the strong tier.

## Non-goals

- No change to review tiers (seed `claude-sonnet-4-6`, resolver `claude-opus-4-8`) — already pinned, already correct.
- No change to executor/fixer model — stays on the main session model (fix-loop *escalation* targets the opus alias; the base fixer stays on session).
- No change to SDD's per-task reviewer *mechanism* — it stays a spawned leaf; only its **model routing** becomes risk-scaled (session by default, the pinned `dev-flow:task-reviewer` for `risk: high` tasks). The plan-side `risk: high` marker (contract in the Stage 2 edit) is the only plan-format addition.
- No attempt to override provider/endpoint per sub-agent (unsupported; claude-code issue #38698). Tier selection is model-id-level, within a single-provider session.
- No new pipeline structure — Stages 1 and 2 still spawn exactly one produce leaf; only the leaf's agent definition and dispatch name change.

## Verification

- `claude plugin validate .` passes; the new agents listed by `claude plugin details dev-flow` (note: it reports the marketplace-synced version, not the running install — re-sync and restart before trusting it).
- `python3 scripts/check-sync.py` passes with the two new mirror pairs (`produce-subagent` and `task-reviewer` agents) registered.
- `python3 scripts/check-version-bump.py origin/main` passes (both version bumps present).
- Removed-phrase grep: the phrases removed from `SKILL.md` — `spawns produce-subagents and executors on the main session model` (the combined Model-Policy clause; the bare `on the main session model` *stays* for executors, so grep the full combined phrase, not the fragment), `runs in a fresh \`general-purpose\` produce-subagent`, `writes its draft into the working checkout`, and `written into the working checkout on the feature branch` — return no hits in either variant. (Per CLAUDE.md's removed-phrase rule: the fragment `on the main session model` is intentionally kept for executors, so it must NOT be the grep target — only the combined clause that's actually removed.)
- Live check (Anthropic): run dev-flow Stage 1, confirm the produce-subagent self-reports `claude-opus-4-8` (ignoring any harness-appended variant suffix); run Stage 2, confirm the same.
- Provenance check: run Stage 1 + Stage 2 with `CLAUDE_CODE_SUBAGENT_MODEL` set to a wrong model, confirm the orchestrator halts on the produce-tier self-report mismatch — the guardrail, not a repair of a current break (unset, the pin holds and no halt fires).
- Live check (Ollama): launch per the Launch reference, confirm produce-subagent and resolver run on the opus alias target (`deepseek-v4-pro`), the seed on the sonnet alias target (`flash`), and the driver on `flash`; for a `risk: high` task, confirm its per-task reviewer runs on the pinned opus tier.
- Plan-review preservation check: run a plan carrying a `risk: high` marker through `dev-flow:adversarial-review` (mode: plan) with a finding that touches the marked task's section, and confirm the rewritten plan still carries the marker.