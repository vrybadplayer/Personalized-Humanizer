import React, { useState, useEffect, useRef } from 'react';
import confetti from 'canvas-confetti';
import { Header } from './components/Header';
import { DropzoneUpload } from './components/DropzoneUpload';
import { RawFilesList } from './components/RawFilesList';
import { PipelineRunner } from './components/PipelineRunner';
import { SettingsModal } from './components/SettingsModal';
import { ResetConfirmModal } from './components/ResetConfirmModal';
import { SkillPreviewModal } from './components/SkillPreviewModal';
import { LogsModal } from './components/LogsModal';
import { AppSettings, RawFileSummary, DataFolderStatus, PipelineState, SetupStatus } from './types';

export default function App() {
  const [settings, setSettings] = useState<AppSettings | null>(null);
  const [files, setFiles] = useState<RawFileSummary[]>([]);
  const [folderStatus, setFolderStatus] = useState<DataFolderStatus | null>(null);
  const [setupStatus, setSetupStatus] = useState<SetupStatus | null>(null);
  const [pipelineState, setPipelineState] = useState<PipelineState>({
    status: 'idle',
    currentStage: null,
    logs: [],
    lastError: null,
    parsedError: null,
    startedAt: null,
    finishedAt: null,
    profile: null,
    skillContent: null,
  });

  const [isUploading, setIsUploading] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isResetOpen, setIsResetOpen] = useState(false);
  const [isSkillPreviewOpen, setIsSkillPreviewOpen] = useState(false);
  const [isLogsOpen, setIsLogsOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const prevPipelineStatus = useRef(pipelineState.status);
  const pollingTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Show transient toast
  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  // Initial Data Fetching & Setup Verification
  const fetchAllData = async () => {
    try {
      // 1. Setup Status
      const setupRes = await fetch('/api/setup/status');
      if (setupRes.ok) {
        const data = await setupRes.json();
        setSetupStatus(data);
        if (!data.isSetupComplete) {
          // Auto run setup orchestrator
          const runRes = await fetch('/api/setup/run', { method: 'POST' });
          if (runRes.ok) {
            const runData = await runRes.json();
            setSetupStatus(runData);
          }
        }
      }

      // 2. Settings
      const settingsRes = await fetch('/api/settings');
      if (settingsRes.ok) {
        const data = await settingsRes.json();
        setSettings(data.settings);
      }

      // 3. Files & Folders
      const filesRes = await fetch('/api/files');
      if (filesRes.ok) {
        const data = await filesRes.json();
        setFiles(data.files || []);
        setFolderStatus(data.status || null);
      }

      // 4. Pipeline State
      const pipeRes = await fetch('/api/pipeline/status');
      if (pipeRes.ok) {
        const data = await pipeRes.json();
        if (data.state) {
          setPipelineState(data.state);
        }
      }
    } catch (err) {
      console.error('Error initializing app state:', err);
    }
  };

  useEffect(() => {
    fetchAllData();
  }, []);

  // Download SKILL.md helper
  const triggerSkillDownload = () => {
    const link = document.createElement('a');
    link.href = '/api/pipeline/download';
    link.download = 'SKILL.md';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Handle pipeline polling when running
  useEffect(() => {
    if (pipelineState.status === 'running') {
      pollingTimerRef.current = setInterval(async () => {
        try {
          const res = await fetch('/api/pipeline/status');
          if (res.ok) {
            const data = await res.json();
            setPipelineState(data.state);
          }
        } catch (e) {
          console.warn('Status poll error:', e);
        }
      }, 400);
    } else {
      if (pollingTimerRef.current) {
        clearInterval(pollingTimerRef.current);
        pollingTimerRef.current = null;
      }
    }

    return () => {
      if (pollingTimerRef.current) {
        clearInterval(pollingTimerRef.current);
      }
    };
  }, [pipelineState.status]);

  // Detect completion transition -> Auto Download SKILL.md per specification
  useEffect(() => {
    if (prevPipelineStatus.current === 'running' && pipelineState.status === 'completed') {
      try {
        confetti({
          particleCount: 80,
          spread: 60,
          origin: { y: 0.6 },
          colors: ['#6366f1', '#a855f7', '#10b981', '#38bdf8']
        });
      } catch {
        // Safe fallback
      }

      showToast('Pipeline completed! Automatically downloading SKILL.md...');
      triggerSkillDownload();

      // Refresh files and status
      fetch('/api/files')
        .then((r) => r.json())
        .then((d) => {
          setFiles(d.files || []);
          setFolderStatus(d.status || null);
        });
    }
    prevPipelineStatus.current = pipelineState.status;
  }, [pipelineState.status]);

  // Upload file handler
  const handleFileUpload = async (file: File) => {
    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/files/upload', {
        method: 'POST',
        body: formData,
      });

      if (res.ok) {
        const data = await res.json();
        setFiles(data.files || []);
        showToast(`Uploaded ${file.name} to data/raw`);
      } else {
        const err = await res.json();
        showToast(`Upload failed: ${err.error || 'Unknown error'}`);
      }
    } catch (e) {
      showToast('File upload failed.');
    } finally {
      setIsUploading(false);
    }
  };

  // Paste text sample handler
  const handlePasteText = async (title: string, text: string) => {
    try {
      const res = await fetch('/api/files/sample', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, text }),
      });

      if (res.ok) {
        const data = await res.json();
        setFiles(data.files || []);
        showToast(`Writing sample saved to data/raw`);
      } else {
        const err = await res.json();
        showToast(`Failed: ${err.error || 'Unknown error'}`);
      }
    } catch (e) {
      showToast('Could not save sample.');
    }
  };

  // Delete individual file
  const handleDeleteFile = async (filename: string) => {
    try {
      const res = await fetch(`/api/files/item/${encodeURIComponent(filename)}`, {
        method: 'DELETE',
      });
      if (res.ok) {
        const data = await res.json();
        setFiles(data.files || []);
        showToast(`Removed ${filename}`);
      }
    } catch (e) {
      showToast('Could not delete file.');
    }
  };

  // Clear all data (reset memory)
  const handleClearAllData = async () => {
    setIsResetting(true);
    try {
      const res = await fetch('/api/files/clear', { method: 'DELETE' });
      if (res.ok) {
        const data = await res.json();
        setFiles([]);
        setFolderStatus(data.status || null);
        setPipelineState({
          status: 'idle',
          currentStage: null,
          logs: [],
          lastError: null,
          parsedError: null,
          startedAt: null,
          finishedAt: null,
          profile: null,
          skillContent: null,
        });
        setIsResetOpen(false);
        showToast('Memory reset: data/raw, clean, profiles, and output cleared.');
      }
    } catch (e) {
      showToast('Reset failed.');
    } finally {
      setIsResetting(false);
    }
  };

  // Save settings
  const handleSaveSettings = async (newSettings: AppSettings) => {
    try {
      const res = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newSettings),
      });
      if (res.ok) {
        const data = await res.json();
        setSettings(data.settings);
        showToast('Settings saved directly to backend/config/settings.py');
      }
    } catch (e) {
      showToast('Error saving settings.');
    }
  };

  // Run pipeline
  const handleRunPipeline = async () => {
    try {
      const res = await fetch('/api/pipeline/run', { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setPipelineState(data.state);
      }
    } catch (e) {
      showToast('Failed to trigger pipeline.');
    }
  };

  return (
    <div className="min-h-screen bg-[#FAFAFA] text-[#1A1A1A] flex flex-col font-sans selection:bg-neutral-200 selection:text-black">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 px-4 py-2.5 rounded-xl bg-black text-xs font-medium text-white shadow-2xl animate-in slide-in-from-bottom-2 fade-in">
          {toastMessage}
        </div>
      )}

      {/* Header */}
      <Header
        setupStatus={setupStatus}
        pipelineState={pipelineState}
        onOpenSettings={() => setIsSettingsOpen(true)}
        onOpenReset={() => setIsResetOpen(true)}
        onOpenLogs={() => setIsLogsOpen(true)}
      />

      {/* Main Content Dashboard */}
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 sm:px-6 py-8 sm:py-10 space-y-8">
        {/* Intro Tagline */}
        <div className="text-center max-w-xl mx-auto space-y-2">
          <h2 className="text-2xl sm:text-3xl font-light tracking-tight text-[#1A1A1A]">
            Humanize AI with Authentic Stylometry
          </h2>
          <p className="text-xs sm:text-sm text-gray-400 leading-relaxed">
            Upload your personal handwriting transcripts or writing samples. The pipeline computes burstiness, sentence deviations, and Anti-AI rules, packaging them into <span className="font-mono text-neutral-800">SKILL.md</span>.
          </p>
        </div>

        {/* Upload Section */}
        <section className="space-y-4">
          <DropzoneUpload
            onFileUpload={handleFileUpload}
            onPasteText={handlePasteText}
            isUploading={isUploading}
          />
          <RawFilesList files={files} onDeleteFile={handleDeleteFile} />
        </section>

        {/* Pipeline Execution Block */}
        <section>
          <PipelineRunner
            pipelineState={pipelineState}
            settings={settings}
            onRunPipeline={handleRunPipeline}
            onDownloadSkill={triggerSkillDownload}
            onViewSkillModal={() => setIsSkillPreviewOpen(true)}
            onOpenSettings={() => setIsSettingsOpen(true)}
          />
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-[#EDEDED] py-6 text-center text-xs text-gray-400">
        <div className="max-w-4xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>Personalized Humanizer • Minimalist Control Interface</span>
          <span className="font-mono text-[11px] text-gray-400">
            Local VS Code IDE Ready
          </span>
        </div>
      </footer>

      {/* Modals */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        settings={settings}
        onSaveSettings={handleSaveSettings}
      />

      <ResetConfirmModal
        isOpen={isResetOpen}
        onClose={() => setIsResetOpen(false)}
        onConfirmReset={handleClearAllData}
        isResetting={isResetting}
      />

      <SkillPreviewModal
        isOpen={isSkillPreviewOpen}
        onClose={() => setIsSkillPreviewOpen(false)}
        skillContent={pipelineState.skillContent}
        profile={pipelineState.profile}
        onDownload={triggerSkillDownload}
      />

      <LogsModal
        isOpen={isLogsOpen}
        onClose={() => setIsLogsOpen(false)}
        logs={pipelineState.logs}
      />
    </div>
  );
}
