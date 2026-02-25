import { FormEvent, useMemo, useState } from 'react';
import clsx from 'clsx';
import { ChatMessage, JarvisStatus } from '@/hooks/useJarvisState';

interface Props {
  status: JarvisStatus;
  transcript: string;
  messages: ChatMessage[];
  onSend: (text: string) => void;
}

export default function ChatPanel({ status, transcript, messages, onSend }: Props) {
  const [input, setInput] = useState('');

  const latestAssistant = useMemo(() => [...messages].reverse().find((m) => m.role === 'assistant'), [messages]);

  const submit = (event: FormEvent) => {
    event.preventDefault();
    onSend(input);
    setInput('');
  };

  return (
    <section className="glass-panel flex h-full flex-col p-4">
      <header className="mb-3 flex items-center justify-between">
        <h2 className="text-xl font-semibold text-white">Conversation</h2>
        <span className="text-xs uppercase tracking-[0.2em] text-slate-300">{status}</span>
      </header>

      <div className="mb-3 min-h-12 rounded-xl border border-cyan-500/20 bg-cyan-500/5 px-3 py-2 text-sm text-cyan-200">
        Live transcript: <span className="opacity-90">{transcript || '...'}</span>
      </div>

      {status === 'listening' && (
        <div className="mb-4 flex h-8 items-end gap-1">
          {[0, 1, 2, 3, 4, 5].map((idx) => (
            <span key={idx} className="wave-bar" style={{ animationDelay: `${idx * 0.08}s` }} />
          ))}
        </div>
      )}

      <div className="chat-scroll flex-1 space-y-3 overflow-y-auto pr-1">
        {messages.map((message) => (
          <div key={message.id} className={clsx('chat-bubble', message.role === 'user' ? 'chat-user' : 'chat-assistant')}>
            {message.text}
          </div>
        ))}

        {status === 'thinking' && <div className="chat-bubble chat-assistant animate-pulse">Jarvis is thinking...</div>}

        {latestAssistant && status === 'speaking' && (
          <div className="text-xs text-emerald-300">Streaming: {latestAssistant.text}</div>
        )}
      </div>

      <form onSubmit={submit} className="mt-4 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="input"
          placeholder="Type a command..."
        />
        <button type="submit" className="primary-btn">
          Send
        </button>
      </form>
    </section>
  );
}
