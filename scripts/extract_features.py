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
        # count whole word occurrences
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
    # Count punctuation per sentence for common marks
    sentences = list(doc.sents)
    if not sentences:
        return {}
    total_sentences = len(sentences)
    punct_counts = Counter()
    for char in text:
        if char in ".,;:!?":
            punct_counts[char] += 1
    # per sentence
    return {char: count / total_sentences for char, count in punct_counts.items()}

def discourse_marker_positions(doc):
    # For each transition word, count occurrences and positions
    marker_info = {}
    for marker in TRANSITION_WORDS:
        sentence_initial = 0
        total = 0
        for sent in doc.sents:
            sent_text = sent.text.strip().lower()
            if sent_text.startswith(marker):
                sentence_initial += 1
            # count total occurrences in the whole text (approximate)
        # We'll compute total occurrences separately using text search
        # because using sentences for total is expensive; we'll just count sentence-initial for now
        # In summarize we may only need initial position info.
        if sentence_initial > 0:
            marker_info[marker] = {"sentence_initial": sentence_initial}
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

    # Deviations from baseline (overuse/underuse)
    deviations = {}
    for word, baseline in FUNCTION_WORDS.items():
        actual = function_freq.get(word, 0)
        if actual > 0 and baseline > 0:
            ratio = actual / baseline
            if ratio > 1.3 or ratio < 0.7:
                deviations[word] = {
                    "actual": actual,
                    "baseline": baseline,
                    "ratio": ratio
                }
    # Sort deviations by ratio (overuse first)
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
    # sentence_initial info
    marker_positions = {}
    for marker in TRANSITION_WORDS:
        initial_count = 0
        for sent in doc.sents:
            sent_text = sent.text.strip().lower()
            if sent_text.startswith(marker):
                initial_count += 1
        if initial_count > 0:
            marker_positions[marker] = initial_count

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

    # Paragraph stats (requires double newlines in text)
    paragraphs = [p for p in text.split('\n\n') if p.strip()]
    if len(paragraphs) > 1:
        para_lengths = [len(p.split()) for p in paragraphs]
        paragraph_stats = {
            "avg_words": statistics.mean(para_lengths),
            "median_words": statistics.median(para_lengths),
            "stdev_words": statistics.stdev(para_lengths) if len(para_lengths) > 1 else 0,
            "total_paragraphs": len(paragraphs)
        }
    else:
        paragraph_stats = None

    # Build feature dictionary
    features = {
        "basic_counts": {
            "total_words": total_words,
            "total_sentences": total_sentences,
            "total_paragraphs": len(paragraphs) if paragraphs else 0,
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
            "passive_voice_ratio": passive_ratio
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
            "sentence_initial_counts": marker_positions
        },
        "hedging": hedging_counts,
        "boosters": booster_counts,
        "contractions_per_100_words": contractions_per_100,
        "pronoun_usage": pron_usage,
        "sentence_starters": starters,
        "paragraph_stats": paragraph_stats
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