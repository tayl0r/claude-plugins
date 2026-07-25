# claude-plugins

A Claude Code plugin marketplace. `.claude-plugin/marketplace.json` is the registry; each plugin lives at `plugins/<name>/` with `.claude-plugin/plugin.json` plus some of `skills/<skill>/SKILL.md`, `agents/`, `scripts/`. Markdown and one Python script — no build, test, or lint tooling.

## Changing a plugin

- **Bump `version` in `plugins/<name>/.claude-plugin/plugin.json` on any behavior change.** The install cache is version-keyed (`~/.claude/plugins/cache/taylor-plugins/<plugin>/<version>/`), so an edit at an unchanged version is never picked up on re-sync.
- **New plugin: add an entry to `.claude-plugin/marketplace.json`** with `"source": "./plugins/<name>"` — the leading `./` is required. `description` is duplicated in both manifests; keep them in sync.
- Validate before committing: `claude plugin validate .` — checks the marketplace and every entry. The 8 missing-author warnings are expected.
- Load local edits: `claude plugin marketplace update taylor-plugins`, then restart.

## Workflow

Changes land via PR against `main`. dev-flow design/plan artifacts go to `docs/superpowers/{specs,plans}/` and are committed here (no `.claude/dev-flow.local.md`, so the `commit` default applies).

## Agent skills

### Issue tracker

Issues live as GitHub issues on `tayl0r/claude-plugins`, managed with the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical triage roles, using their default label strings. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context — `CONTEXT.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
