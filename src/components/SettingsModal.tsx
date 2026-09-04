import React, { useState, useEffect } from 'react';
import { Sliders, Check, RotateCcw, X, Cpu, Thermometer, Hash, GitCommit } from 'lucide-react';
import { AppSettings } from '../types';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  settings: AppSettings | null;
  onSaveSettings: (settings: AppSettings) => Promise<void>;
}

const DEFAULT_SETTINGS: AppSettings = {
  GENERATION_TEMPERATURE: 0.72,
  FEW_SHOT_EXAMPLE_COUNT: 3,
  SUMMARIZE_EXAMPLE_COUNT: 5,
  SENTENCE_WORD_COUNT_DEVIATION: 4.5,
  PARAGRAPH_WORD_COUNT_DEVIATION: 15.0,
  OLLAMA_MODEL: 'llama3:latest',
  BURSTINESS_TARGET_INDEX: 0.68,
  VOCABULARY_DIVERSITY_FLOOR: 0.42
};

const POPULAR_MODELS = [
  'llama3:latest',
  'llama3.1:8b',
  'mistral:latest',
  'gemma2:9b',
  'qwen2.5:14b',
  'deepseek-r1:8b'
];

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  settings,
  onSaveSettings,
}) => {
  const [formData, setFormData] = useState<AppSettings>(DEFAULT_SETTINGS);
  const [isSaving, setIsSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    if (settings) {
      setFormData(settings);
    }
  }, [settings, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      await onSaveSettings(formData);
      setSavedSuccess(true);
      setTimeout(() => {
        setSavedSuccess(false);
        onClose();
      }, 700);
    } finally {
      setIsSaving(false);
    }
  };

  const handleResetDefaults = () => {
    setFormData(DEFAULT_SETTINGS);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="w-full max-w-2xl bg-white border border-[#EDEDED] rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="px-6 py-5 border-b border-[#F5F5F5] flex items-center justify-between bg-white">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#F5F5F5] text-neutral-800 flex items-center justify-center">
              <Sliders className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-medium text-[#1A1A1A]">System Settings & Hyperparameters</h3>
              <p className="text-xs text-gray-400">Directly written and persisted to <span className="font-mono text-gray-600">backend/config/settings.py</span></p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg text-gray-400 hover:text-black hover:bg-[#F5F5F5] transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <form onSubmit={handleSubmit} className="p-6 overflow-y-auto space-y-6">
          {/* OLLAMA_MODEL */}
          <div className="space-y-2">
            <label className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-gray-500">
              <span className="flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5 text-gray-400" />
                <span>OLLAMA_MODEL</span>
              </span>
              <span className="font-mono text-gray-700">{formData.OLLAMA_MODEL}</span>
            </label>
            <input
              type="text"
              value={formData.OLLAMA_MODEL}
              onChange={(e) => setFormData({ ...formData, OLLAMA_MODEL: e.target.value })}
              className="w-full px-3.5 py-2.5 bg-[#FAFAFA] border border-[#EEEEEE] rounded-xl text-sm font-mono text-[#1A1A1A] placeholder:text-gray-400 focus:bg-white focus:outline-none focus:border-neutral-400"
              placeholder="e.g. llama3:latest"
              required
            />
            <div className="flex flex-wrap gap-1.5 pt-1">
              <span className="text-[11px] text-gray-400 mr-1">Presets:</span>
              {POPULAR_MODELS.map((model) => (
                <button
                  key={model}
                  type="button"
                  onClick={() => setFormData({ ...formData, OLLAMA_MODEL: model })}
                  className={`text-[11px] font-mono px-2 py-0.5 rounded-md border transition-all ${
                    formData.OLLAMA_MODEL === model
                      ? 'bg-black text-white border-black'
                      : 'bg-[#F9F9F9] text-gray-600 border-[#EEEEEE] hover:border-gray-400'
                  }`}
                >
                  {model}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            {/* GENERATION_TEMPERATURE */}
            <div className="space-y-2 bg-[#FAFAFA] p-4 rounded-xl border border-[#EEEEEE]">
              <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-gray-500">
                <span className="flex items-center gap-1.5">
                  <Thermometer className="w-3.5 h-3.5 text-gray-400" />
                  <span>TEMPERATURE</span>
                </span>
                <span className="font-mono text-gray-800">{formData.GENERATION_TEMPERATURE.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0.1"
                max="1.5"
                step="0.01"
                value={formData.GENERATION_TEMPERATURE}
                onChange={(e) => setFormData({ ...formData, GENERATION_TEMPERATURE: parseFloat(e.target.value) })}
                className="w-full accent-black cursor-pointer"
              />
              <p className="text-[11px] text-gray-400 leading-tight">
                Controls sampling randomness and creative variation.
              </p>
            </div>

            {/* BURSTINESS_TARGET_INDEX */}
            <div className="space-y-2 bg-[#FAFAFA] p-4 rounded-xl border border-[#EEEEEE]">
              <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-gray-500">
                <span className="flex items-center gap-1.5">
                  <GitCommit className="w-3.5 h-3.5 text-gray-400" />
                  <span>BURSTINESS INDEX</span>
                </span>
                <span className="font-mono text-gray-800">{(formData.BURSTINESS_TARGET_INDEX || 0.68).toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0.3"
                max="0.95"
                step="0.01"
                value={formData.BURSTINESS_TARGET_INDEX || 0.68}
                onChange={(e) => setFormData({ ...formData, BURSTINESS_TARGET_INDEX: parseFloat(e.target.value) })}
                className="w-full accent-black cursor-pointer"
              />
              <p className="text-[11px] text-gray-400 leading-tight">
                Higher values force irregular, human-like rhythm variations.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            {/* SENTENCE_WORD_COUNT_DEVIATION */}
            <div className="space-y-2 bg-[#FAFAFA] p-4 rounded-xl border border-[#EEEEEE]">
              <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-gray-500">
                <span>SENTENCE DEVIATION</span>
                <span className="font-mono text-gray-800">±{formData.SENTENCE_WORD_COUNT_DEVIATION.toFixed(1)} words</span>
              </div>
              <input
                type="range"
                min="1.0"
                max="15.0"
                step="0.5"
                value={formData.SENTENCE_WORD_COUNT_DEVIATION}
                onChange={(e) => setFormData({ ...formData, SENTENCE_WORD_COUNT_DEVIATION: parseFloat(e.target.value) })}
                className="w-full accent-black cursor-pointer"
              />
              <p className="text-[11px] text-gray-400 leading-tight">
                Permitted variance from mean sentence length.
              </p>
            </div>

            {/* PARAGRAPH_WORD_COUNT_DEVIATION */}
            <div className="space-y-2 bg-[#FAFAFA] p-4 rounded-xl border border-[#EEEEEE]">
              <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-gray-500">
                <span>PARAGRAPH DEVIATION</span>
                <span className="font-mono text-gray-800">±{formData.PARAGRAPH_WORD_COUNT_DEVIATION.toFixed(1)} words</span>
              </div>
              <input
                type="range"
                min="3.0"
                max="35.0"
                step="1.0"
                value={formData.PARAGRAPH_WORD_COUNT_DEVIATION}
                onChange={(e) => setFormData({ ...formData, PARAGRAPH_WORD_COUNT_DEVIATION: parseFloat(e.target.value) })}
                className="w-full accent-black cursor-pointer"
              />
              <p className="text-[11px] text-gray-400 leading-tight">
                Permitted variance across paragraph lengths.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            {/* FEW_SHOT_EXAMPLE_COUNT */}
            <div className="space-y-2 bg-[#FAFAFA] p-4 rounded-xl border border-[#EEEEEE]">
              <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-gray-500">
                <span className="flex items-center gap-1.5">
                  <Hash className="w-3.5 h-3.5 text-gray-400" />
                  <span>FEW_SHOT EXAMPLES</span>
                </span>
                <span className="font-mono text-gray-800">{formData.FEW_SHOT_EXAMPLE_COUNT} exemplars</span>
              </div>
              <input
                type="number"
                min="1"
                max="10"
                value={formData.FEW_SHOT_EXAMPLE_COUNT}
                onChange={(e) => setFormData({ ...formData, FEW_SHOT_EXAMPLE_COUNT: parseInt(e.target.value, 10) || 1 })}
                className="w-full px-3.5 py-2 bg-white border border-[#EEEEEE] rounded-xl text-sm font-mono text-[#1A1A1A] focus:outline-none focus:border-neutral-400"
              />
              <p className="text-[11px] text-gray-400 leading-tight">
                Number of verbatim human excerpts injected into SKILL.md.
              </p>
            </div>

            {/* SUMMARIZE_EXAMPLE_COUNT */}
            <div className="space-y-2 bg-[#FAFAFA] p-4 rounded-xl border border-[#EEEEEE]">
              <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-gray-500">
                <span className="flex items-center gap-1.5">
                  <Hash className="w-3.5 h-3.5 text-gray-400" />
                  <span>SUMMARIZE EXAMPLES</span>
                </span>
                <span className="font-mono text-gray-800">{formData.SUMMARIZE_EXAMPLE_COUNT} samples</span>
              </div>
              <input
                type="number"
                min="1"
                max="10"
                value={formData.SUMMARIZE_EXAMPLE_COUNT}
                onChange={(e) => setFormData({ ...formData, SUMMARIZE_EXAMPLE_COUNT: parseInt(e.target.value, 10) || 1 })}
                className="w-full px-3.5 py-2 bg-white border border-[#EEEEEE] rounded-xl text-sm font-mono text-[#1A1A1A] focus:outline-none focus:border-neutral-400"
              />
              <p className="text-[11px] text-gray-400 leading-tight">
                Maximum synthesis candidate blocks during extraction.
              </p>
            </div>
          </div>

          {/* Modal Footer Actions */}
          <div className="flex items-center justify-between pt-4 border-t border-[#F5F5F5]">
            <button
              type="button"
              onClick={handleResetDefaults}
              className="text-xs text-gray-400 hover:text-black flex items-center gap-1.5"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset to Defaults</span>
            </button>

            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-xs font-medium text-gray-500 hover:text-black"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSaving}
                className="px-5 py-2.5 rounded-xl text-xs font-medium bg-black hover:opacity-90 active:scale-[0.98] text-white transition-all flex items-center gap-1.5"
              >
                {savedSuccess ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-green-300" />
                    <span>Saved to backend/config/settings.py!</span>
                  </>
                ) : (
                  <>
                    <Check className="w-3.5 h-3.5" />
                    <span>Save Parameters</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};
