---
dev-flow:
  slug: gh-8-drift-check
  spec: docs/superpowers/specs/2026-07-26-gh-8-drift-check-design.md
---

# Mechanical drift check for the duplicated plugin prose — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `scripts/check-sync.py` — a zero-flag, stdlib-only Python 3 checker that fails loudly when the two facts this repo duplicates by hand drift apart (the `adversarial-review/SKILL.md` mirror pair, and each plugin's `description` across `plugin.json` and `marketplace.json`) — plus the PR workflow that runs it and the CLAUDE.md bullet that documents it.

**Architecture:** One script, two independent checks, one command. **Check A** is entirely *derived* from the filesystem — it globs `plugins/*/.claude-plugin/plugin.json` and cross-checks each against `.claude-plugin/marketplace.json`, so a new plugin is covered the day its directory exists. **Check B** is *declared* — a `MIRROR_PAIRS` Python list literal names each file pair that must stay line-for-line parallel after a per-pair canonicalization, plus the handful of divergences deliberately allowed. Both checks always run (one invocation reports every problem in the tree), and the process exits 0 iff all pass. `.github/workflows/check-sync.yml` runs the identical command on every PR.

**Tech Stack:** Python 3 standard library only (`json`, `sys`, `textwrap`, `pathlib`). GitHub Actions YAML. JSON manifests. Markdown. No package manager, no lockfile, no venv, no `requirements.txt`, no `setup-python`, no network.

---

## Global Constraints

Every task's requirements implicitly include this section.

- **Repo root:** `/Users/taylor/dev/claude-plugins`. Every path in this plan is relative to it. Work in place on the existing branch `tayl0r/gh-8-drift-check` — **do not create a git worktree**.
- **Do not push, do not open a PR, do not merge.** Per-task `git commit` is expected; nothing beyond it.
- **No `plugin.json` `version` bump anywhere.** The design (Decision 8) is explicit: this change touches no file under `plugins/`, no plugin's behavior changes, so no bump is required and none should be added. Do not "helpfully" bump `dev-flow` or `dev-flow-worktree`.
- **No file under `plugins/` may be modified, added, or deleted in the final diff.** Two tasks temporarily create or edit files under `plugins/` to prove a failure mode; each such task ends by removing/restoring them and asserting `git status --porcelain` prints nothing. A stray mutation left behind poisons every later task.
- **Mutate-and-restore discipline.** Any step that edits a file to observe a failure is followed, in the same task, by a restore step and a cleanliness assertion:

  ```bash
  cd /Users/taylor/dev/claude-plugins
  git status --porcelain
  ```

  Expected output: **nothing at all** (zero lines) — *except* that an untracked `?? docs/superpowers/plans/2026-07-26-gh-8-drift-check-plan.md` (and/or its design doc) may appear if the pipeline has not yet committed them. Those two `docs/superpowers/` paths are the only tolerated entries anywhere in this plan. **Any other path, and in particular anything under `plugins/` or `scripts/`, means a mutation was left behind — stop and clean up before continuing.** Every "Expected: nothing" in the steps below is governed by this rule.
- **There is no test framework, no build, no linter.** Do not run `pytest`, `npm test`, `ruff`, or `black` — none exist. **Every verification step in this plan is an exit code plus stdout from `python3 scripts/check-sync.py`, a `git` read-back, or `claude plugin validate .`.**
- **Python 3 stdlib only.** The only permitted imports in `scripts/check-sync.py` are `json`, `sys`, `textwrap`, and `from pathlib import Path`. No third-party packages, no `requirements.txt`, no `pyproject.toml`, no `setup.py`.
- **Zero flags.** `scripts/check-sync.py` accepts no command-line arguments and must never grow a `--fix` / `--bless` / `--update` mode. This is a deliberate design decision (Decision 1): an auto-regenerate escape hatch turns a check into a ceremony.
- **Everything goes to stdout.** No `sys.stderr`, no `logging`. Exit **0** iff every check passed, **1** otherwise. A missing declared path or an unparseable manifest is reported as a failure of the check that needed it, not as a distinct exit code.
- **All file reads pass `encoding="utf-8"` explicitly.** These files contain em dashes (`—`); a C/POSIX-locale run with the locale default would raise `UnicodeDecodeError` as a stderr traceback. Never omit the encoding.
- **The invocation is `python3 scripts/check-sync.py`, byte-identical locally and in CI.** The script resolves its own repo root from `__file__`, so it works from any cwd. Do not `chmod +x` the script and do not invoke it as `./scripts/check-sync.py` — match the repo's existing `plugins/youtube-upload/scripts/yt-resumable-upload.py`, which has a shebang and mode `644`.
- **Copy code and message strings verbatim.** Every output string that design Decision 4 specifies is reproduced in the Task 2 and Task 4 listings character-for-character; Check A's remaining messages (name mismatch, unregistered directory, duplicate entry, source format, unreadable/unparseable manifest) are specified by the Task 2 code listing itself and asserted byte-for-byte by Task 3. Retyping em dashes as hyphens, or "smart" quotes as ASCII, will make verification steps fail.
- **The shell hook mangles `diff`/`find`/`grep` output and exit codes.** Prefix those with `rtk proxy` when exact output or exit codes matter (e.g. `rtk proxy grep -c ...`).

---

## File map

| File | Responsibility | Tasks |
|---|---|---|
| `.claude-plugin/marketplace.json` | The registry. Gains one comma in the `dev-flow-worktree` description so it matches its `plugin.json`. | 1 |
| `scripts/check-sync.py` | **New.** The whole checker. Check A (derived manifest sync) in Task 2; Check B (`MIRROR_PAIRS`, canonicalization, exceptions) in Task 4. | 2, 4 |
| `.github/workflows/check-sync.yml` | **New.** The repo's first workflow. One job, one step, `pull_request` + `push: [main]`. | 6 |
| `CLAUDE.md` | Repo instructions loaded into every session. Gains one bullet in **Changing a plugin**, and its opening line's now-false repo description is repaired. | 7 |

No file under `plugins/` is created, modified, or deleted. No file is renamed or removed.

---

### Task 1: Repair the live `dev-flow-worktree` description drift

**Files:**
- Modify: `.claude-plugin/marketplace.json:46`
- Test: none yet (the checker does not exist) — verified by direct JSON comparison

**Interfaces:**
- Consumes: nothing. This is the first task.
- Produces: a tree on which Check A (Task 2) is **green**. This ordering is required by design Decision 8 / Scope of edits: if the fix landed after the checker, the repo's first CI run would be red for a pre-existing defect.

**Context:** `plugins/dev-flow-worktree/.claude-plugin/plugin.json` says `"... merge pipeline, isolated in a dedicated git worktree, ..."` while `.claude-plugin/marketplace.json` says `"... merge pipeline isolated in a dedicated git worktree, ..."` — one missing comma. CLAUDE.md already requires these to be identical; nothing enforced it. The repair goes on the **marketplace** side (Decision 8): `plugin.json` is the source of truth for Check A rule 4, the `plugin.json` text is the better-punctuated of the two, and editing the plugin side would put a file under `plugins/` in the diff and reopen the version-bump question over a comma.

- [x] **Step 1: Confirm the drift is still present**

```bash
cd /Users/taylor/dev/claude-plugins
python3 -c "
import json
p = json.load(open('plugins/dev-flow-worktree/.claude-plugin/plugin.json', encoding='utf-8'))
m = json.load(open('.claude-plugin/marketplace.json', encoding='utf-8'))
e = [x for x in m['plugins'] if x['name'] == 'dev-flow-worktree'][0]
print('equal:', p['description'] == e['description'])
"
```

Expected output:

```
equal: False
```

- [x] **Step 2: Add the missing comma in `.claude-plugin/marketplace.json`**

Find this line (line 46, inside the `dev-flow-worktree` entry):

```
      "description": "Autonomous design -> plan -> execute -> PR -> merge pipeline isolated in a dedicated git worktree, with adversarial review at each artifact boundary"
```

Replace it with (one comma added after `pipeline`):

```
      "description": "Autonomous design -> plan -> execute -> PR -> merge pipeline, isolated in a dedicated git worktree, with adversarial review at each artifact boundary"
```

Change nothing else in the file — not whitespace, not key order, not any other entry.

- [x] **Step 3: Verify the two descriptions now match, and that only this file changed**

```bash
cd /Users/taylor/dev/claude-plugins
python3 -c "
import json
p = json.load(open('plugins/dev-flow-worktree/.claude-plugin/plugin.json', encoding='utf-8'))
m = json.load(open('.claude-plugin/marketplace.json', encoding='utf-8'))
e = [x for x in m['plugins'] if x['name'] == 'dev-flow-worktree'][0]
print('equal:', p['description'] == e['description'])
"
git status --porcelain
```

Expected output:

```
equal: True
 M .claude-plugin/marketplace.json
```

Exactly one modified file. If `plugins/...` appears, you edited the wrong side — revert and redo.

- [x] **Step 4: Verify the marketplace still validates**

```bash
cd /Users/taylor/dev/claude-plugins
claude plugin validate .
echo "exit=$?"
```

Expected: `exit=0`. Eight missing-author warnings are expected and are not failures.

- [x] **Step 5: Commit**

```bash
cd /Users/taylor/dev/claude-plugins
git add .claude-plugin/marketplace.json
git commit -m "marketplace: match the dev-flow-worktree description to its plugin.json"
```

---

### Task 2: Create `scripts/check-sync.py` with Check A (manifest description sync)

**Files:**
- Create: `scripts/check-sync.py`
- Test: the script is its own test — run it and read the exit code

**Interfaces:**
- Consumes: the green tree from Task 1.
- Produces, for Task 4 to build on — copy these names exactly:
  - `REPO_ROOT` — `Path`, the repo root, resolved from `__file__`.
  - `MARKETPLACE` — `str`, `".claude-plugin/marketplace.json"`.
  - `plural(count, word) -> str` — `"1 plugin"` / `"8 plugins"`.
  - `READ_ERRORS` — the exception tuple every reported read is wrapped in: `(OSError, UnicodeDecodeError)`.
  - `read_text(relpath) -> str` — repo-relative UTF-8 read; raises anything in `READ_ERRORS`.
  - `report(label, summary, problems) -> bool` — prints one unit's progress line and any problem blocks, each separated by a blank line; returns `True` when `problems` is empty.
  - `check_manifests() -> (str, list[str])` — the same `(summary, problems)` shape `check_pair` returns in Task 4.
  - `main() -> int` — accumulates a `failures` count and prints the final summary line.

**Context:** Check A enforces the two rules CLAUDE.md already states but nothing enforced. It is entirely derived from the filesystem — nothing to declare. For every `plugins/<dir>/.claude-plugin/plugin.json`: its `name` equals `<dir>`; `.claude-plugin/marketplace.json` has exactly one entry with that name; that entry's `source` is exactly `./plugins/<dir>`; that entry's `description` is byte-equal to the plugin.json one. And symmetrically, every marketplace entry has a matching plugin directory — the reverse direction matters because `claude plugin validate .` iterates the *marketplace's* entry list, so an unregistered plugin directory is invisible to it (verified: it exits 0 on such a tree).

The `description differs` message below is reproduced **byte-for-byte** from design Decision 4 — do not reword it. Copy the other messages exactly as written too — Task 3 asserts several of them byte-for-byte. (Their maintenance contract for future edits outside this plan is only that they keep three elements: the plugin name, the rule, and the file path(s).)

- [x] **Step 1: Create `scripts/` and write the script**

Create the directory and write `scripts/check-sync.py` with exactly this content:

```python
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
```

- [x] **Step 2: Run it — the tree is green after Task 1**

```bash
cd /Users/taylor/dev/claude-plugins
python3 scripts/check-sync.py
echo "exit=$?"
```

Expected output, exactly:

```
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: all checks passed
exit=0
```

- [x] **Step 3: Verify it runs from any cwd (the script resolves its own repo root)**

```bash
cd /
python3 /Users/taylor/dev/claude-plugins/scripts/check-sync.py
echo "exit=$?"
```

Expected: the same two lines and `exit=0`. If this fails, `REPO_ROOT` was not derived from `__file__`.

- [x] **Step 4: Verify stdlib-only imports and mode 644**

```bash
cd /Users/taylor/dev/claude-plugins
rtk proxy grep -nE '^(import|from) ' scripts/check-sync.py
ls -l scripts/check-sync.py
```

Expected import lines, and nothing else (the line numbers shift to 19–22 in Task 4, when the docstring grows):

```
13:import json
14:import sys
15:import textwrap
16:from pathlib import Path
```

Expected mode: `-rw-r--r--`. If the file is executable, run `chmod 644 scripts/check-sync.py`.

- [x] **Step 5: Commit**

```bash
cd /Users/taylor/dev/claude-plugins
git add scripts/check-sync.py
git commit -m "check-sync: add the manifest description/source/registration check"
```

---

### Task 3: Prove Check A catches the three defect families that have actually occurred

**Files:**
- Temporarily modify: `.claude-plugin/marketplace.json` (restored)
- Temporarily create: `plugins/scratch/.claude-plugin/plugin.json` (deleted)
- Test: `python3 scripts/check-sync.py` exit codes and stdout

**Interfaces:**
- Consumes: `scripts/check-sync.py` from Task 2.
- Produces: nothing. This task's deliverable is *evidence*, plus any fix to `scripts/check-sync.py` the experiments turn up. If an experiment's output does not match, fix the script, re-run, and commit the fix.

**Context:** This task covers design Smoke test steps 2 and 8, and acceptance criteria 10 and 11. Three of Check A's four rule families have already failed in real commits in this repo: description drift (born in `a104d2b`, the live one Task 1 just fixed), unregistered plugin directories (`b192e3f`), and `source` paths missing the leading `./` (`60c799c`). A fourth direction — a *marketplace entry* with no plugin directory — has no instance in this repo's history, but it is the one Check A direction nothing else in this plan exercises and `claude plugin validate .` misses it too, so Step 6 pins it.

> **Constraint reminder:** this task creates a directory under `plugins/` (Step 4) and edits `.claude-plugin/marketplace.json` three times. The directory is untracked and is deleted in Step 5; every marketplace edit is undone with `git restore` in the same step that made it. `git status --porcelain` must be empty when the task ends.

- [ ] **Step 1: Revert the Task 1 comma fix and observe the failure**

```bash
cd /Users/taylor/dev/claude-plugins
python3 -c "
import pathlib
p = pathlib.Path('.claude-plugin/marketplace.json')
t = p.read_text(encoding='utf-8')
old = 'merge pipeline, isolated in a dedicated git worktree'
new = 'merge pipeline isolated in a dedicated git worktree'
assert t.count(old) == 1
p.write_text(t.replace(old, new), encoding='utf-8')
"
python3 scripts/check-sync.py
echo "exit=$?"
```

Expected output, exactly (this is design Decision 4's Check A failure example):

```
check-sync: manifest descriptions ... FAIL

  dev-flow-worktree: description differs between the two manifests.
  CLAUDE.md requires them to be identical.

    plugins/dev-flow-worktree/.claude-plugin/plugin.json
      Autonomous design -> plan -> execute -> PR -> merge pipeline, isolated in a dedicated git worktree, with adversarial review at each artifact boundary
    .claude-plugin/marketplace.json
      Autonomous design -> plan -> execute -> PR -> merge pipeline isolated in a dedicated git worktree, with adversarial review at each artifact boundary

check-sync: 1 check failed
exit=1
```

- [ ] **Step 2: Restore, and confirm the check goes green again**

```bash
cd /Users/taylor/dev/claude-plugins
git restore .claude-plugin/marketplace.json
python3 scripts/check-sync.py
echo "exit=$?"
git status --porcelain
```

Expected:

```
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: all checks passed
exit=0
```

and `git status --porcelain` prints **nothing**.

- [ ] **Step 3: Break the `source` format and observe the failure**

```bash
cd /Users/taylor/dev/claude-plugins
python3 -c "
import pathlib
p = pathlib.Path('.claude-plugin/marketplace.json')
t = p.read_text(encoding='utf-8')
p.write_text(t.replace('\"./plugins/justfile\"', '\"plugins/justfile\"'), encoding='utf-8')
"
python3 scripts/check-sync.py
echo "exit=$?"
git restore .claude-plugin/marketplace.json
git status --porcelain
```

Expected output:

```
check-sync: manifest descriptions ... FAIL

  justfile: marketplace entry "source" is "plugins/justfile", expected
  "./plugins/justfile". CLAUDE.md requires the leading "./".

    .claude-plugin/marketplace.json

check-sync: 1 check failed
exit=1
```

and `git status --porcelain` prints **nothing** after the restore.

- [ ] **Step 4: Add an unregistered plugin directory and observe the failure**

```bash
cd /Users/taylor/dev/claude-plugins
mkdir -p plugins/scratch/.claude-plugin
printf '{\n  "name": "scratch",\n  "version": "0.0.1",\n  "description": "probe"\n}\n' > plugins/scratch/.claude-plugin/plugin.json
python3 scripts/check-sync.py
echo "exit=$?"
```

Expected output:

```
check-sync: manifest descriptions ... FAIL

  scratch: no entry in .claude-plugin/marketplace.json.
  Every plugin directory must be registered. `claude plugin validate .`
  does not catch this: it only iterates the marketplace's own entries.

    plugins/scratch/.claude-plugin/plugin.json

check-sync: 1 check failed
exit=1
```

- [ ] **Step 5: Confirm `claude plugin validate .` is blind to this, then clean up**

This is the evidence for design Decision 2's claim that Check A is complementary, not redundant.

```bash
cd /Users/taylor/dev/claude-plugins
claude plugin validate . > /dev/null 2>&1
echo "validate exit=$?"
rm -rf plugins/scratch
python3 scripts/check-sync.py
echo "check exit=$?"
git status --porcelain
```

Expected:

```
validate exit=0
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: all checks passed
check exit=0
```

and `git status --porcelain` prints **nothing**. Verify `plugins/scratch` is gone: `ls plugins/` must list exactly the eight original directories (`address-pr-feedback`, `better-code-review`, `dev-flow`, `dev-flow-worktree`, `justfile`, `react-performance`, `sync-latest-git`, `youtube-upload`).

- [ ] **Step 6: The reverse direction — a marketplace entry with no plugin directory**

The mirror image of Step 4, and the only Check A direction no other step in this plan covers. `claude plugin validate .` is blind to it as well (verified: exit 0), so this rule has no other enforcement anywhere in the repo.

```bash
cd /Users/taylor/dev/claude-plugins
python3 - <<'PY'
import pathlib
p = pathlib.Path(".claude-plugin/marketplace.json")
t = p.read_text(encoding="utf-8")
anchor = '    }\n  ]\n}\n'
ghost = ('    },\n    {\n      "name": "ghost",\n      "source": "./plugins/ghost",\n'
         '      "description": "an entry with no plugin directory"\n    }\n  ]\n}\n')
assert t.count(anchor) == 1
p.write_text(t.replace(anchor, ghost), encoding="utf-8")
PY
python3 scripts/check-sync.py
echo "check exit=$?"
claude plugin validate . > /dev/null 2>&1
echo "validate exit=$?"
git restore .claude-plugin/marketplace.json
git status --porcelain
```

Expected output:

```
check-sync: manifest descriptions ... FAIL

  ghost: .claude-plugin/marketplace.json registers this plugin, but there is no
  plugins/ghost/ directory with a .claude-plugin/plugin.json.

check-sync: 1 check failed
check exit=1
validate exit=0
```

and `git status --porcelain` prints **nothing** after the restore. `validate exit=0` is the point: this is a third case where the repo's existing tooling passes a tree that Check A rejects.

- [ ] **Step 7: Commit only if a script fix was needed**

If Steps 1–6 all matched, there is nothing to commit — `git status --porcelain` is empty and this task ends here. If you had to correct `scripts/check-sync.py`:

```bash
cd /Users/taylor/dev/claude-plugins
git add scripts/check-sync.py
git commit -m "check-sync: correct Check A output"
```

---

### Task 4: Add Check B (declared mirror pairs) to `scripts/check-sync.py`

**Files:**
- Modify: `scripts/check-sync.py`
- Test: `python3 scripts/check-sync.py`

**Interfaces:**
- Consumes: `plural`, `read_text`, `report`, `REPO_ROOT` from Task 2.
- Produces:
  - `MIRROR_PAIRS` — module-level `list[dict]`; each dict has keys `name`, `a`, `b`, `canonicalize` (list of `(src, dst)` tuples), `exceptions` (list of dicts with keys `why`, `a`, `b`).
  - `canonicalize(text, substitutions) -> str`.
  - `format_why(why) -> str`.
  - `check_pair(pair) -> (str, list[str])`.
  - Task 8 adds a second temporary entry to `MIRROR_PAIRS` and removes it again; the schema above is the contract it relies on.

**Context — read design Decision 3 before starting.** The algorithm, in the design's numbering:

1. Read both files as UTF-8 text, default universal-newlines mode. Any `OSError` fails that pair, naming the path and the OS error.
2. Canonicalize **both** sides with every declared substitution — symmetric, so the rule stays correct if a cross-reference to the other variant appears in either file. Substitutions are applied longest-source-token-first, so declaration order carries no meaning. Each exception's `a`/`b` strings get the same canonicalization before matching.
3. If the canonicalized texts are byte-equal, skip the line comparison and go straight to step 6 — with the files identical, every declared exception is by definition stale.
4. If exactly one canonicalized text ends in a newline, the pair fails naming the file that lacks it; comparison continues. Split with `str.splitlines()` so a final newline does not produce a phantom empty last line and the reported count agrees with `wc -l`. **If the line counts differ, the pair fails** with both counts and the 1-based index of the first *undeclared* divergence in the common prefix — a scan that **skips positions whose canonicalized lines match a declared exception**, the same content match step 5 performs — plus both raw lines there; if the common prefix holds no undeclared divergence (the extra lines sit at the end of the longer file), say so and name the first unmatched line instead. Steps 5–6 are skipped for that pair — past a one-sided insertion every later index is offset. **One definition of "declared divergence", shared by this scan and step 5**: without it the scan stops at the pair's first declared divergence and reports that line for every length-changing edit below it (measured: on the enrolled pair, deletions anywhere in lines 13–81 would all report "line 12").
5. Compare index by index. At each index where the canonicalized lines differ, look for a declared exception whose canonicalized `a`/`b` equal the canonicalized lines at that index. Found → allowed, mark the exception used. Not found → report the 1-based line number and both raw lines. Exceptions match on **content, not position**.
6. Any usable exception never used is a failure (**stale**). An exception whose `a` and `b` are equal after canonicalization can never match; report it as **malformed**, not stale.

Only one pair is enrolled: `adversarial-review` (81/81 lines, one 1:1 divergence at line 12). The pipeline `SKILL.md` pair and the two `README.md`s are deliberately **not** enrollable under this schema — do not add them (design Decision 6).

- [ ] **Step 1: Replace the module docstring's Check A paragraph with the two-check version**

Find these lines near the top of `scripts/check-sync.py`:

```
Check A: every plugins/<dir>/.claude-plugin/plugin.json agrees with its
.claude-plugin/marketplace.json entry (name, source, description), and every
marketplace entry has a plugin directory.

Exit 0 iff every check passed, 1 otherwise. Python 3 stdlib only, no flags.
```

Replace them with:

```
Two independent checks, one command, no flags:

  Check A  every plugins/<dir>/.claude-plugin/plugin.json agrees with its
           .claude-plugin/marketplace.json entry (name, source, description),
           and every marketplace entry has a plugin directory.

  Check B  each pair declared in MIRROR_PAIRS is line-for-line identical after
           canonicalization, except where an exception declares otherwise.

Both checks run every time, so one run reports every problem in the tree.
Exit 0 iff every check passed, 1 otherwise. Python 3 stdlib only, no flags.
```

- [ ] **Step 2: Insert the `MIRROR_PAIRS` table**

Find this line:

```python
MARKETPLACE = ".claude-plugin/marketplace.json"
```

Insert the following **immediately after it** (one blank line, then the block). The two exception strings are the *raw* line 12 of each file, wrapped across Python string literals; they must reconstruct those lines byte-for-byte, em dashes and backticks included:

```python

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
]
```

- [ ] **Step 3: Verify the exception strings reconstruct the real file lines**

Do this before writing any more code — a single mistyped character here makes every later step confusing.

```bash
cd /Users/taylor/dev/claude-plugins
python3 -c "
import importlib.util
spec = importlib.util.spec_from_file_location('cs', 'scripts/check-sync.py')
cs = importlib.util.module_from_spec(spec); spec.loader.exec_module(cs)
exc = cs.MIRROR_PAIRS[0]['exceptions'][0]
for side in ('a', 'b'):
    line = open(cs.MIRROR_PAIRS[0][side], encoding='utf-8').read().splitlines()[11]
    print(side, 'matches file line 12:', exc[side] == line)
"
```

Expected output:

```
a matches file line 12: True
b matches file line 12: True
```

If either prints `False`, re-copy that string. (Loading the module runs nothing: `main()` is guarded by `if __name__ == "__main__"`.)

- [ ] **Step 4: Append the Check B section**

Insert the following block between `check_manifests`'s closing `return plural(len(manifests), "plugin"), problems` and the existing `def main():`. Leave exactly two blank lines before the block's first line and exactly two blank lines after its last line (`    return summary, [header, *items]`), so `def main():` still has two blank lines above it:

```python
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
    containing another as a substring is always replaced first."""
    for src, dst in sorted(substitutions, key=lambda pair: -len(pair[0])):
        text = text.replace(src, dst)
    return text


def format_why(why):
    return textwrap.fill(why, width=84, initial_indent="  why: ",
                         subsequent_indent="       ")


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
    lines = {side: canon[side].splitlines() for side in ("a", "b")}
    raw_lines = {side: texts[side].splitlines() for side in ("a", "b")}

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

    # Step 6 (part 1): an exception whose two sides match after canonicalization
    # declares no divergence and can never fire. Split usable from malformed up
    # front: both the line-count scan and the positional comparison match
    # against the usable set.
    usable = []
    malformed = []
    for exc in exceptions:
        canon_a = canonicalize(exc["a"], subs)
        canon_b = canonicalize(exc["b"], subs)
        if canon_a == canon_b:
            malformed.append(exc)
        else:
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

    for exc in malformed:
        items.append(
            "malformed exception: after canonicalization its two sides are identical,\n"
            "so it declares no divergence and can never match. The canonicalization\n"
            "already permits this difference; remove the entry from "
            "scripts/check-sync.py.\n"
            f"{format_why(exc['why'])}\n"
            f"  A: {exc['a']}\n"
            f"  B: {exc['b']}"
        )

    for position, (_, _, exc) in enumerate(usable):
        if position in used:
            continue
        items.append(
            "stale exception: the divergence it describes no longer appears in the "
            "files.\n"
            f"{format_why(exc['why'])}\n"
            f"  A: {exc['a']}\n"
            f"  B: {exc['b']}\n"
            "Remove the entry from scripts/check-sync.py, or restore the divergence "
            "it describes."
        )

    if not items:
        return summary, []
    return summary, [header, *items]


```

- [ ] **Step 5: Wire Check B into `main()`**

Find this block in `main()`:

```python
    summary, problems = check_manifests()
    if not report("manifest descriptions", summary, problems):
        failures += 1

    if failures:
```

Replace it with:

```python
    summary, problems = check_manifests()
    if not report("manifest descriptions", summary, problems):
        failures += 1

    for pair in MIRROR_PAIRS:
        summary, problems = check_pair(pair)
        if not report(f'mirror pair "{pair["name"]}"', summary, problems):
            failures += 1

    if failures:
```

- [ ] **Step 6: Run it — the pair is green today**

```bash
cd /Users/taylor/dev/claude-plugins
python3 scripts/check-sync.py
echo "exit=$?"
```

Expected output, exactly (this is design Decision 4's success example):

```
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... OK (81 lines, 1 declared exception)
check-sync: all checks passed
exit=0
```

The `81 lines` count agrees with `wc -l` — confirm:

```bash
cd /Users/taylor/dev/claude-plugins
rtk proxy wc -l plugins/dev-flow/skills/adversarial-review/SKILL.md plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
```

Expected: `81` for both.

- [ ] **Step 7: Confirm the imports are still stdlib-only and nothing under `plugins/` moved**

```bash
cd /Users/taylor/dev/claude-plugins
rtk proxy grep -nE '^(import|from) ' scripts/check-sync.py
git status --porcelain
```

Expected: the same four imports as Task 2 — now reported at lines 19–22, because Step 1 grew the docstring by six lines and `MIRROR_PAIRS` sits *below* the imports — and exactly one changed file:

```
19:import json
20:import sys
21:import textwrap
22:from pathlib import Path
 M scripts/check-sync.py
```

- [ ] **Step 8: Commit**

```bash
cd /Users/taylor/dev/claude-plugins
git add scripts/check-sync.py
git commit -m "check-sync: add the declared mirror-pair check and enroll adversarial-review"
```

---

### Task 5: Prove Check B's failure modes on the enrolled pair

**Files:**
- Temporarily modify: `plugins/dev-flow/skills/adversarial-review/SKILL.md`, `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md`, `scripts/check-sync.py` (all restored)
- Test: `python3 scripts/check-sync.py` exit codes and stdout

**Interfaces:**
- Consumes: `scripts/check-sync.py` from Task 4.
- Produces: nothing. The deliverable is *evidence*, plus any script fix an experiment turns up.

**Context:** This task covers design Smoke test steps 3–7 and acceptance criteria 1–6. Shorthands used below:

```
A = plugins/dev-flow/skills/adversarial-review/SKILL.md
B = plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
```

> **Constraint reminder:** every step here edits tracked files under `plugins/`. Each experiment ends with `git restore` and a `git status --porcelain` that must print nothing. Nothing from this task may reach a commit except a genuine fix to `scripts/check-sync.py`.
>
> Some reported lines are very long (line 18 is ~950 characters). They are printed **whole** by design — the expected output below marks elisions with `[…]`, but the real output must show the complete line with no truncation.
>
> For FAIL steps, the paired structural assertion plus the exit code are the pass/fail signal; the full block documents the expected shape. If real output and this document disagree only inside a `[…]`-elided line, the plan's transcription is the suspect, not the tree — never retype a SKILL.md line or a script message to make it match this document.

- [ ] **Step 1: Undeclared divergence — edit one word in A only (AC 1)**

```bash
cd /Users/taylor/dev/claude-plugins
python3 -c "
import pathlib
p = pathlib.Path('plugins/dev-flow/skills/adversarial-review/SKILL.md')
L = p.read_text(encoding='utf-8').split('\n')
assert 'passes MUST run' in L[17]
L[17] = L[17].replace('passes MUST run', 'passes SHOULD run')
p.write_text('\n'.join(L), encoding='utf-8')
"
python3 scripts/check-sync.py
echo "exit=$?"
```

Expected output:

```
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... FAIL

  These two files must stay line-for-line identical after canonicalizing
  "dev-flow-worktree" -> "dev-flow". Every cross-cutting edit lands in both.

    A: plugins/dev-flow/skills/adversarial-review/SKILL.md
    B: plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md

  line 18: undeclared divergence
    A: **Review integrity (never inline).** The seed and resolver passes SHOULD run as separate subagents […]
    B: **Review integrity (never inline).** The seed and resolver passes MUST run as separate subagents […]

  Fix: mirror the edit into both files. If the divergence is genuinely variant-specific,
  add it to MIRROR_PAIRS["adversarial-review"]["exceptions"] in scripts/check-sync.py
  with a one-line reason.

check-sync: 1 check failed
exit=1
```

Structural assertions (independent of the long lines) — these, plus `exit=1`, are the pass/fail signal:

```bash
cd /Users/taylor/dev/claude-plugins
python3 scripts/check-sync.py | rtk proxy grep -c '^  line 18: undeclared divergence$'
python3 scripts/check-sync.py | rtk proxy grep -cE '^  line [0-9]+: undeclared divergence$'
```

Expected: `1` and `1`. The second is the load-bearing one: it asserts line 18 is the **only** flagged line. A run that also flagged line 12 — the declared exception — would still satisfy the first grep, and would mean exception matching is broken.

- [ ] **Step 2: Mirror the same edit into B — green again, script untouched (AC 3)**

```bash
cd /Users/taylor/dev/claude-plugins
python3 -c "
import pathlib
p = pathlib.Path('plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md')
L = p.read_text(encoding='utf-8').split('\n')
L[17] = L[17].replace('passes MUST run', 'passes SHOULD run')
p.write_text('\n'.join(L), encoding='utf-8')
"
python3 scripts/check-sync.py
echo "exit=$?"
git status --porcelain
```

Expected:

```
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... OK (81 lines, 1 declared exception)
check-sync: all checks passed
exit=0
 M plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
 M plugins/dev-flow/skills/adversarial-review/SKILL.md
```

The critical part: **`scripts/check-sync.py` is not in that list.** Mirroring an edit correctly costs no change to the checker.

- [ ] **Step 3: Restore both files**

```bash
cd /Users/taylor/dev/claude-plugins
git restore plugins/dev-flow/skills/adversarial-review/SKILL.md plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
git status --porcelain
```

Expected: **nothing**.

- [ ] **Step 4: Line-count mismatch — two deletions, each must name where the length actually changed (AC 2)**

This step is **two experiments on the same pair**. Together they prove the line-count scan consults declared exceptions: a scan that ignored them would stop at line 12 — the pair's one declared divergence — and print byte-identical output for both.

**Experiment A — delete line 30 from B.** Mutate and run first; the assertions run while the mutation is live.

```bash
cd /Users/taylor/dev/claude-plugins
python3 -c "
import pathlib
p = pathlib.Path('plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md')
L = p.read_text(encoding='utf-8').split('\n')
del L[29]
p.write_text('\n'.join(L), encoding='utf-8')
"
python3 scripts/check-sync.py
echo "exit=$?"
```

Expected output (the `A:` line is elided at `[…]`; the real output prints it whole):

```
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... FAIL

  These two files must stay line-for-line identical after canonicalizing
  "dev-flow-worktree" -> "dev-flow". Every cross-cutting edit lands in both.

    A: plugins/dev-flow/skills/adversarial-review/SKILL.md
    B: plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md

  line count differs: A has 81, B has 80.
  first undeclared divergence at line 30:
    A: | **plan** | The rubric applied to the plan's approach *and* to any embedded code sketches. […]
    B:

  A line-for-line pair cannot differ in length — one side gained or lost a line that was
  not mirrored. Mirror it, then re-run.

  If the extra line is an *intentional* one-sided divergence, note that Check B's
  line-parallel schema cannot declare it — see the design doc (Decision 6) before
  contorting the prose to fit. The schema, not your edit, is what needs extending.

check-sync: 1 check failed
exit=1
```

The `B:` line really is empty: after the deletion, B's index 30 holds what was its line 31 — the blank row below that table entry — so the script prints `    B: ` with a trailing space. That is correct behavior, not a truncation.

Structural assertions — these, plus `exit=1`, are the pass/fail signal:

```bash
cd /Users/taylor/dev/claude-plugins
python3 scripts/check-sync.py | rtk proxy grep -c '^  line count differs: A has 81, B has 80.$'
python3 scripts/check-sync.py | rtk proxy grep -c '^  first undeclared divergence at line 30:$'
python3 scripts/check-sync.py | rtk proxy grep -c 'the first unmatched line'
```

Expected: `1`, `1`, `0`. **Line 30, not line 12** — if this prints `first undeclared divergence at line 12`, the scan is not consulting `usable` (Task 4 Step 4's `declared_at`).

Restore:

```bash
cd /Users/taylor/dev/claude-plugins
git restore plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
git status --porcelain
```

Expected: **nothing**.

**Experiment B — delete the *last* line (line 81) from B.** The extra line now sits past the end of the shorter file, so the common prefix holds no undeclared divergence and the end-of-file branch fires.

```bash
cd /Users/taylor/dev/claude-plugins
python3 -c "
import pathlib
p = pathlib.Path('plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md')
L = p.read_text(encoding='utf-8').split('\n')
del L[80]
p.write_text('\n'.join(L), encoding='utf-8')
"
python3 scripts/check-sync.py
echo "exit=$?"
```

Expected output:

```
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... FAIL

  These two files must stay line-for-line identical after canonicalizing
  "dev-flow-worktree" -> "dev-flow". Every cross-cutting edit lands in both.

    A: plugins/dev-flow/skills/adversarial-review/SKILL.md
    B: plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md

  line count differs: A has 81, B has 80.
  the files match through the end of the shorter (modulo declared exceptions);
  the first unmatched line is line 81 of A:
    A: File new issues with `gh issue create` when a GitHub remote exists; otherwise append them to `docs/superpowers/issues/BACKLOG.md`. […]

  A line-for-line pair cannot differ in length — one side gained or lost a line that was
  not mirrored. Mirror it, then re-run.

  If the extra line is an *intentional* one-sided divergence, note that Check B's
  line-parallel schema cannot declare it — see the design doc (Decision 6) before
  contorting the prose to fit. The schema, not your edit, is what needs extending.

check-sync: 1 check failed
exit=1
```

Structural assertions:

```bash
cd /Users/taylor/dev/claude-plugins
python3 scripts/check-sync.py | rtk proxy grep -c '^  line count differs: A has 81, B has 80.$'
python3 scripts/check-sync.py | rtk proxy grep -c '^  the first unmatched line is line 81 of A:$'
python3 scripts/check-sync.py | rtk proxy grep -c 'first undeclared divergence'
```

Expected: `1`, `1`, `0`.

Restore:

```bash
cd /Users/taylor/dev/claude-plugins
git restore plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
git status --porcelain
```

Expected: **nothing**.

> **What the pair of experiments proves:** both deletions produce the same counts (`81` vs `80`) but **different** reports — line 30 in one, the end-of-file branch naming line 81 in the other. A scan that ignored the declared exception would print "line 12" for both, byte-identically, and the end-of-file branch would be unreachable on this pair. That distinction is the whole point of `declared_at` being the single definition of "declared divergence" (Task 4 Step 4).

- [ ] **Step 5: Trailing newline — strip it from B only, then prove the comparison still continues (AC 6)**

```bash
cd /Users/taylor/dev/claude-plugins
python3 -c "
import pathlib
p = pathlib.Path('plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md')
t = p.read_text(encoding='utf-8')
p.write_text(t.rstrip('\n'), encoding='utf-8')
"
python3 scripts/check-sync.py
echo "exit=$?"
```

Expected output:

```
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... FAIL

  These two files must stay line-for-line identical after canonicalizing
  "dev-flow-worktree" -> "dev-flow". Every cross-cutting edit lands in both.

    A: plugins/dev-flow/skills/adversarial-review/SKILL.md
    B: plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md

  trailing newline differs: A ends with a newline, B does not.
  Mirror it, then re-run.

check-sync: 1 check failed
exit=1
```

Note that **no line-count failure appears** — `str.splitlines()` gives 81 lines either way, so the reported count still agrees with `wc -l`.

Now, **without restoring**, add Step 1's one-word edit to A on top. Design step 4 says comparison *continues* past a trailing-newline failure; this is the only step that proves it. A script that returned right after appending the newline item would pass every other step in this plan.

```bash
cd /Users/taylor/dev/claude-plugins
python3 -c "
import pathlib
p = pathlib.Path('plugins/dev-flow/skills/adversarial-review/SKILL.md')
L = p.read_text(encoding='utf-8').split('\n')
assert 'passes MUST run' in L[17]
L[17] = L[17].replace('passes MUST run', 'passes SHOULD run')
p.write_text('\n'.join(L), encoding='utf-8')
"
python3 scripts/check-sync.py
echo "exit=$?"
python3 scripts/check-sync.py | rtk proxy grep -c 'trailing newline differs'
python3 scripts/check-sync.py | rtk proxy grep -cE '^  line [0-9]+: undeclared divergence$'
```

Expected: `exit=1`, then `1` and `1` — **both** items in one run. The full output is the Step 1 block with the two `trailing newline differs` lines inserted between the header and `line 18: undeclared divergence`, in that order.

Restore both files:

```bash
cd /Users/taylor/dev/claude-plugins
git restore plugins/dev-flow/skills/adversarial-review/SKILL.md plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
git status --porcelain
```

Expected: **nothing**.

- [ ] **Step 6: Namespacing-only mirrored edit — still green (AC 4)**

Append a parenthetical to line 18 of each file, using each variant's own name. After canonicalization the two lines are identical, so this must **not** be flagged.

```bash
cd /Users/taylor/dev/claude-plugins
python3 -c "
import pathlib
for path, token in (
    ('plugins/dev-flow/skills/adversarial-review/SKILL.md', 'dev-flow'),
    ('plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md', 'dev-flow-worktree'),
):
    p = pathlib.Path(path)
    L = p.read_text(encoding='utf-8').split('\n')
    L[17] = L[17] + ' (' + token + ')'
    p.write_text('\n'.join(L), encoding='utf-8')
"
python3 scripts/check-sync.py
echo "exit=$?"
git restore plugins/dev-flow/skills/adversarial-review/SKILL.md plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
git status --porcelain
```

Expected:

```
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... OK (81 lines, 1 declared exception)
check-sync: all checks passed
exit=0
```

and `git status --porcelain` prints **nothing** after the restore.

- [ ] **Step 7: Stale exception — erase the declared divergence (AC 5)**

Copy A's line 12 over B's, making the two files fully identical after canonicalization. The exception no longer describes anything real and must be reported, not silently tolerated.

```bash
cd /Users/taylor/dev/claude-plugins
python3 -c "
import pathlib
a = pathlib.Path('plugins/dev-flow/skills/adversarial-review/SKILL.md').read_text(encoding='utf-8').split('\n')
p = pathlib.Path('plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md')
L = p.read_text(encoding='utf-8').split('\n')
L[11] = a[11]
p.write_text('\n'.join(L), encoding='utf-8')
"
python3 scripts/check-sync.py
echo "exit=$?"
```

Expected output (the two long `A:`/`B:` lines are elided at `[…]`; the real output prints them whole):

```
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... FAIL

  These two files must stay line-for-line identical after canonicalizing
  "dev-flow-worktree" -> "dev-flow". Every cross-cutting edit lands in both.

    A: plugins/dev-flow/skills/adversarial-review/SKILL.md
    B: plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md

  stale exception: the divergence it describes no longer appears in the files.
    why: The two pipelines pass working-dir differently: dev-flow omits it and the
         review defaults to the invoking checkout; dev-flow-worktree passes the
         worktree path explicitly.
    A: - When called by dev-flow, the review runs in-context on the feature branch […]
    B: - When called by dev-flow-worktree, `working-dir` is the pipeline worktree's absolute path […]
  Remove the entry from scripts/check-sync.py, or restore the divergence it describes.

check-sync: 1 check failed
exit=1
```

Structural assertions — these, plus `exit=1`, are the pass/fail signal:

```bash
cd /Users/taylor/dev/claude-plugins
python3 scripts/check-sync.py | rtk proxy grep -c '^  stale exception:'
python3 scripts/check-sync.py | rtk proxy grep -c 'malformed'
```

Expected: `1` and `0`. The second pins the stale/malformed distinction from the other side: this entry still describes a real difference between two raw lines, so it must **not** be reported as malformed.

Restore:

```bash
cd /Users/taylor/dev/claude-plugins
git restore plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
git status --porcelain
```

Expected: **nothing**.

- [ ] **Step 8: Malformed exception — an entry that can never match**

Design step 6 requires this to be reported as *malformed*, not as *stale*: telling an author staring at two visibly different raw lines that the divergence "no longer appears" would be a lie. Temporarily add a second exception whose two sides are equal after canonicalization.

```bash
cd /Users/taylor/dev/claude-plugins
python3 - <<'PY'
import pathlib
p = pathlib.Path("scripts/check-sync.py")
t = p.read_text(encoding="utf-8")
extra = '''            {
                "why": "Deliberately malformed probe entry.",
                "a": "- When called by dev-flow, the mode is passed explicitly.",
                "b": "- When called by dev-flow-worktree, the mode is passed explicitly.",
            },
'''
anchor = "        ],\n    },\n]\n"
assert t.count(anchor) == 1
p.write_text(t.replace(anchor, extra + anchor), encoding="utf-8")
PY
python3 scripts/check-sync.py
echo "exit=$?"
```

Expected output:

```
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... FAIL

  These two files must stay line-for-line identical after canonicalizing
  "dev-flow-worktree" -> "dev-flow". Every cross-cutting edit lands in both.

    A: plugins/dev-flow/skills/adversarial-review/SKILL.md
    B: plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md

  malformed exception: after canonicalization its two sides are identical,
  so it declares no divergence and can never match. The canonicalization
  already permits this difference; remove the entry from scripts/check-sync.py.
    why: Deliberately malformed probe entry.
    A: - When called by dev-flow, the mode is passed explicitly.
    B: - When called by dev-flow-worktree, the mode is passed explicitly.

check-sync: 1 check failed
exit=1
```

Structural assertions — these, plus `exit=1`, are the pass/fail signal:

```bash
cd /Users/taylor/dev/claude-plugins
python3 scripts/check-sync.py | rtk proxy grep -c '^  malformed exception:'
python3 scripts/check-sync.py | rtk proxy grep -c 'stale'
```

Expected: `1` and `0`. The word is **malformed**, not **stale** — and the `0` is the half that matters, since the wrong classification would still print a one-block failure with the same `why`/`A`/`B` lines.

Restore:

```bash
cd /Users/taylor/dev/claude-plugins
git restore scripts/check-sync.py
git status --porcelain
```

Expected: **nothing**.

- [ ] **Step 9: Final cleanliness gate for this task**

```bash
cd /Users/taylor/dev/claude-plugins
git status --porcelain
python3 scripts/check-sync.py
echo "exit=$?"
```

Expected: `git status --porcelain` prints **nothing**, and the check prints the two OK lines with `exit=0`.

- [ ] **Step 10: Commit only if a script fix was needed**

If Steps 1–9 all matched, there is nothing to commit and this task ends here. If an experiment revealed a defect in `scripts/check-sync.py` and you fixed it:

```bash
cd /Users/taylor/dev/claude-plugins
git add scripts/check-sync.py
git commit -m "check-sync: correct Check B output"
```

---

### Task 6: Add the PR workflow

**Files:**
- Create: `.github/workflows/check-sync.yml`
- Test: exact-content read-back (`.github/` does not exist yet; the repo has no workflows)

**Interfaces:**
- Consumes: `scripts/check-sync.py` from Tasks 2 and 4. The workflow is only meaningful once the script exists.
- Produces: nothing consumed by later tasks.

**Context — design Decision 5.** Both surfaces run the *identical* command, so nothing can pass locally and fail in CI. `pull_request` is the real enforcement point (CLAUDE.md: changes land via PR against `main`); `push: [main]` covers a direct push. **No `setup-python` step** — `ubuntu-latest` preinstalls `python3`, and adding one would be a second dependency for nothing. `permissions: contents: read` because the job only reads the tree. Do **not** add `claude plugin validate .` to this workflow (rejected in the design: it needs the Claude Code CLI on the runner, and its coverage misses every rule that has actually failed here). Do not add a `paths:` filter — the check is a tree invariant.

Making this a **required** status check is a repo setting, not a file: out of scope here, and not something to attempt.

- [ ] **Step 1: Create the workflow file**

Create `.github/workflows/check-sync.yml` (creating the two parent directories) with exactly this content:

```yaml
name: check-sync
on:
  pull_request:
  push:
    branches: [main]
permissions:
  contents: read
jobs:
  check-sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python3 scripts/check-sync.py
```

- [ ] **Step 2: Verify the file is byte-exact**

```bash
cd /Users/taylor/dev/claude-plugins
python3 - <<'PY'
import pathlib
expected = """name: check-sync
on:
  pull_request:
  push:
    branches: [main]
permissions:
  contents: read
jobs:
  check-sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python3 scripts/check-sync.py
"""
actual = pathlib.Path(".github/workflows/check-sync.yml").read_text(encoding="utf-8")
print("byte-exact:", actual == expected)
if actual != expected:
    print(repr(actual))
PY
```

Expected output:

```
byte-exact: True
```

- [ ] **Step 3: Confirm the run command matches the documented local command exactly**

```bash
cd /Users/taylor/dev/claude-plugins
rtk proxy grep -n 'python3 scripts/check-sync.py' .github/workflows/check-sync.yml
rtk proxy grep -c 'setup-python' .github/workflows/check-sync.yml
rtk proxy grep -c 'claude plugin validate' .github/workflows/check-sync.yml
```

Expected:

```
13:      - run: python3 scripts/check-sync.py
0
0
```

- [ ] **Step 4: Commit**

```bash
cd /Users/taylor/dev/claude-plugins
git add .github/workflows/check-sync.yml
git commit -m "ci: run check-sync on every pull request and on push to main"
```

---

### Task 7: Document the rule in CLAUDE.md

**Files:**
- Modify: `CLAUDE.md` (line 3's closing sentence, and the **Changing a plugin** section after the `New plugin:` bullet on line 8)
- Test: `grep` read-back

**Interfaces:**
- Consumes: the command `python3 scripts/check-sync.py` (Tasks 2, 4) and the fact that it runs on every PR (Task 6). Both must already be true — the bullet asserts them.
- Produces: nothing consumed by later tasks.

**Context — design Decision 7.** CLAUDE.md is loaded into every session in this repo, human or Claude, so it is where the rule belongs. The bullet teaches the rule; the PR check catches you regardless. The bullet must also state the honest limit: the pipeline `SKILL.md` pair and the two `README.md`s are too divergent to check mechanically and stay hand-mirrored.

The same edit repairs the file's **opening line**, which this branch falsifies: line 3 ends `Markdown and one Python script — no build, test, or lint tooling.`, and the branch adds a second Python script and the repo's first CI check. Left alone it would contradict the new bullet three lines below it, in the one file every session loads. Design Decision 7 and the Scope of edits row both authorize this; the replacement is deliberately **count-free**, since a hand-maintained count is the same drifting-fact class this whole change exists to kill.

**Line style:** every bullet in this file is a **single long unwrapped line**. Do not introduce manual line breaks inside the bullet.

- [ ] **Step 1: Insert the bullet**

Find this line in `CLAUDE.md` (line 8, the second bullet of `## Changing a plugin`):

```
- **New plugin: add an entry to `.claude-plugin/marketplace.json`** with `"source": "./plugins/<name>"` — the leading `./` is required. `description` is duplicated in both manifests; keep them in sync.
```

Insert the following as a **single line immediately after it**, before the `- Validate before committing:` bullet:

```
- **Some files are mirrored across `dev-flow` and `dev-flow-worktree` and must be edited in both.** `python3 scripts/check-sync.py` enforces what can be enforced mechanically — the `adversarial-review/SKILL.md` pair (line-for-line identical after `dev-flow-worktree` → `dev-flow`, minus declared exceptions) and the `description` duplicated between each `plugin.json` and `.claude-plugin/marketplace.json`. It runs on every PR. The pipeline `SKILL.md` pair and the two `README.md`s are too divergent to check mechanically — mirror those by hand.
```

Change nothing else in the file *except* what Step 2 specifies.

- [ ] **Step 2: Repair line 3's closing sentence**

Line 3 currently ends with this sentence:

```
Markdown and one Python script — no build, test, or lint tooling.
```

Replace **that sentence only** with:

```
Markdown plus a couple of Python scripts — no build, test, or lint tooling beyond `scripts/check-sync.py`.
```

Everything else on line 3 stays byte-identical, and line 3 remains a single line — so every line number asserted in Step 3 is unaffected. The reference deliberately omits the `python3 ` prefix, which keeps Step 3's `grep -c 'python3 scripts/check-sync.py' CLAUDE.md` at exactly `1` (the bullet, and only the bullet).

- [ ] **Step 3: Verify placement, the line-3 repair, and that the bullet is one line**

```bash
cd /Users/taylor/dev/claude-plugins
rtk proxy grep -n -e '- \*\*New plugin' -e '- \*\*Some files are mirrored' -e '- Validate before committing' CLAUDE.md
rtk proxy grep -c 'python3 scripts/check-sync.py' CLAUDE.md
rtk proxy grep -c 'one Python script' CLAUDE.md
```

Expected output — three consecutive line numbers in this order, exactly one mention of the command, and zero survivals of the stale phrase:

```
8:- **New plugin: add an entry to `.claude-plugin/marketplace.json`** with `"source": "./plugins/<name>"` — the leading `./` is required. `description` is duplicated in both manifests; keep them in sync.
9:- **Some files are mirrored across `dev-flow` and `dev-flow-worktree` and must be edited in both.** `python3 scripts/check-sync.py` enforces what can be enforced mechanically — the `adversarial-review/SKILL.md` pair (line-for-line identical after `dev-flow-worktree` → `dev-flow`, minus declared exceptions) and the `description` duplicated between each `plugin.json` and `.claude-plugin/marketplace.json`. It runs on every PR. The pipeline `SKILL.md` pair and the two `README.md`s are too divergent to check mechanically — mirror those by hand.
10:- Validate before committing: `claude plugin validate .` — checks the marketplace and every entry. The 8 missing-author warnings are expected.
1
0
```

The order 8 → 9 → 10 is the assertion: the new bullet sits between the marketplace bullet it extends and the validate bullet (a different tool). The trailing `0` is Step 2's assertion — the stale "one Python script" phrase is gone, and the line numbers prove the sentence replacement did not add or remove a line.

- [ ] **Step 4: Confirm the documented command is the one CI runs**

```bash
cd /Users/taylor/dev/claude-plugins
rtk proxy grep -oh 'python3 scripts/check-sync.py' CLAUDE.md .github/workflows/check-sync.yml
```

Expected: the identical string printed twice.

- [ ] **Step 5: Verify only CLAUDE.md changed, then commit**

```bash
cd /Users/taylor/dev/claude-plugins
git status --porcelain
```

Expected: exactly ` M CLAUDE.md`.

```bash
cd /Users/taylor/dev/claude-plugins
git add CLAUDE.md
git commit -m "CLAUDE.md: document the mirrored files and the check-sync command, and refresh the stale opening line"
```

---

### Task 8: Acceptance sweep — extensibility, scope, and a clean tree

**Files:**
- Temporarily modify: `scripts/check-sync.py` (restored)
- Temporarily create: `probe/one.md`, `probe/two.md` (deleted)
- Test: `python3 scripts/check-sync.py`, `claude plugin validate .`, `git diff`

**Interfaces:**
- Consumes: everything from Tasks 1–7.
- Produces: nothing. This is the final gate.

**Context:** Covers acceptance criteria 9, 12, and 13, plus a whole-branch scope check. AC 12 asks that enrolling a *new* line-parallel pair — or declaring a new same-index 1:1 divergence — be a single edit to `MIRROR_PAIRS`, with no new file, no new format, and no schema change. The probe below demonstrates exactly that; Step 2 then uses it for the missing-declared-path case, which cannot be staged on a tracked pair. The probe also exercises the line-count report's end-of-file branch on a pair with **no declared exceptions** — the complement to Task 5 Step 4's experiment B, which reaches the same branch on the enrolled pair *past* a declared exception.

> **Constraint reminder:** `probe/` is a throwaway directory at the repo root, deleted in Step 3. Nothing from this task is committed.

- [ ] **Step 1: Enroll a second pair with a single `MIRROR_PAIRS` edit**

```bash
cd /Users/taylor/dev/claude-plugins
mkdir -p probe
printf 'alpha\nbeta\ngamma\n' > probe/one.md
printf 'alpha\nbeta\n'         > probe/two.md
python3 - <<'PY'
import pathlib
p = pathlib.Path("scripts/check-sync.py")
t = p.read_text(encoding="utf-8")
entry = '''    {
        "name": "probe",
        "a": "probe/one.md",
        "b": "probe/two.md",
        "canonicalize": [],
        "exceptions": [],
    },
'''
anchor = "        ],\n    },\n]\n"
assert t.count(anchor) == 1
p.write_text(t.replace(anchor, "        ],\n    },\n" + entry + "]\n"), encoding="utf-8")
PY
python3 scripts/check-sync.py
echo "exit=$?"
```

Expected output — a third unit appears with no other change to the script:

```
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... OK (81 lines, 1 declared exception)
check-sync: mirror pair "probe" ... FAIL

  These two files must stay line-for-line identical after canonicalizing
  nothing. Every cross-cutting edit lands in both.

    A: probe/one.md
    B: probe/two.md

  line count differs: A has 3, B has 2.
  the files match through the end of the shorter (modulo declared exceptions);
  the first unmatched line is line 3 of A:
    A: gamma

  A line-for-line pair cannot differ in length — one side gained or lost a line that was
  not mirrored. Mirror it, then re-run.

  If the extra line is an *intentional* one-sided divergence, note that Check B's
  line-parallel schema cannot declare it — see the design doc (Decision 6) before
  contorting the prose to fit. The schema, not your edit, is what needs extending.

check-sync: 1 check failed
exit=1
```

- [ ] **Step 2: Confirm a missing declared path fails the pair that needed it, not the process**

```bash
cd /Users/taylor/dev/claude-plugins
rm probe/two.md
python3 scripts/check-sync.py
echo "exit=$?"
```

Expected: the first two units still report `OK`, and the `probe` unit reports a single line containing `cannot read B: [Errno 2] No such file or directory:` followed by the absolute path — **no Python traceback**, and `exit=1`. (The line is indented two spaces by `report()`, and it appears as its own block below the pair header.) Structural assertion:

```bash
cd /Users/taylor/dev/claude-plugins
python3 scripts/check-sync.py | rtk proxy grep -c 'cannot read B: \[Errno 2\] No such file or directory:'
```

Expected: `1`.

- [ ] **Step 3: Remove the probe and verify the tree is clean**

```bash
cd /Users/taylor/dev/claude-plugins
git restore scripts/check-sync.py
rm -rf probe
git status --porcelain
```

Expected: **nothing**. If `?? probe/` or ` M scripts/check-sync.py` prints, clean up before continuing.

- [ ] **Step 4: Full green run, offline, with no install step (AC 9)**

```bash
cd /Users/taylor/dev/claude-plugins
python3 scripts/check-sync.py
echo "exit=$?"
rtk proxy grep -nE '^(import|from) ' scripts/check-sync.py
```

Expected:

```
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... OK (81 lines, 1 declared exception)
check-sync: all checks passed
exit=0
19:import json
20:import sys
21:import textwrap
22:from pathlib import Path
```

All four are standard library. There is no `requirements.txt`, no `pyproject.toml`, no lockfile, and no `setup-python` step anywhere in the branch — confirm:

```bash
cd /Users/taylor/dev/claude-plugins
ls requirements.txt pyproject.toml setup.py 2>&1 | rtk proxy grep -c 'No such file'
```

Expected: `3`.

- [ ] **Step 5: Confirm no file under `plugins/` was touched (AC 13)**

```bash
cd /Users/taylor/dev/claude-plugins
git diff --name-only main...HEAD -- plugins/
git diff --name-only main...HEAD
```

Expected: the first command prints **nothing** — not one path under `plugins/`. The second lists exactly these paths (order may vary):

```
.claude-plugin/marketplace.json
.github/workflows/check-sync.yml
CLAUDE.md
docs/superpowers/plans/2026-07-26-gh-8-drift-check-plan.md
docs/superpowers/specs/2026-07-26-gh-8-drift-check-design.md
scripts/check-sync.py
```

The two `docs/superpowers/` entries are this plan and its design doc, and are expected. Anything under `plugins/` is a scope violation — investigate before proceeding.

- [ ] **Step 6: Confirm no version was bumped (design Decision 8)**

```bash
cd /Users/taylor/dev/claude-plugins
git diff --name-only main...HEAD -- '*plugin.json' | rtk proxy grep -c .
```

Expected: `0` — no `plugin.json` appears in the branch diff at all, so no `version` line can have changed. (`grep -c .` counts non-empty lines; `0` means the diff listed no such file.)

- [ ] **Step 7: Confirm the marketplace still validates**

```bash
cd /Users/taylor/dev/claude-plugins
claude plugin validate .
echo "exit=$?"
```

Expected: `exit=0`, with the eight expected missing-author warnings.

- [ ] **Step 8: Final cleanliness gate**

```bash
cd /Users/taylor/dev/claude-plugins
git status --porcelain
git log --oneline main..HEAD
```

Expected: `git status --porcelain` prints **nothing**, and the log shows this branch's commits (the design doc, plus the four to six commits from Tasks 1–7). Nothing is pushed, no PR is opened, no merge is performed — the pipeline owns those stages.

---

## Acceptance criteria → coverage

| # | Criterion (abridged) | Covered by |
|---|---|---|
| 1 | Editing a non-exception line of one `adversarial-review/SKILL.md` fails, naming the pair, both paths, the 1-based line number, and both lines | Task 5, Step 1 |
| 2 | Adding/removing a line in one and not the other fails with both line counts **and** the line number of the first *undeclared* divergence (never the declared line-12 one), or the first unmatched line at the end of the longer file when the prefix aligns | Task 5, Step 4 — experiment A (line 30) and experiment B (line 81, end-of-file branch) |
| 3 | Mirroring the same edit into both exits 0, with **no** edit to `scripts/check-sync.py` | Task 5, Step 2 |
| 4 | Changing only `dev-flow` ↔ `dev-flow-worktree` namespacing in a mirrored line still exits 0 | Task 5, Step 6 |
| 5 | Deleting the declared line-12 divergence from both files fails as a **stale exception** | Task 5, Step 7 |
| 6 | Stripping the trailing newline from one file fails, naming it; the line count still agrees with `wc -l` | Task 5, Step 5 |
| 7 | `.github/workflows/check-sync.yml` runs the check on every `pull_request` and on `push` to `main` | Task 6, Steps 1–3 |
| 8 | `python3 scripts/check-sync.py` is documented in CLAUDE.md and is the identical command CI runs | Task 7, Steps 1–4 |
| 9 | Needs nothing beyond `python3` — no install step, no lockfile, no `setup-python`, no network | Task 2 Step 4; Task 6 Step 3; Task 8 Step 4 |
| 10 | Fails on the base tree's `dev-flow-worktree` description; passes after the `marketplace.json` fix | Task 1 (the fix) + Task 3, Steps 1–2 (both directions) |
| 11 | An unregistered `plugins/<name>/`, or a `source` missing the leading `./`, fails the check | Task 3, Steps 3–5 |
| 12 | Enrolling a future line-parallel pair is a single edit to `MIRROR_PAIRS` — no new file, no new format, no schema change | Task 8, Step 1 |
| 13 | No file under `plugins/` is modified, so no `plugin.json` `version` bump is required | Task 1 (marketplace-side repair); Task 8, Steps 5–6 |

Design **Smoke test** steps 1–8 map to: 1 → Task 4 Step 6; 2 → Task 3 Steps 1–2; 3 → Task 5 Steps 1–3; 4 → Task 5 Step 4; 5 → Task 5 Step 5; 6 → Task 5 Step 6; 7 → Task 5 Step 7; 8 → Task 3 Steps 4–5. Smoke step 9 ("open the PR and confirm the `check-sync` job appears and is green") is a **pipeline** action, not a task in this plan — the plan stops before pushing.

---

## Open Questions

None — both questions raised during planning were resolved in review (see Task 4 Step 4 and Task 7 Step 2).
