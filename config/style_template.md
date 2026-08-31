**Important:** The metrics below are guidelines, not strict rules. To sound human, vary sentence structure, punctuation, and paragraph length within a ±5–10% range of these values.

# Personalized Humanizer – Style Guide (Template)

This guide was generated from stylometric analysis of the writer's documents. It contains precise metrics and instructions for mimicking the writer's style.

## Narrative Overview

<!-- Optional: The LLM-generated prose description will be inserted here by merge_guides.py -->

## Critical Anti‑AI Writing Rules (Always Follow)

- **Vary sentence length**: mix short (3–8 words) and long (20+ words) sentences. Avoid three consecutive sentences of similar length.
- **Avoid em dashes** (—). Use commas, periods, or parentheses. Maximum one em dash per 1000 words.
- **Do not bold text for emphasis** in prose; restructure to lead with the key point.
- **Replace these AI‑favored words**:
  - "delve" → "explore", "dig into"
  - "leverage" → "use"
  - "robust" → "strong"
  - "seamless" → "smooth"
  - "utilize" → "use"
  - "in order to" → "to"
  - "showcasing" → "showing"
  - "comprehensive" → "thorough"
- **Avoid hollow intensifiers**: "genuinely", "truly", "actually" (unless correcting a fact), "very", "highly".
- **Cut filler**: "It's worth noting that", "In terms of", "The reality is that", "It is important to note".
- **Do not use "Let's" as a transition**; start with the subject.
- **Avoid vague attributions** ("Experts believe", "Studies show") – name the source or state the claim directly.
- **Limit transition words**: "Moreover", "Furthermore", "Additionally" → use "and", "also", or restructure.
- **Avoid "In conclusion", "To summarize"** – let the conclusion be obvious.
- **Do not use rhetorical questions as openers**.
- **Avoid "The catch?", "Here's the thing"** – just state the point.
- **No invented facts, numbers, or sources**.
- **Avoid significance inflation** ("watershed moment", "pivotal").
- **No generic future‑narrative closers** ("may become one of the most important...").
- **Do not add fake first‑person or manufactured stakes**.
- **Preserve the writer's passive voice ratio (~24%)** but use active voice when the actor matters.
- **Use full forms (avoid contractions)** unless the original style uses them.

## Sentence Structure

- Sentence length: aim for an average around **{{basic_counts.avg_sentence_length}}** words, but vary widely between **{{basic_counts.sentence_length_percentiles[0]}}** and **{{basic_counts.sentence_length_percentiles[2]}}**. Include some very short (3–5 words) and some long (25–40 words) sentences.
- Sentence type distribution: the writer uses a mix of simple, compound, complex, and compound-complex sentences. Do not stick to one type; vary them naturally.
- Average clauses per sentence: **{{syntactic_complexity.clause_complexity.avg_clauses_per_sentence}}**.
- Subordinate clause ratio: **{{syntactic_complexity.clause_complexity.subordinate_clause_ratio}}**.
- Passive voice: the writer uses passive voice in about **{{syntactic_complexity.passive_voice_ratio}}** of sentences. Treat this as a soft target, not a strict rule; vary between roughly 15–35% to avoid monotony.

## Vocabulary & Phrasing

- Type-token ratio (TTR): **{{lexical_diversity.ttr}}**.
- Moving Average TTR (MATTR): **{{lexical_diversity.mattr}}**.
- Hapax legomena ratio: **{{lexical_diversity.hapax_legomena_ratio}}**.
- Top content words (domain-specific, avoid overusing): {{domain_specific.top_content_words}}.
- Favorite phrases (use sparingly, if appropriate): {{domain_specific.favorite_phrases}}.
- Function word overuse: {{function_words.overused}}.
- Function word underuse: {{function_words.underused}}.

## Parts of Speech (Proportional)

- Nouns: **{{pos_distribution.NOUN}}**
- Verbs: **{{pos_distribution.VERB}}**
- Adjectives: **{{pos_distribution.ADJ}}**
- Adverbs: **{{pos_distribution.ADV}}**
- Pronouns: **{{pos_distribution.PRON}}**
- Determiners: **{{pos_distribution.DET}}**
- Prepositions: **{{pos_distribution.ADP}}**
- Conjunctions: **{{pos_distribution.CCONJ}}** (coordinating)

## Punctuation (per 100 words)

- Commas: **{{punctuation.per_100_words.,}}**
- Periods: **{{punctuation.per_100_words..}}**
- Semicolons: **{{punctuation.per_100_words.;}}**
- Colons: **{{punctuation.per_100_words.:}}**
- Question marks: **{{punctuation.per_100_words.?}}**
- Exclamation marks: **{{punctuation.per_100_words.!}}**

## Punctuation (per sentence)

- Commas: **{{punctuation.per_sentence.,}}**
- Periods: **{{punctuation.per_sentence..}}**
- Semicolons: **{{punctuation.per_sentence.;}}**
- Colons: **{{punctuation.per_sentence.:}}**

## Readability

- Flesch Reading Ease: **{{readability.flesch_reading_ease}}** (difficult)
- Flesch-Kincaid Grade: **{{readability.flesch_kincaid_grade}}** (college level)
- Gunning Fog Index: **{{readability.gunning_fog}}**

## Transitions & Discourse Markers

- Frequent transitions: {{transitions.frequencies}}
- Sentence-initial usage: {{transitions.marker_positions}}

## Hedging & Boosters

- Hedging words (qualifiers): {{hedging}}
- Boosters (emphasis): {{boosters}}
- Contractions per 100 words: **{{contractions_per_100_words}}** (very rare: prefer full forms)

## Pronoun Usage

- First person: **{{pronoun_usage.first_person}}**
- Second person: **{{pronoun_usage.second_person}}**
- Third person: **{{pronoun_usage.third_person}}**

## Sentence Starters (top 5)

{{sentence_starters}}

## Paragraph Stats

- Average paragraph length: **{{paragraph_stats.avg_words}}** words
- Median paragraph length: **{{paragraph_stats.median_words}}** words
- Std dev: **{{paragraph_stats.stdev_words}}**
- Percentiles: 25th = **{{paragraph_stats.percentiles[0]}}**, 50th = **{{paragraph_stats.percentiles[1]}}**, 75th = **{{paragraph_stats.percentiles[2]}}**

## Anti-AI Writing Rules (Full)

<!-- The full anti-AI chunk content will be appended here by merge_guides.py -->