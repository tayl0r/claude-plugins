---
name: justfile
description: Use when setting up a justfile, finding useful just recipes, automating repetitive commands, creating a task runner or Makefile equivalent, or codifying workflows. Analyzes project structure to recommend high-value compound commands worth automating.
---

# Discover Justfile Recipes

Analyze a project and recommend high-value `justfile` recipes. Focus on **compound commands** (2+ steps that must run together) and **hard-to-remember commands** (long flags, specific container names, env vars). Skip simple single-command aliases — those add no value.

## Where to Look

1. **Claude Code history** — the highest-signal source. Run `rtk discover` to find repeated multi-step shell commands across sessions — these are the workflows Claude re-derives from scratch every time.
2. **CLAUDE.md / README.md** — documented multi-step workflows
3. **package.json / Makefile / Taskfile / docker-compose.yml** — existing task definitions. In monorepos, also check each workspace's package.json scripts, not just the root.
4. **Shell scripts** (`.sh` files, `scripts/` directory)
5. **CI config** (`.github/workflows/`, `.gitlab-ci.yml`) — multi-step pipeline sequences
6. **.env.example / infrastructure config** — setup/reset workflows

## What Makes a Recipe High-Value

- Multiple sequential commands that fail if run out of order (e.g. drop DB, push schema, seed)
- Commands with project-specific magic strings (container names, stage names, API URLs)
- Destructive operations that benefit from being named clearly (reset, nuke, clean)
- Status-check workflows that aggregate info from multiple sources
- Setup/bootstrap sequences for new developers

## Output Format

Write a complete justfile ready to paste. Each recipe must have a comment (shown by `just --list`):

```just
# [clear one-line description of what this does]
recipe-name:
    command1
    command2
```

## Naming Conventions

- **kebab-case**, **verb-first**: `db-reset`, `logs-tail`, `deploy-staging`
- Short and scannable — optimize for `just --list` output

## Target Count

Aim for 4-8 recipes. Enough to cover real pain points, not so many it becomes a second build system.

## Before Starting

If a justfile already exists, read it first. Preserve existing recipes and only add new ones.

## After Creating the Justfile

If `just-claude` is installed (`which just-claude`), run `just-claude init` to generate Claude Code skills from the recipes. Add `.claude/skills/just-*` to `.gitignore` (generated files).
