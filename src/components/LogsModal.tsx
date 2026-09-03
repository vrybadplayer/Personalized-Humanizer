import React from 'react';
import { Terminal, X, Trash2, Copy, Check } from 'lucide-react';

interface LogsModalProps {
  isOpen: boolean;
  onClose: () => void;
  logs: string[];
}

export const LogsModal: React.FC<LogsModalProps> = ({ isOpen, onClose, logs }) => {
  const [copied, setCopied] = React.useState(false);

  if (!isOpen) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(logs.join('\n'));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="w-full max-w-3xl bg-white border border-[#EDEDED] rounded-2xl shadow-2xl overflow-hidden flex flex-col h-[70vh]">
        <div className="px-6 py-4 border-b border-[#F5F5F5] flex items-center justify-between bg-white">
          <div className="flex items-center gap-2.5">
            <Terminal className="w-4 h-4 text-gray-500" />
            <h3 className="text-sm font-medium text-[#1A1A1A]">Pipeline Execution & Setup Logs</h3>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleCopy}
              className="p-1.5 rounded-lg text-gray-400 hover:text-black hover:bg-[#F5F5F5] transition-colors text-xs flex items-center gap-1"
              title="Copy logs"
            >
              {copied ? <Check className="w-4 h-4 text-green-600" /> : <Copy className="w-4 h-4 text-gray-400" />}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="p-1.5 rounded-lg text-gray-400 hover:text-black hover:bg-[#F5F5F5] transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-5 bg-[#FAFAFA] font-mono text-xs text-neutral-800 space-y-1 select-text">
          {logs.length === 0 ? (
            <p className="text-gray-400 italic">No logs recorded yet. Run the pipeline to view activity stream.</p>
          ) : (
            logs.map((log, index) => (
              <div
                key={index}
                className={`py-0.5 ${
                  log.includes('ERROR')
                    ? 'text-red-600 font-semibold'
                    : log.includes('SKILL.md') || log.includes('Completed')
                    ? 'text-green-700 font-medium'
                    : 'text-gray-700'
                }`}
              >
                {log}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
