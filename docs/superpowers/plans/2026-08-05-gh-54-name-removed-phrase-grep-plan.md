---
dev-flow: {slug: gh-54-name-removed-phrase-grep, spec: docs/superpowers/specs/2026-08-05-gh-54-name-removed-phrase-grep-design.md}
---

# Give the removed-phrase grep a canonical name (CLAUDE.md + ADR 0001) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Coin the canonical name **the removed-phrase grep** for the one `## Verifying a change` rule that had none, and apply it in the two shipped places the check is named — a 30-byte bold appositive inserted into `CLAUDE.md`'s `**Always:**` bullet, and a one-word swap (`residue-grep` → `removed-phrase grep`, unbolded) in `docs/adr/0001-duplicate-the-two-dev-flow-variants.md`.

**Architecture:** Two one-line documentation edits, both surgical: every other byte of each file stays identical to its merge-base blob. The exact replacement lines are NOT retyped anywhere — they are re-read at execute time from the design doc's two plain fenced blocks (`read_blocks(DESIGN, [1, 1])`, block 0 → `CLAUDE.md`, block 1 → the ADR) and spliced onto the line each file's unique anchor substring matches. Three verification checks — the removed-phrase grep, the `verify_blob` byte-for-byte blob assertion, and the `read_blocks` design-conformance check — are the entire correctness surface (this repo has no test suite beyond `scripts/check-sync.py`, which this change does not engage).

**Tech Stack:** Markdown docs; Python 3 helper scripts already in the repo (`scripts/design_blocks.py` → `read_blocks`; `scripts/verify_blob.py` → `blob`, `to_lines`, `reconstructed`); `git grep`. No new dependencies.

## Global Constraints

Every task's requirements implicitly include this section.

- **Run every command from the repo root** `/Users/taylor/dev/claude-plugins`. `sys.path.insert(0, "scripts")`, the `scripts/…` script paths, the repo-relative git paths (`CLAUDE.md`, `docs/adr/0001-duplicate-the-two-dev-flow-variants.md`), and `read_blocks`' cwd-relative path resolution all assume this.
- **Anchor each edit by its unique substring, NOT by line number.** The clause sits at `CLAUDE.md:16` at HEAD but the issue brief cites line 15; two later PRs pushed it down. Match on content so the edit is correct regardless of drift. CLAUDE.md anchor: `expecting no hits, and assert`. ADR anchor: `the residue-grep and design-conformance rules`.
- **Never retype the replacement text.** Per this repo's `CLAUDE.md` `## Verifying a change`, the replacement lines must be re-read from the design doc's fenced blocks on disk, never retyped. Obtain them via `read_blocks(DESIGN, [1, 1])` (block 0 → `CLAUDE.md`, block 1 → the ADR).
- **No `plugins/` change, no `SKILL.md` change, no `scripts/` change, no version bump.** No file under `plugins/` is touched, so `scripts/check-version-bump.py` requires no bump; the ADR is not a `scripts/check-sync.py` mirror pair, so it carries no sync obligation. The only files this change writes are `CLAUDE.md`, `docs/adr/0001-duplicate-the-two-dev-flow-variants.md`, and (as dev-flow docs) this plan and its spec.
- **The design doc is the authoritative source of the replacement text.** Its absolute path is `/Users/taylor/dev/claude-plugins/docs/superpowers/specs/2026-08-05-gh-54-name-removed-phrase-grep-design.md`. Where a step reads from it: read the referenced block verbatim from the file at that absolute path; never reconstruct or substitute it; if you cannot read the file, stop and report.
- **All three verification checks run against the working tree, after the edit and before the commit.** None of them read `git show HEAD:` (the `verify_blob` blob comes from the merge-base, not HEAD), so no check needs to be gated behind the commit.

---

### Task 1: Coin and apply "the removed-phrase grep" across `CLAUDE.md` and ADR 0001, then verify byte-for-byte

Both edits share the single coined name and the same design-conformance source (the two blocks are read together from one design doc), so they are one task with one shared commit and one verification pass.

**Run every command in this task from the repo root** `/Users/taylor/dev/claude-plugins`. Every step below uses repo-root-relative paths — the `scripts/…` script paths, `sys.path.insert(0, "scripts")`, `Path("CLAUDE.md")` and `Path("docs/adr/0001-duplicate-the-two-dev-flow-variants.md")`, `read_blocks`' cwd-relative resolution, and the `git add` / `git grep` pathspecs — none of which resolve from anywhere else. (`## Global Constraints` states this too, but `task-brief` strips that section from the implementer's brief, so it is restated here.)

**Files:**
- Modify: `CLAUDE.md` — the `**Always:**` bullet of `## Verifying a change` (anchor substring `expecting no hits, and assert`); one line replaced, every other byte identical.
- Modify: `docs/adr/0001-duplicate-the-two-dev-flow-variants.md` — the `## Consequences` pointer line (anchor substring `the residue-grep and design-conformance rules`); one line replaced, every other byte identical.
- Read-only source of replacement text: `/Users/taylor/dev/claude-plugins/docs/superpowers/specs/2026-08-05-gh-54-name-removed-phrase-grep-design.md` (block 0 → `CLAUDE.md`, block 1 → the ADR). Read the referenced blocks verbatim from this file; never reconstruct or substitute them; if you cannot read the file, stop and report.
- Helpers (already in the repo, do not modify): `scripts/design_blocks.py` (`read_blocks`), `scripts/verify_blob.py` (`blob`, `to_lines`, `reconstructed`).

**Interfaces:**
- Consumes: nothing from an earlier task (this is the only task).
- Produces: nothing a later task relies on (this is the only task). The deliverable is the two edited files, verified and committed.

**Preconditions (informational — hold at plan time):** In the working tree, `git grep -c -F 'expecting no hits, and assert' -- CLAUDE.md` is `1` and `git grep -c -i 'residue' -- . ':(exclude)docs/superpowers'` is `1`, so the "expect 0" grep checks below are non-vacuous. `CLAUDE.md` and the ADR are byte-identical to their merge-base blob (base `= git merge-base HEAD origin/main`), so the `verify_blob` "exactly one line changed" assertion is satisfiable.

- [ ] **Step 1: Confirm the design's block shape is `[1, 1]`**

Run:

```bash
python3 scripts/design_blocks.py /Users/taylor/dev/claude-plugins/docs/superpowers/specs/2026-08-05-gh-54-name-removed-phrase-grep-design.md
```

Expected: first line `shape: [1, 1]`; block `[0]` begins `- **Always:** grep for the exact phrases the edit removes, expecting n…` and block `[1]` begins `A one-sided edit to the hand-mirrored pair passes every check in CI. C…`. If the shape is anything other than `[1, 1]`, STOP and report — every edit below is indexed off that shape.

- [ ] **Step 2: Apply both one-line edits, reading each replacement from the design doc**

The replacement lines are re-read from the design via `read_blocks`; they are not typed here. Each file's unique anchor substring locates the single line to replace; the script asserts exactly one match per file and preserves every other byte (splits on `\n` only, restores the file's own trailing-newline convention, writes raw bytes). Run:

```bash
python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
from verify_blob import to_lines

DESIGN = "/Users/taylor/dev/claude-plugins/docs/superpowers/specs/2026-08-05-gh-54-name-removed-phrase-grep-design.md"
blocks = read_blocks(DESIGN, [1, 1])   # exits non-zero if the design's block shape moved

edits = [
    ("CLAUDE.md",
     "expecting no hits, and assert",
     blocks[0][0]),
    ("docs/adr/0001-duplicate-the-two-dev-flow-variants.md",
     "the residue-grep and design-conformance rules",
     blocks[1][0]),
]

for path, anchor, replacement in edits:
    data = Path(path).read_bytes()
    trailing = data.endswith(b"\n")
    lines = to_lines(data)              # the byte-faithful split verify_blob uses in Step 4
    hits = [i for i, ln in enumerate(lines) if anchor in ln]
    if len(hits) != 1:
        raise SystemExit("%s: expected exactly 1 line matching anchor %r, got %d"
                         % (path, anchor, len(hits)))
    lines[hits[0]] = replacement
    out = ("\n".join(lines) + ("\n" if trailing else "")).encode("utf-8")
    Path(path).write_bytes(out)
    print("edited %s (line %d)" % (path, hits[0] + 1))
PY
```

Expected: two lines, `edited CLAUDE.md (line 16)` and `edited docs/adr/0001-duplicate-the-two-dev-flow-variants.md (line 9)`. (The line numbers are informational; correctness comes from the anchor match, not the number.) Any `SystemExit` — a shape mismatch or an anchor that did not match exactly once — means STOP and report.

- [ ] **Step 3: Removed-phrase grep — one scoped target per file (working tree)**

Each edit dissolves one contiguous string that must be gone afterward. Both greps are pre-scoped so committed `docs/superpowers/` history (which legitimately still contains both strings) does not false-positive. Run:

```bash
python3 - <<'PY'
import subprocess

# git grep exit codes: 0 = a match remains (FAIL — the string is still present),
# 1 = no match (PASS), >=2 = git error, e.g. a bad pathspec exits 128 (STOP — an
# error must never read as "clean"). The bare `git grep` this replaces treated
# every nonzero exit as the pass, so a silent git error (empty stdout, exit 128)
# passed falsely.
greps = [
    ("CLAUDE.md phrase",
     ("git", "grep", "-F", "expecting no hits, and assert", "--", "CLAUDE.md")),
    ("residue token",
     ("git", "grep", "-i", "residue", "--", ".", ":(exclude)docs/superpowers")),
]

bad = False
for label, argv in greps:
    r = subprocess.run(argv, capture_output=True, text=True)
    if r.returncode == 1:
        print("PASS (%s): no match" % label)
    elif r.returncode == 0:
        print("FAIL (%s): string still present:\n%s" % (label, r.stdout.rstrip()))
        bad = True
    else:
        print("ERROR (%s): git grep exited %d: %s"
              % (label, r.returncode, r.stderr.strip() or "(no stderr)"))
        bad = True

if bad:
    raise SystemExit("removed-phrase grep did not cleanly pass — STOP and report")
print("removed-phrase grep OK: both strings absent (git grep exit 1, no match)")
PY
```

Expected: three lines — `PASS (CLAUDE.md phrase): no match`, `PASS (residue token): no match`, and the final `removed-phrase grep OK: …` — and exit 0. Each string was present (count `1`) before the edit (see Preconditions), so a `PASS` here is non-vacuous. A `FAIL` (the string survived) or an `ERROR` (git grep exited `>=2` — e.g. a bad pathspec, which exits 128) raises `SystemExit`: STOP and report.

- [ ] **Step 4: `verify_blob` — each file byte-for-byte its merge-base blob with exactly the one intended line replaced**

The merge-base ref is computed as a validated, non-empty variable and passed to git as an argv element (never interpolated into a shell string). For each file the reconstruction finds the anchor line **in the base blob** and splices in that file's replacement block, then asserts the working-tree bytes equal the reconstruction exactly. Run:

```bash
python3 - <<'PY'
import subprocess, sys
sys.path.insert(0, "scripts")
from verify_blob import blob, to_lines, reconstructed
from design_blocks import read_blocks

r = subprocess.run(("git", "merge-base", "HEAD", "origin/main"),
                   capture_output=True, text=True)
if r.returncode != 0:
    raise SystemExit("git merge-base failed: %s" % r.stderr.strip())
base = r.stdout.strip()
if not base:
    raise SystemExit("merge-base is empty; refusing to run verify_blob")

DESIGN = "/Users/taylor/dev/claude-plugins/docs/superpowers/specs/2026-08-05-gh-54-name-removed-phrase-grep-design.md"
blocks = read_blocks(DESIGN, [1, 1])

targets = [
    ("CLAUDE.md",
     "expecting no hits, and assert",
     blocks[0][0]),
    ("docs/adr/0001-duplicate-the-two-dev-flow-variants.md",
     "the residue-grep and design-conformance rules",
     blocks[1][0]),
]

problems = []
for path, anchor, replacement in targets:
    base_bytes = blob(base, path)            # raw bytes of the merge-base blob
    old = to_lines(base_bytes)
    hits = [i for i, ln in enumerate(old) if anchor in ln]
    if len(hits) != 1:
        raise SystemExit("%s: base blob has %d lines matching anchor %r, want 1"
                         % (path, len(hits), anchor))
    new = old[:hits[0]] + [replacement] + old[hits[0] + 1:]
    problems += reconstructed(path, new, base_bytes)   # [] on a byte-for-byte match

if problems:
    print("\n".join(problems))
    raise SystemExit(1)
print("verify_blob OK: CLAUDE.md and the ADR each equal their merge-base blob "
      "(base %s) with exactly the one intended line replaced; every other byte identical" % base)
PY
```

Expected: the single `verify_blob OK: …` line and exit 0. Any problem list (a differing line, a changed line count, or "lines match but bytes differ") means a stray edit landed somewhere — STOP and report.

- [ ] **Step 5: `read_blocks` design-conformance — each replacement appears verbatim in its target**

Re-reads the two blocks from the design (never retyped) and asserts each is present verbatim in the edited file it belongs to. Run:

```bash
python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "/Users/taylor/dev/claude-plugins/docs/superpowers/specs/2026-08-05-gh-54-name-removed-phrase-grep-design.md"
blocks = read_blocks(DESIGN, [1, 1])       # exits non-zero if the shape moved

claude = Path("CLAUDE.md").read_text(encoding="utf-8")
adr = Path("docs/adr/0001-duplicate-the-two-dev-flow-variants.md").read_text(encoding="utf-8")

if blocks[0][0] not in claude:
    raise SystemExit("design block 0 not found verbatim in CLAUDE.md")
if blocks[1][0] not in adr:
    raise SystemExit("design block 1 not found verbatim in the ADR")
print("read_blocks OK: block 0 verbatim in CLAUDE.md; block 1 verbatim in the ADR (shape [1, 1])")
PY
```

Expected: the single `read_blocks OK: …` line and exit 0. Any `SystemExit` means STOP and report.

- [ ] **Step 6: Commit**

Only after Steps 3–5 all pass. Stage the two edited files plus the dev-flow docs (`docs: commit` applies), and commit:

```bash
git add CLAUDE.md \
        docs/adr/0001-duplicate-the-two-dev-flow-variants.md \
        docs/superpowers/specs/2026-08-05-gh-54-name-removed-phrase-grep-design.md \
        docs/superpowers/plans/2026-08-05-gh-54-name-removed-phrase-grep-plan.md
git commit -m "gh-54: name the removed-phrase grep across CLAUDE.md and ADR 0001

Coin 'the removed-phrase grep' as a bold appositive in CLAUDE.md's
Verifying-a-change Always bullet, and align ADR 0001's pointer from
'residue-grep' to the same name (unbolded). Two one-line doc edits;
no plugins/, SKILL.md, or scripts/ change and no version bump.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

Expected: one commit created containing the two edited files and the two dev-flow docs. (If a dev-flow doc is already committed and unchanged, `git add` on it is a harmless no-op.)

---

## Plan self-review (author's check — not part of any task section)

- **Spec coverage.** Anchor 1 (`CLAUDE.md` appositive) → Step 2 (block 0). Anchor 2 (ADR swap) → Step 2 (block 1). Verification approach checks 1/2/3 → Steps 3/4/5, each an executable command with an explicit expected result. Design decisions carried verbatim: anchor-by-content not line number (Global Constraints + every anchor use), replacement text never retyped (blocks re-read in Steps 2, 4, 5), scope limited to the two files with no bump/sync obligation (Global Constraints). The design's out-of-scope items (`plugins/`, `SKILL.md`, `scripts/`, dated `docs/superpowers/` artifacts) are excluded — the ADR grep in Step 3 is explicitly scoped `':(exclude)docs/superpowers'`.
- **No placeholders.** Every step is a runnable command with a stated expected output and a STOP-and-report failure branch.
- **Self-sufficiency.** One task, so there are no cross-task references. Its only external content dependency — the design doc's replacement text — is named by absolute path with the "read verbatim; never reconstruct; stop if unreadable" clause, and the two helper scripts are repo files invoked by stable path. `task-brief` hands the SDD implementer only the text between `### Task 1` and the next heading, stripping `## Global Constraints`; of the constraints there, the steps operationally lean on anchor-by-substring, never-retype, the design's absolute path, the merge-base base, and *run every command from the repo root* — the first four already appear in the steps or Files list, and the repo-root requirement is restated inside the Task 1 section itself. The one remaining Global Constraint (the no-`plugins/` / no-version-bump scope note) is not an instruction any step executes, so its stripping loses nothing. Nothing the task leans on lives only outside its own section.
- **Ordering.** Confirm shape → edit → three working-tree checks → commit. No check reads `git show HEAD:` (the `verify_blob` blob is the merge-base), so none needs to run after the commit.
