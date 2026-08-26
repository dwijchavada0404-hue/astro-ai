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
};

const apiUrl = (
  import.meta.env.VITE_ASTROAI_API_URL || "https://astro-ai-production-54a7.up.railway.app"
).replace(/\/$/, "");

export async function apiRequest<T>(path: string, token: string, init: RequestInit = {}): Promise<T> {
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
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${apiUrl}/health`);
    return response.ok;
  } catch {
    return false;
  }
}
