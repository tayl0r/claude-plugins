---
dev-flow:
  slug: gh-28-29-review-prose
  stops: [pre-merge]
  docs: commit
---

# gh-28 / gh-29: two prose-judgment calls in `adversarial-review/SKILL.md`

Two issues filed by the same `diff`-mode quality seed run over PR #25's range, both against the machine-checked `adversarial-review/SKILL.md` mirror pair, both explicitly filed for judgment rather than as defects with obvious fixes. **#28 SHIPS**, widened from the one word the issue proposes to all three places in the file that name the second review tier by a `group`-qualified name — after this change the file names that tier exactly one way, `resolver`, and every surviving `group` in it refers to the grouping *operation*. **#29 is NO CHANGE**, with the ruling recorded here: `:42` and `:48` are never composed into the same seed prompt, so a cross-reference between them cannot resolve for the one reader it is written for — and that holds at any size, down to a single sentence; the repetition is systematic house style across all three findings-only passages rather than an accident of two; and what is literally shared is two boilerplate sentences, against five compared mechanics that all differ.

## What was verified before designing

Run against the base commit `c8b2182`, in this worktree. (`c8b2182` is the fork point — `git merge-base origin/main HEAD`. It touches only `CONTEXT.md`'s **Family** entry and two `docs/superpowers/` records, so every fact below is unchanged from the `0c05098` state the issues were filed against, and none of the glossary entries this document cites — **Resolver**, **Pass**, **Angle**, **Tier** — is affected.)

- The three candidate lines — `:52`, `:71`, `:81` — are **byte-identical** in both mirror copies. `diff` between the two copies reports divergence only at `:3`, `:11`, `:12`, `:77` (the `dev-flow-worktree` → `dev-flow` canonicalized text plus the one declared exception). So a single replacement text serves both files.
- `python3 scripts/check-sync.py` passes today: `mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)`.
- `git grep -oin 'group resolvers\?' -- plugins/ CONTEXT.md README.md` returns exactly two lines, `:71` in each copy. `git grep -in 'group agent'` returns `CONTEXT.md:15` (the `_Avoid_:` line itself) plus `docs/superpowers/` records only — no shipped-text hit.
- `git grep -in 'group-resolution' -- .` returns: `:52` and `:81` in both copies, `docs/adr/0002-…:3`, and `docs/superpowers/` records. **Nothing else in the repo keys off the string** — not the two pipeline `SKILL.md`s, not either `README.md`.
- Both pipeline `SKILL.md`s already call the tier `resolver` — "the review's seed/resolver leaves", "resolvers the resolver tier", "`resolvers: M× <tier>`". Neither ever says `group-resolution`. This is corroboration from **outside** the mirror pair, which is what `CLAUDE.md` requires of any change to it.
- **The issue #28 body is wrong on one point.** `git diff 0a8a158 0c05098` shows PR #25's `-`/`+` pair for line 71; the `-` line already read `(seed reviewers, group resolvers)`. #25 changed only the sentence-initial `**Group-agents never invoke…**` → `**Resolvers never invoke…**`. `group resolvers` was **pre-existing and untouched**, not reintroduced. Correction folded into the ruling below.

## Decomposition check

The two issues stay one change. They touch the same two files, they are both prose judgments about the same skill, and shipping them separately would mean two version-bump pairs and two PRs for what is at most a three-line edit. #29 rules NO CHANGE, so the merged change is exactly #28's edit plus this document; nothing about #29 constrains or is constrained by #28's text. **No split.**

## Issue #28 — `group resolvers` at `:71`

### The case for acting

- **One sentence names one tier two ways, seven words apart.** `:71` opens `**Resolvers never invoke …**` and closes `(seed reviewers, group resolvers)`. This is a prompt read once by a fresh, context-free agent — an agent that has no way to resolve whether `Resolvers` and `group resolvers` are the same population or two related ones. The sentence's whole job is to state that there are **exactly two tiers** and that recursion is forbidden; a reader who suspects a third name has been introduced is reading the one sentence in the file where an off-by-one in the tier count matters most.
- **The parenthetical is a naming context, not incidental prose.** `(seed reviewers, resolvers)` is the sentence's authoritative enumeration of what the two tiers are *called*. That is the strongest naming position in the file after the Model section's lead-ins.
- **The qualifier distinguishes nothing.** `CONTEXT.md`'s **Resolver** entry — "A reviewer in the second tier, which weighs grouped seed findings against the design rubric and decides what changes" — defines exactly one kind of resolver, and it is always assigned per group. `group` cannot be selecting a subtype, because there is no other kind.
- **The correction strengthens rather than weakens the case.** The issue argued "the same sentence just removed a `group` qualifier, so the second use reads as an oversight." That argument is unavailable — the phrase predates #25. What replaces it is stronger: the phrase is **residue**. The #20 rename converted `group-agent` → `resolver` on the lines its drift rule reached and swept past this one; #25 converted the same sentence's subject and swept past it again. Two passes over this exact sentence left it behind. That reclassifies it from "a deliberate authorial choice" to "a leftover", which is the reading under which a fix is clearly warranted.
- **This file is the prompt that teaches other agents terminology discipline.** A file that instructs reviewers to grep a glossary for names it does not define owes more internal naming consistency than average, and its own inconsistency is the first thing a reviewer of it will find — as in fact happened.

### The case against

- **`group resolvers` is ordinary English.** Resolvers, of groups. The Glossary-conformance angle's own reportability rule says "The same term carrying its ordinary-English meaning inside a sentence names nothing and is not a candidate." On that reading there is no finding at all.
- **The angle fired on the generous limb.** "names something the entry does not define" is the false-positive-prone half of the rule, and the entry *does* define `resolver`, which is the head noun here.
- **A prior recorded ruling reads the phrase exactly that way.** `docs/superpowers/specs/2026-07-29-gh-20-diff-terminology-design.md:291` lists this document's own resolver-naming as "'the resolvers' call', 'one resolver group each', 'group resolvers'" — i.e. a prior author explicitly counted `group resolvers` as *using* the defined term, not coining a rival.
- **A one-word deletion is a small return** for a version bump pair, a PR, and a mirror-pair edit.

### Weighing

The prior ruling is real evidence and I am not overriding it — it answers a **different question**. gh-20 asked whether `group resolvers` violates `_Avoid_: group agent`, i.e. whether it is *drift*. It does not, and that ruling stands. #28 asks whether one sentence should name one tier two ways. A phrase can be perfectly clear of the `_Avoid_:` list and still be the wrong word in the position it occupies.

The ordinary-English defence is the strongest argument on the "against" side, and it fails specifically at `:71` because of position. Elsewhere in the file `group` genuinely is ordinary English: `:67` "**Group** similar issues together. For each group, spawn one agent" (the operation), `:70` "judging the group's findings together" (the operand). In an enumeration of tier *names*, it is not describing anything — it sits where a name goes.

Rubric: **"A fix must be worth its complexity: skip super-rare edge cases … unless the fix is essentially free."** This one is essentially free — no structure added, one word removed, no line count change, no cross-reference broken. **"Every change must earn its place; if the fix is worse than the wart, leave it."** The fix here is strictly less text saying the same thing more consistently; there is no configuration in which it is worse than the wart.

**Ruling for the `:71` text: SHIPS.**

### Scope — does the ruling cover `:52` and `:81`?

`:52` says "Every **group-resolution agent** (see Resolution procedure, below) applies this rubric" and `:81` says "**Group-resolution agents** — the tier that determines the best long-term design and adversarially self-checks — run on `opus`". These are structurally the same candidate as `:71`: a `group`-qualified name for the tier `CONTEXT.md` calls `Resolver`, and `Group-resolution agents` is arguably *closer* to the avoided `group agent` than `group resolvers` is.

**Options considered**

1. **Narrow — `:71` only.** Fix exactly what the issue reports. Smallest diff. Respects gh-20's explicit "deliberately not repaired" note for these two lines.
2. **Full normalization — `:52`, `:71`, `:81`.** After it, the file names the tier `resolver` everywhere and `group` survives only as the grouping operation.
3. **Widen further** — also normalize `seed reviewers` → `seeds` to match `CONTEXT.md`'s **Tier** entry ("`sonnet` for seeds, `opus` for resolvers").

**Chosen: option 2.**

Why not option 1. Fixing `:71` alone leaves two structurally identical candidates in the same file, one of them a *more* `group`-qualified name than the one just removed. The next `diff`-mode run that touches `:52` or `:81` fires the same angle on the same limb and files the same issue, and the next person re-litigates it. It also trades a sentence-internal inconsistency for a cross-section one — see the third bullet under *Why the two lines are genuinely improved*, below. Rubric: **"Value simplicity; widen the lens only against concrete demand (planned siblings, 2+ instances), never speculation"** — there are 2+ instances, measured, so widening is licensed rather than speculative. And **"OK to change adjacent code if it gets us to the better design."**

**What this change is, precisely: an exhaustive sweep, not a seam.** The rubric's zoom-out bullet — **"put the fix at the shared seam so current and future members inherit it — a per-instance fix the next person must remember to repeat is a latent regression"** — is what rules option 1 out, because option 1 leaves instances to repeat. It does not make option 2 a seam. Option 2 is a per-instance fix as well: three instances instead of one, over a closed set enumerated and grep-verified inside a single file. What earns it is exhaustiveness — afterwards nothing is left to repeat — not inheritance. And a seam does exist in the neighbourhood: `CONTEXT.md`'s **Resolver** `_Avoid_:` line, which the drift half and the glossary-conformance angle both grep verbatim, is the thing that would protect against *reintroduction*, which this sweep does not. It is deliberately not taken here; see *Out of scope* and **A7**. Success criteria 3 and 4 verify the sweep is complete at merge; nothing in this change keeps it complete afterwards, and that residual is recorded rather than papered over.

Why gh-20's note does not bind. Its grounds were: "it is not a name any entry rejects, the drift clause keys strictly off `_Avoid_:` lines, and the tier it names is recorded in ADR-0002." The first two are statements about the **reach of the drift rule**, and they remain true — this change is not claiming `group-resolution agent` is drift. Correctly, a change that *ships* an enforcement rule repairs only what that rule catches, or its demonstration is contaminated; gh-20's restraint was right for gh-20. The third ground is the weakest of the three and does not survive inspection: ADR-0002's own filename is `0002-opus-resolvers-and-the-end-of-adversary-not-author.md`, so the ADR is already internally mixed, and an ADR is a dated record whose wording is expected to age past the shipped text. It is not an argument for freezing shipped prose.

Why the two lines are genuinely improved, not merely made uniform:

- At `:81` the `group-resolution` qualifier is **redundant with the gloss in its own sentence** — "**Resolvers** — the tier that determines the best long-term design and adversarially self-checks —" already tells the reader what the tier does. The qualifier is doing the gloss's job, worse. It also restores symmetry with `:83`'s "**Seed reviewers** — the findings-only quality and correctness passes — run on `sonnet`".
- At `:52` the phrase points forward to the section titled "Resolution procedure", which is the one weak justification for keeping it; "Every resolver (see Resolution procedure, below)" points there just as well and matches `:68`'s "Each resolver:" two lines later inside that very section.
- The change makes `:71`'s parenthetical `(seed reviewers, resolvers)` an **exact mirror of the Model section's two bold lead-ins**, so the enumeration becomes a pointer to where each tier is specified. That payoff only exists if `:81` changes too — under option 1 the parenthetical would name a tier the Model section calls something else.

Why not option 3. `seed reviewers` is not an avoided synonym, it is the file's established phrase, and it is the Model section's own lead-in — which is precisely what `:71`'s parenthetical should mirror. Renaming it would be style-widening with no defect behind it and would break the mirror the change just created. **Rejected.**

**Ruling on scope: the change covers `:52`, `:71`, and `:81`.**

## Issue #29 — the Drift half restating the Glossary-conformance angle

### What is actually shared (measured, not assumed)

First, what the two passages are, since the ruling turns on it: per `CONTEXT.md`, `:42` **Glossary conformance** is an **angle** — "one lens in the diff-mode quality seed's list" — while `:48` **Terminology collision and drift** is a **pass**, "a whole check". They are different constructs, delivered to different seeds in different modes, and never composed into one prompt.

Two sentences are literal copies, not one:

- "The same term carrying its ordinary-English meaning inside a sentence names nothing and is not a candidate." — `:42` and `:48`.
- "the glossary's own state is never a finding: never flag it, never propose creating one." — `:42` and `:48`. The issue does not mention this one.

And a third shared refrain the issue does not mention — this one adapted per passage, not copied. All three of `:42`, `:46` (*Input-contract completeness*) and `:48` close their reportability rule with a findings-only hand-off to the resolvers, each with its own lead-in: `:42` "Findings only — a mismatch does not imply a rename, so report it either way; the fix is the resolvers' call."; `:48` "Findings only — neither a collision nor drift implies a rename, so report it either way; the fix is the resolvers' call."; `:46` "Findings only: which gaps are worth guarding is the resolvers' call." Only the tail is shared verbatim, and only `:42` and `:48` share the longer form. **Three** passages carry the convention, not two.

Everything else the issue calls "shared logic" differs substantively:

| | `:42` Glossary conformance | `:48` Drift half |
|---|---|---|
| Terms searched | every glossary term **and** every avoided synonym | avoided synonyms **only** |
| Scope | the diff's **added lines** of shipped text | the **whole artifact** |
| Spellings | identifier joins — `twoWords`, `two_words`, `two-words` | "spaced or hyphenated as prose compounds it" |
| Excluding records | path-excludes `docs/superpowers/` outright | cannot — the artifact usually *is* under `docs/superpowers/`; uses a mention-vs-use test instead |
| Candidate test | names something the entry does not define **or** reintroduces an avoided synonym | names the very concept its entry defines |

### The case for acting

- Two passages in one file share a reportability bar, and that file is half a mirror pair, so it is four copies across the two plugins.
- `check-sync.py` proves the two plugins' copies agree with each other. It cannot prove the two passages *within* a copy agree. A future edit to one and not the other drifts silently — in exactly the direction these clauses exist to catch, which is a genuinely uncomfortable shape for this particular file.

### The case against

- **The two passages are never composed into the same prompt, so a cross-reference between them cannot resolve. This is the decisive argument.** Seed prompts are built per mode: the mode table sends `:42` to the `diff`-mode **quality** seed — "inlined (below)" — and `:48` to the `design`/`plan` **correctness** seed, and `CONTEXT.md`'s **Angle** entry binds glossary conformance to the diff-mode quality seed's list explicitly. So a pointer from `:48` to `:42` leaves its reader in one of exactly two states. Either the correctness seed was not given `:42`, and a fresh, context-free reviewer silently applies a weaker rule than the one written — dropping Drift's ordinary-English exclusion restores precisely the false-positive class that sentence exists to suppress. Or the orchestrator ships `:42` into the design/plan prompt to make the pointer resolvable, which puts diff-mode text — added-lines scope, identifier spellings, a `docs/superpowers/` exclusion — in front of the one reader all three are wrong for. Both branches are worse than the repetition. **The argument is independent of how much text the pointer replaces**, down to a single sentence, which is what makes it decisive rather than a scope objection.
- **Repeating rather than pointing is this file's established answer, and the glossary supports it as far as it goes.** `:32` faces the same choice and transcribes `/simplify`'s four angles verbatim rather than point a subagent at them; `CONTEXT.md` defines a **Pass** as "a named, self-contained check". Stated at its real strength, though, and not beyond it: the **Pass** entry spells self-containment out over *trigger and stopping conditions*, and a reportability bar is a separately defined construct — `CONTEXT.md`, **Reportability rule** — which is the same distinction this document relies on when it weighs option (c) below. `:48` also opens by requiring an external document, the glossary. The property actually in play is therefore *complete as delivered*, not literal self-containment, and this bullet supports the ruling rather than carrying it.
- **The repetition is systematic, not accidental.** Three passages — the `:42` angle and the `:46` and `:48` passes — close with a findings-only hand-off, each phrased for its own subject matter. Two of them also share the ordinary-English exclusion and the never-flag-the-glossary refrain verbatim, and those two are exactly the passages that key off the glossary: the shared text tracks a shared input, not a copy-paste slip. House style is that a passage ships self-contained — its own trigger, its own reportability rule, and, where it hands a judgment call back to the resolvers, its own refrain for doing so. Deduplicating two instances of a three-instance pattern does not remove the pattern; it makes the file inconsistent about it.
- **The shared logic is smaller than it looks.** The table above compares five mechanics and **all five** differ. What is literally shared is two refrain sentences.

### Options considered

**(a) No change; record the ruling.**

**(b) Replace Drift's restated mechanics with a cross-reference.** **Rejected** — in the form the issue proposes, and in the narrowest form available, which is the one that has to be beaten.

*As the issue phrases it* — "apply the search-and-filter mechanics from Glossary conformance, scoped to the whole artifact" — the reference is broader than the overlap measured above. Per the table, all five compared mechanics differ, so this imports `:42`'s added-lines scope, its identifier spellings, and its `docs/superpowers/` path exclusion — and that last one excludes the very artifact Drift exists to search, since design and plan docs live there. Three explicit overrides is longer than the sentence it replaces and harder to read. Rubric: **"When reusing shared infrastructure, question whether each inherited behavior belongs in the new context — inherited-but-irrelevant behavior is a wart even when harmless."**

*At its narrowest* — leave Drift's scope, spellings and mention-vs-use test exactly as they stand and point only at the two sentences that genuinely are literal copies — that objection falls away, and the option still fails, for three reasons in descending weight. **First**, the decisive argument above applies unchanged: the `design`/`plan` correctness seed is never handed `:42`, so "as stated under Glossary conformance" names a section its only reader does not have. **Second**, it saves almost nothing. The two sentences are 107 and 87 characters; any pointer must still name its target, so each nets on the order of 25 characters — roughly 100 across the mirror pair — inside a `:48` that runs 2,030 characters. **Third**, neither sentence detaches cleanly. The ordinary-English sentence sits between Drift's positive candidate test and its mention-vs-use exclusion and closes "…is not a candidate." in exact parallel with the exclusion immediately after it; replacing it with a pointer breaks a three-sentence run the reader is using to track what counts. The never-flag-the-glossary sentence is a shared *tail* on two differently-conditioned clauses — `:42`'s "Where the glossary yields no entries to iterate this angle reports nothing: proceed silently —" against `:48`'s "If the glossary is missing, settles nothing about the term, or marks no names to avoid, grep and proceed silently —" — so pointing at it makes the reader resolve which condition it hangs off before it means anything.

Both forms carry one further cost: **invisible coupling across modes.** A future edit to the diff-mode angle would silently change what the design/plan pass means, with no textual divergence to notice. That is a strictly worse failure mode than the one the issue names, where the divergence is at least visible in the file.

**(c) Factor the shared refrains into one named rule both passages point at.** The repo even has the vocabulary — `CONTEXT.md` defines **Reportability rule**. **Rejected**, and this is the option worth taking seriously. It fails on rubric: **"Prefer correct-by-default seams over designs where each caller must remember a flag, ordering, or manual step."** A seed's prompt is composed from these passes by the orchestrator. Today a pass is correct as a standalone excerpt. Under (c), every composition would have to remember to include the shared-rules section as well — a manual step at every call site, silently producing an under-constrained reviewer when forgotten. That inverts the property the rubric asks for. It also adds a section to the file for zero behavioural gain, against **"Value simplicity … zooming out finds the right seam, it doesn't add layers."** And to be coherent it would have to touch `:46` too, since the findings-only refrain is three-way — and `:46`'s per-passage wording is exactly what a factored rule cannot hold.

**(d) Leave both texts alone and make the duplication machine-checked** — extend `check-sync.py` to assert the shared sentences are byte-identical *within* a copy, removing the drift risk without touching a word of either prompt. **Rejected on the merits, not on scope.** It would freeze a divergence this ruling holds to be legitimate: mode-specific passages are already allowed to differ on their reportability bars, and do, on every mechanic the table compares. A check forbidding `:48`'s ordinary-English exclusion from ever being tuned separately from `:42`'s enforces a coupling neither text claims and neither reader needs. It also spends a bespoke, string-keyed rule in a shared script — one more thing to update whenever the sentence legitimately changes — to protect two sentences. (`scripts/` is out of scope for this change in any case, per *Out of scope*; it is rejected here on substance so a later reader does not mistake exclusion for oversight.)

### The residual risk, stated honestly

The drift #29 names is real and this ruling accepts it. Its blast radius is bounded: if a future edit tightens `:42`'s ordinary-English exclusion and not `:48`'s, each passage remains internally coherent and the result is two slightly different reportability bars in two different modes — which is a thing mode-specific passages are already allowed to have, and already do, on every one of the five mechanics the table above compares. The failure mode is divergence, not incoherence. Trading that for cross-mode invisible coupling (option b) or for composition that is only correct when a caller remembers an extra section (option c) is a bad trade.

Rubric: **"Every change must earn its place; if the fix is worse than the wart, leave it."**

**Ruling: NO CHANGE.** Issue #29 closes with this section as its closing comment.

## The edit

Three lines change, identically, in **both** copies. Verified byte-identical across the pair today, so one replacement text serves both. No line is added or removed: line numbers stay `52`, `71`, `81`, the file stays **89 lines**, and `check-sync.py`'s summary stays `89 lines, 1 declared exception`.

Files:
- `plugins/dev-flow/skills/adversarial-review/SKILL.md`
- `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md`

Each block below is the **complete final line** as it must read in the file. Leading whitespace is significant — the line 71 block begins with three spaces. Copy these bytes; do not retype them.

### Line 52 (in both copies)

```
Every resolver (see Resolution procedure, below) applies this rubric, unchanged, as its judgment of what "best long-term design" means:
```

### Line 71 (in both copies)

```
   - Performs an **inline** adversarial self-check within its own context — it tries to break its own conclusion (counterexamples, simpler alternatives, hidden coupling) before concluding. **Resolvers never invoke `adversarial-review` or spawn further reviewer agents** — the protocol has exactly two tiers (seed reviewers, resolvers), and recursion is forbidden.
```

### Line 81 (in both copies)

```
**Resolvers** — the tier that determines the best long-term design and adversarially self-checks — run on `opus` (a harness alias, never a dated model id), unconditionally, with no session-model-dependent fallback. Their independence from the artifact's author is **contextual, not cross-family**: a fresh context window with no memory of authoring, an explicitly adversarial prompt, and a spawn that provenance verifies out of band. A session-model-conditional tier would buy back family separation only by making the resolver tier depend on ambient state, which the provenance check could no longer compare against a fixed expectation.
```

### Removed phrases — grep expecting zero hits

Scope every one of these to `plugins/`. Repo-wide they will still hit, correctly and by design: `docs/adr/0002-…` is an immutable dated record, and `docs/superpowers/` holds prior records plus **this document**, which quotes the removed text. Neither is to be "also fixed".

```
git grep -n 'group resolvers' -- plugins/      # expect: no output, exit 1
git grep -in 'group-resolution' -- plugins/    # expect: no output, exit 1
```

### The `group` that must survive

After the change, `group` (case-insensitive) appears on exactly **three** lines per copy, all of them the grouping *operation*, none of them a name for a tier:

- `:3` — the `description` front-matter, "then **groups** issues and resolves each" (out of scope; `check-sync.py` enforces it against `marketplace.json`)
- `:67` — "**Group** similar issues together. For each group, spawn one agent, on the resolver model"
- `:70` — "judging the group's findings together"

```
git grep -c -i 'group' -- 'plugins/*/skills/adversarial-review/SKILL.md'   # expect: 3 for each file (6 today)
```

## Version bumps

Text in this file ships into every model invocation, so a wording change is a behaviour change under `CLAUDE.md`'s bump rule, and the install cache is version-keyed — an edit at an unchanged version is never picked up on re-sync.

- `plugins/dev-flow/.claude-plugin/plugin.json`: **2.6.0 → 2.7.0**
- `plugins/dev-flow-worktree/.claude-plugin/plugin.json`: **1.8.0 → 1.9.0**

**Why minor and not patch.** Patch is the more literal semver reading — no rule, trigger, contract, or provenance format changes; the protocol says the same thing under one name instead of three. `CLAUDE.md` does not settle it: it requires a bump "on any behavior change" and says nothing about which segment, and a patch bump busts the version-keyed install cache exactly as well as a minor one. Minor is chosen on two grounds. (1) **Uniform precedent**: no version either plugin has ever shipped has a nonzero patch segment — `1.0.0`, `1.1.0`, `1.2.0`, `2.0.0/1.3.0`, `2.1.0/1.4.0`, … through `2.6.0/1.8.0` — verified across the full history of both `plugin.json` files. In a version log carrying no other signal, consistency is worth more than a finer distinction. (2) Establishing a minor-vs-patch convention is a repo-policy decision whose home is `CLAUDE.md`, which this change is scoped out of — adopting one silently here, in the very change that would be its first instance, is worse than not adopting one.

## Success criteria

Every item is mechanically checkable.

1. `python3 scripts/check-sync.py` exits **0** and reports `mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)`.
2. `claude plugin validate .` exits **0** with exactly **8** `No author information provided` warnings and no errors.
3. `git grep -n 'group resolvers' -- plugins/` → no output, exit 1.
4. `git grep -in 'group-resolution' -- plugins/` → no output, exit 1.
5. `git grep -c -i 'group' -- 'plugins/*/skills/adversarial-review/SKILL.md'` → `3` for each of the two files.
6. Each of the three fenced blocks in *The edit* appears **verbatim** in both copies, at lines 52, 71, and 81 respectively. Per `CLAUDE.md`, the implementation adds a short `python3` check that re-reads those three blocks **from this design doc on disk** — never retyped — and asserts each appears verbatim in both target files at the stated line index. Extraction rule for that check: the three blocks are the fenced blocks immediately following the headings `### Line 52 (in both copies)`, `### Line 71 (in both copies)`, and `### Line 81 (in both copies)`; each is a single line and leading spaces are part of it. Operational consequence, since this document is itself rewritten by the design review that precedes implementation: **whoever rewrites it must leave the three fenced blocks in *The edit* byte-identical.** Reading from disk buys "never retyped", not "the spec is immutable".
7. `plugins/dev-flow/.claude-plugin/plugin.json` has `"version": "2.7.0"`; `plugins/dev-flow-worktree/.claude-plugin/plugin.json` has `"version": "1.9.0"`.
8. **The branch's diff is exactly this change — file-scoped *and* line-scoped.**

   Let `BASE` = `git -C <working-dir> merge-base origin/main HEAD`. Do **not** hardcode a SHA: merge-base stays correct if `main` advances or the branch is rebased. Evaluate after committing, when the working tree equals `HEAD`.

   **(a) Files.** `git diff --stat $BASE..HEAD` touches only the two `SKILL.md` files, the two `plugin.json` files, and paths under `docs/superpowers/`. Any other path is a scope violation.

   **(b) Lines.** A short `python3` check compares each of the four non-doc files against its `BASE` blob by line index and asserts the set of differing 1-based line numbers:

   ```python
   import subprocess
   ROOT = "<working-dir, absolute>"
   def split_lines(text):            # check-sync.py's rule; agrees with `wc -l`
       out = text.split("\n")
       if out and out[-1] == "":
           out.pop()
       return out
   def changed(path, base):
       old = split_lines(subprocess.run(["git", "-C", ROOT, "show", f"{base}:{path}"],
                                        capture_output=True, text=True, check=True).stdout)
       new = split_lines(open(f"{ROOT}/{path}", encoding="utf-8").read())
       assert len(old) == len(new), (path, len(old), len(new))
       return {i + 1 for i, (a, b) in enumerate(zip(old, new)) if a != b}
   ```

   - each `plugins/{dev-flow,dev-flow-worktree}/skills/adversarial-review/SKILL.md` → exactly `{52, 71, 81}`;
   - each `plugins/{dev-flow,dev-flow-worktree}/.claude-plugin/plugin.json` → exactly one line, and that line contains `"version"`. Its *value* is criterion 7's business; the line number is deliberately **not** pinned, because line position is not a stable property of a JSON file.

   Paths are repo-relative — `git show <rev>:<path>` resolves them from the repo root. No hunk headers are parsed: the comparison is by line index, so the result does not depend on diff-algorithm choices, and a stray added or deleted line trips the `len(old) == len(new)` assert instead of silently shifting the set. `split_lines` splits on `"\n"` only, matching `check-sync.py`'s documented reasoning. (b) reads the working tree, so it is also runnable before the commit exists.

   **Why this criterion exists.** It closes the gap `CLAUDE.md` names — "text mangled identically in both sides passes [`check-sync.py`]". Criterion 6 says what the three changed lines must *say*; this one says that nothing *else* changed. Together they pin both `SKILL.md` files completely: each of the 89 lines is either byte-identical to `BASE` or one of the three blocks quoted in *The edit*. Two things therefore hold as corollaries and get no criterion of their own: both files are still **89 lines**, and `:42` and `:48` — the *Glossary conformance* and *Terminology collision and drift* passages — are **unchanged in both copies**, which is #29's NO CHANGE ruling holding mechanically rather than by an implementer's restraint.

## Out of scope

Hard-excluded. A proposal touching any of these is a blocker, not a design.

- **`CONTEXT.md`** — untouched, and the reason is scope, not sufficiency. The **Resolver** entry defines the tier correctly; what it does not do is reject `group-resolution agent`. Measured: `git grep -in 'group.agent' -- plugins/ CONTEXT.md` returns only `CONTEXT.md:15` — the existing `_Avoid_: group agent` provably does not match the longer phrase, since both passages grep each avoided name literally, spaced or hyphenated. So today a reintroduction would at best be caught by the glossary-conformance angle's *generous* limb ("names something the entry does not define") — the same false-positive-prone limb that produced #28. Adding the phrase to that `_Avoid_:` line is the seam-shaped version of this change: it would convert a generous-limb maybe into a strict-limb certainty. It is deliberately deferred, on two grounds — it is a glossary-policy decision carrying a standing cost (every `_Avoid_:` entry is grepped over every design and plan artifact forever, and every document discussing this history, including this one and ADR-0002, then leans on the mention-versus-use clause to stay clean), and `CONTEXT.md` is outside this change's authorized file set. Recorded as a follow-up issue instead; see **A7**. Note what is *not* being claimed: "after the edit no shipped text uses the phrase" says such a rule would catch nothing **today**, not that it would catch nothing.
- **`docs/adr/0002-opus-resolvers-and-the-end-of-adversary-not-author.md`** — says "group-resolution tier" at `:3`. An ADR is a dated historical record and is **deliberately left alone**; shipped prose moving past an ADR's wording is normal and is not drift.
- **`.claude-plugin/marketplace.json`** and the **`description`** line duplicated into it and into `SKILL.md:3` ("then groups issues and resolves each") — `check-sync.py` enforces the pair; `groups` there is the ordinary verb for the grouping operation and is correct. Untouched.
- **`scripts/check-sync.py`** — no new exception is needed; the three changed lines are identical in both copies, and the pair's one declared exception (line 12) is unaffected.
- **`CLAUDE.md`**, **`docs/agents/`**, the two plugin **`README.md`**s (neither mentions the tier by any `group`-qualified name), the two pipeline **`SKILL.md`**s (both already say `resolver`), and every **pre-existing file under `docs/superpowers/`** — prior records, including the passages quoted in this document.

## Assumptions

- **A1.** Line numbers 52 / 71 / 81 are correct as of base `c8b2182` and the three lines are byte-identical across the mirror pair — both verified. The implementation should match on **text**, not line number, and halt if a target line's current text differs from the pre-edit text quoted in this document.
- **A2.** `check-sync.py` needs no new declared exception, because all three edits are identical on both sides. If the run reports a new divergence, the edit was applied to only one copy — repair, do not declare an exception.
- **A3.** Nothing outside the mirror pair keys off the strings `group-resolution` or `group resolvers` — verified repo-wide; the only other occurrences are in `docs/adr/` and `docs/superpowers/`, both records.
- **A4.** `claude plugin validate .` emitting exactly 8 `No author information provided` warnings and exiting 0 is the expected pass state, per `CLAUDE.md`.
- **A5.** #28 closes on merge. **#29 closes with the *Issue #29* section above as its closing comment** — a recorded ruling with no code change is its complete outcome. Neither closure is part of the implementation; both are the pipeline's integration step.
- **A6.** No test framework exists in this repo; the checks in *Success criteria* are the whole verification surface.
- **A7.** One question this design identifies and defers is recorded as a follow-up GitHub issue rather than decided here: whether `group-resolution agent` belongs on `CONTEXT.md`'s **Resolver** `_Avoid_:` line, which is the only mechanism that would keep this normalization from silently regressing. Filing is the pipeline's integration step, alongside the #28/#29 closures in A5 — not part of the implementation, and it touches no file in this change's authorized set. The filer checks first that no equivalent open issue already exists.
- **A8.** A second deferred question is recorded the same way: criterion 8(b)'s line-set check is derived per change, but the property it buys — "nothing outside the intended lines moved" — applies to *every* mirrored-pair change in this repo, and its home is `CLAUDE.md`'s `Always:` list, which this change is scoped out of. `CLAUDE.md` today prescribes only the removed-phrase grep and the fenced-block check; neither catches an identical stray edit on both sides, the failure mode `CLAUDE.md` itself names. Filed as a follow-up issue, not blocking this change; same dedupe check as A7. The dedupe found **#24** ("Design-block reader: 20 byte-identical hand-copies across 4 changes, and `CLAUDE.md`'s 'no shared runner' ruling has outgrown its stated premise") — adjacent but not equivalent: #24 is about the *fenced-block* check being hand-copied, this is about a *second* check that is not in `CLAUDE.md` at all. Filed separately with an explicit cross-reference, since #24 is in flight and its resolution may well absorb this one.

## Spec self-review

- **Placeholders / TBDs:** none. Every changed line is given in full; both version numbers are stated; every grep is given as a runnable command with its expected result.
- **Internal consistency:** each replacement block is its target's current line with one substitution applied and every other byte carried over unchanged, line 71's three leading spaces included — `:52` `group-resolution agent` → `resolver`, `:81` `Group-resolution agents` → `Resolvers`, `:71` `group resolvers` → `resolvers`. Measured, not eyeballed: a character-level diff of each block against the current line in both copies reports edits only inside those spans, and success criterion 6 asserts those exact bytes land in both files. Success criterion 5 (`3` hits per file) is consistent with the enumeration in *The `group` that must survive* (`:3`, `:67`, `:70`) and with the measured baseline of 6.
- **Scope:** the authorized file set is the two `SKILL.md`s, the two `plugin.json`s, and this document. Criterion 8 checks it mechanically — 8(a) by file, 8(b) by line.
- **Ambiguity:** the one place a fresh implementer could go wrong is grep scope — the removed phrases legitimately survive in `docs/adr/` and in this document. Called out at the point of use, in *Out of scope*, and in A3.
- **Applying this skill's own passes to this document.** *Drift*, over the six names `CONTEXT.md` marks as ones to avoid (`finder`, `first-pass reviewer`, `group agent`, `judge`, `arbiter`, `boundary`), grepped case-insensitively over this file: five of the six — `finder`, `first-pass reviewer`, `judge`, `arbiter`, `boundary` — occur nowhere in this document outside this bullet, i.e. only in the enumeration just given and in this sentence, which is mention rather than use. `group agent` occurs outside it as well, and only as a mention each time: a `git grep` pattern in *What was verified*, a quotation of `CONTEXT.md`'s `_Avoid_:` line in *Weighing*, and the avoided form named in *Scope* — all excluded by "a term it merely *mentions* … is not a candidate". No occurrence of any of the six names the tier, which this document calls **resolver** throughout; `judge`'s inflected forms (`judgment`, `judging`) are not the term and carry their ordinary-English sense. **No finding.** *Glossary conformance* over the diff this change produces: the three added lines name the second tier `Resolvers`/`resolver`, exactly the concept `CONTEXT.md`'s **Resolver** entry defines, and contain no avoided synonym. **No finding** — the change is consistent with the rule that found it.
