export type SpeakerId = "elon_musk" | "sam_altman" | "dario_amodei" | "mark_zuckerberg";

export interface Speaker {
  id: SpeakerId;
  name: string;
  company: string;
  avatar: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  speaker?: SpeakerId;
  timestamp: number;
}

export interface ChatSession {
  id: string;
  speaker: SpeakerId;
  messages: Message[];
  createdAt: number;
  title: string;
}

export interface ChatResponse {
  speaker: string;
  speaker_name: string;
  message: string;
}
