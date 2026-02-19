import { useState, useCallback, useEffect } from "react";
import type { ChatSession, SpeakerId } from "./types";
import { sendMessage, checkHealth } from "./api";
import { loadSessions, saveSessions, createSession, addMessage } from "./store";
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
  const [apiReady, setApiReady] = useState<boolean | null>(null);

  const activeSession = sessions.find((s) => s.id === activeSessionId) ?? null;
  const activeSpeaker = SPEAKERS_DATA.find((s) => s.id === activeSession?.speaker);

  useEffect(() => {
    let cancelled = false;

    const ping = async () => {
      const isHealthy = await checkHealth();
      if (!cancelled) setApiReady(isHealthy);
    };

    ping();
    const timer = setInterval(ping, 15000);

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
        <section className="hero glass">
          <button className="hero-icon-btn glass-hover" onClick={() => setSidebarOpen(true)} aria-label="Open conversation history">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M3 5h12M3 9h12M3 13h12" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
            </svg>
          </button>

          <div className="hero-copy">
            <h1 className="hero-title">CEO Arena</h1>
            <p className="hero-subtitle">A clean glass chat experience for the 4 AI-era CEOs.</p>
          </div>

          <div className="hero-actions">
            <span className={`status-pill ${apiReady === true ? "status-pill-ready" : "status-pill-waiting"}`}>
              {apiReady === null ? "Checking API" : apiReady ? "API Ready" : "API Offline"}
            </span>
            <button className="hero-new-chat glass-hover" onClick={handleNewChat}>
              New Chat
            </button>
          </div>
        </section>

        <section className="chat-shell glass">
          {!activeSession ? (
            <div className="welcome">
              <div className="welcome-content">
                <h2 className="welcome-title">Choose a CEO</h2>
                <p className="welcome-subtitle">
                  Start one conversation at a time. Your local chat history is saved automatically.
                </p>
                <SpeakerSelector speakers={SPEAKERS_DATA} onSelect={handleSelectSpeaker} />
                <p className="disclaimer">
                  Fan-made simulation based on public data. Not affiliated with any individual.
                </p>
              </div>
            </div>
          ) : (
            <>
              <div className="active-speaker-strip">
                <div className="active-speaker-badge">
                  <span>{activeSpeaker?.emoji}</span>
                  <div>
                    <strong>{activeSpeaker?.name}</strong>
                    <small>{activeSpeaker?.company}</small>
                  </div>
                </div>
                <button className="change-speaker-btn glass-hover" onClick={handleNewChat}>
                  Switch Speaker
                </button>
              </div>
              <ChatArea messages={activeSession.messages} speaker={activeSpeaker!} isLoading={isLoading} />
              <ChatInput onSend={handleSend} isLoading={isLoading} speakerName={activeSpeaker?.name ?? ""} />
            </>
          )}
        </section>
      </main>
    </div>
  );
}
