---
dev-flow:
  slug: gh-31-34-glossary-contents
  stops: [pre-merge]
  docs: commit
---

# gh-31 / gh-34: what `CONTEXT.md` should contain

Two issues about the contents of one file, both filed for judgment rather than as defects. **#34 SHIPS, narrowed**: a new `### Topology` section defines **Orchestrator**, **Leaf**, **Fan-out**, and **Flat topology** — four headwords, and **none** of the three `_Avoid_:` names the issue proposes, each of which fails a test the issue did not apply. **#31 SHIPS as filed**: `group-resolution agent` joins the **Resolver** `_Avoid_:` line. Totals: **4 new entries** (17 → 21), **1 new avoided name** (6 → 7), one file changed.

The two rulings look opposed — #31 adds the only kind of thing #34 is refused — and that is the point. They fall out of one test applied twice, stated in *The framework* below: a headword and an `_Avoid_:` name are read by different consumers, at different frequencies, on different limbs, and must therefore be priced separately. #34 proposes headwords for a real gap and avoided names that fail the `_Avoid_:` gate — two of them despite a measured vector, which is not what that gate asks; #31 proposes an avoided name that passes the gate on concept identity and costs one grep on a line that already runs.

## What was verified before designing

Run in this worktree against `b4b5d1c` (`origin/main`, and this branch's tip at design time). Every number below is measured, not carried over from the issues. Every `git grep` figure is measured over tracked files at that commit and so excludes this document, which is untracked while it is written and which itself uses several of the terms it counts — re-running any of these greps after this document lands returns more.

**The glossary as it stands.** 67 lines, **17** entries (`grep -c '^\*\*'`), **3** carrying `_Avoid_:` (lines 11, 15, 67) for **6** avoided names, under **4** `###` sections (*The review protocol* `:7`, *The pipeline* `:44`, *Duplication* `:55`, *Cross-cutting* `:63`). Every definition is a single line.

**The topology cluster is absent, and #34's table is correct.** In `CONTEXT.md`: `orchestrator` 0, `leaf`/`leaves` 0, `spawner` 0, `topology` 0, `fan-out` **1** — inside the **Provenance** definition, used and never defined. In shipped text (`plugins/`, both mirror copies):

| Term | Lines | Senses |
|---|---|---|
| `orchestrator` | **47** across 4 files | one |
| `leaf` (whole word) | **7** lines / 9 occurrences | one |
| `leaves` (whole word) | **13** lines / 14 occurrences | **two** — 8 the concept's plural, **5 the ordinary English verb** |
| `fan-out` | **8** lines — "fan-out work", "fan-out skill", "fan-out controllers" | one |
| `flat topology` | **2** lines (one per pipeline copy) | one |
| `topology` (bare) | the same **2** lines | one |
| `spawner` | the same **2** lines, only "the orchestrator is the only spawner" | one |
| `controller` | **5** lines per pipeline copy — "SDD's controller", "the fan-out controllers' state" | one |

**`group-resolution agent` is dead in shipped text.** `git grep -in 'group.resolution.agent' -- plugins/` → no output, exit 1. PR #37 removed the last instances. Repo-wide the phrase survives on **22** lines across **9** artifacts, all under `docs/superpowers/`. `docs/adr/0002-…:3` carries the *different* string `group-resolution tier`, which no grep for the agent form reaches.

**Three of the six existing avoided names are already dead phrases.** `finder`, `first-pass reviewer`, and `arbiter` each return exactly **1** hit across `plugins/ CONTEXT.md .claude-plugin/` — the `_Avoid_:` line that names them. This is what makes #31 *eligible*, not what makes it cheap; the two are priced separately in *Issue #31*.

**`scripts/check-sync.py` does not read `CONTEXT.md`.** `grep -n 'CONTEXT' scripts/check-sync.py` → no output, exit 1. It passes today (`OK (89 lines, 1 declared exception)`, exit 0) and will pass identically after this change, having proved nothing about it. The design-conformance check in *Success criteria* is therefore the **only** mechanical guard on the new text.

**`headword` is a new word in this repo.** `git grep -in headword` → no output, exit 1. This document coins it for the bolded term line of an entry, as distinct from the entry's `_Avoid_:` line; it is a fact about the glossary's *format*, not a domain concept, and it is not proposed as an entry.

## Decomposition check

One change. Both issues edit `CONTEXT.md` and nothing else; #34 explicitly flags the collision ("same file, so sequence them"), and holding them together dissolves the sequencing rather than managing it. More substantively, they cannot be priced apart: the framework below is one framework, and #31's ruling turns on a precedent that #34's ruling also has to respect. Splitting would mean deriving the same cost model twice and risking two incompatible answers to "when does a name earn an `_Avoid_:` slot". **No split.**

## The framework: what an entry buys and what it costs

`CONTEXT.md` has exactly two shipped consumers, both in `plugins/*/skills/adversarial-review/SKILL.md`. Everything below follows from what they literally do, not from taste about glossary hygiene.

**Consumer A — the *Glossary conformance* angle (`:42`).** Diff mode, quality seed, one mode only. It *"Iterate[s] the glossary's entries, never the diff's names: for each term, and for each synonym its entry marks as one to avoid, grep the diff's added lines of shipped text for that term"*, skipping `docs/superpowers/`. A hit is a candidate only where the diff uses the term **as a name**, and then a finding only on one of two limbs:

- **generous** — *"names something the entry does not define"*. This is the false-positive-prone limb; it is the limb that produced #28.
- **strict** — *"reintroduces an avoided synonym for the very concept the entry does"*. Reachable **only** by names on an `_Avoid_:` line.

**Consumer B — the *Terminology collision and drift* pass (`:48`).** Design **and** plan modes, correctness seed — so **twice per dev-flow run, forever**. It *"read[s] the domain glossary first … both halves key off it"*.

- **Collision** applies to words the artifact adopts as the name of a concept, *"never to a word the artifact uses in the sense the repo already has"*, and greps the repo for *"any term the glossary does not settle — a sense that lives only in shipped prose is still a collision"*.
- **Drift** *"applies **only** to the names the glossary's entries mark as ones to avoid"*, searched over the artifact, spaced or hyphenated, counted only where the artifact **uses** rather than **mentions** the name and only where it names *"the very concept its entry defines"*.

From those two texts, four consequences that decide everything downstream:

1. **A headword is a *suppressor* for Consumer B's collision half.** Settling a term removes it from "grep the repo for any term the glossary does not settle" and makes the exemption checkable against a definition instead of against shipped prose a seed must first find. The saving is not hypothetical: #30's design review spent a `sonnet` seed reporting `topology` as a collision and an `opus` resolver group disproving it, and `gh-30`'s own spec self-review (`:202`) had to reason the exemption out from first principles in prose. **A headword can therefore have negative net cost.**

2. **A headword is a *workload* for Consumer A, and its only exposure is the generous limb.** Each headword adds one grep over each diff's added shipped lines, and can produce a finding only where the diff uses the word as a name in a sense the entry does not define. So a headword's cost is measured by **how many senses the word carries in this repo's shipped text**, not by how often it appears. A word with one sense costs a grep and no findings; a word with two costs a judgment per hit.

3. **An `_Avoid_:` name is read by both consumers, and by Consumer B on every design and every plan, forever.** It is the only route to Consumer A's strict limb *and* the only route to Consumer B's drift half — two catches at two stages: the strict limb fires on a reintroduction into shipped text, the drift half fires on the artifact that proposes one, which is earlier. It is also the only construct in the file whose cost recurs per run rather than per diff. Its cost is therefore measured by **how often the name appears in text the drift half will search**, and by whether the mention-versus-use clause carries those appearances — a metric over *artifacts*, note, not over shipped text: whether the name is live in `plugins/` is not an input to it in either direction.

4. **Consumer B's drift half never reads headwords, and Consumer A's strict limb never reads anything else.** The two decisions are mechanically independent. "Add an entry" and "add an avoided name" are separate rulings and must be argued separately — which is the discipline #34 skips when it bundles three avoided names into a section proposal.

Two further rules, both read off shipped text rather than invented here:

- **The `_Avoid_:` test.** Every existing `_Avoid_:` line lists *alternative names for the concept its own entry defines* — `finder`/`first-pass reviewer` for **Seed**, `group agent`/`judge`/`arbiter` for **Resolver**, `boundary` for **Seam**. `docs/agents/domain.md` states the same scoping normatively (*"When your output **names a domain concept** …, use the term as defined in `CONTEXT.md`"*), and the gh-20 design settled it at length. A candidate that is not an alternative name for its host entry's concept is not an `_Avoid_:` name, whatever else it is. **The test is a gate, not a factor**, and both consumers make it so mechanically: Consumer A's strict limb fires only on *"an avoided synonym for the very concept the entry does"* define, and Consumer B's drift half counts a hit *"only where it names the very concept its entry defines"*. A name that is not such a synonym can never fire either limb, so it buys nothing on the only limbs an `_Avoid_:` name exists to reach, however live its use. A measured reintroduction vector is therefore a reason to **pay** for a name that passes the gate, never a reason to admit one that fails it. That is the single rule this document runs four times — it is why the same fact, a phrase surviving in `docs/superpowers/`, counts for `group-resolution agent` and for none of `nested`, `depth-2`, or `stage subagent`.
- **`_Avoid_:` is prescriptive, not a census.** gh-20: *"The glossary was written as the vocabulary the repo should use, not as a report on the vocabulary it had."* Measured above: 3 of the 6 existing avoided names occur nowhere in shipped text but their own entry.

**What section headings buy: nothing mechanical.** Neither consumer reads them — the angle iterates *entries*, the pass reads *the glossary*. A `###` heading is for human and exploration-time readers only (`docs/agents/domain.md`). It is therefore free to choose on readability grounds alone, and it is not evidence for or against any entry.

## Issue #34 — the spawn-topology cluster

### The gap is real

**Two defects, argued separately; they share a file, not evidence.**

*The first.* The axis ADR-0003 exists to decide, and the axis #30 spent a full review cycle on, has zero vocabulary in the glossary. By framework consequence 1 that is not a cosmetic hole — it is the reason Consumer B had nothing to check `topology` against, and the reason gh-30's design had to argue the exemption in prose rather than point at a definition. **Orchestrator**, **Leaf**, and **Flat topology** repair that, and the #30 incident is their whole evidence.

*The second, independent of #30 and standing even if #30 had never happened.* `fan-out` is already *in* `CONTEXT.md`, inside the **Provenance** definition, doing definitional work while itself undefined. That is precisely the shape the collision half is written to catch — *"a sense that lives only in shipped prose is still a collision"* — and it is repaired by one entry, **Fan-out**, at a measured cost of one grep and nil generous-limb exposure (8 shipped lines, one sense). Neither defect's evidence is transferable to the other, and this document does not transfer it.

#34's structural argument is also right and is adopted: a lone **Topology** entry would be a per-instance patch on a cluster-shaped hole. Be precise about which terms that argument covers. **Orchestrator**, **Leaf**, and **Flat topology** are mutually defining in the strict sense — a leaf is what the orchestrator spawns, and flat topology is the property that those two exhaust the shape; delete any one and the other two lose a term they are stated in. **Fan-out** is not in that cycle and is not claimed to be: its definition reaches for all three (the orchestrator as its controller, leaves as its workers, *adds no level* as the flat-topology property) and nothing in the new section reaches back. It belongs in the same section on two facts of its own. First, an entry already in the file depends on it — **Provenance** reads *"Evidence of fan-out and tier conformance"*, so the reference from outside the section already exists and is the defect being repaired. Second, fan-out is the one construct in either pipeline that *could* have added a level and does not, which is what ADR-0003's operative sentence is about: *"The orchestrator invokes every fan-out skill … in-context and spawns those skills' workers itself; no spawned subagent spawns anything."* A reader who does not know what a fan-out is cannot see why flat topology was a decision rather than a tautology. What ADR-0003 decides nothing about is fan-out *breadth* — how many workers a controller dispatches — and no entry here says otherwise.

### Which terms earn a headword

Priced per framework consequence 2 — one grep each, exposure proportional to the number of senses the word carries in shipped text.

| Candidate | Shipped lines | Senses | Generous-limb exposure | Ruling |
|---|---|---|---|---|
| `orchestrator` | 47 | 1 | **nil** — every shipped use is the defined sense | **entry** |
| `leaf` | 7 | 1 | **nil** | **entry** |
| `leaves` (its plural) | 13 | 2 | **nil** — a grep for the headword `leaf` never reaches it; the 5 verb lines would be exposure only if the plural were headworded | **no entry**, and nothing said about it inside **Leaf** — below |
| `fan-out` | 8 | 1 | **nil** | **entry** |
| `flat topology` / `topology` | 2 | 1 | **nil** | **entry** |
| `spawner` | 2 | 1 | — | **no entry** — defined inside **Orchestrator** |
| `controller` | 5 per copy | 1 | — | **no entry** — defined inside **Fan-out** |

**Orchestrator, Fan-out, Flat topology** are the easy three: each carries exactly one sense across every shipped line, so each costs one grep and can produce no finding on either limb, while buying the collision-half suppression that motivated the issue. The **Flat topology** entry is written to **define** the bare word `topology` explicitly, because the bare word is what #30's false positive fired on; the headword is the compound because that is the phrase shipped text actually uses, and grepping `flat topology` is strictly narrower than grepping `topology`.

**The Fan-out definition does not say "in parallel", and that is deliberate.** Shipped text names two fan-outs — *"the fan-out skills — `adversarial-review` and `subagent-driven-development`"* — and holds their controller state as *"the review's group loop, SDD's task loop"*. Only one is concurrent: `adversarial-review`'s seeds are explicitly *"run in parallel"*, while SDD advances one task at a time, per-task review and per-task checkbox commit. A definition requiring parallelism would be contradicted by the second of its own two examples, and by every shipped line that calls SDD a fan-out skill, on the day it landed — the same objection this document makes to `_Avoid_: stage subagent`. It would also drift from **Provenance**, the entry the definition exists to repair, whose sense is *"really fanned out to separate reviewer subagents … never a single inline pass"* — one-to-many, not concurrency. The definition says *dispatching N workers and holding their loop* and stays silent on whether they run at once; silence asserts nothing, where "in parallel" would have asserted something false.

**Leaf needs no special argument, and the plural is why it looked as though it did.** `leaves` carries two senses in this repo — the concept's plural (8 lines: *"the review's seed/resolver leaves"*, *"Spawned leaves are pinned to the repo root"*) and the ordinary English verb (5 lines: *"a `pre-merge` stop leaves them in place"*, *"leaves `origin/<baseRef>` unresolvable"*, *"the pipeline leaves the branch itself alone"*). But a grep for the headword `leaf` reaches **none** of the 13 — `leaf` is not a substring of `leaves`, and Consumer A inflects nothing, matching only case variants and identifier joinings. So the second sense sits on neither consumer's path: Consumer A never greps the string at all, and Consumer B's collision half triggers only on *"words the artifact introduces or adopts as the name of a concept"*, which an ordinary verb is not — the trigger excludes it before the ordinary-English clause is reached. The two-sense measurement is therefore an argument against ever headwording the plural (13 lines, 5 of them judgment calls per diff, for coverage the singular does not have under that string anyway), not an argument for saying anything about it inside the entry. **Leaf** ships as a bare definition: one sense, 7 shipped lines, nil exposure — the same profile as the easy three.

**And the entry says nothing about the verb.** An earlier draft added a sentence to **Leaf** noting that its plural is also an ordinary English verb. Dropped, on three grounds. *The mechanism does not exist* — per the paragraph above, no shipped consumer ever asks the question that sentence answers. *The house-style precedent cited for it does not cover it* — **Tier**'s *"Distinct from *family*"*, **Family**'s *"A set of merely related constructs … is not a family"*, and **Pass**'s contrast with an angle each separate one *glossary* concept from another *glossary* concept, which is a fact about this repo's vocabulary that a reader choosing between two live terms needs; a homograph rider is a fact about English, aimed at a checking pass's parsing. *And the precedent runs the other way, measured* — `plugins/dev-flow/skills/adversarial-review/SKILL.md:3` uses *Seeds* and *passes* as this glossary's terms and *Triggers on* in a sense **Trigger** does not define, and `:14` uses *pass* as the ordinary English verb (*"A caller may pass additional findings"*) four lines before `:18` uses *passes* as the term. That is the same homograph situation as `leaves`, in the very file both consumers live in, across at least **Seed**, **Pass**, and **Trigger** — and not one of those entries carries a rider. Adding the first would make **Leaf** the anomaly and set the precedent that every ordinary-English headword needs one: the glossary growing to serve itself, which this document rejects below (*What is not being claimed*).

**`spawner` gets no entry.** Its entire content is "the orchestrator". A headword whose definition names another headword and adds nothing is a synonym, and synonyms belong on `_Avoid_:` lines — which this one must not join, because shipped text uses it correctly (*"the orchestrator is the only spawner"*, both pipeline copies) and an `_Avoid_:` slot would make the repo's own prose drift. The **Orchestrator** entry **defines** it instead — *"the run's only *spawner* — the one agent that spawns any other"* — on the same rule applied to `controller` below: a word carried inside an entry must be glossed there, not merely used, or the entry reproduces the `fan-out`-in-**Provenance** defect this change exists to repair. An earlier draft left `spawner` as a bare appositive (*"its only spawner"*) while marking `controller` and bare `topology`; that inconsistency was the defect, and marking all three is the repair.

**`controller` gets no entry either**, and this is the closer call. It is a genuine term — 5 lines per pipeline copy, and it is the word #34's own proposed **Fan-out** definition reaches for. But it names no concept the cluster does not already contain: a controller is the orchestrator *viewed from one fan-out*, which is why shipped text writes "the orchestrator (SDD's controller)" and "the fan-out controllers' state" in the plural. A role-relative label is not a second concept. It is also a common enough technical word that a headword's grep would be the highest-yield of the five and the yield would be noise. So it is **defined inside the Fan-out entry** rather than headworded — deliberately *defined* there, not merely used, because "used inside a definition without being defined" is exactly the `fan-out`-in-**Provenance** defect this change exists to repair, and repeating it one entry over would be incoherent. And it must not go on an `_Avoid_:` line for the same reason as `spawner`.

**What "defined inside another entry" buys, stated at the strength the shipped text supports.** Consumer A is unaffected either way: it iterates *entries* — headwords and `_Avoid_:` names — so a word inside a definition's body is never grepped, and carrying `spawner`, `controller`, and bare `topology` this way costs zero greps per diff. That much is mechanical. Consumer B is a judgment, not a mechanism: `:48` says *"grep the review's working directory for any term the glossary does not settle"* and nowhere states that a word appearing inside another entry's body counts as settled. The honest claim is the one this document already makes for headwords: a seed still has to notice, and what a definition buys is that the answer is a line of a file the pass has already opened rather than shipped prose the seed must first locate. That is also why the three words are *defined*, in the entry's own sentence, rather than merely present — a definition is the strongest signal available to a reader deciding whether the glossary settles a word.

### The three `_Avoid_:` names #34 proposes: all three rejected

#34 offers *"Candidate `_Avoid_`: nested, depth-2, stage subagent"* under **Flat topology**. Applying the `_Avoid_:` test — *is this an alternative name for the concept the entry defines?* — all three fail the gate, two of them with measured collateral damage besides.

**`nested` — rejected.** It is not another name for flat topology; it is the name of the **negation**. Adding it would put the antonym of a concept on the concept's own avoid line, which no existing entry does and which `docs/agents/domain.md`'s concept scoping cannot express. The damage is measured: `nest`/`nested` appears on **5 lines of shipped text**, every one of them a correct use of the antonym (`dev-flow/skills/dev-flow/SKILL.md:8`, `:266`; the `dev-flow-worktree` copy at `:8`, `:155`, `:261`), plus ADR-0003 throughout. Drift's concept test would spare them — `nested` never names *flat topology* — but Consumer A's **generous** limb would not: `nested` on an avoid list, in an added shipped line, naming a concept the **Flat topology** entry does not define, is a candidate by the letter of the rule. That is the #28 limb firing on correct prose, at every future edit to those five lines.

**`depth-2` — rejected on the gate.** Like `nested` it is not another name for flat topology but the name of a violation of it — the two-level spawn chain the property forbids — so it fails the `_Avoid_:` test as an antonym, one step more specific than `nested`. Its vector is conceded, not denied: `git grep -in 'depth-2'` returns **11 lines / 14 occurrences**, all under `docs/superpowers/` — 9 in `docs/superpowers/plans/2026-07-22-dev-flow-nested-review-fix.md`, plus `docs/superpowers/specs/2026-07-22-dev-flow-nested-review-fix-design.md` and `docs/superpowers/specs/2026-07-22-dev-flow-flatten-design.md`. That is the same kind of material *Issue #31* counts as a live source, and by the gate it changes nothing: an antonym can fire neither the strict limb nor the drift half, so the name would buy nothing while Consumer B grepped it over every design and plan forever — including the artifacts this repo keeps producing about the flatten history, which are precisely where the word lives. Where it differs from `nested` is that all 11 lines are records, which Consumer A skips, so there is no shipped-text collateral to measure: the cost is Consumer B's alone, and the benefit is nil either way.

**`stage subagent` — rejected, and this is the one worth stating carefully because #34's strongest sentence is about it.** The issue argues it is *"not hypothetical: that vocabulary is live in `docs/superpowers/` and was live in shipped text until 1.2.0"*. The vector is real. The name still fails, twice over.

*First, on the `_Avoid_:` test.* A stage subagent was the thing between the orchestrator and the reviewers under 1.1.0's nested shape. It is not another name for **Flat topology** (a property), nor for **Leaf** (a stage subagent spawned, so it was by definition not a leaf), nor for **Orchestrator**. It is the name of a **construct that no longer exists**. `_Avoid_:` lines reject rival names for live concepts; they have no slot for the name of a deleted one, and hanging it under **Flat topology** would be filing it against the property that killed it rather than against anything it named.

*Second, and decisively, it is live in shipped text right now.* Both pipeline copies read *"No execute-stage-subagent wrapper."* (`dev-flow/skills/dev-flow/SKILL.md:225`, `dev-flow-worktree/…:219`). The drift half greps each avoided name *"spaced or hyphenated as prose compounds it"*, so `stage-subagent` matches, and the sentence **names** the construct — in order to deny it, which is still a naming use, not ordinary English. So `_Avoid_: stage subagent` would ship a rule that the repo's own shipped prose violates on the day it lands. The sentence is correct as written and is not proposed for repair here (`plugins/` is out of scope, and there is nothing wrong with it). That the rule and the correct sentence cannot coexist is the argument against the rule.

Beyond shipped text, the recurring cost is the larger of the two: `git grep -inE 'stage[ -]subagent' -- docs/adr/ docs/superpowers/` returns **33 lines / 37 occurrences** across 8 files, and this repo keeps producing artifacts about the flatten history (the flatten design, the nested-review-fix design and plan, gh-30, and now this one). Every occurrence would pay a drift hit, resolved by the mention clause each time. The figure cross-checks against the shipped-text measurement above: repo-wide the same grep returns 35 lines — these 33 plus the two `execute-stage-subagent` lines in the pipeline copies.

**So #34's cluster ships with zero `_Avoid_:` names.** Framework consequence 4 is what licenses splitting the issue's proposal this way: the entries buy their value through Consumer B's collision half, which never reads `_Avoid_:` lines, so dropping all three avoided names costs the section nothing it was proposed for.

### Ruling on #34

**SHIPS, narrowed: a new `### Topology` section with four entries — Orchestrator, Leaf, Fan-out, Flat topology — and no `_Avoid_:` names.** `spawner` is **defined** inside **Orchestrator**, `controller` inside **Fan-out**, and the bare word `topology` inside **Flat topology**.

**What is not being claimed.**

- Not that these entries would have prevented #30's false positive with certainty. Consumer B's exemption is *"a word the artifact uses in the sense the repo already has"*, and a seed still has to notice. The claim is narrower and mechanical: the exemption becomes checkable against a definition the pass already opened, instead of against shipped prose the seed must first locate — which is the difference between a lookup and an investigation.
- Not that the glossary is now complete. `worker`, `subagent`, `run`, and `stage` remain unglossed and are deliberately left so; none has a measured second sense, and adding entries so the section looks symmetrical is the glossary growing to serve itself. Recorded as residue, not filed — per the gh-20 precedent that a residue a future reader trips on is an issue then, not a blocker now.
- Not that the `### Topology` heading does any mechanical work. Framework: neither consumer reads headings. It is chosen for readers, and the reason is that **Orchestrator**, **Leaf**, and **Flat topology** cannot be read apart, while **Fan-out** is what makes the third of them legible as a decision rather than a tautology. Not that all four are mutually defining — three are; **Fan-out** points at those three one-way, and is pointed at from **Provenance**, outside the section (see *The gap is real*).
- Not that a word defined inside another entry's body is mechanically exempt from Consumer B's collision grep. `:48` says *"any term the glossary does not settle"* and does not define *settle*; nothing in either consumer's text makes a definition's body count. `spawner`, `controller`, and bare `topology` are **defined**, not **settled** — the claim is that a seed asking the question finds an answer in a file it has already opened, not that it is spared the question.

## Issue #31 — `group-resolution agent` on the **Resolver** `_Avoid_:` line

### It passes the test that killed #34's three

Ask the `_Avoid_:` test: *is `group-resolution agent` an alternative name for the concept the **Resolver** entry defines?* Unambiguously yes. `CONTEXT.md:14` defines *"A reviewer in the second tier, which weighs grouped seed findings against the design rubric and decides what changes"*; `group-resolution agent` was, until PR #37, that exact population's name in that exact file. It is the same shape as the `group agent` already on the line, one qualifier longer.

That is the whole structural case, and it is worth noting that the contrast is not rhetorical: the three names #34 proposes fail on concept identity, and this one passes on concept identity. One test, run four times, three rejections and one admission.

### The cost, priced

By framework consequence 3, the cost is what the drift half pays over artifacts it will search.

- **Shipped text: nil.** 0 occurrences in `plugins/` since PR #37. Consumer A can only fire on a *reintroduction*, which is the point.
- **`docs/adr/0002`: nil.** It says `group-resolution tier`. No grep for the agent form — spaced or hyphenated — reaches the tier form. The ADR stays clear without anyone remembering to keep it clear.
- **`docs/superpowers/` records: 22 lines across 9 artifacts — and the drift half will never read any of them.** The clause searches *the artifact under review*, one document at a time; the 25 records committed at design time are frozen and are never re-reviewed. The standing corpus therefore contributes **zero** recurring cost, and the real question is what *future* artifacts pay. Measured: of the **12** artifacts dated 2026-07-28 or later, the **4** that are *about* this vocabulary (gh-20's spec and plan, gh-28/29's spec and plan) carry all **14** of those lines, and the other **8** carry **none**. The sharpest case is `2026-08-02-gh-30-flat-topology-design.md` — this repo's most recent design about the pipeline's spawn history, carrying **4** lines of `stage subagent` and **0** of `group-resolution agent`. Those are two different histories, and only one of them is the one this repo keeps revisiting.
- **Where a future artifact does discuss it, the call is easy — and easy *because* the name is dead.** Once no shipped text uses a name, a new artifact can only be quoting a record, which is the clause's most explicit genre (*"reporting a prior record's wording"*), or reintroducing the name, which is the finding the entry exists to produce. There is no third case. The corpus bears this out: of the 22 lines, exactly three are written in a document's own voice — `2026-07-20-dev-flow-design.md:66`, `…-plan.md:28`, and `2026-07-27-gh-7-review-depth-design.md:35` — and all three date from when the phrase *was* the shipped name, a condition that cannot recur. Every line written after the phrase came under scrutiny is a quotation, a substitution-table row, or a grep pattern.
- **Against the six names already on the list, this one is mid-pack and unusually clean.** Over the same 25 records: `boundary` 124 lines in 21 artifacts, `group agent` 40 in 9, `group-resolution agent` 22 in 9, `judge` 19 in 8, `arbiter` 10 in 5, `finder` 9 in 5, `first-pass reviewer` 8 in 4. The new name would rank third of seven by lines and joint-second by files — but unlike `judge` and `boundary`, which are ordinary English and carry this list's entire false-positive load, it is a three-word technical compound whose every hit sorts by inspection.
- **Marginal grep cost: one literal grep on a line that already exists.** The **Resolver** `_Avoid_:` line is already opened and already iterated; this adds a fourth name to it, 6 → 7 across the file. No entry is created, no section, no line count change beyond the one edited line.

### Why "already dead" is not a bar

The serious objection is #31's own: *"Adding entries for phrases that are already dead is close to widening against speculation."* It fails — but on the framework's own terms rather than on a precedent, and the difference is worth stating carefully, because the three dead names on the existing list prove less than they look like they prove.

**What they do prove: the *test* is not this repo's.** `finder`, `first-pass reviewer`, and `arbiter` each occur **exactly once** in tracked shipped text — on the `_Avoid_:` line that names them. gh-20 measured this, recorded that *"they will never fire"*, and proposed removing none of them. So liveness-in-shipped-text is demonstrably not the criterion this repo applies to `_Avoid_:` membership, and adopting it here would invalidate three standing entries as a side effect. The criterion is self-erasing besides: a name would qualify while the drift is live, you repair the live instances, and the name then fails the bar that justified adding it — `_Avoid_:` lines could exist only in the window between noticing drift and fixing it. gh-20 forecloses that directly: *"The glossary was written as the vocabulary the repo should use, not as a report on the vocabulary it had."*

**What they do not prove: that the cost is comparable.** `arbiter` and `first-pass reviewer` occur in `docs/superpowers/` only inside enumerations of the avoid list itself, so their standing cost really is near nil, and it would be sleight of hand to price 22 lines against that and call them the same thing. (`finder` is not even that clean: `2026-07-27-gh-7-review-depth-design.md:318` uses it twice on one line in the document's own voice, for findings-only reviewer prompts in another repo — a live concept-identity call on a name this repo treats as inert. Dead names are cheap, not free.) The precedent settles **eligibility**. Cost is settled in *The cost, priced* above, on its own measurements, and is not carried by this section.

**The framework answers the objection without the precedent at all.** Consequence 3 prices an `_Avoid_:` name by *"how often the name appears in text the drift half will search, and … whether the mention-versus-use clause carries those appearances"* — a metric over **artifacts**, not over shipped text. Whether the phrase is live in `plugins/` is not an input to it in either direction, which is why the *"already dead"* framing cannot decide this question: it measures the wrong corpus. The framework's own rule states the same thing prescriptively — *"`_Avoid_:` is prescriptive, not a census"* — and that rule is read off gh-20's shipped sentence rather than invented here.

And the demand side is not speculative either. The rubric licenses widening *"against concrete demand (planned siblings, 2+ instances)"*. Measured: the phrase was live in shipped text at **2 lines per mirror copy, 4 instances**, until PR #37; **two** prior sweeps (#20, #25) passed over this exact sentence and left it; and the gh-28/29 design records in its own words that its fix is *"an exhaustive sweep, not a seam"*, that the seam *"is deliberately not taken here"*, and that *"nothing in this change keeps it complete afterwards"*. This issue exists because that document named the missing seam and deferred it. The vector is documented, and its sources — an immutable ADR and 22 record lines — are exactly the material an agent reads before writing new prose.

**And the drift half is not purely the cost side of this ledger.** Consequence 3 calls the `_Avoid_:` line *"the only route to Consumer A's strict limb"*; it is equally the only route to Consumer B's drift half firing at all, and on this name that is the **earlier** of the two catches. The vector #31 names is *an agent reading history and copying it forward* — and an agent reads history while writing a design or a plan, which is the one document Consumer B searches. A reintroduction would be flagged at the design stage, before any shipped text is written. The naming reflex is measured, not assumed: three artifacts named the tier `group-resolution agent` in their own voice (`2026-07-20-dev-flow-design.md:66`, `…-plan.md:28`, `2026-07-27-gh-7-review-depth-design.md:35`). Those were correct when written — the phrase was the shipped name — so they are not retroactive defects and nothing here proposes editing them. What they establish is narrower and sufficient: **the artifact is where this tier gets named**, so the artifact is where a guard is worth having. Consumer A's strict limb then backstops it across every shipped path the angle does not exclude — `plugins/`, `CONTEXT.md`, `scripts/`, `.claude-plugin/`, `CLAUDE.md`, `docs/agents/`, and `docs/adr/`, which matters because ADR-0002's `group-resolution tier` is exactly what a future ADR author would be reading.

### Ruling on #31

**SHIPS.** `CONTEXT.md:15` becomes `_Avoid_: group agent, group-resolution agent, judge, arbiter` — the new name placed second so the two `group`-prefixed forms sit together and the existing order is otherwise preserved.

**What is not being claimed.**

- Not that the phrase is live. It is dead in shipped text, verified: `git grep -in 'group.resolution.agent' -- plugins/` → exit 1. The entry catches nothing today; that is its intended state, exactly as for `finder`, `first-pass reviewer`, and `arbiter`.
- Not that reintroduction is likely. Only that it is *possible from sources agents demonstrably read*, that nothing else prevents it, and that the guard costs one grep on a line that already runs.
- Not that `group-resolution tier` in ADR-0002 is drift, or that any `docs/superpowers/` record should be edited. Both are dated records; shipped prose moving past an ADR's wording is normal, and this change touches neither.
- Not that this makes the gh-28/29 sweep permanent in every respect. It closes the specific reintroduction path that document named. A differently-worded rival name would still get in.

## How the two rulings interact

**The explicit check #34 makes necessary: is a new topology entry a better home for `group-resolution agent`?** Run against both new candidates, and the answer is no in both cases.

- **Orchestrator.** No. `group-resolution agent` names a spawned second-tier reviewer; the orchestrator is the agent that spawns it. They are opposite ends of the same edge. No reading makes one an alternative name for the other.
- **Leaf.** No, and this is the near miss worth recording rather than waving past. A resolver *is* a leaf — so is a seed, a produce-subagent, an implementer, a fixer. **Leaf** names the category; `group-resolution agent` names one population inside it. An `_Avoid_:` name must be an alternative name for its entry's concept, and a name for a proper subset is not a name for the set: filing it under **Leaf** would assert that "leaf" and "group-resolution agent" pick out the same thing, which is false and would misdirect any future reader. **Resolver** defines exactly that population, so **Resolver** remains the correct and only home. The check found nothing; the placement is unchanged and now recorded rather than assumed.

**The interaction that is real runs the other way: #34 supplies the reason #31's addition is principled.** Before this change the glossary had no word for *a spawned thing*, so `agent` was an unmarked head-noun and `group-resolution agent` looked like a stylistic variant. With **Leaf** in the file, the repo's naming convention becomes legible: spawned populations are named by role — `seed`, `resolver`, `implementer`, `fixer` — and are collectively *leaves*; `… agent` as a head-noun is the pre-flatten register that `stage subagent` and `group agent` also belong to. #31's addition stops being a one-off patch on one phrase and becomes an instance of a convention the same change makes visible.

**Three composition checks, all clean.**

1. **File regions are disjoint.** #31 replaces one line inside *The review protocol*; #34 inserts a section between *The pipeline* and *Duplication*. Neither anchor moves the other's — the replacement is at line 15, the insertion after line 53 — and holding them in one change removes the sequencing #34 flagged.
2. **No new entry collides with an existing one.** **Leaf** sits one level above **Seed** and **Resolver** (category versus population) and contradicts neither. **Fan-out** is used in exactly **Provenance**'s existing sense — *"Evidence of fan-out and tier conformance"* — so defining it repairs the undefined-word-inside-a-definition defect **without editing the Provenance line**, which stays byte-identical. **Flat topology** shares no word with any existing headword.
3. **No new text uses any avoided name, including the newly added one.** The four definitions contain none of `finder`, `first-pass reviewer`, `group agent`, `group-resolution agent`, `judge`, `arbiter`, `boundary`. The one occurrence of the new name in the file is the `_Avoid_:` line itself, which both consumers exempt (*"the glossary's own state is never a finding"*).

**Combined cost, stated as one number.** Consumer A gains 4 headword greps and 1 avoided-name grep per diff review. Consumer B's collision half gets **cheaper** (four fewer unsettled terms, including the one that already cost a resolver group). Consumer B's drift half goes from 6 names to 7 — a 17% widening of the smallest trigger in the file, on a name with no live footprint at all and a frozen record footprint the drift half never reads (22 lines across 9 artifacts, three of them own-voice uses from before the rename).

## Considered and rejected alternatives

**Do nothing on both; record two no-change rulings.** Rejected. #34 names a measured, already-paid cost (a wasted seed and resolver group in #30, and an incorrect claim in gh-30's own self-review that had to be corrected during review) with a cheap, one-file, negative-marginal-cost fix. #31 names a seam its own predecessor document identified, deferred, and filed. Declining both would be discipline as a pose rather than as evidence-following.

**#34 exactly as filed — five entries plus `_Avoid_: nested, depth-2, stage subagent`.** Rejected on the avoid names — all three fail the `_Avoid_:` gate, and two carry measured collateral besides (5 shipped lines for `nested`, one live shipped violation for `stage subagent`) — and on the fifth entry (`spawner`, a synonym for `orchestrator`, defined inside that entry instead). The issue's own framing licenses this: *"Exact wording is the change's business, not this issue's."*

**#34's cluster, but as a lone `Topology` entry.** Rejected, and the issue's argument is adopted verbatim: a cluster-shaped hole patched with one entry is the per-instance fix the rubric ranks below the shared one, and each term here is only meaningful relative to the others.

**Add `controller` as a fifth headword.** Rejected on framework consequence 2. It names no concept **Orchestrator** and **Fan-out** do not already contain — it is the orchestrator viewed from one fan-out, which is why shipped text writes it appositively and in the plural — and it is the most common English word of the five, so its grep would be the highest-yield and the yield would be noise. Defined inside **Fan-out** instead, where it is glossed rather than merely used.

**Fold the four entries into the existing `### The pipeline` section instead of adding `### Topology`.** Rejected on readability, which is the only axis available (headings do nothing mechanical). The cluster is not pipeline-only: **Provenance**, a *review protocol* entry, already uses `fan-out`, and `adversarial-review`'s Model section names the orchestrator. Filing the vocabulary under *The pipeline* would assert a scope it does not have. A section that spans both is placed between them.

**Put the four entries under `### Cross-cutting` beside **Seam**.** Rejected: that section holds a general software-engineering concept borrowed from outside (attributed to Michael Feathers), not this system's own architecture. Mixing the two would make the section mean "everything else".

**Add `_Avoid_: agent` under **Leaf**, to reject the pre-flatten head-noun generically.** Rejected, and it is the tempting generalization of #31. `agent` is not an alternative name for a leaf — the orchestrator is an agent and is not a leaf — so it fails the `_Avoid_:` test. Worse, it is the highest-frequency word in the entire corpus; putting it on an avoid line would fire the drift half on essentially every artifact this repo produces. The correct scope for the head-noun problem is one rejected phrase at a time, which is what #31 is.

**Extend `scripts/check-sync.py` to validate `CONTEXT.md`'s structure** (entry count, `_Avoid_:` well-formedness). Rejected on the merits, not merely on scope — recorded so a later reader does not mistake exclusion for oversight. The glossary's format is not a mirror-pair invariant and shares nothing with what that script checks; a bespoke structural rule there would be a second, differently-shaped job in a script whose whole value is that it checks one thing. The per-change design-conformance check in *Success criteria* covers this change completely. `CLAUDE.md`'s `python3`-check rule is scoped to mirrored pairs and so does not reach `CONTEXT.md`; the check is modelled on it because the reasoning does reach — a check that retypes the design's text proves only that one transcription matches another — and because `check-sync.py` reads nothing here, so it is the only mechanical guard this file has. (`scripts/` is hard-excluded here in any case.)

**Repair `execute-stage-subagent` in both pipeline copies while at it.** Rejected. `plugins/` is hard-excluded, concurrent changes own those files, and — independently — there is nothing wrong with the sentence: naming a construct in order to deny it is correct prose. It is a cost only under an `_Avoid_: stage subagent` rule, which this change declines to create. Not filed as a follow-up, because there is no defect to file.

## The edit

One file, `CONTEXT.md`, two edits. Both blocks below are the **exact final bytes**; copy them, do not retype them. They are the only plain (untagged) fenced blocks in this document, in this order — `python3 scripts/design_blocks.py <this design>` must report shape `[1, 14]`.

**Before either edit, confirm the anchors.** Run from `<wd>`:

```bash
wc -l < CONTEXT.md                                                                    # expect: 67
grep -n '^_Avoid_: group agent, judge, arbiter$' CONTEXT.md                           # expect: exactly one hit, line 15
grep -n '^The short, opaque, immutable identifier for one pipeline run,' CONTEXT.md   # expect: exactly one hit, line 53
```

Any other result — no hit, more than one, a different line number — means the file has drifted from the base this design measured: **stop and re-derive, do not edit.** Both edits are then made by **matching the anchor text**, never by line index — replace the old `_Avoid_:` line by its full text, and insert block 1 by matching the **Slug** definition line and re-emitting it followed by the block. A text-matched edit that cannot find its anchor fails without writing; a line-indexed one corrupts the wrong line and leaves criterion 6 to discover it afterwards.

### Block 0 — replaces the **Resolver** `_Avoid_:` line (line 15 at base)

Anchor: the block **replaces** this line, whose current text is

```text
_Avoid_: group agent, judge, arbiter
```

Replacement:

```
_Avoid_: group agent, group-resolution agent, judge, arbiter
```

### Block 1 — inserted directly after the **Slug** definition (line 53 at base)

Anchor line — the block goes **directly after** it, and nothing else moves:

```text
The short, opaque, immutable identifier for one pipeline run, threading its branch, its document filenames, and its PR. Renaming a feature changes prose, never the slug.
```

The block's **first line is empty**: it supplies the blank line that separates *The pipeline* from the new section. The block has **no** trailing blank line — the file's existing blank line after the anchor (old line 54) becomes the separator before `### Duplication`. Fourteen lines:

```

### Topology

**Orchestrator**:
The agent that drives one pipeline run from stage to stage, and the run's only *spawner* — the one agent that spawns any other; every other agent in the run is a leaf.

**Leaf**:
A spawned subagent that spawns nothing itself: a produce-subagent, one of a review's seeds or resolvers, one of SDD's implementers or fixers.

**Fan-out**:
One agent dispatching N workers and holding their loop — a review's seeds and resolvers, SDD's implementers. That agent is the fan-out's *controller*, and in both pipelines it is always the orchestrator, which is why fanning out adds no level.

**Flat topology**:
The property that every spawn in a run is one level deep: the orchestrator spawns leaves, and nothing else spawns at all. *Topology* alone names this axis — which agent may spawn which — and nothing else here. Required rather than preferred, for reasons independent of any harness version (ADR-0003).
```

### The resulting file

67 → **81** lines; 17 → **21** entries; 4 → **5** sections; 3 `_Avoid_:` lines (unchanged) carrying 6 → **7** names. The **Seam** entry's `_Avoid_: boundary` moves from line 67 to line 81 and stays the file's last line.

## Success criteria

Every item is mechanically checkable. `<wd>` is the absolute working directory; run from it.

1. **The removed line is gone** — the grep-for-what-you-removed discipline `CLAUDE.md` requires of mirrored pairs, adopted here on its own merits: `CONTEXT.md` is not a mirrored pair, and nothing else in the repo would notice a stale copy of the old line.

   ```bash
   git grep -n '^_Avoid_: group agent, judge, arbiter$' -- CONTEXT.md   # expect: no output, exit 1
   ```

2. **No rejected name entered the glossary:**

   ```bash
   git grep -in -e 'nested' -e 'depth-2' -e 'stage subagent' -- CONTEXT.md   # expect: no output, exit 1
   ```

3. **The three `_Avoid_:` lines read exactly:**

   ```bash
   grep -n '^_Avoid_:' CONTEXT.md
   # 11:_Avoid_: finder, first-pass reviewer
   # 15:_Avoid_: group agent, group-resolution agent, judge, arbiter
   # 81:_Avoid_: boundary
   ```

4. **Structure:**

   ```bash
   wc -l < CONTEXT.md            # expect: 81
   grep -c '^\*\*' CONTEXT.md    # expect: 21
   grep -c '^### ' CONTEXT.md    # expect: 5
   grep -c '^_Avoid_:' CONTEXT.md # expect: 3
   ```

   `wc -l` and criterion 6's `len(new)` are not redundant — `split_lines` treats a missing final newline as invisible and `wc -l` does not, so the two together are what pin it. Neither can be dropped.

5. **The new entries are present and the Provenance line is untouched:**

   ```bash
   git grep -c -i 'orchestrator' -- CONTEXT.md   # expect: 3
   git grep -n '^### Topology$' -- CONTEXT.md    # expect: one hit, line 55
   git grep -n 'Evidence of fan-out and tier conformance' -- CONTEXT.md   # expect: one hit, line 27
   grep -nE '^\*\*(Orchestrator|Leaf|Fan-out|Flat topology)\*\*:$' CONTEXT.md
   # 57:**Orchestrator**:
   # 60:**Leaf**:
   # 63:**Fan-out**:
   # 66:**Flat topology**:
   ```

6. **Design conformance — the only mechanical guard on the new text.** `CLAUDE.md` mandates this shape of check only for mirrored pairs, which `CONTEXT.md` is not; it is written here anyway because the rule's reasoning transfers whole — the design supplies its replacement text as fenced blocks, so a check that retypes them proves only that two transcriptions agree — and because `check-sync.py` reads nothing in this file (A3). A short `python3` check therefore re-reads both blocks **from this design on disk**, never retyped, and asserts the post-change file is exactly the pre-change file with block 0 substituted at line 15 and block 1 inserted after line 53. Because the reconstruction is total, this single assert also discharges "nothing else in the file moved":

   ```python
   import difflib, subprocess, sys

   ROOT = "<wd, absolute>"
   sys.path.insert(0, f"{ROOT}/scripts")     # absolute: this check has no other cwd dependency
   from design_blocks import read_blocks

   DESIGN = "docs/superpowers/specs/2026-08-02-gh-31-34-glossary-contents-design.md"
   BASE = subprocess.run(["git", "-C", ROOT, "merge-base", "origin/main", "HEAD"],
                         capture_output=True, text=True, check=True).stdout.strip()

   def split_lines(text):            # check-sync.py's rule; agrees with `wc -l` when the file ends in a newline
       out = text.split("\n")
       if out and out[-1] == "":
           out.pop()
       return out

   old = split_lines(subprocess.run(["git", "-C", ROOT, "show", f"{BASE}:CONTEXT.md"],
                                    capture_output=True, text=True, check=True).stdout)
   new = split_lines(open(f"{ROOT}/CONTEXT.md", encoding="utf-8").read())
   blocks = read_blocks(f"{ROOT}/{DESIGN}", [1, 14])

   assert len(old) == 67, len(old)
   assert old[14] == "_Avoid_: group agent, judge, arbiter", old[14]
   assert old[52].startswith("The short, opaque, immutable identifier"), old[52]
   want = old[:14] + blocks[0] + old[15:53] + blocks[1] + old[53:]
   assert new == want, "\n".join(difflib.unified_diff(want, new, "want", "got", lineterm=""))
   assert len(new) == 81, len(new)
   print("design-conformance: OK")
   ```

   The two retyped strings are *pre-edit* anchors checked against the base revision, so a typo here fails the assert instead of silently blessing a misrouted edit; *The edit*'s pre-flight step is what stops the misroute in the first place. `read_blocks`'s required shape argument `[1, 14]` exits non-zero if this document's block shape moved.

   `BASE` is the merge-base, not `origin/main`'s tip, and no `git fetch` is mandated: a concurrent PR landing on `main` advances the tip but not the merge-base, so freshening the remote-tracking ref cannot change what `old` is. The merge-base is the revision this branch forked from, which is the only one the reconstruction is meaningful against. If this branch is later rebased onto a `main` that did change `CONTEXT.md`, `old` moves with it and `assert len(old) == 67` fails loudly — the check surfaces the collision rather than hiding it. The check is also indifferent to whether the edit is committed yet, since `new` is read from the working tree.

   **What the shape argument does not cover, and why nothing here tries to.** `read_blocks` compares line counts, and criterion 6 draws its expected text from the same document a rewrite would have changed — so a rewrite that alters wording *inside* a block while preserving its line count passes both. That is deliberate: the blocks are this design's output and a design review is entitled to rewrite them, so a content hash pinned in this file would have to be recomputed by hand on every legitimate rewrite, and the only window in which it could catch anything is the window in which it is guaranteed to be stale. The independent pins are instead the *retyped* expectations elsewhere in *Success criteria*, written from the rulings rather than read from the blocks: criterion 3 fixes block 0's text verbatim, and criteria 4 and 5 fix block 1's section heading, its four headwords, and the counts they imply. A block edited without editing those fails loudly; a block whose definition *prose* is reworded passes, which is correct — the rulings fix which terms are defined, not the sentences that define them. **Operational consequence for whoever rewrites this document: every fenced block added to it must carry an info string (` ```bash `, ` ```python `, ` ```text `), because `read_blocks` indexes plain blocks only and a third plain block would shift every index in this check.**

7. **Nothing else regressed:**

   ```bash
   python3 scripts/check-sync.py    # expect: exit 0, final line `check-sync: all checks passed`
   claude plugin validate .         # expect: exit 0, exactly 8 `No author information provided` warnings, no errors
   ```

   `check-sync.py`'s per-pair summary counts (`89 lines, 1 declared exception` at design time) are deliberately not pinned: they describe a hard-excluded file that concurrent changes own, and a legitimate edit there would fail this criterion for a reason that has nothing to do with this change.

   Neither reads `CONTEXT.md` (A3). They prove the change broke nothing; criterion 6 is what proves it is right.

8. **Scope — file-level.** With `BASE = git -C <wd> merge-base origin/main HEAD` (never hardcoded):

   ```bash
   git diff --stat "$BASE"    # BASE → working tree: committed and uncommitted alike
   git status --porcelain     # anything untracked
   ```

   Between them these must name **only** `CONTEXT.md` and paths under `docs/superpowers/`. `$BASE..HEAD` is deliberately not used: it sees committed work only, so it would pass vacuously on an uncommitted implementation — the same state criterion 6 reads `CONTEXT.md` from. Any other path — in particular anything under `plugins/`, `scripts/`, `docs/adr/`, `docs/agents/`, `.claude-plugin/`, or `CLAUDE.md` — is a scope violation. Line-level scope is criterion 6's `assert new == …`, which pins all 81 lines.

## Out of scope

Hard-excluded. A proposal touching any of these is a blocker, not a design.

- **Everything under `plugins/` — every file, both plugins.** No shipped text changes here: #34 is a glossary gap, and #31's phrase is already absent from `plugins/` (PR #37). Concurrent changes own several of these files. This includes `plugins/*/skills/adversarial-review/SKILL.md`, whose `:42` and `:48` this document quotes at length and does not touch, and the two pipeline `SKILL.md`s, whose `execute-stage-subagent` at `:225`/`:219` is measured above and deliberately left alone.
- **`scripts/`** — `check-sync.py` is untouched (it does not read `CONTEXT.md`, so nothing it checks can change) and no structural check is added to it; rejected on the merits under *Considered and rejected*. `design_blocks.py` is *used* by criterion 6, unmodified.
- **`docs/adr/0002-opus-resolvers-and-the-end-of-adversary-not-author.md`** — carries `group-resolution tier`, a different string that no grep for the agent form reaches. A dated record; shipped prose moving past its wording is normal and is not drift.
- **`docs/adr/0003-flat-topology-for-the-dev-flow-pipelines.md`** — the decision the new entries name. The **Flat topology** entry *points at* it; the glossary states what the term means, the ADR states why the property is required, and neither restates the other.
- **`docs/agents/domain.md`** — states the concept scoping every `_Avoid_:` line depends on, and is load-bearing for this design's `_Avoid_:` test. Unchanged, and relied upon exactly as written.
- **`CLAUDE.md`**, **`.claude-plugin/`**, and every pre-existing file under `docs/superpowers/`.
- **`CONTEXT.md`'s own untouched regions.** Only line 15 changes and 14 lines are inserted after line 53. In particular the **Provenance** entry keeps its undefined-until-now `fan-out` **byte-identical** — the new entry supplies the definition, so no byte there needs to move; and the **Resolver** definition line 14 is unchanged, only its `_Avoid_:` line.

## Assumptions

- **A1.** Base is `b4b5d1c` (`origin/main` at design time). Line 15 is `_Avoid_: group agent, judge, arbiter`, line 53 is the **Slug** definition, and the file is 67 lines — all three verified. The line numbers in *The edit* are descriptive; the anchors are the quoted **text**, and *The edit*'s pre-flight step plus its text-matched edits are what make that binding — if either anchor is absent or not unique, the implementation halts before writing anything. Criterion 6 re-asserts all three afterwards against the base revision, so a drifted file fails twice: once before the edit and once after.
- **A2. No version bump.** `CONTEXT.md` sits at the repo root, outside `plugins/`, so it enters no version-keyed install cache (`~/.claude/plugins/cache/taylor-plugins/<plugin>/<version>/`) and `CLAUDE.md`'s bump rule — which is scoped to `plugins/<name>/.claude-plugin/plugin.json` and justified by that cache — does not apply. No `plugin.json` is edited; editing one would be a scope violation under *Out of scope*. Precedent: `4049d23` and `c8b2182` both changed `CONTEXT.md` alone with no bump.
- **A3. `check-sync.py` cannot validate this change.** Verified: it contains no reference to `CONTEXT.md`. It must still pass unchanged (criterion 7), but it proves nothing about the new text — criterion 6 is the whole mechanical surface.
- **A4.** `claude plugin validate .` emitting exactly 8 `No author information provided` warnings and exiting 0 is the expected pass state, per `CLAUDE.md`.
- **A5. Issue closure is the pipeline's integration step, not part of the implementation.** Both issues ship, so both close on merge — neither is a no-change ruling, and the A5 precedent's "close with the design section as the closing comment" form applies to only one sub-question here. **#34's closing comment must carry the *The three `_Avoid_:` names #34 proposes* section**, because that sub-question *is* a recorded no-change: without it the three rejected names (`nested`, `depth-2`, `stage subagent`) will be re-proposed by the next reader of the issue, which is exactly the re-derivation these issues exist to stop. **#31 closes on merge** with a pointer to *Issue #31*, since the ruling is "yes" and the reasoning — particularly the `finder`/`first-pass reviewer`/`arbiter` precedent — is what stops the question being re-opened. No follow-up issues are filed by this change.
- **A6.** No test framework exists in this repo; the commands in *Success criteria* are the whole verification surface.
- **A7. Residues, recorded rather than filed.** Two, both deliberate. (i) `worker`, `subagent`, `run`, and `stage` remain unglossed; none has a measured second sense in shipped text, and per the gh-20 precedent an entry added so a section looks complete is the glossary serving itself. (ii) `execute-stage-subagent` survives in both pipeline copies as the name of a denied construct; it is correct prose, `plugins/` is hard-excluded, and it is a cost only under a rule this change declines to create. Neither is filed — filing an issue for a non-defect manufactures the re-derivation these two issues were filed to end.

## Spec self-review

- **Placeholders / TBDs:** none. Both edits are given as complete final bytes with their anchors; every count, line number, and grep result is stated with its expected output; the one substitution in criterion 6 (`<wd>`) is the working directory the implementation already holds.
- **Internal consistency:** the arithmetic closes. 67 old lines = `old[:14]` (14) + line 15 (1, replaced) + `old[15:53]` (38) + `old[53:]` (14); 81 new = 14 + 1 + 38 + **14 inserted** + 14. Entry count 17 + 4 = 21; section count 4 + 1 = 5; avoided names 6 + 1 = 7 on an unchanged 3 `_Avoid_:` lines; the **Seam** avoid line moves 67 → 81 as the file's last line. Criteria 3, 4, and 6 assert these independently of each other. Block 1's line count is stated three times — "Fourteen lines", `read_blocks(..., [1, 14])`, and the reconstruction — and all three agree. Criterion 5's pinned line numbers fall out of the same arithmetic: the block's 14 lines occupy 54–67, so `### Topology` lands at 55 and the four headwords at 57 / 60 / 63 / 66.
- **Scope:** the authorized file set is `CONTEXT.md` and this document (plus its plan). Criterion 8 checks it by file; criterion 6's total reconstruction checks it by line. No proposal in this document touches `plugins/`, `scripts/`, `CLAUDE.md`, `docs/adr/`, `docs/agents/`, or `.claude-plugin/`; no blocker was hit.
- **Ambiguity:** the one place a fresh implementer could go wrong is block 1's whitespace — its first line is empty and it has no trailing blank line. Stated at the point of use and asserted byte-exactly by criterion 6, which reads the block from disk rather than from an implementer's transcription. The second is grep scope: the rejected names and `group-resolution agent` legitimately survive in `docs/`, so criteria 1 and 2 are scoped to `CONTEXT.md`.
- **Applying this repo's *Drift* pass to this document.** Over the **post-change** avoid list of seven — `finder`, `first-pass reviewer`, `group agent`, `group-resolution agent`, `judge`, `arbiter`, `boundary` — searched spaced and hyphenated. `finder`, `first-pass reviewer`, `arbiter`, `boundary` occur only in enumerations of the avoid list itself and in measurements of where they appear — including *Why "already dead" is not a bar*'s report of `finder`'s own-voice use in a prior design: mentions, in the "quoting the glossary" and "reporting a prior record's wording" genres. `group agent` and `group-resolution agent` occur throughout, and **every occurrence in this document is a mention** across all three enumerated genres — quoting `CONTEXT.md:15`, quoting the replacement text under decision, and reporting prior records (#20, #25, #37, ADR-0002, the gh-28/29 design, and the three artifacts that used the phrase in their own voice before the rename). This document names the second tier `resolver` throughout and never once uses either phrase to refer to it. `judge` occurs only as the ordinary English verb and in the avoid-list enumerations; its inflections (`judgment`, `judging`) are not the term. **No finding.**
- **Applying *Glossary conformance* to the diff this change produces.** Iterating all 21 post-change entries and all 7 avoided names over the added shipped lines (`CONTEXT.md`'s new section and its edited `_Avoid_:` line): the added text names **Orchestrator**, **Leaf**, **Fan-out**, and **Flat topology** — the four concepts it defines — and uses **Seed**, **Resolver**, and **Slug** senses (`a review's seeds or resolvers`, `one pipeline run`) exactly as their entries define them. The three words carried inside definitions — `spawner`, `controller`, bare `topology` — are each glossed by the sentence that carries them, never left as bare uses, which is the `fan-out`-in-**Provenance** defect this change repairs. No avoided name appears in any definition; the single occurrence of `group-resolution agent` is on the `_Avoid_:` line, which both consumers exempt under *"the glossary's own state is never a finding"*. **No finding** — the change is consistent with the rules that motivated it.
- **Applying *Collision* to this document.** It coins one word, `headword`, for the bolded term line of a glossary entry. Measured: `git grep -in headword` returns nothing across tracked files, so there is no repo sense to collide with (this document itself is untracked as measured — see *What was verified before designing*); within this document it carries one sense throughout, contrasted consistently with `_Avoid_: name`. It names a property of the glossary's *format*, not a domain concept, and is deliberately not proposed as an entry. **No finding.**
- **ADR conflict check** (`docs/agents/domain.md`): nothing here contradicts ADR-0001, ADR-0002, or ADR-0003. The **Flat topology** entry states ADR-0003's decision in ADR-0003's own terms and cites it by number; the **Resolver** `_Avoid_:` addition leaves ADR-0002's `group-resolution tier` untouched and unreached, consistent with the gh-28/29 ruling that shipped prose is expected to age past an ADR's wording.
