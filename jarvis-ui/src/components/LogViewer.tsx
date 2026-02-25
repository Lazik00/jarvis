interface Props {
  logs: string[];
}

export default function LogViewer({ logs }: Props) {
  return (
    <div className="terminal h-56 overflow-y-auto rounded-xl border border-white/10 bg-black/40 p-3 font-mono text-xs text-emerald-300">
      {logs.length === 0 ? <p className="text-slate-500">No logs yet.</p> : logs.map((line, idx) => <p key={`${idx}-${line}`}>{line}</p>)}
    </div>
  );
}
