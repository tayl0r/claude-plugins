---
dev-flow:
  slug: gh-16-terminology-collision
  stops: [pre-merge]
  docs: commit
---

# gh-16: terminology collisions are invisible to stage reviews

## Goal

Close issue #16 with one trigger-gated pass on `adversarial-review`'s **design and plan correctness seed**, so a design that adopts a word the repo already uses for something else is reported as a finding instead of shipping. The pass reads the repo's domain glossary first and greps for what the glossary does not settle, because two of the three known collisions were against prose no glossary covered. It is findings-only and read-only: it never renames anything, never writes `CONTEXT.md`, and never proposes creating one. Nothing lands in the design rubric, the `/simplify` angles, the resolver tier, or `diff` mode.

## The evidence, restated

Three real instances, all shipped:

| Term | Artifact's sense | Colliding sense | Where the collision lived |
|---|---|---|---|
| `seam` | code-level, from `codebase-design` | protocol-level (`Step-0 seam`, "user-directed seams") | pipeline `SKILL.md` prose |
| `family` | the plugin family the two dev-flow variants share | model family (`family match`, `cross-family`) | `adversarial-review` `SKILL.md` prose |
| `angle` / `pass` | used interchangeably | two different things: a lens *inside* a seed vs. a whole check | the artifact itself |

The `seam` instance is the control. gh-7's design went through a full design-stage review — 2 `sonnet` seeds, 3 `opus` resolvers, ~484k tokens — and all five missed it. A `/grill-with-docs` run on the same document immediately afterwards found it, along with `angle`/`pass`.

**Why the existing seeds miss all three.** The quality seed applies the design rubric, which is about *design* quality — and all three documents were sound designs. The correctness seed checks document *integrity*: placeholders, contradictions, planning-blocking ambiguity, unstated assumptions, missing success criteria. Two of the three instances are invisible to it by construction — `seam` and `family` sit in internally consistent documents and are wrong only from outside, against the rest of the repo's language, and nothing in the protocol looks outside.

`angle`/`pass` is different, and the design should say so rather than round it off. It lives *in the artifact*, so on its face it is an internal contradiction — and "internal contradictions" and "planning-blocking ambiguity" are in that checklist today. The claim is not that the existing bullets are out of scope; it is that they are empirically insufficient. Both were already in the `design` correctness cell when gh-7's own design review ran (`git show 4e32e0e~1`, line 29), and that review — two `sonnet` seeds, three `opus` resolvers, ~484k tokens — still shipped `angle` and `pass` used interchangeably; a `/grill-with-docs` run found it minutes later. The reason is structural rather than a fluke: a reviewer hunting contradictions compares what sentences *assert*, and here every sentence asserts something true. The contradiction is in what one word *denotes* across them, which is visible only to a reviewer told to hold a term fixed and check its senses. That is what the against-itself clause instructs, and it is why the clause is a pointed restatement rather than a duplicate.

## Where the change lands

| Mode(s) | Seed | Concretely |
|---|---|---|
| `design`, `plan` | **correctness** | The prose-integrity checklist (table row `design`, inherited by row `plan`), plus a new below-table pass |

The same slot and the same shape as gh-7's input-contract completeness pass. `plan` inherits it through the `plan` row's existing "The prose checklist above" reference, and — as with gh-7 — the pass's own heading names both modes so a plan-mode prompt built from either reading of that phrase includes it. The `plan` row is not edited.

Nothing lands in the design rubric, which is the design/plan quality seed's lens **and** every resolver's judgment criteria in all three modes, making it the widest-broadcast text in the file. That ruling is gh-7's, unchanged, and it applies here for the same reason: this is a *noticing* obligation for a seed, not a statement of what "best long-term design" means for a decider.

**Why the correctness seed and not the quality seed — decided, not defaulted.** In `design` and `plan` mode there is no quality-seed slot distinct from the rubric: that cell's entire content is that the rubric *is* the lens. The ruling above therefore rejects the quality seed as well, and the live alternatives are the correctness seed or nothing. The pass fits neither seed's stated remit — that is what *Why the existing seeds miss all three* establishes, and it is why the gap existed — so it lands in the correctness seed on cost, which is exactly the rule gh-7 stated when it put the input-contract pass there: *"anything else lands there on its own cost argument, or not at all."* This is that rule's second exercise, taken deliberately. The cost is named rather than absorbed: the correctness cell's inline checklist no longer describes everything that seed does. What bounds the drift is the cell's own grammar, which separates the checklist from its below-table pointers — a third pass lengthens the pointer list, it does not loosen the checklist — and a pass that cannot make its own cost argument is a signal to restructure the section, not to add another pointer.

## The decision

**Trigger.** Only words the artifact introduces or adopts as the **name of a concept** — one it defines, coins, or borrows from another source. Deciding that is a semantic read, not a typographic one, and this repo's own docs show why: its design docs carry 49–132 bolded spans each (fenced blocks excluded, spans not crossing a line), almost all ordinary emphasis (`**both**`, `**not**`, `**First:**`), and not one of this document's headings names a coined term. What keeps the trigger tight is not markup but that prose names concepts *sparsely and out loud* — a doc that coins a term almost always says so in the sentence that coins it ("we call this X", "borrowed from `codebase-design`"), so the artifact supplies its own evidence and the candidate set stays a handful regardless of word count. Typography is where a reviewer looks first, never the test it applies. Sparseness is the property that does not survive into `diff` mode (see Out of scope).

**Stopping conditions**, both stated in the trigger sentence itself so a reviewer reads them before doing any work:

1. **Never the repo's vocabulary at large.** This is not a glossary audit. An artifact introducing three named concepts checks three words, regardless of how large the repo's vocabulary is.
2. **Never a word the artifact uses in the sense the repo already has.** Without this, every use of `seed`, `resolver`, `tier`, or `mode` in a dev-flow design fires the pass.

Worst case is linear in the count of concepts the artifact names — a handful for any design doc that is not itself a glossary. This document names five (see *Applying the pass to itself*), against 94 bolded spans and 24 headings measured the same way.

**The check, two clauses.**

- **Against the repo.** Glossary first (`CONTEXT.md` at the root, or the per-context files a root `CONTEXT-MAP.md` names), then grep the review's working directory for any term the glossary does not settle — restricted to shipped prose, skipping the artifact itself and prior design/plan records.
- **Against itself.** One word carrying two senses, or two words carrying one — the `angle`/`pass` case, which no glossary can catch because both senses are new.

**Reportability rule.** Report only what you can quote: the artifact's sense, the colliding sense, and where the colliding one lives. "Define your terms" and "the vocabulary could be tighter" are not findings. As in gh-7, the trigger narrows *which artifacts get asked* and the reportability rule narrows *what may be said*. The two filter different things, and both are load-bearing: stopping condition 2 discards a word the artifact uses in the sense the repo already has — which ordinary English always is, so it is what stops an over-extracted `**both**` — while the reportability rule discards anything that cannot quote two distinct senses plus a location, forcing every finding into a checkable claim a resolver can reject in a single read.

**Findings only, and the fix is the resolvers' call.** A collision does not imply a rename. `seam` resolved the other way: the word stayed and `CONTEXT.md` gained an entry stating that this repo uses it at two levels. Because both outcomes are legitimate, the pass says to report the collision *either way* — a seed that finds a collision, privately judges a rename unwarranted, and stays silent is the one failure this pass cannot tolerate, being indistinguishable from the gap it exists to close.

**The fix lands in the artifact.** If a term needs a glossary entry, the artifact says so and the entry ships in the same commit as the behaviour it defines — gh-7's §6 precedent. The seed never writes `CONTEXT.md`; neither does the fixer, except as part of a change the artifact itself specifies. That boundary is what keeps this inside `adversarial-review`'s "owns the artifact end-to-end" contract.

## Why glossary-first-then-grep, and not either alone

**Glossary-only fails on the actual evidence.** `CONTEXT.md` did not exist when `seam` collided. And gh-7's own self-caught collision — its new `Trigger` glossary entry against the `Triggers on …` phrasing in every plugin's frontmatter — is a collision *with shipped prose the glossary does not cover*, which is a permanent property, not a transitional one. A glossary records the senses someone has already noticed. The senses that cause collisions are by definition the ones nobody noticed.

**Grep-only loses precision.** The glossary supplies the canonical sense, and on some entries an explicit `_Avoid_:` synonym line (3 of `CONTEXT.md`'s 17 entries carry one). That is what lets a finding say "the glossary defines X as A, the artifact means B" instead of "this word appears elsewhere." It also settles most terms in one read, so the grep runs on the remainder rather than on everything.

**So: glossary first, grep the remainder.** Exhaustive on sources, narrow on surface. The cost is one file read plus a grep per unsettled term.

**The grep is scoped to shipped prose**, and this is measured rather than assumed. `docs/superpowers/` is **82,688 of 113,891 tracked words — 72.6% of this repo's prose** — and the hit skew for the terms in question is extreme: `trigger` 58 hits inside vs. 4 outside, `angle` 70/7, `pass` 163/25, `seam` 52/9. The decisive case is `fable`: **84 occurrences inside `docs/superpowers/`, 0 under `plugins/`** — it was the resolver tier gh-10 removed, so a design coining `fable` today would collect 84 hits, every one a sense the repo deliberately abandoned. The pass therefore skips prior design and plan records, and skips the artifact itself — without the latter, a genuine self-collision gets reported through the *against-the-repo* clause with a bogus location pointing back at the artifact, satisfying the reportability rule with two quotes of the same document.

Naming `docs/superpowers/` in a general-purpose skill is not the hardcoding wart it looks like. `adversarial-review/SKILL.md` **already names that directory today** (line 85, "otherwise append them to `docs/superpowers/issues/BACKLOG.md`") — and that is a *write* into the tree, so a read-side skip of the same tree is strictly weaker. The skill is also never installed standalone: it exists only inside `dev-flow` and `dev-flow-worktree`, whose own `SKILL.md` declares those exact paths as the pipeline's artifact root. A principle-only formulation ("skip immutable historical records") was tested against this repo and mis-sorts two of three file classes in opposite directions: `docs/superpowers/specs/*.md` is committed and readable, so a seed may reasonably call it shipped, while `docs/adr/` is historical by definition yet is deliberately left greppable. The path is not a shortcut around a principle a `sonnet` seed could apply; it is the only formulation that resolves the ambiguity. The pass states the principle first and the path as its instance.

**Graceful fallback, closed rather than enumerated.** Missing, empty, present-but-not-a-glossary, and named-by-a-`CONTEXT-MAP`-path-that-does-not-exist all produce one outcome — the glossary settles nothing about this term — and all have one correct response: fall through to the grep and say nothing about the glossary. The pass says "missing or settles nothing about the term", which is exhaustive *by construction* (the file is present or not; if present, it settles the term or not) rather than by listing. The scoping to *the term* is load-bearing: "settles nothing" unqualified invites the reading "`CONTEXT.md` settles 17 terms, so it does not settle *nothing*, so this fallback does not apply", which frees a seed to report "term X is missing from the glossary" — the exact non-finding the fallback exists to forbid. And "the glossary's own state is never a finding" is a scope limiter, not a restatement: "proceed silently" alone could be read as suppressing the real collision the grep just found.

**Lineage, including one deliberate override.** "Grep and proceed silently … never flag it, never propose creating one" descends from `docs/agents/domain.md` — byte-identical to `setup-matt-pocock-skills/domain.md` upstream — whose *Before exploring* section says "proceed silently. Don't flag their absence; don't suggest creating them upfront." But that file's *Use the glossary's vocabulary* section rules the **missing-term** case the opposite way: "If the concept you need isn't in the glossary yet, that's a signal — … note it for `/domain-modeling`." The pass deliberately overrides that half. "Note it for `/domain-modeling`" is a write-path recommendation this pass explicitly closes, and it would manufacture precisely the "define your terms" non-finding the reportability rule bans. The asymmetry worth naming: `domain-modeling`'s own fallback for a missing glossary is *create it lazily*, and that path is closed to a findings-only seed.

**Deliberately not guarded**, having been considered: an enormous glossary (no repo in evidence has one, and the threshold would be a made-up number); a `CONTEXT-MAP.md` naming many contexts, where `domain.md`'s "relevant to the topic" scoping is dropped and cross-context term reuse is legitimate rather than a collision (zero multi-context repos in evidence, and adding a relevance judgment to a `sonnet` seed trades one imprecision for another); and a symlinked or binary `CONTEXT.md`. All four degrade into "settles nothing", which routes correctly.

## The `domain-modeling` question, settled

gh-7 rejected wiring in `domain-modeling` on mechanism: its body is user dialogue ("force the user to be precise", "offer to create an ADR"), and it *writes* repo state — neither of which a findings-only review leaf can do. **That rejection stands and is not reopened.** What this design takes is not the skill but the read habit, which the skill itself declares separable in its opening paragraph:

> Merely *reading* `CONTEXT.md` for vocabulary is not this skill — that's a one-line habit any skill can do. This skill is for when you're changing the model, not just consuming it.

`/grill-with-docs`, which found what five reviewers missed, is one line: "Run a `/grilling` session, using the `/domain-modeling` skill." Its glossary behaviour is entirely `domain-modeling`'s, and the part that did the work here is the part its own author says any skill can inline. gh-7 also removed a third, false disqualifier — that `domain-modeling`'s subject is project-wide vocabulary rather than the artifact under review — and this design is what replaces it.

## Working directory — one clause edited, so the dependency holds in shipped text

This is the first **design/plan** seed pass that reads outside the artifact. gh-7's input-contract pass is explicitly bounded to the artifact's own text ("no codebase spelunking for unnamed callers"); this one reads the glossary and greps the repo, so it depends on the correctness seed actually receiving the absolute repo root.

The Working directory section threads that root into "every spawned agent's prompt — seeds, resolvers, and fixers". But the sentence after it — *"Read-only reviewers receive absolute artifact/diff paths and need no entry"* — is a **role contrast**, and a role contrast written as `receive <list>` reads as exhaustive: read-only reviewers get X, write-side fixers get Y. Under that reading a prompt-builder ships a seed prompt with no repo root in it, this pass's "against the repo" clause is silently unusable on day one, and nothing in the file reveals it. Resolving that ambiguity here, in a document that never ships, does not reach the prompt-builder.

Two facts make the sentence worth fixing regardless of this pass:

- **"Absolute artifact/diff paths" describes nothing that exists in `diff` mode.** There is no diff file — the target is "a PR number, branch, or SHA range". So for two of the three read-only instances the phrase names a thing that is not there.
- **Both `diff`-mode seeds already need the root.** The pinned `code-reviewer.md` is not handed a pre-computed diff; it hands the reviewer `git diff --stat [BASE_SHA]..[HEAD_SHA]` to run itself, with no `-C`, plus prose presupposing a checkout ("read-only on this checkout … never move HEAD on this checkout"). `adversarial-review` fills only the four placeholders and uses the template "as designed", so the only lever it has is telling the reviewer which repository to run in. The diff quality seed ("run against `BASE..HEAD`") is the same shape.

So the under-specification has two instances on `main` before this pass adds a third — concrete demand, not speculation — and the fix belongs at the shared boundary. A restatement inside the pass would be the per-instance fix every future repo-reading pass must remember to repeat. Under `dev-flow-worktree` the guarantee is load-bearing rather than pedantic: leaves are pinned to the *main* repo root while the artifact lives in `.claude/worktrees/`, so a read-only seed deriving its location from cwd greps the right repo on the wrong branch — a silent wrong answer that exits 0.

The replacement says "they address it explicitly", reusing the verb the write-side sentence already uses, rather than enumerating "read, grep, and `git -C`". Enumerating the mechanism would be wrong three ways: it duplicates the write-side sentence's `git -C` and blurs the role contrast the paragraph is built on; it asserts a uniformity that does not exist, since the pinned template's git commands are not the review's to edit and carry no `-C`; and "in place" is itself a terminology collision, because `dev-flow`'s SKILL.md uses "work in place" as a named preference meaning *cwd **is** the target*, the near-inverse of *address it from outside*. The path half becomes a rule rather than a list, for the first of the two reasons above: a list has to say what a `diff`-mode reviewer receives, and the answer is no path at all — the pinned template is filled with `BASE`/`HEAD`, and there is no diff file. "Absolute paths for every file the review hands them" is exact in all three modes, and not vacuous in `diff`: the review does hand that prompt one file path, the plan the template's `[PLAN_OR_REQUIREMENTS]` is filled from. Scoping it to what the review *hands* the reviewer, rather than to every path its prompt contains, keeps the root-relative locations inside the pass text itself (`CONTEXT.md`, `docs/superpowers/`) out of the rule — those are resolved against the threaded root, not supplied. It duplicates nothing: the per-mode target definition stays on the Invocation line, and how the template is filled stays in the Pinned template paragraph. "Need no entry" keeps its meaning — no cd, no worktree entry.

## Applying the pass to itself

The check this change adds, run against this document — including the two candidates it would be embarrassing to miss, since they are two of the three instances that motivated it. Two of the five produced a real finding, and both were fixed rather than argued away.

- **`collision`** — used in this repo in exactly this meaning already (gh-7's design, "A collision this change must not repeat"). Same sense; no finding.
- **`domain glossary`** — `docs/agents/domain.md` and gh-7's design both call `CONTEXT.md` "the glossary". Same referent; no finding.
- **`family`** — **fired.** The repo already carries two senses: `CONTEXT.md`'s model product line, and the design rubric's "one of a known family (connectors, handlers, jobs…)". An earlier draft of §Working directory wrote "the seed family", a third sense, in the very file this change edits. Reworded to "the shared boundary". The artifact now only *mentions* `family` when describing the historical collision, and uses it for nothing of its own.
- **`pass`** — **fired.** An earlier draft wrote "a `/grill-with-docs` pass", the ordinary-English sense of a run over a document, while `CONTEXT.md` defines **Pass** as "a named, self-contained check a seed runs over an artifact, carrying its own trigger and stopping conditions." Both senses quotable, both located, so it was reportable under this pass's own rule. Reworded to "run"; `pass` now appears only in the glossary's sense.
- **`sense`** — ordinary English, naming no concept. The trigger does not fire, and no markup rule would have told you that.

**Against itself**, holding each named term fixed across the whole document: `trigger`, `stopping condition`, `reportability rule`, `seed`, and `resolver` each carry one sense throughout, matching `CONTEXT.md`. No second-sense drift found after the two rewordings above.

That two of five candidates produced findings in a document written by the check's own author is the expected shape, not an embarrassment — and it is the strongest available evidence that the pass does something the existing seeds do not.

## Rejected alternatives

**A rubric bullet ("use the repo's established vocabulary").** Rejected. Widest possible context cost — the rubric ships into every resolver in all three modes — to serve two modes' correctness seed, and it mislocates the work: the rubric tells a *decider* what good design means, and this is an enumeration for a *noticer*. Identical to gh-7's reasoning for both its families.

**Invoke or recommend `domain-modeling` / `codebase-design`.** Rejected — see above. The mechanism disqualifiers are unchanged; only the read habit is borrowed, inline.

**Gate the review on a glossary existing.** Rejected. It makes a shipped, general-purpose skill assume one person's documentation convention, turns a missing file into a halt (the pipeline's most expensive outcome), and would have been useless on the motivating instance, where no glossary existed.

**Have the seed write the missing glossary entry.** Rejected on two counts. Seeds are findings-only by construction — the property is in the prompts themselves so no caller has to enforce it — and writing `CONTEXT.md` is outside the artifact, which is the exact boundary that disqualifies `domain-modeling`. When an entry is warranted, the artifact specifies it and it ships with the behaviour.

**A third seed pass, or a separate "vocabulary" seed.** Rejected. It raises design/plan seed cost by 50% for one question and breaks the uniform two-seed shape the whole section and the provenance line are written around. The question fits in the existing correctness seed.

**Sharpen the existing "internal contradictions" bullet instead of adding the against-itself clause.** Rejected — though it is the closest alternative to the shipped design and the one a reader reaches for first. The checklist bullet is the shared boundary for within-document inconsistency, so putting the fix there is the right instinct; it fails on gating. The bullet has no trigger and no reportability rule, and it cannot acquire them without becoming this pass. Widened to name vocabulary, it asks every artifact whether any word carries two senses, over every word rather than over named concepts, with no bar on what may be reported — precisely the shape `CONTEXT.md`'s **Trigger** entry warns manufactures false positives. Kept in the pass, the clause inherits both gates for free and the two halves of one question stay in one place. The evidence that the bullet as it stands is insufficient is in *Why the existing seeds miss all three*.

**State the grep exclusion as a principle only, naming no path.** Rejected — tested against this repo and it mis-sorts `docs/superpowers/specs/` and `docs/adr/` in opposite directions. Full argument under *The grep is scoped to shipped prose*.

**Cover `diff` mode in the same pass.** Rejected — see Out of scope.

## Out of scope

**`diff` mode — filed as #20.** Neither diff seed checks terminology today: the correctness seed is the pinned superpowers `code-reviewer.md`, whose "What to Check" list has no naming or vocabulary item anywhere in it, and the five quality angles are all structural. That is a real hole, and it leaves two gaps this change does not close — standalone `adversarial-review(<PR#>, diff)` on a PR that never had a design stage, and names invented during execution that no design could have contained.

It is deferred rather than bundled because **the trigger does not transfer**. In prose the candidate set is sparse and self-announcing: most words name nothing, and a doc that coins a term usually says so in the sentence that coins it. A code diff inverts both properties — every new function, field, local, and test helper *is* a name, and none of them announces whether it is a domain concept — so the discriminator becomes "names a domain concept, not an incidental identifier", a judgment a `sonnet` seed makes unreliably across dozens of identifiers per diff. The economics punish that: `config`, `client`, `handler`, `result` always grep-hit somewhere, and one false-positive resolver group measured ~86k tokens in gh-7's run, hundreds of times the entire prose addition. Bolting a second, weaker trigger into this paragraph would degrade the one that works.

#20 records the sketch that does work — invert the direction, iterating over the glossary's fixed entry count rather than the diff's unbounded identifier count — and the open question it must answer, that such a check has no fallback in a repo with no glossary.

**`docs/adr/`.** `docs/agents/domain.md` has agents read ADRs as well as the glossary, but ADRs record decisions, not vocabulary. The pass reads the glossary only, and leaves `docs/adr/` greppable.

**`CONTEXT.md`.** No entry is added. gh-7 added none for its input-contract pass either; `Pass`, `Trigger`, and `Reportability rule` already define the shape this pass is an instance of, and `Pass` — unlike `Angle` — does not enumerate its instances. Adding one would be the glossary growing an entry per check.

## Context cost

`adversarial-review/SKILL.md` is 2,237 words today. The addition is 217 words in the pass, plus a net 16 in the Working directory section and a net 2 in the `design` cell — 235 words, about **10.5%** of the file, ~330 tokens. The `dev-flow` pipeline `SKILL.md` gains a net 34 words (§5), in a file the orchestrator loads once per run and no seed prompt carries.

Measured against gh-7's real review invocation of 484,005 tokens, the `adversarial-review` growth is roughly **0.068%** — the orchestrator's whole-file load plus one seed prompt. The number on the other side of the trigger is the one that matters: a single false-positive resolver group measured 86,022 tokens, ~260× this entire addition. Every word spent on the trigger, the grep scoping, and the reportability rule is therefore lopsidedly worth it, which is why all three are stated in full rather than compressed.

**A word count is the wrong ceiling, and gh-7's argument states its own precondition.** Its structure is a ratio, and ratios set no absolute limit — but it only covers prose spent *to reduce false positives or catch real cases*. Words that do neither are not rescued by any ratio. So the test applied here was per-clause marginal value, run over all eight clauses of the pass, and nothing was cut because nothing failed it: the two weakest survive because "For each, check twice" is what makes the sub-clauses a mandatory pair rather than alternatives, and "a sense that lives only in shipped prose is still a collision" is the entire reason the grep exists. For scale, the file already ships a 200-word single-line check — the seam-placement angle — so at 217 the new pass is 8.5% longer than the existing longest, not a new order of magnitude.

Structural dilution is worth separating from the word count. The trigger sentence — the one an artifact naming no new concept reads before stopping — is unchanged by everything the reviews added; the grep scoping and the fallback sit in the check body, read only after the trigger has fired. The two below-table passes have independent first-sentence triggers, so a seed reads both triggers and only the fired one's body; length asymmetry between independently-gated checks is not dilution. The remaining cost is **a standing obligation** — one more pass every future protocol change must keep coherent, which is why the pass names no tier.

## Exact change list

Five files. Every wording below is literal.

### 1 & 2. `plugins/dev-flow/skills/adversarial-review/SKILL.md` and `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md`

A declared `check-sync.py` mirror pair. **Every edit below lands byte-identically in both files.** None of the new or edited text contains a `dev-flow` or `dev-flow-worktree` token, so the two copies compare equal in every touched region before canonicalization does anything.

Three edits: two in-place line replacements and one two-line insertion. Both replacements are above the insertion point and in place, so neither shifts it. Line numbers are the current (pre-change) file, which is 85 lines.

#### Line 20 — Working directory, the read-only-reviewer sentence

Only the third sentence changes; the halt rule, the threading sentence, the fixer sentence, the `EnterWorktree` rules, and the override sentence are byte-identical. Replace the whole line with:

```
**Working directory (resolve once, thread always).** Resolve the working directory exactly once at invocation: the explicit `working-dir` argument if given, else the invoking checkout root (`git rev-parse --show-toplevel`), normalized to an absolute path; resolution failure (not a git repo) is a loud halt at invocation, because the contract requires committing. Thread that absolute path into every spawned agent's prompt — seeds, resolvers, and fixers — so no spawned agent derives its location from inherited cwd (process cwd is global mutable state; parallel fixers make ambient cwd a race). Read-only reviewers receive that root as well as absolute paths for every file the review hands them — they address it explicitly, and need no entry. Write-side fixers address the root explicitly with `git -C <path>` and absolute file paths (harness worktree-entry via `EnterWorktree` is not accepted from these cwd-pinned subagents, and explicit addressing is in any case the only mechanism that works for standalone reviews of checkouts outside `.claude/worktrees/`, which `EnterWorktree` rejects). The `working-dir` argument is an override only — omission cannot produce ambient-cwd behavior.
```

#### Line 29 — Seed passes table, the `design` row

The correctness cell points at the one below-table pass it has; a second is added, so the cell must name both or the new one is unreachable by a prompt-builder that resolves the cell. Replace the whole line with:

```
| **design** | The design rubric (below) *is* the lens, applied adversarially to the proposed approach. | A prose-integrity checklist: placeholders/TBDs, internal contradictions, planning-blocking ambiguity, unstated assumptions, missing or untestable success criteria — plus the input-contract completeness and terminology-collision passes (below). |
```

Only the correctness cell changes; the quality cell is verbatim as today. **Line 30 (the `plan` row) is not edited** — its "The prose checklist above" reference carries the addition, and the new pass names both modes in its own heading.

#### Insert after line 44 (the input-contract completeness pass) — the terminology-collision pass

Insert exactly two lines: one empty line, then this line. Placing it after the input-contract pass keeps the two design/plan notes contiguous and last in the section, matching the layout gh-7 established.

```

**Terminology collision — the design *and* plan correctness seed:** applies only to words the artifact introduces or adopts as the name of a concept — one it defines, coins, or borrows from another source — never to the repo's vocabulary at large, and never to a word the artifact uses in the sense the repo already has. For each, check twice. **Against the repo:** read the domain glossary first (`CONTEXT.md` at the repo root, or the per-context files a root `CONTEXT-MAP.md` names), then grep the review's working directory for any term the glossary does not settle — a sense that lives only in shipped prose is still a collision. Grep shipped prose only: skip the artifact itself, and skip prior design/plan records (`docs/superpowers/`) — history, not shipped text. **Against itself:** one word carrying two senses, or two words carrying one. Report only what you can quote: the artifact's sense, the colliding sense, and where the colliding one lives; "define your terms" is not a finding. Findings only — a collision does not imply a rename, so report it either way; the fix is the resolvers' call. If the glossary is missing or settles nothing about the term, grep and proceed silently — the glossary's own state is never a finding: never flag it, never propose creating one.
```

#### Resulting file shape

Both copies go from **85 to 87 lines**.

| Line | Content |
|---|---|
| 20 | Working directory (edited, in place) |
| 29 | `design` row (edited, in place) |
| 30 | `plan` row (unchanged) |
| 44 | input-contract completeness pass (unchanged) |
| 45 | empty (new) |
| 46 | terminology-collision pass (new) |
| 48 | `## The design rubric` (unchanged, was 46) |

Everything from the old line 45 onward shifts by +2. The declared exception's line (12) is above every edit and does not move.

**Explicitly unchanged in these files:** the `diff` and `plan` table rows, the four `/simplify` angle bullets and the seam-placement angle, line 32, the angles-block header, the input-contract completeness pass, the design rubric (all nine bullets), the Resolution procedure, the Model section, the provenance line, Review integrity, the Contract, and the frontmatter `description`. Within the Working directory paragraph, only the read-only-reviewer sentence changes.

### 3 & 4. Version bumps

- `plugins/dev-flow/.claude-plugin/plugin.json` — `"version": "2.4.0"` → `"version": "2.5.0"`.
- `plugins/dev-flow-worktree/.claude-plugin/plugin.json` — `"version": "1.6.0"` → `"version": "1.7.0"`.

Mandatory, not cosmetic: the install cache is version-keyed, so an edit at an unchanged version is never picked up on re-sync. Minor rather than major — the skill's invocation signature, contract, provenance format, and mode set are unchanged; only seed content and one clause each of the working-directory rule and the branch lifecycle change.

### 5. `plugins/dev-flow/skills/dev-flow/SKILL.md` — a false clause about the guarantee this change establishes

Line 139 currently ends: *"…so no `working-dir` argument, no `Work from:` field, and no absolute-path threading is needed anywhere in this pipeline."* The first two clauses are correct and scoped to the pipeline's own arguments. The third is **false as a universal**: dev-flow invokes `adversarial-review` in-context, that skill's leaves are spawned inside this pipeline, and its contract threads the absolute root into every one of them unconditionally. A pipeline does not get to waive a delegated skill's internal rule — and this file already states the correct pattern for exactly this, at its Model Policy paragraph, where reviewer-model selection "is owned by `dev-flow:adversarial-review` and stated once, in its Model section; that rule travels with the review skill wherever it is invoked, and is deliberately not restated here."

Shipping the line-20 clarification while leaving this sentence in the review's primary caller would put two files of one plugin in contradiction on precisely the guarantee this change buys. Replace the whole of line 139 with:

```
**Branch lifecycle — owned by dev-flow, plain git.** The contract stakes everything on one invariant: *a branch named exactly `<username>/<slug>`, based off the default branch, exists and is checked out in your working directory whenever a stage runs.* No delegated mechanism guarantees that (native worktree tools auto-name branches and take their base from a user setting), so dev-flow creates and checks out the branch itself with plain git. Because the branch is checked out in the repo root itself, every command — the orchestrator's own and every spawned leaf's (leaves are pinned to the repo root and cannot inherit cwd) — runs against it by default; the cwd-inheritance problem a separate worktree would create simply does not arise, so no `working-dir` argument and no `Work from:` field is needed anywhere in this pipeline. What a delegated skill threads into the leaves *it* spawns is that skill's own rule and is not waived here — `dev-flow:adversarial-review` threads the absolute repo root into every agent it spawns unconditionally (its Working directory section).
```

The file stays at **277 lines** — an in-place, one-line replacement.

**This edit is one-sided, and that is correct.** The pipeline `SKILL.md` pair is hand-mirrored, not machine-checked, and the two copies have genuinely diverged here: `dev-flow-worktree`'s counterpart is a *Worktree lifecycle* paragraph that already states the opposite, correctly — leaves "are pinned to the repo root and cannot inherit cwd, so each is handed the absolute worktree path explicitly: `adversarial-review` via its `working-dir` argument". There is no sibling claim to fix, so `dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` is not edited. Per `CLAUDE.md`, a hand-mirrored edit carries a residue grep — Verification step 3.

## Sync constraint — how `check-sync.py` still passes

**Check B (mirror pair `adversarial-review`)** requires the two files to be line-for-line identical after substituting `dev-flow-worktree` → `dev-flow`, except the declared exception at line 12.

1. **All three edits land in both files.** A one-sided edit produces an undeclared-divergence failure naming the line.
2. **The insertion is symmetric, so line counts stay equal.** Both files go 85 → 87. An asymmetric insertion is a `LINE_COUNT_FIX` failure and could not be declared as an exception even deliberately.
3. **No new variant token is introduced.** The added and edited text contains no `dev-flow` / `dev-flow-worktree` occurrence.
4. **The declared exception still fires and does not go stale.** It covers line 12, above every edit, which does not shift.

**Check A (manifest descriptions)** compares `name`, `source`, and `description` between each `plugin.json` and its marketplace entry, and does not read `version`. This change edits only `version`, so `.claude-plugin/marketplace.json` is not touched.

**The hand-mirrored pipeline `SKILL.md` pair is edited on one side only** (§5), which `check-sync.py` does not police — that pair is too divergent to check mechanically, which is exactly why the divergence being corrected could exist. The residue grep in Verification step 3 is the substitute, and the sibling needs no matching edit because it already says the opposite thing correctly.

## Blast radius

A repo-wide search of tracked files outside `docs/superpowers/` for `input-contract`, `correctness seed`, and `prose-integrity` returns hits **only** in the two `adversarial-review/SKILL.md` copies. Specifically confirmed:

- **`plugins/dev-flow/skills/dev-flow/SKILL.md`** — edited (§5). It does not enumerate or describe a seed pass, but it *does* make a claim about absolute-path threading, which is the clause being corrected.
- **`plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`** — not edited. It restates the threading rule explicitly and correctly (leaves "handed the absolute worktree path explicitly: `adversarial-review` via its `working-dir` argument"), so it needs no change. This is the one place the earlier draft of this design was factually wrong: it claimed neither pipeline file restates the working-directory rule.
- **Both `README.md` files** — no seed/pass/checklist content.
- **`.claude-plugin/marketplace.json`** — no `description` changes; Check A does not read `version`.
- **`CONTEXT.md`** — no entry added (see Out of scope).
- **`CLAUDE.md`** — the mirrored-pair verification rule gh-7 landed already covers this change as written; no new rule and no rescoping is needed, so it is not edited.
- **`scripts/check-sync.py`**, `.github/workflows/`, `docs/agents/*.md` — untouched.

## Verification

1. `python3 scripts/check-sync.py` — passes. Expect `mirror pair "adversarial-review" ... OK (87 lines, 1 declared exception)`.
2. `claude plugin validate .` — passes; the 8 missing-author warnings are expected.
3. **Residue grep (always, per `CLAUDE.md`).** All four return **no hits**:

   ```sh
   git grep -n -e 'input-contract completeness pass (below)' \
              -e 'artifact/diff paths' \
              -e 'no absolute-path threading' \
              -e 'never flag its absence or propose creating one' -- plugins/
   ```

   The first three are text this change deletes — the two in-place replacements in the mirror pair, and §5's one-sided edit to the hand-mirrored pipeline file, which is the one with no mechanical check behind it. A hit on the first two means one side of the mirror pair was missed. The fourth never existed in any shipped file: it is the pre-review draft of the pass's final sentence, and a hit means a stale block was applied instead of the one in §Exact change list.
4. **Design conformance — all four blocks landed verbatim, in the right place.** This is the one step steps 1–3 structurally cannot provide. Step 3's residue grep is tied to the in-place replacements and says nothing about the insertion, and `check-sync.py` compares the two mirror copies only to *each other*, so a word mangled identically in both passes it at the correct 87 lines — and it never reads the pipeline file at all. This check reads the expected text from this design file on disk — never retyped — and requires a byte-for-byte line match in each target, plus, for the insertion, that it sits directly after its anchor line. The anchor matters on its own: the pass inserted after the `Pinned template` paragraph instead would leave a diff-mode note trailing the two design/plan notes and pass every other check here. It also asserts each file's length, using `check-sync.py`'s own `wc -l` convention so "87" means the same thing in both steps. Copy the script exactly; it is deliberately pure ASCII, so a mistyped copy fails loudly instead of passing. **The fence is unindented on purpose** — a `python3` heredoc indented under the list item is an `IndentationError`.

```sh
python3 - <<'PY'
import sys
from pathlib import Path
DESIGN = "docs/superpowers/specs/2026-07-28-gh-16-terminology-collision-design.md"
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
assert [len(b) for b in blocks] == [1, 1, 2, 1], "design code-block shape changed; stop and re-read the design"
PAIR = ["plugins/dev-flow/skills/adversarial-review/SKILL.md",
        "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md"]
PIPE = ["plugins/dev-flow/skills/dev-flow/SKILL.md"]
WANT = {PAIR[0]: 87, PAIR[1]: 87, PIPE[0]: 277}
SPEC = [("line 20, working directory",          blocks[0], None, PAIR),
        ("line 29, design row",                 blocks[1], None, PAIR),
        ("terminology-collision pass",          blocks[2], "**Input-contract completeness", PAIR),
        ("pipeline line 139, branch lifecycle", blocks[3], None, PIPE)]
bad, text = [], {}
for path, want in WANT.items():
    L = Path(path).read_text(encoding="utf-8").split("\n")
    if L and L[-1] == "":
        L.pop()
    text[path] = L
    if len(L) != want:
        bad.append(("file length", path, "%d lines, want %d" % (len(L), want)))
for name, want, anchor, paths in SPEC:
    for path in paths:
        L = text[path]
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

   Expect exactly `design-conformance: OK` and `exit=0`. A `MISMATCH` line names the block and the file whose text or position differs — re-paste that block from §Exact change list and re-run from step 1. The shape assertion (`[1, 1, 2, 1]`) fires if this document's plain-fenced blocks are ever added to, removed, or reflowed: that is deliberate, because the blocks are indexed positionally. The script's own fence carries the `sh` info string and is therefore skipped by the `mode == ""` filter, so adding or editing a verification step never disturbs that index — keep it that way.

5. Both `plugin.json` versions read `2.5.0` and `1.7.0`.
6. **Behavioural check, on this design doc itself.** The pass is meant to fire on documents like this one, and during this design's own review it did — twice, on `family` and `pass` (see *Applying the pass to itself*). The bar for a future run is the same: a reported collision must quote both senses and a location, and a run that reports "consider defining your terms" is evidence the reportability rule is too weak to have shipped.

## Assumptions recorded

- **`CONTEXT.md` is the glossary filename in repos that have one.** Taken from `docs/agents/domain.md`, which is byte-identical to the upstream file `setup-matt-pocock-skills` installs. Repos that use a different filename get grep-only behaviour, which is the fallback path and is correct rather than broken.
- **A `sonnet` seed can pick a design doc's named concepts out of its prose.** This is the trigger's load-bearing assumption, and because it is a semantic judgment it can fail in either direction — not only the convenient one. Under-extraction is the status quo: collisions missed, nothing spent. Over-extraction — an emphatic `**both**` read as a coined term — costs seed-side reads and greps, and two independent filters stand between it and a resolver group: the second stopping condition discards every word the artifact uses in the sense the repo already has, which is what ordinary English always is; the reportability rule then discards anything that cannot quote two distinct senses and the place the other one lives. So the failure this assumption can produce is seed cost, not the 86k-token one, and the design does not depend on extraction erring conservatively.
- **Line numbers 20, 29 and 44 in the mirror pair, and 139 in the pipeline file, are current as of `4e32e0e`.** The plan re-derives them by content match rather than trusting the numbers.
