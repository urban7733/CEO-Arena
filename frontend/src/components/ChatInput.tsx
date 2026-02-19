import { useState, useRef, type KeyboardEvent } from "react";
import "./ChatInput.css";

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
  speakerName: string;
}

export function ChatInput({ onSend, isLoading, speakerName }: ChatInputProps) {
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
        Powered by Llama 3.3 via Groq. Responses are AI-generated simulations.
      </p>
    </div>
  );
}
