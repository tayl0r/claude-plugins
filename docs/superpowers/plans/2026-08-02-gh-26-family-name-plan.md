---
dev-flow:
  slug: gh-26-family-name
  spec: docs/superpowers/specs/2026-07-31-gh-26-family-name-design.md
---

# gh-26: `family name` for the plugin pair is the same relation, one domain over — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace one line of `CONTEXT.md` — the **Family** definition — so the glossary names the plugin domain as a second instance of the relation it already defines, binding issue #26's ruling of **no finding** where the shipped checks actually read it. Nothing else in the repo changes.

**Architecture:** A single in-place line replacement in one un-mirrored, un-cached Markdown file. `CONTEXT.md` goes from 67 lines to **67 lines** — a replacement, not an append. No plugin file, no manifest, no version, and none of the three `family` sites named in #26 is touched; the design's whole ruling is that those stay as they are, and Steps 7–13 assert it against the base commit.

**Tech Stack:** Markdown. `python3` (stdlib only), `git grep`, `git diff`, `grep`, `python3 scripts/check-sync.py`, `claude plugin validate .`. **There is no build, no linter, and no test framework in this repo — do not run `pytest`, `npm test`, or `ruff`, and do not add one.**

**Authoritative source:** `docs/superpowers/specs/2026-07-31-gh-26-family-name-design.md`. Its `§Exact change list` holds the replacement text and its `§Verification` holds all nine checks folded in below. **If this plan and the design ever disagree, the design wins — stop, re-read `§Exact change list`, and report.**

---

## Global Constraints

Every task's requirements implicitly include this section.

- **Repo root:** `/Users/taylor/dev/claude-plugins`. Every relative path below is relative to it, and every command below is run from it. Work in place on the existing branch `tayl0r/gh-26-family-name` (base commit `0c05098`) — **do not create a git worktree, do not switch branches, do not commit, do not push, do not open a PR, do not merge, do not invoke a review skill.** The pipeline owns every one of those.
- **NEVER RETYPE THE REPLACEMENT TEXT.** The design gives it as the one plain fenced block in `§Exact change list`. The applier in Task 1 parses that block out of the design file **on disk** and writes it into `CONTEXT.md`. Do **not** transcribe it by hand, do **not** paste it from a chat message, do **not** use `Edit` with a retyped `new_string`. The line contains a U+2026 ellipsis (`…`) and a U+2014 em dash (`—`) — precisely the characters a retype gets wrong. `CLAUDE.md` requires this design-conformance check for exactly this reason, and here it is the *only* thing standing between the design and a paraphrase: `scripts/check-sync.py` never reads `CONTEXT.md`, and no mirror pair is involved.
- **Scope is exactly one file: `CONTEXT.md`.** Nothing else may appear in the final diff beyond this run's own `docs/superpowers/` design and plan artifacts. Do **not** touch anything under `plugins/`, `.claude-plugin/marketplace.json`, `CLAUDE.md`, `docs/adr/`, `docs/agents/`, `scripts/`, `.github/`, or either `README.md`.
- **Do not edit the three `family` sites named in #26.** `plugins/dev-flow/skills/dev-flow/SKILL.md`, `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`, and `plugins/dev-flow-worktree/README.md:89` are **correct as shipped** — that is the design's ruling. Leaving them alone is the deliverable, not an omission.
- **No version bump.** `dev-flow` stays `2.6.0` and `dev-flow-worktree` stays `1.8.0`. `CONTEXT.md` lives outside `plugins/`, so it enters no version-keyed cache and `CLAUDE.md`'s bump rule does not apply. This is asserted in Step 10 because the reflex is to bump.
- **`CONTEXT.md` is edited on exactly one line — the **Family** definition.** **Family match**, **Tier**, and every other line stay byte-identical on purpose. Do not "also fix" them. Do not add an `_Avoid_:` line to **Family**, and do not add a second entry (e.g. **Plugin family**); the design rejects both explicitly.
- **The design doc is read-only reference material.** `docs/superpowers/specs/2026-07-31-gh-26-family-name-design.md` is never edited — every script here only *reads* it. Editing it would silently change what the conformance check compares against.
- **Every inline `python3` script below is pure ASCII on purpose**, including its anchor strings, so a mistyped copy fails loudly instead of passing. The *content* it moves is not ASCII — but you never type that content, the script copies it. **Copy each script exactly, character for character. The heredoc fences are unindented on purpose: a `python3` heredoc indented under a list item is an `IndentationError`.**
- **`claude plugin validate .` emits 8 missing-author warnings and exits 0. That is expected and is NOT a failure.** Only a non-zero exit or an explicit error is a failure.
- **Line numbers in this plan and in the design are informational, never inputs.** Every script locates its target by exact content match and asserts the match is unique. If a script prints a line number different from the one predicted here, note it in your report and keep going; the conformance script is the authority.
- **The applier is idempotent.** Re-running it after it has landed prints `already applied: Family definition, in CONTEXT.md` and changes nothing. A task re-dispatched after a partial run is safe to run from Step 1.
- **`git diff` here compares the working tree against a commit**, so every assertion below works on uncommitted edits. You never need to commit to verify.

---

## File map

| File | Responsibility in this change | Lines | Task |
|---|---|---|---|
| `CONTEXT.md` | The sole plain-fenced design block replaces the **Family** definition line (pre-change line 21), directly under the `**Family**:` anchor. One line replaced, none added. | 67 → **67** | 1 |

No file is created, renamed, or deleted. No other file is modified.

## Design block map

The design's `§Exact change list` holds **exactly one** plain-fenced block (no info string). Every script below asserts that shape before using it, so the shape is the contract:

| Block | Design heading | Shape | Target | Anchor (ASCII, exact match) |
|---|---|---|---|---|
| 0 | `### 1. CONTEXT.md — line 21, the definition line under **Family**:` | 1 line, replace | `CONTEXT.md` | `**Family**:` (block goes on the line *directly after* it) |

Every other fence in the design carries an info string (`text`, `sh`), which is what keeps this index stable. **Keep it that way.**

### The replacement line — reference copy, NOT the source

Shown so you can eyeball the result. **It is not what you apply** — the applier reads the design on disk. If this copy and the design ever differ, the design wins, and Step 5's byte-exact check will catch a hand-typed copy.

```text
A model's product line (Opus, Sonnet, Fable), independent of any dated version within it. A plugin's product line likewise: `dev-flow` is the family name its two variants share, independent of either variant's own version. A set of merely related constructs (connectors, handlers, jobs…) is not a family — the word for that is *kind*.
```

The line it replaces, in full:

```text
A model's product line (Opus, Sonnet, Fable), independent of any dated version within it.
```

Three properties are deliberate and load-bearing: the **model sentence stays first and byte-identical** (so **Family match** and **Tier** resolve exactly as before), the plugin sentence uses **`variant`** for the member (a word shipped prose already uses), and the closing **exclusion sentence** points at `kind` so the entry cannot re-admit the sense commit `0c05098` removed.

## Task ordering

**One task, strict order.** Steps 1–6 apply the edit; Steps 7–13 gate the whole change against the base commit; Step 14 reports. Steps 7–13 assert properties of the applied working tree and fail on every content check if Steps 1–6 have not run. No prerequisites beyond a clean checkout of the branch.

---

### Task 1: Replace the `CONTEXT.md` **Family** definition, then gate the whole change

**Files:**
- Modify: `/Users/taylor/dev/claude-plugins/CONTEXT.md` (the definition line under `**Family**:`, pre-change line 21)
- Read-only: `/Users/taylor/dev/claude-plugins/docs/superpowers/specs/2026-07-31-gh-26-family-name-design.md`, and the whole working tree for Steps 7–13
- Test: none — this repo has no test framework. The design-conformance script (written out at Step 2, re-run at Step 5) is the test.

**Interfaces:**
- Consumes: nothing from an earlier task.
- Produces: a `CONTEXT.md` that is 67 lines long and whose line directly after `**Family**:` is byte-identical to the design's sole plain-fenced block. Steps 7–13 depend on exactly that.

- [x] **Step 1: Read the design's change list, and read the target region**

Read `/Users/taylor/dev/claude-plugins/docs/superpowers/specs/2026-07-31-gh-26-family-name-design.md` §`Exact change list` (the section headed `## Exact change list`) and confirm it contains one plain fenced block — a fence line that is exactly three backticks with nothing after it. Then look at the target:

```sh
sed -n '18,24p' CONTEXT.md
wc -l CONTEXT.md
```

Expected: line 20 is `**Family**:`, line 21 is `A model's product line (Opus, Sonnet, Fable), independent of any dated version within it.`, and `67 CONTEXT.md`.

- [x] **Step 2: Run the design-conformance check and watch it FAIL (red)**

This is the design's Verification step 4, run before the edit so you can see it discriminate. **The fence below is unindented on purpose** — an indented `python3` heredoc is an `IndentationError`. Copy it character for character.

```sh
python3 - <<'PY'
import sys
from pathlib import Path
DESIGN = "docs/superpowers/specs/2026-07-31-gh-26-family-name-design.md"
TARGET = "CONTEXT.md"
ANCHOR = "**Family**:"
OLD = "A model's product line (Opus, Sonnet, Fable), independent of any dated version within it."
FENCE = chr(96) * 3
blocks, cur, mode = [], None, None
for line in Path(DESIGN).read_text(encoding="utf-8").split("\n"):
    s = line.strip()
    if mode is None:
        if s.startswith(FENCE):
            mode, cur = s[3:], []
    elif s == FENCE:
        if mode == "":
            blocks.append(cur)
        mode, cur = None, None
    else:
        cur.append(line)
assert [len(b) for b in blocks] == [1], "design plain-fence shape changed; stop and re-read the design"
want = blocks[0]
lines = Path(TARGET).read_text(encoding="utf-8").split("\n")
if lines and lines[-1] == "":
    lines.pop()
bad = []
if len(lines) != 67:
    bad.append("%s is %d lines, want 67" % (TARGET, len(lines)))
at = [i for i in range(len(lines) - len(want) + 1) if lines[i:i + len(want)] == want]
if len(at) != 1:
    bad.append("Family definition found %d times, want exactly 1" % len(at))
elif lines[at[0] - 1] != ANCHOR:
    bad.append("sits after %r, want %r" % (lines[at[0] - 1][:40], ANCHOR))
if OLD in lines:
    bad.append("the pre-change one-sentence Family line survives as a whole line")
if not want or not want[0].startswith(OLD):
    bad.append("the replacement no longer opens with the model sentence Family match depends on")
for why in bad:
    print("MISMATCH:", why)
print("design-conformance:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected, exactly:

```text
MISMATCH: Family definition found 0 times, want exactly 1
MISMATCH: the pre-change one-sentence Family line survives as a whole line
design-conformance: FAIL
exit=1
```

If instead you see `design-conformance: OK`, the edit is already applied — skip to Step 5. If the `assert` on the fence shape trips (`design plain-fence shape changed`), **stop and report**: the design has been edited and this plan's block index is stale.

- [x] **Step 3: Apply the replacement with the applier script**

Reads block 0 from the design on disk and writes it into `CONTEXT.md`, matching the old line by content and requiring the `**Family**:` anchor immediately above it. Idempotent. **Unindented fence, pure ASCII — copy exactly.**

```sh
python3 - <<'PY'
import sys
from pathlib import Path
DESIGN = "docs/superpowers/specs/2026-07-31-gh-26-family-name-design.md"
TARGET = "CONTEXT.md"
ANCHOR = "**Family**:"
OLD = "A model's product line (Opus, Sonnet, Fable), independent of any dated version within it."
FENCE = chr(96) * 3
blocks, cur, mode = [], None, None
for line in Path(DESIGN).read_text(encoding="utf-8").split("\n"):
    s = line.strip()
    if mode is None:
        if s.startswith(FENCE):
            mode, cur = s[3:], []
    elif s == FENCE:
        if mode == "":
            blocks.append(cur)
        mode, cur = None, None
    else:
        cur.append(line)
assert [len(b) for b in blocks] == [1], "design plain-fence shape changed; stop and re-read the design"
want = blocks[0]
assert want[0].startswith(OLD), "design block no longer opens with the model sentence"
lines = Path(TARGET).read_text(encoding="utf-8").split("\n")
if want[0] in lines:
    print("already applied: Family definition, in " + TARGET)
    sys.exit(0)
at = [i for i, l in enumerate(lines) if l == OLD]
assert len(at) == 1, "expected exactly 1 pre-change Family line, found %d" % len(at)
i = at[0]
assert i > 0 and lines[i - 1] == ANCHOR, "line %d not preceded by %r" % (i + 1, ANCHOR)
lines[i:i + 1] = want
Path(TARGET).write_text("\n".join(lines), encoding="utf-8")
print("applied: Family definition, at line %d of %s" % (i + 1, TARGET))
PY
echo "exit=$?"
```

Expected: `applied: Family definition, at line 21 of CONTEXT.md` and `exit=0` (or the `already applied:` line if re-run). Any `AssertionError` is a **stop and report**.

- [x] **Step 4: Residue check — the pre-change one-sentence form is gone as a whole line**

This is the design's Verification step 3. This edit deletes no text (it extends a line), so the usual removed-phrase grep degenerates to one assertion: the old form must no longer occur as a *complete* line. `git grep` has no `-x`, so this is deliberately a plain `grep`.

```sh
grep -x -F "A model's product line (Opus, Sonnet, Fable), independent of any dated version within it." CONTEXT.md; echo "exit=$?"
```

Expected: **no output**, then `exit=1`. (`exit=1` is the pass here — `grep` exits 1 on no match.) One file, one exact-line match, no ordering — this behaves identically under a plain `grep` and under an aliased one. Step 5's script re-asserts the same thing from Python; the two are independent implementations of one assertion, and if they ever disagree, **stop and report** rather than picking a winner.

- [x] **Step 5: Run the design-conformance check and watch it PASS (green)**

Re-run **the exact script from Step 2 above** — same characters, no edits; re-read this task's text if you need it. It is deliberately not duplicated here: one copy is the check, two copies are two things to keep in step. It re-reads the replacement from the design on disk and demands a byte-for-byte line match in `CONTEXT.md` directly after the `**Family**:` anchor. The anchor matters on its own: the same line pasted under **Family match** or **Tier** would satisfy a bare containment check and be wrong. The final branch is the one protecting **Family match** — it fails if the model sentence is no longer first.

Expected, exactly:

```text
design-conformance: OK
exit=0
```

Any `MISMATCH:` line is a **stop and report** — do not hand-patch `CONTEXT.md` to satisfy it. Re-run Step 3 instead.

- [x] **Step 6: Confirm the edit is a one-line replacement, not an append**

```sh
wc -l CONTEXT.md
git diff --numstat 0c05098 -- CONTEXT.md
git diff 0c05098 -- CONTEXT.md
```

Expected: `67 CONTEXT.md`; then `1	1	CONTEXT.md` (one insertion, one deletion — that *is* what a single-line replacement means); then a diff with exactly one `-` line (the old **Family** definition) and one `+` line (the new one), and no other hunk.

**Steps 7–13 make no edits; their deliverable is the recorded evidence that the ruling of "no finding" shipped without collateral. If any check here fails, stop and report — do not repair by editing the files the check names.**

- [x] **Step 7: Exactly one source file changed, and it is not a plugin file** (design Verification step 1)

```sh
git diff --stat 0c05098 -- . ':!docs/superpowers/'
git diff --quiet 0c05098 -- plugins/ .claude-plugin/ && echo "plugins/ untouched: OK"
```

Expected from the first command: one row, ` CONTEXT.md | 2 +-`, and the summary ` 1 file changed, 1 insertion(+), 1 deletion(-)`. Expected from the second: `plugins/ untouched: OK`.

The `':!docs/superpowers/'` pathspec is the design's own, verbatim: the design's front-matter sets `docs: commit`, so this run's design doc is *already* committed on this branch (`8d7c242`, `67315fe`) and this plan doc joins it. Without the exclusion the diff necessarily reports them. An untracked plan file does not appear in `--stat` at all, which is not a failure. Any path outside `CONTEXT.md` and `docs/superpowers/` **is** a failure.

The second command is the strongest form of the check `CLAUDE.md` requires for a hand-mirrored pair: rather than proving a mirrored edit landed on both sides, it proves **neither side was touched**, measured against the base commit rather than against the pair's other half. Note `git diff --quiet` exits 1 when differences exist, so a missing `plugins/ untouched: OK` line is the failure signal.

- [x] **Step 8: The three sites named in #26 read exactly as they did** (design Verification step 2)

```sh
git grep -c -F '(`dev-flow` is the family name they share)' -- plugins/
git grep -n -F 'The file keeps the family name `dev-flow` for that' -- plugins/dev-flow-worktree/README.md
```

Expected from the first: two rows, each ending `:1` —

```text
plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md:1
plugins/dev-flow/skills/dev-flow/SKILL.md:1
```

Expected from the second: one hit, `plugins/dev-flow-worktree/README.md:89:repo, not one per plugin. The file keeps the family name `dev-flow` for that`.

These three sites staying untouched **is the ruling**. A missing or altered hit means someone "fixed" prose the design found correct.

- [x] **Step 9: Commit `0c05098`'s repair is not silently undone** (design Verification step 5)

The widened entry must not re-admit the grab-bag sense that commit removed.

```sh
git grep -n -i 'known family' -- . ':!docs/superpowers/'; echo "exit=$?"
```

Expected: **no output**, then `exit=1`. The pathspec is required — the design quotes that string, and so does nothing else in shipped text.

- [x] **Step 10: Versions did not move** (design Verification step 6)

```sh
git grep '"version"' -- plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
```

Expected, exactly:

```text
plugins/dev-flow-worktree/.claude-plugin/plugin.json:  "version": "1.8.0",
plugins/dev-flow/.claude-plugin/plugin.json:  "version": "2.6.0",
```

`git grep` rather than `grep -h`, because the assertion is *which plugin is at which version* and `-h` strips exactly the labels that carry it: under Claude Code's Bash tool bare `grep` is a ugrep-backed shell function whose multi-file output order is not stable between runs, so with `-h` the two values become indistinguishable. `git grep` labels each hit and sorts by path, so this output is deterministic. `CONTEXT.md` ships into no version-keyed plugin cache, so `CLAUDE.md`'s bump rule does not apply here. **If you bumped either version, revert the bump.**

- [x] **Step 11: `check-sync.py` passes, unchanged** (design Verification step 7)

```sh
python3 scripts/check-sync.py; echo "exit=$?"
```

Expected, exactly:

```text
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)
check-sync: all checks passed
exit=0
```

Unchanged from before this task, since no file it reads is touched — it never reads `CONTEXT.md`, and `.claude-plugin/marketplace.json` carries no `description` change.

- [x] **Step 12: `claude plugin validate .` passes** (design Verification step 8)

```sh
claude plugin validate .; echo "exit=$?"
```

Expected: `✔ Validation passed with warnings`, `exit=0`, and **8** `No author information provided` warnings. **Those 8 warnings are expected and are not a failure.** A non-zero exit, an error, or a warning count other than 8 is a failure.

- [x] **Step 13: Record the behavioural observation for #23 — take no action** (design Verification step 9)

**Do not invoke `adversarial-review` or any other review skill.** The pipeline runs its own reviews and owns that stage. Your job is only to carry this note into your report so it can be recorded on issue #23:

> The installed `dev-flow` is already `2.6.0` at `gitCommitSha 0c050989`, so this change's own reviews exercise the glossary-conformance angle and the drift clause. Correct outcomes: **no finding** on `family` in `design` and `plan` mode on this run's artifacts, and **no finding** in `diff` mode on this branch — the one added shipped line is `CONTEXT.md`'s own **Family** entry, which by construction names what its entry defines. A finding that quotes **Family**'s model sentence against this change's plugin use is evidence the *"in the sense the repo already has"* exclusion is too weak, which is the false positive this change exists to foreclose. Record the outcome on #23; **do not change the design because of it.**

- [x] **Step 14: Report, do not commit**

Report each of Steps 1–13 as pass or fail with the actual output you saw. Leave the edit in the working tree. **Do not run `git commit`, `git push`, `gh pr create`, or any review skill** — the pipeline owns all of them.
