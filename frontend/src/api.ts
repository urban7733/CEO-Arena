import type { ChatResponse, SpeakerId } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000/api";

interface ChatHistoryTurn {
  role: "user" | "assistant";
  content: string;
}

export async function sendMessage(
  speaker: SpeakerId,
  message: string,
  history?: ChatHistoryTurn[]
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ speaker, message, history }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Server error" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

export async function sendDebate(
  message: string,
  speakers?: SpeakerId[]
): Promise<ChatResponse[]> {
  const res = await fetch(`${API_BASE}/debate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, speakers }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Server error" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/health`);
    const data = await res.json();
    return data.engine_loaded === true;
  } catch {
    return false;
  }
}
