---
dev-flow:
  slug: gh-6-docs-policy
  spec: docs/superpowers/specs/2026-07-24-gh-6-docs-policy-design.md
---

# Per-repo docs commit/strip policy — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Teach both dev-flow pipelines to read a per-repo `.claude/dev-flow.local.md` setting that decides whether their design/plan scaffolding docs reach the default branch, and to strip them safely and resumably at the merge gate when it says `strip`.

**Architecture:** These plugins contain **no executable code**. They are prose specifications (`SKILL.md`, `README.md`) plus a `plugin.json` version string, interpreted at runtime by an orchestrating agent. "Implementation" therefore means surgical edits to specific documents at specific anchors. The change lands **twice** — once in `plugins/dev-flow/`, once in `plugins/dev-flow-worktree/` — because the two plugins install independently into a version-keyed cache containing only their own files, so no shared file can exist at runtime. Nothing mechanically enforces that the two copies stay in sync, so **every task in this plan edits both variants together**, and the final task runs a mechanical parity sweep.

**Tech Stack:** Markdown prose, YAML front-matter, JSON manifests. Shell snippets appear *inside* the prose as instructions to a future agent — they are specification text, not scripts this repo runs.

## Global Constraints

Every task's requirements implicitly include this section.

- **Repo root:** `/Users/taylor/dev/claude-plugins`. Every path in this plan is relative to it.
- **There is no test suite and no build.** Do not run `npm test`, `pytest`, `cargo test`, or a linter — none exist. **Every verification step in this plan is a `grep`, `diff`, `python3 -c`, or `git diff` read-back.** A task is verified when its stated commands produce the stated output.
- **Never edit the installed plugin cache** (`~/.claude/plugins/cache/...`). Only edit files under this repo.
- **The change lands twice.** Every SKILL.md edit is made to *both* files in the same task, with this exact naming substitution and no other:

  | In `plugins/dev-flow/skills/dev-flow/SKILL.md` | In `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` |
  |---|---|
  | `dev-flow` (the pipeline's name, in prose) | `dev-flow-worktree` |
  | `dev-flow:` (front-matter block name) | `dev-flow-worktree:` |
  | `dev-flow-stripped: <slug>` (commit trailer) | `dev-flow-worktree-stripped: <slug>` |
  | `dev-flow:adversarial-review` | `dev-flow-worktree:adversarial-review` |
  | `dev-flow: review clean @ <sha>` (PR marker) | `dev-flow-worktree: review clean @ <sha>` |
  | "branch entry" / "your checkout" | "worktree entry" / "the worktree" |
  | `.claude/dev-flow.local.md` | **`.claude/dev-flow.local.md` — NOT substituted. Same file, shared by both variants.** |

- **The settings file is `.claude/dev-flow.local.md` in both plugins.** `dev-flow` is the family name the two variants share. A file named `.claude/dev-flow-worktree.local.md` must never appear anywhere in this change — that is the single most likely mechanical error in this plan.
- **Exact literals** (copy verbatim; do not paraphrase):
  - Settings key and values: `docs: commit` / `docs: strip`.
  - Qualifying-path globs: `docs/superpowers/specs/*-<slug>-design.md` and `docs/superpowers/plans/*-<slug>-plan.md`.
  - Trailer grep: `--grep='^dev-flow-stripped: <slug>$'` (worktree: `--grep='^dev-flow-worktree-stripped: <slug>$'`), anchored at both ends.
  - Version bumps: `dev-flow` `2.1.0` → `2.2.0`; `dev-flow-worktree` `1.3.0` → `1.4.0`.
- **Line style:** `SKILL.md` paragraphs and list items are written as **single long unwrapped lines** — do not introduce manual line breaks inside a paragraph or bullet. `README.md` files wrap at roughly 72 columns — match that. Code fences and tables are structured normally in both.
- **Do not renumber existing steps.** The new ignore-enforcement step is deliberately numbered **0** so the existing steps 1–6 and every cross-reference to them ("skip to step 5") stay valid.
- **Cross-section references are by name, never by step number.** When inserted prose cites a step in *another* section, cite it by what it does ("the merge gate's `stops` consultation", "Marker validity"), not by its number: a number minted by a later task leaves every intervening commit citing a step that does not exist, and none of this plan's grep checks can catch a dangling number. Numeric references *within* one numbered list ("skip to step 5", "re-enter this gate at step 1") are fine, and existing ones are frozen by the no-renumbering rule above.
- **Verification-command form.** A `grep -c` check may assert only `0` or `1` of a string this change introduces or forbids, or a structurally anchored count (`^\|` table rows, `^[0-9]\. ` list steps). Never assert a hand-computed whole-file total (≥2) of a free-text phrase — the phrase may already exist elsewhere in the file, and a wrong prediction is indistinguishable from a wrong edit; instead run `grep -n` listing the phrase alongside the anchors the task inserted beside, and state the expected lines *and their order*. Every `grep` pattern is passed via `-e` (or after `--`) so a leading `-` is never parsed as an option.
- **Preserve existing wording** outside the stated anchor. These files have been through adversarial review; unrelated rewording is out of scope.

## File map

| File | Responsibility | Tasks touching it |
|---|---|---|
| `plugins/dev-flow/skills/dev-flow/SKILL.md` | The in-checkout pipeline spec. Gains: Command-discipline rule, Docs policy contract block, entry step 0, ownership clause, resume row, marker validity, Stage 1/4/5 changes. | 1–9 |
| `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` | The worktree-isolated pipeline spec. Gains the same, plus: the exclude-ensure moves out of Create into entry step 0, and entry step 4's addressing enumeration grows to cover the merge gate's new commands. | 1–9 |
| `plugins/dev-flow/README.md` | User-facing docs for the in-checkout variant. Gains a "Design and plan docs" section and a smoke-test step. | 10 |
| `plugins/dev-flow-worktree/README.md` | Same, worktree variant. | 10 |
| `plugins/dev-flow/.claude-plugin/plugin.json` | Version-keyed cache identity. `2.1.0` → `2.2.0`. | 11 |
| `plugins/dev-flow-worktree/.claude-plugin/plugin.json` | Version-keyed cache identity. `1.3.0` → `1.4.0`. | 11 |

No files are created. No files are deleted.

---

### Task 1: Command discipline — the standing rule

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md` (Cross-Cutting Concerns, ~line 208)
- Modify: `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` (Cross-Cutting Concerns, ~line 200)
- Test: none (prose repo — verify by grep)

**Interfaces:**
- Consumes: nothing. This is the first task.
- Produces: the phrase **"Command discipline"** as a bullet in each file's Cross-Cutting Concerns. Tasks 3, 4, and 6 cite it by that exact name ("Per Command discipline, …"), so the bullet must exist and must be labelled exactly `- **Command discipline:**`.

**Context:** Every command later tasks add is governed by two standing rules — resolve git-internal paths through git, and never let an empty captured variable stand in for a real value. The design makes them permanent rules for all future contributors, not this-change-only rationale, so they land as a Cross-Cutting Concerns bullet rather than being repeated at each call site.

- [x] **Step 1: Insert the bullet in `plugins/dev-flow/skills/dev-flow/SKILL.md`**

Find this line (it is the last bullet of `## Cross-Cutting Concerns`):

```
- **Severity-independent, value-gated:** the protocol acts on issues of any severity but only applies a fix when it genuinely improves the codebase.
```

Insert the following single line **immediately before** it (one new line, then the existing line unchanged):

```
- **Command discipline:** resolve git-internal paths through git (`git rev-parse --git-path …`), never as `.git/...` literals — `.git` is a file, not a directory, in any linked worktree. Capture, validate non-empty, and quote any command output a later command consumes; a failed producer halts the run and never substitutes an empty string — an empty variable silently *inverts* git predicates (an empty `<merge-base>` turns `git log <mb>..HEAD` into the empty range `HEAD..HEAD`, a false "no matches", and turns `git cat-file -e :<path>` into an index lookup that falsely succeeds).
```

- [x] **Step 2: Insert the byte-identical bullet in the worktree SKILL.md**

Find the same last bullet in `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`:

```
- **Severity-independent, value-gated:** the protocol acts on issues of any severity but only applies a fix when it genuinely improves the codebase.
```

Insert **the exact same line as Step 1, byte for byte** immediately before it. This bullet is one of the few places where the two files are *identical* — it contains no plugin name, so the Global Constraints substitution table does not apply. Do not adapt it.

- [x] **Step 3: Verify presence and byte-identity**

Run:

```bash
cd /Users/taylor/dev/claude-plugins
grep -c -F -e '- **Command discipline:**' plugins/dev-flow/skills/dev-flow/SKILL.md
grep -c -F -e '- **Command discipline:**' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
diff <(grep -F '**Command discipline:**' plugins/dev-flow/skills/dev-flow/SKILL.md) \
     <(grep -F '**Command discipline:**' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md) && echo IDENTICAL
```

Expected: `1`, `1`, then `IDENTICAL`.

- [x] **Step 4: Verify the bullet landed inside Cross-Cutting Concerns, not elsewhere**

Run:

```bash
cd /Users/taylor/dev/claude-plugins
for f in plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md; do
  echo "== $f"; grep -n -E '^## Cross-Cutting Concerns|^- \*\*Command discipline:|^- \*\*Severity-independent' "$f"
done
```

Expected for each file: three lines, in this order — the `## Cross-Cutting Concerns` heading, then `- **Command discipline:`, then `- **Severity-independent`.

- [x] **Step 5: Commit**

```bash
cd /Users/taylor/dev/claude-plugins
git add plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
git commit -m "dev-flow: add the standing Command discipline rule to both variants"
```

---

### Task 2: The docs-policy setting and its resolution (Artifact Contract)

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md` (Artifact Contract — Front-matter block, ~lines 83–93)
- Modify: `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` (Artifact Contract — Front-matter block, ~lines 81–91)
- Test: none (verify by grep)

**Interfaces:**
- Consumes: Task 1's Command-discipline bullet (referenced indirectly; no textual dependency).
- Produces: an Artifact Contract block whose heading is exactly `**Docs policy — commit or strip the scaffolding.**`, and the front-matter key `docs:`. Tasks 3, 5, 6, 7, 8, and 9 all cite this block by the name **"Docs policy"** and rely on the front-matter key being `docs`. Task 3 anchors on the `*Resolution happens once, at intake.*` paragraph **verbatim** — insert it exactly as written, or Task 3's anchor match fails.

**Context:** The setting is `.claude/dev-flow.local.md` — the plugin-settings pattern (`.claude/<plugin>.local.md`, YAML front-matter, user-local, git-ignored). Both variants read the **same** file and the **same** bare `docs:` key, because "does scaffolding land in the default branch?" is a question about the repo, with one answer per repo. The resolved value is stamped once at intake into the design doc's plugin-scoped front-matter block; every later stage reads the artifact, never the settings file.

- [x] **Step 1: Extend the front-matter schema example in `plugins/dev-flow/skills/dev-flow/SKILL.md`**

Find this fenced block (under `**Front-matter (the only new schema).** Design doc:`):

````
```yaml
---
dev-flow:
  slug: rate-limit
  stops: [post-plan, pre-merge]   # [] = full-auto to merge
---
```
````

Replace it with:

````
```yaml
---
dev-flow:
  slug: rate-limit
  stops: [post-plan, pre-merge]   # [] = full-auto to merge
  docs: commit                    # commit | strip — resolved and stamped once at intake (see Docs policy)
---
```
````

Align the `#` of the new line with the `#` on the `stops` line above it.

- [x] **Step 2: Insert the Docs policy block in `plugins/dev-flow/skills/dev-flow/SKILL.md`**

Find this paragraph (the last line of the Front-matter block):

```
Plan doc: `dev-flow: {slug: rate-limit, spec: docs/superpowers/specs/2026-07-20-rate-limit-design.md}` (linkage only). **Stops live solely in the design doc.** The PR body links both doc paths. `dev-flow:adversarial-review` preserves front-matter on every rewrite (part of its contract), so this block survives all reviews.
```

Insert the following **immediately after** it (blank line, then this text, then a blank line before the existing `**Doc git lifecycle — branch at design start.**` paragraph):

````
**Docs policy — commit or strip the scaffolding.** Whether this pipeline's design and plan docs reach the default branch is a **per-repo setting**, resolved once at intake and then carried in the artifact.

*The setting.* `.claude/dev-flow.local.md` — the plugin-settings pattern (`.claude/<plugin>.local.md`: YAML front-matter, user-local, git-ignored by definition). Keys are bare; the filename scopes them, so the file carries no plugin block at all:

```yaml
---
docs: strip      # commit | strip
---
```

| State | Resolves to |
|---|---|
| File absent | `commit` |
| File present, no `docs:` key | `commit` |
| `docs: commit` | `commit` |
| `docs: strip` | `strip` |
| Any other value | `commit`, **and emit a one-line warning naming the bad value** |

The default is `commit` because it is the pre-existing behavior and the resume-safe one. The warning on an unrecognized value exists because a typo'd `strip` silently meaning `commit` fails in the direction that surprises the user — scaffolding appears in the default branch after they believed they had turned it off. **Both plugin variants read this same file and this same key** (`dev-flow` is the family name they share): the keep-vs-strip question is about the repo's default branch, and its answer does not change with the variant you invoked, so there is one file, not two — parallel per-variant files would be two things to keep in sync for a question with one answer. Because the file is git-ignored, what it holds is each developer's local declaration of the repo's convention, not a team-enforced fact. The strict `dev-flow:` front-matter namespacing rule is untouched and never applied here: it governs plugin-scoped blocks in *artifacts*, where the branch-ownership predicate keys off the block name, and this file is input, not an artifact.

*Resolution happens once, at intake.* Stage 1 reads the file and stamps the resolved value into the design doc's `dev-flow` front-matter block, alongside `slug` and `stops`. **Every later stage reads the artifact, never the settings file again.** Precedence: front-matter (present on any resume) > settings file (first run only) > default `commit`. This follows the contract's "state lives in artifacts" rule and mirrors how `stops` already works, and it matters more here than for `stops`: the settings file is git-ignored, so it may not exist in the checkout where a run resumes, and a resumed run must not silently flip policy. `dev-flow:adversarial-review` preserves front-matter across rewrites, so the key survives every review.
````

- [x] **Step 3: Make the mirrored edits in the worktree SKILL.md**

In `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`, apply Steps 1 and 2 with the Global Constraints substitutions. Concretely:

Replace the front-matter example:

````
```yaml
---
dev-flow-worktree:
  slug: rate-limit
  stops: [post-plan, pre-merge]   # [] = full-auto to merge
  docs: commit                    # commit | strip — resolved and stamped once at intake (see Docs policy)
---
```
````

Then, immediately after the paragraph beginning `Plan doc: \`dev-flow-worktree: {slug: rate-limit, …` and before `**Doc git lifecycle — branch + worktree at design start.**`, insert the same Docs policy block with exactly these differences from Step 2's text and no others:

- `**Both plugin variants read this same file and this same key** (\`dev-flow\` is the family name they share)` — **unchanged**, including the un-suffixed `dev-flow` family name.
- `The strict \`dev-flow:\` front-matter namespacing rule` → `The strict \`dev-flow-worktree:\` front-matter namespacing rule`.
- `stamps the resolved value into the design doc's \`dev-flow\` front-matter block` → `… into the design doc's \`dev-flow-worktree\` front-matter block`.
- `\`dev-flow:adversarial-review\` preserves front-matter` → `\`dev-flow-worktree:adversarial-review\` preserves front-matter`.
- `\`.claude/dev-flow.local.md\`` → **unchanged.** Both variants read this exact path.

Everything else — the yaml fence, the five-row table, both italic sub-headings — is byte-identical to Step 2.

- [x] **Step 4: Verify the block, the key, and the shared filename**

Run:

```bash
cd /Users/taylor/dev/claude-plugins
for f in plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md; do
  echo "== $f"
  grep -c -F '**Docs policy — commit or strip the scaffolding.**' "$f"
  grep -c -F '.claude/dev-flow.local.md' "$f"
  grep -c -F 'dev-flow-worktree.local.md' "$f"
  grep -c -E '^  docs: commit +# commit \| strip' "$f"
  grep -n -F -e 'Plan doc: `' -e '**Docs policy — commit or strip the scaffolding.**' -e '**Doc git lifecycle' "$f"
done
```

Expected for **each** file, in order: `1` (the block is present), `1` (the settings path is named once — in this block's `*The setting.*` line; Tasks 4 and 7 add two more sites later), `0` (**the per-variant filename must never appear**), `1` (the front-matter example carries the key), then exactly three numbered lines **in this order** — the Plan-doc paragraph, the Docs policy heading, the Doc-git-lifecycle paragraph — proving the block landed between its two anchors rather than elsewhere in the Artifact Contract.

- [x] **Step 5: Verify the resolution table is complete and identical in both files**

Run:

```bash
cd /Users/taylor/dev/claude-plugins
grep -c -E '^\| (File absent|File present, no|`docs: commit`|`docs: strip`|Any other value)' plugins/dev-flow/skills/dev-flow/SKILL.md
grep -c -E '^\| (File absent|File present, no|`docs: commit`|`docs: strip`|Any other value)' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
diff <(sed -n '/^| State | Resolves to |/,/^| Any other value/p' plugins/dev-flow/skills/dev-flow/SKILL.md) \
     <(sed -n '/^| State | Resolves to |/,/^| Any other value/p' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md) && echo TABLES-IDENTICAL
```

Expected: `5`, `5`, then `TABLES-IDENTICAL` (the resolution table contains no plugin name, so the two copies must match byte for byte).

- [x] **Step 6: Commit**

```bash
cd /Users/taylor/dev/claude-plugins
git add plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
git commit -m "dev-flow: add the Docs policy setting and its resolution to the Artifact Contract"
```

---

### Task 3: Qualifying paths and the stripped state (Artifact Contract)

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md` (Docs policy block, appended)
- Modify: `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` (Docs policy block, appended)
- Test: none (verify by grep)

**Interfaces:**
- Consumes: Task 2's Docs policy block. This task appends two more italic sub-sections to it; the anchor is the `*Resolution happens once, at intake.*` paragraph Task 2 added.
- Produces: two named concepts every later task cites — **"Docs policy's qualifying-path gates"** (numbered 1, 2, 3) and **"the stripped state"**. Also produces the validated variable name `merge_base`, which Task 5's ownership clause and Task 9's Stage 5 both reference by that exact name.

**Context:** A strip must remove only *this run's* docs and never a path that predates the branch. Gate 3 (`git cat-file -e "$merge_base:$P"` fails) is the gate that actually delivers that — slug-scoping alone does not, because a previously shipped feature's docs can legitimately match the slug globs. `merge_base` must be a validated variable: an empty one turns `git cat-file -e :P` into an *index* lookup that falsely succeeds.

- [x] **Step 1: Append the two sub-sections in `plugins/dev-flow/skills/dev-flow/SKILL.md`**

Find the paragraph Task 2 added that begins `*Resolution happens once, at intake.*` and ends:

```
`dev-flow:adversarial-review` preserves front-matter across rewrites, so the key survives every review.
```

Insert the following **immediately after** that paragraph, still inside the Docs policy block and still before `**Doc git lifecycle — branch at design start.**`:

````
*Qualifying paths — what a strip may remove.* `<merge-base>` is a **validated variable, never an inline substitution**:

```sh
git fetch origin "+refs/heads/<baseRef>:refs/remotes/origin/<baseRef>"  # failure halts
merge_base=$(git merge-base HEAD "origin/<baseRef>")                    # failure or empty halts
```

`<baseRef>` comes from `gh pr view --json baseRefName`, which is available everywhere `merge_base` is consumed: the strip runs inside Stage 5, and the stripped-state resume row is reachable only with an open PR (the MERGED and CLOSED rows match first otherwise). The explicit refspec, rather than a bare `git fetch origin <baseRef>`, is deliberate — in a single-branch clone a bare fetch updates only `FETCH_HEAD` and leaves `origin/<baseRef>` unresolvable. A checkout where fetch or merge-base still fails (offline, or shallow history not containing the base) halts with the failing command's output, instead of the silent false success an empty substitution produces.

A path `P` **qualifies** iff **all** of:

1. `P` matches `docs/superpowers/specs/*-<slug>-design.md` or `docs/superpowers/plans/*-<slug>-plan.md`.
2. `P` exists at `HEAD`.
3. `git cat-file -e "$merge_base:$P"` **fails** — i.e. `P` did not exist when this branch was created. With `merge_base` validated above the exit code is unambiguous: the ref is known-good and we are known to be in a repo, so a non-zero exit can only mean path-absent-at-merge-base.

Any path failing any gate is left alone. **No `git rm -r` of a directory, ever.** Gate 3 is the gate that prevents deleting already-merged work — slug-scoping alone does not, because a previously shipped feature's docs can legitimately match the globs. Merge-base rather than base-tip is deliberate: if another feature added a matching path to the default branch *after* we branched, a base-tip test would report "exists on base" and we would fail to remove our own copy. Merge-base is precisely "what this branch started from", so the predicate reads exactly as intended — *this branch added it.* Gate 1's globs are anchored only on the right, so a slug that is a hyphenated suffix of another (`docs-policy` vs `gh-6-docs-policy`) glob-matches the longer slug's filename; that is left as-is deliberately, because gates 2–3 make the collision unreachable — a foreign feature's doc passes "exists at `HEAD` but not at `<merge-base>`" only if this branch itself committed it.

*The stripped state, defined once.* A branch is **stripped** iff the design doc is absent at tip **and** at least one commit in `<merge-base>..HEAD` carries the trailer `dev-flow-stripped: <slug>`. In this state, front-matter reads have **defined answers, not failed producers**: the recorded `stops` is empty — a recorded `pre-merge` stop halts at the merge gate's `stops` consultation (Stage 5), *before* any strip, so no branch reaches the stripped state with a stop outstanding — and `docs:` is never consulted, because no path can pass gate 2 above once the strip removed it. This is the same move gate 3 already makes: once the surrounding state is validated (here, the trailer proven in range), a negative probe is an unambiguous answer, so Command discipline's halt-on-failure rule is satisfied, not suspended — nothing failed to produce. An absent design doc **without** the trailer is not the stripped state and keeps its existing meaning exactly: foreign branch, halt.
````

- [x] **Step 2: Append the mirrored sub-sections in the worktree SKILL.md**

In `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`, append the same two sub-sections after the `*Resolution happens once, at intake.*` paragraph. Exactly one substitution applies to this text:

- `` `dev-flow-stripped: <slug>` `` → `` `dev-flow-worktree-stripped: <slug>` `` (one occurrence, in *The stripped state*).

Everything else — both `sh` fences, the three numbered gates, the glob patterns, every sentence — is byte-identical.

- [x] **Step 3: Verify the gates and the trailer naming**

Run:

```bash
cd /Users/taylor/dev/claude-plugins
echo "== dev-flow"
grep -c -F 'merge_base=$(git merge-base HEAD "origin/<baseRef>")' plugins/dev-flow/skills/dev-flow/SKILL.md
grep -c -F 'git cat-file -e "$merge_base:$P"' plugins/dev-flow/skills/dev-flow/SKILL.md
grep -c -F -e '1. `P` matches `docs/superpowers/specs/*-<slug>-design.md` or `docs/superpowers/plans/*-<slug>-plan.md`.' plugins/dev-flow/skills/dev-flow/SKILL.md
grep -c -F -e '*The stripped state, defined once.*' plugins/dev-flow/skills/dev-flow/SKILL.md
grep -n -F -e '*Resolution happens once, at intake.*' -e '*Qualifying paths — what a strip may remove.*' -e '*The stripped state, defined once.*' -e '**Doc git lifecycle' plugins/dev-flow/skills/dev-flow/SKILL.md
echo "== dev-flow-worktree"
grep -c -F 'merge_base=$(git merge-base HEAD "origin/<baseRef>")' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
grep -c -F 'git cat-file -e "$merge_base:$P"' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
grep -c -F -e '1. `P` matches `docs/superpowers/specs/*-<slug>-design.md` or `docs/superpowers/plans/*-<slug>-plan.md`.' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
grep -c -F -e '*The stripped state, defined once.*' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
grep -n -F -e '*Resolution happens once, at intake.*' -e '*Qualifying paths — what a strip may remove.*' -e '*The stripped state, defined once.*' -e '**Doc git lifecycle' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
```

Expected: `1` for each of the eight `grep -c` checks, and each `grep -n` prints exactly four numbered lines **in this order** — `*Resolution happens once, at intake.*`, `*Qualifying paths…*`, `*The stripped state, defined once.*`, `**Doc git lifecycle` — proving both sub-sections landed inside the Docs policy block and before Doc git lifecycle.

Note: gate 1 is checked as its **full line**, not as a bare glob total. The bare glob `docs/superpowers/specs/*-<slug>-design.md` appears **twice** per file after this task — gate 1 plus the pre-existing Branch-ownership bullet — so a whole-file glob count would be `2`, not `1` (Global Constraints, *Verification-command form*).

- [x] **Step 4: Verify no cross-contaminated trailer names**

Run:

```bash
cd /Users/taylor/dev/claude-plugins
grep -c -F 'dev-flow-worktree-stripped' plugins/dev-flow/skills/dev-flow/SKILL.md
grep -c -F 'dev-flow-stripped' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
grep -c -F 'dev-flow-stripped: <slug>' plugins/dev-flow/skills/dev-flow/SKILL.md
grep -c -F 'dev-flow-worktree-stripped: <slug>' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
```

Expected: `0`, `0`, `1`, `1`. (`dev-flow-worktree-stripped` does not contain the substring `dev-flow-stripped`, so the second count being `0` is a real check, not a tautology.)

- [x] **Step 5: Commit**

```bash
cd /Users/taylor/dev/claude-plugins
git add plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
git commit -m "dev-flow: define qualifying paths and the stripped state in the Artifact Contract"
```

---

### Task 4: Ignore enforcement at entry step 0

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md` (branch-entry procedure, before existing step 1, ~line 102)
- Modify: `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` (worktree-entry procedure: new step 0; step 3 loses its exclude-ensure; step 4's addressing enumeration grows)
- Test: none (verify by grep)

**Interfaces:**
- Consumes: Task 1's Command-discipline bullet (this step is its first enforcement site) and Task 2's `.claude/dev-flow.local.md` filename.
- Produces: entry **step 0** in both files. Nothing later references it by number, but Task 9's Stage 5 relies on the settings file being excluded so the strip commit cannot sweep it in.

**Context:** The settings file is git-ignored *by intent*, but the user creates it, so nothing guarantees it actually is. The exclude file is resolved through git (`git rev-parse --git-path info/exclude`) rather than spelled `.git/info/exclude`, because `.git` is a **file**, not a directory, in any linked worktree. `--git-path` resolves to the main repository's shared `info/exclude` from any worktree, so one write covers the main checkout and every worktree at once. This runs at **every** stage boundary (entry is re-run at each), not once at intake, so a settings file created mid-run is excluded before any Execute-stage broad `git add` can sweep it in. It is ordered ahead of the dirty-checkout gate so a not-yet-excluded settings file cannot trip that gate as an untracked file.

In `dev-flow-worktree` this is an *extension of existing machinery, not new machinery*: the Create step already ensured `.claude/worktrees/` was excluded. That ensure **moves** to step 0 and covers both patterns in one block. Step 0 still precedes Create's `git worktree add`, so the container is ignored before it exists.

- [x] **Step 1: Insert step 0 in `plugins/dev-flow/skills/dev-flow/SKILL.md`**

Find these two consecutive lines:

```
*Branch entry — the orchestrator runs this at each stage boundary, first run and resume:*
1. **Already there:** if the current branch is `<username>/<slug>`, no switch is needed — skip to step 5 (ensure runnable) / step 6 (resume dirtiness).
```

Insert the following **between** them (i.e. after the italic heading line, before existing step 1). Do **not** renumber steps 1–6:

````
0. **Ensure the settings file is excluded** — idempotent, and first, *before* the dirty-checkout gate, so a not-yet-excluded settings file cannot trip that gate as an untracked file. Per Command discipline the exclude file is resolved through git, never spelled as a `.git/...` literal:

   ```sh
   exclude_file=$(git rev-parse --git-path info/exclude)   # failure or empty halts
   grep -qxF '.claude/dev-flow.local.md' "$exclude_file" || printf '%s\n' '.claude/dev-flow.local.md' >> "$exclude_file"
   ```

   A local exclude, never a committed `.gitignore` edit — which would itself pollute the PR diff. Grep the file rather than `git check-ignore`. Because entry runs at every stage boundary and this check is idempotent, a settings file created mid-run is excluded before any Execute-stage broad `git add` can sweep it in.
````

- [x] **Step 2: Insert step 0 in the worktree SKILL.md**

In `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`, find these two consecutive lines:

```
*Worktree entry — the orchestrator runs this at each stage boundary, first run and resume:*
1. **Locate:** in `git worktree list --porcelain`, the entry whose `branch` is `refs/heads/<username>/<slug>`; its `worktree <path>` is the pipeline worktree. (Git allows a branch in at most one worktree, so the match is unique.)
```

Insert the following **between** them. Note this variant covers **two** patterns, so it uses a loop — this is a deliberate, expected divergence from the `dev-flow` copy and the parity sweep in Task 11 accounts for it:

````
0. **Ensure the pipeline's local paths are excluded** — idempotent, and first, so the worktree container is ignored before it exists and a settings file created mid-run is excluded before any Execute-stage broad `git add` can sweep it in. Per Command discipline the exclude file is resolved through git, never spelled as a `.git/...` literal — `.git` is a file, not a directory, in any linked worktree:

   ```sh
   exclude_file=$(git rev-parse --git-path info/exclude)   # failure or empty halts
   for pat in '.claude/worktrees/' '.claude/dev-flow.local.md'; do
     grep -qxF "$pat" "$exclude_file" || printf '%s\n' "$pat" >> "$exclude_file"
   done
   ```

   `--git-path` resolves to the main repository's shared `info/exclude` from any worktree, so one write covers the main checkout and every worktree at once. A local exclude, never a committed `.gitignore` edit — which would itself pollute the PR diff. Grep the file rather than `git check-ignore`, which misfires on the not-yet-created directory. This step precedes step 3's `git worktree add`, so the container is ignored before it is created.
````

- [x] **Step 3: Remove the now-duplicated exclude-ensure from the worktree's Create step**

In the same file, find step 3 in full:

```
3. **Create** if neither exists — legal only as Stage 1's first act (the resume table routes every other no-branch state to Design; any other stage landing here halts: contract violation). Ensure the container is ignored — add `.claude/worktrees/` to `<main-root>/.git/info/exclude` if absent (`grep -qxF '.claude/worktrees/' <exclude> || echo '.claude/worktrees/' >> <exclude>` — a local exclude, never a committed `.gitignore` edit, which would pollute the PR diff; grep the file rather than `git check-ignore`, which misfires on the not-yet-created directory) — then `git worktree add <path> -b <username>/<slug> <base>`. **If creation fails (sandbox/permission), halt and report; there is no work-in-place fallback.**
```

Replace it with:

```
3. **Create** if neither exists — legal only as Stage 1's first act (the resume table routes every other no-branch state to Design; any other stage landing here halts: contract violation). The container is already ignored by step 0, which always precedes this step: `git worktree add <path> -b <username>/<slug> <base>`. **If creation fails (sandbox/permission), halt and report; there is no work-in-place fallback.**
```

This must leave **exactly one** `.claude/worktrees/` exclude-ensure in the file — the one in step 0. The old `<main-root>/.git/info/exclude` literal is deleted, not kept: it is precisely the `.git/...` literal Command discipline forbids.

- [x] **Step 4: Extend worktree entry step 4's addressing enumeration (Command discipline item 3)**

Still in `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`, inside step 4 (**Enter**), find this exact fragment:

```
and **Stage 4's `gh pr create`, the branch push on any halt/stop, and the `review clean` marker-SHA read** — so all of it (baseline/per-task suites, `HEAD`-relative commands, the review's post-fix suite, PR creation and push) runs against the pipeline tree and branch;
```

Replace it with:

```
and **Stage 4's `gh pr create`, the branch push on any halt/stop, the `review clean` marker-SHA read, and every command the merge gate runs — its `git push`, the base-ref `git fetch`, `git merge-base`, `git cat-file -e`, `git rev-list`, `git diff --name-status`, `git rm`, the strip commit, and the strip push** — so all of it (baseline/per-task suites, `HEAD`-relative commands, the review's post-fix suite, PR creation and push, the strip) runs against the pipeline tree and branch;
```

This is the worktree-specific third item of Command discipline, and this enumeration is its durable home: every git command this change adds derives its target from cwd and the current branch, so it must be driven from inside the pipeline worktree or explicitly addressed via `git -C <worktree-path>`. The commands named here are added by Tasks 6 and 9; naming them now is intentional — this is prose, so there is no ordering dependency.

- [x] **Step 5: Verify step 0 exists in both, and the worktree duplicate is gone**

Run:

```bash
cd /Users/taylor/dev/claude-plugins
echo "== step 0 present"
grep -c -E '^0\. \*\*Ensure ' plugins/dev-flow/skills/dev-flow/SKILL.md
grep -c -E '^0\. \*\*Ensure ' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
echo "== git-path resolution used in both"
grep -c -F 'exclude_file=$(git rev-parse --git-path info/exclude)' plugins/dev-flow/skills/dev-flow/SKILL.md
grep -c -F 'exclude_file=$(git rev-parse --git-path info/exclude)' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
echo "== no .git/info/exclude literal remains anywhere (was 1 in the worktree file)"
grep -c -F '.git/info/exclude' plugins/dev-flow/skills/dev-flow/SKILL.md
grep -c -F '.git/info/exclude' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
echo "== exactly one worktree-container exclude, now in step 0"
grep -n -F "'.claude/worktrees/'" plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
```

Expected: `1`, `1`, `1`, `1`; then `0`, `0` — the forbidden literal is gone. It was `0` in the dev-flow file and `1` in the worktree file before this task, so the worktree `0` is the real check that Step 3's deletion landed. The Command-discipline bullet mentions `.git/...`, which does not contain this literal, so `0` is achievable. The last command must print **exactly one** line, and its line number must fall inside entry step 0 (before the `1. **Locate:**` line).

- [x] **Step 6: Read back step 0 and step 3 in the worktree file**

Run:

```bash
cd /Users/taylor/dev/claude-plugins
sed -n '/^\*Worktree entry/,/^5\. \*\*Ensure runnable/p' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
```

Confirm by reading: step 0 exists and loops over both patterns; step 1 (Locate), 2 (Re-attach) unchanged; step 3 (Create) no longer contains any `grep -qxF` or `info/exclude` text and now says "already ignored by step 0"; step 4 (Enter) enumerates the merge gate's commands.

- [x] **Step 7: Verify the numbering was not disturbed**

Run:

```bash
cd /Users/taylor/dev/claude-plugins
sed -n '/^\*Branch entry — the orchestrator/,/^6\. /p'   plugins/dev-flow/skills/dev-flow/SKILL.md | grep -c -E '^[0-6]\. \*\*'
sed -n '/^\*Worktree entry — the orchestrator/,/^6\. /p' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md | grep -c -E '^[0-6]\. \*\*'
sed -n '/^\*Branch entry — the orchestrator/,/^6\. /p'   plugins/dev-flow/skills/dev-flow/SKILL.md | grep -o -E '^[0-6]\.' | tr '\n' ' '; echo
sed -n '/^\*Worktree entry — the orchestrator/,/^6\. /p' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md | grep -o -E '^[0-6]\.' | tr '\n' ' '; echo
```

Expected: `7` and `7` (was 6 before this task), then `0. 1. 2. 3. 4. 5. 6.` twice — ascending, no gaps, no duplicates.

- [x] **Step 8: Commit**

```bash
cd /Users/taylor/dev/claude-plugins
git add plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
git commit -m "dev-flow: enforce the settings-file ignore at entry step 0 in both variants"
```

---

### Task 5: Branch ownership gains the stripped-state clause, and the resume table gains its route

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md` (Branch ownership bullet ~line 79; resume table row ~line 127)
- Modify: `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` (Branch ownership bullet ~line 77; resume table row ~line 119)
- Test: none (verify by grep)

**Interfaces:**
- Consumes: Task 3's `merge_base` variable and *stripped state* definition, cited by name.
- Produces: the ownership predicate's second limb and the resume table's third outcome. Task 9's Stage 5 assumes a resumed stripped branch arrives at the merge gate.

**Context:** Between the strip commit and the merge, the branch tip carries no design doc. Under today's ownership predicate that reads as **foreign**, so the user gets a halt telling them to rename the slug or delete the branch — for a branch that is entirely ours and one command from merging. One narrow, explicit clause fixes it. Ownership is deliberately *not* broadened to "the branch's history ever contained our design doc": that is inference, and it weakens a load-bearing guard for every non-strip case in order to serve one.

- [x] **Step 1: Extend the Branch ownership bullet in `plugins/dev-flow/skills/dev-flow/SKILL.md`**

Find the end of the `- **Branch ownership …**` bullet, which currently reads:

```
(The pipeline itself deletes no branches — see Stage 5 — so the only thing to guard is *building on* a branch that isn't ours, never destroying one.)
```

Append the following to that **same line** (it is one long unwrapped bullet — do not start a new line):

```
 **dev-flow also owns a branch if any commit in `<merge-base>..HEAD` carries the trailer `dev-flow-stripped: <slug>`** — the stripped state (Docs policy), where the design doc is deliberately gone from tip and the branch is one command from merging. Detection: `git log "$merge_base..HEAD" --grep='^dev-flow-stripped: <slug>$' --format=%H` is non-empty, using the validated `merge_base` from Docs policy — an empty one silently yields the range `HEAD..HEAD`, which would report "no trailer" and produce exactly the misleading foreign-branch halt this clause exists to prevent. Scanning the commit range rather than only the tip commit is free and strictly more robust: it survives a stripped-state halt that the user pushed a commit on top of. Ownership is deliberately **not** broadened to "the branch's history ever contained our design doc" — that would work, but it is inference, and it weakens a load-bearing safety guard for every non-strip case in order to serve one; the trailer is explicit and fires only where it is written.
```

- [x] **Step 2: Replace the resume table's no-design row in `plugins/dev-flow/skills/dev-flow/SKILL.md`**

Find this table row (one line):

```
| Branch exists; no design doc with `dev-flow` front-matter at tip | **Foreign** (has commits beyond `<base>`, per Branch ownership) -> **Halt** — never adopt or delete a branch we didn't create. **Empty beyond `<base>`** (our just-created branch, Design crashed before committing) -> Design (redo; uncommitted drafts discarded) |
```

Replace it with:

```
| Branch exists; no design doc with `dev-flow` front-matter at tip | **No commits beyond `<base>`** (our just-created branch, Design crashed before committing) -> Design (redo; uncommitted drafts discarded). **`dev-flow-stripped: <slug>` trailer in `<merge-base>..HEAD`** (the stripped state, per Docs policy) -> **Merge gate** — the gate's ordinary steps handle it; there is no stripped-only entry point. **Otherwise foreign** (has commits beyond `<base>`, per Branch ownership) -> **Halt** — never adopt or delete a branch we didn't create |
```

The three outcomes are evaluated in that written order: empty first, trailer second, foreign last.

- [x] **Step 3: Make both mirrored edits in the worktree SKILL.md**

In `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`, apply Steps 1 and 2 with these substitutions and no others:

- `**dev-flow also owns a branch …**` → `**dev-flow-worktree also owns a branch …**`
- `` `dev-flow-stripped: <slug>` `` → `` `dev-flow-worktree-stripped: <slug>` `` (three occurrences total across the two edits: twice in the ownership clause — prose and `--grep` — and once in the table row).
- The table row's `no design doc with \`dev-flow\` front-matter at tip` → `no design doc with \`dev-flow-worktree\` front-matter at tip` (this is already the existing wording in that file — keep it).

The worktree file's ownership bullet ends with the identical sentence `(The pipeline itself deletes no branches — see Stage 5 — so the only thing to guard is *building on* a branch that isn't ours, never destroying one.)`, so the anchor is the same.

- [x] **Step 4: Verify both edits**

Run:

```bash
cd /Users/taylor/dev/claude-plugins
echo "== ownership clause"
grep -c -F 'also owns a branch if any commit in `<merge-base>..HEAD` carries the trailer' plugins/dev-flow/skills/dev-flow/SKILL.md
grep -c -F 'also owns a branch if any commit in `<merge-base>..HEAD` carries the trailer' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
echo "== resume row routes to the merge gate"
grep -c -F 'the stripped state, per Docs policy) -> **Merge gate**' plugins/dev-flow/skills/dev-flow/SKILL.md
grep -c -F 'the stripped state, per Docs policy) -> **Merge gate**' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
echo "== the old foreign-first row is gone"
grep -c -F '| **Foreign** (has commits beyond `<base>`, per Branch ownership) -> **Halt** — never adopt' plugins/dev-flow/skills/dev-flow/SKILL.md
grep -c -F '| **Foreign** (has commits beyond `<base>`, per Branch ownership) -> **Halt** — never adopt' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
```

Expected: `1`, `1`, `1`, `1`, `0`, `0`.

- [x] **Step 5: Verify the resume table still has exactly one row per check**

Run:

```bash
cd /Users/taylor/dev/claude-plugins
grep -c -E '^\| (No |Branch exists|Design committed|Plan at tip|Plan fully checked|Open PR|No row matches)' plugins/dev-flow/skills/dev-flow/SKILL.md
grep -c -E '^\| (No |Branch exists|Design committed|Plan at tip|Plan fully checked|Open PR|No row matches)' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
```

Expected: `11` and `11` — the same eleven rows as before this task; the no-design row gained an outcome, it did not split into new rows.

- [x] **Step 6: Commit**

```bash
cd /Users/taylor/dev/claude-plugins
git add plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
git commit -m "dev-flow: own the stripped state in branch ownership and route it in the resume table"
```

---

### Task 6: Marker validity in Review state

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md` (Artifact Contract — Review state ~line 117, and the resume table's two `Open PR` rows ~lines 131–132)
- Modify: `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` (Artifact Contract — Review state ~line 109, and the resume table's two `Open PR` rows ~lines 123–124)
- Test: none (verify by grep)

**Interfaces:**
- Consumes: Task 3's qualifying-path gates (cited as "Docs policy's qualifying-path gates 1 and 3") and the trailer name.
- Produces: the term **"Marker validity"**, which Task 9's Stage 5 step 1 and this task's own resume-table rows reference by name instead of restating the rule.

**Context:** A strip commit moves the head, so the `review clean @ <sha>` marker goes stale, and the contract's current rule says stale means re-review. Re-review in the stripped state is incoherent — it would be a `diff`-mode review of a branch whose design doc *and* plan are deleted, with no artifact to review against; if it committed anything the head would move again. So validity is redefined once, here at the shared boundary, rather than exempted at the call site. The redefinition is unsatisfiable on a `commit`-policy run, so "any push invalidates the marker" still holds everywhere it held before.

- [x] **Step 1: Replace the Review state paragraph in `plugins/dev-flow/skills/dev-flow/SKILL.md`**

Find this paragraph (one line):

```
**Review state.** After Stage 4's review has committed its fixes and the stage has pushed, post a PR comment with the marker line `dev-flow: review clean @ <full-head-sha>`. Detection: marker SHA equals the current head -> merge gate; stale SHA -> re-review (any push, including a CI fix, correctly invalidates the marker); no marker -> PR review. (A label can't carry the SHA and goes silently stale — rejected.)
```

Replace it with:

````
**Review state.** After Stage 4's review has committed its fixes and the stage has pushed, post a PR comment with the marker line `dev-flow: review clean @ <full-head-sha>`. Detection: marker **valid** -> merge gate; marker present but **invalid** -> re-review; no marker -> PR review. (A label can't carry the SHA and goes silently stale — rejected.)

**Marker validity.** The marker is valid **iff** the marker SHA equals the current head, **or** every commit in `<marker-sha>..HEAD` carries the trailer `dev-flow-stripped: <slug>` **and** `git diff --name-status <marker-sha> HEAD` contains only `D` entries, each for a path satisfying Docs policy's qualifying-path gates 1 and 3 — gate 2 ("exists at `HEAD`") is evaluated **at the marker SHA** here, since the paths being gone from head is the point. That second clause is a mechanical proof that the only change since the reviewed head is the intended deletion: any non-deletion entry, any deletion outside this branch's own scaffolding, or any trailer-less commit in the range invalidates it. It is unsatisfiable on a `commit`-policy run (no trailer commits can exist), so "any push, including a CI fix, correctly invalidates the marker" still holds everywhere it held before. The strip is verified by this rule, **not** by re-posting the marker — re-posting would assert "reviewed and suite-green at this SHA" for a SHA nothing reviewed, and would be fooled by an unrelated commit landing in the gap.

The trailer conjunct is mechanical, not eyeballed:

```sh
total=$(git rev-list --count "<marker-sha>..HEAD")                                          # failure or empty halts
stripped=$(git rev-list --count --grep='^dev-flow-stripped: <slug>$' "<marker-sha>..HEAD")  # failure or empty halts
[ "$total" -eq "$stripped" ]    # equal <=> every commit in the range carries the trailer
```

Both counts derive from the same range, so equality is exactly "every commit matched"; one trailer-less commit — a manual push, a merge from the default branch — breaks it. The grep is anchored at both ends so a prefix- or suffix-sharing slug cannot false-match. On inequality, the offending SHAs come from the same grep inverted: `git log "<marker-sha>..HEAD" --grep='^dev-flow-stripped: <slug>$' --invert-grep --format=%H`. Per Command discipline, `<marker-sha>` is validated non-empty before either command — an empty one collapses the range to `HEAD..HEAD`, where `0 -eq 0` would falsely validate.
````

- [x] **Step 2: Make the mirrored edit in the worktree SKILL.md**

In `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`, find the corresponding paragraph:

```
**Review state.** After Stage 4's review has committed its fixes and the stage has pushed, post a PR comment with the marker line `dev-flow-worktree: review clean @ <full-head-sha>`. Detection: marker SHA equals the current head -> merge gate; stale SHA -> re-review (any push, including a CI fix, correctly invalidates the marker); no marker -> PR review. (A label can't carry the SHA and goes silently stale — rejected.)
```

Replace it with the same text as Step 1, with exactly these substitutions:

- `` `dev-flow: review clean @ <full-head-sha>` `` → `` `dev-flow-worktree: review clean @ <full-head-sha>` `` (already the existing wording — keep it).
- `dev-flow-stripped: <slug>` → `dev-flow-worktree-stripped: <slug>` (**three** occurrences: the prose sentence, the `rev-list --grep`, and the `log --invert-grep`).

Everything else, including the `sh` fence's alignment, is byte-identical.

- [x] **Step 3: Update the resume table's two marker rows to speak of validity, in both files**

Marker validity is redefined **once, at the shared boundary**, so every call site must read the new rule rather than the old "SHA equals head" test. The resume table has two such call sites. They matter in a real case: if the design doc was already committed on the default branch before the branch was created, gate 3 spares it, only the plan is stripped, and the doc is still at tip — so the stripped-state resume row does not match and these two rows decide the route. Left unchanged they would force a spurious re-review of a branch whose strip is already mechanically proven.

In `plugins/dev-flow/skills/dev-flow/SKILL.md`, replace these two consecutive rows:

```
| Open PR; no `review clean @ <current head>` marker | PR review |
| Open PR; marker matches head | Merge gate (CI, `stops` from front-matter) |
```

with:

```
| Open PR; no `review clean` marker, or the marker is **invalid** (Marker validity) | PR review |
| Open PR; marker **valid** (Marker validity — SHA equals head, or a proven strip since) | Merge gate (CI, `stops` from front-matter) |
```

Apply the identical replacement in `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`; both files' rows are byte-identical before and after (they contain no plugin name).

- [x] **Step 4: Verify**

Run:

```bash
cd /Users/taylor/dev/claude-plugins
echo "== marker validity heading"
grep -c -F '**Marker validity.**' plugins/dev-flow/skills/dev-flow/SKILL.md
grep -c -F '**Marker validity.**' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
echo "== the count-equality proof"
grep -c -F '[ "$total" -eq "$stripped" ]' plugins/dev-flow/skills/dev-flow/SKILL.md
grep -c -F '[ "$total" -eq "$stripped" ]' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
echo "== old stale-SHA rule removed"
grep -c -F 'Detection: marker SHA equals the current head -> merge gate; stale SHA -> re-review' plugins/dev-flow/skills/dev-flow/SKILL.md
grep -c -F 'Detection: marker SHA equals the current head -> merge gate; stale SHA -> re-review' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
echo "== anchored greps, per-variant trailer — listed by line, not counted"
grep -n -F -e "^dev-flow-stripped: <slug>\$" plugins/dev-flow/skills/dev-flow/SKILL.md
grep -n -F -e "^dev-flow-worktree-stripped: <slug>\$" plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
echo "== Marker validity sits between Review state and the resume table"
for f in plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md; do
  grep -n -F -e '**Review state.**' -e '**Marker validity.**' -e 'total=$(git rev-list --count' -e '**Resume table**' "$f"
done
echo "== resume table now routes on validity, and the old rows are gone"
grep -c -F '| Open PR; marker matches head | Merge gate' plugins/dev-flow/skills/dev-flow/SKILL.md
grep -c -F '| Open PR; marker matches head | Merge gate' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
grep -c -F 'marker **valid** (Marker validity' plugins/dev-flow/skills/dev-flow/SKILL.md
grep -c -F 'marker **valid** (Marker validity' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
grep -c -E '^\| (No |Branch exists|Design committed|Plan at tip|Plan fully checked|Open PR|No row matches)' plugins/dev-flow/skills/dev-flow/SKILL.md
grep -c -E '^\| (No |Branch exists|Design committed|Plan at tip|Plan fully checked|Open PR|No row matches)' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
```

Expected: `1`, `1`, `1`, `1`, `0`, `0`. Then each anchored-trailer `grep -n` prints exactly **three** numbered lines — the Branch-ownership clause (Task 5), the `stripped=$(git rev-list …)` fence line, and the `--invert-grep` prose line. Then each ordering loop prints four lines per file in the order `**Review state.**`, `**Marker validity.**`, the count fence, `**Resume table**` — proving Marker validity landed between the Review state paragraph it extends and the resume table, not elsewhere. Then `0`, `0`, `1`, `1`, and finally `11`, `11` — the resume table still has exactly eleven rows.

- [x] **Step 5: Commit**

```bash
cd /Users/taylor/dev/claude-plugins
git add plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
git commit -m "dev-flow: redefine marker validity so a verified strip does not force a re-review"
```

---

### Task 7: Stage 1 resolves and stamps the policy

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md` (`### Stage 1 — Design`, ~line 151)
- Modify: `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` (`### Stage 1 — Design`, ~line 143)
- Test: none (verify by grep)

**Interfaces:**
- Consumes: Task 2's Docs policy block (resolution table and precedence).
- Produces: the guarantee every later stage relies on — that `docs:` is present in the design doc's front-matter from the first review onward.

**Context:** Resolution happens exactly once, at intake, and the stamp must land **before** the review runs, because the review rewrites the doc and (by its contract) preserves front-matter. A resume never re-reads the settings file: the front-matter value wins.

- [x] **Step 1: Insert the intake bullet in `plugins/dev-flow/skills/dev-flow/SKILL.md`**

Find this line inside `### Stage 1 — Design`:

```
- The **orchestrator** invokes `dev-flow:adversarial-review` (mode: `design`) in-context on the feature branch — it is the approval gate that substitutes for the user's. The review rewrites the design and commits it on the branch (its contract); the orchestrator then checks the returned provenance line (Cross-Cutting Concerns) before proceeding. No separate apply or commit step.
```

Insert the following single line **immediately before** it:

```
- **Docs policy (intake):** resolve `docs` per the Artifact Contract's Docs policy — read `.claude/dev-flow.local.md`, apply the resolution table (emitting the one-line warning on an unrecognized value), and stamp the result into the design doc's `dev-flow` front-matter block alongside `slug` and `stops`. Do this **before** the review runs, so the review's rewrite carries it. A `docs` value already present in the front-matter wins outright — a resume never re-reads the settings file.
```

- [x] **Step 2: Insert the mirrored bullet in the worktree SKILL.md**

In `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`, find:

```
- The **orchestrator** invokes `dev-flow-worktree:adversarial-review` (mode: `design`) in-context from inside the worktree, passing the worktree as `working-dir` — it is the approval gate that substitutes for the user's. The review rewrites the design and commits it on the branch (its contract); the orchestrator then checks the returned provenance line (Cross-Cutting Concerns) before proceeding. No separate apply or commit step.
```

Insert the same bullet immediately before it, with one substitution: `the design doc's \`dev-flow\` front-matter block` → `the design doc's \`dev-flow-worktree\` front-matter block`. `.claude/dev-flow.local.md` is **not** substituted.

- [x] **Step 3: Verify placement and ordering**

Run:

```bash
cd /Users/taylor/dev/claude-plugins
for f in plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md; do
  echo "== $f"
  grep -n -F -e '- **Docs policy (intake):**' "$f"
  grep -n -F 'adversarial-review` (mode: `design`)' "$f"
done
```

Expected for each file: exactly one `Docs policy (intake)` line, and its line number is **lower** than the `mode: design` review line (the stamp precedes the review).

- [x] **Step 4: Verify the settings file is named once per Stage 1**

Run:

```bash
cd /Users/taylor/dev/claude-plugins
grep -n -F -e '.claude/dev-flow.local.md' plugins/dev-flow/skills/dev-flow/SKILL.md
grep -n -F -e '.claude/dev-flow.local.md' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
grep -c -F -e 'dev-flow-worktree.local.md' plugins/dev-flow/skills/dev-flow/SKILL.md
grep -c -F -e 'dev-flow-worktree.local.md' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
```

Expected: each `grep -n` prints exactly **three** numbered lines, one per site — the Docs policy block's `*The setting.*` sentence, entry step 0's one-line `grep`/`for`, and this task's Stage 1 bullet — then `0`, `0`. Listing the lines rather than counting them makes a mis-placed site visible instead of merely uncounted.

- [x] **Step 5: Commit**

```bash
cd /Users/taylor/dev/claude-plugins
git add plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
git commit -m "dev-flow: resolve and stamp the docs policy at Stage 1 intake"
```

---

### Task 8: Stage 4 discloses the strip in the PR body

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md` (`### Stage 4 — PR`, ~line 172)
- Modify: `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` (`### Stage 4 — PR`, ~line 164)
- Test: none (verify by grep)

**Interfaces:**
- Consumes: Task 2's `docs` front-matter key.
- Produces: nothing later depends on.

**Context:** A stripped PR's body links doc paths that will not exist on the default branch after merge. The design rejected fixing that with SHA permalinks (a Stage 4 step to repair two dead links in a merged PR body — a fix roughly as costly as the wart). Instead the body carries one free line saying so.

- [x] **Step 1: Insert the bullet in `plugins/dev-flow/skills/dev-flow/SKILL.md`**

Find this line (the first bullet of `### Stage 4 — PR`):

```
- `gh pr create`; PR body links the spec + plan paths and derives a summary from them. When the slug carries a task/issue ID (see Slug), reference it in the PR body — `Closes #42` for a GitHub issue, or the plain Linear/Jira key for those trackers. If an open PR already exists for the branch, reuse it — skip create.
```

Insert the following single line **immediately after** it:

```
- **Under `docs: strip`** (front-matter, per Docs policy), the PR body also carries one line noting that the design and plan live in this PR's commit history and are removed before merge by repo policy — so the linked paths will not exist on the default branch after the merge. Under `docs: commit` the body is unchanged.
```

- [x] **Step 2: Insert the mirrored bullet in the worktree SKILL.md**

In `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`, find the identical first bullet of `### Stage 4 — PR` (its text is the same in both files) and insert the same line immediately after it. **No substitutions apply** — this bullet contains no plugin name.

- [x] **Step 3: Verify byte-identity and placement**

Run:

```bash
cd /Users/taylor/dev/claude-plugins
diff <(grep -F "Under \`docs: strip\`" plugins/dev-flow/skills/dev-flow/SKILL.md) \
     <(grep -F "Under \`docs: strip\`" plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md) && echo IDENTICAL
for f in plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md; do
  echo "== $f"; grep -n -E '^### Stage 4 — PR|^- `gh pr create`|^- \*\*Under `docs: strip`' "$f"
done
```

Expected: `IDENTICAL`, then for each file three lines whose numbers ascend in exactly that order (heading, `gh pr create`, the new bullet).

- [x] **Step 4: Commit**

```bash
cd /Users/taylor/dev/claude-plugins
git add plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
git commit -m "dev-flow: disclose the pending strip in the PR body under docs: strip"
```

---

### Task 9: Stage 5 becomes a re-entrant merge gate

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md` (`### Stage 5 — Merge`, ~lines 180–187)
- Modify: `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` (`### Stage 5 — Merge`, ~lines 172–179)
- Test: none (verify by grep + read-back)

**Interfaces:**
- Consumes: Task 3's qualifying-path gates and stripped-state rule; Task 6's **Marker validity**; Task 5's resume route into this gate.
- Produces: the five-step gate. This is the last behavioral edit; nothing after it depends on new names.

**Context:** The strip runs *inside* the gate and **re-enters it at step 1** rather than running a private post-strip tail, so first run and resume travel the identical path and no resume-only entry point exists. The re-wait at step 2 is load-bearing: where branch protection requires checks, GitHub demands they pass on the new head. Step 1's leading `git push` closes a real crash window — a crash between the strip commit and its push would otherwise merge the un-stripped remote head. Step 3 (the `stops` read) sits deliberately **before** step 4 (the strip), so a `pre-merge` halt always leaves the branch intact with both docs at tip.

- [ ] **Step 1: Replace the first four bullets of Stage 5 in `plugins/dev-flow/skills/dev-flow/SKILL.md`**

Find this contiguous block — it begins at the first line after `### Stage 5 — Merge` and ends at the `- **Merge:**` bullet, inclusive:

```
- Confirm the `review clean` marker SHA equals the current head (else re-review).
- **Bounded CI wait:** run `gh pr checks <pr> --watch` under a hard cap (default 10 minutes, enforced via the Bash tool's `timeout: 600000`, since `gh pr checks --watch` has no native timeout of its own). Exactly four outcomes — distinguish failure from no-checks by output text, not exit code (both exit 1; pending exits 8):
  - **All checks pass** -> proceed.
  - **Any check fails** -> halt and report.
  - **Still pending at the cap** -> halt and report "CI still pending" (resume re-enters the merge gate for free). Never an open-ended block.
  - **Output contains "no checks reported"** (the repo has no CI on this PR) -> proceed. This is safe only because the marker already certifies Stage 4's test gate — suite green at this head, or no suite exists. Never read "no checks" as a green test signal on its own.
- Consult `stops` from front-matter; a `pre-merge` stop pauses here with the testing note.
- **Merge:** `gh pr merge <pr> --squash`. No `--delete-branch`, and no manual branch deletion anywhere — **the pipeline deletes no branches.** The merged **remote** branch is removed by the repository's *automatically delete head branches* setting (the standard GitHub configuration); the **local** `<username>/<slug>` branch is left for you to prune on your own schedule.
```

Replace the whole block with:

```
The merge gate is five steps and is **re-entrant**: step 4 can send the run back to step 1, so first run and resume travel the identical path and no resume-only entry point exists anywhere.

1. **Push, then confirm the marker.** `git push` first — a no-op when already up to date, and it closes a real crash window: a crash between a strip *commit* and its *push* would otherwise merge the un-stripped remote head. Then confirm the marker is **valid** per the Artifact Contract's Marker validity rule. Invalid -> re-review, **unless the design doc is no longer at tip**, where re-review is impossible (there is no artifact to review against): halt and report the offending SHA(s) and that the doc is gone. That is what a stripped branch which has diverged past its strip commit gets — a specific, honest halt rather than a misleading foreign-branch one, and never a re-review the stripped state cannot support.
2. **Bounded CI wait** against the current head: run `gh pr checks <pr> --watch` under a hard cap (default 10 minutes, enforced via the Bash tool's `timeout: 600000`, since `gh pr checks --watch` has no native timeout of its own). Exactly four outcomes — distinguish failure from no-checks by output text, not exit code (both exit 1; pending exits 8):
   - **All checks pass** -> proceed.
   - **Any check fails** -> halt and report.
   - **Still pending at the cap** -> halt and report "CI still pending" (resume re-enters the merge gate for free). Never an open-ended block.
   - **Output contains "no checks reported"** (the repo has no CI on this PR) -> proceed. This is safe only because the marker already certifies Stage 4's test gate — suite green at this head, or no suite exists. Never read "no checks" as a green test signal on its own.
3. **Consult `stops`** from the design doc's front-matter at tip; a `pre-merge` stop pauses **here**, with the testing note — before any strip, so a halted branch is always intact and fully resumable with both docs at tip. In the stripped state there is no doc at tip and this read is not attempted: the recorded stops are empty by the stripped-state rule (Docs policy) — proceed, never halt. (A doc-less tip *without* the trailer cannot reach this step; step 1 already halted it.)
4. **Strip, if the policy says so.** If any path qualifies under Docs policy's gates **and** the front-matter at tip says `docs: strip`: `git rm` the qualifying paths, commit with the trailer (`git commit -m "<msg>" --trailer "dev-flow-stripped: <slug>"`), push, and **re-enter this gate at step 1**. Evaluate qualification **first**: the gates are policy-agnostic — they return the same answer under `commit` and `strip` — so a `commit`-policy pass on an intact branch does reach the policy read and no-ops on the second conjunct. The ordering matters for exactly one case, the already-stripped branch: gate 2 ("exists at `HEAD`") fails for every removed path, so the step no-ops before any policy read — which is the point, because the stripped state has no front-matter left to read. Re-entry terminates by construction: the strip removed every qualifying path, so the next pass falls through. The re-wait at step 2 is not optional politeness — where branch protection requires checks, GitHub demands they pass on the new head; where there is no CI, step 2 returns "no checks reported" and proceeds, exactly as before.
5. **Merge:** `gh pr merge <pr> --squash`. No `--delete-branch`, and no manual branch deletion anywhere — **the pipeline deletes no branches.** The merged **remote** branch is removed by the repository's *automatically delete head branches* setting (the standard GitHub configuration); the **local** `<username>/<slug>` branch is left for you to prune on your own schedule.
```

Leave the `- **Cleanup (idempotent …)**` and `- **Final report:**` bullets that follow **exactly as they are**. Insert a blank line between step 5 and the `- **Cleanup` bullet so the numbered list and the bullet list render as separate lists.

- [ ] **Step 2: Make the mirrored replacement in the worktree SKILL.md**

In `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` the same four bullets appear, with one difference: its `- **Merge:**` bullet reads `No \`--delete-branch\`, and no manual branch deletion —` (no "anywhere") and ends with the extra sentence `(Cleanup below still removes the pipeline's own *worktree* — that is the pipeline's artifact, not your branch.)`.

Apply the same replacement, with exactly these differences from Step 1's text:

- Insert this sentence at the end of the opening paragraph: `Every git command in this gate is driven from inside the pipeline worktree (worktree entry, step 4).`
- `` --trailer "dev-flow-stripped: <slug>" `` → `` --trailer "dev-flow-worktree-stripped: <slug>" ``.
- Step 5 keeps the worktree file's existing merge wording verbatim: `5. **Merge:** \`gh pr merge <pr> --squash\`. No \`--delete-branch\`, and no manual branch deletion — **the pipeline deletes no branches.** The merged **remote** branch is removed by the repository's *automatically delete head branches* setting (the standard GitHub configuration); the **local** \`<username>/<slug>\` branch is left for you to prune on your own schedule. (Cleanup below still removes the pipeline's own *worktree* — that is the pipeline's artifact, not your branch.)`

Everything else, including all four CI-wait sub-bullets, is byte-identical to Step 1.

- [ ] **Step 3: Verify the gate's shape**

Run:

```bash
cd /Users/taylor/dev/claude-plugins
for f in plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md; do
  echo "== $f"
  grep -c -F 'The merge gate is five steps and is **re-entrant**' "$f"
  grep -n -E '^[1-5]\. \*\*(Push, then confirm the marker|Bounded CI wait|Consult|Strip, if the policy says so|Merge:)' "$f"
done
```

Expected for each file: `1`, then exactly five numbered lines `1.` through `5.` in ascending order.

- [ ] **Step 4: Verify ordering invariants and the removed old text**

Run:

```bash
cd /Users/taylor/dev/claude-plugins
echo "== stops read (step 3) precedes the strip (step 4)"
for f in plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md; do
  echo "== $f"
  grep -n -F '3. **Consult `stops`**' "$f"
  grep -n -F '4. **Strip, if the policy says so.**' "$f"
  grep -n -F '5. **Merge:**' "$f"
done
echo "== old single-line marker check is gone"
grep -c -F -e '- Confirm the `review clean` marker SHA equals the current head (else re-review).' plugins/dev-flow/skills/dev-flow/SKILL.md
grep -c -F -e '- Confirm the `review clean` marker SHA equals the current head (else re-review).' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
echo "== Cleanup and Final report survived"
grep -c -F -e '- **Cleanup (idempotent' plugins/dev-flow/skills/dev-flow/SKILL.md
grep -c -F -e '- **Cleanup (idempotent' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
grep -c -F -e '- **Final report:**' plugins/dev-flow/skills/dev-flow/SKILL.md
grep -c -F -e '- **Final report:**' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
```

Expected: the three line numbers ascend (3 < 4 < 5) in each file; then `0`, `0`; then `1`, `1`, `1`, `1`.

- [ ] **Step 5: Read back Stage 5 in full, both files**

Run:

```bash
cd /Users/taylor/dev/claude-plugins
sed -n '/^### Stage 5 — Merge/,/^---$/p' plugins/dev-flow/skills/dev-flow/SKILL.md
echo "======================================"
sed -n '/^### Stage 5 — Merge/,/^---$/p' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
```

Read both and confirm: the numbered gate renders as one list; the CI sub-bullets are indented under step 2; the Cleanup bullet is separated by a blank line; the worktree copy names the worktree in its opening paragraph and uses the `dev-flow-worktree-stripped` trailer.

- [ ] **Step 6: Commit**

```bash
cd /Users/taylor/dev/claude-plugins
git add plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
git commit -m "dev-flow: make Stage 5 a re-entrant merge gate that strips under docs: strip"
```

---

### Task 10: Document the setting in both READMEs

**Files:**
- Modify: `plugins/dev-flow/README.md` (new section after `## Stops`; extra smoke-test step)
- Modify: `plugins/dev-flow-worktree/README.md` (same)
- Test: none (verify by grep)

**Interfaces:**
- Consumes: the settings filename, key, and values from Task 2.
- Produces: the user-facing traceability the plugin-settings pattern asks for — both READMEs name the shared file, which is what makes the deliberate family-name departure (a `dev-flow-worktree` plugin reading a `dev-flow`-named file) discoverable.

**Context:** Three consequences are accepted by the design and must be stated plainly, because a user who does not know them will be surprised: the policy is per-developer (the file is git-ignored, so a teammate without it commits the docs); merging outside the pipeline skips the strip; and a stripped PR's body links paths that stop existing after merge.

- [ ] **Step 1: Add the section to `plugins/dev-flow/README.md`**

Find this line (the last line of the `## Stops` section):

```
`adversarial-review` is internal machinery but can also be invoked standalone
on any existing design/plan/PR.
```

Insert the following **after** it and **before** the `## How to smoke-test` heading. Wrap prose at ~72 columns to match the file:

````
## Design and plan docs: commit or strip

By default, dev-flow commits its design doc
(`docs/superpowers/specs/…-design.md`) and its plan
(`docs/superpowers/plans/…-plan.md`) on the feature branch, and the squash
merge carries both into your default branch. If your repo deliberately keeps
that scaffolding out of `main`, say so once per checkout in
`.claude/dev-flow.local.md`:

```yaml
---
docs: strip      # commit | strip
---
```

Under `docs: strip` the docs are still written, reviewed, and committed on the
feature branch — the PR shows them, and a `pre-merge` stop leaves them in place
for you to read — but the merge gate removes them in a final commit just before
merging, so nothing under `docs/superpowers/` reaches your default branch. The
removal is scoped to paths **this branch added**: a doc that already existed
when the branch was created is never touched, even if its filename matches.

An absent file, `docs: commit`, or an unrecognized value all resolve to
`commit`, so a checkout with no settings file behaves exactly as it did
before (the unrecognized case also prints a one-line warning naming the bad
value, so a typo'd `strip` doesn't silently commit your docs).

The same file and the same key serve both `dev-flow` and `dev-flow-worktree`:
the question is about your repo's default branch, so it has one answer per
repo, not one per plugin. dev-flow adds `.claude/dev-flow.local.md` to your
repository's local `info/exclude` at every stage boundary, so it never shows
up in a PR diff — even if you create it mid-run.

Three consequences worth knowing:

- **The policy is per-developer, not per-team.** The settings file is
  git-ignored by definition, so a teammate without it commits the docs. On a
  multi-committer repo the docs tree can become a mix of stripped and
  committed scaffolding with no signal distinguishing policy from accident.
- **Merging outside the pipeline skips the strip.** If you take a `pre-merge`
  stop and then merge in the GitHub UI, the docs land in your default branch.
  The pipeline cannot prevent that.
- **A stripped PR's body links paths that stop existing after merge.** Under
  `docs: strip` the PR body says so: the docs live in the PR's own commit
  history.
````

- [ ] **Step 2: Add a smoke-test step to `plugins/dev-flow/README.md`**

Find the last numbered item of `## How to smoke-test`:

```
2. Resume with `continue dev-flow on <slug>` and confirm it proceeds through
   plan and execute on the same slug.
```

Insert the following **after** it:

```
3. Write `.claude/dev-flow.local.md` with `docs: strip` and run dev-flow
   full-auto on a small change in a repo that already has an unrelated doc
   under `docs/superpowers/specs/`. Confirm the merged commit contains no
   `docs/superpowers/` paths, the pre-existing doc is still on the default
   branch, and `.claude/dev-flow.local.md` never appeared in the PR diff.
   Then delete the settings file and re-run: the docs should be committed and
   reach the default branch as before.
```

- [ ] **Step 3: Add the mirrored section and smoke-test step to `plugins/dev-flow-worktree/README.md`**

Apply Steps 1 and 2 to `plugins/dev-flow-worktree/README.md`, anchored on the same two lines (both files carry the identical `adversarial-review` closing sentence, and the worktree file's step 2 reads `continue dev-flow-worktree on <slug>`). Substitutions:

- `dev-flow` (the plugin's name, in prose) → `dev-flow-worktree` — **except** in the sentence naming both plugins, which stays `both \`dev-flow\` and \`dev-flow-worktree\``.
- `.claude/dev-flow.local.md` → **unchanged**, everywhere. Add this sentence right after the "one answer per repo, not one per plugin" sentence: `The file keeps the family name \`dev-flow\` for that reason, even here.`
- In Step 2's smoke-test text, `run dev-flow full-auto` → `run dev-flow-worktree full-auto`, and append this final sentence: `Confirm the same run from the linked worktree — the exclude and every git command the merge gate runs must work from there, not just from the main checkout.`

- [ ] **Step 4: Verify both READMEs**

Run:

```bash
cd /Users/taylor/dev/claude-plugins
for f in plugins/dev-flow/README.md plugins/dev-flow-worktree/README.md; do
  echo "== $f"
  grep -n -F -e '## Stops' -e 'on any existing design/plan/PR.' -e '## Design and plan docs: commit or strip' -e '## How to smoke-test' "$f"
  grep -n -F -e '.claude/dev-flow.local.md' "$f"
  grep -c -F -e 'dev-flow-worktree.local.md' "$f"
  grep -c -F -e 'docs: strip      # commit | strip' "$f"
  grep -c -F -e 'The policy is per-developer, not per-team.' "$f"
  grep -c -F -e 'Merging outside the pipeline skips the strip.' "$f"
  grep -c -F -e 'stripped PR' "$f"
  grep -c -E '^3\. Write `.claude/dev-flow.local.md`' "$f"
done
```

Expected for **each** file: the first `grep -n` prints four numbered lines **in this order** — `## Stops`, the `adversarial-review` closing sentence, the new `## Design and plan docs` heading, `## How to smoke-test` — proving the section landed between the end of Stops and the smoke-test heading. The second `grep -n` prints exactly **four** settings-path lines (the yaml-intro sentence, the `info/exclude` sentence, and smoke-test step 3 across two lines). Then `0`, `1`, `1`, `1`, `1`, `1`.

Note: the settings path is listed by line, not counted. A whole-file total here is `4`, not `3` — the value the arithmetic-based form of this check originally asserted, which would have failed on a correctly executed task (Global Constraints, *Verification-command form*).

- [ ] **Step 5: Verify line width**

Run:

```bash
cd /Users/taylor/dev/claude-plugins
git diff -- plugins/dev-flow/README.md plugins/dev-flow-worktree/README.md | grep -E '^\+[^+]' | awk 'length > 80 {print}'
```

Expected: no output. This checks only the lines this task **added** (the `+` prefix costs one column, so a threshold of 80 permits 79 content columns — Step 1's block deliberately carries two 79-column lines). A whole-file check would flag a pre-existing 81-column line in `plugins/dev-flow-worktree/README.md` that is not ours to touch. If any line is reported, re-wrap it at ~72 columns.

- [ ] **Step 6: Commit**

```bash
cd /Users/taylor/dev/claude-plugins
git add plugins/dev-flow/README.md plugins/dev-flow-worktree/README.md
git commit -m "dev-flow: document the docs commit/strip setting in both READMEs"
```

---

### Task 11: Parity sweep and version bumps

**Files:**
- Modify: `plugins/dev-flow/.claude-plugin/plugin.json` (`"version": "2.1.0"` → `"2.2.0"`)
- Modify: `plugins/dev-flow-worktree/.claude-plugin/plugin.json` (`"version": "1.3.0"` → `"1.4.0"`)
- Verify (no edit): both SKILL.md files, both README.md files
- Test: none (verify by grep/diff/`python3 -c`)

**Interfaces:**
- Consumes: everything Tasks 1–10 wrote.
- Produces: the release. The plugin cache is **version-keyed**, so a re-sync will not pick up any of this work at an unchanged version — the bumps are required, not cosmetic.

**Context:** Nothing mechanically enforces that the two variants stay identical (drift control is tracked in issue #8). This task is the manual stand-in: a mechanical sweep that the mirrored prose is the same modulo naming, run **before** the bumps so a drifted pair is never released.

- [ ] **Step 1: Sweep for cross-contaminated names**

Run:

```bash
cd /Users/taylor/dev/claude-plugins
echo "== worktree names inside the dev-flow plugin's skill (expect exactly the 2 pre-existing sibling references)"
grep -rn -F 'dev-flow-worktree' plugins/dev-flow/skills/
echo "== the per-variant settings filename must not exist anywhere"
grep -rn -F 'dev-flow-worktree.local.md' plugins/ || echo NONE
echo "== the unsuffixed trailer must not appear in the worktree plugin"
grep -rn -F 'dev-flow-stripped' plugins/dev-flow-worktree/ || echo NONE
echo "== the worktree trailer must not appear in the dev-flow plugin"
grep -rn -F 'dev-flow-worktree-stripped' plugins/dev-flow/ || echo NONE
```

Expected: the last three each print `NONE`. The first prints exactly **two** lines, both pre-existing: the Branch-ownership bullet's "a feature of the sibling `dev-flow-worktree` plugin", and Environment Assumptions' "use the `dev-flow-worktree` plugin instead". More than two means an edit from this change leaked the wrong variant's name into the wrong file.

- [ ] **Step 2: Sweep that every new element exists in both SKILL.md files**

Run:

```bash
cd /Users/taylor/dev/claude-plugins
A=plugins/dev-flow/skills/dev-flow/SKILL.md
B=plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
for s in \
  '- **Command discipline:**' \
  '**Docs policy — commit or strip the scaffolding.**' \
  '*Qualifying paths — what a strip may remove.*' \
  '*The stripped state, defined once.*' \
  '**Marker validity.**' \
  '0. **Ensure ' \
  '- **Docs policy (intake):**' \
  '- **Under `docs: strip`**' \
  'The merge gate is five steps and is **re-entrant**' \
  ; do
  printf '%-55s A=%s B=%s\n' "$s" "$(grep -c -F -e "$s" $A)" "$(grep -c -F -e "$s" $B)"
done
```

Expected: every row shows `A=1 B=1`.

- [ ] **Step 3: Confirm the two files' new prose matches modulo naming**

Run:

```bash
cd /Users/taylor/dev/claude-plugins
A=plugins/dev-flow/skills/dev-flow/SKILL.md
B=plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
base=$(git merge-base main HEAD)   # failure or empty halts (Command discipline)
normit(){ sed -e 's/dev-flow-worktree/dev-flow/g' -e 's/[Ww]orktree entry/branch entry/g'; }
diff <(diff <(git show "$base:$A") <(git show "$base:$B" | normit) | grep '^[<>]') \
     <(diff "$A" <(normit < "$B") | grep '^[<>]')
```

This compares the two files' *divergence after* the change against their divergence *before* it, so every pre-existing structural difference cancels — the surviving delta is exclusively this change's responsibility. (The token substitution `dev-flow-worktree`→`dev-flow` already normalizes five of the seven Global Constraints substitution rows, since all five contain the token.)

Every line of the delta must belong to one of exactly five items:

1. the Branch-ownership bullet pair — a pre-existing divergent line that both files extended identically-modulo-naming (Task 5);
2. entry step 0 — one pattern (dev-flow) vs the two-pattern `for` loop (worktree), plus adjacent lines that `diff` re-pairs around the insertion;
3. worktree entry steps 3 and 4, which have no dev-flow counterpart;
4. the merge gate's opening paragraph — the worktree's extra addressing sentence;
5. merge-gate step 5 — each file's pre-existing merge wording.

Anything else is drift introduced by this change — fix it before continuing.

Why the before/after form: a plain whole-file normalized diff emits ~130 lines across ~26 hunks, of which ~113 pre-date this change, and asks the reader to decide "pre-existing, or drift I just introduced?" — which is not mechanically decidable from that output. The delta form reduces it to ~43 lines, all falling inside the five enumerated items.

- [ ] **Step 4: Bump `plugins/dev-flow/.claude-plugin/plugin.json`**

Change the version line from:

```json
  "version": "2.1.0",
```

to:

```json
  "version": "2.2.0",
```

Leave `name` and `description` untouched.

- [ ] **Step 5: Bump `plugins/dev-flow-worktree/.claude-plugin/plugin.json`**

Change the version line from:

```json
  "version": "1.3.0",
```

to:

```json
  "version": "1.4.0",
```

Leave `name` and `description` untouched.

- [ ] **Step 6: Verify both manifests are valid JSON with the right versions**

Run:

```bash
cd /Users/taylor/dev/claude-plugins
python3 -c "
import json
for p, want in [('plugins/dev-flow/.claude-plugin/plugin.json','2.2.0'),
                ('plugins/dev-flow-worktree/.claude-plugin/plugin.json','1.4.0')]:
    d = json.load(open(p))
    assert d['version'] == want, (p, d['version'], want)
    print(p, d['name'], d['version'], 'OK')
"
```

Expected: two `OK` lines, no assertion error.

- [ ] **Step 7: Confirm the whole change touches only the six intended files**

Run:

```bash
cd /Users/taylor/dev/claude-plugins
git diff --name-only main...HEAD -- plugins/
```

Expected exactly these six paths, and nothing else under `plugins/`:

```
plugins/dev-flow-worktree/.claude-plugin/plugin.json
plugins/dev-flow-worktree/README.md
plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
plugins/dev-flow/.claude-plugin/plugin.json
plugins/dev-flow/README.md
plugins/dev-flow/skills/dev-flow/SKILL.md
```

(The branch will also contain `docs/superpowers/specs/` and `docs/superpowers/plans/` paths — this plan and its design doc. Those are expected; the `-- plugins/` filter excludes them.)

- [ ] **Step 8: Commit**

```bash
cd /Users/taylor/dev/claude-plugins
git add plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
git commit -m "dev-flow: bump to 2.2.0 and dev-flow-worktree to 1.4.0 for the docs policy"
```

---

## Acceptance criteria → coverage

The design's acceptance criteria are behavioral and can only be exercised by running the pipeline (see the design's Smoke test, which is a post-merge activity in a scratch repo). Within this repo, each criterion is *specified* by these tasks:

| Criterion | Specified by |
|---|---|
| 1. `docs: strip` merges a PR whose net diff has no `docs/superpowers/` paths | Tasks 2, 3, 9 |
| 2. Previously shipped docs on the default branch are untouched | Task 3 (gate 3, merge-base) |
| 3. No settings file / `docs: commit` behaves exactly as today | Tasks 2 (default), 9 (step 4 evaluates gates, reads `commit`, removes nothing), 6 (validity clause unsatisfiable without trailer commits) |
| 4. Interrupt anywhere between strip commit and merge, then resume, completes | Tasks 5 (ownership + resume row), 6 (marker validity), 9 (step 1's leading push; re-entry) |
| 5. `pre-merge` stop under `strip` leaves both docs at tip | Task 9 (step 3 precedes step 4) |
| 6. `.claude/dev-flow.local.md` never appears in a PR diff, including created mid-run | Task 4 (entry step 0 at every boundary) |
| 7. Every added command works from a linked worktree | Tasks 1 (item 1–2), 4 (`--git-path`, entry step 4's enumeration) |
