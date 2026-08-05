---
dev-flow:
  slug: gh-51-55-verification-helpers
  stops: [pre-merge]
  docs: commit
---

# gh-51/55 — the byte-for-byte blob check made a shared helper, and the validator warning-count made a CI-enforced check

Close **#55** and **#51** by turning two verification snippets that every change re-types into shared, correct-by-default seams:

- **#55** — the `## Verifying a change` "Always" bullet asks for a **byte-for-byte** merge-base-blob comparison, but every implementation is line-for-line and two real deviations pass undetected: a lost final newline, and a CRLF→LF whole-file change. New `scripts/verify_blob.py` reads both sides as **raw bytes** (no universal-newline translation) and does the byte comparison; the per-change reconstruction keeps only its own splice. `CLAUDE.md` line 16 gains a sentence pointing at it — the same shape line 17 already uses for `read_blocks`.
- **#51** — `claude plugin validate .` exits 0 whether or not it warns, so the "8 missing-author warnings are expected" fact is enforced by no exit code, and every change re-types a six-line wrapper with the count `8` hand-typed. The count is a **filesystem fact** — how many `plugin.json` files lack an `author` key — so it does not need the validator to measure it. A new `check_authors` check inside `scripts/check-sync.py` counts author-less manifests and tripwires the count against a named constant. Because CI already runs `check-sync.py` on every PR, a new author-less plugin (or a removed author key) turns CI **red on the introducing PR** — the enforcement gap the validator leaves open, closed. `CLAUDE.md` line 11 points at that check instead of stating the number.

Three files change: `CLAUDE.md` (two same-line replacements), a new `scripts/verify_blob.py`, and an added check in the existing `scripts/check-sync.py`. **No file under `plugins/` is touched, so no plugin version is bumped** — confirmed against `scripts/check-version-bump.py`, below. Each of those is a conclusion, not a deferral; see *Out of scope*.

## Decomposition — two issues, one theme, still separable

The two issues are combined per explicit user direction, and they share one theme: **each turns a verification step that does not differ per change from a hand-retyped snippet into a shared, correct-by-default seam.** For #55 that seam is a shared reader in `scripts/` — the exact precedent `scripts/design_blocks.py` set. For #51 it is a check in the CI-run `scripts/check-sync.py`, which is *stronger* than a shared helper a caller must remember to import: it fires automatically. Both are the same move — hoist the part that never varies out of the per-change text — landing at the seam each fact actually wants.

They are **separable**, and this is recorded so a reviewer may split them without loss:

- #55 touches `CLAUDE.md` line 16 and adds `scripts/verify_blob.py`; #51 touches `CLAUDE.md` line 11 and adds a check to `scripts/check-sync.py`. The two `CLAUDE.md` edits are different lines and do not overlap; the two script changes are different files.
- There is **no ordering dependency** between them and no shared file except `CLAUDE.md` (disjoint lines). `verify_blob.py` and the `check-sync.py` change do not reference each other.
- If a review flips either issue to no-change, that issue's section becomes its closing comment and its edits are dropped, leaving the other fully coherent.

They are kept together only because both establish the same "hoist the invariant part to its right seam" pattern, reviewed once.

## The shared frame both issues rest on

`scripts/design_blocks.py` is the governing precedent, and its module docstring states the principle:

> The block-to-file mapping and the assertions each target must satisfy differ per change and stay in that check; only the reader is shared.

Both fixes carry exactly the part that does **not** differ per change, to the seam that fact belongs at:

- **#55.** The read-both-sides-and-compare step is identical every time; only the reconstruction (which block lands on which line) is per-change. The bug lives entirely in the shared part — the retyped `split()` and the text-mode reads — so sharing it as a `scripts/` helper is what makes it correct once instead of wrong many times. `verify_blob` carries the reads and the byte comparison; the per-change check keeps the splice.
- **#51.** The validator wrapper's command, warning string, and assertion shape are fixed; only the expected count is a repo fact, and it changes when a plugin is added or an author key is set — never when a change is made. But the thing #51 wants noticed — a plugin gaining or losing author attribution — is a filesystem fact that needs no validator to measure, so its right seam is not a per-change helper but the CI-run drift checker `check-sync.py`, whose whole charter is "mechanical drift check for the facts this repo duplicates by hand." The author-less count is exactly such a fact.

`verify_blob` mirrors `design_blocks.py`'s discipline: a module docstring that states why it exists and how to call it, and failure that exits non-zero with **one line on stderr, never a traceback**. The `check-sync.py` addition mirrors that file's own discipline: a `(summary, problems)` check wired into `main`, pure stdlib, deterministic, CI-run.

## Issue #55 — byte-for-byte is implemented line-for-line

### Problem

`CLAUDE.md` line 16 (the "Always" bullet under `## Verifying a change`) states the rule in **bytes**: *"assert that every file the edit touches is byte-for-byte its merge-base blob … with exactly the intended edit applied."* Every implementation in the repo is **line-for-line**: both sides are read in text mode and split on `"\n"` with a trailing-empty-string pop. Two real deviations pass undetected:

1. **A lost final newline.** `split("a\nb\n")` and `split("a\nb")` both pop to `["a", "b"]`, so a file whose last byte was dropped compares equal.
2. **A CRLF→LF change.** Python's universal-newline translation rewrites `\r\n`→`\n` in `Path.read_text()` and in `subprocess(text=True)` before any comparison, so a whole-file line-ending flip compares equal.

Both live in the **read-and-split** step. The block-level assertions elsewhere in a reconstruction check (`sec[2] == "- " + …`) genuinely operate on `str` and want to stay `str`; only the whole-file equality needs to be byte-exact.

### Approaches considered

- **A — Correct the wording to "line-for-line."** If line granularity is the right level for a prose repo (as `check-sync.py` itself is line-based), the wart is the word, not the scripts. **Rejected as the primary fix.** It weakens a stated guarantee rather than meeting it, and it discards a real signal: the two deviations are exactly the kind a prose repo with no formatter and no `.editorconfig` can acquire from an editor silently. The word "byte-for-byte" is a correct *intent*; the implementations, not the intent, are what is wrong.
- **B — Pure bytes: read both sides as bytes, build the expected side as bytes, compare bytes throughout.** Catches both deviations. **Rejected.** It forces every reconstruction's block-level assertions to `.encode()` and makes every mismatch message harder to print, for no gain over B-plus-readability: the readable line diff is what makes a failed reconstruction diagnosable ("line 9 replaced by block 0", "34 lines want 29").
- **C — Hybrid, shared: keep the readable line-list reconstruction, add one raw-bytes whole-file equality, and put the shared read in `scripts/`. — chosen.** A new `scripts/verify_blob.py` reads both sides as raw bytes (no translation) and provides lossless `bytes`↔`lines` conversions, so a per-change check reconstructs the **expected bytes** and asserts byte equality, while still deriving a readable line diff for the message. The word "byte-for-byte" becomes literally true, both deviations are caught, and the fix is inherited rather than retyped. This is the hybrid the issue leans toward, made a shared seam.

### The chosen change

**New file `scripts/verify_blob.py`.** Its public surface is exactly the operations a per-change check needs — `blob`, `to_lines`, `reconstructed`, and the pure `compare` its self-test drives — and nothing that could be used to reconstruct-and-compare in a way that skips bytes. The two byte/line plumbing helpers (`_worktree`, `_to_bytes`) are underscore-private, the way `design_blocks.py` keeps `_blocks` private behind the public `read_blocks`: a caller who reads the working tree by hand (`_worktree`) or builds bytes to compare against a text-mode read (`_to_bytes`) is precisely how the byte-for-byte guarantee gets bypassed, so neither is caller API.

`to_lines` and `_to_bytes` are exact inverses given the base blob's trailing-newline convention, so a per-change check round-trips any UTF-8 file that uses `"\n"` as its only separator. `compare` is the pure byte-for-byte decision, factored out — the sibling of nothing else in this PR now, but modelled on the same "pure decision, testable without I/O" discipline the review asked for: it takes pre-read bytes, so the self-test drives it with synthetic `actual_bytes` and no temp-file ceremony, and it covers its own branchy message-builder deterministically. `reconstructed` is then a thin I/O wrapper: it reads the working tree once and defers the whole decision to `compare`. On a mismatch `compare` returns a readable problem list — a first-differing-line or line-count message when the line lists disagree, and the explicit **"lines match but bytes differ"** diagnosis when only a trailing newline or a line ending moved, which is precisely the case the line list cannot see. `blob` guards an empty `rev` at the shared seam, so every future caller inherits it: `git show ":path"` with an empty rev reads the git **index**, exits 0, and returns bytes — a silent false-positive pass, exactly the empty-computed-ref hazard the repo's Command-discipline rule names — so `blob` refuses an empty rev loudly rather than comparing against the staging area.

```python
#!/usr/bin/env python3
"""Newline-faithful reads and reconstruction for the byte-for-byte blob check.

CLAUDE.md's `## Verifying a change` "Always" rule asks that every file an edit
touches be *byte-for-byte* its merge-base blob with exactly the intended edit
applied. Every hand-written implementation of it reads both sides in text mode
and splits on "\n" with a trailing-empty-string pop, which is line-for-line,
not byte-for-byte: two real deviations pass undetected.

  - A lost final newline. split("a\nb\n") and split("a\nb") pop to the same
    line list, so a file whose last byte was dropped compares equal.
  - A CRLF->LF change. Python's universal-newline translation rewrites "\r\n"
    to "\n" in Path.read_text() and in subprocess(text=True) before any
    comparison, so a whole-file line-ending flip compares equal.

Both live in the read-and-split step, which does NOT differ per change -- only
the reconstruction (which design block goes on which line) does. So the read
is shared here, the way scripts/design_blocks.py shares the block reader, and
the per-change check keeps only its own splice:

    import sys
    from pathlib import Path
    sys.path.insert(0, "scripts")
    from verify_blob import blob, to_lines, reconstructed
    base = ...                              # a resolved git ref, never empty
    base_bytes = blob(base, "CLAUDE.md")
    old = to_lines(base_bytes)
    new = old[:10] + [BLOCK] + old[11:]     # the per-change reconstruction
    bad = reconstructed("CLAUDE.md", new, base_bytes)   # [] on a byte match

`reconstructed` reads the working tree and defers to the pure `compare`, which
joins `new` with "\n" and the base blob's own trailing-newline convention and
asserts the two byte strings are equal -- the assertion the word "byte-for-byte"
names. When they differ it returns a readable problem list: a first-differing-
line or line-count message when the line lists disagree, and the explicit
"lines match, bytes differ" diagnosis when only a trailing newline or a line
ending moved -- the two deviations the line list cannot see. `compare` takes
pre-read bytes so a self-test can drive it without a working-tree file, the
`--selftest` entry point below does exactly that.

The public surface is `blob`, `to_lines`, `reconstructed`, `compare`; every one
is safe to call because none of them can reconstruct-and-compare in a way that
misses bytes. The two that can -- `_worktree` (hands you bytes to compare
however you like) and `_to_bytes` (builds bytes you might compare against a
text-mode read) -- are private, as design_blocks.py keeps `_blocks` private.

Every read here is raw bytes: git blobs via `git show` with text=False, working
trees via Path.read_bytes(). No universal-newline translation touches either
side. Paths are taken as given. An empty `rev` is refused, not passed to git,
because `git show ":path"` reads the index and would pass silently. Every other
failure -- a blob that cannot be read, a working-tree file that cannot be read,
bytes that are not valid UTF-8 -- exits non-zero with one line on stderr rather
than a traceback.

Design: docs/superpowers/specs/2026-08-04-gh-51-55-verification-helpers-design.md
"""

import subprocess
import sys
from pathlib import Path


def blob(rev, path):
    """The raw bytes of `path` at git `rev`. No newline translation (text=False).
    An empty `rev` is refused: `git show ":path"` reads the index, not a
    merge-base blob, and would pass silently. A git failure exits non-zero with
    one stderr line, never a traceback."""
    if not rev:
        raise SystemExit('verify_blob: empty rev -- a resolved git ref is required; '
                         'git show ":%s" reads the index, not a merge-base blob, and '
                         'would pass silently' % path)
    result = subprocess.run(("git", "show", "%s:%s" % (rev, path)),
                            capture_output=True)
    if result.returncode != 0:
        raise SystemExit("verify_blob: cannot read %s:%s -- %s"
                         % (rev, path,
                            result.stderr.decode("utf-8", "replace").strip()
                            or "(no message)"))
    return result.stdout


def _worktree(path):
    """The raw working-tree bytes of `path`. No newline translation. Internal to
    `reconstructed`: a caller reconstructs through `reconstructed`/`compare`,
    which own the byte comparison -- reading the working tree here and comparing
    it by hand is how the byte-for-byte guarantee gets bypassed."""
    try:
        return Path(path).read_bytes()
    except OSError as e:
        raise SystemExit("verify_blob: cannot read %s -- %s" % (path, e))


def to_lines(data):
    """`data` (raw bytes) decoded UTF-8 and split on "\n", dropping the one
    trailing empty string a final newline produces. The readable view; NOT
    byte-faithful alone -- pair it with `_to_bytes` and the trailing flag, which
    together round-trip any UTF-8 bytes using "\n" as the only separator."""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as e:
        raise SystemExit("verify_blob: not valid UTF-8: %s" % e)
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return lines


def _to_bytes(lines, trailing):
    """The exact inverse of to_lines given the base blob's trailing-newline
    convention: join with "\n", add a final "\n" iff `trailing`, encode UTF-8."""
    return ("\n".join(lines) + ("\n" if trailing else "")).encode("utf-8")


def compare(expected_lines, base_bytes, actual_bytes, label="the working-tree file"):
    """The pure byte-for-byte decision, factored out so it is testable without a
    working-tree file. Returns the problems (possibly empty) with `actual_bytes`
    against `expected_lines` joined using the base blob's own trailing-newline
    convention. [] means a byte-for-byte match; otherwise a readable problem
    list. The byte comparison is the guarantee; the line list only shapes the
    message."""
    expected = _to_bytes(expected_lines, base_bytes.endswith(b"\n"))
    if actual_bytes == expected:
        return []
    problems = ["%s is not byte-for-byte its base blob with the intended edit applied"
                % label]
    actual_lines = to_lines(actual_bytes)
    if actual_lines != expected_lines:
        if len(actual_lines) != len(expected_lines):
            problems.append("  line count: file has %d, want %d"
                            % (len(actual_lines), len(expected_lines)))
        first = next((i for i in range(min(len(actual_lines), len(expected_lines)))
                      if actual_lines[i] != expected_lines[i]), None)
        if first is not None:
            problems.append("  first differing line %d:" % (first + 1))
            problems.append("    file: %r" % actual_lines[first])
            problems.append("    want: %r" % expected_lines[first])
    else:
        problems.append("  lines match but bytes differ: a trailing-newline or "
                        "line-ending deviation the line comparison cannot see")
    return problems


def reconstructed(path, expected_lines, base_bytes):
    """Assert `path`'s working-tree bytes equal `expected_lines` joined with the
    base blob's own trailing-newline convention. Returns [] on a byte-for-byte
    match, else a readable problem list (see `compare`). Thin I/O wrapper: it
    reads the working tree, then defers the whole decision to the pure `compare`."""
    return compare(expected_lines, base_bytes, _worktree(path), label=path)


if __name__ == "__main__":
    # `python3 scripts/verify_blob.py --selftest` drives the pure `compare` with
    # synthetic actual_bytes (correct / lost-newline / CRLF) against a fixed base
    # blob, contrasting each with the old line-for-line snippet. Contract: the
    # control case passes both ways; each deviation passes the old line check and
    # FAILs compare, with "lines match but bytes differ" named on the lost newline
    # and a visible \r on the CRLF (Verification step 5). Body written at execute
    # time to reproduce that contract.
    if "--selftest" not in sys.argv:
        raise SystemExit("verify_blob is import-only; pass --selftest to run its test")
    raise SystemExit(_selftest())
```

**`CLAUDE.md` line 16 — the new "Always" bullet.** This is a **pure append**: every byte of the existing bullet is carried over unchanged and one sentence is added, pointing at the shared helper the way line 17 points at `read_blocks`. Because it removes nothing, *Verification* step 2 makes the stronger assertion a removed-phrase grep cannot — that the base line is a strict prefix of this block. It is **block 0** of this design (plain fenced, shape `[1, …]`):

```
- **Always:** grep for the exact phrases the edit removes, expecting no hits, and assert that every file the edit touches is byte-for-byte its merge-base blob (nothing, for a file it creates) with exactly the intended edit applied. The other checks here prove that edit landed; only this one proves nothing else did. Read both sides as raw bytes — text mode translates `\r\n`→`\n` and a trailing-newline-dropping split hides a lost final newline, so a line-list comparison is not byte-for-byte: `sys.path.insert(0, "scripts")` and use `verify_blob` (`blob(base, path)`, `to_lines`, `reconstructed`) for the read-and-compare, which does not differ per change — only the reconstruction that splices your edit in does.
```

## Issue #51 — the validator exits 0 with warnings, so the count is unenforced

### Problem

`claude plugin validate .` exits **0** whether or not it emits warnings, so `CLAUDE.md`'s "the 8 missing-author warnings are expected" is a fact no exit code enforces. A 9th warning — a new plugin, or an author key removed from a manifest — passes silently. Every design that runs the validator re-types the same six-line `python3` wrapper, with the count `8` hand-typed each time. Unlike the block-conformance and reconstruction checks, this wrapper's content is **identical across changes**: the command is fixed, the warning string is fixed, and the expected count is a repo fact.

Crucially, the fact the count measures — *how many plugins lack an `author` key* — is a **filesystem fact**, readable straight from the `plugin.json` files. It does not need `claude plugin validate` to observe it, and that reframing is what unlocks the right seam.

### Approaches considered

- **A — Drop the count; assert only exit 0.** Cheapest. **Rejected.** `validate` exits 0 even while warning, so an exit-0 assertion alone catches nothing the command does not already do — it would pass on 8, 9, or 800 warnings. It loses the only signal that would notice an author key going missing, which the issue names as the reason not to do this.
- **B1 — A third check inside `scripts/check-sync.py` that shells out to `claude plugin validate .`.** Reuses the workflow that already runs `check-sync.py` on every PR, but **rejected on CI reality.** The GitHub Actions runners have no `claude` CLI (`.github/workflows/check-sync.yml` runs `python3 scripts/check-sync.py` on stock `ubuntu-latest`). A `check-sync.py` that shells out to `claude` would either **fail CI** (command not found) or need a skip-when-absent guard that **silently no-ops on exactly the runner meant to enforce it**. It would also break `check-sync.py`'s clean contract (pure stdlib, deterministic).
- **B2 — A third check inside `scripts/check-sync.py` that reads the `plugin.json` files directly. — chosen.** Because the author-less count is a filesystem fact, the check needs no `claude` at all: it globs `plugins/*/.claude-plugin/plugin.json` (the glob `check_manifests()` already performs), counts those lacking an `author` key, and tripwires the count against a named constant `EXPECTED_AUTHORLESS_PLUGINS`. Pure stdlib, deterministic, CI-run. A new author-less plugin makes the count diverge from the constant, turning CI **red on the introducing PR** — the enforcement the validator can never provide. This is the seam #51's own body pointed at: *"CI covers it — check-sync.yml already runs check-sync.py on every PR, so a third check costs no new workflow."*
- **C — A standalone local `scripts/check-validate.py` wrapping the real validator, not wired into CI.** A contributor and the pipeline run it at commit time; it fails loudly when `claude` is absent. **Rejected in favor of B2.** It leaves the enforcement gap open (a mis-authored plugin merges green unless someone remembered to run the local check), which violates the rubric's "prefer correct-by-default seams over designs where each caller must remember a manual step." Once the count is a CI-enforced filesystem check, a local validator wrapper has no remaining unique job — `claude plugin validate .` is still run before committing per `CLAUDE.md` line 11 for its schema checks, but its warning *count* is no longer the thing anyone must remember to assert.

### Why B2 is equivalent to the validator warning, and why the constant is a tripwire

**The manifest count equals the validator's warning count — by construction, not coincidence.** `claude plugin validate .` emits one `No author information provided` warning per **marketplace entry** whose `plugin.json` lacks author info. `check-sync.py`'s existing Check A enforces a **bijection** between marketplace entries and plugin directories (every directory registered, every entry backed by a directory, names matching). So in any check-sync-passing state, `#marketplace-entries == #plugin-dirs`, and the count of author-less `plugin.json` files equals the validator's warning count. Confirmed live today: 8 of 8 `plugin.json` files lack an `author` key, and `claude plugin validate .` emits exactly 8 warnings and exits 0. The one divergence — an `author` key *present but malformed* — is an exotic, deliberate-to-create edge the rubric says to skip; plain key-absence matches the validator's current behavior and all 8 live manifests.

**The constant is a hand-set tripwire, not a derived value.** `check_authors` could compute an "expected" count from the same manifests it reads, but that would make a newly added author-less plugin *self-consistent* and pass silently — destroying the "notice a new plugin" signal #51 exists to preserve. So `EXPECTED_AUTHORLESS_PLUGINS = 8` is a constant a human bumps deliberately, the way `check-version-bump.py`'s floors are set. A change that adds an author-less plugin or drops an author key must bump it, and until it does, CI is red — which is the tripwire firing. The comparison itself is factored into a pure `author_problems(count, expected)` so the criterion is demonstrably able to fail (Verification step 6) without mutating the tree.

### The chosen change

**Modify `scripts/check-sync.py` — add a third check, `check_authors`.** It sits beside `check_manifests` and `check_pair`, is wired into `main`'s report loop as `"author attribution"`, and touches neither `MIRROR_PAIRS` nor the existing checks. The module docstring's check enumeration goes from two to three. `check-sync.py` is not a mirrored file and lives under `scripts/`, so this touches no plugin and no version (A4). The additions:

```python
# Number of plugins whose plugin.json carries no `author` key. A hand-set
# tripwire, not a value derived from the tree: a change that adds an author-less
# plugin or drops an author key must bump this deliberately, which is the signal
# #51 exists to preserve. It equals the `No author information provided` count
# `claude plugin validate .` warns on -- Check A's marketplace<->dir bijection
# makes the two counts identical -- but needs no validator to measure.
EXPECTED_AUTHORLESS_PLUGINS = 8


def author_problems(count, expected):
    """The pure decision, factored out so the criterion is testable without the
    tree: the problems (possibly empty) with `count` author-less plugins against
    the `expected` tripwire."""
    if count == expected:
        return []
    return ["%d plugin.json files lack an \"author\" key, want exactly %d -- bump "
            "EXPECTED_AUTHORLESS_PLUGINS deliberately if a plugin was added or an "
            "author key set" % (count, expected)]


def check_authors():
    """Returns (summary, problems). Counts plugin.json files with no top-level
    `author` key and tripwires the count against EXPECTED_AUTHORLESS_PLUGINS --
    the count `claude plugin validate .` warns on but exits 0 for, so nothing
    else enforces it."""
    manifests = sorted((REPO_ROOT / "plugins").glob("*/.claude-plugin/plugin.json"))
    problems, authorless = [], []
    for manifest in manifests:
        rel = manifest.relative_to(REPO_ROOT).as_posix()
        try:
            data = json.loads(read_text(rel))
        except READ_ERRORS as exc:
            problems.append(f"cannot read {rel}: {exc}")
            continue
        except json.JSONDecodeError as exc:
            problems.append(f"cannot parse {rel}: {exc}")
            continue
        if not (isinstance(data, dict) and "author" in data):
            authorless.append(rel)
    problems.extend(author_problems(len(authorless), EXPECTED_AUTHORLESS_PLUGINS))
    return plural(len(authorless), "author-less plugin"), problems
```

Wired into `main` alongside the existing reports (after `check_manifests`):

```python
    summary, problems = check_authors()
    if not report("author attribution", summary, problems):
        failures += 1
```

And the module docstring's enumeration changes from "Two independent checks" to "Three independent checks", adding:

```text
  Check C  the number of plugins/<dir>/.claude-plugin/plugin.json files with no
           `author` key equals the EXPECTED_AUTHORLESS_PLUGINS tripwire -- the
           `No author information provided` count `claude plugin validate .`
           warns on but exits 0 for, so nothing else enforces it.
```

**`CLAUDE.md` line 11 — the new validate bullet.** This **replaces** the line in full, dropping the bare number for a pointer at the CI-enforced check. It is **block 1** of this design:

```
- Validate before committing: `claude plugin validate .` — checks the marketplace and every entry. It exits 0 even when it warns, so the expected `No author information provided` count (one per author-less plugin) is enforced mechanically by `scripts/check-sync.py`'s author check, which CI runs on every PR: adding an author-less plugin or setting an author key turns it red until its `EXPECTED_AUTHORLESS_PLUGINS` constant is bumped deliberately.
```

## Assumptions

- **A1. Targets as of the merge base (`7f78af0` today).** `CLAUDE.md` line 11 is the validate bullet; line 16 is the "Always" bullet under `## Verifying a change`; line 17 is the design-doc bullet, unchanged. The implementation matches on **text, not line number**: step 2 reconstructs each changed prose file from its merge-base blob via `verify_blob`, so a base that moved and shifted the lines fails loudly instead of editing the wrong one.
- **A2. No test framework exists in this repo** (`CLAUDE.md` line 3). *Verification* below is the whole correctness surface, which is why `verify_blob` ships a `--selftest` demonstrating it flags the exact deviations it targets, and why `check_authors`'s decision is factored into a pure `author_problems` driven with wrong counts.
- **A3.** `claude plugin validate .` emitting exactly 8 `No author information provided` warnings and exiting 0 is the expected pass state today; `check-sync.py`'s author check tripwires the equal manifest count. Confirmed real: 8 of 8 `plugin.json` files lack an `author` key, and the validator emits 8 warnings (measured while this document was written).
- **A4. No plugin file changes, so no version is bumped.** All three touched files sit outside `plugins/` — `CLAUDE.md`, `scripts/verify_blob.py`, `scripts/check-sync.py`. `scripts/check-version-bump.py` only requires a bump for a plugin whose `plugins/<name>/` directory the change contributes a path under — its `touched()` collects `parts[0] == "plugins"` paths only — so a change confined to `CLAUDE.md` and `scripts/` touches no plugin and needs no bump. A conclusion, not a deferral; step 8 asserts it.
- **A5. `claude` is available where this design's own #51 measurement runs, but not on CI runners.** This is why #51's enforcement is a pure-stdlib check in `check-sync.py`, not a `claude` shell-out — the CI runner has no `claude`, and B2 needs none. In this authoring environment `claude` resolves on `PATH`, so the validator count in A3 was measured directly.
- **A6. Neither issue is a no-change ruling.** Both ship code and close on merge; the PR body carries the reasoning. If a review flips either to no-change, that issue's section becomes its closing comment verbatim, and its edits are dropped (they are separable — see *Decomposition*).
- **A7. Text assertions use `git`/`python3`, not bare `grep`.** Under Claude Code's Bash tool bare `grep` is a ugrep-backed shell function whose output layout is not reliable for per-file assertions; exact assertions are made in `python3` or `git grep`, where they are byte-exact.
- **A8. This design's own plain fenced blocks are 0 (`CLAUDE.md` line 16, an append) and 1 (`CLAUDE.md` line 11, a replacement), shape `[1, 1]`.** No expectation below depends on a block's *character* content except through assertions that derive the expected side from git or read the block from this design on disk, so a review that rewrites either block's new text leaves every check runnable as written. A review that adds or removes a **line** in either block changes the shape and trips step 0, which halts. Every source block (`verify_blob.py`, the `check-sync.py` additions) and every command/output block is given in a language-tagged fence (`python`, `sh`, `text`), invisible to `read_blocks`, which counts only plain untagged blocks.
- **A9. The design and plan are committed on this branch** (`docs: commit`), so every scope check and residue grep excludes `docs/superpowers/` with a pathspec — this document quotes the removed phrase and both blocks and would otherwise sit in the changed set.
- **A10. `origin/main` is fetchable at implementation time.** Steps 1, 2 and 8 resolve the base or a published version from it and fail loudly — naming the command, its exit status and git's message — rather than silently comparing against a stale ref.
- **A11. #39 is merged, so the `## Verifying a change` section both fixes build on is already live.** #55 and #51 each record that they sequence after #39 — the change that gave this repo's verification rules a top-level home. #39 is closed and the section is present in `CLAUDE.md` (line 14; the "Always" bullet #55 appends to is line 16 under it), so nothing here waits on it.

## Out of scope

Hard-excluded. A proposal touching any of these is a blocker, not a design.

- **`plugins/`, `.claude-plugin/`, and every `plugin.json`** — no plugin text changes and no version moves (A4). `check_authors` *reads* the `plugin.json` files but changes none of them, and it lives in `scripts/`.
- **`scripts/check-sync.py`'s existing checks** — Check A (`check_manifests`) and Check B (`check_pair`) and `MIRROR_PAIRS` are untouched; `check_authors` is added beside them. No `description` and no mirror-pair changes.
- **`scripts/design_blocks.py`** — *used* by step 2's block reader and *not* modified. `verify_blob` is a sibling to it, not an edit of it: the two share a discipline (a shared reader, per-change assertions kept out) but carry different concerns (design blocks vs. blob bytes).
- **`.github/`** — no CI change. `check-sync.yml` already runs `check-sync.py` on every PR; adding a check inside that script needs no workflow edit and adds no `claude` dependency (B2, not B1).
- **A standalone `scripts/check-validate.py`** — not created. #51's enforcement is the CI-run `check_authors`, not a local wrapper a contributor must remember to run (Approach C, rejected).
- **`CONTEXT.md`** — untouched, and no edit is implied. This change coins no repo concept; *verify*, *blob*, *validate*, *author*, *warning* are ordinary vocabulary, and the glossary defines shapes this repo reasons about rather than one row per word.
- **`docs/adr/`** — no ADR is warranted. Neither change reverses a recorded decision or establishes an architectural constraint; both are conventions about how a change is verified.
- **`.claude-plugin/marketplace.json`** — untouched, because no `description` changes.
- **The wording of `CLAUDE.md` line 17** (the design-doc bullet) and the `## Verifying a change` heading — unchanged. #55 appends to line 16 only; #51 replaces line 11 only.
- **Every pre-existing file under `docs/superpowers/`** — prior records, one of which (`plans/2026-07-26-gh-8-drift-check-plan.md`) legitimately contains the phrase #51 removes.

## Verification

Every command runs from the repo root, after the edit unless stated. The base is `git merge-base origin/main HEAD` — computed, never hardcoded — and resolves to `7f78af0` today. **Every step that consumes the computed base passes it to `git` as an `argv` element from `python3`, never through a shell** (the repo's command-discipline rule for computed refs): `git merge-base` prints nothing on failure, so an unquoted `$(…)` would degrade a base comparison into a working-tree-vs-index one that passes on a branch committed per task. There is no `$(git …)` substitution below. Each step below can fail, and each one's red output is recorded or specified rather than claimed; steps 1 and 2 collect every mismatch and print them all before exiting.

**0. Block shape — asserted, not reported.** `design_blocks.py`'s CLI is a shape *reporter* that always exits 0; the *guard* is `read_blocks`, where the shape is a required argument and a mismatch is a `SystemExit`. This step calls the guard.

```sh
python3 - <<'PY'
import sys
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
DESIGN = "docs/superpowers/specs/2026-08-04-gh-51-55-verification-helpers-design.md"
for i, b in enumerate(read_blocks(DESIGN, [1, 1])):
    print("  [%d] len=%d: %s" % (i, len(b), b[0][:66]))
print("shape guard: OK")
PY
echo "exit=$?"
```

Expect block 0 previewing the "Always" bullet and block 1 previewing the validate bullet, then `shape guard: OK` and `exit=0`. Anything else means this design was edited after the plan captured its shape — **stop and report**.

**1. File scope — exactly three files, and no fourth.** The `--name-only` set is compared for equality against the authorized list, so a stray edit to `plugins/`, a `plugin.json`, `check-sync.py`'s existing checks, `design_blocks.py`, `CONTEXT.md`, `docs/adr/`, `.github/` or `marketplace.json` fails the step **and names the offending path**. `docs/superpowers/` is excluded by pathspec because the design and plan are committed (A9).

```sh
python3 - <<'PY'
import subprocess, sys
SCOPE = ["--", ".", ":!docs/superpowers/"]
WANT = sorted(["CLAUDE.md", "scripts/check-sync.py", "scripts/verify_blob.py"])
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

Expect a `base:` line carrying a 40-character SHA (`7f78af0…` today), then `file scope: OK` and `exit=0`. Run at the base with no edit applied, `changed` is `[]` and the step FAILs against the three-file `WANT` — the shape of its red run.

**2. Reconstruction, design conformance, and the new file is new.** One program, using the helper this change introduces (`verify_blob`) to check its own edit — the byte-for-byte rule run on the change that adds the byte-for-byte helper:

- `CLAUDE.md` is **byte-for-byte its merge-base blob** with line 16 replaced by block 0 and line 11 replaced by block 1, asserted by `verify_blob.reconstructed` — which is what proves no other line moved;
- `scripts/check-sync.py` is **byte-for-byte its merge-base blob** with exactly the documented additions applied (the constant, `author_problems`, `check_authors`, the two-line `main` wiring, and the docstring's "Two"→"Three" enumeration), asserted the same way — the base blob is read, the additions are spliced at their anchors, and `verify_blob.reconstructed` proves nothing else in the 471-line file moved;
- both `CLAUDE.md` blocks are read **from this design on disk** through `read_blocks`, never retyped;
- block 0 is a **strict extension** of base line 16 (#55 appends, removes nothing); block 1 **differs** from base line 11 and no longer carries the removed phrase (#51 replaces);
- `scripts/verify_blob.py` is **new** — absent at the base blob, the "nothing, for a file it creates" half of the rule; `scripts/check-sync.py` is **present** at the base (modified, not created).

The `CLAUDE.md` blocks come from `read_blocks`; the `check-sync.py` splice recipe (anchors and inserted text) is fixed by *The chosen change* above and is the plan's to render as an exact reconstruction task. Failures of the producers (`git`, `read_blocks`, `verify_blob.blob`) are left to raise as themselves; they name the failing command and no traceback can be mistaken for a pass. Run before the edit exists, `reconstructed` reports `CLAUDE.md`'s first differing line (the working tree still carries old line 11) and exits 1 — the red run; the green run (`reconstruction: OK`, `exit=0`) cannot be produced until `verify_blob` is on disk and both edits are applied.

**3. Residue — #51's removed phrase is gone from shipped text.** #55 removes no phrase (it appends), so there is no #55 residue grep; step 2's strict-extension assertion is its counterpart. #51's replacement drops `The 8 missing-author warnings are expected`, which the new line 11 does not contain. Expect no output and a non-zero exit. The pathspec is required: one prior plan under `docs/superpowers/` legitimately contains the phrase.

```sh
git grep -n -F 'The 8 missing-author warnings are expected' -- . ':!docs/superpowers/'
echo "exit=$?"
```

At the base, before the edit, this same command found the phrase and exited 0 (the red run) — `-n` prints each match as `file:line:content`, so line 11 shows in full:

```text
CLAUDE.md:11:- Validate before committing: `claude plugin validate .` — checks the marketplace and every entry. The 8 missing-author warnings are expected.
exit=0
```

The design and plan under `docs/superpowers/` are excluded by the pathspec.

**4. `python3 scripts/check-sync.py` — green, now including the author check.** This is #51's enforcement, live: the added `check_authors` reports the 8 author-less plugins against the tripwire, and the existing checks are unchanged. Expected output after the edit:

```text
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: author attribution ... OK (8 author-less plugins)
check-sync: mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)
check-sync: mirror pair "adversarial-review-seed agent" ... OK (19 lines, 0 declared exceptions)
check-sync: mirror pair "adversarial-review-resolver agent" ... OK (25 lines, 0 declared exceptions)
check-sync: all checks passed
exit=0
```

Measured at the base (before the edit), the same command prints the four existing lines without the `author attribution` line and exits 0 — the pre-change baseline.

**5. `verify_blob --selftest` — the byte check flags what the line check passed.** For each of #55's two deviations, a corrupted `actual_bytes` is judged both ways against the same LF base blob: the retyped line-for-line snippet (text-mode read + split + trailing pop), and `verify_blob.compare`. Contract of `python3 scripts/verify_blob.py --selftest`:

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
```

Both deviations that the old check passed must FAIL under `verify_blob`, each carrying the diagnosis for its own case — "lines match but bytes differ" for the lost newline, a visible `\r` for the CRLF. The `--selftest` body is written at execute time to reproduce this contract; step 2 asserts `verify_blob.py` is new but does not byte-check its body, so the self-test is reference source the executor completes. (The OLD line-for-line column exercises a real text-mode read to reproduce universal-newline translation honestly — inherent to the snippet being contrasted, not part of `verify_blob.py`'s surface.)

**6. `author_problems` — the #51 criterion can fail.** Drives the pure decision with synthetic counts, so no tree mutation is needed to prove the criterion fails on a wrong count and passes at the true one. `check-sync.py`'s hyphenated name is loaded via `importlib`. Contract:

```text
8 author-less, expect 8 (true state)        -> OK   (no problems)
7 author-less, expect 8 (author key set)    -> FAIL (1 problem)
9 author-less, expect 8 (new plugin)        -> FAIL (1 problem)

author_problems self-test: all cases as expected
```

This is what makes CI's author check a criterion that can go red: a count diverging from `EXPECTED_AUTHORLESS_PLUGINS` returns a non-empty problem list, which `main` reports as FAIL and exits 1.

**7. `python3 scripts/check-version-bump.py origin/main` — no plugin touched, so no bump.** This is A4 made a criterion: the change confines itself to `CLAUDE.md` and `scripts/`, so `check-version-bump.py` finds no `plugins/<name>/` path and passes without asking for a bump. Expected after the edit:

```text
check-version-bump: no plugin directory touched ... OK
exit=0
```

Measured at the base (before any commit) the same command reports `no plugin directory touched ... OK`; after the edit is committed the base stays `origin/main` and the touched set stays empty, since no `plugins/` path is added.

## Files the plan will touch

- **Modify:** `CLAUDE.md` — line 16 replaced by block 0 (a pure append), line 11 replaced by block 1 (a full replacement); nothing else, it stays 35 lines. `scripts/check-sync.py` — add the `EXPECTED_AUTHORLESS_PLUGINS` constant, `author_problems`, `check_authors`, the two-line `main` wiring, and the docstring's two→three enumeration; the existing checks and `MIRROR_PAIRS` unchanged.
- **Create:** `scripts/verify_blob.py`, carrying its self-test in-file behind a `--selftest` path (`python3 scripts/verify_blob.py --selftest`, step 5) — no separate test file, so the changed set stays the three files step 1 asserts.
- **Committed by dev-flow per `docs: commit`:** this design and its plan under `docs/superpowers/`.

Nothing else. No plugin file, no `plugin.json`, no change to `check-sync.py`'s existing checks, no `design_blocks.py`, no `CONTEXT.md`, no `docs/adr/`, no `.github/` file, no `marketplace.json`.

## PR

```text
Close #55 and #51 by hoisting two verification snippets that never vary per
change to the seam each fact belongs at, the way scripts/design_blocks.py carries
the block reader.

#55: CLAUDE.md's "Always" bullet asks for a byte-for-byte merge-base-blob
comparison, but every implementation is line-for-line -- both sides read in text
mode and split on "\n" with a trailing pop. Two real deviations pass: a lost
final newline (both sides pop to the same list) and a CRLF->LF change (universal-
newline translation rewrites \r\n before comparison). Both live in the shared
read step, so new scripts/verify_blob.py reads both sides as raw bytes and does a
byte-for-byte comparison via a pure compare(), keeping a readable line diff for
the message; the per-change reconstruction keeps only its splice. CLAUDE.md line
16 gains one sentence pointing at it, the shape line 17 already uses for
read_blocks.

#51: claude plugin validate . exits 0 whether or not it warns, so the "8 missing-
author warnings are expected" fact is unenforced and every design re-types a
six-line wrapper with the count hand-typed. The count is a filesystem fact -- how
many plugin.json files lack an author key -- so it needs no validator to measure:
a new check_authors in scripts/check-sync.py counts author-less manifests and
tripwires the count against a named EXPECTED_AUTHORLESS_PLUGINS constant. Because
CI already runs check-sync.py on every PR, a new author-less plugin (or a removed
author key) turns CI red on the introducing PR -- the enforcement the validator,
which exits 0 while warning, can never provide. Check A's marketplace<->dir
bijection makes the manifest count equal the validator's warning count. CLAUDE.md
line 11 points at that check instead of stating the number 8.

Three files: CLAUDE.md (two same-line replacements), new scripts/verify_blob.py,
and an added check in the existing scripts/check-sync.py. No plugins/ path is
touched, so no version is bumped -- confirmed against check-version-bump.py,
which only asks for a bump on a plugins/<name>/ change.

Closes #55
Closes #51
```

## Spec self-review

- **Placeholders / TBDs:** none. Both `CLAUDE.md` replacement lines are given in full as plain fenced blocks; `verify_blob.py`'s library source and the `check-sync.py` additions are given in full. `verify_blob.py`'s `--selftest` path is specified by contract — the cases it drives, the verdict per case, and the diagnosis strings that must appear (step 5) — and its exact lines are written at execute time to reproduce that contract; step 2 asserts the file is new but does not byte-check its body, so the `--selftest` code is reference source the executor completes, like the rest of the helper body. Every criterion is runnable, with its expected green output and a recorded or specified red run.

- **Every measurement this document states, and the command that printed it** (per *Measurements are derived, not typed*), each run while this document was written unless marked as an execute-time contract:

  | Measurement | Command / step |
  |---|---|
  | 8 of 8 `plugin.json` files lack an `author` key | `grep -rl '"author"' plugins/*/.claude-plugin/plugin.json` → 0 matches; `ls plugins/*/.claude-plugin/plugin.json` → 8 |
  | `claude plugin validate .` exits 0 with 8 `No author information provided` warnings | the direct validator run (A3, A5) |
  | `check-sync.py` at the base prints 4 check lines (1 manifest, 3 mirror pairs) and passes | step 4's pre-change baseline run |
  | `CLAUDE.md` is 35 lines and ends with a newline | a `read_bytes()` newline count |
  | the removed phrase sits in exactly one file outside `docs/superpowers/` (`CLAUDE.md` line 11) and one plan inside it | step 3's `git grep -n -F` run, scoped in and out of `docs/superpowers/` |
  | no `plugins/` path is touched, so no version bump is required | step 7's `check-version-bump.py` run, plus reading its `touched()` (`parts[0] == "plugins"`) |
  | the merge base is `7f78af0…` | `git merge-base origin/main HEAD` |
  | the block shape is `[1, 1]` | step 0's `read_blocks` guard / reporter |
  | `verify_blob` flags the lost newline and the CRLF the old check passed | step 5's `--selftest` contract (execute-time) |
  | `author_problems` fails on 7/9 and passes at 8 | step 6's contract (execute-time) |
  | `check-sync.py` after the edit adds an `author attribution ... OK (8 author-less plugins)` line | step 4's expected post-edit output (execute-time) |
  | the file scope is exactly the three files | step 1's run |

  No number is typed without a command beside it; the execute-time rows are expected outputs of specified commands, not claimed prior runs.

- **Internal consistency:** block 0 is base line 16 plus one appended sentence — step 2 asserts the strict-prefix relation. Block 1 replaces base line 11 and drops the counted phrase — steps 2 and 3 assert both. The `[1, 1]` shape, the anchor lines 16 and 11, the three-file scope, and the 35-line count agree everywhere they appear. `verify_blob`'s `to_lines`/`_to_bytes` are exact inverses given the trailing flag, which is what makes the reconstruction byte-exact; `compare` is the pure decision `reconstructed` defers to.

- **Scope:** three files. Step 1 checks by file; step 2 checks `CLAUDE.md` and `check-sync.py` line by line against their merge-base blobs and asserts `verify_blob.py` is new. `plugins/`, `check-sync.py`'s existing checks, `design_blocks.py`, `CONTEXT.md`, `docs/adr/`, `.github/`, `marketplace.json`, a standalone `check-validate.py`, and line 17 are each named in *Out of scope* with a reason, each a conclusion rather than a deferral.

- **Ambiguity:** the one place a fresh implementer could go wrong is scope — the removed phrase and both blocks appear in this document. Steps 1 and 3 carry `':!docs/superpowers/'`. The second is which `CLAUDE.md` line each block targets: block 0 → line 16 (append), block 1 → line 11 (replace), stated at each block and asserted by step 2. The third is the `check-sync.py` splice points, fixed by *The chosen change* (constant near `MARKETPLACE`, the two functions beside `check_manifests`, the two-line wiring in `main` after the manifest report, the docstring enumeration) and asserted byte-for-byte by step 2.

- **Positions taken:** #55 gets the hybrid — a shared byte-level read/compare helper (public `blob`/`to_lines`/`reconstructed`/`compare`, private `_worktree`/`_to_bytes`, empty-`rev` guarded) plus the readable line diff — rather than a pure-bytes rewrite (loses readability) or a wording downgrade to "line-for-line" (weakens the guarantee). #51 gets a pure-stdlib, CI-enforced `check_authors` in `check-sync.py` with the count as a hand-set tripwire, rather than a `claude` shell-out in CI (fails/skips on runners with no `claude`), a standalone local wrapper (leaves the enforcement gap the issue set out to close), an auto-derived count (loses the new-plugin signal), or an exit-0-only assertion (catches nothing). The two issues are bundled for one review of the "hoist the invariant to its seam" pattern but recorded as separable. No ADR, no plugin change, no version bump. Nothing is left for the implementer to decide.
