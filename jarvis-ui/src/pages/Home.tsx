import { Settings, X } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import ChatPanel from '@/components/ChatPanel';
import DevOpsPanel from '@/components/DevOpsPanel';
import Sidebar from '@/components/Sidebar';
import { JarvisStatus, useJarvisState } from '@/hooks/useJarvisState';

function SettingsModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [language, setLanguage] = useState('EN');
  const [voice, setVoice] = useState('en_US-lessac-medium');
  const [autoListen, setAutoListen] = useState(true);

  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-6">
      <div className="glass-panel w-full max-w-md p-5">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-white">Settings</h3>
          <button onClick={onClose} className="icon-btn"><X size={16} /></button>
        </div>
        <div className="space-y-3 text-sm text-slate-100">
          <label className="field">Language
            <select value={language} onChange={(e) => setLanguage(e.target.value)} className="input">
              <option>EN</option>
              <option>UZ</option>
            </select>
          </label>
          <label className="field">Voice
            <select value={voice} onChange={(e) => setVoice(e.target.value)} className="input">
              <option>en_US-lessac-medium</option>
              <option>uz_UZ-voice</option>
            </select>
          </label>
          <label className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 px-3 py-2">
            Auto Listen
            <input type="checkbox" checked={autoListen} onChange={(e) => setAutoListen(e.target.checked)} />
          </label>
        </div>
      </div>
    </div>
  );
}

export default function Home() {
  const jarvis = useJarvisState();
  const [settingsOpen, setSettingsOpen] = useState(false);

  useEffect(() => {
    const i = setInterval(() => {
      jarvis.sendUserMessage('show cpu usage');
    }, 60000);
    return () => clearInterval(i);
  }, []);

  const statusLabel = useMemo(() => {
    if (!jarvis.connected) return 'offline';
    return jarvis.status;
  }, [jarvis.connected, jarvis.status]);

  const pushToTalk = () => {
    jarvis.setStatus('listening' as JarvisStatus);
    jarvis.setTranscript('Listening for command...');
  };

  return (
    <main className="min-h-screen bg-bg p-4 text-slate-100">
      <div className="mx-auto mb-3 flex max-w-[1600px] items-center justify-between px-1">
        <h1 className="text-2xl font-bold tracking-wide text-white">JARVIS DESKTOP</h1>
        <div className="flex items-center gap-2">
          <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs uppercase tracking-widest">{statusLabel}</span>
          <button className="icon-btn" onClick={() => setSettingsOpen(true)}><Settings size={16} /></button>
        </div>
      </div>

      <div className="mx-auto grid h-[calc(100vh-6rem)] max-w-[1600px] grid-cols-12 gap-4">
        <div className="col-span-3">
          <Sidebar status={jarvis.status} stats={jarvis.stats} onShortcut={jarvis.sendUserMessage} onPushToTalk={pushToTalk} />
        </div>
        <div className="col-span-6">
          <ChatPanel
            status={jarvis.status}
            transcript={jarvis.transcript}
            messages={jarvis.messages}
            onSend={jarvis.sendUserMessage}
          />
        </div>
        <div className="col-span-3">
          <DevOpsPanel containers={jarvis.containers} logs={jarvis.logs} onQuickAction={jarvis.sendUserMessage} />
        </div>
      </div>

      <SettingsModal open={settingsOpen} onClose={() => setSettingsOpen(false)} />

      <div className="fixed bottom-4 right-4 z-50 space-y-2">
        {jarvis.toasts.slice(-4).map((toast) => (
          <div key={toast.id} className="glass-panel flex min-w-64 items-center justify-between gap-3 p-3 text-sm">
            <span>{toast.message}</span>
            <button onClick={() => jarvis.dismissToast(toast.id)}><X size={14} /></button>
          </div>
        ))}
      </div>
    </main>
  );
}
