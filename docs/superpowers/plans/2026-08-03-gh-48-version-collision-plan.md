---
dev-flow:
  slug: gh-48-version-collision
  spec: docs/superpowers/specs/2026-08-03-gh-48-version-collision-design.md
---

# gh-48 version collision — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use markdown checkbox syntax for tracking.

**Goal:** Land a new `scripts/check-version-bump.py`, a new `.github/workflows/check-version-bump.yml` that runs it on every pull request against the base branch's tip, and one appended sentence-pair on `CLAUDE.md` line 7 — so that a plugin whose directory a change touches can no longer ship a version `main` has already published.

**Architecture:** The design (`docs/superpowers/specs/2026-08-03-gh-48-version-collision-design.md`) gives **both new files in full** and the `CLAUDE.md` replacement line in full, as plain (untagged) fenced blocks of shape `[155, 18, 1]`. It also decides the predicate, the trigger, the file layout, and every rejected alternative. **No task re-derives or re-decides any of that, and no task retypes a single byte of it.** Every task obtains its content by reading the blocks off the design on disk through the shared reader `scripts/design_blocks.py`, writes them positionally, and then re-derives from git that each touched file is byte-for-byte its merge-base blob (nothing, for a file it creates) with exactly the intended edit applied. Tasks are drawn one per file, in dependency order — the script first, because the workflow invokes it by path and `CLAUDE.md` names it; the workflow second; the one-line doc edit third — so that no commit references a path that does not yet exist. Task 4 is the acceptance gate, and it re-runs nothing an earlier task already settled: Task 1 proves the shipped script's *behaviour* (criteria 3, 4, 5, 10) and Task 4's criterion 2 proves the file on disk is still block 0 byte for byte, so the behaviour proven there is the behaviour of the artifact being pushed. What Task 4 adds is what only the finished tree can show — criteria 1, 2 and 6 over the assembled tree, criteria 8 and 9 for the repo's standing checks, that nothing in scope is left uncommitted, and the hand-off of criteria 7 and 11 to the orchestrator, because those two cannot run until a PR exists with a completed CI run.

**Tech Stack:** Python 3 stdlib only (the shipped script imports `json`, `subprocess`, `sys`), GitHub Actions YAML, Markdown. **There is no test framework in this repo.** The whole check suite is `python3 scripts/check-sync.py`, `claude plugin validate .` (exit 0 with exactly 8 `No author information provided` warnings), and the design's *Success criteria*, which Tasks 1–4 run in full between them — 3, 4, 5, 6 and 10 in Task 1, 1 and 2 in Task 3 and again in Task 4, 6, 8 and 9 in Task 4, 0 by every `read_blocks` call, and 7 and 11 as prose in *After the last task*.

## Global Constraints

Every task's requirements implicitly include this section.

**1. Three files, and no fourth.** These are the only files any task may create or modify:

| # | File | Edit |
|---|---|---|
| 1 | `scripts/check-version-bump.py` | **created** from design block **0** (155 lines) |
| 2 | `.github/workflows/check-version-bump.yml` | **created** from design block **1** (18 lines) |
| 3 | `CLAUDE.md` | line **7** replaced in full by design block **2** (1 line) |

The design and this plan under `docs/superpowers/` are committed by the pipeline (`docs: commit`); **no task edits them either**, and every scope check below excludes that directory with a `':!docs/superpowers/'` pathspec.

**Hard-excluded, per the design's *Out of scope*:** everything under `plugins/`, every `.claude-plugin/` directory and every `plugin.json`, `scripts/check-sync.py`, `scripts/design_blocks.py`, `.github/workflows/check-sync.yml` (which must stay **byte-identical**), `.claude-plugin/marketplace.json`, `CONTEXT.md`, and `docs/adr/`. Each is a decided conclusion in the design, not a deferral. **A task that appears to need one of them is a blocker to report — stop and report it; do not work around it, and do not edit the file.** `scripts/design_blocks.py` is *used* by every task and *modified* by none.

**2. No `plugin.json` version is bumped, and that is a conclusion, not an oversight.** `CLAUDE.md`'s standing rule is *bump `version` on any behavior change* — but this change touches **no plugin directory at all**, so there is no plugin whose behavior changed and no version to move (design **A5**). The consequence is stated in the design and must not be treated as a gap: **this PR's own new check passes vacuously** (*Success criteria* 6), which is exactly why criteria 3, 5 and 10 exist — they exercise the check against history and against a synthetic repository instead of against this PR's green run. **If any step here appears to ask for a version bump, that is a blocker: stop and report.**

**3. File content is read from the design, never retyped.** Both new files and the replacement line live only in the design. Every task that writes or checks one obtains it by running:

```sh
python3 scripts/design_blocks.py docs/superpowers/specs/2026-08-03-gh-48-version-collision-design.md
```

to confirm the shape, and then, inside its own program, `sys.path.insert(0, "scripts")` followed by `read_blocks(DESIGN, [155, 18, 1])`. The design's plain fenced blocks are indices **0, 1, 2** with shape **`[155, 18, 1]`**. `read_blocks` takes the shape as a required argument and exits non-zero if it moved; the CLI above only *reports* the shape and always exits 0, so it is a convenience, never the guard. Identifying prefixes only, so you know which is which:

- **block 0**, 155 lines, first line `#!/usr/bin/env python3` — the complete `scripts/check-version-bump.py`.
- **block 1**, 18 lines, first line `name: check-version-bump` — the complete `.github/workflows/check-version-bump.yml`.
- **block 2**, 1 line, starting `- **Bump \`version\` in \`plugins/<name>/.claude-plugin/plugin.json\`` — the complete new `CLAUDE.md` line 7.

If `read_blocks` raises `design code-block shape is …, want [155, 18, 1]`, **stop and report**: the design was edited after this plan captured its shape, and every index and length below is unreliable.

**Retyping any block is a defect**, not a shortcut — 155 lines of Python transcribed by hand is the single most likely way this change ships wrong, and `git diff` cannot flag it because a wrong byte in a new file looks exactly like a right one.

**4. Every verification obeys this repo's rules.** They are in `CLAUDE.md`'s *Verifying a change* and in the pipeline's *Command discipline*:

- **A criterion must be able to fail.** No `--stat`. No human-read output standing in for an assertion. No step unreachable behind an earlier short-circuit — every program below collects all mismatches into a list and prints them before exiting.
- **A step consuming a computed git ref passes it to `git` as an `argv` element from `python3`/`subprocess`.** **No command in this plan uses an inline `$(git …)` substitution** — the form appears only in this sentence and its restatement under *Self-review*, which quote it. A ref pinned to a **literal** SHA is not a computed ref and stays writable as one line of shell; that is why the criteria that name `963a66c`, `84d8cc9`, `5f99cf2`, `02ffb7b`, `c28a613` and `1f359e2` do so as literals.
- **Every measurement stated is printed by a command given beside it**, and no number is stated that the output does not show.
- **The `Always:` rule's two halves.** The removed-phrase grep and the merge-base reconstruction both apply. Here the first is vacuous by construction and the second stands in for it: block 2 **appends** to line 7 and removes nothing, and two of the three files are created, so there is no phrase to grep for. What replaces it is the assertion that the base line 7 is a strict **prefix** of block 2 — which makes a removal detectable rather than merely unsearched-for — plus the assertion that neither new path existed at the base. Both live in the design's criterion 2, run by Tasks 1, 3 and 4.

**5. Setup, branch and integration.** Work in place in the current checkout. **Do not create a git worktree** and do not invoke `superpowers:using-git-worktrees`. The branch `tayl0r/gh-48-version-collision` already exists and is checked out — do not create or switch branches. Do not push, do not open a PR, do not merge, do not run a final review. The pipeline owns every stage transition.

**6. Do not make the new script executable.** `scripts/check-sync.py` carries the same `#!/usr/bin/env python3` shebang and is mode `100644`, and both the workflow and every criterion invoke the new script as `python3 scripts/check-version-bump.py`. Writing the file with Python's `write_text` under a normal umask gives 644; **do not `chmod +x` it.** Task 1 asserts it — at creation, before any commit could record the wrong mode. `core.fileMode` is `true` in this checkout, so the working-tree bit is exactly what git records; asserting the recorded mode again after the commit would only restate what that first assertion already guarantees.

## Base facts, pinned to `52c3883`

`52c3883` is this branch's base; `git merge-base origin/main HEAD` printed `52c388353c8a89dd9367e083253345c35df4d07b` when this plan was written. Every constant used below was printed at that revision by the command beside it, and the claims are past-tense at that revision. Tasks compute the base rather than hardcoding it, so a base that moved and shifted `CLAUDE.md`'s lines fails loudly instead of editing the wrong line.

**The design's block shape is `[155, 18, 1]`:**

```sh
python3 scripts/design_blocks.py docs/superpowers/specs/2026-08-03-gh-48-version-collision-design.md
```

```text
shape: [155, 18, 1]
  [0] len=155: #!/usr/bin/env python3
  [1] len=18: name: check-version-bump
  [2] len=1: - **Bump `version` in `plugins/<name>/.claude-plugin/plugin.json` on a
```

**Neither new path exists, and nothing in the tree is named `check-version`:**

```sh
git grep -c -F 'check-version' 52c3883
```

No output, exit 1.

**`CLAUDE.md` is 34 lines and its line 7 is the version-bump bullet:**

```sh
git grep -c '' 52c3883 -- CLAUDE.md
```

```text
52c3883:CLAUDE.md:34
```

**All existing scripts and workflows are mode `100644`** — which is why Global Constraint 6 forbids `chmod +x`:

```sh
git ls-files -s scripts/ .github/workflows/ CLAUDE.md
```

```text
100644 b3711dee8b12b547ca41eb6dded40b084feb6fb9 0	.github/workflows/check-sync.yml
100644 b62b306d5b18716ba6866482e424850fe9e86332 0	CLAUDE.md
100644 ddee28c7a23cf5bfa8fa9d8ce9fca52ee2164f05 0	scripts/check-sync.py
100644 ba56549b8af0d4ac490df53a4ef9a4bd2a555418 0	scripts/design_blocks.py
```

**The literal SHAs the criteria name all resolve, and mean what the criteria say they mean:**

```sh
git log -1 --format='%h %s' c28a613
git log -1 --format='%h %s' 'c28a613^'
git log -1 --format='%h %s' 1f359e2
```

```text
c28a613 Add dev-flow plugin
b900f61 Add --prune to fetch commands in sync-latest-git skill
1f359e2 CLAUDE.md: document repo layout, plugin gotchas, and validation (#12)
```

`c28a613` is the *plugin added for the first time* case criterion 3 exercises as a **skip**, and it has a parent, so `c28a613^` resolves. `1f359e2` is the commit that wrote the bump rule, and criterion 5's replay range `1f359e2^..origin/main` starts there.

**Block 2 appends to `CLAUDE.md` line 7 rather than rewriting it, and it names the new script:** both were checked before this plan was written by reading block 2 through `read_blocks` and comparing it to `git show 52c3883:CLAUDE.md`'s seventh line — `block 2 startswith base line 7: True`, `block 2 strictly longer: True`, `block 2 names scripts/check-version-bump.py: True`. Both properties are **asserted, not trusted**: they are the design's criterion 2, run by Tasks 1, 3 and 4.

The post-edit numbers — `CLAUDE.md` still **34 lines**, the two new files at **155** and **18** lines, and the **three-file** scope — are *asserted rather than measured here*: Tasks 1–4's programs fail if any is wrong.

## File Structure

Three files, drawn one per task because each is independently rejectable — a reviewer can accept the script and reject the workflow's trigger, or accept both and reject the `CLAUDE.md` wording — and because the dependency order is strict:

- **`scripts/check-version-bump.py` (Task 1).** The whole correctness surface. It is a standalone tool with no dependency on the other two files, so it lands first and carries every behavioural criterion: the design's criteria 3 (rejects the incident), 4 (failed producers halt), 5 (zero false positives across history), 6 (passes this change vacuously) and 10 (sees paths git would otherwise hide). This is the only task whose deliverable can be exercised red as well as green, and criteria 3 and 10 are the only evidence anywhere that the check catches the bug it was written for — A5 means this PR's own run cannot supply it.
- **`.github/workflows/check-version-bump.yml` (Task 2).** Wiring only. It invokes the script by path, so it lands **after** Task 1 — otherwise its commit references a file that does not exist. Its own two design criteria (7 and 11) need a PR with a completed CI run and cannot run in the Execute stage at all; what Task 2 can and does assert locally is block equality, that the script path the workflow names exists on disk, and that `.github/workflows/check-sync.yml` is byte-identical to its base blob.
- **`CLAUDE.md` (Task 3).** One line, replaced in full by block 2. It names `scripts/check-version-bump.py` as a runnable local command, so it lands after Task 1 too. This is the only file the change *modifies* rather than creates, so it is the only one whose merge-base reconstruction has a non-empty left-hand side, and criterion 2 goes fully green here for the first time.

**Task 4** adds no file change. It is the acceptance gate over the tree that will actually be pushed: the design's *Success criteria* 1, 2 and 6 (the tree is exactly the three authorized files; each is its design block, or its base blob with exactly line 7 replaced; and the shipped script's own verdict on the shipped tree), 8 and 9 (the repo's standing checks still pass), that nothing in scope is left uncommitted, and the hand-off of criteria 7 and 11 to the orchestrator. Criteria 0, 3, 4, 5 and 10 are **not** re-run here: each is a property of `scripts/check-version-bump.py`'s bytes over immutable history, Task 1 established all of them against those bytes, and Step 2's byte equality is what carries them forward to the file that ships.

---

### Task 1: `scripts/check-version-bump.py` from design block 0

**Files:**
- Create: `scripts/check-version-bump.py` — design block **0**, 155 lines, read from disk and never retyped
- Test: none — this repo has no test framework. The checks are the programs in Steps 3–8.

**Interfaces:**
- Consumes: block 0 of `docs/superpowers/specs/2026-08-03-gh-48-version-collision-design.md`, read through `read_blocks(DESIGN, [155, 18, 1])[0]`. Nothing from any other task.
- Produces: `scripts/check-version-bump.py`, a 155-line non-executable Python 3 file with the command-line contract `python3 scripts/check-version-bump.py <base-ref> [<head-ref>]`, exiting 0 when every touched plugin's version is strictly ahead of the base ref's and 1 otherwise. **Task 2's workflow invokes exactly that path with exactly one argument**; **Task 3's `CLAUDE.md` line names exactly that path**; Task 4 re-asserts this file's *bytes* over the finished tree, which is what carries the behavioural results below onto the artifact that ships.

**Why the behavioural criteria live here, and only here:** design **A5** means this change touches no plugin directory, so the check passes vacuously on its own PR. The only evidence it works is criterion 3 (the incident, replayed against literal SHAs), criterion 4 (a failed producer halts), criterion 5 (the false-positive bound across history) and criterion 10 (the synthetic repository). Deferring them to the gate would leave the script's red path unexercised through two more commits. Repeating them at the gate would buy nothing: each is a deterministic function of this file's bytes over history that cannot move, and Task 4's criterion 2 asserts those bytes are unchanged in the shipped tree — so the gate re-establishes the *premise* of these results rather than re-deriving the results.

- [x] **Step 1: Confirm the design's block shape**

Run:

```sh
python3 scripts/design_blocks.py docs/superpowers/specs/2026-08-03-gh-48-version-collision-design.md
```

Expected:

```text
shape: [155, 18, 1]
  [0] len=155: #!/usr/bin/env python3
  [1] len=18: name: check-version-bump
  [2] len=1: - **Bump `version` in `plugins/<name>/.claude-plugin/plugin.json` on a
```

**Anything else: stop and report** — the design moved after this plan captured its shape, and every index and length in this plan is unreliable.

- [x] **Step 2: Create the file from block 0**

The program reads block 0 from the design on disk and refuses to write if the target already exists — which is what a second run, a hand-created file, or a moved base looks like. **Do not type the script's contents.** Run:

```sh
python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-03-gh-48-version-collision-design.md"
TARGET = "scripts/check-version-bump.py"

block = read_blocks(DESIGN, [155, 18, 1])[0]
target = Path(TARGET)
if target.exists():
    raise SystemExit("%s already exists; this change creates it -- already applied, "
                     "hand-created, or the base moved; stop and report" % TARGET)
target.write_text("\n".join(block) + "\n", encoding="utf-8")
print("created %s, %d lines, first line %r" % (TARGET, len(block), block[0]))
PY
echo "exit=$?"
```

Expected: `created scripts/check-version-bump.py, 155 lines, first line '#!/usr/bin/env python3'` and `exit=0`.

- [x] **Step 3: Verify the file is its design block, is not executable, did not exist at the base, and is the only change**

Every mismatch is collected and printed before exit, so a first failure never hides a second. Run:

```sh
python3 - <<'PY'
import subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-03-gh-48-version-collision-design.md"
SCRIPT = "scripts/check-version-bump.py"
SCOPE = ["--", ".", ":!docs/superpowers/"]
WANT_SCOPE = [SCRIPT]

def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout

def split(text):
    out = text.split("\n")
    if out and out[-1] == "":
        out.pop()
    return out

block = read_blocks(DESIGN, [155, 18, 1])[0]
base = git("merge-base", "origin/main", "HEAD").strip()
print("base:", base)
bad = []

if subprocess.run(("git", "cat-file", "-e", "%s:%s" % (base, SCRIPT)),
                  capture_output=True).returncode == 0:
    bad.append("%s already existed at the base; this change creates it" % SCRIPT)
p = Path(SCRIPT)
if not p.is_file():
    bad.append("%s does not exist on disk; this change creates it from design block 0" % SCRIPT)
else:
    on_disk = split(p.read_text(encoding="utf-8"))
    print("%s: %d lines" % (SCRIPT, len(on_disk)))
    if on_disk != block:
        bad.append("%s is not design block 0 verbatim (%d lines on disk, %d in the block)"
                   % (SCRIPT, len(on_disk), len(block)))
    mode = p.stat().st_mode & 0o777
    print("%s mode: %s" % (SCRIPT, oct(mode)))
    if mode & 0o111:
        bad.append("%s is executable (%s); every existing script here is 100644 and every "
                   "caller runs it as 'python3 %s'" % (SCRIPT, oct(mode), SCRIPT))

changed = sorted(x for x in git("diff", "--name-only", base, *SCOPE).split("\n") if x)
untracked = sorted(x for x in git("ls-files", "--others", "--exclude-standard",
                                  *SCOPE).split("\n") if x)
seen = sorted(set(changed) | set(untracked))
print("in scope:", seen)
if seen != sorted(WANT_SCOPE):
    bad.append("file scope: %s, want %s" % (seen, sorted(WANT_SCOPE)))

for why in bad:
    print("MISMATCH:", why)
print("task 1 file:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected: a `base:` line carrying a 40-character SHA, `scripts/check-version-bump.py: 155 lines`, `scripts/check-version-bump.py mode: 0o644`, an `in scope:` line listing exactly that one path, then `task 1 file: OK` and `exit=0`. Run before Step 2 the same program prints a `does not exist on disk` mismatch and a `file scope: []` mismatch and exits 1.

The `ls-files --others` half is required here and only here: at this point the file is created but not yet committed or staged, so `git diff --name-only` alone would not see it and the scope assertion would pass vacuously.

- [x] **Step 4: Success criterion 3 — the check rejects the incident**

The criterion the whole change exists for, and the only one that exercises a red path of the shipped script. Verbatim from the design's *Success criteria* 3. Run:

```sh
python3 - <<'PY'
import subprocess, sys
CASES = [
    # (base, head, want_exit, why)
    ("963a66c", "84d8cc9", 1, "the merge that reused main's published 2.7.0/1.9.0"),
    ("963a66c", "5f99cf2", 1, "the same branch before it merged main in"),
    ("963a66c", "02ffb7b", 0, "the fix that re-targeted to 2.8.0/1.10.0"),
    ("c28a613^", "c28a613", 0, "a plugin added for the first time -- skipped, not failed"),
]
bad = []
for base, head, want, why in CASES:
    r = subprocess.run(["python3", "scripts/check-version-bump.py", base, head],
                       capture_output=True, text=True)
    print("%s..%s exit=%d want=%d  (%s)" % (base, head, r.returncode, want, why))
    if r.returncode != want:
        bad.append("%s..%s exited %d, want %d\n%s" % (base, head, r.returncode, want,
                                                      r.stdout + r.stderr))
    if want == 1:
        for name in ("dev-flow", "dev-flow-worktree"):
            if ("  %-20s" % name) + " " not in r.stdout:
                bad.append("%s..%s does not name %s in its report" % (base, head, name))
for why in bad:
    print("MISMATCH:", why)
print("incident:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected: four rows with `exit` equal to `want` — `1`, `1`, `0`, `0` in that order — then `incident: OK` and `exit=0`.

- [x] **Step 5: Success criterion 4 — failed producers halt, and the usage line is real**

Verbatim from the design's *Success criteria* 4. The `HEAD:plugins` row is the one that fails if `resolve` ever stops appending `^{commit}`: `git rev-parse --verify HEAD:plugins` succeeds and yields a tree. Run:

```sh
python3 - <<'PY'
import subprocess, sys
CASES = [([], "usage:"), (["no-such-ref"], "FAILED: git rev-parse"),
         ([""], "FAILED: git rev-parse"),
         (["HEAD:plugins"], "FAILED: git rev-parse"),
         (["origin/main", "HEAD", "extra"], "usage:")]
bad = []
for args, needle in CASES:
    r = subprocess.run(["python3", "scripts/check-version-bump.py"] + args,
                       capture_output=True, text=True)
    out = r.stdout + r.stderr
    print("argv=%r exit=%d first-line=%r" % (args, r.returncode, out.strip().split("\n")[0][:72]))
    if r.returncode == 0:
        bad.append("argv=%r exited 0; a failed producer must halt" % (args,))
    if needle not in out:
        bad.append("argv=%r did not report %r" % (args, needle))
for why in bad:
    print("MISMATCH:", why)
print("producers:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected: five rows, every one with a non-zero `exit`, then `producers: OK` and `exit=0`.

- [x] **Step 6: Success criterion 5 — the check rejects nothing merged since the bump rule was written**

The false-positive bound. Verbatim from the design's *Success criteria* 5. Run:

```sh
python3 - <<'PY'
import subprocess, sys
def git(*a):
    r = subprocess.run(("git",) + a, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(a), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout
rejected, n = [], 0
for line in git("log", "--first-parent", "--format=%H %s", "1f359e2^..origin/main").strip().split("\n"):
    sha, subj = line.split(" ", 1)
    parents = git("rev-parse", sha + "^@").split()
    if len(parents) != 1:
        continue
    n += 1
    if subprocess.run(["python3", "scripts/check-version-bump.py", parents[0], sha],
                      capture_output=True, text=True).returncode:
        rejected.append((sha[:7], subj[:52]))
print("commits replayed:", n)
print("rejected:", len(rejected))
for row in rejected:
    print("   %s  %s" % row)
sys.exit(1 if rejected else 0)
PY
echo "exit=$?"
```

Expected: `commits replayed:` at least **17** (it grows as `main` advances), `rejected: 0`, and `exit=0`. A non-zero `rejected` count names each offending commit; **stop and report** rather than editing the script — the design's replay measured zero across every post-convention merge, so a rejection here means either the script is not block 0 or `main` has since acquired a genuine violation.

- [x] **Step 7: Success criterion 10 — the check sees a touched plugin whose path git would otherwise hide**

The falsifier for the shipped script's `-z` and `--no-renames` flags: without either, every row below exits 0 and reports `no plugin directory touched`, which is the silent pass this whole change exists to prevent. The probe repository is built in a temporary directory and removed. Verbatim from the design's *Success criteria* 10. Run from the repo root:

```sh
python3 - <<'PY'
import os, pathlib, shutil, subprocess, sys, tempfile
SCRIPT = os.path.abspath("scripts/check-version-bump.py")
tmp = tempfile.mkdtemp(prefix="check-version-bump-")
root = pathlib.Path(tmp)
def git(*a):
    return subprocess.run(("git", "-C", tmp) + a, capture_output=True, text=True,
                          check=True).stdout
git("init", "-q")
git("config", "user.email", "t@example.invalid")
git("config", "user.name", "t")
(root / "plugins/foo/skills").mkdir(parents=True)
(root / "plugins/foo/.claude-plugin").mkdir(parents=True)
(root / "plugins/foo/.claude-plugin/plugin.json").write_text('{"name": "foo", "version": "1.0.0"}\n')
(root / "plugins/foo/skills/a.md").write_text("x\n" * 40)
git("add", "-A"), git("commit", "-qm", "base")
base = git("rev-parse", "HEAD").strip()
CASES = [
    ("a newline in the path", lambda: (root / "plugins/foo/skills/we\nird.md").write_text("y\n")),
    ("a non-ASCII path", lambda: (root / "plugins/foo/skills/café.md").write_text("y\n")),
    ("a file moved out of the plugin", lambda: git("mv", "plugins/foo/skills/a.md", "moved.md")),
]
bad = []
for why, make in CASES:
    git("checkout", "-q", "-B", "probe", base), git("clean", "-qfd")
    make()
    git("add", "-A"), git("commit", "-qm", why)
    head = git("rev-parse", "HEAD").strip()
    r = subprocess.run(["python3", SCRIPT, base, head], capture_output=True, text=True, cwd=tmp)
    print("%-32s exit=%d" % (why, r.returncode))
    if r.returncode != 1 or "foo" not in r.stdout:
        bad.append("%s: exit %d, want 1 naming foo\n%s" % (why, r.returncode, r.stdout + r.stderr))
shutil.rmtree(tmp)
for w in bad:
    print("MISMATCH:", w)
print("hidden paths:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected: three rows at `exit=1`, then `hidden paths: OK` and `exit=0`. Design **A12** records the premise: the filesystem must accept a newline and a non-ASCII byte in a filename, which macOS and `ubuntu-latest` both do; on a filesystem that refuses them this step fails loudly at the write rather than passing vacuously.

- [x] **Step 8: Success criterion 6 — the check passes this change's own tree, vacuously and visibly**

Verbatim from the design's *Success criteria* 6. The word *vacuously* is the point (**A5**), which is why Steps 4, 6 and 7 exist. Run:

```sh
python3 scripts/check-version-bump.py origin/main
echo "exit=$?"
```

Expected: a `check-version-bump: base … head … merge-base …` line, then `check-version-bump: no plugin directory touched ... OK` and `exit=0`. **If it prints anything about a plugin directory, stop and report** — Global Constraint 1 has been violated and something under `plugins/` was touched.

- [x] **Step 9: Commit**

```sh
git add scripts/check-version-bump.py
git commit -m "Add scripts/check-version-bump.py: every touched plugin ahead of the base ref's tip (#48)"
```

---

### Task 2: `.github/workflows/check-version-bump.yml` from design block 1

**Files:**
- Create: `.github/workflows/check-version-bump.yml` — design block **1**, 18 lines, read from disk and never retyped
- Test: none — the checks are the program in Step 2.

**Interfaces:**
- Consumes: block 1 of the design, read through `read_blocks(DESIGN, [155, 18, 1])[1]`; and `scripts/check-version-bump.py` from **Task 1**, which must already exist on disk — the workflow's last line is `run: python3 scripts/check-version-bump.py "origin/$BASE"`.
- Produces: a workflow named `check-version-bump` triggering on `pull_request`, checking out `github.event.pull_request.head.sha` at `fetch-depth: 0`, fetching the base branch by explicit refspec, and running the script with one argument. **The design's criteria 7 and 11 are what verify this in the world**, and neither can run here — see *After the last task*.

**Ordering:** this task runs **after** Task 1. The workflow references the script by path, so landing it first would produce a commit whose CI job cannot run.

**Why there is less to assert here than in Task 1:** the workflow's real verification is GitHub's — the design states that no YAML parser is available on this machine (`python3 -c 'import yaml'` fails), so *"the file is well-formed"* is asserted by the workflow appearing in the PR's checks at all (criterion 7), and *"it evaluated the PR's own tip"* by reading the run's log (criterion 11). What Step 2 asserts locally is everything that does not need a PR: block equality, the referenced script path existing, `check-sync.yml` untouched, and scope.

- [x] **Step 1: Create the file from block 1**

The program reads block 1 from the design on disk and refuses to write if the target already exists. **Do not type the workflow's contents.** Run:

```sh
python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-03-gh-48-version-collision-design.md"
TARGET = ".github/workflows/check-version-bump.yml"

block = read_blocks(DESIGN, [155, 18, 1])[1]
target = Path(TARGET)
if target.exists():
    raise SystemExit("%s already exists; this change creates it -- already applied, "
                     "hand-created, or the base moved; stop and report" % TARGET)
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text("\n".join(block) + "\n", encoding="utf-8")
print("created %s, %d lines, first line %r" % (TARGET, len(block), block[0]))
PY
echo "exit=$?"
```

Expected: `created .github/workflows/check-version-bump.yml, 18 lines, first line 'name: check-version-bump'` and `exit=0`.

- [x] **Step 2: Verify the workflow is its design block, names a script that exists, leaves `check-sync.yml` byte-identical, and is the only new change**

Run:

```sh
python3 - <<'PY'
import subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-03-gh-48-version-collision-design.md"
SCRIPT = "scripts/check-version-bump.py"
WORKFLOW = ".github/workflows/check-version-bump.yml"
SIBLING = ".github/workflows/check-sync.yml"
SCOPE = ["--", ".", ":!docs/superpowers/"]
WANT_SCOPE = sorted([SCRIPT, WORKFLOW])

def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout

def split(text):
    out = text.split("\n")
    if out and out[-1] == "":
        out.pop()
    return out

block = read_blocks(DESIGN, [155, 18, 1])[1]
base = git("merge-base", "origin/main", "HEAD").strip()
print("base:", base)
bad = []

if subprocess.run(("git", "cat-file", "-e", "%s:%s" % (base, WORKFLOW)),
                  capture_output=True).returncode == 0:
    bad.append("%s already existed at the base; this change creates it" % WORKFLOW)
p = Path(WORKFLOW)
if not p.is_file():
    bad.append("%s does not exist on disk; this change creates it from design block 1" % WORKFLOW)
else:
    on_disk = split(p.read_text(encoding="utf-8"))
    print("%s: %d lines" % (WORKFLOW, len(on_disk)))
    if on_disk != block:
        bad.append("%s is not design block 1 verbatim (%d lines on disk, %d in the block)"
                   % (WORKFLOW, len(on_disk), len(block)))

# The workflow names a path; nothing else here proves that path resolves.
named = [line for line in block if SCRIPT in line]
print("lines of block 1 naming %s: %d" % (SCRIPT, len(named)))
if len(named) != 1:
    bad.append("block 1 names %s on %d lines, want exactly 1" % (SCRIPT, len(named)))
if not Path(SCRIPT).is_file():
    bad.append("%s names %s, which does not exist on disk; Task 1 must land first"
               % (WORKFLOW, SCRIPT))

# check-sync.yml must be byte-identical: the design keeps its green history untouched.
if split(Path(SIBLING).read_text(encoding="utf-8")) != split(git("show", base + ":" + SIBLING)):
    bad.append("%s differs from its base blob; the design requires it byte-identical" % SIBLING)

changed = sorted(x for x in git("diff", "--name-only", base, *SCOPE).split("\n") if x)
untracked = sorted(x for x in git("ls-files", "--others", "--exclude-standard",
                                  *SCOPE).split("\n") if x)
seen = sorted(set(changed) | set(untracked))
print("in scope:", seen)
if seen != WANT_SCOPE:
    bad.append("file scope: %s, want %s" % (seen, WANT_SCOPE))

for why in bad:
    print("MISMATCH:", why)
print("task 2 file:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected: a `base:` line, `.github/workflows/check-version-bump.yml: 18 lines`, `lines of block 1 naming scripts/check-version-bump.py: 1`, an `in scope:` line listing exactly the script and the workflow, then `task 2 file: OK` and `exit=0`. Run before Step 1 it prints a `does not exist on disk` mismatch and a scope mismatch and exits 1.

- [x] **Step 3: Commit**

```sh
git add .github/workflows/check-version-bump.yml
git commit -m "Run check-version-bump on every pull request (#48)"
```

---

### Task 3: `CLAUDE.md` line 7 replaced by design block 2

**Files:**
- Modify: `CLAUDE.md:7` — replaced in full by design block **2**, read from disk and never retyped
- Test: none — the checks are the programs in Steps 2–3.

**Interfaces:**
- Consumes: block 2 of the design, read through `read_blocks(DESIGN, [155, 18, 1])[2][0]`; anchor line `BULLET_I = 7`, 1-based, **at the merge base**; and the existence of `scripts/check-version-bump.py` from **Task 1**, which block 2 names as a runnable local command.
- Produces: `CLAUDE.md` at **34 lines** — unchanged, because block 2 appends to line 7 rather than adding a line — with line 7 equal to block 2. Task 4 re-asserts this over the finished tree.

**Ordering:** after Task 1, because the sentence block 2 appends points at `scripts/check-version-bump.py` and Step 3's criterion 2 asserts that the file it names exists as its block.

**The direction of this edit is the one place a fresh implementer can go wrong.** Block 2 **appends**: everything through `Major only when a plugin is split (\`dev-flow\` 1.x → 2.0.0).` is byte-identical to the base line, two sentences are added, and nothing is removed. The program below refuses to write unless the base line is a **strict prefix** of block 2, and Step 2's criterion 2 asserts the same property again over the written file. That strict-prefix assertion is what stands in for this change's `Always:` removed-phrase grep — there is no removed phrase to grep for, so removal is made detectable instead.

**Do not renumber, reflow, or reformat anything else in `CLAUDE.md`.** The edit is a single whole-line replacement.

- [x] **Step 1: Apply block 2 to line 7**

The program refuses to write if the line it is about to replace already differs from the merge-base blob — which is what a second run, a hand edit, or a moved base looks like. Run:

```sh
python3 - <<'PY'
import subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-03-gh-48-version-collision-design.md"
TARGET = "CLAUDE.md"
BULLET_I = 7                        # 1-based, at the base

def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout

def split(text):
    out = text.split("\n")
    if out and out[-1] == "":
        out.pop()
    return out

bullet = read_blocks(DESIGN, [155, 18, 1])[2][0]
base = git("merge-base", "origin/main", "HEAD").strip()
print("base:", base)
disk = split(Path(TARGET).read_text(encoding="utf-8"))
old = split(git("show", base + ":" + TARGET))
if disk[BULLET_I - 1] != old[BULLET_I - 1]:
    raise SystemExit("%s line %d already differs from the base blob -- already applied, "
                     "hand-edited, or the base moved; stop and report" % (TARGET, BULLET_I))
if not bullet.startswith(old[BULLET_I - 1]) or bullet == old[BULLET_I - 1]:
    raise SystemExit("block 2 is not a strict extension of base line %d; this edit appends "
                     "and removes nothing, so every existing byte must survive" % BULLET_I)
disk[BULLET_I - 1] = bullet
Path(TARGET).write_text("\n".join(disk) + "\n", encoding="utf-8")
print("replaced %s line %d; file is %d lines" % (TARGET, BULLET_I, len(disk)))
PY
echo "exit=$?"
```

Expected: a `base:` line carrying a 40-character SHA, then `replaced CLAUDE.md line 7; file is 34 lines` and `exit=0`.

- [x] **Step 2: Success criterion 2 — design conformance, now for all three files**

This is the design's *Success criteria* 2, verbatim, and this is the first point in the plan at which it can go fully green: it asserts all three files at once. One program, nothing retyped on either side — the blocks are read **from the design on disk** through the shared reader, and `CLAUDE.md`'s expected content is reconstructed **from the base blob**. Run:

```sh
python3 - <<'PY'
import subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-03-gh-48-version-collision-design.md"
SCRIPT = "scripts/check-version-bump.py"
WORKFLOW = ".github/workflows/check-version-bump.yml"
TARGET = "CLAUDE.md"
BULLET_I = 7                        # 1-based, at the base
WANT_LEN = 34                       # unchanged: block 2 appends, it does not add a line

def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout
def split(text):
    out = text.split("\n")
    if out and out[-1] == "":
        out.pop()
    return out

base = git("merge-base", "origin/main", "HEAD").strip()
blocks = read_blocks(DESIGN, [155, 18, 1])
script, workflow, bullet = blocks[0], blocks[1], blocks[2][0]
bad = []

for path, block in ((SCRIPT, script), (WORKFLOW, workflow)):
    if subprocess.run(("git", "cat-file", "-e", "%s:%s" % (base, path)),
                      capture_output=True).returncode == 0:
        bad.append("%s already existed at the base; this change creates it" % path)
    if not Path(path).is_file():
        bad.append("%s does not exist on disk; this change creates it from its design block"
                   % path)
        continue
    on_disk = split(Path(path).read_text(encoding="utf-8"))
    if on_disk != block:
        bad.append("%s is not its design block verbatim (%d lines on disk, %d in the block)"
                   % (path, len(on_disk), len(block)))

old = split(git("show", base + ":" + TARGET))
new = split(Path(TARGET).read_text(encoding="utf-8"))
expected = old[:BULLET_I - 1] + [bullet] + old[BULLET_I:]
if new != expected:
    bad.append("%s is not its base blob with line %d replaced by block 2"
               % (TARGET, BULLET_I))
if len(new) != WANT_LEN:
    bad.append("%s is %d lines, want %d" % (TARGET, len(new), WANT_LEN))
if new.count(bullet) != 1:
    bad.append("%s holds block 2 %d times, want exactly 1" % (TARGET, new.count(bullet)))
if not bullet.startswith(old[BULLET_I - 1]):
    bad.append("block 2 does not start with the base line %d; the edit must append, "
               "never rewrite" % BULLET_I)
if SCRIPT not in bullet:
    bad.append("block 2 does not name %s; the appended sentence must point at the check"
               % SCRIPT)

for why in bad:
    print("MISMATCH:", why)
print("conformance:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected: exactly `conformance: OK` and `exit=0`. Run at the base with no edit applied, the design records that this same program printed four `MISMATCH:` lines — both new paths not existing on disk, `CLAUDE.md is not its base blob with line 7 replaced by block 2`, and `CLAUDE.md holds block 2 0 times, want exactly 1` — then `conformance: FAIL` and `exit=1`. That is its red form.

- [x] **Step 3: Success criterion 1 — file scope is exactly three files, and they are the three named**

The design's *Success criteria* 1, verbatim. The `--name-only` set is compared for **equality** against the authorized list, so a stray edit to `plugins/`, a `plugin.json`, `check-sync.yml`, `check-sync.py`, `CONTEXT.md`, `docs/adr/` or `marketplace.json` fails the step **and names the offending path**. Run:

```sh
python3 - <<'PY'
import subprocess, sys
SCOPE = ["--", ".", ":!docs/superpowers/"]
WANT = [".github/workflows/check-version-bump.yml", "CLAUDE.md",
        "scripts/check-version-bump.py"]
def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout
base = git("merge-base", "origin/main", "HEAD").strip()
print("base:", base)
changed = sorted(p for p in git("diff", "--name-only", base, *SCOPE).split("\n") if p)
if changed != sorted(WANT):
    print("file scope: FAIL -- changed %s, want %s" % (changed, sorted(WANT)))
    sys.exit(1)
print("file scope: OK")
PY
echo "exit=$?"
```

Expected: a `base:` line carrying a 40-character SHA, then `file scope: OK` and `exit=0`. Tasks 1 and 2 have already committed their files, and `CLAUDE.md` is modified in the working tree, so all three are in `git diff`'s set here.

- [x] **Step 4: Commit**

```sh
git add CLAUDE.md
git commit -m "CLAUDE.md: bump past origin/main, not past your branch's base (#48)"
```

---

### Task 4: The acceptance gate — the design's *Success criteria* 1, 2, 6, 8 and 9 over the finished tree, then hand off 7 and 11

**Files:** none modified. This task is the acceptance gate.

**Interfaces:**
- Consumes: the finished tree from Tasks 1–3, and blocks 0–2 of the design, re-read from disk by Step 2 below — which is also this task's shape guard, since `read_blocks` takes the shape as a required argument and exits non-zero if it moved.
- Produces: the pass evidence the pipeline's Execute-stage report carries, plus the criteria 7 / 11 hand-off in *After the last task*.

The commands below are the design's *Success criteria* 1, 2, 6, 8 and 9, **verbatim and runnable as written** — byte-for-byte the design's, so what passes here is the design's own criteria rather than a paraphrase of them. **Do not restyle them.** Where a criterion wraps `git` differently from a Task 1–3 program, that difference is the design's and is carried here deliberately; normalizing it would put this task out of step with the document it quotes.

**What this task adds, and what it deliberately does not repeat.** Every per-task verifier ran **before** the next task's edits and before that task's own review, so none of them saw the tree that will actually be pushed: Task 3's Step 2 ran with `CLAUDE.md` still uncommitted, and any fix a per-task review applied afterwards is outside all of them. Steps 1 and 2 are that gap closed — they are the only assertions anywhere that the *assembled* tree is exactly the three authorized files and that each is its design block, or its base blob with exactly line 7 replaced.

Steps 3, 4 and 5 are new here for their own reasons. Criterion 6 is the shipped script run against the shipped tree — at Task 1 it saw a diff carrying only the docs commits, here it sees the whole three-file change — and the verdict line it prints, `no plugin directory touched ... OK`, is the exact string criterion 11 later requires in the CI log. Criteria 8 and 9 are the repo's standing checks, which no earlier task runs at all.

The design's criteria **0, 3, 4, 5 and 10 are not repeated here, on purpose.** Each is a deterministic function of `scripts/check-version-bump.py`'s bytes over history that cannot move — literal SHAs, an argv contract, a temporary probe repository — and Task 1 established every one of them against those bytes. Step 2 asserts the file on disk is still block 0 byte for byte, and *that* is what carries Task 1's results onto the artifact being pushed; re-deriving them at the gate would be testing Python's determinism rather than this change. Criterion 0 goes the same way: `read_blocks` is the guard and the CLI is only a reporter, so Step 2's `read_blocks(DESIGN, [155, 18, 1])` call **is** criterion 0 — a step of its own could only fail where Step 2 fails anyway.

Run them in order and read each expected output before moving on.

- [x] **Step 1 — Criterion 1: file scope, exactly three files**

```sh
python3 - <<'PY'
import subprocess, sys
SCOPE = ["--", ".", ":!docs/superpowers/"]
WANT = [".github/workflows/check-version-bump.yml", "CLAUDE.md",
        "scripts/check-version-bump.py"]
def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout
base = git("merge-base", "origin/main", "HEAD").strip()
print("base:", base)
changed = sorted(p for p in git("diff", "--name-only", base, *SCOPE).split("\n") if p)
if changed != sorted(WANT):
    print("file scope: FAIL -- changed %s, want %s" % (changed, sorted(WANT)))
    sys.exit(1)
print("file scope: OK")
PY
echo "exit=$?"
```

Expected: a `base:` line carrying a 40-character SHA, then `file scope: OK` and `exit=0`.

- [x] **Step 2 — Criterion 2: design conformance for all three files**

```sh
python3 - <<'PY'
import subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-03-gh-48-version-collision-design.md"
SCRIPT = "scripts/check-version-bump.py"
WORKFLOW = ".github/workflows/check-version-bump.yml"
TARGET = "CLAUDE.md"
BULLET_I = 7                        # 1-based, at the base
WANT_LEN = 34                       # unchanged: block 2 appends, it does not add a line

def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout
def split(text):
    out = text.split("\n")
    if out and out[-1] == "":
        out.pop()
    return out

base = git("merge-base", "origin/main", "HEAD").strip()
blocks = read_blocks(DESIGN, [155, 18, 1])
script, workflow, bullet = blocks[0], blocks[1], blocks[2][0]
bad = []

for path, block in ((SCRIPT, script), (WORKFLOW, workflow)):
    if subprocess.run(("git", "cat-file", "-e", "%s:%s" % (base, path)),
                      capture_output=True).returncode == 0:
        bad.append("%s already existed at the base; this change creates it" % path)
    if not Path(path).is_file():
        bad.append("%s does not exist on disk; this change creates it from its design block"
                   % path)
        continue
    on_disk = split(Path(path).read_text(encoding="utf-8"))
    if on_disk != block:
        bad.append("%s is not its design block verbatim (%d lines on disk, %d in the block)"
                   % (path, len(on_disk), len(block)))

old = split(git("show", base + ":" + TARGET))
new = split(Path(TARGET).read_text(encoding="utf-8"))
expected = old[:BULLET_I - 1] + [bullet] + old[BULLET_I:]
if new != expected:
    bad.append("%s is not its base blob with line %d replaced by block 2"
               % (TARGET, BULLET_I))
if len(new) != WANT_LEN:
    bad.append("%s is %d lines, want %d" % (TARGET, len(new), WANT_LEN))
if new.count(bullet) != 1:
    bad.append("%s holds block 2 %d times, want exactly 1" % (TARGET, new.count(bullet)))
if not bullet.startswith(old[BULLET_I - 1]):
    bad.append("block 2 does not start with the base line %d; the edit must append, "
               "never rewrite" % BULLET_I)
if SCRIPT not in bullet:
    bad.append("block 2 does not name %s; the appended sentence must point at the check"
               % SCRIPT)

for why in bad:
    print("MISMATCH:", why)
print("conformance:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected: exactly `conformance: OK` and `exit=0`.

- [x] **Step 3 — Criterion 6: the check passes this change's own PR, vacuously and visibly**

```sh
python3 scripts/check-version-bump.py origin/main
echo "exit=$?"
```

Expected: a `base … head … merge-base` line, then `check-version-bump: no plugin directory touched ... OK` and `exit=0`. The word *vacuously* is the point (**A5**), which is why criteria 3, 5 and 10 exist.

- [x] **Step 4 — Criterion 8: `python3 scripts/check-sync.py` passes, with output identical to before the change**

It reads none of the changed files; this is a regression guard, not a claim about the edit.

```sh
python3 scripts/check-sync.py
echo "exit=$?"
```

Expected — unchanged from the base:

```text
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)
check-sync: all checks passed
exit=0
```

- [x] **Step 5 — Criterion 9: `claude plugin validate .` exits 0 *and* emits exactly 8 author warnings**

Both halves are asserted, because either alone passes vacuously: the command exits 0 while emitting warnings (**A6**), and a count assertion alone would pass on a run that errored out. This change adds no plugin, so the count is unchanged.

```sh
python3 - <<'PY'
import shutil, subprocess, sys
WANT_WARNINGS = 8
NEEDLE = "No author information provided"
if shutil.which("claude") is None:
    raise SystemExit("FAILED: claude is not on PATH; this step cannot run")
r = subprocess.run(["claude", "plugin", "validate", "."], capture_output=True, text=True)
n = (r.stdout + r.stderr).count(NEEDLE)
print("claude plugin validate: exit %d, %d author warnings" % (r.returncode, n))
bad = []
if r.returncode != 0:
    bad.append("claude plugin validate . exited %d, want 0" % r.returncode)
if n != WANT_WARNINGS:
    bad.append("%d %r warnings, want exactly %d" % (n, NEEDLE, WANT_WARNINGS))
for why in bad:
    print("MISMATCH:", why)
print("validate:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected:

```text
claude plugin validate: exit 0, 8 author warnings
validate: OK
exit=0
```

- [x] **Step 6 — Confirm nothing in scope is left uncommitted**

Tasks 1–3 each committed their own file; the design and this plan are the pipeline's to commit. Run:

```sh
python3 - <<'PY'
import subprocess, sys
def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout
bad = []
dirty = [line for line in git("status", "--porcelain", "--", ".", ":!docs/superpowers/")
         .split("\n") if line]
print("uncommitted in scope:", dirty)
if dirty:
    bad.append("uncommitted or untracked files in scope: %s" % dirty)
for why in bad:
    print("MISMATCH:", why)
print("tree state:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected: `uncommitted in scope: []`, then `tree state: OK` and `exit=0`. Any path printed under *uncommitted in scope* is inside the change's scope — report it rather than committing it, since the three authorized files are already committed.

- [x] **Step 7 — Hand criteria 7 and 11 to the orchestrator**

This is the last checkbox in the plan. Do **not** attempt criteria 7 and 11 yourself — neither can run yet, because both need an open PR with a *completed* CI run, and no PR exists during Execute. Report to the orchestrator, in the Execute-stage completion report, the whole of the *After the last task* section below, and say plainly that both criteria are outstanding.

---

## After the last task: criteria 7 and 11, at the PR stage

**This is prose addressed to the orchestrator, and it is deliberately not a checkbox.** Every checkbox in this plan is completable inside the Execute stage; these two are not — they must run **after** Stage 4 has opened the PR and GitHub has finished a `check-version-bump` run against it. dev-flow's own rule is that *execution is complete if and only if no unchecked task box remains in the plan at branch tip*, and its resume table routes a plan with any unchecked box straight back into Execute; a checkbox here would therefore trap the pipeline in a loop it can never leave. So these two criteria are carried as prose, exactly as the repo's prior plans carry their stage-boundary steps.

**Nothing mechanically detects these being skipped.** They are the *only* verification anywhere that the workflow file is well-formed YAML and that CI evaluated the right revision — the design states that no YAML parser is available on this machine, so *"the file parses"* is asserted only by the workflow appearing among the PR's checks. Treat a criteria pass reported without them as incomplete.

**Criterion 7 — the workflow is valid, wired up, and green on this PR.** Under `--json`, `gh pr checks` exits **0** for pass, fail *and* pending alike and **1** only when there are no checks at all, so this program takes its verdict from the JSON and never from the exit code, and reads `bucket` — gh's own `pass`/`fail`/`pending`/`skipping`/`cancel` categorisation of `state` — rather than a state list retyped here. **A check that has not finished is not a check that failed:** the program polls every 10 s under a 300 s cap and ends in exactly one of three states — `OK` (exit 0), `FAIL` (exit 1), `NOT READY` (exit 2, CI unfinished, nothing to fix). Absence that survives the cap is a `FAIL`; unfinished is not. Run it with a Bash-tool timeout above the cap (`timeout: 330000`).

```sh
python3 - <<'PY'
import json, subprocess, sys, time
BRANCH = "tayl0r/gh-48-version-collision"
WANT = "check-version-bump"
CAP, INTERVAL = 300, 10   # gh's own watch interval, under a cap the Bash tool can outlive
def gh(*a, ok=(0,)):
    r = subprocess.run(("gh",) + a, capture_output=True, text=True)
    if r.returncode not in ok:
        raise SystemExit("FAILED: gh %s -- exit %d, %s" % (" ".join(a), r.returncode,
                                                           r.stderr.strip() or "(no message)"))
    return r
prs = json.loads(gh("pr", "list", "--head", BRANCH, "--state", "all", "--json", "number").stdout)
if not prs:
    raise SystemExit("FAILED: no PR for %s -- Stage 4 has not opened it yet" % BRANCH)
pr = str(max(p["number"] for p in prs))
# Under --json, gh pr checks writes the rows and returns before it maps counts to a
# status: it exits 0 for pass, fail and pending alike, and 1 only when there are no
# checks at all, where stdout is empty. The JSON is the verdict, never the exit code.
# bucket is gh's own categorisation of state -- pass/fail/pending/skipping/cancel --
# so "has not finished" is read from gh's table rather than a state list retyped here.
deadline = time.monotonic() + CAP
while True:
    r = gh("pr", "checks", pr, "--json", "name,state,bucket", ok=(0, 1, 8))
    checks = json.loads(r.stdout.strip() or "[]")
    print("PR #%s (gh exit %d): %s" % (pr, r.returncode,
          sorted("%s=%s" % (c["name"], c["state"]) for c in checks) or "no checks reported"))
    rows = [c for c in checks if c["name"] == WANT]
    if rows and not [c for c in rows if c["bucket"] == "pending"]:
        break                    # WANT reached a terminal state -- judge it
    left = deadline - time.monotonic()
    if left <= 0:
        break                    # at the cap: absence is a defect, unfinished is not
    time.sleep(min(INTERVAL, left))
if [c for c in rows if c["bucket"] == "pending"]:
    print("pr checks: NOT READY -- %s is %s after %ds; a run that has not finished is "
          "not a defect. Run this step again." % (WANT, rows[0]["state"], CAP))
    sys.exit(2)
bad = []
if not rows:
    bad.append("%r is not among the PR's checks after %ds; the workflow did not parse "
               "or did not run" % (WANT, CAP))
for c in rows:
    if c["bucket"] != "pass":
        bad.append("%s is %s (bucket %s), want SUCCESS" % (c["name"], c["state"], c["bucket"]))
if not [c for c in checks if c["name"] == "check-sync"]:
    bad.append("check-sync is missing; the new workflow must not disturb the existing one")
for why in bad:
    print("MISMATCH:", why)
print("pr checks:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected: one or more poll lines, the last showing `check-sync` and `check-version-bump` both at `SUCCESS`, then `pr checks: OK` and `exit=0`. `pr checks: NOT READY` at `exit=2` is not a red result — it is this step declining to judge a run that has not finished.

**Criterion 11 — CI evaluated the PR's own tip, not a merge commit.** Criterion 7 reads the check list, never the revision the run evaluated, so it would pass with the checkout unpinned. This one reads the run's log and asserts the head the script printed is the PR's head sha (**A11**). The run is selected by that sha (`--branch` + `--commit`, matched on `workflowName`), never by recency and never through `--workflow`, which 404s until the file is on the default branch; with no completed run for the current head it reports `NOT READY` at exit **2**. Run **after** criterion 7.

```sh
python3 - <<'PY'
import json, subprocess, sys
BRANCH = "tayl0r/gh-48-version-collision"
WORKFLOW = "check-version-bump"        # block 1's name:, not the file name
def sh(*a):
    r = subprocess.run(a, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: %s -- exit %d, %s"
                         % (" ".join(a), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout
head = json.loads(sh("gh", "pr", "view", BRANCH, "--json", "headRefOid"))["headRefOid"]
# Selected by the head sha, never by recency: a completed run for an *earlier* head --
# the ordinary state of a branch that has been pushed twice -- is not this criterion's
# subject, and reading one would report a pinned checkout as unpinned. --branch and
# --commit are plain filters; --workflow is a lookup that 404s until the file is on the
# default branch, which it is not until this PR merges.
runs = [r for r in json.loads(sh("gh", "run", "list", "--branch", BRANCH, "--commit", head,
                                 "--status", "completed", "--limit", "20",
                                 "--json", "databaseId,conclusion,workflowName"))
        if r["workflowName"] == WORKFLOW]
if not runs:
    print("ci head: NOT READY -- no completed %s run for %s at %s; a run that has not "
          "finished is not a defect. Run criterion 7, then this step, again."
          % (WORKFLOW, BRANCH, head[:9]))
    sys.exit(2)
run = runs[0]
log = sh("gh", "run", "view", str(run["databaseId"]), "--log")
needle = "head %s," % head[:9]
print("PR head %s, run %s concluded %s" % (head[:9], run["databaseId"], run["conclusion"]))
bad = []
if run["conclusion"] != "success":
    bad.append("run %s concluded %s, want success" % (run["databaseId"], run["conclusion"]))
if needle not in log:
    bad.append("the log does not report %r; CI resolved some other head -- the checkout "
               "is not pinned to the PR's head sha" % needle)
if "no plugin directory touched ... OK" not in log:
    bad.append("the log does not carry the script's own verdict line")
for why in bad:
    print("MISMATCH:", why)
print("ci head:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected: a `PR head … run … concluded success` line, then `ci head: OK` and `exit=0`. `ci head: NOT READY` at `exit=2` means the run for this head has not finished — run criterion 7, then this step, again.

**How to read the three tail states.** Each program ends in exactly one — `OK` (exit 0), **`NOT READY`** (exit 2) or **`FAIL`** (exit 1) — and only the last is a defect. A `NOT READY` tail means CI has not finished on this head: nothing is wrong, nothing here is to be changed, run the step again; if it never settles, read the PR's Actions tab before touching any file. A halt whose message begins `FAILED:` is not a verdict either — the step could not run at all (no PR yet, `gh` unauthenticated, a producer command that failed); fix that and run it again. **A `FAIL` is one of three defects, and none of them is in the script** — its behaviour is fully covered by criteria 3, 4, 5 and 10, all of which ran green in Task 1 against a file Task 4's criterion 2 then asserted byte-identical to the one being pushed, plus criterion 6 over the finished tree in Task 4:

- **`check-version-bump` absent from the PR's checks, or `check-sync` missing** — the YAML did not parse, or the job did not run. Re-derive the workflow from **block 1**; never hand-edit it.
- **criterion 11 red with 7 `OK`** — the checkout is not pinned to `github.event.pull_request.head.sha`. Same fix, same source.
- **`check-version-bump` present and not green** — the check itself is red on this PR, which by **A5** it cannot be within the authorized three-file scope. That is the case the paragraph below decides: a file outside those three paths was touched. Find it and revert it.

**Where these must be reported:** in the PR-stage report, each named as run with its output, or named as outstanding. A step that ended `NOT READY`, or halted with a `FAILED:` message, is **outstanding** — it verified nothing and must never be reported as run. Do not report the criteria pass as complete without both.

**One thing that is decided and must not be reopened at this stage:** if CI ever reports this PR failing `check-version-bump`, that is not a signal to bump a `plugin.json`. This change touches no plugin directory (**A5**), so the check is vacuous on it by construction, and a failure would mean a file outside the three authorized paths was touched. Find and revert that file; do not add a version bump.

---

## Self-review

**Spec coverage.** Every file in the design's *Files the plan will touch* has a task: block 0 → Task 1, block 1 → Task 2, block 2 → Task 3. Every one of the design's twelve *Success criteria* is carried, each placed where it can still fail: 3, 4, 5, 6 and 10 verbatim in Task 1, against the file whose bytes Task 4 then re-asserts; 1 and 2 verbatim in Task 3 and again in Task 4; 6, 8 and 9 verbatim in Task 4; 0 by every `read_blocks(DESIGN, [155, 18, 1])` call, which is the guard the criterion itself names; and 7 and 11 as prose in *After the last task*, with the reason they cannot be checkboxes. **No criterion is run twice unless the second run can reach a different verdict** — true of 1 and 2, because the tree changes between tasks and per-task reviews, and of 6, because the diff it evaluates grows; false of 0, 3, 4, 5 and 10, each a deterministic function of bytes that Task 4's criterion 2 pins. The design's *Out of scope* list is carried as Global Constraint 1, and its **A5** no-version-bump conclusion as Global Constraint 2 and again in *After the last task*. Assumptions A1 (targets at `52c3883`, matched on text not line number), A6 (8 author warnings), A8 (block shape), A9 (`origin/main` fetchable), A10 (docs excluded by pathspec) and A12 (filesystem accepts odd filenames) each appear where they bind. The design decides everything else — the predicate, the trigger, the file contents, every rejected alternative — and no task re-opens any of it.

**Placeholders.** None. Every step is a runnable command with its expected output. The only content not spelled out is the three blocks, and that is deliberate and mandatory — 155 lines of Python retyped by hand is the defect most likely to ship here, and `git diff` cannot flag a wrong byte in a new file. Every program that needs a block reads it from the design on disk through `read_blocks`.

**Consistency.** The block shape `[155, 18, 1]`, the block-to-file mapping (0 → script, 1 → workflow, 2 → `CLAUDE.md` line 7), the anchor `BULLET_I = 7`, the post-edit `WANT_LEN = 34`, and the three-file scope list agree in every task and match the design; the `100644` mode is asserted once, in Task 1, at the moment the file is created and before any commit could record it wrong (`core.fileMode` is `true` in this checkout, so the working-tree bit is what git records). Each task's scope assertion is **cumulative** — Task 1 expects 1 path, Task 2 expects 2, Tasks 3 and 4 expect all 3 — which is correct for tasks run in order and is itself an ordering check. Tasks 1 and 2 union `git diff --name-only` with `git ls-files --others` because their file is created and not yet committed when the check runs; Tasks 3 and 4 need only the diff, because by then the earlier files are committed.

**Ordering is load-bearing, not stylistic.** Task 2's workflow invokes `scripts/check-version-bump.py` by path and Task 3's `CLAUDE.md` line names it as a runnable command, so Task 1 lands first or both later commits reference a file that does not exist. Task 2's Step 2 asserts that dependency directly (`names %s, which does not exist on disk; Task 1 must land first`).

**Compliance with this repo's verification rules.** No `--stat` and no human-read output stands in for an assertion anywhere; every program collects all mismatches and prints them before exiting, so no assertion sits behind a short-circuit. Every step that consumes the computed merge base passes it to `git` as an `argv` element from `python3`/`subprocess`; **no command in this document uses a `$(git …)` substitution**, the form appearing only in this sentence and in Global Constraint 4, which quote it. The literal SHAs the criteria name (`963a66c`, `84d8cc9`, `5f99cf2`, `02ffb7b`, `c28a613`, `1f359e2`) are not computed refs. Every number in *Base facts* was printed by the command given beside it, past-tense at `52c3883`; the post-edit numbers are asserted by Tasks 1–4 rather than certified here. The `Always:` rule's merge-base reconstruction is Task 3's and Task 4's criterion 2; its removed-phrase grep is vacuous by construction here (two files are created, and block 2 removes nothing), and the strict-prefix assertion replaces it, as Global Constraint 4 states.

**What this plan does not certify.** No step here has been run against this checkout — no edit has been applied. The base facts under *Base facts, pinned to `52c3883`* were measured; everything after them is asserted by the tasks.
