import React, { useState } from 'react';
import { FileCode, Download, Copy, Check, X, Sparkles, BookOpen } from 'lucide-react';
import { StylometryProfile } from '../types';

interface SkillPreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  skillContent: string | null;
  profile: StylometryProfile | null;
  onDownload: () => void;
}

export const SkillPreviewModal: React.FC<SkillPreviewModalProps> = ({
  isOpen,
  onClose,
  skillContent,
  profile,
  onDownload,
}) => {
  const [activeTab, setActiveTab] = useState<'skill' | 'profile'>('skill');
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const handleCopy = () => {
    if (!skillContent) return;
    navigator.clipboard.writeText(skillContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="w-full max-w-4xl bg-white border border-[#EDEDED] rounded-2xl shadow-2xl overflow-hidden flex flex-col h-[85vh]">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-[#F5F5F5] flex items-center justify-between bg-white">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-[#F5F5F5] text-neutral-800 flex items-center justify-center">
              <FileCode className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-medium text-[#1A1A1A]">SKILL.md Output & Stylometric Blueprint</h3>
              <p className="text-xs text-gray-400 font-mono">Location: data/output/SKILL.md</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className="flex rounded-lg bg-[#F5F5F5] p-0.5 border border-[#EEEEEE] mr-2">
              <button
                type="button"
                onClick={() => setActiveTab('skill')}
                className={`px-3 py-1 text-xs font-medium rounded-md transition-all ${
                  activeTab === 'skill'
                    ? 'bg-white text-black shadow-sm'
                    : 'text-gray-400 hover:text-black'
                }`}
              >
                SKILL.md
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('profile')}
                className={`px-3 py-1 text-xs font-medium rounded-md transition-all ${
                  activeTab === 'profile'
                    ? 'bg-white text-black shadow-sm'
                    : 'text-gray-400 hover:text-black'
                }`}
              >
                Profile JSON
              </button>
            </div>

            <button
              type="button"
              onClick={handleCopy}
              className="p-2 rounded-lg text-gray-400 hover:text-black hover:bg-[#F5F5F5] transition-colors text-xs flex items-center gap-1.5"
              title="Copy to clipboard"
            >
              {copied ? <Check className="w-4 h-4 text-green-600" /> : <Copy className="w-4 h-4" />}
            </button>

            <button
              type="button"
              onClick={onDownload}
              className="px-3 py-1.5 rounded-lg text-xs font-medium bg-black hover:opacity-90 active:scale-[0.98] text-white transition-all flex items-center gap-1.5 shadow-sm"
              title="Download SKILL.md"
            >
              <Download className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Download</span>
            </button>

            <button
              type="button"
              onClick={onClose}
              className="p-2 rounded-lg text-gray-400 hover:text-black hover:bg-[#F5F5F5] transition-colors ml-1"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 bg-[#FAFAFA] font-mono text-xs text-neutral-800 leading-relaxed select-text">
          {activeTab === 'skill' ? (
            <pre className="whitespace-pre-wrap font-mono">{skillContent || 'No SKILL.md generated yet.'}</pre>
          ) : (
            <pre className="whitespace-pre-wrap text-neutral-800 font-mono">
              {profile ? JSON.stringify(profile, null, 2) : 'No profile loaded.'}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
};
