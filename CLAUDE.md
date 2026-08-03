# claude-plugins

A Claude Code plugin marketplace. `.claude-plugin/marketplace.json` is the registry; each plugin lives at `plugins/<name>/` with `.claude-plugin/plugin.json` plus some of `skills/<skill>/SKILL.md`, `agents/`, `scripts/`. Markdown plus a couple of Python scripts — no build, test, or lint tooling beyond `scripts/check-sync.py`.

## Changing a plugin

- **Bump `version` in `plugins/<name>/.claude-plugin/plugin.json` on any behavior change.** The install cache is version-keyed (`~/.claude/plugins/cache/taylor-plugins/<plugin>/<version>/`), so an edit at an unchanged version is never picked up on re-sync. **Always the minor segment** — `1.4.0 → 1.5.0`. Nothing reads the segment (the cache keys the whole string), and for prose a model reads there is no stable editorial-versus-behavioural line for a patch to mark. Major only when a plugin is split or renamed (`dev-flow` 1.x → 2.0.0).
- **New plugin: add an entry to `.claude-plugin/marketplace.json`** with `"source": "./plugins/<name>"` — the leading `./` is required. `description` is duplicated in both manifests; keep them in sync.
- **Some files are mirrored across `dev-flow` and `dev-flow-worktree` and must be edited in both.** `python3 scripts/check-sync.py` enforces what can be enforced mechanically — the `adversarial-review/SKILL.md` pair (line-for-line identical after `dev-flow-worktree` → `dev-flow`, minus declared exceptions) and the `description` duplicated between each `plugin.json` and `.claude-plugin/marketplace.json`. It runs on every PR. The pipeline `SKILL.md` pair and the two `README.md`s are too divergent to check mechanically — mirror those by hand. **`check-sync.py` proves the two copies agree with each other, never that either is correct**: text mangled identically in both sides passes it, and so does an edit missed on both. So any change to a mirrored pair, machine-checked or hand-mirrored, must also verify against something *outside* the pair. **Always:** grep for the exact phrases the edit removes, expecting no hits. **When the change has a design doc** that gives replacement or inserted text as fenced blocks: also add a short `python3` check that re-reads those blocks from the design on disk, never retyped, asserting each appears verbatim in its target and, for an insertion, directly after its anchor line. Write that check per change — the block-to-file mapping and the assertions differ every time, so there is no shared runner to call. The *reader* is not per change: run `python3 scripts/design_blocks.py <design>` to get the block shape and indices, then have the check `sys.path.insert(0, "scripts")` and call `read_blocks(<design>, <shape>)` — it re-reads the blocks and exits non-zero if the shape moved — instead of re-typing the reader.
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
