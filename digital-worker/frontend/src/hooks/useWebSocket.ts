import { useEffect, useRef, useCallback, useState } from 'react';

type MessageHandler = (data: any) => void;
type ChannelType = 'chat' | 'notification' | 'dashboard';

interface UseWebSocketOptions {
  channels?: ChannelType[];
  onMessage?: MessageHandler;
  onNotification?: MessageHandler;
  onDashboard?: MessageHandler;
  enabled?: boolean;
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const {
    channels = ['notification'],
    onMessage,
    onNotification,
    onDashboard,
    enabled = true,
  } = options;

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [connected, setConnected] = useState(false);
  const reconnectAttempt = useRef(0);
  const maxReconnectAttempts = 10;
  const baseDelay = 1000;

  const connect = useCallback(() => {
    if (!enabled) return;
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const wsUrl = import.meta.env.VITE_WS_URL || '/ws';
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const url = `${protocol}//${host}${wsUrl}?channels=${channels.join(',')}`;

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        reconnectAttempt.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          const channel = data.channel || 'notification';

          switch (channel) {
            case 'chat':
              onMessage?.(data.payload || data);
              break;
            case 'notification':
              onNotification?.(data.payload || data);
              break;
            case 'dashboard':
              onDashboard?.(data.payload || data);
              break;
            default:
              onMessage?.(data);
          }
        } catch {
          onMessage?.(event.data);
        }
      };

      ws.onclose = () => {
        setConnected(false);
        wsRef.current = null;
        attemptReconnect();
      };

      ws.onerror = () => {
        ws.close();
      };
    } catch {
      attemptReconnect();
    }
  }, [enabled, channels.join(',')]);

  const attemptReconnect = useCallback(() => {
    if (reconnectAttempt.current >= maxReconnectAttempts) return;
    const delay = Math.min(baseDelay * Math.pow(2, reconnectAttempt.current), 30000);
    reconnectAttempt.current += 1;

    reconnectTimeoutRef.current = setTimeout(() => {
      connect();
    }, delay);
  }, [connect]);

  const sendMessage = useCallback((data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(typeof data === 'string' ? data : JSON.stringify(data));
    }
  }, []);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    reconnectAttempt.current = maxReconnectAttempts;
    wsRef.current?.close();
    wsRef.current = null;
    setConnected(false);
  }, []);

  useEffect(() => {
    if (enabled) {
      connect();
    }
    return () => {
      disconnect();
    };
  }, [enabled, connect, disconnect]);

  return {
    connected,
    sendMessage,
    disconnect,
    reconnect: connect,
  };
}
