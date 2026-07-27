#!/usr/bin/env python3
"""Mechanical drift check for the facts this repo duplicates by hand.

Check A: every plugins/<dir>/.claude-plugin/plugin.json agrees with its
.claude-plugin/marketplace.json entry (name, source, description), and every
marketplace entry has a plugin directory.

Exit 0 iff every check passed, 1 otherwise. Python 3 stdlib only, no flags.

Design: docs/superpowers/specs/2026-07-26-gh-8-drift-check-design.md
"""

import json
import sys
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE = ".claude-plugin/marketplace.json"


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
            problems.append(
                f"{name}: description differs between the two manifests.\n"
                f"CLAUDE.md requires them to be identical.\n\n"
                f"  {rel}\n"
                f"    {description}\n"
                f"  {MARKETPLACE}\n"
                f"    {entry_description}"
            )

    for name in by_name:
        if name in seen_dirs:
            continue
        problems.append(
            f"{name}: {MARKETPLACE} registers this plugin, but there is no\n"
            f"plugins/{name}/ directory with a .claude-plugin/plugin.json."
        )

    return plural(len(manifests), "plugin"), problems


def main():
    failures = 0

    summary, problems = check_manifests()
    if not report("manifest descriptions", summary, problems):
        failures += 1

    if failures:
        print(f"check-sync: {plural(failures, 'check')} failed")
        return 1
    print("check-sync: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
