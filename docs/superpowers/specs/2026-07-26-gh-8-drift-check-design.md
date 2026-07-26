---
dev-flow:
  slug: gh-8-drift-check
  stops: [pre-merge]
---

# Mechanical drift check for the duplicated plugin prose

Closes #8.

## Problem

`dev-flow` and `dev-flow-worktree` are maintained as separate plugins (split in
a104d2b), and unification is precluded by the distribution model — each installs alone
into a version-keyed cache directory containing only its own tree, so no runtime path to
a cross-plugin shared file exists. That conclusion is settled in #8 and is not
re-litigated here.

What follows from it is a maintenance obligation: every cross-cutting change lands
twice, by hand. Today the only thing enforcing that is memory. #6 landed in six files
across both plugins on exactly that basis.

The same defect class already exists a second time in this repo, and has already
failed. CLAUDE.md says the plugin `description` is "duplicated in both manifests; keep
them in sync." It is out of sync **right now**:

```
plugins/dev-flow-worktree/.claude-plugin/plugin.json
  "... merge pipeline, isolated in a dedicated git worktree, with adversarial ..."
.claude-plugin/marketplace.json
  "... merge pipeline isolated in a dedicated git worktree, with adversarial ..."
```

`claude plugin validate .` — the repo's only existing validation — exits **0** on that
tree. Verified. So the repo already contains a silently-realized instance of the exact
regression #8 was filed to prevent, and the existing tooling does not see it.

## Goals

1. Editing one `adversarial-review/SKILL.md` without the other fails loudly.
2. The check is a tree invariant: a pure function of the working tree, runnable at any
   time, with no base revision and no network.
3. It runs automatically at the point where changes actually land (a PR against `main`),
   *and* is a documented one-command local check — the same command in both places.
4. Adding the next duplicated pair, or *declaring* the next intentional divergence, is
   one small edit in one file.
5. Zero new toolchain: no package manager, no lockfile, no new binary to install.

### Non-goals

- **Unifying the two plugins.** Settled in #8.
- **Proving the mirrored change was *correct*.** No mechanical check can decide whether a
  worktree port is a faithful adaptation. This checks identity where identity is the
  intended relation, and nothing more.
- **Checking the pipeline `SKILL.md` pair or the two `README.md`s.** Evaluated in
  Decision 6 and deliberately left to hand-mirroring, with a stated revisit trigger.
- **Broad repo CI** (link checks, spell checks, `claude plugin validate .`). See
  Rejected alternatives.

## What the duplicated files actually look like (measured)

Every number below was measured on the tree at this design's base commit. "Canonicalized"
means after substituting the token `dev-flow-worktree` → `dev-flow` in both files, which
is the deliberate namespacing #8 names.

| Duplicated pair | Size | Raw divergence | Canonicalized divergence |
|---|---|---|---|
| `adversarial-review/SKILL.md` | 81 / 81 lines | 4 lines (3, 11, 12, 69) | **1 line (12)** |
| pipeline `SKILL.md` | 277 / 271 lines | ~130 lines | 26 hunks, 44 − / 38 + |
| `README.md` | 122 / 126 lines | — | 6 hunks, 32 − / 36 + |
| `description` × 8 plugins | — | — | **1 pair already drifted** |

The pipeline row is self-checking: 277 − 44 + 38 = 271, the measured length of the
worktree file.

**#8's premise for item 1 is wrong, and it changes the design.** The
`adversarial-review` pair is *not* byte-identical today. Three of its four differing
lines are pure `dev-flow` → `dev-flow-worktree` substitution. The fourth, line 12, is a
genuine semantic divergence:

```
A: - When called by dev-flow, the review runs in-context on the feature branch checked
     out in the invoking checkout, so `working-dir` is omitted — it defaults to that
     checkout (see dev-flow's branch-entry rule). dev-flow uses no worktree.
B: - When called by dev-flow-worktree, `working-dir` is the pipeline worktree's absolute
     path — the orchestrator passes it explicitly and invokes the review in-context (see
     dev-flow-worktree's worktree-entry rule).
```

(Shown wrapped; each is a single line in the file.) These state different caller
contracts, and the skill is read by a model that must decide whether to expect a
`working-dir` argument. So a literal `cmp` would fail on day one, and the fix for that
failure is not to edit the files.

Neither `adversarial-review/SKILL.md` has been touched since a104d2b created the pair —
so the drift risk is live but not yet realized, and enrolling the pair costs no cleanup.

**Divergence shape matters, not just size.** Of the pipeline pair's 26 canonicalized
hunks, 19 replace an equal number of lines on each side, 5 replace unequal counts
(11:7, 3:1, 1:3, 2:1, 2:3), and 2 are strictly one-sided — a block present in one file
with no counterpart at all. Those 7 non-parallel hunks are exactly why the two files
differ in length. This is the fact that bounds Check B's scope (Decision 3) and drives
Decision 6.

## Decisions

### 1. One checker: `scripts/check-sync.py`, Python 3 stdlib, zero flags

A single script at the repo root — **not** under `plugins/`, so it ships to nobody and
touches no plugin behavior (see Decision 8).

**Python 3, stdlib only.** This is not a new language for this repo: it already ships
`plugins/youtube-upload/scripts/yt-resumable-upload.py`. It needs no package manager, no
lockfile, no venv, and no `requirements.txt` — `json` is in the stdlib. `python3` is
present on stock macOS and preinstalled on `ubuntu-latest`. The manifest check (Check A,
Decision 2) needs correct JSON parsing, which rules out `sed`/`grep` scraping.

**Zero flags, and deliberately no `--bless` / `--fix` / `--update` mode.** An
auto-regenerate escape hatch is the single fastest way to turn a check into a ceremony:
the first time it fires, the contributor learns that the response to a red check is to
re-run it with `--bless`. Every exception in this design is declared by hand, in the
script, and lands in a reviewed diff. That cost is affordable *because* Decision 6 keeps
the exception count at one.

**Two checks, one command.** They fail independently and both run every time — a run
reports every problem in the tree, not just the first.

### 2. Check A — manifest description sync (derived, no configuration)

Enforces the two rules CLAUDE.md already states but nothing enforces. Entirely derived
from the filesystem — there is nothing to declare, and a new plugin is covered the day
its directory exists.

For every `plugins/<dir>/.claude-plugin/plugin.json`:

1. Its `name` equals `<dir>`.
2. `.claude-plugin/marketplace.json` has exactly one entry with that `name`.
3. That entry's `source` is exactly `./plugins/<dir>` — with the leading `./`, which
   CLAUDE.md flags as required.
4. That entry's `description` is byte-equal to the plugin.json `description`.

And symmetrically: every marketplace entry has a matching `plugins/<name>/` directory.

Rule 2's reverse direction matters more than it looks. `claude plugin validate .`
iterates the *marketplace's* entry list, so a plugin directory that was never registered
is invisible to it — it is not reported as an error, it is simply never visited. Check A
sees it.

**Check A is in scope on demonstrated demand, not on "while we're here."** Three of its
four rule families have already failed in real commits in this repo:

- **Rule 4 (`description`)** — the live drift, and it was *born in a104d2b*: one reviewed
  PR wrote two different descriptions in a single commit. Memory-sync failed on day one
  of the duplication, under review.
- **Rule 2, reverse direction** — `b192e3f` "Add missing plugins to marketplace.json":
  three plugin directories sat unregistered. This is precisely the case
  `claude plugin validate .` is blind to (verified: exit 0).
- **Rule 3 (`source` format)** — `60c799c` "Fix marketplace.json source paths to use
  ./relative format": every source was in the wrong format at once.

So this is not widening the lens on speculation — each family has 2+ instances or a live
one. It is also the *derived* half of the checker: a new plugin is covered with zero
enrollment, whereas Check B must be told about each pair by hand. A script that only ever
checked one hand-declared pair would be the per-instance fix that the next person must
remember to extend. Cost is about ten lines.

Check A does exceed #8's literal acceptance list, which names only the SKILL.md pair. It
earns inclusion on the history above and because it is the same defect — two copies of one
fact, kept in sync by memory — at the same boundary. Landing this change also fixes the
live drift (see Scope of edits), because otherwise the check is red on arrival.

### 3. Check B — declared mirror pairs, line-for-line modulo canonicalization

**Scope, stated up front.** Check B enrolls only pairs intended to be **line-for-line
parallel**, and its exception schema deliberately expresses only same-index,
one-line-for-one-line divergence. Measured, that fits exactly one of the three duplicated
pairs in this repo: the `adversarial-review` pair (81/81 lines, one 1:1 divergence). The
pipeline pair has 7 non-parallel hunks and the README pair re-wraps to a different line
count; neither is enrollable under this schema. Decision 6 addresses both, and the
line-count failure message (Decision 4) tells a maintainer who hits this wall that the
schema — not their edit — is what would need extending.

A pair is declared in a table at the top of the script:

```python
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

A Python list literal, **not** a separate YAML/JSON manifest: it is already declarative,
the script is its only consumer, and a second file would be a second format and a second
place to look. Extending it is one entry.

**Algorithm.**

1. Read both files as text with explicit `encoding="utf-8"` — never the locale default;
   these files contain em dashes, and a C/POSIX-locale run would otherwise raise
   `UnicodeDecodeError` as a stderr traceback. Use default universal-newlines mode
   (line-ending style is git's concern, not this check's). Any `OSError` — missing,
   unreadable, or a directory — fails that pair, naming the path and the OS error. Check
   A's manifest reads use the same explicit encoding.
2. Canonicalize both by applying every substitution to **both** sides — symmetric, so the
   rule stays correct if a cross-reference to the other variant ever appears in either
   file. The script sorts substitutions by descending source-token length, so a token
   containing another as a substring is always replaced first; declaration order in the
   table carries no meaning. The same canonicalization is applied to each declared
   exception's `a`/`b` strings before matching in step 5.
3. If the canonicalized texts are byte-equal, skip the line-by-line comparison and go
   straight to step 6 — with the files fully identical, every declared exception is by
   definition stale.
4. If exactly one of the two canonicalized texts ends in a newline, the pair fails,
   naming the file that lacks it; comparison still continues, since the remaining steps
   are insensitive to it. Split both into lines with `str.splitlines()`, so a final
   newline does not produce a phantom empty last line and the reported count agrees with
   `wc -l`. **If the line counts differ, the pair fails** with both counts *and* the
   1-based index of the first position where the canonicalized lines differ — a scan over
   the common prefix — plus both raw lines there; if the common prefix is entirely equal
   (one file is a strict prefix of the other), say so and name the first extra line
   instead. Steps 5–6 are then skipped for that pair: past a one-sided insertion every
   later index is offset, so positional comparison is meaningless.
5. Compare index by index. At each index where the canonicalized lines differ, look for a
   declared exception whose canonicalized `a`/`b` equal the canonicalized `a`/`b` lines at
   that index. Found → allowed, and that exception is marked used. Not found → report
   the 1-based line number and both raw lines.
   Exceptions match on **content, not position**, so mirroring a change that shifts the
   divergent bullet up or down does not require touching the script.
6. Any exception never used is a failure: the divergence it describes no longer exists,
   so the entry is stale and is now silently permitting a divergence nobody reviewed. An
   exception whose `a` and `b` are equal *after canonicalization* declares no divergence
   and can never match; report it as **malformed** — "the canonicalization already permits
   this difference; remove the entry" — rather than letting it surface as stale, which
   would tell an author staring at two visibly different raw lines that the divergence
   "no longer appears."

Positional line-for-line comparison, rather than a diff, is the right primitive for a pair
declared line-parallel: the invariant we actually want is *"these files are parallel line
for line, except where we said otherwise."* It needs no baseline artifact and produces a
line number instead of a hunk. Its cost is the scope limit stated above, which is why that
limit is documented rather than discovered.

### 4. Exact failure and success output

Everything goes to stdout. Exit **0** iff every check passed, **1** otherwise — a missing
declared path or an unparseable manifest is reported as a failure of the check that
needed it, not as a separate exit code.

Reported lines are printed **whole** — no truncation. The trailing `...` in the examples
below elides long lines for this document's width only.

The final summary counts **failing units** — the manifest check plus each mirror pair,
one per `...` progress line.

Success, on a repaired tree:

```
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... OK (81 lines, 1 declared exception)
check-sync: all checks passed
```

Check A failure — this is the literal output on the tree as of this design:

```
check-sync: manifest descriptions ... FAIL

  dev-flow-worktree: description differs between the two manifests.
  CLAUDE.md requires them to be identical.

    plugins/dev-flow-worktree/.claude-plugin/plugin.json
      Autonomous design -> plan -> execute -> PR -> merge pipeline, isolated in a dedicated git worktree, with adversarial review at each artifact boundary
    .claude-plugin/marketplace.json
      Autonomous design -> plan -> execute -> PR -> merge pipeline isolated in a dedicated git worktree, with adversarial review at each artifact boundary

check-sync: 1 check failed
```

Check B failure, undeclared divergence (illustrative — line 18 edited on one side only):

```
check-sync: mirror pair "adversarial-review" ... FAIL

  These two files must stay line-for-line identical after canonicalizing
  "dev-flow-worktree" -> "dev-flow". Every cross-cutting edit lands in both.

    A: plugins/dev-flow/skills/adversarial-review/SKILL.md
    B: plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md

  line 18: undeclared divergence
    A: **Review integrity (never inline).** The seed and resolver passes MUST run as ...
    B: **Review integrity (never inline).** The seed and resolver passes SHOULD run as ...

  Fix: mirror the edit into both files. If the divergence is genuinely variant-specific,
  add it to MIRROR_PAIRS["adversarial-review"]["exceptions"] in scripts/check-sync.py
  with a one-line reason.

check-sync: 1 check failed
```

Check B failure, line-count mismatch:

```
  line count differs: A has 81, B has 82.
  first divergence at line 44:
    A: - **Baseline:** branch entry has already ensured setup (deps installed); run ...
    B: - **Baseline:** the worktree's own setup runs first; run the baseline suite ...

  A line-for-line pair cannot differ in length — one side gained or lost a line that was
  not mirrored. Mirror it, then re-run.

  If the extra line is an *intentional* one-sided divergence, note that Check B's
  line-parallel schema cannot declare it — see the design doc (Decision 6) before
  contorting the prose to fit. The schema, not your edit, is what needs extending.
```

Check B failure, trailing newline:

```
  trailing newline differs: A ends with a newline, B does not.
  Mirror it, then re-run.
```

Check B failure, stale exception:

```
  stale exception: the divergence it describes no longer appears in the files.
    why: The two pipelines pass working-dir differently: dev-flow omits it and the
         review defaults to the invoking checkout; dev-flow-worktree passes the
         worktree path explicitly.
    A: - When called by dev-flow, the review runs in-context on the feature branch ...
    B: - When called by dev-flow-worktree, `working-dir` is the pipeline worktree's ...
  Remove the entry from scripts/check-sync.py, or restore the divergence it describes.
```

Every failure names the invariant, the exact location, and the two ways out. A check that
prints a raw diff and stops makes the reader re-derive the rule.

### 5. Where it runs: PR CI **and** the same documented local command

Both. Not either.

A local-only check reproduces the exact failure mode #8 is about — a human forgetting to
run something — one level up. And CI-only means you cannot verify before pushing. Both
surfaces run the identical command, so there is nothing that can pass locally and fail in
CI.

`.github/workflows/check-sync.yml` — the repo's first workflow:

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

`pull_request` is the real enforcement point (CLAUDE.md: changes land via PR against
`main`); `push: [main]` covers a direct push. No `setup-python` step — `ubuntu-latest`
preinstalls `python3`, and adding one would be a second dependency for nothing.
`permissions: contents: read` because the job only reads the tree.

This is new infrastructure for a repo with none, which the issue anticipates ("whatever
CI this repo adopts"). The cost is bounded deliberately: one workflow, one job, one step,
one dependency-free command.

Making the check a **required** status check is a repo setting, not a file in this diff —
recommended, but out of scope here. An advisory red check is still visibly red on the PR,
which is the loud failure the issue asks for.

### 6. Item 2 — the pipeline `SKILL.md` pair (and the `README.md` pair)

#8 asks for an evaluation of normalized-diff-with-allowlist versus documenting
hand-mirroring as accepted. **Documented as accepted.** The evidence:

- **Size.** After canonicalization the pipeline pair still diverges across **26 hunks**,
  44 removed and 38 added lines. An exception list of that size is not a declaration, it
  is a copy of the diff.
- **Shape.** 7 of those 26 hunks are not line-parallel (2 strictly one-sided, 5 replacing
  unequal counts). Check B's schema cannot express them at all, and its line-count guard
  hard-fails before exceptions are ever consulted. So the pair is not merely expensive to
  enroll — the shipped mechanism cannot check it.
- **Churn.** Of the two post-split changes, **65bbe63 edited three divergent regions** —
  a hand-maintained exception list would have needed simultaneous updates. **39d5ea9 did
  not**: it removed the same section from both files, byte-mirrored modulo the namespace
  token, leaving the divergent hunk set untouched (22 hunks before and after). So a
  content-keyed list would have churned on 1 of 2 changes, not 2 of 2. A committed
  *positional* baseline would have been regenerated by both, since 39d5ea9's ten-line
  symmetric removal shifts every hunk header below it — which is itself the decisive
  argument against that format: it churns even on perfectly mirrored edits.
- **Reflex.** With one exception, adding another is an event a reviewer reads; with 26,
  updating the 27th is rote. A rote exception edit is the same reflex as a re-blessed
  baseline, and it would then be applied to the `adversarial-review` pair, where the check
  does work. That would poison the one asset this change creates. This argument does not
  depend on the churn count, and after the correction above it is the strongest leg.
- The `README.md` pair is the same bucket, plus an extra reason: it is hard-wrapped at
  ~72 columns, and `dev-flow-worktree` is eight characters longer than `dev-flow`, so the
  same sentence legitimately re-wraps differently in the two files. Canonicalization
  cannot see through that; a paragraph-joining normalizer could, but now the checker is
  reimplementing prose reflow to make a report it will be told to ignore anyway.

**What would change the answer**, concretely:

- A restructuring that restores line-for-line parallelism — gathering the variant-specific
  prose into contiguous, individually nameable blocks of equal length on both sides; or
- three consecutive changes leaving the canonicalized divergence unchanged, evidence that
  the divergence has stabilized enough for an exception list to stay quiet.

The `MIRROR_PAIRS` table survives enrollment either way, but the comparison does not. The
pair becomes enrollable **as-is** only under the first trigger. Otherwise enrollment
requires generalizing Check B from positional lines to content-matched *hunk* exceptions
(difflib opcodes; `a`/`b` sides of differing lengths, possibly empty) — a contained
extension of this same script, deliberately not built now: the one enrolled pair needs
none of it, and hunk matching brings alignment subtleties (hunk boundaries around repeated
blank lines, an edit adjacent to a declared divergence merging into its hunk) not worth
buying ahead of a single concrete instance. So "accepted for now" is not a dead end, but
it is not a free one-line enrollment either, and the doc should not pretend otherwise.

Until then, the obligation is written down where a contributor will see it (Decision 7),
which is the honest thing to say about a rule only humans can enforce.

### 7. Discoverability: CLAUDE.md, plus the PR check itself

CLAUDE.md is loaded into every session in this repo, human or Claude, so it is where the
rule belongs. One bullet in **Changing a plugin**:

> - **Some files are mirrored across `dev-flow` and `dev-flow-worktree` and must be
>   edited in both.** `python3 scripts/check-sync.py` enforces what can be enforced
>   mechanically — the `adversarial-review/SKILL.md` pair (line-for-line identical after
>   `dev-flow-worktree` → `dev-flow`, minus declared exceptions) and the `description`
>   duplicated between each `plugin.json` and `.claude-plugin/marketplace.json`. It runs
>   on every PR. The pipeline `SKILL.md` pair and the two `README.md`s are too divergent
>   to check mechanically — mirror those by hand.

The second surface is the PR check itself, which appears on every PR whether or not
anyone read CLAUDE.md. The first teaches the rule; the second catches you regardless.

### 8. No plugin version bump, and no new marketplace entry

This change touches **no file under `plugins/`**. It adds `scripts/check-sync.py` and
`.github/workflows/check-sync.yml`, edits `CLAUDE.md`, and edits
`.claude-plugin/marketplace.json`. It is repo tooling; no plugin's behavior changes, so
**no `plugin.json` `version` bump is required** and none should be demanded in review.

The description drift is repaired on the **marketplace** side (add the missing comma to
`.claude-plugin/marketplace.json`) rather than the plugin side, for three reasons: Check
A's rule 4 already treats `plugin.json` as the source of truth and the marketplace entry
as its mirror, so repairing the mirror is the consistent direction; the plugin.json text
is the better of the two (paired appositive commas, matching the `dev-flow` sibling's
structure); and editing `plugins/dev-flow-worktree/.claude-plugin/plugin.json` would put a
file under `plugins/` in the diff and reopen the version-bump question for a comma — a
bump that would push a no-op reinstall through the version-keyed cache.

No plugin is added, so no new `marketplace.json` *entry* is needed — only the correction
to the existing one.

## Scope of edits

| File | Change |
|---|---|
| `scripts/check-sync.py` | **New.** Python 3 stdlib. Check A (derived manifest sync) + Check B (`MIRROR_PAIRS`, one entry, one exception). Exit 0/1. |
| `.github/workflows/check-sync.yml` | **New.** The repo's first workflow; `pull_request` + `push: [main]`; one step. |
| `.claude-plugin/marketplace.json` | Fix the `dev-flow-worktree` description to match its `plugin.json` (missing comma after "pipeline"). Required — otherwise the check is red on arrival. |
| `CLAUDE.md` | One bullet in **Changing a plugin** (Decision 7). |

No file under `plugins/` is touched. No version bump (Decision 8).

## Known consequences (accepted)

- **The largest duplication in the repo stays unchecked.** The pipeline `SKILL.md` pair
  (277/271 lines) and the two `README.md`s remain hand-mirrored. Decision 6 argues why,
  and names what would change it.
- **Check B cannot declare a one-sided or unequal-length intentional divergence.** Its
  schema is same-index, one-line-for-one-line. If such a divergence arises in an enrolled
  pair, the schema must be generalized first (Decision 6 names how), and the line-count
  failure message says so. Deliberate: the alternative default is prose mangled to stay
  line-parallel in order to satisfy a checker.
- **An exception matches by content wherever it occurs.** If the same divergent line-pair
  ever appears at a second index, it is permitted there too under the same `why`.
  Accepted: a pair of full-line sentences recurring in lockstep is deliberate duplication,
  not coincidence, and position-matching would instead break the exception on every
  reflow above it — the exact churn content-matching was chosen to avoid.
- **The check proves identity, not correctness.** It cannot tell whether a mirrored edit
  was the right adaptation for the worktree variant — #6 called that port "a mechanism
  extension, not a rename." For the `adversarial-review` pair this limit is not binding,
  because identity *is* the intended relation there.
- **A new intentional divergence costs three edits** — both files plus the exception
  entry. Deliberate: it makes new divergence in a pair declared identical a reviewed act
  rather than a silent one.
- **The exception's `why` string can go stale in spirit** while still matching by content.
  Staleness of *content* is caught (Decision 3, step 6); staleness of *reasoning* is not.
  Accepted — with one exception, a reviewer reads it.
- **A fork without Actions enabled gets no enforcement** until the PR is opened against
  this repo, which is where changes land anyway.

## Rejected alternatives

**Byte-identical assertion, exactly as #8 item 1 specifies it.** Measured false: the pair
differs at lines 3, 11, 12, and 69. A `cmp` would be red on day one for reasons nobody
should fix.

**Erase the line-12 divergence so byte-identity becomes true.** The two sentences state
different caller contracts for `working-dir`, and this file is read by a model that must
decide whether to expect that argument. Merging them into a variant-agnostic sentence
degrades operational precision to satisfy a checker — backwards — and it is a behavior
change to both plugins, so a tooling-only change would suddenly need two version bumps.

**Normalized diff against a committed baseline, with a `--bless` regenerate mode, applied
to the pipeline pair.** 26 hunks over 44/38 lines. A *positional* baseline would have been
regenerated by both post-split changes — including 39d5ea9, which mirrored its edit
perfectly and merely shifted every hunk header below it. A format that churns on a
correctly mirrored change is worse than no check, and Decision 6 gives the rest of the
argument: the re-bless reflex it trains would then be applied to the pair where the check
works.

**A co-change check** — fail if one file of a pair changed in the diff and the other did
not. Zero maintenance and it targets exactly the stated failure mode, but: it is not a
tree invariant (it needs a base revision, so it cannot be the same command locally and in
CI), it false-positives on legitimately one-sided changes such as a worktree-only fix,
and the escape hatch it then needs — a commit trailer or PR label — is one more thing to
remember, which is the disease.

**A heading-skeleton invariant for the pipeline pair** — require both files to carry the
same section headings, in the same order, after canonicalization. Measured true today
(14 headings, identical), needs no baseline, and would catch the severe structural miss:
a section added to one variant and not the other. Rejected as speculative on this repo's
evidence — it would have fired on neither post-split change, for two different reasons.
39d5ea9 removed an entire section, heading included (15 → 14 headings on **both** sides),
but symmetrically, so an A-versus-B skeleton comparison stays equal; 65bbe63 edited only
paragraph bodies. The one thing the invariant would catch — an *asymmetric* structural
change — has zero instances in this repo's history. It buys a third check concept against
no demonstrated demand.

**A shell one-liner (`cmp` / `diff`) or a bash + `jq` script.** A one-liner cannot express
canonicalization, exceptions, or an actionable message, and it cannot parse JSON at all.
`jq` does ship with recent macOS (`/usr/bin/jq`), so availability is not the objection —
but it covers only the JSON half, and Check B's canonicalization, content-matched
exceptions, and staleness tracking would still be a nontrivial shell program. The repo
already contains Python.

**A separate `sync-pairs.yaml` / `.json` manifest.** A second format and a second place to
look, with exactly one consumer. The Python table in Decision 3 is already declarative.

**A `justfile` recipe (`just check-sync`).** The repo has no justfile and no `just`; adding
a task runner to alias one command is a new tool dependency for zero abstraction.

**Adding `claude plugin validate .` to the workflow.** It needs the Claude Code CLI
installed on the runner — a heavyweight, independently-versioned external dependency that
can turn the repo's first CI red for reasons unrelated to the repo. Its coverage is also
close to complementary rather than overlapping: verified case by case, it exits **1** on a
malformed `source` and on a duplicate entry, but exits **0** on description drift, on an
unregistered `plugins/<dir>/`, and on a marketplace entry whose `name` matches no plugin —
i.e. it catches the Check A rule with no live failure and misses all three that have
failed here. It is already documented as a pre-commit step in CLAUDE.md, and it stays
there. Worth revisiting only once this workflow has proven stable.

**Unifying the two plugins.** Settled in #8 with evidence; out of scope.

## Assumptions

Each is a defensible default, stated so a reviewer can overturn it cheaply.

1. **`python3` (3.9+, stdlib only) is available** on a contributor's machine and on
   `ubuntu-latest`. Verified locally (3.14.5); preinstalled on GitHub runners; the repo
   already ships a Python script.
2. **GitHub Actions may be enabled for this repo.** #8's acceptance criterion says
   "whatever CI this repo adopts," which reads as permission to adopt one. If Actions must
   stay off, the local command and the CLAUDE.md bullet still satisfy the criterion's
   second half — drop the workflow file and delete the bullet's "It runs on every PR"
   sentence; nothing else changes.
3. **Line-for-line parallelism is an enrollment *requirement* of Check B**, not merely an
   observed property of the enrolled pair. The `adversarial-review` pair satisfies it
   (81/81 lines, one canonicalized divergence, neither file touched since the commit that
   created the pair). A pair that does not satisfy it is not enrollable — Decision 6.
4. **`dev-flow-worktree` → `dev-flow` is the whole of the deliberate namespacing** for
   this pair. Verified: substituting that one token reduces four divergent lines to one.
   Canonicalization is declared per pair rather than inferred from plugin names, so a
   future pair with a different relationship declares its own.
5. **Repairing the description drift on the marketplace side is right.** Decision 8.
6. **A non-required status check is sufficient** for "fails loudly." Promoting it to
   required is a repo setting a maintainer can flip later without touching this design.

## Acceptance criteria

Traceable to #8's two acceptance bullets.

*From "Editing one `adversarial-review/SKILL.md` without the other fails the check":*

1. Editing any non-exception line of one `adversarial-review/SKILL.md` and not the other
   makes `python3 scripts/check-sync.py` exit non-zero, naming the pair, both paths, the
   1-based line number, and both lines.
2. Adding or removing a line in one and not the other fails with both line counts **and
   the 1-based line number of the first divergence**.
3. Mirroring the same edit into both files exits 0, with **no** edit to
   `scripts/check-sync.py` — the check is not a tax on doing it correctly.
4. Changing only the `dev-flow` ↔ `dev-flow-worktree` namespacing in a mirrored line still
   exits 0 — canonicalization does not produce false positives on deliberate namespacing.
5. Deleting the declared line-12 divergence from both files (making them fully identical)
   fails as a **stale exception**, not silently.
6. Stripping the trailing newline from one file of the pair fails, naming the file that
   lacks it; the reported line count still agrees with `wc -l`.

*From "The check runs in whatever CI this repo adopts, or is a documented one-command
local check" — this design does both:*

7. `.github/workflows/check-sync.yml` runs the check on every `pull_request` and on
   `push` to `main`, and its failure is visible on the PR.
8. `python3 scripts/check-sync.py` is documented in CLAUDE.md and is the identical command
   CI runs.
9. The check needs nothing beyond `python3` — no install step, no lockfile, no
   `setup-python`, no network.

*Additional criteria this design takes on:*

10. On the tree at this design's base commit, the check **fails** on the
    `dev-flow-worktree` description; after the `marketplace.json` fix it **passes**. The
    check demonstrably catches a real, pre-existing defect on day one.
11. A `plugins/<name>/` directory with no `marketplace.json` entry, or an entry whose
    `source` lacks the leading `./`, fails the check.
12. Enrolling a future *line-parallel* pair, or declaring a new same-index 1:1 divergence,
    is a single edit to `MIRROR_PAIRS` — no new file, no new format, no schema change.
13. No file under `plugins/` is modified, so no `plugin.json` `version` bump is required.

## Open questions

None.

Two things a reader might expect to be open are decided, not deferred: whether the
workflow should be a *required* status check (Decision 5 — recommended, but a repo
setting rather than a file, so outside this diff), and whether it should also run
`claude plugin validate .` (Rejected alternatives — no, with case-by-case evidence that
its coverage is complementary and misses every rule that has actually failed here).

## Smoke test

Run from a clean checkout of the branch.

1. `python3 scripts/check-sync.py` → exits 0, prints both OK lines, reports `81 lines`.
2. Revert the `marketplace.json` comma fix → exits 1 with the Check A output in
   Decision 4. Restore it.
3. Change one word in `plugins/dev-flow/skills/adversarial-review/SKILL.md` (say line 18,
   not line 12) → exits 1, naming that line number. Mirror the same change into the
   sibling → exits 0 with the script untouched. Revert both.
4. Delete one line from one of the pair → exits 1 with `81` vs `80` **and a first-
   divergence line number**. Restore.
5. Strip the trailing newline from one file of the pair → exits 1 naming that file.
   Restore.
6. Replace `dev-flow` with `dev-flow-worktree` in a mirrored line of the worktree file's
   prose → still exits 0 (canonicalization). Revert.
7. Make line 12 identical in both files → exits 1 as a stale exception. Revert.
8. Add `plugins/scratch/.claude-plugin/plugin.json` with no marketplace entry → exits 1.
   Remove it.
9. Open the PR and confirm the `check-sync` job appears and is green.
