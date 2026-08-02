---
dev-flow:
  slug: gh-28-29-review-prose
  spec: docs/superpowers/specs/2026-08-02-gh-28-29-review-prose-design.md
---

# gh-28 / gh-29 review-prose normalization — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename the second review tier to `resolver` on the three lines of `adversarial-review/SKILL.md` that still name it with a `group`-qualified name, identically in both mirror copies, and bump both plugin versions.

**Architecture:** Three prose lines change in each of two byte-identical mirror copies; no line is added or removed and each file stays 89 lines. The edit is applied as six exact-string replacements over the three short spans that actually change (design **A1**: selected by **text**, never by line number, halting if the text is absent or not unique), so no byte of the surrounding prose is ever transcribed. The result is then proved independently against the design on disk: criterion 6 asserts the design's three fenced blocks landed verbatim at 52/71/81 in both copies, and criterion 8(b) asserts no other line moved. Issue #29 ships nothing; criterion 8(b) enforces that mechanically.

**Tech Stack:** Markdown, JSON, Python 3 stdlib, `git`, `claude` CLI. There is no build and no test framework (design **A6**) — the design's eight success criteria are the entire verification surface.

## Global Constraints

Every task's requirements implicitly include this section.

- **Working directory (absolute, always):** `/Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b`. Branch `tayl0r/gh-28-29-review-prose`. Address git as `git -C <that path>`; never rely on inherited cwd.
- **Authorized file set — nothing else may be created, modified, or deleted:**
  - `plugins/dev-flow/skills/adversarial-review/SKILL.md`
  - `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md`
  - the `"version"` field of `plugins/dev-flow/.claude-plugin/plugin.json`
  - the `"version"` field of `plugins/dev-flow-worktree/.claude-plugin/plugin.json`
  - `docs/superpowers/plans/2026-08-02-gh-28-29-review-prose-plan.md` (this file — checkbox ticks only)
- **Explicitly forbidden — touching any of these is a HALT, not a judgment call:** `CLAUDE.md`, `CONTEXT.md`, anything under `scripts/` (including `check-sync.py` — a concurrent agent owns that file), `docs/adr/`, `docs/agents/`, `.claude-plugin/marketplace.json`, either `README.md`, either pipeline `SKILL.md`, and **every pre-existing file under `docs/superpowers/`** — meaning the *prior records*: every `docs/superpowers/` file other than this change's own design doc and this plan. Those two are already committed by the time Task 1 starts, and they are governed by the two bullets above rather than by this one — the design is read-only, this plan takes checkbox ticks only.
- **The design doc is read-only input.** `docs/superpowers/specs/2026-08-02-gh-28-29-review-prose-design.md` must end this work byte-identical to how it started. Its three fenced blocks in *The edit* must not be modified. Expected blob hash, unchanged throughout: `3f0b75ab7e602ee78ffbe77dcf4fa2b4de7ee1bf` (`git -C <root> hash-object <design path>`). If it differs at Task 1 Step 1, **halt and report** — do not proceed and do not "fix" the design.
- **Never retype the replacement text.** Per `CLAUDE.md`, any change to this mirrored pair whose design doc gives replacement text as fenced blocks must add a check that **re-reads those blocks from the design on disk, never retyped**, asserting each appears verbatim in its target. That mandate is on the *check*: Task 1 Step 4 and Task 3 Step 4 are it. The edit itself satisfies the same property structurally rather than by citation — Step 3 replaces only the three short spans that change, so no byte of lines 52, 71 or 81 outside those spans is ever transcribed. Do not paste a whole line 52/71/81 into a shell command, an `Edit` call, or a commit message; the only literals typed anywhere are the three fragments in Step 3's table, each quoted from the design.
- **Nothing ships for issue #29.** Its ruling is NO CHANGE. `SKILL.md:42` and `:48` must be unchanged in both copies. This is not left to restraint — criterion 8(b) asserts the changed-line set is exactly `{52, 71, 81}`.
- **Never stage with `git add -A`, `git add .`, or `git commit -a`.** Every commit stages the exact paths named in its step.
- **Never match `--stat` output literally.** Where a step gives an expected `git … --stat` result it states the per-file insertion/deletion counts in prose, and git's rendering deliberately does not echo those numbers back: `--stat`'s leading integer is insertions *plus* deletions (3 + 3 renders `6 +++---`), the integer's column and the `+/-` graph scale with terminal width, and long paths are elided to `.../<tail>`. Compare the file *set* and the counts; never the bar. A step that needs a literal, byte-comparable expected block uses `--name-only` instead.
- **`claude plugin validate .` exiting 0 with exactly 8 `No author information provided` warnings is a PASS** (design **A4**, `CLAUDE.md`). Warnings are not failures. Do not add author fields to silence them.
- **No new files anywhere, including temp files inside the repo.** Every Python snippet below is run as a heredoc piped to `python3 -`, so nothing is written to disk.
- **`BASE` is always computed, never hardcoded:** `BASE=$(git -C <root> merge-base origin/main HEAD)`. It resolves to `c8b2182a4fa140d53d2162486ef725ce79e82739` today, but merge-base stays correct if `main` advances or the branch is rebased.

---

## File Structure

| Path (repo-relative) | Change |
|---|---|
| `plugins/dev-flow/skills/adversarial-review/SKILL.md` | Lines 52, 71, 81 replaced. Still 89 lines. |
| `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md` | Same three lines, same replacement bytes (the two copies are byte-identical on these lines today). Still 89 lines. |
| `plugins/dev-flow/.claude-plugin/plugin.json` | `"version": "2.6.0"` → `"2.7.0"` |
| `plugins/dev-flow-worktree/.claude-plugin/plugin.json` | `"version": "1.8.0"` → `"1.9.0"` |

No file is created. No file is deleted. No `check-sync.py` exception is added (design **A2**: all three edits are identical on both sides, so the pair stays in sync with its one existing declared exception).

## Task order and dependencies

- **Task 1** (prose edit) and **Task 2** (version bumps) are independent of each other and may run in either order, but **both must be committed before Task 3**, because criterion 8(a) reads `BASE..HEAD`.
- **Task 3** depends on Tasks 1 and 2 being committed.
- Execution is complete when zero `- [ ]` boxes remain unchecked.

---

## Task 1: Normalize the three tier-name lines in both mirror copies

**Files:**
- Modify: `plugins/dev-flow/skills/adversarial-review/SKILL.md` (lines 52, 71, 81)
- Modify: `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md` (lines 52, 71, 81)
- Read-only input: `docs/superpowers/specs/2026-08-02-gh-28-29-review-prose-design.md`
- Test: none — this repo has no test framework (design **A6**)

**Interfaces:**
- Consumes: the three single-line fenced blocks in the design doc's *The edit* section, under the headings `### Line 52 (in both copies)`, `### Line 71 (in both copies)`, `### Line 81 (in both copies)`. Each block is the **complete final line**; leading whitespace is significant (line 71's block begins with three spaces).
- Produces: both `SKILL.md` copies at 89 lines with those three lines replaced. Task 3 re-runs the same design-sourced verification against the committed result.

**What changes:** three short spans, one per line, listed in Step 3's table. Nothing else on those lines moves.

- [ ] **Step 1: Confirm the starting state and that the design doc is intact**

```bash
cd /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b
git -C /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b hash-object docs/superpowers/specs/2026-08-02-gh-28-29-review-prose-design.md
git -C /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b status --porcelain
wc -l /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b/plugins/dev-flow/skills/adversarial-review/SKILL.md /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b/plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
```

Expected:
- hash-object prints `3f0b75ab7e602ee78ffbe77dcf4fa2b4de7ee1bf`. **Any other value → HALT and report "design doc modified".**
- `status --porcelain` prints nothing except, possibly, a modified `docs/superpowers/plans/2026-08-02-gh-28-29-review-prose-plan.md` (this plan's own checkbox ticks — an authorized modification, and the same allowance Task 3 Step 1 makes). Any other modified or untracked path → **HALT and report**: the tree is not in the state this plan was written against.
- `wc -l` prints `89` for each file.

- [ ] **Step 2: Record the pre-edit grep baseline**

```bash
git -C /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b grep -c -i 'group' -- 'plugins/*/skills/adversarial-review/SKILL.md'
```

Expected — exactly these two lines (order may vary):

```
plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md:6
plugins/dev-flow/skills/adversarial-review/SKILL.md:6
```

`6` is the pre-edit count; criterion 5 requires `3` after the edit. If it is not `6`, the files are not in the state the design measured → **HALT and report**.

- [ ] **Step 3: Apply the three substitutions in both copies**

Six exact-string replacements — three per file — with the `Edit` tool (or an equivalent exact-string replacement). This is design **A1** applied literally: `Edit` locates its target by **text**, never by line number, and refuses when the string is absent or not unique, so a file that is not in the state the design measured cannot be edited by accident. Each `old_string` below is quoted verbatim in the design doc and occurs **exactly once** per file at `BASE` (verified). Each replacement substitutes only the named span, so every other byte of lines 52, 71 and 81 — line 71's three leading spaces and its em dashes included — is carried over by the tool rather than transcribed.

Apply all three to `plugins/dev-flow/skills/adversarial-review/SKILL.md` **and** all three to `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md`. Same edits, same bytes, both files — the two copies are byte-identical on these lines today.

| # | `old_string` | `new_string` |
|---|---|---|
| 1 | `group-resolution agent` | `resolver` |
| 2 | `(seed reviewers, group resolvers)` | `(seed reviewers, resolvers)` |
| 3 | `**Group-resolution agents**` | `**Resolvers**` |

Six edits total. Do not use `replace_all` — each string is already unique. Do not type any other part of lines 52, 71 or 81: nothing in the table is a whole line, and nothing here needs to be.

If an `Edit` reports its string is absent or not unique, **HALT and report** — the file differs from what the design measured. If it is absent because an earlier attempt already applied it, that is a partial application: finish the remaining edits and let Step 4 adjudicate the result. Do not hand-edit around a refusal.

Nothing downstream trusts this step. Step 4 re-reads the design's three fenced blocks **from disk** and proves they landed byte-for-byte at 52/71/81 in both copies; Step 6 proves the pair is still in sync; Step 7 proves no other line moved. All three run before Step 8 commits.

- [ ] **Step 4: Verify the three blocks landed verbatim — success criterion 6**

This is the `CLAUDE.md`-mandated check: it re-reads the three blocks **from the design on disk** and asserts each appears verbatim at its stated line index in both copies. It shares `split_lines` / `block_after` with Step 3 by design — it is a *separate* read-only run, not the same process.

```bash
python3 - <<'PY'
ROOT = "/Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b"
DESIGN = ROOT + "/docs/superpowers/specs/2026-08-02-gh-28-29-review-prose-design.md"
TARGETS = [
    ROOT + "/plugins/dev-flow/skills/adversarial-review/SKILL.md",
    ROOT + "/plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md",
]
EXPECT = [
    ("### Line 52 (in both copies)", 52),
    ("### Line 71 (in both copies)", 71),
    ("### Line 81 (in both copies)", 81),
]

def split_lines(text):
    out = text.split("\n")
    if out and out[-1] == "":
        out.pop()
    return out

def block_after(doc_lines, heading):
    i = doc_lines.index(heading)
    j = i + 1
    while doc_lines[j].strip() == "":
        j += 1
    assert doc_lines[j] == "```", (heading, "expected a fence", repr(doc_lines[j]))
    body, k = [], j + 1
    while doc_lines[k] != "```":
        body.append(doc_lines[k])
        k += 1
    assert len(body) == 1, (heading, "expected a one-line block", len(body))
    return body[0]

doc = split_lines(open(DESIGN, encoding="utf-8").read())
for path in TARGETS:
    lines = split_lines(open(path, encoding="utf-8").read())
    assert len(lines) == 89, (path, "expected 89 lines", len(lines))
    for heading, lineno in EXPECT:
        want = block_after(doc, heading)
        got = lines[lineno - 1]
        assert got == want, (path, lineno, "got", repr(got), "want", repr(want))
        print(f"  OK {path}:{lineno}")
print("criterion 6: PASS")
PY
```

Expected: six `OK` lines then `criterion 6: PASS`, exit 0.

- [ ] **Step 5: Verify the removed phrases are gone — success criteria 3, 4, 5**

Scope every grep to `plugins/`. Repo-wide these phrases still hit, **correctly and by design**, in `docs/adr/0002-…` (an immutable dated record) and in `docs/superpowers/` (prior records plus the design doc, which quotes the removed text). Neither is to be "also fixed" (design *Out of scope*, **A3**).

```bash
git -C /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b grep -n 'group resolvers' -- plugins/ ; echo "exit=$?"
git -C /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b grep -in 'group-resolution' -- plugins/ ; echo "exit=$?"
git -C /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b grep -c -i 'group' -- 'plugins/*/skills/adversarial-review/SKILL.md'
```

Expected:
- criterion 3: no output, `exit=1`
- criterion 4: no output, `exit=1`
- criterion 5: exactly two lines, each ending `:3` —

```
plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md:3
plugins/dev-flow/skills/adversarial-review/SKILL.md:3
```

The three surviving `group` hits per copy are `:3` (front-matter `description`, out of scope, enforced against `marketplace.json` by `check-sync.py`), `:67` ("**Group** similar issues together…"), and `:70` ("judging the group's findings together") — all the grouping *operation*, none a tier name.

- [ ] **Step 6: Verify the mirror pair is still in sync — success criterion 1**

```bash
python3 /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b/scripts/check-sync.py ; echo "exit=$?"
```

Expected, exit 0:

```
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)
check-sync: all checks passed
```

If it reports a divergence, the edit landed in only one copy (design **A2**) — apply Step 3's three edits to the copy that missed them; **do not add a declared exception**, and **do not edit `scripts/check-sync.py` for any reason** (out of scope, concurrently owned).

- [ ] **Step 7: Verify only lines 52, 71, 81 moved — success criterion 8(b), `SKILL.md` half**

This reads the working tree, so it runs before the commit exists. It closes the gap `CLAUDE.md` names — `check-sync.py` passes text that was mangled identically on both sides. It is also what makes issue #29's NO CHANGE ruling mechanical: `:42` and `:48` are unchanged because *nothing* outside `{52, 71, 81}` is.

```bash
python3 - <<'PY'
import subprocess
ROOT = "/Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b"
BASE = subprocess.run(["git", "-C", ROOT, "merge-base", "origin/main", "HEAD"],
                      capture_output=True, text=True, check=True).stdout.strip()
print("BASE =", BASE)

def split_lines(text):            # check-sync.py's rule; agrees with `wc -l`
    out = text.split("\n")
    if out and out[-1] == "":
        out.pop()
    return out

def changed(path, base):
    old = split_lines(subprocess.run(["git", "-C", ROOT, "show", f"{base}:{path}"],
                                     capture_output=True, text=True, check=True).stdout)
    new = split_lines(open(f"{ROOT}/{path}", encoding="utf-8").read())
    assert len(old) == len(new), (path, len(old), len(new))
    return {i + 1 for i, (a, b) in enumerate(zip(old, new)) if a != b}

for path in ("plugins/dev-flow/skills/adversarial-review/SKILL.md",
             "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md"):
    got = changed(path, BASE)
    assert got == {52, 71, 81}, (path, sorted(got))
    print("  OK", path, sorted(got))
print("criterion 8(b) [SKILL.md]: PASS")
PY
```

Expected: the `BASE =` line, two `OK` lines each showing `[52, 71, 81]`, then `criterion 8(b) [SKILL.md]: PASS`, exit 0. A stray added or deleted line trips the `len(old) == len(new)` assert rather than silently shifting the set.

- [ ] **Step 8: Commit**

Stage the two files by exact path — never `git add -A`.

```bash
git -C /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b add plugins/dev-flow/skills/adversarial-review/SKILL.md plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
git -C /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b commit -m "adversarial-review: name the second tier resolver everywhere (#28)"
git -C /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b show --stat --format=%s HEAD
```

Expected: the commit succeeds and `show --stat` lists **exactly two** files, both `adversarial-review/SKILL.md`, each 3 insertions / 3 deletions. Any third path means something outside the authorized set was staged → **HALT and report**.

---

## Task 2: Bump both plugin versions

**Files:**
- Modify: `plugins/dev-flow/.claude-plugin/plugin.json` — `"version"` only
- Modify: `plugins/dev-flow-worktree/.claude-plugin/plugin.json` — `"version"` only
- Test: none

**Interfaces:**
- Consumes: nothing from Task 1. Independent; either order.
- Produces: the two bumped versions Task 3's criterion 7 asserts.

**Why:** the text in `adversarial-review/SKILL.md` ships into every model invocation, so a wording change is a behavior change under `CLAUDE.md`'s bump rule, and the install cache is version-keyed — an edit at an unchanged version is never picked up on re-sync. Minor rather than patch is the design's ruling: no version either plugin has ever shipped has a nonzero patch segment, and adopting a minor-vs-patch convention is a `CLAUDE.md`-level decision this change is scoped out of.

- [ ] **Step 1: Confirm the current versions**

```bash
grep -n '"version"' /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b/plugins/dev-flow/.claude-plugin/plugin.json
grep -n '"version"' /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b/plugins/dev-flow-worktree/.claude-plugin/plugin.json
```

Expected — the first command (`dev-flow`) prints:

```
3:  "version": "2.6.0",
```

and the second (`dev-flow-worktree`) prints:

```
3:  "version": "1.8.0",
```

Anything else → **HALT and report**; do not guess the next number.

- [ ] **Step 2: Apply both bumps**

Use the `Edit` tool (or an equivalent exact-string replacement) on each file — one edit per file, replacing only the version string:

- `plugins/dev-flow/.claude-plugin/plugin.json`: `"version": "2.6.0",` → `"version": "2.7.0",`
- `plugins/dev-flow-worktree/.claude-plugin/plugin.json`: `"version": "1.8.0",` → `"version": "1.9.0",`

Do not reformat, reorder keys, or touch `name` or `description` — `description` is duplicated into `.claude-plugin/marketplace.json` and `check-sync.py` enforces the pair.

- [ ] **Step 3: Verify the versions and that the JSON still parses — success criterion 7**

```bash
python3 - <<'PY'
import json
ROOT = "/Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b"
for rel, want in (("plugins/dev-flow/.claude-plugin/plugin.json", "2.7.0"),
                  ("plugins/dev-flow-worktree/.claude-plugin/plugin.json", "1.9.0")):
    data = json.loads(open(f"{ROOT}/{rel}", encoding="utf-8").read())
    assert data["version"] == want, (rel, data["version"], want)
    print(f"  OK {rel} -> {data['version']}")
print("criterion 7: PASS")
PY
```

Expected: two `OK` lines then `criterion 7: PASS`, exit 0.

- [ ] **Step 4: Verify only the version line moved — success criterion 8(b), `plugin.json` half**

The line *number* is deliberately not pinned — line position is not a stable property of a JSON file. What is asserted is that exactly one line differs and that it is the `"version"` line.

```bash
python3 - <<'PY'
import subprocess
ROOT = "/Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b"
BASE = subprocess.run(["git", "-C", ROOT, "merge-base", "origin/main", "HEAD"],
                      capture_output=True, text=True, check=True).stdout.strip()
print("BASE =", BASE)

def split_lines(text):
    out = text.split("\n")
    if out and out[-1] == "":
        out.pop()
    return out

def changed(path, base):
    old = split_lines(subprocess.run(["git", "-C", ROOT, "show", f"{base}:{path}"],
                                     capture_output=True, text=True, check=True).stdout)
    new = split_lines(open(f"{ROOT}/{path}", encoding="utf-8").read())
    assert len(old) == len(new), (path, len(old), len(new))
    return {i + 1 for i, (a, b) in enumerate(zip(old, new)) if a != b}

for path in ("plugins/dev-flow/.claude-plugin/plugin.json",
             "plugins/dev-flow-worktree/.claude-plugin/plugin.json"):
    got = changed(path, BASE)
    assert len(got) == 1, (path, "expected exactly one changed line", sorted(got))
    line = split_lines(open(f"{ROOT}/{path}", encoding="utf-8").read())[next(iter(got)) - 1]
    assert '"version"' in line, (path, "changed line is not the version line", line)
    print("  OK", path, sorted(got), line.strip())
print("criterion 8(b) [plugin.json]: PASS")
PY
```

Expected: the `BASE =` line, two `OK` lines each showing a single line number and the new `"version"` text, then `criterion 8(b) [plugin.json]: PASS`, exit 0.

- [ ] **Step 5: Verify `check-sync.py` still passes — the `description` pair is untouched**

```bash
python3 /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b/scripts/check-sync.py ; echo "exit=$?"
```

Expected, exit 0:

```
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)
check-sync: all checks passed
```

- [ ] **Step 6: Commit**

```bash
git -C /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b add plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
git -C /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b commit -m "dev-flow 2.7.0, dev-flow-worktree 1.9.0"
git -C /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b show --stat --format=%s HEAD
```

Expected: the commit succeeds and `show --stat` lists **exactly two** files, both `.claude-plugin/plugin.json`, each 1 insertion / 1 deletion.

---

## Task 3: Full success-criteria sweep on the committed branch

**Depends on:** Tasks 1 and 2, both committed. Criterion 8(a) reads `BASE..HEAD`, so it is only meaningful once the working tree equals `HEAD`.

**Files:** none modified. This task is verification only, and it is the whole verification surface (design **A6** — no test framework exists).

**Interfaces:**
- Consumes: the committed result of Tasks 1 and 2.
- Produces: a pass/fail verdict on all eight of the design's success criteria.

- [ ] **Step 1: Confirm the tree is clean and the design doc is still intact**

```bash
git -C /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b status --porcelain
git -C /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b hash-object docs/superpowers/specs/2026-08-02-gh-28-29-review-prose-design.md
```

Expected: `status --porcelain` prints nothing except, possibly, a modified `docs/superpowers/plans/2026-08-02-gh-28-29-review-prose-plan.md` (this plan's own checkbox ticks). `hash-object` prints `3f0b75ab7e602ee78ffbe77dcf4fa2b4de7ee1bf` — **any other value means the implementation modified the design doc → HALT and report.**

- [ ] **Step 2: Criteria 1 and 2 — `check-sync.py` and `claude plugin validate .`**

```bash
python3 /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b/scripts/check-sync.py ; echo "exit=$?"
```

Expected, exit 0, with the mirror-pair line reading exactly `check-sync: mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)`.

```bash
cd /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b
claude plugin validate . ; echo "exit=$?"
```

Expected — `exit=0`, `⚠ Found 8 warnings:`, eight `author: No author information provided…` lines, and `✔ Validation passed with warnings`. **This is a PASS** (design **A4**). Zero errors is the requirement; the 8 warnings are expected and must not be "fixed".

- [ ] **Step 3: Criteria 3, 4, 5 — the removed phrases and the surviving `group`**

```bash
git -C /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b grep -n 'group resolvers' -- plugins/ ; echo "exit=$?"
git -C /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b grep -in 'group-resolution' -- plugins/ ; echo "exit=$?"
git -C /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b grep -c -i 'group' -- 'plugins/*/skills/adversarial-review/SKILL.md'
```

Expected: no output and `exit=1` for the first two; `:3` for each of the two files on the third.

- [ ] **Step 4: Criterion 6 — the design-sourced fenced-block check**

Read `/Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b/docs/superpowers/plans/2026-08-02-gh-28-29-review-prose-plan.md`, find **Task 1 → Step 4**, and re-run its `python3` heredoc verbatim. It is read-only and idempotent, so re-running it here is safe. Do not retype it and do not substitute an equivalent of your own — this is the `CLAUDE.md`-mandated design-sourced check, and its whole point is that it reads the design from disk. (`subagent-driven-development` briefs one task at a time, so Task 1's text is not in this context; read it from the plan file rather than reconstructing it.)

Expected: six `OK` lines then `criterion 6: PASS`, exit 0.

- [ ] **Step 5: Criterion 7 — the versions**

Same pointer discipline as Step 4: read the plan file, find **Task 2 → Step 3**, and re-run its `python3` heredoc verbatim.

Expected: two `OK` lines then `criterion 7: PASS`, exit 0.

- [ ] **Step 6: Criterion 8(a) — file scope of the branch diff**

```bash
git -C /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b diff --name-only "$(git -C /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b merge-base origin/main HEAD)"..HEAD
```

Expected: exactly these paths and no others —

```
docs/superpowers/plans/2026-08-02-gh-28-29-review-prose-plan.md
docs/superpowers/specs/2026-08-02-gh-28-29-review-prose-design.md
plugins/dev-flow-worktree/.claude-plugin/plugin.json
plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
plugins/dev-flow/.claude-plugin/plugin.json
plugins/dev-flow/skills/adversarial-review/SKILL.md
```

`--name-only` rather than the design's `--stat`: the criterion is unchanged — 8(a) asserts the *path set*, and that is exactly what `--name-only` prints. `--stat` pads every row with a changed-line count, a `+/-` graph and a summary line, and elides long paths to `.../<tail>` at the default width, which would collapse the two `adversarial-review/SKILL.md` rows into indistinguishable tails.

Then assert it mechanically rather than by eye — this prints any path outside the authorized set:

```bash
git -C /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b diff --name-only "$(git -C /Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b merge-base origin/main HEAD)"..HEAD | grep -v -E '^(docs/superpowers/|plugins/(dev-flow|dev-flow-worktree)/skills/adversarial-review/SKILL\.md$|plugins/(dev-flow|dev-flow-worktree)/\.claude-plugin/plugin\.json$)' ; echo "exit=$?"
```

Expected: no output, `exit=1`. Any printed path is a scope violation → **HALT and report the path.**

- [ ] **Step 7: Criterion 8(b) — line scope, all four non-doc files in one run**

```bash
python3 - <<'PY'
import subprocess
ROOT = "/Users/taylor/dev/claude-plugins/.claude/worktrees/agent-ae55cefd286cb728b"
BASE = subprocess.run(["git", "-C", ROOT, "merge-base", "origin/main", "HEAD"],
                      capture_output=True, text=True, check=True).stdout.strip()
print("BASE =", BASE)

def split_lines(text):            # check-sync.py's rule; agrees with `wc -l`
    out = text.split("\n")
    if out and out[-1] == "":
        out.pop()
    return out

def changed(path, base):
    old = split_lines(subprocess.run(["git", "-C", ROOT, "show", f"{base}:{path}"],
                                     capture_output=True, text=True, check=True).stdout)
    new = split_lines(open(f"{ROOT}/{path}", encoding="utf-8").read())
    assert len(old) == len(new), (path, len(old), len(new))
    return {i + 1 for i, (a, b) in enumerate(zip(old, new)) if a != b}

for path in ("plugins/dev-flow/skills/adversarial-review/SKILL.md",
             "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md"):
    got = changed(path, BASE)
    assert got == {52, 71, 81}, (path, sorted(got))
    print("  OK", path, sorted(got))

for path in ("plugins/dev-flow/.claude-plugin/plugin.json",
             "plugins/dev-flow-worktree/.claude-plugin/plugin.json"):
    got = changed(path, BASE)
    assert len(got) == 1, (path, "expected exactly one changed line", sorted(got))
    line = split_lines(open(f"{ROOT}/{path}", encoding="utf-8").read())[next(iter(got)) - 1]
    assert '"version"' in line, (path, "changed line is not the version line", line)
    print("  OK", path, sorted(got), line.strip())
print("criterion 8(b): PASS")
PY
```

Expected: the `BASE =` line, four `OK` lines, then `criterion 8(b): PASS`, exit 0.

Together with criterion 6 this pins both `SKILL.md` files completely: every one of the 89 lines is either byte-identical to `BASE` or one of the three blocks quoted in the design. Two things follow as corollaries and need no separate check — both files are still 89 lines, and `:42` and `:48` (the *Glossary conformance* and *Terminology collision and drift* passages) are unchanged in both copies, which is issue #29's NO CHANGE ruling holding mechanically.

- [ ] **Step 8: Record the verdict**

All eight criteria must be green:

| # | Criterion | Where checked |
|---|---|---|
| 1 | `check-sync.py` exits 0, `89 lines, 1 declared exception` | Task 3 Step 2 |
| 2 | `claude plugin validate .` exits 0, exactly 8 author warnings, 0 errors | Task 3 Step 2 |
| 3 | `git grep -n 'group resolvers' -- plugins/` → no output, exit 1 | Task 3 Step 3 |
| 4 | `git grep -in 'group-resolution' -- plugins/` → no output, exit 1 | Task 3 Step 3 |
| 5 | `git grep -c -i 'group' -- 'plugins/*/skills/adversarial-review/SKILL.md'` → `3` each | Task 3 Step 3 |
| 6 | Design's three fenced blocks appear verbatim at lines 52/71/81 in both copies | Task 3 Step 4 |
| 7 | Versions are `2.7.0` and `1.9.0` | Task 3 Step 5 |
| 8a | Branch diff touches only the four files plus `docs/superpowers/` | Task 3 Step 6 |
| 8b | Changed-line sets are exactly `{52, 71, 81}` / one `"version"` line | Task 3 Step 7 |

If every row is green, execution is complete. Report the verdict; do not open a PR, close issues, file follow-ups, or run any integration skill — those are the pipeline's steps.

---

## Not part of this implementation

Recorded so a fresh implementer does not helpfully do them. These are the pipeline's integration steps (design **A5**, **A7**, **A8**):

- Closing issue **#28** on merge.
- Closing issue **#29** with the design's *Issue #29* section as its closing comment (a recorded ruling with no code change is its complete outcome).
- Filing the two follow-up issues: whether `group-resolution agent` belongs on `CONTEXT.md`'s **Resolver** `_Avoid_:` line (**A7**), and whether criterion 8(b)'s line-set check belongs in `CLAUDE.md`'s `Always:` list, cross-referencing the in-flight **#24** (**A8**).
- Pushing, opening the PR, merging.

And, hard-excluded by the design's *Out of scope* — a proposal to touch any of these is a blocker, not a task: `CONTEXT.md`, `docs/adr/0002-opus-resolvers-and-the-end-of-adversary-not-author.md` (says "group-resolution tier"; a dated record, deliberately left alone), `.claude-plugin/marketplace.json` and the duplicated `description`, `scripts/check-sync.py`, `CLAUDE.md`, `docs/agents/`, both `README.md`s, both pipeline `SKILL.md`s, and every pre-existing file under `docs/superpowers/` — the prior records, not this change's own design doc and plan (Global Constraints).

## Plan self-review

- **Spec coverage.** *The edit* → Task 1 Steps 3–5. *Version bumps* → Task 2. *Success criteria* 1–8 → the Task 3 Step 8 table, each row naming the step that runs it; 6 and 8(b) additionally run inside Tasks 1–2 so a failure is caught before the commit. *Out of scope* and *Assumptions* → Global Constraints plus *Not part of this implementation*. **A1** → Task 1 Step 3's exact-string replacements, which match by text, never by line number, and refuse a string that is absent or not unique. **A2** → Task 1 Step 6's repair-don't-declare instruction. **A3** → Task 1 Step 5's scoping note. **A4** → Task 3 Step 2. **A6** → Tech Stack. **A5/A7/A8** → *Not part of this implementation*.
- **Placeholder scan.** No TBDs. Every command carries its absolute path and its expected output; every Python snippet is complete and runnable as written.
- **Retype check.** No step restates line 52, 71, or 81 in full. The only literals typed anywhere are the six short fragments in Task 1 Step 3's table — each the exact span that changes, each quoted verbatim in the design. Every other byte of those three lines is carried over by the replacement, never transcribed. A wrong `old_string` writes nothing: `Edit` refuses a string it cannot find uniquely. A wrong `new_string` writes, and Step 4 catches it before the commit by comparing against the design's blocks read fresh from disk.
- **Type consistency.** `split_lines` (4 copies), `changed` (3), and `block_after` (1) have one definition each, repeated verbatim wherever they appear. The reason is **process** isolation, not context isolation: every snippet is a separate `python3 -` heredoc and Global Constraints forbid writing a shared module to disk, so two snippets cannot share a definition even inside one task. `superpowers:subagent-driven-development` briefs one implementer **per task**, not per step — Task 1's Steps 4 and 7 run in the *same* context, and their two `split_lines` copies are justified by the process boundary alone, not by a context boundary. Where a snippet is reused across a task boundary it is pointed at by path rather than re-pasted (Task 3 Steps 4 and 5). In-flight issue **#24** tracks this repo's accumulation of hand-copied design-block readers; this plan adds one, not five.
