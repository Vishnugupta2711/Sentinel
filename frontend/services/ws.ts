export type WSStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

export class WebSocketManager {
  private url: string;
  private ws: WebSocket | null = null;
  private reconnectInterval = 3000;
  private maxReconnectInterval = 30000;
  private currentReconnectInterval: number;
  private reconnectAttempts = 0;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private onMessageCallback: (data: any) => void;
  private onStatusChange?: (status: WSStatus) => void;
  private intentionalClose = false;

  constructor(
    url: string,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    onMessage: (data: any) => void,
    onStatusChange?: (status: WSStatus) => void
  ) {
    this.url = url;
    this.onMessageCallback = onMessage;
    this.onStatusChange = onStatusChange;
    this.currentReconnectInterval = this.reconnectInterval;
  }

  connect() {
    this.intentionalClose = false;
    this.onStatusChange?.('connecting');
    console.log(`[WS] Attempting to connect to ${this.url}`);

    try {
      this.ws = new WebSocket(this.url);
    } catch (e) {
      console.error(`[WS] Failed to instantiate WebSocket for ${this.url}:`, e);
      this.onStatusChange?.('error');
      this.scheduleReconnect();
      return;
    }

    this.ws.onopen = () => {
      console.log(`[WS] Connected to ${this.url}`);
      this.reconnectAttempts = 0;
      this.currentReconnectInterval = this.reconnectInterval;
      this.onStatusChange?.('connected');
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.onMessageCallback(data);
      } catch (err) {
        console.error(`[WS] Failed to parse message from ${this.url}`, err);
      }
    };

    this.ws.onclose = () => {
      if (this.intentionalClose) return;
      console.log(`[WS] Disconnected from ${this.url}. Reconnecting...`);
      this.onStatusChange?.('disconnected');
      this.scheduleReconnect();
    };

    this.ws.onerror = (err) => {
      console.error(`[WS] Error on ${this.url}:`, err);
      this.onStatusChange?.('error');
      this.ws?.close();
    };
  }

  private scheduleReconnect() {
    if (this.intentionalClose) return;
    this.reconnectAttempts++;
    // Exponential backoff capped at maxReconnectInterval
    this.currentReconnectInterval = Math.min(
      this.reconnectInterval * Math.pow(1.5, this.reconnectAttempts),
      this.maxReconnectInterval
    );
    setTimeout(() => this.connect(), this.currentReconnectInterval);
  }

  disconnect() {
    this.intentionalClose = true;
    if (this.ws) {
      this.ws.onclose = null;
      this.ws.close();
      this.ws = null;
    }
    this.onStatusChange?.('disconnected');
  }
}
