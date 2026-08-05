---
dev-flow:
  slug: gh-51-55-verification-helpers
  spec: docs/superpowers/specs/2026-08-04-gh-51-55-verification-helpers-design.md
---

# gh-51/55 — verification helpers: `verify_blob` seam + CI-enforced author tripwire — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn two verification snippets every change re-types into shared, correct-by-default seams — a new `scripts/verify_blob.py` that does a genuine byte-for-byte merge-base-blob comparison (#55), and a new CI-run `check_authors` inside `scripts/check-sync.py` that tripwires the author-less-plugin count (#51) — then point `CLAUDE.md` at both.

**Architecture:** Three files change and no `plugins/` path is touched, so no plugin version is bumped. `scripts/verify_blob.py` is new (reads both sides as raw bytes, no universal-newline translation; public `blob`/`to_lines`/`reconstructed`/`compare`, private `_worktree`/`_to_bytes`; ships a `--selftest`). `scripts/check-sync.py` gains a third check (`EXPECTED_AUTHORLESS_PLUGINS`, `author_problems`, `check_authors`, one `main` wiring, a docstring two→three enumeration) beside its existing Check A / Check B, which are untouched. `CLAUDE.md` line 16 gains one appended sentence (block 0) and line 11 is replaced in full (block 1). There is no test framework — the design's Verification section (steps 0–7) is the whole correctness surface, so `verify_blob` carries a `--selftest` and `author_problems` is a pure decision driven with synthetic counts.

**Tech Stack:** Python 3 stdlib scripts, Markdown, `git` driven from `python3` (`git show`/`git diff`/`git merge-base` as `argv` elements, never shell `$(…)`), and the repo helpers `scripts/design_blocks.py` (`read_blocks`), `scripts/check-sync.py`, `scripts/check-version-bump.py`, plus `claude plugin validate`.

## Global Constraints

> NOTE: This section is orientation for a human reader only. Under this repo's dev-flow Stage 2 rule (`scripts/task-brief`), an implementer sees **only its own `## Task N` section** — this preamble is stripped and never reaches them. Every constraint below is therefore re-inlined verbatim into each task that needs it. Nothing here is load-bearing on its own.

- **Repo root & branch.** Every command in every task runs from the repo root `/Users/taylor/dev/claude-plugins`. You are already on the feature branch `tayl0r/gh-51-55-verification-helpers`. Do not create a worktree or switch branches.
- **Design doc is the authoritative source of every block.** `/Users/taylor/dev/claude-plugins/docs/superpowers/specs/2026-08-04-gh-51-55-verification-helpers-design.md`. Its two **plain (untagged)** fenced blocks are shape `[1, 1]`: block 0 (append to `CLAUDE.md` line 16), block 1 (replace `CLAUDE.md` line 11). Its **language-tagged** fences (`python`, `text`) carry `verify_blob.py`'s source and the `check-sync.py` additions; `read_blocks` cannot see them, so they are read with the small `fenced_block(...)` extractor each task inlines. **Never retype any design block** — read it verbatim from the design on disk; if you cannot read the design, stop and report.
- **Command discipline.** Compute any git ref (the merge base) inside `python3`/`subprocess` and pass it to `git` as an `argv` element, validated non-empty — never an inline `$(git …)`. `git merge-base` prints nothing and exits non-zero on an unresolvable ref, so an unquoted substitution silently degrades a base comparison into a working-tree one.
- **No bare `grep` for assertions.** Under Claude Code's Bash tool bare `grep` is a ugrep-backed function whose output layout is unreliable for per-file assertions. Every load-bearing equality is made in `python3` or with `git grep`.
- **Verification ordering.** Any step that reads committed HEAD (`git show HEAD:…`, `check-version-bump.py`'s `git diff merge-base..HEAD`) must run **after** that task's commit, never before. The reconstruction checks read the **working tree** against the merge-base blob, so they run pre-commit fine.
- **No new tests, no plugin version bump.** This repo has no test framework; the design's Verification steps are the correctness surface. All three touched files sit outside `plugins/`, so `check-version-bump.py` asks for no bump (asserted in Task 4).
- **Scope: exactly three files.** `scripts/verify_blob.py` (new), `scripts/check-sync.py` (modified), `CLAUDE.md` (modified). Nothing under `plugins/`, no `plugin.json`, no `check-sync.py` existing check, no `MIRROR_PAIRS`, no `design_blocks.py`, no `CONTEXT.md`, no `docs/adr/`, no `.github/`, no `marketplace.json`. The design and this plan under `docs/superpowers/` are committed separately by the dev-flow pipeline (`docs: commit`) — do not stage them in any task.

---

## Task 1: Create `scripts/verify_blob.py` (library source verbatim from the design + authored `--selftest`)

**Files:**
- Create: `scripts/verify_blob.py`

**Interfaces:**
- Consumes: nothing — this is the first task.
- Produces, for Tasks 2–4: a module importable via `sys.path.insert(0, "scripts"); from verify_blob import blob, to_lines, reconstructed, compare`.
  - `blob(rev, path) -> bytes` — raw bytes of `path` at git `rev` (no newline translation); refuses an empty `rev`.
  - `to_lines(data: bytes) -> list[str]` — UTF-8 decode, split on `"\n"`, drop the one trailing empty a final newline yields.
  - `reconstructed(path, expected_lines, base_bytes) -> list[str]` — `[]` iff the working-tree bytes of `path` equal `expected_lines` joined with the base blob's own trailing-newline convention; else a readable problem list.
  - `compare(expected_lines, base_bytes, actual_bytes, label=...) -> list[str]` — the pure byte-for-byte decision `reconstructed` defers to.
  - Private (never called by other tasks): `_worktree(path)`, `_to_bytes(lines, trailing)`.

**Repo root & branch (restated — task-brief strips the preamble):** run every command from `/Users/taylor/dev/claude-plugins`; you are on `tayl0r/gh-51-55-verification-helpers`.

**Design doc (authoritative source of the library body):** `/Users/taylor/dev/claude-plugins/docs/superpowers/specs/2026-08-04-gh-51-55-verification-helpers-design.md`. The library source is the single **`python`-tagged** fenced block whose first line is `#!/usr/bin/env python3` (under "## Issue #55 … → ### The chosen change"). **Read that block verbatim from the design file at that path; never reconstruct, reflow, or substitute it; if you cannot read the design file, stop and report.** Step 1 below writes it programmatically so its bytes are never transcribed by hand.

**What Task 1 builds.** The design's library block already contains the module docstring, imports, `blob`, `_worktree`, `to_lines`, `_to_bytes`, `compare`, `reconstructed`, and an `if __name__ == "__main__":` guard whose last line is `raise SystemExit(_selftest())`. That `_selftest` is **deliberately not in the design** — the design leaves the self-test body to execute time (step 5 of its Verification), specified only by contract. So Task 1 = write the library block verbatim, then insert an authored `_selftest` (plus its `_old_line_check` helper) immediately before the `if __name__` guard so it is in scope when the guard calls it.

**The `--selftest` contract this file must satisfy (design Verification step 5).** `python3 scripts/verify_blob.py --selftest` judges three cases against the same LF base blob two ways — the OLD line-for-line snippet (a real text-mode read + `split("\n")` + trailing-empty pop) and the NEW `verify_blob.compare` — and must reproduce exactly:

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

Binding requirements: both deviations the OLD check **passes** must **FAIL** under `verify_blob`; the lost-newline failure names `lines match but bytes differ`; the CRLF failure shows a visible `\r`. On all-pass, `--selftest` prints a final `verify_blob self-test: all cases as expected` and returns 0; on any mismatch it prints `MISMATCH: …` and returns non-zero. (The exact self-test bytes are not byte-checked by any later step, so the reference implementation below is authoritative only insofar as it reproduces this contract — run step 3 and confirm.)

- [ ] **Step 1: Write the library source verbatim from the design**

Extracts the `python` block (first line `#!/usr/bin/env python3`) from the design and writes it to `scripts/verify_blob.py`. Run from the repo root:

```bash
python3 - <<'PY'
from pathlib import Path

DESIGN = "docs/superpowers/specs/2026-08-04-gh-51-55-verification-helpers-design.md"
OUT = "scripts/verify_blob.py"

def fenced_block(design_path, first_prefix):
    """Lines of the unique ```-fenced block (tagged or plain) whose first content
    line startswith first_prefix. Mirrors scripts/design_blocks._blocks: refuses a
    4+-backtick fence and an unclosed fence rather than mis-parsing silently. Exits
    non-zero on 0 or >1 matches."""
    fence = chr(96) * 3
    try:
        text = Path(design_path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise SystemExit("cannot read design %s: %s" % (design_path, e))
    blocks, cur, opened = [], None, 0
    for n, line in enumerate(text.split("\n"), 1):
        s = line.strip()
        if s.startswith(fence + fence[0]):
            raise SystemExit("%s line %d: this reader parses three-backtick fences "
                             "only; a longer one mis-indexes every block after it"
                             % (design_path, n))
        if cur is None:
            if s.startswith(fence):
                cur, opened = [], n
        elif s == fence:
            blocks.append(cur); cur = None
        else:
            cur.append(line)
    if cur is not None:
        raise SystemExit("design %s: the fence opened at line %d is never closed"
                         % (design_path, opened))
    hits = [b for b in blocks if b and b[0].startswith(first_prefix)]
    if len(hits) != 1:
        raise SystemExit("design: %d fenced blocks start with %r, want exactly 1"
                         % (len(hits), first_prefix))
    return hits[0]

src = fenced_block(DESIGN, "#!/usr/bin/env python3")
if len(src) != 161:
    raise SystemExit("design library block is %d lines, want 161 -- the block moved; "
                     "stop and report" % len(src))
if src[-1] != "    raise SystemExit(_selftest())":
    raise SystemExit("design library block does not end with the _selftest guard; "
                     "last line is %r -- stop and report" % src[-1])
Path(OUT).write_text("\n".join(src) + "\n", encoding="utf-8")
print("wrote %s (%d lines, verbatim from the design)" % (OUT, len(src)))
PY
echo "exit=$?"
```

Expected: `wrote scripts/verify_blob.py (161 lines, verbatim from the design)` and `exit=0`. The script asserts both the 161-line count and the `_selftest`-guard last line before writing, so a design whose library block moved exits non-zero here — **stop and report**.

- [ ] **Step 2: Insert the authored `_selftest` (and its `_old_line_check` helper) before the `if __name__` guard**

Open `scripts/verify_blob.py` and insert the two functions below **immediately before** the line `if __name__ == "__main__":` (keep PEP-8 two-blank-line spacing at every top-level boundary — the two blank lines the library block already places before the guard now sit between `reconstructed` and `_old_line_check`; the block below already carries two blank lines between `_old_line_check` and `_selftest`; add two blank lines after `_selftest` so it is not flush against `if __name__`). Do not change any other line. These are authored to reproduce the step-5 contract above; the base blob is `b"# title\n"`, so the sole reconstruction is the file unchanged, and each deviation corrupts `actual_bytes` only:

```python
def _old_line_check(base_bytes, expected_lines, actual_bytes):
    """The retyped line-for-line snippet #55 replaces: write actual_bytes, read it
    back in TEXT mode (universal-newline translation on), split on "\n" with the
    trailing-empty pop, compare the line lists. Returns True on 'pass' -- exactly
    the false pass verify_blob is built to stop."""
    import os
    import tempfile
    fd, tmp = tempfile.mkstemp()
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(actual_bytes)
        text = Path(tmp).read_text(encoding="utf-8")   # text mode: \r\n and \r -> \n
    finally:
        os.unlink(tmp)
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return lines == expected_lines


def _selftest():
    base = b"# title\n"
    expected = to_lines(base)                          # ["# title"]
    cases = [
        # name, actual_bytes, OLD must pass, NEW must be clean, needle NEW must show
        ("correct (control)",  base,                         True, True,  None),
        ("lost final newline", base[:-1],                    True, False, "lines match but bytes differ"),
        ("whole file CRLF",    base.replace(b"\n", b"\r\n"), True, False, "\\r"),
    ]
    print("deviation                | OLD line-for-line | NEW verify_blob")
    print("-" * 78)
    bad = []
    for name, actual, old_ok, new_clean, needle in cases:
        old_pass = _old_line_check(base, expected, actual)
        problems = compare(expected, base, actual)
        print("%-24s | %-17s | %s"
              % (name, "pass" if old_pass else "FAIL", "OK" if not problems else "FAIL"))
        for p in problems:
            print("      " + p.strip())
        if old_pass != old_ok:
            bad.append("%s: OLD line-for-line pass=%s, want %s" % (name, old_pass, old_ok))
        if (not problems) != new_clean:
            bad.append("%s: NEW verify_blob clean=%s, want %s" % (name, not problems, new_clean))
        if needle is not None and not any(needle in p for p in problems):
            bad.append("%s: NEW verify_blob problems missing %r" % (name, needle))
    for why in bad:
        print("MISMATCH:", why)
    print("verify_blob self-test:", "all cases as expected" if not bad else "FAIL")
    return 0 if not bad else 1
```

- [ ] **Step 3: Run the self-test — the byte check flags what the line check passed**

```bash
python3 scripts/verify_blob.py --selftest
echo "exit=$?"
```

Expected: the three-row table exactly as in the contract above — OLD `pass` on every row; NEW `OK` for the control, `FAIL` for the lost newline (with `lines match but bytes differ`) and `FAIL` for the CRLF (with `file: '# title\r'` showing a visible `\r`) — then `verify_blob self-test: all cases as expected` and `exit=0`. If any row disagrees, the self-test prints `MISMATCH: …` and exits 1 — fix the inserted `_selftest`/`_old_line_check` (never the library body, which is verbatim from the design) and re-run.

- [ ] **Step 4: Confirm the module is import-only without `--selftest`**

```bash
python3 scripts/verify_blob.py
echo "exit=$?"
```

Expected: `verify_blob is import-only; pass --selftest to run its test` on stderr and a non-zero exit — the guard from the verbatim library body. This proves only that the import-only guard rejects a no-arg invocation with that message and a non-zero exit; it does **not** exercise `_selftest` (the `if "--selftest" not in sys.argv` branch raises before `_selftest` is ever referenced, so a missing or misplaced `_selftest` would not surface here). Step 3's `--selftest` run — which reaches `raise SystemExit(_selftest())` — is what proves `_selftest` resolves.

- [ ] **Step 5: Commit**

Stage only the new file (the design/plan under `docs/superpowers/` are committed later by the pipeline — do not add them):

```bash
git add scripts/verify_blob.py
git commit -m "$(cat <<'EOF'
gh-55: add scripts/verify_blob.py -- byte-for-byte merge-base-blob helper

The "Always" verifying-a-change rule asks for a byte-for-byte merge-base-blob
comparison, but every hand-written implementation is line-for-line: both sides
read in text mode and split on "\n" with a trailing pop, so a lost final
newline and a whole-file CRLF->LF flip both pass undetected. verify_blob reads
both sides as raw bytes (no universal-newline translation) and does the byte
comparison via a pure compare(), keeping a readable line diff for the message;
per-change checks keep only their own splice. Ships a --selftest that shows the
two deviations the old line check passes now FAIL.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

Expected: one commit containing exactly `scripts/verify_blob.py`. Confirm with `git show --stat HEAD` that only that path appears.

---

## Task 2: Add the `check_authors` tripwire to `scripts/check-sync.py`

**Files:**
- Modify: `scripts/check-sync.py` — add `EXPECTED_AUTHORLESS_PLUGINS`, `author_problems`, `check_authors`, one `main` wiring, and the docstring two→three enumeration. Check A (`check_manifests`), Check B (`check_pair`), and `MIRROR_PAIRS` are untouched.

**Interfaces:**
- Consumes (from Task 1): `sys.path.insert(0, "scripts"); from verify_blob import blob, to_lines, reconstructed` — used only by this task's verification, not by `check-sync.py` itself.
- Produces: `check-sync.py` now reports a third check line, `check-sync: author attribution ... OK (8 author-less plugins)`, between the manifest line and the mirror-pair lines.

**Repo root & branch (restated — task-brief strips the preamble):** run every command from `/Users/taylor/dev/claude-plugins`; you are on `tayl0r/gh-51-55-verification-helpers`.

**Command discipline (restated):** the merge base is computed inside `python3` and passed to `git` as an `argv` element, validated non-empty — never an inline `$(git …)`.

**Design doc (authoritative source of the additions):** `/Users/taylor/dev/claude-plugins/docs/superpowers/specs/2026-08-04-gh-51-55-verification-helpers-design.md`. The additions live in four **tagged** fenced blocks under "## Issue #51 … → ### The chosen change":
- the `python` block whose first line is `# Number of plugins whose plugin.json carries no` — the 7-line `EXPECTED_AUTHORLESS_PLUGINS = 8` constant (6 comment lines + the assignment);
- the `python` block whose first line is `def author_problems(count, expected):` — the two pure functions `author_problems` and `check_authors`, with the PEP-8 blank lines between them;
- the `python` block whose first line is `    summary, problems = check_authors()` — the 3-line `main` wiring;
- the `text` block whose first line is `  Check C  the number of plugins/<dir>/.claude-plugin/plugin` — the 4-line Check C docstring paragraph.

**Read those blocks verbatim from the design file at that path; never reconstruct or substitute them; if you cannot read the design file, stop and report.** Step 1 reads them programmatically with the inlined `fenced_block(...)` extractor, so their bytes are never transcribed by hand.

**Splice recipe (fixed by the design; the builder in Step 1 applies it, the check in Step 2 re-derives and byte-verifies it).** Against the merge-base blob of `scripts/check-sync.py`, the edit is: the docstring line `Two independent checks, one command, no flags:` becomes `Three independent checks, one command, no flags:`; the Check C paragraph is inserted (after one blank line) right after the Check B docstring line ending `canonicalization, except where an exception declares otherwise.`; the constant block is inserted (after one blank line) right after `MARKETPLACE = ".claude-plugin/marketplace.json"`; the `main` wiring is inserted (after one blank line) right after the `failures += 1` that follows `if not report("manifest descriptions", summary, problems):`; and `author_problems` + `check_authors` are inserted (with PEP-8 two-blank spacing) right before `def main():`. Nothing else in the file changes.

- [ ] **Step 1: Apply the additions — build the target from the base blob + the design blocks, and write it**

Reads the base blob, reads the four design blocks verbatim, splices them at the anchors above (anchors located by content, each asserted unique), and writes `scripts/check-sync.py`. Run from the repo root:

```bash
python3 - <<'PY'
import subprocess, sys
from pathlib import Path

DESIGN = "docs/superpowers/specs/2026-08-04-gh-51-55-verification-helpers-design.md"
TARGET = "scripts/check-sync.py"

def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout

def fenced_block(design_path, first_prefix):
    """Lines of the unique ```-fenced block (tagged or plain) whose first content
    line startswith first_prefix. Mirrors scripts/design_blocks._blocks: refuses a
    4+-backtick fence and an unclosed fence rather than mis-parsing silently. Exits
    non-zero on 0 or >1 matches."""
    fence = chr(96) * 3
    try:
        text = Path(design_path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise SystemExit("cannot read design %s: %s" % (design_path, e))
    blocks, cur, opened = [], None, 0
    for n, line in enumerate(text.split("\n"), 1):
        s = line.strip()
        if s.startswith(fence + fence[0]):
            raise SystemExit("%s line %d: this reader parses three-backtick fences "
                             "only; a longer one mis-indexes every block after it"
                             % (design_path, n))
        if cur is None:
            if s.startswith(fence):
                cur, opened = [], n
        elif s == fence:
            blocks.append(cur); cur = None
        else:
            cur.append(line)
    if cur is not None:
        raise SystemExit("design %s: the fence opened at line %d is never closed"
                         % (design_path, opened))
    hits = [b for b in blocks if b and b[0].startswith(first_prefix)]
    if len(hits) != 1:
        raise SystemExit("design: %d fenced blocks start with %r, want exactly 1"
                         % (len(hits), first_prefix))
    return hits[0]

base = git("merge-base", "origin/main", "HEAD").strip()
if not base:
    raise SystemExit("empty merge-base -- refusing to build against an unresolved ref")
base_lines = git("show", "%s:%s" % (base, TARGET)).split("\n")
if base_lines and base_lines[-1] == "":
    base_lines.pop()

# --- the four design blocks, verbatim ---
const_lines = fenced_block(DESIGN, "# Number of plugins whose plugin.json carries no")
func_lines = fenced_block(DESIGN, "def author_problems(count, expected):")
block_wiring = fenced_block(DESIGN, "    summary, problems = check_authors()")
block_checkc = fenced_block(DESIGN, "  Check C  the number of plugins/<dir>/.claude-plugin/plugin")

# --- anchors (located by content; each must be unique) ---
OLD_DOC = "Two independent checks, one command, no flags:"
NEW_DOC = OLD_DOC.replace("Two independent", "Three independent")
def is_checkb_last(l): return l.strip() == "canonicalization, except where an exception declares otherwise."
def is_market(l):      return l == 'MARKETPLACE = ".claude-plugin/marketplace.json"'
def is_manifest_if(l): return l.strip() == 'if not report("manifest descriptions", summary, problems):'
def is_def_main(l):    return l == "def main():"

hits = {"doc": 0, "checkb": 0, "market": 0, "manifest_if": 0, "def_main": 0}
out, after_manifest_if = [], False
for l in base_lines:
    if after_manifest_if:                 # l is the manifest report's `failures += 1`
        out.append(l); out.append(""); out.extend(block_wiring)
        after_manifest_if = False
        continue
    if is_def_main(l):
        hits["def_main"] += 1
        out.extend(func_lines); out.append(""); out.append(""); out.append(l)
        continue
    if l == OLD_DOC:
        hits["doc"] += 1; out.append(NEW_DOC); continue
    out.append(l)
    if is_checkb_last(l):
        hits["checkb"] += 1; out.append(""); out.extend(block_checkc)
    elif is_market(l):
        hits["market"] += 1; out.append(""); out.extend(const_lines)
    elif is_manifest_if(l):
        hits["manifest_if"] += 1; after_manifest_if = True

bad = [k for k, v in hits.items() if v != 1]
if bad:
    raise SystemExit("anchor(s) not unique in base blob: %s (hits=%r) -- stop and report"
                     % (", ".join(bad), hits))

Path(TARGET).write_text("\n".join(out) + "\n", encoding="utf-8")
print("wrote %s: base %d lines -> %d lines; anchors all unique"
      % (TARGET, len(base_lines), len(out)))
PY
echo "exit=$?"
```

Expected: `wrote scripts/check-sync.py: base 471 lines -> 522 lines; anchors all unique` and `exit=0` (line count is base + the spliced blanks and blocks; the exact new count is informational — the byte check in Step 2 is authoritative). Any `anchor(s) not unique` or shape message means the base or the design moved — **stop and report**.

- [ ] **Step 2: Green check — byte-for-byte reconstruction against the base blob (uses `verify_blob`)**

Independently re-derives the target from the base blob + the design blocks and asserts the on-disk file equals it **byte-for-byte** via `verify_blob.reconstructed` — the byte check catching a stray trailing-newline or CRLF the line lists cannot see, and proving nothing outside the spliced additions moved. Run from the repo root:

```bash
python3 - <<'PY'
import subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from verify_blob import blob, to_lines, reconstructed

DESIGN = "docs/superpowers/specs/2026-08-04-gh-51-55-verification-helpers-design.md"
TARGET = "scripts/check-sync.py"

def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout

def fenced_block(design_path, first_prefix):
    """Lines of the unique ```-fenced block (tagged or plain) whose first content
    line startswith first_prefix. Mirrors scripts/design_blocks._blocks: refuses a
    4+-backtick fence and an unclosed fence rather than mis-parsing silently. Exits
    non-zero on 0 or >1 matches."""
    fence = chr(96) * 3
    try:
        text = Path(design_path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise SystemExit("cannot read design %s: %s" % (design_path, e))
    blocks, cur, opened = [], None, 0
    for n, line in enumerate(text.split("\n"), 1):
        s = line.strip()
        if s.startswith(fence + fence[0]):
            raise SystemExit("%s line %d: this reader parses three-backtick fences "
                             "only; a longer one mis-indexes every block after it"
                             % (design_path, n))
        if cur is None:
            if s.startswith(fence):
                cur, opened = [], n
        elif s == fence:
            blocks.append(cur); cur = None
        else:
            cur.append(line)
    if cur is not None:
        raise SystemExit("design %s: the fence opened at line %d is never closed"
                         % (design_path, opened))
    hits = [b for b in blocks if b and b[0].startswith(first_prefix)]
    if len(hits) != 1:
        raise SystemExit("design: %d fenced blocks start with %r, want exactly 1"
                         % (len(hits), first_prefix))
    return hits[0]

base = git("merge-base", "origin/main", "HEAD").strip()
if not base:
    raise SystemExit("empty merge-base -- refusing to reconstruct against an unresolved ref")
base_bytes = blob(base, TARGET)
base_lines = to_lines(base_bytes)

const_lines = fenced_block(DESIGN, "# Number of plugins whose plugin.json carries no")
func_lines = fenced_block(DESIGN, "def author_problems(count, expected):")
block_wiring = fenced_block(DESIGN, "    summary, problems = check_authors()")
block_checkc = fenced_block(DESIGN, "  Check C  the number of plugins/<dir>/.claude-plugin/plugin")

OLD_DOC = "Two independent checks, one command, no flags:"
NEW_DOC = OLD_DOC.replace("Two independent", "Three independent")
expected, after_manifest_if = [], False
for l in base_lines:
    if after_manifest_if:
        expected.append(l); expected.append(""); expected.extend(block_wiring)
        after_manifest_if = False
        continue
    if l == "def main():":
        expected.extend(func_lines); expected.append(""); expected.append(""); expected.append(l)
        continue
    if l == OLD_DOC:
        expected.append(NEW_DOC); continue
    expected.append(l)
    if l.strip() == "canonicalization, except where an exception declares otherwise.":
        expected.append(""); expected.extend(block_checkc)
    elif l == 'MARKETPLACE = ".claude-plugin/marketplace.json"':
        expected.append(""); expected.extend(const_lines)
    elif l.strip() == 'if not report("manifest descriptions", summary, problems):':
        after_manifest_if = True

problems = reconstructed(TARGET, expected, base_bytes)
for p in problems:
    print(p)
print("check-sync reconstruction:", "OK" if not problems else "FAIL")
sys.exit(1 if problems else 0)
PY
echo "exit=$?"
```

Expected: `check-sync reconstruction: OK` and `exit=0`. Run before Step 1's write, `reconstructed` reports the working tree's first differing line and exits 1 — the red form.

- [ ] **Step 3: Green check — `check-sync.py` runs, now with the author line**

```bash
python3 scripts/check-sync.py
echo "exit=$?"
```

Expected (the new `author attribution` line sits between the manifest line and the mirror-pair lines; all else unchanged):

```text
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: author attribution ... OK (8 author-less plugins)
check-sync: mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)
check-sync: mirror pair "adversarial-review-seed agent" ... OK (19 lines, 0 declared exceptions)
check-sync: mirror pair "adversarial-review-resolver agent" ... OK (25 lines, 0 declared exceptions)
check-sync: all checks passed
exit=0
```

- [ ] **Step 4: Green check — the `author_problems` criterion can fail (design step 6)**

Drives the pure decision with synthetic counts, so no tree mutation is needed to prove it fails on a wrong count and passes at the true one. `check-sync.py`'s hyphenated name is loaded via `importlib`. Run from the repo root:

```bash
python3 - <<'PY'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("check_sync", "scripts/check-sync.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
if mod.EXPECTED_AUTHORLESS_PLUGINS != 8:
    raise SystemExit("EXPECTED_AUTHORLESS_PLUGINS is %r, want 8" % mod.EXPECTED_AUTHORLESS_PLUGINS)
cases = [(8, 8, 0), (7, 8, 1), (9, 8, 1)]
notes = {8: "true state", 7: "author key set", 9: "new plugin"}
bad = []
for count, expected, want in cases:
    got = len(mod.author_problems(count, expected))
    print("%d author-less, expect %d (%s) -> %s (%d problem%s)"
          % (count, expected, notes[count], "OK" if got == 0 else "FAIL", got, "" if got == 1 else "s"))
    if got != want:
        bad.append("author_problems(%d, %d) returned %d problems, want %d" % (count, expected, got, want))
print()
print("author_problems self-test:", "all cases as expected" if not bad else "FAIL")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected:

```text
8 author-less, expect 8 (true state) -> OK (0 problems)
7 author-less, expect 8 (author key set) -> FAIL (1 problem)
9 author-less, expect 8 (new plugin) -> FAIL (1 problem)

author_problems self-test: all cases as expected
exit=0
```

- [ ] **Step 5: Presence check — the docstring enumeration and the check's key lines landed**

An independent confirmation (outside the reconstruction) that the design's exact lines are present — one match each. Run from the repo root:

```bash
git grep -c -F -e 'Three independent checks, one command, no flags:' \
             -e 'EXPECTED_AUTHORLESS_PLUGINS = 8' \
             -e 'def author_problems(count, expected):' \
             -e 'def check_authors():' \
             -e 'report("author attribution"' \
             -e '  Check C  the number of plugins/<dir>/.claude-plugin/plugin.json files with no' \
             -- scripts/check-sync.py
echo "exit=$?"
```

Expected: `scripts/check-sync.py:6` (six of the searched lines present) and `exit=0`. Also confirm the old enumeration is gone:

```bash
git grep -n -F 'Two independent checks' -- scripts/check-sync.py
echo "exit=$?"
```

Expected: no output and a non-zero exit (the `Two…` line was replaced by `Three…`).

- [ ] **Step 6: Commit**

```bash
git add scripts/check-sync.py
git commit -m "$(cat <<'EOF'
gh-51: add a CI-enforced author-attribution tripwire to check-sync.py

claude plugin validate . exits 0 whether or not it warns, so the "8 missing-
author warnings are expected" fact is enforced by no exit code and every change
re-types a six-line wrapper with the count hand-typed. The count is a filesystem
fact -- how many plugin.json files lack an author key -- so a third check_authors
counts author-less manifests and tripwires the count against a named
EXPECTED_AUTHORLESS_PLUGINS constant. Because CI already runs check-sync.py on
every PR, a new author-less plugin (or a removed author key) turns CI red on the
introducing PR. Check A's marketplace<->dir bijection makes the manifest count
equal the validator's warning count. Check A, Check B, and MIRROR_PAIRS are
untouched.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

Expected: one commit containing exactly `scripts/check-sync.py`. Confirm with `git show --stat HEAD`.

---

## Task 3: Point `CLAUDE.md` at both seams (block 0 appends to line 16, block 1 replaces line 11)

**Files:**
- Modify: `CLAUDE.md` — line 16 (the "Always" bullet under `## Verifying a change`) gains block 0; line 11 (the validate bullet) is replaced by block 1. Nothing else changes; the file stays 35 lines.

**Interfaces:**
- Consumes (from Task 1): `sys.path.insert(0, "scripts"); from verify_blob import blob, to_lines, reconstructed` — for this task's byte-for-byte check.
- Produces: nothing for a later task; Task 4 re-verifies the whole change.

**Repo root & branch (restated — task-brief strips the preamble):** run every command from `/Users/taylor/dev/claude-plugins`; you are on `tayl0r/gh-51-55-verification-helpers`.

**Command discipline (restated):** the merge base is computed inside `python3` and passed to `git` as an `argv` element, validated non-empty — never an inline `$(git …)`.

**Design doc (authoritative source of both replacement lines):** `/Users/taylor/dev/claude-plugins/docs/superpowers/specs/2026-08-04-gh-51-55-verification-helpers-design.md`. Its two **plain (untagged)** fenced blocks are shape `[1, 1]`: **block 0** (index 0, the "Always" append) and **block 1** (index 1, the validate replacement). **Read both blocks verbatim from the design via `read_blocks`; never retype either; if you cannot read the design file, stop and report.** The scripts below obtain them only through `read_blocks(DESIGN, [1, 1])[k][0]`.

**What the edit is.** Block 0 is a **pure append** to line 16: it starts with the entire existing "Always" bullet and adds one sentence pointing at `verify_blob` (the check below asserts the strict-prefix relation — nothing removed). Block 1 **fully replaces** line 11: it drops the bare number and the phrase `The 8 missing-author warnings are expected`, pointing instead at the CI-enforced author check. Both anchors are located by content, not line number.

- [ ] **Step 1: Confirm the design's block shape (design Verification step 0)**

Calls the `read_blocks` guard: if the design's plain-block shape is not `[1, 1]`, it exits non-zero rather than misrouting an edit. Run from the repo root:

```bash
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

Expected: block `[0]` previewing the "Always" bullet, block `[1]` previewing the validate bullet, then `shape guard: OK` and `exit=0`. A `design code-block shape is …` error means the design moved after this plan captured its shape — **stop and report**.

- [ ] **Step 2: Apply both edits — build the target from the base blob + blocks 0/1, and write it**

Reads the base blob and both design blocks, replaces the two anchor lines (each asserted unique), verifies block 0 strictly extends the base "Always" line and block 1 drops the removed phrase, and writes `CLAUDE.md`. Run from the repo root:

```bash
python3 - <<'PY'
import subprocess, sys
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-04-gh-51-55-verification-helpers-design.md"
TARGET = "CLAUDE.md"

def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout

base = git("merge-base", "origin/main", "HEAD").strip()
if not base:
    raise SystemExit("empty merge-base -- refusing to build against an unresolved ref")
base_lines = git("show", "%s:%s" % (base, TARGET)).split("\n")
if base_lines and base_lines[-1] == "":
    base_lines.pop()

b0, b1 = (b[0] for b in read_blocks(DESIGN, [1, 1]))   # block 0 -> line 16, block 1 -> line 11
ALWAYS = "- **Always:** grep for the exact phrases"     # line 16 prefix
VALIDATE = "- Validate before committing:"              # line 11 prefix
REMOVED = "The 8 missing-author warnings are expected"

always = [l for l in base_lines if l.startswith(ALWAYS)]
validate = [l for l in base_lines if l.startswith(VALIDATE)]
if len(always) != 1 or len(validate) != 1:
    raise SystemExit("anchors not unique: Always=%d, Validate=%d -- stop and report"
                     % (len(always), len(validate)))
if not (b0.startswith(always[0]) and len(b0) > len(always[0])):
    raise SystemExit("block 0 is not a strict append to the base Always line -- stop and report")
if b1 == validate[0] or REMOVED in b1:
    raise SystemExit("block 1 does not replace/drop the removed phrase -- stop and report")

out = []
for l in base_lines:
    if l.startswith(ALWAYS):
        out.append(b0)
    elif l.startswith(VALIDATE):
        out.append(b1)
    else:
        out.append(l)
import pathlib
pathlib.Path(TARGET).write_text("\n".join(out) + "\n", encoding="utf-8")
print("wrote %s: %d lines (block 0 -> Always, block 1 -> Validate)" % (TARGET, len(out)))
PY
echo "exit=$?"
```

Expected: `wrote CLAUDE.md: 35 lines (block 0 -> Always, block 1 -> Validate)` and `exit=0`. Any `anchors not unique` / `strict append` / `removed phrase` message means the base or a design block moved — **stop and report**.

- [ ] **Step 3: Green check — byte-for-byte reconstruction against the base blob (uses `verify_blob`)**

Independently re-derives `CLAUDE.md` from the base blob + blocks 0/1 and asserts the on-disk file equals it byte-for-byte via `verify_blob.reconstructed` — proving no other line moved. Run from the repo root:

```bash
python3 - <<'PY'
import subprocess, sys
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
from verify_blob import blob, to_lines, reconstructed

DESIGN = "docs/superpowers/specs/2026-08-04-gh-51-55-verification-helpers-design.md"
TARGET = "CLAUDE.md"

def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout

base = git("merge-base", "origin/main", "HEAD").strip()
if not base:
    raise SystemExit("empty merge-base -- refusing to reconstruct against an unresolved ref")
base_bytes = blob(base, TARGET)
base_lines = to_lines(base_bytes)
b0, b1 = (b[0] for b in read_blocks(DESIGN, [1, 1]))
ALWAYS = "- **Always:** grep for the exact phrases"
VALIDATE = "- Validate before committing:"
expected = [b0 if l.startswith(ALWAYS) else b1 if l.startswith(VALIDATE) else l
            for l in base_lines]
problems = reconstructed(TARGET, expected, base_bytes)
for p in problems:
    print(p)
print("CLAUDE.md reconstruction:", "OK" if not problems else "FAIL")
sys.exit(1 if problems else 0)
PY
echo "exit=$?"
```

Expected: `CLAUDE.md reconstruction: OK` and `exit=0`. Run before Step 2's write, `reconstructed` reports the first differing line (the working tree still carries the old line 11/16) and exits 1 — the red form.

- [ ] **Step 4: Residue check — the removed phrase is gone from shipped text (design step 3)**

#55 removes nothing (Step 3's strict-append assertion is its counterpart); #51's replacement drops the phrase. The `docs/superpowers/` pathspec is required — one prior plan there legitimately contains it. Run from the repo root:

```bash
git grep -n -F 'The 8 missing-author warnings are expected' -- . ':!docs/superpowers/'
echo "exit=$?"
```

Expected: **no output** and a **non-zero** exit (the phrase survives only in the excluded `docs/superpowers/`). If it prints `CLAUDE.md:11:…`, the replacement did not land — re-run Step 2.

- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md
git commit -m "$(cat <<'EOF'
gh-51-55: point CLAUDE.md at verify_blob and the author check

Line 16's "Always" bullet gains one sentence: read both sides as raw bytes and
use scripts/verify_blob for the read-and-compare, which does not differ per
change. Line 11's validate bullet drops the bare "8 missing-author warnings are
expected" for a pointer at check-sync.py's CI-enforced author check. Two
same-file, disjoint-line edits; the file stays 35 lines.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

Expected: one commit containing exactly `CLAUDE.md`. Confirm with `git show --stat HEAD`.

---

## Task 4: Whole-change acceptance sweep (design Verification steps 0–7)

**Files:** none modified — this task only verifies. It runs after Tasks 1–3 have committed, so every committed-HEAD read (step 7) is post-commit.

**Interfaces:**
- Consumes: the three commits from Tasks 1–3 and `verify_blob` on disk.
- Produces: the green acceptance gate for the whole change. Any red step sends work back to the task that owns it (verify_blob → Task 1, check-sync → Task 2, CLAUDE.md → Task 3).

**Repo root & branch (restated — task-brief strips the preamble):** run every command from `/Users/taylor/dev/claude-plugins`; you are on `tayl0r/gh-51-55-verification-helpers`. Run this task **only after Tasks 1, 2 and 3 are committed** — steps 1, 2 and 7 assert the whole three-file change at once.

**Command discipline (restated):** every computed base is passed to `git` as an `argv` element, validated non-empty — never `$(git …)`. **Verification ordering:** step 7 reads committed HEAD via `check-version-bump.py`, so it runs here, after all commits.

**Design doc (authoritative source of the blocks re-read below):** `/Users/taylor/dev/claude-plugins/docs/superpowers/specs/2026-08-04-gh-51-55-verification-helpers-design.md`. Step 2 re-reads the two plain blocks (`read_blocks(DESIGN, [1, 1])`) and the four tagged blocks (via the inlined `fenced_block`). **Read every block verbatim from the design; never retype; if you cannot read the design, stop and report.**

- [ ] **Step 0: Block shape guard**

```bash
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

Expected: two block previews, `shape guard: OK`, `exit=0`.

- [ ] **Step 1: File scope — exactly the three files, and no fourth (design step 1)**

```bash
python3 - <<'PY'
import subprocess, sys
SCOPE = ["--", ".", ":!docs/superpowers/"]
WANT = sorted(["CLAUDE.md", "scripts/check-sync.py", "scripts/verify_blob.py"])
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
changed = sorted(p for p in git("diff", "--name-only", base, *SCOPE).split("\n") if p)
if changed != WANT:
    print("file scope: FAIL -- changed %s, want %s" % (changed, WANT))
    sys.exit(1)
print("file scope: OK")
PY
echo "exit=$?"
```

Expected: a `base:` line with a 40-char SHA (`7f78af0…` today), then `file scope: OK` and `exit=0`. A stray path (any `plugins/` file, a `plugin.json`, `design_blocks.py`, `CONTEXT.md`, `docs/adr/`, `.github/`, `marketplace.json`) fails the step and is named.

- [ ] **Step 2: Reconstruction + design conformance + `verify_blob.py` is new (design step 2)**

Three sub-checks in sequence; each must print `OK` and `exit=0`.

**2a — `CLAUDE.md` is byte-for-byte its base blob with block 0 on line 16 and block 1 on line 11:**

```bash
python3 - <<'PY'
import subprocess, sys
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
from verify_blob import blob, to_lines, reconstructed
DESIGN = "docs/superpowers/specs/2026-08-04-gh-51-55-verification-helpers-design.md"
def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout
base = git("merge-base", "origin/main", "HEAD").strip()
if not base:
    raise SystemExit("empty merge-base")
base_bytes = blob(base, "CLAUDE.md")
base_lines = to_lines(base_bytes)
b0, b1 = (b[0] for b in read_blocks(DESIGN, [1, 1]))
A, V = "- **Always:** grep for the exact phrases", "- Validate before committing:"
if not (b0.startswith(next(l for l in base_lines if l.startswith(A))) and len(b0) > len(next(l for l in base_lines if l.startswith(A)))):
    raise SystemExit("block 0 is not a strict append to base line 16")
expected = [b0 if l.startswith(A) else b1 if l.startswith(V) else l for l in base_lines]
problems = reconstructed("CLAUDE.md", expected, base_bytes)
for p in problems: print(p)
print("CLAUDE.md reconstruction:", "OK" if not problems else "FAIL")
sys.exit(1 if problems else 0)
PY
echo "exit=$?"
```

Expected: `CLAUDE.md reconstruction: OK`, `exit=0`.

**2b — `scripts/check-sync.py` is byte-for-byte its base blob with exactly the documented additions:**

```bash
python3 - <<'PY'
import subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from verify_blob import blob, to_lines, reconstructed
DESIGN = "docs/superpowers/specs/2026-08-04-gh-51-55-verification-helpers-design.md"
TARGET = "scripts/check-sync.py"
def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout
def fenced_block(design_path, first_prefix):
    """Lines of the unique ```-fenced block (tagged or plain) whose first content
    line startswith first_prefix. Mirrors scripts/design_blocks._blocks: refuses a
    4+-backtick fence and an unclosed fence rather than mis-parsing silently. Exits
    non-zero on 0 or >1 matches."""
    fence = chr(96) * 3
    try:
        text = Path(design_path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise SystemExit("cannot read design %s: %s" % (design_path, e))
    blocks, cur, opened = [], None, 0
    for n, line in enumerate(text.split("\n"), 1):
        s = line.strip()
        if s.startswith(fence + fence[0]):
            raise SystemExit("%s line %d: this reader parses three-backtick fences "
                             "only; a longer one mis-indexes every block after it"
                             % (design_path, n))
        if cur is None:
            if s.startswith(fence):
                cur, opened = [], n
        elif s == fence:
            blocks.append(cur); cur = None
        else:
            cur.append(line)
    if cur is not None:
        raise SystemExit("design %s: the fence opened at line %d is never closed"
                         % (design_path, opened))
    hits = [b for b in blocks if b and b[0].startswith(first_prefix)]
    if len(hits) != 1:
        raise SystemExit("design: %d fenced blocks start with %r, want exactly 1"
                         % (len(hits), first_prefix))
    return hits[0]
base = git("merge-base", "origin/main", "HEAD").strip()
if not base:
    raise SystemExit("empty merge-base")
base_bytes = blob(base, TARGET)
base_lines = to_lines(base_bytes)
const_lines = fenced_block(DESIGN, "# Number of plugins whose plugin.json carries no")
func_lines = fenced_block(DESIGN, "def author_problems(count, expected):")
block_wiring = fenced_block(DESIGN, "    summary, problems = check_authors()")
block_checkc = fenced_block(DESIGN, "  Check C  the number of plugins/<dir>/.claude-plugin/plugin")
OLD_DOC = "Two independent checks, one command, no flags:"
NEW_DOC = OLD_DOC.replace("Two independent", "Three independent")
expected, after = [], False
for l in base_lines:
    if after:
        expected.append(l); expected.append(""); expected.extend(block_wiring); after = False; continue
    if l == "def main():":
        expected.extend(func_lines); expected.append(""); expected.append(""); expected.append(l); continue
    if l == OLD_DOC:
        expected.append(NEW_DOC); continue
    expected.append(l)
    if l.strip() == "canonicalization, except where an exception declares otherwise.":
        expected.append(""); expected.extend(block_checkc)
    elif l == 'MARKETPLACE = ".claude-plugin/marketplace.json"':
        expected.append(""); expected.extend(const_lines)
    elif l.strip() == 'if not report("manifest descriptions", summary, problems):':
        after = True
problems = reconstructed(TARGET, expected, base_bytes)
for p in problems: print(p)
print("check-sync reconstruction:", "OK" if not problems else "FAIL")
sys.exit(1 if problems else 0)
PY
echo "exit=$?"
```

Expected: `check-sync reconstruction: OK`, `exit=0`.

**2c — `scripts/verify_blob.py` is new (absent at the base), `scripts/check-sync.py` is present at the base:**

```bash
python3 - <<'PY'
import subprocess, sys
def git_rc(*args):
    return subprocess.run(("git",) + args, capture_output=True, text=True, encoding="utf-8").returncode
def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- %s" % (" ".join(args), r.stderr.strip() or "(no message)"))
    return r.stdout
base = git("merge-base", "origin/main", "HEAD").strip()
if not base:
    raise SystemExit("empty merge-base")
new_absent = git_rc("cat-file", "-e", "%s:scripts/verify_blob.py" % base) != 0
sync_present = git_rc("cat-file", "-e", "%s:scripts/check-sync.py" % base) == 0
print("verify_blob.py new at base:", new_absent)
print("check-sync.py present at base:", sync_present)
print("new-file check:", "OK" if (new_absent and sync_present) else "FAIL")
sys.exit(0 if (new_absent and sync_present) else 1)
PY
echo "exit=$?"
```

Expected: `verify_blob.py new at base: True`, `check-sync.py present at base: True`, `new-file check: OK`, `exit=0`.

- [ ] **Step 3: Residue — #51's removed phrase is gone from shipped text (design step 3)**

```bash
git grep -n -F 'The 8 missing-author warnings are expected' -- . ':!docs/superpowers/'
echo "exit=$?"
```

Expected: no output and a non-zero exit.

- [ ] **Step 4: `check-sync.py` green, including the author check (design step 4)**

```bash
python3 scripts/check-sync.py
echo "exit=$?"
```

Expected:

```text
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: author attribution ... OK (8 author-less plugins)
check-sync: mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)
check-sync: mirror pair "adversarial-review-seed agent" ... OK (19 lines, 0 declared exceptions)
check-sync: mirror pair "adversarial-review-resolver agent" ... OK (25 lines, 0 declared exceptions)
check-sync: all checks passed
exit=0
```

- [ ] **Step 5: `verify_blob --selftest` — the byte check flags what the line check passed (design step 5)**

```bash
python3 scripts/verify_blob.py --selftest
echo "exit=$?"
```

Expected: the three-row table (OLD `pass` everywhere; NEW `OK`, `FAIL` + `lines match but bytes differ`, `FAIL` + visible `\r`), then `verify_blob self-test: all cases as expected` and `exit=0`.

- [ ] **Step 6: `author_problems` — the #51 criterion can fail (design step 6)**

```bash
python3 - <<'PY'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("check_sync", "scripts/check-sync.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
bad = []
for count, expected, want in [(8, 8, 0), (7, 8, 1), (9, 8, 1)]:
    got = len(mod.author_problems(count, expected))
    print("%d author-less, expect %d -> %s (%d)" % (count, expected, "OK" if got == 0 else "FAIL", got))
    if got != want:
        bad.append((count, expected, got, want))
print("author_problems self-test:", "all cases as expected" if not bad else "FAIL")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expected: `8 … -> OK (0)`, `7 … -> FAIL (1)`, `9 … -> FAIL (1)`, `author_problems self-test: all cases as expected`, `exit=0`.

- [ ] **Step 7: `check-version-bump.py` — no plugin touched, so no bump (design step 7; runs after all commits)**

Reads committed HEAD (`git diff merge-base..HEAD`), so per the verification-ordering rule it runs here, after Tasks 1–3 have committed. All three touched files sit outside `plugins/`, so `touched()` finds no plugin directory and the check passes without asking for a bump. Pass `origin/main` as the symbolic ref shown — never a captured `$(…)`.

```bash
python3 scripts/check-version-bump.py origin/main
echo "exit=$?"
```

Expected (the first line's three SHAs are 9-char abbreviations that vary per commit — `check-version-bump.py` always prints this header before the result line):

```text
check-version-bump: base <sha>, head <sha>, merge-base <sha>
check-version-bump: no plugin directory touched ... OK
exit=0
```

**Acceptance gate (all must hold):** step 0 (shape `[1, 1]`), step 1 (exactly the three files), step 2a/2b/2c (both prose files byte-for-byte their base blob with exactly the intended edits; `verify_blob.py` new), step 3 (removed phrase gone from shipped text), step 4 (`check-sync.py` green with the author line), step 5 (`--selftest` flags both deviations), step 6 (`author_problems` fails on 7/9, passes on 8), step 7 (no plugin touched → no bump). The design and this plan under `docs/superpowers/` are committed separately by the dev-flow pipeline (`docs: commit`).

---

## Self-Review

**1. Spec coverage.** Every decision in the design maps to a task. #55's `scripts/verify_blob.py` (library body verbatim + authored `--selftest`) → Task 1. #51's `check-sync.py` additions (constant, `author_problems`, `check_authors`, `main` wiring, docstring two→three) → Task 2, with Check A/Check B/`MIRROR_PAIRS` explicitly untouched. `CLAUDE.md` block 0 (line 16 append) and block 1 (line 11 replace) → Task 3. The design's Verification steps 0–7 all appear: step 0 → Tasks 3/4; step 1 → Task 4; step 2 (CLAUDE.md + check-sync reconstruction + verify_blob-is-new) → Tasks 2/3 (per file) and Task 4 (combined); step 3 → Tasks 3/4; step 4 → Tasks 2/4; step 5 → Tasks 1/4; step 6 → Tasks 2/4; step 7 → Task 4 (post-commit). The no-version-bump conclusion (A4) is asserted by step 7. Out-of-scope items (`plugins/`, existing checks, `design_blocks.py`, `CONTEXT.md`, `docs/adr/`, `.github/`, `marketplace.json`) are guarded by step 1's scope-equality. No gaps.

**2. Placeholder scan.** No TBD/TODO/"handle edge cases"/"similar to Task N". The library body and the check-sync additions are read verbatim from the design on disk (never pasted-and-trusted from this plan); block 0/1 come from `read_blocks`. The one authored artifact — `verify_blob`'s `--selftest` — is given as complete, runnable reference code plus the exact step-5 contract it must reproduce, and Task 1 Step 3 verifies it. Every code step carries its command and expected output, red form noted where meaningful.

**3. Type/name consistency.** `blob`, `to_lines`, `reconstructed`, `compare` (public) and `_worktree`, `_to_bytes` (private) match the design and are used consistently in Tasks 2–4. `EXPECTED_AUTHORLESS_PLUGINS`, `author_problems`, `check_authors`, the report label `"author attribution"`, the docstring `Three independent checks`, and the anchors (`MARKETPLACE = ".claude-plugin/marketplace.json"`, the manifest-report `if not report("manifest descriptions", …)` line, `def main():`, the Check B `canonicalization, except …` line, `Two independent checks…`) match `scripts/check-sync.py` exactly. The `CLAUDE.md` anchors (`- **Always:** grep for the exact phrases`, `- Validate before committing:`) and the removed phrase match the file. The design path and the block-shape `[1, 1]` are identical everywhere.

**4. Self-sufficiency (dev-flow Stage 2 rule).** Each `## Task N` section re-inlines its repo-root/branch statement, command-discipline and verbatim-read clauses, the design's absolute path, and every verification command — no task leans on the stripped Global Constraints or on another task's text. Cross-task dependencies are satisfied by order: Task 1 puts `verify_blob` on disk before Tasks 2–4 import it; Tasks 2 and 3 verify against the merge-base blob (reading the working tree, so pre-commit-safe); Task 4 runs the whole sweep after all three commits, so its only committed-HEAD read (step 7) is post-commit. Every design block a task needs is read from the design on disk (the `python`/`text` additions via the inlined `fenced_block`, the two plain blocks via `read_blocks`), never reconstructed from this plan.
