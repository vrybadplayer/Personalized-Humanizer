import json
import re
from pathlib import Path
from collections import Counter, defaultdict
import statistics
import sys

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import spacy
import nltk
from nltk.util import ngrams
from nltk.tokenize import word_tokenize
import textstat

from config.settings import CLEAN_DATA_DIR, PROFILE_DIR

# Ensure NLTK data is available
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    print("spaCy model 'en_core_web_md' not found. Install with: python -m spacy download en_core_web_md")
    sys.exit(1)

# List of common function words (determiners, prepositions, conjunctions, pronouns, auxiliary verbs)
FUNCTION_WORDS = {
    "the", "a", "an", "and", "or", "but", "if", "because", "as", "what",
    "which", "this", "that", "these", "those", "then", "just", "so", "than",
    "such", "both", "through", "about", "up", "out", "if", "is", "are", "was",
    "were", "be", "been", "being", "have", "has", "had", "having", "do", "does",
    "did", "doing", "will", "would", "shall", "should", "may", "might", "must",
    "can", "could", "of", "to", "in", "for", "on", "with", "at", "by", "from",
    "as", "into", "over", "under", "again", "further", "then", "once", "here",
    "there", "when", "where", "why", "how", "all", "any", "each", "few", "more",
    "most", "other", "some", "no", "nor", "not", "only", "own", "same", "s",
    "t", "can", "will", "don", "should", "now"
}

# List of common transition words
TRANSITION_WORDS = [
    "however", "therefore", "moreover", "furthermore", "thus", "hence",
    "accordingly", "consequently", "meanwhile", "nevertheless", "nonetheless",
    "otherwise", "similarly", "likewise", "additionally", "besides", "finally",
    "in addition", "for example", "for instance", "in conclusion", "as a result",
    "on the other hand", "in contrast", "in comparison", "in fact", "indeed",
    "instead", "subsequently", "previously", "currently", "ultimately"
]

def clean_token(token):
    """Check if a spaCy token should be considered a word."""
    return not token.is_space and not token.is_punct and token.is_alpha

def get_sentence_lengths(doc):
    """Return list of word counts per sentence."""
    return [sum(1 for token in sent if clean_token(token)) for sent in doc.sents]

def compute_ttr(tokens):
    """Type-token ratio."""
    if len(tokens) == 0:
        return 0.0
    return len(set(tokens)) / len(tokens)

def compute_mattr(tokens, window=100):
    """Moving Average Type-Token Ratio."""
    if len(tokens) < window:
        return compute_ttr(tokens)
    ttrs = []
    for i in range(0, len(tokens) - window + 1, window):
        window_tokens = tokens[i:i+window]
        ttrs.append(compute_ttr(window_tokens))
    return sum(ttrs) / len(ttrs)

def compute_hapax_legomena_ratio(tokens):
    """Ratio of words that appear exactly once."""
    if len(tokens) == 0:
        return 0.0
    freq = Counter(tokens)
    hapax = sum(1 for count in freq.values() if count == 1)
    return hapax / len(tokens)

def detect_passive_voice(doc):
    """Count passive voice occurrences using dependency parsing."""
    passive_count = 0
    total_sentences = 0
    for sent in doc.sents:
        total_sentences += 1
        for token in sent:
            # Passive auxiliary: token.dep_ == 'auxpass'
            if token.dep_ == 'auxpass':
                passive_count += 1
                break
    if total_sentences == 0:
        return 0.0
    return passive_count / total_sentences

def extract_features(text):
    """Extract stylometric features from a single text string."""
    doc = nlp(text)
    tokens = [token.text.lower() for token in doc if clean_token(token)]

    # Basic counts
    total_words = len(tokens)
    sentences = list(doc.sents)
    total_sentences = len(sentences)
    paragraphs = [p for p in text.split('\n\n') if p.strip()]
    total_paragraphs = len(paragraphs)

    sentence_lengths = get_sentence_lengths(doc)
    avg_sentence_length = statistics.mean(sentence_lengths) if sentence_lengths else 0
    median_sentence_length = statistics.median(sentence_lengths) if sentence_lengths else 0
    stdev_sentence_length = statistics.stdev(sentence_lengths) if len(sentence_lengths) > 1 else 0

    # Lexical diversity
    ttr = compute_ttr(tokens)
    mattr = compute_mattr(tokens)
    hapax_ratio = compute_hapax_legomena_ratio(tokens)

    # Word frequencies (excluding stopwords)
    stopwords = nlp.Defaults.stop_words
    content_words = [tok for tok in tokens if tok not in stopwords]
    word_freq = Counter(content_words)
    top_content_words = word_freq.most_common(20)

    # Favorite phrases (2-5 word ngrams)
    phrase_counter = Counter()
    for n in range(2, 6):
        for gram in ngrams(tokens, n):
            # Exclude ngrams with stopwords only? Keep all for now
            phrase_counter[" ".join(gram)] += 1
    top_phrases = [phrase for phrase, count in phrase_counter.most_common(20) if count > 1]

    # Function word frequencies
    function_freq = {}
    total_tokens = len(tokens)
    for fw in FUNCTION_WORDS:
        count = tokens.count(fw)
        if count > 0:
            function_freq[fw] = count / total_tokens

    # POS distribution (using universal POS tags)
    pos_counts = Counter()
    for token in doc:
        if clean_token(token):
            pos_counts[token.pos_] += 1
    pos_distribution = {pos: count / total_tokens for pos, count in pos_counts.items()}

    # Syntactic complexity: average number of clauses per sentence (approximated by number of verbs)
    verbs_per_sentence = []
    for sent in doc.sents:
        verb_count = sum(1 for token in sent if token.pos_ == "VERB")
        verbs_per_sentence.append(verb_count)
    avg_verbs_per_sentence = statistics.mean(verbs_per_sentence) if verbs_per_sentence else 0

    passive_ratio = detect_passive_voice(doc)

    # Punctuation usage
    punct_counts = Counter()
    for char in text:
        if char in ".,;:!?—-" :
            punct_counts[char] += 1
    # Normalise per 100 words
    punct_per_100 = {p: (count / total_words * 100) if total_words > 0 else 0 for p, count in punct_counts.items()}

    # Readability
    flesch_reading_ease = textstat.flesch_reading_ease(text)
    flesch_kincaid_grade = textstat.flesch_kincaid_grade(text)
    gunning_fog = textstat.gunning_fog(text)

    # Transition words
    transition_freq = {}
    for tw in TRANSITION_WORDS:
        # Count occurrences of phrase or word in lowercase text
        count = text.lower().count(tw)
        if count > 0:
            transition_freq[tw] = count / total_tokens

    # Character n-grams (top 50 trigrams)
    char_ngrams = Counter()
    clean_text = re.sub(r'\s+', ' ', text.lower())
    for i in range(len(clean_text) - 2):
        gram = clean_text[i:i+3]
        char_ngrams[gram] += 1
    top_char_trigrams = char_ngrams.most_common(50)

    # Compile all features into dict
    features = {
        "basic_counts": {
            "total_words": total_words,
            "total_sentences": total_sentences,
            "total_paragraphs": total_paragraphs,
            "avg_sentence_length": avg_sentence_length,
            "median_sentence_length": median_sentence_length,
            "stdev_sentence_length": stdev_sentence_length
        },
        "lexical_diversity": {
            "ttr": ttr,
            "mattr": mattr,
            "hapax_legomena_ratio": hapax_ratio
        },
        "top_content_words": top_content_words,
        "favorite_phrases": top_phrases,
        "function_word_frequencies": function_freq,
        "pos_distribution": pos_distribution,
        "syntactic_complexity": {
            "avg_verbs_per_sentence": avg_verbs_per_sentence,
            "passive_voice_ratio": passive_ratio
        },
        "punctuation_usage_per_100_words": punct_per_100,
        "readability": {
            "flesch_reading_ease": flesch_reading_ease,
            "flesch_kincaid_grade": flesch_kincaid_grade,
            "gunning_fog": gunning_fog
        },
        "transition_word_frequencies": transition_freq,
        "top_character_trigrams": top_char_trigrams
    }
    return features

def main():
    # Ensure directories exist
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    # Read all cleaned text files
    clean_files = list(CLEAN_DATA_DIR.glob("*.txt"))
    if not clean_files:
        print(f"No clean text files found in {CLEAN_DATA_DIR}. Run ingestion first.")
        sys.exit(1)

    print(f"Found {len(clean_files)} cleaned files.")

    # If only one file, just use that; else concatenate with double newlines
    all_text = ""
    for file_path in clean_files:
        text = file_path.read_text(encoding="utf-8")
        all_text += text + "\n\n"

    print("Extracting features...")
    features = extract_features(all_text)

    # Save to JSON
    output_file = PROFILE_DIR / "style_profile.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(features, f, indent=2, ensure_ascii=False)

    print(f"Style profile saved to {output_file}")

if __name__ == "__main__":
    main()