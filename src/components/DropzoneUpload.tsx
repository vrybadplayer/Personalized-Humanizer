import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, Plus, Check, Loader2, Sparkles } from 'lucide-react';

interface DropzoneUploadProps {
  onFileUpload: (file: File) => Promise<void>;
  onPasteText: (title: string, text: string) => Promise<void>;
  isUploading: boolean;
}

const SAMPLE_WRITING_EXCERPTS = [
  {
    title: 'personal_reflection_essay.txt',
    text: `I've always believed that writing should sound like a real person talking across a coffee table, not like an algorithmic summary produced by a corporate committee. When I look back at my older journal entries, there's an undeniable rhythm—some thoughts run on for five lines with layered clauses, and then suddenly stop. Period. That contrast is where voice lives.\n\nMost modern AI tools try to smooth everything out until every paragraph is thirty-eight words long with three perfectly balanced supporting details. It feels sterile. True authenticity isn't about avoiding mistakes; it's about intentional cadence, subtle idiosyncrasies, and the willingness to let an em-dash carry the weight of an unfinished thought. We don't always need transitional signposts like 'furthermore' or 'moreover'—context alone is often enough.`
  },
  {
    title: 'handwriting_sample_analysis.txt',
    text: `Notes from my physical notebook (transcribed):\n\nFirst draft thoughts on architecture and simplicity. We overcomplicate workflows because complexity gives the illusion of productivity. But the best tools are the ones you forget you're using. You drop a file in, flip one or two knobs if needed, and hit execute. Everything else is distraction.\n\nNotice how natural handwriting skips decorative transitions. If an idea is strong, it stands on its own feet. Keep the sentences bursty—mix seven-word declarations with complex wandering paragraphs. That's the secret to evading detection heuristics.`
  }
];

export const DropzoneUpload: React.FC<DropzoneUploadProps> = ({
  onFileUpload,
  onPasteText,
  isUploading,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [showPasteModal, setShowPasteModal] = useState(false);
  const [pasteTitle, setPasteTitle] = useState('');
  const [pasteContent, setPasteContent] = useState('');
  const [isSubmittingPaste, setIsSubmittingPaste] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      for (let i = 0; i < e.dataTransfer.files.length; i++) {
        await onFileUpload(e.dataTransfer.files[i]);
      }
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      for (let i = 0; i < e.target.files.length; i++) {
        await onFileUpload(e.target.files[i]);
      }
      e.target.value = '';
    }
  };

  const handlePasteSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!pasteContent.trim()) return;
    setIsSubmittingPaste(true);
    try {
      await onPasteText(pasteTitle || 'pasted_writing_sample', pasteContent);
      setPasteTitle('');
      setPasteContent('');
      setShowPasteModal(false);
    } finally {
      setIsSubmittingPaste(false);
    }
  };

  const handleLoadPreset = async (preset: typeof SAMPLE_WRITING_EXCERPTS[0]) => {
    setIsSubmittingPaste(true);
    try {
      await onPasteText(preset.title, preset.text);
    } finally {
      setIsSubmittingPaste(false);
    }
  };

  return (
    <div className="w-full">
      {/* Hidden file input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        multiple
        className="hidden"
        accept=".txt,.md,.markdown,.pdf,.doc,.docx,.rtf,.json"
      />

      {/* Main Drag & Drop Card */}
      <div
        id="dropzone-card"
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative cursor-pointer group rounded-2xl border-2 border-dashed transition-all duration-200 p-8 sm:p-10 text-center flex flex-col items-center justify-center ${
          isDragging
            ? 'border-neutral-900 bg-neutral-50 scale-[1.005]'
            : 'border-[#EDEDED] bg-white hover:border-neutral-400 hover:bg-[#FAFAFA]'
        }`}
      >
        <div className="w-16 h-16 rounded-full bg-[#F5F5F5] group-hover:scale-105 transition-transform text-gray-400 flex items-center justify-center mb-4">
          {isUploading ? (
            <Loader2 className="w-7 h-7 animate-spin text-black" />
          ) : (
            <UploadCloud className="w-7 h-7" />
          )}
        </div>

        <h3 className="text-base sm:text-lg font-medium text-[#1A1A1A] mb-1">
          {isUploading ? 'Ingesting writing sample...' : 'Upload Handwriting Samples'}
        </h3>
        
        <p className="text-xs sm:text-sm text-gray-400 max-w-sm mx-auto mb-6 leading-relaxed">
          Drag and drop your <span className="text-gray-600 font-mono text-xs">.txt, .pdf, .md</span> documents to scan authentic stylometric rhythm and voice.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-2.5">
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              fileInputRef.current?.click();
            }}
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-black hover:opacity-90 active:scale-[0.98] text-white transition-all flex items-center gap-1.5"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Browse Files</span>
          </button>

          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              setShowPasteModal(true);
            }}
            className="px-4 py-2 rounded-xl text-xs font-medium bg-[#F9F9F9] hover:bg-[#EFEFEF] text-gray-700 border border-[#EEEEEE] transition-all flex items-center gap-1.5"
          >
            <FileText className="w-3.5 h-3.5 text-gray-400" />
            <span>Paste Text Sample</span>
          </button>

          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              handleLoadPreset(SAMPLE_WRITING_EXCERPTS[0]);
            }}
            disabled={isSubmittingPaste}
            className="text-[11px] bg-gray-100 hover:bg-gray-200 px-3 py-1.5 rounded-lg text-gray-600 transition-colors flex items-center gap-1.5"
          >
            <Sparkles className="w-3.5 h-3.5 text-gray-500" />
            <span>Sample Essay</span>
          </button>
        </div>
      </div>

      {/* Paste Writing Sample Modal */}
      {showPasteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm animate-in fade-in duration-150">
          <div className="w-full max-w-xl bg-white border border-[#EDEDED] rounded-2xl p-6 sm:p-8 shadow-2xl">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-neutral-800" />
                <h3 className="text-base font-semibold text-[#1A1A1A]">Paste Writing / Handwriting Sample</h3>
              </div>
              <button
                type="button"
                onClick={() => setShowPasteModal(false)}
                className="text-gray-400 hover:text-black text-sm"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handlePasteSubmit} className="space-y-4">
              <div>
                <label className="block text-[10px] uppercase font-bold text-gray-400 tracking-wider mb-1.5">
                  Document Title (Optional)
                </label>
                <input
                  type="text"
                  placeholder="e.g. personal_journal_entry.txt"
                  value={pasteTitle}
                  onChange={(e) => setPasteTitle(e.target.value)}
                  className="w-full px-4 py-2.5 bg-[#F9F9F9] border border-[#EEEEEE] rounded-lg text-sm text-[#1A1A1A] placeholder:text-gray-400 focus:bg-white focus:outline-none focus:border-neutral-400"
                />
              </div>

              <div>
                <label className="block text-[10px] uppercase font-bold text-gray-400 tracking-wider mb-1.5">
                  Writing Sample Body
                </label>
                <textarea
                  rows={8}
                  placeholder="Paste your natural handwriting transcript, essay, or writing sample here..."
                  value={pasteContent}
                  onChange={(e) => setPasteContent(e.target.value)}
                  className="w-full px-4 py-2.5 bg-[#F9F9F9] border border-[#EEEEEE] rounded-lg text-sm text-[#1A1A1A] placeholder:text-gray-400 focus:bg-white focus:outline-none focus:border-neutral-400 resize-none font-sans"
                  required
                />
                <p className="text-[11px] text-gray-400 mt-1">
                  ~{pasteContent.trim().split(/\s+/).filter(Boolean).length} words entered.
                </p>
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowPasteModal(false)}
                  className="px-4 py-2 text-xs font-medium text-gray-500 hover:text-black"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={!pasteContent.trim() || isSubmittingPaste}
                  className="px-5 py-2.5 rounded-xl text-xs font-medium bg-black hover:opacity-90 active:scale-[0.98] disabled:opacity-50 text-white transition-all flex items-center gap-1.5"
                >
                  {isSubmittingPaste ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      <span>Saving...</span>
                    </>
                  ) : (
                    <>
                      <Check className="w-3.5 h-3.5" />
                      <span>Save to data/raw</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
