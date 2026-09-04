import * as fs from 'fs';
import * as path from 'path';
import { AppSettings } from '../models/SettingsModel.js';

export interface StylometryProfile {
  metadata: {
    model_configured: string;
    generation_temperature: number;
    target_sentence_deviation: number;
    target_paragraph_deviation: number;
    analyzed_at: string;
  };
  statistics: {
    total_words: number;
    total_sentences: number;
    total_paragraphs: number;
    unique_words: number;
    type_token_ratio: number;
  };
  sentence_metrics: {
    mean_length: number;
    observed_deviation: number;
    configured_deviation: number;
    min_length: number;
    max_length: number;
    conjunction_starter_ratio: number;
  };
  paragraph_metrics: {
    mean_length: number;
    observed_deviation: number;
    configured_deviation: number;
    min_length: number;
    max_length: number;
  };
  punctuation_profile_per_1000w: {
    commas: number;
    semicolons: number;
    em_dashes: number;
    ellipses: number;
    question_marks: number;
    exclamation_marks: number;
    parentheses: number;
  };
  stylistic_fingerprint: {
    burstiness_index: number;
    rhythm_variation: string;
    cadence_pattern: string;
    preferred_contractions: boolean;
  };
  few_shot_examples: string[];
}

export class StylometryEngine {
  public static cleanText(raw: string): string {
    return raw
      .replace(/\r\n/g, '\n')
      .replace(/\r/g, '\n')
      .replace(/\n{3,}/g, '\n\n')
      .trim();
  }

  private static calculateStdDev(numbers: number[], mean: number): number {
    if (numbers.length < 2) return 0;
    const variance = numbers.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / (numbers.length - 1);
    return Math.sqrt(variance);
  }

  public static analyzeCorpus(corpus: string, settings: AppSettings): StylometryProfile {
    const cleaned = this.cleanText(corpus);
    const paragraphs = cleaned.split('\n\n').map(p => p.trim()).filter(Boolean);
    const sentences = cleaned
      .split(/(?<=[.?!])\s+/)
      .map(s => s.trim())
      .filter(s => s.length > 3);

    const words = cleaned.match(/\b[a-zA-Z0-9_\'-]+\b/g) || [];
    const lowerWords = words.map(w => w.toLowerCase());
    const totalWords = words.length;
    const uniqueWords = new Set(lowerWords).size;

    // Sentence lengths
    const sentenceLengths = sentences.map(s => (s.match(/\b[a-zA-Z0-9_\'-]+\b/g) || []).length).filter(l => l > 0);
    const avgSentLen = sentenceLengths.length ? sentenceLengths.reduce((a, b) => a + b, 0) / sentenceLengths.length : 0;
    const stdSentLen = this.calculateStdDev(sentenceLengths, avgSentLen);

    // Paragraph lengths
    const paraLengths = paragraphs.map(p => (p.match(/\b[a-zA-Z0-9_\'-]+\b/g) || []).length).filter(l => l > 0);
    const avgParaLen = paraLengths.length ? paraLengths.reduce((a, b) => a + b, 0) / paraLengths.length : 0;
    const stdParaLen = this.calculateStdDev(paraLengths, avgParaLen);

    // Lexical diversity
    const ttr = totalWords > 0 ? uniqueWords / totalWords : 0;

    // Punctuation per 1000 words
    const mult = totalWords > 0 ? 1000 / totalWords : 1;
    const commas = (cleaned.match(/,/g) || []).length * mult;
    const semicolons = (cleaned.match(/;/g) || []).length * mult;
    const emDashes = ((cleaned.match(/—/g) || []).length + (cleaned.match(/--/g) || []).length) * mult;
    const ellipses = ((cleaned.match(/\.\.\./g) || []).length + (cleaned.match(/…/g) || []).length) * mult;
    const questionMarks = (cleaned.match(/\?/g) || []).length * mult;
    const exclamationMarks = (cleaned.match(/!/g) || []).length * mult;
    const parentheses = (cleaned.match(/\(/g) || []).length * mult;

    // Conjunction starters
    const conjWords = new Set(['and', 'but', 'so', 'yet', 'or', 'nor', 'however', 'moreover', 'furthermore', 'meanwhile', 'actually', 'well', 'basically', 'frankly']);
    let conjCount = 0;
    for (const s of sentences) {
      const first = s.toLowerCase().match(/^[a-z]+/);
      if (first && conjWords.has(first[0])) {
        conjCount++;
      }
    }
    const conjRatio = sentences.length ? conjCount / sentences.length : 0;
    const burstiness = Math.min(1.0, Math.max(0.2, (stdSentLen / (avgSentLen + 1e-5)) * 0.75 + (stdParaLen / (avgParaLen + 1e-5)) * 0.25));

    // Few-shot candidate selection
    const candidateParas = paragraphs.filter(p => {
      const len = p.split(/\s+/).length;
      return len >= 20 && len <= 180;
    });
    const pool = candidateParas.length >= settings.FEW_SHOT_EXAMPLE_COUNT ? candidateParas : paragraphs;
    const fewShotExamples = pool.slice(0, settings.FEW_SHOT_EXAMPLE_COUNT);

    return {
      metadata: {
        model_configured: settings.OLLAMA_MODEL || 'llama3:latest',
        generation_temperature: settings.GENERATION_TEMPERATURE,
        target_sentence_deviation: settings.SENTENCE_WORD_COUNT_DEVIATION,
        target_paragraph_deviation: settings.PARAGRAPH_WORD_COUNT_DEVIATION,
        analyzed_at: new Date().toISOString()
      },
      statistics: {
        total_words: totalWords,
        total_sentences: sentences.length,
        total_paragraphs: paragraphs.length,
        unique_words: uniqueWords,
        type_token_ratio: Number(ttr.toFixed(3))
      },
      sentence_metrics: {
        mean_length: Number(avgSentLen.toFixed(1)),
        observed_deviation: Number(stdSentLen.toFixed(1)),
        configured_deviation: settings.SENTENCE_WORD_COUNT_DEVIATION,
        min_length: sentenceLengths.length ? Math.min(...sentenceLengths) : 0,
        max_length: sentenceLengths.length ? Math.max(...sentenceLengths) : 0,
        conjunction_starter_ratio: Number(conjRatio.toFixed(3))
      },
      paragraph_metrics: {
        mean_length: Number(avgParaLen.toFixed(1)),
        observed_deviation: Number(stdParaLen.toFixed(1)),
        configured_deviation: settings.PARAGRAPH_WORD_COUNT_DEVIATION,
        min_length: paraLengths.length ? Math.min(...paraLengths) : 0,
        max_length: paraLengths.length ? Math.max(...paraLengths) : 0
      },
      punctuation_profile_per_1000w: {
        commas: Number(commas.toFixed(1)),
        semicolons: Number(semicolons.toFixed(1)),
        em_dashes: Number(emDashes.toFixed(1)),
        ellipses: Number(ellipses.toFixed(1)),
        question_marks: Number(questionMarks.toFixed(1)),
        exclamation_marks: Number(exclamationMarks.toFixed(1)),
        parentheses: Number(parentheses.toFixed(1))
      },
      stylistic_fingerprint: {
        burstiness_index: Number(burstiness.toFixed(2)),
        rhythm_variation: burstiness > 0.55 ? 'High (Bursty & Organic)' : 'Moderate Rhythm',
        cadence_pattern: 'Dynamic human variability with mixed compound & concise punchy clauses',
        preferred_contractions: words.slice(0, 150).some(w => w.includes("'"))
      },
      few_shot_examples: fewShotExamples
    };
  }

  public static generateSkillMarkdown(profile: StylometryProfile): string {
    const { metadata, statistics, sentence_metrics, paragraph_metrics, punctuation_profile_per_1000w, stylistic_fingerprint, few_shot_examples } = profile;

    const bannedWords = [
      'delve into', 'testament to', "it's important to remember",
      "in today's fast-paced world", 'tapestry', 'beacon', 'pinnacle',
      'leverage', 'furthermore,', 'moreover,', 'in conclusion,',
      'it is worth noting', 'serves as a reminder', 'unravel', 'transformative',
      'holistic approach', 'revolutionize', 'embark on a journey', 'navigating the complexities'
    ];

    let exemplarSection = '';
    if (few_shot_examples.length > 0) {
      exemplarSection = few_shot_examples.map((ex, i) => {
        const quoted = ex.split('\n').map(l => `> ${l}`).join('\n');
        return `### Exemplar ${i + 1} (Authentic Human Ground Truth)\n${quoted}`;
      }).join('\n\n');
    } else {
      exemplarSection = '*(Baseline calibrated profile used)*';
    }

    return `---
name: personalized-humanizer-skill
description: Custom writing profile and Anti-AI detection humanization skill calibrated to user stylometry.
version: 1.0.0
model: ${metadata.model_configured}
temperature: ${metadata.generation_temperature}
sentence_deviation_target: ±${metadata.target_sentence_deviation} words
paragraph_deviation_target: ±${metadata.target_paragraph_deviation} words
---

# Personalized Humanizer: Authentic Style & Anti-AI Detection Engine

You are calibrated to emulate the specific, authentic writing style and linguistic fingerprint extracted from the user's authentic documents. All produced text must bypass modern AI detection systems (such as GPTZero, Turnitin, Copyleaks, Originality.ai) by mirroring the organic irregularity, burstiness, and rhetorical cadence of human handwriting and prose.

---

## 1. Stylometric Fingerprint & Linguistic Metrics

- **Target Sentence Length**: Mean ~${sentence_metrics.mean_length} words (Deviation target: **±${metadata.target_sentence_deviation} words**; observed std: **${sentence_metrics.observed_deviation}**).
- **Target Paragraph Length**: Mean ~${paragraph_metrics.mean_length} words (Deviation target: **±${metadata.target_paragraph_deviation} words**; observed std: **${paragraph_metrics.observed_deviation}**).
- **Burstiness & Perplexity Index**: **${stylistic_fingerprint.burstiness_index}** (Status: *${stylistic_fingerprint.rhythm_variation}*).
- **Type-Token Ratio (Lexical Diversity)**: **${statistics.type_token_ratio}** (${statistics.unique_words} unique words out of ${statistics.total_words} total corpus tokens).
- **Punctuation Frequency (per 1,000 words)**:
  - Commas: ${punctuation_profile_per_1000w.commas}
  - Em-dashes (—): ${punctuation_profile_per_1000w.em_dashes}
  - Semicolons (;): ${punctuation_profile_per_1000w.semicolons}
  - Ellipses (...): ${punctuation_profile_per_1000w.ellipses}
  - Question Density: ${punctuation_profile_per_1000w.question_marks}
  - Parentheses: ${punctuation_profile_per_1000w.parentheses}

---

## 2. Mandatory Anti-AI Detection Rules

To eliminate robotic syntactic predictability and defeat AI detector heuristics, you MUST strictly adhere to the following rules:

1. **Banned Boilerplate Vocabulary & Transitions**:
   Never use the following hallmark AI words or phrases:
   ${bannedWords.map(w => `\`"${w}"\``).join(', ')}.
2. **Organic Sentence Cadence & High Burstiness**:
   - Alternate aggressively between short, punchy declarative statements (3–7 words) and complex, rhythmically wandering compound-complex sentences (22–38 words).
   - Never write three consecutive sentences of approximately equal word counts.
3. **Intentional Human Asymmetry**:
   - Do not construct perfectly symmetrical lists (e.g. 3 bullet points with identical noun-verb structures and equal lengths).
   - Integrate natural transition variety (use occasional starting conjunctions like *'And'*, *'But'*, or *'So'* at a frequency of ~${(sentence_metrics.conjunction_starter_ratio * 100).toFixed(1)}%).
4. **Natural Perspective & Voice Consistency**:
   - Maintain a grounded, authentic tone without unnecessary hedging or synthetic disclaimers (*"It is crucial to remember..."*).
   - Use natural contractions (${stylistic_fingerprint.preferred_contractions ? 'enabled' : 'sparingly'}) consistent with human conversational prose.

---

## 3. Authentic Few-Shot Exemplars (Ground Truth)

${exemplarSection}

---

## 4. Baked-In Usage Prompt Template

Use the template below whenever prompting an LLM (such as ${metadata.model_configured} or Gemini) to generate text in this exact style:

\`\`\`markdown
[SYSTEM / STYLE INSTRUCTION]
Act as an author writing with the following stylometric constraints:
- Persona: Direct, authentic human voice calibrated with ${stylistic_fingerprint.burstiness_index} burstiness.
- Sentence Cadence: Average ${sentence_metrics.mean_length} words with high variance (±${metadata.target_sentence_deviation} words). Alternate between short punchy sentences and fluid compound thoughts.
- Anti-AI Constraint: Strictly avoid robotic transitions (no "furthermore", "moreover", "delve", "testament", "tapestry"). Use natural human rhythm and occasional parenthetical aside.
- Temperature: ${metadata.generation_temperature}

[USER TASK]
{{YOUR_TOPIC_OR_DRAFT_HERE}}
\`\`\`
`;
  }
}
