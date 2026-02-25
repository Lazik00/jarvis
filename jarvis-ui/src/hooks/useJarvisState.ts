import { useMemo, useState } from 'react';
import { JarvisEvent, useSocket } from './useSocket';

export type JarvisStatus = 'idle' | 'listening' | 'thinking' | 'speaking';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  text: string;
}

export const useJarvisState = () => {
  const socket = useSocket();
  const [status, setStatus] = useState<JarvisStatus>('idle');
  const [transcript, setTranscript] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [logs, setLogs] = useState<string[]>([]);
  const [toasts, setToasts] = useState<Array<{ id: string; level: string; message: string }>>([]);
  const [stats, setStats] = useState({ cpu: 0, ram: 0, docker: 'unknown' });
  const [containers, setContainers] = useState<Array<{ name: string; status: string }>>([]);

  useMemo(() => {
    const latest = socket.events[socket.events.length - 1];
    if (!latest) return;
    processEvent(latest);
  }, [socket.events]);

  const processEvent = (event: JarvisEvent) => {
    switch (event.type) {
      case 'jarvis_listening':
        setStatus('listening');
        setTranscript(event.transcript ?? 'Listening...');
        break;
      case 'jarvis_thinking':
      case 'processing':
        setStatus('thinking');
        break;
      case 'jarvis_reply':
      case 'response':
        setStatus('speaking');
        setMessages((prev) => [...prev, { id: crypto.randomUUID(), role: 'assistant', text: event.text }]);
        setLogs((prev) => [...prev, `[Jarvis] ${event.text}`].slice(-300));
        setTimeout(() => setStatus('idle'), 1200);
        break;
      case 'system_stats':
        setStats({ cpu: event.cpu, ram: event.ram, docker: event.docker });
        break;
      case 'docker_update':
        setContainers(event.containers);
        break;
      case 'toast':
        setToasts((prev) => [...prev, { id: crypto.randomUUID(), level: event.level, message: event.message }]);
        break;
      case 'error':
        setToasts((prev) => [...prev, { id: crypto.randomUUID(), level: 'error', message: event.message }]);
        break;
      default:
        break;
    }
  };

  const sendUserMessage = (text: string) => {
    if (!text.trim()) return;
    setMessages((prev) => [...prev, { id: crypto.randomUUID(), role: 'user', text }]);
    setLogs((prev) => [...prev, `[You] ${text}`].slice(-300));
    setStatus('thinking');
    socket.sendText(text);
  };

  const dismissToast = (id: string) => setToasts((prev) => prev.filter((t) => t.id !== id));

  return {
    ...socket,
    status,
    transcript,
    messages,
    logs,
    stats,
    containers,
    toasts,
    sendUserMessage,
    setStatus,
    setTranscript,
    dismissToast,
  };
};
