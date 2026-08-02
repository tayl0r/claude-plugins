---
dev-flow: {slug: gh-30-flat-topology, spec: docs/superpowers/specs/2026-08-02-gh-30-flat-topology-design.md}
---

# gh-30 Flat-Topology Re-Anchor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite the flat-topology bullet in both pipeline `SKILL.md`s so it names no harness version and no tool name, record the topology decision in a new ADR, and bump both plugin versions.

**Architecture:** Three payload texts already exist, complete and literal, inside the design document at `docs/superpowers/specs/2026-08-02-gh-30-flat-topology-design.md`. They are the three **plain fenced blocks** in that file (fences with *no* info string; every other fence there is ` ```text ` or ` ```sh `). Task 1 runs one `python3` heredoc that **re-reads those blocks from the design file on disk and writes them into their three targets** — the payload text is never retyped by a human or a model. Task 2 bumps two version numbers. Task 3 runs the design's whole Verification section.

**Tech Stack:** Markdown, JSON, `python3` (stdlib only), `grep`, `git`, `claude plugin validate`.

## Global Constraints

- **Work in place** in the current checkout (`/Users/taylor/dev/claude-plugins/.claude/worktrees/agent-af461c65d1a815cb6`, branch `tayl0r/gh-30-flat-topology`). Do **not** create a git worktree.
- **Commit per task; never push.** Each task commits its own work on the current branch, as `subagent-driven-development` expects and as dev-flow's Artifact Contract requires — its resume position is derived from *committed* state, and an Execute-landing resume stashes uncommitted tracked modifications. Do **not** `git push`, do not open or merge a PR, do not switch or create branches: the pipeline owns every integration step.
- **Never retype the payload text.** Task 1 must extract it from the design file on disk with the supplied script. A hand-typed or model-paraphrased copy is a defect even if it looks identical — the design-conformance check run by Task 1 Step 4 and Task 3 Step 3 exists specifically to catch that.
- **This repo has no test framework.** There is nothing to `pytest` / `npm test`. Verification is exactly the commands in this plan, which are exactly the design's Verification section.
- **Files in scope — nothing else may be created or edited:**
  - `plugins/dev-flow/skills/dev-flow/SKILL.md` (one-line replacement at line 266; file stays **277** lines)
  - `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` (one-line replacement at line 261; file stays **271** lines)
  - `docs/adr/0003-flat-topology-for-the-dev-flow-pipelines.md` (new file)
  - `plugins/dev-flow/.claude-plugin/plugin.json` → version `2.7.0`
  - `plugins/dev-flow-worktree/.claude-plugin/plugin.json` → version `1.9.0`
- **Forbidden files — if a step appears to need one of these, STOP and report it as a blocker; do not work around it:** `plugins/*/skills/adversarial-review/SKILL.md` (a concurrent change owns it — the ADR *quotes* it and it stays byte-identical), `CLAUDE.md`, `scripts/`, `CONTEXT.md`, `.claude-plugin/marketplace.json`.
- **Do not "fix" `2.1.218` mentions under `docs/superpowers/`.** Those are dated historical records; editing them would falsify the record. Every residue grep in this plan is scoped to `plugins/` for exactly that reason — the design doc and the new ADR both legitimately quote those strings.
- **All commands run from the repo root.**

### Why verification is unusually heavy here

`plugins/dev-flow/skills/dev-flow/SKILL.md` and `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` are the **hand-mirrored pair**. `python3 scripts/check-sync.py` does **not** compare them — it only enrols the `adversarial-review/SKILL.md` pair and the manifest descriptions. So a change made to one pipeline file and missed on the other is caught by **nothing** in this repository, and a paraphrase applied identically to both would also pass every automated check.

`CLAUDE.md` therefore requires that any change to a mirrored pair verify against something **outside the pair**. That is what Task 1 Step 4 and Task 3 Step 3 are: a `python3` block that re-reads the three payload blocks from the design file and asserts each landed byte-for-byte in its target, in the right place, with both files unchanged in length, and with the two bullets exact substitution images of one another. Plus the residue greps, which assert the removed phrases are gone from shipped text. Do not skip or reword them.

## File Structure

| Path | Change | Responsibility |
|---|---|---|
| `plugins/dev-flow/skills/dev-flow/SKILL.md` | modify line 266 | Shipped `dev-flow` orchestrator instructions; the flat-topology bullet under `## Environment Assumptions` |
| `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` | modify line 261 | Same bullet in the mirrored `dev-flow-worktree` pipeline |
| `docs/adr/0003-flat-topology-for-the-dev-flow-pipelines.md` | create | Durable record of *why* the pipelines are flat, plus the dated 2.1.217→218→220 evidence |
| `plugins/dev-flow/.claude-plugin/plugin.json` | modify `version` | Version-keyed install cache must see the shipped text change |
| `plugins/dev-flow-worktree/.claude-plugin/plugin.json` | modify `version` | Same |

---

### Task 1: Apply the three payload edits

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md:266`
- Modify: `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md:261`
- Create: `docs/adr/0003-flat-topology-for-the-dev-flow-pipelines.md`
- Read-only input: `docs/superpowers/specs/2026-08-02-gh-30-flat-topology-design.md`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: the design's three plain-fenced payload blocks now occupy their three targets — block 0 at line 266 of the `dev-flow` pipeline `SKILL.md`, block 1 at line 261 of the `dev-flow-worktree` one, block 2 as the whole of the new ADR. Task 3 Step 3 re-runs this task's Step 4 check unchanged.

**Why these three edits are one task and not three.** The two pipeline `SKILL.md`s are the **hand-mirrored pair** (ADR-0001): `check-sync.py` does not compare them, so an edit landing on one and not the other is caught by nothing in this repository. Splitting them across tasks would leave a one-sided pair on disk at a task boundary and would force each half to assert a *failure* — an exact count of expected `MISMATCH:` lines — because neither half can make the conformance check pass on its own. Step 2 applies all three edits from one script that validates every target **before** writing any of them, so no partial application is reachable even from a mid-script failure; Step 4's check, which passes only once all three have landed, is the single gate over the whole payload. The design reaches the same conclusion about the change itself: *"the ADR and the bullet are not independent subsystems … Nothing here decomposes."*

Context: line 266 of the `dev-flow` copy and line 261 of the `dev-flow-worktree` copy are each the first bullet under `## Environment Assumptions`, beginning `- **Flat topology — the orchestrator is the only spawner.**`. Each contains the false clause `**Claude Code 2.1.218 does not grant spawned subagents the ...` and a trailing parenthetical about 2.1.217 / 1.2.0. Each whole line is replaced by the design's matching block, which keeps the normative `This is required, not a preference:` clause but re-anchors it to a version-independent reason. The ADR body deliberately *does* contain `2.1.217` / `2.1.218` / `2.1.220` and quotes `adversarial-review`'s Review-integrity clause — that is dated evidence, correct and intended, and it is why every residue grep in this plan is scoped to `plugins/`. `plugins/*/skills/adversarial-review/SKILL.md` is quoted but **must not be edited**.

- [x] **Step 1: Confirm the pre-change state of all three targets**

Run:

```sh
sed -n '264,266p' plugins/dev-flow/skills/dev-flow/SKILL.md; wc -l < plugins/dev-flow/skills/dev-flow/SKILL.md
sed -n '259,261p' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md; wc -l < plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
ls docs/adr/
```

Expected: in each `SKILL.md`, `## Environment Assumptions`, then a blank line, then the flat-topology bullet containing the substring `does not grant spawned subagents` — at lines 264–266 with a line count of `277` for `dev-flow`, and at lines 259–261 with a line count of `271` for `dev-flow-worktree`; then `docs/adr/` holding exactly `0001-duplicate-the-two-dev-flow-variants.md` and `0002-opus-resolvers-and-the-end-of-adversary-not-author.md`. If any of that differs — including a `0003-…` already present — STOP and report; the design's line numbers no longer describe the files.

- [x] **Step 2: Apply all three edits by copying the payload blocks out of the design on disk**

Run this exactly. Do **not** retype any payload text, and do **not** derive the second bullet by search-and-replacing the first — every byte comes from the design file. (The fence is unindented on purpose — an indented `python3` heredoc is an `IndentationError`.)

```sh
python3 - <<'PY'
from pathlib import Path

DESIGN = "docs/superpowers/specs/2026-08-02-gh-30-flat-topology-design.md"
ANCHOR = "## Environment Assumptions"
ADR = "docs/adr/0003-flat-topology-for-the-dev-flow-pipelines.md"
BULLETS = [
    ("plugins/dev-flow/skills/dev-flow/SKILL.md", 0),
    ("plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md", 1),
]
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

assert len(blocks) == 3, "design has %d plain-fenced blocks, want 3" % len(blocks)

pending, report = [], []

for target, idx in BULLETS:
    assert len(blocks[idx]) == 1, "payload block %d is not one line" % idx
    lines = Path(target).read_text(encoding="utf-8").split("\n")
    assert lines.count(ANCHOR) == 1, "%s: %r appears %d times" % (target, ANCHOR, lines.count(ANCHOR))
    i = lines.index(ANCHOR) + 2
    old = lines[i]
    assert old.startswith("- **Flat topology"), "%s line %d is not the flat-topology bullet" % (target, i + 1)
    assert "does not grant spawned subagents" in old, "%s line %d is not the pre-change bullet" % (target, i + 1)
    lines[i] = blocks[idx][0]
    pending.append((target, "\n".join(lines)))
    report.append("replaced line %d in %s" % (i + 1, target))

body = blocks[2]
assert body and body[0].startswith("# "), "payload block 2 is not the ADR body"
assert not Path(ADR).exists(), "%s already exists" % ADR
pending.append((ADR, "\n".join(body) + "\n"))
report.append("wrote %s %d lines" % (ADR, len(body)))

for path, text in pending:
    Path(path).write_text(text, encoding="utf-8")
for line in report:
    print(line)
PY
```

Expected output, exactly:

```text
replaced line 266 in plugins/dev-flow/skills/dev-flow/SKILL.md
replaced line 261 in plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
wrote docs/adr/0003-flat-topology-for-the-dev-flow-pipelines.md 30 lines
```

Any `AssertionError` traceback means STOP and report — a target or the design is not in the state this plan assumes, and **nothing was written**: the script validates all three targets before writing any of them. That includes a re-run after a successful apply, which fails on the first bullet — a completed apply is not re-appliable, so report it rather than editing anything by hand.

- [x] **Step 3: Verify — both bullets in place, both files still their original length, the ADR present, and the removed phrases gone from `plugins/`**

Run:

```sh
wc -l < plugins/dev-flow/skills/dev-flow/SKILL.md
wc -l < plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
sed -n '264,266p' plugins/dev-flow/skills/dev-flow/SKILL.md
sed -n '259,261p' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
wc -l < docs/adr/0003-flat-topology-for-the-dev-flow-pipelines.md
head -1 docs/adr/0003-flat-topology-for-the-dev-flow-pipelines.md
grep -c -E '^## (Considered options|Consequences|Revisit when)$' docs/adr/0003-flat-topology-for-the-dev-flow-pipelines.md
grep -rc -F 'This is required, not a preference:' plugins/ | grep -v ':0$'
grep -rn -E '2\.1\.2|does not grant spawned subagents|is why 1\.2\.0 flattened' plugins/; echo "residue-exit=$?"
```

Expected: `277`; then `271`; then, for each file in turn, `## Environment Assumptions`, a blank line, and a bullet beginning `- **Flat topology — the orchestrator is the only spawner.**` that contains `has been withdrawn and restored across patch releases` and no digits-and-dots version string — naming `dev-flow` in the first, `dev-flow-worktree` in the second; then `30`; then `# The dev-flow pipelines are flat — the orchestrator is the only spawner`; then `3`; then exactly two lines (either order):

```text
plugins/dev-flow/skills/dev-flow/SKILL.md:1
plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md:1
```

then **no output** from the residue grep followed by `residue-exit=1`.

- [x] **Step 4: Verify against the design — the conformance check must pass clean**

This is the `CLAUDE.md` per-change check: it re-reads all three payload blocks from the design on disk and asserts each landed byte-for-byte in its target. It is reproduced in full here and again in **Task 3 Step 3**, because each task is dispatched with only its own text — that duplication is deliberate, and neither copy may be replaced by a pointer to the other. (Whether this repo should grow a shared runner for it is **#24**, which owns `CLAUDE.md` and `scripts/`; both are forbidden here.)

Run (the fence is unindented on purpose — an indented `python3` heredoc is an `IndentationError`):

```sh
python3 - <<'PY'
import sys
from pathlib import Path

DESIGN = "docs/superpowers/specs/2026-08-02-gh-30-flat-topology-design.md"
ANCHOR = "## Environment Assumptions"
TARGETS = [
    ("plugins/dev-flow/skills/dev-flow/SKILL.md", 277),
    ("plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md", 271),
]
ADR = "docs/adr/0003-flat-topology-for-the-dev-flow-pipelines.md"
GONE = [
    "does not grant spawned subagents",
    "is why 1.2.0 flattened",
    "2.1.218",
    "2.1.217",
]
FENCE = chr(96) * 3

bad = []

def read(path):
    try:
        return Path(path).read_text(encoding="utf-8").split("\n")
    except (OSError, UnicodeDecodeError) as e:
        bad.append("%s: cannot read (%s)" % (path, e.__class__.__name__))
        return None

def report():
    for why in bad:
        print("MISMATCH:", why)
    print("design-conformance:", "FAIL" if bad else "OK")
    sys.exit(1 if bad else 0)

design = read(DESIGN)
if design is None:
    report()

blocks, cur, mode = [], None, None
for line in design:
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

shape = [len(b) for b in blocks]
if len(blocks) != 3:
    bad.append("design has %d plain-fenced blocks, want 3" % len(blocks))
elif shape[:2] != [1, 1]:
    bad.append("design's two bullet blocks are %s lines, want 1 each" % shape[:2])
if bad:
    report()

for (path, want_len), block in zip(TARGETS, blocks[:2]):
    want = block[0]
    lines = read(path)
    if lines is None:
        continue
    if lines and lines[-1] == "":
        lines.pop()
    if len(lines) != want_len:
        bad.append("%s is %d lines, want %d" % (path, len(lines), want_len))
    at = [i for i, l in enumerate(lines) if l == want]
    if len(at) != 1:
        bad.append("%s: bullet found %d times, want exactly 1" % (path, len(at)))
    elif not (at[0] >= 2 and lines[at[0] - 1] == "" and lines[at[0] - 2] == ANCHOR):
        bad.append("%s: bullet does not sit first under %r" % (path, ANCHOR))
    body = "\n".join(lines)
    for g in GONE:
        if g in body:
            bad.append("%s: removed phrase survives: %r" % (path, g))

if blocks[1][0].replace("dev-flow-worktree", "dev-flow") != blocks[0][0]:
    bad.append("the two bullets are not substitution images of each other")

adr_lines = read(ADR)
if adr_lines is not None:
    while adr_lines and adr_lines[-1] == "":
        adr_lines.pop()
    if adr_lines != blocks[2]:
        bad.append("%s does not match the design's ADR block exactly" % ADR)

report()
PY
echo "exit=$?"
```

Expected, exactly:

```text
design-conformance: OK
exit=0
```

Any `MISMATCH:` line means STOP and report which one. This is the check that catches a paraphrase, a one-sided edit, a length change, or a bullet moved out from under `## Environment Assumptions`. Nothing else in the repository catches any of those.

---

### Task 2: Bump both plugin versions

**Files:**
- Modify: `plugins/dev-flow/.claude-plugin/plugin.json` — `"version": "2.6.0"` → `"version": "2.7.0"`
- Modify: `plugins/dev-flow-worktree/.claude-plugin/plugin.json` — `"version": "1.8.0"` → `"version": "1.9.0"`

**Interfaces:**
- Consumes: Task 1 changed shipped `SKILL.md` text; the install cache is version-keyed (`~/.claude/plugins/cache/taylor-plugins/<plugin>/<version>/`), so an unbumped version is never picked up on re-sync.
- Produces: nothing later depends on beyond Task 3's version assertion.

Why **minor**, not patch: the replacement clause carries an instruction the bullet did not previously carry (*observing that it currently works is not permission to nest*), which is a behavior change on `CLAUDE.md`'s terms; and this repo has never used a non-zero patch segment, so introducing one would establish a convention as a side effect. Decided in the design — do not re-decide it. Do **not** touch `description` in either file and do **not** touch `.claude-plugin/marketplace.json`.

- [ ] **Step 1: Confirm the current versions**

Run:

```sh
git grep '"version"' -- plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
```

Expected, exactly:

```text
plugins/dev-flow-worktree/.claude-plugin/plugin.json:  "version": "1.8.0",
plugins/dev-flow/.claude-plugin/plugin.json:  "version": "2.6.0",
```

If either differs, STOP and report. (The design's recorded default for a colliding bump from another change is *rebase and take the next minor above whatever `main` then holds* — but that changes the target numbers this plan and its verification state, so it is a report-and-confirm, not a silent adjustment.)

- [ ] **Step 2: Edit `plugins/dev-flow/.claude-plugin/plugin.json`**

Replace the single line `  "version": "2.6.0",` with `  "version": "2.7.0",`. Change nothing else in the file — same indentation, same trailing comma.

- [ ] **Step 3: Edit `plugins/dev-flow-worktree/.claude-plugin/plugin.json`**

Replace the single line `  "version": "1.8.0",` with `  "version": "1.9.0",`. Change nothing else in the file.

- [ ] **Step 4: Verify — both versions moved, both files still valid JSON, nothing else changed**

Run:

```sh
git grep '"version"' -- plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
python3 -c "import json;[json.load(open(p)) for p in ['plugins/dev-flow/.claude-plugin/plugin.json','plugins/dev-flow-worktree/.claude-plugin/plugin.json']];print('json OK')"
git diff --stat -- plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
```

Expected, exactly:

```text
plugins/dev-flow-worktree/.claude-plugin/plugin.json:  "version": "1.9.0",
plugins/dev-flow/.claude-plugin/plugin.json:  "version": "2.7.0",
json OK
```

then a `git diff --stat` whose summary line is exactly `2 files changed, 2 insertions(+), 2 deletions(-)`, with each of the two `plugin.json` paths listed as `| 2 +-`. Git's leading number is *lines touched*, so a one-line value edit reads `2` — one insertion plus one deletion — not `1`. Any other summary line, or a third path in the listing, means STOP and report.

---

### Task 3: Full verification

**Files:** none modified. This task only runs checks.

**Interfaces:**
- Consumes: all of Tasks 1–2. Every step below assumes all five in-scope file changes have landed.
- Produces: the evidence that the change is complete and correct. Do not claim completion without having seen each expected output below.

This is the design's Verification section run end to end. Steps 1–3 are the `CLAUDE.md` hand-mirrored-pair procedure — residue greps plus the per-change design-conformance check — and they are the only things anchored **outside** the pair. `check-sync.py` (step 6) does **not** read these two files at all.

- [ ] **Step 1: Residue — the removed phrases are gone from shipped text**

Run:

```sh
grep -rn -F '2.1.218' plugins/; echo "exit=$?"
grep -rn -F '2.1.217' plugins/; echo "exit=$?"
grep -rn -F 'does not grant spawned subagents' plugins/; echo "exit=$?"
grep -rn -F 'is why 1.2.0 flattened' plugins/; echo "exit=$?"
grep -rn -E '2\.1\.2' plugins/; echo "exit=$?"
```

Expected: **no output** from any of the five greps, and `exit=1` after each. Scoped to `plugins/` deliberately — this design doc and ADR-0003 both quote these strings and are correct places for them to appear.

- [ ] **Step 2: The normative clause survives in both copies and only there**

Run:

```sh
grep -rc -F 'This is required, not a preference:' plugins/ | grep -v ':0$'
```

Expected: exactly two lines (either order), each ending in `:1`:

```text
plugins/dev-flow/skills/dev-flow/SKILL.md:1
plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md:1
```

Any third line, or a count other than `1`, means STOP and report.

- [ ] **Step 3: Design conformance — both bullets and the ADR landed verbatim, in the right place**

Run (the fence is unindented on purpose — an indented `python3` heredoc is an `IndentationError`). This is the same block as **Task 1 Step 4**, reproduced in full because each task is dispatched with only its own text:

```sh
python3 - <<'PY'
import sys
from pathlib import Path

DESIGN = "docs/superpowers/specs/2026-08-02-gh-30-flat-topology-design.md"
ANCHOR = "## Environment Assumptions"
TARGETS = [
    ("plugins/dev-flow/skills/dev-flow/SKILL.md", 277),
    ("plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md", 271),
]
ADR = "docs/adr/0003-flat-topology-for-the-dev-flow-pipelines.md"
GONE = [
    "does not grant spawned subagents",
    "is why 1.2.0 flattened",
    "2.1.218",
    "2.1.217",
]
FENCE = chr(96) * 3

bad = []

def read(path):
    try:
        return Path(path).read_text(encoding="utf-8").split("\n")
    except (OSError, UnicodeDecodeError) as e:
        bad.append("%s: cannot read (%s)" % (path, e.__class__.__name__))
        return None

def report():
    for why in bad:
        print("MISMATCH:", why)
    print("design-conformance:", "FAIL" if bad else "OK")
    sys.exit(1 if bad else 0)

design = read(DESIGN)
if design is None:
    report()

blocks, cur, mode = [], None, None
for line in design:
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

shape = [len(b) for b in blocks]
if len(blocks) != 3:
    bad.append("design has %d plain-fenced blocks, want 3" % len(blocks))
elif shape[:2] != [1, 1]:
    bad.append("design's two bullet blocks are %s lines, want 1 each" % shape[:2])
if bad:
    report()

for (path, want_len), block in zip(TARGETS, blocks[:2]):
    want = block[0]
    lines = read(path)
    if lines is None:
        continue
    if lines and lines[-1] == "":
        lines.pop()
    if len(lines) != want_len:
        bad.append("%s is %d lines, want %d" % (path, len(lines), want_len))
    at = [i for i, l in enumerate(lines) if l == want]
    if len(at) != 1:
        bad.append("%s: bullet found %d times, want exactly 1" % (path, len(at)))
    elif not (at[0] >= 2 and lines[at[0] - 1] == "" and lines[at[0] - 2] == ANCHOR):
        bad.append("%s: bullet does not sit first under %r" % (path, ANCHOR))
    body = "\n".join(lines)
    for g in GONE:
        if g in body:
            bad.append("%s: removed phrase survives: %r" % (path, g))

if blocks[1][0].replace("dev-flow-worktree", "dev-flow") != blocks[0][0]:
    bad.append("the two bullets are not substitution images of each other")

adr_lines = read(ADR)
if adr_lines is not None:
    while adr_lines and adr_lines[-1] == "":
        adr_lines.pop()
    if adr_lines != blocks[2]:
        bad.append("%s does not match the design's ADR block exactly" % ADR)

report()
PY
echo "exit=$?"
```

Expected, exactly:

```text
design-conformance: OK
exit=0
```

This is the check that catches a paraphrase, a one-sided edit, a length change, or a bullet moved out from under `## Environment Assumptions`. Nothing else in the repository catches any of those.

- [ ] **Step 4: Versions moved, and by one minor**

Run:

```sh
git grep '"version"' -- plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
```

Expected, exactly:

```text
plugins/dev-flow-worktree/.claude-plugin/plugin.json:  "version": "1.9.0",
plugins/dev-flow/.claude-plugin/plugin.json:  "version": "2.7.0",
```

`git grep` rather than bare `grep`: the assertion is *which plugin is at which version*, and only `git grep`'s path-labelled, path-sorted output makes that deterministic.

- [ ] **Step 5: Forbidden files untouched**

Run:

```sh
git diff --name-only main -- CLAUDE.md CONTEXT.md scripts/ 'plugins/*/skills/adversarial-review/'
```

Expected: **no output.** Any path printed here is a scope violation — STOP and report it rather than reverting silently.

- [ ] **Step 6: `check-sync.py` still passes**

Run:

```sh
python3 scripts/check-sync.py
```

Expected, exactly (unchanged from baseline — this change touches no file it reads):

```text
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)
check-sync: all checks passed
```

Note what this does **not** cover: the pipeline `SKILL.md` pair is not enrolled, so a one-sided edit passes it silently. Step 3 is the check that catches that.

- [ ] **Step 7: `claude plugin validate .` passes**

Run:

```sh
claude plugin validate .; echo "exit=$?"
```

Expected: validation succeeds with **exactly 8** `No author information provided` warnings and `exit=0`. Those 8 warnings are the expected steady state of this repo, **not a failure** — do not attempt to fix them, and do not add author fields.

- [ ] **Step 8: Confirm the working tree holds only the expected changes, uncommitted**

Run:

```sh
git status --short
```

Expected: **no output**, or untracked scratch only. Tasks 1 and 2 between them committed exactly these five paths —

```text
plugins/dev-flow/skills/dev-flow/SKILL.md
plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
plugins/dev-flow/.claude-plugin/plugin.json
plugins/dev-flow-worktree/.claude-plugin/plugin.json
```

— plus `docs/adr/0003-flat-topology-for-the-dev-flow-pipelines.md`, all of them **already committed by their own task**, so a clean tree here is the expected result. Untracked scratch (e.g. SDD's git-ignored ledger) is fine. Anything else modified and uncommitted means STOP and report. **Do not `git push`** — the pipeline owns every integration step.

---

## Self-Review

**Spec coverage.** Design change list items 1 and 2 (both pipeline bullets) and item 4 (the new ADR) → Task 1, applied by one script and gated by one conformance check. Item 3 (phrases removed) → Task 1 Step 3, Task 3 Step 1, and the `GONE` list inside the conformance check. Item 5 (version bumps) → Task 2. Design Verification steps 1–7 → Task 3 steps 1–5 and 6–7. Design "Assumptions recorded" → the pre-state confirmations in Task 1 Step 1 and Task 2 Step 1, each a STOP-and-report on divergence. Forbidden-file list → Global Constraints plus Task 3 Step 5. No gaps.

**Placeholder scan.** No `TBD`, no "handle edge cases", and no cross-task pointer standing in for anything an executor must run: the conformance block appears in full at both sites that run it (Task 1 Step 4, Task 3 Step 3), because a task is dispatched with only its own text and cannot reach another task's. Every expected output is a literal.

**Consistency.** Paths, line numbers (266 / 261), line counts (277 / 271), block indices (0 / 1 / 2), ADR body length (30 lines), and versions (`2.7.0` / `1.9.0`) match the design and were confirmed against the files on disk while writing this plan. The two copies of the conformance block are byte-identical to each other. The payload text is never reproduced in this plan — by construction it can only come from the design file, which is the point.
