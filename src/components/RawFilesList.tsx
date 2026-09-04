import React, { useState } from 'react';
import { FileText, Trash2, Eye, EyeOff, FileCode } from 'lucide-react';
import { RawFileSummary } from '../types';

interface RawFilesListProps {
  files: RawFileSummary[];
  onDeleteFile: (filename: string) => Promise<void>;
}

export const RawFilesList: React.FC<RawFilesListProps> = ({ files, onDeleteFile }) => {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  if (files.length === 0) {
    return null;
  }

  const handleDelete = async (filename: string) => {
    setDeletingId(filename);
    try {
      await onDeleteFile(filename);
    } finally {
      setDeletingId(null);
    }
  };

  const totalWords = files.reduce((acc, f) => acc + f.estimatedWords, 0);

  return (
    <div className="w-full bg-white border border-[#EDEDED] rounded-2xl p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-[#F5F5F5]">
        <div className="flex items-center gap-2">
          <FileCode className="w-4 h-4 text-gray-400" />
          <h3 className="text-xs font-semibold uppercase tracking-widest text-gray-500">
            Uploaded Corpus ({files.length})
          </h3>
        </div>
        <div className="text-xs text-gray-400">
          Total: <span className="font-medium text-[#1A1A1A]">{totalWords.toLocaleString()} words</span>
        </div>
      </div>

      <div className="space-y-2">
        {files.map((file) => {
          const isExpanded = expandedId === file.id;
          const isDeleting = deletingId === file.id;

          return (
            <div
              key={file.id}
              className="group border border-[#EDEDED] hover:border-gray-300 bg-[#FAFAFA] hover:bg-white rounded-xl p-3.5 transition-all"
            >
              <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-8 h-8 rounded-lg bg-[#F0F0F0] text-gray-600 flex items-center justify-center shrink-0">
                    <FileText className="w-4 h-4 text-gray-500" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs sm:text-sm font-medium text-[#1A1A1A] truncate">
                      {file.name}
                    </p>
                    <div className="flex items-center gap-2 text-[11px] text-gray-400 font-mono">
                      <span>{file.sizeFormatted}</span>
                      <span>•</span>
                      <span>~{file.estimatedWords} words</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-1.5 shrink-0">
                  <button
                    type="button"
                    onClick={() => setExpandedId(isExpanded ? null : file.id)}
                    className="p-1.5 rounded-lg text-gray-400 hover:text-black hover:bg-[#EFEFEF] transition-all text-xs"
                    title={isExpanded ? 'Hide preview' : 'View preview snippet'}
                  >
                    {isExpanded ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>

                  <button
                    type="button"
                    onClick={() => handleDelete(file.name)}
                    disabled={isDeleting}
                    className="p-1.5 rounded-lg text-gray-400 hover:text-red-600 hover:bg-red-50 transition-all text-xs"
                    title="Remove file from data/raw"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Preview Snippet */}
              {isExpanded && (
                <div className="mt-3 pt-3 border-t border-[#EDEDED] text-xs text-gray-600 bg-[#F9F9F9] p-3 rounded-lg font-mono leading-relaxed wrap-break-word">
                  {file.preview || '(Empty preview)'}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
