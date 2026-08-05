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
