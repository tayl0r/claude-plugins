---
dev-flow:
  slug: gh-39-verification-rules-home
  stops: [pre-merge]
  docs: commit
---

# gh-39 — the verification rules get a repo-wide home, and the mirror bullet keeps its reason

Close **#39** by moving `CLAUDE.md` line 9's two verification prescriptions — the `Always:` pair and the design-doc block check — **verbatim** into a new repo-wide section, `## Verifying a change`, and rewriting the mirror-pair bullet's closing sentence to point forward at it while keeping the one argument that is genuinely mirror-pair-specific.

One file changes: `CLAUDE.md`. Line 9 is replaced; a four-line section plus one blank line is inserted after line 12. **No `scripts/` change, no plugin file, no version bump.** Each of those is a conclusion, not a deferral — see *Out of scope*.

The issue's decisive question — *whether option 3's guidance can carry a rule whose sharpest motivation is mirror-pair-specific* — is answered **no**, on four measured grounds, in *The option-3 question, answered*. That answer is the reason option 3 is not chosen, and it does not rest on the motivation at all. One half of the `Always:` pair — the removed-phrase grep — does generalize, and ground 4 answers it too: `plugins/` could at most *echo* it, never house it, so the severable half is filed as **#54** and changes nothing here.

## Scope check — one subsystem, one file

One subsystem: this repo's written contributor conventions, the same subsystem `bf7676b` (#32/#33) and `963a66c` (#24) changed. #39 asks exactly one question — *where do these prescriptions live?* — and the answer is one file's worth of edits with no ordering dependency on anything. Nothing decomposes further.

Sequencing is already discharged. `0445fb9` (#40/#41) was explicitly sequenced **before** this change by its own *Decomposition* table, on the grounds that it *"creates the first pipeline-general success-criteria text there, which is the evidence that makes option 3 evaluable against shipped text rather than against a hypothetical."* It merged; this design is written against `0445fb9` and uses that shipped text as evidence.

## What is true today, measured at `0445fb9`

Every measurement in this section is of the tree **before** this change, pinned to `0445fb9` (this branch's base), given with the command that printed it, run while this document was written. No number appears that its command's output does not show.

### The clauses, and where they sit

`CLAUDE.md` line 9 is a bullet under `## Changing a plugin`. Its subject is the mirrored pairs; its final three sentences are:

- the punchline — *"So any change to a mirrored pair, machine-checked or hand-mirrored, must also verify against something outside the pair"*;
- **`Always:`** — grep for the removed phrases; assert every file the edit touches is byte-for-byte its merge-base blob with exactly the intended edit applied;
- **`When the change has a design doc`** — the `python3` block-conformance check, and the shared `read_blocks` reader.

Both markers entered `CLAUDE.md` in the same commit, but the clauses' current text did not: the `Always:` clause's byte-for-byte sentence arrived at `bf7676b`, and the design-doc clause's `read_blocks` tail at `963a66c`. Only three commits have touched the file at or after `4e32e0e`, so those three are the whole provenance of line 9's current text. The table below measures from `4e32e0e` because that is where the block-conformance check it counts first appeared.

```sh
git log --oneline -S'**Always:**' 0445fb9 -- CLAUDE.md
git log --oneline -S'byte-for-byte its merge-base blob' 0445fb9 -- CLAUDE.md
git log --oneline -S'When the change has a design doc' 0445fb9 -- CLAUDE.md
git log --oneline -S'read_blocks' 0445fb9 -- CLAUDE.md
git log --oneline 4e32e0e^..0445fb9 -- CLAUDE.md
```

```text
4e32e0e adversarial-review: close two review-depth gaps in the seed passes (#18)
bf7676b Write down the two conventions CLAUDE.md left to judgment (#32, #33) (#49)
4e32e0e adversarial-review: close two review-depth gaps in the seed passes (#18)
963a66c Share the design-block reader, keep the mapping per change (#24) (#36)
bf7676b Write down the two conventions CLAUDE.md left to judgment (#32, #33) (#49)
963a66c Share the design-block reader, keep the mapping per change (#24) (#36)
4e32e0e adversarial-review: close two review-depth gaps in the seed passes (#18)
```

That five-command block and its seven-line output were run verbatim from the repo root and are transcribed exactly as printed (the last three lines are the fifth command). The commands are now pinned to `0445fb9`, which the old unpinned pair was not.

Each marker occurs once in the whole file, which is what lets *Verification* step 2 locate both spans by `partition`:

```sh
python3 -c 'import subprocess
t = subprocess.run(["git","show","0445fb9:CLAUDE.md"],capture_output=True,text=True,check=True).stdout
for p in ("**Always:**","**When the change has a design doc**"):
    print("%-40s occurrences=%d" % (p, t.count(p)))'
```

```text
**Always:**                              occurrences=1
**When the change has a design doc**     occurrences=1
```

### The repo applies them to every change, not to the pair

Every change merged after `4e32e0e` that carried a design doc, classified by whether it touched a mirrored file (machine-checked `adversarial-review/SKILL.md`, or one of the four hand-mirrored files) and by whether its design prescribed the block-conformance check:

```sh
python3 - <<'PY'
import subprocess, re
def git(*a):
    return subprocess.run(("git",)+a, capture_output=True, text=True, check=True).stdout
MIRROR = {"plugins/dev-flow/skills/adversarial-review/SKILL.md",
          "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md"}
HAND = {"plugins/dev-flow/skills/dev-flow/SKILL.md",
        "plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md",
        "plugins/dev-flow/README.md", "plugins/dev-flow-worktree/README.md"}
PAT = re.compile(r"read_blocks|never retyped|never re-?typed|from this design( doc)? on disk", re.I)
rows = []
for line in git("log", "--first-parent", "--format=%H %s", "4e32e0e..0445fb9").strip().split("\n"):
    sha, subj = line.split(" ", 1)
    files = sorted(set(f for f in git("show", "--name-only", "--format=", "-m",
                                      "--first-parent", sha).split("\n") if f))
    specs = [f for f in files if f.startswith("docs/superpowers/specs/")]
    if not specs:
        continue
    body = "".join(git("show", sha + ":" + p) for p in specs)
    touched = "mirror" if set(files) & MIRROR else ("hand" if set(files) & HAND else "none")
    rows.append((sha[:7], specs[0].split("/")[-1][:44], touched, bool(PAT.search(body))))
for r in rows:
    print("%s | %-44s | pair=%-6s | block-check=%s" % r)
print()
print("changes after 4e32e0e carrying a design doc:", len(rows))
print("  no mirrored file touched:", sum(1 for r in rows if r[2] == "none"),
      "-- of those with the block check:", sum(1 for r in rows if r[2] == "none" and r[3]))
print("  a mirrored file touched  :", sum(1 for r in rows if r[2] != "none"),
      "-- of those with the block check:", sum(1 for r in rows if r[2] != "none" and r[3]))
PY
```

```text
0445fb9 | 2026-08-02-gh-40-41-verification-blocks-desi | pair=mirror | block-check=True
bf7676b | 2026-08-02-gh-32-33-claude-md-conventions-de | pair=none   | block-check=True
c053b8e | 2026-08-02-gh-31-34-glossary-contents-design | pair=none   | block-check=True
a94f60a | 2026-08-02-gh-38-marker-framing-design.md    | pair=hand   | block-check=True
b4b5d1c | 2026-08-02-gh-28-29-review-prose-design.md   | pair=mirror | block-check=True
963a66c | 2026-08-02-gh-24-design-block-reader-design. | pair=none   | block-check=True
9a5cab2 | 2026-08-02-gh-30-flat-topology-design.md     | pair=hand   | block-check=True
c8b2182 | 2026-07-31-gh-26-family-name-design.md       | pair=none   | block-check=True
0c05098 | 2026-07-29-gh-20-diff-terminology-design.md  | pair=mirror | block-check=True
0a8a158 | 2026-07-28-gh-16-terminology-collision-desig | pair=mirror | block-check=True

changes after 4e32e0e carrying a design doc: 10
  no mirrored file touched: 4 -- of those with the block check: 4
  a mirrored file touched  : 6 -- of those with the block check: 6
```

**Ten changes, ten block-conformance checks, and four of the ten touched no mirrored file at all.** The four are `bf7676b` (`CLAUDE.md`), `c053b8e` (`CONTEXT.md`), `963a66c` (`CLAUDE.md` + `scripts/` + `.gitignore`) and `c8b2182` (`CONTEXT.md`). Adoption is total; 40% of it is outside the scope the text states.

Those ten are also *every* change merged in that range, not a design-carrying subset of a larger set — `git rev-list --count --first-parent 4e32e0e..0445fb9` printed `10`. So the table has no unexamined remainder.

The other half of the `Always:` pair tracks it exactly: all ten of the same designs prescribe a removed-phrase grep, under one of three labels.

```sh
python3 - <<'PY'
import subprocess, re
def git(*a):
    return subprocess.run(("git",)+a, capture_output=True, text=True, check=True).stdout
PAT = re.compile(r"expecting no hits|residue|removed phrase", re.I)
for line in git("log", "--first-parent", "--format=%H", "4e32e0e..0445fb9").strip().split("\n"):
    sha = line.strip()
    files = [f for f in git("show", "--name-only", "--format=", "-m", "--first-parent",
                            sha).split("\n") if f.startswith("docs/superpowers/specs/")]
    if not files:
        continue
    body = "".join(git("show", sha + ":" + p) for p in files)
    print("%s %-46s residue-grep=%s" % (sha[:7], files[0].split("/")[-1][:46], bool(PAT.search(body))))
PY
```

```text
0445fb9 2026-08-02-gh-40-41-verification-blocks-design residue-grep=True
bf7676b 2026-08-02-gh-32-33-claude-md-conventions-desi residue-grep=True
c053b8e 2026-08-02-gh-31-34-glossary-contents-design.m residue-grep=True
a94f60a 2026-08-02-gh-38-marker-framing-design.md      residue-grep=True
b4b5d1c 2026-08-02-gh-28-29-review-prose-design.md     residue-grep=True
963a66c 2026-08-02-gh-24-design-block-reader-design.md residue-grep=True
9a5cab2 2026-08-02-gh-30-flat-topology-design.md       residue-grep=True
c8b2182 2026-07-31-gh-26-family-name-design.md         residue-grep=True
0c05098 2026-07-29-gh-20-diff-terminology-design.md    residue-grep=True
0a8a158 2026-07-28-gh-16-terminology-collision-design. residue-grep=True
```

The label variation is worth recording, because it is the same shape the block check showed: `a94f60a` calls it *"Removed phrase — the check outside the pair"* while others call it *residue* or quote the clause's own *"expecting no hits"*. The prescription is followed universally; only its name varies.

### The repo has already written the wider scope down, in a second place

`scripts/design_blocks.py` — shipped code in this repo, landed by `963a66c` — states the rule's scope in its module docstring with **no mirror-pair qualifier at all**:

```sh
git grep -n -F 'CLAUDE.md requires every change carrying a design doc' 0445fb9 -- scripts/
```

```text
0445fb9:scripts/design_blocks.py:4:CLAUDE.md requires every change carrying a design doc to add a python3 check
```

So two files in this repo disagree today about who the rule binds, and the one stating the wider scope is the one the practice follows. That is not a second opinion to be reconciled; it is the same defect #39 reports, visible from the other side. **Hoisting makes the docstring true with no edit to `scripts/`.**

### The `Always:` clause's first exercise was declared out of its own scope

`bf7676b`'s design carries **A8**: *"This change is **not itself a mirrored-pair change** — `CLAUDE.md` is enrolled in no pair — so its own new `Always:` clause does not bind it. *Verification* steps 2 and 5 apply it anyway, as the rule's first exercise; that is voluntary."* The byte-for-byte clause is newer than the design-doc clause — `bf7676b` wrote it — so its sample is small and is stated at its real size: it has had exactly two exercises, that voluntary one and `0445fb9`'s, which was in scope. The classification table above is ordered newest-first, and `0445fb9` is the only row above `bf7676b`, so those two are the whole population. One of two is in scope, and it is the newer clause's turn to repeat the older one's pattern rather than a trend already measured.

### The heading mis-scopes the bullet a second time

The mirror bullet sits under `## Changing a plugin`. The four out-of-scope changes above touched `CLAUDE.md`, `CONTEXT.md`, `scripts/design_blocks.py` and `.gitignore` — not one of them a plugin file. So even a reader who ignored the bullet's own sentence would take the enclosing heading as the scope and get the same wrong answer. Moving the prescriptions to their own top-level section fixes both scopings at once; a new bullet inside `## Changing a plugin` would fix neither.

### `MIRROR_PAIRS` holds one pair, and enrols neither prose file

```sh
git grep -n -E 'MIRROR_PAIRS = \[|"name":' 0445fb9 -- scripts/check-sync.py
```

```text
0445fb9:scripts/check-sync.py:30:MIRROR_PAIRS = [
0445fb9:scripts/check-sync.py:32:        "name": "adversarial-review",
```

One entry. The issue's observation stands, and it is context rather than a proposal: `CLAUDE.md` and `CONTEXT.md` have no second copy to enrol, so *enrol them* is not among the options (*Rejected alternatives*).

## The decision

**A hybrid of options 2 and 1: a repo-wide `## Verifying a change` section in `CLAUDE.md` that the mirror bullet points to, with the mirror-specific residue kept in the bullet.**

- Block 1 is the new section: the heading and the two prescriptions **byte-identically**, each as one bullet, and nothing else. The repo-wide scope is carried by the top-level heading, by the word `Always:` that opens the first bullet, and by block 0's forward pointer — no framing sentence restates it (*Rejected: a framing sentence for the new section*).
- Block 0 is the new line 9. Everything up to and including *"must also verify against something outside the pair."* is byte-identical to the base; what follows is replaced by a forward pointer plus the one sentence that is genuinely mirror-pair-specific — *a stray edit applied identically to both copies is the one place here where reading the diff cannot catch it, because a doubled hunk is the expected shape there.*

The split is exactly the issue's own diagnosis applied in both directions. The **rule** is repo-wide, so it goes where every change's author reads it. The **reason the rule is sharpest** is mirror-pair-specific, so it stays where the pair is described. Neither is duplicated.

### The option-3 question, answered

The issue asks it directly: *whether option 3's guidance can carry a rule whose sharpest motivation is mirror-pair-specific.* **It cannot** — and what stops it is not the motivation. Three of the four grounds below would stop it even if the motivation generalized perfectly.

**1. The design-doc clause names repo-local instruments, and `plugins/` names none.** It names `scripts/design_blocks.py` and `read_blocks`; the bullet that hosts it names `scripts/check-sync.py`. None of the three exists in any repo but this one, and dev-flow ships into arbitrary repos. This ground reaches one of the three prescriptions, and the other two are not left unanswered: the byte-for-byte assertion is ground 3's, the removed-phrase grep is ground 4's. Measured — no instrument token of any kind appears under `plugins/` today:

```sh
git grep -c -i -E 'check-sync|design_blocks|read_blocks|merge-base blob|mirror pair|fenced block' 0445fb9 -- plugins/
```

That command printed nothing and exited 1. `0445fb9`'s own design set that boundary in terms this change can be tested against: *"a proposal to reference `design_blocks.py`, `read_blocks`, the merge-base-blob assertion or the removed-phrase grep from `plugins/` is out of scope here and is #39's to make."* This design makes that call, and the answer is *no* for all four: grounds 1 and 2 for `design_blocks.py` and `read_blocks`, ground 3 for the merge-base-blob assertion, ground 4 for the removed-phrase grep.

**2. The clause's precondition is absent from `plugins/`.** The design-doc clause fires only for *"a design doc that gives replacement or inserted text as fenced blocks"*. dev-flow nowhere asks a design for that — the word does not occur under `plugins/` at all:

```sh
git grep -c -i -F 'fenced' 0445fb9 -- plugins/
```

That command printed nothing and exited 1. Option 3 would therefore have to ship the **precondition** as well as the rule: every dev-flow design in every repo would be told to express its edits as verbatim replacement blocks. That is this repo's convention for prose changes, adopted because its product *is* prose. It is not a pipeline-general design convention, and shipping it as one is a much larger change than #39 contemplates.

**3. Outside a repo like this one, the byte-for-byte clause becomes a criterion that cannot fail — which the same plugin's review tier is now told to flag.** *"Every file the edit touches is byte-for-byte its merge-base blob with exactly the intended edit applied"* is checkable only where *the intended edit is itself a machine-comparable artifact*, which is precisely what the fenced blocks supply. Where a design describes behaviour rather than bytes — the ordinary case in a code repo — the expected side has to be read off the working tree, and the assertion degenerates into *the diff equals the diff*. `0445fb9` shipped the clause that catches that, into the same plugins option 3 would edit:

```sh
git grep -c -F 'a criterion that cannot fail is untestable' 0445fb9 -- plugins/
```

```text
0445fb9:plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md:1
0445fb9:plugins/dev-flow/skills/adversarial-review/SKILL.md:1
```

Option 3 would ship a rule whose general-repo instances the same plugin's design/plan correctness seed is instructed to report. That is a self-contradiction inside one plugin, not a cost to be weighed.

**4. What already crossed named no instrument; the one prescription that still generalizes is severable, and `plugins/` is no *home* for it either.** `0445fb9` extracted the pipeline-general residue: *Command discipline* now binds the success criteria a design emits, and *Measurements are derived, not typed* generalizes the never-retype principle from replacement text to numbers. Both state properties; neither names a repo path, a script, a mirror pair, or a check to write. The evidence #39 was sequenced to wait for therefore exists and reads clearly: the boundary between property and instrument is real, and it is already drawn in shipped text. But one of the four things `0445fb9` handed to #39 sits on the property side and has **not** crossed, and it is answered here rather than assumed: the removed-phrase grep — *"grep for the exact phrases the edit removes, expecting no hits"* — names no instrument, and ground 2's precondition does not reach it, because the phrases an edit removes are what its own diff shows rather than something the design must first have written as a block. Neither passage above states it: one governs how a criterion's commands are written, the other what numbers an artifact may state.

Severable is not relocatable, and what stops the move is the two files' **audiences** rather than the rule's content. `CLAUDE.md` is auto-loaded and binds every change made in this repo, dev-flow-driven or not; a plugin's `SKILL.md` binds a run of that skill, in whatever repo it runs. `plugins/` therefore cannot *hold* the grep on this repo's behalf — a relocation would leave every hand edit here unbound. The only form option 3 can take for it is an **additive echo** beside the two properties above, which is exactly the shape `0445fb9` used: *"Non-goal: this change does not decide #39. `CLAUDE.md` is untouched and stays the home of every repo-local instrument."* An additive echo answers no part of *where do these prescriptions live* and leaves this change's edit byte-for-byte what it already is, so it is a separate change on top of this one — filed as **#54** — not an alternative to it. What the new section carries, then, is instruments, a precondition, and one property that belongs in a repo-wide home regardless of what `plugins/` later says.

One counter-consideration, recorded because `0445fb9`'s design raised it against itself: the *Measurements* bullet landed in **Cross-Cutting Concerns**, which is where an option-3 implementation would append, so option 3's *price* is now a bullet beside an existing one rather than a new home. That is a fact about cost. Grounds 1–3 are about correctness, and cost does not reach them. `0445fb9` asked for exactly this treatment — *"#39 should weigh it as a fact about cost, never as a precedent for merit"* — and this is that weighing.

### Rejected: option 1, leave it in the mirror bullet

The strongest rejected option, because the anchoring argument is real: the new byte-for-byte clause does close a hazard the bullet names as a property of `check-sync.py`. What defeats it:

- **The scope the text states is not the scope the repo uses, by a measured 4 of 10** (*The repo applies them to every change*). Every one of those four wrote the checks anyway, so the text is not restraining anyone; it is only making each author decide again whether it binds them.
- **The repo has already written the wider scope down elsewhere**, in `scripts/design_blocks.py`'s docstring, and the two statements contradict each other. Leaving it means keeping a contradiction between a rule and the shipped code that implements it.
- **The rule's own author declared the rule out of scope for the change that wrote it** (`bf7676b`'s A8) and applied it voluntarily. A rule whose first exercise needs an assumption to license it is mis-housed — that is #39's central sentence, and nothing measured here contradicts it.
- **The enclosing heading mis-scopes it independently.** Even a reader who reads *"any change"* generously still finds the bullet under `## Changing a plugin`, and none of the four out-of-scope changes touched a plugin file.

What survives the rejection is the *reason*, which block 0 keeps verbatim in substance: the mirror pair is where reading the diff cannot substitute for the assertion. Option 1's argument is not discarded, it is relocated to the sentence it actually supports.

### Rejected: pure option 2 — move everything, leave the bullet with no verification sentence

This is what a naive hoist produces, and it loses the one thing option 1 is right about. `bf7676b`'s design established it as the clause's whole justification: *"a stray edit applied identically to both copies looks exactly like a correct mirrored edit. Everywhere else in the repo a doubled hunk is a smell; in the pair it is the expected shape. That is why this clause belongs in this bullet rather than being generic change hygiene."* Delete that from the bullet and a later reader has a repo-wide rule with no statement anywhere of why it is not belt-and-braces — which is exactly the state that invites someone to weaken it. Block 0 keeps it, one sentence, attached to the pair it is about.

### Rejected: a new bullet inside `## Changing a plugin`

Fixes the bullet's sentence and leaves the heading's mis-scoping untouched, which is half the defect (*The heading mis-scopes the bullet a second time*). The issue reaches the same conclusion from the other direction.

### Rejected: rewriting the prescriptions while moving them

Tempting — `Always:` reads slightly oddly as the first of two list items, and *"The other checks here"* could be sharpened. Refused on three grounds:

- This change's charter is **placement**. The content was reviewed one, five and ten changes back — `bf7676b` for the byte-for-byte sentence, `963a66c` for the design-doc clause's `read_blocks` tail, `4e32e0e` for the rest, all three counts read off the range the classification table covers. Re-opening it inside a relocation is how a move turns into an unreviewed rewrite.
- Moving verbatim makes *"moved, not rewritten"* a **machine-checkable property**: *Verification* step 2 extracts both spans from the base blob with `partition` and asserts each equals its new bullet, byte for byte, with nothing retyped anywhere. Any wording change destroys that check and replaces it with a reviewer's eye.
- *"The other checks here"* stays true after the move, and arguably gets sharper. In the base, *here* meant the checks named in the mirror bullet. In the new section it means the design-doc block check in the bullet below — which proves the intended edit landed, against the blob assertion that proves nothing else did. That is the contrast the sentence draws.

### Rejected: a framing sentence for the new section

Drafted as *"There is no test suite here, so a change's success criteria are its whole correctness surface. Both checks below bind **every** change — a plugin file, `CLAUDE.md`, `CONTEXT.md`, `scripts/`, an ADR — not only the mirrored pairs they were first written for."* Cut, because every clause is said better somewhere else:

- **The no-test-suite fact is `CLAUDE.md` line 3**, six lines above the insertion point: *"Markdown plus a couple of Python scripts — no build, test, or lint tooling beyond `scripts/check-sync.py`."* Restating it in a file whose cost model is per-line is the cheapest kind of bloat.
- **The scope claim is block 0's**, in the one place a mis-scoped reader is standing: *"it binds every change in this repo."* It is also carried structurally — a top-level unqualified section is repo-wide the way `## Workflow` is — and lexically, by the word `Always:` that opens the first bullet. Three signals; the sentence would be a fourth.
- **The enumeration was never measured.** *A plugin file, `CLAUDE.md`, `CONTEXT.md`, `scripts/`, an ADR* is the four out-of-scope changes' file kinds plus a guess, and a closed-looking list invites the reading that an unlisted kind — `.github/`, `marketplace.json` — is exempt. The classification table's population is changes **carrying a design doc** (`if not specs: continue`), so it licenses the hoist and measures nothing about a change with no design doc at all.
- **"not only the mirrored pairs they were first written for" is a changelog line.** It describes a state of the document that this change removes, to a reader who never saw it.

This is not *Rejected: pure option 2* by another route. That rejection is about deleting the mirror-specific **reason** from the bullet; block 0 keeps it verbatim in substance. What is cut here is a restatement, not an argument.

### Rejected: an ADR

`docs/adr/` records architecture decisions with live consequences (a duplication policy, a model-tier change, a topology invariant). *Where a convention is written down* has no consequence beyond the file it is written in. Same disposition as `963a66c` and `bf7676b` reached for the same reason.

### Rejected: enrolling `CLAUDE.md` or `CONTEXT.md` in `MIRROR_PAIRS`

Not an option, and named only because the issue's *Measured* paragraph mentions the absence. `MIRROR_PAIRS` declares pairs of files that must stay line-for-line identical; neither file has a second copy. There is nothing to enrol.

## The edit

Two plain (untagged) fenced blocks, shape `[1, 4]`. **Both were produced by applying the substitution to the base blob in `python3` and printing the result** — neither is retyped, and every byte carried over from line 9 came out of `git show 0445fb9:CLAUDE.md`. *Verification* step 2 re-proves that from git rather than asking to be trusted.

Every other fenced block in this document carries an info string (`sh`, `text`), so `read_blocks` cannot see it.

### Block 0 — the complete new `CLAUDE.md` line 9

Replaces line 9 in full. Everything through `must also verify against something *outside* the pair.` is byte-identical to the base; the two prescriptions are gone from the line, replaced by a forward pointer and the mirror-specific reason.

```
- **Some files are mirrored across `dev-flow` and `dev-flow-worktree` and must be edited in both.** `python3 scripts/check-sync.py` enforces what can be enforced mechanically — the `adversarial-review/SKILL.md` pair (line-for-line identical after `dev-flow-worktree` → `dev-flow`, minus declared exceptions) and the `description` duplicated between each `plugin.json` and `.claude-plugin/marketplace.json`. It runs on every PR. The pipeline `SKILL.md` pair and the two `README.md`s are too divergent to check mechanically — mirror those by hand. **`check-sync.py` proves the two copies agree with each other, never that either is correct**: text mangled identically in both sides passes it, and so does an edit missed on both. So any change to a mirrored pair, machine-checked or hand-mirrored, must also verify against something *outside* the pair. *Verifying a change*, below, is that verification, and it binds every change in this repo; the pair is where it is load-bearing rather than belt-and-braces, because a stray edit applied identically to both copies is the one place here where reading the diff cannot catch it — a doubled hunk is the expected shape there.
```

### Block 1 — the new `## Verifying a change` section

Four lines — heading, blank, two bullets, the shape `## Changing a plugin` already uses. Inserted **directly after line 12** (the blank line closing `## Changing a plugin`), followed by one blank line, so `## Workflow` — line 13 at the base — becomes line 18. Lines 3 and 4 of the block are the base line 9's two prescription spans, each prefixed with `- ` and otherwise byte-identical. The section carries no framing prose (*Rejected: a framing sentence for the new section*).

```
## Verifying a change

- **Always:** grep for the exact phrases the edit removes, expecting no hits, and assert that every file the edit touches is byte-for-byte its merge-base blob (nothing, for a file it creates) with exactly the intended edit applied. The other checks here prove that edit landed; only this one proves nothing else did.
- **When the change has a design doc** that gives replacement or inserted text as fenced blocks: also add a short `python3` check that re-reads those blocks from the design on disk, never retyped, asserting each appears verbatim in its target and, for an insertion, directly after its anchor line. Write that check per change — the block-to-file mapping and the assertions differ every time, so there is no shared runner to call. The *reader* is not per change: run `python3 scripts/design_blocks.py <design>` to get the block shape and indices, then have the check `sys.path.insert(0, "scripts")` and call `read_blocks(<design>, <shape>)` — it re-reads the blocks and exits non-zero if the shape moved — instead of re-typing the reader.
```

Two shape notes, because both are load-bearing for the checks below:

- **The list is tight** — no blank line between the two bullets — matching every other list in `CLAUDE.md`.
- **The block carries no leading or trailing blank line.** The separating blank before `## Workflow` is supplied by the insertion, not by the block, so a formatter or a reviewer trimming edge blanks inside a fence cannot silently change the shape. *Verification* step 2 asserts the inserted span is exactly `block 1 + [""]`.

### The phrase this edit removes

The junction between the mirror bullet's punchline and the first prescription:

```text
pair. **Always:**
```

At `0445fb9` it appeared in exactly one file outside `docs/superpowers/` — `CLAUDE.md` — and in four prior records inside it. The first half is the premise that lets *Verification* steps 1 and 2 discharge the removed-phrase grep between them; the second is why step 1's scope equality carries `':!docs/superpowers/'`:

```sh
git grep -c -F 'pair. **Always:**' 0445fb9 -- . ':!docs/superpowers/'
git grep -c -F 'pair. **Always:**' 0445fb9 -- docs/superpowers/
```

```text
0445fb9:CLAUDE.md:1

0445fb9:docs/superpowers/plans/2026-07-27-gh-7-review-depth-plan.md:1
0445fb9:docs/superpowers/specs/2026-07-27-gh-7-review-depth-design.md:1
0445fb9:docs/superpowers/specs/2026-08-02-gh-24-design-block-reader-design.md:1
0445fb9:docs/superpowers/specs/2026-08-02-gh-32-33-claude-md-conventions-design.md:1
```

## Length

`CLAUDE.md` is read in full by every contributor and every agent working this repo, so length has a real cost. This change is a **hoist**, not an addition: the two prescriptions move rather than duplicate, and no wording is expanded. What is genuinely new is a heading, the forward-pointer sentence on line 9, and the blank lines the section needs. A framing sentence for the section was drafted and cut (*Rejected: a framing sentence for the new section*) — its no-test-suite opener restated line 3, and its scope claim restated block 0's.

The file goes **29 → 34 lines**. Both numbers are derived: 29 by `git grep -c '' 0445fb9 -- CLAUDE.md`, which printed `0445fb9:CLAUDE.md:29`; 34 by *Verification* step 2, which asserts it rather than trusting it. **No word count of this change's own replacement text is stated anywhere in this document**, which is how the own-text branch of *Measurements are derived, not typed* is satisfied without adding a check that a review rewrite would falsify (A8).

The search for offsetting cuts was run and found nothing worth taking; recorded so it is not re-run. The design-doc clause's tail — the `design_blocks.py` discovery command and call form — is the obvious target, and `bf7676b`'s own *Length budget* already refused it for reasons that have not changed. This document has an additional one: cutting it would break the byte-identical hoist that makes step 2's *moved, not rewritten* assertion possible.

## Assumptions

- **A1. Targets as of `0445fb9`.** `CLAUDE.md` line 9 is the mirror bullet; line 12 is the blank line closing `## Changing a plugin`; line 13 is `## Workflow`. The implementation matches on **text, not line number**: step 2 reconstructs the whole file from its merge-base blob, so a base that moved and shifted the lines fails loudly instead of editing the wrong one.
- **A2. No test framework exists in this repo.** *Verification* is the whole correctness surface. `CLAUDE.md` line 3 already states the underlying fact — *"no build, test, or lint tooling beyond `scripts/check-sync.py`"* — which is why the new section does not restate it.
- **A3.** `claude plugin validate .` emitting exactly 8 `No author information provided` warnings and exiting 0 is the expected pass state, per `CLAUDE.md`.
- **A4. No plugin file changes, so no version is bumped.** `CLAUDE.md` sits outside `plugins/`, ships into no version-keyed cache, and is read at edit time rather than into any model invocation. A conclusion, not a deferral; step 1's file-scope equality asserts it, because the reflex is to bump.
- **A5. This is not a no-change ruling.** #39 ships text and closes on merge, so there is no separate issue-close comment to write — the PR body carries the ruling. If a review flips it to no-change, *The decision* becomes the closing comment verbatim and both blocks are dropped.
- **A6. `scripts/design_blocks.py` needs no edit.** Its docstring already claims the wider scope; the hoist makes that claim true. A conclusion, not a deferral (*The repo has already written the wider scope down*).
- **A7. Text assertions use `git grep`, not bare `grep`** — under Claude Code's Bash tool bare `grep` is a ugrep-backed shell function whose output layout is not reliable for per-file assertions. Exact assertions are made in `python3`, where they are byte-exact.
- **A8. This design's own plain fenced blocks are 0 and 1, shape `[1, 4]`.** No expectation below depends on a block's *character* content except through assertions that derive the expected side from git, so a review that rewrites block 0's new tail leaves every check runnable as written. Block 1 has no rewritable prose left — a heading and two verbatim-hoisted bullets, all three pinned by step 2. A review that adds or removes a **line** in either block changes the shape and trips step 0, which halts. The one number in this document that describes the post-edit tree — 34 lines — is asserted by step 2, not certified by prose.
- **A9. The design and plan are committed on this branch** (`docs: commit`), so *Verification* step 1's scope equality excludes `docs/superpowers/` with a pathspec — this document and its plan quote the removed junction and would otherwise sit in the changed set.
- **A10. `origin/main` is fetchable at implementation time.** Steps 1 and 2 resolve the base from it and fail loudly — naming the command, its exit status and git's message — rather than silently comparing against a stale ref.

## Out of scope

Hard-excluded. A proposal touching any of these is a blocker, not a design.

- **`plugins/`, `.claude-plugin/`, and every `plugin.json`** — no plugin text changes and no version moves (A4). Option 3 is rejected on the merits, not deferred (*The option-3 question, answered*), so this is a conclusion. The removed-phrase grep's severable **additive** echo into `plugins/` is a different question, filed as **#54**; it would add to `plugins/` rather than remove from `CLAUDE.md`, so it changes nothing here either way (ground 4).
- **`scripts/`** — no change. `design_blocks.py` is *used* by step 2 and not modified, and its docstring becomes true by this change rather than needing one (A6). `check-sync.py` is untouched: `MIRROR_PAIRS` is unchanged, no `description` changes, and neither mirror-pair file is in this change.
- **`CONTEXT.md`** — untouched, and **no edit is implied**. This change coins no repo concept. The nearest glossary entries are **Mirror pair** and **Hand-mirrored pair**, and block 0 uses both terms in exactly the sense those entries define, on a line that already used them. *Verification*, *check* and *prescription* are ordinary vocabulary, not shapes this repo reasons about, and the glossary defines shapes rather than one row per word.
- **`docs/adr/`** — no ADR is warranted (*Rejected: an ADR*).
- **`.claude-plugin/marketplace.json`** — untouched, because no `description` changes.
- **`.github/`** — no CI change.
- **The `## Changing a plugin` heading itself** — not renamed. The mis-scoping it causes is fixed by moving the prescriptions out from under it; the five bullets that remain (version bump, new plugin, mirrored files, `claude plugin validate`, load local edits) are all genuinely plugin-scoped, so the heading is correct for what is left.
- **The wording of the two prescriptions** — moved byte-identically (*Rejected: rewriting the prescriptions while moving them*). A proposal to improve either sentence's phrasing belongs in its own change, where it can be reviewed as a content change rather than smuggled through a relocation.
- **Every pre-existing file under `docs/superpowers/`** — prior records, four of which legitimately contain the phrase this edit removes.

## Verification

Every command runs from the repo root, after the edit unless stated. The base is `git merge-base origin/main HEAD` — computed, never hardcoded, so it stays correct if `main` advances or the branch is rebased; it resolves to `0445fb9` today.

**Every step that consumes the computed base — 1 and 2 — passes it to `git` as an `argv` element from `python3`, never through a shell.** That is *Command discipline*'s rule for computed refs, landed at `0445fb9`, applied here: `git merge-base` prints nothing on failure (exit 128 for an unresolvable ref, exit 1 and total silence when the histories share no ancestor), so an unquoted `$(…)` would degrade a base comparison into a working-tree-vs-index one that passes on a branch committed per task. There is **no `$(git …)` substitution anywhere below**; the `0445fb9`-pinned greps elsewhere in this document take a **literal** SHA, which is not a computed ref.

Every step below can fail, and each one's red output is recorded rather than claimed. No step's output is human-read in place of an assertion, and no assertion sits behind an earlier short-circuit — steps 1, 2 and 4 collect every mismatch and print them all before exiting.

**0. Block shape — asserted, not reported.** `design_blocks.py`'s CLI is a shape *reporter* that always exits 0; the *guard* is `read_blocks`, where the shape is a required argument and a mismatch is a `SystemExit`. This step calls the guard.

```sh
python3 - <<'PY'
import sys
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
DESIGN = "docs/superpowers/specs/2026-08-02-gh-39-verification-rules-home-design.md"
for i, b in enumerate(read_blocks(DESIGN, [1, 4])):
    print("  [%d] len=%d: %s" % (i, len(b), b[0][:66]))
print("shape guard: OK")
PY
echo "exit=$?"
```

Expect block 0 previewing the mirrored-files bullet and block 1 previewing `## Verifying a change`, then `shape guard: OK` and `exit=0`. Run against this document it printed:

```text
  [0] len=1: - **Some files are mirrored across `dev-flow` and `dev-flow-worktr
  [1] len=4: ## Verifying a change
shape guard: OK
exit=0
```

Anything else means this design was edited after the plan captured its shape — **stop and report**. The red run was produced for real, by copying this document to a scratch path outside the repo, splitting block 1's heading line in two there, and pointing the same program at the copy: it printed nothing on stdout and this on stderr, at `exit=1`:

```text
design code-block shape is [1, 5], want [1, 4]; stop and re-read the design
```

**1. File scope — exactly one file, and it is `CLAUDE.md`.** The `--name-only` set is compared for equality against the authorized list, so a stray edit to `plugins/`, a `plugin.json`, `scripts/`, `CONTEXT.md`, `docs/adr/` or `marketplace.json` fails the step **and names the offending path**. There is deliberately no `--stat` line and no `--quiet` companion: `--stat` asserts nothing, and a `--quiet` pathspec list over paths this equality already covers would pass vacuously. **The equality is also the `Always:` rule's removed-phrase grep, in a stronger form**, which is why no separate residue step follows it. `git grep`'s search domain is the tracked paths this `--name-only` set covers, and at `0445fb9` the removed junction sat in exactly one file outside `docs/superpowers/` — `CLAUDE.md` (*The phrase this edit removes*). A changed set equal to `['CLAUDE.md']`, plus step 2 pinning that one file byte for byte, leaves the phrase nowhere to reappear, so a standalone `git grep -F 'pair. **Always:**'` could not fail unless this step already had — the same vacuity that rules out the `--quiet` companion, and it would carry a pass condition no runner reads correctly, since `git grep` exits **1** on no match.

```sh
python3 - <<'PY'
import subprocess, sys
SCOPE = ["--", ".", ":!docs/superpowers/"]
WANT = ["CLAUDE.md"]
def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout
base = git("merge-base", "origin/main", "HEAD").strip()
print("base:", base)
changed = sorted(p for p in git("diff", "--name-only", base, *SCOPE).split("\n") if p)
if changed != WANT:
    print("file scope: FAIL -- changed %s, want %s" % (changed, WANT))
    sys.exit(1)
print("file scope: OK")
PY
echo "exit=$?"
```

Expect a `base:` line carrying a 40-character SHA, then `file scope: OK` and `exit=0`. Run at `0445fb9` with no edit applied, it printed:

```text
base: 0445fb983511fa3ca27badeb9e597b0b3b6ccb3f
file scope: FAIL -- changed [], want ['CLAUDE.md']
exit=1
```

A base that cannot be computed fails as one quotable line naming the command, its exit status and git's message — `FAILED: git merge-base origin/main HEAD -- exit 1, (no message)` for histories sharing no ancestor, where git itself says nothing.

**2. Reconstruction, design conformance, and the hoist is verbatim.** One program, three families of assertion, nothing retyped on either side:

- `CLAUDE.md` is **byte-for-byte its merge-base blob with exactly the intended edit applied** — line 9 replaced by block 0, and block 1 plus one blank line inserted after line 12 — which is what proves no other line moved, and is this repo's own `Always:` rule run on the change that relocates it;
- both blocks are read **from this design on disk** through the shared reader, never retyped, and block 0 occurs exactly once in the file;
- the two prescription spans are extracted **from the base blob** with `partition` and asserted equal to the new section's two bullets, byte for byte — the machine-checkable form of *moved, not rewritten* — while block 0 is asserted to start with the base line's head and to contain neither prescription marker any more.

Both markers are located with `partition`, so a base whose line 9 lost either one reports `MISMATCH:` and exits 1 like every other failure path rather than raising. Failures of the *producers* — `git`, `read_blocks` — are deliberately left to raise as themselves: they name the failing command, and no traceback can be mistaken for a pass. **The fence is unindented on purpose** — a `python3` heredoc indented under a list item is an `IndentationError`.

```sh
python3 - <<'PY'
import subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-02-gh-39-verification-rules-home-design.md"
TARGET = "CLAUDE.md"
BULLET_I, ANCHOR_I = 9, 12          # 1-based, at the base
WANT_LEN = 34                       # after the edit
HEADING = "## Verifying a change"
ALWAYS = "**Always:**"
WHEN = "**When the change has a design doc**"

def git(*args):
    return subprocess.run(("git",) + args, capture_output=True, text=True,
                          check=True).stdout
def split(text):
    out = text.split("\n")
    if out and out[-1] == "":
        out.pop()
    return out
base = git("merge-base", "origin/main", "HEAD").strip()
old = split(git("show", base + ":" + TARGET))
new = split(Path(TARGET).read_text(encoding="utf-8"))
blocks = read_blocks(DESIGN, [1, 4])
b0, sec = blocks[0][0], blocks[1]
bad = []

expected = (old[:BULLET_I - 1] + [b0] + old[BULLET_I:ANCHOR_I] + sec + [""] + old[ANCHOR_I:])
if new != expected:
    bad.append("%s is not its base blob with line %d replaced by block 0 and block 1"
               " plus one blank line inserted directly after line %d"
               % (TARGET, BULLET_I, ANCHOR_I))
if len(new) != WANT_LEN:
    bad.append("%s is %d lines, want %d" % (TARGET, len(new), WANT_LEN))
if new.count(b0) != 1:
    bad.append("%s holds block 0 %d times, want exactly 1" % (TARGET, new.count(b0)))

o9 = old[BULLET_I - 1]
head, m1, rest = o9.partition(ALWAYS)
mid, m2, tail = rest.partition(WHEN)
if not m1 or not m2:
    bad.append("base line %d does not carry both %r and %r -- the base moved"
               % (BULLET_I, ALWAYS, WHEN))
else:
    if sec[2] != "- " + (m1 + mid).rstrip():
        bad.append("the Always: bullet is not the base prescription moved verbatim")
    if sec[3] != "- " + m2 + tail:
        bad.append("the design-doc bullet is not the base prescription moved verbatim")
    if not b0.startswith(head):
        bad.append("block 0 changes text before %r; the hoist must keep the bullet's head"
                   % ALWAYS)
    if ALWAYS in b0 or WHEN in b0:
        bad.append("block 0 still carries a prescription marker; the hoist left a copy behind")

if sec[0] != HEADING:
    bad.append("block 1 line 1 is %r, want %r" % (sec[0], HEADING))
if sec[1] != "":
    bad.append("block 1's blank line moved; the section shape is not heading/blank"
               "/bullet/bullet")

for why in bad:
    print("MISMATCH:", why)
print("reconstruction:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expect exactly `reconstruction: OK` and `exit=0`. Extracted from this document and run at `0445fb9` with no edit applied, it printed **three** `MISMATCH:` lines and `exit=1`:

```text
MISMATCH: CLAUDE.md is not its base blob with line 9 replaced by block 0 and block 1 plus one blank line inserted directly after line 12
MISMATCH: CLAUDE.md is 29 lines, want 34
MISMATCH: CLAUDE.md holds block 0 0 times, want exactly 1
reconstruction: FAIL
exit=1
```

Three of the program's ten assertions, and the split is the interesting part. The three that fired are the only ones that read the **post-edit tree**. The other seven — the base still carrying both markers, the two verbatim-span comparisons, the head-prefix relation, the absence of both markers from block 0, the heading, the blank-line shape — compare the design's blocks against the **base blob** or against each other, so they were already green before the edit and stay green whatever the tree holds. That is the point of them: they fail only if a review rewrites a block, which is a failure the tree can never show.

The **green** run cannot be produced at design time, because producing it means applying the edit. What was produced instead, while this document was written, is the same program with `new` computed as the intended post-edit content rather than read from disk — every assertion green, `reconstruction: OK`, and the resulting file 34 lines with `## Verifying a change` at line 13, its two bullets at 15 and 16, and `## Workflow` at 18. If the shape guard trips instead (`design code-block shape is …`), **stop and report**: this design was edited after the plan captured its shape.

**3. `python3 scripts/check-sync.py`** — passes, with output identical to before the change. It reads none of the changed files; this step is a regression guard, not a claim about the edit.

```sh
python3 scripts/check-sync.py
echo "exit=$?"
```

Run against this tree it printed:

```text
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)
check-sync: all checks passed
exit=0
```

**4. `claude plugin validate .` — exit 0 *and* exactly 8 author warnings.** Both halves are asserted, because either alone passes vacuously: the command exits 0 while emitting warnings (A3), and a count assertion alone would pass on a run that errored out.

```sh
python3 - <<'PY'
import shutil, subprocess, sys
WANT_WARNINGS = 8
NEEDLE = "No author information provided"
if shutil.which("claude") is None:
    raise SystemExit("FAILED: claude is not on PATH; this step cannot run")
r = subprocess.run(["claude", "plugin", "validate", "."], capture_output=True, text=True)
n = (r.stdout + r.stderr).count(NEEDLE)
print("claude plugin validate: exit %d, %d author warnings" % (r.returncode, n))
bad = []
if r.returncode != 0:
    bad.append("claude plugin validate . exited %d, want 0" % r.returncode)
if n != WANT_WARNINGS:
    bad.append("%d 'No author information provided' warnings, want exactly %d"
               % (n, WANT_WARNINGS))
for why in bad:
    print("MISMATCH:", why)
print("validate:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Run against this tree it printed:

```text
claude plugin validate: exit 0, 8 author warnings
validate: OK
exit=0
```

Run with `WANT_WARNINGS = 7` and nothing else changed — the cheapest way to show the count is asserted rather than decorative — it printed:

```text
claude plugin validate: exit 0, 8 author warnings
MISMATCH: 8 'No author information provided' warnings, want exactly 7
validate: FAIL
exit=1
```

## Files the plan will touch

- **Modify:** `CLAUDE.md` — line 9 replaced by block 0 (verbatim, whole-line replacement), and block 1 plus one blank line inserted directly after line 12. Nothing else in the file.
- **Committed by dev-flow per `docs: commit`:** this design and its plan under `docs/superpowers/`.

Nothing else. No plugin file, no `plugin.json`, no `scripts/` file, no `CONTEXT.md`, no `docs/adr/`, no `.github/` file, no `marketplace.json`.

## PR

```text
Close #39 by giving the verification rules a repo-wide home and leaving the
mirror bullet the one reason that is genuinely mirror-pair-specific.

CLAUDE.md line 9's Always: pair and its design-doc block check are textually
scoped to changes touching a mirrored pair, and the repo applies them to
everything. Measured at 0445fb9, with the command in the design: of the ten
changes merged since 4e32e0e -- the commit that first wrote both clauses --
carrying a design doc, all ten prescribed the block-conformance check, and
four touched no mirrored file at all (CLAUDE.md, CONTEXT.md, scripts/,
.gitignore). The repo had already written the wider scope down a second time,
in scripts/design_blocks.py's docstring: "CLAUDE.md requires every change
carrying a design doc to add a python3 check". Two files disagreed; the hoist
makes the docstring true with no scripts/ change.

Both prescriptions move byte-identically into a new top-level section,
## Verifying a change -- the heading and the two bullets, no framing
prose, the shape ## Changing a plugin already uses. Nothing restates the
scope: a top-level unqualified section is repo-wide, the first bullet
opens with the word Always:, and the mirror bullet's punchline now points
forward and says it -- "it binds every change in this repo". That bullet
keeps its head unchanged and retains the argument that makes the rule
load-bearing there rather than belt-and-braces: a stray edit applied
identically to both copies is the one place here where reading the diff
cannot catch it, because a doubled hunk is the expected shape. A new
bullet under ## Changing a plugin was rejected -- the enclosing heading
mis-scopes the rule independently of the bullet's own sentence, and none
of the four out-of-scope changes touched a plugin.

Option 3 -- moving the rules into dev-flow's success-criteria guidance under
plugins/ -- is rejected on four measured grounds, and three of them are
independent of the mirror-pair motivation the issue asks about. The design-doc
clause names scripts/design_blocks.py and read_blocks, and no instrument token
of any kind appears under plugins/ today. Its precondition -- a design that
gives replacement text as fenced blocks -- is absent too: the word "fenced"
occurs nowhere under plugins/, so option 3 would ship this repo's prose-change
design convention to every repo dev-flow runs in. And outside a repo like this
one the byte-for-byte-merge-base-blob assertion has no machine-comparable
expected side, so it degenerates into "the diff equals the diff" -- exactly
what the clause landed by #40/#41 tells the same plugin's design correctness
seed to report as a criterion that cannot fail. What already crossed named no
instrument: Command discipline's criteria scope and "Measurements are derived,
not typed" name no repo path, script, mirror pair, or check to write. One
prescription still generalizes -- the removed-phrase grep -- but plugins/ is no
home for it either: CLAUDE.md is auto-loaded and binds every change made in
this repo, while a SKILL.md binds a run of that skill. An additive echo in
plugins/ is filed as #54 and changes nothing here.

CLAUDE.md only, 29 -> 34 lines. No plugin file is touched and no version is
bumped: CLAUDE.md ships into no cache.

Closes #39
```

## Spec self-review

- **Placeholders / TBDs:** none. Both replacement passages are given in full as plain fenced blocks; every criterion is runnable as written, with its expected green output and its recorded red output.

- **Every measurement this document states, and the command that printed it.** *Measurements are derived, not typed* requires the whole list, not a selection, so this is the whole list.

  **Of the tree at `0445fb9`, each with its command given beside the claim and re-run while this document was written:**

  | Measurement | Command |
  |---|---|
  | both markers entered `CLAUDE.md` at `4e32e0e`; the byte-for-byte sentence at `bf7676b` and the `read_blocks` tail at `963a66c`; three commits have touched the file at or after `4e32e0e` | the `git log` set under *The clauses, and where they sit* |
  | one occurrence of each marker in the whole file | the `python3 -c` counter in the same section |
  | 10 changes since `4e32e0e` carried a design doc; 10 of 10 wrote the block check; 4 of 10 touched no mirrored file, and 4 of those 4 wrote it | the classification program under *The repo applies them to every change* |
  | those 10 are every first-parent commit in the range, so the table has no remainder | `git rev-list --count --first-parent 4e32e0e..0445fb9` (printed `10`) |
  | `bf7676b` is 1 change back, `963a66c` 5 and `4e32e0e` 10 — the *"one, five and ten changes back"* in *Rejected: rewriting the prescriptions* | the same `git rev-list --count --first-parent`, with `bf7676b..0445fb9` (printed `1`) and `963a66c..0445fb9` (printed `5`) |
  | all 10 of the same designs prescribed a removed-phrase grep | the residue-grep program in the same section |
  | `design_blocks.py`'s docstring claims the wider scope, at line 4 | `git grep -n -F 'CLAUDE.md requires every change carrying a design doc' 0445fb9 -- scripts/` |
  | `MIRROR_PAIRS` holds one entry, `adversarial-review` | the `git grep -n -E` under *`MIRROR_PAIRS` holds one pair* |
  | no instrument token under `plugins/` — no output, exit 1 | the `git grep -c -i -E 'check-sync\|design_blocks\|…'` in *The option-3 question* |
  | *fenced* occurs nowhere under `plugins/` — no output, exit 1 | `git grep -c -i -F 'fenced' 0445fb9 -- plugins/` |
  | the falsifiability clause ships in both `adversarial-review` copies, one line each | `git grep -c -F 'a criterion that cannot fail is untestable' 0445fb9 -- plugins/` |
  | the removed junction in one file outside `docs/superpowers/`, four inside | the `git grep -c -F` pair under *The phrase this edit removes* |
  | `CLAUDE.md` was 29 lines | `git grep -c '' 0445fb9 -- CLAUDE.md` |

  The `Always:` byte-for-byte clause's two exercises — `bf7676b`'s own voluntary one, recorded in its A8, and `0445fb9`'s — are read off the same classification table plus the `bf7676b..0445fb9` count of `1`: `bf7676b` wrote the clause and exactly one change has merged since. No separate number is claimed.

  **Of this document's own replacement text:** the `[1, 4]` shape, printed by step 0's guard, and the post-edit length of 34 lines, asserted by step 2. **No word count of this change's own replacement text is stated** (A8), so there is nothing here a review rewriting a block's prose can leave stale.

  **Recorded command output:** step 0's green run and steps 3 and 4's green runs were produced against this tree while the document was written; step 0's red by copying this document to a scratch path outside the repo and splitting block 1's heading line there, and step 4's red by re-running the same program with `WANT_WARNINGS = 7`. Both scratch artifacts were deleted afterwards. Steps 1 and 2's red runs were produced by running each at `0445fb9` with no edit applied — step 1 printed `changed []`, step 2 **three** `MISMATCH:` lines. A first draft of this review said four for step 2; running it corrected the count and the explanation beside it. A first draft also reported 9 of 10 for the removed-phrase grep, on a predicate matching only two of the three labels the designs use; widening it to the third (`a94f60a`'s *"Removed phrase"*) made it 10 of 10, and the corrected predicate is the one shown. Step 2's green path was exercised by running the same program with `new` computed as the intended post-edit content instead of read from disk, which is the only form available before the edit exists. A first draft of *The clauses, and where they sit* read the two marker `-S` probes as dating the clauses' whole text to `4e32e0e`; probing each added sentence separately corrected it to three commits, and the probes shown are the corrected set.

- **Internal consistency:** block 0 is the base line 9's head plus a new tail, with both prescription markers gone — step 2 asserts the prefix relation and the absence. Block 1's lines 3 and 4 are the base line 9's two prescription spans verbatim, which step 2 derives from the base blob rather than from this document. The `[1, 4]` shape, the anchor lines 9 and 12, the one-file scope, and the 29 → 34 line counts agree everywhere they appear, and 29 + 4 + 1 = 34 is the arithmetic the insertion implies.

- **Scope:** one file. Step 1 checks it by file; step 2 checks that file line by line against its merge-base blob. `plugins/`, `scripts/`, `CONTEXT.md`, `docs/adr/`, `.github/`, `marketplace.json`, the `## Changing a plugin` heading and the prescriptions' own wording are each named in *Out of scope* with a reason, and each is a conclusion rather than a deferral.

- **Ambiguity:** the one place a fresh implementer could go wrong is scope — the removed junction and both blocks legitimately appear in this document. Step 1 carries `':!docs/superpowers/'`; every backward-looking grep is pinned to `0445fb9`. The second is the insertion point: block 1 goes after line 12, the blank line, and supplies no edge blank of its own, so the inserted span is `block 1 + [""]` — stated in *Block 1*, in *Files the plan will touch*, and asserted by step 2.

- **Positions taken:** the prescriptions get a repo-wide home in `CLAUDE.md`, as a new top-level section rather than a new bullet, carrying no framing prose, and the mirror bullet keeps the mirror-specific reason and gains a forward pointer that states the repo-wide scope. Option 1 is rejected on the 4-of-10 measurement plus the `design_blocks.py` docstring contradiction; option 3 is rejected on four grounds, three of them independent of the mirror-pair motivation the issue flags, and its one severable half — the removed-phrase grep, which `plugins/` could echo but never house — is filed as #54 rather than decided here. The wording of both prescriptions is deliberately unchanged, which makes *moved, not rewritten* a machine-checked property rather than a reviewer's judgment. No ADR, no `scripts/` change, no version bump. Nothing is left for the implementer to decide.
