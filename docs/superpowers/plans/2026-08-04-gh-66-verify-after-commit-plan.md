---
dev-flow:
  slug: gh-66-verify-after-commit
  spec: docs/superpowers/specs/2026-08-04-gh-66-verify-after-commit-design.md
---

# gh-66 Verify-After-Commit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add one **Verification ordering** bullet to dev-flow's Cross-Cutting Concerns (mirrored byte-identically into `dev-flow-worktree`) stating that a verification step reading committed HEAD (`git show HEAD:…`) must run **after** the task's commit, and bump both plugins' minor versions — all four edits in one atomic commit.

**Architecture:** A pure single-line insertion of the new bullet directly after the byte-identical Command discipline bullet in both pipeline `SKILL.md` files (a hand-mirrored pair not covered by `check-sync.py`), plus the two mechanical `plugin.json` version bumps that any plugin-text change carries in this repo. There is no ordering dependency between the four edits and none can land without the others; they form one commit. Correctness is proven by the design's Verification section (the repo has no test framework), which itself dogfoods the new rule: two of its checks read committed HEAD and therefore run after the commit.

**Tech Stack:** Markdown skill files, JSON plugin manifests, `python3` verification checks driving `git show`/`git diff`, and the repo scripts `scripts/design_blocks.py` (`read_blocks`), `scripts/check-sync.py`, `scripts/check-version-bump.py`, plus `claude plugin validate`.

## Global Constraints

> NOTE: This section is orientation for a human reader only. Under this repo's dev-flow Stage 2 rule an implementer sees **only its own `## Task N` section**, so every constraint below is also inlined verbatim into Task 1, which is where it binds. Nothing here is load-bearing on its own.

- **One atomic commit.** All four file edits (both `SKILL.md` inserts, both `plugin.json` bumps) go in a **single** commit. Do **not** split the `SKILL.md` edits and the version bumps into separate commits — that recreates the multi-commit shape where `check-version-bump.py` reads a committed-but-unbumped state and FAILs (the exact bug #66 documents).
- **Verification ordering (the rule this change adds — dogfood it).** The two verification checks that read committed HEAD — design step 3 (version assertions via `git show HEAD:…`) and design step 6 (`python3 scripts/check-version-bump.py origin/main`) — MUST run **after** the commit, never in a pre-commit sweep. The pre-commit-safe checks (design steps 0, 1, 2, 4, 5) may run before or after the commit.
- **Command discipline.** Pass any computed git ref (e.g. the merge-base) to `git` as an `argv` element from `python3`, never through an unquoted shell `$( )`. `git merge-base` prints nothing and exits non-zero on an unresolvable ref, so an unquoted substitution silently degrades a base comparison into a working-tree one. The verification commands below already obey this; do not rewrite them to use `$( )`.
- **No bare `grep` for byte assertions.** Under Claude Code's Bash tool bare `grep` is a ugrep-backed function that mis-parses leading `-` and is not reliable for per-file byte assertions. Every load-bearing equality is done in `python3` against `git show`/`git diff`.
- **No new tests.** This repo has no test framework; the design's Verification section is the entire correctness surface. Do not invent unit tests.
- **Byte-identical mirror.** The new bullet names no plugin, so the **same bytes** go into both `SKILL.md` files. The pair is hand-mirrored (absent from `check-sync.py`'s `MIRROR_PAIRS`), so both edits are by hand and the reconstruction check rebuilds both files from their `origin/main` blobs.

---

### Task 1: Insert the Verification ordering bullet into both pipeline SKILL.md files, bump both plugin versions, and commit atomically

This is a single, tightly-specified, atomic change: four file edits that form one commit. Do **not** decompose it into multiple commits. Apply all four edits, run the pre-commit-safe checks, make **one** commit of all four files, then run the two post-commit checks.

**Constraints (the Global Constraints, restated here because under this repo's dev-flow Stage 2 rule you see only this `### Task 1` section):**

- **One atomic commit.** All four file edits (both `SKILL.md` inserts, both `plugin.json` bumps) go in a **single** commit. Do **not** split the `SKILL.md` edits and the version bumps into separate commits — that recreates the multi-commit shape where `check-version-bump.py` reads a committed-but-unbumped state and FAILs (the exact bug #66 documents).
- **Verification ordering (the rule this change adds — dogfood it).** The two verification checks that read committed HEAD — design step 3 (version assertions via `git show HEAD:…`) and design step 6 (`python3 scripts/check-version-bump.py origin/main`) — MUST run **after** the commit, never in a pre-commit sweep. The pre-commit-safe checks (design steps 0, 1, 2, 4, 5) may run before or after the commit.
- **Command discipline.** Pass any computed git ref (e.g. the merge-base) to `git` as an `argv` element from `python3`, never through an unquoted shell `$( )`. `git merge-base` prints nothing and exits non-zero on an unresolvable ref, so an unquoted substitution silently degrades a base comparison into a working-tree one. The verification commands below already obey this; do not rewrite them to use `$( )`.
- **No bare `grep` for byte assertions.** Under Claude Code's Bash tool bare `grep` is a ugrep-backed function that mis-parses leading `-` and is not reliable for per-file byte assertions. Every load-bearing equality is done in `python3` against `git show`/`git diff`.
- **No new tests.** This repo has no test framework; the design's Verification section is the entire correctness surface. Do not invent unit tests.
- **Byte-identical mirror.** The new bullet names no plugin, so the **same bytes** go into both `SKILL.md` files. The pair is hand-mirrored (absent from `check-sync.py`'s `MIRROR_PAIRS`), so both edits are by hand and the reconstruction check rebuilds both files from their `origin/main` blobs.

**Repo root:** `/Users/taylor/dev/claude-plugins`. Run every command below from the repo root. You are already on the feature branch `tayl0r/gh-66-verify-after-commit`.

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md` — insert the new bullet as a new line directly after the Command discipline bullet (opener `- **Command discipline:**`, which occurs exactly once); nothing else changes, and the Command discipline bullet itself stays byte-for-byte.
- Modify: `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` — the **same** bytes inserted after the same bullet (hand-mirrored pair; `check-sync.py` does not cover it).
- Modify: `plugins/dev-flow/.claude-plugin/plugin.json` — `"version": "2.14.0"` → `"version": "2.15.0"`; nothing else in the manifest changes (the `description` stays byte-for-byte).
- Modify: `plugins/dev-flow-worktree/.claude-plugin/plugin.json` — `"version": "1.16.0"` → `"version": "1.17.0"`; nothing else changes.
- Read-only input (never edited): the approved design at `/Users/taylor/dev/claude-plugins/docs/superpowers/specs/2026-08-04-gh-66-verify-after-commit-design.md`. It is the verbatim source of the bullet's bytes and of the verification commands.

**Interfaces:**
- Consumes: nothing — this is the first and only task.
- Produces: nothing for a later task — this is the terminal task. Its deliverable is the single commit carrying all four edits, verified green by the design's Verification steps 0–6.

**The exact bytes to insert (do not retype them).** The new bullet is **block 0** of the design: the single plain (untagged) ` ``` ` fenced block under the heading `### Block 0` in `/Users/taylor/dev/claude-plugins/docs/superpowers/specs/2026-08-04-gh-66-verify-after-commit-design.md`. Read it verbatim from that file — never retype, reconstruct, reflow, or paraphrase it. If you cannot read that file, **stop and report**. The insertion step below reads it programmatically via `read_blocks` so the bytes are never transcribed by hand; the reconstruction check (design step 2) re-reads the same block the same way and asserts each file equals its base blob with exactly that bullet inserted, so any hand-transcription drift would fail.

- [ ] **Step 1: Pre-flight — confirm branch, resolvable base, and block shape**

Confirms you are on the feature branch, that the merge-base against `origin/main` resolves (every later check consumes it), and that the design still carries exactly one plain fenced block of shape `[1]` (design step 0). If the shape guard trips (`design code-block shape is [N], want [1]`), the design was edited after this plan was written — **stop and report**, do not proceed.

Run:
```sh
git rev-parse --abbrev-ref HEAD
git merge-base origin/main HEAD
python3 - <<'PY'
import sys
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
DESIGN = "docs/superpowers/specs/2026-08-04-gh-66-verify-after-commit-design.md"
for i, b in enumerate(read_blocks(DESIGN, [1])):
    print("  [%d] len=%d: %s" % (i, len(b), b[0][:70]))
print("shape guard: OK")
PY
echo "exit=$?"
```
Expected: branch `tayl0r/gh-66-verify-after-commit`; a 40-character merge-base SHA (today `bd7b2be6d455839928fdff3f011f085a231a6c54`); then:
```text
  [0] len=1: - **Verification ordering:** a verification step that reads committed 
shape guard: OK
exit=0
```

- [ ] **Step 2: Apply the two SKILL.md inserts programmatically (bytes read from the design, never retyped)**

This reads block 0 from the design via `read_blocks`, finds the single Command discipline opener line in each target, inserts the bullet as the very next line, and writes each file back. It preserves each file's trailing newline. It refuses to run if a file has other than exactly one Command discipline opener. Because it reads the bytes from the design and both files get the same `bullet` object, the two edits cannot diverge.

Run:
```sh
python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-04-gh-66-verify-after-commit-design.md"
TARGETS = ["plugins/dev-flow/skills/dev-flow/SKILL.md",
           "plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md"]
OPENER = "- **Command discipline:**"

bullet = read_blocks(DESIGN, [1])[0][0]
for path in TARGETS:
    lines = Path(path).read_text(encoding="utf-8").split("\n")
    idx = [i for i, ln in enumerate(lines) if ln.startswith(OPENER)]
    if len(idx) != 1:
        raise SystemExit("FAILED: %s has %d Command discipline openers, want exactly 1" % (path, len(idx)))
    i = idx[0]
    lines.insert(i + 1, bullet)
    Path(path).write_text("\n".join(lines), encoding="utf-8")
    print("inserted into %s after 0-index line %d" % (path, i))
print("inserts: OK")
PY
echo "exit=$?"
```
Expected (0-index anchors today are 276 for `dev-flow` and 270 for `dev-flow-worktree`; the reconstruction check in Step 5 matches on text, so different line numbers are fine as long as it stays green):
```text
inserted into plugins/dev-flow/skills/dev-flow/SKILL.md after 0-index line 276
inserted into plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md after 0-index line 270
inserts: OK
exit=0
```

- [ ] **Step 3: Bump `dev-flow` version 2.14.0 → 2.15.0**

Edit `plugins/dev-flow/.claude-plugin/plugin.json`: change the line `"version": "2.14.0",` to `"version": "2.15.0",`. Change nothing else — the `name` and `description` stay byte-for-byte. (This is a whole-value replacement; the design gives no fenced block for it because design step 3 asserts the bumped value directly.)

- [ ] **Step 4: Bump `dev-flow-worktree` version 1.16.0 → 1.17.0**

Edit `plugins/dev-flow-worktree/.claude-plugin/plugin.json`: change the line `"version": "1.16.0",` to `"version": "1.17.0",`. Change nothing else — the `name` and `description` stay byte-for-byte.

- [ ] **Step 5: Run the pre-commit-safe verification checks (design steps 1, 2, 4, 5)**

These read the working tree and the base blob, not committed HEAD, so they are meaningful now (before the commit). Do **not** run design step 3 or step 6 here — those read committed HEAD and are covered post-commit in Step 7. Run all four; each must end `exit=0` and print its `OK` line.

**Design step 1 — file scope is exactly the four intended files:**
```sh
python3 - <<'PY'
import subprocess, sys
SCOPE = ["--", ".", ":!docs/superpowers/"]
WANT = sorted([
    "plugins/dev-flow/.claude-plugin/plugin.json",
    "plugins/dev-flow/skills/dev-flow/SKILL.md",
    "plugins/dev-flow-worktree/.claude-plugin/plugin.json",
    "plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md",
])
def git(*a):
    r = subprocess.run(("git",) + a, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(a), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout
base = git("merge-base", "origin/main", "HEAD").strip()
print("base:", base)
changed = sorted(p for p in git("diff", "--name-only", base, *SCOPE).split("\n") if p)
if changed != WANT:
    print("file scope: FAIL -- changed %s, want %s" % (changed, WANT))
    sys.exit(1)
print("file scope: OK")
PY
echo "exit=$?"
```
Expected: a `base:` line with the SHA, then `file scope: OK` and `exit=0`. A stray path (another plugin, `scripts/`, `CONTEXT.md`, `marketplace.json`, `CLAUDE.md`) fails the step and is named.

**Design step 2 — each `SKILL.md` is its base blob with exactly the new bullet inserted after the Command discipline bullet, and the two files stay identical:**
```sh
python3 - <<'PY'
import subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-04-gh-66-verify-after-commit-design.md"
TARGETS = ["plugins/dev-flow/skills/dev-flow/SKILL.md",
           "plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md"]
OPENER = "- **Command discipline:**"

def git(*a):
    return subprocess.run(("git",) + a, capture_output=True, text=True, encoding="utf-8", check=True).stdout
def split(t):
    o = t.split("\n")
    if o and o[-1] == "":
        o.pop()
    return o

base = git("merge-base", "origin/main", "HEAD").strip()
bullet = read_blocks(DESIGN, [1])[0][0]
bad = []
for path in TARGETS:
    old = split(git("show", base + ":" + path))
    new = split(Path(path).read_text(encoding="utf-8"))
    idx = [i for i, ln in enumerate(old) if ln.startswith(OPENER)]
    if len(idx) != 1:
        bad.append("%s: base has %d Command discipline openers, want exactly 1" % (path, len(idx)))
        continue
    i = idx[0]
    expected = old[:i + 1] + [bullet] + old[i + 1:]
    if new != expected:
        bad.append("%s is not its base blob with the Verification ordering bullet inserted after the Command discipline bullet" % path)
    if len(new) != len(old) + 1:
        bad.append("%s changed line count %d -> %d; the insert must add exactly one line" % (path, len(old), len(new)))
    if i >= len(new) or new[i] != old[i]:
        bad.append("%s changed the Command discipline bullet; the insert must leave it byte-for-byte" % path)
    if new.count(bullet) != 1:
        bad.append("%s holds the inserted bullet %d times after the edit, want exactly 1" % (path, new.count(bullet)))
    if any(bullet == ln for ln in old):
        bad.append("%s already carried the inserted bullet at the base" % path)
for why in bad:
    print("MISMATCH:", why)
print("reconstruction:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```
Expected: exactly `reconstruction: OK` and `exit=0`. If the shape guard trips instead (`design code-block shape is …`), the design was edited after this plan captured its shape — **stop and report**.

**Design step 4 — `check-sync.py` still passes (regression guard; it reads none of the four edited files):**
```sh
python3 scripts/check-sync.py
echo "exit=$?"
```
Expected (byte-for-byte the base output):
```text
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)
check-sync: mirror pair "adversarial-review-seed agent" ... OK (19 lines, 0 declared exceptions)
check-sync: mirror pair "adversarial-review-resolver agent" ... OK (25 lines, 0 declared exceptions)
check-sync: all checks passed
exit=0
```

**Design step 5 — `claude plugin validate .` exits 0 with exactly 8 author warnings:**
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
    bad.append("exit %d, want 0" % r.returncode)
if n != WANT_WARNINGS:
    bad.append("%d author warnings, want exactly %d" % (n, WANT_WARNINGS))
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

If any of these four checks fails, fix the edit and re-run — do **not** commit until all four are green.

- [ ] **Step 6: Commit all four files as one atomic commit**

Stage exactly the four edited files and commit them together. This is the single commit; do not split it, and do not stage anything else. (The design and this plan under `docs/superpowers/` are committed separately by the dev-flow pipeline per `docs: commit`; do not add them here.)

Run:
```bash
git add plugins/dev-flow/skills/dev-flow/SKILL.md \
        plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md \
        plugins/dev-flow/.claude-plugin/plugin.json \
        plugins/dev-flow-worktree/.claude-plugin/plugin.json
git commit -m "$(cat <<'EOF'
gh-66: a committed-HEAD verification step runs after the commit, not before

Add one Verification ordering bullet to dev-flow's Cross-Cutting Concerns
(mirrored byte-identically in dev-flow-worktree): a verification step that
reads committed HEAD (git show HEAD:...) must run after the task's commit,
never in the pre-commit sweep, or it reads the pre-edit committed state and
reports a spurious FAIL. Surfaced by gh-45 (PR #64).

Both plugins bump a minor version because their behaviour text changed:
dev-flow 2.14.0 -> 2.15.0, dev-flow-worktree 1.16.0 -> 1.17.0.
marketplace.json carries description, not version, and no description
changes, so it is untouched.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```
Expected: one commit created with the four files. Confirm with `git show --stat HEAD` that exactly those four paths appear and nothing else.

- [ ] **Step 7: Run the post-commit verification checks (design steps 3 and 6)**

These read committed HEAD (`git show HEAD:…` and `check-version-bump.py`'s `git diff merge-base..HEAD`), so per the very rule this change adds they are meaningful only **after** the Step 6 commit. Both must end `exit=0`.

**Design step 3 — both versions bumped, both descriptions unchanged, `marketplace.json` untouched:**
```sh
python3 - <<'PY'
import json, subprocess, sys
WANT = {"dev-flow": ("2.14.0", "2.15.0"), "dev-flow-worktree": ("1.16.0", "1.17.0")}
MAN = "plugins/%s/.claude-plugin/plugin.json"
def git(*a):
    return subprocess.run(("git",) + a, capture_output=True, text=True, encoding="utf-8", check=True).stdout
def field(rev, name, key):
    return json.loads(git("show", "%s:%s" % (rev, MAN % name)))[key]
base = git("merge-base", "origin/main", "HEAD").strip()
bad = []
for name, (b, h) in WANT.items():
    if field(base, name, "version") != b:
        bad.append("%s base version %s, want %s" % (name, field(base, name, "version"), b))
    if field("HEAD", name, "version") != h:
        bad.append("%s HEAD version %s, want %s" % (name, field("HEAD", name, "version"), h))
    if field("HEAD", name, "description") != field(base, name, "description"):
        bad.append("%s description changed" % name)
if git("show", base + ":.claude-plugin/marketplace.json") != git("show", "HEAD:.claude-plugin/marketplace.json"):
    bad.append(".claude-plugin/marketplace.json changed")
for why in bad:
    print("MISMATCH:", why)
print("versions:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```
Expected:
```text
versions: OK
exit=0
```
(Run **before** the commit this step spuriously FAILs with `dev-flow HEAD version 2.14.0, want 2.15.0` etc. — that is exactly the hazard the new bullet names. If you see that, you ran it too early: commit first, then re-run. Do **not** "fix" it by bumping a second time.)

**Design step 6 — `check-version-bump.py` reports both plugins ahead:**
```sh
python3 scripts/check-version-bump.py origin/main
echo "exit=$?"
```
Expected (short SHAs are the program's own live output):
```text
check-version-bump: base <sha>, head <sha>, merge-base <sha>
  dev-flow             2.14.0 -> 2.15.0 ... OK
  dev-flow-worktree    1.16.0 -> 1.17.0 ... OK
check-version-bump: 2 compared, 0 skipped ... OK
exit=0
```
(Run **before** the commit, this single-commit change has committed nothing, so `git diff merge-base..HEAD` is empty, `touched()` finds no plugin directory, and the script passes *vacuously* — `no plugin directory touched ... OK` — having verified no bump. That is why it too must run post-commit: only then is the touched set non-empty and the check meaningful. Pass `origin/main` as the symbolic ref shown — never a captured `$( )`.)

**Acceptance gate (all must hold after Step 7):** design steps 0, 1, 2 green (block shape, four-file scope, reconstruction of **both** `SKILL.md`), step 3 green (both versions bumped, both descriptions unchanged, `marketplace.json` unchanged), step 4 green (`check-sync.py`), step 5 green (`claude plugin validate .` → exit 0, exactly 8 author warnings), step 6 green (`check-version-bump.py origin/main`). The change is a pure insertion, so there is no removed text to grep for; the meaningful direction — that the added bullet was not already present — is asserted by step 2 (base blob carries it zero times).

---

## Self-Review

**1. Spec coverage.** The design's four file edits (both `SKILL.md` inserts, both `plugin.json` bumps) are all in Task 1's Files block and Steps 2–4. The design's Verification steps 0–6 map to Task 1 Steps 1, 5, and 7: step 0 → Step 1; steps 1, 2, 4, 5 (pre-commit-safe) → Step 5; steps 3, 6 (post-commit) → Step 7. The single-commit constraint and the verification-ordering split (pre- vs post-commit) are honored by the Step 5 → Step 6 (commit) → Step 7 sequence. `marketplace.json`, `CLAUDE.md`, `scripts/`, `CONTEXT.md`, `docs/adr/`, `.github/` are out of scope and are guarded by design step 1's scope-equality and step 3's `marketplace.json` byte-equality. No gaps.

**2. Placeholder scan.** No TBD/TODO/"handle edge cases"/"similar to Task N". The bullet bytes are not retyped — they are read from the design via `read_blocks` in Steps 2 and 5, satisfying the design's "never reconstruct" clause. Every code step carries the exact command and its expected output.

**3. Type/name consistency.** The anchor opener `- **Command discipline:**`, the design path `docs/superpowers/specs/2026-08-04-gh-66-verify-after-commit-design.md`, the four target paths, the version pairs (2.14.0→2.15.0, 1.16.0→1.17.0), and the block shape `[1]` are identical everywhere they appear across the task and match the design. The insertion in Step 2 and the reconstruction in Step 5 use the same `OPENER`, the same `read_blocks(DESIGN, [1])[0][0]` bullet, and the same trailing-newline handling, so what Step 2 writes is exactly what Step 5 asserts.

**4. Self-sufficiency (dev-flow Stage 2 rule).** Task 1 is the only task and carries everything it needs in-section: the four file paths, the design's absolute path with the verbatim-read clause for block 0, the literal version pairs, and every verification command inlined (design steps 0–6) rather than referenced. The Global Constraints section is explicitly marked non-load-bearing and its contents are duplicated into Task 1. No out-of-section pointer is relied on.
