import type { ChatSession, Message, SpeakerId } from "./types";

const STORAGE_KEY = "ceo-arena-history";

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export function loadSessions(): ChatSession[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    return JSON.parse(raw) as ChatSession[];
  } catch {
    return [];
  }
}

export function saveSessions(sessions: ChatSession[]): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
}

export function createSession(speaker: SpeakerId): ChatSession {
  return {
    id: generateId(),
    speaker,
    messages: [],
    createdAt: Date.now(),
    title: "New Chat",
  };
}

export function addMessage(
  session: ChatSession,
  role: "user" | "assistant",
  content: string,
  speaker?: SpeakerId
): Message {
  const msg: Message = {
    id: generateId(),
    role,
    content,
    speaker,
    timestamp: Date.now(),
  };
  session.messages.push(msg);

  // Auto-title from first user message
  if (session.messages.length === 1 && role === "user") {
    session.title = content.slice(0, 50) + (content.length > 50 ? "..." : "");
  }

  return msg;
}
