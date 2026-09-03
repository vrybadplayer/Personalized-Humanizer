import React from 'react';
import { AlertTriangle, Trash2, X, Loader2 } from 'lucide-react';

interface ResetConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirmReset: () => Promise<void>;
  isResetting: boolean;
}

export const ResetConfirmModal: React.FC<ResetConfirmModalProps> = ({
  isOpen,
  onClose,
  onConfirmReset,
  isResetting,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="w-full max-w-md bg-white border border-[#EDEDED] rounded-2xl shadow-2xl overflow-hidden">
        <div className="p-6 sm:p-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-full bg-red-50 border border-red-200 text-red-600 flex items-center justify-center shrink-0">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-medium text-[#1A1A1A]">Reset Memory & Clear Data</h3>
              <p className="text-xs text-gray-400">Irreversible workspace cleanup</p>
            </div>
          </div>

          <p className="text-xs sm:text-sm text-gray-500 mb-4 leading-relaxed">
            This action will remove all uploaded user handwriting documents and purge all generated data folders:
          </p>

          <div className="bg-[#FAFAFA] rounded-xl p-3.5 border border-[#EEEEEE] mb-5 space-y-1.5 font-mono text-xs text-gray-600">
            <div className="flex items-center gap-2">
              <span className="text-red-500">✕</span>
              <span>data/raw/ <span className="text-gray-400">(uploaded writing samples)</span></span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-red-500">✕</span>
              <span>data/clean/ <span className="text-gray-400">(sanitized text corpus)</span></span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-red-500">✕</span>
              <span>data/profiles/ <span className="text-gray-400">(style_profile.json)</span></span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-red-500">✕</span>
              <span>data/output/ <span className="text-gray-400">(SKILL.md)</span></span>
            </div>
          </div>

          <div className="flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              disabled={isResetting}
              className="px-4 py-2 text-xs font-medium text-gray-500 hover:text-black"
            >
              Cancel
            </button>
            <button
              id="confirm-reset-btn"
              type="button"
              onClick={onConfirmReset}
              disabled={isResetting}
              className="px-4 py-2.5 rounded-xl text-xs font-medium bg-red-600 hover:bg-red-700 text-white transition-all flex items-center gap-1.5"
            >
              {isResetting ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Clearing Workspaces...</span>
                </>
              ) : (
                <>
                  <Trash2 className="w-3.5 h-3.5" />
                  <span>Confirm Reset</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
