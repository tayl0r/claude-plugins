---
dev-flow:
  slug: verify-blob-dry-run
  stops: [post-design]
  docs: commit
---

# verify-blob: add a `--dry-run` flag

Add a `--dry-run` CLI flag to `scripts/verify_blob.py` and a new public `check` function that owns the exit-code decision for per-change verification. `check(path, expected_lines, base_bytes, dry_run=False)` wraps `reconstructed` and exits non-zero on failure; with `dry_run=True` it prints the problems to stderr and returns them, so the process exits 0. The `--dry-run` CLI flag is confined to the `__main__` block: `python3 scripts/verify_blob.py --selftest --dry-run` runs the self-test and exits 0 even on failure, printing a note that names the outcome. The existing public surface (`blob`, `to_lines`, `reconstructed`, `compare`) and private surface (`_worktree`, `_to_bytes`, `_old_line_check`, `_selftest`) are carried over byte-identically.

One file changes: `scripts/verify_blob.py`. **No file under `plugins/` is touched, so no plugin version is bumped** — confirmed against `scripts/check-version-bump.py`, below.

## Original problem

add a --dry-run flag to the verify-blob helper

## The design question — what does `--dry-run` mean?

`verify_blob.py` is import-only with a single CLI path (`--selftest`). The per-change verification checks are inline `python3 - <<'PY'` heredocs that import the module and call `reconstructed` + manual exit-code handling — they do not take CLI flags. So "add a `--dry-run` flag" needs a defensible interpretation of what the flag attaches to and what it changes.

Two sources of intent bear on the answer:

1. **The executor's friction.** During Execute, a failing per-change check exits non-zero and halts the pipeline; the executor must fix and re-run. A report-only mode (report all problems, exit 0) would let an executor see every deviation in one pass without the stop-and-fix cycle.
2. **The gh-39 precedent.** The plan author validated a verification check *before the edit existed* by "a dry run of the same program against base `0445fb9` while the plan was written, writing to a scratch path outside the repo" — i.e. dry-run = run the check logic against a scratch reconstruction instead of the working tree. `compare` already accepts pre-read bytes, so that capability exists; this design does not need to add it.

### Interpretation chosen: report-only exit mode, owned by `check`'s `dry_run` parameter

`--dry-run` means "run the check but don't fail" — the standard Unix convention (e.g. `make --dry-run`, `rsync --dry-run`). The mechanism is a `dry_run` parameter on a new public `check` function, the standard entry point for per-change verification. `check` wraps `reconstructed` and owns the exit-code decision: it exits non-zero on failure, or — with `dry_run=True` — prints the problems to stderr and returns them, so the process exits 0. The `--dry-run` CLI flag is confined to the `__main__` block, where it makes `--selftest` exit 0 even on failure.

This interpretation is:

- **(a) genuinely useful for the repo's actual workflow.** The primary consumers of `check` are inline heredocs, which pass `dry_run=True` as a keyword argument at the call site — no `sys.argv` manipulation, no wrapper script. The executor can run any migrated check in report-only mode by adding the argument. `--selftest --dry-run` gives the CLI a non-fatal self-test for the same "see the result without the halt" purpose.
- **(b) minimal and consistent with the helper's existing design.** `check` is a thin wrapper around `reconstructed`, following the same "thin I/O wrapper around pure `compare`" layering the module already uses. The exit-code decision moves from the caller (the `assert not bad` pattern) into `check`, where it belongs. No module-level state, no change to `reconstructed` or `compare`, no test framework — the self-test is extended to cover the new behavior.
- **(c) defensible as the obvious reading of "add a --dry-run flag."** A `--dry-run` flag on a verification helper naturally means "run the check but don't fail." The flag attaches to the module's CLI (`__main__` block) exactly as `--selftest` does; the function-level behavior is a parameter because the function's callers are code, not a command line.

### Alternatives considered

- **A — CLI check mode + `--dry-run`.** Add a `--check <path> --base <rev> ...` CLI that runs a verification, where `--dry-run` reports problems but exits 0. **Rejected.** This is a large surface change: it adds a full CLI subcommand to an import-only module, and the per-change checks are inline heredocs that would need to be rewritten as CLI invocations to use it. The heredoc pattern exists for a reason — each check carries its own reconstruction logic (which block goes where), and a CLI would need to encode that logic in arguments, which is exactly the complexity the heredoc avoids.

- **B — A `dry_run` parameter on `reconstructed`/`compare`.** Add a boolean parameter that changes the return type or exit behavior. **Rejected.** `compare` is a pure function that returns a problem list — it never exits, and adding an exit-code concern to it would violate its "pure decision, testable without I/O" contract. `reconstructed` is a thin I/O wrapper that also returns a problem list — the exit code is the *caller's* responsibility, and pushing it down into `reconstructed` would make the function own two concerns (I/O + exit policy). The right seam for the exit-code decision is a new function that wraps `reconstructed`, which is what `check` is.

- **C — A dry-run that doesn't read the working tree (the gh-39 scratch-path pattern).** Add a function that accepts explicit `actual_bytes` instead of reading the working tree, formalizing the "validate a check before the edit exists" pattern. **Rejected as the primary interpretation.** `compare` already accepts pre-read bytes — `compare(expected_lines, base_bytes, actual_bytes)` does exactly this. A new function that only renames `compare`'s signature adds no capability. The gh-39 pattern was the whole applier program writing to a scratch path, not a feature of `verify_blob`. That said, `compare`'s existing pre-read-bytes interface is what makes the gh-39 pattern possible, and this design preserves it unchanged.

- **D — A module-level `_dry_run` flag detected from `sys.argv` at import time.** The flag sets a module-level boolean that `check` reads. **Rejected.** The primary consumers of `check` are inline heredocs, where `sys.argv` is `[""]` at import — getting `--dry-run` into it requires an unspecified workaround (a `python3 -c` wrapper or a new script), pushing the integration problem onto the executor. A parameter is the correct-by-default seam: the caller controls the behavior at the call site, with no dependence on process state. The module-level flag also couples `check`'s behavior to ambient state, making it less testable and less composable.

- **E — `--dry-run` affects only `--selftest`.** The flag makes `python3 scripts/verify_blob.py --selftest --dry-run` exit 0 even on failure, and does nothing else. **Rejected as the *only* behavior.** The self-test is a development tool for `verify_blob.py` itself — it is not run in the pipeline. A flag that only affects the self-test does not address the executor's friction (the pipeline-halting failure). The `check` function is the part that serves the pipeline; the flag on `--selftest` is a small, essentially-free convenience on top.

- **F — Environment variable instead of a CLI flag.** Use `DRY_RUN=1` rather than `--dry-run`. **Rejected.** The task says "flag," not "environment variable." A CLI flag is the natural interface for a script; an environment variable is a side channel that is harder to discover and document.

## The chosen change

**Modify `scripts/verify_blob.py`** — add a new public `check` function and extend the `__main__` block to respect `--dry-run` on the `--selftest` path. The existing public surface (`blob`, `to_lines`, `reconstructed`, `compare`) and private surface (`_worktree`, `_to_bytes`, `_old_line_check`, `_selftest`) are carried over byte-identically from the base blob.

### `check` function

A new public function, sitting beside `reconstructed` in the module. It wraps `reconstructed` and owns the exit-code decision:

```
def check(path, expected_lines, base_bytes, dry_run=False):
    """Run reconstructed. Returns the problem list ([] on a byte-for-byte match).
    On failure, exits non-zero with a readable message -- unless dry_run is True,
    in which case problems are printed to stderr and returned (exit 0). The
    standard entry point for per-change verification checks."""
    problems = reconstructed(path, expected_lines, base_bytes)
    if not problems:
        return problems
    msg = "\n".join(problems)
    if dry_run:
        print(msg, file=sys.stderr)
        return problems
    raise SystemExit(msg)
```

`check` is the standard entry point for per-change verification. It replaces the two-step pattern:

```python
# Old pattern — caller owns the exit code
bad = reconstructed("CLAUDE.md", new, base_bytes)
assert not bad, "\n".join(bad)
```

with a single call:

```python
# New pattern — check owns the exit code
check("CLAUDE.md", new, base_bytes)
```

In normal mode (`dry_run=False`, the default), `check` exits non-zero on failure — the lines after the call are unreachable on failure, so there is no risk of a half-checked file proceeding. In dry-run mode (`dry_run=True`), `check` prints problems to stderr and returns them, so the caller can inspect the problem list and the process exits 0.

Existing checks that use `reconstructed` + manual exit-code handling continue to work unchanged. They can migrate to `check` at their own pace. New checks should use `check`.

### `--selftest` with `--dry-run`

The `__main__` block is extended to detect `--dry-run` and override the exit code:

```
if __name__ == "__main__":
    if "--selftest" not in sys.argv:
        raise SystemExit("verify_blob is import-only; pass --selftest to run its test")
    code = _selftest()
    if "--dry-run" in sys.argv:
        print("verify_blob self-test: %s (dry-run: exiting 0)"
              % ("all cases as expected" if code == 0 else "FAIL"))
        code = 0
    raise SystemExit(code)
```

`_selftest` is unchanged — it runs the same cases, prints the same table, and returns its normal exit code. The `--dry-run` flag only overrides the exit code to 0 and prints a note naming the outcome, so the executor sees every failure without the halt. The note is printed in both outcomes, which is what makes the flag's detection observable (Verification step 4).

### Per-change check migration path

Existing checks are not modified by this change. They continue to use `reconstructed` + manual exit-code handling. The migration path is:

1. Replace `from verify_blob import blob, to_lines, reconstructed` with `from verify_blob import blob, to_lines, check`
2. Replace the `for p in reconstructed(...)` / `assert not bad` / `sys.exit(1 if bad else 0)` block with a single `check(...)` call

A check that has migrated to `check` gets report-only mode by passing `dry_run=True` at the call site — no `sys.argv` manipulation, no wrapper script. The `--dry-run` CLI flag is a `--selftest`-only concern.

## Assumptions

- **A1. Target as of the merge base (computed, never hardcoded).** `scripts/verify_blob.py` is 212 lines, ends with a newline, and carries the public surface `blob`, `to_lines`, `reconstructed`, `compare` plus the private `_worktree`, `_to_bytes`, `_old_line_check`, `_selftest` and the `__main__` block. The implementation matches on **text, not line number**: the reconstruction in Verification step 2 splices the new functions at their anchor points in the base blob's line list, so a base that moved fails loudly instead of editing the wrong lines.
- **A2. No test framework exists in this repo** (`CLAUDE.md` line 3). *Verification* below is the whole correctness surface, which is why `verify_blob` ships a `--selftest` and why this design extends it to cover the new `check` function and `--dry-run` behavior.
- **A3. No plugin file changes, so no version is bumped.** The only touched file is `scripts/verify_blob.py`, which sits outside `plugins/`. `scripts/check-version-bump.py` only requires a bump for a plugin whose `plugins/<name>/` directory the change contributes a path under — its `touched()` collects `parts[0] == "plugins"` paths only — so a change confined to `scripts/` touches no plugin and needs no bump. A conclusion, not a deferral; Verification step 7 asserts it.
- **A4. `origin/main` is fetchable at implementation time.** Steps that resolve the base from it fail loudly — naming the command, its exit status and git's message — rather than silently comparing against a stale ref.
- **A5. The design and plan are committed on this branch** (`docs: commit`), so every scope check and residue grep excludes `docs/superpowers/` with a pathspec.
- **A6. Text assertions use `git`/`python3`, not bare `grep`** (design A7 of the parent design). Under Claude Code's Bash tool bare `grep` is a ugrep-backed shell function whose output layout is not reliable for per-file assertions.
- **A7. This design's own plain fenced blocks are the `check` function (13 lines) and the `__main__` block extension (9 lines) — shape `[13, 9]`.** No expectation below depends on a block's *character* content except through assertions that derive the expected side from git or read the block from this design on disk. Every other fenced block in this document is language-tagged (`sh`, `text`, `python`), invisible to `read_blocks`, which counts only plain untagged blocks.

## Out of scope

Hard-excluded. A proposal touching any of these is a blocker, not a design.

- **`plugins/`, `.claude-plugin/`, and every `plugin.json`** — no plugin text changes and no version moves (A3).
- **`reconstructed` and `compare`** — unchanged. Their signatures, return types, and behavior are preserved exactly. `check` is added beside them, not as a replacement.
- **`blob`, `to_lines`, `_worktree`, `_to_bytes`, `_old_line_check`, `_selftest`** — unchanged. `_selftest` does not gain a parameter; the `--dry-run` override lives entirely in the `__main__` block.
- **Existing per-change verification checks** — not modified. They continue to use `reconstructed` + manual exit-code handling. Migration to `check` is optional and at each check owner's pace.
- **`scripts/design_blocks.py`** — untouched.
- **`scripts/check-sync.py`** — untouched.
- **`CLAUDE.md`** — the `## Verifying a change` section is unchanged. The existing usage example (lines 16–17) shows `reconstructed`, which remains valid. A future change may update the example to show `check`, but that is not part of this change.
- **`CONTEXT.md`** — untouched. This change coins no repo concept; *dry run* and *check* are ordinary vocabulary.
- **`docs/adr/`** — no ADR is warranted. This change adds a flag and a function to an existing helper; it reverses no recorded decision and establishes no architectural constraint.
- **`.github/`** — no CI change.
- **`.claude-plugin/marketplace.json`** — untouched, because no `description` changes.
- **A CLI check mode** (`--check <path> --base <rev>`) — not added. Approach A, rejected. The heredoc pattern is the right seam for per-change reconstruction logic.
- **A module-level `_dry_run` flag** — not added. Approach D, rejected. The `dry_run` parameter on `check` is the correct-by-default seam.

## Verification

Every command runs from the repo root, after the edit unless stated. The base is `git merge-base origin/main HEAD` — computed, never hardcoded. **Every step that consumes the computed base passes it to `git` as an `argv` element from `python3`, never through a shell** (the repo's command-discipline rule for computed refs). Each step below can fail, and each one's red output is recorded or specified rather than claimed.

**0. Block shape — asserted, not reported.** `design_blocks.py`'s CLI is a shape *reporter* that always exits 0; the *guard* is `read_blocks`, where the shape is a required argument and a mismatch is a `SystemExit`. This step calls the guard.

```sh
python3 - <<'PY'
import sys
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
DESIGN = "docs/superpowers/specs/2026-08-08-verify-blob-dry-run-design.md"
for i, b in enumerate(read_blocks(DESIGN, [13, 9])):
    print("  [%d] len=%d: %s" % (i, len(b), b[0][:66]))
print("shape guard: OK")
PY
echo "exit=$?"
```

Expect block 0 previewing the `check` function signature and block 1 previewing the `__main__` block extension, then `shape guard: OK` and `exit=0`. Anything else means this design was edited after the plan captured its shape — **stop and report**.

**1. File scope — exactly one file, and no second.** The `--name-only` set is compared for equality against the authorized list, so a stray edit to `plugins/`, a `plugin.json`, `CLAUDE.md`, `design_blocks.py`, `check-sync.py`, `CONTEXT.md`, `docs/adr/`, `.github/` or `marketplace.json` fails the step **and names the offending path**. `docs/superpowers/` is excluded by pathspec because the design and plan are committed (A5).

```sh
python3 - <<'PY'
import subprocess, sys
SCOPE = ["--", ".", ":!docs/superpowers/"]
WANT = sorted(["scripts/verify_blob.py"])
def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
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

Expect a `base:` line carrying a 40-character SHA (computed at implementation time), then `file scope: OK` and `exit=0`. Run at the base with no edit applied, `changed` is `[]` and the step FAILs against the one-file `WANT` — the shape of its red run.

**2. Reconstruction — `verify_blob.py` is byte-for-byte its merge-base blob with exactly the intended additions applied.** One program, using the helper this change extends to check its own edit — the byte-for-byte rule run on the change that adds the `--dry-run` flag:

- `scripts/verify_blob.py` is **byte-for-byte its merge-base blob** with exactly the documented additions applied: the `check` function (block 0) inserted before `_old_line_check`, and the `__main__` block replaced by block 1;
- both blocks are read **from this design on disk** through `read_blocks`, never retyped;
- the existing public surface (`blob`, `to_lines`, `reconstructed`, `compare`) and private surface (`_worktree`, `_to_bytes`, `_old_line_check`, `_selftest`) are carried over byte-identically from the base blob — the reconstruction splices the new code around them, and `verify_blob.reconstructed` proves nothing else moved.

The reconstruction is specified by anchor points in the base blob's line list, not by line numbers. The anchors are stable ASCII strings that exist exactly once in the base file:

| Addition | Anchor | Mechanics |
|---|---|---|
| `check` function (block 0) | `def _old_line_check(base_bytes, expected_lines, actual_bytes):` | Insert the block, with a blank line before and after, immediately BEFORE the anchor line |
| `__main__` block (block 1) | `if __name__ == "__main__":` | Replace the entire `if __name__ == "__main__":` block — from the `if` line through the last line of the file — with block 1 |

The reconstruction program is the plan's to render as an exact task. Failures of the producers (`git`, `read_blocks`, `verify_blob.blob`) are left to raise as themselves; they name the failing command and no traceback can be mistaken for a pass. Run before the edit exists, `reconstructed` reports the first differing line and exits 1 — the red run; the green run (`reconstruction: OK`, `exit=0`) cannot be produced until the edit is applied.

**3. `--selftest` — green, unchanged behavior without `--dry-run`.** The existing self-test contract is preserved: `python3 scripts/verify_blob.py --selftest` runs the same cases, prints the same table, and exits 0 on success. Expected output (identical to the pre-change contract):

```text
deviation                | OLD line-for-line | NEW verify_blob
------------------------------------------------------------------------------
correct (control)        | pass              | OK
lost final newline       | pass              | FAIL
      the working-tree file is not byte-for-byte its base blob with the intended edit applied
      lines match but bytes differ: a trailing-newline or line-ending deviation the line comparison cannot see
whole file CRLF          | pass              | FAIL
      the working-tree file is not byte-for-byte its base blob with the intended edit applied
      first differing line 1:
      file: '# title\r'
      want: '# title'
verify_blob self-test: all cases as expected
exit=0
```

**4. `--selftest --dry-run` — flag detected, note printed, exit 0.** The `--dry-run` flag is detected from `sys.argv` and the self-test runs normally. The note `(dry-run: exiting 0)` in the output proves the flag was detected — without it, the flag would be silently ignored and the output would be identical to step 3's. On a correct tree the self-test passes and the note names `all cases as expected`.

```sh
python3 scripts/verify_blob.py --selftest --dry-run
echo "exit=$?"
```

Expected: the full self-test table (same output as step 3), followed by `verify_blob self-test: all cases as expected`, then `verify_blob self-test: all cases as expected (dry-run: exiting 0)`, and `exit=0`. The second line is the proof of detection: it appears only when `--dry-run` is in `sys.argv`.

**5. `check` — exits non-zero on failure, exits 0 on failure with `dry_run=True`.** Drives `check` with a correct and an incorrect reconstruction, both with and without `dry_run=True`. The correct reconstruction proves `check` returns `[]` on success; the incorrect reconstruction proves `check` exits non-zero in normal mode and returns the problems (exit 0) in dry-run mode.

```sh
python3 - <<'PY'
import subprocess, sys
sys.path.insert(0, "scripts")
from verify_blob import blob, to_lines, check

def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout

base = git("merge-base", "origin/main", "HEAD").strip()
base_bytes = blob(base, "scripts/verify_blob.py")
lines = to_lines(base_bytes)

# Correct reconstruction: the file IS its base blob (no edit applied yet in
# this step — we're testing check's behavior, not the edit).
result = check("scripts/verify_blob.py", lines, base_bytes)
print("correct reconstruction: problems=%s (want [])" % result)
assert result == [], "expected no problems for correct reconstruction"

# Incorrect reconstruction: drop the last line.
wrong = lines[:-1]
try:
    check("scripts/verify_blob.py", wrong, base_bytes)
    print("incorrect reconstruction, normal mode: DID NOT EXIT (FAIL)")
    sys.exit(1)
except SystemExit as e:
    print("incorrect reconstruction, normal mode: SystemExit (want non-zero) = %s" % (e.code or 1))
    assert e.code != 0, "expected non-zero exit"

print("check behavior, normal mode: OK")
PY
echo "exit=$?"
```

Expected: `correct reconstruction: problems=[] (want [])`, `incorrect reconstruction, normal mode: SystemExit (want non-zero) = ...`, `check behavior, normal mode: OK`, `exit=0`.

Now the dry-run mode — same incorrect reconstruction, but with `dry_run=True`:

```sh
python3 - <<'PY'
import subprocess, sys
sys.path.insert(0, "scripts")
from verify_blob import blob, to_lines, check

def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout

base = git("merge-base", "origin/main", "HEAD").strip()
base_bytes = blob(base, "scripts/verify_blob.py")
lines = to_lines(base_bytes)

# Incorrect reconstruction with dry_run=True: should print problems to stderr
# and return them, NOT exit.
wrong = lines[:-1]
result = check("scripts/verify_blob.py", wrong, base_bytes, dry_run=True)
print("incorrect reconstruction, dry-run mode: problems=%d (want >0)" % len(result))
assert len(result) > 0, "expected problems for incorrect reconstruction"
print("check behavior, dry-run mode: OK (returned problems, did not exit)")
PY
echo "exit=$?"
```

Expected: the problems are printed to stderr (visible in the output), `incorrect reconstruction, dry-run mode: problems=... (want >0)`, `check behavior, dry-run mode: OK (returned problems, did not exit)`, `exit=0`. The key assertion: with `dry_run=True`, `check` returns the problem list instead of raising `SystemExit`, and the process exits 0.

**6. `reconstructed` and `compare` — regression guard, unchanged.** The existing public functions are byte-identical to their pre-change behavior. Drive `compare` with the same synthetic cases the self-test uses, and assert the results match the pre-change contract.

```sh
python3 - <<'PY'
import sys
sys.path.insert(0, "scripts")
from verify_blob import compare, to_lines

base = b"# title\n"
expected = to_lines(base)

# correct
assert compare(expected, base, base) == []
# lost final newline
problems = compare(expected, base, base[:-1])
assert len(problems) > 0
assert any("lines match but bytes differ" in p for p in problems)
# whole file CRLF
problems = compare(expected, base, base.replace(b"\n", b"\r\n"))
assert len(problems) > 0
assert any("\\r" in p for p in problems)

print("compare regression guard: OK (all pre-change contracts hold)")
PY
echo "exit=$?"
```

Expected: `compare regression guard: OK (all pre-change contracts hold)`, `exit=0`.

**7. `python3 scripts/check-version-bump.py origin/main` — no plugin touched, so no bump.** This is A3 made a criterion: the change confines itself to `scripts/verify_blob.py`, so `check-version-bump.py` finds no `plugins/<name>/` path and passes without asking for a bump. Expected after the edit:

```text
check-version-bump: base <sha>, head <sha>, merge-base <sha>
check-version-bump: no plugin directory touched ... OK
exit=0
```

Measured at the base (before any commit) the same command reports `no plugin directory touched ... OK`; after the edit is committed the base stays `origin/main` and the touched set stays empty, since no `plugins/` path is added.

## Files the plan will touch

- **Modify:** `scripts/verify_blob.py` — add the `check` function before `_old_line_check`, and replace the `__main__` block. The existing public surface (`blob`, `to_lines`, `reconstructed`, `compare`) and private surface (`_worktree`, `_to_bytes`, `_old_line_check`, `_selftest`) are carried over byte-identically.
- **Committed by dev-flow per `docs: commit`:** this design and its plan under `docs/superpowers/`.

Nothing else. No plugin file, no `plugin.json`, no `CLAUDE.md`, no `design_blocks.py`, no `check-sync.py`, no `CONTEXT.md`, no `docs/adr/`, no `.github/` file, no `marketplace.json`.

## Spec self-review

- **Placeholders / TBDs:** none. The `check` function and `__main__` block are given in full as plain fenced blocks. Every criterion is runnable, with its expected green output and a recorded or specified red run.

- **Every measurement this document states, and the command that printed it** (per *Measurements are derived, not typed*), each run while this document was written unless marked as an execute-time contract:

  | Measurement | Command / step |
  |---|---|
  | `scripts/verify_blob.py` is 212 lines at the base | `wc -l scripts/verify_blob.py` |
  | the merge base (computed, never hardcoded) | `git merge-base origin/main HEAD` |
  | the block shape is `[13, 9]` | step 0's `read_blocks` guard / reporter |
  | no `plugins/` path is touched, so no version bump is required | step 7's `check-version-bump.py` run, plus reading its `touched()` (`parts[0] == "plugins"`) |
  | `--selftest` without `--dry-run` preserves the pre-change contract | step 3's run (execute-time) |
  | `--selftest --dry-run` prints the detection note and exits 0 | step 4's run (execute-time) |
  | `check` exits non-zero on failure, returns problems on failure with `dry_run=True` | step 5's two runs (execute-time) |
  | `compare` behavior is unchanged | step 6's run (execute-time) |
  | the file scope is exactly `scripts/verify_blob.py` | step 1's run |

  No number is typed without a command beside it; the execute-time rows are expected outputs of specified commands, not claimed prior runs.

- **Internal consistency:** `check` wraps `reconstructed` and owns the exit-code decision — it does not duplicate the comparison logic. The `__main__` block runs `_selftest()` unchanged and overrides the exit code when `--dry-run` is in `sys.argv`; `_selftest` itself is byte-identical to the base. The two plain fenced blocks agree with the anchor-point table in Verification step 2. The file scope (one file) is stated in the preamble, the *Files the plan will touch* section, and step 1.

- **Scope:** one file. Step 1 checks by file; step 2 checks `verify_blob.py` line by line against its merge-base blob. `plugins/`, `CLAUDE.md`, `design_blocks.py`, `check-sync.py`, `CONTEXT.md`, `docs/adr/`, `.github/`, `marketplace.json`, a CLI check mode, and a module-level `_dry_run` flag are each named in *Out of scope* with a reason, each a conclusion rather than a deferral.

- **Ambiguity:** the one place a fresh implementer could go wrong is the anchor points for the reconstruction — which lines the new code is inserted before. The anchor-point table in Verification step 2 gives the exact ASCII strings to match against, each verified to appear exactly once in the base file. The second is the `__main__` block replacement range — the table states it runs from the `if __name__ == "__main__":` line through the last line of the file.

- **Positions taken:** `--dry-run` is a report-only exit mode, not a scratch-path mode (Approach C, rejected — `compare` already accepts pre-read bytes) and not a `reconstructed` parameter (Approach B, rejected — the exit code is the caller's responsibility, and `check` is the right seam for it). The report-only behavior is a `dry_run` parameter on `check`, not a module-level flag read from `sys.argv` (Approach D, rejected — the parameter is the correct-by-default seam for the heredoc consumers). The flag is a CLI flag, not an environment variable (Approach F, rejected — the task says "flag"). A CLI check mode is not added (Approach A, rejected — too large a surface change; the heredoc pattern is the right seam for per-change reconstruction logic). `--dry-run` on `--selftest` is confined to the `__main__` block (Approach E, rejected as the *only* behavior — too narrow to justify a design doc; kept as a small convenience on top of `check`). Existing per-change checks are not modified — migration to `check` is optional. No plugin version is bumped. Nothing is left for the implementer to decide.
