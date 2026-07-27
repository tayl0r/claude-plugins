---
dev-flow:
  slug: gh-7-review-depth
  stops: [post-design]
  docs: commit
---

# gh-7: two depth gaps in `adversarial-review`'s seed passes

## Goal

Close the two review-depth gaps issue #7 reports, entirely inside `adversarial-review`'s **Seed passes** section, by adding one trigger-gated pass to the design/plan **correctness** seed and one trigger-gated angle to the diff **quality** seed. Family 1 (input-contract completeness) becomes a bounded per-field enumeration that fires only when an artifact newly accepts input from outside the code it describes, so a blanket "validate minimally" is treated as the claim under test rather than an exemption from the test. Family 2 (seam questioning) becomes a fifth diff-quality angle that fires only on constructs which cannot be defined without naming another construct plus a qualifier, and whose findings are reportable only when they name a specific relocation that *deletes* the construct **and** show that nothing reappears in its place — so every finding it can shape is a removal, while whether a named relocation is plausible remains the resolver tier's call (see Family 2's *Honest limits*). Neither family touches the shared design rubric, the four `/simplify` angles, the resolver tier, or anything outside these two files.

## Scope check — one change, not two

The issue holds two genuinely independent problems: different stage targets (design/plan vs. diff), different seed passes (correctness vs. quality), different risk profiles (Family 1 is a low-risk enumeration; Family 2 is the one that can turn into a false-positive machine). The decomposition check therefore has to be asked seriously. The answer is **one change**, and the reason is not convenience:

- **They land in the same two files, in the same section, and share one architectural decision.** Both edits are inside `## Seed passes` of the `adversarial-review/SKILL.md` mirror pair. Both are resolved by the same non-obvious ruling — *seed-side, not rubric-side* (see both families' decisions below). Splitting means establishing that ruling twice, and the second design would be mostly a restatement of the first.
- **Splitting is strictly more expensive with no isolation benefit.** Two changes means two version bumps of the same two plugins, two PRs mutating the same `check-sync.py`-enforced mirror pair within nine lines of each other, and a guaranteed rebase. The mirror pair's line-parallel schema makes overlapping edits in one region the exact thing that is annoying to land twice.
- **Bundling costs nothing in reversibility, which is the real worry.** Family 2 is the risky one, and the honest question behind "should these be separate?" is "can we back Family 2 out if it misbehaves?" It is a contiguous two-line insertion plus eleven words in one table cell, referencing nothing else and referenced by nothing else. Reverting it is a two-line delete and a cell edit whether or not Family 1 shipped in the same commit.

This is not a case of independent subsystems being forced together, so no halt is warranted. Family 2's risk is addressed by designing its trigger properly (below), not by shipping it separately.

## Where each change lands — stated precisely

`adversarial-review` runs a two-seed shape per mode. The seed contents differ per mode, and the **design rubric does double duty**: it is the design/plan *quality* seed lens **and** the judgment criteria every group-resolution agent applies in *all three* modes. That makes the rubric the single most expensive place in the file to add a sentence, and it is why neither family goes there.

| Family | Mode(s) | Seed | Concretely |
|---|---|---|---|
| 1 — input-contract completeness | `design`, `plan` | **correctness** | The prose-integrity checklist (table row `design`, inherited by row `plan`), plus a new below-table pass |
| 2 — seam placement | `diff` | **quality** | The `/simplify`-angles block, plus a new fifth angle outside the verbatim transcription |

Nothing lands in the design rubric, so the design/plan quality seed and every resolver prompt in every mode are byte-identical to today.

## Family 1 — input-contract completeness

### The decision

A new **correctness-seed** pass, gated on a trigger, bounded by three explicit stopping conditions, reported as findings and pruned by the existing resolver machinery.

**Trigger.** The artifact newly accepts input from outside the code it describes — an operator, an API client, a file, an upstream service. A design that only wires together internal calls never fires this pass.

**Stopping conditions (all three, or "enumerate the input surface" balloons):**

1. **Only fields the artifact *newly* accepts** — not the system's whole input surface, not fields the artifact merely reads. A design that adds three operator-settable fields enumerates three fields, regardless of how large the surrounding system is.
2. **Only input crossing into the described code from outside it.** Parameters passed between two functions the same design introduces are not input-contract surface; they are internal calls, and the correctness seed already covers internal inconsistency.
3. **Consumers are the ones the artifact names.** "What does each downstream consumer do with a degenerate value" is answered from the consumers the design or plan itself identifies — no codebase spelunking for unnamed callers. That keeps the pass bounded by the artifact's own text, which is what a findings-only prose reviewer should be bounded by.

Worst case is linear in the count of newly-accepted external fields. A design that newly accepts two hundred fields is a bulk-schema design where that enumeration *is* the work.

**Why a seed obligation rather than a resolver obligation or a gate.** The incident was a **noticing** failure, not a judgment failure: nobody produced the per-field list, so the resolver had nothing to weigh. Enumerating what a declared type permits that the domain does not is mechanical work a `sonnet` seed does well and cheaply. Once the gaps arrive as findings, the resolvers apply the rubric they already have — including *"a fix must be worth its complexity"* and *"every change must earn its place"* — and drop the fields where a degenerate value is harmless. That division of labor is exactly the protocol's existing shape, and it means the pass **cannot** become a mandate to validate everything: the pass can only surface, never decide.

**Why the *correctness* seed and not the quality seed.** One argument decides this; a second only checks the result is not a misfiling. **The decisive one is cost.** In design/plan mode the quality seed *is* the design rubric, and that rubric is also every group-resolver's prompt in all three modes — so "the quality seed" is not a second comparably-priced slot here, it is the widest-broadcast text in the file, and an input-contract bullet there would ship into diff-mode resolvers with no use for it. That rules it out on its own, whatever the pass's taxonomy. **The second is fit, and it is a check, not a proof.** The correctness checklist is document integrity — "placeholders/TBDs, internal contradictions, planning-blocking ambiguity, unstated assumptions, missing or untestable success criteria" — whereas this pass asks a reviewer to enumerate a declared type's degenerate values, which is more substantive than the rest of that list. It does fit under **unstated assumptions**: a blanket "validate minimally" that no per-field reasoning substantiates is exactly one, made specific. But "it fits" is the whole of the claim. It is *not* a finding that the correctness seed is where substantive engineering questions belong, and it must not be read as licence to grow that checklist on those grounds — anything else lands there on its own cost argument, or not at all.

**How `plan` mode inherits it.** The `plan` row's correctness cell already reads "The prose checklist above, plus plan-specific checks: …", so extending the `design` cell propagates for free. Because "the prose checklist above" *could* be read narrowly as excluding an appended clause, the new pass's own heading states both modes explicitly — `the design *and* plan correctness seed` — so a plan-mode seed prompt built from either reading includes it. Zero extra words in the table; the ambiguity a plan-writer would otherwise have to resolve is removed at the source.

### Rejected alternatives

**A rubric bullet ("enumerate the input contract before accepting a validation decision").** Rejected. The rubric is shared by the design/plan quality seed and all resolvers in all three modes, so this pays the widest possible context cost to serve two modes' correctness pass. It also mislocates the work: the rubric states what "best long-term design" means for a *decider*, and this is an enumeration for a *noticer*.

**A hard gate ("no design declaring minimal validation may pass review without a per-field table").** Rejected on two counts. It makes the review able to halt on a document-formatting requirement, and a halt is the pipeline's most expensive outcome — it hands back to a user who must then hand-write a table. And it inverts the protocol's chosen shape everywhere else: dev-flow surfaces findings and resolves them adversarially rather than blocking on checklists. A gate would also be wrong on the merits — some blanket validation decisions are correct, and the pass exists to make that a per-field conclusion, not to forbid the conclusion.

**Leave it to the resolvers ("resolvers must challenge any blanket validation decision").** Rejected. Resolvers only see what seeds report. If no seed reports the input surface, a resolver challenging "minimal validation" has to do the enumeration itself, at resolver cost, inside a context also holding every other grouped finding. Do the mechanical part where it is cheap.

## Family 2 — seam placement

This is the dangerous one, and the danger is precise: *"question where the seam is"* is one clause to write and produces a reviewer that proposes speculative restructuring on every diff — which the rubric explicitly forbids (*"widen the lens only against concrete demand … never speculation"*, *"if the fix is worse than the wart, leave it"*). A reviewer that always asks it manufactures expensive false positives and trains users to ignore resolvers. So the whole design question is: **what is the trigger?**

### The trigger discriminator, answered

**Discriminator: the diff adds a construct that cannot be defined without naming another construct plus a qualifier.**

That is the observable property. `ValidatableRegion` cannot be described except as *"`Region`, with fields loosened to `| null`"* — its definition requires naming `Region` and a qualifier. Contrast a genuinely new domain concept (`ShippingConfig`, `RateLimiter`): its definition stands alone. The first kind exists to **span a transformation** — it is the shape the data has between two points in the code, and it exists *because* the transformation happens where it happens. The second kind is not spanning anything; it *is* the thing.

That distinction is exactly what makes "should the structure change so this isn't needed?" a live question in one case and noise in the other. A construct that spans a transformation has a relocatable cause. A construct that is a concept does not.

Concretely, the shapes that satisfy the property — the issue's own "new type/flag/ordering", sharpened:

- a near-copy of an existing type with fields loosened (or added, or removed);
- a `raw`/`validated`/`pre-`/`post-` variant of one concept;
- a converter between two shapes of one concept;
- a flag whose job is to tell a callee which state its input is in;
- a newly required call ordering ("must call A before B").

The general rule governs and the list illustrates it, so a shape not on the list still fires if it satisfies the rule.

**The second half of the discriminator — the reportability rule — is what actually prevents false positives.** The trigger narrows *which diffs get asked*; this narrows *what may be reported*: **a finding is reportable only when the reviewer can name one specific other place to perform the transformation, name the construct that relocation deletes, and establish that nothing reappears in its place.** "The structure could be better" is not a finding. "Consider whether the seam belongs elsewhere" is not a finding. "Move normalization to the API edge and `ValidatableRegion` disappears" is a finding.

The third clause is what separates a misplaced seam from an ordinary boundary type, and it is load-bearing: a shape that exists to keep a wire, stored, or versioned contract decoupled from the domain type earns its keep wherever the transformation runs, so relocating the transformation does not delete it; and a diff that already performs the transformation at the place a reviewer would move it to has nowhere to move it. Without this clause the rule admits every request/response DTO and every `raw`/`validated` wrapper, because "just parse at the API edge and the DTO disappears" is always nameable — and those splits are frequently the intended end state, not a symptom. `ValidatableRegion` fails both escapes — it is an internal bridge, not a contract, and normalization did not happen at the edge — which is why it remains a finding while a request DTO with a mapper does not.

This is the property that makes the angle rubric-compatible rather than rubric-violating. Every finding it can produce is **net-negative in complexity** — it removes a construct rather than adding a layer. That is precisely what the rubric's *"zooming out finds the right boundary, it doesn't add layers"* licenses, and it is why the angle needs no rubric change to be resolvable: a resolver handed "move X to Y, and Z is deleted" already has the criteria to judge it. It is also falsifiable in a way "restructure this" is not, so a resolver can research the named place and reject the finding cheaply.

It is, in shape, `codebase-design`'s **deletion test** applied to a relocation rather than to a module in place — see the skills question below.

### Honest limits of the discriminator

- **False negatives are real and accepted.** A misplaced seam that produces no definable-by-reference construct — say, the same normalization duplicated inline at three call sites with no bridge type — does not fire this trigger. The `Reuse` angle may catch that one; this angle will not. Broadening the trigger to cover it is the false-positive machine, so the coverage gap is taken deliberately.
- **The reportability rule is prose, not a type system.** A reviewer can name an implausible place, or assert "nothing reappears" without checking, because a `sonnet` seed sees `BASE..HEAD` and not the codebase. What the rule buys is not prevention but *falsifiability*: every reportable finding is a stated, checkable claim about one named location, which the resolver tier researches and can reject in one read. This is residual, not eliminated — and the Goal is worded to say so.
- **The trigger fires more often than "rare."** On a product repo roughly one diff in five adds a construct definable only by reference — DTO/mapper pairs, wrappers, form-state shapes, versioned payloads. The third reportability clause, not the trigger, carries the false-positive load. Budget one resolver group on that fraction of PRs.
- **Overlap with `Altitude` is real, and the addition still earns its place.** `Altitude` asks whether *the changed code* sits at the right layer; this angle asks whether a transformation *elsewhere* is positioned such that the changed code need not exist at all. Different subject. A sharp reviewer might have reached the same place through `Altitude`; the incident is evidence that leaving it implicit is not reliable.

### Observable success criterion

If this angle fires on most diffs, the trigger is wrong. Expected behaviour on a product repo is that roughly one diff in five *fires* the trigger, and that most of those produce nothing because the construct survives its transformation moving. Fires are not the metric; reported findings are. A run of PRs where this angle contributes findings at a rate comparable to `Simplification` is evidence the trigger has been read too loosely and should be narrowed or reverted — a two-line delete, per the scope check.

### Rejected alternatives

**Edit the `Altitude` angle to cover it.** Rejected, and this is a hard constraint rather than a preference. Line 32 declares that `/simplify` is a harness built-in with no readable file, "so its four angles are transcribed verbatim below instead." Editing a bullet inside that block — or appending a fifth bullet to it — makes the verbatim claim false and creates silent drift the next person to diff against the built-in cannot detect. The addition therefore lands *outside* the bullet list, as its own paragraph. What the verbatim claim binds is the **four bullets' content**, not the wording of the header line above them: that header is this skill's own prose, so it *is* edited (see the change list) to announce the fifth angle and instruct that all five apply — which is what keeps the addition reachable by a prompt-builder that extracts the block rather than reading the section whole. The bullets and line 32 are untouched.

**Use `codebase-design`'s two-adapter rule as the trigger** (*"One adapter means a hypothetical seam. Two adapters means a real one"*). Rejected on category. The rule governs **ports and adapters** — an injected interface with implementations behind it — and its operative form (*"Don't introduce a port unless at least two adapters are justified"*) lives in `DEEPENING.md:29`, not the `SKILL.md` this design borrows the deletion test from; `SKILL.md:65`'s narrower variant reads *"Don't introduce a seam unless something actually varies across it."* `ValidatableRegion` is a data shape with no adapters, so a two-adapter trigger is silent on the exact incident this angle exists for, while firing on every ordinary repository/gateway interface whose second adapter is a test fake. It tests for speculative abstraction, which `Altitude`'s "not over-abstracting a one-off" already covers.

**A rubric bullet ("question where the seam is, not only whether the construct is necessary in place").** Rejected. Widest context cost, wrong tier, and unnecessary: the rubric already carries *"zooming out finds the right boundary, it doesn't add layers"*, which licenses a seam relocation the moment one is on the table. The incident's failure was that none was ever on the table — a seed-side noticing failure, not a resolver-side judgment failure. Fixing the rubric would be fixing the tier that behaved correctly given its inputs.

**Ask it of every new type ("for each type this diff introduces, could a restructuring remove it?").** Rejected — this is the exact failure mode the design has to avoid, and the rubric names it: speculation.

**Add a third seed pass to `diff` mode (a "structural" seed).** Rejected. It raises diff-mode seed cost by 50% for one question, and it breaks the uniform two-seed shape that the whole Seed passes section, and the provenance line's expectations, are written around. The question fits inside the existing quality seed.

**Invoke or recommend `codebase-design` / `domain-modeling`.** Rejected — see below.

## The `codebase-design` / `domain-modeling` question

The issue suggests invoking or recommending these when a stage introduces new domain types. Grounded in what the two skills actually contain (read at `~/.claude/plugins/cache/mattpocock/mattpocock-skills/1.2.0/skills/engineering/`), the answer is **neither invoke nor recommend — borrow one principle instead.**

**`domain-modeling` is disqualified on mechanism.** Its body is user dialogue: *"call it out immediately"*, *"propose a precise canonical term"*, *"force the user to be precise"*, *"offer to create an ADR"*. That is the same disqualifier that already bars `brainstorming` from this pipeline — dev-flow's stated corollary is that a skill whose core mechanism is user dialogue cannot be dispatched at all. It also *writes* repo state (`CONTEXT.md`, `docs/adr/`), which a findings-only seed may not do and which falls outside `adversarial-review`'s "owns the artifact end-to-end" contract. And its subject is project-wide vocabulary, not the artifact under review. There is nothing here to invoke and nothing to borrow.

**`codebase-design` is disqualified on two counts, one structural and one substantive.**

- *Structural:* dev-flow's flat topology makes the orchestrator the only spawner — Claude Code 2.1.218 does not grant spawned subagents the `Agent` tool. A review leaf is a leaf. It cannot invoke a skill that spawns, and `codebase-design`'s own "going deeper" path is `DESIGN-IT-TWICE.md`, which is explicitly a parallel sub-agent pattern. Wiring it in would mean the orchestrator running it in-context at review time, i.e. a new fan-out tier in a protocol that declares itself to have exactly two.
- *Substantive, and the more important one:* `codebase-design` is a **vocabulary**, not a procedure. Its content is a glossary (module, interface, depth, seam, adapter, leverage, locality), a deep-vs-shallow contrast, and a short principles list. There is no pass to run. Invoking it would load a glossary into a reviewer that then has to invent the check anyway — which is the check this design had to write regardless. The issue's suggestion assumes the skill contains the missing question; it contains the words for stating it.

**What is borrowed.** One principle in `codebase-design` is directly load-bearing here — **the deletion test**: *"Imagine deleting the module. If complexity vanishes, it was a pass-through. If complexity reappears across N callers, it was earning its keep."* Family 2's reportability rule is that test applied to a relocation instead of to a module in place, **both halves of it**: name the other place and what its deletion removes (*complexity vanishes*), and establish that nothing reappears in the construct's stead (*complexity reappears across N callers → it was earning its keep*). The second half is what excludes ordinary wire/storage/version boundary types. That shape is inlined into the angle rather than taken as a dependency. The term **seam** — which `codebase-design` prefers and explicitly defends over "boundary" — is also adopted, at zero cost, and matches the vocabulary the issue itself uses.

**Why inline rather than depend.** `mattpocock-skills` is a third-party marketplace referenced nowhere in this repo today. dev-flow's only cross-plugin dependencies are on `superpowers` skills it names explicitly and pins carefully (see the pinned-template clause). Adding a soft "consider invoking `codebase-design`" line into a SKILL.md that ships into every review invocation would cost words to emit an instruction a leaf cannot act on. One borrowed principle, stated in place, is the whole of the available value.

## Context cost, weighed

`plugins/dev-flow/skills/adversarial-review/SKILL.md` is 1,900 words today and ships into every review invocation of both plugins. The two additions total 303 words, plus a net +11 on the angles-block header and ~11 in the two table cells — about **+17%**. That is a real cost and it needs an explicit defence:

- **The cost is context tokens, not reasoning.** Both passes lead with their trigger. A diff that adds no definable-by-reference construct, and a design that accepts no new external input, each read one clause and stop. The runtime cost on a non-triggering artifact is a sentence.
- **The length is load-bearing, and the cheap version is worse.** For Family 2 in particular, the words doing the safety work *are* the trigger clause and the reportability rule. A terse "question where the seam is" would cost a tenth as much and produce exactly the speculative-restructuring reviewer this design exists to avoid. Here, shorter is not simpler — it is a different, worse design.
- **This section of the file is its payload.** The rest of the skill is contract, working-directory, and model plumbing; Seed passes is where the review's actual content lives. Two evidenced misses closing into that section is what the file is for.

A shorter variant was drafted and rejected on the second point. No other place in the file was shortened to pay for this: trading unrelated precision for room would be a false economy.

## Exact change list

Five files. Every wording below is literal.

### 1 & 2. `plugins/dev-flow/skills/adversarial-review/SKILL.md` and `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md`

A declared `check-sync.py` mirror pair. **Every edit below lands byte-identically in both files.** None of the new or edited text contains a `dev-flow` or `dev-flow-worktree` token, so the two copies are literally identical in every touched region and the mirror check's canonicalization has no work to do there — one less thing for a future editor to get wrong.

Five edits: three in-place line replacements and two symmetric two-line insertions. Line numbers below are the current (pre-change) file; the three replacements are in place, so none of them shifts the insertion points.

#### Line 28 — Seed passes table, the `diff` row

The quality cell currently says "four angles"; a fifth angle is added below it, so the cell must point at it or it becomes wrong. Replace the whole line with:

```
| **diff** | `/simplify`'s four angles plus this skill's seam-placement angle, inlined (below), findings-only, run against `BASE..HEAD`. | The superpowers `code-reviewer.md` template, used as designed (already read-only/findings-only) — see "Pinned template," below. |
```

Only the quality cell changes; the correctness cell is verbatim as today.

#### Line 29 — Seed passes table, the `design` row

The correctness cell gains a pointer to the new pass, following the file's own idiom (every other below-table expansion is pointed at from its cell). Replace the whole line with:

```
| **design** | The design rubric (below) *is* the lens, applied adversarially to the proposed approach. | A prose-integrity checklist: placeholders/TBDs, internal contradictions, planning-blocking ambiguity, unstated assumptions, missing or untestable success criteria — plus the input-contract completeness pass (below). |
```

Only the correctness cell changes. **Line 30 (the `plan` row) is not edited** — its "The prose checklist above" reference carries the addition, and the new pass names both modes in its own heading.

#### Line 34 — the angles-block header

The header currently asserts the block is complete at four, and it is the last structure a prompt-builder reads before extracting it. A builder that resolves the `diff` cell by grabbing "the four-angle block" would stop at `Altitude` and never reach the fifth angle — the table cell's pointer is consumed several steps earlier and does not intercept that shortcut. The header is this skill's own prose, not transcribed text, so editing it leaves line 32 and the four bullets' content untouched. Replace the whole line with:

```
**The four `/simplify` angles (verbatim), then a fifth of this skill's own — all five apply:**
```

This also makes any residual truncation self-detecting: a seed prompt that announces five and carries four is visibly short to the reviewer receiving it, where today the omission is silent.

#### Insert after line 38 (the `Altitude` bullet) — the fifth angle

Insert exactly two lines: one empty line, then this line. It goes *after* the four-bullet block, so the bullets' content and line 32's "transcribed verbatim below" claim both stay true; the edited header on line 34 is what makes it reachable, so the angle itself carries no provenance preamble and matches the bullets' `**Name:** description` idiom.

```

**Seam placement:** applies only where the diff adds a construct that cannot be defined without naming another construct plus a qualifier: a near-copy of an existing type with fields loosened, a `raw`/`validated` variant of one concept, a converter between two shapes of one concept, a flag telling a callee which state its input is in, a newly required call ordering. Each spans a transformation, so "is it necessary as things stand?" is the wrong question — the answer is nearly always yes. Ask instead where the diff performs that transformation, and whether performing it at one *specific* other place deletes the construct outright. Then apply the deletion test to what you propose deleting: if the construct is what keeps a wire, stored, or versioned contract decoupled from the domain type, that reason survives the transformation moving and there is no finding; likewise if the diff already performs the transformation at the place you would move it to. Report only when you can name the place, the deletion, and that nothing reappears in the construct's stead — this angle proposes removals, never a restructuring whose payoff is a nicer structure.
```

#### Insert after line 40 (the `Pinned template` paragraph) — the input-contract pass

Insert exactly two lines: one empty line, then this line. Placing it after the pinned template keeps the three diff-mode notes contiguous (lines 32, 34–40 pre-change) and puts the design/plan note last.

```

**Input-contract completeness — the design *and* plan correctness seed:** applies only to fields the artifact newly accepts from outside the code it describes (an operator, an API client, a file, an upstream service). For each, report the gap between what its declared type permits and what the artifact says the domain allows — empty string, negative, fractional, out of range, `NaN`, duplicate within a collection, absent optional — and what each downstream consumer the artifact names does with a degenerate value. A blanket "validate minimally" or "the type is enough" is the claim this pass tests, per field, never an exemption from it. Findings only: which gaps are worth guarding is the resolvers' call.
```

#### Resulting file shape

Both copies go from **81 to 85 lines**. Post-change layout of the affected region:

| Line | Content |
|---|---|
| 28 | `diff` row (edited) |
| 29 | `design` row (edited) |
| 30 | `plan` row (unchanged) |
| 34 | angles-block header (edited) |
| 35–38 | the four `/simplify` angle bullets (unchanged) |
| 39 | empty (new) |
| 40 | the fifth angle (new) |
| 42 | `Pinned template` (unchanged, was 40) |
| 43 | empty (new) |
| 44 | input-contract completeness pass (new) |
| 46 | `## The design rubric` (unchanged, was 42) |

Old lines 39–40 shift by +2 — they sit between the two insertion points — and everything from the old line 41 onward shifts by +4. The declared exception's line (12) is above every edit and does not move.

**Explicitly unchanged in these files:** the four `/simplify` angle bullets (their content, and there are still exactly four of them), line 32, the design rubric (all nine bullets), the Resolution procedure, the Model section, the provenance line, Review integrity, Working directory, the Contract, and the frontmatter `description`. The header line above the four bullets *is* edited — it is this skill's own prose, not part of the transcription.

### 3 & 4. Version bumps

- `plugins/dev-flow/.claude-plugin/plugin.json` — `"version": "2.3.0"` → `"version": "2.4.0"`.
- `plugins/dev-flow-worktree/.claude-plugin/plugin.json` — `"version": "1.5.0"` → `"version": "1.6.0"`.

Mandatory, not cosmetic: the install cache is version-keyed (`~/.claude/plugins/cache/taylor-plugins/<plugin>/<version>/`), so an edit at an unchanged version is never picked up on re-sync. Minor rather than major — the skill's invocation signature, contract, provenance format, and mode set are unchanged; only seed content changes.

### 5. `CLAUDE.md` — the design-conformance check, as standing policy

Verification step 6 (below) is a mechanical check that the inserted and replaced prose matches this document byte-for-byte. It is the **second** instance of that gap in this repo, and the two instances differ instructively. `gh-10` hit it and solved it *inside its plan* (`Task 5 Step 4b`), where the fix stayed — this design had to rediscover the same need from scratch. `gh-10`'s *other* backstop, the residue grep, was written into `CLAUDE.md` instead, and it propagated: §Verification steps 3 and 4 exist, and are argued for below, because the auto-loaded `CLAUDE.md` asks for them. Same repo, two consecutive changes, one seam that carried and one that did not. The check therefore goes where the next change inherits it rather than reinvents it.

`CLAUDE.md` is the right boundary and `dev-flow`'s own `SKILL.md` is not: this is repo-local contributor guidance about how a change in *this* tree is verified, it ships into no plugin and costs no invocation context, and it is where the sibling residue-grep policy already lives. The rule states the obligation and the technique, not a reusable script — the block-to-file mapping and the shape assertion differ per change (`gh-10`: eight one-line blocks; this change: `[1, 1, 1, 2, 2, 2]`), and turning that into a generic runner would require a machine-readable annotation schema on every design doc, which two instances do not justify.

Insert after the `## Workflow` paragraph (line 15) exactly two lines: one empty line, then this line.

```

When a change's replacement or inserted text is given as fenced blocks in a design doc, its verification must include a design-conformance check: a short `python3` script that re-reads those blocks from the design file on disk — never retyped — and asserts each appears verbatim in its target file, and for an insertion, directly after its anchor line. `check-sync.py` and the residue/presence greps test line counts, presence, and absence only; text mangled identically in **both** copies of a mirrored pair passes every one of them, and this is the check that catches it.
```

`CLAUDE.md` goes from 29 to 31 lines. No other line moves content; `check-sync.py` never reads this file (it names it only in error strings), and no plugin ships it.

### Blast radius — verified complete

A repo-wide search of tracked files outside `docs/superpowers/` for `seed pass`, `four angles`, `simplify`, `prose-integrity`, and `correctness seed` returns hits **only** in the two `adversarial-review/SKILL.md` copies. Specifically confirmed to need no edit:

- **Both pipeline `SKILL.md` copies** (`plugins/dev-flow/skills/dev-flow/SKILL.md`, `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`). They invoke the review by mode and delegate seed content entirely; neither enumerates or describes a seed pass. This is what keeps the hand-mirrored pair out of the change (see Verification).
- **Both `README.md` files** — zero hits for `seed`, `angle`, `rubric`, or `checklist`.
- **`.claude-plugin/marketplace.json`** — no `description` changes anywhere, and Check A does not read `version`.
- **`scripts/check-sync.py`**, `.github/workflows/`, `docs/agents/*.md` — untouched. **`CLAUDE.md`** gains one paragraph (§5 above) and nothing else; it is repo-local contributor guidance, ships into no plugin, and `check-sync.py` never reads it (it names the file only in error strings).
- **`plugins/better-code-review/`** — exists in this repo but is referenced nowhere by dev-flow (the diff correctness seed pins the *superpowers* `requesting-code-review/code-reviewer.md`), and the issue assigns its backstop to #37 regardless. Out of scope.

## Sync constraint — how `check-sync.py` still passes

**Check B (mirror pair `adversarial-review`)** requires the two files to be line-for-line identical after substituting `dev-flow-worktree` → `dev-flow` on both sides, except the one declared exception at line 12.

1. **All four edits land in both files.** A one-sided edit produces an undeclared-divergence failure naming the line.
2. **Insertions are symmetric, so the line counts stay equal.** Both files go 81 → 85. The pair's schema expresses only same-index one-line-for-one-line divergences, so an asymmetric insertion could not be declared as an exception even if someone wanted to — it would be a `LINE_COUNT_FIX` failure. Adding lines is fine here; adding them to only one side is not.
3. **No new variant token is introduced.** The added and edited text contains no `dev-flow` / `dev-flow-worktree` occurrence, so the touched lines compare equal before canonicalization does anything.
4. **The declared exception still fires and does not go stale.** It covers line 12, which is above every edit and does not shift; the "stale exception" check stays satisfied.

**Check A (manifest descriptions)** compares `name`, `source`, and `description` between each `plugin.json` and its marketplace entry, and does not read `version`. This change edits only `version`, so Check A is unaffected and `.claude-plugin/marketplace.json` is not touched.

**The hand-mirrored pipeline `SKILL.md` pair is not edited at all**, so no hand-mirroring risk is incurred by this change (see Verification for what `CLAUDE.md`'s residue-grep policy asks for here and why).

## Out of scope

- **`Loot-Labs/claude-plugins#37`** — the finder-prompt fixes (`ar-doc-reviewer`, `ar-simplicity`, and a `better-code-review` backstop) in a different organisation's repo, **unreachable from this environment**. This design does not read, reference, depend on, or constrain that work. Per issue #7's own stated boundary, #37 owns finder prompts elsewhere and #7 owns dev-flow's stage reviews here. Every change in this doc is confined to two files in this repo, so nothing here can conflict with whatever #37 does.
- **`Loot-Labs/boxed-backend#2424`** — also unreachable. The issue's account of the incident is the sole evidence and is taken as accurate; no attempt is made to verify field names, types, or the eventual fix.
- **The pipeline `SKILL.md` pair, the Artifact Contract, the resume table, the stop boundaries, and the model policy.** Untouched, per the issue's scope.
- **The design rubric.** Deliberately unchanged, in both families, for the reasons argued above — not overlooked.
- **The four `/simplify` angles' content and line 32.** Unchanged by the verbatim-transcription constraint. The header line above the bullets is in scope and is edited — the constraint binds what the bullets say, not how this skill introduces them.
- **`mattpocock-skills` as a dependency.** Neither plugin gains a reference to `codebase-design` or `domain-modeling`; one principle is inlined instead.
- **`plugins/better-code-review/`** — assigned to #37 by the issue and unreferenced by dev-flow.
- **Historical `docs/superpowers/specs/` and `docs/superpowers/plans/` documents.** Immutable records of what was decided at the time; none may be edited, and the verification greps exclude them.
- **`.superpowers/` SDD scratch** — git-ignored, per-run, never repo content.

## Verification

Run every step from the repo root; all must pass.

1. **Mirror and manifest sync:**

   ```sh
   python3 scripts/check-sync.py
   ```

   Expect `check-sync: all checks passed`, with the mirror pair reporting **`85 lines, 1 declared exception`**. The line count is the assertion that the insertions were symmetric.

2. **Marketplace validation:**

   ```sh
   claude plugin validate .
   ```

   Expect success. **8 missing-author warnings are expected** and are not a failure.

3. **Residue grep — the two in-place edits left no old text behind:**

   ```sh
   git grep -nF -e 'four angles, inlined (below)' -e 'untestable success criteria. |' -e '(verbatim):**' -- ':!docs/superpowers'
   ```

   Expect **no output** (exit 1). Each of the three in-place replacements removes exactly one of these substrings — two table cells and the angles-block header. `check-sync.py` cannot cover this: it compares the two copies *to each other*, so an edit missed on **both** sides leaves them identical and passes clean. Only a residue grep sees that. `-F` is deliberate — the patterns contain `(`, `)`, and `|`, and a fixed-string match avoids regex interpretation. The pathspec excludes the immutable historical specs and plans; `git grep` reads tracked files only, so the git-ignored `.superpowers/` scratch is excluded automatically.

4. **Presence grep — the two insertions landed in both copies:**

   ```sh
   git grep -nF -e '**Seam placement:**' -e 'all five apply' -e 'Input-contract completeness' -- ':!docs/superpowers'
   ```

   Expect **exactly six lines**: each phrase once in `plugins/dev-flow/skills/adversarial-review/SKILL.md` and once in `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md`. This is the insertion-shaped counterpart to step 3, covering the same both-sides-missed blind spot for text that is added rather than removed — including the header rewrite, which step 3 only proves was *deleted*, not that its replacement arrived.

5. **Version spot-check:**

   ```sh
   grep -n '"version"' plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
   ```

   Expect `2.4.0` and `1.6.0`.

6. **Design conformance — every block landed verbatim, in the right place.** This is the one step steps 1–5 structurally cannot provide, and it replaces a manual side-by-side read. Step 3's residue patterns are tied to the three in-place replacements, and step 4 matches only each insertion's *opening* phrase, so a word mangled further into an inserted line passes both. Step 1 compares the two copies only to *each other*, so the same mangling applied identically to both also passes, at the correct 85 lines. This check reads the expected text from the design file on disk — never retyped — and requires a byte-for-byte line match in each target, plus, for the three insertions, that the block sits directly after its anchor line. That last part matters: the fifth angle inserted *inside* the four-bullet block instead of after it would falsify line 32's "transcribed verbatim" claim while passing every other check here. Copy the script exactly; it is deliberately pure ASCII, so a mistyped copy fails loudly instead of passing. **The fence is unindented on purpose** — a `python3` heredoc indented under the list item is an `IndentationError`.

```sh
python3 - <<'PY'
import sys
from pathlib import Path
DESIGN = "docs/superpowers/specs/2026-07-27-gh-7-review-depth-design.md"
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
assert [len(b) for b in blocks] == [1, 1, 1, 2, 2, 2], "design code-block shape changed; stop and re-read the design"
PAIR = ["plugins/dev-flow/skills/adversarial-review/SKILL.md",
        "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md"]
SPEC = [("line 28, diff row",     blocks[0], None,                  PAIR),
        ("line 29, design row",   blocks[1], None,                  PAIR),
        ("line 34, block header", blocks[2], None,                  PAIR),
        ("fifth angle",           blocks[3], "- **Altitude:**",     PAIR),
        ("input-contract pass",   blocks[4], "**Pinned template",   PAIR),
        ("CLAUDE.md rule",        blocks[5], "Changes land via PR", ["CLAUDE.md"])]
bad = []
for name, want, anchor, targets in SPEC:
    for path in targets:
        L = Path(path).read_text(encoding="utf-8").split("\n")
        at = [i for i in range(len(L) - len(want) + 1) if L[i:i + len(want)] == want]
        if len(at) != 1:
            bad.append((name, path, "found %d times, want exactly 1" % len(at)))
        elif anchor is not None and not L[at[0] - 1].startswith(anchor):
            bad.append((name, path, "sits after %r, want %r" % (L[at[0] - 1][:40], anchor)))
for name, path, why in bad:
    print("MISMATCH:", name, "in", path, "--", why)
print("design-conformance:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

   Expect exactly `design-conformance: OK` and `exit=0`. A `MISMATCH` line names the block and the file whose text or position differs — re-paste that block from §Exact change list and re-run from step 1. The shape assertion (`[1, 1, 1, 2, 2, 2]`) fires if this document's plain-fenced blocks are ever added to, removed, or reflowed: that is deliberate, because the blocks are indexed positionally. Every fenced block in this Verification section carries the `sh` info string and is therefore skipped by the `mode == ""` filter, so adding or editing a verification step never disturbs that index — keep it that way.

**On `CLAUDE.md`'s residue-grep policy.** The policy binds "any hand-mirrored edit." This change edits **no** hand-mirrored file — the pipeline `SKILL.md` pair and both `README.md`s are untouched, and the only mirrored pair it touches is the machine-checked one. The policy is therefore vacuously satisfied. Steps 3 and 4 apply the same idea anyway, aimed at the *machine-checked* pair's one real blind spot (an edit missed on both sides), because that blind spot is genuine and the greps are free. Step 6 extends the same reasoning from residue to content, and §5 writes it back into `CLAUDE.md` next to the residue-grep policy it complements, so the next change inherits both.

## Assumptions recorded

- **`Loot-Labs/claude-plugins#37` and `Loot-Labs/boxed-backend#2424` are unreachable from this environment**, per the dispatch. #7's own stated boundary is used as the scope line, and the incident narrative in #7 is taken as accurate without verification. Consequence for the design: nothing here depends on, duplicates, or constrains #37, because every change is confined to two files in this repo.
- **Minor version bumps.** `2.4.0` and `1.6.0`. Behaviour changes; no interface does.
- **The `plan` row needs no edit.** Its correctness cell's "The prose checklist above" reference is taken to carry the appended pass. The new pass's heading names both modes explicitly, so this holds under either reading of that reference — the assumption is defensible because it is made unnecessary by construction.
- **The `/simplify` four-angle block is genuinely a verbatim transcription** of the harness built-in, as line 32 states. The claim binds the **four bullets' content**: they are not edited, and no fifth bullet joins them. The header line above them is this skill's own prose and is edited; the fifth angle is a paragraph after the list.
- **Seed prompts are constructed from the Seed passes section**, and a below-table expansion is reached only if the structure *on the path to it* says so. Both new passes follow the file's existing pointer idiom from their table cell. For the fifth angle that pointer is deliberately not relied on alone: a builder that resolves the cell by grabbing "the four-angle block" stops at `Altitude`, so the block's own header is edited to announce the fifth angle. The cell is the first line of defence; the header is the one standing on the path the shortcut takes.
- **Wording that avoids the variant token is preferred over per-copy wording.** "this skill's own" rather than "dev-flow's own" — either would pass `check-sync.py` (canonicalization erases the difference in both directions, so the check could not catch a wrong choice), which is precisely why the token is avoided rather than chosen.
- **Family 2's coverage gap is accepted, not solved.** Seam misplacements that produce no definable-by-reference construct are outside this trigger. The alternative — a broader trigger — is the failure mode the design is built to prevent.
