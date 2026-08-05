---
dev-flow:
  slug: gh-53-computed-base
  spec: docs/superpowers/specs/2026-08-05-gh-53-computed-base-design.md
---

# A this-change success criterion computes its base (both pipeline SKILL.md copies) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the **Measurements are derived, not typed** bullet in both hand-mirrored pipeline `SKILL.md` copies — a byte-identical two-sentence insertion — so the guidance names the this-change pole of the base-choice axis: a scope / diff / reconstruction check **computes** its base with `git merge-base origin/<default> HEAD`, never a hardcoded SHA. Then bump each plugin's `version` so the version-keyed install cache picks the new text up.

**Architecture:** One prose insertion applied identically to two mirrored files, plus a minor `version` bump in each of the two plugins' manifests. Every edit is surgical: apart from the one replaced bullet line in each `SKILL.md` and the one `version` value in each `plugin.json`, every byte stays identical to its merge-base blob. The bullet's full post-edit text is NOT retyped anywhere in this plan — it is re-read at execute time from the design doc's single plain fenced block (`read_blocks(DESIGN, [1])`, block `0`) and spliced onto the line each file's unique `Measurements are derived, not typed` marker matches. The correctness surface is six checks (this repo has no test suite beyond `scripts/check-*.py`): the removed-phrase grep, the `verify_blob` byte-for-byte blob assertion (both `SKILL.md` copies and, per CLAUDE.md's Always rule, both `plugin.json` files) — which, because it splices in the design's block `0` re-read from disk, doubles as the design-block-conformance check, so no separate `read_blocks` presence check is carried — the two-copy mirror check, the `git diff --name-only <base> HEAD` file-scope check, `scripts/check-version-bump.py`, and `claude plugin validate .`.

**Tech Stack:** Markdown skill docs; small JSON manifests; Python 3 helper scripts already in the repo (`scripts/design_blocks.py` → `read_blocks`; `scripts/verify_blob.py` → `blob`, `to_lines`, `reconstructed`; `scripts/check-version-bump.py`); `grep`; `claude plugin validate`. No new dependencies.

## Global Constraints

Every task's requirements implicitly include this section. This plan has a single task; the task section restates operationally load-bearing constraints inline, because the SDD implementer is handed only the text between the task heading and the next heading and never sees this section.

- **Run every command from the repo root** `/Users/taylor/dev/claude-plugins`. `sys.path.insert(0, "scripts")`, the `scripts/…` script paths, `read_blocks`' cwd-relative path resolution, the repo-relative git pathspecs, and every `plugins/…` path assume this.
- **The insertion is byte-identical in both copies.** The Measurements bullet names no plugin and no routing ref, so both `SKILL.md` copies receive the same bytes. It is a **pure insertion** into the existing single-line bullet — nothing is deleted or reworded.
- **Never retype the bullet text.** Per this repo's `CLAUDE.md` `## Verifying a change`, the replacement line is re-read from the design doc's fenced block on disk, never retyped. Obtain it via `read_blocks(DESIGN, [1])` → block `0` (a single line).
- **Anchor each `SKILL.md` edit by its unique substring `Measurements are derived, not typed`, NOT by line number.** The bullet sits at line 279 in the `dev-flow` copy and 273 in the `dev-flow-worktree` copy; a shifted base must fail loudly rather than edit the wrong line.
- **Bump each plugin's `version` — minor segment, landing strictly past whatever `origin/main` holds at execute time.** No target number is fixed in this plan (the design deliberately dropped it): compute it from `origin/main`'s current version at execute time. `python3 scripts/check-version-bump.py origin/main` is the gate (criterion 5).
- **Scope.** The only files this change writes are the two `SKILL.md` copies, the two `plugin.json` manifests, and (as dev-flow docs, `docs: commit`) this plan and its spec. `scripts/`, `CLAUDE.md`, `CONTEXT.md`, `.claude-plugin/marketplace.json`, both `README.md`s, `docs/adr/`, and the `adversarial-review` mirrored pair are all out of scope.
- **The design doc is the authoritative source of the bullet text.** Its absolute path is `/Users/taylor/dev/claude-plugins/docs/superpowers/specs/2026-08-05-gh-53-computed-base-design.md`. Where a step reads from it: read the referenced block verbatim from the file at that absolute path; never reconstruct or substitute it; if you cannot read the file, stop and report.
- **Verification ordering.** The four working-tree checks (removed-phrase grep, `verify_blob`, mirror, `claude plugin validate .`) run **after the edits and before the commit**. The two committed-HEAD checks — the `git diff --name-only <base> HEAD` file-scope check and `scripts/check-version-bump.py` (which reads `git show HEAD:…`) — read committed HEAD, so they run **after** the commit (pipeline Verification-ordering rule).

---

### Task 1: Insert the this-change base-choice sentences into both SKILL.md copies, bump both plugin versions, verify, commit

The prose insertion and the two version bumps are one atomic change: `scripts/check-version-bump.py` fails any commit that touches a `plugins/<name>/` directory without moving that plugin's `version` past `origin/main`, so editing the two `SKILL.md` copies without the two bumps in the *same commit* is a broken intermediate state a reviewer could not sensibly approve. Hence one task, one commit, one verification pass.

**Run every command in this task from the repo root** `/Users/taylor/dev/claude-plugins`. Every step below uses repo-root-relative paths — `sys.path.insert(0, "scripts")`, the `scripts/…` script paths, `read_blocks`' cwd-relative resolution, the `plugins/…` file paths, and the `git add` / `grep` / `check-version-bump.py` pathspecs — none of which resolve from anywhere else. (`## Global Constraints` states this too, but the SDD implementer's brief is only the text of this task section, so it is restated here.)

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md` — the **Measurements are derived, not typed** bullet (anchor substring `Measurements are derived, not typed`, line 279 today); one line replaced with the design's block `0`, every other byte identical.
- Modify: `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` — the same bullet (anchor substring `Measurements are derived, not typed`, line 273 today); the **byte-identical** replacement, every other byte identical.
- Modify: `plugins/dev-flow/.claude-plugin/plugin.json` — `version` value only; minor bump computed from `origin/main` at execute time, every other byte identical.
- Modify: `plugins/dev-flow-worktree/.claude-plugin/plugin.json` — `version` value only; the same minor-bump rule, every other byte identical.
- Read-only source of the bullet text: `/Users/taylor/dev/claude-plugins/docs/superpowers/specs/2026-08-05-gh-53-computed-base-design.md` (single plain fenced block, shape `[1]`, block `0` → the post-edit bullet, a single line). Read that block verbatim from this file; never reconstruct or substitute it; if you cannot read the file, stop and report.
- Helpers (already in the repo, do not modify): `scripts/design_blocks.py` (`read_blocks`), `scripts/verify_blob.py` (`blob`, `to_lines`, `reconstructed`), `scripts/check-version-bump.py`.

**Interfaces:**
- Consumes: nothing from an earlier task (this is the only task).
- Produces: nothing a later task relies on (this is the only task). The deliverable is the two edited `SKILL.md` copies, the two bumped `plugin.json` manifests, verified and committed together in one commit.

**Preconditions (informational — verified at plan time against the current tree):**
- `python3 scripts/design_blocks.py <design>` reports `shape: [1]`, with block `[0]` beginning `- **Measurements are derived, not typed.** Every measurement an artifa…`. Every splice below is indexed off that shape; the reader exits non-zero if it moved.
- Each `SKILL.md` matches the `Measurements are derived, not typed` marker on exactly one line, and the two bullet lines are currently byte-identical, so the mirror check (Step 6) is satisfiable.
- `grep -c -F "does not show. A spec self-review"` is `1` in each `SKILL.md` (the old sentence junction the pure insertion breaks), so the removed-phrase grep (Step 4) is non-vacuous.
- Both `SKILL.md` copies and both `plugin.json` files are byte-identical to their merge-base blob (base `= git merge-base origin/main HEAD`; at plan-writing time that was `4fab113`, equal to `origin/main`'s tip then — a snapshot for orientation, not a value any step reads: every runtime check recomputes the merge-base), so each `verify_blob` "exactly one line changed" assertion is satisfiable.
- Both plugins' `version` is currently equal to `origin/main`'s (`dev-flow` `2.15.0`, `dev-flow-worktree` `1.17.0`), so a minor bump computed from `origin/main` lands strictly ahead.
- **`origin/main` is assumed current** (the dev-flow pipeline keeps it fetched); criterion 5's `check-version-bump.py origin/main` reads the local `origin/main` ref exactly as this plan does, so no `git fetch` is introduced here.

- [x] **Step 1: Confirm the design's block shape is `[1]`**

Run:

```bash
python3 scripts/design_blocks.py /Users/taylor/dev/claude-plugins/docs/superpowers/specs/2026-08-05-gh-53-computed-base-design.md
```

Expected: first line `shape: [1]`; block `[0]` begins `- **Measurements are derived, not typed.** Every measurement an artifa…`. If the shape is anything other than `[1]`, STOP and report — every splice below is indexed off that shape.

- [x] **Step 2: Apply the byte-identical bullet insertion to both SKILL.md copies**

The replacement line is re-read from the design via `read_blocks`; it is not typed here. Each file's unique `Measurements are derived, not typed` marker locates the single line to replace; the script asserts exactly one match per file, replaces it with the **same** block `0` line in both, and preserves every other byte (splits on `\n` only via `to_lines`, restores each file's own trailing-newline convention, writes raw bytes). Run:

```bash
python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
from verify_blob import to_lines

DESIGN = "/Users/taylor/dev/claude-plugins/docs/superpowers/specs/2026-08-05-gh-53-computed-base-design.md"
blocks = read_blocks(DESIGN, [1])          # exits non-zero if the design's block shape moved
replacement = blocks[0][0]                 # the single post-edit bullet line, read from disk

ANCHOR = "Measurements are derived, not typed"
targets = [
    "plugins/dev-flow/skills/dev-flow/SKILL.md",
    "plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md",
]

for path in targets:
    data = Path(path).read_bytes()
    trailing = data.endswith(b"\n")
    lines = to_lines(data)                 # the byte-faithful split verify_blob uses in Step 5
    hits = [i for i, ln in enumerate(lines) if ANCHOR in ln]
    if len(hits) != 1:
        raise SystemExit("%s: expected exactly 1 line matching %r, got %d"
                         % (path, ANCHOR, len(hits)))
    lines[hits[0]] = replacement
    out = ("\n".join(lines) + ("\n" if trailing else "")).encode("utf-8")
    Path(path).write_bytes(out)
    print("edited %s (line %d)" % (path, hits[0] + 1))
PY
```

Expected: two lines, `edited plugins/dev-flow/skills/dev-flow/SKILL.md (line 279)` and `edited plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md (line 273)`. (Line numbers are informational; correctness comes from the anchor match, not the number.) Any `SystemExit` — a shape mismatch or an anchor that did not match exactly once — means STOP and report.

- [x] **Step 3: Bump both plugins' `version` — minor segment, computed from `origin/main`**

No target number is fixed here. For each plugin the target is `origin/main`'s current version with the **minor** segment incremented and the patch zeroed (e.g. `2.15.0` → `2.16.0`), which lands strictly past `origin/main` even if a concurrent branch already published the next number relative to the merge base. Only the `version` value changes; every other byte of each `plugin.json` is preserved. Run:

```bash
python3 - <<'PY'
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from verify_blob import to_lines

MANIFEST = "plugins/%s/.claude-plugin/plugin.json"
PLUGINS = ["dev-flow", "dev-flow-worktree"]

def origin_version(name):
    path = MANIFEST % name
    r = subprocess.run(("git", "show", "origin/main:%s" % path), capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("cannot read origin/main:%s -- %s" % (path, r.stderr.strip() or "(no message)"))
    v = json.loads(r.stdout).get("version")
    if not isinstance(v, str):
        raise SystemExit("origin/main:%s has no version string" % path)
    return v

def minor_bump(v):
    parts = v.split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        raise SystemExit("version %r is not three dotted-numeric segments (X.Y.Z)" % v)
    return "%d.%d.0" % (int(parts[0]), int(parts[1]) + 1)

for name in PLUGINS:
    path = MANIFEST % name
    ov = origin_version(name)                          # read origin/main's tip once (used below too)
    target = minor_bump(ov)                            # strictly past origin/main
    data = Path(path).read_bytes()
    trailing = data.endswith(b"\n")
    lines = to_lines(data)
    cur = json.loads(data.decode("utf-8")).get("version")
    if not isinstance(cur, str):
        raise SystemExit("%s has no version string" % path)
    hits = [i for i, ln in enumerate(lines) if '"version"' in ln]
    if len(hits) != 1:
        raise SystemExit("%s: expected exactly 1 line containing '\"version\"', got %d"
                         % (path, len(hits)))
    lines[hits[0]] = lines[hits[0]].replace(cur, target, 1)   # swap the single value on the version line
    out = ("\n".join(lines) + ("\n" if trailing else "")).encode("utf-8")
    Path(path).write_bytes(out)
    print("bumped %s: %s -> %s (origin/main was %s)" % (name, cur, target, ov))
PY
```

Expected: two lines, `bumped dev-flow: 2.15.0 -> 2.16.0 (origin/main was 2.15.0)` and `bumped dev-flow-worktree: 1.17.0 -> 1.18.0 (origin/main was 1.17.0)` (the concrete numbers depend on `origin/main` at execute time). Any `SystemExit` means STOP and report.

- [x] **Step 4: Removed-phrase grep — the broken sentence junction is gone from both copies (working tree)**

This is a pure insertion, so the only text that ceases to exist is the old sentence junction `does not show. A spec self-review` (the inserted sentences now sit between `does not show.` and `A spec self-review`). Assert it returns **no** hits in either `SKILL.md`. Run:

```bash
python3 - <<'PY'
import subprocess

# grep exit codes: 0 = a match remains (FAIL — the junction survived), 1 = no match
# (PASS), >=2 = grep error (STOP — an error must never read as "clean").
NEEDLE = "does not show. A spec self-review"
FILES = [
    "plugins/dev-flow/skills/dev-flow/SKILL.md",
    "plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md",
]

bad = False
for path in FILES:
    r = subprocess.run(("grep", "-F", NEEDLE, path), capture_output=True, text=True)
    if r.returncode == 1:
        print("PASS (%s): junction absent" % path)
    elif r.returncode == 0:
        print("FAIL (%s): junction still present:\n%s" % (path, r.stdout.rstrip()))
        bad = True
    else:
        print("ERROR (%s): grep exited %d: %s" % (path, r.returncode, r.stderr.strip() or "(no stderr)"))
        bad = True

if bad:
    raise SystemExit("removed-phrase grep did not cleanly pass — STOP and report")
print("removed-phrase grep OK: junction absent in both copies (grep exit 1)")
PY
```

Expected: `PASS (…)` for each file and the final `removed-phrase grep OK: …`, exit 0. The junction was present once per file before the edit (see Preconditions), so a PASS is non-vacuous. A FAIL (junction survived) or ERROR (grep exit ≥2) raises `SystemExit`: STOP and report.

- [x] **Step 5: `verify_blob` — each touched file byte-for-byte its merge-base blob with exactly the one intended change**

The merge-base ref is computed as a validated, non-empty variable and passed to `git` as an `argv` element (never interpolated into a shell string) — this change dogfooding its own rule. For each `SKILL.md` the reconstruction finds the `Measurements are derived, not typed` marker line **in the base blob** and splices in the design's block `0`; for each `plugin.json` it finds the `"version"` line in the base blob and swaps only its value for **the working tree manifest's own current version value** — read here, never recomputed — so Step 5 verifies structural integrity only: every byte equals the base blob except the version value. That the value is a valid forward bump is Step 3's and Step 10's job, not this check's. Then it asserts the working-tree bytes equal the reconstruction exactly. (The design's criterion 3 names the two `SKILL.md` copies; the two `plugin.json` files are added here because CLAUDE.md's `## Verifying a change` **Always** rule binds *every* file the edit touches, and the design's Affected-files list includes both manifests.) Because the reconstruction splices in the design's block `0` re-read from disk (`read_blocks(DESIGN, [1])[0][0]`, never retyped), a passing `verify_blob` also proves block `0` landed verbatim at the anchor line in both copies — so this step is *also* the design-block-conformance check CLAUDE.md's design-doc rule asks for, and no separate `read_blocks` presence check is carried (it would be a strict consequence of this one). Run:

```bash
python3 - <<'PY'
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from verify_blob import blob, to_lines, reconstructed, compare
from design_blocks import read_blocks

r = subprocess.run(("git", "merge-base", "origin/main", "HEAD"), capture_output=True, text=True)
if r.returncode != 0:
    raise SystemExit("git merge-base failed: %s" % (r.stderr.strip() or "(no message)"))
base = r.stdout.strip()
if not base:
    raise SystemExit("merge-base is empty; refusing to run verify_blob")

DESIGN = "/Users/taylor/dev/claude-plugins/docs/superpowers/specs/2026-08-05-gh-53-computed-base-design.md"
replacement = read_blocks(DESIGN, [1])[0][0]     # the post-edit bullet line, re-read from disk
ANCHOR = "Measurements are derived, not typed"

problems = []

# --- the two SKILL.md copies: one bullet line replaced ---
for path in ["plugins/dev-flow/skills/dev-flow/SKILL.md",
             "plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md"]:
    base_bytes = blob(base, path)
    old = to_lines(base_bytes)
    hits = [i for i, ln in enumerate(old) if ANCHOR in ln]
    if len(hits) != 1:
        raise SystemExit("%s: base blob has %d lines matching %r, want 1" % (path, len(hits), ANCHOR))
    new = old[:hits[0]] + [replacement] + old[hits[0] + 1:]
    problems += reconstructed(path, new, base_bytes)

# --- the two plugin.json manifests: only the version VALUE changed ---
# Step 5 owns structural integrity only: every byte equals the base blob except the
# version value. It does NOT recompute the bump target -- a second minor_bump here
# could disagree with Step 3 under a concurrent release and fail spuriously. Instead
# it reads the working tree's OWN version value and swaps only that onto the base
# version line, so nothing can disagree. That the value is a valid forward bump is
# Step 3's and Step 10's (check-version-bump) concern, not this check's.
for name in ["dev-flow", "dev-flow-worktree"]:
    path = "plugins/%s/.claude-plugin/plugin.json" % name
    base_bytes = blob(base, path)
    base_ver = json.loads(base_bytes.decode("utf-8"))["version"]
    old = to_lines(base_bytes)
    hits = [i for i, ln in enumerate(old) if '"version"' in ln]
    if len(hits) != 1:
        raise SystemExit("%s: base blob has %d version lines, want 1" % (path, len(hits)))
    work_bytes = Path(path).read_bytes()                            # the working tree, read once
    work_ver = json.loads(work_bytes.decode("utf-8"))["version"]    # its own value, never recomputed
    new = old[:hits[0]] + [old[hits[0]].replace(base_ver, work_ver, 1)] + old[hits[0] + 1:]
    problems += compare(new, base_bytes, work_bytes, label=path)

if problems:
    print("\n".join(problems))
    raise SystemExit(1)
print("verify_blob OK: both SKILL.md copies and both plugin.json files equal their "
      "merge-base blob (base %s) with exactly the one intended change each; every other byte identical" % base)
PY
```

Expected: the single `verify_blob OK: …` line and exit 0. Because the `plugin.json` reconstruction swaps in the working tree's own version value rather than a recomputed target, no second computation can disagree with Step 3 — so any problem list (a differing line, a changed line count, or "lines match but bytes differ") means a genuine stray edit landed somewhere. STOP and report.

- [x] **Step 6: The two copies stay mirrored — compare the bullet's bytes, not its line number (working tree)**

`scripts/check-sync.py` does **not** cover this pipeline `SKILL.md` pair (it covers the `adversarial-review` pair and the manifest `description`s only), so verify the mirror directly. The bullet sits at a different line in each copy (279 vs 273), so the comparison must be of the line's **bytes**, never its line number. This is the *outside-the-pair* check CLAUDE.md requires for any mirrored-pair edit — Steps 4 and 5 already verify each copy against the design and its own merge-base blob independently (Step 5 splices in the design's block `0` re-read from disk), so a doubled-but-wrong edit cannot pass unseen; this step confirms the two copies are identical to each other. Run:

```bash
python3 - <<'PY'
import subprocess
NEEDLE = "Measurements are derived, not typed"
FILES = [
    "plugins/dev-flow/skills/dev-flow/SKILL.md",
    "plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md",
]

lines = []
for path in FILES:
    # grep -F (fixed string), NO -n: the whole bullet line with no line-number prefix,
    # so byte-identical bullets compare equal wherever each sits in its file.
    r = subprocess.run(("grep", "-F", NEEDLE, path), capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("%s: grep found no bullet line (exit %d) — STOP and report" % (path, r.returncode))
    out = r.stdout
    if out.count("\n") != 1:
        raise SystemExit("%s: expected exactly one matching line, got %d — STOP and report"
                         % (path, out.count("\n")))
    lines.append(out)

if lines[0] != lines[1]:
    raise SystemExit("MIRROR MISMATCH: the two bullet lines differ byte-for-byte:\n  dev-flow:          %r\n  dev-flow-worktree: %r"
                     % (lines[0], lines[1]))
print("mirror OK: the Measurements bullet is byte-identical in both copies")
PY
```

Expected: the single `mirror OK: …` line and exit 0. This is the robust form of the design's `diff <(grep -F …) <(grep -F …)` criterion — it additionally asserts each grep matched exactly one non-empty line, so a marker that vanished from *both* copies (which would make a bare `diff` of two empty outputs exit 0 spuriously) is caught here. Any `SystemExit` means STOP and report.

- [x] **Step 7: `claude plugin validate .` — the marketplace is still valid (working tree)**

Run:

```bash
claude plugin validate .
```

Expected: exit 0. It validates the marketplace and every entry, and exits 0 even when it warns; the author-less warning count is unchanged (no new plugin, no author key touched). Confirm the exit status is 0:

```bash
claude plugin validate . ; echo "exit: $?"
```

Expected: `exit: 0`. A non-zero exit means STOP and report.

- [x] **Step 8: Commit**

Only after Steps 4–7 all pass. Stage the two edited `SKILL.md` copies, the two bumped `plugin.json` manifests, and the dev-flow docs (`docs: commit` applies), then commit:

```bash
git add plugins/dev-flow/skills/dev-flow/SKILL.md \
        plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md \
        plugins/dev-flow/.claude-plugin/plugin.json \
        plugins/dev-flow-worktree/.claude-plugin/plugin.json \
        docs/superpowers/specs/2026-08-05-gh-53-computed-base-design.md \
        docs/superpowers/plans/2026-08-05-gh-53-computed-base-plan.md
git commit -m "gh-53: a this-change success criterion computes its base, not hardcodes one

Extend the 'Measurements are derived, not typed' bullet in both pipeline
SKILL.md copies (byte-identical insertion) with the this-change pole of the
base-choice axis: a scope / diff / reconstruction check computes its base
with 'git merge-base origin/<default> HEAD' (a computed ref passed to git as
an argv element per Command discipline), never a hardcoded SHA, which would
fail green on rebase or an advancing default branch. Minor version bump for
both plugins so the version-keyed install cache picks up the new text.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

Expected: one commit created containing the two `SKILL.md` copies, the two `plugin.json` manifests, and the two dev-flow docs. (If a dev-flow doc is already committed and unchanged, `git add` on it is a harmless no-op.)

- [x] **Step 9: File scope — exactly the six intended files changed on this branch, and no seventh (committed HEAD)**

This dogfoods the very rule this change adds: a measurement of *the change itself* — here its **file scope** — computes its base with `git merge-base origin/main HEAD` (a computed ref, validated non-empty, passed to `git` as an `argv` element), never a hardcoded SHA, so it keeps measuring what *this branch* changed as `origin/main` advances. It reads committed HEAD (`git diff --name-only <base> HEAD`), so per the Verification-ordering rule it runs **after** the Step 8 commit. The intended set is the four code files plus the two dev-flow docs (design + plan, committed on this branch — Step 8 stages both), so `base..HEAD` lists exactly six; a stray edit to any seventh file (another plugin, `scripts/`, `CLAUDE.md`, `CONTEXT.md`, `marketplace.json`, a `README.md`, `docs/adr/`, the `adversarial-review` pair) makes the set differ and fails the step. `WANT` names the same six paths as Step 8's `git add`. Run:

```bash
python3 - <<'PY'
import subprocess, sys
WANT = sorted([
    "plugins/dev-flow/skills/dev-flow/SKILL.md",
    "plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md",
    "plugins/dev-flow/.claude-plugin/plugin.json",
    "plugins/dev-flow-worktree/.claude-plugin/plugin.json",
    "docs/superpowers/specs/2026-08-05-gh-53-computed-base-design.md",
    "docs/superpowers/plans/2026-08-05-gh-53-computed-base-plan.md",
])
def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout
base = git("merge-base", "origin/main", "HEAD").strip()
if not base:
    raise SystemExit("empty merge-base -- refusing to run a base-relative scope check")
print("base:", base)
changed = sorted(p for p in git("diff", "--name-only", base, "HEAD").split("\n") if p)
if changed != WANT:
    print("file scope: FAIL -- changed %s, want %s" % (changed, WANT))
    sys.exit(1)
print("file scope: OK")
PY
echo "exit=$?"
```

Expected: a `base:` line with the 40-char merge-base SHA, then `file scope: OK` and `exit=0`. A `file scope: FAIL` line naming the differing set — a stray seventh path, or a missing intended file — means STOP and report; do not weaken `WANT` to match a stray. (If `changed` is missing the plan doc, the pipeline has not committed it yet: commit it, then re-run.)

- [x] **Step 10: `check-version-bump.py` — both plugins land past `origin/main` (committed HEAD)**

This check reads `git show HEAD:plugins/<name>/.claude-plugin/plugin.json`, so it must run **after** the commit (Step 8). It compares each touched plugin's HEAD version against `origin/main`'s *tip* (not the merge base) and exits 0 only if both are strictly ahead. Run:

```bash
python3 scripts/check-version-bump.py origin/main ; echo "exit: $?"
```

Expected — a header line, one indented row per touched plugin, a summary line, then `exit: 0` (the concrete versions and SHAs depend on `origin/main` at execute time):

```text
check-version-bump: base <9-hex>, head <9-hex>, merge-base <9-hex>
  dev-flow             2.15.0 -> 2.16.0 ... OK
  dev-flow-worktree    1.17.0 -> 1.18.0 ... OK
check-version-bump: 2 compared, 0 skipped ... OK
exit: 0
```

Each plugin's row ends `... OK` (its version moved past `origin/main`'s tip) and the summary reads `2 compared, 0 skipped ... OK`. A row ending `... FAIL`, a `check-version-bump: N of M compared plugin directories failed` line, or a non-zero exit means the bump does not clear `origin/main`'s tip — a concurrent branch may have published the number, or `origin/main` advanced. STOP and report: recompute the target from the current `origin/main` tip (Step 3's rule), amend the commit, and re-run this step. Do not weaken the check.

---

## Plan self-review (author's check — not part of any task section)

- **Spec coverage.** The one edit (the byte-identical Measurements-bullet insertion) → Steps 1–2 (design block `0`, spliced onto the marker line in both copies). The two version bumps (Affected files) → Step 3. Success criteria 1–6 map to Steps 5 (criterion 1, replacement landed verbatim — the `verify_blob` reconstruction splices in block `0` re-read from the design, so a byte-for-byte pass proves it verbatim at the anchor line, subsuming a separate `read_blocks` presence check), 4 (removed-phrase grep), 5 (byte-for-byte reconstruction, extended to the two `plugin.json` files per CLAUDE.md's Always rule), 6 (mirror), 10 (check-version-bump), 7 (`claude plugin validate .`). A file-scope check (Step 9) is added beyond the design's six criteria: it is correct-by-default over the whole branch — `git diff --name-only <base> HEAD` must equal exactly the six intended files, so a stray edit to any seventh is caught — and it dogfoods this change's own computed-base rule. Design decisions carried verbatim: anchor-by-content not line number (Global Constraints + every anchor use), bullet text never retyped (block re-read in Steps 2 and 5), byte-identical in both copies (Step 2 writes the one `replacement` to both; Step 6 proves it), no hardcoded version (Steps 3/5/9/10 compute from `origin/main`). Out-of-scope files (`scripts/`, `CLAUDE.md`, `CONTEXT.md`, `marketplace.json`, both `README.md`s, `docs/adr/`, the `adversarial-review` pair) are named in Global Constraints, touched by no step, and now positively asserted absent from the change by Step 9's file-scope check.
- **No placeholders.** Every step is a runnable command with a stated expected output and a STOP-and-report failure branch. No target version number is hardcoded — each is computed at execute time, honoring the design's deliberate omission.
- **Type / name consistency.** `read_blocks(DESIGN, [1])[0][0]` (a single line) is used identically in Steps 2 and 5. `minor_bump` now lives only in Step 3 (Step 5 no longer recomputes the target — it reads the working tree's own version value), so there is no second copy to keep in step. The anchor substring `Measurements are derived, not typed` and the `"version"` line anchor are used consistently across edit and verification steps. Step 9's file-scope `WANT` names the same six paths as Step 8's `git add` list.
- **Self-sufficiency.** One task, so there are no cross-task references. Its only external content dependency — the design doc's bullet text — is named by absolute path with the "read verbatim; never reconstruct; stop if unreadable" clause, and every helper is a repo file invoked by stable path. The SDD implementer's brief is only this task section: the run-from-repo-root requirement, the anchor-by-substring rule, the never-retype rule, the design's absolute path, the merge-base base, and the compute-not-hardcode version rule all appear inside the Task 1 section (Files, the intro paragraph, or the step bodies), so nothing the task executes lives only in the stripped `## Global Constraints`.
- **Ordering.** Confirm shape → edit both copies → bump both versions → four working-tree checks (removed-phrase grep, verify_blob, mirror, `claude plugin validate .`) → commit → two committed-HEAD checks (Step 9 `base..HEAD` file scope, Step 10 `check-version-bump.py`). The file-scope check and `check-version-bump.py` both read committed HEAD (`git diff --name-only <base> HEAD` and `git show HEAD:…`), so both are placed after the commit; `verify_blob` reads the merge-base blob and the working tree (never HEAD), so it correctly runs pre-commit.
