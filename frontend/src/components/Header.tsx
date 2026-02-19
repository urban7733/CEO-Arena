import type { Speaker } from "../types";
import "./Header.css";

interface HeaderProps {
  speaker?: Speaker;
  onMenuClick: () => void;
  onBack?: () => void;
}

export function Header({ speaker, onMenuClick, onBack }: HeaderProps) {
  return (
    <header className="header glass">
      <button className="header-btn" onClick={onMenuClick} aria-label="Open menu">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path d="M3 5h14M3 10h14M3 15h14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
      </button>

      <div className="header-center">
        {speaker ? (
          <div className="header-speaker">
            <span className="header-avatar">
              <img src={speaker.avatar} alt={speaker.name} />
            </span>
            <div>
              <span className="header-name">{speaker.name}</span>
              <span className="header-company">{speaker.company}</span>
            </div>
          </div>
        ) : (
          <span className="header-logo">CEO Arena</span>
        )}
      </div>

      {onBack ? (
        <button className="header-btn" onClick={onBack} aria-label="New chat">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M10 4v12M4 10h12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        </button>
      ) : (
        <div style={{ width: 36 }} />
      )}
    </header>
  );
}
