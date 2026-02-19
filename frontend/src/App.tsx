import { useState, useCallback } from "react";
import type { ChatSession, SpeakerId } from "./types";
import { sendMessage } from "./api";
import { loadSessions, saveSessions, createSession, addMessage } from "./store";
import { Header } from "./components/Header";
import { SpeakerSelector } from "./components/SpeakerSelector";
import { ChatArea } from "./components/ChatArea";
import { ChatInput } from "./components/ChatInput";
import { Sidebar } from "./components/Sidebar";
import "./App.css";

const SPEAKERS_DATA = [
  { id: "elon_musk" as SpeakerId, name: "Elon Musk", company: "Tesla, SpaceX, xAI", emoji: "🚀" },
  { id: "sam_altman" as SpeakerId, name: "Sam Altman", company: "OpenAI", emoji: "🧠" },
  { id: "dario_amodei" as SpeakerId, name: "Dario Amodei", company: "Anthropic", emoji: "🛡️" },
  { id: "mark_zuckerberg" as SpeakerId, name: "Mark Zuckerberg", company: "Meta", emoji: "👓" },
];

export default function App() {
  const [sessions, setSessions] = useState<ChatSession[]>(() => loadSessions());
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const activeSession = sessions.find((s) => s.id === activeSessionId) ?? null;
  const activeSpeaker = SPEAKERS_DATA.find((s) => s.id === activeSession?.speaker);

  const updateSessions = useCallback(
    (updater: (prev: ChatSession[]) => ChatSession[]) => {
      setSessions((prev) => {
        const next = updater(prev);
        saveSessions(next);
        return next;
      });
    },
    []
  );

  const handleSelectSpeaker = useCallback(
    (speakerId: SpeakerId) => {
      const session = createSession(speakerId);
      updateSessions((prev) => [session, ...prev]);
      setActiveSessionId(session.id);
    },
    [updateSessions]
  );

  const handleSend = useCallback(
    async (text: string) => {
      if (!activeSession) return;

      addMessage(activeSession, "user", text);
      updateSessions((prev) =>
        prev.map((s) => (s.id === activeSession.id ? { ...activeSession } : s))
      );

      setIsLoading(true);
      try {
        const res = await sendMessage(activeSession.speaker, text);
        addMessage(activeSession, "assistant", res.message, activeSession.speaker);
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : "Something went wrong";
        addMessage(activeSession, "assistant", `Error: ${errorMsg}`);
      } finally {
        setIsLoading(false);
        updateSessions((prev) =>
          prev.map((s) => (s.id === activeSession.id ? { ...activeSession } : s))
        );
      }
    },
    [activeSession, updateSessions]
  );

  const handleSelectSession = useCallback((sessionId: string) => {
    setActiveSessionId(sessionId);
    setSidebarOpen(false);
  }, []);

  const handleDeleteSession = useCallback(
    (sessionId: string) => {
      updateSessions((prev) => prev.filter((s) => s.id !== sessionId));
      if (activeSessionId === sessionId) setActiveSessionId(null);
    },
    [activeSessionId, updateSessions]
  );

  const handleNewChat = useCallback(() => {
    setActiveSessionId(null);
    setSidebarOpen(false);
  }, []);

  return (
    <div className="app">
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        speakers={SPEAKERS_DATA}
        isOpen={sidebarOpen}
        onSelect={handleSelectSession}
        onDelete={handleDeleteSession}
        onNewChat={handleNewChat}
        onClose={() => setSidebarOpen(false)}
      />

      <main className="main">
        <Header
          speaker={activeSpeaker}
          onMenuClick={() => setSidebarOpen(true)}
          onBack={activeSession ? handleNewChat : undefined}
        />

        {!activeSession ? (
          <div className="welcome">
            <div className="welcome-content">
              <h1 className="welcome-title">CEO Arena</h1>
              <p className="welcome-subtitle">
                Chat with AI simulations of tech's most powerful leaders
              </p>
              <SpeakerSelector speakers={SPEAKERS_DATA} onSelect={handleSelectSpeaker} />
              <p className="disclaimer">
                Fan-made simulation based on public data. Not affiliated with any individuals.
              </p>
            </div>
          </div>
        ) : (
          <>
            <ChatArea messages={activeSession.messages} speaker={activeSpeaker!} isLoading={isLoading} />
            <ChatInput onSend={handleSend} isLoading={isLoading} speakerName={activeSpeaker?.name ?? ""} />
          </>
        )}
      </main>
    </div>
  );
}
