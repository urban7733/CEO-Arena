import type { Speaker, SpeakerId } from "../types";
import "./SpeakerSelector.css";

interface SpeakerSelectorProps {
  speakers: Speaker[];
  onSelect: (id: SpeakerId) => void;
}

export function SpeakerSelector({ speakers, onSelect }: SpeakerSelectorProps) {
  return (
    <div className="speaker-grid" role="listbox" aria-label="Choose CEO speaker">
      {speakers.map((s, index) => (
        <button
          key={s.id}
          className="speaker-card glass glass-hover"
          onClick={() => onSelect(s.id)}
          style={{ animationDelay: `${index * 70}ms` }}
        >
          <span className="speaker-card-emoji">{s.emoji}</span>
          <span className="speaker-card-name">{s.name}</span>
          <span className="speaker-card-company">{s.company}</span>
        </button>
      ))}
    </div>
  );
}
