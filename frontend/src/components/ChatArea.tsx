import { useEffect, useRef } from "react";
import type { Message, Speaker, SpeakerId } from "../types";
import "./ChatArea.css";

interface ChatAreaProps {
  messages: Message[];
  speaker: Speaker;
  isLoading: boolean;
}

interface ThinkingProfile {
  inner: string[];
  draft: string[];
  pacing: string;
}

const THINKING_PROFILES: Record<SpeakerId, ThinkingProfile> = {
  elon_musk: {
    inner: [
      "Running first-principles check against physics and scale.",
      "Pressure-testing this for speed, cost, and leverage.",
      "Looking for the weird but high-upside angle.",
    ],
    draft: [
      "Uh... okay, first principles: the core constraint is energy and throughput.",
      "Wait-no, better framing: ship fast, then iterate brutally on feedback.",
      "Net: bold move beats committee logic if the math holds.",
    ],
    pacing: "Fast cadence. Slightly chaotic wording, then a sharp conclusion.",
  },
  sam_altman: {
    inner: [
      "Defining the core tradeoff and second-order effects.",
      "Balancing near-term execution with long-term compounding.",
      "Turning this into practical, founder-friendly guidance.",
    ],
    draft: [
      "I think the key is to pick the highest-leverage constraint first.",
      "Short term, ship a narrow win. Long term, build the compounding loop.",
      "If this works, it creates optionality instead of locking you in.",
    ],
    pacing: "Measured, optimistic pacing with clear next-step framing.",
  },
  dario_amodei: {
    inner: [
      "Separating real signal from narrative noise.",
      "Estimating upside while stress-testing failure modes.",
      "Choosing the most robust interpretation under uncertainty.",
    ],
    draft: [
      "My best read is this works, but the uncertainty bars still matter.",
      "The upside is meaningful, yet safety and reliability are the gating factors.",
      "I'd proceed empirically with checkpoints rather than heroic assumptions.",
    ],
    pacing: "Careful and analytical, with explicit uncertainty handling.",
  },
  mark_zuckerberg: {
    inner: [
      "Mapping product surface, distribution, and platform risk.",
      "Checking execution path from MVP to scaled rollout.",
      "Sharpening the recommendation to be precise and shippable.",
    ],
    draft: [
      "Let me take a second: this is mostly a product and control question.",
      "The right move is simple but strict: own the critical platform layer.",
      "Precise call: ship version one now, then optimize retention hard.",
    ],
    pacing: "Slightly slower start, then highly precise and execution-focused.",
  },
};

export function ChatArea({ messages, speaker, isLoading }: ChatAreaProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const shouldStickToBottomRef = useRef(true);
  const thinkingTickRef = useRef(0);
  const thinkingTextRef = useRef<HTMLParagraphElement>(null);
  const draftTextRef = useRef<HTMLParagraphElement>(null);
  const thinkingProfile = THINKING_PROFILES[speaker.id] ?? THINKING_PROFILES.sam_altman;

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

  useEffect(() => {
    if (!isLoading) return;
    const profile = THINKING_PROFILES[speaker.id] ?? THINKING_PROFILES.sam_altman;
    const steps = profile.inner;
    const drafts = profile.draft;
    thinkingTickRef.current = 0;
    if (thinkingTextRef.current) {
      thinkingTextRef.current.textContent = steps[0];
    }
    if (draftTextRef.current) {
      draftTextRef.current.textContent = drafts[0];
    }

    const timer = setInterval(() => {
      thinkingTickRef.current = (thinkingTickRef.current + 1) % steps.length;
      if (thinkingTextRef.current) {
        thinkingTextRef.current.textContent = steps[thinkingTickRef.current];
      }
      if (draftTextRef.current) {
        draftTextRef.current.textContent = drafts[thinkingTickRef.current % drafts.length];
      }
    }, 900);

    return () => clearInterval(timer);
  }, [isLoading, speaker.id]);

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
              <div className="thinking-panel">
                <p className="thinking-label">{speaker.name} is thinking</p>
                <div className="thinking-split">
                  <div className="thinking-box">
                    <p className="thinking-box-label">Inside head</p>
                    <p className="thinking-line" ref={thinkingTextRef} />
                  </div>
                  <div className="thinking-box">
                    <p className="thinking-box-label">Would say</p>
                    <p className="thinking-line thinking-line-draft" ref={draftTextRef} />
                  </div>
                </div>
                <p className="thinking-subline">{thinkingProfile.pacing}</p>
              </div>
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
