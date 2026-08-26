import json
import re
import sys
import statistics
from pathlib import Path
from collections import Counter

sys.path.append(str(Path(__file__).resolve().parent.parent))

import spacy
import nltk
from nltk.util import ngrams
import textstat
from config.settings import CLEAN_DATA_DIR, PROFILE_DIR

nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    print("spaCy model 'en_core_web_md' not found. Install with: python -m spacy download en_core_web_md")
    sys.exit(1)

# Function words and baseline frequencies (approximate from COCA/BNC)
FUNCTION_WORDS = {
    "the": 0.06, "a": 0.02, "an": 0.01, "and": 0.03, "or": 0.01,
    "but": 0.01, "if": 0.01, "because": 0.01, "as": 0.015, "what": 0.005,
    "which": 0.005, "this": 0.015, "that": 0.03, "these": 0.005, "those": 0.005,
    "then": 0.005, "just": 0.005, "so": 0.01, "than": 0.01, "such": 0.01,
    "both": 0.005, "through": 0.005, "about": 0.01, "up": 0.005, "out": 0.01,
    "is": 0.02, "are": 0.015, "was": 0.015, "were": 0.01, "be": 0.015,
    "been": 0.01, "being": 0.005, "have": 0.015, "has": 0.01, "had": 0.01,
    "having": 0.005, "do": 0.01, "does": 0.005, "did": 0.01, "doing": 0.005,
    "will": 0.01, "would": 0.01, "shall": 0.001, "should": 0.005, "may": 0.005,
    "might": 0.005, "must": 0.005, "can": 0.015, "could": 0.01, "of": 0.04,
    "to": 0.025, "in": 0.025, "for": 0.015, "on": 0.015, "with": 0.015,
    "at": 0.01, "by": 0.01, "from": 0.01, "into": 0.005, "over": 0.005,
    "under": 0.005, "again": 0.005, "further": 0.005, "once": 0.005,
    "here": 0.005, "there": 0.01, "when": 0.005, "where": 0.005,
    "why": 0.005, "how": 0.005, "all": 0.01, "any": 0.01, "each": 0.01,
    "few": 0.005, "more": 0.015, "most": 0.01, "other": 0.01, "some": 0.01,
    "no": 0.01, "nor": 0.001, "not": 0.02, "only": 0.01, "own": 0.005,
    "same": 0.005, "s": 0.005, "t": 0.005, "don": 0.001
}

TRANSITION_WORDS = [
    "however", "therefore", "moreover", "furthermore", "thus", "hence",
    "accordingly", "consequently", "meanwhile", "nevertheless", "nonetheless",
    "otherwise", "similarly", "likewise", "additionally", "besides", "finally",
    "in addition", "for example", "for instance", "in conclusion", "as a result",
    "on the other hand", "in contrast", "in comparison", "in fact", "indeed",
    "instead", "subsequently", "previously", "currently", "ultimately"
]

HEDGING_WORDS = [
    "perhaps", "maybe", "might", "may", "could", "can", "seems", "appears",
    "likely", "probably", "often", "sometimes", "generally", "tends", "suggests",
    "indicates", "typically", "usually", "somewhat", "relatively"
]

BOOSTER_WORDS = [
    "clearly", "obviously", "certainly", "definitely", "undoubtedly", "indeed",
    "of course", "in fact", "actually", "really", "very", "extremely", "highly"
]

CONTRACTIONS = [
    "don't", "do not", "can't", "cannot", "won't", "will not", "shouldn't",
    "should not", "it's", "it is", "isn't", "is not", "aren't", "are not",
    "wasn't", "was not", "weren't", "were not", "hasn't", "has not", "haven't",
    "have not", "hadn't", "had not", "doesn't", "does not", "didn't", "did not",
    "wouldn't", "would not", "couldn't", "could not", "mightn't", "might not",
    "mustn't", "must not", "i'm", "i am", "you're", "you are", "he's", "he is",
    "she's", "she is", "we're", "we are", "they're", "they are", "i've", "i have",
    "you've", "you have", "we've", "we have", "they've", "they have", "i'll",
    "i will", "you'll", "you will", "he'll", "he will", "she'll", "she will",
    "we'll", "we will", "they'll", "they will", "i'd", "i would", "you'd",
    "you would", "he'd", "he would", "she'd", "she would", "we'd", "we would",
    "they'd", "they would"
]

def clean_token(token):
    return not token.is_space and not token.is_punct and token.is_alpha

def get_sentence_lengths(doc):
    return [sum(1 for token in sent if clean_token(token)) for sent in doc.sents]

def compute_ttr(tokens):
    if len(tokens) == 0:
        return 0.0
    return len(set(tokens)) / len(tokens)

def compute_mattr(tokens, window=100):
    if len(tokens) < window:
        return compute_ttr(tokens)
    ttrs = []
    for i in range(0, len(tokens) - window + 1, window):
        window_tokens = tokens[i:i+window]
        ttrs.append(compute_ttr(window_tokens))
    return sum(ttrs) / len(ttrs)

def compute_hapax_ratio(tokens):
    if len(tokens) == 0:
        return 0.0
    freq = Counter(tokens)
    return sum(1 for c in freq.values() if c == 1) / len(tokens)

def detect_passive_voice(doc):
    passive_count = 0
    total_sentences = 0
    for sent in doc.sents:
        total_sentences += 1
        for token in sent:
            if token.dep_ == 'auxpass':
                passive_count += 1
                break
    return passive_count / total_sentences if total_sentences else 0.0

def count_contractions(text):
    text_lower = text.lower()
    count = 0
    for c in CONTRACTIONS:
        count += len(re.findall(r'\b' + re.escape(c) + r'\b', text_lower))
    return count

def pronoun_usage(doc, total_words):
    pronouns = {
        "first_person": ["i", "me", "my", "mine", "we", "us", "our", "ours"],
        "second_person": ["you", "your", "yours"],
        "third_person": ["he", "she", "it", "they", "him", "her", "them",
                         "his", "hers", "its", "their", "theirs"]
    }
    counts = {k: 0 for k in pronouns}
    for token in doc:
        if clean_token(token):
            low = token.text.lower()
            for person, words in pronouns.items():
                if low in words:
                    counts[person] += 1
    return {k: v / total_words if total_words else 0 for k, v in counts.items()}

def sentence_starters(doc, top_n=10):
    starters = []
    for sent in doc.sents:
        for token in sent:
            if clean_token(token):
                starters.append(token.text.lower())
                break
    if not starters:
        return []
    freq = Counter(starters)
    return freq.most_common(top_n)

def punctuation_per_sentence(doc, text):
    sentences = list(doc.sents)
    if not sentences:
        return {}
    total_sentences = len(sentences)
    punct_counts = Counter()
    for char in text:
        if char in ".,;:!?":
            punct_counts[char] += 1
    return {char: count / total_sentences for char, count in punct_counts.items()}

def classify_sentence_type(sent):
    """Classify sentence based on clause structure (approximate)."""
    finite_verbs = sum(
        1 for tok in sent
        if tok.pos_ in ("VERB", "AUX") and tok.morph.get("VerbForm") == ["Fin"]
    )
    # Count coordinating conjunctions that join independent clauses (simplified)
    coordinators = sum(1 for tok in sent if tok.dep_ == "cc")
    # Count subordinating conjunctions or relative pronouns
    subordinators = sum(
        1 for tok in sent
        if tok.dep_ == "mark" or (tok.dep_ == "relcl" and tok.pos_ == "PRON")
    )

    if finite_verbs <= 1:
        return "simple"
    elif coordinators > 0 and subordinators > 0:
        return "compound-complex"
    elif coordinators > 0:
        return "compound"
    elif subordinators > 0:
        return "complex"
    else:
        # More than one finite verb but no clear marker; treat as complex
        return "complex"

def sentence_type_distribution(doc):
    types = Counter()
    for sent in doc.sents:
        stype = classify_sentence_type(sent)
        types[stype] += 1
    total = sum(types.values())
    if total == 0:
        return {}
    return {k: v / total for k, v in types.items()}

def clause_complexity(doc):
    """Return average clauses per sentence and subordinate clause ratio."""
    total_sentences = 0
    total_clauses = 0
    total_subordinate = 0
    sentences_with_subordinate = 0

    for sent in doc.sents:
        total_sentences += 1
        # Count finite verbs as approximation of clauses
        finite_verbs = sum(
            1 for tok in sent
            if tok.pos_ in ("VERB", "AUX") and tok.morph.get("VerbForm") == ["Fin"]
        )
        total_clauses += finite_verbs

        # Count subordinating conjunctions and relative pronouns introducing subordinate clauses
        subord = sum(
            1 for tok in sent
            if tok.dep_ == "mark" or (tok.dep_ == "relcl" and tok.pos_ == "PRON")
        )
        total_subordinate += subord
        if subord > 0:
            sentences_with_subordinate += 1

    avg_clauses = total_clauses / total_sentences if total_sentences else 0
    subord_ratio = total_subordinate / total_clauses if total_clauses else 0
    subord_sentence_ratio = sentences_with_subordinate / total_sentences if total_sentences else 0

    return {
        "avg_clauses_per_sentence": avg_clauses,
        "subordinate_clause_ratio": subord_ratio,          # now between 0 and 1
        "sentences_with_subordinate_ratio": subord_sentence_ratio
    }

def paragraph_stats(text):
    paragraphs = [p for p in text.split('\n\n') if p.strip()]
    if len(paragraphs) < 2:
        return None
    lengths = [len(p.split()) for p in paragraphs]
    if len(lengths) < 4:  # need at least 4 for percentiles
        percentiles = [0, 0, 0]
    else:
        percentiles = statistics.quantiles(lengths, n=4)
    return {
        "avg_words": statistics.mean(lengths),
        "median_words": statistics.median(lengths),
        "stdev_words": statistics.stdev(lengths) if len(lengths) > 1 else 0,
        "percentiles": percentiles,
        "total_paragraphs": len(paragraphs)
    }

def discourse_marker_positions(doc):
    """For each transition word, compute total occurrences and sentence-initial count."""
    marker_info = {}
    text_lower = " ".join(sent.text.strip().lower() for sent in doc.sents)
    for marker in TRANSITION_WORDS:
        total_count = text_lower.count(marker)
        if total_count == 0:
            continue
        initial_count = 0
        for sent in doc.sents:
            if sent.text.strip().lower().startswith(marker):
                initial_count += 1
        marker_info[marker] = {
            "total_count": total_count,
            "sentence_initial_count": initial_count,
            "initial_percentage": initial_count / total_count if total_count else 0
        }
    return marker_info

def extract_features(text):
    doc = nlp(text)
    tokens = [token.text.lower() for token in doc if clean_token(token)]
    total_words = len(tokens)
    sentences = list(doc.sents)
    total_sentences = len(sentences)

    # Basic counts
    sentence_lengths = get_sentence_lengths(doc)
    avg_sentence_length = statistics.mean(sentence_lengths) if sentence_lengths else 0
    median_sentence_length = statistics.median(sentence_lengths) if sentence_lengths else 0
    stdev_sentence_length = statistics.stdev(sentence_lengths) if len(sentence_lengths) > 1 else 0
    percentiles = statistics.quantiles(sentence_lengths, n=4) if sentence_lengths else [0,0,0]

    # Lexical diversity
    ttr = compute_ttr(tokens)
    mattr = compute_mattr(tokens)
    hapax_ratio = compute_hapax_ratio(tokens)

    # Content words and phrases (domain-specific)
    stopwords = nlp.Defaults.stop_words
    content_words = [tok for tok in tokens if tok not in stopwords]
    word_freq = Counter(content_words)
    top_content_words = word_freq.most_common(20)

    phrase_counter = Counter()
    for n in range(2, 6):
        for gram in ngrams(tokens, n):
            phrase_counter[" ".join(gram)] += 1
    top_phrases = [phrase for phrase, count in phrase_counter.most_common(20) if count > 1]

    # Function word frequencies and deviations
    function_freq = {}
    for fw in FUNCTION_WORDS:
        count = tokens.count(fw)
        if count > 0:
            function_freq[fw] = count / total_words

    deviations = {}
    for word, baseline in FUNCTION_WORDS.items():
        actual = function_freq.get(word, 0)
        if actual > 0 and baseline > 0:
            ratio = actual / baseline
            if ratio > 1.3 or ratio < 0.7:
                deviations[word] = {"actual": actual, "baseline": baseline, "ratio": ratio}
    overused = {k: v for k, v in deviations.items() if v["ratio"] > 1}
    underused = {k: v for k, v in deviations.items() if v["ratio"] < 1}
    overused_sorted = sorted(overused.items(), key=lambda x: x[1]["ratio"], reverse=True)[:5]
    underused_sorted = sorted(underused.items(), key=lambda x: x[1]["ratio"])[:5]

    # POS distribution
    pos_counts = Counter()
    for token in doc:
        if clean_token(token):
            pos_counts[token.pos_] += 1
    pos_distribution = {pos: count / total_words for pos, count in pos_counts.items()}

    # Syntactic complexity
    verbs_per_sentence = []
    for sent in doc.sents:
        verb_count = sum(1 for token in sent if token.pos_ == "VERB")
        verbs_per_sentence.append(verb_count)
    avg_verbs_per_sentence = statistics.mean(verbs_per_sentence) if verbs_per_sentence else 0
    passive_ratio = detect_passive_voice(doc)

    # New: sentence type distribution
    sent_type_dist = sentence_type_distribution(doc)

    # New: clause complexity
    clause_info = clause_complexity(doc)

    # Punctuation (per 100 words and per sentence)
    punct_counts = Counter()
    for char in text:
        if char in ".,;:!?":
            punct_counts[char] += 1
    punct_per_100 = {p: (count / total_words * 100) if total_words else 0 for p, count in punct_counts.items()}
    punct_per_sentence = punctuation_per_sentence(doc, text)

    # Readability
    flesch_reading_ease = textstat.flesch_reading_ease(text)
    flesch_kincaid_grade = textstat.flesch_kincaid_grade(text)
    gunning_fog = textstat.gunning_fog(text)

    # Transition words: frequency and sentence-initial positions
    transition_freq = {}
    for tw in TRANSITION_WORDS:
        count = text.lower().count(tw)
        if count > 0:
            transition_freq[tw] = count / total_words
    # New: discourse marker positions (total, initial, percentage)
    marker_positions = discourse_marker_positions(doc)

    # Hedging and boosters
    hedging_counts = {}
    for h in HEDGING_WORDS:
        c = len(re.findall(r'\b' + re.escape(h) + r'\b', text.lower()))
        if c > 0:
            hedging_counts[h] = c / total_words
    booster_counts = {}
    for b in BOOSTER_WORDS:
        c = len(re.findall(r'\b' + re.escape(b) + r'\b', text.lower()))
        if c > 0:
            booster_counts[b] = c / total_words

    # Contractions
    contractions_count = count_contractions(text)
    contractions_per_100 = (contractions_count / total_words * 100) if total_words else 0

    # Pronoun usage
    pron_usage = pronoun_usage(doc, total_words)

    # Sentence starters
    starters = sentence_starters(doc, top_n=10)

    # New: paragraph stats with percentiles
    para_stats = paragraph_stats(text)

    # Build feature dictionary
    features = {
        "basic_counts": {
            "total_words": total_words,
            "total_sentences": total_sentences,
            "total_paragraphs": para_stats["total_paragraphs"] if para_stats else 0,
            "avg_sentence_length": avg_sentence_length,
            "median_sentence_length": median_sentence_length,
            "stdev_sentence_length": stdev_sentence_length,
            "sentence_length_percentiles": percentiles
        },
        "lexical_diversity": {
            "ttr": ttr,
            "mattr": mattr,
            "hapax_legomena_ratio": hapax_ratio
        },
        "domain_specific": {
            "top_content_words": top_content_words,
            "favorite_phrases": top_phrases
        },
        "function_words": {
            "frequencies": function_freq,
            "overused": overused_sorted,
            "underused": underused_sorted
        },
        "pos_distribution": pos_distribution,
        "syntactic_complexity": {
            "avg_verbs_per_sentence": avg_verbs_per_sentence,
            "passive_voice_ratio": passive_ratio,
            "sentence_type_distribution": sent_type_dist,
            "clause_complexity": clause_info
        },
        "punctuation": {
            "per_100_words": punct_per_100,
            "per_sentence": punct_per_sentence
        },
        "readability": {
            "flesch_reading_ease": flesch_reading_ease,
            "flesch_kincaid_grade": flesch_kincaid_grade,
            "gunning_fog": gunning_fog
        },
        "transitions": {
            "frequencies": transition_freq,
            "marker_positions": marker_positions
        },
        "hedging": hedging_counts,
        "boosters": booster_counts,
        "contractions_per_100_words": contractions_per_100,
        "pronoun_usage": pron_usage,
        "sentence_starters": starters,
        "paragraph_stats": para_stats
    }
    return features

def main():
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    clean_files = list(CLEAN_DATA_DIR.glob("*.txt"))
    if not clean_files:
        print(f"No clean text files found in {CLEAN_DATA_DIR}. Run ingestion first.")
        sys.exit(1)

    print(f"Found {len(clean_files)} cleaned files.")
    all_text = ""
    for file_path in clean_files:
        text = file_path.read_text(encoding="utf-8")
        all_text += text + "\n\n"

    print("Extracting features...")
    features = extract_features(all_text)

    output_file = PROFILE_DIR / "style_profile.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(features, f, indent=2, ensure_ascii=False)

    print(f"Style profile saved to {output_file}")

if __name__ == "__main__":
    main()