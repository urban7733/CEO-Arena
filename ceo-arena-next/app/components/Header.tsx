"use client";

interface HeaderProps {
  apiReady: boolean | null;
  onToggleSidebar: () => void;
  onNewChat: () => void;
}

export function Header({ apiReady, onToggleSidebar, onNewChat }: HeaderProps) {
  return (
    <section className="topbar">
      <button
        className="topbar-icon-btn glass-hover"
        onClick={onToggleSidebar}
        aria-label="Open conversation history"
      >
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
          <path d="M3 5h12M3 9h12M3 13h12" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
        </svg>
      </button>

      <div className="topbar-copy">
        <h1 className="topbar-title">CEO Arena</h1>
        <p className="topbar-subtitle">Four CEOs, one conversation.</p>
      </div>

      <div className="topbar-actions">
        <span className={`status-pill ${apiReady === true ? "status-pill-ready" : "status-pill-waiting"}`}>
          {apiReady === null ? "Checking API" : apiReady ? "API Ready" : "API Offline"}
        </span>
        <button className="new-chat-btn glass-hover" onClick={onNewChat}>
          New Chat
        </button>
      </div>
    </section>
  );
}
