import { useState, useRef, type KeyboardEvent } from "react";
import type { Speaker, SpeakerId } from "../types";
import "./ChatInput.css";

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
  speakerName: string;
  speakers: Speaker[];
  selectedSpeakerId: SpeakerId;
  onSpeakerChange: (speakerId: SpeakerId) => void;
}

export function ChatInput({
  onSend,
  isLoading,
  speakerName,
  speakers,
  selectedSpeakerId,
  onSpeakerChange,
}: ChatInputProps) {
  const [text, setText] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    const trimmed = text.trim();
    if (!trimmed || isLoading) return;
    onSend(trimmed);
    setText("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = () => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 160) + "px";
  };

  return (
    <div className="input-wrapper">
      <div className="input-container glass">
        <div className="speaker-pick" aria-label="Choose speaker" role="listbox">
          {speakers.map((speaker) => (
            <button
              key={speaker.id}
              className={`speaker-avatar-btn ${selectedSpeakerId === speaker.id ? "speaker-avatar-btn-active" : ""}`}
              onClick={() => onSpeakerChange(speaker.id)}
              type="button"
              disabled={isLoading}
              title={speaker.name}
              aria-label={`Use ${speaker.name}`}
            >
              <img src={speaker.avatar} alt={speaker.name} loading="lazy" />
            </button>
          ))}
        </div>

        <textarea
          ref={textareaRef}
          className="input-field"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          onInput={handleInput}
          placeholder={`Ask ${speakerName} anything...`}
          rows={1}
          disabled={isLoading}
          aria-label="Message input"
        />
        <button
          className="send-btn"
          onClick={handleSend}
          disabled={!text.trim() || isLoading}
          aria-label="Send message"
        >
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
            <path
              d="M3 9h12M10 4l5 5-5 5"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>
      <p className="input-hint">
        Talking to {speakerName}. History is saved automatically on this device.
      </p>
    </div>
  );
}
