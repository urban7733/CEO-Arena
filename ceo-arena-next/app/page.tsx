"use client";

import { useState, useCallback, useEffect } from "react";
import type { ChatSession, SpeakerId } from "@/types";
import { sendMessage, checkHealth } from "@/lib/api-client";
import { loadSessions, saveSessions, createSession, addMessage } from "@/lib/store";
import { SPEAKERS } from "@/lib/constants";
import { ChatArea } from "./components/ChatArea";
import { ChatInput } from "./components/ChatInput";
import { Sidebar } from "./components/Sidebar";
import { Header } from "./components/Header";

const MIN_REPLY_DELAY_MS: Record<SpeakerId, number> = {
  elon_musk: 450,
  sam_altman: 700,
  dario_amodei: 950,
  mark_zuckerberg: 1200,
};

const COMPLEX_REPLY_BOOST_MS: Record<SpeakerId, number> = {
  elon_musk: 160,
  sam_altman: 220,
  dario_amodei: 260,
  mark_zuckerberg: 380,
};

const COMPLEX_PROMPT_RE =
  /\b(why|how|compare|tradeoff|strategy|architecture|roadmap|details?|deep|step by step|warum|wieso|ausf[uü]hrlich|analyse|plan)\b/i;

function isComplexPrompt(text: string): boolean {
  const wordCount = text.trim().split(/\s+/).filter(Boolean).length;
  return wordCount >= 18 || COMPLEX_PROMPT_RE.test(text);
}

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export default function Home() {
  const [sessions, setSessions] = useState<ChatSession[]>(() => loadSessions());
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [selectedSpeakerId, setSelectedSpeakerId] = useState<SpeakerId>("elon_musk");
  const [isLoading, setIsLoading] = useState(false);
  const [lastPromptComplex, setLastPromptComplex] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [apiReady, setApiReady] = useState<boolean | null>(null);

  const activeSession = sessions.find((s) => s.id === activeSessionId) ?? null;
  const activeSpeaker = activeSession
    ? SPEAKERS.find((s) => s.id === activeSession.speaker) ?? SPEAKERS[0]!
    : SPEAKERS.find((s) => s.id === selectedSpeakerId) ?? SPEAKERS[0]!;

  useEffect(() => {
    let cancelled = false;

    const ping = async () => {
      const isHealthy = await checkHealth();
      if (!cancelled) setApiReady(isHealthy);
    };

    void ping();
    const timer = setInterval(() => void ping(), 15000);

    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, []);

  const updateSessions = useCallback(
    (updater: (prev: ChatSession[]) => ChatSession[]) => {
      setSessions((prev) => {
        const next = updater(prev);
        saveSessions(next);
        return next;
      });
    },
    [],
  );

  const createNewSession = useCallback(
    (speakerId: SpeakerId) => {
      const session = createSession(speakerId);
      updateSessions((prev) => [session, ...prev]);
      setActiveSessionId(session.id);
      return session;
    },
    [updateSessions],
  );

  const handleSend = useCallback(
    async (text: string) => {
      let session = activeSession;
      if (!session) {
        session = createNewSession(selectedSpeakerId);
      }

      addMessage(session, "user", text);
      updateSessions((prev) =>
        prev.map((s) => (s.id === session.id ? { ...session } : s)),
      );

      const history = session.messages
        .slice(0, -1)
        .filter((m) => (m.role === "user" || m.role === "assistant") && !m.content.startsWith("Error:"))
        .slice(-12)
        .map((m) => ({ role: m.role, content: m.content }));

      setLastPromptComplex(isComplexPrompt(text));
      setIsLoading(true);
      try {
        const requestStartedAt = Date.now();
        const res = await sendMessage(session.speaker, text, history);
        const baseDelay = MIN_REPLY_DELAY_MS[session.speaker] ?? 650;
        const boost = isComplexPrompt(text) ? (COMPLEX_REPLY_BOOST_MS[session.speaker] ?? 0) : 0;
        const minDelay = baseDelay + boost;
        const elapsed = Date.now() - requestStartedAt;
        if (elapsed < minDelay) {
          await sleep(minDelay - elapsed);
        }
        addMessage(session, "assistant", res.message, session.speaker);
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : "Something went wrong";
        addMessage(session, "assistant", `Error: ${errorMsg}`);
      } finally {
        setIsLoading(false);
        updateSessions((prev) =>
          prev.map((s) => (s.id === session.id ? { ...session } : s)),
        );
      }
    },
    [activeSession, createNewSession, selectedSpeakerId, updateSessions],
  );

  const handleSelectSession = useCallback(
    (sessionId: string) => {
      const session = sessions.find((s) => s.id === sessionId);
      if (session) setSelectedSpeakerId(session.speaker);
      setActiveSessionId(sessionId);
      setSidebarOpen(false);
    },
    [sessions],
  );

  const handleDeleteSession = useCallback(
    (sessionId: string) => {
      updateSessions((prev) => prev.filter((s) => s.id !== sessionId));
      if (activeSessionId === sessionId) setActiveSessionId(null);
    },
    [activeSessionId, updateSessions],
  );

  const handleNewChat = useCallback(() => {
    setActiveSessionId(null);
    setSidebarOpen(false);
  }, []);

  const handleSpeakerChange = useCallback(
    (speakerId: SpeakerId) => {
      setSelectedSpeakerId(speakerId);

      if (!activeSession) return;
      if (activeSession.speaker === speakerId) return;

      if (activeSession.messages.length === 0) {
        activeSession.speaker = speakerId;
        updateSessions((prev) =>
          prev.map((s) => (s.id === activeSession.id ? { ...activeSession } : s)),
        );
        return;
      }

      setActiveSessionId(null);
    },
    [activeSession, updateSessions],
  );

  return (
    <div className="app">
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        speakers={SPEAKERS}
        isOpen={sidebarOpen}
        onSelect={handleSelectSession}
        onDelete={handleDeleteSession}
        onNewChat={handleNewChat}
        onClose={() => setSidebarOpen(false)}
      />

      <main className="main">
        <Header
          apiReady={apiReady}
          onToggleSidebar={() => setSidebarOpen((prev) => !prev)}
          onNewChat={handleNewChat}
        />

        <section className="chat-shell glass">
          <ChatArea messages={activeSession?.messages ?? []} speaker={activeSpeaker} isLoading={isLoading} isComplex={lastPromptComplex} />
          <ChatInput
            onSend={handleSend}
            isLoading={isLoading}
            speakerName={activeSpeaker.name}
            speakers={SPEAKERS}
            selectedSpeakerId={selectedSpeakerId}
            onSpeakerChange={handleSpeakerChange}
          />
        </section>
      </main>
    </div>
  );
}
