---
dev-flow:
  slug: gh-65-brief-plan-path
  spec: docs/superpowers/specs/2026-08-05-gh-65-brief-plan-path-design.md
---

# gh-65: the Execute stage hands each implementer the plan path — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add one Stage 3 "Implementer briefing" bullet (block 0) after each pipeline `SKILL.md`'s own `Baseline` anchor, create ADR 0005 (block 1), and bump both plugin versions — so dev-flow's orchestrator hands every implementer the plan's absolute path plus a resolve-out-of-section-references-verbatim clause, making the fix correct-by-default.

**Architecture:** Four tasks over exactly five files. Tasks 1–3 each apply one part of the change from the design's two plain fenced blocks (shape `[1, 31]`), verify their own files byte-for-byte against the merge-base blob, and commit; Task 4 is a pure acceptance gate that runs the design's own `## Verification` section over the finished, committed tree. Block 0 (the shared Implementer-briefing bullet, byte-identical in both files) is inserted after each pipeline `SKILL.md`'s own `Baseline` anchor — a **hand-mirrored pair**, not machine-checked by `scripts/check-sync.py`, so both insertions move together in one task. Block 1 (the 31-line ADR) is written as the created `docs/adr/0005-…md`. Both plugin versions bump one minor past `origin/main`. There is no source code and no test framework — the design's mechanical/derived checks are the whole correctness surface, so this plan dogfoods the very rule it lands.

**Tech Stack:** Markdown skill files, two small JSON manifests, and `python3` helper scripts (`scripts/design_blocks.py` for `read_blocks`, `scripts/verify_blob.py` for `blob`/`to_lines`/`reconstructed`, `scripts/check-sync.py`, `scripts/check-version-bump.py`); `git` and `claude plugin validate .` for verification.

## Global Constraints

> **This section is orientation for a human reader and reaches no implementer.** `scripts/task-brief` hands each implementer ONLY the text between its own `## Task N` heading and the next `## Task` heading — this `## Global Constraints` section is stripped and never delivered. Nothing here is load-bearing: **every task below re-states, inside its own body, every path, block, anchor, command and clause it needs.** (That property is exactly what this change is about.)

- **Repo:** a Claude Code plugin marketplace — Markdown plus a couple of `python3` scripts, **no test framework**. There is no red/green TDD; each task's "test" is its mechanical/derived check, run red before the edit and green after.
- **CWD:** every command in every task runs from the repo root `/Users/taylor/dev/claude-plugins`. The `python3` blocks resolve `sys.path.insert(0, "scripts")` and their `docs/…` and `plugins/…` paths relative to it; from any other directory they fail to resolve.
- **Design doc (authoritative source of both edit blocks AND the acceptance-gate Verification):** `/Users/taylor/dev/claude-plugins/docs/superpowers/specs/2026-08-05-gh-65-brief-plan-path-design.md`. Its plain fenced blocks are shape `[1, 31]`: **block 0** (1 line) is the shared Implementer-briefing bullet inserted into both files; **block 1** (31 lines) is the ADR body.
- **Never retype block 0 or block 1.** Every task obtains their exact bytes only via `read_blocks(DESIGN, [1, 31])` (`sys.path.insert(0, "scripts")`), which is itself the shape guard — it exits non-zero if the design's plain-block shape ever moves off `[1, 31]`. Retyping either block is a defect.
- **Command discipline:** every computed git ref (the merge base) is captured inside `python3`/`subprocess`, validated non-empty, and passed to `git` as an `argv` element — never an inline `$(git …)`, which word-splits an empty ref into a different valid command.
- **Version bump:** both touched plugins bump their `version` minor segment **past `origin/main`** — expected `dev-flow` `2.16.0 → 2.17.0` and `dev-flow-worktree` `1.18.0 → 1.19.0`, re-confirmed against `origin/main` at apply time (a concurrent branch may have published these numbers first).
- **Setup / branch / integration:** work in place in the current checkout on branch `tayl0r/gh-65-brief-plan-path` (already checked out). Do **not** create a worktree or branch, do not push, do not open a PR, do not merge, do not run a final whole-branch review. The pipeline owns every stage transition. The design and this plan under `docs/superpowers/` are committed by the pipeline (`docs: commit`); **no task edits them,** and every scope check excludes that directory.

---

## Task 1: Insert the Implementer-briefing bullet (block 0) into both pipeline `SKILL.md` files

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md` (insert one line after its `Baseline` anchor)
- Modify: `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` (insert the same line after its own `Baseline` anchor)
- Test: none — this repo has no test framework. The check is the program in Steps 1 and 3.

**Interfaces:**
- Consumes: **block 0** of the design at `/Users/taylor/dev/claude-plugins/docs/superpowers/specs/2026-08-05-gh-65-brief-plan-path-design.md`, read through `read_blocks(DESIGN, [1, 31])[0][0]`. Read this block verbatim from the design file at that path; never reconstruct or substitute it; if you cannot read the design file, stop and report.
- Produces: both pipeline `SKILL.md` files carrying block 0 as the line immediately after their own `Baseline` anchor, each byte-for-byte its merge-base blob with only that one line added. Task 4's whole-tree scope check relies on exactly these two paths (among the five) having changed.

**Run every command in this task from the repo root `/Users/taylor/dev/claude-plugins`.**

**What the edit is:** block 0 becomes a **new bullet immediately after each file's own `Baseline` anchor** — the first Stage 3 override in that list. The two files are a **hand-mirrored pair that `check-sync.py` does not compare**, so a one-sided edit is caught by nothing mechanical; both insertions therefore move together in this one task, and block 0 is byte-identical in both. Each file's anchor differs (dev-flow's names the checkout, worktree's names the pipeline worktree), so each insertion is located by a **content match on its own anchor's stable ASCII prefix**, asserted to occur exactly once — never by line number. The applier is idempotent (a re-run that finds block 0 already after the anchor makes no change). Task 4's design-conformance check re-verifies placement against the design's **exact full `Baseline` anchor** on the finished tree.

- [x] **Step 1: Confirm the design's block shape, then run the red check.**

The shape smoke-test must print `shape: [1, 31]`. The conformance program then confirms block 0 is **not yet** the byte-for-byte reconstruction after each anchor — expect `task 1 conformance: FAIL` and `exit=1` (its demonstrated red form: the working tree still equals the base blob, so block 0 is absent).

```bash
python3 scripts/design_blocks.py docs/superpowers/specs/2026-08-05-gh-65-brief-plan-path-design.md   # expect: shape: [1, 31]
```

```bash
python3 - <<'PY'
import subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
from verify_blob import blob, to_lines, reconstructed

DESIGN = "docs/superpowers/specs/2026-08-05-gh-65-brief-plan-path-design.md"
b0, b1 = read_blocks(DESIGN, [1, 31])          # [1,31] guards the shape; b0[0] is the shared bullet
BULLET = b0[0]
TARGETS = [
    ("plugins/dev-flow/skills/dev-flow/SKILL.md",
     "- **Baseline:** branch entry has already ensured setup"),
    ("plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md",
     "- **Baseline:** worktree entry has already ensured setup"),
]

def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout

base = git("merge-base", "origin/main", "HEAD").strip()
if not base:
    raise SystemExit("empty merge-base -- refusing to run a base-relative check")

bad = []
for path, prefix in TARGETS:
    base_bytes = blob(base, path)
    lines = to_lines(base_bytes)
    at = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    if len(at) != 1:
        bad.append("%s: Baseline anchor prefix matched %d lines at base, want 1" % (path, len(at)))
        continue
    expected = lines[:at[0] + 1] + [BULLET] + lines[at[0] + 1:]
    for p in reconstructed(path, expected, base_bytes):
        bad.append("%s: %s" % (path, p))
for why in bad:
    print("MISMATCH:", why)
print("task 1 conformance:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

- [x] **Step 2: Apply the edit — insert block 0 after each file's `Baseline` anchor.**

The applier reads block 0 from the design (never retyped), locates each file's anchor by its unique ASCII prefix, asserts the prefix matches exactly one line, and inserts the bullet directly after it. Expect one `inserted block 0 immediately after the Baseline anchor` line per file.

```bash
python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-05-gh-65-brief-plan-path-design.md"
b0, b1 = read_blocks(DESIGN, [1, 31])
BULLET = b0[0]
TARGETS = [
    ("plugins/dev-flow/skills/dev-flow/SKILL.md",
     "- **Baseline:** branch entry has already ensured setup"),
    ("plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md",
     "- **Baseline:** worktree entry has already ensured setup"),
]

for path, prefix in TARGETS:
    lines = Path(path).read_text(encoding="utf-8").split("\n")
    at = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    if len(at) != 1:
        raise SystemExit("%s: Baseline anchor prefix matched %d lines, want exactly 1" % (path, len(at)))
    i = at[0]
    if i + 1 < len(lines) and lines[i + 1] == BULLET:
        print("%s: block 0 already after the anchor; leaving as-is" % path)
        continue
    lines.insert(i + 1, BULLET)
    Path(path).write_text("\n".join(lines), encoding="utf-8")
    print("%s: inserted block 0 immediately after the Baseline anchor" % path)
PY
echo "exit=$?"
```

- [x] **Step 3: Run the green check — re-run the Step 1 conformance program verbatim.**

Re-run the exact `python3 - <<'PY' … PY` conformance block from Step 1 (the shape smoke-test above it is optional to repeat). Expect `task 1 conformance: OK` and `exit=0`. This proves, per file: the working tree is byte-for-byte its merge-base blob with block 0 spliced immediately after the (unique) `Baseline` anchor and **nothing else moved** — the byte comparison covers a lost final newline and a CRLF flip the line list cannot see.

- [x] **Step 4: Commit.**

```bash
git add plugins/dev-flow/skills/dev-flow/SKILL.md \
        plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
git commit -m "gh-65: Stage 3 hands each implementer the plan path (both pipeline SKILL.md files)" \
           -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 2: Create ADR 0005 (block 1)

**Files:**
- Create: `docs/adr/0005-implementer-briefs-carry-the-plan-path.md` (content = block 1, verbatim)
- Test: none — the check is the program in Steps 1 and 3.

**Interfaces:**
- Consumes: **block 1** (31 lines) of the design at `/Users/taylor/dev/claude-plugins/docs/superpowers/specs/2026-08-05-gh-65-brief-plan-path-design.md`, read through `read_blocks(DESIGN, [1, 31])[1]`. Read this block verbatim from the design file at that path; never reconstruct or substitute it; if you cannot read the design file, stop and report.
- Produces: the created ADR whose bytes equal block 1 joined with `"\n"` plus a single trailing newline. Task 4's whole-tree scope check relies on exactly this path (among the five) being newly created; nothing in this task depends on Task 1.

**Run every command in this task from the repo root `/Users/taylor/dev/claude-plugins`.**

**What the edit is:** the file is **created** (absent at the merge base). Its content is block 1, read from the design and written as `("\n".join(b1) + "\n")` bytes — each of block 1's 31 paragraphs is one physical line; the reader's `[1, 31]` shape guard fails loudly if the design's ADR block ever drifts off 31 lines. The next free ADR number is **0005** (`docs/adr/` holds 0001–0004). The writer is idempotent (writing the same deterministic bytes again is a no-op in content).

- [x] **Step 1: Confirm the design's block shape, then run the red check.**

The shape smoke-test must print `shape: [1, 31]`. The conformance program then confirms the ADR is **not yet** present with block 1's bytes — expect `task 2 conformance: FAIL` and `exit=1` (its red form: the file does not exist yet).

```bash
python3 scripts/design_blocks.py docs/superpowers/specs/2026-08-05-gh-65-brief-plan-path-design.md   # expect: shape: [1, 31]
```

```bash
python3 - <<'PY'
import subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-05-gh-65-brief-plan-path-design.md"
b0, b1 = read_blocks(DESIGN, [1, 31])          # [1,31] guards the shape; b1 is the 31-line ADR
ADR = "docs/adr/0005-implementer-briefs-carry-the-plan-path.md"
want_bytes = ("\n".join(b1) + "\n").encode("utf-8")

def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout

base = git("merge-base", "origin/main", "HEAD").strip()
if not base:
    raise SystemExit("empty merge-base -- refusing to run a base-relative check")

bad = []
absent = subprocess.run(("git", "cat-file", "-e", "%s:%s" % (base, ADR)), capture_output=True)
if absent.returncode == 0:
    bad.append("%s: expected absent at merge-base, but it exists there" % ADR)
p = Path(ADR)
if not p.exists():
    bad.append("%s: file not created" % ADR)
elif p.read_bytes() != want_bytes:
    bad.append("%s: working-tree bytes != block 1 joined with a trailing newline" % ADR)
for why in bad:
    print("MISMATCH:", why)
print("task 2 conformance:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

- [x] **Step 2: Apply the edit — write the ADR from block 1.**

The writer reads block 1 from the design (never retyped) and writes it as the new file's exact bytes. Expect `wrote docs/adr/0005-implementer-briefs-carry-the-plan-path.md (31 lines from block 1)`.

```bash
python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-05-gh-65-brief-plan-path-design.md"
b0, b1 = read_blocks(DESIGN, [1, 31])
ADR = "docs/adr/0005-implementer-briefs-carry-the-plan-path.md"
want_bytes = ("\n".join(b1) + "\n").encode("utf-8")
Path(ADR).write_bytes(want_bytes)
print("wrote %s (%d lines from block 1)" % (ADR, len(b1)))
PY
echo "exit=$?"
```

- [x] **Step 3: Run the green check — re-run the Step 1 conformance program verbatim.**

Re-run the exact `python3 - <<'PY' … PY` conformance block from Step 1 (the shape smoke-test above it is optional to repeat). Expect `task 2 conformance: OK` and `exit=0`: the file exists, its bytes equal block 1 joined with a trailing newline, and it was absent at the merge base (so it is genuinely created, not a stray already-tracked file).

- [x] **Step 4: Commit.**

```bash
git add docs/adr/0005-implementer-briefs-carry-the-plan-path.md
git commit -m "gh-65: ADR 0005 — Execute stage carries the plan path so out-of-section references resolve" \
           -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 3: Bump both plugin versions past `origin/main`

**Files:**
- Modify: `plugins/dev-flow/.claude-plugin/plugin.json` (one `"version"` line)
- Modify: `plugins/dev-flow-worktree/.claude-plugin/plugin.json` (one `"version"` line)
- Test: none — the checks are the programs in Steps 2 and 4.

**Interfaces:**
- Consumes: nothing from Tasks 1–2 except that both plugins' shipped text has already changed, which is what obliges the bump — `dev-flow`'s pipeline `SKILL.md` changed in Task 1, and `dev-flow-worktree`'s changed in Task 1 too, so both plugin directories are touched. This task reads no other task's text.
- Produces: `plugins/dev-flow/.claude-plugin/plugin.json` at `"version": "2.17.0"` and `plugins/dev-flow-worktree/.claude-plugin/plugin.json` at `"version": "1.19.0"`, each byte-for-byte its merge-base blob with only the version value swapped. Task 4's design-conformance and check-version-bump gate rely on these committed values.

**Run every command in this task from the repo root `/Users/taylor/dev/claude-plugins`.** Run this task **after** Tasks 1 and 2 are committed. **Do not reformat the JSON** — the edit is a single-line string replacement; re-serializing with `json.dump` would rewrite the whole file and put a stray reformat into scope.

**What the edit is:** each `plugin.json`'s `version` minor segment bumps by one, **derived from that plugin's `origin/main` version at apply time**, so it is guaranteed past `origin/main` even if a concurrent branch already advanced it. Expected result: `dev-flow` `2.16.0 → 2.17.0`, `dev-flow-worktree` `1.18.0 → 1.19.0`. **If `origin/main` has advanced so the natural bump is not `2.17.0` / `1.19.0`, the applier HALTS and reports** — because the design's `## Verification` hardcodes the `2.16.0 → 2.17.0` / `1.18.0 → 1.19.0` pair against the merge-base blob, so a concurrent publish is a design-owner re-confirmation, not an implementer improvisation. The bumper selects the unique `"version"` line by content, edits only that line, and is idempotent.

- [ ] **Step 1: Refresh `origin/main`, then apply both bumps.**

`git fetch origin main` first so the bump derives from and validates against the true remote tip (a resumed run may otherwise see a stale ref). Expect two `… -> …` lines, e.g. `plugins/dev-flow/.claude-plugin/plugin.json: 2.16.0 -> 2.17.0` and `plugins/dev-flow-worktree/.claude-plugin/plugin.json: 1.18.0 -> 1.19.0`. The applier works in two passes — it validates every file and computes both targets first, and only then writes — so if `origin/main` has advanced and the HALT fires, no file has been modified (no half-applied bump left in the tree).

```bash
python3 - <<'PY'
import subprocess, json, re, sys
from pathlib import Path

def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout

EXPECTED = {
    "plugins/dev-flow/.claude-plugin/plugin.json": "2.17.0",
    "plugins/dev-flow-worktree/.claude-plugin/plugin.json": "1.19.0",
}
git("fetch", "origin", "main")

# Pass 1 -- validate every file and compute both targets; write nothing, so a
# HALT here leaves the working tree untouched (no half-applied bump).
plan = []
for f, expected_new in sorted(EXPECTED.items()):
    base_ver = json.loads(git("show", "origin/main:%s" % f))["version"]
    a, b, c = base_ver.split(".")
    new_ver = "%s.%d.%s" % (a, int(b) + 1, c)                 # minor bump, past origin/main
    if new_ver != expected_new:
        raise SystemExit(
            "%s: origin/main is %s, so the natural minor bump is %s, not the design's %s. "
            "A concurrent branch advanced origin/main; the design hardcodes the %s pair in "
            "its Verification against the merge-base blob, so re-confirm the design's targets "
            "before proceeding -- stop and report." % (f, base_ver, new_ver, expected_new, expected_new))
    text = Path(f).read_text(encoding="utf-8")
    cur_ver = json.loads(text)["version"]
    if tuple(map(int, cur_ver.split("."))) >= tuple(map(int, new_ver.split("."))):
        plan.append((f, cur_ver, new_ver, None)); continue    # already at/past target; nothing to write
    lines = text.split("\n")
    vlines = [i for i, l in enumerate(lines) if '"version"' in l]
    if len(vlines) != 1:
        raise SystemExit("%s: found %d '\"version\"' lines, want exactly 1" % (f, len(vlines)))
    i = vlines[0]
    new_line = re.sub(r'("version"\s*:\s*")[^"]*(")',
                      lambda m: m.group(1) + new_ver + m.group(2), lines[i])
    if new_line == lines[i]:
        raise SystemExit("%s: version substitution changed nothing" % f)
    lines[i] = new_line
    plan.append((f, cur_ver, new_ver, lines))

# Pass 2 -- every file validated and every target computed; apply the writes.
for f, cur_ver, new_ver, lines in plan:
    if lines is None:
        print("%s: already at %s (>= target %s); leaving" % (f, cur_ver, new_ver)); continue
    Path(f).write_text("\n".join(lines), encoding="utf-8")
    print("%s: %s -> %s" % (f, cur_ver, new_ver))
PY
echo "exit=$?"
```

- [ ] **Step 2: Verify both versions are strictly greater than `origin/main`, and byte-for-byte otherwise unchanged.**

The program re-reads `origin/main`, and for each file asserts: (a) the working-tree version, compared as a **tuple of integers** (not a string — `"2.10.0" > "2.9.0"` is false lexically once the minor reaches two digits, though 2.10.0 is the newer version), is strictly greater than `origin/main`'s; and (b) the file is byte-for-byte its merge-base blob with **only** the version value swapped. Expect `task 3 conformance: OK` and `exit=0`. Run before Step 1 it prints a `not strictly greater` mismatch per plugin (the working tree still equals the base version) and exits 1.

```bash
python3 - <<'PY'
import subprocess, json, re, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from verify_blob import blob, to_lines, reconstructed

def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout

PLUGINS = ["plugins/dev-flow/.claude-plugin/plugin.json",
           "plugins/dev-flow-worktree/.claude-plugin/plugin.json"]
git("fetch", "origin", "main")
base = git("merge-base", "origin/main", "HEAD").strip()
if not base:
    raise SystemExit("empty merge-base -- refusing to run a base-relative check")

bad = []
for f in PLUGINS:
    base_bytes = blob(base, f)
    lines = to_lines(base_bytes)
    vlines = [i for i, l in enumerate(lines) if '"version"' in l]
    if len(vlines) != 1:
        bad.append("%s: %d version lines at base, want 1" % (f, len(vlines))); continue
    i = vlines[0]
    cur_ver = json.loads(Path(f).read_text(encoding="utf-8"))["version"]
    new_line = re.sub(r'("version"\s*:\s*")[^"]*(")',
                      lambda m: m.group(1) + cur_ver + m.group(2), lines[i])
    expected = lines[:i] + [new_line] + lines[i + 1:]
    for p in reconstructed(f, expected, base_bytes):
        bad.append("%s: %s" % (f, p))
    published = json.loads(git("show", "origin/main:%s" % f))["version"]
    if tuple(map(int, cur_ver.split("."))) <= tuple(map(int, published.split("."))):
        bad.append("%s: version %s is not strictly greater than origin/main's %s"
                   % (f, cur_ver, published))
for why in bad:
    print("MISMATCH:", why)
print("task 3 conformance:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

- [ ] **Step 3: Commit.**

```bash
git add plugins/dev-flow/.claude-plugin/plugin.json \
        plugins/dev-flow-worktree/.claude-plugin/plugin.json
git commit -m "gh-65: bump dev-flow 2.17.0 and dev-flow-worktree 1.19.0" \
           -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

- [ ] **Step 4: Confirm the bump is registered (runs AFTER the Step 3 commit).**

`check-version-bump.py` reads each plugin's **committed** version via `git show HEAD:…plugin.json`, so it can only see the bump once it is committed — run it *after* Step 3, never before (before, it compares `origin/main`'s version against the still-unbumped committed HEAD and reports FAIL, a staleness artifact, not a real collision). Expect it to pass (both touched plugins now ahead of `origin/main`).

```bash
python3 scripts/check-version-bump.py origin/main
echo "exit=$?"
```

---

## Task 4: Run the design's `## Verification` as the acceptance gate, then hand off the pre-merge re-check

**Files:** none modified. This task is the acceptance gate over the finished, fully-committed tree.

**Interfaces:**
- Consumes: the finished tree from Tasks 1–3 (all five files committed), and the design's own `## Verification` section, read from disk below.
- Produces: the pass evidence the pipeline's Execute-stage report carries, plus the pre-merge version re-check hand-off in *After the last task*.

**Run every command in this task from the repo root `/Users/taylor/dev/claude-plugins`.**

**Precondition — all prior tasks committed.** This gate reads committed history. It must run only after Tasks 1, 2, and 3 have each committed, so that HEAD carries all five changed files (`plugins/dev-flow/skills/dev-flow/SKILL.md`, `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`, `docs/adr/0005-implementer-briefs-carry-the-plan-path.md`, `plugins/dev-flow/.claude-plugin/plugin.json`, `plugins/dev-flow-worktree/.claude-plugin/plugin.json`) and none is still uncommitted. If any prior task is not yet committed, stop and report.

**The acceptance gate is the design's own `## Verification` section — run it verbatim.** The design is at:

`/Users/taylor/dev/claude-plugins/docs/superpowers/specs/2026-08-05-gh-65-brief-plan-path-design.md`

Read its `## Verification` section verbatim from the design file at that path; run each of its four numbered checks exactly as written; never reconstruct, retype, or substitute any of them; if you cannot read the design file, stop and report. That section's `python`/`sh` blocks re-read blocks 0 and 1 from the design through `read_blocks(DESIGN, [1, 31])`, compute the base as `git merge-base origin/main HEAD` (captured, validated non-empty, passed to `git` as an `argv` element — never shell-interpolated), and are already consistent at shape `[1, 31]`; they are the whole correctness surface for this change and supersede the per-task checks, which each ran before the next task's edits.

- [ ] **Step 1: Run the design's `## Verification` check 1 — Design-block conformance.**

Run, verbatim from the design's `## Verification`, its check **1. Design-block conformance** — the `python3 scripts/design_blocks.py …` shape smoke-test (expect `shape: [1, 31]`) followed by its `python` block. It asserts block 0 is the line immediately after **each file's exact full `Baseline` anchor** and that the created ADR's content equals block 1. Expect `design-conformance: OK` and exit 0. This is the finished-tree, exact-anchor re-check of Tasks 1 and 2.

- [ ] **Step 2: Run the design's `## Verification` check 2 — Byte-for-byte blob + file scope.**

Run, verbatim from the design's `## Verification`, its check **2. Byte-for-byte blob check + file scope**. It compares `merge-base..HEAD`, so it is a **committed-HEAD check** and only runs correctly now that Tasks 1–3 are committed; it guards itself onto the feature branch (asserts `merge-base != HEAD`) and asserts the changed set — excluding `docs/superpowers/` — equals exactly the five files, each byte-for-byte its base blob with only its intended edit, and the ADR absent at base and equal to block 1. Expect `file scope + byte-for-byte: OK` and exit 0. This is the only check that proves **no other line anywhere moved** — the doubled-hunk blind spot the hand-mirrored pair cannot otherwise catch.

- [ ] **Step 3: Run the design's `## Verification` check 3 — Removed-phrase grep.**

Run, verbatim from the design's `## Verification`, its check **3. Removed-phrase grep** — the two file-scoped `git grep -F` commands for the old version literals (`"version": "2.16.0"` scoped to `plugins/dev-flow/.claude-plugin/plugin.json`, `"version": "1.18.0"` scoped to `plugins/dev-flow-worktree/.claude-plugin/plugin.json`). Expect **0 matches** each (the literals were 1 each at base). The `SKILL.md` insertions and the created ADR remove no prose, so the grep is N/A for those three files, as the design states.

- [ ] **Step 4: Run the design's `## Verification` check 4 — Sync, version-bump, and marketplace validation.**

Run, verbatim from the design's `## Verification`, its check **4**: `python3 scripts/check-sync.py` (expect pass — the `adversarial-review` pairs and author counts are untouched, and the pipeline `SKILL.md` pair is hand-mirrored, not compared), `python3 scripts/check-version-bump.py origin/main` (a **committed-HEAD check**, expect pass now that Task 3 is committed), and `claude plugin validate .` (expect exit 0 with exactly the expected author-less warnings — **do NOT add author keys**).

- [ ] **Step 5: Confirm nothing is uncommitted in scope (belt-and-braces beyond the design's Verification).**

The check-2 scope equality reads `merge-base..HEAD` and so cannot see an *uncommitted* stray file in scope. This closes that gap. Expect **no output** and `exit=0`; any line printed is an uncommitted or untracked file inside the change's scope — report it rather than committing it, since the five authorized files are already committed.

```bash
git status --porcelain -- . ':!docs/superpowers/'
echo "exit=$?"
```

- [ ] **Step 6: Hand the pre-merge version re-check to the orchestrator.**

This is the last checkbox in the plan. Do **not** attempt the pre-merge re-check yourself — it runs at a stage boundary that has not happened. Report to the orchestrator, in the Execute-stage completion report, the whole of the *After the last task* section below, and say plainly that it is outstanding.

---

## After the last task: the `pre-merge` version re-check

**This is prose addressed to the orchestrator, and it is deliberately not a `- [ ]` checkbox.** Every checkbox above is completable inside the Execute stage; this is not. It runs at a **stage boundary** — after the *last* merge or rebase of `origin/main` into this branch, immediately before the pipeline halts at `pre-merge` (the design's front-matter declares `stops: [pre-merge]`). **Nothing mechanically detects it being skipped:** there is no CI check, no hook, no artifact whose absence is noticed. Treat a criteria pass reported without it as incomplete.

**What to run:** the design's `## Verification` check **4**'s `python3 scripts/check-version-bump.py origin/main`, unchanged — re-fetching `origin/main` and re-comparing. It is idempotent and re-runnable.

**Why re-running it is not redundant.** Two branches writing the byte-identical `"version": "2.17.0"` (or `"1.19.0"`) line **auto-resolve on merge with no conflict** and produce no version change at all — the incident where a concurrent PR lands the same number first, and the merge silently yields no bump. The execute-time run cannot see a concurrent PR that lands after it; only a re-run against a freshly re-fetched `origin/main` at the stage boundary catches it, via the strict `>` comparison `check-version-bump.py` makes.

**If it fails:** re-target both versions upward — bump each minor past the freshly re-fetched `origin/main` — and re-run. Re-running Task 3's Steps 1–2 after such a re-target is worthwhile; the version files are in scope for both.

**Where it must be reported:** in the `pre-merge` halt report, named as run with its output, or named as outstanding. Do not report the criteria pass as complete without it.

---

## Self-review

**Spec coverage.** Every one of the design's five touched files has a task: block 0 into both pipeline `SKILL.md`s → Task 1; the created ADR (block 1) → Task 2; both `plugin.json` bumps → Task 3. The design's entire `## Verification` section (its four numbered checks) is run in full by Task 4, verbatim from the design. The design decides every placement, anchor, block, and version target; no task re-opens any of it.

**Every `## Task N` section is self-sufficient under `scripts/task-brief`.** The brief hands each implementer only the text between its own task heading and the next, with no plan-file path and nothing from `## Global Constraints`. So each task re-states, inside its own body, its CWD (repo root), the design's absolute path, the read-verbatim clause, the block index it reads through `read_blocks(DESIGN, [1, 31])`, its own anchor prefix, the applier, the check, and the commit. **No task leans on `## Global Constraints`, a shared block, another task's output, or a `§`/`§V` ID.** There is no out-of-section reference I could not give an in-section pointer for, so no halt is warranted.

**How the final Verification task resolves its blocks from within its own section.** Task 4 does not retype the design's Verification. It names the design by absolute path inside its own section and carries the read-verbatim clause (*read the `## Verification` section verbatim from the design file at that path; run each check exactly as written; never reconstruct or substitute; if you cannot read the design file, stop and report*), then enumerates the four checks, their committed-HEAD run order (checks 2 and 4's `check-version-bump` run after all commits), and the expected pass output of each. The pointer and clause live entirely in Task 4's section, so it is resolvable from the brief alone — this reuses the design's already-consistent Verification python (one source of truth, no transcription risk) rather than a retyped copy.

**Never retype block text.** No task contains block 0 or block 1 as pasted prose. Every content edit is applied by a `python3` step that reads the block from the design on disk via `read_blocks(DESIGN, [1, 31])` and splices/writes it; insertion points are located by a content match on each file's own `Baseline` anchor prefix (asserted unique), never by line number. The `[1, 31]` argument is itself the shape guard.

**Committed-HEAD ordering.** Task 3's `check-version-bump.py origin/main` (Step 4) runs after its own commit (Step 3). Task 4's check 2 (`merge-base..HEAD`) and check 4's `check-version-bump.py` run only after Tasks 1–3 are all committed. No step reading committed history runs before the commit it depends on.

**Command discipline.** Every program captures the merge base inside `python3`/`subprocess`, validates it non-empty, and passes it to `git` as an `argv` element; no command uses an inline `$(git …)` substitution. The removed-phrase greps (design check 3) are file-scoped literals, not computed refs.

**Placeholders / consistency.** None. Every step is a runnable command with its expected output; the only text not spelled out is blocks 0 and 1, read from the design by every program that needs them — which is the defect this whole change is about. The design path, block shape `[1, 31]`, ADR filename (`0005-implementer-briefs-carry-the-plan-path.md`), version targets (`2.17.0` / `1.19.0`), the five touched files, and the two anchor prefixes agree across all four tasks and match the design.
