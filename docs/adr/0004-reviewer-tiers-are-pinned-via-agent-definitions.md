# Reviewer tiers are pinned to dated model ids via agent definitions

`adversarial-review` named its two tiers with harness family aliases — `sonnet` for seeds, `opus` for resolvers — and said so normatively: "a harness alias, never a dated model id." As of `dev-flow` 2.12.0 and `dev-flow-worktree` 1.14.0 the tiers are `claude-sonnet-4-6` and `claude-opus-4-8`, and `better-code-review`'s five parallel reviewers are pinned the same way. `CONTEXT.md`'s **Tier** entry follows, gains an **Agent definition** entry, and the self-report check is renamed from **family match** to **tier match**, since matching a family is no longer what it does.

The reason is the failure mode aliases have: an alias resolves to whatever the newest model in its family is, so every release silently re-points every tier that uses one. Opus 5 and Sonnet 5 shipped and the reviewers got worse for us with no change to this repo and nothing in the protocol to point at. A tier whose model can change without an edit here is not a tier this repo chose; it is one the release calendar chooses.

## The mechanism

The `Agent` tool's `model` parameter accepts **only** family aliases and rejects a dated id outright:

```
InputValidationError: Invalid option: expected one of "sonnet"|"opus"|"haiku"|"fable"
```

Agent-definition frontmatter *does* accept a full id. So each tier is a `plugins/<name>/agents/<name>.md` definition whose frontmatter carries the pin, distributed by the plugin system exactly like a skill. Two properties of that registration are load-bearing:

- **The registered name is plugin-qualified** — `dev-flow:adversarial-review-seed`, not `adversarial-review-seed`. The bare name does not resolve. Skills must spawn the qualified form, which is why each mirrored copy names its own plugin; `check-sync.py`'s `dev-flow-worktree` → `dev-flow` canonicalization folds the pair back together.
- **Passing `model` at the spawn site overrides the frontmatter**, silently un-pinning the tier. The skills must never pass it.

Verified end-to-end: spawned by qualified name with no `model` parameter, the seed self-reports `claude-sonnet-4-6` and the resolver `claude-opus-4-8[1m]` — `[1m]` marks the 1M-context variant and is no part of the pin, so tier match normalizes it away.

Registration happens at session startup, so an edit needs a marketplace re-sync and a restart. `claude plugin details <plugin>` reports the agents a plugin will register, for the *installed* version — re-sync before trusting it.

## A wrong turn worth recording

This decision briefly claimed that Claude Code does not register a plugin's `agents/` directory, and shipped a `scripts/install-agents.py` that copied the definitions into `~/.claude/agents/`. That was wrong, and the reasoning failed in three separate ways at once:

- `code-simplifier` and `feature-dev`, the plugins whose agents were observed missing, are installed at **project scope for a different project**. They never load in this repo, so their agents were never going to appear here.
- The `superpowers` agent found on disk lives in a **stale cache directory** for version 4.3.1. The installed 6.2.0 reports `Agents (0)` and ships none.
- The available-agents list was searched for the **bare** name. The qualified name was there the whole time.

`claude plugin details` would have settled it immediately, listing agents as a first-class component with a per-invocation token cost. The lesson is narrow and reusable: before building a workaround for a capability a harness appears to lack, check that capability's own inventory command, and confirm the thing under test is actually loaded in the context it is being tested from.

The installer is deleted. Distribution belongs to the plugin system, which already versions, scopes, and enables these files. A parallel copy step would have meant an agent that a normal marketplace install does not deliver, that plugin versioning does not cover, and that disabling a plugin does not disable.

## Cost accepted

Maintenance. A pinned id is deprecated and eventually retired, and someone must bump it; that recurring edit is exactly what the alias was buying. It is the right trade because the alias bought it by giving away reproducibility, and a review protocol whose judgment tier moves underneath it cannot be tuned against.

This revises ADR 0002 only where it argues for aliases. Its substantive decision — resolvers unconditionally in the Opus family, `adversary ≠ author` abandoned, provenance claiming only fan-out — stands unchanged.

## Considered options

- **Keep the aliases and pin the session model to `claude-opus-4-8` instead** — rejected: it moves executors, fixers, and the orchestrator, which run on the main session model, but seeds and resolvers are pinned by tier rather than inherited from the session, so the two tiers that actually regressed would stay on their family's newest model. It also puts the reviewer tier back under ambient state, which is what ADR 0002 rejected.
- **Name the dated ids in the skills and let the alias-only spawn interface approximate them** — rejected: it leaves every run silently off-tier. Shipping a pin the spawn interface cannot honor is a comment, not a decision.
- **Copy the definitions into `~/.claude/agents/` with an install script** — rejected, having been briefly adopted; see above. It bypassed the plugin system for files the plugin system already distributes.
- **Have a skill write its own agent definition on first run** — rejected: definitions are read at session startup, so a file written mid-session does not register (confirmed empirically), and it would have a plugin writing into the user's config as a side effect of a review.
- **Name the tier by family plus a floor** (e.g. "Opus, at most 4.8") — rejected: no spawn interface expresses it, so it would be a constraint no caller can act on and no check can verify.
