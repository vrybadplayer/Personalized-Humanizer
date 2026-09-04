### Transition phrases to remove or rewrite
- "Moreover" / "Furthermore" / "Additionally" → restructure so the connection is obvious, or use "and," "also," "on top of that"
- "In today's [X]" / "In an era where" → cut or state specific context
- "It's worth noting that" / "Notably" → just state the fact
- "Here's what's interesting" / "Here's what caught my eye" / "Here's what stood out" → reader-steering frames. Let the content signal its own importance. If you need a lead-in, make it specific: "The revenue number matters because..." not "Here's the interesting part."
- "In conclusion" / "In summary" / "To summarize" → your conclusion should be obvious
- "When it comes to" → just talk about the thing directly
- "At the end of the day" → cut
- "That said" / "That being said" → cut or use "but," "yet," or "however." Don't overuse any one of them.

### Rhetorical question openers
- "But what does this mean for developers?" / "So why should you care?" / "What's next?" — AI uses rhetorical questions to stall before the actual point. If you know the answer, just say it. Rhetorical questions are earned by strong setup, not dropped as section transitions.

### Parenthetical hedging
- "(and, increasingly, Z)" / "(or, more precisely, Y)" / "(and perhaps more importantly, W)" — AI inserts parenthetical asides to sound nuanced without committing. If the aside matters, give it its own sentence. If it doesn't, cut it.

### Confidence calibration phrases
- "It's worth noting that," "Interestingly," "Surprisingly," "Importantly," "Significantly," "Notably," "Certainly," "Undoubtedly," "Without a doubt" — AI uses these to signal how the reader should feel about a fact instead of letting the fact speak for itself.
- "Here's what's interesting," "Here's the interesting part," "Here are the parts I found interesting" — reader-steering cue that pre-interprets importance. Works when followed by genuinely surprising data; fails when it introduces a restatement of something obvious (which is the AI default).
- One "notably" in a 2,000-word piece is fine. Three in 500 words is AI-style emphasis stacking. Flag by density.
- Related — **persuasive-authority tropes**: "the real question is," "at its core," "fundamentally," "make no mistake," "the truth is." Same move as the calibration phrases above, but they assert depth or stakes instead of feeling: they announce that what follows is important rather than showing it. Cut the trope and lead with the substance. Adapted from `blader/humanizer` P27.

### Self-labeling significance
- After listing or describing several items, the writer points back at one and labels it as contrarian / clever / surprising / counterintuitive / key: "That last move is the contrarian one," "This is the interesting part," "That third bullet is the real story," "Here's where it gets clever," "The last bit is the counterintuitive one."
- The label does the work the content was supposed to do. If a move is genuinely contrarian, the reader recognizes it from the description; if it isn't recognizable without the label, the label is unearned. The pattern reads as the writer auditing their own list to flag which item should matter, instead of writing the list so the right item carries the weight on its own.
- Distinct from confidence calibration ("Notably," "Interestingly") which front-loads the cue, and from emotional flatline ("What surprised me most," "The most interesting part") which prefaces a single claim. This pattern back-points after the fact, usually as "[that / this / the Xth / the last] [noun] is the [adjective] one."
- Significance-adjectives that signal the pattern: contrarian, clever, surprising, counterintuitive, interesting, key, important, unusual, smart, brilliant, real, actual.
- Fix: cut the labeling sentence and let the explanation that follows do the work directly. Or restructure so the item you wanted to highlight is positioned first or expanded with specifics, making the label redundant.
- Example. Before: "→ Two separate indexes for tiered storage. That last move is the contrarian one. Co-locating related data usually helps cache locality." After: "→ Two separate indexes for tiered storage. Co-locating related data usually helps cache locality, but splitting the indexes is what makes the hot path cheap." The contrast carries itself; the label is gone.