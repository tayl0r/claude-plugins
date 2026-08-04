#!/usr/bin/env python3
"""Every plugin a change touches carries a version ahead of the base ref's.

    python3 scripts/check-version-bump.py <base-ref> [<head-ref>]

<head-ref> defaults to HEAD. A plugin is *touched* when the change contributes
at least one path under plugins/<name>/ -- computed from the merge base, so a
branch that has already merged the base in is judged on what it adds, not on
what its last commit happened to touch. That is the case this check exists for:
two branches derive the same next version from the same base, the second merges
the first's release in without a conflict (both made the identical change), and
its diff against its own last commit shows no plugin.json row at all.

The comparison is against the base ref's *tip*, never the merge base: the
question is whether this number was already published, and only the tip knows
that. Versions compare as tuples of integers -- "2.10.0" is ahead of "2.9.0",
which a string comparison gets backwards, and both plugins in this marketplace
have passed a two-digit minor.

A plugin absent at the base (newly added) or absent at the head (removed) is
skipped: neither can reuse a published version.

Exit 0 iff every touched plugin passed, 1 otherwise. Python 3 stdlib only.

Design: docs/superpowers/specs/2026-08-03-gh-48-version-collision-design.md
"""

import json
import subprocess
import sys

MANIFEST = "plugins/%s/.claude-plugin/plugin.json"

FIX = """\
Bump past the base ref's version, not past your branch's. A concurrent change
may have published your next number already, and the merge has nothing to flag
-- both sides made the identical change, so there is no conflict to resolve."""


def git(*args):
    """Run git with args as argv elements -- never a shell string, so an empty
    ref is a loud "bad revision" rather than a different valid command."""
    result = subprocess.run(("git",) + args, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit("check-version-bump: FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), result.returncode,
                            result.stderr.strip() or "(no message)"))
    return result.stdout


def resolve(ref, label):
    sha = git("rev-parse", "--verify", ref + "^{commit}").strip()
    if not sha:
        raise SystemExit("check-version-bump: %s ref %r resolved to nothing" % (label, ref))
    return sha


def version_at(rev, name):
    """The plugin's declared version at rev, or None if it has no manifest there."""
    path = MANIFEST % name
    result = subprocess.run(("git", "show", "%s:%s" % (rev, path)),
                            capture_output=True, text=True)
    if result.returncode != 0:
        return None
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit("check-version-bump: cannot parse %s at %s: %s" % (path, rev, exc))
    version = data.get("version") if isinstance(data, dict) else None
    if not isinstance(version, str):
        raise SystemExit('check-version-bump: %s at %s has no "version" string' % (path, rev))
    return version


def key(version, rev, name):
    """The version as an orderable tuple. The shape is pinned rather than padded:
    tuples of unequal length do not order the way anyone means them to -- (1, 0)
    sorts below (1, 0, 0) though nothing moved -- and X.Y.Z is the only shape
    CLAUDE.md's bump rule describes. Nothing else in the repo enforces it."""
    parts = version.split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        raise SystemExit("check-version-bump: %s at %s has version %r, which is not "
                         "three dotted-numeric segments (X.Y.Z); this check cannot "
                         "order it" % (MANIFEST % name, rev, version))
    return tuple(int(part) for part in parts)


def touched(base_sha, head_sha):
    """(merge base, the plugin directories this change contributes a path under)."""
    merge_base = git("merge-base", base_sha, head_sha).strip()
    if not merge_base:
        raise SystemExit("check-version-bump: git merge-base printed nothing")
    names = set()
    # -z and --no-renames pin this diff's output, so neither a path's own bytes
    # nor a git config can shrink the set: without -z a newline or non-ASCII
    # path arrives C-quoted as '"plugins/...' and stops matching, and rename
    # detection reports a file moved *out* of plugins/<name>/ only at its
    # destination. Either one is a silent pass on a touched plugin.
    for path in git("diff", "--name-only", "-z", "--no-renames",
                    merge_base, head_sha).split("\0"):
        parts = path.split("/")
        if len(parts) > 2 and parts[0] == "plugins":
            names.add(parts[1])
    return merge_base, sorted(names)


def main():
    if not 2 <= len(sys.argv) <= 3:
        raise SystemExit("usage: python3 scripts/check-version-bump.py <base-ref> [<head-ref>]")
    base_sha = resolve(sys.argv[1], "base")
    head_sha = resolve(sys.argv[2] if len(sys.argv) == 3 else "HEAD", "head")
    merge_base, names = touched(base_sha, head_sha)
    print("check-version-bump: base %s, head %s, merge-base %s"
          % (base_sha[:9], head_sha[:9], merge_base[:9]))
    if not names:
        print("check-version-bump: no plugin directory touched ... OK")
        return 0

    problems, compared = [], 0
    for name in names:
        head_version = version_at(head_sha, name)
        base_version = version_at(base_sha, name)
        if head_version is None:
            print("  %-20s removed at head ... skipped" % name)
            continue
        if base_version is None:
            print("  %-20s new at head (%s) ... skipped" % (name, head_version))
            continue
        compared += 1
        ahead = key(head_version, head_sha, name) > key(base_version, base_sha, name)
        print("  %-20s %s -> %s ... %s"
              % (name, base_version, head_version, "OK" if ahead else "FAIL"))
        if not ahead:
            problems.append(
                '%s: version "%s" is not ahead of the base ref\'s "%s", and this change\n'
                "touches plugins/%s/. The install cache is keyed on the version string, so\n"
                "the new text would never be picked up on re-sync.\n\n"
                "  %s" % (name, head_version, base_version, name, MANIFEST % name))

    if not problems:
        print("check-version-bump: %d compared, %d skipped ... OK"
              % (compared, len(names) - compared))
        return 0
    for block in problems:
        print()
        print(block)
    print()
    print(FIX)
    print("check-version-bump: %d of %d compared plugin directories failed"
          % (len(problems), compared))
    return 1


if __name__ == "__main__":
    sys.exit(main())
