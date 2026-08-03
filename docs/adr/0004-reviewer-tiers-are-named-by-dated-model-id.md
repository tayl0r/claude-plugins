# Reviewer tiers are pinned to dated model ids via agent definitions

`adversarial-review` named its two tiers with harness family aliases — `sonnet` for seeds, `opus` for resolvers — and said so normatively: "a harness alias, never a dated model id." As of `dev-flow` 2.12.0 and `dev-flow-worktree` 1.14.0 the tiers are `claude-sonnet-4-6` and `claude-opus-4-8`, and `better-code-review`'s five parallel reviewers are pinned the same way. `CONTEXT.md`'s **Tier** entry follows, gains an **Agent definition** entry, and the self-report check is renamed from **family match** to **tier match**, since matching a family is no longer what it does.

The reason is the failure mode aliases have: an alias resolves to whatever the newest model in its family is, so every release silently re-points every tier that uses one. Opus 5 and Sonnet 5 shipped and the reviewers got worse for us with no change to this repo and nothing in the protocol to point at. A tier whose model can change without an edit here is not a tier this repo chose; it is one the release calendar chooses.

## The mechanism, and why it is indirect

The `Agent` tool's `model` parameter accepts **only** family aliases and rejects a dated id outright:

```
InputValidationError: Invalid option: expected one of "sonnet"|"opus"|"haiku"|"fable"
```

Agent-definition frontmatter *does* accept a full id. So each tier is now a named `subagent_type` — `adversarial-review-seed`, `adversarial-review-resolver`, `better-code-review-reviewer` — whose frontmatter carries the pin. The skills spawn by that name and **never pass `model`**, which would override the frontmatter and silently un-pin the tier. Verified end-to-end: spawned with no `model` parameter, the seed self-reports `claude-sonnet-4-6` and the resolver `claude-opus-4-8[1m]`.

One wrinkle forces an install step. **Claude Code 2.1.220 does not register a plugin's own `agents/` directory.** Three independent observations agree: neither `plugin.json` nor `marketplace.json` has an `agents` key; an enabled plugin's agent (`code-simplifier`) is absent from the Agent tool's available list while that same plugin's skills are present; and only `~/.claude/agents/` and `.claude/agents/` entries do appear, read once at session startup. So the definitions live at `plugins/<name>/agents/` — the documented convention, and where they will already be if a later version starts registering them — and `scripts/install-agents.py` copies them into `~/.claude/agents/`. It copies rather than symlinks because a symlink into a worktree under `.claude/worktrees/` dangles when that worktree is removed, which would fail at spawn time inside an unrelated session.

Because registration happens at startup, a fresh clone reviews on the wrong models until the installer is run. `Review integrity` therefore treats a missing agent type as a failed spawn — halt and report the install command — rather than falling back to an alias, so the failure is loud instead of a quiet downgrade.

The Sonnet line has no 4.8: 4.6 is the newest Sonnet before 5, so the seed tier is 4.6 by availability, not by preference.

## Cost accepted

Maintenance. A pinned id is deprecated and eventually retired, and someone must bump it; that recurring edit is exactly what the alias was buying. It is the right trade because the alias bought it by giving away reproducibility, and a review protocol whose judgment tier moves underneath it cannot be tuned against. The install step adds a second cost — a machine-local artifact that can drift from the repo — which `install-agents.py --check` exists to report.

This revises ADR 0002 only where it argues for aliases. Its substantive decision — resolvers unconditionally in the Opus family, `adversary ≠ author` abandoned, provenance claiming only fan-out — stands unchanged.

## Considered options

- **Keep the aliases and pin the session model to `claude-opus-4-8` instead** — rejected: it moves executors, fixers, and the orchestrator, which run on the main session model, but seeds and resolvers are pinned by tier rather than inherited from the session, so the two tiers that actually regressed would stay on their family's newest model. It also puts the reviewer tier back under ambient state, which is what ADR 0002 rejected.
- **Name the dated ids in the skills and let the alias-only spawn interface approximate them** — rejected as a resting place. It is honest only if provenance reports the substitution, and it leaves every run silently off-tier; shipping the pin as prose the harness cannot honor is a comment, not a decision.
- **Halt when a dated id cannot be honored, with no agent definitions** — rejected on its own: with an alias-only spawn interface that halts every run. Adopted *with* agent definitions, where a halt means "run the installer" and is fixable in one command.
- **Symlink the definitions instead of copying** — rejected: live-updating is the nicer property, but a link into `.claude/worktrees/<name>` dangles when the worktree is removed, and the resulting failure surfaces in an unrelated session with no obvious cause. `--check` recovers most of the benefit safely.
- **Have a skill write its own agent definition on first run** — rejected: definitions are read at session startup, so a file written mid-session does not register (confirmed empirically). It would also have a plugin writing into the user's config as a side effect of a review.
- **Name the tier by family plus a floor** (e.g. "Opus, at most 4.8") — rejected: no spawn interface expresses it, so it would be a constraint no caller can act on and no check can verify.
