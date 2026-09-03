export interface AppSettings {
  GENERATION_TEMPERATURE: number;
  FEW_SHOT_EXAMPLE_COUNT: number;
  SUMMARIZE_EXAMPLE_COUNT: number;
  SENTENCE_WORD_COUNT_DEVIATION: number;
  PARAGRAPH_WORD_COUNT_DEVIATION: number;
  OLLAMA_MODEL: string;
  BURSTINESS_TARGET_INDEX?: number;
  VOCABULARY_DIVERSITY_FLOOR?: number;
}

export interface RawFileSummary {
  id: string;
  name: string;
  size: number;
  sizeFormatted: string;
  createdAt: string;
  estimatedWords: number;
  preview: string;
}

export interface DataFolderStatus {
  rawCount: number;
  cleanExists: boolean;
  profileExists: boolean;
  outputExists: boolean;
  outputFileSize?: number;
  lastUpdated?: string;
}

export interface PipelineProgressStage {
  step: number;
  totalSteps: number;
  percent: number;
  stage: string;
  details: string;
  timestamp: number;
}

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

export interface PipelineState {
  status: 'idle' | 'running' | 'completed' | 'error';
  currentStage: PipelineProgressStage | null;
  logs: string[];
  lastError: string | null;
  startedAt: string | null;
  finishedAt: string | null;
  profile: StylometryProfile | null;
  skillContent: string | null;
}

export interface SetupStatus {
  isSetupComplete: boolean;
  directoriesStatus: {
    raw: boolean;
    clean: boolean;
    profiles: boolean;
    output: boolean;
  };
  settingsConfigured: boolean;
  lastChecked: string;
  message: string;
}
