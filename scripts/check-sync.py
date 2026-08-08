#!/usr/bin/env python3
"""Mechanical drift check for the facts this repo duplicates by hand.

Three independent checks, one command, no flags:

  Check A  every plugins/<dir>/.claude-plugin/plugin.json agrees with its
           .claude-plugin/marketplace.json entry (name, source, description),
           and every marketplace entry has a plugin directory.

  Check B  each pair declared in MIRROR_PAIRS is line-for-line identical after
           canonicalization, except where an exception declares otherwise.

  Check C  the number of plugins/<dir>/.claude-plugin/plugin.json files with no
           `author` key equals the EXPECTED_AUTHORLESS_PLUGINS tripwire -- the
           `No author information provided` count `claude plugin validate .`
           warns on but exits 0 for, so nothing else enforces it.

All three checks run every time, so one run reports every problem in the tree.
Exit 0 iff every check passed, 1 otherwise. Python 3 stdlib only, no flags.

Design: docs/superpowers/specs/2026-07-26-gh-8-drift-check-design.md
"""

import json
import sys
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE = ".claude-plugin/marketplace.json"

# Number of plugins whose plugin.json carries no `author` key. A hand-set
# tripwire, not a value derived from the tree: a change that adds an author-less
# plugin or drops an author key must bump this deliberately, which is the signal
# #51 exists to preserve. It equals the `No author information provided` count
# `claude plugin validate .` warns on -- Check A's marketplace<->dir bijection
# makes the two counts identical -- but needs no validator to measure.
EXPECTED_AUTHORLESS_PLUGINS = 8

# Pairs of files that must stay line-for-line parallel. Enrollment requires
# line-for-line parallelism: this schema can only declare same-index,
# one-line-for-one-line divergences. See the design doc, Decision 6.
MIRROR_PAIRS = [
    {
        "name": "adversarial-review",
        "a": "plugins/dev-flow/skills/adversarial-review/SKILL.md",
        "b": "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md",
        # applied to both sides; the script substitutes longest token first
        "canonicalize": [("dev-flow-worktree", "dev-flow")],
        "exceptions": [
            {
                "why": "The two pipelines pass working-dir differently: dev-flow omits "
                       "it and the review defaults to the invoking checkout; "
                       "dev-flow-worktree passes the worktree path explicitly.",
                "a": "- When called by dev-flow, the review runs in-context on the "
                     "feature branch checked out in the invoking checkout, so "
                     "`working-dir` is omitted — it defaults to that checkout (see "
                     "dev-flow's branch-entry rule). dev-flow uses no worktree.",
                "b": "- When called by dev-flow-worktree, `working-dir` is the pipeline "
                     "worktree's absolute path — the orchestrator passes it explicitly "
                     "and invokes the review in-context (see dev-flow-worktree's "
                     "worktree-entry rule).",
            },
        ],
    },
    {
        "name": "adversarial-review-seed agent",
        "a": "plugins/dev-flow/agents/adversarial-review-seed.md",
        "b": "plugins/dev-flow-worktree/agents/adversarial-review-seed.md",
        # Same canonicalization as the SKILL.md pair: each variant's agent body
        # may name its own plugin, and both register under their own qualified
        # name, so "dev-flow-worktree" there is correct rather than drift.
        "canonicalize": [("dev-flow-worktree", "dev-flow")],
        "exceptions": [],
    },
    {
        "name": "adversarial-review-resolver agent",
        "a": "plugins/dev-flow/agents/adversarial-review-resolver.md",
        "b": "plugins/dev-flow-worktree/agents/adversarial-review-resolver.md",
        # Same canonicalization as the SKILL.md pair: each variant's agent body
        # may name its own plugin, and both register under their own qualified
        # name, so "dev-flow-worktree" there is correct rather than drift.
        "canonicalize": [("dev-flow-worktree", "dev-flow")],
        "exceptions": [],
    },
    {
        "name": "produce-subagent agent",
        "a": "plugins/dev-flow/agents/produce-subagent.md",
        "b": "plugins/dev-flow-worktree/agents/produce-subagent.md",
        # Same canonicalization as the SKILL.md pair: each variant's agent
        # description and body may name its own plugin, and both register
        # under their own qualified name, so "dev-flow-worktree" there is
        # correct rather than drift.
        "canonicalize": [("dev-flow-worktree", "dev-flow")],
        "exceptions": [],
    },
    {
        "name": "task-reviewer agent",
        "a": "plugins/dev-flow/agents/task-reviewer.md",
        "b": "plugins/dev-flow-worktree/agents/task-reviewer.md",
        "canonicalize": [("dev-flow-worktree", "dev-flow")],
        "exceptions": [],
    },
]


def plural(count, word):
    return f"{count} {word}" if count == 1 else f"{count} {word}s"


# Everything read_text can raise: a missing/unreadable path, or a file whose
# bytes are not valid UTF-8. Catch these wherever a read is reported as a
# check failure — never let them escape as a traceback.
READ_ERRORS = (OSError, UnicodeDecodeError)


def read_text(relpath):
    """Read a repo-relative file as UTF-8. Never the locale default: these files
    contain em dashes and a C/POSIX-locale run would otherwise traceback."""
    return (REPO_ROOT / relpath).read_text(encoding="utf-8")


def report(label, summary, problems):
    """Print one unit's progress line plus any problem blocks. Returns True if OK."""
    if not problems:
        print(f"check-sync: {label} ... OK ({summary})")
        return True
    print(f"check-sync: {label} ... FAIL")
    for block in problems:
        print()
        print(textwrap.indent(block, "  "))
    print()
    return False


# --------------------------------------------------------------------------
# Check A: manifest description sync
# --------------------------------------------------------------------------

def check_manifests():
    """Returns (summary, problems). summary is the OK suffix for the progress line."""
    try:
        market = json.loads(read_text(MARKETPLACE))
    except READ_ERRORS as exc:
        return "", [f"cannot read {MARKETPLACE}: {exc}"]
    except json.JSONDecodeError as exc:
        return "", [f"cannot parse {MARKETPLACE}: {exc}"]

    entries = market.get("plugins") if isinstance(market, dict) else None
    if not isinstance(entries, list):
        return "", [f'{MARKETPLACE} has no "plugins" list.']

    problems = []
    by_name = {}
    for entry in entries:
        name = entry.get("name") if isinstance(entry, dict) else None
        if not isinstance(name, str):
            problems.append(
                f'{MARKETPLACE} has an entry with no "name" string: {entry!r}'
            )
            continue
        by_name.setdefault(name, []).append(entry)

    manifests = sorted((REPO_ROOT / "plugins").glob("*/.claude-plugin/plugin.json"))
    seen_dirs = set()
    for manifest in manifests:
        directory = manifest.parent.parent.name
        seen_dirs.add(directory)
        rel = f"plugins/{directory}/.claude-plugin/plugin.json"
        try:
            data = json.loads(read_text(rel))
        except READ_ERRORS as exc:
            problems.append(f"cannot read {rel}: {exc}")
            continue
        except json.JSONDecodeError as exc:
            problems.append(f"cannot parse {rel}: {exc}")
            continue

        name = data.get("name") if isinstance(data, dict) else None
        if not isinstance(name, str):
            problems.append(f'{directory}: {rel} has no "name" string.')
            continue
        if name != directory:
            problems.append(
                f'{directory}: plugin.json "name" is "{name}", but the directory is\n'
                f'"plugins/{directory}". They must match.\n\n'
                f"  {rel}"
            )
            continue

        description = data.get("description")
        if not isinstance(description, str):
            problems.append(f'{name}: {rel} has no "description" string.')
            continue

        found = by_name.get(name, [])
        if not found:
            problems.append(
                f"{name}: no entry in {MARKETPLACE}.\n"
                f"Every plugin directory must be registered. `claude plugin validate .`\n"
                f"does not catch this: it only iterates the marketplace's own entries.\n\n"
                f"  {rel}"
            )
            continue
        if len(found) > 1:
            problems.append(
                f"{name}: {MARKETPLACE} has {len(found)} entries with this name;\n"
                f"expected exactly 1."
            )
            continue

        entry = found[0]
        expected_source = f"./plugins/{name}"
        source = entry.get("source")
        if source != expected_source:
            problems.append(
                f"{name}: marketplace entry \"source\" is {json.dumps(source)}, "
                f"expected\n"
                f'"{expected_source}". CLAUDE.md requires the leading "./".\n\n'
                f"  {MARKETPLACE}"
            )

        entry_description = entry.get("description")
        if entry_description != description:
            # A non-string (or absent) value renders as JSON, like "source" above,
            # so a missing key prints null rather than Python's None.
            shown = (entry_description if isinstance(entry_description, str)
                     else json.dumps(entry_description))
            problems.append(
                f"{name}: description differs between the two manifests.\n"
                f"CLAUDE.md requires them to be identical.\n\n"
                f"  {rel}\n"
                f"    {description}\n"
                f"  {MARKETPLACE}\n"
                f"    {shown}"
            )

    for name in by_name:
        if name in seen_dirs:
            continue
        problems.append(
            f"{name}: {MARKETPLACE} registers this plugin, but there is no\n"
            f"plugins/{name}/ directory with a .claude-plugin/plugin.json."
        )

    return plural(len(manifests), "plugin"), problems


# --------------------------------------------------------------------------
# Check B: declared mirror pairs
# --------------------------------------------------------------------------

PAIR_HEADER = """\
These two files must stay line-for-line identical after canonicalizing
{subs}. Every cross-cutting edit lands in both.

  A: {a}
  B: {b}"""

DIVERGENCE_FIX = """\
Fix: mirror the edit into both files. If the divergence is genuinely variant-specific,
add it to MIRROR_PAIRS["{name}"]["exceptions"] in scripts/check-sync.py
with a one-line reason."""

LINE_COUNT_FIX = """\
A line-for-line pair cannot differ in length — one side gained or lost a line that was
not mirrored. Mirror it, then re-run.

If the extra line is an *intentional* one-sided divergence, note that Check B's
line-parallel schema cannot declare it — see the design doc (Decision 6) before
contorting the prose to fit. The schema, not your edit, is what needs extending."""


def canonicalize(text, substitutions):
    """Apply every substitution to the text, longest source token first, so a token
    containing another as a substring is always replaced first. Substitutions are
    applied sequentially: a destination that contains another entry's source would
    be replaced again by that entry — declare disjoint tokens."""
    for src, dst in sorted(substitutions, key=lambda pair: -len(pair[0])):
        text = text.replace(src, dst)
    return text


def split_lines(text):
    """Split on "\\n" only, dropping the final empty string a trailing newline
    produces, so the reported count agrees with `wc -l`. str.splitlines() would
    also break on form feed, NEL, and U+2028/9 — one invisible pasted control
    character and the reported counts contradict `wc -l`."""
    lines = text.split("\n")
    if lines[-1] == "":
        lines.pop()
    return lines


def format_why(why):
    return textwrap.fill(why, width=84, initial_indent="  why: ",
                         subsequent_indent="       ")


def exception_block(headline, exc, trailer=None):
    """The shared rendering for every problem block about one declared exception:
    headline, then the entry itself. Three of these would otherwise drift apart."""
    lines = [headline, format_why(exc["why"]),
             f"  A: {exc['a']}", f"  B: {exc['b']}"]
    if trailer is not None:
        lines.append(trailer)
    return "\n".join(lines)


def check_pair(pair):
    """Returns (summary, problems). summary is the OK suffix for the progress line.
    On failure, problems[0] is the pair's shared header block."""
    subs = pair.get("canonicalize", [])
    exceptions = pair.get("exceptions", [])
    header = PAIR_HEADER.format(
        subs=", ".join(f'"{src}" -> "{dst}"' for src, dst in subs) or "nothing",
        a=pair["a"],
        b=pair["b"],
    )

    texts = {}
    for side in ("a", "b"):
        try:
            texts[side] = read_text(pair[side])
        except READ_ERRORS as exc:
            return "", [header, f"cannot read {side.upper()}: {exc}"]

    canon = {side: canonicalize(texts[side], subs) for side in ("a", "b")}
    lines = {side: split_lines(canon[side]) for side in ("a", "b")}
    raw_lines = {side: split_lines(texts[side]) for side in ("a", "b")}

    items = []

    ends_nl = {side: canon[side].endswith("\n") for side in ("a", "b")}
    if ends_nl["a"] != ends_nl["b"]:
        with_nl, without_nl = ("A", "B") if ends_nl["a"] else ("B", "A")
        items.append(
            f"trailing newline differs: {with_nl} ends with a newline, "
            f"{without_nl} does not.\nMirror it, then re-run."
        )

    summary = f"{plural(len(lines['a']), 'line')}, " \
              f"{plural(len(exceptions), 'declared exception')}"

    # Step 3: fully identical after canonicalization -> skip the line comparison.
    identical = canon["a"] == canon["b"]

    # Step 6 (part 1): classify every declared exception before any matching, so
    # both the line-count scan and the positional comparison match against one
    # usable set. An entry is unusable three ways: it is missing a required key;
    # its two sides match after canonicalization, so it declares no divergence
    # and can never fire; or an earlier entry already declares the same
    # divergence, and one entry permits it everywhere it occurs.
    usable = []
    malformed = []
    invalid = []
    duplicates = []
    declared = set()
    for exc in exceptions:
        missing = [key for key in ("why", "a", "b") if key not in exc]
        if missing:
            invalid.append((missing, exc))
            continue
        canon_a = canonicalize(exc["a"], subs)
        canon_b = canonicalize(exc["b"], subs)
        if canon_a == canon_b:
            malformed.append(exc)
        elif (canon_a, canon_b) in declared:
            duplicates.append(exc)
        else:
            declared.add((canon_a, canon_b))
            usable.append((canon_a, canon_b, exc))

    def declared_at(index):
        """Position in `usable` of the exception matching the canonicalized lines
        at this index, or None. The single definition of 'declared divergence'."""
        return next(
            (
                position
                for position, (canon_a, canon_b, _) in enumerate(usable)
                if canon_a == lines["a"][index] and canon_b == lines["b"][index]
            ),
            None,
        )

    if not identical and len(lines["a"]) != len(lines["b"]):
        common = min(len(lines["a"]), len(lines["b"]))
        first = next(
            (
                i for i in range(common)
                if lines["a"][i] != lines["b"][i] and declared_at(i) is None
            ),
            None,
        )
        block = (
            f"line count differs: A has {len(lines['a'])}, "
            f"B has {len(lines['b'])}.\n"
        )
        if first is None:
            longer = "A" if len(lines["a"]) > len(lines["b"]) else "B"
            block += (
                f"the files match through the end of the shorter (modulo declared "
                f"exceptions);\nthe first unmatched line is line {common + 1} "
                f"of {longer}:\n"
                f"  {longer}: {raw_lines[longer.lower()][common]}"
            )
        else:
            block += (
                f"first undeclared divergence at line {first + 1}:\n"
                f"  A: {raw_lines['a'][first]}\n"
                f"  B: {raw_lines['b'][first]}"
            )
        items.append(block)
        items.append(LINE_COUNT_FIX)
        return summary, [header, *items]

    used = set()
    undeclared = False
    if not identical:
        # Step 5: positional comparison.
        for index in range(len(lines["a"])):
            if lines["a"][index] == lines["b"][index]:
                continue
            match = declared_at(index)
            if match is not None:
                used.add(match)
                continue
            undeclared = True
            items.append(
                f"line {index + 1}: undeclared divergence\n"
                f"  A: {raw_lines['a'][index]}\n"
                f"  B: {raw_lines['b'][index]}"
            )
        if undeclared:
            items.append(DIVERGENCE_FIX.format(name=pair["name"]))

    # An invalid entry cannot use exception_block: it is defined by not having
    # the keys that block renders.
    for missing, exc in invalid:
        names = ", ".join(f'"{key}"' for key in missing)
        items.append(
            f'invalid exception: missing {names} — every exception declares '
            f'"why", "a", and "b".\n'
            f'Complete the entry in scripts/check-sync.py:\n'
            f'  {exc!r}'
        )

    for exc in malformed:
        items.append(exception_block(
            "malformed exception: after canonicalization its two sides are identical,\n"
            "so it declares no divergence and can never match. The canonicalization\n"
            "already permits this difference; remove the entry from "
            "scripts/check-sync.py.",
            exc,
        ))

    for exc in duplicates:
        items.append(exception_block(
            "duplicate exception: it declares the same divergence as an earlier entry\n"
            "(identical after canonicalization). One entry permits a divergence "
            "everywhere\n"
            "it occurs; remove the duplicate from scripts/check-sync.py.",
            exc,
        ))

    for position, (_, _, exc) in enumerate(usable):
        if position in used:
            continue
        items.append(exception_block(
            "stale exception: the divergence it describes no longer appears in the "
            "files.",
            exc,
            "Remove the entry from scripts/check-sync.py, or restore the divergence "
            "it describes.",
        ))

    if not items:
        return summary, []
    return summary, [header, *items]


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


def main():
    failures = 0

    summary, problems = check_manifests()
    if not report("manifest descriptions", summary, problems):
        failures += 1

    summary, problems = check_authors()
    if not report("author attribution", summary, problems):
        failures += 1

    for pair in MIRROR_PAIRS:
        summary, problems = check_pair(pair)
        if not report(f'mirror pair "{pair["name"]}"', summary, problems):
            failures += 1

    if failures:
        print(f"check-sync: {plural(failures, 'check')} failed")
        return 1
    print("check-sync: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
