---
dev-flow:
  slug: provider-blended-reviews
  stops: [pre-merge]
  docs: commit
---

# Provider-blended review tiers for dev-flow

## Problem

Every review tier in dev-flow runs on an Anthropic model: sonnet-4-6 seeds, opus-4-8 resolvers, session-model task-reviewers and fixers. The user holds three quotas — $200 Claude, $20 Ollama, $20 Codex — and the Claude quota carries everything while the other two sit idle. Review findings from a genuinely different model family catch different issues than the author's family (the adversarial-review skill already calls cross-family "a bonus on what gets noticed"). We want a small, targeted mix: delegate the *findings* tiers (seeds, task-reviewers, fixers) to Codex or Ollama, while writing (produce) and judgment (resolvers) stay on Anthropic opus.

## Approach

Make the review tiers provider-configurable. Each of **seeds**, **task-reviewers**, and **fixers** can run on one of three providers:

- **`session`** (default) — the current behavior: spawn via the Agent tool on the session's provider.
- **`codex`** — shell-delegate to the codex companion (`review` for seeds, `task` for task-reviewers/fixers).
- **`ollama-<flash|pro|nano>`** — shell-delegate to `claude-ollama <tier> -p "<prompt>"`: a fresh Claude Code session routed to Ollama (verified: reads, edits, reports).

Produce and resolvers are **not** provider-configurable — they stay on the session's best model (opus on Anthropic, pro on Ollama) via their existing agent pins.

### Driver model

The session model (the driver) is a launch choice, not a config key: `claude` (opus default), `claude --model sonnet`, or `claude-ollama <flash|pro|nano>`. Recommended: **opus driver** — the orchestrator runs the adversarial-review and SDD protocols in-context and makes the routing decisions, so its reliability is load-bearing. A sonnet driver is a cost lever (drops the orchestrator and any `session`-configured review tiers — fixers, routine task-reviewers — to sonnet while produce/resolvers stay pinned on opus) that trades orchestrator reliability; the pinned tiers stay opus either way. Tiers delegated to `codex` or `ollama-<tier>` are unaffected by the driver choice — they run on their configured provider regardless. An Ollama driver requires Anthropic auth to be available for `risk: high` task reviews, since `dev-flow:task-reviewer` is pinned to `claude-opus-4-8`; if auth is unavailable the pipeline halts when it tries to spawn that reviewer.

### Config

The provider choice lives in `.claude/dev-flow.local.md` (per-machine, git-ignored), alongside `docs:`:

```yaml
---
docs: commit
providers:
  seeds: codex
  task-reviewers: ollama-flash
  fixers: session
---
```

Unset = `session` (current behavior). The config is per-machine, so each laptop blends differently. The file is read from the repository root — the main working tree. For `dev-flow` (non-worktree) the repository root is the working directory, so the relative path `.claude/dev-flow.local.md` resolves correctly. For `dev-flow-worktree`, the orchestrator reads `<main-root>/.claude/dev-flow.local.md` (the main checkout, computed as the first entry of `git worktree list --porcelain`), not the worktree's own root. Both variants thus read the same file and the same keys.

### Delegation mechanics

The SKILL.md defines the delegation as command mappings — `(provider, tier)` → command — executed by the orchestrator via Bash (it remains the only spawner). This follows the repo's existing pattern: `task-brief` is likewise described in the SKILL.md and implemented inline by the orchestrator, not shipped as a script. Per-tier prompt shapes (a review prompt for seeds, a verification prompt for task-reviewers, a fix prompt for fixers) are defined in the SKILL.md.

Provider path resolution is a documented, verified procedure (Command discipline): the codex companion is resolved via the marketplace/cache layout and verified to exist (halt on failure); `claude-ollama` is resolved via PATH.

### Provenance

Shell-delegated tiers don't self-report a model. The provenance line reports the provider name (e.g. `codex`, `ollama-flash`) in place of the dated model id. The orchestrator's provenance check reads the `providers:` config: for `session` (or unset) tiers it validates against the dated model id the tier pins; for `codex` and `ollama-<tier>` tiers it validates against the configured provider name.

### Skill contract

The adversarial-review skill's "Review integrity (never inline)" rule requires seeds/resolvers to run as separate subagents and halts otherwise. A caller may supply seed findings directly (via the `extra findings` parameter, or by passing `seeds: skipped` with externally-produced findings), in which case the seed spawn is skipped — the supplied findings join any other caller-supplied findings in Resolution step 1, and the provenance line records the delegation. The resolver spawn is never skipped. The "if neither spawn nor delegation is possible, halt" logic lives in dev-flow's pipeline SKILL.md (the orchestrator resolves paths, runs delegation, and halts on failure before invoking adversarial-review).

### Example configs

Two example configs committed to the plugin (the real files are git-ignored), at `plugins/dev-flow/examples/` and mirrored to `plugins/dev-flow-worktree/examples/`:

- `dev-flow.local.work.md` — work laptop ($100 Claude enterprise): seeds + task-reviewers on `codex`, fixers on `session`.
- `dev-flow.local.home.md` — home laptop ($200 Claude, $20 Ollama, $20 Codex): seeds on `codex`, task-reviewers on `ollama-flash`, fixers on `session`.

## Insertion blocks

The exact text inserted into the SKILL.md files. These blocks use tagged fences (`markdown`, `yaml`) because some contain nested fenced code blocks — a documented limitation of `scripts/design_blocks.py`, whose plain-block parser cannot handle a line that is exactly three backticks inside a block. A custom reader (not `design_blocks`) is needed for the design-conformance check; the check re-reads these blocks from this design on disk, never retyped, and asserts each appears verbatim in its target.

**Block A — pipeline SKILL.md, Provider policy (inserted after the Docs policy section, before "Doc git lifecycle"):**

````markdown
**Provider policy — `providers:`.** Whether the review tiers (seeds, task-reviewers, fixers) run on the session or are shell-delegated to another provider. Keys are bare; the filename scopes them:

```yaml
---
docs: commit
providers:
  seeds: codex
  task-reviewers: ollama-flash
  fixers: session
---
```

| Value | Meaning |
|---|---|
| `session` (default) | spawn via the Agent tool on the session's provider |
| `codex` | shell-delegate to the codex companion |
| `ollama-<flash\|pro\|nano>` | shell-delegate to `claude-ollama <tier> -p` |

Unset = `session` (current behavior). The config is per-machine (git-ignored), so each laptop blends differently. The file is read from the repository root — the main working tree. For `dev-flow` (non-worktree) the repository root is the working directory, so the relative path `.claude/dev-flow.local.md` resolves correctly. For `dev-flow-worktree`, the orchestrator reads `<main-root>/.claude/dev-flow.local.md` (the main checkout, computed as the first entry of `git worktree list --porcelain`), not the worktree's own root. Both variants thus read the same file and the same keys.

Unknown keys are ignored; the config is per-machine and a typo will be noticed on first run. An unrecognized value defaults to `session` with a warning; an empty value is treated as unset (defaults to `session`). The `<tier>` in `ollama-<tier>` is validated against `flash`, `pro`, `nano` at config-read time; an unrecognized tier halts with a clear error.

**Delegation.** When a tier is provider-configured to `codex` or `ollama-<tier>`, the orchestrator runs the one-shot via Bash instead of spawning the Agent-tool subagent:

- `codex` seeds: `node <companion> review --wait --scope working-tree` (design/plan) or `--scope branch` (PR; the companion auto-detects the base ref).
- `codex` task-reviewers/fixers: `node <companion> task [--write] "<prompt>"`.
- `ollama-<tier>`: `claude-ollama <tier> -p "<prompt>"`.

Non-zero exit codes halt the pipeline (standard Command discipline). Set a reasonable Bash timeout (e.g. 5 minutes for seeds, 10 for task-reviewers). Escape prompt arguments in single quotes to prevent shell interpretation of the prompt text.

Path resolution: the codex companion is resolved via the marketplace/cache layout and verified to exist (halt on failure); `claude-ollama` via PATH. Delegated output is passed through as-is — the raw stdout becomes the seed findings. No transformation or parsing is needed: the resolver reads prose findings regardless of source. A delegated seed pass's findings are passed to the adversarial review as caller-supplied findings, and the review's seed spawn is skipped for that tier.
````

**Block B — pipeline SKILL.md, Stage 3 task-reviewer routing (appended to the existing "Per-task reviewer routing" bullet):**

```markdown
Routine task-reviewers run on the session model, unless `providers.task-reviewers` delegates them to `codex` or `ollama-<tier>`, in which case the orchestrator runs the one-shot via Bash. `risk: high` tasks always use `dev-flow:task-reviewer` (the pinned opus-tier leaf) — never delegated.
```

**Block C — pipeline SKILL.md, Cross-Cutting Concerns provenance (appended to the "Review provenance is checked" bullet):**

```markdown
For shell-delegated tiers, the provenance line reports the provider name (e.g. `codex`, `ollama-flash`) in place of the dated model id. The orchestrator's provenance check reads the `providers:` config: for `session` (or unset) tiers it validates against the dated model id the tier pins; for `codex` and `ollama-<tier>` tiers it validates against the configured provider name.
```

**Block D — adversarial-review SKILL.md, Review integrity (appended to the "never inline" rule):**

```markdown
A caller may supply seed findings directly (via the `extra findings` parameter, or by passing `seeds: skipped` with externally-produced findings), in which case the seed spawn is skipped — the supplied findings join any other caller-supplied findings in Resolution step 1, and the provenance line records the delegation. The resolver spawn is never skipped.
```

**Block E — adversarial-review SKILL.md, Seed passes (appended to the seed-passes section):**

```markdown
When the caller passes `seeds: skipped` with delegated seed findings, the seed passes are not spawned — the delegated findings ARE the seed findings, joining any other caller-supplied findings in Resolution step 1.
```

**Block F — adversarial-review SKILL.md, Resolution step 6 provenance (appended to the provenance sentence):**

```markdown
A delegated seed pass reports the provider name (e.g. `codex`, `ollama-flash`) in place of the dated model id in the provenance line.
```

**Block G — adversarial-review SKILL.md, Model section fixer delegation (inserted after "Executors, fixers, and the orchestrator run on the main session model."):**

```markdown
When the invoking pipeline's `providers:` config sets `fixers` to `codex` or `ollama-<tier>`, fixers run as shell-delegated one-shots on the configured provider instead of on the session model. The resolution procedure's "on the main model" is likewise overridden — the orchestrator runs the delegation command via Bash.
```

**Block H — example configs:**

`plugins/dev-flow/examples/dev-flow.local.work.md`:

```yaml
---
docs: commit
providers:
  seeds: codex
  task-reviewers: codex
  fixers: session
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
---
```

## Success criteria

- Each of seeds, task-reviewers, fixers can run on `codex`, `ollama-<tier>`, or `session`.
- Unset config = current behavior (no change when the key is absent).
- Shell-delegated tiers report the provider name (e.g. `codex`, `ollama-flash`) in place of the dated model id in the provenance line, and the orchestrator's provenance check validates against the configured provider rather than a dated model id.
- The two example configs are committed and match the two laptop setups.
- Both `dev-flow` and `dev-flow-worktree` are updated (mirrored) and their plugin versions bumped.
