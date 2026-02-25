import LogViewer from './LogViewer';

interface Props {
  containers: Array<{ name: string; status: string }>;
  logs: string[];
  onQuickAction: (cmd: string) => void;
}

export default function DevOpsPanel({ containers, logs, onQuickAction }: Props) {
  return (
    <section className="glass-panel flex h-full flex-col gap-4 p-4">
      <h2 className="text-lg font-semibold text-white">DevOps Control</h2>

      <div className="rounded-2xl border border-white/10 bg-white/5 p-3">
        <div className="mb-2 text-sm font-medium text-slate-200">Docker Containers</div>
        <div className="space-y-2 text-sm">
          {containers.length === 0 ? (
            <p className="text-slate-400">No container data</p>
          ) : (
            containers.map((container) => (
              <div key={container.name} className="metric">
                <span>{container.name}</span>
                <span className="text-slate-300">{container.status}</span>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <button className="secondary-btn" onClick={() => onQuickAction('docker status')}>docker ps</button>
        <button className="secondary-btn" onClick={() => onQuickAction('docker logs')}>docker logs</button>
        <button className="secondary-btn" onClick={() => onQuickAction('show cpu usage')}>cpu usage</button>
        <button className="secondary-btn" onClick={() => onQuickAction('show ram usage')}>ram usage</button>
      </div>

      <div>
        <div className="mb-2 text-sm font-medium text-slate-200">Logs Preview</div>
        <LogViewer logs={logs} />
      </div>
    </section>
  );
}
