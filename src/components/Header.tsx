import React from 'react';
import { Sliders, RefreshCw, Trash2, CheckCircle2, AlertCircle, Sparkles, Terminal } from 'lucide-react';
import { SetupStatus, PipelineState } from '../types';

interface HeaderProps {
  setupStatus: SetupStatus | null;
  pipelineState: PipelineState;
  onOpenSettings: () => void;
  onOpenReset: () => void;
  onOpenLogs: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  setupStatus,
  pipelineState,
  onOpenSettings,
  onOpenReset,
  onOpenLogs,
}) => {
  const isRunning = pipelineState.status === 'running';
  const isCompleted = pipelineState.status === 'completed';

  return (
    <header className="border-b border-[#E5E5E5] bg-white sticky top-0 z-30 shadow-[0_1px_2px_rgba(0,0,0,0.02)]">
      <div className="max-w-6xl mx-auto px-6 sm:px-10 py-5 flex items-center justify-between gap-4">
        {/* Brand identity */}
        <div className="flex items-center gap-3.5">
          <div className="relative flex items-center justify-center shrink-0">
            <img
              src="/favicon.png"
              alt="Favicon"
              className="w-10 h-10 sm:w-12 sm:h-12 object-contain"
              onError={(e) => {
                // If favicon.png doesn't exist, hide image and show icon fallback
                (e.target as HTMLElement).style.display = 'none';
              }}
              referrerPolicy="no-referrer"
            />
            <Sparkles className="w-5 h-5 text-neutral-600 hidden group-has-[[style*='display: none']]:block" />
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <h1 className="text-xl sm:text-2xl font-light tracking-tight text-[#1A1A1A]">
                Personalized Humanizer
              </h1>
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-[#F5F5F5] text-neutral-600 border border-[#E5E5E5] uppercase tracking-wider">
                MVC
              </span>
            </div>
            <p className="text-[10px] sm:text-xs text-gray-400 mt-0.5 uppercase tracking-widest font-mono">
              Authentic Stylometric Injection
            </p>
          </div>
        </div>

        {/* Global Controls & Status */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Setup Health Pill */}
          <div className="hidden md:flex items-center">
            {setupStatus?.isSetupComplete ? (
              <span className="flex items-center gap-2 text-xs font-medium text-green-700 bg-green-50 px-3 py-1 rounded-full border border-green-200/80">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                <span>Orchestrator Active</span>
              </span>
            ) : (
              <span className="flex items-center gap-2 text-xs font-medium text-amber-700 bg-amber-50 px-3 py-1 rounded-full border border-amber-200/80">
                <span className="w-2 h-2 bg-amber-500 rounded-full animate-pulse"></span>
                <span>Auto-Configuring</span>
              </span>
            )}
          </div>

          {/* Activity Status */}
          {isRunning && (
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-neutral-100 border border-neutral-200 text-xs text-black font-medium animate-pulse">
              <RefreshCw className="w-3.5 h-3.5 animate-spin text-black" />
              <span>Analyzing Style Matrix...</span>
            </div>
          )}

          {/* Terminal Logs Toggle */}
          <button
            id="view-terminal-logs-btn"
            onClick={onOpenLogs}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-gray-600 bg-[#F9F9F9] hover:bg-[#F0F0F0] hover:text-black border border-[#EDEDED] transition-all"
            title="View Pipeline Orchestrator Logs"
          >
            <Terminal className="w-3.5 h-3.5 text-gray-400" />
            <span className="hidden sm:inline">Logs</span>
          </button>

          {/* Settings Button */}
          <button
            id="open-settings-btn"
            onClick={onOpenSettings}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-medium text-gray-700 bg-[#F9F9F9] hover:bg-[#F0F0F0] hover:text-black border border-[#EDEDED] transition-all"
          >
            <Sliders className="w-3.5 h-3.5 text-gray-500" />
            <span>Config</span>
          </button>

          {/* Reset Memory / Clear Files Button */}
          <button
            id="clear-data-btn"
            onClick={onOpenReset}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-red-500 bg-red-50/50 hover:bg-red-50 hover:text-red-700 border border-red-200/70 transition-all"
            title="Reset Memory & Clear data/raw, clean, profiles, output"
          >
            <Trash2 className="w-3.5 h-3.5 text-red-400" />
            <span className="hidden sm:inline">Reset Memory</span>
          </button>
        </div>
      </div>
    </header>
  );
};
