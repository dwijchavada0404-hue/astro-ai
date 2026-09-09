import { frontendRuntime } from "./runtime-config";

export type BirthProfile = {
  profile_id: string;
  label: string;
  birth_date: string;
  birth_time: string;
  place: string;
  is_default: boolean;
};

export type Conversation = {
  conversation_id: string;
  title: string;
  birth_profile_id: string | null;
  updated_at?: string;
};

export type Message = {
  message_id: string;
  role: "user" | "assistant";
  content: string | null;
  domain?: string | null;
  payload?: unknown;
};

export const apiUrl = frontendRuntime.apiUrl;
export const MIN_READING_DURATION_MS = 8000;

function sleep(milliseconds: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
}

export async function apiRequest<T>(path: string, token: string, init: RequestInit = {}): Promise<T> {
  const readingStartedAt = path.endsWith("/ask") ? Date.now() : null;
  const response = await fetch(`${apiUrl}${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      ...init.headers,
    },
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(payload?.detail || `AstroAI request failed (${response.status}).`);
  }
  if (readingStartedAt !== null) {
    const remaining = MIN_READING_DURATION_MS - (Date.now() - readingStartedAt);
    if (remaining > 0) await sleep(remaining);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export async function apiDownload(path: string, token: string): Promise<Blob> {
  const response = await fetch(`${apiUrl}${path}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(payload?.detail || `AstroAI request failed (${response.status}).`);
  }
  return response.blob();
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${apiUrl}/health`);
    return response.ok;
  } catch {
    return false;
  }
}
