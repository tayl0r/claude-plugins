---
dev-flow:
  slug: gh-26-family-name
  stops: [pre-merge]
  docs: commit
---

# gh-26: `family name` for the plugin pair is the same relation, one domain over

## Goal

Close issue #26 with a **ruling of no finding** on the three shipped uses of `family` for the two dev-flow plugin variants, and with the one edit that makes that ruling bind: `CONTEXT.md`'s **Family** entry gains the plugin domain as a second instance of the relation it already defines, keeping its model sentence byte-identical so **Family match** is untouched.

No shipped skill text changes. No hand-mirrored pair is edited. No version is bumped. The three sites named in the issue stay exactly as they are, and the whole change is one line of `CONTEXT.md`.

## Scope check — one file, and not a mirrored one

One subsystem: the glossary. The three sites live in two hand-mirrored pairs (the pipeline `SKILL.md` pair and the two `README.md`s), which is what makes touching them expensive — and this change touches neither. `CONTEXT.md` is enrolled in no mirror pair, ships into no plugin cache, and `scripts/check-sync.py` never reads it. Nothing here decomposes.

## The ruling: no finding

`family`, used for the shared name of `dev-flow` and `dev-flow-worktree`, is **the same relation one domain over** — the rule that spared `collision` and `drift` on the #20/#22 branch. It is not a second sense, and renaming it would be the error, not the repair.

The precedent, verbatim from `docs/superpowers/specs/2026-07-29-gh-20-diff-terminology-design.md:278`:

> The pipeline pair's *"accidental branch collisions"* and *"Intake collision check"* are the ordinary computing sense — one identifier, two claimants — applied to branch names rather than words. Same sense, different domain; **no finding**. Renaming would be the actual error, leaving one concept with two names across the pass and this document.

### What the three sites actually name

Read in context rather than as the quoted line, all three do one job: they explain why a single settings file, `.claude/dev-flow.local.md`, serves two separately installed plugins. The pipeline `SKILL.md` pair says it inside a sentence that has already called the two plugins *variants* — *"**Both plugin variants read this same file and this same key** (`dev-flow` is the family name they share)"* — so `variant` is the member and `family` is the line, in one sentence, unambiguously. `plugins/dev-flow-worktree/README.md:89` says the same thing to a user: *"The file keeps the family name `dev-flow` for that reason, even here."*

That is a product line named independently of any version within it. `CONTEXT.md`'s **Family** defines exactly that relation for models; ADR-0001 establishes it for these plugins — two near-identical trees, one axis apart, each installing alone into its own version-keyed cache. The domain changes from models to plugins; the relation does not.

### The strongest case for a finding, and where it breaks

The issue's version of this case is that nothing has ever flagged the plugin use, and that may be absence of evidence. The stronger version is structural, and worth stating at full force:

> **Family**'s relation is *one product, many dated versions* — Opus 5 and Opus 4 are the same product at two times. The plugin pair is *one name, two different products*, each carrying its own independent version stream (`2.6.0` and `1.8.0`). Worse, the family name is also one member's name: there is no model called "Opus" simpliciter, but there *is* a plugin called `dev-flow`. So the plugin use is not the model relation transposed — it is a containment relation the entry does not describe, carrying an overload the model sense does not have.

Three things defeat it.

**1. The overload is a fact about the plugins, not about the word.** `dev-flow` really does name both the line and one member — that follows from ADR-0001's naming (`dev-flow-worktree` is `dev-flow` plus one axis), and it is true whatever noun the parenthetical uses. Rename `family` to anything and the overload sits untouched; the parenthetical is the sentence that *resolves* it. A proposed finding whose proposed fix removes nothing is the shape #20 rejected when it demanded that a repair close the defect it names.

**2. "Two different products" is false on the repo's own record, and the objection needs it.** ADR-0001 opens: *"`dev-flow` and `dev-flow-worktree` are the same pipeline differing on one axis … their skill files are near-identical copies. This is forced, not lazy"* — forced because *"each plugin installs alone into a version-keyed cache directory holding only its own tree."* One pipeline, two packages; the two version streams are what that packaging split buys — ADR-0001's *Revisit when* names *"coupling both variants to a single version stream"* as the cost of merging them — not evidence of two products. So the real contrast is not *one product over time* versus *two products at once*; it is one product line whose members are individuated by date versus by axis. **Family** does not legislate that: *"independent of any dated version within it"* states what the name is independent **of**, not how members are told apart, and it transposes intact — one settings file, one key, one answer, across two independently versioned plugins, which is precisely what the shipped sentence leans on. And if a reader still holds the two relations distinct, the ruling does not move: the rename is rejected independently on cost and on every available replacement word (see *Rejected alternatives*), and the glossary edit settles the sense either way.

**3. The repaired case and this case differ on that same clause, which is what makes the discriminator a rule rather than a preference.** #20 repaired *"one of a known family (connectors, handlers, jobs…)"* to `kind` because connectors, handlers and jobs are not a product line at all: no shared name, no shared release identity, nothing versioned. The plugin pair has a shared name, a shared marketplace entry pattern, a shared source per ADR-0001, and per-member versions. Ruling this one a finding therefore requires a discriminator the entry does not contain — *members individuated by date, not by axis* — read into it rather than found there. And `collision` and `drift` are not the parallel #26 assumes: neither has a `CONTEXT.md` entry, so #20 decided both against shipped-prose usage rather than against a definition. The comparison that settles `family` is the repaired rubric case, made above.

### What the shipped checks would actually do here

The rule being applied is the one that shipped in `0c05098`, so both halves are quoted rather than recalled.

The **glossary-conformance angle** (`plugins/*/skills/adversarial-review/SKILL.md:42`) greps *"the diff's added lines of shipped text"*, and counts a hit only where the diff *"uses the term as a **name** … and then only if it names something the entry does not define"*. It is diff-scoped by construction. The three sites are pre-existing lines in no current diff, so the angle has never looked at them and never will until someone edits them. **That is the answer to the issue's "is it fine, or was no check pointed here" question: both.** Nothing scans standing shipped prose, deliberately — and the standing prose is also correct.

The **terminology collision and drift** pass (`:48`) runs on design and plan artifacts, not on shipped files, and reads the glossary first. Its collision half excludes *"a word the artifact uses in the sense the repo already has"*. So the question a future artifact writing "the family name" puts to the check is: does `CONTEXT.md` settle `family` for plugins? Today the entry opens *"A model's product line"*, and a literal reader of the check answers **no** — the glossary settles a model's product line, the artifact means a plugin's, the senses differ, report it. That is the false positive this issue is, arriving on schedule, and it costs a resolver group — priced at ~86,022 tokens in gh-7's measured run.

## A no-finding ruling still has to ship something, and only one place binds

The three candidate homes are not equivalent, because the checks name their inputs:

| Home | Read by the shipped checks? |
|---|---|
| This design doc / the issue thread | **No.** The collision half says *"skip prior design/plan records (`docs/superpowers/`) — history, not shipped text"*, and the angle skips the same path. No reviewer reads GitHub issues. |
| `docs/adr/` | **No.** Both checks name `CONTEXT.md` at the repo root, or the per-context files a root `CONTEXT-MAP.md` names. Neither reads `docs/adr/`. (`docs/agents/domain.md` has *agents* read ADRs before exploring; the two checks do not.) |
| `CONTEXT.md` | **Yes, first.** *"read the domain glossary first … both halves key off it"*, and the angle *"Iterate the glossary's entries"*. |

So a ruling recorded anywhere but the glossary is a ruling that re-litigates itself on the next artifact that says "family". That is the whole reason this change is not zero-diff.

### The edit, and why it is not the risky widening

Issue #26's option 3 — make **Family** domain-neutral — is correctly flagged as risky: **Family match** depends on *"the family its requested tier names"* meaning a model family, and a neutral definition also re-legitimizes the grab-bag sense #20 just removed. This change does neither. It keeps the model sentence first and byte-identical, appends the plugin domain as a named second instance, and closes with an explicit exclusion so the repaired rubric case stays repaired.

The shape is already in the file: **Seam** carries a definition plus *"This repo uses the word at two levels"*, which is how #16 resolved `seam` — the word stayed and the glossary recorded the two levels. **Tier** already cross-references (*"Distinct from *family*"*). This is that pattern, not a new one.

## Exact change list

### 1. `CONTEXT.md` — line 21, the definition line under `**Family**:`

Current (line 21):

```text
A model's product line (Opus, Sonnet, Fable), independent of any dated version within it.
```

Replace **line 21** with:

```
A model's product line (Opus, Sonnet, Fable), independent of any dated version within it. A plugin's product line likewise: `dev-flow` is the family name its two variants share, independent of either variant's own version. A set of merely related constructs (connectors, handlers, jobs…) is not a family — the word for that is *kind*.
```

A one-line replacement, not an append: `CONTEXT.md` stays at **67 lines**.

Three properties are deliberate. The **model sentence is first and unchanged**, so **Family match** and **Tier** resolve against it exactly as before — a tier names `sonnet` or `opus` and never names a plugin, so the second sentence introduces no ambiguity into the provenance check. The **plugin sentence names `variant` for the member**, the word both `SKILL.md` copies and `plugins/dev-flow-worktree/README.md:11` already use, so the entry does not coin anything. The **exclusion sentence quotes the rubric's own parenthetical** and points at `kind`, so the entry cannot be read as licence for the third sense #20 removed — the one guard a widened entry actually needs.

Measured against its own rule: the replacement line contains none of the six names `CONTEXT.md` marks as ones to avoid (`finder`, `first-pass reviewer`, `group agent`, `judge`, `arbiter`, `boundary` — zero occurrences in that line), and both borrowed words carry the sense shipped prose already gives them (`variant` = one of the two plugins, 7 occurrences; `kind` = a set of related constructs, 2 occurrences, both the repaired rubric bullet).

### 2. Nothing else changes, and each is a decision rather than an omission

- **The three sites named in #26 are untouched** — that is the ruling.
- **No `_Avoid_:` line is added to Family.** The entry now covers both domains; there is no rejected synonym to record.
- **No second entry** (e.g. **Plugin family**). The angle iterates entries and checks a hit against the entry it came from; two entries for one word doubles that work and makes "which entry" a judgment call the seed should not have.
- **`Family match`, `Tier`, and every other line stay byte-identical.**
- **No version bump.** `CONTEXT.md` ships into no plugin cache, so the version-keyed-cache rule in `CLAUDE.md` does not apply. `dev-flow` stays `2.6.0`; `dev-flow-worktree` stays `1.8.0`. This is asserted in Verification because the reflex is to bump.
- **`.claude-plugin/marketplace.json` is untouched**; no `description` changes, so `check-sync.py`'s Check A is unaffected, and Check B's mirror pair is not in this change at all.

## Applying the shipped checks to this document

**Collision half.** `family` — used throughout in `CONTEXT.md`'s sense as this change extends it, which is the change; the extension is stated in the glossary rather than assumed here. `variant`, `kind`, `angle`, `pass`, `seed`, `resolver`, `artifact`, `mirror pair`, `hand-mirrored pair` — each held to `CONTEXT.md`'s sense throughout. `ruling` (0 prior occurrences in shipped prose) and `precedent` (0) are coined here and collide with nothing. **Against itself:** `family` carries one sense in this document — the product line — and `variant`/`member` carry the other, never swapped.

**Drift half**, over the six names `CONTEXT.md` marks as ones to avoid — `finder`, `first-pass reviewer`, `group agent`, `judge`, `arbiter`, `boundary`. Each occurs exactly **twice**, and all twelve occurrences are the two enumerations of the `_Avoid_:` list itself, in *The edit* and in this section: mentions, excluded by *"a term it merely mentions — quoting the glossary … is not a candidate"*. This document names nothing by any of them: the Seam concept is `seam` throughout, including inside the quotation of #20's precedent, and the second tier is `resolver`. **No finding**, and unlike gh-20's document this one had no adversarial corpus to survive.

## Rejected alternatives

- **Rename the three sites.** Rejected on the ruling — it repairs nothing — and independently on cost and on the replacement words. Cost: two hand-mirrored pairs with no mechanical check behind them, the highest-risk edit shape in this repo per ADR-0001's own *Consequences*, plus two version bumps, for a non-defect. Words: measured with `git grep -oiw <w> -- 'plugins/**' CONTEXT.md README.md` — the corpus that ships into a plugin cache plus the two authoritative root files, excluding `docs/superpowers/` because both shipped checks exclude it and `docs/adr/`/`docs/agents/` because neither check reads them. `kind` **2** (the repaired rubric bullet, both copies), `sibling` **2**, `pair` **4**, `variant` **7**, `type` **15**, `group` **16**, `suite` **31**, `line` **47**, `name` **59**; `series` and `umbrella` **0**. The counts are not the decisive part — the senses are. `sibling` and `variant` both already denote *one member* of the pair in these very files (`SKILL.md:77`/`:79` *"the sibling `dev-flow-worktree` plugin"*; `README.md:11` *"the worktree-isolated variant of `dev-flow`"*), so promoting either to mean the *line* manufactures the collision the rename claims to remove. `kind` is available and clean but is now the repo's word for the un-versioned grab-bag, which is the opposite of what this names. `type` and `group` are taken by *Seam placement* and the Resolution procedure. The best available rename is strictly worse than no rename.
- **Zero diff: rule in the issue and in this document, change no file.** Rejected on the table above — `docs/superpowers/` is explicitly skipped by both shipped checks and no reviewer reads issues, so the ruling would bind nothing and the next artifact saying "family" re-opens it at resolver cost.
- **Record it in a new ADR.** Rejected for the same mechanical reason: neither shipped check reads `docs/adr/`. An ADR is the right home for a decision with consequences to revisit; this is a vocabulary fact, and vocabulary facts are read out of the glossary by name.
- **Widen Family to a domain-neutral definition (#26's option 3 as written).** Rejected: **Family match** is defined against *"the family its requested tier names"*, and a definition with no model in it makes that phrase resolve to nothing in particular; a neutral "a product line" also re-admits *"one of a known family (connectors, handlers, jobs…)"*, undoing `0c05098`. Naming the second domain explicitly, with an exclusion, buys the binding effect without either cost.
- **Also reword the parenthetical while it is under the microscope**, e.g. to spell out that `dev-flow` names both the line and one member. Rejected: it is a hand-mirrored edit across two pairs that no check covers, the README pair already diverges on this text so no symmetric edit exists, and it would force two version bumps — all to improve a sentence this design just found correct. `CLAUDE.md`'s "just do it" rule is scoped to low-risk changes; this is the repo's own documented high-risk shape.

## Honest limit

The widened entry makes `family` harder to flag, and that cuts both ways: a genuinely bad third use is now marginally better camouflaged. The exclusion sentence is the guard, and it is a semantic judgment a `sonnet` seed can get wrong in either direction. Under-detection returns the status quo — the sense that shipped for three releases without complaint. Over-detection costs one seed read and is then filtered by the reportability rule, which demands two quotable senses and a location. Neither failure produces a wrong ruling; both produce seed cost.

## Out of scope

- **Issue #23.** Nothing designed here changes it, and this design does not attempt to discharge it. One observation belongs on that issue and is recorded here because it was verified rather than assumed: `~/.claude/plugins/installed_plugins.json` now pins `dev-flow@taylor-plugins` to **`2.6.0`** at `gitCommitSha 0c050989`, and the cached `~/.claude/plugins/cache/taylor-plugins/dev-flow/2.6.0/skills/adversarial-review/SKILL.md` is **89 lines** — the post-`0c05098` text, not the 87-line pre-change copy. So this run executes the drift clause and the glossary-conformance angle, and its own design, plan and PR reviews are the zero-marginal-cost observation #23 asks for. Whether they fire, and on what, is for #23 to record.
- **The README pair's divergence.** `plugins/dev-flow/README.md` has zero `family` occurrences and `plugins/dev-flow-worktree/README.md` has one; that asymmetry is content-driven (only the worktree README explains why the file is not called `dev-flow-worktree.local.md`) and is not repaired here.
- **A `Kind` glossary entry.** The rubric's `kind` is one word in one bullet; the glossary defines shapes, not one row per word. If `kind` ever names a concept the repo reasons about, that is a different change.

## Verification

1. **Exactly one file changed, and it is not a plugin file.** Expect ` CONTEXT.md | 2 +-` then ` 1 file changed, 1 insertion(+), 1 deletion(-)` and nothing else, then `plugins/ untouched: OK`:

   ```sh
   git diff --stat 0c05098 -- . ':!docs/superpowers/'
   git diff --quiet 0c05098 -- plugins/ .claude-plugin/ && echo "plugins/ untouched: OK"
   ```

   The `':!docs/superpowers/'` pathspec is required, for the same reason step 5's is: this design's front-matter sets `docs: commit`, so this run's own design and plan docs are themselves committed on this branch, and an unfiltered diff against the base necessarily reports them — *"and nothing else"* would be unsatisfiable by construction. Any path outside `CONTEXT.md` and `docs/superpowers/` is a failure.

   The second command is the check `CLAUDE.md` requires for a hand-mirrored pair and the one this change can make strongest: rather than proving a mirrored edit landed on both sides, it proves neither side was touched, against the base commit rather than against the pair's other half.

2. **The three sites named in #26 read exactly as they did.** Expect `1` for each of the two `SKILL.md` copies, and one hit in the README:

   ```sh
   git grep -c -F '(`dev-flow` is the family name they share)' -- plugins/
   git grep -n -F 'The file keeps the family name `dev-flow` for that' -- plugins/dev-flow-worktree/README.md
   ```

3. **Residue.** This edit deletes no text — it extends a line — so the usual removed-phrase grep degenerates to one assertion: the pre-change one-sentence form must no longer occur as a *whole* line. `git grep` has no `-x`, so this runs as plain `grep` and is also folded into step 4. Expect no output and `exit=1`:

   ```sh
   grep -x -F "A model's product line (Opus, Sonnet, Fable), independent of any dated version within it." CONTEXT.md; echo "exit=$?"
   ```

4. **Design conformance — the replacement line landed verbatim, in the right place.** `check-sync.py` never reads `CONTEXT.md` and no mirror check applies, so this is the only thing standing between the design and a paraphrase. It re-reads the replacement from this design file on disk — never retyped — and requires a byte-for-byte line match in `CONTEXT.md` directly after the `**Family**:` anchor. The anchor matters on its own: the same line pasted under **Family match** or **Tier** would satisfy a bare containment check and be wrong. The script is pure ASCII on purpose, so a mistyped copy fails loudly rather than passing; the non-ASCII characters live only in the block it reads. **The fence is unindented on purpose** — a `python3` heredoc indented under a list item is an `IndentationError`.

```sh
python3 - <<'PY'
import sys
from pathlib import Path
DESIGN = "docs/superpowers/specs/2026-07-31-gh-26-family-name-design.md"
TARGET = "CONTEXT.md"
ANCHOR = "**Family**:"
OLD = "A model's product line (Opus, Sonnet, Fable), independent of any dated version within it."
FENCE = chr(96) * 3
blocks, cur, mode = [], None, None
for line in Path(DESIGN).read_text(encoding="utf-8").split("\n"):
    s = line.strip()
    if mode is None:
        if s.startswith(FENCE):
            mode, cur = s[3:], []
    elif s == FENCE:
        if mode == "":
            blocks.append(cur)
        mode, cur = None, None
    else:
        cur.append(line)
assert [len(b) for b in blocks] == [1], "design plain-fence shape changed; stop and re-read the design"
want = blocks[0]
lines = Path(TARGET).read_text(encoding="utf-8").split("\n")
if lines and lines[-1] == "":
    lines.pop()
bad = []
if len(lines) != 67:
    bad.append("%s is %d lines, want 67" % (TARGET, len(lines)))
at = [i for i in range(len(lines) - len(want) + 1) if lines[i:i + len(want)] == want]
if len(at) != 1:
    bad.append("Family definition found %d times, want exactly 1" % len(at))
elif lines[at[0] - 1] != ANCHOR:
    bad.append("sits after %r, want %r" % (lines[at[0] - 1][:40], ANCHOR))
if OLD in lines:
    bad.append("the pre-change one-sentence Family line survives as a whole line")
if not want or not want[0].startswith(OLD):
    bad.append("the replacement no longer opens with the model sentence Family match depends on")
for why in bad:
    print("MISMATCH:", why)
print("design-conformance:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

   Expect exactly `design-conformance: OK` and `exit=0`. The shape assertion (`[1]`) fires if this document's plain-fenced blocks are ever added to or reordered — every other fence here carries an info string (`text`, `sh`), so adding a verification step never disturbs the index. **Keep it that way.** The final check is the one that protects **Family match**: it fails if a future edit reorders the entry so the model sentence is no longer first.

5. **`0c05098`'s repair is not silently undone.** The widened entry must not re-admit the grab-bag sense. Expect **no hits** — today it is 0, measured:

   ```sh
   git grep -n -i 'known family' -- . ':!docs/superpowers/'
   ```

   The pathspec is required: this design quotes the string.

6. **Versions did not move.** Expect `dev-flow-worktree` at `1.8.0` and `dev-flow` at `2.6.0`, each on a line naming its own file:

   ```sh
   git grep '"version"' -- plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
   ```

   `git grep`, not `grep -h`: the assertion is *which plugin is at which version*, and `-h` strips exactly the labels that carry it — under Claude Code's Bash tool bare `grep` is a ugrep-backed shell function whose multi-file output order is not stable between runs (measured: both orders occur), so with `-h` the two values become indistinguishable. `git grep` labels each hit with its path and sorts by path, so the output is deterministic and self-describing.

7. `python3 scripts/check-sync.py` — passes. Expect `mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)`, unchanged, since no file it reads is touched.

8. `claude plugin validate .` — passes; the 8 missing-author warnings are expected.

9. **Behavioural, and for #23 rather than for this change's gate.** The installed copy is already `2.6.0` (see *Out of scope*), so this change's own reviews exercise both new checks. Correct outcomes: in `design` and `plan` mode on this change's artifacts, **no finding** on `family` — a finding that quotes **Family**'s model sentence against this document's plugin use is evidence the *"in the sense the repo already has"* exclusion is too weak, which is the same false positive this change exists to foreclose. In `diff` mode on this branch, the added shipped line is `CONTEXT.md`'s own **Family** entry, which by construction names what its entry defines, so **no finding** there either. Record the outcome on #23; do not change this design because of it.

## PR

```text
Closes #26
```

## Assumptions recorded

- **`CONTEXT.md` is what the shipped checks read, and `docs/adr/` is not.** Read from the shipped text of both checks in `plugins/dev-flow/skills/adversarial-review/SKILL.md:42` and `:48`, not from memory. The whole "where does the ruling live" argument rests on it. If a future change teaches either check to read ADRs, the ruling's home is worth revisiting; nothing about the ruling itself changes.
- **`CONTEXT.md` requires no version bump.** It is outside `plugins/`, so it enters no version-keyed cache. Verified against `CLAUDE.md`'s rule, which scopes the bump to `plugins/<name>/.claude-plugin/plugin.json` behavior changes.
- **The plugin pair is a product line in the sense the entry means.** Taken from ADR-0001, which establishes one pipeline differing on one axis with per-plugin version streams — not inferred from the names. If the two plugins ever diverge into genuinely different products, the second sentence of the entry becomes false and the ruling with it; that is a visible event, not a silent one.
- **A seed can tell "a product line with versioned members" from "a set of related constructs".** Load-bearing in the exclusion sentence. It is a semantic judgment and can fail either way; both failure modes cost seed reads, not a wrong ruling. See *Honest limit*.
- **The measured counts are a floor, not a census of the repo.** The corpus is `plugins/**` plus `CONTEXT.md` and the root `README.md`. `docs/adr/` was measured separately for `family` — 7 occurrences, all in ADR-0002, all the model sense — and excluded from the table because no shipped check reads it.
