import type { ChatSession, Speaker, SpeakerId } from "../types";
import "./Sidebar.css";

interface SidebarProps {
  sessions: ChatSession[];
  activeSessionId: string | null;
  speakers: Speaker[];
  isOpen: boolean;
  onSelect: (sessionId: string) => void;
  onDelete: (sessionId: string) => void;
  onNewChat: () => void;
  onClose: () => void;
}

export function Sidebar({
  sessions,
  activeSessionId,
  speakers,
  isOpen,
  onSelect,
  onDelete,
  onNewChat,
  onClose,
}: SidebarProps) {
  const getSpeaker = (id: SpeakerId) => speakers.find((s) => s.id === id);

  return (
    <>
      {/* Overlay */}
      {isOpen && <div className="sidebar-overlay" onClick={onClose} />}

      <aside className={`sidebar glass ${isOpen ? "sidebar-open" : ""}`}>
        <div className="sidebar-header">
          <h2 className="sidebar-title">Conversations</h2>
          <button className="sidebar-close-btn glass-hover" onClick={onClose} aria-label="Close history">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M3 3l10 10M13 3L3 13" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
            </svg>
          </button>
        </div>

        <div className="sidebar-toolbar">
          <button className="sidebar-new-btn glass glass-hover" onClick={onNewChat}>
            + New Chat
          </button>
        </div>

        <div className="sidebar-sessions">
          {sessions.length === 0 ? (
            <p className="sidebar-empty">No conversations yet</p>
          ) : (
            sessions.map((session) => {
              const speaker = getSpeaker(session.speaker);
              return (
                <div
                  key={session.id}
                  className={`sidebar-item glass-hover ${
                    session.id === activeSessionId ? "sidebar-item-active" : ""
                  }`}
                  onClick={() => onSelect(session.id)}
                >
                  <span className="sidebar-item-emoji">{speaker?.emoji}</span>
                  <div className="sidebar-item-info">
                    <span className="sidebar-item-title">{session.title}</span>
                    <span className="sidebar-item-meta">
                      {speaker?.name} &middot; {session.messages.length} msgs
                    </span>
                  </div>
                  <button
                    className="sidebar-item-delete"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDelete(session.id);
                    }}
                    aria-label="Delete conversation"
                  >
                    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                      <path d="M3 3l8 8M11 3l-8 8" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
                    </svg>
                  </button>
                </div>
              );
            })
          )}
        </div>
      </aside>
    </>
  );
}
