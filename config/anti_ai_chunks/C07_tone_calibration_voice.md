## Voice profiles
Context profiles (above) set *how strict* to be for an audience. Voice profiles set *how the prose should sound* — the persona. They're independent axes: you can write blunt for a blog or warm for docs. Voice is **optional** — if the writer doesn't name one, infer it from the input's existing register and don't impose a persona on text that already has one.

Every target below is bounded by the Never-inject guardrails: a voice profile can bring out what the source already has, never manufacture what it doesn't.

Each profile is a set of concrete targets, not a vibe:

**`casual`** — Contractions throughout; their absence reads stiff. Short sentences (aim for ≤14 words on average); fragments allowed. Keep first-person and concrete touches where the source has them; never add one it lacks. Near-zero jargon. Keep warm hedges ("honestly," "I think") but cut corporate ones ("it's worth noting"). *Blog posts, social, community.*

**`professional`** — Active voice for most sentences. Vary sentence length; avoid three in a row within a few words of each other. Prefer a concrete claim per paragraph (a number, a name, a date) when the source provides one; never "experts say." Keep the ask explicit where the source makes one; never invent facts or an ask. Low tolerance for hedging. *LinkedIn, investor email, sponsor pitches.*

**`technical`** — Prefer plain copulatives ("X is Y") over inflated substitutes ("serves as," "stands as a testament to"). One idea per sentence; imperative mood for instructions. Jargon is fine, but define it on first use. Tables and lists only where the content is genuinely list-shaped, not for decoration. *Docs, technical blog.*

**`warm`** — Address the reader directly where the source already speaks to them ("you"), and keep its acknowledgment rather than adding one. Cut intensifiers ("very," "truly," "incredibly") in favor of stronger verbs. No performative-empathy openers ("I completely understand how you feel"). Medium sentences (15–20 words) for an unhurried cadence. *Mentorship, onboarding, thank-yous.*

**`blunt`** — Lead with the claim; cut "It's important to note that" windups. Em-dashes are rare here; use periods for emphasis. No padding to hit a rule of three. Near-zero hedging; flag "may / could / potentially" stacks. Short declaratives, with the occasional long sentence for contrast. *Decision memos, thought leadership, hard feedback.*

**Calibrate to a sample (optional).** If the writer gives you a sample of their own writing ("match my voice — here's a post"), analyze its sentence-length pattern, contraction rate, paragraph openings, and recurring word choices, then match those instead of a named profile. Don't "upgrade" their vocabulary: if they write "stuff" and "things," keep that register.

**How voice composes with context.** Voice sets the target; context sets how hard to enforce it. A voice *target* always applies, even where a context profile would skip that category — `technical` voice still prefers plain copulatives in a `casual` context that otherwise ignores copula avoidance. Where both axes govern the same rule and agree, they reinforce: `blunt` voice wants near-zero em-dashes and a `blog` context is already strict on them, so it stays a hard edit. Where they disagree, resolve toward the **stricter** of the two — a `warm` voice on `docs` still doesn't get decorative tables. Sensible default pairings: casual↔casual, professional↔linkedin/investor-email, technical↔docs/technical-blog.

---

## Tone calibration
The goal is writing that sounds like a person wrote it. Direct. Specific. The writing should demonstrate confidence, not assert it.

Five principles for human-sounding rewrites:
1. **Vary sentence length** — mix short with long. Fragments are fine.
2. **Be concrete** — replace vague claims with numbers, names, dates, or examples.
3. **Have a voice** — where appropriate, use first person, state preferences, show reactions.
4. **Cut the neutrality** — humans have opinions. If the piece is supposed to take a position, take it.
5. **Earn your emphasis** — don't tell the reader something is interesting. Make it interesting.

Removal is half the job. A rewrite that clears every flag but reads sterile — even sentence lengths, no stance, no first person where one belongs — is still recognizably machine output. When the genre carries a voice (essays, posts, personal writing), put voice back on purpose: a reaction, a stated preference, an aside, one thought left unresolved. For encyclopedic, technical, or legal text, neutral and plain is the correct human voice; don't inject personality there. Adapted from `blader/humanizer` ("Personality and soul").

If the original writing is already strong, say so and make only the necessary cuts. Don't over-edit for the sake of it.

The replacement table provides defaults, not mandates. If a flagged word is clearly the right choice in context, preserve it.

### Never inject these
The instruction above — put voice back on purpose — has a predictable failure mode: the model reaches for a stock kit of "human" moves and installs a personality the author never had. That trades one detectable register for a louder one. An independent stress test of `blader/humanizer` found exactly this: generic AI phrasing replaced by a recognizable *humanizer* voice of fragments and staccato rhythm. A new fingerprint, not the absence of one.

None of the following may be **added** to a text that did not already contain it. Every one is a rewrite failure even when the result scores clean:

- **Fake first person.** "I've seen this a hundred times," "in my experience," "I'll admit" dropped into prose that had no author presence. Voice comes from the author or not at all. If the source has no `I`, the rewrite has no `I`.
- **Manufactured stakes.** "In a world where," "now more than ever," "the stakes have never been higher." Covered as a detection rule under Speculative scenario openers; listed again here because the rewrite side is where it gets *introduced*.
- **Forced contrarianism.** "Everyone says X, but they're wrong," "the conventional wisdom is backwards." Only legitimate when the source actually argued it. Inventing a foil is inventing a claim.
- **Performed candor.** "Let's be honest," "real talk," "here's the thing." See Narrated candor and Infomercial engagement hooks. A rewrite that adds one is failing two rules at once.
- **Em-dash theatrics.** Dashes staged for drama the content has not earned. The rule elsewhere is a rate ceiling; this is about *adding* dashes during a rewrite, which should never happen.
- **Staccato conversion.** Chopping ordinary sentences into fragments to manufacture rhythm. Vary sentence length by varying the sentences, not by breaking them.
- **Invented specifics.** A number, name, date, tool, or mechanism the source never contained. Specificity is the most tempting fix because it always reads better, and a fabricated specific is worse than the vague phrasing it replaced. If the concrete detail is missing, flag the gap and leave it. Never fill it.

**The test.** For each edit, ask whether the information in the rewrite came from the source. Subtraction and sharpening are in scope: cutting filler, making an existing claim concrete, surfacing a buried point. Addition of stance, personality, or fact is not. Adapted from `isatimur/de-slop`'s guardrails, which state the rule plainly: you may subtract and sharpen, you may not add.

**Why it belongs here rather than in the pattern catalog.** These are constraints on the editor, not detections on the text. A first-person aside is not a flag when the author wrote it; it is a failure when the tool inserted it. The difference is provenance, which no pattern can see, so it lives with the rewrite instructions where the decision is actually made.