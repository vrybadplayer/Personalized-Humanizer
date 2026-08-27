# Personalized Humanizer – Style Guide (Template)

This guide was generated from stylometric analysis of the writer's documents. It contains precise metrics and instructions for mimicking the writer's style.

## Narrative Overview

<!-- Optional: The LLM-generated prose description will be inserted here by merge_guides.py -->

## Sentence Structure

- Average sentence length: **{{basic_counts.avg_sentence_length}}** words (median **{{basic_counts.median_sentence_length}}**, std **{{basic_counts.stdev_sentence_length}}**).
- Sentence length percentiles: 25th = **{{basic_counts.sentence_length_percentiles[0]}}**, 50th = **{{basic_counts.sentence_length_percentiles[1]}}**, 75th = **{{basic_counts.sentence_length_percentiles[2]}}**.
- Sentence type distribution: simple **{{syntactic_complexity.sentence_type_distribution.simple}}**, compound **{{syntactic_complexity.sentence_type_distribution.compound}}**, complex **{{syntactic_complexity.sentence_type_distribution.complex}}**, compound-complex **{{syntactic_complexity.sentence_type_distribution.compound-complex}}**.
- Average clauses per sentence: **{{syntactic_complexity.clause_complexity.avg_clauses_per_sentence}}**.
- Subordinate clause ratio: **{{syntactic_complexity.clause_complexity.subordinate_clause_ratio}}**.
- Passive voice ratio: **{{syntactic_complexity.passive_voice_ratio}}** (i.e., about **{{syntactic_complexity.passive_voice_ratio_percent}}**% of sentences).

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

## Anti-AI Writing Rules

<!-- The static anti-AI block will be appended here by merge_guides.py -->