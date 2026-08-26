### Words and phrases to replace
Words are organized into three tiers based on how reliably they signal AI-generated text. This tiered approach — adapted from [brandonwise/humanizer](https://github.com/brandonwise/humanizer)'s vocabulary research — reduces false positives on words that are fine in isolation but suspicious in clusters.

- **Tier 1 — Always flag.** These words appear 5–20x more often in AI text than human text. Replace on sight.
- **Tier 2 — Flag in clusters.** Individually fine, but two or more in the same paragraph is a strong AI signal. Flag when they appear together.
- **Tier 3 — Flag by density.** Common words that AI simply overuses. Only flag when they make up a noticeable fraction of the text (roughly 3%+ of total words).

**Match inflected forms.** Each entry below covers the listed word *and its morphological variants* — adverb (`-ly`), gerund/participle (`-ing`), plural, comparative/superlative, and verb conjugations — unless a variant carries a distinct, legitimate meaning. So `genuine` also flags `genuinely`, `leverage` also flags `leveraging` / `leveraged`, `delve` covers `delving`, and `meticulous` covers `meticulously`. When a variant has a separate honest sense (e.g. `real` meaning factual, not the intensifier in "a real improvement"), judge by context rather than matching blindly.

#### Tier 1 — Always replace

Tier 1 splits into two bands. **Both are always replaced**; the edit is the same. What differs is what a flag *means*.

**1A — AI frequency markers.** Words claimed to appear far more often in machine text than in human writing. A cluster of these is evidence about how a passage was produced.

**1B — Clarity edits.** Wordiness and inflated formality. Replacing them is good writing regardless of who wrote the sentence, and a 1B hit is **not** evidence of machine authorship. Measured against 257 paragraphs of verified pre-2023 human prose, 1B entries fire on ordinary professional and formal writing at a meaningful rate — `in order to`, `utilize`, `commence`, `ascertain`, and `endeavor` are simply the words some people reach for. The detector emits these as `tier1-clarity`, weights them like Tier 2, and excludes them from the dense-AI-vocabulary signal so a wordiness fix can never push a document toward an AI classification.

In `detect` mode, report the two bands separately. Presenting a wordiness fix as authorship evidence is the error this split exists to prevent.

Caveat worth keeping visible: the "appears far more often in AI text" claim behind 1A is **inherited, not measured here**. It traces to [brandonwise/humanizer](https://github.com/brandonwise/humanizer), which states a 5–20x ratio without publishing a method or dataset. Treat 1A as a well-supported convention rather than a verified statistic until this repo measures the ratios itself against a machine-written corpus.

##### Tier 1A — AI frequency markers

| Replace | With |
|---|---|
| delve / delve into | explore, dig into, look at |
| landscape (metaphor) | field, space, industry, world |
| tapestry | (describe the actual complexity) |
| realm | area, field, domain |
| paradigm | model, approach, framework |
| embark | start, begin |
| beacon | (rewrite entirely) |
| testament to | shows, proves, demonstrates |
| robust | strong, reliable, solid |
| comprehensive | thorough, complete, full |
| cutting-edge | latest, newest, advanced |
| leverage (verb) | use |
| pivotal | important, key, critical |
| underscores | highlights, shows |
| meticulous / meticulously | careful, detailed, precise |
| seamless / seamlessly | smooth, easy, without friction |
| game-changer / game-changing | describe what specifically changed and why it matters |
| hit differently / hits different | (say what specifically changed, or cut) |
| watershed moment | turning point, shift (or describe what changed) |
| marking a pivotal moment | (state what happened) |
| the future looks bright | (cut — say something specific or nothing) |
| only time will tell | (cut — say something specific or nothing) |
| nestled | is located, sits, is in |
| vibrant | (describe what makes it active, or cut) |
| thriving | growing, active (or cite a number) |
| despite challenges… continues to thrive | (name the challenge and the response, or cut) |
| showcasing | showing, demonstrating (or cut the clause) |
| deep dive / dive into | look at, examine, explore |
| unpack / unpacking | explain, break down, walk through |
| bustling | busy, active (or cite what makes it busy) |
| intricate / intricacies | complex, detailed (or name the specific complexity) |
| complexities | (name the actual complexities, or use "problems" / "details") |
| ever-evolving | changing, growing (or describe how) |
| enduring | lasting, long-running (or cite how long) |
| daunting | hard, difficult, challenging |
| holistic / holistically | complete, full, whole (or describe what's included) |
| actionable | practical, useful, concrete |
| impactful | effective, significant (or describe the impact) |
| learnings | lessons, findings, takeaways |
| thought leader / thought leadership | expert, authority (or describe their actual contribution) |
| best practices | what works, proven methods, standard approach |
| at its core | (cut — just state the thing) |
| synergy / synergies | (describe the actual combined effect) |
| interplay | relationship, connection, interaction |
| keen (as intensifier) | interested, eager, enthusiastic (or cut — just state the interest) |
| genuinely / genuine (as intensifier) | (cut — just state the fact) |
| symphony (metaphor) | (describe the actual coordination or combination) |
| embrace (metaphor) | adopt, accept, use, switch to |
| load-bearing *(metaphor)* | essential, critical, necessary — or say what breaks if you remove it |

**Hyphen required:** unhyphenated "load bearing" is ordinary English ("the load bearing down on the bridge") — only the hyphenated compound is the tell.

**Construction carve-out:** `load-bearing` before a literal structural noun (`wall`, `beam`, `column`, `joist`, `truss`, `member`, `footing`, `slab`, `stud`, `partition`, `masonry`, `lintel`, `pier`, `rafter`, `girder`, `capacity`), optionally with one material or position adjective in between (`load-bearing structural wall`), is standard building terminology — don't flag. Abstract-capable nouns (`structure`, `element`, `frame`, `foundation`) are excluded on purpose, so "the load-bearing structure of his argument" still flags. Known gap: predicative use ("the wall is load-bearing") still flags — see issue #56.

##### Tier 1B — Clarity edits

Wordiness and formality, not authorship evidence. Same fix, weaker claim.

| Replace | With |
|---|---|
| utilize | use |
| in order to | to |
| due to the fact that | because |
| serves as | is |
| features (verb) | has, includes |
| boasts | has |
| presents (inflated) | is, shows, gives |
| commence | start, begin |
| ascertain | find out, determine, learn |
| endeavor | effort, attempt, try |

#### Tier 2 — Flag when 2+ appear in the same paragraph

These words are legitimate on their own. When two or more show up together, the paragraph likely needs a rewrite.

| Replace | With |
|---|---|
| harness | use, take advantage of |
| navigate / navigating | work through, handle, deal with |
| foster | encourage, support, build |
| elevate | improve, raise, strengthen |
| unleash | release, enable, unlock |
| streamline | simplify, speed up |
| empower | enable, let, allow |
| bolster | support, strengthen, back up |
| spearhead | lead, drive, run |
| resonate / resonates with | connect with, appeal to, matter to |
| revolutionize | change, transform, reshape (or describe what changed) |
| facilitate / facilitates | enable, help, allow, run |
| underpin | support, form the basis of |
| nuanced | specific, subtle, detailed (or name the actual nuance) |
| crucial | important, key, necessary |
| multifaceted | (describe the actual facets, or cut) |
| ecosystem (metaphor) | system, community, network, market |
| myriad | many, numerous (or give a number) |
| plethora | many, a lot of (or give a number) |
| encompass | include, cover, span |
| catalyze | start, trigger, accelerate |
| reimagine | rethink, redesign, rebuild |
| galvanize | motivate, rally, push |
| augment | add to, expand, supplement |
| cultivate | build, develop, grow |
| illuminate | clarify, explain, show |
| elucidate | explain, clarify, spell out |
| juxtapose | compare, contrast, set side by side |
| paradigm-shifting | (describe what actually shifted) |
| transformative / transformation | (describe what changed and how) |
| cornerstone | foundation, basis, key part |
| paramount | most important, top priority |
| poised (to) | ready, set, about to |
| burgeoning | growing, emerging (or cite a number) |
| nascent | new, early-stage, emerging |
| quintessential | typical, classic, defining |
| overarching | main, central, broad |
| quietly | cut, or name the concrete contrast |
| deeply *(significance collocations only — "deeply integrated," "deeply committed," "deeply rooted"; literal uses like "deeply nested" or "cares deeply" never count toward a cluster)* | cut, or name what specifically runs deep |
| underpinning / underpinnings | basis, foundation, what supports |

#### Tier 3 — Flag only at high density

These are normal words. Only flag them when the text is saturated with them — a sign that AI filled space with vague praise instead of specifics.

| Word | What to do |
|---|---|
| significant / significantly | Replace some with specifics: numbers, comparisons, examples |
| innovative / innovation | Describe what's actually new |
| effective / effectively | Say how or cite a metric |
| dynamic / dynamics | Name the actual forces or changes |
| scalable / scalability | Describe what scales and to what |
| compelling | Say why it compels |
| unprecedented | Name the precedent it breaks (or cut) |
| exceptional / exceptionally | Cite what makes it an exception |
| remarkable / remarkably | Say what's worth remarking on |
| sophisticated | Describe the sophistication |
| instrumental | Say what role it played |
| world-class / state-of-the-art / best-in-class | Cite a benchmark or comparison |
| verbatim | Usually redundant with the verb ("copies X verbatim" = "copies X") — cut it. If the exactness marks a contrast, name it: byte-for-byte, word for word, unchanged. Term of art in legal/research/QA registers ("verbatim transcript / record / testimony"), so weigh density in that context before flagging |

#### Tier 3 phrases — Flag at density or in clusters

Multi-word boilerplate that's individually unobjectionable but stacks heavily in AI-generated content (crypto, web3, DePIN, AI/infra reviews are the worst offenders). Flag at **2+ uses of the same phrase** (the per-phrase rule — lower threshold than single-word Tier 3 because a two-word match repeated twice is already stronger evidence than re-using "significant"), *plus* a **cluster rule**: three or more *distinct* phrases from this table in one piece is a strong signal even when each phrase only appears once — that's the shape LLMs take when they vary their own boilerplate to seem less repetitive.

| Phrase | What to do |
|---|---|
| emerging sector / emerging space / emerging category | Name the actual sector or what's emerging about it |
| the integration of (X with Y) | Describe what's being integrated and what changes for the user |
| the intersection of (X and Y) | Pick the specific overlap that matters or cut the framing |
| community-driven | Name what the community does. "Community-driven" alone is filler |
| long-term sustainability | Cite the time horizon and the constraint. "Long-term" is hand-waving |
| user engagement | Name the action. "Engagement" is a wrapper around clicks/comments/retention |
| decentralized compute | Specify the architecture or cut. The phrase has become a category label, not a claim |
| (sustainable) reward emissions | Cite the emission schedule and the sink |
| tokenized incentive structures | Describe the actual mechanism (vesting, gauge, bonded LP, etc.) |
| designed for long-term [X] | Cut "designed for" — either it is or it isn't. Then state the property |

### Template phrases (avoid)
These slot-fill constructions signal that a sentence was generated, not written. If a phrase has a blank where a noun or adjective could go and still sound the same, it's too generic.

- "a [adjective] step towards [adjective] AI infrastructure" → describe the specific capability, benchmark, or outcome
- "a [adjective] step forward for [noun]" → same rule: say what actually changed
- "Whether you're [X] or [Y]" → false-breadth construction. Pick the audience you're actually addressing, or cut. "Whether you're a startup founder or an enterprise architect" means nothing — it's just "everyone."
- "I recently had the pleasure of [verb]-ing" → review/social AI pattern. Just say what happened: "I talked to," "I read," "I attended."

### Significance inflation
- Phrases like "marking a pivotal moment in the evolution of..." or "a watershed moment for the industry" inflate routine events into history-making ones. State what happened and let the reader judge significance.
- If the sentence still works after you delete the inflation clause, delete it.

### Aphorism formulas
- Slot-fill profundity: "X is the language of Y," "X is the currency of Z," "the architecture of trust," "X becomes a trap," "X is not a tool but a mirror." The formula turns an ordinary claim into something that sounds quotable without adding precision — the shape does the persuading instead of the evidence.
- Fix: replace the formula with the concrete claim it gestures at. "Symmetry is the language of trust" → "symmetric layouts feel more predictable to users."
- Distinct from significance inflation (which puffs up an event's importance) and from the persuasive-authority tropes under Confidence calibration (which announce depth): this pattern manufactures a general law out of a specific observation.
- Carve-out: quotations and established idioms ("time is money") are attributed speech or common coin — leave them. Adapted from `blader/humanizer` P32.

### Generic future-narrative closers
- "May become one of the most important narratives of the next market cycle," "could become the defining trend of the coming decade," "is poised to become the next major chapter in [X]." AI defaults to this shape when it needs to land a closing thought without committing to a falsifiable claim. The closer is grammatically a prediction but contains no testable content.
- Pattern: modal (may / could / will / is poised to) + "become" + (one of) the most [adjective] + (narrative / story / trend / theme / chapter / movement / force).
- Fix: pick the falsifiable version. "DePIN compute may exceed AWS spot pricing for embarrassingly parallel workloads by 2027" is a prediction. "The intersection of AI and DePIN may become one of the most important narratives of the next market cycle" is not.

### Hedge-stacked predictions
- Stacking a modal with a hedge adverb: "could potentially create," "may eventually unlock," "might ultimately transform." Either word alone is acceptable; the stack is the tell. Each hedge cancels the next, leaving a sentence that asserts nothing while sounding cautious and thoughtful.
- Fix: pick one. If you mean "could create," say that. If you mean "potentially creates," say that. Both together is filler.

### "Real/actual" adjective inflation
- "Real on-chain tokenomics," "actual reward sustainability," "genuine utility," "true product-market fit." Using `real` / `actual` / `genuine` / `true` as an empty intensifier on an abstract noun implies the rest of the field is fake or superficial — without naming what makes this instance the real one. Common in crypto/AI/web3 content where the writer wants to signal sophistication.
- Distinct from the existing "hollow intensifiers" rule (genuine / truly / quite frankly as sentence-level hedges). This is the noun-modifier form, where the intensifier latches onto an abstract noun to manufacture a contrast that goes unsaid.
- **Carve-out — named contrast:** if the sentence explicitly names what the fake/superficial version is, leave it. "Real on-chain settlement, not bridged IOUs" or "actual revenue from paying customers, not grants" is honest contrastive writing. The AI tell is the unsaid contrast.
- Fix when no contrast is named: drop the adjective and add the specific claim. "Reward sustainability" → "rewards funded from $X/mo in fees rather than emissions."

### Moral-adjective category errors
- AI glues moral or character adjectives (`honest`, `genuine`, `faithful`, `truthful`) onto non-agentic technical nouns (`shape`, `number`, `representation`, `accuracy`, `curve`, `output`) where the adjective cannot literally modify the noun. "An honest shape" — shapes are not moral agents; it is a category error. The same move appears as the adverb form: "described honestly," "flagged honestly" — the passive voice hides that there is no subject capable of honesty.
- **Fix:** state the concrete property instead of the moral one. "An honest shape" → "a more realistic curve." "A more honest representation" → "a clearer picture." Cut moral adverbs from passive constructions entirely — "flagged honestly" → "noted." Let the evidence carry the honesty claim.
- **Related — ontological slop on assumptions:** "The assumption stops being true." Assumptions do not flip from true to false; they degrade in adequacy. Write "the assumption breaks down" or "no longer holds."
- **Related — gratuitous universal quantifiers:** "Taught in every first-year biochemistry course" instead of "taught in introductory biochemistry." The universal claim ("every") is unverifiable and unnecessary — it borrows authority from a scope the writer cannot check. Replace with the actual scope or drop the quantifier.

### Generic conclusions
- "The future looks bright," "Only time will tell," "One thing is certain," "As we move forward" — these are filler disguised as conclusions. Cut them. If the piece needs a closing thought, make it specific to the argument.

### Superficial -ing analyses
- Strings of present participles used as pseudo-analysis: "symbolizing the region's commitment to progress, reflecting decades of investment, and showcasing a new era of collaboration." These say nothing. Replace with specific facts or cut entirely.
- The same move shows up without the -ing: declarative "meaning-telling" that glosses a mundane subject as if it were profound — "this represents a broader shift," "the decision symbolizes a commitment to excellence," "it speaks to a larger trend in the industry." If the significance is real, show it with a specific consequence; otherwise cut. Adapted from `Aboudjem/humanizer-skill` P40.

### Promotional language
- AI defaults to tourism-brochure prose: "nestled within the breathtaking foothills," "a vibrant hub of innovation," "a thriving ecosystem." Replace with plain description: "is a town in the Gonder region," "has 12 startups." If you wouldn't say it in conversation, cut it.

### Formulaic challenges
- "Despite challenges, [subject] continues to thrive" or "While facing headwinds, the organization remains resilient." This is a non-statement. Name the actual challenge and the actual response, or cut the sentence.

### False ranges
- AI creates false breadth by pairing unrelated extremes: "from the Big Bang to dark matter," "from ancient civilizations to modern startups." These sound sweeping but say nothing. List the actual topics or pick the one that matters.

### Novelty inflation
- AI text treats established concepts as if the speaker invented or discovered them: "He introduced a term," "She coined the phrase," "a concept nobody's naming," "a failure mode nobody talks about." In reality, most ideas in a conversation are applications of existing concepts, not inventions.
- Two problems. First, it's factually risky: if the concept already has a Wikipedia page or conference talks from last year, claiming novelty makes the writer look uninformed. Second, it flatters the subject in a way that reads as promotional rather than analytical.
- The fix: describe what the person *did with* the concept, not that they discovered it. "Michel walked through how context poisoning works in practice" instead of "Michel introduced a term I hadn't heard before: context poisoning." If you're unsure whether something is novel, assume it isn't and frame accordingly.
- Related patterns to flag: "the failure mode nobody's naming," "a problem nobody talks about," "the insight everyone's missing," "what nobody tells you about." These are engagement-bait framings that claim scarcity of knowledge where none exists.
- Also flag invented labels: pseudo-analytical compound terms coined mid-sentence and never defined ("the supervision paradox," "the context-collapse problem," "a coordination tax"). Naming a concept is not explaining it. Define the term on first use or describe the mechanism instead of branding it. Source: tropes.fyi (Invented Labels).

### Invented contrast-pair mirroring
- An AI-specific form of forced symmetry: one half of a contrast pair is a legitimate term of art, and the other is the AI inventing its mirror to balance the sentence. "False precision rather than genuine accuracy" — "false precision" is a real statistical term; "genuine accuracy" is a phantom counterpart generated for parallelism. The asymmetry is invisible unless you know which half is real. The same pattern can produce pairs like "real data rather than theoretical models" (both real) or "practical results rather than abstract speculation" (both real), but the AI-specific tell is when one term is borrowed from the domain and the other is entirely fabricated.
- **Fix:** if you need a contrast, reach for an actual opposite. If no real opposite exists, drop the contrast structure and state the positive claim directly. "May create a misleadingly exact number rather than a more accurate one" — the contrast works because both halves are real descriptions.