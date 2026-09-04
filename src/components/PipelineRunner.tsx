import React from 'react';
import { Play, Loader2, Download, CheckCircle2, AlertTriangle, FileCode2, Copy, Sparkles } from 'lucide-react';
import { PipelineState, AppSettings } from '../types';

interface PipelineRunnerProps {
  pipelineState: PipelineState;
  settings: AppSettings | null;
  onRunPipeline: () => Promise<void>;
  onDownloadSkill: () => void;
  onViewSkillModal: () => void;
  onOpenSettings: () => void;
}

export const PipelineRunner: React.FC<PipelineRunnerProps> = ({
  pipelineState,
  settings,
  onRunPipeline,
  onDownloadSkill,
  onViewSkillModal,
  onOpenSettings,
}) => {
  const [copiedPrompt, setCopiedPrompt] = React.useState(false);
  const isRunning = pipelineState.status === 'running';
  const isCompleted = pipelineState.status === 'completed';
  const isError = pipelineState.status === 'error';
  const currentStage = pipelineState.currentStage;
  const profile = pipelineState.profile;

  // Safe type-cast for dynamic/optional fallback properties
  const profileAny = profile as any;

  // Safely extract stylometric metrics with multi-key fallbacks to settings.py
  const burstiness = 
    profile?.stylistic_fingerprint?.burstiness_index ?? 
    profileAny?.burstiness_index ?? 
    settings?.BURSTINESS_TARGET_INDEX ?? 
    0.95;

  const meanLength = 
    profile?.sentence_metrics?.mean_length ?? 
    profileAny?.sentence_metrics?.mean ?? 
    15;

  const targetSentenceDev = 
    profileAny?.metadata?.target_sentence_deviation ?? 
    settings?.SENTENCE_WORD_COUNT_DEVIATION ?? 
    15;

  const obsSentenceDev = 
    profile?.sentence_metrics?.observed_deviation ?? 
    profileAny?.sentence_metrics?.std_length ?? 
    profileAny?.sentence_metrics?.std_dev ?? 
    0;

  const targetParagraphDev = 
    profileAny?.metadata?.target_paragraph_deviation ?? 
    settings?.PARAGRAPH_WORD_COUNT_DEVIATION ?? 
    40;

  const obsParagraphDev = 
    profile?.paragraph_metrics?.observed_deviation ?? 
    profileAny?.paragraph_metrics?.std_length ?? 
    profileAny?.paragraph_metrics?.std_dev ?? 
    0;

  const rhythmVariation = 
    profile?.stylistic_fingerprint?.rhythm_variation?.split(' ')[0] ?? 
    'Balanced';

  const typeTokenRatio = 
    profile?.statistics?.type_token_ratio ?? 
    profileAny?.lexical_diversity?.type_token_ratio ?? 
    0;

  const uniqueWords = 
    profile?.statistics?.unique_words ?? 
    profileAny?.lexical_diversity?.unique_words ?? 
    0;

  const genTemperature = 
    profileAny?.metadata?.generation_temperature ?? 
    settings?.GENERATION_TEMPERATURE ?? 
    0.62;

  const copyUsagePrompt = () => {
    if (!profile) return;
    const template = `[SYSTEM / STYLE INSTRUCTION]
Act as an author writing with the following stylometric constraints:
- Persona: Direct, authentic human voice calibrated with ${burstiness} burstiness.
- Sentence Cadence: Average ${meanLength} words with high variance (±${targetSentenceDev} words). Alternate between short punchy sentences and fluid compound thoughts.
- Anti-AI Constraint: Strictly avoid robotic transitions (no "furthermore", "moreover", "delve", "testament", "tapestry"). Use natural human rhythm and occasional parenthetical aside.
- Temperature: ${genTemperature}

[USER TASK]
`;
    navigator.clipboard.writeText(template);
    setCopiedPrompt(true);
    setTimeout(() => setCopiedPrompt(false), 2000);
  };

  const STAGES = [
    { step: 1, label: 'Environment' },
    { step: 2, label: 'Ingestion' },
    { step: 3, label: 'Stylometry' },
    { step: 4, label: 'Anti-AI Rules' },
    { step: 5, label: 'SKILL.md' },
  ];

  return (
    <div className="w-full space-y-6">
      {/* Primary Action Button & Status Bar */}
      <div className="bg-white border border-[#EDEDED] rounded-2xl p-6 sm:p-8 shadow-sm">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="text-center sm:text-left">
            <div className="flex items-center justify-center sm:justify-start gap-2 mb-1">
              <h2 className="text-sm font-semibold uppercase tracking-widest text-gray-500">
                Active Pipeline
              </h2>
              {settings && (
                <span className="text-[11px] font-mono text-gray-600 bg-[#F9F9F9] border border-[#EEEEEE] px-2 py-0.5 rounded-md">
                  {settings.OLLAMA_MODEL} (T={genTemperature})
                </span>
              )}
            </div>
            <h3 className="text-xl sm:text-2xl font-light text-[#1A1A1A] tracking-tight">
              Execute Stylometry Pipeline
            </h3>
            <p className="text-xs sm:text-sm text-gray-400 mt-1 max-w-lg">
              Scans your authentic writing corpus, extracts sentence & paragraph variance, applies Anti-AI detector rules, and packages the result into <span className="font-mono text-neutral-800">SKILL.md</span>.
            </p>
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            <button
              id="run-pipeline-btn"
              type="button"
              disabled={isRunning}
              onClick={onRunPipeline}
              className={`w-full sm:w-auto px-8 py-3.5 rounded-xl font-medium text-sm uppercase tracking-wider transition-all flex items-center justify-center gap-2.5 ${
                isRunning
                  ? 'bg-neutral-200 text-neutral-500 cursor-not-allowed'
                  : 'bg-black hover:opacity-90 active:scale-[0.98] text-white shadow-sm'
              }`}
            >
              {isRunning ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-white" />
                  <span>Processing...</span>
                </>
              ) : isCompleted ? (
                <>
                  <Play className="w-3.5 h-3.5 fill-white" />
                  <span>RE-RUN PIPELINE</span>
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5 fill-white" />
                  <span>RUN PIPELINE</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Loading Progress State */}
        {isRunning && (
          <div className="mt-8 pt-6 border-t border-[#F5F5F5] animate-in fade-in duration-200">
            <div className="flex justify-between items-center text-xs mb-2">
              <span className="font-medium text-gray-600 flex items-center gap-1.5">
                <Loader2 className="w-3.5 h-3.5 animate-spin text-black" />
                <span>{currentStage?.stage || 'Processing Style Matrix...'}</span>
              </span>
              <span className="font-mono text-gray-500 font-medium">
                {currentStage?.percent || 15}% Complete
              </span>
            </div>

            {/* Progress Track */}
            <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden mb-3">
              <div
                className="bg-black h-full transition-all duration-300 rounded-full"
                style={{ width: `${Math.max(currentStage?.percent || 15, 8)}%` }}
              />
            </div>

            <div className="flex justify-between text-[11px] text-gray-500 font-mono uppercase">
              <span className="truncate pr-2">{currentStage?.details || 'Analyzing Linguistic Variance'}</span>
              <span>{currentStage?.percent || 15}%</span>
            </div>

            {/* Stepper Dots */}
            <div className="grid grid-cols-5 gap-2 mt-5 pt-4 border-t border-[#F5F5F5]">
              {STAGES.map((s) => {
                const isPassed = (currentStage?.step || 1) >= s.step;
                const isCurrent = (currentStage?.step || 1) === s.step;

                return (
                  <div key={s.step} className="text-center">
                    <div
                      className={`w-6 h-6 rounded-full mx-auto flex items-center justify-center text-[10px] font-bold mb-1 transition-all ${
                        isPassed
                          ? 'bg-black text-white'
                          : 'bg-gray-100 text-gray-400'
                      } ${isCurrent ? 'ring-2 ring-black ring-offset-2 ring-offset-white' : ''}`}
                    >
                      {s.step}
                    </div>
                    <span className="text-[10px] text-gray-400 font-medium hidden sm:inline uppercase tracking-wider">
                      {s.label}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Error State */}
        {isError && (
          <div className="mt-6 p-4 rounded-xl bg-red-50 border border-red-200 flex items-start gap-3 text-xs text-red-700">
            <AlertTriangle className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-red-800">Pipeline Execution Error</p>
              <p className="text-red-600 mt-0.5">{pipelineState.lastError}</p>
            </div>
          </div>
        )}
      </div>

      {/* Completed Output Summary Card */}
      {isCompleted && profile && (
        <div className="bg-white border border-[#EDEDED] rounded-2xl p-6 sm:p-8 shadow-sm animate-in fade-in duration-300">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-6 pb-6 border-b border-[#F5F5F5]">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-green-50 border border-green-200 text-green-700 flex items-center justify-center">
                <CheckCircle2 className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <h3 className="text-base sm:text-lg font-medium text-[#1A1A1A]">
                  SKILL.md Generated & Calibrated
                </h3>
                <p className="text-xs text-gray-400 font-mono">
                  Target output saved to <span className="text-gray-600 underline">data/output/SKILL.md</span>
                </p>
              </div>
            </div>

            {/* Direct Action Buttons */}
            <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
              <button
                id="download-skill-btn"
                type="button"
                onClick={onDownloadSkill}
                className="flex-1 md:flex-initial px-4 py-2 rounded-xl text-xs font-semibold bg-black hover:opacity-90 active:scale-[0.98] text-white transition-all flex items-center justify-center gap-1.5"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Download SKILL.md</span>
              </button>

              <button
                id="view-skill-modal-btn"
                type="button"
                onClick={onViewSkillModal}
                className="px-3.5 py-2 rounded-xl text-xs font-medium bg-[#F9F9F9] hover:bg-[#EFEFEF] text-gray-700 border border-[#EEEEEE] transition-all flex items-center gap-1.5"
              >
                <FileCode2 className="w-3.5 h-3.5 text-gray-500" />
                <span>Preview SKILL.md</span>
              </button>

              <button
                id="copy-prompt-template-btn"
                type="button"
                onClick={copyUsagePrompt}
                className="px-3.5 py-2 rounded-xl text-xs font-medium bg-[#F9F9F9] hover:bg-[#EFEFEF] text-gray-700 border border-[#EEEEEE] transition-all flex items-center gap-1.5"
              >
                <Copy className="w-3.5 h-3.5 text-gray-500" />
                <span>{copiedPrompt ? 'Copied Prompt!' : 'Copy Prompt'}</span>
              </button>
            </div>
          </div>

          {/* Stylometric Key Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5 mb-6">
            <div className="bg-[#F9F9F9] border border-[#EEEEEE] rounded-xl p-4">
              <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block">
                Sentence Dev Target
              </span>
              <div className="flex items-baseline gap-1.5 mt-1">
                <span className="text-xl font-bold text-[#1A1A1A] font-mono">
                  ±{targetSentenceDev}
                </span>
                <span className="text-[11px] text-gray-400 font-mono">
                  (obs: {obsSentenceDev})
                </span>
              </div>
            </div>

            <div className="bg-[#F9F9F9] border border-[#EEEEEE] rounded-xl p-4">
              <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block">
                Paragraph Dev Target
              </span>
              <div className="flex items-baseline gap-1.5 mt-1">
                <span className="text-xl font-bold text-[#1A1A1A] font-mono">
                  ±{targetParagraphDev}
                </span>
                <span className="text-[11px] text-gray-400 font-mono">
                  (obs: {obsParagraphDev})
                </span>
              </div>
            </div>

            <div className="bg-[#F9F9F9] border border-[#EEEEEE] rounded-xl p-4">
              <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block">
                Burstiness Score
              </span>
              <div className="flex items-baseline gap-1.5 mt-1">
                <span className="text-xl font-bold text-[#1A1A1A] font-mono">
                  {burstiness}
                </span>
                <span className="text-[11px] text-gray-400 font-mono">
                  {rhythmVariation}
                </span>
              </div>
            </div>

            <div className="bg-[#F9F9F9] border border-[#EEEEEE] rounded-xl p-4">
              <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block">
                Lexical Diversity (TTR)
              </span>
              <div className="flex items-baseline gap-1.5 mt-1">
                <span className="text-xl font-bold text-[#1A1A1A] font-mono">
                  {typeTokenRatio}
                </span>
                <span className="text-[11px] text-gray-400 font-mono">
                  ({uniqueWords} uniq)
                </span>
              </div>
            </div>
          </div>

          {/* Anti-AI Prompt Snippet Box */}
          <div className="bg-[#FAFAFA] border border-[#EEEEEE] rounded-xl p-4 font-mono text-xs text-neutral-800">
            <div className="flex items-center justify-between text-gray-400 mb-2 font-sans font-medium">
              <span className="flex items-center gap-1.5 text-xs text-gray-700">
                <Sparkles className="w-3.5 h-3.5 text-gray-500" />
                <span>Calibrated System Prompt Injection (Bake-in)</span>
              </span>
              <button
                type="button"
                onClick={copyUsagePrompt}
                className="text-gray-700 hover:text-black transition-colors text-xs font-semibold"
              >
                {copiedPrompt ? 'Copied to Clipboard!' : 'Copy Template'}
              </button>
            </div>
            <pre className="text-gray-700 overflow-x-auto whitespace-pre-wrap leading-relaxed">
{`[SYSTEM / STYLE INSTRUCTION]
Act as an author with burstiness ${burstiness}, sentence deviation ±${targetSentenceDev} words, paragraph deviation ±${targetParagraphDev} words, and temperature ${genTemperature}. Strictly avoid robotic AI transitions ("furthermore", "moreover", "delve", "testament").`}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};