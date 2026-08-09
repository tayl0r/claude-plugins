# Provider-blended review tiers for dev-flow

## Problem

Every review tier in dev-flow runs on an Anthropic model: sonnet-4-6 seeds, opus-4-8 resolvers, session-model task-reviewers and fixers. The user holds three quotas — $200 Claude, $20 Ollama, $20 Codex — and the Claude quota carries everything while the other two sit idle. Review findings from a genuinely different model family catch different issues than the author's family (the adversarial-review skill already calls cross-family "a bonus on what gets noticed"). We want a small, targeted mix: delegate the *findings* tiers (seeds, task-reviewers, fixers) to Codex or Ollama, while writing (produce) and judgment (resolvers) stay on Anthropic opus.

## Approach

Make the review tiers provider-configurable. Each of **seeds**, **task-reviewers**, and **fixers** can run on one of four providers:

- **`session`** (default) — the current behavior: spawn via the Agent tool on the session's provider.
- **`codex`** — shell-delegate to the codex companion (`review` for seeds, `task` for task-reviewers/fixers).
- **`ollama-<flash|pro|nano>`** — shell-delegate to `claude-ollama <tier> -p "<prompt>"`: a fresh Claude Code session routed to Ollama (verified: reads, edits, reports).
- **`claude`** — run on Anthropic: via the Agent tool when the session is Anthropic; via `claude -p` shell-out with Anthropic auth restored when the session is not. Least-tested path; not used by the example configs.

Produce and resolvers are **not** provider-configurable — they stay on the session's best model (opus on Anthropic, pro on Ollama) via their existing agent pins.

### Driver model

The session model (the driver) is a launch choice, not a config key: `claude` (opus default), `claude --model sonnet`, or `claude-ollama <flash|pro|nano>`. Recommended: **opus driver** — the orchestrator runs the adversarial-review and SDD protocols in-context and makes the routing decisions, so its reliability is load-bearing. A sonnet driver is a cost lever (drops orchestrator/fixers/routine task-reviewers to sonnet while produce/resolvers stay pinned on opus) that trades orchestrator reliability; the pinned tiers stay opus either way.

### Config

The provider choice lives in `.claude/dev-flow.local.md` (per-machine, git-ignored), alongside `docs:`:

```yaml
---
docs: commit
providers:
  seeds: codex
  task-reviewers: ollama-flash
  fixers: session
  risk-high-reviewers: session
---
```

Unset = `session` (current behavior). The config is per-machine, so each laptop blends differently. Both `dev-flow` and `dev-flow-worktree` read the same file and the same keys.

### Delegation mechanics

The SKILL.md defines the delegation as command mappings — `(provider, tier)` → command — executed by the orchestrator via Bash (it remains the only spawner). This follows the repo's existing pattern: `task-brief` is likewise described in the SKILL.md and implemented inline by the orchestrator, not shipped as a script. Per-tier prompt shapes (a review prompt for seeds, a verification prompt for task-reviewers, a fix prompt for fixers) are defined in the SKILL.md.

Provider path resolution is a documented, verified procedure (Command discipline): the codex companion is resolved via the marketplace/cache layout and verified to exist (halt on failure); `claude-ollama` is resolved via PATH. A small helper script is an implementation option, not a requirement.

### Provenance

Shell-delegated tiers don't self-report a model. The provenance line becomes `tier: N× <provider> (<command>)` instead of `tier: N× <pinned id>`. The orchestrator's provenance check accepts both forms.

### Skill contract

The adversarial-review skill's "Review integrity (never inline)" rule requires seeds/resolvers to run as separate subagents and halts otherwise. Shell delegation is a separate process — more isolated, not inline — so the rule is amended to allow it when a tier is provider-configured.

### Example configs

Two example configs committed to the plugin (the real files are git-ignored), at `plugins/dev-flow/examples/` and mirrored to `plugins/dev-flow-worktree/examples/`:

- `dev-flow.local.work.md` — work laptop ($100 Claude enterprise): seeds + task-reviewers on `codex`, fixers + risk-high on `session`.
- `dev-flow.local.home.md` — home laptop ($200 Claude, $20 Ollama, $20 Codex): seeds on `codex`, task-reviewers on `ollama-flash`, fixers + risk-high on `session`.

## Insertion blocks

The exact text inserted into the SKILL.md files, so a `design_blocks` check can verify each appears verbatim in its target.

**Block A — pipeline SKILL.md, Provider policy (inserted after the Docs policy section, before "Doc git lifecycle"):**

```markdown
**Provider policy — `providers:`.** Whether the review tiers (seeds, task-reviewers, fixers) run on the session or are shell-delegated to another provider. Keys are bare; the filename scopes them:

```yaml
---
docs: commit
providers:
  seeds: codex
  task-reviewers: ollama-flash
  fixers: session
  risk-high-reviewers: session
---
```

| Value | Meaning |
|---|---|
| `session` (default) | spawn via the Agent tool on the session's provider |
| `codex` | shell-delegate to the codex companion |
| `ollama-<flash\|pro\|nano>` | shell-delegate to `claude-ollama <tier> -p` |
| `claude` | run on Anthropic — Agent tool when the session is Anthropic; `claude -p` shell-out with auth restored otherwise |

Unset = `session` (current behavior). The config is per-machine (git-ignored), so each laptop blends differently. Both `dev-flow` and `dev-flow-worktree` read this same file and these same keys. `risk-high-reviewers` defaults to `session` and is never delegated — the risk gate stays on the best model.

**Delegation.** When a tier is provider-configured to `codex` or `ollama-<tier>`, the orchestrator runs the one-shot via Bash instead of spawning the Agent-tool subagent:

- `codex` seeds: `node <companion> review --wait --scope working-tree` (design/plan) or `--scope branch --base <default-ref>` (PR).
- `codex` task-reviewers/fixers: `node <companion> task [--write] "<prompt>"`.
- `ollama-<tier>`: `claude-ollama <tier> -p "<prompt>"`.
- `claude` (non-Anthropic session): `claude -p "<prompt>"` with Anthropic auth restored.

Path resolution: the codex companion is resolved via the marketplace/cache layout and verified to exist (halt on failure); `claude-ollama` via PATH. A delegated seed pass's findings are passed to the adversarial review as caller-supplied findings, and the review's seed spawn is skipped for that tier.
```

**Block B — pipeline SKILL.md, Stage 3 task-reviewer routing (appended to the existing "Per-task reviewer routing" bullet):**

```markdown
Routine task-reviewers run on the session model, unless `providers.task-reviewers` delegates them to `codex` or `ollama-<tier>`, in which case the orchestrator runs the one-shot via Bash. `risk: high` tasks always use `dev-flow:task-reviewer` (the pinned opus-tier leaf) — never delegated.
```

**Block C — pipeline SKILL.md, Cross-Cutting Concerns provenance (appended to the "Review provenance is checked" bullet):**

```markdown
For shell-delegated tiers, the provenance line reports `tier: N× <provider> (<command>)` instead of `tier: N× <pinned id>`; the check accepts both forms.
```

**Block D — adversarial-review SKILL.md, Review integrity (appended to the "never inline" rule):**

```markdown
When the invoking pipeline's `providers:` config delegates a tier to `codex` or `ollama-<tier>`, that tier runs as a shell-delegated one-shot on the configured provider — a separate process, not an inline review, and it satisfies this rule. If neither a spawn nor a delegation is possible, halt and report.
```

**Block E — adversarial-review SKILL.md, Seed passes (appended to the seed-passes section):**

```markdown
When the caller passes `seeds: skipped` with delegated seed findings, the seed passes are not spawned — the delegated findings ARE the seed findings, joining any other caller-supplied findings in Resolution step 1.
```

**Block F — adversarial-review SKILL.md, Resolution step 6 provenance (appended to the provenance sentence):**

```markdown
A delegated seed pass reports `seeds: N× <provider> (<command>)` in the provenance line.
```

**Block G — example configs:**

`plugins/dev-flow/examples/dev-flow.local.work.md`:

```yaml
---
docs: commit
providers:
  seeds: codex
  task-reviewers: codex
  fixers: session
  risk-high-reviewers: session
---
```

`plugins/dev-flow/examples/dev-flow.local.home.md`:

```yaml
---
docs: commit
providers:
  seeds: codex
  task-reviewers: ollama-flash
  fixers: session
  risk-high-reviewers: session
---
```

## Success criteria

- Each of seeds, task-reviewers, fixers can run on `codex`, `ollama-<tier>`, `claude`, or `session`.
- Unset config = current behavior (no change when the key is absent).
- Shell-delegated tiers report provenance as `ran via <provider> <command>`.
- The two example configs are committed and match the two laptop setups.
- Both `dev-flow` and `dev-flow-worktree` are updated (mirrored) and their plugin versions bumped.
