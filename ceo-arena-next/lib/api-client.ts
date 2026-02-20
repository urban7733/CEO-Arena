import type { ChatResponse, SpeakerId } from "@/types";

interface ChatHistoryTurn {
  role: "user" | "assistant";
  content: string;
}

export async function sendMessage(
  speaker: SpeakerId,
  message: string,
  history?: ChatHistoryTurn[],
): Promise<ChatResponse> {
  let res: Response;
  try {
    res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ speaker, message, history }),
    });
  } catch {
    throw new Error("Failed to reach API. Check your connection.");
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Server error" })) as { detail?: string };
    throw new Error(err.detail ?? `HTTP ${res.status}`);
  }

  return res.json() as Promise<ChatResponse>;
}

export async function sendDebate(
  message: string,
  speakers?: SpeakerId[],
): Promise<ChatResponse[]> {
  let res: Response;
  try {
    res = await fetch("/api/debate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, speakers }),
    });
  } catch {
    throw new Error("Failed to reach API. Check your connection.");
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Server error" })) as { detail?: string };
    throw new Error(err.detail ?? `HTTP ${res.status}`);
  }

  return res.json() as Promise<ChatResponse[]>;
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch("/api/health");
    const data = await res.json() as { status?: string };
    return data.status === "ok";
  } catch {
    return false;
  }
}
