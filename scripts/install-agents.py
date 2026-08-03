#!/usr/bin/env python3
"""Install this repo's plugin agent definitions where Claude Code registers them.

Claude Code 2.1.220 does NOT register a plugin's `agents/*.md` as spawnable
subagent types — only user-level `~/.claude/agents/` and project-level
`.claude/agents/` are read, and only at session startup. Verified three ways:
neither plugin.json nor marketplace.json has an `agents` key, and an enabled
plugin's agent is absent from the Agent tool's available list while that same
plugin's skills are present. See docs/adr/0004.

The agent definitions stay in `plugins/<name>/agents/` — the documented
convention, and the place they will already be if a later Claude Code starts
registering them. This script copies them to `~/.claude/agents/` so they
register today.

    python3 scripts/install-agents.py            # install / update
    python3 scripts/install-agents.py --check    # exit 1 if a shipped agent differs

`--check` compares in one direction only: every agent this repo ships against its
installed copy. It cannot flag an installed agent the repo no longer ships, because
`~/.claude/agents/` also holds agents from elsewhere and nothing here marks which
copies came from this repo.

Copies rather than symlinks on purpose: a symlink into a git worktree under
`.claude/worktrees/` dangles the moment that worktree is removed, and a
dangling agent definition fails at spawn time inside an unrelated session.
The cost is that editing an agent means re-running this; `--check` reports it.

Registration happens at startup, so restart Claude Code after installing.
Python 3 stdlib only.
"""

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEST = Path.home() / ".claude" / "agents"


def frontmatter_name(path, text):
    """The `name:` field of the leading --- block. That name, not the filename,
    is what Claude Code registers, so a mismatch would install to the wrong file."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path}: no leading '---' frontmatter block")
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith("name:"):
            name = line[len("name:"):].strip()
            if not name:
                raise ValueError(f"{path}: empty 'name:' in frontmatter")
            if name != path.stem:
                raise ValueError(
                    f"{path}: frontmatter name {name!r} != filename stem {path.stem!r}; "
                    f"they must match so the installed path is predictable")
            return name
    raise ValueError(f"{path}: no 'name:' line in frontmatter")


def collect():
    """name -> (text, [source paths]). Mirrored plugins ship byte-identical
    copies of a shared agent; identical duplicates collapse, conflicts raise."""
    found = {}
    for src in sorted(REPO_ROOT.glob("plugins/*/agents/*.md")):
        text = src.read_text(encoding="utf-8")
        name = frontmatter_name(src, text)
        rel = src.relative_to(REPO_ROOT)
        if name in found:
            prev_text, prev_srcs = found[name]
            if prev_text != text:
                raise ValueError(
                    f"two agents named {name!r} with differing content: "
                    f"{prev_srcs[0]} and {rel}. Mirrored copies must be "
                    f"byte-identical; otherwise rename one.")
            prev_srcs.append(rel)
        else:
            found[name] = (text, [rel])
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="report what would change and exit 1 if anything would")
    args = ap.parse_args()

    try:
        agents = collect()
    except ValueError as exc:
        print(f"install-agents: {exc}", file=sys.stderr)
        return 1
    if not agents:
        print("install-agents: no plugins/*/agents/*.md found", file=sys.stderr)
        return 1

    stale, actions = [], []
    for name, (text, srcs) in sorted(agents.items()):
        dest = DEST / f"{name}.md"
        current = dest.read_text(encoding="utf-8") if dest.exists() else None
        if current == text:
            verb = "unchanged"
        else:
            verb = "install" if current is None else "update"
            stale.append(name)
        actions.append((verb, name, srcs, dest, text))

    for verb, name, srcs, dest, text in actions:
        mirrored = f"  (mirrored: {len(srcs)} copies)" if len(srcs) > 1 else ""
        if verb == "unchanged":
            print(f"  unchanged  {name}{mirrored}")
            continue
        if args.check:
            print(f"  WOULD {verb.upper():7s} {name}  <- {srcs[0]}{mirrored}")
            continue
        DEST.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        print(f"  {'installed' if verb == 'install' else 'updated':10s} "
              f"{name}  <- {srcs[0]}{mirrored}")

    if args.check:
        if stale:
            sys.stdout.flush()
            print(f"\ninstall-agents: {len(stale)} agent(s) differ from the repo: "
                  f"{', '.join(stale)}\nRun: python3 scripts/install-agents.py",
                  file=sys.stderr)
            return 1
        print(f"\ninstall-agents: all {len(agents)} agent(s) up to date in {DEST}")
        return 0

    print(f"\ninstall-agents: {len(agents)} agent(s) in {DEST}")
    if stale:
        print("Restart Claude Code — agent definitions are read at session startup.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except OSError as exc:
        # One handler for every filesystem failure — an unreadable source, an
        # unwritable ~/.claude/agents, a destination that is a directory. Kept at
        # the top level rather than around individual reads and writes, so no one
        # path is guarded more tightly than the others.
        print(f"install-agents: {exc}", file=sys.stderr)
        sys.exit(1)
