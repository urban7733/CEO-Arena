import { useEffect, useRef } from "react";
import type { Message, Speaker } from "../types";
import "./ChatArea.css";

interface ChatAreaProps {
  messages: Message[];
  speaker: Speaker;
  isLoading: boolean;
}

export function ChatArea({ messages, speaker, isLoading }: ChatAreaProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const shouldStickToBottomRef = useRef(true);

  const handleScroll = () => {
    const el = containerRef.current;
    if (!el) return;
    const threshold = 80;
    const isNearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < threshold;
    shouldStickToBottomRef.current = isNearBottom;
  };

  useEffect(() => {
    if (!shouldStickToBottomRef.current) return;
    bottomRef.current?.scrollIntoView({ behavior: "auto" });
  }, [messages, isLoading]);

  return (
    <div className="chat-area" ref={containerRef} onScroll={handleScroll}>
      <div className="chat-messages">
        {messages.length === 0 && !isLoading && (
          <div className="chat-empty glass">
            <p className="chat-empty-title">Start the conversation</p>
            <p className="chat-empty-text">Ask {speaker.name} anything. Answers are generated from the RAG backend.</p>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`message message-${msg.role}`}>
            {msg.role === "assistant" && (
              <div className="message-avatar">
                <img src={speaker.avatar} alt={speaker.name} loading="lazy" />
              </div>
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
            <div className="message-avatar">
              <img src={speaker.avatar} alt={speaker.name} loading="lazy" />
            </div>
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
