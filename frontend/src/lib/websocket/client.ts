type Handler = (data: unknown) => void;

class WsClient {
  private ws: WebSocket | null = null;
  private apiKey: string | null = null;
  private verbosity = 2;
  private handlers = new Map<string, Set<Handler>>();
  private messageHandlers = new Set<(msg: unknown) => void>();

  setApiKey(key: string | null): void {
    this.apiKey = key;
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  setVerbosity(level: number): void {
    this.verbosity = level;
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'verbosity', level }));
    }
  }

  connect(experimentId: string, verbosity?: number): void {
    if (verbosity !== undefined) this.verbosity = verbosity;
    const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = import.meta.env.VITE_WS_HOST || window.location.host;
    const q = new URLSearchParams({ verbosity: String(this.verbosity) });
    if (this.apiKey) q.set('api_key', this.apiKey);
    const url = `${proto}//${host}/ws/scan/${experimentId}?${q}`;
    try {
      this.ws = new WebSocket(url);
      this.ws.onmessage = (ev) => {
        try {
          const data = JSON.parse(ev.data as string) as unknown;
          this.messageHandlers.forEach((h) => h(data));
          const t = (data as { type?: string })?.type;
          if (t) this.handlers.get(t)?.forEach((h) => h(data));
        } catch {
          /* ignore */
        }
      };
    } catch {
      this.ws = null;
    }
  }

  disconnect(): void {
    this.ws?.close();
    this.ws = null;
  }

  onMessage(cb: (msg: unknown) => void): () => void {
    this.messageHandlers.add(cb);
    return () => this.messageHandlers.delete(cb);
  }

  on(event: string, handler: Handler): void {
    if (!this.handlers.has(event)) this.handlers.set(event, new Set());
    this.handlers.get(event)!.add(handler);
  }

  off(event: string, handler: Handler): void {
    this.handlers.get(event)?.delete(handler);
  }
}

export const wsClient = new WsClient();
