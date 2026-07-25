// Backend endpoint config. Reads Vite env (set VITE_API_BASE / VITE_WS_URL in
// Vercel); falls back to local dev defaults. Single source of backend URLs.

export const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000';
export const WS_URL = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:8000/ws/stream';
