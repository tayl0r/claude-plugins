---
dev-flow:
  slug: gh-40-41-verification-blocks
  stops: [pre-merge]
  docs: commit
---

# gh-40/41 — what a design's success criteria may claim, and how their commands are written

Close **#40** and **#41** by writing down two rules the pipeline never stated, and one check its review tier was not making:

- a design's or plan's **success criteria** are governed by *Command discipline* — and, where a criterion consumes a **computed** git ref, by an `argv` form rather than a shell chain;
- a **measurement** an artifact states was printed by a command its author ran, or it is cut — re-derived in the artifact's own criteria when it measures the artifact's own replacement text, and carrying its base-pinned command beside the claim when it measures the tree before the edit;
- and the design/plan correctness seed looks for criteria that **cannot fail**, not only for criteria that are missing.

Three passages change: one line in the machine-checked `adversarial-review/SKILL.md` mirror pair, and, in each hand-mirrored pipeline `SKILL.md`, one appended sentence-group on the *Command discipline* bullet plus one new Cross-Cutting bullet.

## Decomposition

Two independent scope assessors — one asked to test a split hypothesis, one asked to steel-man bundling — converged on the same three groups, and the orchestrator ruled. Recorded here so it is not re-opened:

| Group | Issues | Why it is one change | Sequencing |
|---|---|---|---|
| **A — this change** | #40, #41 | One subject: what a design's success criteria may claim and how their commands are written. Same originating review (#32/#33, findings B1 and C1), same two file pairs, and both review-checklist clauses land in the **same sentence** of `adversarial-review/SKILL.md` — line 29 at `bf7676b`. Splitting them would be two edits to one sentence in two machine-checked copies. | Now. |
| **B** | #39 | A housing question with three candidate homes, not a defect. The issue says outright that *"Choosing needs its own evidence, notably whether option 3's guidance can carry a rule whose sharpest motivation is mirror-pair-specific."* | **After** this change. Option 3 names a home in dev-flow's `SKILL.md` that does not exist yet; this change creates the first pipeline-general success-criteria text there, which is the evidence that makes option 3 evaluable against shipped text rather than against a hypothetical. |
| **C** | #43 | Two pipeline-vocabulary gaps (a checkbox that must run at a stage boundary; a merge gate that re-verifies only the marker and CI). The issue says of itself *"Filing as a question with evidence, not a demanded fix — the design work is not done here"*, and both halves end *"Candidate directions, none decided."* | Its own design pass. |

**Non-goal: this change does not decide #39.** `CLAUDE.md` is untouched and stays the home of every repo-local instrument.

### The strongest argument against the split, answered

#41's clause — *re-derive a measurement of your own text, never hand-type it* — **is** `CLAUDE.md` line 9's design-block-conformance principle, generalized. So landing it in `plugins/` could settle #39's option 3 by precedent, without the evidence #39 says the choice needs.

The line this change draws, and holds:

- **What stays in `CLAUDE.md`, untouched: every instrument.** `scripts/design_blocks.py` and the `read_blocks` call form, the byte-for-byte-merge-base-blob assertion, the removed-phrase grep, and the mirror-pair framing that scopes them. None of the three is mentioned, moved, generalized, or referred to by the text this change lands.
- **What lands in `plugins/`: no instrument at all.** Both new passages state a property a criterion or a stated number must have — *able to fail*, *derived rather than typed*, *pinned and past-tense* — and name no repo path, no script, no mirror pair, and no check to write. They are true in a repo with no `scripts/`, no `check-sync.py` and no duplicated plugin.

That is a testable boundary, not a slogan: a proposal to reference `design_blocks.py`, `read_blocks`, the merge-base-blob assertion or the removed-phrase grep from `plugins/` is out of scope here and is #39's to make. #39's three options are all about relocating *instruments* whose sharpest motivation is mirror-pair-specific; all three remain open, and this change removes none of them.

It also does not silently pre-answer #39 in the other direction. The evidence it produces cuts both ways and is worth having either way: after this change, dev-flow's `SKILL.md` contains success-criteria guidance for the first time, so #39 can ask its question — *can this text carry the mirror-pair rules too?* — against a real passage with a real length cost, rather than against an empty section.

One asymmetry, named rather than glossed: the passage lands in **Cross-Cutting Concerns**, which is where an option-3 implementation would append. That lowers option 3's *price* relative to options 1 and 2 — a bullet beside an existing one, not a new home — without naming an instrument. #39 should weigh it as a fact about cost, never as a precedent for merit.

## What the two issues ask for

Measurements in this section are of the tree **before** this change and are pinned to `bf7676b`, this branch's base. Each is given with the command that printed it, each command was run while this document was written, and no number appears that its command's output does not show.

### The gap #40 reports is real and is a scope gap, not a missing rule

At `bf7676b`, neither pipeline `SKILL.md` mentioned the word *verification* or the phrase *success criteria* even once. The only matches anywhere under `plugins/` were `adversarial-review/SKILL.md` lines 29 and 30, in both copies:

```sh
git grep -n -i -E 'verification|success criteri' bf7676b -- plugins/
```

Four lines, two files. So the pipeline that *commissions* a design's criteria said nothing about them, while *Command discipline* — the bullet that works the hazard out in full, down to `merge_base=$(git merge-base HEAD "origin/<baseRef>")  # failure or empty halts` — was scoped to the commands the pipeline itself runs.

What that let through is in #40: a criteria block whose two `git` commands took their base from an unquoted `$(git merge-base …)`, so an unresolvable `origin/main` degraded both into working-tree-vs-index comparisons that pass on a branch committed per task, and printed `untouched: OK`.

### #40's comment supersedes the naive fix, and its narrowing is wrong in two places

The naive fix — extend *Command discipline* verbatim, so criteria capture, validate and quote the base — prescribes a form the runner refuses. The comment's evidence is correct; its narrowing of *which* forms are refused is not. Re-measured today from this worktree, in this runner:

| Command | Result |
|---|---|
| `git log -1 --format=%H bf7676b` | runs |
| `X=bf7676b && git log -1 --format=%H "$X"` | **runs** |
| `X=bf7676b; git diff --quiet "$X" -- plugins/ && echo ok` | **runs**, prints `ok` |
| `BASE=$(git merge-base HEAD origin/main)` alone | runs (and the value is then lost — shell state does not persist between tool calls) |
| `BASE=$(git merge-base HEAD origin/main) && git diff --name-only "$BASE"` | refused |
| `BASE=$(date) && echo "$BASE"` | **refused** |
| `echo hi && echo $(date)` | **refused** |
| `git log -1 --format=%H $(git merge-base HEAD origin/main)` | refused |
| `python3 - <<'PY' … subprocess.run(["git", …]) … PY` | runs |

Every row above was run again while this document was written, and the table records what each one printed. The refused rows all printed the message #40's comment quotes, whose operative clause is *"this command is too complex to verify that it stays inside the worktree; break it into plain, separate commands. Refusing to run it"* — the runner then names the worktree it is isolated in.

Two corrections to the comment, neither of which changes its conclusion:

1. **It is not about `git`.** `echo hi && echo $(date)` is refused, and it contains no `git`. The predicate is a **command substitution in a line that is more than one simple command**, whatever the commands are.
2. **It is not about variables.** `X=bf7676b; git diff --quiet "$X" -- plugins/ && echo ok` runs. A `git` argument coming from a shell *variable* is fine; the comment's claim that this is refused "including with a hardcoded SHA" is false as measured.

The conclusion survives intact and is if anything stronger. Capture-validate-quote needs the capture and its consumer in **one** tool call — shell state does not persist between calls — and that is exactly the shape refused. The tool's own advice ("break it into plain, separate commands") reintroduces the original hazard, because the base would then have to be hardcoded. Passing the ref to `git` as an `argv` element from `python3` retires word-splitting **by construction** — an empty base is `fatal: bad revision ''`, not a different valid command — and is never refused.

### The second half of #40: a criterion must be able to fail

The same criteria block claimed *exactly one file changed* and asserted nothing: `--stat` is human-read, and the accompanying `--quiet` pathspec list enumerated only paths the change had already hard-excluded, so it passed vacuously. `adversarial-review`'s design/plan prose checklist looks for *"missing or untestable success criteria"* — the words are there, and they did not fire, because a criterion that is *present and running* does not read as untestable.

#40's comment adds the sharper instance, and it is the one that shapes the wording: `git diff --quiet` writes zero bytes on stdout **and** stderr, on pass and on fail, so the prose keeping it — *"fails with the offending path rather than a generic set mismatch"* — was false; and in an `&&` chain it was **unreachable** on the very case it was kept for, because a version bump fails the `--name-only` equality one line earlier and short-circuits it. So the checklist item needs both halves: a criterion must be able to fail, **and** prose asserting a criterion's diagnostic value is itself a measurement to check.

### #41: measurements, and the two different rules it needs

#41's instance: the gh-32/33 design stated three numbers about its own replacement text — *"the shortest bullet in the section"* twice, and *"Major stays named, in seven words"* — and all three were false, two of them the receipt for the length-budget argument the change leaned on. Its *Spec self-review* certified them unchecked.

The issue instructs weighing the cheaper variant first: **forbid derived numbers in design prose unless they carry an argument, since most do not.** Weighed, and rejected as the rule — kept only as advice about which numbers are worth the trouble. It fails on its own evidence: the numbers that failed were exactly the ones that *did* carry an argument, since they were the length-budget receipt. A rule that only forbids decorative numbers leaves the load-bearing ones hand-typed, which is the case that hurt. Worse, "does it carry an argument?" is a judgment call the author makes about their own text, and the author who typed the number is the one least likely to rule against it. So the rule keys on nothing the author decides: **the number came out of a command that was run, or it is cut.** The cheap way to satisfy that is to state fewer numbers, which is the issue's variant arriving as a consequence rather than as the rule.

#41's comment adds a second sub-class that the issue's own remedy would get **wrong**. The gh-38 design asserted that `operative` and `framing` had zero hits in shipped text — true when written at `b4b5d1c`, false against the merged tree, because the edit itself coins `operative`. Mechanizing that claim post-edit, as "assert it in the design's own criteria" prescribes, produces a **red criterion for a correct design**. So there are two rules — both requiring the number to come out of a command that was run — and which applies is decided by *what is being measured*, not by when the measurement was taken:

| What the number measures | Rule | Why |
|---|---|---|
| The artifact's **own replacement text** (word counts, line counts, "the shortest bullet") | **Re-derive** it in the artifact's own success criteria, or do not state it | The text is under the author's hand and can move again; only a check that reads it from disk stays true |
| The **tree before the edit** (what a grep returned at the base, what a file used to contain) | **Pin** the command to the base revision (`git grep … <base> -- …`), give it beside the claim, state the claim in the **past tense at that revision**, and state no number its output does not show | The edit is what changes the answer. Pinned, the command reproduces the result forever — but only what it prints is derived; a number typed alongside it is not |

The line between them is sharp and needs no judgment call: if the change's own text can appear in the result, the measurement is of the artifact's own text; if it cannot, because the revision predates the change, it is of the pre-edit tree.

## The placement question

Four clauses want a home. Two homes are available, and they are not interchangeable:

- the **pipeline `SKILL.md` pair** owns Stage 1's design protocol and the Cross-Cutting *Command discipline* bullet — the **authoring** side, which #41 names explicitly (*"The gap is on the authoring side"*). It is **hand-mirrored**: `check-sync.py` does not know the pair exists, so drift there is silent.
- **`adversarial-review/SKILL.md`** owns the seed checklists — the **detection** side. It is a **machine-checked** mirror pair, one edit verified by `scripts/check-sync.py`, and it runs in both pipelines *and* standalone.

### Approach A — everything in `adversarial-review`

Cheapest by a wide margin: one sentence, one machine-checked pair, no hand-mirroring, and it reaches standalone reviews. **Rejected**, on two grounds:

1. *Command discipline* is a rule about how the pipeline's commands are written, and it lives in the pipeline files. Restating it in `adversarial-review` would duplicate a rule across two skills — and `adversarial-review` reviews artifacts in repos that have no dev-flow at all, where a rule about the pipeline's own git ref discipline has no referent.
2. A findings-only seed can only report. If the only home is detection, every design starts non-conformant and is repaired per instance by review. The rubric is explicit: *prefer correct-by-default seams over designs where each caller must remember a flag, ordering, or manual step.* The authoring rule is the seam; the checklist is the net.

### Approach B — split by side: authoring in the pipeline pair, detection in `adversarial-review` — **chosen**

- **Pipeline pair** gets the two authoring rules: the *Command discipline* scope extension plus the `argv` form (block 1), and one new Cross-Cutting bullet for measurements (block 2).
- **`adversarial-review`** gets one extension of the existing enumeration on line 29 (block 0), covering both halves of #40's second gap and the detection counterpart of #41.

Line 30 — the plan-mode correctness seed — reads *"The prose checklist above, plus plan-specific checks"*, so the design-mode edit reaches plan mode with no second edit. That is worth naming, because #40's comment records that the false diagnostic-value prose *"was mirrored unchanged into the plan"*: the one place the defect propagated is covered by the one line that is already being changed.

### Approach C — everything in the pipeline pair

**Rejected.** The falsifiability clause belongs beside *"missing or untestable success criteria"*, which already exists in `adversarial-review` and already tried to catch this; putting a second, competing statement of the same idea in a different file leaves two places to read and one of them wrong. And it would put the whole change in the pair that nothing checks mechanically, when half of it fits in the pair that `check-sync.py` verifies.

### Why the detection side gets a measurement clause at all

The argument against: #41 records that *both* adversarial-review seeds caught the false numbers independently, so the review tier already works, and a rule the tier already discharges does not earn its place.

The argument for, which wins: what the seeds caught was a number that was **false**. A number that is **true today and unpinned** contradicts nothing and reads clean — #38's `operative` claim was caught only at the PR stage, one full stage after the design and the plan had both shipped it. Moving that catch to the design-mode checklist costs one clause in a sentence already being edited and buys back two stages. The clause is worded to catch that case specifically — *"measurements the artifact states that no command it gives actually printed"* — not to restate "check the arithmetic", which the checklist's *internal contradictions* item already covers. An unpinned true number is a number no command in the artifact printed **where the edit falsifies it** — #38's `operative` precedent — but not where the edit leaves it standing, which is block 2's to catch rather than block 0's; the wording reaches the first case without naming pinning, which is an authoring remedy rather than a detection test.

### Why no new named pass, and no criteria contract

`adversarial-review` has a shape: a heavy check becomes a named paragraph below the table with its own trigger and reportability rule (*Input-contract completeness*, *Terminology collision and drift*), while a cheap check is an item in the table cell's enumeration. Both new clauses are cheap: they have no trigger to state (every design has criteria and every design states numbers) and no false-positive class to fence off. They join the enumeration. A named pass would add a heading, a trigger sentence and a reportability rule to say what fits in one clause.

Likewise, the pipeline pair gets no new "criteria contract" section. The Cross-Cutting section already holds one-bullet cross-cutting rules — *Command discipline* is one — and a new section would have to restate scope and motivation that the bullet inherits for free.

## The edit

Three passages, given below as plain (untagged) fenced blocks. **Every one was produced by applying the substitution to the file on disk in `python3` and printing the result** — none is retyped. *Verification* step 2 re-proves that from git rather than asking to be trusted: it reads these blocks back off this document and reconstructs each target file from its merge-base blob.

Every other fenced block in this document carries an info string (`sh`, `python`, `text`) and is therefore invisible to `read_blocks`, which reads plain blocks only. The shape is `[1, 1, 1]`: three single-line blocks, in the order below. A rewrite that splits one of them into two lines trips step 0 and halts.

### Block 0 — `adversarial-review/SKILL.md` line 29, both copies

Replaces line 29 in full, in `plugins/dev-flow/skills/adversarial-review/SKILL.md` and `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md`. At `bf7676b` the two copies' line 29 was byte-identical (no `dev-flow` token appears in it), so one block serves both files and `check-sync.py`'s canonicalization has nothing to do.

Everything outside the enumeration is unchanged; the edit adds one parenthesised gloss to an existing item — *missing or untestable success criteria* — and one new item after it, before *plus the input-contract completeness*.

```
| **design** | The design rubric (below) *is* the lens, applied adversarially to the proposed approach. | A prose-integrity checklist: placeholders/TBDs, internal contradictions, planning-blocking ambiguity, unstated assumptions, missing or untestable success criteria (a criterion that cannot fail is untestable: human-read output standing in for an assertion, a scope that excludes everything it would catch, a step unreachable behind an earlier short-circuit), measurements the artifact states that no command it gives actually printed (of its own replacement text, of the tree it changes, or of what a command it prescribes outputs) — plus the input-contract completeness and terminology collision-and-drift passes (below). |
```

**Why both glosses are parenthesised rather than em-dashed.** The first draft of this block put three em-dashes at one visual level doing three different jobs — opening the falsifiability gloss, closing it, and carrying the original *— plus* junction — so a reader could not tell where the inner gloss ended. Parenthesising both glosses restores what line 29 already was: one flat comma-list of checklist items, joined to the named passes by a single `— plus`.

The three failure shapes named inside the first gloss are the three that were measured, not a taxonomy: `--stat` output nobody asserts on, a pathspec list enumerating only already-excluded paths, and a `--quiet` assertion short-circuited by the `&&` before it. #40's comment's second half — the `"fails with the offending path"` prose about a command that writes zero bytes — is deliberately **not** a fourth failure shape here. It is not a way a criterion cannot fail; it is a number-shaped claim about a command's behaviour that nobody checked, so it belongs to the measurement item, which is generalised to cover it: *"or of what a command it prescribes outputs"*.

The phrase this edit removes, for the residue grep, is the junction it splits:

```text
success criteria — plus the input-contract
```

At `bf7676b` that phrase appeared in exactly two files outside `docs/superpowers/` — the two copies of line 29 — and in four prior design and plan records inside it, which is why the grep in *Verification* step 3 is scoped. Both counts come from this pair of commands, one match per file listed:

```sh
git grep -c -F 'success criteria — plus the input-contract' bf7676b -- . ':!docs/superpowers/'
git grep -c -F 'success criteria — plus the input-contract' bf7676b -- docs/superpowers/
```

```text
bf7676b:plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md:1
bf7676b:plugins/dev-flow/skills/adversarial-review/SKILL.md:1

bf7676b:docs/superpowers/plans/2026-07-27-gh-7-review-depth-plan.md:1
bf7676b:docs/superpowers/specs/2026-07-27-gh-7-review-depth-design.md:1
bf7676b:docs/superpowers/specs/2026-07-28-gh-16-terminology-collision-design.md:1
bf7676b:docs/superpowers/specs/2026-07-29-gh-20-diff-terminology-design.md:1
```

### Block 1 — the complete new *Command discipline* bullet, both pipeline files

Replaces `plugins/dev-flow/skills/dev-flow/SKILL.md` line 276 and `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` line 270 — the same bullet, byte-identical in both files at `bf7676b`. This is a **pure append**: every byte of the existing bullet is carried over unchanged and the new text is added at the end, so **the edit removes no phrase**. *Verification* step 2 makes the stronger assertion a removed-phrase grep cannot: that the base line is a strict prefix of this block.

```
- **Command discipline:** resolve git-internal paths through git (`git rev-parse --git-path …`), never as `.git/...` literals — `.git` is a file, not a directory, in any linked worktree. Capture, validate non-empty, and quote any command output a later command consumes; a failed producer halts the run and never substitutes an empty string — an empty variable silently *inverts* git predicates (an empty `<marker-sha>` turns `git rev-list <marker-sha>..HEAD` into the empty range `HEAD..HEAD`, a false "every commit matched"; an empty `<branch-ref>` turns `git log <default-ref>..<branch-ref>` back into a `HEAD`-relative scan, a false "no trailer"; an empty `<merge-base>` turns `git cat-file -e :<path>` into an index lookup that falsely succeeds). **This governs the success criteria a design or plan emits as well as the pipeline's own commands** — in a repo with no test suite they are the whole correctness surface. There, a step that consumes a **computed** git ref runs its `git` calls through `python3`/`subprocess` with the ref as an `argv` element rather than a shell chain: `argv` cannot word-split, so an empty ref is `fatal: bad revision ''` rather than a different valid command. Capture-validate-quote stays the rule everywhere else.
```

Three wording choices worth recording:

- **"success criteria", not "`## Verification` block".** At `bf7676b` the designs under `docs/superpowers/specs/` used three different headings for it, and the oldest ones used none at all. A rule keyed to a heading name would silently exempt every design that used a different one. This command prints all three counts:

  ```sh
  git grep -h -E '^## (Verification|Success criteria|Acceptance criteria)' bf7676b -- docs/superpowers/specs/ | sort | uniq -c
  ```

  ```text
     2 ## Acceptance criteria
     3 ## Success criteria
     8 ## Verification
  ```

- **"a **computed** git ref"**, not "a git ref". A criterion pinned to a literal SHA runs as a plain shell command and is not in scope — which matters, because the pre-edit-tree half of block 2 tells authors to pin, and a pinned grep must stay writable as one line of shell.
- **The runner-refusal clause is cut, not demoted to secondary.** An earlier draft shipped it after the by-construction reason; it now ships in neither block. The refusal's condition is a **harness sandbox** — the message names the worktree the *agent* is isolated in, the fact the table under *#40's comment supersedes the naive fix* records — which is a different sense of *worktree* from the pipeline's own, the one each pipeline file already fixes for its reader. In `dev-flow-worktree`'s file the phrase therefore reads as the pipeline's own worktree, where it is wrong; `dev-flow`'s file states outright that it uses no worktree, so a positive "worktree-isolated" claim collides with its own defining text. The by-construction argument carries the rule alone (A6), and the refusal stays where it is evidence rather than instruction: in this design, as the reason the naive fix is rejected.

### Block 2 — a new Cross-Cutting bullet, inserted directly after block 1

Inserted immediately after the *Command discipline* bullet in both pipeline files — `dev-flow` line 277, `dev-flow-worktree` line 271, ahead of *Severity-independent, value-gated* — so each file gains exactly one line.

```
- **Measurements are derived, not typed.** Every measurement an artifact states was printed by a command its author ran, or it is cut. A measurement of the artifact's **own replacement text** — a word or line count, "the shortest bullet", "in seven words" — is asserted in that artifact's own success criteria: the text is still under the author's hand, and a later rewrite silently falsifies anything typed beside it. A measurement of the **tree before the edit** is the opposite case — re-deriving it afterwards falsifies a design that is correct — so give the command pinned to the base revision (`git grep … <base> -- …`) beside the claim, state the claim in the past tense at that revision, and state no number its output does not show. A spec self-review names every measurement the artifact states and the command that printed it.
```

Placement is Cross-Cutting Concerns rather than Stage 1's inlined design protocol, deliberately. Stage 1's numbered bones sit under **Bare-idea entry** and bind only the produce-subagent that drafts from an idea; they do not reach design-file entry, they do not reach Stage 2's plan, and they do not reach the review's own rewrite of the doc — and the review *is* an author, since its contract is to rewrite and commit the artifact. Cross-Cutting reaches all of them.

The closing sentence is this design's replacement for #41's proposed *"a spec self-review may not certify a number it did not re-derive."* That wording is itself unfalsifiable — the failure mode #41 documents is a self-review that asserted *"the word counts … are consistent"* while re-deriving nothing, and a self-review that certifies nothing satisfies a prohibition on certifying vacuously. Requiring it to **name every measurement the artifact states, and the command that printed each**, is what makes the certification checkable by the next reader: the reader can compare the list against the document and see an omission, which is exactly what a prohibition cannot express.

The stem — *every measurement was printed by a command its author ran, or it is cut* — is what makes the two branches symmetric. The first draft stated the own-text branch as a disjunction (*asserted, or not stated at all*) and the pre-edit-tree branch as *pinned and reproducible*, which never required that anyone had run the pinned command. That asymmetry is a live defect and not a hypothetical one: this document's own first draft stated four heading counts for `docs/superpowers/specs/` beside a pinned command that prints only two of them, and both of the two the command did not print were wrong. The command reproduced its result perfectly, as the old wording required; nobody had run it, which the old wording did not require.

Neither block 1 nor block 2 contains the token `dev-flow` or `dev-flow-worktree`, so the two copies of each are byte-identical and the substitution image is equality. *Verification* step 2 re-derives that count rather than trusting this sentence, and asserts the substitution-image property in its general form, so a future rewrite that does introduce a variant name still has to mirror correctly.

## Version bumps

Both plugins ship changed text — each contains its own pipeline `SKILL.md` **and** its own copy of `adversarial-review/SKILL.md` — so both bump. Per `CLAUDE.md` line 7, always the minor segment:

| Plugin | `plugin.json` | Before | After |
|---|---|---|---|
| `dev-flow` | `plugins/dev-flow/.claude-plugin/plugin.json` | `2.9.0` | **`2.10.0`** |
| `dev-flow-worktree` | `plugins/dev-flow-worktree/.claude-plugin/plugin.json` | `1.11.0` | **`1.12.0`** |

`2.9.0` → `2.10.0` is a minor bump, not a major one: the segments are numbers, not decimals. Neither `description` changes, so `.claude-plugin/marketplace.json` is untouched and `check-sync.py`'s Check A is unaffected.

*Verification* step 6 treats both targets as a **floor** and asserts strict inequality against `origin/main`, because equality is the failure mode: two branches that bump to the identical string auto-resolve on merge with no conflict and produce no version change at all (#43, and the incident it records against PRs #35/#36/#37).

## Assumptions

- **A1. Targets as of `bf7676b`:** `adversarial-review/SKILL.md` line 29 in both copies; `dev-flow/skills/dev-flow/SKILL.md` line 276 with an insertion at 277; `dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` line 270 with an insertion at 271. The implementation matches on **text**: step 2 reconstructs each file from its merge-base blob, so a base that moved and shifted the lines fails loudly instead of editing the wrong line.
- **A2. No test framework exists in this repo.** The success criteria below are the whole correctness surface — which is the fact #40 is about, applied to this change.
- **A3.** `claude plugin validate .` emitting exactly 8 `No author information provided` warnings and exiting 0 is the expected pass state, per `CLAUDE.md`.
- **A4. Both plugins bump.** Not a judgment call: `adversarial-review/SKILL.md` exists inside both plugin directories, so a one-line edit to the mirror pair changes both shipped plugins even before the pipeline files are counted.
- **A5. Neither issue is a no-change ruling.** #40 and #41 both ship text and both close on merge; the PR body carries the reasoning. If a review flips either to no-change, that issue's section above becomes its closing comment verbatim and the corresponding block is dropped, along with the parts of steps 2 and 3 that reference it.
- **A6. The runner-refusal predicate is a harness fact, measured today and not pinned by any check here.** The table under *#40's comment supersedes the naive fix* records the measurement and the date. Block 1 is worded so that the by-construction argument carries the rule on its own, and the refusal ships in no block: if the harness later accepts the shell form, the `argv` rule is still correct and no shipped sentence goes stale.
- **A7. Text assertions use `git grep`, not bare `grep`.** Under Claude Code's Bash tool bare `grep` is a ugrep-backed shell function whose output layout is not reliable for per-file assertions. Exact assertions are made in `python3`.
- **A8. This design's own plain fenced blocks are 0, 1 and 2, shape `[1, 1, 1]`.** No expectation below depends on a block's *length* except that shape, so a review that rewrites a block's text leaves every check runnable as written. The one measurement this design states about its own replacement text is the `dev-flow`-token count, which step 2 re-derives, so there is no gh-32/33-style stale-count exposure to declare (see *Self-reference*). Every other measurement in this document is of the tree at `bf7676b` or is a recorded command run, and each is stated with the command that printed it — which is the pre-edit-tree branch of block 2, not the own-text branch, and is unaffected by a review rewriting a block.
- **A9. The design and plan are committed on this branch** (`docs: commit`), so every scope check excludes `docs/superpowers/` with a pathspec, and every grep for a phrase this document quotes does the same.
- **A10. `origin/main` is fetchable at implementation time.** Steps 1, 2 and 6 all resolve a base or a published version from it. Step 6 fetches explicitly; steps 1 and 2 rely on the pipeline having fetched at branch creation, and fail loudly (naming the command and git's message) rather than silently comparing against a stale ref.

## Out of scope

Hard-excluded. A proposal touching any of these is a blocker, not a design.

- **`CLAUDE.md`** — that is #39, sequenced after this change (*Decomposition*). Every repo-local instrument stays there untouched. This is a conclusion, not a deferral: the text landing in `plugins/` names no instrument, so nothing here needs `CLAUDE.md` to change to be correct.
- **`scripts/`** — no change. `design_blocks.py` is *used* by step 2 and not modified; `check-sync.py` is not touched, and needs no new `MIRROR_PAIRS` entry, since the pipeline pair remained too divergent at `bf7676b` to check line-for-line — the two files did not even have the same length, which Check B's schema requires. The command below prints all four file lengths this document states; `dev-flow`'s and `dev-flow-worktree`'s pipeline files are the two that differ.

  ```sh
  git grep -c '' bf7676b -- plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md plugins/dev-flow/skills/adversarial-review/SKILL.md plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
  ```

  ```text
  bf7676b:plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md:89
  bf7676b:plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md:271
  bf7676b:plugins/dev-flow/skills/adversarial-review/SKILL.md:89
  bf7676b:plugins/dev-flow/skills/dev-flow/SKILL.md:277
  ```

- **`CONTEXT.md`** — untouched, and **no edit is implied**, which is a finding rather than a scope dodge. This change coins no repo concept: *measurement*, *criterion* and *success criteria* are ordinary vocabulary rather than shapes this repo reasons about, and the glossary defines shapes, not one row per word. The one term with a glossary entry that appears near this text is **Pass**, and neither new clause introduces a pass — both join an existing enumeration inside an existing seed, which is exactly the distinction the *Pass* entry draws ("An angle is a lens *within* a seed's list; a pass is a whole check"). *Vacuous* is not newly coined either: at `bf7676b` both pipeline `SKILL.md`s already used *"passes the resolver check vacuously"* in the same sense.
- **`.github/`** — no CI change. The version-collision check that would belong there is #43's territory, and step 6b covers this branch by hand in the meantime.
- **The two plugin `README.md`s** — at `bf7676b` neither contained the word *verification*, *criteri* or *command discipline*; there is nothing to hand-mirror. `git grep -c -i 'verification\|criteri\|command discipline' bf7676b -- plugins/dev-flow/README.md plugins/dev-flow-worktree/README.md` reproduces this: no output, exit 1.
- **`docs/adr/`** — no ADR is warranted. Neither clause reverses a recorded decision or establishes an architectural constraint; both are conventions about artifact text.
- **`.claude-plugin/marketplace.json`** — untouched, because no `description` changes.
- **#43's two gaps** — the stage-boundary checkbox and the merge gate that re-verifies nothing. Step 6b below is exactly the per-plan workaround #43 describes; it is named as such rather than fixed here.
- **The diff-mode correctness seed** (`adversarial-review/SKILL.md` line 28) — deliberately unchanged. A PR diff has no success criteria of its own; it is reviewed against the design's, which line 29 already covers at the stage where they are written.
- **Every pre-existing file under `docs/superpowers/`** — prior records, four of which legitimately contain the phrase this edit removes.

## Verification

Every command runs from the repo root, after the edit unless stated. The base is `git merge-base origin/main HEAD` — computed, never hardcoded, so it stays correct if `main` advances or the branch is rebased; it resolves to `bf7676b` today.

**Every step that consumes the computed base — 1 and 2 — passes it to `git` as an `argv` element from `python3`, never through a shell.** That is this design's own rule (block 1) applied to itself, and it is load-bearing twice over: `git merge-base` prints nothing on failure (exit 128 for an unresolvable ref, exit 1 and total silence when the histories share no ancestor), so an unquoted `$(…)` degrades a base comparison into a working-tree-vs-index one that passes on a branch committed per task; and the compliant shell alternative is refused unrun (*#40's comment supersedes the naive fix*). There is **no `$(git …)` substitution anywhere below.** Steps 3, 4 and 5 consume no ref at all, and the `bf7676b`-pinned greps elsewhere in this document take a **literal** SHA, which is not a computed ref and so stays writable as one line of shell — the distinction block 1 draws.

Every step below can fail, and the red output of each is given so the discrimination is demonstrated rather than claimed. No step's output is human-read in place of an assertion, and no assertion sits behind an earlier short-circuit: steps 2 and 6 collect every mismatch into a list and print them all before exiting, so a first failure never hides a second.

**0. Block shape — asserted, not reported.** `design_blocks.py`'s CLI is a shape **reporter**: `main()` calls `_blocks()`, prints the shape and unconditionally returns 0, so running it can never fail on a shape mismatch and its output would be human-read. The **guard** is `read_blocks`, where the shape is a required argument and a mismatch is a `SystemExit`. So this step calls the guard. That is a defect in using a reporter as a guard, not a defect in the script; `scripts/` stays out of scope and is not edited.

```sh
python3 - <<'PY'
import sys
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
DESIGN = "docs/superpowers/specs/2026-08-02-gh-40-41-verification-blocks-design.md"
for i, b in enumerate(read_blocks(DESIGN, [1, 1, 1])):
    print("  [%d] %s" % (i, b[0][:70]))
print("shape guard: OK")
PY
echo "exit=$?"
```

Expect three preview lines — block 0 the `| **design** |` table row, block 1 the *Command discipline* bullet, block 2 the *Measurements* bullet — then `shape guard: OK` and `exit=0`. Run against this document it printed:

```text
  [0] | **design** | The design rubric (below) *is* the lens, applied advers
  [1] - **Command discipline:** resolve git-internal paths through git (`git
  [2] - **Measurements are derived, not typed.** Every measurement an artifa
shape guard: OK
exit=0
```

Anything else means this design was edited after the plan captured its shape — **stop and report**. Produced for real, by copying this document to a scratch path outside the repo, splitting block 0's single line in two there, and pointing the same program at the copy: it printed nothing on stdout and this on stderr, at `exit=1`:

```text
design code-block shape is [2, 1, 1], want [1, 1, 1]; stop and re-read the design
```

The reporter, given the same file, prints `shape: [2, 1, 1]` and exits 0. That difference is the whole reason this step calls the guard.

**1. File scope — exactly six files, and no seventh.** The `--name-only` set is compared for equality against the authorized list, so a stray edit to `CLAUDE.md`, `CONTEXT.md`, `scripts/`, `.github/`, a `README.md` or `marketplace.json` fails the step **and names the offending path**; that claim is what the printed `changed …, want …` pair delivers, and the red run below shows it. There is deliberately no `--stat` line and no `--quiet` companion: `--stat` asserts nothing, and a `--quiet` pathspec list over paths already excluded by this equality would pass vacuously — the two failures #40 reports.

```sh
python3 - <<'PY'
import subprocess, sys
SCOPE = ["--", ".", ":!docs/superpowers/"]
WANT = sorted([
    "plugins/dev-flow/.claude-plugin/plugin.json",
    "plugins/dev-flow/skills/adversarial-review/SKILL.md",
    "plugins/dev-flow/skills/dev-flow/SKILL.md",
    "plugins/dev-flow-worktree/.claude-plugin/plugin.json",
    "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md",
    "plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md",
])
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

Expect a `base:` line carrying a 40-character SHA, then `file scope: OK` and `exit=0`. Run at `bf7676b` with no edit applied, it printed `file scope: FAIL -- changed [], want [...]` and `exit=1`. A base that cannot be computed fails as one quotable line naming the command, its exit status and git's message — `FAILED: git merge-base origin/main HEAD -- exit 1, (no message)` for histories sharing no ancestor, where git itself says nothing.

**2. Reconstruction and design conformance — the check that proves both what landed and what did not.** One program, four assertions per file family:

- each of the six edited markdown lines is **the block from this design on disk**, read through the shared reader and never retyped;
- each target file is **byte-for-byte its merge-base blob with exactly the intended edit applied** — line replaced, or line replaced plus one line inserted **directly after** it — which is what proves no other line moved;
- the two **hand-mirrored** files' edited passages are exact substitution images of one another (`dev-flow-worktree` → `dev-flow`), after the edit and at the base, which is the check `check-sync.py` cannot make because it does not know this pair exists;
- the one measurement this design states about its own replacement text — that no block names a plugin variant — is **re-derived here**, not trusted.

The fence is unindented on purpose: a `python3` heredoc indented under a list item is an `IndentationError`. Failures of the producers — `git`, `read_blocks` — are left to raise as themselves; they name the failing command, and no traceback can be mistaken for a pass.

```sh
python3 - <<'PY'
import subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-02-gh-40-41-verification-blocks-design.md"
AR_DF = "plugins/dev-flow/skills/adversarial-review/SKILL.md"
AR_WT = "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md"
DF = "plugins/dev-flow/skills/dev-flow/SKILL.md"
WT = "plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md"
AR_I, DF_I, WT_I = 29, 276, 270          # 1-based anchor lines, at the base
WANT_LEN = {DF: 278, WT: 272, AR_DF: 89, AR_WT: 89}   # after the edit

def git(*args):
    return subprocess.run(("git",) + args, capture_output=True, text=True,
                          check=True).stdout
def split(text):
    out = text.split("\n")
    if out and out[-1] == "":
        out.pop()
    return out
base = git("merge-base", "origin/main", "HEAD").strip()
def old(path):
    return split(git("show", base + ":" + path))
def now(path):
    return split(Path(path).read_text(encoding="utf-8"))

b0, b1, b2 = (b[0] for b in read_blocks(DESIGN, [1, 1, 1]))
bad = []

for path in (AR_DF, AR_WT):
    o, n = old(path), now(path)
    if n != o[:AR_I - 1] + [b0] + o[AR_I:]:
        bad.append("%s is not its base blob with line %d replaced by block 0" % (path, AR_I))
    if n.count(b0) != 1:
        bad.append("%s holds block 0 %d times, want exactly 1" % (path, n.count(b0)))

for path, i in ((DF, DF_I), (WT, WT_I)):
    o, n = old(path), now(path)
    if n != o[:i - 1] + [b1, b2] + o[i:]:
        bad.append("%s is not its base blob with line %d replaced by block 1 and block 2"
                   " inserted directly after it" % (path, i))
    if n.count(b2) != 1:
        bad.append("%s holds block 2 %d times, want exactly 1" % (path, n.count(b2)))
    if not b1.startswith(o[i - 1]) or b1 == o[i - 1]:
        bad.append("%s: block 1 is not a strict extension of base line %d; this edit removes"
                   " no phrase, so every existing byte must survive" % (path, i))

sub = lambda s: s.replace("dev-flow-worktree", "dev-flow")
if sub(now(WT)[WT_I - 1]) != now(DF)[DF_I - 1]:
    bad.append("the edited Command discipline lines are not substitution images")
if sub(now(WT)[WT_I]) != now(DF)[DF_I]:
    bad.append("the inserted Measurements bullets are not substitution images")
if sub(old(WT)[WT_I - 1]) != old(DF)[DF_I - 1]:
    bad.append("the two Command discipline lines were not images at the base either -- the"
               " anchor line numbers are wrong")

counts = [b.count("dev-flow") for b in (b0, b1, b2)]
print("dev-flow occurrences per block:", counts)
if counts != [0, 0, 0]:
    bad.append("a block names a plugin variant, so its two copies are no longer byte-identical")

for path, want in sorted(WANT_LEN.items()):
    if len(now(path)) != want:
        bad.append("%s is %d lines, want %d" % (path, len(now(path)), want))

for why in bad:
    print("MISMATCH:", why)
print("reconstruction:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expect `dev-flow occurrences per block: [0, 0, 0]`, then `reconstruction: OK` and `exit=0`. Extracted from this document and run at `bf7676b` with no edit applied, it printed the token counts, then **ten** `MISMATCH:` lines — four reconstruction failures, one per file; four `holds block … 0 times, want exactly 1` failures (block 0 in each `adversarial-review` copy, block 2 in each pipeline file); and the two pipeline files at 271 and 277 lines instead of 272 and 278 — then `reconstruction: FAIL` and `exit=1`. If the shape guard trips instead (`design code-block shape is …`), **stop and report**: this design was edited after the plan captured its shape.

**3. Residue — the split junction is gone from shipped text.** Expect no output and a non-zero exit. The pathspec is required: four prior records under `docs/superpowers/`, and this document, legitimately contain the phrase.

```sh
git grep -n -F 'success criteria — plus the input-contract' -- . ':!docs/superpowers/'
```

At `bf7676b` this same command printed the two copies of line 29 and exited 0, which is the red run.

**4. Mirror-pair sync.** This is the mechanical proof that the two `adversarial-review` copies took the *same* edit; step 2 is the proof for the pair `check-sync.py` cannot see.

```sh
python3 scripts/check-sync.py
echo "exit=$?"
```

Expect, unchanged from before the edit, `mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)` — block 0 replaces a line rather than adding one, so the pair's length is untouched — then `check-sync: all checks passed` and `exit=0`:

```text
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)
check-sync: all checks passed
exit=0
```

The red run matters more than most here, because every argument in this document about the machine-checked pair rests on `check-sync.py` actually catching a one-sided edit. Produced by cloning the repo to a scratch directory outside it, applying block 0 to the **`dev-flow` copy only**, and running `check-sync.py` there:

```text
check-sync: manifest descriptions ... OK (8 plugins)
check-sync: mirror pair "adversarial-review" ... FAIL

  These two files must stay line-for-line identical after canonicalizing
  "dev-flow-worktree" -> "dev-flow". Every cross-cutting edit lands in both.

    A: plugins/dev-flow/skills/adversarial-review/SKILL.md
    B: plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md

  line 29: undeclared divergence
    A: <block 0, as given above>
    B: <line 29 as it stood at bf7676b>

  Fix: mirror the edit into both files. If the divergence is genuinely variant-specific,
  add it to MIRROR_PAIRS["adversarial-review"]["exceptions"] in scripts/check-sync.py
  with a one-line reason.

check-sync: 1 check failed

exit=1
```

The two `line 29:` lines are elided above only because each is the full text of a block already given verbatim in this document; the run printed both in full. What matters is that the check **names the line number and both sides**, so a one-sided edit cannot be mistaken for a mirrored one.

**5. `claude plugin validate .` — exit 0 *and* exactly 8 author warnings.** Both halves are asserted, because either alone passes vacuously: the command exits 0 while emitting warnings (that is the documented pass state, A3), and a count assertion alone would pass on a run that errored out. `claude` resolves on `PATH` from a `python3` subprocess, so no shell is needed; a `PATH` on which it does not resolve fails as one quotable line rather than a `FileNotFoundError` traceback.

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

**6. Versions — strictly greater than published. Two runs, both required.**

```sh
python3 - <<'PY'
import json, subprocess, sys
from pathlib import Path
JSON_DF = "plugins/dev-flow/.claude-plugin/plugin.json"
JSON_WT = "plugins/dev-flow-worktree/.claude-plugin/plugin.json"
WANT = {JSON_DF: (2, 10, 0), JSON_WT: (1, 12, 0)}     # a floor, never an equality
def git(*args):
    return subprocess.run(("git",) + args, capture_output=True, text=True,
                          check=True).stdout
def ver(text):
    return tuple(int(p) for p in json.loads(text)["version"].split("."))
git("fetch", "origin", "main")
bad = []
for path, want in sorted(WANT.items()):
    mine = ver(Path(path).read_text(encoding="utf-8"))
    published = ver(git("show", "origin/main:" + path))
    print("%s: mine %s, origin/main %s" % (path, mine, published))
    if mine < want:
        bad.append("%s is %s, below the designed floor %s" % (path, mine, want))
    if mine <= published:
        bad.append("%s is %s, not strictly greater than origin/main's %s"
                   % (path, mine, published))
for why in bad:
    print("MISMATCH:", why)
print("versions:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expect two `mine … origin/main …` lines, `versions: OK` and `exit=0`. Extracted from this document and run at `bf7676b` with no bump applied, it printed both versions as equal to `origin/main`'s, then **four** `MISMATCH:` lines — one *below the designed floor* and one *not strictly greater than origin/main's* per plugin — then `versions: FAIL` and `exit=1`.

- **6a — at implementation**, with both bumps in the working tree.
- **6b — immediately before the pipeline halts at `pre-merge`**, after the last merge or rebase of `origin/main` into the branch. Neither substitutes for the other, and a criteria pass reported without 6b is incomplete: 6b is the only check anywhere that notices a concurrent PR landing `2.10.0`/`1.12.0` first, because two branches writing the byte-identical `"version"` line **auto-resolve with no conflict** and produce no version change at all. String equality against a literal would not catch it; the comparison is `>` against `origin/main`, re-fetched.
- The comparison is a **tuple of integers**, not a string: `"2.10.0" > "2.9.0"` is false lexicographically, and this is the first change in the repo's history where that distinction bites.
- `WANT` is a floor, so the remediation the criterion prescribes — re-target both versions upward and re-run — leaves it green.
- **6b has no mechanical carrier**, which is #43's first gap exactly: a plan checkbox cannot express a step that runs at a stage boundary. It travels as prose in the plan's final task and in the `pre-merge` halt report. Named here rather than worked around silently.

## Files the plan will touch

- **Modify:** `plugins/dev-flow/skills/adversarial-review/SKILL.md` line 29 (block 0, whole-line replacement).
- **Modify:** `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md` line 29 (block 0, whole-line replacement — the identical line).
- **Modify:** `plugins/dev-flow/skills/dev-flow/SKILL.md` line 276 (block 1, whole-line replacement) and insert block 2 as the new line 277.
- **Modify:** `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` line 270 (block 1) and insert block 2 as the new line 271.
- **Modify:** `plugins/dev-flow/.claude-plugin/plugin.json` — `"version"` `2.9.0` → `2.10.0`.
- **Modify:** `plugins/dev-flow-worktree/.claude-plugin/plugin.json` — `"version"` `1.11.0` → `1.12.0`.
- **Committed by dev-flow per `docs: commit`:** this design and its plan under `docs/superpowers/`.

Nothing else. No `CLAUDE.md`, no `CONTEXT.md`, no `scripts/` file, no `.github/` file, no `README.md`, no `marketplace.json`, no `docs/adr/`.

## Self-reference

This design's own success criteria are subject to the rules it proposes. Where it complies, and where it cannot:

- **Block 1's `argv` rule.** Complied with: steps 1 and 2 compute the base inside `python3` and pass it to `git` as an `argv` element; there is no `$(git …)` anywhere in this document's criteria. Step 3's `git grep` consumes no computed ref — it takes a literal phrase — and step 4's, 5's and 6's commands take none either, apart from step 6's `origin/main`, which is a named ref rather than a computed one.
- **Block 1's scope extension.** This is the first design written under it, so compliance is the point rather than a formality: every criterion above is a command with an assertion, and each one's red output is recorded.
- **Block 0's falsifiability clause.** Complied with: no `--stat`, no `--quiet` companion whose pathspec enumerates already-excluded paths, and no assertion behind an earlier short-circuit — steps 2 and 6 collect all mismatches and print them before exiting. Where prose asserts a criterion's *diagnostic value* — step 1's claim that a scope violation is **named**, step 2's that a reconstruction failure says which file and which line — the claim is measured by the recorded red output, not asserted. Step 0 was the one place this failed while the document was being written: it ran `design_blocks.py`'s CLI, which reports a shape and always exits 0, so the criterion could not fail and the claim that a split block *"trips step 0 and halts"* was false. It now calls `read_blocks`, the guard, and its red run is recorded.
- **Block 2's own-text clause.** This design states exactly **one** measurement of its own replacement text — that no block contains the token `dev-flow` or `dev-flow-worktree` — and step 2 re-derives it, printing the counts. It states no word counts and no length comparisons of its own replacement text, so there is nothing in this document a review edit to a block's text can leave stale (A8). Note what this does *not* rest on: the earlier draft justified the omission as "#41's cheaper variant applied first — these numbers carry no argument", and that reasoning is exactly what licensed the false heading counts, which did carry an argument and were typed anyway. The stem now covers every measurement regardless.
- **Block 2's pre-edit-tree clause.** Every measurement of the tree before this change — the `verification|success criteri` grep under `plugins/`, the three heading counts, the phrase-junction counts inside and outside `docs/superpowers/`, the README greps, the four file lengths, the published versions, the anchor line numbers — is pinned to `bf7676b`, stated in the past tense at that revision, and given with the command that printed it. Each was re-derived by running its pinned command, and no number is stated that its command's output does not show.
- **The two clauses do not conflict, and their boundary shows here.** Step 3's grep is pinned to no revision *because it runs post-edit and must see the post-edit tree*; the `bf7676b`-pinned greps in *What the two issues ask for* are the opposite case. The distinguishing question is the one block 2 states: can this change's own text appear in the result?
- **Where it cannot comply.** Criterion 6b must run at a stage boundary and no plan checkbox can express that, so it is prose addressed to the orchestrator. That is a real weakness — nothing mechanically detects a skipped 6b — and it is #43's first gap, named in *Out of scope* rather than papered over.

## Rejected alternatives

- **Extend *Command discipline* verbatim to criteria** (#40's original wording). Rejected on evidence: the capture-validate-quote form it prescribes is refused unrun by the runner that executes these criteria, and the tool's own remedy — separate commands — forces a hardcoded base, which is the original hazard wearing a different hat.
- **Put everything in `adversarial-review`** (approach A). Rejected: duplicates a pipeline rule into a skill that reviews repos with no pipeline, and leaves authoring uncorrected so every design is repaired per instance.
- **Put everything in the pipeline pair** (approach C). Rejected: the falsifiability clause belongs beside the *"missing or untestable success criteria"* item that already exists and already tried to catch this, and moving the whole change into the pair nothing checks mechanically forfeits `check-sync.py` for the half that fits it.
- **A new named pass in `adversarial-review`**, with its own trigger and reportability rule. Rejected: both clauses are unconditional (every design has criteria; every design states numbers) so there is no trigger to write, and a named pass would cost a heading and two framing sentences to say what one clause says.
- **A new "criteria contract" section in the pipeline files.** Rejected for the same reason plus one: Cross-Cutting already carries exactly this kind of one-bullet rule, and a new section would restate scope and motivation the bullet inherits.
- **Split the criteria-scope rule into a second Cross-Cutting bullet**, leaving *Command discipline* near its base length. Rejected: both halves of the append are bound to the bullet by reference — the scope sentence extends *capture, validate non-empty, and quote*, and the `argv` form is an exception to it that closes with *"Capture-validate-quote stays the rule everywhere else."* A separate bullet would have to restate the rule it extends and excepts, duplicating one rule inside one section; block 2 is a new bullet precisely because its subject is different. The weight was examined rather than accepted, and the search for offsetting cuts is recorded so it is not re-run: at `bf7676b` the section's other bullets — `git grep -n -A 8 '^## Cross-Cutting Concerns' bf7676b -- plugins/dev-flow/skills/dev-flow/SKILL.md` lists them — were the pipeline's own rules, each already at its minimum, and the one of comparable length, *Review provenance is checked, not assumed*, is the guarantee this skill's model policy depends on. There is nothing to spend.
- **Put the measurement rule in Stage 1's inlined design bones.** Rejected: those bullets sit under *Bare-idea entry* and bind only the drafting subagent — not design-file entry, not Stage 2, and not the review's own rewrite, which is itself an authoring step.
- **Forbid derived numbers unless they carry an argument** (#41's cheaper variant, as the whole rule). Rejected on its own evidence: the numbers that failed in practice were the ones carrying the argument, so a rule that only forbids decorative numbers leaves the load-bearing ones typed by hand. And its trigger — *does this number carry an argument?* — is a judgment the author makes about their own text, which the author who typed the number is least likely to rule against. The stem keys on nothing the author decides instead: the number came out of a command that was run, or it is cut. Stating fewer numbers is then a way to comply, not the rule.
- **Also edit the diff-mode correctness seed** (line 28). Rejected: a diff has no success criteria of its own, and it is reviewed against a design whose criteria line 29 already governs at the stage they are written.
- **Enrol the pipeline `SKILL.md` pair in `check-sync.py`'s `MIRROR_PAIRS`.** Rejected here as out of scope and as wrong on the merits for this schema: at `bf7676b` the two files did not have the same length — the line-count command in *Out of scope* prints both — and Check B's line-parallel schema can only declare same-index one-line divergences.
- **Name an instrument in the `plugins/` text** — the block reader, the merge-base-blob assertion, the removed-phrase grep. Rejected: that is precisely the move that would settle #39's option 3 by precedent, and it is the boundary this change holds (*Decomposition*).

## PR

```text
Close #40 and #41 by writing down what a design's success criteria may claim
and how their commands are written.

#40 -- Command discipline binds the pipeline's own commands and said nothing
about the success criteria a design or plan emits, which in a repo with no
test suite are the whole correctness surface. Measured at bf7676b, with the
command in the design: neither pipeline SKILL.md contained the word
"verification" or the phrase "success criteria" at all. The bullet's scope now
says so. The naive fix -- extend capture-validate-quote verbatim -- prescribes
a form the runner refuses unrun, because a capture and its consumer must share
one Bash call; so a criterion consuming a *computed* git ref runs its git calls
through python3/subprocess with the ref as an argv element, which retires
word-splitting by construction rather than by remembering to quote.

#40's second half and #41's detection side land in one sentence of the
adversarial-review mirror pair: a criterion that cannot fail is untestable
(human-read output, a scope excluding everything it would catch, a step
unreachable behind a short-circuit), and measurements the artifact states that
no command it gives actually printed -- of its own replacement text, of the
tree it changes, or of what a command it prescribes outputs. That last case is
#40's comment's second half, the "fails with the offending path" prose about a
command that writes zero bytes: an unchecked measurement, not a fourth way a
criterion cannot fail. Plan mode inherits the whole item -- line 30 reads "the
prose checklist above" -- which is where the one documented propagation went.

#41 -- three numbers a design stated about its own replacement text were false,
two of them the receipt for its central argument, and the spec self-review
certified them unchecked. New Cross-Cutting bullet: every measurement an
artifact states was printed by a command its author ran, or it is cut. A
measurement of the artifact's own text is asserted in its own success criteria;
a measurement of the tree before the edit is the opposite case and carries the
command pinned to the base revision beside the claim, stated in the past tense
at that revision, with no number the output does not show -- since re-deriving
it afterwards would fail a correct design. A spec self-review names every
measurement the artifact states and the command that printed it.

Three passages: one line of the machine-checked adversarial-review pair, and
one appended sentence-group plus one new bullet in each hand-mirrored pipeline
SKILL.md. CLAUDE.md is untouched -- every repo-local instrument stays there,
and the text landing in plugins/ names none, which is what keeps #39's three
options open rather than settling option 3 by precedent.

dev-flow 2.9.0 -> 2.10.0, dev-flow-worktree 1.11.0 -> 1.12.0 (a minor bump;
the segments are numbers, not decimals). Both plugins ship a changed
adversarial-review copy as well as their own pipeline file.

Closes #40
Closes #41
```

## Spec self-review

- **Placeholders / TBDs:** none. All three replacement passages are given in full as plain fenced blocks; every criterion is runnable as written, with its expected green output and its recorded red output; both version targets are exact.
- **Every measurement this document states, and the command that printed it.** Block 2 requires the whole list, not a selection, so this is the whole list.

  **Of the tree at `bf7676b`, each with its command given beside the claim in the text and re-run while writing this review:**

  | Measurement | Command |
  |---|---|
  | four matching lines in two files for `verification\|success criteri` under `plugins/` | `git grep -n -i -E 'verification\|success criteri' bf7676b -- plugins/` (*The gap #40 reports…*) |
  | the removed junction in two files outside `docs/superpowers/`, four inside | the `git grep -c -F` pair under *Block 0* |
  | 2 `## Acceptance criteria`, 3 `## Success criteria`, 8 `## Verification` | the `git grep -h -E … \| sort \| uniq -c` under *Block 1* |
  | no README match at all, exit 1 | the `git grep -c -i` in *Out of scope* |
  | file lengths 89 / 89 / 271 / 277 | the `git grep -c ''` in *Out of scope* |
  | published versions `2.9.0` and `1.11.0` | `git grep -n -F '"version"' bf7676b -- plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json` |
  | anchor lines 29, 29, 270, 276, and the two pipeline copies' *Command discipline* lines byte-identical | `git grep -n -F -e '- **Command discipline:**' -e '\| **design** \| The design rubric' bf7676b -- plugins/`, and step 2's substitution-image assertion |
  | every row of the runner-refusal table | the command in that row's left-hand cell |

  **Of this document's own blocks:** the `[1, 1, 1]` shape, printed by step 0's guard; the zero `dev-flow`-token count per block, printed by step 2. Each block was also compared byte-for-byte against the substitution output printed from the files on disk, which is what "never retyped" means here.

  **Recorded command output:** the green and red runs of steps 0, 4 and 5 were produced while writing this document and are pasted verbatim — step 0's red by splitting a block in a scratch copy outside the repo, step 4's by cloning the repo to a scratch directory and applying block 0 to the `dev-flow` side only, step 5's by re-running the same program with `WANT_WARNINGS = 7`. Both scratch paths were deleted afterwards. Steps 1, 2, 3 and 6's red runs were produced by running each at `bf7676b` with no edit applied: step 1 printed `changed []`, step 2 ten `MISMATCH:` lines, step 3 the two copies of line 29 at exit 0, step 6 four `MISMATCH:` lines. A first draft of this review said eight and two for steps 2 and 6; running them corrected it.

  **Asserted rather than certified, because they describe the post-edit tree:** 278 / 272 / 89 / 89 lines and the `2.10.0` / `1.12.0` floors — step 2 and step 6 fail if either is wrong.

  **Corrected by this review.** The *Block 1* heading bullet previously stated four counts — *"8 `## Verification`, 3 `## Success criteria`, and gh-8's `## Acceptance criteria`, with five older designs carrying none"*, across *"the 16 designs"* — beside a command that prints only two of them. Two things falsified it. The three-way command's output, now pasted under *Block 1*, shows **2** `## Acceptance criteria`, so gh-8 was not its only user. And the four stated counts sum to 17 against the stated total of 16, which needs no measurement at all to see. The bullet now states the qualitative claim, which is the stronger one and cannot go stale, and pastes the command's output rather than any number the command does not print.
- **Internal consistency:** block 0 is line 29 with one parenthesised gloss added to an existing item, one new item after it, and nothing else changed — it holds four pipes and three cells, like the row it replaces, and no longer contains the junction the residue grep looks for; block 1 is the base bullet plus an append, which step 2 asserts as a strict-prefix relation; block 2 is new and inserted directly after block 1. The `[1, 1, 1]` shape, the six-file scope list, the four anchor line numbers and the two version targets agree everywhere they appear. The claim that no block names a plugin variant is re-derived rather than trusted.
- **Scope:** six files. Step 1 checks it by file; step 2 checks each markdown file line by line against its merge-base blob. `CLAUDE.md`, `CONTEXT.md`, `scripts/`, `.github/`, both `README.md`s, `marketplace.json` and `docs/adr/` are each named in *Out of scope* with a reason, and each is a conclusion rather than a deferral.
- **Ambiguity:** the one place a fresh implementer could go wrong is grep scope — the removed junction and every quoted passage legitimately appear in this document. Every grep that could hit it carries `':!docs/superpowers/'` or is pinned to `bf7676b`. The second is which of block 2's two measurement rules applies to a given number; the table under *#41* states the test in one question, and *Self-reference* works it on this document's own greps.
- **Positions taken:** #40 and #41 ship together as one change (*Decomposition*); #39 is not decided and #43 is not fixed. Placement splits by side — authoring in the hand-mirrored pipeline pair, detection in the machine-checked `adversarial-review` pair — rather than consolidating into either. No named pass and no new section is added — nor a second Cross-Cutting bullet splitting the criteria rule, and no *Length budget* section, since stating word counts of this change's own replacement text would oblige asserting them in *Verification* and contradicts A8. The measurement rule is one stem over two branches: the stem requires the number to have come out of a command that was run, and which branch applies is decided by what is measured. Both plugins bump the minor segment. Nothing is left for the implementer to decide.
