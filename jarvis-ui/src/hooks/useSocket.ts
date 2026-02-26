import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

export type JarvisEvent =
  | { type: 'jarvis_listening'; transcript?: string }
  | { type: 'jarvis_thinking'; text?: string }
  | { type: 'jarvis_reply'; text: string; stream?: boolean }
  | { type: 'system_stats'; cpu: number; ram: number; docker: string }
  | { type: 'docker_update'; containers: Array<{ name: string; status: string }> }
  | { type: 'toast'; level: 'info' | 'success' | 'error'; message: string }
  | { type: 'ready'; message: string }
  | { type: 'response'; text: string }
  | { type: 'processing'; text: string }
  | { type: 'error'; message: string };

const SOCKET_URL = import.meta.env.VITE_JARVIS_WS_URL ?? 'ws://127.0.0.1:8000/ws';

export const useSocket = () => {
  const wsRef = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [events, setEvents] = useState<JarvisEvent[]>([]);

  const connect = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState <= 1) return;
    const ws = new WebSocket(SOCKET_URL);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onerror = () => {
      setConnected(false);
      setEvents((prev) => [...prev, { type: 'toast', level: 'error', message: 'WebSocket connection error' }]);
    };

    ws.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data) as JarvisEvent;
        setEvents((prev) => [...prev.slice(-100), parsed]);
      } catch {
        setEvents((prev) => [...prev, { type: 'toast', level: 'error', message: String(event.data) }]);
      }
    };
  }, []);

  const disconnect = useCallback(() => {
    wsRef.current?.close();
    wsRef.current = null;
    setConnected(false);
  }, []);

  useEffect(() => {
    connect();
    return disconnect;
  }, [connect, disconnect]);

  const sendText = useCallback((text: string) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
    wsRef.current.send(JSON.stringify({ text }));
  }, []);

  return useMemo(
    () => ({ connected, events, sendText, reconnect: connect, disconnect }),
    [connected, events, sendText, connect, disconnect]
  );
};
