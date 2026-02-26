import { Activity, Cpu, Database, MemoryStick } from 'lucide-react';
import VoiceIndicator from './VoiceIndicator';
import { JarvisStatus } from '@/hooks/useJarvisState';

interface Props {
  status: JarvisStatus;
  stats: { cpu: number; ram: number; docker: string };
  onShortcut: (cmd: string) => void;
  onPushToTalk: () => void;
}

const shortcuts = ['open vscode', 'docker status', 'show cpu usage', 'restart nginx', 'check logs nginx'];

export default function Sidebar({ status, stats, onShortcut, onPushToTalk }: Props) {
  return (
    <aside className="glass-panel flex h-full flex-col gap-4 p-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">Jarvis Core</h2>
        <span className="text-xs uppercase tracking-widest text-slate-300">{status}</span>
      </div>

      <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
        <div className="mb-3 flex items-center gap-2 text-slate-200">
          <Activity size={16} /> Status
        </div>
        <div className="flex justify-center py-2">
          <VoiceIndicator status={status} listening={status === 'listening'} onPushToTalk={onPushToTalk} />
        </div>
      </div>

      <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm">
        <div className="mb-3 font-medium text-slate-200">System Metrics</div>
        <div className="space-y-3">
          <div className="metric"><Cpu size={14} /> CPU <strong>{stats.cpu.toFixed(1)}%</strong></div>
          <div className="metric"><MemoryStick size={14} /> RAM <strong>{stats.ram.toFixed(1)}%</strong></div>
          <div className="metric"><Database size={14} /> Docker <strong>{stats.docker}</strong></div>
        </div>
      </div>

      <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
        <div className="mb-3 text-sm font-medium text-slate-200">Quick Commands</div>
        <div className="space-y-2">
          {shortcuts.map((cmd) => (
            <button key={cmd} className="shortcut-btn" onClick={() => onShortcut(cmd)}>
              {cmd}
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
}
