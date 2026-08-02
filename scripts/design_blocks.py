#!/usr/bin/env python3
"""Read a design doc's plain fenced blocks, for design-conformance checks.

CLAUDE.md requires every change carrying a design doc to add a python3 check
that re-reads the design's replacement text from disk rather than retyping it.
The block-to-file mapping and the assertions each target must satisfy differ
per change and stay in that check; only the reader is shared.

    import sys
    from pathlib import Path
    sys.path.insert(0, "scripts")
    from design_blocks import read_blocks
    DESIGN = "docs/superpowers/specs/<design>.md"
    blocks = read_blocks(DESIGN, [1, 1, 2])

read_blocks returns the plain (untagged) fenced blocks in document order, as
lists of lines, having first checked they have the shape the caller indexed
its edits against. A mismatch exits non-zero rather than returning: a design
whose blocks moved silently misroutes every edit indexed off them. The shape
is a required argument, not an option to remember.

Run this file as a script to obtain that shape and the block indices:

    python3 scripts/design_blocks.py <design-path>

Paths are taken as given, so a relative one resolves against the current
directory -- like the inline reader this replaces, and like every target path
in the same check. Every failure detected here -- a design that cannot be
read, a fence that cannot be parsed, a shape that moved -- exits non-zero with
one line on stderr rather than a traceback.

Fence detection matches the inline reader exactly on well-formed input: a line
whose stripped form opens with three backticks, an empty info string for a
plain block. Three-backtick fences are the only ones parsed, so the two inputs
that would otherwise shift every block index unnoticed are refused rather than
guessed at: a longer fence, and a fence that is never closed. It follows that
no block of either kind can hold a line that is exactly three backticks: that
line closes it, tagged or not, and the resulting mis-pairing can be silent. A
design must build any fence it quotes in code, the way this file does.

Design: docs/superpowers/specs/2026-08-02-gh-24-design-block-reader-design.md
"""

import sys
from pathlib import Path

FENCE = chr(96) * 3


def _blocks(design_path):
    """Every plain (untagged) fenced block, in document order, as lists of lines."""
    try:
        text = Path(design_path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise SystemExit("cannot read design %s: %s" % (design_path, e))
    blocks, cur, mode, opened = [], None, None, 0
    for n, line in enumerate(text.split("\n"), 1):
        s = line.strip()
        if s.startswith(FENCE + FENCE[0]):
            raise SystemExit("%s line %d: this reader parses three-backtick"
                             " fences only; a longer one mis-indexes every"
                             " block after it" % (design_path, n))
        if mode is None:
            if s.startswith(FENCE):
                mode, cur, opened = s[3:], [], n
        elif s == FENCE:
            if mode == "":
                blocks.append(cur)
            mode, cur = None, None
        else:
            cur.append(line)
    if mode is not None:
        raise SystemExit("%s: the fence opened at line %d is never closed; a plain"
                         " block cannot contain a three-backtick line"
                         % (design_path, opened))
    return blocks


def read_blocks(design_path, shape):
    """_blocks, guarded by the shape the caller indexed its edits against."""
    blocks = _blocks(design_path)
    actual = [len(b) for b in blocks]
    if actual != list(shape):
        raise SystemExit(
            "design code-block shape is %s, want %r; stop and re-read the design"
            % (actual, shape))
    return blocks


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 scripts/design_blocks.py <design-path>")
    blocks = _blocks(sys.argv[1])
    print("shape: %s" % [len(b) for b in blocks])
    for i, b in enumerate(blocks):
        print("  [%d] len=%d: %s" % (i, len(b), b[0][:70] if b else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
