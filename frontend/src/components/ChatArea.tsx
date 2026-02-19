import { useEffect, useRef } from "react";
import type { Message, Speaker } from "../types";
import "./ChatArea.css";

interface ChatAreaProps {
  messages: Message[];
  speaker: Speaker;
  isLoading: boolean;
}

export function ChatArea({ messages, speaker, isLoading }: ChatAreaProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div className="chat-area">
      <div className="chat-messages">
        {messages.map((msg) => (
          <div key={msg.id} className={`message message-${msg.role}`}>
            {msg.role === "assistant" && (
              <div className="message-avatar">{speaker.emoji}</div>
            )}
            <div
              className={`message-bubble glass ${
                msg.role === "user" ? "message-bubble-user" : "message-bubble-assistant"
              }`}
            >
              <p className="message-text">{msg.content}</p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message message-assistant">
            <div className="message-avatar">{speaker.emoji}</div>
            <div className="message-bubble glass message-bubble-assistant">
              <div className="typing-indicator">
                <span />
                <span />
                <span />
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  );
}
